"""Independent bounded integer-state equations for declared native ROM paths.

This is a semantic oracle, not a stock runner or an execution receipt. Only
explicit instruction spans and declared memory are admitted. Calls, returns,
SR, stack contents and exact-width accesses remain observable in its result.
"""

MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
RAM_SIZE = 65536
ISA_REFERENCE = 'https://www.renesas.com/en/document/mah/sh-2e-software-manual'
ISA_REFERENCE_ID = 'REJ09B0316-0200'


def signed(value,bits=32):
    return value-(1 << bits) if value & (1 << (bits-1)) else value


def divide_step(divisor,partial,sr):
    """Independent Boolean form of SH-2E section 7.2.18, pp.85-86."""
    previous=(sr >> 8)&1
    mode=(sr >> 9)&1
    high=partial >> 31
    shifted=((partial << 1)|(sr&1))&MASK
    subtract=previous==mode
    result=(shifted-divisor if subtract else shifted+divisor)&MASK
    carry=int(result>shifted) if subtract else int(result<shifted)
    quotient=carry ^ high ^ mode
    return result,(sr&~0x101)|(quotient << 8)|int(quotient==mode)


def execute(declared,fixture,context,ram_before,frame_before,sp,continuation,entry,sr_before,*,trace=False):
    """Predict complete state over an exact natural caller/helper closure.

    The caller separately admits current stock bytes, fixture transformations,
    actual original observations, native fact scope and the terminal. No call
    is replaced by its arithmetic result; each helper instruction is interpreted.
    """
    if type(trace) is not bool:
        raise ValueError('the bounded instruction trace requires an explicit Boolean mode')
    events=[] if trace else None
    feedback_window=False
    if declared.get('id')=='jk08a-closed-loop-feedback-accesses':
        from kb import closed_loop_feedback_access_contract
        feedback_window=closed_loop_feedback_access_contract.state_storage_premise(declared)
    frame_prefix=320 if feedback_window else 160
    frame_size=352 if feedback_window else 192
    if (type(fixture) is not bytes or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(ram_before) is not bytes or len(ram_before)!=RAM_SIZE
            or type(frame_before) is not bytes or len(frame_before)!=frame_size
            or type(sp) is not int or not frame_prefix<=sp<=MASK-32 or sp&3
            or type(continuation) is not int or not 0<=continuation<=MASK
            or type(sr_before) is not int or not 0<=sr_before<=MASK
            or sr_before&0x3F1!=context[18]):
        raise ValueError('the byte-surface oracle lacks its complete typed entry state')
    spans=tuple((row['start'],row['end']) for row in declared['entry'])
    step_limit=16384
    if declared.get('id')=='jk08a-ram-initialization':
        from kb import ram_initialization_contract
        step_limit=ram_initialization_contract.oracle_budget(declared)
    native_controls=declared.get('native_control_bytes')
    native_window=(declared.get('id')=='jk08a-ignition-diagnostic-path'
        and type(native_controls) is dict
        and native_controls.get('window_start')==0xFFFF9900
        and native_controls.get('window_size')==256
        and native_controls.get('addresses')==[0xFFFF99C4,0xFFFF9926])
    publication_window=(declared.get('id')=='jk08a-publication-inhibit-path'
        and type(native_controls) is dict
        and native_controls.get('window_start')==0xFFFF8400
        and native_controls.get('window_size')==256
        and native_controls.get('addresses')==[0xFFFF84C3])
    gopher_window=declared.get('id')=='jk08a-fine-gopher'
    coordinate_window=(declared.get('id')=='jk08a-closed-loop-coordinate'
        and declared.get('native_storage')==dict(start=0xFFFF8560,size=20,logical_offset=0x8560,
            observed_start=0xFFFF8500,observed_size=256))
    native_io_window=(declared.get('id')=='jk08a-io-accesses'
        and declared.get('native_io')==[dict(start=0xFFFFD900,size=1024),
            dict(start=0xFFFFF400,size=256),dict(start=0xFFFFF700,size=256)])
    if entry not in {start for start,end in spans}:
        raise ValueError('the byte-surface oracle requires an explicitly declared natural entry')
    if sp-frame_prefix<RAM_BASE+RAM_SIZE and RAM_BASE<sp+32 or sp-frame_prefix<len(fixture):
        raise ValueError('the byte-surface frame overlaps ROM or admitted RAM')
    if native_io_window and any(sp-frame_prefix<start+size and start<sp+32 for start,size in
            ((0xFFFFD900,1024),(0xFFFFF400,256),(0xFFFFF700,256))):
        raise ValueError('the bounded I/O frame overlaps declared native storage')
    if coordinate_window and sp-frame_prefix<0xFFFF8574 and 0xFFFF8560<sp+32:
        raise ValueError('the coordinate frame overlaps its exact native twenty-byte workspace')
    registers=[*context[:15],sp]
    gbr,mach,macl=context[15:18]
    sr,pr=sr_before,continuation
    ram,frame=bytearray(ram_before),bytearray(frame_before)
    accesses,calls,branches,code=[],[],[],{}
    pc,steps,pending=entry,0,None
    pending_call_index=None

    def access(site,mode,address,width,value=None,register=None):
        if width not in (1,2,4) or type(address) is not int or address%width:
            raise ValueError('the byte-surface oracle changes a natural aligned access')
        if RAM_BASE<=address<=RAM_BASE+RAM_SIZE-width:
            memory,offset,domain=ram,address-RAM_BASE,'ram'
        elif feedback_window and 0x5FFC<=address<=0x612A-width:
            memory,offset,domain=ram,0x88B0+address-0x5FFC,'feedback-workspace'
        elif native_window and 0xFFFF9900<=address<=0xFFFF9A00-width:
            # The independent consumer requires actual native/relocated snapshots to agree.
            memory,offset,domain=ram,address&65535,'native-control'
        elif publication_window and 0xFFFF8400<=address<=0xFFFF8500-width:
            memory,offset,domain=ram,address&65535,'native-control'
        elif gopher_window and 0xFFFF8C00<=address<=0xFFFF8D00-width:
            memory,offset,domain=ram,address&65535,'gbr-window'
        elif gopher_window and 0xFFFF9900<=address<=0xFFFF9B00-width:
            memory,offset,domain=ram,address&65535,'block-window'
        elif coordinate_window and 0xFFFF8560<=address<=0xFFFF8574-width:
            memory,offset,domain=ram,address&65535,'coordinate-workspace'
        elif native_io_window and any(start<=address<=start+size-width for start,size in
                ((0xFFFFD900,1024),(0xFFFFF400,256),(0xFFFFF700,256))):
            memory,offset,domain=ram,address&65535,'native-io'
        elif sp-frame_prefix<=address<=sp+32-width:
            memory,offset,domain=frame,address-sp+frame_prefix,'frame'
        elif 0<=address<=len(fixture)-width and mode=='read':
            memory,offset,domain=fixture,address,'rom'
        else:
            raise ValueError('the byte-surface oracle accesses an undeclared memory domain or writes ROM')
        if mode=='write':
            memory[offset:offset+width]=(value&((1 << (width*8))-1)).to_bytes(width,'big')
        raw=bytes(memory[offset:offset+width])
        accesses.append(dict(site=site,mode=mode,address=address,width_bytes=width,
                             register=register,domain=domain,bytes=raw.hex()))
        result=int.from_bytes(raw,'big')
        return signed(result,width*8)&MASK if width<4 else result

    def transfer(target,kind,delay=True):
        nonlocal pending,pr,pending_call_index
        if previous is not None:
            raise ValueError('the byte-surface oracle encounters a control transfer in a delay slot')
        if kind=='call':
            pr=(pc+4)&MASK
            calls.append(dict(site=pc,target=target,return_address=pr,sp=registers[15],
                registers=tuple(registers[:15]),gbr=gbr,mach=mach,macl=macl,sr=sr))
            pending_call_index=len(calls)-1
        branches.append(dict(site=pc,target=target,kind=kind,delay=delay))
        if delay:pending=target
        return pc+2 if delay else target

    while pc!=continuation:
        if steps>=step_limit or not any(start<=pc<end for start,end in spans) or pc+2>len(fixture):
            raise ValueError('the byte-surface oracle leaves its exact finite instruction closure')
        steps+=1
        word=int.from_bytes(fixture[pc:pc+2],'big')
        code[pc]=fixture[pc:pc+2].hex()
        if trace:
            initial=dict(registers=tuple(registers),gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr)
            counts=(len(accesses),len(calls),len(branches))
        n,m,low=(word >> 8)&15,(word >> 4)&15,word&15
        previous,pending=pending,None
        next_pc=(pc+2)&MASK
        if word >> 12 in (9,13):
            width=4 if word >> 12==13 else 2
            address=((pc&~3) if width==4 else pc)+4+(word&255)*width
            registers[n]=access(pc,'read',address,width,register=n)
        elif word >> 12==14:
            registers[n]=signed(word&255,8)&MASK
        elif word >> 12==7:
            registers[n]=(registers[n]+signed(word&255,8))&MASK
        elif word&0xF00F==0x6003:
            registers[n]=registers[m]
        elif word&0xF00F in (0x600C,0x600D):
            registers[n]=registers[m]&(255 if low==12 else 65535)
        elif word&0xF00F in (0x600E,0x600F):
            bits=8 if low==14 else 16
            registers[n]=signed(registers[m]&((1 << bits)-1),bits)&MASK
        elif word&0xF00F==0x600B:
            registers[n]=(-registers[m])&MASK
        elif word&0xF00F==0x6007:
            registers[n]=(~registers[m])&MASK
        elif word&0xF00F==0x6009:
            registers[n]=((registers[m] << 16)|(registers[m] >> 16))&MASK
        elif word&0xF00F in (0x6000,0x6001,0x6002):
            registers[n]=access(pc,'read',registers[m],1 << low,register=n)
        elif word&0xF00F in (0x6004,0x6005,0x6006):
            width=1 << (low-4)
            value=access(pc,'read',registers[m],width,register=n)
            if n!=m:registers[m]=(registers[m]+width)&MASK
            registers[n]=value
        elif word&0xF00F in (0x2000,0x2001,0x2002):
            access(pc,'write',registers[n],1 << low,registers[m],m)
        elif word&0xF00F in (0x2004,0x2005,0x2006):
            width=1 << (low-4)
            value=registers[m]
            registers[n]=(registers[n]-width)&MASK
            access(pc,'write',registers[n],width,value,m)
        elif word&0xF00F in (0x000C,0x000D,0x000E):
            registers[n]=access(pc,'read',(registers[m]+registers[0])&MASK,1 << (low-12),register=n)
        elif word&0xF00F in (0x0004,0x0005,0x0006):
            access(pc,'write',(registers[n]+registers[0])&MASK,1 << (low-4),registers[m],m)
        elif word >> 8 in (0x84,0x85):
            width=1 << (word >> 8&1)
            registers[0]=access(pc,'read',(registers[m]+low*width)&MASK,width,register=0)
        elif word >> 8 in (0x80,0x81):
            width=1 << (word >> 8&1)
            access(pc,'write',(registers[m]+low*width)&MASK,width,registers[0],0)
        elif word >> 12==5:
            registers[n]=access(pc,'read',(registers[m]+low*4)&MASK,4,register=n)
        elif word >> 12==1:
            access(pc,'write',(registers[n]+low*4)&MASK,4,registers[m],m)
        elif word >> 8 in (0xC0,0xC1,0xC2):
            width=1 << (word >> 8&3)
            access(pc,'write',(gbr+(word&255)*width)&MASK,width,registers[0],0)
        elif word >> 8 in (0xC4,0xC5,0xC6):
            width=1 << (word >> 8&3)
            registers[0]=access(pc,'read',(gbr+(word&255)*width)&MASK,width,register=0)
        elif word&0xF0FF==0x4022:
            registers[n]=(registers[n]-4)&MASK
            access(pc,'write',registers[n],4,pr)
        elif word&0xF0FF==0x4026:
            pr=access(pc,'read',registers[n],4)
            registers[n]=(registers[n]+4)&MASK
        elif word&0xF0FF==0x402A:
            pr=registers[n]
        elif word&0xF0FF==0x4012:
            registers[n]=(registers[n]-4)&MASK
            access(pc,'write',registers[n],4,macl)
        elif word&0xF0FF==0x4016:
            macl=access(pc,'read',registers[n],4)
            registers[n]=(registers[n]+4)&MASK
        elif word&0xF0FF==0x4013:
            registers[n]=(registers[n]-4)&MASK
            access(pc,'write',registers[n],4,gbr)
        elif word&0xF0FF==0x4017:
            gbr=access(pc,'read',registers[n],4)
            registers[n]=(registers[n]+4)&MASK
        elif word&0xF0FF==0x0012:
            registers[n]=gbr
        elif word&0xF0FF==0x401E:
            gbr=registers[n]
        elif word&0xF0FF==0x001A:
            registers[n]=macl
        elif word&0xF0FF==0x401A:
            macl=registers[n]
        elif word&0xF00F==0x0007:
            macl=(registers[n]*registers[m])&MASK
        elif word&0xF00F==0x200E:
            macl=(registers[n]&65535)*(registers[m]&65535)
        elif word&0xF00F==0x300C:
            registers[n]=(registers[n]+registers[m])&MASK
        elif word&0xF00F==0x3008:
            registers[n]=(registers[n]-registers[m])&MASK
        elif word&0xF00F in (0x300F,0x300B):
            # Renesas REJ09B0171 sections6.1.4/6.1.66: signed overflow updates T.
            first,second=registers[n],registers[m]
            result=(first+second if word&15==15 else first-second)&MASK
            overflow=((first^result)&(second^result) if word&15==15 else
                (first^second)&(first^result))>>31
            registers[n]=result
            sr=(sr&~1)|(overflow&1)
        elif word&0xF00F==0x300E:
            total=registers[n]+registers[m]+(sr&1)
            registers[n]=total&MASK
            sr=(sr&~1)|int(total>MASK)
        elif word&0xF00F==0x300A:
            first,subtrahend=registers[n],registers[m]+(sr&1)
            registers[n]=(first-subtrahend)&MASK
            sr=(sr&~1)|int(first<subtrahend)
        elif word&0xF00F==0x200D:
            registers[n]=((registers[n] >> 16)|(registers[m] << 16))&MASK
        elif word&0xF00F in (0x2009,0x200A,0x200B):
            first,second=registers[n],registers[m]
            registers[n]=(first&second if low==9 else first^second if low==10 else first|second)&MASK
        elif word >> 8 in (0xC9,0xCA,0xCB):
            first,second=registers[0],word&255
            registers[0]=(first&second if word >> 8==0xC9 else first^second if word >> 8==0xCA else first|second)&MASK
        elif word&0xF0FF in (0x4008,0x4018,0x4028):
            registers[n]=(registers[n] << {8:2,24:8,40:16}[word&255])&MASK
        elif word&0xF0FF in (0x4009,0x4019,0x4029):
            registers[n] >>= {9:2,25:8,41:16}[word&255]
        elif word&0xF0FF in (0x4000,0x4020):
            value=registers[n]
            registers[n]=(value << 1)&MASK
            sr=(sr&~1)|(value >> 31)
        elif word&0xF0FF in (0x4001,0x4021):
            value=registers[n]
            registers[n]=(value >> 1)|(value&0x80000000 if word&255==0x21 else 0)
            sr=(sr&~1)|(value&1)
        elif word&0xF0FF==0x0029:
            registers[n]=sr&1
        elif word&0xF0FF in (0x4011,0x4015):
            value=signed(registers[n])
            sr=(sr&~1)|int(value>=0 if word&255==0x11 else value>0)
        elif word&0xF00F in (0x3000,0x3002,0x3003,0x3006,0x3007):
            first,second=registers[n],registers[m]
            result={0:first==second,2:first>=second,3:signed(first)>=signed(second),
                    6:first>second,7:signed(first)>signed(second)}[low]
            sr=(sr&~1)|int(result)
        elif word&0xF00F==0x2008:
            sr=(sr&~1)|int(registers[n]&registers[m]==0)
        elif word >> 8==0x88:
            sr=(sr&~1)|int(registers[0]==signed(word&255,8)&MASK)
        elif word >> 8==0xC8:
            sr=(sr&~1)|int(registers[0]&(word&255)==0)
        elif word >> 8 in (0xCD,0xCF):
            address=(gbr+registers[0])&MASK
            value=access(pc,'read',address,1)
            value=value&(word&255) if word >> 8==0xCD else value|(word&255)
            access(pc,'write',address,1,value)
        elif word >> 8==0xCC:
            value=access(pc,'read',(gbr+registers[0])&MASK,1)
            sr=(sr&~1)|int(value&(word&255)==0)
        elif word==0x0019:
            sr&=~0x301
        elif word&0xF0FF==0x4024:
            value=registers[n]
            registers[n]=((value << 1)|(sr&1))&MASK
            sr=(sr&~1)|(value >> 31)
        elif word&0xF0FF==0x4025:
            value=registers[n]
            registers[n]=(value >> 1)|((sr&1) << 31)
            sr=(sr&~1)|(value&1)
        elif word&0xF00F==0x3004:
            registers[n],sr=divide_step(registers[m],registers[n],sr)
        elif word&0xF00F==0x2007:
            # REJ09B0316-0200, section7.2.16: initialize signed division state.
            dividend_sign,divisor_sign=registers[n] >> 31,registers[m] >> 31
            sr=(sr&~0x301)|(dividend_sign << 8)|(divisor_sign << 9)|(dividend_sign^divisor_sign)
        elif word&0xF0FF in (0x400B,0x402B):
            next_pc=transfer(registers[n],'call' if word&255==0x0B else 'jump')
        elif word >> 12 in (0xA,0xB):
            target=(pc+4+signed(word&4095,12)*2)&MASK
            next_pc=transfer(target,'call' if word >> 12==0xB else 'jump')
        elif word >> 8 in (0x89,0x8B,0x8D,0x8F):
            take=bool(sr&1) if word >> 8 in (0x89,0x8D) else not bool(sr&1)
            delay=word >> 8 in (0x8D,0x8F)
            target=(pc+4+signed(word&255,8)*2)&MASK if take else (pc+4 if delay else pc+2)
            next_pc=transfer(target,'taken' if take else 'fallthrough',delay)
        elif word==0x000B:
            next_pc=transfer(pr,'return')
        elif word==0x0009:
            pass
        else:
            raise ValueError(f'the byte-surface oracle does not admit opcode {word:04x} at {pc:08x}')
        if previous is not None and pending_call_index is not None:
            call=calls[pending_call_index]
            if call['target']!=previous:
                raise ValueError('the natural call changes its delayed entry target')
            call['entry']=dict(registers=tuple(registers[:15]),sp=registers[15],
                gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr)
            pending_call_index=None
        destination=previous if previous is not None else next_pc
        if trace:
            events.append(dict(index=len(events),site=pc,word=word,bytes=fixture[pc:pc+2].hex(),
                before=initial,after=dict(registers=tuple(registers),gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr),
                next=destination,delay_slot=previous is not None,
                accesses=[dict(row) for row in accesses[counts[0]:]],
                calls=[dict(row) for row in calls[counts[1]:]],
                branches=[dict(row) for row in branches[counts[2]:]]))
        pc=destination
    if pending is not None or pending_call_index is not None or registers[15]!=sp or pr!=continuation:
        raise ValueError('the byte-surface natural entry changes its actual terminal SP/PR or pending delay slot')
    result=dict(registers=tuple(registers[:15]),gbr=gbr,mach=mach,macl=macl,sr=sr,pr=pr,sp=sp,
        ram=bytes(ram),frame=bytes(frame),accesses=accesses,calls=calls,branches=branches,
        code=code,steps=steps,entry=entry,continuation=continuation,
        ISA_reference=dict(id=ISA_REFERENCE_ID,url=ISA_REFERENCE))
    if trace:result['trace']=events
    return result
