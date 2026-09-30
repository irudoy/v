import unittest

from kb import adapters, convert, repo
from kb.adapters import definitions, interp, native, overrides, profiles, signals, telemetry
from kb.repo import KbError


class ConvertTest(unittest.TestCase):
    def test_a_converted_registry_converts_to_no_change(self):
        for registry, counts in (("interp", (247, 2)), ("native", (226, 23)),
                                 ("definitions", (718, 50)), ("profiles", (459, 15)),
                                 ("telemetry", (0, 0)), ("signals", (0, 0)),
                                 ("overrides", (0, 0))):
            with self.subTest(registry=registry):
                conversion, texts, _ = convert.plan(registry, repo.ROOT)
                self.assertEqual(texts, {})
                self.assertEqual((len(conversion.evidence), len(conversion.statuses)), counts)

    def test_only_a_converted_registry_converts(self):
        self.assertEqual(adapters.CONVERTED,
                         (interp, native, definitions, profiles, telemetry, signals,
                          overrides))
        with self.assertRaises(KbError) as error:
            convert.plan("ledgers", repo.ROOT)
        self.assertEqual(error.exception.code, 2)
        self.assertIn("the conversions are interp, native, definitions, profiles, telemetry, "
                      "signals, overrides", str(error.exception))

    def test_a_registry_target_keeps_the_entries_of_its_file_that_it_lacks(self):
        held = {"layout": "7mfk", "status": "supported", "mailbox_index": 26,
                "allocations": {"phase": {"address": "ffff5d40", "width": 1}}}
        entry = {"layout": "7mfk", "status": "supported",
                 "allocations": {"flags": {"address": "ffff5d42", "width": 2}}}
        self.assertEqual(convert._over(held, entry), {
            "layout": "7mfk", "status": "supported", "mailbox_index": 26,
            "allocations": {"phase": {"address": "ffff5d40", "width": 1},
                            "flags": {"address": "ffff5d42", "width": 2}}})

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
