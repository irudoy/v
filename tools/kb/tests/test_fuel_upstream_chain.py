"""Bind upstream equations, exact instructions, literal observations and owned facts."""
from dataclasses import asdict
from functools import cache
import hashlib,json,re,sys
from pathlib import Path
import pytest
from kb import compile as kb_compile,repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR=repo.ROOT/'tools/sh-elf-run'
PATH='tools/kb/tests/test_fuel_upstream_chain.py'
SPEC='Upstream fuel pulse calculations'

@cache
def contracts():return json.loads((TOOL_DIR/'fuel-upstream-contracts.json').read_text())

def regions(module):
    wanted={row['key']:row for row in contracts()['regions']}
    selected={row.key:row for row in module.REGIONS if row.key in wanted}
    assert len(selected)==len(wanted)==11
    for key,row in selected.items():
        assert json.loads(json.dumps(asdict(row)))==wanted[key]
        assert type(row.cases) is int and row.cases>0
        assert dict(row.constants)['EARLY_ONLY']==0
    return selected

def owner_contract(model):
    expected_contracts=contracts()['owner_contracts']
    assert expected_contracts and set(contracts()['required_owners'])==set(expected_contracts)
    for ref,expected in expected_contracts.items():
        owner=publication.required_owner(model,ref,int(expected['address'],16));symbol=owner.symbols['7mfk']
        publication.required_properties(model,owner.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        assert symbol.name==expected['symbol_name'] and symbol.value('level')==expected['level']
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        if 'ledger' in expected:
            markers=[items for kind,name,items,_ in model.stash.get('ledger_rows',())
                if kind==owner.kind and name==owner.name]
            assert len(markers)==1 and markers[0]==expected['ledger']
        for wanted in expected['links']:
            matches=[row for row in owner.links if row.type==wanted['type'] and row.to.key==wanted['to']
                and row.slot==wanted['slot'] and row.offset==wanted['offset']]
            assert len(matches)==1
            [link]=matches
            assert link.stated>=set(wanted['layouts']) and link.roles>=set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    for ref,kind,target in contracts()['removed_links']:
        owner=next(row for row in model.meanings if row.key==ref)
        assert not any(link.type==kind and link.to.key==target for link in owner.links)
    chain=model.entities[('chain','fuel_pulse')]
    assert len(chain.steps)==26 and len(contracts()['steps']['fuel_pulse'])==16
    for number,wanted in contracts()['steps']['fuel_pulse'].items():
        step=publication.normalized(model,chain.steps[int(number)-1])
        assert step['note']==wanted['formula'] and step['via']==wanted['via'] and step['sign']==wanted['sign']
        assert step['specs']==['defs/JK08A.fuel.md']
        assert Grammar(repo.config()).validate(step['note']) is None

def stock_contract(image):
    for address,hex_bytes in contracts()['slices']:
        span=bytes.fromhex(hex_bytes)
        assert image[address:address+len(span)]==span,f'{address:08x}'

def harness_contract(region,text,tool_dir=TOOL_DIR):
    assert dict(region.constants)['EARLY_ONLY']==0
    [name]=re.findall(r'^#include "([^"]+-cases.h)"$',text,re.M)
    header=(tool_dir/name).read_text()
    [count]=re.findall(r'^#define [A-Z_]+CASE_COUNT (\d+)U$',header,re.M)
    assert int(count)==region.cases
    [body]=re.findall(r'[a-z_]+_cases\[\]\s*=\s*\{(.*?)\n\};',header,re.S)
    rows=[line.strip() for line in body.splitlines() if line.strip()]
    assert len(rows)==region.cases and all(re.fullmatch(r'[{}0-9a-fxU, ]+',line) for line in rows)
    assert 'ACTIVE_CASE_COUNT' in text and 'completed' in text
    assert '76U' in text and '192' in text
    assert 'RAM_WORDS' in text or '65536' in text

def test_fuel_upstream_owner_contract():owner_contract(kb_compile.cached(repo.ROOT))

def test_fuel_upstream_stock_regions_contract(jk08a_stock_bytes):
    module=publication.stock_module();selected=regions(module);stock_contract(jk08a_stock_bytes)
    for path,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest()==digest,path
    for key,row in selected.items():
        assert hashlib.sha256(module.build_fixture(row,jk08a_stock_bytes)).hexdigest()==contracts()['fixtures'][key]
        harness_contract(row,(TOOL_DIR/row.harness).read_text())
    assert {key:module.REGION_OBSERVERS[key] for key in contracts()['observers']}==contracts()['observers']

def test_fuel_upstream_every_prior_region_and_fixture_is_held(jk08a_stock_bytes):
    module=publication.stock_module();held=contracts()['held_regions']
    current={row.key:row for row in module.REGIONS if row.key in held}
    assert len(current)==len(held)==60
    images={rom:module.stock_image(rom) for rom in {row.rom for row in current.values()}}
    for key,row in current.items():
        assert json.loads(json.dumps(asdict(row)))==held[key]
        assert hashlib.sha256(module.build_fixture(row,images[row.rom])).hexdigest()==contracts()['held_fixtures'][key]

def test_fuel_upstream_every_bound_byte_mutation_is_rejected(jk08a_stock_bytes):
    for address,hex_bytes in contracts()['slices']:
        for offset in range(len(bytes.fromhex(hex_bytes))):
            changed=bytearray(jk08a_stock_bytes);changed[address+offset]^=1
            with pytest.raises(AssertionError):stock_contract(changed)

def test_fuel_upstream_published_counts_follow_registered_regions():
    selected=regions(publication.stock_module()).values()
    counts=(len(selected),sum((end-start)//2 for row in selected for start,end in row.code_spans),
        sum(sum(end-start for start,end in row.code_spans)+sum(size for _,size in row.pools) for row in selected),
        sum(row.cases for row in selected))
    assert counts==(11,2726,6494,696084)
    for path in ('defs/JK08A.fuel.md','tools/sh-elf-run/README.md'):
        section=(repo.ROOT/path).read_text().split('## '+SPEC,1)[1]
        [published]=re.findall(r'Eleven mandatory Regions bind (\d+) instructions, (\d+) bound bytes\s+and (\d+) literal cases',section)
        assert tuple(map(int,published))==counts[1:]
        published_regions=re.findall(r'^\| [^|]+ \| `([^`]+)` \| (\d+) \|$',section,re.M)
        assert len(published_regions)==11
        assert {key:int(cases) for key,cases in published_regions}=={row.key:row.cases for row in selected}

def test_fuel_upstream_specs_cover_every_chain_member():
    from tools.romviz.architecture import spec_addresses
    model=kb_compile.cached(repo.ROOT);chain=model.entities[('chain','fuel_pulse')]
    required=set()
    for number in contracts()['steps']['fuel_pulse']:
        step=publication.normalized(model,chain.steps[int(number)-1])
        for ref in (step['from'],step['to'],*step['via']):
            name,kind=ref.split('/')
            meaning=next(row for row in model.meanings if row.key==ref)
            required.add(f'{meaning.symbols["7mfk"].key.address:08x}')
    section=(repo.ROOT/'defs/JK08A.fuel.md').read_text().split('## '+SPEC,1)[1]
    assert required<=spec_addresses(section)

def test_fuel_upstream_hardware_and_staged_boundaries_remain_explicit():
    assert contracts()['hardware_ready'] is False
    for path in ('defs/JK08A.fuel.md','tools/sh-elf-run/README.md'):
        section=(repo.ROOT/path).read_text().split('## '+SPEC,1)[1]
        for required in ('staged','SP+12','physical units','cadence','hardware'):
            assert required.lower() in section.lower()
    terminal=(TOOL_DIR/'harness-stock-jk08a-enrichment-terminal.c').read_text()
    assert '192' in terminal and 'RAM_WORDS' in terminal

from math import floor
sys.path.insert(0,str(TOOL_DIR))
import stock_accumulator_model as accumulator_model,stock_transient_pair_model as transient_pair_model,stock_coolant_conditional_model as coolant_conditional_model
import stock_fuel_multiplier_model as fuel_multiplier_model,stock_precursor_model as precursor_model,stock_common_gain_model as common_gain_model
import stock_enrichment_prefix_model as enrichment_prefix_model,stock_enrichment_terminal_model as enrichment_terminal_model
FORMULAS=contracts()['steps']['fuel_pulse']

@cache
def equations(formula):
    output=[]
    for text in formula.split(';'):
        target,expression=text.split('=',1)
        expression=re.sub(r'\b([0-9a-f]{8})\b',r'0x\1',expression)
        expression=re.sub(r'\bfrom\b','source',expression)
        output.append((target.strip(),compile(expression.strip(),'upstream-equation','eval')))
    return output

def evaluate(number,**values):
    def signed(value,bits):
        value=int(value)&((1<<bits)-1)
        return value-(1<<bits) if value&(1<<(bits-1)) else value
    env={'RAM8':{},'RAM16':{},'RAM32':{},'ROM8':{},'ROM16':{},'ROM32':{},
        'uint8':lambda v:int(v)&255,'uint16':lambda v:int(v)&65535,'uint32':lambda v:int(v)&0xffffffff,
        'int8':lambda v:signed(v,8),'int16':lambda v:signed(v,16),'int32':lambda v:signed(v,32),
        'floor':floor,'trunc0':int,'min':min,'max':max,'abs':abs,'prev':0,'x':0,'source':0}
    env.update(values)
    for target,expression in equations(FORMULAS[str(number)]['formula']):
        env[target]=eval(expression,{'__builtins__':{}},env)
    return env['to']

def memory(row,fields):return {0xffff0000+at:row[name] for name,at in fields if at is not None}

def implicit(table,x,step=32):
    if x>=step*(len(table)-1):return table[-1]
    cell,rem=divmod(x,step);left,right=table[cell:cell+2]
    delta=abs(right-left)*rem//step
    return left+delta if right>=left else left-delta

def test_all_prefix_rows_bind_both_indices_and_selected_mixture():
    m=enrichment_prefix_model
    for v in m.matrix():
        cal=m.CALIBRATIONS[v['calibration']]
        byte=memory(v,m.BYTE_INPUTS)
        rom={at+i:cal[name][i] for name,at,size in m.TABLES for i in range(size)}
        rom.update({at:cal[name] for name,at in m.SCALARS})
        def lookup(address,x):
            if address==0xa9aa:return m.surface_lookup(cal,*x)
            if address==0x1214e:return implicit(cal['wide_curve'],x,16)
            assert address==0x12552
            cell,fraction=m.coordinate(cal['correction_axis'],x)
            return m.linear(cal['correction_curve'][cell],cal['correction_curve'][cell+1],fraction)
        args={'RAM8':byte,'ROM8':rom,'lookup':lookup}
        assert evaluate(1,source=v['normalized'],**args)==m.coordinate(cal['column_axis'],v['load_coordinate'])[0]
        assert evaluate(2,source=v['speed'],ROM8=rom)==m.coordinate(cal['row_axis'],v['speed'],4)[0]
        assert evaluate(3,x=(v['speed'],v['load_coordinate']),**args)==v['mixture_byte']

def test_all_terminal_rows_bind_staged_candidate_auxiliary_call_and_output():
    m=enrichment_terminal_model
    for v in m.matrix():
        cal=m.CALIBRATIONS[v['calibration']]
        rom8={at:cal[name] for name,at in m.CAL_BYTE};rom16={at:cal[name] for name,at in m.CAL_WORD}
        args={'RAM8':memory(v,m.BYTE_INPUTS),'RAM16':memory(v,m.WORD_INPUTS),
            'ROM8':rom8,'ROM16':rom16,'lookup':lambda address,x:implicit(cal['curve'],x)}
        assert evaluate(4,source=v['mixture'],x=v['staged'],**args)==v['output_word']

def test_all_multiplier_rows_bind_both_full_publication_views():
    m=fuel_multiplier_model
    for v in m.matrix():
        rom={}
        for name,at,size in m.CALIBRATIONS:
            values=v[name] if isinstance(v[name],tuple) else (v[name],)
            rom.update({at+i:value for i,value in enumerate(values)})
        args={'RAM8':memory(v,m.BYTE_INPUTS),'RAM16':memory(v,m.WORD_INPUTS),'ROM8':rom}
        assert evaluate(5,source=v['mixture'],**args)==v['output']
        assert evaluate(9,source=v['base'],**args)==v['output']

def test_all_coolant_rows_bind_coordinate_and_conditional_publication():
    m=coolant_conditional_model
    for v in m.matrix():
        rom8={};rom16={}
        for name,at,size in m.CALIBRATIONS:
            if isinstance(v[name],tuple):rom8.update({at+i:value for i,value in enumerate(v[name])})
            elif size==1:rom8[at]=v[name]
            else:rom16[at]=v[name]&65535
        args={'RAM8':memory(v,m.BYTE_INPUTS),'RAM16':memory(v,m.WORD_INPUTS),
            'ROM8':rom8,'ROM16':rom16,'lookup':lambda address,x:implicit(v['curve'],x)}
        coordinate=(4*max(0,v['previous_coolant']+v['coolant_offset']))&255
        assert evaluate(6,source=v['previous_coolant'],ROM16=rom16)==coordinate
        assert evaluate(7,**args)==v['output']

def test_all_accumulator_rows_bind_signed_low32_clamp():
    for v in accumulator_model.matrix():
        assert evaluate(8,source=v['coolant'],RAM32={0xffff15f8:v['term']},
            RAM16={0xffff230c:v['conditional']})==v['output']

def test_both_natural_caller_pairs_bind_the_signed_additive():
    for v in transient_pair_model.matrix():
        assert evaluate(12,RAM8={0xffff102c:v['normalized'],0xffff245d:v['flags']},
            RAM16={0xffff1a66:v['term']&65535},ROM8={0x8b40:v['calibration']},
            lookup=lambda address,x:implicit(v['table'],x))==(v['output'] if v['output']<32768 else v['output']-65536)

def test_all_precursor_rows_bind_four_bank_views():
    m=precursor_model
    for v in m.matrix():
        args={'RAM8':memory(v,m.BYTE_INPUTS),'RAM16':memory(v,m.WORD_INPUTS),
            'ROM16':{0x94e8:v['pulse_floor']},'ROM32':{0x96e0:v['cap_numerator']}}
        for bank in range(2):
            for number,key in ((10,'bfs'),(11,'multiplier'),(13,'transient_raw'),(16,'gain')):
                assert evaluate(number,source=v[key],x=bank,**args)==v[f'bank{bank}_output']

def test_all_common_rows_bind_both_curves_and_inactive_retention():
    m=common_gain_model
    prior=int.from_bytes(bytes((0x5d+at*19+(at>>8))&255 for at in (0x165e,0x165f)),'big')
    for v in m.matrix():
        rom8={};rom16={}
        for name,at,size in m.CALIBRATIONS:
            (rom8 if size==1 else rom16)[at]=v[name]
        tables={at:v[name] for name,at,size in m.TABLES}
        args={'RAM8':memory(v,m.BYTE_INPUTS),'RAM16':memory(v,m.WORD_INPUTS),
            'ROM8':rom8,'ROM16':rom16,'lookup':lambda address,x:implicit(tables[address],x,16),'prev':prior}
        for number in (14,15):assert evaluate(number,**args)==(v['gain_word'] if v['active'] else prior)

def test_direction_witnesses_reject_universal_positive_claims():
    assert FORMULAS['8']['sign']=='none'
    first=accumulator_model.case(0,0x7fffbfff,0,0)
    second=accumulator_model.case(1,0x7fffbfff,0,1)
    assert (first['output'],second['output'])==(65535,0)
    m=fuel_multiplier_model
    common={'floor':16384,'old':0,'rates':(0,0),'transition_rates':(0,255,0,0,0,255),'previous_flags':0}
    assert (m.case(0,base=0,**common)['output'],m.case(1,base=65535,**common)['output'])==(4080,0)
    assert FORMULAS['5']['sign']==FORMULAS['9']['sign']=='none'
    assert (evaluate(6,source=63,ROM16={0x5533c:0}),evaluate(6,source=64,ROM16={0x5533c:0}))==(252,0)
    assert FORMULAS['6']['sign']=='none'

def test_mixture_direction_retains_complete_scalar_domains():
    common={'RAM8':{0xffff11ae:0,0xffff2466:0,0xffff24a2:0},'ROM8':{0x8b9b:127,0x8b9f:126}}
    def result(value):return evaluate(3,x=(0,0),lookup=lambda address,x:value if address==0xa9aa else 128,**common)
    assert (result(126),result(127))==(128,127)
    assert FORMULAS['3']['sign']=='none'
