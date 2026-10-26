"""Independent sentinel predicate, ordered short-circuit gate and complete call-state equations."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000
INDICES=(0x14,0x47,0x48,0x49,0x4A,0x4B,0x4C,0x8A,0x8B,0x8C)
CALLS=((0x25A14,MASK),(0x25A1C,MASK),(0x25A24,0x14),(0x25A2C,0x47),
    (0x25A34,0x48),(0x25A3C,0x49),(0x25A44,0x4A),(0x25A4C,0x4B),
    (0x25A54,0x4C),(0x25A60,0x8A),(0x25A6C,0x8B),(0x25A78,0x8C))


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x25A12 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(raw) is not int or not 0<=raw<=MASK for raw in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the composite equations require complete exact caller CPU, frame and RAM inputs')
    if calibration!={0x25B98:(RAM_BASE+0x5718).to_bytes(4,'big')}:
        raise ValueError('the composite equations change the exact single aliased array PC literal')
    base=RAM_BASE+0x5718;cpu=[*context[:15],sp];frame=bytearray(frame_before)
    sr,pr=sr_before,continuation;steps=[];operands=[];branches=[];calls=[];returns=[];predicates=[]
    def snapshot():return dict(registers=tuple(cpu),gbr=context[15],mach=context[16],macl=context[17],sr=sr,pr=pr)
    def emit(site,updates=None,*,t=None,new_pr=None,control=None,delay=False,event=None):
        nonlocal sr,pr
        before=snapshot()
        for register,value in (updates or {}).items():cpu[register]=value&MASK
        if t is not None:sr=(sr&~1)|int(bool(t))
        if new_pr is not None:pr=new_pr
        row=dict(site=site,before=before,after=snapshot(),delay_slot=delay,branches=[])
        if event is not None:
            mode,address,width,register,domain,raw=event
            operands.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        if control is not None:
            kind,target,delayed=control
            branch=dict(site=site,kind=kind,target=target,delay=delayed);branches.append(branch);row['branches']=[branch]
        steps.append(row)
    def condition(site,taken,target,*,delayed=False):
        emit(site,control=('taken' if taken else 'fallthrough',target if taken else site+(4 if delayed else 2),delayed))
    def load(site,index):
        address=base+3*index+2;raw=memory[address-RAM_BASE]
        emit(site,{0:signed(raw,8)},event=('read',address,1,0,'ram',bytes([raw])))
        return raw
    def predicate(site,argument):
        # The pre-delay call and complete post-delay entry retain distinct R4.
        call=dict(site=site,target=0x259E4,return_address=site+4,sp=cpu[15],registers=tuple(cpu[:15]),
            gbr=context[15],mach=context[16],macl=context[17],sr=sr)
        calls.append(call)
        emit(site,new_pr=site+4,control=('call',0x259E4,True))
        emit(site+2,{4:argument} if site<0x25A60 else None,delay=True)
        call['entry']=dict(registers=tuple(cpu[:15]),sp=cpu[15],gbr=context[15],mach=context[16],macl=context[17],sr=sr,pr=pr)
        index=signed(argument&65535,16);sentinel=index==-1
        emit(0x259E4,{1:base},event=('read',0x25B98,4,1,'rom',base.to_bytes(4,'big')))
        emit(0x259E6,{0:index});emit(0x259E8,t=sentinel)
        condition(0x259EA,sentinel,0x25A0C)
        reads=[]
        if sentinel:
            emit(0x25A0C,{5:0});output=0
        else:
            if index not in INDICES:raise ValueError('the composite caller invents a different post-delay predicate argument')
            emit(0x259EC,{7:index});emit(0x259EE,{7:2*index},t=(index&MASK)>>31)
            emit(0x259F0,{2:base});emit(0x259F2,{7:3*index});emit(0x259F4,{2:base+3*index})
            raw=load(0x259F6,index);reads.append((0x259F6,base+3*index+2,raw))
            bit6=bool(raw&64);emit(0x259F8,t=not bit6);condition(0x259FA,bit6,0x25A0E,delayed=True)
            emit(0x259FC,{5:1},delay=True)
            if bit6:output=1
            else:
                emit(0x259FE,{2:base});emit(0x25A00,{2:base+3*index})
                again=load(0x25A02,index);reads.append((0x25A02,base+3*index+2,again))
                bit5=bool(again&32);emit(0x25A04,t=not bit5);condition(0x25A06,bit5,0x25A0E)
                if bit5:output=1
                else:
                    emit(0x25A08,control=('jump',0x25A0E,True));emit(0x25A0A,{5:0},delay=True);output=0
        emit(0x25A0E,control=('return',pr,True));emit(0x25A10,{0:output},delay=True)
        returns.append(dict(call_site=site,site=0x25A0E,target=site+4,state=snapshot()))
        predicates.append(dict(site=site,argument=argument,index=index,sentinel=sentinel,reads=reads,output=output))
        return output
    frame[156:160]=continuation.to_bytes(4,'big')
    emit(0x25A12,{15:sp-4},event=('write',sp-4,4,None,'frame',continuation.to_bytes(4,'big')))
    active=None
    for position,(site,argument) in enumerate(CALLS):
        if site>=0x25A60:
            prefix={0x25A60:0x25A5C,0x25A6C:0x25A68,0x25A78:0x25A74}[site]
            emit(prefix,{3:argument|0xFFFFFF00});emit(prefix+2,{4:argument})
        output=predicate(site,argument)
        test=site+4;emit(test,t=output==0)
        condition(test+2,output!=0,0x25A84)
        if output:
            active=argument;emit(0x25A84,{2:1});break
    if active is None:
        emit(0x25A80,control=('jump',0x25A86,True));emit(0x25A82,{2:0},delay=True)
    emit(0x25A86,{15:sp},new_pr=continuation,event=('read',sp-4,4,None,'frame',continuation.to_bytes(4,'big')))
    emit(0x25A88,control=('return',continuation,True));emit(0x25A8A,{0:int(active is not None)},delay=True)
    for index,row in enumerate(steps):row['next']=steps[index+1]['site'] if index+1<len(steps) else continuation
    return dict(entry=entry,active_index=active,output=int(active is not None),registers=tuple(cpu[:15]),sr=sr,
        gbr=context[15],mach=context[16],macl=context[17],pr=pr,sp=cpu[15],frame=bytes(frame),ram=memory,
        path=tuple(row['site'] for row in steps),steps=steps,operands=operands,branches=branches,calls=calls,
        returns=returns,predicates=predicates,exit=(sr,pr,context[17],context[16],context[15],*reversed(cpu[:15])))
