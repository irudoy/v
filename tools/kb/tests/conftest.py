"""Test-local stock inputs with catalog validation before and after use."""

import pytest

from kb import derive, repo


@pytest.fixture(scope="session")
def jk08a_stock_bytes():
    layout = repo.layout("7mfk")
    data = derive.image_bytes(layout)
    yield data
    assert derive.image_bytes(layout) == data, "JK08A stock image changes during the test session"
