from pathlib import Path
from copy import deepcopy
import subprocess
import sys

import pytest

from kb import evidence_ref, repo


def archive_claim():
    return {'at': 12, 'note': 'Retain this condition.', 'evidence': [
        {'kind': 'test', 'path': 'tools/tests/stock.py#test_entry', 'key': 'test_entry',
         'supports': 'identity'},
        {'kind': 'spec', 'path': 'defs/mechanism.md', 'key': 'mechanism'}]}


def test_archive_equivalence_retains_the_complete_ordered_claim():
    before = archive_claim()
    after = deepcopy(before)
    after['evidence'][0]['path'] = f"git:{evidence_ref.STOCK_ARCHIVE}:" + before['evidence'][0]['path']
    assert evidence_ref.archive_equivalent(before, after)
    assert evidence_ref.archive_equivalent(after, after)
    assert not evidence_ref.archive_equivalent(after, before)


def test_archive_equivalence_accepts_a_specification_key_locator():
    before = {'evidence': [{'kind': 'spec', 'key': 'defs/proof.md#entry'}]}
    after = {'evidence': [{'kind': 'spec', 'key':
                          f'git:{evidence_ref.STOCK_ARCHIVE}:defs/proof.md#entry'}]}
    assert evidence_ref.archive_equivalent(before, after)


def test_archive_equivalence_retains_typed_compiled_claim_leaves():
    from kb.model import SymbolKey
    before = archive_claim()
    before['props'] = {'via': [SymbolKey('7mfk', 'fn', 0x4ead4)]}
    before['evidence'].append({'kind': 'trace', 'to': SymbolKey('7mfk', 'ram', 0xffff2312),
                               'relies': 'structure'})
    after = deepcopy(before)
    after['evidence'][0]['path'] = f"git:{evidence_ref.STOCK_ARCHIVE}:" + before['evidence'][0]['path']
    assert evidence_ref.archive_equivalent(before, after)
    after['props']['via'][0] = SymbolKey('7mfk', 'fn', 0x4ead6)
    assert not evidence_ref.archive_equivalent(before, after)
    after = deepcopy(before)
    after['evidence'][2]['to'] = SymbolKey('7mfk', 'ram', 0xffff2314)
    assert not evidence_ref.archive_equivalent(before, after)


@pytest.mark.parametrize('value', (True, 1.0))
def test_archive_equivalence_distinguishes_boolean_integer_and_float(value):
    before = archive_claim()
    before['at'] = 1
    after = deepcopy(before)
    after['at'] = value
    assert not evidence_ref.archive_equivalent(before, after)


@pytest.mark.parametrize('changed', (
    'tag', 'path', 'fragment', 'kind', 'supports', 'note', 'at', 'type',
    'added', 'removed', 'order', 'missing-field',
))
def test_archive_equivalence_refuses_every_other_change(changed):
    before = archive_claim()
    after = deepcopy(before)
    item = after['evidence'][0]
    item['path'] = f"git:{evidence_ref.STOCK_ARCHIVE}:" + item['path']
    if changed in ('tag', 'path', 'fragment'):
        old, new = {'tag': (evidence_ref.STOCK_ARCHIVE, 'another-tag'),
                    'path': ('stock.py', 'other.py'),
                    'fragment': ('test_entry', 'other_entry')}[changed]
        item['path'] = item['path'].replace(old, new)
    elif changed in ('kind', 'supports'):
        item[changed] = 'code' if changed == 'kind' else 'contract'
    elif changed == 'note':
        after['note'] += ' Changed.'
    elif changed == 'at':
        after['at'] += 1
    elif changed == 'type':
        after['at'] = 12.0
    elif changed == 'added':
        after['evidence'].append(deepcopy(item))
    elif changed == 'removed':
        after['evidence'].pop()
    elif changed == 'order':
        after['evidence'].reverse()
    else:
        del item['supports']
    assert not evidence_ref.archive_equivalent(before, after)


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
