from collections import defaultdict
import copy
import csv
import re
import tomllib
from types import SimpleNamespace
import unittest

from kb import adapters, checks, compile, match, names, repo, vocab
from kb.adapters import (architecture, definitions, interp, ledgers, native, overrides,
                         profiles, signals, telemetry)
from kb.model import Builder, Ref, SymbolKey
from kb.repo import KbError


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
        self.assertEqual((meaning.key, meaning.tier), ("periodic_tick_isr/fn", "curated"))

    def test_the_file_of_a_meaning_wins_over_a_curated_name(self):
        # The conversion of the address profiles named the file by the symbol
        # key, which wins over the curated name.
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x20DFE))
        self.assertEqual((meaning.key, meaning.tier), ("coherent_snapshot/fn", "file"))
        self.assertIn(("periodic_snapshot_dispatch", "curated", "tools/ghidra/symbols/7mfk.csv"),
                      meaning.other_names)
        self.assertEqual(model().meaning_of(SymbolKey("1nd", "fn", 0x11363C)).name, "hcan1_init")


class ProfileAdapterTest(unittest.TestCase):
    def test_a_telemetry_source_joins_the_meaning_of_its_field(self):
        meaning = model().meaning_of(SymbolKey("jk00d", "ram", 0xFFFF1034))
        self.assertEqual((meaning.key, meaning.tier), ("normalized_load/ram", "file"))
        self.assertEqual(meaning.symbols["7mfk"].address, 0xFFFF102C)
        self.assertEqual({layout: status.state for layout, status in meaning.statuses.items()},
                         {"1nd": "unresolved", "1me3b": "unresolved"})
        self.assertEqual(meaning.symbols["jk78c"].address, 0xFFFF1032)

    def test_an_unavailable_field_states_absent_or_unresolved_by_its_evidence(self):
        m = model()
        knock = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF121A))
        self.assertEqual({layout: status.state for layout, status in knock.statuses.items()},
                         {"1me3b": "absent"})
        self.assertEqual((knock.symbols["jk78c"].address, knock.symbols["1nd"].address),
                         (0xFFFF1204, 0xFFFE8214))
        flow = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1170))
        self.assertEqual({layout: status.state for layout, status in flow.statuses.items()},
                         {"1nd": "unresolved", "1me3b": "unresolved"})
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
        rolling = m.targets[("rolling_launch", "1nd")].props
        role = rolling["roles"]["fuel_inhibit"]
        self.assertEqual(role["symbol"], SymbolKey("1nd", "ram", 0xFFFE94BA))
        self.assertIn("the arm and the active cut", role["note"])
        self.assertEqual(m.meaning_of(role["symbol"]).key, "rev_fuel_cut_state/ram")
        self.assertEqual(rolling["symbols"]["fuel_inhibit_mask"],
                         SymbolKey("1nd", "ram", 0xFFFE92E4))
        state = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF2497))
        self.assertEqual((state.key, sorted(state.symbols)),
                         ("fuel_inhibit/ram", ["7mfk", "jk00c", "jk00d"]))
        config = m.targets[("map_switching", "jk78c")].props["roles"]
        self.assertEqual(config["ignition_coordinator_config_byte"]["symbol"],
                         SymbolKey("jk78c", "tbl", 0x8965))
        # Where no mapped row places its address, the key joins its own meaning.
        byte = m.meaning_of(SymbolKey("1me3b", "tbl", 0x8A7D))
        self.assertEqual((byte.key, sorted(byte.symbols)),
                         ("ignition_coordinator_config_byte/tbl", ["1me3b"]))
        self.assertFalse([issue for issue in m.issues if "refused join" in issue.message])

    def test_every_layout_writes_the_data_register_of_mailbox_26(self):
        data = model().meaning_of(SymbolKey("7mfk", "reg", 0xFFFFDC48))
        self.assertEqual((data.key, sorted(data.symbols)),
                         ("mailbox_data/reg", ["1me3b", "1nd", "7mfk", "jk00c", "jk00d", "jk78c"]))

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

    def test_a_target_specific_telemetry_row_fills_the_role_of_its_field(self):
        m = model()
        target = m.targets[("can_telemetry", "jk78c")].props
        role = target["roles"]["alpha_n_flow_raw"]
        self.assertEqual(role["symbol"], SymbolKey("jk78c", "ram", 0xFFFF22F8))
        self.assertIn("column of the target Fuel Compensation surfaces", role["note"])
        self.assertEqual(sorted(m.meaning_of(role["symbol"]).symbols), ["jk78c"])
        self.assertNotIn("alpha_n_flow_raw", target.get("symbols", {}))
        # The source meaning of the field keeps the homolog of its producer.
        flow = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1170))
        self.assertEqual((flow.key, flow.symbols["jk78c"].address),
                         ("alpha_n_flow/ram", 0xFFFF115C))

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
        self.assertEqual({issue.path.count(";")
                          for issue in checks.audit(model(), ("untyped",))["untyped"]}, {0})

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
        rolling = m.targets[("rolling_launch", "jk00d")]
        self.assertEqual(rolling.status, "supported")
        self.assertIn("displaced_periodic_task", rolling.props["hooks"])
        self.assertTrue(rolling.props["allocations"])
        self.assertEqual(rolling.props["allocations"]["flags"]["address"], "ffff6042")
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
        word = SymbolKey("1nd", "hook", 0x00115490)
        self.assertEqual(profiles.row_item(m.symbols[word], "the word")[1]["note"],
                         "Dispatcher literal resolves the exact 0x551 serializer")
        entry = m.targets[("rolling_launch", "1nd")].props["hooks"]["feedback_arbitration"]
        self.assertEqual((entry["hook"], entry["note"]),
                         (word, "Rolling feedback chains from the Map Switching serializer wrapper"))


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
                         (definitions.HOMOLOGOUS, "call-ordinal", "7mfk:000734d4"))
        self.assertIsNone(match.verify(m, symbol, item))

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
        self.assertEqual(sorted(files), [f"defs/{name}" for name in (
            "1ME3B.interp.csv", "1ND0A.interp.csv", "JK00D.interp.csv",
            "JK08A-1ND0A.interp-correspondence.csv", "JK08A-JK00D.interp-correspondence.csv",
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
                         {"jk78c": 0x9FBA, "1nd": 0xA2C0, "1me3b": 0xA1F4})
        self.assertIn("fuel_compensation_main_alternate",
                      {name for name, _, _ in meaning.other_names})
        self.assertEqual((meaning.props["cols"], meaning.props["rows"], meaning.props["storage"]),
                         (16, 16, "uint8"))
        self.assertEqual(meaning.props["editor"]["order"], 21)

    def test_a_layout_that_differs_keeps_its_keys_as_overrides(self):
        meaning = model().meaning_of(SymbolKey("jk78c", "axis", 0x000160CA))
        self.assertEqual((meaning.key, meaning.props["quantity"], meaning.props["unit"]),
                         ("vvel_duration_hot_intake_idle_axis_x/axis", "rpm", "RPM"))
        own = meaning.symbols["1nd"].props
        self.assertEqual((own["quantity"], own["unit"], own["scale"], own["editor"]["name"]),
                         ("temp", "degC", "x-50", "Coolant Temperature [degC]"))
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
        self.assertEqual(accessor.evidence,
                         [{"kind": "l0", "supports": "identity", "at": "jk78c:00040e00"}])

    def test_an_axis_link_takes_evidence_at_the_first_census_call_that_passes_both(self):
        table = model().meaning_of(SymbolKey("jk78c", "tbl", 0x00009FBA))
        for link in table.links:
            if link.type == "axis":
                with self.subTest(slot=link.slot):
                    self.assertEqual(sorted(item["at"] for item in link.evidence),
                                     ["1me3b:00033cec", "1nd:00030f7c", "jk78c:0002fd32"])

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
                         {"jk78c": 0x16A64, "1nd": 0x17072, "1me3b": 0x17106})
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
                         ["1me3b:0007b1bc", "1nd:00076aee", "jk78c:0006aeea"])

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
    def test_a_scale_splits_into_arithmetic_unit_level_and_prose(self):
        units = frozenset(repo.config()["vocab"]["unit"])
        cases = {
            "raw / 200 V": {"scale": "x/200", "unit": "V"},
            "110 - raw degBTDC": {"scale": "110-x", "unit": "degBTDC"},
            "candidate raw * 0.1 Nm signed request": {
                "scale": "x*0.1", "unit": "Nm", "scale_level": "candidate",
                "summary": "signed request"},
            "enumeration: 0 IDLE, 1 ACTIVE, 2 COOLDOWN": {"value": [
                {"value": 0, "name": "idle"}, {"value": 1, "name": "active"},
                {"value": 2, "name": "cooldown"}]},
            "raw * 2 - 590 deg after intake TDC; raw * 2 degCA after the tooth": None,
            "candidate raw * 0.002 A/F ADJ factor": None,
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
        throttle = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1075))
        self.assertEqual((throttle.props["scale"], throttle.props["unit"]),
                         ("x*100/255", "percent"))
        timing = m.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF11D4))
        self.assertEqual((timing.props.get("scale"), timing.props["unit"]), (None, "degBTDC"))

    def test_an_unsplit_scale_stays_on_its_field_and_goes_to_the_audit(self):
        m = model()
        field = m.entities[("field", "injection_end_angle_raw")]
        self.assertTrue(field.props["scale"].startswith("raw * 2 - 590 deg"))
        unsplit = {issue.subject for issue in checks.audit(m, ("unsplit",))["unsplit"]}
        self.assertLessEqual({"field.injection_end_angle_raw", "field.af_adjustment_b1_raw",
                              "field.final_timing_raw"}, unsplit)
        self.assertNotIn("field.maf_b1_raw", unsplit)

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

    def test_a_source_outside_its_region_and_an_unlisted_ecu_ram_field_fail_the_schema(self):
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
            ("references", "signal.probe"),
            ("schema", "field.feature_raw"), ("schema", "field.mode"),
            ("schema", "field.other"), ("schema", "field.rom_raw"),
            ("schema", "field.short"), ("schema", "field.state"),
            ("schema", "field.unlisted_raw")])
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
                 ({"value": [{"value": 0, "name": "idle"}, {"value": 1, "name": "active"}]},
                  "enumeration: 0 IDLE, 1 ACTIVE"),
                 ({"scale": "x*(1/4)", "unit": "V"}, None),
                 ({"unit": "V"}, None)]
        units = frozenset(repo.config()["vocab"]["unit"])
        for props, text in cases:
            with self.subTest(props=props):
                self.assertEqual(telemetry.scale_text(props), text)
                if text is not None:
                    self.assertEqual(telemetry.parse_scale(text, units), props)

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
                         {"id": "X_VQ_QH0_Flow_Potential", "unit": "QH0 Flow Potential [%]",
                          "scale": "x*0.00152588"})

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
        self.assertLessEqual(set(entry) - {"rom", "checksums", "note"},
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
                                         "functions": [SymbolKey("7mfk", "fn", 0x00029588)]})

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
        self.assertTrue(step["note"].startswith("ffff114a = floor(0xA2C2/ffff22bc)"))

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


class StageTwoChecksTest(unittest.TestCase):
    def test_the_readme_lists_every_adapter_in_compiler_order(self):
        text = (repo.ROOT / "tools/kb/README.md").read_text(encoding="utf-8")
        listed = re.findall(r"^\| `([a-z]+)` \| `(?:kb|tools|defs|patches)/", text, re.M)
        self.assertEqual(listed, [adapter.__name__.rsplit(".", 1)[1]
                                  for adapter in adapters.ADAPTERS])

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
