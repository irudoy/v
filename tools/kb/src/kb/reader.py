"""Isolated fingerprint-checked read transactions for project consumers."""
from contextlib import contextmanager, nullcontext
import sys

from kb import fingerprint,graph,lock,repo


class ReadTransaction:
    """The established driver result API with mutation clauses refused."""

    def __init__(self,transaction,write_procedures,uri=None):
        self._transaction=transaction
        self._write_procedures=write_procedures
        self.uri=uri

    def run(self,query,parameters=None,**values):
        reason=graph.refusal(query,self._write_procedures)
        if reason:
            raise repo.KbError(reason,code=2)
        params=dict(parameters or {})
        params.update(values)
        from neo4j.exceptions import Neo4jError
        try:
            return self._transaction.run(query,params)
        except Neo4jError as error:
            raise repo.KbError(f'cypher: {error.message}',code=2) from None


class ReadGraph:
    """The compiler Graph result interface over one isolated transaction."""

    def __init__(self,transaction):
        self.transaction=transaction
        self.uri=transaction.uri

    def run(self,query,**params):
        return [record.data() for record in self.transaction.run(query,params)]


@contextmanager
def session(root=repo.ROOT,no_sync=False,held=False):
    """Hold the writer lock, check the source fingerprint and always roll back."""
    from neo4j.exceptions import Neo4jError
    with nullcontext() if held else lock.held(root):
        with graph.fresh(root,no_sync=no_sync,held=True,log=lambda text:print(text,file=sys.stderr)) as source:
            original=graph.meta(source)
            if graph.proof_stale(original, root):
                raise repo.KbError('the copy execution proof changes before the isolated read', code=6)
            writers={row['name'] for row in source.run(
                'CALL mg.procedures() YIELD name, is_write WHERE is_write RETURN name')}
            with source.driver.session(default_access_mode='READ') as connection:
                transaction=connection.begin_transaction()
                try:
                    yield ReadTransaction(transaction,writers,getattr(source,'uri',None))
                    if graph.stale(original,fingerprint.compute(root)):
                        raise repo.KbError('the source fingerprint changes during the isolated read',code=6)
                    if graph.proof_stale(original, root):
                        raise repo.KbError('the copy execution proof changes during the isolated read', code=6)
                except Neo4jError as error:
                    # Result consumption can report a server error after run().
                    raise repo.KbError(f'cypher: {error.message}',code=2) from None
                finally:
                    transaction.rollback()


@contextmanager
def graph_session(root=repo.ROOT,no_sync=False,held=False):
    """Expose materialized graph rows while retaining the same read boundary."""
    with session(root,no_sync,held=held) as transaction:
        yield ReadGraph(transaction)
