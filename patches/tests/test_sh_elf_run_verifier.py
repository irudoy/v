import importlib.util
from dataclasses import replace
from io import StringIO
import re
from pathlib import Path
import sys
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

STOCK_MODULE_PATH = ROOT / "tools/sh-elf-run/verify_stock_code.py"
STOCK_SPEC = importlib.util.spec_from_file_location(
    "verify_stock_code_sh_elf", STOCK_MODULE_PATH
)
STOCK_VERIFIER = importlib.util.module_from_spec(STOCK_SPEC)
# The dataclasses of the module resolve their annotations through the module
# registry.
sys.modules[STOCK_SPEC.name] = STOCK_VERIFIER
STOCK_SPEC.loader.exec_module(STOCK_VERIFIER)


def _require_bank_invoker_include_and_symbols(shared, included):
    includes = re.findall(r'^\s*\.include\s+"([^"]+)"\s*$', shared, re.MULTILINE)
    assert includes.count("stock_bank_base_pulse_invoke.s") == 1
    combined = shared + "\n" + included
    exported = "_stock_invoke_bank_base_pulse"
    assert len(re.findall(r'^' + exported + r':$', combined, re.MULTILINE)) == 1
    assert len(re.findall(r'^\s*\.size ' + exported + r',', combined, re.MULTILINE)) == 1
    local = re.findall(r'^(L_bank_base_pulse_[a-z0-9_]+):', combined, re.MULTILINE)
    assert local and len(local) == len(set(local))


def _require_ltft_invoker_include_and_symbols(shared, included):
    includes = re.findall(r'^\s*\.include\s+"([^"]+)"\s*$', shared, re.MULTILINE)
    assert includes.count("stock_ltft_publication_invoke.s") == 1
    combined = shared + "\n" + included
    exported = "_stock_invoke_ltft_publication"
    assert len(re.findall(r'^' + exported + r':$', combined, re.MULTILINE)) == 1
    assert len(re.findall(r'^\s*\.size ' + exported + r',', combined, re.MULTILINE)) == 1
    local = re.findall(r'^(L_ltft_publication_[a-z0-9_]+):', combined, re.MULTILINE)
    assert local and len(local) == len(set(local))


def _require_injection_invoker_include_and_symbols(shared, included):
    includes = re.findall(r'^\s*\.include\s+"([^"]+)"\s*$', shared, re.MULTILINE)
    assert includes.count("stock_injection_start_delay_invoke.s") == 1
    combined = shared + "\n" + included
    exported = "_stock_invoke_injection_start_delay"
    assert len(re.findall(r'^' + exported + r':$', combined, re.MULTILINE)) == 1
    assert len(re.findall(r'^\s*\.size ' + exported + r',', combined, re.MULTILINE)) == 1
    local = re.findall(r'^(L_injection_start_delay_[a-z0-9_]+):', combined, re.MULTILINE)
    assert local and len(local) == len(set(local))


