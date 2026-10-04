"""Bind two-word event retard to its bounded signed-byte stock contract."""

import builtins
from collections import Counter
import importlib.util
import hashlib
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-event-retard'
SOURCE = 'stock_jk08a_knock_event_retard.s'
HARNESS = 'harness-stock-jk08a-knock-event-retard.c'
HEADER = 'stock-jk08a-knock-event-retard-cases.h'
SPEC = 'defs/JK08A.ignition-state.md'
THIS_TEST = 'tools/kb/tests/test_knock_event_retard_chain.py'
OWNER_TEST = 'test_knock_event_retard_chain_owner_contract'
STOCK_TEST = 'test_knock_event_retard_registered_stock_contract'
FUNCTION = SymbolKey('7mfk', 'fn', 0x4d99c)
BUILDER = 'event_timing_correction_builder/fn'
FORMULA = (
    'Q = min(1,((uint8(ffff24c5)>>5)&1)+((uint8(ffff24cb)>>2)&1)); '
    'G = (ROM8[0x00008710]>>5)&1; K = int8(ffff22fa); '
    'A = int8(ffff11f9); B = int8(ffff11fa); H = uint16(ffff23c2)>>8; '
    'ffff11d6 = (1-Q)*(-A)+Q*((1-G)*min(K,-A)+G*min(K-H,-B)); '
    'ffff11d8 = (1-G)*uint16(ffff11d8)+G*((1-Q)*(-B)+Q*min(K,-B))'
)
CODE_SPANS = ((0x4d9ac, 0x4da2a),)
POOLS = ((0x8710, 1), (0x4dba4, 4), (0x4dba8, 4),
         (0x4dbac, 4), (0x4dbb0, 4), (0x4dbb4, 4))
RAM_LITERALS = (0x4dba8, 0x4dbac, 0x4dbb0, 0x4dbb4)
SPANS = (
    (0x4d9ac, 0x4da2a, 'ebabd1f7ee0ad5db05b856a7a22d5fe8b45f1a27262a6349690c59dbfccf7ff8'),
    (0x8710, 0x8711, 'cbe5cfdf7c2118a9c3d78ef1d684f3afa089201352886449a06a6511cfef74a7'),
    (0x4dba4, 0x4dba8, '5491350ca72b082a944de960a00a39722c59cab03bdb40bda760b8a4bdc33b1b'),
    (0x4dba8, 0x4dbac, '0ed2290b0380a864dd74110044de9f7744b9ce8c16edb586be0217c8254b4e3c'),
    (0x4dbac, 0x4dbb0, '9fb5dc466d8f9a48731e0b949648179140d08a44981958b15dcd437029e243e8'),
    (0x4dbb0, 0x4dbb4, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
    (0x4dbb4, 0x4dbb8, 'f255c3ddd26dfde9e1d8988839cd7a8c27e8f88bbcfa6ccc068b59d3ea4c7fd0'),
)
OWNER_DEFINES = {
    'FIRST': ('eccentric-badger/ram', 0xffff11d6),
    'SECOND': ('wooden-aardwolf/ram', 0xffff11d8),
    'KNOCK_BYTE': ('steady-lionfish/ram', 0xffff22fa),
    'REQUEST_A': ('hopeful-hedgehog/ram', 0xffff11f9),
    'REQUEST_B': ('aquamarine-leopard/ram', 0xffff11fa),
    'SOURCE_WORD': ('athletic-coucal/ram', 0xffff23c2),
    'FLAG5': ('utopian-grebe/ram', 0xffff24c5),
    'FLAGB': ('muscular-malamute/ram', 0xffff24cb),
    'MODE': ('event_retard_config/tbl', 0x8710),
}


def _verifier():
    name = 'knock_event_retard_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    regions = [item for item in _verifier().REGIONS if item.key == KEY]
    assert len(regions) == 1, 'The bounded two-word retard Region must be registered exactly once'
    return regions[0]


def _text(value):
    return ' '.join(value.split()) if isinstance(value, str) else ' '.join(value)


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links if item.type == kind
              and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'} and FUNCTION in link.props['via']
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _note():
    step = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[14]
    assert Grammar(repo.config()).validate(step['note']) is None
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    return step['note']


def _rows(header):
    [body] = re.findall(r'\bretard_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+)\},', line)
        assert match is not None, 'Every two-word expectation is an explicit literal tuple'
        fields = [item.strip() for item in match[1].split(',')]
        assert len(fields) == 16
        assert all(re.fullmatch(r'-?(?:0x[0-9a-f]{8}|[0-9]+)U?', field) for field in fields)
        rows.append(tuple(int(field.rstrip('U'), 0) for field in fields))
    return rows


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    found = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:(?:stock|bound|literal)\s+)?'+noun+r'\b', section)]
    assert value in found, f'The bounded contract must publish {value} {noun}'


