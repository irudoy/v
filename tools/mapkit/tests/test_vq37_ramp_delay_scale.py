"""Bounded count-scale gates for the 1ME3B throttled-duration delay curve.

Exact/end-point lookup and the byte-to-threshold multiplier execute in place.
Separate publication/call consumers have an explicitly independent incoming R11;
full leaf snapshots bind the reviewed static MACL/R11 preservation between them.
The floating-point intervals and continuous execution of the caller are excluded.
The subclass adds exclusion guards only, not instructions, stubs, or publication.
"""

from __future__ import annotations

import ast
import hashlib
from itertools import product
from pathlib import Path
import re

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_vq37_ramp_delay_scale.py"
SPEC = "defs/VQ37.ramp-delay-scale.md"
OWNER = "kb/tbl/vvel_duration_throttled_ramp_delay.toml"
SCALE_KEY = "test_ramp_delay_local_count_scale"
IMAGE_SHA = "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3"
TABLE, AXIS = 0x1457A, 0x14582
GBR, COUNTER, THRESHOLD, FLAG = 0xFFFEF458, 0xFFFEF4D8, 0xFFFEF4DC, 0xFFFEF4E2
LOOKUP, HELPER = 0x2AC9C, 0x2861E
STOCK_CELLS = (30, 30, 30, 30, 20, 12, 5, 0)
STOCK_AXIS = tuple(range(20, 91, 10))
EXACT_INPUTS = (0, 1, 19, *STOCK_AXIS, 91, 255)
ARMS = ((0x635B4, 0x635CE, 0x635CA, 0x635CC),
        (0x63664, 0x63688, 0x63684, 0x63686))

# Retained instruction/literal bytes, independent of the image loaded by a test.
SPANS = (
    (0x6354A, "d09a401e7ff86a536d63664cd598d498d199410b6c73610ce464041766ad6eddd596d496d797470b2f62620d425af82dc795ff08da8d0b1af8f2fa8a2fe6d692d593d493dd944d0b57f17f04620d425af02dc791f808c791f908d191f89e6ecce601e0843e638d58f187"),
    (0x635B4, "3e630429d57ec6216753777f757fdb8b7701750bdc8a4b0b6603"),
    (0x63664, "c48a20088b0160b3c2213e630429d550c6216753777f757fdb5c7701750bdc5c4b0b6603"),
    (0x637B4, "fffef458000145820001457a0002ac9c00017346000173d60002af883d4ccccc000174d6000174b60001087c0002a0b4c68000003f000000fffef4d80002861e000094a6"),
    (0x2AC9C, "666c6053e207012c611c3612893ee206012c611c3610893936168927e205012c611c3610893236168920e204012c611c3610892b36168919e203012c611c3610892436168912e202012c611c3610891d3616890be201012c611c3610891636168904e200012c611c36168b0f36184628352c8451600c301820088d08e500465af12d405af02df103a001e501e500342c2558891b61408441611c600c3012890b67133108061af13d055a0157011a461a60734129000b30183018061af13d055a0057001a461a4029000b301c000b6040"),
    (0x2AF88, "666d6053e21e012d611d3612897be21c012d611d361089763616895fe21a012d611d3610896f36168958e218012d611d3610896836168951e216012d611d361089613616894ae214012d611d3610895a36168943e212012d611d361089533616893ce210012d611d3610894c36168935e20e012d611d361089453616892ee20c012d611d3610893e36168927e20a012d611d3610893736168920e208012d611d3610893036168919e206012d611d3610892936168912e204012d611d361089223616890be202012d611d3610891b36168904e200012d611d36168b1436184628352c8551600d301820088d0de5004601465af12de102415af22df122405af02df103a001e501e500342c2558891b61418541611d600d3012890b67133108061af13d055a0157011a461a60734129000b30183018061af13d055a0057001a461a4029000b301c000b6041"),
    (0x2A0B4, "677d6053e21e012d611d3712897be21c012d611d371089763716895fe21a012d611d3710896f37168958e218012d611d3710896837168951e216012d611d371089613716894ae214012d611d3710895a37168943e212012d611d371089533716893ce210012d611d3710894c37168935e20e012d611d371089453716892ee20c012d611d3710893e37168927e20a012d611d3710893737168920e208012d611d3710893037168919e206012d611d3710892937168912e204012d611d371089223716890be202012d611d3710891b37168904e200012d611d37168b1437184728352c8551600d301820088d0de5004701475af12de102415af22df122405af02df103a001e501e50063f26063633de71e017d611d3312897be71c017d611d331089763316895fe71a017d611d3310896f33168958e718017d611d3310896833168951e716017d611d331089613316894ae714017d611d3310895a33168943e712017d611d331089533316893ce710017d611d3310894c33168935e70e017d611d331089453316892ee70c017d611d3310893e33168927e70a017d611d3310893733168920e708017d611d3310893033168919e706017d611d3310892933168912e704017d611d331089223316890be702017d611d3310891b33168904e700017d611d33168b1433184328367c8561600d301820088d0de6004301435af32de102415af22df322405af02df303a001e601e600e110031a221e347c021a4100342c314c2668893d67418541677d600df33d065a30728907627337080767071a47293278a005602330780067001a4029307c2558893df13d055a621164038511622d670d37228907612332780267021a42293128a005621337280767071a4729327c604332028907610330280057001a40293108a01d601332080257021a4229a017302c25588d146041f13d055a6211600d622d32028907610330280057001a40293108a005601332080257021a4229302c000b431a"),
    (0x2861E, "644c24488f036163e200a013272262502228890b667276013612890426688902e200a0072762e201a004271221180229e60027622540000b6023"),
)
EXCLUDED = (0x2AD1A, 0x2B076, 0x2A1A4, 0x2A2AE, 0x63576, 0x63582)


