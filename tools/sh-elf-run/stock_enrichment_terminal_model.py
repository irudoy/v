"""Independent staged mixture bounds, auxiliary state and complete terminal observations."""
from stock_injection_end_angle_model import State

MASK=0xffffffff
BYTE_INPUTS=(('mode',0x1410),('flags',0x2485),('phase_flags',0x2493),('mixture',0x15eb),
    ('tick',0x84c3),('rpm',0x2700),('delay',0x2531),('override',0x4252),
    ('aux_flags',0x2474),('normalized',0x102c),('temperature',0x110e),('aux_delay',0x24e9),('rpm_byte',0x11b3))
WORD_INPUTS=(('previous',0x1278),('aux_previous',0x127a),('aux_current',0x123c),('staged',None))
CAL_BYTE=(('down',0x849b),('up',0x849c),('rich_set',0x8b9b),('rich_initial',0x8b9c),
    ('rich_hold',0x8b9f),('norm_hysteresis',0x86ea),('temperature_hysteresis',0x86f3),
    ('temperature_threshold',0x87d9),('delay_reload',0x8bef),('speed_reload',0x87d6))
CAL_WORD=(('main_limit',0x929c),('override_limit',0x94ec),('aux_cap',0x8f86))
STOCK={'down':38,'up':48,'rich_set':130,'rich_initial':130,'rich_hold':129,
    'norm_hysteresis':0,'temperature_hysteresis':0,'temperature_threshold':0,'delay_reload':254,
    'speed_reload':2,'main_limit':16384,'override_limit':65535,'aux_cap':16384,'curve':(254,)*8}
CALIBRATIONS=[STOCK,
    {**STOCK,'curve':(0,)*8,'down':0,'up':0,'delay_reload':0,'speed_reload':0},
    {**STOCK,'curve':(255,)*8,'down':255,'up':255,'aux_cap':65535,'main_limit':65535,
        'temperature_threshold':255,'override_limit':0},
    {**STOCK,'curve':tuple(range(0,256,32)),'norm_hysteresis':255,'temperature_hysteresis':255,
        'rich_set':0,'rich_initial':255,'rich_hold':255,'aux_cap':0,'override_limit':32768},
    {**STOCK,'curve':tuple(reversed(range(0,256,32))),'norm_hysteresis':1,'temperature_hysteresis':1,
        'temperature_threshold':128,'rich_set':255,'rich_initial':0,'rich_hold':0,'aux_cap':32768},
    {**STOCK,'curve':(255,0,255,0,255,0,255,0),'aux_cap':32767,'main_limit':32767,
        'override_limit':1,'delay_reload':1,'speed_reload':255}]
DEFAULTS={'mode':2,'flags':0,'phase_flags':0,'mixture':149,'tick':128,'rpm':32,'delay':0,'override':0,
    'aux_flags':0,'normalized':128,'temperature':100,'aux_delay':1,'rpm_byte':100,
    'previous':16384,'aux_previous':16384,'aux_current':16384,'staged':16384,'calibration':0}

def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value

