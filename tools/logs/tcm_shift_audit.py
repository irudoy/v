#!/usr/bin/env python3
"""Audit the JK08A transmission interface frames in road TRC captures.

The TCM sends frames 0x174, 0x176, and 0x177 back to back every 10 ms. The
audit replays a PEAK TRC through the dashboard model into verified profile 5
snapshots, groups the three TCM frames, and pairs snapshot j with the 0x180 and
0x160 frames that follow the first page of snapshot j + 1, which carry the
values of the same scheduler pass. Per capture it reports:

- the 0x174 byte 4 rolling counter in bits 0..3, bit 4, and the status field
  in bits 5..7 with its value-3 episodes;
- the packed torque-domain words A and B of 0x174 bytes 0..2 and the
  restarts and ramps of word B after the episodes;
- the shift events of the 0x174 byte 3 gear pair with the 0x177 byte 5 shift
  code, the 0x177 byte 4 bursts, and the divergence of the 0x180 actual-torque
  word from the 0x160 parallel word;
- the identity of the 0x180 request word with the packed bounded request
  0xFFFF19C6, the passes in which the packed 0xFFFF19C6 lies above that word,
  and the passes in which 0xFFFF19C6 equals the unpacked word B;
- the agreement of the current gear with the 0x176 speed ratio, of the
  0x177 gear phase with the current gear, and of the 0x421 manual position with
  the target gear;
- the shared throttle target in closed-pedal downshifts.

A shift event starts where the 0x174 target nibble changes to a gear that
differs from the current nibble, ends where the current nibble reaches it or
the target changes again, and its window closes on the first frame at or after
the target change whose 0x177 byte 5 holds idle code 0x78. The packed torque
domain is the one of the ECU packer FUN 00079E70:
word = clamp(trunc0(raw / 5) + 800, 0, 4094), so a word unpacks to
5 * (word - 800).

Before the captures are read, `interface_code` checks the exact instruction
bytes of the path from the TCM frames to the shared request 0xFFFF19C6 in the
ROM and derives its addresses, tables, and options from the literals of those
instructions; the `code_` keys report them. The floor passes of the status
episodes use the floor table read from the same ROM. `scalar_source` is the
address from which FUN_00077892 reads the throttle-limit scalar that caps its
gear-indexed target: 0x942C in the stock ROM and the selected-map copy in a
map-switching image, so it stays outside the stock comparison.

The output is one `key = value` line per figure in TOML syntax.
"""

from __future__ import annotations

import argparse
import bisect
from dataclasses import dataclass
import hashlib
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import DashboardModel, FrameRecord  # noqa: E402
from tools.logs import mlg_relation_audit  # noqa: E402
from tools.logs import peak_trc_audit  # noqa: E402
from tools.logs.torque_scale_audit import RE5R05A_RATIOS  # noqa: E402

TELEMETRY_ID = 0x6F0
GEAR_ID = 0x174
SPEED_ID = 0x176
PHASE_ID = 0x177
ACTUAL_ID = 0x180
LIMITED_ID = 0x160
SELECTOR_ID = 0x421
TCM_GROUP_MS = 2.0
SNAPSHOT_FIELDS = (
    "app1_raw",
    "engine_torque_state_raw",
    "throttle_request_bounded_raw",
    "throttle_target_shared_raw",
    "final_timing_raw",
    "fuel_inhibit_mask",
)
RPM_PER_COUNT = 12.5
PACK_DIVISOR = 5
PACK_ZERO = 800
PACK_MAX = 4094
IDLE_SHIFT_CODE = 0x78
STATUS_EPISODE_VALUE = 3
# Frames of one status episode lie at most this far apart.
EPISODE_GAP_S = 0.1
# Word B is back at its default after this many consecutive default frames.
RAMP_SETTLE_FRAMES = 10
# Episode windows run from this long before the first value-3 frame to this
# long after word B settles.
EPISODE_MARGIN_S = (0.03, 0.05)
# A burst of nonzero 0x177 byte 4 frames tolerates this many zero frames.
BURST_ZERO_GAP = 1
# Burst windows run from this long before the first to this long after the
# last nonzero frame of the burst.
BURST_MARGIN_S = (0.03, 0.5)
# Upshift divergence is counted up to this long after the shift window closes.
DIVERGENCE_TAIL_S = 0.3
# Timing and pedal references of a burst come from this span before it.
BURST_REFERENCE_S = 0.3
# Word B of a TCM frame at most this old binds a pass.
BINDING_WINDOW_S = 0.03
BINDING_FRAMES = 4
CLOSED_PEDAL_APP1 = 160
# 0x421 byte 0 codes of the drive and manual positions (defs/JK08A.can.md).
DRIVE_SELECTORS = {0x20: "D", 0x28: "DS"}
MANUAL_SELECTORS = {0x80: 1, 0x88: 2, 0x90: 3, 0x98: 4, 0xA0: 5}
RATIO_TOLERANCE = 0.02
RATIO_MIN_TURBINE = 800
RATIO_MIN_OUTPUT = 300
STOCK_ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
# The periodic task of the path and the hold decrement run once per 10.24 ms
# scheduler pass (defs/JK08A.can.md).
SCHEDULER_PASS_S = 0.01024
IDLE_CODE_INDEX = 15

