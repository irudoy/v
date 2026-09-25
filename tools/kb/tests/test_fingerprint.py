import subprocess
import tempfile
import unittest
from pathlib import Path

from kb import fingerprint, repo


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
