# ------------------------------------------------------------------------------
# lint.py - Run pylint
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Linter for python scripts in repo."""

__all__ = []

import argparse
import subprocess

import cmn


class _PylintReturnCodes(cmn.ReturnCodes):
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
    # Error code 32 means a usage error was hit


def _run_lint(args):
    """
    Runs pylint on python files in workspace.

    :param args:
        Namespace object with args to run lint with.
    """
    include_files = cmn.get_python_files(args.untracked_files)

    cmd = ["pylint"] + list(include_files)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        cmn.handle_cli_error(_PylintReturnCodes, exc.returncode, exc.cmd, exc)


def main():
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

    _run_lint(args)


if __name__ == "__main__":
    main()
