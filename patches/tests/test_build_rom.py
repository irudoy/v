import ast
import contextlib
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import pytest

from patches import build_rom
from patches import jk08a_checksums as checksums
from patches import map_switching_layout
from patches import can_telemetry
from patches import rom_checksums
from patches import rolling_launch
from patches import rolling_launch_layout
from patches import runtime_targets
from tools import rom_homology


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


def profile_text(*, telemetry=None, **overrides):
    values = {
        "mode": '"hold"',
        "enabled_maps": "[1, 3]",
        "coolant_min": "10",
        "coolant_max": "220",
        "min_speed": "200",
        "max_speed": "1200",
        "min_rpm_native": "160",
        "min_pedal": "3",
        "target_speed_offset": "-20",
        "window_width": "40",
        "window_top": "20",
        "u_rate_limit": "50",
        "integral_gain": "3",
        "launch_rpm_native": "400",
        "launch_speed_threshold": "50",
        "launch_soft_width_native": "16",
        "integrator_limit": "500",
        "abort_above": "150",
        "abort_below": "100",
        "run_timeout_ticks": "781",
        "rearm_ticks": "98",
        "speed_frame_age_limit": "10",
    }
    values.update(overrides)
    body = "\n".join(
        f"{key} = {value}" for key, value in values.items() if value is not None
    )
    result = (
        "schema_version = 4\n"
        'rom = "JK08A"\n'
        'name = "hold-test"\n\n'
        "[rolling_launch]\n"
        f"{body}\n"
    )
    if telemetry is not None:
        result += "\n[can_telemetry]\n" + "\n".join(
            f"{key} = {value}" for key, value in telemetry.items()
        ) + "\n"
    return result


def parse(text):
    return build_rom.parse_profile(text.encode("utf-8"), "profile.toml")


def hold_slot(**fields):
    values = dict(
        integral_gain=3,
        launch_rpm_native=400,
        launch_speed_threshold=50,
        launch_soft_width_native=16,
    )
    values.update(fields)
    return rolling_launch.Slot(**values)


