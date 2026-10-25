"""Exact native/COPY refusal contracts; controlled packets grant no execution."""
from copy import deepcopy
import hashlib

import pytest

from kb import coherent_copy_evidence as proof, coherent_copy_matrix as matrix
from kb import compile, copy_evidence as common, injection_copy_evidence, lock, repo, sid22_evidence
from kb.model import SymbolKey


@pytest.fixture(scope='module')
def native():
    with lock.held(repo.ROOT):
        return compile.build(repo.ROOT)


def test_all_exact_callers_bind_original_native_claims_without_declared_width_changes(native):
    from kb import checks
    assert len(proof.MEMBERS)==84 and len(proof.MEMBER_KEYS)==81
    for row in proof.MEMBERS:
        symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
        assert proof.member(native,symbol,row=row)==row
        assert not any(proof.registered(item) for item in proof.link(native,symbol,row).evidence)
        item=proof.member_item(row)
        assert common.registered(item,symbol)
        assert not list(checks._evidence_issues([item],proof.DESCRIPTOR,row[2],True))
    assert sum(row[7]=='word-lane' for row in proof.MEMBERS)==2


@pytest.mark.parametrize('address',(0xffff1073,0xffff1076,0xffff1078))
def test_shared_reader_requires_exact_caller_and_owning_attachment(native,address):
    symbol=native.symbols[SymbolKey('7mfk','ram',address)]
    rows=[row for row in proof.MEMBERS if row[0]==address]
    assert len(rows)==2 and {proof.parent(row)[0].address for row in rows}=={0x209d8,0x20dfe}
    with pytest.raises(ValueError,match='one exact owning caller'):
        proof.member(native,symbol)
    for row in rows:
        item=proof.member_item(row)
        assert proof.member(native,symbol,evidence=item)==row
        assert proof.link(native,symbol,row).to.key==proof.parent(row)[1]
        changed=deepcopy(item);changed['to']=proof.parent(next(other for other in rows if other!=row))[0]
        assert proof.failure(changed,symbol,native,'identity') is not None


@pytest.mark.parametrize('failure',(None,'unqualified original'))
def test_coherent_levels_bind_owning_identity_without_reverse_or_scale_donation(native,monkeypatch,failure):
    from kb import levels
    row=next(row for row in proof.MEMBERS if row[6]==0x20bd0)
    relation=proof.link(native,native.symbols[SymbolKey('7mfk','ram',row[0])],row)
    monkeypatch.setattr(relation,'evidence',[*relation.evidence,proof.member_item(row)])
    owner=levels.Claim('controlled','owner','identity','code')
    scale=levels.Claim('controlled','scale','scale','code')
    reverse=levels.Claim('controlled','function','identity','code')
    collector=object.__new__(levels._Collector)
    collector.model,collector.pointed,collector.symbols=native,set(),{}
    collector.meanings={(id(relation.owner),'identity'):owner,(id(relation.owner),'scale'):scale,
                        (id(relation.to),'identity'):reverse}
    monkeypatch.setattr(proof,'link_failure',lambda model,relation:failure)
    collector._link(relation)
    assert scale.items==scale.deps==reverse.items==reverse.deps==[]
    if failure is None:
        assert owner.deps==[] and owner.items==[(relation.owner.symbols['7mfk'],relation.evidence[-1])]
    else:
        assert owner.items==[] and len(owner.deps)==1 and owner.deps[0].lacks==failure


def test_exact_appends_preserve_can_snapshot_coherent_and_sid22_scopes(native):
    scopes=lambda:(common.scope_digest(native),injection_copy_evidence.scope_digest(native),
        proof.scope_digest(native),sid22_evidence.scope_digest(native))
    before=scopes();saved=[]
    try:
        for row in proof.MEMBERS:
            symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
            relation=proof.link(native,symbol,row);saved.append((relation,list(relation.evidence)))
            relation.evidence.append(proof.member_item(row))
        assert scopes()==before
    finally:
        for relation,evidence in saved:relation.evidence[:]=evidence


REPRESENTATIVES=tuple(next(i for i,row in enumerate(proof.MEMBERS) if row[6]==window.call)
                      for window in matrix.WINDOWS)+(11,12)


