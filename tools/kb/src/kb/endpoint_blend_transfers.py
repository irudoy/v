"""Complete actual endpoint calls, word operands, signed stores and natural frame state."""
from kb import test_contract
from kb import endpoint_blend_contract as contract, endpoint_blend_semantics as numeric

MASK = 0xFFFFFFFF
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# A fractional axis interval has lower < coordinate < upper. Its actual
# unsigned divisor is positive; the generic divider's zero return is unused.
INFEASIBLE_SITES = {0x26DA2, 0x26DA4}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x26D12: 'fallthrough'}
CALL_TARGETS = {0x740E6: 0x74028, 0x740EA: 0x740AE, 0x74072: 0x26628, 0x7408C: 0x26628,
                0x26634: 0x26B84, 0x26642: 0x26B84, 0x26BAA: 0x26D10,
                0x26B4A: 0x26AF8, 0x26B5A: 0x26AF8, 0x26B62: 0x26AF8, 0x26B76: 0x26AF8}
FIXED_STACK_DELTAS = {0x740E6: -8, 0x740EA: -8, 0x74072: -44, 0x7408C: -44,
                      0x26634: -52, 0x26642: -60, 0x26B4A: -52, 0x26B5A: -56,
                      0x26B62: -52, 0x26B76: -52}
TABLE_SITES = {0x26B44, 0x26B46, 0x26B54, 0x26B56, 0x26B6E, 0x26B70}
AXIS_SITES = {0x26B86, 0x26B9C, 0x26B9E}


def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)


def ram_event(site, mode, at, width, register, raw):
    return dict(site=site, mode=mode, address=0x01000000+at, width_bytes=width,
                register=register, domain='ram', bytes=raw.hex())


def ram_operands(memory, value):
    rows = [ram_event(0x74040, 'read', 0x4255, 1, 0, memory[0x4255:0x4256]),
            ram_event(0x74046, 'read', 0x10D2, 2, 0, memory[0x10D2:0x10D4])]
    if memory[0x4255] & 128:
        rows.append(ram_event(0x7404A, 'read', 0x10E2, 2, 0, memory[0x10E2:0x10E4]))
    rows.extend([
        ram_event(0x7405E, 'read', 0x1210, 2, 0, memory[0x1210:0x1212]),
        ram_event(0x74082, 'write', 0x1CFC, 2, 2, (value['signed_a'] & 65535).to_bytes(2, 'big')),
        ram_event(0x7408A, 'read', 0x1210, 2, 0, memory[0x1210:0x1212]),
        ram_event(0x74098, 'write', 0x1CFE, 2, 2, (value['signed_b'] & 65535).to_bytes(2, 'big')),
        ram_event(0x740B2, 'read', 0x245C, 1, 0, memory[0x245C:0x245D]),
        ram_event(0x740BC, 'read', 0x1D0C, 2, 2, memory[0x1D0C:0x1D0E]),
        ram_event(0x740E0, 'write', 0x1D0C, 2, 2, value['weight'].to_bytes(2, 'big')),
        ram_event(0x740F2, 'read', 0x1D0C, 2, 5, value['weight'].to_bytes(2, 'big')),
    ])
    if value['weight'] == 0:
        rows.append(ram_event(0x740FE, 'read', 0x1CFC, 2, 2, (value['signed_a'] & 65535).to_bytes(2, 'big')))
    elif value['weight'] == 65535:
        rows.append(ram_event(0x7410C, 'read', 0x1CFE, 2, 6, (value['signed_b'] & 65535).to_bytes(2, 'big')))
    else:
        rows.extend([ram_event(0x74114, 'read', 0x1CFC, 2, 6, (value['signed_a'] & 65535).to_bytes(2, 'big')),
                     ram_event(0x7411C, 'read', 0x1CFE, 2, 2, (value['signed_b'] & 65535).to_bytes(2, 'big'))])
    rows.append(ram_event(0x7412E, 'write', 0x1CF6, 2, 2, value['value'].to_bytes(2, 'big')))
    return rows


