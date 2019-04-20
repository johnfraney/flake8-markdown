import argparse
import glob
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor


def non_matching_lookbehind(pattern):
    return r'(?<={})'.format(pattern)


def non_matching_lookahead(pattern):
    return r'(?={})'.format(pattern)


def matching_group(pattern):
    return r'({})'.format(pattern)


def non_matching_group(pattern):
    return r'(?:{})'.format(pattern)


ONE_OR_MORE_LINES_NOT_GREEDY = r'(?:.*\n)+?'

regex_rule = ''.join([
    # Use non-matching group instead of a lookbehind because the code
    # block may have line highlighting hints. See:
    # https://python-markdown.github.io/extensions/fenced_code_blocks/#emphasized-lines
    non_matching_group('^```python.*$'),
    matching_group(ONE_OR_MORE_LINES_NOT_GREEDY),
    non_matching_lookahead('^```')
])

regex = re.compile(regex_rule, re.MULTILINE)


def lint_markdown_file(markdown_file_path):
    linting_errors = []
    markdown_content = open(markdown_file_path, 'r').read()
    code_block_start_lines = []
    for line_no, line in enumerate(markdown_content.split('\n'), start=1):
        if line.startswith('```python'):
            code_block_start_lines.append(line_no)
    matches = regex.findall(markdown_content)
    for match_number, match in enumerate(matches):
        match_text = match.lstrip()
        flake8_process = subprocess.run(
            ['flake8', '-'],
            capture_output=True,
            input=match_text,
            encoding='ascii',
        )
        flake8_output = flake8_process.stdout
        markdown_line_number = code_block_start_lines[match_number] + 1
        # Replace reference to stdin line number with file line number
        flake8_output = re.sub(
            r'stdin:[0-9]+',
            '{}:{}'.format(markdown_file_path, markdown_line_number),
            flake8_output
        )
        stripped_output = flake8_output.strip()
        if stripped_output:
            linting_errors.append(stripped_output)
    if linting_errors:
        linting_error_output = '\n'.join(linting_errors)
        print(linting_error_output)


def lint_markdown_glob(markdown_glob):
    files = glob.iglob(markdown_glob, recursive=True)
    with ThreadPoolExecutor() as executor:
        executor.map(lint_markdown_file, files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Markdown globs')
    parser.add_argument(
        'globs',
        metavar='glob',
        type=str,
        nargs='+',
        help='a glob of Markdown files to lint',
    )
    args = parser.parse_args()
    markdown_globs = args.globs
    with ThreadPoolExecutor() as executor:
        executor.map(lint_markdown_glob, markdown_globs)
