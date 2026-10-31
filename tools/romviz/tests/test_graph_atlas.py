"""Actual per-layout bindings of graph-based architecture views."""

from copy import deepcopy

import pytest

from tools.romviz import graph_atlas, model


def fixture_rows():
    def symbol(meaning, layout, kind, address, **props):
        return {'meaning': meaning, 'props': {
            'key': f'{layout}-{address:08x}/{kind}', 'layout': layout,
            'kind': kind, 'address': address, 'name': meaning.split('/')[0], **props}}

    return {
        'fingerprint': 'fixture',
        'layouts': [{'key': '7mfk'}, {'key': 'jk00d'}],
        'images': [{'image': 'JK08A', 'layout': '7mfk'},
                   {'image': 'JK00A', 'layout': '7mfk'},
                   {'image': 'JK00D', 'layout': 'jk00d'}],
        'meanings': [
            {'key': 'producer/fn', 'name': 'producer', 'kind': 'fn', 'home': '7mfk',
             'title': 'Producer', 'level': 'code', 'block': 'engine_speed/block'},
            {'key': 'input/ram', 'name': 'input', 'kind': 'ram', 'home': '7mfk',
             'width': 16, 'summary': ['First statement.', 'Second statement.']},
            {'key': 'output/ram', 'name': 'output', 'kind': 'ram', 'home': '7mfk',
             'width': 16, 'former': ['old_speed']},
            {'key': 'alternative/ram', 'name': 'alternative', 'kind': 'ram'}],
        'symbols': [symbol('producer/fn', '7mfk', 'fn', 0x3000),
                    symbol('producer/fn', 'jk00d', 'fn', 0x4000),
                    symbol('input/ram', '7mfk', 'ram', 0xffff1000),
                    symbol('input/ram', 'jk00d', 'ram', 0xffff2000, width=32),
                    symbol('output/ram', '7mfk', 'ram', 0xffff1002),
                    symbol('alternative/ram', 'jk00d', 'ram', 0xffff2002)],
        'statuses': [{'meaning': 'output/ram', 'layout': 'jk00d',
                      'props': {'state': 'unresolved', 'count': 0}}],
        'analogs': [{'from': 'output/ram', 'to': 'alternative/ram',
                    'props': {'note': 'Separate mechanism.'}}],
        'entities': [{'key': 'estimation/stage', 'kind': 'stage', 'title': 'Estimation'},
                     {'key': 'engine_speed/block', 'kind': 'block', 'title': 'Engine speed'},
                     {'key': 'speed/chain', 'kind': 'chain', 'title': 'Speed', 'home': '7mfk'}],
        'entity_refs': [{'from': 'engine_speed/block', 'kind': 'STAGE', 'to': 'estimation/stage'},
                        {'from': 'speed/chain', 'kind': 'OUTPUT', 'to': 'output/ram'}],
        'steps': [{'chain': 'speed/chain', 'order': 1, 'props': {
            'key': 'speed#1', 'effect': 'converts', 'sign': 'negative', 'note': 'y = 100 / x'}}],
        'step_refs': [{'from': 'speed#1', 'kind': 'FROM', 'to': 'input/ram'},
                      {'from': 'speed#1', 'kind': 'TO', 'to': 'output/ram'},
                      {'from': 'speed#1', 'kind': 'THROUGH', 'order': 2, 'to': 'producer/fn'},
                      {'from': 'speed#1', 'kind': 'THROUGH', 'order': 1, 'to': 'producer/fn'}],
        'links': [{'from': '7mfk-ffff1002/ram', 'to': '7mfk-00003000/fn',
                   'kind': 'WRITER', 'props': {'verified': True}}],
    }


def test_foreign_layout_uses_only_its_actual_symbol_addresses():
    knowledge = graph_atlas.Knowledge(fixture_rows())
    home, foreign = knowledge.model('7mfk'), knowledge.model('jk00d')
    assert set(node.addr for node in home.nodes.values()) == {'00003000', 'ffff1000', 'ffff1002'}
    assert set(node.addr for node in foreign.nodes.values()) == {'00004000', 'ffff2000', 'ffff2002'}
    assert foreign.nodes['signal:ffff2000'].meta['shape']['width'] == 32
    assert foreign.nodes['signal:ffff2000'].meta['summaryLayout'] == '7mfk'
    assert foreign.nodes['function:00004000'].block == 'engine-speed'
    assert len(home.chains) == 1
    assert not foreign.chains
    unavailable = foreign.chain_availability[0]
    assert (unavailable['bound'], unavailable['total']) == (0, 1)
    assert unavailable['missing'][0]['meaning'] == 'output/ram'
    assert unavailable['missing'][0]['symbol'] is None
    assert unavailable['missing'][0]['statuses'][0]['state'] == 'unresolved'


