"""Knowledge-owner declarations cannot alter executed L0 settings."""
from copy import deepcopy
import tomllib

import pytest
import tomlkit

from kb import compile, fingerprint, repo, transition


EXECUTION = '# Retained execution settings.\n[names]\nwords = 2\n[l0]\nscripts = ["ExportGraph.java"]\n'


def owners():
    return dict(schema_version=1, names=dict(owners_checked=True, reserved=[]),
                reconciliation=dict(enabled=True, review=[]),
                source_bindings=dict(enabled=True, review=[]))


def test_owner_separation_restores_exact_execution_bytes():
    current = tomllib.loads(EXECUTION)
    extra = owners()
    current['names'].update(extra['names'])
    current.update({key: extra[key] for key in ('reconciliation', 'source_bindings')})
    texts = transition.separated_owner_texts(tomlkit.dumps(current), EXECUTION)
    assert texts[repo.CONFIG] == EXECUTION
    assert tomllib.loads(texts[repo.OWNER_CONFIG]) == extra


def test_owner_separation_refuses_an_execution_change():
    current = tomllib.loads(EXECUTION)
    extra = owners()
    current['names'].update(extra['names'])
    current.update({key: extra[key] for key in ('reconciliation', 'source_bindings')})
    current['l0']['scripts'].append('ChangedProducer.java')
    with pytest.raises(repo.KbError, match='beyond owner'):
        transition.separated_owner_texts(tomlkit.dumps(current), EXECUTION)


def test_owner_overlay_preserves_execution_settings_and_supports_historical_reads(tmp_path):
    (tmp_path / repo.CONFIG).parent.mkdir(parents=True)
    (tmp_path / repo.CONFIG).write_text(EXECUTION)
    (tmp_path / repo.OWNER_CONFIG).write_text(tomlkit.dumps(owners()))
    assert repo.config(tmp_path)['l0'] == tomllib.loads(EXECUTION)['l0']
    assert repo.config(tmp_path)['names']['words'] == 2
    assert repo.config(tmp_path, {repo.OWNER_CONFIG: None}) == tomllib.loads(EXECUTION)


def test_owner_content_contributes_to_the_compiler_fingerprint(tmp_path, monkeypatch):
    monkeypatch.setattr(compile.adapters, 'inputs', lambda root: [])
    monkeypatch.setattr(compile.names, 'inputs', lambda: [])
    from kb import compatibility
    monkeypatch.setattr(compatibility, 'inputs', lambda root: [])
    monkeypatch.setattr(repo, 'layouts', lambda root: {})
    monkeypatch.setattr(repo, 'images', lambda root: {})
    (tmp_path / repo.CONFIG).parent.mkdir(parents=True)
    (tmp_path / repo.CONFIG).write_text(EXECUTION)
    (tmp_path / repo.OWNER_CONFIG).write_text(tomlkit.dumps(owners()))
    before = fingerprint.compute(tmp_path)
    changed = owners()
    changed['names']['reserved'].append({'name': 'held-name'})
    (tmp_path / repo.OWNER_CONFIG).write_text(tomlkit.dumps(changed))
    after = fingerprint.compute(tmp_path)
    assert repo.OWNER_CONFIG.as_posix() in before.blobs
    assert before.blobs[repo.CONFIG.as_posix()] == after.blobs[repo.CONFIG.as_posix()]
    assert before.value != after.value


@pytest.mark.parametrize('alteration', ['l0', 'census', 'names', 'schema', 'reviews'])
def test_owner_file_refuses_execution_overrides_and_malformed_sections(tmp_path, alteration):
    value = deepcopy(owners())
    if alteration in ('l0', 'census'):
        value[alteration] = {'scripts': ['ChangedProducer.java']}
    elif alteration == 'names':
        value['names']['words'] = 17
    elif alteration == 'schema':
        value['schema_version'] = True
    else:
        value['reconciliation'] = []
    with pytest.raises(repo.KbError, match='only name ownership'):
        repo.config(tmp_path, {repo.CONFIG: EXECUTION, repo.OWNER_CONFIG: tomlkit.dumps(value)})
