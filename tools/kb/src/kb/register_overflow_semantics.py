"""Independent exact stock overflow-helper equations, including minimum-word NEG."""

MASK=0xFFFFFFFF
MINIMUM=-(1<<31)
MAXIMUM=(1<<31)-1


def signed(value):return value-(1<<32) if value&0x80000000 else value


def control_path(controls,continuation):
    path=[];branches=[];pc=0x265C4
    while pc!=continuation:
        if len(path)>=17:raise ValueError('the overflow equations leave the complete finite natural helper')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x265C4 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192 or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int
            or calibration!={0x265E8:bytes.fromhex('80000000'),0x265EC:bytes.fromhex('7fffffff')}):
        raise ValueError('the overflow equations require complete exact raw32 CPU, RAM, frame, SR and immutable constants')
    registers=list(context[:15]);first,second=signed(context[4]),signed(context[5]);positive=second>=0
    if positive:
        total=first+second;overflow=total>MAXIMUM;registers[5]=total&MASK
        output=MAXIMUM if overflow else registers[5]
    else:
        registers[5]=(-context[5])&MASK
        if second==MINIMUM:
            total=first+(1<<31);overflow=first>=0
        else:
            total=first+second;overflow=total<MINIMUM
        registers[4]=total&MASK;output=(1<<31) if overflow else registers[4]
    registers[0]=output;sr=(sr_before&~1)|int(overflow)
    controls={0x265C6:('taken' if positive else 'fallthrough',0x265D2 if positive else 0x265C8,False),
        0x265CC:('taken' if overflow else 'fallthrough',0x265DA if overflow else 0x265CE,False),
        0x265D4:('taken' if overflow else 'fallthrough',0x265E0 if overflow else 0x265D6,False)}
    for site in (0x265CE,0x265D6,0x265DC,0x265E2):controls[site]=('return',continuation,True)
    path,branches=control_path(controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=frame_before,ram=memory,path=path,branches=branches,
        tags=dict(first=first,second=second,positive=positive,minimum_word=second==MINIMUM,
            total=total,overflow=overflow,output=output),
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
