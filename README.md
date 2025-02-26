# Flake8 Markdown

[
![PyPI](https://img.shields.io/pypi/v/flake8-markdown.svg)
![PyPI](https://img.shields.io/pypi/pyversions/flake8-markdown.svg)
![PyPI](https://img.shields.io/github/license/johnfraney/flake8-markdown.svg)
](https://pypi.org/project/flake8-markdown/)
[![PyPI downloads per month](https://img.shields.io/pypi/dm/flake8-markdown.svg)](https://pypi.python.org/pypi/flake8-markdown/)
[![Tox](https://github.com/johnfraney/flake8-markdown/actions/workflows/github-actions-tox.yml/badge.svg)](https://github.com/johnfraney/flake8-markdown/actions/workflows/github-actions-tox.yml)

Flake8 Markdown lints [GitHub-style Python code blocks](https://help.github.com/en/articles/creating-and-highlighting-code-blocks#fenced-code-blocks) in Markdown files using [`flake8`](https://flake8.readthedocs.io/en/stable/).

This package helps improve a Python project's documentation by ensuring that code samples are error-free.

## Features

- Lints code blocks containing regular Python and Python interpreter code ([`pycon`](http://pygments.org/docs/lexers/#pygments.lexers.python.PythonConsoleLexer))
- [pre-commit](#pre-commit-hook) hook to lint on commit

## Installation

Flake8 Markdown can be installed from PyPI using `pip` or your package manager of choice:

```shell
pip install flake8-markdown
```

## Usage

### CLI

You can use Flake8 Markdown as a CLI tool using the `flake8-markdown` command.

`flake8-markdown` accepts one or more [globs](https://docs.python.org/3.7/library/glob.html) as its arguments.

Example:

```console
$ flake8-markdown "tests/samples/*.md"
tests/samples/emphasized_lines.md:6:1: F821 undefined name 'emphasized_imaginary_function'
tests/samples/basic.md:8:48: E999 SyntaxError: EOL while scanning string literal
tests/samples/basic.md:14:7: F821 undefined name 'undefined_variable'
```

### pre-commit hook

You can also add `flake8-markdown` to your project using [pre-commit](https://pre-commit.com/). When configured, any staged Markdown files will be linted using `flake8-markdown` once you run `git commit`.

To enable this hook in your local repository, add the following `repo` to your `.pre-commit-config.yaml` file:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/johnfraney/flake8-markdown
    rev: v0.5.0
    hooks:
      - id: flake8-markdown
```

## Code of Conduct

Everyone interacting in the project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [PyPA Code of Conduct](https://www.pypa.io/en/latest/code-of-conduct/).
