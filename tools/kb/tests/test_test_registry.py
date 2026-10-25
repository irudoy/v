"""Owning-context, claimed-fact and typed-case registration refusal contracts."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from kb import test_contract, test_origins, test_registry
from tools.kb.tests.test_test_origins import native_origins


def profile(model, symbol, origin, *, key='raw-observation', parameters=None):
    nodeid = origin.path + '::' + origin.selector + '[zero]'
    contract = test_contract.Contract(key, (test_contract.Case(nodeid,
        {'value': 0} if parameters is None else parameters),))
    binding = test_registry.Binding(origin.key, origin.context_digest,
        origin.path, origin.selector, symbol.key.key,
        test_registry.Claim(symbol.key.key, 'identity'), 'identity',
        'exact-byte-observation', (nodeid,), origin.locator_text)
    return test_registry.Profile(key, contract, (binding,),
        'controlled-independent-observer', ('exact-byte-observation',)), binding, nodeid


def test_registry_prepares_a_request_without_an_execution_admission(native_origins):
    model, symbol, _, evidence = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, binding, _ = profile(model, symbol, origin)
    registry = test_registry.Registry((selected,))
    request = registry.request(model, symbol, evidence, 'identity', origin)
    assert isinstance(request, test_registry.Request)
    assert request.packet()['binding'] == binding.packet()
    assert 'receipt' not in request.packet()
    assert 'qualified' not in request.packet()


def test_same_test_at_another_native_attachment_does_not_share_admission(native_origins):
    model, symbol, link, evidence = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, _ = profile(model, symbol, origin)
    registry = test_registry.Registry((selected,))
    wrong = test_origins.link_attachment(model, link, 0)
    with pytest.raises(ValueError, match='unregistered'):
        registry.request(model, symbol, evidence, 'identity', wrong)


@pytest.mark.parametrize('name', ['scale', 'contract', 'role', 'diagnostic'])
def test_identity_binding_does_not_supply_another_claim(native_origins, name):
    model, symbol, _, evidence = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, _ = profile(model, symbol, origin)
    registry = test_registry.Registry((selected,))
    claim = SimpleNamespace(subject=symbol.key.key, name=name)
    with pytest.raises(ValueError):
        registry.request(model, symbol, evidence, claim, origin)


def test_current_origin_does_not_renew_a_stale_registered_context(native_origins):
    model, symbol, _, evidence = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, _ = profile(model, symbol, origin)
    registry = test_registry.Registry((selected,))
    symbol.props['signed'] = True
    current = test_origins.symbol_attachment(model, symbol, 0)
    with pytest.raises(ValueError, match='stale facts'):
        registry.request(model, symbol, evidence, 'identity', current)


def test_metadata_role_alone_cannot_define_a_semantic_profile(native_origins):
    model, symbol, _, _ = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, _ = profile(model, symbol, origin)
    with pytest.raises(ValueError, match='metadata consistency alone'):
        test_registry.Registry((replace(selected, adapter='metadata'),))


def test_common_case_union_preserves_typed_parameters_and_exact_membership(native_origins):
    model, symbol, link, _ = native_origins
    first = test_origins.symbol_attachment(model, symbol, 0)
    second = test_origins.link_attachment(model, link, 0)
    one, _, nodeid = profile(model, symbol, first)
    two, _, _ = profile(model, symbol, second, key='same-observed-case')
    registry = test_registry.Registry((one, two))
    assert len(registry.cohort((nodeid,)).cases) == 1
    with pytest.raises(ValueError, match='exactly once'):
        registry.cohort((nodeid, nodeid))
    conflicting, _, _ = profile(model, symbol, second, key='changed-parameter', parameters={'value': False})
    registry = test_registry.Registry((one, conflicting))
    with pytest.raises(ValueError, match='different typed parameters'):
        registry.cohort((nodeid,))


def test_duplicate_claim_and_missing_independent_fact_are_refused(native_origins):
    model, symbol, _, _ = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, binding, _ = profile(model, symbol, origin)
    with pytest.raises(ValueError, match='repeats an origin'):
        test_registry.Registry((replace(selected, bindings=(binding, binding)),))
    with pytest.raises(ValueError, match='no registered fact'):
        test_registry.Registry((replace(selected, bindings=(replace(binding, fact='unproved'),)),))


def test_reordered_case_union_is_not_a_new_execution_contract(native_origins):
    model, symbol, _, _ = native_origins
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, first = profile(model, symbol, origin)
    second = origin.path + '::' + origin.selector + '[one]'
    contract = test_contract.Contract(selected.key,
        (*selected.contract.cases, test_contract.Case(second, {'value': 1})))
    registry = test_registry.Registry((replace(selected, contract=contract),))
    assert [case.nodeid for case in registry.cohort().cases] == [first, second]
    with pytest.raises(ValueError, match='declared order'):
        registry.cohort((second, first))


def test_native_explicit_fact_cannot_be_rebound_by_a_profile(native_origins):
    model, symbol, _, evidence = native_origins
    symbol.evidence[0]['supports'] = 'scale'
    evidence = dict(symbol.evidence[0])
    origin = test_origins.symbol_attachment(model, symbol, 0)
    selected, _, _ = profile(model, symbol, origin)
    registry = test_registry.Registry((selected,))
    with pytest.raises(ValueError, match='another explicit native fact'):
        registry.request(model, symbol, evidence, 'identity', origin)


def test_explicit_common_order_preserves_module_fixture_interleaving(native_origins):
    model, symbol, link, _ = native_origins
    first = test_origins.symbol_attachment(model, symbol, 0)
    second = test_origins.link_attachment(model, link, 0)
    one, one_binding, one_zero = profile(model, symbol, first, key='first')
    two, two_binding, _ = profile(model, symbol, second, key='second')
    two_zero = second.path + '::' + second.selector + '[other-zero]'
    one_one = first.path + '::' + first.selector + '[one]'
    two_one = second.path + '::' + second.selector + '[other-one]'
    one = replace(one, contract=test_contract.Contract('first',
        (test_contract.Case(one_zero, {'value': 0}), test_contract.Case(one_one, {'value': 1}))),
        bindings=(replace(one_binding, cases=(one_zero, one_one)),))
    two = replace(two, contract=test_contract.Contract('second',
        (test_contract.Case(two_zero, {'value': 0}), test_contract.Case(two_one, {'value': 1}))),
        bindings=(replace(two_binding, cases=(two_zero, two_one)),))
    order = (one_zero, two_zero, one_one, two_one)
    registry = test_registry.Registry((one, two), case_order=order)
    assert tuple(case.nodeid for case in registry.cohort().cases) == order
    wrong = test_registry.Registry((one, two), case_order=(one_one, two_zero, one_zero, two_one))
    with pytest.raises(ValueError, match='conflicting actual case order'):
        wrong.cohort()