def verify_event_retard_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert data[0x8710] == 0x7c
    assert (word(0x4dba4, 4), word(0x4dba8, 4)) == (0x8710, 0xffff24c0)
    assert word(0x4dbac, 4)+2 == OWNER_DEFINES['FIRST'][1]
    assert word(0x4dbac, 4)+4 == OWNER_DEFINES['SECOND'][1]
    assert word(0x4dbac, 4)+0x25 == OWNER_DEFINES['REQUEST_A'][1]
    assert word(0x4dbac, 4)+0x26 == OWNER_DEFINES['REQUEST_B'][1]
    assert word(0x4dbb0, 4)+2 == OWNER_DEFINES['KNOCK_BYTE'][1]
    assert word(0x4dbb4, 4)+6 == OWNER_DEFINES['SOURCE_WORD'][1]
    assert word(0x4dba8, 4)+5 == OWNER_DEFINES['FLAG5'][1]
    assert word(0x4dba8, 4)+11 == OWNER_DEFINES['FLAGB'][1]
    assert [word(a) for a in (0x4d9b2, 0x4d9b8, 0x4d9be)] == [0xc920, 0xc820, 0xc804]
    assert sh2.decode(word(0x4d9fa), 0x4d9fa).access == sh2.Access(6, 6, 2, 'load')
    assert [word(a) for a in (0x4d9fe, 0x4da02, 0x4da0c, 0x4da0e)] == [
        0x660d, 0x4619, 0x3268, 0x622f]
    assert word(0x4d9ca) == 0x605b and word(0x4d9d6) == 0x606b
    stores = [(a, insn.access) for a in range(0x4d9ac, 0x4da2a, 2)
              if (insn := sh2.decode(word(a), a)).access is not None
              and insn.access.mode == 'store']
    assert stores == [(a, sh2.Access(14, 2, 2, 'store'))
                      for a in (0x4d9ce, 0x4d9f4, 0x4da1e)] + [
                          (0x4da28, sh2.Access(14, 4, 2, 'store'))]
    for address in (0x4d9cc, 0x4d9f2, 0x4da1c, 0x4da20):
        assert sh2.decode(word(address), address).delayed
    assert [word(a) for a in (0x4da12, 0x4da18, 0x4da22, 0x4da24)] == [
        0x3267, 0x3567, 0x6263, 0x625e]
    for address in range(0x4d9ac, 0x4da2a, 2):
        insn = sh2.decode(word(address), address)
        assert insn.flow != 'call' and insn.gbr is None
        assert insn.access is None or insn.access.base != 15


def test_knock_event_retard_exact_stock_signed_requests_and_two_word_stores():
    verify_event_retard_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 63
    assert sum(end-start for start, end, _ in SPANS) == 147


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_event_retard_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_event_retard_stock(data)


