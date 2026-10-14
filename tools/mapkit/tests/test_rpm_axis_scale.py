"""Four-image stock-byte gates for four candidate nominal RPM axis scales.

Each named image is independently SHA-locked, bound to fixed expected spans,
and executed. Identical expectations are stored once; no live image supplies
another image's expected bytes. The physical conversion comes from a pinned
external community PID fragment, not an ECU name, map shape, or generated scale.

The producer is executed as three conversion segments, with the intervening
filter calculations and producer-helper calls/returns outside this gate. The
56-byte copier and diagnostic byte writer execute their real calls and returns.
Axis callers and the first wrapper call execute up to the byte-axis sample read;
wrapper/helper returns, fractional interpolation, and complete ECU functions are
outside the placement/conversion proof. No stock-function stubs or instruction
relocations are used. Mutants change only in-memory negative fixtures.
"""

from __future__ import annotations

import ast
import copy
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tomllib

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, STACK_TOP, Sh2, sext

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_rpm_axis_scale.py"
SPEC = "defs/JK08A.rpm-axis-scale.md"
SOURCE_ROOT = ROOT / "refs/diagnostics/public/370z-can-logger"
DATASET = "370z-can-logger-2025-07-05"
REVISION = "2decbc957523ee46dd39b3e3a7594e23ad7eee97"
DOCUMENT = f"{DATASET}:candata-standard-pids-csv"
FRAGMENT = f"{DOCUMENT}:l0014-l0014:source-row-standard-pids"
SOURCE_URL = f"https://github.com/TihanPelser/370Z-CAN-Logger/blob/{REVISION}/candata/standard_pids.csv"
# These expectations do not come from the current retained corpus at test time.
SOURCE_FIELDS = {
    "PID": "0C", "Bytes": "2", "Description": "Engine RPM",
    "Units": "rpm", "Formula": "((A*256)+B)/4",
}

