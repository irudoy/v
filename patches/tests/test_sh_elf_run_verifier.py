import importlib.util
import re
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from patches import map_switching_assembly as assembly_model
from patches import map_switching_layout as layout_model
from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_profile
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/sh-elf-run/verify_map_switching.py"
SPEC = importlib.util.spec_from_file_location(
    "verify_map_switching_sh_elf", MODULE_PATH
)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)

ROLLING_MODULE_PATH = ROOT / "tools/sh-elf-run/verify_rolling_launch.py"
ROLLING_SPEC = importlib.util.spec_from_file_location(
    "verify_rolling_launch_sh_elf", ROLLING_MODULE_PATH
)
ROLLING_VERIFIER = importlib.util.module_from_spec(ROLLING_SPEC)
ROLLING_SPEC.loader.exec_module(ROLLING_VERIFIER)

TELEMETRY_MODULE_PATH = ROOT / "tools/sh-elf-run/verify_can_telemetry.py"
TELEMETRY_SPEC = importlib.util.spec_from_file_location(
    "verify_can_telemetry_sh_elf", TELEMETRY_MODULE_PATH
)
TELEMETRY_VERIFIER = importlib.util.module_from_spec(TELEMETRY_SPEC)
TELEMETRY_SPEC.loader.exec_module(TELEMETRY_VERIFIER)

RUNTIME_MODULE_PATH = ROOT / "tools/sh-elf-run/verify_runtime_targets.py"
RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "verify_runtime_targets_sh_elf", RUNTIME_MODULE_PATH
)
RUNTIME_VERIFIER = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(RUNTIME_VERIFIER)


