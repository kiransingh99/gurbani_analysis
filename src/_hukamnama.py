# ------------------------------------------------------------------------------
# main.py - Hukamnama parsing
#
# October 2022, Gurkiran Singh
#
# Copyright (c) 2022
# All rights reserved.
# ------------------------------------------------------------------------------

"""Parses requests for hukamnama parsing."""

__all__ = [
    "DataUpdate",
    "Function",
    "parse",
]

from urllib.request import Request, urlopen

import dataclasses
import datetime
import enum
import json
import re

import _cmn

_BASE_URL = "https://www.sikhnet.com/hukam/archive/"
_DATABASE = "./artifacts/hukamnama.json"

_DATE_FORMAT = "%Y-%m-%d"
_FIRST_DATE = _cmn.str_to_datetime("2002-01-01", _DATE_FORMAT)
_today_date = datetime.datetime.today()

class DataUpdate(enum.IntEnum):
    """
    Methods of updating data in the database.

    WRITE: Starting from the beginning of the archives, (re)populate all entries
        until today (overwrites existing data)
    UPDATE: Add information to database, continuing from the most recently
        populated entry, until today
    UPDATE_FILL_GAPS: Starting from the beginning of the archives, populate
        entries without any data (does not overwrites existing data)
    """

    UNKNOWN = 0
    WRITE = 1
    UPDATE = 2
    UPDATE_FILL_GAPS = 3


class Function(enum.Enum):
    """
    Subfunctions within Hukamnama Analysis.

    DATA: Update/repopulate the database
    """

    DATA = "data"


@dataclasses.dataclass()
class _ShabadMetaData:
    """
    Object to store information about each shabad recorded.

    id: a unique identifier for the date
    date: date the hukamnama was taken
    ang: ang of the hukamnama
    gurmukhi: lines of the shabad
    raag: raag the hukamnama was written in
    writer: the author of the shabad
    first_letter: the first consonant of the first line of the hukamnama
    """

    id: int
    date: str
    ang: int
    gurmukhi: list
    raag: str
    writer: str
    first_letter: str

    def __eq__(self, other):
        """
        A necessary and sufficient condition to determine that two
        _ShabadMetaData objects represent the same shabad is if all the lines of
        the two shabads are the same.
        """
        return self.gurmukhi == other.gurmukhi

    @classmethod
    def get_id(cls, date):
        """
        Generates a unique, sequential, integer ID for the date of the
        hukamnama.
        """
        difference = (_cmn.str_to_datetime(date, _DATE_FORMAT) -
            _FIRST_DATE)
        return difference.days + 1

    @classmethod
    def get_keys(cls):
        """Get a list of the attributes of this object."""
        return [item.name for item in dataclasses.fields(cls)]

    def remove_data(self):
        """Remove data about the shabad from the shabad object."""
        self.ang = None
        self.gurmukhi = None
        self.raag = None
        self.writer = None
        self.first_letter = None

    def to_dict(self):
        """Produces a dictionary that represents a shabad's metadata."""
        data = {}
        for key in self.get_keys():
            if getattr(self, key) is not None:
                data[key] = getattr(self, key)
        return data
        return {
                "id": self.id,
                "date": self.date,
                "ang": self.ang,
                "gurmukhi": self.gurmukhi,
                "raag": self.raag,
                "writer": str(self.writer),
                "first_letter": self.first_letter,
            }

class _WriterError(_cmn.Error):
    def __init__(self, writer):
        msg = f"The writer '{writer}' was not recognised."
        steps = [
            "Add a mapping for this writer to a value in the `_Writers` enum."
        ]
        super().__init__(msg, steps)


class _Writers(enum.IntEnum):
    """Writers of shabads"""
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
    # Bhatts: 26-37

    # Gursikhs: 38-40


    def __str__(self):
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
        }
        return names[self]

    @classmethod
    def from_string(cls, name):
        if any(s in name.lower() for s in ["nanak"]):
            return cls.NANAK
        elif any(s in name.lower() for s in ["angad"]):
            return cls.ANGAD
        elif any(s in name.lower() for s in ["amar"]):
            return cls.AMAR_DAS
        elif any(s in name.lower() for s in ["raam"]):
            return cls.RAM_DAS
        elif any(s in name.lower() for s in ["arjan"]):
            return cls.ARJAN
        elif any(s in name.lower() for s in ["tegh"]):
            return cls.TEGH_BAHADUR
        elif any(s in name.lower() for s in ["kabir"]):
            return cls.KABIR
        elif any(s in name.lower() for s in ["ravi"]):
            return cls.RAVIDAS
        elif any(s in name.lower() for s in ["naam"]):
            return cls.NAAMDEV
        else:
            raise _WriterError(name)

