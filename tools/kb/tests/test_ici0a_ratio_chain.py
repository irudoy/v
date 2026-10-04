"""Bind the bounded ICI0A ratio metadata to the existing exact-stock proof."""

import re

from kb import compile, derive, repo
from kb.arithmetic import Grammar
from kb.model import SymbolKey
from tools.mapkit.tests import test_ici0a_ratio_path as stock


FORMULA = (
    'P = uint16(prev); D = uint16(x); Z = min(1,D); '
    'G = (uint8(ffff8505)>>7)&1; C = uint8(ffff196c); '
    'R = (1-Z)*255+Z*min(255,floor(64*P/max(1,D))); '
    'ffff196c = G*R+(1-G)*C'
)
OWNER_TEST = ('tools/kb/tests/test_ici0a_ratio_chain.py',
              'test_ici0a_ratio_chain_owner_contract')
STOCK_TESTS = {(stock.THIS_TEST, stock.IDENTITY_TEST),
               (stock.THIS_TEST, stock.CONTRACT_TEST)}
HANDLER = SymbolKey('7mfk', 'fn', stock.ENTRY)
DIVIDER = SymbolKey('7mfk', 'fn', stock.DIVIDER)


def _link(owner, kind, target, slot=None):
    [link] = [link for link in owner.links
              if link.type == kind and link.to.key == target and link.slot == slot]
    return link


def _proof(link, via):
    assert link.stated == {'7mfk'}
    assert link.props['via'] == via
    named = {(item.get('path'), item.get('key')) for item in link.evidence
             if item['kind'] == 'test'}
    assert STOCK_TESTS | {OWNER_TEST} <= named


def test_ici0a_ratio_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'ici0a_ratio_cell')]
    [step] = chain.steps
    cell_key = SymbolKey('7mfk', 'ram', stock.CELL)
    assert chain.refs['output'] == [cell_key]
    assert chain.props['specs'] == [stock.SPEC]
    assert step['from'] == HANDLER and step['to'] == cell_key
    assert step['effect'] == 'stores' and step['sign'] == 'none'
    assert step['via'] == [DIVIDER]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    assert Grammar(repo.config()).validate(step['note']) is None
    summary = ' '.join(chain.props['summary'].split())
    for phrase in ('writer entry 0002909a', 'prev denotes independent incoming R12',
                   'x denotes independent incoming R13', 'before skip-tail arming'):
        assert phrase in summary

    cell = model.meaning_of(cell_key)
    assert cell.key == 'thundering-bonobo/ram'
    assert not [link for link in cell.links if link.type == 'input']
    assert {(link.to.key, link.slot) for link in cell.links if link.type == 'selector'} == {
        ('ici0a_ratio_gate/ram', 'bit7'), ('pompous-firefly/fn', None)}
    for kind in ('writer', 'reader'):
        [link] = [link for link in cell.links if link.type == kind]
        assert link.to.key == 'pastel-yak/fn' and link.stated == {'7mfk'}
    base = _link(cell, 'base', 'outstanding-marmot/ram')
    assert base.to.symbols['7mfk'].address + base.offset == stock.CELL
    assert base.offset == 0x6e0
    _proof(base, [HANDLER])
    _proof(_link(cell, 'selector', 'ici0a_ratio_gate/ram', 'bit7'), [HANDLER])
    _proof(_link(cell, 'selector', 'pompous-firefly/fn'), [HANDLER, DIVIDER])
    _proof(_link(cell, 'threshold', 'ici0a_ratio_threshold/tbl'), [HANDLER])
    stock.assert_ici0a_ratio_specification((repo.ROOT / stock.SPEC).read_text())


def test_ici0a_ratio_numeric_owner_contract():
    model = compile.cached(repo.ROOT)
    for address, name in ((stock.CELL, 'thundering-bonobo/ram'),
                          (stock.GATE, 'ici0a_ratio_gate/ram')):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.meaning.key == name
        assert symbol.value('width') == 8 and symbol.value('signed') is False
        assert symbol.value('level') == 'code'
        assert symbol.meaning.props['block'] == 'crank_cam/block'
    cell = model.meaning_of(SymbolKey('7mfk', 'ram', stock.CELL))
    writer = _link(cell, 'writer', 'pastel-yak/fn').props['note']
    for phrase in ('0002909a-000290ce/0002911c', 'incoming R12 and R13',
                   'aliases prev and x', 'EXTU.W'):
        assert phrase in writer
    gate = model.meaning_of(SymbolKey('7mfk', 'ram', stock.GATE))
    gate_writer = _link(gate, 'writer', 'pastel-yak/fn')
    gate_reader = _link(gate, 'reader', 'pastel-yak/fn')
    _proof(gate_writer, [HANDLER])
    _proof(gate_reader, [HANDLER])
    for phrase in ('sampled gate bit 7 is clear', 'R4 >= 2', '0002911a', 'mode byte'):
        assert phrase in gate_writer.props['note']
    selector = _link(cell, 'selector', 'ici0a_ratio_gate/ram', 'bit7').props['note']
    for phrase in ('original sampled bit', 'not the final armed byte'):
        assert phrase in selector
    divider = _link(cell, 'selector', 'pompous-firefly/fn').props['note']
    for phrase in ('nonzero incoming uint16(R13)', 'Zero incoming uint16(R13) bypasses',
                   'third SHLL2 delay slot'):
        assert phrase in divider


def test_ici0a_ratio_reader_owner_contract():
    model = compile.cached(repo.ROOT)
    threshold = model.symbols[SymbolKey('7mfk', 'tbl', stock.THRESHOLD_ADDRESS)]
    assert threshold.meaning.key == 'ici0a_ratio_threshold/tbl'
    assert threshold.value('access') == 'direct-scalar'
    assert threshold.value('storage') == 'uint8'
    assert (threshold.value('cols'), threshold.value('rows')) == (1, 1)
    assert threshold.value('role') == 'threshold' and threshold.value('level') == 'code'
    assert threshold.meaning.props['block'] == 'crank_cam/block'
    assert stock.THRESHOLD == 118
    assert derive.image_bytes(repo.layout('7mfk'))[threshold.address] == stock.THRESHOLD
    reader = _link(threshold.meaning, 'reader', 'pastel-yak/fn')
    _proof(reader, [HANDLER])
    for phrase in ('ROM8[00008c89]', 'independent incoming R0.bit7 is set'):
        assert phrase in reader.props['note']
    cell = model.meaning_of(SymbolKey('7mfk', 'ram', stock.CELL))
    comparison = _link(cell, 'threshold', threshold.meaning.key)
    _proof(comparison, [HANDLER])
    for phrase in ('independent incoming reader R0.bit7 clear',
                   'cell > threshold', 'Equality is false', stock.SPEC):
        assert phrase in comparison.props['note']
    cell_reader = _link(cell, 'reader', 'pastel-yak/fn').props['note']
    for phrase in ('00029272-00029286/000292ec', 'independent incoming R0 status',
                   'no RAM stores'):
        assert phrase in cell_reader
