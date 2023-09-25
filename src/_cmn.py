# ------------------------------------------------------------------------------
# _cmn.py - Common file for Gurbani Analysis CLI
#
# November 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Common objects for the Gurbani Analysis CLI."""

from __future__ import annotations

__all__ = [
    "Error",
    "Logger",
    "NotImplementedException",
    "RC",
    "UnhandledExceptionError",
    "Verbosity",
    "gurbani_ascii_to_unicode",
]

from typing import Any, Optional

import enum
import logging


class Error(Exception):
    """Base error class for all errors in the Gurbani Analysis CLI."""

    def __init__(
        self,
        msg: str,
        *,
        rc: Optional[RC] = None,
        suggested_steps: Optional[list[str]] = None,
    ):
        self.rc = rc
        self.msg = msg
        self.suggested_steps = suggested_steps

    def __str__(self) -> str:
        output = "\nError: "
        output += self.msg + "\n"
        if self.suggested_steps:
            output += " Suggested steps:\n"
            for step in self.suggested_steps:
                output += f"  - {step}\n"

        return output


class Logger:
    """Handles logging for the CLI."""

    def __init__(self, name: str):
        self.logger = logging.Logger(name)
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)

    def _log(self, level: Verbosity, *msg: Any) -> None:
        """Logging function.

        :param level: level at which to log the message.
        :param *msg: message to log.
        """
        self.logger.log(level.value, "".join(str(item) for item in msg))

    def set_level(self, level: Verbosity) -> None:
        """Set the level of the logger.

        :param level: verbosity of logging output.
        """
        self.handler.setLevel(level.value)

    def suppressed(self, *msg: Any) -> None:
        """Suppressed level logging.

        :param *msg: message to log.
        """
        self._log(Verbosity.SUPPRESSED, *msg)

    def standard(self, *msg: str) -> None:
        """Standard level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.STANDARD, *msg)

    def verbose(self, *msg: str) -> None:
        """Verbose level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.VERBOSE, *msg)

    def very_verbose(self, *msg: str) -> None:
        """Very verbose level logging.

        :param msg: message to log.
        """
        self._log(Verbosity.VERY_VERBOSE, *msg)


class NotImplementedException(Error):
    """Custom error type for unimplemented code."""

    def __init__(self, traceback: str):
        msg = "This code path was not implemented.\n" + traceback
        suggested_steps = [
            "Contact the developers and explain the steps to recreate this error."
        ]
        super().__init__(msg, suggested_steps=suggested_steps)


class RC(enum.Enum):
    """Return codes that can be output from this script."""

    # Misc
    SUCCESS = "00"
    UNHANDLED_ERROR = "10"

    # Parser errors
    LOAD_WEBPAGE_ERROR = "20"
    SCRAPE_HTML_ERROR = "21"

    # Development errors
    NOT_IMPLEMENTED = "90"

    def is_ok(self) -> bool:
        """Determines if error shows that an error has occurred.

        :return: True if error code does not signify an error, False otherwise.
        """
        return self in [self.SUCCESS]


class UnhandledExceptionError(Error):
    """Custom error type to reraise when there's an unhandled exception raised
    by an imported library.
    """

    def __init__(self, msg: str):
        msg = "The following exception was not handled:\n" + msg
        super().__init__(msg)


class Verbosity(enum.Enum):
    """Verbosity of output from CLI."""

    SUPPRESSED = 25
    STANDARD = 20
    VERBOSE = 15
    VERY_VERBOSE = 10


