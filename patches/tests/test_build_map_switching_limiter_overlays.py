from pathlib import Path
import tempfile
import unittest

from patches import build_map_switching_limiter as limiter_gate
from patches import build_map_switching_limiter_overlays as overlays
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


class BuildMapSwitchingLimiterOverlaysTest(unittest.TestCase):
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
        cls.source = selector_result.data
        cls.source_sha256 = limiter_gate.sha256(cls.source)
        cls.payloads = limiter_gate.load_gate_payloads(cls.layout)
        cls.results = overlays.build_overlays(
            cls.source,
            layout=cls.layout,
            payloads=cls.payloads,
            source_name="synthetic selector-init readback",
            expected_source_sha256=cls.source_sha256,
            expected_output_sha256=None,
        )

    def test_chain_has_five_ordered_stages(self):
        self.assertEqual(len(self.results), 5)
        self.assertEqual(
            tuple(result.spec.sequence for result in self.results),
            (1, 2, 3, 4, 5),
        )

    def test_hardware_hash_contract_ends_at_combined_gate(self):
        self.assertEqual(
            len(overlays.EXPECTED_OUTPUT_SHA256),
            len(overlays.OVERLAY_SPECS),
        )
        self.assertEqual(
            overlays.EXPECTED_OUTPUT_SHA256[-1],
            limiter_gate.HARDWARE_OUTPUT_SHA256,
        )
        self.assertEqual(
            tuple(result.spec.key for result in self.results),
            (
                "payload_map1",
                "startup_commit",
                "fuel_hook",
                "throttle_cluster_hook",
                "throttle_scalar_hook",
            ),
        )

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

    def test_first_stage_installs_only_inactive_payload_and_storage(self):
        result = self.results[0]
        self.assertEqual(
            result.data[
                limiter_gate.STARTUP_WRAPPER_START :
                limiter_gate.STARTUP_WRAPPER_END
            ],
            self.source[
                limiter_gate.STARTUP_WRAPPER_START :
                limiter_gate.STARTUP_WRAPPER_END
            ],
        )
        self.assertEqual(
            result.data[
                limiter_gate.LIMITER_COMMIT_START :
                limiter_gate.LIMITER_COMMIT_END
            ],
            self.payloads["limiter_commit"],
        )
        self._assert_active_limiter_hooks(result.data, ())

    def test_storage_is_map_1_equivalent_from_first_stage(self):
        for result in self.results:
            for family in limiter_gate._limiter_families(self.layout):
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

    def test_second_stage_activates_startup_commit_without_consumer_hooks(self):
        result = self.results[1]
        self.assertEqual(
            result.data[
                limiter_gate.STARTUP_WRAPPER_START :
                limiter_gate.STARTUP_WRAPPER_END
            ],
            self.payloads["startup_wrapper"],
        )
        self.assertEqual(
            result.data[
                limiter_gate.LIMITER_COMMIT_START :
                limiter_gate.LIMITER_COMMIT_END
            ],
            self.payloads["limiter_commit"],
        )
        self._assert_active_limiter_hooks(result.data, ())

    def test_last_three_stages_activate_one_hook_each(self):
        for result in self.results[2:]:
            with self.subTest(stage=result.spec.sequence):
                self._assert_active_limiter_hooks(
                    result.data, result.spec.active_hook_keys
                )
                self.assertEqual(result.component_changed_bytes, 4)

    def test_each_stage_changes_only_one_component_and_checksums(self):
        checksum_offsets = set(checksums.checksum_byte_offsets())
        previous = self.source
        for result in self.results:
            component = overlays._component_offsets(
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

    def test_stage_permitted_set_sizes_are_exact(self):
        self.assertEqual(
            tuple(result.permitted_write_bytes for result in self.results),
            (356, 116, 24, 24, 24),
        )

    def test_final_stage_equals_combined_limiter_gate(self):
        combined = limiter_gate.build_image(
            self.source,
            layout=self.layout,
            payloads=self.payloads,
            source_name="synthetic selector-init readback",
            expected_source_sha256=self.source_sha256,
        )
        self.assertEqual(self.results[-1].data, combined.data)

    def test_no_non_limiter_runtime_region_is_installed(self):
        final = self.results[-1].data
        for key in (
            "selector_host",
            "adapter_select_helper",
            "lookup_adapters",
            "cruise_feedback_wrapper",
            "cruise_feedback_engine",
        ):
            unit = self.layout.assembly_unit_by_key[key]
            with self.subTest(unit=key):
                self.assertEqual(
                    final[unit.span.start : unit.span.end],
                    self.source[unit.span.start : unit.span.end],
                )

    def test_wrong_source_is_rejected(self):
        with self.assertRaisesRegex(
            overlays.LimiterOverlayError, "source sha256"
        ):
            overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
                expected_output_sha256=None,
            )

    def test_wrong_expected_hash_count_is_rejected(self):
        with self.assertRaisesRegex(
            overlays.LimiterOverlayError,
            "SHA-256 count differs",
        ):
            overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong hash count",
                expected_source_sha256=self.source_sha256,
                expected_output_sha256=("0" * 64,),
            )

    def test_default_paths_encode_mandatory_order(self):
        source = Path(
            "/tmp/example-startup-selector-init-d22a0_readback.bin"
        )
        prefix = overlays.default_output_prefix(source)
        self.assertEqual(prefix, Path("/tmp/example-limiter-overlay"))
        self.assertEqual(
            tuple(path.name for path in overlays.output_paths(prefix)),
            (
                "example-limiter-overlay-01-payload-map1.bin",
                "example-limiter-overlay-02-startup-commit.bin",
                "example-limiter-overlay-03-fuel-hook-4f468.bin",
                "example-limiter-overlay-04-throttle-cluster-hook-75964.bin",
                "example-limiter-overlay-05-throttle-scalar-hook-77bac.bin",
            ),
        )

    def test_writer_creates_exact_images_sidecars_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            paths, manifest, created = overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(created, 11)
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
                overlays._manifest_content(self.results, paths),
            )
            _, _, repeated_created = overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(repeated_created, 0)

    def test_writer_preflights_different_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            first = overlays.output_paths(prefix)[0]
            first.write_bytes(b"different")
            with self.assertRaisesRegex(
                overlays.LimiterOverlayError,
                "existing output differs",
            ):
                overlays.write_overlays(prefix, self.results)
            self.assertFalse(overlays.output_paths(prefix)[1].exists())

    def _assert_active_limiter_hooks(self, image, active_keys):
        active_keys = set(active_keys)
        for hook in self.layout.hooks:
            if hook.key not in limiter_gate.LIMITER_HOOK_KEYS:
                continue
            actual = int.from_bytes(
                image[hook.address : hook.address + hook.width],
                self.layout.byte_order,
            )
            expected = (
                hook.replacement if hook.key in active_keys else hook.stock
            )
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
