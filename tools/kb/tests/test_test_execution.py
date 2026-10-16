"""The registered identity adapter requires the strict shared execution contract."""

from copy import deepcopy
import hashlib
import json
import os
import shutil
from types import SimpleNamespace

import pytest

from kb import (compile, copy_evidence, graph, levels, match, passes, repo, store,
                test_evidence as execution)
from kb.model import Link, SymbolKey
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
    candidate = {'schema': execution.SCHEMA, 'run_id': '01234567-89ab-4def-8123-456789abcdef',
                 'contract': execution.CONTRACT.packet(),
                 'assertions': {'mode': 'rewrite', 'python_optimize': 0},
                 'native_model': execution.model_digest(model),
                 'producer_inputs': execution.inputs(repo.ROOT),
                 'collected': [execution.NODEID],
                 'parameters': {execution.NODEID: execution.encode({})},
                 'reports': [[execution.NODEID, phase, 'passed', False]
                             for phase in ('setup', 'call', 'teardown')],
                 'context': execution.context(model, symbol, execution.item()),
                 'complete': True, 'exitstatus': 0,
                 'witness': {'facts': execution.facts(), 'profile_origin': origin,
                             'profiles': execution.encode({'controlled': 'values'}),
                             'images': {'1ME3B': {'path': 'fixture.bin', 'sha256': image_hash}},
                             'fixture_image_reads': [{'path': 'fixture.bin', 'sha256': image_hash}]}}
    candidate['witness']['profiles_digest'] = execution.digest(candidate['witness']['profiles'])
    process_path = tmp_path / 'process.json'
    candidate_path = tmp_path / 'candidate.json'
    record = {'schema': execution.SCHEMA, 'candidate': candidate,
              'native_model': candidate['native_model'],
              'native_inputs': execution.digest(execution.encode(candidate['producer_inputs'])),
              'terminal': {'actual_exit_code': 0, 'timed_out': False,
                           'command': ['pytest', execution.NODEID,
                                       '--kb-test-candidate=' + str(candidate_path)],
                           'declared_limit_seconds': 30, 'inclusive_process_seconds': 1.0,
                           'started_utc': '2026-10-16T00:00:00+00:00',
                           'finished_utc': '2026-10-16T00:00:01+00:00'}}

    def save(value=None):
        current = deepcopy(record if value is None else value)
        stdout.write_text('kb-test-candidate sha256=' + execution.digest(current['candidate']) + '\n')
        stderr.write_bytes(b'')
        for stream, path in (('stdout', stdout), ('stderr', stderr)):
            current['terminal'][stream] = str(path)
            current['terminal'][stream + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        original = {key: value for key, value in current['terminal'].items()
                    if key not in ('stdout', 'stderr')}
        process_path.write_text(json.dumps(original))
        current.update(process_path=str(process_path),
                       process_sha256=hashlib.sha256(process_path.read_bytes()).hexdigest(),
                       candidate_option='--kb-test-candidate=' + str(candidate_path))
        destination.write_text(json.dumps(current))
        return current

    save()
    return SimpleNamespace(model=model, symbol=symbol, record=record, save=save,
                           destination=destination, source=source, stdout=stdout, stderr=stderr,
                           process_path=process_path, candidate_path=candidate_path)


def award(state, route, monkeypatch, item=None, claim_name='identity'):
    item = execution.item() if item is None else item
    if route == 'rank':
        return match.rank(item, state.symbol, state.model, 'identity')
    if route == 'anchor':
        return match.grounded(state.model, [state.symbol.key])[state.symbol.key][0]
    claim = levels.Claim('controlled', execution.MEANING, claim_name, 'code',
                         items=[(state.symbol, item)], symbol=state.symbol)
    monkeypatch.setattr(levels._Collector, 'collect', lambda self: [claim])
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    monkeypatch.setattr(levels, '_all_items', lambda model: ())
    return levels.analyze(state.model).grounded[id(claim)]


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
def test_current_qualified_receipt_reuses_without_executing_the_case(qualified, monkeypatch, route):
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    assert award(qualified, route, monkeypatch) == match.vocab.LEVEL_RANK['code']
    assert match.verify(qualified.model, qualified.symbol, execution.item()) is None


@pytest.mark.parametrize('fault', ['missing', 'changed-source', 'scale'])
def test_scoped_levels_require_current_execution_and_identity_scope(qualified, monkeypatch, fault):
    claim = levels.Claim('controlled', execution.MEANING, 'identity', 'code',
                         items=[(qualified.symbol, execution.item())], symbol=qualified.symbol)
    monkeypatch.setattr(levels._Collector, 'collect', lambda self: [claim])
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    monkeypatch.setattr(levels, '_all_items', lambda model: ())
    subjects = {execution.MEANING}
    assert levels.check(qualified.model, subjects=subjects) == []
    saved_source = qualified.source.read_bytes()
    try:
        if fault == 'missing':
            qualified.destination.unlink()
        elif fault == 'changed-source':
            qualified.source.write_bytes(b'changed')
        else:
            claim.name = 'scale'
        complete = levels.check(qualified.model)
        selected = levels.check(qualified.model, subjects=subjects)
        assert selected == [issue for issue in complete if issue.subject in subjects]
        assert any('lacks grounding' in issue.message for issue in selected)
    finally:
        qualified.source.write_bytes(saved_source)
        qualified.save()
        claim.name = 'identity'
    assert levels.check(qualified.model, subjects=subjects) == []


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
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
            candidate['reports'][1][2] = 'failed'
        elif fault == 'skipped':
            candidate['reports'][1][2] = 'skipped'
        elif fault == 'xfail':
            candidate['reports'][1][3] = True
        elif fault == 'unrelated':
            candidate['collected'][0] += '_unrelated'
        elif fault == 'parameters':
            candidate['parameters'][execution.NODEID] = execution.encode({'wrong': 1})
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


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
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


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
def test_unrelated_writer_overlay_preserves_the_exact_identity(qualified, monkeypatch, route):
    model = deepcopy(qualified.model)
    model.overlay = {'kb/ram/independent.toml': 'summary = "Independent writer fact"\n'}
    state = SimpleNamespace(model=model, symbol=model.symbols[qualified.symbol.key])
    assert award(state, route, monkeypatch) == 2


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
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


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
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


@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
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


@pytest.mark.parametrize('fault', ['complete-int', 'exit-bool', 'phase-bool', 'contract',
                                 'process-missing', 'process-changed', 'terminal-substitution',
                                 'assertions', 'runtime'])
@pytest.mark.parametrize('route', ['rank', 'anchor', 'direct'])
def test_registered_consumers_refuse_malformed_or_substituted_execution(qualified, monkeypatch,
                                                                       route, fault):
    value = deepcopy(qualified.record)
    candidate = value['candidate']
    if fault == 'complete-int':
        candidate['complete'] = 1
    elif fault == 'exit-bool':
        candidate['exitstatus'] = False
    elif fault == 'phase-bool':
        candidate['reports'][1][3] = 0
    elif fault == 'contract':
        candidate['contract']['name'] = 'different-claim'
    elif fault == 'assertions':
        candidate['assertions']['mode'] = 'plain'
    elif fault == 'runtime':
        candidate['context']['runtime']['python_optimize'] = 1
    qualified.save(value)
    if fault == 'process-missing':
        qualified.process_path.unlink()
    elif fault == 'process-changed':
        qualified.process_path.write_bytes(b'{}')
    elif fault == 'terminal-substitution':
        current = json.loads(qualified.destination.read_bytes())
        current['terminal']['inclusive_process_seconds'] = 0.5
        qualified.destination.write_text(json.dumps(current))
    assert award(qualified, route, monkeypatch) < 2


@pytest.mark.parametrize('key', ['test_unrelated', execution.KEY])
def test_link_anchor_cannot_borrow_contextless_test_execution(qualified, key):
    model = deepcopy(qualified.model)
    symbol = model.symbols[qualified.symbol.key]
    symbol.evidence.clear()
    evidence = {**execution.item(), 'key': key, 'at': '1me3b:000791a4'}
    link = Link(symbol.meaning, 'source', symbol.meaning, None, None,
                props={'relies': 'structure'}, evidence=[evidence])
    symbol.meaning.links.append(link)
    model.links.append(link)
    assert match.grounded(model, [symbol.key])[symbol.key][0] < 2


@pytest.mark.parametrize('fault', [None, 'missing', 'scale', 'other-meaning'])
def test_actual_collector_keeps_meaning_and_symbol_identity_in_scope(qualified, monkeypatch, fault):
    model = deepcopy(qualified.model)
    symbol = model.symbols[qualified.symbol.key]
    symbol.props['level'] = 'code'
    symbol.meaning.props['level'] = 'code'
    value = deepcopy(qualified.record)
    candidate = value['candidate']
    candidate['native_model'] = execution.model_digest(model)
    candidate['context'] = execution.context(model, symbol, execution.item())
    value['native_model'] = candidate['native_model']
    qualified.save(value)
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    state = levels.analyze(model)
    identities = [claim for claim in state.claims if claim.name == 'identity']
    assert len(identities) == 2
    assert all(state.grounded[id(claim)] == 2 for claim in identities)
    if fault == 'missing':
        qualified.destination.unlink()
        refused = levels.analyze(model)
        assert all(refused.grounded[id(claim)] < 2 for claim in refused.claims)
    elif fault in ('scale', 'other-meaning'):
        claim = next(claim for claim in identities if claim.symbol is None)
        if fault == 'scale':
            claim.name = 'scale'
        else:
            claim.subject = 'other/const'
        assert match.rank(execution.item(), symbol, model, claim) < 2


def test_successful_finalization_binds_the_original_process(qualified, monkeypatch):
    qualified.candidate_path.write_text(json.dumps(qualified.record['candidate']))
    monkeypatch.setattr(compile, 'build', lambda root: qualified.model)
    monkeypatch.setattr(execution, 'producer_inputs', lambda root:
                        qualified.record['candidate']['producer_inputs'])
    from kb import lock
    previous = qualified.destination.read_bytes()
    with lock.held(repo.ROOT, timeout=1):
        prepared = execution.prepare(qualified.candidate_path, qualified.process_path,
                                     qualified.stdout, qualified.stderr, repo.ROOT)
    assert prepared['candidate'] == qualified.record['candidate']
    assert qualified.destination.read_bytes() == previous
    record = execution.finalize(qualified.candidate_path, qualified.process_path,
                                qualified.stdout, qualified.stderr, repo.ROOT)
    assert record == json.loads(qualified.destination.read_bytes())
    assert execution.failure(execution.item(), qualified.symbol, qualified.model, 'identity') is None
    qualified.process_path.write_text('{}')
    assert execution.failure(execution.item(), qualified.symbol, qualified.model, 'identity') is not None


def test_invalid_valid_invalid_receipt_cannot_escape_a_consumed_snapshot(qualified):
    valid = qualified.destination.read_bytes()
    qualified.destination.write_bytes(b'{}')
    original = copy_evidence.proof_state(repo.ROOT)
    with copy_evidence.consuming(repo.ROOT):
        qualified.destination.write_bytes(valid)
        assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') < 2
        qualified.destination.write_bytes(b'{}')
        assert copy_evidence.proof_state(repo.ROOT, live=True) == original
    qualified.destination.write_bytes(valid)
    assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') == 2


@pytest.mark.parametrize('dependency', ['receipt', 'process', 'stdout', 'stderr'])
def test_cached_pass_and_graph_meta_follow_test_output_bytes(qualified, monkeypatch, dependency):
    monkeypatch.setattr(passes.Passes, 'inputs', lambda self, name: set())
    record = passes.Passes(repo.ROOT)
    calls = []

    def check(root):
        calls.append(root)
        return [] if match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') == 2 else ['refused']

    assert record.run('controlled-test', check, changed=True) == []
    assert record.run('controlled-test', check, changed=True) is None
    assert len(calls) == 1
    original = copy_evidence.proof_state(repo.ROOT)
    path = {'receipt': qualified.destination, 'process': qualified.process_path,
            'stdout': qualified.stdout, 'stderr': qualified.stderr}[dependency]
    previous = path.stat()
    data = path.read_bytes()
    path.write_bytes(b' ' * len(data) if data else b'x')
    os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    assert graph.proof_stale({'copy_proof_state': original}, repo.ROOT)
    assert record.run('controlled-test', check, changed=True) == ['refused']
    assert len(calls) == 2


def test_mutation_during_a_check_cannot_publish_a_cached_pass(qualified, monkeypatch):
    monkeypatch.setattr(passes.Passes, 'inputs', lambda self, name: set())
    record = passes.Passes(repo.ROOT)

    def check(root):
        assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') == 2
        qualified.process_path.write_text('{}')
        # The decision keeps its original primitive inputs; publication fences the change.
        assert match.rank(execution.item(), qualified.symbol, qualified.model, 'identity') == 2
        return []

    with pytest.raises(repo.KbError, match='proof changes during the check'):
        record.run('controlled-test', check)
    assert 'controlled-test' not in record.passed


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