def arithmetic(v,cal):
    tick=bool(v['tick']&128);p=v['previous'];target=v['mixture']*128
    down=max(16384,p-cal['down']*8) if tick else p
    up=min(target,p+cal['up']*8) if tick else p
    mode=v['mode'];special=not v['phase_flags']&16 and bool(v['phase_flags']&8)
    candidate=v['staged'];candidate_written=True
    if mode==1:candidate=16384
    elif mode==2 and special:candidate=down if down>=cal['rich_hold']*128 else 16384
    elif mode==6 and special:
        candidate=cal['rich_initial']*128 if p==16384 else (down if p>cal['main_limit'] else up)
    elif mode in (2,3,6):
        if v['flags']&32:candidate=target
        elif p==16384:candidate=cal['rich_set']*128
        elif p>16384:candidate=up
        else:candidate_written=False
    elif mode in (4,5):candidate=target
    else:candidate_written=False
    primary=min(candidate&65535,target)
    updated_flags=(v['flags']|32) if primary==target else (v['flags']&223)
    x=v['rpm_byte'];curve=cal['curve']
    if x>=224:curve_value=curve[7]
    else:
        cell,rem=divmod(x,32);left,right=curve[cell:cell+2];delta=abs(right-left)*rem//32
        curve_value=left+delta if right>=left else left-delta
    aux_on=v['normalized']+(cal['norm_hysteresis'] if v['aux_flags']&128 else 0)>=curve_value
    aux_flags=(v['aux_flags']|128) if aux_on else (v['aux_flags']&127)
    temp_on=v['temperature']+(cal['temperature_hysteresis'] if not v['phase_flags']&4 else 0)<=cal['temperature_threshold']
    phase_flags=(v['phase_flags']|4) if temp_on else (v['phase_flags']&251)
    ready=aux_on and temp_on
    aux_delay=v['aux_delay'] if ready else cal['delay_reload']
    active=ready and v['aux_delay']==0
    aux_flags=(aux_flags|64) if active else (aux_flags&191)
    b=v['aux_previous'];cap=cal['aux_cap'];aux=v['aux_current'];aux_written=False
    aux_down=max(16384,b-cal['down']*8);aux_up=min(cap,b+cal['up']*8)
    if tick:
        if active:
            if b==16384:aux=cal['rich_set']*128;aux_written=True
            elif b>16384 and b<cap:aux=aux_up;aux_written=True
            elif b>=cap:aux=cap;aux_written=True
        else:
            if b>cal['rich_hold']*128 and b<=cap:aux=aux_down;aux_written=True
            elif b<=cal['rich_hold']*128:aux=16384;aux_written=True
    aux&=65535
    delay=cal['speed_reload'] if v['rpm']<32 else v['delay']
    output=max(primary,aux)
    if v['rpm']<32 or delay:output=16384
    before_override=output
    if v['override']&2:output=min(output,cal['override_limit'])
    return {'down_bound':down,'up_bound':up,'candidate_word':candidate&65535,
        'candidate_written':candidate_written,'primary_word':primary,'updated_flags':updated_flags,
        'aux_curve_value':curve_value,'updated_aux_flags':aux_flags,'updated_phase_flags':phase_flags,
        'updated_aux_delay':aux_delay,'aux_active':active,'aux_word':aux,'aux_written':aux_written,
        'updated_delay':delay,'output_word':output,'before_override':before_override}