def gurbani_unicode_to_romanised(unicode):
    grammar_mapping = {
        " ": " ",  # space
        "[": ".",  # full stop
        "]": ".",  # double full stop
        ".": ".",  # full stop (probably used in elipses)
        ",": ",",  # comma
    }
    oora_aera_eeri_mapping = {
        # For oora aera and eeri, add mukta sound. Presence of a vowel will
        # modify this further.
        "a": "",  # oora
        "A": "a",  # aera
        "e": "",  # eeri
    }
    consonant_mapping = {
        # Oora, aera and eeri are in the vowels mapping as they follow that
        # pattern better.
        "s": "s",  # sassa
        "h": "h",  # haha
        "k": "k",  # kakka
        "K": "kh",  # khakha
        "g": "g",  # gagga
        "G": "gh",  # ghagha
        "|": "ng",  # nganga
        "c": "ch",  # chacha
        "C": "chh",  # chhachha
        "j": "j",  # jaja
        "J": "jh",  # jhajha
        "\\": "nj",  # njanja
        "t": "tt",  # tainka
        "T": "tth",  # ttattha
        "f": "dd",  # ddadda
        "F": "ddh",  # ddhaddha
        "x": "ṉ",  # nana
        "q": "t",  # tata
        "Q": "th",  # thatha
        "d": "d",  # dada
        "D": "dh",  # dhadha
        "n": "n",  # nana
        "p": "p",  # pappa
        "P": "ph",  # phapha
        "b": "b",  # babba
        "B": "bh",  # bhabha
        "m": "m",  # mamma
        "X": "y",  # yaya
        "r": "r",  # rara
        "l": "l",  # lala
        "v": "v",  # vava
        "V": "ṙ",  # rrarra
        "S": "sh",  # shasha
        "Z": "ghh",  # ghhaghha
        "@@@": "",  # khhakhha @@@
        "z": "z",  # zazza
        "@@@": "",  # faffa @@@
        "L": "ḷ",  # lalla pair bindi
    }
    pairee_mapping = {
        "H": "h",  # haha
        "R": "r",  # rara
    }
    vowel_mapping = {
        # True vowels.
        "w": "aa",  # kannaa
        "W": "aaṅ",  # kannaa bindi
        "i": "i",  # sihaari
        "I": "ee",  # bihaari
        "u": "u",  # aunkar
        "U": "oo",  # dulainkar
        "o": "o",  # horaa
        "O": "ou",  # kanhaura
        "y": "ae",  # laav
        "Y": "ai",  # dulaav
    }
    semi_vowel_mapping = {
        "N": "ṅ",  # bindee
        "M": "ṅ",  # tippee
        "µ": "ṅ",  # tippee
    }
    special_mapping = {
        "~": None,  # adhak
        "`": None,  # adhak
    }

    mapping = {}
    mapping.update(grammar_mapping)
    mapping.update(oora_aera_eeri_mapping)
    mapping.update(consonant_mapping)
    mapping.update(pairee_mapping)
    mapping.update(vowel_mapping)
    mapping.update(semi_vowel_mapping)
    mapping.update(special_mapping)

    romanised = []
    buf = ""
    adhak = False

    for i, char in enumerate(unicode):
        mapped_char = mapping[char]

        if romanised and char == " ":
            if romanised[-1] in ("u", "i"):
                romanised = romanised[:-1] + ["(" + romanised[-1] + ")"]
        if char == "i":  # sihaari
            buf = mapped_char
        elif char in pairee_mapping.keys():
            if romanised[-1] == "i":
                romanised = romanised[:-2] + [mapped_char, romanised[-1]]
            else:
                romanised.append(mapped_char)
        elif char == "~":  # adhak
            adhak = True
        else:
            if romanised and romanised[-1].lower() == "a" and "aa" in mapped_char:
                romanised[-1] = ""
            # For consecutive consonants, and for vowels after oora aera eeri, add mukta sound between them
            elif romanised and (
                (
                    romanised[-1].lower() in consonant_mapping.values()
                    and char
                    in list(oora_aera_eeri_mapping.keys())
                    + list(consonant_mapping.keys())
                    + list(pairee_mapping.keys())
                )
                or (
                    romanised[-1].lower() in oora_aera_eeri_mapping.values()
                    and char in vowel_mapping.keys()
                )
            ):
                romanised[-1] += "a"
            if mapped_char:
                if adhak:
                    mapped_char = mapped_char.upper()
                    adhak = False
                romanised.append(mapped_char)
            if buf:
                romanised.append(buf)
                buf = ""

    return "".join(romanised)


gurbani_unicode_to_romanised("ijnI nwmu iDAwieAw gey mskiq Gwil ]")