def test_bindings_show_siblings_formers_and_analogs_without_joining_them():
    knowledge = graph_atlas.Knowledge(fixture_rows())
    binding = knowledge.binding('output/ram', '7mfk')
    assert binding['former'] == ['old_speed']
    assert binding['symbols'][0]['address'] == 'ffff1002'
    assert binding['analogs'] == [{'to': 'alternative/ram', 'name': 'alternative',
                                  'note': 'Separate mechanism.'}]
    assert knowledge.binding('alternative/ram', 'jk00d')['analogs'][0]['to'] == 'output/ram'
    assert 'alternative/ram' not in knowledge.model('7mfk').by_meaning


def test_steps_keep_repeated_call_order_and_layouts_share_one_snapshot():
    knowledge = graph_atlas.Knowledge(fixture_rows())
    home = knowledge.model('7mfk')
    assert knowledge.model('7mfk') is home
    assert home.chains[0].steps[0].via == ('function:00003000', 'function:00003000')
    assert home.export()['fingerprint'] == 'fixture'


def test_missing_intermediate_step_does_not_create_a_partial_chain():
    rows = deepcopy(fixture_rows())
    rows['symbols'] = [item for item in rows['symbols']
                       if item['meaning'] != 'producer/fn' or item['props']['layout'] != '7mfk']
    home = graph_atlas.Knowledge(rows).model('7mfk')
    assert not home.chains
    assert home.chain_availability[0]['missing'][0]['meaning'] == 'producer/fn'


def test_l0_accesses_join_actual_symbols_and_distinguish_a_parameter_from_a_load():
    rows = fixture_rows()
    rows['accesses'] = [
        {'source': '7mfk-00003000/fn', 'target': '7mfk-ffff1000/ram',
         'modes': ['param'], 'producer': 'l0'},
        {'source': '7mfk-00003000/fn', 'target': '7mfk-ffff1002/ram',
         'modes': ['store', 'load'], 'producer': 'derived'},
        {'source': 'jk00d-00004000/fn', 'target': '7mfk-ffff1002/ram',
         'modes': ['store'], 'producer': 'l0'},
    ]
    knowledge = graph_atlas.Knowledge(rows)
    home = knowledge.model('7mfk')
    assert home.chains[0].steps[0].support == 'graph'
    reference = home.edges[('signal:ffff1000', 'function:00003000', 'access')]
    assert reference.roles == {'references'} and reference.origins == {'L0 export'}
    write = home.edges[('function:00003000', 'signal:ffff1002', 'data')]
    assert 'L0 derived' in write.origins
    assert ('signal:ffff1002', 'function:00003000', 'data') in home.edges
    assert knowledge.model('jk00d').edges == {}


def test_image_restriction_filters_nodes_relations_endpoints_and_complete_chains():
    rows = fixture_rows()
    rows['symbols'][0]['props']['images'] = ['JK08A']
    rows['entities'].append({'key': 'sensor/endpoint', 'kind': 'endpoint', 'title': 'Sensor'})
    rows['entity_refs'].extend([
        {'from': 'sensor/endpoint', 'kind': 'BLOCK', 'to': 'engine_speed/block'},
        {'from': 'sensor/endpoint', 'kind': 'FUNCTION', 'to': 'producer/fn'}])
    rows['accesses'] = [{'source': '7mfk-00003000/fn', 'target': '7mfk-ffff1000/ram',
                        'modes': ['load'], 'producer': 'l0'}]
    knowledge = graph_atlas.Knowledge(rows)
    included = knowledge.model('7mfk', 'JK08A')
    excluded = knowledge.model('7mfk', 'JK00A')
    assert len(included.chains) == len(included.endpoints) == 1
    assert included.edges
    assert not excluded.chains and not excluded.endpoints and not excluded.edges
    assert set(excluded.by_meaning) == {'input/ram', 'output/ram'}
    missing = excluded.chain_availability[0]['missing']
    assert len(missing) == 1 and missing[0]['meaning'] == 'producer/fn'
    assert missing[0]['symbol'] is None and missing[0]['reference'] is None
    assert missing[0]['availability'] == 'image-excluded'
    assert missing[0]['image'] == 'JK00A' and missing[0]['images'] == ['JK08A']
    assert missing[0]['symbols'][0]['images'] == ['JK08A']
    assert included is knowledge.model('7mfk', 'JK08A')
    assert excluded is knowledge.model('7mfk', 'JK00A') and excluded is not included
    assert included.export()['image'] == 'JK08A'
    assert excluded.export()['image'] == 'JK00A'
    foreign = knowledge.binding('output/ram', 'jk00d', 'JK00D')
    assert foreign['availability'] == 'missing'
    assert foreign['former'] == ['old_speed']
    assert foreign['statuses'][0]['state'] == 'unresolved'
    assert foreign['analogs'][0]['to'] == 'alternative/ram'


