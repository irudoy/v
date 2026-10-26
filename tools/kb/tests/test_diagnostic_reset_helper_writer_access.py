"""Joint normal writer operations and strict helper owning-result admission."""
from copy import deepcopy
import json
import pytest
from kb import repo,ordinary_access_registry as registry
from kb import diagnostic_reset_helper_writer_contract as helper,diagnostic_reset_helper_writer_capture_evidence as capture
from kb import diagnostic_state_reset_writer_access_contract as contract,diagnostic_state_reset_writer_access_evidence as proof


def rows():return contract.descriptor(repo.ROOT)['reference']


def result():
    return dict({flag:True for flag in proof.REQUIRED_FLAGS},**{flag:False for flag in proof.NON_ADMISSIONS},
        causal_inputs=dict(raw_rom_8dfc=True,raw_rom_8dfd=True),
        constant_writer_inputs=dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True),
        helper_constant_writer_inputs=dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True),
        native_bindings=[dict(symbol=f"7mfk-{row['address']:08x}/ram",meaning=row['owner'],function=f"7mfk-{row['function']:08x}/fn",
            function_meaning=json.loads(row['original_claim_json'])['to'],original_claim_sha256=row['original_claim_sha256']) for row in rows()])


def test_existing_family_and_capture_route_both_exact_originals_without_new_profile():
    family,=[entry for entry in registry.FAMILIES if entry.mode==contract.MODE]
    assert family.captures==(('diagnostic_state_reset_writer_paths','diagnostic_state_reset_writer_capture'),)
    assert set(helper.SOURCE_FILES)<=set(family.source_files)
    assert family.direct_owning is True and family.owner_fallback is False and family.withdrawal_only is False
    for row in rows():
        assert registry.matching(contract.item(row))==(family,)
        assert registry.original_family(json.loads(row['original_claim_json'])) is family
        assert proof.require_result(result(),row) is True
    assert contract.operations([contract.operation(row) for row in rows()],repo.ROOT) is True


@pytest.mark.parametrize('fault',('parent-only','helper-only','duplicate','helper-PC','helper-carrier','parent-original','helper-original','reader'))
def test_normal_joint_append_requires_both_complete_unchanged_exact_operations(fault):
    ops=[contract.operation(row) for row in rows()]
    if fault=='parent-only':ops=ops[:1]
    elif fault=='helper-only':ops=ops[1:]
    elif fault=='duplicate':ops.append(deepcopy(ops[1]))
    elif fault=='helper-PC':ops[1]['evidence'][0]['at']='7mfk:0002e77c'
    elif fault=='helper-carrier':ops[1]['evidence'][0]['value']['actual_constant_write']['full_register_value']=0x100
    elif fault in ('parent-original','helper-original'):ops[int(fault=='helper-original')]['evidence'][0]['value']['original_claim_sha256']='0'*64
    else:ops[1]['type']='reader'
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('field',('complete_helper_zero_PC_R7_loop','actual_helper_zero_priors'))
@pytest.mark.parametrize('value',(False,1,None))
def test_helper_owning_boundary_requires_strict_measured_obligations(field,value):
    current=result();current[field]=value
    with pytest.raises(ValueError):capture.require_result(current)
    with pytest.raises(ValueError):proof.require_result(current,rows()[1])


@pytest.mark.parametrize('fault',('helper-proof','missing-helper','helper-owner','helper-function','helper-original','hardware','units'))
def test_shared_result_cannot_replace_helper_original_or_admit_unmeasured_facts(fault):
    current=result()
    if fault=='helper-proof':current['helper_constant_writer_inputs']['gate_1_full_priors']=False
    elif fault=='missing-helper':current['native_bindings'].pop()
    elif fault in ('helper-owner','helper-function','helper-original'):
        current['native_bindings'][1][{'helper-owner':'meaning','helper-function':'function_meaning','helper-original':'original_claim_sha256'}[fault]]='changed'
    else:current['hardware_qualification' if fault=='hardware' else 'units_admission']=True
    with pytest.raises(ValueError):proof.require_result(current,rows()[1])
