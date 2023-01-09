#!/usr/bin/python3
# ------------------------------------------------------------------------------
# lint.py - Run pylint
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Linter for python scripts in repo."""

from __future__ import annotations

__all__: list[str] = []

import argparse
import subprocess
import sys

import cmn


class _LintReturnCodes(cmn.ReturnCodes):
    """Return codes that can be received from pylint."""

    SUCCESS = 0
    # Error code 1 means a fatal error was hit
    ERROR = 2
    WARNING = 4
    ERROR_WARNING = 6
    REFACTOR = 8
    ERROR_REFACTOR = 10
    WARNING_REFACTOR = 12
    ERROR_WARNING_REFACTOR = 14
    CONVENTION = 16
    ERROR_CONVENTION = 18
    WARNING_CONVENTION = 20
    ERROR_WARNING_CONVENTION = 22
    REFACTOR_CONVENTION = 24
    ERROR_REFACTOR_CONVENTION = 26
    WARNING_REFACTOR_CONVENTION = 28
    ERROR_WARNING_REFACTOR_CONVENTION = 30
    USAGE_ERROR = 32

    COMMAND_NOT_FOUND = 200


def _run_lint(args: argparse.Namespace) -> int:
    """
    Runs pylint on python files in workspace.

    :param args:
        Namespace object with args to run lint with.

    :return:
        Return code from CLI.
    """
    rc = _LintReturnCodes.SUCCESS

    include_files = cmn.get_python_files(args.untracked_files)

    cmd = [cmn.which_python(), "-m", "pylint"] + list(include_files)

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        if exc.errno is cmn.WinErrorCodes.FILE_NOT_FOUND.value:
            cmn.handle_missing_package_error(exc.filename)
            rc = _LintReturnCodes.COMMAND_NOT_FOUND
        else:
            raise
    except subprocess.CalledProcessError as exc:
        cmn.handle_cli_error(_LintReturnCodes, exc.returncode, exc.cmd, exc)
        rc = _LintReturnCodes.USAGE_ERROR

    return rc


def main() -> None:
    """Main function for pylint CLI. Parses and handles CLI input."""
    parser = argparse.ArgumentParser(description="Run pylint on given files.")
    parser.add_argument(
        "-u",
        "--untracked-files",
        action="store_true",
        default=False,
        help="run on files untracked by git",
    )

    args = parser.parse_args()

    rc = _run_lint(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
