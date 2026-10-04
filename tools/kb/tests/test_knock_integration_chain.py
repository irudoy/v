"""Bind signed knock integration to separate bounded arithmetic entries."""

import builtins
from collections import Counter
import hashlib
import importlib.util
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-integration'
SOURCE = 'stock_jk08a_knock_integration.s'
HARNESS = 'harness-stock-jk08a-knock-integration.c'
HEADER = 'stock-jk08a-knock-integration-cases.h'
SPEC = 'defs/JK08A.ignition-state.md'
THIS_TEST = 'tools/kb/tests/test_knock_integration_chain.py'
OWNER_TEST = 'test_knock_integration_chain_owner_contract'
STOCK_TEST = 'test_knock_integration_registered_stock_contract'
FUNCTION = SymbolKey('7mfk', 'fn', 0x493e8)
STATE = SymbolKey('7mfk', 'ram', 0xffff1258)
OUTPUT = SymbolKey('7mfk', 'ram', 0xffff1380)
COUNT = SymbolKey('7mfk', 'ram', 0xffff2142)
EVENT_NOTE = (
    'n = uint8(x); ffff1380 = '
    'max(-32768,min(32767,int16(ffff1258)-ROM16[0x00008eae]*n)); ffff2142 = 0'
)
QUIET_NOTE = (
    'ffff1380 = max(-32768,min(32767,int16(ffff1258)+ROM16[0x00008eaa])); '
    'ffff2142 = 0'
)
CODE_SPANS = ((0x4956a, 0x49582), (0x49544, 0x49568), (0x49900, 0x49912))
POOLS = ((0x8eaa, 2), (0x8eae, 2), (0x49668, 4), (0x49678, 4),
         (0x4968c, 4), (0x49690, 4), (0x49694, 4), (0x49698, 4),
         (0x49938, 4), (0x4995c, 4))
RAM_LITERALS = (0x49668, 0x49678, 0x4968c, 0x49690, 0x49938)
SPANS = (
    (0x4956a, 0x49582, 'ecfe544ab4e9ce3eda3c7f678e1346dc20c34fe85f7e429ee7127abe504947b1'),
    (0x49544, 0x49568, '4a8efb0d3f153a6585830f5ca592a4f1a7f508b1414a3ba52b29b4ec77a13143'),
    (0x49900, 0x49912, 'f9961aafde1872f606b9dbd437f85e2d6d41b2dbf42b817b1888c072e505f048'),
    (0x8eaa, 0x8eac, 'a1f386a0ecb061b3c46a038616212779858ba7258b2eccb818a64986c97282da'),
    (0x8eae, 0x8eb0, '4efb97e7cc4520b9d437ce251ecdd94e243437933cdfa44ec76ec52e5a9a9b04'),
    (0x49668, 0x4966c, '69d759635c10d644ac4bf1593ca54bcca11be228e56c97a48e8e7f0ecbb23a08'),
    (0x49678, 0x4967c, '4f7e96f2f3d19407e474f2d34b2db605ff768abffb7f78d34e14dae07a06b8b1'),
    (0x4968c, 0x49690, '5e786f8c50352578ffd902c835ec360fcf23e7ee8fdb041717dd370be8b25cad'),
    (0x49690, 0x49694, 'cec236a342262bbc5156539981a6ecd5056a5aa425be5cb55434dcc6699e14ab'),
    (0x49694, 0x49698, '7f53b134f7a915e64f0293f1c69650bd4cd92e440be5a7af3e45c9a0d8ce06fc'),
    (0x49698, 0x4969c, 'e6475e4389df8f735541a94a395c6c4eb59274084333f01ebb865abcdb563f04'),
    (0x49938, 0x4993c, 'cec236a342262bbc5156539981a6ecd5056a5aa425be5cb55434dcc6699e14ab'),
    (0x4995c, 0x49960, '5640aaaa0ef732d2222997a7642b2afb211a9a87f549ac2a789193fd092e0724'),
)
STATE_BOUNDARIES = (-32768, -32767, -257, -256, -255, -1, 0, 1,
                    255, 256, 257, 32766, 32767)


def _verifier():
    name = 'knock_integration_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    regions = [item for item in _verifier().REGIONS if item.key == KEY]
    assert len(regions) == 1, 'The bounded integration Region must be registered exactly once'
    return regions[0]


def _text(value):
    return ' '.join(value.split()) if isinstance(value, str) else ' '.join(value)


def _link(owner, kind, target):
    [link] = [item for item in owner.links if item.type == kind and item.to.key == target
              and item.slot is None]
    return link


def _proof(link):
    assert link.stated == {'7mfk'} and FUNCTION in link.props['via']
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _notes():
    steps = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[8:10]
    for step, expected in zip(steps, (EVENT_NOTE, QUIET_NOTE)):
        assert Grammar(repo.config()).validate(step['note']) is None
        assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', expected)
    return [step['note'] for step in steps]


def _rows(header):
    [body] = re.findall(r'\bintegration_cases\[\]\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+)\},', line)
        assert match is not None, 'Every integration expectation is an explicit literal tuple'
        fields = [item.strip() for item in match[1].split(',')]
        assert len(fields) == 8
        assert all(re.fullmatch(r'-?[0-9]+U?', field) for field in fields)
        rows.append(tuple(int(field.rstrip('U')) for field in fields))
    return rows


