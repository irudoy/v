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
