"""Scoped parser requests share only exact immutable retained contents."""

import tomllib
from unittest import mock

from kb import adapters
from tools.kb.tests.source_parse_cache import SourceParseCache


def test_first_parse_in_each_root_and_order_keeps_shared_storage(tmp_path):
    cache = SourceParseCache()
    text = '[[item]]\nvalues = [1, 2]\n'
    scopes = [(tmp_path / 'first', tuple(adapters.ADAPTERS)),
              (tmp_path / 'second', tuple(adapters.ADAPTERS)),
              (tmp_path / 'first', tuple(reversed(adapters.ADAPTERS)))]
    original = tomllib.loads
    with mock.patch.object(tomllib, 'loads', wraps=original) as parsed:
        for root, order in scopes:
            with cache.scope(root, order):
                first = cache.loads(text)
                first['item'][0]['values'].append(3)
                assert cache.loads(text) == {'item': [{'values': [1, 2]}]}
        assert parsed.call_count == len(scopes)
    assert len(cache.sources) == 1 and len(cache.entries) == len(scopes)
    source = next(iter(cache.sources.values()))
    assert source.owners == len(scopes)
    assert all(entry is source for entry in cache.entries.values())
    assert cache.bytes == source.size + len(scopes) * cache.REFERENCE_BYTES


def test_identical_text_with_different_parsed_values_keeps_separate_storage(tmp_path):
    cache = SourceParseCache()
    text = 'value = 1\n'
    for name, value in [('first', 1), ('second', 2)]:
        with mock.patch.object(tomllib, 'loads', return_value={'value': value}) as parsed, \
                cache.scope(tmp_path / name, adapters.ADAPTERS):
            assert cache.loads(text) == {'value': value}
            assert cache.loads(text) == {'value': value}
            assert parsed.call_count == 1
    assert len(cache.sources) == 2
    assert all(source.owners == 1 for source in cache.sources.values())


def test_scoped_references_and_contents_obey_one_budget(tmp_path):
    cache = SourceParseCache(capacity=512)
    text = 'value = 1\n'
    for index in range(100):
        with cache.scope(tmp_path / str(index), adapters.ADAPTERS):
            assert cache.loads(text) == {'value': 1}
        assert cache.bytes <= cache.capacity
        assert len(cache.entries) <= cache.capacity // cache.REFERENCE_BYTES
        assert sum(source.owners for source in cache.sources.values()) == len(cache.entries)
        assert all(source.owners > 0 for source in cache.sources.values())
    assert cache.evictions > 0 and len(cache.sources) == 1


def test_last_reference_eviction_releases_contents_and_later_reads_are_fresh(tmp_path):
    cache = SourceParseCache(capacity=128)
    with cache.scope(tmp_path, adapters.ADAPTERS):
        first = cache.loads('title = "first"\n')
        first['title'] = 'changed'
        for index in range(8):
            assert cache.loads(f'title = "value{index}"\n') == {'title': f'value{index}'}
        assert cache.loads('title = "first"\n') == {'title': 'first'}
    assert cache.evictions > 0
    assert cache.bytes <= cache.capacity
    assert sum(source.owners for source in cache.sources.values()) == len(cache.entries)


def test_oversized_preparation_preserves_the_retained_small_source(tmp_path):
    cache = SourceParseCache(capacity=128)
    with cache.scope(tmp_path, adapters.ADAPTERS):
        assert cache.loads('value = 1\n') == {'value': 1}
        before = cache.stats()
        text = 'value = "' + 'x' * 1024 + '"\n'
        assert cache.loads(text) == {'value': 'x' * 1024}
        assert cache.bytes == before['bytes'] and cache.evictions == before['evictions']
        assert cache.loads('value = 1\n') == {'value': 1}
