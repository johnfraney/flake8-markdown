import argparse
import glob
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from flake8_markdown.constants import SUBPROCESS_ARGS

__version__ = '0.2.0'


def non_matching_lookahead(pattern):
    return r'(?={})'.format(pattern)


def matching_group(pattern):
    return r'({})'.format(pattern)


def non_matching_group(pattern):
    return r'(?:{})'.format(pattern)


def strip_repl_characters(code):
    """Removes the first four characters from each REPL-style line.

    >>> strip_repl_characters('>>> "banana"') == '"banana"'
    True
    >>> strip_repl_characters('... banana') == 'banana'
    True
    """
    stripped_lines = []
    for line in code.splitlines():
        if line.startswith('>>> ') or line.startswith('... '):
            stripped_lines.append(line[4:])
        else:
            stripped_lines.append(line)
    return '\n'.join(stripped_lines)


ONE_OR_MORE_LINES_NOT_GREEDY = r'(?:.*\n)+?'

regex_rule = ''.join([
    # Use non-matching group instead of a lookbehind because the code
    # block may have line highlighting hints. See:
    # https://python-markdown.github.io/extensions/fenced_code_blocks/#emphasized-lines
    non_matching_group('^```(python|pycon).*$'),
    matching_group(ONE_OR_MORE_LINES_NOT_GREEDY),
    non_matching_lookahead('^```')
])

regex = re.compile(regex_rule, re.MULTILINE)


def lint_markdown_file(markdown_file_path):
    linting_errors = []
    markdown_content = open(markdown_file_path, 'r').read()
    code_block_start_lines = []
    for line_no, line in enumerate(markdown_content.splitlines(), start=1):
        # Match python and pycon
        if line.startswith('```py'):
            code_block_start_lines.append(line_no)
    code_block_matches = regex.findall(markdown_content)
    for match_number, code_block_match in enumerate(code_block_matches):
        code_block_type = code_block_match[0]
        match_text = code_block_match[1]
        # pycon lines start with ">>> " or "... ", so strip those characters
        if code_block_type == 'pycon':
            match_text = strip_repl_characters(match_text)
        match_text = match_text.lstrip()
        flake8_process = subprocess.run(
            ['flake8', '-'],
            input=match_text,
            **SUBPROCESS_ARGS,
        )
        flake8_output = flake8_process.stdout
        flake8_output = flake8_output.strip()
        # Skip empty lines
        if not flake8_output:
            continue
        flake8_output_split = flake8_output.split(':')
        line_number = int(flake8_output_split[1])
        column_number = int(flake8_output_split[2])
        markdown_line_number = (
            line_number + code_block_start_lines[match_number]
        )
        if code_block_type == 'pycon':
            match_lines = match_text.splitlines()
            line = match_lines[line_number - 1]
            if any([
                    line.startswith('>>> '),
                    line.startswith('... '),
            ]):
                flake8_output_split[2] = column_number + 4
        # Replace reference to stdin line number with file line number
        flake8_output = re.sub(
            r'stdin:[0-9]+',
            '{}:{}'.format(markdown_file_path, markdown_line_number),
            flake8_output
        )
        linting_errors.append(flake8_output)

    if linting_errors:
        linting_error_output = '\n'.join(linting_errors)
        print(linting_error_output)
        return False

    return True


def lint_markdown_glob(markdown_glob):
    files = glob.iglob(markdown_glob, recursive=True)
    passing = True
    with ThreadPoolExecutor() as executor:
        results = executor.map(lint_markdown_file, files)
        for result in results:
            if result is False:
                passing = False

    return passing


def main(argv=None):
    parser = argparse.ArgumentParser(description='Markdown globs')
    parser.add_argument(
        'globs',
        metavar='glob',
        type=str,
        nargs='+',
        help='a glob of Markdown files to lint',
    )
    args = parser.parse_args(argv)
    markdown_globs = args.globs
    passing = True
    with ThreadPoolExecutor() as executor:
        results = executor.map(lint_markdown_glob, markdown_globs)
        for result in results:
            if result is False:
                passing = False

    if not passing:
        sys.exit(1)
    sys.exit(0)
