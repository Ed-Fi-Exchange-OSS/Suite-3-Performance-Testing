# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""Build automation scripts"""

import os
from subprocess import run
import shutil
import sys
from typing import List


def _display_help():
    message = """Please specify a command followed by a module. Valid commands:
* install
* test
* coverage
* coverage:html
* coverage:xml
* lint
* typecheck
* typecheck:xml
* build
* publish
* ci:test
* ci:publish
For example, to run unit tests with code coverage, on utility `edfi-paging-test`:
> ./build.py coverage:xml edfi_paging_test
"""
    print(message)
    exit(-1)


def _run_command(command: List[str], exit_immediately: bool = True):

    print("\033[95m" + " ".join(command) + "\033[0m")

    # On Windows, must run inside of cmd.exe in order to get the user's $PATH.
    if os.name == "nt":
        # All versions of Windows are "nt"
        command = ["cmd", "/c", *command]

    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    package_name = sys.argv[2]

    package_dir = os.path.join(script_dir, "..", "src", package_name)
    if not os.path.exists(package_dir):
        raise RuntimeError(f"Cannot find package {package_name}")

    print(package_dir)
    result = run(command, cwd=package_dir)

    return_code = result.returncode

    if exit_immediately:
        # Exits the script regardless of the prior return code
        exit(return_code)

    if return_code != 0:
        # Only exits the script for non-zero return code
        exit(return_code)


def _run_install(exit_immediately: bool = True):
    _run_command(["poetry", "install"], exit_immediately)


def _run_tests(exit_immediately: bool = True):
    _run_command(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "pytest",
            "tests",
        ],
        exit_immediately,
    )


def _run_coverage_without_report():
    _run_command(
        [
            "poetry",
            "run",
            "coverage",
            "run",
            "-m",
            "pytest",
            "tests",
            "--junitxml=pytest-junit.xml"
        ],
        exit_immediately=False,
    )


def _run_coverage(exit_immediately: bool = True):
    _run_coverage_without_report()

    _run_command(
        [
            "poetry",
            "run",
            "coverage",
            "report",
        ],
        exit_immediately=exit_immediately,
    )


def _run_coverage_html(exit_immediately: bool = True):
    _run_coverage(exit_immediately)

    _run_command(
        [
            "poetry",
            "run",
            "coverage",
            "html",
        ],
        exit_immediately,
    )


def _run_coverage_xml():
    _run_coverage_without_report(
        [
            "poetry",
            "run",
            "coverage",
            "run",
            "-m",
            "pytest",
            "tests",
        ],
        exit_immediately=False,
    )

    _run_command(["poetry", "run", "coverage", "xml"], exit_immediately=False)


def _run_lint(exit_immediately: bool = True):
    _run_command(["poetry", "run", "flake8"], exit_immediately)


def _run_typecheck():
    _run_command(["poetry", "run", "mypy"], exit_immediately=True)


def _run_typecheck_xml(exit_immediately: bool = True):
    _run_command(["poetry", "run", "mypy", "--junit-xml", "mypy-junit.xml"], exit_immediately)


def _run_build(exit_immediately: bool = True):
    _run_command(["poetry", "build"], exit_immediately)


def _run_publish(exit_immediately: bool = True):
    shutil.rmtree("dist", ignore_errors=True)

    _run_build(False)

    _run_command(["poetry", "run", "twine", "upload", "dist/*"], exit_immediately)


def _run_ci_test():
    """
    Calls the commands required for a continuous unit testing, type-checking, and linting job.
    """
    _run_install(False)
    _run_coverage_html(False)
    _run_typecheck_xml(False)
    _run_lint(True)


def _run_ci_publish():
    """
    Calls the commands required for a continuous integration publishing job.
    """
    _run_install(False)
    _run_tests(False)
    _run_publish(True)


if __name__ == "__main__":
    if not sys.version_info >= (3, 9):
        print("This program requires Python 3.9 or newer.", file=sys.stderr)
        exit(-1)

    if len(sys.argv) < 3:
        _display_help()

    switcher = {
        "install": _run_install,
        "test": _run_tests,
        "coverage": _run_coverage,
        "coverage:html": _run_coverage_html,
        "coverage:xml": _run_coverage_xml,
        "lint": _run_lint,
        "typecheck": _run_typecheck,
        "typecheck:xml": _run_typecheck_xml,
        "build": _run_build,
        "publish": _run_publish,
        "ci:test": _run_ci_test,
        "ci:publish": _run_ci_publish,
    }

    switcher.get(sys.argv[1], _display_help)()
