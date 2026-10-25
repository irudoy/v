"""Independent physical operands, delayed calls and complete paired-entry state."""
from kb import test_contract
from kb import blend_weight_quantity_contract as contract, blend_weight_quantity_semantics as numeric

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# Axis intervals have a positive divisor. The rate divider receives100 and
# a nonnegative uint16*uint8 product. Generic helpers retain their separate
# complete-primary obligations outside these exact caller premises.
# The rate is bounded by max(0,x-blend), so blend+rate never exceeds65535.
INFEASIBLE_SITES = {0x26D0A, 0x26D0C, 0x26DA2, 0x26DA4,
    0x70F82, 0x721BC,
    0x21BCC, 0x21BCE, 0x21BFE, 0x21C00, 0x21C64, 0x21C66,
    *range(0x21C70, 0x21CD6, 2)}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x26C7A: 'fallthrough', 0x26D12: 'fallthrough',
    0x70F80: 'taken', 0x721BA: 'taken',
    0x21BC0: 'fallthrough', 0x21BCA: 'taken', 0x21BDC: 'fallthrough',
    0x21BFC: 'taken', 0x21C62: 'taken'}
CALL_TARGETS = {0x70E76: 0x262A8, 0x70E90: 0x262A8, 0x70EB8: 0x264F8,
    0x70F3C: 0x21BBC, 0x720EE: 0x26628, 0x72108: 0x26628, 0x72188: 0x21BBC,
    0x262B4: 0x26984, 0x262C2: 0x26984, 0x26502: 0x26984,
    0x26634: 0x26B84, 0x26642: 0x26B84, 0x269AA: 0x26C78, 0x26BAA: 0x26D10,
    0x2686A: 0x26740, 0x2687A: 0x26740, 0x26882: 0x26740, 0x26896: 0x26740,
    0x26B4A: 0x26AF8, 0x26B5A: 0x26AF8, 0x26B62: 0x26AF8, 0x26B76: 0x26AF8}
STACK_DELTAS = {0x70E76: -44, 0x70E90: -44, 0x70EB8: -44, 0x70F3C: -44,
    0x720EE: -44, 0x72108: -44, 0x72188: -44,
    0x262B4: -52, 0x262C2: -60, 0x26502: -48,
    0x26634: -52, 0x26642: -60,
    0x2686A: -52, 0x2687A: -56, 0x26882: -52, 0x26896: -52,
    0x26B4A: -52, 0x26B5A: -56, 0x26B62: -52, 0x26B76: -52}
