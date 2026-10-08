"""Independent full-width arithmetic of the natural base accumulator."""
MASK=(1<<32)-1

def signed32(value):
    value&=MASK
    return value-(1<<32) if value&(1<<31) else value

def case(index,term,conditional,coolant,variant=0,entry_sr=0):
    assert 0<=term<=MASK and 0<=conditional<=65535 and 0<=coolant<=65535
    assert variant in (0,1) and entry_sr&~0x3f1==0
    first=(term+16384)&MASK
    total=(first+conditional+coolant)&MASK
    upper=int(signed32(total)>65535)
    selected=65535 if upper else total
    negative=int(signed32(selected)<0)
    output=0 if negative else selected
    incoming=[((0x1728394a+r*0x110203) if variant==0 else
               (0x81234567+r*0x1020305))&MASK for r in range(15)]
    expected=incoming.copy()
    expected[0]=output
    expected[1]=0x0100128c
    expected[2]=output
    expected[4]=conditional
    expected[5]=first if upper else total
    expected[6]=65535
    expected[7]=coolant
    return {'term':term,'conditional':conditional,'coolant':coolant,
        'variant':variant,'entry_sr':entry_sr,'total':total,'upper':upper,
        'negative':negative,'output':output,'expected_t':1-negative,
        'incoming':incoming,'expected':expected}

def matrix():
    rows=[]
    def add(**values):rows.append(case(len(rows),**values))
    for term,conditional,coolant in (
        (0,0,0),(49150,0,0),(49151,0,0),(49152,0,0),
        (0x7fffbfff,0,0),(0x7fffc000,0,0),(0xffffbfff,0,0),
        (0xffffc000,0,0),(0xffffffff,65535,65535),
        (0x7fffbffe,1,0),(0x7fffbffe,2,0),(0x80000000,65535,65535)):
        add(term=term,conditional=conditional,coolant=coolant,variant=len(rows)&1,
            entry_sr=(len(rows)&1)|(((len(rows)>>1)&15)<<4)|((len(rows)&3)<<8))
    for conditional in range(65536):
        add(term=0,conditional=conditional,coolant=0,variant=conditional&1,
            entry_sr=(conditional&1)|(((conditional>>1)&15)<<4)|((conditional&3)<<8))
    for coolant in range(65536):
        add(term=0,conditional=0,coolant=coolant,variant=coolant&1,
            entry_sr=(coolant&1)|(((coolant>>1)&15)<<4)|((coolant&3)<<8))
    for conditional,coolant in ((0,0),(1,0),(0,1),(32767,32768),(65535,65535)):
        for boundary in (0,65535,1<<31,1<<32):
            for delta in (-2,-1,0,1,2):
                term=(boundary-16384-conditional-coolant+delta)&MASK
                for variant in range(2):
                    for sr in (0,1,0xf0,0xf1,0x100,0x301,0x3f0,0x3f1):
                        add(term=term,conditional=conditional,coolant=coolant,
                            variant=variant,entry_sr=sr)
    return rows

def arithmetic(term,conditional,coolant):
    total=(term+16384+conditional+coolant)&MASK
    return max(0,min(65535,total-(1<<32)*(total//(1<<31))))

if __name__=='__main__':
    rows=matrix()
    for row in rows:assert row['output']==arithmetic(row['term'],row['conditional'],row['coolant'])
    before=case(0,0x7fffbfff,0,0)['output']
    after=case(1,0x7fffc000,0,0)['output']
    assert (before,after)==(65535,0)
    print('ACCUMULATOR_ORACLE cases='+str(len(rows))+' wrap_direction_witness=65535,0 GNU_executions=0')
