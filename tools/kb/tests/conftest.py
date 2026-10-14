"""Test-local stock inputs with catalog validation before and after use."""

from contextlib import contextmanager
from functools import lru_cache

import pytest

from kb import compile, derive, match, repo
from tools.kb.tests.source_parse_cache import SourceParseCache


@pytest.fixture(scope="session")
def jk08a_stock_bytes():
    layout = repo.layout("7mfk")
    data = derive.image_bytes(layout)
    yield data
    assert derive.image_bytes(layout) == data, "JK08A stock image changes during the test session"


@pytest.fixture(scope="module")
def reuse_kb_source_parses(request):
    cache = SourceParseCache()
    cold_start = cache.stats()
    with pytest.MonkeyPatch.context() as patch:
        cache.install(patch)
        yield cache
    results = getattr(request.config, '_kb_source_parse_cache_stats', [])
    results.append(dict(module=request.node.nodeid, cold_start=cold_start, final=cache.stats()))
    request.config._kb_source_parse_cache_stats = results


@contextmanager
def _isolated_function_cache(monkeypatch, module, name, public=None):
    """Keep synthetic cache entries and resets inside their fixture owner."""
    original = getattr(module, name)
    local = lru_cache(**original.cache_parameters())(original.__wrapped__)
    with monkeypatch.context() as patch:
        patch.setattr(module, name, local)
        if public is not None:
            patch.setattr(public, 'cache_clear', local.cache_clear)
            patch.setattr(public, 'cache_info', local.cache_info)
        try:
            yield
        finally:
            local.cache_clear()


@pytest.fixture
def isolated_compiler_cache(monkeypatch):
    with _isolated_function_cache(monkeypatch, compile, '_cached', compile.cached):
        yield


@pytest.fixture
def isolated_literal_pair_cache(monkeypatch):
    with _isolated_function_cache(monkeypatch, derive, '_literal_pairs', derive.literal_pairs):
        yield


@pytest.fixture
def isolated_match_cache(monkeypatch):
    with _isolated_function_cache(monkeypatch, match, '_code'):
        yield
