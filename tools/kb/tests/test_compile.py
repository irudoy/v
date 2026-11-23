from collections import Counter, defaultdict
import copy
import csv
import re
import subprocess
import textwrap
import tomllib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pytest

from kb import adapters, checks, compile, derive, levels, match, names, repo, tokens, vocab
from kb.adapters import (architecture, curated, definitions, interp, ledgers, native, overrides,
                         profiles, signals, telemetry)
from kb.model import Builder, Ref, SymbolKey
from kb.repo import KbError
from tools.mapkit import dtc_projection


def model():
    return compile.cached(repo.ROOT)


class LedgerAdapterTest(unittest.TestCase):
    def test_every_ledger_row_is_a_declared_symbol_of_its_kind(self):
        m = model()
        kinds = {"funcs": ("fn",), "vars": ("ram", "reg"), "findings": ("tbl",),
                 "axes": ("axis",), "dtc": ("dtc",)}
        column = {"dtc": "record_addr"}
        for ledger, allowed in kinds.items():
            with (repo.ROOT / ledgers.PATHS[ledger]).open(newline="", encoding="utf-8") as src:
                for row in csv.DictReader(src):
                    address = int(row[column.get(ledger, "addr")], 16)
                    found = [SymbolKey("7mfk", kind, address) for kind in allowed
                             if SymbolKey("7mfk", kind, address) in m.symbols]
                    self.assertEqual(len(found), 1, f"{ledger} {address:08x}")
                    self.assertFalse(m.symbols[found[0]].implicit)

    def test_an_axis_that_the_census_passes_has_identity_evidence_at_its_first_call(self):
        m = model()
        calls = native.census("7mfk")
        with (repo.ROOT / ledgers.PATHS["axes"]).open(newline="", encoding="utf-8") as src:
            rows = list(csv.DictReader(src))
        self.assertEqual(len(rows), 79)
        for row in rows:
            address = int(row["addr"], 16)
            symbol = m.symbols[SymbolKey("7mfk", "axis", address)]
            first = next(site for site, _, passed in calls if address in passed)
            item = {"kind": "l0", "supports": "identity", "at": f"7mfk:{first:08x}"}
            with self.subTest(axis=row["addr"]):
                self.assertIn(item, symbol.evidence)
                self.assertIsNone(match.verify(m, symbol, item))
                self.assertEqual(symbol.meaning.props["level"], "code")

    def test_links_follow_the_token_table(self):
        m = model()
        table = m.meaning_of(SymbolKey("7mfk", "tbl", 0xA4AA))
        out = {(link.type, link.to.symbols["7mfk"].address) for link in table.links}
        self.assertIn(("index", 0xFFFF11BC), out)
        self.assertIn(("index", 0xFFFF102C), out)
        self.assertIn(("selector", 0xFFFF2458), out)
        writer = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF106A))
        self.assertIn(("writer", 0x20DFE),
                      {(link.type, link.to.symbols["7mfk"].address) for link in writer.links})

    def test_curated_names_name_their_meanings(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x2040C))
        self.assertEqual((meaning.key, meaning.tier), ("periodic_tick_isr/fn", "file"))

    def test_the_file_of_a_meaning_wins_over_a_curated_name(self):
        # The conversion of the address profiles named the file by the symbol
        # key, which wins over the curated name.
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x20DFE))
        self.assertEqual((meaning.key, meaning.tier), ("coherent_snapshot/fn", "file"))
        self.assertIn(("periodic_snapshot_dispatch", "former", "kb/fn/coherent_snapshot.toml"),
                      meaning.other_names)
        self.assertEqual(model().meaning_of(SymbolKey("1nd", "fn", 0x11363C)).name, "hcan1_init")


class ExplicitLedgerTokenTest(unittest.TestCase):
    TEXT = ("site:0004ec9e; rom_const:00009000=2; spec:sh2-decode; registry:probe; "
            "wave:3; arg:review; indirect_base:0004ec9e+2; "
            "test:tools/kb/tests/test_tokens.py#test_a_dependency_names_address_offset_and_property")
    ROWS = {
        "funcs": {"addr": "0004ec9e", "role": "accessor", "semantics": "Probe.",
                  "contract": "Probe.", "contract_conf": "code", "confidence": "code", "note": ""},
        "vars": {"addr": "ffff23ca", "semantics": "Probe.", "confidence": "code",
                 "units": "raw", "note": ""},
        "findings": {"addr": "00009000", "family": "explicit", "width": "1", "height": "1",
                     "storagetype": "uint8", "role": "table", "confidence": "code",
                     "semantics": "Probe.", "units": "raw", "scale_expr": "x", "to_byte": "x",
                     "scale_conf": "code", "note": "", "accessor": ""},
        "axes": {"addr": "00009000", "kind": "rpm", "units": "rpm", "scale_expr": "x",
                 "to_byte": "x", "scale_conf": "code", "note": ""},
        "diagnostic-bindings": {
            "id": "probe", "firmware_addr": "ffff23ca", "firmware_label": "Reg",
            "kind": "live-data", "diagnostic_label": "Probe", "diagnostic_key": "probe",
            "source_claim_label": "Reg", "source_claim_id": "ffff23ca", "applicability": "",
            "rom_scope": "JK08A", "priority": "1", "confidence": "code", "note": ""},
    }

    def declare(self, ledger, column, text):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
        row = {**self.ROWS[ledger], column: text}
        with patch.object(ledgers, "rows", side_effect=lambda _, name, overlay=None: [row] if name == ledger else ()), \
                patch.object(curated, "declare_layout"), \
                patch.object(native, "census_call", return_value=None):
            ledgers.declare(b, repo.ROOT)
        m = b.finish()
        m.root, m.config = repo.ROOT, repo.config()
        return m

    def test_only_explicit_new_tokens_are_typed_in_each_ledger_column(self):
        columns = {"funcs": ("evidence", "contract_evidence"), "vars": ("evidence",),
                   "findings": ("evidence", "scale_evidence"), "axes": ("scale_evidence",),
                   "diagnostic-bindings": ("evidence",)}
        parsed = tokens.parse(self.TEXT)
        for ledger, names_ in columns.items():
            for column in names_:
                with self.subTest(ledger=ledger, column=column):
                    m = self.declare(ledger, column, self.TEXT)
                    self.assertEqual(m.issues, [])
                    [symbol] = m.symbols.values()
                    if ledger == "diagnostic-bindings":
                        [binding] = symbol.meaning.tables["diagnostic"]
                        items = binding["evidence"]
                        expected = [tokens.evidence(token, "7mfk", ()) for token in parsed]
                    else:
                        items = symbol.evidence
                        expected = [{"supports": tokens.SUPPORTS[column], **item} if item else None
                                    for token in parsed
                                    for item in [tokens.evidence(token, "7mfk", ())]]
                    expected = [{**item, **({} if token.role in tokens.TYPED_TERMINAL
                                           else {"legacy": token.text})}
                                for token, item in zip(parsed, expected) if item is not None]
                    self.assertEqual(items, expected)
                    self.assertEqual(sum("legacy" not in item for item in items), 2)
                    self.assertFalse(checks._owned(m, symbol))

    def test_malformed_explicit_tokens_report_schema_without_typed_items(self):
        for text in ("indirect_base:0004ec9e+-2", "test:../test_probe.py#test_probe"):
            with self.subTest(text=text):
                m = self.declare("vars", "evidence", text)
                [issue] = m.issues
                self.assertEqual((issue.check, issue.path), ("schema", "defs/registries/JK08A.vars.csv"))
                [symbol] = m.symbols.values()
                self.assertEqual(symbol.evidence, [])

    def test_the_dependency_base_token_keeps_its_link_and_no_terminal_item(self):
        m = self.declare("vars", "evidence", "base:ffff128c+0x10@structural")
        [symbol] = m.symbols.values()
        self.assertEqual(symbol.evidence, [])
        # The dependency is deferred, not an indirect identity item.
        [pending] = m.stash[ledgers.__name__]
        self.assertEqual((pending[1].role, pending[1].offset, pending[1].relies),
                         ("base", 0x10, "structure"))


