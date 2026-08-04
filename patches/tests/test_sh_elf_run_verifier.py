import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

from patches import map_switching_assembly as assembly_model
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/sh-elf-run/verify_map_switching.py"
SPEC = importlib.util.spec_from_file_location(
    "verify_map_switching_sh_elf", MODULE_PATH
)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class ShElfRunVerifierTest(unittest.TestCase):
    def test_preprocessor_translates_only_dialect_differences(self):
        source = """// comment
.align 4
cmp/eq 0x2,r0
add -0x1,r4
or 0xF0,r0
cmp/hs r1,r0
mov #0x5,r1
"""
        self.assertEqual(
            VERIFIER.preprocess_gnu_source(source),
            "\n.balign 4\ncmp/eq #0x2,r0\nadd #-0x1,r4\n"
            "or #0xF0,r0\ncmp/hs r1,r0\nmov #0x5,r1\n",
        )

    def test_high_ram_alias_preserves_low_sixteen_bits(self):
        self.assertEqual(
            VERIFIER.alias_high_ram(0xFFFF5D00), 0x01005D00
        )
        self.assertEqual(
            VERIFIER.alias_high_ram(0xFFFFFFFF), 0x0100FFFF
        )
        with self.assertRaisesRegex(
            VERIFIER.VerificationError, "not a high-RAM address"
        ):
            VERIFIER.alias_high_ram(0xFFFEFFFF)

    def test_ram_relocation_changes_only_declared_long_data(self):
        fixture = bytearray(32)
        fixture[4:8] = (0xFFFF5D00).to_bytes(4, "big")
        fixture[8:12] = (0x00026388).to_bytes(4, "big")
        fixture[12:14] = bytes.fromhex("d304")
        parsed = assembly_model.ParsedSource(
            Path("fixture.s"),
            {},
            (
                assembly_model.SourceStatement(
                    1, 4, "long", "0xFFFF5D00", 4
                ),
                assembly_model.SourceStatement(
                    2, 8, "long", "0x00026388", 4
                ),
                assembly_model.SourceStatement(
                    3, 12, "instruction", "mov.l @(x,pc),r3", 2
                ),
            ),
        )

        count = VERIFIER.relocate_assembly_ram_literals(
            fixture, {"fixture": parsed}
        )

        self.assertEqual(count, 1)
        self.assertEqual(fixture[4:8], (0x01005D00).to_bytes(4, "big"))
        self.assertEqual(fixture[8:12], (0x00026388).to_bytes(4, "big"))
        self.assertEqual(fixture[12:14], bytes.fromhex("d304"))

    def test_dynamic_map_values_differ_without_touching_canonical_data(self):
        fixture = bytearray(range(64))
        original = bytes(fixture)
        family = SimpleNamespace(
            canonical_address=4,
            copies=(16, 24),
            byte_length=4,
        )
        layout = SimpleNamespace(families=(family,))

        changed = VERIFIER.differentiate_map_copies(fixture, layout)

        self.assertEqual(changed, 8)
        self.assertEqual(fixture[4:8], original[4:8])
        self.assertNotEqual(fixture[16:20], original[16:20])
        self.assertNotEqual(fixture[24:28], original[24:28])

    def test_stock_stub_set_is_derived_from_authoritative_hooks(self):
        layout = layout_model.load_layout()
        fixture = bytearray(VERIFIER.ROM_SIZE)

        count = VERIFIER.install_stock_return_stubs(fixture, layout)

        self.assertEqual(count, 7)
        targets = {
            hook.stock
            for hook in layout.hooks
            if hook.key
            in {
                "selector_host_call",
                "startup_initializer",
                "overrun_cut_lookup",
                "overrun_restore_lookup",
                "ignition_lookup_493e8",
                "ignition_lookup_4e1c0_a",
                "ignition_lookup_4e1c0_b",
                "fuel_compensation_lookup_2c648",
                "fuel_compensation_lookup_3be3c",
                "fuel_targets_lookup",
                "cruise_feedback_serializer",
            }
        }
        for target in targets:
            with self.subTest(target=target):
                self.assertEqual(
                    fixture[target : target + 4], VERIFIER.RETURN_STUB
                )

    def test_incident_fixture_keeps_exact_failed_words(self):
        source = (ROOT / "tools/sh-elf-run/delay_slot_probe.s").read_text()
        self.assertIn(".word 0xafac", source)
        self.assertIn(".word SLOT_WORD", source)
        self.assertEqual(VERIFIER.INCIDENT_ADDRESS, 0xD2314)
        self.assertEqual(VERIFIER.INCIDENT_UNSAFE_SLOT_WORD, 0xD304)
        self.assertEqual(VERIFIER.INCIDENT_SAFE_SLOT_WORD, 0x0009)


if __name__ == "__main__":
    unittest.main()
