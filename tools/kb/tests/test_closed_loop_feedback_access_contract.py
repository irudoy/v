"""Retained coordinate/calculation facts and exact feedback input-only boundaries."""

from copy import deepcopy
import hashlib
import json
import re

import pytest

from kb import repo,test_contract,byte_surface_equations as state
from kb import closed_loop_feedback_access_contract as contract,closed_loop_feedback_matrix as matrix
from kb import closed_loop_feedback_argument_contract as arguments,closed_loop_feedback_capture_evidence as proof
from kb import closed_loop_coordinate_access_contract as owning,calculation_dependency_contract as calculation
from kb.test_stock_capture import tool

RETAINED_SIX = {'0003edb4-00008f98-reader': '1e45f677779bd28a051e508a4cb426506721f1ca3d859211e8e154c835c348ac',
 '0003edb4-00009384-reader': 'c3fdf5e608e17389e909606487462b6a636dfe23892abb1b5243d9c96f55f31d',
 '0003edb4-00009386-reader': '4ffd2101d35293622ae84c74da6bc856264323469fa4f7d531a6801f8e957205',
 '0003edb4-000095c6-reader': '3d7ca588794f6aa78ba9987d7fcba407ead06e94dd746ce8131247bf57f493b1',
 '0003edb4-00012292-reader': '7113f00aff8f16c472138eb6c57c32d07dee0341d7dec3dd5c9ad7fe14149757',
 '0003edb4-ffff2f8e-writer': 'ab3e1671272ae624ec5472c6d4b828e618c0d0006caefac9bf4cc549d965d594'}
RETAINED_CALCULATION_IDENTITIES_SHA256 = '4110090e9d53a35a802041c3b147111cd9857bde76fe7a45baf4aedc3a1cae2a'
RETAINED_EIGHT = {'0003edb4-00008f98-reader': '1e45f677779bd28a051e508a4cb426506721f1ca3d859211e8e154c835c348ac',
 '0003edb4-00009384-reader': 'c3fdf5e608e17389e909606487462b6a636dfe23892abb1b5243d9c96f55f31d',
 '0003edb4-00009386-reader': '4ffd2101d35293622ae84c74da6bc856264323469fa4f7d531a6801f8e957205',
 '0003edb4-000095c6-reader': '3d7ca588794f6aa78ba9987d7fcba407ead06e94dd746ce8131247bf57f493b1',
 '0003edb4-00012292-reader': '7113f00aff8f16c472138eb6c57c32d07dee0341d7dec3dd5c9ad7fe14149757',
 '0003edb4-ffff2f8e-writer': 'ab3e1671272ae624ec5472c6d4b828e618c0d0006caefac9bf4cc549d965d594',
 '0005d6ae-ffff895c-writer': 'a51bfdd4ec9f159761bd896522626c5c4b036d55605868989db60c78ca8caa97',
 '0005d6ae-ffff8960-writer': 'd4b805b29e2f1fd76811894956b2b1107bc62e4e398b78263a1e734318446122'}
RETAINED_THIRTY_SEVEN_SHA256 = '3bbcb91f1fc98b69e3af2681ab6fccee51a26f1ceaf93afd0e63a0dbdd9ab4e3'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_every_previous_coordinate_reference_and_calculation_identity_remains_exact():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==12 and {row['id']:digest(row) for row in rows[:6]}==RETAINED_SIX
    assert {row['address'] for row in rows[6:8]}=={0xFFFF895C,0xFFFF8960}
    assert digest(calculation.IDENTITIES[:34])==RETAINED_CALCULATION_IDENTITIES_SHA256
    assert len(calculation.IDENTITIES)==38


