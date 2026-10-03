"""Read-only architecture candidates from the installed MAGE procedures."""

from collections import Counter, defaultdict

from kb import repo
from kb.answer import Answer, DETAIL, FACTS, IDENTITY
from kb.repo import KbError

PROCEDURE = 'leiden_community_detection.get_subgraph'
QUERY = '''
MATCH (f:Kb:Function {layout: $layout})
WITH collect(f) AS nodes
OPTIONAL MATCH (a:Kb:Function {layout: $layout})-[r:CALL|SHARED_RAM]-(b:Kb:Function {layout: $layout})
WITH nodes, collect(DISTINCT r) AS edges
CALL leiden_community_detection.get_subgraph(nodes, edges, 'weight', 1.0, 0.01, 1.0)
YIELD node, community_id
OPTIONAL MATCH (node)<-[:AT]-(s:Kb:Symbol)<-[:HAS]-(m:Kb:Meaning)
OPTIONAL MATCH (m)-[:BLOCK]->(b:Kb:Entity {kind: 'block'})
RETURN node.address AS address, community_id AS community,
       s.name AS name, m.key AS meaning, b.key AS block
ORDER BY address
'''


def communities(rows):
    """Dominant placed blocks guide candidates; ties remain alternatives."""
    groups = defaultdict(list)
    for row in rows:
        groups[row['community']].append(row)
    found = []
    for members in groups.values():
        unplaced = [row for row in members if not row.get('block')]
        if not unplaced:
            continue
        votes = Counter(row['block'] for row in members if row.get('block'))
        most = max(votes.values(), default=0)
        blocks = sorted(block for block, count in votes.items() if count == most)
        found.append({'community': members[0]['community'], 'members': len(members),
                      'placed': sum(votes.values()), 'votes': dict(sorted(votes.items())),
                      'blocks': blocks, 'new_block': not blocks,
                      'functions': sorted(unplaced, key=lambda row: row['address'])})
    return sorted(found, key=lambda item: item['functions'][0]['address'])


def blocks(graph, layout_id, root=repo.ROOT):
    layout = repo.layout(layout_id, root).id
    available = graph.run('CALL mg.procedures() YIELD name, is_write '
                          'WHERE name = $name RETURN name, is_write', name=PROCEDURE)
    if not available or available[0]['is_write']:
        raise KbError(f'no read-only {PROCEDURE} is installed; block candidates require '
                      'the configured MAGE procedure', code=6)
    rows = graph.run(QUERY, layout=layout)
    groups = communities(rows)
    unplaced = sum(len(item['functions']) for item in groups)
    stats = graph.run(
        'MATCH (a:Kb:Function {layout: $layout})-[r:CALL|SHARED_RAM]->'
        '(b:Kb:Function {layout: $layout}) '
        'RETURN type(r) AS kind, count(r) AS count', layout=layout)
    counts = {row['kind']: row['count'] for row in stats}
    answer = Answer(f'kb suggest --blocks --layout {layout}')
    answer.section(None, IDENTITY, [
        f'[candidate] leiden_community_detection on {layout}: calls and shared RAM'])
    answer.section(None, FACTS, [
        f'{len(rows)} functions; {counts.get("CALL", 0)} calls; '
        f'{counts.get("SHARED_RAM", 0)} weighted shared-RAM pairs; '
        f'{unplaced} unplaced functions in {len(groups)} candidate communities',
        'Candidates require review; they do not change blocks or knowledge levels.'])
    for item in groups:
        targets = ', '.join(item['blocks']) if item['blocks'] else 'new block'
        votes = ', '.join(f'{block} {count}' for block, count in item['votes'].items())
        answer.section(None, DETAIL, [
            f'[candidate] {targets}: {item["placed"]}/{item["members"]} placed'
            + (f'; votes {votes}' if votes else ''),
            *(f'  {layout}:{row["address"]:08x} '
              f'{row.get("meaning") or row.get("name") or "unreviewed function"}'
              for row in item['functions'])])
    answer.data = {'producer': 'candidate', 'layout': layout, 'procedure': PROCEDURE,
                   'params': {'weight_property': 'weight', 'gamma': 1.0, 'theta': 0.01,
                              'resolution_parameter': 1.0},
                   'functions': len(rows), 'edges': counts, 'unplaced': unplaced,
                   'communities': groups}
    return answer
