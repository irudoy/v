"""Exact native removal, original TEST context, writer and no-donation refusals."""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tomllib
from types import SimpleNamespace

import pytest

from kb import compile,copy_evidence,levels,match,reconciliation,repo,store,test_contract,test_origins,write
from kb import ordinary_access_registry as registry
from kb import register_only_withdrawal_contract as contract,register_only_withdrawal_evidence as proof
from kb import register_only_withdrawal_resolution as resolution
from kb.repo import KbError


@pytest.fixture(scope='module')
def models():
    rows=contract.descriptor(repo.ROOT)['reference']
    overlays={phase:{Path(row['source']):store.render(row['owner'].rsplit('/',1)[1],
        json.loads(row[phase+'_native_json'])) for row in rows} for phase in ('original','proposed')}
    return rows,compile.build(repo.ROOT,overlays['original']),compile.build(repo.ROOT,overlays['proposed'])


def test_twelve_exact_withdrawals_retain_all_eleven_complete_native_owners_and_test_positions(models):
    rows,before,after=models
    assert proof.native_rows(before,'original')==proof.native_rows(after,'proposed')==rows
    assert {key:value.packet() for key,value in test_origins.index(before).items()}=={
        key:value.packet() for key,value in test_origins.index(after).items()}
    for row in rows:
        assert 'proposed_claim_json' not in row and 'evidence_json' not in row
        assert json.loads(row['original_claim_json'])['evidence']==[]
        old,new=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        assert old['symbol']==new['symbol']
        assert {key:value for key,value in old.items() if key not in ('link','ledger')}=={
            key:value for key,value in new.items() if key not in ('link','ledger')}


def test_existing_unlink_writer_produces_exact_grouped_native_postimages_without_replacement(models):
    rows,model,_=models;owners={meaning.key:meaning for meaning in model.meanings}
    documents={row['owner']:json.loads(row['original_native_json']) for row in rows}
    change=object.__new__(write.Change);change.model,change.lines=model,[]
    change._ends=lambda op:(owners[op['meaning']],owners[op['to']],op['type'])
    change._held=lambda meaning:documents.get(meaning.key)
    for row in rows:change.unlink(contract.operation(row))
    assert all(test_contract.exact(tomllib.loads(store.render(row['owner'].rsplit('/',1)[1],documents[row['owner']])),
        json.loads(row['proposed_native_json'])) for row in rows)
    assert all(line.startswith('unlink ') for line in change.lines) and len(change.lines)==12


def test_joint_publication_permits_only_selected_links_and_matching_ledger_selectors(models,monkeypatch):
    rows,before,after=models;after=deepcopy(after)
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_only=True))
    selected={('access',contract.symbol_key(row).key,row['original_claim_sha256']) for row in rows}
    reviews=before.config['reconciliation']['review']
    assert len([row for row in reviews if reconciliation.difference_key(row) in selected])==12
    after.config['reconciliation']['review']=[row for row in reviews if reconciliation.difference_key(row) not in selected]
    expected=resolution.publication_expected(before,after,write.publication_view(before))
    assert test_contract.exact(expected,write.publication_view(after))
    ops=[contract.operation(row) for row in rows]
    write.require_metadata_only(before,after,ops,SimpleNamespace(width_resolutions={}),{})
    assert all(resolution.retires(before,after,json.loads(row['original_claim_json'])) for row in rows)


@pytest.mark.parametrize('fault',('extra-review','changed-review','missing-admission'))
def test_review_retirement_requires_only_the_twelve_exact_originals_and_complete_admission(models,monkeypatch,fault):
    rows,before,after=models;after=deepcopy(after)
    selected={('access',contract.symbol_key(row).key,row['original_claim_sha256']) for row in rows}
    after.config['reconciliation']['review']=[deepcopy(row) for row in before.config['reconciliation']['review']
        if reconciliation.difference_key(row) not in selected]
    def current(model):
        if fault=='missing-admission':raise ValueError('controlled missing complete original')
        return dict(controlled_only=True)
    monkeypatch.setattr(proof,'require_current',current)
    if fault=='extra-review':after.config['reconciliation']['review'].pop()
    elif fault=='changed-review':after.config['reconciliation']['review'][0]['reason']='unregistered'
    with pytest.raises(KbError):write.require_metadata_only(before,after,[contract.operation(row) for row in rows],
        SimpleNamespace(width_resolutions={}),{})


