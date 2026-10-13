import contextlib
import copy
import csv
import io
import tomllib
import unittest
from unittest import mock

import pytest

from kb import adapters, cli, compile, convert, ledger_projection, repo, store, write
from kb.adapters import files as file_adapter
from kb.repo import KbError
from tools.kb.tests import selector_sources

pytestmark = pytest.mark.usefixtures('reuse_kb_source_parses', 'source_order')

ISOLATED_CASES = {
    'test_unique_exact_repeat_is_idempotent_in_one_batch_and_on_the_result',
    'test_symbol_references_select_the_meanings_home_ledger_row',
    'test_a_late_refusal_writes_no_file_or_graph',
    'test_an_offset_must_match_the_canonical_relation',
    'test_final_batch_refuses_a_relation_replaced_without_its_selected_claim',
    'test_final_batch_refuses_marker_removal_and_incompatible_replacement',
    'test_final_batch_refuses_unlink_even_when_the_source_had_no_selector',
    'test_refuses_an_incompatible_or_duplicate_selected_claim',
    'test_refuses_claims_without_a_projected_dependency_column',
    'test_refuses_invalid_vocabulary_and_role_direction_mappings',
    'test_refuses_missing_and_ambiguous_native_relations',
    'test_refuses_missing_duplicate_and_incompatible_owned_markers',
    'test_refuses_noninteger_native_base_offsets_that_compare_equal_to_zero',
    'test_refuses_unknown_keys_missing_keys_and_wrong_value_types',
    'test_select_cannot_create_a_marker_or_adopt_one_from_an_earlier_operation',
    'test_the_native_relation_must_hold_each_claiming_end',
    'test_zero_base_offset_selects_one_relation_and_normalizes_duplicate_identity',
}


@pytest.fixture(scope='module')
def preserved_full_models(reuse_kb_source_parses):
    held = {}
    yield held
    for cls, model, before, documents in held.values():
        assert convert.dump(model) == before
        assert cls.documents == documents


@pytest.fixture(scope='module')
def isolated_model(reuse_kb_source_parses, tmp_path_factory):
    root = tmp_path_factory.mktemp('selector-writer')
    hashes = selector_sources.write_sources(root)
    model = compile.build(root, order=(file_adapter,))
    assert model.stash['ledger_rows'] and write._issues(model) == {}
    before = convert.dump(model)
    documents = {path: store.load(root, path) for path in (STATE_PATH, FUNCTION_PATH)}
    yield model, documents
    assert convert.dump(model) == before
    assert selector_sources.unchanged(root, hashes)


@pytest.fixture
def source_order(request, monkeypatch, preserved_full_models):
    instance = request.instance
    if not isinstance(instance, SelectTest):
        return
    cls = type(instance)
    if id(cls.base) not in preserved_full_models:
        preserved_full_models[id(cls.base)] = (
            cls, cls.base, convert.dump(cls.base), copy.deepcopy(cls.documents))
    if request.node.name in ISOLATED_CASES:
        monkeypatch.setattr(adapters, 'ADAPTERS', (file_adapter,))
        model, documents = request.getfixturevalue('isolated_model')
        monkeypatch.setattr(instance, 'base', model)
        monkeypatch.setattr(instance, 'documents', copy.deepcopy(documents))
        monkeypatch.setattr(instance, 'model', lambda documents: cls.model(documents, root=model.root))


STATE, FUNCTION = "knock_timing_state/ram", "knock_function/fn"
STATE_PATH = store.path_of("ram", "knock_timing_state")
FUNCTION_PATH = store.path_of("fn", "knock_function")
OPS = [
    {"cmd": "select", "meaning": STATE, "registry": "vars", "order": 584,
     "dependency": {"role": "writes", "to": FUNCTION, "type": "writer", "end": "owner",
                    "relies": "structure", "supports": "identity"}},
    {"cmd": "select", "meaning": FUNCTION, "registry": "funcs", "order": 142,
     "dependency": {"role": "writes", "to": STATE, "type": "writer", "end": "to",
                    "relies": "structure", "supports": "identity"}},
]
UNLINK = {"cmd": "unlink", "meaning": STATE, "type": "writer", "to": FUNCTION}


