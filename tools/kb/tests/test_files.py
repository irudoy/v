import tempfile
import unittest
from pathlib import Path

from kb import checks, compile, names, repo, store
from kb.adapters import files
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


if __name__ == "__main__":
    unittest.main()
