# ------------------------------------------------------------------------------
# _hukamnama.py - Hukamnama parsing
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022 - 2023
# All rights reserved.
# ------------------------------------------------------------------------------

"""Handler for hukamnama subparser."""

from __future__ import annotations

__all__ = [
    "DataUpdate",
    "Function",
    "parse",
]

from collections.abc import Generator, MutableSequence
from functools import cache
from typing import Any, Optional
from urllib.request import Request, urlopen

import argparse
import dataclasses
import datetime
import enum
import json
import os
import re
import urllib

import _cmn

_log = _cmn.Logger("hukamanama")

_BASE_URL = "https://www.sikhnet.com/hukam/archive/"
_DATABASE_PATH = "./artifacts/hukamnama/"
_DATABASE_FILE_EXT = ".json"

_DATE_FORMAT = "%Y-%m-%d"
_FIRST_DATE = "2002-01-01"
_today_date = datetime.datetime.today()


class DataUpdate(enum.IntEnum):
    """Methods of updating data in the database.

    WRITE: Starting from the beginning of the archives, (re)populate all entries
        until today (overwrites existing data).
    UPDATE: Add information to database, continuing from the most recently
        populated entry, until today.
    UPDATE_FILL_GAPS: Starting from the beginning of the archives, populate
        entries without any data (does not overwrites existing data).
    """

    UNKNOWN = 0
    WRITE = 1
    UPDATE = 2
    UPDATE_FILL_GAPS = 3


class Function(enum.Enum):
    """Subfunctions within Hukamnama Analysis.

    DATA: Update/repopulate the database.
    """

    DATA = "data"


class _LineType(enum.IntEnum):
    """Types of lines in Gurbani."""

    MANGLACHARAN = 1
    SIRLEKH = 2
    GURBANI = 3


class _Raags(enum.IntEnum):
    """Raags of shabads."""

    ASA = 4
    GUJRI = 5
    DEVGANDHARI = 6
    BIHAGARA = 7
    WADHANS = 8
    SORATH = 9
    DHANASARI = 10
    JAITSARI = 11
    TODI = 12
    BAIRARI = 13
    TILANG = 14
    SUHI = 15
    BILAAVAL = 16
    GAUND = 17
    RAMKALI = 18

    def __str__(self) -> str:
        raags = {
            self.ASA: "Asa",
            self.GUJRI: "Gujri",
            self.DEVGANDHARI: "Devgandhari",
            self.BIHAGARA: "Bihagra",
            self.WADHANS: "Wadhans",
            self.SORATH: "Sorath",
            self.DHANASARI: "Dhanasari",
            self.JAITSARI: "Jaitsari",
            self.TODI: "Todi",
            self.BAIRARI: "Bairari",
            self.TILANG: "Tilang",
            self.SUHI: "Suhi",
            self.BILAAVAL: "Bilaaval",
            self.GAUND: "Gaund",
            self.RAMKALI: "Ramkali",
        }
        return raags[self]

    @classmethod
    def from_string(cls, raag: str) -> _Raags:
        """Converts a string with a single raag into a _Raags enum value.

        :param raag: string containing name of a raag.
        :raises _RaagError: if a `raag` string could not be matched to a raag.
        :return: enum value corresponding to the `raag` given.
        """
        # pylint: disable=R0912
        if any(r == raag.lower() for r in ["aasaa"]):
            obj = cls.ASA
        elif any(r == raag.lower() for r in ["gujri"]):
            obj = cls.GUJRI
        elif any(r == raag.lower() for r in ["dayv gandhaaree"]):
            obj = cls.DEVGANDHARI
        elif any(r == raag.lower() for r in ["bihaagraa"]):
            obj = cls.BIHAGARA
        elif any(r == raag.lower() for r in ["vadhans"]):
            obj = cls.WADHANS
        elif any(r == raag.lower() for r in ["sorath"]):
            obj = cls.SORATH
        elif any(r == raag.lower() for r in ["dhanaasree"]):
            obj = cls.DHANASARI
        elif any(r == raag.lower() for r in ["jaithsree"]):
            obj = cls.JAITSARI
        elif any(r == raag.lower() for r in ["todee"]):
            obj = cls.TODI
        elif any(r == raag.lower() for r in ["bairaaree"]):
            obj = cls.BAIRARI
        elif any(r == raag.lower() for r in ["tilang"]):
            obj = cls.TILANG
        elif any(r == raag.lower() for r in ["soohee"]):
            obj = cls.SUHI
        elif any(r == raag.lower() for r in ["bilaaval"]):
            obj = cls.BILAAVAL
        elif any(r == raag.lower() for r in ["gond"]):
            obj = cls.GAUND
        elif any(r == raag.lower() for r in ["raamkalee"]):
            obj = cls.RAMKALI
        else:
            raise _RaagError(raag)

        return obj


