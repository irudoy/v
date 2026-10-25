"""Existing base-pulse scalar equations over complete explicit input memory."""


def evaluate(before,bank,flag1,flag2):
    if (type(before) is not bytes or len(before)!=65536 or type(bank) is not int or bank not in (0,1)
            or any(type(value) is not int or not 0<=value<=255 for value in (flag1,flag2))):
        raise ValueError('the bank-pulse equations need complete RAM, one legal bank and exact flag bytes')
    def word(offset):return int.from_bytes(before[offset:offset+2],'big')
    shift=bank*2
    s,l,e=word(0x22DC+shift),word(0x2302+shift),word(0x2A24+shift)
    precursor,additive,offset=word(0x18C0+shift),word(0x2436),word(0x2310+shift)
    control_address=0x22E8 if flag2&16 else 0x22E6
    control=word(control_address)
    include_l=bool(flag1&2) or control<=16384
    trim=max(0,s+(l if include_l else 0)+e-25600*(1+int(include_l)))
    product=(precursor*trim)&0xFFFFFFFF
    intermediate=additive+(product//65536)
    corrected=((256*intermediate+offset-32768)&0xFFFFFFFF)//256 if precursor else intermediate
    output=min(65535,corrected)
    memory=bytearray(before);at=0x191C+shift;memory[at:at+2]=output.to_bytes(2,'big')
    return dict(memory=bytes(memory),bank=bank,s=s,l=l,e=e,precursor=precursor,additive=additive,
        offset=offset,control=control,control_address=control_address,include_l=include_l,
        trim=trim,product=product,intermediate=intermediate,corrected=corrected,output=output,
        exit_t=int(corrected>65535))
