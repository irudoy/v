from pathlib import Path
import tempfile
import unittest

from patches import apply_map_switching as runtime
from patches import build_map_switching_limiter as limiter_gate
from patches import build_map_switching_limiter_overlays as limiter_overlays
from patches import build_map_switching_lookup_overlays as lookup_overlays
from patches import build_map_switching_selector_init as selector_init
from patches import build_map_switching_trampoline as trampoline
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class BuildMapSwitchingLookupOverlaysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        marker_source = bytearray(STOCK.read_bytes())
        marker_source[
            limiter_gate.RESET_SELECTOR_LINE_START :
            limiter_gate.RESET_SELECTOR_LINE_END
        ] = bytes(128)
        marker_source[
            limiter_gate.MARKER_LINE_START :
            limiter_gate.MARKER_LINE_END
        ] = bytes(128)
        marker_source = checksums.recalculate(marker_source)
        trampoline_result = trampoline.build_image(
            marker_source,
            layout=cls.layout,
            source_name="synthetic marker readback",
            expected_source_sha256=trampoline.sha256(marker_source),
        )
        selector_result = selector_init.build_image(
            trampoline_result.data,
            layout=cls.layout,
            source_name="synthetic trampoline readback",
            expected_source_sha256=selector_init.sha256(
                trampoline_result.data
            ),
        )
        limiter_results = limiter_overlays.build_overlays(
            selector_result.data,
            layout=cls.layout,
            source_name="synthetic selector-init readback",
            expected_source_sha256=limiter_gate.sha256(
                selector_result.data
            ),
            expected_output_sha256=None,
        )
        cls.source = limiter_results[-1].data
        cls.source_sha256 = limiter_gate.sha256(cls.source)
        cls.payloads = runtime.load_payloads(cls.layout)
        cls.results = lookup_overlays.build_overlays(
            cls.source,
            layout=cls.layout,
            payloads=cls.payloads,
            source_name="synthetic limiter Overlay 05",
            expected_source_sha256=cls.source_sha256,
            expected_output_sha256=None,
        )

    def test_chain_has_nine_ordered_stages(self):
        self.assertEqual(len(self.results), 9)
        self.assertEqual(
            tuple(result.spec.sequence for result in self.results),
            tuple(range(6, 15)),
        )

    def test_hook_order_places_startup_lookup_last(self):
        self.assertEqual(
            tuple(
                result.spec.hook_key
                for result in self.results
                if result.spec.hook_key is not None
            ),
            lookup_overlays.LOOKUP_HOOK_ORDER,
        )
        self.assertEqual(
            lookup_overlays.LOOKUP_HOOK_ORDER[-1],
            "fuel_compensation_lookup_2c648",
        )

    def test_hardware_hash_contract_has_one_entry_per_stage(self):
        self.assertEqual(
            len(lookup_overlays.EXPECTED_OUTPUT_SHA256),
            len(lookup_overlays.OVERLAY_SPECS),
        )
        self.assertEqual(len(set(lookup_overlays.EXPECTED_OUTPUT_SHA256)), 9)
        for digest in lookup_overlays.EXPECTED_OUTPUT_SHA256:
            self.assertEqual(len(digest), 64)
            int(digest, 16)

    def test_every_stage_is_a_complete_checksum_valid_rom(self):
        for result in self.results:
            with self.subTest(stage=result.spec.sequence):
                self.assertEqual(len(result.data), limiter_gate.ROM_SIZE)
                verification = checksums.verify(result.data)
                self.assertTrue(verification.valid)
                self.assertEqual(
                    verification.stored, verification.calculated
                )

    def test_hash_chain_uses_previous_planned_image(self):
        expected_source = self.source_sha256
        for result in self.results:
            with self.subTest(stage=result.spec.sequence):
                self.assertEqual(result.source_sha256, expected_source)
                expected_source = result.output_sha256

    def test_first_stage_installs_inactive_payload_and_storage(self):
        result = self.results[0]
        for key in lookup_overlays.LOOKUP_UNIT_KEYS:
            unit = self.layout.assembly_unit_by_key[key]
            self.assertEqual(
                result.data[unit.span.start : unit.span.end],
                self.payloads[key],
            )
        self._assert_active_lookup_hooks(result.data, ())

    def test_lookup_storage_is_map_1_equivalent_from_first_stage(self):
        for result in self.results:
            for family in lookup_overlays._lookup_families(self.layout):
                map_1 = self.source[
                    family.canonical_address :
                    family.canonical_address + family.byte_length
                ]
                for address in family.copies:
                    with self.subTest(
                        stage=result.spec.sequence,
                        family=family.key,
                        address=address,
                    ):
                        self.assertEqual(
                            result.data[
                                address : address + family.byte_length
                            ],
                            map_1,
                        )
                expected_pointers = b"".join(
                    address.to_bytes(4, self.layout.byte_order)
                    for address in family.all_slot_addresses
                )
                start = family.pointer_table
                self.assertEqual(
                    result.data[
                        start : start + self.layout.pointer_table_size
                    ],
                    expected_pointers,
                )

    def test_last_eight_stages_activate_one_lookup_hook_each(self):
        for result in self.results[1:]:
            with self.subTest(stage=result.spec.sequence):
                self._assert_active_lookup_hooks(
                    result.data, result.spec.active_hook_keys
                )
                self.assertEqual(result.component_changed_bytes, 3)

    def test_existing_startup_and_limiter_runtime_remain_active(self):
        persistent = {
            "startup_initializer",
            *limiter_gate.LIMITER_HOOK_KEYS,
        }
        for result in self.results:
            for hook in self.layout.hooks:
                if hook.key not in persistent:
                    continue
                actual = int.from_bytes(
                    result.data[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                self.assertEqual(actual, hook.replacement)

    def test_selector_and_feedback_units_remain_absent(self):
        for result in self.results:
            for key in lookup_overlays.PASSIVE_UNIT_KEYS:
                unit = self.layout.assembly_unit_by_key[key]
                with self.subTest(stage=result.spec.sequence, unit=key):
                    self.assertEqual(
                        result.data[unit.span.start : unit.span.end],
                        self.source[unit.span.start : unit.span.end],
                    )

    def test_each_stage_changes_only_one_component_and_checksums(self):
        checksum_offsets = set(checksums.checksum_byte_offsets())
        previous = self.source
        for result in self.results:
            component = lookup_overlays._component_offsets(
                self.layout, result.spec
            )
            changed = {
                offset
                for offset, (before, after) in enumerate(
                    zip(previous, result.data)
                )
                if before != after
            }
            with self.subTest(stage=result.spec.sequence):
                self.assertEqual(
                    changed - component - checksum_offsets, set()
                )
                self.assertEqual(
                    result.component_changed_bytes,
                    len(changed & component),
                )
                self.assertEqual(
                    result.checksum_changed_bytes,
                    len(changed & checksum_offsets),
                )
                self.assertEqual(
                    result.permitted_write_bytes,
                    len(component | checksum_offsets),
                )
            previous = result.data
        self.assertEqual(
            tuple(result.permitted_write_bytes for result in self.results),
            (4668, 24, 24, 24, 24, 24, 24, 24, 24),
        )

    def test_final_stage_equals_combined_lookup_endpoint(self):
        self.assertEqual(
            self.results[-1].data,
            lookup_overlays._build_final_endpoint(
                self.layout, self.source, self.payloads
            ),
        )

    def test_wrong_source_is_rejected(self):
        with self.assertRaisesRegex(
            lookup_overlays.LookupOverlayError, "source sha256"
        ):
            lookup_overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
                expected_output_sha256=None,
            )

    def test_wrong_expected_hash_count_is_rejected(self):
        with self.assertRaisesRegex(
            lookup_overlays.LookupOverlayError,
            "SHA-256 count differs",
        ):
            lookup_overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong hash count",
                expected_source_sha256=self.source_sha256,
                expected_output_sha256=("0" * 64,),
            )

    def test_default_paths_continue_global_stage_numbers(self):
        source = Path(
            "/tmp/example-limiter-overlay-05-throttle-scalar-hook-77bac.bin"
        )
        prefix = lookup_overlays.default_output_prefix(source)
        self.assertEqual(
            prefix, Path("/tmp/example-map-switching-overlay-v2")
        )
        self.assertEqual(
            tuple(path.name for path in lookup_overlays.output_paths(prefix)),
            (
                "example-map-switching-overlay-v2-06-lookup-payload-map1.bin",
                "example-map-switching-overlay-v2-07-overrun-cut-hook-4fdd0.bin",
                "example-map-switching-overlay-v2-08-overrun-restore-hook-50258.bin",
                "example-map-switching-overlay-v2-09-ignition-hook-496c0.bin",
                "example-map-switching-overlay-v2-10-ignition-hook-4e474.bin",
                "example-map-switching-overlay-v2-11-ignition-hook-4e58c.bin",
                "example-map-switching-overlay-v2-12-fuel-comp-hook-3c388.bin",
                "example-map-switching-overlay-v2-13-fuel-targets-hook-c0020.bin",
                "example-map-switching-overlay-v2-14-fuel-comp-startup-hook-2cf1c.bin",
            ),
        )

    def test_writer_creates_exact_images_sidecars_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            paths, manifest, created = lookup_overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(created, 19)
            for result, path in zip(self.results, paths):
                self.assertEqual(path.read_bytes(), result.data)
                self.assertEqual(
                    path.with_name(f"{path.name}.md5").read_text(
                        encoding="ascii"
                    ),
                    f"{result.output_md5} *{path.name}\n",
                )
            self.assertEqual(
                manifest.read_text(encoding="ascii"),
                lookup_overlays._manifest_content(self.results, paths),
            )
            _, _, repeated_created = lookup_overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(repeated_created, 0)

    def test_writer_preflights_different_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            first = lookup_overlays.output_paths(prefix)[0]
            first.write_bytes(b"different")
            with self.assertRaisesRegex(
                lookup_overlays.LookupOverlayError,
                "existing output differs",
            ):
                lookup_overlays.write_overlays(prefix, self.results)
            self.assertFalse(lookup_overlays.output_paths(prefix)[1].exists())

    def _assert_active_lookup_hooks(self, image, active_keys):
        active_keys = set(active_keys)
        for key in lookup_overlays.LOOKUP_HOOK_ORDER:
            hook = next(
                hook for hook in self.layout.hooks if hook.key == key
            )
            actual = int.from_bytes(
                image[hook.address : hook.address + hook.width],
                self.layout.byte_order,
            )
            expected = hook.replacement if key in active_keys else hook.stock
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
