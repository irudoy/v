"""Bind RAM-only reference learning to unsigned words and natural stock returns."""

import builtins
from collections import Counter
from dataclasses import replace
import hashlib
import importlib.util
import math
import re
import sys
from types import SimpleNamespace

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-reference-learning'
SOURCE = 'stock_jk08a_knock_reference_learning.s'
HARNESS = 'harness-stock-jk08a-knock-reference-learning.c'
HEADER = 'stock-jk08a-knock-reference-learning-cases.h'
SPEC = 'defs/JK08A.knock-detection.md'
THIS_TEST = 'tools/kb/tests/test_knock_reference_learning_chain.py'
OWNER_TEST = 'test_knock_reference_learning_chain_owner_contract'
STOCK_TEST = 'test_knock_reference_learning_registered_stock_contract'
SECTION = 'Bounded knock reference learning'
LEARNER = 'knock_reference_learning/fn'
PREDICATE = 'diagnostic_record_byte1_bit7_predicate/fn'
FUNCTION = SymbolKey('7mfk', 'fn', 0x4a118)
PREDICATE_FUNCTION = SymbolKey('7mfk', 'fn', 0x25e20)
FORMULA = (
    'D = (ROM8[0x00008b3d]>>3)&1; '
    'c = (1-D)*uint8(ffff11de)+D*uint8(ffff2143); i = x; '
    'row = 0xffff2178+16*(c-1); v = RAM16[0xffff20c2+2*i]; '
    'old = RAM16[row+2*i]; W = ROM8[0x0000884b]; '
    'q = floor((W*uint16(v)+(255-W)*uint16(old))/256); '
    'to = min(65535,q+min(1,max(0,uint16(old)-q)))'
)
RESET_FORMULA = 'to = ROM16[0x00009282]'
CODE_SPANS = ((0x4a118, 0x4a1fc), (0x25e20, 0x25e44))
POOLS = ((0x884b, 1), (0x8b3d, 1), (0x9282, 2), (0x25f10, 4),
         (0x4a1fc, 4), (0x4a200, 4), (0x4a208, 4), (0x4a224, 4),
         (0x4a228, 4), (0x4a22c, 4), (0x4a230, 4), (0x4a234, 4))
RAM_LITERALS = (0x25f10, 0x4a200, 0x4a208, 0x4a22c, 0x4a234)
SPANS = (
    (0x4a118, 0x4a1fc, '83fdb6599c62206c8a99f457e92e6ca1fff948d30eeaf322c4c7480644347bc9'),
    (0x25e20, 0x25e44, '4768088bf64e2c278a107a2a2030b4e47c2c380cf1c05dbb8f0468e8aeef4778'),
    (0x884b, 0x884c, '7d8c5da7fd418379048e430b33dc8ffcda739e44326b8a5d647dc0ad81ed2157'),
    (0x8b3d, 0x8b3e, 'a5ab782c805e8bfbe34cb65742a0471cf5a53a97f0a1160ab6cccbb64c9131ce'),
    (0x9282, 0x9284, 'ca2fd00fa001190744c15c317643ab092e7048ce086a243e2be9437c898de1bb'),
    (0x25f10, 0x25f14, '4b9e90bd8b8a501f4cace831f15ee6c421b3a92edcad3f7990ae6ed6ee7fe2f2'),
    (0x4a1fc, 0x4a200, 'fba538115eb72235f96fd00a75bb5a5e2d2378c7ae678ae4e78723aa30754438'),
    (0x4a200, 0x4a204, '5e786f8c50352578ffd902c835ec360fcf23e7ee8fdb041717dd370be8b25cad'),
    (0x4a208, 0x4a20c, '9fb5dc466d8f9a48731e0b949648179140d08a44981958b15dcd437029e243e8'),
    (0x4a224, 0x4a228, '9c66b87e86623017146f7d7dfdab9866991b4de7786cc99c3b031ac565982a14'),
    (0x4a228, 0x4a22c, '0a396a9a79110f0d78d50150bf99fa9e3389e9a654e66d12af3858f258ffc053'),
    (0x4a22c, 0x4a230, '046df2bd86bb9fe3cd30cfbc1d17c77df08ce48a13cfcbbf713212183d8a452e'),
    (0x4a230, 0x4a234, 'af21b8d1e50b8a793c0bd988c0c874ab72139c3d644b437cbf6218d926a4ceef'),
    (0x4a234, 0x4a238, 'c425cf5a9f5943423d6eb98b905ae54ad88e6ef9f598a3a65bc3cd40fa44997f'),
)
CALLER_SPANS = (
    (0x4a386, 0x4a38a, '761ffdb06b7426e728f09959c2366491dc9217ea45658fc5ecdae513cbaf3386'),
    (0x4a954, 0x4a95c, 'be38a9daa0ac8e5e88a3b4af93e2a0af7dd2d70dbac36b28bd4a8e3c7dccf475'),
    (0x4a9c0, 0x4a9c4, 'c016ec2580b56c42d45c3c9565cf6174d7b1c2075a8456d0b22890b399ace344'),
)
OWNER_DEFINES = {
    'REFERENCES': ('gigantic-goshawk/ram', 0xffff2178),
    'SAMPLES': ('knock_reference_samples/ram', 0xffff20c2),
    'PRIMARY': ('knock_channel_primary/ram', 0xffff11de),
    'ALTERNATE': ('knock_channel_alternate/ram', 0xffff2143),
    'DIAGNOSTICS': ('hallowed-malkoha/ram', 0xffff5718),
    'SELECTOR': ('knock_selector_config/tbl', 0x8b3d),
    'WEIGHT': ('knock_reference_weight/tbl', 0x884b),
    'RESET_WORD': ('knock_reference_reset/tbl', 0x9282),
}


