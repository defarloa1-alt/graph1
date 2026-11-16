"""Reading a coin series' named units from CRRO legends (D-151). Offline."""
import unittest

from GraphRevised.harvest.crro_coins import edtf_year, roman, unit


class CoinLegendTests(unittest.TestCase):
    def test_numerals_including_variant_spellings(self):
        self.assertEqual([roman(n) for n in ("PRI", "IIII", "IV", "IIX", "VIII", "XIIII", "XIV", "XXIII")],
                         [1, 4, 4, 8, 8, 14, 14, 23])
        self.assertIsNone(roman("ANT"))

    def test_units_named_on_reverses(self):
        # A title is an alternative name of the numbered legion, not another unit (curator, 2026-11-15).
        self.assertEqual(unit("LEG·XII·ANTIQVAE")["key"], unit("LEG XII")["key"])
        self.assertEqual(unit("LEG·XII·ANTIQVAE")["title"], "Antiqua")
        self.assertEqual(unit("LEG·XVIII·LYBICAE")["name"], "legion 18")
        self.assertEqual(unit("LEG·XVIII·LYBICAE")["title"], "Libyca")
        self.assertIsNone(unit("LEG XVII")["title"])
        self.assertEqual(unit("LEG IIII")["key"], unit("LEG IV")["key"])
        self.assertEqual(unit("LEG VIII or LEG IIX")["key"], "legion-8")
        self.assertEqual(unit("CHORTIVM·PRAETORIARVM")["key"], "praetorian-cohorts")
        self.assertEqual(unit("CHORTIS·SPECVLATORVM")["kind"], "cohort")
        self.assertIsNone(unit("ANT AVG"))

    def test_bc_years_to_edtf(self):
        self.assertEqual(edtf_year(32), "-0031")
        self.assertEqual(edtf_year(1), "-0000")


if __name__ == "__main__":
    unittest.main()
