"""Generated descriptor and complete raw-transport refusal sources."""

from kb import proof_adapter, repo
from tools.kb.tests.proof_adapter_cases import require_descriptor_refusals, require_transport_refusals

DESCRIPTOR = 'defs/JK08A.clamp-latch-caller-withdrawal-paths.toml'


def test_current_generated_adapter_source_is_exact():
    proof_adapter.require_generated(repo.ROOT, DESCRIPTOR)


def test_adapter_rejects_inconsistent_or_result_bearing_declarations():
    require_descriptor_refusals(proof_adapter.descriptor(repo.ROOT, DESCRIPTOR))


def test_adapter_rejects_incomplete_or_substituted_raw_transport():
    require_transport_refusals(proof_adapter.descriptor(repo.ROOT, DESCRIPTOR))
