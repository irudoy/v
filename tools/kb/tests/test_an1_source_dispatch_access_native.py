"""Four complete owner states, original TEST positions and independent owning refusals."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import compile,repo,store,test_origins
from kb import an1_source_dispatch_access_native_contract as contract
from kb import an1_source_dispatch_access_evidence as proof
from kb import an1_source_dispatch_access_capture_evidence as capture
from kb import an1_source_dispatch_access_resolution as resolution
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal_contract
from kb import scalar_ram_leaf_withdrawal_evidence as withdrawals

PHASES=('original','qualified','withdrawn','combined')


def selected():return contract.descriptor(repo.ROOT)['reference'][0]


def as_link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))


@pytest.fixture(scope='module')
def native_models():
    """Compile each exact complete phase once through the normal source overlay."""
    row=selected();images=contract.native_images(repo.ROOT)
    declared=withdrawal_contract.descriptor(repo.ROOT);result={}
    for phase in PHASES:
        scalar_phase='proposed' if phase in ('withdrawn','combined') else 'original'
        overlay={Path(item['source']):store.render(item['owner'].rsplit('/',1)[1],
            json.loads(item[scalar_phase+'_native_json'])) for item in declared['reference']}
        overlay.update({Path(item['source']):store.render('fn',
            withdrawal_contract.function_native_document(item,scalar_phase)) for item in declared['function']})
        overlay[Path(row['source'])]=store.render('tbl',images[phase])
        retained=contract.DECLARED['retained_function']
        overlay[Path(retained['source'])]=store.render('fn',json.loads(retained['native_json']))
        result[phase]=compile.build(repo.ROOT,overlay)
    return result


def test_four_real_native_phases_preserve_original_TEST_positions_and_each_family_obligation(native_models):
    row=selected();images=contract.native_images(repo.ROOT)
    origins=None
    for phase,model in native_models.items():
        assert proof.native_rows(model)==[row]
        scalar_phase='proposed' if phase in ('withdrawn','combined') else 'original'
        assert withdrawals.native_rows(model,scalar_phase)==withdrawal_contract.descriptor(repo.ROOT)['reference']
        assert store.load(repo.ROOT,Path(row['source']),model.overlay)==images[phase]
        current={key:item.packet() for key,item in test_origins.index(model).items()}
        if origins is None:origins=current
        else:assert current==origins
        links=[item for item in model.links if contract.original(row,item) or contract.qualified(row,item)]
        assert len(links)==1
        assert contract.qualified(row,links[0]) is (phase in ('qualified','combined'))
        symbol=model.symbols[contract.symbol_key(row)]
        assert symbol.value('width') is None and symbol.value('signed') is None


def test_exact_compatibility_strips_only_one_qualified_append_from_either_complete_owner_phase():
    images=contract.native_images(repo.ROOT);row=selected()
    assert images['original']==json.loads(row['original_native_json'])
    assert images['qualified']==json.loads(row['proposed_native_json'])
    assert images['original']['symbol']==images['combined']['symbol']
    for before,after in (('original','qualified'),('withdrawn','combined')):
        value=deepcopy(images[after]);target,=[item for item in value['link']
            if (item['type'],item['to'])==('reader','romantic-caiman/fn')]
        assert target['evidence'].pop()==contract.item(row)
        old_target,=[item for item in images[before]['link']
            if (item['type'],item['to'])==('reader','romantic-caiman/fn')]
        if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
        assert value==images[before]
        assert contract.strip_exact_owning_append(repo.ROOT,deepcopy(images[after]))==images[before]
        for fault in ('note','duplicate','other-target','changed-original'):
            changed=deepcopy(images[after])
            target,=[item for item in changed['link'] if (item['type'],item['to'])==('reader','romantic-caiman/fn')]
            if fault=='note':changed['note'].append('unrelated native fact')
            elif fault=='duplicate':target['evidence'].append(deepcopy(contract.item(row)))
            elif fault=='other-target':target['to']='unrelated/fn'
            else:target['evidence'][0]['value']['original_claim_sha256']='0'*64
            assert contract.strip_exact_owning_append(repo.ROOT,changed) is changed


@pytest.mark.parametrize('phase',PHASES)
@pytest.mark.parametrize('fault',('owner-summary','owner-note','owner-TEST','owner-ledger','other-reader',
    'function-summary','function-ledger','function-TEST','duplicate-append','changed-append'))
def test_real_native_consumer_refuses_any_changed_full_owner_function_selector_or_TEST(native_models,monkeypatch,phase,fault):
    model=native_models[phase];row=selected();load=store.load
    retained=contract.DECLARED['retained_function']
    path=retained['source'] if fault.startswith('function-') else row['source']
    def changed(root,name,overlay=None):
        value=deepcopy(load(root,name,overlay))
        if str(name)!=path:return value
        if fault.endswith('summary'):value['summary']='partial native image'
        elif fault=='owner-note':value['note']=[]
        elif fault.endswith('TEST'):value['symbol'][0]['evidence']=[]
        elif fault.endswith('ledger'):value['ledger']=[]
        elif fault=='other-reader':
            value['link']=[item for item in value['link'] if item['to']!='dazzling-ladybug/fn']
        else:
            target,=[item for item in value['link'] if (item['type'],item['to'])==('reader','romantic-caiman/fn')]
            target.setdefault('evidence',[]).append(deepcopy(contract.item(row)))
            if fault=='changed-append':target['evidence'][-1]['value']['physical_table_bytes']=1
        return value
    monkeypatch.setattr(store,'load',changed)
    # In an unqualified phase one exact append forms the qualified phase;
    # the duplicate fault must contain two items to remain a real corruption.
    if fault=='duplicate-append' and phase in ('original','withdrawn'):
        first=store.load
        def duplicate(root,name,overlay=None):
            value=first(root,name,overlay)
            if str(name)==path:
                target,=[item for item in value['link'] if (item['type'],item['to'])==('reader','romantic-caiman/fn')]
                target['evidence'].append(deepcopy(contract.item(row)))
            return value
        monkeypatch.setattr(store,'load',duplicate)
    with pytest.raises(ValueError):proof.native_rows(model)
    if not fault.startswith('function-'):
        with pytest.raises(ValueError):withdrawals.native_rows(model,'proposed' if phase in ('withdrawn','combined') else 'original')


@pytest.mark.parametrize('phase',PHASES)
@pytest.mark.parametrize('field',('width','signed'))
def test_real_owner_refuses_invented_semantic_types_in_every_phase(native_models,monkeypatch,phase,field):
    model=native_models[phase];symbol=model.symbols[contract.symbol_key(selected())];method=type(symbol).value
    def changed(self,name):
        return (8 if field=='width' else False) if self is symbol and name==field else method(self,name)
    monkeypatch.setattr(type(symbol),'value',changed)
    with pytest.raises(ValueError):proof.native_rows(model)


@pytest.mark.parametrize('fault',('duplicate','target','owner','direction','scale','physical-scope','original'))
def test_normal_owning_operation_requires_the_single_exact_positive_reader(fault):
    op=contract.operation(selected());assert contract.operations([deepcopy(op)],repo.ROOT) is True
    if fault=='duplicate':ops=[op,deepcopy(op)]
    else:
        if fault=='target':op['to']='piquant-echidna/fn'
        elif fault=='owner':op['meaning']='unrelated/tbl'
        elif fault=='direction':op['type']='writer'
        elif fault=='scale':op['evidence'][0]['supports']='scale'
        elif fault=='physical-scope':op['evidence'][0]['value']['scope']='direct-root-byte-read'
        else:op['evidence'][0]['value']['original_claim_sha256']='0'*64
        ops=[op]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('fault',('duplicate','direction','role','scope','native-fact','original'))
def test_published_namespace_cannot_donate_to_another_relation_or_scope(fault):
    row=selected();item=contract.item(row);link=as_link(json.loads(row['proposed_claim_json']))
    assert contract.publication(link,item) is True
    assert contract.publication(as_link(json.loads(row['original_claim_json'])),item) is False
    if fault=='duplicate':link.evidence.append(deepcopy(item))
    elif fault=='direction':link.type='writer'
    elif fault=='role':link.roles.append('arithmetic-factor')
    elif fault=='scope':link.evidence[0]['value']['scope']='whole-datum-absence'
    elif fault=='native-fact':link.props['note']='changed native fact'
    else:link.evidence[0]['value']['original_claim_sha256']='0'*64
    assert contract.publication(link,item) is False


@pytest.mark.parametrize('phase',('qualified','combined'))
def test_actual_qualified_owner_routes_identity_match_and_failure_to_its_own_primary(native_models,monkeypatch,phase):
    from kb.model import SymbolKey
    model=native_models[phase];row=selected();symbol=model.symbols[contract.symbol_key(row)]
    function=model.symbols[SymbolKey('7mfk','fn',row['function'])];seen=[]
    monkeypatch.setattr(proof,'require_current',lambda current:seen.append(current) or dict(controlled_only=True))
    item=contract.item(row)
    assert proof.failure(item,symbol,model,'identity') is None
    accepted=proof.accepted(model,symbol,function,json.loads(row['proposed_claim_json']))
    assert accepted['proof']==contract.PREFIX+row['id'] and accepted['support']=='identity'
    assert accepted['scope']=='exact-natural-nested-table-reader'
    assert seen==[model,model]
    assert proof.failure(item,symbol,model,'scale') is not None
    assert proof.accepted(model,symbol,function,json.loads(row['original_claim_json'])) is None


@pytest.mark.parametrize('phase',('original','withdrawn'))
def test_a_remaining_original_link_cannot_borrow_the_qualified_owning_primary(native_models,monkeypatch,phase):
    model=native_models[phase];symbol=model.symbols[contract.symbol_key(selected())]
    def unexpected(current):raise AssertionError('an unattached original must fail before primary admission')
    monkeypatch.setattr(proof,'require_current',unexpected)
    assert proof.failure(contract.item(selected()),symbol,model,'identity') is not None


def test_positive_namespace_has_no_scalar_absence_or_scale_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('scalar-ram-leaf-withdrawal','diagnostic-record-bit4-access','maf-access'):
        assert not contract.registered(dict(mode=mode))
    assert contract.looks_like_access(as_link(json.loads(selected()['original_claim_json'])))


def test_published_call_count_and_shared_source_boundary_read_the_execution_declarations():
    import re,tomllib
    from kb import ordinary_access_registry as registry,proof_adapter
    from kb import an1_source_dispatch_access_transfers as transfers
    text=' '.join((repo.ROOT/'defs/JK08A.an1-source-dispatch-access-paths.md').read_text().split())
    count=re.search(r'makes (\d+) ordered direct calls',text)
    assert count is not None and int(count[1])==len(transfers.ROOT_CALLS)==22
    outputs=set()
    for name in proof_adapter.DESCRIPTORS:
        adapter=tomllib.loads((repo.ROOT/name).read_text())['adapter']
        outputs.update((adapter['driver'],adapter['refusals']))
    assert len(registry.FAMILIES)==42 and len(registry.captures())==85
    assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
    assert len(proof_adapter.DESCRIPTORS)==38 and len(outputs)==76
    assert f'{len(proof_adapter.DESCRIPTORS)} descriptors and {len(outputs)} generated outputs' in text


def controlled_result():
    return dict(exact_an1_source_dispatch_access_paths=True,actual_selected_table_access=True,
        **{flag:True for flag in capture.OWNING_FLAGS},**{flag:False for flag in capture.OWNING_NON_ADMISSIONS},
        native_bindings=dict(original_claim_sha256=selected()['original_claim_sha256'],owner='cautious-iguana/tbl',
            entry='7mfk:0003d832',native_width=None,native_signed=None,scope='exact-natural-nested-table-reader'))


@pytest.mark.parametrize('flag',('exact_an1_source_dispatch_access_paths','actual_selected_table_access',*capture.OWNING_FLAGS))
@pytest.mark.parametrize('fault',('missing','integer','false'))
def test_controlled_owning_result_requires_every_independent_positive_obligation(flag,fault):
    result=controlled_result();assert capture.require_owning_result(result) is True
    if fault=='missing':result.pop(flag)
    else:result[flag]=1 if fault=='integer' else False
    with pytest.raises(ValueError):capture.require_owning_result(result)


@pytest.mark.parametrize('flag',capture.OWNING_NON_ADMISSIONS)
@pytest.mark.parametrize('fault',('missing','integer','true'))
def test_owning_result_grants_no_native_geometry_scale_units_caller_or_hardware_admission(flag,fault):
    result=controlled_result()
    if fault=='missing':result.pop(flag)
    else:result[flag]=0 if fault=='integer' else True
    with pytest.raises(ValueError):capture.require_owning_result(result)


def controlled_primary():
    paths=(contract.DESCRIPTOR,'tools/kb/src/kb/an1_source_dispatch_access_native_contract.py',
        'tools/kb/src/kb/an1_source_dispatch_access_evidence.py','tools/kb/src/kb/an1_source_dispatch_access_resolution.py')
    return dict(candidate=dict(producer_inputs={name:hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()
        for name in paths}),process_sha256='controlled-primary',native_model='controlled-native')


@pytest.mark.parametrize('phase',PHASES)
def test_positive_and_withdrawal_admission_keep_the_identical_complete_primary(native_models,monkeypatch,phase):
    model=native_models[phase];record=controlled_primary();seen=[]
    def scalar(current,primary):
        assert current is model and primary is record;seen.append('withdrawal')
        return dict(controlled_only=True)
    def positive(current,primary):
        assert current is model and primary is record;seen.append('positive')
        return controlled_result()
    monkeypatch.setattr(withdrawals,'require_primary',scalar);monkeypatch.setattr(capture,'require_primary',positive)
    result=proof.require_primary(model,record)
    assert seen==(['withdrawal','positive'] if phase in ('withdrawn','combined') else ['positive'])
    assert result['original_process_sha256']==record['process_sha256'] and result['native_model']==record['native_model']
    assert result['original_claims']=={selected()['id']:selected()['original_claim_sha256']}


@pytest.mark.parametrize('fault',('withdrawal-original','positive-original','owning-flag','source-pin'))
def test_combined_owner_cannot_replace_either_complete_primary_obligation(native_models,monkeypatch,fault):
    model=native_models['combined'];record=controlled_primary()
    def scalar(current,primary):
        assert current is model and primary is record
        if fault=='withdrawal-original':raise ValueError('missing independent scalar primary')
    def positive(current,primary):
        assert current is model and primary is record
        if fault=='positive-original':raise ValueError('missing independent AN1 primary')
        result=controlled_result()
        if fault=='owning-flag':result.pop(capture.OWNING_FLAGS[-1])
        return result
    monkeypatch.setattr(withdrawals,'require_primary',scalar);monkeypatch.setattr(capture,'require_primary',positive)
    if fault=='source-pin':record['candidate']['producer_inputs'].pop(contract.DESCRIPTOR)
    with pytest.raises(ValueError):proof.require_primary(model,record)


@pytest.mark.parametrize('before,after',(('original','qualified'),('withdrawn','combined')))
def test_exact_positive_transition_preserves_original_TESTs_and_existing_physical_namespaces(native_models,monkeypatch,before,after):
    seen=[]
    monkeypatch.setattr(proof,'require_current',lambda model:seen.append(model) or dict(controlled_only=True))
    assert resolution.require_transition(native_models[before],native_models[after])==[selected()]
    assert seen==[native_models[after]]
