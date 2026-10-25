"""Original fine-gopher observations fence the zero-word bypass and complete state."""

import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import fine_gopher_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['fine_gopher_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original fine-gopher capture')
        pytest.skip('the complete original fine-gopher capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['zero_bypass_distinct_from_fault_store'] is True
    assert any(row['zero_bypass'] for row in result['semantic_results'])
    assert any(row['beetle_call'] for row in result['semantic_results'])
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries','observations','simulator'))
def test_missing_fine_gopher_physical_input_refuses(original,field):
    packet=dict(original[2]);packet.pop(field);refuse(original,packet)
