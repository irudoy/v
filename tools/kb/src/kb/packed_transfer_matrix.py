"""Explicit bounded input matrix for packed-field transfers, without verdicts."""

from kb import packed_transfer_evidence as contract

PATTERNS = (0x00000000, 0xFFFFFFFF, 0x80FF017F, 0x7F0080FF, 0x12345678, 0xA55AC33C)


def cases(declared, key):
    window = next(row for row in declared['window'] if row['key'] == key)
    transfers = [row for field in declared['field'] for row in field['transfer'] if row['window'] == key]
    width = max(row['physical_width_bytes'] for row in transfers)
    patterns = (*PATTERNS, *(1 << bit for bit in range(width * 8)))
    return tuple(dict(index=index, entry=window['start'], pattern=pattern & ((1 << (width * 8)) - 1),
                      variant=index % 6, sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8))
                 for index, pattern in enumerate(patterns))


def entry(window, case):
    registers = [(0x1728394A + register * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for register in range(15)]
    if window['natural_copy_callee_required']:
        call = window['copy_callee']
        registers[1], registers[2], registers[7] = call['destination'], call['source'], call['entry']
    return (*registers, 0x01003579, 0x13579BDF, 0x2468ACE0, case['sr'])


def memory(declared, key, case):
    ram = bytearray((0x5D + address * 19 + (address >> 8) + case['variant'] * 37) & 255
                    for address in range(contract.RAM_SIZE))
    for field in declared['field']:
        for transfer in field['transfer']:
            if transfer['window'] != key:
                continue
            width = transfer['physical_width_bytes']
            address = transfer['source'] & 65535
            ram[address:address + width] = case['pattern'].to_bytes(width, 'big')
    return bytes(ram)


def require_input(declared, window, case, observed):
    if observed['entry'] != case['entry'] or observed['context'] != entry(window, case):
        raise ValueError('the packed transfer observation changes its exact bounded entry case')
    if observed['memory_before'] != (memory(declared, window['key'], case),):
        raise ValueError('the packed transfer observation changes its exact input field, neighbors or RAM')
