"""Four-image stock-code gates for two candidate local count conversions.

The fixed spans are retained literals from the separate identity fixture, not
values extracted from a loaded image. This module supplies its own SHA locks,
named scale tests, observations, and arithmetic oracles. It reuses PathSh2 without
changing that interpreter or invoking the identity tests as scale evidence.
Explicit-axis execution covers exact/end points only. Implicit-byte execution
includes fractional interpolation. No instruction relocation or stock stub is
used; instruction mutants exist only in memory as negative fixtures.
"""

from __future__ import annotations

import ast
import csv
from fractions import Fraction
import hashlib
from itertools import product
from pathlib import Path
import re

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import COMMON, PATHS, PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_local_count_scales.py"
SPEC = "defs/JK08A.local-count-scales.md"
OWNER = "defs/JK08A.findings.csv"
IMAGE_FIXTURES = {
    "JK00A": "ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118",
    "JK03A": "f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4",
    "JK03B": "a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a",
    "JK08A": "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23",
}
SPANS = {
    "c98e": PATHS["c98e"] + COMMON["word-axis"] + COMMON["word-2d"] + COMMON["finish"],
    "1295c": PATHS["1295c"] + COMMON["implicit-byte"] + COMMON["implicit"] + COMMON["finish"],
}
CENTER_RAW = (0, 1, 0x7FFE, 0x7FFF, 0x8000, 0x8001, 0xFFFE, 0xFFFF)
BOUND_RAW = (0, 1, 127, 128, 129, 254, 255)
SCALE_KEYS = {
    0xC98E: "test_c98e_centered_word_scale",
    0x1295C: "test_1295c_local_bound_scale",
}


def _bind(data: bytes, key: str) -> None:
    for address, encoded in SPANS[key]:
        expected = bytes.fromhex(encoded)
        assert data[address:address + len(expected)] == expected, f"{key}: stock span {address:08x}"


@pytest.fixture(params=tuple(IMAGE_FIXTURES), scope="module")
def image(request) -> bytes:
    name = request.param
    data = romkit.load(name).data
    assert hashlib.sha256(data).hexdigest() == IMAGE_FIXTURES[name], name
    for key in SPANS:
        _bind(data, key)
    assert data[0x83C1] == 0x2C
    assert data[0xC98E:0xCB8E] == bytes.fromhex("8000") * 256
    assert data[0x1295C:0x12964] == b"\x80" * 8
    return data


def _patch(data: bytes, address: int, value: bytes) -> bytes:
    changed = bytearray(data)
    changed[address:address + len(value)] = value
    return bytes(changed)


def _word(machine: PathSh2, address: int, value: int) -> None:
    machine.seed_word(address, value & 0xFFFF)


def _map_reads(machine: PathSh2, address: int, size: int, width: int) -> None:
    found = [(pc, at, count) for pc, at, count in machine.loads if address <= at < address + size]
    assert found and all(count == width and at + count <= address + size for _, at, count in found)


def _center_source(data: bytes, raw: int | None, row: int = 0, column: int = 0) -> PathSh2:
    if raw is not None:
        data = _patch(data, 0xC98E, raw.to_bytes(2, "big") * 256)
    data = _patch(data, 0x83C1, bytes([data[0x83C1] | 2]))
    machine = PathSh2(data)
    _word(machine, 0xFFFF11B6, column)
    _word(machine, 0xFFFF412A, row)
    machine.run(0x7B2D2, (0x262A8,))
    assert (machine.r[4], machine.r[5], machine.r[6], machine.r[7]) == (
        0xC98E, 0x13478, 0x13498, row)
    assert machine.peek(STACK_TOP - 2, 2) == column
    machine.run(0x262A8, (0x7B2F6,))
    assert machine.r[15] == STACK_TOP - 4
    machine.run(0x7B2F6, (0x7B30A,))
    return machine


def _center_consumer(machine: PathSh2, other: int, lower: int, upper: int, flags: int) -> None:
    _word(machine, 0xFFFF413A, lower)
    _word(machine, 0xFFFF4138, upper)
    machine.seed(0xFFFF41FB, bytes([flags]))
    # The other term's producer and divider are not executed.
    machine.r[0] = other & 0xFFFF
    machine.run(0x7B35A, (0x7B3A0,))


