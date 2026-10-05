"""Sample the edges and interior of complete byte-range binding assertions.

Use these representatives only when a validator checks every byte in each
range before its semantic assertions. Positive stock checks retain the full
bindings; independent semantic and executable cases retain their own inputs.
"""


def _samples(spans, stride):
    result = []
    for start, end in spans:
        assert 0 <= start < end
        count = (end - start + stride - 1) // stride
        for position in sorted({0, count // 2, count - 1}):
            address = start + stride * position
            result.append((address, f'{start:08x}..{end:08x}@{address:08x}'))
    return tuple(result)


def _byte_spans(spans):
    return _samples(((start, end) for start, end, _ in spans), 1)


def byte_span_samples(spans):
    return tuple(address for address, _ in _byte_spans(spans))


def byte_span_ids(spans):
    return tuple(label for _, label in _byte_spans(spans))


def _slices(slices, stride):
    return _samples(((address, address + len(bytes.fromhex(data)
                     if isinstance(data, str) else data))
                     for address, data in slices), stride)


def slice_byte_samples(slices):
    return tuple(address for address, _ in _slices(slices, 1))


def slice_byte_ids(slices):
    return tuple(label for _, label in _slices(slices, 1))


def slice_word_samples(slices):
    return tuple(address for address, _ in _slices(slices, 2))


def slice_word_ids(slices):
    return tuple(label for _, label in _slices(slices, 2))
