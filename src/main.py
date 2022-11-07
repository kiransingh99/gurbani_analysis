# ------------------------------------------------------------------------------
# main.py - Main handler for Gurbani Analysis CLI
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Main handler for Gurbani Analysis CLI."""

__all__ = []

import argparse
import sys

import _cmn
import _hukamnama


def main():
    """
    Main handler for Gurbani Analysis CLI. Calls callbacks based on the
    subcommand received.
    """
    rc = _cmn.RC.SUCCESS

    # Common parsing
    verbosity_parser = argparse.ArgumentParser(add_help=False)
    verbosity_group = verbosity_parser.add_mutually_exclusive_group()
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
    verbosity_group.add_argument(
        "-s",
        "--suppress-output",
        action="store_const",
        const=_cmn.Verbosity.SUPPRESSED,
        dest="verbosity",
        help="Suppress logging output",
    )

    # Main parser
    parser = argparse.ArgumentParser(
        description="Collect and analyse data about Gurbani."
    )
    composition = parser.add_subparsers(dest="composition")

    # Hukamnama
    hukamnama = composition.add_parser(
        "hukamnama",
        description="Data regarding hukamnama archives."
    )
    hukamnama_subparser = hukamnama.add_subparsers(dest="function")

    ## Hukamnama -> Data
    data = hukamnama_subparser.add_parser(
        _hukamnama.Function.DATA.value,
        description="Update database from archives.",
        parents=[verbosity_parser]
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
    print("verbosity:", args.verbosity)
    if args.verbosity is None:
        args.verbosity = _cmn.Verbosity.STANDARD
        print(args)

    if rc.is_ok():
        subparser = None
        if args.composition == "hukamnama":
            subparser = _hukamnama

        if subparser is not None:
            rc = subparser.parse(args)
        else:
            raise NotImplementedError

    sys.exit(rc)


if __name__ == "__main__":
    main()
