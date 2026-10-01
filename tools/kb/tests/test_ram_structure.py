"""Reviewed RAM placement slices, not whole-function or hardware proofs.

The fixed stock snapshots are independent of the image under test. Address
operations use the public SH-2E decoder; the fixtures supply the results of
physical calculations outside these slices. No general instruction runner or
persistent image/model/file mutation is involved. The snapshot copy takes
22038 -> 220d8 directly at length 0x80; it never enters 22094..220d6.
"""

from hashlib import sha256
from types import SimpleNamespace

import pytest

from kb import derive, match, repo, sh2
from kb.model import SymbolKey


OWNED_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
IMAGES = ("JK00A", "JK03A", "JK03B", "JK08A")

# Each half-open span locks only the reviewed instructions or literal/table
# bytes. It does not declare the surrounding function's physical semantics.
MAF = (
    (0x97EC2, "d0e8401e"),
    (0x97ECE, "dce6"),
    (0x97EDE, "eb03"),
    (0x97F8E, "917c660384f4206b80f184f2620384f50612202b62f380f2361c61634c0b60b360a3"),
    (0x9808A, "037b"),
    (0x98264, "ffff571800022558"),
    (0x22558, "2f262f362f46880089126423340c6024210034268b0c6024801134268b086024801234268b04602480133426710489ee64f663f6000b62f6"),
    (0x7EC1A, "e50094aed6af6b53"),
    (0x7ECAC, "441075018fba7603"),
    (0x7ED7C, "0157"),
    (0x7EEDC, "ffff5718"),
)
WORD_COPY = (
    (0x3C45C, "d20c604c40009308722e062dd20c323c000b0265"),
    (0x3C476, "07b2"), (0x3C490, "ffff1d34"),
    (0x3C49C, "ffff128c"), (0x3C3BE, "b04de400b04be401"),
)
SNAPSHOT = (
    (0x20E14, "ecf06ccc"), (0x20EF4, "d981"),
    (0x210FC, "00022038"),
    (0x20F48, "d17e626185612421d27d814160c3490b7090"),
    (0x21144, "ffff1094ffff1114"),
    (0x22038, "2f36e34033028b4bd301033e432b0009"),
    (0x220D8, "2f266323330c602633228b062102602633228b021101aff6710862f6000b63f6"),
)
SNAPSHOT_READER = (
    (0xA6DC8, "d094401e7ff86043400840003048400806124000026e22288f026403"),
    (0xA6EF2, "60f288028b48021272306043062e656006127634026c6053c903622c32008b3b"),
    (0xA701C, "00023ac4"),
    (0x23C14, "fffff754000400000000000000000000ffff4348000000d7000000020000000000000000000000010000000000000000ffff109801000000"),
    (0xA6FEE, "4f22d611e014006cc8808901bee3e400d60ee038006cc8018902e406aedb4f264f26000b0009"),
    (0xA7038, "000186c8"),
)
DECODER = (
    (0x4111C, "d027401e"),
    (0x41168, "631c81f4623342000912323c420879284200eb0c392c4b18ea0aed00e3ff51f36ddc633d60d3400831308d220c9e"),
    (0x411C8, "62e322b9d5126aac602d450b61a3"),
    (0x411D6, "a0022c00e3002c30"),
    (0x411DE, "7d016ddce3066bbd3d337afe4b098fca6aac63f0e10573012f30633c33128b93"),
    (0x411BC, "00023290"), (0x41218, "0002227c"),
    (0x232D0, "ffff1120ffff1121ffff111effff111fffff1e98ffff1e99"),
    (0x23298, "ffff1eb24000ffff"),
)
MAF_STATE = (
    (0x3A9AE, "d070401ed26d614cd56f410072106013062d"),
    (0x3A9C2, "0212c820666d72048d1e6013042d"),
    (0x3AA00, "021272046013a00102750265"),
    (0x3AB68, "ffff1048"), (0x3AB70, "ffff1dec"),
    (0x3A90C, "ec00de9364c3b07eed01b07c"),
    (0x3A958, "b02764c3b02564d3"),
    (0x3AF4C, "d06f401e7fe4d26f674c6d734d0084216e730212c9807204660360d3052d"),
    (0x3B10C, "ffff1dec"), (0x3A960, "b2ef64c3b2ed64d3"),
)
INJECTION = (
    (0x4E9F0, "986d"), (0x4E9FC, "ec00"),
    (0x4EA04, "d2816ccc6bc34b00720260b3062d"),
    (0x4EA52, "d26c7c016ccc60b3e602328c3c638fd002e5"),
    (0x4EACE, "0634"), (0x4EC04, "ffff128c"),
    (0x4EADC, "614c"), (0x4EAE2, "4100"),
    (0x4EB54, "d72b601396436273326c062d"),
    (0x4EBE2, "0634"), (0x4ED3E, "bec9e400bec7e401"),
)
CAM_COMMON = (
    (0xC1DF8, "6e4cdd85947c60e362d36ce3324c062c26688f134c08"),
    (0xC2248, "64e3bef9ee01"), (0xC226E, "bdbd64e3bee564e3"),
    (0xC2050, "d98d6a4c"), (0xC2288, "ffff128c"),
    (0xC2010, "ffff128c"), (0xC1EF8, "0890"),
)
MODE = (
    (0xC1E2A, "62d3324ce60160e30264"),
    (0xC1E5E, "62d3324ce60260e30264"),
    (0xC1E8A, "62d3324ce60060e30264"),
    (0xC1EAC, "62d3324ce60160e3026462d3324c60e3062c"),
    (0xC20DC, "9667629360a3326c062c"), (0xC21AE, "0890"),
)
LONGWORD = (
    (0xC1FEE, "960e60c33d6c0d26"), (0xC200E, "0818ffff128c"),
    (0xC2050, "d98d6a4c92a860a366934008362c0c6e"),
    (0xC21A8, "0818"),
)

