"""Original sexy-tamarin observations fence both lookup dividends and complete state."""

import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import sexy_tamarin_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['sexy_tamarin_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original sexy-tamarin capture')
        pytest.skip('the complete original sexy-tamarin capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['lookup_scales_the_signed_dividend'] is True
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries','observations','simulator'))
def test_missing_sexy_tamarin_physical_input_refuses(original,field):
    packet=dict(original[2]);packet.pop(field);refuse(original,packet)
