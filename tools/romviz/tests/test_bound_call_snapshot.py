"""The architecture snapshot retains every source call its symbols can render."""

from kb import graph, lock, repo
from tools.romviz import graph_atlas


def test_current_snapshot_retains_every_renderable_source_call():
    knowledge = graph_atlas.snapshot()
    keys = knowledge.symbol_keys
    with lock.held(repo.ROOT):
        with graph.fresh(repo.ROOT, held=True) as session:
            assert graph.meta(session)['fingerprint'] == knowledge.fingerprint
            original = session.run('MATCH (a:Kb:Function)-[:CALL]->(b:Kb:Function) '
                                   'RETURN a.layout AS layout, a.address AS source, b.address AS target')
    expected = [row for row in original
                if f'{row["layout"]}-{row["source"]:08x}/fn' in keys
                and f'{row["layout"]}-{row["target"]:08x}/fn' in keys]
    assert expected and knowledge.calls == expected
    assert all(meaning in knowledge.meanings for meaning in knowledge.symbols)
    assert all(target['to'] in knowledge.meanings
               for analogs in knowledge.analogs.values() for target in analogs)
