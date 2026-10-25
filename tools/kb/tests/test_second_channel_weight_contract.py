"""Exact stock scope, complete raw inputs and declared-source preservation gates."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import second_channel_weight_contract as contract, second_channel_weight_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='controlled-second-channel-entry')


def test_published_counts_read_the_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    text = (repo.ROOT/'defs/JK08A.second-channel-weight.md').read_text()
    actual = (sum((r['end']-r['start'])//2 for r in source['unit']['code']), len(source['entries']),
        len(source['unit']['code']), len(source['unit']['pools']), len(source['unit']['aliases']),
        len(source['controlled_calibration']))
    match = re.search(r'binds (\d+) stock instructions in (\d+) actual entry path and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert match is not None and tuple(map(int,match.groups())) == actual == (524,1,9,42,8,49)
    root = sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x7A804 <= r['start'] < 0x7A998)
    assert int(re.search(r'entry has (\d+) instructions',text)[1]) == root == 196
    assert int(re.search(r'(\d+) stock entry paths',text)[1]) == len(source['stock_entry_paths']) == 8
    assert int(re.search(r'(\d+) raw ROM controls',text)[1]) == len(source['control_blobs']) == 2
    assert int(re.search(r'containing (\d+) bytes',text)[1]) == sum(r['size'] for r in source['control_blobs']) == 3
    for phrase, key, wanted in (('byte context','context_bytes',80), ('byte observer','observation_bytes',572),
                                ('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1]) == source[key] == wanted
    assert int(re.search(r'(\d+) independent context',text)[1]) == source['independent_context_fields'] == 20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1]) == source['complete_initial_final_RAM_bytes'] == 65536
    assert int(re.search(r'allocates (\d+) stack bytes',text)[1]) == source['outer_stack_bytes'] == 40


def test_published_word_domains_bind_the_physical_spans():
    source = contract.descriptor(repo.ROOT)
    text = (repo.ROOT/'defs/JK08A.second-channel-weight.md').read_text()
    inputs = {r['name']:r for r in source['input_blobs']}
    rows, columns = map(int,re.search(r'(\d+)x(\d+) uint16 surface',text).groups())
    assert (rows,columns) == (source['source_weight']['word_rows'],source['source_weight']['word_columns']) == (8,8)
    assert int(re.search(r'surface has (\d+) physical words',text)[1]) == source['source_weight']['words'] == 64
    assert inputs['weight_surface']['size'] == rows*columns*2
    assert int(re.search(r'one (\d+)-word physical span',text)[1]) == inputs['ordinary_curves']['size']//2 == 49
    assert int(re.search(r'one (\d+)-word physical span; the alternate curves\s*occupy one (\d+)-word',text)[2]) == inputs['alternate_curves']['size']//2 == 33
    assert int(re.search(r'occupy (\d+) physical words',text)[1]) == inputs['weight_axes']['size']//2 == 16
    assert int(re.search(r'(\d+)-word unsigned axis',text)[1]) == inputs['curve_axis']['size']//2 == 16
    assert int(re.search(r'Every one of (\d+) surface words',text)[1]) == source['source_weight']['words']


def test_fixture_preserves_all_stock_instructions_and_only_declared_pointer_aliases():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a != z} <= {
        i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    changed = bytearray(image)
    changed[0x7A804] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source,bytes(changed))


@pytest.mark.parametrize('fault',('wide-byte','wide-word','bool-mode','short-context',
    'short-surface','short-axes','short-curve','bad-SR','supplied-R5'))
def test_raw_input_refuses_width_loss_and_supplied_live_values(fault):
    value = case()
    if fault == 'wide-byte': value['byte_2c71'] = 256
    elif fault == 'wide-word': value['weight_surface'][0] = 65536
    elif fault == 'bool-mode': value['rom_83c1'] = True
    elif fault == 'short-context': value['context'].pop()
    elif fault == 'short-surface': value['weight_surface'].pop()
    elif fault == 'short-axes': value['weight_axes'].pop()
    elif fault == 'short-curve': value['ordinary_curves'].pop()
    elif fault == 'bad-SR': value['context'][18] = 2
    else: value['supplied_R5'] = 1
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_input_source_retains_raw_domains_and_complete_same_primary_originals():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows = matrix.cases(source,image)
    assert rows and all(set(r) == {*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    assert any(r['byte_2c71'] == 255 and len(r['weight_surface']) == 64 for r in rows)
    raw = matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R5' not in raw and 'expected_35f4' not in raw
    assert source['prior35F4_memory_is_input'] is False
    assert source['full_existing_same_primary_originals'] == ['word_interp_caller_withdrawal_paths','division_callees_paths']
    assert source['complete_inner_argument']['original_frame_high16_offset'] == 120
    assert source['actual_divisions']['second_divisor'] == 800
    assert source['actual_divisions']['second_multiplier'] == 727
    for name, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest() == wanted