@pytest.mark.slow
class RamStructureEvidenceTest(unittest.TestCase):
    PATH = "tools/kb/tests/test_ram_structure.py"
    # Fixed expectations bind the ledger items, not values inferred from ROM.
    EXPECTED = {
        0xFFFF5A93: ("7mfk:00097ec2", 0x37B, "test_maf_extension_record_path"),
        0xFFFF1A40: ("7mfk:0003c46e", 2, "test_indexed_word_copy_path"),
        0xFFFF1098: ("7mfk:00020f48", 4, "test_snapshot_destination_path"),
        0xFFFF111E: ("7mfk:00020f50", 10, "test_snapshot_source_and_decoder_path"),
        0xFFFF1DF2: ("7mfk:0003a9ae", 6, "test_maf_indexed_state_path"),
        0xFFFF18C2: ("7mfk:0004ea52", 0x636, "test_injection_precursor_path"),
        0xFFFF1B1D: ("7mfk:000c1dfa", 0x891, "test_indexed_mode_byte_paths"),
        0xFFFF1AA8: ("7mfk:000c1dfa", 0x81C, "test_indexed_state_longword_path"),
    }
    STRUCTURE_COUNTS = {0xFFFF5A93: 8, 0xFFFF1A40: 1, 0xFFFF1098: 3,
                        0xFFFF111E: 1, 0xFFFF1DF2: 3, 0xFFFF18C2: 2,
                        0xFFFF1B1D: 1, 0xFFFF1AA8: 1}

    @classmethod
    def setUpClass(cls):
        cls.rows = {int(row["addr"], 16): row for row in ledgers.rows(repo.ROOT, "vars")
                    if int(row["addr"], 16) in cls.EXPECTED}

    def expected_items(self, address):
        at, value, key = self.EXPECTED[address]
        return [{"kind": "indirect", "supports": "identity", "at": at,
                 "mode": "base", "value": value},
                {"kind": "test", "supports": "identity", "path": self.PATH, "key": key}]

    def assert_pair(self, address, items):
        # Independent execution contracts may accompany the required base pair.
        self.assertEqual([item for item in items
                          if item["kind"] == "indirect"
                          or (item["kind"] == "test" and item.get("path") == self.PATH)],
                         self.expected_items(address))

    def test_independent_contract_keeps_the_original_pair_required(self):
        address = 0xFFFF18C2
        pair = self.expected_items(address)
        independent = {"kind": "test", "supports": "identity",
                       "path": "tools/kb/tests/test_bank_base_pulse_chain.py",
                       "key": "test_bank_base_pulse_chain_owner_contract"}
        self.assert_pair(address, [*pair, independent])
        for omitted in range(2):
            with self.subTest(omitted=omitted):
                with self.assertRaises(AssertionError):
                    self.assert_pair(address, [pair[1 - omitted], independent])
        for index, field, value in ((0, "value", pair[0]["value"] + 1),
                                    (0, "supports", "structure"),
                                    (1, "key", "test_other_contract"),
                                    (1, "supports", "structure"),
                                    (1, "path", independent["path"])):
            with self.subTest(index=index, field=field):
                changed = copy.deepcopy(pair)
                changed[index][field] = value
                with self.assertRaises(AssertionError):
                    self.assert_pair(address, [*changed, independent])

    def declare(self, row):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
        with patch.object(ledgers, "rows", side_effect=lambda _, name, overlay=None: [row] if name == "vars" else ()), \
                patch.object(curated, "declare_layout"):
            ledgers.declare(b, repo.ROOT)
        m = b.finish()
        m.root, m.config = repo.ROOT, repo.config()
        self.assertEqual(m.issues, [])
        return m.symbols[SymbolKey("7mfk", "ram", int(row["addr"], 16))]

    def test_eight_real_owned_symbols_keep_the_exact_base_and_test_pair(self):
        m = model()
        self.assertEqual(set(self.rows), set(self.EXPECTED))
        for address, row in self.rows.items():
            with self.subTest(address=f"{address:08x}"):
                symbol = m.symbols[SymbolKey("7mfk", "ram", address)]
                self.assert_pair(address, symbol.evidence)
                self.assertTrue(checks._owned(m, symbol))
                self.assertTrue(any(src.startswith("kb/ram/") for src in symbol.sources))
                self.assertFalse(any("legacy" in item for item in symbol.evidence))
                for item in self.expected_items(address):
                    self.assertIsNone(match.verify(m, symbol, item))

    def test_an_omitted_base_or_test_token_cannot_satisfy_the_compiled_pair(self):
        for address, row in self.rows.items():
            parsed = tokens.parse(row["evidence"])
            for role in tokens.TYPED_TERMINAL:
                with self.subTest(address=f"{address:08x}", omitted=role):
                    changed = {**row, "evidence": ";".join(token.text for token in parsed
                                                          if token.role != role)}
                    symbol = self.declare(changed)
                    with self.assertRaises(AssertionError):
                        self.assert_pair(address, symbol.evidence)
                    expected = self.expected_items(address)[1 if role == "indirect_base" else 0]
                    self.assertEqual([item for item in symbol.evidence if "legacy" not in item],
                                     [expected])

    def test_wrong_offsets_fail_homology_and_structure_grounding(self):
        m = compile.build()
        failures = {}
        for address in self.EXPECTED:
            key = SymbolKey("7mfk", "ram", address)
            symbol = m.symbols[key]
            self.assert_pair(address, symbol.evidence)
            self.assertTrue(levels.held(m, symbol))
            base = self.expected_items(address)[0]
            wrong = {**base, "value": base["value"] + 1}
            symbol.evidence[symbol.evidence.index(base)] = wrong
            failure = match.verify(m, symbol, wrong)
            self.assertIsNotNone(failure)
            self.assertFalse(levels.held(m, symbol))
            failures[key.key] = failure
        issues = [issue for issue in checks.CHECKS["homology"](m)
                  if issue.subject in failures]
        self.assertEqual(Counter(issue.subject for issue in issues),
                         Counter({subject: 1 for subject in failures}))
        for issue in issues:
            self.assertIn(failures[issue.subject], issue.message)

    def test_removing_eight_base_items_restores_their_structure_findings_without_changing_claims(self):
        m = compile.build()
        keys = {SymbolKey("7mfk", "ram", address) for address in self.EXPECTED}
        snapshot = lambda: {key: (m.symbols[key].meaning.home,
                                 copy.deepcopy(m.symbols[key].meaning.props),
                                 copy.deepcopy(m.symbols[key].props)) for key in keys}
        unchanged = snapshot()
        before = set(levels.check(m))
        state = m.symbols[SymbolKey("7mfk", "ram", 0xFFFF1AA8)]
        word = m.symbols[SymbolKey("7mfk", "ram", 0xFFFF1B1A)]
        word_base = {"kind": "indirect", "supports": "identity", "mode": "base",
                     "at": "7mfk:000c1dfa", "value": 0x88E}
        self.assertIn(word_base, word.evidence)
        self.assertTrue(levels.held(m, word))
        self.assertFalse([issue for issue in before if issue.subject == state.meaning.key])
        self.assertFalse([issue for issue in before
                          if "the structure of 7mfk-ffff1b1a/ram," in issue.message])
        ratio = m.symbols[SymbolKey("7mfk", "ram", 0xFFFF196C)]
        self.assertTrue(levels.held(m, ratio))
        self.assertFalse([issue for issue in before
                          if "the structure of 7mfk-ffff196c/ram," in issue.message])
        # Removing the input word's base item restores its own structural
        # boundary through the unchanged input link of the state longword.
        word_position = word.evidence.index(word_base)
        word_removed = word.evidence.pop(word_position)
        without_word_base = set(levels.check(m))
        [next_barrier] = [issue for issue in without_word_base - before
                          if issue.subject == state.meaning.key]
        self.assertIn("the structure of 7mfk-ffff1b1a/ram,", next_barrier.message)
        self.assertIn("(input link)", next_barrier.message)
        self.assertFalse(levels.held(m, word))
        self.assertFalse([issue for issue in without_word_base
                          if "the structure of 7mfk-ffff196c/ram," in issue.message])
        word.evidence.insert(word_position, word_removed)
        self.assertEqual(set(levels.check(m)), before)
        # Removing the state placement restores the earlier input boundary
        # while the input word and ratio placement stay grounded.
        base = self.expected_items(0xFFFF1AA8)[0]
        position = state.evidence.index(base)
        removed = state.evidence.pop(position)
        without_state_base = set(levels.check(m))
        [first_barrier] = [issue for issue in without_state_base - before
                           if "the structure of 7mfk-ffff1aa8/ram," in issue.message]
        self.assertIn("(input link)", first_barrier.message)
        self.assertNotIn(next_barrier, without_state_base)
        self.assertFalse([issue for issue in without_state_base
                          if "the structure of 7mfk-ffff196c/ram," in issue.message])
        state.evidence.insert(position, removed)
        pointed = levels.entries(m)
        for key in keys:
            symbol = m.symbols[key]
            self.assert_pair(key.address, symbol.evidence)
            symbol.evidence.remove(self.expected_items(key.address)[0])
            self.assertFalse(levels.held(m, symbol, pointed))
        after = set(levels.check(m))
        counts = Counter()
        for issue in after - before:
            found = re.search(r"the structure of 7mfk-([0-9a-f]{8})/ram,", issue.message)
            if found and int(found.group(1), 16) in self.EXPECTED:
                counts[int(found.group(1), 16)] += 1
        self.assertEqual(dict(counts), self.STRUCTURE_COUNTS)
        ltft_record_barriers = Counter(
            issue.subject for issue in after - before
            if issue.subject in {"ltft_b1/ram", "ltft_b2/ram"}
            and "the structure of 7mfk-ffff5a93/ram," in issue.message)
        self.assertEqual(ltft_record_barriers,
                         Counter({"ltft_b1/ram": 1, "ltft_b2/ram": 1}))
        self.assertFalse([issue for issue in after
                          if "the structure of 7mfk-ffff196c/ram," in issue.message])
        self.assertEqual(snapshot(), unchanged)
        # The cached model remains intact; a test cannot remove its evidence.
        for key in keys:
            self.assert_pair(key.address, model().symbols[key].evidence)


class Ici0aRatioOwnerTest(unittest.TestCase):
    BASE = {"kind": "indirect", "supports": "identity", "at": "7mfk:00028f06",
            "mode": "base", "value": 0x6E0}
    TEST = {"kind": "test", "supports": "identity",
            "path": "git:archive/stock-proofs-2026-10-26:tools/mapkit/tests/test_ici0a_ratio_path.py",
            "key": "test_ici0a_ratio_cell_path"}

    def test_actual_ratio_has_reviewed_base_test_and_handler_access_roles(self):
        m = model()
        symbol = m.symbols[SymbolKey("7mfk", "ram", 0xFFFF196C)]
        self.assertEqual([e for e in symbol.evidence if e["kind"] in ("indirect", "test")],
                         [self.BASE, self.TEST])
        self.assertIsNone(match.verify(m, symbol, self.BASE))
        owner = SymbolKey("7mfk", "fn", 0x28EA2)
        reader = {(link.type, layout, link.to.symbols[layout].key)
                  for link in symbol.meaning.links
                  if link.owner is symbol.meaning and link.type in ("writer", "reader")
                  for layout in checks._claimed(link)}
        self.assertEqual(reader, {("writer", "7mfk", owner), ("reader", "7mfk", owner)})
        self.assertTrue(any(e.get("kind") == "trace" and e.get("to") == SymbolKey("7mfk", "fn", 0x21BBC)
                            for e in symbol.evidence))
        self.assertTrue(levels.held(m, symbol))
        self.assertFalse([i for i in levels.check(m)
                          if "the structure of 7mfk-ffff196c/ram," in i.message])

    @pytest.mark.slow
    def test_ratio_base_and_direct_references_are_independent_structural_routes(self):
        from kb import sites
        m = compile.build()
        key = SymbolKey("7mfk", "ram", 0xFFFF196C)
        symbol = m.symbols[key]
        evidence = copy.deepcopy(symbol.evidence)
        referenced = {layout: sites.referenced(layout, m.root) for layout in m.layouts}
        props = copy.deepcopy(symbol.props), copy.deepcopy(symbol.meaning.props)
        before = set(levels.check(m))
        self.assertIn(self.BASE, symbol.evidence)
        self.assertIn(self.TEST, symbol.evidence)
        # Accepted direct accesses and reviewed base evidence are independent
        # structural routes. Losing only one must not fabricate a deficiency.
        try:
            with patch.object(sites, "referenced", side_effect=lambda layout, root:
                              frozenset({0xFFFF196C}) if layout == "7mfk" else frozenset()):
                symbol.evidence = [e for e in symbol.evidence if e != self.BASE]
                self.assertTrue(levels.held(m, symbol))
            symbol.evidence = evidence
            with patch.object(sites, "referenced", side_effect=lambda layout, root:
                              referenced[layout] - {key.address} if layout == key.layout else referenced[layout]):
                self.assertTrue(levels.held(m, symbol))
                symbol.evidence = [e for e in symbol.evidence if e != self.BASE]
                self.assertFalse(levels.held(m, symbol))
                after = set(levels.check(m))
                barriers = [i for i in after - before
                            if "the structure of 7mfk-ffff196c/ram," in i.message]
                self.assertEqual(len(barriers), 4)
                self.assertEqual({i.subject for i in barriers},
                                 {"knowing-manul/ram", "pastel-yak/fn",
                                  "pink-mustang/ram", "spry-uakari/reg"})
                self.assertTrue(all("link" in i.message for i in barriers))
                symbol.evidence = evidence
                self.assertTrue(levels.held(m, symbol))
                self.assertFalse([i for i in levels.check(m)
                                  if "the structure of 7mfk-ffff196c/ram," in i.message])
        finally:
            symbol.evidence = evidence
        self.assertEqual((symbol.props, symbol.meaning.props), props)
        self.assertEqual(set(levels.check(m)), before)
        self.assertEqual(model().symbols[key].evidence, evidence)


class DtcLedgerAdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = dtc_projection.read_registry(dtc_projection.SOURCE_ROM)
        cls.tables = dtc_projection.canonical_tables()
        cls.image = derive.image_bytes(repo.layout("7mfk"))

    def declare(self, rows, root=repo.ROOT):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
        with patch.object(ledgers, "rows", side_effect=lambda _, name, overlay=None: rows if name == "dtc" else ()), \
                patch.object(curated, "declare_layout"):
            ledgers.declare(b, root)
        m = b.finish()
        m.root, m.config = repo.ROOT, repo.config()
        return m

    def test_every_dtc_has_three_complete_typed_byte_items(self):
        m = model()
        dtcs = [symbol for symbol in m.symbols.values() if symbol.kind == "dtc"]
        self.assertEqual(len(dtcs), len(self.rows))
        grounded = match.grounded(m, [symbol.key for symbol in dtcs])
        for row in self.rows:
            key = SymbolKey("7mfk", "dtc", int(row["record_addr"], 16))
            symbol = m.symbols[key]
            spans = dtc_projection.canonical_evidence(row, self.tables, len(self.image))
            with self.subTest(index=row["index"]):
                self.assertCountEqual(symbol.evidence, [
                    {"kind": "rom-bytes", "supports": "identity", "at": f"7mfk:{address:08x}",
                     "value": raw.hex()} for address, raw in spans])
                self.assertNotIn("images", symbol.props)
                self.assertGreaterEqual(grounded[key][0], vocab.LEVEL_RANK["code"])
                self.assertTrue(all(match.verify(m, symbol, item) is None
                                    for item in symbol.evidence))
        # The other converted ledgers also own typed evidence.
        table = m.symbols[SymbolKey("7mfk", "tbl", 0xA4AA)]
        self.assertFalse(any("legacy" in item for item in table.evidence))
        self.assertTrue(any(item["kind"] == "l0-context" for item in table.evidence))

    def test_row_mismatches_fail_the_schema_instead_of_creating_a_symbol(self):
        row = next(row for row in self.rows if row["index"] == "17")
        changes = {
            "negative index": {"index": "-1"},
            "upper index": {"index": str(self.tables.count)},
            "code": {"dtc": "P0430"},
            "packed prefix": {"dtc": "C0420"},
            "record": {"record_addr": "00019438"},
            "pointer": {"attribute_addr": "0001603c"},
            "stock attribute": {"stock_attribute": "00b0"},
            "short attribute": {"stock_attribute": "a0"},
            "missing evidence": {"evidence": ""},
            "untyped evidence": {"evidence": "rom_const:0001942c"},
            "short descriptor": {"evidence": row["evidence"].replace(
                "06060c000000042010000000", "0420")},
            "wrong pointer value": {"evidence": row["evidence"].replace(
                "rom_const:0001a190=0001603a", "rom_const:0001a190=0001603c")},
            "wrong attribute value": {"evidence": row["evidence"].replace(
                "rom_const:0001603a=00a0", "rom_const:0001603a=00b0")},
        }
        for name, changed in changes.items():
            with self.subTest(change=name):
                m = self.declare([{**row, **changed}])
                self.assertEqual(len(m.issues), 1)
                self.assertEqual(m.issues[0].check, "schema")
                self.assertEqual(m.issues[0].path, ledgers.PATHS["dtc"].as_posix())
                self.assertFalse(m.symbols)

    def test_duplicate_indices_fail_and_duplicate_codes_keep_separate_symbols(self):
        row = next(row for row in self.rows if row["index"] == "17")
        m = self.declare([row, row])
        self.assertEqual([issue.message for issue in m.issues], ["duplicate index 17"])
        m = self.declare([row for row in self.rows if row["index"] in ("132", "133", "134", "135", "40")])
        self.assertEqual(m.issues, [])
        self.assertEqual(len(m.meanings), 5)
        for code, indices in (("P1078", [132, 134]), ("P1084", [133, 135])):
            self.assertEqual(sorted(meaning.symbols["7mfk"].props["index"]
                                    for meaning in m.meanings if meaning.props["code"] == code), indices)
        nats = m.symbols[SymbolKey("7mfk", "dtc", 0x19540)]
        attribute = next(item for item in nats.evidence
                         if item["at"] == "7mfk:" + nats.props["attribute"])
        self.assertEqual(attribute["value"], "0000")

    def test_image_bytes_are_read_with_the_compiler_root(self):
        root = repo.ROOT / "tmp/issue63/root-probe"
        with patch.object(ledgers, "_dtc_decoder", return_value=dtc_projection), \
                patch.object(dtc_projection, "canonical_tables", return_value=self.tables) as tables, \
                patch.object(derive, "image_bytes", return_value=self.image) as image:
            self.assertEqual(self.declare(self.rows, root).issues, [])
            self.assertIn(dtc_projection.LAYOUTS.as_posix(), ledgers.inputs(root))
        tables.assert_called_once_with(root)
        image.assert_called_once_with(repo.layout("7mfk"), root)

    @pytest.mark.slow
    def test_console_entrypoint_compiles_without_a_pythonpath_override(self):
        completed = subprocess.run(["uv", "run", "kb", "project",
                                    "defs/registries/JK08A.architecture.toml", "--check"],
                                   cwd=repo.ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(completed.stdout, "defs/registries/JK08A.architecture.toml: current\n")


class ProfileAdapterTest(unittest.TestCase):
    def test_a_telemetry_source_joins_the_meaning_of_its_field(self):
        meaning = model().meaning_of(SymbolKey("jk00d", "ram", 0xFFFF1034))
        self.assertEqual((meaning.key, meaning.tier), ("normalized_load/ram", "file"))
        self.assertEqual(meaning.symbols["7mfk"].address, 0xFFFF102C)
        self.assertEqual((meaning.symbols["1nd"].address, meaning.symbols["1nd"].value("level")),
                         (0xFFFE8034, "code"))
        self.assertEqual(meaning.symbols["jk78c"].address, 0xFFFF1032)

    def test_an_unavailable_field_states_absent_or_unresolved_by_its_evidence(self):
        m = model()
        knock = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF121A))
        self.assertEqual({layout: status.state for layout, status in knock.statuses.items()},
                         {"1ek7a": "absent", "1me3b": "absent"})
        self.assertEqual((knock.symbols["jk78c"].address, knock.symbols["1nd"].address),
                         (0xFFFF1204, 0xFFFE8214))
        branch = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF2469))
        self.assertEqual({layout: status.state for layout, status in branch.statuses.items()},
                         {"jk78c": "unresolved", "1nd": "unresolved",
                          "1ek7a": "absent", "1me3b": "absent"})
        # The status of the source meaning states the unavailable field; the
        # target holds no list of the fields.
        self.assertNotIn("unavailable", model().targets[("can_telemetry", "1nd")].props)

    def test_a_hook_word_takes_its_canonical_key(self):
        m = model()
        cases = {("7mfk", 0x000496C0): "ignition_lookup_493e8",
                 ("jk00d", 0x0004A70C): "ignition_lookup_493e8",
                 ("1nd", 0x00074FCC): "ignition_lookup_493e8",
                 ("jk00d", 0x000C3880): "exhaust_cvtc_target_lookup",
                 ("1nd", 0x00074FB0): "ignition_state_lookup",
                 ("jk78c", 0x00021A4C): "displaced_periodic_task"}
        for (layout, address), name in cases.items():
            with self.subTest(layout=layout, address=f"{address:08x}"):
                meaning = m.meaning_of(SymbolKey(layout, "hook", address))
                self.assertEqual((meaning.name, meaning.tier), (name, "file"))
        # The 8MFK key exhaust_cvtc_target_lookup names another word than the
        # canonical key of the same spelling.
        own = m.meaning_of(SymbolKey("jk00d", "hook", 0x000C5B94))
        self.assertNotEqual(own.name, "exhaust_cvtc_target_lookup")
        self.assertIs(own, m.meaning_of(SymbolKey("jk00c", "hook", 0x000C5B58)))

    def test_a_hook_word_links_to_the_meaning_at_its_stock_value(self):
        m = model()
        hook = m.meaning_of(SymbolKey("1nd", "hook", 0x00022184))
        [link] = [link for link in hook.links if link.type == "target"
                  and "1nd" in link.to.symbols]
        self.assertEqual(link.to.symbols["1nd"].address, 0x0006D948)
        self.assertEqual(link.to.key, "knock_function/fn")

    def test_a_join_that_would_hold_two_symbols_of_a_layout_is_refused(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        mask, state = (b.symbol("7mfk", "ram", address, "probe.csv")
                       for address in (0xFFFF22E0, 0xFFFF2497))
        target = b.symbol("1nd", "ram", 0xFFFE92E4, "probe.csv")
        b.join(mask, target, "probe.csv:2", "homology")
        b.join(state, target, "probe.csv:3", "role")
        m = b.finish()
        self.assertEqual([(issue.path, issue.subject) for issue in b.issues],
                         [("probe.csv:3", "1nd-fffe92e4/ram")])
        self.assertEqual(m.meaning_of(target).symbols["7mfk"].address, 0xFFFF22E0)
        self.assertNotIn("1nd", m.meaning_of(state).symbols)

    def test_a_key_that_another_meaning_fills_on_a_layout_binds_a_role(self):
        m = model()
        state = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF2497))
        self.assertEqual((state.key, sorted(state.symbols)),
                         ("fuel_inhibit/ram", ["7mfk", "jk00c", "jk00d"]))
        config = m.targets[("map_switching", "jk78c")].props["roles"]
        self.assertEqual(config["ignition_coordinator_config_byte"]["symbol"],
                         SymbolKey("jk78c", "tbl", 0x8965))
        # Where no mapped row places its address, the key joins its own meaning.
        byte = m.meaning_of(SymbolKey("1me3b", "tbl", 0x8A7D))
        self.assertEqual(byte.key, "ignition_coordinator_config_byte/tbl")
        self.assertEqual({layout: symbol.address for layout, symbol in byte.symbols.items()},
                         {"1ek7a": 0x8AF5, "1me3b": 0x8A7D})
        self.assertFalse([issue for issue in m.issues if "refused join" in issue.message])

    def test_every_layout_writes_the_data_register_of_mailbox_26(self):
        m = model()
        address = 0xFFFFDC48
        data = m.meaning_of(SymbolKey("7mfk", "reg", address))
        layouts = {layout for (feature, layout), target in m.targets.items()
                   if feature == "can_telemetry" and target.status == "supported"}
        self.assertEqual(data.key, "mailbox_data/reg")
        self.assertEqual({layout: symbol.address for layout, symbol in data.symbols.items()},
                         dict.fromkeys(layouts, address))

    def test_a_register_at_another_address_fills_a_role(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        rows = [("7mfk", 0xFFFFDC48, "can_symbols", "probe.py"),
                ("jk78c", 0xFFFFDC48, "can_symbols", "probe.toml"),
                *((layout, 0xFFFFDC08, "can_symbols", "probe.toml")
                  for layout in ("jk00c", "jk00d"))]
        facts = SimpleNamespace(roles={}, all_words=frozenset(),
                                key_entries=lambda: ({"mailbox_data": rows}, {}))
        targets = defaultdict(dict)
        profiles._declare_keys(b, facts, targets)
        m = b.finish()
        data = m.meaning_of(SymbolKey("7mfk", "reg", 0xFFFFDC48))
        self.assertEqual((data.key, sorted(data.symbols)), ("mailbox_data/reg", ["7mfk", "jk78c"]))
        # The data register of mailbox 24 takes the key on both layouts in
        # its role, one meaning on both.
        roles = [targets[("can_telemetry", layout)]["roles"]["mailbox_data"]["symbol"]
                 for layout in ("jk00c", "jk00d")]
        self.assertEqual(roles, [SymbolKey(layout, "reg", 0xFFFFDC08)
                                 for layout in ("jk00c", "jk00d")])
        register = m.meaning_of(roles[0])
        self.assertIs(register, m.meaning_of(roles[1]))
        self.assertIsNot(register, data)

    def test_a_native_symbol_can_have_an_explicit_unsupported_wire_role(self):
        m = model()
        source = m.entities[("field", "maf_b1_raw")].refs["source"][0]
        meaning = m.meaning_of(source)
        target = copy.copy(m.targets[("can_telemetry", "jk78c")])
        target.props = dict(target.props)
        target.props["unsupported"] = [{"symbol": meaning.symbols["jk78c"].key,
                                         "note": "The native bit layout requires a wire conversion."}]
        targets = {feature: held for (feature, layout), held in m.targets.items() if layout == "jk78c"}
        targets["can_telemetry"] = target
        fields = profiles.telemetry_fields(m)
        stocks = profiles._stocks(m)
        document = profiles._profile(m, m.layouts["jk78c"], targets, fields, stocks)
        self.assertIn("maf_b1_raw", document["telemetry_unavailable"])
        self.assertNotIn("maf_b1_raw", document["telemetry_sources"])
        rows = profiles.correspondence_rows(m, "jk78c", targets, fields, stocks)
        [row] = [row for row in rows if row["domain"] == "telemetry" and row["key"] == "maf_b1_raw"]
        self.assertEqual(row["status"], profiles.UNSUPPORTED)
        self.assertIn("wire conversion", row["evidence"])

    def test_a_pointer_into_a_table_row_keeps_the_row_address(self):
        m = model()
        # The release curve is the second row of the grouped rev-limit curves:
        # its hook targets the table plus 0x10, and the fuel-cut binding of the
        # same literal takes the stock word.
        stocks = profiles._stocks(m)
        self.assertEqual(stocks[SymbolKey("1nd", "hook", 0x76CAC)], 0x17212)
        self.assertEqual(stocks[SymbolKey("1me3b", "hook", 0x7B334)], 0x172C6)
        targets = native.fuel_cut_document(m)["target"]
        self.assertIn({"site": 0x76CAC, "target": 0x17212},
                      targets["1ND0A"]["pointer_bindings"])
        self.assertIn({"site": 0x7B334, "target": 0x172C6},
                      targets["1ME3B"]["pointer_bindings"])
        # A stock word beyond the 32 bytes of the curves binds no owner.
        [image] = [image for rom, _, image in native.targets(m) if rom == "1ND0A"]
        data = bytearray(native._image(image.path))
        data[0x76CAC:0x76CB0] = (0x17222).to_bytes(4, "big")
        function = m.meaning_of(SymbolKey("1nd", "fn", 0x76AD2)).symbols["1nd"]
        with self.assertRaises(KbError) as caught:
            native._function_bindings(m, function, "1nd", data)
        self.assertIn("the word 00017222 at 1nd:00076cac lies outside the storage of "
                      "rev_limit_fuel_cut_curves/tbl", str(caught.exception))

    def test_a_target_specific_telemetry_row_fills_the_role_of_its_field(self):
        m = model()
        target = m.targets[("can_telemetry", "jk78c")].props
        role = target["roles"]["alpha_n_flow_raw"]
        self.assertEqual(role["symbol"], SymbolKey("jk78c", "ram", 0xFFFF22F8))
        self.assertIn("column of the target Fuel Compensation surfaces", role["note"])
        snapshot = m.meaning_of(role["symbol"])
        self.assertEqual((snapshot.key, snapshot.symbols["1nd"].address),
                         ("diamond-macaque/ram", 0xFFFE93AA))
        self.assertNotIn("alpha_n_flow_raw", target.get("symbols", {}))
        # The source meaning of the field keeps the homolog of its producer.
        flow = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1170))
        self.assertEqual((flow.key, flow.symbols["jk78c"].address),
                         ("alpha_n_flow/ram", 0xFFFF115C))
        self.assertIsNot(snapshot, flow)

    def test_a_record_of_the_image_byte_keys_is_one_32_bit_word(self):
        m = model()
        for layout, address in (("7mfk", 0x9766), ("7mfk", 0x97BE), ("7mfk", 0x97C6),
                                ("jk78c", 0x945A)):
            with self.subTest(layout=layout, address=f"{address:08x}"):
                symbol = m.symbols[SymbolKey(layout, "tbl", address)]
                self.assertEqual(match.storage_size(symbol), 4)

    def test_untyped_legacy_evidence_goes_to_the_audit_under_its_registry(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        item = {"kind": "rom-bytes", "supports": "identity", "value": 1,
                "legacy": "rom_const:1"}
        for src in ("one.csv", "two.csv"):
            b.symbol("7mfk", "tbl", 0x9000, src, evidence=[item, {**item, "at": 0x9000}])
        found = checks.audit(b.finish(), ("untyped",))["untyped"]
        self.assertEqual([(issue.path, issue.subject, issue.message) for issue in found],
                         [(src, "7mfk-00009000/tbl",
                           "token rom_const:1 gives rom-bytes evidence without at")
                          for src in ("one.csv", "two.csv")])
        self.assertEqual(checks.audit(model(), ("untyped",))["untyped"], [])

    def test_an_unsupported_map_row_gives_way_to_a_target_specific_surface(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "tbl", 0x00009A1A))
        self.assertEqual(meaning.symbols["1nd"].address, 0x00009980)
        self.assertNotIn("1nd", meaning.statuses)
        self.assertEqual(meaning.statuses["1me3b"].state, "absent")

    def test_the_registries_are_their_canonical_rendering(self):
        fields = profiles.telemetry_fields(model())
        text = (repo.ROOT / profiles.PROFILES).read_text(encoding="utf-8")
        self.assertEqual(profiles.render_profiles(tomllib.loads(text), fields), text)
        for path, rows in profiles.correspondence(repo.ROOT).values():
            with self.subTest(path=path):
                self.assertEqual(profiles.render_correspondence(rows, fields),
                                 (repo.ROOT / path).read_text(encoding="utf-8"))

    def test_a_hook_row_names_the_7mfk_word_of_its_meaning(self):
        m = model()
        for layout, (path, rows) in profiles.correspondence(repo.ROOT).items():
            for row in rows:
                if row["domain"] not in profiles.HOOK_DOMAINS:
                    continue
                with self.subTest(path=path, key=row["key"]):
                    self.assertFalse(row["variant"])
                    target = m.meaning_of(SymbolKey(layout, "hook", int(row["target"], 16)))
                    if row["source"]:
                        self.assertIs(target, m.meaning_of(
                            SymbolKey("7mfk", "hook", int(row["source"], 16))))
                    else:
                        self.assertNotIn("7mfk", target.symbols)

    def test_feature_targets_carry_hooks_allocations_and_status(self):
        m = model()
        rolling = m.targets[("rolling_launch", "7mfk")]
        self.assertEqual(rolling.status, "supported")
        self.assertIn("displaced_periodic_task", rolling.props["hooks"])
        self.assertTrue(rolling.props["allocations"])
        self.assertEqual(rolling.props["allocations"]["flags"]["address"], "ffff5d42")
        self.assertEqual(m.targets[("rolling_launch", "jk00d")].status, "planned")
        runtime = m.targets[("runtime", "1nd")]
        self.assertEqual(runtime.props["rom_delta"], 0x60000)
        self.assertEqual(runtime.props["free_ram_start"], "ffff0c00")
        self.assertIn(("feature", "map_switching"), m.entities)

    def test_feature_targets_carry_the_key_tables_of_the_profile(self):
        m = model()
        maps = m.targets[("map_switching", "1me3b")].props
        self.assertEqual(maps["families"]["rev_limit_fuel_cut_caps"],
                         SymbolKey("1me3b", "tbl", 0x00009266))
        self.assertEqual(maps["symbols"]["ignition_lookup"], SymbolKey("1me3b", "fn", 0x00029BA8))
        # A role key enters `roles`, not `symbols`.
        roles = m.targets[("map_switching", "jk78c")].props
        self.assertIn("ignition_coordinator_config_byte", roles["roles"])
        self.assertNotIn("ignition_coordinator_config_byte", roles["symbols"])
        canonical = m.targets[("map_switching", "7mfk")].props
        self.assertEqual(canonical["families"]["fuel_compensation_main"],
                         SymbolKey("7mfk", "tbl", 0x0000A29A))
        self.assertEqual(canonical["symbols"]["ignition_lookup"],
                         SymbolKey("7mfk", "fn", 0x00026230))
        self.assertEqual(m.targets[("can_telemetry", "7mfk")].props["symbols"]["mailbox_data"],
                         SymbolKey("7mfk", "reg", 0xFFFFDC48))

    def test_a_correspondence_row_without_a_profile_key_enters_requires(self):
        m = model()
        target = m.targets[("map_switching", "1nd")]
        required = {m.meaning_of(key).key for key in target.props["requires"]}
        self.assertEqual(required, {
            "over_run_channel_multiplier/tbl", "rev_fuel_cut_delay/ram",
            "rev_fuel_cut_selector/ram", "rev_fuel_cut_state/ram", "rev_fuel_cut_state_machine/fn",
            "rev_limit_fuel_cut_delay_calibration/tbl"})
        self.assertLessEqual(set(target.props["requires"]), set(target.needs()))
        self.assertIn(target.props["families"]["over_run_fuel_cut"], target.needs())

    def test_rows_give_notes_bases_variants_and_unsupported_entries(self):
        m = model()
        runtime = m.targets[("runtime", "jk78c")].props
        self.assertEqual(sorted(runtime["notes"]), sorted(profiles.RUNTIME_KEYS[3:11]))
        self.assertEqual(sorted(runtime["basis"]), ["free_ram", "free_rom"])
        can = m.targets[("can_telemetry", "jk78c")].props
        self.assertEqual(sorted(can["notes"]), sorted(profiles.CAN_KEYS))
        self.assertEqual(sorted(can["basis"]), ["can", "telemetry"])
        self.assertEqual(m.targets[("can_telemetry", "7mfk")].props["feedback_payload_offset"],
                         0x20)
        maps = m.targets[("map_switching", "1nd")].props
        self.assertIn({"symbol": SymbolKey("1nd", "tbl", 0x0000A2C0), "variant": "alternate"},
                      maps["variants"])
        unsupported = {m.meaning_of(item["symbol"]).key for item in maps["unsupported"]}
        self.assertIn("exhaust_cvtc_target/tbl", unsupported)
        self.assertTrue(maps["note"])
        # The allocation rows give the canonical runtime envelope.
        self.assertEqual(m.targets[("runtime", "7mfk")].props,
                         {"injected_rom_start": "000d2108", "injected_rom_end": "000d6000",
                          "injected_ram_start": "ffff5d00", "injected_ram_end": "ffff6000"})

    def test_a_later_feature_states_its_hook_text_in_its_target(self):
        m = model()
        word = SymbolKey("1nd", "hook", 0x0002B398)
        self.assertEqual(profiles.row_item(m.symbols[word], "the word")[1]["note"],
                         "Literal call target identifies the exact startup initializer")
        self.assertNotIn("note", m.targets[("map_switching", "1nd")].props["hooks"]
                         ["startup_initializer"])
        entry = m.targets[("can_telemetry", "1nd")].props["hooks"]["startup_state_clear"]
        self.assertEqual((entry["hook"], entry["note"]),
                         (word, "Telemetry clear can chain from the startup literal"))


