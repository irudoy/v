"""Exact shared native postimages, retained function and owning result refusals."""
from copy import deepcopy
import json
import pytest
from kb import compile,repo,store,test_origins
from kb import scalar_ram_leaf_withdrawal_contract as owning
from kb import scalar_ram_leaf_withdrawal_evidence as family
from kb import map_bias_division_caller_withdrawal_contract as contract
from kb import map_bias_division_caller_withdrawal_capture_evidence as capture


def selected():
    return [row for row in owning.descriptor(repo.ROOT)['reference']
        if row['component']=='map_bias_division_caller_withdrawal_paths']


def test_exact_reader_withdrawal_preserves_complete_joint_owner_types_units_and_all_other_claims():
    row,=selected()
    assert row['original_claim_sha256']=='4ab4eef347a3af18890ac2e967e38f483d8b48d5322c8cebffc136692bf01688'
    assert row['declared_width']==row['declared_signed']=='unset'
    claim=json.loads(row['original_claim_json'])
    assert (claim['type'],claim['owner'],claim['to'])==('reader','rev_limit_throttle_cut/tbl','malachite-fossa/fn')
    before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json']);expected=deepcopy(before)
    shared=[item for item in owning.descriptor(repo.ROOT)['reference'] if item['owner']==row['owner']]
    assert len(shared)>=5
    for item in shared:
        original=json.loads(item['original_claim_json'])
        links=[link for link in expected['link'] if (link['type'],link['to'])==(original['type'],original['to'])]
        assert len(links)==1 and links[0]['layouts']==['7mfk'];expected['link'].remove(links[0])
        removed=[]
        for marker in expected.get('ledger',[]):
            retained=[]
            for dependency in marker.get('dependency',[]):
                if (dependency.get('type'),dependency.get('to'),dependency.get('end'))==(original['type'],original['to'],'owner'):
                    removed.append(dependency)
                else:retained.append(dependency)
            if 'dependency' in marker:
                if retained:marker['dependency']=retained
                else:marker.pop('dependency')
        assert len(removed)==1
        assert json.loads(item['original_native_json'])==before
        assert json.loads(item['proposed_native_json'])==after
    assert after==expected and after['unit']==before['unit']=='RPM'
    assert after['symbol']==before['symbol'] and len(after['symbol'])==6
    assert {key:value for key,value in before.items() if key not in ('link','ledger')}=={
        key:value for key,value in after.items() if key not in ('link','ledger')}


def test_complete_native_function_preserves_request_dependencies_all_ledger_ends_and_TESTs():
    value=owning.descriptor(repo.ROOT)
    function,=[row for row in value['function'] if row['function']==0x702C6]
    before=owning.function_native_document(function,'original');after=owning.function_native_document(function,'proposed')
    assert function['owner']=='malachite-fossa/fn' and before==after
    assert before['block']=='torque_request/block' and before['role']=='consumer'
    assert any(dependency.get('to')=='shapeless-cricket/ram'
        for marker in before['ledger'] for dependency in marker.get('dependency',[]))
    assert any(dependency.get('to')=='amber-kestrel/ram' and dependency.get('end')=='to'
        for marker in before['ledger'] for dependency in marker.get('dependency',[]))
    assert all(dependency.get('to')!='rev_limit_throttle_cut/tbl'
        for marker in before['ledger'] for dependency in marker.get('dependency',[]))
    assert any('JK08A.throttle-control.md' in note for note in before['note'])


def result():
    return dict(**{name:True for name in capture.OWNING_FLAGS},**{name:False for name in capture.NON_ADMISSIONS},
        stdout_sha256='1'*64,direct_helper_original_stdout_sha256='2'*64,
        native_bindings=[dict(symbol='7mfk-0000942c/tbl',meaning='rev_limit_throttle_cut/tbl',
            function='7mfk-000702c6/fn',function_meaning='malachite-fossa/fn',
            original_claim_sha256='4ab4eef347a3af18890ac2e967e38f483d8b48d5322c8cebffc136692bf01688')])


@pytest.mark.parametrize('flag',capture.OWNING_FLAGS)
@pytest.mark.parametrize('fault',('missing','false','integer'))
def test_owning_consumer_requires_every_independent_actual_result_flag(flag,fault):
    value=result();assert capture.require_owning_result(value) is True
    if fault=='missing':value.pop(flag)
    else:value[flag]=1 if fault=='integer' else False
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.mark.parametrize('flag',capture.NON_ADMISSIONS)
@pytest.mark.parametrize('fault',('missing','true','integer'))
def test_owning_boundary_adds_no_native_scale_unit_geometry_caller_or_hardware_fact(flag,fault):
    value=result()
    if fault=='missing':value.pop(flag)
    else:value[flag]=0 if fault=='integer' else True
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.mark.parametrize('fault',('owner','function','original','shape','helper-hash'))
def test_owning_result_refuses_a_different_original_native_scope_or_missing_same_primary_helper(fault):
    value=result()
    if fault=='shape':value['native_bindings']={}
    elif fault=='helper-hash':value['direct_helper_original_stdout_sha256']='missing'
    else:value['native_bindings'][0][{'owner':'meaning','function':'function','original':'original_claim_sha256'}[fault]]='changed'
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.fixture(scope='module')
def native_models():
    from pathlib import Path
    declared=owning.descriptor(repo.ROOT);models={}
    for phase in ('original','proposed'):
        overlay={Path(row['source']):store.render(row['owner'].rsplit('/',1)[1],json.loads(row[phase+'_native_json']))
            for row in declared['reference']}
        overlay.update({Path(row['source']):store.render('fn',owning.function_native_document(row,phase))
            for row in declared['function']})
        models[phase]=compile.build(repo.ROOT,overlay)
    return models


