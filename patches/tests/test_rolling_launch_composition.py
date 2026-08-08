import dataclasses
import unittest

from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


class RollingLaunchCompositionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = rolling_launch_layout.load_layout()
        cls.blobs = rolling_launch_assembly.load_payloads(cls.layout)
        cls.parsed = rolling_launch_assembly.validate_assembly_sources(
            cls.layout
        )
        cls.base = rolling_launch_compose.build_base_composition().data
        cls.result = rolling_launch_compose.compose(
            layout=cls.layout,
            base=cls.base,
            blobs=cls.blobs,
        )

    def test_manifest_locks_fail_closed_default_and_exact_endpoint(self):
        calibration = rolling_launch.Calibration.from_bytes(
            self.layout.default_configuration
        )
        self.assertTrue(calibration.is_valid())
        self.assertEqual(calibration.enable_mask, 0)
        self.assertEqual(
            self.result.base_sha256,
            self.layout.base_composition_sha256,
        )
        self.assertEqual(
            self.result.sha256,
            self.layout.expected_composition_sha256,
        )
        self.assertFalse(self.result.checksums_recalculated)

    def test_ram_state_is_disjoint_and_diagnostics_cover_live_pairs(self):
        self.assertFalse(
            self.layout.ram.state.overlaps(
                self.layout.ram.base_reservation
            )
        )
        self.assertEqual(self.layout.ram.state.size, 20)
        self.assertEqual(
            tuple(item.target for item in self.layout.diagnostics),
            tuple(range(
                self.layout.ram.state.start,
                self.layout.ram.state.start + 18,
                2,
            )),
        )

    def test_scheduler_tick_formula_is_explicit(self):
        scheduler = self.layout.scheduler
        self.assertEqual(scheduler.table_index, 0)
        self.assertEqual(scheduler.tick_numerator, 204800)
        self.assertEqual(
            scheduler.candidate_tick_microseconds,
            scheduler.tick_numerator * 1_000_000
            // scheduler.pphi_candidate_hz,
        )

    def test_tracked_payloads_and_machine_control_flow_match_sources(self):
        audit = rolling_launch_assembly.validate_instruction_semantics(
            self.layout, self.parsed, self.blobs
        )
        self.assertEqual(audit.instructions, 837)
        self.assertEqual(audit.delayed_transfers, 61)
        self.assertEqual(audit.pc_relative_references, 74)
        self.assertEqual(audit.direct_branches, 144)
        self.assertEqual(audit.indirect_transfers, 22)

    def test_payload_tamper_is_rejected_by_sha_lock(self):
        blobs = dict(self.blobs)
        tampered = bytearray(blobs["engine"])
        tampered[0] ^= 0x01
        blobs["engine"] = bytes(tampered)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            rolling_launch_compose.compose(
                layout=self.layout,
                base=self.base,
                blobs=blobs,
            )

    def test_base_composition_tamper_is_rejected(self):
        tampered = bytearray(self.base)
        tampered[0x100] ^= 0x01
        with self.assertRaisesRegex(ValueError, "base map-switching"):
            rolling_launch_layout.validate_base_composition(
                self.layout, tampered
            )

    def test_closed_write_set_contains_only_declared_ranges(self):
        ranges = rolling_launch_compose.composition_write_ranges(self.layout)
        self.assertEqual(sum(item.size for item in ranges), 2164)
        self.assertEqual(self.result.permitted_write_bytes, 2164)
        self.assertEqual(self.result.changed_bytes, 1883)
        for left, right in zip(ranges, ranges[1:]):
            self.assertFalse(left.overlaps(right))

    def test_all_hooks_and_did_pointers_are_published_big_endian(self):
        data = self.result.data
        for hook in self.layout.hooks:
            self.assertEqual(
                int.from_bytes(
                    data[hook.address : hook.address + hook.width], "big"
                ),
                hook.replacement,
            )
        for item in self.layout.diagnostics:
            self.assertEqual(
                int.from_bytes(
                    data[item.pointer_address : item.pointer_address + 4],
                    "big",
                ),
                item.target,
            )

    def test_custom_valid_calibration_changes_only_configuration(self):
        calibration = dataclasses.replace(
            rolling_launch.Calibration(),
            mode=rolling_launch.Mode.RPM_HOLD,
            enable_mask=0x01,
        )
        custom = rolling_launch_compose.compose(
            layout=self.layout,
            base=self.base,
            blobs=self.blobs,
            configuration=calibration,
        )
        differences = {
            index
            for index, (left, right) in enumerate(
                zip(self.result.data, custom.data)
            )
            if left != right
        }
        self.assertTrue(differences)
        self.assertTrue(all(
            self.layout.configuration.start
            <= index
            < self.layout.configuration.end
            for index in differences
        ))

    def test_invalid_calibration_is_rejected(self):
        invalid = dataclasses.replace(
            rolling_launch.Calibration(), magic=0
        )
        with self.assertRaisesRegex(ValueError, "configuration is invalid"):
            rolling_launch_compose.compose(
                layout=self.layout,
                base=self.base,
                blobs=self.blobs,
                configuration=invalid,
            )

    def test_composed_tamper_inside_and_outside_write_set_is_rejected(self):
        for address in (self.layout.configuration.start, 0x100):
            with self.subTest(address=address):
                tampered = bytearray(self.result.data)
                tampered[address] ^= 0x01
                with self.assertRaises(ValueError):
                    rolling_launch_compose.validate_composed(
                        layout=self.layout,
                        base=self.base,
                        composed=tampered,
                        blobs=self.blobs,
                    )

    def test_source_counts_equal_manifest_totals(self):
        self.assertEqual(
            sum(item.instruction_count for item in self.layout.assembly_units),
            837,
        )
        self.assertEqual(
            sum(item.data_bytes for item in self.layout.assembly_units),
            198,
        )
        self.assertEqual(
            sum(item.instruction_count for item in self.parsed.values()),
            837,
        )


if __name__ == "__main__":
    unittest.main()
