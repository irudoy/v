"""Independent common-gain equations and exact real-helper observations."""
from stock_injection_end_angle_model import State

MASK=0xffffffff
BYTE_INPUTS=(('flags',0x2485),('diagnostic',0x5aa3),('correction',0x2733),('rpm',0x11b3))
WORD_INPUTS=(('pressure_input',0x4524),('bfs',0x1024))
CALIBRATIONS=(('a_floor',0x83c4,1),('factor_low',0x83c5,1),('factor_high',0x83c6,1),
    ('pressure_slope',0x89fe,1),('pressure_offset',0x93c6,2),('constant_correction',0x8b51,1),
    ('ratio_constant',0x8ae7,1),('gain_scalar',0x9332,2))
TABLES=(('load_curve',0x129e2,16),('rpm_curve',0x129f2,16))
DEFAULTS={'flags':8,'diagnostic':0,'correction':70,'rpm':100,'pressure_input':32768,
    'bfs':32768,'a_floor':128,'factor_low':51,'factor_high':215,'pressure_slope':0,
    'pressure_offset':0xca99,'constant_correction':75,'ratio_constant':175,'gain_scalar':0x3694,
    'load_curve':tuple(bytes.fromhex('22364a5e72869aaec2d6eaffffffffff')),
    'rpm_curve':tuple(bytes.fromhex('211a120e0b0b05040803000000000000'))}
OUTPUTS=(('updated_flags',0x2485,1),('pressure_word',0x517c,2),('coordinate',0x13b1,1),
    ('load_value',0x17ba,1),('rpm_value',0x17bb,1),('curve_sum',0x17b9,1),
    ('load_word',0x31d8,2),('ratio_byte',0x17ee,1),('affine_byte',0x160d,1),('gain_word',0x165e,2))

