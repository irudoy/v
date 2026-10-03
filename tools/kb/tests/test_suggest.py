from unittest.mock import Mock

import pytest

from kb import l0graph, suggest
from kb.repo import KbError


def test_shared_ram_counts_distinct_locations_and_excludes_rom_io_and_missing_functions():
    functions = [{'key': key} for key in ('f1', 'f2', 'f3')]
    locations = [{'key': key, 'space': space} for key, space in (
        ('r1', 'ram'), ('r2', 'ram'), ('rom', 'rom'), ('reg', 'io'), ('pointer', 'ram'))]
    accesses = [{'from': func, 'to': loc, 'props': {'modes': ['load']}} for func, loc in (
        ('f1', 'r1'), ('f1', 'r1'), ('f2', 'r1'), ('f3', 'r1'), ('absent', 'r1'),
        ('f1', 'r2'), ('f2', 'r2'), ('f1', 'rom'), ('f2', 'rom'),
        ('f1', 'reg'), ('f2', 'reg'))]
    accesses.extend({'from': func, 'to': 'pointer', 'props': {'modes': ['literal']}}
                    for func in ('f1', 'f2'))
    rows = l0graph.shared_ram(functions, locations, accesses)
    assert {(row['from'], row['to']): row['props']['weight'] for row in rows} == {
        ('f1', 'f2'): 2, ('f1', 'f3'): 1, ('f2', 'f3'): 1}
    assert all(row['props']['producer'] == 'derived' for row in rows)


def test_a_unique_dominant_block_guides_unplaced_members_without_changing_them():
    rows = [{'community': 4, 'address': address, 'block': block} for address, block in (
        (0x10, None), (0x20, 'fuel/block'), (0x30, 'fuel/block'), (0x40, 'air/block'))]
    [found] = suggest.communities(rows)
    assert found['blocks'] == ['fuel/block']
    assert found['votes'] == {'air/block': 1, 'fuel/block': 2}
    assert found['placed'] == 3
    assert found['functions'] == [rows[0]]
    assert rows[0]['block'] is None


def test_a_tie_retains_both_alternatives_and_an_unplaced_community_proposes_a_new_block():
    rows = [{'community': group, 'address': address, 'block': block}
            for group, address, block in (
                (1, 0x50, None), (1, 0x60, 'b/block'), (1, 0x70, 'a/block'),
                (2, 0x20, None), (3, 0x10, 'placed/block'))]
    first, second = suggest.communities(rows)
    assert first['new_block'] and first['blocks'] == []
    assert second['blocks'] == ['a/block', 'b/block'] and not second['new_block']


@pytest.mark.parametrize('available', [[], [{'name': suggest.PROCEDURE, 'is_write': True}]])
def test_missing_or_writing_mage_procedures_are_refused_without_another_algorithm(available):
    graph = Mock()
    graph.run.return_value = available
    with pytest.raises(KbError) as error:
        suggest.blocks(graph, '7mfk')
    assert error.value.code == 6
    assert graph.run.call_count == 1


def test_suggestions_are_read_only_and_layout_scoped():
    assert 'Function {layout: $layout}' in suggest.QUERY
    assert 'CALL|SHARED_RAM' in suggest.QUERY
    assert 'leiden_community_detection.get_subgraph' in suggest.QUERY
    assert 'SET ' not in suggest.QUERY and 'CREATE ' not in suggest.QUERY
