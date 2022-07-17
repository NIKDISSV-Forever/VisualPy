from __future__ import annotations

import pygments.lexers.python as py_lexers
from pygments import highlight as _highlight
from pygments.formatter import Formatter
from pygments.formatters import terminal
from pygments.lexer import Lexer

LEXER: Lexer = py_lexers.PythonLexer()
TRACEBACK_LEXER = py_lexers.PythonTracebackLexer()
FORMATTER: Formatter = terminal.TerminalFormatter()
CURSOR = '<'


def highlight(executed, lex: Lexer = None, formatter: Formatter = None) -> str:
    return highlighted[:-1] if (highlighted := _highlight(
        executed := str(executed), LEXER if lex is None else lex,
        FORMATTER if formatter is None else formatter
    )).endswith('\n') and not executed.endswith('\n') else highlighted
