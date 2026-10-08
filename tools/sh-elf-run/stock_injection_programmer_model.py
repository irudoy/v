"""Independent scalar expectations for complete entry-to-decision composition."""
MASK = (1 << 32) - 1
ENTRY = 0x2b64a
BASE = 0x0100128c
COUNT = 0x010013b8
REMAINDER = 0x0100193b
BOUNDARY_RETURN = 0xfedcba98


def normalized(count, remainder, phase):
    old = count
    signed_remainder = remainder if remainder < 128 else remainder - 256
    def changed(value, amount):
        return value, (remainder + amount) & 255, (signed_remainder + amount) & MASK
    if phase == 4:
        scratch = 6 if count < 6 else 15
        if 6 <= count <= 15:
            return count - 2, remainder, 4, count - 2, scratch, 0
        if count == 5:
            c, r, r2 = changed(3, 20)
            return c, r, 5, r2, scratch, 1
        if count == 4:
            c, r, r2 = changed(3, 10)
            return c, r, 4, r2, scratch, 1
        return count, remainder, count, count, scratch, 0
    if phase == 9:
        if count == 9:
            count, remainder = 8, (remainder + 10) & 255
        if count >= 10:
            c, r, r2 = changed(count - 2, 20)
            return c, r, old, r2, 10, 1
        return count, remainder, old, count, 10, 0
    if 15 <= count <= 24:
        return count - 4, remainder, phase, count - 4, 24, 0
    if count == 14:
        c, r, r2 = changed(10, 20)
        return c, r, 14, r2, 15, 1
    if count == 13:
        c, r, r2 = changed(10, 10)
        return c, r, 13, r2, 15, 1
    if 3 <= count <= 12:
        return count - 2, remainder, count, count - 2, 12, 0
    if count == 2:
        c, r, r2 = changed(0, 20)
        return c, r, 2, r2, 3, 1
    if count == 1:
        c, r, r2 = changed(0, 10)
        return c, r, 1, r2, 3, 1
    assert count == 0 or count > 24
    return count, remainder, count, count, 3 if count == 0 else 12, 0


def append(rows, argument, mode, position, flag, period, variant, entry_t):
    assert 0 <= argument <= MASK and all(0 <= x <= 255 for x in (mode, position, flag))
    assert 0 <= period <= 65535 and variant in (0, 1) and entry_t in (0, 1)
    incoming = [((0x81234567+i*0x1020305) if variant else
                 (0x1728394a+i*0x110203)) & MASK for i in range(15)]
    incoming[4], incoming[7] = argument, ENTRY
    expected = incoming.copy()
    angle = argument & 255
    normal = not mode & 64
    if normal:
        split_count = angle // 10
        prior_count = max(0, split_count - 1)
        prior_remainder = angle % 10 + (10 if split_count else 0)
        count, remainder, _, r2, r5, _ = normalized(prior_count, prior_remainder, position)
        expected[2], expected[3], expected[4], expected[5] = r2, 0x28dc8, COUNT, r5
        expected[6], expected[7], expected[14] = prior_count, REMAINDER, REMAINDER
        if split_count:
            expected[13] = BASE
    else:
        count = int(angle >= 120)
        remainder = angle - 120 if count else angle
        expected[2], expected[4], expected[6], expected[13] = remainder, angle, remainder if count else 120, BASE
    expected[0] = count
    product = period * remainder
    quotient = ((product * 6554) & MASK) // 65536
    residue = (product - 10 * quotient) & MASK
    if count:
        expected[13], expected[14] = incoming[13], incoming[14]
        expected_t = 0
    else:
        expected[0], expected[2], expected[3] = 0x6af, quotient, 0x199a
        expected[4], expected[5], expected[6] = residue, 0x010016c2, 10 * quotient
        expected[7], expected[11], expected[13] = 0x0100166c, BOUNDARY_RETURN, BASE
        expected_t = int(quotient == 0)
    rows.append((argument, mode, position, flag, period, variant, entry_t,
                 count, remainder, product, quotient, residue & 255, expected_t,
                 int(normal), incoming, expected))


def matrix():
    rows = []
    early = ((0,0,0,0,0),(20,0,0,1,65535),(50,0,4,127,8192),
             (100,0,9,128,65535),(255,0,0,255,65535),(119,64,4,128,65535),
             (120,64,9,127,65535),(255,64,0,1,8192),(0xffffffff,0,0,255,1),
             (0x8000001f,0,0,0,65535),(0xffffff77,64,0,128,25000),(0x80000078,64,9,255,65535))
    for i, values in enumerate(early):
        append(rows, *values, i & 1, (i >> 1) & 1)
    for mode in (0, 64):
        for position in (0, 4, 9):
            for argument in range(256):
                for variant in range(2):
                    for t in range(2):
                        append(rows, argument, mode, position, argument,
                               (argument * 257) & 65535, variant, t)
    for position in range(256):
        for argument in (0,10,20,30,40,50,60,90,100,130,140,150,160,250):
            append(rows, argument, 0, position, position, 65535, position & 1, argument & 1)
    for mode in range(256):
        for argument in (0, 119, 120, 255):
            append(rows, argument, mode, mode, mode, 8192, mode & 1, argument & 1)
    for high in range(256):
        for low in (0, 1, 128, 255):
            for argument in (0, 9, 20, 29, 119):
                append(rows, argument, 64, high, low, high * 256 + low, low & 1, high & 1)
    for upper in (0x100, 0x7fffff00, 0xffff0000):
        for argument in (0, 19, 20, 39, 40, 119, 120, 255):
            for mode in (0, 64):
                for position in (0, 4, 9):
                    append(rows, upper | argument, mode, position, argument, 65535, argument & 1, upper & 1)
    assert len(rows) == 16028
    return rows


def header(rows):
    scalar = lambda value: f'0x{value:x}U'
    lines = ['{' + ','.join(map(scalar, row[:14])) + ',' +
             ','.join('{' + ','.join(map(scalar, values)) + '}' for values in row[14:]) + '},'
             for row in rows]
    return '''#ifndef VQ_INJECTION_PROGRAMMER_CASES_H
#define VQ_INJECTION_PROGRAMMER_CASES_H
#include <stdint.h>
struct programmer_case {
    uint32_t argument,mode,position,flag,period,variant,entry_t,count,remainder,product,quotient,scratch,expected_t,normal;
    uint32_t incoming[15],expected[15];
};
''' + f'#define PROGRAMMER_CASE_COUNT {len(rows)}U\n' + \
        'static const struct programmer_case programmer_cases[] = {\n' + '\n'.join(lines) + '\n};\n#endif\n'
