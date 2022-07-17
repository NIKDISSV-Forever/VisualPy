from __future__ import annotations

import abc
import ast
import inspect
import keyword
import os
import pkgutil
import re
import shutil
import string
import sys
import textwrap
from contextlib import contextmanager
from typing import Iterable, Literal

import rich

from VPython import highlights
from VPython import interactive

punctuation_space = re.sub(r'[._]', '', string.punctuation) + ' '
punctuations = re.compile(r'[{0}]'.format('\\'.join(punctuation_space)))


class Tiper(abc.ABC):
    __slots__ = ('line',)

    def __init__(self, line: str):
        self.line = line

    @abc.abstractmethod
    def check(self) -> None | tuple[str, str]:
        pass

    @classmethod
    def filter_options(cls, part: str, options: Iterable[str], *, check_lower: bool = True) -> tuple[str]:
        part_lower = part.casefold()
        options = [opt for opt in options if opt]
        filtered = [opt for opt in options if opt.startswith(part)]
        if not filtered and check_lower:
            filtered = [opt for opt in options if opt.startswith(part_lower)]
        if not filtered:
            filtered = [opt for opt in options if part in opt]
        if not filtered and check_lower:
            filtered = [opt for opt in options if part_lower in opt]
        return *filtered,

    @classmethod
    def find_general(cls, filtered: Iterable[str]):
        lowest = min(filtered, key=len)
        return lowest if all(lowest in el for el in filtered) else None


class Keyword(Tiper):
    __slots__ = ()

    def check(self) -> None | tuple[str, str]:
        options = (*keyword.kwlist, *getattr(keyword, 'softkwlist', ()))
        part = punctuations.split(self.line)[-1]

        filtered = Tiper.filter_options(part, options, check_lower=False)
        if not filtered:
            return
        if len(filtered) == 1:
            return part, filtered[-1]
        _print_filtered(filtered)
        return


class Imports(Tiper):
    __slots__ = ()

    def check(self) -> None | tuple[str, str] | Literal[False]:
        with disable_stdout():
            options = [mod[1] for mod in pkgutil.walk_packages(onerror=_ignore)]
        imported = ()
        try:
            parsed = ast.parse(self.line)
        except SyntaxError as e:
            slices = e.args[-1][1:3]
            words = self.line[slices[0] - 1:].strip().split()
            if 'from' in words:
                if 'import' in words:
                    import_pos = words.index('import')
                    module_name = words[:import_pos][-1]
                    try:
                        options = [name for name, _ in
                                   inspect.getmembers(__import__(module_name))] if module_name in options else []
                    except Exception:
                        pass
                    options.append('*')
                    import_names = words[import_pos + 1:]
                    part = ''.join(import_names).split(',')[-1]
                else:
                    words_count = len(words)
                    if words_count != 2:
                        return
                    part = words[words.index('from') + 1]
            elif 'import' in words:
                import_pos = words.index('import')
                imported = ''.join(words[import_pos + 1:]).split(',')
                part = imported[-1]
                imported = imported[:-1]
            else:
                return
        else:
            body = parsed.body
            if not body:
                return
            last_ast = body[-1]
            if isinstance(last_ast, ast.Import):
                aliases = last_ast.names
                imported = [alias.name for alias in aliases[:-1]]
                part = aliases[-1].name
            elif isinstance(last_ast, ast.ImportFrom):
                module_name = last_ast.module
                aliases = last_ast.names
                imported = [alias.name for alias in aliases[:-1]]
                try:
                    options = dir(__import__(module_name)) if module_name in options else []
                except Exception:
                    pass
                options.append('*')
                part = aliases[-1].name
            else:
                return
        filtered = Tiper.filter_options(part, [opt for opt in options if opt not in imported])
        if not filtered:
            return
        if len(filtered) > 1:
            general = Tiper.find_general(filtered)
            _print_filtered(filtered)
            return (part, general) if general is not None else False
        return part, filtered[0]


class Attrs(Tiper):
    __slots__ = ()

    @staticmethod
    def get_obj_by_path(mn: tuple[str]) -> object | None:
        obj = None
        if mn[0] in interactive.INTERACTIVE_LOCALS:
            obj = interactive.INTERACTIVE_LOCALS[mn[0]]
            for attr_name in mn[1:]:
                obj = getattr(obj, attr_name, obj)
        return obj

    def check(self) -> None | tuple[str, str]:
        options = (*interactive.INTERACTIVE_LOCALS.keys(),)
        obj = None
        if '.' in self.line:
            parts = punctuations.split('.'.join([dots.strip(punctuation_space) for dots in self.line.split('.')]))
            *mn, part = parts[-1].split('.')
            if mn:
                obj = self.get_obj_by_path(mn)
                options = dir(obj) if obj is not None else ()
        else:
            part = punctuations.split(self.line)[-1]
        filtered = Tiper.filter_options(part, options)
        if len(filtered) == 1:
            opt = filtered[0]
            if opt == part:
                try:
                    sigs = inspect.signature(interactive.INTERACTIVE_LOCALS[opt] if obj is None else getattr(obj, opt))
                except Exception:
                    pass
                else:
                    return '', str(sigs)
            return part, opt
        opt: str
        similar_prefix = [opt for opt in filtered if opt.startswith(part)]
        if len(similar_prefix) > 1:
            pref_len = len(part) + 1
            max_len = max(len(i) for i in similar_prefix)
            while all(opt.startswith(similar_prefix[0][:pref_len]) for opt in similar_prefix) and max_len > pref_len:
                pref_len += 1
            pref_len -= 1
            if pref_len > len(part):
                return part, similar_prefix[0][:pref_len]
        _print_filtered(filtered)
        return


@contextmanager
def disable_stdout():
    _stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, 'w')
        yield
    finally:
        sys.stdout = _stdout


def _ignore(_):
    return


def _print_filtered(results: Iterable | None):
    if not results:
        return
    values = [str(i) for i in results]
    w, h = shutil.get_terminal_size()
    max_chars = w * (h - 1) - 1
    allowed = 0
    for val in values:
        allowed += len(val) + 2
    if allowed <= max_chars:
        print(f"\n{highlights.highlight(textwrap.shorten(', '.join(values), max_chars))}")
        return
    rich.print('\n'
               f'Display all {len(values)} possibilities? '
               f'[i]start[:stop:step][/i] |'

               f' [yellow][b]S[/b]horten[/yellow]'
               f'/[red][b]n[/b]o[/red]'
               f'/[green][b]y[/b]es[/green]',
               end=' ')
    choice = (input().strip().casefold() or 's')[0]
    if choice == 'y':
        print(f"\n{highlights.highlight(', '.join(values))}")
        return
    if choice == 'n':
        return
    start, stop, step = (i.strip().isdigit() and int(i) or None for i in (*choice.split(':'), '', '')[:3])
    if start is not None:
        values = values[slice(start, stop, step)]
    print(f"\n{highlights.highlight(textwrap.shorten(', '.join(values), max_chars))}")


TIPS = (Imports, Keyword, Attrs)
