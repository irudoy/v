"""Actual indexed word operands, local wraps, fixed calls and complete updater state."""
from kb import test_contract
from kb import ltft_adjustment_update_contract as contract

RAM_BASE = 0x01000000
MASK = 0xFFFFFFFF
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
FEASIBLE_SITES = EXACT_SITES - set(contract.DECLARED['caller_scoped_infeasible_sites'])
FIXED_BRANCHES = {int(site): outcome for site, outcome in contract.DECLARED['caller_scoped_fixed_branches'].items()}
CALL_TARGETS = {0x581AE: 0x21BBC, 0x58228: 0x21BBC, 0x58242: 0x21BBC, 0x58478: 0x25E20}


def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)


def event(site, mode, address, width, register, domain, raw):
    return dict(site=site, mode=mode, address=address, width_bytes=width, register=register,
                domain=domain, bytes=raw.hex())


def ram_operands(memory, value):
    rows = []

    def read(site, address, width, register):
        rows.append(event(site, 'read', RAM_BASE + address, width, register, 'ram', memory[address:address + width]))

    def write(site, address, width, register, number):
        rows.append(event(site, 'write', RAM_BASE + address, width, register, 'ram', number.to_bytes(width, 'big')))

    read(0x58186, 0x564A, 2, 0)
    read(0x5819C, 0x2304, 2, 0)
    read(0x581B6, 0x22E1, 1, 0)
    if value['first_permit']:
        read(0x581C6, 0x230E, 1, 7)
    if value['permitted']:
        read(0x581D6, 0x4498, 1, 7)
        if value['timer_written']:
            write(0x581E6, 0x4498, 1, 6, 16)
            read(0x581EC, 0x3E30, 1, 7)
            if value['active_status']:
                read(0x58200, 0x1308, 2, 0)
                read(0x5820A, 0x2308, 2, 2)
            else:
                read(0x5838E, 0x3EA4, 1, 6)
                if value['quiet_status']:
                    read(0x58398, 0x2461, 1, 0)
    else:
        read(0x583E8, 0x3082, 1, 6)
        if value['reset_cleared']:
            write(0x583F4, 0x3082, 1, 6, value['reset_after'])
            read(0x583FA, 0x3E30, 1, 2)
            if value['active_status']:
                read(0x5840C, 0x29E4, 2, 6)
    read(0x25E32, 0x5A94, 1, 0)
    if not value['diagnostic_neutral']:
        read(0x58482, 0x41B5, 1, 0)
    write(0x5848E, 0x564A, 2, 14, value['value'])
    read(0x58494, 0x3E30, 1, 2)
    if value['active_status']:
        read(0x584A0, 0x12FE, 1, 2)
        write(0x584A6, 0x12FE, 1, 2, value['status'])
    else:
        read(0x584AE, 0x12FE, 1, 6)
        write(0x584B2, 0x12FE, 1, 6, value['status'])
    return rows


def controls(observed, value):
    rows = []

    def read(site, address, register):
        raw = observed['calibration_before'][address]
        rows.append(event(site, 'read', address, len(raw), register, 'rom', raw))

    read(0x58198, 0x878B, 6)
    if value['timer_written'] and value['active_status']:
        read(0x58216, 0x878B, 6)
        read(0x58236, 0x878B, 2)
        read(0x5825A, 0x878F, 7)
        if value['branch'] == 'active-upper-error-step':
            read(0x58274, 0x86BE, 6)
            if value['increased'] > value['upper']:
                read(0x5828C, 0x86BE, 6)
        else:
            read(0x5829E, 0x8790, 6)
            if value['branch'] == 'active-lower-error-step':
                read(0x582B6, 0x86BF, 6)
                if value['decreased'] < value['lower']:
                    read(0x582C8, 0x86BF, 6)
            elif value['old'] < 25600:
                read(0x58312, 0x8790, 6)
    elif value['temperature'] is not None:
        read(0x58406, 0x8FA8, 7)
        if value['temperature'] < value['temperature_upper']:
            read(0x58418, 0x878C, 6)
        else:
            read(0x58426, 0x8FA6, 2)
            if value['temperature_step'] is not None:
                read(0x58432, 0x878C, 6)
    read(0x58444, 0x86BE, 5)
    read(0x5845C, 0x86BF, 7)
    return rows