class ProfileSchemaTest(unittest.TestCase):
    """Profile schema 4 and the derived efficiency table, without a build."""

    @classmethod
    def setUpClass(cls):
        cls.stock = STOCK.read_bytes()

    def test_slot_keys_take_scalars_or_per_map_values(self):
        profile = parse(profile_text(
            launch_rpm_native="[400, 480, 560, 640, 720]",
            launch_speed_threshold="[50, 0x7FFF, 1, 65535, 50]",
            launch_soft_width_native="[0, 16, 32, 0, 559]",
            integral_gain="[0, 2, 4, 2, 0]",
            max_trim_rpm="[0, 10, 20, 30, 40]",
            max_trim_speed="[40, 0, 7, 20, 0]",
            floor_command="[120, 110, 0, 120, 60]",
        ))
        slots = profile.calibration.slots
        self.assertEqual(
            [slot.launch_rpm_native for slot in slots], [400, 480, 560, 640, 720]
        )
        self.assertEqual(
            [slot.launch_speed_threshold for slot in slots],
            [50, 0x7FFF, 1, 65535, 50],
        )
        self.assertEqual(
            [slot.launch_soft_width_native for slot in slots], [0, 16, 32, 0, 559]
        )
        self.assertEqual(
            [slot.max_trim_rpm for slot in slots], [0, 10, 20, 30, 40]
        )
        self.assertEqual(
            [slot.max_trim_speed for slot in slots], [40, 0, 7, 20, 0]
        )
        self.assertEqual(
            [slot.floor_command for slot in slots], [120, 110, 0, 120, 60]
        )
        self.assertEqual({slot.reserved_05 for slot in slots}, {0})
        text = build_rom.profile_text("slots", "JK08A", profile.calibration)
        self.assertIn("launch_soft_width_native = [0, 16, 32, 0, 559]", text)
        self.assertIn("max_trim_rpm = [0, 10, 20, 30, 40]", text)
        self.assertIn("max_trim_speed = [40, 0, 7, 20, 0]", text)
        self.assertNotIn("max_trim =", text)
        self.assertEqual(parse(text).calibration, profile.calibration)

    def test_optional_trims_and_floor_default_to_zero(self):
        profile = parse(profile_text())
        self.assertEqual(
            profile.calibration.slots, (hold_slot(),) * rolling_launch.SLOT_COUNT
        )
        for key in ("launch_rpm_native", "launch_speed_threshold",
                    "launch_soft_width_native", "integral_gain"):
            with self.subTest(missing=key):
                with self.assertRaisesRegex(build_rom.BuildError, "fields differ"):
                    parse(profile_text(**{key: None}))

    def test_ambiguous_retired_and_old_schema_keys_are_refused(self):
        with self.assertRaisesRegex(build_rom.BuildError, "max_trim is ambiguous"):
            parse(profile_text(max_trim="20"))
        for key in ("rpm_ceiling_offset_native", "rpm_ceiling_hysteresis_native",
                    "trim_efficiency", "reserved_05"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(build_rom.BuildError, "fields differ"):
                    parse(profile_text(**{key: "8"}))
        old = profile_text().replace("schema_version = 4", "schema_version = 3")
        with self.assertRaisesRegex(
            build_rom.BuildError, "unsupported profile schema 3"
        ):
            parse(old)

    def test_invalid_slot_values_name_the_map(self):
        cases = {
            # The launch RPM must lie above the minimum engine speed.
            "launch_rpm_native": ("[400, 160, 400, 400, 400]", "map 2"),
            # The soft-width zone must stay above the minimum engine speed.
            "launch_soft_width_native": ("[0, 0, 240, 0, 0]", "map 3"),
            "launch_speed_threshold": ("[50, 50, 50, 0, 50]", "map 4"),
            "floor_command": ("[120, 120, 120, 120, 121]", "map 5"),
            "max_trim_rpm": ("[41, 0, 0, 0, 0]", "map 1"),
            "max_trim_speed": ("[0, 41, 0, 0, 0]", "map 2"),
        }
        for key, (value, maps) in cases.items():
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    build_rom.BuildError, f"calibration is invalid in {maps}"
                ):
                    parse(profile_text(**{key: value}))
        for value in ("[1, 2]", "true", "[400, 400, 400, 400, 400.0]"):
            with self.subTest(value=value):
                with self.assertRaises(build_rom.BuildError):
                    parse(profile_text(launch_rpm_native=value))

    def test_builtin_profile_is_the_disabled_observe_record_of_every_family(self):
        for rom in (build_rom.ROM_SERIES, *(
            runtime_targets.load_runtime_target(item).family
            for item in runtime_targets.RELOCATED_ROMS
        )):
            with self.subTest(rom=rom):
                profile = build_rom.builtin_profile(rom)
                self.assertEqual(profile.name, build_rom.OBSERVE_PROFILE_NAME)
                self.assertEqual(profile.calibration, rolling_launch.Calibration())
                self.assertTrue(profile.calibration.is_valid())
                self.assertEqual(profile.calibration.enable_mask, 0)
                self.assertEqual(
                    profile.calibration.mode, rolling_launch.Mode.OBSERVE
                )

    def test_efficiency_table_derives_from_the_f_curve_of_the_image(self):
        axis = self.stock[
            build_rom.TRIM_AXIS_ADDRESS :
            build_rom.TRIM_AXIS_ADDRESS + build_rom.TRIM_POINTS
        ]
        values = self.stock[
            build_rom.TRIM_TABLE_ADDRESS :
            build_rom.TRIM_TABLE_ADDRESS + build_rom.TRIM_POINTS
        ]
        table = build_rom.efficiency_table(self.stock)
        self.assertEqual(
            table, rolling_launch.EfficiencyTable.from_curve(tuple(axis), tuple(values))
        )
        # F(20) = 45 on the axis; F(7) lies between F(6) = 4 and F(9) = 9.
        self.assertEqual(table.at(0), 1000)
        self.assertEqual(table.at(20), 824)
        self.assertEqual(table.at(7), 980)

        tuned = bytearray(self.stock)
        index = list(axis).index(20)
        tuned[build_rom.TRIM_TABLE_ADDRESS + index] += 1
        self.assertEqual(build_rom.efficiency_table(tuned).at(20), 820)

        layout = rolling_launch_layout.load_layout()
        data = bytearray(self.stock)
        written = build_rom.write_efficiency_table(data, layout, tuned)
        span = layout.efficiency
        self.assertEqual(written, frozenset(range(span.start, span.end)))
        self.assertEqual(
            bytes(data[span.start : span.end]),
            build_rom.efficiency_table(tuned).to_bytes(),
        )
        self.assertEqual(
            [offset for offset, pair in enumerate(zip(self.stock, data)) if pair[0] != pair[1]],
            [offset for offset in sorted(written) if self.stock[offset] != data[offset]],
        )

        broken = bytearray(self.stock)
        broken[build_rom.TRIM_AXIS_ADDRESS + 1] = 0
        with self.assertRaisesRegex(build_rom.BuildError, "axis"):
            build_rom.efficiency_table(broken)