class DefinitionAdapterTest(unittest.TestCase):
    def test_a_table_and_axis_operand_gives_a_symbol_of_each_kind(self):
        m = model()
        for kind in ("tbl", "axis"):
            meaning = m.meaning_of(SymbolKey("7mfk", kind, 0x0000E98E))
            self.assertIs(meaning, m.meaning_of(SymbolKey("jk00d", kind, 0x000104A2)))
            self.assertIs(meaning, m.meaning_of(SymbolKey("jk00c", kind, 0x00010492)))
        self.assertIsNot(m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000E98E)),
                         m.meaning_of(SymbolKey("7mfk", "axis", 0x0000E98E)))

    def test_the_function_kind_is_the_kind_of_the_row_evidence(self):
        m = model()
        symbol = m.symbols[SymbolKey("jk00d", "tbl", 0x000104A2)]
        state, item = definitions.row_item(symbol)
        self.assertEqual((state, item["kind"], item["to"]),
                         (definitions.HOMOLOGOUS, "l0", "7mfk:0000e98e"))
        self.assertIsNone(match.verify(m, symbol, item))

    @pytest.mark.slow
    def test_a_reviewed_target_is_an_anchor_of_the_source_meaning(self):
        m = model()
        meaning = m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000B43A))
        self.assertEqual(meaning.name, "intake_cvtc_target")
        self.assertEqual(meaning.symbols["jk00d"].address, 0x0000B7CE)
        self.assertIn({"kind": "l0", "supports": "identity"},
                      [{key: item[key] for key in ("kind", "supports")}
                       for item in meaning.symbols["jk00d"].evidence])

    def test_an_unsupported_row_states_its_reason(self):
        m = model()
        self.assertEqual(m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000AB4A)).statuses["1nd"].state,
                         "absent")
        for source, targets in (
            (0xA9AA, (("1nd", 0xA7D0), ("1me3b", 0xA704))),
            (0x12552, (("1nd", 0x13F0A), ("1me3b", 0x13CE6))),
        ):
            meaning = m.meaning_of(SymbolKey("7mfk", "tbl", source))
            for layout, address in targets:
                self.assertIs(m.meaning_of(SymbolKey(layout, "tbl", address)), meaning)
                self.assertNotIn(layout, meaning.statuses)
        inert = m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000991A))
        self.assertEqual(inert.symbols["1nd"].address, 0x00009880)
        omitted = m.targets[("definitions", "1nd")].props["omitted"]
        self.assertIn(SymbolKey("1nd", "tbl", 0x00009880), [item["symbol"] for item in omitted])

    def test_projections_give_the_image_entries_of_the_definitions_target(self):
        m = model()
        target = m.targets[("definitions", "1nd")]
        self.assertEqual(target.status, "supported")
        self.assertEqual(sorted(target.props["images"]), ["1ND0A", "1ND3B"])
        self.assertEqual(target.props["images"]["1ND3B"]["switch"],
                         {"developer_immobilizer": "00008668",
                          "can_telemetry_startup": "00134e03",
                          "cruise_control_switch": "00008a11"})
        self.assertEqual([item["variant"] for item in target.props["variants"]],
                         ["default", "default"])
        self.assertEqual([issue for issue in m.issues if issue.check == "schema"], [])


class InterpFilesTest(unittest.TestCase):
    """The interpolation facts that the entity files own from stage 3."""

    def test_a_kernel_entry_inside_a_function_names_the_function_and_the_offset(self):
        m = model()
        interp = m.meaning_of(SymbolKey("7mfk", "fn", 0x000263F4)).props["interp"]
        self.assertEqual({key: value for key, value in interp.items() if key != "kernel"},
                         {"access": "implicit", "offset": 4, "cols": 16, "step": 4096})
        kernel = m.meaning_of(interp["kernel"])
        self.assertEqual(interp["kernel"], SymbolKey("7mfk", "fn", 0x00026A60))
        self.assertEqual({layout: symbol.address for layout, symbol in kernel.symbols.items()},
                         {"7mfk": 0x26A60, "jk00c": 0x27664, "jk00d": 0x27664, "1nd": 0x28EA4,
                          "jk78c": 0x28888})
        found = {item["key"] for item in kernel.symbols["jk00d"].evidence
                 if item["kind"] == "interp-contract"}
        self.assertEqual(found, {"00026a60", "00026a64", "00026a74", "00026a7c", "00026a80",
                                 "00026a84", "00026a88"})

    def test_a_fused_leaf_keeps_its_own_signature_as_an_override(self):
        m = model()
        meaning = m.meaning_of(SymbolKey("1me3b", "fn", 0x00029BA8))
        self.assertEqual(meaning.key, "ignition_lookup/fn")
        self.assertEqual(meaning.props["interp"]["kernel"], SymbolKey("7mfk", "fn", 0x00026944))
        own = meaning.symbols["1me3b"].props["interp"]
        self.assertEqual(own["kernel"], SymbolKey("1me3b", "fn", 0x00029BA8))
        self.assertEqual({key: value for key, value in own.items() if key != "kernel"},
                         {key: value for key, value in meaning.props["interp"].items()
                          if key != "kernel"})
        self.assertNotIn("interp", meaning.symbols["jk00d"].props)

    def test_a_copied_wrapper_carries_its_bytes_and_its_call_of_the_kernel_entry(self):
        m = model()
        symbol = m.symbols[SymbolKey("jk00c", "fn", 0x00026FC0)]
        self.assertIs(symbol.meaning, m.meaning_of(SymbolKey("jk00d", "fn", 0x00026FC0)))
        self.assertEqual([(item["kind"], item["at"], item.get("to")) for item in symbol.evidence],
                         [("byte-identical", "jk00c:00026fc0", "jk00d:00026fc0"),
                          ("l0", "jk00c:00026fc8", None)])
        _, entry = match.interp_entry(m, symbol)
        self.assertEqual(match.kernel_calls(m, symbol, entry)[0], 0x00026FC8)
        self.assertTrue(all(source.startswith("kb/fn/") for source in symbol.sources))

    def test_an_unsupported_correspondence_is_an_unresolved_search(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x000261B8))
        for layout in ("1nd", "jk78c"):
            status = meaning.statuses[layout]
            self.assertEqual((status.state, status.props["method"], status.props["count"]),
                             ("unresolved", "interp-contract", 0))
            self.assertEqual(list(status.evidence), [])
            self.assertRegex(status.props["l0"], r"^[0-9a-f]{16}$")

    def test_the_registries_are_projections_of_the_files(self):
        m = model()
        files = {**interp.render_registries(m), **interp.render_correspondences(m)}
        self.assertEqual(sorted(files), [f"defs/registries/{name}" for name in (
            "1EK7A.interp.csv", "1ME3B.interp.csv", "1ND0A.interp.csv", "JK00D.interp.csv",
            "JK08A-1ME3B.interp-correspondence.csv", "JK08A-1ND0A.interp-correspondence.csv",
            "JK08A-JK00D.interp-correspondence.csv",
            "JK08A-JK78C.interp-correspondence.csv", "JK08A.interp.csv", "JK78C.interp.csv")])
        for path, text in files.items():
            with self.subTest(path=path):
                self.assertEqual((repo.ROOT / path).read_text(encoding="utf-8"), text)
        self.assertNotIn(interp, adapters.ADAPTERS)


