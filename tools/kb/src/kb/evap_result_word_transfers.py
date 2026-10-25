"""Independent EVAP physical words, live wide arithmetic and complete call state."""
from kb import test_contract
from kb import evap_result_word_contract as contract, evap_result_word_semantics as numeric

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# Root divisions receive a nonzero uint16 parameter. Axis intervals are
# positive. The26388 tail enters26A84 with R0=00F0 and selects byte reads.
# After the high quotient cap, the combined quotient shifted by5 fits uint16.
# The remainder call has high/parameter<=31, so its short division path suffices.
INFEASIBLE_SITES = {0x26D0A, 0x26D0C, *range(0x26A9C, 0x26AAA, 2),
    *range(0x21D6A, 0x21DC6, 2), *range(0x21F72, 0x2202E, 2)}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x26C7A: 'fallthrough', 0x26A9A: 'taken',
    0x21CE4: 'fallthrough', 0x21CEA: 'fallthrough', 0x21F44: 'fallthrough',
    0x21F4A: 'fallthrough', 0x21F52: 'fallthrough', 0xB226C: 'fallthrough'}
CALL_TARGETS = {0xB20EC: 0x26388, 0xB2132: 0x26388, 0xB2116: 0x26474,
    0xB2150: 0x26474, 0xB2166: 0x264F8, 0xB222A: 0x21CE0,
    0xB2240: 0x21F40, 0xB2258: 0x21CE0, 0x2647E: 0x26944,
    0x26502: 0x26984, 0x2696A: 0x26C78, 0x269AA: 0x26C78}
STACK_DELTAS = {site: -40 for site in (0xB20EC, 0xB2132, 0xB2116, 0xB2150,
    0xB2166, 0xB222A, 0xB2240, 0xB2258)}
STACK_DELTAS.update({0x2647E: -48, 0x26502: -48, 0x2696A: -52, 0x269AA: -52})
HELPER_ROM_SITES = {0x26398, 0x26AAC, 0x26AAE, 0x26486, 0x2648C,
    0x2650A, 0x26510, 0x26946, 0x2695C, 0x2695E, 0x26986, 0x2699C, 0x2699E}


def same(actual, expected, reason):
    if not test_contract.exact(actual, expected):
        raise ValueError(reason)


def root_operands(memory, calibration, value):
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
    def control(site, at, width, register):
        raw = calibration[at]
        if len(raw) != width:
            raise ValueError('the EVAP control changes an exact complete physical width')
        rom.append(dict(site=site, mode='read', address=at, width_bytes=width,
            register=register, domain='rom', bytes=raw.hex()))
        return int.from_bytes(raw, 'big')
    mode = control(0xB20AA, 0x893E, 1, 0)
    if mode & 64:
        control(0xB20C8, 0x94CC, 2, 2)
    else:
        read(0xB20BA, 0x272A, 2, 2)
    write(0xB20CE, 0x3062, 2, 2, value['baseline'])
    mode = control(0xB20D2, 0x893F, 1, 0)
    active = bool(read(0xB20DC, 0x41E5, 1, 0) & 4) if mode & 16 else False
    if active:
        read(0xB20E8, 0x10FA, 1, 6)
        write(0xB20F6, 0x2F8D, 1, 2, value['coefficient_a']['value'])
        read(0xB20FA, 0x10F9, 1, 5)
        threshold = control(0xB2104, 0x85C1, 1, 6)
        read(0xB2106, 0x272A, 2, 2)
        if memory[0x10F9] < threshold:
            write(0xB2120, 0x2F94, 1, 2, value['coefficient_b']['value'])
        else:
            write(0xB2158, 0x2F94, 1, 6, value['coefficient_b']['value'])
    else:
        read(0xB212E, 0x10FA, 1, 6)
        write(0xB213C, 0x2F8D, 1, 6, value['coefficient_a']['value'])
        read(0xB2142, 0x272A, 2, 2)
        write(0xB2158, 0x2F94, 1, 6, value['coefficient_b']['value'])
    read(0xB2160, 0x2C92, 2, 7)
    write(0xB2172, 0x3240, 2, 6, value['transform']['value'])
    if value['difference'] > 0 and value['parameter']:
        control(0xB21F6, 0x8813, 1, 2)
        read(0xB21F8, 0x3062, 2, 5)
    site, register = (0xB2276, 5) if value['branch'] == 'normalized-positive' else (0xB227C, 2)
    write(site, 0x3018, 2, register, value['normalized'])
    read(0xB2282, 0x2F8D, 1, 6)
    read(0xB228A, 0x2F94, 1, 6)
    write(0xB22A6, 0x301C, 2, 6, value['result'])
    same(bytes(out), value['memory'], 'the EVAP physical words disagree with independent complete numerical RAM')
    return ram, rom