@pytest.mark.parametrize('image', ['JK00D', 'unknown'])
def test_image_model_refuses_wrong_or_unregistered_layout_membership(image):
    knowledge = graph_atlas.Knowledge(fixture_rows())
    with pytest.raises(ValueError, match='belongs to .*not to 7mfk'):
        knowledge.model('7mfk', image)
    assert not knowledge.models


def annotation_rows():
    """A layout without ledgers: KB functions, tables and axes beside definition objects."""
    rows = deepcopy(fixture_rows())

    def symbol(meaning, kind, address, **props):
        return {'meaning': meaning, 'props': {
            'key': f'jk00d-{address:08x}/{kind}', 'layout': 'jk00d', 'kind': kind,
            'address': address, 'name': meaning.split('/')[0], **props}}

    rows['images'].append({'image': 'JK00E', 'layout': 'jk00d'})
    rows['meanings'].extend([
        {'key': 'excluded/fn', 'name': 'excluded', 'kind': 'fn', 'home': 'jk00d'},
        {'key': 'curve/tbl', 'name': 'curve', 'kind': 'tbl', 'home': '7mfk', 'level': 'code',
         'role': 'table', 'cols': 8, 'storage': 'uint8', 'editor': {'emit': False},
         'summary': 'Curve read on the home layout.'},
        {'key': 'census_only/tbl', 'name': 'census_only', 'kind': 'tbl', 'home': 'jk00d'},
        {'key': 'published/tbl', 'name': 'published', 'kind': 'tbl', 'home': 'jk00d',
         'cols': 4, 'rows': 2, 'storage': 'uint16', 'editor': {'name': 'Published'}},
        {'key': 'declared/tbl', 'name': 'declared', 'kind': 'tbl', 'home': 'jk00d',
         'cols': 2, 'storage': 'uint8', 'editor': {'name': 'Declared'}},
        {'key': 'bare/tbl', 'name': 'bare', 'kind': 'tbl', 'home': 'jk00d'},
        {'key': 'grouped/tbl', 'name': 'grouped', 'kind': 'tbl', 'home': 'jk00d',
         'cols': 8, 'rows': 2, 'storage': 'uint16'},
        {'key': 'curve_axis/axis', 'name': 'curve_axis', 'kind': 'axis', 'home': 'jk00d',
         'points': 8, 'storage': 'uint8'},
        {'key': 'published_axis/axis', 'name': 'published_axis', 'kind': 'axis',
         'home': 'jk00d', 'points': 4, 'storage': 'uint16'}])
    rows['symbols'].extend([
        symbol('excluded/fn', 'fn', 0x4100, images=['JK00E']),
        symbol('curve/tbl', 'tbl', 0x5000, note='Target note.'),
        symbol('census_only/tbl', 'tbl', 0x5100),
        symbol('published/tbl', 'tbl', 0x5200),
        symbol('declared/tbl', 'tbl', 0x5300),
        symbol('bare/tbl', 'tbl', 0x5400),
        symbol('grouped/tbl', 'tbl', 0x5800),
        symbol('curve_axis/axis', 'axis', 0x5500),
        symbol('published_axis/axis', 'axis', 0x5600)])
    rows['links'].append({'from': 'jk00d-00005000/tbl', 'to': 'jk00d-00005500/axis',
                          'kind': 'AXIS', 'props': {}})
    rows['census_maps'] = [
        {'image': 'JK00D', 'address': '00005000', 'width': 8, 'height': None, 'storage': 'uint8'},
        {'image': 'JK00D', 'address': '00005100', 'width': 8, 'height': None, 'storage': 'uint16'},
        {'image': 'JK00D', 'address': '00005800', 'width': 8, 'height': None, 'storage': 'uint16'},
        {'image': 'JK00D', 'address': '00005810', 'width': 8, 'height': None, 'storage': 'uint16'}]
    rows['census_axes'] = [{'image': 'JK00D', 'address': '00005600', 'count': 4,
                            'storage': 'uint16'}]
    rows['census_axis_uses'] = [{'image': 'JK00D', 'map': '00005100', 'address': '00005600'}]
    return rows


