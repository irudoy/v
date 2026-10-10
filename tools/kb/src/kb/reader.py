"""Isolated fingerprint-checked read transactions for project consumers."""
from contextlib import contextmanager
import sys

from kb import fingerprint,graph,lock,repo


class ReadTransaction:
    """The established driver result API with mutation clauses refused."""

    def __init__(self,transaction,write_procedures):
        self._transaction=transaction
        self._write_procedures=write_procedures

    def run(self,query,parameters=None,**values):
        reason=graph.refusal(query,self._write_procedures)
        if reason:
            raise repo.KbError(reason,code=2)
        params=dict(parameters or {})
        params.update(values)
        return self._transaction.run(query,params)


@contextmanager
def session(root=repo.ROOT,no_sync=False):
    """Hold the writer lock, check the source fingerprint and always roll back."""
    with lock.held(root):
        with graph.fresh(root,no_sync=no_sync,held=True,log=lambda text:print(text,file=sys.stderr)) as source:
            original=graph.meta(source)
            writers={row['name'] for row in source.run(
                'CALL mg.procedures() YIELD name, is_write WHERE is_write RETURN name')}
            with source.driver.session(default_access_mode='READ') as connection:
                transaction=connection.begin_transaction()
                try:
                    yield ReadTransaction(transaction,writers)
                    if graph.stale(original,fingerprint.compute(root)):
                        raise repo.KbError('the source fingerprint changes during the isolated read',code=6)
                finally:
                    transaction.rollback()
