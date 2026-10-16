"""Ordered cases and independent byte/ABI oracle for the DID publisher."""

import json

from kb import sid22_evidence as proof

RAM_BASE = 0x01000000
OBSERVER = RAM_BASE + 0xf000
ABI = tuple(0x18283848 + i * 0x01010101 for i in range(7))
EARLY_IDS = (
    'did-1101-l04-iFF-v80', 'did-1204-l06-i80-v7F',
    'did-1302-l04-iFB-vFF', 'did-130D-l04-iFF-v80',
    'did-130E-l06-i00-v7F', 'request-invalid',
    'family13-bound-15', 'family11-sentinel', 'family-unsupported',
)


def alias(address):
    if 0xffff8000 <= address < 0xffff8500:
        return address - 0xffff8000 + 0x2000
    return RAM_BASE + (address & 0xffff)


def stub_bytes(kind, address):
    """Explicit simulator-only transport/error observation, outside tested code."""
    end = (address + 22 + 3) & ~3
    displacement = (end - ((address & ~3) + 4)) // 4
    words = [0xd200 | displacement, 0x2242, 0x1251, 0x5022, 0x7001,
             0x1202, 0xe000 | kind, 0x1203, 0xe000 | (0x5a if kind == 1 else 0x6b),
             0x000b, 0x0009]
    if address + 2 * len(words) != end:
        words.append(0x0009)
    return b''.join(word.to_bytes(2, 'big') for word in words) + OBSERVER.to_bytes(4, 'big')