@pytest.mark.slow
class BuildRomTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = STOCK.read_bytes()
        cls.map_layout = map_switching_layout.load_layout()
        cls.base_result = build_rom.build_image(
            cls.stock, source_name="exact stock"
        )
        cls.family_images = rom_homology.load_images()
        cls.family_results = {
            rom: (
                cls.base_result
                if rom == "JK08A"
                else build_rom.build_image(
                    cls.family_images[rom].data,
                    source_name=f"exact {rom} stock",
                )
            )
            for rom in runtime_targets.EXACT_ROMS
        }
        cls.relocated_results = {
            rom: build_rom.build_image(
                cls.family_images[rom].data,
                source_name=f"exact {rom} stock",
            )
            for rom in runtime_targets.RELOCATED_ROMS
        }

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

    def test_exact_family_builds_preserve_each_target_identity_and_calibration(self):
        launch_layout = rolling_launch_layout.load_layout()
        component_offsets = build_rom._component_offsets(
            self.map_layout, launch_layout
        )
        permitted = component_offsets | set(checksums.checksum_byte_offsets())
        output_hashes = set()

        self.assertEqual(
            build_rom.builtin_profile().rom,
            build_rom.ROM_SERIES,
        )
        for rom in runtime_targets.EXACT_ROMS:
            with self.subTest(rom=rom):
                source = self.family_images[rom].data
                result = self.family_results[rom]
                self.assertEqual(result.rom, rom)
                self.assertEqual(result.series, build_rom.ROM_SERIES)
                self.assertEqual(result.detection, build_rom.AUTO_ROM)
                self.assertEqual(
                    build_rom.select_rom(source),
                    (rom, build_rom.AUTO_ROM),
                )
                self.assertTrue(checksums.verify(result.data).valid)
                identity = slice(
                    map_switching_layout.COMPATIBLE_IDENTITY_START,
                    map_switching_layout.COMPATIBLE_IDENTITY_END,
                )
                self.assertEqual(result.data[identity], source[identity])
                changed = {
                    offset
                    for offset, (before, after) in enumerate(
                        zip(source, result.data)
                    )
                    if before != after
                }
                self.assertEqual(changed - permitted, set())
                for family in self.map_layout.families:
                    canonical = source[
                        family.canonical_address :
                        family.canonical_address + family.byte_length
                    ]
                    for address in family.copies:
                        self.assertEqual(
                            result.data[
                                address : address + family.byte_length
                            ],
                            canonical,
                        )
                output_hashes.add(result.output_sha256)
        self.assertEqual(len(output_hashes), len(runtime_targets.EXACT_ROMS))

    def test_relocated_family_builds_are_target_specific(self):
        output_hashes = set()
        for rom in runtime_targets.RELOCATED_ROMS:
            with self.subTest(rom=rom):
                source = self.family_images[rom].data
                target = runtime_targets.load_runtime_target(rom)
                result = self.relocated_results[rom]
                checksum_layout = target.checksum_layout
                component_offsets = build_rom._component_offsets(
                    target.map_layout,
                    target.rolling_layout,
                    target.telemetry_layout,
                    checksum_layout,
                )
                permitted = component_offsets | set(
                    rom_checksums.checksum_byte_offsets(checksum_layout)
                )

                self.assertEqual(result.rom, rom)
                self.assertEqual(result.series, target.family)
                self.assertEqual(result.detection, build_rom.AUTO_ROM)
                self.assertEqual(result.profile.rom, target.family)
                self.assertEqual(
                    result.profile.name, build_rom.OBSERVE_PROFILE_NAME
                )
                self.assertEqual(build_rom.select_rom(source), (rom, "auto"))
                explicit = build_rom.build_image(
                    source, rom=rom.lower(), source_name=f"explicit {rom}"
                )
                self.assertEqual(explicit.detection, "explicit")
                self.assertEqual(explicit.data, result.data)
                self.assertTrue(
                    rom_checksums.verify(result.data, checksum_layout).valid
                )
                # The SH7059 layouts add the 30-instruction state-code
                # ignition adapter to the VQ37 map stage.
                self.assertEqual(
                    result.map_instruction_count,
                    467
                    if rom in (
                        runtime_targets.SH7059_1ND_ROMS
                        + runtime_targets.SH7059_1ME3B_ROMS
                    )
                    else 437
                    if rom in runtime_targets.VQ37_RUNTIME_ROMS
                    else 453,
                )
                self.assertIsNone(target.rolling_layout)
                self.assertEqual(result.rolling_instruction_count, 0)
                # The VQ37 captures add the instructions that move the
                # one-bit fields into their wire bits.
                self.assertEqual(
                    result.telemetry_instruction_count,
                    1038 + {
                        "1ME3B": 13, "JK78C": 15, "1ND0A": 16, "1ND3B": 16,
                    }.get(rom, 0),
                )
                self.assertEqual(
                    target.map_layout.variant,
                    (
                        (
                            "sh7059-1nd"
                            if rom in runtime_targets.SH7059_1ND_ROMS
                            else "sh7059-1me3b"
                            if rom in runtime_targets.SH7059_1ME3B_ROMS
                            else "sh7058-jk78"
                        )
                        if rom in runtime_targets.VQ37_RUNTIME_ROMS
                        else "dual-cvtc"
                    ),
                )
                self.assertEqual(
                    target.telemetry_layout.variant, "mailbox26-tail-chain"
                )
                self.assertEqual(
                    result.data[
                        target.telemetry_layout.mailbox_record_address :
                        target.telemetry_layout.mailbox_record_address + 4
                    ],
                    result.telemetry_mailbox_record,
                )

                changed = {
                    offset
                    for offset, pair in enumerate(zip(source, result.data))
                    if pair[0] != pair[1]
                }
                self.assertEqual(changed - permitted, set())
                identity = slice(
                    map_switching_layout.COMPATIBLE_IDENTITY_START,
                    map_switching_layout.COMPATIBLE_IDENTITY_END,
                )
                self.assertEqual(result.data[identity], source[identity])
                for family in target.map_layout.families:
                    canonical = source[
                        family.canonical_address :
                        family.canonical_address + family.byte_length
                    ]
                    for address in family.copies:
                        self.assertEqual(
                            result.data[address : address + family.byte_length],
                            canonical,
                        )
                output_hashes.add(result.output_sha256)
        self.assertEqual(len(output_hashes), len(runtime_targets.RELOCATED_ROMS))

    def test_a_relocated_target_refuses_a_profile_that_enables_rolling_launch(self):
        pairs = (
            (runtime_targets.RELOCATED_8MFK_FAMILY, "JK00C"),
            (runtime_targets.SH7059_1ND_FAMILY, "1ND0A"),
            (runtime_targets.SH7058_JK78C_FAMILY, "JK78C"),
        )
        for family, rom in pairs:
            with self.subTest(rom=rom):
                profile = replace(
                    build_rom.builtin_profile(family),
                    calibration=parse(profile_text()).calibration,
                )
                source = self.family_images[rom].data
                with self.assertRaisesRegex(
                    build_rom.BuildError, "Rolling Launch is unsupported"
                ):
                    build_rom.build_image(source, profile=profile)

    def test_unknown_identity_and_unsupported_rom_are_rejected(self):
        wrong_identity = bytearray(self.stock)
        wrong_identity[
            map_switching_layout.COMPATIBLE_IDENTITY_START
        ] ^= 1
        with self.assertRaisesRegex(
            build_rom.BuildError, "could not be detected"
        ):
            build_rom.select_rom(wrong_identity)
        with self.assertRaisesRegex(
            build_rom.BuildError, "unsupported ROM selector"
        ):
            build_rom.select_rom(self.stock, "NOT-A-ROM")

    def test_explicit_series_still_requires_matching_identity(self):
        wrong_identity = bytearray(self.stock)
        wrong_identity[
            map_switching_layout.COMPATIBLE_IDENTITY_START
        ] ^= 1
        wrong_identity = checksums.recalculate(wrong_identity)
        with self.assertRaisesRegex(
            build_rom.BuildError, "is not the registered JK08A stock image"
        ):
            build_rom.build_image(wrong_identity, rom="JK08A")

    def test_complete_output_is_checksum_valid_and_closed(self):
        result = self.base_result
        self.assertTrue(checksums.verify(result.data).valid)
        map_layout = map_switching_layout.load_layout()
        launch_layout = rolling_launch_layout.load_layout()
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

    def test_every_input_other_than_the_stock_image_is_refused(self):
        images = {**self.family_results, **self.relocated_results}
        for rom, result in images.items():
            target = runtime_targets.load_runtime_target(rom)
            calibrated = bytearray(target.stock_image.data)
            calibrated[target.map_layout.families[0].canonical_address] ^= 1
            corrupt = bytearray(result.data)
            record = (target.rolling_layout or target.telemetry_layout).configuration
            corrupt[record.start] ^= 0xA5
            cases = {
                "built image": result.data,
                "calibrated stock": rom_checksums.recalculate(
                    bytearray(calibrated), target.checksum_layout
                ),
                "corrupt runtime record": rom_checksums.recalculate(
                    corrupt, target.checksum_layout
                ),
                "invalid checksum": calibrated,
            }
            for name, source in cases.items():
                with self.subTest(rom=rom, case=name), mock.patch.object(
                    build_rom.apply_map_switching, "patch_image"
                ) as compose:
                    with self.assertRaisesRegex(
                        build_rom.BuildError,
                        f"input is not the registered {rom} stock image",
                    ):
                        build_rom.build_image(bytes(source), source_name=name)
                    compose.assert_not_called()

    def test_cli_refuses_a_built_image_before_writing_any_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.bin"
            output_path = Path(directory) / "output.bin"
            input_path.write_bytes(self.base_result.data)
            error = io.StringIO()
            with contextlib.redirect_stderr(error), self.assertRaises(SystemExit) as stopped:
                build_rom.main([str(input_path), "--output", str(output_path)])
            self.assertEqual(stopped.exception.code, 2)
            self.assertIn("is not the registered JK08A stock image", error.getvalue())
            self.assertIn("make rom-extract", error.getvalue())
            self.assertEqual(list(Path(directory).iterdir()), [input_path])

    def test_strict_profile_enables_hold_mode_and_controller_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.toml"
            path.write_text(profile_text(), encoding="utf-8")
            profile = build_rom.load_profile(path)
        self.assertEqual(profile.calibration.mode, rolling_launch.Mode.HOLD)
        self.assertEqual(profile.calibration.enable_mask, 0x05)
        self.assertEqual(profile.calibration.target_speed_offset, -20)
        self.assertEqual(
            profile.calibration.slots, (hold_slot(),) * rolling_launch.SLOT_COUNT
        )
        result = build_rom.build_image(self.stock, profile=profile)
        self.assertEqual(
            result.configuration, profile.calibration.to_bytes()
        )

    def test_build_writes_the_record_and_the_efficiency_table_of_the_source(self):
        profile = parse(profile_text(
            max_trim_rpm="[0, 0, 0, 20, 7]",
            max_trim_speed="[7, 20, 0, 0, 0]",
            floor_command="120",
        ))
        result = build_rom.build_image(self.stock, profile=profile)
        self.assertEqual(result.configuration, profile.calibration.to_bytes())
        span = rolling_launch_layout.load_layout().efficiency
        expected = build_rom.efficiency_table(self.stock).to_bytes()
        self.assertEqual(result.data[span.start : span.end], expected)
        self.assertEqual(result.rolling_efficiency, expected)
        # The observe build derives the same table: E depends on F only.
        self.assertEqual(self.base_result.rolling_efficiency, expected)

    def test_profile_can_enable_configurable_can_telemetry(self):
        telemetry_values = {
            "enabled": "true",
            "can_id": "0x6EF",
            "profile": '"tuning"',
            "tick_divisor": "5",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.toml"
            path.write_text(
                profile_text(telemetry=telemetry_values),
                encoding="utf-8",
            )
            profile = build_rom.load_profile(path)
        self.assertEqual(
            profile.telemetry,
            can_telemetry.Configuration(True, 0x6EF, "tuning", 5),
        )
        result = build_rom.build_image(self.stock, profile=profile)
        self.assertEqual(
            result.telemetry_configuration, profile.telemetry.to_bytes()
        )
        self.assertEqual(
            result.telemetry_mailbox_record,
            profile.telemetry.mailbox_record(),
        )
        self.assertTrue(checksums.verify(result.data).valid)

    def test_builtin_profile_installs_disabled_telemetry(self):
        result = self.base_result
        self.assertFalse(result.profile.telemetry.enabled)
        self.assertEqual(
            result.telemetry_mailbox_record,
            result.profile.telemetry.mailbox_record(),
        )
        layout = build_rom.can_telemetry_layout.load_layout()
        self.assertTrue(all(
            result.data[unit.span.start : unit.span.end]
            != bytes([0xFF]) * unit.span.size
            for unit in layout.assembly_units
            if unit.key != "tables"
        ))

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
                profile_text(window_width="0"), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                build_rom.BuildError, "calibration is invalid"
            ):
                build_rom.load_profile(invalid)

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


class BuildArtifactsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = STOCK.read_bytes()
        cls.base_result = build_rom.build_image(cls.stock, source_name="artifact fixture")

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
            self.assertEqual(manifest["schema_version"], 5)
            self.assertEqual(manifest["series"], build_rom.ROM_SERIES)
            self.assertEqual(manifest["rom"], "JK08A")
            self.assertEqual(
                set(manifest["input"]), {"path", "sha256", "checksums"}
            )
            launch = manifest["output"]["configuration"]["rolling_launch"]
            self.assertEqual(
                launch["configuration_hex"], self.base_result.configuration.hex()
            )
            self.assertEqual(
                launch["efficiency_hex"], self.base_result.rolling_efficiency.hex()
            )
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

    def test_default_output_path_is_adjacent_and_non_destructive(self):
        self.assertEqual(
            build_rom.default_output_path(Path("/tmp/input.bin")),
            Path("/tmp/input-complete.bin"),
        )

    def test_all_sidecars_are_complete_before_rom_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image.bin"
            artifacts = build_rom.artifact_contents(self.base_result, STOCK, output)
            link = os.link

            def publish(source, destination):
                self.assertFalse(output.exists())
                if destination == output:
                    for path, content in artifacts.items():
                        if path != output:
                            self.assertEqual(path.read_bytes(), content)
                    self.assertEqual(source.read_bytes(), self.base_result.data)
                link(source, destination)

            with mock.patch.object(build_rom.apply_map_switching.os, "link", side_effect=publish):
                created = build_rom.write_artifacts(self.base_result, STOCK, output)
            self.assertEqual(set(created), set(artifacts))
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])

    def test_manifest_staging_failure_leaves_no_published_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image.bin"
            fsync = os.fsync
            calls = 0

            def sync(fd):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise OSError("injected manifest staging failure")
                fsync(fd)

            with mock.patch.object(build_rom.apply_map_switching.os, "fsync", side_effect=sync):
                with self.assertRaisesRegex(OSError, "manifest staging failure"):
                    build_rom.write_artifacts(self.base_result, STOCK, output)
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertEqual(len(build_rom.write_artifacts(self.base_result, STOCK, output)), 4)

    def test_failure_or_interruption_between_sidecars_allows_retry(self):
        for failure in (OSError, KeyboardInterrupt):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "image.bin"
                artifacts = build_rom.artifact_contents(self.base_result, STOCK, output)
                digest = Path(f"{output}.sha256")
                digest.write_bytes(artifacts[digest])
                manifest = Path(f"{output}.manifest.json")
                link = os.link

                def publish(source, destination):
                    if destination == manifest:
                        raise failure("injected publication failure")
                    link(source, destination)

                with mock.patch.object(build_rom.apply_map_switching.os, "link", side_effect=publish):
                    with self.assertRaises(failure):
                        build_rom.write_artifacts(self.base_result, STOCK, output)
                remaining = {digest}
                if failure is KeyboardInterrupt:
                    remaining.add(Path(f"{output}.md5"))
                self.assertEqual(set(Path(directory).iterdir()), remaining)
                for path in remaining:
                    self.assertEqual(path.read_bytes(), artifacts[path])
                created = build_rom.write_artifacts(self.base_result, STOCK, output)
                self.assertEqual(set(created), set(artifacts) - remaining)

    def test_relative_and_absolute_paths_accept_the_same_artifact_set(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "source.bin"
            output_path = Path(directory) / "image.bin"
            input_path.write_bytes(self.stock)
            relative_input = Path(os.path.relpath(input_path))
            relative_output = Path(os.path.relpath(output_path))
            self.assertEqual(
                len(build_rom.write_artifacts(self.base_result, relative_input, relative_output)), 4
            )
            self.assertEqual(
                build_rom.write_artifacts(self.base_result, input_path, output_path), ()
            )
            manifest = json.loads(Path(f"{output_path}.manifest.json").read_bytes())
            self.assertEqual(manifest["input"]["path"], str(input_path.resolve()))
            self.assertEqual(manifest["output"]["path"], str(output_path.resolve()))

    def test_stock_input_requires_explicit_output_but_allows_verify_only(self):
        with mock.patch.object(build_rom, "build_image", return_value=self.base_result):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with mock.patch.object(build_rom, "write_artifacts") as write:
                    with self.assertRaises(SystemExit) as stopped:
                        build_rom.main([str(STOCK)])
                    self.assertEqual(stopped.exception.code, 2)
                    write.assert_not_called()
                    self.assertEqual(build_rom.main([str(STOCK), "--verify-only"]), 0)
                    write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
