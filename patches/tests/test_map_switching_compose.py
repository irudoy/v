from dataclasses import replace
import hashlib
from pathlib import Path
import unittest

from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]


class MapSwitchingCompositionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_layout = layout_model.load_layout()
        cls.image = layout_model.validate_image(base_layout)
        units = []
        blobs = {}
        for index, unit in enumerate(base_layout.assembly_units, 1):
            blob = bytearray([unit.fill]) * unit.span.size
            blob[0:4] = bytes((0xA0, index, 0x5A, index ^ 0xFF))
            if unit.key == "cruise_feedback_engine":
                counts_offset = (
                    base_layout.feedback.phase_counts_address
                    - unit.span.start
                )
                blob[counts_offset : counts_offset + 2] = bytes(
                    (
                        base_layout.feedback.default_on_frames,
                        base_layout.feedback.default_off_frames,
                    )
                )
            blob = bytes(blob)
            blobs[unit.key] = blob
            units.append(
                replace(
                    unit,
                    expected_sha256=hashlib.sha256(blob).hexdigest(),
                )
            )
        cls.layout = replace(base_layout, assembly_units=tuple(units))
        cls.blobs = blobs

    def test_composition_installs_every_declared_write(self):
        result = composer.compose(self.layout, self.image, self.blobs)
        for unit in self.layout.assembly_units:
            with self.subTest(unit=unit.key):
                self.assertEqual(
                    result.data[unit.span.start : unit.span.end],
                    self.blobs[unit.key],
                )
        for hook in self.layout.hooks:
            with self.subTest(hook=hook.key):
                self.assertEqual(
                    int.from_bytes(
                        result.data[
                            hook.address : hook.address + hook.width
                        ],
                        self.layout.byte_order,
                    ),
                    hook.replacement,
                )

    def test_composition_materializes_identical_maps_and_pointer_tables(self):
        result = composer.compose(self.layout, self.image, self.blobs)
        for family in self.layout.families:
            source = self.image.data[
                family.canonical_address :
                family.canonical_address + family.byte_length
            ]
            with self.subTest(family=family.key):
                for address in family.copies:
                    self.assertEqual(
                        result.data[
                            address : address + family.byte_length
                        ],
                        source,
                    )
                pointers = tuple(
                    int.from_bytes(
                        result.data[address : address + 4],
                        self.layout.byte_order,
                    )
                    for address in range(
                        family.pointer_table,
                        family.pointer_table
                        + self.layout.pointer_table_size,
                        4,
                    )
                )
                self.assertEqual(pointers, family.all_slot_addresses)

    def test_composition_changes_only_declared_write_ranges(self):
        result = composer.compose(self.layout, self.image, self.blobs)
        permitted = {
            offset
            for region in composer.composition_write_ranges(self.layout)
            for offset in range(region.start, region.end)
        }
        changed = {
            offset
            for offset, (stock, composed) in enumerate(
                zip(self.image.data, result.data)
            )
            if stock != composed
        }
        self.assertTrue(changed)
        self.assertLessEqual(changed, permitted)
        self.assertEqual(result.changed_bytes, len(changed))
        self.assertEqual(result.permitted_write_bytes, len(permitted))
        self.assertEqual(result.instruction_count, 386)
        self.assertEqual(result.code_entry_count, 10)
        self.assertFalse(result.checksums_recalculated)

    def test_locked_feedback_counts_are_present_in_composition(self):
        result = composer.compose(self.layout, self.image, self.blobs)
        start = self.layout.feedback.phase_counts_address
        self.assertEqual(result.data[start : start + 2], b"\x0a\x0a")

    def test_composition_requires_the_exact_blob_set(self):
        missing = dict(self.blobs)
        missing.pop(next(iter(missing)))
        with self.assertRaisesRegex(ValueError, "blob set differs"):
            composer.compose(self.layout, self.image, missing)
        extra = dict(self.blobs, undeclared=b"\xff")
        with self.assertRaisesRegex(ValueError, "blob set differs"):
            composer.compose(self.layout, self.image, extra)

    def test_composition_rejects_a_blob_with_wrong_hash(self):
        corrupt = dict(self.blobs)
        key = next(iter(corrupt))
        corrupt[key] = bytes([0x00]) + corrupt[key][1:]
        with self.assertRaisesRegex(ValueError, "blob SHA-256"):
            composer.compose(self.layout, self.image, corrupt)

    def test_validator_rejects_any_byte_outside_the_composition(self):
        result = composer.compose(self.layout, self.image, self.blobs)
        corrupt = bytearray(result.data)
        corrupt[0x10] ^= 0x01
        with self.assertRaisesRegex(ValueError, "composed byte at 0x10"):
            composer.validate_composed(
                self.layout,
                self.image,
                corrupt,
                self.blobs,
            )

    def test_composition_is_deterministic_and_never_writes_a_file(self):
        first = composer.compose(self.layout, self.image, self.blobs)
        second = composer.compose(self.layout, self.image, self.blobs)
        self.assertEqual(first.data, second.data)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.sha256, hashlib.sha256(first.data).hexdigest())
        self.assertFalse(hasattr(composer, "write"))

    def test_ghidra_harness_mirrors_the_authoritative_layout(self):
        authoritative = layout_model.load_layout()
        source = (
            ROOT / "tools/ghidra/EmulateMapSwitchingComposition.java"
        ).read_text()
        compact = "".join(source.split()).replace(",}", "}")

        self.assertIn(f'"{authoritative.source_sha256}"', source)
        for argument, unit in enumerate(authoritative.assembly_units):
            with self.subTest(unit=unit.key):
                expected = (
                    f'newUnitSpec("{unit.key}",{argument},'
                    f"0x{unit.span.start:08X}L,0x{unit.span.size:X},"
                    f'"{unit.expected_sha256}")'
                )
                self.assertIn(expected, compact)

        for hook in authoritative.hooks:
            with self.subTest(hook=hook.key):
                expected = (
                    f'newHookSpec("{hook.key}",'
                    f"0x{hook.address:08X}L,"
                    f"0x{hook.stock:08X}L,"
                    f"0x{hook.replacement:08X}L)"
                )
                self.assertIn(expected, compact)

        for family in authoritative.families:
            with self.subTest(family=family.key):
                copies = ",".join(
                    f"0x{address:08X}L" for address in family.copies
                )
                expected = (
                    f'newFamilySpec("{family.key}",'
                    f"0x{family.canonical_address:08X}L,"
                    f"{family.byte_length},"
                    f"0x{family.pointer_table:08X}L,"
                    f"newlong[]{{{copies}}})"
                )
                self.assertIn(expected, compact)

        self.assertNotIn("Files.write(", source)
        self.assertNotIn("newOutputStream(", source)


if __name__ == "__main__":
    unittest.main()
