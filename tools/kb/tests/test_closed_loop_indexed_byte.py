"""88bba's guarded indexed lookup-result placement, not a monitor proof."""

from itertools import product

import pytest

from kb import checks, compile, levels, match, repo, sh2, sites
from kb.model import SymbolKey


ADDRESS = 0xFFFF157F
IMAGES = ("JK00A", "JK03A", "JK03B", "JK08A")
PATH = "tools/kb/tests/test_closed_loop_indexed_byte.py"
KEY = "test_closed_loop_indexed_byte_placement"
# Fixed reviewed SH-2E words, independently reconstructed from the listing.
# The unrelated latch update before 88bf0, the lookup calculation, and the
# monitor acceptance predicates after 88c4a remain outside this fixture.
SPANS = (
    (0x88B56, "b030e400"), (0x88B80, "b01be401"),
    (0x88BC4, "d04e401e"), (0x88BCC, "6c437c016d43"),
    (0x88BF0, "d6446060c8408b12d6436260662c26c8890dd24260d3724d062c26688b0dd2407208062c26688b18a017ee01"),
    (0x88C1E, "d53d60d3d23a6650724d0264c406d43ad53bd23b420b660cd23b6603955160d3325c026460d3d23272080264"),
    (0x88CE0, "02f3"),
    (0x88D00, "ffff1068ffff4184ffff267affff4258ffff24d40000861a0001231200012f9e000264a0ffff128c"),
    (0x861A, "ff"),
)
EVIDENCE = [
    {"kind": "rom-bytes", "supports": "identity", "at": "7mfk:00088d24",
     "value": "ffff128c", "legacy": "rom_const:00088d24=ffff128c"},
    {"kind": "rom-bytes", "supports": "identity", "at": "7mfk:00088ce0",
     "value": "02f3", "legacy": "rom_const:00088ce0=02f3"},
    {"kind": "l0", "supports": "identity", "at": "7mfk:00088c40",
     "legacy": "site:00088c40"},
    {"kind": "test", "supports": "identity", "path": PATH, "key": KEY},
]


def _insn(data, pc):
    raw = data[pc:pc + 2]
    assert len(raw) == 2
    return sh2.decode(int.from_bytes(raw, "big"), pc)


def _values(data, r, *pcs):
    """Only named address/argument operations; no general control-flow runner."""
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
            value = int.from_bytes(data[pool:pool + size], "big")
            assert len(data[pool:pool + size]) == size
            if size == 2:
                value = sh2.sext(value, 16)
        elif op == "copy":
            value = r[args[0]]
        elif op == "addi":
            value = r[ins.dest] + args[0]
        elif op == "add":
            value = r[ins.dest] + r[args[0]]
        elif op == "extu":
            bits, source = args
            value = r[source] & ((1 << bits) - 1)
        elif op == "const":
            [value] = args
        else:
            raise AssertionError(f"unexpected placement operation {op}")
        r[ins.dest] = value & sh2.MASK


def _branch(data, pc, t, target, delayed=False):
    ins = _insn(data, pc)
    assert (ins.target, ins.delayed) == (target, delayed)
    assert ins.flow in ("branch", "cbranch")
    taken = ins.flow == "branch" or (t if ins.word >> 8 == 0x89 else not t)
    return target if taken else pc + (4 if delayed else 2)


class _Memory:
    def __init__(self):
        self.cells, self.writable, self.writes = {}, set(), []

    def byte(self, address, value):
        assert address not in self.cells
        self.cells[address] = value

    def guarded(self, address, values):
        for i, value in enumerate(b"\xa5" * 4 + bytes(values) + b"\xa5" * 4):
            self.byte(address - 4 + i, value)
            self.writable.add(address - 4 + i)

    def guard(self, address):
        assert bytes(self.cells[address - 4 + i] for i in range(4)) == b"\xa5" * 4
        assert bytes(self.cells[address + 2 + i] for i in range(4)) == b"\xa5" * 4