def _center_case(data: bytes, raw: int, other: int = 0, lower: int = -32768,
                 upper: int = 32767, flags: int = 0) -> PathSh2:
    machine = _center_source(data, raw)
    _center_consumer(machine, other, lower, upper, flags)
    return machine


def test_c98e_centered_word_scale(image: bytes) -> None:
    _bind(image, "c98e")
    executed = set()
    for raw, other, bounds, flags in product(
        CENTER_RAW, (-32768, -1, 0, 1, 32767),
        ((-32768, 32767), (-100, 100), (0, 0)), (0, 0x10, 0x20, 0x30),
    ):
        lower, upper = bounds
        centered = raw - 32768
        expected = min(upper, max(lower, centered + other))
        if flags & 0x20:
            expected = upper
        if flags & 0x10:
            expected = lower
        machine = _center_case(image, raw, other, lower, upper, flags)
        _map_reads(machine, 0xC98E, 512, 2)
        assert machine.stored(0xFFFF2C6E) == [(0x7B308, 2, centered & 0xFFFF)]
        assert sext(machine.peek(0xFFFF2C6E, 2), 16) == centered
        assert (0x7B35E, 0xFFFF2C6E, 2) in machine.loads
        assert machine.stored(0xFFFF2C6C) == [(0x7B390, 2, expected & 0xFFFF)]
        executed.update(machine.executed)
    assert {0x7B2F2, 0x7B2F4, 0x262A8, 0x26984, 0x26848, 0x2688E,
            0x7B304, 0x7B308, 0x7B35E, 0x7B364, 0x7B366, 0x7B368,
            0x7B36A, 0x7B36E, 0x7B370, 0x7B372, 0x7B374, 0x7B378,
            0x7B37E, 0x7B380, 0x7B384, 0x7B388, 0x7B38A, 0x7B38E, 0x7B390} <= executed
    assert not {0x26740, 0x26C78, 0x26D10, 0x26AF8} & executed


def test_c98e_stock_disabled_lookup_has_no_centered_sample(image: bytes) -> None:
    machine = PathSh2(image)
    _word(machine, 0xFFFF243C, 0xABCD)
    machine.run(0x7B2D2, (0x7B3A0,))
    assert machine.stored(0xFFFF2C6C) == [(0x7B39E, 2, 0xABCD)]
    assert not machine.stored(0xFFFF2C6E)
    assert 0x7B2DE in machine.executed and 0x262A8 not in machine.executed
    assert not any(0xC98E <= address < 0xCB8E for _, address, _ in machine.loads)


def test_c98e_exact_and_clamped_axis_endpoints_select_distinct_cells(image: bytes) -> None:
    cells = [0x8000] * 256
    witnesses = {0: 1, 15: 0x7FFF, 240: 0x8001, 255: 0xFFFF}
    for index, value in witnesses.items():
        cells[index] = value
    data = _patch(image, 0xC98E, b"".join(value.to_bytes(2, "big") for value in cells))
    for row, column in product((0, 65535), repeat=2):
        machine = _center_source(data, None, row, column)
        index = (240 if row == 65535 else 0) + (15 if column == 65535 else 0)
        expected = witnesses[index] - 32768
        _map_reads(machine, 0xC98E, 512, 2)
        assert any(address == 0xC98E + index * 2 and width == 2
                   for _, address, width in machine.loads)
        assert sext(machine.peek(0xFFFF2C6E, 2), 16) == expected
        assert not {0x26C78, 0x26D10, 0x26AF8} & set(machine.executed)


def _bound_source(data: bytes, cells: bytes, coolant: int = 0) -> PathSh2:
    machine = PathSh2(_patch(data, 0x1295C, cells))
    for site in (0x44A30, 0x44A34):
        machine.run(site, (site + 2,))
    machine.seed(0xFFFF106F, bytes([coolant]))
    machine.run(0x44A46, (0x44A5C,))
    return machine


def _bound_consumer(machine: PathSh2, value: int, branch: str, added: int = 0) -> None:
    if branch == "first":
        machine.r[2] = value & MASK
        machine.run(0x453AC, (0x45446,))
    else:
        assert branch == "second"
        _word(machine, STACK_TOP + 8, value)
        machine.seed(0xFFFF13F7, bytes([added]))
        machine.run(0x455B4, (0x455DE,))


