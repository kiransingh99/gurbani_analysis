# ------------------------------------------------------------------------------
# lint.py - Run pylint
#
# September 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Linter for python scripts in repo."""

import argparse
import subprocess

import cmn


class _PylintReturnCodes(cmn.ReturnCodes):
    """Return codes that can be received from pylint."""

    SUCCESS = 0
    ERROR = 1


def _run_lint(args):
    """
    Runs pylint on python files in workspace.

    :param args:
        Namespace object with args to run lint with.
    """

    def _filter_python_files(files):
        """
        Filters a set of file names and returns a subset of *.py filenamess from
        it.

        :param files:
            File names to be filtered.

        :return:
            Subset of file names ending with `.py`.
        """
        filtered = set()
        for file in files:
            if file.endswith(".py"):
                filtered.add(file)

        return filtered

    tracked_files_output = subprocess.run(
        "git ls-files", capture_output=True, check=True
    )
    include_file_unfiltered = set(
        tracked_files_output.stdout.decode("utf-8").split("\n")
    )

    if args.untracked_files:
        untracked_files_output = subprocess.run(
            "git ls-files --others", capture_output=True, check=True
        )
        include_file_unfiltered.update(
            set(untracked_files_output.stdout.decode("utf-8").split("\n"))
        )

    include_files = _filter_python_files(include_file_unfiltered)

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