LINK_CONTRACTS = (('gigantic-goshawk/ram',
  'input',
  'knock_reference_samples/ram',
  None,
  'Normal learning reads unsigned v=RAM16[ffff20c2+2*i] with i=x in 0..7. EXTU.W 0004a1c2 precedes '
  'multiplication. Both real diagnostic results must be clear; forced reset does not read the sample vector. '
  'Acquisition and digital-bin production are not executed by this CPU-only learner.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'input',
  'knock_reference_weight/tbl',
  None,
  'Normal learning uses byte W and coefficients W and 255-W. q=floor((W*v+(255-W)*old)/256); the conditional '
  '+1 is taken only if q<old. The declared uint16/byte domain has q<=65279 and result<=65280, so the final '
  'upper-clamp taken arm is unreachable. Artificial weights are labelled independently of stock bytes.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'input',
  'knock_reference_reset/tbl',
  None,
  'Either queried diagnostic result set selects forced full-bank reset: for every j in 0..47, to = '
  'ROM16[0x00009282]. All 48 raw words receive this value, not only the selected row. The normal path does '
  'not read this scalar. Artificial reset words are separate contexts.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'input',
  'knock_channel_primary/ram',
  None,
  'With selector bit3 clear, MOV.B 0004a17e supplies selected channel c, then normal learning constrains its '
  'zero-extended value to the declared legal domain 1..6. The other channel byte is independently different. '
  'The caller channel-zero guard and physical cylinder order are not executed or inferred here.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'input',
  'knock_channel_alternate/ram',
  None,
  'With selector bit3 set, MOV.B 0004a13a supplies selected channel c from ffff1ff4+0x14f. Normal learning '
  'uses declared legal c in 1..6. The other channel byte remains independently different; all selector-byte '
  'contexts preserve both inputs, without a channel-zero guard or physical ordering claim.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'selector',
  'knock_selector_config/tbl',
  'bit3',
  'ROM8[00008b3d].bit3 clear selects primary ffff11de; set selects alternate ffff2143. Legal channel c is '
  '1..6. Every unrelated selector bit is independently varied and preserved. The complete learner reads the '
  'scalar and channel bytes, without executing acquisition or its caller zero-guard.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'selector',
  'diagnostic_record_byte1_bit7_predicate/fn',
  None,
  'The real queries use ids 012d and 013f. Both clear selects normal eight-word learning; either byte1.bit7 '
  'set selects all 48 reference words for forced reset. If the first result is set the second query is '
  'skipped by the genuine code. This source/branch contract makes no direct call-count observation, '
  'diagnostic producer, acquisition or hardware claim.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'writer',
  'knock_reference_learning/fn',
  None,
  'With both diagnostic results clear, the arithmetic-only normal note applies to i=x in 0..7 and the '
  'selected row only, updating eight words/16 bytes. With either result set, the independent reset view for '
  'j in 0..47 is to = ROM16[0x00009282] and writes all 48 words/96 bytes. The maximum normal result is 65280 '
  'for the declared uint16/byte-weight domain; the upper-clamp taken arm is unreachable. All other 64k RAM, '
  'samples, channels, diagnostic records and calibration/pool bytes are preserved per case. Acquisition, the '
  'static caller and full evaluator dispatch are not executed.',
  {'relies': 'structure',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity',
   'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('gigantic-goshawk/ram',
  'reader',
  'knock_reference_learning/fn',
  None,
  'On normal learning, the loaded reference base and channel select eight old uint16 words; EXTU.W '
  'zero-extends each before the weighted multiply. Only the selected row is rewritten. Forced reset reads no '
  'old numeric reference value and copies all 48 reset words. Natural return and per-case sibling isolation '
  'are independently checked.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_reference_samples/ram',
  'reader',
  'knock_reference_learning/fn',
  None,
  'MOV.W 0004a1ba reads eight sample words at indices 0..7, and EXTU.W 0004a1c2 supplies uint16 values. The '
  'vector is preserved per case. Forced reset does not read it; prior ADC/DMAC and digital-bin production '
  'remain outside the learner.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_channel_primary/ram',
  'reader',
  'knock_reference_learning/fn',
  None,
  'Selector bit3 clear reads channel through ffff11d4+10. The normal eight-word row calculation has explicit '
  'legal c in 1..6; its caller guard and any physical cylinder mapping are separate, unexecuted facts.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_channel_alternate/ram',
  'reader',
  'knock_reference_learning/fn',
  None,
  'Selector bit3 set reads alternate channel through ffff1ff4+0x14f. The normal row calculation has explicit '
  'legal c in 1..6 and preserves the independently different unused channel byte.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_selector_config/tbl',
  'reader',
  'knock_reference_learning/fn',
  None,
  'MOV.B 0004a12c and TST bit3 choose the two declared channel-byte contexts. Every selector value is '
  'explicit; stock bytes and artificial calibration contexts do not establish full scheduler or hardware '
  'mode reachability.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_reference_weight/tbl',
  'reader',
  'knock_reference_learning/fn',
  None,
  'Normal learning reads this byte, zero-extends it and forms both W and 255-W. Forced reset does not read '
  'it. Generic shape and the executed byte domain are separate from stock or artificial weight values.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('knock_reference_reset/tbl',
  'reader',
  'knock_reference_learning/fn',
  None,
  'Forced reset reads and sign-extends this ROM word, then stores its unchanged low16 bits to every word of '
  'the six-row bank. Normal learning does not read it. Startup reader semantics and stock/artificial '
  'calibration contexts remain separate.',
  {'relies': 'structure', 'supports': 'identity'},
  (),
  'knock_reference_learning/fn'),
 ('hallowed-malkoha/ram',
  'reader',
  'diagnostic_record_byte1_bit7_predicate/fn',
  None,
  'The real predicate uses three-byte records, loads byte1 at 00025e32 and returns bit7. Bounded direct '
  'contexts use ids 012d/013f with independent upper-word R4 patterns; the low-word ffff sentinel makes no '
  'record read. Nonsentinel R6 addresses base+3*id while full R4 is preserved. These indexed reader claims '
  'establish no complete array extent, record producer or hardware meaning. The existing diagnostic record '
  'byte unit and both ledger claiming ends remain unchanged.',
  {'relies': 'structure',
   'reverse_relies': 'structure',
   'reverse_supports': ['contract', 'identity'],
   'supports': 'identity'},
  ('indexed_by',),
  'diagnostic_record_byte1_bit7_predicate/fn'),
 ('knock_reference_learning/fn',
  'depends',
  'knock_slice_evaluator/fn',
  None,
  'Static primary BSR 0004a386 and delay-slot NOP 0004a388 call this learner from the evaluator. The caller '
  'entry, its channel-zero guard, acquisition, preceding metric/threshold/count arithmetic and scheduler are '
  'not executed by the RAM-only learning fixture. The chain step therefore begins at the explicit RAM sample '
  'vector and names the learner only.',
  {'relies': 'structure', 'supports': 'identity'},
  ('consumer',),
  'knock_reference_learning/fn'))


def _verifier():
    name = 'knock_reference_learning_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    return _required_region(_verifier().REGIONS)


def _required_region(items):
    regions = [item for item in items if item.key == KEY]
    assert len(regions) == 1, 'The registered reference Region is mandatory and unique'
    [region] = regions
    return region


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links if item.type == kind and item.to.key == target and item.slot == slot]
    assert link.offset is None
    return link


def _proof(link, function=FUNCTION):
    assert link.stated == {'7mfk'} and link.props['via'] == [function]
    assert (link.props['relies'], link.props['supports']) == ('structure', 'identity')
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence if item['kind'] == 'test'}
    assert (SPEC, SECTION) in {(item.get('path'), item.get('key'))
                             for item in link.evidence if item['kind'] == 'spec'}
    [contract] = [item for item in LINK_CONTRACTS
                  if item[:4] == (link.owner.key, link.type, link.to.key, link.slot)]
    _check_link_contract(link, contract)


