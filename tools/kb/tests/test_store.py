import re
import tempfile
import tomllib
import unittest
from pathlib import Path

from kb import repo, store

EXAMPLE = re.compile(r"^`kb/(?P<kind>[a-z]+)/(?P<name>[a-z_]+)\.toml`:\n\n```toml\n(?P<text>.*?)```$",
                     re.M | re.S)


def canonical(kind, document):
    text = store.render(kind, document)
    return text, tomllib.loads(text)


class RenderTest(unittest.TestCase):
    def test_the_examples_of_the_specification_are_canonical(self):
        examples = list(EXAMPLE.finditer((repo.ROOT / "tools/kb/SPEC.md").read_text(
            encoding="utf-8")))
        self.assertGreaterEqual(len(examples), 2)
        for example in examples:
            with self.subTest(name=example["name"]):
                text = example["text"]
                self.assertEqual(store.render(example["kind"], tomllib.loads(text)), text)

    def test_keys_follow_the_schema_and_absent_keys_are_omitted(self):
        text, _ = canonical("tbl", {"storage": "uint8", "title": "A table", "cols": 4,
                                    "summary": "", "note": [], "level": "code"})
        self.assertEqual(text, 'title = "A table"\nlevel = "code"\ncols = 4\n'
                               'storage = "uint8"\n')

    def test_a_long_string_wraps_within_78_columns_and_keeps_its_value(self):
        summary = " ".join(["word"] * 40) + " [[normalized_bfs/ram]] closes it."
        text, document = canonical("ram", {"title": "t", "summary": summary})
        self.assertEqual(document["summary"], summary)
        lines = text.splitlines()
        self.assertEqual(lines[1], 'summary = """')
        self.assertTrue(all(len(line) <= store.WIDTH for line in lines))
        self.assertTrue(all(line.endswith(" \\") for line in lines[2:-1]))
        self.assertTrue(lines[-1].endswith('"""'))

    def test_a_string_of_72_characters_stays_on_one_line(self):
        title = "x" * store.SHORT
        text, _ = canonical("fn", {"title": title})
        self.assertEqual(text, f'title = "{title}"\n')

    def test_an_array_that_does_not_fit_puts_one_element_per_line(self):
        notes = ["first note " * 3, "second note " * 3, "third"]
        text, document = canonical("fn", {"title": "t", "note": notes})
        self.assertEqual(document["note"], notes)
        self.assertIn('note = [\n    "first note', text)
        self.assertIn('    "third",\n]\n', text)
        short, _ = canonical("fn", {"title": "t", "note": ["a", "b"]})
        self.assertIn('note = ["a", "b"]\n', short)

    def test_offsets_and_did_numbers_are_hexadecimal(self):
        text, document = canonical("did", {"title": "t", "number": 0x1234, "link": [
            {"type": "source", "to": "x/ram", "offset": 10}]})
        self.assertIn("number = 0x1234\n", text)
        self.assertIn("offset = 0xa\n", text)
        self.assertEqual(document["link"][0]["offset"], 10)

    def test_arrays_of_tables_sort_by_their_schema_keys(self):
        text, document = canonical("ram", {"title": "t", "symbol": [
            {"layout": "jk00d", "address": "ffff1050"},
            {"layout": "7mfk", "address": "ffff1048",
             "evidence": [{"kind": "l0", "supports": "identity", "at": "7mfk:0003bd5a"}]}],
            "status": [{"layout": "jk78c", "state": "absent"},
                       {"layout": "1nd", "state": "absent"}]})
        self.assertEqual([item["layout"] for item in document["symbol"]], ["7mfk", "jk00d"])
        self.assertEqual([item["layout"] for item in document["status"]], ["1nd", "jk78c"])
        self.assertLess(text.index("[[symbol.evidence]]"), text.index('layout = "jk00d"'))

    def test_keys_outside_the_schema_follow_in_alphabetical_order(self):
        text, document = canonical("feature", {
            "title": "Runtime", "target": [
                {"layout": "7mfk", "status": "supported", "rom_size": 1048576,
                 "hooks": {"b": {"hook": "b/hook", "replacement": "0000f000"},
                           "a": {"hook": "a/hook", "replacement": "0000e000"}}}]})
        self.assertEqual(list(document["target"][0]["hooks"]), ["a", "b"])
        self.assertLess(text.index("rom_size"), text.index("[target.hooks.a]"))
        self.assertEqual(store.render("feature", document), text)

    def test_rendering_is_idempotent(self):
        document = {"title": "t", "summary": "s " * 50, "home": "7mfk", "width": 8,
                    "bit": [{"bit": 3, "name": "armed"}, {"bit": 0, "name": "active"}],
                    "link": [{"type": "writer", "to": "f/fn", "relies": "structure",
                              "via": ["g/fn", "h/fn"]}]}
        text = store.render("ram", document)
        self.assertEqual(store.render("ram", tomllib.loads(text)), text)


class CanonicalTest(unittest.TestCase):
    def test_the_check_names_a_file_that_differs_and_fmt_rewrites_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kb" / "ram" / "loose_value.toml"
            path.parent.mkdir(parents=True)
            path.write_text('level = "code"\ntitle = "Loose"\n', encoding="utf-8")
            issues = store.canonical(root)
            self.assertEqual([(issue.path, issue.subject) for issue in issues],
                             [("kb/ram/loose_value.toml", "loose_value/ram")])
            self.assertEqual(store.fmt(root), [Path("kb/ram/loose_value.toml")])
            self.assertEqual(path.read_text(encoding="utf-8"), 'title = "Loose"\nlevel = "code"\n')
            self.assertEqual(store.canonical(root), [])

    def test_a_file_that_does_not_parse_fails_the_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kb" / "fn" / "broken.toml"
            path.parent.mkdir(parents=True)
            path.write_text("title = \n", encoding="utf-8")
            (issue,) = store.canonical(root)
            self.assertTrue(issue.message.startswith("no TOML"))


if __name__ == "__main__":
    unittest.main()
