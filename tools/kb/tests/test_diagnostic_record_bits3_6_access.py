"""Second exact diagnostic writer, joint native image, complete original and owning refusals."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import diagnostic_record_bit4_access_contract as contract
from kb import diagnostic_record_bit4_access_evidence as proof


def row():
    selected,=[row for row in contract.descriptor(repo.ROOT)['reference'] if row['component']=='diagnostic_record_bits3_6_paths']
    return selected


def test_two_exact_writer_originals_share_one_joint_native_postimage_without_changing_other_relations():
    declared=contract.descriptor(repo.ROOT);rows=declared['reference'];selected=row()
    assert selected['original_claim_sha256']=='a1a0e755b180a883c2233b9b0defed3824a8f5bc50dd9fa1756a57fe16b6f680'
    assert {'diagnostic_record_bit4_paths','diagnostic_record_bits3_6_paths'}<={item['component'] for item in rows}
    before=json.loads(selected['original_native_json']);after=json.loads(selected['proposed_native_json']);stripped=deepcopy(after)
    for item in rows:
        claim=json.loads(item['original_claim_json']);link,=[link for link in stripped['link'] if (link['type'],link['to'])==(claim['type'],claim['to'])]
        assert link['evidence'].pop()==contract.item(item)
        if not link['evidence']:link.pop('evidence')
        assert item['proposed_native_json']==selected['proposed_native_json']
        assert item['original_ledger_json']==item['proposed_ledger_json']
    assert stripped==before and before['unit']=='diagnostic record byte'
    functions={item['owner']:json.loads(item['native_json']) for item in declared['retained_functions']}
    assert {'cherry-wildcat/fn','provocative-vulture/fn'}<=set(functions)
    fn=functions['provocative-vulture/fn']
    selectors=[item for marker in fn['ledger'] for item in marker.get('dependency',())]
    assert any(item['to']=='cerise-chicken/ram' and item['end']=='to' and item['type']=='writer' for item in selectors)
    assert any(item['to']=='hallowed-malkoha/ram' and item['end']=='to' and item['type']=='writer' for item in selectors)
    assert selected['sites']==[0x8C954,0x8C95E]


@pytest.mark.parametrize('fault',('omit-first','omit-second','duplicate','wrong-direction','other-mask','merged-stage'))
def test_joint_normal_operations_require_both_exact_separate_positive_originals(fault):
    rows=contract.descriptor(repo.ROOT)['reference'];ops=[contract.operation(item) for item in rows]
    assert contract.operations(deepcopy(ops),repo.ROOT) is True
    target=next(op for op in ops if op['to']=='provocative-vulture/fn')
    if fault=='omit-first':ops.pop(0)
    elif fault=='omit-second':ops.remove(target)
    elif fault=='duplicate':ops.append(deepcopy(ops[-1]))
    elif fault=='wrong-direction':target['type']='reader'
    elif fault=='other-mask':target['evidence'][0]['value']['actual_indexed_write']['ordered_stages'][0]['mask']=16
    else:target['evidence'][0]['value']['actual_indexed_write']['ordered_stages'].pop()
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('flag',('exact_diagnostic_record_bits3_6_paths','complete_two_ordered_byte_OR_stages_and_RTS_delay',
    'complete_CPU_SR_frame_RAM','complete_physical_member_preimages_and_publications',
    'fixed_other_actual_common_member_alternatives','complete_native_owner_function_TEST_ledger',
    'no_array_extent_inference','no_selected_datum_absence_inference','native_bindings'))
def test_second_original_requires_its_own_complete_independent_admission(flag):
    selected=row();flags=proof.COMPONENT_FLAGS[selected['component']]
    result={key:True for key in flags}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c942/fn',
        function_meaning='provocative-vulture/fn',original_claim_sha256=selected['original_claim_sha256'])]
    assert proof.require_result(deepcopy(result),selected) is True
    result.pop(flag)
    with pytest.raises(ValueError):proof.require_result(result,selected)


@pytest.mark.parametrize('fault',('other-original','other-function','other-component','integer-flag'))
def test_first_bit4_original_cannot_supply_second_writer_admission(fault):
    selected=row();result={key:True for key in proof.COMPONENT_FLAGS[selected['component']]}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c942/fn',
        function_meaning='provocative-vulture/fn',original_claim_sha256=selected['original_claim_sha256'])]
    if fault=='other-original':result['native_bindings'][0]['original_claim_sha256']=contract.DECLARED['reference'][0]['original_claim_sha256']
    elif fault=='other-function':result['native_bindings'][0]['function_meaning']='cherry-wildcat/fn'
    elif fault=='other-component':result.pop('exact_diagnostic_record_bits3_6_paths');result['exact_diagnostic_record_bit4_paths']=True
    else:result['complete_two_ordered_byte_OR_stages_and_RTS_delay']=1
    with pytest.raises(ValueError):proof.require_result(result,selected)
