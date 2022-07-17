Interactive console with syntax highlighting and tooltips.

Works with both _CPython_ and _PyPy_.

# Installing

> pip install VPython -U

# Usage

> python -m VPython

![](screenshots/main.png)
![](screenshots/many_options.png)

> CPython
![](screenshots/CPython.png)

> Imports
![](screenshots/import_hints.png)
![](screenshots/import.png)

> Dark Theme (Default)
![](screenshots/dark_theme.png)
> Light Theme (-dbg --darkbg flag)
![](screenshots/light_theme.png)

# Arguments

```
usage: VPython [-h] [-dbg]
               [-lex {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}]
               [-t-lex {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}]
               [-cr CURSOR] [-i INTERACT_IT] [-q]

optional arguments:
  -h, --help            show this help message and exit

Highlight:
  Highlight Options

  -dbg, --darkbg        depending on the terminal's background

Lexer:
  Lexer Options

  -lex {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}, --lexer {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}
  -t-lex {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}, --traceback-lexer {PythonLexer,PythonConsoleLexer,PythonTracebackLexer,Python2Lexer,Python2TracebackLexer,CythonLexer,DgLexer,NumPyLexer}
  -cr CURSOR, --cursor CURSOR

Python:
  Python Options

  -i INTERACT_IT, --interact-it INTERACT_IT
                        Inspect interactively after running script
  -q, --quiet           Don't print version and copyright messages on interactive startup
```