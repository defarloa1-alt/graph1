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
