import csv
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from tools import rom_homology


def build_image(label, calibration, first="", second=""):
    """Compose a synthetic flash image carrying the given identity strings."""

    data = bytearray(b"\xff" * 0x9000)
    data[
        rom_homology.CALIBRATION_OFFSET : rom_homology.CALIBRATION_OFFSET
        + rom_homology.IDENTITY_WIDTH
    ] = calibration.encode("ascii").ljust(rom_homology.IDENTITY_WIDTH, b"\x00")
    for value, (marker_offset, marker, offset) in zip(
        (first, second), rom_homology.IDENTITY_BLOCKS
    ):
        if not value:
            continue
        data[marker_offset : marker_offset + len(marker)] = marker
        data[offset : offset + rom_homology.IDENTITY_WIDTH] = value.encode(
            "ascii"
        ).ljust(rom_homology.IDENTITY_WIDTH, b"\x00")
    return rom_homology.Image(
        label=label,
        path=Path(f"{label}.bin"),
        registry_path=f"{label}/{label}-20260101-stock.bin",
        sha256="0" * 64,
        data=bytes(data),
    )


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
            "new-rom-intake.md",
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

    def test_every_part_directory_carries_its_evidence_readme(self):
        directories = [
            path
            for path in ROMDIR.iterdir()
            if path.is_dir() and path.name.startswith("23710-")
        ]
        self.assertTrue(directories)
        for directory in directories:
            with self.subTest(directory=directory.name):
                readme = directory / "README.md"
                self.assertTrue(readme.is_file())
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
            reader = csv.DictReader(fh)
            self.assertEqual(reader.fieldnames, ["path", "rom", "sha256", "note"])
            rows = list(reader)
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(path=row["path"], field="note"):
                self.assertTrue(row["note"].strip())
                self.assertNotIn("\n", row["note"])
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


