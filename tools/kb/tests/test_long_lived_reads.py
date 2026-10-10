"""Long-lived readers follow exact inputs and withhold incoherent answers."""
from argparse import Namespace
from contextlib import contextmanager, nullcontext
import hashlib
from types import SimpleNamespace

import pytest

from kb import cli, compile, derive, fingerprint, mcp, reader, repo
from kb.repo import KbError
from tools.kb.tests.test_derive import image


@pytest.fixture
def compiler_inputs(tmp_path, monkeypatch):
    source = tmp_path / 'source.txt'
    source.write_text('first')
    monkeypatch.setattr(fingerprint, 'inputs', lambda root: ['source.txt'])
    from kb import compatibility
    monkeypatch.setattr(compatibility, 'reference_commit', lambda root: 'pinned')
    compile.cached.cache_clear()
    yield source
    compile.cached.cache_clear()


def test_two_mcp_checks_observe_an_edit_in_the_same_process(tmp_path, monkeypatch, compiler_inputs):
    builds = []
    def build(root):
        value = compiler_inputs.read_text()
        builds.append(value)
        return SimpleNamespace(value=value)
    monkeypatch.setattr(compile, 'build', build)
    monkeypatch.setattr(cli.lock, 'timeout_of', lambda root: 2)
    monkeypatch.setattr(cli, 'CHECKS', {'probe': lambda root: [] if compile.cached(root).value == 'first' else ['edited source']})
    monkeypatch.setattr(cli.passes, 'INPUTS', {'probe': lambda root: {'source.txt'}})
    monkeypatch.setattr(cli.passes, 'common', lambda root: set())
    original = cli.command_check
    monkeypatch.setattr(cli, 'command_check', lambda args: original(args, tmp_path))
    assert mcp.call('check', {'only': ['probe']})[0] == 0
    assert mcp.call('check', {'only': ['probe']})[0] == 0
    assert builds == ['first']
    compiler_inputs.write_text('second, changed')
    code, text = mcp.call('check', {'only': ['probe']})
    assert code == 1 and 'edited source' in text
    assert builds == ['first', 'second, changed']


def test_model_changed_during_build_is_refused_and_never_cached(tmp_path, monkeypatch, compiler_inputs):
    def changed(root):
        compiler_inputs.write_text('changed while compiling')
        return object()
    monkeypatch.setattr(compile, 'build', changed)
    with pytest.raises(KbError, match='inputs change'):
        compile.cached(tmp_path)
    assert compile.cached.cache_info().currsize == 0


@pytest.fixture
def pair_inputs(tmp_path, monkeypatch):
    tokens = tmp_path / repo.L0 / 'fixture' / 'function_tokens.csv'
    tokens.parent.mkdir(parents=True)
    tokens.write_text('func_addr,ins_addr\n00000100,00000100\n00000100,00000102\n')
    rom = tmp_path / 'stock.bin'
    rom.write_bytes(image({0x100: 0xD107, 0x102: 0x8413}, [(0x120, bytes.fromhex('ffff1234'))]))
    layout = SimpleNamespace(image='fixture')
    catalog = {'fixture': repo.Image('fixture', rom, hashlib.sha256(rom.read_bytes()).hexdigest())}
    monkeypatch.setattr(repo, 'layout', lambda name, root: layout)
    monkeypatch.setattr(repo, 'images', lambda root: catalog)
    derive.literal_pairs.cache_clear()
    yield tokens, rom, catalog
    derive.literal_pairs.cache_clear()


def test_literal_pair_cache_follows_tokens_and_revalidates_changed_rom(tmp_path, pair_inputs):
    tokens, rom, catalog = pair_inputs
    first = derive.literal_pairs('fixture', tmp_path)
    assert len(first) == 1 and first[0].address == 0xFFFF1237
    assert derive.literal_pairs('fixture', tmp_path) is first
    tokens.write_text('func_addr,ins_addr\n00000100,00000100\n')
    assert derive.literal_pairs('fixture', tmp_path) == ()
    data = bytearray(rom.read_bytes())
    data[0x123] = 0x40
    rom.write_bytes(data)
    with pytest.raises(KbError, match='digest differs'):
        derive.literal_pairs('fixture', tmp_path)
    catalog['fixture'] = repo.Image('fixture', rom, hashlib.sha256(data).hexdigest())
    tokens.write_text('func_addr,ins_addr\n00000100,00000100\n00000100,00000102\n')
    assert derive.literal_pairs('fixture', tmp_path)[0].address == 0xFFFF1243


def test_pair_inputs_changed_during_derivation_are_not_cached(tmp_path, monkeypatch, pair_inputs):
    tokens, _, _ = pair_inputs
    original = derive.function_pairs
    def changed(*args):
        result = original(*args)
        tokens.write_text('func_addr,ins_addr\n')
        return result
    monkeypatch.setattr(derive, 'function_pairs', changed)
    with pytest.raises(KbError, match='inputs change'):
        derive.literal_pairs('fixture', tmp_path)
    assert derive.literal_pairs.cache_info().currsize == 0


@pytest.mark.parametrize('as_json', [False, True])
def test_complete_graph_answer_is_rendered_before_final_check_and_never_partially_printed(monkeypatch, capsys, as_json):
    events = []
    @contextmanager
    def isolated(*args):
        events.append('lock')
        yield None
        events.append('check')
        raise KbError('source changes', code=6)
    class Data(dict):
        def items(self):
            assert events == ['lock']
            events.append('render')
            return super().items()
    found = SimpleNamespace(data=Data(value=1))
    def text(budget):
        assert events == ['lock']
        events.append('render')
        return 'complete answer\n'
    found.text = text
    monkeypatch.setattr(reader, 'graph_session', isolated)
    monkeypatch.setattr(cli, 'budget_of', lambda *args: None)
    with pytest.raises(KbError):
        cli._answer(Namespace(no_sync=True, json=as_json), 'brief', lambda source: found)
    assert events == ['lock', 'render', 'check']
    assert capsys.readouterr().out == ''


def test_source_only_answer_is_withheld_when_fingerprint_changes(monkeypatch, capsys):
    monkeypatch.setattr(cli.lock, 'held', lambda root: nullcontext())
    values = iter(['before', 'after'])
    monkeypatch.setattr(fingerprint, 'compute', lambda root: next(values))
    @cli._source_read
    def answer(args, root):
        print('partial result')
        return 0
    with pytest.raises(KbError) as refused:
        answer(None, 'root')
    assert refused.value.code == 6
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize('as_json', [False, True])
def test_cypher_never_publishes_rows_before_final_freshness_check(monkeypatch, capsys, as_json):
    class Result(list):
        def keys(self):
            return ['value']
    @contextmanager
    def isolated(*args):
        yield SimpleNamespace(run=lambda *args: Result([{'value': 1}]))
        raise KbError('source changes', code=6)
    monkeypatch.setattr(reader, 'session', isolated)
    monkeypatch.setattr(cli, 'budget_of', lambda *args: None)
    with pytest.raises(KbError):
        cli.command_cypher(Namespace(param=[], query='RETURN 1 AS value', no_sync=True, json=as_json))
    assert capsys.readouterr().out == ''
