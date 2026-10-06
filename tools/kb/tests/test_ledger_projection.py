import csv
import io
import copy
import unittest
from types import SimpleNamespace

from kb import compile, ledger_projection, match, project, repo, tokens, vocab
from kb.adapters import ledgers
from kb.model import Builder, SymbolKey
from kb.repo import KbError
from unittest.mock import patch


def model_of(role="base", offset=7, relies="structure", supports="identity"):
    b = Builder(repo.layouts(), compile.spaces(repo.config()), {"7mfk": {0x2040C}}, {})
    row = b.symbol("7mfk", "ram", 0xFFFF106F, "probe")
    to = b.symbol("7mfk", "ram", 0xFFFF1068, "probe")
    b.name(row, "row", "file", "probe")
    b.name(to, "target", "file", "probe")
    token = tokens.Token(role, "", to.address, offset, relies)
    owner, type_, target, end, props = ledgers.dependency(row, to, token, supports, {})
    b.link(owner, type_, target, "probe", props=props, stated=end)
    m = b.finish()
    m.root, m.config = repo.ROOT, repo.config()
    item = {"role": role, "to": m.meaning_of(to).key, "type": type_, "end": end,
            "relies": relies, "supports": supports}
    if offset is not None:
        item["offset"] = offset
    if props.get("role"):
        item["link_role"] = props["role"]
    return m, m.symbols[row], item


class NormalizationTest(unittest.TestCase):
    def test_order_preserves_values_properties_and_process_tokens(self):
        text = ("wave:6; trace:00031118@contract_conf; rom_const:0000991a=0x02; "
                "base:ffff128c+0x10@structural; spec:(168-128)*0.5=20")
        found = tokens.canonical(text)
        self.assertEqual(set(tokens.parse(found)), set(tokens.parse(text)))
        self.assertEqual(found, tokens.canonical(found))
        self.assertEqual(found.split("; "), sorted(token.text for token in tokens.parse(text)))

    def test_only_evidence_cells_change_and_csv_quoting_is_preserved(self):
        text = ('addr,semantics,evidence,contract_evidence,note\n'
                '0000991a,"A, B",wave:2; site:00031118,'
                'spec:sh2-decode; rom_const:100,"Paragraph one.\nParagraph two."\n')
        found = ledger_projection.normalize(text)
        [before] = csv.DictReader(io.StringIO(text))
        [after] = csv.DictReader(io.StringIO(found))
        for key in before:
            self.assertEqual(after[key], tokens.canonical(before[key])
                             if key in tokens.SUPPORTS else before[key])
        self.assertEqual(ledger_projection.normalize(found), found)

    def test_invalid_or_duplicate_evidence_refuses_before_serialization(self):
        for cell in ("unknown:1", "site:00031118; site:00031118"):
            with self.subTest(cell=cell), self.assertRaises(tokens.TokenError):
                ledger_projection.normalize(f"addr,evidence\n0000991a,{cell}\n")

    def test_conversion_preserves_every_cell_except_process_tokens(self):
        old = "addr,evidence,note\nffff106f,wave:2; base:ffff1068+7@structural,Boundary.\n"
        new = "addr,evidence,note\nffff106f,base:ffff1068+7@structural,Boundary.\n"
        ledger_projection.validate_conversion("probe.csv", old, new)
        for changed in (new.replace("+7", "+0x7"), new.replace("Boundary.", "Changed."),
                        new.replace("base:ffff1068+7@structural", "")):
            with self.subTest(changed=changed), self.assertRaises(KbError):
                ledger_projection.validate_conversion("probe.csv", old, changed)

    def test_converted_ledgers_refuse_the_preconversion_normalizer(self):
        with patch.object(project, "stage", return_value=5), self.assertRaises(KbError) as error:
            ledger_projection.normalization()
        self.assertEqual(error.exception.code, 2)
        self.assertIn("kb project", str(error.exception))


class OwnedProjectionTest(unittest.TestCase):
    def test_the_owned_model_reproduces_every_ledger_byte_and_curated_alias(self):
        m = compile.cached(repo.ROOT)
        rendered = ledger_projection.render(m)
        self.assertEqual(set(rendered), {path.as_posix() for path in ledgers.PATHS.values()}
                         | {"tools/ghidra/symbols/7mfk.csv"})
        for path, text in rendered.items():
            with self.subTest(path=path):
                self.assertEqual((repo.ROOT / path).read_text(encoding="utf-8"), text)
        self.assertIn("00020dfe,periodic_snapshot_dispatch,", rendered["tools/ghidra/symbols/7mfk.csv"])
        self.assertEqual(m.symbols[next(key for key in m.symbols if key.layout == "7mfk"
                                      and key.kind == "fn" and key.address == 0x20DFE)].meaning.name,
                         "coherent_snapshot")