class IdentityStringTest(unittest.TestCase):
    def test_unpopulated_block_reads_as_absent(self):
        image = build_image("JK08A", "1JK08A00000", first="7MFKAVN86")
        self.assertEqual(
            rom_homology.read_identity(image.data),
            ("1JK08A00000", ("7MFKAVN86", "")),
        )

    def test_space_padded_second_block_keeps_its_identifier(self):
        image = build_image(
            "JK00C", "1JK00C00000", first="7MFKAVN86", second="8MFKPCN14  "
        )
        self.assertEqual(
            rom_homology.read_identity(image.data)[1], ("7MFKAVN86", "8MFKPCN14")
        )

    def _families(self, members, software_ids):
        return {
            "family": {
                "kind": "exact-code",
                "members": list(members),
                "canonical": members[0],
                "mcu": "SH7058",
                "flash_size": 0x9000,
                "software_ids": list(software_ids),
                "same_address_inheritance": True,
                "evidence": "synthetic",
            }
        }

    def _layout_family(self, members, inherits, layouts):
        return {
            "members": list(members),
            "canonical": members[0],
            "same_address_inheritance": inherits,
            "layouts": layouts,
        }

    def test_inheriting_family_has_one_layout_of_its_canonical_rom(self):
        rom_homology.validate_layouts(
            self._layout_family(["JK08A", "JK00A"], True, {"7mfk": "JK08A"}),
            "family",
            set(),
        )
        for layouts in ({"7mfk": "JK00A"}, {"7mfk": "JK08A", "jk00a": "JK00A"}):
            with self.subTest(layouts=layouts):
                with self.assertRaises(rom_homology.HomologyError):
                    rom_homology.validate_layouts(
                        self._layout_family(["JK08A", "JK00A"], True, layouts),
                        "family",
                        set(),
                    )

    def test_family_without_inheritance_needs_a_layout_per_member(self):
        rom_homology.validate_layouts(
            self._layout_family(
                ["JK00C", "JK00D"], False, {"jk00c": "JK00C", "jk00d": "JK00D"}
            ),
            "family",
            set(),
        )
        with self.assertRaises(rom_homology.HomologyError) as raised:
            rom_homology.validate_layouts(
                self._layout_family(["JK00C", "JK00D"], False, {"jk00c": "JK00C"}),
                "family",
                set(),
            )
        self.assertIn("its own layout", str(raised.exception))

    def test_layout_ids_are_well_formed_and_unique_across_families(self):
        for layout in ("J", "JK00C", "jk_00c", "toolonglayout"):
            with self.subTest(layout=layout):
                with self.assertRaises(rom_homology.HomologyError):
                    rom_homology.validate_layouts(
                        self._layout_family(["JK78C"], False, {layout: "JK78C"}),
                        "family",
                        set(),
                    )
        with self.assertRaises(rom_homology.HomologyError) as raised:
            rom_homology.validate_layouts(
                self._layout_family(["JK78C"], False, {"jk78c": "JK78C"}),
                "family",
                {"jk78c"},
            )
        self.assertIn("declared twice", str(raised.exception))

    def test_empty_software_ids_are_rejected(self):
        images = {"JK08A": build_image("JK08A", "1JK08A00000", first="7MFKAVN86")}
        with self.assertRaises(rom_homology.HomologyError) as raised:
            rom_homology.validate_software_ids(images, self._families(["JK08A"], []))
        self.assertIn("at least one identifier", str(raised.exception))

    def test_identifier_absent_from_every_member_is_rejected(self):
        images = {"JK08A": build_image("JK08A", "1JK08A00000", first="7MFKAVN86")}
        with self.assertRaises(rom_homology.HomologyError) as raised:
            rom_homology.validate_software_ids(
                images, self._families(["JK08A"], ["8MFK36N15"])
            )
        self.assertIn("no member image carries", str(raised.exception))

    def test_member_without_a_declared_identifier_is_rejected(self):
        images = {
            "JK00C": build_image(
                "JK00C", "1JK00C00000", first="7MFKAVN86", second="8MFKPCN14"
            ),
            "JK00D": build_image(
                "JK00D", "1JK00D00000", first="7MFKAVN86", second="8MFK36N15"
            ),
        }
        with self.assertRaises(rom_homology.HomologyError) as raised:
            rom_homology.validate_software_ids(
                images, self._families(["JK00C", "JK00D"], ["8MFKPCN14"])
            )
        self.assertIn("carry no declared identifier", str(raised.exception))

    def test_declared_identifiers_of_a_split_family_are_accepted(self):
        images = {
            "JK00C": build_image(
                "JK00C", "1JK00C00000", first="7MFKAVN86", second="8MFKPCN14"
            ),
            "JK00D": build_image(
                "JK00D", "1JK00D00000", first="7MFKAVN86", second="8MFK36N15"
            ),
        }
        rom_homology.validate_software_ids(
            images, self._families(["JK00C", "JK00D"], ["8MFKPCN14", "8MFK36N15"])
        )

    def _document(self, rows):
        body = "\n".join(rows)
        return (
            f"{rom_homology.IDENTITY_SECTION}\n\n"
            "| ROM | Calibration | First | Second |\n"
            "| --- | --- | --- | --- |\n"
            f"{body}\n\n### Next section\n"
        )

    def test_published_table_matching_the_images_passes(self):
        images = {"JK08A": build_image("JK08A", "1JK08A00000", first="7MFKAVN86")}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(
                self._document(["| JK08A | `1JK08A00000` | `7MFKAVN86` | empty |"]),
                encoding="utf-8",
            )
            rom_homology.validate_identity_document(images, path)

    def test_published_table_diverging_from_the_image_is_rejected(self):
        images = {"JK08A": build_image("JK08A", "1JK08A00000", first="7MFKAVN86")}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(
                self._document(["| JK08A | `1JK08A00000` | `8MFK36N15` | empty |"]),
                encoding="utf-8",
            )
            with self.assertRaises(rom_homology.HomologyError) as raised:
                rom_homology.validate_identity_document(images, path)
        self.assertIn("while the image carries", str(raised.exception))

    def test_unpublished_image_is_rejected(self):
        images = {
            "JK08A": build_image("JK08A", "1JK08A00000", first="7MFKAVN86"),
            "JK03A": build_image("JK03A", "1JK03A00000", first="7MFKAVN86"),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(
                self._document(["| JK08A | `1JK08A00000` | `7MFKAVN86` | empty |"]),
                encoding="utf-8",
            )
            with self.assertRaises(rom_homology.HomologyError) as raised:
                rom_homology.validate_identity_document(images, path)
        self.assertIn("coverage differs", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
