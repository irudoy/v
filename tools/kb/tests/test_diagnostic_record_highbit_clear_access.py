"""One additional exact writer retains the complete shared array, function and TEST facts."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import diagnostic_record_bit4_access_contract as contract
from kb import diagnostic_record_bit4_access_evidence as proof


def row():
    selected,=[r for r in contract.descriptor(repo.ROOT)['reference'] if r['component']=='diagnostic_record_highbit_clear_paths']
    return selected


def test_exact_highbit_writer_append_preserves_all_shared_native_and_function_facts():
    declared=contract.descriptor(repo.ROOT);selected=row();rows=declared['reference']
    assert selected['original_claim_sha256']=='0e678170c81620a6a4cdf9506fc54f5b3c460ff14a59b9a157a01b6b8164205b'
    claim=json.loads(selected['original_claim_json'])
    assert (claim['owner'],claim['to'],claim['type'])==('hallowed-malkoha/ram','tough-avocet/fn','writer')
    assert claim['roles']==[] and claim['slot'] is None and claim['offset'] is None
    before=json.loads(selected['original_native_json']);after=json.loads(selected['proposed_native_json']);stripped=deepcopy(after)
    for item in rows:
        original=json.loads(item['original_claim_json'])
        target,=[r for r in stripped['link'] if (r['type'],r['to'])==(original['type'],original['to'])]
        assert target['evidence'].pop()==contract.item(item)
        if not target['evidence']:target.pop('evidence')
        assert item['proposed_native_json']==selected['proposed_native_json']
        assert item['original_ledger_json']==item['proposed_ledger_json']
    assert stripped==before and before['symbol']==after['symbol'] and before['ledger']==after['ledger']
    functions={r['owner']:json.loads(r['native_json']) for r in declared['retained_functions']}
    fn=functions['tough-avocet/fn']
    assert fn['contract']=='Input r4 is a record index; -1 returns without a write.'
    selectors=[r for marker in fn['ledger'] for r in marker.get('dependency',[])]
    assert any((r.get('to'),r.get('type'),r.get('end'))==('hallowed-malkoha/ram','writer','to') for r in selectors)
    assert selected['sites']==[0x8C360]
    evidence=contract.item(selected)
    assert evidence['supports']=='identity' and evidence['at']=='7mfk:0008c360'
    for key in ('scale_admission','units_admission','native_geometry_inference','natural_caller_reachability',
            'natural_scheduling_inference','hardware_qualification'):
        assert evidence['value'][key] is False


@pytest.mark.parametrize('fault',('omit-selected','duplicate','reader-direction','wrong-mask','wrong-delay','low16-index'))
def test_joint_normal_owning_operations_refuse_any_broadened_or_partial_highbit_attachment(fault):
    rows=contract.descriptor(repo.ROOT)['reference'];ops=[contract.operation(r) for r in rows]
    assert contract.operations(deepcopy(ops),repo.ROOT) is True
    op=next(op for op in ops if op['to']=='tough-avocet/fn')
    if fault=='omit-selected':ops.remove(op)
    elif fault=='duplicate':ops.append(deepcopy(op))
    elif fault=='reader-direction':op['type']='reader'
    elif fault=='wrong-mask':op['evidence'][0]['value']['actual_indexed_write']['mask']=0xFF
    elif fault=='wrong-delay':op['evidence'][0]['at']='7mfk:0008c35e'
    else:op['evidence'][0]['value']['full_raw_R4_not_low16']=False
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('flag',('exact_diagnostic_record_highbit_clear_paths','complete_AND7F_read_write_RTS_delay',
    'complete_sentinel_no_RAM_access','complete_full_R4_modulo_addressing','complete_CPU_SR_frame_RAM',
    'complete_physical_member_preimages_and_publications','fixed_other_actual_common_member_alternatives',
    'complete_native_owner_function_TEST_ledger','no_array_extent_inference','no_selected_datum_absence_inference','native_bindings'))
@pytest.mark.parametrize('fault',('omit','false','integer'))
def test_owning_boundary_requires_every_independent_highbit_obligation(flag,fault):
    selected=row();result={name:True for name in proof.COMPONENT_FLAGS[selected['component']]}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c348/fn',
        function_meaning='tough-avocet/fn',original_claim_sha256=selected['original_claim_sha256'])]
    assert proof.require_result(deepcopy(result),selected) is True
    if fault=='omit':result.pop(flag)
    else:result[flag]=False if fault=='false' else 1
    with pytest.raises(ValueError):proof.require_result(result,selected)


@pytest.mark.parametrize('fault',('other-original','other-function','other-owner','sentinel-omission','other-component'))
def test_other_writers_and_the_sentinel_cannot_donate_positive_array_identity(fault):
    selected=row();result={name:True for name in proof.COMPONENT_FLAGS[selected['component']]}
    binding=dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c348/fn',
        function_meaning='tough-avocet/fn',original_claim_sha256=selected['original_claim_sha256'])
    result['native_bindings']=[binding]
    if fault=='other-original':binding['original_claim_sha256']=contract.DECLARED['reference'][0]['original_claim_sha256']
    elif fault=='other-function':binding['function_meaning']='cherry-wildcat/fn'
    elif fault=='other-owner':binding['meaning']='gigantic-lizard/ram'
    elif fault=='sentinel-omission':result['complete_sentinel_no_RAM_access']=False
    else:result.pop('exact_diagnostic_record_highbit_clear_paths');result['exact_diagnostic_record_bit4_paths']=True
    with pytest.raises(ValueError):proof.require_result(result,selected)
