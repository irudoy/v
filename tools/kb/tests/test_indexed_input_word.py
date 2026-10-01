"""Fixed-byte placement of one software-indexed input word.

This is a reader-only slice of C1DEC, not a whole-function execution gate.
The earlier state machine and all callees are outside the slice. Caller tests
check targets and delay slots at opaque call boundaries, not callee behavior.
Controlled flags and coefficient words establish branch geometry, not stock
reachability, physical meaning, engineering units, or the C1152 writer.
"""

from dataclasses import replace
import hashlib

import pytest

from kb import compile, derive, match, repo, sh2
from kb.model import SymbolKey


KEY = SymbolKey("7mfk", "ram", 0xFFFF1B1A)
BASE = {"kind": "indirect", "supports": "identity", "mode": "base",
        "at": "7mfk:000c1dfa", "value": 0x88E}
TEST = {"kind": "test", "supports": "identity",
        "path": "tools/kb/tests/test_indexed_input_word.py",
        "key": "test_indexed_input_word_path"}
OWNED_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
# Reviewed constants, never regenerated from the image under test.
SNAPSHOTS = (
    (0xC1DF8, "6e4cdd85"),
    (0xC1EDE, "67e34700"),
    (0xC1EE4, "d2516020c80889402ee8d5508b056451a005644d"),
    (0xC1EFE, "8551640d957f62d36073d74a325c052d907a655d"),
    (0xC2004, "088c0271"),
    (0xC2010, "ffff128c"),
    (0xC202C, "000086150000921200021ce0"),
    (0xC2222, "ee00"),
    (0xC2244, "bdd264e364e3bef9ee01"),
    (0xC2254, "d51e6050c8088f0564e3d31d430b0009a0030009d31b430b0009bdbd64e3"),
    (0xC22D0, "00008615000c0d90000c1152"),
)


def _binding(symbol, item):
    assert (symbol.layout, symbol.kind, symbol.address) == (KEY.layout, KEY.kind, KEY.address)
    assert {key: item.get(key) for key in BASE} == BASE
    assert "legacy" not in item


def _uint(data, address, size):
    assert 0 <= address <= len(data) - size
    return int.from_bytes(data[address:address + size], "big")


def _insn(data, pc):
    return sh2.decode(_uint(data, pc, 2), pc)


def _math(data, registers, *pcs):
    """Evaluate only named register operations, with no fetch/flow runner."""
    for pc in pcs:
        ins = _insn(data, pc)
        assert ins.value is not None, f"{pc:08x}: missing register operation"
        op, *args = ins.value
        n = ins.dest
        if op == "pool":
            address, size = args
            value = _uint(data, address, size)
            value = sh2.sext(value, 16) if size == 2 else value
        elif op == "const":
            [value] = args
        elif op == "copy":
            value = registers[args[0]]
        elif op == "extu":
            bits, m = args
            value = registers[m] & ((1 << bits) - 1)
        elif op == "shl":
            value = registers[n] << args[0]
        elif op == "add":
            value = registers[n] + registers[args[0]]
        else:
            raise AssertionError(f"{pc:08x}: operation outside the placement slice: {op}")
        registers[n] = value & sh2.MASK


class _Memory:
    def __init__(self, *chunks):
        self.bytes = {address + i: value for address, data in chunks
                      for i, value in enumerate(data)}
        assert len(self.bytes) == sum(len(data) for _, data in chunks)
        self.reads = []

    def read(self, address, size):
        assert all(address + i in self.bytes for i in range(size)), "unmapped read"
        self.reads.append((address, size))
        return int.from_bytes(bytes(self.bytes[address + i] for i in range(size)), "big")


def _load(data, registers, memory, pc, expected):
    ins = _insn(data, pc)
    assert ins.access == expected and ins.access.mode == "load"
    access = ins.access
    address = (registers[access.base] + access.disp
               + (registers[0] if access.indexed else 0)) & sh2.MASK
    value = memory.read(address, access.size)
    registers[ins.dest] = sh2.sext(value, access.size * 8) & sh2.MASK
    return address


def _tst(data, registers, pc):
    word = _insn(data, pc).word
    if word >> 8 == 0xC8:
        return (registers[0] & (word & 0xFF)) == 0
    assert word & 0xF00F == 0x2008
    return (registers[(word >> 8) & 15] & registers[(word >> 4) & 15]) == 0


def _branch(data, pc, t, target, delayed=False):
    ins = _insn(data, pc)
    assert (ins.flow, ins.target, ins.delayed) == ("cbranch", target, delayed)
    form = ins.word >> 8
    assert form in (0x89, 0x8B, 0x8D, 0x8F)
    taken = t if form in (0x89, 0x8D) else not t
    return target if taken else pc + (4 if delayed else 2)