# Exact instruction windows of the TCM interface path, as address and opcodes.
CODE_WINDOWS = (
    # FUN_000C47EA: 0x174 payload at frame buffer + 0x70, words A and B into
    # the field block, byte 4 bits 5..7 into field block + 0x6A.
    (
        0xC47F4,
        "d474 da77 6243 7270 6620 6243 7270 dc6f 656c 9671 4508 dd73 4508 2569 "
        "6643 7670 8461 660c 9069 4609 4609 666c 356c 0a55",
    ),
    (
        0xC4824,
        "e60f 8421 4618 656d c90f 6203 4218 2259 6523 6243 7270 8422 6243 7270 "
        "660c 9055 356c d665 0a55",
    ),
    (0xC49EC, "6243 7270 8424 6243 7270 600c 4009 4009 4001 c907 6603 e06a 0a64"),
    # FUN_0007724C: status 3 ORs 0x18 into GBR + 7; words A and B become
    # min(5 * word - 4000, 0x7FFF) at limit block + 0xF4 and + 0xF6.
    (0x77254, "d07f 401e d17f e06a 041c c407 644c 6c03 c400 6e03 6043 8803 8b05 60c3 cb18 c007"),
    (
        0x772B4,
        "9069 9269 0d1d 9768 6ddd 66d3 4608 36dc 362c 3677 8b00 6673 d463 e0f4 "
        "600c 925b 0465 905b 051d 655d 6653 4608 365c 362c 3677 8b00 6673 e0f6 "
        "d55c 600c 0465",
    ),
    # FUN_00020DFE: block copier 0x22558 copies r0 bytes from @r2 to @r1.
    (0x20EEA, "db82"),
    (0x20FB2, "d17a"),
    (0x20FC8, "e041 d277 4b0b 4008"),
    (0x21066, "d173"),
    (0x21094, "d271 4b0b e00c"),
    (0x22558, "2f26 2f36 2f46 8800 8912 6423 340c 6024 2100"),
    # FUN_0002040C: every tenth invocation decrements each nonzero byte of the
    # 195-byte block that holds the hold byte.
    (0x20596, "9855 6082 7001 880a 8d02 2802 a182 0009"),
    (
        0x205F2,
        "d51d e4c3 644c 6253 324c 3522 8d0c 6653 6260 2228 8903 6260 72ff 622c "
        "2620 7601 6253 324c 3622 8bf3",
    ),
    # Selection of FUN_00077892 and the tail call of FUN_000777FA.
    (0x77364, "d640 6060 c801 8b0c d63f 6060 c880 8b03 b28d 0009"),
    (0x77386, "a238 4f26"),
    # FUN_00077892: neutralizer bit 1, hold byte, request-select bit 3.
    (0x778AE, "d91f"),
    (0x778B2, "dd1a"),
    (
        0x7799E,
        "d676 8097 8467 c810 8919 d574 6650 8451 3600 8914 8497 c840 8b11 d671 "
        "60e3 cb02 d86d 6260 e4ff d66f 644c 8096 e04c 0624 9088 0e8c 6eec 3e43 "
        "8908 a005 7e01 60e3 c9fd 8096 ee00 d863 907c 08e4",
    ),
    (0x779EA, "8496 c902 2008 8f08 6a03 d663 e04c 026c 2228 8b02 60c3 a002 c9f7 60c3 cb08 80d1"),
    # FUN_00077892: cap of the gear-indexed target at the throttle-limit scalar.
    (0x77AC0, "d23a 6621 666d 3066 8f01 6403 6463"),
    # FUN_00077892: shift-code floor of the neutralized passes.
    (
        0x77A0A,
        "e0ae dc5e 600c e50f 06cc 666c 3657 8b00 e60f d25b 646c 8421 c904 2008 "
        "8f06 80f4 d259 d559 8521 6251 3026 8916 d558 6043 6eec 025c 622c 3e27 "
        "890f 2aa8 890d e010 d654 2b0b e058 4400 0db4 6043 066d e480 9043 4418 "
        "364c a009 0865 60b3 c9ef 6b03 e058 0db4 e280 9038 4218 0825",
    ),
    # FUN_00077892: candidate 0xFFFF4162 with and without the neutralizer.
    (0x77B24, "2aa8 8f02 0825 a0fb 0009"),
    (
        0x77CE6,
        "905b 068d 3e63 8b00 66e3 d73b 857a 3607 8d01 6203 6263 6523 d239 6020 "
        "c801 8908 e0f6 600c 02cd 3527 8b02 6523 a001 1f24 1f54 e480 4418 3543 "
        "890a a009 6543 903d 058d e0f6 600c 06cd 3657 8900 6563 d72a 6aac e03e "
        "2aa8 8d06 0755",
    ),
    # FUN_000777FA: request bounds while the request-select bit is set.
    (0x777FE, "d144"),
    (
        0x77818,
        "d23f d440 6020 c901 6603 8441 c808 8913 2668 8903 d53c e03e a002 0d5d "
        "9026 0d1d 9025 d539 071d e03e 065d 3677 8900 6763",
    ),
    (0x77864, "9011 01d5 9010 0175"),
    # FUN_00079030: lower bound by maximum, upper bound by minimum, and the
    # store of the shared request.
    (0x7912A, "d241 6920"),
    (0x79148, "d137 0355 9060 051d 3d53 8b00 65d3 d334 655f 905a 023d 3527 8b00 6523"),
    (0x7919E, "6093 c801 8904 d31f 9036 03d5 a003 0009 d31d 9031 0375"),
    # FUN_000C4ACE: 0x177 payload at frame buffer + 0x66, byte 4 to limit
    # block + 0xC0, byte 5 to limit block + 0xAE as 15 or bits 3..6.
    (0xC4ADE, "db70"),
    (
        0xC4C5E,
        "d316 c90f 6603 e084 600c 0264 62b3 7266 8424 62b3 7266 6603 e0c0 600c "
        "0364 8425 600c 4009 4001 c810 8927 d30b e0ae e20f 600c 0324",
    ),
    (0xC4CD8, "7b66 d37d 84b5 600c 4009 4001 c90f 6603 e0ae 600c 0364"),
    # FUN_0006425A: latched byte 4 into 0xFFFF3373 under ROM option bit 4.
    (0x64266, "d613 6060 c810 8926 d612 e0c0 600c a02c 026c"),
    (0x642D0, "d66e 9001 a001 0009 0a7b a0ad 0624"),
)
SCALAR_LOAD = 0x77AC0
LATCH_BYTES = 65 << 2
STATUS_LATCH_BYTES = 12
HOLD_BLOCK_BYTES = 0xC3


@dataclass(frozen=True)
class Snapshot:
    tick: int
    first_page_s: float
    rpm_raw: int
    app1_raw: int
    torque_state_raw: int
    request_raw: int
    throttle_target_raw: int
    timing_raw: int
    fuel_inhibit_mask: int


@dataclass(frozen=True)
class TcmFrame:
    seconds: float
    gear: bytes
    speed: bytes
    phase: bytes
    selector: int | None

    @property
    def target(self) -> int:
        return self.gear[3] >> 4

    @property
    def current(self) -> int:
        return self.gear[3] & 0x0F

    @property
    def counter(self) -> int:
        return self.gear[4] & 0x0F

    @property
    def status(self) -> int:
        return self.gear[4] >> 5

    @property
    def word_a(self) -> int:
        return self.gear[0] << 4 | self.gear[1] >> 4

    @property
    def word_b(self) -> int:
        return (self.gear[1] & 0x0F) << 8 | self.gear[2]

    @property
    def output_speed(self) -> int:
        return int.from_bytes(self.speed[0:2], "big")

    @property
    def turbine_speed(self) -> int:
        return int.from_bytes(self.speed[2:4], "big")

    @property
    def gear_phase(self) -> int:
        return self.phase[2] & 0x07

    @property
    def reduction(self) -> int:
        return self.phase[4]

    @property
    def shift_code(self) -> int:
        return self.phase[5]