# Expected public model binding. These are reviewed constants, not values
# regenerated from the compiler or the live image.
BINDINGS = {
    0xFFFF5A93: (0x97EC2, 0x37B, "test_maf_extension_record_path"),
    0xFFFF1A40: (0x3C46E, 2, "test_indexed_word_copy_path"),
    0xFFFF1098: (0x20F48, 4, "test_snapshot_destination_path"),
    0xFFFF111E: (0x20F50, 10, "test_snapshot_source_and_decoder_path"),
    0xFFFF1DF2: (0x3A9AE, 6, "test_maf_indexed_state_path"),
    0xFFFF18C2: (0x4EA52, 0x636, "test_injection_precursor_path"),
    0xFFFF1B1D: (0xC1DFA, 0x891, "test_indexed_mode_byte_paths"),
    0xFFFF1AA8: (0xC1DFA, 0x81C, "test_indexed_state_longword_path"),
}


def _expected_item(address):
    site, offset, _ = BINDINGS[address]
    return {"kind": "indirect", "supports": "identity", "mode": "base",
            "at": f"7mfk:{site:08x}", "value": offset}


def _binding(symbol, item, address):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", address)
    assert {key: item.get(key) for key in _expected_item(address)} == _expected_item(address)
    assert "legacy" not in item


def _locks(data, spans):
    for address, expected in spans:
        raw = bytes.fromhex(expected)
        assert data[address:address + len(raw)] == raw, f"stock slice at {address:08x} differs"


def _uint(data, address, size):
    raw = data[address:address + size]
    assert len(raw) == size
    return int.from_bytes(raw, "big")


def _insn(data, pc):
    return sh2.decode(_uint(data, pc, 2), pc)


def _math(data, registers, *pcs):
    """Evaluate only explicitly named register/address operations, without flow."""
    for pc in pcs:
        ins = _insn(data, pc)
        if ins.gbr is not None:
            assert ins.gbr[0] == "copy"
            registers["gbr"] = registers[ins.gbr[1]]
            continue
        assert ins.value is not None and ins.access is None, f"not address arithmetic: {pc:08x}"
        op, *args = ins.value
        n = ins.dest
        if op == "pool":
            address, size = args
            value = _uint(data, address, size)
            if size == 2:
                value = sh2.sext(value, 16)
        elif op == "const":
            [value] = args
        elif op == "copy":
            value = registers[args[0]]
        elif op == "gbr":
            value = registers["gbr"]
        elif op == "addi":
            value = registers[n] + args[0]
        elif op in ("add", "sub"):
            right = registers[args[0]]
            value = registers[n] + right if op == "add" else registers[n] - right
        elif op == "extu":
            bits, source = args
            value = registers[source] & ((1 << bits) - 1)
        elif op in ("shl", "shr"):
            value = registers[n] << args[0] if op == "shl" else registers[n] >> args[0]
        else:
            raise AssertionError(f"unsupported address operation {op} at {pc:08x}")
        registers[n] = value & sh2.MASK
    return registers


class _Memory:
    """Initialized sparse memory with writable destinations and visible guards."""

    def __init__(self):
        self.cells = {}
        self.writable = set()
        self.reads = []
        self.writes = []

    def region(self, address, raw, writable=False):
        for offset, byte in enumerate(raw):
            assert address + offset not in self.cells
            self.cells[address + offset] = byte
            if writable:
                self.writable.add(address + offset)

    def read(self, address, size):
        assert all(address + i in self.cells for i in range(size)), "unmapped read"
        self.reads.append((address, size))
        return int.from_bytes(bytes(self.cells[address + i] for i in range(size)), "big")

    def write(self, address, size, value):
        assert all(address + i in self.writable for i in range(size)), "unmapped write"
        raw = (value & ((1 << (8 * size)) - 1)).to_bytes(size, "big")
        self.writes.append((address, size))
        self.cells.update({address + i: byte for i, byte in enumerate(raw)})

    def bytes(self, address, count):
        return bytes(self.cells[address + i] for i in range(count))


def _operand(data, pc, registers, mode, width):
    ins = _insn(data, pc)
    access = ins.access
    assert access is not None and (access.mode, access.size) == (mode, width)
    address = registers[access.base] + access.disp
    if access.indexed:
        address += registers[0]
    return ins, address & sh2.MASK


def _load(data, pc, registers, memory, width):
    ins, address = _operand(data, pc, registers, "load", width)
    value = memory.read(address, width)
    registers[ins.dest] = sh2.sext(value, 8 * width) & sh2.MASK
    # Only group-6 postincrement loads occur in the reviewed copy helpers.
    if ins.word >> 12 == 6 and (ins.word & 15) in (4, 5, 6):
        source = (ins.word >> 4) & 15
        assert source != ins.dest
        registers[source] = (registers[source] + width) & sh2.MASK
    return address


def _store(data, pc, registers, memory, width):
    ins, address = _operand(data, pc, registers, "store", width)
    source = 0 if ins.word >> 12 == 8 else (ins.word >> 4) & 15
    memory.write(address, width, registers[source])
    return address


def _branch(data, pc, t, target, delayed):
    ins = _insn(data, pc)
    assert ins.flow in ("branch", "cbranch")
    assert (ins.target, ins.delayed) == (target, delayed)
    high = ins.word >> 8
    taken = ins.flow == "branch" or (t if high in (0x89, 0x8D) else not t)
    return ins.target if taken else pc + (4 if delayed else 2)


