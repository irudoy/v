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


class CompilerBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture_inputs = (
            'kb/ram/fixture.toml', 'kb/names.csv',
            'defs/vq37-native-tables.toml', 'tools/kb/config.toml',
            'rom-images/homology.toml', 'rom-images/roms.csv',
            'l0/fixture/funcs.csv', 'rom-images/fixture.bin',
        )
        self.active_modules = (
            'compile.py', 'store.py', 'graph.py', 'derive.py',
            'l0graph.py', 'adapters/files.py',
        )
        self.projection_modules = (
            'ledger_projection.py', 'architecture_projection.py',
        )
        for path in self.fixture_inputs:
            self.write(path, b'fixture input\n')
        for name in self.active_modules + self.projection_modules:
            self.write(f'{compile.PACKAGE}/{name}', b'VALUE = 1\n')
        from unittest.mock import patch
        self.enterContext(patch.object(compile.adapters, 'inputs',
            return_value=['kb/ram/fixture.toml', 'defs/vq37-native-tables.toml']))
        self.enterContext(patch.object(compile.names, 'inputs',
            return_value=['kb/names.csv']))
        self.enterContext(patch.object(repo, 'layouts', return_value={'fixture': None}))
        self.enterContext(patch.object(repo, 'images', return_value={
            'fixture': repo.Image('fixture', self.root / 'rom-images/fixture.bin', 'unused'),
        }))

    def write(self, path, data):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    def test_ledger_rendering_content_does_not_change_compiler_fingerprint(self):
        before = fingerprint.compute(self.root)
        path = f'{compile.PACKAGE}/ledger_projection.py'
        self.write(path, b'VALUE = 200\n')
        after = fingerprint.compute(self.root)
        self.assertNotIn(path, before.blobs)
        self.assertEqual(after.blobs, before.blobs)
        self.assertEqual(after.value, before.value)

    def test_each_active_module_content_changes_compiler_fingerprint(self):
        for name in self.active_modules:
            with self.subTest(module=name):
                before = fingerprint.compute(self.root)
                path = f'{compile.PACKAGE}/{name}'
                self.write(path, b'VALUE = 200\n')
                after = fingerprint.compute(self.root)
                self.assertNotEqual(after.blobs[path], before.blobs[path])
                self.assertNotEqual(after.value, before.value)

    def test_fact_configuration_l0_and_image_content_remain_inputs(self):
        for path in self.fixture_inputs:
            with self.subTest(path=path):
                before = fingerprint.compute(self.root)
                self.write(path, b'changed fixture input with distinct length\n')
                after = fingerprint.compute(self.root)
                self.assertNotEqual(after.blobs[path], before.blobs[path])
                self.assertNotEqual(after.value, before.value)

    def test_an_unknown_nested_python_module_is_included(self):
        before = fingerprint.compute(self.root)
        path = f'{compile.PACKAGE}/extensions/fixture.py'
        self.write(path, b'VALUE = 1\n')
        after = fingerprint.compute(self.root)
        self.assertEqual(after.blobs[path], fingerprint.blob(b'VALUE = 1\n'))
        self.assertEqual(set(after.blobs) - set(before.blobs), {path})
        self.assertNotEqual(after.value, before.value)

    def test_removing_an_active_module_changes_the_fingerprint(self):
        before = fingerprint.compute(self.root)
        path = f'{compile.PACKAGE}/store.py'
        (self.root / path).unlink()
        after = fingerprint.compute(self.root)
        self.assertIn(path, before.blobs)
        self.assertNotIn(path, after.blobs)
        self.assertNotEqual(after.value, before.value)

    def test_removing_projection_modules_keeps_the_fingerprint(self):
        before = fingerprint.compute(self.root)
        for name in self.projection_modules:
            (self.root / compile.PACKAGE / name).unlink()
        after = fingerprint.compute(self.root)
        self.assertEqual(after.blobs, before.blobs)
        self.assertEqual(after.value, before.value)


if __name__ == "__main__":
    unittest.main()
