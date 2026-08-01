from pathlib import Path
import unittest

from patches import apply_map_switching as patcher
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model
from patches import upgrade_map_switching_reset as upgrader


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class UpgradeMapSwitchingResetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        cls.blobs = patcher.load_payloads(cls.layout)
        cls.fixed = patcher.patch_image(
            STOCK.read_bytes(),
            layout=cls.layout,
            blobs=cls.blobs,
            source_name="stock JK08A",
        ).data
        startup = cls.layout.assembly_unit_by_key["startup_wrapper"]
        anchor = cls.layout.anchor_by_key["startup_clear_start_stock"]
        old = bytearray(cls.fixed)
        old[startup.span.start : startup.span.end] = (
            upgrader.OLD_STARTUP_BLOB
        )
        old[
            anchor.address : anchor.address + anchor.width
        ] = upgrader.OLD_CLEAR_START.to_bytes(
            anchor.width, cls.layout.byte_order
        )
        cls.old = checksums.recalculate(old)

    def test_upgrade_reproduces_the_fixed_runtime_exactly(self):
        result = upgrader.upgrade_image(
            self.old,
            layout=self.layout,
            blobs=self.blobs,
            source_name="synthetic pre-fix runtime",
        )
        self.assertEqual(result.data, self.fixed)
        self.assertTrue(checksums.verify(result.data).valid)
        self.assertEqual(result.permitted_write_bytes, 120)

    def test_upgrade_preserves_manually_edited_slot_calibration(self):
        family = self.layout.family_by_key["fuel_compensation_main"]
        offset = family.copies[1] + 17
        tuned = bytearray(self.old)
        tuned[offset] ^= 0x03
        tuned = checksums.recalculate(tuned)
        result = upgrader.upgrade_image(
            tuned,
            layout=self.layout,
            blobs=self.blobs,
            source_name="synthetic tuned pre-fix runtime",
        )
        self.assertEqual(result.data[offset], tuned[offset])
        self.assertTrue(checksums.verify(result.data).valid)

    def test_upgrade_preserves_compatible_lower_partition_edit(self):
        offset = 0x00010000
        tuned = bytearray(self.old)
        tuned[offset] ^= 0x03
        tuned = checksums.recalculate(tuned)
        result = upgrader.upgrade_image(
            tuned,
            layout=self.layout,
            blobs=self.blobs,
            source_name="synthetic calibrated pre-fix runtime",
        )
        self.assertEqual(result.data[offset], tuned[offset])
        self.assertTrue(checksums.verify(result.data).valid)

    def test_upgrade_rejects_a_different_runtime_hook(self):
        hook = self.layout.hooks[0]
        corrupt = bytearray(self.old)
        corrupt[hook.address] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(upgrader.UpgradeError, hook.key):
            upgrader.upgrade_image(
                corrupt,
                layout=self.layout,
                blobs=self.blobs,
                source_name="corrupt pre-fix runtime",
            )

    def test_upgrade_rejects_changed_protected_upper_rom(self):
        offset = 0x00080000
        corrupt = bytearray(self.old)
        corrupt[offset] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            upgrader.UpgradeError, "protected upper ROM"
        ):
            upgrader.upgrade_image(
                corrupt,
                layout=self.layout,
                blobs=self.blobs,
                source_name="corrupt protected code",
            )

    def test_upgrade_rejects_unlocked_payload_override(self):
        unit = self.layout.assembly_unit_by_key["selector_host"]
        blobs = dict(self.blobs)
        corrupt = bytearray(blobs[unit.key])
        corrupt[0] ^= 0x01
        blobs[unit.key] = bytes(corrupt)
        with self.assertRaisesRegex(
            upgrader.UpgradeError, "blob SHA-256"
        ):
            upgrader.upgrade_image(
                self.old,
                layout=self.layout,
                blobs=blobs,
                source_name="synthetic pre-fix runtime",
            )

    def test_default_output_path_is_non_destructive(self):
        self.assertEqual(
            upgrader.default_output_path(Path("/tmp/example.bin")),
            Path("/tmp/example-fixed-reset.bin"),
        )


if __name__ == "__main__":
    unittest.main()
