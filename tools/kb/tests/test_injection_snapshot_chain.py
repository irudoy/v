"""Bind two unsigned result snapshots to their real bounded stock copy call."""
import ast
from collections import Counter
import copy
from dataclasses import replace
from functools import cache
import hashlib
import re
from types import SimpleNamespace

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR = repo.ROOT / 'tools/sh-elf-run'
KEY = 'jk08a-injection-snapshot'
HEADER = 'injection-snapshot-cases.h'
SOURCE = 'stock_jk08a_injection_snapshot.s'
HARNESS = 'harness-stock-jk08a-injection-snapshot.c'
PATH = 'tools/kb/tests/test_injection_snapshot_chain.py'
SECTION = 'Bounded injection result snapshot'
VIA = ['coherent_snapshot/fn', 'mahogany-bobcat/fn']
SYMBOLS = (('LEAD_SOURCE', 'flat-coyote/ram', 0xffff23f0),
           ('ANGLE_SOURCE', 'righteous-scorpion/ram', 0xffff23bf),
           ('LEAD_SNAPSHOT', 'fabulous-koel/ram', 0xffff2364),
           ('ANGLE_SNAPSHOT', 'nippy-caribou/ram', 0xffff2333))
SLICES = ((0x21314, bytes.fromhex('d122d2234b0b60c3')),
          (0x22558, bytes.fromhex('2f262f362f46880089126423340c6024210034268b0c6024801134268b086024801234268b04602480133426710489ee64f663f6000b62f6')),
          (0x213a0, bytes.fromhex('ffff2330ffff23bc')))
STATIC = ((0x20e14, bytes.fromhex('ecf06ccc')), (0x20eea, bytes.fromhex('db82')),
          (0x210f4, bytes.fromhex('00022558')), (0x21308, bytes.fromhex('4b0b7c9c')))
COPY_NOTE = ('This bounded 7mfk caller copies the unsigned byte through its real '
             '140-byte block-copy helper; to = uint8(from). Entry R11 and R12 '
             'are explicit contexts. No complete scheduler execution, live '
             'cadence or hardware atomicity is established.')


def stock_contract(data):
    for address, expected in (*SLICES, *STATIC):
        assert data[address:address + len(expected)] == expected, f'{address:08x}'
    word = lambda at: int.from_bytes(data[at:at + 2], 'big')
    assert sh2.decode(word(0x21314), 0x21314).value == ('pool', 0x213a0, 4)
    assert sh2.decode(word(0x21316), 0x21316).value == ('pool', 0x213a4, 4)
    assert word(0x21318) == 0x4b0b and sh2.decode(word(0x21318), 0x21318).delayed
    assert word(0x2131a) == 0x60c3
    for at in range(0x22558, 0x22590, 2):
        instruction = sh2.decode(word(at), at)
        if instruction.flow == 'branch':
            assert 0x22558 <= instruction.target < 0x22590
    assert sh2.decode(word(0x2258c), 0x2258c).flow == 'return'
    assert word(0x2258e) == 0x62f6


def declared_region():
    return publication.stock_module().Region(
        key=KEY, rom='JK08A', source=SOURCE, harness=HARNESS,
        start=0x21314, end=0x2131c, pools=((0x213a0, 8),),
        ram_literals=(0x213a0, 0x213a4), cases=1700,
        return_address_offset=24, return_register=7,
        symbols=tuple((macro, owner) for macro, owner, _ in SYMBOLS),
        constants=(('EARLY_ONLY', 0),), callees=((0x22558, 0x22590),))


def region_contract(module):
    matches = [region for region in module.REGIONS if region.key == KEY]
    assert len(matches) == 1, 'The mandatory stock copy Region is absent or duplicated'
    [region] = matches
    assert region == declared_region()
    assert type(region.cases) is int
    return region


