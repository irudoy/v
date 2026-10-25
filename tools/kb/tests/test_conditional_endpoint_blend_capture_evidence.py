"""Directed rounding, exact endpoint choice and complete physical-state refusal controls."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import conditional_endpoint_blend_contract as contract, conditional_endpoint_blend_matrix as matrix
from kb import conditional_endpoint_blend_semantics as numeric, conditional_endpoint_blend_transfers as transfers
from kb import conditional_endpoint_blend_capture_evidence as proof


def case(**updates):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value.update(updates)
    return value


def equations(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value))


def test_directed_word_rounding_preserves_the_distinct_downward_result():
    assert numeric.directed_word(0, 65535, 32768) == 32767
    assert numeric.directed_word(65535, 0, 32768) == 32768
    assert numeric.directed_word(10, 0, 1) == 10
    assert numeric.directed_word(0, 10, 1) == 0


def test_axis_exact_knots_bounds_and_duplicate_lower_knots():
    axis = tuple(matrix.DEFAULTS['axis_x'])
    assert numeric.position(axis, 0) == (0, 0)
    assert numeric.position(axis, 1000) == (0, 0)
    assert numeric.position(axis, 2750) == (0, 32768)
    assert numeric.position(axis, 65535) == (15, 0)
    assert numeric.position((1000, 1000, *axis[2:]), 1000) == (1, 0)


def test_maximum_weight_selects_B_exactly_instead_of_a_fractional_mix():
    profile = dict(surface_a=[0]*256, surface_b=[65535]*256, weight_step=0)
    selected = equations(case(**profile, word_2420=65535))
    blended = equations(case(**profile, word_2420=65534))
    assert (selected['output'], selected['branch']) == (32767, 'endpoint-b')
    assert (blended['output'], blended['branch']) == (32765, 'intermediate')
    assert equations(case(**profile, word_2420=1))['output'] == -32768


@pytest.mark.parametrize(('direction', 'prior', 'wanted'), ((0, 299, 0), (0, 300, 0), (0, 301, 1), (4, 65235, 65535), (4, 65236, 65535)))
def test_actual_weight_update_preserves_both_saturation_boundaries(direction, prior, wanted):
    assert equations(case(byte_245c=direction, word_2420=prior))['weight'] == wanted


def test_full_endpoint_register_is_distinct_from_the_stored_signed_word():
    value = equations(case(surface_a=[32768]*256))
    assert value['signed_a'] == 0 and value['publication_register_a'] == 0xFFFF0000
    assert value['memory'][0x18EC:0x18EE] == bytes(2)


def causal_observation(source):
    before, calibration = matrix.memory(source), matrix.input_calibrations(source)
    value = numeric.caller(before, calibration)
    return dict(entry=contract.ENTRY, context=matrix.context({}, source), memory_before=(before,), memory_after=(value['memory'],),
                calibration_before=calibration, bound_before=bytes(sum(row['size'] for row in contract.BOUND_SPANS)),
                frame_before=bytes(192), sp=0x30000000, continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0), value


@pytest.mark.parametrize('fault', ('RAM', 'other-surface', 'axis', 'context', 'frame', 'bound', 'ROM-gate', 'SP'))
def test_surface_held_key_rejects_a_change_to_any_other_complete_input(fault):
    first = causal_observation(case())[0]
    source = case()
    source['surface_a'][0] ^= 1
    second = causal_observation(source)[0]
    assert proof.held_key(first, 0xDE8E, 512, 'rom')[0] == proof.held_key(second, 0xDE8E, 512, 'rom')[0]
    if fault == 'RAM':
        raw = bytearray(second['memory_before'][0]); raw[0x88] ^= 1; second['memory_before'] = (bytes(raw),)
    elif fault in ('other-surface', 'axis'):
        address = 0xE08E if fault == 'other-surface' else 0x13D14
        raw = bytearray(second['calibration_before'][address]); raw[0] ^= 1; second['calibration_before'][address] = bytes(raw)
    elif fault == 'ROM-gate':
        second['calibration_before'][0x89FA]=b'\x40'
    elif fault == 'context':
        second['context'] = (second['context'][0] ^ 1, *second['context'][1:])
    elif fault == 'frame':
        second['frame_before'] = b'\x01' + second['frame_before'][1:]
    elif fault == 'bound':
        second['bound_before'] = b'\x01' + second['bound_before'][1:]
    else:
        second['sp'] += 4
    assert proof.held_key(first, 0xDE8E, 512, 'rom')[0] != proof.held_key(second, 0xDE8E, 512, 'rom')[0]


def reconstructed(**updates):
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source, value = contract.descriptor(repo.ROOT), case(word_1210=2750, word_10d2=2750)
    value.update(updates)
    fixture, _ = contract.fixture_for_case(source, image, value)
    context, sp, continuation = matrix.context(source, value), 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4, 'big') for index in range(48)))
    frame[160:164] = context[19].to_bytes(4, 'big')
    frame[164:168] = context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    before, calibration = matrix.memory(value), matrix.calibrations(source, image, value)
    result = state.execute(source, fixture, context, before, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(context=context, sp=sp, continuation=continuation, memory_before=(before,), calibration_before=calibration,
                    exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
                    frame_before=bytes(frame), frame_after=result['frame'], memory_after=(result['ram'],), sr_before=0)
    return observed, result, numeric.caller(before, calibration), fixture


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'other-RAM', 'helper-argument', 'physical-width', 'table-byte', 'wrapper-tail', 'live-register', 'returned-PR', 'scalar-only'))
def test_matching_word_does_not_replace_complete_calls_frame_operands_and_live_registers(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault == 'other-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0x88] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'helper-argument':
        call = next(row for row in result['calls'] if row['site'] == 0x76096)
        raw = list(call['entry']['registers']); raw[4] ^= 2; call['entry']['registers'] = tuple(raw)
    elif fault in ('physical-width', 'table-byte'):
        event = next(row for row in result['accesses'] if row['site'] == 0x26864)
        event['width_bytes' if fault == 'physical-width' else 'bytes'] = 1 if fault == 'physical-width' else '0000'
    elif fault == 'wrapper-tail':
        next(row for row in result['trace'] if row['site'] == 0x262D6)['delay_slot'] = False
    elif fault == 'live-register':
        value['publication_register_a'] ^= 0x10000
    elif fault == 'returned-PR':
        result['pr'] ^= 2
    else:
        value['value'] ^= 1
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('duplicate-key', 'context-after', 'short-bound', 'wrong-entry'))
def test_raw_stream_refuses_detached_complete_identity_context_or_bound_bytes(fault):
    source = case()
    declared = dict(cases=[source], calibration_spans=[[row['address'], row['size']] for row in contract.CONTROLLED_CALIBRATION],
                    bound_spans=[[row['address'], row['size']] for row in contract.BOUND_SPANS])
    context = b''.join(value.to_bytes(4, 'big') for value in matrix.context({}, source)).hex()
    calibration_size = sum(size for at, size in declared['calibration_spans'])
    bound_size = sum(size for at, size in declared['bound_spans'])
    row = dict(schema=1, index=0, entry=contract.ENTRY, context=context, context_after=context,
               observation=bytes(572).hex(), ram_before='65536:a5', ram_after='65536:a5',
               calibration_before=bytes(calibration_size).hex(), calibration_after=bytes(calibration_size).hex(),
               bound_before=bytes(bound_size).hex(), bound_after=bytes(bound_size).hex())
    marker = proof.MARKER+' status=PASS region='+proof.REGION+' cases=1'
    packet = dict(observations=[deepcopy(row)], marker=marker, stdout=proof.PREFIX+json.dumps(row)+'\n'+marker)
    assert len(proof.observations(packet, declared)) == 1
    if fault == 'context-after':
        row['context_after'] = bytes(80).hex()
    elif fault == 'short-bound':
        row['bound_after'] = '00'
    elif fault == 'wrong-entry':
        row['entry'] += 2
    packet['observations'] = [deepcopy(row)]
    packet['stdout'] = proof.PREFIX+json.dumps(row)+'\n'+marker
    if fault == 'duplicate-key':
        packet['stdout'] = packet['stdout'].replace('"schema": 1', '"schema": 1, "schema": 1', 1)
    with pytest.raises(ValueError):
        proof.observations(packet, declared)


@pytest.mark.parametrize(('first','second','branch'),((0x18,0x40,'gate-b-refusal'),(0x80,0x60,'gate-a-refusal'),(0xFF,0,'gate-a-refusal')))
def test_actual_disabled_ROM_controls_preserve_every_RAM_byte(first,second,branch):
    source=case(gate_8b3f=first,gate_89fa=second)
    value=equations(source)
    assert value['enabled'] is False and value['branch']==branch
    assert value['memory']==matrix.memory(source) and value['value']==source['prior_18e6']


@pytest.mark.parametrize('fault',('gate-byte','invented-call','other-RAM','live-register','full-SR'))
def test_disabled_path_requires_real_gate_reads_no_calls_and_complete_retained_state(fault):
    observed,result,value,fixture=reconstructed(gate_89fa=0x40)
    transfers.require(observed,result,value,fixture)
    if fault=='gate-byte':
        next(event for event in result['accesses'] if event['site']==0x76116)['bytes']='60'
    elif fault=='invented-call':
        result['calls'].append(dict(site=0x7611C,target=0x7604C))
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x18E6]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='live-register':
        raw=list(result['registers']);raw[2]^=1;result['registers']=tuple(raw)
        observed['exit']=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    else:
        result['sr']^=1
        observed['exit']=(result['sr'],*observed['exit'][1:])
    with pytest.raises(ValueError):
        transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize(('prior','direction','branch'),((0,0,'endpoint-a'),(65535,4,'endpoint-b'),(32768,0,'intermediate')))
def test_complete_active_paths_retain_actual_calls_weight_store_and_endpoint_register(prior,direction,branch):
    observed,result,value,fixture=reconstructed(word_2420=prior,byte_245c=direction)
    assert value['enabled'] is True and value['branch']==branch
    transfers.require(observed,result,value,fixture)
    assert result['macl']==observed['context'][17]
