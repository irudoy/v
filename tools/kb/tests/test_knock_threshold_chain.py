"""Bind raw knock lookup arithmetic and owners to the registered stock slice."""

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


SELECT = (
    'D = (ROM8[0x00008b3d]>>3)&1; '
    'c = (1-D)*uint8(ffff11de)+D*uint8(ffff2143); '
    'row = 0x0001108e+32*(c-1); slot = 0xffff2144+2*(c-1)'
)
INDEX = (
    'x = uint16(ffff11f4); i = min(15,max(0,floor(x/32)-1)); '
    'f = min(1,max(0,512-x))*max(0,x-32*(i+1))*2048'
)
LOOKUP = (
    SELECT + '; ' + INDEX + '; '
    'a = ROM16[row+2*i]; b = ROM16[row+2*i+2]; '
    'to = a+floor(max(0,b-a)*f/65536)-floor(max(0,a-b)*f/65536)'
)
SPEC = 'defs/JK08A.knock-detection.md'
THIS_TEST = 'tools/kb/tests/test_knock_threshold_chain.py'
OWNER_TEST = 'test_knock_threshold_chain_owner_contract'
STOCK_TEST = 'test_knock_threshold_registered_stock_contract'
LOOKUP_FN = 'knock_slice_threshold_lookup/fn'
SPANS = (
    (0x49ffc, 0x4a04a, 'e32b801d6090a980735d7fbc8767b3930b6ef69bcb0bdcd0e3187c661fed5225'),
    (0x264f8, 0x2651a, '447b6ff9e2250de46f0f19e880e6f6600b0da89b99ff5e85914495630fc7c5ce'),
    (0x26740, 0x2676e, 'e5ebb39cde98cd32ad8cbf753572029a70a828ea592d112b2d4d5cef40cd2cb0'),
    (0x26984, 0x269c0, 'ab62a51b7580cfa4bff1a671bb9db89aa74b5a51e133600f7fb351dfbe4275d7'),
    (0x26c78, 0x26d0e, 'd280566761efb42c1ca0d5f80c451d1de214aae45441e6bcd43f9d0f31fdbcb8'),
    (0x4a1fc, 0x4a218, 'd2903e51955ccf1a9fbf6a3a6350c188eb868518005b750867d7be548c7a68ad'),
    (0x2651c, 0x26524, '02d1bb7547b0669b2e6fc808032aa70ab31869a3b3c1ac2be21538c024e8d244'),
    (0x269c0, 0x269c4, 'f48d18c3250763b996e2c2d4e34fec4761199c6d4cef0f0b18ae23f2aa0fa35c'),
    (0x8b3d, 0x8b3e, 'a5ab782c805e8bfbe34cb65742a0471cf5a53a97f0a1160ab6cccbb64c9131ce'),
    (0x1108e, 0x11150, '60ab13e3cac1db35fa96de9a25117bdf991df195b25c32e539418e2d772a15cc'),
    (0x15340, 0x15360, 'a1f650f98972f766875ddb90d4b029ad494f786a0519c921d65af6b0b5f9e3de'),
)


def _verifier():
    name = 'knock_threshold_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    return next(item for item in _verifier().REGIONS
                if item.key == 'jk08a-knock-threshold')


def _rows(text, name):
    [body] = re.findall(r'\b' + name + r'\[\]\s*=\s*\{(.*?)\n\};', text, re.S)
    return [tuple(int(item) for item in re.findall(r'\b(\d+)U\b', row))
            for row in re.findall(r'\{([^{}]+)\}', body)]