def test_complete_native_phases_keep_every_original_TEST_origin_and_position(native_models):
    before,after=(native_models[phase] for phase in ('original','proposed'))
    assert family.native_rows(before,'original')==family.native_rows(after,'proposed')
    assert {key:origin.packet() for key,origin in test_origins.index(before).items()}=={
        key:origin.packet() for key,origin in test_origins.index(after).items()}


@pytest.mark.parametrize('phase',('original','proposed'))
@pytest.mark.parametrize('fault',('owner-unit','other-reader','symbol-TEST','ledger-position','function-note','function-TEST'))
def test_actual_native_consumer_refuses_unrelated_owner_function_or_TEST_changes(native_models,monkeypatch,phase,fault):
    row,=selected();model=native_models[phase];load=store.load
    function,=[item for item in owning.descriptor(repo.ROOT)['function'] if item['function']==0x702C6]
    path=function['source'] if fault.startswith('function-') else row['source']
    def changed(root,name,overlay=None):
        value=deepcopy(load(root,name,overlay))
        if str(name)!=path:return value
        if fault=='owner-unit':value['unit']='unregistered unit'
        elif fault=='other-reader':value['link'].pop()
        elif fault.endswith('TEST'):value['symbol'][0]['evidence']=[]
        elif fault=='ledger-position':value['ledger'][0]['order']+=1
        else:value['note']=[]
        return value
    monkeypatch.setattr(store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(model,phase)


def test_specification_counts_read_the_exact_unit_and_physical_sources():
    from kb import map_bias_division_caller_withdrawal_transfers as transfers
    words=' '.join((repo.ROOT/'defs/JK08A.map-bias-division-caller-withdrawal-paths.md').read_text().split())
    value=contract.descriptor(repo.ROOT)
    assert len(value['unit']['code'])==9 and 'nine complete function bodies' in words
    count=sum((row['end']-row['start'])//2 for row in value['unit']['code'])
    assert count==453 and f'{count} stock instructions' in words
    assert len(value['unit']['pools'])==21 and '21 literal pools' in words
    assert len(value['unit']['aliases'])==3 and all(row['width']==4 for row in value['unit']['aliases']) and 'three four-byte ordinary RAM pointer aliases' in words
    assert len(transfers.OPERANDS)==88 and '88 physical operand sites' in words
    row,=selected();prior=[item for item in owning.descriptor(repo.ROOT)['reference'][:134]
        if item['owner']==row['owner'] and item['id']!=row['id']]
    assert len(prior)==4 and 'four prior withdrawals' in words


def test_current_publications_read_the_exact_execution_registries_and_selector_rows():
    import tomllib
    from kb import ordinary_access_registry as registry,proof_adapter
    declared=owning.descriptor(repo.ROOT)
    references=declared['reference'];functions=declared['function']
    readers=sum(json.loads(row['original_claim_json'])['type']=='reader' for row in references)
    writers=len(references)-readers
    owners=len({row['owner'] for row in references})
    datum_removed=0
    for owner in {row['owner'] for row in references}:
        row=next(row for row in references if row['owner']==owner)
        before=json.loads(row['original_ledger_json']) or []
        after=json.loads(row['proposed_ledger_json']) or []
        datum_removed+=sum(len(marker.get('dependency',[])) for marker in before)-sum(len(marker.get('dependency',[])) for marker in after)
    function_removed=sum(sum(len(marker.get('dependency',[])) for marker in owning.function_native_document(row,'original').get('ledger',[]))
        -sum(len(marker.get('dependency',[])) for marker in owning.function_native_document(row,'proposed').get('ledger',[])) for row in functions)
    assert (len(references),readers,writers,owners,len(functions),datum_removed,function_removed)==(136,125,11,101,76,120,8)
    assert len(family.COMPONENTS)==35
    for path in ('tools/sh-elf-run/README.md','tools/kb/ordinary-access.md',
            'defs/JK08A.map-bias-division-caller-withdrawal-paths.md','defs/JK08A.register-overflow-paths.md'):
        text=' '.join((repo.ROOT/path).read_text().split())
        for phrase in (f'{len(references)} normal unlinks' if not path.endswith('-paths.md') else f'{len(references)} exact access originals',
                f'{readers} readers',f'{owners} '+('complete datum owners' if path.endswith('-paths.md') else 'full datum owners'),
                f'{len(functions)} complete functions',f'{datum_removed+function_removed} matching ledger selectors',
                f'{datum_removed} datum-end',f'{function_removed} function-end','Thirty-five independent components'):
            assert phrase in text,(path,phrase)
    outputs=set()
    for path in proof_adapter.DESCRIPTORS:
        adapter=tomllib.loads((repo.ROOT/path).read_text())['adapter'];outputs.update((adapter['driver'],adapter['refusals']))
    text=' '.join((repo.ROOT/'defs/JK08A.map-bias-division-caller-withdrawal-paths.md').read_text().split())
    assert len(registry.FAMILIES)==42 and len(registry.captures())==88
    assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
    assert len(proof_adapter.DESCRIPTORS)==41 and len(outputs)==82
    assert f'{len(proof_adapter.DESCRIPTORS)} descriptors and {len(outputs)} generated outputs' in text
    preceding=set()
    for path in proof_adapter.DESCRIPTORS[:proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)]:
        adapter=tomllib.loads((repo.ROOT/path).read_text())['adapter'];preceding.update((adapter['driver'],adapter['refusals']))
    assert f'{len(preceding)} preceding generated outputs' in text
    readme=' '.join((repo.ROOT/'tools/sh-elf-run/README.md').read_text().split())
    assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in readme