def definition_objects():
    return [{'id': 'definition-map:0:00005200', 'kind': 'definition-map', 'layer': 'maps',
             'start': 0x5200, 'end': 0x5210},
            {'id': 'definition-axis:00005600', 'kind': 'definition-axis', 'layer': 'axes',
             'start': 0x5600, 'end': 0x5608}]


def meta(item):
    return {entry['label']: entry['value'] for entry in item['meta']}


def test_kb_tables_and_axes_fill_the_address_map_without_duplicating_definitions():
    knowledge = graph_atlas.Knowledge(annotation_rows())
    annotations = knowledge.address_annotations('jk00d', 'JK00D')
    found, conflicts = model._kb_calibration_objects(
        annotations, definition_objects(), knowledge, 'JK00D', 'jk00d', 0x10000)
    by_id = {item['id']: item for item in found}

    assert conflicts == []
    assert set(by_id) == {'kb-map:00005000', 'kb-map:00005100', 'kb-map:00005300',
                          'kb-map:00005400', 'kb-map:00005800', 'kb-axis:00005500'}
    curve = by_id['kb-map:00005000']
    assert (curve['label'], curve['layer'], curve['kind']) == ('curve', 'maps', 'kb-map')
    assert (curve['end'] - curve['start'], curve['exactExtent']) == (8, True)
    assert {'hidden', 'kb', 'map'} <= set(curve['tags'])
    assert curve['description'] == 'Curve read on the home layout.'
    assert curve['note'] == 'Target note.'
    assert meta(curve)['Editor'] == 'emit = false'
    assert meta(curve)['Geometry'] == 'kb meaning'
    assert meta(curve)['Summary layout'] == '7mfk'
    assert 'Note layout' not in meta(curve)
    assert meta(curve)['Symbol'] == 'curve/tbl/jk00d-00005000'
    assert curve['related'] == [{'label': 'Axis 0x005500', 'address': 0x5500}]
    census = by_id['kb-map:00005100']
    assert (census['end'] - census['start'], meta(census)['Geometry']) == (16, 'census')
    assert meta(census)['Editor'] == 'no editor declaration'
    assert census['related'] == [{'label': 'Axis 0x005600', 'address': 0x5600}]
    assert meta(by_id['kb-map:00005300'])['Editor'] == 'declared, not published for JK00D'
    bare = by_id['kb-map:00005400']
    assert (bare['end'] - bare['start'], bare['exactExtent']) == (1, False)
    assert meta(bare)['Geometry'] == 'unknown'
    # Two adjacent census curves of one width tile the grouped 8x2 table.
    assert by_id['kb-map:00005800']['end'] - 0x5800 == 32
    axis = by_id['kb-axis:00005500']
    assert (axis['layer'], axis['end'] - axis['start']) == ('axes', 8)
    assert axis['related'] == [{'label': 'Map 0x005000', 'address': 0x5000}]


def test_published_objects_receive_the_kb_binding_and_keep_their_geometry():
    knowledge = graph_atlas.Knowledge(annotation_rows())
    objects = definition_objects()
    model._bind_objects(objects, {'layout': 'jk00d', 'image': 'JK00D'}, knowledge)
    assert [item['binding']['reference'] for item in objects] == [
        'published/tbl/jk00d-00005200', 'published_axis/axis/jk00d-00005600']
    assert [(item['start'], item['end']) for item in objects] == [
        (0x5200, 0x5210), (0x5600, 0x5608)]


def row(rows, group, field, value):
    return next(item for item in rows[group] if item[field] == value)


