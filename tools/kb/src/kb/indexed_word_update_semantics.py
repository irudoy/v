"""Independent indexed word/status equations and complete interrupt-mask state."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(controls,continuation):
    path=[];branches=[];pc=0x52034
    while pc!=continuation:
        if len(path)>=92:raise ValueError('the indexed word equations leave their complete finite natural entry')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x52034 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192 or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the indexed word equations require exact complete CPU/SR/RAM/frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={};writes={};frames={}
    def u(at,width=1):return int.from_bytes(memory[at:at+width],'big')
    def sb(at):return signed(u(at),8)
    def reg(i,v):registers[i]=v&MASK
    def put(site,at,value,width=1):
        blob=(value&((1<<(width*8))-1)).to_bytes(width,'big');ram[at:at+width]=blob;writes[site]=blob
    def saved(site,depth,value,register=None,mode='write'):
        raw=(value&MASK).to_bytes(4,'big');frames[site]=(mode,depth,register,raw)
        if mode=='write':frame[160-depth:164-depth]=raw
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    enable=calibration[0x8D92][0];factor=calibration[0x87FE][0]
    index=context[4]&255;mask=context[5]&255;enabled=bool(enable&8)
    saved(0x52034,4,context[15]);saved(0x520EA,4,context[15],mode='read')
    reg(0,signed(enable,8));reg(4,mask);reg(6,0x8D92);reg(7,context[4]);t=not enabled
    branch(0x52044,not enabled,0x520E6,True)
    blocked=False;held=False;counter_changed=False;difference=None
    if enabled:
        threshold=factor*128;reg(2,signed(factor,8));reg(5,threshold);reg(6,RAM_BASE+0x22DC)
        reg(0,sb(0x22E0));fuel=bool(mask&u(0x22E0));blocked=fuel
        branch(0x5205C,fuel,0x520DE);t=not fuel
        if not fuel:
            reg(2,RAM_BASE+0x142E);reg(7,2*index);reg(0,2*index)
            sample=signed(u(0x142E+2*index,2),16);reg(6,sample)
            below=sample<threshold;blocked=below;branch(0x52070,below,0x520DE);t=not below
            if not below:
                reg(6,RAM_BASE+0x128C);reg(0,0x473);reg(2,sb(0x16FF))
                inhibited=bool(mask&u(0x16FF));blocked=inhibited
                branch(0x5207A,inhibited,0x520DE);t=not inhibited
        if blocked:
            status=sb(0x1220)&(~mask&MASK);reg(2,~mask);reg(0,status);put(0x520E4,0x1220,status)
        else:
            old=sb(0x1220);saved(0x5207E,8,old,0)
            put(0x52082,0x1220,old|mask);reg(0,sb(0x125E));held=bool(mask&u(0x125E))
            branch(0x52088,held,0x520E6);t=not held
            if not held:
                previous=u(0x2348+2*index,2);delta=signed(u(0x1396+2*index,2),16)
                difference=previous-delta;nonnegative=difference>=0;value=max(difference,0)
                saved(0x520A2,12,RAM_BASE+0x2330,6)
                saved(0x520BE,12,RAM_BASE+0x2330,5,mode='read')
                put(0x520C4,0x2348+2*index,value,2)
                saved(0x520CA,12,RAM_BASE+0x2348,5)
                branch(0x520B8,nonnegative,0x520BE,True)
                controls[0x520DA]=('jump',0x520E6,True)
                final_sr=(sr_before&~1)|int(nonnegative)
                reg(0,sr_before&0xF0);reg(2,final_sr);reg(4,difference);reg(5,0xFFFFFF0F);reg(6,value)
                t=nonnegative;counter_changed=True
    controls[0x520E8]=('return',continuation,True)
    sr=(sr_before&~1)|int(t);path,branches=control_path(controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,
        tags=dict(index=index,mask=mask,enabled=enabled,blocked=blocked,held=held,counter_changed=counter_changed,
            difference=difference,physical_writes=writes,frame_accesses=frames,
            interrupted_sr=((sr_before&~0xF1)|0xF1) if counter_changed else None,restored_interrupt_mask=sr_before&0xF0),
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
