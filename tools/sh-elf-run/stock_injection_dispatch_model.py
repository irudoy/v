"""Independent complete dispatch, catch-up and actual callee composition."""
import importlib.util
from pathlib import Path
import stock_injection_selector_model as selector_model
import stock_injection_oneshot_model as oneshot_model

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('held_full_programmer',HERE/'stock_injection_full_programmer_model.py')
programmer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(programmer)
MASK=0xffffffff
RAM=0x01000000
CONTROL_ALIAS=0x7f00
EVENT_ALIAS=0x7b00
TIMER_ALIAS=0x7e00
PULSE_ALIAS=0x7d00
ENTRY=0x54a44
BYTE_RAM=(('ticks',0x4555),('cylinder',0x11de),('cylinder_history',0x1526),
          ('lead_source',0x2364),('event_source',0x24c9),('event_mode',0x2298),
          ('slot',0x20b4),('queue',0x20b5),('mask_a',0x157e),('mask_b',0x16fe),
          ('history',0x1935),('mask_c',0x14c3),('mask_d',0x14c2),
          ('pending',0x2228),('old_lead',0x221d),('cursor',0x221e),
          ('angle',0x2333),('diagnostic',0x4251),('mode',0x24c9),('position',0x13b2),
          ('enable',0x4184),('scratch',0x166c),('remainder',0x193b))
WORD_RAM=(('period',0x22bc),('capture',0x158a),('count',0x13b8),('offset',0x16c2))
SCALARS=('entry_sr','variant','control_flag','event_flag','event_aux','timer','compare','timer_status',
         'timer_control','started','path','expected_sr','r0_full_sr','expected_control_flag',
         'expected_event_flag','expected_event_aux','expected_compare','expected_timer_status',
         'expected_timer_control','expected_started','selector_calls','oneshot_calls','programmer_calls')

def signed(value,bits):
    return value if value<(1<<(bits-1)) else value-(1<<bits)

class State:
    def __init__(self,incoming,sr,macl,gbr):
        self.r=incoming.copy();self.sr=sr;self.macl=macl;self.gbr=gbr;self.frame={}
    def put(self,at,size,value):
        assert 0<=at<=192-size
        for i,byte in enumerate((value&((1<<(8*size))-1)).to_bytes(size,'big')):self.frame[at+i]=byte
    def t(self,value):self.sr=(self.sr&~1)|int(bool(value))
    def merge(self,row):
        for i,(before,after) in enumerate(zip(row['incoming'],row['expected'])):
            if before!=after:self.r[i]=after