class RampSh2(PathSh2):
    """Keep the primary interpreter and reject the excluded float intervals."""

    def _execute(self, pc: int, opcode: int):
        assert pc not in EXCLUDED, "FPUL/float interval outside gate"
        return super()._execute(pc, opcode)


def _bind(data: bytes) -> None:
    for address, encoded in SPANS:
        expected = bytes.fromhex(encoded)
        assert data[address:address + len(expected)] == expected, f"stock span {address:08x}"


@pytest.fixture(scope="module")
def image() -> bytes:
    source = romkit.load("1ME3B")
    assert hashlib.sha256(source.data).hexdigest() == IMAGE_SHA
    _bind(source.data)
    assert tuple(source.values(TABLE, 8, "uint8")) == STOCK_CELLS
    assert tuple(source.values(AXIS, 8, "uint8")) == STOCK_AXIS
    return source.data


def _patch(data: bytes, address: int, values: bytes) -> bytes:
    changed = bytearray(data)
    changed[address:address + len(values)] = values
    return bytes(changed)


def _machine(data: bytes) -> RampSh2:
    machine = RampSh2(data)
    machine.run(0x6354A, (0x6354E,))
    return machine


def _lookup(data: bytes, coordinate: int) -> RampSh2:
    machine = _machine(data)
    machine.r[4] = coordinate
    machine.run(0x63554, (0x63560,))
    return machine


def _factor(data: bytes, returned: int) -> RampSh2:
    machine = _machine(data)
    machine.r[0], machine.r[1] = returned & MASK, 0xA55A5AA5
    machine.run(0x63560, (0x63566,))
    return machine


def _state(machine: RampSh2, threshold: int, counter: int, previous: int) -> None:
    machine.seed(COUNTER - 1, bytes.fromhex("a5"))
    machine.seed(COUNTER, counter.to_bytes(4, "big"))
    machine.seed(THRESHOLD, threshold.to_bytes(4, "big"))
    machine.seed(THRESHOLD + 4, bytes.fromhex("5a"))
    machine.seed(FLAG - 1, bytes.fromhex("c3"))
    machine.seed(FLAG, bytes([previous]))
    machine.seed(FLAG + 1, bytes.fromhex("3c"))


