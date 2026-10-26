"""Complete reset CPU/frame/calls and separate actual physical native effects."""
from kb import test_contract
from kb import diagnostic_state_reset_writer_contract as contract,diagnostic_state_reset_writer_matrix as matrix
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
FEASIBLE_SITES=EXACT_SITES
INFEASIBLE_SITES=set()
CONDITIONAL_SITES=(0x2E784,0x2E796,0x2E7A8,0x2E7BA,0x2E7CC,0x2E7DC,0x2E7EC,0x2E7FE,
    0x2E83C,0x2E850,0x2E860,0xCD7BC,0xCD7FE)
FIXED_BRANCHES={}
NATIVE_WORD_SITES=(0xCD812,0xCD816,0xCD81A,0xCD81E,0xCD82A,0xCD82E,0xCD832,0xCD836)


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the reset changes the complete independently reconstructed actual exit CPU/SR')
    same(observed['exit'],value['exit'],'the reset changes separate complete numerical and carrier equations')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(value['ordinary_ram'],) or observed['native_after']!=value['native_after']
            or matrix.logical(observed['memory_after'][0],observed['native_after'])!=result['ram']
            or result['ram']!=value['ram']):
        raise ValueError('the reset changes complete ordinary RAM, separate actual native banks or the real frame')
    same(result['accesses'],value['operands'],'the reset changes an ordered exact PC/address/width/register/mode/byte operand')
    same(result['branches'],value['branches'],'the reset changes a complete real loop, conditional, call, jump, return or delay')
    same(result['calls'],value['calls'],'the reset changes a real caller/helper full CPU, SR, PR, SP or delayed argument boundary')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the reset changes exact executed instructions or admits its internal literal as code')
    trace=result.get('trace')
    if type(trace) is not list or len(trace)!=len(value['steps']):
        raise ValueError('the reset omits or duplicates a complete instruction, loop iteration or real delay slot')
    keys=('site','before','after','branches','accesses','calls','delay_slot','next')
    for actual,expected in zip(trace,value['steps']):
        same({key:actual[key] for key in keys},expected,
            'the reset changes independent intermediate CPU/SR/GBR/PR/MACH/MACL/frame-pointer or attached physical/call state')
        site=actual['site']
        if actual['word']!=int.from_bytes(fixture[site:site+2],'big') or actual['bytes']!=fixture[site:site+2].hex():
            raise ValueError('the reset substitutes a real stock instruction or delay')
        if actual['after']['sr']&~1!=observed['sr_before']&~1:
            raise ValueError('the reset changes full SR controls outside its real comparison T-bit effects')
    if (result['sp'],result['pr'],result['gbr'],result['mach'],result['macl'])!=(observed['sp'],observed['continuation'],*observed['context'][15:18]):
        raise ValueError('the reset changes the complete natural outer SP/PR/GBR/MACH/MACL')
    if any(result['registers'][register]!=observed['context'][register] for register in (3,*range(8,15))):
        raise ValueError('the reset replaces a complete preserved register or the full saved outer R14')
    if [(row['site'],row['target'],row['return_address'],row['sp']) for row in result['calls']]!=[
            (0x2E824,0x2E76E,0x2E828,observed['sp']-12),(0x2E884,0xCD75C,0x2E888,observed['sp']-12)]:
        raise ValueError('the reset changes either complete unconditional natural call or its real saved outer frame')
    second=result['calls'][1]
    if second['registers'][4]!=2 or second['entry']['registers'][4]!=value['callee_argument']:
        raise ValueError('the reset substitutes the actual pre-delay R4 or full post-delay raw-byte call argument')
    frames=[row for row in result['accesses'] if row['domain']=='frame']
    if ([row['address'] for row in frames if row['mode']=='write']!=[observed['sp']-offset for offset in (4,8,12,16,20,24)]
            or [row['address'] for row in frames if row['mode']=='read']!=[observed['sp']-offset for offset in (24,20,16,12,8,4)]
            or any(row['width_bytes']!=4 for row in frames)):
        raise ValueError('the reset changes a complete real parent/callee R14,PR,GBR or MACL frame slot')
    native=[row for row in result['accesses'] if row['domain']=='native-io']
    if any(not any(row['site']==permission['site'] and row['width_bytes']==permission['width_bytes']
            and row['mode'] in permission['modes']
            and permission['start']<=row['address']<=permission['end']-row['width_bytes']
            for permission in contract.PERMISSIONS) for row in native):
        raise ValueError('the reset widens an exact ROM-bound native PC/address/width/mode permission')
    target=[row for row in result['accesses'] if row['address']<=0xFFFF99DE<row['address']+row['width_bytes']]
    same(target,[dict(site=0x2E84A,mode='write',address=0xFFFF99DE,width_bytes=1,register=14,domain='native-io',bytes='00')],
        'the reset omits or replaces its one exact actual99DE constant-zero byte store')
    loop=[row for row in trace if row['site']==0x2E84A]
    if (len(loop)!=24 or [row['before']['registers'][4] for row in loop]!=list(range(0xFFFF99DC,0xFFFF99F4))
            or any(row['before']['registers'][14]!=0 or row['before']['registers'][6]!=index+1 for index,row in enumerate(loop))):
        raise ValueError('the reset detaches the exact99DE store from its real full R14, pointer, counter or loop position')
    words=[row for row in native if row['site'] in NATIVE_WORD_SITES]
    if value['gate']:
        wanted=[(0xFFFFF588,value['products'][0]),(0xFFFFF590,0),(0xFFFFF58A,value['products'][0]),(0xFFFFF592,0),
            (0xFFFFF58C,value['products'][1]),(0xFFFFF594,0),(0xFFFFF58E,value['products'][1]),(0xFFFFF596,0)]
        same([(row['site'],row['address'],row['bytes'],row['register']) for row in words],
            [(site,address,integer.to_bytes(2,'big').hex(),0) for site,(address,integer) in zip(NATIVE_WORD_SITES,wanted)],
            'the reset changes independent ordered raw-ROM products or zero native halfword publications')
    elif words:
        raise ValueError('the reset invents a native halfword publication on the real inhibited path')
    if (trace[-2]['site'],trace[-1]['site'],trace[-1]['delay_slot'],trace[-1]['next'])!=(0x2E8A4,0x2E8A6,True,observed['continuation']):
        raise ValueError('the reset replaces its complete real outer RTS-delay R14/SP restoration')
    return True