def case(index,table,event_flag=0xe0,event_aux=0,control_flag=0,event_source=0,
         cylinder=2,lead_source=3,old_lead=3,cursor=0,angle=20,event_mode=0,
         enable=128,history=0,started=0,diagnostic=0,mode=0,position=0,period=65535,
         config=0,entry_sr=None,**selection):
    assert len(table)==269
    if entry_sr is None:entry_sr=(index&1)|((index&30)<<3)|((index&96)<<3)
    initial_control_flag,initial_started=control_flag,started
    event_source|=mode
    mode=event_source
    incoming=[(0x17395b7d^i*0x1020304^index*0x101)&MASK for i in range(15)]
    macl=0x9274b6d8 if index&1 else 0x2468ace0
    gbr=0x01004567 if index&1 else 0x01003579
    state=State(incoming,entry_sr,macl,gbr);r=state.r
    memory={name:0 for name,_ in (*BYTE_RAM,*WORD_RAM)}
    memory.update(ticks=index&255,cylinder=cylinder,cylinder_history=(index*17)&255,
        lead_source=lead_source,event_source=event_source,event_mode=event_mode,
        queue=(index*19)&255,mask_a=(index*23)&255,mask_b=(index*31)&255,
        mask_c=(index*41)&255,mask_d=(index*47)&255,history=history,
        pending=(index*37)&255,old_lead=old_lead,cursor=cursor,angle=angle,
        diagnostic=diagnostic,mode=mode,position=position,enable=enable,
        period=period,capture=(index*257)&65535,count=0xa7b8,offset=0xc9da,
        scratch=(index*53)&255,remainder=(index*59)&255)
    old_memory=memory.copy()
    for i in range(8,15):state.put(188-4*i,4,incoming[i])
    state.put(124,4,gbr) # Independent main PR occupies offset 128.
    state.gbr=RAM+0x1ff4
    timer=(0xfffe-index*131)&65535
    compare,timer_status,timer_control=0xa7b8,(0x8001^index*97)&65535,(0xa55b^index*131)&65535
    counters=[(0,1,32767,32768,65534,65535)[(i+index)%6] for i in range(6)]
    original_counters=counters.copy()
    selection_args=selector_model.case(argument=3,config=config,variant=index&1,pending=memory['pending'],**selection)
    selection_inputs=selection_args
    outputs=list(selection_args['snapshot'])
    corrections=list(selection_args['correction']);secondary=list(selection_args['secondary'])
    selector_calls=oneshot_calls=programmer_calls=0
    final_event_flag,final_event_aux=event_flag,event_aux
    def choose(argument,return_pc):
        nonlocal selector_calls,outputs,corrections,secondary,selection_args
        selector_calls+=1
        r[4]=argument
        params=selector_model.case(argument=argument,config=config,variant=index&1,
            pending=memory['pending'],correction=corrections,secondary=secondary,
            **{key:value for key,value in selection.items() if key not in ('correction','secondary')})
        params['incoming']=list(params['incoming'])
        state.put(96,4,r[14]);state.put(92,4,return_pc)
        state.put(88,4,macl);state.put(84,4,state.gbr)
        if params['local_written']:state.put(80,4,params['local_value'])
        if config&8:
            for i in range(8,14):state.put(108-4*i,4,r[i])
            state.put(52,4,params['running'] if params['local_written'] else r[14])
            state.put(48,4,0x54e7c)
            state.put(44,4,params['child_macl'])
            state.put(40,4,RAM+0x2330);state.put(36,4,params['child_r2'])
        state.merge(params)
        r[4]=params['expected'][4]
        outputs=list(params['output']);corrections=list(params['expected_correction'])
        secondary=list(params['expected_secondary'])
        selection_args=params
        # The final TST of config and all possible six-channel loops have fixed T.
        state.t(True)
    def one(mask):
        nonlocal oneshot_calls,counters,started
        oneshot_calls+=1
        r[4],r[5]=mask&MASK,RAM+0x224e
        row=oneshot_model.case(1,argument=mask&MASK,enable=enable,opening=selection_args['opening'],
            inhibit=selection_args['inhibit'],history=memory['history'],started=started,
            diagnostic=diagnostic,entry_sr=state.sr,durations=outputs,counters=counters)
        for i in range(8,15):state.put(128-4*i,4,r[i])
        state.put(68,4,macl);state.put(64,4,state.gbr)
        if enable&128:
            state.put(52,4,PULSE_ALIAS+12);state.put(56,1,64)
            if row['selected']:state.put(60,2,row['last_increment'])
        state.merge(row);state.t(True)
        counters=list(row['output']);started=row['expected_started'];memory['history']=row['expected_history']
    memory['ticks']=min(255,memory['ticks']+1)
    r[14]=RAM+0x4555;r[4]=memory['ticks'];r[7]=signed(event_flag,8)
    r[0]=cylinder;r[8]=0x2268e
    channels=table[cylinder]
    r[4]=channels
    order=signed(table[cylinder+13],8)-1
    bit=(1<<max(0,channels-1))&MASK
    r[2]=bit;r[5]=order;r[3]=RAM+0x128c
    r[6]=signed(memory['cylinder_history'],8)|bit
    memory['cylinder_history']=r[6]&255
    lead=lead_source if event_flag&32 else 3
    if event_flag&32:r[4]=RAM+0x2330
    slot=((order&15)-lead)
    if slot<0:slot+=6
    slot&=255
    memory['slot']=slot;r[9]=lead;r[5]=slot
    r[0]=event_source&32;r[2]=r[0];r[6]=RAM+0x24c8
    if event_source&32 and not event_flag&16:
        final_event_flag=event_flag|240
        final_event_aux=event_aux|128
        cursor=(slot-1)&255 if slot else 5
        state.put(104,4,cursor)
        memory['cursor'],memory['old_lead']=cursor,lead
        r[14]=RAM+0x1ff4;r[4]=EVENT_ALIAS;r[5]=EVENT_ALIAS;r[7]=signed(final_event_flag,8)
    r[0],r[5],r[6]=final_event_flag&224,224,signed(224,8)
    state.t(r[0]==224)
    path=0;r0_full_sr=0
    if r[0]==224:
        if control_flag&128:
            if not event_source&32 and event_mode<=4:
                r[14]=RAM+0x1ff4
                choose(4,0x54b3c)
                if event_mode==4:final_event_aux|=128
            else:choose(3,0x54b62)
            state.put(120,4,signed(memory['queue'],8))
            pending=memory['pending']
            for name in ('queue','mask_a','mask_b'):memory[name]|=pending
            memory['history']&=~pending&255
            if config&8:
                memory['mask_c']|=pending;memory['mask_d']|=pending
            r[2]=0x2c13c
            one(signed(pending,8))
            timer_control&=65534
            r[5]=TIMER_ALIAS;r[4]=MASK-1;r[6]=timer_control;r[0]=34
        r[14]=RAM+0x1ff4;r[4]=RAM+0x2330
        delta=memory['old_lead']-lead
        produced=4*angle
        state.put(108,4,produced)
        r[5]=produced;r[6]=delta
        if delta==0:
            memory['pending']=0
            next_slot=memory['cursor']+1
            if next_slot>=6:next_slot=0
            r[0],r[2],r[5],r[6]=slot,signed(memory['cursor'],8),slot,next_slot
            if next_slot==slot:
                memory['cursor']=slot;r[8]+=7
                r[2]=signed(table[7+slot],8);memory['pending']=r[2]&255
            path=1
        elif delta<0:
            memory['pending']=0;r[3],r[2],r[0]=RAM+0x1ff4,0,0x234
            path=2
        else:
            path=3
            r[10],r[11],r[6]=delta,0,0
            state.put(112,4,0);state.put(116,4,0)
            state.put(100,4,lead)
            r[9]=6;r[12]=signed(memory['cursor'],8)
            r[7]=signed(memory['queue'],8);r[13]=signed(memory['mask_a'],8)
            r[14]=signed(memory['mask_b'],8);r[4]=signed(memory['history'],8)
            queue_before,mask_a_before,mask_b_before=memory['queue'],memory['mask_a'],memory['mask_b']
            mask=0
            for _ in range(delta):
                next_slot=(memory['cursor']+1)&255
                if next_slot>=6:next_slot=0
                memory['cursor']=next_slot
                mask|=table[7+next_slot]
            memory['queue']|=mask;memory['mask_a']|=mask;memory['mask_b']|=mask
            memory['history']&=~mask&255
            r[11]=delta;r[12]=memory['cursor'];r[13]=signed(mask_a_before,8)|mask
            r[14]=signed(mask_b_before,8)|mask;r[7]=signed(queue_before,8)|mask
            state.put(112,4,delta);state.put(116,4,mask)
            r[9]=lead
            if config&8:
                memory['mask_c']|=mask;memory['mask_d']|=mask
            memory['pending']=mask;r[14]=RAM+0x1ff4;r[8]+=7
            choose(3,0x54cee)
            r[2]=0x2c13c
            one(mask)
            memory['cursor']=slot;r[0]=slot
            r[2]=signed(table[7+slot],8);memory['pending']=r[2]&255
        memory['old_lead']=lead
        r[3],r[6]=RAM+0x1ff4,RAM+0x424c
        argument=52 if diagnostic&1 else produced
        r[4],r[2]=argument,0x2b64a
        state.t(not diagnostic&1)
        state.put(96,4,r[13]);state.put(92,4,r[14]);state.put(88,4,0x54d28)
        state.put(84,4,macl);state.put(80,4,state.gbr)
        original=[]
        programmer.held.append(original,argument,mode,position,control_flag,period,index&1,state.sr&1)
        calculation=programmer.convert(original[0],index,timer=timer,capture=memory['capture'],
            compare=compare,status=timer_status,control=timer_control,entry_sr=state.sr)
        if calculation['normal'] or not calculation['count']:
            state.put(76,4,calculation['product'] if not calculation['count'] else macl)
        state.merge(calculation)
        memory['count'],memory['remainder']=calculation['count'],calculation['remainder']
        if not calculation['count']:
            memory['offset'],memory['scratch']=calculation['quotient']&65535,calculation['scratch']
            state.sr=(state.sr&~0xf1)|0x80|calculation['expected_t']
            r[0]=state.sr;r0_full_sr=1
        else:state.t(False)
        compare,timer_status,timer_control=calculation['expected_compare'],calculation['expected_status'],calculation['expected_control']
        control_flag|=128
        programmer_calls=1
    for i in range(8,15):r[i]=incoming[i]
    row=dict(entry_sr=entry_sr,variant=index&1,control_flag=initial_control_flag,
        event_flag=event_flag,event_aux=event_aux,timer=timer,compare=0xa7b8,
        timer_status=(0x8001^index*97)&65535,timer_control=(0xa55b^index*131)&65535,
        started=initial_started,path=path,expected_sr=state.sr,r0_full_sr=r0_full_sr,
        expected_control_flag=control_flag,expected_event_flag=final_event_flag,expected_event_aux=final_event_aux,
        expected_compare=compare,expected_timer_status=timer_status,expected_timer_control=timer_control,
        expected_started=started,selector_calls=selector_calls,oneshot_calls=oneshot_calls,programmer_calls=programmer_calls,
        old_memory=old_memory,output=memory,counters=original_counters,counter_output=counters,
        incoming=incoming,expected=[value&MASK for value in r],frame=state.frame,
        selection=selection_inputs,selection_output=selection_args,
        durations=selection_inputs['snapshot'],output_words=outputs,
        output_corrections=corrections,output_secondary=secondary,channel_table=table)
    return row

