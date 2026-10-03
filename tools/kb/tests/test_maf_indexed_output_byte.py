"""Fixed-byte placement of 3aa12's indexed byte, not its physical calculation."""

import pytest

from kb import checks, compile, levels, match, repo, sh2, sites, store
from kb.model import SymbolKey


ADDRESS = 0xFFFF3979
BASE = 0xFFFF3968
FUNCTION = 0x3AA12
IMAGES = ("JK00A", "JK03A", "JK03B", "JK08A")
PATH = "tools/kb/tests/test_maf_indexed_output_byte.py"
KEY = "test_maf_indexed_output_byte_placement"

# Reviewed stock words reconstructed from the SH-2E listing, not refreshed
# from the image under test. Only index preservation and byte placement are
# covered; the divide calls and the physical calculation remain outside.
SPANS = (
    (0x3AA22, "d056401e"),
    (0x3AA32, "674c"),
    (0x3AA36, "607380f3"),
    (0x3AB7C, "ffff3968"),
    (0x3AC74, "02127211a019e6ff"),
    (0x3ACA6, "021284f37211670c60730264021272116073062c"),
)
EVIDENCE = [
    {"kind": "rom-bytes", "supports": "identity", "at": "7mfk:0003ab7c",
     "value": "ffff3968"},
    {"kind": "l0-context", "supports": "identity", "at": "7mfk:0003acb0",
     "key": "reference", "value": {"span": 1, "named": [
         "0003aa12", "0003ab7c", "ffff3968", "ffff3979"]}},
    {"kind": "l0-context", "supports": "identity", "at": "7mfk:0003acb8",
     "key": "reference", "value": {"span": 1, "named": [
         "0003aa12", "0003ab7c", "ffff3968", "ffff3979"]}},
    {"kind": "test", "supports": "identity", "path": PATH, "key": KEY},
]


def _insn(data, pc):
    raw = data[pc:pc + 2]
    assert len(raw) == 2
    return sh2.decode(int.from_bytes(raw, "big"), pc)


def _value(data, pc, dest, value):
    ins = _insn(data, pc)
    assert (ins.dest, ins.value, ins.access) == (dest, value, None)


def _address(data, gbr_pc, offset_pc, gbr, index):
    _value(data, gbr_pc, 2, ("gbr",))
    _value(data, offset_pc, 2, ("addi", 0x11))
    return (gbr + 0x11 + index) & sh2.MASK


def verify_indexed_byte(data, symbol):
    assert (symbol.layout, symbol.kind, symbol.address) == ("7mfk", "ram", ADDRESS)
    for pc, expected in SPANS:
        raw = bytes.fromhex(expected)
        assert data[pc:pc + len(raw)] == raw, f"stock slice at {pc:08x} differs"
    _value(data, 0x3AA22, 0, ("pool", 0x3AB7C, 4))
    assert _insn(data, 0x3AA24).gbr == ("copy", 0)
    gbr = int.from_bytes(data[0x3AB7C:0x3AB80], "big")
    assert gbr == BASE and symbol.address - gbr == 0x11
    _value(data, 0x3AA32, 7, ("extu", 8, 4))
    _value(data, 0x3AA36, 0, ("copy", 7))
    assert _insn(data, 0x3AA38).access == sh2.Access(15, 3, 1, "store")
    assert _insn(data, 0x3AA38).word == 0x80F3  # save r0 as a byte
    store = _insn(data, 0x3ACB0)
    read = _insn(data, 0x3ACB8)
    assert store.access == sh2.Access(2, 0, 1, "store", True)
    assert store.word == 0x0264  # source r6, not the index in r0
    assert read.access == sh2.Access(2, 0, 1, "load", True) and read.dest == 6
    for argument in (0, 1, 0x100, 0x101):
        index = argument & 0xFF
        saved = index  # the byte at sp+3 survives the omitted divide calls
        for zero_denominator in (False, True):
            if zero_denominator:
                address = _address(data, 0x3AC74, 0x3AC76, gbr, index)
                branch = _insn(data, 0x3AC78)
                assert (branch.flow, branch.target, branch.delayed) == (
                    "branch", 0x3ACAE, True)
                _value(data, 0x3AC7A, 6, ("const", sh2.MASK))  # delay slot
                results = (sh2.MASK,)
            else:
                reload = _insn(data, 0x3ACA8)
                assert reload.access == sh2.Access(15, 3, 1, "load") and reload.dest == 0
                _value(data, 0x3ACAC, 7, ("extu", 8, 0))
                index = sh2.sext(saved, 8) & 0xFF
                address = _address(data, 0x3ACA6, 0x3ACAA, gbr, index)
                # Arbitrary calculation results exercise byte boundaries;
                # they do not reconstruct either divide helper's semantics.
                results = (0, 0x7F, 0x80, 0xFF)
            _value(data, 0x3ACAE, 0, ("copy", 7))
            assert address == symbol.address + (argument & 0xFF)
            reader_address = _address(data, 0x3ACB2, 0x3ACB4, gbr, index)
            _value(data, 0x3ACB6, 0, ("copy", 7))
            assert reader_address == address
            for result in results:
                # Two indexed bytes between four-byte guards. The other
                # element and both guards must survive the byte store.
                memory = bytearray(b"\xa5" * 10)
                slot = address - (symbol.address - 4)
                assert slot in (4, 5)
                memory[slot] = result & 0xFF
                loaded = sh2.sext(memory[reader_address - (symbol.address - 4)], 8)
                assert loaded & 0xFF == result & 0xFF
                assert memory[4 + (1 - index)] == 0xA5
                assert memory[:4] == memory[6:] == b"\xa5" * 4