def _bound_case(data: bytes, raw: int, value: int, branch: str, added: int = 0) -> PathSh2:
    machine = _bound_source(data, bytes([raw]) * 8)
    _bound_consumer(machine, value, branch, added)
    return machine


def _normal_completion(machine: PathSh2, added: int) -> None:
    machine.seed(0xFFFF15B4, bytes([added]))
    machine.r[9] = 0
    machine.run(0x455EA, (0x45620,))


def test_1295c_local_bound_scale(image: bytes) -> None:
    _bind(image, "1295c")
    executed = set()
    for raw in BOUND_RAW:
        bound = 2 * raw
        for value in (-32768, -1, 0, bound - 1, bound, bound + 1, 32767):
            machine = _bound_case(image, raw, value, "first")
            _map_reads(machine, 0x1295C, 8, 1)
            assert machine.stored(0xFFFF172E) == [(0x44A5A, 1, raw)]
            assert (0x453B2, 0xFFFF172E, 1) in machine.loads
            assert machine.stored(STACK_TOP + 8) == [(0x45444, 2, min(value, bound) & 0xFFFF)]
            executed.update(machine.executed)
            for added in (0, 1, 255):
                machine = _bound_case(image, raw, value, "second", added)
                local = min(value + added, bound)
                assert machine.stored(0xFFFF172E) == [(0x44A5A, 1, raw)]
                assert (0x455C6, 0xFFFF172E, 1) in machine.loads
                assert machine.stored(STACK_TOP + 8) == [(0x455DC, 2, local & 0xFFFF)]
                for final_added in (0, 1, 255):
                    completed = _bound_case(image, raw, value, "second", added)
                    _normal_completion(completed, final_added)
                    assert completed.stored(0xFFFF1230) == [
                        (0x4561E, 2, min(local + 2 * final_added, 32767) & 0xFFFF)]
                    executed.update(completed.executed)
                executed.update(machine.executed)
    assert {0x44A50, 0x44A52, 0x26370, 0x26A80, 0x26740, 0x44A5A,
            0x453B8, 0x453BC, 0x453BE, 0x453C0, 0x453C2, 0x45444,
            0x455CC, 0x455D0, 0x455D2, 0x455D4, 0x455D6, 0x455D8,
            0x455DC, 0x45606, 0x4561E} <= executed


def test_each_unsigned_byte_reaches_both_local_count_bounds(image: bytes) -> None:
    for raw, branch in product(range(256), ("first", "second")):
        machine = _bound_case(image, raw, 2 * raw + 1, branch)
        assert machine.stored(0xFFFF172E) == [(0x44A5A, 1, raw)]
        assert machine.peek(STACK_TOP + 8, 2) == 2 * raw


def _implicit_lookup(cells: bytes, coolant: int) -> int:
    if coolant >= 224:
        return cells[7]
    index, remainder = divmod(coolant, 32)
    left, right = cells[index:index + 2]
    if right >= left:
        return left + (right - left) * remainder // 32
    return left - (left - right) * remainder // 32


def test_1295c_fractional_and_terminal_lookups_feed_the_local_consumer(image: bytes) -> None:
    cells = bytes((0, 1, 127, 128, 255, 129, 254, 0))
    for coolant in (0, 1, 15, 31, 32, 33, 63, 64, 95, 96, 127, 128,
                    159, 160, 191, 192, 223, 224, 225, 255):
        machine = _bound_source(image, cells, coolant)
        raw = _implicit_lookup(cells, coolant)
        assert machine.stored(0xFFFF172E) == [(0x44A5A, 1, raw)]
        assert (0x44A4C, 0xFFFF106F, 1) in machine.loads
        _map_reads(machine, 0x1295C, 8, 1)
        assert machine.r[15] == STACK_TOP
        if coolant < 224:
            assert {0x26A80, 0x26740} <= set(machine.executed)
        else:
            assert 0x26A80 not in machine.executed and 0x26740 not in machine.executed
        _bound_consumer(machine, 2 * raw + 1, "second")
        assert machine.peek(STACK_TOP + 8, 2) == 2 * raw


