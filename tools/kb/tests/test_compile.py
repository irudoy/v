import csv
import re
import tomllib
import unittest

from kb import adapters, checks, compile, names, repo
from kb.adapters import definitions, ledgers, native, overrides, signals, telemetry
from kb.model import Builder, SymbolKey


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


class InterpAdapterTest(unittest.TestCase):
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

    def test_a_shared_registry_carries_to_a_layout_with_the_same_function_bytes(self):
        m = model()
        symbol = m.symbols[SymbolKey("jk00c", "fn", 0x00026FC0)]
        self.assertIs(symbol.meaning, m.meaning_of(SymbolKey("jk00d", "fn", 0x00026FC0)))
        self.assertEqual([(item["kind"], item["to"]) for item in symbol.evidence],
                         [("byte-identical", SymbolKey("jk00d", "fn", 0x00026FC0))])

    def test_an_unsupported_correspondence_is_an_unresolved_search(self):
        meaning = model().meaning_of(SymbolKey("7mfk", "fn", 0x000261B8))
        for layout in ("1nd", "jk78c"):
            status = meaning.statuses[layout]
            self.assertEqual((status.state, status.props["method"], status.props["count"]),
                             ("unresolved", "interp-contract", 0))


def _readers(meaning, layout):
    """{accessor address: evidence} of the reader links of a meaning on a layout."""
    return {link.to.symbols[layout].address: link.evidence for link in meaning.links
            if link.type == "reader" and layout in link.to.symbols and layout in link.stated}


class NativeAdapterTest(unittest.TestCase):
    def test_a_native_id_joins_its_targets_and_names_the_meaning(self):
        meaning = model().meaning_of(SymbolKey("jk78c", "tbl", 0x00009FBA))
        self.assertEqual((meaning.key, meaning.tier, meaning.home),
                         ("fuel_compensation_alternate/tbl", "native", "jk78c"))
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

    def test_text_that_the_images_of_a_layout_state_differently_names_its_image(self):
        meaning = model().meaning_of(SymbolKey("1nd", "tbl", 0x0000E6C8))
        self.assertEqual((meaning.key, meaning.home),
                         ("vvel_duration_mode_14/tbl", "1nd"))
        self.assertTrue(meaning.props["summary"].startswith("Mode 14 duration surface"))
        notes = meaning.symbols["1nd"].props["note"]
        self.assertEqual(sorted({note.split(": ", 1)[0] for note in notes}), ["1ND0A", "1ND3B"])

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
        self.assertEqual((call["kind"], call["at"], call["value"]), ("l0", "jk78c:0006a9e8", 28))
        base = m.meaning_of(SymbolKey("jk78c", "ram", 0xFFFF1084))
        self.assertEqual(list(_readers(base, "jk78c")), [0x0006AEB8])
        self.assertEqual(base.symbols["jk78c"].evidence,
                         [{"kind": "l0", "supports": "identity", "at": "jk78c:0006b044"}])

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
        self.assertEqual((margins.refs.get("observes"), margins.props["observes"]),
                         (None, [f"can_telemetry.knock_margin_min_ch{index}"
                                 for index in range(1, 7)]))
        self.assertNotIn(SymbolKey("7mfk", "ram", 0xFFFF5E10), m.symbols)

    def test_the_catalog_constants_are_keys_of_can_telemetry(self):
        props = model().entities[("feature", "can_telemetry")].props
        self.assertEqual({key: props[key] for key in signals.FEATURE_KEYS},
                         {"telemetry_profile": "tuning", "full_rate_hz": 97.65625,
                          "rotating_divisor": 5})

    def test_stored_dids_that_differ_from_the_derived_ones_go_to_the_audit(self):
        found = {issue.subject: issue.message for issue in model().issues
                 if issue.path == signals.SIGNALS.as_posix()}
        self.assertEqual(sorted(found), ["signal.apc_ignition_command", "signal.temperatures"])
        self.assertTrue(found["signal.temperatures"].endswith(
            "observed meaning: 1101, 1104, 1106, 1111, 111f"))

    def test_the_fields_of_a_signal_serve_it(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        signals.declare(b, repo.ROOT)
        self.assertEqual(b.stash["signal_fields"]["knock_count_latched"], "knock_event_latches")

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
        unsplit = {issue.subject for issue in checks.audit(m)["unsplit"]}
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
                                           "can_telemetry_startup": "000d4e03"})
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


class StageTwoChecksTest(unittest.TestCase):
    def test_the_readme_lists_every_adapter_in_compiler_order(self):
        text = (repo.ROOT / "tools/kb/README.md").read_text(encoding="utf-8")
        listed = re.findall(r"^\| `([a-z]+)` \| `(?:tools|defs|patches)/", text, re.M)
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