@dataclass(frozen=True)
class Pass:
    snapshot: Snapshot
    actual_word: int
    request_word: int
    limited_word: int
    parallel_word: int

    @property
    def seconds(self) -> float:
        return self.snapshot.first_page_s

    @property
    def diverged(self) -> bool:
        return self.actual_word != self.parallel_word


@dataclass(frozen=True)
class Capture:
    path: Path
    sha256: str
    snapshots: tuple[Snapshot, ...]
    tcm: tuple[TcmFrame, ...]
    passes: tuple[Pass, ...]
    selector_frames: tuple[tuple[float, int], ...]


@dataclass(frozen=True)
class ShiftEvent:
    target_index: int
    end_index: int
    window_end_index: int
    completed: bool
    source: int
    destination: int

    @property
    def upshift(self) -> bool:
        return self.destination > self.source

    @property
    def name(self) -> str:
        return f"{self.source}-{self.destination}"


@dataclass(frozen=True)
class Episode:
    start_index: int
    end_index: int
    settled_index: int
    value_frames: int


def pack(raw: int) -> int:
    """The ECU packer: clamp(trunc0(raw / 5) + 800, 0, 4094)."""
    quotient = abs(raw) // PACK_DIVISOR
    if raw < 0:
        quotient = -quotient
    return max(0, min(PACK_MAX, quotient + PACK_ZERO))


def unpack(word: int) -> int:
    return PACK_DIVISOR * (word - PACK_ZERO)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Hex(int):
    """An address printed as a hexadecimal TOML integer."""

    def __str__(self) -> str:
        return f"0x{int(self):X}"


def _u16(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 2], "big")


def _pc_literal(data: bytes, address: int) -> int:
    """The 32-bit literal that mov.l @(disp,pc) at `address` loads."""
    opcode = _u16(data, address)
    if opcode >> 12 != 0xD:
        raise ValueError(f"0x{address:05X}: 0x{opcode:04X} is not mov.l @(disp,pc)")
    literal = ((address + 4) & ~3) + (opcode & 0xFF) * 4
    return int.from_bytes(data[literal : literal + 4], "big")


def _pc_word(data: bytes, address: int) -> int:
    """The sign-extended word that mov.w @(disp,pc) at `address` loads."""
    opcode = _u16(data, address)
    if opcode >> 12 != 0x9:
        raise ValueError(f"0x{address:05X}: 0x{opcode:04X} is not mov.w @(disp,pc)")
    value = _u16(data, address + 4 + (opcode & 0xFF) * 2)
    return value - 0x10000 if value & 0x8000 else value


def _same(label: str, *values: int) -> int:
    if len(set(values)) != 1:
        raise ValueError(f"{label}: inconsistent values {[hex(value) for value in values]}")
    return values[0]


def interface_code(data: bytes) -> dict:
    """Check the TCM interface path in a JK08A ROM and derive its addresses.

    Every value comes from a literal, displacement, or table that one of the
    checked instruction windows reads; a byte that differs from CODE_WINDOWS
    raises ValueError.
    """
    for address, expected in CODE_WINDOWS:
        count = len(expected.split())
        found = " ".join(f"{_u16(data, address + 2 * k):04x}" for k in range(count))
        if found != expected:
            raise ValueError(f"0x{address:05X}: expected {expected}, found {found}")
    if _pc_literal(data, 0x20EEA) != 0x22558:
        raise ValueError("FUN_00020DFE does not copy through block copier 0x22558")
    fields = _same("field block", _pc_literal(data, 0xC47F6), _pc_literal(data, 0x77258))
    word_offsets = (
        _same("word A offset", _pc_word(data, 0xC4818), _pc_word(data, 0x772B4)),
        _same("word B offset", _pc_word(data, 0xC4842), _pc_word(data, 0x772D6)),
    )
    _same("frame buffer", _pc_literal(data, 0xC47F4), _pc_literal(data, 0xC4ADE))
    flags = _same("status flags", _pc_literal(data, 0x77254), _pc_literal(data, 0x21094))
    flag_latches = _same("status latches", _pc_literal(data, 0x21066), _pc_literal(data, 0x7799E))
    limits = _same(
        "limit block",
        _pc_literal(data, 0x772CC),
        _pc_literal(data, 0x20FCA),
        _pc_literal(data, 0xC4C5E),
        _pc_literal(data, 0xC4C88),
        _pc_literal(data, 0xC4CDA),
    )
    latches = _same(
        "latch block",
        _pc_literal(data, 0x20FB2),
        _pc_literal(data, 0x77A0C),
        _pc_literal(data, 0x6426E),
    )
    transmission = _same(
        "transmission block",
        _pc_literal(data, 0x779BE),
        _pc_literal(data, 0x779E4),
        _pc_literal(data, 0x777FE),
        _pc_literal(data, 0x79148),
        _pc_literal(data, 0x79156),
        _pc_literal(data, 0x642D0),
    )
    selectors = _same("selector bytes", _pc_literal(data, 0x778B2), _pc_literal(data, 0x7781A))
    bounds = _same(
        "bound block",
        _pc_literal(data, 0x77CF0),
        _pc_literal(data, 0x77D34),
        _pc_literal(data, 0x7782C),
        _pc_literal(data, 0x7783A),
    )
    hold_block = _same("hold block", _pc_literal(data, 0x779C4), _pc_literal(data, 0x205F2))
    implementation = _same("implementation", _pc_literal(data, 0x7912A), _pc_literal(data, 0x77364))

    def latch_of(address: int) -> int:
        if not limits <= address < limits + LATCH_BYTES:
            raise ValueError(f"0x{address:08X} lies outside the latched block")
        return latches + address - limits

    # The immediates below are part of the checked windows.
    word_b_limit = limits + 0xF6
    shift_code_field = limits + 0xAE
    reduction_field = limits + 0xC0
    hold_byte = hold_block + 76
    if not hold_block <= hold_byte < hold_block + HOLD_BLOCK_BYTES:
        raise ValueError("the hold byte lies outside the decremented block")
    floor_word = _same(
        "floor word",
        *(transmission + _pc_word(data, address) for address in (0x77A5A, 0x77A70, 0x77CE6)),
    )
    options = {
        "hold": _pc_literal(data, 0x779B8),
        "word_b_term": _pc_literal(data, 0x77CFE),
        "bounds": _pc_literal(data, 0x77818),
        "reduction_copy": _pc_literal(data, 0x64266),
        "implementation": implementation,
        "alternate": _pc_literal(data, 0x7736C),
    }
    floor_gate_limit = _pc_literal(data, 0x77A2C)
    floor_table = _pc_literal(data, 0x77A4A)
    floor_passes_table = _pc_literal(data, 0x77A36)
    states = _pc_literal(data, 0x778AE)
    return {
        "code_status_field": Hex(fields + 0x6A),
        "code_word_fields": [Hex(fields + offset) for offset in word_offsets],
        "code_word_offset": _same("word offset", _pc_word(data, 0x772B6), _pc_word(data, 0x772D2)),
        "code_word_cap": _pc_word(data, 0x772BA),
        "code_word_limits": [Hex(limits + 0xF4), Hex(word_b_limit)],
        "code_status_flags": Hex(flags + 7),
        "code_status_set_mask": Hex(0x18),
        "code_status_latch": Hex(flag_latches + 7),
        "code_status_latch_copy": [Hex(flags), Hex(flag_latches), STATUS_LATCH_BYTES],
        "code_latch_copy": [Hex(limits), Hex(latches), LATCH_BYTES],
        "code_word_b_latch": Hex(latch_of(word_b_limit)),
        "code_gears": [Hex(_pc_literal(data, 0x779A8)), Hex(_pc_literal(data, 0x779A8) + 1)],
        "code_neutralizer": Hex(states + 6),
        "code_inhibit": Hex(states + 7),
        "code_hold_byte": Hex(hold_byte),
        "code_hold_block": [Hex(hold_block), HOLD_BLOCK_BYTES],
        "code_hold_passes": data[options["hold"]],
        "code_hold_s": round(data[options["hold"]] * SCHEDULER_PASS_S, 4),
        "code_floor_counter": Hex(transmission + _pc_word(data, 0x779CE)),
        "code_request_select": Hex(selectors + 1),
        "code_shift_code_field": Hex(shift_code_field),
        "code_shift_code_latch": Hex(latch_of(shift_code_field)),
        "code_floor_gate": [Hex(_pc_literal(data, 0x77A1C) + 1), Hex(_pc_literal(data, 0x77A2A) + 2)],
        "code_floor_gate_limit": [Hex(floor_gate_limit), _u16(data, floor_gate_limit)],
        "code_floor_table": Hex(floor_table),
        "code_floor_values": [_u16(data, floor_table + 2 * k) - 0x8000 for k in range(16)],
        "code_floor_passes_table": Hex(floor_passes_table),
        "code_floor_passes": list(data[floor_passes_table : floor_passes_table + 16]),
        "code_floor_word": Hex(floor_word),
        "code_candidate": Hex(bounds + 62),
        "code_candidate_limit": Hex(bounds + 20),
        "code_candidate_other": Hex(transmission + _pc_word(data, 0x77D24)),
        "code_request_bounds": [
            Hex(_same("upper bound", *(transmission + _pc_word(data, a) for a in (0x77864, 0x7915A)))),
            Hex(_same("lower bound", *(transmission + _pc_word(data, a) for a in (0x77868, 0x7914C)))),
        ],
        "code_lower_bound_other": Hex(transmission + _pc_word(data, 0x77838)),
        "code_shared_request": Hex(_pc_literal(data, 0x791AE) + _pc_word(data, 0x791B0)),
        "code_reduction_field": Hex(reduction_field),
        "code_reduction_latch": Hex(latch_of(reduction_field)),
        "code_reduction_copy": Hex(transmission + _pc_word(data, 0x642D2)),
        "code_options": [Hex(address) for address in options.values()],
        "code_option_values": [Hex(data[address]) for address in options.values()],
        "code_path_selected": not data[implementation] & 0x01 and not data[options["alternate"]] & 0x80,
        "code_word_b_term_enabled": bool(data[options["word_b_term"]] & 0x01),
        "code_bounds_enabled": bool(data[options["bounds"]] & 0x01),
        "code_reduction_copy_enabled": bool(data[options["reduction_copy"]] & 0x10),
    }