HELPER_ROM_SITES = {0x26986, 0x2699C, 0x2699E, 0x26B86, 0x26B9C, 0x26B9E,
    0x26864, 0x26866, 0x26874, 0x26876, 0x2688E, 0x26890,
    0x26B44, 0x26B46, 0x26B54, 0x26B56, 0x26B6E, 0x26B70, 0x2650A, 0x26510}


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
    def control(site, at, width, register):
        raw = calibration[at]
        if len(raw) != width:
            raise ValueError('the shared-weight physical control loses its exact width')
        rom.append(dict(site=site, mode='read', address=at, width_bytes=width,
            register=register, domain='rom', bytes=raw.hex()))
        return int.from_bytes(raw, 'big')
    if phase == 0:
        read(0x70E62, 0x10D2, 2, 0)
        read(0x70E68, 0x1210, 2, 0)
        write(0x70E82, 0x133A, 2, 2, value['endpoint_a']['value'])
        read(0x70E86, 0x10D2, 2, 0)
        read(0x70E8E, 0x1210, 2, 0)
        write(0x70E9A, 0x133C, 2, 2, value['endpoint_b']['value'])
        if read(0x70E9C, 0x417E, 1, 0) & 8:
            raw = read(0x70EA2, 0x10D2, 2, 0)
            write(0x70EAA, 0x1A78, 2, 2, raw)
        read(0x70EB0, 0x1A78, 2, 7)
        write(0x70EC2, 0x190E, 2, 6, value['weight'])
        read(0x70EC8, 0x133A, 2, 5)
        read(0x70ED6, 0x133C, 2, 2)
        write(0x70EE8, 0x1212, 2, 0, value['blend'])
        mode = control(0x70EEA, 0x89FB, 1, 0)
        if mode & 64:
            y = read(0x70EFC, 0x10D2, 2, 0)
            limit = control(0x70EFE, 0x95D2, 2, 2)
            calculate = numeric.sign_extended_word(y) <= numeric.sign_extended_word(limit)
            if calculate:
                calculate = not read(0x70F06, 0x244F, 1, 0) & 128
            if calculate:
                calculate = not read(0x70F0E, 0x245E, 1, 0) & 64
            if calculate:
                calculate = not read(0x70F18, 0x41BD, 1, 0) & 1
            if calculate:
                calculate = not read(0x70F20, 0x245D, 1, 0) & 1
            if calculate:
                read(0x70F26, 0x10B2, 2, 0)
                control(0x70F28, 0x8775, 1, 2)
                control(0x70F32, 0x840F, 1, 4)
                read(0x70F42, 0x1210, 2, 0)
                read(0x70F48, 0x1212, 2, 0)
                write(0x70F64, 0x1328, 2, 2, value['rate'])
            else:
                write(0x70F72, 0x1328, 2, 2, 0)
            write(0x70F88, 0x1330, 2, 6, value['conditioned'])
        else:
            write(0x70EF8, 0x1330, 2, 7, value['conditioned'])
        latch = read(0x70F8C, 0x4205, 1, 14)
        changed = False
        if not latch & 4:
            enabled = bool(read(0x70F9A, 0x4180, 1, 0) & 8)
            if enabled:
                enabled = not read(0x70FA0, 0x417E, 1, 0) & 8
            if enabled:
                enabled = not read(0x70FA8, 0x245D, 1, 0) & 1
            if enabled:
                y = read(0x70FB0, 0x10D2, 2, 0)
                limit = control(0x70FB2, 0x9020, 2, 6)
                changed = numeric.sign_extended_word(y) < numeric.sign_extended_word(limit)
        else:
            low = read(0x70FC2, 0x124E, 2, 0)
            high = read(0x70FC6, 0x1250, 2, 0)
            if low < high:
                changed = read(0x70FCE, 0x1210, 2, 0) >= value['blend']
            elif low > high:
                x = read(0x70FDA, 0x1210, 2, 0)
                if x <= value['blend']:
                    changed = x <= control(0x70FE4, 0x9022, 2, 2)
        if changed:
            write(0x70FF4, 0x4205, 1, 14, value['latch_after'])
        enabled = read(0x70FFA, 0x26B0, 1, 6) not in (1, 4)
        if enabled:
            enabled = read(0x71008, 0x26E0, 1, 0) != 3
        if enabled:
            enabled = bool(control(0x7100E, 0x89FB, 1, 0) & 8)
        if enabled:
            enabled = not control(0x71016, 0x89FA, 1, 0) & 1
        if enabled:
            enabled = not control(0x7101E, 0x8B3F, 1, 0) & 128
        if enabled:
            enabled = bool(read(0x71026, 0x4205, 1, 0) & 4)
        if enabled:
            raw = read(0x71030, 0x1330, 2, 2)
            write(0x71038, 0x1332, 2, 2, raw)
        else:
            raw = read(0x7103A, 0x1210, 2, 0)
            write(0x71042, 0x1332, 2, 14, raw)
    else:
        read(0x720DA, 0x10D2, 2, 0)
        read(0x720E0, 0x1248, 2, 0)
        write(0x720FA, 0x1CBA, 2, 2, value['endpoint_a']['value'])
        read(0x720FE, 0x10D2, 2, 0)
        read(0x72104, 0x1248, 2, 0)
        write(0x72112, 0x1CBC, 2, 6, value['endpoint_b']['value'])
        read(0x7211A, 0x190E, 2, 5)
        read(0x72120, 0x1CBA, 2, 4)
        write(0x72136, 0x124A, 2, 0, value['blend'])
        latch = read(0x7213A, 0x4214, 1, 14)
        mode = control(0x72140, 0x89FB, 1, 0)
        if mode & 64:
            y = read(0x72148, 0x10D2, 2, 0)
            limit = control(0x7214A, 0x16338, 2, 6)
            calculate = numeric.sign_extended_word(y) <= numeric.sign_extended_word(limit)
            if calculate:
                calculate = not read(0x72152, 0x244F, 1, 0) & 128
            if calculate:
                calculate = not read(0x7215A, 0x245E, 1, 0) & 64
            if calculate:
                calculate = not read(0x72162, 0x41BD, 1, 0) & 1
            if calculate:
                calculate = not read(0x72168, 0x245D, 1, 0) & 1
            if calculate:
                read(0x72170, 0x10B2, 2, 0)
                control(0x72172, 0x15F69, 1, 6)
                control(0x7217C, 0x15F55, 1, 4)
                read(0x7218E, 0x1248, 2, 0)
            write(0x721AE, 0x1CB2, 2, 6, value['rate'])
            write(0x721C2, 0x1CB4, 2, 5, value['conditioned'])
        else:
            write(0x721C6, 0x1CB4, 2, 13, value['conditioned'])
        changed = False
        if not latch & 4:
            enabled = bool(read(0x721D6, 0x4180, 1, 0) & 8)
            if enabled:
                enabled = not read(0x721DE, 0x417E, 1, 0) & 8
            if enabled:
                enabled = not read(0x721E6, 0x245D, 1, 0) & 1
            if enabled:
                y = read(0x721EE, 0x10D2, 2, 0)
                limit = control(0x721F0, 0x15F9A, 2, 6)
                changed = numeric.sign_extended_word(y) < numeric.sign_extended_word(limit)
        else:
            low = read(0x7220A, 0x1286, 2, 0)
            high = read(0x7220E, 0x1288, 2, 0)
            if low < high:
                changed = read(0x72216, 0x1248, 2, 0) >= value['blend']
            elif low > high:
                x = read(0x72222, 0x1248, 2, 0)
                if x <= value['blend']:
                    changed = x <= control(0x7222E, 0x15F9C, 2, 6)
        local_latch = (latch & 0xFB if latch & 4 else latch | 4) if changed else latch
        if changed:
            write(0x7223C, 0x4214, 1, 2, local_latch)
        shared = read(0x72242, 0x4205, 1, 4)
        if bool(shared & 4) != bool(local_latch & 4):
            write(0x72264, 0x4205, 1, 2, shared & 0xFB)
            local_latch &= 0xFB
            write(0x7226E, 0x4214, 1, 2, local_latch)
        enabled = read(0x72274, 0x26B0, 1, 6) not in (1, 4)
        if enabled:
            enabled = read(0x72282, 0x26E0, 1, 0) != 3
        if enabled:
            enabled = bool(control(0x72288, 0x89FB, 1, 0) & 8)
        if enabled:
            enabled = not control(0x72290, 0x89FA, 1, 0) & 1
        if enabled:
            enabled = not control(0x72298, 0x8B3F, 1, 0) & 128
        if enabled:
            enabled = bool(read(0x722A0, 0x4214, 1, 0) & 4)
        if enabled:
            raw = read(0x722A8, 0x1CB4, 2, 2)
            write(0x722AE, 0x1CB6, 2, 2, raw)
        else:
            raw = read(0x722B0, 0x1248, 2, 0)
            write(0x722B6, 0x1CB6, 2, 14, raw)
    same(bytes(out), value['memory'], 'the shared-weight physical publication path disagrees with independent numerical RAM')
    return ram, rom


