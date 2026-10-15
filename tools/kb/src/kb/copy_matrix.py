"""Ordered inputs and independent observations of the bounded CAN copy."""

from kb import copy_evidence


def cases(descriptor):
    matrix = descriptor['matrix']
    if copy_evidence.encode(matrix) != copy_evidence.encode(dict(raw_byte_values=256, isolated_positions=12,
            incoming_mq_states=[0, 256, 512, 768], incoming_t_states=[0, 1],
            register_variants=2, helper_control_lengths=[0, 1, 2, 3, 4, 5, 13])):
        raise ValueError('unsupported CAN copy matrix')
    rows = []

    def add(group, pattern, *, value=0, position=0, variant=0, sr=0, carry=False, length=12):
        index = len(rows)
        caller = group != 'helper-control'
        source, destination = (0xffff4194, 0xffff4188) if caller else (0xffff4300, 0xffff4280)
        incoming = [((0x10203040 + register * 0x01010101) ^
                     (0xa596c387 if variant else 0) ^ index * 0x101) & 0xffffffff
                    for register in range(15)]
        incoming[1], incoming[11] = alias(destination), 0x22558
        if not caller:
            incoming[0], incoming[2] = length, alias(source)
        rows.append(dict(id=f'{group}-{index:04d}', index=index, group=group,
            caller=caller, source=source, destination=destination, length=length,
            pattern=pattern, value=value, position=position, variant=variant, sr=sr,
            carry=carry, incoming=incoming,
            gbr=0xd8b6a491 if variant else 0x456789ab,
            mach=0xf1e2d3c4 if variant else 0x13579bdf,
            macl=0x9274b6d8 if variant else 0x2468ace0))

    for value in range(matrix['raw_byte_values']):
        for t in matrix['incoming_t_states']:
            add('raw', 'raw', value=value, sr=matrix['incoming_mq_states'][value % 4] | t,
                variant=value % 2)
    for position in range(matrix['isolated_positions']):
        for variant in range(matrix['register_variants']):
            for t in matrix['incoming_t_states']:
                add('isolated', 'isolated', position=position, variant=variant, sr=t)
    for pattern in ('zero', 'ones', 'increment', 'alternate', 'sequence'):
        for mq in matrix['incoming_mq_states']:
            for t in matrix['incoming_t_states']:
                for variant in range(matrix['register_variants']):
                    add('pattern', pattern, variant=variant, sr=mq | t)
    for mq in matrix['incoming_mq_states']:
        for t in matrix['incoming_t_states']:
            for variant in range(matrix['register_variants']):
                for value in (0x12, 0x34, 0x56, 0x78):
                    add('successive', 'raw', value=value, variant=variant, sr=mq | t,
                        carry=value != 0x12)
    for length in matrix['helper_control_lengths']:
        for t in matrix['incoming_t_states']:
            for variant in range(matrix['register_variants']):
                add('helper-control', 'sequence', length=length, variant=variant, sr=t)
    return rows


def alias(address):
    return 0x01000000 + (address & 65535)


def source_bytes(case):
    found = []
    for position in range(case['length']):
        pattern = case['pattern']
        value = (0 if pattern == 'zero' else 255 if pattern == 'ones'
                 else position if pattern == 'increment'
                 else 0xaa if pattern == 'alternate' and position % 2 == 0
                 else 0x55 if pattern == 'alternate'
                 else 0x81 if pattern == 'isolated' and position == case['position']
                 else 0 if pattern == 'isolated'
                 else (case['index'] + position * 29 + 0x5d) & 255)
        if pattern == 'raw' and position == 7:
            value = case['value']
        found.append(value)
    return bytes(found)


def expected_registers(case):
    found = list(case['incoming'])
    found[1] = alias(case['destination']) + case['length'] // 4 * 4
    found[2] = alias(case['source'])
    if case['length']:
        byte = source_bytes(case)[-1]
        found[0] = byte if byte < 128 else 0xffffff00 | byte
    return found


def early_indices(rows):
    selected = [0, 1, 254, 255, 256, 257, 510, 511]
    selected += [row['index'] for row in rows if row['group'] == 'isolated'
                 and row['variant'] == 0 and row['sr'] == 0]
    selected += [row['index'] for row in rows if row['group'] == 'helper-control'
                 and row['variant'] == 0 and row['sr'] == 0]
    return selected


def boundary_bytes():
    """Position-independent observation stores, after every live GPR is saved."""
    words = [0x1f00 | register << 4 | register for register in range(15)]
    words += [0x0002, 0x1f0f, 0x61f3, 0x7140]
    for control in (0x002a, 0x0012, 0x000a, 0x001a):
        words += [control, 0x2102, 0x7104]
    words += [0x6012, 0x402b, 0x0009]
    return b''.join(word.to_bytes(2, 'big') for word in words)


def validate_observation(case, observed):
    integers = ['index', 'sr_before', 'sr_after', 'pr', 'gbr', 'mach', 'macl',
                'sp_before', 'sp_after', 'return_pc', 'ram_checked_bytes']
    if any(type(observed[key]) is not int for key in integers) or any(
            type(value) is not int for value in observed['gpr']):
        raise ValueError('copy observations require exact integer machine values')
    if observed['index'] != case['index'] or observed['gpr'] != expected_registers(case):
        raise ValueError('wrong CAN copy case or live GPR effects')
    expected = source_bytes(case).hex()
    if any(observed[name] != expected for name in ('source_before', 'source_after', 'destination_after')):
        raise ValueError('the required source/destination bytes were not copied')
    if observed['sr_before'] & 0x301 != case['sr']:
        raise ValueError('wrong prepared M/Q/T context')
    expected_t = int(case['length'] == 0)
    if observed['sr_after'] != (observed['sr_before'] & ~1) | expected_t:
        raise ValueError('wrong complete SR result')
    if [observed[name] for name in ('gbr', 'mach', 'macl')] != [case[name] for name in ('gbr', 'mach', 'macl')]:
        raise ValueError('wrong live control-register effects')
    if (observed['sp_before'] != observed['sp_after'] or observed['sp_before'] % 4
            or observed['pr'] != (0x2109a if case['caller'] else observed['return_pc'])):
        raise ValueError('wrong natural return or SP')
    frame = bytearray.fromhex(observed['frame_before'])
    if len(frame) != 64:
        raise ValueError('incomplete helper frame')
    for offset, value in ((52, case['incoming'][4]), (56, case['incoming'][3]),
                          (60, alias(case['source']))):
        frame[offset:offset + 4] = value.to_bytes(4, 'big')
    if observed['frame_after'] != frame.hex():
        raise ValueError('wrong helper stack writes or neighboring frame bytes')
    if (observed['ram_checked_bytes'] != 65536 or observed['unchanged_outside_destination'] is not True
            or observed['abi_preserved'] is not True or observed['input_preserved'] is not True):
        raise ValueError('incomplete full-RAM or observer-boundary checks')
