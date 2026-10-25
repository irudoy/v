"""Exact argument dispositions and refusal of unrelated native changes."""

from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import timing_argument_contract as contract,timing_argument_evidence as proof
from kb import timing_argument_resolution as resolution,levels,repo,test_contract,write
from kb import copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence
from kb.model import Link,Meaning,Model,Symbol,SymbolKey
from kb.repo import KbError


def representation(row,meanings,dependency=False):
    claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
    return Link(meanings[claim['owner']],claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
        deepcopy(claim['props']),[contract.item(row)] if dependency else [],
        set(claim['stated']),set(claim['sources']),set(claim['roles']))


@pytest.fixture
def transition(tmp_path,monkeypatch):
    declared=contract.descriptor(repo.ROOT)
    monkeypatch.setattr(contract,'descriptor',lambda root:deepcopy(declared))
    before=Model({}, {}, {}, {}, [])
    before.root=tmp_path;before.spaces={};before.functions={};before.names=[]
    before.config={'reconciliation':{'enabled':True,'review':[]}}
    meanings={}
    def add(owner,kind,address):
        meaning=Meaning(kind,name=owner.rsplit('/',1)[0],sources={'controlled-native.toml'})
        meanings[owner]=meaning;before.meanings.append(meaning)
        key=SymbolKey('7mfk',kind,address)
        symbol=Symbol(key,meaning=meaning,sources={'controlled-native.toml'})
        before.symbols[key]=symbol;meaning.symbols['7mfk']=symbol
    add(contract.TARGET,'fn',contract.FUNCTION.address)
    for row in declared['reference']:
        add(row['owner'],'tbl',row['address'])
        before.links.append(representation(row,meanings))
        path=tmp_path/json.loads(row['original_claim_json'])['sources'][0]
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text('controlled original source')
        before.stash.setdefault('ledger_rows',[]).append(('tbl',row['owner'].rsplit('/',1)[0],
            json.loads(row['original_ledger_json']),json.loads(row['original_claim_json'])['sources'][0]))
    for link in before.links:link.owner.links.append(link)
    after=deepcopy(before);owners={meaning.key:meaning for meaning in after.meanings}
    after.links=[representation(row,owners,True) for row in declared['reference']]
    for meaning in after.meanings:meaning.links=[]
    for link in after.links:link.owner.links.append(link)
    after.stash['ledger_rows']=[('tbl',row['owner'].rsplit('/',1)[0],json.loads(row['proposed_ledger_json']),
        json.loads(row['original_claim_json'])['sources'][0]) for row in declared['reference']]
    resolutions={row['id']:row['original_claim_sha256'] for row in declared['reference']}
    operations=[dict(cmd='reconcile-timing-argument',id=key,claim_sha256=value) for key,value in resolutions.items()]
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_admission=True))
    # These objects exercise metadata comparisons only. Actual complete
    # namespace preservation is covered against the qualified original.
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        monkeypatch.setattr(module,'scope_digest',lambda model:'controlled-scope')
    return declared,before,after,resolutions,operations


def test_all_exact_replacements_preserve_the_complete_other_native_view(transition):
    declared,before,after,resolutions,operations=transition
    expected=resolution.publication_expected(before,after,resolutions,
        write.publication_view(before),write.publication_view(after))
    assert test_contract.exact(expected,write.publication_view(after))
    for row,old,new in zip(declared['reference'],before.links,after.links):
        assert contract.original(row,old) and contract.dependency(row,new)
        assert contract.registered(contract.item(row))
        assert contract.item(row)['value']['physical_reader_inference'] is False
    change=SimpleNamespace(width_resolutions={},diagnostic_resolutions={},argument_resolutions=resolutions)
    path=before.root/repo.OWNER_CONFIG;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('controlled reviews')
    write.require_metadata_only(before,after,operations,change,{repo.OWNER_CONFIG:'controlled reviews'})


@pytest.mark.parametrize('fault',('partial','wrong-sha','extra-property','geometry','extra-evidence',
    'changed-role','changed-via','changed-layout','ledger-selector','ledger-order','ledger-source','extra-TEST'))