@cache
def literals():
    text = (TOOL_DIR / HEADER).read_text()
    [body] = re.findall(r'snapshot_cases\[\] = \{(.*?)\n\};', text, re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    rows = ast.literal_eval('[' + body.replace('{', '[').replace('}', ']') + ']')
    assert all(len(row) == 13 and len(row[11]) == len(row[12]) == 15 for row in rows)
    [count] = re.findall(r'^#define SNAPSHOT_CASE_COUNT (\d+)U$', text, re.M)
    assert len(rows) == int(count) == 1700
    return rows


def vector_contract(row):
    entry, source, target, length, pattern, position, seed, variant, t, exit_t, carry, incoming, expected = row
    assert entry in (0x21314, 0x22558) and pattern in (0, 1)
    assert t in (0, 1) and variant in (0, 1) and carry in (0, 1)
    assert 0 <= seed <= 255 and 0 <= length <= 255 and 0 <= position <= 139
    mask = (1 << 32) - 1
    alias = lambda address: 0x01000000 + (address & 65535)
    actual_in = [((0xa9876543 + i * 0x00130709) if variant
                  else (0x28765430 + i * 0x01030507)) & mask for i in range(15)]
    actual_in[7] = entry
    if entry == 0x21314:
        assert (source, target, length) == (0xffff23bc, 0xffff2330, 140)
        actual_in[11:13] = [0x22558, 140]
    else:
        assert 0xffff4000 <= source <= 0xffff4003 and 0xffff5000 <= target <= 0xffff5003
        actual_in[:3] = [length, alias(target), alias(source)]
        assert not pattern and not carry
    assert incoming == actual_in
    result = actual_in.copy()
    last = (int(position == length - 1) * 129 if pattern else (seed + 29 * (length - 1)) % 256)
    result[0] = ((last if last < 128 else last - 256) & mask) if length else 0
    result[1:3] = [alias(target) + 4 * (length // 4), alias(source)]
    if entry == 0x21314:
        result[7] = 0
    assert expected == result and exit_t == int(length == 0)


def chain_contract(model):
    chain = model.entities[('chain', 'injection_phase')]
    assert len(chain.steps) == 22
    for index, source, target in ((12, 'flat-coyote/ram', 'fabulous-koel/ram'),
                                  (13, 'righteous-scorpion/ram', 'nippy-caribou/ram')):
        expected = {'from': source, 'to': target, 'effect': 'copies', 'sign': 'positive',
                    'via': VIA, 'note': 'to = uint8(from)',
                    'specs': ['defs/JK08A.fuel.md', 'defs/JK08A.injection.md']}
        assert publication.normalized(model, chain.steps[index]) == expected
        assert Grammar(repo.config()).validate(chain.steps[index]['note']) is None


def owner_contract(model):
    for _, owner, address in SYMBOLS:
        entity = publication.required_owner(model, owner, address)
        symbol = entity.symbols['7mfk']
        assert symbol.value('width') == 8 and symbol.value('signed') is False
    for target, source in [('fabulous-koel/ram', 'flat-coyote/ram'),
                           ('nippy-caribou/ram', 'righteous-scorpion/ram')]:
        address = next(address for _, name, address in SYMBOLS if name == target)
        owner = publication.required_owner(model, target, address)
        for kind, to in [('copy', source), ('input', source), ('writer', VIA[0])]:
            [link] = [link for link in owner.links if link.type == kind and link.to.key == to]
            assert link.slot is None and link.offset is None and link.stated == {'7mfk'}
            assert publication.normalized(model, link.props['via']) == VIA
            assert link.props['relies'] == 'structure' and link.props['supports'] == 'identity'
            assert link.props['note'] == COPY_NOTE
            publication.required_evidence(model, link.evidence, [
                {'kind': 'l0', 'at': '7mfk:00021318'}, {'kind': 'l0', 'at': '7mfk:00022558'},
                {'kind': 'test', 'path': PATH, 'key': 'test_injection_snapshot_chain_owner_contract'},
                {'kind': 'test', 'path': PATH, 'key': 'test_injection_snapshot_registered_stock_contract'},
                {'kind': 'spec', 'path': publication.SPEC, 'key': SECTION}])
    for name, address in [(VIA[0], 0x20dfe), (VIA[1], 0x22558)]:
        owner = publication.required_owner(model, name, address)
        assert any('R12=140' in note and 'hardware atomicity' in note
                   for note in owner.symbols['7mfk'].props['note'])
    chain_contract(model)


def publication_contract(text, model):
    region = region_contract(publication.stock_module())
    instructions = sum((end - start) // 2 for start, end in region.code_spans)
    bound = 2 * instructions + sum(size for _, size in region.pools)
    for pattern, value in ((r'\b(\d+) instructions\b', instructions),
                           (r'\b(\d+) bound bytes\b', bound),
                           (r'\b(\d+) literal cases\b', len(literals()))):
        claims = re.findall(pattern, text)
        assert claims and all(int(claim) == value for claim in claims)
    assert '1024 affine caller contexts' in text and '280 isolated-byte caller contexts' in text
    assert '384 direct helper contexts' in text and '12 successive caller contexts' in text
    for phrase in ('R11=00022558', 'R12=140', 'SP+24', 'R7', 'hardware atomicity',
                   'ffff23f0 -> ffff2364', 'ffff23bf -> ffff2333', 'steps 13 and 14'):
        assert phrase in text
    grammar = Grammar(repo.config())
    indices = [i + 1 for i, step in enumerate(model.entities[('chain', 'injection_phase')].steps)
               if grammar.validate(step['note']) is None
               and publication.normalized(model, step['via']) in (['transformed_pulse_maximum/fn'], VIA)]
    assert indices == [9, 10, 11, 12, 13, 14]
    assert 'The 6 arithmetic records' in text


def test_injection_snapshot_stock_caller_pools_helper_branches_and_static_inputs_match():
    stock_contract(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [at + i for at, span in (*SLICES, *STATIC) for i in range(len(span))])
def test_injection_snapshot_rejects_each_changed_bound_or_static_byte(address):
    image = bytearray(derive.image_bytes(repo.layout('7mfk')))
    image[address] ^= 1
    with pytest.raises(AssertionError):
        stock_contract(image)


def test_injection_snapshot_literal_gpr_and_tail_contract_covers_every_frozen_case():
    for row in literals():
        vector_contract(row)
    rows = literals()
    assert Counter(row[0] for row in rows) == {0x21314: 1316, 0x22558: 384}
    affine = rows[:1024]
    assert {(row[6], row[7], row[8]) for row in affine} == {
        (seed, variant, t) for seed in range(256) for variant in (0, 1) for t in (0, 1)}
    for offset in (3, 52):
        assert {(row[6] + offset * 29) % 256 for row in affine} == set(range(256))
    assert {(row[5], row[7]) for row in rows[1024:1304]} == {
        (position, variant) for position in range(140) for variant in (0, 1)}
    assert {(row[3], row[1] & 3, row[2] & 3, row[8]) for row in rows[1304:1688]} == {
        (length, src, dst, t) for length in (0, 1, 2, 3, 4, 5, 6, 7, 139, 140, 141, 255)
        for src in range(4) for dst in range(4) for t in (0, 1)}
    assert [row[10] for row in rows[1688:]] == [0, 1, 1] * 4


@pytest.mark.parametrize('index', (0, 1, 2, 3, 9, 11, 12))
def test_injection_snapshot_refuses_entry_pointer_length_register_and_exit_mutations(index):
    row = copy.deepcopy(literals()[0])
    if index in (11, 12):
        row[index][3] ^= 1
    else:
        row[index] ^= 1
    with pytest.raises(AssertionError):
        vector_contract(row)


def test_injection_snapshot_chain_owner_contract():
    owner_contract(compile.cached(repo.ROOT))


@pytest.mark.parametrize('field,value', (('note', 'to = uint16(from)'), ('sign', 'none'),
    ('effect', 'converts'), ('via', []), ('via', [SymbolKey('7mfk', 'fn', 0x20dfe)]),
    ('via', [SymbolKey('7mfk', 'fn', 0x22558), SymbolKey('7mfk', 'fn', 0x20dfe)]),
    ('to', SymbolKey('7mfk', 'ram', 0xffff2333))))
def test_injection_snapshot_chain_refuses_width_sign_direction_or_missing_real_call(field, value):
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'injection_phase')]
    changed = replace(chain, steps=[dict(step) for step in chain.steps])
    changed.steps[12][field] = value
    proxy = SimpleNamespace(entities={('chain', 'injection_phase'): changed}, meaning_of=model.meaning_of)
    with pytest.raises(AssertionError):
        chain_contract(proxy)


def test_injection_snapshot_registered_stock_contract():
    region = region_contract(publication.stock_module())
    assert len(literals()) == region.cases
    defines = publication.stock_module().harness_defines(region, derive.image_bytes(repo.layout('7mfk')))
    assert all(defines[macro] == address for macro, _, address in SYMBOLS)
    text = (TOOL_DIR / HARNESS).read_text()
    assert 'i < ARRAY_SIZE(snapshot_cases)' in text and 'completed != SNAPSHOT_CASE_COUNT' in text
    assert 'i < 65536U' in text and 'out.frame_after, expected_frame' in text
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu' in text
    publication_contract(publication.section(publication.SPEC, SECTION), compile.cached(repo.ROOT))
    publication_contract(publication.section('tools/sh-elf-run/README.md', SECTION), compile.cached(repo.ROOT))


@pytest.mark.parametrize('phrase,replacement', (('32 instructions', '31 instructions'),
    ('72 bound bytes', '71 bound bytes'), ('1700 literal cases', '1699 literal cases'),
    ('R12=140', 'R12=139'), ('steps 13 and 14', 'steps 12 and 13'),
    ('The 6 arithmetic records', 'The 5 arithmetic records')))
def test_injection_snapshot_publication_rejects_changed_counts_bindings_and_chain_indices(phrase, replacement):
    text = publication.section(publication.SPEC, SECTION)
    assert phrase in text
    with pytest.raises(AssertionError):
        publication_contract(text.replace(phrase, replacement), compile.cached(repo.ROOT))


def test_injection_snapshot_retains_the_independently_executed_source_and_shared_invocation_bytes():
    expected = {
        SOURCE: '1cf159ca21f598e30318b444936d5dc13fd7c9c3783736fffe26c1c3a53d1ced',
        HARNESS: '101a7b4c8bab81887ae45e38bc8c775966329be9e1cb5074eda5509b1e6fbdde',
        HEADER: 'b8281a9ba37226a071600d8a9f2d6c9660403bb3b7da2016a3f402f094145212',
        'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db',
    }
    assert {name: hashlib.sha256((TOOL_DIR / name).read_bytes()).hexdigest()
            for name in expected} == expected


@pytest.mark.parametrize('mode', ('absent', 'duplicate', 'tail', 'scratch', 'count'))
def test_injection_snapshot_mandatory_region_refuses_omissions_duplicates_and_changed_limits(mode):
    region = declared_region()
    regions = [region]
    if mode == 'absent':
        regions = []
    elif mode == 'duplicate':
        regions = [region, region]
    elif mode == 'tail':
        regions = [replace(region, callees=((0x22558, 0x2258e),))]
    elif mode == 'scratch':
        regions = [replace(region, return_register=5)]
    else:
        regions = [replace(region, cases=1699)]
    with pytest.raises(AssertionError):
        region_contract(SimpleNamespace(REGIONS=regions))


def test_injection_snapshot_all_unsigned_bytes_copy_with_positive_bounded_sign():
    grammar = Grammar(repo.config())
    assert grammar.validate('to = uint8(from)') is None
    images = [value & 255 for value in range(256)]
    assert images == list(range(256))
    assert all(images[index + 1] > images[index] for index in range(255))