def local_operands(memory, value):
    rows = []

    def put(site, mode, offset, width, number):
        rows.append((site, mode, offset, width, number & ((1 << (8 * width)) - 1)))

    old, diagnostic = value['old'], value['diagnostic']
    put(0x58190, 'write', 0, 2, old)
    put(0x58194, 'write', 4, 2, old)
    put(0x581A6, 'write', 8, 2, diagnostic)
    if value['timer_written'] and value['active_status']:
        error, up, down = value['error'], value['increased'], value['decreased']
        for site, mode, offset, width, number in (
            (0x58206, 'write', 12, 2, value['measured']), (0x5820C, 'read', 12, 2, value['measured']),
            (0x58210, 'write', 12, 2, value['measured'] + value['selected']), (0x58218, 'write', 12, 2, error),
            (0x5821A, 'read', 8, 2, diagnostic), (0x5822A, 'write', 16, 4, 25600),
            (0x5822C, 'read', 0, 2, old), (0x58234, 'write', 20, 2, up),
            (0x58238, 'read', 8, 2, diagnostic), (0x5823E, 'read', 16, 4, 25600),
            (0x58246, 'read', 0, 2, old), (0x58250, 'write', 24, 2, down),
            (0x58252, 'read', 12, 2, error), (0x58256, 'write', 28, 4, error),
            (0x58264, 'read', 28, 4, error)):
            put(site, mode, offset, width, number)
        if value['branch'] == 'active-upper-error-step':
            put(0x5826A, 'read', 20, 2, up)
            put(0x5826E, 'write', 4, 2, up)
            put(0x58270, 'write', 28, 4, up)
            put(0x58278, 'read', 28, 4, up)
            if up > value['upper']:
                put(0x58294, 'write', 4, 2, value['upper'])
        else:
            put(0x58296, 'read', 12, 2, error)
            put(0x5829C, 'write', 28, 4, error)
            put(0x582A2, 'read', 28, 4, error)
            if value['branch'] == 'active-lower-error-step':
                put(0x582AC, 'read', 24, 2, down)
                put(0x582B0, 'write', 4, 2, down)
                put(0x582B2, 'write', 28, 4, down)
                put(0x582BA, 'read', 28, 4, down)
                if down < value['lower']:
                    put(0x582CE, 'write', 4, 2, value['lower'])
            else:
                put(0x582DA, 'read', 12, 2, error)
                if old >= 25600:
                    put(0x582EE, 'read', 24, 2, down)
                    put(0x582F6, 'write', 4, 2, down)
                    if down <= 25600:
                        put(0x58302, 'write', 4, 2, 25600)
                else:
                    put(0x58310, 'read', 12, 2, error)
                    put(0x58330, 'read', 20, 2, up)
                    put(0x5833C, 'write', 4, 2, up)
                    if up >= 25600:
                        put(0x5843E, 'write', 4, 2, 25600)
    elif value['timer_written'] and value['branch'] != 'quiet-status-hold':
        put(0x5839E, 'read', 0, 2, old)
        if old > 25600:
            down = (old - value['delta']) & 65535
            put(0x583B8, 'write', 4, 2, down)
            if down <= 25600:
                put(0x583BE, 'write', 4, 2, 25600)
        elif old < 25600:
            up = (old + value['delta']) & 65535
            put(0x583CE, 'write', 0, 2, up)
            put(0x583DC, 'write', 4, 2, up)
            if up >= 25600:
                put(0x5843E, 'write', 4, 2, 25600)
    elif value['temperature_step'] is not None:
        site = 0x58416 if value['branch'] == 'disabled-temperature-decrease' else 0x58430
        put(site, 'read', 0, 2, old)
        put(0x5843C, 'write', 0, 2, value['candidate'])
        put(0x5843E, 'write', 4, 2, value['candidate'])
    put(0x58442, 'read', 4, 2, value['candidate'])
    return rows


