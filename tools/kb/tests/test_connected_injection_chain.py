"""Bind connected raw calculations to exact stock instructions and typed owners."""
import ast
import copy
from dataclasses import asdict,replace
from functools import cache
import hashlib
import importlib
import json
from pathlib import Path
import re

import pytest
from kb import compile as kb_compile,repo,sh2
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR=repo.ROOT/'tools/sh-elf-run'
PATH='tools/kb/tests/test_connected_injection_chain.py'
SPEC='Connected injection calculation and raw scheduling'

@cache
def contracts():
    return json.loads((TOOL_DIR/'injection-chain-contracts.json').read_text())

def regions(module):
    wanted={row['key']:row for row in contracts()['regions']}
    selected={row.key:row for row in module.REGIONS if row.key in wanted}
    assert len(selected)==len(wanted)==10
    for key,row in selected.items():
        assert json.loads(json.dumps(asdict(row)))==wanted[key]
        assert type(row.cases) is int and row.cases>0
        assert dict(row.constants)['EARLY_ONLY']==0
    return selected

def owner_contract(model):
    assert len(contracts()['owner_contracts'])==45
    for ref,expected in contracts()['owner_contracts'].items():
        current=publication.required_owner(model,ref,int(expected['address'],16))
        symbol=current.symbols['7mfk']
        publication.required_properties(model,current.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        if expected['symbol_name'] is not None:assert symbol.name==expected['symbol_name']
        assert set(symbol.former)>={ref.split('/',1)[0] for ref in expected['former']}
        assert symbol.value('level')==expected['level']
        for wanted in expected['statuses']:
            status=current.statuses[wanted['layout']]
            assert status.state==wanted['state']
            publication.required_properties(model,status.props,{key:value for key,value in wanted.items()
                if key not in ('layout','state','evidence')})
            publication.required_evidence(model,status.evidence,wanted.get('evidence',[]))
        markers=[items for kind,name,items,_ in model.stash.get('ledger_rows',())
                 if kind==current.kind and name==current.name]
        assert (markers[0] if markers else [])==expected['ledger']
        for note in expected['notes']:assert note in symbol.props.get('note',[])
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        for wanted in expected['links']:
            matches=[row for row in current.links if row.type==wanted['type'] and row.to.key==wanted['to']
                and row.slot==wanted.get('slot') and row.offset==wanted.get('offset')]
            assert len(matches)==1
            [link]=matches
            assert link.stated>=set(wanted['layouts'])
            assert link.roles>=set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    for name,selected in contracts()['steps'].items():
        chain=model.entities[('chain',name)]
        assert len(chain.steps)==(26 if name=='fuel_pulse' else 22)
        for number,wanted in selected.items():
            step=publication.normalized(model,chain.steps[int(number)-1])
            assert step['note']==wanted['formula'] and step['via']==wanted['via'] and step['sign']==wanted['sign']
            assert step['specs']==['defs/JK08A.fuel.md','defs/JK08A.injection.md']
            assert Grammar(repo.config()).validate(step['note']) is None

def stock_contract(image):
    for address,hex_bytes in contracts()['slices']:
        span=bytes.fromhex(hex_bytes)
        assert image[address:address+len(span)]==span,f'{address:08x}'

def harness_contract(region,text,tool_dir=TOOL_DIR):
    assert dict(region.constants)['EARLY_ONLY']==0
    if region.key.startswith('jk08a-rpm-phase-'):
        assert 'VIEW_KIND' in text and 'ACTIVE_CASE_COUNT' in text
        assert 'completed!=ACTIVE_CASE_COUNT' in text
        return
    headers=re.findall(r'^#include "([^"]+-cases.h)"$',text,re.M)
    assert len(headers)==1
    header=(tool_dir/headers[0]).read_text()
    [count]=re.findall(r'^#define [A-Z_]+CASE_COUNT (\d+)U$',header,re.M)
    assert int(count)==region.cases
    [body]=re.findall(r'[a-z_]+_cases\[\]\s*=\s*\{(.*?)\n\};',header,re.S)
    rows=[line.strip() for line in body.splitlines() if line.strip()]
    assert len(rows)==region.cases
    assert all(re.fullmatch(r'[{}0-9a-fxU, ]+',line) for line in rows)
    assert 'ACTIVE_CASE_COUNT' in text and 'completed' in text
    assert '76U' in text and ('192' in text or '96' in text)
    assert 'RAM_WORDS' in text or '65536' in text

def test_connected_injection_owner_contract():
    owner_contract(kb_compile.cached(repo.ROOT))

def test_connected_stock_regions_contract(jk08a_stock_bytes):
    module=publication.stock_module()
    selected=regions(module)
    stock_contract(jk08a_stock_bytes)
    for path,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest()==digest,path
    for key,row in selected.items():
        assert hashlib.sha256(module.build_fixture(row,jk08a_stock_bytes)).hexdigest()==contracts()['fixtures'][key]
        harness_contract(row,(TOOL_DIR/row.harness).read_text())
    assert {key:module.REGION_OBSERVERS[key] for key in contracts()['observers']}==contracts()['observers']

def test_connected_retains_every_prior_region_and_fixture(jk08a_stock_bytes):
    module=publication.stock_module()
    held=contracts()['held_regions']
    current={row.key:row for row in module.REGIONS if row.key in held}
    assert len(current)==len(held)==50
    for key,row in current.items():
        assert row.register_word_literals==()
        actual=json.loads(json.dumps(asdict(row)));actual.pop('register_word_literals')
        assert actual==held[key]
        assert hashlib.sha256(module.build_fixture(row,module.stock_image(row.rom))).hexdigest()==contracts()['held_fixtures'][key]

def test_connected_every_bound_byte_mutation_is_rejected(jk08a_stock_bytes):
    for address,hex_bytes in contracts()['slices']:
        for offset in range(len(bytes.fromhex(hex_bytes))):
            altered=bytearray(jk08a_stock_bytes);altered[address+offset]^=1
            with pytest.raises(AssertionError):stock_contract(altered)

def test_connected_full_exception_frame_and_hardware_boundary():
    assert contracts()['hardware_ready'] is False
    text=(TOOL_DIR/'harness-stock-jk08a-event-isr.c').read_text()
    assert '192' in text and 'frame_after' in text and 'frame_before' in text
    for path in ('defs/JK08A.fuel.md','defs/JK08A.injection.md','tools/sh-elf-run/README.md'):
        section=(repo.ROOT/path).read_text().split('## '+SPEC,1)[1]
        assert 'SPC/SSR' in section and 'SH-2E exception stack' in section

def test_connected_published_counts_follow_executed_regions():
    selected=regions(publication.stock_module()).values()
    counts=(len(selected),sum((end-start)//2 for row in selected for start,end in row.code_spans),
        sum(sum(end-start for start,end in row.code_spans)+sum(size for _,size in row.pools) for row in selected),
        sum(row.cases for row in selected))
    assert counts==(10,3021,7319,194860)
    for path in ('defs/JK08A.fuel.md','defs/JK08A.injection.md','tools/sh-elf-run/README.md'):
        section=(repo.ROOT/path).read_text().split('## '+SPEC,1)[1]
        [published]=re.findall(r'Ten mandatory Regions bind (\d+) instructions, (\d+) bound bytes\s+and (\d+) literal cases',section)
        assert tuple(map(int,published))==counts[1:]

def test_connected_named_specs_cover_every_member_of_base_bias_step():
    from tools.romviz.architecture import spec_addresses
    required={'ffff340c','ffff192e','00056bd0','00026370','00026740'}
    for path in ('defs/JK08A.fuel.md','defs/JK08A.injection.md'):
        section=(repo.ROOT/path).read_text().split('## '+SPEC,1)[1]
        assert required<=spec_addresses(section)

@pytest.mark.parametrize('model_name,header_name',(
    ('opening','opening-word'),('selector','pulse-selector'),('oneshot','oneshot'),
    ('full_programmer','full-programmer'),('event','event-isr'),
    ('end_angle','end-angle'),('dispatch','full-dispatch')))
def test_connected_literal_headers_match_independent_model(model_name,header_name):
    module=importlib.import_module('stock_injection_'+model_name+'_model')
    args={'end_angle':[contracts()['end_angle_defaults']],
          'dispatch':[contracts()['channel_table']]}.get(model_name,[])
    assert module.header(module.matrix(*args))==(TOOL_DIR/(header_name+'-cases.h')).read_text()

import sys
from math import floor
sys.path.insert(0,str(TOOL_DIR))
import stock_injection_opening_model as opening_model
import stock_injection_selector_model as selector_model
import stock_injection_oneshot_model as oneshot_model
import stock_injection_event_model as event_isr_model
import stock_injection_end_angle_model as end_angle_model
import stock_injection_dispatch_model as full_dispatch_model
FORMULAS=contracts()['steps']

def implicit(table, x):
    if x >= 224:
        return table[7]
    index, part = divmod(x, 32)
    left, right = table[index:index+2]
    distance = abs(right-left)*part//32
    return left+distance if right >= left else left-distance

@cache
def equations(formula):
    output = []
    for text in formula.split(';'):
        target, expression = text.split('=', 1)
        expression = re.sub(r'\b([0-9a-f]{8})\b', r'0x\1', expression)
        expression = re.sub(r'\bfrom\b', 'source', expression)
        output.append((target.strip(), compile(expression.strip(), 'connected-equation', 'eval')))
    return output

def evaluate(chain, number, **values):
    env = {'RAM8': {}, 'RAM16': {}, 'ROM8': {}, 'ROM16': {},
           'uint8': lambda v: int(v)&255, 'uint16': lambda v: int(v)&65535,
           'uint32': lambda v: int(v)&0xffffffff, 'floor': floor,
           'min': min, 'max': max, 'abs': abs, 'prev': 0, 'x': 0, 'source': 0}
    env.update(values)
    for target, expression in equations(FORMULAS[chain][str(number)]['formula']):
        env[target] = eval(expression, {'__builtins__': {}}, env)
    return env['to']

def test_opening_all_12556_exact_literal_states():
    for battery, slope, additive, *rest in opening_model.matrix():
        assert evaluate('fuel_pulse', 18, source=battery,
            ROM8={0x84f6:slope, 0x8c9e:additive}) == rest[4]

def test_selector_all_7302_modes_and_six_word_publications():
    for row in selector_model.matrix():
        byte = {0xffff418c:row['flag_a'], 0xffff24a0:row['flag_b']}
        word = {address:row[key] for address,key in ((0xffff23aa,'opening'),
            (0xffff2388,'threshold'),(0xffff2386,'start'),(0xffff238a,'stopped'),
            (0xffff238c,'floor1'),(0xffff238e,'floor2'),(0xffff2392,'floor4'),(0xffff2390,'running'))}
        for channel in range(6):
            assert evaluate('fuel_pulse',24,x=row['argument'],source=row['snapshot'][channel],
                RAM8=byte,RAM16=word,ROM16={0x94e8:row['calibration']}) == row['output'][channel]

def test_oneshot_all_8012_masks_and_six_counter_words():
    for row in oneshot_model.matrix():
        byte = {0xffff4184:row['enable'],0xffff22e0:row['inhibit'],
                0xffff1935:row['history'],0xffff4251:row['diagnostic']}
        word = {0xffff23aa:row['opening'],0xfffff666:row['started']}
        for channel in range(6):
            assert evaluate('fuel_pulse',25,x=[row['argument'],channel],
                source=row['durations'][channel],prev=row['counters'][channel],RAM8=byte,RAM16=word) == row['output'][channel]
        assert evaluate('fuel_pulse',26,source=row['argument'],prev=row['started'],RAM8=byte) == row['expected_started']

def test_oneshot_wrapping_result_does_not_claim_monotonicity():
    byte={0xffff4184:128,0xffff22e0:0,0xffff1935:0,0xffff4251:0}
    word={0xffff23aa:0,0xfffff666:0}
    first=evaluate('fuel_pulse',25,x=[1,0],source=1,prev=65532,RAM8=byte,RAM16=word)
    second=evaluate('fuel_pulse',25,x=[1,0],source=2,prev=65532,RAM8=byte,RAM16=word)
    assert (first,second)==(65535,2)
    assert FORMULAS['fuel_pulse']['25']['sign']=='none'

def test_rpm_all_65536_word_inputs_bind_the_composed_conversion():
    for source in range(65536):
        work_word=source//8
        work_byte=min(255,work_word//16)
        assert evaluate('injection_phase',1,source=source)==work_byte

def test_end_angle_all_4056_states_bind_coordinates_and_selected_publication():
    defaults=contracts()['end_angle_defaults']
    paths=set()
    for row in end_angle_model.matrix(defaults):
        paths.add(row['path'])
        byte={0xffff0000+at:row['output'][name] for name,at in end_angle_model.BYTE_RAM}
        table={0x12302:row['base_curve'],0x1230a:row['conditional_curve']}
        args={'RAM8':byte,'ROM8':{0x8729:row['override']},'lookup':lambda address,x:implicit(table[address],x)}
        for point in (2,3):
            assert evaluate('injection_phase',point,source=row['rpm'])==min(7,row['rpm']//32)
        if row['path']==6:
            assert evaluate('injection_phase',4,**args)==row['output']['angle']
            assert evaluate('injection_phase',6,source=row['output']['bias'],**args)==row['output']['angle']
        if row['path']==4:
            assert evaluate('injection_phase',5,**args)==row['output']['angle']
        if row['path'] in (4,5,6):
            for point in (7,8):
                assert evaluate('injection_phase',point,**args)==row['output']['angle']
    assert paths=={1,2,4,5,6}

def test_full_dispatch_all_3864_states_bind_pending_and_wrapped_argument():
    proof={'channel_table':contracts()['channel_table']}
    paths=set()
    for row in full_dispatch_model.matrix(proof['channel_table']):
        paths.add(row['path'])
        old=row['old_memory']
        byte={0xffff0000+at:old[name] for name,at in full_dispatch_model.BYTE_RAM}
        if row['path']:
            flag=row['event_flag']
            if old['event_source']&32 and not flag&16:
                flag|=240
                lead=old['lead_source'] if row['event_flag']&32 else 3
                byte[0xffff221d]=lead
                byte[0xffff221e]=(row['output']['slot']-1)&255 if row['output']['slot'] else 5
            byte[0xffff8513]=flag
            rom={0x2268e+i:value for i,value in enumerate(proof['channel_table'])}
            assert evaluate('injection_phase',17,source=row['output']['slot'],RAM8=byte,ROM8=rom)==row['output']['pending']
            assert evaluate('injection_phase',18,source=old['angle'],prev=old['offset'],RAM8=byte,
                RAM16={0xffff22bc:old['period']})==row['output']['offset']
    assert paths=={0,1,2,3}

def test_isr_all_7254_states_bind_explicit_publication_with_staged_history():
    for row in event_isr_model.matrix():
        selection=row['selection']
        pending=selection['pending']
        history=row['history']&(~pending&255)
        if row['release'] and selection['inhibit']:
            history|=pending
        byte={0xffff4184:row['enable'],0xffff2228:pending,0xffff22e0:selection['inhibit'],
              0xffff1935:history,0xffff4251:row['diagnostic']}
        word={0xfffff666:row['started'],0xffff23aa:selection['opening']}
        word.update({0xffff224e+2*i:value for i,value in enumerate(selection['output'])})
        child=oneshot_model.case(1,argument=pending,enable=row['enable'],opening=selection['opening'],
            inhibit=selection['inhibit'],history=history,started=row['started'],diagnostic=row['diagnostic'],
            entry_sr=row['entry_sr'],durations=selection['output'],counters=row['counters'])
        assert child['output']==row['counter_output']
        for point in (20,21):
            assert evaluate('injection_phase',point,source=pending,prev=row['started'],RAM8=byte)==child['expected_started']
        for channel in range(6):
            assert evaluate('injection_phase',22,source=pending,x=channel,prev=row['counters'][channel],
                RAM8=byte,RAM16=word)==row['counter_output'][channel]