def _call(data, pc, registers, target, slot):
    ins = _insn(data, pc)
    assert ins.flow == "call" and ins.delayed
    actual = ins.target if ins.target is not None else registers[(ins.word >> 8) & 15]
    assert actual == target
    _math(data, registers, slot)


def _return(data, pc):
    assert (_insn(data, pc).flow, _insn(data, pc).delayed) == ("return", True)


def _guarded_destination(memory, address, count):
    memory.region(address - 4, b"\xa5" * (count + 8), writable=True)


def _guards(memory, address, count, after=b"\xa5" * 4):
    assert memory.bytes(address - 4, 4) == b"\xa5" * 4
    assert memory.bytes(address + count, 4) == after


def _byte_copy(data, destination, source, count, memory):
    """22558's actual byte-pointer/count loop, including zero and short tails."""
    r = {0: count, 1: destination, 2: source}
    # Saved r2/r3/r4 and return restores do not change pointer/count inputs.
    for pc, register in ((0x22558, 2), (0x2255A, 3), (0x2255C, 4)):
        ins = _insn(data, pc)
        assert ins.access == sh2.Access(15, -4, 4, "store")
        assert (ins.word >> 4) & 15 == register
    assert _uint(data, 0x2255E, 2) == 0x8800  # cmp/eq #0,r0
    exit_pc = _branch(data, 0x22560, count == 0, 0x22588, False)
    if exit_pc != 0x22588:
        _math(data, r, 0x22562, 0x22564)
        for _ in range(count + 1):
            finished = False
            for load, store, compare, branch in (
                (0x22566, 0x22568, 0x2256A, 0x2256C),
                (0x2256E, 0x22570, 0x22572, 0x22574),
                (0x22576, 0x22578, 0x2257A, 0x2257C),
                (0x2257E, 0x22580, 0x22582, 0x22586),
            ):
                _load(data, load, r, memory, 1)
                _store(data, store, r, memory, 1)
                word = _uint(data, compare, 2)
                assert word & 0xF00F == 0x3006  # cmp/hi Rm,Rn
                t = r[(word >> 8) & 15] > r[(word >> 4) & 15]
                if branch == 0x22586:
                    _math(data, r, 0x22584)
                    finished = _branch(data, branch, t, 0x22566, False) != 0x22566
                else:
                    finished = _branch(data, branch, t, 0x22588, False) == 0x22588
                if finished:
                    break
            if finished:
                break
        else:
            raise AssertionError("byte copy does not terminate")
    for pc, register in ((0x22588, 4), (0x2258A, 3), (0x2258E, 2)):
        ins = _insn(data, pc)
        assert ins.access == sh2.Access(15, 0, 4, "load") and ins.dest == register
    _return(data, 0x2258C)
    assert memory.writes == [(destination + i, 1) for i in range(count)]


def verify_maf_extension_record_path(data, symbol, item):
    """Bind the three-byte record and initialization geometry, not summary ORs."""
    _binding(symbol, item, 0xFFFF5A93)
    _locks(data, MAF)
    r = {15: 0x1000}
    _math(data, r, 0x97EC2, 0x97EC4, 0x97ECE, 0x97EDE,
          0x97F8E, 0x97F9E, 0x97FA2, 0x97FA6, 0x97FA8)
    _call(data, 0x97FAA, r, 0x22558, 0x97FAC)
    assert (r[1], r[2], r[0]) == (symbol.address, r[15], 3)
    assert r[1] - r["gbr"] == item["value"]
    for count in (0, 1, 2, r[0], 4, 5, 8):
        memory = _Memory()
        raw = bytes(range(0x31, 0x31 + count))
        memory.region(r[2], raw)
        _guarded_destination(memory, r[1], count)
        _byte_copy(data, r[1], r[2], count, memory)
        assert memory.bytes(r[1], count) == raw
        _guards(memory, r[1], count)
    init = {}
    _math(data, init, 0x7EC1A, 0x7EC1C, 0x7EC1E, 0x7EC20)
    assert (init[4], init[6], init[5]) == (0x157, r["gbr"], 0)
    # Placement only: traverse all record starts, not the omitted bit clearing.
    starts = []
    count = init[4]
    for _ in range(count):
        starts.append(init[6])
        decrement = _uint(data, 0x7ECAC, 2)
        assert decrement & 0xF0FF == 0x4010  # dt Rn
        n = (decrement >> 8) & 15
        init[n] = (init[n] - 1) & sh2.MASK
        t = init[n] == 0
        _math(data, init, 0x7ECAE)
        target = _branch(data, 0x7ECB0, t, 0x7EC28, True)
        _math(data, init, 0x7ECB2)  # also on the final, untaken iteration
        assert target == (0x7ECB4 if t else 0x7EC28)
    assert init[4] == 0 and init[5] == count
    assert len(starts) == 0x157 and starts[0x129] == symbol.address
    assert starts[1] - starts[0] == 3 and init[6] == starts[-1] + 3


def verify_indexed_word_copy_path(data, symbol, item):
    _binding(symbol, item, 0xFFFF1A40)
    _locks(data, WORD_COPY)
    caller = {}
    _call(data, 0x3C3BE, caller, 0x3C45C, 0x3C3C0)
    assert caller[4] == 0
    _call(data, 0x3C3C2, caller, 0x3C45C, 0x3C3C4)
    assert caller[4] == 1
    for bank in (0, caller[4], 0x100, 0x101):
        r = {4: bank}
        _math(data, r, 0x3C45C, 0x3C45E, 0x3C460, 0x3C462, 0x3C464)
        assert r[0] == 2 * (bank & 0xFF)
        memory = _Memory()
        memory.region(0xFFFF1D62, bytes.fromhex("13572468"))
        _guarded_destination(memory, 0xFFFF1A3E, 4)
        source = _load(data, 0x3C466, r, memory, 2)
        _math(data, r, 0x3C468, 0x3C46A)
        _return(data, 0x3C46C)
        destination = _store(data, 0x3C46E, r, memory, 2)  # RTS delay slot
        index = bank & 0xFF
        assert source == 0xFFFF1D62 + 2 * index
        assert destination == symbol.address - item["value"] + 2 * index
        assert memory.bytes(destination, 2) == (b"\x13\x57" if index == 0 else b"\x24\x68")
        assert memory.bytes(0xFFFF1A3E + 2 * (1 - index), 2) == b"\xa5\xa5"
        _guards(memory, 0xFFFF1A3E, 4)


