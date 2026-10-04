"""Bind widened event-correction publication to explicit bounded R6 inputs."""

import builtins
import hashlib
import importlib.util
from itertools import product
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-event-publication'
SOURCE = 'stock_jk08a_knock_event_publication.s'
HARNESS = 'harness-stock-jk08a-knock-event-publication.c'
HEADER = 'stock-jk08a-knock-event-publication-cases.h'
SPEC = 'defs/JK08A.ignition-state.md'
THIS_TEST = 'tools/kb/tests/test_knock_event_publication_chain.py'
OWNER_TEST = 'test_knock_event_publication_chain_owner_contract'
STOCK_TEST = 'test_knock_event_publication_registered_stock_contract'
FUNCTION = SymbolKey('7mfk', 'fn', 0x4d99c)
BUILDER = 'event_timing_correction_builder/fn'
FORMULA = (
    'P = x; ffff1ff8 = int8(ffff2378)+int16(ffff11d6); '
    'ffff12d6 = max(-128,min(127,ffff1ff8+int8(ffff2356)-P))'
)
CODE_SPANS = ((0x4db86, 0x4db8e), (0x4db48, 0x4db74))
POOLS = ((0x4d9a8, 4), (0x4d9c2, 2), (0x4da7c, 2),
         (0x4dba0, 4), (0x4dbac, 4), (0x4dbbc, 4), (0x4dbe4, 4))
RAM_LITERALS = (0x4dba0, 0x4dbac, 0x4dbbc, 0x4dbe4)
SPANS = (
    (0x4db48, 0x4db74, '439a077d30a57cedd9a4cac659993c9d080ce49d4959df7d9bded9db22c646fc'),
    (0x4db86, 0x4db8e, 'de3f4bf38530b1ebd8ab1fb0d52ae9f95feb87a28460f13e9e27db9191ee0c85'),
    (0x4d9a8, 0x4d9ac, 'a28db7b829300d68f93d48bcdbaaecf43f13e8d239ed389207ffbbdce01900aa'),
    (0x4d9c2, 0x4d9c4, 'e5eb1d49ac05241a252537efd322e3c2416d2239e7721a8c1e78b7a72a99cbf3'),
    (0x4da7c, 0x4da7e, '7f011b58184f7734c61fbf2f5c863d9c7548a715977206f56f9b954b874cab8f'),
    (0x4dba0, 0x4dba4, '5e786f8c50352578ffd902c835ec360fcf23e7ee8fdb041717dd370be8b25cad'),
    (0x4dbac, 0x4dbb0, '9fb5dc466d8f9a48731e0b949648179140d08a44981958b15dcd437029e243e8'),
    (0x4dbbc, 0x4dbc0, '214cd838ba45440beac36849f9fd069e39df86c0cbeeffc2139f4f7e35498c08'),
    (0x4dbe4, 0x4dbe8, '4f7e96f2f3d19407e474f2d34b2db605ff768abffb7f78d34e14dae07a06b8b1'),
)
OWNER_DEFINES = {
    'RETARD': ('eccentric-badger/ram', 0xffff11d6),
    'SNAPSHOT': ('liberal-gorilla/ram', 0xffff2378),
    'CORRECTION': ('lumpy-kudu/ram', 0xffff2356),
    'SCALED_RAM': ('artichoke-capuchin/ram', 0xffff1ff6),
    'LONG_SUM': ('venomous-oyster/ram', 0xffff1ff8),
    'BYTE_OUTPUT': ('viridian-koel/ram', 0xffff12d6),
}
BYTES = (-128, -127, -1, 0, 1, 126, 127)
WORDS = (-32768, -32767, -383, -257, -256, -255, -129, -128, -127,
         -1, 0, 1, 127, 128, 129, 255, 256, 257, 32766, 32767)
P_VALUES = (0, 1, 127, 128, 255, 256, 65534, 65535)


def _verifier():
    name = 'knock_event_publication_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    [region] = [item for item in _verifier().REGIONS if item.key == KEY]
    return region


def _link(owner, kind, target):
    [link] = [item for item in owner.links if item.type == kind
              and item.to.key == target and item.slot is None]
    return link


def _proof(link):
    assert link.stated == {'7mfk'} and FUNCTION in link.props['via']
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _note():
    step = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[15]
    assert Grammar(repo.config()).validate(step['note']) is None
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    return step['note']


def _rows(header):
    [body] = re.findall(r'\bpublication_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+)\},', line)
        assert match is not None, 'Every widened-sum/clamp expectation is an explicit literal tuple'
        fields = [item.strip() for item in match[1].split(',')]
        assert len(fields) == 7 and all(re.fullmatch(r'-?[0-9]+U?', field) for field in fields)
        rows.append(tuple(int(field.rstrip('U')) for field in fields))
    return rows


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    found = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:(?:stock|bound|literal)\s+)?'+noun+r'\b', section)]
    assert value in found, f'The bounded contract must publish {value} {noun}'


