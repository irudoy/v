"""Independent bounded vehicle-speed state, control, counter and CPU expectations."""
ENTRY = 0x4f19c
BASE = 0x01000000
MASK = 0xffffffff
ACTIVATION = 93
RELEASE = 91
DELAY = 0

def signed(value,bits=8):
    return value if value < 1 << (bits-1) else value-(1 << bits)

def case(index,speed=ACTIVATION,flags=0,control=0,counter=255,sr=None):
    assert all(type(value) is int and 0 <= value <= 255 for value in (speed,flags,control,counter))
    if sr is None:
        sr = (index&1)|((index&15)<<4)|((index&3)<<8)
    assert sr&~0x3f1 == 0
    incoming = [(0x197b3d5f^i*0x1020507^index*0x101)&MASK for i in range(15)]
    incoming[7] = ENTRY
    expected = list(incoming)
    expected[1] = expected[4] = signed(flags)
    expected[7] = signed(control)
    expected[5] = 0x8db7
    expected[6] = signed(speed)
    after,ctl,remaining = flags,control,counter
    active = flags&1
    gate = bool(control&32)
    if active:
        expected[2] = BASE+0x1094
        if gate:
            after &= 0xfe
        if speed < RELEASE:
            after &= 0xfe
            ctl &= 0x7f
            outcome = 'active-release-gate' if gate else 'active-release'
            t = 0
        else:
            outcome = 'active-rpm-gate' if gate else 'active-hold'
            t = 1
    else:
        expected[2] = ACTIVATION
        if speed < ACTIVATION:
            ctl &= 0x7f
            outcome,t = 'inactive-below',0
        else:
            if not control&128:
                remaining = DELAY
                ctl |= 128
                expected[6] = 0x8caf
                outcome = 'new-arm-gate' if gate else 'new-arm-activate'
            elif remaining:
                outcome = 'armed-counter-wait'
            else:
                outcome = 'armed-zero-gate' if gate else 'armed-zero-activate'
            if remaining:
                t = 0
            else:
                t = int(not gate)
                if not gate: after |= 1
    expected[0] = after&1
    return dict(speed=speed,flags=flags,control=control,counter=counter,sr=sr,
        expected_flags=after,expected_control=ctl,expected_counter=remaining,expected_t=t,
        expected_sr=(sr&~1)|t,result=after&1,outcome=outcome,incoming=incoming,
        expected=[value&MASK for value in expected])

def matrix():
    rows = []
    def add(**values): rows.append(case(len(rows),**values))
    edges = (0,90,91,92,93,94,127,128,255)
    for flags in range(256):
        for control in (0,32,128,160):
            for speed in edges:
                add(flags=flags,control=control,speed=speed,counter=255 if flags&8 else 0)
    for counter in range(256):
        for flags,control in ((0,0),(0,128),(0,160),(1,128)):
            add(flags=flags,control=control,counter=counter)
    seeds = ((0,90,255),(0,93,255),(0,93,0),(1,90,255),(1,91,0),(255,255,255))
    for control in range(256):
        for flags,speed,counter in seeds:
            add(flags=flags,control=control,speed=speed,counter=counter)
    for t in range(2):
        for imask in range(16):
            for mq in range(4):
                sr = t|(imask<<4)|(mq<<8)
                for flags,control,speed,counter in ((0,0,92,255),(0,0,93,255),
                    (0,128,93,255),(0,128,93,0),(1,0,90,255),(1,32,91,0)):
                    add(flags=flags,control=control,speed=speed,counter=counter,sr=sr)
    assert len(rows) == 12544
    assert {row['flags'] for row in rows} == set(range(256))
    assert {row['control'] for row in rows} == set(range(256))
    assert {row['counter'] for row in rows} == set(range(256))
    assert {row['sr'] for row in rows} == {t|(imask<<4)|(mq<<8) for t in range(2) for imask in range(16) for mq in range(4)}
    assert len({row['outcome'] for row in rows}) == 10
    first,seen = [],set()
    for index,row in enumerate(rows):
        if row['outcome'] not in seen:
            first.append(index)
            seen.add(row['outcome'])
    rows = [rows[index] for index in first]+[row for index,row in enumerate(rows) if index not in first]
    assert len({row['outcome'] for row in rows[:10]}) == 10
    return rows

def header(rows):
    scalars = ('speed','flags','control','counter','sr','expected_flags','expected_control',
        'expected_counter','expected_t','expected_sr','result','gbr','mach','macl')
    words = (0,0xffffffff,0x80000000,0x7fffffff,0x16347258,0xafbecddc)
    literal = lambda value:f'0x{value&MASK:x}U'
    records = []
    for index,original in enumerate(rows):
        row = dict(original,gbr=words[index%6],mach=words[(index+2)%6],macl=words[(index+4)%6])
        records.append('{'+','.join(literal(row[name]) for name in scalars)+','+
            ','.join('{'+','.join(map(literal,row[name]))+'}' for name in ('incoming','expected'))+'},')
    return '\n'.join([
        '/* Independent bounded vehicle state, control, counter and complete CPU expectations. */',
        '#ifndef VEHICLE_FUEL_CUT_CASES_H',
        '#define VEHICLE_FUEL_CUT_CASES_H',
        '#include <stdint.h>',
        'struct vehicle_fuel_cut_case {',
        '    uint32_t '+', '.join(scalars)+';',
        '    uint32_t incoming[15],expected[15];',
        '};',
        'static const struct vehicle_fuel_cut_case vehicle_fuel_cut_cases[]={',
        *records,
        '};',
        f'#define VEHICLE_FUEL_CUT_CASE_COUNT {len(rows)}U',
        f'#define VEHICLE_FUEL_CUT_EARLY_COUNT {len({row["outcome"] for row in rows})}U',
        '#endif','',
    ])

