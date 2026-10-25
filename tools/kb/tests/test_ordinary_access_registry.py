"""Ordinary-family registration coverage and controlled shared-route refusals."""

import ast
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from types import SimpleNamespace

import pytest

from kb import copy_evidence,match,repo,test_contract,vocab,write
from kb import ordinary_access_registry as registry
from kb.repo import KbError
from kb.model import Link,Meaning


def discovered_contracts():
    required={'operations','registered','looks_like_access','publication'}
    return {path.stem for path in (repo.ROOT/'tools/kb/src/kb').glob('*contract.py')
        if required<={node.name for node in ast.parse(path.read_text()).body if isinstance(node,ast.FunctionDef)}}


def test_each_existing_ordinary_contract_has_one_authoritative_entry_and_complete_consumers():
    families=registry.require_bindings()
    assert {family.contract_name for family in families}==discovered_contracts()
    assert len(families)==len({family.mode for family in families})
    assert set(registry.MODES)<=set(vocab.INDIRECT_MODES)
    assert set(registry.EXECUTION_FILES)<=set(copy_evidence.EXECUTION_FILES)
    for family in families:
        assert family.contract.DESCRIPTOR in family.sources
        assert {component for component,producer in family.captures}==set(family.evidence.COMPONENTS)
        assert set(family.source_files)<=set(copy_evidence.EXECUTION_FILES)


def test_natural_CVTC_family_uses_one_registration_for_all_eleven_owning_relations_and_its_raw_component():
    family=next(row for row in registry.FAMILIES if row.mode=='exhaust-cvtc-access')
    assert family.captures==(('exhaust_cvtc_transition_paths','exhaust_cvtc_capture'),)
    assert set(family.evidence.COMPONENTS)=={'exhaust_cvtc_transition_paths'}
    rows=family.contract.descriptor(repo.ROOT)['reference']
    assert len(rows)==11 and len({row['owner'] for row in rows})==6
    for row in rows:
        assert registry.matching(family.contract.item(row))==(family,)
    for name in ('test_ram_structure.py','test_indexed_input_word.py'):
        assert 'tools/kb/tests/'+name in family.source_files


@pytest.mark.parametrize('fault',('missing','empty','duplicate','mode','contract','evidence','resolution','capture','producer'))
def test_missing_duplicate_or_inconsistent_registration_refuses_before_routing(monkeypatch,fault):
    entries=list(registry.FAMILIES);first,second=entries[:2]
    if fault=='missing':entries.pop()
    elif fault=='empty':entries=[]
    elif fault=='duplicate':entries.append(first)
    elif fault in ('mode','contract','evidence','resolution'):
        field=fault if fault=='mode' else fault+'_name'
        entries[1]=replace(second,**{field:getattr(first,field)})
    else:
        binding=list(second.captures[0]);binding[0 if fault=='capture' else 1]=first.captures[0][0 if fault=='capture' else 1]
        entries[1]=replace(second,captures=(tuple(binding),*second.captures[1:]))
    monkeypatch.setattr(registry,'FAMILIES',tuple(entries))
    with pytest.raises(ValueError):registry.require_bindings()


@pytest.mark.parametrize('fault',('missing-consumer','extra-consumer','non-callable','missing-descriptor-source','wrong-mode','missing-producer-source'))
def test_registration_requires_exact_independent_consumer_and_source_coverage(monkeypatch,fault):
    family=next(row for row in registry.FAMILIES if row.mode=='rpm-inhibit-access')
    if fault in ('missing-consumer','extra-consumer'):
        components=dict(family.evidence.COMPONENTS)
        if fault=='missing-consumer':components.pop(family.captures[0][0])
        else:components['unregistered_capture']=next(iter(components.values()))
        monkeypatch.setattr(family.evidence,'COMPONENTS',components)
    elif fault=='non-callable':monkeypatch.setattr(family.resolution,'publication_expected',None)
    elif fault=='wrong-mode':
        original=family.contract.registered
        monkeypatch.setattr(family.contract,'registered',lambda item:False if set(item)=={'mode'} else original(item))
    else:
        changed=replace(family,sources=tuple(path for path in family.sources if path!=family.contract.DESCRIPTOR))
        if fault=='missing-producer-source':changed=replace(family,captures=((family.captures[0][0],'unbound_capture'),))
        monkeypatch.setattr(registry,'FAMILIES',tuple(changed if row is family else row for row in registry.FAMILIES))
    with pytest.raises(ValueError):registry.require_bindings()


