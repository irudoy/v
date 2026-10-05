"""Bind unsigned knock comparison metadata to its bounded stock execution."""

import builtins
from collections import Counter
import hashlib
import importlib.util
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from tools.kb.tests.stock_corruption import byte_span_ids, byte_span_samples
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-comparison'
SOURCE = 'stock_jk08a_knock_comparison.s'
HARNESS = 'harness-stock-jk08a-knock-comparison.c'
HEADER = 'stock-jk08a-knock-comparison-cases.h'
SPEC = 'defs/JK08A.knock-detection.md'
THIS_TEST = 'tools/kb/tests/test_knock_comparison_chain.py'
OWNER_TEST = 'test_knock_comparison_chain_owner_contract'
STOCK_TEST = 'test_knock_comparison_registered_stock_contract'
EVALUATOR = 'knock_slice_evaluator/fn'
FUNCTION = SymbolKey('7mfk', 'fn', 0x4a238)
CONTEXT = (
    'D = (ROM8[0x00008b3d]>>3)&1; '
    'c = (1-D)*uint8(ffff11de)+D*uint8(ffff2143); '
    'T = RAM16[0xffff2144+2*(c-1)]; '
    'M = RAM32[0xffff21d8+4*(c-1)]; '
    'E = min(1,max(0,uint32(M)-0x80000000-uint16(T))); '
    'C = uint8(ffff2142)'
)
THRESHOLD_NOTE = CONTEXT + '; ffff2142 = min(255,C+E)'
METRIC_NOTE = (
    CONTEXT + '; S = uint8(ffff24c2); B = uint8(ffff2150); H = 1<<(c-1); '
    'ffff2142 = min(255,C+E); ffff24c2 = (S&191)|(E<<6); '
    'ffff2150 = (B&uint8(~H))|(E*H)'
)
CODE_SPANS = (
    (0x4a2ee, 0x4a386), (0x49ffc, 0x4a04a),
    (0x264f8, 0x2651a), (0x26740, 0x2676e),
    (0x26984, 0x269c0), (0x26c78, 0x26d0e),
    (0x4a3fe, 0x4a438), (0x221bc, 0x221d6), (0x221e0, 0x221f8),
)
POOLS = (
    (0x8b3d, 1), (0x1108e, 194), (0x15340, 32), (0x2219c, 32),
    (0x221d8, 8), (0x2651c, 8), (0x269c0, 4), (0x4a1fc, 28),
    (0x4a4c8, 12), (0x4a4e4, 16),
)
RAM_LITERALS = (0x4a200, 0x4a208, 0x4a214, 0x4a4cc,
                0x4a4d0, 0x4a4e4, 0x4a4e8, 0x4a4ec)
