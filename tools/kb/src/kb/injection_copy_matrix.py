"""Independent expectations for the existing bounded snapshot capture.

This module does not admit native claims or execution receipts. Actual original
execution, instruction/fixture binding and native owner checks remain required.
"""
from itertools import product

MASK = 0xffffffff
CALLER = 0x21314
HELPER = 0x22558
SOURCE = 0xffff23bc
DESTINATION = 0xffff2330
RAM_BASE = 0x01000000
LENGTHS = (0, 1, 2, 3, 4, 5, 6, 7, 139, 140, 141, 255)
BASE_RAM = bytes((0x5d + i * 19 + (i >> 8)) & 255 for i in range(65536))
ABI = [0x18283848, 0x19293949, 0x1a2a3a4a, 0x1b2b3b4b, 0x1c2c3c4c,
       0x1d2d3d4d, 0x1e2e3e4e, 0x12344321, 0x10203040, 0x50607080]


def alias(address):
    return RAM_BASE + (address & 65535)


def _context(entry, source, destination, length, variant):
    result = [((0xa9876543 + i * 0x00130709) if variant
               else (0x28765430 + i * 0x01030507)) & MASK for i in range(15)]
    result[7] = entry
    if entry == CALLER:
        result[11:13] = [HELPER, 140]
    else:
        result[:3] = [length, alias(destination), alias(source)]
    return result


