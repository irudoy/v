"""Separate bounded caller quotient, clamp, RAM/frame and post-delay argument equations."""

from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000
CALLER_SPANS=((0x3A254,0x3A286),(0x6E442,0x6E490),(0xB7C84,0xB7CF2))


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry not in (0x3A254,0x6E442,0xB7C84)
            or type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20 or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the bounded division caller equations need complete typed CPU/RAM/frame inputs')
    ram=bytearray(memory);frame=bytearray(frame_before);frames={};controls={};writes={};calls=[]
    registers={i:v for i,v in enumerate(context[:15])};t=False
    def put(site,at,width,value):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');ram[at:at+width]=raw;writes[site]=raw
    def access(site,mode,depth,value,register=None):
        raw=(value&MASK).to_bytes(4,'big');frames[site]=(mode,depth,register,raw)
        if mode=='write':frame[160-depth:164-depth]=raw
    def branch(site,taken,target,delay=False):
        controls[site]=dict(site=site,target=target if taken else site+(4 if delay else 2),
            kind='taken' if taken else 'fallthrough',delay=delay)
    def jump(site,target):controls[site]=dict(site=site,target=target,kind='jump',delay=True)
    def helper(site,target,divisor,dividend,depth,r2,r4,overrides,macl):
        magnitude=abs(signed(dividend)) if target==0x21BBC else dividend
        long_path=magnitude>=divisor*256
        incoming=list(context[:15]);incoming[0:2]=[divisor,dividend]
        for index,value in overrides.items():incoming[index]=value&MASK
        calls.append(dict(site=site,target=target,return_address=site+4,sp=sp-depth,
            registers=tuple(incoming),gbr=context[15],mach=context[16],macl=macl,
            sr=sr_before&~1,arguments={0:divisor,1:dividend},long_path=long_path))
        controls[site]=dict(site=site,target=target,kind='call',delay=True)
        registers.pop(1,None)
        if target==0x21BBC:
            access(0x21BBC,'write',depth+4,r2,2);access(0x21BC2,'write',depth+8,context[3],3)
            if long_path:
                access(0x21C08,'write',depth+12,r4,4);access(0x21C68,'read',depth+12,r4,4)
                access(0x21C6A,'read',depth+8,context[3],3);access(0x21C6E,'read',depth+4,r2,2)
            else:
                access(0x21C02,'read',depth+8,context[3],3);access(0x21C06,'read',depth+4,r2,2)
        else:
            access(0x21CE0,'write',depth+4,r2,2)
            if long_path:
                access(0x21D0C,'write',depth+8,context[3],3);access(0x21D64,'read',depth+8,context[3],3)
                access(0x21D68,'read',depth+4,r2,2)
            else:access(0x21D06,'read',depth+4,r2,2)
    if entry==0x3A254:
        access(0x3A254,'write',4,continuation);access(0x3A280,'read',4,continuation)
        enable=calibration[0x8349][0];active=bool(enable&8);t=not active
        branch(0x3A25C,not active,0x3A280)
        registers.update({0:signed(enable,8)&MASK,6:0x8349})
        output=None
        if active:
            dividend=context[4]&65535;output=dividend//20
            helper(0x3A262,0x21BBC,20,dividend,4,0x21BBC,context[4],{2:0x21BBC,6:0x8349},context[17])
            t=output>255;branch(0x3A26C,not t,0x3A272,True);output=min(output,255)
            put(0x3A27A,0x1020,1,output);put(0x3A27E,0x118E,1,output)
            registers.update({0:0x7A,2:RAM_BASE+0x1114,5:RAM_BASE+0x1018,6:output})
        returned=0x3A282
    elif entry==0x6E442:
        access(0x6E442,'write',4,continuation);access(0x6E444,'write',8,context[17])
        access(0x6E488,'read',8,context[17]);access(0x6E48A,'read',4,continuation)
        level=memory[0x11B3];factor=memory[0x1766];active=bool(level);t=not active
        branch(0x6E450,not active,0x6E482)
        if active:
            divisor=level*80;dividend=factor*1475;candidate=dividend//divisor+50
            helper(0x6E46E,0x21CE0,divisor,dividend,8,1475,context[4],{2:1475,5:0x21CE0,6:divisor},dividend)
            t=candidate>255;branch(0x6E47A,not t,0x6E484,True)
            if t:jump(0x6E47E,0x6E484)
            output=min(candidate,255);registers[6]=255
        else:output=0;registers[6]=0
        registers.update({0:0x126,2:output,5:RAM_BASE+0x1E60})
        put(0x6E48E,0x1F86,1,output);returned=0x6E48C
    else:
        access(0xB7C84,'write',4,continuation);access(0xB7C86,'write',8,context[17])
        access(0xB7CEA,'read',8,context[17]);access(0xB7CEC,'read',4,continuation)
        raw=signed(context[4]);above=raw>107350;branch(0xB7C8C,above,0xB7C96)
        if not above:branch(0xB7C92,raw<(-107350),0xB7C96)
        numerator=max(-107350,min(107350,raw))
        product=calibration[0x8542][0]*calibration[0x8543][0]
        branch(0xB7CAC,product<=10735,0xB7CB0)
        divisor=min(product,10735);active=bool(divisor);branch(0xB7CB4,not active,0xB7CC6)
        if active:
            dividend=(numerator*20000)&MASK
            helper(0xB7CBE,0x21BBC,divisor,dividend,8,20000,10735,{2:20000,4:10735,5:0x21BBC,6:divisor},dividend)
            candidate=signed(division.quotient('signed',divisor,dividend));jump(0xB7CC2,0xB7CD4)
            registers[5]=0x21BBC
        else:
            nonnegative=numerator>=0;branch(0xB7CC8,nonnegative,0xB7CD2)
            candidate=0x7FFFFFFF if nonnegative else -0x80000000
            if not nonnegative:jump(0xB7CCE,0xB7CD4)
            registers[5]=numerator&MASK
        above_output=candidate>200000;branch(0xB7CD8,above_output,0xB7CE2)
        if not above_output:branch(0xB7CDE,candidate<(-200000),0xB7CE2)
        output=max(-200000,min(200000,candidate));t=candidate>=(-200000)
        registers.update({0:0xB08,2:output&MASK,4:10735,6:RAM_BASE+0x28F8})
        put(0xB7CE8,0x3400,4,output);returned=0xB7CEE
    controls[returned]=dict(site=returned,target=continuation,kind='return',delay=True)
    caller_path=[];caller_branches=[];pc=entry
    while pc!=continuation:
        if len(caller_path)>119:raise ValueError('the division caller equation leaves its finite natural path')
        caller_path.append(pc)
        if pc not in controls:pc+=2;continue
        control=controls[pc];caller_branches.append(control)
        if control['delay']:caller_path.append(pc+2)
        pc=pc+4 if control['kind']=='call' else control['target']
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers=registers,t=bool(t),helper_active=active,
        gbr=context[15],mach=context[16],macl=context[17],pr=continuation,sp=sp,
        caller_path=tuple(caller_path),caller_branches=caller_branches,calls=calls,output=output,
        frame_accesses=frames,physical_writes=writes,sr_before=sr_before)
