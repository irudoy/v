"""Independent exact ratio/state operands, natural calls and complete phase state."""
from kb import test_contract
from kb import ratio_state_quantity_contract as contract, ratio_state_quantity_semantics as numeric

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# The unsigned producer divisor is at least3 and can exceed65535. Both signed
# consumer divisors are unsigned words or1000; the first admits the real zero
# handler. The physical axis interval is positive and the curve tail is word.
INFEASIBLE_SITES = {0x751B4, 0x26D0A, 0x26D0C, 0x21BCC, 0x21BCE,
    *range(0x21C7C, 0x21CD6, 2), *range(0x21D6A, 0x21D76, 2),
    *range(0x26AAA, 0x26AB4, 2)}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x751B0: 'taken', 0x21CE4: 'fallthrough', 0x21BCA: 'taken',
    0x21BDC: 'fallthrough', 0x26A9A: 'fallthrough', 0x26C7A: 'fallthrough'}
CALL_TARGETS = {0x751C0: 0x21CE0, 0x751FC: 0x263F4, 0x76576: 0x224FA,
    0x7659A: 0x21BBC, 0x765C2: 0x264CC, 0x264D6: 0x26984,
    0x269AA: 0x26C78, 0x7669C: 0x21BBC}
STACK_DELTAS = {0x751C0: -12, 0x751FC: -12, 0x76576: -40, 0x7659A: -40,
    0x765C2: -40, 0x264D6: -48, 0x269AA: -52, 0x7669C: -40}
HELPER_ROM_SITES = {0x26404, 0x26AA0, 0x26AA2, 0x26986, 0x2699C,
    0x2699E, 0x264DE, 0x264E4}


def same(actual, expected, reason):
    if not test_contract.exact(actual, expected):
        raise ValueError(reason)