class _RaagError(_cmn.Error):
    """Error raised when a raag is not recognised by the parser."""

    def __init__(self, raag: str):
        msg = f"The raag '{raag}' was not recognised."
        steps = ["Add a mapping for this raag to a value in the `_Raag` enum."]
        super().__init__(msg, steps)


class _ScrapeHtmlError(_cmn.Error):
    """Error raised when there was a problem scraping values from the html
    source code.
    """

    def __init__(self, attribute_not_found: str):
        msg = f"Could not find the {attribute_not_found}."
        super().__init__(_cmn.RC.SCRAPE_HTML_ERROR, msg)


_ShabadLine = tuple[str, _LineType]
_ShabadLines = dict[int, _ShabadLine]


@dataclasses.dataclass(frozen=True)
class _ShabadMetaData:
    """Object to store information about each shabad recorded.

    id: a unique identifier for the date
    date: date the hukamnama was taken
    ang: ang of the hukamnama
    raag: raag the hukamnama was written in
    writer: the author of the shabad
    first_line: the first line of the shabad
    first_letter: the first consonant of the first line of the hukamnama
    needs_verification: whether the entry needs to be checked
    gurmukhi: the actual shabad
    """

    id: int
    date: str
    ang: Optional[int]
    raag: Optional[_Raags]
    writer: Optional[_Writers]
    gurmukhi: Optional[_ShabadLines]
    first_line: Optional[_ShabadLine]
    first_letter: Optional[str]
    needs_verification: bool = False

    def __eq__(self, other: object) -> bool:
        """A necessary and sufficient condition to determine that two
        _ShabadMetaData objects represent the same shabad is if all the lines of
        the two shabads are the same.

        :return: true if the lines of the two hukamnamas are the same, False
            otherwise.
        """
        if not isinstance(other, _ShabadMetaData):
            return NotImplemented
        return self.gurmukhi == other.gurmukhi

    @classmethod
    def get_id(cls, date: str) -> int:
        """Generates a unique, sequential, integer ID for the date of the
        hukamnama.

        :param date: date of hukamnama as a string, formatted as `_DATE_FORMAT`.
        """
        difference = _str_to_datetime(date) - _str_to_datetime(_FIRST_DATE)
        return difference.days + 1

    @classmethod
    def get_keys(cls) -> list[str]:
        """Get a list of the attributes of this object.

        :return: attributes of _ShabadMetaData object.
        """
        return [item.name for item in dataclasses.fields(cls)]

    def remove_data(self) -> _ShabadMetaData:
        """Return a new _ShabadMetaData object without shabad-specific data.
        Only the ID and date are retained. `needs_verification` is also set to
        True.

        :return: new instance of class without information about the specific
            hukamnama, and flagged as needing verification.
        """
        return _ShabadMetaData(
            id=self.id,
            date=self.date,
            ang=None,
            raag=None,
            writer=None,
            gurmukhi=None,
            first_line=None,
            first_letter=None,
            needs_verification=True,
        )

    def to_dict(self) -> dict[str, Any]:
        """Produces a dictionary that represents a shabad's metadata. Attributes
        with the value `None` are not included.

        return: this object, represented as a dict.
        """
        data = {
            "id": self.id,
            "date": self.date,
            "needs_verification": self.needs_verification,
        }

        if self.ang:
            data["ang"] = self.ang
        if self.writer:
            data["writer"] = self.writer
        if self.raag:
            data["raag"] = self.raag
        if self.gurmukhi:
            data["gurmukhi"] = self.gurmukhi
        if self.first_line:
            data["first_line"] = self.first_line
        if self.first_letter:
            data["first_letter"] = self.first_letter
        return data


