import pytest
import subprocess
import sys
from flake8_markdown.constants import SUBPROCESS_ARGS

FILE_WITH_ERRORS = "tests/samples/basic.md"
FILE_WITHOUT_ERRORS = "tests/samples/good.md"
FILE_WITH_EMPHASIZED_LINES = "tests/samples/emphasized_lines.md"
FILE_WITH_PYCON_BLOCKS = "tests/samples/pycon.md"


@pytest.fixture
def run_flake8_markdown():
    def do_run_flake8_markdown(*args):
        process = subprocess.run(
            ("flake8-markdown",) + args,
            **SUBPROCESS_ARGS,
        )
        return process

    return do_run_flake8_markdown


def test_run_as_module():
    flake8_markdown_process = subprocess.run(
        ["python", "-m", "flake8_markdown"],
        **SUBPROCESS_ARGS,
    )
    output = flake8_markdown_process.stderr
    assert "__main__.py" in str(output)


def test_run_without_arguments(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown()
    output = flake8_markdown_process.stderr
    assert "error: the following arguments are required: glob" in output
    return_code = flake8_markdown_process.returncode
    assert return_code > 0


def test_run_with_non_matching_glob(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown("non_existant_file.md")
    assert flake8_markdown_process.returncode == 0


def test_run_with_matching_single_file_with_linting_errors(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown(FILE_WITH_ERRORS)
    assert flake8_markdown_process.returncode == 1

    output = flake8_markdown_process.stdout
    if sys.version_info < (3, 10):
        assert "tests/samples/basic.md:8:48: E999" in output
    elif sys.version_info >= (3, 10):
        assert "tests/samples/basic.md:8:8: E999" in output
    assert "tests/samples/basic.md:14:7" in output
    # this case covers the shorthand ```py
    assert "tests/samples/basic.md:20:1: F401" in output


def test_run_with_matching_single_file_wihout_linting_errors(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown(FILE_WITHOUT_ERRORS)
    assert flake8_markdown_process.returncode == 0


def test_run_with_multiple_files(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown(FILE_WITH_ERRORS, FILE_WITHOUT_ERRORS)
    assert flake8_markdown_process.returncode == 1


def test_run_with_file_containing_emphasized_lines(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown(FILE_WITH_EMPHASIZED_LINES)
    output = flake8_markdown_process.stdout
    assert flake8_markdown_process.returncode == 1
    # noqa:
    assert (
        "tests/samples/emphasized_lines.md:6:1: F821 undefined name 'emphasized_imaginary_function'"
        in output
    )


def test_run_with_file_containing_pycon_blocks(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown(FILE_WITH_PYCON_BLOCKS)
    output = flake8_markdown_process.stdout
    print(output)
    assert flake8_markdown_process.returncode == 1
    error_count = len(output.splitlines())
    assert error_count == 3
    assert "tests/samples/pycon.md:10:11: F821" in output
    if sys.version_info < (3, 10):
        assert "tests/samples/pycon.md:17:10: E999" in output
    elif sys.version_info >= (3, 10):
        assert "tests/samples/pycon.md:17:2: E999" in output
    assert "tests/samples/pycon.md:25:1: F821" in output


def test_run_with_glob(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown("tests/samples/*.md")
    assert flake8_markdown_process.returncode == 1
    output = flake8_markdown_process.stdout
    assert FILE_WITH_ERRORS in output
    assert FILE_WITH_EMPHASIZED_LINES in output


def test_run_with_recursive_glob(run_flake8_markdown):
    flake8_markdown_process = run_flake8_markdown("tests/**/*.md")
    assert flake8_markdown_process.returncode == 1
    output = flake8_markdown_process.stdout
    assert FILE_WITH_ERRORS in output
    assert FILE_WITH_EMPHASIZED_LINES in output