# All four independently inspected images have these exact conversion,
# placement, and calibration spans. Their separate digests are below.
COMMON = {
    "producer": (
        (0x38506, "d028401ed62a6261d62a622d420942016d2d626060d3c10a"),
        (0x38552, "d416"),
        (0x38560, "901c4d094d01042460d3bf80c110"),
        (0x38572, "c50ae5ff655c660d46094609460136568b0066536063bf04c012"),
        (0x3859C, "02a5"),
        (0x385A8, "ffff11d4ffff1ff4"),
        (0x385B4, "ffff119600008743"),
    ),
    "snapshot": (
        (0x20EFE, "de82"),
        (0x21108, "000220f8"),
        (0x20F5A, "d47cd67c6241d17c2621d67c62612421d27c4e0be038"),
        (0x2114C, "ffff1194ffff1198ffff119cffff1196ffff11d4"),
        (0x220F8, "2f36d305033e70fc432b002e"),
        (0x22110, "00022158"),
        (0x2211E, "532c110d502b113c532a110b5029113a5328110950271138532611075025113653241105502311345322110350211132632211012132000b63f6"),
        (0x22190, "0002211e"),
    ),
    "publisher": (
        (0x35D04, "880c8b18d64fe020026d662de2320267e6ff666d021a32668f011f296263e0280f25642dd244420b4419e028d242420b04fda0e00009"),
        (0x35E3C, "00037acc"),
        (0x35E48, "ffff11d4"),
        (0x37ACC, "d107d507e6e362139009666c326c065c606c0244660390027601000b056405e1ffff39c4"),
    ),
    "axis-core": ((0x26944, "6343014c611c351089163516"),),
}
AXES = {
    "banana": {
        "address": 0x12858, "points": "1020304050607080", "count": 8,
        "key": "test_banana_shark_nominal_rpm_scale",
        "segments": ((0xBEFBE, 0x26944),),
        "source_site": 0xBEFD2, "call": 0xBEFD8, "wrapper": 0x26140,
        "literal": 0xBF174,
        "spans": (
            (0xBEFBE, "dc6add6a62c1d46a602dd56a4019d66a80f3e01202dcde69db634e0b672c"),
            (0xBF164, "ffff28f8ffff1024ffff119c0000b23a000128580001286000026140"),
            (0x26140, "4f222f46677c60536573d70a470be407"),
            (0x26174, "00026944"),
        ),
    },
    "vegan": {
        "address": 0x120AE, "points": "1020304050607080", "count": 8,
        "key": "test_vegan_fulmar_nominal_rpm_scale",
        "segments": ((0xBEFBE, 0xBEFC2), (0xBEFD4, 0xBEFD8), (0xBEFE4, 0x26944)),
        "source_site": 0xBEFF2, "call": 0xBEFF4, "wrapper": 0x26140,
        "literal": 0xBF184,
        "spans": (
            (0xBEFBE, "dc6add6a"), (0xBEFD4, "de69db63"),
            (0xBEFE4, "62c1d567602dd667401980f3e01202dc4e0b672c"),
            (0xBF164, "ffff28f8ffff1024ffff119c"),
            (0xBF17C, "000261400000ab0a000120ae000120b6"),
            (0x26140, "4f222f46677c60536573d70a470be407"),
            (0x26174, "00026944"),
        ),
    },
    "resilient": {
        "address": 0x11B6B, "points": "0c1014182028323c46505a646e788296", "count": 16,
        "key": "test_resilient_eagle_nominal_rpm_scale",
        "segments": ((0x8329A, 0x26944),),
        "source_site": 0x832B2, "call": 0x832B6, "wrapper": 0x26320,
        "literal": 0x8336C,
        "spans": (
            (0x8329A, "d632da2f6261d4316d2dd5314d19d63160d380f3e012d2300eacdb26420b67ec"),
            (0x83350, "ffff28f8"), (0x8335C, "ffff119c"),
            (0x83364, "ffff10240000b81a00011b6b00011b8b00026320"),
            (0x26320, "4f222f46677c60536573d70a470be40f"),
            (0x26354, "00026944"),
        ),
    },
    "dashing": {
        "address": 0x1264A, "points": "0c1014182028323c46505a646e788296", "count": 16,
        "key": "test_dashing_whippet_nominal_rpm_scale",
        "segments": ((0x83978, 0x26944),),
        "source_site": 0x8397E, "call": 0x83988, "wrapper": 0x264A0,
        "literal": 0x83A44,
        "spans": (
            (0x83978, "de30c04ee01202ecd42fda30662cd930490b65a3"),
            (0x83A3C, "ffff119c0001261a0001264a000264a0"),
            (0x264A0, "4f222f466053656cd707470be40f"),
            (0x264C8, "00026944"),
        ),
    },
}
IMAGE_FIXTURES = {
    "JK00A": ("ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118", COMMON, AXES),
    "JK03A": ("f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4", COMMON, AXES),
    "JK03B": ("a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a", COMMON, AXES),
    "JK08A": ("ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23", COMMON, AXES),
}


class ScaleSh2(Sh2):
    """Three local integer forms: SHLR, GBR MOV.W store, GBR MOV.W load."""

    def __init__(self, data):
        super().__init__(data)
        self.executed = []

    def _execute(self, pc, opcode):
        assert pc != 0x26C78, "fractional interpolation is outside this gate"
        self.executed.append(pc)
        n = (opcode >> 8) & 15
        if opcode & 0xF0FF == 0x4001:
            self.t = self.r[n] & 1
            self.r[n] >>= 1
        elif opcode >> 8 == 0xC1:
            self._write(self.gbr + (opcode & 255) * 2, 2, self.r[0], pc)
        elif opcode >> 8 == 0xC5:
            self.r[0] = sext(self._read(self.gbr + (opcode & 255) * 2, 2, pc), 16) & MASK
        else:
            return super()._execute(pc, opcode)
        return None


def _bind(data, *groups):
    for group in groups:
        spans = COMMON[group] if group in COMMON else AXES[group]["spans"]
        for address, encoded in spans:
            expected = bytes.fromhex(encoded)
            assert data[address:address + len(expected)] == expected, f"{group}: {address:08x}"
        if group in AXES:
            axis = AXES[group]
            expected = bytes.fromhex(axis["points"])
            address = axis["address"]
            assert data[address:address + len(expected)] == expected


@pytest.fixture(params=tuple(IMAGE_FIXTURES), scope="module")
def image(request):
    name = request.param
    data = romkit.load(name).data
    digest, common, axes = IMAGE_FIXTURES[name]
    assert hashlib.sha256(data).hexdigest() == digest
    assert common is COMMON and axes is AXES
    _bind(data, *COMMON, *AXES)
    return data


