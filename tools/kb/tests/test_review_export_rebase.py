"""Export maintenance preserves uncertainty and never reviews a new difference."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import contextlib
import io

import pytest
import tomlkit

from kb import cli, fingerprint, l0, reconciliation, repo, write
from kb.model import SymbolKey
from kb.repo import KbError
from tools.kb.tests.test_code_reconciliation import model, observed


OLD = '0123456789abcdef'
NEW = 'fedcba9876543210'


@contextlib.contextmanager
def export(digest, sites=()):
    with patch.object(reconciliation.match, 'l0_digest', return_value=digest), \
            patch.object(reconciliation, 'accesses', return_value=observed(None, sites)):
        yield


def declared(tmp_path, sites=()):
    subject = model()
    subject.root, subject.overlay, subject.names, subject.meanings = tmp_path, {}, [], []
    subject.entities = {}
    with export(OLD, sites):
        subject.config['reconciliation']['review'] = reconciliation.reviews(subject)
    text = '# Keep unrelated owner metadata.\n' + tomlkit.dumps({
        'schema_version': 1, 'names': {'owners_checked': True, 'reserved': []},
        'reconciliation': subject.config['reconciliation']})
    path = tmp_path / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(text)
    (tmp_path / repo.CONFIG).write_text('schema_version = 1\n[lock]\ntimeout = 1\n')
    return subject, path


def plan(subject, sites=(), **kwargs):
    with export(NEW, sites):
        return reconciliation.rebase_export(subject, '7mfk', OLD, **kwargs)


def test_export_rebase_changes_only_l0_and_preserves_state_reason_and_owner_text(tmp_path):
    subject, path = declared(tmp_path)
    before = path.read_text()
    held = deepcopy(subject.config)
    text, lines = plan(subject)
    assert text == before.replace(f'l0 = "{OLD}"', f'l0 = "{NEW}"')
    assert any('rebased=1' in line for line in lines)
    assert path.read_text() == before and subject.config == held
    after = deepcopy(subject)
    after.config['reconciliation'] = tomlkit.parse(text)['reconciliation'].unwrap()
    after.overlay[repo.OWNER_CONFIG] = text
    with export(NEW):
        assert reconciliation.check(after) == []
        assert reconciliation.rebase_export(after, '7mfk', OLD)[0] is None


def test_a_reproduced_access_leaves_the_vanished_difference_untransferred(tmp_path):
    subject, path = declared(tmp_path)
    before = path.read_text()
    text, lines = plan(subject, [{'site': 0x200, 'mode': 'store', 'width': 1}])
    assert text is None and path.read_text() == before
    assert any('vanished' in line and '7mfk-ffff1000/ram' in line for line in lines)


def test_a_changed_width_reports_both_the_old_and_new_keys_without_reviewing_them(tmp_path):
    sites = [{'site': 0x200, 'mode': 'store', 'width': 4}]
    subject, path = declared(tmp_path, sites)
    old = subject.config['reconciliation']['review'][0]
    next(iter(subject.symbols.values())).value = lambda key: 16 if key == 'width' else None
    text, lines = plan(subject, sites)
    assert text is None and OLD in path.read_text()
    assert any(old['claim_sha256'] in line and 'changed' in line for line in lines)
    assert any('not reviewed width' in line and 'new' in line for line in lines)


def test_another_layout_review_and_name_owners_are_unchanged(tmp_path):
    subject, path = declared(tmp_path)
    other = deepcopy(subject.config['reconciliation']['review'][0])
    other.update(layout='jk78c', subject='jk78c-ffff1000/ram', l0='0' * 16)
    subject.config['reconciliation']['review'].append(other)
    document = tomlkit.parse(path.read_text())
    document['reconciliation']['review'].append(other)
    path.write_text(tomlkit.dumps(document))
    text, _ = plan(subject)
    updated = tomlkit.parse(text)
    assert updated['reconciliation']['review'][1].unwrap() == other
    assert updated['names'] == document['names']


def test_custom_reasons_require_explicit_review_and_stay_verbatim(tmp_path):
    subject, path = declared(tmp_path)
    reason = 'The helper uses an indirect pointer at the declared call site.'
    subject.config['reconciliation']['review'][0]['reason'] = reason
    document = tomlkit.parse(path.read_text())
    document['reconciliation']['review'][0]['reason'] = reason
    path.write_text(tomlkit.dumps(document))
    text, lines = plan(subject)
    assert text is None and any('reason-review-required' in line for line in lines)
    assert any(reason in line for line in lines)
    text, lines = plan(subject, reasons_reviewed=True)
    updated = tomlkit.parse(text)['reconciliation']['review'][0].unwrap()
    assert updated == {**subject.config['reconciliation']['review'][0], 'l0': NEW}
    assert any('reviewed reason' in line and reason in line for line in lines)


def test_same_width_key_with_changed_provenance_is_not_transferred(tmp_path):
    sites = [{'site': 0x200, 'mode': 'store', 'width': 2}]
    subject, _ = declared(tmp_path, sites)
    next(iter(subject.symbols.values())).sources = {'kb/ram/another.toml'}
    text, lines = plan(subject, sites)
    assert text is None and any('binding-changed' in line for line in lines)


@pytest.mark.parametrize('changed', ('claim', 'duplicate', 'state', 'source-l0'))
def test_changed_claims_or_invalid_records_never_gain_an_updated_binding(tmp_path, changed):
    subject, path = declared(tmp_path)
    if changed == 'claim':
        subject.links[0].roles.append('different condition')
        text, lines = plan(subject)
        assert text is None and any('changed' in line for line in lines)
        return
    rows = subject.config['reconciliation']['review']
    if changed == 'duplicate':
        rows.append(deepcopy(rows[0]))
    elif changed == 'state':
        rows[0]['state'] = 'verified'
    else:
        rows[0]['l0'] = '0' * 16
    document = tomlkit.parse(path.read_text())
    document['reconciliation']['review'] = rows
    path.write_text(tomlkit.dumps(document))
    before = path.read_text()
    with pytest.raises(KbError):
        plan(subject)
    assert path.read_text() == before


def test_cli_dry_run_prints_the_diff_and_keeps_the_owner_on_disk(tmp_path):
    subject, path = declared(tmp_path)
    before = path.read_text()
    change = write.Change(subject, lambda ref: None, tmp_path)
    with export(NEW):
        change.run({'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD})
    output = io.StringIO()
    with patch.object(write, 'apply', return_value=(change, change.texts())) as apply, \
            contextlib.redirect_stdout(output):
        assert cli.main(['rebase-reviews', '--layout', '7mfk', '--from-l0', OLD,
                         '--reasons-reviewed', '--dry-run']) == 0
    assert f'-l0 = "{OLD}"' in output.getvalue()
    assert f'+l0 = "{NEW}"' in output.getvalue()
    assert path.read_text() == before
    assert apply.call_args.args[0] == [{'cmd': 'rebase-reviews', 'layout': '7mfk',
                                      'from_l0': OLD, 'reasons_reviewed': True}]
    assert apply.call_args.kwargs['dry_run'] is True


@pytest.mark.parametrize('dry_run', (False, True))
def test_supported_apply_checks_l0_before_writes_and_dry_run_does_not_sync(tmp_path, dry_run):
    subject, _ = declared(tmp_path)
    texts = {repo.OWNER_CONFIG: 'the planned owner text'}
    with patch.object(write.compile, 'build', return_value=subject), \
            patch.object(fingerprint, 'compute', return_value='stable'), \
            patch.object(write, 'plan', return_value=(SimpleNamespace(), texts, subject)), \
            patch.object(l0, 'check_all', return_value=[]) as check, \
            patch.object(write.graph, 'fresh') as fresh, \
            patch.object(write.graph, 'sync_held') as sync, \
            patch.object(write.store, 'write') as save:
        write.apply([{'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD}],
                    tmp_path, dry_run=dry_run)
    check.assert_called_once_with(tmp_path, only=['7mfk'])
    fresh.assert_not_called()
    assert save.call_count == sync.call_count == (0 if dry_run else 1)


def test_invalid_l0_refuses_writes_even_when_the_difference_would_reproduce(tmp_path):
    subject, _ = declared(tmp_path)
    with patch.object(write.compile, 'build', return_value=subject), \
            patch.object(fingerprint, 'compute', return_value='stable'), \
            patch.object(write, 'plan', return_value=(None, {}, subject)), \
            patch.object(l0, 'check_all', return_value=[
                l0.Failure('l0/7mfk', 'manifest', 'the normalized export differs', 'export it')]), \
            patch.object(write.store, 'write') as save:
        with pytest.raises(KbError, match='requires valid L0'):
            write.apply([{'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD}], tmp_path)
    save.assert_not_called()


def test_a_concurrent_export_or_claim_change_refuses_before_any_owner_write(tmp_path):
    subject, _ = declared(tmp_path)
    with patch.object(write.compile, 'build', return_value=subject), \
            patch.object(write, 'plan', return_value=(None, {repo.OWNER_CONFIG: 'text'}, subject)), \
            patch.object(fingerprint, 'compute', side_effect=['before', 'after']), \
            patch.object(l0, 'check_all', return_value=[]), \
            patch.object(write.store, 'write') as save, \
            patch.object(write.graph, 'sync_held') as sync:
        with pytest.raises(KbError, match='sources change') as caught:
            write.apply([{'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD}], tmp_path)
    assert caught.value.code == 6
    save.assert_not_called()
    sync.assert_not_called()


def test_rebasing_cannot_accept_claim_edits_in_the_same_batch():
    with pytest.raises(KbError, match='separately from native fact edits'):
        write.plan([{'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD},
                    {'cmd': 'set', 'ref': 'test/ram', 'keys': {'width': 16}}], None, None)


def test_primary_plan_compiles_the_updated_owner_without_mutating_native_facts(tmp_path):
    subject, path = declared(tmp_path)
    before = deepcopy(subject)

    def build(root, overlay):
        result = deepcopy(subject)
        result.overlay = overlay
        result.config['reconciliation'] = tomlkit.parse(
            overlay[repo.OWNER_CONFIG])['reconciliation'].unwrap()
        return result

    def issues(model):
        return {(item.check, item.subject, item.message): item
                for item in reconciliation.check(model)}

    with export(NEW), patch.object(write.compile, 'build', side_effect=build), \
            patch.object(write, '_issues', side_effect=issues):
        change, texts, result = write.plan(
            [{'cmd': 'rebase-reviews', 'layout': '7mfk', 'from_l0': OLD}],
            subject, write.model_resolver(subject), tmp_path)
        assert reconciliation.check(result) == []
    assert set(texts) == {repo.OWNER_CONFIG}
    assert result.links[0].props == before.links[0].props
    assert result.links[0].evidence == before.links[0].evidence
    assert result.config['reconciliation']['review'][0] == {
        **before.config['reconciliation']['review'][0], 'l0': NEW}
    assert subject.config == before.config and OLD in path.read_text()


@pytest.mark.parametrize('value', (None, 1, 'short', 'F' * 16, 'z' * 16))
def test_invalid_prior_digests_are_usage_errors(tmp_path, value):
    subject, _ = declared(tmp_path)
    with export(NEW), pytest.raises(KbError) as caught:
        reconciliation.rebase_export(subject, '7mfk', value)
    assert caught.value.code == 2


def test_multiple_layout_operations_keep_the_prior_operation_in_the_owner_overlay(tmp_path):
    subject, path = declared(tmp_path)
    foreign = deepcopy(subject.links[0])
    storage = foreign.owner.symbols.pop('7mfk')
    function = foreign.to.symbols.pop('7mfk')
    storage.key, storage.layout = SymbolKey('jk78c', 'ram', 0xffff1000), 'jk78c'
    function.key, function.layout = SymbolKey('jk78c', 'fn', 0x300), 'jk78c'
    foreign.owner.symbols['jk78c'] = storage
    foreign.to.symbols['jk78c'] = function
    subject.layouts['jk78c'] = SimpleNamespace(mcu='SH7058')
    subject.symbols.update({storage.key: storage, function.key: function})
    subject.links.append(foreign)
    with export(OLD):
        subject.config['reconciliation']['review'] = reconciliation.reviews(subject)
    document = tomlkit.parse(path.read_text())
    document['reconciliation']['review'] = subject.config['reconciliation']['review']
    path.write_text(tomlkit.dumps(document))

    def build(root, overlay):
        result = deepcopy(subject)
        result.overlay = overlay
        result.config['reconciliation'] = tomlkit.parse(
            overlay[repo.OWNER_CONFIG])['reconciliation'].unwrap()
        return result

    change = write.Change(subject, lambda ref: None, tmp_path)
    with export(NEW), patch.object(write.compile, 'build', side_effect=build):
        for layout in ('7mfk', 'jk78c'):
            change.run({'cmd': 'rebase-reviews', 'layout': layout, 'from_l0': OLD})
    updated = tomlkit.parse(change.texts()[repo.OWNER_CONFIG])['reconciliation']['review']
    assert len(updated) == 2 and all(record['l0'] == NEW for record in updated)
    assert all(record['l0'] == OLD for record in subject.config['reconciliation']['review'])
