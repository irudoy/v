"""Configuration preparation retains current sources and independent checks."""

from concurrent.futures import ThreadPoolExecutor
import pickle
import re
import tomllib
from unittest import mock

import pytest

from kb import repo


TEXT = 'title = "Probe"\nstamp = 2026-10-05T00:00:00Z\n' \
       '[[items]]\nname = "first"\nvalues = [1, 2]\n'
OWNERS = ('schema_version = 1\n[names]\nowners_checked = true\nreserved = []\n'
          '[reconciliation]\nenabled = true\nreview = []\n'
          '[source_bindings]\nenabled = true\nreview = []\n')


def test_default_preparation_budget_matches_its_published_contract():
    text = (repo.ROOT / 'tools/kb/README.md').read_text(encoding='utf-8')
    [published] = re.findall(r'a ([0-9]+) MiB content budget', text)
    documents = repo._ConfigurationDocuments()
    assert documents.capacity == int(published) * (1 << 20)
    assert documents.bytes == 0 and not documents.entries


def fresh_reader(monkeypatch, capacity=64 << 20):
    documents = repo._ConfigurationDocuments(capacity=capacity)
    monkeypatch.setattr(repo, '_CONFIG_DOCUMENTS', documents)
    return documents


def test_successful_parse_returns_separate_nested_documents():
    parser = mock.Mock(wraps=tomllib.loads)
    documents = repo._ConfigurationDocuments(parser)
    expected = tomllib.loads(TEXT)
    first = documents.loads(TEXT)
    first['items'][0]['values'].append(3)
    first['items'].append({'name': 'other'})
    second = documents.loads(TEXT)
    assert second == expected
    second['items'][0]['name'] = 'changed'
    assert documents.loads(TEXT) == expected
    assert parser.call_count == 1
    assert all(isinstance(packed, bytes) for packed, _ in documents.entries.values())


def test_reader_observes_roots_disk_changes_overlays_and_owner_removal(tmp_path, monkeypatch):
    fresh_reader(monkeypatch)
    roots = [tmp_path / name for name in ('first', 'second')]
    for root in roots:
        (root / repo.CONFIG).parent.mkdir(parents=True)
        (root / repo.CONFIG).write_text(TEXT)
        (root / repo.OWNER_CONFIG).write_text(OWNERS)
    first = repo.config(roots[0])
    first['reconciliation']['review'].append({'key': 'changed'})
    first['items'][0]['values'].append(3)
    assert repo.config(roots[1]) == repo.config(roots[0])
    (roots[0] / repo.CONFIG).write_text('title = "changed"\n')
    assert repo.config(roots[0])['title'] == 'changed'
    assert repo.config(roots[1])['title'] == 'Probe'
    overlay = {repo.CONFIG: 'title = "overlay"\n', repo.OWNER_CONFIG: None}
    assert repo.config(roots[0], overlay) == {'title': 'overlay'}
    overlay[repo.CONFIG] = 'title = "replacement"\n'
    assert repo.config(roots[0], overlay) == {'title': 'replacement'}
    (roots[0] / repo.OWNER_CONFIG).unlink()
    assert repo.config(roots[0]) == {'title': 'changed'}
    (roots[0] / repo.CONFIG).unlink()
    with pytest.raises(FileNotFoundError):
        repo.config(roots[0])


def test_owner_schema_validation_executes_after_every_preparation(tmp_path, monkeypatch):
    documents = fresh_reader(monkeypatch)
    bad = OWNERS + '[l0]\nscripts = ["Other.java"]\n'
    overlay = {repo.CONFIG: TEXT, repo.OWNER_CONFIG: bad}
    for _ in range(2):
        with pytest.raises(repo.KbError, match='only name ownership'):
            repo.config(tmp_path, overlay)
    assert bad in documents.entries
    overlay[repo.OWNER_CONFIG] = OWNERS
    assert repo.config(tmp_path, overlay)['source_bindings']['enabled'] is True


