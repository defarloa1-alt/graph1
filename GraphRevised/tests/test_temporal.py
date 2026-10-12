"""Year numbering, Julian Day Numbers, and EDTF parsing for time qualifiers."""

import unittest

from GraphRevised.proposals.temporal import (
    MAX_LINKED_YEARS,
    TimeValueError,
    from_astronomical,
    julian_day_number,
    parse_edtf,
    to_astronomical,
)


class YearNumberingTests(unittest.TestCase):
    def test_bce_years_shift_by_one(self):
        self.assertEqual(to_astronomical(-31), -30)
        self.assertEqual(to_astronomical(-1), 0)
        self.assertEqual(to_astronomical(1), 1)
        self.assertEqual(from_astronomical(-30), -31)
        self.assertEqual(from_astronomical(0), -1)
        self.assertEqual(from_astronomical(2025), 2025)

    def test_round_trip_and_no_year_zero(self):
        for year in (-2000, -509, -31, -1, 1, 14, 2025):
            self.assertEqual(from_astronomical(to_astronomical(year)), year)
        with self.assertRaises(TimeValueError):
            to_astronomical(0)


class JulianDayNumberTests(unittest.TestCase):
    def test_reference_dates(self):
        self.assertEqual(julian_day_number(2000, 1, 1, "gregorian"), 2451545)
        self.assertEqual(julian_day_number(-4712, 1, 1, "julian"), 0)
        # The Gregorian reform: 4 October 1582 (Julian) was followed by 15 October (Gregorian).
        self.assertEqual(julian_day_number(1582, 10, 4, "julian"), 2299160)
        self.assertEqual(julian_day_number(1582, 10, 15, "gregorian"), 2299161)
        # The Ides of March, 44 BCE (astronomical -43), Julian.
        self.assertEqual(julian_day_number(-43, 3, 15, "julian"), 1705426)

    def test_leap_years_follow_the_calendar(self):
        self.assertEqual(julian_day_number(1900, 3, 1, "julian") - julian_day_number(1900, 2, 28, "julian"), 2)
        self.assertEqual(julian_day_number(1900, 3, 1, "gregorian") - julian_day_number(1900, 2, 28, "gregorian"), 1)
        # Astronomical year 0 (1 BCE) is a Julian leap year.
        julian_day_number(0, 2, 29, "julian")

    def test_invalid_dates_are_refused(self):
        for args in ((-30, 2, 30, "julian"), (-30, 13, 1, "julian"), (-30, 9, 2, "roman")):
            with self.subTest(args=args), self.assertRaises(TimeValueError):
                julian_day_number(*args)


class EdtfTests(unittest.TestCase):
    def test_day_precision(self):
        actium = parse_edtf("-0030-09-02", "julian")
        self.assertEqual(actium.precision, "day")
        self.assertEqual(actium.start_earliest_jdn, actium.end_latest_jdn)
        self.assertEqual((actium.earliest_year, actium.latest_year), (-31, -31))
        self.assertEqual(actium.years(), [-31])

    def test_year_precision_covers_the_year(self):
        year = parse_edtf("-0030", "julian")
        self.assertEqual(year.precision, "year")
        self.assertEqual(year.end_latest_jdn - year.start_earliest_jdn, 364)
        self.assertEqual(year.years(), [-31])

    def test_month_precision(self):
        september = parse_edtf("-0030-09", "julian")
        self.assertEqual(september.end_latest_jdn - september.start_earliest_jdn, 29)

    def test_uncertain_span_between_two_years(self):
        married = parse_edtf("-0036~/-0035", "julian")
        self.assertTrue(married.approximate)
        self.assertFalse(married.uncertain)
        self.assertEqual((married.earliest_year, married.latest_year), (-37, -36))
        self.assertEqual(married.years(), [-37, -36])

    def test_span_across_the_era_skips_year_zero(self):
        span = parse_edtf("-0001/0001", "julian")
        self.assertEqual(span.years(), [-2, -1, 1])

    def test_unspecified_digits(self):
        decade = parse_edtf("-003X", "julian")
        self.assertEqual(decade.precision, "decade")
        self.assertEqual((decade.earliest_year, decade.latest_year), (-40, -31))
        self.assertEqual(parse_edtf("-00XX", "julian").precision, "century")

    def test_open_interval_has_no_years(self):
        bounds = parse_edtf("-0030/..", "julian")
        self.assertIsNone(bounds.end_latest_jdn)
        with self.assertRaises(TimeValueError):
            bounds.years()

    def test_long_spans_are_not_linked(self):
        with self.assertRaises(TimeValueError):
            parse_edtf(f"-0500/{-500 + MAX_LINKED_YEARS + 10:05d}", "julian").years()

    def test_flags(self):
        self.assertTrue(parse_edtf("-0030?", "julian").uncertain)
        both = parse_edtf("-0030%", "julian")
        self.assertTrue(both.approximate and both.uncertain)

    def test_julian_and_gregorian_values_compare(self):
        self.assertEqual(
            parse_edtf("1582-10-04", "julian").start_earliest_jdn + 1,
            parse_edtf("1582-10-15", "gregorian").start_earliest_jdn,
        )

    def test_unsupported_or_invalid_values_are_refused(self):
        for value in ("31 BCE", "-0030-02-30", "-0030-21", "../..", "-0030/-0031", "-00X0", "-003X-09", "a/b/c"):
            with self.subTest(value=value), self.assertRaises(TimeValueError):
                parse_edtf(value, "julian")
        with self.assertRaises(TimeValueError):
            parse_edtf("-0030", "roman-prejulian")


if __name__ == "__main__":
    unittest.main()