@pytest.mark.parametrize(('change', 'reported'), [
    (lambda rows: row(rows, 'meanings', 'key', 'published/tbl').update(rows=4),
     'published/tbl'),
    (lambda rows: row(rows, 'census_maps', 'address', '00005000').update(width=4),
     'curve/tbl'),
    (lambda rows: row(rows, 'census_maps', 'address', '00005810').update(storage='uint8'),
     'grouped/tbl'),
])
def test_geometry_conflicts_are_reported(change, reported):
    rows = annotation_rows()
    change(rows)
    knowledge = graph_atlas.Knowledge(rows)
    _found, conflicts = model._kb_calibration_objects(
        knowledge.address_annotations('jk00d', 'JK00D'), definition_objects(), knowledge,
        'JK00D', 'jk00d', 0x10000)
    assert len(conflicts) == 1 and conflicts[0].startswith(f'{reported}/jk00d-')


def test_kb_functions_become_reviewed_objects_for_their_images(tmp_path, monkeypatch):
    (tmp_path / 'funcs.csv').write_text(
        'addr,size,is_external,is_thunk\n00004000,64,false,false\n00004100,32,false,false\n',
        encoding='utf-8')
    monkeypatch.setattr(model.rom_sources, 'l0_dir', lambda rom: tmp_path)
    monkeypatch.setattr(model.rom_sources, 'function_names', lambda rom: {})
    knowledge = graph_atlas.Knowledge(annotation_rows())
    manifest = {'rom': 'JK00D'}
    for image, kb_entries in (('JK00D', {0x4000}), ('JK00E', {0x4000, 0x4100})):
        warnings = []
        objects = model._function_objects(
            manifest, 0x10000, warnings, knowledge.address_annotations('jk00d', image), 'jk00d')
        reviewed = {item['start'] for item in objects if item['reviewed']}
        assert reviewed == kb_entries
        assert warnings == []
    producer = objects[0]
    assert (producer['kind'], producer['label']) == ('reviewed-function', 'producer')
    assert producer['confidence'] == 'code'
    assert 'kb' in producer['tags']
    assert meta(producer)['Meaning'] == 'producer/fn'
    assert meta(producer)['Block'] == 'engine_speed/block'
    assert producer['source'].endswith('funcs.csv:2')
    excluded = model._function_objects(
        manifest, 0x10000, [], knowledge.address_annotations('jk00d', 'JK00D'), 'jk00d')[1]
    assert (excluded['kind'], excluded['label']) == ('function-structure', 'FUN_00004100')


class AnnotationSpy:
    def __init__(self):
        self.calls = []

    def address_annotations(self, layout, image):
        self.calls.append((layout, image))
        return []


def test_ledger_manifests_never_request_kb_annotations():
    spy = AnnotationSpy()
    architecture = {'layout': '7mfk', 'image': 'JK08A'}
    for fields in ({'reviewed_functions': 'f'}, {'map_ledger': 'm'},
                   {'reviewed_functions': 'f', 'map_ledger': 'm'}):
        assert model._kb_annotations({'rom': 'JK08A', **fields}, spy, architecture) is None
    assert spy.calls == []
    assert model._kb_annotations({'rom': 'JK78C'}, spy, {'layout': 'jk78c'}) == []
    assert spy.calls == [('jk78c', 'JK78C')]


@pytest.mark.parametrize('images', [None, [], ['JK08A'], ['JK08A', 'JK00A']])
def test_semantic_object_binding_respects_image_scope_and_preserves_geometry(images):
    rows = fixture_rows()
    if images is not None:
        rows['symbols'][0]['props']['images'] = images
    knowledge = graph_atlas.Knowledge(rows)
    original = {'id': 'function:00003000', 'kind': 'reviewed-function',
                'start': 0x3000, 'end': 0x3100, 'layer': 'functions', 'label': 'Producer'}
    for image in ('JK08A', 'JK00A'):
        item = deepcopy(original)
        architecture = {'layout': '7mfk', 'image': image}
        model._bind_objects([item], architecture, knowledge)
        expected = not images or image in images
        assert ('binding' in item) == expected
        assert {key: value for key, value in item.items() if key != 'binding'} == original
        if expected:
            assert item['binding']['availability'] == 'bound'
            assert item['binding']['image'] == image
            assert item['binding']['reference'] == 'producer/fn/7mfk-00003000'