def matrix(table):
    rows=[]
    def add(**changes):rows.append(case(len(rows),table,**changes))
    early=(dict(event_flag=0),dict(event_flag=0xe0,old_lead=3,lead_source=3),
        dict(event_flag=0xe0,old_lead=2,lead_source=3),
        dict(event_flag=0xe0,old_lead=4,lead_source=3),
        dict(event_flag=0xe0,old_lead=9,lead_source=3,config=8),
        dict(event_flag=0xe0,old_lead=255,lead_source=0,config=8),
        dict(control_flag=128,event_mode=0,old_lead=3),
        dict(control_flag=128,event_mode=4,old_lead=3),
        dict(control_flag=128,event_mode=5,old_lead=4),
        dict(control_flag=128,event_source=32,event_flag=0xe0,old_lead=4),
        dict(control_flag=128,event_source=32,event_flag=0,old_lead=4),
        dict(mode=64,angle=255,old_lead=3),
        dict(mode=64,angle=20,old_lead=3),
        dict(mode=0,angle=50,old_lead=3,position=4),
        dict(mode=0,angle=25,old_lead=3,position=9),
        dict(mode=64,angle=64,old_lead=3,diagnostic=1),
        dict(config=8,control_flag=128,started=65535,old_lead=4),
        dict(enable=0,control_flag=128,old_lead=4),
        dict(event_flag=0xe0,old_lead=3,cursor=5,cylinder=1),
        dict(event_flag=0xe0,old_lead=3,cursor=255,cylinder=1),
        dict(event_flag=0xe0,old_lead=0,lead_source=255,cursor=4),
        dict(event_flag=0xe0,old_lead=255,lead_source=255,cursor=4),
        dict(event_flag=0xe0,old_lead=255,lead_source=254,cursor=4),
        dict(event_flag=0xe0,old_lead=0,lead_source=0,cursor=4))
    for values in early:add(**values)
    for angle in range(256):
        for mode in (0,64):
            for delta in (-1,0,1):
                add(angle=angle,mode=mode,old_lead=3+delta,config=8 if angle&1 else 0,
                    control_flag=128 if angle&2 else 0,diagnostic=angle&1,position=angle)
    for delta in range(256):
        for control in (0,128):
            add(lead_source=0,old_lead=delta,control_flag=control,config=8,started=(delta*257)&65535,
                cursor=delta,history=delta^0x55)
    for flag in range(256):
        for event in (0,32):
            add(event_flag=flag,event_source=event,event_aux=flag^0x2a,control_flag=flag,
                event_mode=flag,enable=flag,config=flag,diagnostic=flag,old_lead=flag)
    for lead in range(256):
        for delta in (-1,0,1):
            old=max(0,min(255,lead+delta))
            add(lead_source=lead,old_lead=old,cursor=lead,cylinder=lead,
                control_flag=128,config=8,started=65535)
    for bits in range(128):
        entry=(bits&1)|((bits&30)<<3)|((bits&96)<<3)
        for kind in range(4):
            add(entry_sr=entry,mode=64 if kind&1 else 0,old_lead=4 if kind&2 else 3,
                config=8,control_flag=128,diagnostic=kind&1,angle=bits,position=bits)
    return rows

