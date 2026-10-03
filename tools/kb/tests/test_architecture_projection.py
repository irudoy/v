"""Conservation of the architecture view, including kind and ordered steps."""

from types import SimpleNamespace
import tomllib

import pytest

from kb import architecture_projection as projection, compile, repo
from kb.adapters import architecture
from kb.model import Symbol, SymbolKey
from kb.repo import KbError
from tools.romviz import architecture as romviz


@pytest.fixture(scope='module')
def tracked():
    return compile.cached()


def source():
    return (repo.ROOT / architecture.ARCHITECTURE).read_text(encoding='utf-8')


def test_every_architecture_fact_and_step_survives_projection(tracked):
    rendered = projection.render(projection.document(tracked))
    projection.validate_conversion(source(), rendered, tracked)
    original, generated = (projection.comparable(tomllib.loads(text), tracked)
                           for text in (source(), rendered))
    assert generated == original
    assert sum(len(chain['step']) for chain in generated['chain']) == 387


def test_the_architecture_gate_reproduces_placements_and_flows(tmp_path, tracked):
    current = romviz.load()
    projected = tmp_path / 'JK08A.architecture.toml'
    projected.write_text(projection.render(projection.document(tracked)))
    generated = romviz.load(projected)
    assert [(block.id, block.functions, block.maps, block.signals)
            for block in generated.blocks] == [
                (block.id, tuple(sorted(block.functions)), tuple(sorted(block.maps)),
                 tuple(sorted(block.signals))) for block in current.blocks]
    assert {key: node.block for key, node in generated.nodes.items()} == {
        key: node.block for key, node in current.nodes.items()}
    assert generated.flows == current.flows
    assert len(generated.edges) == len(current.edges)
    assert [(chain.id, [(step.source, step.target, step.note, step.support)
                        for step in chain.steps]) for chain in generated.chains] == [
        (chain.id, [(step.source, step.target, step.note, step.support)
                   for step in chain.steps]) for chain in current.chains]


@pytest.mark.parametrize('change', ['arithmetic', 'order', 'kind', 'via'])
def test_a_fact_change_refuses_the_projection(tracked, change):
    document = projection.document(tracked)
    steps = next(chain['step'] for chain in document['chain'] if chain['id'] == 'engine-speed')
    if change == 'arithmetic':
        steps[0]['note'] = 'output = input * 99'
    elif change == 'order':
        steps[0], steps[1] = steps[1], steps[0]
    elif change == 'kind':
        steps[0]['to'] = 'function:' + steps[0]['to'].split(':')[-1]
    else:
        steps[0]['via'] = ['0003deec']
    with pytest.raises(KbError):
        projection.validate_conversion(source(), projection.render(document), tracked)


def test_a_kind_prefix_preserves_two_objects_at_one_address():
    symbols = {SymbolKey('7mfk', kind, 0x10000): Symbol(SymbolKey('7mfk', kind, 0x10000))
               for kind in ('tbl', 'axis')}
    model = SimpleNamespace(symbols=symbols)
    assert projection.address(model, SymbolKey('7mfk', 'tbl', 0x10000)) == '00010000'
    assert projection.address(model, SymbolKey('7mfk', 'axis', 0x10000)) == 'axis:00010000'


def test_a_symbol_of_another_layout_cannot_supply_the_home_address():
    key = SymbolKey('jk78c', 'ram', 0xFFFF1000)
    with pytest.raises(KbError, match='has no 7mfk symbol'):
        projection.address(SimpleNamespace(symbols={key: Symbol(key)}), key)


def test_empty_block_lists_remain_explicit():
    document = {'schema_version': 1, 'rom': 'JK08A', 'summary': projection.SUMMARY,
                'sources': projection.SOURCES, 'stage': [],
                'block': [{'id': 'probe', 'name': 'Probe', 'stage': 'control',
                           'summary': 'Probe.', 'functions': [], 'maps': [], 'signals': []}],
                'endpoint': [], 'chain': []}
    parsed = tomllib.loads(projection.render(document))
    assert parsed['block'][0]['functions'] == []