def require(observed, result, value, fixture):
    phase = observed['phase']
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'],
        result['gbr'], *reversed(result['registers'])), 'the shared-weight phase changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the shared-weight phase changes complete frame, unrelated RAM or independent arithmetic publications')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the shared-weight phase changes natural return, saved registers, GBR or MACL')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRIES[phase]:
        raise ValueError('the shared-weight phase omits its complete natural entry trace')
    first = trace[0]['before']
    same(tuple(first[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
        ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
        'the shared-weight phase detaches complete entry CPU from immutable observed input')
    for index, row in enumerate(trace):
        next_site = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != next_site
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()):
            raise ValueError('the shared-weight phase changes a complete instruction or natural continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the shared-weight phase detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
        'the shared-weight phase changes executed exact instruction identities')
    delayed = {row['site'] + 2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the shared-weight phase omits or invents an actual delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the shared-weight phase violates a positive axis or rate-divisor premise')
    calibration = observed['calibration_before']
    wanted_ram, wanted_rom = root_operands(phase, observed['memory_before'][0], calibration, value)
    same([row for row in result['accesses'] if row['domain'] == 'ram'], wanted_ram,
        'the shared-weight phase changes ordered physical RAM sites, widths, directions, operands or complete bytes')
    root_rom = []
    for event in result['accesses']:
        site = event['site']
        if event['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                domain='rom', bytes=fixture[at:at + width].hex()), 'the shared-weight phase changes an exact PC literal operand')
        elif site not in HELPER_ROM_SITES:
            root_rom.append(event)
        elif event['domain'] != 'rom' or event['mode'] != 'read' or event['width_bytes'] != 2:
            raise ValueError('the shared-weight helper changes a physical ROM word read')
    same(root_rom, wanted_rom, 'the shared-weight phase changes ordered actual ROM control sites, widths or bytes')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site + 4:
            raise ValueError('the shared-weight phase changes a real helper target or continuation')
        if site in STACK_DELTAS and call['sp'] != observed['sp'] + STACK_DELTAS[site]:
            raise ValueError('the shared-weight phase changes a complete nested call frame')
        start = next((i + 2 for i in range(cursor, len(trace) - 2) if trace[i]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the shared-weight phase replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
            (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
            'the shared-weight phase detaches complete helper arguments from its preceding delay slot')
        terminal = next((i for i in range(start, len(trace) - 1)
            if any(branch['kind'] == 'return' for branch in trace[i]['branches'])
            and trace[i + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the shared-weight phase omits an actual complete helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the shared-weight phase changes returned helper SP or PR')
        call_spans.append((call, start, terminal + 1, returned))
        registers = call['entry']['registers']
        if call['target'] in (0x26740, 0x26AF8):
            if returned['registers'][0] != numeric.directed_word(registers[0], registers[2], registers[3]):
                raise ValueError('the shared-weight phase changes an independent directed interpolation return')
        elif call['target'] in (0x26C78, 0x26D10):
            divisor, dividend = registers[:2]
            if (not 0 < divisor <= 65535 or not 0 <= dividend < 1 << 32 or dividend & 65535
                    or dividend // divisor > 65535 or returned['registers'][0] != dividend // divisor):
                raise ValueError('the shared-weight phase changes unsigned axis division operands or quotient')
    surface_sites = (0x70E76, 0x70E90) if phase == 0 else (0x720EE, 0x72108)
    wrapper, axis_sites, axis_reads, table_reads, tail_site, kernel = (
        (0x262A8, (0x262B4, 0x262C2), (0x26986, 0x2699C, 0x2699E),
         (0x26864, 0x26866, 0x26874, 0x26876, 0x2688E, 0x26890), 0x262D6, 0x26848)
        if phase == 0 else
        (0x26628, (0x26634, 0x26642), (0x26B86, 0x26B9C, 0x26B9E),
         (0x26B44, 0x26B46, 0x26B54, 0x26B56, 0x26B6E, 0x26B70), 0x26656, 0x26B28))
    for site, table, endpoint in zip(surface_sites, value['surface_addresses'], (value['endpoint_a'], value['endpoint_b'])):
        selected = [row for row in call_spans if row[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the shared-weight phase omits or repeats a complete endpoint invocation')
        call, start, end, returned = selected[0]
        same(tuple(call['entry']['registers'][4:8]), (table, *value['axis_addresses'], value['x']),
            'the shared-weight phase changes actual table/axis/coordinate arguments')
        if call['target'] != wrapper or returned['registers'][0] != endpoint['returned'] & MASK:
            raise ValueError('the shared-weight phase replaces a real complete raw endpoint return')
        local = trace[start:end + 1]
        stack_site = 0x262BE if phase == 0 else 0x2663E
        stack_reads = [event for row in local for event in row['accesses'] if event['site'] == stack_site]
        if (len(stack_reads) != 1 or stack_reads[0]['domain'] != 'frame'
                or stack_reads[0]['address'] != call['sp'] or stack_reads[0]['width_bytes'] != 4
                or int(stack_reads[0]['bytes'], 16) & 65535 != value['y']):
            raise ValueError('the shared-weight phase loses the real caller-local column word and complete dword read')
        tails = [row for row in local if row['site'] == tail_site]
        if (len(tails) != 1 or not tails[0]['delay_slot'] or tails[0]['next'] != kernel
                or tails[0]['after']['registers'][15] != call['sp'] or tails[0]['after']['pr'] != site + 4):
            raise ValueError('the shared-weight phase changes an actual wrapper tail, restored PR or delay slot')
        actual_table = [event for row in local for event in row['accesses']
            if event['domain'] == 'rom' and table <= event['address'] < table + 512]
        if endpoint['fraction_y']:
            sites = [(table_reads[0], 1), (table_reads[1], 0)]
            if endpoint['fraction_x']:
                sites += [(table_reads[2], 1), (table_reads[3], 0)]
        else:
            sites = [(table_reads[4], 0)]
            if endpoint['fraction_x']:
                sites += [(table_reads[5], 2)]
        expected_table = [dict(site=read_site, mode='read', address=table + 2 * cell,
            width_bytes=2, register=register, domain='rom', bytes=calibration[table][2 * cell:2 * cell + 2].hex())
            for cell, (read_site, register) in zip(endpoint['cells'], sites)]
        same(actual_table, expected_table, 'the shared-weight phase changes actual lazy surface neighbors or word bytes')
        for axis_site, axis, coordinate, index, fraction in (
                (axis_sites[0], value['axis_addresses'][0], value['x'], endpoint['row'], endpoint['fraction_x']),
                (axis_sites[1], value['axis_addresses'][1], value['y'], endpoint['column'], endpoint['fraction_y'])):
            require_axis(trace, call_spans, axis_site, axis, coordinate, index, fraction,
                start, end, axis_reads, calibration)
    if phase == 0:
        selected = [row for row in call_spans if row[0]['site'] == 0x70EB8]
        if len(selected) != 1:
            raise ValueError('the shared-weight producer omits its actual curve call')
        call, start, end, returned = selected[0]
        same(tuple(call['entry']['registers'][4:7]), (0x1488A, 0x14C7A, value['weight_coordinate']),
            'the shared-weight producer changes actual curve/axis/coordinate arguments')
        if returned['registers'][0] != value['weight']:
            raise ValueError('the shared-weight producer changes its real unsigned curve return')
        curve = value['weight_curve']
        require_axis(trace, call_spans, 0x26502, 0x14C7A, value['weight_coordinate'],
            curve['index'], curve['fraction'], start, end, (0x26986, 0x2699C, 0x2699E), calibration)
        actual = [event for row in trace[start:end + 1] for event in row['accesses']
            if event['domain'] == 'rom' and 0x1488A <= event['address'] < 0x148AC]
        expected = [dict(site=site, mode='read', address=0x1488A + 2 * index, width_bytes=2,
            register=register, domain='rom', bytes=calibration[0x1488A][2 * index:2 * index + 2].hex())
            for site, index, register in ((0x2650A, curve['index'] + 1, 0), (0x26510, curve['index'], 1))]
        same(actual, expected, 'the shared-weight producer omits or substitutes its unconditional physical neighbor-first curve reads')
        tails = [row for row in trace[start:end + 1] if row['site'] == 0x26518]
        if (len(tails) != 1 or not tails[0]['delay_slot'] or tails[0]['next'] != 0x26740
                or tails[0]['after']['registers'][15] != call['sp'] or tails[0]['after']['pr'] != 0x70EBC):
            raise ValueError('the shared-weight curve changes its restored-PR interpolation tail')
    rate_site = 0x70F3C if phase == 0 else 0x72188
    rate_calls = [row for row in call_spans if row[0]['site'] == rate_site]
    if len(rate_calls) != int(value['rate_branch'] == 'rate-add'):
        raise ValueError('the shared-weight phase invents or omits its actual rate division')
    for call, start, end, returned in rate_calls:
        gain = 0x8775 if phase == 0 else 0x15F69
        dividend = numeric.unsigned_word(observed['memory_before'][0], 0x10B2) * calibration[gain][0]
        if (tuple(call['entry']['registers'][:2]) != (100, dividend)
                or returned['registers'][0] != value['rate_quotient']):
            raise ValueError('the shared-weight phase changes its actual positive signed rate-divide arguments or return')
    stores = ((0x70E82, 2, value['endpoint_a']['returned'] & MASK),
        (0x70E9A, 2, value['endpoint_b']['returned'] & MASK),
        (0x70EC2, 6, value['weight']), (0x70EE8, 0, value['blend'])) if phase == 0 else (
        (0x720FA, 2, value['endpoint_a']['returned'] & MASK),
        (0x72112, 6, value['endpoint_b']['returned'] & MASK), (0x72136, 0, value['blend']))
    for site, register, wanted in stores:
        rows = [row for row in trace if row['site'] == site]
        if len(rows) != 1 or rows[0]['before']['registers'][register] != wanted:
            raise ValueError('the shared-weight phase replaces a real full live publication operand with matching bytes')
    left_site, right_site = (0x70ED2, 0x70EDC) if phase == 0 else (0x72126, 0x7212A)
    left_regs, right_regs = ((2, 5), (6, 2)) if phase == 0 else ((2, 4), (7, 6))
    for site, registers, wanted in ((left_site, left_regs, (65536 - value['weight'], value['endpoint_a']['value'])),
            (right_site, right_regs, (value['weight'], value['endpoint_b']['value']))):
        rows = [row for row in trace if row['site'] == site]
        if len(rows) != 1 or tuple(rows[0]['before']['registers'][r] for r in registers) != wanted:
            raise ValueError('the shared-weight phase substitutes a scalar for actual carried coefficient multiplication operands')


def require_axis(trace, call_spans, site, axis, coordinate, index, fraction, start, end, reads, calibration):
    selected = [row for row in call_spans if row[0]['site'] == site and start <= row[1] <= end]
    if len(selected) != 1:
        raise ValueError('the shared-weight phase omits an actual complete axis call')
    call, first, last, returned = selected[0]
    registers = call['entry']['registers']
    if ((registers[0], registers[4], registers[5]) != (axis, 30, coordinate)
            or (returned['registers'][4], returned['registers'][5]) != (2 * index, fraction)):
        raise ValueError('the shared-weight phase changes actual axis arguments, lower knot or fraction')
    actual = [event for row in trace[first:last + 1] for event in row['accesses']
        if event['domain'] == 'rom' and axis <= event['address'] < axis + 32]
    expected = [dict(site=reads[0], mode='read', address=axis + 2 * knot, width_bytes=2, register=1,
        domain='rom', bytes=calibration[axis][2 * knot:2 * knot + 2].hex()) for knot in range(15, index - 1, -1)]
    if fraction:
        expected += [dict(site=read_site, mode='read', address=axis + 2 * knot, width_bytes=2, register=register,
            domain='rom', bytes=calibration[axis][2 * knot:2 * knot + 2].hex())
            for read_site, knot, register in ((reads[1], index, 1), (reads[2], index + 1, 0))]
    same(actual, expected, 'the shared-weight phase changes complete backwards axis reads or a real fractional neighbor')


def require_handoff(producer, consumer, producer_value, consumer_value):
    if (producer['phase'] != 0 or consumer['phase'] != 1 or producer['pair'] != consumer['pair']
            or producer['memory_after'] != consumer['memory_before']
            or not test_contract.exact(producer['calibration_after'], consumer['calibration_before'])
            or producer['bound_after'] != consumer['bound_before']):
        raise ValueError('the shared-weight handoff changes complete actual RAM, immutable calibration or bound continuity')
    carried = numeric.unsigned_word(producer['memory_after'][0], 0x190E)
    if carried != producer_value['weight'] or carried != consumer_value['weight']:
        raise ValueError('the shared-weight handoff substitutes a synthetic or independently reset coefficient')
    for at in (0x4205, 0x4214):
        if producer['memory_after'][0][at] != consumer['memory_before'][0][at]:
            raise ValueError('the shared-weight handoff discards an actual shared latch update')
