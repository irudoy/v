"""Exact batch publication and owning level guards use controlled native models."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from kb import calculation_dependency_contract as contract
from kb import calculation_dependency_evidence as proof
from kb import calculation_dependency_resolution as resolution
from kb import copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import counter_threshold_factor_contract as factor
from kb import levels, repo, test_contract, write
from kb.model import Link, Meaning, Model, Symbol
from kb.repo import KbError


def representation(row, meanings, dependency=False):
    claim = json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
    return Link(meanings[claim['owner']], claim['type'], meanings[claim['to']], claim['slot'], claim['offset'],
                deepcopy(claim['props']), [contract.item(row)] if dependency else [],
                set(claim['stated']), set(claim['sources']), set(claim['roles']))


@pytest.fixture
def transition(tmp_path, monkeypatch):
    rows = contract.rows(repo.ROOT)
    factor_source = factor.descriptor(repo.ROOT)
    monkeypatch.setattr(contract, 'rows', lambda root: deepcopy(rows))
    monkeypatch.setattr(factor, 'descriptor', lambda root: deepcopy(factor_source))
    before = Model({}, {}, {}, {}, [])
    before.root, before.spaces, before.functions, before.names = tmp_path, {}, {}, []
    before.config = {'reconciliation': {'enabled': True, 'review': []}}
    meanings = {}

    def add(owner, key):
        if owner in meanings:
            return
        meaning = Meaning(key.kind, name=owner.rsplit('/', 1)[0], sources={'controlled-native.toml'})
        meanings[owner] = meaning
        before.meanings.append(meaning)
        symbol = Symbol(key, meaning=meaning, sources={'controlled-native.toml'})
        before.symbols[key] = symbol
        meaning.symbols['7mfk'] = symbol
        if owner == factor.OWNER:
            meaning.props.update(factor.FIELDS)

    for row in rows:
        for proposed in (False, True):
            claim = json.loads(row['proposed_claim_json'] if proposed else row['original_claim_json'])
            add(claim['to'], contract.target(row, proposed=proposed))
        add(row['owner'], contract.symbol_key(row))
        if row['family']=='closed-loop-feedback':
            symbol=before.symbols[contract.symbol_key(row)]
            for field in ('width','signed'):
                if row['declared_'+field]!='unset':symbol.props[field]=row['declared_'+field]
        if row['family']=='cvtc-gain':
            before.symbols[contract.symbol_key(row)].evidence=json.loads(row['original_symbol_evidence_json'])
        before.links.append(representation(row, meanings))
        path = tmp_path / json.loads(row['original_claim_json'])['sources'][0]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('controlled original source')
        before.stash.setdefault('ledger_rows', []).append((row['symbol_kind'], row['owner'].rsplit('/', 1)[0],
            json.loads(row['original_ledger_json']), json.loads(row['original_claim_json'])['sources'][0]))
    for link in before.links:
        link.owner.links.append(link)
    after = deepcopy(before)
    owners = {meaning.key: meaning for meaning in after.meanings}
    after.links = [representation(row, owners, True) for row in rows]
    for meaning in after.meanings:
        meaning.links = []
    for link in after.links:
        link.owner.links.append(link)
    after.stash['ledger_rows'] = [(row['symbol_kind'], row['owner'].rsplit('/', 1)[0],
        json.loads(row['proposed_ledger_json']), json.loads(row['original_claim_json'])['sources'][0]) for row in rows]
    resolutions = {row['operation_id']: row['original_claim_sha256'] for row in rows}
    operations = [dict(cmd='reconcile-calculation-dependency', id=key, claim_sha256=value)
                  for key, value in resolutions.items()]
    monkeypatch.setattr(proof, 'require_current', lambda model, **kwargs: dict(controlled_admission=True))
    # Controlled metadata tests grant no actual execution or namespace admission.
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        monkeypatch.setattr(module, 'scope_digest', lambda model: 'controlled-scope')
    return rows, before, after, resolutions, operations


def test_exact_batch_changes_only_registered_relations_and_original_ledger_selectors(transition):
    rows, before, after, resolutions, operations = transition
    expected = resolution.publication_expected(before, after, resolutions,
                                              write.publication_view(before), write.publication_view(after))
    assert test_contract.exact(expected, write.publication_view(after))
    assert len(rows) == len(contract.IDENTITIES) == 38
    for row, old, new in zip(rows, before.links, after.links):
        assert contract.original(row, old) and contract.dependency(row, new)
        assert contract.item(row)['supports'] == ('scale' if row['family'] == 'counter-threshold' else 'identity')
    change = SimpleNamespace(width_resolutions={}, diagnostic_resolutions={}, argument_resolutions={},
                             calculation_resolutions=resolutions, snapshot_resolutions={})
    path = before.root / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('controlled reviews')
    write.require_metadata_only(before, after, operations, change, {repo.OWNER_CONFIG: 'controlled reviews'})


@pytest.mark.parametrize('fault', ('partial', 'duplicate', 'wrong-id', 'wrong-sha', 'extra-evidence'))
def test_batch_preflight_refuses_any_incomplete_or_changed_operation(transition, fault):
    operations = deepcopy(transition[4])
    if fault == 'partial':
        operations.pop()
    elif fault == 'duplicate':
        operations[-1] = deepcopy(operations[0])
    elif fault == 'wrong-id':
        operations[0]['id'] = 'other'
    elif fault == 'wrong-sha':
        operations[0]['claim_sha256'] = '0' * 64
    else:
        operations[0]['evidence'] = [{'kind': 'arithmetic', 'value': '1=1'}]
    with pytest.raises(KbError):
        write.require_publication_operations(operations)


@pytest.mark.parametrize('fault', ('partial', 'property', 'geometry', 'role', 'via', 'layout', 'evidence',
                                  'ledger-selector', 'ledger-order', 'ledger-source', 'TEST', 'AAFA-scale'))
def test_publication_refuses_unrelated_native_origin_or_scale_changes(transition, fault):
    rows, before, after, resolutions, _ = transition
    row = rows[0]
    symbol = after.symbols[contract.symbol_key(row)]
    link = after.links[0]
    if fault == 'partial':
        resolutions.pop(next(iter(resolutions)))
    elif fault == 'property':
        symbol.meaning.props['unit'] = 'degree'
    elif fault == 'geometry':
        symbol.props['rows'] = 8
    elif fault == 'role':
        link.roles.add('scale')
    elif fault == 'via':
        link.props['via'] = []
    elif fault == 'layout':
        link.stated.add('1nd')
    elif fault == 'evidence':
        link.evidence.append({'kind': 'arithmetic', 'value': '1=1'})
    elif fault == 'ledger-selector':
        after.stash['ledger_rows'][0][2][0]['dependency'] = []
    elif fault == 'ledger-order':
        after.stash['ledger_rows'][0][2][0]['identity'].reverse()
    elif fault == 'ledger-source':
        kind, name, ledger, source = after.stash['ledger_rows'][0]
        after.stash['ledger_rows'][0] = kind, name, ledger, 'other-native.toml'
    elif fault == 'TEST':
        symbol.evidence.append({'kind': 'test', 'path': 'controlled.py', 'key': 'test_identity', 'supports': 'identity'})
    else:
        after.symbols[factor.SYMBOL].meaning.props['scale'] = 'x/100'
    with pytest.raises((ValueError, KbError)):
        expected = resolution.publication_expected(before, after, resolutions,
                                                  write.publication_view(before), write.publication_view(after))
        if not test_contract.exact(expected, write.publication_view(after)):
            raise ValueError('another native value changes')


@pytest.mark.parametrize('family,name', (('denominator', 'identity'), ('counter-threshold', 'scale'),
                                       ('scaled-publication', 'identity'), ('radical-capuchin', 'identity'),
                                       ('closed-loop-sample', 'identity')))
@pytest.mark.parametrize('failure', (None, 'unqualified original'))
def test_only_exact_owning_support_gets_direct_proof_without_reverse_donation(transition, monkeypatch, family, name, failure):
    rows, _, model, _, _ = transition
    index = next(index for index, row in enumerate(rows) if row['family'] == family)
    link = model.links[index]
    collector = object.__new__(levels._Collector)
    collector.model, collector.pointed, collector.symbols = model, set(), {}
    claims = {key: levels.Claim('controlled', key, key, 'code') for key in ('identity', 'scale')}
    collector.meanings = {(id(link.owner), key): claim for key, claim in claims.items()}
    monkeypatch.setattr(proof, 'link_failure', lambda model, link: failure)
    collector._link(link)
    selected, other = claims[name], claims['identity' if name == 'scale' else 'scale']
    assert other.deps == [] and other.items == []
    if failure is None:
        assert selected.deps == [] and selected.items == [(link.owner.symbols['7mfk'], link.evidence[0])]
    else:
        assert selected.items == [] and len(selected.deps) == 1 and selected.deps[0].lacks == failure


def test_existing_writer_prepares_the_exact_complete_reverse_only_sample_disposition(transition,monkeypatch):
    from pathlib import Path
    from kb import closed_loop_sample_argument_contract as sample,reconciliation
    from kb.model import SymbolKey
    rows,before,_,_,operations=transition
    row=next(row for row in rows if row['family']==sample.FAMILY)
    document=json.loads(row['original_native_json'])
    caller_key=SymbolKey('7mfk','fn',row['caller'])
    caller=Meaning('fn',name='enlightened-orangutan')
    caller_symbol=Symbol(caller_key,meaning=caller)
    before.symbols[caller_key]=caller_symbol;caller.symbols['7mfk']=caller_symbol;before.meanings.append(caller)
    question=dict(kind='access',subject=contract.symbol_key(row).key,claim_sha256=row['original_claim_sha256'])
    before.config['reconciliation']['review']=[dict(question,state='unresolved',reason='Retained exact original')]
    monkeypatch.setattr(reconciliation,'differences',lambda model:[deepcopy(question)])
    change=SimpleNamespace(model=before,root=before.root,calculation_resolutions={},expected=[],lines=[],
        document=lambda meaning:(Path(json.loads(row['original_claim_json'])['sources'][0]),document),
        _same_link=lambda entry,props,target:entry['type']==props['type'] and entry['to']==target.key)
    operation=next(item for item in operations if item['id']==row['operation_id'])
    resolution.prepare(change,operation)
    assert test_contract.exact(document,json.loads(row['proposed_native_json']))
    assert change.calculation_resolutions=={row['operation_id']:row['original_claim_sha256']}
    assert len(change.expected)==1


def test_existing_writer_prepares_exact_CVTC_result_and_only_its_legacy_reader_selector(transition,monkeypatch):
    from pathlib import Path
    from kb import cvtc_gain_output_contract as output,reconciliation
    from kb.model import SymbolKey
    rows,before,_,_,operations=transition
    row=next(row for row in rows if row['family']==output.FAMILY)
    document=json.loads(row['original_native_json']);caller_key=SymbolKey('7mfk','fn',row['caller'])
    caller=Meaning('fn',name='orange-hamster');caller_symbol=Symbol(caller_key,meaning=caller)
    before.symbols[caller_key]=caller_symbol;caller.symbols['7mfk']=caller_symbol;before.meanings.append(caller)
    question=dict(kind='access',subject=contract.symbol_key(row).key,claim_sha256=row['original_claim_sha256'])
    before.config['reconciliation']['review']=[dict(question,state='unresolved',reason='Retained exact original')]
    monkeypatch.setattr(reconciliation,'differences',lambda model:[deepcopy(question)])
    change=SimpleNamespace(model=before,root=before.root,calculation_resolutions={},expected=[],lines=[],
        document=lambda meaning:(Path(json.loads(row['original_claim_json'])['sources'][0]),document),
        _same_link=lambda entry,props,target:entry['type']==props['type'] and entry['to']==target.key)
    operation=next(item for item in operations if item['id']==row['operation_id'])
    resolution.prepare(change,operation)
    assert test_contract.exact(document,json.loads(row['proposed_native_json']))
    assert change.calculation_resolutions=={row['operation_id']:row['original_claim_sha256']}
    assert len(change.expected)==1


@pytest.mark.parametrize('field,value',(('width',16),('signed',False)))
@pytest.mark.parametrize('side',('symbol','meaning'))
def test_sample_argument_refuses_promotion_of_either_unset_semantic_type(transition,field,value,side):
    rows,_,model,_,_=transition
    row=next(row for row in rows if row['family']=='closed-loop-sample')
    symbol=model.symbols[contract.symbol_key(row)]
    target=symbol if side=='symbol' else symbol.meaning
    target.props[field]=value
    with pytest.raises(ValueError):proof.native_rows(model)


def test_sample_dependency_reverse_properties_cannot_donate_a_level_to_its_helper(transition,monkeypatch):
    rows,_,model,_,_=transition
    row=next(row for row in rows if row['family']=='closed-loop-sample')
    link=next(link for link in model.links if link.owner.key==row['owner'])
    collector=object.__new__(levels._Collector)
    collector.model,collector.pointed,collector.symbols=model,set(),{}
    owning=levels.Claim('controlled','identity','identity','code')
    helper=levels.Claim('controlled-helper','identity','identity','code')
    collector.meanings={(id(link.owner),'identity'):owning,(id(link.to),'identity'):helper}
    monkeypatch.setattr(proof,'link_failure',lambda model,link:None)
    collector._link(link)
    assert owning.items==[(link.owner.symbols['7mfk'],link.evidence[0])]
    assert helper.items==helper.deps==[]
