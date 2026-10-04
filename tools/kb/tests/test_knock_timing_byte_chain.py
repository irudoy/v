"""Bind signed timing-byte metadata to the bounded registered stock conversion."""

import builtins
import hashlib
import importlib.util
import math
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-timing-byte'
SOURCE = 'stock_jk08a_knock_timing_byte.s'
HARNESS = 'harness-stock-jk08a-knock-timing-byte.c'
HEADER = 'stock-jk08a-knock-timing-byte-cases.h'
SPEC = 'defs/JK08A.ignition-state.md'
THIS_TEST = 'tools/kb/tests/test_knock_timing_byte_chain.py'
OWNER_TEST = 'test_knock_timing_byte_chain_owner_contract'
STOCK_TEST = 'test_knock_timing_byte_registered_stock_contract'
FORMULA = 'ffff22fa = trunc0(int16(ffff121a)/256)'
FUNCTION = SymbolKey('7mfk', 'fn', 0x493e8)
WORD = SymbolKey('7mfk', 'ram', 0xffff121a)
BYTE = SymbolKey('7mfk', 'ram', 0xffff22fa)
CODE_SPANS = ((0x496cc, 0x496da), (0x4964a, 0x4965c))
POOLS = ((0x495da, 2), (0x496ac, 4), (0x496c8, 4),
         (0x499ae, 2), (0x49b38, 4))
