"""Fixed source-bound uncertainty and permanent-name owner contracts."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from kb import names, reconciliation, repo
from kb.adapters import dids
from kb.model import SymbolKey


def model():
    storage = SimpleNamespace(key=SymbolKey('7mfk', 'ram', 0xffff1000), layout='7mfk',
        kind='ram', sources={'kb/ram/test.toml'}, value=lambda key: 8 if key == 'width' else None)
    function = SimpleNamespace(key=SymbolKey('7mfk', 'fn', 0x200), layout='7mfk',
        kind='fn', value=lambda key: None)
    owner = SimpleNamespace(key='test/ram', symbols={'7mfk': storage})
    target = SimpleNamespace(key='caller/fn', symbols={'7mfk': function})
    link = SimpleNamespace(owner=owner, to=target, type='writer', slot=None, offset=None,
        roles=['store'], props={}, evidence=[], stated=['7mfk'], sources={'kb/ram/test.toml'})
    return SimpleNamespace(root=repo.ROOT, symbols={storage.key: storage, function.key: function},
        layouts={'7mfk': SimpleNamespace(mcu='SH7058')}, spaces={'SH7058': {}},
        links=[link], config={'reconciliation': {'enabled': True}})


def observed(subject, sites):
    function = '7mfk:00000200'
    storage = '7mfk:ffff1000'
    return ({(function, storage): sites}, {storage: [(function, site) for site in sites]})


def run(subject, sites, operation):
    with patch.object(reconciliation, 'accesses', return_value=observed(subject, sites)), \
         patch.object(reconciliation.match, 'l0_digest', return_value='0123456789abcdef'):
        return operation(subject)


def test_missing_store_requires_exact_unresolved_record():
    subject = model()
    assert len(run(subject, [], reconciliation.check)) == 1
    subject.config['reconciliation']['review'] = run(subject, [], reconciliation.reviews)
    assert run(subject, [], reconciliation.check) == []
    assert subject.links[0].evidence == []
    assert subject.config['reconciliation']['review'][0]['state'] == 'unresolved'


@pytest.mark.parametrize('changed', ['claim', 'l0', 'reason', 'state', 'duplicate'])
def test_stale_or_invalid_review_refuses(changed):
    subject = model()
    held = run(subject, [], reconciliation.reviews)
    if changed == 'claim':
        subject.links[0].roles.append('new')
    elif changed == 'l0':
        held[0]['l0'] = 'fedcba9876543210'
    elif changed == 'reason':
        held[0]['reason'] = ' '
    elif changed == 'state':
        held[0]['state'] = 'verified'
    else:
        held.append(deepcopy(held[0]))
    subject.config['reconciliation']['review'] = held
    assert run(subject, [], reconciliation.check)


def test_reproduced_store_retires_old_exception_instead_of_leaving_it_accepted():
    subject = model()
    subject.config['reconciliation']['review'] = run(subject, [], reconciliation.reviews)
    found = run(subject, [{'site': 0x200, 'mode': 'store', 'width': 1}], reconciliation.check)
    assert len(found) == 1 and 'no longer reproduces' in found[0].message


def test_wider_access_does_not_change_declared_width():
    subject = model()
    site = [{'site': 0x200, 'mode': 'store', 'width': 2}]
    subject.config['reconciliation']['review'] = run(subject, site, reconciliation.reviews)
    assert subject.config['reconciliation']['review'][0]['kind'] == 'width'
    assert run(subject, site, reconciliation.check) == []
    assert next(iter(subject.symbols.values())).value('width') == 8


def name_model():
    row = names.Row('7mfk', 'tbl', 0x100, 'active-otter')
    document = dict(layout='7mfk', kind='tbl', address='00000100', name=row.name,
                    former=[], reason='Permanent reservation of the original registry name.')
    return SimpleNamespace(names=[row], symbols={}, config={
        'names': {'owners_checked': True, 'reserved': [document]}})


def test_exact_inactive_name_owner_passes():
    assert names.owner_check(name_model()) == []


@pytest.mark.parametrize('changed', ['name', 'missing', 'reason', 'active'])
def test_inactive_name_owner_cannot_accept_a_new_identity(changed):
    subject = name_model()
    if changed == 'name':
        subject.config['names']['reserved'][0]['name'] = 'another-otter'
    elif changed == 'missing':
        subject.config['names']['reserved'] = []
    elif changed == 'reason':
        subject.config['names']['reserved'][0]['reason'] = ''
    else:
        subject.symbols[SymbolKey(*subject.names[0].key)] = SimpleNamespace(
            sources={dids.DECODER.as_posix()})
    assert names.owner_check(subject)


def test_decoder_only_name_has_its_existing_primary_owner():
    subject = name_model()
    subject.config['names']['reserved'] = []
    subject.symbols[SymbolKey(*subject.names[0].key)] = SimpleNamespace(
        sources={dids.DECODER.as_posix()})
    assert names.owner_check(subject) == []
