"""Independent signed arithmetic and complete natural-return expectations."""
MASK = (1 << 32) - 1
ENTRY = 0x56fc0

def append(rows, battery, slope, additive, variant=0, entry_t=0):
    assert all(type(value) is int and 0 <= value <= 255
               for value in (battery, slope, additive))
    assert variant in (0, 1) and entry_t in (0, 1)
    incoming = [((0x81234567 + index * 0x1020305) if variant else
                 (0x1728394a + index * 0x110203)) & MASK for index in range(15)]
    incoming[7] = ENTRY
    product = (175 - battery) * slope
    shifted = product // 128
    value = min(65535, max(0, shifted + additive))
    assert shifted + additive <= 603
    expected = incoming.copy()
    expected[0], expected[2] = 0x7a, 0x010023bc
    expected[5], expected[6] = 0x8c9e, value
    # The final CMP/GT tests the bounded word against 65535.
    expected_t = 0
    rows.append((battery, slope, additive, variant, entry_t,
                 product & MASK, shifted & MASK, value, expected_t, incoming, expected))

def matrix():
    rows = []
    early = ((0, 92, 70), (175, 92, 70), (255, 92, 70),
             (255, 255, 0), (174, 255, 0), (176, 255, 0),
             (0, 255, 255), (175, 0, 255), (255, 0, 0),
             (176, 1, 1), (176, 127, 1), (176, 128, 1))
    for index, values in enumerate(early):
        append(rows, *values, index & 1, (index >> 1) & 1)
    for battery in range(256):
        for variant in range(2):
            for entry_t in range(2):
                append(rows, battery, 92, 70, variant, entry_t)
    for battery in range(256):
        for slope in (0, 1, 127, 128, 255):
            for additive in (0, 1, 127, 128, 255):
                append(rows, battery, slope, additive, battery & 1, slope & 1)
    for slope in range(256):
        for battery in (0, 174, 175, 176, 255):
            for additive in (0, 255):
                append(rows, battery, slope, additive, slope & 1, additive & 1)
    for additive in range(256):
        for battery in (0, 174, 175, 176, 255):
            for slope in (0, 255):
                append(rows, battery, slope, additive, additive & 1, battery & 1)
    assert len(rows) == 12556
    return rows

def header(rows):
    literal = lambda value: f'0x{value:x}U'
    lines = ['{' + ','.join(map(literal, row[:9])) + ',' +
             ','.join('{' + ','.join(map(literal, registers)) + '}' for registers in row[9:]) + '},'
             for row in rows]
    return '''/* Independent full state for the stock battery-dependent opening word. */
#ifndef OPENING_WORD_CASES_H
#define OPENING_WORD_CASES_H
#include <stdint.h>
struct opening_word_case {
    uint32_t battery, slope, additive, variant, entry_t;
    uint32_t product, shifted, value, expected_t;
    uint32_t incoming[15], expected[15];
};
static const struct opening_word_case opening_word_cases[] = {
''' + '\n'.join(lines) + '''
};
#define OPENING_WORD_CASE_COUNT ''' + str(len(rows)) + '''U
#endif
'''
