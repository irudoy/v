"""Complete source scope, raw-word input and immutable fixture refusal controls."""
from copy import deepcopy
from pathlib import Path
import re
import pytest
from kb import repo
from kb import conditional_endpoint_blend_contract as contract, conditional_endpoint_blend_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='complete-source-contract')


def test_published_counts_read_the_exact_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    counts = (sum((row['end']-row['start'])//2 for row in source['unit']['code']),
              sum(row['end']-row['start'] for row in source['unit']['code']), len(source['unit']['code']), len(contract.FUNCTIONS))
    text = (Path(repo.ROOT) / 'defs/JK08A.conditional-endpoint-blend.md').read_text()
    published = re.search(r'binds (\d+) stock instructions, (\d+) instruction bytes,\s+(\d+) contiguous spans, and (\d+) complete source bodies', text)
    assert published and tuple(map(int, published.groups())) == counts == (343, 686, 8, 8)
    pools = re.search(r'binds (\d+) literal pools, (\d+) four-byte RAM pointer\s+aliases, and (\d+) calibration spans', text)
    assert pools and tuple(map(int, pools.groups())) == (len(source['unit']['pools']), len(source['unit']['aliases']), len(source['controlled_calibration']))
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)
    assert source['entries'] == [0x76108]
    assert {row['table'] for row in source['actual_endpoints']} == {0xDE8E, 0xE08E}
    assert source['actual_blend']['maximum_weight_selects_B_exactly'] is True
    step = next(row for row in source['control_blobs'] if row['name'] == 'weight_step')
    published_step = re.search(r'The stock weight step is (\d+)', text)
    assert published_step and int(published_step[1]) == int(step['stock_hex'], 16)


def test_fixture_preserves_full_instructions_and_changes_only_declared_pointer_aliases():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    fixture, aliases = contract.independent_fixture(source, image)
    allowed = {at for row in aliases for at in range(row['address'], row['address']+4)}
    assert {at for at, (a, b) in enumerate(zip(image, fixture)) if a != b} <= allowed
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    changed = bytearray(image)
    changed[0x7611E] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(changed))


@pytest.mark.parametrize('fault', ('boolean-word', 'short-surface', 'wide-axis', 'short-context', 'bad-SR', 'boolean-gate', 'wide-gate', 'supplied-output'))
def test_raw_input_contract_refuses_truncation_width_loss_or_expected_outputs(fault):
    value = case()
    if fault == 'boolean-word':
        value['word_1210'] = True
    elif fault == 'short-surface':
        value['surface_a'].pop()
    elif fault == 'wide-axis':
        value['axis_y'][15] = 65536
    elif fault == 'short-context':
        value['context'].pop()
    elif fault == 'bad-SR':
        value['context'][18] = 2
    elif fault == 'boolean-gate':
        value['gate_89fa'] = True
    elif fault == 'wide-gate':
        value['gate_8b3f'] = 256
    else:
        value['expected_endpoint'] = 0
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_private_header_supplies_complete_inputs_without_signed_blend_results():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    text = matrix.header(dict(source=source, cases=[case()]), image).decode()
    assert 'struct context context' in text and 'uint32_t ram[9]' in text
    assert not any(word in text for word in ('expected', 'signed_a', 'signed_b', 'quotient'))


def test_published_stock_ROM_gate_bytes_come_from_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=(Path(repo.ROOT)/'defs/JK08A.conditional-endpoint-blend.md').read_text()
    match=re.search(r'Stock ROM8\[00008B3F\]=0x([0-9a-fA-F]+) and ROM8\[000089FA\]=0x([0-9a-fA-F]+)',text)
    controls={row['name']:int(row['stock_hex'],16) for row in source['control_blobs']}
    assert match and tuple(int(x,16) for x in match.groups())==(controls['gate_8b3f'],controls['gate_89fa'])
    assert source['actual_entry_gates']==[
        dict(site=0x7610E,address=0x8B3F,mask=0x80,required_clear=True),
        dict(site=0x76116,address=0x89FA,mask=0x20,required_set=True)]
