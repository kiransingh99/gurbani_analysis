#!/usr/bin/python3
# ------------------------------------------------------------------------------
# mut.py - Run MUT and code coverage
#
# February 2023, Gurkiran Singh
#
# Copyright (c) 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Runs MUT, and optionally code coverage on the source code."""

from __future__ import annotations

__all__: list[str] = []

from typing import overload, Union

import argparse
import re
import subprocess
import sys

import cmn


class _UnitTestReturnCodes(cmn.ReturnCodes):
    """Possible exit codes from the unittest module, with some locally
    introduced ones."""

    PASS = 0
    FAIL = 1
    CLI_ERROR = 2

    COVERAGE_LOW = 3
    COMMAND_NOT_FOUND = 127


@overload
def _run_cmd(cmd: list[str]) -> int:
    ...


@overload
def _run_cmd(cmd: list[str], *, capture_output: bool) -> tuple[int, str]:
    ...


def _run_cmd(
    cmd: list[str], *, capture_output: bool = False
) -> Union[int, tuple[int, str]]:
    """Run a given command in the bash prompt.

    :param cmd: the command to run.
    :param capture_output: True, to return stdout. False to print it,
    :return: a tuple of (return code, stdout)
    """
    try:
        output = subprocess.run(cmd, capture_output=capture_output, check=False)
    except FileNotFoundError as exc:
        if exc.errno is cmn.WinErrorCodes.FILE_NOT_FOUND.value:
            cmn.handle_missing_package_error(exc.filename)
            rc = _UnitTestReturnCodes.COMMAND_NOT_FOUND
        else:
            raise
    except subprocess.CalledProcessError as exc:
        cmn.handle_cli_error(_UnitTestReturnCodes, exc.returncode, exc.cmd, exc)
        rc = _UnitTestReturnCodes.CLI_ERROR
    else:
        rc = output.returncode

    if capture_output:
        return rc, output.stdout.decode("utf-8")

    return rc


def _run_cov() -> int:
    """Run coverage checks. Requires MUT to be passing.

    :return: Return code from MUT and coverage checks.
    """
    rc = _run_cmd(
        [
            "coverage",
            "run",
            "--source",
            "src/",
            "-m",
            "unittest",
            "discover",
        ]
    )

    if cmn.ReturnCodes.is_ok(rc):
        rc, output = _run_cmd(["coverage", "report"], capture_output=True)
    else:
        print("Check MUT is passing before running coverage!")

    if cmn.ReturnCodes.is_ok(rc):
        coverage = int(re.findall(r" (\d+)%", output)[-1])
        print(f"Code coverage is {coverage}")
        if coverage != 100:
            rc = _UnitTestReturnCodes.COVERAGE_LOW

    return rc


def _run_mut(args: argparse.Namespace) -> int:
    """Run MUT.

    :param args: Namespace object with args to run check on.
    :return: return code from CLI.
    """
    if args.coverage:
        return _run_cov()

    cmd = [cmn.which_python(), "-m", "unittest"]
    cmd.append(*args.modules)

    if args.testcases:
        for module in args.testcases:
            cmd.append("-k")
            cmd.append(module)

    rc = _run_cmd(cmd)

    return rc


def main() -> None:
    """Main function for MUT and coverage CLI. Parses and handles CLI input."""
    parser = argparse.ArgumentParser(description="Run MUT on given files.")

    parser.add_argument(
        "-c",
        "--coverage",
        action="store_true",
        help="Collect code coverage. Ignores all other arguments.",
    )

    parser.add_argument(
        "-m",
        "--modules",
        nargs="+",
        default=["discover"],
        action="store",
        help="Module(s) to run",
    )

    parser.add_argument(
        "-t",
        "--testcases",
        nargs="+",
        action="store",
        help="Testcase(s) to run",
    )

    args = parser.parse_args()

    rc = _run_mut(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
