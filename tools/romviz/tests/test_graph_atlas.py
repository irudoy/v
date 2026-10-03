"""Actual per-layout bindings of graph-based architecture views."""

from copy import deepcopy

import pytest

from tools.romviz import graph_atlas


def fixture_rows():
    def symbol(meaning, layout, kind, address, **props):
        return {'meaning': meaning, 'props': {
            'key': f'{layout}-{address:08x}/{kind}', 'layout': layout,
            'kind': kind, 'address': address, 'name': meaning.split('/')[0], **props}}

    return {
        'fingerprint': 'fixture',
        'layouts': [{'key': '7mfk'}, {'key': 'jk00d'}],
        'images': [{'image': 'JK08A', 'layout': '7mfk'},
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
