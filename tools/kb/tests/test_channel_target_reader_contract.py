"""Complete source scope and refusals for lossy raw inputs or altered fixtures."""
from copy import deepcopy
from pathlib import Path
import re
import pytest
from kb import repo
from kb import channel_target_reader_contract as contract, channel_target_reader_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='complete-source-contract')


def test_published_scope_counts_read_the_exact_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    counts = (sum((row['end'] - row['start']) // 2 for row in source['unit']['code']),
              sum(row['end'] - row['start'] for row in source['unit']['code']),
              len(source['unit']['code']), len(contract.FUNCTIONS))
    text = (Path(repo.ROOT) / 'defs/JK08A.channel-target-reader.md').read_text()
    published = re.search(r'binds (\d+) stock instructions, (\d+) instruction bytes,\s+(\d+) contiguous span, and (\d+) complete source body', text)
    assert published and tuple(map(int, published.groups())) == counts == (23, 46, 1, 1)
    pools = re.search(r'binds (\d+) literal pools, (\d+) four-byte RAM pointer\s+aliases, and (\d+) calibration spans', text)
    assert pools and tuple(map(int, pools.groups())) == (len(source['unit']['pools']), len(source['unit']['aliases']), len(source['controlled_calibration']))
    domain = re.search(r'The uint8 index domain contains (\d+) raw values', text)
    assert domain and int(domain[1]) == 1 << source['physical_read']['index_bits']
    assert source['entries'] == [0xCB1CA]
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)
    assert source['physical_read']['site'] == 0xCB1D4 and source['physical_store']['site'] == 0xCB1F6


def test_fixture_retains_every_instruction_and_changes_only_two_declared_pointer_pools():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    fixture, aliases = contract.independent_fixture(source, image)
    allowed = {at for row in aliases for at in range(row['address'], row['address'] + 4)}
    assert {at for at, (a, b) in enumerate(zip(image, fixture)) if a != b} <= allowed
    assert fixture[0xCB1CA:0xCB1F8] == image[0xCB1CA:0xCB1F8]
    assert fixture[0xCB1FA:0xCB1FC] == bytes.fromhex('01a2')
    assert {row['original'] for row in aliases} == {0xFFFF2898, 0xFFFF36D8}
    changed = bytearray(image)
    changed[0xCB1F6] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(changed))


@pytest.mark.parametrize('fault', ('boolean-word', 'short-input-array', 'wide-word', 'short-context', 'bad-SR', 'supplied-result'))
def test_raw_inputs_refuse_width_loss_truncation_and_supplied_results(fault):
    value = case()
    if fault == 'boolean-word':
        value['input_words'][1] = True
    elif fault == 'short-input-array':
        value['input_words'].pop()
    elif fault == 'wide-word':
        value['prior_words'][255] = 65536
    elif fault == 'short-context':
        value['context'].pop()
    elif fault == 'bad-SR':
        value['context'][18] = 2
    else:
        value['expected_word'] = 65535
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_private_header_transports_complete_inputs_without_expected_arithmetic():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    text = matrix.header(dict(source=source, cases=[case()]), image).decode()
    assert 'input_words[256],prior_words[256]' in text and 'struct context context' in text
    assert not any(word in text for word in ('expected', 'saturated', 'scaled'))
