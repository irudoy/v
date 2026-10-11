"""Prepared wrapping observes current formatting and returns separate lists."""

import re
import tomllib
from unittest import mock

from kb import store

TEXT = ' '.join(['a current declaration with several words'] * 6)


def test_prepared_lines_are_separate_and_preserve_the_complete_value():
    first = store.string_lines(TEXT, 'value = ', '')
    expected = list(first)
    first[1] = 'changed returned line'
    second = store.string_lines(TEXT, 'value = ', '')
    assert second == expected and second is not first
    assert tomllib.loads('\n'.join(second)) == {'value': TEXT}


def test_width_changes_select_current_wrapping(monkeypatch):
    first = store.string_lines(TEXT, 'value = ', '')
    monkeypatch.setattr(store, 'WIDTH', 40)
    second = store.string_lines(TEXT, 'value = ', '')
    assert second != first
    assert tomllib.loads('\n'.join(second)) == {'value': TEXT}
    assert all(len(line) <= 40 for line in second[1:])


def test_current_escape_mapping_replaces_prepared_text(monkeypatch):
    text = TEXT + ' "quoted"'
    first = store.string_lines(text, 'value = ', '')
    monkeypatch.setitem(store.ESCAPES, '"', '\\u0022')
    second = store.string_lines(text, 'value = ', '')
    assert second != first
    assert tomllib.loads('\n'.join(second)) == {'value': text}


def test_changed_break_callback_executes_even_for_a_prepared_input():
    store.string_lines(TEXT, 'value = ', '')
    with mock.patch.object(store, '_breaks', return_value=False) as breaks:
        lines = store.string_lines(TEXT, 'value = ', '')
        assert breaks.called and len(lines) == 2
        assert tomllib.loads('\n'.join(lines)) == {'value': TEXT}


def test_changed_key_pattern_and_equal_distinct_keys_keep_current_behavior(monkeypatch):
    first = ''.join(['prepared', '_key'])
    second = ''.join(['prepared_', 'key'])
    assert first == second and first is not second
    assert store._key(first) is first and store._key(second) is second
    monkeypatch.setattr(store, 'BARE_KEY', re.compile(r'[a-z]+'))
    assert store._key(second) == '"prepared_key"'


def test_oversized_strings_leave_preparation_unchanged():
    store.string_lines(TEXT, 'value = ', '')
    before = store._string_program.cache_info()
    text = TEXT * 30
    lines = store.string_lines(text, 'value = ', '')
    assert tomllib.loads('\n'.join(lines)) == {'value': text}
    assert store._string_program.cache_info() == before
