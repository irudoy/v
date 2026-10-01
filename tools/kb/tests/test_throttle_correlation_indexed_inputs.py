"""A773A's bounded input placement paths, not a sensor or monitor proof."""

from itertools import product

import pytest

from kb import checks, compile, levels, match, repo, sh2, sites
from kb.model import SymbolKey


ADDRESS = 0xFFFF274F
IMAGES = ("JK00A", "JK03A", "JK03B", "JK08A")
PATH = "tools/kb/tests/test_throttle_correlation_indexed_inputs.py"
BYTE_KEY = "test_throttle_correlation_input_byte_placement"
# Fixed reviewed SH-2E words, reconstructed from the instruction listing.
# The sensor differences before a77a0, all helper bodies and returns, and the
# monitor acceptance predicates after a77d0 are outside the byte fixture.
BYTE_SPANS = (
    (0xA7744, "d03c401e"), (0xA7750, "6d4c"),
    (0xA77A0, "dc1f60c0c98020088f026203a0880009"),
    (0xA77B0, "e2d560d3662c0212326c052c762a655c4500655d35678b00e5ffd41cd21c420b655c"),
    (0xA7820, "ffff4184"),
    (0xA7838, "ffff267a00023ddc00026370"),
    (0xA7938, "beffe400e401aefc4f26"),
)


def _evidence(site, key):
    return [
        {"kind": "rom-bytes", "supports": "identity", "at": "7mfk:000a7838",
         "value": "ffff267a", "legacy": "rom_const:000a7838=ffff267a"},
        {"kind": "l0", "supports": "identity", "at": f"7mfk:{site:08x}",
         "legacy": f"site:{site:08x}"},
        {"kind": "test", "supports": "identity", "path": PATH, "key": key},
    ]


def _insn(data, pc):
    raw = data[pc:pc + 2]
    assert len(raw) == 2
    return sh2.decode(int.from_bytes(raw, "big"), pc)


def _values(data, r, *pcs):
    """Only named register/address operations; no general instruction runner."""
    for pc in pcs:
        ins = _insn(data, pc)
        if ins.gbr is not None:
            assert ins.gbr[0] == "copy"
            r["gbr"] = r[ins.gbr[1]]
            continue
        assert ins.value is not None and ins.access is None
        op, *args = ins.value
        if op == "pool":
            pool, size = args
            raw = data[pool:pool + size]
            assert len(raw) == size
            value = int.from_bytes(raw, "big")
            if size == 2:
                value = sh2.sext(value, 16)
        elif op == "copy":
            value = r[args[0]]
        elif op == "addi":
            value = r[ins.dest] + args[0]
        elif op == "add":
            value = r[ins.dest] + r[args[0]]
        elif op == "sub":
            value = r[ins.dest] - r[args[0]]
        elif op == "gbr":
            value = r["gbr"]
        elif op == "extu":
            bits, source = args
            value = r[source] & ((1 << bits) - 1)
        elif op == "shl":
            [bits] = args
            value = r[ins.dest] << bits
        elif op == "const":
            [value] = args
        else:
            raise AssertionError(f"unexpected placement operation {op}")
        r[ins.dest] = value & sh2.MASK


def _branch(data, pc, t, target, delayed=False):
    ins = _insn(data, pc)
    assert (ins.target, ins.delayed) == (target, delayed)
    assert ins.flow in ("branch", "cbranch")
    if ins.flow == "branch":
        return target
    opcode = ins.word >> 8
    assert opcode in (0x89, 0x8B, 0x8D, 0x8F)
    taken = t if opcode in (0x89, 0x8D) else not t
    return target if taken else pc + (4 if delayed else 2)


class _Memory:
    def __init__(self):
        self.cells, self.reads = {}, []

    def put(self, address, raw):
        for offset, value in enumerate(raw):
            assert address + offset not in self.cells
            self.cells[address + offset] = value

    def guarded(self, address, raw):
        self.put(address - 4, b"\xa5" * 4 + raw + b"\xa5" * 4)

    def read(self, address, size):
        assert all(address + i in self.cells for i in range(size))
        self.reads.append((address, size))
        return int.from_bytes(bytes(self.cells[address + i] for i in range(size)), "big")


