"""Separate complete stage equations and ordered signed request publication."""
from kb.arrogant_catfish_semantics import curve
from kb.counter_threshold_semantics import cell

RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed_word(raw):
    return raw-65536 if raw&32768 else raw

def caller(before,calibration):
    if type(before) is not bytes or len(before)!=65536 or type(calibration) is not dict:
        raise ValueError('the request equations need complete raw RAM and calibration bytes')
    after=bytearray(before)
    def byte(address):return after[address]
    def word(address):return int.from_bytes(after[address:address+2],'big')
    def put(address,value,width=1):
        after[address:address+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
    def rom(address,size=1):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+size<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the request equations lack an exact complete physical calibration span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the request equations replace immutable calibration bytes')
        return raw[address-at:address-at+size]
    mode=rom(0x8B38)[0]

    # Complete79358: the retained byte is clamped to [sample,sample+10],
    # then an optional actual integer division supplies the correction byte.
    sample=byte(0x1864);retained=max(sample,min(byte(0x186B),min(255,sample+10)))
    put(0x186B,retained)
    correction=(6-(6*retained)//255)*3 if mode&2 else 0
    put(0x336B,correction)

    # Complete793D2: four real hysteresis calls update their individual bits.
    lookup=curve(rom(0x12E1A,16),byte(0x106F));put(0x351B,lookup['value'])
    flags_a=byte(0x420A);flags_b=byte(0x420B)
    coordinate=byte(0x11B2);first_limit=lookup['value']+rom(0x8D37)[0]
    first=int(coordinate-(4 if flags_a&2 else 0)<=first_limit)
    flags_a=(flags_a&~2)|(first<<1);put(0x420A,flags_a)
    second=int(word(0x40C6)-(5 if flags_b&128 else 0)<=rom(0x8D3A)[0])
    flags_b=(flags_b&~128)|(second<<7);put(0x420B,flags_b)
    third=int(coordinate-(4 if flags_a&1 else 0)<=lookup['value'])
    flags_a=(flags_a&~1)|third;put(0x420A,flags_a)
    fourth_limit=lookup['value']+rom(0x8D36)[0]
    fourth=int(coordinate-(4 if flags_a&4 else 0)<=fourth_limit)
    flags_a=(flags_a&~4)|(fourth<<2);put(0x420A,flags_a)
    if byte(0x4184)&64 or byte(0x244F)&2 or flags_a&2 and flags_b&128 or flags_a&1:
        selected=0
    elif flags_a&4:
        selected=min(correction,rom(0x88C2)[0])
    else:
        selected=correction
    put(0x3368,selected)

    # Complete79538: all reset, latch, lower-knot selection and counter paths
    # operate on the state actually published by the preceding two stages.
    stage=max(selected,byte(0x2EC3));put(0x3369,stage)
    active=False;threshold=None;first_grid=None;second_grid=None;counter=None
    if not byte(0x4184)&128 or not byte(0x244F)&32:
        active=True;local=stage
    elif not byte(0x41E1)&1:
        if stage>=3:put(0x3448,min(byte(0x3448)+1,255))
        local=stage;elapsed=byte(0x3448)
        if elapsed>=rom(0x8CAB)[0] or elapsed!=0 and stage<3:
            put(0x41E1,byte(0x41E1)|1)
    else:
        local=max(stage,min(rom(0x884A)[0],18)) if stage>=3 and stage>=rom(0x8868)[0] else 0
        column=min(word(0x40C6)>>2,255);row=byte(0x11AE)
        first_grid=cell(rom(0xAAFA,16),rom(0x12FEE,4),rom(0x12FF2,4),row,column)
        second_grid=cell(rom(0xAAEA,16),rom(0x12FEE,4),rom(0x12FF2,4),row,column)
        put(0x351C,first_grid['value']);put(0x3449,second_grid['value'])
        counter=min(word(0x3446)+1,65535);put(0x3446,counter,2)
        threshold=max((byte(0x3448)*first_grid['value'])//10,second_grid['value'])
        active=counter>=threshold
    if active:
        put(0x41E1,byte(0x41E1)&~1);put(0x3448,0);put(0x3446,0,2)
    put(0x336A,local);quantity=local//3
    put(0x289C,quantity);put(0x2ECE,quantity)
    if byte(0x28CC)!=0 and quantity==0:put(0x43E9,rom(0x8423)[0])
    put(0x4204,(byte(0x4204)&~128)|(128 if quantity!=0 or byte(0x43E9)!=0 else 0))

    # Complete79030. Its operands and every publication are independently
    # ordered, preserving physical byte/word widths and the original registers.
    operands=[]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        put(address,value,width)
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=bytes(after[address:address+width]).hex()))

    flag=read(0x79044,0x41BB,1,6);state_flag=read(0x79046,0x4253,1,0)
    selected_request=signed_word(read(0x7904E,0x2438,2,4))
    duplicated=signed_word(read(0x79054,0x19C2,2,2))
    if duplicated<selected_request:
        upper_seed=duplicated;write(0x79064,0x41BB,1,flag|8,6)
    else:
        upper_seed=32767;write(0x7906E,0x41BB,1,flag&247,6)
    offset=min(signed_word(read(0x79074,0x34CA,2,6)),0)
    boundary_mode=read(0x79080,0x8B38,1,11,'rom')
    if boundary_mode&1:upper_seed=min(upper_seed,offset)
    upper_candidate=min(upper_seed,signed_word(read(0x790A2,0x34B8,2,6)))
    lower_seed=max(selected_request,offset) if boundary_mode&1 else selected_request
    independent_cap=signed_word(read(0x790C4,0x34BA,2,7))
    lower_candidate=min(lower_seed,independent_cap,signed_word(read(0x790D6,0x34B4,2,2)))
    joint=min(upper_candidate,lower_candidate);write(0x790EE,0x34A4,2,joint,6)
    selected_upper=upper_seed if boundary_mode&2 else upper_candidate
    write(0x790F8 if boundary_mode&2 else 0x7910C,0x2434,2,selected_upper,12 if boundary_mode&2 else 14)
    upper=max(selected_upper,signed_word(read(0x79114,0x3482,2,5)))
    upper=min(upper,signed_word(read(0x79122,0x347E,2,2)))
    selection_mode=read(0x7912C,0x83C1,1,9,'rom')
    if not selection_mode&32:upper=max(upper,signed_word(read(0x79138,0x413A,2,0)))
    write(0x7914A,0x19CC,2,upper,5)
    transmission=max(lower_candidate,signed_word(read(0x7914E,0x3484,2,5)))
    transmission=min(transmission,signed_word(read(0x7915C,0x3480,2,2)))
    lower_limit=signed_word(read(0x7916A,0x413A,2,0))
    upper_limit=signed_word(read(0x79178,0x4138,2,0))
    final_signed=min(max(transmission,lower_limit),upper_limit)
    floor=signed_word(read(0x79188,0x349A,2,14))
    capped=min(independent_cap,max(final_signed,floor))
    direct=bool(selection_mode&1);published=final_signed if direct else capped
    write(0x791A8 if direct else 0x791B2,0x19C6,2,published,13 if direct else 7)
    write(0x791C4,0x4253,1,(state_flag&239)|(16 if transmission>selected_request else 0),0)
    write(0x791E0,0x415E,2,max(min(joint,upper_limit),lower_limit),6)
    write(0x791F8,0x4160,2,max(min(selected_request,upper_limit),lower_limit),6)
    return dict(memory=bytes(after),operands=operands,value=published&65535,signed_value=published,
        direct=direct,publication_site=0x791A8 if direct else 0x791B2,
        publication_register=13 if direct else 7,final_signed=final_signed,cap=independent_cap,floor=floor,
        selected_request=selected_request,duplicated=duplicated,offset=offset,
        correction=correction,lookup=lookup,selected_stage=selected,stage=stage,local=local,retained=retained,
        hysteresis=(first,second,third,fourth),
        active=active,first_grid=first_grid,second_grid=second_grid,counter=counter,threshold=threshold,
        fault=bytes(after[0x9818:0x981C]))

def call_values(before,calibration,value):
    def raw(address,size=1):
        rows=[(at,data) for at,data in calibration.items() if at<=address and address+size<=at+len(data)]
        if len(rows)!=1:raise ValueError('the independent call equations lack a complete calibration operand')
        at,data=rows[0];return data[address-at:address-at+size]
    def word(address):return int.from_bytes(before[address:address+2],'big')
    def sxbyte(byte):return (byte-256 if byte&128 else byte)&MASK
    def call(target,arguments,returned):return dict(target=target,arguments=arguments,returned=returned)
    lookup_return=sxbyte(value['lookup']['value']) if before[0x106F]>=240 else value['lookup']['value']
    first,second,third,fourth=value['hysteresis']
    out={
        0x793F2:call(0x26388,{4:0x12E1A,5:before[0x106F]},{0:lookup_return}),
        0x79420:call(0x259D0,{4:before[0x11B2],5:value['lookup']['value']+raw(0x8D37)[0],6:4,7:int(bool(before[0x420A]&2))},{0:first}),
        0x79450:call(0x259D0,{4:word(0x40C6),5:raw(0x8D3A)[0],6:5,7:int(bool(before[0x420B]&128))},{0:second}),
        0x7947A:call(0x259D0,{4:before[0x11B2],5:value['lookup']['value'],6:4,7:before[0x420A]&1},{0:third}),
        0x794B4:call(0x259D0,{4:before[0x11B2],5:value['lookup']['value']+raw(0x8D36)[0],6:4,7:int(bool(before[0x420A]&4))},{0:fourth}),
        0x7977A:call(0x21BBC,{0:3,1:value['local']},{0:value['local']//3}),
    }
    if raw(0x8B38)[0]&2:
        out[0x793AE]=call(0x21BBC,{0:255,1:6*value['retained']},{0:(6*value['retained'])//255})
    if value['first_grid'] is not None:
        for site,table,grid in ((0x7969C,0xAAFA,value['first_grid']),(0x796E6,0xAAEA,value['second_grid'])):
            out[site]=call(0x260BC,{4:table,5:0x12FEE,6:0x12FF2,7:before[0x11AE]},{0:sxbyte(grid['value'])})
        dividend=before[0x3448]*value['first_grid']['value']
        out[0x79728]=call(0x21BBC,{0:10,1:dividend},{0:dividend//10})
    return out