def _data(ctx):
    """
    Handler for all data requests to the Hukamnama CLI.

    :param ctx:
        Context about the original instruction.
    """
    if ctx.verbosity.is_very_verbose():
        breakpoint() # FAIL_COMMIT check this works properly
        print(
            "Ignoring today's shabad:\n  - ",
            "\n ".join(_get_today_hukam(ctx).gurmukhi),
        )
    if ctx.update is DataUpdate.WRITE:
        start = _FIRST_DATE
        # Reset existing database.
        with open(_DATABASE, "w") as f:
            f.write("[]")
    elif ctx.update is DataUpdate.UPDATE:
            start = _get_most_recent_entry_date(ctx) + datetime.timedelta(days=1)
    elif ctx.update is DataUpdate.UPDATE_FILL_GAPS:
        start = _FIRST_DATE
        fill_gaps = True
        most_recent_entry_date = _get_most_recent_entry_date(ctx)
    else:
        raise NotImplementedError  # FAIL_COMMIT see what errors get raised
    end = _today_date

    if ctx.verbosity.is_verbose():
        print(
            "Operating between dates: "
           f"{_cmn.datetime_to_str(start, _DATE_FORMAT)} - "
           f"{_cmn.datetime_to_str(end, _DATE_FORMAT)}"
        )

    prev_year = start.year
    prev_month = start.month

    for date in _get_next_date(start, end):
        date_str = _cmn.datetime_to_str(date, _DATE_FORMAT)
        current_year = date.year
        current_month = date.month
        if current_month != prev_month:
            if current_year != prev_year:
                prev_year = current_year
                if not ctx.verbosity.is_suppressed():
                    print("  new year: ", current_year)
            prev_month = current_month
            if not ctx.verbosity.is_suppressed():
                print("  new month: ", current_month)
        url = _BASE_URL + date_str
        try:
            with open(_DATABASE, "r") as f:
                data = json.loads(f.read())
            read = True
            if fill_gaps:
                if date < most_recent_entry_date:
                    for entry in data:
                        # If entry doesn't have a date, it's fatally badly
                        # formatted
                        if "date" not in entry:
                            data.remove(entry)
                            if ctx.verbosity.is_verbose():
                                print(
                                    "Removing the following entry due to a "
                                    "missing `date` field:\n",
                                    entry
                                )
                            continue
                        if entry["date"] == date_str:
                            if [key for key in entry] == _ShabadMetaData.get_keys():
                                # Fields are all up to date:
                                read = False
                            else:
                                # If entry needs updating:
                                data.remove(entry)
                                break

            if read:
                shabad = _scrape(ctx, url)
                if shabad == _get_today_hukam(ctx):
                    shabad.remove_data()
                data.append(shabad.to_dict())
                with open(_DATABASE, "w") as f:
                    f.write(json.dumps(data))
        except:
            raise  # FAIL_COMMIT see what errors get hit
            # FAIL_COMMIT file not found
            # FAIL_COMMIT file in use

def _get_ang(html):
    """
    Gets the ang of the hukamnama from the HTML.

    :param html:
        Full HTML source code.

    :return:
        The ang corresponding to the hukamnama.
    """
    ang_start = html.split('"angs":{"')[1]
    ang = int(ang_start.split('"')[0])
    return ang

def _get_first_letter(line):
    """
    Gets the first letter of a line written in Gurmukhi. Usually just the first
    letter, except if the first letter is a sihaari, in which case it's the
    second letter of the line.

    :param line:
        The line to get the first letter of.

    :return:
        The first letter of the line, when read in the Gurmukhi
    """
    if line[0] == "i":  # sihaari
        return line[1]
    else:
        return line[0]


def _get_entry_dates(ctx):
    """FAIL_COMMIT TODO"""
    with open(_DATABASE, "r") as f:
        data = json.loads(f.read())
    dates = []
    for entry in data:
        try:
            dates.append(_cmn.str_to_datetime(entry["date"], _DATE_FORMAT))
        except KeyError:
            if ctx.verbosity.is_very_verbose():
                print("Missing 'date' entry for: ", entry)
    return dates


def _get_most_recent_entry_date(ctx, entry_dates=None):
    """FAIL_COMMIT TODO"""
    if entry_dates is None:
        entry_dates = _get_entry_dates(ctx)
    return max(entry_dates)


def _get_next_date(start, end):
    """
    Generates dates between the given start and end dates (inclusive) in order.
    Dates must be in YYYY-MM-DD format.

    :param start:
        Date to begin range with.

    :param end:
        Date to end range with.
    """
    difference = (end - start).days + 1
    for x in range(0, difference):
        yield start + datetime.timedelta(days=x)