def shift_code_index(byte5: int) -> int:
    """The 0x177 byte 5 code index of FUN_000C4ACE: 15 for bit 7, else bits 3..6."""
    return IDLE_CODE_INDEX if byte5 & 0x80 else (byte5 >> 3) & 0x0F


def read_trc(
    path: Path, *, profile: str = "tuning", can_id: int = TELEMETRY_ID, tick_divisor: int = 1
) -> Capture:
    """Replay a PEAK TRC into snapshots, TCM groups, and joined passes."""
    path = Path(path)
    trace = peak_trc_audit.load_trace(path)
    model = DashboardModel(profile, can_id, tick_divisor)
    snapshots: list[Snapshot] = []
    tcm: list[TcmFrame] = []
    selector_frames: list[tuple[float, int]] = []
    ecu: dict[int, list[tuple[float, bytes]]] = {ACTUAL_ID: [], LIMITED_ID: []}
    group_start = None
    selector = None
    pending: dict[int, tuple[float, bytes]] = {}
    run = None
    for frame in trace.frames:
        seconds = frame.offset_ms / 1000.0
        standard = not frame.extended and not frame.remote
        data = bytes(frame.data)
        if standard and frame.can_id == can_id and len(data) == 8 and not data[0] & 0x0F:
            group_start = seconds
        elif standard and frame.can_id == SELECTOR_ID and data:
            selector = data[0]
            selector_frames.append((seconds, selector))
        elif standard and frame.can_id in ecu and len(data) >= 5:
            ecu[frame.can_id].append((seconds, data))
        elif standard and frame.can_id in (GEAR_ID, SPEED_ID, PHASE_ID):
            if len(data) < 6:
                raise ValueError(f"{path}: short TCM frame 0x{frame.can_id:03X} at {seconds:.3f} s")
            if frame.can_id == GEAR_ID:
                if pending:
                    raise ValueError(f"{path}: incomplete TCM group at {pending[GEAR_ID][0]:.3f} s")
                pending[GEAR_ID] = (seconds, data)
            else:
                if GEAR_ID not in pending or frame.can_id in pending:
                    raise ValueError(f"{path}: TCM frame 0x{frame.can_id:03X} outside a group")
                if (seconds - pending[GEAR_ID][0]) * 1000.0 >= TCM_GROUP_MS:
                    raise ValueError(f"{path}: late TCM frame 0x{frame.can_id:03X}")
                pending[frame.can_id] = (seconds, data)
            if len(pending) == 3:
                tcm.append(
                    TcmFrame(
                        pending[GEAR_ID][0],
                        pending[GEAR_ID][1],
                        pending[SPEED_ID][1],
                        pending[PHASE_ID][1],
                        selector,
                    )
                )
                pending = {}
        snapshot = model.process_frame(
            FrameRecord(
                arbitration_id=frame.can_id,
                data=frame.data,
                timestamp=seconds,
                received_monotonic=seconds,
                is_extended_id=frame.extended,
                is_remote_frame=frame.remote,
            ),
            now=seconds,
        )
        if snapshot is None or not model.schema_verified or group_start is None:
            continue
        if any(name not in model.raw for name in SNAPSHOT_FIELDS):
            continue
        rpm_raw = model.engine_speed_counts
        if rpm_raw is None:
            continue
        if run is None:
            run = snapshot.run
        elif snapshot.run != run:
            raise ValueError(f"{path}: the capture spans more than one producer run")
        raw = model.raw
        snapshots.append(
            Snapshot(
                tick=snapshot.unwrapped_tick,
                first_page_s=group_start,
                rpm_raw=rpm_raw,
                app1_raw=int(raw["app1_raw"]),
                torque_state_raw=int(raw["engine_torque_state_raw"]),
                request_raw=int(raw["throttle_request_bounded_raw"]),
                throttle_target_raw=int(raw["throttle_target_shared_raw"]),
                timing_raw=int(raw["final_timing_raw"]),
                fuel_inhibit_mask=int(raw["fuel_inhibit_mask"]),
            )
        )
    return Capture(
        path,
        sha256_file(path),
        tuple(snapshots),
        tuple(tcm),
        join_passes(snapshots, ecu),
        tuple(selector_frames),
    )


