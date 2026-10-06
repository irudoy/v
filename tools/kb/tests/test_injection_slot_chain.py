"""Bind bounded injection slot arithmetic to byte inputs and real SH-2E execution."""
import ast
import builtins
from collections import Counter
from dataclasses import replace
from functools import cache
import hashlib
import re
from types import SimpleNamespace

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR = repo.ROOT / 'tools/sh-elf-run'
KEY = 'jk08a-injection-slot'
HEADER = 'injection-slot-cases.h'
SOURCE = 'stock_jk08a_injection_slot.s'
HARNESS = 'harness-stock-jk08a-injection-slot.c'
PATH = 'tools/kb/tests/test_injection_slot_chain.py'
SECTION = 'Bounded injection slot construction'
VIA = ['amigurumi-dormouse/fn']
FORMULA = ('F = (uint8(ffff8513)>>5)&1; L = F*uint8(ffff2364)+(1-F)*3; '
           'd = uint8(ffff11de)-1-L; to = uint8(d+6*min(1,max(0,-d)))')
SYMBOLS = (('CYLINDER', 'knock_channel_primary/ram', 0xffff11de),
           ('LEAD', 'fabulous-koel/ram', 0xffff2364),
           ('MODE', 'flawless-silkworm/ram', 0xffff8513),
           ('COUNTER', 'arcane-chinchilla/ram', 0xffff4555),
           ('HISTORY', 'lime-caracara/ram', 0xffff1526),
           ('SLOT', 'acrid-bonobo/ram', 0xffff20b4))
SLICES = ((0x54a64, bytes.fromhex('64e08453644c34238d02670374012e40d270d871842a600c028c642c6283720d052ce20134268f0575ffe6017601420036428bfbd369905b063c262b03646073c8208b01a004e903d465e034094c699c6053c90f309840118d0162037206d6616023c0c0')),
          (0x2268e, bytes.fromhex('0001020304050602040810200100010203040506')),
          (0x54b52, bytes.fromhex('8510029a')),
          (0x54c30, bytes.fromhex('ffff1ff4ffff4555ffff11d40002268effff128cffff2330ffff24c8')))
STATIC = ((0x54a56, bytes.fromhex('d076401e7fe8de75e2ff9577622c')),)


def stock_contract(data):
    for address, expected in (*SLICES, *STATIC):
        assert data[address:address + len(expected)] == expected, f'{address:08x}'
    word = lambda address: int.from_bytes(data[address:address + 2], 'big')
    for address in range(0x54a64, 0x54ac8, 2):
        instruction = sh2.decode(word(address), address)
        assert instruction.flow not in ('call', 'return')
        if instruction.flow == 'branch':
            assert 0x54a64 <= instruction.target < 0x54ac8
    assert word(0x54abc) == 0x8d01 and word(0x54abe) == 0x6203
    assert word(0x54ac0) == 0x7206 and word(0x54ac6) == 0xc0c0


def declared_region():
    return publication.stock_module().Region(
        key=KEY, rom='JK08A', source=SOURCE, harness=HARNESS,
        start=0x54a64, end=0x54ac8,
        pools=((0x2268e, 20), (0x54b52, 4), (0x54c30, 28)),
        ram_literals=(0x54c38, 0x54c40, 0x54c44, 0x54c48), cases=8508,
        symbols=tuple((macro, owner) for macro, owner, _ in SYMBOLS),
        constants=(('EARLY_ONLY', 0),))


def region_contract(module):
    matches = [region for region in module.REGIONS if region.key == KEY]
    assert len(matches) == 1, 'The mandatory bounded injection-slot Region is absent or duplicated'
    [region] = matches
    assert region == declared_region() and type(region.cases) is int
    return region