SPANS = (
    (0x4a2ee, 0x4a386, 'f0a32820417a6689ce2a586d6dd8106d101a58208f0fdff22ca26881c97b041b'),
    (0x49ffc, 0x4a04a, 'e32b801d6090a980735d7fbc8767b3930b6ef69bcb0bdcd0e3187c661fed5225'),
    (0x264f8, 0x2651a, '447b6ff9e2250de46f0f19e880e6f6600b0da89b99ff5e85914495630fc7c5ce'),
    (0x26740, 0x2676e, 'e5ebb39cde98cd32ad8cbf753572029a70a828ea592d112b2d4d5cef40cd2cb0'),
    (0x26984, 0x269c0, 'ab62a51b7580cfa4bff1a671bb9db89aa74b5a51e133600f7fb351dfbe4275d7'),
    (0x26c78, 0x26d0e, 'd280566761efb42c1ca0d5f80c451d1de214aae45441e6bcd43f9d0f31fdbcb8'),
    (0x4a3fe, 0x4a438, '83757fbd2c2f49df374b32b8ff54a424fb125e05c9637345399ab429f7b630d9'),
    (0x221bc, 0x221d6, 'f26a9750e4b018c79ed192748c1ebd0272cf854a01bf7420e8e596c227301af4'),
    (0x221e0, 0x221f8, '9438c506bd58228afed5927502edc82fd5cccc7f392280c807d3b3ff210862b2'),
    (0x8b3d, 0x8b3e, 'a5ab782c805e8bfbe34cb65742a0471cf5a53a97f0a1160ab6cccbb64c9131ce'),
    (0x1108e, 0x11150, '60ab13e3cac1db35fa96de9a25117bdf991df195b25c32e539418e2d772a15cc'),
    (0x15340, 0x15360, 'a1f650f98972f766875ddb90d4b029ad494f786a0519c921d65af6b0b5f9e3de'),
    (0x2219c, 0x221bc, 'e671b7d1b66e94f2ef78699146d60090bf9d3eb63384581f94d45ebde9fe0308'),
    (0x221d8, 0x221e0, '2cb95ced1fb2078e86e257330635dabf123fdf0d5625d8f21acd56b7074d42b1'),
    (0x2651c, 0x26524, '02d1bb7547b0669b2e6fc808032aa70ab31869a3b3c1ac2be21538c024e8d244'),
    (0x269c0, 0x269c4, 'f48d18c3250763b996e2c2d4e34fec4761199c6d4cef0f0b18ae23f2aa0fa35c'),
    (0x4a1fc, 0x4a218, 'd2903e51955ccf1a9fbf6a3a6350c188eb868518005b750867d7be548c7a68ad'),
    (0x4a4c8, 0x4a4d4, '10bfc8e730d2c32c377700ada684ccfc5133e5b5e54cddf23122249fdbddfc66'),
    (0x4a4e4, 0x4a4f4, '8a4d7748f65358aa06bb99b3a4611d6bce6ac1b4ef2b61fad7e8fde17fbdeb67'),
)
OWNER_DEFINES = {
    'TABLE': ('amorphous-bird/tbl', 0x1108e),
    'AXIS': ('laughing-caterpillar/axis', 0x15340),
    'MODE': ('knock_selector_config/tbl', 0x8b3d),
    'PRIMARY': ('knock_channel_primary/ram', 0xffff11de),
    'ALTERNATE': ('knock_channel_alternate/ram', 0xffff2143),
    'SPEED': ('authentic-wasp/ram', 0xffff11f4),
    'THRESHOLDS': ('knock_threshold_base/ram', 0xffff2144),
    'METRICS': ('knock_metric_base/ram', 0xffff21d8),
    'COUNT': ('knock_count/ram', 0xffff2142),
    'STATUS': ('military-flamingo/ram', 0xffff24c2),
    'BITMAP': ('knock_mask/ram', 0xffff2150),
}


def _verifier():
    name = 'knock_comparison_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    regions = [item for item in _verifier().REGIONS if item.key == KEY]
    assert len(regions) == 1, 'The bounded comparison Region must be registered exactly once'
    return regions[0]


def _text(value):
    return ' '.join(value.split()) if isinstance(value, str) else ' '.join(value)


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links
              if item.type == kind and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'}
    assert FUNCTION in link.props['via']
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _notes():
    steps = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[6:8]
    for step, expected in zip(steps, (THRESHOLD_NOTE, METRIC_NOTE)):
        assert Grammar(repo.config()).validate(step['note']) is None
        assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', expected)
    return [step['note'] for step in steps]


def _rows(header, name, width):
    [body] = re.findall(r'\b'+name+r'\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+)\},', line)
        assert match is not None, 'Every comparison expectation must be an explicit literal row'
        fields = [item.strip() for item in match[1].split(',')]
        assert len(fields) == width
        values = []
        for field in fields:
            if field == '(-2147483647 - 1)':
                values.append(-2147483648)
            else:
                assert re.fullmatch(r'-?[0-9]+U?', field) is not None
                values.append(int(field.rstrip('U')))
        rows.append(tuple(values))
    return rows


def _bytes(header, name):
    [(size, body)] = re.findall(r'\b'+name+r'\[(\d+)\]\s*=\s*\{([^{}]*)\};', header, re.S)
    data = bytes(int(item, 16) for item in re.findall(r'0x([0-9a-fA-F]{2})U?', body))
    assert len(data) == int(size)
    return data


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    found = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:bound\s+)?'+noun+r'\b', section)]
    assert value in found, f'The bounded contract must publish {value} {noun}'