def header(rows):
    memory_names=tuple(name for name,_ in (*BYTE_RAM,*WORD_RAM))
    literal=lambda value:f'0x{value&MASK:x}U'
    max_frame=max(len(row['frame']) for row in rows)
    lines=[]
    nested=lambda row:'{'+','.join(literal(row[name]) for name in selector_model.SCALARS)+','+','.join(
        '{'+','.join(map(literal,row[name]))+'}' for name,_ in selector_model.ARRAYS)+'}'
    array_names=('counters','counter_output','durations','output_words','output_corrections','output_secondary','incoming','expected')
    for row in rows:
        fields=[literal(row[name]) for name in SCALARS]
        fields += [literal(row['old_memory'][name]) for name in memory_names]
        fields += [literal(row['output'][name]) for name in memory_names]
        fields += ['{'+','.join(map(literal,row[name]))+'}' for name in array_names]
        fields += [nested(row['selection']),str(len(row['frame']))+'U',
                   '{'+','.join('{'+str(at)+'U,'+literal(value)+'}' for at,value in sorted(row['frame'].items()))+'}']
        lines.append('{'+','.join(fields)+'},')
    return ('/* Independent whole-call state and ordered byte writes. */\n'
        '#ifndef FULL_DISPATCH_CASES_H\n#define FULL_DISPATCH_CASES_H\n#include <stdint.h>\n'
        'struct dispatch_selector { uint32_t '+','.join(selector_model.SCALARS)+';\n'+
        ''.join(f'    uint32_t {name}[{size}];\n' for name,size in selector_model.ARRAYS)+'};\n'
        'struct full_dispatch_case {\n    uint32_t '+','.join(SCALARS)+';\n'
        '    uint32_t '+','.join('in_'+name for name in memory_names)+';\n'
        '    uint32_t '+','.join('out_'+name for name in memory_names)+';\n'+
        ''.join(f'    uint32_t {name}[{15 if name in ("incoming","expected") else 6}];\n' for name in array_names)+
        '    struct dispatch_selector selection;\n    uint32_t frame_count;\n'+
        f'    struct {{ uint32_t at,value; }} frame[{max_frame}];\n'+
        '};\nstatic const struct full_dispatch_case full_dispatch_cases[]={\n'+'\n'.join(lines)+
        '\n};\n#define FULL_DISPATCH_CASE_COUNT '+str(len(rows))+'U\n'
        '#define FULL_DISPATCH_EARLY_COUNT 24U\n#endif\n')
