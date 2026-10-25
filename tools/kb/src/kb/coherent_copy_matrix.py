"""Independent bounded caller equations for the remaining coherent RAM copies.

Native claims, descriptor admission and actual GNU execution are separate gates.
The model preserves declared member widths rather than deriving them from copies.
"""
from dataclasses import dataclass
from itertools import product

MASK=0xffffffff
RAM_BASE=0x01000000
ABI=[0x18283848,0x19293949,0x1a2a3a4a,0x1b2b3b4b,0x1c2c3c4c,
     0x1d2d3d4d,0x1e2e3e4e,0x12344321,0x10203040,0x50607080]
BASE_RAM=bytes((0x5d+i*19+(i>>8))&255 for i in range(65536))

@dataclass(frozen=True)
class Window:
    entry:int
    call:int
    helper:int
    source:int
    destination:int
    length:int
    context:tuple
    history:tuple
    r4:int|None
    r6:int|None

WINDOWS=(
 Window(0x20f04,0x20f18,0x22104,0xffff1048,0xffff102c,28,(),
        ((0xffff1024,0xffff1028,2),(0xffff1026,0xffff1024,2)),0xffff1024,0x22104),
 Window(0x20f1c,0x20f36,0x22558,0xffff1072,0xffff106a,8,((11,0x22558),),
        ((0xffff1064,0xffff1068,2),(0xffff1066,0xffff1064,2)),0xffff1064,0xffff1066),
 Window(0x20f3a,0x20f56,0x22038,0xffff1114,0xffff1094,128,((9,0x22038),(12,240)),
        ((0xffff1082,0xffff108a,4),(0xffff1086,0xffff1082,4)),0xffff1082,0xffff1086),
 Window(0x20f5a,0x20f6c,0x220f8,0xffff11d4,0xffff119c,56,((14,0x220f8),),
        ((0xffff1194,0xffff1198,2),(0xffff1196,0xffff1194,2)),0xffff1194,0xffff1196),
 Window(0x20f70,0x20f7c,0x22558,0xffff120e,0xffff124c,62,((11,0x22558),),
        ((0xffff120d,0xffff120c,1),),None,0xffff120c),
 Window(0x20fa4,0x20fcc,0x22558,0xffff277e,0xffff267a,260,((11,0x22558),),
        ((0xffff2668,0xffff266c,2),(0xffff266a,0xffff2668,2),(0xffff2672,0xffff266e,4)),0xffff266e,0xffff2672),
 Window(0x2104e,0x2105a,0x22558,0xffff246a,0xffff246d,3,((11,0x22558),),
        ((0xffff2465,0xffff2464,1),),None,0xffff2464),
 Window(0x2130c,0x21310,0x22558,0xffff2324,0xffff232a,6,((11,0x22558),),(),None,None),
 Window(0x2131c,0x2132c,0x22038,0xffff4124,0xffff40cc,88,((9,0x22038),),
        ((0xffff40c6,0xffff40c4,2),(0xffff40c6,0xffff40c8,2)),None,0xffff40c8),
 Window(0x21330,0x21334,0x22558,0xffff56b2,0xffff564c,102,((11,0x22558),),(),None,None),
 Window(0x21338,0x21348,0x22558,0xffff24ce,0xffff24c8,6,((11,0x22558),),
        ((0xffff24c6,0xffff24c5,1),(0xffff24c6,0xffff24c7,1)),None,0xffff24c7),
 Window(0x20bce,0x20bd0,0x220f8,0xffff1dec,0xffff1e04,24,
        ((1,0x01001e04),(9,0x220f8)),(),None,None),
 Window(0x20cb8,0x20cba,0x22558,0xffff1072,0xffff107a,8,
        ((1,0x0100107a),(5,0x22558)),(),None,None),
 Window(0x20cdc,0x20cdc,0x22558,0xffff1e50,0xffff1e58,8,
        ((1,0x01001e58),(2,0x01001e50),(4,0x22558)),(),None,None),
 Window(0x20ce0,0x20ce6,0x22558,0xffff39a4,0xffff39b4,16,
        ((5,0x22558),),(),None,None),
)

def alias(address):
    return RAM_BASE+(address&65535) if address>=0xffff0000 else address

def read_addresses(window):
    extra=4 if window.helper==0x22038 else 0
    addresses=set(range(window.source,window.source+window.length+extra))
    for source,_,size in window.history:
        addresses.update(range(source,source+size))
    return tuple(sorted(addresses))

def cases(window):
    """Complete affine, isolated-lane and successive-state ordered cases."""
    rows=[dict(seed=seed,variant=variant,t=t,isolated=None,carry=False)
          for seed,variant,t in product(range(256),range(2),range(2))]
    rows.extend(dict(seed=0,variant=variant,t=(offset+variant)&1,isolated=address,carry=False)
                for offset,address in enumerate(read_addresses(window)) for variant in range(2))
    rows.extend(dict(seed=seed,variant=variant,t=t,isolated=None,carry=carry)
                for variant,t in product(range(2),range(2))
                for seed,carry in ((0,False),(128,True),(255,True)))
    return [dict(index=index,call=window.call,**row) for index,row in enumerate(rows)]

