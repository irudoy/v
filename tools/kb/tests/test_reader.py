"""Bounded transaction isolation, refusal and cleanup without a live graph."""
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from kb import reader
from kb.repo import KbError


@contextmanager
def context(value):
    yield value


class Transaction:
    def __init__(self):
        self.calls=[]
        self.rolled_back=0

    def run(self,query,parameters):
        self.calls.append((query,parameters));return ['actual driver result']

    def rollback(self):
        self.rolled_back+=1


def test_parameterized_read_retains_the_existing_driver_result_api():
    transaction=Transaction()
    view=reader.ReadTransaction(transaction,{'mutate.write'})
    assert view.run('MATCH (n) RETURN n',{'a':1},b=2)==['actual driver result']
    assert transaction.calls==[('MATCH (n) RETURN n',{'a':1,'b':2})]


@pytest.mark.parametrize('query',[
    'CREATE (n)', 'MATCH (n) DETACH DELETE n', 'MATCH (n) SET n.x=1',
    'CALL mutate.write()', 'CALL mutate.write($value) YIELD x RETURN x',
    'CALL `mutate`.`write`()', 'CALL `mutate.write`()',
    "CALL periodic.iterate('MATCH (n) RETURN n', 'DELETE n', {})",
    "CALL `periodic` . `iterate`('MATCH (n) RETURN n', 'DELETE n', {})",
    "CALL `periodic.iterate`('MATCH (n) RETURN n', 'DELETE n', {})",
])
def test_mutations_and_discovered_write_procedures_are_refused_before_execution(query):
    transaction=Transaction()
    with pytest.raises(KbError):reader.ReadTransaction(transaction,{'mutate.write'}).run(query)
    assert transaction.calls==[]


@pytest.mark.parametrize('stale,body_error',[(False,False),(True,False),(False,True)])
def test_all_reads_hold_the_lock_check_freshness_and_rollback(monkeypatch,stale,body_error):
    events=[];transaction=Transaction()
    @contextmanager
    def held(root):
        events.append('lock')
        try:yield
        finally:events.append('unlock')
    class Driver:
        def session(self,**options):
            assert options=={'default_access_mode':'READ'}
            return context(SimpleNamespace(begin_transaction=lambda:transaction))
    source=SimpleNamespace(driver=Driver(),run=lambda query:[{'name':'mutate.write'}])
    def fresh(root,**options):
        assert events==['lock'] and options['held'] is True
        return context(source)
    monkeypatch.setattr(reader.lock,'held',held)
    monkeypatch.setattr(reader.graph,'fresh',fresh)
    monkeypatch.setattr(reader.graph,'meta',lambda source:{'fingerprint':'held'})
    monkeypatch.setattr(reader.fingerprint,'compute',lambda root:'after')
    monkeypatch.setattr(reader.graph,'stale',lambda original,after:stale)
    monkeypatch.setattr(reader.graph, 'proof_stale', lambda *args: False)
    if stale or body_error:
        with pytest.raises((KbError,ValueError)):
            with reader.session('root') as view:
                view.run('MATCH (n) RETURN n')
                if body_error:raise ValueError('caller failure')
    else:
        with reader.session('root') as view:view.run('MATCH (n) RETURN n')
    assert transaction.rolled_back==1
    assert events[0]=='lock'
    assert events[-1]=='unlock'


@pytest.mark.parametrize('query', [
    "RETURN 'CALL periodic.iterate()' AS text",
    'RETURN "CALL periodic.iterate()" AS text',
    'RETURN 1 // CALL periodic.iterate()',
    'RETURN 1 /* CALL periodic.iterate() */',
    'MATCH (m) RETURN m.commit, m.`CALL periodic.iterate`',
    'CALL pagerank.get() YIELD node RETURN node',
])
def test_literals_comments_and_ordinary_read_procedures_are_allowed(query):
    transaction = Transaction()
    reader.ReadTransaction(transaction, set()).run(query)
    assert transaction.calls == [(query, {})]


