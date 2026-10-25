"""Generated standard transport retains exact bounded input responsibilities."""

from copy import deepcopy
import json

import pytest

from kb import proof_adapter, repo, ignition_literal_evidence
from kb import closed_loop_coolant_access_contract, maf_record_contract, rpm_remaining_inhibit_contract
from kb import ordinary_access_registry as registry


@pytest.mark.parametrize('path', proof_adapter.DESCRIPTORS)
def test_source_generation_is_deterministic_current_and_manifest_bound(path):
    first = proof_adapter.generated(repo.ROOT, path)
    assert first == proof_adapter.generated(repo.ROOT, path)
    proof_adapter.require_generated(repo.ROOT, path)
    assert set(first) <= set(proof_adapter.source_files(repo.ROOT, path))
    inputs = ignition_literal_evidence.execution_inputs(repo.ROOT)
    for source in proof_adapter.source_files(repo.ROOT, path):
        assert inputs[source] == proof_adapter.digest((repo.ROOT/source).read_bytes())
    assert {proof_adapter.SOURCE, 'tools/kb/src/kb/proof_transport.py',
        'tools/kb/tests/proof_adapter_cases.py', 'tools/kb/tests/test_proof_adapter.py',
        *first} <= set(registry.EXECUTION_FILES)


@pytest.mark.parametrize('path', proof_adapter.DESCRIPTORS)
def test_stale_generated_driver_or_refusal_source_refuses(tmp_path, path):
    source = tmp_path/path;source.parent.mkdir(parents=True)
    source.write_bytes((repo.ROOT/path).read_bytes())
    outputs = proof_adapter.generated(repo.ROOT, path)
    for output, data in outputs.items():
        target = tmp_path/output;target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(data)
    for output, data in outputs.items():
        target = tmp_path/output;target.write_bytes(data+b'\n')
        with pytest.raises(ValueError, match='stale or inconsistent'):
            proof_adapter.require_generated(tmp_path, path)
        target.write_bytes(data)


@pytest.mark.parametrize('contract', (closed_loop_coolant_access_contract, maf_record_contract, rpm_remaining_inhibit_contract))
def test_reviewed_domain_contract_pins_the_complete_generated_mapping(tmp_path, contract):
    path = tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text = (repo.ROOT/contract.DESCRIPTOR).read_text()
    before, adapter = text.split('\n[adapter]\n', 1)
    changed = adapter.replace('profile = "ordinary-80-572"', 'profile = "partial-state"', 1)
    assert changed != adapter
    path.write_text(before+'\n[adapter]\n'+changed)
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


@pytest.mark.parametrize('path', proof_adapter.DESCRIPTORS)
def test_header_consumes_only_declared_typed_inputs_and_complete_context(path):
    value = proof_adapter.descriptor(repo.ROOT, path)
    row = {field['name']: 0 for field in value['fields']}
    row['entry'] = value['entries'][0]
    if value['kind']['field'] == 'kind':
        row['kind'] = value['kind']['values'][0]
    calibrations = {span['address']: bytes(span['size']) for span in value['calibration']}
    context = lambda case: (0,)*20
    calibration = lambda case: calibrations
    original = proof_adapter.header(value, [row], context, calibration)
    extra = dict(row, expected_output=0xDEADBEEF, terminal=[0xDEADBEEF]*20,
        numerical_oracle=0xDEADBEEF)
    assert proof_adapter.header(value, [extra], context, calibration) == original
    assert b'deadbeef' not in original.lower()
    assert not any(word in original for word in (b'expected_output', b'numerical_oracle', b'terminal'))
    with pytest.raises(ValueError, match='complete 80-byte'):
        proof_adapter.header(value, [row], lambda case: (0,)*19, calibration)
    broken = deepcopy(row);broken[value['fields'][0]['name']] = True
    with pytest.raises(ValueError, match='typed scalar'):
        proof_adapter.header(value, [broken], context, calibration)


def test_reference_components_reuse_transport_with_distinct_reviewed_operand_mappings():
    coolant, record = (proof_adapter.descriptor(repo.ROOT, path) for path in proof_adapter.REFERENCE_DESCRIPTORS)
    assert coolant['profile'] == record['profile'] == proof_adapter.PROFILE
    assert coolant['calibration_input'] is True and record['calibration_input'] is False
    assert coolant['entries'] == [0x5525A] and record['entries'] == [0x25E20, 0x3C3C6]
    assert {row['width'] for row in coolant['memory']} == {1, 2}
    assert {row['width'] for row in record['memory']} == {1}
    assert any('value' in row for row in record['memory'])
    assert coolant['bound'] and not record['bound']
    for value in (coolant, record):
        text = proof_adapter.driver(value, 'reviewed-descriptor').decode()
        assert 'frame_before[192],frame_after[192]' in text
        assert 'sizeof(struct observation)==572U' in text
        assert 'sizeof(struct context)==80U' in text
        assert 'memcpy(memory_before' in text and 'context_after' in text
        assert 'stock_invoke_ignition_consumer(input->entry,&context,&out)' in text