def _validate_source(manifest, document, fragment):
    assert (manifest["id"], manifest["revision"], manifest["source_tier"],
            manifest["applicability_status"]) == (DATASET, REVISION, "community", "homologous_community")
    assert (document["id"], document["dataset_id"], document["filename"],
            document["revision"], document["source_url"], document["applicability_status"]) == (
                DOCUMENT, DATASET, "candata/standard_pids.csv", REVISION,
                SOURCE_URL, "homologous_community")
    assert (fragment["id"], fragment["dataset_id"], fragment["document_id"],
            fragment["line_start"], fragment["line_end"], fragment["kind"]) == (
                FRAGMENT, DATASET, DOCUMENT, 14, 14, "source_row_standard_pids")
    assert hashlib.sha256(fragment["text"].encode()).hexdigest() == fragment["text_sha256"]
    record = json.loads(fragment["text"])
    actual = {key: record[key] for key in SOURCE_FIELDS}
    # The width is numeric; CSV forms 2 and 2.0 both denote the independently
    # expected two bytes. Formula, unit, quantity, and PID remain exact strings.
    assert Fraction(actual.pop("Bytes")) == Fraction(SOURCE_FIELDS["Bytes"])
    assert actual == {key: value for key, value in SOURCE_FIELDS.items() if key != "Bytes"}


@pytest.fixture(scope="module")
def source_claim():
    # This is an offline corpus contract: actual retained source records are
    # compared with the independent literals above, never used as expectations.
    manifest = tomllib.loads((SOURCE_ROOT / "source_pack.toml").read_text())
    with (SOURCE_ROOT / "documents.csv").open(newline="", encoding="utf-8") as source:
        [document] = [row for row in csv.DictReader(source) if row["id"] == DOCUMENT]
    with (SOURCE_ROOT / "fragments.jsonl").open(encoding="utf-8") as source:
        [fragment] = [row for line in source if (row := json.loads(line))["id"] == FRAGMENT]
    _validate_source(manifest, document, fragment)
    return manifest, document, fragment


def _producer(data, value, *, bind=True):
    if bind:
        _bind(data, "producer")
    machine = ScaleSh2(data)
    # Other copied source fields and the previous snapshot are explicit inputs.
    machine.seed(0xFFFF11D4, b"\0" * 56)
    machine.seed(0xFFFF119C, b"\xa5" * 56)
    machine.seed_word(0xFFFF1196, value)
    machine.seed_word(0xFFFF1194, 0x1234)
    machine.run(0x38506, (0x3851E,))
    # The preserved conversion operands bridge separately reviewed segments;
    # the intervening filter and producer-helper returns are not simulated.
    # The middle segment also writes an unrelated byte; its stock destination
    # base and offset loads execute, without claiming that byte's value.
    machine.run(0x38552, (0x38554,))
    machine.run(0x38560, (0x3846E,))
    machine.run(0x38572, (0x38394,))
    return machine


def _snapshot(machine, *, bind=True):
    if bind:
        _bind(machine.data, "snapshot")
    before = bytes(machine.peek(0xFFFF11D4 + offset) for offset in range(56))
    machine.run(0x20EFE, (0x20F00,))  # Actual stock load of the copier pointer.
    machine.run(0x20F5A, (0x20F70,))
    assert bytes(machine.peek(0xFFFF119C + offset) for offset in range(56)) == before
    assert (0x2213E, 0xFFFF11E4, 4) in machine.loads
    assert any(pc == 0x22144 and at == 0xFFFF11AC and size == 4
               for pc, at, size, _ in machine.stores)
    assert machine.r[15] == STACK_TOP
    return machine.peek(0xFFFF11AE)


def _publisher(data, word, *, pid=0x0C, bind=True):
    if bind:
        _bind(data, "publisher")
    machine = ScaleSh2(data)
    # This segment receives the PID in R0 after the earlier dispatcher checks.
    # Counter zero isolates its two data bytes, excluding response headers.
    machine.r[0] = pid
    machine.seed_word(0xFFFF11F4, word)
    machine.seed(0xFFFF3FA5, b"\0")
    machine.run(0x35D04, (0x35D36, 0x35D3A))
    count = machine.peek(0xFFFF3FA5)
    payload = bytes(machine.peek(0xFFFF3AA7 + offset) for offset in range(count))
    return payload, machine