def test_all_five_native_transitions_preserve_every_symbol_type_layout_ledger_TEST_and_other_link():
    args=arguments.descriptor(repo.ROOT)['reference']
    assert len(args)==3 and {row['address'] for row in args}=={0xFFFF106E,0xFFFF1071,0xFFFF11BC}
    rows=[*args,*owning.descriptor(repo.ROOT)['reference'][6:8]]
    for row in rows:
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        assert before['symbol']==after['symbol'] and before.get('ledger')==after.get('ledger')
        assert len(before['link'])==len(after['link'])
        held_before=[value for value in before['link'] if value['to']!='funky-toucanet/fn']
        held_after=[value for value in after['link'] if value['to']!='funky-toucanet/fn']
        assert test_contract.exact(held_before,held_after)
        if row['address']==0xFFFF11BC:assert (row['declared_width'],row['declared_signed'])==(16,False)
        else:assert row['declared_width']==row['declared_signed']=='unset'
    for row in args:
        old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
        assert old['roles']==['indexed_by'] and old['type']=='reader'
        assert new['roles']==['arithmetic-argument'] and new['type']=='depends'
        assert new['props']['reverse_relies']=='structure' and new['props']['reverse_supports']=='identity'
        assert new['props']['via']==["SymbolKey(layout='7mfk', kind='fn', address=379884)"]
        assert old['evidence']==new['evidence']==[]


def test_whole_feedback_reuses_every_stock_span_alias_and_the_existing_frame_workspace_observer():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(76,352,320)
    assert source['observer']=='tools/sh-elf-run/invoke-closed-loop-feedback.s'
    assert source['workspace']==dict(start=0x5FFC,size=302,logical_offset=0x88B0,observed_start=0x5FDC,observed_size=366)
    assert sum(row['width']==4 for row in aliases)==43 and sum(row['width']==2 for row in aliases)==17
    for row in aliases:
        at,width=row['address'],row['width'];restored[at:at+width]=image[at:at+width]
        assert not any(first<at+width and at<last for first,last in contract.SPANS)
        if width==2:assert row['alias']-row['original']==0x5FFC-0xFFFF88B0
    assert bytes(restored)==image
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert contract.state_storage_premise(source) is True


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_feedback_descriptor_refuses_direct_callee_reads_geometry_scale_scheduling_or_hardware(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('flag',arguments.FLAGS)
def test_feedback_argument_descriptor_refuses_physical_reader_or_broader_admission(tmp_path,flag):
    path=tmp_path/arguments.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/arguments.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):arguments.descriptor(tmp_path)


@pytest.mark.parametrize('fault',('id','layout','rom','image','entry','observer','context','frame','prefix',
    'workspace','native-size','native-offset','canary','unit','alias','spans','scope'))
def test_existing_extended_frame_and_workspace_are_admitted_only_under_the_complete_exact_premise(fault):
    source=deepcopy(contract.descriptor(repo.ROOT))
    if fault in ('id','layout','rom'):source[fault]='another'
    elif fault=='image':source['image_sha256']='0'*64
    elif fault=='entry':source['entry_point']+=2
    elif fault=='observer':source['observer']='another.s'
    elif fault in ('context','frame','prefix'):source[{'context':'context_bytes','frame':'frame_bytes','prefix':'frame_prefix'}[fault]]+=4
    elif fault=='workspace':source['workspace']['start']+=4
    elif fault=='native-size':source['workspace']['size']+=4
    elif fault=='native-offset':source['workspace']['logical_offset']+=4
    elif fault=='canary':source['workspace']['observed_start']+=4
    elif fault=='unit':source['unit']['code'][0]['end']+=2
    elif fault=='alias':source['unit']['aliases'][0]['alias']+=4
    elif fault=='spans':source['entry'][0]['end']+=2
    else:source['physical_callee_reader_inference']=True
    assert contract.state_storage_premise(source) is False
    with pytest.raises(ValueError):state.execute(source,b'',tuple([0]*20),bytes(65536),bytes(352),0x02001000,0x123456,contract.ENTRY,0)


