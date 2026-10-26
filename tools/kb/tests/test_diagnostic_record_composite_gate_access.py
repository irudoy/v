"""Exact positive nested array reader, full caller/helper, original selectors and owning refusals."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import diagnostic_record_bit4_access_contract as contract
from kb import diagnostic_record_bit4_access_evidence as proof


def row():
    selected,=[row for row in contract.descriptor(repo.ROOT)['reference'] if row['component']=='diagnostic_record_composite_gate_paths']
    return selected


def test_positive_reader_retains_indexed_by_role_reverse_properties_and_complete_native_documents():
    selected=row();old=json.loads(selected['original_claim_json']);new=json.loads(selected['proposed_claim_json'])
    expected=deepcopy(old);expected['evidence'].append(contract.item(selected))
    assert new==expected and old['type']=='reader' and old['roles']==['indexed_by']
    assert selected['original_claim_sha256']=='3efeebbd3eaa8ba22a1a2e8fb3f75996035dc5edd14852ded72d683e95f27468'
    assert old['to']=='ruby-kangaroo/fn' and selected['sites']==[0x259F6,0x25A02]
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    functions={item['owner']:json.loads(item['native_json']) for item in contract.DECLARED['retained_functions']}
    assert {'ruby-kangaroo/fn','diagnostic_record_byte2_fault_predicate/fn'}<=set(functions)
    for name in ('ruby-kangaroo/fn','diagnostic_record_byte2_fault_predicate/fn'):
        selectors=[item for marker in functions[name]['ledger'] for item in marker.get('dependency',())]
        assert any(item['to']=='hallowed-malkoha/ram' and item['type']=='reader' and item['end']=='to' for item in selectors)
        assert functions[name]['contract_level']=='code' and functions[name]['contract']
    assert contract.item(selected)['value']['actual_nested_read']==dict(base=0xFFFF5718,stride=3,member_offset=2,
        width_bytes=1,sites=[0x259F6,0x25A02],callee=0x259E4,mask_bits=[5,6])


@pytest.mark.parametrize('fault',('omit-reader','wrong-direction','remove-indexed_by','sentinel-memory','different-callee','fake-original'))
def test_original_reader_needs_all_exact_joint_normal_positive_appends(fault):
    declared=contract.descriptor(repo.ROOT);ops=[contract.operation(item) for item in declared['reference']]
    assert contract.operations(deepcopy(ops),repo.ROOT) is True
    reader=next(op for op in ops if op['to']=='ruby-kangaroo/fn')
    if fault=='omit-reader':ops.remove(reader)
    elif fault=='wrong-direction':reader['type']='writer'
    elif fault=='remove-indexed_by':reader['evidence'][0]['value']['all_native_TEST_and_ledger_positions_preserved']=False
    elif fault=='sentinel-memory':reader['evidence'][0]['value']['exact_post_delay_arguments'][0]=0
    elif fault=='different-callee':reader['evidence'][0]['value']['actual_nested_read']['callee']=0x25E20
    else:reader['evidence'][0]['value']['original_claim_sha256']='0'*64
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('flag',('exact_diagnostic_record_composite_gate_paths','complete_actual_sentinel_and_short_circuit_calls',
    'complete_nested_indexed_array_reads','complete_CPU_SR_frame_RAM','fixed_other_actual_R0_alternatives',
    'complete_native_owner_function_TEST_ledger','no_array_extent_inference','no_selected_datum_absence_inference','native_bindings'))
def test_reader_owning_result_requires_every_separate_nested_state_and_causal_obligation(flag):
    selected=row();result={key:True for key in proof.COMPONENT_FLAGS[selected['component']]}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-00025a12/fn',
        function_meaning='ruby-kangaroo/fn',original_claim_sha256=selected['original_claim_sha256'])]
    assert proof.require_result(deepcopy(result),selected) is True
    result.pop(flag)
    with pytest.raises(ValueError):proof.require_result(result,selected)


@pytest.mark.parametrize('fault',('writer-original','helper-as-parent','integer-flag','false-absence'))
def test_prior_writer_or_helper_identity_cannot_replace_the_exact_parent_reader(fault):
    selected=row();result={key:True for key in proof.COMPONENT_FLAGS[selected['component']]}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-00025a12/fn',
        function_meaning='ruby-kangaroo/fn',original_claim_sha256=selected['original_claim_sha256'])]
    if fault=='writer-original':result['native_bindings'][0]['original_claim_sha256']=contract.DECLARED['reference'][0]['original_claim_sha256']
    elif fault=='helper-as-parent':result['native_bindings'][0]['function_meaning']='diagnostic_record_byte2_fault_predicate/fn'
    elif fault=='integer-flag':result['complete_nested_indexed_array_reads']=1
    else:result.pop('complete_nested_indexed_array_reads');result['no_selected_datum_access']=True
    with pytest.raises(ValueError):proof.require_result(result,selected)


@pytest.mark.parametrize('fault',('reader-role','reader-direction','reader-TEST','caller-contract','helper-contract','helper-ledger'))
def test_complete_native_images_refuse_any_changed_original_role_TEST_contract_or_selector(monkeypatch,fault):
    declared=deepcopy(contract.DECLARED);selected=next(row for row in declared['reference'] if row['component']=='diagnostic_record_composite_gate_paths')
    if fault in ('caller-contract','helper-contract','helper-ledger'):
        target=next(item for item in declared['retained_functions'] if item['owner']==('ruby-kangaroo/fn' if fault=='caller-contract' else 'diagnostic_record_byte2_fault_predicate/fn'))
        value=json.loads(target['native_json'])
        if fault=='helper-ledger':value['ledger']=[]
        else:value['contract']='partial function'
        target['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_claim_json'])
        if fault=='reader-role':value['roles']=[]
        elif fault=='reader-direction':value['type']='writer'
        else:value['evidence']=[dict(kind='test',path='unrelated',key='unrelated')]
        selected['original_claim_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:declared)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)
