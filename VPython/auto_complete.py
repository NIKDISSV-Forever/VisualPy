from __future__ import annotations

import re

SPACES = re.compile(r'^(\s+).+')
BRACKETS = {'(': ')\xe0K', '[': ']\xe0K', '{': '}\xe0K', '<': '>\xe0K'}
QUOTES = "'\""

STATEMENTS = {
    'if': 'if \0:', 'elif': 'elif \0:', 'else': 'else:\n', 'ife': 'if \0 else ',
    'while': 'while \0:', 'wtrue': 'while 1:\n',
    'for': 'for \0 in :',
    'try': 'try:\n', 'except': 'except \0:', 'finally': 'finally:\n',
    'with': 'with \0 as :',
    'match': 'match \0:', 'case': 'case \0:',
    'def': 'def \0():', 'class': 'class \0:',
}