def _text(value):
    return ' '.join((value if isinstance(value, str) else ' '.join(value)).split())


def _check_link_contract(link, contract):
    owner, kind, target, slot, note, props, roles, function = contract
    assert (link.owner.key, link.type, link.to.key, link.slot) == (owner, kind, target, slot)
    assert link.offset is None
    assert link.stated == {'7mfk'}
    expected_function = PREDICATE_FUNCTION if function == PREDICATE else FUNCTION
    assert link.props['via'] == [expected_function]
    assert _text(link.props['note']) == _text(note)
    assert all(link.props.get(key) == value for key, value in props.items())
    assert set(roles) <= link.roles
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence if item['kind'] == 'test'}
    assert (SPEC, SECTION) in {(item.get('path'), item.get('key'))
                             for item in link.evidence if item['kind'] == 'spec'}


def _check_step(step):
    assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
        SymbolKey('7mfk', 'ram', 0xffff20c2), SymbolKey('7mfk', 'ram', 0xffff2178),
        'learns', 'none', [FUNCTION])
    assert Grammar(repo.config()).validate(step['note']) is None
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)


def _require_owner_integration(model):
    missing = sorted({LEARNER, PREDICATE, *(item[0] for item in OWNER_DEFINES.values())}
                     - {item.key for item in model.meanings})
    assert not missing, 'Mandatory native reference owners missing: ' + ', '.join(missing)


def _required_header(path):
    assert path.is_file(), 'The tracked reference literal header is mandatory'
    return path.read_text()


def _normal_note():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'knock_retard')].steps[1]
    _check_step(step)
    return step['note']


def _rows(header):
    [body] = re.findall(r'\breference_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+),\s*\{([^{}]+)\},\s*\{([^{}]+)\},\s*'
                             r'\{([^{}]+)\},\s*\{([^{}]+)\},\s*([^{}]+)\},', line)
        assert match is not None, 'Every weighted/predicate expectation is a complete literal vector'
        groups = [[value.strip() for value in group.split(',')] for group in match.groups()]
        assert [len(group) for group in groups] == [10, 8, 8, 8, 15, 1]
        assert all(re.fullmatch(r'(?:0x[0-9a-f]{8}|[0-9]+)U?', value) for group in groups for value in group)
        rows.append(tuple(tuple(int(value.rstrip('U'), 0) for value in group) for group in groups))
    return rows


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    labels = {'instructions': r'instructions?', 'bytes': r'bytes?',
              'cases': r'(?:cases?|times)'}
    found = []
    for match in re.finditer(r'\b([0-9][0-9,]*)\s*(?:-\s*)?'
                             r'((?:[a-z]+(?:-[a-z]+)?\s+){0,5})'+labels[noun]+r'\b',
                             section, re.I):
        descriptor = match[2].strip().lower()
        if noun == 'instructions' and re.match(r'\s+bytes?\b', section[match.end():], re.I):
            continue
        if noun == 'cases':
            category = _case_category(descriptor, section[match.end():])
            if category != 'total':
                continue
        if noun == 'bytes' and (descriptor in ('instruction', 'code', 'data', 'pool',
                'bound data', 'bound pool', 'calibration', 'bound calibration', 'record') or re.match(
                r'(?:(?:observed|stack|local|natural|saved|save|reference)\s+)*'
                r'(?:frame|footprint|row|bank|pool|calibration|RAM|output)\b',
                section[match.end():].lstrip(), re.I)):
            continue
        found.append(int(match[1].replace(',', '')))
    assert found and set(found) == {value}, f'Only {value} {noun} belongs to this envelope'


def _case_category(descriptor, after):
    if descriptor in ('normal', 'normal learning', 'normal weighted-learning',
                      'natural weighted-learning', 'weighted-learning', 'natural normal'):
        return 'normal'
    if descriptor in ('forced', 'forced reset', 'forced full-bank reset',
                      'natural forced', 'full-bank reset', 'natural full-bank reset'):
        return 'forced'
    if descriptor in ('direct', 'direct predicate', 'direct real-predicate',
                      'direct real predicate'):
        return 'direct'
    if descriptor in ('stock natural', 'natural stock'):
        return 'stock'
    if descriptor == 'stock normal':
        return 'stock_normal'
    if descriptor == 'stock forced':
        return 'stock_forced'
    if descriptor == 'natural' and re.match(r'\s+(?:use|retain)\s+stock\b', after, re.I):
        return 'stock'
    assert descriptor in ('', 'literal', 'executed', 'registered', 'bound',
                          'executed literal', 'registered literal'), 'Unbound case-count category'
    return 'total'


def _publication_details(section, counts, frame_bytes, pool_bytes):
    case_counts = {key: [] for key in ('total', 'normal', 'forced', 'direct',
                                     'stock', 'stock_normal', 'stock_forced')}
    for match in re.finditer(r'\b([0-9][0-9,]*)\s*(?:-\s*)?'
                             r'((?:[a-z]+(?:-[a-z]+)?\s+){0,5})(?:cases?|times)\b',
                             section, re.I):
        category = _case_category(match[2].strip().lower(), section[match.end():])
        case_counts[category].append(int(match[1].replace(',', '')))
    for name, expected in counts.items():
        if name in case_counts:
            assert case_counts[name] and set(case_counts[name]) == {expected}
    natural = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+natural\s+learner\s+calls?\b', section, re.I)]
    assert natural and set(natural) == {counts['normal']+counts['forced']}
    words = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+(?:normal\s+)?output\s+words?\b', section, re.I)]
    assert words and set(words) == {counts['words']}
    records = [int(number.replace(',', '')) for number in re.findall(
        r'\b([0-9][0-9,]*)\s+record\s+bytes\b', section, re.I)]
    if records:
        assert set(records) == {counts['record_values']}
    scopes = (
        (r'byte\s+(?:(?:observed|stack|local)\s+)?frame', frame_bytes),
        (r'(?:bound\s+)?pool/calibration\s+bytes', pool_bytes),
        (r'byte\s+(?:selected\s+)?reference\s+row', 16),
        (r'byte\s+(?:forced\s+)?reference\s+bank', 96),
        (r'byte\s+natural\s+save\s+footprint', 36),
        (r'instruction\s+bytes', sum(end-start for start, end in CODE_SPANS)),
        (r'(?:bound\s+)?data\s+bytes', sum(size for _, size in POOLS)),
        (r'pool\s+bytes', sum(size for _, size in POOLS if size == 4)),
        (r'calibration\s+bytes', sum(size for _, size in POOLS if size < 4)),
    )
    for label, expected in scopes:
        found = [int(number.replace(',', '')) for number in re.findall(
            r'\b([0-9][0-9,]*)\s*(?:-\s*)?'+label+r'\b', section, re.I)]
        assert found and set(found) == {expected}