def _read(data, pc, r, memory, size):
    ins = _insn(data, pc)
    access = ins.access
    assert access is not None and (access.mode, access.size) == ("load", size)
    address = (r[access.base] + access.disp + (r[0] if access.indexed else 0)) & sh2.MASK
    r[ins.dest] = sh2.sext(memory.read(address, size), size * 8) & sh2.MASK
    return address


def _spans(data, spans):
    for pc, expected in spans:
        raw = bytes.fromhex(expected)
        assert data[pc:pc + len(raw)] == raw, f"stock slice at {pc:08x} differs"


def _caller_indices(data):
    """Only the two calls to a773a; earlier range-monitor calls are opaque."""
    r = {4: 0xA5, 15: 0xFFFF6000}
    call = _insn(data, 0xA7938)
    assert (call.flow, call.target, call.delayed) == ("call", 0xA773A, True)
    r["pr"] = 0xA793C
    _values(data, r, 0xA793A)  # BSR delay slot supplies the first index
    assert r[4] == 0
    first = r[4]
    # The first monitor call and return are opaque, with this return address.
    assert r["pr"] == 0xA793C
    _values(data, r, 0xA793C)
    assert _branch(data, 0xA793E, False, 0xA773A, True) == 0xA773A
    slot = _insn(data, 0xA7940)
    assert slot.word == 0x4F26  # LDS.L @R15+,PR in the tail BRA delay slot
    assert (slot.dest, slot.value) == (15, ("addi", 4))
    assert (slot.access.base, slot.access.disp, slot.access.size, slot.access.mode) == (15, 0, 4, "load")
    memory = _Memory()
    memory.put(r[15], bytes.fromhex("00012346"))
    r["pr"] = memory.read(r[15], 4)
    r[15] = (r[15] + 4) & sh2.MASK
    assert (r[4], r["pr"], r[15]) == (1, 0x12346, 0xFFFF6004)
    return first, r[4]


def _byte_scenario(data, symbol, index, flags, value):
    r = {4: index}
    _values(data, r, 0xA7744, 0xA7746, 0xA7750)
    normalized = index & 0xFF
    assert (r["gbr"], r[13]) == (0xFFFF267A, normalized)
    memory = _Memory()
    memory.put(0xFFFF4184, bytes([flags]))
    inputs = [value ^ 0x5A, value ^ 0x5A]
    inputs[normalized] = value
    memory.guarded(symbol.address, bytes(inputs))
    before = dict(memory.cells)
    _values(data, r, 0xA77A0)
    assert _read(data, 0xA77A2, r, memory, 1) == 0xFFFF4184
    assert _insn(data, 0xA77A4).word == 0xC980  # AND #0x80,R0
    r[0] &= 0x80
    assert _insn(data, 0xA77A6).word == 0x2008  # TST R0,R0
    next_pc = _branch(data, 0xA77A8, r[0] == 0, 0xA77B0, True)
    r[2] = 0xA5A5A5A5
    _values(data, r, 0xA77AA)  # BF/S delay slot executes on both outcomes
    assert r[2] == flags & 0x80
    if next_pc == 0xA77AC:
        assert _branch(data, next_pc, False, 0xA78C0, True) == 0xA78C0
        assert _insn(data, 0xA77AE).word == 0x0009  # BRA delay slot
        assert memory.reads == [(0xFFFF4184, 1)]
        assert memory.cells == before
        return None
    assert next_pc == 0xA77B0
    _values(data, r, 0xA77B0, 0xA77B2, 0xA77B4, 0xA77B6, 0xA77B8)
    assert (r[2], r[0], r[6]) == (0xFFFF267A + 0xD5, normalized, 0xD5)
    assert _read(data, 0xA77BA, r, memory, 1) == symbol.address + normalized
    assert r[5] == sh2.sext(value, 8) & sh2.MASK
    _values(data, r, 0xA77BC, 0xA77BE, 0xA77C0, 0xA77C2)
    assert (r[6], r[5]) == (0xFF, 2 * value)
    assert _insn(data, 0xA77C4).word == 0x3567  # signed CMP/GT R6,R5
    next_pc = _branch(data, 0xA77C6, sh2.sext(r[5], 32) > sh2.sext(r[6], 32), 0xA77CA)
    if next_pc == 0xA77C8:
        _values(data, r, next_pc)
        assert r[5] == sh2.MASK
    else:
        assert next_pc == 0xA77CA and r[5] == 2 * value
    _values(data, r, 0xA77CA, 0xA77CC)
    call = _insn(data, 0xA77CE)
    assert call.word == 0x420B and (call.flow, call.delayed) == ("call", True)
    assert (r[4], r[2]) == (0x23DDC, 0x26370)
    _values(data, r, 0xA77D0)  # JSR delay slot truncates the sentinel to 255
    assert r[5] == min(255, 2 * value)
    assert memory.reads == [(0xFFFF4184, 1), (symbol.address + normalized, 1)]
    assert memory.cells == before  # both inputs and all surrounding guard bytes
    # Stop at helper entry. No helper return or physical-scale claim is modeled.
    return r[5]


