"""Native source preparation retains values, aliases and separate containers."""

from datetime import datetime, timezone
import math
import pickle
import struct
from types import SimpleNamespace
import tomllib

from kb import source_documents


def test_native_toml_preserves_order_types_and_fresh_nested_values():
    document = tomllib.loads('name = "source"\nactive = true\ninteger = 123456789012345678901\n'
                            '[[items]]\nvalues = [1, 2, 3]\n')
    packed = source_documents.freeze(document, native=True)
    assert packed[:1] != b'\x80'
    first, second = source_documents.thaw(packed), source_documents.thaw(packed)
    assert list(first) == list(second) == list(document)
    assert first == second == document
    assert type(second['active']) is bool and type(second['integer']) is int
    first['items'][0]['values'].append(4)
    assert second == document and source_documents.thaw(packed) == document


def test_native_float_bits_retain_nan_and_signed_zero():
    for text in ('value = 0.0', 'value = -0.0', 'value = inf', 'value = -inf', 'value = nan'):
        document = tomllib.loads(text)
        result = source_documents.thaw(source_documents.freeze(document, native=True))
        assert struct.pack('>d', result['value']) == struct.pack('>d', document['value'])
        assert math.isnan(result['value']) == math.isnan(document['value'])


def test_native_datetime_keeps_the_original_pickle_encoding():
    document = {'stamp': datetime(2026, 10, 12, tzinfo=timezone.utc), 'values': [1]}
    packed = source_documents.freeze(document, native=True)
    assert packed == pickle.dumps(document, protocol=pickle.HIGHEST_PROTOCOL)
    first = source_documents.thaw(packed)
    first['values'].append(2)
    assert source_documents.thaw(packed) == document


def test_supplied_documents_keep_custom_types_aliases_and_cycles():
    shared = [bytearray(b'bytes')]
    document = SimpleNamespace(first=shared, second=shared)
    document.cycle = document
    packed = source_documents.freeze(document)
    first, second = source_documents.thaw(packed), source_documents.thaw(packed)
    assert first is first.cycle and second is second.cycle
    assert first.first is first.second and second.first is second.second
    assert first.first is not second.first
    assert type(second.first[0]) is bytearray
    first.first[0][0] = 0
    assert second.first[0] == bytearray(b'bytes')