def _literal_counts(header):
    rows = _rows(header)
    counts = Counter()
    for fields, _, _, _, _, _ in rows:
        selector, _, _, _, weight, forced, direct, _, reset, _ = fields
        counts['direct' if direct else 'forced' if forced else 'normal'] += 1
        counts['stock'] += not direct and (selector, weight, reset) == (130, 224, 65535)
        if not direct and (selector, weight, reset) == (130, 224, 65535):
            counts['stock_forced' if forced else 'stock_normal'] += 1
    counts['total'] = len(rows)
    counts['words'] = 8*counts['normal']
    counts['record_values'] = len({fields[7] for fields, *_ in rows
                                 if fields[6] and (fields[9]&65535) != 65535})
    return counts


def _check_region(region):
    assert (region.key, region.rom, region.source, region.harness) == (KEY, 'JK08A', SOURCE, HARNESS)
    assert (region.start, region.end, region.callees) == (0x4a118, 0x4a1fc, ((0x25e20, 0x25e44),))
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.cases == 7336
    assert region.boundary is False and region.return_address_offset is None
    assert region.return_register == 5 and region.base_load is None and region.bits == ()
    assert region.constants == (('PREDICATE_ENTRY', 0x25e20),)
    assert region.symbols == tuple((name, item[0]) for name, item in OWNER_DEFINES.items())


def _synthetic_region():
    return _verifier().Region(key=KEY, rom='JK08A', source=SOURCE, harness=HARNESS,
        start=0x4a118, end=0x4a1fc, pools=POOLS, ram_literals=RAM_LITERALS,
        cases=7336, boundary=False,
        symbols=tuple((name, item[0]) for name, item in OWNER_DEFINES.items()),
        constants=(('PREDICATE_ENTRY', 0x25e20),), callees=((0x25e20, 0x25e44),))


PUBLICATION = (
    'The fixture binds 132 instructions, 304 bound bytes and 7336 literal cases. '
    'There are 264 instruction bytes and 40 data bytes: 36 pool bytes and 4 calibration bytes. '
    'The matrix contains 5256 normal learning cases, 540 forced reset cases and '
    '1540 direct predicate cases. There are 5796 natural learner calls. '
    'Stock calibration supplies 2015 stock normal cases and 18 stock forced cases, '
    'totaling 2033 stock natural cases. All 42048 normal output words are checked. '
    'Direct predicate contexts cover all 256 record bytes. '
    'The 80-byte observed frame contains a 36-byte natural save footprint. '
    'All 40 bound pool/calibration bytes are preserved. Normal learning permits '
    'the 16-byte reference row and forced reset permits the 96-byte reference bank.'
)
PUBLICATION_COUNTS = dict(total=7336, normal=5256, forced=540, direct=1540,
                          stock=2033, stock_normal=2015, stock_forced=18,
                          words=42048, record_values=256)


def _valid_link(contract):
    owner, kind, target, slot, note, props, roles, function = contract
    return SimpleNamespace(owner=SimpleNamespace(key=owner), type=kind,
        to=SimpleNamespace(key=target), slot=slot, offset=None, stated={'7mfk'}, roles=set(roles),
        props={**props, 'via': [PREDICATE_FUNCTION if function == PREDICATE else FUNCTION],
               'note': note}, evidence=[
            dict(kind='test', path=THIS_TEST, key=OWNER_TEST),
            dict(kind='test', path=THIS_TEST, key=STOCK_TEST),
            dict(kind='spec', path=SPEC, key=SECTION)])


def test_knock_reference_learning_all_typed_notes_and_claim_levels_are_explicit():
    assert len(LINK_CONTRACTS) == 17
    assert len({item[:4] for item in LINK_CONTRACTS}) == 17
    for contract in LINK_CONTRACTS:
        _check_link_contract(_valid_link(contract), contract)


@pytest.mark.parametrize('contract', LINK_CONTRACTS)
@pytest.mark.parametrize('offset', (0, 1))
def test_knock_reference_learning_unstated_address_offsets_are_rejected(contract, offset):
    link = _valid_link(contract)
    _check_link_contract(link, contract)
    link.offset = offset
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('contract', LINK_CONTRACTS)
@pytest.mark.parametrize('mutation', ('note', 'inverse', 'via', 'scope', 'relies',
                                     'supports', 'owner_evidence', 'stock_evidence', 'spec_evidence'))
def test_knock_reference_learning_typed_condition_mutations_are_rejected(contract, mutation):
    link = _valid_link(contract)
    if mutation == 'note':
        link.props['note'] = ''
    elif mutation == 'inverse':
        link.props['note'] += ' Opposite selector conditions select normal learning.'
    elif mutation == 'via':
        link.props['via'].append(SymbolKey('7mfk', 'fn', 0x4a238))
    elif mutation == 'scope':
        link.stated.add('jk78c')
    elif mutation in ('relies', 'supports'):
        link.props[mutation] = 'level' if mutation == 'relies' else 'contract'
    else:
        excluded = {'owner_evidence': ('test', OWNER_TEST), 'stock_evidence': ('test', STOCK_TEST),
                    'spec_evidence': ('spec', SECTION)}[mutation]
        link.evidence = [item for item in link.evidence if (item['kind'], item['key']) != excluded]
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index,old,new', (
    (3, 'bit3 clear', 'bit3 set'), (4, 'bit3 set', 'bit3 clear'),
    (5, 'clear selects primary', 'set selects primary'),
    (6, 'Both clear selects normal', 'Either set selects normal'),
    (1, 'only if q<old', 'only if q>=old'),
    (2, 'not only the selected row', 'only the selected row'),
    (7, 'upper-clamp taken arm is unreachable', 'upper-clamp taken arm is reachable'),
))
def test_knock_reference_learning_inverse_numeric_and_selector_notes_are_rejected(index, old, new):
    contract = LINK_CONTRACTS[index]
    link = _valid_link(contract)
    assert old in link.props['note']
    link.props['note'] = link.props['note'].replace(old, new)
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index,key', [(index, key) for index, item in enumerate(LINK_CONTRACTS)
                                     for key in item[5] if key.startswith('reverse_')])