def early_indices(window):
    rows=cases(window);addresses=read_addresses(window)
    selected={0,1023,1024,1024+2*(len(addresses)-1),len(rows)-12,len(rows)-11,len(rows)-10}
    for at in (0xffff1083,0xffff1087,window.source+window.length):
        if at in addresses:selected.add(1024+2*addresses.index(at))
    return tuple(sorted(selected))

def render_header(pool_addresses):
    """Canonical C input bytes; no expected MCU output is supplied to the driver."""
    if type(pool_addresses) is not list or len(pool_addresses)!=len(WINDOWS):
        raise ValueError('each bounded caller requires its exact pool set')
    lines=['/* Bounded coherent-copy inputs; semantic expectations stay in the host oracle. */',
        'struct coherent_case { uint32_t index, seed, variant, entry_t, isolated, carry; };',
        'struct coherent_window {',
        '    uint32_t entry, call, helper, source, destination, length, context_mask;',
        '    uint32_t context[15];',
        '    unsigned read_start, read_count, pool_start, pool_count, case_start, case_count, early_start, early_count;',
        '};']
    case_rows=[];read_rows=[];pool_rows=[];early_rows=[];window_rows=[]
    for window,pools in zip(WINDOWS,pool_addresses):
        rows=cases(window);addresses=read_addresses(window);early=early_indices(window)
        context=[0]*15
        for register,value in window.context:context[register]=value
        mask=sum(1<<register for register,_ in window.context)
        window_rows.append((window,mask,context,len(read_rows),len(addresses),len(pool_rows),
            len(pools),len(case_rows),len(rows),len(early_rows),len(early)))
        case_rows.extend([row['index'],row['seed'],row['variant'],row['t'],
            0xffffffff if row['isolated'] is None else row['isolated'],int(row['carry'])] for row in rows)
        read_rows.extend(addresses);pool_rows.extend(pools);early_rows.extend(early)
    vector=lambda values:'{'+','.join(f'0x{value:x}U' for value in values)+'}'
    lines+=['static const struct coherent_case coherent_cases[] = {']
    lines.extend('    '+vector(row)+',' for row in case_rows)
    lines+=['};','static const uint32_t coherent_read_addresses[] = '+vector(read_rows)+';',
        'static const uint32_t coherent_pool_addresses[] = '+vector(pool_rows)+';',
        'static const unsigned coherent_early_indices[] = '+vector(early_rows)+';',
        'static const struct coherent_window coherent_windows[] = {']
    for window,mask,context,*offsets in window_rows:
        values=[window.entry,window.call,window.helper,window.source,window.destination,window.length,mask]
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+','+vector(context)+','+
            ','.join(str(value)+'U' for value in offsets)+'},')
    lines+=['};',f'#define COHERENT_WINDOW_COUNT {len(window_rows)}U',
        f'#define COHERENT_CASE_COUNT {len(case_rows)}U',f'#define COHERENT_EARLY_COUNT {len(early_rows)}U','']
    return '\n'.join(lines)

def incoming(window,case):
    variant=case['variant']
    values=[((0xa9876543+i*0x00130709) if variant else (0x28765430+i*0x01030507))&MASK
            for i in range(15)]
    values[7]=window.entry
    for register,value in window.context:
        values[register]=value
    return values

def special(case):
    return ([0xd8b6a491,0xf1e2d3c4,0x9274b6d8] if case['variant']
            else [0x456789ab,0x13579bdf,0x2468ace0])

def seed(window,case,previous=None):
    if case['carry']:
        if previous is None or len(previous)!=65536:
            raise ValueError('successive copy requires the exact prior full RAM state')
        memory=bytearray(previous)
    else:
        translation=bytes((value+case['index'])&255 for value in range(256))
        memory=bytearray(BASE_RAM.translate(translation))
    addresses=read_addresses(window)
    for offset,address in enumerate(addresses):
        memory[address&65535]=(0x81*int(address==case['isolated']) if case['isolated'] is not None
                              else (case['seed']+offset*29)&255)
    return memory

