import csv
import io
import unittest

from kb import ledger_projection, tokens


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


if __name__ == "__main__":
    unittest.main()
