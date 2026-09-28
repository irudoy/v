import contextlib
import io
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest import mock

from kb import adapters, checks, cli, compile, match, names, repo, store, vocab, write
from kb.adapters import profiles
from kb.model import Meaning, SymbolKey
from kb.repo import KbError

# A table without a semantic name: the search from its symbol on 7mfk finds one
# counterpart on JK00C through 40 masked words.
TABLE, TABLE_HOME, TABLE_JK00C = "astute-toad/tbl", 0x11FF6, 0x142D3
TABLE_EVIDENCE = {"kind": "masked-match", "supports": "homology", "at": "jk00c:0004820a",
                  "to": "7mfk:00047282", "count": 1, "value": 40}
# Named data with files: the search of the first finds one counterpart on
# JK78C and that of the second none on 1ND.
THROTTLE, THROTTLE_HOME, THROTTLE_JK78C = "throttle_runtime/ram", 0xFFFF1796, 0xFFFF17A4
INHIBIT, INHIBIT_HOME = "fuel_inhibit/ram", 0xFFFF2497
# A curated function without a file, whose symbol on 7mfk the base gives a row
# of kb/names.csv: the search from it finds one counterpart on JK78C.
SELECTOR, SELECTOR_HOME, SELECTOR_JK78C = "accelerator_pedal_pair_selector/fn", 0x6EC68, 0x8D384
SPEC = {"kind": "spec", "path": "tools/kb/SPEC.md", "note": "section 7.4"}


def bind(meaning, symbol, **keys):
    return {"cmd": "bind", "meaning": meaning, "symbol": symbol, **keys}


class PlanTest(unittest.TestCase):
    """Operations planned over the working tree with the files in memory; the
    base is the tree before the binding of TABLE on JK00C, where the meaning has
    no file and its 7mfk symbol takes its name from kb/names.csv, and the 7mfk
    symbol of SELECTOR has a row of kb/names.csv."""

    @classmethod
    def setUpClass(cls):
        home = names.Row("7mfk", "tbl", TABLE_HOME, "astute-toad")
        selector = names.Row("7mfk", "fn", SELECTOR_HOME, "probe-heron", ("probe-otter",))
        rows = [row for row in names.read() if row.key not in (home.key, selector.key)]
        rows += [home, selector]
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
        self.assertEqual(sorted(meaning.symbols), ["7mfk", "jk00c"])
        self.assertEqual(result.symbols[key].generated, bound["name"])
        self.assertIn(key, result.file_evidence)
        self.assertEqual(change.lines, [
            f"bind {bound['name']}/tbl/jk00c-{TABLE_JK00C:08x}: masked-match at jk00c:0004820a "
            "to 7mfk:00047282 count 1 value 40"])

    def test_bind_of_a_named_meaning_keeps_the_row_names_as_former_references(self):
        row = self.row("7mfk", "fn", SELECTOR_HOME)
        _, texts, result = self.plan(bind(SELECTOR, f"jk78c:{SELECTOR_JK78C:08x}", note="probe",
                                          level="candidate"))
        document = tomllib.loads(texts[store.path_of("fn", "accelerator_pedal_pair_selector")])
        home, bound = document["symbol"]
        self.assertEqual(home, {"layout": "7mfk", "address": f"{SELECTOR_HOME:08x}", "former": [
            f"{name}/fn/7mfk-{SELECTOR_HOME:08x}" for name in (row.name, *row.former)]})
        self.assertEqual((bound["level"], bound["note"]), ("candidate", "probe"))
        self.assertNotIn("name", bound)
        symbol = result.symbols[SymbolKey("7mfk", "fn", SELECTOR_HOME)]
        self.assertEqual(symbol.former, (row.name, *row.former))
        self.assertEqual(symbol.meaning.key, SELECTOR)

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
                                      "count": 2}, {"cmd": "move"}, code=2).startswith("op 1: "))
        self.assertTrue(self.refused(bind(TABLE, f"jk00c:{TABLE_JK00C:08x}"), {"cmd": "move"},
                                     code=2).startswith("op 2: cmd 'move'"))


def merge(meaning, other, **keys):
    return {"cmd": "merge", "meaning": meaning, "other": other, **keys}


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


class RenameTest(unittest.TestCase):
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
