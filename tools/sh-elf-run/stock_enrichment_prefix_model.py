"""Independent axis, surface, correction and rich-latch equations at the prefix boundary."""
from stock_injection_end_angle_model import State

MASK=0xffffffff
BYTE_INPUTS=(('rpm_byte',0x11b3),('load_threshold',0x3528),('wide_flags',0x2468),
    ('normalized',0x102c),('correction_flags',0x2466),('correction_coordinate',0x11ae),('rich_flags',0x24a2))
WORD_INPUTS=(('speed',0x11bc),)
TABLES=(('wide_curve',0x1214e,16),('surface',0xa9aa,64),('row_axis',0x11cc0,8),
    ('column_axis',0x11ac7,8),('correction_curve',0x12552,9),('correction_axis',0x11cd8,8))
SCALARS=(('rich_set',0x8b9b),('rich_hold',0x8b9f))
STOCK={'wide_curve':(200,)*16,
    'surface':tuple(bytes.fromhex('808080808080808e80808080808080928080808080808092808080808a9292958080808a8a9292958080808a8e95959580808e8e90959595808c909293959595')),
    'row_axis':(48,56,64,80,104,112,120,136),'column_axis':(80,88,104,112,120,128,135,149),
    'correction_curve':(128,128,128,128,128,128,154,154,40),'correction_axis':(0,16,32,48,64,80,96,112),
    'rich_set':130,'rich_hold':129}
CALIBRATIONS=[STOCK]
for pattern in range(1,6):
    if pattern==1:surface=(0,)*64;wide=(0,)*16;curve=(0,)*9
    elif pattern==2:surface=(255,)*64;wide=(255,)*16;curve=(255,)*9
    elif pattern==3:
        surface=tuple(row*17+column*13 for row in range(8) for column in range(8))
        wide=tuple(range(0,256,16));curve=tuple(i*31 for i in range(9))
    elif pattern==4:
        surface=tuple(255-row*17-column*13 for row in range(8) for column in range(8))
        wide=tuple(reversed(range(0,256,16)));curve=tuple(255-i*31 for i in range(9))
    else:
        surface=tuple(255 if (row+column)&1 else 0 for row in range(8) for column in range(8))
        wide=tuple(255 if i&1 else 0 for i in range(16));curve=tuple(255 if i&1 else 0 for i in range(9))
    CALIBRATIONS.append({**STOCK,'surface':surface,'wide_curve':wide,'correction_curve':curve})
CALIBRATIONS += [{**CALIBRATIONS[3],'rich_set':0,'rich_hold':255},
                 {**CALIBRATIONS[4],'rich_set':255,'rich_hold':0}]
DEFAULTS={'rpm_byte':100,'load_threshold':128,'wide_flags':0,'normalized':120,
    'correction_flags':0,'correction_coordinate':80,'rich_flags':0,'speed':300,'calibration':0}

def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value
def linear(left,right,fraction):
    distance=abs(right-left)*fraction//65536
    return left+distance if right>=left else left-distance
