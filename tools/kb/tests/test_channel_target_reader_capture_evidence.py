"""Adversarial full-state, physical-word and held-other admission controls."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import channel_target_reader_contract as contract, channel_target_reader_matrix as matrix
from kb import channel_target_reader_semantics as numeric, channel_target_reader_transfers as transfers
from kb import channel_target_reader_capture_evidence as proof


def case(index=1, word=100):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value['context'][4] = index
    value['input_words'][1] = word
    return value


@pytest.mark.parametrize(('word', 'wanted'), ((0, 8192), (1, 8208), (3583, 65520), (3584, 65535), (32768, 65535), (65535, 65535)))
def test_real_unsigned_word_and_saturation_boundaries(word, wanted):
    source = case(word=word)
    result = numeric.caller(matrix.memory(source), source['context'][4])
    assert result['value'] == wanted and result['source'] == 0x010028BE
    assert result['memory'][0x387C:0x387E] == wanted.to_bytes(2, 'big')


def test_full_low_byte_index_preserves_upper_input_bits_without_array_wrap():
    source = case(index=0xFFFFFFFF)
    result = numeric.caller(matrix.memory(source), source['context'][4])
    assert (result['index'], result['source'], result['destination'], result['owning_read']) == (255, 0x01002ABA, 0x01003A78, False)


def causal_observation(source):
    memory = matrix.memory(source)
    value = numeric.caller(memory, source['context'][4])
    return dict(entry=contract.ENTRY, context=matrix.context({}, source), memory_before=(memory,),
                memory_after=(value['memory'],), calibration_before={0xCB1FA: bytes.fromhex('01a2')},
                bound_before=bytes(56), frame_before=bytes(192), sp=0x30000000,
                continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0), value


def causal_pairs():
    return [causal_observation(case(index=index, word=word)) for index in (1, 0, 2, 255) for word in (100, 200)]


@pytest.mark.parametrize('fault', ('unrelated-RAM', 'calibration', 'context', 'frame', 'bound', 'SP', 'scalar-only'))
def test_owner_alternatives_require_actual_bytes_and_every_other_complete_input_fixed(fault):
    pairs = causal_pairs()
    assert proof.require_causal_alternatives(pairs)['actual_28BE_word_changes_output_with_other_inputs_fixed']
    observed, value = pairs[1]
    if fault == 'unrelated-RAM':
        raw = bytearray(observed['memory_before'][0]); raw[0x88] ^= 1; observed['memory_before'] = (bytes(raw),)
    elif fault == 'calibration':
        observed['calibration_before'][0xCB1FA] = bytes(2)
    elif fault == 'context':
        observed['context'] = (observed['context'][0] ^ 1, *observed['context'][1:])
    elif fault == 'frame':
        observed['frame_before'] = b'\x01' + observed['frame_before'][1:]
    elif fault == 'bound':
        observed['bound_before'] = b'\x01' + observed['bound_before'][1:]
    elif fault == 'SP':
        observed['sp'] += 4
    else:
        value['value'] ^= 1
    with pytest.raises(ValueError):
        proof.require_causal_alternatives(pairs)


def reconstructed():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source, value = contract.descriptor(repo.ROOT), case()
    fixture, _ = contract.fixture_for_case(source, image, value)
    context = matrix.context(source, value)
    sp, continuation = 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6 + index * 17).to_bytes(4, 'big') for index in range(48)))
    frame[160:164] = context[19].to_bytes(4, 'big')
    frame[164:168] = context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    before = matrix.memory(value)
    result = state.execute(source, fixture, context, before, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(context=context, sp=sp, continuation=continuation, memory_before=(before,),
                    exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
                    frame_before=bytes(frame), frame_after=result['frame'], memory_after=(result['ram'],), sr_before=0)
    return observed, result, numeric.caller(before, context[4]), fixture


@pytest.mark.parametrize('fault', ('exit-SR', 'frame-byte', 'other-RAM', 'read-address', 'physical-width', 'delay-slot', 'live-register', 'returned-PR', 'scalar-only'))
def test_matching_word_does_not_replace_full_physical_register_frame_and_return_state(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame-byte':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault == 'other-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0x88] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'read-address':
        next(row for row in result['accesses'] if row['site'] == 0xCB1D4)['address'] -= 2
    elif fault == 'physical-width':
        result['accesses'][-1]['width_bytes'] = 1
    elif fault == 'delay-slot':
        result['trace'][-1]['delay_slot'] = False
    elif fault == 'live-register':
        registers = list(result['trace'][-1]['before']['registers']); registers[6] ^= 1; result['trace'][-1]['before']['registers'] = tuple(registers)
    elif fault == 'returned-PR':
        result['pr'] ^= 2
    else:
        value['value'] ^= 1
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('duplicate-key', 'context-after', 'short-bound', 'wrong-entry'))
def test_complete_raw_stream_refuses_detached_context_identity_or_bound_snapshots(fault):
    source = case()
    declared = dict(cases=[source], calibration_spans=[[row['address'], row['size']] for row in contract.CONTROLLED_CALIBRATION],
                    bound_spans=[[row['address'], row['size']] for row in contract.BOUND_SPANS])
    context = b''.join(v.to_bytes(4, 'big') for v in matrix.context({}, source)).hex()
    row = dict(schema=1, index=0, entry=contract.ENTRY, context=context, context_after=context,
               observation=bytes(572).hex(), ram_before='65536:a5', ram_after='65536:a5',
               calibration_before=bytes(10).hex(), calibration_after=bytes(10).hex(),
               bound_before=bytes(56).hex(), bound_after=bytes(56).hex())
    marker = proof.MARKER + ' status=PASS region=' + proof.REGION + ' cases=1'
    packet = dict(observations=[deepcopy(row)], marker=marker, stdout=proof.PREFIX + json.dumps(row) + '\n' + marker)
    assert len(proof.observations(packet, declared)) == 1
    if fault == 'context-after':
        row['context_after'] = bytes(80).hex()
    elif fault == 'short-bound':
        row['bound_after'] = '00'
    elif fault == 'wrong-entry':
        row['entry'] += 2
    packet['observations'] = [deepcopy(row)]
    packet['stdout'] = proof.PREFIX + json.dumps(row) + '\n' + marker
    if fault == 'duplicate-key':
        packet['stdout'] = packet['stdout'].replace('"schema": 1', '"schema": 1, "schema": 1', 1)
    with pytest.raises(ValueError):
        proof.observations(packet, declared)