class _WriterError(_cmn.Error):
    """Error raised when a writer is not recognised by the parser."""

    def __init__(self, writer: str):
        msg = f"The writer '{writer}' was not recognised."
        steps = [
            "Add a mapping for this writer to a value in the `_Writers` enum."
        ]
        super().__init__(msg, steps)


class _Writers(enum.IntEnum):
    """Writers of shabads."""

    # Gurus: 1-10
    NANAK = 1
    ANGAD = 2
    AMAR_DAS = 3
    RAM_DAS = 4
    ARJAN = 5
    TEGH_BAHADUR = 9
    # Bhagats: 11-25
    KABIR = 11
    RAVIDAS = 12
    NAAMDEV = 16
    BHIKHAN = 18
    # Bhatts: 26-37

    # Gursikhs: 38-40

    def __str__(self) -> str:
        names = {
            self.NANAK: "Guru Nanak Dev Ji",
            self.ANGAD: "Guru Angad Dev Ji",
            self.AMAR_DAS: "Guru Amar Das Ji",
            self.RAM_DAS: "Guru Ram Das Ji",
            self.ARJAN: "Guru Arjan Dev Ji",
            self.TEGH_BAHADUR: "Guru Tegh Bahadur Ji",
            self.KABIR: "Bhagat Kabir Ji",
            self.RAVIDAS: "Bhagat Ravidas Ji",
            self.NAAMDEV: "Bhagat Naamdev Ji",
            self.BHIKHAN: "Bhagat Bhikhan Ji",
        }
        return names[self]

    @classmethod
    def from_string(cls, name: str) -> _Writers:
        """Converts a string with a single writer's name into a _Writers enum
        value.

        :param name: string containing name of a writer.
        :raises _WriterError: if a `name` string could not be matched to a
            writer.
        :return: enum value corresponding to the `name` given.
        """
        if any(s == name.lower() for s in ["guru nanak dev ji"]):
            obj = cls.NANAK
        elif any(s == name.lower() for s in ["guru angad dev ji"]):
            obj = cls.ANGAD
        elif any(s == name.lower() for s in ["guru amar daas ji"]):
            obj = cls.AMAR_DAS
        elif any(s == name.lower() for s in ["guru raam daas ji"]):
            obj = cls.RAM_DAS
        elif any(s == name.lower() for s in ["guru arjan dev ji"]):
            obj = cls.ARJAN
        elif any(s == name.lower() for s in ["guru tegh bahaadur ji"]):
            obj = cls.TEGH_BAHADUR
        elif any(s == name.lower() for s in ["bhagat kabeer ji"]):
            obj = cls.KABIR
        elif any(s == name.lower() for s in ["bhagat ravi daas ji"]):
            obj = cls.RAVIDAS
        elif any(s == name.lower() for s in ["bhagat naam dev ji"]):
            obj = cls.NAAMDEV
        elif any(s == name.lower() for s in ["bhagat bheekhan ji"]):
            obj = cls.BHIKHAN
        else:
            raise _WriterError(name)

        return obj


def _data(ctx: argparse.Namespace) -> None:
    """Handler for all data requests to the Hukamnama CLI.

    :param ctx: context about the original instruction.
    """
    _log.very_verbose("Setting today's date as ", _datetime_to_str(_today_date))

    if ctx.update is not None:
        _update_database(ctx)


def _database_file_name(date: datetime.datetime) -> str:
    """Entries get stored in files based on the date the entry corresponds to.

    :param date: date of data entry.
    :return: file name for this data entry.
    """
    return (
        _DATABASE_PATH
        + str(date.year)
        + f".{date.month:02d}"
        + _DATABASE_FILE_EXT
    )


def _datetime_to_str(date: datetime.datetime) -> str:
    """Converts a datetime object into a string formatted like `_DATE_FORMAT`.

    :param date: `datetime` object to be converted.
    :return: string representation of the given date.
    """
    return datetime.datetime.strftime(date, _DATE_FORMAT)