def _readers(meaning, layout):
    """{accessor address: evidence} of the reader links of a meaning on a layout."""
    return {link.to.symbols[layout].address: link.evidence for link in meaning.links
            if link.type == "reader" and layout in link.to.symbols and layout in link.stated}


class NativeAdapterTest(unittest.TestCase):
    """The native facts that the entity files own from stage 3, and the
    adapter that states them from the registries."""

    def test_a_native_id_joins_its_targets_and_names_the_meaning(self):
        meaning = model().meaning_of(SymbolKey("jk78c", "tbl", 0x00009FBA))
        self.assertEqual((meaning.key, meaning.tier, meaning.home),
                         ("fuel_compensation_alternate/tbl", "file", "jk78c"))
        self.assertEqual({layout: symbol.address for layout, symbol in meaning.symbols.items()},
                         {"jk78c": 0x9FBA, "1nd": 0xA2C0, "1me3b": 0xA1F4, "1ek7a": 0xA2AC})
        self.assertIn("fuel_compensation_main_alternate",
                      {name for name, _, _ in meaning.other_names})
        self.assertEqual((meaning.props["cols"], meaning.props["rows"], meaning.props["storage"]),
                         (16, 16, "uint8"))
        self.assertEqual(meaning.props["editor"]["order"], 21)

    def test_a_layout_that_differs_keeps_its_keys_as_overrides(self):
        meaning = model().meaning_of(SymbolKey("jk78c", "axis", 0x000160CA))
        self.assertEqual((meaning.key, meaning.props["quantity"]),
                         ("vvel_duration_hot_intake_idle_axis_x/axis", "rpm"))
        self.assertNotIn("unit", meaning.props)
        own = meaning.symbols["1nd"].props
        self.assertEqual((own["quantity"], own["editor"]["name"]),
                         ("temp", "Coolant Temperature [degC]"))
        self.assertNotIn("scale", own)
        self.assertNotIn("unit", own)
        self.assertTrue(all("x-50 degC" in note for note in own["note"]))
        self.assertNotIn("quantity", meaning.symbols["jk78c"].props)

    def test_a_pointer_binding_gives_evidence_and_a_reader_link(self):
        m = model()
        axis = m.meaning_of(SymbolKey("jk78c", "axis", 0x000160CA))
        displaced = {"kind": "indirect", "supports": "identity", "at": "jk78c:00056678",
                     "mode": "base", "value": 0xD0}
        self.assertEqual(axis.symbols["jk78c"].evidence, [displaced])
        self.assertIn(displaced, _readers(axis, "jk78c")[0x000564A4])
        table = m.meaning_of(SymbolKey("jk78c", "tbl", 0x00009FBA))
        self.assertEqual([item["at"] for item in table.symbols["jk78c"].evidence],
                         ["jk78c:0002febc", "jk78c:00040f70"])
        self.assertEqual(sorted(_readers(table, "jk78c")), [0x0002F596, 0x00040958])
        axes = {link.slot: link.to.key for link in table.links if link.type == "axis"}
        self.assertEqual(sorted(axes), ["x", "y"])

    def test_an_accessor_takes_evidence_at_its_first_census_call_of_a_bound_entry(self):
        accessor = model().symbols[SymbolKey("jk78c", "fn", 0x00040958)]
        self.assertFalse(accessor.implicit)
        self.assertEqual(accessor.evidence[0],
                         {"kind": "l0", "supports": "identity", "at": "jk78c:00040e00"})

    def test_an_axis_link_takes_evidence_at_the_first_census_call_that_passes_both(self):
        table = model().meaning_of(SymbolKey("jk78c", "tbl", 0x00009FBA))
        for link in table.links:
            if link.type == "axis":
                with self.subTest(slot=link.slot):
                    self.assertEqual(sorted(item["at"] for item in link.evidence),
                                     ["1ek7a:00034a46", "1me3b:00033cec",
                                      "1nd:00030f7c", "jk78c:0002fd32"])

    def test_values_sha256_must_equal_the_digest_of_the_image_block(self):
        catalog = repo.images()
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        entry = {"id": "probe_surface", "address": 0xA000, "width": 2, "height": 1,
                 "storagetype": "uint8", "values_sha256": "0" * 64}
        native.declare_tables(b, {"schema_version": 3, "target": {
            "1ME3B": {"stock_sha256": catalog["1ME3B"].sha256, "table": [entry]}}},
            "probe.toml", catalog)
        self.assertEqual([(issue.check, issue.subject) for issue in b.issues],
                         [("audit", "target.1ME3B.probe_surface")])

    def test_text_that_the_images_of_a_layout_state_differently_names_its_image(self):
        meaning = model().meaning_of(SymbolKey("1nd", "tbl", 0x0000E6C8))
        self.assertEqual((meaning.key, meaning.home),
                         ("vvel_duration_mode_14/tbl", "1nd"))
        self.assertTrue(meaning.props["summary"].startswith("Mode 14 duration surface"))
        notes = meaning.symbols["1nd"].props["note"]
        self.assertEqual(sorted({note.split(": ", 1)[0] for note in notes}), ["1ND0A", "1ND3B"])

    def test_a_target_whose_semantics_differ_keeps_its_summary_as_an_override(self):
        meaning = model().meaning_of(SymbolKey("1nd", "tbl", 0x0001B8DE))
        own = meaning.symbols["1nd"].props
        self.assertTrue(own["summary"].startswith("Second copy of monitor floor A"))
        self.assertNotEqual(own["summary"], meaning.props["summary"])
        self.assertNotIn(own["summary"], own.get("note", ()))
        self.assertNotIn("summary", meaning.symbols[meaning.home].props)

    def test_the_images_of_one_layout_state_one_semantics_text(self):
        catalog = repo.images()
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        entry = {"id": "probe_surface", "address": 0xA000, "width": 2, "height": 1,
                 "storagetype": "uint8", "semantics": "One text."}
        native.declare_tables(b, {"schema_version": 3, "target": {
            "1ND0A": {"stock_sha256": catalog["1ND0A"].sha256, "table": [entry]},
            "1ND3B": {"stock_sha256": catalog["1ND3B"].sha256,
                      "table": [{**entry, "semantics": "Another text."}]}}},
            "probe.toml", catalog)
        self.assertEqual([(issue.check, issue.subject) for issue in b.issues],
                         [("schema", "probe_surface@1nd")])

    def test_an_absent_entry_gives_l0_evidence_at_the_function_its_text_names(self):
        meaning = model().meaning_of(SymbolKey("1nd", "tbl", 0x0000E6C8))
        found = {layout: (status.state, [item["at"] for item in status.evidence])
                 for layout, status in meaning.statuses.items()}
        self.assertEqual(found, {"jk78c": ("absent", ["jk78c:000564a4"]),
                                 "1me3b": ("absent", ["1me3b:00062fac"])})

    def test_the_fuel_cut_state_names_its_bits_on_each_layout(self):
        meaning = model().meaning_of(SymbolKey("jk78c", "ram", 0xFFFF23F5))
        bits = lambda value: [(item["bit"], item["name"]) for item in value]
        self.assertEqual((meaning.home, bits(meaning.props["bit"])),
                         ("1me3b", [(2, "armed"), (3, "active")]))
        self.assertNotIn("bit", meaning.symbols["1me3b"].props)
        self.assertEqual(bits(meaning.symbols["jk78c"].props["bit"]), [(3, "armed"), (4, "active")])
        self.assertEqual(bits(meaning.symbols["1nd"].props["bit"]), [(4, "armed"), (5, "active")])

    def test_fuel_cut_keys_join_their_targets_and_bindings_read_the_function(self):
        m = model()
        axis = m.meaning_of(SymbolKey("jk78c", "axis", 0x00016A64))
        self.assertEqual({layout: symbol.address for layout, symbol in axis.symbols.items()},
                         {"jk78c": 0x16A64, "1nd": 0x17072, "1me3b": 0x17106, "1ek7a": 0x17B3E})
        function = m.meaning_of(SymbolKey("jk78c", "fn", 0x0006AEB8))
        call = function.symbols["jk78c"].evidence[-1]
        self.assertEqual((call["kind"], call["at"], call["value"]), ("l0", "jk78c:0006a9e8", 3))
        base = m.meaning_of(SymbolKey("jk78c", "ram", 0xFFFF1084))
        self.assertEqual(list(_readers(base, "jk78c")), [0x0006AEB8])
        self.assertEqual(base.symbols["jk78c"].evidence,
                         [{"kind": "l0", "supports": "identity", "at": "jk78c:0006b044"}])

    def test_the_fuel_cut_curves_take_the_axis_as_their_x_axis(self):
        m = model()
        curves = m.meaning_of(SymbolKey("jk78c", "tbl", _fuel_cut()["JK78C"]["curves_address"]))
        axis = m.meaning_of(SymbolKey("jk78c", "axis", 0x16A64))
        links = [link for link in curves.links if link.type == "axis"]
        self.assertEqual([(link.slot, link.to.key) for link in links], [("x", axis.key)])
        self.assertEqual(sorted(item["at"] for item in links[0].evidence),
                         ["1ek7a:0007c8ac", "1me3b:0007b1bc", "1nd:00076aee", "jk78c:0006aeea"])

    def test_the_scheduler_word_gives_the_coordinator_rom_bytes_evidence(self):
        coordinator = model().symbols[SymbolKey("jk78c", "fn", 0x0006A9B0)]
        self.assertIn({"kind": "rom-bytes", "supports": "identity", "at": "jk78c:00021ac8",
                       "value": "0006a9b0"}, coordinator.evidence)

    def test_the_fuel_cut_values_give_the_geometry_of_their_symbols(self):
        m = model()
        target = _fuel_cut()["JK78C"]

        def geometry(kind, key):
            props = m.meaning_of(SymbolKey("jk78c", kind, target[key])).props
            return tuple(props.get(name) for name in ("points", "cols", "rows", "storage"))

        self.assertEqual(geometry("axis", "axis_address"), (8, None, None, "uint16"))
        self.assertEqual(geometry("tbl", "caps_address"), (None, 2, 1, "uint16"))
        self.assertEqual(geometry("tbl", "curves_address"), (None, 8, 2, "uint16"))
        self.assertEqual(geometry("tbl", "delay_calibration_address"), (None, 1, 1, "uint8"))

    def test_fuel_cut_values_that_differ_from_the_image_are_an_issue(self):
        targets = _fuel_cut()
        targets["1ME3B"]["curve_values"][0] += 1
        self.assertEqual(_fuel_cut_issues(targets), [("audit", "target.1ME3B.curve_values")])

    def test_each_fuel_cut_datum_takes_evidence_at_its_first_reference_in_the_function(self):
        m = model()
        item = lambda at: {"kind": "l0", "supports": "identity", "at": at}
        # A correspondence row states its text as the note of the item.
        stated = lambda key: [{name: value for name, value in found.items() if name != "note"}
                              for found in m.symbols[key].evidence]
        self.assertIn(item("jk78c:0006aedc"), stated(SymbolKey("jk78c", "ram", 0xFFFF10E5)))
        self.assertIn(item("1nd:00076b1e"), stated(SymbolKey("1nd", "ram", 0xFFFE94BA)))

    def test_a_call_site_off_its_instruction_ordinal_is_an_issue(self):
        targets = _fuel_cut()
        targets["JK78C"]["predicate_call_site"] += 2
        self.assertEqual(_fuel_cut_issues(targets),
                         [("schema", "target.JK78C.predicate_call_site")])

    def test_the_targets_of_one_layout_state_one_evidence_text(self):
        targets = _fuel_cut()
        targets["1ND3B"]["evidence"] = "Another text."
        self.assertEqual(_fuel_cut_issues(targets), [("schema", "target.1ND3B.evidence")])

    def test_the_registries_are_their_canonical_rendering(self):
        for path, render in ((native.TABLES, native.render_tables),
                             (native.FUEL_CUT, native.render_fuel_cut)):
            with self.subTest(path=path):
                text = (repo.ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(render(tomllib.loads(text)), text)

    def test_the_registries_are_projections_of_the_files(self):
        m = model()
        files = {native.TABLES: native.render_tables(native.tables_document(m)),
                 native.FUEL_CUT: native.render_fuel_cut(native.fuel_cut_document(m))}
        for path, text in files.items():
            with self.subTest(path=path):
                self.assertEqual((repo.ROOT / path).read_text(encoding="utf-8"), text)
        self.assertNotIn(native, adapters.ADAPTERS)
        self.assertTrue(all(source.startswith("kb/")
                            for source in m.symbols[SymbolKey("1nd", "tbl", 0x0000E6C8)].sources))

    def test_an_entry_that_some_images_of_a_layout_carry_gives_the_symbol_images(self):
        catalog = repo.images()
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        entry = {"id": "probe_surface", "address": 0xA000, "width": 2, "height": 1,
                 "storagetype": "uint8"}
        native.declare_tables(b, {"schema_version": 3, "target": {
            "1ND0A": {"stock_sha256": catalog["1ND0A"].sha256, "table": [entry]},
            "1ND3B": {"stock_sha256": "0" * 64}}}, "probe.toml", catalog)
        meaning = b.finish().meaning_of(SymbolKey("1nd", "tbl", 0xA000))
        self.assertEqual(meaning.symbols["1nd"].props["images"], ["1ND0A"])
        self.assertEqual([(issue.check, issue.subject) for issue in b.issues],
                         [("audit", "target.1ND3B")])


def _fuel_cut():
    return tomllib.loads((repo.ROOT / native.FUEL_CUT).read_text(encoding="utf-8"))["target"]


def _fuel_cut_issues(targets):
    """(check, subject) of the issues of a fuel-cut document of these targets."""
    b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
    native.declare_fuel_cut(b, repo.ROOT, {"schema_version": 1, "target": targets},
                            "probe.toml", repo.images())
    return [(issue.check, issue.subject) for issue in b.issues]


def _sources(meaning):
    """{offset: (kind, address)} of the source links of a DID meaning on `7mfk`."""
    return {link.offset: (link.to.kind, link.to.symbols["7mfk"].address)
            for link in meaning.links if link.type == "source"}


class DidTableTest(unittest.TestCase):
    def test_a_did_is_its_table_slot_and_returns_its_source(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "did", 0x000228A0))
        self.assertEqual((meaning.props["number"], meaning.props["width"],
                          meaning.props["level"]), (0x1201, 2, "code"))
        self.assertEqual(meaning.symbols["7mfk"].evidence, [{
            "kind": "did-table", "supports": "identity", "at": "7mfk:000228a0",
            "value": "ffff11f4"}])
        self.assertEqual(_sources(meaning), {None: ("ram", 0xFFFF11F4)})

    def test_an_assembled_response_orders_its_bytes_by_offset(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "did", 0x00022A48))
        self.assertEqual(meaning.props["number"], 0x130D)
        self.assertEqual(_sources(meaning), {0: ("ram", 0xFFFF2A83), 1: ("ram", 0xFFFF2A81)})

    def test_a_rom_source_is_a_table_inside_the_calibration_region(self):
        m = model()
        self.assertEqual(_sources(m.meaning_of(SymbolKey("7mfk", "did", 0x000227C8))),
                         {None: ("tbl", 0x00008AD1)})
        self.assertEqual(_sources(m.meaning_of(SymbolKey("7mfk", "did", 0x00022BB4))),
                         {None: ("const", 0x00022BAE)})

    def test_a_dynamic_did_has_no_source(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "did", 0x000228C8))
        self.assertEqual((meaning.props["number"], _sources(meaning)), (0x120B, {}))
        self.assertIn("dedicated branch", meaning.props["note"][0])

    def test_every_image_of_the_layout_carries_the_table(self):
        m = model()
        self.assertEqual([issue for issue in m.issues if issue.path.endswith("sid22_inventory.py")],
                         [])
        numbers = [meaning.props["number"] for meaning in m.meanings if meaning.kind == "did"
                   and "7mfk" in meaning.symbols and meaning.symbols["7mfk"].evidence]
        self.assertEqual(len(numbers), 276)
        rolling = m.meaning_of(SymbolKey("7mfk", "did", 0x000228E0))
        self.assertEqual((rolling.props["number"], len(rolling.symbols)), (0x1211, 6))