def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
         'the trim updater changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the trim updater changes complete frame, numerical publications or unrelated RAM')
    if (observed['context'][4] & 255 != 1 or result['sp'] != observed['sp']
            or result['pr'] != observed['continuation'] or result['registers'][0] != 0x72
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the trim updater changes native index1, complete retained CPU or natural return')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the trim updater lacks its complete natural entry trace')
    initial = trace[0]['before']
    same(tuple(initial[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
         ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
         'the trim updater detaches complete initial CPU from immutable raw inputs')
    for index, row in enumerate(trace):
        destination = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != destination
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()
                or row['before']['gbr'] != observed['context'][15]):
            raise ValueError('the trim updater changes an exact instruction, GBR or continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the trim updater detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
         'the trim updater changes exact executed instruction identities')
    if {row['site'] for row in trace if row['delay_slot']} != {row['site'] + 2 for row in result['branches'] if row['delay']}:
        raise ValueError('the trim updater omits or invents a real delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the trim updater reaches an impossible immutable-threshold or fixed-argument branch')
    same([row for row in result['accesses'] if row['domain'] == 'ram'],
         ram_operands(observed['memory_before'][0], value),
         'the trim updater changes ordered actual RAM operands, conditional input reads or publications')
    actual_controls = []
    for operand in result['accesses']:
        if operand['domain'] in ('ram', 'frame'):
            continue
        site = operand['site']
        if site in contract.LITERAL_OPERANDS:
            address, width, register = contract.LITERAL_OPERANDS[site]
            same(operand, event(site, 'read', address, width, register, 'rom', fixture[address:address + width]),
                 'the trim updater changes an exact PC literal operand')
        else:
            actual_controls.append(operand)
    same(actual_controls, controls(observed, value),
         'the trim updater changes actual repeated immutable ROM controls, widths or read order')
    local_base = observed['sp'] - 68
    actual_locals = [(row['site'], row['mode'], row['address'] - local_base, row['width_bytes'], int(row['bytes'], 16))
                     for row in result['accesses'] if row['domain'] == 'frame'
                     and local_base <= row['address'] and row['address'] + row['width_bytes'] <= local_base + 32]
    same(actual_locals, local_operands(observed['memory_before'][0], value),
         'the trim updater changes real local word/long values, wraps, access order or slot widths')
    expected = [0x581AE]
    if value['timer_written'] and value['active_status']:
        expected.extend((0x58228, 0x58242))
    expected.append(0x58478)
    same([call['site'] for call in result['calls']], expected,
         'the trim updater changes complete actual helper order or invokes an extra call')
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if (call['target'] != CALL_TARGETS[site] or call['return_address'] != site + 4
                or call['sp'] != observed['sp'] - 68):
            raise ValueError('the trim updater changes a real helper target, nested SP or continuation')
        first = next((index + 2 for index in range(cursor, len(trace) - 2) if trace[index]['site'] == site), None)
        if first is None or trace[first]['site'] != call['target']:
            raise ValueError('the trim updater replaces a real post-delay helper entry')
        cursor = first
        before = trace[first]['before']
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
             (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
             'the trim updater detaches complete actual post-delay operands')
        terminal = next((index for index in range(first, len(trace) - 1)
                         if any(branch['kind'] == 'return' for branch in trace[index]['branches'])
                         and trace[index + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the trim updater omits a complete real helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the trim updater changes a helper natural return SP/PR')
        if call['target'] == 0x21BBC:
            if (tuple(call['entry']['registers'][:2]) != (25600, value['dividend'])
                    or not 0 <= value['dividend'] <= 65535 * 255
                    or returned['registers'][0] != value['delta']):
                raise ValueError('the trim updater changes a live signed-division argument or independent quotient')
        elif (call['entry']['registers'][4] != 0x129
                or returned['registers'][0] != int(value['diagnostic_neutral'])):
            raise ValueError('the trim updater changes its actual fixed record ID or predicate return')
    old_status = observed['memory_before'][0][0x12FE]
    signed_status = old_status if old_status < 128 else old_status - 256
    status_site, status_register = (0x584A6, 2) if value['active_status'] else (0x584B2, 6)
    status_live = (signed_status | 2) if value['active_status'] else (signed_status & ~2)
    wanted_stores = [(0x5848E, 14, value['value']), (status_site, status_register, status_live & MASK)]
    if value['timer_written']:
        wanted_stores.append((0x581E6, 6, 16))
    if value['reset_cleared']:
        wanted_stores.append((0x583F4, 6, value['reset_after']))
    for site, register, wanted in wanted_stores:
        selected = [row for row in trace if row['site'] == site]
        if len(selected) != 1 or selected[0]['before']['registers'][register] != wanted:
            raise ValueError('the trim updater substitutes matching low bytes for a complete actual live store register')
