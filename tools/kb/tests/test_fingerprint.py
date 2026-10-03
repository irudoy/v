import subprocess
import tempfile
import unittest
from pathlib import Path

from kb import compile, fingerprint, repo
from kb.adapters import architecture, ledgers


class BlobTest(unittest.TestCase):
    def test_blob_hashes_equal_git_hash_object(self):
        for path in ("tools/kb/config.toml", "l0/7mfk/manifest.toml"):
            expected = subprocess.run(["git", "hash-object", path], cwd=repo.ROOT,
                                      capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(fingerprint.blob((repo.ROOT / path).read_bytes()), expected)

    def test_the_inputs_cover_the_model_the_l0_and_the_images(self):
        paths = fingerprint.inputs()
        self.assertIn("kb/names.csv", paths)
        self.assertIn("tools/kb/src/kb/graph.py", paths)
        self.assertIn("l0/jk78c/function_tokens.csv", paths)
        self.assertIn("rom-images/23710-JK08A/1JK08A-20260726-stock.bin", paths)
        self.assertEqual(paths, sorted(set(paths)))

    def test_converted_ledgers_and_curated_names_are_outputs_not_compiler_inputs(self):
        paths = set(compile.inputs())
        self.assertFalse(paths & {path.as_posix() for path in ledgers.PATHS.values()})
        self.assertNotIn("tools/ghidra/symbols/7mfk.csv", paths)
        self.assertIn("tools/ghidra/symbols/1nd.csv", paths)

    def test_architecture_entities_own_the_view_and_read_modules_do_not_change_the_graph(self):
        paths = set(compile.inputs())
        self.assertNotIn(architecture.ARCHITECTURE.as_posix(), paths)
        self.assertNotIn('tools/kb/src/kb/architecture_projection.py', paths)
        self.assertNotIn('tools/kb/src/kb/suggest.py', paths)
        self.assertIn('kb/chain/engine_speed.toml', paths)
        self.assertIn('tools/kb/src/kb/l0graph.py', paths)


class CacheTest(unittest.TestCase):
    def test_a_hash_is_recomputed_only_for_a_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("one\n")
            hashes = fingerprint.Hashes(root)
            first = hashes.of("a.txt")
            hashes.save()
            reread = fingerprint.Hashes(root)
            self.assertEqual(reread.entries["a.txt"][2], first)
            self.assertEqual(reread.of("a.txt"), first)
            self.assertFalse(reread.changed)
            (root / "a.txt").write_text("two, longer\n")
            self.assertNotEqual(reread.of("a.txt"), first)
            self.assertEqual(reread.of("missing.txt"), fingerprint.ABSENT)


class FingerprintTest(unittest.TestCase):
    def test_the_digest_follows_every_pair_and_the_versions(self):
        base = fingerprint.digest([("a", "1"), ("b", "2")])
        self.assertEqual(base, fingerprint.digest([("b", "2"), ("a", "1")]))
        self.assertNotEqual(base, fingerprint.digest([("a", "1"), ("b", "3")]))
        self.assertNotEqual(base, fingerprint.digest([("a", "1")]))

    def test_dirty_lists_inputs_that_differ_from_head(self):
        found = fingerprint.Fingerprint("x", {"a": "1", "b": "2", "c": fingerprint.ABSENT})
        self.assertEqual(fingerprint.dirty(found, {"a": "1", "b": "9"}), ["b"])
        self.assertEqual(found.part(lambda path: path == "a"), fingerprint.digest([("a", "1")]))


if __name__ == "__main__":
    unittest.main()