def test_legacy_input_reader_ignores_all_expected_workspace_output_ranges_and_CPU_rows(tmp_path):
    original=matrix.legacy_inputs(repo.ROOT)
    text=(repo.ROOT/matrix.INPUT_SOURCE).read_text()
    text=re.sub(r'(^\{[01]U,\d+U,\d+U,)[^\n]*',r'\1not-an-input},',text,flags=re.M)
    path=tmp_path/matrix.INPUT_SOURCE;path.parent.mkdir(parents=True);path.write_text(text)
    assert matrix.legacy_inputs(tmp_path)==original
    assert len(original)==matrix.LEGACY_CASES==1829


def test_raw_producer_and_independent_consumer_compile_identical_input_only_schemas():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    declared=dict(source=source,cases=list(matrix.cases(source,image,root=repo.ROOT)))
    producer=tool(repo.ROOT,'closed_loop_feedback_capture.py','_kb_feedback_input_source')
    header=proof.header(declared,image)
    assert producer.header(declared,image)==header
    names=set(re.findall(rb'static const struct \w+ (\w+)\[\]',header))
    assert names=={b'feedback_bound',b'feedback_controlled',b'feedback_changes',b'feedback_cases'}
    harness=(repo.ROOT/'tools/sh-elf-run/harness-closed-loop-feedback-paths.c').read_text()
    assert '#include "stock-jk08a-closed-loop-feedback-cases.h"' not in harness
    assert not any(value in harness for value in ('cpu_samples','memory_samples','expected['))


@pytest.mark.parametrize('address,width,low,high',((0x106E,1,0,255),(0x1071,1,0,255),(0x11BC,2,0,65535),(0x10C8,1,0,3)))
def test_controlled_positive_pairs_hold_every_other_complete_input_context_workspace_and_calibration(address,width,low,high):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image,root=repo.ROOT);selected=[]
    reference=next(row for row in rows if row['kind']=='controlled' and row['profile']=='argument-contrast'
        and matrix.memory(row)[0x106E]==40 and matrix.memory(row)[0x1071]==60
        and int.from_bytes(matrix.memory(row)[0x11BC:0x11BE],'big')==3 and matrix.memory(row)[0x10C8]==3)
    fixed=matrix.memory(reference)
    for value in (low,high):
        wanted=bytearray(fixed);wanted[address:address+width]=value.to_bytes(width,'big')
        choices=[row for row in rows if row['kind']=='controlled' and row['profile']=='argument-contrast'
            and matrix.memory(row)==bytes(wanted)]
        assert choices;selected.append(choices[0])
    left,right=map(matrix.memory,selected);a,b=bytearray(left),bytearray(right)
    a[address:address+width]=b[address:address+width]
    assert a==b and left[address:address+width]!=right[address:address+width]
    assert matrix.context(source,selected[0])==matrix.context(source,selected[1])
    assert matrix.workspace(selected[0])==matrix.workspace(selected[1])
    assert matrix.calibrations(source,image,selected[0])==matrix.calibrations(source,image,selected[1])