def test_knock_event_retard_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    step = chain.steps[14]
    assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
        SymbolKey('7mfk', 'ram', 0xffff22fa), SymbolKey('7mfk', 'ram', 0xffff11d6),
        'adds', 'positive', [FUNCTION])
    _note()
    owners = {name: model.meaning_of(SymbolKey('7mfk', 'tbl' if name == 'MODE' else 'ram', at))
              for name, (_, at) in OWNER_DEFINES.items()}
    for definition, (name, _) in OWNER_DEFINES.items():
        assert owners[definition].key == name
    for name, width, signed in (('FIRST', 16, True), ('SECOND', 16, True),
                                ('KNOCK_BYTE', 8, True), ('REQUEST_A', 8, True),
                                ('REQUEST_B', 8, True), ('FLAG5', 8, False), ('FLAGB', 8, False)):
        symbol = owners[name].symbols['7mfk']
        assert (symbol.value('width'), symbol.value('signed'), symbol.value('level')) == (
            width, signed, 'code')
    assert owners['SOURCE_WORD'].symbols['7mfk'].value('width') == 16
    mode = owners['MODE'].symbols['7mfk']
    assert (mode.value('storage'), mode.value('rows'), mode.value('cols'), mode.value('level')) == (
        'uint8', 1, 1, 'code')
    assert mode.value('block') == 'ignition_timing/block'
    assert '0x7c' not in _text(owners['MODE'].props['summary']).lower()
    for definition in ('FIRST', 'SECOND'):
        owner = owners[definition]
        for selector, bit in (('FLAG5', 'bit5'), ('FLAGB', 'bit2'), ('MODE', 'bit5')):
            _proof(_link(owner, 'selector', owners[selector].key, bit))
        writer = _link(owner, 'writer', BUILDER)
        _proof(writer)
        assert writer.props['reverse_relies'] == 'structure'
    for source in ('KNOCK_BYTE', 'REQUEST_A', 'REQUEST_B', 'SOURCE_WORD'):
        _proof(_link(owners['FIRST'], 'input', owners[source].key))
    for source in ('KNOCK_BYTE', 'REQUEST_B'):
        _proof(_link(owners['SECOND'], 'input', owners[source].key))
    companion = _link(owners['SECOND'], 'writer', BUILDER).props['note'].lower()
    for phrase in ('g0', 'no store', 'prior', 'raw', 'g1', '0004da28'):
        assert phrase in companion
    high = _link(owners['SOURCE_WORD'], 'reader', BUILDER)
    _proof(high)
    assert high.roles == {'indexed_by'}
    for phrase in ('0004d9fa', '0004d9fe', '0004da02', 'unsigned high byte', 'low byte', 'producer signedness'):
        assert phrase in high.props['note'].lower()
    for definition in ('REQUEST_A', 'REQUEST_B', 'KNOCK_BYTE', 'FLAG5', 'FLAGB', 'MODE'):
        _proof(_link(owners[definition], 'reader', BUILDER))


