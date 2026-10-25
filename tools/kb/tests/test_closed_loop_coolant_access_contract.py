"""Exact coolant native retention, input-only source domain and published boundaries."""

from copy import deepcopy
import hashlib
import json
import re

import pytest

from kb import repo,test_contract,ordinary_access_registry as ordinary
from kb import closed_loop_coolant_access_contract as contract,closed_loop_coolant_matrix as matrix
from kb import closed_loop_coolant_capture_evidence as proof
from kb import closed_loop_coordinate_access_contract as owning,calculation_dependency_contract as calculation
from kb.test_stock_capture import tool

RETAINED_TEN = {'0003edb4-00008f98-reader': '1e45f677779bd28a051e508a4cb426506721f1ca3d859211e8e154c835c348ac',
 '0003edb4-00009384-reader': 'c3fdf5e608e17389e909606487462b6a636dfe23892abb1b5243d9c96f55f31d',
 '0003edb4-00009386-reader': '4ffd2101d35293622ae84c74da6bc856264323469fa4f7d531a6801f8e957205',
 '0003edb4-000095c6-reader': '3d7ca588794f6aa78ba9987d7fcba407ead06e94dd746ce8131247bf57f493b1',
 '0003edb4-00012292-reader': '7113f00aff8f16c472138eb6c57c32d07dee0341d7dec3dd5c9ad7fe14149757',
 '0003edb4-ffff2f8e-writer': 'ab3e1671272ae624ec5472c6d4b828e618c0d0006caefac9bf4cc549d965d594',
 '0005d6ae-ffff895c-writer': 'a51bfdd4ec9f159761bd896522626c5c4b036d55605868989db60c78ca8caa97',
 '0005d6ae-ffff8960-writer': 'd4b805b29e2f1fd76811894956b2b1107bc62e4e398b78263a1e734318446122',
 '0005ca8c-ffff88ba-reader': '6e4f1ed8abc6b6e6215b1afbaeb2fd11d37eb3dab265870a8f93c8297dbe7463',
 '0005ca8c-ffff88ba-writer': '02377577b098c8ee0f416890b221e797c6326e313f0570a1324bfe4ea2fd7658'}
RETAINED_CALCULATION_SHA256='3bbcb91f1fc98b69e3af2681ab6fccee51a26f1ceaf93afd0e63a0dbdd9ab4e3'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_coolant_pair_preserves_all_ten_full_references_and_all_37_calculation_identities():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==12 and {row['id']:digest(row) for row in rows[:10]}==RETAINED_TEN
    assert len(calculation.IDENTITIES)==38 and digest(calculation.IDENTITIES[:37])==RETAINED_CALCULATION_SHA256
    pair=rows[10:];assert len(pair)==2
    assert {row['original_claim_sha256'] for row in pair}=={
        '73ac1338a230b99a635d72a05d8b67a68c562379048b03c1ffcccbb005a9d338',
        'd773155aadf3691cc8cd12896b8a1eb2698b8ff6ac0722d99db603c9a2939544'}
    assert {(row['address'],row['sites'][0],row['declared_width'],row['declared_signed']) for row in pair}=={
        (0x990A,0x553E6,8,False),(0x5533C,0x5532A,16,True)}
    for row in pair:
        old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        assert row['function']==0x5525A and row['component']=='closed_loop_coolant_paths'
        assert old['type']==new['type']=='reader' and old['to']==new['to']=='knowing-potoo/fn'
        assert old['evidence']==[
            dict(kind='test',path='tools/kb/tests/test_fuel_upstream_chain.py',key='test_fuel_upstream_owner_contract'),
            dict(kind='test',path='tools/kb/tests/test_fuel_upstream_chain.py',key='test_fuel_upstream_stock_regions_contract'),
            dict(kind='spec',path='defs/JK08A.fuel.md',key='Upstream fuel pulse calculations')]
        assert new['evidence'][:-1]==old['evidence'] and old['props']==new['props']
        expected=deepcopy(before);expected['link'][0]['evidence'].append(owning.item(row))
        assert test_contract.exact(expected,after)
        assert before['symbol']==after['symbol'] and before.get('ledger')==after.get('ledger')


