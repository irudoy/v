import contextlib
import copy
import csv
import io
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest import mock

import pytest

from kb import (adapters, checks, cli, compile, convert, ledger_projection, match, names, repo,
                store, targets, vocab, write)
from kb.adapters import files as file_adapter
from kb.adapters import profiles
from kb.model import Meaning, SymbolKey
from kb.repo import KbError
from tools.kb.tests import writer_sources

pytestmark = pytest.mark.usefixtures('reuse_kb_source_parses', 'source_order')

ISOLATED_CASES = {
    ('PlanTest', 'test_set_refuses_to_remove_the_block_of_a_reviewed_function'),
    ('PlanTest', 'test_set_refuses_a_block_that_no_entity_declares'),
    ('NewTest', 'test_new_starts_a_meaning_with_the_generated_name_of_its_row'),
    ('NewTest', 'test_a_batch_sets_and_links_a_new_meaning_without_mutating_its_source'),
    ('NewTest', 'test_a_batch_starts_a_field_with_its_keys'),
    ('SetTest', 'test_set_refuses_a_code_bit_without_its_own_evidence'),
    ('RenameMeaningTest',
     'test_rename_names_an_unnamed_meaning_and_keeps_its_generated_names_as_former_references'),
    ('NewTest', 'test_a_failed_batch_with_a_new_meaning_writes_no_files_or_graph'),
    ('NewTest', 'test_a_named_meaning_keeps_the_names_of_the_row_as_former_references'),
    ('NewTest', 'test_a_new_location_does_not_shadow_an_existing_kind'),
    ('NewTest', 'test_a_new_meaning_resolves_its_current_symbols_and_former_names'),
    ('NewTest', 'test_an_unsupported_access_width_refuses_an_entire_batch_before_writes'),
    ('NewTest', 'test_new_refuses_a_held_place_or_name_and_the_keys_of_the_other_form'),
    ('NewTest', 'test_new_starts_the_empty_file_of_a_designed_entity'),
    ('SetTest', 'test_a_feature_takes_every_key_besides_its_targets'),
    ('SetTest', 'test_set_refuses_keys_and_values_outside_its_schema'),
    ('SetTest', 'test_tables_join_and_an_unset_key_leaves_no_empty_table'),
    ('LinkTest', 'test_a_link_names_its_target_by_any_of_its_names'),
    ('LinkTest', 'test_link_joins_the_keys_and_the_evidence_of_the_held_link'),
    ('LinkTest', 'test_link_refuses_reliance_on_a_missing_contract'),
    ('LinkTest', 'test_links_refuse_what_the_schema_or_the_files_contradict'),
    ('LinkTest', 'test_unlink_removes_the_link_that_its_keys_choose'),
    ('LinkTest', 'test_unlink_withdraws_converted_dependency_tokens_at_both_claiming_ends'),
    ('RenameMeaningTest', 'test_a_batch_renames_a_meaning_after_its_other_operations'),
    ('RenameMeaningTest', 'test_renames_refuse_the_names_that_the_model_holds'),
}


@pytest.fixture(scope='module')
def preserved_full_models(reuse_kb_source_parses):
    held = {}
    yield held
    for cls, model, before, document in held.values():
        assert convert.dump(model) == before
        assert getattr(cls, 'held', None) == document


@pytest.fixture(scope='module')
def isolated_model(reuse_kb_source_parses, tmp_path_factory):
    root = tmp_path_factory.mktemp('generic-writer')
    hashes = writer_sources.write_sources(root)
    model = compile.build(root, order=(file_adapter,))
    assert model.stash['ledger_rows'] and write._issues(model) == {}
    before = convert.dump(model)
    held = store.load(root, LinkTest.RPM_FILE)
    yield model, held
    assert convert.dump(model) == before
    assert writer_sources.unchanged(root, hashes)


@pytest.fixture(scope='module')
def isolated_feature_model(reuse_kb_source_parses, isolated_model):
    base, _ = isolated_model
    probe = {'title': 'Probe', 'target': [{'layout': 'jk00c', 'status': 'planned',
             'basis': {'maps': 'stock', 'timing': 'stock'}}]}
    model = compile.build(base.root, {SetTest.PROBE_FILE: store.render('feature', probe)},
                          order=(file_adapter,))
    assert model.stash['ledger_rows'] and write._issues(model) == {}
    before = convert.dump(model)
    yield model
    assert convert.dump(model) == before


@pytest.fixture
def source_order(request, monkeypatch, preserved_full_models):
    instance = request.instance
    if instance is None or type(instance).__name__ not in {key[0] for key in ISOLATED_CASES}:
        return
    cls = type(instance)
    if cls not in preserved_full_models:
        preserved_full_models[cls] = (
            cls, cls.base, convert.dump(cls.base), copy.deepcopy(getattr(cls, 'held', None)))
    if (cls.__name__, request.node.name) not in ISOLATED_CASES:
        return
    monkeypatch.setattr(adapters, 'ADAPTERS', (file_adapter,))
    model, held = request.getfixturevalue('isolated_model')
    if cls is SetTest:
        model = request.getfixturevalue('isolated_feature_model')
    monkeypatch.setattr(instance, 'base', model)
    if cls is LinkTest:
        monkeypatch.setattr(instance, 'held', copy.deepcopy(held))

# A table without a semantic name: the search from its symbol on 7mfk finds one
# counterpart on JK00C through 40 masked words.
TABLE, TABLE_HOME, TABLE_JK00C = "astute-toad/tbl", 0x11FF6, 0x142D3
TABLE_EVIDENCE = {"kind": "masked-match", "supports": "homology", "at": "jk00c:0004820a",
                  "to": "7mfk:00047282", "count": 1, "value": 40}
# Named data with files: the search of the first finds one counterpart on
# JK78C and that of the second none on 1ND.
THROTTLE, THROTTLE_HOME, THROTTLE_JK78C = "throttle_runtime/ram", 0xFFFF1796, 0xFFFF17A4
INHIBIT, INHIBIT_HOME = "fuel_inhibit/ram", 0xFFFF2497
# Named data whose status on 1ND records a search without matches and a note.
FLOW, FLOW_HOME = "alpha_n_flow/ram", 0xFFFF1170
# A converted curated function: the search from its 7mfk symbol finds one
# counterpart on JK78C.
SELECTOR, SELECTOR_HOME, SELECTOR_JK78C = "accelerator_pedal_pair_selector/fn", 0x6EC68, 0x8D384
SPEC = {"kind": "spec", "path": "tools/kb/SPEC.md", "note": "section 7.4"}


def bind(meaning, symbol, **keys):
    return {"cmd": "bind", "meaning": meaning, "symbol": symbol, **keys}


