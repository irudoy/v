import dataclasses
from itertools import chain
import unittest

from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


def _offsets(ranges):
    return set(chain.from_iterable(range(item.start, item.end) for item in ranges))


class RollingLaunchAbiCompositionTest(unittest.TestCase):
    """Composition contracts that hold for the ABI before payloads exist."""

    @classmethod
    def setUpClass(cls):
        cls.layout = rolling_launch_layout.load_layout()
        cls.ranges = rolling_launch_compose.composition_write_ranges(cls.layout)

    def test_ram_state_is_disjoint_and_diagnostics_cover_live_pairs(self):
        self.assertFalse(
            self.layout.ram.state.overlaps(
                self.layout.ram.base_reservation
            )
        )
        self.assertEqual(self.layout.ram.state.size, 44)
        # Words +0x14, +0x18, and +0x1A have no view; the spark-cut counters
        # share the view at +0x1C.
        self.assertEqual(
            tuple(item.target for item in self.layout.diagnostics),
            tuple(
                self.layout.ram.state.start + offset
                for offset in (*range(0, 0x14, 2), 0x16, 0x1C)
            ),
        )

    def test_scheduler_tick_formula_matches_target_measurement(self):
        scheduler = self.layout.scheduler
        self.assertEqual(scheduler.table_address, 0x0002196C)
        self.assertEqual(scheduler.table_index, 1)
        self.assertEqual(
            self.layout.hook_by_key["displaced_periodic_task"].address,
            scheduler.table_address + 4 * scheduler.table_index,
        )
        # Entry 28 holds the stock fuel-output inhibit coordinator.
        restored = {item.key: item for item in self.layout.restored_words}
        self.assertEqual(
            restored["stock_fuel_coordinator"].address,
            scheduler.table_address + 4 * 28,
        )
        self.assertEqual(restored["stock_fuel_coordinator"].value, 0x0004ED88)
        self.assertEqual(scheduler.tick_numerator, 204800)
        self.assertEqual(scheduler.pphi_hz, 20_000_000)
        self.assertEqual(
            scheduler.tick_microseconds,
            scheduler.tick_numerator * 1_000_000
            // scheduler.pphi_hz,
        )
        self.assertEqual(scheduler.tick_microseconds, 10_240)
        calibration = rolling_launch.Calibration.from_bytes(
            self.layout.default_configuration
        )
        self.assertEqual(
            calibration.run_timeout_ticks * scheduler.tick_microseconds,
            7_997_440,
        )
        self.assertEqual(
            calibration.rearm_ticks * scheduler.tick_microseconds,
            1_003_520,
        )

    def test_write_set_is_the_claimed_rom_outside_pending_code(self):
        for left, right in zip(self.ranges, self.ranges[1:]):
            self.assertFalse(left.overlaps(right))
        owned = {key for unit in self.layout.assembly_units for key in unit.code_regions}
        pending = [
            region.span for region in self.layout.code_regions if region.key not in owned
        ]
        self.assertEqual(
            _offsets(self.ranges) & _offsets(self.layout.claimed_rom_ranges),
            _offsets(self.layout.claimed_rom_ranges) - _offsets(pending),
        )
        for span in (
            self.layout.configuration,
            self.layout.efficiency,
            *self.layout.erased_rom_ranges,
            *self.layout.retired_configuration_spans,
        ):
            with self.subTest(span=span.key):
                self.assertIn(span, self.ranges)

    def test_write_set_holds_every_hook_pointer_and_restored_word(self):
        words = [
            (hook.address, hook.width) for hook in self.layout.hooks
        ] + [
            (item.pointer_address, 4) for item in self.layout.diagnostics
        ] + [
            (item.address, item.width) for item in self.layout.restored_words
        ]
        offsets = _offsets(self.ranges)
        for address, width in words:
            with self.subTest(address=hex(address)):
                self.assertLessEqual(set(range(address, address + width)), offsets)

    def test_expected_image_writes_the_table_the_erasures_and_the_stock_words(self):
        base = bytes(0x100000)
        blobs = {
            unit.key: bytes([0x09]) * unit.span.size
            for unit in self.layout.assembly_units
        }
        configuration = rolling_launch.Calibration().to_bytes()
        efficiency = rolling_launch.EfficiencyTable(
            (1000, *range(999, 959, -1))
        ).to_bytes()
        data = rolling_launch_compose._build_expected(
            self.layout, base, blobs, configuration, efficiency
        )
        span = self.layout.efficiency
        self.assertEqual(data[span.start : span.end], efficiency)
        span = self.layout.configuration
        self.assertEqual(data[span.start : span.end], configuration)
        for span in (*self.layout.erased_rom_ranges, *self.layout.retired_configuration_spans):
            with self.subTest(span=span.key):
                self.assertEqual(data[span.start : span.end], bytes([0xFF]) * span.size)
        for item in self.layout.restored_words:
            with self.subTest(word=item.key):
                self.assertEqual(
                    int.from_bytes(data[item.address : item.address + item.width], "big"),
                    item.value,
                )
        changed, _permitted = rolling_launch_compose._validate_write_set(
            base, data, self.ranges
        )
        self.assertGreater(changed, 0)

    def test_efficiency_table_derives_from_f_of_the_image(self):
        image = bytearray(0x100000)
        axis = (0, 2, 4, 6, 9, 12, 15, 18, 20, 24, 28, 32, 36, 40, 45, 50)
        values = (0, 1, 2, 4, 9, 14, 20, 30, 45, 60, 80, 100, 120, 110, 90, 80)
        axis_address = rolling_launch_compose.TRIM_AXIS_ADDRESS
        table_address = rolling_launch_compose.TRIM_TABLE_ADDRESS
        image[axis_address : axis_address + 16] = bytes(axis)
        image[table_address : table_address + 16] = bytes(values)
        table = rolling_launch_compose.efficiency_table(bytes(image))
        self.assertEqual(table.at(0), 1000)
        # F(7) = 4 + (9 - 4) * 1 // 3 = 5; F(20) = 45 on the axis.
        self.assertEqual(table.at(7), (256 - 5) * 1000 // 256)
        self.assertEqual(table.at(20), (256 - 45) * 1000 // 256)
        # F(38) lies on the descending segment: 120 + (110 - 120) * 2 // 4 = 115.
        self.assertEqual(table.at(38), (256 - 115) * 1000 // 256)
        image[rolling_launch_compose.TRIM_AXIS_ADDRESS + 1] = 0
        with self.assertRaisesRegex(ValueError, "axis"):
            rolling_launch_compose.efficiency_table(bytes(image))

    def test_efficiency_input_must_be_one_valid_table(self):
        table = rolling_launch.EfficiencyTable()
        self.assertEqual(
            rolling_launch_compose._validate_efficiency(self.layout, table),
            table.to_bytes(),
        )
        for damaged, message in (
            (table.to_bytes()[:-2], "expected 82"),
            (bytes(2) + table.to_bytes()[2:], "invalid efficiency table"),
        ):
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    rolling_launch_compose._validate_efficiency(self.layout, damaged)


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

    def test_tracked_payloads_and_machine_control_flow_match_sources(self):
        audit = rolling_launch_assembly.validate_instruction_semantics(
            self.layout, self.parsed, self.blobs
        )
        self.assertEqual(audit.instructions, 1539)
        self.assertEqual(audit.delayed_transfers, 94)
        self.assertEqual(audit.pc_relative_references, 92)
        self.assertEqual(audit.direct_branches, 249)
        self.assertEqual(audit.indirect_transfers, 36)

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
        self.assertEqual(sum(item.size for item in ranges), 4318)
        self.assertEqual(self.result.permitted_write_bytes, 4318)
        self.assertEqual(self.result.changed_bytes, 3453)
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

    def test_composition_derives_the_efficiency_table_from_the_base(self):
        span = self.layout.efficiency
        self.assertEqual(
            self.result.data[span.start : span.end],
            rolling_launch_compose.efficiency_table(self.base).to_bytes(),
        )
        table = rolling_launch.EfficiencyTable((1000, *range(999, 959, -1)))
        custom = rolling_launch_compose.compose(
            layout=self.layout, base=self.base, blobs=self.blobs, efficiency=table,
        )
        self.assertEqual(custom.data[span.start : span.end], table.to_bytes())
        self.assertTrue(all(
            span.start <= index < span.end
            for index, (left, right) in enumerate(zip(self.result.data, custom.data))
            if left != right
        ))
        with self.assertRaisesRegex(ValueError, "composed byte"):
            rolling_launch_compose.validate_composed(
                layout=self.layout, base=self.base, composed=custom.data,
                blobs=self.blobs,
            )

    def test_custom_valid_calibration_changes_only_configuration(self):
        calibration = dataclasses.replace(
            rolling_launch.Calibration(),
            mode=rolling_launch.Mode.HOLD,
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
            1539,
        )
        self.assertEqual(
            sum(item.data_bytes for item in self.layout.assembly_units),
            320,
        )
        self.assertEqual(
            sum(item.instruction_count for item in self.parsed.values()),
            1539,
        )


if __name__ == "__main__":
    unittest.main()