def join_passes(snapshots, ecu) -> tuple[Pass, ...]:
    """Pair snapshot j with the last ECU frames after the first page of snapshot j + 1."""
    starts = [snapshot.first_page_s for snapshot in snapshots]
    latest: dict[int, dict[int, bytes]] = {}
    for can_id, frames in ecu.items():
        by_snapshot: dict[int, bytes] = {}
        for seconds, data in frames:
            index = bisect.bisect_right(starts, seconds) - 1
            if index >= 0:
                by_snapshot[index] = data
        latest[can_id] = by_snapshot
    passes = []
    for index, snapshot in enumerate(snapshots[:-1]):
        if snapshots[index + 1].tick != snapshot.tick + 1:
            continue
        actual = latest[ACTUAL_ID].get(index + 1)
        limited = latest[LIMITED_ID].get(index + 1)
        if actual is None or limited is None:
            continue
        passes.append(
            Pass(
                snapshot,
                actual_word=actual[2] << 4 | actual[3] >> 4,
                request_word=(actual[3] & 0x0F) << 8 | actual[4],
                limited_word=limited[0] << 4 | limited[1] >> 4,
                parallel_word=(limited[1] & 0x0F) << 8 | limited[2],
            )
        )
    return tuple(passes)


def shift_events(tcm) -> list[ShiftEvent]:
    events = []
    count = len(tcm)
    for index in range(1, count):
        frame = tcm[index]
        if frame.target == tcm[index - 1].target:
            continue
        if not (1 <= frame.target <= 7 and 1 <= frame.current <= 7):
            continue
        if frame.target == frame.current:
            continue
        end = index
        completed = False
        while end < count:
            if tcm[end].current == frame.target:
                completed = True
                break
            if tcm[end].target != frame.target:
                break
            end += 1
        window_end = next(
            (k for k in range(index, count) if tcm[k].shift_code == IDLE_SHIFT_CODE), count - 1
        )
        events.append(
            ShiftEvent(
                index, min(end, count - 1), window_end, completed, frame.current, frame.target
            )
        )
    return events


def status_episodes(tcm, default_word_b: int) -> list[Episode]:
    runs: list[list[int]] = []
    for index, frame in enumerate(tcm):
        if frame.status != STATUS_EPISODE_VALUE:
            continue
        if runs and frame.seconds - tcm[runs[-1][1]].seconds <= EPISODE_GAP_S:
            runs[-1][1] = index
            runs[-1][2] += 1
        else:
            runs.append([index, index, 1])
    episodes = []
    for start, end, value_frames in runs:
        settled = end + 1
        while settled < len(tcm) - RAMP_SETTLE_FRAMES and not all(
            tcm[settled + step].word_b == default_word_b for step in range(RAMP_SETTLE_FRAMES)
        ):
            settled += 1
        episodes.append(Episode(start, end, min(settled, len(tcm) - 1), value_frames))
    return episodes


def reduction_bursts(tcm) -> list[tuple[int, int]]:
    """Index ranges of nonzero 0x177 byte 4 runs that tolerate BURST_ZERO_GAP zeros."""
    bursts = []
    index = 0
    count = len(tcm)
    while index < count:
        if not tcm[index].reduction:
            index += 1
            continue
        end = index
        while True:
            ahead = next(
                (
                    step
                    for step in range(1, BURST_ZERO_GAP + 2)
                    if end + step < count and tcm[end + step].reduction
                ),
                None,
            )
            if ahead is None:
                break
            end += ahead
        bursts.append((index, end))
        index = end + 1
    return bursts


def mechanical_gear(output_speed: int, turbine_speed: int) -> int | None:
    """Gear whose inverse RE5R05A ratio matches output / turbine within the tolerance."""
    if turbine_speed <= 0:
        return None
    ratio = output_speed / turbine_speed
    for gear, gear_ratio in RE5R05A_RATIOS.items():
        inverse = 1.0 / gear_ratio
        if abs(ratio - inverse) <= RATIO_TOLERANCE * inverse:
            return gear
    return 0


def _frame_at(times, seconds) -> int:
    return bisect.bisect_right(times, seconds) - 1


def _snapshot_at(snapshots, starts, seconds) -> Snapshot:
    return snapshots[max(0, bisect.bisect_right(starts, seconds) - 1)]


def _between(items, times, start, end):
    return items[bisect.bisect_left(times, start) : bisect.bisect_right(times, end)]


def _before(items, times, start, end):
    return items[bisect.bisect_left(times, start) : bisect.bisect_left(times, end)]


def _run_count(times, gap) -> int:
    runs = 0
    previous = None
    for seconds in times:
        if previous is None or seconds - previous > gap:
            runs += 1
        previous = seconds
    return runs


def _rounded(value: float, digits: int = 3) -> float:
    return round(value, digits)


