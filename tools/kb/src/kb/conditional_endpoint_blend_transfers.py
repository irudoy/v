"""Complete actual endpoint calls, word operands, signed stores and natural frame state."""
from kb import test_contract
from kb import conditional_endpoint_blend_contract as contract, conditional_endpoint_blend_semantics as numeric

MASK = 0xFFFFFFFF
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
# A fractional axis interval has lower < coordinate < upper. Its actual
# unsigned divisor is positive; the generic divider's zero return is unused.
INFEASIBLE_SITES = {0x26D0A, 0x26D0C}
FEASIBLE_SITES = EXACT_SITES - INFEASIBLE_SITES
FIXED_BRANCHES = {0x26C7A: 'fallthrough'}
CALL_TARGETS = {0x7611C: 0x7604C, 0x76120: 0x760D2, 0x76096: 0x262A8, 0x760B0: 0x262A8,
                0x262B4: 0x26984, 0x262C2: 0x26984, 0x269AA: 0x26C78,
                0x2686A: 0x26740, 0x2687A: 0x26740, 0x26882: 0x26740, 0x26896: 0x26740}
FIXED_STACK_DELTAS = {0x7611C: -8, 0x76120: -8, 0x76096: -44, 0x760B0: -44,
                      0x262B4: -52, 0x262C2: -60, 0x2686A: -52, 0x2687A: -56,
                      0x26882: -52, 0x26896: -52}
TABLE_SITES = {0x26864, 0x26866, 0x26874, 0x26876, 0x2688E, 0x26890}
AXIS_SITES = {0x26986, 0x2699C, 0x2699E}


def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)


def ram_event(site, mode, at, width, register, raw):
    return dict(site=site, mode=mode, address=0x1000000+at, width_bytes=width,
                register=register, domain='ram', bytes=raw.hex())


def ram_operands(memory, value):
    if not value['enabled']:
        return []
    rows = [ram_event(0x76064, 'read', 0x4255, 1, 0, memory[0x4255:0x4256]),
            ram_event(0x7606A, 'read', 0x10D2, 2, 0, memory[0x10D2:0x10D4])]
    if memory[0x4255] & 128:
        rows.append(ram_event(0x7606E, 'read', 0x10E2, 2, 0, memory[0x10E2:0x10E4]))
    rows.extend([
        ram_event(0x76082, 'read', 0x1210, 2, 0, memory[0x1210:0x1212]),
        ram_event(0x760A6, 'write', 0x18EC, 2, 2, (value['signed_a'] & 65535).to_bytes(2, 'big')),
        ram_event(0x760AE, 'read', 0x1210, 2, 0, memory[0x1210:0x1212]),
        ram_event(0x760BC, 'write', 0x18EE, 2, 2, (value['signed_b'] & 65535).to_bytes(2, 'big')),
        ram_event(0x760D8, 'read', 0x245C, 1, 0, memory[0x245C:0x245D]),
        ram_event(0x760DE, 'read', 0x2420, 2, 0, memory[0x2420:0x2422]),
        ram_event(0x76102, 'write', 0x2420, 2, 0, value['weight'].to_bytes(2, 'big')),
        ram_event(0x76128, 'read', 0x2420, 2, 5, value['weight'].to_bytes(2, 'big')),
    ])
    if value['weight'] == 0:
        rows.append(ram_event(0x76136, 'read', 0x18EC, 2, 2, (value['signed_a'] & 65535).to_bytes(2, 'big')))
    elif value['weight'] == 65535:
        rows.append(ram_event(0x76146, 'read', 0x18EE, 2, 2, (value['signed_b'] & 65535).to_bytes(2, 'big')))
    else:
        rows.extend([ram_event(0x76152, 'read', 0x18EC, 2, 6, (value['signed_a'] & 65535).to_bytes(2, 'big')),
                     ram_event(0x76158, 'read', 0x18EE, 2, 2, (value['signed_b'] & 65535).to_bytes(2, 'big'))])
    rows.append(ram_event(0x76168, 'write', 0x18E6, 2, 2, value['value'].to_bytes(2, 'big')))
    return rows


