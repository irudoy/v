"""Bounded transfer contracts preserve lanes and reject wider semantic claims."""

from copy import deepcopy

import pytest

from kb import packed_transfer_evidence as contract, packed_transfer_matrix as matrix, repo


@pytest.fixture(scope='module')
def declared():
    return contract.descriptor(repo.ROOT)


@pytest.fixture(scope='module')
def images():
    return {rom: image.path.read_bytes() for rom, image in repo.images().items()
            if rom in {row[0] for row in contract.LAYOUTS.values()}}


@pytest.mark.parametrize('key', tuple(contract.WINDOWS))
def test_explicit_window_retains_each_byte_and_neighbor_without_width_inference(declared, images, key):
    window = next(row for row in declared['window'] if row['key'] == key)
    case = {**matrix.cases(declared, key)[0], 'pattern': 0x80FF if key != '1me3b-timing-history'
            and key != '1nd-timing-history' else 0x80FF017F}
    context = matrix.entry(window, case)
    before = matrix.memory(declared, key, case)
    result = contract.execute(window, images[window['rom']], context, before)
    for field in declared['field']:
        if not any(row['window'] == key for row in field['transfer']):
            continue
        conclusions = contract.require_lanes(field, window, result, before)
        for row in conclusions:
            width = row['physical_width_bytes']
            expected = case['pattern'].to_bytes(width, 'big')
            assert row['retained_field_byte'] == expected[0]
            assert row['neighboring_bytes'] == expected[1:].hex()
            assert row['declared_field_bits'] == 8
            assert row['semantic_width_inference'] is False
            assert row['publication_width_inference'] is False
            assert row['natural_entry_proven'] is False


@pytest.mark.parametrize('key', ('1me3b-mask-history', '1nd-mask-history'))
def test_mask_window_models_the_real_callee_between_literal_and_access(declared, images, key):
    window = next(row for row in declared['window'] if row['key'] == key)
    case = matrix.cases(declared, key)[3]
    context = matrix.entry(window, case)
    before = matrix.memory(declared, key, case)
    result = contract.execute(window, images[window['rom']], context, before)
    call = window['copy_callee']
    start, end = call['destination'] - contract.RAM_BASE, call['source'] - contract.RAM_BASE
    assert result['ram'][start:start + call['length_bytes']] == before[end:end + call['length_bytes']]
    assert result['registers'][1] == call['destination'] + call['length_bytes']
    assert result['registers'][2] == call['source']
    assert result['registers'][10] == (0x010092AC if window['layout'] == '1me3b' else 0x010092E0)
    assert result['registers'][10] != context[10]
    assert result['saved_frame'] == b''.join(context[index].to_bytes(4, 'big') for index in (4, 3, 2))
    assert result['sr_clear_t'] is True
    assert result['natural_callee_in_scope'] is True


@pytest.mark.parametrize('fault', ('access-site', 'source', 'destination', 'width', 'data-register', 'instruction'))
def test_wrong_physical_transfer_cannot_explain_a_byte_field(declared, images, fault):
    field = deepcopy(next(row for row in declared['field'] if row['layout'] == 'jk78c'))
    transfer = field['transfer'][0]
    key = transfer['window']
    window = next(row for row in declared['window'] if row['key'] == key)
    case = matrix.cases(declared, key)[2]
    before = matrix.memory(declared, key, case)
    result = contract.execute(window, images[window['rom']], matrix.entry(window, case), before)
    if fault == 'access-site':
        transfer['read'] += 2
    elif fault == 'source':
        transfer['source'] += 1
    elif fault == 'destination':
        transfer['destination'] += 2
    elif fault == 'width':
        transfer['physical_width_bytes'] = 1
    elif fault == 'data-register':
        transfer['data_register'] = 0
    else:
        transfer['retained_read_bytes'] = '6270'
    with pytest.raises(ValueError):
        contract.require_lanes(field, window, result, before)


@pytest.mark.parametrize('fault', ('callee-byte', 'callee-register', 'length-delay', 'entry-source', 'entry-destination'))
def test_natural_copy_preservation_has_no_assumed_post_call_base(declared, images, fault):
    window = next(row for row in declared['window'] if row['key'] == '1me3b-mask-history')
    case = matrix.cases(declared, window['key'])[0]
    image = bytearray(images[window['rom']])
    context = list(matrix.entry(window, case))
    call = window['copy_callee']
    if fault == 'callee-byte':
        image[call['entry'] + 6] ^= 1
    elif fault == 'callee-register':
        image[call['call']] = 0x46
    elif fault == 'length-delay':
        image[call['call'] + 3] ^= 1
    elif fault == 'entry-source':
        context[2] += 1
    else:
        context[1] += 1
    with pytest.raises(ValueError):
        contract.execute(window, bytes(image), tuple(context), matrix.memory(declared, window['key'], case))


def test_word_load_sign_extension_is_separate_from_preserved_byte_lanes(declared, images):
    key = 'jk78c-cvtc-history'
    window = next(row for row in declared['window'] if row['key'] == key)
    case = {**matrix.cases(declared, key)[0], 'pattern': 0x80FF}
    before = matrix.memory(declared, key, case)
    result = contract.execute(window, images[window['rom']], matrix.entry(window, case), before)
    assert result['registers'][2] == 0xFFFF80FF
    assert result['ram'][0x2276:0x2278] == bytes.fromhex('80ff')
    assert result['ram'][0x227E:0x2280] == bytes.fromhex('80ff')
    assert result['ram'][0x227A:0x227C] == bytes.fromhex('80ff')