def _axis_input(machine, name, expected, *, bind=True):
    if bind:
        _bind(machine.data, "axis-core", name)
    axis = AXES[name]
    machine.seed_word(0xFFFF1024, 0x0123)  # Independent second-coordinate input.
    machine.seed(STACK_TOP, b"\0" * 4)
    # Incoming GBR of the diagnostic caller; only its unrelated flag store
    # uses it in the placement segment. RPM base loads execute in stock code.
    machine.gbr = 0xFFFF4184
    machine.r[0] = 0
    for start, stop in axis["segments"]:
        machine.run(start, (stop,))
    assert (machine.r[0], machine.r[4], machine.r[5]) == (
        axis["address"], axis["count"] - 1, expected)
    assert (axis["source_site"], 0xFFFF11AE, 1) in machine.loads
    assert axis["call"] in machine.executed and axis["wrapper"] in machine.executed
    machine.run(0x26944, (0x2694C,))
    assert (0x26946, axis["address"] + axis["count"] - 1, 1) in machine.loads
    assert machine.r[1] == bytes.fromhex(axis["points"])[-1]
    assert machine.t == int(expected == machine.r[1])


def _decode(payload):
    assert len(payload) == 2
    return Fraction(payload[0] * 256 + payload[1], 4)


def _nominal_path(data, source, name):
    _validate_source(*source)
    # All residual classes, both low-six-bit endpoints, and byte boundaries.
    for byte in (0, 1, 15, 16, 127, 128, 149, 150, 254, 255):
        for remainder in (0, 64, 128, 192, 255):
            value = byte * 256 + remainder
            machine = _producer(data, value)
            word = machine.peek(0xFFFF11F4, 2)
            assert word == value >> 6 and word <= 1023
            assert machine.peek(0xFFFF11E8, 2) == value >> 3
            assert machine.stored(0xFFFF11F4) == [(0x3856C, 2, word)]
            assert machine.stored(0xFFFF11E6) == [(0x3858A, 1, byte)]
            assert _snapshot(machine) == byte
            payload, publisher = _publisher(data, word)
            assert payload == (50 * word).to_bytes(2, "big")
            assert _decode(payload) - 50 * byte == Fraction((word % 4) * 25, 2)
            assert publisher.r[15] == STACK_TOP
            _axis_input(machine, name, byte)


def test_banana_shark_nominal_rpm_scale(image, source_claim):
    _nominal_path(image, source_claim, "banana")


def test_vegan_fulmar_nominal_rpm_scale(image, source_claim):
    _nominal_path(image, source_claim, "vegan")


def test_resilient_eagle_nominal_rpm_scale(image, source_claim):
    _nominal_path(image, source_claim, "resilient")


def test_dashing_whippet_nominal_rpm_scale(image, source_claim):
    _nominal_path(image, source_claim, "dashing")


def test_every_byte_and_residual_class_has_the_nominal_quantum(image):
    for byte in range(256):
        for low in (0, 63, 64, 127, 128, 191, 192, 255):
            value = 256 * byte + low
            machine = _producer(image, value)
            assert machine.peek(0xFFFF11F4, 2) == value >> 6
            assert machine.peek(0xFFFF11E6) == byte
            assert Fraction(25 * machine.peek(0xFFFF11F4, 2), 2) - 50 * byte in (
                Fraction(0), Fraction(25, 2), Fraction(25), Fraction(75, 2))


@pytest.mark.parametrize("word", (0, 1, 1023, 1310, 1311, 65535))
def test_publisher_unsigned_word_and_independent_saturation_boundary(image, source_claim, word):
    # 1310/1311 and 65535 are independent publisher operands, outside W <= 1023
    # produced from U16. They do not assert attainable production engine speed.
    _validate_source(*source_claim)
    payload, machine = _publisher(image, word)
    assert payload == min(65535, 50 * word).to_bytes(2, "big")
    assert _decode(payload) == Fraction(min(65535, 50 * word), 4)
    assert (0x35D0C, 0xFFFF11F4, 2) in machine.loads
    assert [pc for pc in machine.executed if pc == 0x37ADE] == [0x37ADE, 0x37ADE]
    assert all(size == 1 for pc, _, size, _ in machine.stores if pc == 0x37ADE)


def test_other_pid_does_not_publish_the_rpm_bytes(image):
    payload, _ = _publisher(image, 160, pid=0x0D)
    assert payload == b""


