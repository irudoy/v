"""Fresh equivalent graph rows retain complete atlas bindings and structure."""

import copy
import hashlib
import json
import random

from kb import graph
from tools.romviz import graph_atlas, model


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def rows():
    meanings, symbols = [], []
    for name, kind, address, block in (
            ('a_fn', 'fn', 0x100, 'a'), ('b_fn', 'fn', 0x104, 'b'),
            ('source_a', 'ram', 0xFFFF1000, None), ('source_b', 'ram', 0xFFFF1001, None),
            ('bridge_a', 'ram', 0xFFFF1002, None), ('bridge_b', 'ram', 0xFFFF1003, None),
            ('contested', 'ram', 0xFFFF1004, None)):
        meaning = dict(key=f'{name}/{kind}', name=name, kind=kind, home='sample')
        if block:
            meaning['block'] = f'{block}/block'
        meanings.append(meaning)
        symbols.append(dict(meaning=meaning['key'], props=dict(
            key=f'sample-{address:08x}/{kind}', name=name, kind=kind,
            layout='sample', address=address)))
    keys = {row['meaning'].split('/')[0]: row['props']['key'] for row in symbols}
    links = [dict(**{'from': keys[target], 'to': keys[source]}, kind=kind, props={})
             for source, target, kind in (
                 ('a_fn', 'source_a', 'WRITER'), ('b_fn', 'source_b', 'WRITER'),
                 ('source_a', 'bridge_a', 'COPY'), ('source_b', 'bridge_b', 'COPY'),
                 ('bridge_a', 'contested', 'COPY'), ('bridge_b', 'contested', 'COPY'))]
    return dict(fingerprint='fixture', layouts=[dict(key='sample', l0='')],
                images=[dict(image='Sample', layout='sample')], meanings=meanings, symbols=symbols,
                entities=[dict(key='main/stage', kind='stage', title='Main', lane='flow'),
                          dict(key='a/block', kind='block', title='A', order=0),
                          dict(key='b/block', kind='block', title='B', order=1)],
                entity_refs=[dict(**{'from': f'{name}/block', 'to': 'main/stage'}, kind='STAGE')
                             for name in ('a', 'b')], links=links)


def test_copy_ownership_and_edge_inventory_agree_for_equivalent_row_orders():
    source = rows()
    initial = graph_atlas.Knowledge(copy.deepcopy(source)).model('sample', 'Sample').export()
    nodes = {node['id']: node for node in initial['nodes']}
    assert nodes['signal:ffff1004']['block'] == 'a'
    assert len(initial['edges']) == 6
    assert {node['id'] for node in initial['nodes']} == {
        'function:00000100', 'function:00000104',
        *[f'signal:{address:08x}' for address in range(0xFFFF1000, 0xFFFF1005)]}
    expected = canonical(initial)
    for seed in range(20):
        shuffled = copy.deepcopy(source)
        randomizer = random.Random(seed)
        for value in shuffled.values():
            if isinstance(value, list):
                randomizer.shuffle(value)
        actual = graph_atlas.Knowledge(shuffled).model('sample', 'Sample').export()
        assert canonical(actual) == expected


def test_fresh_complete_atlases_agree_for_reversed_and_shuffled_graph_rows(monkeypatch):
    original = graph.Graph.run
    fingerprints, digests, query_counts = [], [], []
    for mode in ('original', 'reversed', 'shuffled'):
        queries = []
        randomizer = random.Random(521)

        def reordered(session, query, **params):
            result = list(original(session, query, **params))
            queries.append(query)
            if mode == 'reversed':
                result.reverse()
            elif mode == 'shuffled':
                randomizer.shuffle(result)
            return result

        with monkeypatch.context() as patch:
            patch.setattr(graph.Graph, 'run', reordered)
            atlas = model.build_atlas(['all'])
        assert len(atlas['roms']) == 10
        fingerprints.append({view['fingerprint'] for view in atlas['architectures'].values()})
        digests.append(hashlib.sha256(canonical(atlas)).hexdigest())
        assert any('MATCH (n:Kb:Meaning)' in query for query in queries)
        assert any('MATCH (s:Kb:Symbol {kind: "fn"})' in query for query in queries)
        assert any('a.modes AS modes' in query for query in queries)
        query_counts.append(len(queries))
    assert fingerprints[0] == fingerprints[1] == fingerprints[2]
    assert len(fingerprints[0]) == 1
    assert digests[0] == digests[1] == digests[2]
    assert query_counts[0] == query_counts[1] == query_counts[2]
