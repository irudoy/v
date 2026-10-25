"""Independent ordered native-index1 reads, full-width live bit operands and complete natural state."""
from kb import test_contract
from kb import rest_position_judgement_contract as contract

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
EXACT_SITES = {at for first, last in contract.SPANS for at in range(first, last, 2)}
FEASIBLE_SITES = EXACT_SITES
FIXED_BRANCHES = {}


def same(actual, expected, reason):
    if not test_contract.exact(actual, expected):
        raise ValueError(reason)


def signed_byte(raw):
    return raw if raw < 128 else raw - 256


def operands(observed, value):
    out = bytearray(observed['memory_before'][0])
    calibration = observed['calibration_before']
    events, live = [], []
    def read(site, at, register):
        raw = out[at]
        events.append(dict(site=site, mode='read', address=RAM_BASE + at, width_bytes=1,
            register=register, domain='ram', bytes=bytes([raw]).hex()))
        return raw
    def write(site, at, register, number):
        raw = number & 255
        events.append(dict(site=site, mode='write', address=RAM_BASE + at, width_bytes=1,
            register=register, domain='ram', bytes=bytes([raw]).hex()))
        live.append((site, register, number & MASK))
        out[at] = raw
    def control(site, at, register):
        raw = calibration[at]
        if len(raw) != 1:
            raise ValueError('the rest-position physical control loses its exact byte width')
        events.append(dict(site=site, mode='read', address=at, width_bytes=1,
            register=register, domain='rom', bytes=raw.hex()))
        return raw[0]
    if observed['context'][5]:
        read(0x9026E, 0x2327, 0)
    if not value['enabled']:
        old = read(0x9046C, 0x3599, 6)
        write(0x90472, 0x3599, 6, signed_byte(old) & ~2)
        second = control(0x90476, 0x871F, 6)
        write(0x9047C, 0x430B, 6, signed_byte(second))
        first = control(0x90482, 0x855D, 6)
        write(0x90488, 0x42F7, 6, signed_byte(first))
        high = control(0x9048E, 0x8E25, 0)
        write(0x90498, 0x43C1, 4, signed_byte(high))
        low = control(0x9049E, 0x8E1C, 5)
        write(0x904A4, 0x43B7, 5, signed_byte(low))
        write(0x904B0, 0x43B5, 4, signed_byte(high))
        write(0x904BA, 0x43AF, 5, signed_byte(low))
    else:
        flag = read(0x9027A, 0x43C3, 0)
        if not flag:
            read(0x90284, 0x24AB, 0)
        if not value['first_permit']:
            raw = control(0x90294, 0x855D, 6)
            write(0x9029A, 0x42F7, 6, signed_byte(raw))
            old = read(0x902A4, 0x3599, 6)
            write(0x902A8, 0x3599, 6, signed_byte(old) & ~2)
        flag = read(0x902AA, 0x43C2, 0)
        if not flag:
            flag = read(0x902B4, 0x24AA, 0)
            if flag & 0x58 == 0x58:
                read(0x902C4, 0x2458, 0)
        if not value['second_permit']:
            raw = control(0x902D0, 0x871F, 6)
            write(0x902D6, 0x430B, 6, signed_byte(raw))
            old = read(0x902E0, 0x3599, 6)
            write(0x902E4, 0x3599, 6, signed_byte(old) & ~2)
        counter = read(0x902EC, 0x42F7, 6)
        first = value['first']
        if not counter:
            old = read(0x902FC, 0x3599, 6)
            write(0x90304, 0x3599, 6, signed_byte(old) | 2)
            selected = read(0x9030C, 0x16BB, 6)
            high = control(0x9030E, 0x8951, 2)
            if selected <= 128 + high:
                control(0x9031C, 0x8952, 6)
            if first['outside']:
                timer = read(0x90332, 0x43C1, 6)
                if not timer:
                    old = read(0x9033C, 0x358B, 2)
                    write(0x90340, 0x358B, 2, signed_byte(old) | 2)
                timer = read(0x9034C, 0x43B7, 6)
                if not timer:
                    old = read(0x90356, 0x3582, 2)
                    write(0x9035C, 0x3582, 2, signed_byte(old) | 2)
        if counter or not first['outside']:
            high = control(0x9036E, 0x8E25, 0)
            write(0x90378, 0x43C1, 4, signed_byte(high))
            low = control(0x90380, 0x8E1C, 2)
            write(0x90382, 0x43B7, 2, signed_byte(low))
        counter = read(0x9038A, 0x430B, 6)
        second = value['second']
        if not counter:
            old = read(0x9039A, 0x3599, 6)
            write(0x903A2, 0x3599, 6, signed_byte(old) | 2)
            selected = read(0x903AA, 0x16BB, 6)
            high = control(0x903AC, 0x8736, 2)
            if selected <= 128 + high:
                control(0x903BA, 0x8737, 2)
            if second['outside']:
                timer = read(0x903CE, 0x43B5, 2)
                if not timer:
                    old = read(0x903D8, 0x358B, 2)
                    write(0x903DC, 0x358B, 2, signed_byte(old) | 2)
                timer = read(0x903E8, 0x43AF, 6)
                if not timer:
                    old = read(0x90438, 0x3582, 2)
                    write(0x9043E, 0x3582, 2, signed_byte(old) | 2)
        if counter or not second['outside']:
            high = control(0x90448, 0x8E25, 0)
            write(0x90452, 0x43B5, 5, signed_byte(high))
            low = control(0x9045A, 0x8E1C, 2)
            write(0x9045E, 0x43AF, 2, signed_byte(low))
    same(bytes(out), value['memory'], 'the rest-position physical events disagree with complete independent byte equations')
    return events, live