class ShElfRunVerifierTest(unittest.TestCase):
    def test_preprocessor_translates_only_dialect_differences(self):
        source = """// comment
.align 4
cmp/eq 0x2,r0
add -0x1,r4
or 0xF0,r0
tst 0x80,r0
cmp/hs r1,r0
mov #0x5,r1
"""
        self.assertEqual(
            VERIFIER.preprocess_gnu_source(source),
            "\n.balign 4\ncmp/eq #0x2,r0\nadd #-0x1,r4\n"
            "or #0xF0,r0\ntst #0x80,r0\ncmp/hs r1,r0\n"
            "mov #0x5,r1\n",
        )

    def test_high_ram_alias_preserves_low_sixteen_bits(self):
        self.assertEqual(
            VERIFIER.alias_high_ram(0xFFFF5D00), 0x01005D00
        )
        self.assertEqual(
            VERIFIER.alias_high_ram(0xFFFE8024), 0x01008024
        )
        self.assertEqual(
            VERIFIER.alias_high_ram(0xFFFFFFFF), 0x0100FFFF
        )
        with self.assertRaisesRegex(
            VERIFIER.VerificationError, "not a high-RAM address"
        ):
            VERIFIER.alias_high_ram(0xFFFE7FFF)

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

    def test_serializer_stub_aligns_pc_relative_literal(self):
        status_alias = 0x0100B0F2

        aligned = RUNTIME_VERIFIER._feedback_serializer_stub(
            0x00116E4C, status_alias
        )
        halfword_aligned = RUNTIME_VERIFIER._feedback_serializer_stub(
            0x000CCB32, status_alias
        )

        self.assertEqual(aligned[16:20], status_alias.to_bytes(4, "big"))
        self.assertEqual(
            halfword_aligned[14:18], status_alias.to_bytes(4, "big")
        )

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

        self.assertEqual(count, 8)
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
                "exhaust_cvtc_target_lookup",
                "idle_ignition_lookup",
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

    def test_verifier_uses_only_the_current_composer(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("build_map_switching_", source)
        self.assertIn("map_switching_compose as composer", source)
        self.assertIn("require_composition(layout, blobs)", source)

    def test_runner_pins_default_without_changing_user_context(self):
        main_source = (
            ROOT / "tools/sh-elf-run/run.sh"
        ).read_text(encoding="utf-8")
        external_source = (
            ROOT / "tools/sh-elf-run/run-npkern.sh"
        ).read_text(encoding="utf-8")
        for source in (main_source, external_source):
            with self.subTest(source=source.splitlines()[0]):
                context = source.index("DOCKER_CONTEXT=default")
                export = source.index("export DOCKER_CONTEXT")
                unset = source.index("unset DOCKER_HOST")
                first_docker = source.index("docker build")
                self.assertLess(context, export)
                self.assertLess(export, unset)
                self.assertLess(unset, first_docker)
                self.assertNotIn("docker context use", source)

    def test_npkern_is_an_explicit_revision_locked_external_gate(self):
        main_source = (
            ROOT / "tools/sh-elf-run/run.sh"
        ).read_text(encoding="utf-8")
        external_source = (
            ROOT / "tools/sh-elf-run/run-npkern.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("--with-npkern", main_source)
        self.assertIn("status=SKIP reason=not_requested", main_source)
        self.assertIn(
            "d364011963c1da59a907ca291e1c0602977e9fd0",
            external_source,
        )
        self.assertIn("revision_mismatch", external_source)
        self.assertIn("source_dirty", external_source)
        self.assertIn("status=SKIP reason=source_missing", external_source)

    def test_rolling_launch_composition_lock_matches_verifier(self):
        layout = rolling_launch_layout.load_layout()
        blobs = rolling_launch_assembly.load_payloads(layout)

        result = ROLLING_VERIFIER.require_composition(layout, blobs)

        self.assertEqual(
            result.sha256,
            ROLLING_VERIFIER.EXPECTED_COMPOSITION_SHA256,
        )
        self.assertEqual(result.instruction_count, 878)
        self.assertEqual(result.diagnostic_count, 9)

    def test_rolling_stock_stubs_come_from_both_manifests(self):
        base_layout = layout_model.load_layout()
        rolling_layout = rolling_launch_layout.load_layout()
        fixture = bytearray(VERIFIER.ROM_SIZE)

        count = ROLLING_VERIFIER.install_stock_return_stubs(
            fixture, base_layout, rolling_layout
        )

        self.assertEqual(count, 5)
        for address in (0xD09D8, 0x2C648, 0xA9554, 0x2A892):
            with self.subTest(address=address):
                self.assertEqual(
                    fixture[address : address + 4],
                    ROLLING_VERIFIER.RETURN_STUB,
                )
        self.assertEqual(
            fixture[0xC5372 : 0xC5372 + len(
                ROLLING_VERIFIER.FEEDBACK_SERIALIZER_STUB
            )],
            ROLLING_VERIFIER.FEEDBACK_SERIALIZER_STUB,
        )

    def test_rolling_dynamic_transform_preserves_new_instructions(self):
        base_layout = layout_model.load_layout()
        rolling_layout = rolling_launch_layout.load_layout()
        parsed = rolling_launch_assembly.validate_assembly_sources(
            rolling_layout
        )
        composition = rolling_launch_compose.compose(
            layout=rolling_layout
        )

        fixture, _, relocated, differentiated, stubs = (
            ROLLING_VERIFIER.build_dynamic_fixture(
                composition,
                parsed,
                base_layout,
                rolling_layout,
            )
        )

        self.assertGreater(relocated, 0)
        self.assertGreater(differentiated, 0)
        self.assertEqual(stubs, 5)
        for unit in rolling_layout.assembly_units:
            for statement in parsed[unit.key].statements:
                if statement.kind != "instruction":
                    continue
                self.assertEqual(
                    fixture[statement.address : statement.address + 2],
                    composition.data[
                        statement.address : statement.address + 2
                    ],
                )

    def test_top_level_gate_registers_rolling_launch(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        harness = (
            ROOT / "tools/sh-elf-run/rolling_launch_harness.c"
        ).read_text(encoding="utf-8")

        self.assertIn("verify_rolling_launch.verify", source)
        self.assertIn("rolling_launch_cases", source)
        self.assertIn("cases=%lu", harness)
        self.assertIn("feedback=7", harness)
        self.assertIn("entries=8", harness)

    def test_can_telemetry_composition_lock_matches_verifier(self):
        layout = can_telemetry_layout.load_layout()
        blobs = can_telemetry_assembly.load_payloads(layout)

        result = TELEMETRY_VERIFIER.require_composition(layout, blobs)

        self.assertEqual(
            result.sha256,
            TELEMETRY_VERIFIER.EXPECTED_COMPOSITION_SHA256,
        )
        self.assertEqual(result.instruction_count, 720)
        self.assertEqual(result.code_entry_count, 11)

    def test_can_telemetry_harness_rejects_the_neighbouring_profile_ids(self):
        (profile,) = can_telemetry_profile.load_manifest().profiles
        previous, high = profile.profile_id - 1, profile.profile_id + 1
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")
        published = " ".join(
            (ROOT / "patches/can-telemetry.md").read_text(encoding="utf-8").split()
        )

        for case, value in (
            ("CONFIG_PROFILE_ZERO", 0),
            ("CONFIG_PROFILE_PREVIOUS", previous),
            ("CONFIG_PROFILE_HIGH", high),
        ):
            with self.subTest(case=case):
                self.assertRegex(
                    harness, rf"case {case}:\s+config\[4\] = {value};"
                )
        self.assertRegex(harness, rf"rom_pointer\(CONFIG\)\[4\] = {previous};")
        self.assertIn(
            f"rejection of profile IDs 0, {previous}, and {high} by the capture "
            f"entry and of profile ID {previous} by the control receiver",
            published,
        )

    def test_can_telemetry_latest_wins_writes_the_page_0_word_source(self):
        # The pending and latest-wins cases change the source bytes of the
        # word at bank bytes 3 and 4 and read the newest value back there, so
        # they must write the source the profile reads into that word.
        (field,) = (
            field
            for field in can_telemetry_profile.load_manifest().fields
            if field.page == 0 and field.offset == 3
        )
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")

        self.assertEqual(field.width, 2)
        self.assertIn(
            "ram_pointer(BANK_A)[3] != 0xab || ram_pointer(BANK_A)[4] != 0xcd",
            harness,
        )
        written = re.findall(r"ram_pointer\((0x[0-9a-f]+)U\)\[[01]\] = ", harness)
        self.assertEqual(len(written), 4)
        self.assertEqual(set(written), {f"0x{field.source:08x}"})

    def test_can_telemetry_relocator_supports_generated_pointer_rows(self):
        fixture = bytearray(32)
        fixture[4:16] = bytes.fromhex(
            "ffff5e00000d4e00ffff1234"
        )
        parsed = assembly_model.ParsedSource(
            Path("tables.s"),
            {},
            (
                assembly_model.SourceStatement(
                    1,
                    4,
                    "long",
                    "0xFFFF5E00, 0x000D4E00, 0xFFFF1234",
                    12,
                ),
            ),
        )

        count = TELEMETRY_VERIFIER.relocate_telemetry_ram_literals(
            fixture, {"tables": parsed}
        )

        self.assertEqual(count, 2)
        self.assertEqual(fixture[4:8], bytes.fromhex("01005e00"))
        self.assertEqual(fixture[8:12], bytes.fromhex("000d4e00"))
        self.assertEqual(fixture[12:16], bytes.fromhex("01001234"))

    def test_can_telemetry_dynamic_transform_preserves_instructions(self):
        base_layout = layout_model.load_layout()
        launch_layout = rolling_launch_layout.load_layout()
        telemetry_layout = can_telemetry_layout.load_layout()
        parsed = can_telemetry_assembly.validate_assembly_sources(
            telemetry_layout
        )
        composition = can_telemetry_compose.compose(
            layout=telemetry_layout
        )

        fixture, base_count, launch_count, telemetry_count, _, stubs = (
            TELEMETRY_VERIFIER.build_dynamic_fixture(
                composition,
                base_layout,
                launch_layout,
                telemetry_layout,
                parsed,
            )
        )

        self.assertGreater(base_count, 0)
        self.assertGreater(launch_count, 0)
        self.assertGreater(telemetry_count, 0)
        self.assertEqual(stubs, 10)
        self.assertEqual(
            fixture[
                TELEMETRY_VERIFIER.TRAPA_VECTOR_ADDRESS :
                TELEMETRY_VERIFIER.TRAPA_VECTOR_ADDRESS + 4
            ],
            (0xD4800).to_bytes(4, "big"),
        )
        for unit in telemetry_layout.assembly_units:
            for statement in parsed[unit.key].statements:
                if statement.kind != "instruction":
                    continue
                self.assertEqual(
                    fixture[statement.address : statement.address + 2],
                    composition.data[
                        statement.address : statement.address + 2
                    ],
                )

    def test_top_level_gate_registers_can_telemetry(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        verifier = TELEMETRY_MODULE_PATH.read_text(encoding="utf-8")
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")
        exception = (
            ROOT / "tools/sh-elf-run/invoke_exception.s"
        ).read_text(encoding="utf-8")

        self.assertIn("verify_can_telemetry.verify", source)
        self.assertIn("can_telemetry_cases", source)
        self.assertIn("can_telemetry_harness.c", verifier)
        self.assertIn("cases=78", verifier)
        self.assertIn("trapa #0x40", exception)
        self.assertIn("entries=11", harness)

    def test_top_level_gate_registers_relocated_runtime_targets(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        verifier = (
            ROOT / "tools/sh-elf-run/verify_runtime_targets.py"
        ).read_text(encoding="utf-8")
        map_harness = (
            ROOT / "tools/sh-elf-run/map_switching_harness.c"
        ).read_text(encoding="utf-8")
        telemetry_harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")

        self.assertIn("verify_runtime_targets.verify", source)
        self.assertIn("runtime_target_cases", source)
        self.assertIn("runtime_targets.RELOCATED_ROMS", verifier)
        self.assertIn("TARGET_DUAL_CVTC", map_harness)
        self.assertIn("TARGET_VQ37", map_harness)
        self.assertIn("NATIVE_FUEL_CUT", map_harness)
        self.assertIn("native_fuel=20", map_harness)
        self.assertIn("vq37_native_fuel_cut", verifier)
        self.assertIn("TELEMETRY_TAIL_CHAIN", telemetry_harness)
        self.assertIn("RTE_STUB", verifier)

    def test_harness_configuration_fixture_is_the_manifest_record(self):
        manifest = can_telemetry_profile.load_manifest()
        expected = can_telemetry.Configuration(
            enabled=True,
            can_id=manifest.candidate_can_id,
            profile=manifest.profiles[0].name,
            tick_divisor=manifest.candidate_tick_divisor,
        ).to_bytes(manifest)
        self.assertEqual(
            TELEMETRY_VERIFIER.require_harness_configuration(), expected
        )

    def test_drifted_harness_configuration_fails_the_gate(self):
        source = TELEMETRY_VERIFIER.HARNESS_SOURCE.read_text(
            encoding="utf-8"
        )
        fixture = TELEMETRY_VERIFIER.require_harness_configuration()

        def row(values):
            return ", ".join(f"0x{value:02x}" for value in values)

        def drift(start, stop):
            # The last byte of each span is the field under test.
            changed = bytearray(fixture[start:stop])
            changed[-1] ^= 1
            return row(fixture[start:stop]), row(changed)

        drifts = (
            ("profile CRC", *drift(10, 12)),
            ("page count", *drift(4, 6)),
            ("profile ID", *drift(2, 5)),
        )
        original = TELEMETRY_VERIFIER.HARNESS_SOURCE
        with tempfile.TemporaryDirectory() as directory:
            drifted = Path(directory) / "can_telemetry_harness.c"
            for field, carried, replacement in drifts:
                with self.subTest(field=field):
                    self.assertIn(carried, source)
                    drifted.write_text(
                        source.replace(carried, replacement, 1),
                        encoding="utf-8",
                    )
                    TELEMETRY_VERIFIER.HARNESS_SOURCE = drifted
                    try:
                        with self.assertRaises(
                            TELEMETRY_VERIFIER.VerificationError
                        ):
                            TELEMETRY_VERIFIER.require_harness_configuration()
                    finally:
                        TELEMETRY_VERIFIER.HARNESS_SOURCE = original

    def test_case_counts_are_read_from_the_harness_markers(self):
        self.assertEqual(
            TELEMETRY_VERIFIER.marker_cases(
                TELEMETRY_VERIFIER.REQUIRED_DYNAMIC_MARKER
            ),
            78,
        )
        for output in ("no counter here", "cases=1 and cases=2"):
            with self.subTest(output=output):
                with self.assertRaises(
                    TELEMETRY_VERIFIER.VerificationError
                ):
                    TELEMETRY_VERIFIER.marker_cases(output)
        runtime_source = (
            ROOT / "tools/sh-elf-run/verify_runtime_targets.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("TELEMETRY_CASES", runtime_source)
        self.assertIn("can_verifier.marker_cases(marker)", runtime_source)


if __name__ == "__main__":
    unittest.main()