@pytest.fixture(scope="module")
def compiled_placement():
    model = compile.cached(repo.ROOT)
    symbol = model.symbols[SymbolKey("7mfk", "ram", ADDRESS)]
    assert symbol.sources == {store.path_of("ram", symbol.meaning.name).as_posix()}
    assert symbol.value("level") == "code" and symbol.value("unit") == "raw"
    assert len(symbol.evidence) == len(EVIDENCE) and all(item in symbol.evidence for item in EVIDENCE)
    assert checks._owned(model, symbol)
    assert levels.held(model, symbol)
    # Actual derived L0 references already hold this byte. An invented
    # indirect base item is neither necessary nor part of the declaration.
    references = sites.references("7mfk", model.root)
    assert BASE in references[0x3AA22]
    assert ADDRESS in references[0x3ACB0] and ADDRESS in references[0x3ACB8]
    for item in symbol.evidence:
        assert match.verify(model, symbol, item) is None
    for relation in ("writer", "reader"):
        assert any(link.type == relation and link.owner is symbol.meaning
                   and link.to.symbols["7mfk"].address == FUNCTION
                   for link in symbol.meaning.links)
    images = dict(match.images(model, "7mfk"))
    assert set(images) == set(IMAGES)
    return symbol, images


@pytest.mark.parametrize("rom", IMAGES)
def test_maf_indexed_output_byte_placement(compiled_placement, rom):
    symbol, images = compiled_placement
    data = images[rom]
    verify_indexed_byte(data, symbol)
    for pc, raw in (
        (0x3AB7C, "ffff3969"), (0x3AA22, "d055"), (0x3AA24, "411e"),
        (0x3AA32, "674d"), (0x3AA38, "80f2"), (0x3ACA8, "84f2"),
        (0x3AC76, "7212"), (0x3ACAA, "7210"), (0x3ACB4, "7212"),
        (0x3AC78, "a01a"), (0x3AC7A, "e600"), (0x3ACAC, "670d"),
        (0x3ACB0, "0274"), (0x3ACB0, "0265"), (0x3ACB8, "062d"),
    ):
        changed = bytearray(data)
        replacement = bytes.fromhex(raw)
        changed[pc:pc + len(replacement)] = replacement
        assert changed != data
        with pytest.raises(AssertionError):
            verify_indexed_byte(bytes(changed), symbol)
    with pytest.raises(AssertionError):
        verify_indexed_byte(data, SymbolKey("7mfk", "ram", ADDRESS + 1))