def verify_input_byte(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", ADDRESS)
    _spans(data, BYTE_SPANS)
    assert _caller_indices(data) == (0, 1)
    boundaries = {0: 0, 1: 2, 127: 254, 128: 255, 255: 255}
    for index, flags, value in product((0, 1, 0x100, 0x101), (0, 0x40, 0x7F, 0x80, 0xC0, 0xFF), boundaries):
        argument = _byte_scenario(data, symbol, index, flags, value)
        assert argument == (boundaries[value] if flags & 0x80 else None)


@pytest.fixture(scope="module")
def compiled_placements():
    model = compile.cached(repo.ROOT)
    images = dict(match.images(model, "7mfk"))
    assert set(images) == set(IMAGES)
    return model, images


def _compiled_symbol(model, address, site, key):
    symbol = model.symbols[SymbolKey("7mfk", "ram", address)]
    assert "defs/JK08A.vars.csv" in symbol.sources
    assert symbol.value("unit") == "raw" and symbol.value("level") == "code"
    assert symbol.evidence == _evidence(site, key) and not checks._owned(model, symbol)
    assert levels.held(model, symbol)
    references = sites.references("7mfk", model.root)
    assert 0xFFFF267A in references[0xA7744]
    assert address in references[site]
    for item in symbol.evidence:
        assert match.verify(model, symbol, item) is None
    assert any(link.type == "reader" and link.owner is symbol.meaning
               and link.to.symbols["7mfk"].address == 0xA773A
               for link in symbol.meaning.links)
    assert not any(link.type == "writer" and link.owner is symbol.meaning
                   for link in symbol.meaning.links)
    return symbol


# A775A precedes the bit-7 guard and all difference branches.
WORD_2752_SPANS = (
    (0xA7744, "d03c401e"),
    (0xA774A, "e2d8662c02126d4c67d34700326c6073052d"),
    (0xA7838, "ffff267a"), (0xA7938, "beffe400e401aefc4f26"),
)
WORD_2752_KEY = "test_throttle_correlation_2752_word_placement"


def _word_memory(address, index, value):
    memory = _Memory()
    values = [value ^ 0x5A5A, value ^ 0x5A5A]
    values[index] = value
    memory.guarded(address, b"".join(v.to_bytes(2, "big") for v in values))
    return memory


def _first_word(data, r, memory):
    _values(data, r, 0xA7744, 0xA7746, 0xA774A, 0xA774C, 0xA774E,
            0xA7750, 0xA7752, 0xA7754, 0xA7756, 0xA7758)
    assert (r["gbr"], r[13], r[7], r[0], r[2], r[6]) == (
        0xFFFF267A, r[4] & 0xFF, 2 * (r[4] & 0xFF),
        2 * (r[4] & 0xFF), 0xFFFF2752, 0xD8,
    )
    return _read(data, 0xA775A, r, memory, 2)


def verify_2752_word(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", 0xFFFF2752)
    _spans(data, WORD_2752_SPANS)
    assert _caller_indices(data) == (0, 1)
    for index, value in product((0, 1, 0x100, 0x101), (0, 1, 0x7FFF, 0x8000, 0xFFFF)):
        r = {4: index}
        normalized = index & 0xFF
        memory = _word_memory(symbol.address, normalized, value)
        before = dict(memory.cells)
        assert _first_word(data, r, memory) == symbol.address + 2 * normalized
        assert r[5] == sh2.sext(value, 16) & sh2.MASK
        assert memory.reads == [(symbol.address + 2 * normalized, 2)]
        assert memory.cells == before  # both words and the four-byte guards


# A7762 reuses the doubled index and advances the D8 offset by eight bytes.
WORD_275A_SPANS = WORD_2752_SPANS + ((0xA775C, "76080212326c062d"),)
WORD_275A_KEY = "test_throttle_correlation_275a_word_placement"


def verify_275a_word(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", 0xFFFF275A)
    _spans(data, WORD_275A_SPANS)
    assert _caller_indices(data) == (0, 1)
    for index, value in product((0, 1, 0x100, 0x101), (0, 1, 0x7FFF, 0x8000, 0xFFFF)):
        r = {4: index}
        normalized = index & 0xFF
        memory = _word_memory(symbol.address, normalized, value)
        memory.put(0xFFFF2752, bytes.fromhex("1357fdb9"))
        before = dict(memory.cells)
        assert _first_word(data, r, memory) == 0xFFFF2752 + 2 * normalized
        first = (0x1357, 0xFDB9)[normalized]
        assert r[5] == sh2.sext(first, 16) & sh2.MASK
        _values(data, r, 0xA775C, 0xA775E, 0xA7760)
        assert (r[2], r[0], r[6]) == (0xFFFF267A + 0xE0, 2 * normalized, 0xE0)
        assert _read(data, 0xA7762, r, memory, 2) == symbol.address + 2 * normalized
        assert r[6] == sh2.sext(value, 16) & sh2.MASK
        assert memory.reads == [(0xFFFF2752 + 2 * normalized, 2),
                                (symbol.address + 2 * normalized, 2)]
        assert memory.cells == before


# Both arms of the preceding signed difference reach a7772 with the doubled
# index intact; a7786 reads the word before the bit-7 guard at a77a8.
WORD_274A_SPANS = WORD_275A_SPANS + (
    (0xA7764, "35638b023568a0026e5336586e63e2cc6073652c0212325c062d75040212325c6073052d666d655d"),
)
WORD_274A_KEY = "test_throttle_correlation_274a_word_placement"


def verify_274a_word(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", 0xFFFF274A)
    _spans(data, WORD_274A_SPANS)
    assert _caller_indices(data) == (0, 1)
    pairs = ((0, 1), (1, 0), (0xFFFF, 0), (0x7FFF, 0x8000),
             (0x8000, 0x7FFF), (0x8000, 0x8000))
    for index, value, pair in product((0, 1, 0x100, 0x101), (0, 1, 0x7FFF, 0x8000, 0xFFFF), pairs):
        r = {4: index}
        normalized = index & 0xFF
        memory = _word_memory(symbol.address, normalized, value)
        first, second = pair
        for address, source in ((0xFFFF2752, first), (0xFFFF275A, second)):
            values = [source ^ 0x5A5A, source ^ 0x5A5A]
            values[normalized] = source
            memory.put(address, b"".join(v.to_bytes(2, "big") for v in values))
        before = dict(memory.cells)
        assert _first_word(data, r, memory) == 0xFFFF2752 + 2 * normalized
        _values(data, r, 0xA775C, 0xA775E, 0xA7760)
        assert _read(data, 0xA7762, r, memory, 2) == 0xFFFF275A + 2 * normalized
        assert (r[5], r[6]) == (sh2.sext(first, 16) & sh2.MASK,
                               sh2.sext(second, 16) & sh2.MASK)
        assert _insn(data, 0xA7764).word == 0x3563  # signed CMP/GE R6,R5
        next_pc = _branch(data, 0xA7766, sh2.sext(r[5], 32) >= sh2.sext(r[6], 32), 0xA776E)
        if next_pc == 0xA7768:
            _values(data, r, 0xA7768)
            assert _branch(data, 0xA776A, False, 0xA7772, True) == 0xA7772
            _values(data, r, 0xA776C)  # BRA delay slot, greater/equal arm
        else:
            assert next_pc == 0xA776E
            _values(data, r, 0xA776E, 0xA7770)
        assert r[14] == abs(sh2.sext(first, 16) - sh2.sext(second, 16))
        assert r[7] == 2 * normalized
        _values(data, r, 0xA7772, 0xA7774, 0xA7776, 0xA7778, 0xA777A)
        assert (r[2], r[0], r[5]) == (0xFFFF2746, 2 * normalized, 0xCC)
        assert _read(data, 0xA777C, r, memory, 2) == 0xFFFF2746 + 2 * normalized
        assert r[6] == sh2.sext(0xA5A5, 16) & sh2.MASK
        _values(data, r, 0xA777E, 0xA7780, 0xA7782, 0xA7784)
        assert (r[2], r[0], r[5]) == (0xFFFF267A + 0xD0, 2 * normalized, 0xD0)
        assert _read(data, 0xA7786, r, memory, 2) == symbol.address + 2 * normalized
        assert r[5] == sh2.sext(value, 16) & sh2.MASK
        _values(data, r, 0xA7788, 0xA778A)
        assert (r[6], r[5]) == (0xA5A5, value)
        assert memory.reads == [(0xFFFF2752 + 2 * normalized, 2),
                                (0xFFFF275A + 2 * normalized, 2),
                                (0xFFFF2746 + 2 * normalized, 2),
                                (symbol.address + 2 * normalized, 2)]
        assert memory.cells == before


def _mutations(data, symbol, verifier, mutations):
    for pc, raw in mutations:
        changed = bytearray(data)
        replacement = bytes.fromhex(raw)
        changed[pc:pc + len(replacement)] = replacement
        assert changed != data
        with pytest.raises(AssertionError):
            verifier(bytes(changed), symbol)
    with pytest.raises(AssertionError):
        verifier(data, SymbolKey("7mfk", "ram", symbol.address + 1))


@pytest.mark.parametrize("rom", IMAGES)
def test_throttle_correlation_input_byte_placement(compiled_placements, rom):
    model, images = compiled_placements
    symbol = _compiled_symbol(model, ADDRESS, 0xA77BA, BYTE_KEY)
    data = images[rom]
    verify_input_byte(data, symbol)
    _mutations(data, symbol, verify_input_byte, (
        (0xA7838, "ffff267b"), (0xA7744, "d03b"), (0xA7746, "401f"),
        (0xA7750, "6d4d"), (0xA77B0, "e2d6"), (0xA77B2, "60c3"),
        (0xA77B4, "662d"), (0xA77B6, "0312"), (0xA77B8, "325c"),
        (0xA77BA, "052d"), (0xA77BA, "062c"), (0xA77A4, "c940"),
        (0xA77A8, "8d02"), (0xA77A8, "8f03"), (0xA77AA, "6303"),
        (0xA77AC, "a087"), (0xA77AE, "e200"), (0xA77BC, "7629"),
        (0xA77BE, "655d"), (0xA77C0, "4508"), (0xA77C2, "655c"),
        (0xA77C4, "3563"), (0xA77C6, "8900"), (0xA77C8, "e5fe"),
        (0xA783C, "00023ddd"), (0xA7840, "00026372"),
        (0xA77CE, "430b"), (0xA77D0, "655d"),
        (0xA7938, "befe"), (0xA793A, "e401"), (0xA793C, "e400"),
        (0xA793E, "aefd"), (0xA7940, "4f22"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_throttle_correlation_2752_word_placement(compiled_placements, rom):
    model, images = compiled_placements
    symbol = _compiled_symbol(model, 0xFFFF2752, 0xA775A, WORD_2752_KEY)
    data = images[rom]
    verify_2752_word(data, symbol)
    _mutations(data, symbol, verify_2752_word, (
        (0xA7838, "ffff267b"), (0xA7744, "d03b"), (0xA7746, "401f"),
        (0xA774A, "e2d9"), (0xA774C, "662d"), (0xA774E, "0312"),
        (0xA7750, "6d4d"), (0xA7752, "67c3"), (0xA7754, "4708"),
        (0xA7756, "325c"), (0xA7758, "60d3"), (0xA775A, "052c"),
        (0xA775A, "052e"), (0xA775A, "062d"),
        (0xA7938, "befe"), (0xA793A, "e401"), (0xA793C, "e400"),
        (0xA793E, "aefd"), (0xA7940, "4f22"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_throttle_correlation_275a_word_placement(compiled_placements, rom):
    model, images = compiled_placements
    symbol = _compiled_symbol(model, 0xFFFF275A, 0xA7762, WORD_275A_KEY)
    data = images[rom]
    verify_275a_word(data, symbol)
    _mutations(data, symbol, verify_275a_word, (
        (0xA7838, "ffff267b"), (0xA7744, "d03b"), (0xA7746, "401f"),
        (0xA774A, "e2d9"), (0xA774C, "662d"), (0xA774E, "0312"),
        (0xA7750, "6d4d"), (0xA7752, "67c3"), (0xA7754, "4708"),
        (0xA7756, "325c"), (0xA7758, "60d3"), (0xA775A, "052c"),
        (0xA775C, "7609"), (0xA775E, "0312"), (0xA7760, "325c"),
        (0xA7762, "062c"), (0xA7762, "062e"), (0xA7762, "052d"),
        (0xA7938, "befe"), (0xA793A, "e401"), (0xA793C, "e400"),
        (0xA793E, "aefd"), (0xA7940, "4f22"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_throttle_correlation_274a_word_placement(compiled_placements, rom):
    model, images = compiled_placements
    symbol = _compiled_symbol(model, 0xFFFF274A, 0xA7786, WORD_274A_KEY)
    data = images[rom]
    verify_274a_word(data, symbol)
    _mutations(data, symbol, verify_274a_word, (
        (0xA7838, "ffff267b"), (0xA7744, "d03b"), (0xA7746, "401f"),
        (0xA774A, "e2d9"), (0xA7750, "6d4d"), (0xA7754, "4708"),
        (0xA7758, "60d3"), (0xA775A, "052c"), (0xA775C, "7609"),
        (0xA7762, "062c"), (0xA7764, "3562"), (0xA7766, "8902"),
        (0xA7766, "8b03"), (0xA7768, "356c"), (0xA776A, "a003"),
        (0xA776C, "6e63"), (0xA776E, "365c"), (0xA7770, "6e53"),
        (0xA7772, "e2cd"), (0xA7774, "60d3"), (0xA7776, "652d"),
        (0xA7778, "0312"), (0xA777A, "326c"), (0xA777C, "062c"),
        (0xA777E, "7505"), (0xA7780, "0312"), (0xA7782, "326c"),
        (0xA7784, "60d3"), (0xA7786, "052c"), (0xA7786, "052e"),
        (0xA7786, "062d"), (0xA7788, "666c"), (0xA778A, "655c"),
        (0xA7938, "befe"), (0xA793A, "e401"), (0xA793C, "e400"),
        (0xA793E, "aefd"), (0xA7940, "4f22"),
    ))
