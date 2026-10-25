"""Independent physical operands, delayed calls and complete torque-ratio state."""
from kb import test_contract
from kb import torque_correction_ratio_contract as contract, torque_correction_ratio_semantics as numeric

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# Both root divisors are signed words or the positive constant6. Their zero
# cases branch before calling21BBC. The axis division has a positive interval.
# The actual263F4 tail retains nonzero R0 after SHLR8 and selects word reads.
INFEASIBLE_SITES = {0x26D0A, 0x26D0C, *range(0x21C70, 0x21CD6, 2),
    *range(0x26AAA, 0x26AB4, 2)}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x26C7A: 'fallthrough', 0x21BC0: 'fallthrough',
    0x21BDC: 'fallthrough', 0x26A9A: 'fallthrough'}
CALL_TARGETS = {0x658B8: 0x264CC, 0x264D6: 0x26984, 0x269AA: 0x26C78,
    0x64A40: 0x263F4, 0x64BA0: 0x21BBC, 0x64BEC: 0x21BBC, 0x64C58: 0x21BBC}
STACK_DELTAS = {0x658B8: -12, 0x264D6: -20, 0x269AA: -24,
    0x64A40: -36, 0x64BA0: -36, 0x64BEC: -36, 0x64C58: -36}
HELPER_ROM_SITES = {0x26986, 0x2699C, 0x2699E, 0x264DE, 0x264E4,
    0x26404, 0x26AA0, 0x26AA2}


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
        if len(raw) != 1:
            raise ValueError('the torque ratio control changes its exact byte width')
        rom.append(dict(site=site, mode='read', address=at, width_bytes=1,
            register=register, domain='rom', bytes=raw.hex()))
        return raw[0]
    if phase == 0:
        read(0x658B0, 0x11BC, 2, 7)
        write(0x658C2, 0x14E4, 2, 6, value['lookup']['value'])
        selector = read(0x658C4, 0x4181, 1, 0)
        if selector & 128:
            read(0x658CC, 0x1071, 1, 0)
        else:
            control(0x658DA, 0x8639, 4)
            read(0x658E0, 0x1071, 1, 0)
            read(0x658EC, 0x2772, 1, 2)
        control(0x65902, 0x8E51, 2)
        write(0x6591E, 0x14E2, 2, 2, value['correction'])
    else:
        read(0x64A34, 0x11B3, 1, 2)
        write(0x64A4A, 0x1608, 2, 2, value['weight']['value'])
        read(0x64A4E, 0x2408, 2, 9)
        read(0x64A52, 0x2410, 2, 8)
        read(0x64A5A, 0x19C6, 2, 4)
        read(0x64A72, 0x199E, 2, 7)
        write(0x64A8A, 0x199E, 2, 13, value['lag_initial'])
        if value['lag'] != value['lag_initial']:
            write(0x64A94, 0x199E, 2, 13, value['lag'])
        flag = read(0x64A9A, 0x24A3, 1, 7)
        if not flag & 8:
            for index in range(10):
                write(0x64ABA, 0x19F6 + 2 * index, 2, 13, value['lag'])
            write(0x64AC2, 0x24A3, 1, 7, flag | 8)
        delay = control(0x64AC6, 0x8C61, 6)
        if delay:
            read(0x64AEE, 0x19F6 + 2 * min(delay - 1, 9), 2, 6)
        write(0x64AFC, 0x19A0, 2, 11, value['delayed'])
        for index in range(9, 0, -1):
            raw = read(0x64B0A, 0x19F6 + 2 * (index - 1), 2, 5)
            write(0x64B1C, 0x19F6 + 2 * index, 2, 5, raw)
        write(0x64B22, 0x19F6, 2, 13, value['lag'])
        if control(0x64B24, 0x83C1, 0) & 32:
            read(0x64B2E, 0x18D4, 2, 5)
        if control(0x64B84, 0x8B38, 0) & 2:
            read(0x64B94, 0x16A3, 1, 6)
            write(0x64BAA, 0x34D6, 2, 2, value['stored_divisor'])
        else:
            write(0x64BB2, 0x34D6, 2, 5, value['stored_divisor'])
        source = read(0x64BB8, 0x19CC, 2, 6)
        first = value['first_ratio']
        if source == 32767:
            write(0x64BC4, 0x186C, 1, 2, 255)
        else:
            read(0x64BD4, 0x14E2, 2, 4)
            read(0x64BDA, 0x19CC, 2, 14)
            site = 0x64C06 if value['divisor'] else (0x64C16 if first['sum'] > 0 else 0x64C22)
            write(site, 0x186C, 1, 2, first['value'])
        source = read(0x64C26, 0x34B8, 2, 7)
        second = value['second_ratio']
        if source == 32767:
            write(0x64C32, 0x1864, 1, 2, 255)
        else:
            read(0x64C44, 0x14E2, 2, 6)
            site = 0x64C72 if value['delayed'] else (0x64C82 if second['sum'] > 0 else 0x64C8E)
            write(site, 0x1864, 1, 2, second['value'])
    same(bytes(out), value['memory'], 'the torque ratio physical path disagrees with independent complete numerical RAM')
    return ram, rom