def _snapshot_copy(data):
    """Caller setup and the direct large-copy arm; no unclassified prefix."""
    _locks(data, SNAPSHOT)
    r = {}
    _math(data, r, 0x20E14, 0x20E16, 0x20EF4, 0x20F48, 0x20F50, 0x20F54)
    assert r[12] == 0xF0  # unsigned low byte of the sign-extended immediate
    _call(data, 0x20F56, r, 0x22038, 0x20F58)
    assert (r[1], r[2], r[0]) == (0xFFFF1094, 0xFFFF1114, 0x80)
    destination, source, count = r[1], r[2], r[0]
    memory = _Memory()
    raw = bytes((17 * i + 3) & 0xFF for i in range(count))
    memory.region(source, raw + b"\xde\xad\xbe\xef")
    # The regions are adjacent: the first source word is also the destination
    # trailing sentinel. It remains read-only, not a synthetic writable guard.
    assert destination + count == source
    memory.region(destination - 4, b"\xa5" * (count + 4), writable=True)
    # 22038 saves r3; 220d8 saves r2. Restore contract is locked below.
    assert _insn(data, 0x22038).access == sh2.Access(15, -4, 4, "store")
    _math(data, r, 0x2203A)
    assert _uint(data, 0x2203C, 2) == 0x3302  # unsigned cmp/hs r0,r3
    assert _branch(data, 0x2203E, r[3] >= r[0], 0x220D8, False) == 0x220D8
    assert _insn(data, 0x220D8).access == sh2.Access(15, -4, 4, "store")
    _math(data, r, 0x220DA, 0x220DC)
    for _ in range(count // 8 + 1):
        _load(data, 0x220DE, r, memory, 4)
        assert _uint(data, 0x220E0, 2) == 0x3322
        if _branch(data, 0x220E2, r[3] >= r[2], 0x220F2, False) == 0x220F2:
            break
        _store(data, 0x220E4, r, memory, 4)
        _load(data, 0x220E6, r, memory, 4)
        assert _uint(data, 0x220E8, 2) == 0x3322
        if _branch(data, 0x220EA, r[3] >= r[2], 0x220F2, False) == 0x220F2:
            break
        _store(data, 0x220EC, r, memory, 4)
        assert _branch(data, 0x220EE, False, 0x220DE, True) == 0x220DE
        _math(data, r, 0x220F0)
    else:
        raise AssertionError("long copy does not terminate")
    assert (_insn(data, 0x220F2).dest, _insn(data, 0x220F2).access) == (
        2, sh2.Access(15, 0, 4, "load"))
    _return(data, 0x220F4)
    assert (_insn(data, 0x220F6).dest, _insn(data, 0x220F6).access) == (
        3, sh2.Access(15, 0, 4, "load"))
    assert memory.bytes(destination, count) == raw
    assert memory.writes == [(destination + i, 4) for i in range(0, count, 4)]
    assert memory.reads == [(source + i, 4) for i in range(0, count + 4, 4)]
    _guards(memory, destination, count, after=raw[:4])
    assert memory.bytes(source + count, 4) == b"\xde\xad\xbe\xef"
    return destination, source, count, memory


def verify_snapshot_destination_path(data, symbol, item):
    _binding(symbol, item, 0xFFFF1098)
    _locks(data, SNAPSHOT_READER)
    destination, source, count, memory = _snapshot_copy(data)
    assert destination + item["value"] == symbol.address
    assert memory.bytes(symbol.address, 1) == memory.bytes(source + item["value"], 1)
    caller = {}
    _math(data, caller, 0xA6FFE, 0xA7000)
    _, flag_address = _operand(data, 0xA7002, caller, "load", 1)
    assert flag_address == 0x18700
    assert _uint(data, 0xA7004, 2) == 0xC801  # bit 0 guard; not a per-family value claim
    assert _branch(data, 0xA7006, True, 0xA700E, False) == 0xA700E
    assert _branch(data, 0xA7006, False, 0xA700E, False) == 0xA7008
    _math(data, caller, 0xA7008)
    assert caller[4] == 6
    assert _branch(data, 0xA700A, False, 0xA6DC4, True) == 0xA6DC4
    slot = _insn(data, 0xA700C)
    assert slot.word == 0x4F26  # restore PR in the tail branch delay slot
    for j in (5, caller[4], 7):
        r = {4: j}
        _math(data, r, 0xA6DC8, 0xA6DCA, 0xA6DCE, 0xA6DD0, 0xA6DD2,
              0xA6DD4, 0xA6DD6, 0xA6DD8, 0xA6DDA)
        assert r[0] == 0x38 * j
        _, entry = _operand(data, 0xA6DDC, r, "load", 4)
        assert entry == 0x23AC4 + 0x38 * j
        assert _branch(data, 0xA6DE0, False, 0xA6DE8, True) == 0xA6DE8
        _math(data, r, 0xA6DE2)
        # This is the reviewed pointer-reader slice after intervening monitor
        # logic. r4 carries the decoded table displacement; no monitor stub.
        _math(data, r, 0xA6EF8, 0xA6EFA, 0xA6EFC)
        _, pointer_slot = _operand(data, 0xA6EFE, r, "load", 4)
        assert pointer_slot == entry + 0x30
        if j == 6:
            assert (entry, pointer_slot) == (0x23C14, 0x23C44)
            table = _Memory()
            table.region(pointer_slot, data[pointer_slot:pointer_slot + 4])
            _load(data, 0xA6EFE, r, table, 4)
            assert r[6] == symbol.address
            assert _load(data, 0xA6F00, r, memory, 1) == symbol.address
    assert source + item["value"] == 0xFFFF1118 and item["value"] < count


def verify_snapshot_source_and_decoder_path(data, symbol, item):
    """Prove snapshot and decoder storage, not full decoder or physical semantics.

    The mask/shift call arguments and target are bound to stock bytes, but the
    shift helper's return semantics and the acceptance predicates are not
    reproduced. An opaque returned byte exercises the accepted storage slice.
    """
    _binding(symbol, item, 0xFFFF111E)
    _locks(data, DECODER)
    destination, source, count, copied = _snapshot_copy(data)
    assert source + item["value"] == symbol.address
    assert destination + item["value"] == 0xFFFF109E
    assert copied.bytes(0xFFFF109E, 1) == copied.bytes(symbol.address, 1)
    for device in (0, 1, 0x101):
        r = {1: device}
        _math(data, r, 0x4111C, 0x4111E, 0x41168, 0x4116C, 0x4116E,
              0x41170, 0x41172, 0x41174, 0x41176, 0x41178,
              0x4117A, 0x4117C, 0x4117E, 0x41180, 0x41182)
        assert r[9] == 0x23290 + 0x28 + 0x18 * (device & 0xFF)
        if device & 0xFF != 1:
            continue
        assert _uint(data, 0x23298, 4) == 0xFFFF1EB2
        assert _uint(data, 0x2329C, 2) == 0x4000
        for k in range(6):
            _math(data, r, 0x41188, 0x4118C, 0x4118E)
            _, pointer_slot = _operand(data, 0x41194, r, "load", 4)
            assert pointer_slot == 0x232D0 + 4 * k
            table = _Memory()
            table.region(pointer_slot, data[pointer_slot:pointer_slot + 4])
            _load(data, 0x41194, r, table, 4)
            assert _branch(data, 0x41192, True, 0x411DA, True) == 0x411DA
            assert _branch(data, 0x41192, False, 0x411DA, True) == 0x41196
            # The pointer load is the BT/S delay slot on both outcomes.
            if k == 2:
                assert pointer_slot == 0x232D8 and r[12] == symbol.address
                assert (r[11], r[10]) == (0xC0, 6)
                for word, returned_byte in ((0, 0), (0x40, 1), (0x80, 2),
                                            (0xC0, 3), (0xFFFF, 0xFF), (0xAA55, 0x80)):
                    for accepted in (False, True):
                        m = _Memory()
                        _guarded_destination(m, symbol.address, 1)
                        state = {**r, 14: word}
                        _math(data, state, 0x411C8)
                        word_and = _uint(data, 0x411CA, 2)
                        assert word_and & 0xF00F == 0x2009  # and Rm,Rn
                        n, source_register = (word_and >> 8) & 15, (word_and >> 4) & 15
                        state[n] &= state[source_register]
                        _math(data, state, 0x411CC, 0x411CE, 0x411D0)
                        _call(data, 0x411D2, state, 0x2227C, 0x411D4)
                        assert (state[0], state[1]) == (word & 0xC0, 6)
                        # Only call arguments and return-byte placement are
                        # proven here. The table-driven shift subroutine is
                        # outside this fixture; this is not a decoder-value
                        # proof of (word >> 6) & 3.
                        state[0] = returned_byte
                        if accepted:
                            assert _branch(data, 0x411D6, False, 0x411DE, True) == 0x411DE
                            address = _store(data, 0x411D8, state, m, 1)
                        else:
                            _math(data, state, 0x411DA)
                            address = _store(data, 0x411DC, state, m, 1)
                        assert address == symbol.address
                        assert m.bytes(address, 1) == bytes([returned_byte if accepted else 0])
                        _guards(m, symbol.address, 1)
            _math(data, r, 0x411DE, 0x411E0, 0x411E2, 0x411E8, 0x411EA, 0x411EE)
            assert _uint(data, 0x411E6, 2) == 0x3D33  # cmp/ge r3,r13
            assert _branch(data, 0x411EC, r[13] >= r[3], 0x41184, True) == (
                0x411F0 if k == 5 else 0x41184)
    assert item["value"] < count


def _maf_callers(data):
    r = {}
    _math(data, r, 0x3A90C)
    _call(data, 0x3A912, r, 0x3AA12, 0x3A914)
    assert (r[12], r[13]) == (0, 1)
    for call, slot, target, bank in (
        (0x3A958, 0x3A95A, 0x3A9AA, 0), (0x3A95C, 0x3A95E, 0x3A9AA, 1),
        (0x3A960, 0x3A962, 0x3AF42, 0), (0x3A964, 0x3A966, 0x3AF42, 1),
    ):
        _call(data, call, r, target, slot)
        assert r[4] == bank


def verify_maf_indexed_state_path(data, symbol, item):
    _binding(symbol, item, 0xFFFF1DF2)
    _locks(data, MAF_STATE)
    _maf_callers(data)
    for bank in (0, 1, 0x100, 0x101):
        r = {4: bank}
        _math(data, r, 0x3A9AE, 0x3A9B0, 0x3A9B2, 0x3A9B4, 0x3A9B8,
              0x3A9BA, 0x3A9BC)
        m = _Memory()
        m.region(0xFFFF1058, bytes.fromhex("3579468a"))
        _guarded_destination(m, 0xFFFF1DF0, 4)
        source = _load(data, 0x3A9BE, r, m, 2)
        _math(data, r, 0x3A9C2, 0x3A9C6, 0x3A9C8)
        assert source == 0xFFFF1058 + 2 * (bank & 0xFF)
        for direct in (True, False):
            state = dict(r)
            assert _branch(data, 0x3A9CA, direct, 0x3AA0A, True) == (
                0x3AA0A if direct else 0x3A9CE)
            _math(data, state, 0x3A9CC)
            if direct:
                site = 0x3AA0A
            else:
                _load(data, 0x3A9CE, state, m, 2)
                # The filtered result is an external fixture value, not a
                # model of the omitted filter's physical arithmetic.
                state[7] = 0xACED
                _math(data, state, 0x3AA00, 0x3AA02, 0x3AA04)
                assert _branch(data, 0x3AA06, False, 0x3AA0C, True) == 0x3AA0C
                site = 0x3AA08
            address = _store(data, site, state, m, 2)
            index = bank & 0xFF
            assert address == symbol.address - 2 + 2 * index
            assert address - state["gbr"] == item["value"] - 2 + 2 * index
            assert m.bytes(address, 2) == (state[6] if direct else state[7]).to_bytes(2, "big")
            assert m.bytes(0xFFFF1DF0 + 2 * (1 - index), 2) == b"\xa5\xa5"
            _guards(m, 0xFFFF1DF0, 4)
        reader = {4: bank}
        _math(data, reader, 0x3AF4C, 0x3AF4E, 0x3AF54, 0x3AF56, 0x3AF58,
              0x3AF5E, 0x3AF62, 0x3AF66)
        assert _load(data, 0x3AF68, reader, m, 2) == address
        assert reader[5] & 0xFFFF == 0xACED


def verify_injection_precursor_path(data, symbol, item):
    _binding(symbol, item, 0xFFFF18C2)
    _locks(data, INJECTION)
    r = {}
    _math(data, r, 0x4E9F0, 0x4E9FC)
    m = _Memory()
    _guarded_destination(m, 0xFFFF18C0, 4)
    for index, result in enumerate((0x1234, 0xBEEF)):
        _math(data, r, 0x4EA06, 0x4EA08, 0x4EA0A)
        assert r[11] == 2 * index
        r[14] = result  # omitted precursor calculation result
        _math(data, r, 0x4EA52, 0x4EA54, 0x4EA56, 0x4EA58, 0x4EA5A, 0x4EA5C)
        assert _uint(data, 0x4EA5E, 2) == 0x3C63
        next_pc = _branch(data, 0x4EA60, r[12] >= r[6], 0x4EA04, True)
        address = _store(data, 0x4EA62, r, m, 2)  # also final fall-through
        assert address == symbol.address - 2 + 2 * index
        assert next_pc == (0x4EA04 if index == 0 else 0x4EA64)
    assert r[12] == 2 and m.writes == [(0xFFFF18C0, 2), (symbol.address, 2)]
    assert symbol.address - _uint(data, 0x4EC04, 4) == item["value"]
    assert m.bytes(0xFFFF18C0, 4) == bytes.fromhex("1234beef")
    _guards(m, 0xFFFF18C0, 4)
    caller = {}
    for pc, slot, bank in ((0x4ED3E, 0x4ED40, 0), (0x4ED42, 0x4ED44, 1)):
        _call(data, pc, caller, 0x4EAD4, slot)
        assert caller[4] == bank
    for bank in (0, 1, 0x100, 0x101):
        reader = {4: bank}
        _math(data, reader, 0x4EADC, 0x4EAE2, 0x4EB54, 0x4EB56, 0x4EB58,
              0x4EB5A, 0x4EB5C)
        address = _load(data, 0x4EB5E, reader, m, 2)
        assert address == symbol.address - 2 + 2 * (bank & 0xFF)
        assert reader[6] & 0xFFFF == (0x1234 if bank & 0xFF == 0 else 0xBEEF)


def _cam_callers(data):
    caller = {14: 0}
    _math(data, caller, 0xC2248)
    _call(data, 0xC224A, caller, 0xC2040, 0xC224C)
    assert caller[14] == 1
    _call(data, 0xC226E, caller, 0xC1DEC, 0xC2270)
    assert caller[4] == 1
    _call(data, 0xC2272, caller, 0xC2040, 0xC2274)
    assert caller[4] == 1


def _cam_entry(data, bank, zero):
    r = {4: bank}
    _math(data, r, 0xC1DF8, 0xC1DFA, 0xC1DFC, 0xC1DFE,
          0xC1E00, 0xC1E02, 0xC1E04)
    m = _Memory()
    m.region(0xFFFF1B1C, bytes([0 if zero else 2]) * 2)
    _load(data, 0xC1E06, r, m, 1)
    assert _uint(data, 0xC1E08, 2) == 0x2668
    assert _branch(data, 0xC1E0A, r[6] == 0, 0xC1E34, True) == (
        0xC1E0E if zero else 0xC1E34)
    _math(data, r, 0xC1E0C)  # SHLL2 in BF/S delay slot on both outcomes
    assert (r[14], r[12]) == (bank & 0xFF, 4 * (bank & 0xFF))
    return r


def verify_indexed_mode_byte_paths(data, symbol, item):
    _binding(symbol, item, 0xFFFF1B1D)
    _locks(data, CAM_COMMON + MODE)
    _cam_callers(data)
    for bank in (0, 1, 0x100, 0x101):
        for zero in (True, False):
            entry = _cam_entry(data, bank, zero)
            for start, value in ((0xC1E2A, 1), (0xC1E5E, 2),
                                 (0xC1E8A, 0), (0xC1EAC, 1)):
                r = dict(entry)
                _math(data, r, start, start + 2, start + 4, start + 6)
                m = _Memory()
                _guarded_destination(m, 0xFFFF1B1C, 2)
                address = _store(data, start + 8, r, m, 1)
                index = bank & 0xFF
                assert address == symbol.address - 1 + index
                assert address - entry[13] == item["value"] - 1 + index
                assert m.bytes(address, 1) == bytes([value])
                assert m.bytes(0xFFFF1B1C + 1 - index, 1) == b"\xa5"
                _guards(m, 0xFFFF1B1C, 2)
                if start == 0xC1EAC:
                    _math(data, r, 0xC1EB6, 0xC1EB8, 0xC1EBA)
                    assert _load(data, 0xC1EBC, r, m, 1) == address
                    assert r[6] == value
                reader = {4: bank}
                _math(data, reader, 0xC2050, 0xC2052, 0xC20DC,
                      0xC20DE, 0xC20E0, 0xC20E2)
                assert _load(data, 0xC20E4, reader, m, 1) == address
                assert reader[6] == value


def verify_indexed_state_longword_path(data, symbol, item):
    _binding(symbol, item, 0xFFFF1AA8)
    _locks(data, CAM_COMMON + LONGWORD)
    _cam_callers(data)
    for bank in (0, 1, 0x100, 0x101):
        for zero in (True, False):
            r = _cam_entry(data, bank, zero)
            base = r[13]
            r[2] = 0x12345678 if bank & 0xFF == 0 else 0x89ABCDEF
            value = r[2]  # omitted controller calculation result
            _math(data, r, 0xC1FEE, 0xC1FF0, 0xC1FF2)
            m = _Memory()
            _guarded_destination(m, 0xFFFF1AA4, 8)
            address = _store(data, 0xC1FF4, r, m, 4)
            index = bank & 0xFF
            assert address == symbol.address - 4 + 4 * index
            assert address - base == item["value"] - 4 + 4 * index
            assert m.bytes(address, 4) == value.to_bytes(4, "big")
            assert m.bytes(0xFFFF1AA4 + 4 * (1 - index), 4) == b"\xa5" * 4
            _guards(m, 0xFFFF1AA4, 8)
            reader = {4: bank}
            _math(data, reader, 0xC2050, 0xC2052, 0xC2054, 0xC2056,
                  0xC2058, 0xC205A, 0xC205C)
            assert _load(data, 0xC205E, reader, m, 4) == address
            assert reader[12] == value


@pytest.fixture(scope="module")
def stock_images():
    # match.images only needs these public model attributes. A compiler is not
    # needed to load images or to reject any of the byte mutations below.
    image_model = SimpleNamespace(root=repo.ROOT, layouts=repo.layouts())
    images = dict(match.images(image_model, "7mfk"))
    assert set(images) == set(IMAGES)
    owned = derive.image_bytes(repo.layout("7mfk"))
    assert images["JK08A"] == owned and sha256(owned).hexdigest() == OWNED_SHA256
    return images


@pytest.fixture(scope="module")
def compiled_bindings():
    from kb import compile

    # Compile once for positive evidence binding. Pure mutation helpers never
    # read the graph, recompile it, or change symbol evidence.
    model = compile.cached(repo.ROOT)
    found = {}
    for address, (_, _, key) in BINDINGS.items():
        symbol = model.symbols[SymbolKey("7mfk", "ram", address)]
        candidates = [item for item in symbol.evidence
                      if item.get("kind") == "indirect" and item.get("mode") == "base"
                      and "legacy" not in item]
        assert len(candidates) == 1, f"{address:08x}: explicit base item is not unique"
        [item] = candidates
        _binding(symbol, item, address)
        assert any(evidence.get("kind") == "test"
                   and evidence.get("supports") == "identity"
                   and evidence.get("path") == "tools/kb/tests/test_ram_structure.py"
                   and evidence.get("key") == key and "legacy" not in evidence
                   for evidence in symbol.evidence), f"{address:08x}: path test binding is absent"
        found[address] = symbol, item
    return found


def _negative_cases(helper, data, symbol, item, mutations):
    for pc, raw in mutations:
        changed = bytearray(data)
        changed[pc:pc + len(bytes.fromhex(raw))] = bytes.fromhex(raw)
        assert changed != data
        with pytest.raises(AssertionError):
            helper(bytes(changed), symbol, item)
    for key, value in (("value", item["value"] + 1), ("at", "7mfk:00000000"),
                       ("mode", "gbr"), ("supports", "homology")):
        with pytest.raises(AssertionError):
            helper(data, symbol, {**item, key: value})
    with pytest.raises(AssertionError):
        helper(data, SymbolKey("7mfk", "ram", symbol.address + 1), item)


@pytest.mark.parametrize("rom", IMAGES)
def test_maf_extension_record_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF5A93]
    data = stock_images[rom]
    verify_maf_extension_record_path(data, symbol, item)
    _negative_cases(verify_maf_extension_record_path, data, symbol, item, (
        (0x98264, "ffff5719"), (0x9808A, "037a"), (0x97EC2, "d0e7"),
        (0x97EC4, "411e"), (0x97F9E, "0712"), (0x97FA6, "362c"),
        (0x97EDE, "eb04"), (0x97FAC, "60a3"), (0x98268, "0002255a"),
        (0x22568, "2101"), (0x2256C, "8b0b"), (0x22584, "7103"),
        (0x2258E, "0009"), (0x7ED7C, "0156"), (0x7EEDC, "ffff5719"),
        (0x7ECB0, "8bba"), (0x7ECB2, "7602"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_indexed_word_copy_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF1A40]
    data = stock_images[rom]
    verify_indexed_word_copy_path(data, symbol, item)
    _negative_cases(verify_indexed_word_copy_path, data, symbol, item, (
        (0x3C490, "ffff1d35"), (0x3C49C, "ffff128e"), (0x3C476, "07b0"),
        (0x3C45C, "d20d"), (0x3C45E, "604d"), (0x3C460, "4008"),
        (0x3C466, "062c"), (0x3C46E, "0365"), (0x3C46E, "0266"),
        (0x3C46C, "0009"), (0x3C3C4, "e400"), (0x3C3C2, "b04a"),
    ))


SNAPSHOT_MUTATIONS = (
    (0x20E16, "6cce"), (0x20F58, "7094"), (0x20F48, "d17f"),
    (0x21144, "ffff1098"), (0x21148, "ffff1118"), (0x210FC, "00022094"),
    (0x2203E, "894b"), (0x220DE, "6025"), (0x220E4, "2101"),
    (0x220E2, "8b05"), (0x220EA, "8902"), (0x220F0, "7104"),
    (0x220F6, "0009"),
)


@pytest.mark.parametrize("rom", IMAGES)
def test_snapshot_destination_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF1098]
    data = stock_images[rom]
    verify_snapshot_destination_path(data, symbol, item)
    if rom == "JK08A":
        assert data[0x18700:0x18701] == b"\x00"  # owned calibration only
    _negative_cases(verify_snapshot_destination_path, data, symbol, item,
                    SNAPSHOT_MUTATIONS + (
                        (0xA6DD2, "4008"), (0xA6EFE, "072e"), (0xA6F00, "6561"),
                        (0x23C44, "ffff1099"), (0xA7008, "e405"),
                        (0xA700A, "aeda"), (0xA700C, "0009"), (0xA701C, "00023ac8"),
                    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_snapshot_source_and_decoder_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF111E]
    data = stock_images[rom]
    verify_snapshot_source_and_decoder_path(data, symbol, item)
    _negative_cases(verify_snapshot_source_and_decoder_path, data, symbol, item,
                    SNAPSHOT_MUTATIONS + (
                        (0x411BC, "00023294"), (0x4116E, "4208"), (0x4118E, "4000"),
                        (0x41194, "0c8e"), (0x232D8, "ffff111f"), (0x41192, "8922"),
                        (0x411D8, "2c01"), (0x411DC, "2c31"), (0x411D6, "a003"),
                        (0x4117A, "eb0d"), (0x411E8, "7aff"), (0x411EE, "6aad"),
                        (0x411CA, "22a9"), (0x411D0, "602c"), (0x411D4, "61b3"),
                        (0x41218, "0002227e"), (0x411CC, "d513"),
                    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_maf_indexed_state_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF1DF2]
    data = stock_images[rom]
    verify_maf_indexed_state_path(data, symbol, item)
    _negative_cases(verify_maf_indexed_state_path, data, symbol, item, (
        (0x3AB70, "ffff1ded"), (0x3AB68, "ffff104a"), (0x3A9AE, "d071"),
        (0x3A9B4, "614d"), (0x3A9B8, "4108"), (0x3A914, "ed00"),
        (0x3A95E, "64c3"), (0x3A9CA, "891e"), (0x3A9CC, "6023"),
        (0x3AA08, "0375"), (0x3AA0A, "0264"), (0x3AA06, "a002"),
        (0x3B10C, "ffff1dee"), (0x3AF68, "052e"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_injection_precursor_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF18C2]
    data = stock_images[rom]
    verify_injection_precursor_path(data, symbol, item)
    _negative_cases(verify_injection_precursor_path, data, symbol, item, (
        (0x4EC04, "ffff128e"), (0x4EACE, "0636"), (0x4EA52, "d36c"),
        (0x4E9FC, "ec01"), (0x4EA0A, "4b08"), (0x4EA58, "60c3"),
        (0x4EA5A, "e601"), (0x4EA60, "8bd0"), (0x4EA62, "02e6"),
        (0x4EA62, "03e5"), (0x4EBE2, "0636"), (0x4EB5E, "062c"),
        (0x4ED44, "e400"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_indexed_mode_byte_paths(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF1B1D]
    data = stock_images[rom]
    verify_indexed_mode_byte_paths(data, symbol, item)
    _negative_cases(verify_indexed_mode_byte_paths, data, symbol, item, (
        (0xC2010, "ffff128d"), (0xC1EF8, "0891"), (0xC1DF8, "6e4d"),
        (0xC1DFA, "dd84"), (0xC224C, "ee00"), (0xC2270, "64d3"),
        (0xC1E32, "0364"), (0xC1E66, "0265"), (0xC1E92, "0266"),
        (0xC1EB4, "0274"), (0xC1E0A, "8931"), (0xC1E0C, "4c00"),
        (0xC21AE, "0892"), (0xC20E4, "062d"), (0xC2288, "ffff128e"),
    ))


@pytest.mark.parametrize("rom", IMAGES)
def test_indexed_state_longword_path(stock_images, compiled_bindings, rom):
    symbol, item = compiled_bindings[0xFFFF1AA8]
    data = stock_images[rom]
    verify_indexed_state_longword_path(data, symbol, item)
    _negative_cases(verify_indexed_state_longword_path, data, symbol, item, (
        (0xC2010, "ffff128d"), (0xC200E, "081c"), (0xC1DFA, "dd84"),
        (0xC1DF8, "6e4d"), (0xC224C, "ee00"), (0xC2270, "64d3"),
        (0xC1E0A, "8931"), (0xC1E0C, "4c00"), (0xC1FF0, "60e3"),
        (0xC1FF4, "0d25"), (0xC1FF4, "0c26"), (0xC1FEE, "960f"),
        (0xC21A8, "081c"), (0xC205A, "4000"), (0xC205E, "0c6d"),
    ))