class DependencyTest(unittest.TestCase):
    def test_decimal_and_hexadecimal_offsets_preserve_their_selected_spelling(self):
        m, row, item = model_of()
        for text in ("7", "0x7", "0x07"):
            with self.subTest(text=text):
                self.assertEqual(ledger_projection.dependency(m, row, {**item, "offset_text": text}),
                                 f"base:ffff1068+{text}@structural")

    def test_a_missing_link_or_another_claim_refuses_the_token(self):
        m, row, item = model_of()
        for changes in ({"type": "input"}, {"end": "to"}, {"offset": 8},
                        {"offset_text": "8"}, {"supports": "scale"}, {"relies": "level"},
                        {"role": "writes"}, {"link_role": "consumer"}, {"offset": -1},
                        {"offset": True}, {"offset_text": "7; spec:probe"}):
            with self.subTest(changes=changes), self.assertRaises(KbError):
                ledger_projection.dependency(m, row, {**item, **changes})
        m.links.clear()
        with self.assertRaises(KbError):
            ledger_projection.dependency(m, row, item)

    def test_another_relation_between_the_same_endpoints_does_not_satisfy_the_selector(self):
        m, row, item = model_of(role="indexed_by", offset=None)
        item.update(role="base", type="base", offset=7)
        with self.assertRaises(KbError):
            ledger_projection.dependency(m, row, item)

    def test_an_ignored_self_declaration_keeps_its_type_role_and_claim(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        key = b.symbol("7mfk", "tbl", 0x9000, "probe")
        b.name(key, "table", "file", "probe")
        b.link(key, "depends", key, "probe", props={"role": "match", "relies": "structure",
                                                      "supports": "scale"})
        m = b.finish()
        row = m.symbols[key]
        item = {"role": "match", "to": row.meaning.key, "type": "depends", "end": "owner",
                "link_role": "match", "relies": "structure", "supports": "scale"}
        self.assertEqual(ledger_projection.dependency(m, row, item), "match:00009000@structural")
        for changes in ({"supports": "identity"}, {"link_role": "homolog"}, {"type": "reader"}):
            with self.subTest(changes=changes), self.assertRaises(KbError):
                ledger_projection.dependency(m, row, {**item, **changes})


class SelectionTest(unittest.TestCase):
    def setUp(self):
        self.model, self.row, _ = model_of()
        self.document = {"note": ["Boundary."], "symbol": [{"layout": "7mfk", "evidence": [
            {"kind": "indirect", "supports": "identity", "mode": "base", "at": "7mfk:0004ea52",
             "value": 0x636}, {"kind": "spec", "supports": "scale", "key": "probe"}]}]}
        self.marker = {"registry": "vars", "fields": ["units"], "storage_description": "raw_u16",
                       "notes": [0], "identity": [0], "offset": [{"evidence": 0, "text": "0x636"}]}

    def test_a_storage_description_does_not_restore_an_absent_semantic_unit(self):
        found = ledger_projection._row(self.model, self.row, self.document, self.marker)
        self.assertEqual(found["units"], "raw_u16")
        self.assertIsNone(self.row.value("unit"))
        self.assertEqual(found["evidence"], "indirect_base:0004ea52+0x636")
        self.assertEqual(found["note"], "Boundary.")

    def test_a_selector_cannot_pick_another_claim_or_an_invalid_index(self):
        for changes in ({"identity": [1]}, {"identity": [-1]}, {"identity": [True]},
                        {"identity": [0, 0]}, {"notes": [-1]}, {"notes": [1]},
                        {"offset": [{"evidence": 1, "text": "0x636"}]},
                        {"offset": [{"evidence": 0, "text": "0x635"}]},
                        {"offset": [{"evidence": 0, "text": "0x636"}] * 2}):
            with self.subTest(changes=changes), self.assertRaises(KbError):
                ledger_projection._row(self.model, self.row, self.document,
                                       {**copy.deepcopy(self.marker), **changes})

    def test_unbound_constants_and_unverified_sites_do_not_ground_a_level(self):
        for item in ({"kind": "unbound-constant", "value": "124"},
                     {"kind": "unverified-site", "at": "7mfk:0004ea52"}):
            with self.subTest(item=item):
                self.assertTrue(all(key in item for key in vocab.EVIDENCE_KINDS[item['kind']][0]))
                self.assertEqual(match.rank(item, self.row, self.model), -1)


def target(key='target/ram', address=0xffff1068):
    return SimpleNamespace(key=key, symbols={'7mfk': SimpleNamespace(address=address)})


def fixture(targets, count=1):
    evidence = {'kind': 'trace', 'to': 'target/ram/7mfk', 'relies': 'structure'}
    document = {'symbol': [{'layout': '7mfk', 'evidence': [evidence]}]}
    symbol = SimpleNamespace(kind='ram', address=0xffff106f,
                             key=SymbolKey('7mfk', 'ram', 0xffff106f), value=lambda name: None)
    owner = SimpleNamespace(key='row/ram', symbols={'7mfk': symbol})
    symbol.meaning = owner
    markers = [{'registry': 'vars', 'order': index, 'fields': [], 'identity': [0]}
               for index in range(count)]
    model = SimpleNamespace(meanings=[*targets, owner], links=[], self_links=[],
                            files={('ram', 'row'): (owner, None)}, root=repo.ROOT, overlay={},
                            stash={'ledger_rows': [('ram', 'row', markers, 'probe')]})
    return model, symbol, document, evidence


def rows(model, document):
    with patch.object(ledger_projection.store, 'load', return_value=document):
        text = ledger_projection.render(model)[ledgers.PATHS['vars'].as_posix()]
    return list(csv.DictReader(io.StringIO(text)))


class TraceLookupTest(unittest.TestCase):
    def test_duplicate_meaning_keys_keep_the_first_trace_target(self):
        model, _, document, _ = fixture([target(), target(address=0xffff1080)])
        self.assertEqual(rows(model, document)[0]['evidence'], 'trace:ffff1068@structural')

    def test_each_render_observes_current_targets_names_and_addresses(self):
        selected = target()
        model, _, document, evidence = fixture([selected])
        self.assertEqual(rows(model, document)[0]['evidence'], 'trace:ffff1068@structural')
        selected.symbols['7mfk'].address = 0xffff1080
        selected.key = 'renamed/ram'
        evidence['to'] = 'renamed/ram/7mfk'
        self.assertEqual(rows(model, document)[0]['evidence'], 'trace:ffff1080@structural')
        model.meanings[0] = target('renamed/ram', 0xffff1090)
        self.assertEqual(rows(model, document)[0]['evidence'], 'trace:ffff1090@structural')

    def test_numeric_and_symbol_targets_keep_their_selected_notes_and_properties(self):
        model, symbol, _, evidence = fixture([])
        for to in ('7mfk:ffff1068', SymbolKey('7mfk', 'ram', 0xffff1068)):
            for note in ('trace', 'irq_trace'):
                with self.subTest(to=to, note=note):
                    item = {**evidence, 'to': to, 'note': note}
                    self.assertEqual(ledger_projection.terminal(model, symbol, item),
                                     note + ':ffff1068@structural')

    def test_missing_and_malformed_trace_targets_keep_their_errors(self):
        model, symbol, document, evidence = fixture([target()])
        for to, error in (('missing/ram/7mfk', StopIteration),
                          ('target/ram', ValueError), ('target/ram/7mfk/extra', ValueError)):
            with self.subTest(to=to):
                evidence['to'] = to
                with self.assertRaises(error) as direct:
                    ledger_projection.terminal(model, symbol, evidence)
                with self.assertRaises(error) as rendered:
                    rows(model, document)
                self.assertEqual(str(rendered.exception), str(direct.exception))

    def test_rendering_does_not_reuse_l0_context_verdicts(self):
        model, symbol, document, _ = fixture([target()], count=3)
        item = {'kind': 'l0-context', 'at': '7mfk:0002040c'}
        document['symbol'][0]['evidence'] = [item]
        with patch.object(match, 'verify', return_value=None) as verify:
            rows(model, document)
        self.assertEqual(verify.call_args_list, [unittest.mock.call(model, symbol, item)] * 3)

    def test_repeated_trace_targets_do_not_scan_all_meaning_keys(self):
        accesses = []
        class Meaning:
            def __init__(self, key, address):
                self.name = key
                self.symbols = {'7mfk': SimpleNamespace(address=address)}
            @property
            def key(self):
                accesses.append(self.name)
                return self.name
        targets = [Meaning(f'other_{index}/ram', 0xffff0000 + index) for index in range(128)]
        targets.append(Meaning('target/ram', 0xffff1068))
        model, _, document, _ = fixture(targets, count=64)
        self.assertEqual(len(rows(model, document)), 64)
        self.assertLessEqual(len(accesses), 3 * len(model.meanings))


class RenderOrderTest(unittest.TestCase):
    def make_model(self, orders):
        model, symbol, document, _ = fixture([], count=0)
        model.stash['ledger_rows'][0][2].extend(
            {'registry': 'vars', 'order': order} for order in orders)
        return model, symbol, document

    def render_model(self, model, document):
        with patch.object(ledger_projection.store, 'load', return_value=document), \
                patch.object(ledger_projection, '_row', side_effect=lambda m, s, d, marker, lookup:
                             {'addr': str(marker['order'])}) as row:
            rendered = ledger_projection.render(model)
        return rendered, row.call_count

    def test_noncontiguous_selectors_keep_numeric_output_order(self):
        model, _, document = self.make_model([3, 0, 2, 1000000])
        rendered, count = self.render_model(model, document)
        values = list(csv.DictReader(io.StringIO(rendered[ledgers.PATHS['vars'].as_posix()])))
        self.assertEqual([value['addr'] for value in values], ['0', '2', '3', '1000000'])
        self.assertEqual(count, 4)

    def test_a_duplicate_selector_refuses_before_rendering_the_duplicate_row(self):
        model, _, document = self.make_model([2, 0, 2])
        with patch.object(ledger_projection.store, 'load', return_value=document), \
                patch.object(ledger_projection, '_row', return_value={}) as row, \
                self.assertRaises(KbError) as error:
            ledger_projection.render(model)
        self.assertEqual(error.exception.code, 3)
        self.assertEqual(str(error.exception), '7mfk-ffff106f/ram: invalid or duplicate ledger row selector')
        self.assertEqual(row.call_count, 2)

    def test_equal_orders_of_different_registries_are_independent(self):
        model, symbol, document = self.make_model([])
        symbol.kind = 'fn'
        model.stash['ledger_rows'][0][2].extend([
            {'registry': 'funcs', 'order': 0}, {'registry': 'curated', 'order': 0}])
        rendered, count = self.render_model(model, document)
        self.assertEqual(count, 2)
        self.assertIn('0,', rendered[ledgers.PATHS['funcs'].as_posix()])
        self.assertIn('0,', rendered['tools/ghidra/symbols/7mfk.csv'])

    def test_invalid_selectors_refuse_before_serializing_a_row(self):
        for changes in ({'order': True}, {'order': -1}, {'order': 1.5},
                        {'order': None}, {'registry': 'unknown'}, {'registry': 'funcs'}):
            with self.subTest(changes=changes):
                model, _, document = self.make_model([0])
                model.stash['ledger_rows'][0][2][0].update(changes)
                with patch.object(ledger_projection.store, 'load', return_value=document), \
                        patch.object(ledger_projection, '_row') as row, \
                        self.assertRaises(KbError) as error:
                    ledger_projection.render(model)
                self.assertEqual(error.exception.code, 3)
                row.assert_not_called()

    def test_unhashable_integer_subclasses_keep_duplicate_equality(self):
        class UnhashableInteger(int):
            __hash__ = None
        for orders in ([UnhashableInteger(2), 2], [2, UnhashableInteger(2)],
                       [UnhashableInteger(2), UnhashableInteger(2)]):
            with self.subTest(orders=orders):
                model, _, document = self.make_model(orders)
                with self.assertRaises(KbError) as error:
                    self.render_model(model, document)
                self.assertEqual(error.exception.code, 3)
        model, _, document = self.make_model([UnhashableInteger(2), 3, 1])
        rendered, count = self.render_model(model, document)
        self.assertEqual(count, 3)
        values = list(csv.DictReader(io.StringIO(rendered[ledgers.PATHS['vars'].as_posix()])))
        self.assertEqual([value['addr'] for value in values], ['1', '2', '3'])

    def test_each_render_reads_current_selectors_after_success_and_refusal(self):
        model, _, document = self.make_model([0, 1])
        first, _ = self.render_model(model, document)
        markers = model.stash['ledger_rows'][0][2]
        markers[1]['order'] = 0
        with self.assertRaises(KbError):
            self.render_model(model, document)
        markers[1]['order'] = 2
        after, count = self.render_model(model, document)
        self.assertEqual(count, 2)
        self.assertNotEqual(after, first)
        self.assertIn('2,', after[ledgers.PATHS['vars'].as_posix()])

    def test_the_duplicate_check_observes_the_selector_appended_by_row_rendering(self):
        model, _, document = self.make_model([0, 4])
        def render_row(m, s, d, marker, lookup):
            marker['order'] = 4
            return {}
        with patch.object(ledger_projection.store, 'load', return_value=document), \
                patch.object(ledger_projection, '_row', side_effect=render_row) as row, \
                self.assertRaises(KbError) as error:
            ledger_projection.render(model)
        self.assertEqual(error.exception.code, 3)
        self.assertEqual(row.call_count, 1)


if __name__ == "__main__":
    unittest.main()
