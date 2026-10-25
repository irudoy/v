"""Independent physical inverse operands, real nested calls and channel word publication."""
from kb import test_contract
from kb import channel_target_builder_contract as contract

RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
INFEASIBLE_SITES = set(contract.DECLARED['caller_scoped_infeasible_sites'])
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {int(site): outcome for site, outcome in contract.DECLARED['caller_scoped_fixed_branches'].items()}
CALL_TARGETS = {0x6F4C4: 0x26524, 0x6F52E: 0x26524, 0x6F5B0: 0x26474,
                0x2652E: 0x26984, 0x2647E: 0x26944, 0x269AA: 0x26C78, 0x2696A: 0x26C78,
                0x6F624: 0x25E20, 0x6F62E: 0x25E20, 0x6F640: 0x25E20, 0x6F64A: 0x25E20}
STACK_DELTAS = {site: (-48 if site in (0x2652E, 0x2647E) else
                       -52 if site in (0x269AA, 0x2696A) else -40) for site in CALL_TARGETS}
TABLE_SITES = {0x26536, 0x2653C, 0x26486, 0x2648C}
AXIS_SITES = {0x26986, 0x2699C, 0x2699E, 0x26946, 0x2695C, 0x2695E}


def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)


def event(site, domain, address, width, register, raw, mode='read'):
    return dict(site=site, mode=mode, address=address, width_bytes=width, register=register,
                domain=domain, bytes=raw.hex())


def ram_operands(memory, value):
    rows = []

    def read(site, address, width, register):
        rows.append(event(site, 'ram', RAM_BASE + address, width, register, memory[address:address + width]))

    def write(site, address, register, number):
        rows.append(event(site, 'ram', RAM_BASE + address, 2, register, (number & 65535).to_bytes(2, 'big'), 'write'))

    read(0x6F4AE, 0x1340, 2, 6)
    write(0x6F4D2, 0x28F8, 5, value['scratch'])
    read(0x6F4D4, 0x24CE, 1, 0)
    if not memory[0x24CE] & 4:
        read(0x6F4DC, 0x24D2, 1, 0)
    if value['mode']:
        read(0x6F57E, 0x2696, 2, 0)
    else:
        read(0x6F4E4, 0x41A5, 1, 0)
        if memory[0x41A5] & 4:
            read(0x6F4EC, 0x244F, 1, 0)
            if value['second_inverse'] is not None:
                read(0x6F4F6, 0x19B2, 2, 5)
                read(0x6F4FE, 0x570A, 2, 4)
            else:
                read(0x6F540, 0x2696, 2, 0)
    read(0x6F592, 0x417E, 1, 0)
    if value['upper_lookup'] is not None:
        read(0x6F5AA, 0x11B3, 1, 7)
    write(0x6F5E6, 0x3508, 6, value['upper_raw'])
    read(0x25E32, 0x5866, 1, 0)
    if value['predicate_121'] is not None:
        read(0x25E32, 0x5A7C, 1, 0)
    read(0x25E32, 0x5869, 1, 0)
    if value['predicate_122'] is not None:
        read(0x25E32, 0x5A7F, 1, 0)
    write(0x6F668, 0x28BE, 7, value['value'])
    return rows


def control_operands(observed, value):
    rows = []
    calibration = observed['calibration_before']

    def read(site, address, register):
        raw = calibration[address]
        rows.append(event(site, 'rom', address, len(raw), register, raw))

    if value['branch'] == 'fixed-byte-base':
        read(0x6F564, 0x8CB6, 6)
    elif value['branch'] == 'base-plus-byte-offset':
        read(0x6F544, 0x8CB7, 0)
    if value['upper_lookup'] is None:
        read(0x6F598, 0x9578, 0)
    else:
        read(0x6F5B6, 0x9578, 0)
        read(0x6F5CE, 0x9576, 0)
    if value['initial_request'] <= value['upper_stored']:
        read(0x6F5EE, 0x9574, 0)
    read(0x6F5FA, 0x8CB6, 6)
    if value['second_active']:
        read(0x6F656, 0x92F2, 6)
    return rows


