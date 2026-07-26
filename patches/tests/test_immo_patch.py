import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "patches"))

import apply_immo_patch as patcher  # noqa: E402
import lock_setbit_scan  # noqa: E402


JK08A_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
JK08A_MD5 = "db4eeb16e6385afcb69e70955147c483"
JK08A_CORE_NO_CHECKSUM_SHA256 = "1882b06a6e58f7f0d3bef0e33e7b1df3566572781c6c586b4537052c2abe4879"
JK08A_CORE_SHA256 = "768d8280eb6fd9d2e3261bd3710e8d6034fc1552b61c71c98cb2ce69565eb445"
JK08A_FULL_SHA256 = "27e7e26da038af6e37c45efea2454335a7f4d02007fc51418af7a950d7490396"
JK08A_READBACK_MD5 = "4a5238cf0fcfcfd8d361895778ce4976"
JK08A_READBACK_SHA256 = "b9ae5e0150939d10b189ee6f85aa1410b9288f7206ae4fd94135187f02b8dd08"


class JK08AStockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jk08a = (ROOT / "rom-images" / patcher.ROMS["JK08A"]["stock"]).read_bytes()
        cls.jk03a = (ROOT / "rom-images" / patcher.ROMS["JK03A"]["stock"]).read_bytes()

    def test_hashes_and_embedded_identifiers(self):
        self.assertEqual(len(self.jk08a), 0x100000)
        self.assertEqual(hashlib.sha256(self.jk08a).hexdigest(), JK08A_SHA256)
        self.assertEqual(hashlib.md5(self.jk08a).hexdigest(), JK08A_MD5)
        self.assertEqual(self.jk08a[0x50C6:0x50CF], b"SH705822N")
        self.assertEqual(self.jk08a[0x6F09:0x6F12], b"7MFKAVN86")
        self.assertEqual(self.jk08a[0x2259C:0x225A5], b"7MFKAVN86")
        self.assertEqual(self.jk08a[0x8204:0x820F], b"1JK08A00000")

    def test_exact_code_identity_and_bounded_calibration_delta(self):
        self.assertEqual(self.jk08a[:0x8200], self.jk03a[:0x8200])
        self.assertEqual(self.jk08a[0x20000:], self.jk03a[0x20000:])
        self.assertEqual(
            hashlib.sha256(self.jk08a[:0x8200]).hexdigest(),
            "d3b00d4ea983f0eaaa2085af4c79f087c8a6256379b11e5f962eefd121a4c902",
        )
        self.assertEqual(
            hashlib.sha256(self.jk08a[0x20000:]).hexdigest(),
            "34726ad5cf8a81b632502102887273dad7c45e4e0a4f380163d251b386bb4c9e",
        )
        changed = [off for off, pair in enumerate(zip(self.jk03a, self.jk08a)) if pair[0] != pair[1]]
        self.assertEqual(len(changed), 121)
        self.assertEqual((min(changed), max(changed)), (0x8200, 0x190C9))

    def test_all_five_patch_sites_match_jk03a(self):
        sites = patcher.selected_patches(
            patcher.ROMS["JK08A"], with_l2b=True, with_esc=True
        )
        self.assertEqual(len(sites), 5)
        for off, original, _patched, _label in sites:
            self.assertEqual(self.jk08a[off:off + len(original)], original)
            self.assertEqual(self.jk08a[off:off + len(original)],
                             self.jk03a[off:off + len(original)])

    def test_stock_checksum_fields_are_self_consistent(self):
        self.assertEqual(patcher.checksum_mismatches(self.jk08a), {})
        self.assertEqual(
            patcher.stored_checksums(self.jk08a),
            {
                "sum16_a": 0x2CAE,
                "sum16_b": 0xEEE1,
                "self_a_xor": 0x47A28253,
                "self_a_sum": 0x094AA8CF,
                "self_b_sum": 0xAC399870,
                "self_b_xor": 0x07131670,
            },
        )
        patcher.validate_exact_source("JK08A", patcher.ROMS["JK08A"], self.jk08a)

    def test_sum16_a_and_selftest_a_exclude_sum16_b_storage(self):
        changed = bytearray(self.jk08a)
        changed[0x20000] ^= 0xFF
        changed[0x20001] ^= 0xFF
        self.assertEqual(
            patcher.calculated_checksums(changed),
            patcher.calculated_checksums(self.jk08a),
        )


