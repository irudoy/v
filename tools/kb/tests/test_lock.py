from contextlib import ExitStack
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from kb import lock
from kb.repo import KbError


class LockTest(unittest.TestCase):
    def test_a_second_holder_gives_up_with_code_7_and_names_the_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with lock.held(root, timeout=5):
                self.assertEqual(json.loads((root / lock.PATH).read_text())["pid"], os.getpid())
                log = io.StringIO()
                with self.assertRaises(KbError) as refused:
                    with lock.held(root, timeout=0, log=log):
                        pass
                self.assertEqual(refused.exception.code, 7)
                self.assertIn("held by pid ", log.getvalue())
            with lock.held(root, timeout=0):
                pass
            self.assertEqual((root / lock.PATH).read_text(), "")


def virtual_time(monkeypatch, advance=lambda now: None):
    now = [0]
    monkeypatch.setattr(lock.time, "monotonic", lambda: now[0])

    def sleep(seconds):
        now[0] += 1
        advance(now[0])

    monkeypatch.setattr(lock.time, "sleep", sleep)
    return now


def test_wait_outlasts_the_limit_while_the_same_sync_makes_progress(tmp_path, monkeypatch):
    with ExitStack() as holder:
        holder.enter_context(lock.held(tmp_path, timeout=3))
        progress = holder.enter_context(lock.syncing(tmp_path, "sources"))

        def advance(now):
            if now in (2, 4, 6):
                progress(f"accesses {now}")
            if now == 8:
                holder.close()

        now = virtual_time(monkeypatch, advance)
        output = io.StringIO()
        with lock.held(tmp_path, timeout=3, log=output):
            assert now[0] == 8
        assert "graph sync: sources" in output.getvalue()
        assert "graph sync: accesses 6" in output.getvalue()
    assert (tmp_path / lock.PATH).read_text() == ""


@pytest.mark.parametrize("last_update,expired", [(None, 3), (2, 5)])
def test_a_sync_without_new_progress_keeps_the_timeout(tmp_path, monkeypatch, last_update, expired):
    with lock.held(tmp_path, timeout=3), lock.syncing(tmp_path, "stalled accesses") as progress:
        def advance(now):
            if now == last_update:
                progress("stalled accesses")
        now = virtual_time(monkeypatch, advance)
        with pytest.raises(KbError, match="stalled accesses") as caught:
            with lock.held(tmp_path, timeout=3, log=io.StringIO()):
                pytest.fail("the lock is still held")
        assert caught.value.code == 7
        assert now[0] == expired


@pytest.mark.parametrize("damaged", ['{"version":', b'\xff', 'pid 42: kb sync'])
def test_incomplete_or_legacy_status_cannot_extend_the_wait(tmp_path, monkeypatch, damaged):
    with lock.held(tmp_path, timeout=3):
        if isinstance(damaged, bytes):
            (tmp_path / lock.PATH).write_bytes(damaged)
        else:
            (tmp_path / lock.PATH).write_text(damaged)
        now = virtual_time(monkeypatch)
        with pytest.raises(KbError) as caught:
            with lock.held(tmp_path, timeout=3, log=io.StringIO()):
                pytest.fail("the lock is still held")
        assert caught.value.code == 7
        assert now[0] == 3


def test_progress_of_different_holder_tokens_cannot_extend_the_wait(tmp_path, monkeypatch):
    with lock.held(tmp_path, timeout=3), lock.syncing(tmp_path):
        path = tmp_path / lock.PATH
        state = json.loads(path.read_text())

        def advance(now):
            path.write_text(json.dumps({**state, "token": f"other-{now}", "progress": now + 10}))

        now = virtual_time(monkeypatch, advance)
        with pytest.raises(KbError) as caught:
            with lock.held(tmp_path, timeout=3, log=io.StringIO()):
                pytest.fail("the lock is still held")
        assert caught.value.code == 7
        assert now[0] == 3


def test_an_ordinary_successor_uses_ordinary_timeout_diagnostics(tmp_path, monkeypatch):
    with ExitStack() as syncing, ExitStack() as ordinary:
        syncing.enter_context(lock.held(tmp_path, timeout=3))
        progress = syncing.enter_context(lock.syncing(tmp_path))

        def advance(now):
            if now == 2:
                progress("accesses")
            if now == 3:
                syncing.close()
                ordinary.enter_context(lock.held(tmp_path, timeout=3))

        now = virtual_time(monkeypatch, advance)
        with pytest.raises(KbError, match="gave up after 3 s") as caught:
            with lock.held(tmp_path, timeout=3, log=io.StringIO()):
                pytest.fail("the ordinary successor still holds the lock")
        assert caught.value.code == 7
        assert now[0] == 5
        assert "graph-sync progress" not in str(caught.value)


@pytest.mark.parametrize("ordinary", [False, True])
def test_old_counters_and_ordinary_status_cannot_renew_a_deadline(tmp_path, monkeypatch, ordinary):
    with lock.held(tmp_path, timeout=3), lock.syncing(tmp_path):
        path = tmp_path / lock.PATH
        state = json.loads(path.read_text())

        def advance(now):
            changed = ({"operation": None, "progress": now + 1} if ordinary
                       else {"progress": now % 2})
            path.write_text(json.dumps({**state, **changed}))

        now = virtual_time(monkeypatch, advance)
        with pytest.raises(KbError) as caught:
            with lock.held(tmp_path, timeout=3, log=io.StringIO()):
                pytest.fail("the lock is still held")
        assert caught.value.code == 7
        assert now[0] == 3


def test_sync_status_and_lock_are_released_after_a_loader_failure(tmp_path):
    with pytest.raises(ValueError, match="loader failed"):
        with lock.held(tmp_path, timeout=3):
            with lock.syncing(tmp_path) as progress:
                progress("accesses")
                raise ValueError("loader failed")
    assert (tmp_path / lock.PATH).read_text() == ""
    with lock.held(tmp_path, timeout=0):
        with lock.syncing(tmp_path):
            assert json.loads((tmp_path / lock.PATH).read_text())["operation"] == "sync"
        assert json.loads((tmp_path / lock.PATH).read_text())["operation"] is None


if __name__ == "__main__":
    unittest.main()
