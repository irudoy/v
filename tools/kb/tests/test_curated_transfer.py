"""Fixed contracts for exact owned curated-name projections."""

from types import SimpleNamespace
import tomllib

import pytest

from kb import store
from kb.adapters import curated
from kb.model import SymbolKey
from kb.repo import KbError
from tools import rom_sources


def symbol(address, selector, *, name='owned_name', aliases=(), props=None):
    meaning = SimpleNamespace(name=name, other_names=[(alias, 'former', 'owner')
                                                     for alias in aliases],
                              props=props or {})
    return SimpleNamespace(layout='1nd', address=address, kind='fn',
                           key=SymbolKey('1nd', 'fn', address), meaning=meaning,
                           props={'curated': selector})


def render(*symbols):
    model = SimpleNamespace(symbols={item.key: item for item in symbols})
    return curated.render(model)['tools/ghidra/symbols/1nd.csv']


def test_csv_keeps_original_order_alias_and_selected_prose():
    first = symbol(0x200, {'order': 0, 'name': 'old_name', 'notes': [1]},
                   aliases=('old_name',), props={'note': ['Retained context.', 'Original prose.']})
    second = symbol(0x100, {'order': 1, 'title': True}, props={'title': 'Original title.'})
    assert render(second, first) == (curated.HEADERS['1nd'] + 'addr,name,note\n'
                                    '00000200,old_name,Original prose.\n'
                                    '00000100,owned_name,Original title.\n')


@pytest.mark.parametrize('selector', [
    {'order': True}, {'order': 1}, {'order': 0, 'name': 'unowned_name'},
    {'order': 0, 'notes': [0]}, {'order': 0, 'title': True},
    {'order': 0, 'title': 'true'},
])
def test_invalid_or_incomplete_selectors_refuse(selector):
    with pytest.raises(KbError):
        render(symbol(0x100, selector))


def test_duplicate_rows_refuse_even_for_distinct_symbols():
    with pytest.raises(KbError):
        render(symbol(0x100, {'order': 0}), symbol(0x200, {'order': 0}))


@pytest.mark.parametrize('note', ['On 1ND, the state is copied.', 'A "quoted" note.',
                                  'First line\nsecond line', 'First line\rsecond line'])
@pytest.mark.parametrize('source', ['note', 'title'])
def test_selected_prose_that_requires_csv_quoting_refuses_before_projection(note, source):
    selector = {'order': 0, 'notes': [0]} if source == 'note' else {'order': 0, 'title': True}
    props = {'note': [note]} if source == 'note' else {'title': note}
    with pytest.raises(KbError, match='curated note must be a single line') as caught:
        render(symbol(0x100, selector, props=props))
    assert caught.value.code == 3
    assert '1nd-00000100/fn' in str(caught.value)


def test_projected_native_note_is_readable_by_both_curated_consumers(tmp_path, monkeypatch):
    note = "The sample's high byte selects the table; its units remain unresolved."
    text = render(symbol(0x100, {'order': 0, 'notes': [0]}, props={'note': [note]}))
    functions = tmp_path / 'l0/1nd/funcs.csv'
    functions.parent.mkdir(parents=True)
    functions.write_text('addr,size,is_thunk,is_external\n00000100,2,false,false\n')
    projection = tmp_path / 'tools/ghidra/symbols/1nd.csv'
    projection.parent.mkdir(parents=True)
    projection.write_text(text)
    monkeypatch.setattr(rom_sources, 'layout_of', lambda rom, root: '1nd')
    assert rom_sources.function_names('T1', tmp_path) == {'00000100': 'owned_name'}
    assert curated.rows(tmp_path, '1nd') == [
        {'addr': '00000100', 'name': 'owned_name', 'note': note},
    ]


def test_native_selector_round_trip_keeps_evidence_and_uncertainty():
    document = {'level': 'candidate', 'symbol': [
        {'layout': '1nd', 'address': '00000100', 'curated': {'order': 0, 'notes': [0]},
         'evidence': [{'kind': 'l0', 'at': '1nd:00000100', 'supports': 'identity'}]}],
        'note': ['Original source prose, with its context.']}
    assert tomllib.loads(store.render('fn', document)) == document
