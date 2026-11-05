from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from patches import apply_map_switching as map_runtime
from patches import apply_rolling_launch as patcher
from patches import jk08a_checksums as checksums
from patches import map_switching_compose
from patches import map_switching_layout as map_layout_model
from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout as rolling_layout_model


CALIBRATION = rolling_launch.Calibration(
    mode=rolling_launch.Mode.HOLD,
    enable_mask=0x01,
)


class ApplyRollingLaunchTest(unittest.TestCase):
    def test_stage_module_does_not_expose_a_command_entry_point(self):
        self.assertFalse(hasattr(patcher, "main"))

    @classmethod
    def setUpClass(cls):
        cls.map_layout = map_layout_model.load_layout()
        cls.rolling_layout = rolling_layout_model.load_layout()
        cls.map_payloads = map_runtime.load_payloads(cls.map_layout)
        cls.rolling_payloads = rolling_launch_assembly.load_payloads(
            cls.rolling_layout
        )
        cls.source = bytes(checksums.recalculate(
            rolling_launch_compose.build_base_composition().data
        ))
        cls.source_sha256 = patcher.sha256(cls.source)
        cls.efficiency = rolling_launch_compose.efficiency_table(cls.source)
        cls.result = patcher.patch_image(
            cls.source,
            calibration=CALIBRATION,
            efficiency=cls.efficiency,
            map_layout=cls.map_layout,
            rolling_layout=cls.rolling_layout,
            map_payloads=cls.map_payloads,
            rolling_payloads=cls.rolling_payloads,
            source_name="synthetic complete map-switching endpoint",
            expected_source_sha256=cls.source_sha256,
        )

    def patch(self, source, **kwargs):
        kwargs.setdefault("calibration", CALIBRATION)
        kwargs.setdefault("efficiency", self.efficiency)
        return patcher.patch_image(
            source,
            map_layout=self.map_layout,
            rolling_layout=self.rolling_layout,
            map_payloads=self.map_payloads,
            rolling_payloads=self.rolling_payloads,
            source_name="test source",
            expected_source_sha256=kwargs.pop(
                "expected_source_sha256", patcher.sha256(source)
            ),
            **kwargs,
        )

    def test_configuration_is_the_given_calibration(self):
        self.assertEqual(self.result.configuration, CALIBRATION.to_bytes())
        self.assertEqual(
            rolling_launch.Calibration.from_bytes(self.result.configuration),
            CALIBRATION,
        )

    def test_stage_requires_the_calibration_and_the_efficiency_table(self):
        for missing in ("calibration", "efficiency"):
            with self.subTest(missing=missing):
                arguments = {"calibration": CALIBRATION, "efficiency": self.efficiency}
                del arguments[missing]
                with self.assertRaises(TypeError):
                    patcher.patch_image(self.source, **arguments)

    def test_stage_writes_the_given_efficiency_table(self):
        span = self.rolling_layout.efficiency
        self.assertEqual(
            self.result.data[span.start : span.end], self.efficiency.to_bytes()
        )
        self.assertEqual(self.result.efficiency, self.efficiency.to_bytes())
        table = rolling_launch.EfficiencyTable((1000, *range(999, 959, -1)))
        result = self.patch(self.source, efficiency=table)
        self.assertEqual(result.data[span.start : span.end], table.to_bytes())
        self.assertTrue(checksums.verify(result.data).valid)

    def test_invalid_efficiency_table_is_rejected(self):
        table = self.efficiency.to_bytes()
        for damaged in (table[:-2], bytes(2) + table[2:]):
            with self.subTest(size=len(damaged)):
                with self.assertRaisesRegex(
                    patcher.PatchError, "efficiency table is invalid"
                ):
                    self.patch(self.source, efficiency=damaged)

    def test_base_identity_is_the_declared_map_switching_endpoint(self):
        digest = patcher.LOCKED_MAP_SWITCHING_SOURCE_SHA256
        self.assertEqual(len(digest), 64)
        int(digest, 16)
        self.assertEqual(
            digest,
            "8c604b3c6760fdea02a76f724b3daa09e7a799eab4204e0cec991f45d51e8a2d",
        )

    def test_output_has_valid_checksums_and_exact_size(self):
        self.assertEqual(len(self.result.data), checksums.LAYOUT.rom_size)
        verification = checksums.verify(self.result.data)
        self.assertTrue(verification.valid)
        self.assertEqual(verification.stored, verification.calculated)

    def test_payloads_hooks_diagnostics_and_configuration_are_exact(self):
        data = self.result.data
        for unit in self.rolling_layout.assembly_units:
            self.assertEqual(
                data[unit.span.start : unit.span.end],
                self.rolling_payloads[unit.key],
            )
        for hook in self.rolling_layout.hooks:
            actual = int.from_bytes(
                data[hook.address : hook.address + hook.width], "big"
            )
            self.assertEqual(actual, hook.replacement)
        for item in self.rolling_layout.diagnostics:
            actual = int.from_bytes(
                data[item.pointer_address : item.pointer_address + 4], "big"
            )
            self.assertEqual(actual, item.target)
        self.assertEqual(
            data[
                self.rolling_layout.configuration.start :
                self.rolling_layout.configuration.end
            ],
            CALIBRATION.to_bytes(),
        )

    def test_closed_write_set_contains_only_payload_and_checksum_bytes(self):
        permitted, checksum_offsets = patcher._final_write_offsets(
            self.rolling_layout
        )
        changed = {
            offset
            for offset, (before, after) in enumerate(
                zip(self.source, self.result.data)
            )
            if before != after
        }
        self.assertEqual(changed - permitted, set())
        self.assertEqual(
            self.result.final_changed_bytes, len(changed)
        )
        self.assertEqual(
            self.result.checksum_changed_bytes,
            len(changed & checksum_offsets),
        )

    def test_source_map_switching_runtime_is_preserved(self):
        rolling_offsets, _ = patcher._final_write_offsets(
            self.rolling_layout
        )
        for unit in self.map_layout.assembly_units:
            for offset in range(unit.span.start, unit.span.end):
                if offset not in rolling_offsets:
                    self.assertEqual(
                        self.result.data[offset], self.source[offset]
                    )

    def test_exact_source_hash_is_required(self):
        with self.assertRaisesRegex(patcher.PatchError, "source SHA-256"):
            patcher.patch_image(
                self.source,
                calibration=CALIBRATION,
                efficiency=self.efficiency,
                map_layout=self.map_layout,
                rolling_layout=self.rolling_layout,
                map_payloads=self.map_payloads,
                rolling_payloads=self.rolling_payloads,
                expected_source_sha256="0" * 64,
            )

    def test_invalid_checksum_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[0x9000] ^= 1
        with self.assertRaisesRegex(patcher.PatchError, "checksum mismatch"):
            self.patch(bytes(corrupt))

    def test_missing_map_switching_unit_is_rejected(self):
        corrupt = bytearray(self.source)
        unit = self.map_layout.assembly_unit_by_key["selector_host"]
        corrupt[unit.span.start] ^= 1
        corrupt = bytes(checksums.recalculate(corrupt))
        with self.assertRaisesRegex(
            patcher.PatchError, "map-switching unit selector_host differs"
        ):
            self.patch(corrupt)

    def test_occupied_rolling_rom_is_rejected(self):
        for span in self.rolling_layout.claimed_rom_ranges:
            with self.subTest(span=span.key):
                corrupt = bytearray(self.source)
                corrupt[span.start] = 0
                corrupt = bytes(checksums.recalculate(corrupt))
                with self.assertRaisesRegex(
                    patcher.PatchError, "allocation is occupied"
                ):
                    self.patch(corrupt)

    def test_occupied_diagnostic_pointer_is_rejected(self):
        corrupt = bytearray(self.source)
        item = self.rolling_layout.diagnostics[0]
        corrupt[item.pointer_address : item.pointer_address + 4] = bytes(4)
        corrupt = bytes(checksums.recalculate(corrupt))
        with self.assertRaisesRegex(patcher.PatchError, "pointer is occupied"):
            self.patch(corrupt)

    def test_invalid_calibration_is_rejected(self):
        invalid = replace(CALIBRATION, enable_mask=0x20)
        with self.assertRaisesRegex(patcher.PatchError, "calibration is invalid"):
            self.patch(self.source, calibration=invalid)

    def test_pass_through_profile_remains_supported_by_core_patcher(self):
        observe = rolling_launch.Calibration()
        result = self.patch(self.source, calibration=observe)
        self.assertEqual(
            result.data[
                self.rolling_layout.configuration.start :
                self.rolling_layout.configuration.end
            ],
            observe.to_bytes(),
        )
        self.assertTrue(checksums.verify(result.data).valid)

    def test_writer_is_exclusive_and_idempotent_for_identical_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate.bin"
            self.assertTrue(
                map_runtime.write_output(output, self.result.data)
            )
            self.assertFalse(
                map_runtime.write_output(output, self.result.data)
            )
            self.assertTrue(
                map_runtime.write_md5_sidecar(output, self.result.data)
            )
            self.assertFalse(
                map_runtime.write_md5_sidecar(output, self.result.data)
            )
            self.assertEqual(output.read_bytes(), self.result.data)

    def test_different_existing_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate.bin"
            output.write_bytes(b"different")
            with self.assertRaisesRegex(
                map_runtime.PatchError, "existing output differs"
            ):
                map_runtime.write_output(output, self.result.data)

    def test_composition_audit_counts_match_manifest(self):
        self.assertEqual(
            self.result.instruction_count,
            self.rolling_layout.assembled_instruction_count,
        )
        self.assertEqual(self.result.code_entry_count, 12)
        self.assertEqual(
            self.result.diagnostic_count,
            len(self.rolling_layout.diagnostics),
        )
        composed = rolling_launch_compose._build_expected(
            self.rolling_layout,
            self.source,
            self.rolling_payloads,
            self.result.configuration,
            self.result.efficiency,
        )
        rolling_launch_compose._validate_composed(
            self.rolling_layout,
            self.source,
            composed,
            self.rolling_payloads,
            self.result.configuration,
            self.result.efficiency,
        )


if __name__ == "__main__":
    unittest.main()