def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
         'the conditional endpoint blend changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the conditional endpoint blend changes a complete frame, unrelated RAM or independent numerical publication')
    if (result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or result['gbr'] != observed['context'][15] or result['mach'] != observed['context'][16]
            or result['macl'] != observed['context'][17]
            or tuple(result['registers'][8:15]) != observed['context'][8:15]):
        raise ValueError('the conditional endpoint blend changes a retained outer register, MACL, GBR or natural return')
    if value['enabled']:
        if (result['registers'][0] != 0x65A or result['registers'][2] != value['output'] & MASK
                or result['registers'][4] != 0x0100128C or result['registers'][5] != value['weight']):
            raise ValueError('the conditional blend changes its actual transformed final live operands')
    else:
        expected=list(observed['context'][:15])
        rejected_first=value['branch']=='gate-a-refusal'
        raw=value['gate_a'] if rejected_first else value['gate_b']
        expected[0]=(raw if raw<128 else raw-256)&MASK
        expected[6]=0x8B3F if rejected_first else 0x89FA
        same(tuple(result['registers']),tuple(expected), 'the conditional refusal changes another complete live register')
        if result['sr'] != (observed['sr_before']&~1)|int(not rejected_first):
            raise ValueError('the conditional refusal changes its independently predicted full SR')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the conditional endpoint blend lacks its complete natural entry trace')
    initial = trace[0]['before']
    same(tuple(initial[key] for key in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
         ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
         'the conditional endpoint blend detaches its complete initial CPU from immutable inputs')
    for index, row in enumerate(trace):
        destination = trace[index+1]['site'] if index+1 < len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next'] != destination
                or row['word'] != int.from_bytes(fixture[row['site']:row['site']+2], 'big')
                or row['bytes'] != fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the conditional endpoint blend changes a complete actual instruction or continuation')
        if index+1 < len(trace):
            same(row['after'], trace[index+1]['before'], 'the conditional endpoint blend detaches complete intermediate CPU state')
    same(result['code'], {row['site']: fixture[row['site']:row['site']+2].hex() for row in trace},
         'the conditional endpoint blend changes exact executed instruction identities')
    delayed = {row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']} != delayed:
        raise ValueError('the conditional endpoint blend omits or invents a real delay slot')
    for row in result['branches']:
        if row['site'] in FIXED_BRANCHES and row['kind'] != FIXED_BRANCHES[row['site']]:
            raise ValueError('the conditional endpoint blend reaches an impossible natural positive-divisor branch')
    actual_ram = [row for row in result['accesses'] if row['domain'] == 'ram']
    same(actual_ram, ram_operands(observed['memory_before'][0], value),
         'the conditional endpoint blend changes ordered independent physical RAM operands or observed word bytes')
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
                 'the conditional endpoint blend changes an exact PC literal operand')
        elif site == 0x760E0:
            step_reads.append(event)
            same(event, dict(site=site, mode='read', address=0x90A0, width_bytes=2, register=6,
                             domain='rom', bytes=calibration[0x90A0].hex()),
                 'the conditional endpoint blend changes the actual live weight-step word')
        elif site in (0x7610E,0x76116):
            pass
        elif (site not in TABLE_SITES | AXIS_SITES or event['domain'] != 'rom' or event['mode'] != 'read'
                or width != 2 or not any(at <= address and address+2 <= at+len(raw)
                                         for at, raw in calibration.items() if at in (0xE08E, 0xDE8E, 0x13D14, 0x13D34))
                or event['bytes'] != fixture[address:address+2].hex()):
            raise ValueError('the conditional endpoint blend accesses an undeclared table, axis or memory domain')
    gate_reads=[event for event in result['accesses'] if event['site'] in (0x7610E,0x76116)]
    expected_gates=[dict(site=0x7610E,mode='read',address=0x8B3F,width_bytes=1,register=0,domain='rom',bytes=calibration[0x8B3F].hex())]
    if value['branch']!='gate-a-refusal':
        expected_gates.append(dict(site=0x76116,mode='read',address=0x89FA,width_bytes=1,register=0,domain='rom',bytes=calibration[0x89FA].hex()))
    same(gate_reads,expected_gates,'the conditional blend replaces an actual ordered ROM gate operand')
    if len(step_reads) != int(value['enabled']):
        raise ValueError('the conditional blend omits, repeats or invents its actual weight-step word')
    if not value['enabled']:
        if result['calls'] or any(event['site'] in TABLE_SITES|AXIS_SITES for event in result['accesses']):
            raise ValueError('the disabled conditional blend invents a call, surface or axis operand')
        return
    for address, endpoint in ((0xDE8E, value['endpoint_a']), (0xE08E, value['endpoint_b'])):
        actual = [row for row in result['accesses'] if address <= row['address'] < address+512 and row['domain'] == 'rom']
        expected = []
        if endpoint['fraction_y']:
            sites = [(0x26864, 1), (0x26866, 0)]
            if endpoint['fraction_x']:
                sites += [(0x26874, 1), (0x26876, 0)]
        else:
            sites = [(0x2688E, 0)]
            if endpoint['fraction_x']:
                sites += [(0x26890, 2)]
        for cell, (site, register) in zip(endpoint['cells'], sites):
            expected.append(dict(site=site, mode='read', address=address+2*cell, width_bytes=2, register=register,
                                 domain='rom', bytes=calibration[address][2*cell:2*cell+2].hex()))
        same(actual, expected, 'the conditional endpoint blend changes actual lazy-neighbor word addresses, sites or byte order')
    call_spans = []
    cursor = 0
    for call in result['calls']:
        site = call['site']
        if call['target'] != CALL_TARGETS.get(site) or call['return_address'] != site+4:
            raise ValueError('the conditional endpoint blend changes an actual helper call or continuation')
        if site in FIXED_STACK_DELTAS and call['sp'] != observed['sp'] + FIXED_STACK_DELTAS[site]:
            raise ValueError('the conditional endpoint blend changes a natural nested stack frame')
        start = next((index+2 for index in range(cursor, len(trace)-2) if trace[index]['site'] == site), None)
        if start is None or trace[start]['site'] != call['target']:
            raise ValueError('the conditional endpoint blend replaces a real post-delay helper entry')
        before = trace[start]['before']
        cursor = start
        same(tuple(call['entry'][key] for key in ('registers', 'sp', 'gbr', 'mach', 'macl', 'sr', 'pr')),
             (tuple(before['registers'][:15]), before['registers'][15], before['gbr'], before['mach'], before['macl'], before['sr'], before['pr']),
             'the conditional endpoint blend detaches complete actual post-delay arguments')
        terminal = next((index for index in range(start, len(trace)-1)
                         if any(branch['kind'] == 'return' for branch in trace[index]['branches'])
                         and trace[index+1]['next'] == site+4), None)
        if terminal is None:
            raise ValueError('the conditional endpoint blend omits a complete natural helper return')
        returned = trace[terminal+1]['after']
        if returned['registers'][15] != call['sp'] or returned['pr'] != site+4:
            raise ValueError('the conditional endpoint blend changes actual helper return SP or PR')
        call_spans.append((call, start, terminal+1, returned))
        registers = call['entry']['registers']
        if call['target'] == 0x26740:
            if returned['registers'][0] != numeric.directed_word(registers[0], registers[2], registers[3]):
                raise ValueError('the conditional endpoint blend changes an independent directed word interpolation return')
        elif call['target'] == 0x26C78:
            divisor, dividend = registers[:2]
            if (not 0 < divisor <= 65535 or dividend & 65535 or dividend // divisor > 65535
                    or returned['registers'][0] != dividend // divisor):
                raise ValueError('the conditional endpoint blend changes actual positive axis division operands or quotient')
    for site, table, endpoint in ((0x76096, 0xDE8E, value['endpoint_a']), (0x760B0, 0xE08E, value['endpoint_b'])):
        selected = [row for row in call_spans if row[0]['site'] == site]
        if len(selected) != 1:
            raise ValueError('the conditional endpoint blend omits or repeats a complete real endpoint invocation')
        call, start, end, returned = selected[0]
        same(tuple(call['entry']['registers'][4:8]), (table, 0x13D14, 0x13D34, value['x']),
             'the conditional endpoint blend changes actual endpoint table/axis/coordinate registers')
        if returned['registers'][0] != endpoint['returned'] & MASK:
            raise ValueError('the conditional endpoint blend substitutes a scalar for the real signed raw endpoint return')
        local = trace[start:end+1]
        stack_reads = [event for row in local for event in row['accesses'] if event['site'] == 0x262BE]
        if (len(stack_reads) != 1 or stack_reads[0]['domain'] != 'frame' or stack_reads[0]['address'] != call['sp']
                or stack_reads[0]['width_bytes'] != 4 or int(stack_reads[0]['bytes'], 16) & 65535 != value['y']):
            raise ValueError('the conditional endpoint blend loses the actual caller-local column word and its full dword read')
        tails = [row for row in local if row['site'] == 0x262D6]
        if (len(tails) != 1 or not tails[0]['delay_slot'] or tails[0]['next'] != 0x26848
                or tails[0]['after']['registers'][15] != call['sp'] or tails[0]['after']['pr'] != site+4):
            raise ValueError('the conditional endpoint blend replaces the real wrapper tail or restored return state')
        for axis_site, axis, coordinate, index, fraction in (
                (0x262B4, 0x13D14, value['x'], endpoint['row'], endpoint['fraction_x']),
                (0x262C2, 0x13D34, value['y'], endpoint['column'], endpoint['fraction_y'])):
            axis_rows = [row for row in call_spans if row[0]['site'] == axis_site and start <= row[1] <= end]
            if len(axis_rows) != 1:
                raise ValueError('the conditional endpoint blend omits an actual full axis invocation')
            axis_call, axis_start, axis_end, axis_returned = axis_rows[0]
            registers = axis_call['entry']['registers']
            if ((registers[0], registers[4], registers[5]) != (axis, 30, coordinate)
                    or (axis_returned['registers'][4], axis_returned['registers'][5]) != (2*index, fraction)):
                raise ValueError('the conditional endpoint blend changes a real axis argument, lower knot or fraction')
            actual = [event for row in trace[axis_start:axis_end+1] for event in row['accesses']
                      if event['domain'] == 'rom' and axis <= event['address'] < axis+32]
            expected = [dict(site=0x26986, mode='read', address=axis+2*knot, width_bytes=2, register=1,
                             domain='rom', bytes=calibration[axis][2*knot:2*knot+2].hex()) for knot in range(15, index-1, -1)]
            if fraction:
                expected += [dict(site=site_read, mode='read', address=axis+2*knot, width_bytes=2, register=register,
                                  domain='rom', bytes=calibration[axis][2*knot:2*knot+2].hex())
                             for site_read, knot, register in ((0x2699C, index, 1), (0x2699E, index+1, 0))]
            same(actual, expected, 'the conditional endpoint blend changes complete backwards axis reads or a real fractional neighbor')
    stores = {site: [row for row in trace if row['site'] == site] for site in (0x760A6, 0x760BC, 0x76102, 0x76168)}
    for site, register, wanted in ((0x760A6, 2, value['publication_register_a']), (0x760BC, 2, value['publication_register_b']),
                                   (0x76102, 0, value['weight']), (0x76168, 2, value['output'])):
        if len(stores[site]) != 1 or stores[site][0]['before']['registers'][register] != wanted & MASK:
            raise ValueError('the conditional endpoint blend substitutes matching bytes for an independently transformed live store register')