@pytest.mark.parametrize('mutation', ('missing', 'weakened'))
def test_knock_reference_learning_reverse_claims_are_required(index, key, mutation):
    contract = LINK_CONTRACTS[index]
    link = _valid_link(contract)
    if mutation == 'missing':
        del link.props[key]
    else:
        link.props[key] = 'level' if key.endswith('relies') else 'identity'
        if link.props[key] == contract[5][key]:
            link.props[key] = 'contract'
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('contract', [item for item in LINK_CONTRACTS if item[6]])
def test_knock_reference_learning_index_and_consumer_roles_are_required(contract):
    link = _valid_link(contract)
    link.roles.clear()
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('field,value', (
    ('from', SymbolKey('7mfk', 'reg', 0xfffff840)),
    ('from', SymbolKey('7mfk', 'ram', 0xffff2132)),
    ('to', SymbolKey('7mfk', 'ram', 0xffff21d8)),
    ('effect', 'adds'), ('sign', 'positive'),
    ('via', [FUNCTION, SymbolKey('7mfk', 'fn', 0x4a238)]),
    ('via', [SymbolKey('7mfk', 'fn', 0x4a238)]),
    ('note', FORMULA.replace('(255-W)', '(256-W)')),
))
def test_knock_reference_learning_chain_source_formula_and_sole_entry_are_required(field, value):
    step = dict(from_=SymbolKey('7mfk', 'ram', 0xffff20c2))
    step = {'from': step['from_'], 'to': SymbolKey('7mfk', 'ram', 0xffff2178),
            'effect': 'learns', 'sign': 'none', 'via': [FUNCTION], 'note': FORMULA}
    _check_step(step)
    step[field] = value
    with pytest.raises(AssertionError):
        _check_step(step)


@pytest.mark.parametrize('changes', (
    dict(rom='JK00D'), dict(key=KEY+'-other'), dict(source='other.s'), dict(harness='other.c'),
    dict(start=0x4a11a), dict(end=0x4a1fe), dict(callees=()),
    dict(callees=((0x25e22, 0x25e44),)), dict(pools=POOLS[:-1]), dict(pools=tuple(reversed(POOLS))),
    dict(ram_literals=RAM_LITERALS[:-1]), dict(ram_literals=RAM_LITERALS+(0x4a224,)),
    dict(cases=7337), dict(boundary=True), dict(return_address_offset=0),
    dict(return_register=6), dict(base_load=0x4a12c),
    dict(bits=(('EXTRA', 'knock_selector_config/tbl', 'bit3'),)),
    dict(constants=(('PREDICATE_ENTRY', 0x25e22),)),
    dict(constants=(('PREDICATE_ENTRY', 0x25e20), ('EXTRA', 1))),
    dict(constants=(('PREDICATE_ENTRY', 0x25e20), ('PREDICATE_ENTRY', 0x25e20))),
    dict(symbols=tuple(reversed(tuple((name, item[0]) for name, item in OWNER_DEFINES.items())))),
    dict(symbols=tuple((name, item[0]) for name, item in OWNER_DEFINES.items())+(('WEIGHT', 'knock_reference_weight/tbl'),)),
    dict(symbols=(('REFERENCES', 'knock_reference_samples/ram'),)),
))
def test_knock_reference_learning_complete_region_metadata_mutations_are_rejected(changes):
    region = _synthetic_region()
    _check_region(region)
    with pytest.raises(AssertionError):
        _check_region(replace(region, **changes))


def _validate_publication(section):
    for value, noun in ((132, 'instructions'), (304, 'bytes'), (7336, 'cases')):
        _published(section, value, noun)
    _publication_details(section, PUBLICATION_COUNTS, 80, 40)


def _document_arithmetic():
    return 'q = '+FORMULA.split('q = ', 1)[1].replace('; to = ', '\nnew = ')


def _check_document_arithmetic(section, is_spec):
    if is_spec:
        [formula] = re.findall(r'```text\s+(.*?)\s+```', section, re.S)
        assert re.sub(r'\s+', '', formula) == re.sub(r'\s+', '', _document_arithmetic())
    else:
        declarations = re.findall(r'\bThe coefficients\b[^.]*\.', section, re.I)
        assert declarations == ['The coefficients W and 255-W divide by 256; only q<old adds one.']


@pytest.mark.parametrize('old,new', (
    ('(255-W)', '(256-W)'), ('q+min(1,', 'q+min(2,'), ('/256)', '/255)'),
    ('min(65535,', 'min(65534,'), ('uint16(v)', 'int16(v)'),
    ('uint16(old)-q', 'q-uint16(old)'),
    ('q+min(1,max(0,uint16(old)-q))', 'q+1'),
))
def test_knock_reference_learning_documented_equation_mutations_are_rejected(old, new):
    section = '```text '+_document_arithmetic()+' ```'
    _check_document_arithmetic(section, True)
    assert old in section
    with pytest.raises(AssertionError):
        _check_document_arithmetic(section.replace(old, new), True)


@pytest.mark.parametrize('old,new', (
    ('255-W', '256-W'), ('by 256', 'by 255'), ('q<old', 'q>=old'),
    ('adds one', 'adds two'), ('only q<old adds one', 'always adds one'),
))
def test_knock_reference_learning_readme_conditional_equation_mutations_are_rejected(old, new):
    section = 'The coefficients W and 255-W divide by 256; only q<old adds one.'
    _check_document_arithmetic(section, False)
    with pytest.raises(AssertionError):
        _check_document_arithmetic(section.replace(old, new), False)


@pytest.mark.parametrize('extra', (
    'The coefficients W and 256-W divide by 256; only q<old adds one.',
    'The coefficients W and 255-W divide by 255; only q>=old adds one.',
    'The coefficients W and 255-W divide by 256; only q<old adds one.',
))
def test_knock_reference_learning_appended_arithmetic_declarations_are_rejected(extra):
    section = 'The coefficients W and 255-W divide by 256; only q<old adds one.'
    _check_document_arithmetic(section, False)
    with pytest.raises(AssertionError):
        _check_document_arithmetic(section+' '+extra, False)


def test_knock_reference_learning_missing_or_duplicate_region_fails_without_skip():
    region = _synthetic_region()
    assert _required_region([region]) is region
    for items in ([], [region, region]):
        with pytest.raises(AssertionError):
            _required_region(items)


@pytest.mark.parametrize('missing', [LEARNER, PREDICATE, *(item[0] for item in OWNER_DEFINES.values())])
def test_knock_reference_learning_missing_mandatory_owner_fails_without_skip(missing):
    keys = {LEARNER, PREDICATE, *(item[0] for item in OWNER_DEFINES.values())}
    model = SimpleNamespace(meanings=[SimpleNamespace(key=key) for key in keys])
    _require_owner_integration(model)
    model.meanings = [owner for owner in model.meanings if owner.key != missing]
    with pytest.raises(AssertionError):
        _require_owner_integration(model)


def test_knock_reference_learning_missing_tracked_header_fails_without_skip(tmp_path):
    with pytest.raises(AssertionError):
        _required_header(tmp_path / 'missing-reference-cases.h')


