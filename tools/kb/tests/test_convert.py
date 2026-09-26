import unittest

from kb import adapters, convert, repo
from kb.adapters import interp
from kb.repo import KbError


class ConvertTest(unittest.TestCase):
    def test_a_converted_registry_converts_to_no_change(self):
        conversion, texts, _ = convert.plan("interp", repo.ROOT)
        self.assertEqual(texts, {})
        self.assertEqual((len(conversion.evidence), len(conversion.statuses)), (247, 2))

    def test_only_a_converted_registry_converts(self):
        self.assertEqual(adapters.CONVERTED, (interp,))
        with self.assertRaises(KbError) as error:
            convert.plan("ledgers", repo.ROOT)
        self.assertEqual(error.exception.code, 2)
        self.assertIn("the conversions are interp", str(error.exception))

    def test_differences_name_each_fact_that_differs(self):
        expected = {"symbols": {("7mfk:00026388", "fn"): ("a",), ("7mfk:0002638c", "fn"): ("b",)},
                    "links": {}}
        found = {"symbols": {("7mfk:00026388", "fn"): ("a",), ("7mfk:00026390", "fn"): ("c",)},
                 "links": {}}
        self.assertEqual(convert.differences(expected, found), [
            "symbols ('7mfk:0002638c', 'fn'): expected ('b',), found None",
            "symbols ('7mfk:00026390', 'fn'): expected None, found ('c',)"])
        self.assertEqual(convert.differences(expected, expected), [])


if __name__ == "__main__":
    unittest.main()
