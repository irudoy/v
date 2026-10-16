"""Independent allocation phases preserve caller state and native model lifetimes."""

import gc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from threading import Event
import weakref

import pytest

from kb import checks, compile, convert, write
from kb.allocation import allocation_phase


@pytest.mark.parametrize('phase', ['compile', 'digest', 'checks'])
@pytest.mark.parametrize('collecting', [False, True])
@pytest.mark.parametrize('failure', [False, True])
def test_original_phase_callbacks_and_exceptions_restore_caller_state(
        monkeypatch, tmp_path, phase, collecting, failure):
    original_mode, thresholds = gc.isenabled(), gc.get_threshold()
    calls = []
    error = ValueError('controlled allocation failure')

    def callback(*args, **kwargs):
        assert gc.isenabled() == bool(calls)
        calls.append((args, kwargs))
        gc.enable()
        if failure:
            raise error

    def prohibited():
        pytest.fail('allocation changes the caller frozen generation')

    monkeypatch.setattr(gc, 'freeze', prohibited)
    monkeypatch.setattr(gc, 'unfreeze', prohibited)
    if phase == 'compile':
        callback_target = SimpleNamespace(finish=lambda: SimpleNamespace(), config={},
            overlay={}, generated={}, functions={}, spaces={})

        def builder(root, overlay):
            callback(root, overlay)
            return callback_target

        monkeypatch.setattr(compile, 'builder_of', builder)
        monkeypatch.setattr(compile.names, 'read', lambda root, overlay: [])
        monkeypatch.setattr(compile.names, 'assign', lambda model, rows: None)
        invoke = lambda: compile.build('fixture-root', {'example': 'text'}, ())
        expected = [(('fixture-root', {'example': 'text'}), {})]
    elif phase == 'digest':
        original = convert.pickle.dumps

        def dumps(*args, **kwargs):
            callback(*args, **kwargs)
            return original(*args, **kwargs)

        monkeypatch.setattr(convert.pickle, 'dumps', dumps)
        invoke = lambda: convert._model_digest(SimpleNamespace(value=1))
        expected = None
    else:
        class Model:
            root = tmp_path
            links = ()
            symbols = {}

        model = Model()
        monkeypatch.setattr(checks, 'CHECKS', {'controlled': lambda model: (callback(model) or [])})
        monkeypatch.setattr(checks, 'audit', lambda model, sections: {})
        invoke = lambda: write._issues(model)
        expected = [((model,), {})]

    try:
        (gc.enable if collecting else gc.disable)()
        if failure:
            with pytest.raises(ValueError) as caught:
                invoke()
            assert caught.value is error
        else:
            invoke()
        assert calls
        if expected is not None:
            assert calls == expected
        else:
            assert all(arguments[1] == {'protocol': 5} for arguments in calls)
        assert gc.isenabled() == collecting
        assert gc.get_threshold() == thresholds
    finally:
        (gc.enable if original_mode else gc.disable)()


def test_nested_phases_restore_each_callers_mode_and_release_temporary_cycles():
    original_mode = gc.isenabled()

    class Node:
        pass

    @allocation_phase
    def inner():
        assert not gc.isenabled()
        node = Node()
        node.self = node
        return weakref.ref(node)

    @allocation_phase
    def outer():
        reference = inner()
        assert not gc.isenabled()
        return reference

    try:
        gc.enable()
        reference = outer()
        assert gc.isenabled()
        gc.collect()
        assert reference() is None
    finally:
        (gc.enable if original_mode else gc.disable)()


def test_overlapping_thread_requests_preserve_the_callers_enabled_mode():
    original_mode = gc.isenabled()
    first_entered, second_requested, second_entered = Event(), Event(), Event()
    release_first, release_second = Event(), Event()

    @allocation_phase
    def phase(first):
        assert not gc.isenabled()
        (first_entered if first else second_entered).set()
        assert (release_first if first else release_second).wait(timeout=5)

    def second():
        second_requested.set()
        phase(False)

    try:
        gc.enable()
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(phase, True)
            assert first_entered.wait(timeout=5)
            other = pool.submit(second)
            assert second_requested.wait(timeout=5)
            second_entered.wait(timeout=0.1)
            release_first.set()
            first.result(timeout=5)
            release_second.set()
            other.result(timeout=5)
        assert gc.isenabled()
    finally:
        release_first.set()
        release_second.set()
        (gc.enable if original_mode else gc.disable)()


def test_native_models_keep_exact_digests_frozen_callers_and_cycle_release():
    source = '''
import gc
import weakref
from kb import checks, compile, convert, write

class Caller:
    pass

caller = Caller()
caller.self = caller
reference = weakref.ref(caller)
gc.freeze()
frozen, thresholds = gc.get_freeze_count(), gc.get_threshold()
del caller
before, after = compile.build.__wrapped__(), compile.build()
expected = convert._model_digest.__wrapped__(before)
assert expected == convert._model_digest(after)
# A native width refusal exercises the weak model-check owner without
# repeating the full independent check inventory of the conversion tests.
checks.CHECKS = {'widths': checks.widths}
for model in (before, after):
    field = next(entity for entity in model.entities.values() if entity.kind == 'field')
    field.props['width'] = 0
del model, field
issues = write._issues(before)
assert issues and all(issue.check == 'widths' for issue in issues.values())
assert issues == write._issues(after)
del issues
assert before is not after
assert gc.isenabled() and gc.get_threshold() == thresholds
roots = [weakref.ref(before), weakref.ref(after)]
children = [weakref.ref(next(value for value in model.meanings if value.symbols))
            for model in (before, after)]
del before, after
gc.collect()
assert all(value() is None for value in roots + children)
assert reference() is not None
assert all(value is not reference() for value in gc.get_objects())
assert 0 < gc.get_freeze_count() <= frozen
'''
    result = subprocess.run([sys.executable, '-c', source],
        cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
