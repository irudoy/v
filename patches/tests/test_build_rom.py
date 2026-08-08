import ast
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from patches import build_rom
from patches import jk08a_checksums as checksums
from patches import map_switching_layout
from patches import rolling_launch


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


def profile_text(**overrides):
    values = {
        "mode": '"rpm_hold_retard"',
        "enabled_maps": "[1, 3]",
        "coolant_min": "10",
        "coolant_max": "220",
        "min_speed": "2",
        "retard_ramp_native": "12",
        "min_rpm_native": "160",
        "min_pedal": "3",
        "rpm_offset_native": "16",
        "min_hysteresis_native": "4",
        "max_hysteresis_native": "12",
        "hysteresis_ratio_tenths": "20",
        "run_timeout_ticks": "300",
        "rearm_ticks": "100",
        "target_commands": "[115, 114, 113, 112, 111]",
    }
    values.update(overrides)
    body = "\n".join(f"{key} = {value}" for key, value in values.items())
    return (
        "schema_version = 2\n"
        'rom = "JK08A"\n'
        'name = "mode-2-test"\n\n'
        "[rolling_launch]\n"
        f"{body}\n"
    )


class BuildRomTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = STOCK.read_bytes()
        cls.map_layout = map_switching_layout.load_layout()
        cls.base_result = build_rom.build_image(
            cls.stock, source_name="exact stock"
        )

        migrated = bytearray(cls.base_result.data)
        migrated[0x8725] ^= 0x01
        for family_index, family in enumerate(cls.map_layout.families):
            for slot_index, address in enumerate(family.copies):
                migrated[address] ^= 1 + family_index + slot_index
        cls.migration_source = bytes(checksums.recalculate(migrated))
        cls.saved_copies = build_rom._capture_map_copies(
            cls.migration_source, cls.map_layout
        )

    def test_auto_and_explicit_selection_build_identical_jk08a(self):
        explicit = build_rom.build_image(
            self.stock, rom="jk08a", source_name="explicit stock"
        )
        self.assertEqual(self.base_result.rom, "JK08A")
        self.assertEqual(self.base_result.detection, "auto")
        self.assertEqual(explicit.detection, "explicit")
        self.assertEqual(explicit.data, self.base_result.data)

    def test_auto_detection_does_not_use_filename(self):
        selected, detection = build_rom.select_rom(
            self.stock, build_rom.AUTO_ROM
        )
        self.assertEqual((selected, detection), ("JK08A", "auto"))

    def test_unknown_and_unsupported_series_are_rejected(self):
        wrong_identity = bytearray(self.stock)
        wrong_identity[
            map_switching_layout.COMPATIBLE_IDENTITY_START
        ] ^= 1
        with self.assertRaisesRegex(
            build_rom.BuildError, "could not be detected"
        ):
            build_rom.select_rom(wrong_identity)
        with self.assertRaisesRegex(
            build_rom.BuildError, "unsupported ROM series"
        ):
            build_rom.select_rom(self.stock, "JK03A")

    def test_explicit_series_still_requires_matching_identity(self):
        wrong_identity = bytearray(self.stock)
        wrong_identity[
            map_switching_layout.COMPATIBLE_IDENTITY_START
        ] ^= 1
        wrong_identity = checksums.recalculate(wrong_identity)
        with self.assertRaisesRegex(build_rom.BuildError, "identity"):
            build_rom.build_image(wrong_identity, rom="JK08A")

    def test_complete_output_is_checksum_valid_and_closed(self):
        result = self.base_result
        self.assertTrue(checksums.verify(result.data).valid)
        map_layout = map_switching_layout.load_layout()
        launch_layout = build_rom.rolling_launch_layout.load_layout()
        permitted = build_rom._component_offsets(
            map_layout, launch_layout
        ) | set(checksums.checksum_byte_offsets())
        changed = {
            offset
            for offset, (before, after) in enumerate(
                zip(self.stock, result.data)
            )
            if before != after
        }
        self.assertEqual(changed - permitted, set())
        self.assertEqual(result.changed_bytes, len(changed))
        self.assertEqual(result.permitted_write_bytes, len(permitted))

    def test_complete_runtime_can_be_rebuilt_idempotently(self):
        rebuilt = build_rom.build_image(
            self.base_result.data, source_name="complete current output"
        )
        self.assertEqual(
            rebuilt.input_state, "complete-runtime-migration"
        )
        self.assertEqual(rebuilt.data, self.base_result.data)
        self.assertEqual(rebuilt.changed_bytes, 0)

        map_only = bytearray(self.base_result.data)
        launch_layout = build_rom.rolling_launch_layout.load_layout()
        for span in launch_layout.claimed_rom_ranges:
            map_only[span.start : span.end] = bytes([0xFF]) * span.size
        for hook in launch_layout.hooks:
            map_only[hook.address : hook.address + hook.width] = (
                hook.stock.to_bytes(hook.width, launch_layout.byte_order)
            )
        for diagnostic in launch_layout.diagnostics:
            map_only[
                diagnostic.pointer_address : diagnostic.pointer_address + 4
            ] = diagnostic.stock.to_bytes(4, launch_layout.byte_order)
        map_only = checksums.recalculate(map_only)
        rebuilt_map_only = build_rom.build_image(
            map_only, source_name="complete map-switching endpoint"
        )
        self.assertEqual(rebuilt_map_only.data, self.base_result.data)

    def test_migration_preserves_lower_configuration_and_all_map_copies(self):
        result = build_rom.build_image(
            self.migration_source,
            rom="JK08A",
            source_name="current complete runtime",
        )
        self.assertEqual(
            result.input_state, "complete-runtime-migration"
        )
        self.assertEqual(result.data[0x8725], self.migration_source[0x8725])
        self.assertEqual(
            build_rom._capture_map_copies(result.data, self.map_layout),
            self.saved_copies,
        )
        self.assertGreater(result.preserved_map_copy_bytes, 0)
        self.assertTrue(checksums.verify(result.data).valid)

    def test_registered_historical_endpoint_can_be_migrated(self):
        historical = bytearray(self.base_result.data)
        historical[0xD3900] ^= 0x01
        layout = build_rom.rolling_launch_layout.load_layout()
        controller = layout.assembly_unit_by_key["ignition_controller"]
        historical[controller.span.start : controller.span.end] = (
            bytes([0xFF]) * controller.span.size
        )
        historical[0xD3F60 : 0xD3F80] = bytes.fromhex(
            "524c0101050000ff010000a00001001000"
            "04012c0064737373737300adb3a55a"
        )
        historical = checksums.recalculate(historical)
        signature = build_rom.RollingEndpointSignature(
            key="test-schema-1-endpoint",
            configuration_schema_version=1,
            unit_sha256=tuple(
                (
                    unit.key,
                    build_rom.sha256(
                        historical[unit.span.start : unit.span.end]
                    ),
                )
                for unit in layout.assembly_units
            ),
        )
        with mock.patch.object(
            build_rom, "HISTORICAL_ROLLING_ENDPOINTS", (signature,)
        ):
            result = build_rom.build_image(
                historical, source_name="registered schema-1 runtime"
            )
        self.assertEqual(
            result.input_state, "complete-runtime-migration"
        )
        self.assertEqual(
            result.configuration,
            build_rom.builtin_profile().calibration.to_bytes(),
        )

    def test_partial_and_unknown_rolling_states_are_rejected(self):
        layout = build_rom.rolling_launch_layout.load_layout()
        cases = {}

        unknown_payload = bytearray(self.base_result.data)
        unknown_payload[0xD3900] ^= 0x01
        cases["unknown-payload"] = unknown_payload

        partial_hook = bytearray(self.base_result.data)
        hook = layout.hooks[0]
        partial_hook[hook.address : hook.address + hook.width] = (
            hook.stock.to_bytes(hook.width, layout.byte_order)
        )
        cases["partial-hook"] = partial_hook

        partial_did = bytearray(self.base_result.data)
        diagnostic = layout.diagnostics[0]
        partial_did[
            diagnostic.pointer_address : diagnostic.pointer_address + 4
        ] = diagnostic.stock.to_bytes(4, layout.byte_order)
        cases["partial-did"] = partial_did

        invalid_configuration = bytearray(self.base_result.data)
        invalid_configuration[layout.configuration.start + 9] = 0
        cases["framed-invalid-configuration"] = invalid_configuration

        mixed_schema = bytearray(self.base_result.data)
        mixed_schema[layout.configuration.start : layout.configuration.end] = (
            bytes.fromhex(
                "524c0101050000ff010000a00001001000"
                "04012c0064737373737300adb3a55a"
            )
        )
        cases["current-payload-schema-1"] = mixed_schema

        for name, source in cases.items():
            with self.subTest(name=name):
                source = checksums.recalculate(source)
                with self.assertRaisesRegex(
                    build_rom.BuildError,
                    "partial or unknown Rolling Launch state",
                ):
                    build_rom.build_image(source, source_name=name)

    def test_partial_map_pointer_state_is_rejected(self):
        partial = bytearray(self.base_result.data)
        family = self.map_layout.families[0]
        partial[family.pointer_table] ^= 1
        partial = checksums.recalculate(partial)
        with self.assertRaisesRegex(build_rom.BuildError, "pointer table"):
            build_rom.build_image(partial)

    def test_unknown_upper_rom_change_is_rejected(self):
        corrupt = bytearray(self.base_result.data)
        corrupt[0x30000] ^= 1
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            build_rom.BuildError, "protected upper ROM differs"
        ):
            build_rom.build_image(corrupt)

    def test_invalid_input_checksum_is_rejected(self):
        corrupt = bytearray(self.stock)
        corrupt[0x9000] ^= 1
        with self.assertRaisesRegex(build_rom.BuildError, "checksum mismatch"):
            build_rom.build_image(corrupt)

    def test_strict_profile_enables_independent_retard_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.toml"
            path.write_text(profile_text(), encoding="utf-8")
            profile = build_rom.load_profile(path)
        self.assertEqual(
            profile.calibration.mode,
            rolling_launch.Mode.RPM_HOLD_RETARD,
        )
        self.assertEqual(profile.calibration.enable_mask, 0x05)
        self.assertEqual(
            profile.calibration.target_commands,
            (115, 114, 113, 112, 111),
        )
        result = build_rom.build_image(self.stock, profile=profile)
        self.assertEqual(
            result.configuration, profile.calibration.to_bytes()
        )

    def test_profile_accepts_zero_minimum_speed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.toml"
            path.write_text(
                profile_text(min_speed="0"), encoding="utf-8"
            )
            profile = build_rom.load_profile(path)
        self.assertEqual(profile.calibration.min_speed, 0)
        result = build_rom.build_image(self.stock, profile=profile)
        self.assertEqual(
            result.configuration, profile.calibration.to_bytes()
        )

    def test_profile_rom_must_match_selected_series(self):
        profile = replace(build_rom.builtin_profile(), rom="JK03A")
        with self.assertRaisesRegex(build_rom.BuildError, "does not match"):
            build_rom.build_image(self.stock, profile=profile)

    def test_profile_rejects_extra_fields_and_invalid_calibration(self):
        with tempfile.TemporaryDirectory() as directory:
            extra = Path(directory) / "extra.toml"
            extra.write_text(
                profile_text() + "unexpected = 1\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(build_rom.BuildError, "fields differ"):
                build_rom.load_profile(extra)

            invalid = Path(directory) / "invalid.toml"
            invalid.write_text(
                profile_text(max_hysteresis_native="16"), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                build_rom.BuildError, "calibration is invalid"
            ):
                build_rom.load_profile(invalid)

    def test_artifact_set_is_complete_idempotent_and_non_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "source.bin"
            output_path = Path(directory) / "result.bin"
            input_path.write_bytes(self.stock)
            created = build_rom.write_artifacts(
                self.base_result, input_path, output_path
            )
            self.assertEqual(len(created), 4)
            self.assertEqual(
                build_rom.write_artifacts(
                    self.base_result, input_path, output_path
                ),
                (),
            )
            self.assertEqual(output_path.read_bytes(), self.base_result.data)
            manifest_path = Path(f"{output_path}.manifest.json")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["rom"], "JK08A")
            self.assertEqual(
                manifest["output"]["hardware_status"], "UNTESTED"
            )
            self.assertEqual(
                manifest["output"]["sha256"],
                self.base_result.output_sha256,
            )

            Path(f"{output_path}.sha256").write_text(
                "different\n", encoding="ascii"
            )
            with self.assertRaisesRegex(
                build_rom.BuildError, "artifact differs"
            ):
                build_rom.write_artifacts(
                    self.base_result, input_path, output_path
                )

    def test_production_entry_point_imports_no_historical_overlay_builder(self):
        source = (ROOT / "patches" / "build_rom.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.extend(alias.name for alias in node.names)
        self.assertFalse(
            any(name.startswith("build_map_switching_") for name in imports)
        )

    def test_default_output_path_is_adjacent_and_non_destructive(self):
        self.assertEqual(
            build_rom.default_output_path(Path("/tmp/input.bin")),
            Path("/tmp/input-complete.bin"),
        )


if __name__ == "__main__":
    unittest.main()
