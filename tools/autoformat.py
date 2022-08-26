import argparse
import enum
import subprocess
import sys


class _BlackReturnCodes(enum.IntEnum):
    """Return codes that can be received from black."""

    NOTHING_TO_CHANGE = 0  # all files changed, or no files need to change
    NEED_TO_REFORMAT = 1
    FILE_DOES_NOT_EXIST = 2


def _run_cmd(args):
    """
    Runs `black` command based on input parameters.

    :param args:
        Namespace object with args tp run black with.

    :returns:
        CompletedProcess namespace object with command ran and returncode.
    """
    cmd = (
        [
            "black",
            "--check" if args.check else None,
            "--quiet" if args.quiet else None,
            "--verbose" if args.verbose else None,
        ]
        + args.files
        + (["--exclude"] + args.exclude if args.exclude else [None])
    )
    cmd = list(filter(lambda x: x is not None, cmd))

    p = subprocess.run(cmd)

    return p


def _handle_return_code(process):
    """
    Handles the return code received when running the black CLI. If there's an
    unexpected error code, an error message is printed to log this. Then exits
    the script with the same return code as received from black.

    :param process:
        CompletedProcess namespace object with command ran and returncode.
    """
    # Check if return code is known.
    try:
        _BlackReturnCodes(process.returncode)
    except ValueError:
        print(
            "\nAn unexpected error occurred when running the command: '{}'".format(
                " ".join(process.args)
            )
        )
    finally:
        sys.exit(process.returncode)


def main():
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
    parser.add_argument("-e", "--exclude", nargs="*", help="list of files to skip")
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
        help="Also emit messages to stderr about files that were not changed or were ignored due to exclusion patterns.",
    )

    args = parser.parse_args()

    p = _run_cmd(args)
    _handle_return_code(p)


if __name__ == "__main__":
    main()
