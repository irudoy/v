import contextlib
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import unittest

from patches import map_switching_layout
from patches import rolling_launch
from patches import rolling_launch_layout
from tools.can_dashboard import model, recording
from tools.logs import mlvlg
from tools.logs import rolling_launch_audit as audit
from tools.mapkit import rom as romkit

CONFIGURATION = rolling_launch.Calibration(
    mode=rolling_launch.Mode.RPM_HOLD_RETARD,
    enable_mask=0x1E,
    min_speed=0,
    retard_ramp_native=8,
    min_pedal=0,
)
SELECTED_MAP = 3
EXHAUST_SLOT_TARGETS = (140, 140, 128, 140, 140)
RECORDS = 460
BRIDGE_AFTER = 100
FULL = audit.FULL_MASK
RELEASED = rolling_launch.BUTTON_RELEASED
CANCEL = rolling_launch.BUTTON_CANCEL
IDLE_DASHBOARD = 0x02
ACTIVE_DASHBOARD = rolling_launch.ASCD_FEEDBACK_CRUISE_SET | IDLE_DASHBOARD
FAILED_DASHBOARD = rolling_launch.ASCD_FEEDBACK_CRUISE | IDLE_DASHBOARD
CONTEXT_FRAMES = (
    (model.ASCD_BUTTON_ID, 3, "ascd_button_raw"),
    (model.DASHBOARD_STATE_ID, 5, "dashboard_state_raw"),
)


def write_image(path):
    """Write the stock image with a Rolling Launch record and slot surfaces."""
    image = bytearray(romkit.load("JK08A").data)
    configuration = rolling_launch_layout.load_layout().configuration
    image[configuration.start : configuration.end] = CONFIGURATION.to_bytes()
    family = map_switching_layout.load_layout().family_by_key[audit.EXHAUST_FAMILY]
    size = family.width * family.height
    for address, value in zip(family.all_slot_addresses, EXHAUST_SLOT_TARGETS):
        image[address : address + size] = bytes([value]) * size
    Path(path).write_bytes(image)


def base_row():
    return {
        "ascd_button_raw": RELEASED,
        "dashboard_state_raw": IDLE_DASHBOARD,
        "vehicle_speed_kmh": 40.0,
        "coolant_raw": 150,
        "rpm_raw": 200,
        "fuel_inhibit_mask": 0,
        "final_timing_raw": 30,
        "apc_command_raw": 80,
        "app1_raw": 400,
        "bfs_raw": 8000,
        "knock_surface_state": 0,
        "exhaust_cvtc_target_raw": 128,
    }


def put(rows, first, stop, name, value):
    for index in range(first, stop):
        rows[index][name] = value(index) if callable(value) else value


def activate(rows, capture, runtime_end, step=None):
    """Apply the model runtime from one captured RPM word to a record span.

    With a step the RPM follows a cut-limited sawtooth; otherwise the recorded
    RPM words drive the fuel-inhibit hysteresis and the ignition command.
    """
    state = rolling_launch.step(
        rolling_launch.RuntimeState(),
        rolling_launch.Inputs(
            active_index=SELECTED_MAP - 1,
            button=CANCEL,
            rpm_native=rows[capture]["rpm_raw"],
            coolant=rows[capture]["coolant_raw"],
        ),
        CONFIGURATION,
    ).state
    rpm = rows[capture]["rpm_raw"]
    full = False
    for index in range(capture, runtime_end):
        row = rows[index]
        if step is not None:
            row["rpm_raw"] = rpm
        rpm = row["rpm_raw"]
        full = rpm >= state.cut_rpm_native or (
            full and rpm >= state.restore_rpm_native
        )
        row["fuel_inhibit_mask"] = FULL if full else 0
        stock = (audit.APC_COMMAND_BASE - row["final_timing_raw"]) & 0xFF
        row["apc_command_raw"] = rolling_launch.apply_ignition_command(
            state, CONFIGURATION, stock, rpm
        )[1]
        if step is not None:
            rpm += -step if full else step


