#!/usr/bin/python3
# ------------------------------------------------------------------------------
# main.py - Main handler for Gurbani Analysis CLI
#
# August 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Main handler for Gurbani Analysis CLI."""

from __future__ import annotations

__all__ = [
    "main",
]


from typing import Optional

import argparse
import sys
import traceback

try:
    import _cmn
    import _hukamnama
except ModuleNotFoundError:
    from . import _cmn
    from . import _hukamnama


_log = _cmn.Logger("main")


def _exit(rc: _cmn.RC, exc: Optional[_cmn.Error] = None) -> None:
    """Exit script with given return code, optionally logging an exception.

    :param rc: return code from script.
    :param exc: log this exception, if given, defaults to None.
    """
    if exc:
        _log.suppressed(exc)
    sys.exit(int(rc.value))


def main() -> None:
    """Main handler for Gurbani Analysis CLI. Calls callbacks based on the
    subcommand received.
    """
    rc = _cmn.RC.SUCCESS
    _log.set_level(_cmn.Verbosity.SUPPRESSED)

    # Main parser
    parser = argparse.ArgumentParser(
        description="Collect and analyse data about Gurbani."
    )

    # Common parsing
    verbosity_parser = argparse.ArgumentParser(add_help=False)
    verbosity_group = verbosity_parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-s",
        "--suppress-output",
        action="store_const",
        const=_cmn.Verbosity.SUPPRESSED,
        dest="verbosity",
        help="Suppress logging output",
    )
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=_cmn.Verbosity.VERBOSE,
        dest="verbosity",
        help="Suppress logging output",
    )
    verbosity_group.add_argument(
        "-V",
        "--very-verbose",
        action="store_const",
        const=_cmn.Verbosity.VERY_VERBOSE,
        dest="verbosity",
        help="Suppress logging output",
    )

    composition = parser.add_subparsers(dest="composition")

    # Hukamnama
    hukamnama = composition.add_parser(
        "hukamnama", description="Data regarding hukamnama archives."
    )
    hukamnama_subparser = hukamnama.add_subparsers(dest="function")

    ## Hukamnama -> Data
    data = hukamnama_subparser.add_parser(
        _hukamnama.Function.DATA.value,
        description="Update database from archives.",
        parents=[verbosity_parser],
    )
    update_method = data.add_mutually_exclusive_group(required=True)
    update_method.add_argument(
        "-w",
        "--write",
        action="store_const",
        const=_hukamnama.DataUpdate.WRITE,
        dest="update",
        help="Starting from the beginning of the archives, (re)populate all"
        "entries until today (overwrites existing data)",
    )
    update_method.add_argument(
        "-u",
        "--update",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE,
        dest="update",
        help="Add information to database, continuing from the most recently"
        "populated entry, until today",
    )
    update_method.add_argument(
        "-U",
        "--update-fill-gaps",
        action="store_const",
        const=_hukamnama.DataUpdate.UPDATE_FILL_GAPS,
        dest="update",
        help="Starting from the beginning of the archives, populate entries "
        "without any data (does not overwrites existing data)",
    )

    args = parser.parse_args()

    # Defaults
    if not hasattr(args, "verbosity") or args.verbosity is None:
        args.verbosity = _cmn.Verbosity.STANDARD

    exception = None

    if rc.is_ok():
        if args.composition == "hukamnama":
            subparser = _hukamnama

            try:
                rc = subparser.parse(args)
            except KeyboardInterrupt:
                pass
            except NotImplementedError:
                rc = _cmn.RC.NOT_IMPLEMENTED
                exception = _cmn.NotImplementedException(traceback.format_exc())
            except _cmn.Error as exc:
                rc = exc.rc
                exception = exc
            except Exception:
                rc = _cmn.RC.UNHANDLED_ERROR
                exception = _cmn.UnhandledExceptionError(traceback.format_exc())
        else:
            parser.print_help()

    _exit(rc, exception)


if __name__ == "__main__":
    main()