class PlanTest(unittest.TestCase):
    """Operations planned over the working tree with the files in memory; the
    base has only the owned home symbol of TABLE and stored former references
    of the home symbol of SELECTOR."""

    @classmethod
    def setUpClass(cls):
        table_path = store.path_of("tbl", "astute-toad")
        table = store.load(repo.ROOT, table_path)
        table["symbol"] = [entry for entry in table["symbol"] if entry["layout"] == "7mfk"]
        cls.table_home = copy.deepcopy(table["symbol"][0])
        selector_path = store.path_of("fn", "accelerator_pedal_pair_selector")
        selector = store.load(repo.ROOT, selector_path)
        [home] = [entry for entry in selector["symbol"] if entry["layout"] == "7mfk"]
        home["former"] = [*home.get("former", ()),
                          f"probe-heron/fn/7mfk-{SELECTOR_HOME:08x}",
                          f"probe-otter/fn/7mfk-{SELECTOR_HOME:08x}"]
        cls.selector_home = copy.deepcopy(home)
        cls.base = compile.build(repo.ROOT, {table_path: store.render("tbl", table),
                                             selector_path: store.render("fn", selector)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base), root=self.base.root)

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.plan(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    @pytest.mark.slow
    def test_bind_extends_an_unnamed_meaning_and_preserves_its_owned_home(self):
        change, texts, result = self.plan(bind(TABLE, f"jk00c:{TABLE_JK00C:08x}"))
        path = Path("kb/tbl/astute-toad.toml")
        self.assertEqual(list(texts), [path])
        document = tomllib.loads(texts[path])
        self.assertEqual(texts[path], store.render("tbl", document))
        home, bound = document["symbol"]
        self.assertEqual(home, self.table_home)
        self.assertEqual(bound["address"], f"{TABLE_JK00C:08x}")
        self.assertRegex(bound["name"], vocab.GENERATED_NAME)
        self.assertEqual(bound["evidence"], [TABLE_EVIDENCE])
        self.assertNotIn(("7mfk", "tbl", TABLE_HOME),
                         {row.key for row in result.names})
        key = SymbolKey("jk00c", "tbl", TABLE_JK00C)
        meaning = result.meaning_of(key)
        self.assertEqual(meaning.key, TABLE)
        self.assertEqual(sorted(meaning.symbols), ["7mfk", "jk00c"])
        self.assertEqual(result.symbols[key].generated, bound["name"])
        self.assertIn(key, result.file_evidence)
        self.assertEqual(change.lines, [
            f"bind {bound['name']}/tbl/jk00c-{TABLE_JK00C:08x}: masked-match at jk00c:0004820a "
            "to 7mfk:00047282 count 1 value 40"])

    @pytest.mark.slow
    def test_bind_of_a_named_meaning_keeps_the_owned_former_references(self):
        _, texts, result = self.plan(bind(SELECTOR, f"jk78c:{SELECTOR_JK78C:08x}", note="probe",
                                          level="candidate"))
        document = tomllib.loads(texts[store.path_of("fn", "accelerator_pedal_pair_selector")])
        home, bound = document["symbol"]
        self.assertEqual(home, self.selector_home)
        self.assertEqual((bound["level"], bound["note"]), ("candidate", "probe"))
        self.assertNotIn("name", bound)
        symbol = result.symbols[SymbolKey("7mfk", "fn", SELECTOR_HOME)]
        self.assertEqual(symbol.former, ("probe-heron", "probe-otter"))
        self.assertEqual(symbol.meaning.key, SELECTOR)

    def test_set_refuses_to_remove_the_block_of_a_reviewed_function(self):
        error = self.refused({'cmd': 'set', 'ref': SELECTOR, 'unset': ['block']})
        self.assertIn('reviewed function needs a block', error)

    def test_set_refuses_a_block_that_no_entity_declares(self):
        error = self.refused({'cmd': 'set', 'ref': SELECTOR,
                              'keys': {'block': 'missing/block'}})
        self.assertIn('is not a declared block', error)

    @pytest.mark.slow
    def test_a_batch_writes_the_statuses_of_one_meaning_into_its_file(self):
        change, texts, result = self.plan(
            {"cmd": "unresolved", "meaning": INHIBIT, "layout": "1nd"},
            {"cmd": "absent", "meaning": INHIBIT, "layout": "1me3b", "evidence": [SPEC]})
        document = tomllib.loads(texts[Path("kb/ram/fuel_inhibit.toml")])
        self.assertEqual(document["status"], [
            {"layout": "1me3b", "state": "absent", "evidence": [SPEC]},
            {"layout": "1nd", "state": "unresolved", "method": "masked-match",
             "target": f"7mfk:{INHIBIT_HOME:08x}", "count": 0,
             "l0": match.search_digest("1nd")}])
        meaning = result.meaning_of(SymbolKey("7mfk", "ram", INHIBIT_HOME))
        self.assertEqual({layout: status.state for layout, status in meaning.statuses.items()},
                         {"1me3b": "absent", "1nd": "unresolved"})
        self.assertEqual(checks.statuses(result), [])
        self.assertEqual(change.lines, [
            f"unresolved {INHIBIT} on 1nd: masked-match search of 7mfk:{INHIBIT_HOME:08x}, "
            "0 matches",
            f"absent {INHIBIT} on 1me3b: spec path tools/kb/SPEC.md"])

    @pytest.mark.slow
    def test_a_repeated_search_keeps_the_note_of_its_status(self):
        path = Path("kb/ram/alpha_n_flow.toml")
        held = next(entry for entry in tomllib.loads((repo.ROOT / path).read_text())["status"]
                    if entry["layout"] == "1nd")
        self.assertTrue(held["note"])

        def status(**keys):
            _, texts, _ = self.plan({"cmd": "unresolved", "meaning": FLOW, "layout": "1nd",
                                     **keys})
            # A repeat on the L0 of the held digest leaves the file unchanged.
            text = texts[path] if path in texts else (repo.ROOT / path).read_text()
            return next(entry for entry in tomllib.loads(text)["status"]
                        if entry["layout"] == "1nd")

        repeated = status()
        self.assertEqual((repeated["method"], repeated["target"], repeated["count"],
                          repeated["l0"], repeated["note"]),
                         ("masked-match", f"7mfk:{FLOW_HOME:08x}", 0, match.search_digest("1nd"),
                          held["note"]))
        self.assertEqual(status(note="probe")["note"], "probe")
        self.assertNotIn("note", status(method="masked-match", target=f"7mfk:{FLOW_HOME:08x}",
                                        count=2))

    @pytest.mark.slow
    def test_the_checks_of_the_result_refuse_evidence_that_l0_refutes(self):
        message = self.refused(bind(THROTTLE, "jk78c:ffff17a6", evidence=[{
            **TABLE_EVIDENCE, "at": "jk78c:0002ffb8", "to": "7mfk:0002ce62", "value": 12}]))
        self.assertIn("nothing is written", message)
        self.assertIn("homology: kb/ram/throttle_runtime.toml: jk78c-ffff17a6/ram: "
                      "masked-match evidence", message)
        self.assertIn("which stores ffff17a4, not ffff17a6", message)

    @pytest.mark.slow
    def test_a_status_of_a_registry_refuses_a_symbol_on_its_layout(self):
        # The compiler with the adapter of the address profiles, whose
        # correspondence rows state the statuses of the telemetry sources.
        order = tuple(adapter for adapter in adapters.ORDER
                      if adapter not in adapters.CONVERTED or adapter is profiles)
        with mock.patch.object(adapters, "ADAPTERS", order):
            base = compile.build(repo.ROOT)
            meaning = next(meaning for meaning in base.meanings
                           if meaning.key == "normalized_load/ram")
            self.assertEqual(meaning.statuses["1nd"].state, "unresolved")
            with self.assertRaises(KbError) as caught:
                write.plan([bind("normalized_load/ram", "1nd:fffec000", evidence=[
                    {"kind": "registry", "path": "patches/rom-address-profiles.toml"}])],
                    base, write.model_resolver(base))
        self.assertEqual(caught.exception.code, 3, str(caught.exception))
        message = str(caught.exception)
        self.assertIn("symbols: patches/1nd-runtime-correspondence.csv: normalized_load/ram: "
                      "status unresolved on 1nd, where the meaning has 1nd-fffec000/ram", message)

    def test_operations_refuse_what_the_model_contradicts(self):
        self.assertIn("finds jk00c:000142d3 on jk00c, not jk00c:000142d4",
                      self.refused(bind(TABLE, "jk00c:000142d4")))
        self.assertIn("jk00c:0004b27c is knock_slice_evaluator/fn/jk00c-0004b27c; `kb merge`",
                      self.refused(bind("heavenly-fox/fn", "jk00c:0004b27c")))
        self.assertIn(f"{THROTTLE} has {THROTTLE}/jk00d-ffff17ec on jk00d",
                      self.refused(bind(THROTTLE, "jk00d:ffff17ee")))
        self.assertIn(f"`kb bind {THROTTLE} jk78c:{THROTTLE_JK78C:08x}` records it",
                      self.refused({"cmd": "unresolved", "meaning": THROTTLE, "layout": "jk78c"}))

    def test_usage_errors_name_the_operation(self):
        self.assertIn("bind takes no layout", self.refused(
            bind(TABLE, "jk00c:0", layout="jk00c"), code=2))
        self.assertIn("absent needs evidence", self.refused(
            {"cmd": "absent", "meaning": TABLE, "layout": "jk00c"}, code=2))
        self.assertIn("evidence kind 'guess'", self.refused(
            {"cmd": "absent", "meaning": TABLE, "layout": "jk00c", "evidence": [{"kind": "guess"}]},
            code=2))
        self.assertIn("did-table evidence needs value", self.refused(
            bind(TABLE, "jk00c:0", evidence=[{"kind": "did-table", "at": "jk00c:0"}]), code=2))
        self.assertIn("method, target, and count", self.refused(
            {"cmd": "unresolved", "meaning": TABLE, "layout": "jk00c", "count": 2}, code=2))
        self.assertIn("unknown layout 'k9'", self.refused(bind(TABLE, "k9:0"), code=5))
        self.assertIn("no meaning 'nothing/tbl'", self.refused(bind("nothing/tbl", "jk00c:0"),
                                                                code=5))
        self.assertTrue(self.refused({"cmd": "unresolved", "meaning": TABLE, "layout": "jk00c",
                                      "count": 2}, {"cmd": "not-a-command"}, code=2).startswith("op 1: "))
        self.assertTrue(self.refused(bind(TABLE, f"jk00c:{TABLE_JK00C:08x}"), {"cmd": "not-a-command"},
                                     code=2).startswith("op 2: cmd 'not-a-command'"))


def new(kind, ref, **keys):
    return {"cmd": "new", "kind": kind, "symbol" if ":" in ref else "slug": ref, **keys}


class NewTest(unittest.TestCase):
    """`new` over a base whose kb/names.csv reserves the generated name
    probe-heron, with the former name probe-otter, for the RAM location FREE
    on 7mfk, which holds no symbol."""

    FREE = 0xFFFF0FF0
    LOCATION = f"7mfk:{FREE:08x}"
    ROW = names.Row("7mfk", "ram", FREE, "probe-heron", ("probe-otter",))

    @classmethod
    def setUpClass(cls):
        rows = [row for row in names.read() if row.key != cls.ROW.key] + [cls.ROW]
        cls.base = compile.build(repo.ROOT, {names.PATH: names.render(rows)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base), root=self.base.root)

    def refused(self, *ops, code=3):
        change = write.Change(self.base, write.model_resolver(self.base), root=self.base.root)
        with self.assertRaises(KbError) as caught:
            for number, op in enumerate(ops, 1):
                change.run(op, number)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def test_new_starts_a_meaning_with_the_generated_name_of_its_row(self):
        change, texts, result = self.plan(new("ram", self.LOCATION, evidence=[SPEC],
                                              note="probe"))
        path = store.path_of("ram", "probe-heron")
        self.assertEqual(list(texts), [names.PATH, path])
        self.assertNotIn(self.ROW.key, {row.key for row in names.parse(texts[names.PATH])})
        self.assertEqual(tomllib.loads(texts[path]), {"symbol": [{
            "layout": "7mfk", "address": f"{self.FREE:08x}", "name": "probe-heron",
            "former": [f"probe-otter/ram/7mfk-{self.FREE:08x}"], "note": "probe",
            "evidence": [SPEC]}]})
        key = SymbolKey("7mfk", "ram", self.FREE)
        self.assertEqual(result.meaning_of(key).key, "probe-heron/ram")
        self.assertEqual(result.symbols[key].former, ("probe-otter",))
        self.assertEqual(change.lines, [
            f"new probe-heron/ram/7mfk-{self.FREE:08x}: spec path tools/kb/SPEC.md"])

    def test_a_named_meaning_keeps_the_names_of_the_row_as_former_references(self):
        _, texts, result = self.plan(new("ram", self.LOCATION, name="probe_cell",
                                         level="candidate", evidence=[SPEC]))
        [entry] = tomllib.loads(texts[store.path_of("ram", "probe_cell")])["symbol"]
        self.assertEqual(entry, {"layout": "7mfk", "address": f"{self.FREE:08x}", "former": [
            f"{name}/ram/7mfk-{self.FREE:08x}" for name in ("probe-heron", "probe-otter")],
            "level": "candidate", "evidence": [SPEC]})
        symbol = result.symbols[SymbolKey("7mfk", "ram", self.FREE)]
        self.assertEqual((symbol.meaning.key, symbol.former),
                         ("probe_cell/ram", ("probe-heron", "probe-otter")))

    def test_a_batch_sets_and_links_a_new_meaning_without_mutating_its_source(self):
        key = SymbolKey("7mfk", "ram", self.FREE)
        before = len(self.base.meanings), set(self.base.symbols), len(self.base.links)
        _, texts, result = self.plan(
            new("ram", self.LOCATION, name="probe_cell", evidence=[SPEC]),
            new("ram", f"7mfk:{self.FREE + 2:08x}", name="probe_gate", evidence=[SPEC]),
            assign("probe_cell/ram", {"summary": "A counter of the probe.", "unit": "counts"}),
            {"cmd": "link", "meaning": "probe_gate/ram", "type": "selector", "to": "probe_cell/ram",
             "keys": {"layouts": ["7mfk"], "relies": "structure"}},
            {"cmd": "link", "meaning": "probe_cell/ram", "type": "input", "to": FLOW,
             "keys": {"layouts": ["7mfk"], "relies": "structure"}},
        )
        probe = result.meaning_of(key)
        self.assertEqual(probe.props["summary"], "A counter of the probe.")
        self.assertTrue(any(link.type == "input" and link.to.key == FLOW for link in probe.links))
        gate = result.meaning_of(SymbolKey("7mfk", "ram", self.FREE + 2))
        self.assertTrue(any(link.type == "selector" and link.to is probe for link in gate.links))
        self.assertIn(store.path_of("ram", "probe_cell"), texts)
        self.assertEqual((len(self.base.meanings), set(self.base.symbols), len(self.base.links)), before)
        self.assertNotIn(key, self.base.symbols)

    def test_a_new_meaning_resolves_its_current_symbols_and_former_names(self):
        change = write.Change(self.base, write.model_resolver(self.base), root=self.base.root)
        change.run(new("ram", self.LOCATION, name="probe_cell", evidence=[SPEC]))
        for reference in ("probe_cell/ram", "probe_cell", "probe-heron/ram", "probe-otter/ram",
                          self.LOCATION, f"{self.FREE:08x}"):
            with self.subTest(reference=reference):
                self.assertEqual(change.resolve(reference)[0].key, "probe_cell/ram")
        change.run(bind("probe_cell/ram", "jk00d:ffff0ff2", evidence=[SPEC]))
        for reference in ("jk00d:ffff0ff2", "probe_cell/ram/jk00d",
                          "probe_cell/ram/jk00d-ffff0ff2"):
            with self.subTest(reference=reference):
                meaning, symbol = change.resolve(reference)
                self.assertEqual(meaning.key, "probe_cell/ram")
                self.assertEqual(symbol.key, SymbolKey("jk00d", "ram", 0xffff0ff2))
        change.run(assign("probe_cell/ram/jk00d", {"width": 16}))
        self.assertEqual(change.resolve("jk00d:ffff0ff2")[1].props["width"], 16)

    def test_a_new_location_does_not_shadow_an_existing_kind(self):
        change = write.Change(self.base, write.model_resolver(self.base), root=self.base.root)
        location = f"7mfk:{TABLE_HOME:08x}"
        change.run(new("const", location, name="probe_literal", evidence=[SPEC]))
        with self.assertRaises(KbError) as caught:
            change.resolve(location)
        self.assertEqual(caught.exception.code, 4)
        self.assertIn("names 2 entities", str(caught.exception))

    def test_a_failed_batch_with_a_new_meaning_writes_no_files_or_graph(self):
        with mock.patch.object(write.lock, "held", return_value=contextlib.nullcontext()), \
                mock.patch.object(write.graph, "fresh", return_value=contextlib.nullcontext()), \
                mock.patch.object(write.compile, "build", return_value=self.base), \
                mock.patch.object(write, "graph_resolver", return_value=write.model_resolver(self.base)), \
                mock.patch.object(write.store, "write") as files, \
                mock.patch.object(write.graph, "sync_held") as graph:
            with self.assertRaises(KbError) as caught:
                write.apply([new("ram", self.LOCATION, name="probe_cell", evidence=[SPEC]),
                             assign("probe_cell/ram", {"not_a_key": 1})], root=self.base.root)
            self.assertEqual(caught.exception.code, 2)
            self.assertIn("op 2", str(caught.exception))
            files.assert_not_called()
            graph.assert_not_called()

    def test_an_unsupported_access_width_refuses_an_entire_batch_before_writes(self):
        build = compile.build

        def build_result(root, overlay=None):
            return self.base if overlay is None else build(root, overlay)

        for reference in ("probe_cell/ram", "probe_cell/ram/jk00d"):
            with self.subTest(reference=reference), \
                    mock.patch.object(write.lock, "held", return_value=contextlib.nullcontext()), \
                    mock.patch.object(write.graph, "fresh", return_value=contextlib.nullcontext()), \
                    mock.patch.object(write.compile, "build", side_effect=build_result), \
                    mock.patch.object(write, "graph_resolver", return_value=write.model_resolver(self.base)), \
                    mock.patch.object(write.store, "write") as files, \
                    mock.patch.object(write.graph, "sync_held") as graph:
                with self.assertRaises(KbError) as caught:
                    write.apply([
                        new("ram", self.LOCATION, name="probe_cell", evidence=[SPEC]),
                        bind("probe_cell/ram", "jk00d:ffff0ff2", evidence=[SPEC]),
                        assign(reference, {"width": 4}),
                    ], root=self.base.root)
                self.assertIn("width 4 of a ram must be 8, 16, or 32 bits", str(caught.exception))
                files.assert_not_called()
                graph.assert_not_called()

    @pytest.mark.slow
    def test_a_symbol_without_a_row_draws_its_generated_name(self):
        held = {key.address for key in self.base.symbols
                if (key.layout, key.kind) == ("7mfk", "fn")}
        rows = {row.key for row in self.base.names}
        address = next(address for address in sorted(self.base.functions["7mfk"])
                       if address not in held and ("7mfk", "fn", address) not in rows)
        location = f"7mfk:{address:08x}"
        change, texts, result = self.plan(new("fn", location,
                                              evidence=[{"kind": "l0", "at": location}]))
        [(path, text)] = texts.items()
        [entry] = tomllib.loads(text)["symbol"]
        self.assertRegex(entry["name"], vocab.GENERATED_NAME)
        self.assertEqual(path, store.path_of("fn", entry["name"]))
        self.assertEqual(result.meaning_of(SymbolKey("7mfk", "fn", address)).key,
                         f"{entry['name']}/fn")
        self.assertEqual(change.lines, [f"new {entry['name']}/fn/7mfk-{address:08x}: l0 at "
                                        f"{location}"])

    def test_new_starts_the_empty_file_of_a_designed_entity(self):
        change, texts, result = self.plan(new("feature", "probe_feature"))
        self.assertEqual(texts, {store.path_of("feature", "probe_feature"):
                                 store.render("feature", {})})
        self.assertIn(("feature", "probe_feature"), result.entities)
        self.assertEqual(change.lines, ["new probe_feature/feature"])

    def test_a_batch_starts_a_field_with_its_keys(self):
        started = new("field", "probe_coolant_raw")
        keys = {"signal": "temperatures/signal", "source": "coolant/ram", "origin": "ecu_ram",
                "width": 1, "signed": False}
        with self.assertRaises(KbError) as caught:
            self.plan(started)
        self.assertEqual(caught.exception.code, 3)
        self.assertIn("width None is no positive number of bytes", str(caught.exception))
        self.assertIn("op 1: no designed entity probe_coolant_raw/field", self.refused(
            assign("probe_coolant_raw/field", keys), started, code=5))
        change, texts, result = self.plan(started, assign("probe_coolant_raw/field", keys))
        self.assertEqual(texts, {store.path_of("field", "probe_coolant_raw"):
                                 store.render("field", keys)})
        self.assertEqual(result.entities[("field", "probe_coolant_raw")].props["width"], 1)
        self.assertEqual(change.lines, [
            "new probe_coolant_raw/field",
            "set probe_coolant_raw/field: origin, signal, signed, source, width"])

    def test_new_refuses_a_held_place_or_name_and_the_keys_of_the_other_form(self):
        symbol = new("ram", self.LOCATION, evidence=[SPEC])
        cases = [
            ({**symbol, "symbol": f"7mfk:{THROTTLE_HOME:08x}"}, 3,
             f"7mfk:{THROTTLE_HOME:08x} is {THROTTLE}/7mfk-{THROTTLE_HOME:08x}"),
            (new("tbl", f"7mfk:{TABLE_HOME:08x}", evidence=[SPEC]), 3,
             f"`kb rename {TABLE} <semantic-name>` names its meaning"),
            ({**symbol, "name": "throttle_runtime"}, 3, f"{THROTTLE} exists"),
            ({**symbol, "name": "Probe"}, 2, "'Probe' is no semantic name"),
            (new("ram", self.LOCATION), 2,
             "new needs the evidence of the identity of the symbol on its layout"),
            ({**symbol, "level": "sure"}, 2, "level 'sure'"),
            (new("feature", self.LOCATION), 2,
             "a feature is a designed entity; `kb new feature <slug>` starts one"),
            (new("ram", "probe_cell"), 2,
             "a ram meaning starts with a symbol: `kb new ram <layout>:<address>`"),
            (new("feature", "probe_feature", name="probe"), 2,
             "a designed entity takes its slug as its name"),
            (new("feature", "probe_feature", evidence=[SPEC], note="probe"), 2,
             "a designed entity takes no evidence, note"),
            (new("feature", "Probe"), 2, "'Probe' is no slug"),
            (new("feature", "map_switching"), 3, "map_switching/feature exists"),
            ({"cmd": "new", "kind": "ram"}, 2, "new takes a symbol <layout>:<address> or a slug"),
            ({**symbol, "slug": "probe_cell"}, 2, "new takes a symbol"),
            (new("widget", "probe_widget"), 2, "kind 'widget'; the kinds are"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))
        named = {**symbol, "name": "probe_cell"}
        self.assertIn(f"op 2: {self.LOCATION} starts a meaning earlier in this change",
                      self.refused(named, {**named, "name": "probe_store"}))
        self.assertIn(f"op 2: {store.path_of('ram', 'probe_cell').as_posix()} exists",
                      self.refused(named, {**named, "symbol": f"7mfk:{self.FREE + 1:08x}"}))


def merge(meaning, other, **keys):
    return {"cmd": "merge", "meaning": meaning, "other": other, **keys}


@pytest.mark.slow
class MergeTest(unittest.TestCase):
    """Merges over a base that splits the JK00C symbol of EVALUATOR out into the
    unnamed meaning CAPUCHIN, as the conversion of the targets of the knock
    margin latch stated it, and that adds a second file MARMOT of the symbol of
    the unnamed target FOX, as a second session would. The search from the 7mfk
    symbol of EVALUATOR finds the JK00C symbol and nothing on 1ND and 1ME3B."""

    EVALUATOR, CAPUCHIN, FOX, MARMOT = ("knock_slice_evaluator/fn", "vivid-capuchin/fn",
                                        "heavenly-fox/fn", "sturdy-marmot/fn")
    HOOK = store.path_of("hook", "knock_margin_latch")
    FILES = {name: store.path_of("fn", name.partition("/")[0])
             for name in (EVALUATOR, CAPUCHIN, FOX, MARMOT)}

    @classmethod
    def setUpClass(cls):
        paths = (cls.FILES[cls.EVALUATOR], cls.HOOK, cls.FILES[cls.FOX])
        cls.tree = {path: (repo.ROOT / path).read_text(encoding="utf-8") for path in paths}
        evaluator = tomllib.loads(cls.tree[cls.FILES[cls.EVALUATOR]])
        entry = next(entry for entry in evaluator["symbol"] if entry["layout"] == "jk00c")
        evaluator["symbol"].remove(entry)
        capuchin = {"symbol": [{"layout": "jk00c", "address": entry["address"],
                                "name": "vivid-capuchin", "evidence": [
                                    item for item in entry["evidence"] if item["kind"] == "l0"]}]}
        hook = tomllib.loads(cls.tree[cls.HOOK])
        link = next(link for link in hook["link"] if link["to"] == cls.EVALUATOR)
        item = next(item for item in link["evidence"] if item["at"].startswith("jk00c:"))
        link["evidence"].remove(item)
        hook["link"].append({"type": "target", "to": cls.CAPUCHIN, "evidence": [item]})
        fox = tomllib.loads(cls.tree[cls.FILES[cls.FOX]])
        marmot = {"symbol": [{**fox["symbol"][0], "name": "sturdy-marmot", "note": "probe"}]}
        cls.base = compile.build(repo.ROOT, {
            cls.FILES[cls.EVALUATOR]: store.render("fn", evaluator),
            cls.FILES[cls.CAPUCHIN]: store.render("fn", capuchin),
            cls.HOOK: store.render("hook", hook),
            cls.FILES[cls.MARMOT]: store.render("fn", marmot)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base))

    def change(self, *ops):
        change = write.Change(self.base, write.model_resolver(self.base))
        for number, op in enumerate(ops, 1):
            change.run(op, number)
        return change

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.change(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def test_a_merge_of_a_homologous_meaning_gives_the_files_of_the_tree(self):
        change, texts, result = self.plan(merge(self.EVALUATOR, self.CAPUCHIN))
        self.assertEqual(texts, {self.FILES[self.EVALUATOR]: self.tree[self.FILES[self.EVALUATOR]],
                                 self.FILES[self.CAPUCHIN]: None,
                                 self.HOOK: self.tree[self.HOOK]})
        symbol = result.symbols[SymbolKey("jk00c", "fn", 0x4B27C)]
        self.assertEqual(symbol.meaning.key, self.EVALUATOR)
        self.assertEqual(symbol.former, ("vivid-capuchin",))
        self.assertEqual(sorted(symbol.meaning.symbols), ["7mfk", "jk00c", "jk00d", "jk78c"])
        self.assertEqual(change.lines, [
            f"merge {self.CAPUCHIN} into {self.EVALUATOR}: jk00c:0004b27c function-match at "
            "jk00c:0004b27c to 7mfk:0004a238 count 1 value mnemonic; 1 reference rewritten"])
        self.assertIn("--- a/kb/fn/vivid-capuchin.toml\n+++ /dev/null\n", change.diff(texts))

    def test_a_merge_joins_the_files_of_one_meaning(self):
        meaning = self.base.meaning_of(SymbolKey("1me3b", "fn", 0x72920))
        self.assertEqual(meaning.key, self.MARMOT)
        change, texts, result = self.plan(merge(self.FOX, self.MARMOT))
        path = self.FILES[self.FOX]
        self.assertEqual(sorted(texts), [path, self.FILES[self.MARMOT]])
        self.assertIsNone(texts[self.FILES[self.MARMOT]])
        [entry] = tomllib.loads(texts[path])["symbol"]
        self.assertEqual((entry["name"], entry["note"], entry["former"]),
                         ("heavenly-fox", "probe", ["sturdy-marmot/fn/1me3b-00072920"]))
        self.assertEqual(entry["evidence"],
                         tomllib.loads(self.tree[path])["symbol"][0]["evidence"])
        self.assertEqual(result.meaning_of(SymbolKey("1me3b", "fn", 0x72920)).key, self.FOX)
        self.assertNotIn("the files hold one meaning; merge them",
                         {key[2] for key in write._issues(result)})
        self.assertEqual(change.lines, [
            f"merge {self.MARMOT} into {self.FOX}: kb/fn/sturdy-marmot.toml joins "
            "kb/fn/heavenly-fox.toml"])

    def test_a_merge_rewrites_the_references_to_the_other_name(self):
        texts = self.change(merge(self.MARMOT, self.FOX)).texts()
        self.assertIsNone(texts[self.FILES[self.FOX]])
        [entry] = tomllib.loads(texts[self.FILES[self.MARMOT]])["symbol"]
        self.assertEqual((entry["name"], entry["former"]),
                         ("sturdy-marmot", ["heavenly-fox/fn/1me3b-00072920"]))
        links = tomllib.loads(texts[self.HOOK])["link"]
        self.assertIn(self.MARMOT, [link["to"] for link in links])
        self.assertNotIn(self.FOX, [link["to"] for link in links])

    def test_merges_refuse_what_the_model_contradicts(self):
        self.assertIn(f"{self.EVALUATOR} has {self.EVALUATOR}/7mfk-0004a238 on 7mfk",
                      self.refused(merge(self.EVALUATOR, SELECTOR)))
        self.assertIn("the masked-match search from 7mfk:0004a238 finds no candidate on 1nd, "
                      "not 1nd:0006ea18; state the evidence",
                      self.refused(merge(self.EVALUATOR, "ruby-boobook/fn")))
        self.assertIn("op 2: kb/fn/vivid-capuchin.toml leaves the store in this change",
                      self.refused(merge(self.EVALUATOR, self.CAPUCHIN),
                                   merge(self.EVALUATOR, self.CAPUCHIN)))
        self.assertIn(f"{self.EVALUATOR} has a semantic name and {self.CAPUCHIN} a generated "
                      "one", self.refused(merge(self.CAPUCHIN, self.EVALUATOR), code=2))
        self.assertIn("is a fn meaning and throttle_runtime/ram a ram one",
                      self.refused(merge(self.EVALUATOR, THROTTLE), code=2))
        self.assertIn("name one meaning", self.refused(merge(self.CAPUCHIN, self.CAPUCHIN),
                                                       code=2))
        self.assertIn("join without evidence", self.refused(
            merge(self.FOX, self.MARMOT, evidence=[SPEC]), code=2))

    def test_a_rename_waits_for_the_merge_of_the_files_of_its_meaning(self):
        paths = ", ".join(self.FILES[name].as_posix() for name in (self.FOX, self.MARMOT))
        self.assertIn(f"{self.MARMOT} has 2 files, {paths}; `kb merge` joins them first",
                      self.refused(rename(self.MARMOT, "probe_routine")))


def assign(ref, keys=None, unset=None, layout=None):
    op = {"cmd": "set", "ref": ref, "keys": keys, "unset": unset, "layout": layout}
    return {key: value for key, value in op.items() if value is not None}


class SetTest(unittest.TestCase):
    """`set` over a base with the feature PROBE, whose target on JK00C holds
    a table of two keys."""

    PROBE = "probe_feature/feature"
    PROBE_FILE = store.path_of("feature", "probe_feature")
    INHIBIT_FILE = store.path_of("ram", "fuel_inhibit")
    INHIBIT_JK00C = "fuel_inhibit/ram/jk00c-ffff251f"

    @classmethod
    def setUpClass(cls):
        probe = {"title": "Probe", "target": [{"layout": "jk00c", "status": "planned",
                                                "basis": {"maps": "stock", "timing": "stock"}}]}
        cls.base = compile.build(repo.ROOT, {cls.PROBE_FILE: store.render("feature", probe)})

    def change(self, *ops):
        change = write.Change(self.base, write.model_resolver(self.base), root=self.base.root)
        for number, op in enumerate(ops, 1):
            change.run(op, number)
        return change

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.change(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def target(self, texts):
        [target] = tomllib.loads(texts[self.PROBE_FILE])["target"]
        return target

    @pytest.mark.slow
    def test_set_writes_the_bits_of_a_meaning_and_the_override_of_a_symbol(self):
        change, texts, result = write.plan([
            assign(INHIBIT, {"bit": [{"bit": 2, "name": "active", "level": "pattern"}]}),
            assign(INHIBIT, {"bit": [{"bit": 6, "name": "active"}], "note": "probe"},
                   layout="jk00c")], self.base, write.model_resolver(self.base))
        document = tomllib.loads(texts[self.INHIBIT_FILE])
        self.assertEqual(document["bit"], [{"bit": 2, "name": "active", "level": "pattern"}])
        entry = next(entry for entry in document["symbol"] if entry["layout"] == "jk00c")
        self.assertEqual((entry["bit"], entry["note"]), ([{"bit": 6, "name": "active"}], "probe"))
        overlay = {**self.base.overlay, **texts}
        self.assertEqual([targets.bit(INHIBIT, layout, "active", overlay=overlay)
                          for layout in ("7mfk", "jk00c")], [2, 6])
        symbol = result.symbols[SymbolKey("jk00c", "ram", 0xFFFF251F)]
        self.assertEqual(symbol.value("bit"), [{"bit": 6, "name": "active"}])
        self.assertEqual(change.lines, [f"set {INHIBIT}: bit",
                                        f"set {self.INHIBIT_JK00C}: bit, note"])

    def test_set_refuses_a_code_bit_without_its_own_evidence(self):
        with self.assertRaises(KbError) as caught:
            write.plan([assign(INHIBIT, {"bit": [{"bit": 2, "name": "active", "level": "code"}]})],
                       self.base, write.model_resolver(self.base), root=self.base.root)
        self.assertEqual(caught.exception.code, 3)
        self.assertIn("bit active: the bit level code lacks grounding", str(caught.exception))

    def test_tables_join_and_an_unset_key_leaves_no_empty_table(self):
        texts = self.change(assign(self.PROBE, {"basis": {"notes": "x", "maps": "native"}},
                                   layout="jk00c")).texts()
        self.assertEqual(self.target(texts)["basis"],
                         {"maps": "native", "timing": "stock", "notes": "x"})
        change = self.change(assign(self.PROBE, {"basis": {"notes": "x"}}, ["basis"],
                                    layout="jk00c"))
        self.assertEqual(self.target(change.texts())["basis"], {"notes": "x"})
        self.assertEqual(change.lines, [f"set {self.PROBE} on jk00c: basis.notes; unset basis"])
        texts = self.change(assign(self.PROBE, unset=["basis.maps", "basis.timing"],
                                   layout="jk00c")).texts()
        self.assertNotIn("basis", self.target(texts))

    def test_a_feature_takes_every_key_besides_its_targets(self):
        profiles = [{"name": "probe", "id": 6, "page_count": 11}]
        change = self.change(assign(self.PROBE, {"profiles": profiles, "pphi_hz": 20000000}))
        document = tomllib.loads(change.texts()[self.PROBE_FILE])
        self.assertEqual((document["profiles"], document["pphi_hz"], len(document["target"])),
                         (profiles, 20000000, 1))
        self.assertEqual(change.lines, [f"set {self.PROBE}: pphi_hz, profiles"])
        self.assertIn(f"set writes no target of {self.PROBE}; it writes every key besides "
                      "target", self.refused(assign(self.PROBE, {"target": []}), code=2))

    def test_set_refuses_keys_and_values_outside_its_schema(self):
        cases = [
            (assign(INHIBIT, {"symbol": []}), 2, f"set writes no symbol of {INHIBIT}"),
            (assign(INHIBIT, {"address": "ffff2520"}, layout="jk00c"), 2,
             f"set writes no address of {self.INHIBIT_JK00C}"),
            (assign(self.PROBE, unset=["layout"], layout="jk00c"), 2,
             f"set writes no layout of {self.PROBE} on jk00c"),
            (assign(INHIBIT, unset=["to_raw"]), 3, f"{INHIBIT} has no to_raw"),
            (assign(INHIBIT, {"title": "x"}, ["title"]), 2, "set writes and unsets title"),
            (assign(INHIBIT), 2, "set needs keys or unset"),
            (assign(INHIBIT, {"bit": [{"bit": 2, "evidence": [
                {"kind": "rom-bytes", "at": "7mfk:0"}]}]}), 2, "rom-bytes evidence needs value"),
            (assign(INHIBIT, {"bit": [{"bit": 2, "mask": 4}]}), 2, "bit takes no mask"),
            (assign(INHIBIT, {"bit": {"bit": 2}}), 2, "bit is an array of tables"),
            (assign(INHIBIT, {"level": "sure"}), 2, "level 'sure'; the levels are"),
            (assign("nothing/feature", {"title": "x"}), 5, "no designed entity nothing/feature"),
            (assign(self.PROBE, {"note": "x"}, layout="jk00d"), 5,
             f"{self.PROBE} has no target on jk00d"),
            (assign(INHIBIT, {"note": "x"}, layout="1nd"), 5, f"{INHIBIT} has no symbol on 1nd"),
            (assign(f"jk00c:ffff251f", {"note": "x"}, layout="jk00d"), 2,
             f"{self.INHIBIT_JK00C} lies on jk00c, not on jk00d"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))

    def test_set_refuses_a_quoted_key_and_names_the_nested_key_it_spells(self):
        cases = [
            (assign(self.PROBE, {"basis.timing": "native"}, layout="jk00c"),
             f'set writes no "basis.timing" of {self.PROBE} on jk00c; a key is bare, and the '
             "nested key basis.timing names a key of a table"),
            (assign(self.PROBE, {"basis": {"maps.x": "native"}}, layout="jk00c"),
             f'set writes no "maps.x" of {self.PROBE} on jk00c; a key is bare, and the nested '
             "key basis.maps.x names a key of a table"),
            (assign(INHIBIT, {"logparam.id": "x"}),
             f'set writes no "logparam.id" of {INHIBIT}; a key is bare, and the nested key '
             "logparam.id names a key of a table"),
            (assign(self.PROBE, {"basis": {"two words": "x"}}, layout="jk00c"),
             f'set writes no "two words" of {self.PROBE} on jk00c; a key is bare'),
        ]
        for op, message in cases:
            with self.subTest(op=op):
                self.assertEqual(self.refused(op, code=2), f"op 1: {message}")

    def test_a_target_takes_the_keys_of_every_target_and_those_its_feature_states(self):
        change = self.change(assign("can_telemetry/feature", {"mailbox_index": 26},
                                    layout="jk00c"),
                             assign(self.PROBE, {"note": "x", "basis": {"notes": "y"}},
                                    layout="jk00c"))
        self.assertEqual(change.lines, ["set can_telemetry/feature on jk00c: mailbox_index",
                                        f"set {self.PROBE} on jk00c: basis.notes, note"])
        message = self.refused(assign(self.PROBE, {"mailbox_index": 26}, layout="jk00c"),
                               code=2)
        self.assertEqual(message, f"op 1: set writes no mailbox_index of {self.PROBE} on "
                                  "jk00c; it writes status, note, basis, requires, unsupported; a new target "
                                  "key needs a declared key schema of the feature")
        message = self.refused(assign("can_telemetry/feature", {"mailbox_indx": 26},
                                      layout="jk00c"), code=2)
        self.assertIn("it writes status, note, basis, requires, ", message)
        self.assertIn(", mailbox_index, ", message)
        self.assertTrue(message.endswith("a new target key needs a declared key schema of the "
                                         "feature"))

    def test_assignments_are_toml_values_or_strings(self):
        self.assertEqual(write.parse_assignments(
            ["level=code", 'bit=[{bit = 7, name = "main"}]', "basis.maps=a b", "count=3",
             "note="]),
            ({"level": "code", "bit": [{"bit": 7, "name": "main"}], "basis": {"maps": "a b"},
              "count": 3}, ["note"]))
        for texts in (["level"], ["=x"], ["a..b=1"], ["a=1", "a.b=2"], ["a=1", "a=2"]):
            with self.subTest(texts=texts), self.assertRaises(KbError) as caught:
                write.parse_assignments(texts)
            self.assertEqual(caught.exception.code, 2)


def link(meaning, type_, to, cmd="link", **keys):
    return {"cmd": cmd, "meaning": meaning, "type": type_, "to": to, **keys}


class LinkTest(unittest.TestCase):
    """`link` and `unlink` over a base whose file of RPM states its reader
    link to MACHINE and one to KERNEL by the generated name of the 1ND symbol
    of KERNEL. RPM owns its reader link to BUILDER after the ledger conversion.
    The file of ALTERNATE states its axis link to AXIS in slot x and its
    reader link to ACCESSOR with the role accessor."""

    RPM, RPM_HOME, RPM_FILE = "rpm/ram", 0xFFFF11BC, store.path_of("ram", "rpm")
    MACHINE, BUILDER = "rev_fuel_cut_state_machine/fn", "idle_opening_area_builder/fn"
    KERNEL, KERNEL_1ND = "uptight-tiger/fn", "cryptic-heron/fn"
    ALTERNATE, AXIS = "fuel_compensation_alternate/tbl", "fascinating-hog/axis"
    ACCESSOR = "asparagus-scallop/fn"

    @classmethod
    def setUpClass(cls):
        text = (repo.ROOT / cls.RPM_FILE).read_text(encoding="utf-8")
        cls.held = tomllib.loads(text)
        document = tomllib.loads(text)
        document["link"].append({"type": "reader", "to": cls.KERNEL_1ND})
        cls.base = compile.build(repo.ROOT, {cls.RPM_FILE: store.render("ram", document)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base), root=self.base.root)

    def change(self, *ops):
        change = write.Change(self.base, write.model_resolver(self.base), root=self.base.root)
        for number, op in enumerate(ops, 1):
            change.run(op, number)
        return change

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.change(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def links(self, texts, to):
        return [item for item in tomllib.loads(texts[self.RPM_FILE])["link"] if item["to"] == to]

    @pytest.mark.slow
    def test_link_extends_the_converted_file_without_losing_its_facts(self):
        path = store.path_of("fn", "accelerator_pedal_pair_selector")
        held = store.load(repo.ROOT, path)
        change, texts, result = self.plan(link(SELECTOR, "depends", THROTTLE, keys={
            "role": "input", "relies": "structure"}, evidence=[SPEC]))
        self.assertEqual(list(texts), [path])
        wanted = {**held, "link": [*held.get("link", ()), {"type": "depends", "to": THROTTLE,
                  "relies": "structure", "role": "input", "evidence": [SPEC]}]}
        self.assertEqual(texts[path], store.render("fn", wanted))
        meaning = result.meaning_of(SymbolKey("7mfk", "fn", SELECTOR_HOME))
        [found] = [item for item in meaning.links
                   if item.type == "depends" and item.to.key == THROTTLE]
        self.assertEqual(found.props.get("relies"), "structure")
        self.assertIn(path.as_posix(), found.sources)
        self.assertEqual(change.lines, [f"link {SELECTOR} depends {THROTTLE}: spec path "
                                        "tools/kb/SPEC.md"])

    def test_link_refuses_reliance_on_a_missing_contract(self):
        with self.assertRaises(KbError) as caught:
            self.plan(link(SELECTOR, "depends", THROTTLE, keys={
                "role": "input", "relies": "contract"}, evidence=[SPEC]))
        self.assertEqual(caught.exception.code, 3)
        self.assertIn("which declares no contract_level", str(caught.exception))

    def test_link_joins_the_keys_and_the_evidence_of_the_held_link(self):
        change, texts, _ = self.plan(
            link(self.RPM, "reader", self.MACHINE, keys={"layouts": ["1nd"]}),
            link(self.RPM, "reader", self.MACHINE, keys={"layouts": ["1me3b"]}, evidence=[SPEC]))
        [held] = [item for item in self.held["link"] if item["to"] == self.MACHINE]
        self.assertEqual(self.links(texts, self.MACHINE), [
            {**held, "layouts": ["1nd", "1me3b"], "evidence": [*held["evidence"], SPEC]}])
        self.assertEqual(change.lines, [
            f"link {self.RPM} reader {self.MACHINE}: no evidence",
            f"link {self.RPM} reader {self.MACHINE}: spec path tools/kb/SPEC.md"])

    def test_a_link_names_its_target_by_any_of_its_names(self):
        _, texts, result = self.plan(link(self.RPM, "reader", self.KERNEL, evidence=[SPEC]))
        self.assertEqual(self.links(texts, self.KERNEL_1ND),
                         [{"type": "reader", "to": self.KERNEL_1ND, "evidence": [SPEC]}])
        rpm = result.meaning_of(SymbolKey("7mfk", "ram", self.RPM_HOME))
        self.assertIn(self.KERNEL, [item.to.key for item in rpm.links if item.type == "reader"])
        texts = self.change(link(self.RPM, "reader", self.KERNEL, cmd="unlink")).texts()
        self.assertEqual(self.links(texts, self.KERNEL_1ND), [])

    def test_unlink_removes_the_link_that_its_keys_choose(self):
        change, texts, result = self.plan(link(self.RPM, "reader", self.MACHINE, cmd="unlink"))
        self.assertEqual(self.links(texts, self.MACHINE), [])
        rpm = result.meaning_of(SymbolKey("7mfk", "ram", self.RPM_HOME))
        self.assertNotIn(self.MACHINE, [item.to.key for item in rpm.links])
        self.assertEqual(change.lines, [f"unlink {self.RPM} reader {self.MACHINE}"])
        axis = link(self.ALTERNATE, "axis", self.AXIS, keys={"slot": "y"})
        change, texts, _ = self.plan(axis, {**axis, "cmd": "unlink"})
        self.assertEqual(texts, {})
        self.assertEqual(change.lines, [f"link {self.ALTERNATE} axis {self.AXIS}: no evidence",
                                        f"unlink {self.ALTERNATE} axis {self.AXIS}"])
        self.assertIn(f"op 2: {self.ALTERNATE} has 2 axis links to {self.AXIS} (slot = 'x'; "
                      "slot = 'y'); slot or offset chooses one",
                      self.refused(axis, {**axis, "cmd": "unlink", "keys": {}}, code=4))

    def test_unlink_withdraws_converted_dependency_tokens_at_both_claiming_ends(self):
        self.assertNotEqual(self.base.root, repo.ROOT)
        before = ledger_projection.render(self.base)
        _, _, result = self.plan(
            link(self.RPM, "reader", self.BUILDER, cmd="unlink"),
            link(self.RPM, "writer", "coherent_snapshot/fn", cmd="unlink"))
        after = ledger_projection.render(result)
        builder, _ = write.model_resolver(self.base)(self.BUILDER)
        for registry, address, token in (
                ("funcs", builder.symbols["7mfk"].address, "indexed_by:ffff11bc@structural"),
                ("vars", self.RPM_HOME, "writes:00020dfe@structural"),
                ("funcs", 0x20DFE, "writes:ffff11bc@structural")):
            path = f"defs/JK08A.{registry}.csv"
            old = {row["addr"]: row for row in csv.DictReader(io.StringIO(before[path]))}
            new = {row["addr"]: row for row in csv.DictReader(io.StringIO(after[path]))}
            key = f"{address:08x}"
            with self.subTest(registry=registry, address=key):
                self.assertIn(token, old[key]["evidence"])
                self.assertNotIn(token, new[key]["evidence"])

    @pytest.mark.slow
    def test_a_write_refuses_an_evidence_index_that_its_ledger_still_selects(self):
        with self.assertRaises(KbError) as caught:
            self.plan(assign(self.RPM, {"evidence": [SPEC]}, layout="7mfk"))
        self.assertEqual(caught.exception.code, 3)
        self.assertIn("ledgers:", str(caught.exception))
        self.assertIn("invalid evidence selection", str(caught.exception))

    @pytest.mark.slow
    def test_unlink_can_remove_a_word_base_relation_to_its_own_group(self):
        word = self.base.symbols[SymbolKey("7mfk", "ram", 0xFFFF120E)]
        _, _, result = self.plan(link(word.meaning.key, "base", word.meaning.key,
                                     keys={"offset": 0x12}, cmd="unlink"))
        found = result.meaning_of(word.key)
        self.assertFalse(any(item.owner is found and item.to is found
                             and item.type == "base" and item.offset == 0x12
                             for item in result.links))
        ledger_projection.render(result)

    def test_links_refuse_what_the_schema_or_the_files_contradict(self):
        machine = link(self.RPM, "reader", self.MACHINE)
        cases = [
            (machine, 3, f"{self.RPM} has this reader link to {self.MACHINE}"),
            (link(self.ALTERNATE, "reader", self.ACCESSOR, keys={"role": "consumer"}), 3,
             f"the reader link of {self.ALTERNATE} to {self.ACCESSOR} holds role = 'accessor'; "
             "`kb unlink` removes it"),
            (link(self.RPM, "axis", self.AXIS), 2, "the axis type joins tbl to axis, not ram to "
             "axis"),
            (link(self.RPM, "depends", THROTTLE), 2, "a depends link states its role"),
            (link(self.RPM, "reader", self.RPM), 2, "a link joins two meanings"),
            (link(self.RPM, "calls", self.MACHINE), 2, "link type 'calls'; the types are"),
            ({**machine, "keys": {"relies": ["contract"]}}, 2,
             "relies ['contract']; the values are"),
            ({**machine, "keys": {"via": "x"}}, 2, "via is an array"),
            ({**machine, "keys": {"title": "x"}}, 2, "a link takes no title here"),
            ({**machine, "keys": {"layouts": ["k9"]}}, 5, "unknown layout 'k9'"),
            (link(self.RPM, "reader", self.ACCESSOR, cmd="unlink"), 5,
             f"{self.RPM} has no reader link to {self.ACCESSOR}"),
            ({**machine, "cmd": "unlink", "keys": {"role": "consumer"}}, 2,
             "a link takes no role here; the keys are slot, offset"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))


def move(symbol, to, **keys):
    return {"cmd": "move", "symbol": symbol, "to": to, **keys}


@pytest.mark.slow
class MoveTest(unittest.TestCase):
    """`move` over a base whose file states the JK78C symbol of THROTTLE two
    bytes above the counterpart that the search from its 7mfk symbol finds,
    with a note that cites the symbol."""

    WRONG = THROTTLE_JK78C + 2
    FILE = store.path_of("ram", "throttle_runtime")

    @classmethod
    def setUpClass(cls):
        document = tomllib.loads((repo.ROOT / cls.FILE).read_text(encoding="utf-8"))
        document["symbol"].append({
            "layout": "jk78c", "address": f"{cls.WRONG:08x}",
            "note": f"probe of [[{THROTTLE}/jk78c-{cls.WRONG:08x}]]",
            "evidence": [{**TABLE_EVIDENCE, "at": "jk78c:0002ffb8", "to": "7mfk:0002ce62",
                          "value": 12}]})
        cls.base = compile.build(repo.ROOT, {cls.FILE: store.render("ram", document)})

    def refused(self, *ops, code=3):
        change = write.Change(self.base, write.model_resolver(self.base))
        with self.assertRaises(KbError) as caught:
            for op in ops:
                change.run(op)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def test_move_corrects_the_address_with_the_evidence_of_the_search(self):
        home = self.base.symbols[SymbolKey("7mfk", "ram", THROTTLE_HOME)]
        found = match.search(self.base, home, "jk78c").candidates[THROTTLE_JK78C].evidence
        evidence = write.Change._stored(found)
        change, texts, result = write.plan(
            [move(f"jk78c:{self.WRONG:08x}", f"jk78c:{THROTTLE_JK78C:08x}")], self.base,
            write.model_resolver(self.base))
        old, new = (f"{THROTTLE}/jk78c-{address:08x}" for address in (self.WRONG, THROTTLE_JK78C))
        entry = next(entry for entry in tomllib.loads(texts[self.FILE])["symbol"]
                     if entry["layout"] == "jk78c")
        self.assertEqual(entry, {"layout": "jk78c", "address": f"{THROTTLE_JK78C:08x}",
                                 "former": [old], "note": f"probe of [[{new}]]",
                                 "evidence": [evidence]})
        symbol = result.symbols[SymbolKey("jk78c", "ram", THROTTLE_JK78C)]
        self.assertEqual((symbol.meaning.key, symbol.former), (THROTTLE, ("throttle_runtime",)))
        self.assertNotIn(SymbolKey("jk78c", "ram", self.WRONG), result.symbols)
        self.assertEqual(change.lines, [f"move {old} to jk78c:{THROTTLE_JK78C:08x}: "
                                        f"{write.summary(evidence)}; 1 reference rewritten"])

    def test_moves_refuse_what_the_model_contradicts(self):
        wrong = f"jk78c:{self.WRONG:08x}"
        cases = [
            (move(THROTTLE, f"jk78c:{THROTTLE_JK78C:08x}"), 2, f"names the meaning {THROTTLE}"),
            (move(wrong, "jk00c:ffff17e8"), 2, "lies on jk78c, not on jk00c; a symbol moves "
             "within its layout"),
            (move(wrong, wrong), 2, f"lies at {wrong}"),
            (move(wrong, "jk78c:ffff107b"), 3,
             "jk78c:ffff107b is absolute_throttle/ram/jk78c-ffff107b; `kb merge`"),
            (move(wrong, "jk78c:ffff17a8"), 3,
             f"finds jk78c:{THROTTLE_JK78C:08x} on jk78c, not jk78c:ffff17a8; state the evidence"),
            (move(f"7mfk:{THROTTLE_HOME:08x}", "7mfk:ffff1797"), 2,
             f"is the home symbol of {THROTTLE}"),
            (move(wrong, f"jk78c:{THROTTLE_JK78C:08x}", level="sure"), 2, "level 'sure'"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))


def rename(meaning, name):
    return {"cmd": "rename", "meaning": meaning, "name": name}


class RenameMeaningTest(unittest.TestCase):
    """`rename` over the working tree, where TABLE has a file with symbols
    on three layouts and the map switching feature cites THROTTLE."""

    @classmethod
    def setUpClass(cls):
        cls.base = compile.cached(repo.ROOT)

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base), root=self.base.root)

    def refused(self, *ops, code=3, base=None):
        base = base or self.base
        change = write.Change(base, write.model_resolver(base), root=base.root)
        with self.assertRaises(KbError) as caught:
            for number, op in enumerate(ops, 1):
                change.run(op, number)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def test_rename_names_an_unnamed_meaning_and_keeps_its_generated_names_as_former_references(
            self):
        meaning = self.base.meaning_of(SymbolKey("7mfk", "tbl", TABLE_HOME))
        change, texts, result = self.plan(rename(TABLE, "probe_table"))
        self.assertIsNone(texts[store.path_of("tbl", "astute-toad")])
        document = tomllib.loads(texts[store.path_of("tbl", "probe_table")])
        self.assertNotIn("former", document)
        self.assertEqual(
            {entry["layout"]: (entry.get("name"), entry["former"]) for entry in document["symbol"]},
            {layout: (None, [f"{symbol.generated}/tbl/{layout}-{symbol.address:08x}"])
             for layout, symbol in meaning.symbols.items()})
        home = result.symbols[SymbolKey("7mfk", "tbl", TABLE_HOME)]
        self.assertEqual((home.meaning.key, home.former), ("probe_table/tbl", ("astute-toad",)))
        self.assertRegex(change.lines[0],
                         rf"^rename {TABLE} to probe_table/tbl; \d+ references? rewritten$")

    @pytest.mark.slow
    def test_rename_of_a_named_meaning_keeps_its_name_as_a_former_name(self):
        path = store.path_of("ram", "throttle_runtime")
        held = tomllib.loads((repo.ROOT / path).read_text(encoding="utf-8"))
        change, texts, result = self.plan(rename(THROTTLE, "throttle_state"))
        self.assertIsNone(texts[path])
        document = tomllib.loads(texts[store.path_of("ram", "throttle_state")])
        self.assertEqual(document["former"], ["throttle_runtime"])
        self.assertEqual([entry["former"] for entry in document["symbol"]], [
            [f"{THROTTLE}/{entry['layout']}-{entry['address']}", *entry.get("former", ())]
            for entry in held["symbol"]])
        meaning = result.meaning_of(SymbolKey("7mfk", "ram", THROTTLE_HOME))
        self.assertEqual(meaning.key, "throttle_state/ram")
        self.assertIn("throttle_runtime", [name for name, _, _ in meaning.other_names])
        feature = texts[store.path_of("feature", "map_switching")]
        self.assertNotIn(THROTTLE, feature)
        self.assertIn("throttle_state/ram", feature)
        self.assertRegex(change.lines[0],
                         rf"^rename {THROTTLE} to throttle_state/ram; \d+ references rewritten$")

    @pytest.mark.slow
    def test_rename_of_a_converted_curated_function_projects_its_name_and_reserves_the_former(self):
        before = ledger_projection.render(self.base)["tools/ghidra/symbols/7mfk.csv"]
        _, _, result = self.plan(rename(SELECTOR, "probe_selector"))
        after = ledger_projection.render(result)["tools/ghidra/symbols/7mfk.csv"]
        self.assertEqual(after, before.replace(
            f"{SELECTOR_HOME:08x},accelerator_pedal_pair_selector,",
            f"{SELECTOR_HOME:08x},probe_selector,"))
        meaning = result.meaning_of(SymbolKey("7mfk", "fn", SELECTOR_HOME))
        self.assertEqual(meaning.key, "probe_selector/fn")
        self.assertIn("accelerator_pedal_pair_selector",
                      [name for name, _, _ in meaning.other_names])

    @pytest.mark.slow
    def test_rename_preserves_a_word_base_relation_to_its_own_group(self):
        word = self.base.symbols[SymbolKey("7mfk", "ram", 0xFFFF120E)]
        before = ledger_projection.render(self.base)
        _, _, result = self.plan(rename(word.meaning.key, "probe_base_word"))
        found = result.meaning_of(word.key)
        [base] = [item for item in result.links if item.owner is found and item.to is found
                  and item.type == "base" and item.offset == 0x12]
        self.assertEqual(base.offset, 0x12)
        self.assertEqual(ledger_projection.render(result), before)

    def test_renames_refuse_the_names_that_the_model_holds(self):
        cases = [
            (rename(THROTTLE, "throttle_runtime"), 2, f"{THROTTLE} has the name throttle_runtime"),
            (rename(THROTTLE, "fuel_inhibit"), 3, f"{INHIBIT} exists"),
            (rename(THROTTLE, "Throttle"), 2, "'Throttle' is no semantic name"),
            (rename("nothing/ram", "probe_cell"), 5, "no meaning 'nothing/ram'"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))
        # A former name of INHIBIT and a former reference of its JK00C symbol.
        path = store.path_of("ram", "fuel_inhibit")
        document = tomllib.loads((self.base.root / path).read_text(encoding="utf-8"))
        document["former"] = ["throttle_cell"]
        entry = next(entry for entry in document["symbol"] if entry["layout"] == "jk00c")
        entry["former"] = [f"throttle_probe/ram/jk00c-{entry['address']}"]
        base = compile.build(self.base.root, {path: store.render("ram", document)})
        self.assertIn(f"throttle_cell is a former name of {INHIBIT} in {path.as_posix()}",
                      self.refused(rename(THROTTLE, "throttle_cell"), base=base))
        self.assertIn(f"throttle_probe is a former name of {INHIBIT}/jk00c-{entry['address']} "
                      f"in {path.as_posix()}",
                      self.refused(rename(THROTTLE, "throttle_probe"), base=base))

    def test_a_batch_renames_a_meaning_after_its_other_operations(self):
        renamed = rename(THROTTLE, "throttle_state")
        gate = (f"op 2: {THROTTLE} takes the name throttle_state/ram earlier in this change; a "
                "batch renames a meaning after its other operations")
        self.assertIn(gate, self.refused(renamed, assign(THROTTLE, {"note": "probe"})))
        self.assertIn(gate, self.refused(renamed, link("rpm/ram", "depends", THROTTLE,
                                                       keys={"role": "input"})))
        _, texts, _ = self.plan(assign(THROTTLE, {"note": "probe"}), renamed)
        self.assertEqual(tomllib.loads(texts[store.path_of("ram", "throttle_state")])["note"],
                         "probe")


@pytest.mark.slow
class MoveMeaningTest(unittest.TestCase):
    """`move` of a symbol into another meaning over a base whose file of
    INHIBIT states the JK78C counterpart of THROTTLE, which the search from
    the 7mfk symbol of THROTTLE finds, with a note that cites it. WRAPPER and
    ACCESSOR are unnamed functions: WRAPPER has five symbols, and ACCESSOR has
    one on JK78C."""

    SYMBOL = f"jk78c:{THROTTLE_JK78C:08x}"
    WRONG = f"{INHIBIT}/jk78c-{THROTTLE_JK78C:08x}"
    INHIBIT_FILE = store.path_of("ram", "fuel_inhibit")
    THROTTLE_FILE = store.path_of("ram", "throttle_runtime")
    WRAPPER, WRAPPER_JK00C, ACCESSOR = "amusing-ara/fn", 0x26C84, "asparagus-scallop/fn"

    @classmethod
    def setUpClass(cls):
        document = tomllib.loads((repo.ROOT / cls.INHIBIT_FILE).read_text(encoding="utf-8"))
        document["symbol"].append({"layout": "jk78c", "address": f"{THROTTLE_JK78C:08x}",
                                   "evidence": [SPEC]})
        document["note"] = f"probe of [[{cls.WRONG}]] and [[{INHIBIT}/jk78c]]"
        cls.base = compile.build(repo.ROOT, {cls.INHIBIT_FILE: store.render("ram", document)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base))

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.plan(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def test_move_joins_a_symbol_with_the_meaning_whose_search_finds_it(self):
        home = self.base.symbols[SymbolKey("7mfk", "ram", THROTTLE_HOME)]
        found = match.search(self.base, home, "jk78c").candidates[THROTTLE_JK78C].evidence
        evidence = write.Change._stored(found)
        change, texts, result = self.plan(move(self.SYMBOL, THROTTLE))
        self.assertEqual(sorted(texts), [self.INHIBIT_FILE, self.THROTTLE_FILE])
        inhibit = tomllib.loads(texts[self.INHIBIT_FILE])
        self.assertNotIn("jk78c", [entry["layout"] for entry in inhibit["symbol"]])
        self.assertEqual(inhibit["note"], f"probe of [[{THROTTLE}/jk78c-{THROTTLE_JK78C:08x}]] "
                                          f"and [[{THROTTLE}/jk78c]]")
        entry = next(entry for entry in tomllib.loads(texts[self.THROTTLE_FILE])["symbol"]
                     if entry["layout"] == "jk78c")
        self.assertEqual(entry, {"layout": "jk78c", "address": f"{THROTTLE_JK78C:08x}",
                                 "former": [self.WRONG], "evidence": [evidence]})
        symbol = result.symbols[SymbolKey("jk78c", "ram", THROTTLE_JK78C)]
        self.assertEqual((symbol.meaning.key, symbol.former), (THROTTLE, ("fuel_inhibit",)))
        self.assertNotIn("jk78c", result.meaning_of(SymbolKey("7mfk", "ram", INHIBIT_HOME)).symbols)
        self.assertEqual(change.lines, [f"move {self.WRONG} to {THROTTLE}: "
                                        f"{write.summary(evidence)}; 2 references rewritten"])

    def test_a_symbol_keeps_its_generated_name_in_an_unnamed_meaning(self):
        key = SymbolKey("jk00c", "fn", self.WRAPPER_JK00C)
        name = self.base.symbols[key].generated
        change, texts, result = self.plan(move(key.location, self.ACCESSOR, evidence=[SPEC]))
        target = tomllib.loads(texts[store.path_of("fn", "asparagus-scallop")])
        self.assertEqual(target["home"], "jk78c")
        self.assertIn({"layout": "jk00c", "address": f"{self.WRAPPER_JK00C:08x}", "name": name,
                       "evidence": [SPEC]}, target["symbol"])
        wrapper = tomllib.loads(texts[store.path_of("fn", "amusing-ara")])
        self.assertNotIn("jk00c", [entry["layout"] for entry in wrapper["symbol"]])
        self.assertEqual((result.meaning_of(key).key, result.symbols[key].generated),
                         (self.ACCESSOR, name))
        self.assertEqual(change.lines, [f"move {name}/fn/jk00c-{self.WRAPPER_JK00C:08x} to "
                                        f"{self.ACCESSOR}: spec path tools/kb/SPEC.md"])

    def test_a_move_that_the_compiled_model_undoes_is_refused(self):
        change = write.Change(self.base, write.model_resolver(self.base))
        change.run(move(self.SYMBOL, THROTTLE, evidence=[SPEC]))
        [expected] = change.expected
        self.assertIn(f"move {self.WRONG} to {THROTTLE}: the compiled model does not join the "
                      f"symbol with {THROTTLE} alone; `kb raw {self.WRONG}` shows the registry "
                      "rows that state it", expected(self.base))
        # A registry name of the symbol that names the target in the result.
        throttle = self.base.meaning_of(SymbolKey("7mfk", "ram", THROTTLE_HOME))
        inhibit = self.base.meaning_of(SymbolKey("7mfk", "ram", INHIBIT_HOME))
        joined = {SymbolKey("jk78c", "ram", THROTTLE_JK78C),
                  *(symbol.key for symbol in throttle.symbols.values())}
        renamed = Meaning("ram", name="throttle_state", semantic=True)
        result = mock.Mock(meaning_of=lambda key: renamed if key in joined else inhibit)
        self.assertIn(f"the compiled model names the meanings throttle_state/ram and {INHIBIT}",
                      expected(result))
        with mock.patch.object(write.compile, "build", return_value=self.base):
            message = self.refused(move(self.SYMBOL, THROTTLE, evidence=[SPEC]))
        self.assertIn("the change contradicts 1 of its operations; nothing is written", message)

    def test_moves_into_a_meaning_refuse_what_the_model_contradicts(self):
        alternate = next(meaning for meaning in self.base.meanings
                         if meaning.key == "fuel_compensation_alternate/tbl")
        wrapper = f"jk00c:{self.WRAPPER_JK00C:08x}"
        cases = [
            (move(self.SYMBOL, INHIBIT), 2, f"{self.WRONG} is a symbol of {INHIBIT}"),
            (move(self.SYMBOL, "absolute_throttle/ram"), 3, "absolute_throttle/ram has "
             "absolute_throttle/ram/jk78c-ffff107b on jk78c; `kb move` corrects a wrong symbol"),
            (move(self.SYMBOL, SELECTOR), 2,
             f"{self.WRONG} is a ram symbol and {SELECTOR} a fn meaning"),
            (move("jk78c:ffff1084", THROTTLE), 3, "cocky-quetzal/ram/jk78c-ffff1084 is the only "
             "symbol of cocky-quetzal/ram; `kb merge` joins the two meanings"),
            (move("7mfk:00026100", "fuel_cut_coordinator/fn"), 3,
             f"{self.WRAPPER}/7mfk-00026100 is the home symbol of {self.WRAPPER} and gives its "
             f"name; `kb rename {self.WRAPPER} <semantic-name>` names the meaning first"),
            (move(alternate.symbols["jk78c"].key.location, "able-bison/tbl"), 3,
             f"the home of {alternate.key} is jk78c; `kb set {alternate.key} home=` unsets it "
             "first"),
            (move(self.SYMBOL, THROTTLE, level="sure"), 2, "level 'sure'"),
            (move(wrapper, self.ACCESSOR), 3, f"on jk00c, not {wrapper}; state the evidence"),
        ]
        for op, code, message in cases:
            with self.subTest(op=op):
                self.assertIn(message, self.refused(op, code=code))
        self.assertIn(f"op 2: {THROTTLE} takes the name throttle_state/ram earlier in this change",
                      self.refused(rename(THROTTLE, "throttle_state"), move(self.SYMBOL, THROTTLE)))


class RenameTest(unittest.TestCase):
    def test_relocated_references_name_the_new_address(self):
        document = {"to": "x/ram/jk78c-ffff450c", "note": "[[x/ram/jk78c-ffff450c]] and "
                    "[[x/ram/jk78c]]", "former": ["x/ram/jk78c-ffff450c"],
                    "evidence": [{"kind": "l0", "to": "jk78c:ffff450c"}]}
        found, count = write.relocated(document, {"x/ram/jk78c-ffff450c": "x/ram/jk78c-ffff450b"})
        self.assertEqual(count, 2)
        self.assertEqual(found, {**document, "to": "x/ram/jk78c-ffff450b",
                                 "note": "[[x/ram/jk78c-ffff450b]] and [[x/ram/jk78c]]"})

    def test_references_and_citations_to_the_other_names_name_the_target(self):
        document = {"to": "gentle-otter/fn", "via": ["gentle-otter/fn/jk00c"],
                    "note": "[[gentle-otter/fn]], [[gentle-otter]], and [[gentle-otter/ram]]",
                    "former": ["gentle-otter/fn/jk00c-00040000"], "name": "gentle-otter",
                    "evidence": [{"kind": "l0", "to": "gentle-otter/fn/jk00c"}],
                    "other": "gentle-otter/ram"}
        found, count = write.renamed(document, {"gentle-otter"}, "fn", "knock_function")
        self.assertEqual(count, 5)
        self.assertEqual(found, {
            **document, "to": "knock_function/fn", "via": ["knock_function/fn/jk00c"],
            "note": "[[knock_function/fn]], [[knock_function]], and [[gentle-otter/ram]]",
            "evidence": [{"kind": "l0", "to": "knock_function/fn/jk00c"}]})

    def test_links_of_one_key_that_agree_join(self):
        first = {"type": "target", "to": "x/fn", "note": "one",
                 "evidence": [{"kind": "l0", "at": "jk00d:1"}]}
        second = {"type": "target", "to": "x/fn", "evidence": [{"kind": "l0", "at": "jk00c:1"}]}
        other = {"type": "target", "to": "x/fn", "note": "another",
                 "evidence": [{"kind": "l0", "at": "jk78c:1"}]}
        self.assertEqual(write.joined_links([first, second, other]), [
            {"type": "target", "to": "x/fn", "note": "one",
             "evidence": [{"kind": "l0", "at": "jk00c:1"}, {"kind": "l0", "at": "jk00d:1"}]},
            other])


class HomeTest(unittest.TestCase):
    def test_a_symbol_that_would_move_the_home_of_an_unnamed_meaning_pins_it(self):
        meaning = Meaning("fn", symbols={"jk00d": object()})
        document = {}
        write.Change._keep_home(meaning, ["jk78c"], document)
        self.assertEqual(document, {})
        write.Change._keep_home(meaning, ["jk00c"], document)
        self.assertEqual(document, {"home": "jk00d"})
        document = {}
        write.Change._keep_home(meaning, ["jk78c", "7mfk"], document)
        self.assertEqual(document, {"home": "jk00d"})


class OverlayTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        for name in ("kept", "removed"):
            path = self.root / store.path_of("ram", name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(store.render("ram", {"title": name}), encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def test_an_overlay_adds_replaces_and_removes_files(self):
        overlay = {store.path_of("ram", "added"): 'title = "added"\n',
                   store.path_of("ram", "kept"): 'title="kept"\n',
                   store.path_of("ram", "removed"): None}
        self.assertEqual([name for _, name, _ in store.files(self.root, overlay)],
                         ["added", "kept"])
        self.assertEqual(store.load(self.root, store.path_of("ram", "added"), overlay),
                         {"title": "added"})
        self.assertEqual([issue.subject for issue in store.canonical(self.root, overlay)],
                         ["kept/ram"])
        self.assertEqual(store.canonical(self.root), [])
        with self.assertRaises(FileNotFoundError):
            store.load(self.root, store.path_of("ram", "removed"), overlay)

    def test_an_overlay_replaces_the_names(self):
        text = "layout,kind,address,name,former\n7mfk,ram,ffff1000,gentle-otter,brisk-lynx\n"
        self.assertEqual(names.read(self.root, {names.PATH: text}),
                         [names.Row("7mfk", "ram", 0xFFFF1000, "gentle-otter", ("brisk-lynx",))])
        self.assertEqual(names.read(self.root), [])


class ArgumentsTest(unittest.TestCase):
    def test_evidence_is_a_toml_inline_table(self):
        self.assertEqual(write.parse_evidence('kind = "l0", at = "7mfk:0004e070"'),
                         {"kind": "l0", "at": "7mfk:0004e070"})
        self.assertEqual(write.parse_evidence('{kind = "spec", key = "x"}'),
                         {"kind": "spec", "key": "x"})
        with self.assertRaises(KbError) as caught:
            write.parse_evidence("kind = l0")
        self.assertEqual(caught.exception.code, 2)

    def test_a_batch_holds_op_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ops.toml"
            path.write_text('[[op]]\ncmd = "absent"\nmeaning = "x/ram"\nlayout = "1nd"\n\n'
                            '[[op.evidence]]\nkind = "spec"\nkey = "y"\n', encoding="utf-8")
            self.assertEqual(write.read_batch(path), [{
                "cmd": "absent", "meaning": "x/ram", "layout": "1nd",
                "evidence": [{"kind": "spec", "key": "y"}]}])
            path.write_text('title = "x"\n', encoding="utf-8")
            with self.assertRaises(KbError) as caught:
                write.read_batch(path)
            self.assertEqual(caught.exception.code, 2)

    def test_the_commands_pass_their_operations_to_apply(self):
        stub = write.Change(mock.Mock(names=[]), None)
        stub.lines = ["bind x"]
        path = Path("kb/ram/x.toml")
        with mock.patch.object(write, "apply", return_value=(stub, {path: "a\n"})) as applied:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["bind", "x/ram", "jk00c:ffff1000", "--from", "7mfk",
                                 "--evidence", 'kind = "l0", at = "jk00c:00040000"'])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "kb/ram/x.toml: written\nbind x\n")
        ops = applied.call_args.args[0]
        self.assertEqual(ops, [{"cmd": "bind", "meaning": "x/ram", "symbol": "jk00c:ffff1000",
                                "evidence": [{"kind": "l0", "at": "jk00c:00040000"}],
                                "from": "7mfk", "level": None, "note": None}])
        self.assertFalse(applied.call_args.kwargs["dry_run"])

    def test_merge_prints_the_files_it_removes(self):
        stub = write.Change(mock.Mock(names=[]), None)
        stub.lines = ["merge y"]
        texts = {Path("kb/fn/x.toml"): "a\n", Path("kb/fn/y.toml"): None}
        with mock.patch.object(write, "apply", return_value=(stub, texts)) as applied:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(["merge", "x/fn", "y/fn", "--from", "7mfk"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "kb/fn/x.toml: written\nkb/fn/y.toml: removed\nmerge y\n")
        self.assertEqual(applied.call_args.args[0], [{"cmd": "merge", "meaning": "x/fn",
                                                      "other": "y/fn", "evidence": [],
                                                      "from": "7mfk"}])

    def test_set_and_move_pass_their_operations_to_apply(self):
        stub = write.Change(mock.Mock(names=[]), None)
        with mock.patch.object(write, "apply", return_value=(stub, {})) as applied:
            with contextlib.redirect_stdout(io.StringIO()):
                cli.main(["set", "x/ram", "level=code", "note=", "--layout", "jk00c"])
                cli.main(["move", "x/ram/jk78c", "jk78c:ffff450b", "--evidence",
                          'kind = "l0", at = "jk78c:000fcbec"', "--level", "code"])
        self.assertEqual([call.args[0] for call in applied.call_args_list], [
            [{"cmd": "set", "ref": "x/ram", "layout": "jk00c", "keys": {"level": "code"},
              "unset": ["note"]}],
            [{"cmd": "move", "symbol": "x/ram/jk78c", "to": "jk78c:ffff450b",
              "evidence": [{"kind": "l0", "at": "jk78c:000fcbec"}], "from": None,
              "level": "code", "note": None}]])

    def test_new_link_unlink_and_rename_pass_their_operations_to_apply(self):
        stub = write.Change(mock.Mock(names=[]), None)
        with mock.patch.object(write, "apply", return_value=(stub, {})) as applied:
            with contextlib.redirect_stdout(io.StringIO()):
                cli.main(["new", "ram", "7mfk:ffff0ff0", "--name", "probe_cell", "--evidence",
                          'kind = "spec", path = "tools/kb/SPEC.md"', "--level", "candidate",
                          "--note", "probe"])
                cli.main(["new", "feature", "probe_feature"])
                cli.main(["link", "x/ram", "reader", "y/fn", "role=consumer", 'layouts=["1nd"]',
                          "--evidence", 'kind = "l0", at = "1nd:00040000"'])
                cli.main(["unlink", "x/tbl", "axis", "y/axis", "slot=x"])
                cli.main(["rename", "x/ram", "probe_cell"])
                cli.main(["move", "x/ram/jk78c", "y/ram"])
        self.assertEqual([call.args[0] for call in applied.call_args_list], [
            [{"cmd": "new", "kind": "ram", "symbol": "7mfk:ffff0ff0", "name": "probe_cell",
              "evidence": [{"kind": "spec", "path": "tools/kb/SPEC.md"}], "level": "candidate",
              "note": "probe"}],
            [{"cmd": "new", "kind": "feature", "slug": "probe_feature", "name": None,
              "evidence": [], "level": None, "note": None}],
            [{"cmd": "link", "meaning": "x/ram", "type": "reader", "to": "y/fn",
              "keys": {"role": "consumer", "layouts": ["1nd"]},
              "evidence": [{"kind": "l0", "at": "1nd:00040000"}]}],
            [{"cmd": "unlink", "meaning": "x/tbl", "type": "axis", "to": "y/axis",
              "keys": {"slot": "x"}}],
            [{"cmd": "rename", "meaning": "x/ram", "name": "probe_cell"}],
            [{"cmd": "move", "symbol": "x/ram/jk78c", "to": "y/ram", "evidence": [],
              "from": None, "level": None, "note": None}]])

    def test_a_link_key_takes_a_value(self):
        err = io.StringIO()
        with mock.patch.object(write, "apply") as applied, contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(["link", "x/ram", "reader", "y/fn", "slot="]), 2)
        applied.assert_not_called()
        self.assertEqual(err.getvalue(), "error: a link key takes a value: slot\n")


class ApplyTest(unittest.TestCase):
    """`apply` plans under the lock on a current graph, then writes the files
    and loads the graph with the planned model; a dry run does neither."""

    def run_apply(self, dry_run):
        planned = (mock.Mock(), {Path("kb/ram/x.toml"): "a\n"}, mock.sentinel.result)
        with mock.patch.object(write.lock, "held", return_value=contextlib.nullcontext()), \
                mock.patch.object(write.graph, "fresh",
                                  return_value=contextlib.nullcontext("session")), \
                mock.patch.object(write.compile, "build", return_value=mock.sentinel.base), \
                mock.patch.object(write, "graph_resolver", return_value="resolve"), \
                mock.patch.object(write, "plan", return_value=planned) as plan, \
                mock.patch.object(write.store, "write") as written, \
                mock.patch.object(write.graph, "sync_held") as synced:
            write.apply(["op"], Path("/root"), dry_run=dry_run, log=print)
        plan.assert_called_once_with(["op"], mock.sentinel.base, "resolve", Path("/root"))
        return written, synced

    def test_a_change_writes_and_loads_the_planned_model(self):
        written, synced = self.run_apply(False)
        written.assert_called_once_with(Path("/root"), {Path("kb/ram/x.toml"): "a\n"})
        synced.assert_called_once_with(Path("/root"), False, print, mock.sentinel.result)

    def test_a_dry_run_writes_nothing(self):
        written, synced = self.run_apply(True)
        written.assert_not_called()
        synced.assert_not_called()


if __name__ == "__main__":
    unittest.main()
