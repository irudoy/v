from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from kb import history, read, refs


INITIAL = """\
[profile.JK00C.rolling_symbols]
apc_output = 0xffff2064
rpm = 0xffff1b06

[profile.JK00D.rolling_symbols]
apc_output = 0xffff206c
rpm = 0xffff1b06

[profile.JK00D_ALIAS]
inherits = "JK00D"
"""
CORRECTED = INITIAL.replace("0xffff2064", "0xffff11f5").replace("0xffff206c", "0xffff11f5")


ROLLING = {"symbols": {"apc_output": "apc_output/ram", "rpm": "rpm/ram"}}


class HistoryGraph:
    def __init__(self, symbols=(), targets=None):
        self.symbols = symbols
        self.targets = {"jk00c": ROLLING, "jk00d": ROLLING} if targets is None else targets

    def run(self, query, **params):
        if ":TARGETS" in query:
            return [{"feature": "rolling_launch", "layout": layout, "target": target}
                    for layout, target in self.targets.items()]
        if "-[:HAS]->(s:Kb:Symbol)" in query:
            return [{"s": symbol} for symbol in self.symbols]
        raise AssertionError(query)


class ProfileHistoryTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.path = self.root / "patches/rom-address-profiles.toml"
        self.path.parent.mkdir()
        self.git("init", "-q", "--initial-branch=master")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "fixture@example.invalid")
        self.layouts = {"7mfk": SimpleNamespace(images=("JK08A",)),
                        "jk00c": SimpleNamespace(images=("JK00C",)),
                        "jk00d": SimpleNamespace(images=("JK00D", "JK00D_ALIAS"))}
        patcher = mock.patch.object(history.repo, "layouts", return_value=self.layouts)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.commit(INITIAL, "Record numeric profile bindings")

    def git(self, *args):
        result = subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=self.root,
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def commit(self, text, title):
        self.path.write_text(text, encoding="utf-8")
        self.git("add", "patches/rom-address-profiles.toml")
        self.git("commit", "-qm", title)
        return self.git("rev-parse", "HEAD")

    def test_corrections_retain_commit_and_layout_without_inheritance_or_format_duplicates(self):
        corrected = self.commit(CORRECTED, "Bind the diagnostic mirror byte")
        self.commit(CORRECTED.replace("0xffff11f5", '"ffff11f5"'),
                    "Use canonical hexadecimal strings")
        changes = history.profile_changes(HistoryGraph(), "apc_output/ram", root=self.root)
        self.assertEqual([(item["layout"], item["old"], item["new"]) for item in changes],
                         [("jk00c", "ffff2064", "ffff11f5"),
                          ("jk00d", "ffff206c", "ffff11f5")])
        self.assertTrue(all(item["commit"] == corrected for item in changes))
        self.assertTrue(all(item["source"] == "patches/rom-address-profiles.toml"
                            and item["table"] == "rolling_symbols"
                            and item["key"] == "apc_output" for item in changes))
        self.assertEqual(len(history.profile_changes(HistoryGraph(), "apc_output/ram", "jk00d",
                                                    self.root)), 1)
        self.assertEqual(history.profile_changes(HistoryGraph(), "rpm/ram", root=self.root), [])

    def test_the_canonical_target_names_the_meaning_of_a_key_that_a_planned_target_omits(self):
        corrected = self.commit(CORRECTED, "Bind the diagnostic mirror byte")
        graph = HistoryGraph(targets={"7mfk": ROLLING, "jk00c": {"status": "planned"},
                                      "jk00d": {"status": "planned"}})
        changes = history.profile_changes(graph, "apc_output/ram", root=self.root)
        self.assertEqual([(item["commit"], item["layout"], item["old"], item["new"])
                          for item in changes],
                         [(corrected, "jk00c", "ffff2064", "ffff11f5"),
                          (corrected, "jk00d", "ffff206c", "ffff11f5")])
        self.assertEqual([item["layout"] for item in history.profile_changes(
            graph, "apc_output/ram", "jk00d", self.root)], ["jk00d"])

    def test_the_target_of_a_layout_restates_the_meaning_of_a_canonical_key(self):
        self.commit(CORRECTED, "Bind the diagnostic mirror byte")
        graph = HistoryGraph(targets={
            "7mfk": ROLLING, "jk00d": {"status": "planned"},
            "jk00c": {"symbols": {"apc_output": "apc_mirror/ram"}}})
        self.assertEqual([item["layout"] for item in history.profile_changes(
            graph, "apc_output/ram", root=self.root)], ["jk00d"])
        self.assertEqual([item["layout"] for item in history.profile_changes(
            graph, "apc_mirror/ram", root=self.root)], ["jk00c"])

    def test_a_first_parent_merge_records_the_accepted_correction_once(self):
        self.git("switch", "-qc", "correction")
        self.commit(CORRECTED, "Bind the diagnostic mirror byte")
        self.git("switch", "-q", "master")
        self.commit(INITIAL + "\n# Profile source note\n", "Describe the profile source")
        self.git("merge", "--no-edit", "correction")
        merged = self.git("rev-parse", "HEAD")
        changes = history.profile_changes(HistoryGraph(), "apc_output/ram", root=self.root)
        self.assertEqual(len(changes), 2)
        self.assertTrue(all(item["commit"] == merged for item in changes))


class FormerReferenceTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.source = "kb/ram/apc_output.toml"
        path = self.root / self.source
        path.parent.mkdir(parents=True)
        path.write_text('''\
former = ["apc_command"]

[[symbol]]
layout = "jk00d"
address = "ffff11f5"
former = ["apc_output/ram/jk00d-ffff206c"]

[[symbol]]
layout = "7mfk"
address = "ffff2022"
former = ["arcane-beaver/ram/7mfk-ffff2022"]
''', encoding="utf-8")
        self.symbol = {"name": "apc_output", "kind": "ram", "layout": "jk00d",
                       "address": 0xffff11f5, "former": ["apc_output"], "src": [self.source]}

    def test_the_owned_entry_retains_its_full_address_and_excludes_other_layouts(self):
        self.assertEqual(history.former_references(self.symbol, [self.source], self.root),
                         ["apc_output/ram/jk00d-ffff206c"])
        other = {**self.symbol, "layout": "1nd", "former": ["legacy_name"]}
        self.assertEqual(history.former_references(other, [self.source], self.root),
                         ["legacy_name"])

    def test_log_of_a_meaning_shows_the_correction_of_its_member_symbol(self):
        meaning = {"key": "apc_output/ram", "former": ["apc_command"], "src": [self.source]}
        graph = HistoryGraph([self.symbol])
        with mock.patch.object(read.refs, "resolve", return_value=refs.Ref("meaning", meaning)), \
                mock.patch.object(history, "profile_changes", return_value=[]):
            answer = read.log(graph, "apc_output", self.root)
        self.assertIn("apc_output/ram/jk00d-ffff206c -> apc_output/ram/jk00d-ffff11f5",
                      answer.text())
        self.assertEqual(answer.data["symbols"][0]["former"],
                         ["apc_output/ram/jk00d-ffff206c"])


if __name__ == "__main__":
    unittest.main()