class JK08APatcherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = (ROOT / "rom-images" / patcher.ROMS["JK08A"]["stock"]).read_bytes()

    def build(self, with_l2b=False, with_esc=False):
        rom = bytearray(self.stock)
        patches = patcher.selected_patches(
            patcher.ROMS["JK08A"], with_l2b=with_l2b, with_esc=with_esc
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(patcher.apply(patches, rom))
        values = patcher.fix_checksums(rom)
        self.assertEqual(patcher.checksum_mismatches(rom), {})
        self.assertFalse(
            patcher.changed_offsets(self.stock, rom)
            - patcher.allowed_offsets(patches, include_checksums=True)
        )
        return bytes(rom), values, patches

    def test_core_without_checksum_golden_image(self):
        image = bytearray(self.stock)
        patches = patcher.selected_patches(patcher.ROMS["JK08A"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(patcher.apply(patches, image))
        self.assertEqual(
            hashlib.sha256(image).hexdigest(),
            JK08A_CORE_NO_CHECKSUM_SHA256,
        )
        self.assertEqual(
            patcher.stored_checksums(image),
            patcher.stored_checksums(self.stock),
        )
        self.assertEqual(
            patcher.checksum_mismatches(image),
            {
                "sum16_b": (0xEEE1, 0x96E6),
                "self_a_xor": (0x47A28253, 0x88AF0B53),
                "self_a_sum": (0x094AA8CF, 0x3A4F1FCF),
            },
        )
        self.assertFalse(
            patcher.changed_offsets(self.stock, image)
            - patcher.allowed_offsets(patches)
        )

    def test_default_output_omits_checksum_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            stock = Path(tmp) / patcher.ROMS["JK08A"]["stock"]
            stock.parent.mkdir(parents=True)
            stock.write_bytes(self.stock)
            captured = io.StringIO()
            with (
                mock.patch.object(patcher, "ROMDIR", tmp),
                contextlib.redirect_stdout(captured),
            ):
                self.assertEqual(patcher.main(["--rom", "JK08A"]), 0)
            self.assertIn("Коррекция делегирована флешеру", captured.getvalue())
            self.assertNotIn("Образ не для записи", captured.getvalue())
            output = Path(tmp) / "JK08A_immo-id-ok.bin"
            self.assertTrue(output.is_file())
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                JK08A_CORE_NO_CHECKSUM_SHA256,
            )

    def test_core_golden_image(self):
        image, values, patches = self.build()
        self.assertEqual(hashlib.sha256(image).hexdigest(), JK08A_CORE_SHA256)
        self.assertEqual(
            values,
            {
                "sum16_a": 0x9EC0,
                "sum16_b": 0x96E6,
                "self_a_xor": 0x88AF0B53,
                "self_a_sum": 0x3A4F1FCF,
                "self_b_sum": 0xAC399870,
                "self_b_xor": 0x07131670,
            },
        )
        for off, _original, patched, _label in patches:
            self.assertEqual(image[off:off + len(patched)], patched)

    def test_full_fallback_golden_image(self):
        image, values, patches = self.build(with_l2b=True, with_esc=True)
        self.assertEqual(len(patches), 5)
        self.assertEqual(hashlib.sha256(image).hexdigest(), JK08A_FULL_SHA256)
        self.assertEqual(
            values,
            {
                "sum16_a": 0xF0D3,
                "sum16_b": 0x6E3C,
                "self_a_xor": 0x88AF8613,
                "self_a_sum": 0x3A4CF725,
                "self_b_sum": 0xAC399870,
                "self_b_xor": 0x07131670,
            },
        )

    def test_checksum_fix_is_idempotent(self):
        image, _values, _patches = self.build(with_l2b=True, with_esc=True)
        repeated = bytearray(image)
        patcher.fix_checksums(repeated)
        self.assertEqual(bytes(repeated), image)

    def test_repeated_patch_application_is_rejected(self):
        image, _values, patches = self.build()
        repeated = bytearray(image)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(patcher.apply(patches, repeated))
        self.assertEqual(bytes(repeated), image)

    def test_exact_source_rejects_corruption_and_wrong_size(self):
        corrupted = bytearray(self.stock)
        corrupted[0x96D4] ^= 1
        with self.assertRaises(ValueError):
            patcher.validate_exact_source("JK08A", patcher.ROMS["JK08A"], corrupted)
        with self.assertRaises(ValueError):
            patcher.validate_exact_source("JK08A", patcher.ROMS["JK08A"], self.stock[:-1])

    def test_unsupported_rom_rejects_checksum_mode(self):
        stock = (ROOT / "rom-images" / patcher.ROMS["JK00D"]["stock"]).read_bytes()
        with self.assertRaisesRegex(ValueError, "нет проверенного exact-layout"):
            patcher.validate_exact_source("JK00D", patcher.ROMS["JK00D"], stock)

    def test_output_is_idempotent_but_never_overwritten(self):
        image, _values, _patches = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            stock = Path(tmp) / "stock.bin"
            output = Path(tmp) / "output.bin"
            stock.write_bytes(self.stock)
            with self.assertRaisesRegex(ValueError, "совпадает со stock"):
                patcher.write_output(stock, stock, image)
            self.assertTrue(patcher.write_output(output, stock, image))
            self.assertFalse(patcher.write_output(output, stock, image))
            with self.assertRaises(FileExistsError):
                patcher.write_output(output, stock, image[:-1])
            self.assertEqual(output.read_bytes(), image)

    def test_failed_publication_leaves_no_final_or_temporary_file(self):
        image, _values, _patches = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            stock = Path(tmp) / "stock.bin"
            output = Path(tmp) / "output.bin"
            stock.write_bytes(self.stock)
            with (
                mock.patch.object(patcher.os, "link", side_effect=OSError("simulated")),
                self.assertRaisesRegex(OSError, "simulated"),
            ):
                patcher.write_output(output, stock, image)
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(tmp).glob("output.bin.*.tmp")), [])


