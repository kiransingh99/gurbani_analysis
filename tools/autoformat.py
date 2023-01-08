# ------------------------------------------------------------------------------
# autoformat.py - Script to check for correctly formatted code
#
# August 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Checks for badly formatted code and optionally reformats it."""

from __future__ import annotations

__all__: list[str] = []

import argparse
import subprocess

import cmn


class _BlackReturnCodes(cmn.ReturnCodes):
    """Return codes that can be received from black."""

    NOTHING_TO_CHANGE = 0  # all files changed, or no files need to change
    NEED_TO_REFORMAT = 1
    FILE_DOES_NOT_EXIST = 2
    COMMAND_NOT_FOUND = 127


def _run_black(args: argparse.Namespace) -> None:
    """
    Runs `black` command based on input parameters.

    :param args:
        Namespace object with args to run black with.
    """

    cmd = ["python", "-m", "black"]
    if args.check:
        cmd.append("--check")
    if args.quiet:
        cmd.append("--quiet")
    if args.verbose:
        cmd.append("--verbose")

    # Line length is hardcoded to be 80 chars as changing this value
    # could reformat the whole workspace. There is no need for a user to
    # change this value.
    cmd += ["--line-length", "80"]

    cmd += args.files

    if args.exclude:
        cmd += ["--exclude"] + args.exclude

    if args.verbose:
        print(f"Running: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        if exc.errno is cmn.WinErrorCodes.FILE_NOT_FOUND.value:
            cmn.handle_missing_package_error("black")
        else:
            raise
    except subprocess.CalledProcessError as exc:
        cmn.handle_cli_error(_BlackReturnCodes, exc.returncode, exc.cmd, exc)


def main() -> None:
    """Main function for autoformat CLI. Parses and handles CLI input"""
    parser = argparse.ArgumentParser(
        description="Run autoformat checks on given files. Optionally reformat the given files."
    )
    parser.add_argument(
        "files",
        metavar="SRC",
        nargs="*",
        default=["."],
        help="list of files to check",
    )
    parser.add_argument(
        "-e", "--exclude", nargs="*", help="list of files to skip"
    )
    parser.add_argument(
        "-r",
        "--reformat",
        action="store_false",
        dest="check",
        default=True,
        help="reformat the file if it fails the check",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Don't emit non-error messages to stderr. Errors are still emitted.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Also emit messages to stderr about files that were not changed"
        + "or were ignored due to exclusion patterns.",
    )

    args = parser.parse_args()

    _run_black(args)


if __name__ == "__main__":
    main()
