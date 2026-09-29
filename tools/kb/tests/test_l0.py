import csv
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import tomllib
import unittest

from kb import l0, repo
from kb.repo import KbError

IMAGE = b"\x00\x09" * 64
IMAGE_SHA = hashlib.sha256(IMAGE).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def table(header, *rows):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


class SyntheticRoot:
    """A repository root with one layout, `t1`, of image `T1`."""

    def __init__(self, base):
        self.root = Path(base) / "repo"
        root = self.root
        (root / "rom-images/T1").mkdir(parents=True)
        (root / "rom-images/T1/T1.bin").write_bytes(IMAGE)
        write(root / repo.CATALOG, table(("path", "rom", "sha256", "note"),
                                          ("T1/T1.bin", "T1", IMAGE_SHA, "synthetic")))
        write(root / repo.HOMOLOGY, (
            '[family.test]\nkind = "exact-code"\nmembers = ["T1"]\ncanonical = "T1"\n'
            'mcu = "SH7058"\nsame_address_inheritance = false\nlayouts = { t1 = "T1" }\n'
        ))
        write(root / repo.CONFIG, (
            '[l0]\nscripts = ["ExportGraph.java"]\n\n'
            '[l0.census.t1]\ninterp = "defs/T1.interp.csv"\ncopy_helpers = ["22558"]\n'
        ))
        write(root / repo.GHIDRA_PIN, "#!/bin/sh\nGHIDRA_VERSION=12.1.2\n")
        write(root / repo.GHIDRA_SCRIPTS / "ExportGraph.java", "class ExportGraph {}\n")
        write(root / "defs/T1.interp.csv", table(
            ("family", "kernel", "wrapper"),
            ("explicit", "00026944", "00026084"),
            ("explicit", "26984", "26984"),
        ))

    def stage(self, base):
        stage = Path(base) / "stage"
        write(stage / "program.sha256", IMAGE_SHA + "\n")
        write(stage / "program.txt", "T1.bin\n")
        write(stage / "funcs.csv", table(
            ("addr", "name", "size", "is_thunk", "is_external"),
            ("00000104", "FUN_00000104", "4", "false", "false"),
            ("100", "main", "4", "false", "false"),
        ))
        write(stage / "calls.csv", table(("src", "dst"), ("100", "104"), ("100", "104")))
        write(stage / "xrefs.csv", table(("func_addr", "periph_addr", "kind"),
                                         ("100", "FFFF8000", "R")))
        write(stage / "function_signatures.csv", table(
            ("addr", "size", "instructions", "exact_sha256", "mnemonic_sha256", "shape_sha256"),
            ("100", "4", "2", "AB", "cd", "ef"),
        ))
        write(stage / "function_sites.csv", table(
            ("func_addr", "ins_addr", "ordinal", "mnemonic"), ("100", "102", "1", "jsr"),
        ))
        write(stage / "function_references.csv", table(
            ("func_addr", "ins_addr", "ordinal", "mnemonic", "ref_addr", "width",
             "value_hex", "ref_type"),
            ("100", "100", "0", "mov.w", "120", "2", "826E", "read"),
            ("100", "102", "1", "mov.b", "ffff1000", "0", "", "read"),
        ))
        write(stage / "function_tokens.csv", table(
            ("func_addr", "ins_addr", "ordinal", "mnemonic", "shape"),
            ("100", "102", "1", "jsr", "jsr @r3"),
            ("100", "100", "0", "mov.w", "mov.w @(#,pc),r1"),
        ))
        census = ("kernel", "wrapper", "slot", "accessor", "callsite", "func", "bt_r4",
                  "bt_r5", "bt_r6", "df_r4", "df_r5", "df_r6", "df_r7", "k4", "k5", "k6",
                  "k7", "verdict", "branch")
        for kernel in ("26944", "26984"):
            write(stage / f"accessors.{kernel}.csv", table(
                census,
                (kernel, "26084", "", "", "102", "orig", "13d14", "", "", "13d14", "", "",
                 "", "pool", "none", "none", "none", "agree", ""),
            ))
        return stage