def verify_event_publication_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert (word(0x4d9a8), word(0x4d9aa), word(0x4d9c2), word(0x4da7c)) == (
        0xd07d, 0x401e, 0xde7a, 0xdd4f)
    assert sh2.decode(word(0x4da7c), 0x4da7c).value == ('pool', 0x4dbbc, 4)
    assert word(0x4dba0, 4)+4 == OWNER_DEFINES['LONG_SUM'][1]
    assert word(0x4dbac, 4)+2 == OWNER_DEFINES['RETARD'][1]
    assert word(0x4dbbc, 4)+0x48 == OWNER_DEFINES['SNAPSHOT'][1]
    assert word(0x4dbbc, 4)+0x26 == OWNER_DEFINES['CORRECTION'][1]
    assert word(0x4dbe4, 4)+0x4a == OWNER_DEFINES['BYTE_OUTPUT'][1]
    assert sh2.decode(word(0x4db48), 0x4db48).access == sh2.Access(14, 2, 2, 'load')
    assert sh2.decode(word(0x4db4e), 0x4db4e).access == sh2.Access(13, 0, 1, 'load', True)
    assert sh2.decode(word(0x4db58), 0x4db58).access == sh2.Access(13, 0, 1, 'load', True)
    assert [word(a) for a in (0x4db4c, 0x4db56, 0x4db8a)] == [0xe048, 0xe026, 0xe04a]
    assert [word(a) for a in (0x4db50, 0x4db5a, 0x4db5c, 0x4db62, 0x4db6c)] == [
        0x324c, 0x325c, 0x3268, 0x3623, 0x3267]
    assert sh2.decode(word(0x4db64), 0x4db64).delayed
    assert sh2.decode(word(0x4db6e), 0x4db6e).target == 0x4db86
    assert sh2.decode(word(0x4db70), 0x4db70).target == 0x4db86
    stores = [(a, insn.access) for start, end in CODE_SPANS for a in range(start, end, 2)
              if (insn := sh2.decode(word(a), a)).access is not None
              and insn.access.mode == 'store']
    assert stores == [(0x4db8c, sh2.Access(2, 0, 1, 'store', True)),
                      (0x4db54, sh2.Access('gbr', 4, 4, 'store'))]
    for start, end in CODE_SPANS:
        for address in range(start, end, 2):
            insn = sh2.decode(word(address), address)
            assert insn.flow != 'call'
            assert insn.access is None or insn.access.base != 15


def test_knock_event_publication_exact_stock_widened_long_and_signed_byte():
    verify_event_publication_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 26
    assert sum(end-start for start, end, _ in SPANS) == 76


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_event_publication_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_event_publication_stock(data)


def test_knock_event_publication_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    step = chain.steps[15]
    assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
        SymbolKey('7mfk', 'ram', 0xffff11d6), SymbolKey('7mfk', 'ram', 0xffff12d6),
        'adds', 'positive', [FUNCTION])
    _note()
    owners = {name: model.meaning_of(SymbolKey('7mfk', 'ram', at))
              for name, (_, at) in OWNER_DEFINES.items()}
    for name, (key, _) in OWNER_DEFINES.items():
        assert owners[name].key == key
    for name, width in (('RETARD', 16), ('SNAPSHOT', 8), ('CORRECTION', 8),
                        ('LONG_SUM', 32), ('BYTE_OUTPUT', 8)):
        symbol = owners[name].symbols['7mfk']
        assert (symbol.value('width'), symbol.value('signed'), symbol.value('level')) == (
            width, True, 'code')
    for source in ('RETARD', 'SNAPSHOT'):
        _proof(_link(owners['LONG_SUM'], 'input', owners[source].key))
    for source in ('LONG_SUM', 'RETARD', 'SNAPSHOT', 'CORRECTION', 'SCALED_RAM'):
        _proof(_link(owners['BYTE_OUTPUT'], 'input', owners[source].key))
    for output in ('LONG_SUM', 'BYTE_OUTPUT'):
        _proof(_link(owners[output], 'writer', BUILDER))
        assert _link(owners[output], 'writer', BUILDER).props['reverse_relies'] == 'structure'
    for source in ('RETARD', 'SNAPSHOT', 'CORRECTION'):
        _proof(_link(owners[source], 'reader', BUILDER))
    context = _link(owners['BYTE_OUTPUT'], 'input', owners['SCALED_RAM'].key).props['note'].lower()
    for phrase in ('incoming r6', '0..65535', 'full register', 'independent',
                   'no ram', 'outside', '0004dad4'):
        assert phrase in context
    assert not any(link.type == 'reader' and link.to.key == BUILDER
                   for link in owners['SCALED_RAM'].links)
    widened = _link(owners['BYTE_OUTPUT'], 'input', owners['LONG_SUM'].key).props['note'].lower()
    for phrase in ('register', 'no ram readback', 'signed32', '0004db54'):
        assert phrase in widened
    assert _link(owners['SNAPSHOT'], 'reader', BUILDER).roles == {'indexed_by'}
    assert _link(owners['CORRECTION'], 'reader', BUILDER).roles == {'indexed_by'}
    base = _link(owners['LONG_SUM'], 'base', 'wandering-earthworm/ram')
    _proof(base)
    assert base.offset == 4
    for phrase in ('gbr', '0004d9a8', '0004d9aa', 'not executed', '0004db54'):
        assert phrase in base.props['note'].lower()