def _check_literal_arithmetic(header, note):
    rows = _rows(header)
    [total] = re.findall(r'^#define KNOCK_EVENT_RETARD_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(rows) == int(total) == 7408
    assert Counter(row[0] == 0x7c for row in rows) == {True: 3605, False: 3803}
    assert {row[0] for row in rows} == set(range(256))
    assert Counter((int(bool(row[1]&32 or row[2]&4)), int(bool(row[0]&32))) for row in rows) == {
        (0, 0): 1772, (1, 0): 1904, (0, 1): 1772, (1, 1): 1960}
    assert {(bool(row[1]&32), bool(row[2]&4), bool(row[0]&32)) for row in rows} == {
        (a, b, g) for a in (False, True) for b in (False, True) for g in (False, True)}
    for index in (3, 4, 5):
        assert {row[index] for row in rows} >= {-128, -127, -1, 0, 1, 126, 127}
    assert {row[6]>>8 for row in rows} >= {0, 1, 127, 128, 255}
    assert {row[6]&255 for row in rows} >= {0, 1, 90, 127, 128, 165, 255}
    code = builtins.compile(note, '<canonical two-word event retard arithmetic>', 'exec')
    signed_byte = lambda value: int.from_bytes((value&255).to_bytes(1, 'big'), 'big', signed=True)
    retained = wrong_a = 0
    edges = [set(), set(), set()]
    for mode, flag5, flagb, k, a, b, high, old, first, second, *registers in rows:
        assert all(0 <= value <= 0xffffffff for value in registers[:5])
        assert registers[5] in (0, 1)
        values = {'ROM8': {0x8710: mode}, 'ffff24c5': flag5, 'ffff24cb': flagb,
                  'ffff22fa': k&255, 'ffff11f9': a&255, 'ffff11fa': b&255,
                  'ffff23c2': high, 'ffff11d8': old, 'min': min,
                  'uint8': lambda value: value&255, 'uint16': lambda value: value&65535,
                  'int8': signed_byte}
        exec(code, {'__builtins__': {}}, values)
        assert (values['ffff11d6'], values['ffff11d8']) == (first, second)
        assert -383 <= first <= 128
        q, g = values['Q'], values['G']
        if not g:
            assert second == old
            retained += 1
        else:
            assert -128 <= second <= 128
        if q:
            differences = (k+a,) if not g else (k-(high>>8)+b, k+b)
            for index, difference in enumerate(differences, 1 if g else 0):
                edges[index].add((difference > 0)-(difference < 0))
        if q and g and min(k-(high>>8), -a) != first:
            wrong_a += 1
    assert retained == 3676 and wrong_a == 528
    assert edges == [{-1, 0, 1}]*3


def test_knock_event_retard_arithmetic_matches_all_gate_and_retention_literals():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    _check_literal_arithmetic(header, _note())


def test_knock_event_retard_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_event_retard_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.boundary
    assert region.return_address_offset is None and not region.constants and not region.callees
    assert dict(region.symbols) == {name: item[0] for name, item in OWNER_DEFINES.items()}
    defines = module.harness_defines(region, data)
    assert {name: defines[name] for name in OWNER_DEFINES} == {
        name: item[1] for name, item in OWNER_DEFINES.items()}
    fixture = module.build_fixture(region, data)
    assert fixture[0x4d9ac:0x4da2a] == data[0x4d9ac:0x4da2a]
    assert fixture[0x4da2a:0x4da2e] == bytes.fromhex('000b0009')
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    [total] = re.findall(r'^#define KNOCK_EVENT_RETARD_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(_rows(header)) == int(total) == region.cases
    assert (instructions, bound, region.cases) == (63, 147, 7408)
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in OWNER_DEFINES)
    assert 'ARRAY_SIZE(retard_cases)' in harness and harness.count('++completed;') == 1
    assert 'completed != KNOCK_EVENT_RETARD_CASE_COUNT' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    assert ', REGION_KEY, completed);' in harness
    for phrase in ('stock-gate-context', 'artificial-gate-context',
                   'test->first', 'test->second', 'test->r0', 'test->r2', 'test->r4',
                   'test->r5', 'test->r6', 'test->t', 'i < 15U', 'i < 65536U',
                   '(gate && (i == (SECOND & 0xffffU)', 'test->mode & 32U',
                   'calibration_before[21]', 'frame_before[52]',
                   'entire stack/local frame preservation', 'C caller ABI restoration',
                   '!preserve_inputs(scope, index, test->mode & 32U)'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded knock event retard'),
                        ('tools/sh-elf-run/README.md', 'Knock event retard')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        lower = section.lower()
        assert '3605' in section and '3803' in section and '3676' in section
        assert 'artificial' in lower and 'unsigned high byte' in lower and 'signed byte' in lower
        assert 'prior' in lower and 'companion' in lower and 'retains' in lower
        assert 'boundary' in lower and 'latch' in lower and 'outside' in lower
        assert 'full' in lower and 'reachability' in lower and 'hardware' in lower
