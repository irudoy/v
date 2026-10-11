"""Large fixture mismatches retain full equality and bounded explanations."""

import pytest

from tools.kb.tests import test_injection_start_delay_chain as publication


class NoRepresentation(bytearray):
    def __repr__(self):
        raise AssertionError('Fixture representation must not be constructed')


def fixture(stock):
    module = publication.stock_module()
    return NoRepresentation(module.build_fixture(publication.declared_region(), stock))


def test_complete_fixture_equality_accepts_the_exact_registered_image(jk08a_stock_bytes):
    publication.verify_fixture(fixture(jk08a_stock_bytes), jk08a_stock_bytes)


@pytest.mark.parametrize('location', ('first', 'middle', 'last', 'instruction', 'alias'))
def test_complete_fixture_corruption_refuses_without_rendering_the_image(
        location, jk08a_stock_bytes):
    value = fixture(jk08a_stock_bytes)
    address = {'first': 0, 'middle': len(value) // 2, 'last': len(value) - 1,
               'instruction': 0x52284, 'alias': 0x21f3c}[location]
    value[address] ^= 1
    with pytest.raises(AssertionError, match='Full fixture byte equality failed') as refused:
        publication.verify_fixture(value, jk08a_stock_bytes)
    assert len(str(refused.value)) < 160