@pytest.mark.parametrize('extra', (
    '133 instructions', '133-instruction envelope', '305 bound bytes', '305-byte bound envelope',
    '7337 cases', '7337-case literal matrix', 'execution repeats 7337 times',
    '5257 normal learning cases', '541 forced reset cases', '1541 direct predicate cases',
    '2034 stock natural cases', '2016 stock normal cases', '19 stock forced cases',
    '5797 natural learner calls', '42049 normal output words', '8 output words',
    '81-byte observed frame', '37-byte natural save footprint', '41 bound pool/calibration bytes',
    '17-byte reference row', '97-byte reference bank', '265 instruction bytes',
    '41 data bytes', '37 pool bytes', '5 calibration bytes', '540 normal learning cases',
    '5256 forced reset cases', '5256-case total matrix', '257 record bytes',
))
def test_knock_reference_learning_contradictory_main_and_scoped_counts_are_rejected(extra):
    _validate_publication(PUBLICATION)
    with pytest.raises(AssertionError):
        _validate_publication(PUBLICATION+' '+extra)


@pytest.mark.parametrize('old,new', (
    ('5256 normal learning', '540 normal learning'), ('540 forced reset', '5256 forced reset'),
    ('1540 direct predicate', '2033 direct predicate'), ('2033 stock natural', '1540 stock natural'),
    ('2015 stock normal', '18 stock normal'), ('18 stock forced', '2015 stock forced'),
    ('5796 natural learner', '5797 natural learner'), ('80-byte observed', '81-byte observed'),
    ('40 bound pool/calibration', '41 bound pool/calibration'), ('36 pool bytes', '37 pool bytes'),
    ('4 calibration bytes', '5 calibration bytes'), ('264 instruction bytes', '265 instruction bytes'),
    ('40 data bytes', '41 data bytes'), ('36-byte natural save', '37-byte natural save'),
    ('16-byte reference row', '17-byte reference row'), ('96-byte reference bank', '97-byte reference bank'),
))
def test_knock_reference_learning_relabelled_publication_counts_are_rejected(old, new):
    _validate_publication(PUBLICATION)
    assert old in PUBLICATION
    with pytest.raises(AssertionError):
        _validate_publication(PUBLICATION.replace(old, new))


def _ledger_claim(model, owner, registry, order, dependency):
    name, kind = owner.split('/')
    [markers] = [rows for marker_kind, owner_name, rows, _ in model.stash['ledger_rows']
                 if (marker_kind, owner_name) == (kind, name)]
    [row] = [item for item in markers if (item['registry'], item['order']) == (registry, order)]
    assert dependency in row.get('dependency', [])


def test_knock_reference_learning_shared_predicate_ledger_ends_remain_selected():
    model = compile.cached(repo.ROOT)
    _ledger_claim(model, 'hallowed-malkoha/ram', 'vars', 429,
                  dict(role='consumer', to=PREDICATE, type='reader', end='owner',
                       relies='structure', supports='identity'))
    for level in ('identity', 'contract'):
        _ledger_claim(model, PREDICATE, 'funcs', 522,
                      dict(role='indexed_by', to='hallowed-malkoha/ram', type='reader', end='to',
                           link_role='indexed_by', relies='structure', supports=level))


def verify_reference_learning_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert (word(0x884b, 1), word(0x8b3d, 1), word(0x9282)) == (224, 130, 65535)
    pools = {0x25f10: 0xffff5718, 0x4a1fc: 0x8b3d, 0x4a200: 0xffff1ff4,
             0x4a208: 0xffff11d4, 0x4a224: 0x25e20, 0x4a228: 0x9282,
             0x4a22c: 0xffff2178, 0x4a230: 0x884b, 0x4a234: 0xffff20c2}
    assert {at: word(at, 4) for at in pools} == pools
    assert [word(a) for a in (0x4a1bc, 0x4a1be, 0x4a1c2, 0x4a1c4, 0x4a1ca,
                             0x4a1d0, 0x4a1d2, 0x4a1d6, 0x4a1d8)] == [
        0x6ddc, 0x666d, 0x622d, 0x0d27, 0x0467, 0x4519, 0x3562, 0x7501, 0x35b6]
    for call, delay, pool_load in ((0x4a142, 0x4a144, 0x4a13e), (0x4a18a, 0x4a18c, 0x4a186)):
        decoded = sh2.decode(word(call), call)
        assert decoded.flow == 'call' and decoded.delayed
        assert sh2.decode(word(pool_load), pool_load).value == ('pool', 0x4a224, 4)
        assert word(delay) == (0x742d if delay == 0x4a144 else 0x743f)
    assert [word(a) for a in (0x4a178, 0x4a17a, 0x25e40, 0x25e42)] == [0x000b, 0x68f6, 0x000b, 0x6023]
    assert [word(a) for a in (0x25e22, 0x25e24, 0x25e34)] == [0x604f, 0x88ff, 0xc880]
    assert sh2.decode(word(0x25e32), 0x25e32).access == sh2.Access(6, 1, 1, 'load')
    assert sh2.decode(word(0x4a1ee), 0x4a1ee).access == sh2.Access(6, 0, 2, 'store', True)
    assert sh2.decode(word(0x4a158), 0x4a158).access == sh2.Access(2, 0, 2, 'store')
    assert sh2.decode(word(0x4a15c), 0x4a15c).access == sh2.Access(2, 16, 2, 'store')
    assert word(0x4a14c) == 0xe403 and word(0x4a160) == 0x7202 and word(0x4a166) == 0x7720


def verify_static_callers(data):
    for start, end, digest in CALLER_SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    call = sh2.decode(word(0x4a386), 0x4a386)
    assert call.flow == 'call' and call.delayed and call.target == 0x4a118
    assert word(0x4a388) == 0x0009
    load = sh2.decode(word(0x4a954), 0x4a954)
    assert load.dest == 2 and load.value == ('pool', 0x4a9c0, 4)
    assert word(0x4a9c0, 4) == 0x4a238
    assert sh2.decode(word(0x4a958), 0x4a958).flow == 'call'


def test_knock_reference_learning_exact_stock_unsigned_words_natural_returns_and_static_callers():
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_reference_learning_stock(data)
    verify_static_callers(data)
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 132
    assert sum(end-start for start, end, _ in SPANS) == 304


@pytest.mark.parametrize('address', [a for start, end, _ in (*SPANS, *CALLER_SPANS) for a in range(start, end)])
def test_knock_reference_learning_static_corruption_is_rejected(address, jk08a_stock_bytes):
    data = bytearray(jk08a_stock_bytes)
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_reference_learning_stock(data)
        verify_static_callers(data)


