"""Index loads preserve caller collection state and unrelated model lifetimes."""

import gc
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from kb import match


@pytest.mark.parametrize('collecting', [False, True])
@pytest.mark.parametrize('failure', [False, True])
def test_index_load_restores_caller_gc_state_on_every_path(tmp_path, monkeypatch,
                                                         collecting, failure):
    original_mode, thresholds = gc.isenabled(), gc.get_threshold()
    monkeypatch.setattr(match.repo, 'layout', lambda layout, root: SimpleNamespace(id=layout))
    monkeypatch.setattr(match.repo, 'config', lambda root: {})
    monkeypatch.setattr(match, '_cache_key', lambda layout, root, gram: 'fixture-index')
    calls = []

    def prohibited():
        pytest.fail('the index loader changes the caller frozen generation')

    monkeypatch.setattr(gc, 'freeze', prohibited)
    monkeypatch.setattr(gc, 'unfreeze', prohibited)

    def load(layout, root, gram):
        calls.append(layout)
        assert not gc.isenabled()
        gc.enable()
        if failure:
            raise RuntimeError('fixture loader failure')
        return SimpleNamespace(marker='unchanged index')

    monkeypatch.setattr(match.Code, 'load', load)
    match._code.cache_clear()
    try:
        (gc.enable if collecting else gc.disable)()
        if failure:
            with pytest.raises(RuntimeError, match='fixture loader failure'):
                match.code('fixture', tmp_path)
        else:
            assert match.code('fixture', tmp_path).marker == 'unchanged index'
            assert gc.isenabled() == collecting
            match._code.cache_clear()
            assert match.code('fixture', tmp_path).marker == 'unchanged index'
            assert calls == ['fixture']
        assert gc.isenabled() == collecting
        assert gc.get_threshold() == thresholds
    finally:
        match._code.cache_clear()
        (gc.enable if original_mode else gc.disable)()


def test_public_native_index_keeps_frozen_caller_cycles_and_releases_new_model():
    source = '''
import gc
import weakref
from kb import compile as compiler, match

class Caller:
    pass

caller = Caller()
caller.cycle = caller
previous = weakref.ref(caller)
gc.freeze()
del caller
frozen = gc.get_freeze_count()
mode, thresholds = gc.isenabled(), gc.get_threshold()
model = compiler.build()
root = weakref.ref(model)
child = weakref.ref(next(meaning for meaning in model.meanings if meaning.symbols))
index = match.code('7mfk')
assert index.functions
assert gc.isenabled() == mode and gc.get_threshold() == thresholds
assert 0 < gc.get_freeze_count() <= frozen
assert previous() is not None
assert all(obj is not previous() for obj in gc.get_objects())
del model
gc.collect()
assert root() is None and child() is None
assert previous() is not None
assert all(obj is not previous() for obj in gc.get_objects())
assert 0 < gc.get_freeze_count() <= frozen
'''
    result = subprocess.run([sys.executable, '-c', source],
                            cwd=Path(__file__).resolve().parents[3],
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
