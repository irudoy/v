import csv
import io
import copy
import unittest

from kb import compile, ledger_projection, match, project, repo, tokens, vocab
from kb.adapters import ledgers
from kb.model import Builder
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


if __name__ == "__main__":
    unittest.main()