def cases(contract, image):
    by_did = {}
    for binding in contract.bindings:
        previous = by_did.setdefault(binding.did, binding.read_addresses)
        if previous != binding.read_addresses:
            raise ValueError('one DID has inconsistent byte-source order')
    rows = []
    for did, sources in sorted(by_did.items()):
        for length in (4, 6):
            for index in (0, 0x80, 0xfb, 0xff):
                for value in (0, 0x7f, 0x80, 0xff):
                    values = [((value ^ ((i * 0x5a) & 255)) if address >= 0xffff0000
                               else image[address]) for i, address in enumerate(sources)]
                    rows.append(dict(id=f'did-{did:04X}-l{length:02X}-i{index:02X}-v{value:02X}',
                        did=did, request_length=length, start=index, value=value,
                        flag=0, sources=list(sources), values=values, transport=1, error=0x12))
    # These controls assert actual firmware behavior, not a fabricated common bound.
    sentinel = next(low for low in range((0x2289c - 0x226ac) // 4)
                    if image[0x226ac + 4 * low:0x226b0 + 4 * low] == b'\xff' * 4)
    for id_, did, length, error in (
        ('request-invalid', 0x1101, 2, 0x12),
        ('family13-bound-15', 0x1315, 4, 0x12),
        ('family11-sentinel', 0x1100 + sentinel, 4, 0x12),
        ('family-unsupported', 0x1001, 4, 0x10),
    ):
        rows.append(dict(id=id_, did=did, request_length=length, start=0xff, value=0x80,
                         flag=0, sources=[], values=[], transport=0, error=error))
    if 0x1146 in by_did:
        row = next(row for row in rows if row['did'] == 0x1146)
        rows.append({**row, 'id': 'did-1146-post-flag', 'flag': 1})
    for index, row in enumerate(rows):
        row['index'] = index
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('duplicate DID execution case identities')
    early_indices(rows)
    return rows


def early_indices(rows):
    by_id = {row['id']: row['index'] for row in rows}
    return tuple(by_id[id_] for id_ in EARLY_IDS)


def publication(case):
    if not case['transport']:
        return [], 0
    payload = [0x62, case['did'] >> 8, case['did'] & 255, *case['values']]
    writes = [((case['start'] + offset) & 255, byte) for offset, byte in enumerate(payload)]
    # Family11 wraps after its ordinary single byte. Other selected paths pass
    # an untruncated last-index+1, which can be 256, to the transport helper.
    end = writes[-1][0] + 1
    if case['did'] >> 8 == 0x11 and len(case['values']) == 1:
        end &= 255
    return writes, end


def return_value(case):
    if not case['transport']:
        return 0x6b
    if case['did'] >> 8 != 0x11:
        return 0x5a
    low = case['did'] & 255
    if low == 0x46 and case['flag']:
        return 0x679
    return low if low < 128 else low | 0xffffff00


def validate_observation(case, observed):
    from kb.test_evidence import encode
    if any(type(observed[name]) is not int for name in (
            'stub_kind', 'stub_count', 'return_value', 'ram_checked_bytes',
            'sp_before', 'sp_after', 'pr', 'continuation', 'gbr', 'mach', 'macl',
            'sr_before', 'sr_after')):
        raise ValueError('DID observation integer fields have another type')
    if (type(observed['index']) is not int or observed['index'] != case['index']
            or observed['id'] != case['id']):
        raise ValueError('DID observations are missing, duplicated or reordered')
    expected_args = [case['start'] if case['start'] < 128 else case['start'] | 0xffffff00,
                     publication(case)[1]] if case['transport'] else [0x22, case['error']]
    if encode(observed['stub_args']) != encode(expected_args):
        raise ValueError('the real transport/error helper arguments differ')
    if observed['stub_kind'] != (1 if case['transport'] else 2) or observed['stub_count'] != 1:
        raise ValueError('the wrong helper or number of calls executes')
    if observed['return_value'] != return_value(case):
        raise ValueError('the natural publisher return value differs')
    if (encode(observed['sources_before']) != encode(case['values'])
            or encode(observed['sources_after']) != encode(case['values'])):
        raise ValueError('the actual independent byte sources differ or change')
    expected = list(bytes.fromhex(observed['buffer_before']))
    if len(expected) != 256:
        raise ValueError('the complete response ring is missing')
    for offset, byte in publication(case)[0]:
        expected[offset] = byte
    if observed['buffer_after'] != bytes(expected).hex():
        raise ValueError('the actual response bytes or source order differ')
    if (observed['ram_checked_bytes'] != 65536 or observed['outside_writes_unchanged'] is not True
            or observed['lower_guard_unchanged'] is not True):
        raise ValueError('the full RAM footprint or lower frame guard differs')
    if observed['sp_before'] != observed['sp_after'] or observed['pr'] != observed['continuation']:
        raise ValueError('the natural SP/PR return contract fails')
    initial_frame, final_frame = observed['frame_before'], observed['frame_after']
    if (len(initial_frame) != 16 or len(final_frame) != 16
            or initial_frame != [0xa3b4c5d6 + 17 * index for index in range(16)]
            or final_frame[:4] != initial_frame[:4]
            or final_frame[12:] != [observed['continuation'], ABI[6], ABI[5], ABI[4]]):
        raise ValueError('the natural saved frame or lower guard differs')
    if (len(observed['caller_abi_before']) != 12
            or observed['caller_abi_before'] != observed['caller_abi_after']):
        raise ValueError('the independent C caller ABI differs')
    registers = observed['gpr']
    if len(registers) != 15 or any(type(value) is not int or not 0 <= value <= 0xffffffff
                                 for value in registers):
        raise ValueError('the full register exit snapshot is missing')
    if tuple(registers[8:15]) != ABI or registers[0] != return_value(case):
        raise ValueError('callee-saved state or return register differs')
    if (observed['gbr'], observed['mach'], observed['macl']) != (0x12344321, 0x10203040, 0x50607080):
        raise ValueError('the publisher changes preserved special registers')
    if observed['sr_before'] & ~1 != observed['sr_after'] & ~1:
        raise ValueError('the publisher changes status bits outside T')


def render_header(contract, image):
    rows = cases(contract, image)
    lines = ['/* Generated from the exact SID22 descriptor and kb.sid22_matrix. */',
        'struct sid22_case {',
        '    unsigned index,did,length,start,value,flag,transport,error,width;',
        '    uint32_t sources[4]; uint8_t values[4]; const char *id;',
        '};', 'static const struct sid22_case sid22_cases[] = {']
    for row in rows:
        numbers = [row[key] for key in ('index', 'did', 'request_length', 'start', 'value', 'flag', 'transport', 'error')]
        numbers.append(len(row['sources']))
        array = lambda values: '{' + ','.join(f'0x{value:x}U' for value in values or [0]) + '}'
        lines.append('    {' + ','.join(str(value) + 'U' for value in numbers) + ','
                     + array(row['sources']) + ',' + array(row['values']) + ',' + json.dumps(row['id']) + '},')
    lines += ['};', 'static const unsigned sid22_early_indices[] = {'
              + ','.join(str(index) + 'U' for index in early_indices(rows)) + '};', '']
    return '\n'.join(lines)


def fixture(data, contract):
    result, changes = bytearray(data), []
    for address, size in contract.pools:
        value = int.from_bytes(data[address:address + size], 'big')
        original = value | 0xffff0000 if size == 2 and value & 0x8000 else value
        if 0xffff0000 <= original < 0xffffffff:
            target = alias(original)
            if size == 2 and not 0 <= target < 0x8000:
                raise ValueError('a signed-word RAM alias leaves its positive window')
            replacement = target.to_bytes(size, 'big')
            result[address:address + size] = replacement
            changes.append(dict(kind='ram-pool', address=address, before=data[address:address + size].hex(), after=replacement.hex()))
    for _, start, end, _ in proof.TABLES:
        for address in range(start, end, 4):
            original = int.from_bytes(data[address:address + 4], 'big')
            if not 0xffff0000 <= original < 0xffffffff:
                continue
            replacement = alias(original).to_bytes(4, 'big')
            result[address:address + 4] = replacement
            changes.append(dict(kind='ram-table-pointer', address=address,
                                before=data[address:address + 4].hex(), after=replacement.hex()))
    for kind, address in ((1, 0x2ec9a), (2, 0x34114)):
        replacement = stub_bytes(kind, address)
        result[address:address + len(replacement)] = replacement
        changes.append(dict(kind='transport-stub' if kind == 1 else 'error-stub',
            address=address, before=data[address:address + len(replacement)].hex(), after=replacement.hex()))
    for start, end in contract.body:
        if result[start:end] != data[start:end]:
            raise ValueError('a simulator relocation changes tested publisher instructions')
    return bytes(result), changes
