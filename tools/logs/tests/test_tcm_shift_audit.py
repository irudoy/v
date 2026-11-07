import contextlib
import csv
import io
from pathlib import Path
import tempfile
import tomllib
import unittest

from tools.can_dashboard import model
from tools.logs import tcm_shift_audit as audit
from tools.logs.torque_scale_audit import RE5R05A_RATIOS

TICK_MS = 10.24
TICKS = 200
DEFAULT_B = 1820
WORD_A = 4094
PRE_LIMITER = 2000
FLOOR_TICKS = range(55, 59)
RAISE_TICK = 62
STATUS_TICKS = range(54, 67)
RAMP_START = 67
RAMP_STEP = 41
DOWN_TARGET, DOWN_CURRENT, DOWN_IDLE = 50, 70, 75
UP_TARGET, UP_CURRENT, UP_IDLE = 120, 130, 135
BURST_TICKS = range(121, 127)
DIVERGED_PASSES = range(123, 126)
M3, M4 = 0x90, 0x98
DRIVE = 0x20
# 0xFFFF1866 follows the 0x177 byte 4 of the TCM group two passes earlier,
# except one cleared pass, and then decays without byte 4.
REDUCTION_LAG = 2
CLEARED_TICK = 125
DECAY = {131: 0x2080, 132: 0x1800, 133: 0x1000, 134: 0x0800}
# 0xFFFF23C2: a run after the burst with a timing dip, one cut short by
# another page configuration, and one that follows no run.
TRANSITION_BURST = range(124, 132)
TIMING_DIP = range(125, 129)
OTHER_CONFIGURATION = range(188, 193)
TRANSITION_CUT = range(185, 188)
TRANSITION_OTHER = range(194, 198)
GROUP_OFFSET_MS = 1.4


def word_b(tick):
    if tick < RAMP_START:
        return DEFAULT_B
    return min(DEFAULT_B, 1000 + RAMP_STEP * (tick - RAMP_START))


def reduction_byte(tick):
    return 0x30 + tick - BURST_TICKS[0] if tick in BURST_TICKS else 0


def reduction_state(tick):
    if tick == CLEARED_TICK:
        return 0
    return DECAY.get(tick, reduction_byte(tick - REDUCTION_LAG) << 8)


def transition_state(tick):
    if tick in TRANSITION_BURST:
        return (TRANSITION_BURST[-1] + 1 - tick) << 8
    if tick in TRANSITION_CUT or tick in TRANSITION_OTHER:
        return 0x0300
    return 0


def row(tick):
    """Telemetry values and TCM fields of one pass of the scenario."""
    if tick < DOWN_TARGET:
        target, current, code = 4, 4, audit.IDLE_SHIFT_CODE
    elif tick < DOWN_CURRENT:
        target, current, code = 3, 4, 9 << 3
    elif tick < UP_TARGET:
        target, current, code = 3, 3, 9 << 3 if tick < DOWN_IDLE else audit.IDLE_SHIFT_CODE
    elif tick < UP_CURRENT:
        target, current, code = 4, 3, 2 << 3
    else:
        target, current, code = 4, 4, 2 << 3 if tick < UP_IDLE else audit.IDLE_SHIFT_CODE
    request = PRE_LIMITER
    if tick in FLOOR_TICKS:
        request = 500
    elif tick == RAISE_TICK:
        request = PRE_LIMITER + 100
    elif RAMP_START < tick <= RAMP_START + 30:
        request = min(PRE_LIMITER, audit.unpack(word_b(tick - 1)))
    closed = DOWN_TARGET <= tick <= DOWN_IDLE
    return {
        "app1_raw": 100 if closed else 400,
        "engine_torque_state_raw": 1000,
        "throttle_request_bounded_raw": request,
        "throttle_target_shared_raw": 600 + (50 if tick == 60 else 0),
        "final_timing_raw": 20 if tick in TIMING_DIP else 25,
        "fuel_inhibit_mask": 0,
        "transmission_reduction_state_raw": reduction_state(tick),
        "torque_transition_state_raw": transition_state(tick),
        "telemetry_page_configuration": 1 if tick in OTHER_CONFIGURATION else 0,
        "target": target,
        "current": current,
        "code": code,
        "status": audit.STATUS_EPISODE_VALUE if tick in STATUS_TICKS else 0,
        "word_b": word_b(tick),
        "reduction": reduction_byte(tick),
        "selector": M4 if target == 4 else M3,
    }


