import unittest

from kb import compile, repo, targets
from kb.repo import KbError


def model():
    return compile.cached(repo.ROOT)


class TargetsTest(unittest.TestCase):
    """The reads of the patch build equal the compiled model."""

    def test_the_canonical_key_tables_are_the_symbols_of_the_7mfk_targets(self):
        m = model()
        for feature in ("map_switching", "rolling_launch", "can_telemetry"):
            with self.subTest(feature=feature):
                props = m.targets[(feature, "7mfk")].props
                found = targets.canonical_symbols(feature)
                self.assertEqual({key: found[key] for key in props["symbols"]},
                                 {key: symbol.address for key, symbol in props["symbols"].items()})
                self.assertEqual({key: found[key] for key in targets.NUMBERS if key in found},
                                 {key: props[key] for key in targets.NUMBERS if key in props})
        can = targets.canonical_symbols("can_telemetry")
        symbols = m.targets[("can_telemetry", "7mfk")].props["symbols"]
        for key, record in targets.RECORD_WORDS.items():
            with self.subTest(record=record):
                words = {item["value"] for item in m.symbols[symbols[record]].evidence
                         if item.get("kind") == "rom-bytes"}
                self.assertEqual(words, {f"{can[key]:08x}"})

    def test_the_hook_keys_of_a_target_follow_the_7mfk_words_of_their_meanings(self):
        m = model()
        for layout in ("jk00c", "jk00d", "1nd", "1me3b", "jk78c"):
            with self.subTest(layout=layout):
                hooks = m.targets[("map_switching", layout)].props["hooks"]
                expected = {}
                for key, entry in hooks.items():
                    home = m.meaning_of(entry["hook"]).symbols.get("7mfk")
                    if home is not None:
                        expected[home.address] = key
                self.assertEqual(targets.hook_keys("map_switching", layout), expected)
        # The dual-CVTC layouts redirect the canonical exhaust-target lookup as
        # their intake-target lookup.
        self.assertEqual(targets.hook_keys("map_switching", "jk00c")[
            targets.address("exhaust_cvtc_target_lookup/hook", "7mfk")],
            "intake_cvtc_target_lookup")

    def test_an_image_has_the_layout_of_its_family(self):
        self.assertEqual(targets.layout_of("1ND3B"), "1nd")
        self.assertEqual(targets.layout_of("JK08A"), "7mfk")
        with self.assertRaises(KbError) as unknown:
            targets.layout_of("XX00A")
        self.assertEqual(unknown.exception.code, 5)

    def test_a_missing_target_or_file_is_an_error(self):
        with self.assertRaises(KbError) as missing:
            targets.target("map_switching", "xx")
        self.assertEqual(missing.exception.code, 3)
        with self.assertRaises(KbError) as absent:
            targets.symbol("no_such_meaning/ram", "7mfk")
        self.assertIn("no entity file", str(absent.exception))


if __name__ == "__main__":
    unittest.main()