def _get_ang(html: str) -> int:
    """Gets the ang of the hukamnama from the HTML.

    :param html: full HTML source code.
    :return: the ang corresponding to the hukamnama.
    """
    try:
        ang = re.findall(r'"angs":{"\d+":(\d+)', html)[0]
    except IndexError:
        raise _ScrapeHtmlError("ang") from None

    return ang


def _get_entry_dates() -> list[datetime.datetime]:
    """Determines the dates already recorded in the database.

    :return: a list of dates included in the database.
    """
    dates = []
    for file in os.listdir(_DATABASE_PATH):
        with open(
            os.path.join(_DATABASE_PATH, file), "r", encoding="utf-8"
        ) as f:
            data = json.loads(f.read())
        for entry in data:
            try:
                dates.append(_str_to_datetime(entry["date"]))
            except KeyError:
                _log.very_verbose("Missing 'date' entry for: ", entry)
    return dates


def _get_first_letter(line: str) -> str:
    """Gets the first letter of a line written in Gurmukhi. Usually just the
    first letter, except if the first letter is a sihaari, in which case it's
    the second letter of the line.

    :param line: the line to get the first letter of.
    :return: the first letter of the line, when read in the Gurmukhi.
    """
    if line[0] == "i":  # sihaari
        return line[1]

    return line[0]


def _get_first_line(shabad: _ShabadLines) -> _ShabadLine:
    """Get the first line of Gurbani in sthe shabad.

    :param shabad: the lines of the shabad.
    :return: the first Gurbani line (not manglachara/sirlekh) in the shabad.
    """
    for line in shabad.values():
        if line[1] is _LineType.GURBANI:
            return line

    raise IndexError  # this should never be hit as every shabad has Gurbani.


def _get_most_recent_entry_date() -> Optional[datetime.datetime]:
    """Get the most recent entry recorded in the database.

    :return: the most recent date recorded in the database.
    """
    entry_dates = _get_entry_dates()
    if entry_dates:
        most_recent = max(entry_dates)
    else:
        most_recent = None
    return most_recent


def _get_next_date(
    start: datetime.datetime, end: datetime.datetime
) -> Generator[datetime.datetime, None, None]:
    """Generates dates between the given start and end dates (inclusive) in order.

    :param start: date to begin range with.
    :param end: date to end range with.
    :yield: next date within the range.
    """
    difference = (end - start).days + 1
    for days in range(0, difference):
        yield start + datetime.timedelta(days=days)


def _get_raag(html: str) -> _Raags:
    """Gets the raag of the hukamnama from the HTML.

    :param html: full HTML source code.
    :return: the raag corresponding to the hukamnama.
    """
    try:
        raag = re.findall(r'"raags":{"\d+":"([a-zA-Z ]+)"}', html)[0]
    except IndexError:
        raise _ScrapeHtmlError("raag") from None

    return raag


def _get_shabad(html: str) -> list[str]:
    """Gets the shabad from the HTML.

    :param html: full HTML source code.
    :return: the hukamnama, in separated lines.
    """
    shabad_start = html.split('shabad_lines":{"gurmukhi":["')[1]
    shabad = shabad_start.split('"],"transliteration')[0]
    shabad_lines = shabad.split('","')
    return shabad_lines


def _get_start_and_end_dates(
    ctx: argparse.Namespace,
) -> tuple[datetime.datetime, datetime.datetime]:
    """Determine when the search should start and finish.

    :param ctx: context about the original instruction.
    :return: tuple of the correct start and end dates of the search.
    """
    start = _str_to_datetime(_FIRST_DATE)
    end = _today_date
    if ctx.update is DataUpdate.WRITE:
        _reset_database()
    elif ctx.update is DataUpdate.UPDATE:
        most_recent = _get_most_recent_entry_date()
        if most_recent:
            start = most_recent + datetime.timedelta(days=1)

    _log.verbose(
        "Start: ",
        _datetime_to_str(start),
        ", end: ",
        _datetime_to_str(end),
    )
    return start, end


@cache
def _get_today_hukam() -> _ShabadMetaData:
    """Get today's hukamnama.

    :return: _ShabadMetaData object corresponding to today's hukamnama
    """
    _today_date_str = _datetime_to_str(_today_date)
    today_hukam = _scrape(_BASE_URL + _today_date_str)

    # TYPE_CHECKING: we can always get today's hukamnama.
    assert today_hukam is not None

    return today_hukam


