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