def _slot(data, registers, pc):
    if _insn(data, pc).word != 0x0009:
        _math(data, registers, pc)


def _call(data, registers, pc, target):
    ins = _insn(data, pc)
    assert ins.flow == "call" and ins.delayed
    if ins.target is None:
        assert ins.word & 0xF0FF == 0x400B
        assert registers[(ins.word >> 8) & 15] == target
    else:
        assert ins.target == target
    _slot(data, registers, pc + 2)


def _jump(data, registers, pc, target):
    ins = _insn(data, pc)
    assert (ins.flow, ins.target, ins.delayed) == ("branch", target, True)
    _slot(data, registers, pc + 2)


def _caller(data):
    registers = {}
    _math(data, registers, 0xC2222)
    _call(data, registers, 0xC2244, 0xC1DEC)
    assert registers[4] == 0
    _math(data, registers, 0xC2248)
    assert registers[4] == 0
    _call(data, registers, 0xC224A, 0xC2040)
    assert registers[14] == 1  # The delay slot, not the opaque callee, sets this.
    for flag in (0, 8):
        r = dict(registers)
        memory = _Memory((0x8615, bytes([flag])))
        _math(data, r, 0xC2254)
        assert _load(data, r, memory, 0xC2256, sh2.Access(5, 0, 1, "load")) == 0x8615
        next_pc = _branch(data, 0xC225A, _tst(data, r, 0xC2258), 0xC2268, True)
        _math(data, r, 0xC225C)  # BF/S executes this slot on both outcomes.
        assert r[4] == 1
        if flag == 0:
            assert next_pc == 0xC225E
            _math(data, r, next_pc)
            _call(data, r, 0xC2260, 0xC0D90)
            _jump(data, r, 0xC2264, 0xC226E)
        else:
            assert next_pc == 0xC2268
            _math(data, r, next_pc)
            _call(data, r, 0xC226A, 0xC1152)
        _call(data, r, 0xC226E, 0xC1DEC)
        assert r[4] == 1
        assert memory.reads == [(0x8615, 1)]


def verify_indexed_input_word_path(data, symbol, item):
    """Pure placement verification; mutated ROMs do not pass through SHA checks."""
    _binding(symbol, item)
    for start, text in SNAPSHOTS:
        expected = bytes.fromhex(text)
        assert data[start:start + len(expected)] == expected, f"{start:08x}: stock bytes differ"
    _caller(data)
    for argument in (0, 1, 0x100, 0x101):
        index = argument & 0xFF
        for flag in (0, 8, 0xF7, 0xFF):
            for word in (0, 1, 0x7FFF, 0x8000, 0xFFFF):
                pair = (word, 0x3C7A) if index == 0 else (0x3C7A, word)
                guarded = b"\xa5\x5a" + b"".join(v.to_bytes(2, "big") for v in pair) + b"\xc3\x3c"
                memory = _Memory((0xFFFF1B16, guarded), (0x8615, bytes([flag])),
                                 (0x9212, bytes.fromhex("89abfedc")))
                unchanged = dict(memory.bytes)
                r = {4: argument}
                _math(data, r, 0xC1DF8, 0xC1DFA, 0xC1EDE, 0xC1EE0, 0xC1EE4)
                assert r[14] == index and r[7] == 2 * index
                assert r[13] + item["value"] == symbol.address
                assert _load(data, r, memory, 0xC1EE6, sh2.Access(2, 0, 1, "load")) == 0x8615
                guard_pc = _branch(data, 0xC1EEA, _tst(data, r, 0xC1EE8), 0xC1F6E)
                if flag & 8 == 0:
                    assert guard_pc == 0xC1F6E
                    assert memory.reads == [(0x8615, 1)]  # No input-word read on this arm.
                else:
                    assert guard_pc == 0xC1EEC
                    t = _tst(data, r, guard_pc)
                    _math(data, r, 0xC1EEE)
                    index_pc = _branch(data, 0xC1EF0, t, 0xC1EFE)
                    if index == 0:
                        assert index_pc == 0xC1EF2
                        coefficient = _load(data, r, memory, index_pc, sh2.Access(5, 0, 2, "load"))
                        _jump(data, r, 0xC1EF4, 0xC1F02)  # EXTU.W in the BRA delay slot.
                        assert coefficient == 0x9212 and r[4] == 0x89AB
                    else:
                        assert index_pc == 0xC1EFE
                        coefficient = _load(data, r, memory, index_pc, sh2.Access(5, 2, 2, "load"))
                        _math(data, r, 0xC1F00)
                        assert coefficient == 0x9214 and r[4] == 0xFEDC
                    _math(data, r, 0xC1F02, 0xC1F04, 0xC1F06, 0xC1F08, 0xC1F0A)
                    assert r[0] == 2 * index and r[7] == 0x21CE0
                    address = _load(data, r, memory, 0xC1F0C, sh2.Access(2, 0, 2, "load", True))
                    assert address == (symbol.address - 2 if index == 0 else symbol.address)
                    assert sh2.sext(r[5], 32) == (word if word < 0x8000 else word - 0x10000)
                    _math(data, r, 0xC1F0E, 0xC1F10)
                    assert r[5] == word  # The stock EXTU.W removes MOV.W sign extension.
                    assert memory.reads == [(0x8615, 1), (coefficient, 2), (address, 2)]
                assert memory.bytes == unchanged
                assert bytes(memory.bytes[0xFFFF1B16 + i] for i in range(8)) == guarded