def audit_capture(path: Path, code: dict) -> dict:
    capture = read_trc(path)
    floors = code["code_floor_values"]
    tcm = capture.tcm
    passes = capture.passes
    snapshots = capture.snapshots
    tcm_times = [frame.seconds for frame in tcm]
    pass_times = [item.seconds for item in passes]
    snapshot_starts = [snapshot.first_page_s for snapshot in snapshots]
    default_word_b = statistics.mode(frame.word_b for frame in tcm)
    events = shift_events(tcm)
    episodes = status_episodes(tcm, default_word_b)
    bursts = reduction_bursts(tcm)

    def event_of(index, last):
        return next(
            (event for event in events if event.target_index <= index <= last(event)), None
        )

    # Status episodes and word B.
    episode_windows = []
    episode_rows = []
    for episode in episodes:
        start_s = tcm[episode.start_index].seconds
        end_s = tcm[episode.end_index].seconds
        settled_s = tcm[episode.settled_index].seconds
        window = (start_s - EPISODE_MARGIN_S[0], settled_s + EPISODE_MARGIN_S[1])
        episode_windows.append(window)
        event = event_of(episode.start_index, lambda item: item.end_index)
        if event is None or not event.completed:
            raise ValueError(f"{path}: status episode at {start_s:.3f} s outside a completed shift")
        ramp = [tcm[k].word_b for k in range(episode.end_index + 1, episode.settled_index + 1)]
        target = tcm[event.target_index]
        code_index = shift_code_index(target.shift_code)
        window_passes = _between(passes, pass_times, *window)
        floor_items = [
            item
            for item in window_passes
            if item.snapshot.request_raw == floors[code_index]
            and item.request_word != pack(item.snapshot.request_raw)
        ]
        floor_ticks = [item.snapshot.tick for item in floor_items]
        floor_requests = [unpack(item.request_word) for item in floor_items]
        episode_rows.append(
            {
                "shift": event.name,
                "selector": target.selector,
                "rpm": _snapshot_at(snapshots, snapshot_starts, target.seconds).rpm_raw
                * RPM_PER_COUNT,
                "start_s": start_s,
                "value_frames": episode.value_frames,
                "gap_frames": episode.end_index - episode.start_index + 1 - episode.value_frames,
                "start_delay_s": start_s - target.seconds,
                "seconds": end_s - start_s,
                "end_lead_s": tcm[event.end_index].seconds - end_s,
                "word_b_during": sorted(
                    {
                        tcm[k].word_b
                        for k in range(episode.start_index, episode.end_index + 1)
                        if tcm[k].status == STATUS_EPISODE_VALUE
                    }
                ),
                "word_b_restart": ramp[0],
                "word_b_steps": sorted({b - a for a, b in zip(ramp, ramp[1:])} - {0}),
                "ramp_s": settled_s - end_s,
                "request_mismatch_passes": sum(
                    1
                    for item in window_passes
                    if item.request_word != pack(item.snapshot.request_raw)
                ),
                "shift_code": code_index,
                "floor_passes": len(floor_ticks),
                "floor_tick_span": floor_ticks[-1] - floor_ticks[0] + 1 if floor_ticks else 0,
                "floor_start_s": [_rounded(floor_items[0].seconds)] if floor_items else [],
                "floor_request_range": (
                    [min(floor_requests), max(floor_requests)] if floor_requests else []
                ),
            }
        )

    def in_episode(seconds):
        return any(start <= seconds <= end for start, end in episode_windows)

    episode_targets = {
        event.target_index
        for event in events
        for episode in episodes
        if event.target_index <= episode.start_index <= event.end_index
    }
    downshifts = []
    for event in events:
        if event.upshift:
            continue
        target = tcm[event.target_index]
        snapshot = _snapshot_at(snapshots, snapshot_starts, target.seconds)
        downshifts.append(
            {
                "shift": event.name,
                "rpm": snapshot.rpm_raw * RPM_PER_COUNT,
                "app1": snapshot.app1_raw,
                "selector": target.selector,
                "episode": event.target_index in episode_targets,
            }
        )

    # 0x177 byte 4 bursts and the divergence of the actual-torque word.
    burst_rows = []
    for start, end in bursts:
        start_s = tcm[start].seconds
        window = _between(
            passes, pass_times, start_s - BURST_MARGIN_S[0], tcm[end].seconds + BURST_MARGIN_S[1]
        )
        burst_rows.append(
            {
                "start_s": start_s,
                "end_s": tcm[end].seconds,
                "frames": sum(1 for k in range(start, end + 1) if tcm[k].reduction),
                "event": event_of(start, lambda item: item.window_end_index),
                "diverged": [item for item in window if item.diverged],
            }
        )
    burst_windows = [
        (row["start_s"] - BURST_MARGIN_S[0], row["end_s"] + BURST_MARGIN_S[1])
        for row in burst_rows
    ]
    divergence = [item for item in passes if item.diverged]
    in_burst = [
        item for item in divergence
        if any(start <= item.seconds <= end for start, end in burst_windows)
    ]
    in_status = [
        item for item in divergence if item not in in_burst and in_episode(item.seconds)
    ]

    burst_upshifts = []
    for row in burst_rows:
        event = row["event"]
        if event is None or not event.upshift or not row["diverged"]:
            continue
        reference = _before(
            snapshots, snapshot_starts, row["start_s"] - BURST_REFERENCE_S, row["start_s"]
        )
        diverged = row["diverged"]
        burst_upshifts.append(
            {
                "shift": event.name,
                "onset_lag_s": diverged[0].seconds - row["start_s"],
                "app1_before": reference[-1].app1_raw,
                "app1_min": min(item.snapshot.app1_raw for item in diverged),
                "timing_base": statistics.median_low(item.timing_raw for item in reference),
                "timing_min": min(item.snapshot.timing_raw for item in diverged),
                "word_gap_min": min(item.actual_word - item.parallel_word for item in diverged),
            }
        )
    upshift_without_burst = 0
    upshift_without_burst_divergence = 0
    for event in events:
        if not event.upshift or any(row["event"] is event for row in burst_rows):
            continue
        upshift_without_burst += 1
        window = _between(
            passes,
            pass_times,
            tcm[event.target_index].seconds,
            tcm[event.window_end_index].seconds + DIVERGENCE_TAIL_S,
        )
        upshift_without_burst_divergence += sum(1 for item in window if item.diverged)

    # Request word identity and its binding to word B.
    mismatches = [item for item in passes if item.request_word != pack(item.snapshot.request_raw)]
    status_times = [frame.seconds for frame in tcm if frame.status == STATUS_EPISODE_VALUE]
    mismatch_lags = []
    for item in mismatches:
        index = bisect.bisect_right(status_times, item.seconds) - 1
        if index >= 0:
            mismatch_lags.append(item.seconds - status_times[index])
    binding = 0
    binding_equal = 0
    binding_unequal_s = []
    for item in passes:
        index = _frame_at(tcm_times, item.seconds)
        candidates = {
            tcm[k].word_b
            for k in range(max(0, index - BINDING_FRAMES + 1), index + 1)
            if item.seconds - tcm[k].seconds <= BINDING_WINDOW_S
        } - {default_word_b}
        if not candidates or unpack(item.request_word) <= max(map(unpack, candidates)):
            continue
        binding += 1
        if any(item.snapshot.request_raw == unpack(word) for word in candidates):
            binding_equal += 1
        else:
            binding_unequal_s.append(_rounded(item.seconds))

    # Gear signal.
    phase_frames = 0
    phase_equal = 0
    phase_gears = set()
    ratio_frames = 0
    ratio_matched = 0
    ratio_other_gear = 0
    ratios: dict[int, list[float]] = {gear: [] for gear in RE5R05A_RATIOS}
    for frame in tcm:
        if frame.selector not in DRIVE_SELECTORS and frame.selector not in MANUAL_SELECTORS:
            continue
        if not 1 <= frame.current <= 5 or frame.target != frame.current:
            continue
        if frame.shift_code != IDLE_SHIFT_CODE:
            continue
        phase_frames += 1
        phase_equal += frame.gear_phase == frame.current - 1
        phase_gears.add(frame.current)
        if frame.turbine_speed < RATIO_MIN_TURBINE or frame.output_speed < RATIO_MIN_OUTPUT:
            continue
        ratio_frames += 1
        ratios[frame.current].append(frame.output_speed / frame.turbine_speed)
        gear = mechanical_gear(frame.output_speed, frame.turbine_speed)
        if gear == frame.current:
            ratio_matched += 1
        elif gear:
            ratio_other_gear += 1
    manual_frames = 0
    manual_equal = 0
    manual_positions = set()
    for seconds, selector in capture.selector_frames:
        index = _frame_at(tcm_times, seconds)
        if selector not in MANUAL_SELECTORS or index < 0:
            continue
        manual_frames += 1
        manual_equal += MANUAL_SELECTORS[selector] == tcm[index].target
        manual_positions.add(MANUAL_SELECTORS[selector])

    # Closed-pedal downshifts and the shared throttle target.
    closed_rise = []
    closed_max = []
    for event in events:
        if event.upshift:
            continue
        start_s = tcm[event.target_index].seconds
        window = _between(
            snapshots, snapshot_starts, start_s, tcm[event.window_end_index].seconds
        )
        if not window or any(snapshot.app1_raw > CLOSED_PEDAL_APP1 for snapshot in window):
            continue
        start = _snapshot_at(snapshots, snapshot_starts, start_s)
        peak = max(snapshot.throttle_target_raw for snapshot in window)
        closed_rise.append(peak - start.throttle_target_raw)
        closed_max.append(peak)

    codes: dict[str, set[int]] = {}
    constant_codes = 0
    for event in events:
        codes.setdefault(event.name, set()).add(tcm[event.target_index].shift_code)
        values = {tcm[k].shift_code for k in range(event.target_index, event.window_end_index)}
        constant_codes += len(values) == 1 and IDLE_SHIFT_CODE not in values
    boundaries = {event.target_index for event in events} | {
        event.window_end_index for event in events
    }
    return {
        "capture": capture,
        "snapshot_count": len(snapshots),
        "pass_count": len(passes),
        "tcm_group_count": len(tcm),
        "counter_pair_count": len(tcm) - 1,
        "counter_step_count": sum(
            1 for k in range(1, len(tcm)) if (tcm[k].counter - tcm[k - 1].counter) % 16 == 1
        ),
        "status_bit4_count": sum(1 for frame in tcm if frame.gear[4] & 0x10),
        "status_values": sorted({frame.status for frame in tcm}),
        "status_value_3_frames": sum(1 for frame in tcm if frame.status == STATUS_EPISODE_VALUE),
        "word_a_values": sorted({frame.word_a for frame in tcm}),
        "word_b_default": default_word_b,
        "word_b_other_frames": sum(1 for frame in tcm if frame.word_b != default_word_b),
        "word_b_other_outside_episodes": sum(
            1
            for frame in tcm
            if frame.word_b != default_word_b and not in_episode(frame.seconds)
        ),
        "episodes": episode_rows,
        "event_count": len(events),
        "upshift_count": sum(1 for event in events if event.upshift),
        "downshift_count": sum(1 for event in events if not event.upshift),
        "incomplete_event_count": sum(1 for event in events if not event.completed),
        "downshifts": downshifts,
        "shift_codes": codes,
        "event_shift_code_constant_count": constant_codes,
        "shift_code_changes_outside_events": sum(
            1
            for k in range(1, len(tcm))
            if tcm[k].shift_code != tcm[k - 1].shift_code and k not in boundaries
        ),
        "burst_count": len(bursts),
        "burst_frames": sum(row["frames"] for row in burst_rows),
        "bursts_outside_events": sum(1 for row in burst_rows if row["event"] is None),
        "burst_upshift_count": sum(
            1 for row in burst_rows if row["event"] is not None and row["event"].upshift
        ),
        "burst_downshift_count": sum(
            1 for row in burst_rows if row["event"] is not None and not row["event"].upshift
        ),
        "burst_upshift_divergence_count": len(burst_upshifts),
        "burst_downshift_divergence_passes": sum(
            len(row["diverged"])
            for row in burst_rows
            if row["event"] is not None and not row["event"].upshift
        ),
        "burst_upshifts": burst_upshifts,
        "upshift_without_burst_count": upshift_without_burst,
        "upshift_without_burst_divergence_passes": upshift_without_burst_divergence,
        "divergence_passes": len(divergence),
        "divergence_below_parallel_passes": sum(
            1 for item in divergence if item.actual_word < item.parallel_word
        ),
        "divergence_in_burst_passes": len(in_burst),
        "divergence_in_status_passes": len(in_status),
        "divergence_other_passes": len(divergence) - len(in_burst) - len(in_status),
        "fuel_inhibit_passes": sum(1 for item in passes if item.snapshot.fuel_inhibit_mask),
        "request_identity_passes": len(passes) - len(mismatches),
        "request_mismatch_passes": len(mismatches),
        "request_mismatch_above_passes": sum(
            1 for item in mismatches if pack(item.snapshot.request_raw) > item.request_word
        ),
        "request_mismatch_runs": _run_count(
            [item.seconds for item in mismatches], BINDING_WINDOW_S
        ),
        "request_mismatch_outside_episodes": sum(
            1 for item in mismatches if not in_episode(item.seconds)
        ),
        "request_mismatch_without_status": len(mismatches) - len(mismatch_lags),
        "request_mismatch_status_lag_max_s": _rounded(max(mismatch_lags, default=0.0)),
        "limited_equals_request_passes": sum(
            1 for item in passes if item.limited_word == item.request_word
        ),
        "binding_passes": binding,
        "binding_equal_passes": binding_equal,
        "binding_unequal_s": binding_unequal_s,
        "phase_frames": phase_frames,
        "phase_equal_frames": phase_equal,
        "phase_gears": sorted(phase_gears),
        "ratio_frames": ratio_frames,
        "ratio_matched_frames": ratio_matched,
        "ratio_other_gear_frames": ratio_other_gear,
        "ratios": ratios,
        "manual_frames": manual_frames,
        "manual_equal_frames": manual_equal,
        "manual_positions": sorted(manual_positions),
        "closed_pedal_downshift_count": len(closed_rise),
        "closed_pedal_target_rise_max": max(closed_rise, default=0),
        "closed_pedal_target_max": max(closed_max, default=0),
    }


