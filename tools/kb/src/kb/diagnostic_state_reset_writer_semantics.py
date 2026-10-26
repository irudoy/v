"""Independent reset equations, complete leaf/callee carriers and real stack effects."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000
NATIVE_BANKS=((0xFFFF8400,256),(0xFFFF9900,1792),(0xFFFFF500,256))


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def numerical(memory,calibration):
    if type(memory) is not bytes or len(memory)!=65536 or type(calibration.get(0x8DFC)) is not bytes or len(calibration[0x8DFC])!=2:
        raise ValueError('the reset equations require complete RAM and the two physical raw ROM bytes')
    ram=bytearray(memory);gate=bool(memory[0x41E1]&64)
    products=tuple(value*125 for value in calibration[0x8DFC])
    for first,last in ((0x9924,0x99D4),(0x99D8,0x99DA),(0x99DC,0x99FA),
            (0x8422,0x8424),(0x8462,0x8464),(0x9F08,0x9F0A),
            (0x3084,0x3087),(0x3088,0x308C),(0x30AC,0x30AF),
            (0x30B0,0x30F5),(0x30F8,0x30FC),(0x40BE,0x40BF),(0x2985,0x2986)):
        ram[first:last]=bytes(last-first)
    ram[0x2B96]=255
    for address,mask in ((0x4232,0xDF),(0x4198,0xEF),(0x41DE,0xFA),(0x41A4,0x9F),
            (0x4251,0xFE),(0x41F2,0xBF),(0x41FC,0x7F),(0x41FE,0xFD),
            (0x41B9,0x07),(0x41BA,0x6F),(0x41BB,0xFB),(0x41E1,0x9F),(0x41F5,0xF7),(0x9A6B,0x3F)):
        ram[address]&=mask
    if gate:
        for address,value in ((0xF588,products[0]),(0xF58A,products[0]),(0xF58C,products[1]),(0xF58E,products[1]),
                (0xF590,0),(0xF592,0),(0xF594,0),(0xF596,0)):
            ram[address:address+2]=value.to_bytes(2,'big')
    return dict(ram=bytes(ram),gate=gate,raw_rom=tuple(calibration[0x8DFC]),products=products,
        target_before=memory[0x99DE],target_after=ram[0x99DE],callee_argument=memory[0x40BE])


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x2E81A or type(memory) is not bytes or len(memory)!=65536
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or not 0<=sr_before<=MASK or sr_before&0x3F1!=context[18]
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(sp) is not int or not 160<=sp<=MASK-32 or sp&3
            or type(continuation) is not int or not 0<=continuation<=MASK):
        raise ValueError('the reset equations omit a complete typed natural entry, CPU, frame or RAM')
    value=numerical(memory,calibration)
    r=[*context[:15],sp];gbr,mach,macl=context[15:18];sr=sr_before;pr=continuation
    ram=bytearray(memory);frame=bytearray(frame_before);steps=[];operands=[];branches=[];calls=[];pending_call=None
    def snapshot():return dict(registers=tuple(r),gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr)
    def emit(site,updates=None,*,t=None,new_gbr=None,new_macl=None,new_pr=None,events=(),control=None,delay=False):
        nonlocal sr,gbr,macl,pr,pending_call
        before=snapshot()
        for register,raw in (updates or {}).items():r[register]=raw&MASK
        if t is not None:sr=(sr&~1)|int(bool(t))
        if new_gbr is not None:gbr=new_gbr&MASK
        if new_macl is not None:macl=new_macl&MASK
        if new_pr is not None:pr=new_pr&MASK
        row=dict(site=site,before=before,after=snapshot(),branches=[],accesses=[],calls=[],delay_slot=delay)
        for mode,address,width,register,domain,raw in events:
            event=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())
            operands.append(event);row['accesses'].append(dict(event))
        if control is not None:
            kind,target,delayed=control;branch=dict(site=site,kind=kind,target=target,delay=delayed)
            branches.append(branch);row['branches']=[branch]
            if kind=='call':
                calls.append(dict(site=site,target=target,return_address=pr,sp=r[15],registers=tuple(r[:15]),
                    gbr=gbr,mach=mach,macl=macl,sr=sr));pending_call=len(calls)-1
                row['calls']=[dict(calls[-1])]
        if delay and pending_call is not None:
            calls[pending_call]['entry']=dict(registers=tuple(r[:15]),sp=r[15],gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr)
            pending_call=None
        steps.append(row)
    def condition(site,taken,target,delayed=False):
        emit(site,control=('taken' if taken else 'fallthrough',target if taken else site+(4 if delayed else 2),delayed))
    def rom(site,address,width,register):
        pieces=[raw[address-at:address-at+width] for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(pieces)!=1:raise ValueError('the reset equations omit a unique complete physical ROM operand')
        raw=pieces[0];integer=int.from_bytes(raw,'big');integer=signed(integer,width*8) if width<4 else integer
        emit(site,{register:integer},events=(('read',address,width,register,'rom',raw),))
    def read(site,address,width,register,*,native=False):
        offset=address&65535 if native else address-RAM_BASE
        if not 0<=offset<=65536-width:raise ValueError('the reset equations leave complete logical RAM')
        raw=bytes(ram[offset:offset+width]);integer=int.from_bytes(raw,'big');integer=signed(integer,width*8) if width<4 else integer
        emit(site,{register:integer},events=(('read',address,width,register,'native-io' if native else 'ram',raw),))
    def put(site,address,width,integer,register,*,native=False,stack=False,updates=None,delay=False):
        offset=160+address-sp if stack else address&65535 if native else address-RAM_BASE
        storage=frame if stack else ram
        if not 0<=offset<=len(storage)-width:raise ValueError('the reset equations write outside a complete frame or RAM image')
        raw=(integer&((1<<(width*8))-1)).to_bytes(width,'big');storage[offset:offset+width]=raw
        emit(site,updates,events=(('write',address,width,register,'frame' if stack else 'native-io' if native else 'ram',raw),),delay=delay)
    def push(site,integer,register):put(site,r[15]-4,4,integer,register,stack=True,updates={15:r[15]-4})
    def pop(site,register=None,*,special=None,delay=False):
        address=r[15];offset=160+address-sp;raw=bytes(frame[offset:offset+4]);integer=int.from_bytes(raw,'big')
        updates={15:address+4}
        if register is not None:updates[register]=integer
        emit(site,updates,new_gbr=integer if special=='gbr' else None,new_macl=integer if special=='macl' else None,
            new_pr=integer if special=='pr' else None,events=(('read',address,4,register,'frame',raw),),delay=delay)
    def and_byte(site,address,mask):
        offset=address-RAM_BASE;before=bytes([ram[offset]]);after=bytes([ram[offset]&mask]);ram[offset]=after[0]
        emit(site,events=(('read',address,1,None,'ram',before),('write',address,1,None,'ram',after)))

    push(0x2E81A,context[14],14);push(0x2E81C,pr,None);push(0x2E81E,gbr,None)
    rom(0x2E820,0x2E90C,4,0);emit(0x2E822,new_gbr=r[0])
    emit(0x2E824,new_pr=0x2E828,control=('call',0x2E76E,True));emit(0x2E826,delay=True)

    rom(0x2E76E,0x2E780,2,1);emit(0x2E770,{6:0});emit(0x2E772,{7:r[6]})
    emit(0x2E774,{4:4});emit(0x2E776,{5:r[1]})
    for index in range(4):
        emit(0x2E778,{6:r[6]+1});put(0x2E77A,r[5],1,r[7],7,native=True)
        emit(0x2E77C,control=('jump',0x2E782,True));emit(0x2E77E,{6:r[6]&255},delay=True)
        emit(0x2E782,t=r[6]>=r[4]);condition(0x2E784,index<3,0x2E778,True)
        emit(0x2E786,{5:r[5]+1},delay=True)
    for setup,add,zero,body in ((0x2E788,4,0x2E78C,0x2E78E),
            (0x2E79A,8,0x2E79E,0x2E7A0),(0x2E7AC,12,0x2E7B0,0x2E7B2)):
        emit(setup,{5:r[1]});emit(setup+2,{5:r[5]+add});emit(zero,{6:0})
        for index in range(4):
            emit(body,{6:r[6]+1});put(body+2,r[5],1,r[7],7,native=True);emit(body+4,{6:r[6]&255})
            emit(body+6,t=r[6]>=r[4]);condition(body+8,index<3,body,True);emit(body+10,{5:r[5]+1},delay=True)
    for load,pool,zero,bound,body,count in ((0x2E7BE,0x2E8BE,0x2E7C0,0x2E7C2,0x2E7C4,32),
            (0x2E7D0,0x2E8C0,0x2E7D2,None,0x2E7D4,32),(0x2E7E0,0x2E8C2,0x2E7E2,None,0x2E7E4,32),
            (0x2E7F0,0x2E8C4,0x2E7F2,0x2E7F4,0x2E7F6,64)):
        rom(load,pool,2,5);emit(zero,{6:0})
        if bound is not None:emit(bound,{4:count})
        for index in range(count):
            emit(body,{6:r[6]+1});put(body+2,r[5],1,r[7],7,native=True);emit(body+4,{6:r[6]&255})
            emit(body+6,t=r[6]>=r[4]);condition(body+8,index<count-1,body,True);emit(body+10,{5:r[5]+1},delay=True)
    rom(0x2E802,0x2E904,4,6);emit(0x2E804,{2:-1});rom(0x2E806,0x2E8C6,2,0)
    put(0x2E808,r[6]+r[0],1,r[2],2);emit(0x2E80A,{0:21});rom(0x2E80C,0x2E908,4,6)
    read(0x2E80E,r[6]+r[0],1,0);emit(0x2E810,{0:r[0]&0xDF});emit(0x2E812,{2:r[0]});emit(0x2E814,{0:21})
    emit(0x2E816,control=('return',pr,True));put(0x2E818,r[6]+r[0],1,r[2],2,delay=True)

    rom(0x2E828,0x2E8C8,2,5);emit(0x2E82A,{6:0});emit(0x2E82C,{14:r[6]});emit(0x2E82E,{7:6})
    emit(0x2E830,{4:r[5]});emit(0x2E832,{4:r[4]+28})
    for index in range(6):
        emit(0x2E834,{6:r[6]+1});put(0x2E836,r[4],1,r[14],14,native=True);emit(0x2E838,{6:r[6]&255})
        emit(0x2E83A,t=r[6]>=r[7]);condition(0x2E83C,index<5,0x2E834,True);emit(0x2E83E,{4:r[4]+1},delay=True)
    emit(0x2E840,{4:r[5]});emit(0x2E842,{4:r[4]+4});emit(0x2E844,{6:0});emit(0x2E846,{7:24})
    for index in range(24):
        emit(0x2E848,{6:r[6]+1});put(0x2E84A,r[4],1,r[14],14,native=True);emit(0x2E84C,{6:r[6]&255})
        emit(0x2E84E,t=r[6]>=r[7]);condition(0x2E850,index<23,0x2E848,True);emit(0x2E852,{4:r[4]+1},delay=True)
    emit(0x2E854,{6:0});emit(0x2E856,{4:2})
    for index in range(2):
        emit(0x2E858,{6:r[6]+1});put(0x2E85A,r[5],1,r[14],14,native=True);emit(0x2E85C,{6:r[6]&255})
        emit(0x2E85E,t=r[6]>=r[4]);condition(0x2E860,index<1,0x2E858,True);emit(0x2E862,{5:r[5]+1},delay=True)
    rom(0x2E864,0x2E8CA,2,6);rom(0x2E866,0x2E910,4,5);read(0x2E868,r[6],1,0,native=True)
    rom(0x2E86A,0x2E914,4,2);emit(0x2E86C,{0:r[0]&63});put(0x2E86E,r[6],1,r[0],0,native=True)
    emit(0x2E870,{0:0});rom(0x2E872,0x2E8CC,2,6);put(0x2E874,r[6]+1,1,r[0],0,native=True)
    put(0x2E876,r[6],1,r[0],0,native=True);rom(0x2E878,0x2E8CE,2,6)
    put(0x2E87A,r[6]+1,1,r[0],0,native=True);put(0x2E87C,r[6],1,r[0],0,native=True)
    emit(0x2E87E,{0:4});and_byte(0x2E880,gbr+r[0],0xEF);read(0x2E882,r[5]+10,1,0)
    emit(0x2E884,new_pr=0x2E888,control=('call',0xCD75C,True));emit(0x2E886,{4:r[0]&255},delay=True)

    push(0xCD75C,r[14],14);push(0xCD75E,macl,None);push(0xCD760,gbr,None)
    rom(0xCD762,0xCDAC0,4,0);emit(0xCD764,new_gbr=r[0]);emit(0xCD766,{2:-88})
    rom(0xCD768,0xCDAC4,4,14);emit(0xCD76A,{0:r[2]&255});rom(0xCD76C,0xCD844,2,7)
    and_byte(0xCD76E,gbr+r[0],0xFE);emit(0xCD770,{0:53});and_byte(0xCD772,gbr+r[0],0xFB)
    emit(0xCD774,{0:8});emit(0xCD776,{4:0});emit(0xCD778,{0:r[0]<<8});emit(0xCD77A,{5:r[4]})
    put(0xCD77C,r[14]+r[0],4,r[4],4);emit(0xCD77E,{1:32})
    for load,pool,store,width in ((0xCD780,0xCD846,0xCD782,2),(0xCD784,0xCD848,0xCD786,2),
            (0xCD788,0xCD84A,0xCD78A,1),(0xCD78C,0xCD84C,0xCD78E,2),
            (0xCD790,0xCD84E,0xCD792,2),(0xCD794,0xCD850,0xCD796,2),
            (0xCD798,0xCD852,0xCD79A,2),(0xCD79C,0xCD854,0xCD79E,1),(0xCD7A0,0xCD856,0xCD7A2,1)):
        rom(load,pool,2,0);put(store,r[14]+r[0],width,r[4],4)
    for index in range(32):
        emit(0xCD7A4,{6:r[14]});emit(0xCD7A6,{2:r[7]});emit(0xCD7A8,{6:r[6]+r[7]})
        emit(0xCD7AA,{0:r[5]&255});emit(0xCD7AC,{2:r[2]+32});put(0xCD7AE,r[6]+r[0],1,r[4],4)
        emit(0xCD7B0,{6:r[14]});emit(0xCD7B2,{6:r[6]+r[2]});put(0xCD7B4,r[6]+r[0],1,r[4],4)
        emit(0xCD7B6,{0:r[0]+1});emit(0xCD7B8,{5:r[0]&255});emit(0xCD7BA,t=signed(r[5],32)>=signed(r[1],32))
        condition(0xCD7BC,index<31,0xCD7A4)
    rom(0xCD7BE,0xCD858,2,6);emit(0xCD7C0,{0:0});emit(0xCD7C2,{14:16})
    put(0xCD7C4,r[6],1,r[0],0,native=True);emit(0xCD7C6,{2:17});put(0xCD7C8,r[6]+1,1,r[0],0,native=True)
    for move,register,raw,store,mask in ((0xCD7CA,0,73,0xCD7CC,0xBF),(0xCD7CE,0,83,0xCD7D0,0x7F),
            (0xCD7D2,0,85,0xCD7D4,0xFD),(0xCD7D6,14,None,0xCD7D8,0x5F),
            (0xCD7DA,2,None,0xCD7DC,0xEF),(0xCD7DE,14,None,0xCD7E0,0xBF),
            (0xCD7E2,2,None,0xCD7E4,0x7F),(0xCD7E6,14,None,0xCD7E8,0xEF),
            (0xCD7EA,0,18,0xCD7EC,0xFB),(0xCD7EE,14,None,0xCD7F0,0xF7),
            (0xCD7F2,0,56,0xCD7F4,0xDF),(0xCD7F6,0,76,0xCD7F8,0xF7)):
        emit(move,{0:r[register] if raw is None else raw});and_byte(store,gbr+r[0],mask)
    read(0xCD7FA,gbr+56,1,0);emit(0xCD7FC,t=not value['gate']);condition(0xCD7FE,not value['gate'],0xCD83C)
    if value['gate']:
        rom(0xCD800,0xCDAC8,4,7);emit(0xCD802,{4:125});rom(0xCD804,0xCD85A,2,6)
        rom(0xCD806,r[7],1,2);emit(0xCD808,{5:r[2]&255});emit(0xCD80A,new_macl=(r[5]&65535)*(r[4]&65535))
        emit(0xCD80C,{5:0});emit(0xCD80E,{2:macl});emit(0xCD810,{0:r[2]})
        put(0xCD812,r[6]+8,2,r[0],0,native=True);emit(0xCD814,{0:r[5]});put(0xCD816,r[6]+16,2,r[0],0,native=True)
        emit(0xCD818,{0:r[2]});put(0xCD81A,r[6]+10,2,r[0],0,native=True)
        emit(0xCD81C,{0:r[5]});put(0xCD81E,r[6]+18,2,r[0],0,native=True)
        rom(0xCD820,r[7]+1,1,0);emit(0xCD822,{7:r[0]&255});emit(0xCD824,new_macl=(r[7]&65535)*(r[4]&65535))
        emit(0xCD826,{2:macl});emit(0xCD828,{0:r[2]});put(0xCD82A,r[6]+12,2,r[0],0,native=True)
        emit(0xCD82C,{0:r[5]});put(0xCD82E,r[6]+20,2,r[0],0,native=True)
        emit(0xCD830,{0:r[2]});put(0xCD832,r[6]+14,2,r[0],0,native=True)
        emit(0xCD834,{0:r[5]});put(0xCD836,r[6]+22,2,r[0],0,native=True)
        emit(0xCD838,{0:56});and_byte(0xCD83A,gbr+r[0],0xBF)
    pop(0xCD83C,special='gbr');pop(0xCD83E,special='macl');emit(0xCD840,control=('return',pr,True));pop(0xCD842,14,delay=True)

    rom(0x2E888,0x2E910,4,5);emit(0x2E88A,{0:0});rom(0x2E88C,0x2E904,4,6);emit(0x2E88E,{2:0})
    put(0x2E890,r[5]+10,1,r[0],0);emit(0x2E892,{0:74});and_byte(0x2E894,gbr+r[0],0xFE)
    emit(0x2E896,{0:16});and_byte(0x2E898,gbr+r[0],0x9F);emit(0x2E89A,{0:-115});emit(0x2E89C,{0:r[0]&255})
    put(0x2E89E,r[6]+r[0],1,r[2],2);pop(0x2E8A0,special='gbr');pop(0x2E8A2,special='pr')
    emit(0x2E8A4,control=('return',pr,True));pop(0x2E8A6,14,delay=True)
    for index,row in enumerate(steps):row['next']=steps[index+1]['site'] if index+1<len(steps) else continuation
    if bytes(ram)!=value['ram'] or pending_call is not None:
        raise ValueError('the complete reset carrier equations disagree with independent byte/word reset equations')
    ordinary=bytearray(ram)
    for start,size in NATIVE_BANKS:
        at=start&65535;ordinary[at:at+size]=memory[at:at+size]
    return dict(value,entry=entry,registers=tuple(r[:15]),gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr,sp=r[15],
        ram=bytes(ram),ordinary_ram=bytes(ordinary),native_after=b''.join(ram[start&65535:(start&65535)+size] for start,size in NATIVE_BANKS),
        frame=bytes(frame),steps=steps,path=tuple(row['site'] for row in steps),operands=operands,branches=branches,calls=calls,
        exit=(sr,pr,macl,mach,gbr,*reversed(r[:15])))
