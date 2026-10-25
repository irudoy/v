"""Exact cached-snapshot representation and constrained publication boundaries."""

from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import snapshot_rom_contract as contract,snapshot_rom_evidence as proof
from kb import snapshot_rom_resolution as resolution,levels,repo,test_contract,write
from kb import publication_inhibit_contract
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
    declared=contract.descriptor(repo.ROOT);row=declared['reference'][0]
    monkeypatch.setattr(contract,'descriptor',lambda root:deepcopy(declared))
    before=Model({}, {}, {}, {}, []);before.root=tmp_path
    before.spaces={};before.functions={};before.names=[]
    before.config={'reconciliation':{'enabled':True,'review':[]}}
    meanings={}
    for owner,kind,address in ((row['owner'],'tbl',row['address']),('coherent_snapshot/fn','fn',0x20DFE),
            (row['RAM_owner'],'ram',row['RAM_address']),(row['live_owner'],'ram',row['live_address'])):
        meaning=Meaning(kind,name=owner.rsplit('/',1)[0],sources={'controlled-native.toml'})
        meanings[owner]=meaning;before.meanings.append(meaning)
        key=SymbolKey('7mfk',kind,address)
        symbol=Symbol(key,meaning=meaning,sources={'controlled-native.toml'})
        before.symbols[key]=symbol;meaning.symbols['7mfk']=symbol
    old=representation(row,meanings);before.links=[old];old.owner.links.append(old)
    source=json.loads(row['original_claim_json'])['sources'][0]
    before.stash['ledger_rows']=[('tbl',row['owner'].rsplit('/',1)[0],json.loads(row['original_ledger_json']),source)]
    path=tmp_path/source;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('controlled original source')
    after=deepcopy(before);owners={meaning.key:meaning for meaning in after.meanings}
    new=representation(row,owners,True);after.links=[new]
    for meaning in after.meanings:meaning.links=[]
    new.owner.links.append(new)
    after.symbols[SymbolKey('7mfk','tbl',row['address'])].props.update(declared['geometry'])
    after.stash['ledger_rows']=[('tbl',row['owner'].rsplit('/',1)[0],json.loads(row['proposed_ledger_json']),source)]
    resolutions={row['id']:contract.ORIGINAL}
    operations=[dict(cmd='reconcile-snapshot-output',id=row['id'],claim_sha256=contract.ORIGINAL)]
    monkeypatch.setattr(proof,'require_current',lambda model:dict(controlled_admission=True))
    # Controlled metadata objects carry no physical execution proof.
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        monkeypatch.setattr(module,'scope_digest',lambda model:'controlled-scope')
    return declared,before,after,resolutions,operations


def test_exact_snapshot_transition_changes_only_its_reader_selector_and_absent_geometry(transition):
    declared,before,after,resolutions,operations=transition
    row=declared['reference'][0]
    assert contract.representation_only(before.links[0],before.root)
    assert contract.representation_only(after.links[0],after.root)
    assert proof.failure(contract.item(row)) is not None
    expected=resolution.publication_expected(before,after,resolutions,
        write.publication_view(before),write.publication_view(after))
    assert test_contract.exact(expected,write.publication_view(after))
    change=SimpleNamespace(width_resolutions={},diagnostic_resolutions={},argument_resolutions={},snapshot_resolutions=resolutions)
    path=before.root/repo.OWNER_CONFIG;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('controlled reviews')
    write.require_metadata_only(before,after,operations,change,{repo.OWNER_CONFIG:'controlled reviews'})


@pytest.mark.parametrize('dependency',(False,True))
@pytest.mark.parametrize('field',('owner','target','type','layout','source','role','evidence','offset','property','via'))
def test_snapshot_normalization_never_ignores_a_changed_complete_claim(transition,dependency,field):
    _,before,after,_,_=transition
    link=deepcopy((after if dependency else before).links[0])
    if field=='owner':link.owner.name='other'
    elif field=='target':link.to.name='other'
    elif field=='type':link.type='writer'
    elif field=='layout':link.stated.add('1nd')
    elif field=='source':link.sources.add('other-native.toml')
    elif field=='role':link.roles.add('other')
    elif field=='evidence':link.evidence.append({'kind':'arithmetic','value':'1=1'})
    elif field=='offset':link.offset=0
    elif field=='property':link.props['relies']='level'
    else:link.props['via']=[]
    assert not contract.representation_only(link,before.root)