@pytest.fixture(scope="module")
def compiled_binding():
    model = compile.cached(repo.ROOT)
    symbol = model.symbols[KEY]
    assert not symbol.implicit and "defs/JK08A.vars.csv" in symbol.sources
    assert symbol.meaning.props["unit"] == "raw"
    assert symbol.meaning.props["level"] == "code"
    explicit = [item for item in symbol.evidence if "legacy" not in item]
    assert explicit == [BASE, TEST]
    [item, test] = explicit
    _binding(symbol, item)
    assert match.verify(model, symbol, item) is None
    assert match.verify(model, symbol, test) is None
    return model, symbol, item


@pytest.fixture(scope="module")
def stock_images(compiled_binding):
    model, _, _ = compiled_binding
    images = dict(match.images(model, "7mfk"))
    assert set(images) == {"JK00A", "JK03A", "JK03B", "JK08A"}
    assert images["JK08A"] == derive.image_bytes(repo.layout("7mfk"))
    assert hashlib.sha256(images["JK08A"]).hexdigest() == OWNED_SHA256
    return images


@pytest.mark.parametrize("rom", ("JK00A", "JK03A", "JK03B", "JK08A"))
def test_indexed_input_word_path(stock_images, compiled_binding, rom):
    _, symbol, item = compiled_binding
    verify_indexed_input_word_path(stock_images[rom], symbol, item)


@pytest.mark.parametrize("pc, replacement", (
    (0xC2010, "ffff128e"), (0xC2004, "088e"), (0xC1DFA, "dd84"),
    (0xC1DF8, "6e4d"), (0xC1EDE, "67c3"), (0xC1EE0, "4708"),
    (0xC1F06, "60e3"), (0xC1F08, "d74b"), (0xC1F0C, "052c"),
    (0xC1F0C, "052e"), (0xC1F0C, "053d"), (0xC1F10, "655c"),
    (0xC202C, "00008614"), (0xC2030, "00009214"), (0xC1EE8, "c804"),
    (0xC1EEA, "8b40"), (0xC1EEA, "8941"), (0xC1EEA, "8d40"),
    (0xC1EEC, "2e08"), (0xC1EF0, "8905"), (0xC1EF4, "a004"),
    (0xC1EF6, "644c"), (0xC1EFE, "8550"), (0xC1F00, "640c"),
    (0xC2244, "bdd3"), (0xC224C, "ee00"), (0xC225A, "8b05"),
    (0xC225C, "6443"), (0xC2264, "a004"), (0xC226E, "bdbc"),
    (0xC2270, "64c3"), (0xC22D4, "000c0d92"), (0xC22D8, "000c1150"),
))
def test_indexed_input_word_rejects_stock_path_mutations(stock_images, compiled_binding, pc, replacement):
    _, symbol, item = compiled_binding
    for data in stock_images.values():
        changed = bytearray(data)
        raw = bytes.fromhex(replacement)
        assert changed[pc:pc + len(raw)] != raw
        changed[pc:pc + len(raw)] = raw
        with pytest.raises(AssertionError):
            verify_indexed_input_word_path(changed, symbol, item)


@pytest.mark.parametrize("field, value", (("value", 0x88C), ("at", "7mfk:000c1df8"),
                                          ("mode", "indexed"), ("supports", "unit")))
def test_indexed_input_word_rejects_wrong_bindings(stock_images, compiled_binding, field, value):
    _, symbol, item = compiled_binding
    with pytest.raises(AssertionError):
        verify_indexed_input_word_path(stock_images["JK08A"], symbol, {**item, field: value})
    with pytest.raises(AssertionError):
        verify_indexed_input_word_path(stock_images["JK08A"], replace(symbol.key, address=KEY.address - 2), item)
