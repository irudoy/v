"""Exact representation boundaries and guarded four-claim publication."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from kb import diagnostic_rom_contract as contract, diagnostic_rom_evidence as proof
from kb import diagnostic_rom_resolution as resolution, levels, repo, test_contract, write
from kb.model import Link,Meaning,Model,Symbol,SymbolKey
from kb.repo import KbError


def link(row,meanings,dependency=False):
    claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
    return Link(meanings[claim['owner']],claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
        deepcopy(claim['props']),[contract.item(row)] if dependency else [],
        set(claim['stated']),set(claim['sources']),set(claim['roles']))


@pytest.fixture
def transition(tmp_path,monkeypatch):
    declared=contract.descriptor(repo.ROOT)
    monkeypatch.setattr(contract,'descriptor',lambda root:deepcopy(declared))
    model=Model({}, {}, {}, {}, [])
    model.root=tmp_path
    model.spaces={}
    model.functions={}
    model.names=[]
    model.config={'reconciliation':{'enabled':True,'review':[]}}
    meanings={}
    def add(owner,kind,address,width=None):
        if owner not in meanings:
            meaning=Meaning(kind,name=owner.rsplit('/',1)[0],sources={'controlled-native.toml'})
            meanings[owner]=meaning
            model.meanings.append(meaning)
            key=SymbolKey('7mfk',kind,address)
            symbol=Symbol(key,meaning=meaning,sources={'controlled-native.toml'})
            if width is not None:symbol.props['width']=width
            model.symbols[key]=symbol
            meaning.symbols['7mfk']=symbol
        return meanings[owner]
    add(declared['publisher'],'fn',declared['publisher_address'])
    for row in declared['reference']:
        add(row['owner'],'tbl',row['address'])
        add(row['RAM_owner'],'ram',row['RAM_address'],row['RAM_width'])
        model.links.append(link(row,meanings))
        path=tmp_path/json.loads(row['original_claim_json'])['sources'][0]
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('controlled original native source')
        model.stash.setdefault('ledger_rows',[]).append(('tbl',row['owner'].rsplit('/',1)[0],
            json.loads(row['original_ledger_json']),json.loads(row['original_claim_json'])['sources'][0]))
    note=declared['alias_note']
    meanings[note['owner']].props['note']=json.loads(note['original_json'])
    for held in model.links:held.owner.links.append(held)
    before=model
    after=deepcopy(before)
    owners={meaning.key:meaning for meaning in after.meanings}
    after.links=[link(row,owners,True) for row in declared['reference']]
    for meaning in after.meanings:meaning.links=[]
    for held in after.links:held.owner.links.append(held)
    for row in declared['geometry']:
        after.symbols[SymbolKey('7mfk','tbl',row['address'])].props.update(json.loads(row['properties_json']))
    owners[note['owner']].props['note']=json.loads(note['proposed_json'])
    after.stash['ledger_rows']=[('tbl',row['owner'].rsplit('/',1)[0],json.loads(row['proposed_ledger_json']),
        json.loads(row['original_claim_json'])['sources'][0]) for row in declared['reference']]
    resolutions={row['id']:row['original_claim_sha256'] for row in declared['reference']}
    operations=[dict(cmd='reconcile-diagnostic-output',id=key,claim_sha256=value) for key,value in resolutions.items()]
    monkeypatch.setattr(proof,'require_current',lambda supplied:dict(controlled_admission=True))
    return declared,before,after,resolutions,operations


def test_four_exact_representations_do_not_grant_a_standalone_execution_receipt(transition):
    declared,before,after,_,_=transition
    for row,old,new in zip(declared['reference'],before.links,after.links):
        assert contract.sid_representation_only(old,before.root)
        assert contract.sid_representation_only(new,after.root)
        assert contract.original(row,old) and contract.dependency(row,new)
        assert not contract.registered({'kind':'indirect','mode':'base'})
        assert contract.registered(contract.item(row))
        assert proof.failure(contract.item(row)) is not None


@pytest.mark.parametrize('field',('owner','target','type','layout','source','role','evidence','offset','property','via'))
@pytest.mark.parametrize('dependency',(False,True))
def test_sid_representation_rule_never_ignores_a_changed_complete_claim(transition,field,dependency):
    _,before,after,_,_=transition
    held=(after if dependency else before).links[0]
    changed=deepcopy(held)
    if field=='owner':changed.owner.name='unrelated-owner'
    elif field=='target':changed.to.name='unrelated-target'
    elif field=='type':changed.type='writer'
    elif field=='layout':changed.stated.add('1nd')
    elif field=='source':changed.sources.add('different-native.toml')
    elif field=='role':changed.roles.add('another-role')
    elif field=='evidence':changed.evidence.append({'kind':'arithmetic','value':'1=1'})
    elif field=='offset':changed.offset=0
    elif field=='property':changed.props['relies']='contract'
    else:changed.props['via']=['7mfk:00000000']
    assert not contract.sid_representation_only(changed,before.root)


def test_registered_publication_accepts_only_the_complete_narrow_transition(transition):
    declared,before,after,resolutions,operations=transition
    expected=resolution.publication_expected(before,after,resolutions,
        write.publication_view(before),write.publication_view(after))
    assert test_contract.exact(expected,write.publication_view(after))
    change=SimpleNamespace(width_resolutions={},diagnostic_resolutions=resolutions)
    texts={repo.OWNER_CONFIG:'controlled review metadata'}
    path=before.root/repo.OWNER_CONFIG
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('controlled original reviews')
    write.require_metadata_only(before,after,operations,change,texts)
    assert len(declared['reference'])==len(resolutions)


@pytest.mark.parametrize('fault',('partial','wrong-review','extra-property','changed-existing-geometry',
    'meaning-geometry','extra-override','alias-qualifier','RAM-reader-change','extra-TEST','TEST-context',
    'ledger-selector','ledger-evidence-order','ledger-source'))
def test_joint_publication_cannot_absorb_other_semantic_or_origin_changes(transition,fault):
    declared,before,after,resolutions,_=transition
    symbol=after.symbols[SymbolKey('7mfk','tbl',declared['reference'][0]['address'])]
    if fault=='partial':resolutions.pop(next(iter(resolutions)))
    elif fault=='wrong-review':resolutions[next(iter(resolutions))]='0'*64
    elif fault=='extra-property':symbol.props['signed']=True
    elif fault=='changed-existing-geometry':before.symbols[symbol.key].props['storage']='uint8'
    elif fault=='meaning-geometry':symbol.meaning.props['rows']=1
    elif fault=='extra-override':before.symbols[symbol.key].meaning.props['cols']=1
    elif fault=='alias-qualifier':
        note=next(meaning for meaning in after.meanings if meaning.key==declared['alias_note']['owner'])
        note.props['note']=['The degree unit is established.']
    elif fault=='RAM-reader-change':
        after.symbols[SymbolKey('7mfk','ram',declared['reference'][0]['RAM_address'])].props['width']=8
    elif fault=='ledger-selector':
        after.stash['ledger_rows'][0][2][0]['dependency'].append(dict(role='consumer',
            to='married-moth/fn',type='reader',end='owner',relies='level',supports='identity'))
    elif fault=='ledger-evidence-order':after.stash['ledger_rows'][0][2][0]['identity'].reverse()
    elif fault=='ledger-source':
        kind,name,ledger,source=after.stash['ledger_rows'][0]
        after.stash['ledger_rows'][0]=(kind,name,ledger,'unrelated-native.toml')
    else:
        evidence={'kind':'test','path':'controlled.py','key':'test_identity','supports':'identity'}
        symbol.evidence.append(evidence)
        if fault=='TEST-context':before.symbols[symbol.key].evidence.append(deepcopy(evidence))
    with pytest.raises((ValueError,KbError)):
        expected=resolution.publication_expected(before,after,resolutions,
            write.publication_view(before),write.publication_view(after))
        if not test_contract.exact(expected,write.publication_view(after)):
            raise ValueError('the guarded native view differs')


@pytest.mark.parametrize('fault',('extra-key','wrong-id','wrong-sha','boolean-sha','extra-evidence'))
def test_publication_preflight_refuses_changed_diagnostic_operation_parameters(transition,fault):
    operation=dict(transition[4][0])
    if fault=='extra-key':operation['layout']='1nd'
    elif fault=='wrong-id':operation['id']='unrelated'
    elif fault=='wrong-sha':operation['claim_sha256']='0'*64
    elif fault=='boolean-sha':operation['claim_sha256']=True
    else:operation['evidence']=[{'kind':'arithmetic','value':'1=1'}]
    with pytest.raises(KbError):write.require_publication_operations([operation])


@pytest.mark.parametrize('fault',('partial','duplicate','wrong-id'))
def test_all_four_exact_operations_are_required_before_original_execution(transition,fault):
    operations=deepcopy(transition[4])
    if fault=='partial':operations.pop()
    elif fault=='duplicate':operations[-1]=deepcopy(operations[0])
    else:operations[-1]['id']='unrelated'
    with pytest.raises(KbError):write.require_publication_operations(operations)


@pytest.mark.parametrize('row_index',(0,1))
@pytest.mark.parametrize('failure',(None,'unqualified original'))
def test_relation_structure_donates_no_level_without_joint_admission_or_to_scale(transition,monkeypatch,row_index,failure):
    after=transition[2]
    relation=after.links[row_index]
    collector=object.__new__(levels._Collector)
    collector.model=after
    collector.pointed=set()
    collector.symbols={}
    identity=levels.Claim('controlled','identity','identity','code')
    scale=levels.Claim('controlled','scale','scale','code')
    donor_name=levels.RELIED.get(relation.props['relies'],'identity')
    donor=levels.Claim('controlled','RAM claim',donor_name,'code')
    collector.meanings={(id(relation.owner),'identity'):identity,
        (id(relation.owner),'scale'):scale,(id(relation.to),donor_name):donor}
    monkeypatch.setattr(proof,'link_failure',lambda model,link:failure)
    monkeypatch.setattr(levels,'held',lambda model,symbol,pointed:True)
    collector._link(relation)
    assert len(identity.deps)==1 and scale.deps==[]
    expected=donor if failure is None and relation.props['relies']!='structure' else None
    assert identity.deps[0].claim is expected
    if failure is None and relation.props['relies']=='structure':assert identity.deps[0].held
    if failure is not None:
        assert not identity.deps[0].held and identity.deps[0].lacks==failure


def test_document_publishes_the_executed_descriptor_owners_and_source_addresses():
    declared=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.diagnostic-ROM-dependencies.md').read_text()
    for row in declared['reference']:
        assert f'`{row["address"]:08X}`' in text
        assert f'`{row["RAM_address"]:08X}`' in text
    assert 'additional receipt' in text and 'Every original TEST' in text
