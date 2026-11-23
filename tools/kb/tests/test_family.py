"""Bounded comment-preserving onboarding contracts without stock execution."""

from copy import deepcopy
import tomllib

import pytest

from kb import cli, family, repo
from kb.repo import KbError


SOURCE = '''schema_version = 1
# Keep the analysis comment.
[analysis]
window_size = 64 # Keep this inline comment.

[family.existing]
kind = "distinct-code"
members = ["OLD"] # Keep the members comment.
canonical = "OLD"
mcu = "SH7058"
flash_size = 0x100000
software_ids = ["OLDID"]
same_address_inheritance = false
layouts = { old = "OLD" }
evidence = "Original evidence."

[[relationship]]
left_family = "existing"
right_family = "other"
evidence = "Retained relation."
'''
METADATA = dict(kind='distinct-code', mcu='SH7059', flash_size=0x180000,
                software_ids=['NEWID'])


def prepare(operation='new', family_id='new_family', image='NEW', layout='new'):
    return family.prepared(SOURCE, operation, family_id=family_id, image=image,
                           layout=layout, evidence='Exact source report digest.',
                           metadata=METADATA)


def test_new_family_preserves_unrelated_content_and_starts_with_its_own_layout():
    text = prepare()
    document = tomllib.loads(text)
    assert document['family']['existing'] == tomllib.loads(SOURCE)['family']['existing']
    assert document['relationship'] == tomllib.loads(SOURCE)['relationship']
    assert '# Keep the analysis comment.' in text
    assert 'window_size = 64 # Keep this inline comment.' in text
    assert 'members = ["OLD"] # Keep the members comment.' in text
    assert document['family']['new_family']['layouts'] == {'new': 'NEW'}
    assert not document['family']['new_family']['same_address_inheritance']


def test_adding_a_noninheriting_image_keeps_existing_evidence_and_comments():
    text = prepare('add', family_id='existing')
    row = tomllib.loads(text)['family']['existing']
    assert row['members'] == ['OLD', 'NEW']
    assert row['layouts'] == {'old': 'OLD', 'new': 'NEW'}
    assert row['evidence'] == 'Original evidence. Exact source report digest.'
    assert '# Keep the members comment.' in text


@pytest.mark.parametrize('arguments', [
    {'image': 'OLD'}, {'layout': 'old'}, {'layout': 'fn'}, {'layout': 'INVALID'},
    {'operation': 'new', 'family_id': 'existing'},
    {'operation': 'add', 'family_id': 'missing'},
    {'operation': 'add', 'family_id': 'existing', 'layout': None},
])
def test_conflicting_identity_and_missing_layouts_refuse(arguments):
    with pytest.raises(KbError):
        prepare(**arguments)


def test_exact_code_addition_retains_one_layout():
    source = SOURCE.replace('same_address_inheritance = false', 'same_address_inheritance = true')
    text = family.prepared(source, 'add', family_id='existing', image='NEW',
                           layout=None, evidence='Independent exact-code evidence.')
    row = tomllib.loads(text)['family']['existing']
    assert row['layouts'] == {'old': 'OLD'}
    with pytest.raises(KbError):
        family.prepared(source, 'add', family_id='existing', image='NEW',
                        layout='new', evidence='Independent exact-code evidence.')


def test_layout_overlay_is_read_without_changing_the_primary_registry(tmp_path):
    path = tmp_path / repo.HOMOLOGY
    path.parent.mkdir(parents=True)
    path.write_text(SOURCE)
    original = path.read_bytes()
    layouts = repo.layouts(tmp_path, {repo.HOMOLOGY: prepare()})
    assert set(layouts) == {'old', 'new'}
    assert layouts['new'].image == 'NEW'
    assert path.read_bytes() == original


def test_family_parser_has_explicit_stock_identity_and_dry_run():
    args = cli.build_parser().parse_args([
        'family', 'new', 'new_family', '--image', 'NEW', '--layout', 'new',
        '--census', 'defs/registries/OLD-NEW.census-correspondence.csv', '--mcu', 'SH7059',
        '--flash-size', '0x180000', '--software-id', 'NEWID', '--dry-run'])
    assert args.dry_run and args.flash_size == 0x180000
