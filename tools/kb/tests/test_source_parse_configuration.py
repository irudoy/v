"""Scoped test preparation covers default configuration reads and restores them."""

import tomllib
from unittest import mock

import pytest

from kb import adapters, repo
from tools.kb.tests.source_parse_cache import SourceParseCache


def test_configuration_reads_have_scope_and_separate_current_values(tmp_path):
    path = tmp_path / repo.CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('title = "first"\n[[nested]]\nvalues = [1, 2]\n')
    original_config, parser = repo.config, tomllib.loads
    cache = SourceParseCache()
    with mock.patch.object(tomllib, 'loads', wraps=parser) as parsed, \
            pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        first = repo.config(tmp_path)
        first['nested'][0]['values'].append(3)
        assert repo.config(root=tmp_path)['nested'][0]['values'] == [1, 2]
        assert parsed.call_count == 1
        path.write_text('title = "second"\n')
        assert repo.config(tmp_path) == {'title': 'second'}
        assert repo.config(tmp_path, {repo.CONFIG: 'title = "overlay"\n'}) \
               == {'title': 'overlay'}
        assert parsed.call_count == 3
    assert repo.config is original_config


def test_configuration_root_and_adapter_order_keep_separate_parse_preparation(tmp_path):
    roots = [tmp_path / name for name in ('first', 'second')]
    for root in roots:
        path = root / repo.CONFIG
        path.parent.mkdir(parents=True)
        path.write_text('title = "same"\n')
    parser = tomllib.loads
    cache = SourceParseCache()
    with mock.patch.object(tomllib, 'loads', wraps=parser) as parsed, \
            pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        for root in roots:
            assert repo.config(root) == repo.config(root) == {'title': 'same'}
        assert parsed.call_count == 2
        with cache.scope(roots[0], tuple(reversed(adapters.ADAPTERS))):
            assert repo.config(roots[0]) == repo.config(roots[0]) == {'title': 'same'}
        assert parsed.call_count == 3


def test_configuration_default_root_calls_the_original_reader_with_a_scoped_parser():
    cache = SourceParseCache()
    original = repo.config
    with mock.patch.object(repo, 'config', wraps=original) as reader, \
            pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        default = repo.config()
        assert default == repo.config(root=repo.ROOT)
        assert reader.call_count == 2
        assert cache.hits > 0
    assert repo.config is original