def test_feedback_documented_counts_and_scopes_read_the_current_executed_sources():
    from kb import ordinary_access_registry as ordinary
    source=contract.descriptor(repo.ROOT)
    text=re.sub(r'\s+',' ',(repo.ROOT/'defs/JK08A.closed-loop-feedback-accesses.md').read_text())
    facts=(('contains three exact original',len(arguments.descriptor(repo.ROOT)['reference']),3),
        ('contains twelve exact owning appends',len(owning.descriptor(repo.ROOT)['reference']),12),
        ('contains 38 dispositions',len(calculation.rows(repo.ROOT)),38),
        ('contains 3067 instructions',sum((last-first)//2 for first,last in contract.SPANS),3067),
        ('63998 bound code/pool bytes',sum(row['size'] for row in contract.BOUND_SPANS),63998),
        ('43 long pointer aliases',sum(row['width']==4 for row in contract.UNIT['aliases']),43),
        ('17 word pointer aliases',sum(row['width']==2 for row in contract.UNIT['aliases']),17),
        ('has 302 bytes',source['workspace']['size'],302),('76-byte incoming context',source['context_bytes'],76),
        ('892-byte result',184+2*source['frame_bytes']+4,892),('352-byte frame',source['frame_bytes'],352),
        ('preserves 1829 legacy input contexts',matrix.LEGACY_CASES,1829),
        ('18 controlled calibration bytes',sum(row['size'] for row in contract.CONTROLLED_CALIBRATION),18),
        ('All 27 required active-state and transition conditional sites',len(proof.REQUIRED_BRANCHES),27),
        ('thirteen ordinary families',len(ordinary.FAMILIES),13),('forty-seven capture bindings',len(ordinary.captures()),47))
    for phrase,actual,wanted in facts:assert phrase in text and actual==wanted
    assert 'physical RAM reader inside the callee' in text and 'unrestricted absence of reads' in text
    assert 'controlled contrast grants no stock calibration' in text
    assert source['physical_callee_reader_inference'] is False


def test_feedback_shared_docs_publish_current_counts_without_changing_the_coordinate_component_boundary():
    from kb import ordinary_access_registry as ordinary
    owning_rows=owning.descriptor(repo.ROOT)['reference'];calculation_rows=calculation.rows(repo.ROOT)
    coordinate=[row for row in owning_rows if row['component']=='closed_loop_coordinate_paths']
    assert len(coordinate)==6 and len(owning_rows)==12 and len(calculation_rows)==38
    checks={
        'tools/kb/README.md':('Three feedback value arguments','The bounded I/O source',('twelve owning appends','has 38 dispositions','27 active-state/transition branch sites')),
        'tools/kb/SPEC.md':('The `closed_loop_feedback_paths` component','Reserved `rpm-inhibit-access`',('contains 38 dispositions','at 27 active-state/transition','18 controlled calibration bytes')),
        'tools/sh-elf-run/README.md':('`jk08a-closed-loop-feedback-paths` reuses','`jk08a-rpm-inhibit-paths`',('twelve owning appends','has 38 dispositions','All 27 active-state/transition'))}
    for path,(start,end,phrases) in checks.items():
        snippet=re.sub(r'\s+',' ',(repo.ROOT/path).read_text().split(start,1)[1].split(end,1)[0])
        for phrase in phrases:assert phrase in snippet
    ordinary_text=re.sub(r'\s+',' ',(repo.ROOT/'tools/kb/ordinary-access.md').read_text())
    assert 'Thirteen ordinary families contain forty-seven capture bindings' in ordinary_text
    assert len(ordinary.FAMILIES)==13 and len(ordinary.captures())==47


def test_transition_counter_pair_retains_all_eight_full_references_and_37_calculation_identities():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert {row['id']:digest(row) for row in rows[:8]}==RETAINED_EIGHT
    assert digest(calculation.IDENTITIES[:37])==RETAINED_THIRTY_SEVEN_SHA256
    pair=rows[8:10];assert len(pair)==2 and {row['direction'] for row in pair}=={'reader','writer'}
    assert {row['original_claim_sha256'] for row in pair}=={
        '38efa109e85c2b7158788ad15506c4d7062ba6adcbc0fff08decbcf570e38d47',
        'c186b5d66d2b6ac73439c2ffc4431b3b4386042fc333010e6038738c4b1c4c6f'}
    assert len({row['original_native_json'] for row in pair})==len({row['proposed_native_json'] for row in pair})==1
    before,after=(json.loads(pair[0][key]) for key in ('original_native_json','proposed_native_json'))
    expected=deepcopy(before)
    for row in pair:
        assert (row['address'],row['owner'],row['function'],row['component'],row['width_bytes'],
            row['declared_width'],row['declared_signed'])==(0xFFFF88BA,'closed_loop_feedback_transition_counter_b2/ram',
                0x5CA8C,'closed_loop_feedback_paths',2,16,False)
        old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
        assert old['evidence']==[
            dict(kind='test',path='tools/kb/tests/test_closed_loop_feedback_chain.py',key='test_feedback_owner_contract'),
            dict(kind='test',path='tools/kb/tests/test_closed_loop_feedback_chain.py',key='test_registered_feedback_stock_contract'),
            dict(kind='spec',path='defs/JK08A.closed-loop-feedback.md',key='Bounded feedback')]
        assert new['evidence'][:-1]==old['evidence']
        assert {key:value for key,value in old.items() if key!='evidence'}=={key:value for key,value in new.items() if key!='evidence'}
        link=next(link for link in expected['link'] if (link['type'],link['to'])==(row['direction'],'closed_loop_feedback_transition/fn'))
        link['evidence'].append(owning.item(row))
    assert test_contract.exact(expected,after)
    assert before['symbol']==after['symbol'] and before.get('ledger')==after.get('ledger')
    assert pair[0]['sites']==[0x5CB30,0x5CB7A,0x5CB9C] and pair[1]['sites']==[0x5CBAA,0x5CBBC]


@pytest.mark.parametrize('offset,width,values',((0x88BA,2,(0,1)),(0x88C1,1,(0,1))))
def test_transition_counter_positive_inputs_hold_both_complete_native_and_ordinary_mirrors_fixed(offset,width,values):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    candidates=matrix.cases(source,image,root=repo.ROOT);selected=[]
    for value in values:
        def matches(row):
            memory=matrix.memory(row)
            return (row['kind']=='controlled' and row['profile']=='stock'
                and int.from_bytes(memory[0x28BA:0x28BC],'big')==5000
                and int.from_bytes(memory[0x29E4:0x29E6],'big')==0
                and int.from_bytes(memory[0x88BA:0x88BC],'big')==(value if offset==0x88BA else 0)
                and memory[0x88C1]==(value if offset==0x88C1 else 1))
        selected.append(next(row for row in candidates if matches(row)))
    memories=[bytearray(matrix.memory(row)) for row in selected]
    workspaces=[bytearray(matrix.workspace(row)) for row in selected]
    native=32+offset-0x88B0
    assert memories[0][offset:offset+width]!=memories[1][offset:offset+width]
    for memory,workspace in zip(memories,workspaces):
        memory[offset:offset+width]=bytes(width);workspace[native:native+width]=bytes(width)
    assert memories[0]==memories[1] and workspaces[0]==workspaces[1]
    assert matrix.context(source,selected[0])==matrix.context(source,selected[1])
    assert matrix.calibrations(source,image,selected[0])==matrix.calibrations(source,image,selected[1])


def test_transition_counter_threshold_band_boundaries_and_guard_premise_read_stock_bytes():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image,root=repo.ROOT);counts=set();observed=set()
    threshold=image[0x8822]*image[0x23752]
    lower=(5000-int.from_bytes(image[0x92EE:0x92F0],'big'))&65535
    upper=(5000+int.from_bytes(image[0x92F0:0x92F2],'big'))&65535
    for row in rows:
        memory=matrix.memory(row)
        if row['kind']=='controlled' and row['profile']=='stock' and int.from_bytes(memory[0x28BA:0x28BC],'big')==5000:
            counts.add(int.from_bytes(memory[0x88BA:0x88BC],'big'))
            observed.add(int.from_bytes(memory[0x29E4:0x29E6],'big'))
    assert {0,1,max(0,threshold-1),threshold,threshold+1,65534,65535}<=counts
    assert {0,(lower-1)&65535,lower,5000,upper,(upper+1)&65535,65535}<=observed
    text=' '.join((repo.ROOT/'defs/JK08A.closed-loop-feedback-accesses.md').read_text().split())
    assert '5CB84' in text and '65025' in text and '5CB86..5CB92' in text
    assert 'two transition-counter relations' in text and 'Both original TEST positions and the following spec position' in text
