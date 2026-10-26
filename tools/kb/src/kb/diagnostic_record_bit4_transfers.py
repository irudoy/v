"""Complete independent physical, CPU, index, sign-extension and RTS-delay bindings."""
from kb import test_contract
from kb import diagnostic_record_bit4_semantics as semantics

EXACT_SITES=set(semantics.PATH)
FEASIBLE_SITES=EXACT_SITES
INFEASIBLE_SITES=set()
FIXED_BRANCHES={}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the bit4 writer changes complete independently reconstructed instruction exit state')
    same(observed['exit'],value['exit'],'the bit4 writer changes separate full-register and SR equations')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the bit4 writer changes complete independent CPU-frame or computed RAM publication state')
    same(result['accesses'],value['operands'],'the bit4 writer changes ordered exact ROM/RAM site, address, width, register or bytes')
    same(result['branches'],value['branches'],'the bit4 writer changes its natural RTS continuation or delay')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the bit4 writer changes a complete stock instruction or feasible path')
    if result['calls']:raise ValueError('the bit4 leaf invents an external stock call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the bit4 writer omits its complete natural instruction trace')
    initial=dict(registers=(*observed['context'][:15],observed['sp']),gbr=observed['context'][15],
        mach=observed['context'][16],macl=observed['context'][17],sr=observed['sr_before'],pr=observed['continuation'])
    same(trace[0]['before'],initial,'the bit4 writer detaches complete actual incoming CPU state')
    for index,row in enumerate(trace):
        expected=value['states'][row['site']]
        same(row['after'],expected,'the bit4 writer changes an independent complete intermediate register or special-state carrier')
        if index:
            same(row['before'],trace[index-1]['after'],'the bit4 writer detaches ordered intermediate instruction state')
        target=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['next']!=target or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the bit4 writer replaces a natural stock instruction or continuation')
    if {row['site'] for row in trace if row['delay_slot']}!={0x8C982}:
        raise ValueError('the bit4 writer omits or relocates its real RTS-delay byte publication')
    same(tuple(result[key] for key in ('sp','pr','gbr','mach','macl')),
        (observed['sp'],observed['continuation'],*observed['context'][15:18]),
        'the bit4 writer changes complete natural return stack or preserved special state')