class ShElfRunVerifierTest(unittest.TestCase):
    def test_stock_injection_invoker_include_resolves_to_unique_sibling_source(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        source = STOCK_VERIFIER.TOOL_DIR / "stock_injection_start_delay_invoke.s"
        self.assertTrue(source.is_file())
        self.assertEqual(source.parent, STOCK_VERIFIER.TOOL_DIR)
        _require_injection_invoker_include_and_symbols(shared, source.read_text())

    def test_stock_injection_invoker_refuses_missing_duplicate_and_colliding_bindings(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        included = (STOCK_VERIFIER.TOOL_DIR / "stock_injection_start_delay_invoke.s").read_text()
        directive = '    .include "stock_injection_start_delay_invoke.s"'
        mutations = (
            (shared.replace(directive, ''), included),
            (shared + '\n' + directive, included),
            (shared, included + '\n_stock_invoke_injection_start_delay:\n'),
            (shared + '\nL_injection_start_delay_inner:\n', included),
            (shared, included.replace('.size _stock_invoke_injection_start_delay,', '.size _other,')),
        )
        for changed_shared, changed_included in mutations:
            with self.subTest(shared=changed_shared == shared, included=changed_included == included):
                with self.assertRaises(AssertionError):
                    _require_injection_invoker_include_and_symbols(changed_shared, changed_included)

    def test_stock_ltft_invoker_include_resolves_to_unique_sibling_source(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        source = STOCK_VERIFIER.TOOL_DIR / "stock_ltft_publication_invoke.s"
        self.assertTrue(source.is_file())
        self.assertEqual(source.parent, STOCK_VERIFIER.TOOL_DIR)
        _require_ltft_invoker_include_and_symbols(shared, source.read_text())

    def test_stock_ltft_invoker_refuses_missing_duplicate_and_colliding_bindings(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        included = (STOCK_VERIFIER.TOOL_DIR / "stock_ltft_publication_invoke.s").read_text()
        directive = '    .include "stock_ltft_publication_invoke.s"'
        mutations = (
            (shared.replace(directive, ''), included),
            (shared + '\n' + directive, included),
            (shared, included + '\n_stock_invoke_ltft_publication:\n'),
            (shared + '\nL_ltft_publication_inner:\n', included),
            (shared, included.replace('.size _stock_invoke_ltft_publication,', '.size _other,')),
        )
        for changed_shared, changed_included in mutations:
            with self.subTest(shared=changed_shared == shared, included=changed_included == included):
                with self.assertRaises(AssertionError):
                    _require_ltft_invoker_include_and_symbols(changed_shared, changed_included)

    def test_stock_invoker_assembler_search_path_preserves_all_region_calls(self):
        commands, calls = [], []

        def record_region(region, invoke, build):
            self.assertEqual(invoke, build / "stock-invoke.o")
            calls.append(region)
            return sum((end - start) // 2 for start, end in region.code_spans)

        with patch.object(STOCK_VERIFIER.base_verifier, "run_command", commands.append), \
                patch.object(STOCK_VERIFIER, "run_region", record_region), \
                patch("sys.stdout", StringIO()):
            result = STOCK_VERIFIER.verify()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], [
            STOCK_VERIFIER.base_verifier.AS, "--big", "--isa=sh2e", "-I",
            STOCK_VERIFIER.TOOL_DIR, "-o", commands[0][-2],
            STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s",
        ])
        self.assertEqual(Path(commands[0][-2]).name, "stock-invoke.o")
        self.assertEqual(calls, list(STOCK_VERIFIER.REGIONS))
        self.assertEqual(result["regions"], len(calls))
        self.assertEqual(result["dynamic_cases"], sum(region.cases for region in calls))
        self.assertEqual(result["instructions"], sum(
            (end - start) // 2 for region in calls for start, end in region.code_spans))

    def test_stock_bank_invoker_include_resolves_to_unique_sibling_source(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        source = STOCK_VERIFIER.TOOL_DIR / "stock_bank_base_pulse_invoke.s"
        self.assertTrue(source.is_file())
        self.assertEqual(source.parent, STOCK_VERIFIER.TOOL_DIR)
        _require_bank_invoker_include_and_symbols(shared, source.read_text())

    def test_stock_bank_invoker_refuses_missing_duplicate_and_colliding_bindings(self):
        shared = (STOCK_VERIFIER.TOOL_DIR / "stock_invoke.s").read_text()
        included = (STOCK_VERIFIER.TOOL_DIR / "stock_bank_base_pulse_invoke.s").read_text()
        directive = '    .include "stock_bank_base_pulse_invoke.s"'
        mutations = (
            (shared.replace(directive, ''), included),
            (shared + '\n' + directive, included),
            (shared, included + '\n_stock_invoke_bank_base_pulse:\n'),
            (shared + '\nL_bank_base_pulse_inner:\n', included),
            (shared, included.replace('.size _stock_invoke_bank_base_pulse,', '.size _other,')),
        )
        for changed_shared, changed_included in mutations:
            with self.subTest(shared=changed_shared == shared, included=changed_included == included):
                with self.assertRaises(AssertionError):
                    _require_bank_invoker_include_and_symbols(changed_shared, changed_included)

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
        (profile,) = can_telemetry_profile.load_manifest().profiles
        previous, high = profile.profile_id - 1, profile.profile_id + 1
        harness = (
            ROOT / "tools/sh-elf-run/can_telemetry_harness.c"
        ).read_text(encoding="utf-8")
        published = " ".join(
            (ROOT / "patches/can-telemetry.md").read_text(encoding="utf-8").split()
        )

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
            runtime_targets.kb_targets.layout_of(rom): (
                runtime_targets.knock_surface_bits(
                    runtime_targets.kb_targets.layout_of(rom)
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
        self.assertEqual(harness.count("TARGET_1ME3B"), 1)

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

    def test_stock_fixture_keeps_the_region_and_aliases_its_pool(self):
        for region in STOCK_VERIFIER.REGIONS:
            with self.subTest(region=region.key):
                image = STOCK_VERIFIER.stock_image(region.rom)
                fixture = STOCK_VERIFIER.build_fixture(region, image)
                changed = {
                    index for index, (actual, stock) in
                    enumerate(zip(fixture, image)) if actual != stock
                }
                allowed = (
                    set(range(region.end, region.end + len(STOCK_VERIFIER.return_stub(region))))
                    if region.boundary else set()
                )
                for address in region.ram_literals:
                    allowed.update(range(address, address + 4))
                    value = int.from_bytes(image[address:address + 4], "big")
                    self.assertEqual(
                        fixture[address:address + 4],
                        VERIFIER.alias_high_ram(value).to_bytes(4, "big"),
                    )
                for address, original, alias, size in region.ram_word_literals:
                    allowed.update(range(address, address + 2))
                    self.assertEqual(int.from_bytes(image[address:address + 2], "big") | 0xffff0000, original)
                    self.assertEqual(fixture[address:address + 2], alias.to_bytes(2, "big"))
                for address, original, alias, size in region.register_word_literals:
                    allowed.update(range(address, address + 2))
                    self.assertEqual(int.from_bytes(image[address:address + 2], "big") | 0xffff0000, original)
                    self.assertEqual(fixture[address:address + 2], alias.to_bytes(2, "big"))
                self.assertLessEqual(changed, allowed)
                for start, end in region.code_spans:
                    self.assertEqual(fixture[start:end], image[start:end])
                tail = range(region.end, region.end + len(STOCK_VERIFIER.return_stub(region)))
                if region.boundary:
                    self.assertEqual(fixture[tail.start:tail.stop], STOCK_VERIFIER.return_stub(region))
                else:
                    for address in tail:
                        if address not in allowed:
                            self.assertEqual(fixture[address], image[address])

    def test_stock_harness_takes_the_symbols_of_the_entity_files(self):
        regions = {region.key: region for region in STOCK_VERIFIER.REGIONS}
        fuel_cut = {
            "ARMED_MASK": 0x20,
            "ACTIVE_MASK": 0x40,
            "ENGINE_SPEED": 0xFFFF11CA,
        }
        expected = {
            'jk08a-base-accumulator': {'REGION_ENTRY': 349358, 'TERM': 4294907384, 'CONDITIONAL': 4294910732, 'COOLANT': 4294907354, 'OUTPUT': 4294910746, 'EARLY_ONLY': 0},
            'jk08a-transient-coefficient': {'REGION_ENTRY': 338110, 'TERM': 4294908518, 'NORMALIZED': 4294905900, 'OUTPUT': 4294907146, 'EARLY_ONLY': 0},
            'jk08a-transient-additive': {'REGION_ENTRY': 338178, 'TERM': 4294908518, 'COEFFICIENT': 4294907146, 'FLAGS': 4294911069, 'OUTPUT': 4294910720, 'EARLY_ONLY': 0},
            'jk08a-coolant-conditional': {'REGION_ENTRY': 348762, 'OUTPUT': 4294907354, 'EARLY_ONLY': 0},
            'jk08a-transient-pair-1': {'REGION_ENTRY': 336956, 'TERM': 4294908518, 'NORMALIZED': 4294905900, 'OUTPUT': 4294910720, 'EARLY_ONLY': 0},
            'jk08a-transient-pair-2': {'REGION_ENTRY': 337054, 'TERM': 4294908518, 'NORMALIZED': 4294905900, 'OUTPUT': 4294910720, 'EARLY_ONLY': 0},
            'jk08a-fuel-multiplier': {'REGION_ENTRY': 349932, 'OUTPUT': 4294910694, 'SNAPSHOT': 4294908132, 'EARLY_ONLY': 0, 'WORD_ALIAS': 31232},
            'jk08a-pulse-precursor': {'REGION_ENTRY': 321908, 'OUTPUT': 4294908022, 'BANKS': 4294908096, 'EARLY_ONLY': 0, 'SELECTED_BFS': 4294908266},
            'jk08a-common-gain': {'REGION_ENTRY': 341656, 'OUTPUT': 4294907486, 'FACTOR': 4294907405, 'EARLY_ONLY': 0},
            'jk08a-enrichment-prefix': {'REGION_ENTRY': 350712, 'OUTPUT': 4294907371, 'PREFIX_ENTRY': 350538, 'EARLY_ONLY': 0},
            'jk08a-enrichment-terminal': {'REGION_ENTRY': 353288, 'OUTPUT': 4294910696, 'EARLY_ONLY': 0, 'TERMINAL_ENTRY': 352994, 'WORD_ALIAS': 31232},
            'jk08a-opening-word': {'REGION_ENTRY': 356288, 'BATTERY': 4294906120, 'OPENING': 4294911030, 'EARLY_ONLY': 0},
            'jk08a-pulse-selector': {'REGION_ENTRY': 347454, 'OUTPUT': 4294910542, 'SNAPSHOT': 4294910792, 'EARLY_ONLY': 0},
            'jk08a-full-programmer': {'REGION_ENTRY': 177738, 'CONTROL': 4294935788, 'COUNT': 4294906808, 'REMAINDER': 4294908219, 'MODE': 4294911177, 'POSITION': 4294906802, 'PERIOD': 4294910652, 'OUTPUT': 4294907586, 'SCRATCH': 4294907500, 'COUNTER_REGISTER': 4294964288, 'COMPARE_REGISTER': 4294964292, 'STATUS_REGISTER': 4294964318, 'CONTROL_REGISTER': 4294964322, 'EARLY_ONLY': 0, 'WORD_ALIAS': 32512, 'REGISTER_ALIAS': 32256},
            'jk08a-oneshot': {'REGION_ENTRY': 180540, 'COUNTER_REGISTER': 4294964800, 'START_REGISTER': 4294964838, 'OPENING': 4294910890, 'INHIBIT': 4294910688, 'HISTORY': 4294908213, 'ENABLE': 4294918532, 'DIAGNOSTIC': 4294918737, 'EARLY_ONLY': 0, 'REGISTER_ALIAS': 32000},
            'jk08a-rpm-phase-word': {'REGION_ENTRY': 230662, 'INPUT_WORD': 4294906262, 'WORK_WORD': 4294906344, 'WORK_BYTE': 4294906347, 'SNAPSHOT_BYTE': 4294906291, 'EARLY_ONLY': 0, 'VIEW_KIND': 0},
            'jk08a-rpm-phase-byte': {'REGION_ENTRY': 230604, 'INPUT_WORD': 4294906262, 'WORK_WORD': 4294906344, 'WORK_BYTE': 4294906347, 'SNAPSHOT_BYTE': 4294906291, 'EARLY_ONLY': 0, 'VIEW_KIND': 1},
            'jk08a-rpm-phase-copy': {'REGION_ENTRY': 135008, 'INPUT_WORD': 4294906262, 'WORK_WORD': 4294906344, 'WORK_BYTE': 4294906347, 'SNAPSHOT_BYTE': 4294906291, 'EARLY_ONLY': 0, 'VIEW_KIND': 2},
            'jk08a-event-isr': {'REGION_ENTRY': 179776, 'TIMER_REGISTER': 4294964288, 'STATUS_REGISTER': 4294964318, 'CONTROL_REGISTER': 4294964322, 'COUNTER_REGISTER': 4294964800, 'START_REGISTER': 4294964838, 'EARLY_ONLY': 0, 'TIMER_ALIAS': 32256, 'PULSE_ALIAS': 32000, 'CONTROL_ALIAS': 32512, 'EVENT_ALIAS': 31744},
            'jk08a-end-angle': {'REGION_ENTRY': 355280, 'EARLY_ONLY': 0},
            'jk08a-full-dispatch': {'REGION_ENTRY': 346692, 'TIMER_REGISTER': 4294964288, 'STATUS_REGISTER': 4294964318, 'CONTROL_REGISTER': 4294964322, 'COUNTER_REGISTER': 4294964800, 'START_REGISTER': 4294964838, 'EARLY_ONLY': 0, 'TIMER_ALIAS': 32256, 'PULSE_ALIAS': 32000, 'CONTROL_ALIAS': 32512, 'EVENT_ALIAS': 31488},
            'jk08a-channel-pulse': {'REGION_ENTRY': 322466, 'INHIBIT': 4294910688, 'COMPENSATED': 4294910920, 'TRANSFORMED': 4294910932, 'OPENING': 4294911030, 'ADDITIVE': 4294906774, 'SUBTRACTIVE': 4294906982, 'MULTIPLIER': 76224, 'EARLY_ONLY': 0},
            'jk08a-injection-prologue': {'REGION_ENTRY': 177738, 'CONTROL': 4294935788, 'EARLY_ONLY': 0, 'WORD_ALIAS': 32512},
            'jk08a-injection-count': {'REGION_ENTRY': 177870, 'COUNT': 4294906808, 'PERIOD': 4294910652, 'REMAINDER': 4294908219, 'OUTPUT': 4294907586, 'SCRATCH': 4294907500, 'EARLY_ONLY': 0},
            'jk08a-injection-dispatch': {'REGION_ENTRY': 347404, 'LEAD': 4294910493, 'FLAG': 4294918737, 'EARLY_ONLY': 0},
            'jk08a-injection-catchup': {'REGION_ENTRY': 347220, 'CURSOR': 4294910494, 'QUEUE': 4294910133, 'CLEAR': 4294908213, 'MASK_A': 4294907262, 'MASK_B': 4294907646, 'EARLY_ONLY': 0},
            'jk08a-injection-pending': {'REGION_ENTRY': 347398, 'SLOT': 4294910132, 'CURSOR': 4294910494, 'PENDING': 4294910504, 'ZERO_ENTRY': 347100, 'NEGATIVE_ENTRY': 347150, 'EARLY_ONLY': 0},
            'jk08a-injection-reciprocal': {'REGION_ENTRY': 167548, 'OUTPUT': 4294907586, 'REMAINDER': 4294908219, 'EARLY_ONLY': 0},
            'jk08a-injection-tooth': {'REGION_ENTRY': 177760, 'COUNT': 4294906808, 'REMAINDER': 4294908219, 'MODE': 4294911177, 'POSITION': 4294906802, 'DIRECT_ENTRY': 177782, 'NORMALIZER_ENTRY': 167368, 'EARLY_ONLY': 0},
            'jk08a-injection-offset': {'REGION_ENTRY': 177876, 'PERIOD': 4294910652, 'REMAINDER': 4294908219, 'OUTPUT': 4294907586, 'SCRATCH': 4294907500, 'EARLY_ONLY': 0},
            "jk08a-injection-slot": {
                "REGION_ENTRY": 0x00054A64, "CYLINDER": 0xFFFF11DE,
                "LEAD": 0xFFFF2364, "MODE": 0xFFFF8513,
                "COUNTER": 0xFFFF4555, "HISTORY": 0xFFFF1526,
                "SLOT": 0xFFFF20B4, "EARLY_ONLY": 0,
            },
            "jk08a-injection-snapshot": {
                "REGION_ENTRY": 0x00021314,
                "LEAD_SOURCE": 0xFFFF23F0,
                "ANGLE_SOURCE": 0xFFFF23BF,
                "LEAD_SNAPSHOT": 0xFFFF2364,
                "ANGLE_SNAPSHOT": 0xFFFF2333,
                "EARLY_ONLY": 0,
            },
            'jk08a-can-latch-copy': {'REGION_ENTRY': 0x21094, 'EARLY_ONLY': 0},
            "jk08a-injection-start-delay": {
                "REGION_ENTRY": 0x000521A8,
                "PRIMARY_SPEED": 0xFFFF11BC,
                "ALTERNATE_SPEED": 0xFFFF10CA,
                "PULSES": 0xFFFF23D4,
                "FLOOR": 0xFFFF241C,
                "END": 0xFFFF192E,
                "SPEED_SELECTOR": 0xFFFF4184,
                "DELAY_CONTROL": 0xFFFF24C9,
                "LEAD_OVERRIDE": 0xFFFF4251,
                "ANGLE_OUTPUT": 0xFFFF23BF,
                "LEAD_OUTPUT": 0xFFFF23F0,
                "DELAY_CONFIG": 0x000083EA,
            },
            "jk08a-ltft-publication": {
                "REGION_ENTRY": 0x00057B26,
                "SELECTED": 0xFFFF2306,
                "ADJUSTMENT": 0xFFFF5648,
                "OUTPUT": 0xFFFF2302,
                "MASK": 0xFFFF230E,
                "COMPARE_U": 0xFFFF15FC,
                "COMPARE_V": 0xFFFF15FE,
                "DIAGNOSTIC_RECORD": 0xFFFF5A93,
                "CONTROL_F": 0xFFFF41B5,
                "CONTROL_G": 0xFFFF41FA,
                "CONTROL_H": 0xFFFF248B,
                "CONTROL_K": 0xFFFF249C,
                "LOWER": 0x00008E5B,
                "UPPER": 0x00008E5A,
                "DIAGNOSTIC_BYTE1_OFFSET": 1,
            },
            "jk08a-knock-reference-learning": {
                "REGION_ENTRY": 0x0004A118,
                "REFERENCES": 0xFFFF2178,
                "SAMPLES": 0xFFFF20C2,
                "PRIMARY": 0xFFFF11DE,
                "ALTERNATE": 0xFFFF2143,
                "DIAGNOSTICS": 0xFFFF5718,
                "SELECTOR": 0x00008B3D,
                "WEIGHT": 0x0000884B,
                "RESET_WORD": 0x00009282,
                "PREDICATE_ENTRY": 0x00025E20,
            },
            "jk08a-bank-base-pulse": {
                "REGION_ENTRY": 0x0004EAD4,
                "STFT": 0xFFFF22DC, "LTFT": 0xFFFF2302,
                "EXTRA": 0xFFFF2A24, "PRECURSOR": 0xFFFF18C0,
                "ADDITIVE": 0xFFFF2436, "OFFSET": 0xFFFF2310,
                "CONTROL0": 0xFFFF22E6, "CONTROL1": 0xFFFF22E8,
                "OUTPUT": 0xFFFF191C,
                "LTFT_CONFIG": 0x0000893D, "CONTROL_CONFIG": 0x00008940,
            },
            "jk08a-knock-state-selection": {
                "REGION_ENTRY": 0x00049614, "POST_LOOKUP_ENTRY": 0x00049614,
                "ALTERNATIVE_ENTRY": 0x000499B8,
                "SOURCE_STATE": 0xFFFF1258, "TARGET_STATE": 0xFFFF1380,
                "NEGATIVE_BOUND": 0xFFFF230A,
                "GATE69": 0xFFFF2469, "GATE67": 0xFFFF2467,
                "WORD_OUTPUT": 0xFFFF121A, "BYTE_OUTPUT": 0xFFFF22FA,
                "SLEW_STEP": 0x00009078,
            },
            "jk08a-knock-event-publication": {
                "REGION_ENTRY": 0x0004DB86, "PUBLICATION_ENTRY": 0x0004DB48,
                "RETARD": 0xFFFF11D6, "SNAPSHOT": 0xFFFF2378,
                "CORRECTION": 0xFFFF2356, "SCALED_RAM": 0xFFFF1FF6,
                "LONG_SUM": 0xFFFF1FF8, "BYTE_OUTPUT": 0xFFFF12D6,
            },
            "jk08a-knock-event-retard": {
                "REGION_ENTRY": 0x0004D9AC,
                "FIRST": 0xFFFF11D6, "SECOND": 0xFFFF11D8,
                "KNOCK_BYTE": 0xFFFF22FA,
                "REQUEST_A": 0xFFFF11F9, "REQUEST_B": 0xFFFF11FA,
                "SOURCE_WORD": 0xFFFF23C2,
                "FLAG5": 0xFFFF24C5, "FLAGB": 0xFFFF24CB,
                "MODE": 0x00008710,
            },
            "jk08a-knock-integration": {
                "REGION_ENTRY": 0x0004956A,
                "STATE": 0xFFFF1258, "OUTPUT": 0xFFFF1380,
                "COUNT": 0xFFFF2142,
                "QUIET_ENTRY": 0x00049544, "EVENT_ENTRY": 0x00049900,
            },
            "jk08a-knock-timing-byte": {
                "REGION_ENTRY": 0x000496CC,
                "WORD_STATE": 0xFFFF121A, "BYTE_STATE": 0xFFFF22FA,
                "CONVERSION_ENTRY": 0x0004964A,
            },
            "jk08a-knock-comparison": {
                "REGION_ENTRY": 0x0004A2EE, "TABLE": 0x0001108E,
                "AXIS": 0x00015340, "MODE": 0x00008B3D,
                "PRIMARY": 0xFFFF11DE, "ALTERNATE": 0xFFFF2143,
                "SPEED": 0xFFFF11F4, "THRESHOLDS": 0xFFFF2144,
                "METRICS": 0xFFFF21D8, "COUNT": 0xFFFF2142,
                "STATUS": 0xFFFF24C2, "BITMAP": 0xFFFF2150,
                "SHIFT_ENTRY": 0x000221BC, "JUMP_TABLE": 0x0002219C,
            },
            "jk08a-knock-threshold": {
                "REGION_ENTRY": 0x00049FFC, "TABLE": 0x0001108E,
                "AXIS": 0x00015340, "MODE": 0x00008B3D,
                "PRIMARY": 0xFFFF11DE, "ALTERNATE": 0xFFFF2143,
                "SPEED": 0xFFFF11F4, "THRESHOLDS": 0xFFFF2144,
                "WRAPPER_ENTRY": 0x000264F8, "LINEAR_ENTRY": 0x00026740,
                "AXIS_ENTRY": 0x00026984, "DIVIDER_ENTRY": 0x00026C78,
            },
            "jk08a-bfs-rate": {
                "REGION_ENTRY": 0x0003BB24, "PRIMARY_ENTRY": 0x0003B908,
                "CORRECTION_ENTRY": 0x0003BAB8, "BLEND_ENTRY": 0x0003BB3C,
                "POST_QUERY_ENTRY": 0x0003BA6A, "QUERY_ENTRY": 0x000259E4,
                "PRIMARY_BASE": 0xFFFF1114, "MODE_BASE": 0xFFFF2460,
                "Q7_SOURCE": 0xFFFF1062, "SELECTED_SOURCE": 0xFFFF115C,
                "COEFFICIENT": 0xFFFF1F30, "REFERENCE": 0xFFFF1E06,
                "WORKING": 0xFFFF1DEE, "BLENDED": 0xFFFF1DEC,
                "CORRECTION": 0xFFFF1060, "FLAGS": 0xFFFF24B1,
                "ALPHA": 0xFFFF1170, "ENABLE": 0xFFFF2462,
                "DIAGNOSTIC": 0xFFFF24BD, "WEIGHT": 0xFFFF1EE1,
                "BLEND_PRIOR": 0xFFFF1E04, "TIMER_FIRST": 0xFFFF1E20,
                "TIMER_SECOND": 0xFFFF1E47, "TIMER_THIRD": 0xFFFF1E4C,
                "SOURCE_FIRST": 0xFFFF2449, "SOURCE_SECOND": 0xFFFF4250,
                "MONITOR": 0xFFFF244E, "MODE": 0x00008D92,
                "CORRECTION_GAIN": 0x0000865A, "LATCH_SET": 0x00008319,
                "LATCH_CLEAR": 0x0000831A, "QUERY_RECORDS": 0xFFFF5718,
            },
            "jk08a-fuel-compensation": {
                "REGION_ENTRY": 0x0003C284, "SELECTOR_ENTRY": 0x0003C1C0,
                "PRIMARY_BASE": 0xFFFF1114, "WRAPPER_ENTRY": 0x000261F0,
                "DIVIDER_ENTRY": 0x00026C78, "RPM_SOURCE": 0xFFFF11F4,
                "COL_SOURCE": 0xFFFF1170, "OUTPUT": 0xFFFF1160,
                "FIRST_SOURCE": 0xFFFF5625, "SECOND_SOURCE": 0xFFFF2836,
                "MODE_A": 0x00008B42, "MODE_B": 0x00008B34,
                "SOURCE_MODE": 0x000086F9, "BYPASS_SCALAR": 0x0000851A,
                "TABLE": 0x0000A29A, "ROW_AXIS": 0x00011CF0,
                "COL_AXIS": 0x00011D4C,
            },
            "jk08a-bfs-limit": {
                "REGION_ENTRY": 0x0003BC78, "SELECTOR_ENTRY": 0x0003BB86,
                "PRIMARY_BASE": 0xFFFF1DEC, "WORKING": 0xFFFF1DEE,
                "BLENDED": 0xFFFF1DEC, "CORRECTION": 0xFFFF1060,
                "FLAGS": 0xFFFF2449, "SPEED_BYTE": 0xFFFF11EA,
                "RPM_BYTE": 0xFFFF11EB, "THROTTLE_BYTE": 0xFFFF1075,
                "CAP_BYTE": 0xFFFF1E46, "OUTPUT": 0xFFFF1026,
                "LIMIT_TABLE": 0x00012C9E, "ALTERNATE_TABLE": 0x0000974E,
                "WRAPPER_ENTRY": 0x00026388, "BODY_ENTRY": 0x00026A84,
            },
            "jk08a-bfs-base": {
                "REGION_ENTRY": 0x0003B8DA, "PRIMARY_ENTRY": 0x0003B7C6,
                "PRIMARY_BASE": 0xFFFF1DEC, "AGGREGATE": 0xFFFF1E38,
                "PRIMARY_SPEED": 0xFFFF11E8, "ALTERNATE_SPEED": 0xFFFF11DC,
                "SPEED_FLAGS": 0xFFFF2461, "QUARTER_BFS": 0xFFFF1E40,
                "COMPENSATION": 0xFFFF1160, "COMPENSATED_BFS": 0xFFFF1062,
                "CONTROL_BYTE": 0xFFFF24B1, "K_ADDRESS": 0x00009284,
                "FACTOR_ADDRESS": 0x00008A27, "E_ADDRESS": 0x000088FB,
                "DIVIDER_ENTRY": 0x00021CE0, "REMAINDER_ENTRY": 0x00021F40,
                "FAULT_ADDRESS": 0xFFFF9818,
            },
            "jk08a-maf-contribution": {
                "REGION_ENTRY": 0x0003AF42,
                "MAF_INPUT_B1": 0xFFFF1DF0, "MAF_INPUT_B2": 0xFFFF1DF2,
                "MAF_OUTPUT_B1": 0xFFFF1DF8, "MAF_OUTPUT_B2": 0xFFFF1DFC,
                "ENABLE_FLAGS": 0xFFFF2462, "DIAGNOSTIC_FLAGS": 0xFFFF2449,
                "INHIBIT_FLAGS": 0xFFFF24B8,
                "TAIL_ENTRY": 0x0003B042, "CONTRIBUTION_BASE": 0xFFFF1DEC,
                "COEFFICIENT_ADDRESS": 0x000082B6, "FALLBACK_WEIGHT_ADDRESS": 0x00008AC3,
                "BASE_B1": 0xFFFF1E00, "BASE_B2": 0xFFFF1E02,
                "REFERENCE_B1": 0xFFFF1E08, "REFERENCE_B2": 0xFFFF1E0A,
                "FALLBACK_B1": 0xFFFF1E10, "FALLBACK_B2": 0xFFFF1E14,
                "DELTA_B1": 0xFFFF1E18, "DELTA_B2": 0xFFFF1E1A,
                "CORRECTION_B1": 0xFFFF1E1C, "CORRECTION_B2": 0xFFFF1E1E,
                "MAGNITUDE_B1": 0xFFFF1E30, "MAGNITUDE_B2": 0xFFFF1E32,
                "SIGN_FLAGS": 0xFFFF1E34, "LATCH_B1": 0xFFFF43CA, "LATCH_B2": 0xFFFF43CB,
            },
            "jk08a-load-snapshot": {
                "REGION_ENTRY": 0x00020F04,
                "BFS_NEWEST": 0xFFFF1026,
                "BFS_CURRENT": 0xFFFF1024,
                "BFS_PREVIOUS": 0xFFFF1028,
                "LIVE_LOAD": 0xFFFF1048,
                "SNAPSHOT_LOAD": 0xFFFF102C,
                "COPY_SIZE": 28,
            },
            "jk08a-load-normalization": {
                "REGION_ENTRY": 0x0003BD1C,
                "BFS_INPUT": 0xFFFF1026,
                "LIVE_LOAD": 0xFFFF1048,
                "REFERENCE_ADDRESS": 0x00009534,
                "DIVIDER_ENTRY": 0x00021CE0,
                "FAULT_ADDRESS": 0xFFFF9818,
            },
            "jk08a-maf-aggregate": {
                "REGION_ENTRY": 0x0003B252,
                "MAF_BANK1": 0xFFFF1DF8,
                "MAF_BANK2": 0xFFFF1DFC,
                "MAF_CORRECTION": 0xFFFF1E2A,
                "MAF_AUXILIARY": 0xFFFF2368,
                "MAF_AGGREGATE": 0xFFFF1E38,
            },
            "jk08a-maf-filter": {
                "REGION_ENTRY": 0x0003A982,
                "MAF_SOURCE_B1": 0xFFFF1054,
                "MAF_SOURCE_B2": 0xFFFF1056,
                "MAF_WORKING_B1": 0xFFFF1058,
                "MAF_WORKING_B2": 0xFFFF105A,
                "MAF_FILTERED_B1": 0xFFFF1DF0,
                "MAF_FILTERED_B2": 0xFFFF1DF2,
                "MODE_FLAGS": 0xFFFF2461,
                "FILTER_ENTRY": 0x0003A9AA,
                "COPY_CAP_ENTRY": 0x0003A996,
                "ANTI_STALL_ENTRY": 0x0003A9EC,
                "COEFFICIENT_ADDRESS": 0x0000870A,
                "FILTER_BASE": 0xFFFF1DEC,
            },
            "jk08a-maf-transfer": {
                "REGION_ENTRY": 0x0003A922,
                "MAF_INPUT_B1": 0xFFFF1E48,
                "MAF_INPUT_B2": 0xFFFF1E4A,
                "MAF_OUTPUT_B1": 0xFFFF1054,
                "MAF_OUTPUT_B2": 0xFFFF1056,
                "MAF_TABLE_B1": 0x00014274,
                "MAF_TABLE_B2": 0x000141F4,
                "CURVE_ENTRY": 0x00026410,
                "BODY_ENTRY": 0x00026A74,
                "INPUT_BASE": 0xFFFF1E1C,
                "CORRECTION_OUTPUT": 0xFFFF1E2A,
            },
            "jk08a-maf-compensation": {
                "REGION_ENTRY": 0x0003AE8A,
                "MAF_INPUT_B1": 0xFFFF101C,
                "MAF_INPUT_B2": 0xFFFF101E,
                "MAF_OUTPUT_B1": 0xFFFF1E48,
                "MAF_OUTPUT_B2": 0xFFFF1E4A,
                "CORRECTION_B1": 0xFFFF3998,
                "CORRECTION_B2": 0xFFFF399C,
                "INIT_FLAGS": 0xFFFF3976,
                "DIVIDER_ENTRY": 0x00021CE0,
                "ZERO_DEN_ENTRY": 0x0003AEF2,
                "MULTIPLIER_ADDRESS": 0x00009586,
                "BIAS_ADDRESS": 0x0000958C,
                "FAULT_ADDRESS": 0xFFFF9818,
            },
            "jk08a-battery-scaling": {
                "REGION_ENTRY": 0x00039A9E,
                "BATTERY_SAMPLE": 0xFFFF1D6E,
                "BATTERY_COPY": 0xFFFF1FC4,
                "BATTERY_BYTE": 0xFFFF1FC6,
                "BATTERY_OUTPUT": 0xFFFF1188,
                "COEFFICIENT": 0xFFFF4970,
                "MODE_FLAGS": 0xFFFF4252,
            },
            "jk08a-maf-scaling": {
                "REGION_ENTRY": 0x0003C408,
                "MAF_SAMPLE_B1": 0xFFFF1D62,
                "MAF_SAMPLE_B2": 0xFFFF1D64,
                "MAF_OUTPUT_B1": 0xFFFF101C,
                "MAF_OUTPUT_B2": 0xFFFF101E,
                "COEFFICIENT": 0xFFFF4970,
                "MODE_FLAGS": 0xFFFF4252,
                "GUARD_ENTRY": 0x00067188,
                "SCALE_ENTRY": 0x000671D8,
                "CAP_ENTRY": 0x0003C444,
                "BOUNDS_ADDRESS": 0x000087F8,
                "DEFAULT_ADDRESS": 0x000092BE,
            },
            "jk08a-maf-adc": {
                "REGION_ENTRY": 0x000280B6,
                "ADC_BASE": 0xFFFFF800,
                "ADDR4": 0xFFFFF808,
                "ADDR15": 0xFFFFF826,
                "MAF_SAMPLE_B1": 0xFFFF1D62,
                "MAF_SAMPLE_B2": 0xFFFF1D64,
            },
            "jk08a-direct-byte-axis": {
                "REGION_ENTRY": 0x00026944,
                "LAST_OFFSET": 15,
                "AXIS_BYTES": 16,
                "DIVIDER_ENTRY": 0x00026C78,
                "CVTC_RPM_AXIS": 0x00012F3E,
                "CVTC_LOAD_AXIS": 0x00012F1E,
            },
            "jk08a-implicit-byte-curve": {
                "REGION_ENTRY": 0x00026370,
                "BODY_ENTRY": 0x00026A80,
                "INJECTION_TABLE": 0x00012302,
                "COLD_TIMING_TABLE": 0x00012196,
            },
            "jk08a-byte-axis": {
                "REGION_ENTRY": 0x000269C4,
                "LAST_OFFSET": 15,
                "AXIS_BYTES": 16,
                "DIVIDER_ENTRY": 0x00026C78,
                "FUEL_AXIS": 0x00011CF0,
                "IGNITION_AXIS": 0x00011ECE,
            },
            "jk08a-word-axis": {
                "REGION_ENTRY": 0x00026984,
                "LAST_OFFSET": 30,
                "AXIS_BYTES": 32,
                "DIVIDER_ENTRY": 0x00026C78,
                "TORQUE_AXIS": 0x00014B4A,
            },
            "jk08a-crank-capture": {
                "REGION_ENTRY": 0x00028F16,
                "CRANK_BASE": 0xFFFF128C,
                "CORE_BASE": 0xFFFF1FF4,
                "MMIO_BASE": 0xFFFFF440,
                "REFERENCE_PERIOD": 0xFFFF2294,
                "INIT_MASK": 0x40,
                "OSBR1": 0xFFFFF456,
                "CRANK_CAPTURE": 0xFFFF158A,
                "RAW_PERIOD": 0xFFFF22BA,
                "CAPTURE_FLAGS": 0xFFFF24C1,
            },
            "jk08a-tooth-normalization": {
                "REGION_ENTRY": 0x0002915C,
                "NORMALIZATION_ENTRY": 0x0002911C,
                "REFERENCE_PERIOD": 0xFFFF2296,
                "CRANK_BASE": 0xFFFF128C,
                "CORE_BASE": 0xFFFF1FF4,
                "SYNC_MASK": 0x80,
                "TOOTH_COUNTER": 0xFFFF13B2,
                "RAW_PERIOD": 0xFFFF22BA,
                "NORMALIZED_PERIOD": 0xFFFF22BC,
            },
            "jk08a-tooth-fallback": {
                "REGION_ENTRY": 0x0002B800,
                "CORE_BASE": 0xFFFF1FF4,
                "EVENT_INTERVAL": 0xFFFF11FC,
                "RAW_PERIOD": 0xFFFF22BA,
                "NORMALIZED_PERIOD": 0xFFFF22BC,
                "CAM_INTERVAL": 0xFFFF22D4,
            },
            "jk08a-event-interval": {
                "REGION_ENTRY": 0x00028AFA,
                "MODE_FLAGS": 0xFFFF24C9,
                "CURRENT_CAPTURE": 0xFFFF185C,
                "PREVIOUS_CAPTURE": 0xFFFF84CC,
                "EVENT_INTERVAL": 0xFFFF11FC,
                "PUBLISHED_FLAGS": 0xFFFF2465,
                "HOLDOFF": 0xFFFF25FF,
            },
            "jk08a-rpm-median": {
                "REGION_ENTRY": 0x0003DF2C,
                "MODE_FLAGS": 0xFFFF24C9,
                "TOOTH_PERIOD": 0xFFFF22BC,
                "MEDIAN_OUTPUT": 0xFFFF2804,
                "LIVE_SPEED": 0xFFFF11EA,
                "HISTORY_NEWEST": 0xFFFF3E34,
                "DIVIDER_ENTRY": 0x00021BBC,
                "FAULT_POINTER": 0x00021CD8,
                "FAULT_VALUE": 0x00021CDC,
                "HISTORY_PREVIOUS": 0xFFFF3E35,
                "HISTORY_OLDER": 0xFFFF3E36,
            },
            "jk08a-rpm-division": {
                "REGION_ENTRY": 0x00038272,
                "MODE_FLAGS": 0xFFFF417F,
                "EVENT_INTERVAL": 0xFFFF11FC,
                "ENGINE_SPEED": 0xFFFF1196,
                "DIVIDER_ENTRY": 0x00021CE0,
                "FAULT_POINTER": 0x00021DC8,
                "FAULT_VALUE": 0x00021DCC,
            },
            "jk08a-rpm-drop-arithmetic": {
                "REGION_ENTRY": 0x0003E1FE,
                "DROP_WORD": 0xFFFF1E50,
                "CURRENT_SPEED": 0xFFFF114A,
                "HISTORY_SPEED": 0xFFFF1F76,
                "PREVIOUS_DROP": 0xFFFF1E58,
                "DROP_COEFFICIENT": 0x000084A4,
            },
            "jk78c-ascd-main": {
                "REGION_ENTRY": 0x000FCBB0,
                "ASCD_FLAGS": 0xFFFF450B,
                "ASCD_MAIN_MASK": 0x10,
                "BUTTON_STATE": 0xFFFF29A1,
                "REGION_R12": 0xFFFF4506,
            },
            "jk00c-rpm-fuel-cut": {
                **fuel_cut,
                "REGION_ENTRY": 0x00050BF8,
                "FUEL_INHIBIT": 0xFFFF251F,
                "FUEL_CUT_TABLE": 0x000093E6,
                "DELAY_COUNTER": 0xFFFF2579,
                "PAIR_SELECTOR": 0xFFFF24EC,
                "CUT_CONFIG": 0x00008B6B,
                "CUT_DELAY": 0x00008C97,
            },
            "jk00d-rpm-fuel-cut": {
                **fuel_cut,
                "REGION_ENTRY": 0x00050BF4,
                "FUEL_INHIBIT": 0xFFFF2527,
                "FUEL_CUT_TABLE": 0x000093F4,
                "DELAY_COUNTER": 0xFFFF2581,
                "PAIR_SELECTOR": 0xFFFF24F4,
                "CUT_CONFIG": 0x00008B6C,
                "CUT_DELAY": 0x00008C99,
            },
        }
        expected.update({
            'jk08a-sid22-pointer-read': {'REGION_ENTRY': 0x0003235c, 'EARLY_ONLY': 0},
            'jk08a-knock-metric': {'REGION_ENTRY': 0x0004a2b6,
                'TOP_THREE_ENTRY': 0x00049d88, 'SCALER_ENTRY': 0x00049e96},
            'jk08a-knock-normalization': {'REGION_ENTRY': 0x0004a26a,
                'ALTERNATE_ENTRY': 0x0004a3b0},
            'jk08a-stft-publication': {'REGION_ENTRY': 0x0005ca08,
                'MODE_ALIAS': 0x7f40, 'FORCE_ALIAS': 0x7f50, 'EARLY_ONLY': 0},
            'jk08a-grid-selection': {'REGION_ENTRY': 0x0005796c, 'EARLY_ONLY': 0},
            'jk08a-grid-learning': {'REGION_ENTRY': 0x00057d1e, 'EARLY_ONLY': 0},
            'jk08a-closed-loop-conversion': {'REGION_ENTRY': 0x0003edb4, 'EARLY_ONLY': 0},
            'jk08a-closed-loop-adjustment': {'REGION_ENTRY': 0x000a0ee8, 'EARLY_ONLY': 0},
            'jk08a-closed-loop-feedback': {'REGION_ENTRY': 0x0005cbec},
            'jk08a-main-rpm-fuel-cut': {'REGION_ENTRY': 0x0004f282,
                'FUEL_INHIBIT': 0xffff2497, 'ENGINE_SPEED': 0xffff11bc,
                'PAIR_SELECTOR': 0xffff2468, 'DELAY_COUNTER': 0xffff24f1, 'EARLY_ONLY': 0},
            'jk08a-vehicle-speed-fuel-cut': {'REGION_ENTRY': 0x0004f19c,
                'STATE_FLAGS': 0xffff24a6, 'VEHICLE_SPEED': 0xffff110e,
                'CONTROL_FLAGS': 0xffff24a7, 'DELAY_COUNTER': 0xffff24f6, 'EARLY_ONLY': 0},
        })
        self.assertEqual(set(regions), set(expected))
        for key, region in regions.items():
            with self.subTest(region=key):
                image = STOCK_VERIFIER.stock_image(region.rom)
                self.assertEqual(
                    STOCK_VERIFIER.harness_defines(region, image),
                    expected[key],
                )
                harness = (
                    ROOT / "tools/sh-elf-run" / region.harness
                ).read_text(encoding="utf-8")
                cases = re.findall(r'\b\w+_cases\[\]\s*=\s*\{(.*?)\};', harness, re.S)
                if key == 'jk08a-can-latch-copy':
                    helper = STOCK_VERIFIER.can_latch_copy
                    descriptor = helper.proof.descriptor(ROOT)
                    header = (STOCK_VERIFIER.TOOL_DIR / 'can-latch-copy-cases.h').read_text()
                    self.assertEqual(header, helper.render_header(descriptor))
                    self.assertEqual(region.cases, len(helper.copy_matrix.cases(descriptor)))
                    self.assertIn('if (completed != ARRAY_SIZE(can_copy_cases)) return 1;', harness)
                    self.assertIn('if (completed != ARRAY_SIZE(can_copy_early_indices)) return 1;', harness)
                    self.assertIn('production=false', harness)
                elif key == 'jk08a-sid22-pointer-read':
                    helper = STOCK_VERIFIER.sid22_pointer_read
                    descriptor = helper.proof.descriptor(ROOT)
                    image = helper.image(ROOT)
                    header = (STOCK_VERIFIER.TOOL_DIR / 'sid22-pointer-read-cases.h').read_text()
                    self.assertEqual(header, helper.render_header(descriptor, image))
                    self.assertEqual(region.cases, len(helper.matrix.cases(descriptor, image)))
                    self.assertIn('count = EARLY_ONLY ? sizeof(sid22_early_indices)', harness)
                    self.assertIn(': sizeof(sid22_cases) / sizeof(sid22_cases[0])', harness)
                    self.assertIn('production=false', harness)
                elif key in ("jk08a-stft-publication", "jk08a-grid-selection", "jk08a-grid-learning", "jk08a-closed-loop-conversion", "jk08a-closed-loop-adjustment"):
                    scope = key.removeprefix("jk08a-")
                    header_name = "stock-jk08a-" + scope + "-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    macro = scope.replace("-", "_").upper() + "_CASE_COUNT"
                    if key == 'jk08a-closed-loop-conversion':
                        macro = 'CONVERSION_CASE_COUNT'
                    elif key == 'jk08a-closed-loop-adjustment':
                        macro = 'ADJUSTMENT_CASE_COUNT'
                    self.assertEqual(re.findall(r'^#define ' + macro + r' (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    [array] = re.findall(r'samples\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in array.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    self.assertTrue(all(re.fullmatch(r'[\s{},0-9a-fxU]+', row) for row in rows))
                    self.assertRegex(harness, r'count=EARLY_ONLY\?16U:' + macro)
                    self.assertRegex(harness, r'COUNT\(samples\)!=' + macro)
                    self.assertRegex(harness, r'for\(i=0;i<count;\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&samples\[i\]\)')
                elif key == 'jk08a-vehicle-speed-fuel-cut':
                    header_name = 'vehicle-fuel-cut-cases.h'
                    self.assertIn('#include "' + header_name + '"', harness)
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding='utf-8')
                    self.assertEqual(re.findall(r'^#define VEHICLE_FUEL_CUT_CASE_COUNT (\d+)U$', header,
                        re.MULTILINE), [str(region.cases)])
                    [array] = re.findall(r'\bvehicle_fuel_cut_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in array.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    self.assertTrue(all(re.fullmatch(r'[\s{},0-9a-fxU]+', row) for row in rows))
                    self.assertIn('limit=EARLY_ONLY?VEHICLE_FUEL_CUT_EARLY_COUNT:VEHICLE_FUEL_CUT_CASE_COUNT;', harness)
                    self.assertIn('for(index=0;index<limit;++index)', harness)
                    self.assertIn('if(!run_case(index,&vehicle_fuel_cut_cases[index]))return 1;', harness)
                elif key == 'jk08a-main-rpm-fuel-cut':
                    header_name = 'main-rpm-fuel-cut-cases.h'
                    self.assertIn('#include "' + header_name + '"', harness)
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding='utf-8')
                    self.assertEqual(re.findall(r'^#define MAIN_RPM_CASE_COUNT (\d+)U$', header,
                        re.MULTILINE), [str(region.cases)])
                    [array] = re.findall(r'\bmain_rpm_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in array.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    self.assertTrue(all(re.fullmatch(r'[\s{},0-9a-fxU]+', row) for row in rows))
                    self.assertIn('limit=EARLY_ONLY?MAIN_RPM_EARLY_COUNT:MAIN_RPM_CASE_COUNT;', harness)
                    self.assertIn('for(index=0;index<limit;++index)', harness)
                    self.assertIn('if(!run_case(index,&main_rpm_cases[index]))return 1;', harness)
                elif key == 'jk08a-closed-loop-feedback':
                    header_name = 'stock-jk08a-closed-loop-feedback-cases.h'
                    self.assertIn('#include "' + header_name + '"', harness)
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding='utf-8')
                    self.assertEqual(re.findall(r'^#define FEEDBACK_CASE_COUNT (\d+)U$', header,
                        re.MULTILINE), [str(region.cases)])
                    for name in ('memory_samples', 'cpu_samples'):
                        [array] = re.findall(r'\b' + name + r'\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                        rows = [line.strip() for line in array.splitlines() if line.strip()]
                        self.assertEqual(len(rows), region.cases)
                        self.assertTrue(all(re.fullmatch(r'[\s{},0-9a-fxU]+', row) for row in rows))
                    self.assertIn('COUNT(memory_samples)!=FEEDBACK_CASE_COUNT', harness)
                    self.assertIn('COUNT(cpu_samples)!=FEEDBACK_CASE_COUNT', harness)
                    self.assertIn('for(i=0;i<FEEDBACK_CASE_COUNT;++i)if(!run_case(i))return 1;', harness)
                elif key in ("jk08a-knock-metric", "jk08a-knock-normalization"):
                    scope = key.rsplit("-", 1)[1]
                    header_name = "stock-jk08a-knock-" + scope + "-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    macro = "KNOCK_" + scope.upper() + "_CASE_COUNT"
                    self.assertEqual(re.findall(r'^#define ' + macro + r' (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(scope + r'_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    self.assertTrue(all(re.fullmatch(r'[\s{},0-9a-fxU]+', row) for row in rows))
                    self.assertRegex(harness, r'for\(i=0;i<ARRAY_SIZE\(' + scope + r'_cases\);\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&' + scope + r'_cases\[i\]\)')
                    self.assertRegex(harness, r'\+\+completed;')
                    if scope == "metric":
                        self.assertRegex(harness, r'#define EARLY_ONLY 0')
                        self.assertRegex(harness, r'EARLY_ONLY\?ARRAY_SIZE\(early_indices\):' + macro)
                    else:
                        self.assertRegex(harness, r'if\(completed!=' + macro + r'\)')
                elif key == "jk08a-knock-reference-learning":
                    header_name = "stock-jk08a-knock-reference-learning-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define KNOCK_REFERENCE_LEARNING_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'reference_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = (
                        r'\{(?:\d+, ){9}0x[0-9a-f]+U, '
                        r'\{(?:\d+,){7}\d+\}, \{(?:\d+,){7}\d+\}, '
                        r'\{(?:\d+,){7}\d+\}, '
                        r'\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\}, [01]\},'
                    )
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\(i=0;i<ARRAY_SIZE\(reference_cases\);\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&reference_cases\[i\]\)')
                    self.assertRegex(harness, r'if\(completed!=KNOCK_REFERENCE_LEARNING_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-ltft-publication":
                    header_name = "stock-jk08a-ltft-publication-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define LTFT_PUBLICATION_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'ltft_publication_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = r'\{0x[0-9a-f]+U,\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},(?:\d+U,){4}-?\d+,(?:\d+U,){11}\d+U\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\(i=0;i<ARRAY_SIZE\(ltft_publication_cases\);\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&ltft_publication_cases\[i\]\)')
                    self.assertRegex(harness, r'if\(completed!=LTFT_PUBLICATION_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                    self.assertIn("#define DIAGNOSTIC (DIAGNOSTIC_RECORD + DIAGNOSTIC_BYTE1_OFFSET)", harness)
                elif key in ("jk08a-injection-pending", "jk08a-injection-reciprocal",
                             "jk08a-injection-tooth", "jk08a-injection-offset"):
                    scope = key.rsplit("-", 1)[1]
                    upper = scope.upper()
                    header_name = "injection-" + scope + "-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define ' + upper + r'_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(scope + r'_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    scalars = 6 if scope == "reciprocal" else 12 if scope == "tooth" else 8
                    literal_row = r'\{(?:0x[0-9a-f]+U,){' + str(scalars) + r'}\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\}\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define " + upper + "_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : " + upper + "_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(" + scope + "_cases) != " + upper + "_CASE_COUNT", harness)
                    self.assertIn("i < " + upper + "_ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i, " + scope + "_cases + i)", harness)
                    self.assertIn("completed != " + upper + "_ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-channel-pulse":
                    header_name = "channel-pulse-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define CHANNEL_PULSE_CASE_COUNT (\d+)U$', header, re.MULTILINE), [str(region.cases)])
                    [body] = re.findall(r'channel_pulse_cases\[\] = \{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in body.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    def array(count):
                        return r'\{(?:0x[0-9a-f]+U,){' + str(count-1) + r'}0x[0-9a-f]+U\}'
                    literal_row = r'\{(?:0x[0-9a-f]+U,){24}' + ','.join(array(n) for n in (15,15)) + r'\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : CHANNEL_PULSE_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(channel_pulse_cases)!=CHANNEL_PULSE_CASE_COUNT", harness)
                    self.assertIn("i<ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i,channel_pulse_cases+i)", harness)
                    self.assertIn("completed!=ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key in ('jk08a-opening-word', 'jk08a-pulse-selector', 'jk08a-full-programmer', 'jk08a-oneshot', 'jk08a-rpm-phase-word', 'jk08a-rpm-phase-byte', 'jk08a-rpm-phase-copy', 'jk08a-event-isr', 'jk08a-end-angle', 'jk08a-full-dispatch'):
                    from tools.kb.tests import test_connected_injection_chain as connected
                    connected.harness_contract(region,harness,STOCK_VERIFIER.TOOL_DIR)
                elif key in ('jk08a-base-accumulator', 'jk08a-transient-coefficient', 'jk08a-transient-additive', 'jk08a-coolant-conditional', 'jk08a-transient-pair-1', 'jk08a-transient-pair-2', 'jk08a-fuel-multiplier', 'jk08a-pulse-precursor', 'jk08a-common-gain', 'jk08a-enrichment-prefix', 'jk08a-enrichment-terminal'):
                    from tools.kb.tests import test_fuel_upstream_chain as upstream
                    upstream.harness_contract(region,harness,STOCK_VERIFIER.TOOL_DIR)
                elif key == "jk08a-injection-prologue":
                    header_name = "injection-prologue-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define PROLOGUE_CASE_COUNT (\d+)U$', header, re.MULTILINE), [str(region.cases)])
                    [body] = re.findall(r'prologue_cases\[\] = \{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in body.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    def array(count):
                        return r'\{(?:0x[0-9a-f]+U,){' + str(count-1) + r'}0x[0-9a-f]+U\}'
                    literal_row = r'\{(?:0x[0-9a-f]+U,){3}' + ','.join(array(n) for n in (15,15)) + r'\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define PROLOGUE_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : PROLOGUE_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(prologue_cases) != PROLOGUE_CASE_COUNT", harness)
                    self.assertIn("i < PROLOGUE_ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i, prologue_cases + i)", harness)
                    self.assertIn("completed != PROLOGUE_ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-injection-count":
                    header_name = "injection-count-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define COUNT_CASE_COUNT (\d+)U$', header, re.MULTILINE), [str(region.cases)])
                    [body] = re.findall(r'count_cases\[\] = \{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in body.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    def array(count):
                        return r'\{(?:0x[0-9a-f]+U,){' + str(count-1) + r'}0x[0-9a-f]+U\}'
                    literal_row = r'\{(?:0x[0-9a-f]+U,){9}' + ','.join(array(n) for n in (15,15,4)) + r'\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define COUNT_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : COUNT_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(count_cases) != COUNT_CASE_COUNT", harness)
                    self.assertIn("i < COUNT_ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i, count_cases + i)", harness)
                    self.assertIn("completed != COUNT_ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-injection-dispatch":
                    header_name = "injection-dispatch-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define DISPATCH_CASE_COUNT (\d+)U$', header, re.MULTILINE), [str(region.cases)])
                    [body] = re.findall(r'dispatch_cases\[\] = \{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in body.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    def array(count):
                        return r'\{(?:0x[0-9a-f]+U,){' + str(count-1) + r'}0x[0-9a-f]+U\}'
                    literal_row = r'\{(?:0x[0-9a-f]+U,){9}' + ','.join(array(n) for n in (15,15)) + r'\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define DISPATCH_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : DISPATCH_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(dispatch_cases) != DISPATCH_CASE_COUNT", harness)
                    self.assertIn("i < DISPATCH_ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i, dispatch_cases + i)", harness)
                    self.assertIn("completed != DISPATCH_ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-injection-catchup":
                    header_name = "injection-catchup-cases.h"
                    self.assertEqual(re.findall(r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(r'^#define CATCHUP_CASE_COUNT (\d+)U$', header, re.MULTILINE), [str(region.cases)])
                    [body] = re.findall(r'catchup_cases\[\] = \{(.*?)\n\};', header, re.S)
                    rows = [line.strip() for line in body.splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    def array(count):
                        return r'\{(?:0x[0-9a-f]+U,){' + str(count-1) + r'}0x[0-9a-f]+U\}'
                    literal_row = r'\{(?:0x[0-9a-f]+U,){7}' + ','.join(array(n) for n in (4,4,15,15)) + r'\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertIn("#define CATCHUP_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : CATCHUP_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(catchup_cases) != CATCHUP_CASE_COUNT", harness)
                    self.assertIn("i < CATCHUP_ACTIVE_CASE_COUNT", harness)
                    self.assertIn("run_case(i, catchup_cases + i)", harness)
                    self.assertIn("completed != CATCHUP_ACTIVE_CASE_COUNT", harness)
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-injection-slot":
                    header_name = "injection-slot-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define SLOT_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'slot_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = r'\{(?:0x[0-9a-f]+U,){11}\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\}\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\s*\(i = 0; i < SLOT_ACTIVE_CASE_COUNT; \+\+i\)')
                    self.assertRegex(harness, r'run_case\(i, slot_cases \+ i\)')
                    self.assertRegex(harness, r'if\s*\(completed != SLOT_ACTIVE_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                    self.assertIn("#define SLOT_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : SLOT_CASE_COUNT)", harness)
                    self.assertIn("ARRAY_SIZE(slot_cases) != SLOT_CASE_COUNT", harness)
                elif key == "jk08a-injection-snapshot":
                    header_name = "injection-snapshot-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define SNAPSHOT_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'snapshot_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = r'\{(?:0x[0-9a-f]+U,){11}\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\}\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\s*\(i = 0; i < ARRAY_SIZE\(snapshot_cases\); \+\+i\)')
                    self.assertRegex(harness, r'run_case\(i, snapshot_cases \+ i\)')
                    self.assertRegex(harness, r'if\s*\(completed != SNAPSHOT_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-injection-start-delay":
                    header_name = "stock-jk08a-injection-start-delay-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define INJECTION_START_DELAY_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'injection_start_delay_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = r'\{\{0x[0-9a-f]+U,0x[0-9a-f]+U\},\{(?:0x[0-9a-f]+U,){5}0x[0-9a-f]+U\},\d+,\d+,\{(?:0x[0-9a-f]+U,){2}0x[0-9a-f]+U\},(?:\d+,){5}(?:0x[0-9a-f]+U,){8}\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},0x[0-9a-f]+U,\d+\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\(i=0;i<ARRAY_SIZE\(injection_start_delay_cases\);\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&injection_start_delay_cases\[i\]\)')
                    self.assertRegex(harness, r'if\(completed!=INJECTION_START_DELAY_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                elif key == "jk08a-bank-base-pulse":
                    header_name = "stock-jk08a-bank-base-pulse-cases.h"
                    self.assertEqual(re.findall(
                        r'^#include "' + re.escape(header_name) + r'"$',
                        harness, re.MULTILINE), ['#include "' + header_name + '"'])
                    header = (STOCK_VERIFIER.TOOL_DIR / header_name).read_text(encoding="utf-8")
                    self.assertEqual(re.findall(
                        r'^#define BANK_BASE_PULSE_CASE_COUNT (\d+)U$',
                        header, re.MULTILINE), [str(region.cases)])
                    arrays = re.findall(r'bank_base_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
                    self.assertEqual(len(arrays), 1)
                    rows = [line.strip() for line in arrays[0].splitlines() if line.strip()]
                    self.assertEqual(len(rows), region.cases)
                    literal_row = r'\{0x[0-9a-f]+U,\{(?:0x[0-9a-f]+U,){14}0x[0-9a-f]+U\},(?:\d+U,){14}\d+U\},'
                    self.assertTrue(all(re.fullmatch(literal_row, row) for row in rows))
                    self.assertRegex(harness, r'for\(i=0;i<ARRAY_SIZE\(bank_base_cases\);\+\+i\)')
                    self.assertRegex(harness, r'run_case\(i,&bank_base_cases\[i\]\)')
                    self.assertRegex(harness, r'if\(completed!=BANK_BASE_PULSE_CASE_COUNT\)')
                    self.assertRegex(harness, r'\+\+completed;')
                elif key not in ("jk08a-maf-scaling", "jk08a-maf-compensation", "jk08a-maf-filter",
                               "jk08a-maf-contribution", "jk08a-fuel-compensation", "jk08a-bfs-rate",
                               "jk08a-knock-threshold", "jk08a-knock-comparison",
                               "jk08a-knock-timing-byte", "jk08a-knock-integration",
                               "jk08a-knock-event-retard", "jk08a-knock-event-publication",
                               "jk08a-knock-state-selection"):
                    self.assertEqual(sum(array.count('{"') for array in cases), region.cases)
                # Vector tables and harness loops execute additional entries.
                # The executable gate binds their emitted invocation count.
        region = regions["jk78c-ascd-main"]
        image = STOCK_VERIFIER.stock_image(region.rom)
        with self.assertRaisesRegex(
            STOCK_VERIFIER.VerificationError, "no MOV.L"
        ):
            STOCK_VERIFIER.base_register(
                region, image[:region.base_load] + b"\x00\x09"
                + image[region.base_load + 2:]
            )

    def test_published_stock_slice_instruction_counts_match_the_executed_regions(self):
        readme = (ROOT / "tools/sh-elf-run/README.md").read_text(encoding="utf-8")
        regions = {region.key: region for region in STOCK_VERIFIER.REGIONS}
        for key, pattern in (
            ("jk08a-maf-aggregate", r"combined-MAF fixture reconstructs the complete (\d+)-instruction sum"),
            ("jk08a-load-normalization", r"Q7 load fixture reconstructs the (\d+)-instruction normalization slice"),
        ):
            with self.subTest(region=key):
                match = re.search(pattern, readme)
                self.assertIsNotNone(match)
                region = regions[key]
                self.assertEqual(int(match.group(1)), (region.end - region.start) // 2)

    def test_published_maf_contribution_instruction_count_matches_all_executed_spans(self):
        readme = (ROOT / "tools/sh-elf-run/README.md").read_text(encoding="utf-8")
        match = re.search(r"per-bank contribution fixture reconstructs (\d+) instructions", readme)
        self.assertIsNotNone(match)
        region = next(item for item in STOCK_VERIFIER.REGIONS if item.key == "jk08a-maf-contribution")
        self.assertEqual(int(match.group(1)), sum((end-start)//2 for start,end in region.code_spans))

    def test_published_primary_bfs_instruction_and_byte_counts_match_bound_spans(self):
        readme = (ROOT / "tools/sh-elf-run/README.md").read_text(encoding="utf-8")
        match = re.search(r"primary BFS fixture reconstructs (\d+) instructions", readme)
        self.assertIsNotNone(match)
        region = next(item for item in STOCK_VERIFIER.REGIONS if item.key == "jk08a-bfs-base")
        self.assertEqual(int(match.group(1)), sum((end - start) // 2 for start, end in region.code_spans))
        bound = re.search(r"GNU assembly\s+binds (\d+) bytes", readme)
        self.assertIsNotNone(bound)
        self.assertEqual(int(bound.group(1)), sum(end - start for start, end in region.code_spans)
                         + sum(size for _, size in region.pools))
        static = (ROOT / "tools/kb/tests/test_airflow_bfs_base.py").read_text(encoding="utf-8")
        spans = re.findall(r"\(0x([0-9a-f]+), 0x([0-9a-f]+), '[0-9a-f]{64}'\)", static)
        bound_static = re.search(r"for (\d+) bytes in total", readme)
        self.assertIsNotNone(bound_static)
        self.assertEqual(int(bound_static.group(1)),
                         sum(int(end, 16) - int(start, 16) for start, end in spans))

    def test_a_calling_slice_restores_pr_only_at_its_simulator_boundary(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-tooth-fallback")
        image = STOCK_VERIFIER.stock_image(region.rom)
        fixture = STOCK_VERIFIER.build_fixture(region, image)
        self.assertEqual(fixture[region.end:region.end + 8], bytes.fromhex("55f2452a000b0009"))
        for start, end in region.code_spans:
            self.assertEqual(fixture[start:end], image[start:end])
        for invalid in (True, -4, 2, 64, "8"):
            with self.subTest(offset=invalid), self.assertRaisesRegex(
                    STOCK_VERIFIER.VerificationError, "return address offset"):
                STOCK_VERIFIER.build_fixture(replace(region, return_address_offset=invalid), image)
        with self.assertRaisesRegex(STOCK_VERIFIER.VerificationError, "natural stock return"):
            STOCK_VERIFIER.build_fixture(replace(region, boundary=False), image)
        with self.assertRaisesRegex(STOCK_VERIFIER.VerificationError, "overlaps a pool"):
            STOCK_VERIFIER.build_fixture(
                replace(region, pools=(*region.pools, (region.end, 4))), image)

    def test_published_bfs_limiting_counts_match_executed_and_statically_bound_spans(self):
        readme = (ROOT / "tools/sh-elf-run/README.md").read_text(encoding="utf-8")
        section = readme.split("The BFS limiting fixture", 1)[1].split("The Q7 load fixture", 1)[0]
        region = next(item for item in STOCK_VERIFIER.REGIONS if item.key == "jk08a-bfs-limit")
        count = re.search(r"reconstructs (\d+) instructions", section)
        self.assertIsNotNone(count)
        self.assertEqual(int(count.group(1)), sum((end-start)//2 for start,end in region.code_spans))
        bound = re.search(r"GNU assembly\s+binds (\d+) bytes", section)
        self.assertIsNotNone(bound)
        self.assertEqual(int(bound.group(1)), sum(end-start for start,end in region.code_spans)
                         + sum(size for _,size in region.pools))
        static = (ROOT / "tools/kb/tests/test_airflow_bfs_limit.py").read_text(encoding="utf-8")
        spans = re.findall(r"\(0x([0-9a-f]+), 0x([0-9a-f]+), '[0-9a-f]{64}'\)", static)
        bound_static = re.search(r"static test binds (\d+) bytes", section)
        self.assertIsNotNone(bound_static)
        self.assertEqual(int(bound_static.group(1)),
                         sum(int(end,16)-int(start,16) for start,end in spans))

    def test_a_stock_boundary_preserves_the_cached_word_with_a_declared_scratch_register(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-tooth-fallback")
        image = STOCK_VERIFIER.stock_image(region.rom)
        changed = replace(region, return_address_offset=24, return_register=1)
        fixture = STOCK_VERIFIER.build_fixture(changed, image)
        self.assertEqual(fixture[region.end:region.end + 8], bytes.fromhex("51f6412a000b0009"))
        for start, end in region.code_spans:
            self.assertEqual(fixture[start:end], image[start:end])
        for invalid in (True, 0, 15, -1, "1"):
            with self.subTest(register=invalid), self.assertRaisesRegex(
                    STOCK_VERIFIER.VerificationError, "return register"):
                STOCK_VERIFIER.build_fixture(replace(changed, return_register=invalid), image)

    def test_stock_execution_rejects_decimal_prefixes_and_modified_pass_lines(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-fuel-compensation")
        marker = f"VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases={region.cases}"
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)
            for output in (marker + "0\n", "prefix " + marker + "\n", marker + " suffix\n"):
                with self.subTest(output=output), \
                        patch.object(STOCK_VERIFIER, "stock_image", return_value=b"\x00" * 4), \
                        patch.object(STOCK_VERIFIER, "require_reconstruction", return_value=301), \
                        patch.object(STOCK_VERIFIER, "build_fixture", return_value=b"\x00" * 4), \
                        patch.object(STOCK_VERIFIER, "harness_defines", return_value={}), \
                        patch.object(STOCK_VERIFIER, "require_separate_storage", return_value={}), \
                        patch.object(STOCK_VERIFIER.base_verifier, "run_command",
                                     return_value=SimpleNamespace(stdout=output)), \
                        self.assertRaisesRegex(STOCK_VERIFIER.VerificationError, "exact PASS marker"):
                    STOCK_VERIFIER.run_region(region, build / "invoke.o", build)
            with patch.object(STOCK_VERIFIER, "stock_image", return_value=b"\x00" * 4), \
                    patch.object(STOCK_VERIFIER, "require_reconstruction", return_value=301), \
                    patch.object(STOCK_VERIFIER, "build_fixture", return_value=b"\x00" * 4), \
                    patch.object(STOCK_VERIFIER, "harness_defines", return_value={}), \
                        patch.object(STOCK_VERIFIER, "require_separate_storage", return_value={}), \
                    patch.object(STOCK_VERIFIER.base_verifier, "run_command",
                                 return_value=SimpleNamespace(stdout="diagnostic\n" + marker + "\n")):
                self.assertEqual(STOCK_VERIFIER.run_region(region, build / "invoke.o", build), 301)

    def test_fuel_cut_regions_address_the_symbols_through_their_pools(self):
        # The state machine points GBR at its first pool word and stores the
        # state byte at GBR + 0x4f and the delay counter at GBR + 0xa9, reads
        # the selector at GBR + 0x1c and the engine speed at 0x22 past the
        # word of its single pool, and loads the configuration byte, the
        # table, and the delay byte through the other three words.
        for region in STOCK_VERIFIER.REGIONS:
            if not region.key.endswith("-rpm-fuel-cut"):
                continue
            with self.subTest(region=region.key):
                image = STOCK_VERIFIER.stock_image(region.rom)
                defines = STOCK_VERIFIER.harness_defines(region, image)
                def word(address):
                    return int.from_bytes(image[address:address + 4], "big")

                if region.key == 'jk08a-main-rpm-fuel-cut':
                    self.assertEqual(region.pools, ((0x4f460,20),(0x8b38,1),(0x8c69,1),(0x934e,12)))
                    self.assertEqual(region.ram_literals, (0x4f460,0x4f46c))
                    gbr = word(0x4f460)
                    self.assertEqual(defines['FUEL_INHIBIT'], gbr+0x4b)
                    self.assertEqual(defines['DELAY_COUNTER'], gbr+0xa5)
                    self.assertEqual(defines['PAIR_SELECTOR'], gbr+0x1c)
                    self.assertEqual(defines['ENGINE_SPEED'], word(0x4f46c)+0x20)
                    self.assertEqual([word(at) for at in (0x4f464,0x4f468,0x4f470)], [0x8b38,0x934e,0x8c69])
                    continue
                (speed, _), (pool, _) = region.pools
                gbr = word(pool)
                self.assertEqual(defines["FUEL_INHIBIT"], gbr + 0x4F)
                self.assertEqual(defines["DELAY_COUNTER"], gbr + 0xA9)
                self.assertEqual(defines["PAIR_SELECTOR"], gbr + 0x1C)
                self.assertEqual(defines["ENGINE_SPEED"], word(speed) + 0x22)
                self.assertEqual(defines["CUT_CONFIG"], word(pool + 4))
                self.assertEqual(defines["FUEL_CUT_TABLE"], word(pool + 8))
                self.assertEqual(defines["CUT_DELAY"], word(pool + 12))

    def test_rpm_drop_region_binds_its_inputs_and_non_rising_boundary(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-rpm-drop-arithmetic")
        image = STOCK_VERIFIER.stock_image(region.rom)
        defines = STOCK_VERIFIER.harness_defines(region, image)
        speed_base = int.from_bytes(image[0x3E3CC:0x3E3D0], "big")
        coefficient = int.from_bytes(image[0x3E3DC:0x3E3E0], "big")
        self.assertEqual(defines["CURRENT_SPEED"], speed_base + 0x36)
        self.assertEqual(defines["HISTORY_SPEED"], defines["DROP_WORD"] + 0x126)
        self.assertEqual(defines["PREVIOUS_DROP"], defines["DROP_WORD"] + 8)
        self.assertEqual(defines["DROP_COEFFICIENT"], coefficient + 1)
        self.assertEqual(image[region.end - 4:region.end], bytes.fromhex("e000c100"))

    def test_two_byte_stock_entry_preserves_pc_relative_pool_alignment(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-rpm-drop-arithmetic")
        image = STOCK_VERIFIER.stock_image(region.rom)
        origin = region.start & ~3
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)

            def reconstruct(command):
                calls.append(command)
                if command[0] == VERIFIER.OBJCOPY:
                    Path(command[-1]).write_bytes(image[origin:])

            with patch.object(STOCK_VERIFIER.base_verifier, "run_command", reconstruct):
                self.assertEqual(STOCK_VERIFIER.require_reconstruction(region, image, build), 55)
            self.assertIn("-Ttext=0x3e1fc", calls[1])
            self.assertIn("--entry=0x3e1fe", calls[1])

            for address in (region.start, 0x3E20C, 0x3E3CC, 0x3E3DC):
                changed = bytearray(image)
                changed[address] ^= 1

                def mismatched(command):
                    if command[0] == VERIFIER.OBJCOPY:
                        Path(command[-1]).write_bytes(changed[origin:])

                with self.subTest(address=address), patch.object(
                    STOCK_VERIFIER.base_verifier, "run_command", mismatched
                ), self.assertRaisesRegex(STOCK_VERIFIER.VerificationError, "differs"):
                    STOCK_VERIFIER.require_reconstruction(region, image, build)

    def test_rpm_producer_and_divider_share_an_exact_reconstruction(self):
        region = next(item for item in STOCK_VERIFIER.REGIONS
                      if item.key == "jk08a-rpm-division")
        image = STOCK_VERIFIER.stock_image(region.rom)
        origin = 0x21CE0
        calls = []
        self.assertEqual(region.code_spans, ((0x38272, 0x3829E), (0x21CE0, 0x21DC6)))
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)

            def reconstruct(command):
                calls.append(command)
                if command[0] == VERIFIER.OBJCOPY:
                    Path(command[-1]).write_bytes(image[origin:])

            with patch.object(STOCK_VERIFIER.base_verifier, "run_command", reconstruct):
                self.assertEqual(STOCK_VERIFIER.require_reconstruction(region, image, build), 137)
            self.assertIn("-Ttext=0x21ce0", calls[1])
            for address in (0x38282, 0x21CE4, 0x21D80, 0x21DC8, 0x3837C):
                changed = bytearray(image)
                changed[address] ^= 1

                def mismatched(command):
                    if command[0] == VERIFIER.OBJCOPY:
                        Path(command[-1]).write_bytes(changed[origin:])

                with self.subTest(address=address), patch.object(
                    STOCK_VERIFIER.base_verifier, "run_command", mismatched
                ), self.assertRaisesRegex(STOCK_VERIFIER.VerificationError, "differs"):
                    STOCK_VERIFIER.require_reconstruction(region, image, build)

    def test_top_level_gate_registers_stock_code(self):
        source = MODULE_PATH.read_text(encoding="utf-8")

        self.assertIn("verify_stock_code.verify", source)
        self.assertIn("stock_code_cases", source)

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

    def test_case_counts_are_read_from_the_harness_markers(self):
        cases = TELEMETRY_VERIFIER.marker_cases(
            TELEMETRY_VERIFIER.REQUIRED_DYNAMIC_MARKER
        )
        published = " ".join(
            (ROOT / "patches/can-telemetry.md").read_text(encoding="utf-8").split()
        )

        self.assertEqual(cases, 80)
        self.assertIn(
            f"eleven executable entries and {cases} dynamic telemetry cases",
            published,
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
        self.assertIn(
            f'"VQ_SH_ELF_CAN_TELEMETRY status=PASS cases={cases} entries=11 "',
            runtime_source,
        )


if __name__ == "__main__":
    unittest.main()