class NormalFormTest(unittest.TestCase):
    def test_rows_are_padded_sorted_unique_and_names_are_dropped(self):
        text = table(("addr", "name", "size", "is_thunk", "is_external"),
                     ("1A0", "FUN_1", "10", "false", "false"),
                     ("000000FF", "main", "2", "true", "false"),
                     ("1a0", "FUN_1", "10", "false", "false"))
        normal, rows = l0.normalize("funcs.csv", text, "funcs.csv")
        self.assertEqual(rows, 2)
        self.assertEqual(normal, "addr,size,is_thunk,is_external\n"
                                 "000000ff,2,true,false\n000001a0,10,false,false\n")

    def test_addresses_sort_by_value_and_empty_cells_first(self):
        columns = l0.columns_of("function_references.csv")
        rows = [("00000100", "00000102", "2", "mov.w", "00000120", "2", "ab", "read"),
                ("00000100", "00000102", "2", "mov.w", "00000120", "2", "", "read"),
                ("00000100", "00000100", "10", "mov.b", "ffff1000", "0", "", "read")]
        text, count = l0.render(columns, rows)
        lines = text.splitlines()[1:]
        self.assertEqual(count, 3)
        self.assertTrue(lines[0].startswith("00000100,00000100,10"))
        self.assertTrue(lines[1].endswith(",2,,read"))

    def test_quoting_only_where_a_value_requires_it(self):
        text = table(("func_addr", "ins_addr", "ordinal", "mnemonic", "shape"),
                     ("100", "100", "0", "mov.l", "mov.l r1,@(#,r2)"))
        normal, _ = l0.normalize("function_tokens.csv", text, "function_tokens.csv")
        self.assertIn('"mov.l r1,@(#,r2)"', normal)
        self.assertIn(",mov.l,", normal)

    def test_changed_columns_and_bad_cells_are_refused(self):
        with self.assertRaisesRegex(KbError, "columns differ"):
            l0.normalize("calls.csv", "src,dst,extra\n1,2,3\n", "calls.csv")
        with self.assertRaisesRegex(KbError, "not an address"):
            l0.normalize("calls.csv", "src,dst\n1,zz\n", "calls.csv")
        with self.assertRaisesRegex(KbError, "not a boolean"):
            l0.normalize("funcs.csv", "addr,size,is_thunk,is_external\n1,2,yes,false\n",
                         "funcs.csv")
        with self.assertRaisesRegex(KbError, "empty cell"):
            l0.normalize("calls.csv", "src,dst\n1,\n", "calls.csv")


class LayoutTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.synthetic = SyntheticRoot(self.scratch.name)
        self.root = self.synthetic.root
        self.layout = repo.layout("t1", self.root)
        self.plan = l0.census("t1", self.root)
        self.stage = self.synthetic.stage(self.scratch.name)
        self.target = self.root / repo.L0 / "t1"
        l0.build(self.layout, self.plan, self.stage, self.target, self.root)

    def failures(self):
        return [f"{failure.path}: {failure.key}" for failure in l0.check_all(self.root)]

    def test_census_plan_reads_the_registry(self):
        self.assertEqual(self.plan.kernels, ("00026944", "00026984"))
        self.assertEqual(self.plan.fused, ("00026984",))
        self.assertEqual(self.plan.copy_helpers, ("00022558",))
        self.assertIn("accessors.26944.csv", l0.expected_files(self.plan))

    def test_a_built_layout_passes_and_its_manifest_parses(self):
        self.assertEqual(self.failures(), [])
        manifest = tomllib.loads((self.target / l0.MANIFEST).read_text())
        self.assertEqual(manifest["image_sha256"], IMAGE_SHA)
        self.assertEqual(manifest["program"], "T1.bin")
        self.assertEqual(manifest["ghidra"], "12.1.2")
        self.assertEqual(manifest["census"]["fused"], ["00026984"])
        self.assertEqual(manifest["files"]["calls.csv"]["rows"], 1)
        rendered = l0.render_manifest(manifest)
        self.assertEqual(rendered, (self.target / l0.MANIFEST).read_text())

    def test_a_rebuild_is_byte_identical(self):
        again = Path(self.scratch.name) / "again"
        l0.build(self.layout, self.plan, self.stage, again, self.root)
        self.assertEqual(l0.compare_dirs(again, self.target), [])
        (again / "calls.csv").write_text("src,dst\n")
        self.assertEqual(l0.compare_dirs(again, self.target), ["calls.csv"])

    def test_a_partial_export_is_refused(self):
        (self.stage / "accessors.26984.csv").unlink()
        with self.assertRaisesRegex(KbError, "partial export"):
            l0.build(self.layout, self.plan, self.stage, Path(self.scratch.name) / "x",
                     self.root)

    def test_a_program_of_another_image_is_refused(self):
        write(self.stage / "program.sha256", "0" * 64 + "\n")
        with self.assertRaisesRegex(KbError, "registered T1 image"):
            l0.build(self.layout, self.plan, self.stage, Path(self.scratch.name) / "x",
                     self.root)

    def test_an_edited_file_fails_its_digest(self):
        with (self.target / "calls.csv").open("a") as out:
            out.write("00000104,00000100\n")
        self.assertEqual(self.failures(), ["l0/t1/calls.csv: sha256"])

    def test_a_file_out_of_normal_form_fails_even_with_a_matching_manifest(self):
        path = self.target / "calls.csv"
        path.write_text("src,dst\n104,100\n")
        manifest = (self.target / l0.MANIFEST).read_text()
        entry = tomllib.loads(manifest)["files"]["calls.csv"]["sha256"]
        (self.target / l0.MANIFEST).write_text(
            manifest.replace(entry, repo.sha256_file(path)))
        self.assertEqual(self.failures(), ["l0/t1/calls.csv: normal-form"])

    def test_pins_catalog_scripts_and_census_are_compared(self):
        write(self.root / repo.GHIDRA_PIN, "GHIDRA_VERSION=12.2\n")
        write(self.root / repo.GHIDRA_SCRIPTS / "ExportGraph.java", "changed\n")
        with (self.root / "defs/T1.interp.csv").open("a") as out:
            out.write("explicit,00026a60,00026aa0\n")
        self.assertEqual(self.failures(), [
            "l0/t1/manifest.toml: ghidra",
            "l0/t1/manifest.toml: scripts.ExportGraph.java",
            "l0/t1/manifest.toml: census",
            "l0/t1/manifest.toml: files.accessors.26a60.csv",
        ])

    def test_catalog_digest_change_fails(self):
        catalog = (self.root / repo.CATALOG).read_text()
        write(self.root / repo.CATALOG, catalog.replace(IMAGE_SHA, "1" * 64))
        self.assertEqual(self.failures(), ["l0/t1/manifest.toml: image_sha256"])

    def test_unlisted_missing_and_stray_entries_fail(self):
        write(self.target / "extra.csv", "a\n")
        (self.target / "xrefs.csv").unlink()
        (self.root / repo.L0 / "zz").mkdir()
        self.assertEqual(self.failures(), [
            "l0/t1/extra.csv: file",
            "l0/t1/xrefs.csv: file",
            "l0/zz: layout",
        ])

    def test_a_layout_without_export_fails(self):
        shutil.rmtree(self.target)
        self.assertEqual(self.failures(), ["l0/t1/manifest.toml: layout"])

    def test_the_normal_form_cache_skips_verified_files(self):
        self.assertEqual(self.failures(), [])
        cache = self.root / repo.STATE / "cache" / "l0-normal.json"
        self.assertTrue(cache.is_file())
        self.assertIn(repo.sha256_file(self.target / "calls.csv"), cache.read_text())

    def registry(self, *rows):
        write(self.root / l0.MERGES / "t1.csv",
              "# Fragments of layout t1.\nentry,fragment,note\n"
              + "".join(f"{row}\n" for row in rows))

    def test_the_joins_of_the_merge_registry_are_required(self):
        self.registry("00000100,00000102,in the body",
                      "00000100,00000104,a function entry",
                      "00000106,00000108,no function",
                      "00000100,0000010a,outside the body")
        self.assertEqual(l0.merges("t1", self.root)[0], (0x100, 0x102))
        self.assertEqual(self.failures(), [
            "tools/ghidra/merges/t1.csv: 00000104",
            "tools/ghidra/merges/t1.csv: 00000106",
            "tools/ghidra/merges/t1.csv: 0000010a",
        ])

    def test_a_malformed_or_foreign_merge_registry_fails(self):
        self.registry("100,102,short addresses")
        write(self.root / l0.MERGES / "zz.csv", "entry,fragment,note\n")
        self.assertEqual(self.failures(), [
            "tools/ghidra/merges/t1.csv: syntax",
            "tools/ghidra/merges/zz.csv: layout",
        ])
        self.registry("00000100,00000102,a", "00000104,00000102,b")
        with self.assertRaisesRegex(KbError, "a fragment joins one other function"):
            l0.merges("t1", self.root)


class ReviewTest(unittest.TestCase):
    def export(self, base, functions):
        """An L0 directory of `functions`, {entry: body addresses}."""
        write(base / "funcs.csv", table(
            ("addr", "size", "is_thunk", "is_external"),
            *((f"{entry:08x}", 2 * len(body), "false", "false")
              for entry, body in functions.items())))
        write(base / "function_tokens.csv", table(
            ("func_addr", "ins_addr", "ordinal", "mnemonic", "shape"),
            *((f"{entry:08x}", f"{address:08x}", index, "nop", "nop")
              for entry, body in functions.items()
              for index, address in enumerate(body))))
        return base

    def test_joined_split_and_unchanged_functions_of_symbols(self):
        with tempfile.TemporaryDirectory() as scratch:
            old = self.export(Path(scratch) / "old", {
                0x100: (0x100, 0x102), 0x104: (0x104, 0x106),
                0x120: (0x120, 0x122), 0x130: (0x130,)})
            new = self.export(Path(scratch) / "new", {
                0x100: (0x100, 0x102, 0x104, 0x106), 0x120: (0x120,), 0x122: (0x122,),
                0x130: (0x130,)})
            names = {0x100: "joined", 0x104: "fragment", 0x120: "split", 0x130: "same",
                     0x200: "elsewhere"}
            self.assertEqual(l0.body_changes(old, new, names), [
                "00000100 joined: size 4 -> 8",
                "00000104 fragment: no function entry; the instruction lies in 00000100",
                "00000120 split: size 4 -> 2; new entries in the former body: 00000122",
            ])


if __name__ == "__main__":
    unittest.main()
