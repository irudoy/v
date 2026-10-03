import unittest

from kb import adapters, convert, repo
from kb.adapters import definitions, interp, ledgers, native, overrides, profiles, signals, telemetry
from kb.repo import KbError


class ConvertTest(unittest.TestCase):
    def test_a_converted_registry_converts_to_no_change(self):
        for registry, counts in (("interp", (247, 2)), ("native", (226, 23)),
                                 ("definitions", (718, 50)), ("profiles", (459, 15)),
                                 ("telemetry", (0, 0)), ("signals", (0, 0)),
                                 ("overrides", (0, 0)), ("ledgers", None)):
            with self.subTest(registry=registry):
                conversion, texts, _ = convert.plan(registry, repo.ROOT)
                self.assertEqual(texts, {})
                if counts is not None:
                    self.assertEqual((len(conversion.evidence), len(conversion.statuses)), counts)
                else:
                    self.assertTrue(conversion.evidence)
                    self.assertEqual(conversion.statuses, {})

    def test_only_a_converted_registry_converts(self):
        self.assertEqual(adapters.CONVERTED,
                         (interp, native, definitions, profiles, telemetry, signals,
                          overrides, ledgers))
        with self.assertRaises(KbError) as error:
            convert.plan("architecture", repo.ROOT)
        self.assertEqual(error.exception.code, 2)
        self.assertIn("the conversions are interp, native, definitions, profiles, telemetry, "
                      "signals, overrides, ledgers", str(error.exception))

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

    def test_nested_evidence_is_a_set_but_other_sequences_keep_their_order(self):
        first = {"kind": "l0", "at": "7mfk:00031118"}
        second = {"kind": "rom-bytes", "at": "7mfk:0000991a", "value": "02"}
        self.assertEqual(convert._value(None, {"evidence": [first, second]}),
                         convert._value(None, {"evidence": [second, first]}))
        self.assertNotEqual(convert._value(None, {"step": [first, second]}),
                            convert._value(None, {"step": [second, first]}))

    def test_ledger_dependencies_use_store_order_but_evidence_indices_keep_their_order(self):
        first = {"registry": "vars", "order": 0, "identity": [0, 1], "dependency": [
            {"role": "base", "to": "b/ram", "relies": "structure", "supports": "identity"},
            {"role": "base", "to": "a/ram", "relies": "structure", "supports": "identity"}]}
        second = {**first, "dependency": list(reversed(first["dependency"]))}
        self.assertTrue(convert._ledger_equal(first, second))
        self.assertFalse(convert._ledger_equal(first, {**second, "identity": [1, 0]}))


class NativeNoteConversionTest(unittest.TestCase):
    def test_equivalent_image_notes_keep_the_owner_paragraphs(self):
        cases = (
            (("JK78C",), "JK78C: Bounded grid.", "Bounded grid."),
            (("1ME3B",), "1ME3B: Current snapshot.", "Current snapshot."),
            (("1ND0A", "1ND3B"),
             ["1ND0A: Same nominal grid.", "1ND3B: Same nominal grid."],
             "Same nominal grid."),
            (("1ND0A", "1ND3B"),
             ["1ND0A: First image boundary.", "1ND3B: Second image boundary."],
             ["1ND0A: First image boundary.", "1ND3B: Second image boundary."]),
            (("1ND3B",), "1ND3B: Carrier-only boundary.", "Carrier-only boundary."),
        )
        for carriers, held, incoming in cases:
            with self.subTest(carriers=carriers, held=held):
                expected = convert._notes(held)
                found = convert._native_notes(held, incoming, carriers, "probe/axis")
                self.assertEqual(found, expected)
                for image in carriers:
                    self.assertEqual(native._note(found, carriers, image, "probe/axis"),
                                     native._note(convert._notes(incoming), carriers, image,
                                                  "probe/axis"))

    def test_notes_without_an_owner_keep_the_registry_text(self):
        cases = ("Shared boundary.",
                 ["1ND0A: First boundary.", "1ND3B: Second boundary."])
        for incoming in cases:
            with self.subTest(incoming=incoming):
                self.assertEqual(convert._native_notes(None, incoming,
                                                       ("1ND0A", "1ND3B"), "probe/axis"),
                                 convert._notes(incoming))

    def test_notes_without_registry_text_keep_the_owner(self):
        held = ["1ND0A: First boundary.", "1ND3B: Second boundary."]
        self.assertEqual(convert._native_notes(held, None,
                                               ("1ND0A", "1ND3B"), "probe/axis"), held)

    def test_different_or_incomplete_notes_are_not_discarded(self):
        cases = (
            (("JK78C",), ["JK78C: Original boundary."], ["Different boundary."]),
            (("1ND0A", "1ND3B"), ["1ND0A: Shared boundary."], ["Shared boundary."]),
            (("1ND0A", "1ND3B"),
             ["1ND0A: First boundary.", "1ND3B: Second boundary."],
             ["1ND0A: First boundary.", "1ND3B: Changed boundary."]),
            (("JK78C",), ["JK78C: Exact boundary."], ["Exact boundary. "]),
        )
        for carriers, held, incoming in cases:
            with self.subTest(carriers=carriers, held=held):
                found = convert._native_notes(held, incoming, carriers, "probe/axis")
                self.assertEqual(found, held + [note for note in incoming if note not in held])
                with self.assertRaises(KbError) as error:
                    native._note(found, carriers, carriers[-1], "probe/axis")
                self.assertEqual(error.exception.code, 3)

    def test_ambiguous_owner_notes_still_refuse(self):
        cases = (["JK78C: First boundary.", "Unlabelled boundary."],
                 ["JK78C: First boundary.", "JK78C: Second boundary."])
        for held in cases:
            with self.subTest(held=held):
                with self.assertRaises(KbError) as error:
                    convert._native_notes(held, "First boundary.", ("JK78C",), "probe/axis")
                self.assertEqual(error.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
