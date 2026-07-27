import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "patches" / "apply_immo_off.py"
SPEC = importlib.util.spec_from_file_location("apply_immo_off", MODULE_PATH)
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)


class ImmoOffPatcherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = patcher.load_registry()

    def test_registered_stock_roms_match_flag(self):
        for rom, cfg in patcher.PATCHES.items():
            with self.subTest(rom=rom):
                _path, stock = patcher.load_stock(rom, self.registry)
                self.assertEqual(stock[cfg["offset"]], cfg["stock"])

    def test_default_output_paths_follow_rom_layout(self):
        for rom, image_id in patcher.IMAGE_IDS.items():
            with self.subTest(rom=rom):
                self.assertEqual(
                    patcher.default_output_path(rom),
                    patcher.ROMDIR
                    / f"23710-{rom}"
                    / "mods"
                    / "immo-off"
                    / (
                        f"{image_id}-{patcher.MOD_RELEASE_DATE}"
                        "-immo-off.bin"
                    ),
                )

    def test_jk08a_patch_changes_exactly_one_bit(self):
        _path, stock = patcher.load_stock("JK08A", self.registry)
        patched = patcher.patch_image("JK08A", stock)
        changed = [i for i, pair in enumerate(zip(stock, patched)) if pair[0] != pair[1]]
        self.assertEqual(changed, [0x8725])
        self.assertEqual(stock[0x8725], 0x01)
        self.assertEqual(patched[0x8725], 0x00)
        self.assertEqual((stock[0x8725] ^ patched[0x8725]).bit_count(), 1)

    def test_tracked_jk08a_artifact_is_exact_output(self):
        _path, stock = patcher.load_stock("JK08A", self.registry)
        expected = patcher.patch_image("JK08A", stock)
        output = patcher.default_output_path("JK08A")
        actual = output.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual(
            output.with_name(output.name + ".md5").read_text(encoding="ascii"),
            f"{patcher.md5(expected)} *{output.name}\n",
        )
        self.assertTrue((output.parent / "README.md").is_file())

    def test_rejects_non_stock_flag(self):
        _path, stock = patcher.load_stock("JK08A", self.registry)
        modified = bytearray(stock)
        modified[0x8725] = 0x00
        with self.assertRaisesRegex(patcher.PatchError, "ожидалось 0x01"):
            patcher.patch_image("JK08A", modified)

    def test_output_is_idempotent_and_never_overwritten(self):
        source_path, stock = patcher.load_stock("JK08A", self.registry)
        image = patcher.patch_image("JK08A", stock)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "mods" / "immo-off" / "image.bin"
            self.assertTrue(patcher.write_output(output, image))
            self.assertFalse(patcher.write_output(output, image))
            self.assertTrue(
                patcher.write_mod_readme(
                    output, "JK08A", source_path, image
                )
            )
            self.assertFalse(
                patcher.write_mod_readme(
                    output, "JK08A", source_path, image
                )
            )
            self.assertIn(
                source_path.name,
                (output.parent / "README.md").read_text(encoding="utf-8"),
            )
            output.write_bytes(b"different")
            with self.assertRaisesRegex(patcher.PatchError, "output отличается"):
                patcher.write_output(output, image)

    def test_md5_sidecar_is_idempotent_and_never_overwritten(self):
        _path, stock = patcher.load_stock("JK08A", self.registry)
        image = patcher.patch_image("JK08A", stock)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "image.bin"
            output.write_bytes(image)
            sidecar = output.with_name(output.name + ".md5")
            self.assertTrue(patcher.write_md5_sidecar(output, image))
            self.assertFalse(patcher.write_md5_sidecar(output, image))
            sidecar.write_text("different\n", encoding="ascii")
            with self.assertRaisesRegex(
                patcher.PatchError, "MD5 sidecar отличается"
            ):
                patcher.write_md5_sidecar(output, image)

    def test_romraider_switch_matches_patch(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        self.assertIsNotNone(rom)
        switches = [
            node for node in rom.findall("./table")
            if node.get("type") == "Switch"
            and node.get("storageaddress") == "0x08725"
        ]
        self.assertEqual(len(switches), 1)
        states = [
            (state.get("name"), state.get("data"))
            for state in switches[0].findall("./state")
        ]
        self.assertEqual(
            states,
            [("Enabled (Stock)", "01"), ("Disabled (IMMO OFF)", "00")],
        )
        checksum_types = [
            node.get("type") for node in rom.findall("./checksum")
        ]
        self.assertEqual(checksum_types, ["alt", "alt2"])


if __name__ == "__main__":
    unittest.main()
