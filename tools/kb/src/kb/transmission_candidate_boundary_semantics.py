"""Separate full signed completion bounds and boundary publications with physical data order."""
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed_word(raw):return raw-65536 if raw&32768 else raw

def evaluate(phase,memory,calibration):
    if type(phase) is not int or phase not in (0,1) or type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the transmission quantity equations need an exact phase and complete actual RAM')
    after=bytearray(memory);operands=[]
    def put(address,value,width=1):
        after[address:address+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
    def rom(address,size=1):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+size<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the transmission quantity equations lose a complete physical ROM operand')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the transmission equations change immutable calibration bytes')
        return raw[address-at:address-at+size]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        put(address,value,width)
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=bytes(after[address:address+width]).hex()))
    if phase==0:
        upper=signed_word(read(0x77804,0x3488,2,13))
        lower=signed_word(read(0x77808,0x348C,2,7))
        minimum=signed_word(read(0x7780C,0x3486,2,5))
        maximum=signed_word(read(0x77810,0x348A,2,14))
        mode=read(0x77812,0x83C1,1,0,'rom');candidate=None;active=False;selected_upper=False
        if not mode&1:
            select=read(0x7781C,0x89C5,1,0,'rom')&1
            flags=read(0x77822,0x41A6,1,0);active=bool(flags&8)
            if active:
                if select:
                    upper=signed_word(read(0x77832,0x4162,2,13));selected_upper=True
                else:upper=signed_word(read(0x77836,0x34A0,2,13))
                lower=signed_word(read(0x7783C,0x34C8,2,7))
                candidate=signed_word(read(0x77840,0x4162,2,6))
                lower=min(lower,candidate)
                minimum=signed_word(read(0x7784A,0x349C,2,5));maximum=minimum
            else:
                if not select:upper=signed_word(read(0x77856,0x34A0,2,13))
                cap=signed_word(read(0x7785A,0x34C8,2,2));lower=min(lower,cap)
        write(0x77866,0x3480,2,upper,13);write(0x7786A,0x3484,2,lower,7)
        write(0x7786E,0x347E,2,minimum,5);write(0x77872,0x3482,2,maximum,14)
        return dict(phase=phase,memory=bytes(after),operands=operands,upper=upper,lower=lower,
            minimum=minimum,maximum=maximum,candidate=candidate,active=active,selected_upper=selected_upper,
            shared_mode=mode,handoff={0x3480:upper&65535,0x3484:lower&65535,0x347E:minimum&65535,0x3482:maximum&65535})
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
    return dict(phase=phase,memory=bytes(after),operands=operands,value=published&65535,signed_value=published,
        direct=direct,publication_site=0x791A8 if direct else 0x791B2,
        publication_register=13 if direct else 7,final_signed=final_signed,cap=independent_cap,floor=floor,
        selected_request=selected_request,duplicated=duplicated,offset=offset,shared_mode=selection_mode)