DRIVE_TICKS = 160
# Downshifts in D: pressed pedal 4-3, full pedal 3-2, closed pedal 2-1, each
# as (target change, current reaches the target, idle code, APP1, code).
DRIVE_SHIFTS = ((30, 40, 45, 500, 9), (80, 90, 95, 950, 6), (130, 138, 142, 100, 4))
# Reduction runs without byte 4, and transition runs two passes after the
# first, inside the second, and four passes after the third: only the first
# two lie within the binding window.
DRIVE_REDUCTIONS = (range(60, 63), range(110, 116), range(150, 152))
DRIVE_TRANSITIONS = (range(64, 66), range(112, 117), range(155, 157))


def drive_row(tick):
    """A D scenario without bursts or status episodes."""
    gear, code, app1 = 4, audit.IDLE_SHIFT_CODE, 400
    target = current = gear
    for start, reached, idle, pedal, shift_code in DRIVE_SHIFTS:
        if tick >= start - 5:
            app1 = pedal
        if tick >= start:
            if tick < reached:
                target = current - 1
            else:
                current -= 1
                target = current
            code = shift_code << 3 if tick < idle else audit.IDLE_SHIFT_CODE
    return {
        "app1_raw": app1,
        "engine_torque_state_raw": 1000,
        "throttle_request_bounded_raw": PRE_LIMITER,
        "throttle_target_shared_raw": 600,
        "final_timing_raw": 25,
        "fuel_inhibit_mask": 0,
        "transmission_reduction_state_raw":
            0x0500 if any(tick in run for run in DRIVE_REDUCTIONS) else 0,
        "torque_transition_state_raw":
            0x0200 if any(tick in run for run in DRIVE_TRANSITIONS) else 0,
        "telemetry_page_configuration": 0,
        "target": target,
        "current": current,
        "code": code,
        "status": 0,
        "word_b": DEFAULT_B,
        "reduction": 0,
        "selector": DRIVE,
    }


class Generator(model.DemoGenerator):
    def __init__(self):
        super().__init__()
        self.values = {}

    def _values(self, elapsed):
        return {**super()._values(elapsed), **self.values}


def tcm_frames(tick, values):
    b = values["word_b"]
    gear = bytes([
        WORD_A >> 4,
        (WORD_A & 0x0F) << 4 | b >> 8,
        b & 0xFF,
        values["target"] << 4 | values["current"],
        values["status"] << 5 | tick & 0x0F,
        0, 0, 0,
    ])
    output = round(2000 / RE5R05A_RATIOS[values["current"]])
    speed = output.to_bytes(2, "big") + (2000).to_bytes(2, "big") + bytes(4)
    phase = bytes([0, 0, values["current"] - 1, 0, values["reduction"], values["code"], 0, 0])
    return ((audit.GEAR_ID, gear), (audit.SPEED_ID, speed), (audit.PHASE_ID, phase))


def ecu_frames(tick, values):
    """Frames 0x180 and 0x160 of pass `tick`, sent after the next first page."""
    actual = audit.pack(1000)
    parallel = actual + 50 if tick in DIVERGED_PASSES else actual
    request = audit.pack(PRE_LIMITER)
    # The pedal word that the TCM receives follows APP1 in the scenarios.
    pedal = values["app1_raw"]
    return (
        (audit.ACTUAL_ID, bytes([0, 0, actual >> 4, (actual & 0x0F) << 4 | request >> 8,
                                 request & 0xFF, pedal >> 2, (pedal & 0x03) << 6, 0])),
        (audit.LIMITED_ID, bytes([request >> 4, (request & 0x0F) << 4 | parallel >> 8,
                                  parallel & 0xFF, 0, 0, 0, 0, 0])),
    )


def write_trace(path, *, mutate=None, rows=row, ticks=TICKS):
    generator = Generator()
    lines = [";$FILEVERSION=1.1", ";$STARTTIME=46251.0734343518", "; Generated by test"]
    number = 1
    previous = None
    for tick in range(ticks):
        values = rows(tick)
        generator.values = values
        offset_ms = 1000.0 + tick * TICK_MS
        frames = [(frame.arbitration_id, frame.data) for frame in generator.group(tick + 1)]
        if previous is not None:
            frames.extend(ecu_frames(tick - 1, previous))
        frames.append((audit.SELECTOR_ID, bytes([values["selector"], 0, 0, 0, 0, 0, 0, 0])))
        frames.extend(tcm_frames(tick, values))
        if mutate is not None:
            frames = mutate(tick, frames)
        for can_id, data in frames:
            payload = " ".join(f"{value:02X}" for value in data)
            lines.append(f"{number:7d}) {offset_ms:12.4f} Rx   {can_id:04X}  {len(data)}  {payload}")
            number += 1
            offset_ms += 0.1
        previous = values
    Path(path).write_text("\n".join(lines) + "\n", encoding="ascii")


