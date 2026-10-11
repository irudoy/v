"""Layout-specific architecture views read from the current kb graph.

An address belongs to an actual symbol of the selected layout and image.
A missing binding remains unavailable; no other image supplies it.
The address-map layers retain their stock-image and source-file gates.
"""

from collections import defaultdict
from types import SimpleNamespace

from kb import graph, lock, repo, vocab
from tools.romviz import architecture as architecture_model


def identifier(key):
    return key.split('/')[0].replace('_', '-')


def text(value):
    return '\n'.join(value) if isinstance(value, list) else value or ''


class Knowledge:
    """One consistent graph snapshot shared by all ROMs in an atlas build."""

    def __init__(self, rows):
        self.fingerprint = rows.get('fingerprint', '')
        self.layouts = {item['key']: item for item in rows.get('layouts', [])}
        self.images = {item['image']: item['layout'] for item in rows.get('images', [])}
        self.meanings = {item['key']: item for item in rows.get('meanings', [])}
        self.entities = {item['key']: item for item in rows.get('entities', [])}
        self.symbols = defaultdict(dict)
        self.symbol_keys = {}
        for row in rows.get('symbols', []):
            symbol = row['props']
            self.symbols[row['meaning']][symbol['layout']] = symbol
            self.symbol_keys[symbol['key']] = (row['meaning'], symbol)
        self.statuses = defaultdict(list)
        for row in rows.get('statuses', []):
            status = {'layout': row['layout'], **row['props']}
            current = self.layouts.get(row['layout'], {}).get('l0', '')[:16]
            if status.get('state') == 'unresolved' and current and status.get('l0') != current:
                status['stale'] = True
            self.statuses[row['meaning']].append(status)
        self.analogs = defaultdict(list)
        for row in rows.get('analogs', []):
            self.analogs[row['from']].append({'to': row['to'], **row['props']})
            self.analogs[row['to']].append({'to': row['from'], **row['props']})
        self.refs = defaultdict(lambda: defaultdict(list))
        for row in rows.get('entity_refs', []):
            self.refs[row['from']][row['kind']].append(row['to'])
        self.steps = defaultdict(list)
        for row in rows.get('steps', []):
            self.steps[row['chain']].append(row)
        self.step_refs = defaultdict(lambda: defaultdict(list))
        for row in sorted(rows.get('step_refs', []), key=lambda row: row.get('order') or 0):
            self.step_refs[row['from']][row['kind']].append(row['to'])
        self.links = rows.get('links', [])
        self.calls = rows.get('calls', [])
        self.accesses = rows.get('accesses', [])
        self.models = {}

    def binding(self, meaning, layout, image=None):
        facts = self.meanings[meaning]
        candidate = self.symbols[meaning].get(layout)
        images = candidate.get('images', []) if candidate else []
        excluded = bool(images) and image is not None and image not in images
        symbol = None if excluded else candidate
        return {
            'meaning': meaning, 'name': facts['name'], 'home': facts.get('home'),
            'former': sorted(set(facts.get('former', []))
                             | set(symbol.get('former', []) if symbol else [])),
            'layout': layout, 'symbol': symbol['key'] if symbol else None,
            'image': image, 'images': images,
            'availability': 'image-excluded' if excluded else 'bound' if symbol else 'missing',
            'reference': (f'{symbol["name"]}/{facts["kind"]}/'
                          f'{layout}-{symbol["address"]:08x}') if symbol else None,
            'symbols': [{'layout': key, 'address': f'{item["address"]:08x}',
                         'name': item.get('name'),
                         'ref': f'{item["name"]}/{facts["kind"]}/{key}-{item["address"]:08x}',
                         'level': item.get('level', facts.get('level')),
                         'images': item.get('images', [])}
                        for key, item in sorted(self.symbols[meaning].items())],
            'statuses': sorted(self.statuses[meaning], key=lambda item: item['layout']),
            'analogs': [{**item, 'name': self.meanings[item['to']]['name']}
                        for item in self.analogs[meaning]],
        }

    def model(self, layout, image=None):
        if image is not None and self.images.get(image) != layout:
            raise ValueError(f'{image} belongs to {self.images.get(image)}, not to {layout}')
        key = (layout, image)
        if key not in self.models:
            self.models[key] = LayoutArchitecture(self, layout, image)
        return self.models[key]


