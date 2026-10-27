import importlib.util
import re
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

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
from patches import runtime_targets


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


    def test_preprocessor_writes_the_symbols_of_the_included_header(self):
        header = "#define ANSWER 0x2A\n#define RECORD { 0x01, 0x02 }\n"
        source = (
            '.include "answer.h"\ncmp/eq ANSWER,r0\n'
            "mov #ANSWER,r1\n.word ANSWER\n"
        )
        original = assembly_model.INCLUDE_DIR
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "answer.h").write_text(
                header, encoding="utf-8"
            )
            assembly_model.INCLUDE_DIR = Path(directory)
            try:
                self.assertEqual(
                    VERIFIER.preprocess_gnu_source(source),
                    "\ncmp/eq #0x2A,r0\nmov #0x2A,r1\n.word 0x2A\n",
                )
                parsed = assembly_model.parse_source_text(
                    source, "answer.s", 0, 0x10
                )
            finally:
                assembly_model.INCLUDE_DIR = original
        self.assertEqual(
            [(item.line_number, item.text) for item in parsed.statements],
            [(2, "cmp/eq 0x2A,r0"), (3, "mov #0x2A,r1"), (4, "0x2A")],
        )

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

    def _throttle_scalar_fixture(self):
        layout = layout_model.load_layout()
        stock = layout_model.validate_image(layout).data
        composed = bytearray(stock)
        for hook in layout.hooks:
            composed[hook.address:hook.address + hook.width] = hook.replacement.to_bytes(hook.width, "big")
        reconstructed = bytearray(VERIFIER.THROTTLE_SCALAR_POOL + 4 - VERIFIER.THROTTLE_SCALAR_START)
        extent = VERIFIER.THROTTLE_SCALAR_END + 4 - VERIFIER.THROTTLE_SCALAR_START
        reconstructed[:extent] = stock[VERIFIER.THROTTLE_SCALAR_START:VERIFIER.THROTTLE_SCALAR_START + extent]
        reconstructed[-4:] = stock[VERIFIER.THROTTLE_SCALAR_POOL:VERIFIER.THROTTLE_SCALAR_POOL + 4]
        return layout, stock, composed, reconstructed

    def test_throttle_scalar_binds_clamp_and_original_return_boundary(self):
        layout, stock, composed, reconstructed = self._throttle_scalar_fixture()
        VERIFIER.require_throttle_scalar_consumer_bytes(stock, composed, reconstructed, layout)
        for name in ("stock", "composed"):
            for address in range(VERIFIER.THROTTLE_SCALAR_START, VERIFIER.THROTTLE_SCALAR_END + 4, 2):
                with self.subTest(image=name, address=hex(address)):
                    changed = bytearray(stock if name == "stock" else composed)
                    changed[address] ^= 1
                    with self.assertRaisesRegex(VERIFIER.VerificationError, name + " instructions differ"):
                        VERIFIER.require_throttle_scalar_consumer_bytes(
                            changed if name == "stock" else stock,
                            changed if name == "composed" else composed,
                            reconstructed, layout,
                        )

    def test_throttle_scalar_rejects_changed_pointer_and_incomplete_reconstruction(self):
        layout, stock, composed, reconstructed = self._throttle_scalar_fixture()
        for name in ("stock", "composed"):
            changed = bytearray(stock if name == "stock" else composed)
            changed[VERIFIER.THROTTLE_SCALAR_POOL + 3] ^= 1
            with self.assertRaisesRegex(VERIFIER.VerificationError, name + " pool differs"):
                VERIFIER.require_throttle_scalar_consumer_bytes(
                    changed if name == "stock" else stock,
                    changed if name == "composed" else composed,
                    reconstructed, layout,
                )
        for changed in (reconstructed[:-1], reconstructed + b"\0"):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "extent differs"):
                VERIFIER.require_throttle_scalar_consumer_bytes(stock, composed, changed, layout)

    def test_throttle_scalar_fixture_only_translates_pool_and_outside_return_boundary(self):
        layout, stock, composed, reconstructed = self._throttle_scalar_fixture()
        VERIFIER.require_throttle_scalar_consumer_bytes(stock, composed, reconstructed, layout)
        before = bytes(composed)
        VERIFIER.prepare_throttle_scalar_fixture(composed)
        allowed = {address + offset for address in (VERIFIER.THROTTLE_SCALAR_POOL, VERIFIER.THROTTLE_SCALAR_END) for offset in range(4)}
        self.assertLessEqual({i for i, (a, b) in enumerate(zip(before, composed)) if a != b}, allowed)
        self.assertEqual(composed[VERIFIER.THROTTLE_SCALAR_START:VERIFIER.THROTTLE_SCALAR_END], stock[VERIFIER.THROTTLE_SCALAR_START:VERIFIER.THROTTLE_SCALAR_END])
        self.assertEqual(composed[VERIFIER.THROTTLE_SCALAR_END:VERIFIER.THROTTLE_SCALAR_END + 4], VERIFIER.RETURN_STUB)
        expected = VERIFIER.alias_high_ram(int.from_bytes(before[VERIFIER.THROTTLE_SCALAR_POOL:VERIFIER.THROTTLE_SCALAR_POOL + 4], "big"))
        self.assertEqual(int.from_bytes(composed[VERIFIER.THROTTLE_SCALAR_POOL:VERIFIER.THROTTLE_SCALAR_POOL + 4], "big"), expected)

    def test_throttle_scalar_rejects_a_simulator_stub_overlapping_the_clamp(self):
        layout, _, composed, _ = self._throttle_scalar_fixture()

        def overlapping_stub(fixture, layout):
            fixture[VERIFIER.THROTTLE_SCALAR_START:VERIFIER.THROTTLE_SCALAR_START + 4] = VERIFIER.RETURN_STUB
            return 1

        with patch.object(VERIFIER, "install_stock_return_stubs", overlapping_stub):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "simulator fixture changes instructions"):
                VERIFIER.build_dynamic_fixture(SimpleNamespace(data=bytes(composed)), layout, {})

    def test_throttle_scalar_invoke_binding_rejects_changed_or_missing_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)
            elf, invoke = build / "harness.elf", build / "invoke.o"
            image = b"fixture"
            original = bytes.fromhex("000b0009000b0009000b0009")
            linked = bytearray(original)
            missing = False

            def command(arguments, **kwargs):
                if arguments[0] == VERIFIER.OBJCOPY:
                    section = arguments[4]
                    content = image if section == ".rom" else (
                        bytes(linked) if arguments[-2] == elf else original)
                    Path(arguments[-1]).write_bytes(content)
                    return SimpleNamespace(stdout="")
                if arguments[0] == VERIFIER.NM:
                    base = 0x110000 if arguments[-1] == elf else 0
                    names = ("_invoke_r4", "_invoke_r0", "_invoke_throttle_scalar")
                    return SimpleNamespace(stdout="\n".join(
                        f"{base + index * 4:08x} 00000004 T {name}"
                        for index, name in enumerate(names)
                        if not (missing and name == "_invoke_throttle_scalar")))
                if arguments[0] == VERIFIER.OBJDUMP:
                    return SimpleNamespace(stdout="0 .text 0000000c 00110000 00110000 00000000 2**1")
                raise AssertionError(arguments)

            with patch.object(VERIFIER, "run_command", command):
                ranges, words = VERIFIER._invoke_trace_bindings(elf, invoke, image, build)
                self.assertEqual(ranges[-1], (0x110008, 0x11000c))
                self.assertIn(0x11000a, words)
                linked[10] ^= 1
                with self.assertRaisesRegex(VERIFIER.VerificationError, "linked invoke instructions differ: _invoke_throttle_scalar"):
                    VERIFIER._invoke_trace_bindings(elf, invoke, image, build)
                linked[:] = original
                missing = True
                with self.assertRaisesRegex(VERIFIER.VerificationError, "exact invoke function extents"):
                    VERIFIER._invoke_trace_bindings(elf, invoke, image, build)

    def _fuel_cut_fixture(self):
        layout = layout_model.load_layout()
        stock = layout_model.validate_image(layout).data
        composed = bytearray(stock)
        for hook in layout.hooks:
            composed[hook.address:hook.address + hook.width] = hook.replacement.to_bytes(hook.width, "big")
        reconstructed = bytearray(VERIFIER.FUEL_CUT_POOLS[-1] + 4 - VERIFIER.FUEL_CUT_ORIGIN)
        for start, end in (
            (VERIFIER.FUEL_CUT_START, VERIFIER.FUEL_CUT_END),
            (VERIFIER.FUEL_CUT_POOLS[0], VERIFIER.FUEL_CUT_POOLS[-1] + 4),
        ):
            reconstructed[start - VERIFIER.FUEL_CUT_ORIGIN:end - VERIFIER.FUEL_CUT_ORIGIN] = stock[start:end]
        return layout, stock, composed, reconstructed

    def test_fuel_cut_consumer_binds_every_instruction_in_both_images(self):
        layout, stock, composed, reconstructed = self._fuel_cut_fixture()
        VERIFIER.require_fuel_cut_consumer_bytes(stock, composed, reconstructed, layout)
        for name in ("stock", "composed"):
            for address in range(VERIFIER.FUEL_CUT_START, VERIFIER.FUEL_CUT_END, 2):
                with self.subTest(image=name, address=hex(address)):
                    changed = bytearray(stock if name == "stock" else composed)
                    changed[address] ^= 1
                    with self.assertRaisesRegex(VERIFIER.VerificationError, name + " instructions differ"):
                        VERIFIER.require_fuel_cut_consumer_bytes(
                            changed if name == "stock" else stock,
                            changed if name == "composed" else composed,
                            reconstructed, layout,
                        )

    def test_fuel_cut_consumer_rejects_changed_pools_and_fixture_extent(self):
        layout, stock, composed, reconstructed = self._fuel_cut_fixture()
        for name in ("stock", "composed"):
            for address in VERIFIER.FUEL_CUT_POOLS:
                with self.subTest(image=name, address=hex(address)):
                    changed = bytearray(stock if name == "stock" else composed)
                    changed[address + 3] ^= 1
                    with self.assertRaisesRegex(VERIFIER.VerificationError, name + " pool differs"):
                        VERIFIER.require_fuel_cut_consumer_bytes(
                            changed if name == "stock" else stock,
                            changed if name == "composed" else composed,
                            reconstructed, layout,
                        )
        for changed in (reconstructed[:-1], reconstructed + b"\0"):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "extent differs"):
                VERIFIER.require_fuel_cut_consumer_bytes(stock, composed, changed, layout)

    def test_fuel_cut_translation_only_changes_the_three_bound_ram_words(self):
        layout, stock, composed, reconstructed = self._fuel_cut_fixture()
        VERIFIER.require_fuel_cut_consumer_bytes(stock, composed, reconstructed, layout)
        before = bytes(composed)
        self.assertEqual(VERIFIER.relocate_fuel_cut_consumer_literals(composed), 3)
        allowed = {address + offset for address in (0x4f460, 0x4f468, 0x4f46c) for offset in range(4)}
        self.assertLessEqual({i for i, (a, b) in enumerate(zip(before, composed)) if a != b}, allowed)
        self.assertEqual(composed[VERIFIER.FUEL_CUT_START:VERIFIER.FUEL_CUT_END], stock[VERIFIER.FUEL_CUT_START:VERIFIER.FUEL_CUT_END])
        for address in (0x4f460, 0x4f468, 0x4f46c):
            original = int.from_bytes(before[address:address + 4], "big")
            self.assertEqual(int.from_bytes(composed[address:address + 4], "big"), VERIFIER.alias_high_ram(original))

    def test_fuel_cut_rejects_a_simulator_stub_overlapping_tested_instructions(self):
        layout, _, composed, _ = self._fuel_cut_fixture()

        def overlapping_stub(fixture, layout):
            fixture[VERIFIER.FUEL_CUT_START:VERIFIER.FUEL_CUT_START + 4] = VERIFIER.RETURN_STUB
            return 1

        with patch.object(VERIFIER, "install_stock_return_stubs", overlapping_stub):
            with self.assertRaisesRegex(VERIFIER.VerificationError, "simulator fixture changes instructions"):
                VERIFIER.build_dynamic_fixture(SimpleNamespace(data=bytes(composed)), layout, {})

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
        for source, entry in (
            (main_source, 'python3 "$tool_dir/docker_lifecycle.py"'),
            (external_source, 'docker build'),
        ):
            with self.subTest(source=source.splitlines()[0]):
                context = source.index("DOCKER_CONTEXT=default")
                export = source.index("export DOCKER_CONTEXT")
                unset = source.index("unset DOCKER_HOST")
                first_docker = source.index(entry)
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
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")

        for case, value in (
            ("CONFIG_PROFILE_ZERO", "0"),
            ("CONFIG_PROFILE_PREVIOUS", "TELEMETRY_PROFILE_ID - 1"),
            ("CONFIG_PROFILE_HIGH", "TELEMETRY_PROFILE_ID \\+ 1"),
            ("CONFIG_PAGE_COUNT", "TELEMETRY_PAGE_COUNT - 1"),
        ):
            with self.subTest(case=case):
                self.assertRegex(
                    harness, rf"case {case}:\s+config\[[45]\] = {value};"
                )
        self.assertIn(
            "rom_pointer(CONFIG)[4] = TELEMETRY_PROFILE_ID - 1;", harness
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

    def test_can_telemetry_knock_surface_cases_follow_the_entity_files(self):
        # The harness states the slot, the bank byte, and the bits of the
        # knock surface field; they must be those of the profile and of the
        # named bit high_detonation of each layout, and only the telemetry
        # harness of 1ME3B, whose layout moves the bit, takes TARGET_1ME3B.
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")
        block = re.search(
            r"#ifdef TARGET_1ME3B\n(?P<moved>(?:#define KNOCK_SURFACE_\w+ \S+\n)+)"
            r"#else\n(?P<kept>(?:#define KNOCK_SURFACE_\w+ \S+\n)+)#endif\n",
            harness,
        )
        self.assertIsNotNone(block)

        def defines(text):
            return {
                name: int(value, 0)
                for name, value in re.findall(
                    r"#define (KNOCK_SURFACE_\w+) (0x[0-9a-f]+|\d+)U\n", text
                )
            }

        common = defines(harness[: block.start()])
        moved = defines(block.group("moved"))
        kept = defines(block.group("kept"))
        page, offset = runtime_targets.knock_surface_slot()
        bits = {
            runtime_targets.runtime_bindings.layout_of(rom): (
                runtime_targets.knock_surface_bits(
                    runtime_targets.runtime_bindings.layout_of(rom)
                )
            )
            for rom in runtime_targets.SUPPORTED_ROMS
        }
        wire = 1 << bits["7mfk"][1]

        self.assertEqual(
            common,
            {
                "KNOCK_SURFACE_SLOT": page * 7 + offset - 1,
                "KNOCK_SURFACE_BYTE": page * 8 + offset,
                "KNOCK_SURFACE_WIRE": wire,
            },
        )
        self.assertEqual(
            moved,
            {
                "KNOCK_SURFACE_SOURCE": 1 << bits["1me3b"][0],
                "KNOCK_SURFACE_OTHER_BITS_WIRE": 0,
            },
        )
        self.assertEqual(
            kept,
            {
                "KNOCK_SURFACE_SOURCE": wire,
                "KNOCK_SURFACE_OTHER_BITS_WIRE": 0xFF ^ wire,
            },
        )
        self.assertEqual(
            {layout for layout, (source, _) in bits.items() if 1 << source != wire},
            {"1me3b"},
        )
        self.assertEqual(
            {
                RUNTIME_VERIFIER.VQ37_MAP_HARNESS_BY_VARIANT[
                    runtime_targets.load_runtime_target(rom).map_layout.variant
                ][0]
                for rom in runtime_targets.SH7059_1ME3B_ROMS
            },
            {"TARGET_1ME3B"},
        )

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
        self.assertIn("cases=80", verifier)
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


    def test_harness_configuration_fixture_is_the_generated_record(self):
        manifest = can_telemetry_profile.load_manifest()
        expected = can_telemetry.Configuration(
            enabled=True,
            can_id=manifest.candidate_can_id,
            profile=manifest.profiles[0].name,
            tick_divisor=manifest.candidate_tick_divisor,
        ).to_bytes(manifest)
        header = can_telemetry_profile.DEFAULT_IDENTITY.read_text(
            encoding="utf-8"
        )
        record = re.search(
            r"^#define TELEMETRY_CONFIGURATION \{ (?P<bytes>[^}]*) \}$",
            header,
            re.MULTILINE,
        )

        self.assertIsNotNone(record)
        self.assertEqual(
            bytes(int(item, 16) for item in record["bytes"].split(", ")),
            expected,
        )
        self.assertIsNone(TELEMETRY_VERIFIER.require_harness_configuration())

    def test_harness_with_its_own_configuration_fails_the_gate(self):
        source = TELEMETRY_VERIFIER.HARNESS_SOURCE.read_text(
            encoding="utf-8"
        )
        include, fixture = TELEMETRY_VERIFIER.HARNESS_CONFIGURATION
        spelled = (
            "static const uint8_t configuration[16] = { 0x43, 0x54, 0x02, "
            "0x01, 0x07, 0x0B, 0x01, 0x00, 0x06, 0xF0, 0x64, 0x74, 0x54, "
            "0x45, 0x4C, 0x32 };"
        )
        drifts = (
            ("configuration", fixture, spelled),
            ("include", include, ""),
        )
        original = TELEMETRY_VERIFIER.HARNESS_SOURCE
        with tempfile.TemporaryDirectory() as directory:
            drifted = Path(directory) / "can_telemetry_harness.c"
            for name, carried, replacement in drifts:
                with self.subTest(drift=name):
                    self.assertEqual(source.count(carried), 1)
                    drifted.write_text(
                        source.replace(carried, replacement),
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

    def test_case_parser_requires_one_numeric_marker(self):
        self.assertEqual(TELEMETRY_VERIFIER.marker_cases("controlled cases=37"), 37)
        for output in ("no counter here", "cases=1 and cases=2"):
            with self.subTest(output=output):
                with self.assertRaises(TELEMETRY_VERIFIER.VerificationError):
                    TELEMETRY_VERIFIER.marker_cases(output)

    @staticmethod
    def can_wrapper_pc_fixture():
        image = bytearray(0x400)
        rows = ((0x100, 9, "nop"), (0x102, 0xd004, "mov.l @(main_callee,pc),r0"),
                (0x104, 0x400b, "jsr @r0"), (0x106, 9, "nop"),
                (0x108, 11, "rts"), (0x10a, 9, "nop"),
                (0x180, 0xd003, "mov.l @(knock_callee,pc),r0"),
                (0x182, 0x400b, "jsr @r0"), (0x184, 9, "nop"),
                (0x186, 11, "rts"), (0x188, 9, "nop"),
                (0x200, 0x8bfe, "bf repeat"),
                (0x202, 0xd004, "mov.l @(startup_callee,pc),r0"),
                (0x204, 0x400b, "jsr @r0"), (0x206, 9, "nop"),
                (0x208, 11, "rts"), (0x20a, 9, "nop"))
        statements = []
        for index, (pc, word, text) in enumerate(rows):
            image[pc:pc + 2] = word.to_bytes(2, "big")
            statements.append(assembly_model.SourceStatement(index, pc, "instruction", text, 2))
        labels = {"main_callee": 0x114, "knock_callee": 0x190,
                  "startup_callee": 0x214, "repeat": 0x200}
        for pc, target in ((0x114, 0x300), (0x190, 0x304), (0x214, 0x308)):
            image[pc:pc + 4] = target.to_bytes(4, "big")
            image[target:target + 4] = TELEMETRY_VERIFIER.RETURN_STUB
            statements.append(assembly_model.SourceStatement(30, pc, "long", hex(target), 4))
        labels["ram_operand"] = 0x230
        image[0x230:0x234] = (0xffff5e00).to_bytes(4, "big")
        statements.append(assembly_model.SourceStatement(31, 0x230, "long", "0xffff5e00", 4))
        parsed = {"wrappers": assembly_model.ParsedSource(Path("CAN-wrappers.s"), labels, tuple(statements))}
        names = dict(main_wrapper=0x100, knock_wrapper=0x180, startup_wrapper=0x200)
        layout = SimpleNamespace(
            assembly_unit_by_key={"wrappers": SimpleNamespace(code_regions=tuple(names))},
            code_region_by_key={name: SimpleNamespace(entry=pc) for name, pc in names.items()})
        invokes = {0x4000: 0x400b, 0x4002: 9, 0x4004: 9}
        def events(pcs, delays):
            return [(pc, int.from_bytes(image[pc:pc + 2], "big"), int(pc in delays)) for pc in pcs]
        prefix = [(0x4000, 0x400b, 0), (0x4002, 9, 1)]
        suffix = [(0x4004, 9, 0)]
        main = prefix + events((0x100, 0x102, 0x104, 0x106, 0x300, 0x302, 0x108, 0x10a), {0x106, 0x302, 0x10a}) + suffix
        knock = prefix + events((0x180, 0x182, 0x184, 0x304, 0x306, 0x186, 0x188), {0x184, 0x306, 0x188}) + suffix
        startup = prefix + events((0x200, 0x200, 0x202, 0x204, 0x206, 0x308, 0x30a, 0x208, 0x20a), {0x206, 0x30a, 0x20a}) + suffix
        return image, layout, parsed, invokes, main, knock, startup

    def test_can_wrapper_coverage_requires_entries_instructions_and_loop_outcomes(self):
        image, layout, parsed, invokes, main, knock, startup = self.can_wrapper_pc_fixture()
        require = lambda records: TELEMETRY_VERIFIER.require_wrapper_coverage(records, image, layout, parsed, invokes)
        self.assertEqual(require(main + knock + startup), dict(
            entries=3, instructions=17, outcomes=2, delay_slots=6, call_return_paths=6))
        for records, message in ((knock + startup, "uncovered CAN wrapper entry 0x00000100"),
                                 (main + knock + startup[:2] + startup[3:], "uncovered CAN wrapper outcome"),
                                 ([row for row in main if row[0] != 0x102] + knock + startup, "uncovered CAN wrapper instruction 0x00000102")):
            with self.subTest(message=message), self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, message):
                require(records)

    def test_can_wrapper_coverage_rejects_wrong_opcode_delay_callee_and_return(self):
        image, layout, parsed, invokes, main, knock, startup = self.can_wrapper_pc_fixture()
        errors = (TELEMETRY_VERIFIER.VerificationError, TELEMETRY_VERIFIER.base_verifier.VerificationError)
        for pc, target, delay, message in ((0x102, 0x102, 0, "executed CAN opcode"),
                                           (0x106, 0x106, 0, "missing executed delay slot"),
                                           (0x300, 0x304, 0, "executed CAN callee"),
                                           (0x108, 0x102, 0, "executed CAN return")):
            changed = list(main)
            index = next(index for index, row in enumerate(changed) if row[0] == pc)
            word = 9 if pc == 0x102 else int.from_bytes(image[target:target + 2], "big")
            changed[index] = (target, word, delay)
            with self.subTest(message=message), self.assertRaisesRegex(errors, message):
                TELEMETRY_VERIFIER.require_wrapper_coverage(changed + knock + startup, image, layout, parsed, invokes)
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "lacks its invoke frame"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(main[2:] + knock + startup, image, layout, parsed, invokes)
        changed = bytearray(image)
        changed[0x350:0x356] = bytes.fromhex("400b00090009")
        foreign = [(0x350, 0x400b, 0), (0x352, 9, 1)] + main[2:]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "origin is outside bound invoke code"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(foreign + knock + startup, changed, layout, parsed, invokes)
        changed = bytearray(image)
        changed[0x114:0x118] = (0x304).to_bytes(4, "big")
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "executed CAN callee"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(main + knock + startup, changed, layout, parsed, invokes)

    def test_can_wrappers_reject_post_stub_instruction_changes_and_new_transfer_forms(self):
        image, layout, parsed, invokes, main, knock, startup = self.can_wrapper_pc_fixture()
        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(image, image, parsed)
        for row in parsed["wrappers"].statements:
            changed = bytearray(image)
            changed[row.address] ^= 1
            with self.subTest(pc=hex(row.address)):
                if row.kind == "instruction":
                    with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes CAN wrapper instruction"):
                        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed)
                elif row.address == parsed["wrappers"].labels["ram_operand"]:
                    changed[row.address:row.address + 4] = VERIFIER.alias_high_ram(0xffff5e00).to_bytes(4, "big")
                    TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed)
                else:
                    original_target = int.from_bytes(image[row.address:row.address + 4], "big")
                    other_target = 0x304 if original_target != 0x304 else 0x300
                    changed[row.address:row.address + 4] = other_target.to_bytes(4, "big")
                    self.assertTrue(all(changed[item.address:item.address + 2] == image[item.address:item.address + 2]
                                        for item in parsed["wrappers"].statements if item.kind == "instruction"))
                    with tempfile.TemporaryDirectory() as directory, patch.object(TELEMETRY_VERIFIER.base_verifier, "run_command") as command:
                        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes CAN wrapper control literal"):
                            TELEMETRY_VERIFIER.build_and_run_dynamic_harness(
                                changed, Path(directory), layout=layout, parsed_by_unit=parsed, composed_image=image)
                        command.assert_not_called()
        original = parsed["wrappers"]
        for pc, text, message in ((0x104, "jsr @r2", "unbound CAN wrapper call"),
                                  (0x108, "rte", "unsupported CAN wrapper transfer")):
            altered = {"wrappers": assembly_model.ParsedSource(original.path, original.labels, tuple(
                assembly_model.SourceStatement(row.line_number, row.address, row.kind,
                    text if row.address == pc else row.text, row.size) for row in original.statements))}
            with self.subTest(text=text), self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, message):
                TELEMETRY_VERIFIER.require_wrapper_coverage(main + knock + startup, image, layout, altered, invokes)
        changed = bytearray(image)
        changed[0x300:0x302] = (0x002b).to_bytes(2, "big")
        altered = [(pc, 0x002b if pc == 0x300 else word, delay) for pc, word, delay in main]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "unsupported transfer in active CAN wrapper frame"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(altered + knock + startup, changed, layout, parsed, invokes)

    def _throttle_cluster_fixture(self):
        layout = layout_model.load_layout()
        stock = layout_model.validate_image(layout).data
        composed = bytearray(stock)
        for hook in layout.hooks:
            composed[hook.address:hook.address + hook.width] = hook.replacement.to_bytes(hook.width, "big")
        reconstructed = bytearray(0x75c48 - VERIFIER.THROTTLE_CLUSTER_ORIGIN)
        for start, end in (*VERIFIER.THROTTLE_CLUSTER_WINDOWS,
                           *((pc, pc + width) for pc, width in VERIFIER.THROTTLE_CLUSTER_POOLS)):
            reconstructed[start - VERIFIER.THROTTLE_CLUSTER_ORIGIN:end - VERIFIER.THROTTLE_CLUSTER_ORIGIN] = stock[start:end]
        offset = VERIFIER.THROTTLE_CLUSTER_BOUNDARY - VERIFIER.THROTTLE_CLUSTER_ORIGIN
        reconstructed[offset:offset + 4] = bytes.fromhex("a1da0009")
        return layout, stock, composed, reconstructed

    def test_throttle_cluster_rejects_instruction_and_operand_drift(self):
        layout, stock, composed, reconstructed = self._throttle_cluster_fixture()
        VERIFIER.require_throttle_cluster_bytes(stock, composed, reconstructed, layout)
        addresses = [(pc, "instructions") for start, end in VERIFIER.THROTTLE_CLUSTER_WINDOWS
                     for pc in range(start, end, 2)]
        addresses += [(pc, "pool") for pc, width in VERIFIER.THROTTLE_CLUSTER_POOLS]
        for name, original in (("stock", stock), ("composed", composed)):
            for pc, kind in addresses:
                changed = bytearray(original)
                changed[pc] ^= 1
                with self.subTest(image=name, pc=hex(pc)), self.assertRaisesRegex(
                        VERIFIER.VerificationError, name + " " + kind + " differ"):
                    VERIFIER.require_throttle_cluster_bytes(
                        changed if name == "stock" else stock,
                        changed if name == "composed" else composed, reconstructed, layout)
        for offset in (0, 2):
            changed = bytearray(reconstructed)
            changed[0x7587a - VERIFIER.THROTTLE_CLUSTER_ORIGIN + offset] ^= 1
            with self.subTest(boundary=offset), self.assertRaisesRegex(
                    VERIFIER.VerificationError, "assembled boundary differs"):
                VERIFIER.require_throttle_cluster_bytes(stock, composed, changed, layout)

    def test_throttle_cluster_translation_preserves_windows_and_checks_final_stubs(self):
        layout, stock, composed, reconstructed = self._throttle_cluster_fixture()
        before = bytes(composed)
        VERIFIER.install_throttle_cluster_fixture(composed, reconstructed)
        allowed = set(range(0x7587a, 0x7587e)) | set(range(0x75958, 0x7595c)) | set(range(0x75964, 0x75968))
        self.assertLessEqual({i for i, (a, b) in enumerate(zip(before, composed)) if a != b}, allowed)
        self.assertEqual(composed[0x75958:0x7595c], bytes.fromhex("0100128c"))
        self.assertEqual(composed[0x75964:0x75968], bytes.fromhex("01005d20"))
        self.assertEqual(composed[0x7587a:0x7587e], bytes.fromhex("a1da0009"))
        for pc in (0x7584e, 0x75c46, 0x7587a):
            def overlap(fixture, layout, pc=pc):
                fixture[pc:pc + 2] = b"\0\0"
                return 1
            with patch.object(VERIFIER, "install_stock_return_stubs", overlap), self.subTest(pc=hex(pc)):
                with self.assertRaisesRegex(VERIFIER.VerificationError, "throttle-cluster simulator"):
                    VERIFIER.build_dynamic_fixture(SimpleNamespace(data=before), layout, {},
                        throttle_reconstruction=reconstructed)

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_throttle_cluster_trace_requires_both_successors_and_real_delay_slots(self):
        _layout, _stock, fixture, reconstructed = self._throttle_cluster_fixture()
        VERIFIER.install_throttle_cluster_fixture(fixture, reconstructed)
        payload, parsed, old_invokes, taken, untaken = self.pc_fixture()
        fixture[:len(payload)] = payload
        rebase = lambda pc: pc + 0x10c000 if pc in old_invokes else pc
        invokes = {rebase(pc): word for pc, word in old_invokes.items()}
        base = [(rebase(pc), word, delay) for pc, word, delay in taken + untaken]
        def events(pcs):
            return [(pc, int.from_bytes(fixture[pc:pc + 2], "big"),
                     int(pc in (0x75878, 0x7587c, 0x75c46))) for pc in pcs]
        entry = [(0x110000, 0x400b, 0), (0x110002, 9, 1)]
        tail = events(range(0x75c32, 0x75c48, 2)) + [(0x110004, 9, 0)]
        sentinel = entry + events(range(0x7584e, 0x7587a, 2)) + tail
        enabled = entry + events(range(0x7584e, 0x75870, 2)) + events((0x7587a, 0x7587c)) + tail
        require = lambda records: VERIFIER.require_payload_coverage(
            records, fixture, parsed, invokes, throttle_cluster=True, composed_image=bytes(fixture))
        result = require(base + sentinel + enabled)
        self.assertEqual(result["instructions"], 9 + sum(
            (end - start) // 2 for start, end in VERIFIER.THROTTLE_CLUSTER_WINDOWS))
        self.assertEqual(result["fixture_boundary_instructions"], 2)
        self.assertEqual(result["outcomes"], 4)
        self.assertEqual(result["delay_slots"], 6)
        with self.assertRaisesRegex(VERIFIER.VerificationError, "uncovered branch outcome 0x0007586e->0x0007587a"):
            require(base + sentinel)
        with self.assertRaisesRegex(VERIFIER.VerificationError, "uncovered entry 0x0007584e"):
            require(base)
        for pc in (0x75878, 0x75c46):
            records = [(address, word, 0 if address == pc else delay)
                       for address, word, delay in base + sentinel + enabled]
            with self.subTest(pc=hex(pc)), self.assertRaisesRegex(VERIFIER.VerificationError, "missing executed delay slot"):
                require(records)

    def adapter_pc_fixture(self, *, secondary=False):
        original, parsed, invokes, taken, untaken = self.pc_fixture()
        image = bytearray(original.ljust(0x500, b"\0"))
        regions, units = {}, {}
        for key, pc in (("startup_wrapper", 0x100), ("limiter_commit", 0x200)):
            regions[key] = SimpleNamespace(entry=pc, span=SimpleNamespace(start=pc, end=pc + 0x10))
            units[key] = SimpleNamespace(code_regions=(key,))
        helper = 0x220
        parsed["adapter_select_helper"] = assembly_model.ParsedSource(Path("helper.s"), {}, (
            assembly_model.SourceStatement(1, helper, "instruction", "jmp @r3", 2),
            assembly_model.SourceStatement(2, helper + 2, "instruction", "nop", 2)))
        image[helper:helper + 4] = bytes.fromhex("432b0009")
        regions["adapter_select_helper"] = SimpleNamespace(entry=helper, span=SimpleNamespace(start=helper, end=helper + 4))
        units["adapter_select_helper"] = SimpleNamespace(code_regions=("adapter_select_helper",))
        names = ("overrun_adapter", "ignition_adapter", "fuel_compensation_adapter", "cvtc_target_adapter", "full_dfco_adapter", "idle_ignition_adapter")
        if secondary:
            names += ("secondary_cvtc_target_adapter",)
        traces = {}
        def event(pc, delay=0):
            word = invokes[pc] if pc in invokes else int.from_bytes(image[pc:pc + 2], "big")
            return pc, word, delay
        for number, name in enumerate(names):
            entry, stock = 0x240 + number * 0x20, 0x340 + number * 4
            key = "lookup_adapters" if number < 4 else name
            if name == "secondary_cvtc_target_adapter":
                key = "secondary_cvtc_adapter"
            region = SimpleNamespace(entry=entry, span=SimpleNamespace(start=entry, end=entry + 0x20))
            regions[name] = region
            groups = list(units[key].code_regions) if key in units else []
            units[key] = SimpleNamespace(code_regions=tuple(groups + [name]))
            def mov_long(pc, pool, register):
                return 0xd000 | register << 8 | (pool - ((pc + 4) & ~3)) // 4
            rows = [(entry, mov_long(entry, entry + 0x10, 3), "mov.l @(stock,pc),r3"),
                    (entry + 2, 0x8901, "bt tail"),
                    (entry + 4, 0x432b, "jmp @r3"), (entry + 6, 9, "nop")]
            if name == "idle_ignition_adapter":
                rows += [(entry + 8, mov_long(entry + 8, entry + 0x14, 0), "mov.l @(helper,pc),r0"),
                         (entry + 10, 0x402b, "jmp @r0"), (entry + 12, 9, "nop")]
            elif name == "secondary_cvtc_target_adapter":
                rows += [(entry + 8, 0x432b, "jmp @r3"), (entry + 10, 9, "nop")]
            else:
                rows += [(entry + 8, 0xa000 | ((helper - (entry + 12)) // 2 & 0xfff), "bra helper"),
                         (entry + 10, 9, "nop")]
            for pc, word, text in rows:
                image[pc:pc + 2] = word.to_bytes(2, "big")
            image[entry + 0x10:entry + 0x14] = stock.to_bytes(4, "big")
            image[entry + 0x14:entry + 0x18] = helper.to_bytes(4, "big")
            image[stock:stock + 4] = VERIFIER.RETURN_STUB
            statements = tuple(assembly_model.SourceStatement(index, pc, "instruction", text, 2)
                               for index, (pc, word, text) in enumerate(rows))
            statements += (assembly_model.SourceStatement(20, entry + 0x10, "long", hex(stock), 4),)
            if name == "idle_ignition_adapter":
                statements += (assembly_model.SourceStatement(21, entry + 0x14, "long", hex(helper), 4),)
            carried = parsed[key].statements if key in parsed else ()
            labels = dict(parsed[key].labels) if key in parsed else {}
            # Separate pool labels per region preserve the multiple-entry unit.
            unique = name + "_stock"
            statements = tuple(assembly_model.SourceStatement(row.line_number, row.address, row.kind,
                row.text.replace("@(stock,pc)", "@(" + unique + ",pc)").replace("bt tail", "bt " + name + "_tail"), row.size) for row in statements)
            labels.update({unique: entry + 0x10, name + "_tail": entry + 8, "helper": helper})
            if name == "idle_ignition_adapter":
                labels["helper"] = entry + 0x14
            parsed[key] = assembly_model.ParsedSource(Path(key), labels, carried + statements)
            prefix = [event(0x4000), event(0x4002, 1), event(entry), event(entry + 2)]
            suffix = [event(stock), event(stock + 2, 1), event(0x4004)]
            passthrough = prefix + [event(entry + 4), event(entry + 6, 1)] + suffix
            if name == "idle_ignition_adapter":
                selected = prefix + [event(entry + 8), event(entry + 10), event(entry + 12, 1)]
            elif name == "secondary_cvtc_target_adapter":
                selected = prefix + [event(entry + 8), event(entry + 10, 1)]
            else:
                selected = prefix + [event(entry + 8), event(entry + 10, 1)]
            if name != "secondary_cvtc_target_adapter":
                selected += [event(helper), event(helper + 2, 1)]
            selected += suffix
            traces[entry] = passthrough + selected
        layout = SimpleNamespace(code_region_by_key=regions, assembly_unit_by_key=units)
        return image, parsed, invokes, taken + untaken, traces, layout

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_declared_secondary_adapter_requires_its_local_tail_paths(self):
        image, parsed, invokes, base, traces, layout = self.adapter_pc_fixture(secondary=True)
        records = base + [row for trace in traces.values() for row in trace]
        result = VERIFIER.require_payload_coverage(
            records, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
        self.assertEqual(result["entries"], len(layout.code_region_by_key))
        missing = base + [row for entry, trace in traces.items() if entry != 0x300 for row in trace]
        with self.assertRaisesRegex(VERIFIER.VerificationError, "uncovered entry 0x00000300"):
            VERIFIER.require_payload_coverage(
                missing, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
        del parsed["secondary_cvtc_adapter"]
        with self.assertRaisesRegex(VERIFIER.VerificationError, "missing typed map unit: secondary_cvtc_adapter"):
            VERIFIER.require_map_fixture_bindings(image, image, parsed, layout)

    def _jk00c_map_fixture(self):
        target = runtime_targets.load_runtime_target("JK00C")
        parsed = assembly_model.validate_assembly_sources(target.map_layout)
        composition = VERIFIER.composer.compose(
            layout=target.map_layout, image=target.stock_image, blobs=dict(target.map_payloads))
        fixture = bytearray(composition.data)
        VERIFIER.relocate_assembly_ram_literals(fixture, parsed)
        return target, parsed, composition.data, fixture

    def test_jk00c_binding_allows_declared_ram_aliases_and_binds_secondary_words(self):
        target, parsed, composed, fixture = self._jk00c_map_fixture()
        VERIFIER.require_map_fixture_bindings(fixture, composed, parsed, target.map_layout)
        self.assertNotEqual(fixture, composed)
        entry = target.map_layout.code_region_by_key["secondary_cvtc_target_adapter"].entry
        fixture[entry] ^= 1
        with self.assertRaisesRegex(VERIFIER.VerificationError, "simulator changes payload instruction"):
            VERIFIER.require_map_fixture_bindings(fixture, composed, parsed, target.map_layout)

    def test_control_pool_mutations_with_unchanged_opcodes_refuse_before_commands(self):
        target, parsed, composed, fixture = self._jk00c_map_fixture()
        sites = []
        for key, transfer in (("startup_wrapper", "jsr @r0"), ("idle_ignition_adapter", "jmp @r0")):
            unit = parsed[key]
            row = next(row for row in unit.statements if row.kind == "instruction" and row.text == transfer)
            sites.append((key, unit, unit.statement_by_address[row.address - 2]))
        unit = parsed["secondary_cvtc_adapter"]
        entry = target.map_layout.code_region_by_key["secondary_cvtc_target_adapter"].entry
        sites.append(("secondary R3", unit, unit.statement_by_address[entry]))
        base = RUNTIME_VERIFIER.base_verifier
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)
            for name, unit, load in sites:
                pool = unit.labels[assembly_model.PC_RELATIVE_RE.fullmatch(load.text).group("label")]
                changed = bytearray(fixture)
                changed[pool + 3] ^= 2
                self.assertEqual(changed[load.address:load.address + 2], fixture[load.address:load.address + 2])
                with self.subTest(operand=name), patch.object(base, "run_command") as command:
                    with self.assertRaisesRegex(RUNTIME_VERIFIER.VerificationError, "map ROM control pool differs"):
                        RUNTIME_VERIFIER._compile_and_run(
                            target, "map-switching", build / "source.c", build / "rom.o",
                            [build / "invoke.o"], build, "semantic marker",
                            map_parsed=parsed, fixture=changed, composed_image=composed)
                    command.assert_not_called()

    def test_jk00c_has_no_marker_only_fallback_without_binding_context(self):
        target = SimpleNamespace(rom="JK00C")
        with patch.object(RUNTIME_VERIFIER.base_verifier, "run_command") as command:
            with self.assertRaisesRegex(RUNTIME_VERIFIER.VerificationError, "requires typed/composed/fixture context"):
                RUNTIME_VERIFIER._compile_and_run(
                    target, "map-switching", Path("source.c"), Path("rom.o"),
                    [Path("invoke.o")], Path("."), "semantic marker")
            command.assert_not_called()

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_canonical_control_pool_mutation_refuses_before_commands(self):
        image, parsed, _, _, _ = self.pc_fixture()
        changed = bytearray(image)
        changed[0x113] ^= 2
        layout = SimpleNamespace(assembly_unit_by_key={
            key: SimpleNamespace(code_regions=()) for key in parsed})
        with patch.object(VERIFIER, "run_command") as command:
            with self.assertRaisesRegex(VERIFIER.VerificationError, "map ROM control pool differs"):
                VERIFIER.build_and_run_dynamic_harness(
                    changed, Path("."), parsed_by_unit=parsed, composed_image=image, layout=layout)
            command.assert_not_called()

    def test_jk00c_dispatch_rejects_a_marker_only_map_terminal(self):
        target = SimpleNamespace(rom="JK00C", map_layout=SimpleNamespace(variant="dual-cvtc"))
        with patch.object(RUNTIME_VERIFIER, "_build_rom_object", return_value=Path("rom.o")), \
             patch.object(RUNTIME_VERIFIER, "_build_invoke_objects", return_value=(Path("invoke.o"), Path("exception.o"))), \
             patch.object(RUNTIME_VERIFIER, "_render_harness", return_value=Path("source.c")), \
             patch.object(RUNTIME_VERIFIER, "_compile_and_run", return_value="VQ_SH_ELF_MAP_SWITCHING status=PASS "):
            with self.assertRaisesRegex(RUNTIME_VERIFIER.VerificationError, "lacks its measured coverage terminal"):
                RUNTIME_VERIFIER._run_harnesses(
                    target, b"fixture", Path("."), map_parsed={}, composed_image=b"fixture")

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_adapter_coverage_binds_multiple_entries_and_tail_returns(self):
        image, parsed, invokes, base, traces, layout = self.adapter_pc_fixture()
        records = base + [row for trace in traces.values() for row in trace]
        result = VERIFIER.require_payload_coverage(records, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
        self.assertEqual(result["entries"], len(layout.code_region_by_key))
        self.assertEqual(result["instructions"], sum(
            row.kind == "instruction" for unit in parsed.values() for row in unit.statements))
        for omitted, message in ((None, "uncovered entry 0x00000220"),
                                  (0x260, "uncovered entry 0x00000260")):
            records = base + [row for entry, trace in traces.items() if omitted is not None and entry != omitted for row in trace]
            with self.subTest(omitted=omitted), self.assertRaisesRegex(VERIFIER.VerificationError, message):
                VERIFIER.require_payload_coverage(records, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_adapter_coverage_rejects_wrong_tail_targets_and_continuations(self):
        image, parsed, invokes, base, traces, layout = self.adapter_pc_fixture()
        records = base + [row for trace in traces.values() for row in trace]
        # Mutate real successor records to other byte-bound PCs, not arbitrary opcodes.
        for previous, target, message in ((0x244, 0x344, "executed adapter JMP"),
                                          (0x248, 0x222, "executed BRA successor"),
                                          (0x220, 0x344, "executed adapter JMP"),
                                          (0x340, 0x4002, "executed return")):
            changed = list(records)
            index = next(index for index, row in enumerate(changed) if row[0] == previous)
            word = invokes[target] if target in invokes else int.from_bytes(image[target:target + 2], "big")
            changed[index + 2] = (target, word, 0)
            with self.subTest(previous=hex(previous)), self.assertRaisesRegex(VERIFIER.VerificationError, message):
                VERIFIER.require_payload_coverage(changed, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
        changed = bytearray(image)
        changed[0x250:0x254] = (0x344).to_bytes(4, "big")
        with self.assertRaisesRegex(VERIFIER.VerificationError, "map ROM control pool differs"):
            VERIFIER.require_payload_coverage(records, changed, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
        direct_helper = [(0x4000, 0x400b, 0), (0x4002, 9, 1), (0x220, 0x432b, 0)]
        with self.assertRaisesRegex(VERIFIER.VerificationError, "originating invoke frame"):
            VERIFIER.require_payload_coverage(direct_helper, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_adapter_coverage_rejects_unsupported_r3_and_jump_forms(self):
        image, parsed, invokes, base, traces, layout = self.adapter_pc_fixture()
        original = parsed["idle_ignition_adapter"]
        for address, text, message in ((0x2e0, "mov.l @(idle_ignition_adapter_stock,pc),r2", "entry R3 binding"),
                                       (0x2e4, "mov r0,r3", "unsupported adapter R3 use"),
                                       (0x2ea, "jmp @r2", "unsupported adapter JMP")):
            changed = dict(parsed)
            changed["idle_ignition_adapter"] = assembly_model.ParsedSource(original.path, original.labels, tuple(
                assembly_model.SourceStatement(row.line_number, row.address, row.kind,
                    text if row.address == address else row.text, row.size) for row in original.statements))
            with self.subTest(text=text), self.assertRaisesRegex(VERIFIER.VerificationError, message):
                VERIFIER.require_payload_coverage(base, image, changed, invokes, adapter_layout=layout, composed_image=bytes(image))

    @staticmethod
    def pc_fixture():
        """Model two payload units; callers explicitly isolate this test scope."""
        image = bytearray(0x300)
        rows = {
            "startup_wrapper": ((0x100, 0xd003, "mov.l @(callee,pc),r0"),
                                (0x102, 0x400b, "jsr @r0"), (0x104, 9, "nop"),
                                (0x106, 11, "rts"), (0x108, 9, "nop")),
            "limiter_commit": ((0x200, 0x8b00, "bf done"), (0x202, 9, "nop"),
                               (0x204, 11, "rts"), (0x206, 9, "nop")),
        }
        parsed = {}
        for key, instructions in rows.items():
            for address, word, _text in instructions:
                image[address:address + 2] = word.to_bytes(2, "big")
            statements = tuple(
                assembly_model.SourceStatement(index, address, "instruction", text, 2)
                for index, (address, word, text) in enumerate(instructions)
            )
            if key == "startup_wrapper":
                image[0x110:0x114] = (0x200).to_bytes(4, "big")
                statements += (assembly_model.SourceStatement(6, 0x110, "long", "0x200", 4),)
            parsed[key] = assembly_model.ParsedSource(Path(key), {"done": 0x204, "callee": 0x110}, statements)
        invokes = {0x4000: 0x400b, 0x4002: 9, 0x4004: 9}
        prefix = [(0x4000, 0x400b, 0), (0x4002, 9, 1),
                  (0x100, 0xd003, 0), (0x102, 0x400b, 0), (0x104, 9, 1), (0x200, 0x8b00, 0)]
        suffix = [(0x204, 11, 0), (0x206, 9, 1),
                  (0x106, 11, 0), (0x108, 9, 1), (0x4004, 9, 0)]
        return bytes(image), parsed, invokes, prefix + suffix, prefix + [(0x202, 9, 0)] + suffix

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_pc_coverage_requires_both_actual_branch_outcomes(self):
        image, parsed, invokes, taken, untaken = self.pc_fixture()
        covered = VERIFIER.require_payload_coverage(taken + untaken, image, parsed, invokes, composed_image=bytes(image))
        self.assertEqual(covered, dict(entries=2, instructions=9, outcomes=2,
                                      delay_slots=3, call_return_paths=2))
        with self.assertRaisesRegex(VERIFIER.VerificationError,
                                    "uncovered branch outcome 0x00000200->0x00000202"):
            VERIFIER.require_payload_coverage(taken, image, parsed, invokes, composed_image=bytes(image))

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_pc_coverage_rejects_wrong_opcode_delay_and_return(self):
        image, parsed, invokes, taken, untaken = self.pc_fixture()
        mutations = ((2, (0x100, 9, 0), "executed opcode differs"),
                     (4, (0x104, 9, 0), "missing executed delay slot"),
                     (5, (0x210, 0x8b00, 0), "executed call"),
                     (8, (0x100, 0xd003, 0), "executed return"))
        for index, replacement, error in mutations:
            records = list(taken + untaken)
            records[index] = replacement
            with self.subTest(error=error), self.assertRaisesRegex(VERIFIER.VerificationError, error):
                VERIFIER.require_payload_coverage(records, image, parsed, invokes, composed_image=bytes(image))

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_pc_coverage_names_an_omitted_payload_entry(self):
        image, parsed, invokes, taken, untaken = self.pc_fixture()
        records = [*taken[:2], (0x200, 0x8b00, 0), *taken[6:8], taken[-1]]
        with self.assertRaisesRegex(VERIFIER.VerificationError, "uncovered entry 0x00000100"):
            VERIFIER.require_payload_coverage(records, image, parsed, invokes, composed_image=bytes(image))

    def test_pc_trace_requires_a_complete_consistent_stream(self):
        record = "pc=00000100 opcode=0009 delay=0\n"
        complete = "VQ_SH_PC_TRACE version=1\n" + record + "VQ_SH_PC_TRACE end=complete records=1\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace"
            path.write_text(complete)
            self.assertEqual(VERIFIER.read_pc_trace(path), [(0x100, 9, 0)])
            for text in (complete.replace("records=1", "records=2"),
                         complete.rsplit("VQ_SH_PC_TRACE end", 1)[0],
                         complete + record, complete.replace("delay=0", "delay=2")):
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(VERIFIER.VerificationError):
                    VERIFIER.read_pc_trace(path)


class RollingWrapperCoverageTest(unittest.TestCase):
    @staticmethod
    def fixture():
        image = bytearray(0x400)
        rows = [
            (0x100, "mov.l @(periodic_stock,pc),r0"), (0x102, "jsr @r0"),
            (0x104, "nop"), (0x106, "rts"), (0x108, "nop"),
            (0x140, "bt selector_other"), (0x142, "mov.l @(selector_stock,pc),r0"),
            (0x144, "jmp @r0"), (0x146, "nop"),
            (0x14A, "mov.l @(selector_other_stock,pc),r0"), (0x14C, "jmp @r0"), (0x14E, "nop"),
            (0x180, "dt r2"), (0x182, "bf clear_loop"),
            (0x184, "mov.l @(startup_stock,pc),r0"), (0x186, "jsr @r0"),
            (0x188, "nop"), (0x18A, "rts"), (0x18C, "nop"),
        ]
        labels = {"periodic_stock": 0x110, "selector_stock": 0x160,
                  "selector_other_stock": 0x164, "startup_stock": 0x19C,
                  "selector_other": 0x14A, "clear_loop": 0x180}
        fixed = {"nop": 9, "rts": 11, "jsr @r0": 0x400B, "jmp @r0": 0x402B,
                 "dt r2": 0x4210, "bt selector_other": 0x8903, "bf clear_loop": 0x8BFD}
        statements = []
        for index, (pc, text) in enumerate(rows):
            if text.startswith("mov.l"):
                label = text.split("@(")[1].split(",")[0]
                word = 0xD000 | (labels[label] - ((pc + 4) & ~3)) // 4
            else:
                word = fixed[text]
            image[pc:pc + 2] = word.to_bytes(2, "big")
            statements.append(assembly_model.SourceStatement(index + 1, pc, "instruction", text, 2))
        for pool, target in ((0x110, 0x300), (0x160, 0x304), (0x164, 0x304), (0x19C, 0x308)):
            image[pool:pool + 4] = target.to_bytes(4, "big")
            statements.append(assembly_model.SourceStatement(30, pool, "long", hex(target), 4))
        for target in (0x300, 0x304, 0x308, 0x30C):
            image[target:target + 4] = bytes.fromhex("000b0009")
        parsed = assembly_model.ParsedSource(Path("wrappers.s"), labels, tuple(statements))
        regions = {key: SimpleNamespace(entry=entry, span=SimpleNamespace(start=entry, end=end))
                   for key, entry, end in (("periodic_wrapper", 0x100, 0x120),
                                           ("selector_arbiter", 0x140, 0x170),
                                           ("startup_wrapper", 0x180, 0x1A0))}
        boundaries = {0x100: 0x300, 0x140: 0x304, 0x180: 0x308}
        invokes = {0x4000: 0x400B, 0x4002: 9, 0x4004: 9, 0x4006: 9}

        def event(pc, delay=0):
            return pc, invokes[pc] if pc in invokes else int.from_bytes(image[pc:pc + 2], "big"), delay

        prefix, suffix = [event(0x4000), event(0x4002, 1)], [event(0x4004)]
        traces = [
            prefix + [event(0x100), event(0x102), event(0x104, 1), event(0x300),
                      event(0x302, 1), event(0x106), event(0x108, 1)] + suffix,
            prefix + [event(0x140), event(0x142), event(0x144), event(0x146, 1),
                      event(0x304), event(0x306, 1)] + suffix,
            prefix + [event(0x140), event(0x14A), event(0x14C), event(0x14E, 1),
                      event(0x304), event(0x306, 1)] + suffix,
            prefix + [event(0x180), event(0x182), event(0x180), event(0x182),
                      event(0x184), event(0x186), event(0x188, 1), event(0x308),
                      event(0x30A, 1), event(0x18A), event(0x18C, 1)] + suffix,
        ]
        return bytes(image), parsed, regions, boundaries, invokes, traces

    def test_each_entry_branch_delay_and_return_is_measured(self):
        image, parsed, regions, boundaries, invokes, traces = self.fixture()
        result = ROLLING_VERIFIER.require_wrapper_coverage(
            sum(traces, []), image, parsed, regions, boundaries, invokes)
        self.assertEqual(result, dict(entries=3, instructions=19, outcomes=4,
                                      delay_slots=6, call_return_paths=5, tail_paths=2))

    def test_omission_and_single_outcome_cannot_pass(self):
        image, parsed, regions, boundaries, invokes, traces = self.fixture()
        for selected, reason in ((traces[1:], "uncovered wrapper entry 0x00000100"),
                                  ([traces[0], *traces[2:]], "uncovered wrapper branch")):
            with self.subTest(reason=reason), self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, reason):
                ROLLING_VERIFIER.require_wrapper_coverage(
                    sum(selected, []), image, parsed, regions, boundaries, invokes)

    def test_wrong_opcode_slot_call_tail_and_return_are_rejected(self):
        image, parsed, regions, boundaries, invokes, traces = self.fixture()
        records = sum(traces, [])
        mutations = ((2, (0x100, 9, 0), "opcode differs"),
                     (4, (0x104, 9, 0), "missing executed delay slot"),
                     (5, (0x304, 11, 0), "wrapper JSR differs"),
                     (9, (0x4006, 9, 0), "wrapper return differs"),
                     (16, (0x30C, 11, 0), "wrapper JMP differs"))
        for index, replacement, reason in mutations:
            changed = list(records)
            changed[index] = replacement
            with self.subTest(reason=reason), self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, reason):
                ROLLING_VERIFIER.require_wrapper_coverage(changed, image, parsed, regions, boundaries, invokes)

    def test_origin_stock_boundary_and_noninstruction_bytes_are_required(self):
        image, parsed, regions, boundaries, invokes, traces = self.fixture()
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, "originating invoke frame"):
            ROLLING_VERIFIER.require_wrapper_coverage(
                traces[0][2:] + sum(traces[1:], []), image, parsed, regions, boundaries, invokes)
        changed = bytearray(image)
        changed[0x160:0x164] = (0x30C).to_bytes(4, "big")
        records = sum(traces, [])
        records[16:18] = [(0x30C, 11, 0), (0x30E, 9, 1)]
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, "stock return boundary"):
            ROLLING_VERIFIER.require_wrapper_coverage(records, changed, parsed, regions, boundaries, invokes)
        records = traces[0] + [(0x110, 0, 0)] + sum(traces[1:], [])
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, "executed wrapper data"):
            ROLLING_VERIFIER.require_wrapper_coverage(records, image, parsed, regions, boundaries, invokes)

    def test_fixture_instruction_and_control_literal_mutations_fail_before_linking(self):
        image, parsed, _regions, _boundaries, _invokes, _traces = self.fixture()
        for address, reason in ((0x100, "wrapper instruction"), (0x110, "wrapper control literal")):
            changed = bytearray(image)
            changed[address] ^= 1
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                build_dir = Path(directory)
                with patch.object(ROLLING_VERIFIER, "build_rom_object", return_value=build_dir / "rom.o"), \
                        patch.object(ROLLING_VERIFIER.base_verifier, "run_command") as command, \
                        self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, reason):
                    ROLLING_VERIFIER.build_and_run_dynamic_harness(
                        bytes(changed), build_dir, parsed_by_unit={"wrappers": parsed},
                        composed_image=image, base_layout=None, rolling_layout=None)
                self.assertNotIn(ROLLING_VERIFIER.base_verifier.GCC,
                                 [call.args[0][0] for call in command.call_args_list])


if __name__ == "__main__":
    unittest.main()
