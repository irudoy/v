"""Both exact retained owning operations, complete native types and refusal boundaries."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import centered_channel_duty_access_contract as contract

def rows():return contract.descriptor(repo.ROOT)['reference']
def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))

def test_exact_appends_keep_complete_owner_functions_types_and_original_claims():
    selected=rows()
    assert [(r['kind'],r['address'],r['direction'],r['channel']) for r in selected]==[
        ('tbl',0x12E72,'reader',0),('ram',0xFFFF2441,'writer',1)]
    for row in selected:
        before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
        claim=json.loads(row['original_claim_json']);stripped=deepcopy(after)
        target,=[r for r in stripped['link'] if (r['type'],r['to'])==(claim['type'],claim['to'])]
        old_target,=[r for r in before['link'] if (r['type'],r['to'])==(claim['type'],claim['to'])]
        assert target['evidence'].pop()==contract.item(row)
        if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
        assert stripped==before and row['original_ledger_json']==row['proposed_ledger_json']
        assert row['declared_signed']=='unset'
        assert contract.native_type(row,'width')==(None if row['kind']=='tbl' else 8)
        value=contract.item(row)['value']
        assert value['channel']==row['channel'] and value['direction']==row['direction']
        assert value['actual_output']==dict(address=0xFFFF2440+row['channel'],width_bytes=1,write_site=0xBE8DC)
        assert value['source_table_reads_belong_to_producer'] is True
        assert value['stock_implicit_table_active_inference'] is False
        for key in ('native_geometry_inference','scale_admission','units_admission','natural_caller_reachability',
            'natural_scheduling_inference','hardware_qualification'):assert value[key] is False
    assert [(r['owner'],r['address']) for r in contract.DECLARED['retained_functions']]==[
        ('careful-armadillo/fn',0xBE5BC),('ludicrous-albatross/fn',0xBE814)]

@pytest.mark.parametrize('fault',('half-pair','reverse-order','duplicate','other-owner','other-direction','scale-support','other-channel','forged-original'))
def test_normal_writer_requires_both_exact_ordered_evidence_appends(fault):
    selected=rows();ops=[contract.operation(row) for row in selected]
    assert contract.operations(deepcopy(ops),repo.ROOT) is True
    if fault=='half-pair':ops.pop()
    elif fault=='reverse-order':ops.reverse()
    elif fault=='duplicate':ops.append(deepcopy(ops[0]))
    elif fault=='other-owner':ops[0]['meaning']='unrelated/tbl'
    elif fault=='other-direction':ops[1]['type']='reader'
    elif fault=='scale-support':ops[0]['evidence'][0]['supports']='scale'
    elif fault=='other-channel':ops[1]['evidence'][0]['value']['channel']=0
    else:ops[0]['evidence'][0]['value']['original_claim_sha256']='0'*64
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)

@pytest.mark.parametrize('selected',(0,1))
@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','physical-reader'))
def test_only_each_unique_exact_append_is_neutral_to_existing_physical_scopes(selected,fault):
    row=rows()[selected];item=contract.item(row);current=link(json.loads(row['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(row['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='writer' if current.type=='reader' else 'reader'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['source_table_reads_belong_to_producer']=False
    assert contract.publication(current,item) is False

@pytest.mark.parametrize('fault',('owner-summary','other-link','semantic-width','ledger','function'))
def test_full_native_preimages_refuse_unrelated_fact_changes(monkeypatch,fault):
    document=deepcopy(contract.DECLARED)
    if fault=='function':
        row=document['retained_functions'][0];value=json.loads(row['native_json'])
        value['summary']='partial producer';row['native_json']=json.dumps(value)
    else:
        row=document['reference'][0];value=json.loads(row['original_native_json'])
        if fault=='owner-summary':value['summary']='partial table'
        elif fault=='other-link':value['link']=value['link'][:-1]
        elif fault=='semantic-width':value['width']=16
        else:value['ledger']=[]
        row['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)

def test_exact_namespace_has_no_other_owner_or_absence_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('coasting-term-quantity-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    current=link(json.loads(rows()[0]['original_claim_json']));assert contract.looks_like_access(current)
    current.owner.key='unrelated/tbl';assert not contract.looks_like_access(current)