def require(observed, result, value, fixture):
    phase = observed['phase']
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'],
        result['gbr'], *reversed(result['registers'])), 'the torque ratio phase changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the torque ratio phase changes complete frame, unrelated RAM or independent arithmetic publications')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the torque ratio phase changes natural return, saved registers, GBR or MACL')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRIES[phase]:
        raise ValueError('the torque ratio phase omits its complete natural entry trace')
    first = trace[0]['before']
    same(tuple(first[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
        ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
        'the torque ratio phase detaches complete entry CPU from immutable observed input')
    for index, row in enumerate(trace):
        next_site = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != next_site
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()):
            raise ValueError('the torque ratio phase changes a complete instruction or natural continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the torque ratio phase detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
        'the torque ratio phase changes executed exact instruction identities')
    delayed = {row['site'] + 2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the torque ratio phase omits or invents an actual delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the torque ratio phase violates a caller-scoped axis, curve or signed-divisor premise')
    calibration = observed['calibration_before']
    wanted_ram, wanted_rom = root_operands(phase, observed['memory_before'][0], calibration, value)
    same([row for row in result['accesses'] if row['domain'] == 'ram'], wanted_ram,
        'the torque ratio phase changes ordered physical RAM sites, widths, directions, operands or complete bytes')
    root_rom = []
    for event in result['accesses']:
        site = event['site']
        if event['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                domain='rom', bytes=fixture[at:at + width].hex()), 'the torque ratio phase changes an exact PC literal operand')
        elif site not in HELPER_ROM_SITES:
            root_rom.append(event)
        elif event['domain'] != 'rom' or event['mode'] != 'read' or event['width_bytes'] != 2:
            raise ValueError('the torque ratio helper changes a physical ROM word read')
    same(root_rom, wanted_rom, 'the torque ratio phase changes ordered actual ROM control sites, widths or bytes')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site + 4:
            raise ValueError('the torque ratio phase changes a real helper target or continuation')
        if site in STACK_DELTAS and call['sp'] != observed['sp'] + STACK_DELTAS[site]:
            raise ValueError('the torque ratio phase changes a complete nested call frame')
        start = next((i + 2 for i in range(cursor, len(trace) - 2) if trace[i]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the torque ratio phase replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
            (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
            'the torque ratio phase detaches complete helper arguments from its preceding delay slot')
        terminal = next((i for i in range(start, len(trace) - 1)
            if any(branch['kind'] == 'return' for branch in trace[i]['branches'])
            and trace[i + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the torque ratio phase omits an actual complete helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the torque ratio phase changes returned helper SP or PR')
        call_spans.append((call, start, terminal + 1, returned))
        registers = call['entry']['registers']

    def selected_call(site):
        selected = [row for row in call_spans if row[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the torque ratio path omits or repeats a complete natural helper call')
        return selected[0]

    def physical(site, address, register):
        raw = next((data[address - at:address - at + 2] for at, data in calibration.items()
            if at <= address and address + 2 <= at + len(data)), None)
        if raw is None:
            raise ValueError('the torque ratio path loses an exact complete calibration word')
        return dict(site=site, mode='read', address=address, width_bytes=2,
            register=register, domain='rom', bytes=raw.hex())

    if phase == 0:
        call, start, end, returned = selected_call(0x658B8)
        lookup = value['lookup']
        if (tuple(call['entry']['registers'][4:7]) != (0x14C1A, 0x14ABA, value['coordinate'])
                or returned['registers'][0] != lookup['value']):
            raise ValueError('the correction producer changes its real table/axis/coordinate or complete lookup return')
        axis_call, axis_start, axis_end, axis_returned = selected_call(0x264D6)
        registers = axis_call['entry']['registers']
        if ((registers[0], registers[4], registers[5]) != (0x14ABA, 14, value['coordinate'])
                or (axis_returned['registers'][4], axis_returned['registers'][5]) != (2 * lookup['index'], lookup['fraction'])
                or not start < axis_start <= axis_end < end):
            raise ValueError('the correction producer changes its complete eight-knot reverse search')
        expected = [physical(0x26986, 0x14ABA + 2 * index, 1)
            for index in range(7, lookup['index'] - 1, -1)]
        if lookup['fraction']:
            expected.extend((physical(0x2699C, 0x14ABA + 2 * lookup['index'], 1),
                physical(0x2699E, 0x14ABA + 2 * (lookup['index'] + 1), 0)))
        actual = [event for row in trace[axis_start:axis_end + 1] for event in row['accesses']
            if event['site'] in (0x26986, 0x2699C, 0x2699E)]
        same(actual, expected, 'the correction producer changes exact reverse-search word operands or physical order')
        expected = [physical(0x264DE, 0x14C1A + 2 * (lookup['index'] + 1), 0),
            physical(0x264E4, 0x14C1A + 2 * lookup['index'], 1)]
        actual = [event for row in trace[start:end + 1] for event in row['accesses']
            if event['site'] in (0x264DE, 0x264E4)]
        same(actual, expected, 'the correction producer omits unconditional neighbor-first coefficient reads')
        require_tail(trace, start, end, 0x264EC, 0x26740, call,
            (lookup['first'], lookup['second'], lookup['fraction']))
        division_calls = [row for row in call_spans if row[0]['site'] == 0x269AA]
        if len(division_calls) != int(bool(lookup['fraction'])):
            raise ValueError('the correction producer substitutes an axis quotient or invents a call')
        for axis_divide, first, last, axis_result in division_calls:
            registers = axis_divide['entry']['registers']
            axis = numeric.words(calibration[0x14ABA], 8)
            index = lookup['index']
            divisor = axis[index + 1] - axis[index]
            dividend = (value['coordinate'] - axis[index]) * 65536
            if ((registers[0], registers[1]) != (divisor, dividend)
                    or not 0 < divisor <= 65535 or not 0 < dividend < 1 << 32
                    or axis_result['registers'][0] != dividend // divisor):
                raise ValueError('the correction producer changes actual unsigned axis division operands or return')
        require_registers(trace, 0x65908, (4, 6),
            ((value['limit'] - value['selected']) & MASK, lookup['value']))
        require_registers(trace, 0x658C2, (6,), (lookup['value'],))
        require_registers(trace, 0x6591E, (2,), (value['correction'],))
    else:
        call, start, end, returned = selected_call(0x64A40)
        weight = value['weight']
        coordinate = observed['memory_before'][0][0x11B3] * 256
        if tuple(call['entry']['registers'][4:6]) != (0x14E52, coordinate):
            raise ValueError('the torque ratio consumer changes its real lag-table coordinate or pointer')
        expected_return = weight['value']
        if weight['endpoint']:
            expected_return = numeric.signed_word(weight['value']) & MASK
            expected = [physical(0x26404, 0x14E70, 0)]
        else:
            expected = [physical(0x26AA0, 0x14E52 + 2 * weight['index'], 1),
                physical(0x26AA2, 0x14E52 + 2 * (weight['index'] + 1), 0)]
            require_tail(trace, start, end, 0x26400, 0x26A64, call, None)
            curve = numeric.words(calibration[0x14E52], 16)
            require_tail(trace, start, end, 0x26AB8, 0x26740, call,
                (curve[weight['index']], curve[weight['index'] + 1], weight['fraction']))
        actual = [event for row in trace[start:end + 1] for event in row['accesses']
            if event['site'] in (0x26404, 0x26AA0, 0x26AA2)]
        same(actual, expected, 'the torque ratio consumer changes its actual word endpoint or neighbor read')
        if returned['registers'][0] != expected_return:
            raise ValueError('the torque ratio consumer replaces the complete signed endpoint or interpolation return')
        require_registers(trace, 0x64A4A, (2,), (weight['value'],))
        require_registers(trace, 0x64A6E, (2, 4), (weight['value'], value['target'] & MASK))
        require_registers(trace, 0x64A7A, (2, 7), (65536 - weight['value'], value['previous'] & MASK))
        require_registers(trace, 0x64A8A, (13,), (value['lag_initial'] & MASK,))
        require_registers(trace, 0x64AFC, (11,), (value['delayed'] & MASK,))
        expected_divisions = {}
        if value['factor_enabled']:
            expected_divisions[0x64BA0] = (6, value['selected_divisor'] * (6 - value['count']), value['factor_quotient'])
        for site, ratio in ((0x64BEC, value['first_ratio']), (0x64C58, value['second_ratio'])):
            if not ratio['sentinel'] and ratio['divisor']:
                expected_divisions[site] = (ratio['divisor'], ratio['sum'] * 256, ratio['quotient'])
        actual_divisions = [row for row in call_spans if row[0]['target'] == 0x21BBC]
        if [row[0]['site'] for row in actual_divisions] != list(expected_divisions):
            raise ValueError('the torque ratio consumer omits, repeats or invents a complete signed division')
        for divide, first, last, division_returned in actual_divisions:
            divisor, dividend, quotient = expected_divisions[divide['site']]
            if (tuple(divide['entry']['registers'][:2]) != (divisor & MASK, dividend & MASK)
                    or division_returned['registers'][0] != quotient & MASK):
                raise ValueError('the torque ratio consumer changes actual carried signed dividend, divisor or return')


def require_registers(trace, site, registers, values):
    selected = [row for row in trace if row['site'] == site]
    if len(selected) != 1 or tuple(selected[0]['before']['registers'][r] for r in registers) != values:
        raise ValueError('the torque ratio path replaces a complete live operand with matching publication bytes')


def require_tail(trace, start, end, delay_site, target, call, values):
    selected = [row for row in trace[start:end + 1] if row['site'] == delay_site]
    if (len(selected) != 1 or not selected[0]['delay_slot'] or selected[0]['next'] != target
            or selected[0]['after']['registers'][15] != call['sp']
            or selected[0]['after']['pr'] != call['return_address']):
        raise ValueError('the torque ratio path changes an actual delayed tail, restored SP or PR')
    if values is not None:
        registers = selected[0]['after']['registers']
        same((registers[0], registers[2], registers[3]), values,
            'the torque ratio interpolation tail loses complete actual first/second/fraction operands')


def require_handoff(producer, consumer, producer_value, consumer_value):
    if (producer['phase'] != 0 or consumer['phase'] != 1 or producer['pair'] != consumer['pair']
            or producer['memory_after'] != consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'], consumer['calibration_before'])
            or producer['bound_after'] != consumer['bound_before']):
        raise ValueError('the torque ratio handoff changes complete actual RAM, calibration or exact code')
    carried = numeric.word(producer['memory_after'][0], 0x14E2)
    if carried != producer_value['correction'] or carried != consumer_value['correction']:
        raise ValueError('the torque ratio handoff replaces the actual producer correction with a synthetic input')