@pytest.mark.parametrize('fault',('partial','duplicate','owner','type','target','keys','evidence','extra'))
def test_preflight_rejects_partial_changed_broader_or_unmatched_withdrawals(fault):
    rows=contract.descriptor(repo.ROOT)['reference'];ops=[contract.operation(row) for row in rows]
    if fault=='partial':ops.pop()
    elif fault=='duplicate':ops[-1]=deepcopy(ops[0])
    elif fault=='owner':ops[0]['meaning']='other/tbl'
    elif fault=='type':ops[0]['type']='writer'
    elif fault=='target':ops[0]['to']='other/fn'
    elif fault=='keys':ops[0]['keys']={'slot':'unregistered'}
    elif fault=='evidence':ops[0]['evidence']=[dict(kind='indirect',mode=contract.MODE)]
    else:ops.append(dict(cmd='unlink',meaning=rows[0]['owner'],type='reader',to='other/fn'))
    with pytest.raises(KbError):write.require_publication_operations(ops)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_withdrawal_descriptor_refuses_identity_scale_replacement_or_publication_flags(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field',('original_claim_sha256','original_native_sha256','proposed_native_sha256'))
def test_withdrawal_descriptor_pins_each_complete_original_and_native_image(tmp_path,field):
    row=contract.descriptor(repo.ROOT)['reference'][0]
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    path.write_text(text.replace(field+' = "'+row[field]+'"',field+' = "'+'0'*64+'"',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('flag',('exact_register_only_paths','no_datum_access','native_identity_admission'))
def test_withdrawal_requires_both_independent_domain_flags_without_identity_admission(models,monkeypatch,flag):
    _,before,_=models
    result=dict(exact_register_only_paths=True,no_datum_access=True,native_identity_admission=False)
    result[flag]=not result[flag]
    monkeypatch.setattr(proof.capture_consumer,'require_primary',lambda *args:result)
    with pytest.raises(ValueError):proof.require_primary(before,dict(controlled_only=True))


def test_changed_existing_physical_namespace_cannot_be_hidden_by_withdrawal_admission(models,monkeypatch):
    _,before,after=models
    monkeypatch.setattr(copy_evidence,'scope_digest',lambda model:'before' if model is before else 'after')
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_only=True))
    with pytest.raises(ValueError):resolution.require_transition(before,after)


@pytest.mark.parametrize('fault',('property','type','TEST','TEST-order','link-order','other-link','ledger-field','ledger-identity','ledger-note','selector'))
def test_full_native_postimage_refuses_any_unrelated_value_or_position(models,monkeypatch,fault):
    rows,_,after=models;row=next(row for row in rows if row['owner']=='fuel_inhibit_mask/ram')
    changed=json.loads(row['proposed_native_json'])
    if fault=='property':changed['unit']='unregistered'
    elif fault=='type':changed['width']=16
    elif fault=='TEST':changed['symbol'][0]['evidence'].pop()
    elif fault=='TEST-order':changed['symbol'][0]['evidence'].reverse()
    elif fault=='link-order':changed['link'].reverse()
    elif fault=='other-link':changed['link'].pop()
    elif fault=='ledger-field':changed['ledger'][0]['fields'].append('other')
    elif fault=='ledger-identity':changed['ledger'][0]['identity'].append(999)
    elif fault=='ledger-note':changed['ledger'][0]['notes'].append(999)
    else:changed['ledger'][0]['dependency'].pop()
    load=store.load
    monkeypatch.setattr(store,'load',lambda root,path,overlay=None:deepcopy(changed)
        if str(path)==row['source'] else load(root,path,overlay))
    with pytest.raises(ValueError):proof.native_rows(after,'proposed')


@pytest.mark.parametrize('field,value',(('mode','base'),('key',contract.PREFIX+'other'),('supports','identity'),('supports','scale')))
def test_reserved_withdrawal_namespace_cannot_donate_any_owning_fact(models,monkeypatch,field,value):
    rows,before,_=models;row=rows[0];symbol=before.symbols[contract.symbol_key(row)]
    function=next(member for member in before.symbols.values() if member.kind=='fn' and member.address==row['function'])
    item=dict(kind='indirect',mode=contract.MODE,path=contract.DESCRIPTOR,key=contract.PREFIX+row['id']);item[field]=value
    monkeypatch.setattr(proof,'accepted',lambda *args:pytest.fail('withdrawal reaches owning admission'))
    assert copy_evidence.failure(item,symbol,before,'identity') is not None
    assert match.rank(item,symbol,before,'identity')==-1
    claim=json.loads(row['original_claim_json']);claim['evidence']=[item]
    assert copy_evidence.accepted(before,symbol,function,claim) is None
    assert contract.publication(None,item) is False and registry.publication(None,item) is False
    assert proof.identity_only(symbol) is False


def test_withdrawal_registration_cannot_enable_direct_owning_or_owner_fallback(monkeypatch):
    family=next(row for row in registry.FAMILIES if row.withdrawal_only)
    assert family.mode==contract.MODE and not family.direct_owning and not family.owner_fallback
    for field in ('direct_owning','owner_fallback'):
        monkeypatch.setattr(registry,'FAMILIES',tuple(replace(row,**{field:True}) if row is family else row
            for row in registry.FAMILIES))
        with pytest.raises(ValueError):registry.families()
        monkeypatch.undo()


def test_reuse_description_exposes_withdrawal_without_inventing_a_proposed_claim_or_evidence():
    from kb import proof_reuse
    selected=[row for row in proof_reuse.index(repo.ROOT)['references'] if row['family']==contract.MODE]
    assert len(selected)==12
    assert {row['original'] for row in selected}=={row[10] for row in contract.IDENTITIES}
    assert all(row['disposition']=='withdrawal' and row['evidence'] is None and row['width'] is None
        and row['source_prepared'] is True and row['accepted'] is False for row in selected)


def test_withdrawal_never_donates_owning_scale_or_reverse_identity_through_level_collection(models,monkeypatch):
    rows,model,_=models;row=next(row for row in rows if row['owner']=='woodoo-loon/tbl')
    link=next(link for link in model.links if contract.original(row,link))
    own=levels.Claim('controlled','owner','identity','code')
    scale=levels.Claim('controlled','scale','scale','code');reverse=levels.Claim('controlled','fn','identity','code')
    collector=object.__new__(levels._Collector);collector.model,collector.pointed,collector.symbols=model,set(),{}
    collector.meanings={(id(link.owner),'identity'):own,(id(link.owner),'scale'):scale,(id(link.to),'identity'):reverse}
    monkeypatch.setattr(proof,'link_failure',lambda *args:None)
    collector._link(link)
    assert own.items==[] and len(own.deps)==1 and own.deps[0].lacks
    assert scale.items==scale.deps==reverse.items==reverse.deps==[]
