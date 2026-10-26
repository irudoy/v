"""Unresolved review maintenance never supplies evidence for a new claim."""
from copy import deepcopy
from unittest.mock import patch

import pytest
import tomlkit

from kb import reconciliation, repo
from tools.kb.tests.test_code_reconciliation import model, observed


def declared(tmp_path):
    subject = model()
    subject.root, subject.overlay = tmp_path, {}
    link = subject.links[0]
    link.owner.name, link.owner.kind = 'test', 'ram'
    link.to.name, link.to.kind = 'caller', 'fn'
    subject.meanings = [link.owner, link.to]
    for owner in subject.meanings:
        for symbol in owner.symbols.values():
            symbol.generated = owner.name
    records = reconciliation.reviews(subject)
    subject.config['reconciliation']['review'] = records
    source = tomlkit.dumps(dict(schema_version=1,
        names=dict(owners_checked=True, reserved=[]),
        reconciliation=subject.config['reconciliation']))
    path = tmp_path / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('# Retain unrelated owner metadata.\n' + source)
    return subject, path.read_text()


def exact_sources():
    return patch.multiple(reconciliation,
        accesses=lambda *args: observed(None, []))


def test_deleted_access_withdraws_only_its_review_and_preserves_other_owner_tables(tmp_path):
    with exact_sources(), patch.object(reconciliation.match, 'l0_digest', return_value='0123456789abcdef'):
        before, text = declared(tmp_path)
        after = deepcopy(before)
        after.links = []
        updated = reconciliation.rebase(before, after, {})
        document = tomlkit.parse(updated)
        assert document['reconciliation']['review'] == []
        assert document['names'] == tomlkit.parse(text)['names']
        assert updated.startswith('# Retain unrelated owner metadata.\n')
        assert (tmp_path / repo.OWNER_CONFIG).read_text() == text
        after.config['reconciliation'] = document['reconciliation']
        assert reconciliation.check(after) == []


def test_rename_rebinds_the_exact_claim_and_source_without_resolving_its_uncertainty(tmp_path):
    with exact_sources(), patch.object(reconciliation.match, 'l0_digest', return_value='0123456789abcdef'):
        before, text = declared(tmp_path)
        after = deepcopy(before)
        link = after.links[0]
        link.owner.key, link.owner.name = 'renamed_test/ram', 'renamed_test'
        link.sources = {'kb/ram/renamed_test.toml'}
        link.owner.symbols['7mfk'].sources = link.sources
        updated = reconciliation.rebase(before, after, {'test/ram': 'renamed_test/ram'})
        after.config['reconciliation'] = tomlkit.parse(updated)['reconciliation']
        assert reconciliation.check(after) == []
        old = before.config['reconciliation']['review'][0]
        new = after.config['reconciliation']['review'][0]
        assert new['state'] == old['state'] == 'unresolved'
        assert new['reason'] == old['reason']
        assert new['l0'] == old['l0']
        assert new['claim_sha256'] != old['claim_sha256']
        assert (tmp_path / repo.OWNER_CONFIG).read_text() == text


@pytest.mark.parametrize('field,value', [
    ('roles', ['different role']), ('props', {'note': 'A different condition.'}),
    ('evidence', [{'kind': 'spec', 'path': 'defs/different.md'}]),
])
def test_a_changed_claim_cannot_adopt_the_previous_review(tmp_path, field, value):
    with exact_sources(), patch.object(reconciliation.match, 'l0_digest', return_value='0123456789abcdef'):
        before, _ = declared(tmp_path)
        after = deepcopy(before)
        setattr(after.links[0], field, value)
        assert reconciliation.rebase(before, after, {}) is None
        assert reconciliation.check(after)


def test_changed_l0_cannot_reuse_a_renamed_review(tmp_path):
    with exact_sources(), patch.object(reconciliation.match, 'l0_digest', return_value='0123456789abcdef'):
        before, _ = declared(tmp_path)
    after = deepcopy(before)
    after.links[0].to.key, after.links[0].to.name = 'renamed_caller/fn', 'renamed_caller'
    with exact_sources(), patch.object(reconciliation.match, 'l0_digest',
                                      side_effect=['0123456789abcdef', '1111111111111111']):
        assert reconciliation.rebase(before, after, {'caller/fn': 'renamed_caller/fn'}) is None
