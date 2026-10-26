from pathlib import Path
import subprocess
import sys

import pytest

from kb import evidence_ref, repo


@pytest.mark.parametrize("text", (
    "git:archive/stock-proofs-2026-10-26:tools/tests/test_stock_case.py",
    "git:archive/stock-proofs-2026-10-26:defs/mechanism.md#calculation",
    "git:release-1.2:docs/Source Notes.md#L12",
))
def test_tagged_evidence_round_trips_without_normalizing_its_locator(text):
    reference = evidence_ref.parse(text)
    assert str(reference) == text
    assert reference.tag
    assert reference.path


@pytest.mark.parametrize("text", (None, "", "tools/tests/test_case.py", "manual:chapter-5"))
def test_current_references_keep_their_existing_interpretation(text):
    assert evidence_ref.parse(text) is None


@pytest.mark.parametrize("text", (
    "git:tag", "git::file.py", "git:bad..tag:file.py", "git:bad//tag:file.py",
    "git:tag.lock:file.py", "git:tag:/absolute.py", "git:tag:../outside.py",
    "git:tag:a/../file.py", "git:tag:a//file.py", "git:tag:./file.py",
    "git:tag:a\\file.py", "git:tag:file.py#", "git:tag:file.py#two words",
    "git:tag:file.py#one#two", "git:tag:file.py\n", "git:tag:",
))
def test_malformed_archive_references_cannot_become_current_paths(text):
    with pytest.raises(ValueError):
        evidence_ref.parse(text)


def test_parsing_never_resolves_or_opens_the_archive(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("archive reference parsing performs I/O")

    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    reference = evidence_ref.parse("git:missing-tag:absent/path.py#test_case")
    assert (reference.tag, reference.path, reference.fragment) == (
        "missing-tag", "absent/path.py", "test_case")


def test_the_parser_imports_no_other_kb_module():
    probe = """
import sys
class OnlyEvidenceRef:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith('kb.') and fullname != 'kb.evidence_ref':
            raise AssertionError(fullname)
sys.meta_path.insert(0, OnlyEvidenceRef())
sys.path.insert(0, sys.argv[1])
from kb import evidence_ref
assert evidence_ref.parse('git:archive-tag:absent.py').path == 'absent.py'
assert {name for name in sys.modules if name.startswith('kb.')} == {'kb.evidence_ref'}
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", probe, str(repo.ROOT / "tools/kb/src")],
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
