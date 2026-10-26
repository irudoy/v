"""Complete independent physical, CPU, index, sign-extension and RTS-delay bindings."""
from kb import test_contract
from kb import diagnostic_record_highbit_clear_semantics as semantics

EXACT_SITES=set(semantics.ACTIVE_PATH)|set(semantics.SENTINEL_PATH)
FEASIBLE_SITES=EXACT_SITES
INFEASIBLE_SITES=set()
FIXED_BRANCHES={}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the high-bit clearer changes complete independently reconstructed instruction exit state')
    same(observed['exit'],value['exit'],'the high-bit clearer changes separate full-register and SR equations')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the high-bit clearer changes complete independent CPU-frame or computed RAM publication state')
    same(result['accesses'],value['operands'],'the high-bit clearer changes ordered exact ROM/RAM site, address, width, register or bytes')
    same(result['branches'],value['branches'],'the high-bit clearer changes its natural RTS continuation or delay')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the high-bit clearer changes a complete stock instruction or feasible path')
    if result['calls']:raise ValueError('the high-bit clear leaf invents an external stock call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the high-bit clearer omits its complete natural instruction trace')
    initial=dict(registers=(*observed['context'][:15],observed['sp']),gbr=observed['context'][15],
        mach=observed['context'][16],macl=observed['context'][17],sr=observed['sr_before'],pr=observed['continuation'])
    same(trace[0]['before'],initial,'the high-bit clearer detaches complete actual incoming CPU state')
    for index,row in enumerate(trace):
        expected=value['states'][row['site']]
        same(row['accesses'],[event for event in value['operands'] if event['site']==row['site']],
            'the high-bit clearer detaches an actual per-instruction physical operand')
        same(row['after'],expected,'the high-bit clearer changes an independent complete intermediate register or special-state carrier')
        if index:
            same(row['before'],trace[index-1]['after'],'the high-bit clearer detaches ordered intermediate instruction state')
        target=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['next']!=target or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()):
            raise ValueError('the high-bit clearer replaces a natural stock instruction or continuation')
    if {row['site'] for row in trace if row['delay_slot']}!={0x8C364 if value['inert'] else 0x8C360}:
        raise ValueError('the high-bit clearer omits or relocates its real RTS-delay byte publication')
    same(tuple(result[key] for key in ('sp','pr','gbr','mach','macl')),
        (observed['sp'],observed['continuation'],*observed['context'][15:18]),
        'the high-bit clearer changes complete natural return stack or preserved special state')