def scenario():
    """Return three activations, one refused hold, and outside events."""
    rows = [base_row() for _ in range(RECORDS)]
    stock = audit.APC_COMMAND_BASE

    # Moving hold whose sawtooth holds the captured window over three cycles
    # and whose last cycle continues two records past the release.
    lead = (198, 199, 200, 201, 202, 201, 200, 199)
    put(rows, 37, 45, "rpm_raw", lambda i: lead[i - 37])
    activate(rows, capture=45, runtime_end=85, step=1)
    put(rows, 85, 90, "rpm_raw", lambda i: 214 - 2 * (i - 85))
    put(rows, 40, 83, "ascd_button_raw", CANCEL)
    put(rows, 45, 90, "dashboard_state_raw", ACTIVE_DASHBOARD)
    put(rows, 40, 83, "vehicle_speed_kmh", lambda i: 40.0 + 0.25 * (i - 40))

    # Coasting hold at a stock command above the target: the runtime is
    # active, the RPM never reaches the cut, and the stock command remains.
    put(rows, 197, 240, "rpm_raw", lambda i: 182 - (i - 197) // 3)
    put(rows, 197, 240, "final_timing_raw", -7)
    put(rows, 197, 240, "apc_command_raw", (stock + 7) & 0xFF)
    activate(rows, capture=204, runtime_end=232)
    put(rows, 200, 230, "ascd_button_raw", CANCEL)
    put(rows, 204, 240, "dashboard_state_raw", ACTIVE_DASHBOARD)
    put(rows, 200, 230, "vehicle_speed_kmh", 35.5)
    put(rows, 200, 230, "app1_raw", 150)

    # Hold inside the rearm interval, refused with the failed indication.
    put(rows, 260, 266, "ascd_button_raw", CANCEL)
    put(rows, 262, 272, "dashboard_state_raw", FAILED_DASHBOARD)

    # Outside events: one identity difference, a stock full mask, a partial
    # mask, and one SET press.
    rows[300]["apc_command_raw"] = 81
    put(rows, 310, 312, "fuel_inhibit_mask", FULL)
    rows[320]["fuel_inhibit_mask"] = 0x07
    put(rows, 340, 344, "ascd_button_raw", rolling_launch.BUTTON_SET)

    # Hold whose last cut starts after the release.
    lead = (238, 239, 240, 241, 240, 239, 240)
    put(rows, 397, 404, "rpm_raw", lambda i: lead[i - 397])
    activate(rows, capture=403, runtime_end=425, step=2)
    put(rows, 425, 432, "rpm_raw", lambda i: max(240, 250 - 4 * (i - 425)))
    put(rows, 400, 420, "ascd_button_raw", CANCEL)
    put(rows, 403, 432, "dashboard_state_raw", ACTIVE_DASHBOARD)
    put(rows, 400, 420, "vehicle_speed_kmh", lambda i: 44.0 + 0.5 * (i - 400))
    put(rows, 400, 420, "app1_raw", 600)
    return rows


def stock_rpm(row):
    """The stock engine-speed value of the pass that wrote the row's word."""
    return row["rpm_raw"] * 12.5


def capture_from(rows):
    samples = tuple(
        audit.Sample(
            tick=index + 1,
            button=row["ascd_button_raw"],
            dashboard=row["dashboard_state_raw"],
            speed_kmh=row["vehicle_speed_kmh"],
            coolant_raw=row["coolant_raw"],
            rpm_raw=row["rpm_raw"],
            rpm_low=row["rpm_raw"],
            rpm_high=row["rpm_raw"],
            **{name: row[name] for name in audit.TELEMETRY_SOURCES},
        )
        for index, row in enumerate(rows)
    )
    return audit.Capture(Path("synthetic.mlg"), "0" * 64, samples)


def write_log(path, rows, bindings):
    specs = [binding.spec for binding in bindings]
    with Path(path).open("wb") as stream:
        writer = mlvlg.StreamWriter(stream, specs, 1_789_600_000)
        for index, values in enumerate(rows):
            copies = 2 if index == BRIDGE_AFTER else 1
            for _ in range(copies):
                row = []
                for binding in bindings:
                    if binding.source == "date":
                        row.append(1_789_600_000 + index // 100)
                    elif binding.source == "elapsed":
                        row.append(index * model.BASE_TICK_SECONDS)
                    elif binding.source == "tick16":
                        row.append(index + 1)
                    elif binding.source == "schema_verified":
                        row.append(1)
                    elif binding.source == "stock_rpm":
                        row.append(stock_rpm(values))
                    else:
                        row.append(values.get(binding.source, 0))
                writer.write(row, index * model.BASE_TICK_SECONDS)


class ScenarioGenerator(model.DemoGenerator):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        self.index = 0

    def _values(self, elapsed):
        return {**super()._values(elapsed), **self.rows[self.index]}

    def context_frames(self, elapsed):
        values = self.rows[self.index]
        # The stock engine-speed frame follows the previous group.
        rpm = bytearray(8)
        rpm[0:2] = round(stock_rpm(values) * 8).to_bytes(2, "big")
        frames = [model.FrameRecord(model.STOCK_RPM_ID, bytes(rpm), elapsed)]
        for can_id, offset, name in CONTEXT_FRAMES:
            payload = bytearray(8)
            payload[offset] = values[name]
            frames.append(model.FrameRecord(can_id, bytes(payload), elapsed))
        speed = bytearray(8)
        speed[4:6] = round(values["vehicle_speed_kmh"] * 100).to_bytes(2, "big")
        frames.append(model.FrameRecord(model.VEHICLE_SPEED_ID, bytes(speed), elapsed))
        return frames


def write_trace(path, rows):
    generator = ScenarioGenerator(rows)
    lines = [
        ";$FILEVERSION=1.1",
        ";$STARTTIME=46251.0734343518",
        "; Generated by test",
    ]
    number = 1
    for index in range(len(rows)):
        generator.index = index
        tick = index + 1
        elapsed = tick * model.BASE_TICK_SECONDS
        offset_ms = 1000.0 + index * model.BASE_TICK_SECONDS * 1000
        for frame in (
            *generator.context_frames(elapsed),
            *generator.group(tick, elapsed),
        ):
            payload = " ".join(f"{value:02X}" for value in frame.data)
            lines.append(
                f"{number:7d}) {offset_ms:12.4f} Rx   "
                f"{frame.arbitration_id:04X}  {len(frame.data)}  {payload}"
            )
            number += 1
            offset_ms += 0.1
    Path(path).write_text("\n".join(lines) + "\n", encoding="ascii")


class RollingLaunchAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = Path(cls.directory.name)
        cls.image = root / "image.bin"
        cls.log = root / "capture.mlg"
        cls.trace = root / "capture.trc"
        cls.rows = scenario()
        write_image(cls.image)
        write_log(cls.log, cls.rows, recording.build_bindings("tuning"))
        write_trace(cls.trace, cls.rows)
        cls.calibration = audit.load_calibration(cls.image)
        # A capture of exact RPM words pins every bound that the stock
        # engine-speed frame of a recording widens.
        cls.result = audit.audit_capture(
            capture_from(cls.rows), cls.calibration, selected_map=SELECTED_MAP
        )
        cls.stock_result = audit.audit_capture(
            audit.read_mlg(cls.log), cls.calibration, selected_map=SELECTED_MAP
        )

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_calibration_is_read_from_the_image(self):
        calibration = self.calibration
        self.assertEqual(calibration.configuration, CONFIGURATION)
        self.assertEqual(
            calibration.configuration_hex, CONFIGURATION.to_bytes().hex()
        )
        self.assertEqual(calibration.tick_seconds, 0.01024)
        self.assertEqual(len(calibration.exhaust_replays), 5)
        self.assertGreater(150, calibration.exhaust_replays[0].warm_threshold)

    def test_stock_image_without_a_configuration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no valid Rolling Launch"):
            audit.load_calibration(romkit.load("JK08A").path)

    def test_thresholds_follow_the_runtime_model(self):
        slot = SELECTED_MAP - 1
        self.assertEqual(audit.thresholds(CONFIGURATION, slot, 200), (216, 212))
        self.assertEqual(audit.thresholds(CONFIGURATION, slot, 240), (256, 251))
        self.assertEqual(audit.thresholds(CONFIGURATION, slot, 700), (716, 704))
        self.assertIsNone(audit.thresholds(CONFIGURATION, slot, 159))
        self.assertIsNone(audit.thresholds(CONFIGURATION, 0, 200))

    def test_retard_bound_rejects_advance_and_overshoot(self):
        self.assertTrue(audit.within_retard_bound(80, 80, 115))
        self.assertTrue(audit.within_retard_bound(80, 97, 115))
        self.assertTrue(audit.within_retard_bound(80, 115, 115))
        self.assertFalse(audit.within_retard_bound(80, 116, 115))
        self.assertFalse(audit.within_retard_bound(80, 79, 115))
        self.assertTrue(audit.within_retard_bound(117, 117, 115))
        self.assertFalse(audit.within_retard_bound(117, 116, 115))

    def test_clear_masks_after_a_possible_abort_do_not_bound_the_window(self):
        rows = scenario()
        # The minimum-RPM gate can abort the coasting hold from record 215.
        put(rows, 215, 230, "rpm_raw", CONFIGURATION.min_rpm_native - 10)
        result = audit.audit_capture(
            capture_from(rows), self.calibration, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["activation_mask_constraint_count"], [40, 11, 19])
        # A 20-tick timeout can abort the first hold from record 59, which
        # removes the clear records that exclude words 198 and 199.
        short = replace(
            self.calibration,
            configuration=replace(CONFIGURATION, run_timeout_ticks=20),
        )
        result = audit.audit_capture(
            capture_from(scenario()), short, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["activation_mask_constraint_count"][0], 28)
        self.assertEqual(result["activation_captured_rpm_native"][0], [198, 200])

    def test_runs_are_maximal_half_open_intervals(self):
        self.assertEqual(
            audit.runs([True, True, False, True, False, False, True]),
            [(0, 2), (3, 4), (6, 7)],
        )
        self.assertEqual(audit.runs([]), [])

    def test_capture_summary_counts_holds_masks_and_identity(self):
        result = self.result
        self.assertEqual(result["selected_map"], 3)
        self.assertEqual(result["mode"], "rpm_hold_retard")
        self.assertEqual(result["enabled_maps"], [2, 3, 4, 5])
        self.assertEqual(result["target_command"], 115)
        self.assertEqual(result["snapshot_count"], RECORDS)
        self.assertEqual(result["snapshot_gap_count"], 0)
        self.assertEqual(result["span_seconds"], 4.7)
        self.assertEqual(result["exhaust_cvtc_comparison_count"], RECORDS - 1)
        self.assertEqual(
            result["exhaust_cvtc_slot_exact_counts"], [0, 0, RECORDS - 1, 0, 0]
        )
        self.assertEqual(result["cancel_hold_count"], 4)
        self.assertEqual(result["set_hold_count"], 1)
        self.assertEqual(result["active_indication_interval_count"], 3)
        self.assertEqual(result["failed_attempt_record_count"], 10)
        self.assertEqual(result["activation_count"], 3)
        self.assertEqual(result["refused_hold_count"], 1)
        self.assertEqual(result["gesture_tap_count"], 0)
        self.assertEqual(result["full_mask_record_count"], 24)
        self.assertEqual(result["full_mask_outside_record_count"], 2)
        self.assertEqual(result["partial_mask_record_count"], 1)
        self.assertEqual(result["identity_pair_count"], RECORDS)
        self.assertEqual(result["identity_count"], RECORDS - 50)
        self.assertEqual(result["identity_difference_inside_count"], 49)
        self.assertEqual(result["identity_difference_outside_count"], 1)
        self.assertEqual(result["timeout_seconds"], 3.072)
        self.assertEqual(result["longest_hold_seconds"], 0.44)
        self.assertFalse(result["timeout_exercised"])
        self.assertEqual(result["rearm_seconds"], 1.024)
        self.assertEqual(result["minimum_rearm_spacing_seconds"], 1.198)

    def test_activations_bound_the_captured_window_and_the_release(self):
        result = self.result
        self.assertEqual(result["activation_start_seconds"], [0.41, 2.048, 4.096])
        self.assertEqual(result["activation_hold_seconds"], [0.44, 0.307, 0.205])
        self.assertEqual(
            result["activation_active_indication_seconds"], [0.461, 0.369, 0.297]
        )
        self.assertEqual(result["activation_speed_kmh"], [40.0, 35.5, 44.0])
        self.assertEqual(
            result["activation_speed_range_kmh"],
            [[40.0, 50.5], [35.5, 35.5], [44.0, 53.5]],
        )
        self.assertEqual(
            result["activation_app1_range_v"],
            [[2.0, 2.0], [0.75, 0.75], [3.0, 3.0]],
        )
        self.assertEqual(
            result["activation_rpm_range"],
            [[2487.5, 2700.0], [2150.0, 2262.5], [2987.5, 3200.0]],
        )
        # The restore constraint excludes word 199 from the first capture;
        # the coasting hold never reaches a cut, so its hull stays whole.
        self.assertEqual(
            result["activation_captured_rpm_native"],
            [[200, 200], [180, 182], [240, 240]],
        )
        self.assertEqual(
            result["activation_captured_rpm"],
            [[2500.0, 2500.0], [2250.0, 2275.0], [3000.0, 3000.0]],
        )
        self.assertEqual(
            result["activation_cut_rpm"],
            [[2700.0, 2700.0], [2450.0, 2475.0], [3200.0, 3200.0]],
        )
        self.assertEqual(
            result["activation_restore_rpm"],
            [[2650.0, 2650.0], [2400.0, 2425.0], [3137.5, 3137.5]],
        )
        # Every lead record whose RPM hull reaches the captured word can carry
        # the capture pass.
        self.assertEqual(
            result["activation_capture_records"], [[-3, 5], [-3, 4], [-1, 3]]
        )
        self.assertEqual(result["activation_mask_constraint_count"], [40, 26, 19])
        self.assertEqual(result["activation_full_mask_cycles"], [3, 0, 2])
        self.assertEqual(
            result["activation_post_release_full_mask_cycles"], [0, 0, 1]
        )
        self.assertEqual(
            result["activation_full_mask_rpm"],
            [[2650.0, 2700.0], [], [3150.0, 3200.0]],
        )
        self.assertEqual(result["activation_apc_max"], [115, 117, 115])
        self.assertEqual(result["activation_apc_target_records"], [3, 0, 3])
        self.assertEqual(result["activation_apc_outside_bound_records"], [0, 0, 0])
        self.assertEqual(
            result["activation_stock_command_range"],
            [[80, 80], [117, 117], [80, 80]],
        )
        self.assertEqual(result["activation_identity_differences_hold"], [29, 0, 13])
        self.assertEqual(
            result["activation_identity_differences_post_release"], [2, 0, 5]
        )
        # No record after a retarded one reaches the cut with a stock command.
        self.assertEqual(result["activation_exit_records"], [[], [], []])
        self.assertEqual(result["activation_active_ticks_bound"], [[], [], []])
        self.assertEqual(result["activation_release_exit_bound_ms"], [[], [], []])
        self.assertEqual(result["activation_release_full_mask"], [True, False, True])
        self.assertEqual(result["activation_release_clear_records"], [2, 0, 5])
        self.assertEqual(
            result["activation_release_clear_bound_ms"],
            [[10.2, 30.7], [], [41.0, 61.4]],
        )
        # The first release clears the mask at RPM word 213..214, above
        # restore word 212; the last clears it at 250..254, where the
        # hysteresis alone can clear it below restore word 251.
        self.assertEqual(
            result["activation_release_clear_by_window_removal"],
            [True, False, False],
        )
        self.assertEqual(result["activation_rearm_spacing_seconds"], [1.198, 1.741])

    def test_a_stock_command_at_the_cut_bounds_the_end_of_active(self):
        rows = scenario()
        # The first runtime ends after record 84; from record 85 the RPM stays
        # at the 216 cut word with the stock command and a clear mask.
        put(rows, 85, 90, "rpm_raw", 216)
        result = audit.audit_capture(
            capture_from(rows), self.calibration, selected_map=SELECTED_MAP
        )
        # Record 87 is the first whose word and the two before it reach the cut.
        self.assertEqual(result["activation_exit_records"][0], [44, 47])
        self.assertEqual(result["activation_active_ticks_bound"][0], [39, 50])
        self.assertEqual(result["activation_release_exit_bound_ms"][0], [0.0, 51.2])
        # A word below the cut inside the lag window leaves the end unbounded.
        rows[86]["rpm_raw"] = 215
        put(rows, 87, 90, "rpm_raw", 215)
        result = audit.audit_capture(
            capture_from(rows), self.calibration, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["activation_exit_records"][0], [])
        self.assertEqual(result["activation_active_ticks_bound"][0], [])
        # A full mask at the cut does not exclude ACTIVE, so the witness moves
        # to the first clear record.
        rows = scenario()
        put(rows, 85, 90, "rpm_raw", 216)
        rows[88]["fuel_inhibit_mask"] = FULL
        rows[87]["fuel_inhibit_mask"] = FULL
        result = audit.audit_capture(
            capture_from(rows), self.calibration, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["activation_exit_records"][0], [44, 49])

    def test_trace_splits_cancel_frames_into_holds_and_taps(self):
        result = audit.audit_capture(
            audit.read_trc(self.trace), self.calibration, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["trace_cancel_frame_count"], 99)
        self.assertEqual(result["trace_active_frame_count"], 110)
        self.assertEqual(result["trace_failed_frame_count"], 10)
        self.assertEqual(result["trace_gesture_tap_count"], 0)
        self.assertEqual(result["trace_hold_count"], 4)
        self.assertEqual(
            result["trace_hold_start_seconds"], [1.41, 3.048, 3.663, 5.096]
        )
        self.assertEqual(result["trace_hold_seconds"], [0.44, 0.307, 0.061, 0.205])
        self.assertEqual(result["trace_hold_active_frames"], [45, 36, 0, 29])
        self.assertEqual(result["trace_hold_failed_frames"], [0, 0, 10, 0])
        self.assertEqual(
            result["trace_hold_since_previous_release_ms"], [1198.1, 307.2, 1372.2]
        )
        # The dashboard frame follows the button frame of a record by 0.1 ms.
        self.assertEqual(result["trace_activation_active_delay_ms"], [51.3, 41.1, 30.8])
        self.assertEqual(result["trace_activation_inactive_frames_held"], [0, 0, 0])
        # Pages 0 to 10 of the clear group follow the release frame by two and
        # five records plus 0.3 to 1.3 ms.
        self.assertEqual(
            result["trace_activation_release_clear_ms"],
            [[20.8, 21.8], [], [51.5, 52.5]],
        )

    def test_trace_counts_taps_and_an_indication_that_ends_while_held(self):
        rows = scenario()
        # A map-selection tap: CANCEL between two SET frames.
        rows[342]["ascd_button_raw"] = CANCEL
        # The coasting hold loses its indication ten records before release.
        put(rows, 220, 240, "dashboard_state_raw", IDLE_DASHBOARD)
        trace = Path(self.directory.name) / "variant.trc"
        write_trace(trace, rows)
        result = audit.audit_capture(
            audit.read_trc(trace), self.calibration, selected_map=SELECTED_MAP
        )
        self.assertEqual(result["gesture_tap_count"], 1)
        self.assertEqual(result["refused_hold_count"], 2)
        self.assertEqual(result["set_hold_count"], 2)
        self.assertEqual(result["trace_gesture_tap_count"], 1)
        self.assertEqual(result["trace_hold_count"], 4)
        self.assertEqual(result["trace_hold_active_frames"], [45, 16, 0, 29])
        self.assertEqual(result["trace_activation_inactive_frames_held"], [0, 10, 0])

    def test_trace_replay_yields_the_recorded_snapshots(self):
        trace = audit.read_trc(self.trace)
        log = audit.read_mlg(self.log)
        by_tick = {sample.tick: sample for sample in log.samples}
        self.assertGreater(len(trace.samples), RECORDS - 10)
        for sample in trace.samples:
            self.assertEqual(sample, by_tick[sample.tick])
        result = audit.audit_capture(
            trace, self.calibration, selected_map=SELECTED_MAP
        )
        lead = (trace.samples[0].tick - log.samples[0].tick) * 0.01024
        for key, value in self.stock_result.items():
            if key == "activation_start_seconds":
                self.assertEqual(
                    result[key], [round(start - lead, 3) for start in value]
                )
            elif key.startswith("activation_"):
                self.assertEqual(result[key], value, key)

    def test_stock_frame_bounds_each_word_by_the_frames_around_its_snapshot(self):
        stock = audit.read_mlg(self.log)
        self.assertEqual(
            [sample.rpm_raw for sample in stock.samples],
            [row["rpm_raw"] for row in self.rows],
        )
        margin = audit.STOCK_RPM_MARGIN
        for sample, after in zip(stock.samples, [*stock.samples[1:], None]):
            words = [sample.rpm_raw] + ([after.rpm_raw] if after else [])
            self.assertEqual(sample.rpm_low, min(words) - margin)
            self.assertEqual(sample.rpm_high, max(words) + margin)

    def test_stock_frame_figures_span_the_exact_word_figures(self):
        exact = self.result
        stock = self.stock_result
        widened = {
            "activation_rpm_range",
            "activation_captured_rpm_native",
            "activation_captured_rpm",
            "activation_cut_rpm",
            "activation_restore_rpm",
            "activation_capture_records",
            "activation_full_mask_rpm",
            "activation_exit_records",
            "activation_active_ticks_bound",
            "activation_release_exit_bound_ms",
        }
        for key in widened:
            for outer, inner in zip(stock[key], exact[key]):
                with self.subTest(key=key):
                    self.assertTrue(
                        not outer
                        or bool(inner)
                        and outer[0] <= inner[0]
                        and inner[-1] <= outer[-1],
                        (outer, inner),
                    )
        margin = audit.STOCK_RPM_MARGIN
        self.assertEqual(
            stock["activation_captured_rpm_native"],
            [
                [low - margin, high + margin]
                for low, high in exact["activation_captured_rpm_native"]
            ],
        )
        # The widened words no longer prove that the removal of the window
        # clears the first mask.
        self.assertEqual(
            stock["activation_release_clear_by_window_removal"], [False] * 3
        )
        exempt = widened | {
            "capture_name",
            "capture_sha256",
            "activation_release_clear_by_window_removal",
        }
        for key, value in exact.items():
            if key not in exempt:
                with self.subTest(key=key):
                    self.assertEqual(stock[key], value)

    def test_command_line_prints_one_assignment_per_figure(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = audit.main(
                [
                    "--calibration-image",
                    str(self.image),
                    "--map",
                    str(SELECTED_MAP),
                    str(self.log),
                ]
            )
        lines = output.getvalue().splitlines()
        self.assertEqual(status, 0)
        self.assertIn("activation_count = 3", lines)
        self.assertIn(
            "activation_captured_rpm_native = [[192, 208], [172, 190], [232, 248]]",
            lines,
        )
        self.assertIn("timeout_exercised = false", lines)
        self.assertIn('capture_name = "capture.mlg"', lines)
        self.assertIn("gesture_tap_count = 0", lines)
        # Frame times exist only in a TRC.
        self.assertFalse([line for line in lines if line.startswith("trace_")])

    def test_command_line_rejects_a_map_without_rolling_launch(self):
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            status = audit.main(
                ["--calibration-image", str(self.image), "--map", "1", str(self.log)]
            )
        self.assertEqual(status, 1)
        self.assertIn("Map 1 is not enabled", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
