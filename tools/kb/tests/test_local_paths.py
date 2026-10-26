"""Canonical artifact names and historical reads preserve storage boundaries."""

from pathlib import Path

import pytest

from kb import local_paths


MODES = ['native', 'internal', 'external', 'linked-parent']


def layout(tmp_path, mode):
    root = tmp_path / 'checkout'
    root.mkdir()
    if mode == 'native':
        physical = root / 'tmp/local-results'
        physical.mkdir(parents=True)
    elif mode == 'internal':
        physical = root / 'tmp/artifacts'
        physical.mkdir(parents=True)
        (root / 'tmp/local-results').symlink_to('artifacts', target_is_directory=True)
    elif mode == 'external':
        physical = tmp_path / 'data/local-results'
        physical.mkdir(parents=True)
        (root / 'tmp').mkdir()
        (root / 'tmp/local-results').symlink_to(physical, target_is_directory=True)
    else:
        physical = tmp_path / 'data/tmp/local-results'
        physical.mkdir(parents=True)
        (root / 'tmp').symlink_to(physical.parent, target_is_directory=True)
    return root, physical


@pytest.mark.parametrize('mode', MODES)
def test_owned_results_preserve_canonical_names_and_actual_bytes(tmp_path, mode):
    root, physical = layout(tmp_path, mode)
    file = physical / 'job/process.json'
    file.parent.mkdir()
    file.write_bytes(b'original evidence')
    logical = root / 'tmp/local-results/job/process.json'
    assert local_paths.results_root(root) == physical
    assert local_paths.owned(logical, root) == logical
    assert local_paths.owned('tmp/local-results/job/process.json', root) == logical
    assert local_paths.owned(file, root) == logical
    assert local_paths.relative(file, root) == 'tmp/local-results/job/process.json'
    assert logical.read_bytes() == b'original evidence'
    assert local_paths.container_directories(root) == ([] if mode == 'native' else [physical])
    assert not (root / 'local-results').exists()


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('destination', ['checkout', 'unrelated-disk'])
def test_nested_results_links_cannot_escape_even_into_the_checkout(tmp_path, mode, destination):
    root, physical = layout(tmp_path, mode)
    outside = root / 'other' if destination == 'checkout' else tmp_path / 'other-disk'
    outside.mkdir()
    (physical / 'escape').symlink_to(outside, target_is_directory=True)
    for path in (root / 'tmp/local-results/escape/new.json', physical / 'escape/new.json'):
        with pytest.raises(ValueError, match='escapes'):
            local_paths.owned(path, root)
    with pytest.raises(ValueError, match='escapes'):
        local_paths.read_path('local-results/escape/new.json', root)
    assert not (outside / 'new.json').exists()


def test_unrelated_paths_parent_traversal_and_prefix_lookalikes_are_not_owned(tmp_path):
    root, physical = layout(tmp_path, 'external')
    for path in (tmp_path / 'data/local-results-other/out.json', tmp_path / 'unrelated/out.json',
                 root / 'tmp/local-results/job/../out.json'):
        with pytest.raises(ValueError):
            local_paths.owned(path, root)
    (root / 'other-link').symlink_to(tmp_path / 'unrelated', target_is_directory=True)
    with pytest.raises(ValueError):
        local_paths.owned(root / 'other-link/out.json', root)
    assert local_paths.owned(root / 'ordinary-job/out.json', root) == root / 'ordinary-job/out.json'


@pytest.mark.parametrize('destination', ['absent', 'checkout', 'ancestor', 'loop', 'absent-parent'])
def test_unavailable_or_overbroad_results_root_fails_before_creating_output(tmp_path, destination):
    root = tmp_path / 'checkout'
    root.mkdir()
    if destination == 'absent-parent':
        (root / 'tmp').symlink_to(tmp_path / 'missing-disk', target_is_directory=True)
    else:
        (root / 'tmp').mkdir()
        target = {'absent': tmp_path / 'missing-disk', 'checkout': root,
                  'ancestor': tmp_path, 'loop': root / 'tmp/local-results'}[destination]
        (root / 'tmp/local-results').symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError):
        local_paths.owned(root / 'tmp/local-results/job/out.json', root)
    assert not (tmp_path / 'missing-disk').exists()


@pytest.mark.parametrize('mode', MODES)
def test_historical_names_are_read_only_aliases_without_a_root_link(tmp_path, mode):
    root, physical = layout(tmp_path, mode)
    (physical / 'original.json').write_bytes(b'historical bytes')
    for path in ('local-results/original.json', root / 'local-results/original.json'):
        assert local_paths.read_path(path, root).read_bytes() == b'historical bytes'
        with pytest.raises(ValueError, match='must use tmp/local-results'):
            local_paths.owned(path, root)
    (root / 'source.txt').write_bytes(b'input')
    assert local_paths.read_path('source.txt', root).read_bytes() == b'input'
    for path in ('local-results/../outside', 'tmp/local-results/../outside'):
        with pytest.raises(ValueError, match='parent'):
            local_paths.read_path(path, root)
    assert not (root / 'local-results').exists()
