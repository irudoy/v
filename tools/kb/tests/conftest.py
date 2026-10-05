"""Test-local stock inputs with catalog validation before and after use."""

import pytest

from kb import derive, repo
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