def verify_comparison_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert sh2.decode(word(0x4a2ee), 0x4a2ee).target == 0x49ffc
    assert word(0x4a2f0) == 0x0009
    assert sh2.decode(word(0x4a314), 0x4a314).access == sh2.Access(2, 0, 4, 'load', True)
    assert sh2.decode(word(0x4a31a), 0x4a31a).access == sh2.Access(5, 0, 2, 'load', True)
    assert [word(a) for a in range(0x4a31c, 0x4a328, 2)] == [
        0xe580, 0x4518, 0x622d, 0x4528, 0x325c, 0x3726]
    assert sh2.decode(word(0x4a328), 0x4a328).target == 0x4a410
    assert word(0x4a32e) == 0xc9bf and word(0x4a414) == 0xcb40
    for address in (0x4a330, 0x4a418):
        assert sh2.decode(word(address), address).access == sh2.Access(6, 2, 1, 'store')
    for call, delay in ((0x4a342, 0x4a344), (0x4a420, 0x4a422)):
        assert sh2.decode(word(call), call).flow == 'call'
        assert word(delay) == 0x6143
    assert sh2.decode(word(0x4a35e), 0x4a35e).target == 0x4a386
    assert [word(a) for a in (0x4a36c, 0x4a372, 0x4a374, 0x4a400)] == [
        0x655c, 0x7201, 0x3257, 0x6253]
    assert sh2.decode(word(0x4a384), 0x4a384).access == sh2.Access(3, 0, 1, 'store', True)
    assert word(0x4a4c8, 4) == 0x8b3d
    assert word(0x4a4cc, 4)+10 == OWNER_DEFINES['PRIMARY'][1]
    assert word(0x4a4d0, 4)+0x14f == OWNER_DEFINES['ALTERNATE'][1]
    assert word(0x4a4d0, 4)+0x14e == OWNER_DEFINES['COUNT'][1]
    assert word(0x4a4d0, 4)+0x15c == OWNER_DEFINES['BITMAP'][1]
    assert word(0x4a4e4, 4) == OWNER_DEFINES['METRICS'][1]
    assert word(0x4a4e8, 4) == OWNER_DEFINES['THRESHOLDS'][1]
    assert word(0x4a4ec, 4)+2 == OWNER_DEFINES['STATUS'][1]
    assert word(0x4a4f0, 4) == 0x221bc
    assert word(0x221d8, 4) == 0x221e6 and word(0x221dc, 4) == 0x2219c
    assert word(0x221f4) == 0x000b and word(0x221f6) == 0x62f6
    assert data[0x8b3d] == 0x82
    assert word(0x1114e) == 0


def test_knock_comparison_exact_stock_predicate_stores_and_helper():
    verify_comparison_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum(end-start for start, end, _ in SPANS) == 963
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 314


@pytest.mark.parametrize('address', byte_span_samples(SPANS), ids=byte_span_ids(SPANS))
def test_knock_comparison_static_corruption_is_rejected(address, jk08a_stock_bytes):
    data = bytearray(jk08a_stock_bytes)
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_comparison_stock(data)


