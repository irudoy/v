import csv
import importlib.util
import unittest

from kb import repo, tokens
from kb.adapters import ledgers

MANUAL = repo.config()["tokens"]["manual"]


def legacy_provenance():
    path = repo.ROOT / "tools/memgraph/provenance.py"
    spec = importlib.util.spec_from_file_location("legacy_provenance", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GrammarTest(unittest.TestCase):
    def test_a_dependency_names_address_offset_and_property(self):
        [token] = tokens.parse("base:ffff128c+0x10@structural")
        self.assertEqual((token.role, token.address, token.offset, token.relies),
                         ("base", 0xFFFF128C, 0x10, "structure"))
        [token] = tokens.parse(" consumer:0003b75c@contract_conf ")
        self.assertEqual((token.address, token.offset, token.relies),
                         (0x3B75C, None, "contract"))

    def test_malformed_tokens_are_refused(self):
        for text in ("writes:ffff1000", "writes:ffff100@structural", "wave",
                     "unknown:1", "from_map:00012000@confidence", "site:00020000@level",
                     "site:00020000;site:00020000", "spec:"):
            with self.subTest(text=text), self.assertRaises(tokens.TokenError):
                tokens.parse(text)

    def test_terminal_tokens_map_to_evidence_kinds(self):
        def mapped(text):
            [token] = tokens.parse(text)
            return tokens.evidence(token, "7mfk", MANUAL)

        self.assertEqual(mapped("site:0004d464"), {"kind": "l0", "at": "7mfk:0004d464"})
        self.assertEqual(mapped("rom_const:00011cb5=0x04080c20"),
                         {"kind": "rom-bytes", "at": "7mfk:00011cb5", "value": "0x04080c20"})
        self.assertEqual(mapped("rom_const:128"), {"kind": "rom-bytes", "value": "128"})
        self.assertEqual(mapped("spec:(168-128)*0.5=20"),
                         {"kind": "arithmetic", "value": "(168-128)*0.5=20"})
        self.assertEqual(mapped("spec:esm-ec179-tp1-depressed-lt-4.75v")["kind"], "manual")
        self.assertEqual(mapped("spec:sh7058-hw-pfdr")["kind"], "manual")
        self.assertEqual(mapped("spec:sh2-decode"), {"kind": "spec", "key": "sh2-decode"})
        self.assertEqual(mapped("spec:hardware-results:main_fuel_cut.vehicle_2026_09_21"),
                         {"kind": "hardware", "key": "main_fuel_cut.vehicle_2026_09_21"})
        self.assertEqual(mapped("registry:defs/JK08A.interp.csv"),
                         {"kind": "registry", "path": "defs/JK08A.interp.csv"})
        self.assertEqual(mapped("registry:Knock Slice Map")["value"], "Knock Slice Map")
        self.assertIsNone(mapped("wave:3"))


class LegacyAgreementTest(unittest.TestCase):
    def test_every_ledger_cell_parses_as_the_legacy_parser_reads_it(self):
        provenance = legacy_provenance()
        props = {v: k for k, v in tokens.RELIES.items()}
        cells = 0
        for name, path in ledgers.PATHS.items():
            with (repo.ROOT / path).open(newline="", encoding="utf-8") as source:
                for row in csv.DictReader(source):
                    for column in tokens.SUPPORTS:
                        text = row.get(column) or ""
                        if not text:
                            continue
                        cells += 1
                        ours = [(t.role, t.value, None if t.address is None
                                 else f"{t.address:08x}", props.get(t.relies))
                                for t in tokens.parse(text)]
                        theirs = [(t.role, t.value, t.target_addr, t.target_prop)
                                  for t in provenance.parse_evidence(text, "confidence")]
                        self.assertEqual(ours, theirs, f"{path}: {text[:80]}")
        self.assertGreater(cells, 2000)

    def test_every_spec_equation_is_arithmetic_and_nothing_else_is(self):
        for name, path in ledgers.PATHS.items():
            with (repo.ROOT / path).open(newline="", encoding="utf-8") as source:
                for row in csv.DictReader(source):
                    for column in tokens.SUPPORTS:
                        for token in tokens.parse(row.get(column) or ""):
                            if token.role != "spec":
                                continue
                            item = tokens.evidence(token, "7mfk", MANUAL)
                            self.assertEqual(item["kind"] == "arithmetic", "=" in token.value,
                                             token.text)


if __name__ == "__main__":
    unittest.main()
