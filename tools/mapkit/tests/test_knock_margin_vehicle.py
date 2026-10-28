"""Knock channel schedule and the 2026-09-21 knock margin vehicle result."""

import math
import struct
import tomllib
from fractions import Fraction
from pathlib import Path

from tools.can_dashboard.model import RPM_PER_COUNT


ROOT = Path(__file__).resolve().parents[3]
ROM = (ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin").read_bytes()
PROFILE = tomllib.loads(
    (ROOT / "patches/can-telemetry-profile.toml").read_text(encoding="utf-8")
)
REGISTRY = tomllib.loads(
    (ROOT / "patches/hardware-results.toml").read_text(encoding="utf-8")
)
RESULT = REGISTRY["knock_margin"]["vehicle_2026_09_21"]


THRESHOLD_TABLE = 0x1108E
SPEED_AXIS = 0x15340
ROW_WORDS = 16
WORD = 0xFFFF
IDLE = 0x7FFF
MASK32 = 0xFFFFFFFF
# A four-stroke engine cycle is two crankshaft revolutions.
SECONDS_PER_CYCLE_AT_ONE_RPM = 2 * 60

WINDOW_START = 0x0004A5AC
WINDOW_CLOSE = 0x0004A8D4
EVALUATOR = 0x0004A238
EVALUATOR_LITERAL = 0x0004A9C0
TOOTH_7_CALL = 0x000297B0
INDEX_STORE = 0x000297DE
TOOTH_0_CALL = 0x0002A1DE
IDENTIFIED_CYLINDER = 0xFFFF13C8
EVENT_INDEX = 0xFFFF11DE
PREVIOUS_INDEX = 0xFFFF2143
BLOCK_COUNT = 0xFFFF2154
VALUE_FUNCTION = 0x00021CE0
REFERENCE = 0xFFFF2178
DIAGNOSTIC_PREDICATE = 0x00025E20
SAR2 = 0xFFFFECE0
ADCSR2 = 0xFFFFF858
ADDR24 = 0xFFFFF840
ADDR28 = 0xFFFFF848


def u16(address):
    return int.from_bytes(ROM[address : address + 2], "big")


def u32(address):
    return int.from_bytes(ROM[address : address + 4], "big")


def mov_l(address):
    """Return the register and literal of a PC-relative MOV.L."""
    opcode = u16(address)
    assert opcode >> 12 == 0xD, hex(opcode)
    return (opcode >> 8) & 0xF, u32(((address + 4) & ~3) + (opcode & 0xFF) * 4)


def mov_w(address):
    """Return the register and sign-extended literal of a PC-relative MOV.W."""
    opcode = u16(address)
    assert opcode >> 12 == 0x9, hex(opcode)
    value = u16(address + 4 + (opcode & 0xFF) * 2)
    return (opcode >> 8) & 0xF, (value - 0x10000 if value & 0x8000 else value) & MASK32


def imm(address, prefix):
    """Return the sign-extended immediate of a MOV #imm or ADD #imm opcode."""
    opcode = u16(address)
    assert opcode >> 8 == prefix, hex(opcode)
    value = opcode & 0xFF
    return value - 0x100 if value & 0x80 else value


def shll8_add(mov_address, add_address, register):
    """Return `(#imm << 8) + #imm` built by MOV #imm, SHLL8, and ADD #imm."""
    assert 0x4018 | register << 8 in {
        u16(address) for address in range(mov_address + 2, add_address, 2)
    }
    high = imm(mov_address, 0xE0 | register)
    low = imm(add_address, 0x70 | register)
    return ((high << 8) + low) & MASK32


def branch(address, prefix):
    """Return the target of a BT (0x89) or BF (0x8B) opcode."""
    return address + 4 + imm(address, prefix) * 2


def row(channel):
    address = THRESHOLD_TABLE + 0x20 * (channel - 1)
    return struct.unpack_from(f">{ROW_WORDS}H", ROM, address)


def adcsr2_fields(value):
    return {"adie": value >> 6 & 1, "adm": value >> 4 & 3, "ch": value & 7}


AXIS = struct.unpack_from(f">{ROW_WORDS}H", ROM, SPEED_AXIS)
# The record states engine speed as the coordinate 0xFFFF11F4.
RPM_STEP = Fraction(RPM_PER_COUNT)
INTERVAL = Fraction(
    PROFILE["context_count"] * PROFILE["base_tick_numerator"], PROFILE["pphi_hz"]
)
FULL_COVERAGE_RPM = SECONDS_PER_CYCLE_AT_ONE_RPM / INTERVAL


def test_tooth_7_opens_the_window_before_it_advances_the_event_index():
    assert mov_l(TOOTH_7_CALL - 2) == (2, WINDOW_START)
    assert u16(TOOTH_7_CALL) == 0x420B  # jsr @r2
    # The copy requires crank synchronization 0xFFFF8501.bit7.
    register, base = mov_w(0x297B4)
    assert (register, base + 6) == (6, 0xFFFF8501)
    assert u16(0x297B6) == 0x8466  # mov.b @(6,r6),r0
    assert u16(0x297B8) == 0xC880  # tst #0x80,r0
    # r6 = uint8[0xFFFF128C + (79 << 2)], r0 = r6.
    assert mov_l(0x297C2) == (13, 0xFFFF128C)
    assert 0xFFFF128C + (imm(0x297D0, 0xE0) << 2) == IDENTIFIED_CYLINDER
    assert u16(0x297D2) == 0x4008  # shll2 r0
    assert u16(0x297D4) == 0x06DC  # mov.b @(r0,r13),r6
    assert u16(0x297D8) == 0x6063  # mov r6,r0
    # mov.b r0,@(10,r14) stores the event index after the window start.
    register, base = mov_l(0x297CC)
    assert u16(INDEX_STORE) == 0x80EA
    assert (register, base + 10) == (14, EVENT_INDEX)
    assert TOOTH_7_CALL < INDEX_STORE


def test_tooth_0_closes_the_window_through_the_evaluator():
    assert mov_l(TOOTH_0_CALL - 2) == (2, WINDOW_CLOSE)
    assert u16(TOOTH_0_CALL) == 0x420B  # jsr @r2
    assert u32(EVALUATOR_LITERAL) == EVALUATOR
    # The evaluator reads the event index and returns only for zero.
    register, base = mov_l(0x4A25C)
    assert (register, base + 10) == (14, EVENT_INDEX)
    assert u16(0x4A25E) == 0x84EA  # mov.b @(10,r14),r0
    assert u16(0x4A262) == 0x2558  # tst r5,r5
    assert u16(0x4A264) == 0x8B01  # bf over the return branch


def test_ignition_command_is_measured_from_110_degrees():
    # Ignition command ROM8[0x83D5] - advance is measured from tooth 7.
    before_tdc = ROM[0x83D5]
    assert before_tdc == 110


def test_stock_window_start_programs_one_acquisition_for_every_channel():
    assert ROM[0x8B3D] == 0x82
    assert ROM[0x8B3D] & 0x80 and not ROM[0x8B3D] & 0x08
    # Bit 7 enables the window; bit 3 selects the alternating path.
    for load, test, mask, skip in (
        (0x4A5B4, 0x4A5B8, 0x80, 0x4A5C4),
        (0x4A5C8, 0x4A5CC, 0x08, 0x4A638),
    ):
        assert mov_l(load) == (5, 0x8B3D)
        assert u16(load + 2) == 0x6050  # mov.b @r5,r0
        assert u16(test) == 0xC800 | mask
        assert branch(test + 2, 0x8B) == skip
    # mov.l r2,@r4 stores ADDR24 into SAR2; mov.b r6,@r2 writes ADCSR2.
    assert [u16(address) for address in (0x4A5F8, 0x4A5FA, 0x4A600)] == [
        0x4218,
        0x4418,
        0x2422,
    ]
    assert shll8_add(0x4A5F2, 0x4A5FC, 2) == ADDR24
    assert shll8_add(0x4A5F6, 0x4A5FE, 4) == SAR2
    assert imm(0x4A602, 0xE6) == 0x59
    assert u16(0x4A626) == 0x4218
    assert shll8_add(0x4A624, 0x4A628, 2) == ADCSR2
    assert u16(0x4A62C) == 0x2260
    # 4-channel scan mode with CH = 1 converts AN24 and AN25.
    assert adcsr2_fields(0x59) == {"adie": 1, "adm": 1, "ch": 1}


def test_bit_3_window_start_alternates_the_input_by_the_previous_index():
    register, base = mov_l(0x4A638)
    assert (register, base + 10) == (5, EVENT_INDEX)
    assert u16(0x4A63C) == 0x845A  # mov.b @(10,r5),r0
    assert u16(0x4A63E) == 0x6603  # mov r0,r6
    assert mov_l(0x4A63A) == (4, 0xFFFF1FF4)
    assert u16(0x4A642) == 0x4018  # shll8 r0
    assert u16(0x4A646) == 0x0464  # mov.b r6,@(r0,r4)
    assert 0xFFFF1FF4 + shll8_add(0x4A640, 0x4A644, 0) == PREVIOUS_INDEX
    # tst #1,r0 on the previous index: odd branches to ADDR24.
    assert u16(0x4A666) == 0x6063  # mov r6,r0
    assert u16(0x4A668) == 0xC801
    assert branch(0x4A66A, 0x8B) == 0x4A6BA
    assert shll8_add(0x4A66C, 0x4A674, 2) == ADDR28
    assert shll8_add(0x4A6BA, 0x4A6C2, 2) == ADDR24
    for start, store in ((0x4A66E, 0x4A678), (0x4A6BC, 0x4A6C8)):
        assert shll8_add(start, start + 8, 4) == SAR2
        assert u16(store) == 0x2422  # mov.l r2,@r4
    # tst #1,r0 on uint8[0xFFFF2143]: odd branches to ADCSR2 = 0x59.
    assert mov_l(0x4A684) == (1, 0xFFFF1FF4)
    assert 0xFFFF1FF4 + shll8_add(0x4A6A8, 0x4A6AC, 0) == PREVIOUS_INDEX
    assert u16(0x4A6AE) == 0x001C  # mov.b @(r0,r1),r0
    assert shll8_add(0x4A6A0, 0x4A6A4, 2) == ADCSR2
    assert u16(0x4A6B0) == 0xC801
    assert branch(0x4A6B2, 0x8B) == 0x4A6CA
    assert imm(0x4A6B4, 0xE6) == 0x5D
    assert imm(0x4A6CA, 0xE6) == 0x59
    assert u16(0x4A6B8) == u16(0x4A6CE) == 0x2260  # mov.b r6,@r2
    # CH = 5 converts AN28 and AN29.
    assert adcsr2_fields(0x5D) == {"adie": 1, "adm": 1, "ch": 5}


def test_metric_and_reference_constants():
    assert mov_l(0x49D9A) == (2, 0x8618) and ROM[0x8618] == 0x00
    assert mov_l(0x49E26) == (2, 0x8870) and ROM[0x8870] == 3
    gain_bytes = [mov_l(address)[1] for address in (0x49E9A, 0x49EA4, 0x49EAC)]
    assert gain_bytes == [0x86A7, 0x8694, 0x86AC]
    assert [ROM[address] for address in gain_bytes] == [0x80, 0x80, 0x80]
    assert math.prod(ROM[address] for address in gain_bytes) >> 7 == 1 << 14
    assert mov_l(0x49F24) == (5, 0x7FFFFFFF)
    # Window values, the no-block check, and the reference rows.
    assert mov_l(0x4A45E) == (6, VALUE_FUNCTION)
    assert mov_l(0x4A54A) == (6, VALUE_FUNCTION)
    register, base = mov_l(0x4A26A)
    assert (u16(0x4A26E), u16(0x4A270)) == (0x4008, 0x06EC)
    assert (register, base + (imm(0x4A26C, 0xE0) << 2)) == (14, BLOCK_COUNT)
    assert mov_l(0x4A2C2) == (5, REFERENCE)
    # cmp/hi compares metric + 0x80000000 with threshold + 0x80000000.
    assert mov_l(0x4A304) == (2, 0xFFFF21D8)
    assert mov_l(0x4A308) == (5, 0xFFFF2144)
    assert [u16(address) for address in range(0x4A31C, 0x4A328, 2)] == [
        0xE580,
        0x4518,
        0x622D,
        0x4528,
        0x325C,
        0x3726,
    ]
    # Reference weight, the two diagnostic records, and the reset value.
    assert mov_l(0x4A19C) == (2, 0x884B) and ROM[0x884B] == 0xE0
    records = []
    for start in (0x4A13C, 0x4A184):
        assert mov_l(start + 2) == (6, DIAGNOSTIC_PREDICATE)
        assert (u16(start + 4), u16(start + 6)) == (0x4418, 0x460B)
        records.append(shll8_add(start, start + 8, 4))
    assert records == [0x12D, 0x13F]
    # Either nonzero predicate selects the reset at 0x4A14A.
    assert u16(0x4A146) == u16(0x4A18E) == 0x2008  # tst r0,r0
    assert branch(0x4A148, 0x89) == 0x4A184
    assert branch(0x4A190, 0x8B) == 0x4A14A
    assert mov_l(0x4A14A) == (2, 0x9282) and u16(0x9282) == WORD
    # The predicate returns bit 7 of byte 1 of the 3-byte record.
    assert mov_l(DIAGNOSTIC_PREDICATE) == (1, 0xFFFF5718)
    assert [u16(address) for address in range(0x25E2A, 0x25E3A, 2)] == [
        0x6203,  # mov r0,r2
        0x4200,  # shll r2
        0x320C,  # add r0,r2
        0x362C,  # add r2,r6
        0x8461,  # mov.b @(1,r6),r0
        0xC880,  # tst #0x80,r0
        0x0029,  # movt r0
        0xCA01,  # xor #1,r0
    ]


def test_record_uses_the_registered_session_and_captures():
    section, name = RESULT["capture_registry"].split(".")
    captures = REGISTRY[section][name]
    session = REGISTRY["can_telemetry"]["schema2_profile5_drive_2026_09_21"]
    for key in ("recorded_on", "image_sha256", "profile_id", "profile_crc16"):
        assert RESULT[key] == session[key]
    assert RESULT["hardware_status"] == session["hardware_status"] == "pass"
    assert RESULT["capture_name"] == [row["capture_name"] for row in captures]
    assert RESULT["capture_sha256"] == [row["capture_sha256"] for row in captures]
    assert RESULT["mlg_record_count"] == session["record_count_total"]
    assert RESULT["mlg_record_count"] == sum(row["record_count"] for row in captures)
    traces = [name for name in RESULT["capture_name"] if name.endswith(".trc")]
    assert all("converted_mlg_sha256" in row for row in captures)
    assert len(RESULT["tag4_group_count_by_trc_capture"]) == len(traces)
    assert sum(RESULT["tag4_group_count_by_trc_capture"]) == RESULT["tag4_group_count"]


def test_stock_rows_divide_the_channels():
    assert RESULT["threshold_table"] == THRESHOLD_TABLE
    for channel in range(1, 7):
        cells = row(channel)
        if channel in RESULT["all_ffff_rows"]:
            assert set(cells) == {WORD}
        else:
            assert channel in RESULT["valued_channels"]
            assert cells[0] == WORD and max(cells[1:]) < IDLE
    assert sorted(RESULT["all_ffff_rows"] + RESULT["valued_channels"]) == list(
        range(1, 7)
    )


def test_every_interval_holds_an_evaluation_from_the_profile_speed():
    assert INTERVAL == Fraction(512, 10000)
    assert FULL_COVERAGE_RPM == Fraction(234375, 100)
    rpm_raw = math.ceil(FULL_COVERAGE_RPM / RPM_STEP)
    assert RESULT["full_coverage_rpm_raw_min"] == rpm_raw


def test_idle_counts_single_out_channels_3_and_5():
    groups = RESULT["tag4_group_count"]
    full = RESULT["full_coverage_group_count"]
    for channel, idle, full_idle in zip(
        range(1, 7),
        RESULT["idle_group_count"],
        RESULT["full_coverage_idle_group_count"],
        strict=True,
    ):
        if channel in RESULT["all_ffff_rows"]:
            assert (idle, full_idle) == (groups, full)
        else:
            assert idle < groups and full_idle == 0
    assert RESULT["channel_3_5_valued_record_count"] == 0


def test_idle_values_of_the_valued_channels_follow_the_cadence():
    # From the second axis point the finite rows leave their 0xFFFF cell.
    assert RESULT["cadence_rpm_raw_min"] == AXIS[1]
    expected = RESULT["cadence_expected_idle_group_count"]
    observed = RESULT["cadence_idle_group_count"]
    assert len(observed) == len(RESULT["valued_channels"])
    for count in observed:
        assert abs(count - expected) <= expected // 50
    assert (
        RESULT["full_coverage_group_count"]
        < RESULT["cadence_group_count"]
        < RESULT["tag4_group_count"]
    )


def test_margins_and_latches_name_only_the_valued_channels():
    series = [
        RESULT[name]
        for name in (
            "trc_margin_min",
            "trc_margin_p5",
            "trc_margin_p50",
            "trc_margin_p95",
            "trc_margin_max",
        )
    ]
    for values in zip(*series, strict=True):
        assert list(values) == sorted(values) and values[-1] < IDLE
    for low, trace_low in zip(
        RESULT["margin_min"], RESULT["trc_margin_min"], strict=True
    ):
        assert -0x8000 < low <= trace_low
    assert RESULT["saturated_margin_record_count"] == 0
    valued_bits = sum(1 << (channel - 1) for channel in RESULT["valued_channels"])
    idle_bits = sum(1 << (channel - 1) for channel in RESULT["all_ffff_rows"])
    assert RESULT["latched_bitmap_union"] == valued_bits
    assert not RESULT["latched_bitmap_union"] & idle_bits
    assert RESULT["latched_count_max"] >= 1


def test_largest_metrics_are_exact_threshold_differences():
    assert RESULT["metric_max_capture"] in RESULT["capture_name"]
    for channel, metric, margin, rpm_raw in zip(
        RESULT["valued_channels"],
        RESULT["metric_max_by_channel"],
        RESULT["metric_max_margin_by_channel"],
        RESULT["metric_max_rpm_raw_by_channel"],
        strict=True,
    ):
        assert rpm_raw >= AXIS[-1]
        assert metric == row(channel)[-1] - margin
    largest = max(RESULT["metric_max_by_channel"])
    assert largest < WORD - IDLE
    index = RESULT["metric_max_by_channel"].index(largest)
    assert RESULT["valued_channels"][index] == 4
    fuel_cut = REGISTRY["main_fuel_cut"]["vehicle_2026_09_21"]
    assert RESULT["metric_max_capture"] == fuel_cut["capture_name"]
    assert (
        fuel_cut["first_activation_seconds"]
        <= RESULT["metric_max_seconds_by_channel"][index]
        <= fuel_cut["last_release_seconds"]
    )


