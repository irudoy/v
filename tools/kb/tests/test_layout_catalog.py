"""Bounded source-coverage and candidate-channel contracts."""

from copy import deepcopy
from types import SimpleNamespace
import tomllib

import pytest

from kb import catalog, cli, mcp, store, suggest
from kb.model import Entity, SymbolKey, Target
from kb.match import Candidate, Search
from kb.repo import KbError


def row(name, concept='', vendor='ecutek'):
    return {**dict.fromkeys(catalog.COLUMNS, ''), 'name': name, 'concept': concept,
            'vendor': vendor, 'doc': 'document', 'origin': 'patch'}


def model(inventory):
    entities, targets = {}, {}
    for slug, document in catalog.documents(inventory, ['home', 'other']).items():
        document = deepcopy(document)
        target_rows = document.pop('target')
        entity = Entity('feature', slug, props=document)
        entities['feature', slug] = entity
        for item in target_rows:
            targets[slug, item['layout']] = Target(slug, item['layout'], status=item['status'])
    return SimpleNamespace(entities=entities, targets=targets,
                           layouts={'home': None, 'other': None})


def test_only_explicit_concepts_join_and_each_source_row_is_preserved():
    inventory = [row('First', 'shared'), row('Second', 'shared', 'uprev'), row('Unrelated')]
    found = model(inventory)
    assert len(found.entities) == 2
    assert catalog.check(found, inventory) == []
    for entity in found.entities.values():
        assert entity.props['requirements_state'] == 'unresolved'
        assert entity.props.get('requires', []) == []
    assert sum(len(item.props['catalog']) for item in found.entities.values()) == 3


@pytest.mark.parametrize('failure', ['source', 'duplicate', 'missing', 'target', 'bound'])
def test_lost_source_coverage_or_unsupported_binding_claims_refuse(failure):
    inventory = [row('First', 'shared'), row('Second', 'shared')]
    found = model(inventory)
    entity = found.entities['feature', 'parity_shared']
    if failure == 'source':
        entity.props['catalog'][0]['original'] = '{}'
    elif failure == 'duplicate':
        entity.props['catalog'][1]['order'] = 0
    elif failure == 'missing':
        entity.props['catalog'].pop()
    elif failure == 'target':
        found.targets.pop(('parity_shared', 'other'))
    else:
        entity.props['requirements_state'] = 'bound'
    assert catalog.check(found, inventory)


def test_catalog_report_exposes_planned_targets_and_unresolved_requirements():
    found = model([row('Unverified behavior', 'shared')])
    answer = catalog.report(found)
    assert answer.data['unresolved_requirements'] == 1
    assert answer.data['features'][0]['targets'] == {'home': 'planned', 'other': 'planned'}
    assert 'requirements unresolved' in answer.text()
    assert 'acceptance:' in answer.text()


def test_catalog_canonical_form_keeps_full_source_text_and_all_targets():
    document = next(iter(catalog.documents([row('Name, punctuation')], ['home', 'other']).values()))
    assert tomllib.loads(store.render('feature', document)) == document


def test_duplicate_entry_identity_and_colliding_concepts_refuse():
    with pytest.raises(KbError):
        catalog.documents([row('Same'), row('Same')], ['home'])
    with pytest.raises(KbError):
        catalog.documents([row('First', 'same-concept'), row('Second', 'same_concept')], ['home'])


def test_independent_channels_keep_distinct_evidence_and_never_promote_candidates():
    origin = SimpleNamespace(key=SymbolKey('home', 'fn', 0x100))
    first = {'kind': 'function-match', 'at': 'other:00000200', 'value': 'exact_sha256'}
    second = {'kind': 'masked-match', 'at': 'other:00000202', 'value': 8}
    result = Search(origin, 'other', 'masked-match',
                    {0x200: Candidate(0x200, first, 3, [first, first, second])})
    channels = suggest.symbol_channels(result)
    assert set(channels) == {'function-match', 'masked-match'}
    assert channels['function-match'][0]['evidence'] == [first]
    assert channels['masked-match'][0]['evidence'] == [second]
    assert all(item['producer'] == 'candidate' for rows in channels.values() for item in rows)


def test_empty_search_has_no_invented_alternative_channel():
    assert suggest.symbol_channels(Search('source', 'other', 'masked-match')) == {}


def test_symbol_and_block_syntax_share_read_only_mcp_without_required_reference():
    parser = cli.build_parser()
    assert parser.parse_args(['suggest', 'home:00000100', '--layout', 'other']).ref == 'home:00000100'
    assert parser.parse_args(['suggest', '--blocks', '--layout', 'other']).ref is None
    schema = {tool['name']: tool['inputSchema'] for tool in mcp.tools(parser)}['kb_suggest']
    assert schema['required'] == ['layout']
    assert mcp.argv('suggest', {'ref': 'home:00000100', 'layout': 'other'}) == [
        'suggest', 'home:00000100', '--layout', 'other']
    assert parser.parse_args(['gaps', '--catalog']).catalog
