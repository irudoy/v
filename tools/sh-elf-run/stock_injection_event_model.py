"""Compose independently checked selection with the raw event history transition."""
import stock_injection_selector_model as selector_model
import stock_injection_oneshot_model as oneshot_model

MASK=0xffffffff
SCALARS=('control_flag','event_flag','event_mode','enable','history','release','diagnostic',
         'timer_status','timer_control','started','entry_sr','variant','expected_event_flag',
         'expected_history','expected_release','last_increment','selected')
ARRAYS=(('counters',6),('counter_output',6),('event_bytes',8),('expected_event_bytes',8),('incoming',15))

def case(index, pending=63, event_flag=0, event_mode=0, enable=128, history=0,
         release=0, diagnostic=0, started=0, config=0, entry_sr=None, **selection):
    variant=index&1
    if entry_sr is None:entry_sr=(index&1)|((index&15)<<4)|((index&3)<<8)
    mode=3 if event_flag&128 else 4 if event_mode>3 else 2
    params=selector_model.case(argument=mode,pending=pending,config=config,variant=variant,
                               entry_t=entry_sr&1,**selection)
    after_history=history&(~pending&255)
    after_release=release
    if release and params['inhibit']:
        after_release=(release-1)&255
        after_history|=pending
    counters=[(0,1,32767,32768,65534,65535)[(i+index)%6] for i in range(6)]
    one=oneshot_model.case(1,argument=pending,enable=enable,opening=params['opening'],
        inhibit=params['inhibit'],history=after_history,started=started,diagnostic=diagnostic,
        entry_sr=entry_sr,durations=params['output'],counters=counters)
    event_bytes=[(index*29+i*47)&255 for i in range(8)]
    after=list(event_bytes)
    for i in range(3):after[i]|=pending
    if config&8:
        for i in (6,7):after[i]|=pending
    else:
        for i in (3,4,5):after[i]=min(255,event_bytes[i]+1)
    incoming=[(0x1728394a+i*0x1020305+index*0x111)&MASK for i in range(15)]
    row=dict(control_flag=(index*71)&255,event_flag=event_flag,event_mode=event_mode,
        enable=enable,history=history,release=release,diagnostic=diagnostic,
        timer_status=(0x8001^index*97)&65535,timer_control=(0xa55b^index*131)&65535,
        started=started,entry_sr=entry_sr,variant=variant,
        expected_event_flag=event_flag|(128 if mode==4 and not event_flag&128 else 0),
        expected_history=one['expected_history'],expected_release=after_release,
        last_increment=one['last_increment'],selected=one['selected'],
        counters=counters,counter_output=one['output'],event_bytes=event_bytes,
        expected_event_bytes=after,incoming=incoming,selection=params)
    assert entry_sr&~0x3f1==0
    return row

def matrix():
    rows=[]
    def add(**keys):rows.append(case(len(rows),**keys))
    for i in range(16):
        add(pending=(0,1,3,63)[i%4],event_flag=128 if i&4 else 0,
            event_mode=255 if i&8 else 0,config=8 if i&1 else 0,
            enable=0 if i in (2,7) else 128,history=255 if i&2 else 0,release=i,
            diagnostic=i&1,started=65535 if i&1 else 0)
    for pending in range(256):
        for variant in range(6):
            add(pending=pending,event_flag=128 if variant==0 else 0,
                event_mode=(0,3,4,127,128,255)[variant],config=8 if variant&1 else 0,
                history=pending^0x55,release=variant,
                inhibit=0 if variant&2 else pending^0x2a,enable=128 if variant&1 else 0,
                started=(pending*257)&65535,diagnostic=variant&1)
    for value in range(256):
        for flag in (0,128):
            for config in (0,8):
                add(event_mode=value,event_flag=flag,config=config,enable=128,
                    pending=63,release=value,history=value^0x55,inhibit=value,diagnostic=value)
    for pending in range(64):
        for started in range(64):
            add(pending=pending,started=started|(0x8000 if pending&1 else 0),
                history=started^0x2a,release=pending,inhibit=started^0x15,
                event_mode=4 if pending&1 else 0,config=8 if started&1 else 0)
    for bits in range(128):
        sr=(bits&1)|((bits&30)<<3)|((bits&96)<<3)
        for variant in range(4):
            add(entry_sr=sr,event_flag=128 if variant&1 else 0,event_mode=128,
                config=8 if variant&2 else 0,enable=128 if variant&1 else 0,
                pending=(bits*13)&255,started=65535,diagnostic=variant&1)
    for word in (0,1,20971,20972,32767,32768,65535):
        for opening in (0,1,192,32768,65535):
            for flag in (0,2):
                add(start=word,running=word,opening=opening,floor2=word,floor4=word,
                    snapshot=(word,)*6,flag_a=flag,threshold=65535,event_mode=4,
                    config=8,started=65535,clear=0,release=255)
    assert len(rows)==7254
    return rows

def header(rows):
    literal=lambda value:f'0x{value&MASK:x}U'
    nested=lambda row:'{'+','.join(literal(row[name]) for name in selector_model.SCALARS)+','+','.join(
        '{'+','.join(map(literal,row[name]))+'}' for name,_ in selector_model.ARRAYS)+'}'
    lines=['{'+','.join(literal(row[name]) for name in SCALARS)+','+','.join(
        '{'+','.join(map(literal,row[name]))+'}' for name,_ in ARRAYS)+','+nested(row['selection'])+'},' for row in rows]
    return '''/* Independent event transition, actual selector and one-shot expectations. */
#ifndef EVENT_ISR_CASES_H
#define EVENT_ISR_CASES_H
#include <stdint.h>
struct event_selector {
    uint32_t '''+', '.join(selector_model.SCALARS)+';\n'+''.join(
        f'    uint32_t {name}[{size}];\n' for name,size in selector_model.ARRAYS)+'''};
struct event_isr_case {
    uint32_t '''+', '.join(SCALARS)+';\n'+''.join(
        f'    uint32_t {name}[{size}];\n' for name,size in ARRAYS)+'''    struct event_selector selection;
};
static const struct event_isr_case event_isr_cases[]={
'''+'\n'.join(lines)+'''
};
#define EVENT_ISR_CASE_COUNT '''+str(len(rows))+'''U
#define EVENT_ISR_EARLY_COUNT 16U
#endif
'''
