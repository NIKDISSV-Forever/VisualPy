# encoding: utf-8
from __future__ import annotations

import array
import code
import os
import shutil
import sys
import traceback
from types import TracebackType
from typing import Any, Type

import pyperclip
import rich

import vpy.auto_complete
import vpy.highlights
import vpy.hints

try:
    from msvcrt import getwch as _get_char
except ImportError:
    from readchar import readchar as _get_char

INTERACTIVE_LOCALS = {}

os.system('chcp 65001')  # set terminal unicode support


def get_char() -> str:
    c: bytes | str = _get_char()
    if isinstance(c, bytes):
        return c.decode()
    return c


def clear_console():
    os.system('cls || clear')


def write_traceback(data: str):
    sys.stderr.write(vpy.highlights.highlight(data, vpy.highlights.TRACEBACK_LEXER))


def vpython_excepthook(exc_type: Type[BaseException], value: BaseException, tb: TracebackType):
    write_traceback(''.join(traceback.format_exception(exc_type, value, tb.tb_next)))


sys.excepthook = vpython_excepthook


class VisualPython(code.InteractiveConsole):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        if 'pypy' in sys.version.casefold():
            try:
                sys.ps1
            except AttributeError:
                sys.ps1 = ">>>> "
            try:
                sys.ps2
            except AttributeError:
                sys.ps2 = ".... "
        else:
            try:
                sys.ps1
            except AttributeError:
                sys.ps1 = ">>> "
            try:
                sys.ps2
            except AttributeError:
                sys.ps2 = "... "
        super().__init__(*args, **kwargs)

        self._auto_char = array.array('u')
        self._auto_line = []
        self._last_executed = None

        self.LINES_HISTORY = [array.array('u')]

        global INTERACTIVE_LOCALS
        INTERACTIVE_LOCALS = self.locals

    @property
    def last_executed(self):
        return self._last_executed

    @last_executed.setter
    def last_executed(self, value):
        if '_' not in self.locals or self.locals['_'] is self.last_executed:
            self._last_executed = self.locals['_'] = value

    def interact(self, banner=None, exitmsg=None):
        copyright_ = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            if 'py' not in self.__class__.__name__.casefold():
                self.__class__.__name__ += ' Python'
            name_len = len(self.__class__.__name__)
            rich.print(f'[i][blue]{self.__class__.__name__[:name_len // 2]}[/blue]'
                       f'[yellow]{self.__class__.__name__[name_len // 2:]}[/yellow][/] '
                       f'{sys.version} on {sys.platform}\n'
                       f'{copyright_}\n'
                       '[white b on black]Tab[/] for hints, '
                       '2x [white b on black]Esc[/] to clear screen.')
        elif banner:
            self.write(f'{banner}\n')

        more = 0
        while 1:
            try:
                line = self.raw_input(sys.ps2 if more else sys.ps1)
                more = self.push(line)
            except KeyboardInterrupt as exc:
                if exc.args:
                    raise
                self.write('\n')
                self.runsource("raise KeyboardInterrupt from None", filename=self.filename)
            except EOFError as exc:
                if exc.args:
                    raise
                self.write('\n')
                self.runsource(
                    "raise EOFError("
                    f"{f'Exiting {self.__class__.__name__}...' if exitmsg is None else exitmsg!r}"
                    ") from None", filename=self.filename)
                break

    def runsource(self, source: str, filename: str = None, symbol: str = None) -> bool:
        if filename is None:
            filename = self.filename
        if symbol is None:
            try:
                code = self.compile(source, filename, 'eval')
                if code is None:
                    raise ValueError
            except (OverflowError, SyntaxError, ValueError):
                try:
                    code = self.compile(source, filename, 'exec')
                except (OverflowError, SyntaxError, ValueError):
                    self.showsyntaxerror()
                    return False

            if code is None or (len(self.buffer) > 1 and self.buffer[-1]):
                return True
            try:
                # noinspection PyTypeChecker
                executed = eval(code, self.locals)
            except SystemExit as exit_error:
                exit_code = exit_error.code
                if exit_code is not None:
                    color = 'red' if exit_code else 'green'
                    rich.print(f'[i]Exit code: [b {color}]{exit_code}[/b {color}][/]')
                raise
            except BaseException as err:
                if isinstance(err, EOFError):
                    raise
                self.last_executed = sys.exc_info()
                self.showtraceback()
            else:
                if executed is not None:
                    self.last_executed = executed
                    print(vpy.highlights.highlight(repr(executed)))
            return False

        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False

        if code is None:
            return True
        self.runcode(code)
        return False

    def write(self, data: str):
        write_traceback(data)

    def raw_input(self, prompt: Any = '') -> str:
        if not isinstance(prompt, str):
            prompt = prompt.decode() if callable(getattr(prompt, 'decode', None)) else str(prompt)
        if self._auto_line:
            return self._auto_line.pop(0)
        double_esc = False
        quoted = 1
        history_ptr = 0

        line = array.array('u')
        if prompt == sys.ps2 and self.LINES_HISTORY:
            last_line = ''.join(self.LINES_HISTORY[-1])
            if len(last_line) > 1:
                found = vpy.auto_complete.SPACES.findall(last_line)
                if last_line.strip('\0 '):
                    line.extend(found[0] if found else '    ')
        line.append('\0')
        while True:
            if '\0' in line:
                cursor_pos = line.index('\0')
            else:
                line.append('\0')
                cursor_pos = len(line) - 1

            final_line = ''.join(line)
            print('\r' + self.terminal_just(prompt, final_line),
                  end='', flush=True)
            ch = self.getch()

            if ch == '\3':  # Ctrl + C
                raise KeyboardInterrupt
            elif ch == '\x1a':  # Ctrl + Z
                raise EOFError

            elif ch == '\x16':  # Ctrl + V
                line.pop(cursor_pos)
                line += array.array('u', pyperclip.paste() + '\0')
                continue

            elif ch == '\x18':  # Ctrl + X
                pyperclip.copy(''.join(line))
                line = array.array('u', '\0')
                continue

            elif ch == '\x08':  # Backspace
                if len(line) > 1 and cursor_pos:
                    line.pop(cursor_pos - 1)
                continue

            elif ch == '\x1b':  # Esc
                if double_esc:
                    clear_console()
                double_esc = not double_esc
                continue

            elif ch == '\x7f':  # Ctrl + Backspace
                line = line[cursor_pos:]
                continue

            elif ch == '\xe0':
                direction = self.getch()
                if direction in 'KM':  # < >
                    offset = cursor_pos + (-1 if direction == 'K' else 1)
                    if 0 <= offset < len(line):
                        line.pop(cursor_pos)
                        line.insert(offset, '\0')
                elif direction in 'HP':  # UP DOWN
                    offset = -1 if direction == 'H' else 1
                    history_ptr = (history_ptr + offset) % len(self.LINES_HISTORY)
                    line = self.LINES_HISTORY[history_ptr]
                    continue

                elif direction in 'sGtO':  # Ctrl + < >  |  Start End
                    line.pop(cursor_pos)
                    if direction == 's':
                        precursor = line[:cursor_pos]
                        pos = precursor.index(' ') if ' ' in precursor else 0
                    elif direction == 't':
                        post_cursor = line[cursor_pos:]
                        pos = (cursor_pos + post_cursor.index(' ') + 1) if ' ' in post_cursor else len(line)
                    else:
                        pos = 0 if direction == 'G' else len(line)
                    line.insert(pos, '\0')
                elif direction == 'S':  # Delete
                    if cursor_pos != len(line) - 1:
                        line.pop(cursor_pos + 1)
                elif direction == '\x93':
                    line = line[:cursor_pos]
                continue

            elif ch == '\t':  # Auto Complete And Tips
                deployed = False
                for stmt, deploy in vpy.auto_complete.STATEMENTS.items():
                    find_at = slice(cursor_pos - len(stmt), cursor_pos)
                    if ''.join(line[find_at]) == stmt:
                        if '\0' in deploy:
                            line.pop(cursor_pos)
                        if deploy[-1] == '\n':
                            deploy = deploy[:-1]
                            self._auto_char.append('\n')
                        line[find_at] = array.array('u', deploy)
                        deployed = True
                        break
                if deployed:
                    continue

                to_cursor = ''.join(line[:cursor_pos]).rstrip()

                _striped_len = len(to_cursor)
                if _striped_len < cursor_pos:
                    line[:cursor_pos] = array.array('u', to_cursor)
                    cursor_pos = len(to_cursor)

                for hinter in vpy.hints.HINTS:
                    checks = hinter(to_cursor).check()
                    if checks is not None:
                        if not checks:
                            break
                        part, checked = checks
                        line[cursor_pos - len(part):cursor_pos] = array.array('u', checked)
                        break
                continue

            elif ch in vpy.auto_complete.QUOTES:
                if quoted == 3:
                    quoted = 1
                    self._auto_char.extend('\xe0K')
                    continue
                else:
                    self._auto_char.append(ch)
                    quoted += 1
            elif ch in '\r\n':
                break
            if ch in vpy.auto_complete.BRACKETS:
                self._auto_char.extend(vpy.auto_complete.BRACKETS[ch])
            line.insert(cursor_pos, ch)
        if line in self.LINES_HISTORY:
            self.LINES_HISTORY.remove(line)
        self.LINES_HISTORY.append(line)
        print('\r' + self.terminal_just(prompt, final_line, ''))
        return final_line.replace('\0', '')

    @staticmethod
    def terminal_just(prompt: str, line: str, cursor: str = None) -> str:
        if cursor is None:
            cursor = vpy.highlights.CURSOR
        tw = shutil.get_terminal_size()[0] - 1 - len(prompt) - (line.count('\t') * 4)
        parts = [line[i:i + tw] for i in range(0, len(line), tw - 1)]
        part_with_cursor = parts[-1]
        if '\0' in line:
            if '\0' in parts[0]:
                part_with_cursor = parts[0]
            else:
                for part in parts[1:]:
                    if '\0' in part:
                        part_with_cursor = part
                        break
        if len(parts) > 1 and prompt:
            prompt = f'{prompt[:-1]}\N{HORIZONTAL ELLIPSIS}'
        return prompt + vpy.highlights.highlight(part_with_cursor.ljust(tw)).replace('\0', cursor)

    def getch(self) -> str:
        return self._auto_char.pop(0) if self._auto_char else get_char()