def test_knock_comparison_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    owners = {meaning.key: meaning for meaning in model.meanings}
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    _notes()
    for step, source, sign in zip(chain.steps[6:8], (0xffff2144, 0xffff21d8), ('negative', 'positive')):
        assert (step['from'].address, step['to'], step['effect'], step['sign'], step['via']) == (
            source, SymbolKey('7mfk', 'ram', 0xffff2142), 'compares', sign, [FUNCTION])
    for address, name, width in ((0xffff21d8, 'knock_metric_base/ram', 32),
                                  (0xffff2142, 'knock_count/ram', 8),
                                  (0xffff24c2, 'military-flamingo/ram', 8),
                                  (0xffff2150, 'knock_mask/ram', 8)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.meaning.key == name
        assert symbol.value('width') == width and symbol.value('signed') is False
        assert symbol.value('level') == 'code'
    metric = owners['knock_metric_base/ram']
    reader = _link(metric, 'reader', EVALUATOR)
    _proof(reader)
    for phrase in ('0004a314', '4*(c-1)', 'offset-binary', 'explicit input', 'metric production'):
        assert phrase in reader.props['note']
    threshold = owners['knock_threshold_base/ram']
    reader = _link(threshold, 'reader', EVALUATOR)
    _proof(reader)
    assert reader.roles == {'indexed_by'}
    assert reader.props['reverse_relies'] == 'structure'
    for phrase in ('0004a31a', '00049ffc', 'R0 = 2*c', 'R2 = threshold', '0x80000000'):
        assert phrase in reader.props['note']
    for name in ('knock_count/ram', 'military-flamingo/ram', 'knock_mask/ram'):
        owner = owners[name]
        for source in ('knock_channel_primary/ram', 'knock_channel_alternate/ram', 'knock_metric_base/ram'):
            _proof(_link(owner, 'input', source))
        _proof(_link(owner, 'selector', 'knock_selector_config/tbl', 'bit3'))
        condition = _link(owner, 'threshold', 'knock_threshold_base/ram')
        _proof(condition)
        for phrase in ('uint32(M)', '0x80000000 + uint16(T)', 'strict', 'equality', 'natural accessor'):
            assert phrase.lower() in condition.props['note'].lower()
        writer = _link(owner, 'writer', EVALUATOR)
        _proof(writer)
        assert writer.props['reverse_relies'] == 'structure'
    count = owners['knock_count/ram']
    condition = _link(count, 'selector', 'military-flamingo/ram', 'bit6')
    _proof(condition)
    assert 'preserved' in condition.props['note'] and 'once' in condition.props['note']
    bitmap = owners['knock_mask/ram']
    shift = _link(bitmap, 'selector', 'copper-crayfish/fn')
    _proof(shift)
    for phrase in ('1 <= c <= 6', '0..5', '0004a342', '0004a420', '8..31', 'isolated'):
        assert phrase in shift.props['note']
    evaluator = owners[EVALUATOR]
    note = _text(evaluator.props['note'])
    assert 'raw threshold 65535' in note and '0x80010000' in note
    assert 'effectively prevents' not in note
    assert '802-byte' in note and 'reference learning' in note
    status = owners['military-flamingo/ram']
    assert '0x80000000' in _text(status.props['summary'])
    status_note = _text(model.symbols[SymbolKey('7mfk', 'ram', 0xffff24c2)].props['note'])
    assert 'bounded evaluator' in status_note and 'current result' in status_note
    assert 'without an interval-latched event claim' in status_note
    bitmap_note = _text(model.symbols[SymbolKey('7mfk', 'ram', 0xffff2150)].props['note'])
    assert 'Physical cylinder order and interval OR semantics are not established' in bitmap_note


def _check_literal_arithmetic(header, notes, data):
    rows = _rows(header, 'comparison_cases', 14)
    shifts = _rows(header, 'shift_cases', 3)
    assert (len(rows), len(shifts)) == (1048, 52)
    assert Counter(row[1] == 0x82 for row in rows) == {True: 469, False: 579}
    assert [row[1] for row in rows[-256:]] == list(range(256))
    assert {row[4] for row in rows} == {0, 254, 255}
    assert {row[2] if not row[1] & 8 else row[3] for row in rows} == set(range(1, 7))
    assert any(row[8] == 65535 and row[7] == 0x80010000 and row[12] == 64 for row in rows)
    assert any(row[7] == 0x80000000+row[8] and row[12] == 0 for row in rows)
    assert {row[7] for row in rows} >= {0, 0x7fffffff, 0x80000000, 0xffffffff}
    codes = [builtins.compile(note, '<canonical knock comparison arithmetic>', 'exec') for note in notes]
    # Both chain views evaluate one publication from the same pre-event context.
    for row in rows:
        speed, mode, primary, alternate, count, status, bitmap, metric, threshold, *out = row
        channel = alternate if mode & 8 else primary
        context = {'ffff11de': primary, 'ffff2143': alternate, 'ffff2142': count,
                   'ffff24c2': status, 'ffff2150': bitmap, 'ROM8': {0x8b3d: mode},
                   'RAM16': {0xffff2144+2*(channel-1): threshold},
                   'RAM32': {0xffff21d8+4*(channel-1): metric}, 'min': min, 'max': max,
                   'uint8': lambda value: value & 255, 'uint16': lambda value: value & 65535,
                   'uint32': lambda value: value & 0xffffffff}
        for code in codes:
            values = dict(context)
            exec(code, {'__builtins__': {}}, values)
            assert values['ffff2142'] == out[0]
            assert values['E'] * 64 == out[3]
            assert values['c'] == channel and 1 <= channel <= 6
            if 'H' in values:
                assert (values['ffff24c2'], values['ffff2150']) == tuple(out[1:3])
        i = min(15, max(0, speed//32-1))
        f = 0 if speed >= 512 or speed <= 32 else max(0, speed-32*(i+1))*2048
        at = 0x1108e+32*(channel-1)+2*i
        a, b = (int.from_bytes(data[p:p+2], 'big') for p in (at, at+2))
        assert a+(max(0, b-a)*f//65536)-(max(0, a-b)*f//65536) == threshold
    expected = [(value, shift, (value << shift) & 0xffffffff)
                for value in (0, 1, 0x80000000, 0xffffffff) for shift in range(8)]
    expected += [(value, shift, value if shift < 0 else 0)
                 for value in (0, 1, 0x80000000, 0xffffffff)
                 for shift in (-1, -2147483648, 32, 33, 2147483647)]
    assert shifts == expected
    assert not any(8 <= shift <= 31 for _, shift, _ in shifts)


def test_knock_comparison_arithmetic_matches_literal_contexts_and_shift_scope():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    _check_literal_arithmetic(header, _notes(), derive.image_bytes(repo.layout('7mfk')))


def test_knock_comparison_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_comparison_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS
    assert region.boundary and region.return_address_offset == 16 and region.return_register == 1
    assert dict(region.constants) == {'SHIFT_ENTRY': 0x221bc, 'JUMP_TABLE': 0x2219c}
    assert dict(region.symbols) == {name: item[0] for name, item in OWNER_DEFINES.items()}
    defines = module.harness_defines(region, data)
    assert {name: defines[name] for name in OWNER_DEFINES} == {
        name: item[1] for name, item in OWNER_DEFINES.items()}
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    assert fixture[0x4a386:0x4a38e] == bytes.fromhex('51f4412a000b0009')
    for start, size in POOLS:
        expected = bytearray(data[start:start+size])
        for address in RAM_LITERALS:
            if start <= address < start+size:
                value = int.from_bytes(data[address:address+4], 'big')
                expected[address-start:address-start+4] = module.base_verifier.alias_high_ram(value).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    for address in RAM_LITERALS:
        raw = int.from_bytes(data[address:address+4], 'big')
        assert int.from_bytes(fixture[address:address+4], 'big') == module.base_verifier.alias_high_ram(raw)
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    rows, shifts = _rows(header, 'comparison_cases', 14), _rows(header, 'shift_cases', 3)
    [count] = re.findall(r'^#define KNOCK_COMPARISON_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(rows)+len(shifts) == int(count) == region.cases
    assert (instructions, bound, region.cases) == (314, 963, 1100)
    for name, address, size in (('stock_table', 0x1108e, 194), ('stock_axis', 0x15340, 32),
                               ('stock_jump_table', 0x2219c, 32)):
        assert _bytes(header, name) == data[address:address+size]
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in OWNER_DEFINES)
    for name in ('comparisons', 'shifts'):
        assert '!run_'+name+'()' in harness
    assert 'ARRAY_SIZE(comparison_cases)' in harness and 'ARRAY_SIZE(shift_cases)' in harness
    assert harness.count('++completed;') == 2
    assert 'completed != KNOCK_COMPARISON_CASE_COUNT' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    assert ', REGION_KEY, completed);' in harness
    for phrase in ('stock-comparison', 'artificial-mode-comparison',
                   'frame_after[44] != test->local_flag', 'test->saved_tail_slot',
                   '!preserve_inputs(scope, i, output)', '!preserve_inputs("direct-shift", i, 0U)',
                   'i < 65536U', 'calibration_before[335]', 'frame_before[52]',
                   'comparison ? 13U : 14U', 'C caller ABI restoration', 'driver return continuation'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded comparison contract'),
                        ('tools/sh-elf-run/README.md', 'Knock threshold comparison')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        assert '1048' in section and '52' in section and 'artificial' in section.lower()
        assert '8..31' in section and 'outside' in section
        assert 'reference' in section.lower() and 'learning' in section.lower()
        assert 'channel' in section and 'guard' in section and '1..6' in section
        assert 'PR' in section and 'boundary' in section