def _access(data, pc, r, m, mode):
    ins = _insn(data, pc)
    access = ins.access
    assert access is not None and (access.mode, access.size) == (mode, 1)
    address = (r[access.base] + access.disp + (r[0] if access.indexed else 0)) & sh2.MASK
    assert address in m.cells
    if mode == "load":
        r[ins.dest] = sh2.sext(m.cells[address], 8) & sh2.MASK
    else:
        assert address in m.writable
        source = (ins.word >> 4) & 15
        m.cells[address] = r[source] & 0xFF
        m.writes.append((address, 1))
    return address


def _scenario(data, symbol, index, start, enabled, counter, countdown, returned):
    r = {4: index}
    _values(data, r, 0x88BC4, 0x88BC6, 0x88BCC, 0x88BCE, 0x88BD0)
    assert (r["gbr"], r[12], r[13]) == (0xFFFF1068, index + 1, index)
    m = _Memory()
    m.byte(0xFFFF4184, start)
    m.byte(0xFFFF267A, index + 1 if enabled else 0)
    m.byte(0xFFFF106E, 0x80)
    m.byte(0x861A, data[0x861A])
    for address in (symbol.address, 0xFFFF42A5, 0xFFFF24DC):
        m.guarded(address, (0x69, 0x69))
    m.cells[0xFFFF42A5 + index] = counter
    m.cells[0xFFFF24DC + index] = countdown
    _values(data, r, 0x88BF0)
    assert _access(data, 0x88BF2, r, m, "load") == 0xFFFF4184
    assert _insn(data, 0x88BF4).word == 0xC840
    initialize = _branch(data, 0x88BF6, r[0] & 0x40 == 0, 0x88C1E) == 0x88C1E
    if not initialize:
        _values(data, r, 0x88BF8)
        assert _access(data, 0x88BFA, r, m, "load") == 0xFFFF267A
        _values(data, r, 0x88BFC)
        assert _insn(data, 0x88BFE).word == 0x26C8
        initialize = _branch(data, 0x88C00, r[12] & r[6] == 0, 0x88C1E) == 0x88C1E
    reload = initialize
    if initialize:
        _values(data, r, 0x88C1E, 0x88C20, 0x88C22)
        assert _access(data, 0x88C24, r, m, "load") == 0x861A
        _values(data, r, 0x88C26)
        assert _access(data, 0x88C28, r, m, "store") == 0xFFFF42A5 + index
    else:
        _values(data, r, 0x88C02, 0x88C04, 0x88C06)
        assert _access(data, 0x88C08, r, m, "load") == 0xFFFF42A5 + index
        assert _insn(data, 0x88C0A).word == 0x2668
        reload = _branch(data, 0x88C0C, r[6] == 0, 0x88C2A) == 0x88C2A
        if not reload:
            _values(data, r, 0x88C0E, 0x88C10)
            assert _access(data, 0x88C12, r, m, "load") == 0xFFFF24DC + index
            assert _insn(data, 0x88C14).word == 0x2668
            next_pc = _branch(data, 0x88C16, r[6] == 0, 0x88C4A)
            if next_pc != 0x88C4A:
                assert _branch(data, 0x88C18, False, 0x88C4A, True) == 0x88C4A
                _values(data, r, 0x88C1A)  # BRA delay slot, elapsed arm
                assert r[14] == 1
    if reload:
        assert _access(data, 0x88C2A, r, m, "load") == 0xFFFF106E
        _values(data, r, 0x88C2C, 0x88C2E, 0x88C30)
        call = _insn(data, 0x88C32)
        assert (call.flow, call.delayed, r[2]) == ("call", True, 0x264A0)
        _values(data, r, 0x88C34)  # argument in the JSR delay slot
        assert (r[4], r[5], r[6]) == (0x12312, 0x12F9E, 0x80)
        # An opaque lookup result, not interpolation or physical semantics.
        r = {"gbr": r["gbr"], 13: r[13], 0: returned}
        _values(data, r, 0x88C36, 0x88C38, 0x88C3A, 0x88C3C, 0x88C3E)
        assert (r[2], r[5], r[0]) == (0xFFFF128C + 0x2F3, 0x2F3, index)
        assert _access(data, 0x88C40, r, m, "store") == symbol.address + index
        _values(data, r, 0x88C42, 0x88C44, 0x88C46)
        assert _access(data, 0x88C48, r, m, "store") == 0xFFFF24DC + index
    expected = ([(0xFFFF42A5 + index, 1)] if initialize else [])
    expected += ([(symbol.address + index, 1), (0xFFFF24DC + index, 1)] if reload else [])
    assert m.writes == expected
    assert m.cells[symbol.address + index] == (returned if reload else 0x69)
    assert m.cells[0xFFFF24DC + index] == (returned if reload else countdown)
    for address in (symbol.address, 0xFFFF42A5, 0xFFFF24DC):
        m.guard(address)
        assert m.cells[address + (1 - index)] == 0x69


