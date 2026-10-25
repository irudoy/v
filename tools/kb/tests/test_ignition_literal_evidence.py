"""C5 refusals mutate actual shared-primary observations and physical bindings."""

import hashlib
import json
import pytest

from kb import compile, copy_evidence, ignition_literal_evidence as evidence, repo, test_evidence


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['ignition_literals']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its original complete C5 primary record')
        pytest.skip('the original C5 primary record is not available')
    model = compile.build(repo.ROOT)
    accepted = evidence.require_primary(model, record)
    assert accepted['region'] == evidence.REGION
    assert accepted['reachability_proven'] is False
    assert accepted['computed_consumer_absence_proven'] is False
    assert accepted['stock_interpolation_body_executed'] is False
    assert accepted['hardware_qualification'] is False
    return model, record, packet


def rejected_packet(original, packet):
    model, record, _ = original
    with pytest.raises(ValueError):
        evidence.require_witness(model, packet, record['candidate']['producer_inputs'])


@pytest.mark.parametrize('field', ('consumed', 'declaration', 'reconstruction', 'map_blobs',
    'boundaries', 'stubs', 'simulator', 'toolchain', 'fixture_sha256', 'baseline_fixture_sha256',
    'composition_sha256', 'observer_object_sha256', 'elf_sha256'))
def test_actual_physical_binding_cannot_be_omitted(original, field):
    packet = dict(original[2])
    packet.pop(field)
    rejected_packet(original, packet)


@pytest.mark.parametrize('fault', ('admission', 'bool-schema', 'wrong-source', 'observer-stub',
                                  'boundary', 'failed-simulator', 'fixture', 'reconstruction'))
def test_actual_physical_binding_cannot_be_substituted(original, fault):
    packet = dict(original[2])
    if fault == 'admission':
        packet['semantic_admission'] = True
    elif fault == 'bool-schema':
        packet['schema'] = True
    elif fault == 'wrong-source':
        packet['consumed'] = {**packet['consumed'], evidence.SOURCES[0]: '00'}
    elif fault == 'observer-stub':
        packet['stubs'] = [{**row, 'bytes': '000b0009'} for row in packet['stubs']]
    elif fault == 'boundary':
        packet['boundaries'] = [{**row, 'bytes': '57f6442a000b0009'} for row in packet['boundaries']]
    elif fault == 'failed-simulator':
        packet['simulator'] = {**packet['simulator'], 'returncode': 1}
    elif fault == 'fixture':
        packet['fixture_sha256'] = '0' * 64
    else:
        packet['reconstruction'] = {**packet['reconstruction'], 'code': []}
    rejected_packet(original, packet)


def changed_observation(packet, field, byte):
    actual = dict(packet['observations'][0])
    data = bytearray.fromhex(actual[field])
    data[byte] ^= 1
    actual[field] = data.hex()
    observations = [actual, *packet['observations'][1:]]
    lines = packet['stdout'].splitlines()
    for index, line in enumerate(lines):
        if line.startswith(evidence.PREFIX):
            lines[index] = evidence.PREFIX + json.dumps(actual)
            break
    stdout = '\n'.join(lines) + '\n'
    return {**packet, 'observations': observations, 'stdout': stdout,
            'stdout_sha256': hashlib.sha256(stdout.encode()).hexdigest()}


@pytest.mark.parametrize('field,byte', (
    ('context', 31), ('context', 79),
    ('callee', 0), ('callee', 7), ('callee', 51), ('callee', 63), ('callee', 83), ('callee', 87),
    ('observation', 3), ('observation', 51), ('observation', 87), ('observation', 183),
    ('observation', 375), ('observation', 456), ('observation', 571),
    ('ram_before', 0x1234), ('ram_after', 0x1234), ('guards', 31),
))
def test_consistent_raw_stream_cannot_replace_independent_state_equations(original, field, byte):
    rejected_packet(original, changed_observation(original[2], field, byte))