@pytest.mark.parametrize("word,expected", ((8191, 255), (8192, 255), (65535, 255)))
def test_byte_cap_with_independent_pre_conversion_word(image, word, expected):
    # E8 > 8191 is an isolated boundary input, not derived from production U16.
    machine = ScaleSh2(image)
    machine.gbr = 0xFFFF11D4
    machine.seed_word(0xFFFF11E8, word)
    machine.run(0x38572, (0x38394,))
    assert machine.stored(0xFFFF11E6) == [(0x3858A, 1, expected)]


def _patch(data, address, value, size=2):
    changed = bytearray(data)
    changed[address:address + size] = value.to_bytes(size, "big")
    return bytes(changed)


AXIS_MUTANTS = {
    "banana": ((0xBF174, 0x120AE, 4), (0xBEFD2, 0x03DC, 2),
               (0xBEFD2, 0x02DD, 2), (0xBEFDA, 0x670C, 2)),
    "vegan": ((0xBF184, 0x12858, 4), (0xBEFF2, 0x03DC, 2),
              (0xBEFF2, 0x02DD, 2), (0xBEFF6, 0x670C, 2)),
    "resilient": ((0x8336C, 0x1264A, 4), (0x832B2, 0x0FAC, 2),
                  (0x832B2, 0x0EAD, 2), (0x832B8, 0x67DC, 2)),
    "dashing": ((0x83A44, 0x11B6B, 4), (0x8397E, 0x03EC, 2),
                (0x8397E, 0x02ED, 2), (0x8398A, 0x6593, 2)),
}


@pytest.mark.parametrize("name", tuple(AXES))
def test_axis_literal_register_width_and_delay_mutants_are_rejected(image, name):
    for address, value, size in AXIS_MUTANTS[name]:
        with pytest.raises(AssertionError):
            _bind(_patch(image, address, value, size), name)


@pytest.mark.parametrize("group,address,value,size", (
    ("producer", 0x385B4, 0xFFFF1194, 4),
    ("producer", 0x38514, 0x4200, 2),
    ("producer", 0x3856C, 0xC010, 2),
    ("producer", 0x3858A, 0xC013, 2),
    ("snapshot", 0x21154, 0xFFFF119E, 4),
    ("snapshot", 0x20F6E, 0xE034, 2),
    ("snapshot", 0x22190, 0x22122, 4),
    ("snapshot", 0x22144, 0x1135, 2),
    ("publisher", 0x35D10, 0xE231, 2),
    ("publisher", 0x35D1C, 0xA001, 2),
    ("publisher", 0x35D2C, 0x0009, 2),
    ("publisher", 0x37ADE, 0x0245, 2),
    ("axis-core", 0x26946, 0x014D, 2),
))
def test_shared_conversion_operands_are_bound_independently(image, group, address, value, size):
    with pytest.raises(AssertionError):
        _bind(_patch(image, address, value, size), group)


def test_arithmetic_endian_saturation_and_copy_mutants_change_observations(image):
    # Negative fixtures deliberately bypass the span assertion, so execution
    # demonstrates the incorrect observation rather than only a changed byte.
    changed = _patch(image, 0x38514, 0x4200)
    assert _producer(changed, 256, bind=False).peek(0xFFFF11F4, 2) != 4
    changed = _patch(image, 0x3858A, 0xC013)
    assert _producer(changed, 256, bind=False).peek(0xFFFF11E6) != 1
    changed = _patch(image, 0x35D10, 0xE231)
    assert _publisher(changed, 160, bind=False)[0] != bytes.fromhex("1f40")
    changed = _patch(image, 0x35D1C, 0xA001)
    assert _publisher(changed, 1311, bind=False)[0] == bytes.fromhex("000e")
    changed = _patch(image, 0x35D2C, 0x0009)
    assert _publisher(changed, 160, bind=False)[0] == bytes.fromhex("4040")
    changed = _patch(image, 0x37ADE, 0x0245)
    assert _publisher(changed, 160, bind=False)[0] == bytes.fromhex("001f")
    machine = _producer(_patch(image, 0x22144, 0x1135), 32768)
    with pytest.raises(AssertionError):
        _snapshot(machine, bind=False)


@pytest.mark.parametrize("name", tuple(AXES))
def test_axis_byte_width_mutant_changes_the_actual_input(image, name):
    address, value, size = AXIS_MUTANTS[name][2]
    machine = _producer(_patch(image, address, value, size), 32768)
    _snapshot(machine)
    with pytest.raises(AssertionError):
        _axis_input(machine, name, 128, bind=False)


