#!/usr/bin/python3
# ------------------------------------------------------------------------------
# mypy.py - Run mypy
#
# January 2023, Gurkiran Singh
#
# Copyright (c) 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Runs mypy on python scripts in repo."""

from __future__ import annotations

__all__: list[str] = []

import argparse
import subprocess
import sys

import cmn


class _MypyReturnCodes(cmn.ReturnCodes):
    """Return codes that can be received from pylint."""

    SUCCESS = 0
    USAGE_ERROR = 1

    COMMAND_NOT_FOUND = 200


def _run_mypy(args: argparse.Namespace) -> int:
    """
    Runs mypy on python files in workspace.

    :param args:
        Namespace object with args to run mypy with.

    :return:
        Return code from CLI.
    """
    rc = _MypyReturnCodes.SUCCESS

    cmd = [
        cmn.which_python(),
        "-m",
        "mypy",
        ".",
        "--disallow-untyped-defs",
        "--disallow-incomplete-defs",
        "--ignore-missing-imports",
    ]

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        if exc.errno is cmn.WinErrorCodes.FILE_NOT_FOUND.value:
            cmn.handle_missing_package_error(exc.filename)
            rc = _MypyReturnCodes.COMMAND_NOT_FOUND
        else:
            raise
    except subprocess.CalledProcessError as exc:
        cmn.handle_cli_error(_MypyReturnCodes, exc.returncode, exc.cmd, exc)
        rc = _MypyReturnCodes.USAGE_ERROR

    return rc


def main() -> None:
    """Main function for mypy CLI. Parses and handles CLI input."""
    parser = argparse.ArgumentParser(description="Run mypy on given files.")

    args = parser.parse_args()

    rc = _run_mypy(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
