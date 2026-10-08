"""Independent natural signed additive entry, separate from coefficient selection."""
MASK=(1<<32)-1

def signed(value,bits):
    value&=(1<<bits)-1
    return value-(1<<bits) if value&(1<<(bits-1)) else value

def case(coefficient,term,flags,calibration,variant=0,entry_sr=0,incoming=None):
    assert 0<=coefficient<=255 and -32768<=term<=32767
    assert 0<=flags<=255 and 0<=calibration<=255 and variant in (0,1)
    assert entry_sr&~0x3f1==0
    product=coefficient*term
    quotient=abs(product)//256*(-1 if product<0 else 1)
    bounded=max(-32768,min(32767,quotient))
    zero=bool(flags&32 and calibration&4)
    output=0 if zero else bounded
    incoming=([((0x1728394a+r*0x110203) if variant==0 else
               (0x81234567+r*0x1020305))&MASK for r in range(15)]
              if incoming is None else list(incoming))
    assert len(incoming)==15 and all(type(value) is int and 0<=value<=MASK for value in incoming)
    expected=incoming.copy()
    expected[0]=expected[5]=output&MASK
    expected[2]=(32767 if quotient>=0 else -1)&MASK
    expected[6]=0x010022f8
    return {'coefficient':coefficient,'term':term,'flags':flags,'calibration':calibration,
        'variant':variant,'entry_sr':entry_sr,'product':product,'quotient':quotient,
        'zero':int(zero),'output':output&65535,'expected_t':int(not zero),
        'incoming':incoming,'expected':expected}

def matrix():
    rows=[]
    def add(**values):rows.append(case(**values))
    for coefficient,term,flags,calibration in (
        (0,-32768,0,0),(64,-32768,0,0),(64,32767,0,0),(255,-32768,0,0),
        (255,32767,0,0),(1,-1,0,0),(1,-256,0,0),(1,-257,0,0),
        (64,-5,32,4),(64,5,32,4),(64,-5,32,0),(64,-5,0,4)):
        add(coefficient=coefficient,term=term,flags=flags,calibration=calibration,
            variant=len(rows)&1,entry_sr=(len(rows)&1)|(((len(rows)>>1)&15)<<4)|((len(rows)&3)<<8))
    for raw in range(65536):
        add(coefficient=64,term=signed(raw,16),flags=0,calibration=0,
            variant=raw&1,entry_sr=(raw&1)|(((raw>>1)&15)<<4)|((raw&3)<<8))
    for coefficient in range(256):
        for term in (-32768,-32767,-513,-257,-256,-255,-1,0,1,255,256,257,32766,32767):
            for flags,calibration in ((0,0),(0,4),(32,0),(32,4),(255,255),(223,251)):
                add(coefficient=coefficient,term=term,flags=flags,calibration=calibration,
                    variant=coefficient&1,entry_sr=0x3f1 if term<0 else 0x100)
    return rows

if __name__=='__main__':
    rows=matrix()
    assert len(rows)==87052
    for row in rows:
        adjusted=(row['product']+(255 if row['product']<0 else 0))&MASK
        shifted=adjusted>>8
        reconstructed=(signed(shifted>>16,8)<<16)|(shifted&65535)
        assert reconstructed==row['quotient']
        assert -32640<=row['quotient']<=32639
    print(f'PREPARED_TRANSIENT_ADDITIVE cases={len(rows)} gnu_executed=0 accepted_points=0')