def require(observed, result, value, fixture):
    same(observed['exit'], (result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
        'the rest-position judgement changes complete independent exit CPU/SR')
    if (observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)
            or observed['memory_after'] != (value['memory'],)):
        raise ValueError('the rest-position judgement changes a complete frame, computed byte or unrelated RAM')
    if (observed['context'][4] != 1 or result['sp'] != observed['sp'] or result['pr'] != observed['continuation']
            or (result['gbr'], result['mach'], result['macl']) != observed['context'][15:18]
            or tuple(result['registers'][8:15]) != observed['context'][8:15] or result['calls']):
        raise ValueError('the rest-position judgement changes its exact bank premise, preserved CPU, natural return or call-free body')
    trace = result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site'] != contract.ENTRY:
        raise ValueError('the rest-position judgement omits the complete natural entry')
    initial = trace[0]['before']
    same(tuple(initial[k] for k in ('registers', 'gbr', 'mach', 'macl', 'sr', 'pr')),
        ((*observed['context'][:15], observed['sp']), *observed['context'][15:18], observed['sr_before'], observed['continuation']),
        'the rest-position judgement detaches the actual complete incoming CPU')
    for index, row in enumerate(trace):
        next_site = trace[index + 1]['site'] if index + 1 < len(trace) else observed['continuation']
        if (row['site'] not in EXACT_SITES or row['next'] != next_site
                or row['bytes'] != fixture[row['site']:row['site'] + 2].hex()
                or row['word'] != int.from_bytes(fixture[row['site']:row['site'] + 2], 'big')):
            raise ValueError('the rest-position judgement changes an exact instruction, delay or continuation')
        if index + 1 < len(trace):
            same(row['after'], trace[index + 1]['before'], 'the rest-position judgement detaches complete intermediate CPU state')
    same(result['code'], {r['site']: fixture[r['site']:r['site'] + 2].hex() for r in trace},
        'the rest-position judgement changes exact executed instruction identities')
    if {r['site'] for r in trace if r['delay_slot']} != {r['site'] + 2 for r in result['branches'] if r['delay']}:
        raise ValueError('the rest-position judgement omits or invents a natural delay slot')
    wanted, live = operands(observed, value)
    actual = []
    for event in result['accesses']:
        site = event['site']
        if event['domain'] == 'frame':
            continue
        if site in contract.LITERAL_OPERANDS:
            at, width, register = contract.LITERAL_OPERANDS[site]
            same(event, dict(site=site, mode='read', address=at, width_bytes=width, register=register,
                domain='rom', bytes=fixture[at:at + width].hex()), 'the rest-position judgement changes an exact PC literal operand')
        else:
            actual.append(event)
    same(actual, wanted, 'the rest-position judgement changes ordered real RAM/ROM addresses, byte widths, directions or values')
    for site, register, wanted_value in live:
        selected = [r for r in trace if r['site'] == site]
        if len(selected) != 1 or selected[0]['before']['registers'][register] != wanted_value:
            raise ValueError('the rest-position judgement substitutes matching bytes for an actual full-width live store register')
    for row in trace:
        if 0x9025C <= row['site'] <= 0x904C0 and row['before']['gbr'] != RAM_BASE + 0x42D3:
            raise ValueError('the rest-position judgement loses its actual relocated GBR base')
    local_sites = {0x902FA, 0x9033A, 0x90354, 0x90398, 0x903D6, 0x90436}
    for event in result['accesses']:
        if event['site'] in local_sites:
            if (event['domain'] != 'frame' or event['address'] != observed['sp'] - 8
                    or event['width_bytes'] != 1 or event['bytes'] != '02'):
                raise ValueError('the rest-position judgement changes its real local bank-mask byte across the two windows')
