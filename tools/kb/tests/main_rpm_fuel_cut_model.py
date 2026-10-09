"""Independent bounded stock main-RPM state and complete GPR/SR expectations."""
ENTRY = 0x4f282
BASE = 0x01000000
MASK = 0xffffffff
THRESHOLDS = ((612, 596), (596, 368))
CONFIG = 0x63
DELAY = 0

def signed(value, bits):
    return value if value < 1 << (bits - 1) else value - (1 << bits)

def case(index, speed=612, selector=0, flags=0, counter=255, sr=None):
    assert 0 <= speed <= 65535
    assert all(0 <= value <= 255 for value in (selector, flags, counter))
    if sr is None:
        sr = (index & 1) | ((index & 15) << 4) | ((index & 3) << 8)
    assert sr & ~0x3f1 == 0
    pair = (selector >> 4) & 1
    on, release = THRESHOLDS[pair]
    incoming = [(0x17395b7d ^ i * 0x1020304 ^ index * 0x101) & MASK for i in range(15)]
    incoming[7] = ENTRY
    expected = list(incoming)
    expected[1] = signed(flags, 8)
    expected[4], expected[5] = BASE + 0x119c, on
    after, remaining = flags, counter
    if flags & 4:
        expected[2], expected[6] = speed, release
        if speed < release:
            after = flags & 0xf9
            outcome = 'active-release'
        else:
            outcome = 'active-hold'
    else:
        expected[2], expected[6] = signed(speed, 16), speed
        if speed < on:
            after = flags & 0xfd
            outcome = 'inactive-below'
        else:
            if not flags & 2:
                remaining = DELAY
                after = flags | 2
                expected[6] = 0x8c69
                outcome = 'load-stock-delay'
            else:
                outcome = 'armed-wait' if counter else 'armed-activate'
            if remaining == 0:
                after |= 4
    result = (after >> 2) & 1
    expected[0] = result
    return dict(speed=speed, selector=selector, flags=flags, counter=counter, sr=sr,
        expected_flags=after, expected_counter=remaining, expected_t=1-result,
        expected_sr=(sr & ~1) | (1-result), result=result, pair=pair, on=on,
        release=release, outcome=outcome, incoming=incoming,
        expected=[value & MASK for value in expected], variant=index & 7)

def matrix():
    rows = []
    def add(**values):
        rows.append(case(len(rows), **values))
    for pair in range(2):
        on, release = THRESHOLDS[pair]
        edges = (0, release-1, release, on-1, on, on+1, 32768, 65535)
        for flags in range(256):
            for speed in edges:
                add(speed=speed, selector=(0xef | 0x10 * pair), flags=flags,
                    counter=255 if flags & 8 else 0)
    for selector in range(256):
        on, release = THRESHOLDS[(selector >> 4) & 1]
        for flags, speed, counter in ((0,on,255),(2,on,1),(4,release-1,255),(0xff,release,0)):
            add(selector=selector, flags=flags, speed=speed, counter=counter)
    for counter in range(256):
        for flags in (0,2):
            add(flags=flags, counter=counter, speed=612)
    for t in range(2):
        for imask in range(16):
            for mq in range(4):
                sr = t | imask << 4 | mq << 8
                for flags, speed, counter in ((0,611,255),(0,612,255),(2,612,255),(2,612,0),(4,595,255),(4,596,0)):
                    add(sr=sr, flags=flags, speed=speed, counter=counter)
    assert len(rows) == 6400
    assert {row['sr'] for row in rows} == {t | i << 4 | mq << 8 for t in range(2) for i in range(16) for mq in range(4)}
    assert {row['outcome'] for row in rows} == {'active-release','active-hold','inactive-below','load-stock-delay','armed-wait','armed-activate'}
    assert {row['flags'] for row in rows} == set(range(256))
    assert {row['selector'] for row in rows} == set(range(256))
    assert {row['counter'] for row in rows} == set(range(256))
    first = []
    seen = set()
    for index, row in enumerate(rows):
        if row['outcome'] not in seen:
            first.append(index)
            seen.add(row['outcome'])
    rows = [rows[index] for index in first] + [row for index,row in enumerate(rows) if index not in first]
    assert len(rows) == 6400 and len(first) == 6
    assert len({row['outcome'] for row in rows[:6]}) == 6
    return rows

def header(rows):
    scalars = ('speed','selector','flags','counter','sr','expected_flags','expected_counter',
        'expected_t','expected_sr','result','pair','on','release','variant','gbr','mach','macl')
    words = (0,0xffffffff,0x80000000,0x7fffffff,0x12345678,0xaabbccdd)
    literal = lambda value:f'0x{value&0xffffffff:x}U'
    records = []
    for index,original in enumerate(rows):
        row = dict(original,gbr=words[index%6],mach=words[(index+2)%6],macl=words[(index+4)%6])
        records.append('{'+','.join(literal(row[name]) for name in scalars)+','+
            ','.join('{'+','.join(map(literal,row[name]))+'}' for name in ('incoming','expected'))+'},')
    return '\n'.join([
        '/* Independent bounded state, register, full SR and counter expectations. */',
        '#ifndef MAIN_RPM_FUEL_CUT_CASES_H',
        '#define MAIN_RPM_FUEL_CUT_CASES_H',
        '#include <stdint.h>',
        'struct main_rpm_case {',
        '    uint32_t '+', '.join(scalars)+';',
        '    uint32_t incoming[15],expected[15];',
        '};',
        'static const struct main_rpm_case main_rpm_cases[]={',
        *records,
        '};',
        f'#define MAIN_RPM_CASE_COUNT {len(rows)}U',
        f'#define MAIN_RPM_EARLY_COUNT {len({row["outcome"] for row in rows})}U',
        '#endif',
        '',
    ])
