"""Compose the unsigned entry arithmetic with raw compare/control updates."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('held_programmer_arithmetic', HERE / 'stock_injection_programmer_model.py')
held = importlib.util.module_from_spec(spec)
spec.loader.exec_module(held)
MASK = 0xffffffff
SCALARS = ('argument','mode','position','flag','period','variant','entry_t','count','remainder',
           'product','quotient','scratch','expected_t','normal','timer','capture','compare',
           'status','control','entry_sr','expected_compare','expected_status','expected_control')

def convert(original, index, **changes):
    row = dict(zip(SCALARS[:14], original[:14]))
    row.update(timer=(0x3f00 + index * 127) & 65535,
        capture=(0xe100 + index * 257) & 65535, compare=0xa7b8,
        status=(0x8001 ^ index * 257) & 65535, control=(0x7e00 ^ index * 131) & 65535,
        entry_sr=row['entry_t'] | (((index >> 1) & 15) << 4) | ((index & 3) << 8))
    row.update(changes)
    assert all(0 <= row[name] <= 65535 for name in ('timer','capture','compare','status','control'))
    assert row['entry_sr'] & ~0x3f1 == 0
    row['entry_t'] = row['entry_sr'] & 1
    incoming, registers = list(original[14]), list(original[15])
    if row['count'] == 0:
        late = int(((row['timer'] - row['capture']) & 65535) + 2 > row['quotient'])
        row['expected_t'] = late
        row['expected_compare'] = ((row['timer'] + 2) if late else
                                   row['capture'] + row['quotient']) & 65535
        row['expected_status'], row['expected_control'] = row['status'] & 65534, row['control'] | 1
        registers[0] = (row['entry_sr'] & ~0xf1) | 0x80 | late
        registers[2] = (row['control'] if row['control'] < 32768 else row['control'] - 65536) | 1
        registers[4], registers[5], registers[6], registers[7] = 0x7e00, MASK - 1, 0xffffff0f, row['quotient']
        for register in (11,13,14): registers[register] = incoming[register]
    else:
        row['expected_compare'], row['expected_status'], row['expected_control'] = row['compare'], row['status'], row['control']
    row['incoming'], row['expected'] = incoming, [value & MASK for value in registers]
    return row

def extra(index, argument=9, period=65535, entry_sr=0, **changes):
    values = []
    held.append(values, argument, 64, index & 255, index & 255, period, index & 1, entry_sr & 1)
    assert values[0][7] == 0
    return convert(values[0], index, entry_sr=entry_sr, **changes)

def matrix():
    original = held.matrix()
    assert len(original) == 16028
    rows = [convert(row, index) for index, row in enumerate(original)]
    for index in range(12):
        period = (0,1,8192,25000,32768,65535)[index % 6]
        provisional = extra(index, period=period)
        q = provisional['quotient']
        delta = max(0, q - (3 if index % 3 == 0 else 2 if index % 3 == 1 else 1))
        timer = (0xffff if index & 1 else 0x8000)
        rows.append(extra(index, period=period, timer=timer, capture=(timer-delta)&65535,
            status=(0xffff if index & 1 else 0), control=(0x8000 if index & 2 else 1),
            entry_sr=((index & 15)<<4)|((index & 3)<<8)|(index & 1)))
    bounds = (0,1,2,32767,32768,65533,65534,65535)
    for timer in bounds:
        for capture in bounds:
            for argument in (0,1,9,10,119):
                for period in (0,1,32767,32768,65535):
                    index = len(rows)
                    rows.append(extra(index, argument, period, timer=timer, capture=capture,
                        entry_sr=((index & 15)<<4)|((index & 3)<<8)|(index & 1)))
    for argument in (1,9,10,119):
        for period in (1,8192,25000,65535):
            q = extra(0,argument,period)['quotient']
            if q < 3: continue
            for timer in bounds:
                for delta in (q-3,q-2,q-1):
                    index = len(rows)
                    rows.append(extra(index,argument,period,timer=timer,capture=(timer-delta)&65535))
    for byte in range(256):
        for high in (0,128):
            index=len(rows)
            rows.append(extra(index,status=(high<<8)|byte,control=(byte<<8)|high,
                entry_sr=((byte&15)<<4)|((byte&3)<<8)|(byte&1)))
    for bits in range(128):
        entry_sr=(bits&1)|((bits&30)<<3)|((bits&96)<<3)
        for argument in (9,120):
            values=[]
            held.append(values,argument,64,bits,bits,65535,bits&1,bits&1)
            rows.append(convert(values[0],len(rows),entry_sr=entry_sr))
    assert {row['entry_sr'] for row in rows} == {t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
    assert len(rows) > 18000
    return rows

def header(rows):
    literal=lambda value:f'0x{value&MASK:x}U'
    lines=['{'+','.join(literal(row[name]) for name in SCALARS)+','+
           ','.join('{'+','.join(map(literal,row[name]))+'}' for name in ('incoming','expected'))+'},'
           for row in rows]
    return '''/* Independent full entry, compare and complete-SR expectations. */
#ifndef FULL_PROGRAMMER_CASES_H
#define FULL_PROGRAMMER_CASES_H
#include <stdint.h>
struct full_programmer_case {
    uint32_t '''+', '.join(SCALARS)+''';
    uint32_t incoming[15],expected[15];
};
static const struct full_programmer_case full_programmer_cases[]={
'''+'\n'.join(lines)+'''
};
static const uint32_t full_programmer_early_indices[]={
    0,1,2,3,4,5,6,7,8,9,10,11,16028,16029,16030,16031,16032,16033,16034,16035,16036,16037,16038,16039
};
#define FULL_PROGRAMMER_CASE_COUNT '''+str(len(rows))+'''U
#define FULL_PROGRAMMER_EARLY_COUNT 24U
#endif
'''
