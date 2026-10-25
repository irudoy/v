"""Exact value-argument source identity and complete owning-document preservation."""

from copy import deepcopy
import json

import pytest

from kb import closed_loop_sample_argument_contract as contract,calculation_dependency_contract as calculation
from kb import closed_loop_coordinate_matrix as matrix,repo,test_contract


def test_one_exact_bare_helper_reader_reuses_the_coordinate_component_and_keeps_the_complete_owner():
    row=contract.descriptor(repo.ROOT)['reference'][0]
    old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
    before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    assert old['evidence']==[] and old['roles']==['indexed_by']
    assert old['props']==dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
    assert new['roles']==['arithmetic-argument'] and new['type']=='depends'
    assert new['props']['supports']=='identity' and new['props']['reverse_supports']=='identity'
    assert new['props']['via']==["SymbolKey(layout='7mfk', kind='fn', address=257460)"]
    assert row['component']=='closed_loop_coordinate_paths'
    assert (row['source_read'],row['callsite'],row['delay_slot'],row['register'])==(0x3EE72,0x3EE7A,0x3EE7C,6)
    expected=deepcopy(before);expected['link'][2]=deepcopy(after['link'][2])
    assert test_contract.exact(expected,after)
    assert before['symbol']==after['symbol'] and before['ledger']==after['ledger']
    assert len(before['link'])==len(after['link'])==5
    assert before['link'][0]['to']=='enlightened-orangutan/fn'
    assert before['link'][0]==after['link'][0]
    assert all(key not in after['symbol'][0] for key in ('width','signed'))
    assert sum(entry['kind']=='test' for entry in after['symbol'][0]['evidence'])==2
    assert sum(entry['kind']=='test' for entry in after['link'][0]['evidence'])==2
    registered=next(item for item in calculation.rows(repo.ROOT) if item['family']==contract.FAMILY)
    item=calculation.item(registered);item['to']=item['to'].location
    assert after['link'][2]['evidence']==[item]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_one_argument_descriptor_refuses_inference_beyond_its_pinned_value_path(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('old,new',(('source_read = 0x3ee72','source_read = 0x3ee6a'),
    ('callsite = 0x3ee7a','callsite = 0x3ee78'),('delay_slot = 0x3ee7c','delay_slot = 0x3ee7a'),
    ('register = 6','register = 5'),('width_bytes = 2','width_bytes = 1'),
    ('closed_loop_coordinate_paths','closed_loop_admission_paths')))
def test_argument_descriptor_refuses_another_physical_read_delay_or_raw_component(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('fault',('symbol-TEST','caller-TEST','other-relation','reverse-property',
    'link-position','ledger','width','signed'))
def test_exact_proposed_owner_refuses_changes_to_any_retained_native_value(tmp_path,fault):
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();declared=contract.descriptor(repo.ROOT)
    original=declared['reference'][0]['proposed_native_json'];value=json.loads(original)
    if fault=='symbol-TEST':value['symbol'][0]['evidence'][2]['key']='another_test'
    elif fault=='caller-TEST':value['link'][0]['evidence'][1]['key']='another_test'
    elif fault=='other-relation':value['link'][1]['role']='arithmetic-argument'
    elif fault=='reverse-property':value['link'][2]['reverse_supports']='scale'
    elif fault=='link-position':value['link'][1],value['link'][2]=value['link'][2],value['link'][1]
    elif fault=='ledger':value['ledger'][0]['fields'].reverse()
    elif fault=='width':value['symbol'][0]['width']=16
    else:value['symbol'][0]['signed']=False
    changed=json.dumps(value,sort_keys=True,separators=(',',':'))
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text(text.replace(json.dumps(original),json.dumps(changed),1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_fixed_other_sample_contexts_are_input_only_and_preserve_every_other_case_field():
    image=repo.images()['JK08A'].path.read_bytes()
    rows=matrix.cases({},image,root=repo.ROOT)
    selected=[row for row in rows if row['legacy_index']==-1
        and row['coefficient_override']==64 and row['sample'] in (0,51264)
        and all(row[key]==value for key,value in matrix.DEFAULTS.items()
            if key not in ('sample','coefficient_override'))]
    assert {row['sample'] for row in selected}=={0,51264}
    for row in selected:
        assert set(row)=={'index','entry','legacy_index',*matrix.FIELDS}


def test_document_gates_the_one_argument_native_preservation_and_actual_delay_boundary():
    text=(repo.ROOT/'defs/JK08A.closed-loop-sample-argument.md').read_text()
    assert 'contains one exact original' in text
    assert len(contract.descriptor(repo.ROOT)['reference'])==1
    for value in ('FFFF4524','0003EDB4','0003EF74','0003EE72','0003EE7A','0003EE7C'):
        assert value in text
    assert 'all four other' not in text and 'four other reader relations' in text
    assert 'unset semantic width' in text and 'TEST-bearing FFFF110A' in text
