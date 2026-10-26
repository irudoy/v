"""Exact indexed writer append, complete native owner/function, TEST and owning refusals."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import diagnostic_record_bit4_access_contract as contract
from kb import diagnostic_record_bit4_access_evidence as proof


def row():return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))


def test_exact_original_positive_append_preserves_full_array_owner_function_types_and_both_ledger_ends():
    selected=row();before,after=(json.loads(selected[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(after);target,=[r for r in stripped['link'] if (r['type'],r['to'])==('writer','cherry-wildcat/fn')]
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence']:target.pop('evidence')
    assert stripped==before
    assert before['unit']==after['unit']=='diagnostic record byte'
    assert selected['declared_width']==8 and selected['declared_signed'] is False
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    original=json.loads(selected['original_claim_json'])
    assert selected['original_claim_sha256']=='3655c66e3ef972ce95f95db39da784ed70f454d346be7a51411fffaeb1fa00b5'
    assert original['props']['reverse_supports']=='identity' and original['type']=='writer'
    function=contract.DECLARED['retained_functions'][0];value=json.loads(function['native_json'])
    selectors=[item for marker in value['ledger'] for item in marker.get('dependency',())]
    assert any(item['to']=='hallowed-malkoha/ram' and item['type']=='writer' and item['end']=='to' for item in selectors)
    assert any(item['to']=='red-cockle/ram' and item['type']=='writer' and item['end']=='to' for item in selectors)
    assert selected['owner']=='hallowed-malkoha/ram' and function['owner']=='cherry-wildcat/fn'
    assert contract.item(selected)['value']['actual_indexed_write']==dict(base=0xFFFF5718,stride=3,
        member_offset=2,site=0x8C97A,read_site=0x8C974,width_bytes=1,register=0,mask=16)


@pytest.mark.parametrize('fault',('duplicate','reader-direction','other-target','scale-support','other-index','forged-original'))
def test_normal_owning_writer_requires_its_one_exact_registered_append(fault):
    selected=row();op=contract.operation(selected)
    assert contract.operations([deepcopy(op)],repo.ROOT) is True
    if fault=='duplicate':ops=[op,deepcopy(op)]
    else:
        if fault=='reader-direction':op['type']='reader'
        elif fault=='other-target':op['to']='unrelated/fn'
        elif fault=='scale-support':op['evidence'][0]['supports']='scale'
        elif fault=='other-index':op['evidence'][0]['value']['explicit_full_R4_indices'].append(0x157)
        else:op['evidence'][0]['value']['original_claim_sha256']='0'*64
        ops=[op]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','other-mask'))
def test_only_one_exact_published_append_is_neutral_to_existing_scopes(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='reader'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['actual_indexed_write']['mask']=8
    assert contract.publication(current,item) is False


@pytest.mark.parametrize('fault',('summary','other-writer','width','signed','unit','symbol-evidence','ledger','function','function-ledger'))
def test_complete_native_preimages_refuse_any_unrelated_array_or_function_change(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault.startswith('function'):
        value=json.loads(document['retained_functions'][0]['native_json'])
        if fault=='function':value['summary']='partial function'
        else:value['ledger']=[]
        document['retained_functions'][0]['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='summary':value['summary']='partial candidate'
        elif fault=='other-writer':value['link']=[r for r in value['link'] if r['to']!='classy-seahorse/fn']
        elif fault=='width':value['symbol'][0]['width']=16
        elif fault=='signed':value['symbol'][0]['signed']=True
        elif fault=='unit':value['unit']='status'
        elif fault=='symbol-evidence':value['symbol'][0]['evidence']=[]
        else:value['ledger']=[]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


@pytest.mark.parametrize('flag',proof.REQUIRED_FLAGS)
@pytest.mark.parametrize('fault',('missing','integer','false'))
def test_owning_consumer_requires_every_complete_independent_result_flag(flag,fault):
    selected=row();result={key:True for key in proof.REQUIRED_FLAGS}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c968/fn',
        function_meaning='cherry-wildcat/fn',original_claim_sha256=selected['original_claim_sha256'])]
    assert proof.require_result(deepcopy(result),selected) is True
    if fault=='missing':result.pop(flag)
    else:result[flag]=1 if fault=='integer' else False
    with pytest.raises(ValueError):proof.require_result(result,selected)


@pytest.mark.parametrize('field',('symbol','meaning','function','function_meaning','original_claim_sha256'))
def test_owning_consumer_refuses_other_native_owner_function_or_original(field):
    selected=row();result={key:True for key in proof.REQUIRED_FLAGS}
    result['native_bindings']=[dict(symbol='7mfk-ffff5718/ram',meaning=selected['owner'],function='7mfk-0008c968/fn',
        function_meaning='cherry-wildcat/fn',original_claim_sha256=selected['original_claim_sha256'])]
    result['native_bindings'][0][field]='unrelated'
    with pytest.raises(ValueError):proof.require_result(result,selected)


def test_exact_namespace_neither_donates_to_other_writers_nor_grants_array_absence():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('scalar-ram-leaf-withdrawal','register-only-withdrawal','maf-access'):
        assert not contract.registered(dict(mode=mode))
    current=link(json.loads(row()['original_claim_json']));assert contract.looks_like_access(current)
    current.to.key='classy-seahorse/fn';assert not contract.looks_like_access(current)
    assert contract.item(row())['value']['no_array_extent_inference'] is True


@pytest.fixture(scope='module')
def native_model():
    """Prepare the real native model once; individual corruptions retain full images."""
    from kb import compile
    return compile.build(repo.ROOT)


@pytest.mark.parametrize('fault',('owner-summary','owner-note','owner-TEST','owner-selector','other-writer',
    'function-summary','function-ledger','function-TEST','type-width','type-signed'))
def test_owning_native_consumer_refuses_changed_complete_real_owner_function_type_and_TEST(native_model,monkeypatch,fault):
    from kb.model import SymbolKey
    selected=row();model=native_model
    if fault.startswith('type-'):
        symbol=model.symbols[contract.symbol_key(selected)];original=symbol.value
        field=fault.removeprefix('type-')
        monkeypatch.setattr(type(symbol),'value',lambda self,key,*args,**kwargs:
            (16 if field=='width' else True) if self is symbol and key==field else original(key,*args,**kwargs))
    else:
        original=proof.store.load
        retained=contract.DECLARED['retained_functions'][0]
        target=retained['source'] if fault.startswith('function-') else selected['source']
        def changed(root,path,overlay=None):
            value=deepcopy(original(root,path,overlay))
            if str(path)!=target:return value
            if fault.endswith('summary'):value['summary']='partial native image'
            elif fault=='owner-note':value['note']=[]
            elif fault in ('owner-TEST','function-TEST'):value['symbol'][0]['evidence']=[]
            elif fault.endswith('ledger') or fault=='owner-selector':value['ledger']=[]
            else:value['link']=[r for r in value['link'] if r['to']!='classy-seahorse/fn']
            return value
        monkeypatch.setattr(proof.store,'load',changed)
    with pytest.raises(ValueError):proof.native_rows(model)