def _bytes(text, name):
    [(size, body)] = re.findall(r'\b' + name + r'\[(\d+)\]\s*=\s*\{(.*?)\n\};', text, re.S)
    data = bytes(int(item, 16) for item in re.findall(r'0x([0-9a-fA-F]{2})U?', body))
    assert len(data) == int(size)
    return data


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links
              if item.type == kind and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'}
    assert SymbolKey('7mfk', 'fn', 0x49ffc) in link.props['via']
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def verify_stock_lookup(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert word(0x4a1fc, 4) == 0x8b3d
    assert word(0x4a200, 4) + 0x14f == 0xffff2143
    assert word(0x4a204, 4) == 0x1108e
    assert word(0x4a208, 4) + 0xa == 0xffff11de
    assert word(0x4a208, 4) + 0x20 == 0xffff11f4
    assert word(0x4a20c, 4) == 0x15340
    assert word(0x4a210, 4) == 0x264f8
    assert word(0x4a214, 4) == 0xffff2144
    assert word(0x2651c, 4) == 0x26740 and word(0x26520, 4) == 0x26984
    assert word(0x269c0, 4) == 0x26c78
    assert data[0x8b3d] == 0x82
    assert [word(address) for address in range(0x15340, 0x15360, 2)] == list(range(32, 513, 32))
    assert word(0x1114e) == 0
    assert sh2.decode(word(0x2650a), 0x2650a).access == sh2.Access(6, 2, 2, 'load')
    assert sh2.decode(word(0x26510), 0x26510).access == sh2.Access(6, 0, 2, 'load')
    assert word(0x26740) == 0x3202 and word(0x26756) == 0x3208
    assert word(0x2676c) == 0x302c
    assert word(0x4a03a) == 0x0525


def test_knock_threshold_registered_stock_contract():
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_stock_lookup(data)
    module, region = _verifier(), _region()
    assert set(region.code_spans) | {(a, a+n) for a, n in region.pools} == {
        (a, b) for a, b, _ in SPANS}
    instructions = sum((b-a)//2 for a, b in region.code_spans)
    bound = sum(b-a for a, b, _ in SPANS)
    assert (instructions, bound, region.cases) == (184, 635, 829)
    assert not region.boundary and region.return_address_offset is None
    assert region.ram_literals == (0x4a200, 0x4a208, 0x4a214)
    fixture = module.build_fixture(region, data)
    for start, end in region.code_spans:
        assert fixture[start:end] == data[start:end]

    expected = {
        'TABLE': ('amorphous-bird/tbl', 0x1108e),
        'AXIS': ('laughing-caterpillar/axis', 0x15340),
        'MODE': ('knock_selector_config/tbl', 0x8b3d),
        'PRIMARY': ('knock_channel_primary/ram', 0xffff11de),
        'ALTERNATE': ('knock_channel_alternate/ram', 0xffff2143),
        'SPEED': ('authentic-wasp/ram', 0xffff11f4),
        'THRESHOLDS': ('knock_threshold_base/ram', 0xffff2144),
    }
    assert dict(region.symbols) == {key: item[0] for key, item in expected.items()}
    defines = module.harness_defines(region, data)
    assert {key: defines[key] for key in expected} == {key: item[1] for key, item in expected.items()}
    directory = repo.ROOT / 'tools/sh-elf-run'
    header = (directory / 'stock-jk08a-knock-threshold-cases.h').read_text()
    harness = (directory / region.harness).read_text()
    arrays = ('accessor', 'wrapper', 'axis', 'linear', 'divider')
    assert sum(len(_rows(header, name+'_cases')) for name in arrays) == region.cases
    assert f'#define KNOCK_CASE_COUNT {region.cases}U' in header
    assert _bytes(header, 'stock_table') == data[0x1108e:0x11150]
    assert _bytes(header, 'stock_axis') == data[0x15340:0x15360]
    runs = ('accessors', 'wrappers', 'axes', 'linear', 'dividers')
    for name, run in zip(arrays, runs):
        assert f'ARRAY_SIZE({name}_cases)' in harness
        assert f'!run_{run}()' in harness
    assert harness.count('++completed;') == len(arrays)
    assert 'if (completed != KNOCK_CASE_COUNT) return 1;' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    assert ', REGION_KEY, completed);' in harness
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in expected)
    for path, title in ((SPEC, 'Executable lookup contract'),
                        ('tools/sh-elf-run/README.md', 'Knock threshold lookup')):
        section = (repo.ROOT / path).read_text().split('## '+title+'\n', 1)[1].split('\n## ', 1)[0]
        section = ' '.join(section.split())
        assert f'{instructions} instructions' in section
        assert f'{bound} bytes' in section and f'{region.cases} cases' in section


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_threshold_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_stock_lookup(data)


def test_knock_threshold_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    for step, note, source, effect, sign in zip(
            chain.steps[3:6], (SELECT, INDEX, LOOKUP),
            (0xffff11de, 0xffff11f4, 0x1108e),
            ('selects', 'indexes', 'looks-up'), ('none', 'none', 'positive')):
        assert step['from'].address == source
        assert step['to'] == SymbolKey('7mfk', 'ram', 0xffff2144)
        assert step['via'] == [SymbolKey('7mfk', 'fn', 0x49ffc)]
        assert (step['effect'], step['sign']) == (effect, sign)
        assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', note)
        assert Grammar(repo.config()).validate(step['note']) is None
    threshold = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff2144))
    selector = _link(threshold, 'selector', 'knock_selector_config/tbl', 'bit3')
    _proof(selector)
    for phrase in ('bit 3 clear', 'bit 3 set', '0x82', 'artificial'):
        assert phrase in selector.props['note']
    for source in ('knock_channel_primary/ram', 'knock_channel_alternate/ram',
                   'authentic-wasp/ram', 'amorphous-bird/tbl', 'laughing-caterpillar/axis'):
        _proof(_link(threshold, 'input', source))
    writer = _link(threshold, 'writer', LOOKUP_FN)
    _proof(writer)
    for phrase in ('1 <= c <= 6', 'no channel guard', 'slot', 'to',
                   'ffff2144 + 2*(c-1)', 'siblings', '0004a03a'):
        assert phrase in writer.props['note']
    for address, width in ((0xffff11de, 8), (0xffff2143, 8),
                           (0xffff11f4, 16), (0xffff2144, 16)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is False
        assert symbol.value('level') == 'code'
    axis = model.symbols[SymbolKey('7mfk', 'axis', 0x15340)]
    assert (axis.value('storage'), axis.value('points'), axis.value('level')) == ('uint16', 16, 'code')
    axis_note = ' '.join(axis.props['note'])
    assert 'JK08A' in axis_note and '32..512' in axis_note
    mode = model.symbols[SymbolKey('7mfk', 'tbl', 0x8b3d)]
    assert (mode.value('storage'), mode.value('cols'), mode.value('rows')) == ('uint8', 1, 1)
    assert mode.value('level') == 'code'
    table = model.meaning_of(SymbolKey('7mfk', 'tbl', 0x1108e))
    _proof(_link(table, 'axis', axis.meaning.key))
    assert table.props['scale_level'] == 'candidate'
    assert table.props['scale'] == 'x*0.0015259'
    note = ' '.join(table.props['note'])
    assert 'raw threshold 65535' in note
    assert 'practically impossible' not in note
    reader = _link(table, 'reader', LOOKUP_FN)
    _proof(reader)
    for phrase in ('0001114e', 'zero fraction', 'positive decrement', '00026740'):
        assert phrase in reader.props['note']


def test_knock_threshold_arithmetic_matches_literal_stock_and_mode_contexts():
    model = compile.cached(repo.ROOT)
    [note] = [step['note'] for step in model.entities[('chain', 'knock_retard')].steps[5:6]]
    assert Grammar(repo.config()).validate(note) is None
    assert re.sub(r'\s+', '', note) == re.sub(r'\s+', '', LOOKUP)
    code = builtins.compile(note, '<knock lookup arithmetic>', 'exec')
    data = derive.image_bytes(repo.layout('7mfk'))
    header = (repo.ROOT / 'tools/sh-elf-run/stock-jk08a-knock-threshold-cases.h').read_text()

    class Words:
        def __getitem__(self, address):
            return int.from_bytes(data[address:address+2], 'big')

    rows = _rows(header, 'accessor_cases')
    assert len(rows) == 408 + 256
    assert {row[1] for row in rows[:408]} == {0x82}
    assert [row[1] for row in rows[408:]] == list(range(256))
    assert all(row[5] == (row[1] != 0x82) for row in rows)
    for speed, mode, primary, alternate, expected, _ in rows:
        values = {'ffff11f4': speed, 'ffff11de': primary, 'ffff2143': alternate,
                  'ROM8': {0x8b3d: mode}, 'ROM16': Words(), 'min': min, 'max': max,
                  'uint8': lambda value: value & 255,
                  'uint16': lambda value: value & 65535, 'floor': math.floor}
        exec(code, {'__builtins__': {}}, values)
        assert values['to'] == expected
        assert 1 <= values['c'] <= 6
        assert 0 <= values['f'] < 65536
        assert values['slot'] == 0xffff2144+2*(values['c']-1)
        if speed >= 512 or speed <= 32:
            assert values['f'] == 0
