import tempfile
import unittest
from pathlib import Path

from kb import checks, compile, names, repo, store
from kb.adapters import files, ledgers, telemetry
from kb.model import Builder, SymbolKey

WRITER = 0x3BD1C
COPIER = 0x20DFE


def builder():
    return Builder(repo.layouts(), compile.spaces(repo.config()),
                   {"7mfk": frozenset({WRITER, COPIER}), "jk00d": frozenset({0x3CACC})},
                   {"7mfk": (0x8200, 0x20000)})


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def write(self, kind, name, document):
        path = self.root / store.path_of(kind, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(store.render(kind, document), encoding="utf-8")

    def build(self, declare=None):
        b = builder()
        files.declare(b, self.root)
        if declare:
            declare(b)
        files.relate(b, self.root)
        model = b.finish()
        names.assign(model, [])
        return b, model

    def test_a_meaning_file_joins_its_symbols_and_names_the_meaning(self):
        self.write("ram", "normalized_bfs", {
            "title": "Normalized load", "level": "code", "home": "7mfk", "width": 8,
            "former": ["normalized_load"],
            "symbol": [{"layout": "7mfk", "address": "ffff1048"},
                       {"layout": "jk00d", "address": "ffff1050", "former": [
                           "bouncing-badger/ram/jk00d-ffff1050"], "evidence": [{
                               "kind": "masked-match", "supports": "homology",
                               "at": "jk00d:0003cacc", "to": "7mfk:0003bd1c", "count": 1,
                               "value": 32}]}],
            "status": [{"layout": "jk78c", "state": "unresolved", "method": "masked-match",
                        "target": "7mfk:0003bd1c", "count": 0, "l0": "0123456789abcdef"}]})
        b, model = self.build()
        meaning = model.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1048))
        self.assertEqual((meaning.key, meaning.tier, meaning.props["width"]),
                         ("normalized_bfs/ram", "file", 8))
        self.assertEqual(sorted(meaning.symbols), ["7mfk", "jk00d"])
        self.assertEqual(meaning.statuses["jk78c"].props["method"], "masked-match")
        self.assertEqual(meaning.symbols["jk00d"].former, ("bouncing-badger",))
        self.assertEqual(meaning.other_names, [("normalized_load", "former",
                                                "kb/ram/normalized_bfs.toml")])
        self.assertEqual(checks.audit(model, ("names",))["names"], [])
        self.assertEqual(b.issues, [])

    def test_a_file_symbol_merges_with_the_symbol_of_a_registry(self):
        self.write("ram", "normalized_bfs", {
            "title": "Normalized load", "symbol": [{"layout": "7mfk", "address": "ffff1048"}]})

        def ledger(b):
            key = b.symbol("7mfk", "ram", 0xFFFF1048, "defs/JK08A.vars.csv")
            b.props(key, {"summary": "From the ledger."}, "defs/JK08A.vars.csv")
            b.name(key, "load_curated", "curated", "tools/ghidra/symbols/7mfk.csv")

        _, model = self.build(ledger)
        meaning = model.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1048))
        self.assertEqual((meaning.name, meaning.props["summary"]),
                         ("normalized_bfs", "From the ledger."))
        self.assertEqual([tier for _, tier, _ in meaning.other_names], ["curated"])

    def test_a_numeric_telemetry_source_owns_an_absent_or_partial_unit(self):
        address = 0xFFFF11F4
        key = SymbolKey("7mfk", "ram", address)

        def ledger(b):
            b.symbol("7mfk", "ram", address, "defs/JK08A.vars.csv")
            b.stash[ledgers.UNITS] = [(key, "signed torque raw", "defs/JK08A.vars.csv")]
            ledgers.relate(b, self.root)

        for props, unit, scale in (({}, None, "raw count"),
                                   ({"unit": "Nm"}, "Nm", None),
                                   ({"scale": "x"}, None, None)):
            with self.subTest(props=props):
                self.write("ram", "probe", {
                    "title": "Probe", **props,
                    "symbol": [{"layout": "7mfk", "address": f"{address:08x}"}]})
                self.write("field", "probe_raw", {
                    "source": "probe/ram", "origin": "ecu_ram", "width": 2,
                    "signed": True, "page": 0, "offset": 1, "profiles": ["tuning"]})
                b, model = self.build(ledger)
                self.assertEqual(b.issues, [])
                self.assertEqual(model.meaning_of(key).props.get("unit"), unit)
                field = model.entities[("field", "probe_raw")]
                self.assertEqual(telemetry._source(model, field, {}),
                                 {"source": address, "scale": scale})

    def test_references_resolve_once_the_meanings_are_named(self):
        self.write("fn", "bfs_producer", {"title": "Producer", "symbol": [
            {"layout": "7mfk", "address": f"{WRITER:08x}"}]})
        self.write("fn", "block_copier", {"title": "Copier", "symbol": [
            {"layout": "7mfk", "address": f"{COPIER:08x}"}]})
        self.write("ram", "normalized_bfs", {"title": "Load", "symbol": [
            {"layout": "7mfk", "address": "ffff1048", "evidence": [
                {"kind": "trace", "supports": "identity", "to": "bfs_producer/fn/7mfk",
                 "relies": "contract"}]}],
            "link": [{"type": "writer", "to": "bfs_producer/fn", "relies": "structure",
                      "via": ["block_copier/fn"]}]})
        b, model = self.build()
        meaning = model.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1048))
        (link,) = meaning.links
        self.assertEqual((link.type, link.to.key, link.stated), ("writer", "bfs_producer/fn",
                                                                   {"7mfk"}))
        self.assertEqual(link.props["via"], [SymbolKey("7mfk", "fn", COPIER)])
        self.assertEqual(meaning.symbols["7mfk"].evidence[0]["to"],
                         SymbolKey("7mfk", "fn", WRITER))
        self.assertEqual(b.issues, [])

    def test_a_reference_that_names_nothing_fails_the_references_check(self):
        self.write("ram", "normalized_bfs", {"title": "Load", "symbol": [
            {"layout": "7mfk", "address": "ffff1048"}],
            "link": [{"type": "writer", "to": "missing_producer/fn"}]})
        b, model = self.build()
        self.assertEqual([(issue.check, issue.subject) for issue in b.issues],
                         [("references", "missing_producer/fn")])
        self.assertEqual(model.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF1048)).links, [])

    def test_owned_architecture_resolves_typed_references_and_ordered_steps(self):
        self.write('stage', 'estimation', {'title': 'Estimation', 'lane': 'flow', 'order': 2})
        self.write('block', 'engine_speed', {'title': 'Engine speed',
                                            'stage': 'estimation/stage', 'home': '7mfk'})
        self.write('fn', 'producer', {'block': 'engine_speed/block', 'symbol': [
            {'layout': '7mfk', 'address': f'{WRITER:08x}'}]})
        self.write('fn', 'copier', {'symbol': [
            {'layout': '7mfk', 'address': f'{COPIER:08x}'}]})
        self.write('ram', 'speed', {'symbol': [
            {'layout': '7mfk', 'address': 'ffff1048'}]})
        self.write('reg', 'capture', {'symbol': [
            {'layout': '7mfk', 'address': 'fffff434'}]})
        self.write('endpoint', 'crank', {'block': 'engine_speed/block', 'direction': 'input',
                                        'registers': ['capture/reg'], 'functions': ['producer/fn']})
        self.write('chain', 'engine_speed', {'output': 'speed/ram', 'home': '7mfk', 'step': [
            {'from': 'capture/reg', 'to': 'speed/ram', 'effect': 'converts',
             'sign': 'negative', 'via': ['copier/fn', 'producer/fn'], 'note': 'y = 100 / x'},
            {'from': 'speed/ram', 'to': 'capture/reg', 'effect': 'stores', 'sign': 'none'}]})
        b, model = self.build()
        self.assertEqual(b.issues, [])
        self.assertEqual(model.entities['block', 'engine_speed'].refs,
                         {'stage': [('stage', 'estimation')]})
        self.assertEqual(model.entities['endpoint', 'crank'].refs,
                         {'block': [('block', 'engine_speed')],
                          'registers': [SymbolKey('7mfk', 'reg', 0xFFFFF434)],
                          'functions': [SymbolKey('7mfk', 'fn', WRITER)]})
        steps = model.entities['chain', 'engine_speed'].steps
        self.assertEqual(steps[0]['via'], [SymbolKey('7mfk', 'fn', COPIER),
                                          SymbolKey('7mfk', 'fn', WRITER)])
        self.assertEqual(steps[1]['from'], SymbolKey('7mfk', 'ram', 0xFFFF1048))
        self.assertEqual(steps[0]['note'], 'y = 100 / x')

    def test_an_architecture_reference_cannot_borrow_a_foreign_layout_symbol(self):
        self.write('ram', 'speed', {'symbol': [
            {'layout': 'jk78c', 'address': 'ffff1000'}]})
        for reference, message in (
                ('speed/ram', 'has no symbol on 7mfk'),
                ('speed/ram/jk78c', 'architecture reference lies on jk78c, not on 7mfk')):
            with self.subTest(reference=reference):
                self.write('chain', 'probe', {'home': '7mfk', 'output': reference, 'step': []})
                b, model = self.build()
                self.assertIn(message, [issue.message for issue in b.issues])
                self.assertEqual(model.entities['chain', 'probe'].refs['output'], [reference])

    def test_malformed_architecture_steps_fail_without_untyped_references(self):
        for step, message in (
                ({'from': 7, 'to': 'speed/ram'}, 'from and to must be references'),
                ({'from': 'speed/ram', 'to': 'speed/ram', 'via': 'producer/fn'},
                 'via is no array of references')):
            with self.subTest(step=step):
                self.write('chain', 'probe', {'step': [step]})
                b, model = self.build()
                self.assertIn(message, [issue.message for issue in b.issues])
                self.assertEqual(model.entities['chain', 'probe'].steps, [])

    def test_an_unnamed_meaning_takes_the_generated_names_of_its_file(self):
        self.write("ram", "quiet-otter", {"title": "Unnamed", "home": "7mfk", "symbol": [
            {"layout": "7mfk", "address": "ffff1048", "name": "quiet-otter"},
            {"layout": "jk00d", "address": "ffff1050", "name": "rapid-heron"}]})
        self.write("ram", "normalized_bfs", {"title": "Load", "symbol": [
            {"layout": "7mfk", "address": "ffff102c"}],
            "link": [{"type": "copy", "to": "rapid-heron/ram"}]})
        b, model = self.build()
        meaning = model.meaning_of(SymbolKey("jk00d", "ram", 0xFFFF1050))
        self.assertEqual((meaning.name, meaning.semantic, meaning.symbols["jk00d"].name),
                         ("quiet-otter", False, "rapid-heron"))
        self.assertEqual(names.missing(model, []), [])
        self.assertIn("rapid-heron", names.reserved(model, []))
        (link,) = model.meaning_of(SymbolKey("7mfk", "ram", 0xFFFF102C)).links
        self.assertIs(link.to, meaning)
        self.assertEqual(b.issues, [])

    def test_a_file_that_differs_from_the_name_of_its_meaning_fails_the_names_check(self):
        self.write("ram", "quiet-otter", {"title": "Unnamed", "symbol": [
            {"layout": "7mfk", "address": "ffff1048", "name": "quiet-otter"}]})

        def curated(b):
            b.name(SymbolKey("7mfk", "ram", 0xFFFF1048), "load_curated", "curated", "c.csv")

        _, model = self.build(curated)
        model.names = []
        found = [issue.message for issue in checks.names_check(model)
                 if issue.subject == "quiet-otter/ram"]
        self.assertEqual(found, ["the meaning is load_curated/ram; a file carries the name of "
                                 "its meaning"])

    def test_unknown_keys_and_layouts_fail_the_schema_check(self):
        self.write("ram", "normalized_bfs", {"title": "Load", "colour": "red", "symbol": [
            {"layout": "9zzz", "address": "ffff1048"},
            {"layout": "7mfk", "address": "FFFF1048"}]})
        b, _ = self.build()
        self.assertEqual(sorted(issue.message for issue in b.issues if issue.check == "schema"),
                         ["address 'FFFF1048' of 7mfk is not eight lowercase hexadecimal digits",
                          "layout '9zzz'", "unknown key colour"])

    def test_a_feature_file_gives_the_targets_with_their_symbol_references(self):
        self.write("hook", "fuel_cut_hook", {"title": "Hook", "width": 32, "symbol": [
            {"layout": "7mfk", "address": "0000f000"}, {"layout": "jk00d", "address": "0000f100"}]})
        self.write("feature", "map_switching", {"title": "Map switching", "target": [
            {"layout": "jk00d", "status": "supported", "extra_cvtc_storage": "000fe000",
             "hooks": {"fuel_cut": {"hook": "fuel_cut_hook/hook", "replacement": "000f8000"}}}]})
        b, model = self.build()
        target = model.targets[("map_switching", "jk00d")]
        self.assertEqual((target.status, target.props["hooks"]["fuel_cut"]["hook"],
                          target.props["extra_cvtc_storage"]),
                         ("supported", SymbolKey("jk00d", "hook", 0xF100), "000fe000"))
        self.assertIn(("feature", "map_switching"), model.entities)
        self.assertEqual(b.issues, [])

    def test_the_key_tables_and_unsupported_entries_of_a_target_name_symbols(self):
        self.write("tbl", "fuel_cut", {"title": "Cut", "symbol": [
            {"layout": "7mfk", "address": "0000f000"}, {"layout": "jk00d", "address": "0000f100"}]})
        self.write("tbl", "exhaust_target", {"title": "Target", "symbol": [
            {"layout": "7mfk", "address": "0000f200"}]})
        self.write("feature", "map_switching", {"title": "Map switching", "target": [
            {"layout": "jk00d", "status": "supported",
             "families": {"over_run_fuel_cut": "fuel_cut/tbl"},
             "unsupported": [{"symbol": "exhaust_target/tbl", "note": "No surface"}]}]})
        b, model = self.build()
        target = model.targets[("map_switching", "jk00d")]
        self.assertEqual(target.props["families"],
                         {"over_run_fuel_cut": SymbolKey("jk00d", "tbl", 0xF100)})
        # A meaning without a symbol on the layout of the target resolves to
        # its home symbol.
        self.assertEqual(target.props["unsupported"],
                         [{"symbol": SymbolKey("7mfk", "tbl", 0xF200), "note": "No surface"}])
        self.assertEqual(target.needs(), [SymbolKey("jk00d", "tbl", 0xF100)])
        self.assertEqual(b.issues, [])

    def test_a_field_file_names_its_signal_and_the_7mfk_symbol_of_its_source(self):
        self.write("ram", "probe", {"title": "Probe", "unit": "V", "scale": "x/200",
                                    "symbol": [{"layout": "7mfk", "address": "ffff11f4"}]})
        self.write("field", "probe_raw", {
            "signal": "probe/signal", "source": "probe/ram", "origin": "ecu_ram", "width": 2,
            "signed": False, "profiles": ["tuning"], "page": 0, "offset": 1})
        self.write("field", "tick16", {
            "source": "can_telemetry.tick16", "origin": "telemetry_state", "width": 2,
            "signed": False, "scale": "raw ticks", "profiles": ["tuning"], "page": 0,
            "offset": 3})
        self.write("field", "loose_raw", {
            "source": "probe/ram", "origin": "ecu_ram", "width": 2, "signed": False,
            "scale": "Q14 factor", "context": "trims", "position": 0})
        b, model = self.build(lambda b: b.entity("signal", "probe", "probe.toml"))
        field = model.entities[("field", "probe_raw")]
        self.assertEqual((field.refs["source"], field.refs["signal"]),
                         ([SymbolKey("7mfk", "ram", 0xFFFF11F4)], [("signal", "probe")]))
        self.assertNotIn("source", field.props)
        self.assertEqual(model.entities[("field", "tick16")].props["source"],
                         "can_telemetry.tick16")
        self.assertEqual(sorted(model.entities[("feature", "can_telemetry")].refs["requires"]),
                         [("field", "loose_raw"), ("field", "probe_raw"), ("field", "tick16")])
        self.assertEqual(b.stash["telemetry_units"], {SymbolKey("7mfk", "ram", 0xFFFF11F4)})
        # The `fields` check, not the reader, reports the missing signal and
        # the scale of an `ecu_ram` field.
        self.assertEqual(b.issues, [])

    def test_the_fields_and_widths_checks_verify_what_each_field_reads(self):
        status = {"layout": "jk00d", "state": "unresolved", "method": "masked-match",
                  "target": "7mfk:0003bd1c", "count": 0, "l0": "0123456789abcdef"}
        self.write("ram", "probe", {"title": "Probe", "width": 16, "unit": "V", "scale": "x/200",
                                    "symbol": [{"layout": "7mfk", "address": "ffff11f4"}],
                                    "status": [status]})
        self.write("ram", "narrow", {"title": "Narrow", "width": 8, "signed": True,
                                     "symbol": [{"layout": "7mfk", "address": "ffff11f8"}]})
        self.write("ram", "inside", {"title": "Inside", "width": 8,
                                     "symbol": [{"layout": "7mfk", "address": "ffff5e40"}],
                                     "status": [status]})
        self.write("ram", "cell", {"title": "Cell", "width": 16,
                                   "symbol": [{"layout": "jk00d", "address": "ffff1200"}]})
        self.write("feature", "can_telemetry", {"title": "CAN telemetry", "target": [
            {"layout": "7mfk", "status": "supported", "allocations": {
                "tick16": {"address": "ffff5e08", "width": 2},
                "late": {"address": "ffff5f00", "width": 1}}},
            {"layout": "jk00d", "status": "supported",
             "roles": {"cell_raw": {"symbol": "cell/ram"}}}]})
        read = {"signal": "probe/signal", "origin": "ecu_ram", "signed": False,
                "profiles": ["tuning"], "page": 0}
        self.write("field", "probe_raw", {**read, "source": "probe/ram", "width": 2, "offset": 1})
        self.write("field", "loose_raw", {
            "source": "probe/ram", "origin": "ecu_ram", "width": 2, "signed": False,
            "scale": "Q14 factor", "profiles": ["tuning"], "page": 0, "offset": 3})
        self.write("field", "narrow_raw", {**read, "source": "narrow/ram", "width": 2,
                                           "offset": 5})
        self.write("field", "cell_raw", {**read, "source": "narrow/ram", "width": 1,
                                         "signed": True, "offset": 7})
        self.write("field", "inside_raw", {**read, "source": "inside/ram", "width": 1,
                                           "offset": 8})
        allocated = {"origin": "telemetry_state", "width": 2, "signed": False,
                     "profiles": ["tuning"], "page": 1}
        self.write("field", "tick16", {**allocated, "source": "can_telemetry.tick16",
                                       "scale": "raw ticks", "offset": 1})
        self.write("field", "late", {**allocated, "source": "can_telemetry.late", "offset": 3})

        def declare(b):
            b.entity("signal", "probe", "probe.toml")
            b.stash["feature_ram"] = [(0xFFFF5E00, 0xFFFF5F10, "can_telemetry")]
            b.stash["origin_regions"] = {
                "telemetry_state": [(0xFFFF5E00, 0xFFFF5E20, "can_telemetry")]}

        _, model = self.build(declare)
        self.assertEqual(sorted((issue.subject, issue.message) for issue in checks.fields(model)), [
            ("inside_raw/field", "the source 7mfk-ffff5e40/ram lies in the RAM that a feature "
             "allocates"),
            ("late/field", "a telemetry_state field without scale"),
            ("late/field", "allocation can_telemetry.late lies outside the telemetry_state "
             "regions of can_telemetry"),
            ("loose_raw/field", "an ecu_ram field that names no signal"),
            ("loose_raw/field", "an ecu_ram field with scale 'Q14 factor'; the meaning of its "
             "source holds the scale"),
            ("narrow_raw/field", "on jk00d the source meaning has no symbol and no status, and "
             "no symbol fills the role of the field"),
            ("narrow_raw/field", "signed False disagrees with 7mfk-ffff11f8/ram, whose signed is "
             "True")])
        self.assertEqual(sorted((issue.subject, issue.message) for issue in checks.widths(model)), [
            ("late/field", "the field of 2 bytes exceeds allocation can_telemetry.late, which "
             "holds 1"),
            ("narrow_raw/field", "the field of 2 bytes exceeds 7mfk-ffff11f8/ram, whose width is "
             "8 bits")])

    def test_a_signal_file_observes_the_7mfk_symbols_of_meanings_and_allocations(self):
        self.write("ram", "probe", {"title": "Probe", "width": 16,
                                    "symbol": [{"layout": "7mfk", "address": "ffff11f4"}]})
        self.write("feature", "can_telemetry", {"title": "CAN telemetry", "target": [
            {"layout": "7mfk", "status": "supported",
             "allocations": {"tick16": {"address": "ffff5e08", "width": 2}}}]})
        signal = {"title": "Probe", "domain": "engine", "priority": "core", "coverage": "fixed",
                  "basis": "exact-code", "note": "Probe."}
        self.write("signal", "probe", {**signal, "observes": ["probe/ram", "can_telemetry.tick16"]})
        self.write("signal", "loose", {**signal, "observes": ["can_telemetry.probe"]})
        self.write("signal", "bare", {**signal, "observes": "probe/ram"})
        b, model = self.build()
        probe = model.entities[("signal", "probe")]
        self.assertEqual((probe.refs["observes"], probe.props["observes"]),
                         ([SymbolKey("7mfk", "ram", 0xFFFF11F4), "can_telemetry.tick16"],
                          ["can_telemetry.tick16"]))
        self.assertEqual(sorted((issue.check, issue.subject, issue.message) for issue in b.issues),
                         [("references", "loose/signal",
                           "can_telemetry.probe is no allocation of a 7mfk target"),
                          ("schema", "bare/signal", "observes is no array of references")])


if __name__ == "__main__":
    unittest.main()