def test_read_waits_for_actual_writer_lock_before_opening_graph(tmp_path, monkeypatch):
    import io
    import threading
    from kb import lock
    entered = threading.Event()
    waiting = threading.Event()
    complete = threading.Event()
    errors = []
    transaction = Transaction()
    source = SimpleNamespace(driver=SimpleNamespace(session=lambda **kwargs:
        context(SimpleNamespace(begin_transaction=lambda: transaction))),
        run=lambda query: [])
    def fresh(*args, **kwargs):
        entered.set()
        return context(source)
    class Log(io.StringIO):
        def write(self, text):
            if 'waiting for' in text:
                waiting.set()
            return super().write(text)
    original = lock.held
    monkeypatch.setattr(lock, 'held', lambda root: original(root, timeout=5, log=Log()))
    monkeypatch.setattr(reader.graph, 'fresh', fresh)
    monkeypatch.setattr(reader.graph, 'meta', lambda source: {})
    monkeypatch.setattr(reader.graph, 'stale', lambda *args: False)
    monkeypatch.setattr(reader.graph, 'proof_stale', lambda *args: False)
    monkeypatch.setattr(reader.fingerprint, 'compute', lambda root: None)
    def read():
        try:
            with reader.session(tmp_path):
                pass
        except Exception as error:
            errors.append(error)
        finally:
            complete.set()
    with original(tmp_path, timeout=5):
        worker = threading.Thread(target=read)
        worker.start()
        assert waiting.wait(3), 'the reader must reach the held writer lock'
        assert not entered.is_set()
    assert complete.wait(5)
    worker.join()
    assert not errors and entered.is_set()
    assert transaction.rolled_back == 1


def test_invalid_driver_scheme_is_a_graph_error(tmp_path, monkeypatch):
    monkeypatch.setattr(reader.graph.instance, 'uri', lambda root: 'http://127.0.0.1:7687')
    with pytest.raises(KbError) as refused:
        reader.graph.Graph(tmp_path)
    assert refused.value.code == 6
    assert 'http://127.0.0.1:7687' in str(refused.value)


def test_cli_driver_failure_uses_code_6_without_a_traceback(monkeypatch, capsys):
    from neo4j.exceptions import ServiceUnavailable
    from kb import cli
    def unavailable(args):
        raise ServiceUnavailable('connection lost during read')
    monkeypatch.setattr(cli, 'command_brief', unavailable)
    assert cli.main(['brief']) == 6
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'connection lost during read' in captured.err
    assert 'KB_BOLT' in captured.err and 'Traceback' not in captured.err


def test_deferred_server_error_is_a_usage_error_and_rolls_back(monkeypatch):
    from neo4j.exceptions import Neo4jError
    transaction = Transaction()
    source = SimpleNamespace(driver=SimpleNamespace(session=lambda **kwargs:
        context(SimpleNamespace(begin_transaction=lambda: transaction))), run=lambda query: [])
    monkeypatch.setattr(reader.lock, 'held', lambda root: context(None))
    monkeypatch.setattr(reader.graph, 'fresh', lambda *args, **kwargs: context(source))
    monkeypatch.setattr(reader.graph, 'meta', lambda source: {})
    monkeypatch.setattr(reader.graph, 'proof_stale', lambda *args: False)
    with pytest.raises(KbError) as refused:
        with reader.graph_session('root'):
            raise Neo4jError._hydrate_neo4j(code='Neo.ClientError.Statement.SyntaxError', message='deferred query failure')
    assert refused.value.code == 2
    assert 'deferred query failure' in str(refused.value)
    assert transaction.rolled_back == 1


def test_read_inside_an_owned_source_boundary_does_not_reacquire_lock(monkeypatch):
    transaction = Transaction()
    source = SimpleNamespace(driver=SimpleNamespace(session=lambda **kwargs:
        context(SimpleNamespace(begin_transaction=lambda: transaction))), run=lambda query: [])
    monkeypatch.setattr(reader.lock, 'held', lambda root: pytest.fail('caller already owns the lock'))
    monkeypatch.setattr(reader.graph, 'fresh', lambda *args, **kwargs: context(source))
    monkeypatch.setattr(reader.graph, 'meta', lambda source: {})
    monkeypatch.setattr(reader.graph, 'stale', lambda *args: False)
    monkeypatch.setattr(reader.graph, 'proof_stale', lambda *args: False)
    monkeypatch.setattr(reader.fingerprint, 'compute', lambda root: None)
    with reader.session('root', held=True) as view:
        view.run('RETURN 1')
    assert transaction.calls == [('RETURN 1', {})]
    assert transaction.rolled_back == 1