PER_CAPTURE_KEYS = (
    "snapshot_count",
    "pass_count",
    "tcm_group_count",
    "counter_pair_count",
    "counter_step_count",
    "status_bit4_count",
    "status_value_3_frames",
    "word_b_other_frames",
    "word_b_other_outside_episodes",
    "event_count",
    "upshift_count",
    "downshift_count",
    "incomplete_event_count",
    "event_shift_code_constant_count",
    "shift_code_changes_outside_events",
    "burst_count",
    "burst_frames",
    "bursts_outside_events",
    "burst_upshift_count",
    "burst_downshift_count",
    "burst_upshift_divergence_count",
    "burst_downshift_divergence_passes",
    "upshift_without_burst_count",
    "upshift_without_burst_divergence_passes",
    "divergence_passes",
    "divergence_below_parallel_passes",
    "divergence_in_burst_passes",
    "divergence_in_status_passes",
    "divergence_other_passes",
    "fuel_inhibit_passes",
    "request_identity_passes",
    "request_mismatch_passes",
    "request_mismatch_above_passes",
    "request_mismatch_runs",
    "request_mismatch_outside_episodes",
    "request_mismatch_without_status",
    "request_mismatch_status_lag_max_s",
    "limited_equals_request_passes",
    "binding_passes",
    "binding_equal_passes",
    "binding_unequal_s",
    "phase_frames",
    "phase_equal_frames",
    "ratio_frames",
    "ratio_matched_frames",
    "ratio_other_gear_frames",
    "manual_frames",
    "manual_equal_frames",
    "closed_pedal_downshift_count",
    "closed_pedal_target_rise_max",
    "closed_pedal_target_max",
)
EPISODE_KEYS = (
    "shift",
    "selector",
    "rpm",
    "start_s",
    "value_frames",
    "gap_frames",
    "start_delay_s",
    "seconds",
    "end_lead_s",
    "word_b_during",
    "word_b_restart",
    "word_b_steps",
    "ramp_s",
    "request_mismatch_passes",
    "shift_code",
    "floor_passes",
    "floor_tick_span",
    "floor_start_s",
    "floor_request_range",
)
BURST_UPSHIFT_KEYS = (
    "shift",
    "onset_lag_s",
    "app1_before",
    "app1_min",
    "timing_base",
    "timing_min",
    "word_gap_min",
)


