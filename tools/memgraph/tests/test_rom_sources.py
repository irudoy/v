from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import rom_sources  # noqa: E402


class RomSourcesTest(unittest.TestCase):
    def registry(self, text):
        temp = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        temp.write(text)
        temp.close()
        return Path(temp.name)

    def test_unlisted_rom_is_its_own_canonical_source(self):
        model = rom_sources.resolve("JK08A", self.registry(""))
        self.assertEqual(model.target, "JK08A")
        self.assertEqual(model.source, "JK08A")
        self.assertEqual(model.kind, "canonical")
        self.assertFalse(model.inherited)

    def test_exact_code_inheritance_is_explicit(self):
        digest_a = "a" * 64
        digest_b = "b" * 64
        path = self.registry(
            "[inherit.JK03A]\n"
            'source = "JK08A"\n'
            'kind = "exact-code"\n'
            f'target_sha256 = "{digest_a}"\n'
            f'source_sha256 = "{digest_b}"\n'
            'ranges = ["0x0:0x1"]\n'
            'evidence = "verified"\n'
        )
        model = rom_sources.resolve("JK03A", path)
        self.assertEqual(model.source, "JK08A")
        self.assertTrue(model.inherited)

    def test_chained_inheritance_is_rejected(self):
        digest = "a" * 64
        row = (
            'kind = "exact-code"\n'
            f'target_sha256 = "{digest}"\n'
            f'source_sha256 = "{digest}"\n'
            'ranges = ["0x0:0x1"]\n'
            'evidence = "verified"\n'
        )
        path = self.registry(
            '[inherit.A]\nsource = "B"\n' + row
            + '[inherit.B]\nsource = "C"\n' + row
        )
        with self.assertRaisesRegex(
            rom_sources.SourceModelError, "цепочки наследования"
        ):
            rom_sources.read_registry(path)

    def test_materialization_changes_only_prose(self):
        model = rom_sources.SourceModel(
            target="JK03A", source="JK08A", kind="exact-code"
        )
        rows = [{
            "semantics": "JK08A branch",
            "note": "target JK08A",
            "evidence": "registry:defs/JK08A.interp.csv",
        }]
        materialized = rom_sources.materialize_rows(model, "Map", rows)
        self.assertEqual(materialized[0]["semantics"], "JK03A branch")
        self.assertEqual(materialized[0]["note"], "target JK03A")
        self.assertEqual(
            materialized[0]["evidence"],
            "registry:defs/JK08A.interp.csv",
        )
        self.assertEqual(rows[0]["semantics"], "JK08A branch")

    def test_project_registry_is_bound_to_exact_images(self):
        model = rom_sources.resolve("JK03A")
        rom_sources.verify_image_binding(model)
        paths = rom_sources.definition_paths(model)
        self.assertTrue(all(path.is_file() for path in paths.values()))
        for suffix in (
            "axes.csv",
            "direct_lookup_inventory.csv",
            "findings.csv",
            "funcs.csv",
            "interp.csv",
            "map_inventory.26944.csv",
            "map_inventory.26984.csv",
            "map_inventory.26b84.csv",
            "maps.csv",
            "notes.md",
            "overrides.toml",
            "vars.csv",
            "xml",
        ):
            self.assertFalse((ROOT / "defs" / f"JK03A.{suffix}").exists())


if __name__ == "__main__":
    unittest.main()
