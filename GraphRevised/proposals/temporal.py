"""Year numbering and EDTF time values for time qualifiers.

Chrystallum years (`Year.year`) are negative for BCE and have no year zero:
31 BCE is -31. EDTF and ISO 8601 number years astronomically, with year 0 as
1 BCE: 31 BCE is -0030. This module is the only place the two are converted.

`parse_edtf` reads the subset of EDTF (ISO 8601-2) that time qualifiers use:

    YYYY, YYYY-MM, YYYY-MM-DD      year, month, or day precision ("-0030-09-02")
    a trailing ~, ?, or %          approximate, uncertain, or both ("-0036~")
    X for unspecified year digits  decade or century ("-003X", "-00XX")
    start/end                      an interval; ".." is an open end ("-0036~/-0035")

Every value resolves to four bounds as Julian Day Numbers, which are
calendar-neutral integers, so Julian and Gregorian values sort and compare
together. The Julian calendar is applied proleptically. Approximate and
uncertain flags are recorded but do not widen the bounds: EDTF does not say
by how much.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Calendar = Literal["julian", "gregorian"]
CALENDARS = ("julian", "gregorian")

# Year links from one time value are refused beyond this many Years.
MAX_LINKED_YEARS = 200


class TimeValueError(ValueError):
    """A time value that cannot be parsed or resolved."""


def to_astronomical(year: int) -> int:
    """Chrystallum year (no zero) to astronomical year: -31 -> -30."""
    if year == 0:
        raise TimeValueError("Chrystallum years have no year zero")
    return year + 1 if year < 0 else year


def from_astronomical(year: int) -> int:
    """Astronomical year to Chrystallum year: -30 -> -31, 0 -> -1."""
    return year - 1 if year <= 0 else year


def julian_day_number(year: int, month: int, day: int, calendar: Calendar) -> int:
    """Julian Day Number of a date in the given calendar (astronomical year)."""
    if calendar not in CALENDARS:
        raise TimeValueError(f"calendar must be one of {CALENDARS}, not {calendar!r}")
    if not 1 <= month <= 12 or not 1 <= day <= days_in_month(year, month, calendar):
        raise TimeValueError(f"no such date: {year:05d}-{month:02d}-{day:02d} ({calendar})")
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4
    if calendar == "gregorian":
        return jdn - y // 100 + y // 400 - 32045
    return jdn - 32083


def days_in_month(year: int, month: int, calendar: Calendar) -> int:
    if month == 2:
        leap = year % 4 == 0 if calendar == "julian" else (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return 29 if leap else 28
    return 30 if month in (4, 6, 9, 11) else 31


@dataclass(frozen=True)
class TimeBounds:
    """A time value resolved to bounds. `None` marks an open interval end."""

    edtf: str
    calendar: Calendar
    precision: str  # of the start (or the single value): day, month, year, decade, century
    approximate: bool
    uncertain: bool
    start_earliest_jdn: int | None
    start_latest_jdn: int | None
    end_earliest_jdn: int | None
    end_latest_jdn: int | None
    earliest_year: int | None  # Chrystallum numbering
    latest_year: int | None

    def years(self) -> list[int]:
        """The backbone Years this value touches, in Chrystallum numbering."""
        if self.earliest_year is None or self.latest_year is None:
            raise TimeValueError(f"{self.edtf} is open-ended; it cannot be linked to Years")
        years = [y for y in range(self.earliest_year, self.latest_year + 1) if y != 0]
        if len(years) > MAX_LINKED_YEARS:
            raise TimeValueError(f"{self.edtf} spans {len(years)} years; the limit is {MAX_LINKED_YEARS}")
        return years


_DATE = re.compile(r"^(?P<year>-?[0-9X]{4,})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?(?P<flag>[~?%])?$")


@dataclass(frozen=True)
class _Point:
    earliest: int
    latest: int
    first_year: int  # astronomical
    last_year: int
    precision: str
    approximate: bool
    uncertain: bool


def _parse_point(text: str, calendar: Calendar) -> _Point:
    match = _DATE.match(text)
    if not match:
        raise TimeValueError(f"not a supported EDTF date: {text!r}")
    year_text, month, day, flag = match["year"], match["month"], match["day"], match["flag"]
    unspecified = year_text.count("X")
    if unspecified and (month or not re.fullmatch(r"-?\d*X+", year_text)):
        raise TimeValueError(f"unspecified digits must end the year and have no month: {text!r}")
    if unspecified:
        low, high = int(year_text.replace("X", "0")), int(year_text.replace("X", "9"))
        first, last = min(low, high), max(low, high)
        precision = {1: "decade", 2: "century"}.get(unspecified, "millennium")
        earliest = julian_day_number(first, 1, 1, calendar)
        latest = julian_day_number(last, 12, 31, calendar)
    else:
        year = int(year_text)
        first = last = year
        if day:
            precision = "day"
            earliest = latest = julian_day_number(year, int(month), int(day), calendar)
        elif month:
            precision = "month"
            m = int(month)
            earliest = julian_day_number(year, m, 1, calendar)
            latest = julian_day_number(year, m, days_in_month(year, m, calendar), calendar)
        else:
            precision = "year"
            earliest = julian_day_number(year, 1, 1, calendar)
            latest = julian_day_number(year, 12, 31, calendar)
    return _Point(earliest, latest, first, last, precision, flag in ("~", "%"), flag in ("?", "%"))


def parse_edtf(value: str, calendar: Calendar) -> TimeBounds:
    """Resolve an EDTF value in a calendar to four Julian Day Number bounds."""
    if calendar not in CALENDARS:
        raise TimeValueError(f"calendar must be one of {CALENDARS}, not {calendar!r}")
    parts = value.split("/")
    if len(parts) == 1:
        point = _parse_point(value, calendar)
        start = end = point
    elif len(parts) == 2:
        start = None if parts[0] == ".." else _parse_point(parts[0], calendar)
        end = None if parts[1] == ".." else _parse_point(parts[1], calendar)
        if start is None and end is None:
            raise TimeValueError("an interval needs at least one end")
        if start is not None and end is not None and start.earliest > end.latest:
            raise TimeValueError(f"interval ends before it starts: {value!r}")
    else:
        raise TimeValueError(f"not a supported EDTF value: {value!r}")
    shown = start or end
    return TimeBounds(
        edtf=value,
        calendar=calendar,
        precision=shown.precision,
        approximate=any(p.approximate for p in (start, end) if p),
        uncertain=any(p.uncertain for p in (start, end) if p),
        start_earliest_jdn=start.earliest if start else None,
        start_latest_jdn=start.latest if start else None,
        end_earliest_jdn=end.earliest if end else None,
        end_latest_jdn=end.latest if end else None,
        earliest_year=from_astronomical(start.first_year) if start else None,
        latest_year=from_astronomical(end.last_year) if end else None,
    )


WIKIDATA_CALENDARS: dict[str, Calendar] = {
    "http://www.wikidata.org/entity/Q1985786": "julian",
    "http://www.wikidata.org/entity/Q1985727": "gregorian",
}


YEAR_BACKBONE = (-2000, 2025)  # the Year nodes that exist (03-TEMPORAL-YEAR-BACKBONE.md)


def year_links(bounds: TimeBounds, mode: str = "during") -> tuple[list[tuple[int, str]], list[str]]:
    """How a time value tethers to the Year backbone: (year, how) links, and notes.

    during   a point or a definite span: every Year it touches, or its start and
             end Years when it touches more than MAX_LINKED_YEARS
    within   an uncertain window (it happened at some point inside): its earliest
             and latest Years only, never every Year between
    An open end links the end that is known. Years outside the backbone are not
    linked and are named in a note, never skipped silently.
    """
    first, last = bounds.earliest_year, bounds.latest_year
    links: list[tuple[int, str]] = []
    if first is None or last is None:
        links = [(first, "start")] if last is None else [(last, "end")]
    elif mode == "within":
        links = [(first, "earliest")] + ([(last, "latest")] if last != first else [])
    else:
        years = [y for y in range(first, last + 1) if y != 0]
        links = [(y, "during") for y in years] if len(years) <= MAX_LINKED_YEARS else [(first, "start"), (last, "end")]
    inside = [(y, how) for y, how in links if YEAR_BACKBONE[0] <= y <= YEAR_BACKBONE[1]]
    outside = sorted({y for y, _ in links} - {y for y, _ in inside})
    notes = [f"outside the Year backbone, not linked: {', '.join(map(str, outside))}"] if outside else []
    return inside, notes


def _edtf_year(year: int) -> str:
    """Astronomical year in EDTF form: -82 -> '-0082'."""
    return f"-{abs(year):04d}" if year < 0 else f"{year:04d}"


def wikidata_time(value: dict) -> tuple[str, Calendar]:
    """A Wikidata time value as (EDTF, calendar), honouring its precision.

    Wikidata numbers BCE years historically (-0083 is 83 BCE), so the year is
    a Chrystallum year and is converted to EDTF's astronomical numbering here.
    Precision: 11 day, 10 month, 9 year; 8 decade and 7 century become an
    interval of the years they cover (the 50s BCE are 59-50 BCE; the 1st
    century BCE is 100-1 BCE). Anything coarser is refused, never guessed.
    """
    match = re.match(r"^([+-])(\d+)-(\d{2})-(\d{2})T", value["time"])
    if not match:
        raise TimeValueError(f"not a Wikidata time: {value['time']!r}")
    calendar = WIKIDATA_CALENDARS.get(value.get("calendarmodel", ""))
    if calendar is None:
        raise TimeValueError(f"unknown Wikidata calendar model {value.get('calendarmodel')!r}")
    year = int(match[2]) * (-1 if match[1] == "-" else 1)
    if year == 0:
        raise TimeValueError("Wikidata year 0 is not a historical year")
    month, day, precision = int(match[3]), int(match[4]), value["precision"]
    if precision >= 9:
        edtf = _edtf_year(to_astronomical(year))
        if precision >= 10:
            edtf += f"-{month:02d}"
        if precision >= 11:
            edtf += f"-{day:02d}"
        return edtf, calendar
    span = {8: 10, 7: 100}.get(precision)
    if span is None:
        raise TimeValueError(f"Wikidata precision {precision} is coarser than a century")
    if year < 0:  # BCE counts down: the 1st century BCE is 100-1 BCE, the 50s BCE are 59-50 BCE
        if span == 100:
            number = -(-abs(year) // 100)
            first, last = -(number * 100), -((number - 1) * 100 + 1)
        else:
            first, last = -(abs(year) // 10 * 10 + 9), -(abs(year) // 10 * 10)
    elif span == 100:
        number = -(-year // 100)
        first, last = (number - 1) * 100 + 1, number * 100
    else:
        first, last = year // 10 * 10, year // 10 * 10 + 9
    first, last = (1 if first == 0 else first), (-1 if last == 0 else last)
    return f"{_edtf_year(to_astronomical(first))}/{_edtf_year(to_astronomical(last))}", calendar


MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def _era(year: int) -> str:
    """A Chrystallum year for display: -31 -> '31 BCE', 14 -> '14 CE'."""
    return f"{-year} BCE" if year < 0 else f"{year} CE"


def _display_point(text: str) -> str:
    match = _DATE.match(text)
    if not match:
        raise TimeValueError(f"not a supported EDTF date: {text!r}")
    year_text, month, day, flag = match["year"], match["month"], match["day"], match["flag"]
    if "X" in year_text:
        low, high = int(year_text.replace("X", "0")), int(year_text.replace("X", "9"))
        first, last = from_astronomical(min(low, high)), from_astronomical(max(low, high))
        shown = f"{-first}–{_era(last)}" if first < 0 and last < 0 else f"{_era(first)}–{_era(last)}"
    else:
        shown = _era(from_astronomical(int(year_text)))
        if month:
            shown = f"{MONTHS[int(month) - 1]} {shown}"
            if day:
                shown = f"{int(day)} {shown}"
    if flag in ("~", "%"):
        shown = f"c. {shown}"
    if flag in ("?", "%"):
        shown += "?"
    return shown


def display_edtf(value: str) -> str:
    """A reader-facing form: '-0030-09-02' -> '2 September 31 BCE',
    '-0036~/-0035' -> 'c. 37 BCE – 36 BCE', '-0030/..' -> 'from 31 BCE'."""
    parts = value.split("/")
    if len(parts) == 1:
        return _display_point(value)
    start, end = parts
    if start == "..":
        return f"until {_display_point(end)}"
    if end == "..":
        return f"from {_display_point(start)}"
    return f"{_display_point(start)} – {_display_point(end)}"