class PackingTest(unittest.TestCase):
    def test_pack_truncates_toward_zero_and_clamps(self):
        self.assertEqual(audit.pack(0), 800)
        self.assertEqual(audit.pack(9), 801)
        self.assertEqual(audit.pack(-9), 799)
        self.assertEqual(audit.pack(-4000), 0)
        self.assertEqual(audit.pack(-5000), 0)
        self.assertEqual(audit.pack(16470), 4094)
        self.assertEqual(audit.pack(20000), 4094)

    def test_unpack_inverts_whole_counts(self):
        for word in (0, 800, 1820, 4094):
            self.assertEqual(audit.pack(audit.unpack(word)), word)
        self.assertEqual(audit.unpack(1820), 5100)
        self.assertEqual(audit.unpack(940), 700)

    def test_shift_code_index_uses_bit_7_or_bits_3_to_6(self):
        self.assertEqual(audit.shift_code_index(0x78), 15)
        self.assertEqual(audit.shift_code_index(0x48), 9)
        self.assertEqual(audit.shift_code_index(0x80), 15)
        self.assertEqual(audit.shift_code_index(0x07), 0)

    def test_mechanical_gear_matches_the_inverse_ratio(self):
        self.assertEqual(audit.mechanical_gear(2000, 2000), 4)
        self.assertEqual(audit.mechanical_gear(1308, 2000), 3)
        self.assertEqual(audit.mechanical_gear(1500, 2000), 0)
        self.assertIsNone(audit.mechanical_gear(1000, 0))

    def test_hex_prints_as_a_toml_integer(self):
        self.assertEqual(str(audit.Hex(0xFFFF3A2E)), "0xFFFF3A2E")
        line = audit.result_lines({"address": audit.Hex(0x144F2)})[0]
        self.assertEqual(tomllib.loads(line), {"address": 0x144F2})


class FrameTest(unittest.TestCase):
    def frame(self, reduction):
        return audit.TcmFrame(0.0, bytes(8), bytes(8), bytes([0, 0, 0, 0, reduction, 0x78]), None)

    def test_bursts_tolerate_one_zero_frame(self):
        tcm = [self.frame(value) for value in (0, 5, 0, 5, 0, 0, 5, 5, 0)]
        self.assertEqual(audit.reduction_bursts(tcm), [(1, 3), (6, 7)])

    def test_tcm_fields_follow_the_frame_layout(self):
        frame = audit.TcmFrame(
            0.0,
            bytes([0xFF, 0xE7, 0x1C, 0x43, 0x6B, 0, 0, 0]),
            bytes([0x07, 0xD0, 0x07, 0xD0, 0, 0, 0, 0]),
            bytes([0, 0, 0x02, 0, 0x30, 0x10, 0, 0]),
            M4,
        )
        self.assertEqual((frame.word_a, frame.word_b), (4094, 0x71C))
        self.assertEqual((frame.target, frame.current), (4, 3))
        self.assertEqual((frame.status, frame.counter), (3, 11))
        self.assertEqual((frame.output_speed, frame.turbine_speed), (2000, 2000))
        self.assertEqual((frame.gear_phase, frame.reduction, frame.shift_code), (2, 0x30, 0x10))


class InterfaceCodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit.STOCK_ROM.read_bytes()
        cls.code = audit.interface_code(cls.data)

    def test_stock_path_addresses(self):
        code = self.code
        self.assertEqual(code["code_status_field"], 0xFFFF3A2E)
        self.assertEqual(code["code_word_fields"], [0xFFFF3F8C, 0xFFFF3F8E])
        self.assertEqual(code["code_word_limits"], [0xFFFF2872, 0xFFFF2874])
        self.assertEqual(code["code_word_b_latch"], 0xFFFF2770)
        self.assertEqual(code["code_status_latch"], 0xFFFF418F)
        self.assertEqual(code["code_hold_byte"], 0xFFFF4413)
        self.assertEqual(code["code_request_bounds"], [0xFFFF3480, 0xFFFF3484])
        self.assertEqual(code["code_shared_request"], 0xFFFF19C6)
        self.assertEqual(code["code_reduction_copy"], 0xFFFF3373)

    def test_stock_tables_and_options(self):
        code = self.code
        self.assertEqual((code["code_word_offset"], code["code_word_cap"]), (-4000, 0x7FFF))
        self.assertEqual(code["code_hold_passes"], 30)
        self.assertEqual(code["code_hold_s"], 0.3072)
        self.assertEqual(code["code_floor_values"][9], 500)
        self.assertEqual(code["code_floor_passes"][9], 30)
        self.assertEqual(code["code_floor_values"][15], -32768)
        self.assertEqual(code["code_floor_gate_limit"], [0x94B6, 91])
        self.assertTrue(code["code_path_selected"])
        self.assertTrue(code["code_word_b_term_enabled"])
        self.assertTrue(code["code_bounds_enabled"])
        self.assertTrue(code["code_reduction_copy_enabled"])

    def test_a_changed_instruction_is_rejected(self):
        data = bytearray(self.data)
        data[0x7914E] ^= 0x01
        with self.assertRaisesRegex(ValueError, "0x79148"):
            audit.interface_code(bytes(data))

    def test_a_changed_literal_is_rejected(self):
        data = bytearray(self.data)
        # The literal of mov.l at 0x77258, the field block, no longer matches 0xC47F6.
        literal = ((0x77258 + 4) & ~3) + (audit._u16(self.data, 0x77258) & 0xFF) * 4
        data[literal + 3] ^= 0x01
        with self.assertRaisesRegex(ValueError, "field block"):
            audit.interface_code(bytes(data))

    def test_options_follow_the_rom_bytes(self):
        data = bytearray(self.data)
        data[0x870C] |= 0x80
        data[0x8B08] &= 0xFE
        code = audit.interface_code(bytes(data))
        self.assertFalse(code["code_path_selected"])
        self.assertFalse(code["code_word_b_term_enabled"])


class CaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.trace = Path(cls.directory.name) / "capture.trc"
        write_trace(cls.trace)
        cls.code = audit.interface_code(audit.STOCK_ROM.read_bytes())
        cls.result = audit.audit_capture(cls.trace, cls.code)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_frame_fields(self):
        result = self.result
        self.assertEqual(result["tcm_group_count"], TICKS)
        self.assertEqual(result["counter_step_count"], TICKS - 1)
        self.assertEqual(result["status_bit4_count"], 0)
        self.assertEqual(result["status_values"], [0, 3])
        self.assertEqual(result["status_value_3_frames"], len(STATUS_TICKS))
        self.assertEqual(result["word_a_values"], [WORD_A])
        self.assertEqual(result["word_b_default"], DEFAULT_B)
        self.assertEqual(result["word_b_other_outside_episodes"], 0)
        self.assertGreater(result["snapshot_count"], TICKS - 10)

    def test_shift_events_and_codes(self):
        result = self.result
        self.assertEqual(result["event_count"], 2)
        self.assertEqual((result["upshift_count"], result["downshift_count"]), (1, 1))
        self.assertEqual(result["shift_codes"], {"4-3": {9 << 3}, "3-4": {2 << 3}})
        self.assertEqual(result["event_shift_code_constant_count"], 2)
        self.assertEqual(result["shift_code_changes_outside_events"], 0)
        self.assertEqual(result["downshifts"][0]["episode"], True)

    def test_status_episode(self):
        (episode,) = self.result["episodes"]
        self.assertEqual(episode["shift"], "4-3")
        self.assertEqual(episode["selector"], M3)
        self.assertEqual(episode["value_frames"], len(STATUS_TICKS))
        self.assertAlmostEqual(episode["start_delay_s"], 4 * TICK_MS / 1000)
        self.assertAlmostEqual(episode["seconds"], 12 * TICK_MS / 1000)
        self.assertAlmostEqual(episode["end_lead_s"], 4 * TICK_MS / 1000)
        self.assertEqual(episode["word_b_during"], [DEFAULT_B])
        self.assertEqual(episode["word_b_restart"], 1000)
        self.assertEqual(episode["word_b_steps"], [RAMP_STEP])
        self.assertAlmostEqual(episode["ramp_s"], 21 * TICK_MS / 1000)
        self.assertEqual(episode["shift_code"], 9)
        self.assertEqual(episode["floor_passes"], len(FLOOR_TICKS))
        self.assertEqual(episode["floor_tick_span"], len(FLOOR_TICKS))
        (floor_start,) = episode["floor_start_s"]
        self.assertAlmostEqual(floor_start, (1000 + FLOOR_TICKS[0] * TICK_MS) / 1000, places=3)
        self.assertEqual(episode["floor_request_range"], [PRE_LIMITER, PRE_LIMITER])
        # Four floor passes and five hold passes below the pre-limiter request
        # and one pass above it.
        self.assertEqual(episode["request_mismatch_passes"], 10)

    def test_request_word_and_word_b_binding(self):
        result = self.result
        self.assertEqual(result["request_mismatch_passes"], 10)
        self.assertEqual(result["request_mismatch_above_passes"], 1)
        self.assertEqual(result["request_mismatch_runs"], 3)
        self.assertEqual(result["request_mismatch_outside_episodes"], 0)
        self.assertEqual(result["request_mismatch_without_status"], 0)
        # Pass 72 follows the last status frame, sent 1.4 ms into pass 66.
        self.assertEqual(result["request_mismatch_status_lag_max_s"], round((6 * TICK_MS - 1.4) / 1000, 3))
        self.assertEqual(result["binding_passes"], 5)
        self.assertEqual(result["binding_equal_passes"], 5)
        self.assertEqual(result["limited_equals_request_passes"], result["pass_count"])

    def test_burst_divergence(self):
        result = self.result
        self.assertEqual(result["burst_count"], 1)
        self.assertEqual(result["burst_frames"], len(BURST_TICKS))
        self.assertEqual(result["burst_upshift_divergence_count"], 1)
        self.assertEqual(result["divergence_passes"], len(DIVERGED_PASSES))
        self.assertEqual(result["divergence_in_burst_passes"], len(DIVERGED_PASSES))
        (upshift,) = result["burst_upshifts"]
        self.assertEqual(upshift["shift"], "3-4")
        self.assertAlmostEqual(upshift["onset_lag_s"], (2 * TICK_MS - 1.4) / 1000)
        self.assertEqual(upshift["word_gap_min"], -50)

    def test_gear_signal(self):
        result = self.result
        self.assertEqual(result["phase_equal_frames"], result["phase_frames"])
        self.assertEqual(result["ratio_matched_frames"], result["ratio_frames"])
        self.assertEqual(result["ratio_other_gear_frames"], 0)
        # Each 0x421 frame precedes the TCM group of its pass, so the check
        # compares it with the previous group: the first frame has none, and
        # the two frames that announce a new position meet the old target.
        self.assertEqual(result["manual_frames"], TICKS - 1)
        self.assertEqual(result["manual_equal_frames"], TICKS - 3)
        self.assertEqual(result["manual_positions"], [3, 4])
        self.assertEqual(result["closed_pedal_downshift_count"], 1)
        self.assertEqual(result["closed_pedal_target_rise_max"], 50)

    def test_command_line_prints_one_assignment_per_figure(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.main([str(self.trace)]), 0)
        values = tomllib.loads(output.getvalue())
        self.assertEqual(values["code_status_field"], 0xFFFF3A2E)
        self.assertTrue(values["code_matches_stock"])
        self.assertEqual(values["episode_floor_passes"], [len(FLOOR_TICKS)])
        self.assertEqual(values["shift_code_values"], [[2], [9]])
        self.assertEqual(values["scalar_source"], 0x942C)
        self.assertEqual(values["reduction_lag_counts"], [[1, 6, 0, 0]])
        self.assertEqual(values["transition_run_preceding"], ["burst", "none", "none"])
        self.assertEqual(values["reduction_run_peak"], [0x2080])
        self.assertEqual(values["manual_downshift_count"], 1)

    def test_reduction_state_follows_byte_4(self):
        result = self.result
        self.assertEqual(result["reduction_observed_snapshots"], result["snapshot_count"])
        self.assertEqual(result["reduction_unbound_snapshots"], 0)
        # Snapshots 123..128 carry byte 4 of the group two passes earlier,
        # except the cleared snapshot 125.
        self.assertEqual(result["reduction_direct_nonzero_snapshots"], 5)
        self.assertEqual(result["reduction_cleared_snapshots"], 1)
        self.assertEqual(result["reduction_other_snapshots"], len(DECAY))
        self.assertEqual(result["reduction_low_byte_snapshots"], 1)
        # Where the groups of the window differ, the state matches the second
        # newest group, except at the end of the burst where zeros repeat.
        self.assertEqual(result["reduction_lag_counts"], [1, 6, 0, 0])
        self.assertEqual(result["burst_reduction_followed_count"], 1)
        (run,) = result["reduction_runs"]
        self.assertEqual((run["passes"], run["peak"]), (len(DECAY), 0x2080))
        self.assertTrue(run["low_byte"] and run["non_increasing"] and run["burst"])
        self.assertEqual((run["event"], run["selector"], run["gear"]), ("3-4", "M4", 4))

    def test_transition_runs(self):
        result = self.result
        hidden = len(OTHER_CONFIGURATION)
        self.assertEqual(result["transition_unobserved_snapshots"], hidden)
        self.assertEqual(result["transition_observed_snapshots"], result["snapshot_count"] - hidden)
        self.assertEqual(result["transition_run_count"], 3)
        self.assertEqual(
            (result["transition_after_burst_runs"], result["transition_after_reduction_runs"],
             result["transition_unpreceded_runs"]),
            (1, 0, 2),
        )
        self.assertEqual(result["transition_peak_high_max"], len(TRANSITION_BURST))
        burst, cut, other = result["transition_runs"]
        self.assertEqual((burst["passes"], burst["end"], burst["preceding"]),
                         (len(TRANSITION_BURST), "zero", "burst"))
        self.assertEqual(burst["preceding_gap_s"], 0.0)
        self.assertAlmostEqual(
            burst["onset_lag_s"],
            ((TRANSITION_BURST[0] - BURST_TICKS[0]) * TICK_MS - GROUP_OFFSET_MS) / 1000,
        )
        self.assertEqual((burst["timing_base"], burst["timing_min"]), (25, 20))
        self.assertEqual((cut["passes"], cut["end"], cut["preceding"]),
                         (len(TRANSITION_CUT), "unobserved", "none"))
        self.assertEqual((cut["onset_lag_s"], cut["preceding_gap_s"]), (-1.0, -1.0))
        self.assertEqual((other["passes"], other["end"]), (len(TRANSITION_OTHER), "zero"))
        self.assertEqual(result["burst_transition_full_count"], 1)
        self.assertEqual(result["burst_transition_none_count"], 0)

    def test_event_rows(self):
        down, up = self.result["events"]
        self.assertEqual((down["shift"], down["class"], down["selector"]), ("4-3", "manual", "M3"))
        self.assertEqual((down["pedal_word_start"], down["pedal_word_max"]), (100, 100))
        self.assertTrue(down["episode"])
        self.assertEqual((up["shift"], up["class"]), ("3-4", "upshift"))
        self.assertEqual(up["burst_frames"], len(BURST_TICKS))
        self.assertEqual(up["divergence_passes"], len(DIVERGED_PASSES))
        self.assertEqual(up["transition_peak_high"], len(TRANSITION_BURST))
        self.assertEqual(up["reduction_peak"], (0x30 + len(BURST_TICKS) - 1) << 8)
        self.assertEqual((up["timing_base"], up["timing_min"]), (25, 20))
        self.assertEqual(up["transition_observed"], up["snapshots"])

    def test_map_switching_scalar_stays_outside_the_stock_comparison(self):
        data = bytearray(audit.STOCK_ROM.read_bytes())
        opcode = audit._u16(data, audit.SCALAR_LOAD)
        literal = ((audit.SCALAR_LOAD + 4) & ~3) + (opcode & 0xFF) * 4
        data[literal : literal + 4] = (0xFFFF5D28).to_bytes(4, "big")
        rom = Path(self.directory.name) / "map-switching.bin"
        rom.write_bytes(bytes(data))
        result = audit.audit([self.trace], rom)
        self.assertEqual(result["scalar_source"], 0xFFFF5D28)
        self.assertTrue(result["code_matches_stock"])
        self.assertEqual(result["rom_sha256"], audit.sha256_file(rom))


class DriveCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.trace = Path(cls.directory.name) / "drive.trc"
        write_trace(cls.trace, rows=drive_row, ticks=DRIVE_TICKS)
        cls.code = audit.interface_code(audit.STOCK_ROM.read_bytes())
        cls.result = audit.audit_capture(cls.trace, cls.code)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_downshift_classes_follow_the_pedal(self):
        events = self.result["events"]
        self.assertEqual([row["shift"] for row in events], ["4-3", "3-2", "2-1"])
        self.assertEqual([row["class"] for row in events], ["pressed", "full", "closed"])
        self.assertEqual([row["selector"] for row in events], ["D", "D", "D"])
        self.assertEqual([row["app1_start"] for row in events], [500, 950, 100])
        self.assertEqual([row["app1_max"] for row in events], [500, 950, 100])
        self.assertEqual([row["pedal_word_start"] for row in events], [500, 950, 100])
        self.assertEqual([row["pedal_word_max"] for row in events], [500, 950, 100])
        result = audit.combine([self.result])
        self.assertEqual(
            (result["drive_downshift_pressed_count"], result["drive_downshift_full_count"],
             result["drive_downshift_closed_count"], result["manual_downshift_count"]),
            (1, 1, 1, 0),
        )

    def test_transitions_follow_reduction_runs_within_the_binding_window(self):
        result = self.result
        self.assertEqual(result["reduction_other_snapshots"],
                         sum(len(run) for run in DRIVE_REDUCTIONS))
        runs = result["reduction_runs"]
        self.assertEqual(len(runs), len(DRIVE_REDUCTIONS))
        self.assertFalse(any(run["burst"] for run in runs))
        self.assertEqual({(run["selector"], run["peak"]) for run in runs}, {("D", 0x0500)})
        transitions = result["transition_runs"]
        self.assertEqual([row["preceding"] for row in transitions],
                         ["reduction", "reduction", "none"])
        for row, reduction, transition in zip(transitions[:2], DRIVE_REDUCTIONS,
                                               DRIVE_TRANSITIONS):
            self.assertAlmostEqual(row["onset_lag_s"],
                                   (transition[0] - reduction[0]) * TICK_MS / 1000)
            self.assertAlmostEqual(
                row["preceding_gap_s"],
                max(0, transition[0] - reduction[-1]) * TICK_MS / 1000,
            )
        self.assertGreater((DRIVE_TRANSITIONS[2][0] - DRIVE_REDUCTIONS[2][-1]) * TICK_MS / 1000,
                           audit.TRANSITION_GAP_S)
        self.assertEqual((transitions[2]["onset_lag_s"], transitions[2]["preceding_gap_s"]),
                         (-1.0, -1.0))
        result = audit.combine([self.result])
        self.assertEqual(
            (result["transition_after_reduction_runs"], result["transition_unpreceded_runs"]),
            ([2], [1]),
        )

    def test_events_file(self):
        events = Path(self.directory.name) / "events.csv"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.main(["--events", str(events), str(self.trace)]), 0)
        with events.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(list(rows[0]), list(audit.EVENT_COLUMNS))
        self.assertEqual([row["class"] for row in rows], ["pressed", "full", "closed"])
        self.assertEqual({row["capture"] for row in rows}, {self.trace.name})
        with self.assertRaises(FileExistsError):
            audit.audit([self.trace], events=events)


class TraceErrorTest(unittest.TestCase):
    def check(self, mutate, message):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "capture.trc"
            write_trace(trace, mutate=mutate)
            with self.assertRaisesRegex(ValueError, message):
                audit.read_trc(trace)

    def test_short_tcm_frame(self):
        def mutate(tick, frames):
            return [(i, d[:5] if tick == 10 and i == audit.PHASE_ID else d) for i, d in frames]

        self.check(mutate, "short TCM frame 0x177")

    def test_missing_frame_leaves_an_incomplete_group(self):
        def mutate(tick, frames):
            return [(i, d) for i, d in frames if not (tick == 10 and i == audit.PHASE_ID)]

        self.check(mutate, "incomplete TCM group")

    def test_frame_outside_a_group(self):
        def mutate(tick, frames):
            return [(i, d) for i, d in frames if not (tick == 10 and i == audit.GEAR_ID)]

        self.check(mutate, "outside a group")

    def test_capture_without_verified_snapshots(self):
        def mutate(tick, frames):
            return [(i, d) for i, d in frames if i != audit.TELEMETRY_ID]

        self.check(mutate, "no verified snapshot of telemetry profile 'tuning'")


if __name__ == "__main__":
    unittest.main()