@pytest.mark.parametrize("field,value", (("PID", "0D"), ("Units", "count"),
                                          ("Formula", "((A*256)+B)/8"), ("Bytes", "1")))
def test_source_formula_and_context_mutants_cannot_refresh_expectations(source_claim, field, value):
    manifest, document, fragment = copy.deepcopy(source_claim)
    record = json.loads(fragment["text"])
    record[field] = value
    fragment["text"] = json.dumps(record, ensure_ascii=False, sort_keys=True)
    fragment["text_sha256"] = hashlib.sha256(fragment["text"].encode()).hexdigest()
    with pytest.raises(AssertionError):
        _validate_source(manifest, document, fragment)


def test_source_revision_and_fragment_identity_are_pinned(source_claim):
    for at, key, value in ((0, "revision", "0" * 40), (1, "revision", "0" * 40),
                           (2, "line_start", 15), (2, "document_id", "another-document")):
        changed = copy.deepcopy(source_claim)
        changed[at][key] = value
        with pytest.raises(AssertionError):
            _validate_source(*changed)


def test_compiled_axis_owners_bind_typed_scale_tests_and_ast():
    from kb import checks, compile, match, repo, store
    from kb.model import SymbolKey

    model = compile.cached(repo.ROOT)
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    for axis in AXES.values():
        symbol = model.symbols[SymbolKey("7mfk", "axis", axis["address"])]
        assert {key: symbol.value(key) for key in ("unit", "scale", "to_raw", "scale_level")} == {
            "unit": "RPM", "scale": "x*50", "to_raw": "x/50", "scale_level": "candidate"}
        assert symbol.sources == {store.path_of("axis", symbol.meaning.name).as_posix()}
        assert checks._owned(model, symbol)
        [item] = [item for item in symbol.evidence if item.get("kind") == "test"
                  and item.get("path") == THIS_TEST]
        assert item == {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": axis["key"]}
        assert item["key"] in functions
        assert match.verify(model, symbol, item) is None
        broken = {**item, "key": "test_missing_rpm_axis_scale"}
        assert "defines no function" in match.verify(model, symbol, broken)
        original = symbol.evidence
        try:
            symbol.evidence = [broken if existing is item else existing for existing in original]
            issues = [issue for issue in checks.homology(model, subjects={symbol.key.key})
                      if issue.subject == symbol.key.key]
            assert any("test_missing_rpm_axis_scale" in issue.message for issue in issues)
        finally:
            symbol.evidence = original


def test_editor_inverse_is_a_grid_inverse_not_a_physical_reconstruction():
    for byte in range(256):
        assert Fraction(50 * byte, 50) == byte
    assert Fraction(25 * 5, 2) == Fraction(125, 2)
    assert Fraction(125, 2) / 50 != 1  # W=5, B=1: discarded sub-byte RPM.
    text = (ROOT / SPEC).read_text()
    for name in IMAGE_FIXTURES:
        assert f'| `{name}` | `IMAGE_FIXTURES["{name}"]` |' in text
    assert "rom-images/roms.csv" in text
    assert "tools/mapkit/tests/test_rpm_axis_scale.py" in text
    for axis in AXES.values():
        assert f"`{axis['address']:08x}`" in text
        assert f"`{axis['literal']:08x}`" in text
    for required in (REVISION, FRAGMENT, "1310", "1311", "1023", "37.5",
                     "candidate", "not an exact inverse", "community"):
        assert required in text


def test_current_rpm_word_note_preserves_quantization_and_sample_age(image):
    from kb import checks, compile, repo, store
    from kb.model import SymbolKey

    model = compile.cached(repo.ROOT)
    symbol = model.symbols[SymbolKey("7mfk", "ram", 0xFFFF11F4)]
    assert symbol.sources == {store.path_of("ram", "authentic-wasp").as_posix()}
    assert checks._owned(model, symbol)
    [note] = symbol.value("note")
    for required in ("W = 4*B + ((U >> 6) & 3)", "nominal", "raw-value equality",
                     "different producer sample", "saturated byte ffff11b3"):
        assert required in note
    assert "four times the RPM/50 value" not in note
    assert "twice the RPM/25 value" not in note
    machine = _producer(image, 64)
    word = machine.peek(0xFFFF11F4, 2)
    byte = machine.peek(0xFFFF11E6)
    assert (word, byte) == (1, 0)
    assert word == 4 * byte + ((64 >> 6) & 3)
    assert word != 4 * _snapshot(machine)