def snapshot(root=repo.ROOT):
    """Read through the primary graph under its writer lock."""
    with lock.held(root):
        with graph.fresh(root, held=True) as session:
            def nodes(label):
                return [dict(row['node']) for row in session.run(
                    f'MATCH (n:Kb:{label}) RETURN n AS node')]

            rows = {
                'fingerprint': graph.meta(session)['fingerprint'],
                'layouts': nodes('Layout'), 'meanings': nodes('Meaning'),
                'entities': nodes('Entity'),
                'images': session.run('MATCH (i:Kb:Image)-[:IN]->(l:Kb:Layout) '
                                      'RETURN i.key AS image, l.key AS layout'),
                'symbols': [{'meaning': row['meaning'], 'props': dict(row['symbol'])}
                            for row in session.run('MATCH (m:Kb:Meaning)-[:HAS]->(s:Kb:Symbol) '
                                                   'RETURN m.key AS meaning, s AS symbol')],
                'statuses': [{'meaning': row['meaning'], 'layout': row['layout'],
                              'props': dict(row['relation'])} for row in session.run(
                    'MATCH (m:Kb:Meaning)-[r:STATUS]->(l:Kb:Layout) '
                    'RETURN m.key AS meaning, l.key AS layout, properties(r) AS relation')],
                'analogs': [{'from': row['from'], 'to': row['to'],
                             'props': dict(row['relation'])} for row in session.run(
                    'MATCH (m:Kb:Meaning)-[r:ANALOG]->(n:Kb:Meaning) '
                    'RETURN m.key AS from, n.key AS to, properties(r) AS relation')],
                'entity_refs': session.run(
                    'MATCH (e:Kb:Entity)-[r:STAGE|BLOCK|REGISTER|FUNCTION|OUTPUT]->(t:Kb) '
                    'RETURN e.key AS from, type(r) AS kind, t.key AS to'),
                'steps': [{'chain': row['chain'], 'order': row['order'],
                           'props': dict(row['step'])} for row in session.run(
                    'MATCH (e:Kb:Entity {kind: "chain"})-[r:STEP]->(s:Kb:Step) '
                    'RETURN e.key AS chain, r.order AS order, s AS step')],
                'step_refs': session.run(
                    'MATCH (s:Kb:Step)-[r:FROM|TO|THROUGH]->(m:Kb:Meaning) '
                    'RETURN s.key AS from, type(r) AS kind, r.order AS order, m.key AS to'),
                'links': [{'from': row['from'], 'to': row['to'], 'kind': row['kind'],
                           'props': dict(row['relation'])} for row in session.run(
                    'MATCH (a:Kb:Symbol)-[r]->(b:Kb:Symbol) WHERE r.src = "links" '
                    'RETURN a.key AS from, b.key AS to, type(r) AS kind, properties(r) AS relation')
                          if row['kind'].lower() in vocab.LINK_TYPES],
                'calls': session.run(
                    'MATCH (s:Kb:Symbol {kind: "fn"}) '
                    'WITH collect([s.layout, s.address]) AS bound '
                    'MATCH (a:Kb:Function)-[:CALL]->(b:Kb:Function) '
                    'WHERE [a.layout, a.address] IN bound AND [a.layout, b.address] IN bound '
                    'RETURN a.layout AS layout, a.address AS source, b.address AS target'),
                'accesses': session.run(
                    'MATCH (s:Kb:Symbol)-[:AT]->(:Kb:Location)<-[a:ACCESS]-(f:Kb:Function) '
                    'MATCH (g:Kb:Symbol {kind: "fn"})-[:AT]->(f) '
                    'RETURN g.key AS source, s.key AS target, '
                    'a.modes AS modes, a.producer AS producer'),
            }
    return Knowledge(rows)


NODE_KINDS = {'fn': 'function', 'ram': 'signal', 'reg': 'register', 'tbl': 'map',
              'axis': 'axis', 'const': 'rom', 'hook': 'rom', 'did': 'rom', 'dtc': 'rom'}
PREFIXES = {'fn': 'function', 'ram': 'signal', 'reg': 'register', 'tbl': 'map', 'axis': 'axis'}
LINK_RULES = {
    'WRITER': (True, 'data', 'writes'), 'READER': (False, 'data', 'consumer'),
    'INPUT': (True, 'data', 'input'), 'COPY': (True, 'data', 'copy'),
    'INDEX': (True, 'data', 'index'), 'AXIS': (True, 'data', 'axis'),
    'LOOKUP': (True, 'data', 'lookup'), 'SELECTOR': (True, 'control', 'selector'),
    'THRESHOLD': (True, 'control', 'threshold'), 'BASE': (False, 'pair', 'base'),
    'TARGET': (False, 'control', 'target'), 'SOURCE': (True, 'data', 'source'),
    'MONITOR': (True, 'control', 'monitor'),
}