@pytest.mark.parametrize('index',REPRESENTATIVES)
@pytest.mark.parametrize('fault',['width','signed','slot','offset','note','source','duplicate','wrong-lane'])
def test_each_window_and_word_lane_refuses_wrong_native_context(native,monkeypatch,index,fault):
    row=proof.MEMBERS[index];symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
    relation=proof.link(native,symbol,row)
    if fault in ('width','signed'):
        monkeypatch.setattr(symbol,'props',{**symbol.props,fault:32 if fault=='width' else not bool(row[4])})
    elif fault in ('slot','offset'):
        monkeypatch.setattr(relation,fault,1)
    elif fault=='note':monkeypatch.setattr(relation,'props',{**relation.props,'note':'another fact'})
    elif fault=='source':monkeypatch.setattr(relation,'sources',{'kb/ram/other.toml'})
    else:
        item=proof.member_item(row)
        entries=[item,item] if fault=='duplicate' else [{**item,'value':{**item['value'],'offset_bytes':row[9]+1}}]
        monkeypatch.setattr(relation,'evidence',relation.evidence+entries)
    with pytest.raises(ValueError):
        proof.member(native,symbol,row=row);proof.link(native,symbol,row)
    assert proof.failure(proof.member_item(row),symbol,native,'identity') is not None


@pytest.mark.parametrize('index',[0,11,12,69])
@pytest.mark.parametrize('context',[None,'scale','unit','confidence'])
def test_only_exact_identity_can_use_the_existing_shared_terminal(native,monkeypatch,index,context):
    row=proof.MEMBERS[index];symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
    relation=proof.link(native,symbol,row);item=proof.member_item(row);calls=[]
    monkeypatch.setattr(relation,'evidence',[*relation.evidence,item])
    def terminal(entry,can_symbol,model,claim,*,record):
        calls.append((entry,can_symbol.key,model,claim,record));return None
    monkeypatch.setattr(common,'failure',terminal)
    assert proof.failure(item,symbol,native,'identity',record={'controlled':True}) is None
    assert calls==[(common.item('reader'),SymbolKey('7mfk','ram',0xffff419b),native,'identity',{'controlled':True})]
    calls.clear()
    assert proof.failure(item,symbol,native,context) is not None and calls==[]


