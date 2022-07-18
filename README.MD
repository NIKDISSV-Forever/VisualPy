Interactive console with syntax highlighting and tooltips.

Works with both _CPython_ and _PyPy_.

# Installing

> pip install [VisualPy](https://pypi.org/project/VisualPy) -U

# Usage

> python -m vpy

> General
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/main.png)
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/many_options.png)

> CPython
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/CPython.png)

> Imports
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/import_hints.png)
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/import.png)

> Dark Theme (Default)
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/dark_theme.png)
> Light Theme (-dbg --darkbg flag)
![](https://github.com/NIKDISSV-Forever/VisualPython/raw/main/screenshots/light_theme.png)

# Arguments

```
usage: vpy [-h] [-dbg]
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