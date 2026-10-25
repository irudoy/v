"""Independent complete exposure and transition-window state equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control_path(entry,controls,continuation):
    path=[];branches=[];pc=entry
    while pc!=continuation:
        if len(path)>=254:raise ValueError('the RPM-state equations leave their finite natural entries')
        path.append(pc)
        if pc not in controls:pc+=2;continue
        kind,target,delay=controls[pc];branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:path.append(pc+2)
        pc=target
    return tuple(path),branches


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the RPM-state equations require complete raw CPU/RAM/SR/frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before);controls={};tags={}
    reads={};writes={}
    def u(at,width=1):return int.from_bytes(memory[at:at+width],'big')
    def sb(at):return signed(u(at),8)
    def c(at,width=1):
        matches=[blob[at-first:at-first+width] for first,blob in calibration.items()
            if first<=at and at+width<=first+len(blob)]
        if len(matches)!=1:raise ValueError('the RPM-state equations omit an exact complete configuration operand')
        return int.from_bytes(matches[0],'big')
    def cb(at):return signed(c(at),8)
    def reg(index,value):registers[index]=value&MASK
    def put(site,at,value,width=1):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');ram[at:at+width]=raw;writes[site]=raw
    def branch(site,taken,target,delay=False):
        controls[site]=('taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def jump(site,target):controls[site]=('jump',target,True)
    disabled=bool(c(0x8B3F)&128)
    if entry==0x4F7E0:
        frame[156:160]=context[17].to_bytes(4,'big');reg(6,0x8B3F);reg(0,cb(0x8B3F))
        branch(0x4F7E8,not disabled,0x4F7EE);jump(0x4F7EA,0x4F902)
        t=not disabled
        if not disabled:
            base,step=c(0x90E0,2),c(0x84DE);product=base*step;threshold=min(product,65535)
            reg(5,base);reg(4,step);reg(0,cb(0x84DE));reg(6,65535);reg(2,threshold)
            branch(0x4F804,product<=65535,0x4F80A);jump(0x4F806,0x4F814)
            if product<=65535:reg(3,0x84D7);reg(6,step)
            source=bool(u(0x2458)&32);reg(6,RAM_BASE+0x244C);reg(0,sb(0x2458));reg(4,threshold)
            branch(0x4F81A,source,0x4F82C,True)
            if source:inhibit=True;reg(5,1)
            else:
                exposure=u(0x1932,2);reg(2,RAM_BASE+0x128C);reg(0,0x6A6);reg(6,exposure)
                inhibit=exposure<threshold;reg(5,int(inhibit));branch(0x4F828,not inhibit,0x4F82E,True)
            reg(6,RAM_BASE+0x244C);reg(0,sb(0x244F));reset=bool(u(0x244F)&4)
            branch(0x4F834,reset,0x4F8FA);t=not reset
            if reset:
                reg(3,RAM_BASE+0x128C);reg(2,0);reg(0,0x6A6)
                put(0x4F900,0x1932,0,2)
            else:
                reg(6,RAM_BASE+0x424C);reg(0,sb(0x4250));limited=bool(u(0x4250)&64)
                branch(0x4F83C,limited,0x4F8E8);t=not limited
                blocked_site=None
                if limited:blocked_site=0x4F8E8
                else:
                    reg(6,0x83D7);reg(0,cb(0x83D7));gate=bool(c(0x83D7)&1)
                    branch(0x4F844,not gate,0x4F84E);t=not gate
                    if gate:
                        reg(6,RAM_BASE+0x24CE);reg(0,sb(0x24CF));state=bool(u(0x24CF)&32)
                        branch(0x4F84C,state,0x4F8D6);t=not state
                        if state:blocked_site=0x4F8D6
                    if blocked_site is None:
                        reg(6,RAM_BASE+0x41A9);reg(0,sb(0x41D4));mode=bool(u(0x41D4)&1)
                        branch(0x4F856,mode,0x4F8D6);t=not mode
                        if mode:blocked_site=0x4F8D6
                if blocked_site is not None:
                    reg(0,int(inhibit));t=inhibit
                    branch(blocked_site+4,not inhibit,0x4F902)
                    if inhibit:
                        reg(3,RAM_BASE+0x128C);reg(2,0);reg(0,0x6A6)
                        put(0x4F8F4 if limited else 0x4F8E2,0x1932,0,2)
                        jump(0x4F8F6 if limited else 0x4F8E4,0x4F902)
                else:
                    reg(3,0x84D7);reg(6,sb(0x110E));reg(2,cb(0x84D7));reg(0,0x7A)
                    invalid=(sb(0x110E)&MASK)>(cb(0x84D7)&MASK)
                    branch(0x4F864,invalid,0x4F8AC);t=invalid
                    if not invalid:
                        rpm=u(0x11B3);lower=c(0x84DC);reg(7,rpm);reg(2,lower);reg(0,cb(0x84DC))
                        invalid=rpm<lower;branch(0x4F876,invalid,0x4F8AC);t=not invalid
                        if not invalid:
                            upper=c(0x84DB);reg(2,upper);reg(0,cb(0x84DB));invalid=rpm>upper
                            branch(0x4F880,invalid,0x4F8AC);t=invalid
                    if invalid:
                        reg(0,int(inhibit));t=inhibit;branch(0x4F8B0,not inhibit,0x4F902)
                        if inhibit:
                            exposure=u(0x1932,2);decrement=exposure-1;remaining=max(decrement,0)
                            reg(6,remaining);reg(2,remaining);reg(3,RAM_BASE+0x128C);reg(0,0x6A6)
                            branch(0x4F8C0,decrement>=0,0x4F8C6);jump(0x4F8C2,0x4F8CA)
                            put(0x4F8CE,0x1932,remaining,2);jump(0x4F8D0,0x4F902);t=decrement>=0
                    else:
                        exposure=u(0x1932,2);total=exposure+step;high=total>threshold
                        output=min(total,threshold);reg(2,total);reg(3,RAM_BASE+0x128C)
                        reg(4,output);reg(6,step);reg(7,exposure if high else total)
                        reg(0,0x6A6)
                        if not high:reg(5,step)
                        branch(0x4F896,high,0x4F8A2);put(0x4F8A6,0x1932,output,2)
                        jump(0x4F8A8,0x4F902);t=high
            tags.update(base=base,step=step,product=product,threshold=threshold,inhibit=inhibit)
        controls[0x4F902]=('return',continuation,True)
    elif entry==0x4F9C4:
        frame[156:160]=context[15].to_bytes(4,'big');initial=u(0x2497);clock=u(0x1690)
        latch=initial;reg(1,sb(0x2497));reg(6,0x8B3F);reg(0,cb(0x8B3F))
        branch(0x4F9D4,disabled,0x4FA88)
        if disabled:
            latch=initial&127;put(0x4FA8C,0x2497,latch)
        else:
            reset=bool(u(0x244F)&4);reg(0,sb(0x244F));branch(0x4F9DA,not reset,0x4F9E0)
            if reset:
                reg(5,-1);clock=255;jump(0x4F9DC,0x4F9E8)
            else:
                edge=bool(u(0x2453)&4);reg(0,sb(0x2453));branch(0x4F9E4,not edge,0x4F9F0)
                if edge:reg(5,0);clock=0
                else:
                    total=clock+1;reg(5,255);reg(6,clock);reg(2,min(total,255))
                    branch(0x4FA02,total<=255,0x4FA08);jump(0x4FA04,0x4FA0C)
                    if total<=255:reg(6,total)
                    clock=min(total,255);reg(5,clock)
            reg(7,RAM_BASE+0x128C);reg(0,0x404)
            put(0x4F9EE if reset or edge else 0x4FA10,0x1690,clock)
            if reset or edge:jump(0x4F9EC,0x4FA12)
            active=bool(initial&128);reg(0,signed(initial,8));branch(0x4FA16,not active,0x4FA40)
            cleared=False
            if active:
                reg(2,RAM_BASE+0x119C);reg(4,0x88A7);reg(6,sb(0x11B3));reg(0,cb(0x88AE))
                low=(sb(0x11B3)&MASK)<(cb(0x88AE)&MASK);branch(0x4FA24,low,0x4FA30)
                if low:cleared=True
                else:
                    reg(0,cb(0x88AD));reg(5,clock);reg(2,c(0x88AD));cleared=clock>=c(0x88AD)
                    branch(0x4FA2E,not cleared,0x4FA40)
                if cleared:
                    latch=initial&127;put(0x4FA34,0x2497,latch);reg(2,-1);reg(7,RAM_BASE+0x128C)
                    reg(0,0x404);put(0x4FA3E,0x1690,255);jump(0x4FA3C,0x4FA8E)
            if not cleared:
                transition=bool(u(0x245D)&64);reg(0,sb(0x245D));branch(0x4FA44,transition,0x4FA8E)
                eligible=not transition
                if eligible:
                    reg(6,RAM_BASE+0x41A9);reg(0,sb(0x41D4));mode=bool(u(0x41D4)&1)
                    branch(0x4FA4E,mode,0x4FA8E);eligible=not mode
                if eligible:
                    reg(2,RAM_BASE+0x119C);reg(4,0x88A7);reg(6,sb(0x11B3));reg(0,cb(0x88A9))
                    low=(sb(0x11B3)&MASK)<(cb(0x88A9)&MASK);branch(0x4FA5C,low,0x4FA8E);eligible=not low
                if eligible:
                    reg(2,RAM_BASE+0x1068);reg(6,sb(0x1071));reg(0,cb(0x88A8))
                    low=(sb(0x1071)&MASK)<(cb(0x88A8)&MASK);branch(0x4FA68,low,0x4FA8E);eligible=not low
                if eligible:
                    reg(2,RAM_BASE+0x1094);reg(6,sb(0x110E));reg(0,cb(0x88AA))
                    high=(sb(0x110E)&MASK)>(cb(0x88AA)&MASK);branch(0x4FA74,high,0x4FA8E);eligible=not high
                if eligible:
                    reg(7,RAM_BASE+0x128C);reg(0,0x404);reg(2,cb(0x88A7));reg(5,signed(clock,8))
                    high=(signed(clock,8)&MASK)>=(cb(0x88A7)&MASK);branch(0x4FA80,high,0x4FA8E);eligible=not high
                if eligible:
                    latch=initial|128;put(0x4FA8C,0x2497,latch);jump(0x4FA84,0x4FA8C)
            reads[0x4FA7C]=bytes([clock])
        reads[0x4FA8E]=bytes([latch]);reg(0,int(bool(latch&128)));t=not bool(latch&128)
        controls[0x4FA98]=('return',continuation,True)
        tags.update(initial_latch=initial,clock_after_update=clock,latch=latch)
    else:raise ValueError('the RPM-state equations name another natural entry')
    tags.update(disabled=disabled,physical_reads=reads,physical_writes=writes)
    sr=(sr_before&~1)|int(t);path,branches=control_path(entry,controls,continuation)
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),ram=bytes(ram),path=path,branches=branches,tags=tags,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
