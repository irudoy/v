"""Shared execution views retain all actual cases and terminal obligations."""

from copy import deepcopy
from dataclasses import replace

import pytest

from kb import test_cohort, test_contract, test_origins, test_registry
from tools.kb.tests.test_test_origins import native_origins
from tools.kb.tests.test_test_registry import profile


def registered_cohort(model, symbol, link):
    first = test_origins.symbol_attachment(model, symbol, 0)
    second = test_origins.link_attachment(model, link, 0)
    one, _, _ = profile(model, symbol, first, key='first')
    two, binding, _ = profile(model, symbol, second, key='second')
    nodeid = second.path + '::' + second.selector + '[second]'
    two = replace(two,
        contract=test_contract.Contract('second', (test_contract.Case(nodeid, {'value': 1}),)),
        bindings=(replace(binding, cases=(nodeid,)),))
    return test_cohort.Cohort(test_registry.Registry((one, two)))


def complete_candidate(cohort):
    capture = test_contract.Capture(cohort.contract, {'mode': 'rewrite', 'python_optimize': 0})
    capture.collect([(case.nodeid, case.parameters) for case in cohort.contract.cases])
    for case in cohort.contract.cases:
        for phase in test_contract.PHASES:
            capture.report(case.nodeid, phase, 'passed', False)
    return capture.candidate(0, complete=True)


def test_profile_view_keeps_original_global_case_and_report_positions(native_origins):
    model, symbol, link, _ = native_origins
    cohort = registered_cohort(model, symbol, link)
    candidate = complete_candidate(cohort)
    view = cohort.view(candidate, 'second')
    assert view['case_positions'] == [1]
    assert view['report_positions'] == [3, 4, 5]
    assert view['candidate_digest'] == test_contract.digest(candidate)
    assert not {'exitstatus', 'complete', 'qualified', 'semantic_admission'} & view.keys()
    cohort.require_view(candidate, 'second', view)


@pytest.mark.parametrize('damage', ['missing', 'skip', 'failed', 'unrelated', 'parameter', 'order'])
def test_another_profile_failure_cannot_be_filtered_out(native_origins, damage):
    model, symbol, link, _ = native_origins
    cohort = registered_cohort(model, symbol, link)
    candidate = complete_candidate(cohort)
    first = cohort.contract.cases[0].nodeid
    if damage == 'missing':
        candidate['reports'].pop(0)
    elif damage == 'skip':
        candidate['reports'][1][2] = 'skipped'
    elif damage == 'failed':
        candidate['reports'][1][2] = 'failed'
    elif damage == 'unrelated':
        candidate['reports'].append(['unrelated.py::test_other', 'call', 'passed', False])
    elif damage == 'parameter':
        candidate['parameters'][first] = test_contract.encode({'value': False})
    elif damage == 'order':
        candidate['collected'].reverse()
    with pytest.raises(ValueError):
        cohort.view(candidate, 'second')


def test_forged_view_cannot_change_profile_or_remove_original_reports(native_origins):
    model, symbol, link, _ = native_origins
    cohort = registered_cohort(model, symbol, link)
    candidate = complete_candidate(cohort)
    original = cohort.view(candidate, 'second')
    for field, value in [('profile', 'first'), ('case_positions', [0]),
                         ('report_positions', [4]), ('candidate_digest', '0' * 64)]:
        forged = deepcopy(original)
        forged[field] = value
        with pytest.raises(ValueError, match='original cohort or profile'):
            cohort.require_view(candidate, 'second', forged)
