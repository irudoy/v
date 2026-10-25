"""Complete native documents and TEST origins survive exact caller-copy appends."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from kb import compile, copy_evidence as common, coherent_copy_evidence as proof
from kb import injection_copy_evidence, sid22_evidence, lock, repo, test_contract, test_origins, write
from kb.model import SymbolKey


@pytest.fixture(scope='module')
def native():
    with lock.held(repo.ROOT):
        return compile.build(repo.ROOT)


def representation(model, qualified):
    result=deepcopy(model)
    for row in proof.MEMBERS:
        symbol=result.symbols[SymbolKey('7mfk','ram',row[0])]
        relation=proof.link(result,symbol,row)
        item=proof.member_item(row)
        relation.evidence[:]=[entry for entry in relation.evidence if common.encode(entry)!=common.encode(item)]
        if qualified:
            relation.evidence.append(item)
    return result


def test_common_access_dispatch_reaches_the_registered_209d8_caller(native,monkeypatch):
    model=representation(native,True)
    row=next(row for row in proof.MEMBERS if row[0]==0xFFFF107E and proof.parent(row)[0].address==0x209D8)
    symbol=model.symbols[SymbolKey('7mfk','ram',row[0])]
    function=model.symbols[proof.parent(row)[0]]
    link=proof.link(model,symbol,row)
    expected=object();seen=[]
    def admit(current,member,parent,claim):
        seen.append((current,member,parent,claim))
        return expected
    monkeypatch.setattr(proof,'accepted',admit)
    claim=common.claim_fields(link,'7mfk')
    assert common.accepted(model,symbol,function,claim) is expected
    assert seen==[(model,symbol,function,claim)]


def operations():
    return [dict(cmd='link',meaning=row[2],type=row[1],to=proof.parent(row)[1],
                 evidence=[write.Change._stored(proof.member_item(row))]) for row in proof.MEMBERS]


def test_complete_registered_appends_preserve_all_native_values_and_TEST_origins(native,monkeypatch):
    before=representation(native,False)
    after=representation(before,True)
    assert test_contract.exact(write.publication_view(before),write.publication_view(after))
    assert test_contract.exact({key:item.packet() for key,item in test_origins.index(before).items()},
                               {key:item.packet() for key,item in test_origins.index(after).items()})
    for module in (common,injection_copy_evidence,proof,sid22_evidence):
        assert module.scope_digest(before)==module.scope_digest(after)
    # This controlled writer boundary supplies no original execution or physical admission.
    monkeypatch.setattr(common,'failure',lambda *args,**kwargs:None)
    write.require_metadata_only(before,after,operations(),SimpleNamespace(width_resolutions={}),{})


def test_existing_normal_writer_keeps_complete_fourteen_owner_postimages(native):
    before=representation(native,False)
    owners={meaning.key:meaning for meaning in before.meanings}
    selected={row[2] for row in proof.MEMBERS if proof.parent(row)[0].address==0x209d8}
    rows=[row for row in proof.MEMBERS if row[2] in selected]
    assert len(selected)==14 and len(rows)==17
    change=write.Change(before,lambda text:(owners[text],None))
    expected={}
    for owner in selected:
        path,document=change.document(owners[owner])
        original=deepcopy(document)
        for row in rows:
            if row[2]!=owner:
                continue
            item=write.Change._stored(proof.member_item(row))
            matches=[link for link in original.get('link',())
                     if link['type']==row[1] and link['to']==proof.parent(row)[1]]
            assert len(matches)==1
            if 'evidence' in matches[0]:
                matches[0]['evidence']=[entry for entry in matches[0]['evidence']
                                       if not test_contract.exact(entry,item)]
                if not matches[0]['evidence']:
                    matches[0].pop('evidence')
        change.documents[path]=deepcopy(original)
        expected[path]=deepcopy(original)
    for row in rows:
        op=dict(cmd='link',meaning=row[2],type=row[1],to=proof.parent(row)[1],
                evidence=[write.Change._stored(proof.member_item(row))])
        path,_=change.document(owners[row[2]])
        match,=[link for link in expected[path]['link'] if link['type']==row[1] and link['to']==op['to']]
        match.setdefault('evidence',[]).append(deepcopy(op['evidence'][0]))
        change.link(op)
    assert test_contract.exact(change.documents,expected)


def test_metadata_writer_refuses_reordered_link_TEST_even_when_unordered_facts_agree(native,monkeypatch):
    before=representation(native,False)
    after=representation(before,True)
    relation=next(link for link in after.links if link.owner.key=='amigurumi-dormouse/fn'
                  and link.type=='depends' and link.to.key=='bulky-hound/fn'
                  and len([item for item in link.evidence if item.get('kind')=='test'])>=2)
    first,second=next((i,j) for i in range(len(relation.evidence)) for j in range(i+1,len(relation.evidence))
                      if relation.evidence[i].get('kind')==relation.evidence[j].get('kind')=='test'
                      and not test_contract.exact(relation.evidence[i],relation.evidence[j]))
    relation.evidence[first],relation.evidence[second]=relation.evidence[second],relation.evidence[first]
    assert test_contract.exact(write.publication_view(before),write.publication_view(after))
    monkeypatch.setattr(common,'failure',lambda *args,**kwargs:None)
    with pytest.raises(repo.KbError,match='TEST origin or evidence position'):
        write.require_metadata_only(before,after,operations(),SimpleNamespace(width_resolutions={}),{})


@pytest.mark.parametrize('fault',('ledger','TEST-position','property','width','other-evidence','duplicate','caller','lane'))
def test_complete_native_comparison_refuses_another_fact_or_attachment(native,monkeypatch,fault):
    before=representation(native,False)
    after=representation(before,True)
    row=next(row for row in proof.MEMBERS if row[6]==0x20bd0)
    symbol=after.symbols[SymbolKey('7mfk','ram',row[0])]
    relation=proof.link(after,symbol,row)
    if fault=='ledger':
        ledger=next(value for kind,name,value,source in after.stash['ledger_rows'] if f'{name}/{kind}'==row[2])
        ledger[0]['order']+=1
    elif fault=='TEST-position':
        assert len(symbol.evidence)>2 and symbol.evidence[2]['kind']=='test'
        symbol.evidence[1],symbol.evidence[2]=symbol.evidence[2],symbol.evidence[1]
    elif fault=='property':
        symbol.meaning.props['unit']='unrelated unit'
    elif fault=='width':
        symbol.props['width']=32
    elif fault=='other-evidence':
        relation.evidence.append(dict(kind='spec',path='defs/unrelated.md'))
    elif fault=='duplicate':
        relation.evidence.append(deepcopy(relation.evidence[-1]))
    elif fault=='caller':
        relation.evidence[-1]['to']=proof.FUNCTION
    else:
        relation.evidence[-1]['value']['offset_bytes']+=1
    monkeypatch.setattr(common,'failure',lambda *args,**kwargs:None)
    with pytest.raises((ValueError,repo.KbError)):
        write.require_metadata_only(before,after,operations(),SimpleNamespace(width_resolutions={}),{})
