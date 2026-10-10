"""Exact provenance does not stand in for ECU semantics or execution evidence."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
import tomllib

from kb import source_bindings, store
from kb.model import SymbolKey


@pytest.fixture
def inventory(tmp_path):
    for path in source_bindings.PATHS:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text('## Data flow\n`FUN_00000200` uses `0xFFFF1000`.\n'
                               '## Boundary\n`FUN_00000200` has unresolved units.\n')
    roles = {path.as_posix(): {0xffff1000: ('ram', 'selected raw word')}
             for path in source_bindings.PATHS}
    with patch.object(source_bindings, 'ROLES', roles):
        yield tmp_path, source_bindings.records(tmp_path)


def test_only_typed_functions_and_declared_ram_roles_enter_the_inventory(inventory):
    root, records = inventory
    assert set(records) == {SymbolKey('jk78c', 'fn', 0x200), SymbolKey('jk78c', 'ram', 0xffff1000)}
    assert records[SymbolKey('jk78c', 'fn', 0x200)][0]['sections'] == ['Boundary', 'Data flow']
    assert all('level' not in record and 'evidence' not in record
               for values in records.values() for record in values)


def test_owned_source_binding_round_trip_has_no_inferred_level(inventory):
    _, records = inventory
    document = {'source': records[SymbolKey('jk78c', 'fn', 0x200)], 'symbol': [
        {'layout': 'jk78c', 'address': '00000200', 'name': 'active-otter',
         'evidence': [{'kind': 'l0', 'supports': 'identity', 'at': 'jk78c:00000200'}]}]}
    assert tomllib.loads(store.render('fn', document)) == document


def test_exact_full_source_and_anchor_coverage_gate(inventory):
    root, records = inventory
    meanings = [SimpleNamespace(tables={'source': values}, symbols={
        'jk78c': SimpleNamespace(key=key)}) for key, values in records.items()]
    subject = SimpleNamespace(root=root, meanings=meanings, functions={'jk78c': {0x200}},
                              config={'source_bindings': {'enabled': True}})
    assert source_bindings.check(subject) == []
    (root / source_bindings.PATHS[0]).write_text('## Data flow\n`FUN_00000200` uses `0xFFFF1000`.\n')
    assert source_bindings.check(subject)


def test_missing_selected_role_refuses(inventory):
    root, _ = inventory
    (root / source_bindings.PATHS[0]).write_text('`FUN_00000200`\n')
    with pytest.raises(Exception, match='lacks its source anchor'):
        source_bindings.records(root)


def test_explicit_comparison_anchors_keep_their_own_layouts(inventory):
    root, _ = inventory
    with (root / source_bindings.PATHS[0]).open('a') as output:
        output.write('The 1ND mapper `FUN_0004C4B8` and the 1ME3B mapper '
                     '`FUN_00050310` implement the same table.\n')
    records = source_bindings.records(root)
    assert SymbolKey('1nd', 'fn', 0x4c4b8) in records
    assert SymbolKey('1me3b', 'fn', 0x50310) in records
    assert SymbolKey('jk78c', 'fn', 0x4c4b8) not in records