class SelectTest(unittest.TestCase):
    """Public planning over owned documents; no file or graph writes."""

    @classmethod
    def setUpClass(cls):
        cls.documents = {path: store.load(repo.ROOT, path)
                         for path in (STATE_PATH, FUNCTION_PATH)}
        for path, op in zip((STATE_PATH, FUNCTION_PATH), OPS):
            [marker] = [entry for entry in cls.documents[path]["ledger"]
                        if entry["registry"] == op["registry"] and entry["order"] == op["order"]]
            marker["dependency"] = [entry for entry in marker.get("dependency", ())
                                    if entry != op["dependency"]]
        cls.base = cls.model(cls.documents)

    @staticmethod
    def model(documents, root=repo.ROOT):
        return compile.build(root, {path: store.render(path.parent.name, document)
                                         for path, document in documents.items()})

    def plan(self, *ops, base=None):
        base = base or self.base
        return write.plan(list(ops), base, write.model_resolver(base), root=base.root)

    def refused(self, *ops, base=None, code=3):
        with self.assertRaises(KbError) as caught:
            self.plan(*ops, base=base)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def marker(self, document, op=OPS[0]):
        return next(entry for entry in document["ledger"]
                    if entry["registry"] == op["registry"] and entry["order"] == op["order"])

    def writer(self, documents):
        return next(entry for entry in documents[STATE_PATH]["link"]
                    if entry["type"] == "writer" and entry["to"] == FUNCTION)

    def test_both_claiming_ends_add_only_the_exact_selected_claims(self):
        change, texts, result = self.plan(*OPS)
        self.assertEqual(set(texts), {STATE_PATH, FUNCTION_PATH})
        expected = copy.deepcopy(self.documents)
        for path, op in zip((STATE_PATH, FUNCTION_PATH), OPS):
            self.marker(expected[path], op)["dependency"].append(op["dependency"])
            self.assertEqual(texts[path], store.render(path.parent.name, expected[path]))
        self.assertEqual(change.removed, set())
        self.assertFalse(change.rows_changed)
        before, after = ledger_projection.render(self.base), ledger_projection.render(result)
        for registry, address, token in (
                ("vars", "ffff121a", "writes:000493e8@structural"),
                ("funcs", "000493e8", "writes:ffff121a@structural")):
            path = f"defs/JK08A.{registry}.csv"
            old = {row["addr"]: row for row in csv.DictReader(io.StringIO(before[path]))}
            new = {row["addr"]: row for row in csv.DictReader(io.StringIO(after[path]))}
            with self.subTest(registry=registry):
                self.assertNotIn(token, old[address]["evidence"])
                self.assertIn(token, new[address]["evidence"])

    def test_unique_exact_repeat_is_idempotent_in_one_batch_and_on_the_result(self):
        _, texts, result = self.plan(*OPS, *OPS)
        self.assertEqual(set(texts), {STATE_PATH, FUNCTION_PATH})
        _, repeated, _ = self.plan(*OPS, base=result)
        self.assertEqual(repeated, {})

    def test_symbol_references_select_the_meanings_home_ledger_row(self):
        resolve = write.model_resolver(self.base)
        state, _ = resolve(STATE)
        function, _ = resolve(FUNCTION)
        self.assertIn("7mfk", state.symbols)
        self.assertIn("7mfk", function.symbols)
        layout = "1nd" if "1nd" in state.symbols and "1nd" in function.symbols else "7mfk"
        op = {**OPS[0], "meaning": state.symbols[layout].key.location, "dependency": {
            **OPS[0]["dependency"], "to": function.symbols[layout].key.location}}
        _, texts, _ = self.plan(op)
        expected = copy.deepcopy(self.documents[STATE_PATH])
        self.marker(expected)["dependency"].append(OPS[0]["dependency"])
        self.assertEqual(texts, {STATE_PATH: store.render("ram", expected)})

    def test_refuses_unknown_keys_missing_keys_and_wrong_value_types(self):
        variants = [
            {"order": True}, {"order": -1}, {"order": "584"}, {"order": 1.5},
            {"registry": []}, {"registry": "other"}, {"extra": "x"},
            {"dependency": []}, {"dependency": {"role": "writes"}},
        ]
        for key, value in (("evidence", []), ("to", []), ("role", False),
                           ("offset", True), ("offset", -1), ("offset_text", "1"),
                           ("link_role", []), ("supports", ["identity"])):
            variants.append({"dependency": {**OPS[0]["dependency"], key: value}})
        for variant in variants:
            with self.subTest(variant=variant):
                self.refused({**OPS[0], **variant}, code=2)

    def test_refuses_invalid_vocabulary_and_role_direction_mappings(self):
        for key, value in (("role", "other"), ("type", "other"), ("end", "other"),
                           ("supports", "other"), ("relies", "other"),
                           ("end", "to"), ("type", "reader"), ("link_role", "accessor")):
            with self.subTest(key=key, value=value):
                self.refused({**OPS[0], "dependency": {**OPS[0]["dependency"], key: value}})

    def test_an_offset_must_match_the_canonical_relation(self):
        for offset in (0, 1):
            with self.subTest(offset=offset):
                self.assertIn("found 0", self.refused({
                    **OPS[0], "dependency": {**OPS[0]["dependency"], "offset": offset}}))

    def test_refuses_claims_without_a_projected_dependency_column(self):
        self.assertIn("curated does not project", self.refused({
            **OPS[1], "registry": "curated", "order": 98}))
        path = store.path_of("axis", "fascinating-hog")
        axis = store.load(self.base.root, path)
        [marker] = [entry for entry in axis["ledger"] if entry["registry"] == "axes"]
        item = copy.deepcopy(marker["dependency"][0])
        item["supports"] = "contract"
        self.assertIn("axes does not project", self.refused({
            "cmd": "select", "meaning": "fascinating-hog/axis", "registry": "axes",
            "order": marker["order"], "dependency": item}))
        documents = copy.deepcopy(self.documents)
        documents[STATE_PATH]["ledger"].append({"registry": "diagnostic-bindings",
                                                "order": 99999})
        self.assertIn("diagnostic-bindings does not project", self.refused({
            **OPS[0], "registry": "diagnostic-bindings", "order": 99999},
            base=self.model(documents)))

    def test_select_cannot_create_a_marker_or_adopt_one_from_an_earlier_operation(self):
        documents = copy.deepcopy(self.documents)
        documents[STATE_PATH]["ledger"].remove(self.marker(documents[STATE_PATH]))
        base = self.model(documents)
        earlier = {"cmd": "set", "ref": STATE,
                   "keys": {"ledger": self.documents[STATE_PATH]["ledger"]}}
        self.assertIn("no unique owned ledger row", self.refused(earlier, OPS[0], base=base))

    def test_zero_base_offset_selects_one_relation_and_normalizes_duplicate_identity(self):
        documents = copy.deepcopy(self.documents)
        documents[STATE_PATH]["link"].append({
            "type": "base", "to": STATE, "offset": 0, "layouts": ["7mfk"],
            "relies": "structure", "supports": "identity"})
        op = {**OPS[0], "dependency": {
            "role": "base", "to": STATE, "type": "base", "end": "owner",
            "relies": "structure", "supports": "identity", "offset": 0,
            "offset_text": "0x0"}}
        _, texts, result = self.plan(op, base=self.model(documents))
        self.assertEqual(set(texts), {STATE_PATH})
        _, repeated, _ = self.plan(op, base=result)
        self.assertEqual(repeated, {})
        omitted = {key: value for key, value in op["dependency"].items()
                   if key not in ("offset", "offset_text")}
        self.marker(documents[STATE_PATH])["dependency"].append(omitted)
        base = self.model(documents)
        _, repeated, _ = self.plan({**op, "dependency": omitted}, base=base)
        self.assertEqual(repeated, {})
        self.assertIn("duplicate ledger dependency", self.refused(op, base=base))
        for variant in ({**op["dependency"], "offset_text": "1"},
                        {**omitted, "offset": 0, "relies": "level"}):
            with self.subTest(variant=variant):
                self.refused({**op, "dependency": variant}, base=base)

    def test_refuses_noninteger_native_base_offsets_that_compare_equal_to_zero(self):
        for offset in (False, 0.0):
            documents = copy.deepcopy(self.documents)
            documents[STATE_PATH]["link"].append({
                "type": "base", "to": STATE, "offset": offset, "layouts": ["7mfk"],
                "relies": "structure", "supports": "identity"})
            op = {**OPS[0], "dependency": {
                "role": "base", "to": STATE, "type": "base", "end": "owner",
                "relies": "structure", "supports": "identity", "offset": 0}}
            with self.subTest(offset=offset):
                self.assertIn("invalid offset", self.refused(op, base=self.model(documents)))

    def test_refuses_missing_duplicate_and_incompatible_owned_markers(self):
        for mutation in ("missing", "duplicate", "registry", "order", "float"):
            documents = copy.deepcopy(self.documents)
            marker = self.marker(documents[STATE_PATH])
            if mutation == "missing":
                documents[STATE_PATH]["ledger"].remove(marker)
            elif mutation == "duplicate":
                documents[STATE_PATH]["ledger"].append(copy.deepcopy(marker))
            elif mutation == "registry":
                marker["registry"] = "funcs"
            elif mutation == "order":
                marker["order"] = 585
            else:
                marker["order"] = 584.0
            with self.subTest(mutation=mutation):
                self.assertIn("ledger", self.refused(OPS[0], base=self.model(documents)))

    def test_refuses_an_incompatible_or_duplicate_selected_claim(self):
        for mutation in ("relies", "supports", "offset_text", "duplicate"):
            documents = copy.deepcopy(self.documents)
            item = copy.deepcopy(OPS[0]["dependency"])
            if mutation == "relies":
                item["relies"] = "identity"
            elif mutation == "supports":
                item["supports"] = "contract"
            elif mutation == "offset_text":
                item["offset_text"] = "0"
            selected = self.marker(documents[STATE_PATH])["dependency"]
            selected.append(item)
            if mutation == "duplicate":
                selected.append(copy.deepcopy(item))
            with self.subTest(mutation=mutation):
                self.assertIn("duplicate ledger dependency",
                              self.refused(OPS[0], base=self.model(documents)))

    def test_refuses_missing_and_ambiguous_native_relations(self):
        for mutation in ("missing", "collapsed-duplicate", "distinct-slot"):
            documents = copy.deepcopy(self.documents)
            relation = self.writer(documents)
            if mutation == "missing":
                documents[STATE_PATH]["link"].remove(relation)
            else:
                other = copy.deepcopy(relation)
                if mutation == "distinct-slot":
                    other["slot"] = "other"
                documents[STATE_PATH]["link"].append(other)
            with self.subTest(mutation=mutation):
                self.assertIn("relation" if mutation != "missing" else "matching link",
                              self.refused(OPS[0], base=self.model(documents)))

    def test_the_native_relation_must_hold_each_claiming_end(self):
        for key in ("relies", "reverse_relies", "supports", "reverse_supports"):
            documents = copy.deepcopy(self.documents)
            self.writer(documents)[key] = "identity" if key.endswith("relies") else "contract"
            op = OPS[1] if key.startswith("reverse_") else OPS[0]
            with self.subTest(key=key):
                self.refused(op, base=self.model(documents))

    def test_final_batch_refuses_unlink_even_when_the_source_had_no_selector(self):
        self.assertIn("contradicts", self.refused(*OPS, UNLINK))
        self.assertEqual(write.Change(self.base, write.model_resolver(self.base)).texts(), {})

    def test_final_batch_refuses_a_relation_replaced_without_its_selected_claim(self):
        relation = copy.deepcopy(self.writer(self.documents))
        later = {"cmd": "link", "meaning": STATE, "type": "writer", "to": FUNCTION,
                 "keys": {key: value for key, value in relation.items()
                          if key not in ("type", "to", "evidence")},
                 "evidence": relation.get("evidence", [])}
        self.assertIn("selected ledger dependency is not retained",
                      self.refused(OPS[0], UNLINK, later))

    def test_final_batch_refuses_marker_removal_and_incompatible_replacement(self):
        for mutation in ("remove", "replace", "duplicate"):
            documents = copy.deepcopy(self.documents)
            marker = self.marker(documents[STATE_PATH])
            if mutation == "remove":
                documents[STATE_PATH]["ledger"].remove(marker)
            else:
                marker["dependency"].append({**OPS[0]["dependency"], "relies": "identity"})
                if mutation == "duplicate":
                    marker["dependency"].append(OPS[0]["dependency"])
            later = {"cmd": "set", "ref": STATE,
                     "keys": {"ledger": documents[STATE_PATH]["ledger"]}}
            with self.subTest(mutation=mutation):
                self.assertIn("contradicts", self.refused(OPS[0], later))

    def test_a_late_refusal_writes_no_file_or_graph(self):
        original_build = compile.build
        with mock.patch.object(write.lock, "held", return_value=contextlib.nullcontext()), \
                mock.patch.object(write.graph, "fresh", return_value=contextlib.nullcontext()), \
                mock.patch.object(write.compile, "build", side_effect=lambda root, overlay=None:
                                  original_build(root, {**self.base.overlay, **(overlay or {})})), \
                mock.patch.object(write, "graph_resolver",
                                  return_value=write.model_resolver(self.base)), \
                mock.patch.object(write.store, "write") as written, \
                mock.patch.object(write.graph, "sync_held") as synced:
            with self.assertRaises(KbError):
                write.apply([*OPS, UNLINK], log=lambda _: None, root=self.base.root)
        written.assert_not_called()
        synced.assert_not_called()


class SelectArgumentsTest(unittest.TestCase):
    def test_cli_passes_the_selected_claim_and_dry_run_to_apply(self):
        change = write.Change(mock.Mock(names=[]), None)
        with mock.patch.object(write, "apply", return_value=(change, {})) as applied, \
                contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["select", STATE, "vars", "584", "role=writes", f"to={FUNCTION}",
                             "type=writer", "end=owner", "relies=structure", "supports=identity",
                             "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(applied.call_args.args[0], [OPS[0]])
        self.assertTrue(applied.call_args.kwargs["dry_run"])

    def test_cli_refuses_unsetting_a_dependency_key(self):
        with mock.patch.object(write, "apply") as applied, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["select", STATE, "vars", "584", "role="]), 2)
        applied.assert_not_called()


if __name__ == "__main__":
    unittest.main()
