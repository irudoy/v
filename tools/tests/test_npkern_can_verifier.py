import csv
import importlib.util
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "tools" / "sh-elf-run" / "README.md"
ROM_REGISTRY = ROOT / "rom-images" / "roms.csv"
LOADER_ABI_ROW = re.compile(
    r"^\| (?P<rom>\w+) \| `0x(?P<dispatcher>[0-9A-F]{8})` \| "
    r"`0x(?P<sid>[0-9A-F]{2})` \| `0x(?P<entry>[0-9A-F]{8})` \| "
    r"`0x(?P<handler>[0-9A-F]{8})` \|$",
    re.MULTILINE,
)
MODULE_PATH = ROOT / "tools" / "sh-elf-run" / "verify_npkern_can.py"
SPEC = importlib.util.spec_from_file_location("verify_npkern_can", MODULE_PATH)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


class NpkernCanVerifierTest(unittest.TestCase):
    def test_target_windows_and_write_modes_are_locked(self):
        actual = [
            (
                target.mcu,
                target.read_only,
                target.origin,
                target.boundary,
                target.aligned_limit,
            )
            for target in verifier.TARGETS
        ]
        self.assertEqual(
            actual,
            [
                ("7058", True, 0xFFFF84A0, 0xFFFFA314, 0x1E60),
                ("7059", True, 0xFFFEDE24, 0xFFFF0608, 0x27E0),
                ("7058", False, 0xFFFF84A0, 0xFFFFA314, 0x1E60),
                ("7059", False, 0xFFFEDE24, 0xFFFF0608, 0x27E0),
            ],
        )
        self.assertEqual(len(verifier.LEGACY_PARSER_SHA256), 64)
        self.assertEqual(len(verifier.LEGACY_SH7058_BINARY_SHA256), 64)
        for target in verifier.TARGETS:
            with self.subTest(target=target.name):
                self.assertEqual(
                    target.aligned_limit,
                    (target.boundary - target.origin) & ~0x1F,
                )

    def test_factory_loader_abi_matches_the_stock_images(self):
        section = README.read_text(encoding="utf-8").split(
            "### Factory loader ABI", 1
        )[1].split("\n## ", 1)[0]
        rows = [match.groupdict() for match in LOADER_ABI_ROW.finditer(section)]
        with ROM_REGISTRY.open(newline="", encoding="utf-8") as stream:
            images = {
                row["rom"]: ROOT / "rom-images" / row["path"]
                for row in csv.DictReader(stream)
                if row["rom"]
            }
        self.assertEqual(
            {(row["rom"], row["sid"]) for row in rows},
            {
                (rom, sid)
                for rom in ("JK08A", "1ND0A")
                for sid in ("27", "34", "36", "37", "BF")
            },
        )
        self.assertEqual(len(rows), 10)
        for row in rows:
            with self.subTest(rom=row["rom"], sid=row["sid"]):
                image = images[row["rom"]].read_bytes()
                dispatcher = int(row["dispatcher"], 16)
                entry = int(row["entry"], 16)
                self.assertEqual(
                    int.from_bytes(image[entry : entry + 4], "big"),
                    int(row["handler"], 16),
                )
                loads = [
                    address
                    for address in range(dispatcher, entry, 2)
                    if image[address] >> 4 == 0xD
                    and (address & ~3) + 4 + 4 * image[address + 1] == entry
                ]
                self.assertTrue(loads)

    def test_build_definitions_are_explicit_and_fail_closed(self):
        read_only = verifier.common_definitions(verifier.TARGETS[0])
        write_enabled = verifier.common_definitions(verifier.TARGETS[2])
        self.assertIn("-DNPK_CAN_RX_ID=0x700", read_only)
        self.assertIn("-DNPK_CAN_TX_ID=0x708", read_only)
        self.assertIn("-DNPK_HCAN_CHANNEL=1", read_only)
        self.assertIn("-DNPK_READ_ONLY", read_only)
        self.assertNotIn("-DNPK_READ_ONLY", write_enabled)

    def test_source_contract_rejects_fallback_identifier(self):
        hcan_tokens = (
            "#error NPK_CAN_RX_ID must be set from a passive capture",
            "#error NPK_CAN_TX_ID must be set from a passive capture",
            "#error NPK_HCAN_CHANNEL must be set from firmware analysis and bench wiring",
            "#define NPK_HCAN HCAN1",
            "NPK_HCAN.BCR0.WORD",
            "NPK_HCAN.BCR1.WORD",
            "HCAN_MBC_RECEIVE 2U",
            "HCAN_MBC_TRANSMIT 0U",
            "NPK_HCAN.MCR.BIT.RSTRQ",
            "NPK_HCAN.MB[mailbox].LAFMH.WORD",
            "NPK_HCAN.MB[mailbox].TMSTP = 0",
            "NPK_HCAN.MB[mailbox].MSG_DATA[data_index] = 0",
            "while (result == ISOTP_ERR_TIMEOUT)",
        )
        cmake_tokens = (
            'option(NPK_BUILD_CAN "Build read-only HCAN/ISO-TP kernels" OFF)',
            'option(NPK_BUILD_CAN_WRITE "Build explicitly write-enabled CAN kernels" OFF)',
            "NPK_CAN_RX_ID and NPK_CAN_TX_ID must be explicit IDs from a passive trace",
            "NPK_HCAN_CHANNEL must be explicit (0 or 1) from firmware analysis and bench wiring",
            "lkr_7058_can.ld",
            "lkr_7059_can.ld",
            "NPK_READ_ONLY",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_parser = b"locked legacy parser\n"
            (root / "cmd_parser.c").write_bytes(legacy_parser)
            (root / "transport_hcan.c").write_text(
                "\n".join(hcan_tokens), encoding="utf-8"
            )
            (root / "CMakeLists.txt").write_text(
                "\n".join(cmake_tokens), encoding="utf-8"
            )
            parser_digest = hashlib.sha256(legacy_parser).hexdigest()
            with mock.patch.object(
                verifier, "LEGACY_PARSER_SHA256", parser_digest
            ):
                verifier.require_source_contract(root)
                with (root / "transport_hcan.c").open(
                    "a", encoding="utf-8"
                ) as stream:
                    stream.write("\n#define NPK_CAN_RX_ID 0x7E0U\n")
                with self.assertRaises(verifier.VerificationError):
                    verifier.require_source_contract(root)

    def test_harness_declares_both_parser_markers(self):
        source = verifier.HARNESS.read_text(encoding="utf-8")
        self.assertIn('EXPECT_READ_ONLY ? "RO" : "RW"', source)
        self.assertIn("NPKERN_ISOTP status=PASS", source)
        self.assertIn("NPKERN_CAN_HARNESS status=PASS", source)
        flash_source = verifier.FLASH_GUARD_HARNESS.read_text(encoding="utf-8")
        self.assertIn("NPKERN_FLASH_GUARD status=PASS", flash_source)
        self.assertIn("EXPECT_FLASH_MAX - 127U", flash_source)


if __name__ == "__main__":
    unittest.main()
