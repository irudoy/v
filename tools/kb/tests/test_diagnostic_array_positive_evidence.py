"""Actual retained-array writer operands,computed bits and same-primary refusal sources."""
from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import paired_inhibit_writer_withdrawal_contract as contract
from kb import paired_inhibit_writer_withdrawal_capture_evidence as proof
from kb import diagnostic_array_positive_evidence as positive
from kb import actuator_mask_access_capture_evidence as combined


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['paired_inhibit_writer_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original paired flag writer caller withdrawal capture')
        pytest.skip('the complete original paired flag writer caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_paired_inhibit_writer_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    for key in ('native_geometry_inference','automatic_resolution','scale_admission','units_admission',
            'native_identity_admission','natural_caller_reachability','hardware_qualification'):
        assert result[key] is False
    return model,record,packet


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'first':lambda c:c['entry']==0x7C8FA and c['kind']=='complete-raw-register-width',
        'second':lambda c:c['entry']==0x7C9A8 and c['kind']=='complete-raw-register-width',
        'first-bypass':lambda c:c['entry']==0x7C8FA and c['kind']=='independent-active-flag-threshold-and-helper-input' and c['byte_41c5']==0,
        'mid-block':lambda c:c['entry']==0x7C8FA and c['kind']=='independent-active-flag-threshold-and-helper-input' and c['byte_5b2c']==8,
        'helper-block':lambda c:c['entry']==0x7C8FA and c['kind']=='independent-active-flag-threshold-and-helper-input' and c['byte_5b33']==128,
        'helper-bypass':lambda c:c['entry']==0x7C8FA and c['kind']=='independent-active-flag-threshold-and-helper-input' and c['byte_5b33']==0,
        'threshold-block':lambda c:c['kind']=='raw-sign-extended-byte-unsigned-threshold-comparison' and c['byte_3118']==4 and c['config_885d']==4,
        'negative-threshold':lambda c:c['kind']=='raw-sign-extended-byte-unsigned-threshold-comparison' and c['byte_3118']==127 and c['config_885d']==128}
    for name,predicate in predicates.items():
        case=next(row for row in declared['cases'] if predicate(row));observed=actual[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT);selected[name]=(case,observed,result,value)
    return declared,image,actual,selected


@pytest.mark.parametrize('name',('first','second'))
def test_real_array_member_writes_retain_the_array_dependency_when_its_first_byte_is_untouched(windows,name):
    _,_,_,selected=windows;case,observed,result,_=selected[name]
    seen,publications=positive.require_operands(case['entry'],result,observed)
    assert seen==set(positive.sites(case['entry'])) and len(publications)==14
    assert all(address!=positive.ARRAY_BASE for site,address,before,after in publications)
    assert any(row['mode']=='write' and row['address']>positive.ARRAY_BASE for row in result['accesses'])
    # Untouched first-byte state does not delete or negate the proven element writes.
    assert observed['memory_before'][0][0x5718]==observed['memory_after'][0][0x5718]


@pytest.mark.parametrize('name',('first','second'))
@pytest.mark.parametrize('fault',('omit-read','omit-write','swap','duplicate-read','input-echo','wrong-mask',
    'site','address','width_bytes','register','domain','final-byte'))
def test_actual_ordered_array_RMW_requires_both_exact_operands_and_real_computed_publication(windows,name,fault):
    _,_,_,selected=windows;case,observed,result,_=deepcopy(selected[name])
    # Select a real RMW whose bit operation changes the byte when available.
    sites=positive.sites(case['entry']);site=next(iter(sites))
    indexes=[i for i,row in enumerate(result['accesses']) if row['site']==site]
    first,second=indexes;read=result['accesses'][first];write=result['accesses'][second]
    if fault=='omit-read':result['accesses'].pop(first)
    elif fault=='omit-write':result['accesses'].pop(second)
    elif fault=='swap':result['accesses'][first],result['accesses'][second]=write,read
    elif fault=='duplicate-read':result['accesses'].insert(first,deepcopy(read))
    elif fault=='input-echo':
        # Force a missing OR bit in the independent incoming byte,then copy it.
        read['bytes']='00';write['bytes']='00'
    elif fault=='wrong-mask':write['bytes']=bytes((int(read['bytes'],16)^0x80,)).hex()
    elif fault=='final-byte':
        memory=bytearray(observed['memory_after'][0]);memory[write['address']-positive.RAM_BASE]^=1
        observed['memory_after']=(bytes(memory),)
    elif fault=='site':write['site']+=2
    elif fault in ('address','width_bytes'):write[fault]+=1
    elif fault=='register':write[fault]=0
    else:write[fault]='changed'
    with pytest.raises(ValueError):positive.require_operands(case['entry'],result,observed)


def test_complete_existing_paired_primary_and_all_exact_writer_originals_remain_mandatory(original):
    result=positive.require_primary(original[0],original[1])
    assert result['positive_array_member_writes'] is True
    assert result['complete_paired_original_same_primary'] is True
    assert result['originals']==positive.ORIGINALS
    assert result['root_byte_absence_is_array_absence'] is False
    assert result['paired_original_stdout_sha256']==original[2]['stdout_sha256']
    record=deepcopy(original[1]);record['candidate']['witness'].pop('paired_inhibit_writer_withdrawal_paths')
    with pytest.raises((ValueError,KeyError)):positive.require_primary(original[0],record)


@pytest.mark.parametrize('capture',('paired_inhibit_writer_withdrawal_paths','maf_record_paths','actuator_mask_access_paths'))
def test_positive_reader_and_writers_require_each_complete_original_from_the_same_primary(original,capture):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(capture)
    with pytest.raises((ValueError,KeyError)):combined.require_primary(original[0],record)