def _probe(items):
    """A signal catalog of JK08A with the given signals."""
    return {"schema_version": 1, "rom": "JK08A", "telemetry_profile": "tuning",
            "full_rate_hz": 97.65625, "rotating_divisor": 5, "signal": items}


def _signal(**keys):
    item = {"id": "probe", "domain": "engine", "label": "Probe", "priority": "core",
            "coverage": "fixed", "current_fields": [], "sources": [0xFFFF11F4], "widths": [2],
            "dids": [], "evidence": "exact-code", "note": "Probe."}
    item.update(keys)
    return item


class SignalAdapterTest(unittest.TestCase):
    def test_a_signal_observes_the_meanings_of_its_sources(self):
        m = model()
        entity = m.entities[("signal", "engine_speed")]
        self.assertEqual({key: entity.props[key] for key in ("title", "coverage", "basis")},
                         {"title": "Engine speed", "coverage": "stock-can", "basis": "exact-code"})
        self.assertEqual(entity.refs["observes"], [SymbolKey("7mfk", "ram", 0xFFFF11F4)])
        self.assertEqual(m.meaning_of(entity.refs["observes"][0]).props["width"], 16)
        margins = m.entities[("signal", "knock_margin")]
        allocations = [f"can_telemetry.knock_margin_min_ch{index}" for index in range(1, 7)]
        self.assertEqual((margins.refs["observes"], margins.props["observes"]),
                         (allocations, allocations))
        self.assertNotIn(SymbolKey("7mfk", "ram", 0xFFFF5E10), m.symbols)

    def test_the_catalog_constants_are_keys_of_can_telemetry(self):
        props = model().entities[("feature", "can_telemetry")].props
        self.assertEqual({key: props[key] for key in signals.FEATURE_KEYS},
                         {"telemetry_profile": "tuning", "full_rate_hz": 97.65625,
                          "rotating_divisor": 5})

    def test_the_catalog_is_the_projection_of_the_signal_files(self):
        m = model()
        text = (repo.ROOT / signals.SIGNALS).read_text(encoding="utf-8")
        self.assertEqual(signals.render_catalog(signals.catalog_document(m)), text)
        self.assertEqual(signals.render_catalog(tomllib.loads(text)), text)
        self.assertNotIn(signals, adapters.ADAPTERS)
        self.assertEqual(m.entities[("signal", "engine_speed")].sources,
                         {"kb/signal/engine_speed.toml"})

    def test_the_catalog_derives_the_fields_and_the_dids_of_each_signal(self):
        document = signals.catalog_document(model())
        items = {item["id"]: item for item in document["signal"]}
        # The DIDs of each observed source in the order of the sources, and
        # the fields of each source in the order of the profile.
        self.assertEqual((items["ignition_control_state"]["sources"],
                          items["ignition_control_state"]["dids"]),
                         ([0xFFFF2023, 0xFFFF564C], [0x1162, 0x112D]))
        self.assertEqual(items["temperatures"]["current_fields"],
                         ["coolant_raw", "iat_raw", "fuel_temperature_did_source_raw",
                          "oil_temperature_did_source_raw"])
        self.assertEqual((items["knock_margin"]["current_fields"],
                          items["knock_margin"]["sources"], items["knock_margin"]["widths"]),
                         ([f"knock_margin_min_ch{index}_raw" for index in range(1, 7)],
                          list(range(0xFFFF5E10, 0xFFFF5E1C, 2)), [2] * 6))
        ranks = vocab.ENTITY_VOCABULARY["signal"]["priority"]
        order = [(item["domain"], ranks.index(item["priority"]), item["id"])
                 for item in document["signal"]]
        self.assertEqual(order, sorted(order))

    def test_a_source_without_a_catalog_form_refuses_the_projection(self):
        m = model()
        for item in (SymbolKey("jk00c", "ram", 0xFFFF11F4), SymbolKey("7mfk", "ram", 0xFFFF0001),
                     "can_telemetry.probe"):
            with self.subTest(source=item):
                entity = SimpleNamespace(key="probe/signal", refs={"observes": [item]})
                with self.assertRaises(KbError) as error:
                    signals.observed(m, entity, {})
                self.assertEqual(error.exception.code, 3)

    def test_stored_dids_that_differ_from_the_derived_ones_go_to_the_audit(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare_signals(b, _probe([_signal(dids=[0x1101]),
                                           _signal(id="exact", dids=[0x1106, 0x1101])]),
                                "probe.toml")
        b.stash["did_sources"] = {SymbolKey("7mfk", "ram", 0xFFFF11F4): {0x1101, 0x1106}}
        signals.relate(b, repo.ROOT)
        self.assertEqual([(issue.check, issue.subject, issue.message) for issue in b.issues],
                         [("audit", "signal.probe", "dids 1101 differ from the DIDs that "
                           "return an observed meaning: 1101, 1106")])

    def test_the_fields_of_a_signal_serve_it(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare(b, repo.ROOT)
        self.assertEqual(b.stash["signal_fields"]["knock_count_latched"], "knock_event_latches")

    def test_current_fields_that_differ_from_the_fields_of_a_signal_go_to_the_audit(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare_signals(b, _probe([_signal(current_fields=["probe_raw"]),
                                           _signal(id="exact", current_fields=["exact_raw"])]),
                                "probe.toml")
        for name in ("probe_raw", "exact_raw"):
            b.entity("field", name, "p.toml", refs={"signal": [Ref("exact/signal", "p.toml")]})
        signals.relate(b, repo.ROOT)
        self.assertEqual([(issue.check, issue.subject, issue.message) for issue in b.issues], [
            ("audit", "signal.probe", "current_fields ['probe_raw'] differ from the fields "
             "whose signal it is: []"),
            ("audit", "signal.exact", "current_fields ['exact_raw'] differ from the fields "
             "whose signal it is: ['exact_raw', 'probe_raw']")])

    def test_a_width_that_another_registry_states_differently_disagrees(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare_signals(b, _probe([_signal(), _signal(id="other", widths=[1])]),
                                "probe.toml")
        signals.relate(b, repo.ROOT)
        b.finish()
        self.assertEqual([(issue.check, issue.subject) for issue in b.issues],
                         [("audit", "7mfk-ffff11f4/ram")])

    def test_signal_keys_outside_their_vocabularies_fail_the_schema(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare_signals(b, _probe([_signal(priority="urgent"),
                                           _signal(id="short", widths=[])]), "probe.toml")
        signals.relate(b, repo.ROOT)
        m = b.finish()
        m.config = repo.config()
        self.assertEqual([(issue.subject, issue.message) for issue in checks.schema(m)],
                         [("signal.short", "sources and widths differ in length"),
                          ("probe/signal", "priority 'urgent'")])


def _telemetry(fields, contexts=()):
    """A telemetry profile of JK08A with the given stream fields and contexts."""
    return {"schema_version": 2, "rom": "JK08A", "mailbox": 26, "field": fields,
            "context": list(contexts)}


def _field(**keys):
    item = {"name": "probe_raw", "page": 0, "offset": 1, "width": 2, "source": 0xFFFF11F4,
            "profiles": ["tuning"], "kind": "ecu_ram", "signed": False, "scale": "raw / 4 V"}
    item.update(keys)
    return item


def _declare_telemetry(document, owners):
    """The builder after the declaration of the telemetry profile `document`,
    with `owners` as the fields that signals list."""
    b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
    b.stash["signal_fields"] = owners
    b.stash["feature_ram"] = [(0xFFFF5E00, 0xFFFF5F00, "can_telemetry")]
    regions = {"telemetry_state": [(0xFFFF5E00, 0xFFFF5E20, "can_telemetry")],
               "rom_configuration": [(0x000D4E00, 0x000D4E10, "can_telemetry")],
               "runtime_state": [(0xFFFF5D00, 0xFFFF5D3C, "map_switching")]}
    telemetry.declare_profile(b, document, regions, "probe.toml")
    return b


class TelemetryAdapterTest(unittest.TestCase):
    def test_reserved_wire_bytes_have_a_native_configuration_allocation(self):
        document = _telemetry([])
        document.update(padding=[{"page": 3, "offset": 4, "width": 3}],
                        padding_source=0x000D4E07)
        builder = _declare_telemetry(document, {})
        feature = builder.entities[("feature", "can_telemetry")]
        self.assertEqual(feature.props["padding"], document["padding"])
        self.assertEqual(feature.props["padding_source"], "can_telemetry.configuration_reserved")
        self.assertEqual(builder.targets[("can_telemetry", "7mfk")].props["allocations"],
                         {"configuration_reserved": {"address": "000d4e07", "width": 1}})

    def test_a_scale_splits_into_arithmetic_unit_level_and_prose(self):
        units = frozenset(repo.config()["vocab"]["unit"])
        cases = {
            "raw / 200 V": {"scale": "x/200", "unit": "V"},
            "110 - raw degBTDC": {"scale": "110-x", "unit": "degBTDC"},
            "candidate raw * 0.1 Nm signed request": {
                "scale": "x*0.1", "unit": "Nm", "scale_level": "candidate",
                "summary": "signed request"},
            "raw degBTDC": {"scale": "x", "unit": "degBTDC"},
            "raw / 16384 ratio": {"scale": "x/16384", "unit": "ratio"},
            "enumeration: 0 IDLE, 1 ACTIVE, 2 COOLDOWN": {"value": [
                {"value": 0, "name": "idle"}, {"value": 1, "name": "active"},
                {"value": 2, "name": "cooldown"}]},
            "bits: 0 CYLINDER_1, 5 CYLINDER_6": {"bit": [
                {"bit": 0, "name": "cylinder_1"}, {"bit": 5, "name": "cylinder_6"}]},
            "raw * 2 - 590 deg after intake TDC; raw * 2 degCA after the tooth": None,
            "candidate raw * 0.002 A/F ADJ factor": None,
            "raw software coordinate": None,
            "bits: 6 high_detonation": None,
            "raw * raw V": None,
            "Q14 factor": None,
        }
        for text, keys in cases.items():
            with self.subTest(scale=text):
                self.assertEqual(telemetry.parse_scale(text, units), keys)

    def test_an_ecu_ram_field_carries_its_source_meaning_and_serves_its_signal(self):
        m = model()
        field = m.entities[("field", "maf_b1_raw")]
        self.assertEqual((field.refs["source"], field.refs["signal"]),
                         ([SymbolKey("7mfk", "ram", 0xFFFF101C)], [("signal", "airflow_banks")]))
        self.assertEqual({key: field.props[key] for key in ("origin", "width", "page", "offset")},
                         {"origin": "ecu_ram", "width": 2, "page": 1, "offset": 1})
        self.assertNotIn("scale", field.props)
        meaning = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF101C))
        self.assertEqual((meaning.key, meaning.props["scale"], meaning.props["unit"]),
                         ("maf_b1/ram", "x/200", "V"))
        context = m.entities[("field", "stft_b1_raw")].props
        self.assertEqual((context["context"], context["position"]),
                         ("short_fuel_trim_cvtc_duty", 0))

    def test_the_unit_of_a_telemetry_scale_wins_over_the_ledger_units(self):
        m = model()
        # The ledger states `signed Q8 state` for the knock timing state and
        # `bitfield` for the fuel inhibit mask, whose file states no unit.
        cases = {0xFFFF1075: ("x*100/255", "percent"), 0xFFFF121A: ("x/256", "deg"),
                 0xFFFF22E0: (None, "bitfield")}
        for address, keys in cases.items():
            with self.subTest(address=f"{address:08x}"):
                props = m.meaning_of(SymbolKey("7mfk", "ram", address)).props
                self.assertEqual((props.get("scale"), props["unit"]), keys)

    def test_a_scale_that_the_parser_cannot_split_fails_the_fields_check(self):
        b = _declare_telemetry(_telemetry([_field(name="loose_raw", scale="Q14 factor")]),
                               {"loose_raw": "probe"})
        self.assertEqual([(issue.check, issue.subject, issue.message) for issue in b.issues],
                         [("fields", "field.loose_raw",
                           "scale 'Q14 factor' gives the source meaning no keys")])
        self.assertNotIn("scale", b.entities[("field", "loose_raw")].props)

    def test_a_host_count_view_declares_no_semantic_scale(self):
        b = _declare_telemetry(_telemetry([_field(name="count_raw", scale="raw count")]),
                               {"count_raw": "probe"})
        self.assertEqual(b.issues, [])
        source = b.entities[("field", "count_raw")].refs["source"][0]
        meaning = b.finish().meaning_of(source)
        self.assertFalse({"unit", "scale", "to_raw", "scale_level"} & meaning.props.keys())
        self.assertEqual(b.entities[("field", "count_raw")].props["scale"], "raw count")

    def test_a_field_carries_its_presentation_and_another_key_fails_the_schema(self):
        presentation = {"label": "Probe", "digits": 2, "group": "Probe",
                        "feed": {"key": "probe", "name": "VQ Probe", "format": "0.00",
                                 "minimum": 0, "maximum": 5, "step": 1}}
        b = _declare_telemetry(_telemetry([
            _field(name="shown_raw", dashboard=presentation),
            _field(name="plain_raw", offset=3),
            _field(name="loose_raw", offset=5, display={"label": "Loose"})]),
            {"shown_raw": "probe", "plain_raw": "probe"})
        self.assertEqual([(issue.check, issue.subject, issue.message) for issue in b.issues],
                         [("schema", "field.loose_raw", "missing []; unknown ['display']")])
        self.assertEqual(b.entities[("field", "shown_raw")].props["dashboard"], presentation)
        self.assertNotIn("dashboard", b.entities[("field", "plain_raw")].props)

    def test_the_fields_of_the_model_pass_the_fields_and_widths_checks(self):
        m = model()
        self.assertEqual((checks.fields(m), checks.widths(m)), ([], []))

    def test_another_field_names_an_allocation_of_the_feature_that_owns_its_source(self):
        m = model()
        cases = {"tick16": ("can_telemetry", "tick16", "ffff5e08", 2),
                 "protocol_version": ("can_telemetry", "protocol_version", "000d4e02", 1),
                 "knock_margin_min_ch1_raw": ("can_telemetry", "knock_margin_min_ch1",
                                              "ffff5e10", 2),
                 "active_map_index": ("map_switching", "active_map_index", "ffff5d00", 1),
                 "rolling_launch_phase": ("rolling_launch", "rolling_launch_phase",
                                          "ffff5d40", 1)}
        for name, (feature, allocation, address, width) in cases.items():
            with self.subTest(field=name):
                field = m.entities[("field", name)]
                self.assertEqual(field.props["source"], f"{feature}.{allocation}")
                self.assertNotIn("source", field.refs)
                self.assertEqual(m.targets[(feature, "7mfk")].props["allocations"][allocation],
                                 {"address": address, "width": width})
        self.assertEqual(m.entities[("field", "rolling_launch_phase")].props["scale"],
                         "enumeration: 0 IDLE, 1 ACTIVE, 2 COOLDOWN")

    def test_the_wire_constants_are_keys_of_the_feature_and_the_addresses_of_its_target(self):
        m = model()
        document = tomllib.loads((repo.ROOT / telemetry.PROFILE).read_text(encoding="utf-8"))
        feature = m.entities[("feature", "can_telemetry")].props
        self.assertEqual({name: feature[name] for name in telemetry.WIRE_KEYS},
                         {name: document[name] for name in telemetry.WIRE_KEYS})
        self.assertEqual(feature["profiles"], document["profile"])
        self.assertEqual([context["name"] for context in feature["contexts"]],
                         [context["name"] for context in document["context"]])
        target = m.targets[("can_telemetry", "7mfk")].props
        self.assertEqual({name: int(target[name], 16) for name in telemetry.ADDRESS_KEYS},
                         {name: document[name] for name in telemetry.ADDRESS_KEYS})
        self.assertEqual(target["mailbox_index"], document["mailbox"])
        fields = [item["name"] for item in document["field"]] + [
            item["name"] for context in document["context"] for item in context["field"]]
        self.assertEqual(sorted(slug for kind, slug in m.entities if kind == "field"),
                         sorted(fields))

    def test_a_source_outside_its_region_and_an_unlisted_ecu_ram_field_fail_the_fields(self):
        b = _declare_telemetry(_telemetry([
            _field(name="listed_raw"),
            _field(name="unlisted_raw", offset=3),
            _field(name="rom_raw", source=0x00001000),
            _field(name="feature_raw", source=0xFFFF5E40),
            _field(name="state", kind="telemetry_state", source=0xFFFF5E30),
            _field(name="mode", kind="runtime_state", source=0xFFFF5D3B),
            _field(name="map", kind="runtime_state", source=0xFFFF5D00, width=1),
            _field(name="other", kind="host_state"),
            {"name": "short", "width": 1}]),
            {"listed_raw": "probe", "rom_raw": "probe", "feature_raw": "probe",
             "absent_raw": "probe"})
        self.assertEqual(sorted((issue.check, issue.subject) for issue in b.issues), [
            ("fields", "field.feature_raw"), ("fields", "field.mode"),
            ("fields", "field.rom_raw"), ("fields", "field.state"),
            ("fields", "field.unlisted_raw"), ("references", "signal.probe"),
            ("schema", "field.other"), ("schema", "field.short")])
        self.assertEqual(b.targets[("map_switching", "7mfk")].props["allocations"],
                         {"map": {"address": "ffff5d00", "width": 1}})
        self.assertEqual(sorted(slug for kind, slug in b.entities if kind == "field"),
                         ["listed_raw", "map", "unlisted_raw"])

    def test_the_profile_is_its_canonical_rendering(self):
        text = (repo.ROOT / telemetry.PROFILE).read_text(encoding="utf-8")
        self.assertEqual(telemetry.render_profile(tomllib.loads(text)), text)

    def test_the_profile_is_the_projection_of_the_files(self):
        m = model()
        self.assertEqual(telemetry.render_profile(telemetry.profile_document(m)),
                         (repo.ROOT / telemetry.PROFILE).read_text(encoding="utf-8"))
        self.assertNotIn(telemetry, adapters.ADAPTERS)
        self.assertEqual(m.entities[("field", "maf_b1_raw")].sources,
                         {"kb/field/maf_b1_raw.toml"})
        self.assertEqual(sorted(m.entities[("feature", "can_telemetry")].refs["requires"]),
                         sorted(key for key in m.entities if key[0] == "field"))

    def test_a_scale_renders_from_the_keys_of_its_meaning(self):
        cases = [({"scale": "x/200", "unit": "V"}, "raw / 200 V"),
                 ({"scale": "110-x", "unit": "degBTDC"}, "110 - raw degBTDC"),
                 ({"scale": "x*0.1", "unit": "Nm", "scale_level": "candidate"},
                  "candidate raw * 0.1 Nm"),
                 ({"scale": "x", "unit": "degBTDC"}, "raw degBTDC"),
                 ({"value": [{"value": 0, "name": "idle"}, {"value": 1, "name": "active"}]},
                  "enumeration: 0 IDLE, 1 ACTIVE"),
                 ({"bit": [{"bit": 6, "name": "high_detonation"}]}, "bits: 6 HIGH_DETONATION"),
                 ({"scale": "x*(1/4)", "unit": "V"}, None),
                 ({"unit": "V"}, None)]
        units = frozenset(repo.config()["vocab"]["unit"])
        for props, text in cases:
            with self.subTest(props=props):
                self.assertEqual(telemetry.scale_text(props), text)
                if text is not None:
                    self.assertEqual(telemetry.parse_scale(text, units), props)
        # The named bits render by number with their names alone.
        bits = {"bit": [{"bit": 5, "name": "cylinder_6", "level": "candidate"},
                        {"bit": 0, "name": "cylinder_1", "summary": "Channel 0"}]}
        self.assertEqual(telemetry.scale_text(bits), "bits: 0 CYLINDER_1, 5 CYLINDER_6")

    def test_an_unscaled_ecu_source_has_only_a_host_count_view(self):
        key = SymbolKey("7mfk", "ram", 0xFFFF18CC)
        entity = SimpleNamespace(props={"origin": "ecu_ram"}, refs={"source": (key,)})
        for props, expected in (({}, "raw count"),
                                ({"unit": "Nm"}, None),
                                ({"scale": "x"}, None),
                                ({"scale": "x*(1/4)", "unit": "V"}, None)):
            with self.subTest(props=props):
                held = dict(props)
                meaning = SimpleNamespace(props=props)
                source_model = SimpleNamespace(meaning_of=lambda source: meaning)
                self.assertEqual(telemetry._source(source_model, entity, {}),
                                 {"source": key.address, "scale": expected})
                self.assertEqual(props, held)
                self.assertNotIn("scale_level", props)

    def test_an_explicit_count_view_keeps_the_native_unit_without_a_conversion(self):
        key = SymbolKey("7mfk", "ram", 0xFFFF23C2)
        entity = SimpleNamespace(props={"origin": "ecu_ram", "scale": "raw count"},
                                 refs={"source": (key,)})
        native = {"unit": "Q8 state"}
        source_model = SimpleNamespace(meaning_of=lambda source: SimpleNamespace(props=native))
        self.assertEqual(telemetry._source(source_model, entity, {}),
                         {"source": key.address, "scale": "raw count"})
        self.assertEqual(native, {"unit": "Q8 state"})

    def test_the_projection_changes_only_the_scales_of_ecu_ram_fields(self):
        text = (repo.ROOT / telemetry.PROFILE).read_text(encoding="utf-8")
        document = tomllib.loads(text)
        self.assertEqual(telemetry.scale_changes(text, document), [])
        scaled = copy.deepcopy(document)
        item = next(item for item in scaled["field"] if item["kind"] == "ecu_ram")
        old, item["scale"] = item["scale"], "raw / 2 V"
        self.assertEqual(telemetry.scale_changes(text, scaled),
                         [(item["name"], old, "raw / 2 V")])
        other = copy.deepcopy(document)
        next(item for item in other["field"] if item["kind"] != "ecu_ram")["scale"] = "raw"
        moved = copy.deepcopy(document)
        moved["field"][0]["offset"] += 1
        for changed, form in ((other, text), (moved, text), (document, text + "\n")):
            with self.subTest(canonical=form == text):
                with self.assertRaises(KbError) as error:
                    telemetry.scale_changes(form, changed)
                self.assertEqual(error.exception.code, 3)


def _overrides():
    return tomllib.loads((repo.ROOT / overrides.OVERRIDES).read_text(encoding="utf-8"))


class OverridesAdapterTest(unittest.TestCase):
    def test_a_table_takes_its_editor_and_the_masked_views_of_its_source(self):
        document = _overrides()
        editor = model().meaning_of(SymbolKey("7mfk", "tbl", 0x0000991A)).props["editor"]
        views = [{overrides.VIEW_NAMES.get(key, key): value for key, value in item.items()
                  if key != "source"}
                 for item in document["masked_view"] if item["source"] == "0000991a"]
        self.assertEqual(editor, {**document["table"]["0000991a"], "view": views})
        self.assertEqual([(view["unit"], view["scale"], view["to_raw"]) for view in views],
                         [("Enable flag (0: Off | 1: On)", "x", "x")])

    def test_a_static_axis_operand_names_the_meaning_it_labels(self):
        m = model()
        editor = m.meaning_of(SymbolKey("7mfk", "tbl", 0x000126E4)).props["editor"]
        self.assertEqual(editor["static_axis_operand"], SymbolKey("7mfk", "ram", 0xFFFF106F))
        axis = m.meaning_of(SymbolKey("7mfk", "axis", 0x00011BFB)).props["editor"]
        self.assertEqual(axis, _overrides()["axis"]["00011bfb"])

    def test_a_logger_parameter_takes_units_as_unit(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1980))
        self.assertEqual(meaning.props["logparam"],
                         {"id": "X_VQ_QH0_Flow_Potential", "unit": "QH0 Flow Potential [count]",
                          "scale": "x"})

    def test_the_jk08a_entry_carries_the_keys_of_a_projection_entry(self):
        m = model()
        entry = m.targets[("definitions", "7mfk")].props["images"]["JK08A"]
        self.assertEqual((entry["rom"]["xmlid"], entry["map_switching"], entry["rolling_launch"]),
                         ("JK08A", True, True))
        self.assertEqual(entry["switch"], {"developer_immobilizer": "00008725",
                                           "can_telemetry_startup": "000d4e03",
                                           "cruise_control_switch": "00008b28"})
        self.assertEqual([(item["type"], item["start"], item["end"], item.get("skiploc"))
                          for item in entry["checksums"]],
                         [("alt", "0002040c", "0002259c", None),
                          ("alt2", "00008200", "00100000", "00020000")])
        self.assertTrue(entry["note"].startswith("Analysis and method"))
        self.assertIn("rom-images/roms.csv", entry["basis"])
        self.assertLessEqual(set(entry) - {"rom", "checksums", "note", "basis"},
                             set(definitions.IMAGE_KEYS) | {"switch"})
        feature = m.entities[("feature", "definitions")].props
        self.assertEqual(feature["default_emit"], True)
        self.assertEqual(sorted(feature["switches"]),
                         sorted(overrides.switch_names(repo.ROOT).values()))
        self.assertNotIn("storageaddress", feature["switches"]["developer_immobilizer"])

    def test_an_address_without_a_symbol_and_an_unknown_key_fail_their_checks(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
        b.symbol("7mfk", "tbl", 0x00009000, "probe")
        document = {
            "table": {"00009000": {"name": "Probe", "shade": 1}, "00009100": {"name": "Gap"}},
            "masked_view": [{"source": "00009000", "name": "View", "units": "flag",
                             "colour": 1}],
            "logparam": {"ffff0000": {"id": "X_Probe", "units": "u"}},
            "switch": [{"name": "Unknown Switch", "storageaddress": "0x9000"}],
            "palette": {}}
        overrides.declare_overrides(b, document, overrides.switch_names(repo.ROOT), "probe.toml")
        overrides.relate(b, repo.ROOT)
        self.assertEqual(sorted((issue.check, issue.subject, issue.message) for issue in b.issues),
                         [("references", "logparam.ffff0000",
                           "no ram or reg symbol of 7mfk at ffff0000"),
                          ("references", "table.00009100", "no tbl symbol of 7mfk at 00009100"),
                          ("schema", "masked_view.View", "unknown key colour"),
                          ("schema", "palette", "unknown key"),
                          ("schema", "switch.Unknown Switch",
                           f"no slug of SWITCH_NAMES in {overrides.PROJECTIONS}"),
                          ("schema", "table.00009000", "unknown key shade")])

    def test_the_registry_entry_keeps_the_keys_of_the_files_that_it_lacks(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {}, repo.config())
        target = b.target("definitions", "7mfk", "kb/feature/definitions.toml",
                          status="supported")
        target.props["images"] = {"JK08A": {"basis": "Measured.", "map_switching": False}}
        document = {"map_switching": {"enabled": True}, "rom": {"xmlid": "JK08A"}}
        overrides.declare_overrides(b, document, {}, "probe.toml")
        self.assertEqual(target.props["images"]["JK08A"],
                         {"basis": "Measured.", "map_switching": True, "rom": {"xmlid": "JK08A"}})


class PresentationProjectionTest(unittest.TestCase):
    def test_the_projection_renders_the_file(self):
        text = (repo.ROOT / overrides.OVERRIDES).read_text(encoding="utf-8")
        rendered = overrides.render_presentation(overrides.presentation_document(model()))
        self.assertEqual(rendered, text)
        self.assertEqual(overrides.dropped(text, rendered), ([], []))

    def test_switches_render_by_order_and_tables_by_the_order_of_the_editor(self):
        m = model()
        document = overrides.presentation_document(m)
        switches = m.entities[("feature", "definitions")].props["switches"]
        self.assertEqual([item["name"] for item in document["switch"]],
                         [switches[slug]["name"] for slug in
                          sorted(switches, key=lambda slug: switches[slug]["order"])])
        self.assertTrue(all("order" not in item for item in document["switch"]))
        places = [(item.get("order", overrides.LAST), address)
                  for address, item in document["table"].items()]
        self.assertEqual(places, sorted(places))
        self.assertEqual(document["table"]["000126e4"]["static_axis_operand"], "ffff106f")

    def test_a_note_renders_as_its_paragraph_wrapped_at_79_columns(self):
        m = model()
        note = m.targets[("definitions", "7mfk")].props["images"]["JK08A"]["note"]
        text = overrides.presentation_document(m)["rom"]["comment"]["text"]
        self.assertTrue(text.endswith("\n"))
        self.assertLessEqual(max(map(len, text.splitlines())), overrides.NOTE_WIDTH)
        self.assertEqual(" ".join(text.split()), note)

    def test_the_conversion_lists_dropped_comments_and_rewrapped_notes(self):
        text = (repo.ROOT / overrides.OVERRIDES).read_text(encoding="utf-8")
        note = tomllib.loads(text)["rom"]["comment"]["text"]
        narrow = textwrap.fill(" ".join(note.split()), 60, break_on_hyphens=False) + "\n"
        held = text.replace("[presentation]\n", "# A comment of the file.\n[presentation]\n", 1)
        held = held.replace(note, narrow, 1)
        comments, wrapped = overrides.dropped(held, text)
        self.assertEqual([line for _, line in comments], ["# A comment of the file."])
        self.assertEqual(wrapped, [("rom.comment.text", narrow, note)])
        changed = text.replace("default_emit = true", "default_emit = false", 1)
        self.assertNotEqual(changed, text)
        with self.assertRaises(KbError) as error:
            overrides.dropped(changed, text)
        self.assertEqual(error.exception.code, 3)


def _architecture():
    return tomllib.loads((repo.ROOT / architecture.ARCHITECTURE).read_text(encoding="utf-8"))


class ArchitectureAdapterTest(unittest.TestCase):
    def test_stages_blocks_and_endpoints_carry_their_keys_and_references(self):
        m = model()
        stage = m.entities[("stage", "estimation")]
        self.assertEqual({key: stage.props[key] for key in ("title", "lane", "order")},
                         {"title": "Engine state", "lane": "flow", "order": 2})
        block = m.entities[("block", "engine_speed")]
        self.assertEqual((block.refs["stage"], block.props["home"]),
                         ([("stage", "estimation")], "7mfk"))
        endpoint = m.entities[("endpoint", "crank_sensor")]
        self.assertEqual(endpoint.refs, {"block": [("block", "crank_cam")],
                                         "registers": [SymbolKey("7mfk", "reg", 0xFFFFF434)],
                                         "functions": [SymbolKey("7mfk", "fn", 0x00028EA2)]})

    def test_the_lists_of_a_block_become_the_block_key_of_their_meanings(self):
        m = model()
        for item in _architecture()["block"]:
            name = f"{architecture.slug(item['id'])}/block"
            for field, kinds in architecture.BLOCK_LISTS.items():
                for text in item.get(field, ()):
                    meaning = next(m.meaning_of(SymbolKey("7mfk", kind, int(text, 16)))
                                   for kind in kinds
                                   if SymbolKey("7mfk", kind, int(text, 16)) in m.symbols)
                    self.assertEqual(meaning.props["block"], name, text)

    def test_a_chain_keeps_its_steps_in_order_with_their_references(self):
        m = model()
        chain = m.entities[("chain", "engine_speed")]
        source = next(item for item in _architecture()["chain"] if item["id"] == "engine-speed")
        self.assertEqual(len(chain.steps), len(source["step"]))
        self.assertEqual(chain.refs["output"], [SymbolKey("7mfk", "ram", 0xFFFF1196)])
        step = chain.steps[3]
        self.assertEqual({key: step[key] for key in ("from", "to", "effect", "sign", "via")},
                         {"from": SymbolKey("7mfk", "ram", 0xFFFF22BC),
                          "to": SymbolKey("7mfk", "ram", 0xFFFF114A), "effect": "converts",
                          "sign": "negative", "via": [SymbolKey("7mfk", "fn", 0x0003DEEC)]})
        self.assertEqual(step["note"], source["step"][3]["note"])
        self.assertRegex(step["note"], r"\Affff114a\s*=\s*floor\(0xA2C2\s*/\s*ffff22bc\)\Z")

    def test_a_prefix_selects_the_kind_and_a_reference_without_a_symbol_fails(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {"7mfk": {0x00030000}},
                    {"7mfk": (0x8200, 0x20000)}, repo.config())
        for kind, address in (("tbl", 0x9000), ("axis", 0x9000), ("fn", 0x30000)):
            b.symbol("7mfk", kind, address, "probe")
        stage = {"id": "s", "name": "S", "lane": "flow", "summary": "Stage."}
        block = {"id": "b-one", "name": "B", "stage": "s", "summary": "Block.",
                 "functions": ["00030000", "00031000"]}
        steps = [{"from": "00009000", "to": "ffff0010", "effect": "looks-up", "sign": "none",
                  "via": ["00030000"], "note": "x"},
                 {"from": "map:00009000", "to": "ffff0010", "effect": "guesses", "sign": "none",
                  "via": ["00009000"]}]
        chain = {"id": "c", "name": "C", "summary": "Chain.", "quantity": "Q",
                 "output": "axis:00009000", "step": steps}
        architecture.relate_architecture(b, {
            "schema_version": 1, "rom": "JK08A", "stage": [stage],
            "block": [block, {**block, "id": "b-two", "stage": "gone"}],
            "chain": [chain]}, "probe.toml")
        entity = b.entities[("chain", "c")]
        self.assertEqual((entity.refs["output"], entity.steps[0]["from"], entity.steps[0]["to"]),
                         ([SymbolKey("7mfk", "axis", 0x9000)], SymbolKey("7mfk", "tbl", 0x9000),
                          SymbolKey("7mfk", "ram", 0xFFFF0010)))
        self.assertEqual(len(entity.steps), 1)
        b.finish()
        self.assertEqual(sorted((issue.check, issue.subject, issue.message) for issue in b.issues),
                         [("audit", "7mfk-00030000/fn",
                           "block = 'b_two/block' disagrees with 'b_one/block'"),
                          ("references", "block.b-one.functions",
                           "no fn symbol of 7mfk at 00031000"),
                          ("references", "block.b-two", "stage 'gone' is no stage"),
                          ("references", "block.b-two.functions",
                           "no fn symbol of 7mfk at 00031000"),
                          ("references", "chain.c.step.2.via",
                           "00009000 admits no fn symbol of 7mfk"),
                          ("schema", "chain.c.step.2", "effect 'guesses'")])


@pytest.mark.slow
class StageTwoChecksTest(unittest.TestCase):
    def test_the_model_checks_pass(self):
        m = model()
        for name, check in checks.CHECKS.items():
            with self.subTest(check=name):
                self.assertEqual(check(m), [])

    def test_every_symbol_has_a_name_and_names_are_stable(self):
        first, second = compile.build(), compile.build()
        self.assertEqual(names.missing(first, first.names), [])
        by_key = lambda m: {key: symbol.name for key, symbol in m.symbols.items()}
        self.assertEqual(by_key(first), by_key(second))
        self.assertTrue(all(by_key(first).values()))


if __name__ == "__main__":
    unittest.main()
