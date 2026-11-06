from dataclasses import replace
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
ROLLING_ROWS = ROLLING_VERIFIER.rolling_launch_rows

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
        self.assertEqual(result.instruction_count, 1707)
        self.assertEqual(result.diagnostic_count, 12)

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
        # The stock divider runs unstubbed.
        self.assertEqual(fixture[ROLLING_VERIFIER.STOCK_UNSIGNED_DIVIDER:
                                 ROLLING_VERIFIER.STOCK_UNSIGNED_DIVIDER + 4], bytes(4))

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
        self.assertIn("rolling_result['dynamic_cases']", source)
        self.assertIn('#include "rolling_launch_rows.h"', harness)
        self.assertIn('status=PASS cases=%lu engine=%lu ignition=%lu "', harness)
        self.assertIn('"control=%lu fraction=%lu wrappers=5 feedback=%lu', harness)
        self.assertEqual(ROLLING_VERIFIER.WRAPPER_CASES, 5)

    def test_can_telemetry_composition_lock_matches_verifier(self):
        layout = can_telemetry_layout.load_layout()
        blobs = can_telemetry_assembly.load_payloads(layout)

        result = TELEMETRY_VERIFIER.require_composition(layout, blobs)

        self.assertEqual(result.sha256, layout.expected_composition_sha256)
        self.assertEqual(
            result.instruction_count, layout.assembled_instruction_count
        )
        self.assertEqual(result.code_entry_count, len(layout.code_regions))

    def test_can_telemetry_verifier_refuses_an_unlocked_composition(self):
        layout = can_telemetry_layout.load_layout()
        blobs = can_telemetry_assembly.load_payloads(layout)
        unlocked = replace(layout, expected_composition_sha256="0" * 64)

        with self.assertRaisesRegex(
            TELEMETRY_VERIFIER.VerificationError, "does not lock its composition"
        ):
            TELEMETRY_VERIFIER.require_composition(unlocked, blobs)

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
        self.assertEqual(stubs, 11)
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
        layout = can_telemetry_layout.load_layout()
        manifest = can_telemetry_profile.load_manifest()
        pattern = TELEMETRY_VERIFIER.dynamic_marker_pattern(layout, manifest)
        printed = re.search(
            r'"(VQ_SH_ELF_CAN_TELEMETRY status=PASS [^"]*)"\s*"([^"]*)\\n"',
            harness,
        )
        self.assertIsNotNone(printed)
        marker = (printed.group(1) + printed.group(2)).replace("cases=%lu", "cases=37")
        self.assertIsNotNone(re.fullmatch(pattern, marker))
        self.assertIsNone(re.fullmatch(pattern, marker.replace("cases=37", "cases=0")))
        fewer = replace(layout, code_regions=layout.code_regions[1:])
        self.assertIsNone(re.fullmatch(
            TELEMETRY_VERIFIER.dynamic_marker_pattern(fewer, manifest), marker
        ))
        self.assertIn("trapa #0x40", exception)

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
        control_rows = ((0x240, 0xb01e, "bsr telemetry_control_config_valid"), (0x242, 9, "nop"),
                        (0x244, 11, "rts"), (0x246, 9, "nop"),
                        (0x260, 0xb00e, "bsr telemetry_control_config_valid"), (0x262, 9, "nop"),
                        (0x264, 11, "rts"), (0x266, 9, "nop"),
                        (0x280, 0x8904, "bt telemetry_control_config_invalid"), (0x282, 0xe001, "mov #1,r0"),
                        (0x284, 0xa000, "bra valid_return"), (0x286, 9, "nop"),
                        (0x288, 11, "rts"), (0x28a, 9, "nop"),
                        (0x28c, 0xe000, "mov #0,r0"), (0x28e, 11, "rts"), (0x290, 9, "nop"))
        for pc, word, text in control_rows:
            image[pc:pc + 2] = word.to_bytes(2, "big")
        parsed["control"] = assembly_model.ParsedSource(Path("CAN-control.s"),
            {"telemetry_control_config_valid": 0x280, "telemetry_control_config_invalid": 0x28c,
             "valid_return": 0x288}, tuple(assembly_model.SourceStatement(index, pc, "instruction", text, 2)
                for index, (pc, word, text) in enumerate(control_rows)))
        layout.assembly_unit_by_key["control"] = SimpleNamespace(code_regions=("hcan1_init_wrapper", "control_poll"))
        layout.code_region_by_key.update(hcan1_init_wrapper=SimpleNamespace(entry=0x240), control_poll=SimpleNamespace(entry=0x260))
        controls = {}
        for entry in (0x240, 0x260):
            for valid in (True, False):
                body = (0x280, 0x282, 0x284, 0x286, 0x288, 0x28a) if valid else (0x280, 0x28c, 0x28e, 0x290)
                controls[entry, valid] = prefix + events((entry, entry + 2), {entry + 2}) + events(body, {0x286, 0x28a, 0x290}) + events((entry + 4, entry + 6), {entry + 6}) + suffix
        margin_rows = ((0x2b0, 0xd005, "mov.l @(margin_callee,pc),r0"),
                       (0x2b2, 0x400b, "jsr @r0"), (0x2b4, 9, "nop"),
                       (0x2b6, 0x8901, "bt margin_done"), (0x2b8, 0xe001, "mov #1,r0"),
                       (0x2ba, 9, "nop"), (0x2bc, 11, "rts"), (0x2be, 9, "nop"),
                       (0x3a0, 11, "rts"), (0x3a2, 9, "nop"), (0x3a4, 9, "nop"))
        for pc, word, text in margin_rows:
            image[pc:pc + 2] = word.to_bytes(2, "big")
        image[0x2c8:0x2cc] = (0x310).to_bytes(4, "big")
        evaluator = TELEMETRY_VERIFIER.knock_evaluator_stub(0x310)
        image[0x310:0x310 + len(evaluator)] = evaluator
        layout.hook_by_key = {"knock_margin_latch": SimpleNamespace(stock=0x310)}
        request_rows = (
            (0x3a6, 0xb013, "bsr telemetry_build_bank"), (0x3a8, 9, "nop"),
            (0x3b0, 0xb006, "bsr telemetry_request_page"), (0x3b2, 9, "nop"), (0x3b4, 9, "nop"),
            (0x3c0, 0x2008, "tst r0,r0"), (0x3c2, 0x8901, "bt request_join"),
            (0x3c4, 0xa000, "bra request_join"), (0x3c6, 9, "nop"),
            (0x3c8, 0x8bfe, "bf request_loop"), (0x3ca, 11, "rts"), (0x3cc, 9, "nop"),
            (0x3d0, 0x8b00, "bf build_join"), (0x3d2, 9, "nop"),
            (0x3d4, 11, "rts"), (0x3d6, 9, "nop"),
            (0x3e0, 11, "rts"), (0x3e2, 9, "nop"))
        for pc, word, text in request_rows:
            image[pc:pc + 2] = word.to_bytes(2, "big")
        parsed["capture"] = assembly_model.ParsedSource(Path("CAN-capture.s"),
            {"margin_callee": 0x2c8, "margin_done": 0x2bc, "telemetry_request_page": 0x3c0,
             "request_join": 0x3c8, "request_loop": 0x3c8, "telemetry_build_bank": 0x3d0,
             "build_join": 0x3d4},
            tuple(assembly_model.SourceStatement(index, pc, "instruction", text, 2)
                  for index, (pc, word, text) in enumerate(margin_rows + request_rows))
            + (assembly_model.SourceStatement(40, 0x2c8, "long", "0x310", 4),))
        layout.assembly_unit_by_key["capture"] = SimpleNamespace(
            code_regions=("capture", "dynamic_slot", "build_bank", "knock_margin_wrapper",
                          "request_page"))
        layout.code_region_by_key.update(
            knock_margin_wrapper=SimpleNamespace(entry=0x2b0, span=SimpleNamespace(start=0x2b0, end=0x2d0)),
            capture=SimpleNamespace(entry=0x3a0, span=SimpleNamespace(start=0x3a0, end=0x3a4)),
            build_bank=SimpleNamespace(entry=0x3d0, span=SimpleNamespace(start=0x3d0, end=0x3d8)),
            request_page=SimpleNamespace(entry=0x3c0, span=SimpleNamespace(start=0x3c0, end=0x3ce)),
            dynamic_slot=SimpleNamespace(entry=0x3e0, span=SimpleNamespace(start=0x3e0, end=0x3e4)))
        for take in (True, False):
            pcs = (0x2b0, 0x2b2, 0x2b4, *range(0x310, 0x328, 2), 0x2b6)
            pcs += (0x2bc, 0x2be) if take else (0x2b8, 0x2ba, 0x2bc, 0x2be)
            controls[0x2b0, take] = prefix + events(pcs, {0x2b4, 0x326, 0x2be}) + suffix
        bank_tail = (0x3c8, 0x3c8, 0x3ca, 0x3cc)
        controls[0x3c0, True] = prefix + events((0x3c0, 0x3c2, *bank_tail), {0x3cc}) + suffix
        controls[0x3c0, False] = prefix + events((0x3c0, 0x3c2, 0x3c4, 0x3c6, *bank_tail), {0x3c6, 0x3cc}) + suffix
        controls[0x3d0, True] = prefix + events((0x3d0, 0x3d4, 0x3d6), {0x3d6}) + suffix
        controls[0x3d0, False] = prefix + events((0x3d0, 0x3d2, 0x3d4, 0x3d6), {0x3d6}) + suffix
        controls[0x3a0, True] = prefix + events((0x3a0, 0x3a2), {0x3a2}) + suffix
        controls[0x3e0, True] = prefix + events((0x3e0, 0x3e2), {0x3e2}) + suffix
        for pc, word, text in ((0x1e0, 0x002b, "rte"), (0x1e2, 9, "nop"),
                               (0x1e8, 11, "rts"), (0x1ea, 9, "nop"),
                               (0x1f0, 11, "rts"), (0x1f2, 9, "nop")):
            image[pc:pc + 2] = word.to_bytes(2, "big")
        parsed["completion"] = assembly_model.ParsedSource(
            Path("CAN-completion.s"), {"telemetry_handle_completion": 0x1e8},
            (assembly_model.SourceStatement(0, 0x1e0, "instruction", "rte", 2),
             assembly_model.SourceStatement(1, 0x1e2, "instruction", "nop", 2),
             assembly_model.SourceStatement(2, 0x1e8, "instruction", "rts", 2),
             assembly_model.SourceStatement(3, 0x1ea, "instruction", "nop", 2),
             assembly_model.SourceStatement(4, 0x1f0, "instruction", "rts", 2),
             assembly_model.SourceStatement(5, 0x1f2, "instruction", "nop", 2)))
        layout.assembly_unit_by_key["completion"] = SimpleNamespace(
            code_regions=("sle1_isr", "completion", "dynamic_command"))
        layout.code_region_by_key.update(
            sle1_isr=SimpleNamespace(entry=0x1e0, span=SimpleNamespace(start=0x1e0, end=0x1e4)),
            completion=SimpleNamespace(entry=0x1e8, span=SimpleNamespace(start=0x1e8, end=0x1ec)),
            dynamic_command=SimpleNamespace(
                entry=0x1f0, span=SimpleNamespace(start=0x1f0, end=0x1f4)))
        controls[0x1e0, True] = events((0x1e0, 0x1e2), {0x1e2})
        controls[0x1e8, True] = prefix + events((0x1e8, 0x1ea), {0x1ea}) + suffix
        controls[0x1f0, True] = prefix + events((0x1f0, 0x1f2), {0x1f2}) + suffix
        return image, layout, parsed, invokes, main, knock, startup, controls

    def test_can_wrapper_coverage_requires_entries_instructions_and_loop_outcomes(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        control_records = [row for trace in controls.values() for row in trace]
        require = lambda records: TELEMETRY_VERIFIER.require_wrapper_coverage(records + control_records, image, layout, parsed, invokes)
        self.assertEqual(require(main + knock + startup), dict(
            entries=14, instructions=63, outcomes=12, delay_slots=23, call_return_paths=18, config_return_paths=4))
        for records, message in ((knock + startup, "uncovered CAN wrapper entry 0x00000100"),
                                 (main + knock + startup[:2] + startup[3:], "uncovered CAN wrapper outcome"),
                                 ([row for row in main if row[0] != 0x102] + knock + startup, "uncovered CAN wrapper instruction 0x00000102")):
            with self.subTest(message=message), self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, message):
                require(records)

    def test_can_wrapper_coverage_rejects_wrong_opcode_delay_callee_and_return(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        control_records = [row for trace in controls.values() for row in trace]
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
                TELEMETRY_VERIFIER.require_wrapper_coverage(changed + knock + startup + control_records, image, layout, parsed, invokes)
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "lacks its invoke frame"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(main[2:] + knock + startup + control_records, image, layout, parsed, invokes)
        changed = bytearray(image)
        changed[0x350:0x356] = bytes.fromhex("400b00090009")
        foreign = [(0x350, 0x400b, 0), (0x352, 9, 1)] + main[2:]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "origin is outside bound invoke code"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(foreign + knock + startup + control_records, changed, layout, parsed, invokes)
        changed = bytearray(image)
        changed[0x114:0x118] = (0x304).to_bytes(4, "big")
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "executed CAN callee"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(main + knock + startup + control_records, changed, layout, parsed, invokes)

    def test_can_wrappers_reject_post_stub_instruction_changes_and_new_transfer_forms(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        control_records = [row for trace in controls.values() for row in trace]
        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(image, image, parsed, layout)
        for row in parsed["wrappers"].statements:
            changed = bytearray(image)
            changed[row.address] ^= 1
            with self.subTest(pc=hex(row.address)):
                if row.kind == "instruction":
                    with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes CAN wrapper instruction"):
                        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed, layout)
                elif row.address == parsed["wrappers"].labels["ram_operand"]:
                    changed[row.address:row.address + 4] = VERIFIER.alias_high_ram(0xffff5e00).to_bytes(4, "big")
                    TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed, layout)
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
            altered = dict(parsed)
            altered["wrappers"] = assembly_model.ParsedSource(original.path, original.labels, tuple(
                assembly_model.SourceStatement(row.line_number, row.address, row.kind,
                    text if row.address == pc else row.text, row.size) for row in original.statements))
            with self.subTest(text=text), self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, message):
                TELEMETRY_VERIFIER.require_wrapper_coverage(main + knock + startup + control_records, image, layout, altered, invokes)
        changed = bytearray(image)
        changed[0x300:0x302] = (0x002b).to_bytes(2, "big")
        altered = [(pc, 0x002b if pc == 0x300 else word, delay) for pc, word, delay in main]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "unsupported transfer in active CAN wrapper frame"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(altered + knock + startup + control_records, changed, layout, parsed, invokes)

    def test_can_control_requires_each_caller_return_pc_with_global_coverage_preserved(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        full = main + knock + startup + [row for trace in controls.values() for row in trace]
        dropped = main + knock + startup + [row for key, trace in controls.items() if key != (0x240, False) for row in trace]
        self.assertEqual({row[0] for row in full}, {row[0] for row in dropped})
        edges = lambda rows: {(pc, rows[index + 1][0]) for index, (pc, word, delay) in enumerate(rows[:-1]) if pc in (0x200, 0x280)}
        self.assertEqual(edges(full), edges(dropped))
        self.assertEqual(TELEMETRY_VERIFIER.require_wrapper_coverage(full, image, layout, parsed, invokes)["config_return_paths"], 4)
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "uncovered CAN config return 0x00000240->0x0000028e->0x00000244"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(dropped, image, layout, parsed, invokes)
        direct = [(0x4000, 0x400b, 0), (0x4002, 9, 1), (0x280, 0x8904, 0)]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "unbound CAN config caller"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(direct + full, image, layout, parsed, invokes)
        wrong_return = list(controls[0x240, False])
        index = next(index for index, row in enumerate(wrong_return) if row[0] == 0x28e)
        wrong_return[index:index + 2] = [(0x300, 11, 0), (0x302, 9, 1)]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "unsupported CAN config return path"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(wrong_return + full, image, layout, parsed, invokes)

    def test_can_control_rejects_wrong_bt_bra_and_bsr_successors(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        for pc, target, message in ((0x240, 0x28c, "executed CAN callee"),
                                    (0x284, 0x28e, "executed CAN BRA successor"),
                                    (0x280, 0x284, "executed CAN conditional successor")):
            altered = list(controls[0x240, True])
            index = next(index for index, row in enumerate(altered) if row[0] == pc)
            next_index = index + (1 if pc == 0x280 else 2)
            altered[next_index] = (target, int.from_bytes(image[target:target + 2], "big"), 0)
            records = main + knock + startup + altered + [row for key, trace in controls.items() if key != (0x240, True) for row in trace]
            with self.subTest(pc=hex(pc)), self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, message):
                TELEMETRY_VERIFIER.require_wrapper_coverage(records, image, layout, parsed, invokes)

    def test_can_margin_region_preserves_origin_and_excludes_other_capture_entries(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        records = main + knock + startup + [row for trace in controls.values() for row in trace]
        require = lambda rows: TELEMETRY_VERIFIER.require_wrapper_coverage(rows, image, layout, parsed, invokes)
        self.assertEqual(require(records)["entries"], 14)
        self.assertFalse({0x3a4} & {row[0] for row in records})
        self.assertIn(0x3a0, {row[0] for row in records})
        self.assertIn(0x3c0, {row[0] for row in records})
        missing = main + knock + startup + [row for key, trace in controls.items() if key[0] != 0x2b0 for row in trace]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "uncovered CAN wrapper entry 0x000002b0"):
            require(missing)
        missing = main + knock + startup + [row for key, trace in controls.items() if key != (0x2b0, True) for row in trace]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "uncovered CAN wrapper outcome 0x000002b6->0x000002bc"):
            require(missing)
        trace = list(controls[0x2b0, True])
        trace[0:2] = [(0x350, 0x400b, 0), (0x352, 9, 1)]
        altered = bytearray(image)
        altered[0x350:0x354] = bytes.fromhex("400b0009")
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "origin is outside bound invoke code"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(trace + records, altered, layout, parsed, invokes)

    def test_can_margin_admission_binds_selected_words_and_call_pool_only(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        measured = {
            row.address for row in TELEMETRY_VERIFIER._measured_statements(
                "capture", parsed["capture"], layout)
            if row.kind == "instruction"
        }
        callers = {address for address, _pool in TELEMETRY_VERIFIER._bounded_capture_callers(parsed)}
        for row in parsed["capture"].statements:
            changed = bytearray(image)
            changed[row.address] ^= 1
            with self.subTest(pc=hex(row.address)):
                if row.kind == "instruction" and row.address in measured:
                    with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes CAN wrapper instruction"):
                        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed, layout)
                elif any(start <= row.address < start + 4 for start in callers):
                    with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes bounded capture caller"):
                        TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed, layout)
                elif row.kind == "long":
                    changed[row.address:row.address + 4] = (0x300).to_bytes(4, "big")
                    with tempfile.TemporaryDirectory() as directory, patch.object(TELEMETRY_VERIFIER.base_verifier, "run_command") as command:
                        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "simulator changes CAN wrapper control literal"):
                            TELEMETRY_VERIFIER.build_and_run_dynamic_harness(
                                changed, Path(directory), layout=layout, parsed_by_unit=parsed, composed_image=image)
                        command.assert_not_called()
                else:
                    TELEMETRY_VERIFIER.require_wrapper_instruction_bytes(changed, image, parsed, layout)

    def test_can_margin_requires_actual_evaluator_target_and_its_return_site(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        full = main + knock + startup + [row for trace in controls.values() for row in trace]
        trace = list(controls[0x2b0, True])
        first = next(index for index, row in enumerate(trace) if row[0] == 0x310)
        changed = trace[:first] + [(0x300, 11, 0), (0x302, 9, 1)] + trace[first + 12:]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "executed CAN callee"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(changed + full, image, layout, parsed, invokes)
        returned = next(index for index, row in enumerate(trace) if row[0] == 0x324)
        changed = trace[:returned] + [(0x300, 11, 0), (0x302, 9, 1)] + trace[returned + 2:]
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "unsupported CAN evaluator return path"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(changed + full, image, layout, parsed, invokes)
        altered = bytearray(image)
        altered[0x310] ^= 1
        with self.assertRaisesRegex(TELEMETRY_VERIFIER.VerificationError, "CAN knock evaluator stand-in differs"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(full, altered, layout, parsed, invokes)

    def test_can_request_page_requires_harness_invoke_return(self):
        image, layout, parsed, invokes, main, knock, startup, controls = self.can_wrapper_pc_fixture()
        captured = []
        for take in (True, False):
            body = (0x3c0, 0x3c2, 0x3c8, 0x3c8, 0x3ca, 0x3cc) if take else (
                0x3c0, 0x3c2, 0x3c4, 0x3c6, 0x3c8, 0x3c8, 0x3ca, 0x3cc)
            delays = {0x3b2, 0x3cc} if take else {0x3b2, 0x3c6, 0x3cc}
            captured.append([
                (pc, int.from_bytes(image[pc:pc + 2], "big"), int(pc in delays))
                for pc in (0x3b0, 0x3b2, *body, 0x3b4)])
        base = main + knock + startup + [
            row for key, trace in controls.items() if key[0] != 0x3c0 for row in trace]
        with self.assertRaisesRegex(
                TELEMETRY_VERIFIER.VerificationError, "uncovered CAN request invoke return 0x000003c0"):
            TELEMETRY_VERIFIER.require_wrapper_coverage(
                base + [row for trace in captured for row in trace], image, layout, parsed, invokes)

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

    def adapter_pc_fixture(self, *, local_adapter=None):
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
        if local_adapter:
            names += (local_adapter,)
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
            elif name == local_adapter:
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
            elif name == local_adapter:
                selected = prefix + [event(entry + 8), event(entry + 10, 1)]
            else:
                selected = prefix + [event(entry + 8), event(entry + 10, 1)]
            if name != local_adapter:
                selected += [event(helper), event(helper + 2, 1)]
            selected += suffix
            traces[entry] = passthrough + selected
        layout = SimpleNamespace(code_region_by_key=regions, assembly_unit_by_key=units)
        return image, parsed, invokes, taken + untaken, traces, layout

    @patch.object(VERIFIER, "PC_COVERAGE_UNITS", ("startup_wrapper", "limiter_commit"))
    def test_declared_local_adapters_require_their_tail_paths(self):
        for key, region in (("secondary_cvtc_adapter", "secondary_cvtc_target_adapter"),
                            ("ignition_state_adapter", "ignition_state_adapter")):
            with self.subTest(unit=key):
                image, parsed, invokes, base, traces, layout = self.adapter_pc_fixture(local_adapter=region)
                records = base + [row for trace in traces.values() for row in trace]
                result = VERIFIER.require_payload_coverage(
                    records, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
                self.assertEqual(result["entries"], len(layout.code_region_by_key))
                missing = base + [row for entry, trace in traces.items() if entry != 0x300 for row in trace]
                with self.assertRaisesRegex(VERIFIER.VerificationError, "uncovered entry 0x00000300"):
                    VERIFIER.require_payload_coverage(
                        missing, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
                for previous, successor, reason in ((0x308, 0x340, "executed adapter JMP"),
                                                     (0x358, 0x4000, "executed return")):
                    changed = list(records)
                    index = next(index for index, row in enumerate(changed) if row[0] == previous)
                    word = invokes[successor] if successor in invokes else int.from_bytes(image[successor:successor + 2], "big")
                    changed[index + 2] = (successor, word, 0)
                    with self.subTest(previous=hex(previous)), self.assertRaisesRegex(VERIFIER.VerificationError, reason):
                        VERIFIER.require_payload_coverage(
                            changed, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
                missing_origin = missing + traces[0x300][2:]
                with self.assertRaisesRegex(VERIFIER.VerificationError, "adapter lacks its originating invoke frame"):
                    VERIFIER.require_payload_coverage(
                        missing_origin, image, parsed, invokes, adapter_layout=layout, composed_image=bytes(image))
                del parsed[key]
                with self.assertRaisesRegex(VERIFIER.VerificationError, f"missing typed map unit: {key}"):
                    VERIFIER.require_map_fixture_bindings(image, image, parsed, layout)

    def _relocated_map_fixture(self, rom="JK00C"):
        target = runtime_targets.load_runtime_target(rom)
        parsed = assembly_model.validate_assembly_sources(target.map_layout)
        composition = VERIFIER.composer.compose(
            layout=target.map_layout, image=target.stock_image, blobs=dict(target.map_payloads))
        fixture = bytearray(composition.data)
        VERIFIER.relocate_assembly_ram_literals(fixture, parsed)
        return target, parsed, composition.data, fixture

    def test_dual_cvtc_binding_allows_declared_ram_aliases_and_binds_secondary_words(self):
        for rom in ("JK00C", "JK00D"):
            target, parsed, composed, fixture = self._relocated_map_fixture(rom)
            VERIFIER.require_map_fixture_bindings(fixture, composed, parsed, target.map_layout)
            self.assertNotEqual(fixture, composed)
            entry = target.map_layout.code_region_by_key["secondary_cvtc_target_adapter"].entry
            fixture[entry] ^= 1
            with self.assertRaisesRegex(VERIFIER.VerificationError, "simulator changes payload instruction"):
                VERIFIER.require_map_fixture_bindings(fixture, composed, parsed, target.map_layout)

    def test_native_curve_binding_allows_ram_aliases_and_binds_limiter_and_pool_2(self):
        for rom in ("JK78C", "1ND0A", "1ND3B"):
            target, parsed, composed, fixture = self._relocated_map_fixture(rom)
            VERIFIER.require_map_fixture_bindings(fixture, composed, parsed, target.map_layout)
            self.assertNotEqual(fixture, composed)
            sites = [
                parsed["limiter_commit"].labels["fuel_cap_copy_loop"],
                parsed["limiter_commit"].labels["fuel_curve_copy_loop"],
                target.map_layout.code_region_by_key["idle_ignition_pool_2_adapter"].entry,
            ]
            if "ignition_state_adapter" in parsed:
                sites.append(target.map_layout.code_region_by_key["ignition_state_adapter"].entry)
            for entry in sites:
                changed = bytearray(fixture)
                changed[entry] ^= 1
                with self.subTest(rom=rom, entry=hex(entry)), self.assertRaisesRegex(
                        VERIFIER.VerificationError, "simulator changes payload instruction"):
                    VERIFIER.require_map_fixture_bindings(changed, composed, parsed, target.map_layout)

    def test_control_pool_mutations_with_unchanged_opcodes_refuse_before_commands(self):
        for rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B"):
            target, parsed, composed, fixture = self._relocated_map_fixture(rom)
            sites = []
            for key, transfer in (("startup_wrapper", "jsr @r0"), ("idle_ignition_adapter", "jmp @r0")):
                unit = parsed[key]
                row = next(row for row in unit.statements if row.kind == "instruction" and row.text == transfer)
                sites.append((key, unit, unit.statement_by_address[row.address - 2]))
            if "ignition_state_adapter" in parsed:
                unit_key = region_key = "ignition_state_adapter"
            elif rom == "JK78C":
                unit_key, region_key = "lookup_adapters", "idle_ignition_pool_2_adapter"
            else:
                unit_key, region_key = "secondary_cvtc_adapter", "secondary_cvtc_target_adapter"
            unit = parsed[unit_key]
            entry = target.map_layout.code_region_by_key[region_key].entry
            sites.append((f"{region_key} R3", unit, unit.statement_by_address[entry]))
            base = RUNTIME_VERIFIER.base_verifier
            with tempfile.TemporaryDirectory() as directory:
                build = Path(directory)
                for name, unit, load in sites:
                    pool = unit.labels[assembly_model.PC_RELATIVE_RE.fullmatch(load.text).group("label")]
                    changed = bytearray(fixture)
                    changed[pool + 3] ^= 2
                    self.assertEqual(changed[load.address:load.address + 2], fixture[load.address:load.address + 2])
                    with self.subTest(rom=rom, operand=name), patch.object(base, "run_command") as command:
                        with self.assertRaisesRegex(RUNTIME_VERIFIER.VerificationError, f"{rom} map binding: map ROM control pool differs"):
                            RUNTIME_VERIFIER._compile_and_run(
                                target, "map-switching", build / "source.c", build / "rom.o",
                                [build / "invoke.o"], build, "semantic marker",
                                map_parsed=parsed, fixture=changed, composed_image=composed)
                        command.assert_not_called()

    def test_measured_relocated_map_has_no_marker_only_fallback_without_binding_context(self):
        for rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B"):
            target = SimpleNamespace(rom=rom)
            with patch.object(RUNTIME_VERIFIER.base_verifier, "run_command") as command:
                with self.assertRaisesRegex(RUNTIME_VERIFIER.VerificationError, f"{rom} map coverage requires typed/composed/fixture context"):
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

    def test_measured_relocated_map_dispatch_rejects_marker_only_and_wrong_rom_terminals(self):
        for rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B"):
            other = "1ND3B" if rom == "1ND0A" else "1ND0A" if rom == "1ND3B" else "JK00D" if rom == "JK00C" else "JK00C"
            for terminal in ("VQ_SH_ELF_MAP_SWITCHING status=PASS ",
                             f"VQ_SH_ELF_RUNTIME_MAP_COVERAGE status=PASS rom={other} "):
                variant = "sh7059-1nd" if rom in ("1ND0A", "1ND3B") else "sh7058-jk78" if rom == "JK78C" else "dual-cvtc"
                target = SimpleNamespace(rom=rom, map_layout=SimpleNamespace(variant=variant))
                with patch.object(RUNTIME_VERIFIER, "_build_rom_object", return_value=Path("rom.o")), \
                     patch.object(RUNTIME_VERIFIER, "_build_invoke_objects", return_value=(Path("invoke.o"), Path("exception.o"))), \
                     patch.object(RUNTIME_VERIFIER, "_render_harness", return_value=Path("source.c")), \
                     patch.object(RUNTIME_VERIFIER, "_compile_and_run", return_value=terminal):
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


class RollingCoverageTest(unittest.TestCase):
    """The generic PC-trace tracker of the Rolling Launch gate."""

    INVOKES = {0x40000: 0x400B, 0x40002: 9, 0x40004: 9}

    @classmethod
    def fixture(cls):
        # A conditional delayed branch whose slot runs only as a delay slot, a
        # leaf return, and a call through a literal-loaded register.
        rows = (
            (0x100, "tst r4,r4", 0x2448), (0x102, "bf/s call", 0x8F02),
            (0x104, "mov #1,r1", 0xE101), (0x106, "rts", 11), (0x108, "nop", 9),
            (0x10A, "mov.l @(callee,pc),r0", 0xD002), (0x10C, "jsr @r0", 0x400B),
            (0x10E, "nop", 9), (0x110, "rts", 11), (0x112, "nop", 9),
        )
        image = bytearray(0x400)
        statements = []
        for index, (pc, text, word) in enumerate(rows):
            image[pc:pc + 2] = word.to_bytes(2, "big")
            statements.append(assembly_model.SourceStatement(index + 1, pc, "instruction", text, 2))
        image[0x114:0x118] = (0x300).to_bytes(4, "big")
        statements.append(assembly_model.SourceStatement(20, 0x114, "long", "0x300", 4))
        for stub in (0x300, 0x308):
            image[stub:stub + 4] = ROLLING_VERIFIER.RETURN_STUB
        parsed = assembly_model.ParsedSource(
            Path("wrappers.s"), {"call": 0x10A, "callee": 0x114}, tuple(statements))
        regions = {"periodic_wrapper": SimpleNamespace(
            entry=0x100, span=SimpleNamespace(start=0x100, end=0x118))}
        return bytes(image), parsed, regions

    def event(self, image, pc, delay=0):
        word = self.INVOKES.get(pc, int.from_bytes(image[pc:pc + 2], "big"))
        return pc, word, delay

    def runs(self, image, callee=0x300):
        prefix = [self.event(image, 0x40000), self.event(image, 0x40002, 1)]
        suffix = [self.event(image, 0x40004)]
        taken = prefix + [
            self.event(image, 0x100), self.event(image, 0x102), self.event(image, 0x104, 1),
            self.event(image, 0x10A), self.event(image, 0x10C), self.event(image, 0x10E, 1),
            self.event(image, callee), self.event(image, callee + 2, 1),
            self.event(image, 0x110), self.event(image, 0x112, 1),
        ] + suffix
        fall = prefix + [
            self.event(image, 0x100), self.event(image, 0x102), self.event(image, 0x104, 1),
            self.event(image, 0x106), self.event(image, 0x108, 1),
        ] + suffix
        return taken, fall

    def model(self, image, parsed, regions):
        with patch.object(ROLLING_VERIFIER, "COVERAGE_UNITS", ("wrappers",)), \
                patch.object(ROLLING_VERIFIER, "COVERAGE_REGIONS", ("periodic_wrapper",)):
            return ROLLING_VERIFIER.coverage_model(image, {"wrappers": parsed}, regions)

    def cover(self, records, image, model, entries=frozenset({0x100})):
        return ROLLING_VERIFIER.require_coverage(records, image, model, self.INVOKES, entries)

    def test_complete_trace_meets_every_obligation(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, fall = self.runs(image)

        self.assertEqual(self.cover(taken + fall, image, model), dict(
            entries=1, instructions=10, outcomes=2, delay_slots=4,
            call_return_paths=1, register_transfers=1))

    def test_instructions_that_run_only_in_delay_slots_are_executed(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, fall = self.runs(image)
        delayed_only = {0x104, 0x108, 0x10E, 0x112}

        self.assertEqual({pc for pc, _word, delay in taken + fall if not delay}
                         & delayed_only, set())
        self.assertLessEqual(delayed_only, set(model["instructions"]))
        self.cover(taken + fall, image, model)

    def test_each_omitted_outcome_fails(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, fall = self.runs(image)
        for records, message in ((taken, "uncovered branch 0x00000102->0x00000106"),
                                 (fall, "uncovered branch 0x00000102->0x0000010a")):
            with self.subTest(message=message), self.assertRaises(
                    ROLLING_VERIFIER.VerificationError) as caught:
                self.cover(records, image, model)
            self.assertEqual(str(caught.exception), message)

    def test_gaps_name_every_unmet_obligation(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, fall = self.runs(image)
        gaps = ROLLING_VERIFIER.coverage_gaps(taken, image, model, self.INVOKES,
                                              frozenset({0x100}))
        self.assertEqual(gaps, [
            "uncovered branch 0x00000102->0x00000106",
            "uncovered instruction 0x00000106", "uncovered instruction 0x00000108",
            "uncovered delay slot 0x00000108"])
        self.assertEqual(ROLLING_VERIFIER.coverage_gaps(
            taken + fall, image, model, self.INVOKES, frozenset({0x100})), [])
        # Without its trace a span leaves exactly its obligations unmet.
        everything = [ROLLING_VERIFIER.gap_message(*item)
                      for item in ROLLING_VERIFIER.coverage_obligations(model)]
        self.assertEqual(ROLLING_VERIFIER.coverage_gaps(
            [], image, model, self.INVOKES, frozenset({0x100})), everything)
        self.assertEqual(everything[0], "uncovered entry 0x00000100")
        self.assertEqual(
            [item[1] for item in ROLLING_VERIFIER.coverage_obligations(model, (0x106, 0x10A))],
            [0x106, 0x108, 0x108])

    def test_foreign_execution_fails(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, fall = self.runs(image)
        changed = list(taken)
        changed[2] = (0x100, 0x2449, 0)
        pool = fall[:2] + [self.event(image, 0x114)]
        rte = bytearray(image)
        rte[0x308:0x30A] = (0x002B).to_bytes(2, "big")
        cases = (
            (changed + fall, image, frozenset({0x100}), "executed opcode differs at 0x00000100"),
            (pool, image, frozenset({0x114}), "executed covered data at 0x00000114"),
            (fall[2:-1], image, frozenset({0x100}), "return lacks its call at 0x00000106"),
            (taken + fall, image, frozenset({0x10A}), "invoke calls an undeclared entry"),
            (self.runs(image, 0x308)[0] + fall, image, frozenset({0x100}),
             "executed register transfer differs at 0x0000010c"),
            (fall[:2] + [self.event(rte, 0x308)], bytes(rte), frozenset({0x308}),
             "exception return without an exception"),
        )
        for records, fixture, entries, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(
                    ROLLING_VERIFIER.VerificationError, message):
                self.cover(records, fixture, model, entries)

    def test_every_transfer_target_and_call_return_is_required(self):
        image, parsed, regions = self.fixture()
        taken, fall = self.runs(image)
        model = self.model(image, parsed, regions)
        model["transfers"][0x10C] = ("jsr", frozenset({0x300, 0x308}))
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError,
                                    "uncovered register transfer 0x0000010c->0x00000308"):
            self.cover(taken + fall, image, model)
        model = self.model(image, parsed, regions)
        model["calls"].add(0x102)
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError,
                                    "uncovered call return 0x00000102"):
            self.cover(taken + fall, image, model)

    def test_transfer_targets_follow_the_control_flow_of_tracked_units(self):
        layout = rolling_launch_layout.load_layout()
        parsed = rolling_launch_assembly.validate_assembly_sources(layout)
        image = rolling_launch_compose.compose(layout=layout).data

        def targets(unit, address):
            row = next(item for item in parsed[unit].statements if item.address == address)
            return ROLLING_VERIFIER._transfer_targets(parsed[unit], row, image)

        # Each selector path loads its own host; the literal of the other path
        # sits behind an unconditional jump and cannot reach the transfer.
        idle = parsed["wrappers"].labels["rolling_launch_selector_idle"]
        self.assertEqual(targets("wrappers", idle - 4), {0x000D09D8})
        self.assertEqual(targets("wrappers", idle + 2), {0x000D2108})
        # The controller call joins both literal loads through BF.
        call = parsed["engine"].labels["rl_publish_controller"]
        self.assertEqual(targets("engine", call), {0x000D40C0, 0x000D6400})

    def test_a_transfer_without_a_literal_on_every_path_is_unbound(self):
        image, parsed, _regions = self.fixture()
        for text in ("mov r1,r0", "mov r1,r2"):
            statements = tuple(
                replace(item, text=text) if item.address == 0x10A else item
                for item in parsed.statements)
            changed = assembly_model.ParsedSource(parsed.path, parsed.labels, statements)
            row = next(item for item in statements if item.address == 0x10C)
            with self.subTest(text=text), self.assertRaisesRegex(
                    ROLLING_VERIFIER.VerificationError, "unbound register transfer at 0x0000010c"):
                ROLLING_VERIFIER._transfer_targets(changed, row, image)

    def test_omitted_path_is_the_edge_and_the_block_only_it_reaches(self):
        image, parsed, regions = self.fixture()
        model = self.model(image, parsed, regions)
        taken, _fall = self.runs(image)
        # The fall-through of the delayed branch ends after the delay slot of
        # its return; the label of the call joins the other path.
        self.assertEqual(ROLLING_VERIFIER.omitted_path(parsed, "bf/s call", model),
                         ROLLING_VERIFIER.coverage_gaps(taken, image, model, self.INVOKES,
                                                        frozenset({0x100})))
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, "not a branch outcome"):
            ROLLING_VERIFIER.omitted_path(parsed, "tst r4,r4", model)
        layout = rolling_launch_layout.load_layout()
        sources = rolling_launch_assembly.validate_assembly_sources(layout)
        for unit, text in (("speed_controller", ROLLING_ROWS.CONTROLLER_NEGATIVE_EDGE),
                           ("engine", ROLLING_ROWS.ENGINE_NEGATIVE_EDGE)):
            with self.subTest(text=text):
                self.assertEqual(sum(row.kind == "instruction" and row.text == text
                                     for row in sources[unit].statements), 1)
        with self.assertRaisesRegex(ROLLING_VERIFIER.VerificationError, "is not unique"):
            ROLLING_VERIFIER.omitted_path(sources["engine"], "nop", model)


class RollingLaunchRowsTest(unittest.TestCase):
    """The model rows of the Rolling Launch gate and its negative variants."""

    def test_each_variant_removes_only_its_path(self):
        positive = ROLLING_ROWS.build()
        reference = {row.name: row for row in positive.engine}
        self.assertEqual(len(reference), len(positive.engine))
        for variant in ROLLING_ROWS.VARIANTS[1:]:
            rows = ROLLING_ROWS.build(variant)
            engine = {row.name: row for row in rows.engine}
            changed = engine.keys() ^ reference.keys()
            different = {name for name in engine.keys() & reference.keys()
                         if engine[name] != reference[name]}
            with self.subTest(variant=variant):
                if variant == "engine":
                    self.assertEqual((changed, different), ({"cool-config", "cool-table"}, set()))
                else:
                    edited = {"periodic": "speed-periodic",
                              "controller": "ctrl-integrator-lower"}[variant]
                    self.assertEqual((changed, different), (set(), {edited}))
                self.assertEqual(
                    (rows.ignition, rows.control, rows.fraction),
                    (positive.ignition, positive.control, positive.fraction))

    def test_harness_rom_addresses_come_from_the_layouts(self):
        rolling = rolling_launch_layout.load_layout()
        base = layout_model.load_layout()
        self.assertEqual(ROLLING_VERIFIER.harness_definitions(rolling, base), (
            f"-DRL_CONFIG={rolling.configuration.start:#010x}U",
            f"-DRL_TABLE={rolling.efficiency.start:#010x}U",
            f"-DFEEDBACK_COUNTS={base.feedback.phase_counts_address:#010x}U"))
        for name in ("rolling_launch_harness.c", "rolling_launch_irq.c"):
            source = (ROOT / "tools/sh-elf-run" / name).read_text(encoding="utf-8")
            with self.subTest(harness=name):
                self.assertNotRegex(source, r"#define (RL_CONFIG|RL_TABLE|FEEDBACK_COUNTS) ")

    def test_rendered_header_carries_every_row(self):
        rows = ROLLING_ROWS.build()
        header = ROLLING_ROWS.render(rows)
        for row in (*rows.engine, *rows.ignition, *rows.control, *rows.fraction):
            with self.subTest(row=row.name):
                self.assertEqual(header.count(f'{{"{row.name}",'), 1)
        self.assertEqual(sum(ROLLING_ROWS.counts(rows).values())
                         + ROLLING_VERIFIER.WRAPPER_CASES + ROLLING_ROWS.FEEDBACK_CASES,
                         ROLLING_VERIFIER.harness_cases(rows))


ROLLING_IRQ = ROLLING_VERIFIER.rolling_launch_interrupts


class RollingInterruptRowsTest(unittest.TestCase):
    """Acceptance points, scenarios and claims of the Rolling Launch interrupt rows."""

    STORE, LOAD, NOP, LDC_R0, LDC_R6, BRA, OR_MASK = (0x2102, 0x6012, 0x0009, 0x400E, 0x460E,
                                                      0xA000, 0xCBF0)

    def test_store_load_and_inhibit_opcodes(self):
        for opcode in (0x2102, 0x2105, 0x0124, 0x8115, 0x1F12, 0xC10A, 0x4F22, 0x4F13):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertTrue(ROLLING_IRQ.stores(opcode))
        for opcode in (0x6012, 0x8511, 0x4F26, 0x0009, 0x400E):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertFalse(ROLLING_IRQ.stores(opcode))
        for opcode in (0x6012, 0x6F16, 0x017C, 0x8511, 0x5123, 0xC512, 0x4F26, 0x4F07, 0x010F):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertTrue(ROLLING_IRQ.loads(opcode))
        for opcode in (0xD103, 0x9104, 0xC703, 0x2102, 0x0009, 0x000B, 0x400E):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertFalse(ROLLING_IRQ.loads(opcode))
        for opcode in (0x400E, 0x4F07, 0x401E, 0x0002, 0x4F23, 0x401A, 0x4F26, 0x002A,
                       0x4F12, 0x405A, 0xF00D):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertTrue(ROLLING_IRQ.inhibits(opcode))
        for opcode in (0x0009, 0x2102, 0x6012, 0xA000, 0x000B):
            with self.subTest(opcode=f"{opcode:04x}"):
                self.assertFalse(ROLLING_IRQ.inhibits(opcode))

    def _trace(self):
        # A harness LDC sets the engine level; a store precedes a masked group
        # of two stores, and a delay slot store precedes a nop.
        return [
            (0x300, self.LDC_R0, 0), (0x200, self.NOP, 0), (0x202, self.STORE, 0),
            (0x204, self.OR_MASK, 0), (0x206, self.LDC_R0, 0), (0x208, self.STORE, 0),
            (0x20A, self.STORE, 0), (0x20C, self.LDC_R6, 0), (0x20E, self.LOAD, 0),
            (0x210, self.BRA, 0), (0x212, self.STORE, 1), (0x220, self.NOP, 0),
            (0x302, self.NOP, 0),
        ]

    def test_acceptance_follows_the_instruction_after_the_lowering_ldc(self):
        records = self._trace()
        before = ROLLING_IRQ.levels(records)
        self.assertEqual(before[:5], [None, 0, 0, 0, 0])
        self.assertEqual(before[5:9], [15, 15, 15, 0])
        self.assertEqual([ROLLING_IRQ.raises_mask(records, index) for index in (0, 4, 7)],
                         [False, True, False])
        index = {pc: position for position, (pc, _opcode, _delay) in enumerate(records)}
        expected = {0x202: 0x204, 0x208: 0x210, 0x20A: 0x210, 0x212: 0x220}
        for trigger, accepted in expected.items():
            with self.subTest(trigger=f"{trigger:x}"):
                position = ROLLING_IRQ.acceptance(records, index[trigger], before)
                self.assertEqual(records[position][0], accepted)
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "no acceptance point"):
            ROLLING_IRQ.acceptance(records[:9], index[0x208], before)

    def test_triggers_bind_every_memory_access_to_its_pass_and_count(self):
        records = self._trace() * 2
        found = ROLLING_IRQ.triggers(records, 0x200, (0x300, 0x340))
        pcs = [0x200, 0x202, 0x208, 0x20A, 0x20E, 0x212]
        self.assertEqual([(item.scenario, item.pc, item.count) for item in found],
                         [(0, pc, 1) for pc in pcs] + [(1, pc, 2) for pc in pcs])
        first = found[:len(pcs)]
        self.assertEqual([item.store for item in first],
                         [pc in (0x202, 0x208, 0x20A, 0x212) for pc in pcs])
        self.assertEqual([item.deferred for item in first],
                         [pc in (0x208, 0x20A) for pc in pcs])
        self.assertEqual([item.after_ldc for item in first],
                         [pc in (0x208, 0x20A) for pc in pcs])
        self.assertEqual([item.accepted for item in first],
                         [0x202, 0x204, 0x210, 0x210, 0x210, 0x220])
        # The load after the masked group shares its acceptance point.
        self.assertEqual([item.pc for item in ROLLING_IRQ.injections(first)],
                         [0x200, 0x202, 0x208, 0x20A, 0x212])

    def test_scenarios_reach_their_outcomes(self):
        scenarios = ROLLING_ROWS.interrupt_scenarios()
        self.assertEqual([item.kind for item in scenarios],
                         ["steady", "steady", "activation", "activation", "abort", "recovery",
                          "activation", "republication", "republication", "republication"])
        for scenario in scenarios:
            finals = ROLLING_ROWS.interrupt_finals(scenario)
            with self.subTest(scenario=scenario.name):
                self.assertEqual(finals[0] == finals[1], scenario.kind == "steady")
                self.assertEqual(len(finals), 3 if scenario.kind == "recovery" else 2)
                self.assertEqual(len(scenario.prior), 12 if scenario.kind == "republication" else 0)
        header = ROLLING_ROWS.render_interrupts(scenarios)
        for scenario in scenarios:
            self.assertEqual(header.count(f'{{"{scenario.name}",'), 1)
        self.assertEqual(header.count("\n     1, {"), 3)

    def _before_second(self, scenario):
        """The records after the activation stores of ``scenario`` with its first publication."""
        records = (scenario.base, scenario.extension)
        passed = ROLLING_ROWS.engine_pass(records, scenario.inputs)[3]
        neutral = replace(passed, control_error=0, rpm_error_native=0, speed_error=0,
                          integrator=0, torque_command=0,
                          torque_fraction=0 if scenario.regulator == ROLLING_ROWS.model.RegulatorKind.RPM
                          else 1000,
                          law_output=1000, cut_fraction=0, actuation_ready=False,
                          applied_trim=0, stock_command=0, effective_command=0,
                          applied_efficiency=1000)
        return ROLLING_ROWS.with_publication_bytes(ROLLING_ROWS.records(neutral), scenario.prior)

    def test_second_publication_after_the_activation_stores_publishes_ready_p(self):
        for scenario in ROLLING_ROWS.interrupt_scenarios()[7:]:
            with self.subTest(scenario=scenario.name):
                seen = self._before_second(scenario)
                finals = ROLLING_ROWS.interrupt_finals(scenario)
                row = self._row(scenario, seen, final=finals[1])
                self.assertTrue(ROLLING_IRQ.check_republication(row, scenario, seen))
                self.assertEqual(int(row["irq_r5"], 16),
                                 ROLLING_ROWS.ignition_publication(
                                     seen, scenario.stock, scenario.effective).effective_wide)
                with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "publication after it"):
                    ROLLING_IRQ.check_republication(self._row(scenario, seen, final=finals[0]),
                                                    scenario, seen)
                other = ROLLING_ROWS.with_publication_bytes(seen, bytes(12))
                with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "observes records other"):
                    ROLLING_IRQ.check_republication(row, scenario, other)
                # The control error of an earlier hold, or the status view of
                # the IDLE record, rejects the record, and the stock command follows.
                error = (seen[0], seen[1][:0x02] + b"\x00\x37" + seen[1][0x04:])
                for name, rejected in (
                    ("error", error),
                    ("view", ROLLING_ROWS.with_publication_bytes(
                        seen, ROLLING_ROWS.publication_bytes((scenario.base, scenario.extension)))),
                ):
                    with self.subTest(rejected=name):
                        self.assertFalse(ROLLING_IRQ.check_republication(
                            self._row(scenario, rejected, final=finals[0]), scenario, rejected))
                mismatch = replace(scenario, effective=scenario.effective + 1)
                with self.assertRaisesRegex(ROLLING_IRQ.InterruptError,
                                            "of a valid record publishes S"):
                    ROLLING_IRQ.check_republication(
                        self._row(mismatch, seen,
                                  final=ROLLING_ROWS.interrupt_finals(mismatch)[0]),
                        mismatch, seen)

    def test_republication_points_and_transfer(self):
        scenario = ROLLING_ROWS.interrupt_scenarios()[7]
        initial = (scenario.base, scenario.extension)
        final = ROLLING_ROWS.engine_pass(initial, scenario.inputs)[:2]

        def edit(records, region, offset, data):
            parts = [bytearray(records[0]), bytearray(records[1])]
            parts[region][offset:offset + len(data)] = data
            return bytes(parts[0]), bytes(parts[1])

        kind = edit(initial, 1, 0x00, final[1][0x00:0x01])
        trim = edit(kind, 0, 0x1E, final[0][0x1E:0x1F])
        viewed = edit(trim, 1, 0x1F, final[1][0x1F:0x20])
        self.assertEqual(ROLLING_IRQ.republication_points(
            scenario, {0: initial, 1: kind, 2: trim, 3: viewed}), ([1, 2], [2]))
        self.assertEqual(ROLLING_IRQ.expected_republication(scenario, trim, scenario.prior),
                         ROLLING_ROWS.with_publication_bytes(trim, scenario.prior))
        stored = edit(trim, 1, 0x08, b"\x07")
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "publication byte 2"):
            ROLLING_IRQ.expected_republication(scenario, stored, scenario.prior)

    def _row(self, scenario, seen, final=None):
        publication = ROLLING_ROWS.ignition_publication(
            seen, scenario.stock, scenario.effective, contract=False)
        final = final or ROLLING_ROWS.interrupt_finals(scenario)[0]
        return {
            "hits": "1", "returned": f"{ROLLING_IRQ.RETURNED:08x}", "preserved": "1",
            "sp": "1", "gbr": "1", "sr": "00000000", "irq_preserved": "1",
            "irq_r4": f"{publication.stock_wide:08x}", "irq_r5": f"{publication.r5:08x}",
            "irq_sr": f"{ROLLING_IRQ.PUBLISHER_SR:08x}", "seen": b"".join(seen).hex(),
            "published": (publication.base + publication.extension).hex(),
            "final": b"".join(final).hex(),
        }

    def test_steady_pass_requires_a_ready_publication(self):
        scenario = ROLLING_ROWS.interrupt_scenarios()[0]
        records = (scenario.base, scenario.extension)
        self.assertEqual(ROLLING_IRQ.check_interrupted(self._row(scenario, records), scenario),
                         (records, True))
        corrupt = (bytes([3]) + scenario.base[1:], scenario.extension)
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "fails the publisher check"):
            ROLLING_IRQ.check_interrupted(self._row(scenario, corrupt), scenario)
        row = self._row(scenario, records)
        row["irq_r5"] = row["irq_r4"]
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "differs from the model"):
            ROLLING_IRQ.check_interrupted(row, scenario)
        row = self._row(scenario, records)
        row["returned"] = "00000000"
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "interrupt frame differs"):
            ROLLING_IRQ.check_interrupted(row, scenario)

    def test_abort_publishes_stock_after_its_phase_store(self):
        scenario = ROLLING_ROWS.interrupt_scenarios()[4]
        records = (scenario.base, scenario.extension)
        self.assertEqual(ROLLING_IRQ.check_interrupted(self._row(scenario, records), scenario),
                         (records, True))
        moved = (scenario.base[:0x04] + bytes([2]) + scenario.base[0x05:], scenario.extension)
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError,
                                    "active_index_snapshot precede the phase"):
            ROLLING_IRQ.check_interrupted(self._row(scenario, moved), scenario)

    def test_activation_order_rejects_each_reordered_store(self):
        scenario = ROLLING_ROWS.interrupt_scenarios()[2]
        initial = (scenario.base, scenario.extension)
        final = ROLLING_ROWS.engine_pass(initial, scenario.inputs)[:2]
        ROLLING_IRQ.check_activation_order(scenario, [initial, final])

        def edit(records, region, offset, data):
            parts = [bytearray(records[0]), bytearray(records[1])]
            parts[region][offset:offset + len(data)] = data
            return bytes(parts[0]), bytes(parts[1])

        for name, observed, message in (
            ("trim", edit(initial, 0, 0x1E, b"\x14"), "active_max_trim precede the phase"),
            ("map", edit(final, 0, 0x04, initial[0][0x04:0x05]), "mode precedes the map"),
            ("law", edit(final, 1, 0x16, initial[1][0x16:0x18]), "kind precedes the law"),
            ("phase", edit(final, 0, 0x05, initial[0][0x05:0x06]),
             "trim of the run precedes"),
        ):
            with self.subTest(store=name):
                with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, message):
                    ROLLING_IRQ.check_activation_order(scenario, [initial, observed, final])
        with self.assertRaisesRegex(ROLLING_IRQ.InterruptError, "no boundary observes"):
            ROLLING_IRQ.check_activation_order(scenario, [initial])


if __name__ == "__main__":
    unittest.main()