def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
         'the endpoint blend changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the endpoint blend changes a complete frame, unrelated RAM or independent numerical publication')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or result['gbr'] != observed['context'][15] or result['mach'] != observed['context'][16]
            or result['macl'] != observed['context'][17]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the endpoint blend changes a retained outer register, MACL, GBR or natural return')
    if (result['registers'][0] != 0x0A6A or result['registers'][2] != value['output'] & MASK
            or result['registers'][4] != value['weight'] or result['registers'][7] != 0x0100128C):
        raise ValueError('the endpoint blend changes its actual transformed final live operands')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the endpoint blend lacks its complete natural entry trace')
    initial = trace[0]['before']
    same(tuple(initial[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
         ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
         'the endpoint blend detaches its complete initial CPU from immutable inputs')
    for index, row in enumerate(trace):
        destination = trace[index+1]['site'] if index+1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != destination
                or row['word'] != int.from_bytes(fixture[row['site']:row['site']+2], 'big')
                or row['bytes'] != fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the endpoint blend changes a complete actual instruction or continuation')
        if index+1 < len(trace):
            same(row['after'], trace[index+1]['before'], 'the endpoint blend detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site']+2].hex() for row in trace},
         'the endpoint blend changes exact executed instruction identities')
    delayed = {row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the endpoint blend omits or invents a real delay slot')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind'] != FIXED_BRANCHES[row['site']]:
            raise ValueError('the endpoint blend reaches an impossible natural positive-divisor branch')
    actual_ram = [row for row in result['accesses'] if row['domain'] == 'ram']
    same(actual_ram, ram_operands(observed['memory_before'][0], value),
         'the endpoint blend changes ordered independent physical RAM operands or observed word bytes')
    calibration = observed['calibration_before']
    step_reads = []
    for event in result['accesses']:
        site, address, width = event['site'], event['address'], event['width_bytes']
        if event['domain'] in ('frame', 'ram'):
            continue
        if site in contract.LITERAL_OPERANDS:
            at, size, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=size, register=register,
                             domain='rom', bytes=fixture[at:at+size].hex()),
                 'the endpoint blend changes an exact PC literal operand')
        elif site == 0x740BA:
            step_reads.append(event)
            same(event, dict(site=site, mode='read', address=0x162DC, width_bytes=2, register=6,
                             domain='rom', bytes=calibration[0x162DC].hex()),
                 'the endpoint blend changes the actual live weight-step word')
        elif (site not in TABLE_SITES | AXIS_SITES or event['domain'] != 'rom' or event['mode'] != 'read'
                or width != 2 or not any(at <= address and address+2 <= at+len(raw)
                                         for at, raw in calibration.items() if at in (0x16FC8, 0x171C8, 0x18916, 0x18936))
                or event['bytes'] != fixture[address:address+2].hex()):
            raise ValueError('the endpoint blend accesses an undeclared table, axis or memory domain')
    if len(step_reads) != 1:
        raise ValueError('the endpoint blend omits or repeats its actual weight-step word')
    for address, endpoint in ((0x171C8, value['endpoint_a']), (0x16FC8, value['endpoint_b'])):
        actual = [row for row in result['accesses'] if address <= row['address'] < address+512 and row['domain'] == 'rom']
        expected = []
        if endpoint['fraction_y']:
            sites = [(0x26B44, 1), (0x26B46, 0)]
            if endpoint['fraction_x']:
                sites += [(0x26B54, 1), (0x26B56, 0)]
        else:
            sites = [(0x26B6E, 0)]
            if endpoint['fraction_x']:
                sites += [(0x26B70, 2)]
        for cell, (site, register) in zip(endpoint['cells'], sites):
            expected.append(dict(site=site, mode='read', address=address+2*cell, width_bytes=2, register=register,
                                 domain='rom', bytes=calibration[address][2*cell:2*cell+2].hex()))
        same(actual, expected, 'the endpoint blend changes actual lazy-neighbor word addresses, sites or byte order')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site+4:
            raise ValueError('the endpoint blend changes an actual helper call or continuation')
        if site in FIXED_STACK_DELTAS and call['sp'] != observed['sp'] + FIXED_STACK_DELTAS[site]:
            raise ValueError('the endpoint blend changes a natural nested stack frame')
        start = next((index+2 for index in range(cursor, len(trace)-2) if trace[index]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the endpoint blend replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
             (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
             'the endpoint blend detaches complete actual post-delay arguments')
        terminal = next((index for index in range(start, len(trace)-1)
                         if any(branch['kind'] == 'return' for branch in trace[index]['branches'])
                         and trace[index+1]['next'] == site+4), None)
        if terminal is None:
            raise ValueError('the endpoint blend omits a complete natural helper return')
        returned = trace[terminal+1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site+4:
            raise ValueError('the endpoint blend changes actual helper return SP or PR')
        call_spans.append((call, start, terminal+1, returned))
        registers = call['entry']['registers']
        if call['target'] == 0x26AF8:
            if returned['registers'][0] != numeric.directed_word(registers[0], registers[2], registers[3]):
                raise ValueError('the endpoint blend changes an independent directed word interpolation return')
        elif call['target'] == 0x26D10:
            divisor, dividend = registers[:2]
            if (not 0 < divisor <= 65535 or dividend & 65535 or dividend // divisor > 65535
                    or returned['registers'][0] != dividend // divisor):
                raise ValueError('the endpoint blend changes actual positive axis division operands or quotient')
    for site, table, endpoint in ((0x74072, 0x171C8, value['endpoint_a']), (0x7408C, 0x16FC8, value['endpoint_b'])):
        selected = [row for row in call_spans if row[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the endpoint blend omits or repeats a complete real endpoint invocation')
        call, start, end, returned = selected[0]
        same(tuple(call['entry']['registers'][4:8]), (table, 0x18916, 0x18936, value['x']),
             'the endpoint blend changes actual endpoint table/axis/coordinate registers')
        if returned['registers'][0] != endpoint['returned'] & MASK:
            raise ValueError('the endpoint blend substitutes a scalar for the real signed raw endpoint return')
        local = trace[start:end+1]
        stack_reads = [event for row in local for event in row['accesses'] if event['site'] == 0x2663E]
        if (len(stack_reads) != 1 or stack_reads[0]['domain'] != 'frame' or stack_reads[0]['address'] != call['sp']
                or stack_reads[0]['width_bytes'] != 4 or int(stack_reads[0]['bytes'], 16) & 65535 != value['y']):
            raise ValueError('the endpoint blend loses the actual caller-local column word and its full dword read')
        tails = [row for row in local if row['site'] == 0x26656]
        if (len(tails) != 1 or not tails[0]['delay_slot'] or tails[0]['next'] != 0x26B28
                or tails[0]['after']['registers'][15] != call['sp'] or tails[0]['after']['pr'] != site+4):
            raise ValueError('the endpoint blend replaces the real wrapper tail or restored return state')
        for axis_site, axis, coordinate, index, fraction in (
                (0x26634, 0x18916, value['x'], endpoint['row'], endpoint['fraction_x']),
                (0x26642, 0x18936, value['y'], endpoint['column'], endpoint['fraction_y'])):
            axis_rows = [row for row in call_spans if row[0]['site'] == axis_site and start <= row[1] <= end]
            if len(axis_rows) != 1:
                raise ValueError('the endpoint blend omits an actual full axis invocation')
            axis_call, axis_start, axis_end, axis_returned = axis_rows[0]
            registers = axis_call['entry']['registers']
            if ((registers[0], registers[4], registers[5]) != (axis, 30, coordinate)
                    or (axis_returned['registers'][4], axis_returned['registers'][5]) != (2*index, fraction)):
                raise ValueError('the endpoint blend changes a real axis argument, lower knot or fraction')
            actual = [event for row in trace[axis_start:axis_end+1] for event in row['accesses']
                      if event['domain'] == 'rom' and axis <= event['address'] < axis+32]
            expected = [dict(site=0x26B86, mode='read', address=axis+2*knot, width_bytes=2, register=1,
                             domain='rom', bytes=calibration[axis][2*knot:2*knot+2].hex()) for knot in range(15, index-1, -1)]
            if fraction:
                expected += [dict(site=site_read, mode='read', address=axis+2*knot, width_bytes=2, register=register,
                                  domain='rom', bytes=calibration[axis][2*knot:2*knot+2].hex())
                             for site_read, knot, register in ((0x26B9C, index, 1), (0x26B9E, index+1, 0))]
            same(actual, expected, 'the endpoint blend changes complete backwards axis reads or a real fractional neighbor')
    stores = {site: [row for row in trace if row['site'] == site] for site in (0x74082, 0x74098, 0x740E0, 0x7412E)}
    for site, register, wanted in ((0x74082, 2, value['publication_register_a']), (0x74098, 2, value['publication_register_b']),
                                   (0x740E0, 2, value['weight']), (0x7412E, 2, value['output'])):
        if len(stores[site]) != 1 or stores[site][0]['before']['registers'][register] != wanted & MASK:
            raise ValueError('the endpoint blend substitutes matching bytes for an independently transformed live store register')
