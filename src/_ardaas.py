# ------------------------------------------------------------------------------
# _ardaas.py - Ardaas generator
#
# June 2023, Gurkiran Singh
#
# Copyright (c) 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Handler for ardaas subparser."""

from __future__ import annotations

__all__ = []

import _cmn

_log = _cmn.Logger("ardaas")


def _generate(ctx: argparse.Namespace) -> None:
    """Handler for all generate requests to the Ardaas CLI.

    :param ctx: context about the original instruction.
    """
    output = ["Awp jI dy hJur"]
    end = [
        "AKr vWDw Gwtw Bul cuk mWP krnI.",
        "srbq dy kwrj rWs krny."
        "seI ipAwry myl ijnW imilAWM qyrw nwm icq AWvy.",
        "nwnk nwm crdI klW.",
        "qyry Bwny srbq dw Blw.",
    ]
    # Awp jI dy hzUr A~Kr vwDw Gwtw Bul cuk mwP krnI. srb~q dy kwrj rws krny. seI ipAwry myl ijnHW imilAWM qyrw nwm icq Awvy. nwnk nwm cVdI klw. qyry Bwny srb~q dw Blw

    print(" ".join(output + end))


def parse(ctx: argparse.Namespace) -> None:
    """Main handler for Ardaas CLI. This is the API called by the main
    Gurbani Analysis CLI.

    :param ctx: context received from the Gurbani Analysis CLI. Namespace object
        containing the args received by the CLI.
    """
    _log.set_level(ctx.verbosity)
    _generate(ctx)

    return _cmn.RC.SUCCESS