def expected(window,case,before,continuation):
    """Compute byte transfers and complete final GPRs independently of assembly."""
    memory=bytearray(before)
    registers=incoming(window,case)
    for source,destination,size in window.history:
        source&=65535;destination&=65535
        memory[destination:destination+size]=memory[source:source+size]
    source=window.source&65535
    destination=window.destination&65535
    memory[destination:destination+window.length]=memory[source:source+window.length]
    registers[1]=alias(window.destination)
    registers[2]=alias(window.source)
    registers[7]=continuation
    if window.r4 is not None:
        registers[4]=alias(window.r4)
    if window.r6 is not None:
        registers[6]=alias(window.r6)
    if window.helper==0x22558:
        value=memory[source+window.length-1]
        registers[0]=(value if value<128 else value-256)&MASK
        registers[1]+=4*(window.length//4)
        final_t=0
    elif window.helper==0x22038:
        registers[0]=int.from_bytes(memory[source+window.length:source+window.length+4],'big')
        registers[1]+=window.length
        final_t=0
    else:
        registers[0]=int.from_bytes(memory[source+4:source+8],'big')
        final_t=case['t']
    return registers,final_t,memory

def frame(window,case,before):
    result=bytearray(before)
    values=incoming(window,case)
    def store(offset,value):result[offset:offset+4]=value.to_bytes(4,'big')
    if window.helper==0x22558:
        store(60,alias(window.source))
        store(56,values[3])
        store(52,alias(window.r4) if window.r4 is not None else values[4])
    else:
        store(60,values[3])
        if window.helper==0x22038:
            store(56,alias(window.source))
    return result

def initial_frame(continuation):
    result=bytearray(b''.join((0xa3b4c5d6+17*i).to_bytes(4,'big') for i in range(24)))
    result[88:92]=continuation.to_bytes(4,'big')
    return result

def _words(value,count):
    if type(value) is not list or len(value)!=count or any(
            type(v) is not int or not 0<=v<=MASK for v in value):
        raise ValueError('actual register vector shape changes')
    return value

def _bytes(value,count):
    if type(value) is not str or len(value)!=2*count or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('actual byte vector shape changes')
    return bytes.fromhex(value)

def validate_observation(window,case,observed,pools,previous=None):
    """Validate actual captured MCU state; an expected-only packet is insufficient."""
    fields={'index','call','entry','source','destination','length','incoming','incoming_after',
        'gbr','mach','macl','entry_t','gbr_after','mach_after','macl_after','entry_t_after',
        'exit','sp','continuation','sr_before','abi_before','abi_after','frame_before','frame_after',
        'read_before','read_after','destination_before','destination_after',
        'pools_before','pools_after','outside_changes'}
    if type(observed) is not dict or set(observed)!=fields:
        raise ValueError('actual copy packet fields change')
    expected_identity=[case['index'],window.call,window.entry,window.source,window.destination,window.length]
    if [observed[k] for k in ('index','call','entry','source','destination','length')]!=expected_identity:
        raise ValueError('actual copy identity changes')
    for key in ('index','call','entry','source','destination','length','sp','continuation','sr_before'):
        if type(observed[key]) is not int or not 0<=observed[key]<=MASK:
            raise ValueError('actual unsigned scalar shape changes')
    context=incoming(window,case)
    if _words(observed['incoming'],15)!=context or _words(observed['incoming_after'],15)!=context:
        raise ValueError('actual prepared entry context differs or mutates')
    specials=special(case)
    for key,value in zip(('gbr','mach','macl','entry_t'),[*specials,case['t']]):
        if type(observed[key]) is not int or observed[key]!=value or type(observed[key+'_after']) is not int or observed[key+'_after']!=value:
            raise ValueError('actual prepared special registers differ or mutate')
    before=seed(window,case,previous)
    gpr,t,after=expected(window,case,before,observed['continuation'])
    addresses=read_addresses(window)
    for key,memory in (('read_before',before),('read_after',after)):
        if _bytes(observed[key],len(addresses))!=bytes(memory[at&65535] for at in addresses):
            raise ValueError('actual read lanes or read-ahead differ')
    destination=window.destination&65535
    for key,memory in (('destination_before',before),('destination_after',after)):
        if _bytes(observed[key],window.length)!=memory[destination:destination+window.length]:
            raise ValueError('actual destination lanes differ')
    outside=[[i,before[i],after[i]] for i in range(65536)
             if not destination<=i<destination+window.length and before[i]!=after[i]]
    if observed['outside_changes']!=outside or any(type(v) is not int for row in observed['outside_changes'] for v in row):
        raise ValueError('actual full RAM footprint differs')
    out=_words(observed['exit'],20)
    if [out[19-r] for r in range(15)]!=gpr:
        raise ValueError('actual complete GPR state differs')
    sr=observed['sr_before']
    if sr&0x301!=case['t'] or out[:5]!=[(sr&~1)|t,observed['continuation'],specials[2],specials[1],specials[0]]:
        raise ValueError('actual SR, natural return boundary or specials differ')
    abi=_words(observed['abi_before'],12)
    if abi[:10]!=ABI or abi!=_words(observed['abi_after'],12) or observed['sp']!=(abi[10]-164)&MASK:
        raise ValueError('actual C ABI or stack boundary differs')
    frame_before=_bytes(observed['frame_before'],96)
    if frame_before!=initial_frame(observed['continuation']):
        raise ValueError('actual prepared stack seed or outer continuation differs')
    if _bytes(observed['frame_after'],96)!=frame(window,case,frame_before):
        raise ValueError('actual helper frame or neighboring bytes differ')
    if type(pools) is not bytes:
        raise ValueError('the declared relocated pools require exact bytes')
    if _bytes(observed['pools_before'],len(pools))!=pools or _bytes(observed['pools_after'],len(pools))!=pools:
        raise ValueError('actual declared data or dispatch pools differ or mutate')
    return after
