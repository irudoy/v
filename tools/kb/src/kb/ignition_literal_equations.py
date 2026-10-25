"""Independent complete-state equations for bounded ignition call observations.

Packet, consumed-source, fixture and original-terminal validation are separate
requirements. Equation success alone does not grant a native claim.
"""

import re

MASK = 0xFFFFFFFF
ABI = (0x18283848, 0x19293949, 0x1A2A3A4A, 0x1B2B3B4B,
       0x1C2C3C4C, 0x1D2D3D4D, 0x1E2E3E4E, 0x12344321, 0x10203040, 0x50607080)
SELECTORS = (0, 1, 2, 3, 4, 5, 255)
INPUTS = (
    (0x00000000, 0x00000000, 0x000000FF, 0x000),
    (0x000000FF, 0x0000FFFF, 0x00000000, 0x001),
    (0x12345680, 0xFFFF8000, 0x0000007F, 0x0F0),
    (0xFFFFFF7F, 0xFFFF0001, 0x00000080, 0x0F1),
    (0x89ABCDEF, 0x80000000, 0x12345678, 0x300),
    (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x3F1),
)


def raw(value, size):
    if type(value) is not str or len(value) != size * 2 or re.fullmatch('[0-9a-f]*', value) is None:
        raise ValueError('the C5 observation omits exact bounded big-endian bytes')
    return bytes.fromhex(value)


def words(data):
    if type(data) is not bytes or len(data) % 4:
        raise ValueError('the C5 observation has an incomplete word view')
    return tuple(int.from_bytes(data[at:at + 4], 'big') for at in range(0, len(data), 4))


def u32(value):
    return (value & MASK).to_bytes(4, 'big')


def require_observations(declared, observations):
    if (declared['selectors'] != list(SELECTORS)
            or declared['inputs'] != [list(row) for row in INPUTS]
            or declared['context_size'] != 80 or declared['observation_size'] != 572
            or declared['boundary'] != dict(bytes='57f6472a000b0009', scratch_register=7,
                                            return_stack_offset=24)):
        raise ValueError('the C5 observation changes the explicitly supported input or helper ABI')
    cases = tuple((window, selector, variant) for window in range(len(declared['windows']))
                  for selector in SELECTORS for variant in range(len(INPUTS)))
    if type(observations) is not list or len(observations) != len(cases):
        raise ValueError('the C5 observation omits a real changed-entry or branch case')
    keys = {'schema', 'index', 'window', 'selector', 'variant', 'context', 'observation',
            'callee', 'ram_before', 'ram_after', 'guards'}
    base_ram = bytes((0x5D + at * 19 + (at >> 8)) & 255 for at in range(65536))
    base_frame = b''.join(u32(0xA3B4C5D6 + index * 17) for index in range(48))
    summary = []
    for index, (packet, (window_index, selector, variant)) in enumerate(zip(observations, cases)):
        if type(packet) is not dict or set(packet) != keys:
            raise ValueError('the C5 observation changes its complete raw schema')
        for key, value in dict(schema=1, index=index, window=window_index,
                               selector=selector, variant=variant).items():
            if type(packet[key]) is not int or packet[key] != value:
                raise ValueError('the C5 observation changes its exact typed invocation identity')
        window = declared['windows'][window_index]
        family = declared['families'][window['family']]
        if family['canonical'] != window['table'] or len(family['slots']) != 5:
            raise ValueError('the C5 observation changes the owning map family')
        input_r0, input_r7, input_fifth, input_sr = INPUTS[variant]
        initial = [(0x1728394A + register * 0x110203 + variant * 0x1000101) & MASK
                   for register in range(15)]
        initial[0], initial[7], initial[12] = input_r0, input_r7, 0x0100817C
        context = words(raw(packet['context'], 80))
        expected_context = (*initial, 0x01003579, 0x13579BDF, 0x2468ACE0, input_sr, input_fifth)
        if context != expected_context:
            raise ValueError('the C5 actual complete entry context differs from its explicit case')
        observed = raw(packet['observation'], 572)
        exit_state = words(observed[:80])
        sp, continuation = words(observed[80:88])
        abi_before, abi_after = words(observed[88:136]), words(observed[136:184])
        frame_before, frame_after = observed[184:376], observed[376:568]
        sr_before = int.from_bytes(observed[568:572], 'big')
        call_bytes = raw(packet['callee'], 96)
        call = words(call_bytes)
        if (sr_before & 0x3F1 != input_sr or abi_before[:10] != ABI or abi_before != abi_after
                or sp != (abi_before[10] - 164) & MASK or continuation % 2):
            raise ValueError('the C5 actual driver flags, complete ABI or SP relation changed')
        selected = selector if selector < 5 else 0
        expected = list(initial)
        if window['overwrites_fifth']:
            expected[13] = input_r0 & 255
        expected[window['target_register']] = window['adapter']
        expected[0:7] = (selected * 4, 5, family['pointers'], window['stock'],
                         family['slots'][selected], window['axis5'], window['axis6'])
        expected[7] = input_r7 & 65535
        sr = (sr_before & ~1) | int(selector >= 5)
        fifth = input_r0 & 255 if window['overwrites_fifth'] else input_fifth
        expected_call = (sr, window['call'] + 4, context[17], context[16], context[15],
                         *reversed(expected), sp, fifth, 1, window['stock'])
        if call != expected_call:
            raise ValueError('the complete actual callee state disagrees with the independent C5 equation')
        expected[0], expected[7] = 0xA1B2C3D4, continuation
        expected_exit = (sr, continuation, context[17], context[16], context[15], *reversed(expected))
        if exit_state != expected_exit:
            raise ValueError('the complete actual window exit disagrees with its independent C5 equation')
        expected_frame_before = bytearray(base_frame)
        expected_frame_before[160:164] = u32(input_fifth)
        expected_frame_before[164:168] = u32(input_r7)
        expected_frame_before[184:188] = u32(continuation)
        if frame_before != expected_frame_before:
            raise ValueError('the actual C5 before-frame differs from its seeded words and staged return')
        expected_frame_after = bytearray(expected_frame_before)
        expected_frame_after[80:160] = b''.join(u32(value) for value in expected_call[:20])
        expected_frame_after[160:164] = u32(fifth)
        if frame_after != expected_frame_after:
            raise ValueError('the C5 call changes undeclared stack bytes or omits the real fifth argument')
        expected_ram = bytearray(base_ram)
        address = declared['selector'] & 65535
        if address in (0x819E, 0x819F) or address >= 65520:
            raise ValueError('the C5 declaration aliases its selector, argument source or observer guard')
        expected_ram[address] = selector
        expected_ram[0x819E:0x81A0] = (input_r7 & 65535).to_bytes(2, 'big')
        expected_ram[65520:] = bytes([0xA6]) * 16
        before_ram = raw(packet['ram_before'], 65536)
        after_ram = raw(packet['ram_after'], 65536)
        if before_ram != expected_ram or after_ram != expected_ram:
            raise ValueError('the actual C5 entry/exit RAM differs from its exact independent memory contract')
        if raw(packet['guards'], 32) != bytes([0xA6]) * 32:
            raise ValueError('the actual C5 observer changes its complete bounding guards')
        summary.append(dict(index=index, literal=window['literal'], call=window['call'],
                            selector=selector, variant=variant, table=family['slots'][selected]))
    return dict(scope='bounded-real-call-windows-and-adapter-ABI', observations=summary,
                reachability_proven=False, computed_consumer_absence_proven=False,
                stock_interpolation_body_executed=False, hardware_qualification=False)
