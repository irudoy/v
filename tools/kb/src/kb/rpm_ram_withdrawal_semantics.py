"""Independent complete natural MAF, sustained-state and delay-selector equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=64:raise ValueError('the RPM helper equations leave their finite natural path')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the RPM helper equations require complete exact CPU, RAM, SR and frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={};tags={}
    def u(at,width=1):return int.from_bytes(memory[at:at+width],'big')
    def c(at):return calibration[at][0]
    def register(index,value):registers[index]=value&MASK
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def jump(site,target):controls[site]=('jump',target,True)
    def returns(site):controls[site]=('return',continuation,True)
    def saved(value,depth=4):frame[160-depth:164-depth]=value.to_bytes(4,'big')
    if entry==0x4F736:
        fault=bool(u(0x2448)&128);high=u(0x11B2)>=192;output=int(fault and high)
        register(0,output);register(2,output);register(6,192 if fault else RAM_BASE+0x2448)
        t=high if fault else True
        branch(0x4F73C,not fault,0x4F752);branch(0x4F74C,not high,0x4F752)
        jump(0x4F74E,0x4F754);returns(0x4F754)
        tags.update(fault=fault,high=high,output=output)
    elif entry==0x4F958:
        saved(context[17]);saved(context[15],8)
        disabled=bool(c(0x8B3F)&128);base=int.from_bytes(calibration[0x90E0],'big')
        factor=c(0x84DE);product=base*factor;threshold=min(product,65535)
        exposure=u(0x1932,2);rpm=u(0x11B3);restore=c(0x84DD);cut=c(0x84DA);flags=u(0x247C)
        clear=disabled or exposure<threshold or rpm<restore
        output=flags&127 if clear else flags|128 if rpm>=cut else flags
        register(6,0x8B3F)
        if not disabled:
            register(4,base);register(5,RAM_BASE+0x128C);register(6,exposure);register(7,0x84DA);register(2,threshold)
            if exposure>=threshold:
                register(5,rpm);register(2,restore if rpm<restore else cut)
        ram[0x247C]=output;register(0,int(bool(output&128)));t=not bool(output&128)
        branch(0x4F966,disabled,0x4F9B0);branch(0x4F97E,product>65535,0x4F984)
        branch(0x4F990,exposure<threshold,0x4F9B0);branch(0x4F9A0,rpm<restore,0x4F9B0)
        branch(0x4F9A8,rpm<cut,0x4F9B4);jump(0x4F9AC,0x4F9B4);returns(0x4F9C0)
        tags.update(disabled=disabled,base=base,factor=factor,product=product,threshold=threshold,
            exposure=exposure,rpm=rpm,restore=restore,cut=cut,flags=flags,clear=clear,output=output)
    elif entry==0x5038A:
        argument=context[4];limit=bool(u(0x4250)&128);source=bool(u(0x2458)&32)
        state=u(0x106A);threshold=c(0x8A40);blocked=limit or source and state>=threshold
        configuration=bool(c(0x870C)&128)
        register(1,0x8C40);register(6,RAM_BASE+0x424C)
        if not limit:
            register(6,RAM_BASE+0x2458)
            if source:register(5,0x8A40);register(6,signed(state,8))
        if blocked:output=0;t=False if limit else True
        elif argument==1:output=c(0x8C4B);t=True
        else:
            register(6,0x870C);at=(0x8C40 if configuration else 0x8C41) if argument==2 else (0x8C4C if configuration else 0x8C4D)
            output=c(at);t=not configuration
        register(0,output);register(2,output)
        branch(0x50392,limit,0x503DA);branch(0x5039A,not source,0x503A8)
        branch(0x503A6,state>=threshold,0x503DA);branch(0x503AC,argument!=1,0x503B2)
        jump(0x503AE,0x503D6);branch(0x503BE,argument!=2,0x503CC)
        branch(0x503C2,configuration,0x503C8);jump(0x503C4,0x503D6);jump(0x503C8,0x503D6)
        branch(0x503CE,configuration,0x503D4);jump(0x503D0,0x503D6);jump(0x503D6,0x503DC);returns(0x503DC)
        tags.update(argument=argument,limit=limit,source=source,state=state,threshold=threshold,
            blocked=blocked,configuration=configuration,output=output)
    else:raise ValueError('the RPM helper equations name an undeclared natural entry')
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