def _macro(header, name):
    [value] = re.findall(r'^#define '+name+r' ([0-9]+)U$', header, re.M)
    return int(value)


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    found = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:(?:stock|bound|literal)\s+)?'+noun+r'\b', section)]
    assert value in found, f'The bounded contract must publish {value} {noun}'


def verify_integration_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert (word(0x8eaa), word(0x8eae)) == (13, 307)
    for address in (0x49548, 0x49906):
        assert sh2.decode(word(address), address).access == sh2.Access(10, 12, 2, 'load')
    assert word(0x4954c) == 0x302c
    assert [word(a) for a in range(0x49908, 0x49912, 2)] == [
        0x0247, 0x021a, 0x3028, 0xae1f, 0x6403]
    assert not any(sh2.decode(word(a), a).value == ('extu', 8, 4)
                   for start, end in CODE_SPANS for a in range(start, end, 2))
    assert sh2.decode(word(0x4990e), 0x4990e).target == 0x49550
    assert [word(a) for a in (0x49550, 0x49552, 0x49554, 0x49556,
                             0x4955c, 0x4955e, 0x49560)] == [
        0xe280, 0x4218, 0x6227, 0x3427, 0xe280, 0x4218, 0x3423]
    assert sh2.decode(word(0x49562), 0x49562).target == 0x4956a
    assert sh2.decode(word(0x49564), 0x49564).target == 0x4956a
    assert word(0x49566) == 0x6243
    stores = [(a, insn.access.size) for start, end in CODE_SPANS
              for a in range(start, end, 2)
              if (insn := sh2.decode(word(a), a)).access is not None
              and insn.access.mode == 'store']
    assert stores == [(0x49570, 2), (0x49580, 1)]
    assert not any(sh2.decode(word(a), a).flow == 'call'
                   for start, end in CODE_SPANS for a in range(start, end, 2))
    assert word(0x49690, 4)+12 == word(0x49938, 4)+12 == STATE.address
    assert word(0x49678, 4)+0xf4 == OUTPUT.address
    assert word(0x4968c, 4)+0x14e == COUNT.address
    assert word(0x49694, 4) == 0x8eaa and word(0x4995c, 4) == 0x8eae
    assert word(0x49668, 4) == 0xffff119c and word(0x49698, 4) == 0x8292


def test_knock_integration_exact_stock_signed_arithmetic_and_publication():
    verify_integration_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 39
    assert sum(end-start for start, end, _ in SPANS) == 114


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_integration_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_integration_stock(data)


def test_knock_integration_static_count_dispatch_is_outside_envelope():
    data = derive.image_bytes(repo.layout('7mfk'))
    word = lambda address: int.from_bytes(data[address:address+2], 'big')
    assert not any(start <= 0x4952c < end for start, end in CODE_SPANS)
    assert sh2.decode(word(0x4952c), 0x4952c).access == sh2.Access(6, 0, 1, 'load', True)
    assert sh2.decode(word(0x4952e), 0x4952e).value == ('extu', 8, 4)


def test_knock_integration_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    _notes()
    for step, source, effect, sign in zip(chain.steps[8:10], (COUNT, STATE),
                                         ('integrates', 'adds'), ('negative', 'positive')):
        assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
            source, OUTPUT, effect, sign, [FUNCTION])
    for key, name, width, signed in ((STATE, 'thick-dalmatian/ram', 16, True),
                                     (OUTPUT, 'curious-mustang/ram', 16, True),
                                     (COUNT, 'knock_count/ram', 8, False)):
        symbol = model.symbols[key]
        assert symbol.meaning.key == name
        assert (symbol.value('width'), symbol.value('signed'), symbol.value('level')) == (
            width, signed, 'code')
    output, state, count = (model.meaning_of(key) for key in (OUTPUT, STATE, COUNT))
    for kind, target in (('input', state.key), ('input', count.key),
                         ('selector', 'knock_function/fn'), ('writer', 'knock_function/fn')):
        _proof(_link(output, kind, target))
    entry = _link(output, 'selector', 'knock_function/fn').props['note']
    for phrase in ('00049544', '00049900', 'alternative', 'not sequential', 'R4=0', 'dispatcher'):
        assert phrase.lower() in entry.lower()
    operand = _link(output, 'input', count.key).props['note']
    for phrase in ('x', 'incoming 32-bit R4', 'independent', 'does not read', '0004952c', '0004952e', 'outside'):
        assert phrase.lower() in operand.lower()
    for phrase in ('0..255', '32-bit', 'upper-word'):
        assert phrase in operand
    for owner in (state, count):
        reader = _link(owner, 'reader', 'knock_function/fn')
        _proof(reader)
        if owner is state:
            assert '00049548' in reader.props['note'] and '00049906' in reader.props['note']
        else:
            assert '0004952c' in reader.props['note'] and 'outside' in reader.props['note']
    for owner, address in ((output, '00049570'), (count, '00049580')):
        writer = _link(owner, 'writer', 'knock_function/fn')
        _proof(writer)
        assert address in writer.props['note']
        assert writer.props['reverse_relies'] == 'structure'


