"""Independent raw masked one-shot arithmetic and complete return state."""
MASK = 0xffffffff
ALIAS = 0x7d00
BASE = 0x01000000
SCALARS = ('argument','pointer','enable','opening','inhibit','history','started','diagnostic',
           'entry_sr','variant','expected_history','expected_started','last_increment','selected')

def signed(value, bits):
    return value if value < (1 << (bits - 1)) else value - (1 << bits)

def case(index, argument=1, enable=128, opening=192, inhibit=0, history=0,
         started=0, diagnostic=0, entry_sr=None, durations=None, counters=None):
    if durations is None:
        durations = [(0,1,20971,20972,32768,65535)[(i+index)%6] for i in range(6)]
    if counters is None:
        counters = [(0,1,32767,32768,65534,65535)[(i+index)%6] for i in range(6)]
    if entry_sr is None: entry_sr=(index&1)|((index&15)<<4)|((index&3)<<8)
    pointer = BASE + (0x224e if index&1 else 0x1568)
    incoming = [(0x17395b7d ^ i*0x1020304 ^ index*0x101) & MASK for i in range(15)]
    incoming[4],incoming[5]=argument,pointer
    expected=list(incoming)
    expected[0],expected[6]=signed(enable,8),BASE+0x4184
    selected=0
    last_increment=0
    output=list(counters)
    final_history,final_started=history,started
    if enable&128:
        expected[0],expected[2]=64,64
        mask=argument&255
        for i in range(6):
            bit=1<<i
            if not mask&bit: continue
            selected=1
            expected[3]=BASE+0x22dc
            duration=durations[i]
            if not mask&inhibit: expected[3]=BASE+0x128c
            if mask&(inhibit|final_history):
                duration=opening
                final_history|=mask
                expected[1]=BASE+0x128c
            if final_started&bit:
                expected[7]=opening
                duration=max(0,duration-opening)
            increment=min(65535,duration*800//256)
            if diagnostic&1: increment=1000
            output[i]=(output[i]+increment)&65535
            final_started|=bit
            expected[4]=increment
            expected[5]=entry_sr&240
            expected[6]=signed(final_started,16)
            last_increment=increment
    result=dict(zip(SCALARS,(argument,pointer,enable,opening,inhibit,history,started,diagnostic,
        entry_sr,index&1,final_history,final_started,last_increment,selected)))
    result.update(durations=durations,counters=counters,output=output,incoming=incoming,
                  expected=[value&MASK for value in expected])
    assert all(0<=value<=65535 for value in (*durations,*counters,opening,started))
    assert entry_sr&~0x3f1==0
    return result

def matrix():
    rows=[]
    def add(**keys): rows.append(case(len(rows),**keys))
    for i in range(12):
        add(argument=(0,1,2,3,32,63)[i%6]|(0x80420000 if i&1 else 0),
            enable=128 if i<10 else 0,inhibit=1 if i%3==0 else 0,
            history=2 if i%4==0 else 0,started=65535 if i&1 else 0,diagnostic=i&1)
    for mask in range(256):
        for variant in range(8):
            add(argument=mask|(0x89ab0000 if variant&4 else 0),
                enable=128 if variant&1 else 0,inhibit=(mask^0x55) if variant&2 else 0,
                history=0x80 if variant&4 else 0,started=0x8000|(mask^0x2a),diagnostic=variant>>2)
    for mask in range(64):
        for started in range(64):
            add(argument=mask,started=started|(0x8000 if mask&1 else 0),
                inhibit=(mask+3)&63 if started&1 else 0,
                history=(started^5)&63 if started&2 else 0)
    bounds=(0,1,2,191,192,193,20971,20972,32767,32768,65534,65535)
    for duration in bounds:
        for opening in bounds:
            for started in (0,63,0x8000,65535):
                add(argument=63,opening=opening,started=started,
                    durations=[duration]*6,counters=[65535,0,1,32767,32768,65534])
    for sr in range(128):
        entry=(sr&1)|((sr&30)<<3)|((sr&96)<<3)
        for variant in range(8):
            add(argument=63 if variant&1 else 0,enable=128 if variant&2 else 0,
                diagnostic=variant>>2,entry_sr=entry,started=0x8000|((sr*13)&63))
    for flag in range(256):
        add(argument=63,enable=flag,diagnostic=flag,inhibit=flag,history=flag^0x5a)
    assert len(rows)==8012
    assert {row['entry_sr'] for row in rows}=={t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
    return rows

def header(rows):
    literal=lambda value:f'0x{value&MASK:x}U'
    arrays=('durations','counters','output','incoming','expected')
    lines=['{'+','.join(literal(row[name]) for name in SCALARS)+','+
           ','.join('{'+','.join(map(literal,row[name]))+'}' for name in arrays)+'},' for row in rows]
    return '''/* Independent aggregate-mask, arithmetic, register and SR expectations. */
#ifndef ONESHOT_CASES_H
#define ONESHOT_CASES_H
#include <stdint.h>
struct oneshot_case {
    uint32_t '''+', '.join(SCALARS)+''';
    uint32_t durations[6],counters[6],output[6],incoming[15],expected[15];
};
static const struct oneshot_case oneshot_cases[]={
'''+'\n'.join(lines)+'''
};
#define ONESHOT_CASE_COUNT '''+str(len(rows))+'''U
#define ONESHOT_EARLY_COUNT 12U
#endif
'''
