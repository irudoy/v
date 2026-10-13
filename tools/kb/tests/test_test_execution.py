"""One registered TEST needs current qualified execution in both award paths."""

from copy import deepcopy
import hashlib
import json
import shutil
from types import SimpleNamespace

import pytest

from kb import compile, levels, match, repo, store, test_evidence as execution
from kb.model import SymbolKey
from tools.kb.tests.test_match import model_of
from tools.kb.tests import writer_sources

REAL_INPUTS = execution.inputs


@pytest.fixture(scope='module')
def native_model():
    model = model_of(lambda builder: builder.symbol(*execution.SYMBOL, 'controlled',
                     group=('const', 'routine'), evidence=[execution.item()]))
    model.symbols[SymbolKey(*execution.SYMBOL)].meaning.name = MEANING_NAME
    model.names = []
    model.spaces = compile.spaces(model.config)
    model.functions = {'7mfk': frozenset({1, 2})}
    model.overlay = {}
    return model


MEANING_NAME = execution.MEANING.rsplit('/', 1)[0]


@pytest.fixture
def qualified(tmp_path, monkeypatch, native_model):
    model = native_model
    symbol = model.symbols[SymbolKey(*execution.SYMBOL)]
    source = tmp_path / 'input.txt'
    source.write_bytes(b'current')
    origin = 'a' * 64
    image_hash = 'b' * 64
    monkeypatch.setattr(execution, 'inputs', lambda root: {
        execution.PROFILE: origin, 'fixture.bin': image_hash,
        'input.txt': hashlib.sha256(source.read_bytes()).hexdigest()})
    destination = tmp_path / 'receipt.json'
    monkeypatch.setattr(execution, 'RECEIPT', destination)
    stdout, stderr = tmp_path / 'stdout.txt', tmp_path / 'stderr.txt'
    candidate = {'schema': execution.SCHEMA, 'run_id': 'controlled',
                 'native_model': execution.model_digest(model),
                 'producer_inputs': execution.inputs(repo.ROOT),
                 'nodeid': execution.NODEID, 'collected': [execution.NODEID],
                 'parameters': execution.encode({}),
                 'reports': [['setup', 'passed', False], ['call', 'passed', False],
                             ['teardown', 'passed', False]],
                 'context': execution.context(model, symbol, execution.item()),
                 'complete': True, 'exitstatus': 0,
                 'witness': {'facts': execution.facts(), 'profile_origin': origin,
                             'profiles': execution.encode({'controlled': 'values'}),
                             'images': {'1ME3B': {'path': 'fixture.bin', 'sha256': image_hash}},
                             'fixture_image_reads': [{'path': 'fixture.bin', 'sha256': image_hash}]}}
    candidate['witness']['profiles_digest'] = execution.digest(candidate['witness']['profiles'])
    record = {'schema': execution.SCHEMA, 'candidate': candidate,
              'native_model': candidate['native_model'],
              'native_inputs': execution.digest(execution.encode(candidate['producer_inputs'])),
              'terminal': {'actual_exit_code': 0, 'timed_out': False,
                           'command': ['pytest', execution.NODEID]}}

    def save(value=None):
        current = deepcopy(record if value is None else value)
        stdout.write_text('kb-test-candidate sha256=' + execution.digest(current['candidate']))
        stderr.write_bytes(b'')
        for stream, path in (('stdout', stdout), ('stderr', stderr)):
            current['terminal'][stream] = str(path)
            current['terminal'][stream + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        destination.write_text(json.dumps(current))
        return current

    save()
    return SimpleNamespace(model=model, symbol=symbol, record=record, save=save,
                           destination=destination, source=source, stdout=stdout)


def award(state, route, monkeypatch, item=None, claim_name='identity'):
    item = execution.item() if item is None else item
    if route == 'anchor':
        return match.rank(item, state.symbol, state.model, 'identity')
    claim = levels.Claim('controlled', execution.MEANING, claim_name, 'code',
                         items=[(state.symbol, item)], symbol=state.symbol)
    monkeypatch.setattr(levels._Collector, 'collect', lambda self: [claim])
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    monkeypatch.setattr(levels, '_all_items', lambda model: ())
    return levels.analyze(state.model).grounded[id(claim)]


@pytest.mark.parametrize('route', ['anchor', 'direct'])
def test_current_qualified_receipt_reuses_without_executing_the_case(qualified, monkeypatch, route):
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    assert match.verify(qualified.model, qualified.symbol, execution.item()) is None


@pytest.mark.parametrize('route', ['anchor', 'direct'])
@pytest.mark.parametrize('fault', ['missing', 'failed', 'skipped', 'xfail', 'unrelated',
                                 'parameters', 'facts', 'origin', 'model', 'incomplete',
                                 'terminal', 'streams', 'image'])
def test_unqualified_receipts_supply_no_code(qualified, monkeypatch, route, fault):
    value = deepcopy(qualified.record)
    candidate = value['candidate']
    if fault == 'missing':
        qualified.destination.unlink()
    else:
        if fault == 'failed':
            candidate['reports'][1][1] = 'failed'
        elif fault == 'skipped':
            candidate['reports'][1][1] = 'skipped'
        elif fault == 'xfail':
            candidate['reports'][1][2] = True
        elif fault == 'unrelated':
            candidate['nodeid'] += '_unrelated'
        elif fault == 'parameters':
            candidate['parameters'] = execution.encode({'wrong': 1})
        elif fault == 'facts':
            candidate['witness']['facts']['direct_branch_targets'] = 'whole region'
        elif fault == 'origin':
            candidate['witness']['profile_origin'] = 'unknown'
        elif fault == 'model':
            candidate['context']['model'] = 'other model'
        elif fault == 'incomplete':
            candidate['complete'] = False
        elif fault == 'terminal':
            value['terminal']['actual_exit_code'] = 1
        elif fault == 'image':
            candidate['witness']['images']['1ME3B']['sha256'] = 'wrong'
        qualified.save(value)
        if fault == 'streams':
            qualified.stdout.write_text('changed terminal output')
    assert award(qualified, route, monkeypatch) < match.vocab.LEVEL_RANK['code']


@pytest.mark.parametrize('route', ['anchor', 'direct'])
def test_replacement_deletion_and_input_changes_are_seen_in_one_process(qualified, monkeypatch, route):
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    value = deepcopy(qualified.record)
    value['candidate']['witness']['facts']['entry'] = '000791e4'
    qualified.save(value)
    assert award(qualified, route, monkeypatch) < match.vocab.LEVEL_RANK['code']
    qualified.save()
    qualified.source.write_bytes(b'changed')
    assert award(qualified, route, monkeypatch) < match.vocab.LEVEL_RANK['code']
    qualified.source.write_bytes(b'current')
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    qualified.destination.unlink()
    assert award(qualified, route, monkeypatch) < match.vocab.LEVEL_RANK['code']


@pytest.mark.parametrize('fault', ['no-model', 'no-symbol', 'no-claim', 'role', 'scope',
                                 'layout', 'symbol-kind', 'unrelated-case', 'foreign-symbol'])
def test_registered_case_cannot_fall_back_without_exact_context(qualified, fault):
    item = execution.item()
    model, symbol, claim = qualified.model, qualified.symbol, 'identity'
    if fault == 'no-model':
        model = None
    elif fault == 'no-symbol':
        symbol = None
    elif fault == 'no-claim':
        claim = None
    elif fault == 'role':
        item['supports'] = 'scale'
    elif fault == 'scope':
        item['note'] = 'All inbound branches and private literals are proven'
    elif fault in ('layout', 'symbol-kind', 'foreign-symbol'):
        symbol = deepcopy(symbol)
        if fault == 'layout':
            symbol.key = SymbolKey('1nd', 'const', execution.SYMBOL[2])
        elif fault == 'symbol-kind':
            symbol.key = SymbolKey('1me3b', 'fn', execution.SYMBOL[2])
    elif fault == 'unrelated-case':
        item['key'] = 'test_unrelated'
    assert match.rank(item, symbol, model, claim) < match.vocab.LEVEL_RANK['code']


def test_direct_scale_claim_cannot_use_the_identity_witness(qualified, monkeypatch):
    assert award(qualified, 'direct', monkeypatch, claim_name='scale') < match.vocab.LEVEL_RANK['code']


def test_model_value_mutation_invalidates_the_same_receipt(qualified):
    original = dict(qualified.symbol.props)
    try:
        qualified.symbol.props['summary'] = 'mutated model value'
        assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') < 2
    finally:
        qualified.symbol.props.clear()
        qualified.symbol.props.update(original)
    assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') == 2


@pytest.mark.parametrize('route', ['anchor', 'direct'])
def test_unrelated_writer_overlay_preserves_the_exact_identity(qualified, monkeypatch, route):
    model = deepcopy(qualified.model)
    model.overlay = {'kb/ram/independent.toml': 'summary = "Independent writer fact"\n'}
    state = SimpleNamespace(model=model, symbol=model.symbols[qualified.symbol.key])
    assert award(state, route, monkeypatch) == 2


@pytest.mark.parametrize('route', ['anchor', 'direct'])
def test_unrelated_review_rebase_preserves_the_exact_identity(qualified, monkeypatch, route):
    model = deepcopy(qualified.model)
    model.overlay = {repo.OWNER_CONFIG: 'Controlled unrelated review rebase'}
    model.config['reconciliation'] = {'review': [{'subject': 'independent/ram'}]}
    state = SimpleNamespace(model=model, symbol=model.symbols[qualified.symbol.key])
    assert award(state, route, monkeypatch) == 2


@pytest.fixture(scope='module')
def saved_writer_root(tmp_path_factory):
    """Real source compiler and writer with controlled terminal evidence."""
    root = tmp_path_factory.mktemp('saved-test-identity')
    writer_sources.write_sources(root)
    for path in execution.EXECUTION_INPUTS:
        target = root / path
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo.ROOT / path, target)
    for source in (repo.ROOT / 'tools/kb/src/kb').rglob('*.py'):
        target = root / source.relative_to(repo.ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    document = {'summary': 'Controlled registered identity.', 'storage': 'uint8', 'count': 1,
                'symbol': [{'layout': execution.SYMBOL[0],
                            'address': f'{execution.SYMBOL[2]:08x}',
                            'evidence': [execution.item()]}]}
    path = store.path_of('const', execution.MEANING.split('/')[0])
    store.write(root, {path: store.render('const', document)})
    return root, path, document


@pytest.mark.parametrize('route', ['anchor', 'direct'])
def test_saved_unrelated_writer_preserves_identity_and_changed_owner_refuses(
        qualified, monkeypatch, saved_writer_root, route):
    from kb import adapters, write
    from kb.adapters import files
    root, path, original = saved_writer_root
    unrelated = store.path_of('signal', 'saved_unrelated')
    store.write(root, {path: store.render('const', original), unrelated: None})
    monkeypatch.setattr(adapters, 'ADAPTERS', (files,))
    monkeypatch.setattr(execution, 'inputs', REAL_INPUTS)
    model = compile.build(root)
    symbol = model.symbols[SymbolKey(*execution.SYMBOL)]
    value = deepcopy(qualified.record)
    candidate = value['candidate']
    candidate['native_model'] = execution.model_digest(model)
    candidate['context'] = execution.context(model, symbol, execution.item())
    candidate['producer_inputs'] = dict(candidate['context']['inputs'])
    candidate['witness']['profile_origin'] = candidate['context']['inputs'][execution.PROFILE]
    image = next((p, sha) for p, sha in candidate['context']['inputs'].items()
                 if p.endswith('fixture.bin'))
    image_packet = {'path': image[0], 'sha256': image[1]}
    candidate['witness']['images'] = {'1ME3B': image_packet}
    candidate['witness']['fixture_image_reads'] = [image_packet]
    value['native_model'] = candidate['native_model']
    value['native_inputs'] = execution.digest(execution.encode(candidate['producer_inputs']))
    qualified.save(value)
    try:
        _, texts, planned = write.plan([
            {'cmd': 'new', 'kind': 'signal', 'slug': 'saved_unrelated'},
            {'cmd': 'set', 'ref': 'saved_unrelated/signal',
             'keys': {'title': 'Unrelated saved observation'}}],
            model, write.model_resolver(model), root=root)
        assert award(SimpleNamespace(model=planned, symbol=planned.symbols[symbol.key]),
                     route, monkeypatch) == 2
        store.write(root, texts)
        saved = compile.build(root)
        assert saved.overlay == {}
        assert execution.model_digest(saved) != candidate['native_model']
        assert execution.inputs(root) == candidate['context']['inputs']
        assert award(SimpleNamespace(model=saved, symbol=saved.symbols[symbol.key]),
                     route, monkeypatch) == 2
        for dependency in ('patches/can_telemetry.py', 'patches/rolling_launch.py'):
            source = root / dependency
            original_bytes = source.read_bytes()
            try:
                source.write_bytes(original_bytes + b'\n# Changed consumed calibration code.\n')
                assert award(SimpleNamespace(model=saved, symbol=saved.symbols[symbol.key]),
                             route, monkeypatch) < 2
            finally:
                source.write_bytes(original_bytes)
            assert award(SimpleNamespace(model=saved, symbol=saved.symbols[symbol.key]),
                         route, monkeypatch) == 2
        changed = {**original, 'summary': 'Changed supported owner facts.'}
        store.write(root, {path: store.render('const', changed)})
        current = compile.build(root)
        assert award(SimpleNamespace(model=current, symbol=current.symbols[symbol.key]),
                     route, monkeypatch) < 2
        assert award(SimpleNamespace(model=saved, symbol=saved.symbols[symbol.key]),
                     route, monkeypatch) < 2
    finally:
        store.write(root, {path: store.render('const', original), unrelated: None})


@pytest.mark.parametrize('route', ['anchor', 'direct'])
@pytest.mark.parametrize('fault', ['symbol', 'meaning', 'evidence', 'functions', 'config',
                                 'layout', 'space', 'execution-overlay', 'native-finalization'])
def test_writer_overlay_cannot_change_witness_inputs_or_identity(qualified, monkeypatch, route, fault):
    model = deepcopy(qualified.model)
    model.overlay = {'kb/ram/independent.toml': 'summary = "Independent writer fact"\n'}
    symbol = model.symbols[qualified.symbol.key]
    if fault == 'symbol':
        model.overlay[store.path_of('const', execution.MEANING.split('/')[0])] = (
            'summary = "Changed supported value"\n')
        symbol.props['summary'] = 'Changed supported value'
    elif fault == 'meaning':
        symbol.meaning.props['summary'] = 'Changed supported meaning'
    elif fault == 'evidence':
        symbol.evidence.clear()
    elif fault == 'functions':
        model.functions['7mfk'] = frozenset({3})
    elif fault == 'config':
        model.config['changed_execution_setting'] = True
    elif fault == 'layout':
        model.layouts.clear()
    elif fault == 'space':
        model.spaces.clear()
    elif fault == 'execution-overlay':
        model.overlay[execution.PROFILE] = 'Changed preparation input'
    else:
        value = deepcopy(qualified.record)
        value['candidate']['native_model'] = 'c' * 64
        qualified.save(value)
    state = SimpleNamespace(model=model, symbol=symbol)
    assert award(state, route, monkeypatch) < 2


def test_unregistered_definition_keeps_the_unqualified_legacy_mode():
    assert match.rank({'kind': 'test', 'path': 'other.py', 'key': 'test_other'}) == 2


@pytest.mark.parametrize('fault', ['failed', 'timeout', 'unfinished', 'other-case'])
def test_terminal_finalization_refuses_bad_process_and_preserves_prior_pass(qualified, tmp_path, fault):
    before = qualified.destination.read_bytes()
    candidate = deepcopy(qualified.record['candidate'])
    candidate_path = tmp_path / 'candidate.json'
    process_path = tmp_path / 'process.json'
    process = {'actual_exit_code': 0, 'timed_out': False,
               'command': ['pytest', execution.NODEID,
                           '--kb-test-candidate=' + str(candidate_path)]}
    if fault == 'failed':
        process['actual_exit_code'] = 1
    elif fault == 'timeout':
        process['timed_out'] = True
    elif fault == 'unfinished':
        candidate['complete'] = False
    else:
        process['command'][1] = 'unrelated-case'
    candidate_path.write_text(json.dumps(candidate))
    process_path.write_text(json.dumps(process))
    with pytest.raises(ValueError):
        execution.finalize(candidate_path, process_path, qualified.stdout,
                           tmp_path / 'stderr.txt', repo.ROOT)
    assert qualified.destination.read_bytes() == before