SPANS = (
    (0x4964a, 0x4965c, '6c921f40efea9b8a41f21a343f443b12cbc0769b4985ce1d6451541ddc4b1b05'),
    (0x496cc, 0x496da, '77ceff8406269f87df5a9ff97c74664755ba94c857ce225eb24bb370c242f9cc'),
    (0x495da, 0x495dc, '4751ec2f62d6c6007f1741f49c1e2b073ef2ac41d2c1ff3450cecab5ff9f27c1'),
    (0x496ac, 0x496b0, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
    (0x496c8, 0x496cc, 'b6ea3f1e90b525ff4bc3da46a8fb5d52ffe8605e1d80dcbc6e7976c14b81dce3'),
    (0x499ae, 0x499b0, '6199087871afe79e02b3bdab658497ed97d9e1c768f966f734e3f55b32d1b9e7'),
    (0x49b38, 0x49b3c, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
)
SIGNED_BOUNDARIES = (
    (-32768, -128), (-32767, -127), (-258, -1), (-257, -1),
    (-256, -1), (-255, 0), (-254, 0), (-2, 0), (-1, 0),
    (0, 0), (1, 0), (2, 0), (254, 0), (255, 0),
    (256, 1), (257, 1), (258, 1), (32766, 127), (32767, 127),
)
UPPER_WORDS = (0x0000, 0x0001, 0x7fff, 0x8000, 0xffff, 0x5a5a)


def _verifier():
    name = 'knock_timing_byte_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    regions = [region for region in _verifier().REGIONS if region.key == KEY]
    assert len(regions) == 1, 'The bounded timing-byte Region must be registered exactly once'
    return regions[0]


def _text(value):
    return ' '.join(value.split()) if isinstance(value, str) else ' '.join(value)


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links
              if item.type == kind and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'}
    assert link.props['via'] == [FUNCTION]
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _note():
    step = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[13]
    assert Grammar(repo.config()).validate(step['note']) is None
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    return step['note']


def _literal_rows(header):
    [body] = re.findall(r'\bliteral_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{0x([0-9a-f]{8})U, (-?[0-9]+), (-?[0-9]+)\},', line)
        assert match is not None, 'Each timing literal is an explicit raw/signed/result tuple'
        rows.append((int(match[1], 16), int(match[2]), int(match[3])))
    return rows


def _expected_literals():
    return [(upper << 16 | (signed & 65535), signed, quotient)
            for signed, quotient in SIGNED_BOUNDARIES for upper in UPPER_WORDS]


def _macro(text, name):
    [value] = re.findall(r'^#define\s+' + name + r'\s+([0-9]+)U$', text, re.M)
    return int(value)


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    found = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:(?:stock|bound)\s+)?'+noun+r'\b', section)]
    assert value in found, f'The bounded contract must publish {value} {noun}'


def verify_timing_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert word(0x4964a) == 0x6c2f  # EXTS.W R2,R12 binds the shared low word.
    assert word(0x4964e) == 0x6023 and word(0x49650) == 0x62cf
    assert word(0x49652) == 0x4211 and word(0x49654) == 0x8d3c
    assert 0x49654 + 4 + (word(0x49654) & 255)*2 == 0x496d0
    assert word(0x49658) == 0xa038 and word(0x4965a) == 0xe6ff
    assert 0x49658 + 4 + (word(0x49658) & 4095)*2 == 0x496cc
    assert sh2.decode(word(0x49656), 0x49656).access == sh2.Access(8, 12, 2, 'store')
    assert sh2.decode(word(0x496d8), 0x496d8).access == sh2.Access(9, 2, 1, 'store')
    stores = [(address, access) for start, end in CODE_SPANS
              for address in range(start, end, 2)
              if (access := sh2.decode(word(address), address).access) is not None
              and access.mode == 'store']
    assert [address for address, _ in stores] == [0x496d8, 0x49656]
    assert [word(address) for address in range(0x496cc, 0x496da, 2)] == [
        0x666c, 0x326c, 0x4219, 0x6029, 0x660e, 0x206d, 0x8092]
    for address, register, pool in ((0x4964c, 8, 0x496c8),
                                    (0x495da, 9, 0x496ac),
                                    (0x499ae, 9, 0x49b38)):
        opcode = word(address)
        assert opcode & 0xff00 == 0xd000 | register << 8
        assert (address & ~3) + 4 + (opcode & 255)*4 == pool
    assert word(0x496c8, 4) + 12 == WORD.address
    assert word(0x496ac, 4) == word(0x49b38, 4) == BYTE.address - 2


def test_knock_timing_byte_exact_stock_conversion_and_context_anchors():
    verify_timing_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum(end-start for start, end, _ in SPANS) == 48
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 16


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_timing_byte_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_timing_stock(data)


def test_knock_timing_byte_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    step = chain.steps[13]
    assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
        WORD, BYTE, 'scales', 'positive', [FUNCTION])
    _note()
    word, byte = model.meaning_of(WORD), model.meaning_of(BYTE)
    assert word.key == 'knock_timing_state/ram' and byte.key == 'steady-lionfish/ram'
    for key, width in ((WORD, 16), (BYTE, 8)):
        symbol = model.symbols[key]
        assert symbol.value('width') == width and symbol.value('signed') is True
        assert symbol.value('level') == 'code'
    assert model.symbols[WORD].value('scale') == 'x/256'
    assert {item.to.key for item in word.links if item.type == 'input'} >= {
        'curious-mustang/ram', 'glorious-spider/ram', 'masked-inchworm/ram'}
    assert {item.to.key for item in byte.links if item.type == 'lookup'} >= {
        'high_detonation_timing_state/tbl', 'high_octane_timing_state/tbl'}
    word_writer = _link(word, 'writer', 'knock_function/fn')
    byte_writer = _link(byte, 'writer', 'knock_function/fn')
    shared_input = _link(byte, 'input', word.key)
    sign = _link(byte, 'selector', word.key, 'bit15')
    for link in (word_writer, byte_writer, shared_input, sign):
        _proof(link)
    for phrase in ('independent raw R2', '00049656', 'both sign branches'):
        assert phrase in word_writer.props['note']
    for phrase in ('255', 'nonnegative', '000496d8', 'anchored incoming base'):
        assert phrase in byte_writer.props['note']
    for phrase in ('independent incoming R2', '0004964a', 'does not load ffff121a back'):
        assert phrase in shared_input.props['note']
    for phrase in ('Bit 15 set', 'bit 15 clear', '00049652', 'without a RAM readback'):
        assert phrase in sign.props['note']
    for owner, target, offset, source in (
            (word, 'red-sidewinder/ram', 12, '000496c8'),
            (byte, 'hungry-sidewinder/ram', 2, '000496ac/00049b38')):
        base = _link(owner, 'base', target)
        _proof(base)
        assert base.offset == offset
        assert base.to.symbols['7mfk'].address + offset == owner.symbols['7mfk'].address
        assert source in base.props['note'] and 'without a numeric input' in base.props['note']
        assert 'array extent' in base.props['note']