def verify_closed_loop_byte(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", ADDRESS)
    for pc, expected in SPANS:
        raw = bytes.fromhex(expected)
        assert data[pc:pc + len(raw)] == raw, f"stock slice at {pc:08x} differs"
    for call, slot, index in ((0x88B56, 0x88B58, 0), (0x88B80, 0x88B82, 1)):
        ins = _insn(data, call)
        assert (ins.flow, ins.target, ins.delayed) == ("call", 0x88BBA, True)
        assert (_insn(data, slot).dest, _insn(data, slot).value) == (4, ("const", index))
    for args in product((0, 1), (0, 0x40), (False, True), (0, 1), (0, 1), (0, 0x7F, 0x80, 0xFF)):
        _scenario(data, symbol, *args)


@pytest.fixture(scope="module")
def compiled_placement():
    model = compile.cached(repo.ROOT)
    symbol = model.symbols[SymbolKey("7mfk", "ram", ADDRESS)]
    assert "defs/JK08A.vars.csv" in symbol.sources
    assert symbol.value("unit") == "raw" and symbol.value("level") == "code"
    assert symbol.evidence == EVIDENCE and not checks._owned(model, symbol)
    assert levels.held(model, symbol)
    references = sites.references("7mfk", model.root)
    assert 0xFFFF128C in references[0x88C36]
    assert ADDRESS in references[0x88C40]
    for item in symbol.evidence:
        assert match.verify(model, symbol, item) is None
    assert any(link.type == "writer" and link.owner is symbol.meaning
               and link.to.symbols["7mfk"].address == 0x88BBA
               for link in symbol.meaning.links)
    images = dict(match.images(model, "7mfk"))
    assert set(images) == set(IMAGES)
    return symbol, images


@pytest.mark.parametrize("rom", IMAGES)
def test_closed_loop_indexed_byte_placement(compiled_placement, rom):
    symbol, images = compiled_placement
    data = images[rom]
    verify_closed_loop_byte(data, symbol)
    for pc, raw in (
        (0x88D24, "ffff128d"), (0x88CE0, "02f4"), (0x88C36, "d23a"),
        (0x88C3E, "326c"), (0x88C40, "0274"), (0x88C40, "0265"),
        (0x88C48, "0265"), (0x88C46, "7209"), (0x88C3C, "60c3"),
        (0x88B82, "e400"), (0x88BD0, "6d53"), (0x88BF6, "8912"),
        (0x88C00, "8b0d"), (0x88C0C, "890d"), (0x88C16, "8918"),
        (0x88C18, "a018"), (0x88C1A, "ee00"), (0x88C34, "660d"),
        (0x88D20, "000264a2"), (0x88C28, "0265"), (0x88C26, "724e"),
    ):
        changed = bytearray(data)
        replacement = bytes.fromhex(raw)
        changed[pc:pc + len(replacement)] = replacement
        assert changed != data
        with pytest.raises(AssertionError):
            verify_closed_loop_byte(bytes(changed), symbol)
    with pytest.raises(AssertionError):
        verify_closed_loop_byte(data, SymbolKey("7mfk", "ram", ADDRESS + 1))
