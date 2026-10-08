"""Independent numerical coolant selection, hysteresis, limiter and cap context."""
from stock_injection_end_angle_model import State

MASK=0xffffffff
BYTE_INPUTS=(('rpm',0x11b3),('warm',0x1107),('previous_coolant',0x106f),
    ('load',0x102c),('rpm_select',0x11ae),('flags_a',0x2492),('flags_b',0x2493),
    ('source_flag',0x2458),('direction_flag',0x2485))
WORD_INPUTS=(('old',0x15da),('mixture',0x22e8))
CALIBRATIONS=(('thresholds',0x87a5,3),('hysteresis',0x86eb,1),('curve',0x12422,8),
    ('load_axis',0x11b1b,4),('rpm_axis',0x11b17,4),('coefficients',0x990a,16),
    ('rate',0x9090,2),('cap',0x929a,2),('coolant_offset',0x5533c,2))
DEFAULTS={'rpm':144,'warm':150,'previous_coolant':240,'load':80,'rpm_select':72,
    'flags_a':0,'flags_b':0,'source_flag':0,'direction_flag':0,'old':0,'mixture':16384,
    'thresholds':(144,150,150),'hysteresis':3,'curve':(0,0,0,4,7,10,13,16),
    'load_axis':(64,70,82,102),'rpm_axis':(24,72,80,104),
    'coefficients':(0,0,0,128,0,0,0,128,0,0,128,128,0,128,128,128),
    'rate':5,'cap':7799,'coolant_offset':-192}

def signed(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value

def case(index,**changes):
    row={**DEFAULTS,**changes}
    for name,_ in BYTE_INPUTS:assert 0<=row[name]<=255
    for name,_ in WORD_INPUTS:assert 0<=row[name]<=65535
    for name,_,size in CALIBRATIONS:
        value=row[name]
        if isinstance(value,(tuple,list)):assert len(value)==size and all(0<=x<=255 for x in value)
        elif name=='coolant_offset':assert -32768<=value<=32767
        else:assert 0<=value<=(65535 if size==2 else 255)
    variant=changes.get('variant',index&1)
    entry_sr=changes.get('entry_sr',(index&1)|(((index>>1)&15)<<4)|((index&3)<<8))
    assert variant in (0,1) and entry_sr&~0x3f1==0
    incoming=[((0x1728394a+r*0x110203) if variant==0 else
               (0x81234567+r*0x1020305))&MASK for r in range(15)]
    macl=0x9274b6d8 if variant else 0x2468ace0
    gbr=0x01004567 if variant else 0x01003579
    state=State(incoming,macl,entry_sr)
    for i in range(5):state.put(156-4*i,4,incoming[10+i])
    state.put(132,4,macl);state.put(128,4,gbr)
    thresholds=row['thresholds']
    rpm_reached=row['rpm']+(2 if row['flags_a']&8 else 0)>=thresholds[0]
    a=(row['flags_a']|8) if rpm_reached else row['flags_a']&247
    warm_high=row['warm']+(row['hysteresis'] if row['flags_b']&128 else 0)>thresholds[2]
    b=(row['flags_b']|128) if warm_high else row['flags_b']&127
    warm_low=row['warm']+(row['hysteresis'] if a&2 else 0)
    lower_reached=warm_low>=thresholds[1]
    a=(a|2) if lower_reached else a&253
    gate=lower_reached if rpm_reached else warm_high
    a=(a|4) if gate else a&251
    enabled=bool(not row['source_flag']&32 and gate)
    direction=row['direction_flag']
    value=0;coordinate=None;selected=None;lookup=None;candidate=None;cap=None
    if enabled:
        coordinate=(max(0,row['previous_coolant']+row['coolant_offset'])*4)&255
        state.r[2],state.r[4],state.r[5]=0x26370,0x12422,coordinate
        lookup=state.implicit(row['curve'],0x12422,coordinate,108)
        load_index=next((i for i in range(1,4) if row['load']<=row['load_axis'][i]),4)
        rpm_index=next((i for i in range(1,4) if row['rpm_select']<=row['rpm_axis'][i]),4)
        selected=row['coefficients'][4*rpm_index+load_index-5]
        candidate=lookup*selected
        state.put(108,4,candidate)
        if a&1:
            difference=candidate-row['old']
            direction=(direction|128) if difference>=0 else direction&127
            for offset in (112,120):state.put(offset,4,difference)
            state.put(116,4,abs(difference));state.put(124,4,row['rate'])
            if abs(difference)>row['rate']:
                candidate=row['old']+(row['rate'] if difference>=0 else -row['rate'])
        cap=max(0,row['cap']-row['mixture']+16384)
        value=min(candidate,cap)
        state.t(candidate>cap)
        state.put(108,4,value)
        a|=1
        state.r[2]=(row['cap']-row['mixture']+16384)&MASK
        state.r[4],state.r[6],state.r[7]=cap,16384,row['mixture']
    else:
        a&=254
        state.t(not row['source_flag']&32)
        state.put(108,4,0)
        state.r[2],state.r[4],state.r[6]=thresholds[1],0x01001094,warm_low
    state.r[0],state.r[5]=0x34e,value
    state.r[10:15]=incoming[10:15]
    row.update({'variant':variant,'entry_sr':entry_sr,'incoming':incoming,'expected':state.r,
        'expected_sr':state.sr,'frame_writes':state.frame,'output':value&65535,
        'updated_a':a,'updated_b':b,'updated_direction':direction,'enabled':int(enabled),
        'coordinate':coordinate,'lookup':lookup,'selected':selected,'candidate':candidate,'cap_value':cap})
    assert 0<=value<=65535 and state.macl==macl
    return row

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    for flags_a in (0,1,2,3,8,9,10,255):
        for source_flag in (0,32):add(flags_a=flags_a,source_flag=source_flag)
    for rpm in range(256):
        for warm in (0,143,144,147,148,149,150,151,152,153,254,255):
            for flags_a,flags_b in ((0,0),(2,0),(8,0),(10,128)):
                add(rpm=rpm,warm=warm,flags_a=flags_a,flags_b=flags_b)
    for coolant in range(256):
        for curve in (DEFAULTS['curve'],(255,)*8,(255,0,255,0,255,0,255,0)):
            for flags_a in (0,1):add(previous_coolant=coolant,flags_a=flags_a,curve=curve)
    for load in (0,69,70,71,81,82,83,101,102,103,255):
        for rpm in (0,71,72,73,79,80,81,103,104,105,255):add(load=load,rpm_select=rpm)
    for old in (0,1,4,5,6,1023,65024,65025,65534,65535):
        for rate in (0,1,5,255,32768,65535):
            for cap,mixture in ((0,0),(0,16384),(0,65535),(65535,0),(65535,65535)):
                add(flags_a=1,old=old,rate=rate,cap=cap,mixture=mixture,coefficients=(255,)*16,curve=(255,)*8)
    return rows

if __name__=='__main__':
    rows=matrix()
    assert len(rows)==14261
    assert {row['enabled'] for row in rows}=={0,1}
    assert {row['expected_sr']&1 for row in rows}=={0,1}
    print(f'PREPARED_COOLANT_CONDITIONAL cases={len(rows)} gnu_executed=0 accepted_points=0')
