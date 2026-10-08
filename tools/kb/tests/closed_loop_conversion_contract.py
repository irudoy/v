"""Bind conversion knowledge to independent literals, exact bytes and observers."""
import ast
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
from functools import cache
import hashlib
import json
import re

from kb import compile, repo
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests.closed_loop_publication_contract import evaluate

TOOL = repo.ROOT/'tools/sh-elf-run'
SPEC = 'defs/JK08A.closed-loop-conversion.md'
HEADER = 'stock-jk08a-closed-loop-conversion-cases.h'


@cache
def contracts():
    value = json.loads((TOOL/'closed-loop-conversion-contracts.json').read_text())
    assert value['hardware_ready'] is False
    assert set(value['steps']) == {'1','2','3','4','7'}
    assert len(value['new_owners']) == 14
    return value


def owner_contract(model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    for ref, expected in contracts()['owner_contracts'].items():
        owner = publication.required_owner(model, ref, int(expected['address'],16))
        symbol = owner.symbols['7mfk']
        publication.required_properties(model, owner.props, expected['props'])
        publication.required_properties(model, symbol.props, expected['symbol_props'])
        assert symbol.value('level') == expected['level']
        publication.required_evidence(model, symbol.evidence, expected['evidence'])
        for wanted in expected['links']:
            matches = [link for link in owner.links if
                (link.type,link.to.key,link.slot,link.offset) ==
                (wanted['type'],wanted['to'],wanted['slot'],wanted['offset'])]
            assert len(matches) == 1
            [link] = matches
            assert link.stated >= set(wanted['layouts'])
            assert link.roles >= set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    chain = model.entities[('chain','closed_loop_fuel')]
    assert len(chain.steps) == 19
    for number in (1,2,3,4,7):
        assert publication.normalized(model,chain.steps[number-1]) == contracts()['steps'][str(number)]
    for number, expected in contracts()['held_steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1]) == expected
    assert [contracts()['steps'][str(i)]['sign'] for i in (1,2,3,4,7)] == ['none','none','positive','positive','positive']


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
    assert hashlib.sha256(module.build_fixture(row,image)).hexdigest() == contracts()['fixture_sha256']
    assert sum((end-start)//2 for start,end in row.code_spans) == 823
    assert sum(end-start for start,end in row.code_spans)+sum(size for _,size in row.pools) == 2233
    assert row.cases == len(literals()) == 4338
    assert not row.boundary and not row.register_word_literals
    assert len(row.ram_literals) == 9
    assert tuple(row.ram_word_literals) == ((0x3ef10,0xffff8544,0x7d00,28),(0x3f002,0xffff8560,0x7d40,20))
    assert (row.return_address_offset,row.return_register) == (None,5)
    assert dict(row.constants) == {'EARLY_ONLY':0}


def previous_regions_contract():
    module = publication.stock_module()
    held = contracts()['previous_regions']
    assert len(held) == 76 and len(module.REGIONS) == 77
    assert json.loads(json.dumps([asdict(row) for row in module.REGIONS[:76]])) == held
    for key,name in contracts()['previous_observers'].items():
        assert module.REGION_OBSERVERS[key] == name
    images = {rom:module.stock_image(rom) for rom in {row.rom for row in module.REGIONS[:76]}}
    for row in module.REGIONS[:76]:
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
                raise AssertionError(f'conversion accepts changed byte {at+offset:08x}')


def publication_contract():
    row,_ = region()
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        text = re.sub(r'\s+',' ',(repo.ROOT/path).read_text())
        assert f'One mandatory Region binds 823 instructions, 2233 bound bytes and {row.cases} literal cases' in text
    text = (repo.ROOT/SPEC).read_text()
    assert 'readiness is NO' in text and '160-byte' in text
    assert '4022' in text and '46 zero-coefficient' in text
    assert 'physical units' in text and 'cadence' in text


@cache
def array(name):
    text = (TOOL/HEADER).read_text()
    [body] = re.findall(r'\b'+name+r'\[\]\s*=\s*\{(.*?)\};',text,re.S)
    assert re.fullmatch(r'[\s{},0-9a-fxU]+',body)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    return ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')


def literals():
    return array('samples')


def signed16(value):
    value = int(value)&65535
    return value-65536 if value&32768 else value


def signed32(value):
    return value-(1<<32) if value&(1<<31) else value


def axis(points,value,count):
    index = max((i for i in range(count) if value >= points[i]),default=0)
    fraction = 0 if value <= points[0] or index == count-1 or value == points[index] else int(Fraction(65536*(value-points[index]),points[index+1]-points[index]))
    return index,fraction


def linear(left,right,fraction):
    change = abs(right-left)*fraction//65536
    return left+change if right >= left else left-change


def curve(table,points,value,count):
    index,fraction = axis(points,value,count)
    return linear(table[index],table[index+1],fraction),index,fraction


def surface(table,row_input,column_input):
    r,rf = axis(contracts()['axes']['row'],row_input,8)
    c,cf = axis(contracts()['axes']['column'],column_input,8)
    first = table[8*r+c]
    if cf:
        first = linear(first,table[8*r+c+1],cf)
    if rf:
        second = table[8*(r+1)+c]
        if cf:
            second = linear(second,table[8*(r+1)+c+1],cf)
        first = linear(first,second,rf)
    return first,r,c,rf,cf


def profile_table(profile):
    assert profile in range(3)
    return array('stock_148fa') if profile == 0 else (
        [65535-4095*i for i in range(16)]+[0] if profile == 1 else
        [0 if i%2 == 0 else 65535 for i in range(17)])


def literal_contract(rows=None):
    rows = literals() if rows is None else rows
    counts = Counter()
    domains = {key:set() for key in ('mode','permits','coefficient','coefficient_input_byte','row','column','profile')}
    axes = contracts()['axes']
    for row in rows:
        assert len(row) == 38
        (x1,x2,speed_gate,coefficient_input,row_input,load,adjust1,adjust2,
         mode,permits,offset,midpoint,coefficient_override,map_override,profile,entry_t,coefficient,
         selected,z,output,maps,lookups,offsets,sums,difference,scaled,candidates,
         workspace_quotient,last_fraction,divided,exit_q,admitted,coefficient_fraction,
         coefficient_left,coefficient_next,fractions,curve_left,curve_next) = row
        assert all(value in range(65536) for value in row[:8]+[offset,midpoint])
        assert mode in range(256) and permits in range(256) and entry_t in (0,1)
        assert coefficient_override in range(257) and map_override in range(65537)
        assert selected == ([x1,x2] if mode&8 else [(2*x1)&65535,(2*x2)&65535])
        ct = array('stock_12292').copy()
        if coefficient_override < 256:
            ct[:16] = [coefficient_override]*16
        expected_coefficient,ci,cf = curve(ct,axes['coefficient'],coefficient_input//256,16)
        assert [coefficient,coefficient_fraction,coefficient_left,coefficient_next] == [expected_coefficient,cf,ct[ci],ct[ci+1]]
        d = [min(32767,max(-32768,value-midpoint)) for value in selected]
        q = [int(Fraction(128*value,coefficient)) for value in d] if coefficient else []
        expected_scaled = [min(32767,max(-32768,value)) for value in q] if coefficient else [32767 if value >= 0 else -32768 for value in d]
        assert list(map(signed32,difference)) == d
        assert list(map(signed32,scaled)) == expected_scaled
        expected_candidates = [midpoint+value for value in expected_scaled]
        assert list(map(signed32,candidates)) == expected_candidates
        assert signed32(workspace_quotient) == (q[1] if coefficient else selected[1]-midpoint)
        expected_admitted = int(5606 < speed_gate < 65280 and (coefficient_input > 65024 or coefficient_input < 51264) and coefficient > 0)
        assert admitted == expected_admitted
        assert z == ([max(0,value)&65535 for value in expected_candidates] if admitted else selected)
        surfaces = [surface(array('stock_'+name) if map_override == 65536 else [map_override]*64,row_input,load) for name in ('c10e','c18e')]
        assert maps == [packet[0] for packet in surfaces]
        table = profile_table(profile)
        curves = [curve(table,axes['conversion'],value,16) for value in z]
        assert lookups == [packet[0] for packet in curves]
        assert fractions == [packet[2] for packet in curves]
        assert curve_left == [table[packet[1]] for packet in curves]
        assert curve_next == [table[packet[1]+1] for packet in curves]
        assert last_fraction == fractions[1]
        expected_offsets = [signed16(offset) if permits&(1<<bank) else 0 for bank in range(2)]
        assert list(map(signed32,offsets)) == expected_offsets
        expected_sums = [lookups[b]+maps[b]+signed16((adjust1,adjust2)[b])+expected_offsets[b] for b in range(2)]
        assert list(map(signed32,sums)) == expected_sums
        assert output == [min(65535,max(0,value-32768)) for value in expected_sums]
        divisions = [fraction for packet in surfaces for fraction in packet[3:] if fraction]
        if cf:
            divisions.append(cf)
        if coefficient:
            divisions.append(abs(q[1]))
        divisions += [fraction for fraction in fractions if fraction]
        assert [divided,exit_q] == [int(bool(divisions)),1-(divisions[-1]&1) if divisions else 0]
        counts['admitted'] += admitted
        counts['coefficient_zero'] += int(coefficient == 0)
        domains['mode'].add(mode)
        domains['permits'].add(permits)
        domains['coefficient'].add(coefficient_override)
        domains['coefficient_input_byte'].add(coefficient_input//256)
        domains['row'].add(surfaces[0][1])
        domains['column'].add(surfaces[0][2])
        domains['profile'].add(profile)
    assert len(rows) == 4338 and counts == {'admitted':4022,'coefficient_zero':46}
    assert domains['mode'] == domains['permits'] == domains['coefficient_input_byte'] == set(range(256))
    assert set(range(256)) <= domains['coefficient']
    assert domains['row'] == domains['column'] == set(range(8))
    assert domains['profile'] == set(range(3))
    assert rows[2][18] == [31719,31719]
    return dict(counts)


def formula_contract():
    axes = contracts()['axes']
    notes = contracts()['formulas']
    rom16_axis = {0x15d20+2*i:value for i,value in enumerate(axes['conversion'])}
    for row in literals():
        (x1,x2,gate,coefficient_input,_,_,adjust1,adjust2,mode,_,_,midpoint,
         _,_,profile,_,coefficient,selected,z,output,maps,lookups,offsets,_,difference,scaled,*_) = row
        rom16 = {0x8f98:midpoint,0x95c6:5606,0x9384:65024,0x9386:51264,**rom16_axis}
        ram16 = {0xffff110a:gate,0xffff4524:coefficient_input}
        for bank,raw in enumerate((x1,x2)):
            ram16.update({0xffff267c+2*bank:raw,0xffff2882+2*bank:raw,
                0xffff322c+2*bank:z[bank],0xffff8544+14-2*bank:maps[bank],
                0xffff45a0+2*bank:(adjust1,adjust2)[bank],0xffff2b54+2*bank:offsets[bank]&65535})
        table = profile_table(profile)
        def lookup(address,point):
            assert address == 0x148fa
            return curve(table,axes['conversion'],point,16)[0]
        for bank in range(2):
            env = evaluate(notes['1'],source=coefficient,x=bank,RAM16=ram16,ROM16=rom16,
                ROM8={0x8978:mode},sat_s16=lambda value:min(32767,max(-32768,int(value))))
            assert [env['X'],env['D'],env['Q'],env['to']] == [selected[bank],signed32(difference[bank]),signed32(scaled[bank]),z[bank]]
            env = evaluate(notes['2'],source=z[bank],ROM16=rom16)
            _,index,fraction = curve(table,axes['conversion'],z[bank],16)
            assert [env['I'],env['F'],env['to']] == [index,fraction,index]
            for number,source in ((3,lookups[bank]),(4,maps[bank]),(7,(adjust1,adjust2)[bank])):
                env = evaluate(notes[str(number)],source=source,x=bank,RAM16=ram16,int16=signed16,lookup=lookup)
                assert env['to'] == output[bank]