def _check_literal_arithmetic(header, notes, data):
    rows = _rows(header)
    assert len(rows) == _macro(header, 'KNOCK_INTEGRATION_CASE_COUNT') == 4035
    assert Counter(row[0] for row in rows) == {1: 3967, 0: 68}
    assert _macro(header, 'KNOCK_INTEGRATION_EVENT_CASES') == 3967
    assert _macro(header, 'KNOCK_INTEGRATION_QUIET_CASES') == 68
    event, quiet = rows[:3967], rows[3967:]
    assert all(row[0] == 1 and row[1] != row[2] for row in event)
    assert {row[1] for row in event} == set(range(256))
    for n in range(256):
        inputs = set(STATE_BOUNDARIES)
        edge = -32768+307*n
        inputs |= {s for s in (edge-1, edge, edge+1) if -32768 <= s <= 32767}
        assert [row[3] for row in event if row[1] == n] == sorted(inputs)
    assert [(row[3], row[2]) for row in quiet] == [
        (s, count) for s in sorted((*STATE_BOUNDARIES, 32753, 32754, 32755, 32756))
        for count in (0, 1, 254, 255)]
    assert all(row[0] == row[1] == 0 for row in quiet)
    assert all(row[4] == -32768 for row in event if row[1] >= 214)
    assert {row[3] for row in event if row[1] == 213} >= {32622, 32623, 32624}
    assert {row[6] for row in event} == {0, 1} and {row[6] for row in quiet} == {1}
    codes = [builtins.compile(note, '<canonical signed integration arithmetic>', 'exec') for note in notes]

    def signed_word(value):
        return int.from_bytes((value & 65535).to_bytes(2, 'big'), 'big', signed=True)

    words = {address: int.from_bytes(data[address:address+2], 'big')
             for address in (0x8eaa, 0x8eae)}
    for event, n, ram_count, state, expected, r4, t, product in rows:
        values = {'ffff1258': state & 65535, 'ffff2142': ram_count,
                  'x': n, 'ROM16': words, 'min': min, 'max': max,
                  'int16': signed_word, 'uint8': lambda value: value & 255}
        exec(codes[0 if event else 1], {'__builtins__': {}}, values)
        assert (values['ffff1380'], values['ffff2142']) == (expected, 0)
        arithmetic = state-307*n if event else state+13
        assert r4 == min(32767, arithmetic)
        assert t == (r4 >= -32768)
        assert product == (307*n if event else 0)
        assert -(1 << 31) <= arithmetic < 1 << 31


def test_knock_integration_arithmetic_matches_explicit_entry_literals():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    _check_literal_arithmetic(header, _notes(), derive.image_bytes(repo.layout('7mfk')))


def test_knock_integration_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_integration_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.boundary
    assert region.return_address_offset is None
    assert dict(region.constants) == {'QUIET_ENTRY': 0x49544, 'EVENT_ENTRY': 0x49900}
    symbols = {'STATE': 'thick-dalmatian/ram', 'OUTPUT': 'curious-mustang/ram',
               'COUNT': 'knock_count/ram'}
    assert dict(region.symbols) == symbols
    defines = module.harness_defines(region, data)
    assert (defines['STATE'], defines['OUTPUT'], defines['COUNT']) == (
        STATE.address, OUTPUT.address, COUNT.address)
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    assert fixture[0x49582:0x49586] == bytes.fromhex('000b0009')
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    assert len(_rows(header)) == _macro(header, 'KNOCK_INTEGRATION_CASE_COUNT') == region.cases
    assert (instructions, bound, region.cases) == (39, 114, 4035)
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in symbols)
    assert 'ARRAY_SIZE(integration_cases)' in harness and '++completed;' in harness
    assert harness.count('++completed;') == 1
    assert 'completed != KNOCK_INTEGRATION_CASE_COUNT' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    assert ', REGION_KEY, completed);' in harness
    assert 'set_ram_word(STATE, (uint16_t)test->state);' in harness
    assert 'ram_word(OUTPUT) != (uint16_t)test->expected' in harness
    for phrase in ('context.r[4] = test->count', 'test->event ? EVENT_ENTRY : QUIET_ENTRY',
                   'explicit-event-entry', 'explicit-quiet-entry', 'i < 15U',
                   'test->r4', 'test->t', 'test->product : context.macl', '*ram(COUNT) != 0U',
                   'i < 65536U', 'calibration_before[36]', 'frame_before[52]',
                   'entire stack/local frame preservation', 'C caller ABI restoration',
                   '!preserve_inputs(scope, index)'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded knock integration'),
                        ('tools/sh-elf-run/README.md', 'Knock event integration')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        lower = section.lower()
        assert '3967' in section and '68' in section and 'R4' in section
        assert 'independent' in lower and 'dispatcher' in lower and 'outside' in lower
        assert 'quiet' in lower and 'event' in lower and 'count' in lower and 'clear' in lower
        assert 'MACL' in section and 'PR' in section and 'RAM' in section
