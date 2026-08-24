import csv
import hashlib
from pathlib import Path
import re
import unittest

from tools import rom_homology


ROOT = Path(__file__).resolve().parents[2]
ROMDIR = ROOT / "rom-images"
PART_RE = re.compile(r"23710-[A-Z0-9]+")
BIN_RE = re.compile(
    r"[A-Z0-9]+-[0-9]{8}-(?:stock|[a-z0-9]+(?:-[a-z0-9]+)*)\.bin"
)


class RomImagesLayoutTest(unittest.TestCase):
    def test_root_contains_only_part_directories_and_manifests(self):
        allowed_files = {
            "README.md",
            "homology.csv",
            "homology.toml",
            "roms.csv",
            "support-matrix.md",
        }
        for path in ROMDIR.iterdir():
            with self.subTest(path=path.name):
                if path.name == ".DS_Store":
                    continue
                if path.is_dir():
                    self.assertRegex(path.name, rf"^{PART_RE.pattern}$")
                else:
                    self.assertIn(path.name, allowed_files)

    def test_part_readmes_are_optional_evidence_files(self):
        readmes = list(ROMDIR.glob("23710-*/README.md"))
        self.assertTrue(readmes)
        for readme in readmes:
            with self.subTest(readme=readme.relative_to(ROMDIR)):
                self.assertTrue(readme.parent.name.startswith("23710-"))
                self.assertGreater(len(readme.read_text(encoding="utf-8")), 0)

    def test_all_binaries_have_canonical_name_and_exact_md5_sidecar(self):
        binaries = list(ROMDIR.glob("23710-*/*.bin"))
        binaries.extend(ROMDIR.glob("23710-*/mods/*/*.bin"))
        self.assertTrue(binaries)
        for binary in binaries:
            with self.subTest(binary=binary.relative_to(ROMDIR)):
                self.assertRegex(binary.name, rf"^{BIN_RE.pattern}$")
                digest = hashlib.md5(binary.read_bytes()).hexdigest()
                sidecar = binary.with_name(binary.name + ".md5")
                self.assertEqual(
                    sidecar.read_text(encoding="ascii"),
                    f"{digest} *{binary.name}\n",
                )

    def test_each_mod_has_own_directory_and_readme(self):
        for mods in ROMDIR.glob("23710-*/mods"):
            with self.subTest(mods=mods.relative_to(ROMDIR)):
                self.assertFalse((mods / "README.md").exists())
                mod_dirs = [path for path in mods.iterdir() if path.is_dir()]
                self.assertTrue(mod_dirs)
                self.assertFalse(any(path.is_file() for path in mods.iterdir()))
                for mod in mod_dirs:
                    self.assertTrue((mod / "README.md").is_file())
                    self.assertEqual(len(list(mod.glob("*.bin"))), 1)

    def test_registry_covers_and_identifies_stock_sources(self):
        with (ROMDIR / "roms.csv").open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertTrue(rows)
        registered_paths = [row["path"] for row in rows]
        self.assertEqual(
            registered_paths,
            sorted(registered_paths),
        )
        self.assertEqual(len(registered_paths), len(set(registered_paths)))
        for row in rows:
            path = Path(row["path"])
            with self.subTest(path=path):
                self.assertEqual(len(path.parts), 2)
                self.assertRegex(path.parts[0], rf"^{PART_RE.pattern}$")
                self.assertRegex(path.name, rf"^{BIN_RE.pattern}$")
                binary = ROMDIR / path
                self.assertTrue(binary.is_file())
                self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
                self.assertEqual(
                    row["sha256"],
                    hashlib.sha256(binary.read_bytes()).hexdigest(),
                )
        stock_sources = {
            str(path.relative_to(ROMDIR))
            for path in ROMDIR.glob("23710-*/*.bin")
        }
        self.assertEqual(set(registered_paths), stock_sources)

    def test_homology_report_matches_registered_stock_images(self):
        expected = rom_homology.build_report()
        self.assertEqual(
            (ROMDIR / "homology.csv").read_text(encoding="utf-8"),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