def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
         'the channel builder changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the channel builder changes complete frame, independent publications or unrelated RAM')
    if (observed['context'][4] & 255 != 1 or result['sp'] != observed['sp']
            or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]
            or result['registers'][0] != 2 or result['registers'][7] != value['value']):
        raise ValueError('the channel builder changes native index1, retained CPU, live word or natural return')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the channel builder lacks its complete natural entry trace')
    initial = trace[0]['before']
    same(tuple(initial[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
         ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
         'the channel builder detaches the complete initial CPU from immutable inputs')
    for index, row in enumerate(trace):
        destination = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != destination
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()):
            raise ValueError('the channel builder changes an exact instruction or continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the channel builder detaches complete intermediate CPU')
    same(result['code'], {row['site']: fixture[row['site']:row['site'] + 2].hex() for row in trace},
         'the channel builder changes exact executed instruction identities')
    if {row['site'] for row in trace if row['delay_slot']} != {row['site'] + 2 for row in result['branches'] if row['delay']}:
        raise ValueError('the channel builder omits or invents a natural delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind'] != FIXED_BRANCHES[branch['site']]:
            raise ValueError('the channel builder reaches an impossible fixed-record, coordinate or divisor branch')
    same([row for row in result['accesses'] if row['domain'] == 'ram'],
         ram_operands(observed['memory_before'][0], value),
         'the channel builder changes ordered actual RAM operands, record selection or word bytes')
    controls = []
    for operand in result['accesses']:
        site, address, width = operand['site'], operand['address'], operand['width_bytes']
        if operand['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, size, register = contract.LITERAL_OPERANDS[site]
            same(operand, event(site, 'rom', at, size, register, fixture[at:at + size]),
                 'the channel builder changes an exact PC literal operand')
        elif site in TABLE_SITES | AXIS_SITES:
            ranges = ((0x155A0, 66, 2), (0x13202, 64, 2)) if site in (0x26536, 0x2653C, 0x26986, 0x2699C, 0x2699E) else (
                (0x12DAA, 9, 1), (0x12D9A, 8, 1))
            if (operand['domain'] != 'rom' or operand['mode'] != 'read'
                    or not any(width == size and first <= address and address + size <= first + length for first, length, size in ranges)
                    or operand['bytes'] != fixture[address:address + width].hex()):
                raise ValueError('the channel builder changes an actual physical inverse or upper lookup operand')
        else:
            controls.append(operand)
    same(controls, control_operands(observed, value),
         'the channel builder changes the ordered actual raw ROM controls or GBR word addresses')
    spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if (call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site + 4
                or call['sp'] != observed['sp'] + STACK_DELTAS[site]):
            raise ValueError('the channel builder changes an actual nested call, stack depth or continuation')
        start = next((index + 2 for index in range(cursor, len(trace) - 2) if trace[index]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the channel builder replaces a real post-delay entry')
        cursor = start
        before = trace[start]['before']
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
             (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
             'the channel builder detaches complete actual post-delay arguments')
        terminal = next((index for index in range(start, len(trace) - 1)
                         if any(branch['kind'] == 'return' for branch in trace[index]['branches'])
                         and trace[index + 1]['next'] == site + 4), None)
        if terminal is None:
            raise ValueError('the channel builder omits a complete actual helper return')
        returned = trace[terminal + 1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site + 4:
            raise ValueError('the channel builder changes a natural helper return SP/PR')
        spans.append((call, start, terminal + 1, returned))
        if call['target'] == 0x26C78:
            divisor, dividend = call['entry']['registers'][:2]
            if (not 0 < divisor <= 65535 or not 0 <= dividend <= 0xFFFFFFFF or dividend & 65535
                    or not 0 < dividend // divisor < 65536 or returned['registers'][0] != dividend // divisor):
                raise ValueError('the channel builder changes actual positive unsigned axis division operands or return')
    curve_calls = [(0x6F4C4, 0x155A0, 0x13202, 2, value['first_inverse'])]
    if value['second_inverse'] is not None:
        curve_calls.append((0x6F52E, 0x155A0, 0x13202, 2, value['second_inverse']))
    if value['upper_lookup'] is not None:
        curve_calls.append((0x6F5B0, 0x12DAA, 0x12D9A, 1, value['upper_lookup']))
    expected_calls = []
    for site, table, axis, width, curve in curve_calls:
        selected = [span for span in spans if span[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the channel builder omits or repeats an actual curve invocation')
        call, start, end, returned = selected[0]
        same(tuple(call['entry']['registers'][4:7]), (table, axis, curve['coordinate']),
             'the channel builder changes its actual inverse curve/axis order or coordinate')
        if returned['registers'][0] != curve['value']:
            raise ValueError('the channel builder substitutes a scalar for a real curve return')
        wrapper_axis = 0x2652E if width == 2 else 0x2647E
        division = 0x269AA if width == 2 else 0x2696A
        expected_calls.extend((site, wrapper_axis))
        if curve['fraction']:
            expected_calls.append(division)
        local = trace[start:end + 1]
        table_sites = (0x26536, 0x2653C) if width == 2 else (0x26486, 0x2648C)
        reads = [operand for row in local for operand in row['accesses'] if operand['site'] in table_sites]
        wanted = [event(read_site, 'rom', table + width * cell, width, register,
                        fixture[table + width * cell:table + width * (cell + 1)])
                  for read_site, cell, register in ((table_sites[0], curve['index'] + 1, 0), (table_sites[1], curve['index'], 1))]
        same(reads, wanted, 'the channel builder changes either physical curve neighbor, byte width or read order')
        tail_site = 0x26544 if width == 2 else 0x26494
        tails = [row for row in local if row['site'] == tail_site]
        if (len(tails) != 1 or not tails[0]['delay_slot'] or tails[0]['next'] != 0x26740
                or tails[0]['after']['registers'][15] != call['sp'] or tails[0]['after']['pr'] != site + 4
                or tuple(tails[0]['after']['registers'][key] for key in (0, 2, 3)) != (curve['first'], curve['second'], curve['fraction'])):
            raise ValueError('the channel builder changes full live directed-interpolation operands or restored tail SP/PR')
        axes = [span for span in spans if span[0]['site'] == wrapper_axis and start <= span[1] <= end]
        if len(axes) != 1:
            raise ValueError('the channel builder omits a complete real axis call')
        axis_call, first, last, axis_return = axes[0]
        registers = axis_call['entry']['registers']
        count = 32 if width == 2 else 8
        if ((registers[0], registers[4], registers[5]) != (axis, width * (count - 1), curve['coordinate'])
                or (axis_return['registers'][4], axis_return['registers'][5]) != (width * curve['index'], curve['fraction'])):
            raise ValueError('the channel builder changes an actual axis address, count, lower knot or fraction')
        scan, lower, upper = (0x26986, 0x2699C, 0x2699E) if width == 2 else (0x26946, 0x2695C, 0x2695E)
        wanted = [event(scan, 'rom', axis + width * knot, width, 1,
                        fixture[axis + width * knot:axis + width * (knot + 1)])
                  for knot in range(count - 1, curve['index'] - 1, -1)]
        if curve['fraction']:
            wanted.extend(event(read_site, 'rom', axis + width * knot, width, register,
                                fixture[axis + width * knot:axis + width * (knot + 1)])
                          for read_site, knot, register in ((lower, curve['index'], 1), (upper, curve['index'] + 1, 0)))
        reads = [operand for row in trace[first:last + 1] for operand in row['accesses']
                 if operand['site'] in AXIS_SITES]
        same(reads, wanted, 'the channel builder changes complete backwards axis scans or positive neighbor reads')
    predicates = [(0x6F624, 0x6F, value['predicate_6f'])]
    if value['predicate_121'] is not None:
        predicates.append((0x6F62E, 0x121, value['predicate_121']))
    predicates.append((0x6F640, 0x70, value['predicate_70']))
    if value['predicate_122'] is not None:
        predicates.append((0x6F64A, 0x122, value['predicate_122']))
    expected_calls.extend(site for site, index, selected in predicates)
    same([call['site'] for call in result['calls']], expected_calls,
         'the channel builder changes complete natural call order or short-circuit predicate selection')
    for site, index, selected in predicates:
        matches = [span for span in spans if span[0]['site'] == site]
        if (len(matches) != 1 or matches[0][0]['entry']['registers'][4] != index
                or matches[0][3]['registers'][0] != int(selected)):
            raise ValueError('the channel builder changes an actual fixed-record ID or Boolean return')
    for site, register, wanted in ((0x6F4D2, 5, value['scratch']),
                                   (0x6F5E6, 6, value['upper_raw']), (0x6F668, 7, value['value'])):
        selected = [row for row in trace if row['site'] == site]
        if len(selected) != 1 or selected[0]['before']['registers'][register] != wanted:
            raise ValueError('the channel builder substitutes matching bytes for the actual full live store register')
    for operand in result['accesses']:
        if operand['site'] in (0x6F4A4, 0x6F4CA):
            if (operand['domain'] != 'frame' or operand['address'] != observed['sp'] - 37
                    or operand['width_bytes'] != 1 or operand['bytes'] != '01'):
                raise ValueError('the channel builder detaches its actual saved native channel byte')
    request_operands = [(0x6F536 if value['second_inverse'] is not None else 0x6F58E, 'write', value['initial_request']),
                        (0x6F5E4, 'read', value['initial_request'])]
    if value['ordered_branch'] != 'unchanged':
        request_operands.append((0x6F5F6, 'write', value['ordered']))
    if value['first_active']:
        request_operands.append((0x6F636, 'read', value['ordered']))
        if value['ordered'] > value['soft_limit']:
            request_operands.append((0x6F63E, 'write', value['soft_limit']))
    if value['second_active']:
        request_operands.append((0x6F654, 'read', value['soft_result']))
        if value['soft_result'] > value['hard_limit']:
            request_operands.append((0x6F65E, 'write', value['hard_limit']))
    request_operands.append((0x6F664, 'read', value['value']))
    sites = {0x6F536, 0x6F58E, 0x6F5E4, 0x6F5F6, 0x6F636, 0x6F63E, 0x6F654, 0x6F65E, 0x6F664}
    actual = [(operand['site'], operand['mode'], int(operand['bytes'], 16)) for operand in result['accesses']
              if operand['domain'] == 'frame' and operand['site'] in sites]
    same(actual, request_operands, 'the channel builder changes its actual live request frame through either cap')
    for operand in result['accesses']:
        if operand['site'] in sites and (operand['domain'] != 'frame'
                or operand['address'] != observed['sp'] - 36 or operand['width_bytes'] != 4):
            raise ValueError('the channel builder changes its actual local request long address or width')
    first = next(index for index, row in enumerate(trace) if row['site'] == 0x6F49E)
    last = next(index for index, row in enumerate(trace) if row['site'] == 0x6F66C)
    if (trace[first]['after']['gbr'] != 0x9574 or trace[last]['after']['gbr'] != observed['context'][15]
            or any(row['before']['gbr'] != 0x9574 for row in trace[first + 1:last + 1])):
        raise ValueError('the channel builder changes its actual ROM GBR lifetime or natural restoration')