def _get_writer(html: str) -> _Writers:
    """Gets the writer of the hukamnama from the HTML.

    :param html: full HTML source code.
    :return: the writer of the shabad.
    """
    try:
        writer = re.findall(r'"writers":{"\d+":"([a-zA-Z ]+)"', html)[0]
    except IndexError:
        raise _ScrapeHtmlError("writer") from None

    return writer


def _gurbani_ascii_to_unicode(letter: str) -> str:
    """Maps the ASCII character representing each letter to the unicode value.

    :param letter: ASCII letter in roman alphabet.
    :return: the corresponding letter in unicode.
    """
    mapping = {
        "a": "ੳ",
        "A": "ਅ",
        "e": "ੲ",
        "s": "ਸ",
        "h": "ਹ",
        "k": "ਕ",
        "K": "ਖ",
        "g": "ਗ",
        "G": "ਘ",
        "|": "ਙ",
        "c": "ਚ",
        "C": "ਛ",
        "j": "ਜ",
        "J": "ਝ",
        "\\": "ਞ",
        "t": "ਟ",
        "T": "ਠ",
        "f": "ਡ",
        "F": "ਢ",
        "x": "ਣ",
        "q": "ਤ",
        "Q": "ਥ",
        "d": "ਦ",
        "D": "ਧ",
        "n": "ਨ",
        "p": "ਪ",
        "P": "ਫ",
        "b": "ਬ",
        "B": "ਭ",
        "m": "ਮ",
        "X": "ਯ",
        "r": "ਰ",
        "l": "ਲ",
        "v": "ਵ",
        "V": "ੜ",
    }
    return mapping[letter]


def _load_webpage_data(url: str) -> str:
    """Loads the website and gets the HTML source code.

    :param url: the URL of the page to read.
    :return: the source code of the page.
    """
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as page:
        html = page.read().decode("utf-8")
    return html


def parse(ctx: argparse.Namespace) -> None:
    """Main handler for Hukamnama CLI. This is the API called by the main
    Gurbani Analysis CLI.

    :param ctx: context received from the Gurbani Analysis CLI. Namespace object
        containing the args received by the CLI.
    """
    _log.set_level(ctx.verbosity)
    try:
        if ctx.function == Function.DATA.value:
            _data(ctx)
    except urllib.error.URLError as exc:  # @@@ FAIL_COMMIT find out what causes this
        print(exc)


def _separate_manglacharan(
    shabad_lines: MutableSequence[str],
) -> dict[int, tuple[str, _LineType]]:
    """Separates the manglacharan from the shabad.

    :param shabad_lines: lines of Gurbani to remove a manglacharan from.
    :return: a dict mapping the line number to a tuple containing the line and
        an enum representing the type of line.
    """
    # Characters and phrases exclusive to manglacharans:
    manglacharans = [
        "\\u003C\\u003E",
        " siqgur pRswid ]",
    ]
    sirlekhs = [
        # " 1",
        " 2",
        " 3",
        " 4",
        " 5",
        " 9",
        "slok m",
        "slok ]",
        "sloku m",
        "sloku ]",
        "pauVI",
        "sUhI",
        "iblwvlu",
        "jYqsrI",
        "soriT",
        "DnwsrI",
        "dyvgMDwrI",
        "Awsw ]",
        "goNf",
        " kbIr jI",
        "nwmdyv jI",
        "bwxI Bgqw ",
    ]

    i = 0

    shabad = {}

    for i, line in enumerate(shabad_lines):
        line_type = None
        for manglacharan in manglacharans:
            if manglacharan in line:
                line_type = _LineType.MANGLACHARAN
                break
        if not line_type:
            for sirlekh in sirlekhs:
                if sirlekh in line:
                    line_type = _LineType.SIRLEKH
                    break
        if not line_type:
            line_type = _LineType.GURBANI

        _log.very_verbose("  Line is ", line)
        _log.very_verbose("  Line type is ", line_type)
        shabad[i] = (line, line_type)

    return shabad