def test_argument_transition_refuses_extra_native_or_origin_changes(transition,fault):
    declared,before,after,resolutions,_=transition
    relation=after.links[0];symbol=after.symbols[SymbolKey('7mfk','tbl',declared['reference'][0]['address'])]
    if fault=='partial':resolutions.pop(next(iter(resolutions)))
    elif fault=='wrong-sha':resolutions[next(iter(resolutions))]='0'*64
    elif fault=='extra-property':symbol.meaning.props['units']='degree'
    elif fault=='geometry':symbol.props['rows']=8
    elif fault=='extra-evidence':relation.evidence.append({'kind':'arithmetic','value':'1=1'})
    elif fault=='changed-role':relation.roles.add('scale')
    elif fault=='changed-via':relation.props['via']=[]
    elif fault=='changed-layout':relation.stated.add('1nd')
    elif fault=='ledger-selector':after.stash['ledger_rows'][0][2][0]['dependency']=[]
    elif fault=='ledger-order':after.stash['ledger_rows'][0][2][0]['identity'].reverse()
    elif fault=='ledger-source':
        kind,name,ledger,source=after.stash['ledger_rows'][0]
        after.stash['ledger_rows'][0]=kind,name,ledger,'other-native.toml'
    else:symbol.evidence.append({'kind':'test','path':'controlled.py','key':'test_identity','supports':'identity'})
    with pytest.raises((ValueError,KbError)):
        expected=resolution.publication_expected(before,after,resolutions,
            write.publication_view(before),write.publication_view(after))
        if not test_contract.exact(expected,write.publication_view(after)):raise ValueError('another native value changes')


@pytest.mark.parametrize('fault',('partial','duplicate','wrong-id','wrong-sha','extra-evidence'))
def test_argument_preflight_requires_all_exact_unique_operations(transition,fault):
    operations=deepcopy(transition[4])
    if fault=='partial':operations.pop()
    elif fault=='duplicate':operations[-1]=deepcopy(operations[0])
    elif fault=='wrong-id':operations[0]['id']='other'
    elif fault=='wrong-sha':operations[0]['claim_sha256']='0'*64
    else:operations[0]['evidence']=[{'kind':'arithmetic','value':'1=1'}]
    with pytest.raises(KbError):write.require_publication_operations(operations)


@pytest.mark.parametrize('failure',(None,'unqualified original'))
def test_argument_dependency_has_no_scale_or_reverse_donation(transition,monkeypatch,failure):
    relation=transition[2].links[0]
    collector=object.__new__(levels._Collector);collector.model=transition[2]
    collector.pointed=set();collector.symbols={}
    identity=levels.Claim('controlled','identity','identity','code')
    scale=levels.Claim('controlled','scale','scale','code')
    donor=levels.Claim('controlled','callee contract','contract','code')
    collector.meanings={(id(relation.owner),'identity'):identity,(id(relation.owner),'scale'):scale,
        (id(relation.to),'contract'):donor}
    monkeypatch.setattr(proof,'link_failure',lambda model,link:failure)
    collector._link(relation)
    assert len(identity.deps)==1 and scale.deps==[]
    assert identity.deps[0].claim is (donor if failure is None else None)
    if failure is not None:assert not identity.deps[0].held and identity.deps[0].lacks==failure


@pytest.mark.parametrize('fault',('owner','target','property','role','evidence','offset','source','layout','via'))
def test_complete_canonical_equality_refuses_any_changed_argument_claim(transition,fault):
    row=transition[0]['reference'][0];relation=deepcopy(transition[2].links[0])
    if fault=='owner':relation.owner.name='other'
    elif fault=='target':relation.to.name='other'
    elif fault=='property':relation.props['supports']='scale'
    elif fault=='role':relation.roles.add('other')
    elif fault=='evidence':relation.evidence=[]
    elif fault=='offset':relation.offset=0
    elif fault=='source':relation.sources.add('other-native.toml')
    elif fault=='layout':relation.stated.add('1nd')
    else:relation.props['via']=[]
    assert not contract.dependency(row,relation)
