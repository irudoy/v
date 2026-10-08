"""Independent word selection and per-channel correction state transitions."""
MASK = 0xffffffff
ENTRY = 0x54d3e
RAM = 0x01000000
SCALARS = ('argument', 'flag_a', 'flag_b', 'config', 'opening', 'stopped', 'start',
           'threshold', 'floor1', 'floor2', 'floor4', 'running', 'calibration',
           'pending', 'clear', 'inhibit', 'tail_factor', 'variant', 'entry_t',
           'local_written', 'local_value', 'child_r14', 'child_macl', 'child_r2')
ARRAYS = (('snapshot', 6), ('correction', 6), ('secondary', 6), ('copy_source', 6),
          ('output', 6), ('expected_correction', 6), ('expected_secondary', 6),
          ('incoming', 15), ('expected', 15))

def signed_word(value):
    return value if value < 32768 else value - 65536

def signed_byte(value):
    return value if value < 128 else value - 256

def case(**changes):
    row = dict(argument=3, flag_a=0, flag_b=0, config=0x7a,
        opening=32768, stopped=17, start=41000, threshold=42000,
        floor1=31, floor2=32768, floor4=65535, running=32768, calibration=170,
        pending=0x3f, clear=0, inhibit=0x15, tail_factor=128, variant=0, entry_t=0,
        snapshot=(0, 1, 32767, 32768, 65534, 65535),
        correction=(9, 10, 11, 12, 13, 14),
        secondary=(0, 1, 32767, 32768, 65534, 65535),
        copy_source=(65535, 65534, 32768, 32767, 1, 0))
    row.update(changes)
    assert 0 <= row['argument'] <= MASK
    assert all(0 <= row[name] <= 255 for name in
        ('flag_a', 'flag_b', 'config', 'pending', 'clear', 'inhibit', 'tail_factor'))
    assert all(0 <= row[name] <= 65535 for name in
        ('opening', 'stopped', 'start', 'threshold', 'floor1', 'floor2', 'floor4', 'running', 'calibration'))
    assert all(len(row[name]) == 6 and all(0 <= value <= 65535 for value in row[name])
               for name in ('snapshot', 'correction', 'secondary', 'copy_source'))
    assert row['variant'] in (0, 1) and row['entry_t'] in (0, 1)
    incoming = [((0x81234567 + index * 0x1020305) if row['variant'] else
                 (0x1728394a + index * 0x110203)) & MASK for index in range(15)]
    incoming[4], incoming[7] = row['argument'], ENTRY
    registers = incoming.copy()
    mode = row['argument'] & 255
    registers[4] = mode
    override = bool(row['flag_a'] & 2 or row['flag_b'] & 64)
    running = not override and mode not in (0, 1, 2, 4)
    row['local_written'], row['local_value'] = int(running), row['running']
    macl = 0x9274b6d8 if row['variant'] else 0x2468ace0
    primary_r14 = incoming[14]
    if override or mode == 0:
        value = row['opening'] if override else row['stopped']
        output = [value] * 6
        registers[2], registers[5], registers[6] = RAM + 0x225a, signed_word(value), 0
    elif mode in (1, 2, 4):
        macl = row['calibration'] * 100
        cap = min(65535, row['opening'] + macl // 256)
        value = max(0, row['start'] - (row['stopped'] if row['threshold'] > cap else 0))
        value = max(value, row[{1: 'floor1', 2: 'floor2', 4: 'floor4'}[mode]])
        output = [value] * 6
        registers[2], registers[4], registers[5], registers[6] = RAM + 0x225a, 0x25a, value, 0
    else:
        output = [max(value, row['running']) for value in row['snapshot']]
        primary_r14 = row['running']
        registers[2] = (row['snapshot'][-1] if row['snapshot'][-1] >= row['running']
                        else signed_word(row['running']))
        registers[4], registers[5], registers[6], registers[7] = RAM + 0x2354, RAM + 0x225a, RAM + 0x2470, 0
    registers[0], registers[6] = signed_byte(row['config']), 0x8d92
    correction, secondary = list(row['correction']), list(row['secondary'])
    row['child_r14'], row['child_macl'], row['child_r2'] = primary_r14, macl, 0
    if row['config'] & 8:
        registers[0], registers[2] = 0x12, RAM + 0x120e
        for channel in range(6):
            row['child_r2'] = registers[2]
            bit = 1 << channel
            registers[0], registers[1], registers[2] = bit, 0x221f4 - 2 * channel, bit
            if row['pending'] & bit:
                correction[channel] = 0
                registers[0], registers[4] = 2 * channel, 2 * channel
                registers[5], registers[6] = 0, RAM + 0x1466
                if not row['clear'] & bit:
                    registers[0], registers[3], registers[5] = signed_byte(row['inhibit']), RAM + 0x22dc, RAM + 0x128c
                    registers[0], registers[7] = 2 * channel, 0x6d2
                    registers[5] = RAM + 0x195e
                    if row['inhibit'] & bit:
                        secondary[channel] = row['secondary'][channel] * row['tail_factor'] // 256
                        registers[1], registers[2], registers[3], registers[6] = row['tail_factor'], secondary[channel], 0x85f7, 0
                    else:
                        secondary[channel] = row['copy_source'][channel]
                        registers[2], registers[6] = RAM + 0x2398, signed_word(row['copy_source'][channel])
    row['output'], row['expected_correction'], row['expected_secondary'] = output, correction, secondary
    row['incoming'], row['expected'] = incoming, [value & MASK for value in registers]
    return row

def matrix():
    rows = []
    early = (dict(config=0, argument=0), dict(config=0, argument=1),
        dict(config=0, argument=2), dict(config=0, argument=4),
        dict(config=0, argument=3), dict(config=0, argument=0x812300ff, flag_a=2),
        dict(config=0, argument=0x12345678, flag_b=64),
        dict(pending=0), dict(pending=63, clear=63), dict(pending=63, inhibit=0),
        dict(pending=63, inhibit=63, tail_factor=255), dict(argument=4, threshold=65535, start=0))
    for index, values in enumerate(early):
        rows.append(case(**values, variant=index & 1, entry_t=(index >> 1) & 1))
    for mode in range(256):
        for flag_a, flag_b in ((0, 0), (2, 0), (0, 64), (2, 64)):
            for entry_t in range(2):
                rows.append(case(argument=(0x81234500 if entry_t else 0x12345600) | mode,
                    flag_a=flag_a, flag_b=flag_b, config=0 if entry_t else 0x7a,
                    variant=mode & 1, entry_t=entry_t))
    bounds = (0, 1, 32767, 32768, 65535)
    for mode in (1, 2, 4):
        for base in bounds:
            for subtract in bounds:
                for floor in bounds:
                    rows.append(case(argument=mode, start=base, stopped=subtract,
                        threshold=65535, floor1=floor, floor2=floor, floor4=floor,
                        config=0, variant=base & 1, entry_t=subtract & 1))
    for opening in bounds:
        for calibration in (0, 1, 169, 170, 171, 32768, 65535):
            limit = min(65535, opening + calibration * 100 // 256)
            for threshold in sorted({0, max(0, limit - 1), limit, min(65535, limit + 1), 65535}):
                for mode in (1, 2, 4):
                    rows.append(case(argument=mode, opening=opening, calibration=calibration,
                        threshold=threshold, config=0, floor1=0, floor2=0, floor4=0))
    for flag in range(256):
        for mode in (0, 1, 2, 3, 4, 255):
            rows.append(case(argument=mode, flag_a=flag, flag_b=flag, config=flag,
                pending=flag ^ 0x55, clear=flag ^ 0xaa, inhibit=flag, variant=flag & 1, entry_t=mode & 1))
    for pending in range(256):
        for clear in (0, 255):
            for inhibit in (0, 255):
                rows.append(case(pending=pending, clear=clear, inhibit=inhibit,
                    variant=pending & 1, entry_t=clear & 1))
    for clear in range(256):
        for inhibit in (0, 255):
            rows.append(case(pending=255, clear=clear, inhibit=inhibit, variant=clear & 1))
    for inhibit in range(256):
        for factor in (0, 128, 255):
            rows.append(case(pending=255, clear=0, inhibit=inhibit, tail_factor=factor,
                             entry_t=inhibit & 1))
    for factor in range(256):
        for inhibit in (0, 255):
            rows.append(case(pending=255, clear=0, inhibit=inhibit, tail_factor=factor,
                             variant=factor & 1))
    for value in bounds:
        for floor in bounds:
            words = tuple((value + offset) & 65535 for offset in (0, 1, 32767, 32768, 65534, 65535))
            for config in (0, 0x7a):
                rows.append(case(snapshot=words, running=floor, secondary=words,
                                 copy_source=words[::-1], correction=words, config=config))
    return rows

def header(rows):
    literal = lambda value: f'0x{value & MASK:x}U'
    lines = []
    for row in rows:
        lines.append('{' + ','.join(literal(row[name]) for name in SCALARS) + ',' +
                     ','.join('{' + ','.join(map(literal, row[name])) + '}' for name, _ in ARRAYS) + '},')
    return '''/* Independent full state for pulse selection and channel correction. */
#ifndef PULSE_SELECTOR_CASES_H
#define PULSE_SELECTOR_CASES_H
#include <stdint.h>
struct pulse_selector_case {
''' + '    uint32_t ' + ', '.join(SCALARS) + ';\n' + ''.join(
        f'    uint32_t {name}[{size}];\n' for name, size in ARRAYS) + '''};
static const struct pulse_selector_case pulse_selector_cases[] = {
''' + '\n'.join(lines) + '''
};
#define PULSE_SELECTOR_CASE_COUNT ''' + str(len(rows)) + '''U
#endif
'''
