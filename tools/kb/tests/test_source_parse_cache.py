"""Source reuse must preserve independent data and observe every new input."""

from decimal import Decimal
from pathlib import Path
import tomllib
from unittest import mock

import pytest

from kb import adapters, compile, repo, store, write
from tools.kb.tests.source_parse_cache import SourceParseCache


def test_repeated_sources_return_independent_nested_documents(tmp_path):
    text = 'title = "Probe"\nstamp = 2026-10-05T00:00:00Z\n[[symbol]]\naddress = "ffff1000"\n' \
           '[[symbol.evidence]]\nkind = "test"\npath = "defs/probe.md"\n'
    expected = tomllib.loads(text)
    cache = SourceParseCache()
    with cache.scope(tmp_path, adapters.ADAPTERS):
        first = cache.loads(text)
        first['symbol'][0]['evidence'][0]['path'] = 'other.md'
        first['symbol'].append({'address': 'ffff2000'})
        second = cache.loads(text)
        assert second == expected
        second['symbol'][0]['address'] = 'ffff3000'
        assert cache.loads(text) == expected


def test_reads_observe_disk_changes_overlay_replacement_addition_and_removal(tmp_path):
    path = store.path_of('ram', 'probe')
    absolute = tmp_path / path
    absolute.parent.mkdir(parents=True)
    absolute.write_text('title = "first"\n')
    cache = SourceParseCache()
    with pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        assert store.load(tmp_path, path) == {'title': 'first'}
        assert store.load(tmp_path, path) == {'title': 'first'}
        absolute.write_text('title = "second"\n')
        assert store.load(tmp_path, path) == {'title': 'second'}
        overlay = {path: 'title = "overlay"\n'}
        assert store.load(tmp_path, path, overlay) == {'title': 'overlay'}
        assert store.load(tmp_path, path) == {'title': 'second'}
        added = store.path_of('ram', 'added')
        assert store.load(tmp_path, added, {added: 'title = "added"\n'}) == {'title': 'added'}
        with pytest.raises(FileNotFoundError):
            store.load(tmp_path, path, {path: None})
        absolute.unlink()
        with pytest.raises(FileNotFoundError):
            store.load(tmp_path, path)


def test_roots_and_effective_adapter_orders_partition_identical_source_text(tmp_path):
    path = store.path_of('ram', 'probe')
    roots = [tmp_path / name for name in ('first', 'second')]
    for root in roots:
        absolute = root / path
        absolute.parent.mkdir(parents=True)
        absolute.write_text('title = "same"\n')
    cache = SourceParseCache()
    original = tomllib.loads
    with mock.patch.object(tomllib, 'loads', wraps=original) as parsed, \
            pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        for root in roots:
            for _ in range(2):
                assert store.load(root, path) == {'title': 'same'}
        assert parsed.call_count == 2
        with cache.scope(roots[0], tuple(reversed(adapters.ADAPTERS))):
            assert store.load(roots[0], path) == {'title': 'same'}
            assert store.load(roots[0], path) == {'title': 'same'}
            patch.chdir(tmp_path)
            assert store.load(Path('first'), path) == {'title': 'same'}
        assert parsed.call_count == 3


def test_custom_float_conversion_executes_on_every_request(tmp_path):
    cache = SourceParseCache()
    converted = []

    def decimal(text):
        converted.append(text)
        return Decimal(text)

    with cache.scope(tmp_path, adapters.ADAPTERS):
        assert cache.loads('value = 1.25\n') == {'value': 1.25}
        for _ in range(2):
            assert cache.loads('value = 1.25\n', parse_float=decimal) == {'value': Decimal('1.25')}
    assert converted == ['1.25', '1.25']


def test_syntax_refusals_keep_the_original_exception_and_are_not_reused(tmp_path):
    text = 'title = "unterminated'
    original = tomllib.loads
    with pytest.raises(tomllib.TOMLDecodeError) as expected:
        original(text)
    cache = SourceParseCache()
    with mock.patch.object(tomllib, 'loads', wraps=original) as parsed, \
            cache.scope(tmp_path, adapters.ADAPTERS):
        for _ in range(2):
            with pytest.raises(tomllib.TOMLDecodeError) as actual:
                cache.loads(text)
            assert str(actual.value) == str(expected.value)
        assert parsed.call_count == 2


def test_capacity_eviction_preserves_fresh_values(tmp_path):
    cache = SourceParseCache(capacity=128)
    texts = ['title = "first"\n', 'title = "second"\n', 'title = "third"\n']
    with cache.scope(tmp_path, adapters.ADAPTERS):
        first = cache.loads(texts[0])
        first['title'] = 'mutated'
        for text in texts[1:]:
            assert cache.loads(text) == tomllib.loads(text)
        assert cache.loads(texts[0]) == {'title': 'first'}
    assert cache.evictions > 0
    assert cache.bytes <= cache.capacity


def test_patch_scope_restores_original_compiler_readers_and_checks(tmp_path):
    originals = (compile.build, write._issues, store.load, store.canonical,
                 compile.tomllib, repo.tomllib, store.tomllib)
    cache = SourceParseCache()
    with pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        assert compile.build is not originals[0]
        assert write._issues is not originals[1]
    assert (compile.build, write._issues, store.load, store.canonical,
            compile.tomllib, repo.tomllib, store.tomllib) == originals