def case(index,variant=None,entry_sr=None,**changes):
    v={**DEFAULTS,**changes};assert set(v)==set(DEFAULTS)
    for name,_ in BYTE_INPUTS:assert 0<=v[name]<=255
    for name,_ in WORD_INPUTS:assert 0<=v[name]<=65535
    assert 0<=v['calibration']<len(CALIBRATIONS);cal=CALIBRATIONS[v['calibration']]
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and not entry_sr&~0x3f1
    incoming=[((0x1728394a+r*0x110203) if variant==0 else (0x81234567+r*0x1020305))&MASK for r in range(15)]
    incoming[0]=(incoming[0]&0xffff0000)|v['staged']
    macl=0x9274b6d8 if variant else 0x2468ace0;gbr=0x01004567 if variant else 0x01003579
    state=State(incoming,macl,entry_sr);r=state.r;expected=arithmetic(v,cal)
    # The observer stages SP+12 from incoming R0 before its before-frame capture.
    if expected['candidate_written']:state.put(172,2,expected['candidate_word'])
    if v['tick']&128:r[12]=cal['up']
    mode=v['mode'];special=not v['phase_flags']&16 and bool(v['phase_flags']&8)
    if mode==6 and special or mode in (2,3,6) and not special and not v['flags']&32:
        r[12]=16384
    if mode==3 and not v['flags']&32:r[12]=16384
    # Mode 2 with special flags bypasses the general unity comparison.
    flag_register=(signed(v['flags'],8)|32) if expected['primary_word']==v['mixture']*128 else signed(v['flags'],8)&223
    state.put(156,4,0x0100128c);state.put(152,4,flag_register)
    state.put(148,4,0x564aa);state.put(144,4,gbr)
    x=v['rpm_byte'];curve=cal['curve']
    if x<224:
        cell,rem=divmod(x,32)
        value=state.linear(curve[cell],curve[cell+1],rem*2048,140)
        assert value==expected['aux_curve_value']
    if v['tick']&128:
        b=v['aux_previous']
        if expected['aux_active'] and b==16384:state.put(140,2,cal['rich_set']*128)
        elif expected['aux_active'] or b>cal['rich_hold']*128:r[3]=0x8f86
    r[0]=expected['output_word'];r[5]=expected['output_word'];r[6]=0x010022dc;r[7]=0x010024f9
    r[13]=flag_register&MASK;r[14]=0x87cc if v['rpm']<32 else 0x0100120e
    if v['override']&2:
        cap=cal['override_limit'];r[2]=min(expected['before_override'],cap);r[4]=signed(cap,16)&MASK
        state.t(expected['before_override']>cap)
    else:
        r[2]=signed(expected['updated_delay'],8)&MASK;r[4]=32;state.t(True)
    r[:]=[value&MASK for value in r]
    assert set(state.frame)<=set(range(136,176))
    return {**v,**expected,'variant':variant,'entry_sr':entry_sr,'expected_sr':state.sr,
        'incoming':incoming,'expected':r,'frame_writes':state.frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    for mode in range(8):
        for tick in (0,128):add(mode=mode,tick=tick,phase_flags=8 if mode&1 else 0)
    for flags in (0,32,128,255):
        for aux_flags in (0,64,128,255):
            add(flags=flags,aux_flags=aux_flags,aux_delay=0,normalized=255,temperature=0,override=2)
    for previous in range(65536):
        add(previous=previous,aux_previous=previous^0x5555,staged=previous^0xaaaa,
            aux_current=(previous*7)&65535,mode=previous&7,flags=(previous>>8)&255,
            phase_flags=(previous>>4)&255,tick=previous&128,rpm=(previous>>7)&255,
            delay=previous&1,override=(previous>>1)&2,normalized=previous&255,
            temperature=(previous>>8)&255,aux_flags=previous&255,aux_delay=(previous>>9)&1,
            rpm_byte=(previous*13)&255)
    bounds=(0,1,16383,16384,16385,16511,16512,16513,19071,19072,19073,32767,32768,65534,65535)
    for calibration in range(6):
        for previous in bounds:
            for mode in (1,2,3,4,5,6,7,8):
                for phase_flags in (0,8,16,24):
                    add(calibration=calibration,previous=previous,aux_previous=previous,mode=mode,
                        phase_flags=phase_flags,aux_flags=128,aux_delay=0,temperature=0,
                        normalized=255,mixture=(previous*11)&255,rpm_byte=(previous*7)&255,
                        flags=32 if previous&1 else 0,override=2 if previous&2 else 0)
    for value in range(256):
        for calibration in range(6):
            add(calibration=calibration,flags=value,phase_flags=value,aux_flags=value,
                normalized=value,temperature=value,aux_delay=value,tick=value,mixture=value,
                override=value,rpm=value,delay=value,rpm_byte=value)
    for sr in range(128):
        entry=(sr&1)|((sr&30)<<3)|((sr&96)<<3)
        add(entry_sr=entry,override=sr&2,rpm_byte=sr*2)
    assert len(rows)==70112,len(rows)
    assert {row['previous'] for row in rows}==set(range(65536))
    assert {row['entry_sr'] for row in rows}=={t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
    return rows

if __name__=='__main__':
    rows=matrix();print(f'ENRICHMENT_TERMINAL cases={len(rows)} early=32 gnu_executed=0 accepted_points=0')