def test_1295c_local_bound_is_not_a_universal_final_output_bound(image: bytes) -> None:
    machine = _bound_case(image, 128, 300, "second")
    assert machine.peek(0xFFFF172E) == 128
    assert machine.peek(STACK_TOP + 8, 2) == 256
    _normal_completion(machine, 255)
    assert machine.stored(0xFFFF1230) == [(0x4561E, 2, 766)]
    assert 766 > 2 * 128
    alternate = _bound_case(image, 128, 300, "second")
    alternate.r[9] = 1
    alternate.run(0x455EA, (0x2C626,))
    assert {0x455F2, 0x455F4} <= set(alternate.executed)
    assert 0x2C626 not in alternate.executed and not alternate.stored(0xFFFF1230)


@pytest.mark.parametrize("local,added", ((32765, 1), (32766, 1), (32767, 0), (32767, 255)))
def test_normal_saturation_uses_an_independent_incoming_operand(image: bytes, local: int, added: int) -> None:
    machine = PathSh2(image)
    _word(machine, STACK_TOP + 8, local)
    _normal_completion(machine, added)
    assert machine.stored(0xFFFF1230) == [(0x4561E, 2, min(local + 2 * added, 32767))]
    assert not machine.stored(0xFFFF172E)
    assert (0x45618 in machine.executed) and (0x45616 in machine.executed) == (local + 2 * added <= 32767)


SPAN_MUTANTS = (
    ("c98e", 0x7B3C7, 1), ("c98e", 0x7B2E2, 1),
    ("c98e", 0x7B35F, 1), ("c98e", 0x7B370, 4),
    ("c98e", 0x7B390, 1), ("c98e", 0x7B304, 1),
    ("1295c", 0x44B7B, 1), ("1295c", 0x44A4E, 1),
    ("1295c", 0x455C7, 1), ("1295c", 0x455D7, 1),
    ("1295c", 0x453BC, 4), ("1295c", 0x45606, 1),
)


@pytest.mark.parametrize("key,address,xor", SPAN_MUTANTS)
def test_fixed_spans_reject_literal_register_width_branch_and_delay_mutants(
    image: bytes, key: str, address: int, xor: int,
) -> None:
    changed = _patch(image, address, bytes([image[address] ^ xor]))
    with pytest.raises(AssertionError, match="stock span"):
        _bind(changed, key)


def test_execution_mutants_change_centering_and_signed_word_observations(image: bytes) -> None:
    # No _bind call is made on these negative instruction fixtures.
    expected = 0x8001 - 32768
    stock = _center_case(image, 0x8001)
    assert sext(stock.peek(0xFFFF2C6E, 2), 16) == expected
    for address in (0x7B302, 0x7B304):
        changed = _patch(image, address, bytes.fromhex("0009"))
        machine = _center_case(changed, 0x8001)
        assert sext(machine.peek(0xFFFF2C6E, 2), 16) != expected
    changed = _patch(image, 0x7B35E, bytes.fromhex("0ecc"))
    machine = _center_case(changed, 0x8001, lower=-100, upper=100)
    assert sext(machine.peek(0xFFFF2C6E, 2), 16) == expected
    assert machine.peek(0xFFFF2C6C, 2) == 0 != expected


def test_execution_mutants_change_both_local_bounds_and_normal_completion(image: bytes) -> None:
    # Observational helpers return machine state separately from the oracle.
    for branch, site in (("first", 0x453C2), ("second", 0x455D6)):
        assert _bound_case(image, 128, 300, branch).peek(STACK_TOP + 8, 2) == 256
        changed = _patch(image, site, bytes.fromhex("0009"))
        assert _bound_case(changed, 128, 300, branch).peek(STACK_TOP + 8, 2) == 128
    changed = _patch(image, 0x453B8, bytes.fromhex("0009"))
    assert _bound_case(image, 128, 200, "first").peek(STACK_TOP + 8, 2) == 200
    assert _bound_case(changed, 128, 200, "first").peek(STACK_TOP + 8, 2) == 256
    changed = _patch(image, 0x455C8, bytes.fromhex("0009"))
    machine = _bound_case(changed, 128, 300, "second")
    assert sext(machine.peek(STACK_TOP + 8, 2), 16) == -256
    changed = _patch(image, 0x45612, bytes.fromhex("0009"))
    machine = _bound_case(changed, 128, 300, "second")
    _normal_completion(machine, 255)
    assert machine.peek(0xFFFF1230, 2) == 511 != 766
    changed = _patch(image, 0x45606, bytes.fromhex("0009"))
    machine = PathSh2(changed)
    _word(machine, STACK_TOP + 8, 32766)
    _normal_completion(machine, 1)
    assert machine.peek(0xFFFF1230, 2) == 32768 != 32767
    changed = _patch(image, 0x45610, bytes.fromhex("8b02"))
    machine = PathSh2(changed)
    _word(machine, STACK_TOP + 8, 32767)
    _normal_completion(machine, 1)
    assert machine.peek(0xFFFF1230, 2) == 32769 != 32767


