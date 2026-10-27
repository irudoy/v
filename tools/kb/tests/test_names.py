import random
import builtins
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

from kb import names, repo, vocab
from kb.names import Row


class RuleTest(unittest.TestCase):
    def setUp(self):
        self.taken = names.Taken({"fuzzy-badger", "periodic_tick_isr"})
        self.domain = {"fuel", "knock"}

    def test_the_rules_of_generated_names(self):
        reject = lambda name: names.rejection(name, self.taken, self.domain)
        self.assertIsNone(reject("brave-otter"))
        self.assertEqual(reject("Brave-otter"), "grammar")
        self.assertEqual(reject("brave_otter"), "grammar")
        self.assertEqual(reject("deaf-otter"), "hexadecimal word deaf")
        self.assertEqual(reject("brave-bead"), "hexadecimal word bead")
        self.assertEqual(reject("fuel-otter"), "domain word fuel")
        self.assertEqual(reject("fuzzy-badger"), "within distance 2 of fuzzy-badger")
        self.assertEqual(reject("fuzy-badgre"), "within distance 2 of fuzzy-badger")
        self.assertIsNone(reject("fuzzy-bdgrx"))

    def test_a_drawn_name_passes_and_is_taken(self):
        name = names.draw(self.taken, self.domain, 1000, random.Random(7))
        self.assertTrue(vocab.GENERATED_NAME.fullmatch(name))
        self.assertIsNone(names.rejection(name, names.Taken(()), self.domain))
        self.assertEqual(self.taken.near(name), name)

    def test_the_attempt_limit_fails_the_draw(self):
        with self.assertRaises(repo.KbError):
            names.draw(self.taken, self.domain, 0, random.Random(1))


class FileTest(unittest.TestCase):
    def test_rows_render_sorted_and_read_back(self):
        rows = [Row("jk00d", "ram", 0xFFFF1034, "brave-otter"),
                Row("7mfk", "tbl", 0xA4AA, "quiet-heron", ("old-name",)),
                Row("7mfk", "fn", 0x26740, "gentle-lynx")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names.write(rows, root)
            text = (root / names.PATH).read_text()
            self.assertEqual(text.splitlines()[0], ",".join(names.HEADER))
            self.assertEqual([line.split(",")[0:2] for line in text.splitlines()[1:]],
                             [["7mfk", "fn"], ["7mfk", "tbl"], ["jk00d", "ram"]])
            self.assertEqual(sorted(names.read(root)), sorted(rows))


@pytest.mark.slow
def test_saved_name_compilation_does_not_import_optional_generators(monkeypatch):
    from kb import compile
    from kb.model import SymbolKey
    original = builtins.__import__
    def importing(name, *args, **kwargs):
        if name.split('.')[0] in ('coolname', 'rapidfuzz'):
            raise ModuleNotFoundError(name)
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', importing)
    spec = importlib.util.spec_from_file_location('_controlled_saved_names', names.__file__)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    model = compile.build()
    module.assign(model, model.names)
    assert model.symbols[SymbolKey('7mfk', 'ram', 0xffff419b)].meaning.name == 'tunneling-swift'
    assert model.symbols[SymbolKey('7mfk', 'ram', 0xffff418f)].meaning.name == 'prehistoric-horse'
    assert module.Taken({'known'}).near('known') == 'known'
    with unittest.TestCase().assertRaises(ModuleNotFoundError):
        module.Taken({'known'}).near('other')
    with unittest.TestCase().assertRaises(ModuleNotFoundError):
        module.draw(module.Taken(()), set(), 1)


if __name__ == "__main__":
    unittest.main()