def test_knock_reference_learning_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    _require_owner_integration(model)
    assert len(model.entities[('chain', 'knock_retard')].steps) == 16
    _normal_note()
    owners = {name: model.meaning_of(SymbolKey('7mfk', 'tbl' if name in ('SELECTOR', 'WEIGHT', 'RESET_WORD') else 'ram', at))
              for name, (_, at) in OWNER_DEFINES.items()}
    for name, (key, _) in OWNER_DEFINES.items():
        assert owners[name].key == key
    learner = model.meaning_of(FUNCTION)
    assert learner.key == LEARNER and learner.symbols['7mfk'].value('level') == 'code'
    assert learner.symbols['7mfk'].value('block') == 'knock/block'
    assert model.meaning_of(PREDICATE_FUNCTION).key == PREDICATE
    all_owners = {item.key: item for item in model.meanings}
    for contract in LINK_CONTRACTS:
        owner, kind, target, slot = contract[:4]
        _check_link_contract(_link(all_owners[owner], kind, target, slot), contract)
    for name in ('REFERENCES', 'SAMPLES'):
        symbol = owners[name].symbols['7mfk']
        assert (symbol.value('width'), symbol.value('signed'), symbol.value('level')) == (16, False, 'code')
    record = owners['DIAGNOSTICS'].symbols['7mfk']
    assert (record.value('width'), record.value('signed'), record.value('unit')) == (8, False, 'diagnostic record byte')
    for name, storage in (('WEIGHT', 'uint8'), ('RESET_WORD', 'uint16')):
        symbol = owners[name].symbols['7mfk']
        assert (symbol.value('storage'), symbol.value('rows'), symbol.value('cols'), symbol.value('level')) == (
            storage, 1, 1, 'code')
        assert symbol.value('block') == 'knock/block'
    for name, stock in (('WEIGHT', '224'), ('RESET_WORD', '65535')):
        assert stock not in owners[name].props['summary']
    bank = owners['REFERENCES']
    for name in ('SAMPLES', 'WEIGHT', 'RESET_WORD', 'PRIMARY', 'ALTERNATE'):
        _proof(_link(bank, 'input', owners[name].key))
    _proof(_link(bank, 'selector', owners['SELECTOR'].key, 'bit3'))
    condition = _link(bank, 'selector', PREDICATE)
    _proof(condition)
    for phrase in ('012d', '013f', 'both clear', 'either', 'all 48', 'no direct call-count'):
        assert phrase in condition.props['note'].lower()
    writer = _link(bank, 'writer', LEARNER)
    _proof(writer)
    for phrase in ('i=x', '0..7', 'j', '0..47', RESET_FORMULA.lower(), 'unreachable',
                   '65280', 'acquisition', 'not executed'):
        assert phrase in writer.props['note'].lower()
    for name in ('REFERENCES', 'SAMPLES', 'PRIMARY', 'ALTERNATE', 'SELECTOR', 'WEIGHT', 'RESET_WORD'):
        _proof(_link(owners[name], 'reader', LEARNER))
    records = _link(owners['DIAGNOSTICS'], 'reader', PREDICATE)
    _proof(records, PREDICATE_FUNCTION)
    for phrase in ('three-byte', 'byte1', 'ffff', 'no record read', 'array extent', 'upper-word'):
        assert phrase in records.props['note'].lower()
    caller = _link(learner, 'depends', 'knock_slice_evaluator/fn')
    _proof(caller)
    assert 'consumer' in caller.roles
    for phrase in ('0004a386', 'static', 'not executed', 'acquisition'):
        assert phrase in caller.props['note'].lower()


