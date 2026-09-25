import csv
import unittest

from kb import checks, compile, names, repo
from kb.adapters import ledgers
from kb.model import SymbolKey


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
        self.assertEqual((meaning.key, meaning.tier), ("periodic_tick_isr/fn", "curated"))

    def test_a_symbol_key_wins_over_a_curated_name(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x20DFE))
        self.assertEqual((meaning.key, meaning.tier), ("coherent_snapshot/fn", "symbol_key"))
        self.assertIn(("periodic_snapshot_dispatch", "curated", "tools/ghidra/symbols/7mfk.csv"),
                      meaning.other_names)
        self.assertEqual(model().meaning_of(SymbolKey("1nd", "fn", 0x11363C)).name, "hcan1_init")


class ProfileAdapterTest(unittest.TestCase):
    def test_a_telemetry_source_joins_the_meaning_of_its_field(self):
        meaning = model().meaning_of(SymbolKey("jk00d", "ram", 0xFFFF1034))
        self.assertEqual((meaning.key, meaning.tier), ("normalized_load/ram", "field"))
        self.assertEqual(meaning.symbols["7mfk"].address, 0xFFFF102C)
        self.assertEqual({layout: status.state for layout, status in meaning.statuses.items()},
                         {"1nd": "unresolved", "1me3b": "unresolved", "jk78c": "unresolved"})

    def test_an_unavailable_field_states_absent_or_unresolved_by_its_evidence(self):
        knock = model().meaning_of(SymbolKey("7mfk", "ram", 0xFFFF121A))
        self.assertEqual(knock.statuses["1nd"].state, "absent")
        self.assertIn("unavailable", {key for key in
                                      model().targets[("can_telemetry", "1nd")].props})
        self.assertIn("knock_timing_state_raw",
                      model().targets[("can_telemetry", "1nd")].props["unavailable"])

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
                self.assertEqual((meaning.name, meaning.tier), (name, "hook"))
        # The 8MFK key exhaust_cvtc_target_lookup names another word than the
        # canonical key of the same spelling.
        own = m.meaning_of(SymbolKey("jk00d", "hook", 0x000C5B94))
        self.assertNotEqual(own.tier, "hook")
        self.assertIs(own, m.meaning_of(SymbolKey("jk00c", "hook", 0x000C5B58)))

    def test_a_hook_word_links_to_the_meaning_at_its_stock_value(self):
        m = model()
        hook = m.meaning_of(SymbolKey("1nd", "hook", 0x00022184))
        [link] = [link for link in hook.links if link.type == "target"
                  and "1nd" in link.to.symbols]
        self.assertEqual(link.to.symbols["1nd"].address, 0x0006D948)
        self.assertEqual(link.to.key, "knock_function/fn")

    def test_a_join_that_would_hold_two_symbols_of_a_layout_is_refused(self):
        m = model()
        refused = {(issue.subject, issue.path.split(":")[0]) for issue in m.issues
                   if issue.check == "audit" and "refused join" in issue.message}
        self.assertIn(("1nd-fffe92e4/ram", "patches/1nd-runtime-correspondence.csv"), refused)
        mask = m.meaning_of(SymbolKey("1nd", "ram", 0xFFFE92E4))
        self.assertEqual(mask.symbols["7mfk"].address, 0xFFFF22E0)
        self.assertNotIn("1nd", m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF2497)).symbols)

    def test_an_unsupported_map_row_gives_way_to_a_target_specific_surface(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "tbl", 0x00009A1A))
        self.assertEqual(meaning.symbols["1nd"].address, 0x00009980)
        self.assertNotIn("1nd", meaning.statuses)
        self.assertEqual(meaning.statuses["1me3b"].state, "absent")

    def test_feature_targets_carry_hooks_allocations_and_status(self):
        m = model()
        rolling = m.targets[("rolling_launch", "jk00d")]
        self.assertEqual(rolling.status, "supported")
        self.assertIn("displaced_periodic_task", rolling.props["hooks"])
        self.assertTrue(rolling.props["allocations"])
        self.assertEqual(rolling.props["allocations"]["flags"]["address"], "ffff6042")
        runtime = m.targets[("runtime", "1nd")]
        self.assertEqual(runtime.props["rom_delta"], 0x60000)
        self.assertEqual(runtime.props["free_ram_start"], "ffff0c00")
        self.assertIn(("feature", "map_switching"), m.entities)


class DefinitionAdapterTest(unittest.TestCase):
    def test_a_table_and_axis_operand_gives_a_symbol_of_each_kind(self):
        m = model()
        for kind in ("tbl", "axis"):
            meaning = m.meaning_of(SymbolKey("7mfk", kind, 0x0000E98E))
            self.assertIs(meaning, m.meaning_of(SymbolKey("jk00d", kind, 0x000104A2)))
            self.assertIs(meaning, m.meaning_of(SymbolKey("jk00c", kind, 0x00010492)))
        self.assertIsNot(m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000E98E)),
                         m.meaning_of(SymbolKey("7mfk", "axis", 0x0000E98E)))

    def test_function_kinds_type_the_homology_evidence(self):
        m = model()
        symbol = m.symbols[SymbolKey("jk00d", "tbl", 0x000104A2)]
        found = {(item["kind"], item["value"]) for item in symbol.evidence
                 if item.get("supports") == "homology"}
        self.assertEqual(found, {("byte-identical", "exact-bytes"),
                                 ("function-match", "normalized-shape")})
        self.assertTrue(all(item["to"] == SymbolKey("7mfk", "tbl", 0x0000E98E)
                            for item in symbol.evidence if item.get("supports") == "homology"))

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
        self.assertEqual(m.meaning_of(SymbolKey("7mfk", "tbl", 0x0000A9AA)).statuses["1nd"].state,
                         "unresolved")
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
                          "can_telemetry_startup": "00134e03"})
        self.assertEqual([item["variant"] for item in target.props["variants"]],
                         ["default", "default"])
        self.assertEqual([issue for issue in m.issues if issue.check == "schema"], [])


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