@pytest.mark.parametrize('family',registry.FAMILIES,ids=lambda row:row.mode)
@pytest.mark.parametrize('failure',(None,'controlled unqualified original'))
def test_each_registered_namespace_routes_validation_and_rank_through_its_existing_proof(monkeypatch,family,failure):
    row=family.contract.descriptor(repo.ROOT)['reference'][0]
    item=(dict(kind='indirect',mode=family.mode,path=family.contract.DESCRIPTOR,key=family.contract.PREFIX+row['id'])
        if family.withdrawal_only else family.contract.item(row))
    symbol=SimpleNamespace(key=family.contract.symbol_key(row),meaning=SimpleNamespace(key=row['owner']))
    model=SimpleNamespace(root=repo.ROOT);calls=[]
    def controlled(evidence,actual_symbol=None,actual_model=None,claim=None):
        calls.append((evidence,actual_symbol,actual_model,claim))
        return failure
    monkeypatch.setattr(family.evidence,'failure',controlled)
    assert registry.matching(item)==(family,)
    assert copy_evidence.registered(item,symbol)
    if family.withdrawal_only:
        assert match.verify(model,symbol,item)=='an ordinary withdrawal grants no owning evidence or supported fact'
        assert match.rank(item,symbol,model,'identity')==-1
        assert calls==[]
        return
    assert match.verify(model,symbol,item)==failure
    assert match.rank(item,symbol,model,'identity')==(vocab.LEVEL_RANK['code'] if failure is None else -1)
    assert calls and all(test_contract.exact(call[0],item) and call[1] is symbol and call[2] is model for call in calls)


@pytest.mark.parametrize('family',registry.FAMILIES,ids=lambda row:row.mode)
@pytest.mark.parametrize('other',('ordinary','CAN','I/O'))
def test_cross_namespace_ambiguity_cannot_reach_an_independent_admission(monkeypatch,family,other):
    item=dict(kind='indirect',mode=family.mode,key=family.contract.PREFIX+'controlled')
    if other=='ordinary':
        next_family=next(row for row in registry.FAMILIES if row is not family)
        item['path']=next_family.contract.DESCRIPTOR
    elif other=='CAN':item['path']=copy_evidence.DESCRIPTOR
    else:
        from kb import io_access_claim_contract
        item['path']=io_access_claim_contract.DESCRIPTOR
    def forbidden(*args,**kwargs):pytest.fail('ambiguous metadata reaches domain admission')
    monkeypatch.setattr(family.evidence,'failure',forbidden)
    assert copy_evidence.failure(item,None,None,'identity')=='ambiguous reserved access execution proof'


@pytest.mark.parametrize('family',registry.FAMILIES,ids=lambda row:row.mode)
def test_joint_writer_selection_keeps_all_original_operation_shapes_and_refuses_a_missing_claim(family):
    rows=family.contract.descriptor(repo.ROOT)['reference'];ops=[family.contract.operation(row) for row in rows]
    if not family.withdrawal_only and callable(getattr(family.contract,'removal',None)):
        ops.extend(family.contract.removal(row) for row in rows if family.contract.correction(row))
    assert registry.operation_families(ops,repo.ROOT)==(family,)
    write.require_publication_operations(ops)
    with pytest.raises(KbError):write.require_publication_operations(ops[1:])
    with pytest.raises(KbError):write.require_publication_operations([*ops,deepcopy(ops[0])])


@pytest.mark.parametrize('family',tuple(row for row in registry.FAMILIES if not row.withdrawal_only),ids=lambda row:row.mode)
def test_owning_acceptance_and_exact_retirement_reuse_existing_family_hooks(monkeypatch,family):
    row=family.contract.descriptor(repo.ROOT)['reference'][0]
    claim=json.loads(row['proposed_claim_json']);old=json.loads(row['original_claim_json'])
    symbol=SimpleNamespace(meaning=SimpleNamespace(key=row['owner']))
    before,after,function=object(),object(),object();accepted=object();calls=[]
    def accept(model,actual_symbol,actual_function,actual_claim):
        calls.append((model,actual_symbol,actual_function,actual_claim));return accepted
    monkeypatch.setattr(family.evidence,'accepted',accept)
    monkeypatch.setattr(family.resolution,'retires',lambda actual_before,actual_after,actual_claim:
        actual_before is before and actual_after is after and test_contract.exact(actual_claim,old))
    assert copy_evidence.accepted(after,symbol,function,claim) is accepted
    assert calls==[(after,symbol,function,claim)]
    assert copy_evidence.retires(before,after,old) is True
    altered=deepcopy(old);altered['slot']='unregistered'
    if not family.owner_fallback:assert registry.original_family(altered) is None