@pytest.mark.parametrize('fault',('missing','wrong-sha','extra-property','wrong-geometry','meaning-geometry',
    'extra-evidence','ledger-selector','ledger-order','ledger-source','extra-TEST','RAM-width'))
def test_snapshot_transition_refuses_unrelated_values_and_origins(transition,fault):
    declared,before,after,resolutions,_=transition;row=declared['reference'][0]
    symbol=after.symbols[SymbolKey('7mfk','tbl',row['address'])]
    if fault=='missing':resolutions.clear()
    elif fault=='wrong-sha':resolutions[row['id']]='0'*64
    elif fault=='extra-property':symbol.meaning.props['units']='RPM'
    elif fault=='wrong-geometry':symbol.props['cols']=8
    elif fault=='meaning-geometry':symbol.meaning.props['rows']=1
    elif fault=='extra-evidence':after.links[0].evidence.append({'kind':'arithmetic','value':'1=1'})
    elif fault=='ledger-selector':after.stash['ledger_rows'][0][2][0]['dependency'].append(dict(role='consumer',to='other/fn'))
    elif fault=='ledger-order':after.stash['ledger_rows'][0][2][0]['identity'].reverse()
    elif fault=='ledger-source':
        kind,name,ledger,source=after.stash['ledger_rows'][0];after.stash['ledger_rows'][0]=kind,name,ledger,'other-native.toml'
    elif fault=='RAM-width':after.symbols[SymbolKey('7mfk','ram',row['RAM_address'])].props['width']=16
    else:symbol.evidence.append({'kind':'test','path':'controlled.py','key':'test_identity','supports':'identity'})
    with pytest.raises((ValueError,KbError)):
        expected=resolution.publication_expected(before,after,resolutions,
            write.publication_view(before),write.publication_view(after))
        if not test_contract.exact(expected,write.publication_view(after)):raise ValueError('another native value changes')


@pytest.mark.parametrize('fault',('duplicate','wrong-id','wrong-sha','extra-evidence'))
def test_snapshot_preflight_refuses_changed_or_repeated_operations(transition,fault):
    operations=deepcopy(transition[4])
    if fault=='duplicate':operations.append(deepcopy(operations[0]))
    elif fault=='wrong-id':operations[0]['id']='other'
    elif fault=='wrong-sha':operations[0]['claim_sha256']='0'*64
    else:operations[0]['evidence']=[{'kind':'arithmetic','value':'1=1'}]
    with pytest.raises(KbError):write.require_publication_operations(operations)


@pytest.mark.parametrize('failure',(None,'unqualified original'))
def test_snapshot_dependency_has_no_scale_or_reverse_donation(transition,monkeypatch,failure):
    relation=transition[2].links[0]
    collector=object.__new__(levels._Collector);collector.model=transition[2]
    collector.pointed=set();collector.symbols={}
    identity=levels.Claim('controlled','identity','identity','code');scale=levels.Claim('controlled','scale','scale','code')
    collector.meanings={(id(relation.owner),'identity'):identity,(id(relation.owner),'scale'):scale}
    monkeypatch.setattr(proof,'link_failure',lambda model,link:failure)
    monkeypatch.setattr(levels,'held',lambda model,symbol,pointed:True)
    collector._link(relation)
    assert len(identity.deps)==1 and scale.deps==[]
    if failure is None:assert identity.deps[0].held and identity.deps[0].claim is None
    if failure is not None:assert not identity.deps[0].held and identity.deps[0].lacks==failure


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_snapshot_descriptor_refuses_implicit_scale_scheduling_or_hardware_inference(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    assert changed!=original
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_snapshot_documented_owners_and_count_bind_to_executed_producer_geometry():
    declared=contract.descriptor(repo.ROOT);physical=publication_inhibit_contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.snapshot-ROM-dependency.md').read_text()
    assert declared['geometry']['storage']=='uint8'
    assert declared['geometry']['cols']==physical['table']['elements']
    assert f"`{declared['geometry']['cols']}` values" in text
    row=declared['reference'][0]
    for key in ('address','RAM_address','live_address'):assert f'`{row[key]:08X}`' in text
