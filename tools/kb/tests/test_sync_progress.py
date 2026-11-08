"""Reload announcements and lock state without a live graph."""

from contextlib import nullcontext
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from kb import graph, lock
from kb.repo import KbError


@pytest.mark.parametrize("held", [False, True])
def test_a_stale_read_announces_sync_before_the_loader_starts(monkeypatch, tmp_path, held):
    events = []
    old, fresh = SimpleNamespace(close=Mock()), object()
    sources = iter((old, fresh))
    monkeypatch.setattr(graph, "Graph", lambda root: next(sources))
    monkeypatch.setattr(graph.fingerprint, "compute", lambda root: object())
    monkeypatch.setattr(graph, "meta", lambda source: None)
    monkeypatch.setattr(graph, "stale", lambda previous, fp: True)
    monkeypatch.setattr(graph, "sync", lambda root, log: events.append("sync"))
    monkeypatch.setattr(graph, "sync_held", lambda root, log: events.append("sync held"))

    assert graph.fresh(tmp_path, held=held, log=events.append) is fresh
    assert events == ["graph: stale index; starting synchronization under .kb/lock",
                      "sync held" if held else "sync"]
    old.close.assert_called_once()


def test_no_sync_refuses_without_starting_or_announcing_a_reload(monkeypatch, tmp_path):
    messages = []
    source = SimpleNamespace(close=Mock())
    monkeypatch.setattr(graph, "Graph", lambda root: source)
    monkeypatch.setattr(graph.fingerprint, "compute", lambda root: object())
    monkeypatch.setattr(graph, "meta", lambda source: None)
    monkeypatch.setattr(graph, "stale", lambda previous, fp: True)
    sync = Mock()
    monkeypatch.setattr(graph, "sync", sync)
    monkeypatch.setattr(graph, "sync_held", sync)
    with pytest.raises(KbError, match="uv run kb sync") as caught:
        graph.fresh(tmp_path, no_sync=True, log=messages.append)
    assert caught.value.code == 6
    assert messages == []
    sync.assert_not_called()


@pytest.mark.parametrize("failure", [False, True])
def test_sync_held_publishes_loader_progress_and_restores_the_holder(monkeypatch, tmp_path,
                                                                   failure):
    model = SimpleNamespace(names=[])
    fingerprint = SimpleNamespace(value="current")
    seen = []

    def state():
        return json.loads((tmp_path / lock.PATH).read_text())

    def compile_sources(root):
        seen.append(state())
        return model

    def load(*args, progress, **kwargs):
        progress("fixture accesses")
        seen.append(state())
        if failure:
            raise ValueError("loader failed")
        return {}

    monkeypatch.setattr(graph.compile, "build", compile_sources)
    monkeypatch.setattr(graph.names, "enroll", lambda *args: [])
    monkeypatch.setattr(graph.fingerprint, "compute", lambda root: fingerprint)
    monkeypatch.setattr(graph, "Graph", lambda root: nullcontext(SimpleNamespace(uri="fixture")))
    monkeypatch.setattr(graph, "load", load)
    with lock.held(tmp_path, timeout=0):
        if failure:
            with pytest.raises(ValueError, match="loader failed"):
                graph.sync_held(tmp_path, log=lambda text: None)
        else:
            assert graph.sync_held(tmp_path, log=lambda text: None) == (model, fingerprint)
        assert state()["operation"] is None
    assert [item["stage"] for item in seen] == ["compiling sources", "fixture accesses"]
    assert all(item["operation"] == "sync" for item in seen)
    assert seen[0]["token"] == seen[1]["token"]
    assert seen[1]["progress"] > seen[0]["progress"]
    assert (tmp_path / lock.PATH).read_text() == ""