def _consumer(data: bytes, entry: int, incoming_r11: int, mode: int,
              threshold: int, counter: int, previous: int) -> tuple[RampSh2, int]:
    """Execute a separate consumer with an independent incoming R11 and state."""
    machine = _machine(data)
    _state(machine, threshold, counter, previous)
    machine.r[11], machine.r[12] = incoming_r11, mode
    machine.run(0x635A8, (0x635B0,))
    predicate = machine.t
    # The caller's BT/S has an excluded float delay slot; entry is an explicit slice input.
    machine.run(entry, (HELPER,))
    return machine, predicate


def _helper(data: bytes, mode: int, previous: int, threshold: int,
            counter: int) -> RampSh2:
    machine = _machine(data)
    _state(machine, threshold, counter, previous)
    machine.r[4], machine.r[5], machine.r[6], machine.r[7] = mode, FLAG, threshold, COUNTER
    machine.call(HELPER)
    return machine


def _sentinels(machine: RampSh2) -> None:
    assert machine.peek(COUNTER - 1) == 0xA5
    assert machine.peek(THRESHOLD + 4) == 0x5A
    assert machine.peek(FLAG - 1) == 0xC3
    assert machine.peek(FLAG + 1) == 0x3C


@pytest.mark.parametrize("raw", range(256))
def test_ramp_delay_local_count_scale(image: bytes, raw: int) -> None:
    data = _patch(image, TABLE, bytes([raw]) * 8)
    for coordinate in EXACT_INPUTS:
        source = _lookup(data, coordinate)
        assert source.r[0] == sext(raw, 8) & MASK
        source.run(0x63560, (0x63566,))
        assert source.r[1] == raw
        assert source.macl == 100 * raw
        assert {LOOKUP, 0x2AD68, 0x2AD6A, 0x6355C, 0x6355E, 0x63560, 0x63564} <= set(source.executed)
        assert any(TABLE <= at < TABLE + 8 and width == 1 for _, at, width in source.loads)
        assert not set(EXCLUDED) & set(source.executed)
    # This R11 is an independent consumer input, not a claimed continuous caller run.
    consumer, predicate = _consumer(image, 0x63664, 100 * raw, 1, 0xA55A5AA5, 77, 0)
    assert predicate == 1
    assert consumer.gbr == GBR
    assert consumer.r[4:8] == [1, FLAG, 100 * raw, COUNTER]
    assert consumer.stored(THRESHOLD) == [(0x6366C, 4, 100 * raw)]
    assert (0x63674, THRESHOLD, 4) in consumer.loads
    assert {0x63684, 0x63686} <= set(consumer.executed)
    consumer.run(HELPER, (0x63688,))
    assert consumer.r[0] == int(raw == 0)
    assert consumer.peek(COUNTER, 4) == 0
    assert consumer.peek(FLAG) == 1
    _sentinels(consumer)