def _get_raag(html):
    """
    Gets the raag of the hukamnama from the HTML.

    :param html:
        Full HTML source code.

    :return:
        The raag corresponding to the hukamnama.
    """
    raag_start = re.split('"raags":{"\d+":"Raag ', html)[1]
    raag = raag_start.split('"}')[0]
    return raag

def _get_shabad(html):
    """
    Gets the shabad from the HTML.

    :param html:
        Full HTML source code.

    :return:
        The hukamnama, in separated lines.
    """
    shabad_start = html.split('shabad_lines":{"gurmukhi":["')[1]
    shabad = shabad_start.split('"],"transliteration')[0]
    shabad_lines = shabad.split('","')
    return shabad_lines

def _get_today_hukam(ctx):
    """
    Get today's hukamnama.

    :param ctx:
        Context about the original instruction.

    :return:
        _ShabadMetaData object corresponding to today's hukamnama
    """
    _today_date_str = _cmn.datetime_to_str(_today_date, _DATE_FORMAT)
    return _scrape(ctx, _BASE_URL + _today_date_str)

def _get_writer(html):
    """
    Gets the writer of the hukamnama from the HTML.

    :param html:
        Full HTML source code.

    :return:
        The writer of the shabad.
    """
    writer_start = re.split('"writers":{"\d+":"', html)[1]
    writer_str = writer_start.split('"}')[0]

    return _Writers.from_string(writer_str)

def _gurbani_ascii_to_unicode(letter):
    """
    Maps the ASCII character representing each letter to the unicode value. Only
    to be used for display purposes, as words, especially in Gurbani, do not
    appear well when using unicode.

    :param letter:
        ASCII letter in roman alphabet.

    :return:
        The corresponding letter in unicode.
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
        "|": "ਞ",
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


def _load_webpage_data(url):
    """
    Loads the website and gets the HTML source code.

    :param url:
        The URL of the page to read.

    :return:
        The source code of the page.
    """
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urlopen(req)
    html = page.read().decode("utf-8")
    return html


def parse(ctx):
    """
    Main handler for Hukamnama CLI. This is the API called by the main Gurbani
    Analysis CLI.

    :param ctx:
        Context received from the Gurbani Analysis CLI. Namespace object
        containing the args received by the CLI.
    """
    if ctx.verbosity.is_very_verbose():
        print("Setting today's date as", _today_date)

    if ctx.function == Function.DATA.value:
        _data(ctx)
    else:
        raise NotImplementedError  # FAIL_COMMIT unrecognised argument

def _remove_manglacharan(ctx, shabad_lines):
    """
    Removes the manglacharan from the beginning of the shabad.

    :param ctx:
        Context about the original instruction.

    :param shabad_lines:
        Lines of Gurbani to remove a manglacharan from.

    :return:
        Shabad as input, but without the manglacharan.
    """
    # characters and phrases exclusive to manglacharans:
    mangals = [
        "\\u003C\\u003E",
        " siqgur pRswid ]",
        " 1",
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
    while i < len(mangals):
        mangal = mangals[i]
        if mangal in shabad_lines[0]:
            if ctx.verbosity.is_very_verbose():
                print("  Removing manglacharan", shabad_lines[0])
            shabad_lines.pop(0)
            i = 0
        else:
            i+=1

    return shabad_lines


def _scrape(ctx, url):
    """
    Scrapes data from the hukamnama.

    :param ctx:
        Context about the original instruction.

    :param url:
        URL of shabad to read data from.

    :return:
        A _ShabadMetaData object containing information about the shabad.
    """
    if ctx.verbosity.is_verbose():
        print("Scraping data from", url)

    date = url[-10:]
    html = _load_webpage_data(url)

    ang = _get_ang(html)
    if ctx.verbosity.is_verbose():
        print(" - Ang is", ang)

    shabad_lines = _get_shabad(html)
    if ctx.verbosity.is_very_verbose():
        print(" - Shabad is:\n  - ", "\n    ".join(shabad_lines))

    first_line = _remove_manglacharan(ctx, shabad_lines)[0]
    if ctx.verbosity.is_verbose():
        print(" - First line is", first_line)

    first_letter = _get_first_letter(first_line)
    if ctx.verbosity.is_verbose():
        print(
            " - First letter is",
            first_letter,
            f"({_gurbani_ascii_to_unicode(first_letter)})",
        )

    raag = _get_raag(html)
    if ctx.verbosity.is_verbose():
        print(" - Raag is", raag)

    writer = _get_writer(html)
    if ctx.verbosity.is_verbose():
        print(" - Writer is", writer)

    return _ShabadMetaData(
        id=_ShabadMetaData.get_id(date),
        date=date,
        ang=ang,
        gurmukhi=shabad_lines,
        raag=raag,
        writer=writer,
        first_letter=first_letter,
    )