def test_existing_whole_coolant_source_has_only_seven_original_pointer_aliases_and_no_observing_stub():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert len(aliases)==7 and all(row['width']==4 for row in aliases)
    for row in aliases:
        at=row['address'];assert row['alias']==matrix.RAM_BASE+(row['original']&65535)
        restored[at:at+4]=image[at:at+4]
    assert bytes(restored)==image
    assert all(fixture[first:last]==image[first:last] for first,last in contract.SPANS)
    assert (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(80,192,160)
    assert source['observer']=='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
    assert source['stock_function_stubs'] is False


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_coolant_descriptor_refuses_stubs_geometry_scheduling_hardware_or_self_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_legacy_coolant_parser_does_not_parse_nine_scalar_results_or_any_following_result_register_array(tmp_path):
    scalar=','.join(f'0x{matrix.DEFAULTS[key]:x}U' for key in matrix.FIELDS)
    arrays=','.join('{'+','.join(f'0x{value:x}U' for value in matrix.DEFAULTS[key])+'}' for key,size in matrix.ARRAYS)
    line='{'+scalar+','+','.join(['not_an_input']*9)+','+arrays+',ignored,{not_input},{not_input},{not_input}},\n'
    structure='struct coolant_conditional_case { uint32_t '+','.join((*matrix.FIELDS,*('result'+str(i) for i in range(9))))+';\n'
    structure+=''.join('uint32_t '+name+'['+str(size)+'];\n' for name,size in matrix.ARRAYS)+'};\n'
    text=structure+'static const struct coolant_conditional_case coolant_conditional_cases[]={\n'+line*14261+'};\n'
    path=tmp_path/matrix.INPUT_SOURCE;path.parent.mkdir(parents=True);path.write_text(text)
    rows=matrix.legacy_inputs(tmp_path)
    assert len(rows)==14261 and all(row==matrix.DEFAULTS for row in rows)


def test_producer_consumer_headers_have_identical_input_only_fields_and_no_old_expected_results():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    declared=dict(source=source,cases=list(matrix.cases(source,image,root=repo.ROOT)))
    producer=tool(repo.ROOT,'closed_loop_coolant_capture.py','_kb_coolant_header_producer')
    header=proof.header(declared,image)
    assert producer.header(declared,image)==header
    assert set(re.findall(rb'static const struct \w+ (\w+)\[\]',header))=={
        b'coolant_bound',b'coolant_controlled',b'coolant_cases'}
    harness=(repo.ROOT/'tools/sh-elf-run/harness-closed-loop-coolant-paths.c').read_text()
    assert '#include "coolant-conditional-cases.h"' not in harness
    assert not any(value in harness for value in ('expected[','locals_mask','updated_a','updated_b','cpu_samples'))


@pytest.mark.parametrize('address,low,high',((0x990A,1,64),(0x5533C,0xFF40,0xFF48)))
def test_constant_positive_inputs_hold_complete_RAM_context_and_all_other_calibration_bytes_fixed(address,low,high):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    cases=matrix.cases(source,image,root=repo.ROOT);selected=[]
    for value in (low,high):
        if address==0x990A:
            case=next(row for row in cases if row['kind']=='controlled' and row['load']==row['rpm_select']==0
                and row['curve']==[255]*8 and row['coefficients']==[value,*([64]*15)] and row['cap']==65535)
        else:
            case=next(row for row in cases if row['kind']=='controlled' and row['previous_coolant']==240
                and row['coolant_offset']==value and row['coefficients']==[64]*16 and row['curve']==matrix.DEFAULTS['curve'])
        selected.append(case)
    assert matrix.memory(selected[0])==matrix.memory(selected[1])
    assert matrix.context(source,selected[0])==matrix.context(source,selected[1])
    left,right=(matrix.calibrations(source,image,row) for row in selected)
    size=1 if address==0x990A else 2
    assert left[address][:size]!=right[address][:size]
    left[address]=bytes(size)+left[address][size:];right[address]=bytes(size)+right[address][size:]
    assert left==right


def test_current_coolant_document_pins_counts_from_executed_sources_and_the_exact_owning_boundary():
    text=' '.join((repo.ROOT/'defs/JK08A.closed-loop-coolant-accesses.md').read_text().split())
    facts=(('322 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),322),
        ('644 code bytes',sum(last-first for first,last in contract.SPANS),644),
        ('126 pool bytes',sum(row['size'] for row in contract.UNIT['pools']),126),
        ('770 bound bytes',sum(row['size'] for row in contract.BOUND_SPANS),770),
        ('seven long pointer aliases',len(contract.UNIT['aliases']),7),
        ('42 controlled calibration bytes',sum(row['size'] for row in contract.CONTROLLED_CALIBRATION),42),
        ('14261 legacy input rows',len(matrix.legacy_inputs(repo.ROOT)),14261),
        ('17 scalar inputs',len(matrix.FIELDS),17),('five calibration arrays',len(matrix.ARRAYS),5),
        ('25 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),25),
        ('twelve exact owning appends',len(owning.descriptor(repo.ROOT)['reference']),12),
        ('thirteen ordinary families',len(ordinary.FAMILIES),13),('forty-seven capture bindings',len(ordinary.captures()),47))
    for phrase,actual,wanted in facts:assert phrase in text and actual==wanted
    for phrase in ('unsigned8','signed16','4*rpm_bin+load_bin-5','26A9A','26A9C..26AAA',
        'derived word at FFFF15DA','no stock calibration reachability','TEST/spec positions'):
        assert phrase in text


def test_current_shared_coolant_counts_follow_the_actual_source_descriptor_and_registration():
    assert sum((last-first)//2 for first,last in contract.SPANS)==322
    assert sum(row['size'] for row in contract.BOUND_SPANS)==770
    assert sum(row['size'] for row in contract.CONTROLLED_CALIBRATION)==42
    assert len(contract.UNIT['aliases'])==7 and matrix.LEGACY_CASES==14261
    assert len(proof.REQUIRED_BRANCHES)==25 and len(matrix.FIELDS)==17 and len(matrix.ARRAYS)==5
    assert len(owning.descriptor(repo.ROOT)['reference'])==12
    assert len(ordinary.FAMILIES)==13 and len(ordinary.captures())==47
    checks={
        'tools/kb/README.md':('Two coolant constant readers','The bounded I/O source',
            ('322 instructions/770 bound bytes','42 controlled calibration bytes','14261 input-only rows',
             '25 two-sided sites','twelve-item owning batch','forty-seven capture bindings')),
        'tools/kb/SPEC.md':('The `closed_loop_coolant_paths` component','Reserved `rpm-inhibit-access`',
            ('322 stock instructions/770 bound bytes','42 controlled calibration bytes','14261 legacy rows',
             '17 scalar inputs and five calibration arrays','25 two-sided sites','families/twenty-one captures')),
        'tools/sh-elf-run/README.md':('`jk08a-closed-loop-coolant-paths` reuses','`jk08a-rpm-inhibit-paths`',
            ('322 stock instructions/770 bound bytes','42 controlled calibration bytes','14261 legacy input rows',
             '17 scalar inputs and five calibration arrays','All25 feasible conditional sites','families/twenty-one captures'))}
    for path,(start,end,phrases) in checks.items():
        snippet=' '.join((repo.ROOT/path).read_text().split(start,1)[1].split(end,1)[0].split())
        for phrase in phrases:assert phrase in snippet
