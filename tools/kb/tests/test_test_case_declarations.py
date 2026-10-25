"""Typed fixture declarations preserve actual parameter names and source scopes."""

import pytest

from kb import test_cases


def test_module_fixture_parameter_is_the_declared_image_name():
    selector = 'tools/mapkit/tests/test_lavender_scale.py::test_lavender_nominal_initialized_scale'
    cases = test_cases.cases(selector)
    assert cases[0].parameters == {'image': 'JK00A'}
    assert cases[-1].parameters == {'image': 'JK00D'}
    assert cases[0].nodeid == selector + '[JK00A]'


def test_dedicated_image_fixture_does_not_inherit_the_module_image_parameter():
    selector = ('tools/mapkit/tests/test_vvel_temperature_axis_scale.py::'
                'test_vvel_duration_startup_blend_axis_nominal_temperature')
    cases = test_cases.cases(selector)
    assert tuple(case.nodeid for case in cases) == (selector,)
    assert cases[0].parameters == {}


def test_raw_count_parameters_retain_exact_integer_types():
    selector = 'tools/mapkit/tests/test_vq37_ramp_delay_scale.py::test_ramp_delay_local_count_scale'
    first, last = test_cases.cases(selector)[0], test_cases.cases(selector)[-1]
    assert first.parameters == {'raw': 0} and type(first.parameters['raw']) is int
    assert last.parameters == {'raw': 255} and type(last.parameters['raw']) is int


def test_unregistered_selector_cannot_get_an_empty_parameter_fallback():
    with pytest.raises(ValueError, match='no explicit typed case'):
        test_cases.cases('unknown.py::test_ordinary')