def _check_literal_arithmetic(header, normal_note):
    assert Grammar(repo.config()).validate(normal_note) is None
    assert Grammar(repo.config()).validate(RESET_FORMULA) is None
    rows = _rows(header)
    [total] = re.findall(r'^#define KNOCK_REFERENCE_LEARNING_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(rows) == int(total) == 7336
    normal = builtins.compile(normal_note, '<unsigned reference-word arithmetic>', 'exec')
    reset_expression = builtins.compile(RESET_FORMULA, '<full-bank reset arithmetic>', 'exec')
    sentinels = [(0x28765430+i*0x01030507)&0xffffffff for i in range(15)]
    counts, differences = Counter(), Counter()
    comparisons, residues, pairs, records, sentinel_raw = set(), set(), set(), set(), set()
    selectors, channels, weights, status_pairs = set(), set(), set(), set()
    max_q = max_new = words_checked = 0
    for fields, samples, old, words, registers, (t,) in rows:
        selector, channel, first, second, weight, forced, direct, record, reset, raw_id = fields
        assert all(0 <= value <= 255 for value in (selector, first, second, weight, record))
        assert 1 <= channel <= 6 and 0 <= reset <= 65535 and 0 <= raw_id <= 0xffffffff
        assert forced in (0, 1) and direct in (0, 1) and t in (0, 1)
        assert all(0 <= value <= 65535 for value in samples+old+words)
        assert forced == int(not direct and bool((first|second)&128))
        expected = sentinels.copy()
        expected[7] = 0x25e20 if direct else 0x4a118
        expected_t = 1
        if direct:
            counts['predicate'] += 1
            ident = raw_id&65535
            assert ident in (0x12d, 0x13f, 0xffff)
            expected[4] = raw_id
            bit = 0 if ident == 65535 else (record>>7)&1
            expected[0] = expected[2] = bit
            expected[1] = 0x01005718
            expected_t = 1-bit
            if ident == 65535:
                sentinel_raw.add(raw_id)
            else:
                expected[6] = 0x01005718+3*ident
                records.add((ident, raw_id>>16, record))
        elif forced:
            counts['forced'] += 1
            values = dict(ROM16={0x9282: reset})
            exec(reset_expression, {'__builtins__': {}}, values)
            assert words == (values['to'],)*8
            signed_reset = (reset^32768)-32768
            expected[0] = expected[5] = signed_reset&0xffffffff
            expected[1] = 0x01005718
            expected[2], expected[7] = 0x01002178+80, 0x01002178+96
            expected[4] = expected[6] = 0
            counts['stock_forced'] += selector == 130 and weight == 224 and reset == 65535
        else:
            counts['normal'] += 1
            row = 0xffff2178+16*(channel-1)
            memory = {0xffff20c2+2*i: value for i, value in enumerate(samples)}
            memory.update({row+2*i: value for i, value in enumerate(old)})
            values = dict(ROM8={0x8b3d: selector, 0x884b: weight}, RAM16=memory,
                          ffff11de=7-channel if selector&8 else channel,
                          ffff2143=channel if selector&8 else 7-channel,
                          uint8=lambda value: value&255, uint16=lambda value: value&65535,
                          min=min, max=max, floor=math.floor)
            for i, expected_word in enumerate(words):
                values['x'] = i
                exec(normal, {'__builtins__': {}}, values)
                assert values['to'] == expected_word and values['row'] == row and values['c'] == channel
                q = values['q']
                numerator = weight*samples[i]+(255-weight)*old[i]
                assert numerator <= 16711425 and q <= 65279 and expected_word <= 65280
                comparisons.add((q>old[i])-(q<old[i]))
                residues.add(numerator%256)
                pairs.add((weight, samples[i], old[i]))
                differences['ceil'] += expected_word != (numerator+255)//256
                differences['unconditional'] += expected_word != q+1
                differences['sum256'] += expected_word != (weight*samples[i]+(256-weight)*old[i])//256
                max_q, max_new = max(max_q, q), max(max_new, expected_word)
                words_checked += 1
            expected[0], expected[1] = 16*channel+14, 0x01005718
            expected[2] = old[7]*(255-weight)
            expected[4] = expected[5] = words[7]
            expected[6], expected[7] = 0x01002178-16, 16
            counts['stock_normal'] += selector == 130 and weight == 224 and reset == 65535
            weights.add(weight)
        assert tuple(expected) == registers and t == expected_t
        if not direct:
            selectors.add(selector)
            channels.add(channel)
            status_pairs.add((bool(first&128), bool(second&128)))
    assert {key: counts[key] for key in ('normal', 'forced', 'predicate')} == dict(normal=5256, forced=540, predicate=1540)
    assert counts['stock_normal'] == 2015 and counts['stock_forced'] == 18
    assert words_checked == 42048 and (max_q, max_new) == (65279, 65280)
    assert comparisons == {-1, 0, 1} and residues == set(range(256))
    assert weights == {0, 1, 127, 128, 224, 254, 255}
    assert selectors == set(range(256)) and channels == set(range(1, 7))
    assert status_pairs == {(False, False), (True, False), (False, True), (True, True)}
    assert records == {(ident, upper, record) for ident in (0x12d, 0x13f)
                       for upper in (0, 0x8000, 0xa5c3) for record in range(256)}
    assert sentinel_raw == {0xffff, 0x8000ffff, 0xa5c3ffff, 0xffffffff}
    assert all(differences.values())
    for value in (0, 1, 255, 256, 257, 32767, 32768, 65534, 65535):
        assert (224, value, value) in pairs
    assert (224, 1, 0) in pairs and (224, 0, 256) in pairs


def test_knock_reference_learning_arithmetic_matches_all_literal_words_and_natural_exit_vectors():
    _require_owner_integration(compile.cached(repo.ROOT))
    header = _required_header(repo.ROOT / 'tools/sh-elf-run' / HEADER)
    _check_literal_arithmetic(header, _normal_note())


def test_knock_reference_learning_registered_stock_contract():
    module, region = _verifier(), _region()
    _check_region(region)
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_reference_learning_stock(data)
    verify_static_callers(data)
    defines = module.harness_defines(region, data)
    assert defines == {'REGION_ENTRY': 0x4a118, 'PREDICATE_ENTRY': 0x25e20,
                       **{name: item[1] for name, item in OWNER_DEFINES.items()}}
    fixture = module.build_fixture(region, data)
    expected_fixture = bytearray(data)
    for address in RAM_LITERALS:
        expected_fixture[address:address+4] = module.base_verifier.alias_high_ram(
            int.from_bytes(data[address:address+4], 'big')).to_bytes(4, 'big')
    assert fixture == expected_fixture
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    instructions = sum((end-start)//2 for start, end in CODE_SPANS)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    pins = {
        SOURCE: '73e2e41bb2ff23812eaede541df9a7a210d6ce07a578367f16dd5072e4c09120',
        HEADER: '3931b924053dc2cbb13146f420f969a3004e23a5b34980eee69d4ef263a667d3',
        HARNESS: '66a6b3c2040358ab4f0183e09283d26db260d8c3748edb7f9cffe1221972b2aa',
        'stock_knock_reference_learning_invoke.s':
            '54113d2d2d21da24d54232006487c961c2d8a943e2c1e9c46381eb8c5d50be66',
    }
    for name, digest in pins.items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    shared = (directory / 'stock_invoke.s').read_text()
    assert shared.count('.include "stock_knock_reference_learning_invoke.s"') == 1
    assert '_stock_invoke_knock_reference_learning:' not in shared
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    assert len(_rows(header)) == region.cases
    assert (instructions, bound, region.cases) == (132, 304, 7336)
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in OWNER_DEFINES)
    assert 'ARRAY_SIZE(reference_cases)' in harness and harness.count('++completed;') == 1
    assert 'completed!=KNOCK_REFERENCE_LEARNING_CASE_COUNT' in harness
    assert ('VQ_SH_ELF_STOCK_CODE status=PASS '
            'region=jk08a-knock-reference-learning cases=%lu\\n') in harness
    for phrase in ('test->expected[i]', 'test->expected_t', 'i<15U', 'i<65536U',
                   'calibration_before[40]', 'frame_before[80]', 'i<48U', 'i<8U',
                   'first+96U', 'last=first+16U', 'if(!test->direct && i>=first && i<last)continue;',
                   'all 48 literal reset words', 'all eight literal learned words',
                   'natural saved R8..R14 frame', 'natural saved PR/MACL frame',
                   'natural SP preservation', 'natural PR return', 'distinct C caller ABI restoration',
                   'test->direct || i<12U || i>=48U', 'frame_word(out.frame_before,72)',
                   'frame_word(out.frame_after,72)', 'if(!verify_initial_calibration())return 1;'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded knock reference learning'),
                        ('tools/sh-elf-run/README.md', 'Bounded JK08A knock reference learning')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        [(frame_before, frame_after)] = re.findall(
            r'uint8_t frame_before\[([0-9]+)\], frame_after\[([0-9]+)\];', harness)
        assert frame_before == frame_after
        [calibration] = re.findall(r'calibration_before\[([0-9]+)\]', harness)
        assert int(calibration) == sum(size for _, size in region.pools)
        _publication_details(section, _literal_counts(header), int(frame_before), int(calibration))
        _check_document_arithmetic(section, path == SPEC)
        lower = section.lower()
        for phrase in ('unsigned', '255', '65280', '48', '96', '16',
                       'sentinel', 'natural', 'artificial', 'acquisition', 'hardware'):
            assert phrase in lower
        assert re.search(r'\br4 upper(?:-| )words?\b', lower)
        assert set(re.findall(r'\bq\s*<=\s*([0-9]+)', lower)) == {'65279'}
        assert set(re.findall(r'\b(?:new|result)\s*<=\s*([0-9]+)', lower)) == {'65280'}
        if path == SPEC:
            assert 'upper-clamp taken arm is unreachable' in lower
            assert 'no direct invocation-count observation is inferred' in lower
            assert 'diagnostic array extent are outside this contract' in lower
            assert 'static caller anchors do not execute acquisition or full evaluator dispatch' in lower
            assert 'without injecting sr or claiming preservation of its other bits' in lower
        else:
            assert 'it cannot take the final upper clamp' in lower
            assert 'static acquisition and caller anchors remain separate from this execution' in lower
            assert 'sr is not injected and non-t preservation is outside this fixture' in lower
