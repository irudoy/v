"""Bind the complete bounded adjustment entry to exact bytes and raw-state literals."""
import ast
from collections import Counter
from dataclasses import asdict
from functools import cache
import hashlib
import json
import re

from kb import compile,repo
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests.closed_loop_publication_contract import evaluate
from tools.kb.tests.closed_loop_adjustment_model import evaluate as raw_state,signed
from tools.kb.tests.closed_loop_adjustment_cpu import expectations

TOOL = repo.ROOT/'tools/sh-elf-run'
SPEC = 'defs/JK08A.closed-loop-adjustment.md'
HEADER = 'stock-jk08a-closed-loop-adjustment-cases.h'

@cache
def contracts():
    value = json.loads((TOOL/'closed-loop-adjustment-contracts.json').read_text())
    assert value['hardware_ready'] is False
    assert set(value['steps']) == {'5','6'}
    assert len(value['new_owners']) == 53
    return value

def owner_contract(model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    for ref,expected in contracts()['owner_contracts'].items():
        owner = publication.required_owner(model,ref,int(expected['address'],16))
        symbol = owner.symbols['7mfk']
        publication.required_properties(model,owner.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        assert symbol.value('level') == expected['level']
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        for wanted in expected['links']:
            matches = [link for link in owner.links if (link.type,link.to.key,link.slot,link.offset) ==
                (wanted['type'],wanted['to'],wanted['slot'],wanted['offset'])]
            assert len(matches) == 1
            [link] = matches
            assert link.stated >= set(wanted['layouts'])
            assert link.roles >= set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    chain = model.entities[('chain','closed_loop_fuel')]
    assert len(chain.steps) == 19
    for number in (5,6):
        assert publication.normalized(model,chain.steps[number-1]) == contracts()['steps'][str(number)]
    for number,expected in contracts()['held_steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1]) == expected
    assert [contracts()['steps'][str(i)]['sign'] for i in (5,6)] == ['positive','negative']

def region():
    module = publication.stock_module()
    [row] = [item for item in module.REGIONS if item.key == contracts()['region']['key']]
    assert json.loads(json.dumps(asdict(row))) == contracts()['region']
    assert module.REGION_OBSERVERS[row.key] == contracts()['observer']
    return row,module

def stock_bytes(image):
    for at,raw in contracts()['slices']:
        data = bytes.fromhex(raw)
        assert image[at:at+len(data)] == data,f'{at:08x}'

def registered_stock_contract(image):
    row,module = region()
    stock_bytes(image)
    for name,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((TOOL/name).read_bytes()).hexdigest() == digest,name
    for name,digest in contracts()['reference_sources_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest() == digest,name
    assert hashlib.sha256(module.build_fixture(row,image)).hexdigest() == contracts()['fixture_sha256']
    assert sum((end-start)//2 for start,end in row.code_spans) == 1231
    assert sum(end-start for start,end in row.code_spans)+sum(size for _,size in row.pools) == 2678
    assert row.cases == len(literals()) == 10286
    assert not row.boundary and not row.register_word_literals
    assert len(row.ram_literals) == 8
    assert tuple(row.ram_word_literals) == ((0xa101c,0xffff977c,0x7e00,122),)
    assert (row.return_address_offset,row.return_register) == (None,5)
    assert dict(row.constants) == {'EARLY_ONLY':0}
    for name,at in (('00015d00',0x15d00),('00015d10',0x15d10)):
        assert contracts()['stock_tables'][name] == [int.from_bytes(image[at+2*i:at+2*i+2],'big') for i in range(9)]

def previous_regions_contract():
    module = publication.stock_module()
    held = contracts()['previous_regions']
    assert len(held) == 77 and len(module.REGIONS) == 81
    assert json.loads(json.dumps([asdict(row) for row in module.REGIONS[:77]])) == held
    for key,name in contracts()['previous_observers'].items():
        assert module.REGION_OBSERVERS[key] == name
    images = {rom:module.stock_image(rom) for rom in {row.rom for row in module.REGIONS[:77]}}
    for row in module.REGIONS[:77]:
        assert hashlib.sha256(module.build_fixture(row,images[row.rom])).hexdigest() == contracts()['previous_fixtures'][row.key]

def all_bound_mutations_fail(image):
    for at,raw in contracts()['slices']:
        for offset in range(len(bytes.fromhex(raw))):
            changed = bytearray(image)
            changed[at+offset] ^= 1
            try:
                stock_bytes(changed)
            except AssertionError:
                pass
            else:
                raise AssertionError(f'adjustment accepts changed byte {at+offset:08x}')

def publication_contract():
    row,_ = region()
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        text = re.sub(r'\s+',' ',(repo.ROOT/path).read_text())
        assert f'One mandatory Region binds 1231 instructions, 2678 bound bytes and {row.cases} literal cases' in text
    text = (repo.ROOT/SPEC).read_text()
    assert 'readiness is NO' in text and '192-byte' in text
    assert '512-case admission product' in text and 'full Cartesian product' in text
    assert 'physical units' in text and 'cadence' in text
    assert 'Selector-3 constants retain stock zero' in text
    assert 'ffff29e2' in text and 'requires its own whole-path evidence' in text

def numeric_array(body):
    """Decode ordinary numeric lists without constructing a Python AST.

    The original literal reader preserves rare accepted forms and diagnostic
    failures. Deep lists retain its nesting boundary instead of JSON's limit.
    """
    assert re.fullmatch(r'[\s{},0-9a-fxU]+',body)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    original = '['+body.replace('{','[').replace('}',']')+']'
    if re.search(r'[\[,]\s*,',original):
        return ast.literal_eval(original)
    depth = 0
    for brace in re.finditer(r'[{}]',body):
        depth += 1 if brace[0] == '{' else -1
        if depth > 100:
            return ast.literal_eval(original)
    try:
        text = re.sub(r'\b0x[0-9a-f]+\b',lambda value:str(int(value[0],16)),original)
        return json.loads(re.sub(r',(\s*\])',r'\1',text))
    except (ValueError, RecursionError):
        return ast.literal_eval(original)

@cache
def array(name):
    text = (TOOL/HEADER).read_text()
    [body] = re.findall(r'\b'+name+r'\[\]\s*=\s*\{(.*?)\};',text,re.S)
    return numeric_array(body)

def literals():
    return array('samples')

def context(row):
    assert len(row) == 17
    masks,extra,control,previous,coordinate,state,up_table,down_table,scalars = row[:9]
    assert len(masks) == 15 and len(extra) == 4 and len(previous) == 2
    assert all(len(bank) == 7 for bank in previous)
    assert all(value in range(256) for value in masks+extra+[control]+previous[0]+previous[1])
    assert len(coordinate) == len(state) == 2 and len(up_table) == len(down_table) == 9 and len(scalars) == 7
    assert all(value in range(65536) for value in coordinate+state+up_table+down_table)
    assert up_table[8] == down_table[0]
    assert scalars[2:6] == [0,0,1,1] and scalars[6] in (0,1)
    signed32 = lambda value:value-(1<<32) if value&(1<<31) else value
    return dict(masks=masks,extra=extra,control=control,previous=previous,coordinate=coordinate,state=state,
        up_table=up_table,down_table=down_table,lower=signed32(scalars[0]),upper=signed32(scalars[1]),
        up_three=scalars[2],down_three=scalars[3],up_four=scalars[4],down_four=scalars[5],entry_t=scalars[6])

def literal_contract(rows=None):
    rows = literals() if rows is None else rows
    outcomes = Counter()
    selectors = [set(),set()]
    mask_domains = [set() for _ in range(15)]
    extra_domains = [set() for _ in range(4)]
    previous_domains = [[set() for _ in range(7)] for _ in range(2)]
    controls = set()
    for index,row in enumerate(rows):
        raw = context(row)
        result = raw_state(raw,index,contracts()['stock_tables'])
        assert row[9:15] == [result[key] for key in
            ('initial_workspace','workspace','output','counters','up_selector','down_selector')]
        cpu = expectations(raw,result)
        expected_cpu = [int(cpu[key] or 0)&0xffffffff for key in
            ('r0','r2','r4_literal','r4_stack_offset','r5','r6','r7_literal','r7_stack_offset',
             'helper_called','last_fraction','divided','exit_q','exit_t')]
        assert row[15] == expected_cpu
        frame = bytearray().join((0xa3b4c5d6+17*i).to_bytes(4,'big') for i in range(48))
        for at,value in cpu['byte_writes']: frame[at] = value
        for at,value in cpu['long_writes']+cpu['nested_writes']: frame[at:at+4] = value.to_bytes(4,'big')
        assert row[16] == list(frame)
        outcomes[tuple(result['admitted'])] += 1
        for direction,target in zip(('up','down'),selectors): target.update(result[direction+'_selector'])
        for domain,value in zip(mask_domains,raw['masks']): domain.add(value)
        for domain,value in zip(extra_domains,raw['extra']): domain.add(value)
        for bank in range(2):
            for field in range(7): previous_domains[bank][field].add(raw['previous'][bank][field])
        controls.add(raw['control'])
    assert len(rows) == 10286
    assert outcomes == {(1,1):9903,(0,1):143,(1,0):15,(0,0):225}
    assert selectors == [set(range(1,5)),set(range(1,5))]
    assert all(domain == set(range(256)) for domain in mask_domains+extra_domains+previous_domains[0]+previous_domains[1]+[controls])

def formula_contract(model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    notes = [model.entities[('chain','closed_loop_fuel')].steps[i-1]['note'] for i in (5,6)]
    checks = selected = 0
    for index,row in enumerate(literals()):
        raw = context(row)
        result = raw_state(raw,index,contracts()['stock_tables'])
        ram8 = {0xffff977c+i:value for i,value in enumerate(result['workspace'])}
        ram16 = {0xffff45a0+2*bank:raw['state'][bank] for bank in range(2)}
        ram16.update({0xffff97a4+2*bank:result['up_step'][bank] for bank in range(2)})
        ram16.update({0xffff97a0+2*bank:result['down_step'][bank] for bank in range(2)})
        rom16 = {0x8e7c:raw['lower']&65535,0x8e7e:raw['upper']&65535}
        for bank in range(2):
            for note,direction in zip(notes,('up','down')):
                env = evaluate(note,source=result[direction+'_step'][bank],x=bank,
                    RAM8=ram8,RAM16=ram16,ROM16=rom16,int16=signed,
                    sat_s16=lambda value:min(32767,max(-32768,int(value))))
                assert [env['G'],env['I'],int(env['to'])&65535] == [
                    result['admitted'][bank],result['intermediate'][bank],result['output'][bank]]
                checks += 1
                selected += int(result[direction+'_selector'][bank] == 2)
    assert checks == 41144 and selected == 9024
