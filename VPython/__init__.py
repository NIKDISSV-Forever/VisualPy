from __future__ import annotations

import argparse
import builtins
from pathlib import Path

import pygments.lexers.python as py_lexers

import VPython.highlights
from VPython.interactive import VisualPython

builtins.unichr = chr  # pypy msvcrt fix

ALL_LEXERS = py_lexers.__all__


def cli_main():
    arg_parser = argparse.ArgumentParser('VPython')

    highlight_group = arg_parser.add_argument_group('Highlight', 'Highlight Options')
    highlight_group.add_argument('-dbg', '--darkbg', action='store_true', default=False,
                                 help="depending on the terminal's background")

    lexer_group = arg_parser.add_argument_group('Lexer', 'Lexer Options')
    lexer_group.add_argument('-lex', '--lexer', choices=ALL_LEXERS, default='PythonLexer')
    lexer_group.add_argument('-t-lex', '--traceback-lexer', choices=ALL_LEXERS, default='PythonTracebackLexer')
    lexer_group.add_argument('-cr', '--cursor', type=str)

    pyopt_group = arg_parser.add_argument_group('Python', 'Python Options')
    pyopt_group.add_argument('-i', '--interact-it', type=Path, help='Inspect interactively after running script')
    pyopt_group.add_argument('-q', '--quiet', action='store_true',
                             help="Don't print version and copyright messages on interactive startup")

    args = arg_parser.parse_args()

    VPython.highlights.FORMATTER.darkbg = args.darkbg
    VPython.highlights.LEXER = getattr(py_lexers, args.lexer)()
    VPython.highlights.TRACEBACK_LEXER = getattr(py_lexers, args.traceback_lexer)()

    if args.cursor:
        VPython.highlights.CURSOR = args.cursor

    builtins_dict = builtins.__dict__
    builtins_dict['__name__'] = '__name__'
    interactive = VisualPython(builtins_dict)

    interact_it: Path = args.interact_it
    if interact_it:
        try:
            source = interact_it.read_text('UTF-8')
        except Exception as read_error:
            print(f"{__file__!r}: can't open file {interact_it.absolute()!r}: {read_error}")
        else:
            interactive.runsource(source)
    interactive.interact('' if args.quiet else None)