def _reset_database() -> None:
    """Resets the database by removing the files."""
    for file in os.listdir(_DATABASE_PATH):
        os.remove(os.path.join(_DATABASE_PATH, file))


def _scrape(url: str) -> Optional[_ShabadMetaData]:
    """Scrapes data from the hukamnama.

    :param url: URL of shabad to read data from.
    :return: a _ShabadMetaData object containing information about the shabad.
    """
    _log.verbose("Scraping data from ", url)

    date = url[-10:]
    html = _load_webpage_data(url)

    try:
        ang = _get_ang(html)
        _log.verbose(" - Ang is ", ang)

        raag = _get_raag(html)
        _log.verbose(" - Raag is ", raag)

        writer = _get_writer(html)
        _log.verbose(" - Writer is ", writer)

        shabad_lines = _get_shabad(html)
        _log.very_verbose(" - Shabad is:\n   - ", "\n   - ".join(shabad_lines))
    except _ScrapeHtmlError as exc:
        _log.suppressed(exc.msg, "\nURL being parsed: ", url)
        return None

    gurmukhi = _separate_manglacharan(shabad_lines)
    first_line = _get_first_line(gurmukhi)
    _log.verbose(" - First line is ", first_line)

    first_letter = _get_first_letter(first_line[0])
    _log.verbose(
        " - First letter is ",
        first_letter,
        f" ({_gurbani_ascii_to_unicode(first_letter)})",
    )

    return _ShabadMetaData(
        id=_ShabadMetaData.get_id(date),
        date=date,
        ang=ang,
        raag=raag,
        writer=writer,
        gurmukhi=gurmukhi,
        first_line=first_line,
        first_letter=first_letter,
    )


def _store_hukamnama(url: str, data: MutableSequence[dict[str, Any]]) -> None:
    """Scrapes and stores the hukamnama for a given date in the database.

    :param url: URL of the page to parse the hukamnama from.
    :param data: JSON data from the database.
    """
    shabad = _scrape(url)
    if shabad and shabad == _get_today_hukam():
        _log.verbose("Shabad is same as today's hukamnama. Skipping.")
        shabad = shabad.remove_data()
    if shabad:
        data.append(shabad.to_dict())
        if not os.path.exists(_DATABASE_PATH):
            os.makedirs(_DATABASE_PATH)
        with open(
            _database_file_name(_str_to_datetime(shabad.date)),
            "w+",
            encoding="utf-8",
        ) as f:
            f.write(json.dumps(data))


def _str_to_datetime(date: str) -> datetime.datetime:
    """Converts a date string formatted as `_DATE_FORMAT`, to a `datetime` object.

    :param date: date to be converted.
    :return: `datetime` object representing the given date.
    """
    return datetime.datetime.strptime(date, _DATE_FORMAT)


def _update_database(ctx: argparse.Namespace) -> None:
    """Determines the dates to get hukamnamas for, and populates the database.

    :param ctx context about the original instruction.
    """
    start, end = _get_start_and_end_dates(ctx)
    most_recent = _get_most_recent_entry_date()

    for date in _get_next_date(start, end):
        date_str = _datetime_to_str(date)
        if date.day == 1:
            if date.month == 1:
                _log.standard("  new year: ", date.year)
            _log.standard("   new month: ", date.month)

        url = _BASE_URL + date_str
        data: list[dict[str, Any]] = []
        if os.path.isfile(_database_file_name(date)):
            with open(_database_file_name(date), "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        skip = False
        if (
            ctx.update is DataUpdate.UPDATE_FILL_GAPS
            and most_recent is not None
            and date < most_recent
        ):
            for entry in data:
                # If entry doesn't have a date, it's fatally badly formatted
                if "date" not in entry:
                    data.remove(entry)
                    _log.verbose(
                        "Removing the following entry due to a "
                        "missing `date` field:\n",
                        entry,
                    )
                    continue
                if entry["date"] == date_str:
                    if [*entry] == _ShabadMetaData.get_keys() and not entry[
                        "needs_verification"
                    ]:
                        # Fields are all up to date
                        skip = True
                    else:
                        # Entry needs updating
                        data.remove(entry)
                    break

        if not skip:
            _store_hukamnama(url, data)