@pytest.fixture
def packet(monkeypatch):
    """Control observation semantics; real raw-state mutations have separate coverage."""
    descriptor=proof.descriptor();image=repo.images()['JK08A'].path.read_bytes()
    names=proof.consumed_names(descriptor)
    inputs={name:hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest() for name in names}
    windows=[];seen=[]
    for window,row in zip(matrix.WINDOWS,descriptor['window']):
        cases=matrix.cases(window)
        aliases=[[p['address'],p['value'],matrix.alias(p['value'])] for p in row['pool'] if p['value']>=0xffff0000]
        boundary=dict(address=window.call+4,bytes='57f6472a000b0009')
        fixture=bytearray(image)
        for address,original,alias in aliases:fixture[address:address+4]=alias.to_bytes(4,'big')
        fixture[window.call+4:window.call+12]=bytes.fromhex(boundary['bytes'])
        windows.append(dict(region=row['key'],cases=cases,
            observations=[dict(controlled_case=case['index'],controlled_call=window.call) for case in cases],
            code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in proof.code_spans(window)],
            pools=[dict(address=p['address'],stock=image[p['address']:p['address']+4].hex(),
                reconstructed=image[p['address']:p['address']+4].hex()) for p in row['pool']],
            image_sha256=hashlib.sha256(image).hexdigest(),fixture_sha256=hashlib.sha256(fixture).hexdigest(),
            elf_sha256='a'*64,aliases=aliases,boundary=boundary,
            instructions=sum((b-a)//2 for a,b in proof.code_spans(window))))
    def observe(window,case,value,pools,previous):
        if value!=dict(controlled_case=case['index'],controlled_call=window.call):
            raise ValueError('controlled observation boundary refuses a wrong case')
        seen.append((window.call,case['index']));return None
    monkeypatch.setattr(matrix,'validate_observation',observe)
    value=dict(schema=1,key=proof.KEY,windows=windows,
        consumed={name:(repo.ROOT/name).read_bytes().hex() for name in names},
        toolchain=dict(simulator_version='16.3',gcc_version='13.3.0',
            binaries={key:'b'*64 for key in ('as','ld','objcopy','gcc','run')}))
    return value,inputs,seen


def test_complete_packet_checks_each_ordered_window_and_case(packet):
    value,inputs,seen=packet
    proof.validate_witness(value,inputs,repo.ROOT)
    assert seen==[(window.call,case['index']) for window in matrix.WINDOWS for case in matrix.cases(window)]
    assert len(seen)==17228


@pytest.mark.parametrize('fault',['missing-window','duplicate-window','reorder','early','wrong-case',
    'wrong-observation','code','pool','instructions','aliases','boundary','image','fixture','elf',
    'consumed','missing-source','schema','schema-bool','key','toolchain','extra-window-field'])
def test_shared_protocol_rejects_each_wrong_execution_binding(packet,fault):
    value,inputs,_=packet;row=value['windows'][2]
    if fault=='missing-window':value['windows'].pop()
    elif fault=='duplicate-window':value['windows'][3]=deepcopy(row)
    elif fault=='reorder':value['windows'].reverse()
    elif fault=='early':row['cases']=row['cases'][:10];row['observations']=row['observations'][:10]
    elif fault=='wrong-case':row['cases'][0]['seed']^=1
    elif fault=='wrong-observation':row['observations'][0]['controlled_call']^=2
    elif fault=='code':row['code'][0]['reconstructed']='0009'
    elif fault=='pool':row['pools'][0]['reconstructed']='00000000'
    elif fault=='instructions':row['instructions']=True
    elif fault=='aliases':row['aliases'][0][2]^=4
    elif fault=='boundary':row['boundary']['address']+=2
    elif fault=='image':row['image_sha256']='c'*64
    elif fault=='fixture':row['fixture_sha256']='c'*64
    elif fault=='elf':row['elf_sha256']='unbound'
    elif fault=='consumed':value['consumed'][next(iter(value['consumed']))]='00'
    elif fault=='missing-source':value['consumed'].pop(next(iter(value['consumed'])))
    elif fault=='schema':value['schema']=2
    elif fault=='schema-bool':value['schema']=True
    elif fault=='key':value['key']='another key'
    elif fault=='toolchain':value['toolchain']['binaries'].pop('run')
    else:row['unexpected']=True
    with pytest.raises((ValueError,TypeError,KeyError)):
        proof.validate_witness(value,inputs,repo.ROOT)


@pytest.mark.parametrize('fault',['none','other-evidence','note','width','wrong-append'])
def test_retirement_requires_the_exact_original_identity_append(native,monkeypatch,fault):
    row=proof.MEMBERS[11]
    before_symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
    old=deepcopy(common.claim_fields(proof.link(native,before_symbol,row),'7mfk'))
    with lock.held(repo.ROOT):
        after=compile.build(repo.ROOT)
    symbol=after.symbols[before_symbol.key];relation=proof.link(after,symbol,row)
    item=proof.member_item(row)
    relation.evidence.append(item)
    monkeypatch.setattr(proof,'failure',lambda *args,**kwargs:None)
    if fault=='other-evidence':relation.evidence.append(dict(kind='spec',path='defs/other.md'))
    elif fault=='note':relation.props['note']='another fact'
    elif fault=='width':symbol.props['width']=16
    elif fault=='wrong-append':relation.evidence[-1]={**item,'value':{**item['value'],'offset_bytes':0}}
    assert proof.retires(native,after,old) is (fault=='none')
    assert common.retires(native,after,old) is (fault=='none')


@pytest.mark.parametrize('fault',['key','path','at','supports','kind','to','width-bool','transfer','mechanism','site'])
def test_reserved_namespace_never_borrows_generic_grounding(native,monkeypatch,fault):
    from kb import match
    row=proof.MEMBERS[0];symbol=native.symbols[SymbolKey('7mfk','ram',row[0])]
    relation=proof.link(native,symbol,row);item=proof.member_item(row);wrong=deepcopy(item)
    if fault=='key':wrong['key']='unregistered key'
    elif fault=='path':wrong['path']='defs/other.toml'
    elif fault=='at':wrong['at']=f'7mfk:{row[6]+2:08x}'
    elif fault=='supports':wrong['supports']='scale'
    elif fault=='kind':wrong['kind']='spec'
    elif fault=='to':wrong['to']=SymbolKey('7mfk','fn',0x20e00)
    elif fault=='width-bool':wrong['value']['width_bits']=True
    elif fault=='transfer':wrong['value']['transfer_width_bits']=64
    elif fault=='mechanism':wrong['value']['mechanism']='word-lane'
    else:wrong['value']['access_site']=f'7mfk:{row[8]+2:08x}'
    assert common.encode(wrong)!=common.encode(item)
    monkeypatch.setattr(relation,'evidence',relation.evidence+[wrong])
    assert common.registered(wrong,symbol)
    assert common.failure(wrong,symbol,native,'identity') is not None
    assert match.rank(wrong,symbol,native,'identity')==-1
    assert common.accepted(native,symbol,native.symbols[proof.FUNCTION],common.claim_fields(relation,'7mfk')) is None


def test_documented_coherent_counts_and_protocol_follow_executed_adapters():
    text=' '.join((repo.ROOT/'tools/kb/README.md').read_text().split())
    assert f'The shared primary GNU receipt uses schema {common.SCHEMA}.' in text
    assert f'The coherent descriptor binds {len(proof.MEMBERS)} exact native claims in {len(matrix.WINDOWS)} caller windows.' in text
    execution_text=' '.join((repo.ROOT/'tools/sh-elf-run/README.md').read_text().split())
    assert f'the schema-{common.SCHEMA} shared copy receipt.' in execution_text