def root_operands(phase, memory, calibration, value):
    out = bytearray(memory)
    ram, rom = [], []
    def read(site, at, width, register):
        raw = bytes(out[at:at + width])
        ram.append(dict(site=site, mode='read', address=RAM_BASE + at, width_bytes=width,
            register=register, domain='ram', bytes=raw.hex()))
        return int.from_bytes(raw, 'big')
    def write(site, at, width, register, number):
        raw = (number & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')
        ram.append(dict(site=site, mode='write', address=RAM_BASE + at, width_bytes=width,
            register=register, domain='ram', bytes=raw.hex()))
        out[at:at + width] = raw
    def control(site, at, register):
        raw = calibration[at]
        if len(raw) != 2:
            raise ValueError('the ratio-state control changes its exact physical word width')
        rom.append(dict(site=site, mode='read', address=at, width_bytes=2,
            register=register, domain='rom', bytes=raw.hex()))
    if phase == 0:
        source = read(0x7517E, 0x1702, 2, 5)
        if source:
            read(0x7518A, 0x10D6, 2, 4)
            read(0x75190, 0x1582, 2, 7)
        write(0x751DA, 0x17E2, 2, 2, value['primary'])
        control(0x751DC, 0x920E, 2)
        write(0x751FA, 0x16B2, 2, 5, value['coordinate'])
        write(0x75204, 0x19A2, 2, 2, value['quantity'])
    else:
        read(0x76568, 0x19A2, 2, 6)
        read(0x7656E, 0x1770, 2, 2)
        read(0x7658E, 0x18D2, 2, 2)
        control(0x76594, 0x944E, 2)
        if not value['first_divisor']:
            write(0x21C74, 0x9818, 4, 2, 0x44E)
        write(0x765B4, 0x145A, 2, 0, value['first'])
        read(0x765BA, 0x1152, 2, 7)
        write(0x765D0, 0x1792, 2, 11, value['curve']['centered'])
        read(0x765D4, 0x1152, 2, 14)
        control(0x765D6, 0x95A0, 7)
        read(0x765DA, 0x1540, 4, 0)
        control(0x76650, 0x918E, 14)
        write(0x76652, 0x14F4, 2, 5, value['offset_target'])
        write(0x76658, 0x1540, 4, 0, value['accumulator_one']['updated'])
        read(0x7665C, 0x14F8, 4, 0)
        write(0x76684, 0x14F8, 4, 0, value['accumulator_two']['updated'])
        write(0x76690, 0x14F6, 2, 2, value['centered_state'])
        control(0x76694, 0x928E, 0)
        write(0x766CA, 0x1508, 2, 6, value['feedback'])
        read(0x766CE, 0x145A, 2, 0)
        control(0x766EC, 0x928C, 5)
        write(0x766F0, 0x177E, 2, 6, value['target'] - 32768)
        read(0x766FA, 0x177C, 2, 7)
        write(0x7672A, 0x177C, 2, 6, value['result'])
    same(bytes(out), value['memory'], 'the ratio-state ordered physical writes disagree with complete independent numerical RAM')
    return ram, rom


def require(observed, result, value, fixture):
    phase = observed['phase']
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'],
        result['gbr'], *reversed(result['registers'])), 'the ratio-state phase changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the ratio-state phase changes complete frame, unrelated RAM or independent arithmetic publications')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][14:15] if phase == 0 else result['registers'][8:15]) != (observed['context'][14:15] if phase == 0 else observed['context'][8:15])):
        raise ValueError('the ratio-state phase changes natural return, saved registers, GBR or MACL')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRIES[phase]:
        raise ValueError('the ratio-state phase omits its complete natural entry trace')
    first = trace[0]['before']
    same(tuple(first[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
        ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
        'the ratio-state phase detaches complete entry CPU from immutable observed input')
    for index, row in enumerate(trace):
        next_site = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != next_site
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()):
            raise ValueError('the ratio-state phase changes a complete instruction or natural continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the ratio-state phase detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
        'the ratio-state phase changes executed exact instruction identities')
    delayed = {row['site'] + 2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the ratio-state phase omits or invents an actual delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the ratio-state phase violates a caller-scoped axis, curve or signed-divisor premise')
    calibration = observed['calibration_before']
    wanted_ram, wanted_rom = root_operands(phase, observed['memory_before'][0], calibration, value)
    same([row for row in result['accesses'] if row['domain'] == 'ram'], wanted_ram,
        'the ratio-state phase changes ordered physical RAM sites, widths, directions, operands or complete bytes')
    root_rom = []
    for event in result['accesses']:
        site = event['site']
        if event['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                domain='rom', bytes=fixture[at:at + width].hex()), 'the ratio-state phase changes an exact PC literal operand')
        elif site not in HELPER_ROM_SITES:
            root_rom.append(event)
        elif event['domain'] != 'rom' or event['mode'] != 'read' or event['width_bytes'] != 2:
            raise ValueError('the ratio-state helper changes a physical ROM word read')
    same(root_rom, wanted_rom, 'the ratio-state phase changes ordered actual ROM control sites, widths or bytes')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site + 4:
            raise ValueError('the ratio-state phase changes a real helper target or continuation')
        if site in STACK_DELTAS and call['sp'] != observed['sp'] + STACK_DELTAS[site]:
            raise ValueError('the ratio-state phase changes a complete nested call frame')
        start = next((i + 2 for i in range(cursor, len(trace) - 2) if trace[i]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the ratio-state phase replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
            (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
            'the ratio-state phase detaches complete helper arguments from its preceding delay slot')
        terminal = next((i for i in range(start, len(trace) - 1)
            if any(branch['kind'] == 'return' for branch in trace[i]['branches'])
            and trace[i + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the ratio-state phase omits an actual complete helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the ratio-state phase changes returned helper SP or PR')
        call_spans.append((call, start, terminal + 1, returned))
        registers = call['entry']['registers']

    def selected_call(site):
        selected = [row for row in call_spans if row[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the ratio-state path omits or repeats a complete natural helper call')
        return selected[0]

    def physical(site, address, register):
        raw = next((data[address - at:address - at + 2] for at, data in calibration.items()
            if at <= address and address + 2 <= at + len(data)), None)
        if raw is None:
            raise ValueError('the ratio-state path loses an exact complete calibration word')
        return dict(site=site, mode='read', address=address, width_bytes=2,
            register=register, domain='rom', bytes=raw.hex())

    if phase == 0:
        expected = [0x751C0, 0x751FC] if value['coordinate_source'] else [0x751FC]
        same([row[0]['site'] for row in call_spans], expected,
            'the ratio producer omits, invents or reorders a complete real call')
        if value['coordinate_source']:
            division, start, end, returned = selected_call(0x751C0)
            same(tuple(division['entry']['registers'][:2]), (value['divisor'], value['dividend']),
                'the ratio producer substitutes its actual wide unsigned dividend or divisor')
            same(returned['registers'][0], value['quotient'],
                'the ratio producer replaces its actual unsigned division return')
        call, start, end, returned = selected_call(0x751FC)
        lookup = value['curve']
        same(tuple(call['entry']['registers'][4:6]), (0x15770, value['coordinate']),
            'the ratio producer changes the actual table pointer or carried coordinate')
        if lookup['endpoint']:
            expected = [physical(0x26404, 0x1578E, 0)]
        else:
            expected = [physical(0x26AA0, 0x15770 + 2 * lookup['index'], 1),
                physical(0x26AA2, 0x15770 + 2 * (lookup['index'] + 1), 0)]
            require_tail(trace, start, end, 0x26400, 0x26A64, call, None)
            curve = numeric.words(calibration[0x15770], 16)
            require_tail(trace, start, end, 0x26AB8, 0x26740, call,
                (curve[lookup['index']], curve[lookup['index'] + 1], lookup['fraction']))
        actual = [event for row in trace[start:end + 1] for event in row['accesses']
            if event['site'] in (0x26404, 0x26AA0, 0x26AA2)]
        same(actual, expected, 'the ratio producer changes the actual endpoint or ordered neighboring word reads')
        same(returned['registers'][0], lookup['returned'],
            'the ratio producer substitutes a signed endpoint or complete interpolation return')
        require_registers(trace, 0x751E4, (6, 2), (value['primary'], numeric.word(calibration[0x920E], 0)))
        require_registers(trace, 0x751E8, (6,), (value['product'],))
        reconstructed = ((0xFFFF0000 if value['product'] & 0x80000000 else 0)
            | ((value['product'] // 32768) & 65535))
        require_registers(trace, 0x751EE, (6,), (reconstructed,))
        require_registers(trace, 0x751FA, (5,), (value['coordinate'],))
        require_registers(trace, 0x75204, (2,), (lookup['returned'],))
    else:
        expected = [0x76576, 0x7659A, 0x765C2, 0x264D6]
        if value['curve']['fraction']:
            expected.append(0x269AA)
        expected.append(0x7669C)
        same([row[0]['site'] for row in call_spans], expected,
            'the state consumer omits, invents or reorders a complete natural helper call')
        shift, first, last, shifted = selected_call(0x76576)
        same(shift['entry']['registers'][0], value['product'],
            'the state consumer replaces the actual post-delay unsigned product input to224FA')
        same(shifted['registers'][0], value['shifted_return'],
            'the state consumer substitutes a logical shift for the actual signed six-bit shift return')
        for site, divisor, dividend, quotient in (
                (0x7659A, value['first_divisor'], value['first_dividend'], value['first_quotient']),
                (0x7669C, 1000, value['feedback_dividend'], value['feedback_quotient'])):
            divide, first, last, divided = selected_call(site)
            same(tuple(divide['entry']['registers'][:2]), (divisor, dividend & MASK),
                'the state consumer changes an actual complete signed dividend or unsigned-word divisor')
            same(divided['registers'][0], quotient & MASK,
                'the state consumer replaces a complete signed or zero-error division return')
        call, start, end, returned = selected_call(0x765C2)
        lookup = value['curve']
        same(tuple(call['entry']['registers'][4:7]), (0x15276, 0x15286, value['coordinate']),
            'the state consumer changes its actual centered map, shared axis or coordinate')
        same(returned['registers'][0], lookup['value'],
            'the state consumer replaces the actual complete centered-map return')
        axis_call, axis_start, axis_end, axis_returned = selected_call(0x264D6)
        registers = axis_call['entry']['registers']
        if ((registers[0], registers[4], registers[5]) != (0x15286, 14, value['coordinate'])
                or (axis_returned['registers'][4], axis_returned['registers'][5]) != (2 * lookup['index'], lookup['fraction'])
                or not start < axis_start <= axis_end < end):
            raise ValueError('the state consumer changes its complete centered eight-knot reverse search')
        expected = [physical(0x26986, 0x15286 + 2 * index, 1)
            for index in range(7, lookup['index'] - 1, -1)]
        if lookup['fraction']:
            expected.extend((physical(0x2699C, 0x15286 + 2 * lookup['index'], 1),
                physical(0x2699E, 0x15286 + 2 * (lookup['index'] + 1), 0)))
        actual = [event for row in trace[axis_start:axis_end + 1] for event in row['accesses']
            if event['site'] in (0x26986, 0x2699C, 0x2699E)]
        same(actual, expected, 'the state consumer changes complete ordered reverse-search physical operands')
        expected = [physical(0x264DE, 0x15276 + 2 * (lookup['index'] + 1), 0),
            physical(0x264E4, 0x15276 + 2 * lookup['index'], 1)]
        actual = [event for row in trace[start:end + 1] for event in row['accesses']
            if event['site'] in (0x264DE, 0x264E4)]
        same(actual, expected, 'the state consumer omits its unconditional neighbor-first read including the shared axis word')
        require_tail(trace, start, end, 0x264EC, 0x26740, call,
            (lookup['first'], lookup['second'], lookup['fraction']))
        if lookup['fraction']:
            divide, first, last, divided = selected_call(0x269AA)
            axis = numeric.words(calibration[0x15276], 16)[8:]
            index = lookup['index']
            divisor = axis[index + 1] - axis[index]
            dividend = (value['coordinate'] - axis[index]) * 65536
            same(tuple(divide['entry']['registers'][:2]), (divisor, dividend),
                'the state consumer changes actual positive axis division operands')
            if not 0 < divisor <= 65535 or divided['registers'][0] != lookup['fraction']:
                raise ValueError('the state consumer replaces its complete unsigned axis quotient')
        require_registers(trace, 0x76572, (6, 2), (value['quantity'], value['other']))
        require_registers(trace, 0x76592, (6, 2),
            (value['scaled_product'], numeric.signed_word(numeric.word(observed['memory_before'][0], 0x18D2)) & MASK))
        require_registers(trace, 0x765D0, (11,), (lookup['initial_live_signed_offset'],))
        require_registers(trace, 0x76602, (2, 4),
            (value['accumulator_one']['updated'], value['accumulator_one']['previous']))
        require_registers(trace, 0x7660C, (6,), (value['delta'] & MASK,))
        require_registers(trace, 0x7661E, (2, 6), (value['delta_bounded'] & MASK, 283))
        require_registers(trace, 0x76636, (6,), (value['delta_scaled'] & MASK,))
        require_registers(trace, 0x76652, (5,), (value['offset_target'],))
        require_registers(trace, 0x7667E, (6,), (value['accumulator_two']['updated'],))
        require_registers(trace, 0x766D0, (11,), (lookup['centered'] & MASK,))
        require_registers(trace, 0x766D4, (0,), (value['error'] & MASK,))
        require_registers(trace, 0x766F8, (14, 5), (value['target'] & MASK, value['lag_gain']))
        require_registers(trace, 0x7670A, (6,), (value['lag_product'],))
        require_registers(trace, 0x7670E, (2,), (value['lag_initial'] & MASK,))
        require_registers(trace, 0x7672A, (6,), (value['result'],))
        if any(row['before']['gbr'] != RAM_BASE + 0x128C for row in trace
                if 0x76564 <= row['site'] <= 0x7672C):
            raise ValueError('the state consumer loses its actual relocated GBR during the complete body')


def require_registers(trace, site, registers, values):
    selected = [row for row in trace if row['site'] == site]
    if len(selected) != 1 or tuple(selected[0]['before']['registers'][r] for r in registers) != values:
        raise ValueError('the ratio-state path replaces a complete live operand with matching publication bytes')


def require_tail(trace, start, end, delay_site, target, call, values):
    selected = [row for row in trace[start:end + 1] if row['site'] == delay_site]
    if (len(selected) != 1 or not selected[0]['delay_slot'] or selected[0]['next'] != target
            or selected[0]['after']['registers'][15] != call['sp']
            or selected[0]['after']['pr'] != call['return_address']):
        raise ValueError('the ratio-state path changes an actual delayed tail, restored SP or PR')
    if values is not None:
        registers = selected[0]['after']['registers']
        same((registers[0], registers[2], registers[3]), values,
            'the ratio-state interpolation tail loses complete actual first/second/fraction operands')


def require_handoff(producer, consumer, producer_value, consumer_value):
    if (producer['phase'] != 0 or consumer['phase'] != 1 or producer['pair'] != consumer['pair']
            or producer['memory_after'] != consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'], consumer['calibration_before'])
            or producer['bound_after'] != consumer['bound_before']):
        raise ValueError('the ratio-state handoff changes complete actual RAM, calibration or exact code')
    carried = numeric.word(producer['memory_after'][0], 0x19A2)
    if carried != producer_value['quantity'] or carried != consumer_value['quantity']:
        raise ValueError('the ratio-state handoff replaces actual75204 publication and76568 consumption with a synthetic input')