def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'],
        result['gbr'], *reversed(result['registers'])), 'the EVAP writer phase changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the EVAP writer phase changes complete frame, unrelated RAM or independent arithmetic publications')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the EVAP writer phase changes natural return, saved registers, GBR or MACL')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the EVAP writer phase omits its complete natural entry trace')
    first = trace[0]['before']
    same(tuple(first[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
        ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
        'the EVAP writer phase detaches complete entry CPU from immutable observed input')
    for index, row in enumerate(trace):
        next_site = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != next_site
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()):
            raise ValueError('the EVAP writer phase changes a complete instruction or natural continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the EVAP writer phase detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
        'the EVAP writer phase changes executed exact instruction identities')
    delayed = {row['site'] + 2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the EVAP writer phase omits or invents an actual delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the EVAP writer phase violates a caller-scoped axis, curve or signed-divisor premise')
    calibration = observed['calibration_before']
    wanted_ram, wanted_rom = root_operands( observed['memory_before'][0], calibration, value)
    same([row for row in result['accesses'] if row['domain'] == 'ram'], wanted_ram,
        'the EVAP writer phase changes ordered physical RAM sites, widths, directions, operands or complete bytes')
    root_rom = []
    for event in result['accesses']:
        site = event['site']
        if event['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                domain='rom', bytes=fixture[at:at + width].hex()), 'the EVAP writer phase changes an exact PC literal operand')
        elif site not in HELPER_ROM_SITES:
            root_rom.append(event)
        elif event['domain'] != 'rom' or event['mode'] != 'read' or event['width_bytes'] != 2:
            raise ValueError('the EVAP writer helper changes a physical ROM word read')
    same(root_rom, wanted_rom, 'the EVAP writer phase changes ordered actual ROM control sites, widths or bytes')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site + 4:
            raise ValueError('the EVAP writer phase changes a real helper target or continuation')
        if site in STACK_DELTAS and call['sp'] != observed['sp'] + STACK_DELTAS[site]:
            raise ValueError('the EVAP writer phase changes a complete nested call frame')
        start = next((i + 2 for i in range(cursor, len(trace) - 2) if trace[i]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the EVAP writer phase replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
            (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
            'the EVAP writer phase detaches complete helper arguments from its preceding delay slot')
        terminal = next((i for i in range(start, len(trace) - 1)
            if any(branch['kind'] == 'return' for branch in trace[i]['branches'])
            and trace[i + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the EVAP writer phase omits an actual complete helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the EVAP writer phase changes returned helper SP or PR')
        call_spans.append((call, start, terminal + 1, returned))
        registers = call['entry']['registers']

    def selected_call(site):
        rows = [row for row in call_spans if row[0]['site'] == site]
        if len(rows) != 1:
            raise ValueError('the EVAP writer omits or repeats a complete actual helper call')
        return rows[0]

    def operand(site, address, width, register):
        matches = [(at, raw) for at, raw in calibration.items() if at <= address and address + width <= at + len(raw)]
        if len(matches) != 1:
            raise ValueError('the EVAP writer loses a complete authoritative calibration operand')
        at, raw = matches[0]
        return dict(site=site, mode='read', address=address, width_bytes=width,
            register=register, domain='rom', bytes=raw[address - at:address - at + width].hex())

    a_site = 0xB20EC if value['active'] else 0xB2132
    a_call, first, last, a_returned = selected_call(a_site)
    a_value = value['coefficient_a']
    coordinate = observed['memory_before'][0][0x10FA]
    if (tuple(a_call['entry']['registers'][4:6]) != (value['table_a'], coordinate)
            or a_returned['registers'][0] != a_value['returned']):
        raise ValueError('the EVAP writer changes its actual fixed byte-curve arguments or signed endpoint return')
    if a_value['endpoint']:
        expected = [operand(0x26398, value['table_a'] + 15, 1, 0)]
    else:
        expected = [operand(0x26AAC, value['table_a'] + a_value['index'], 1, 1),
            operand(0x26AAE, value['table_a'] + a_value['index'] + 1, 1, 0)]
        require_tail(trace, first, last, 0x26394, 0x26A84, a_call, None)
        raw = calibration[value['table_a']]
        require_tail(trace, first, last, 0x26AB8, 0x26740, a_call,
            (raw[a_value['index']], raw[a_value['index'] + 1], a_value['fraction']))
    actual = [event for row in trace[first:last + 1] for event in row['accesses']
        if event['site'] in (0x26398, 0x26AAC, 0x26AAE)]
    same(actual, expected, 'the EVAP writer changes exact fixed-curve byte reads or their order')

    b_site = 0xB2116 if value['active'] and value['table_b'] == 0x1259A else 0xB2150
    for site, table, axis, coordinate, lookup, width, axis_site, axis_reads, table_reads, tail_site in (
            (b_site, value['table_b'], 0x12A5A, value['coordinate_b'], value['coefficient_b'],
             1, 0x2647E, (0x26946, 0x2695C, 0x2695E), (0x26486, 0x2648C), 0x26494),
            (0xB2166, 0x152D6, 0x13C18, numeric.word(observed['memory_before'][0], 0x2C92), value['transform'],
             2, 0x26502, (0x26986, 0x2699C, 0x2699E), (0x2650A, 0x26510), 0x26518)):
        call, first, last, returned = selected_call(site)
        if (tuple(call['entry']['registers'][4:7]) != (table, axis, coordinate)
                or returned['registers'][0] != lookup['value']):
            raise ValueError('the EVAP writer changes actual indexed curve arguments or full natural return')
        axis_call, begin, end, axis_returned = selected_call(axis_site)
        registers = axis_call['entry']['registers']
        count = 8 if width == 1 else 16
        if ((registers[0], registers[4], registers[5]) != (axis, width * (count - 1), coordinate)
                or (axis_returned['registers'][4], axis_returned['registers'][5]) != (width * lookup['index'], lookup['fraction'])
                or not first < begin <= end < last):
            raise ValueError('the EVAP writer changes its actual reverse-axis search, index or fraction')
        expected = [operand(axis_reads[0], axis + width * index, width, 1)
            for index in range(count - 1, lookup['index'] - 1, -1)]
        if lookup['fraction']:
            expected.extend((operand(axis_reads[1], axis + width * lookup['index'], width, 1),
                operand(axis_reads[2], axis + width * (lookup['index'] + 1), width, 0)))
        actual = [event for row in trace[begin:end + 1] for event in row['accesses'] if event['site'] in axis_reads]
        same(actual, expected, 'the EVAP writer changes complete reverse-axis reads or neighboring divisor bytes')
        actual = [event for row in trace[first:last + 1] for event in row['accesses'] if event['site'] in table_reads]
        expected = [operand(table_reads[0], table + width * (lookup['index'] + 1), width, 0),
            operand(table_reads[1], table + width * lookup['index'], width, 1)]
        same(actual, expected, 'the EVAP writer omits unconditional neighbor-first indexed-curve operands')
        require_tail(trace, first, last, tail_site, 0x26740, call,
            (lookup['first'], lookup['second'], lookup['fraction']))
        divide_site = 0x2696A if width == 1 else 0x269AA
        divisions = [row for row in call_spans if row[0]['site'] == divide_site and begin <= row[1] <= end]
        if len(divisions) != int(bool(lookup['fraction'])):
            raise ValueError('the EVAP writer invents or omits actual positive axis division')
        for divide, unused_first, unused_last, division_returned in divisions:
            values = tuple(calibration[axis]) if width == 1 else numeric.words(calibration[axis], 16)
            index = lookup['index']
            divisor, dividend = values[index + 1] - values[index], (coordinate - values[index]) * 65536
            if (tuple(divide['entry']['registers'][:2]) != (divisor, dividend)
                    or not 0 < divisor <= 65535 or not 0 < dividend < 1 << 32
                    or division_returned['registers'][0] != dividend // divisor):
                raise ValueError('the EVAP writer changes a real unsigned axis numerator, divisor or return')

    expected_divisions = {}
    if value['difference'] > 0 and value['parameter'] and not value['product_capped']:
        expected_divisions[0xB222A] = (value['parameter'], value['high'], value['quotient_high'])
        if not value['quotient_capped']:
            expected_divisions[0xB2240] = (value['parameter'], value['high'], value['remainder_high'])
            expected_divisions[0xB2258] = (value['parameter'], value['low_dividend'], value['quotient_low'])
    divisions = [row for row in call_spans if row[0]['site'] in (0xB222A, 0xB2240, 0xB2258)]
    if [row[0]['site'] for row in divisions] != list(expected_divisions):
        raise ValueError('the EVAP writer omits, repeats or invents actual quotient/remainder calls')
    for call, unused_first, unused_last, returned in divisions:
        divisor, dividend, output = expected_divisions[call['site']]
        if tuple(call['entry']['registers'][:2]) != (divisor, dividend) or returned['registers'][0] != output:
            raise ValueError('the EVAP writer changes actual wide-product division arguments or returned quotient/remainder')

    require_registers(trace, 0xB2172, (6,), (value['transform']['value'],))
    a_store, a_register = (0xB20F6, 2) if value['active'] else (0xB213C, 6)
    require_registers(trace, a_store, (a_register,), (value['coefficient_a']['returned'],))
    require_registers(trace, 0xB2288, (5, 2), (value['coefficient_a']['value'], value['normalized']))
    require_registers(trace, 0xB2290, (2, 5),
        (value['coefficient_a']['value'] * value['normalized'], value['coefficient_b']['value']))
    require_registers(trace, 0xB22A6, (6, 12), (value['result'], numeric.POINTER_ALIAS))
    if value['difference'] > 0 and value['parameter']:
        partial = value['baseline'] * value['gain']
        require_registers(trace, 0xB2200, (4, 2), (value['gain'], value['baseline']))
        require_registers(trace, 0xB220C, (4, 2), (partial, value['difference'] // 256))
        require_registers(trace, 0xB2210, (4, 6), (partial, value['difference'] & 255))
        frame_expected = [frame_operand(0xB2216, 'write', observed['sp'] - 36, 5, value['low_product']),
            frame_operand(0xB2220, 'write', observed['sp'] - 40, 2, value['scaled'])]
        if not value['product_capped']:
            frame_expected.append(frame_operand(0xB222C, 'write', observed['sp'] - 32, 1, value['high']))
            if not value['quotient_capped']:
                frame_expected.extend((frame_operand(0xB223A, 'read', observed['sp'] - 32, 1, value['high']),
                    frame_operand(0xB223E, 'write', observed['sp'] - 28, 4, value['quotient_high'] * 65536),
                    frame_operand(0xB2244, 'read', observed['sp'] - 40, 2, value['scaled']),
                    frame_operand(0xB2248, 'read', observed['sp'] - 36, 4, value['low_product']),
                    frame_operand(0xB225C, 'read', observed['sp'] - 28, 4, value['quotient_high'] * 65536)))
    else:
        frame_expected = []
    stack_sites = {0xB2216, 0xB2220, 0xB222C, 0xB223A, 0xB223E, 0xB2244, 0xB2248, 0xB225C}
    same([event for event in result['accesses'] if event['site'] in stack_sites], frame_expected,
        'the EVAP writer changes exact caller-local wide-product words or quotient/remainder temporaries')


def require_registers(trace, site, registers, values):
    rows = [row for row in trace if row['site'] == site]
    if len(rows) != 1 or tuple(rows[0]['before']['registers'][r] for r in registers) != values:
        raise ValueError('the EVAP writer replaces complete live arithmetic/store operands with matching output bytes')


def require_tail(trace, start, end, site, target, call, values):
    rows = [row for row in trace[start:end + 1] if row['site'] == site]
    if (len(rows) != 1 or not rows[0]['delay_slot'] or rows[0]['next'] != target
            or rows[0]['after']['registers'][15] != call['sp'] or rows[0]['after']['pr'] != call['return_address']):
        raise ValueError('the EVAP writer changes an actual delayed tail or restored caller SP/PR')
    if values is not None:
        registers = rows[0]['after']['registers']
        same((registers[0], registers[2], registers[3]), values,
            'the EVAP interpolation tail changes exact first/second/fraction operands')


def frame_operand(site, mode, address, register, number):
    return dict(site=site, mode=mode, address=address, width_bytes=4, register=register,
        domain='frame', bytes=number.to_bytes(4, 'big').hex())