def coordinate(axis,x,multiplier=1):
    assert len(axis)==8 and all(0<=a<b<=255 for a,b in zip(axis,axis[1:]))
    cell=max((i for i,value in enumerate(axis) if x>=value*multiplier),default=0)
    fraction=0 if cell==7 or x<=axis[cell]*multiplier else (
        (x-axis[cell]*multiplier)*65536//((axis[cell+1]-axis[cell])*multiplier))
    return cell,fraction
def surface_lookup(cal,speed,load):
    row,rf=coordinate(cal['row_axis'],speed,4);column,cf=coordinate(cal['column_axis'],load)
    table=cal['surface'];top=table[row*8+column]
    if cf:top=linear(top,table[row*8+column+1],cf)
    if rf:
        bottom=table[(row+1)*8+column]
        if cf:bottom=linear(bottom,table[(row+1)*8+column+1],cf)
        top=linear(top,bottom,rf)
    return top
def arithmetic(v,cal):
    x=v['rpm_byte'];cell,rem=divmod(min(x,239),16)
    wide=cal['wide_curve'][15] if x>=240 else linear(cal['wide_curve'][cell],cal['wide_curve'][cell+1],rem*4096)
    wide_on=v['load_threshold']+(8 if v['wide_flags']&8 else 0)>=wide
    flags=(v['wide_flags']|8) if wide_on else (v['wide_flags']&247)
    load=255 if wide_on else v['normalized'];m=surface_lookup(cal,v['speed'],load)
    surface=m;correction=None
    if v['correction_flags']&64:
        ci,cf=coordinate(cal['correction_axis'],v['correction_coordinate'])
        correction=linear(cal['correction_curve'][ci],cal['correction_curve'][ci+1],cf)
        m=max(0,min(255,128+((m-128)*correction//128)))
    test=(m+(cal['rich_set']-cal['rich_hold'] if v['rich_flags']&128 else 0))&MASK
    rich_on=test>=cal['rich_set']
    rich_flags=(v['rich_flags']|128) if rich_on else (v['rich_flags']&127)
    return {'wide_value':wide,'updated_wide_flags':flags,'load_coordinate':load,'surface_value':surface,
        'correction_value':correction,'adjusted_value':m,'latch_argument':test,
        'updated_rich_flags':rich_flags,'mixture_byte':m if rich_on else 128,'rich_on':rich_on}

def case(index,variant=None,entry_sr=None,**changes):
    v={**DEFAULTS,**changes};assert set(v)==set(DEFAULTS)
    for name,_ in BYTE_INPUTS:assert 0<=v[name]<=255
    assert 0<=v['speed']<=65535 and 0<=v['calibration']<len(CALIBRATIONS)
    cal=CALIBRATIONS[v['calibration']]
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and not entry_sr&~0x3f1
    incoming=[((0x1728394a+r*0x110203) if variant==0 else (0x81234567+r*0x1020305))&MASK for r in range(15)]
    macl=0x9274b6d8 if variant else 0x2468ace0
    state=State(incoming,macl,entry_sr);r=state.r
    for i in range(4):state.put(156-4*i,4,incoming[11+i])
    state.put(136,4,macl)
    # Offset 140 is the independently observed continuation saved by the stock prologue.
    independent=arithmetic(v,cal)
    x=v['rpm_byte'];cell=x//16
    if x<240 and cal['wide_curve'][cell+1]<cal['wide_curve'][cell]:
        state.put(116,4,cal['wide_curve'][cell])
    state.put(123,1,independent['load_coordinate'])
    def axis(name,x,multiplier,base,stack,return_pc):
        cell,fraction=coordinate(cal[name],x,multiplier)
        if fraction:
            state.put(stack-4,4,return_pc);state.put(stack-8,4,0x26c78)
            state.sr=(state.sr&~0x301)|((1-(fraction&1))<<8)
        r[4],r[5]=cell,fraction
        return cell,fraction
    state.put(116,4,0x559ba);state.put(112,4,0xa9aa)
    row,rf=axis('row_axis',v['speed'],4,0x11cc0,112,0x26188)
    state.put(108,4,rf);state.put(104,4,row)
    column,cf=axis('column_axis',independent['load_coordinate'],1,0x11ac7,104,0x26198)
    state.put(116,4,incoming[8]);state.put(112,4,0x559ba)
    r[0],r[1],r[2],r[3]=row,rf,column,cf
    r[4],r[5]=0xa9aa+8*row+column,0xa9aa+8*(row+1)+column
    table=cal['surface'];top=table[row*8+column]
    if cf:
        top=state.linear(top,table[row*8+column+1],cf,112)
        if rf:
            state.put(108,4,top)
            bottom=state.linear(table[(row+1)*8+column],table[(row+1)*8+column+1],cf,108)
            top=state.linear(top,bottom,rf,112)
    elif rf:top=state.linear(top,table[(row+1)*8+column],rf,112)
    else:r[0]=signed(top,8)
    assert top==independent['surface_value'];state.put(124,4,top)
    if v['correction_flags']&64:
        state.put(116,4,0x559d4);state.put(112,4,0x12552)
        cell,fraction=axis('correction_axis',v['correction_coordinate'],1,0x11cd8,112,0x26482)
        value=state.linear(cal['correction_curve'][cell],cal['correction_curve'][cell+1],fraction,120)
        assert value==independent['correction_value'];state.macl=((top-128)*value)&MASK
    if v['rich_flags']&128:state.put(128,4,cal['rich_set'])
    r[0]=0x35f;r[2]=0x0100106a;r[4]=0x8b9b;r[5]=independent['latch_argument'];r[6]=0x01002464
    r[7]=independent['adjusted_value'] if independent['rich_on'] else MASK-127
    r[12]=0x0100128c;r[13]=0x0100119c;r[14]=signed(v['speed'],16)&MASK
    state.t(not independent['rich_on']);r[:]=[x&MASK for x in r]
    assert set(state.frame)<=set(range(96,160))
    return {**v,**independent,'variant':variant,'entry_sr':entry_sr,'expected_sr':state.sr,
            'expected_macl':state.macl,'incoming':incoming,'expected':r,'frame_writes':state.frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    for cal in range(8):
        for flags in (0,128):add(calibration=cal,rich_flags=flags,correction_flags=64,normalized=255,speed=65535)
    for speed in range(65536):
        add(speed=speed,normalized=(speed*29)&255,rpm_byte=(speed>>1)&255,
            load_threshold=(speed>>8)&255,wide_flags=(speed&8),correction_flags=(speed&64),
            correction_coordinate=(speed*13)&255,rich_flags=(speed&128))
    for normalized in range(256):
        for speed in (0,191,192,193,223,224,255,256,320,416,544,65535):
            add(normalized=normalized,speed=speed,load_threshold=0,calibration=3,
                correction_flags=64,correction_coordinate=normalized,rich_flags=normalized)
    for calibration in range(1,8):
        for value in range(256):
            add(calibration=calibration,normalized=value,rpm_byte=value,speed=value*3,
                wide_flags=value,rich_flags=value,load_threshold=value^255,
                correction_flags=value,correction_coordinate=value)
    for flag in range(256):
        add(wide_flags=flag,rich_flags=flag,correction_flags=flag,load_threshold=199,
            normalized=flag,correction_coordinate=flag,speed=255)
    for sr in range(128):
        entry=(sr&1)|((sr&30)<<3)|((sr&96)<<3)
        add(entry_sr=entry,speed=255 if sr&1 else 65535,correction_flags=64 if sr&2 else 0)
    assert len(rows)==70800
    assert {row['speed'] for row in rows}==set(range(65536))
    assert {row['entry_sr'] for row in rows}=={t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
    return rows

if __name__=='__main__':
    rows=matrix();print(f'ENRICHMENT_PREFIX cases={len(rows)} early=16 gnu_executed=0 accepted_points=0')