@cache
def literals():
    text = (TOOL_DIR / HEADER).read_text()
    [body] = re.findall(r'slot_cases\[\] = \{(.*?)\n\};', text, re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    rows = ast.literal_eval('[' + body.replace('{', '[').replace('}', ']') + ']')
    assert all(len(row) == 13 and len(row[11]) == len(row[12]) == 15 for row in rows)
    [count] = re.findall(r'^#define SLOT_CASE_COUNT (\d+)U$', text, re.M)
    assert len(rows) == int(count) == 8508
    return rows


@cache
def program(formula=FORMULA):
    assert Grammar(repo.config()).validate(formula) is None
    text = re.sub(r'\bffff[0-9a-f]{4}\b', lambda item: 'memory[0x' + item[0] + ']', formula)
    return builtins.compile(text, '<bounded injection slot arithmetic>', 'exec')


def evaluate(row, formula=FORMULA):
    cylinder, lead, flags = row[:3]
    values = {'memory': {0xffff11de: cylinder, 0xffff2364: lead, 0xffff8513: flags},
              'uint8': lambda value: value & 255, 'min': min, 'max': max}
    exec(program(formula), {'__builtins__': {}}, values)
    return values


def vector_contract(row):
    c, lead, flags, count, history, variant, t, slot, next_count, next_history, exit_t, incoming, expected = row
    assert 1 <= c <= 6 and all(0 <= value <= 255 for value in (lead, flags, count, history))
    assert variant in (0, 1) and t in (0, 1)
    value = evaluate(row)
    assert value['to'] == slot
    assert next_count == min(255, count + 1) and next_history == history | (1 << (c - 1))
    assert exit_t == int(value['d'] >= 0)
    mask = 0xffffffff
    entry = [((0xa9876543 + i * 0x00130709) if variant
              else (0x28765430 + i * 0x01030507)) & mask for i in range(15)]
    entry[2], entry[5], entry[7], entry[14] = 255, 0x01008510, 0x54a64, 0x01004555
    assert incoming == entry
    final = entry.copy()
    raw = value['d'] + 6 * int(value['d'] < 0)
    final[0] = final[2] = raw & mask
    final[3] = 0x0100128c
    final[4] = 0x01002330 if flags & 32 else c
    final[5], final[6] = c - 1, 0x010024c8
    final[7] = flags if flags < 128 else (flags - 256) & mask
    final[8], final[9] = 0x2268e, value['L']
    assert expected == final


def test_injection_slot_stock_bytes_and_branch_delay_slot_match():
    stock_contract(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [at + i for at, span in (*SLICES, *STATIC) for i in range(len(span))])
def test_injection_slot_rejects_each_changed_instruction_or_pool_byte(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        stock_contract(data)


def test_injection_slot_full_literal_matrix_and_exact_formula():
    rows = literals()
    for row in rows:
        vector_contract(row)
    counts = Counter((row[0], row[1], row[5], row[6]) for row in rows[12:6156])
    assert counts == Counter((c, lead, variant, t) for c in range(1, 7)
                            for lead in range(256) for variant in (0, 1) for t in (0, 1))
    assert all(row[2] == 32 for row in rows[12:6156])
    assert len(rows[6156:6204]) == 48 and all(row[2] == 0 for row in rows[6156:6204])
    flags = Counter((row[0], row[1], row[2]) for row in rows[6204:8252])
    assert flags == Counter((c, lead, flags) for c in (1, 6) for lead in (0, 6, 7, 255) for flags in range(256))
    assert [row[3] for row in rows[8252:]] == list(range(256))


def test_injection_slot_modulo_six_has_an_explicit_lead_bound():
    rows = literals()
    assert rows[0][:3] == [1, 7, 32] and rows[0][7] == 255
    assert (1 - 1 - 7) % 6 == 5
    for row in rows:
        result = evaluate(row)
        if result['L'] <= row[0] + 5:
            assert 0 <= row[7] <= 5 and row[7] == (row[0] - 1 - result['L']) % 6
        else:
            assert row[7] >= 7 and row[7] != (row[0] - 1 - result['L']) % 6
    assert all(evaluate(row)['L'] == 3 for row in rows if not row[2] & 32)


@pytest.mark.parametrize('before,after', [('d+6*min(1,max(0,-d))', 'd%6'),
    ('uint8(ffff2364)', 'min(6,uint8(ffff2364))'), ('>>5', '>>4'), ('+(1-F)*3', '+(1-F)*0')])
def test_injection_slot_formula_rejects_modulo_clamping_and_wrong_control(before, after):
    changed = FORMULA.replace(before, after)
    assert changed != FORMULA
    assert any(evaluate(row, changed)['to'] != row[7] for row in literals())


def chain_contract(model):
    chain = model.entities[('chain', 'injection_phase')]
    assert len(chain.steps) == 22
    for index, source in ((14, 'fabulous-koel/ram'), (15, 'knock_channel_primary/ram')):
        expected = {'from': source, 'to': 'acrid-bonobo/ram', 'effect': 'indexes',
                    'sign': 'none', 'via': VIA, 'note': FORMULA,
                    'specs': ['defs/JK08A.fuel.md', 'defs/JK08A.injection.md']}
        assert publication.normalized(model, chain.steps[index]) == expected
        assert Grammar(repo.config()).validate(chain.steps[index]['note']) is None


def owner_contract(model):
    evidence = [{'kind': 'test', 'path': PATH, 'key': 'test_injection_slot_chain_owner_contract'},
                {'kind': 'test', 'path': PATH, 'key': 'test_injection_slot_registered_stock_contract'},
                {'kind': 'spec', 'path': publication.SPEC, 'key': SECTION}]
    for _, owner, address in SYMBOLS:
        entity = publication.required_owner(model, owner, address)
        symbol = entity.symbols['7mfk']
        assert symbol.value('width') == 8 and symbol.value('signed') is False
        notes = symbol.value('note')
        if isinstance(notes, str):
            notes = [notes]
        assert any('selected lead <= c+5' in note and 'upstream producer bounds' in note for note in notes)
        publication.required_evidence(model, symbol.evidence, evidence)
    slot = publication.required_owner(model, 'acrid-bonobo/ram', 0xffff20b4)
    assert slot.props['unit'] == 'slot index'
    assert 'adds 6 once' in slot.props['summary'] and 'lead <= 6' in slot.props['summary']
    for kind, target in [('input', 'fabulous-koel/ram'), ('input', 'knock_channel_primary/ram'),
                         ('input', 'flawless-silkworm/ram'), ('writer', VIA[0])]:
        [link] = [link for link in slot.links if link.type == kind and link.to.key == target]
        assert link.slot is None and link.offset is None and link.stated == {'7mfk'}
        assert publication.normalized(model, link.props['via']) == VIA
        assert link.props['relies'] == 'structure' and link.props['supports'] == 'identity'
        publication.required_evidence(model, link.evidence, evidence)
    function = publication.required_owner(model, VIA[0], 0x54a44)
    assert 'selected lead <= c+5' in function.props['summary']
    assert '(ffff11de - 1 - lead) mod 6' not in function.props['summary']
    [selector] = [link for link in function.links
                  if link.type == 'selector' and link.to.key == 'flawless-silkworm/ram']
    assert selector.slot == 'bit5' and selector.stated == {'7mfk'}
    assert publication.normalized(model, selector.props['via']) == VIA
    publication.required_evidence(model, selector.evidence, evidence)
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
    for phrase in ('6144 enabled-lead contexts', '48 disabled-lead contexts',
                   '2048 full-control-byte contexts', '256 counter-byte contexts',
                   '12 early contexts', 'R2=255', 'R5=ffff8510', 'R14=ffff4555',
                   'GBR=ffff1ff4', 'lead <= c+5', 'lead <= 6', 'stores 255',
                   'four RAM literal aliases', 'hardware reachability', 'steps 15 and 16'):
        assert phrase.lower() in text.lower()
    grammar = Grammar(repo.config())
    indices = [i + 1 for i, step in enumerate(model.entities[('chain', 'injection_phase')].steps)
               if grammar.validate(step['note']) is None
               and publication.normalized(model, step['to']) == 'acrid-bonobo/ram']
    assert indices == [15, 16]
    assert f'The {len(indices)} arithmetic records' in text


def test_injection_slot_chain_owner_contract():
    owner_contract(compile.cached(repo.ROOT))


def test_injection_slot_registered_stock_contract():
    module = publication.stock_module()
    region = region_contract(module)
    data = module.stock_image('JK08A')
    stock_contract(data)
    assert module.harness_defines(region, data) == {
        'REGION_ENTRY': region.start, 'EARLY_ONLY': 0,
        **{macro: address for macro, _, address in SYMBOLS}}
    fixture = module.build_fixture(region, data)
    assert fixture[region.start:region.end] == data[region.start:region.end]
    for address in region.ram_literals:
        expected = module.base_verifier.alias_high_ram(int.from_bytes(data[address:address+4], 'big'))
        assert fixture[address:address+4] == expected.to_bytes(4, 'big')


@pytest.mark.parametrize('kind', ['missing', 'duplicate', 'pool', 'aliases', 'extent', 'count', 'scratch'])
def test_injection_slot_rejects_incomplete_or_changed_region(kind):
    region = declared_region()
    regions = [region]
    if kind == 'missing':
        regions = []
    elif kind == 'duplicate':
        regions += [region]
    else:
        changes = {'pool': {'pools': region.pools[:-1]},
                   'aliases': {'ram_literals': region.ram_literals[:-1]},
                   'extent': {'end': region.end - 2}, 'count': {'cases': 8507},
                   'scratch': {'return_address_offset': 24, 'return_register': 7}}
        regions = [replace(region, **changes[kind])]
    with pytest.raises(AssertionError):
        region_contract(SimpleNamespace(REGIONS=regions))


@pytest.mark.parametrize('path', [publication.SPEC, 'tools/sh-elf-run/README.md'])
def test_injection_slot_published_contract_matches_the_executed_fixture(path):
    publication_contract(publication.section(path, SECTION), compile.cached(repo.ROOT))


def test_injection_slot_execution_inputs_and_shared_invocation_remain_exact():
    expected = {
        SOURCE: 'b4f6d337308667c4dfb18062ea396e90897efc17d35c7a4483e16cd67e8a4637',
        HARNESS: 'c51a122f1e4d151dc769c1d574a240fc950cab4dc7b60bb7fae46ec97efbbddd',
        HEADER: 'd52663f0b64775577ca4380bff9d0d30435e43994af2770b53a26aa20fcaf2e7',
        'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db',
    }
    assert {name: hashlib.sha256((TOOL_DIR / name).read_bytes()).hexdigest()
            for name in expected} == expected
    driver = (TOOL_DIR / HARNESS).read_text()
    assert '#define SLOT_ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : SLOT_CASE_COUNT)' in driver
    assert 'i < SLOT_ACTIVE_CASE_COUNT' in driver and 'completed != SLOT_ACTIVE_CASE_COUNT' in driver
    assert 'ARRAY_SIZE(slot_cases) != SLOT_CASE_COUNT' in driver
    assert 'i < 65536U' in driver and 'out.frame_after, expected_frame' in driver


@pytest.mark.parametrize('field,value', [('note', 'to = (uint8(ffff11de)-1)%6'),
    ('sign', 'positive'), ('effect', 'copies'), ('via', []), ('specs', [])])
def test_injection_slot_chain_rejects_modulo_sign_path_and_missing_specification(field, value):
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'injection_phase')]
    changed = replace(chain, steps=[dict(step) for step in chain.steps])
    changed.steps[14][field] = value
    proxy = SimpleNamespace(entities={('chain', 'injection_phase'): changed}, meaning_of=model.meaning_of)
    with pytest.raises(AssertionError):
        chain_contract(proxy)