@pytest.mark.parametrize('fault', ('missing', 'duplicate', 'reordered', 'typed-id', 'duplicate-json-key'))
def test_actual_invocation_identity_and_order_are_mandatory(original, fault):
    packet = dict(original[2])
    observations = list(packet['observations'])
    lines = packet['stdout'].splitlines()
    positions = [index for index, line in enumerate(lines) if line.startswith(evidence.PREFIX)]
    if fault == 'missing':
        observations.pop(0)
        lines.pop(positions[0])
    elif fault == 'duplicate':
        observations[1] = observations[0]
        lines[positions[1]] = lines[positions[0]]
    elif fault == 'reordered':
        observations[0], observations[1] = observations[1], observations[0]
        lines[positions[0]], lines[positions[1]] = lines[positions[1]], lines[positions[0]]
    elif fault == 'typed-id':
        observations[0] = {**observations[0], 'index': False}
        lines[positions[0]] = evidence.PREFIX + json.dumps(observations[0])
    else:
        lines[positions[0]] = lines[positions[0]][:-1] + ',"index":0}'
    packet['observations'] = observations
    packet['stdout'] = '\n'.join(lines) + '\n'
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    rejected_packet(original, packet)


@pytest.mark.parametrize('fault', ('failed', 'timeout', 'interrupted', 'subset', 'missing-packet', 'changed-original'))
def test_original_common_terminal_cannot_be_replaced(original, fault):
    model, held, _ = original
    record = {**held, 'terminal': dict(held['terminal']), 'candidate': dict(held['candidate'])}
    if fault == 'failed':
        record['terminal']['actual_exit_code'] = 1
    elif fault == 'timeout':
        record['terminal']['timed_out'] = True
    elif fault == 'interrupted':
        record['terminal']['interrupted'] = True
    elif fault == 'subset':
        record['candidate']['mode'] = 'subset'
    elif fault == 'missing-packet':
        record['candidate']['witness'] = {key: value for key, value in record['candidate']['witness'].items()
                                          if key != 'ignition_literals'}
    else:
        record['process_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        evidence.require_primary(model, record)


@pytest.mark.parametrize('fault', ('changed', 'new', 'removed', 'removed-config'))
def test_execution_consumption_requires_exact_sources_without_an_exclusion_option(fault):
    path = 'tools/sh-elf-run/harness-ignition-consumers.c'
    original = {path: '1' * 64, 'retained-publication-metadata.toml': '2' * 64}
    current = {path: '1' * 64}
    evidence.require_execution_inputs(original, current)
    if fault == 'changed':
        current[path] = '3' * 64
    elif fault == 'new':
        current['tools/sh-elf-run/new_consumer.py'] = '4' * 64
    elif fault == 'removed':
        original['tools/sh-elf-run/removed_consumer.py'] = '4' * 64
    else:
        original['patches/removed_layout.toml'] = '4' * 64
    with pytest.raises(ValueError):
        evidence.require_execution_inputs(original, current)


@pytest.mark.parametrize('field', ('selector', 'boundary', 'families', 'windows', 'paired_state_loads'))
def test_current_runtime_bindings_cannot_be_changed_by_source_provenance_reuse(original, field):
    packet = dict(original[2])
    declared = dict(packet['declaration'])
    if field == 'selector':
        declared[field] += 1
    elif field == 'boundary':
        declared[field] = {**declared[field], 'return_stack_offset': 20}
    else:
        declared[field] = list(declared[field])[:-1]
    packet['declaration'] = declared
    rejected_packet(original, packet)


def test_original_full_native_provenance_is_not_replaceable_by_a_current_source_subset(original):
    model, held, _ = original
    candidate = dict(held['candidate'])
    candidate['producer_inputs'] = evidence.execution_inputs(model.root)
    record = {**held, 'candidate': candidate}
    with pytest.raises(ValueError):
        evidence.require_primary(model, record)
