import contextlib
import io
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest import mock

from kb import checks, cli, compile, match, names, repo, store, vocab, write
from kb.model import Meaning, SymbolKey
from kb.repo import KbError

# A table without a semantic name: the search from its symbol on 7mfk finds one
# counterpart on JK00C through 40 masked words.
TABLE, TABLE_HOME, TABLE_JK00C = "astute-toad/tbl", 0x11FF6, 0x142D3
TABLE_EVIDENCE = {"kind": "masked-match", "supports": "homology", "at": "jk00c:0004820a",
                  "to": "7mfk:00047282", "count": 1, "value": 40}
# Named data whose symbols on 7mfk have rows of kb/names.csv: the search of the
# first finds one counterpart on JK78C and that of the second none on 1ND.
THROTTLE, THROTTLE_HOME, THROTTLE_JK78C = "throttle_runtime/ram", 0xFFFF1796, 0xFFFF17A4
INHIBIT, INHIBIT_HOME = "fuel_inhibit/ram", 0xFFFF2497
SPEC = {"kind": "spec", "path": "tools/kb/SPEC.md", "note": "section 7.4"}


def bind(meaning, symbol, **keys):
    return {"cmd": "bind", "meaning": meaning, "symbol": symbol, **keys}


class PlanTest(unittest.TestCase):
    """Operations planned over the working tree with the files in memory; the
    base is the tree before the binding of TABLE on JK00C, where the meaning has
    no file and its 7mfk symbol takes its name from kb/names.csv."""

    @classmethod
    def setUpClass(cls):
        home = names.Row("7mfk", "tbl", TABLE_HOME, "astute-toad")
        rows = [row for row in names.read() if row.key != home.key] + [home]
        cls.base = compile.build(repo.ROOT, {store.path_of("tbl", "astute-toad"): None,
                                             names.PATH: names.render(rows)})

    def plan(self, *ops):
        return write.plan(list(ops), self.base, write.model_resolver(self.base))

    def refused(self, *ops, code=3):
        with self.assertRaises(KbError) as caught:
            self.plan(*ops)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return str(caught.exception)

    def row(self, layout, kind, address):
        return next(row for row in self.base.names if row.key == (layout, kind, address))

    def test_bind_starts_the_file_of_an_unnamed_meaning_with_its_home_symbol(self):
        change, texts, result = self.plan(bind(TABLE, f"jk00c:{TABLE_JK00C:08x}"))
        path = Path("kb/tbl/astute-toad.toml")
        self.assertEqual(list(texts), [names.PATH, path])
        document = tomllib.loads(texts[path])
        self.assertEqual(texts[path], store.render("tbl", document))
        home, bound = document["symbol"]
        self.assertEqual(home, {"layout": "7mfk", "address": f"{TABLE_HOME:08x}",
                                "name": "astute-toad"})
        self.assertEqual(bound["address"], f"{TABLE_JK00C:08x}")
        self.assertRegex(bound["name"], vocab.GENERATED_NAME)
        self.assertEqual(bound["evidence"], [TABLE_EVIDENCE])
        self.assertNotIn(("7mfk", "tbl", TABLE_HOME),
                         {row.key for row in names.parse(texts[names.PATH])})
        key = SymbolKey("jk00c", "tbl", TABLE_JK00C)
        meaning = result.meaning_of(key)
        self.assertEqual(meaning.key, TABLE)
        self.assertEqual(sorted(meaning.symbols), ["7mfk", "jk00c", "jk00d"])
        self.assertEqual(result.symbols[key].generated, bound["name"])
        self.assertIn(key, result.file_evidence)
        self.assertEqual(change.lines, [
            f"bind {bound['name']}/tbl/jk00c-{TABLE_JK00C:08x}: masked-match at jk00c:0004820a "
            "to 7mfk:00047282 count 1 value 40"])

    def test_bind_of_a_named_meaning_keeps_the_row_names_as_former_references(self):
        row = self.row("7mfk", "ram", THROTTLE_HOME)
        _, texts, result = self.plan(bind(THROTTLE, f"jk78c:{THROTTLE_JK78C:08x}", note="probe",
                                          level="candidate"))
        document = tomllib.loads(texts[Path("kb/ram/throttle_runtime.toml")])
        home, bound = document["symbol"]
        self.assertEqual(home, {"layout": "7mfk", "address": f"{THROTTLE_HOME:08x}", "former": [
            f"{name}/ram/7mfk-{THROTTLE_HOME:08x}" for name in (row.name, *row.former)]})
        self.assertEqual((bound["level"], bound["note"]), ("candidate", "probe"))
        self.assertNotIn("name", bound)
        symbol = result.symbols[SymbolKey("7mfk", "ram", THROTTLE_HOME)]
        self.assertEqual(symbol.former, (row.name, *row.former))
        self.assertEqual(symbol.meaning.key, THROTTLE)

    def test_a_batch_writes_the_statuses_of_one_meaning_into_its_file(self):
        change, texts, result = self.plan(
            {"cmd": "unresolved", "meaning": INHIBIT, "layout": "1nd"},
            {"cmd": "absent", "meaning": INHIBIT, "layout": "1me3b", "evidence": [SPEC]})
        document = tomllib.loads(texts[Path("kb/ram/fuel_inhibit.toml")])
        self.assertEqual(document["status"], [
            {"layout": "1me3b", "state": "absent", "evidence": [SPEC]},
            {"layout": "1nd", "state": "unresolved", "method": "masked-match",
             "target": f"7mfk:{INHIBIT_HOME:08x}", "count": 0,
             "l0": match.l0_digest("1nd")}])
        meaning = result.meaning_of(SymbolKey("7mfk", "ram", INHIBIT_HOME))
        self.assertEqual({layout: status.state for layout, status in meaning.statuses.items()},
                         {"1me3b": "absent", "1nd": "unresolved"})
        self.assertEqual(checks.statuses(result), [])
        self.assertEqual(change.lines, [
            f"unresolved {INHIBIT} on 1nd: masked-match search of 7mfk:{INHIBIT_HOME:08x}, "
            "0 matches",
            f"absent {INHIBIT} on 1me3b: spec path tools/kb/SPEC.md"])

    def test_the_checks_of_the_result_refuse_evidence_that_l0_refutes(self):
        message = self.refused(bind(THROTTLE, "jk78c:ffff17a6", evidence=[{
            **TABLE_EVIDENCE, "at": "jk78c:0002ffb8", "to": "7mfk:0002ce62", "value": 12}]))
        self.assertIn("nothing is written", message)
        self.assertIn("homology: kb/ram/throttle_runtime.toml: jk78c-ffff17a6/ram: "
                      "masked-match evidence", message)
        self.assertIn("which stores ffff17a4, not ffff17a6", message)

    def test_a_status_of_a_registry_refuses_a_symbol_on_its_layout(self):
        meaning = next(meaning for meaning in self.base.meanings
                       if meaning.key == "alpha_n_flow/ram")
        self.assertEqual(meaning.statuses["jk00c"].state, "unresolved")
        message = self.refused(bind("alpha_n_flow/ram", "jk00c:ffff2000", evidence=[
            {"kind": "registry", "path": "patches/rom-address-profiles.toml"}]))
        self.assertIn("symbols: patches/rom-address-profiles.toml: alpha_n_flow/ram: status "
                      "unresolved on jk00c, where the meaning has jk00c-ffff2000/ram", message)

    def test_operations_refuse_what_the_model_contradicts(self):
        self.assertIn("finds jk00c:000142d3 on jk00c, not jk00c:000142d4",
                      self.refused(bind(TABLE, "jk00c:000142d4")))
        self.assertIn("jk00c:0004b27c is vivid-capuchin/fn/jk00c-0004b27c; `kb merge`",
                      self.refused(bind("adaptable-fulmar/fn", "jk00c:0004b27c")))
        self.assertIn(f"{TABLE} has sensible-muskox/tbl/jk00d-000142e3 on jk00d",
                      self.refused(bind(TABLE, "jk00d:000142e4")))
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
                                      "count": 2}, {"cmd": "move"}, code=2).startswith("op 1: "))
        self.assertTrue(self.refused(bind(TABLE, f"jk00c:{TABLE_JK00C:08x}"), {"cmd": "move"},
                                     code=2).startswith("op 2: cmd 'move'"))


class HomeTest(unittest.TestCase):
    def test_a_symbol_that_would_move_the_home_of_an_unnamed_meaning_pins_it(self):
        meaning = Meaning("fn", symbols={"jk00d": object()})
        document = {}
        write.Change._keep_home(meaning, "jk78c", document)
        self.assertEqual(document, {})
        write.Change._keep_home(meaning, "jk00c", document)
        self.assertEqual(document, {"home": "jk00d"})
        document = {}
        write.Change._keep_home(meaning, "7mfk", document)
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
