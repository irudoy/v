"""Streamed hashes retain the accepted protocol-5 state packets."""

from pathlib import PurePosixPath
from types import SimpleNamespace

from kb import convert


def test_atomic_values_and_paths_retain_the_accepted_packet_hash():
    value = SimpleNamespace(values=[None, False, True, 0, -1, 1.25, -0.0, 'sample', b'bytes'],
                            path=PurePosixPath('fixture/input'))
    assert convert._model_digest(value).hex() == \
        '6ec08a30b2df08890c61d9160a9bb451b9abc19653429a039777661ee069f4ee'


def test_shared_and_equal_distinct_values_retain_the_accepted_packet_hash():
    shared = [1, 2]
    value = {'first': shared, 'second': shared, 'equal': [1, 2]}
    assert convert._model_digest(value).hex() == \
        '363c99385740bf3096ac061ed50514e97b6c0660788d1095d0a34927f095b1ef'


def test_deep_cycle_retain_the_accepted_packet_hash():
    value = SimpleNamespace(value=0)
    child = value
    for index in range(2000):
        child.next = SimpleNamespace(value=index)
        child = child.next
    child.next = value
    assert convert._model_digest(value).hex() == \
        '5b9c09cde347ce1ffb6b720bb24739269ae9f83b0c00ad25d752829be184b042'


def test_packet_larger_than_the_buffer_retains_the_accepted_hash():
    value = {'values': list(range(50000))}
    assert convert._model_digest(value).hex() == \
        'ad903c7cc9df2abafa03ee4bc26a4648db737c07c150ec202b9a58c91b7e90d5'


def test_every_digest_reads_current_state_and_preserves_signed_zero():
    value = SimpleNamespace(value=0.0)
    before = convert._model_digest(value)
    value.value = -0.0
    assert convert._model_digest(value) != before
    value.value = 0.0
    assert convert._model_digest(value) == before
