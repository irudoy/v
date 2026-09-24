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

    def test_exact_jk08a_export_is_the_research_export_default(self):
        self.assertEqual(
            rom_sources.default_export_dir("JK08A").name,
            "export-JK08A-exact",
        )
        self.assertEqual(
            rom_sources.default_export_dir("JK03A").name,
            "export-JK03A",
        )

    def test_a_rom_reads_the_l0_of_its_layout(self):
        expected = {
            "JK08A": "7mfk", "JK00A": "7mfk", "JK03A": "7mfk", "JK03B": "7mfk",
            "1ND0A": "1nd", "1ND3B": "1nd", "1ME3B": "1me3b",
            "JK00C": "jk00c", "JK00D": "jk00d", "JK78C": "jk78c",
        }
        for rom, layout in expected.items():
            with self.subTest(rom=rom):
                self.assertEqual(rom_sources.layout_of(rom), layout)
                self.assertEqual(rom_sources.l0_dir(rom), ROOT / "l0" / layout)
        with self.assertRaisesRegex(rom_sources.SourceModelError, "no layout"):
            rom_sources.layout_of("ZZ99Z")

    def test_curated_names_are_function_entries_of_the_layout(self):
        names = rom_sources.function_names("JK08A")
        self.assertEqual(names["0002040c"], "periodic_tick_isr")
        self.assertEqual(rom_sources.function_names("JK03A"), names)
        self.assertEqual(rom_sources.function_names("1ND3B")["0011363c"], "hcan1_init")
        self.assertEqual(rom_sources.function_names("JK00C"), {})
        self.assertEqual(rom_sources.function_name(names, "00026740"), "FUN_00026740")

    def test_the_name_registry_rejects_rows_the_l0_does_not_support(self):
        rows = {
            "0000001,first,": "eight lowercase",
            "00000010,1st,": "invalid function name",
            "00000030,third,": "not a function entry",
            "00000010,first,\n00000010,again,": "named twice",
            "00000010,first,\n00000020,first,": "names two functions",
            "00000010,first,a, b": "without commas",
        }
        for body, message in rows.items():
            with self.subTest(body=body):
                root = self.layout_root(body)
                with self.assertRaisesRegex(rom_sources.SourceModelError, message):
                    rom_sources.function_names("T1", root)
        root = self.layout_root("00000020,second,note")
        self.assertEqual(rom_sources.function_names("T1", root), {"00000020": "second"})
        header = self.layout_root("")
        (header / "tools/ghidra/symbols/t1.csv").write_text("# names\naddr,name\n")
        with self.assertRaisesRegex(rom_sources.SourceModelError, "header"):
            rom_sources.function_names("T1", header)

    def layout_root(self, body):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "rom-images").mkdir()
        (root / "rom-images/homology.toml").write_text(
            '[family.t]\nkind = "exact-code"\nmcu = "SH7058"\n'
            'members = ["T1"]\ncanonical = "T1"\nsame_address_inheritance = true\n'
            'layouts = { t1 = "T1" }\n'
        )
        (root / "l0/t1").mkdir(parents=True)
        (root / "l0/t1/funcs.csv").write_text(
            "addr,size,is_thunk,is_external\n"
            "00000010,2,false,false\n00000020,4,false,false\n"
        )
        (root / "tools/ghidra/symbols").mkdir(parents=True)
        (root / "tools/ghidra/symbols/t1.csv").write_text(
            "# names of t1\naddr,name,note\n" + body + "\n"
        )
        return root

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
            rom_sources.SourceModelError, "inheritance chains"
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

    def test_project_registry_is_bound_to_all_exact_family_images(self):
        for rom in ("JK00A", "JK03A", "JK03B"):
            with self.subTest(rom=rom):
                model = rom_sources.resolve(rom)
                rom_sources.verify_image_binding(model)
                paths = rom_sources.definition_paths(model)
                self.assertTrue(all(path.is_file() for path in paths.values()))
                for suffix in (
                    "axes.csv",
                    "diagnostic-bindings.csv",
                    "findings.csv",
                    "funcs.csv",
                    "interp.csv",
                    "notes.md",
                    "overrides.toml",
                    "vars.csv",
                ):
                    self.assertFalse((ROOT / "defs" / f"{rom}.{suffix}").exists())


if __name__ == "__main__":
    unittest.main()