class LayoutArchitecture(architecture_model.Architecture):
    """The existing view schema with nodes from one layout's real symbols."""

    def __init__(self, knowledge, layout, image=None):
        self.knowledge, self.rom = knowledge, layout
        self.image, self.view_key = image, image or layout
        self.source = repo.ROOT / 'tools/kb'
        self.summary = (f'Architecture from symbols applicable to {image} in layout {layout}.'
                        if image else f'Architecture from the bound symbols of layout {layout}.')
        self.ledgers = SimpleNamespace(paths={})
        self.errors, self.nodes, self.edges, self._spec_cache = [], {}, {}, {}
        self.by_meaning, self.by_symbol = {}, {}
        for meaning, symbols in knowledge.symbols.items():
            if layout not in symbols:
                continue
            symbol, facts = symbols[layout], knowledge.meanings[meaning]
            binding = knowledge.binding(meaning, layout, image)
            if binding['symbol'] is None:
                continue
            props = {**facts, **symbol}
            kind, address = symbol['kind'], f'{symbol["address"]:08x}'
            node_id = f'{PREFIXES.get(kind, kind)}:{address}'
            label = (props.get('title') or props.get('editor', {}).get('name')
                     or architecture_model.first_sentence(text(props.get('summary', '')),
                                                            symbol.get('name') or meaning))
            self.nodes[node_id] = architecture_model.Node(
                node_id, NODE_KINDS[kind], address, text(label),
                text(props.get('summary')), text(props.get('note')),
                props.get('level', ''), props.get('role', ''), props.get('unit', ''),
                ', '.join(facts.get('src', [])),
                meta={'binding': binding, 'kbKind': kind,
                      'summaryLayout': layout if 'summary' in symbol else facts.get('home'),
                      'noteLayout': layout if 'note' in symbol else facts.get('home'),
                      'scale': props.get('scale'), 'scaleConfidence': props.get('scale_level'),
                      'contract': props.get('contract'),
                      'contractConfidence': props.get('contract_level'),
                      'shape': {key: props[key] for key in ('width', 'signed', 'storage',
                                'cols', 'rows', 'points', 'count') if key in props}},
                block=identifier(facts['block']) if facts.get('block') else None)
            self.by_meaning[meaning] = node_id
            self.by_symbol[symbol['key']] = node_id
        self._graph_edges()
        self._index_edges()
        self.stages = [architecture_model.Stage(identifier(item['key']), item.get('title', ''),
                                                item.get('lane', 'flow'), text(item.get('summary')))
                       for item in self._entities('stage')]
        self.blocks = self._blocks()
        self.endpoints = self._endpoints()
        self.chains, self.chain_availability = self._chains()
        self._derive_blocks()
        self.flows = self._derive_flows()
        for chain in self.chains:
            chain.impact = self._chain_impact(chain)

    def _entities(self, kind):
        return sorted((row for row in self.knowledge.entities.values() if row['kind'] == kind),
                      key=lambda row: (row.get('order', 0), row['key']))

    def _graph_edges(self):
        for row in self.knowledge.calls:
            if row['layout'] != self.rom:
                continue
            first = self.by_symbol.get(f'{self.rom}-{row["source"]:08x}/fn')
            second = self.by_symbol.get(f'{self.rom}-{row["target"]:08x}/fn')
            if first is not None and second is not None:
                self._add_edge(first, second, 'call', 'calls', 'L0')
        for row in self.knowledge.accesses:
            first, second = self.by_symbol.get(row['source']), self.by_symbol.get(row['target'])
            if first is None or second is None:
                continue
            modes = set(row.get('modes') or [])
            producer = row.get('producer', 'access')
            origin = 'L0 export' if producer == 'l0' else f'L0 {producer}'
            if modes & set(graph.STORE_MODES):
                self._add_edge(first, second, 'data', 'writes', origin)
            if modes & set(graph.LOAD_MODES):
                # A literal or a parameter proves a reference, not a load
                # from the referenced address or a physical computation.
                actual_load = modes & {'load', 'read', 'update', 'read_write'}
                self._add_edge(second, first, 'data' if actual_load else 'access',
                               'reads' if actual_load else 'references', origin)
        for row in self.knowledge.links:
            if row['from'] not in self.by_symbol or row['to'] not in self.by_symbol:
                continue
            first, second = self.by_symbol[row['from']], self.by_symbol[row['to']]
            rule = LINK_RULES.get(row['kind'])
            origin = 'verified claim' if row['props'].get('verified') else 'unverified claim'
            if row['kind'] == 'DEPENDS':
                for role in row['props'].get('role', []):
                    rule = self._edge_rule(self.nodes[first].kind, role, self.nodes[second].kind)
                    if rule:
                        reverse, kind = rule
                        self._add_edge(second if reverse else first, first if reverse else second,
                                       kind, role, origin)
            elif rule:
                reverse, kind, role = rule
                self._add_edge(second if reverse else first, first if reverse else second,
                               kind, role, origin)

    def _blocks(self):
        found = []
        for item in self._entities('block'):
            stages = self.knowledge.refs[item['key']]['STAGE']
            members = [node for node in self.nodes.values() if node.block == identifier(item['key'])]
            found.append(architecture_model.Block(
                identifier(item['key']), item.get('title', ''), identifier(stages[0]),
                text(item.get('summary')), tuple(item.get('specs', [])),
                tuple(node.id for node in members if node.kind == 'function'),
                tuple(node.id for node in members if node.kind in ('map', 'axis')),
                tuple(node.id for node in members if node.kind in ('signal', 'register')),
                bool(item.get('generic'))))
        return found

    def _endpoints(self):
        found = []
        for item in self._entities('endpoint'):
            refs = self.knowledge.refs[item['key']]
            registers = tuple(self.by_meaning[key] for key in refs['REGISTER'] if key in self.by_meaning)
            functions = tuple(self.by_meaning[key] for key in refs['FUNCTION'] if key in self.by_meaning)
            if not registers and not functions:
                continue
            found.append(architecture_model.Endpoint(
                identifier(item['key']), item.get('title', ''), item.get('direction', 'input'),
                identifier(refs['BLOCK'][0]), item.get('peripheral', ''), text(item.get('summary')),
                registers, functions, tuple(item.get('specs', []))))
        return found

    def _chains(self):
        found, availability = [], []
        for item in self._entities('chain'):
            steps, missing = [], set()
            rows = sorted(self.knowledge.steps[item['key']], key=lambda row: row['order'])
            for row in rows:
                props, refs = row['props'], self.knowledge.step_refs[row['props']['key']]
                required = [*refs['FROM'], *refs['TO'], *refs['THROUGH']]
                absent = [key for key in required if key not in self.by_meaning]
                missing.update(absent)
                if absent or not refs['FROM'] or not refs['TO']:
                    continue
                step = architecture_model.Step(
                    self.by_meaning[refs['FROM'][0]], self.by_meaning[refs['TO'][0]],
                    props['effect'], props['sign'],
                    tuple(self.by_meaning[key] for key in refs['THROUGH']),
                    text(props.get('note')), tuple(props.get('specs', [])),
                    'claim')
                members = (step.source, step.target, *step.via)
                if self._connected(members):
                    step.support = 'graph'
                elif self.rom == item.get('home', '7mfk'):
                    addresses = {self.nodes[key].addr for key in members}
                    if any(addresses <= self._spec_index(spec)
                           for spec in (*step.specs, *item.get('specs', []))):
                        step.support = 'specification'
                steps.append(step)
            outputs = self.knowledge.refs[item['key']]['OUTPUT']
            missing.update(key for key in outputs if key not in self.by_meaning)
            availability.append({'id': identifier(item['key']), 'name': item.get('title', ''),
                                 'home': item.get('home', '7mfk'), 'bound': len(steps),
                                 'total': len(rows), 'missing': [
                                     self.knowledge.binding(key, self.rom, self.image)
                                     for key in sorted(missing)]})
            # An incomplete calculation is reported as unavailable, never as a
            # complete chain assembled from a subset of its steps.
            if missing or len(steps) != len(rows) or len(outputs) != 1:
                continue
            found.append(architecture_model.Chain(
                identifier(item['key']), item.get('title', ''), text(item.get('summary')),
                item.get('quantity', ''), self.by_meaning[outputs[0]],
                tuple(item.get('specs', [])), steps))
        return found, availability

    def export(self):
        found = super().export()
        found.update({'id': self.view_key, 'layout': self.rom, 'image': self.image,
                      'fingerprint': self.knowledge.fingerprint,
                      'source': 'kb graph', 'chainAvailability': self.chain_availability,
                      'edgeEvidence': [{'from': edge.source, 'to': edge.target,
                                        'kind': edge.kind, 'origins': sorted(edge.origins)}
                                       for edge in self.edges.values()]})
        return found