def test_knock_timing_byte_literal_sign_and_truncation_contract():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    rows = _literal_rows(header)
    assert rows == _expected_literals()
    assert len(rows) == _macro(header, 'KNOCK_TIMING_BYTE_LITERAL_CASES') == 114
    note = _note()
    code = builtins.compile(note, '<canonical timing-byte arithmetic>', 'exec')

    def signed_word(value):
        return int.from_bytes((value & 65535).to_bytes(2, 'big'), 'big', signed=True)

    for raw, signed, expected in rows:
        values = {'ffff121a': raw, 'int16': signed_word, 'trunc0': math.trunc}
        assert signed_word(raw) == signed
        exec(code, {'__builtins__': {}}, values)
        assert values['ffff22fa'] == expected


def test_knock_timing_byte_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_timing_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == (0x496c8,)
    assert region.boundary and region.return_address_offset is None
    assert region.start == 0x496cc and region.end == 0x496da
    assert dict(region.constants)['CONVERSION_ENTRY'] == 0x4964a
    symbols = {'WORD_STATE': 'knock_timing_state/ram', 'BYTE_STATE': 'steady-lionfish/ram'}
    assert dict(region.symbols) == symbols
    defines = module.harness_defines(region, data)
    assert defines['WORD_STATE'] == WORD.address and defines['BYTE_STATE'] == BYTE.address
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    assert fixture[0x496da:0x496de] == bytes.fromhex('000b0009')
    assert int.from_bytes(fixture[0x496c8:0x496cc], 'big') == module.base_verifier.alias_high_ram(WORD.address-12)
    for start, size in POOLS:
        if start != 0x496c8:
            assert fixture[start:start+size] == data[start:start+size]
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header = (directory / HEADER).read_text()
    harness = (directory / HARNESS).read_text()
    sweep = _macro(header, 'KNOCK_TIMING_BYTE_SWEEP_CASES')
    literals = _literal_rows(header)
    assert literals == _expected_literals()
    assert sweep == 65536 and len(literals) == 19 * 6 == 114
    assert sweep + len(literals) == _macro(header, 'KNOCK_TIMING_BYTE_CASE_COUNT') == region.cases
    assert (instructions, bound, region.cases) == (16, 48, 65650)
    assert 'raw < KNOCK_TIMING_BYTE_SWEEP_CASES' in harness
    assert 'ARRAY_SIZE(literal_cases)' in harness
    assert 'int32_t quotient = value / 256;' in harness
    assert harness.count('++completed;') == 1
    assert '!run_literals() || !run_sweep()' in harness
    assert 'completed != KNOCK_TIMING_BYTE_CASE_COUNT' in harness
    marker = 'VQ_SH_ELF_STOCK_CODE status=PASS region='+KEY+' cases=%lu\\n'
    assert marker in harness and ', completed);' in harness
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in symbols)
    assert 'stock_invoke_knock_timing_byte(CONVERSION_ENTRY, &context, &out);' in harness
    assert 'context.r[2] = input;' in harness
    assert 'if (i == 12U) expected = (uint32_t)signed_word;' in harness
    assert 'if (!preserve_neighbors(scope, index)) return 0;' in harness
    assert 'if (!(raw & 255U)) seed_and_snapshot();' in harness
    assert '(raw & 255U) == 255U && !preserve_ram("sweep-block", raw)' in harness
    assert '!preserve_ram("literal-boundary", i)' in harness
    for path, title in ((SPEC, 'Bounded timing-byte conversion'),
                        ('tools/sh-elf-run/README.md', 'Knock timing-byte conversion')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        assert 'literal case' in section and '256-case' in section and 'block' in section
        assert 'compensating writes' in section
        assert 'full per-case RAM' in section and 'does not' in section