class JK08AWriteReadbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        romdir = ROOT / "rom-images"
        readback_dir = romdir / "1JK08A_8MFK36N15-20260726-write-readbacks"
        cls.checked = (romdir / "JK08A_immo-id-ok_CHECKSUMMED.bin").read_bytes()
        cls.jk00d = (romdir / patcher.ROMS["JK00D"]["stock"]).read_bytes()
        cls.first = (
            readback_dir / "1JK08A_8MFK36N15-20260726-201814.bin"
        ).read_bytes()
        cls.second = (
            readback_dir / "1JK08A_8MFK36N15-20260726-205657.bin"
        ).read_bytes()

    def test_checked_and_autocorrected_readbacks_match(self):
        self.assertEqual(self.first, self.second)
        self.assertEqual(hashlib.md5(self.first).hexdigest(), JK08A_READBACK_MD5)
        self.assertEqual(hashlib.sha256(self.first).hexdigest(), JK08A_READBACK_SHA256)
        self.assertEqual(patcher.checksum_mismatches(self.first), {})

        preserved_ranges = ((0x7000, 0x7030), (0x8080, 0x8100))
        expected_offsets = {
            off
            for start, end in preserved_ranges
            for off in range(start, end)
        }
        self.assertEqual(
            patcher.changed_offsets(self.checked, self.first),
            expected_offsets,
        )

        overlaid = bytearray(self.checked)
        for start, end in preserved_ranges:
            self.assertEqual(self.first[start:end], self.jk00d[start:end])
            overlaid[start:end] = self.jk00d[start:end]
        self.assertEqual(bytes(overlaid), self.first)

        for off, _original, patched, _label in patcher.selected_patches(
            patcher.ROMS["JK08A"]
        ):
            self.assertEqual(self.first[off:off + len(patched)], patched)


class JK08ASoleSetterTest(unittest.TestCase):
    def test_jk08a_has_only_the_expected_lock_setter(self):
        cfg = next(rom for rom in lock_setbit_scan.ROMS if rom["name"] == "JK08A")
        result = lock_setbit_scan.scan(cfg)
        self.assertEqual([item[0] for item in result["setters"]], [0x08D7C8])
        self.assertEqual(result["dangers"], [])
        self.assertEqual(result["unresolved"], [])
        self.assertEqual(
            {item[0] for item in result["absptr"]},
            cfg["benign_store"],
        )
        self.assertEqual(result["lit_hits"], [])

    def test_register_addressed_sh2_byte_store_forms_are_detected(self):
        lock = 0xFFFF4201
        cfg = {"lock": lock, "mask": 0x04, "scan_reg_stores": True}

        def scanned(pointer, instructions):
            image = bytearray(20)
            image[0:2] = b"\xd1\x02"  # mov.l @(2,pc),r1; literal по 0x0c
            image[2:2 + len(instructions)] = instructions
            image[12:16] = pointer.to_bytes(4, "big")
            return lock_setbit_scan.scan_data(cfg, image)["absptr"]

        self.assertEqual(scanned(lock, b"\x21\x20")[0][0], 2)       # mov.b r2,@r1
        self.assertEqual(scanned(lock + 1, b"\x21\x24")[0][0], 2)   # mov.b r2,@-r1
        self.assertEqual(
            scanned(lock - 1, b"\xe0\x04\x81\x10")[0][0], 4       # mov.b r0,@(1,r1)
        )
        self.assertEqual(
            scanned(lock, b"\xe0\x00\x01\x24")[0][0], 4           # mov.b r2,@(r0,r1)
        )


if __name__ == "__main__":
    unittest.main()