def _check_literal_arithmetic(header, note):
    rows = _rows(header)
    [count] = re.findall(r'^#define KNOCK_EVENT_PUBLICATION_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(rows) == int(count) == 8754
    assert [row[:4] for row in rows[:7840]] == list(product(BYTES, WORDS, BYTES, P_VALUES))
    assert len({row[:4] for row in rows}) == 8754
    assert len(rows[7840:]) == 914
    assert all(row[3] != 0x6d01 for row in rows)
    edges = {(s, w, c, p) for s, c, p in product(BYTES, BYTES, P_VALUES)
             for edge in (-129, -128, -127, 126, 127, 128)
             if -32768 <= (w := edge-s-c+p) <= 32767}
    assert len(edges) == 1764 and edges <= {row[:4] for row in rows}
    signed = lambda value, bits: int.from_bytes(
        (value&((1<<bits)-1)).to_bytes(bits//8, 'big'), 'big', signed=True)
    code = builtins.compile(note, '<canonical bounded event publication arithmetic>', 'exec')
    cross = set()
    for s, w, c, p, total, output, t in rows:
        assert -128 <= s <= 127 and -32768 <= w <= 32767 and -128 <= c <= 127
        assert 0 <= p <= 65535
        values = {'x': p, 'ffff2378': s&255, 'ffff11d6': w&65535,
                  'ffff2356': c&255, 'min': min, 'max': max,
                  'int8': lambda value: signed(value, 8),
                  'int16': lambda value: signed(value, 16)}
        exec(code, {'__builtins__': {}}, values)
        assert (values['ffff1ff8'], values['ffff12d6']) == (total, output)
        assert total == s+w and t == int(total+c-p > 127)
        cross.add((total < -32768, total > 32767))
    assert cross == {(True, False), (False, True), (False, False)}
    assert min(row[4] for row in rows) == -32896 and max(row[4] for row in rows) == 32894


def test_knock_event_publication_arithmetic_matches_widened_and_clamp_literals():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    _check_literal_arithmetic(header, _note())


def test_knock_event_publication_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_event_publication_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.boundary
    assert region.return_address_offset is None and dict(region.constants) == {'PUBLICATION_ENTRY': 0x4db48}
    assert dict(region.symbols) == {name: item[0] for name, item in OWNER_DEFINES.items()}
    defines = module.harness_defines(region, data)
    assert {name: defines[name] for name in OWNER_DEFINES} == {
        name: item[1] for name, item in OWNER_DEFINES.items()}
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    assert fixture[0x4db8e:0x4db92] == bytes.fromhex('000b0009')
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    [total] = re.findall(r'^#define KNOCK_EVENT_PUBLICATION_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(_rows(header)) == int(total) == region.cases
    assert (instructions, bound, region.cases) == (26, 76, 8754)
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in OWNER_DEFINES)
    assert 'ARRAY_SIZE(publication_cases)' in harness and harness.count('++completed;') == 1
    assert 'completed != KNOCK_EVENT_PUBLICATION_CASE_COUNT' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    assert ', REGION_KEY, completed);' in harness
    for phrase in ('test->sum', 'test->expected', 'test->t', 'context.r[6] = test->scaled',
                   'set_ram_word(SCALED_RAM, 0x6d01U)', 'i < 15U', 'i < 65536U',
                   '(LONG_SUM & 0xffffU) + 4U', 'i == (BYTE_OUTPUT & 0xffffU)',
                   'calibration_before[24]', 'frame_before[52]',
                   'entire stack/local frame preservation', 'C caller ABI restoration',
                   '!preserve_inputs(scope, index)'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded knock event publication'),
                        ('tools/sh-elf-run/README.md', 'Knock event correction publication')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        lower = section.lower()
        assert 'r6' in lower and '0..65535' in lower and 'independent' in lower
        assert 'widened' in lower and 'signed byte' in lower
        assert '0004da7c' in lower and 'not executed' in lower
        assert 'timer/latch' in lower and 'bypass' in lower and 'outside' in lower
        assert 'full' in lower and 'hardware' in lower
