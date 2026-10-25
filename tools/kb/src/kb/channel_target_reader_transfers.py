"""Independent physical operands, live registers and complete natural leaf state."""
from kb import test_contract
from kb import channel_target_reader_contract as contract
from kb import channel_target_reader_semantics as numeric

MASK = 0xFFFFFFFF
EXACT_SITES = set(range(0xCB1CA, 0xCB1F8, 2))
FEASIBLE_SITES = EXACT_SITES
CONDITIONAL_SITES = (0xCB1E8,)


def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)


def require(observed, result, value, fixture):
    expected = numeric.exit_cpu(observed['context'], observed['sp'], observed['continuation'], observed['sr_before'], value)
    same(observed['exit'], expected, 'the indexed reader changes complete independent exit registers or SR')
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
         'the indexed reader changes independently reconstructed complete exit state')
    if (observed['frame_after'] != observed['frame_before'] or observed['frame_after'] != result['frame']
            or observed['memory_after'] != (value['memory'],) or observed['memory_after'] != (result['ram'],)):
        raise ValueError('the indexed reader changes an unrelated RAM byte or complete untouched leaf frame')
    if result['calls'] or result['sp'] != observed['sp'] or result['pr'] != observed['continuation']:
        raise ValueError('the indexed reader introduces a helper, stack mutation or different natural return')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the indexed reader lacks its complete natural entry trace')
    initial = trace[0]['before']
    same(tuple(initial[k] for k in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
         ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
         'the indexed reader detaches its full initial CPU from the actual immutable context')
    expected_sites = EXACT_SITES - ({0xCB1EA} if value['saturated'] else set())
    if set(row['site'] for row in trace) != expected_sites or len(trace) != len(expected_sites):
        raise ValueError('the indexed reader omits or repeats a complete selected stock instruction')
    by_site = {row['site']: row for row in trace}
    for index, row in enumerate(trace):
        destination = trace[index+1]['site'] if index+1 < len(trace) else observed['continuation']
        if (row['next'] != destination or row['word'] != int.from_bytes(fixture[row['site']:row['site']+2], 'big')
                or row['bytes'] != fixture[row['site']:row['site']+2].hex()
                or row['delay_slot'] != (row['site'] == 0xCB1F6)):
            raise ValueError('the indexed reader changes a complete instruction, real delay slot or continuation')
        if index+1 < len(trace):
            same(row['after'], trace[index+1]['before'], 'the indexed reader detaches intermediate complete CPU states')
    same(result['code'], {row['site']: fixture[row['site']:row['site']+2].hex() for row in trace},
         'the indexed reader changes exact executed instruction identities')
    expected_accesses = []
    for site in (0xCB1CA, 0xCB1D4, 0xCB1EC, 0xCB1F0, 0xCB1F6):
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            expected_accesses.append(dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                                          domain='rom', bytes=fixture[at:at+width].hex()))
        else:
            read = site == 0xCB1D4
            expected_accesses.append(dict(site=site, mode='read' if read else 'write',
                                          address=value['source'] if read else value['destination'], width_bytes=2,
                                          register=6, domain='ram', bytes=(value['word'] if read else value['value']).to_bytes(2, 'big').hex()))
    same(result['accesses'], expected_accesses, 'the indexed reader changes ordered actual word/literal operands or live memory bytes')
    load = by_site[0xCB1D4]
    if (load['before']['registers'][0] != 2 * value['index'] or load['before']['registers'][2] != 0x010028BC
            or load['after']['registers'][6] != value['sign_extended_word'] & MASK
            or by_site[0xCB1DA]['after']['registers'][2] != value['word']):
        raise ValueError('the indexed reader changes its live sign-extended word load or independent unsigned operand')
    comparison = by_site[0xCB1E6]
    if (comparison['before']['registers'][2] != value['scaled'] or comparison['before']['registers'][6] != 65535
            or comparison['after']['sr'] & 1 != int(value['saturated'])):
        raise ValueError('the indexed reader changes the actual unsigned saturation comparison')
    store = by_site[0xCB1F6]
    if store['before']['registers'][6] != value['value'] or store['next'] != observed['continuation']:
        raise ValueError('the indexed reader substitutes a scalar for the actual transformed live word in RTS delay')
    conditional = [row for row in result['branches'] if row['site'] == 0xCB1E8]
    returns = [row for row in result['branches'] if row['kind'] == 'return']
    if (len(result['branches']) != 2 or len(conditional) != 1 or len(returns) != 1
            or conditional[0]['kind'] != ('taken' if value['saturated'] else 'fallthrough')
            or returns[0]['site'] != 0xCB1F4 or returns[0]['target'] != observed['continuation'] or not returns[0]['delay']):
        raise ValueError('the indexed reader changes its one actual conditional or real delayed return')