def test_MAF_battery_extension_and_RPM_group_share_global_routing_without_capture_duplication():
    maf=next(row for row in registry.FAMILIES if row.mode=='maf-access')
    rpm=next(row for row in registry.FAMILIES if row.mode=='rpm-inhibit-access')
    rows=maf.contract.descriptor(repo.ROOT)['reference']
    battery=next(row for row in rows if row['address']==0xFFFF4970 and row['function']==0x39A9E)
    assert battery['component']=='maf_extended_paths'
    assert [component for component,producer in maf.captures].count(battery['component'])==1
    assert registry.matching(maf.contract.item(battery))==(maf,)
    rpm_rows=rpm.contract.descriptor(repo.ROOT)['reference']
    assert {row['component'] for row in rpm_rows}=={component for component,producer in rpm.captures}
    assert ('rpm_inhibit_paths','rpm_inhibit_capture') in rpm.captures
    assert ('rpm_remaining_inhibit_paths','rpm_remaining_inhibit_capture') in rpm.captures
    assert all(registry.matching(rpm.contract.item(row))==(rpm,) for row in rpm_rows)


def test_the_registry_and_all_family_descriptors_share_current_primary_source_provenance():
    from kb import copy_witness,ignition_literal_evidence
    producer=copy_witness.provenance(repo.ROOT);consumer=ignition_literal_evidence.execution_inputs(repo.ROOT)
    for path in registry.EXECUTION_FILES:
        identity=hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()
        assert producer[path]==consumer[path]==identity


def test_distinct_I_O_dispositions_and_legacy_guarded_level_policies_remain_separate():
    assert {family.mode for family in registry.FAMILIES if not family.direct_owning}=={
        'ram-clear-access','counter-array-access','register-only-withdrawal','scalar-ram-leaf-withdrawal'}
    assert 'io-access' not in registry.MODES
    assert {family.mode for family in registry.FAMILIES if family.owner_fallback}=={'maf-access'}


@pytest.mark.parametrize('family',tuple(row for row in registry.FAMILIES if not row.withdrawal_only),ids=lambda row:row.mode)
def test_only_the_unique_exact_owning_append_is_neutral_to_existing_physical_scopes(family):
    row=family.contract.descriptor(repo.ROOT)['reference'][0]
    claim=json.loads(row['proposed_claim_json'])
    owner=Meaning(claim['owner'].rsplit('/',1)[1],name=claim['owner'].rsplit('/',1)[0])
    target=Meaning('fn',name=claim['to'].rsplit('/',1)[0])
    link=Link(owner,claim['type'],target,claim['slot'],claim['offset'],deepcopy(claim['props']),
        deepcopy(claim['evidence']),set(claim['stated']),set(claim['sources']),set(claim['roles']))
    assert copy_evidence.semantic_evidence(link)==json.loads(row['original_claim_json'])['evidence']
    own=family.contract.item(row);link.evidence.append(deepcopy(own))
    assert copy_evidence.semantic_evidence(link)==link.evidence
    link.evidence.pop();link.evidence[-1]['value']['direction']='unregistered'
    assert copy_evidence.semantic_evidence(link)==link.evidence


def test_joint_writer_plan_binds_every_selected_existing_transition_without_late_closure_capture(monkeypatch):
    from kb import reconciliation,research,retirement
    families=tuple(row for row in registry.FAMILIES if row.mode in (
        'closed-loop-admission-access','rpm-inhibit-access'))
    ops=[family.contract.operation(row) for family in families
        for row in family.contract.descriptor(repo.ROOT)['reference']]
    before=SimpleNamespace(root=repo.ROOT,overlay={});after=SimpleNamespace(root=repo.ROOT,overlay={})
    change=SimpleNamespace(expected=[],run=lambda *args:None,texts=lambda:{},renamed={},
        width_resolutions={},diagnostic_resolutions={},argument_resolutions={},calculation_resolutions={},
        io_resolutions={},snapshot_resolutions={})
    monkeypatch.setattr(write,'Change',lambda *args:change)
    monkeypatch.setattr(write.compile,'build',lambda *args:after)
    monkeypatch.setattr(write,'refusals',lambda *args:[])
    monkeypatch.setattr(reconciliation,'rebase',lambda *args,**kwargs:None)
    monkeypatch.setattr(research,'preservation',lambda *args:[])
    monkeypatch.setattr(retirement,'preserved',lambda *args:[])
    calls=[]
    for family in families:
        monkeypatch.setattr(family.resolution,'require_transition',lambda actual_before,actual_after,family=family:
            calls.append((family,actual_before,actual_after)))
    actual,texts,result=write.plan(ops,before,object(),repo.ROOT)
    assert actual is change and texts=={} and result is after
    assert len(change.expected)==len(families)
    assert calls==[(family,before,after) for family in families]


@pytest.mark.parametrize('component,producer',registry.captures())
@pytest.mark.parametrize('fault',('missing','empty','not-table'))
def test_the_complete_primary_requires_every_registered_capture_without_granting_semantic_admission(component,producer,fault):
    packet={key:dict(controlled_only=True,semantic_admission=False) for key,name in registry.captures()}
    assert registry.require_captures(packet) is None
    if fault=='missing':packet.pop(component)
    elif fault=='empty':packet[component]={}
    else:packet[component]=[dict(controlled_only=True)]
    with pytest.raises(ValueError):registry.require_captures(packet)