def test_syntax_errors_are_not_retained():
    parser = mock.Mock(wraps=tomllib.loads)
    documents = repo._ConfigurationDocuments(parser)
    text = 'title = "unterminated'
    with pytest.raises(tomllib.TOMLDecodeError) as expected:
        tomllib.loads(text)
    for _ in range(2):
        with pytest.raises(tomllib.TOMLDecodeError) as actual:
            documents.loads(text)
        assert str(actual.value) == str(expected.value)
    assert parser.call_count == 2 and not documents.entries


def test_changed_parser_executes_on_every_reader_call(tmp_path, monkeypatch):
    fresh_reader(monkeypatch)
    parser = mock.Mock(wraps=tomllib.loads)
    monkeypatch.setattr(repo, 'tomllib', mock.Mock(loads=parser))
    for _ in range(2):
        assert repo.config(tmp_path, {repo.CONFIG: TEXT, repo.OWNER_CONFIG: None}) \
               == tomllib.loads(TEXT)
    assert parser.call_count == 2


def test_eviction_and_oversized_inputs_preserve_fresh_values():
    parser = mock.Mock(wraps=tomllib.loads)
    documents = repo._ConfigurationDocuments(parser, capacity=128)
    for text in ('title = "first"\n', 'title = "second"\n', 'title = "third"\n'):
        documents.loads(text)['title'] = 'changed'
    assert documents.loads('title = "first"\n') == {'title': 'first'}
    assert parser.call_count == 4
    assert documents.bytes <= documents.capacity
    big = 'title = "' + 'x' * 256 + '"\n'
    assert documents.loads(big) == documents.loads(big) == {'title': 'x' * 256}
    assert big not in documents.entries


@pytest.mark.parametrize('error', [pickle.PicklingError, TypeError, RecursionError])
def test_unserializable_preparation_returns_the_original_successful_parse(monkeypatch, error):
    parser = mock.Mock(wraps=tomllib.loads)
    documents = repo._ConfigurationDocuments(parser)
    monkeypatch.setattr(repo.pickle, 'dumps', mock.Mock(side_effect=error('cannot serialize')))
    for _ in range(2):
        assert documents.loads(TEXT) == tomllib.loads(TEXT)
    assert parser.call_count == 2 and not documents.entries


def test_nonstandard_text_retains_parser_behavior():
    class Text(str):
        __hash__ = None
    parser = mock.Mock(wraps=tomllib.loads)
    documents = repo._ConfigurationDocuments(parser)
    for _ in range(2):
        assert documents.loads(Text(TEXT)) == tomllib.loads(TEXT)
    assert parser.call_count == 2 and not documents.entries


def test_concurrent_reads_return_independent_results_with_a_bounded_budget():
    documents = repo._ConfigurationDocuments()
    expected = tomllib.loads(TEXT)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(documents.loads, [TEXT] * 20))
    assert all(result == expected for result in results)
    results[0]['items'][0]['values'].append(3)
    assert all(result == expected for result in results[1:])
    assert documents.loads(TEXT) == expected
    assert documents.bytes <= documents.capacity


def test_owner_merges_do_not_change_a_prepared_execution_document(tmp_path, monkeypatch):
    documents = fresh_reader(monkeypatch)
    original = tomllib.loads(TEXT)
    merged = repo.config(tmp_path, {repo.CONFIG: TEXT, repo.OWNER_CONFIG: OWNERS})
    merged['source_bindings']['review'].append({'key': 'changed'})
    assert documents.loads(TEXT) == original
    assert repo.config(tmp_path, {repo.CONFIG: TEXT, repo.OWNER_CONFIG: None}) == original
    owners = tomllib.loads(OWNERS)
    assert repo.config(tmp_path, {repo.CONFIG: TEXT, repo.OWNER_CONFIG: OWNERS}) \
           == {**original, **{key: owners[key] for key in (
               'names', 'reconciliation', 'source_bindings')}}
