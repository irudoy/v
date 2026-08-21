import unittest

from patches import apply_can_telemetry
from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_layout
from patches import jk08a_checksums as checksums
from patches import rolling_launch_compose


class ApplyCanTelemetryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = can_telemetry_layout.load_layout()
        cls.payloads = can_telemetry_assembly.load_payloads(cls.layout)
        cls.base = bytes(checksums.recalculate(
            rolling_launch_compose.compose().data
        ))

    def apply(self, configuration=None, source=None):
        return apply_can_telemetry.patch_image(
            self.base if source is None else source,
            configuration=configuration,
            telemetry_layout=self.layout,
            telemetry_payloads=self.payloads,
            expected_source_sha256=None,
        )

    def test_disabled_and_enabled_outputs_are_checksum_valid(self):
        configurations = (
            can_telemetry.default_configuration(),
            can_telemetry.Configuration(True, 0x6F0, "tuning", 1),
            can_telemetry.Configuration(True, 0x6EF, "tuning", 5),
        )
        for configuration in configurations:
            with self.subTest(configuration=configuration):
                result = self.apply(configuration)
                self.assertTrue(checksums.verify(result.data).valid)
                self.assertEqual(
                    result.configuration, configuration.to_bytes()
                )
                self.assertEqual(
                    result.mailbox_record, configuration.mailbox_record()
                )
                self.assertEqual(result.instruction_count, 482)
                self.assertEqual(result.code_entry_count, 8)
                self.assertGreater(result.final_changed_bytes, 1100)

    def test_output_changes_only_closed_write_set_and_checksums(self):
        result = self.apply(
            can_telemetry.Configuration(True, 0x6F0, "tuning", 1)
        )
        permitted, _ = apply_can_telemetry._final_write_offsets(self.layout)
        changed = {
            index
            for index, pair in enumerate(zip(self.base, result.data))
            if pair[0] != pair[1]
        }
        self.assertEqual(changed - permitted, set())
        self.assertEqual(result.final_changed_bytes, len(changed))
        self.assertEqual(result.permitted_write_bytes, len(permitted))

    def test_source_checksum_payload_hook_config_and_reserve_are_guarded(self):
        invalid_checksum = bytearray(self.base)
        invalid_checksum[0x9000] ^= 1
        with self.assertRaisesRegex(
            apply_can_telemetry.PatchError, "checksum mismatch"
        ):
            self.apply(source=invalid_checksum)

        cases = {}
        unit = self.layout.assembly_units[0]
        occupied_unit = bytearray(self.base)
        occupied_unit[unit.span.start] = 0
        cases["unit"] = occupied_unit
        hook = self.layout.hooks[0]
        occupied_hook = bytearray(self.base)
        occupied_hook[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, self.layout.byte_order)
        )
        cases["hook"] = occupied_hook
        occupied_configuration = bytearray(self.base)
        occupied_configuration[self.layout.configuration.start] = 0
        cases["configuration"] = occupied_configuration
        occupied_reserve = bytearray(self.base)
        occupied_reserve[self.layout.reserved_rom.start] = 0
        cases["reserve"] = occupied_reserve
        for name, source in cases.items():
            with self.subTest(name=name):
                source = bytes(checksums.recalculate(source))
                with self.assertRaises(apply_can_telemetry.PatchError):
                    self.apply(source=source)

    def test_partial_rolling_launch_base_is_rejected(self):
        source = bytearray(self.base)
        source[0xD3900] ^= 1
        source = bytes(checksums.recalculate(source))
        with self.assertRaisesRegex(
            apply_can_telemetry.PatchError, "Rolling Launch unit"
        ):
            self.apply(source=source)


if __name__ == "__main__":
    unittest.main()