def signed(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value

def lookup(table,x):
    assert 0<=x<=255 and len(table)==16
    if x>=240:return table[15]
    cell,remainder=divmod(x,16);left,right=table[cell:cell+2]
    delta=abs(right-left)*remainder//16
    return left+delta if right>=left else left-delta

def arithmetic(v):
    active=bool(v['flags']&8)
    output={'updated_flags':v['flags']^8,'active':active}
    if not active:return output
    p=v['pressure_input']*v['pressure_slope']//128+v['pressure_offset']
    c=v['constant_correction'] if v['diagnostic']&128 else v['correction']
    q1=p*256//0xca99;a=max(v['a_floor'],min(256,q1))
    q2=0x12a00//(c+223);low=v['factor_low']+128;high=v['factor_high']+128
    factor=low if q2<low else (high if q2>high else q2)
    coordinate=min(255,(factor*((a*v['bfs'])//256))//32768)
    load_value=lookup(v['load_curve'],coordinate);rpm_value=lookup(v['rpm_curve'],v['rpm'])
    curve_sum=min(255,load_value+rpm_value)
    load_word=min(65535,p*(256-curve_sum)//256)
    den=v['ratio_constant']*1024+load_word
    quotient=v['ratio_constant']*262144//den if den else 0
    ratio=min(255,quotient)
    affine=(ratio*0x148b+0x128500)//0x2710
    assert affine<=255 and p<=196093 and a<=256 and factor<=383
    output.update(raw_pressure=p,pressure_word=min(65535,p),correction_selected=c,q1=q1,a=a,q2=q2,
        factor=factor,coordinate=coordinate,load_value=load_value,rpm_value=rpm_value,curve_sum=curve_sum,
        load_word=load_word,ratio_denominator=den,ratio_quotient=quotient,ratio_byte=ratio,
        affine_byte=affine,gain_word=affine*v['gain_scalar']//256)
    return output

def case(index,variant=None,entry_sr=None,**changes):
    v={**DEFAULTS,**changes};assert set(v)==set(DEFAULTS)
    for name,_ in BYTE_INPUTS:assert 0<=v[name]<=255
    for name,_ in WORD_INPUTS:assert 0<=v[name]<=65535
    for name,_,size in CALIBRATIONS:assert 0<=v[name]<(1<<(8*size))
    for name,_,size in TABLES:
        v[name]=tuple(v[name]);assert len(v[name])==size and all(0<=x<=255 for x in v[name])
    variant=index&1 if variant is None else variant
    entry_sr=(index&1)|(((index>>1)&15)<<4)|((index&3)<<8) if entry_sr is None else entry_sr
    assert variant in (0,1) and not entry_sr&~0x3f1
    incoming=[((0x1728394a+r*0x110203) if variant==0 else (0x81234567+r*0x1020305))&MASK for r in range(15)]
    macl=0x9274b6d8 if variant else 0x2468ace0
    state=State(incoming,macl,entry_sr);r=state.r
    for at,value in ((156,incoming[12]),(152,incoming[13]),(148,incoming[14]),(140,macl)):state.put(at,4,value)
    expected=arithmetic(v)
    if not expected['active']:
        r[0]=0x15;r[5]=0x01002470;r[6]=(signed(v['flags'],8)|8)&MASK;state.t(True)
    else:
        p,a,c=expected['raw_pressure'],expected['a'],expected['correction_selected']
        for at,value in ((124,p),(128,v['pressure_offset']),(132,c),(136,a)):state.put(at,4,value)
        if expected['q1']>=256 or expected['q2']>=256:state.put(116,4,incoming[3])
        state.macl=(a*v['bfs']//256)*expected['factor']
        def implicit16(table,base,x):
            r[0],r[5],r[6]=240,x,0x26388
            if x>=240:r[0]=signed(table[15],8);return table[15]
            cell,rem=divmod(x,16);fraction=rem*4096
            r[4],r[5],r[6]=base+cell,cell,0x26740
            value=state.linear(table[cell],table[cell+1],fraction,124)
            assert value==lookup(table,x);return value
        implicit16(v['load_curve'],0x129e2,expected['coordinate'])
        implicit16(v['rpm_curve'],0x129f2,v['rpm'])
        den=expected['ratio_denominator'];quot=expected['ratio_quotient']
        if den and den<=65535 and quot>=256:state.put(116,4,r[3])
        numerator=expected['ratio_byte']*0x148b+0x128500;divisor=0x2710
        quotient,remainder=divmod(numerator,divisor)
        assert quotient==expected['affine_byte'] and quotient<256
        r[0]=0x3d2
        r[1]=((remainder-(divisor if quotient%2==0 else 0))*512+256+quotient)&MASK
        r[2]=expected['gain_word'];r[4]=expected['load_word'];r[5]=0x9332;r[6]=0;r[7]=p
        state.put(120,4,expected['ratio_byte'])
        state.sr=(entry_sr&~0x301)|((1-(quotient&1))<<8)
    r[:]=[x&MASK for x in r]
    return {**v,**expected,'variant':variant,'entry_sr':entry_sr,'expected_sr':state.sr,
            'incoming':incoming,'expected':r,'frame_writes':state.frame}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    early=(
        {},{'flags':0},{'flags':255,'diagnostic':128},
        {'pressure_offset':0,'ratio_constant':0,'bfs':0},
        {'pressure_offset':0,'ratio_constant':1,'load_curve':(0,)*16,'rpm_curve':(0,)*16},
        {'pressure_input':65535,'pressure_slope':255,'pressure_offset':65535},
        {'load_curve':(255,)*16,'rpm_curve':(255,)*16},
        {'rpm':255,'bfs':65535},
        {'factor_low':255,'factor_high':0,'correction':0},
        {'factor_low':0,'factor_high':255,'correction':255},
        {'gain_scalar':0}, {'gain_scalar':65535},
        {'flags':128}, {'flags':136,'diagnostic':255,'constant_correction':255},
        {'bfs':0,'rpm':0,'pressure_offset':1,'ratio_constant':255},
        {'bfs':65535,'rpm':239,'load_curve':tuple(reversed(range(0,256,16)))})
    for value in early:add(**value)
    for bfs in range(65536):add(bfs=bfs,rpm=(bfs*37)&255,correction=(bfs>>8)&255)
    for flags in range(256):
        for variant in range(2):add(flags=flags,diagnostic=flags,rpm=flags,variant=variant)
    bounds=(0,1,127,128,255,256,32767,32768,51864,51865,65534,65535)
    for pressure in bounds:
        for slope in (0,1,127,128,254,255):
            for offset in (0,1,32767,32768,51865,65535):
                add(pressure_input=pressure,pressure_slope=slope,pressure_offset=offset,
                    bfs=65535,rpm=(pressure*17)&255)
    curves=((0,)*16,(255,)*16,tuple(range(0,256,16)),tuple(reversed(range(0,256,16))),
            tuple(255 if i&1 else 0 for i in range(16)))
    for curve in curves:
        for x in range(256):
            add(load_curve=curve,rpm_curve=curve,rpm=x,bfs=min(65535,x*256),
                a_floor=255,factor_low=255,factor_high=255,ratio_constant=x)
    for c in range(256):
        for low,high in ((0,255),(255,0),(128,128)):
            add(correction=c,factor_low=low,factor_high=high,diagnostic=0,
                constant_correction=c^255,bfs=65535)
    for k in (0,1,2,63,64,65,127,128,175,254,255):
        for load in (0,1,255,256,65535):
            add(ratio_constant=k,pressure_offset=load,pressure_slope=0,
                load_curve=(0,)*16,rpm_curve=(0,)*16,bfs=0)
    for sr in range(128):
        entry=(sr&1)|((sr&30)<<3)|((sr&96)<<3)
        for flags in (0,8):add(entry_sr=entry,flags=flags)
    assert len(rows)<72000
    assert {row['entry_sr'] for row in rows}=={t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
    assert {row['bfs'] for row in rows if row['active']}==set(range(65536))
    return rows

if __name__=='__main__':
    rows=matrix();print(f'COMMON_GAIN cases={len(rows)} early=16 gnu_executed=0 accepted_points=0')
