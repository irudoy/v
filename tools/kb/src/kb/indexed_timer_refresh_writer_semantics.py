"""Independent indexed latch/timer transitions, SR interrupt discipline and complete leaf carriers."""
MASK=0xFFFFFFFF
SR_ARCH_MASK=0x0FFF0FFF
RAM_BASE=0x01000000
NATIVE_START=0xFFFF8500
INDICES=(*range(256),0xFFFFFFFF)


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x9018C or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(raw) is not int or not 0<=raw<=MASK for raw in context)
            or context[4] not in INDICES or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the timer equations require complete exact CPU/frame/RAM and explicit software index inputs')
    r=[*context[:15],sp];ram=bytearray(memory);frame=bytearray(frame_before)
    gbr=context[15];sr=sr_before;steps=[];operands=[];branches=[];critical=[]
    def snapshot():return dict(registers=tuple(r),gbr=gbr,mach=context[16],macl=context[17],sr=sr,pr=continuation)
    def emit(site,updates=None,*,t=None,new_sr=None,new_gbr=None,event=None,control=None,delay=False):
        nonlocal sr,gbr
        before=snapshot()
        for register,value in (updates or {}).items():r[register]=value&MASK
        if t is not None:sr=(sr&~1)|int(bool(t))
        if new_sr is not None:sr=new_sr&SR_ARCH_MASK
        if new_gbr is not None:gbr=new_gbr&MASK
        row=dict(site=site,before=before,after=snapshot(),branches=[],delay_slot=delay)
        if event is not None:
            mode,address,width,register,domain,raw=event
            operands.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        if control is not None:
            kind,target,delayed=control;branch=dict(site=site,kind=kind,target=target,delay=delayed)
            branches.append(branch);row['branches']=[branch]
        steps.append(row)
    def condition(site,taken,target,delayed=False):
        emit(site,control=('taken' if taken else 'fallthrough',target if taken else site+(4 if delayed else 2),delayed))
    def pool(site,address,width,register):
        pieces=[raw[address-at:address-at+width] for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(pieces)!=1:raise ValueError('the timer equations omit one unique complete physical ROM operand')
        raw=pieces[0];value=int.from_bytes(raw,'big');value=signed(value,width*8) if width<4 else value
        emit(site,{register:value},event=('read',address,width,register,'rom',raw));return value&MASK
    def load(site,address,register,*,domain='ram'):
        offset=(address&65535) if domain=='native-control' else address-RAM_BASE
        if not 0<=offset<65536:raise ValueError('the timer equations leave complete declared logical RAM')
        raw=bytes([ram[offset]]);value=signed(raw[0],8)
        emit(site,{register:value},event=('read',address,1,register,domain,raw));return value&MASK
    def put(site,address,value,register,*,domain='ram',delay=False,updates=None):
        offset=(address&65535) if domain=='native-control' else address-RAM_BASE
        if not 0<=offset<65536:raise ValueError('the timer equations write outside complete declared logical RAM')
        raw=bytes([value&255]);ram[offset]=raw[0]
        emit(site,updates,event=('write',address,1,register,domain,raw),delay=delay)
    def frame_write(site,address,value,register,updates=None):
        offset=160+address-sp;raw=(value&MASK).to_bytes(4,'big');frame[offset:offset+4]=raw
        emit(site,updates,event=('write',address,4,register,'frame',raw))
    index=context[4];mask=(index+1)&MASK;timer=(RAM_BASE+0x43B8+index)&MASK
    enabled=context[5]!=0;blocked=bool(memory[0x3581]&mask)
    armed=bool(memory[0x4179]&mask);other=bool(memory[0x4178]&mask)
    indicator=bool(mask&((memory[0x850D]>>4)&3));live=memory[timer-RAM_BASE]!=0
    refreshed=False;judged=False;raised=False;temporary=False
    frame_write(0x9018C,sp-4,context[14],14,{15:sp-4})
    frame_write(0x9018E,sp-8,context[15],None,{15:sp-8})
    pool(0x90190,0x90400,4,0);emit(0x90192,new_gbr=r[0]);emit(0x90194,{15:sp-12})
    pool(0x90196,0x90404,4,1);emit(0x90198,{7:index});pool(0x9019A,0x90250,2,0)
    emit(0x9019C,{4:mask});emit(0x9019E,{14:index})
    load(0x901A0,RAM_BASE+0x3581,2);emit(0x901A2,{6:memory[0x3581]});emit(0x901A4,t=not blocked)
    condition(0x901A6,blocked,0x90240,True);emit(0x901A8,{14:mask},delay=True)
    if blocked:
        load(0x90240,RAM_BASE+0x4179,0);emit(0x90242,{2:~mask});emit(0x90244,{0:r[0]&r[2]})
        put(0x90246,RAM_BASE+0x4179,r[0],0)
    else:
        emit(0x901AA,t=not enabled);condition(0x901AC,not enabled,0x90224)
        if not enabled:
            load(0x90224,RAM_BASE+0x4179,0);emit(0x90226,{2:~mask})
            frame_write(0x90228,sp-12,r[0],0);temporary=True
            emit(0x9022A,{0:r[0]&r[2]});put(0x9022C,RAM_BASE+0x4179,r[0],0)
        else:
            load(0x901AE,RAM_BASE+0x4179,0);emit(0x901B0,{5:memory[0x4179]});emit(0x901B2,t=not armed)
            condition(0x901B4,armed,0x901F4)
            if not armed:
                load(0x901B6,RAM_BASE+0x4178,0);emit(0x901B8,{2:memory[0x4178]});emit(0x901BA,t=not other)
                condition(0x901BC,other,0x901F4)
            if not armed and not other:
                original_sr=sr;interrupt=(sr>>4)&15
                emit(0x901BE,{0:sr});emit(0x901C0,{0:r[0]>>2});emit(0x901C2,{0:r[0]>>2})
                emit(0x901C4,{0:r[0]&15});emit(0x901C6,{2:interrupt});emit(0x901C8,{0:sr})
                pool(0x901CA,0x90252,2,3);emit(0x901CC,{0:r[0]&r[3]});emit(0x901CE,{0:r[0]|240})
                emit(0x901D0,new_sr=r[0]);critical.append((0x901D0,sr))
                emit(0x901D2,{5:r[5]|mask});emit(0x901D4,{0:r[5]});pool(0x901D6,0x90254,2,5)
                put(0x901D8,RAM_BASE+0x4179,r[0],0)
                load(0x901DA,0xFFFF850C,0,domain='native-control');emit(0x901DC,{0:r[0]|128})
                put(0x901DE,0xFFFF850C,r[0],0,domain='native-control');raised=True
                emit(0x901E0,{0:interrupt});emit(0x901E2,{0:r[0]&15})
                emit(0x901E4,{0:r[0]<<2});emit(0x901E6,{0:r[0]<<2});emit(0x901E8,{2:sr})
                emit(0x901EA,{2:r[2]&r[3]});emit(0x901EC,{2:r[2]|r[0]});emit(0x901EE,new_sr=r[2])
                critical.append((0x901EE,sr))
                if sr!=original_sr:raise ValueError('the timer scalar equation fails its exact interrupt-field restoration')
                emit(0x901F0,control=('jump',0x901FC,True));emit(0x901F2,delay=True)
            else:
                emit(0x901F4,{5:r[5]|mask});emit(0x901F6,{0:r[5]});pool(0x901F8,0x90254,2,5)
                put(0x901FA,RAM_BASE+0x4179,r[0],0)
            load(0x901FC,0xFFFF850D,0,domain='native-control');emit(0x901FE,{0:r[0]&255})
            emit(0x90200,{0:r[0]>>2});emit(0x90202,{0:r[0]>>2});emit(0x90204,{0:r[0]&3})
            emit(0x90206,t=not indicator);condition(0x90208,not indicator,0x9022E)
            if indicator:
                pool(0x9020A,0x903F8,4,2);emit(0x9020C,{6:-27});emit(0x9020E,{6:229})
                emit(0x90210,{0:index});emit(0x90212,{2:RAM_BASE+0x43B8})
                load(0x90214,timer,6);emit(0x90216,t=not live);condition(0x90218,live,0x90248)
                if not live:
                    pool(0x9021A,0x90250,2,0);load(0x9021C,RAM_BASE+0x3581,2);emit(0x9021E,{2:r[2]|mask})
                    emit(0x90220,control=('jump',0x90248,True));put(0x90222,RAM_BASE+0x3581,r[2],2,delay=True);judged=True
        if not enabled or not indicator:
            pool(0x9022E,0x903F8,4,2);emit(0x90230,{6:-27});pool(0x90232,0x903FC,4,5)
            emit(0x90234,{6:229});emit(0x90236,{2:RAM_BASE+0x43B8});emit(0x90238,{0:index})
            pool(0x9023A,0x8E23,1,6);emit(0x9023C,control=('jump',0x90248,True))
            put(0x9023E,timer,r[6],6,delay=True);refreshed=True
    emit(0x90248,{15:sp-8})
    raw=bytes(frame[152:156]);emit(0x9024A,{15:sp-4},new_gbr=int.from_bytes(raw,'big'),event=('read',sp-8,4,None,'frame',raw))
    emit(0x9024C,control=('return',continuation,True))
    raw=bytes(frame[156:160]);emit(0x9024E,{14:int.from_bytes(raw,'big'),15:sp},event=('read',sp-4,4,14,'frame',raw),delay=True)
    for n,row in enumerate(steps):row['next']=steps[n+1]['site'] if n+1<len(steps) else continuation
    ordinary=bytearray(ram);ordinary[0x8500:0x8600]=memory[0x8500:0x8600]
    return dict(entry=entry,index=index,mask=mask,timer=timer,blocked=blocked,enabled=enabled,armed=armed,other_armed=other,
        indicator=indicator,timer_live=live,refreshed=refreshed,judged_set=judged,native_reset_written=raised,
        temporary_word_written=temporary,critical_sr=critical,registers=tuple(r[:15]),sr=sr,gbr=gbr,mach=context[16],macl=context[17],
        pr=continuation,sp=r[15],frame=bytes(frame),ram=bytes(ram),ordinary_ram=bytes(ordinary),native_after=bytes(ram[0x8500:0x8600]),
        path=tuple(row['site'] for row in steps),steps=steps,operands=operands,branches=branches,calls=[],
        exit=(sr,continuation,context[17],context[16],gbr,*reversed(r[:15])))
