"""Exact helper native append and reuse of the complete retained reset source."""
from copy import deepcopy
import json,re
import pytest
from kb import repo,test_contract
from kb import diagnostic_reset_helper_writer_contract as helper
from kb import diagnostic_state_reset_writer_contract as core,diagnostic_state_reset_writer_matrix as matrix
from kb import diagnostic_state_reset_writer_access_contract as joint


def test_helper_append_preserves_complete_owner_other_relations_type_and_functions():
    source=helper.descriptor(repo.ROOT);row=source['reference'][0]
    old,new=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(new);target,=[link for link in stripped['link'] if link['to']=='cheerful-beluga/fn']
    assert target.pop('evidence')==[helper.item(row)] and test_contract.exact(stripped,old)
    assert row['original_ledger_json']==row['proposed_ledger_json']
    assert old['unit']==new['unit']=='bitfield'
    assert row['declared_width']==row['declared_signed']=='unset'
    assert all('width' not in symbol and 'signed' not in symbol for symbol in old['symbol'])
    assert json.loads(row['original_symbol_evidence_json'])==old['symbol'][0]['evidence']
    assert {link['to'] for link in old['link']}=={'muscular-lizard/fn','cheerful-beluga/fn','nissan_service_30_output_control/fn'}
    combined=joint.descriptor(repo.ROOT)
    assert combined['reference'][0]==joint.DECLARED['reference'][0]
    assert combined['reference'][1]==row and len(combined['reference'])==2
    assert combined['retained_functions']==joint.DECLARED['retained_functions']==source['retained_functions']
    assert source['preserved_parent_original_sha256']==combined['reference'][0]['original_claim_sha256']


@pytest.mark.parametrize('fault',('summary','other-writer','reader','ledger','unit','width','signed','symbol-evidence','function','claim'))
def test_helper_descriptor_refuses_any_unrelated_native_or_claim_change(monkeypatch,fault):
    document=deepcopy(helper.DECLARED);row=document['reference'][0]
    if fault=='function':document['retained_functions'][0]['native_json']='{}'
    elif fault=='claim':row['proposed_claim_json']='{}'
    else:
        native=json.loads(row['original_native_json'])
        if fault=='summary':native['summary']='partial owner'
        elif fault=='other-writer':native['link']=[link for link in native['link'] if link['to']!='nissan_service_30_output_control/fn']
        elif fault=='reader':native['link'][0]['role']='changed'
        elif fault=='ledger':native['ledger']=[]
        elif fault=='unit':native['unit']='raw'
        elif fault in ('width','signed'):native['symbol'][0][fault]=8 if fault=='width' else False
        else:native['symbol'][0]['evidence']=[]
        row['original_native_json']=json.dumps(native)
    monkeypatch.setattr(helper.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):helper.descriptor(repo.ROOT)


def test_published_loop_and_prior_counts_read_the_executed_matrix_and_exact_claim():
    row=helper.descriptor(repo.ROOT)['reference'][0];actual=helper.item(row)['value']['actual_constant_write']
    text=(repo.ROOT/'defs/JK08A.diagnostic-reset-helper-writer.md').read_text()
    assert int(re.search(r'loop has (\d+) stores',text)[1])==actual['loop_count']==4
    assert int(re.search(r'iteration is (\d+)',text)[1])==actual['zero_based_iteration']==3
    source=core.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    cases=matrix.cases(source,image);count=int(re.search(r'all (\d+) raw target priors',text)[1])
    for gate in (0,64):
        selected=[case for case in cases if case['kind']=='helper99c7-constant-zero-with-held-other-inputs' and case['byte_41e1']==gate]
        assert len(selected)==count and {case['prior_99c7'] for case in selected}==set(range(count))==set(range(256))
        assert len({tuple((key,value) for key,value in case.items() if key not in ('index','prior_99c7')) for case in selected})==1
    assert actual==dict(address=0xFFFF99C7,site=0x2E77A,width_bytes=1,register=7,full_register_value=0,value=0,
        pointer_register=5,counter_register=6,counter_value=4,loop_start=0xFFFF99C4,loop_count=4,zero_based_iteration=3)
    assert core.ENTRY==0x2E81A and set(source['functions'])=={0x2E76E,0x2E81A,0xCD75C}