def _row(entry, source, destination, length, pattern, position, seed, variant, entry_t, carry):
    incoming = _context(entry, source, destination, length, variant)
    result = incoming.copy()
    last = (129 * int(position == length - 1) if pattern
            else (seed + 29 * (length - 1)) & 255)
    result[0] = (last if last < 128 else last - 256) & MASK if length else 0
    result[1:3] = [alias(destination) + 4 * (length // 4), alias(source)]
    if entry == CALLER:
        result[7] = 0
    return [entry, source, destination, length, pattern, position, seed, variant,
            entry_t, int(length == 0), carry, incoming, result]


def cases():
    """Generate the complete ordered matrix without reading C expectations."""
    rows = [_row(CALLER, SOURCE, DESTINATION, 140, 0, 0, seed, variant, t, 0)
            for seed, variant, t in product(range(256), range(2), range(2))]
    rows.extend(_row(CALLER, SOURCE, DESTINATION, 140, 1, position, 0, variant,
                     (position + variant) & 1, 0)
                for position, variant in product(range(140), range(2)))
    rows.extend(_row(HELPER, 0xffff4000 + source, 0xffff5000 + destination,
                     length, 0, 0, (17 * length + 31 * source + destination) & 255,
                     (source + destination + t) & 1, t, 0)
                for length, source, destination, t in product(LENGTHS, range(4), range(4), range(2)))
    rows.extend(_row(CALLER, SOURCE, DESTINATION, 140, 0, 0, seed, variant, t, carry)
                for variant, t in product(range(2), range(2))
                for seed, carry in ((0, 0), (128, 1), (255, 1)))
    assert len(rows) == 1700
    return rows


def _words(value, count):
    if type(value) is not list or len(value) != count or any(
            type(item) is not int or not 0 <= item <= MASK for item in value):
        raise ValueError('an actual register vector has the wrong shape')
    return value


def _hex(value, count):
    if type(value) is not str or len(value) != 2 * count or any(
            char not in '0123456789abcdef' for char in value):
        raise ValueError('an actual byte span has the wrong shape')
    return bytes.fromhex(value)


def _word_into(data, offset, value):
    data[offset:offset + 4] = value.to_bytes(4, 'big')


def validate_observation(index, case, observed, memory=None):
    """Check raw MCU/C observations and return the predicted full RAM state."""
    if type(observed) is not dict:
        raise ValueError('an actual observation is a table')
    entry, source, destination, length, pattern, position, seed, variant, t, exit_t, carry, incoming, _ = case
    required = {'index', 'entry', 'source', 'destination', 'length', 'incoming',
                'gbr', 'mach', 'macl', 'entry_t', 'exit', 'sp', 'continuation', 'sr_before',
                'abi_before', 'abi_after', 'frame_before', 'frame_after',
                'source_before', 'source_after', 'destination_before', 'destination_after',
                'pools_before', 'pools_after', 'outside_changes', 'incoming_after',
                'gbr_after', 'mach_after', 'macl_after', 'entry_t_after'}
    if set(observed) != required:
        raise ValueError('an actual observation omits or adds fields')
    for key in required - {'incoming', 'exit', 'abi_before', 'abi_after', 'frame_before',
                           'frame_after', 'source_before', 'source_after', 'destination_before',
                           'destination_after', 'pools_before', 'pools_after', 'outside_changes',
                           'incoming_after'}:
        if type(observed[key]) is not int or not 0 <= observed[key] <= MASK:
            raise ValueError('an actual scalar is not an unsigned word')
    if [observed[key] for key in ('index', 'entry', 'source', 'destination', 'length')] != [
            index, entry, source, destination, length]:
        raise ValueError('an actual case has the wrong identity or boundaries')
    if _words(observed['incoming'], 15) != incoming or _words(observed['incoming_after'], 15) != incoming:
        raise ValueError('the actual prepared register context differs or changes')
    special = [0xd8b6a491, 0xf1e2d3c4, 0x9274b6d8, t] if variant else [
        0x456789ab, 0x13579bdf, 0x2468ace0, t]
    for key, expected in zip(('gbr', 'mach', 'macl', 'entry_t'), special):
        if observed[key] != expected or observed[key + '_after'] != expected:
            raise ValueError('the actual prepared special registers differ or change')
    if not carry:
        memory = bytearray(BASE_RAM.translate(bytes((value + index) & 255 for value in range(256))))
    elif memory is None or len(memory) != 65536:
        raise ValueError('a successive case lacks the preceding full RAM state')
    source_start, destination_start = source & 65535, destination & 65535
    memory[source_start:source_start + length] = bytes(
        (129 if offset == position else 0) if pattern else (seed + offset * 29) & 255
        for offset in range(length))
    source_bytes = bytes(memory[source_start:source_start + length])
    destination_bytes = bytes(memory[destination_start:destination_start + length])
    for key, expected in (('source_before', source_bytes), ('source_after', source_bytes),
                          ('destination_before', destination_bytes), ('destination_after', source_bytes)):
        if _hex(observed[key], length) != expected:
            raise ValueError('actual source/destination bytes violate the ordered copy')
    if type(observed['outside_changes']) is not list or observed['outside_changes']:
        raise ValueError('the actual copy changes bytes outside its destination')
    memory[destination_start:destination_start + length] = source_bytes
    output = _words(observed['exit'], 20)
    expected_gpr = _row(entry, source, destination, length, pattern, position, seed, variant, t, carry)[12]
    if entry == CALLER:
        expected_gpr[7] = observed['continuation']
    if [output[19 - register] for register in range(15)] != expected_gpr:
        raise ValueError('actual complete exit registers differ from the instruction model')
    sr = observed['sr_before']
    if sr & 0x301 != t or output[:5] != [
            (sr & ~1) | exit_t, observed['continuation'], special[2], special[1], special[0]]:
        raise ValueError('actual status, return boundary or special registers differ')
    before, after = _words(observed['abi_before'], 12), _words(observed['abi_after'], 12)
    if before[:10] != ABI or before != after or observed['sp'] != (before[10] - 164) & MASK:
        raise ValueError('the actual C ABI or stack boundary changes')
    frame = bytearray(_hex(observed['frame_before'], 96))
    for offset, value in ((60, alias(source)), (56, incoming[3]), (52, incoming[4])):
        _word_into(frame, offset, value)
    if _hex(observed['frame_after'], 96) != frame:
        raise ValueError('the actual helper save frame or its neighbors differ')
    pools = bytes.fromhex('01002330010023bc')
    if _hex(observed['pools_before'], 8) != pools or _hex(observed['pools_after'], 8) != pools:
        raise ValueError('actual aliased data pools differ or change')
    return memory