def _column(value):
    return _rounded(value) if isinstance(value, float) else value


def combine(results: list[dict]) -> dict:
    """Figures of several captures in the order given."""
    episodes = [
        (index, row) for index, result in enumerate(results) for row in result["episodes"]
    ]
    upshifts = [
        (index, row) for index, result in enumerate(results) for row in result["burst_upshifts"]
    ]
    downshifts = [row for result in results for row in result["downshifts"]]
    status_downshifts = [row for row in downshifts if row["episode"]]
    status_types = {row["shift"] for row in status_downshifts}
    same_type = [row for row in downshifts if row["shift"] in status_types and not row["episode"]]
    other_type = [row for row in downshifts if row["shift"] not in status_types]
    drive = [row for row in downshifts if row["selector"] in DRIVE_SELECTORS]
    codes: dict[str, set[int]] = {}
    for result in results:
        for shift, values in result["shift_codes"].items():
            codes.setdefault(shift, set()).update(values)
    ordered = sorted(codes, key=lambda shift: (min(codes[shift]), shift))
    medians = []
    for gear in RE5R05A_RATIOS:
        values = [ratio for result in results for ratio in result["ratios"][gear]]
        medians.append(_rounded(statistics.median(values), 4) if values else 0.0)
    combined = {
        "captures": [result["capture"].path.name for result in results],
        "capture_sha256": [result["capture"].sha256 for result in results],
    }
    combined.update({key: [result[key] for result in results] for key in PER_CAPTURE_KEYS})
    combined.update(
        {
            "status_values": sorted({v for result in results for v in result["status_values"]}),
            "word_a_values": sorted({v for result in results for v in result["word_a_values"]}),
            "word_b_default": sorted({result["word_b_default"] for result in results}),
            "phase_gears": sorted({g for result in results for g in result["phase_gears"]}),
            "manual_positions": sorted(
                {p for result in results for p in result["manual_positions"]}
            ),
            "episode_capture_index": [index for index, _ in episodes],
        }
    )
    combined.update(
        {f"episode_{key}": [_column(row[key]) for _, row in episodes] for key in EPISODE_KEYS}
    )
    combined["burst_upshift_capture_index"] = [index for index, _ in upshifts]
    combined.update(
        {
            f"burst_upshift_{key}": [_column(row[key]) for _, row in upshifts]
            for key in BURST_UPSHIFT_KEYS
        }
    )
    combined.update(
        {
            "status_downshift_count": len(status_downshifts),
            "status_downshift_rpm_range": [
                min((row["rpm"] for row in status_downshifts), default=0.0),
                max((row["rpm"] for row in status_downshifts), default=0.0),
            ],
            "same_type_downshift_count": len(same_type),
            "same_type_downshift_rpm_range": [
                min((row["rpm"] for row in same_type), default=0.0),
                max((row["rpm"] for row in same_type), default=0.0),
            ],
            "other_type_downshift_count": len(other_type),
            "drive_downshift_count": len(drive),
            "drive_downshift_app1_max": max((row["app1"] for row in drive), default=0),
            "shift_code_shifts": ordered,
            "shift_code_values": [sorted(value >> 3 for value in codes[shift]) for shift in ordered],
            "ratio_medians": medians,
        }
    )
    return combined


def result_lines(result: dict) -> list[str]:
    return [f"{key} = {mlg_relation_audit.format_value(value)}" for key, value in result.items()]


def audit(captures: list[Path], rom: Path = STOCK_ROM) -> dict:
    """ROM identity, the path facts of that ROM, and the combined capture figures."""
    data = Path(rom).read_bytes()
    code = interface_code(data)
    result = {
        "rom_sha256": sha256_file(rom),
        "code_matches_stock": code == interface_code(STOCK_ROM.read_bytes()),
        "scalar_source": Hex(_pc_literal(data, SCALAR_LOAD)),
    }
    result.update(code)
    result.update(combine([audit_capture(path, code) for path in captures]))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument(
        "--rom",
        type=Path,
        default=STOCK_ROM,
        help="ROM image that ran during the captures (default: the stock JK08A ROM)",
    )
    args = parser.parse_args(argv)
    for line in result_lines(audit(args.captures, args.rom)):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