def test_every_stock_cell_and_clamped_endpoint_is_read_as_one_byte(image: bytes) -> None:
    cells = set()
    for coordinate in EXACT_INPUTS:
        index = 0 if coordinate <= 20 else min(7, coordinate // 10 - 2)
        raw = STOCK_CELLS[index]
        machine = _lookup(image, coordinate)
        assert (0x2AD6A, TABLE + index, 1) in machine.loads
        assert [(at, width) for _, at, width in machine.loads if TABLE <= at < TABLE + 8] == [(TABLE + index, 1)]
        assert machine.r[0] == raw
        machine.run(0x63560, (0x63566,))
        assert machine.r[1] == raw and machine.macl == 100 * raw
        cells.add(index)
    assert cells == set(range(8))
    # The leaf and caller both mask the coordinate to a byte.
    for high in (0x100, 0x12345600, 0xFFFFFF00):
        for coordinate in STOCK_AXIS:
            machine = _lookup(image, high | coordinate)
            assert machine.r[0] == STOCK_CELLS[coordinate // 10 - 2]


@pytest.mark.parametrize("upper", (0, 0x100, 0x12345600, 0xFFFFFF00))
def test_independent_return_upper_bits_do_not_change_the_byte_count(image: bytes, upper: int) -> None:
    for raw in range(256):
        machine = _factor(image, upper | raw)
        assert machine.r[0] == upper | raw
        assert machine.r[1] == raw and machine.macl == 100 * raw
        assert not any(TABLE <= at < TABLE + 8 for _, at, _ in machine.loads)


def test_static_full_call_snapshots_bind_macl_r11_and_threshold_dataflow(image: bytes) -> None:
    _bind(image)
    expected_literals = {
        0x637B4: GBR, 0x637B8: AXIS, 0x637BC: TABLE, 0x637C0: LOOKUP,
        0x637CC: 0x2AF88, 0x637E0: 0x2A0B4, 0x637EC: COUNTER, 0x637F0: HELPER,
    }
    for address, value in expected_literals.items():
        assert int.from_bytes(image[address:address + 4], "big") == value
    # The complete retained leaves bind the reviewed conservation on every branch.
    for address, encoded in (
        (0x63564, "0417"), (0x63570, "470b2f62"), (0x63580, "0b1a"),
        (0x63590, "4d0b57f1"), (0x6366A, "60b3c221"), (0x63674, "c621"),
        (0x63684, "4b0b6603"), (0x635CA, "4b0b6603"),
        (0x2B0A6, "061a"), (0x2B0B0, "461a"),
        (0x2B0BC, "061a"), (0x2B0C6, "461a"),
        (0x2B0CE, "000b6041"), (0x2A2C8, "031a"), (0x2A384, "000b431a"),
    ):
        assert image[address:address + len(bytes.fromhex(encoded))] == bytes.fromhex(encoded)
    # Calls 63570/63590 and their floating-point intervals are not executed here.


@pytest.mark.parametrize("mode,entry,returned,callsite,slot", (
    (0, *ARMS[0]), (0x100, *ARMS[0]),
    (1, *ARMS[1]), (127, *ARMS[1]), (128, *ARMS[1]), (255, *ARMS[1]), (0x101, *ARMS[1]),
))
@pytest.mark.parametrize("previous", (0, 1, 0x80, 0xFF))
def test_mode_arms_and_fresh_retained_threshold_have_separate_inputs(
    image: bytes, mode: int, entry: int, returned: int, callsite: int, slot: int, previous: int,
) -> None:
    incoming, retained = 12345, 6789
    machine, predicate = _consumer(image, entry, incoming, mode, retained, 3, previous)
    active = int((mode & 255) != 0)
    expected = incoming if active and previous == 0 else retained
    assert predicate == active
    assert machine.r[4:8] == [active, FLAG, expected, COUNTER]
    assert machine.peek(THRESHOLD, 4) == expected
    assert machine.stored(THRESHOLD) == ([(0x6366C, 4, incoming)] if active and previous == 0 else [])
    assert (0x635BA if not active else 0x63674, THRESHOLD, 4) in machine.loads
    assert {callsite, slot} <= set(machine.executed)
    machine.run(HELPER, (returned,))
    assert machine.peek(FLAG) == active
    assert machine.peek(COUNTER, 4) == (4 if active and previous else 0)
    assert machine.r[0] == 0
    assert machine.peek(THRESHOLD, 4) == expected
    assert {0x28652, 0x28654, 0x28656} <= set(machine.executed)
    _sentinels(machine)
    if active and previous:
        assert expected != incoming


@pytest.mark.parametrize("threshold", (0, 1, 2, 100, 25500, 0x80000000, MASK))
def test_full_integer_helper_reset_fresh_increment_limit_and_uint32_wrap(image: bytes, threshold: int) -> None:
    counters = sorted({0, 1, 2, 99, 25500, 0x7FFFFFFF, 0x80000000, MASK,
                       (threshold - 2) & MASK, (threshold - 1) & MASK, threshold, (threshold + 1) & MASK})
    reached = set()
    for mode, previous, counter in product((0, 1, 2, 128, 255, 0x100, 0x101), (0, 1, 128, 255), counters):
        active = mode & 255
        if not active:
            expected_count, expected_result = 0, 0
        elif not previous:
            expected_count, expected_result = 0, int(threshold == 0)
        else:
            incremented = (counter + 1) & MASK
            complete = incremented >= threshold or incremented == 0
            expected_count = threshold if complete else incremented
            expected_result = int(complete)
        machine = _helper(image, mode, previous, threshold, counter)
        assert machine.r[0] == expected_result
        assert machine.peek(COUNTER, 4) == expected_count
        assert machine.peek(FLAG) == active
        assert machine.stored(FLAG) == [(0x28652, 1, active)]
        assert len(machine.stored(COUNTER)) == 1
        assert machine.stored(COUNTER)[0][1:] == (4, expected_count)
        assert machine.peek(THRESHOLD, 4) == threshold
        assert not machine.stored(THRESHOLD)
        assert {0x28624, 0x28654, 0x28656} <= set(machine.executed)
        _sentinels(machine)
        reached.update(machine.executed)
    assert {0x28626, 0x2862A, 0x2864A, 0x28650, 0x28644, 0x28648} <= reached
    if threshold >= 2:
        assert {0x2863E, 0x28642} <= reached


def test_initialized_count_uses_one_increment_per_retained_helper_call(image: bytes) -> None:
    for raw in (0, 1, 5, 255):
        threshold = 100 * raw
        machine, _ = _consumer(image, 0x63664, threshold, 1, 12345, 77, 0)
        machine.run(HELPER, (0x63688,))
        assert machine.peek(COUNTER, 4) == 0
        assert machine.r[0] == int(threshold == 0)
        # Repeated helper calls test its counter trajectory, not the full float caller.
        for invocation in range(1, threshold + 2):
            machine.r[4:8] = [1, FLAG, threshold, COUNTER]
            machine.call(HELPER)
            assert machine.peek(COUNTER, 4) == min(invocation, threshold)
            assert machine.r[0] == int(invocation >= threshold)
            assert machine.peek(FLAG) == 1
        assert machine.peek(THRESHOLD, 4) == threshold
        _sentinels(machine)


@pytest.mark.parametrize("coordinate", (21, 25, 35, 85))
def test_nonzero_fraction_lookup_is_an_explicit_excluded_interval(image: bytes, coordinate: int) -> None:
    with pytest.raises(AssertionError, match="FPUL/float interval outside gate"):
        _lookup(image, coordinate)


@pytest.mark.parametrize("entry", EXCLUDED)
def test_float_intervals_are_guarded_not_stubbed(image: bytes, entry: int) -> None:
    machine = _machine(image)
    with pytest.raises(AssertionError, match="FPUL/float interval outside gate"):
        machine.run(entry, (entry + 2,))
    assert entry not in machine.executed
    assert machine.stores == []


SNAPSHOT_MUTANTS = (
    0x63558, 0x63560, 0x63562, 0x63564, 0x63570, 0x63572, 0x63580, 0x63590,
    0x63668, 0x6366A, 0x6366C, 0x63674, 0x63686, 0x637B7, 0x637BB, 0x637BF,
    0x637CF, 0x637E3, 0x637F3, 0x2AD6A, 0x2B0A6, 0x2B0B0, 0x2B0BC, 0x2B0C6,
    0x2A2C8, 0x2A386, 0x28624, 0x28634, 0x28636, 0x28642, 0x28648, 0x28652, 0x28656,
)


@pytest.mark.parametrize("address", SNAPSHOT_MUTANTS)
def test_snapshot_mutants_reject_literals_conservation_and_control_bytes(image: bytes, address: int) -> None:
    changed = _patch(image, address, bytes([image[address] ^ 1]))
    with pytest.raises(AssertionError, match="stock span"):
        _bind(changed)


def test_executed_extension_multiplier_and_lookup_width_mutants(image: bytes) -> None:
    signed = 0xFFFFFF80
    normal = _factor(image, signed)
    extension = _factor(_patch(image, 0x63560, bytes.fromhex("6103")), signed)
    multiplier = _factor(_patch(image, 0x63562, bytes.fromhex("e465")), signed)
    assert normal.macl == 12800
    assert extension.macl != normal.macl
    assert multiplier.macl == 12928
    for machine in (extension, multiplier):
        assert {0x63560, 0x63562, 0x63564} <= set(machine.executed)
    normal = _lookup(image, 50)
    width = _lookup(_patch(image, 0x2AD6A, bytes.fromhex("6041")), 50)
    assert normal.r[0] == 30 and width.r[0] == 0x1E14
    normal.run(0x63560, (0x63566,))
    width.run(0x63560, (0x63566,))
    assert normal.macl == 3000 and width.macl == 2000


def test_executed_publication_and_read_width_mutants(image: bytes) -> None:
    incoming, retained = 0x12345678, 0xABCDEF01
    normal, _ = _consumer(image, 0x63664, incoming, 1, retained, 0, 0)
    narrow, _ = _consumer(_patch(image, 0x6366C, bytes.fromhex("c142")), 0x63664, incoming, 1, retained, 0, 0)
    assert normal.peek(THRESHOLD, 4) == incoming
    assert narrow.stored(THRESHOLD) == [(0x6366C, 2, 0x5678)]
    assert narrow.peek(THRESHOLD, 4) == 0x5678EF01 != incoming
    for entry, site in ((0x635B4, 0x635BA), (0x63664, 0x63674)):
        normal, _ = _consumer(image, entry, incoming, 0 if entry == 0x635B4 else 1, retained, 0, 1)
        narrow, _ = _consumer(_patch(image, site, bytes.fromhex("c542")), entry, incoming,
                              0 if entry == 0x635B4 else 1, retained, 0, 1)
        assert normal.r[6] == retained
        assert narrow.r[6] == 0xFFFFABCD != retained
        assert (site, THRESHOLD, 2) in narrow.loads


def test_executed_counter_comparison_increment_reset_flag_and_delay_mutants(image: bytes) -> None:
    strict = _patch(image, 0x28636, bytes.fromhex("3616"))
    stock = _helper(image, 1, 1, 2, 1)
    mutant = _helper(strict, 1, 1, 2, 1)
    assert stock.r[0] == 1 and mutant.r[0] == 0
    increment = _patch(image, 0x28634, bytes.fromhex("7602"))
    stock = _helper(image, 1, 1, 10, 0)
    mutant = _helper(increment, 1, 1, 10, 0)
    assert stock.peek(COUNTER, 4) == 1 and mutant.peek(COUNTER, 4) == 2
    reset = _patch(image, 0x28626, bytes.fromhex("e201"))
    assert _helper(image, 0, 1, 10, 77).peek(COUNTER, 4) == 0
    assert _helper(reset, 0, 1, 10, 77).peek(COUNTER, 4) == 1
    no_flag = _patch(image, 0x28652, bytes.fromhex("0009"))
    assert _helper(image, 1, 0, 10, 77).peek(FLAG) == 1
    assert _helper(no_flag, 1, 0, 10, 77).peek(FLAG) == 0
    no_return = _patch(image, 0x28656, bytes.fromhex("0009"))
    stock = _helper(image, 1, 1, 10, 0)
    mutant = _helper(no_return, 1, 1, 10, 0)
    assert stock.r[0] == 0 and mutant.r[0] == GBR
    no_latch = _patch(image, 0x28624, bytes.fromhex("0009"))
    stock = _helper(image, 1, 1, 10, 0)
    mutant = _helper(no_latch, 1, 1, 10, 0)
    assert stock.peek(COUNTER, 4) == 1 and mutant.peek(COUNTER, 4) == 0
    assert stock.r[0] == 0 and mutant.r[0] == 1
    no_argument = _patch(image, 0x63686, bytes.fromhex("0009"))
    stock, _ = _consumer(image, 0x63664, 99, 1, 10, 0, 1)
    mutant, _ = _consumer(no_argument, 0x63664, 99, 1, 10, 0, 1)
    assert stock.r[6] == 10 and mutant.r[6] == 1
    stock.run(HELPER, (0x63688,))
    mutant.run(HELPER, (0x63688,))
    assert stock.r[0] == 0 and mutant.r[0] == 1


def test_compiled_owner_binds_scale_evidence_and_ast() -> None:
    from kb import checks, compile, match, repo
    from kb.model import SymbolKey

    model = compile.cached(repo.ROOT)
    symbol = model.symbols[SymbolKey("1me3b", "tbl", TABLE)]
    assert OWNER in symbol.sources
    assert {key: symbol.value(key) for key in ("unit", "scale", "to_raw", "scale_level")} == {
        "unit": "count", "scale": "x", "to_raw": "x", "scale_level": "code"}
    assert symbol.meaning.props["level"] == "code"
    assert symbol.meaning.props["storage"] == "uint8"
    assert (symbol.meaning.props["cols"], symbol.meaning.props["rows"]) == (8, 1)
    assert {layout: status.state for layout, status in symbol.meaning.statuses.items()} == {"1nd": "absent", "jk78c": "absent"}
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    item = {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": SCALE_KEY}
    actual = [e for e in symbol.evidence if e.get("kind") == "test" and e.get("path") == THIS_TEST]
    assert actual == [item]
    assert SCALE_KEY in functions and match.verify(model, symbol, item) is None
    missing = {**item, "key": "test_missing_ramp_delay_scale"}
    assert "defines no function" in match.verify(model, symbol, missing)
    original = symbol.evidence
    try:
        assert not [issue for issue in checks.homology(model, subjects={symbol.key.key})
                    if issue.subject == symbol.key.key and SCALE_KEY in issue.message]
        symbol.evidence = [e for e in original if e not in actual] + [missing]
        issues = [issue for issue in checks.homology(model, subjects={symbol.key.key})
                  if issue.subject == symbol.key.key]
        assert any("test_missing_ramp_delay_scale" in issue.message for issue in issues)
    finally:
        symbol.evidence = original


def test_specification_binds_the_count_contract_and_static_exclusions() -> None:
    from tools import single_source

    text = (ROOT / SPEC).read_text()
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text, re.IGNORECASE)
    assert THIS_TEST in text and SCALE_KEY in text and "rom-images/roms.csv" in text
    assert SPEC in set(single_source._tracked(".md"))
    assert "| `1ME3B` | `IMAGE_SHA` | `0001457a` | `00014582` |" in text
    assert ", ".join(map(str, STOCK_CELLS)) in text
    assert ", ".join(map(str, STOCK_AXIS)) in text
    normalized = " ".join(text.split())
    for required in ("unit `count`", "scale `x`", "inverse `x`", "scale level `code`",
                     "100*u8(return)", "MACL", "R11", "fffef4dc", "2861e",
                     "independent incoming", "retained", "unsigned", "wrap",
                     "exact/end points", "static", "not executed", "FPUL/float",
                     "not continuous", "physical time", "scheduler", "incoming producers",
                     "final actuator output", "no hardware validation"):
        assert required in normalized