@pytest.mark.parametrize("entry", (0x26C78, 0x26D10, 0x26AF8))
def test_fractional_explicit_axis_entries_remain_outside_the_gate(image: bytes, entry: int) -> None:
    with pytest.raises(AssertionError, match="fractional explicit-axis path outside gate"):
        PathSh2(image).run(entry, (entry + 2,))


def test_compiled_table_owners_bind_candidate_scale_tests_and_ast() -> None:
    from kb import checks, compile, match, repo
    from kb.model import SymbolKey

    model = compile.cached(repo.ROOT)
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    expected = {
        0xC98E: ("raw with offset 32768", "x-32768", "x+32768"),
        0x1295C: ("raw", "x*2", "x/2"),
    }
    with (ROOT / OWNER).open(newline="") as source:
        rows = {int(row["addr"], 16): row for row in csv.DictReader(source)}
    for address, key in SCALE_KEYS.items():
        unit, scale, inverse = expected[address]
        row = rows[address]
        assert (row["confidence"], row["scale_conf"], row["units"], row["scale_expr"], row["to_byte"]) == (
            "candidate", "candidate", unit, scale, inverse)
        assert row["scale_evidence"] == f"test:{THIS_TEST}#{key}"
        symbol = model.symbols[SymbolKey("7mfk", "tbl", address)]
        assert OWNER in symbol.sources
        assert {name: symbol.value(name) for name in ("unit", "scale", "to_raw", "scale_level")} == {
            "unit": unit, "scale": scale, "to_raw": inverse, "scale_level": "candidate"}
        [item] = [item for item in symbol.evidence if item.get("kind") == "test"
                  and item.get("path") == THIS_TEST]
        assert item == {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": key}
        assert key in functions and match.verify(model, symbol, item) is None
        broken = {**item, "key": "test_missing_local_count_scale"}
        assert "defines no function" in match.verify(model, symbol, broken)
        original = symbol.evidence
        try:
            symbol.evidence = [broken if existing is item else existing for existing in original]
            issues = [issue for issue in checks.homology(model) if issue.subject == symbol.key.key]
            assert any("test_missing_local_count_scale" in issue.message for issue in issues)
        finally:
            symbol.evidence = original


def test_count_inverses_and_specification_keep_the_local_domains() -> None:
    for raw in range(65536):
        centered = sext((raw - 32768) & 0xFFFF, 16)
        assert centered == raw - 32768
        assert centered + 32768 == raw
    for raw in range(256):
        assert Fraction(2 * raw, 2) == raw
    assert Fraction(3, 2).denominator != 1
    text = (ROOT / SPEC).read_text()
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text, re.IGNORECASE)
    assert THIS_TEST in text and "rom-images/roms.csv" in text
    for name in IMAGE_FIXTURES:
        assert f'| `{name}` | `IMAGE_FIXTURES["{name}"]` |' in text
    for address, key in SCALE_KEYS.items():
        assert f"`{address:08x}`" in text and key in text
    normalized = " ".join(text.split())
    for required in ("candidate", "raw-32768", "2*raw", "sample", "domain",
                     "stock-disabled", "exact/end points", "fractional", "766",
                     "ffff15b4", "independent incoming operand", "not a universal final-output bound",
                     "physical quantity", "no hardware validation", "0002c626"):
        assert required in normalized
