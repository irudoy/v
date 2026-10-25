"""Exact natural actuator mask access/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import actuator_mask_access_contract as contract
RAM_BASE=0x01000000
ROM={330096: (330520, 4, 6),
 330106: (330520, 4, 6),
 330108: (330328, 2, 4),
 330144: (330516, 4, 6),
 330218: (330524, 4, 5),
 155168: (155408, 4, 1)}
NATIVE_ROOTS=(('ea1447c432b526ee404d11837a8ebcf90ae1d1995bc53372dc5f1ca87c229166', 4294924056, 16799512),)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Both caller-supplied positive record IDs exclude only the -1 return instruction.
INFEASIBLE_SITES={0x25E3E}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    events=[]
    for index,site in enumerate(value['path']):
        if index in value['events']:
            event=value['events'][index]
            events.append(event);continue
        if site in ROM:
            address,width,register=ROM[site]
            events.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
    return events


def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the actuator mask access changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the actuator mask access changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the actuator mask access changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the actuator mask access changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the actuator mask access changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the actuator mask access changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the actuator mask access omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the actuator mask access detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the actuator mask access changes a separate natural branch, threshold, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the actuator mask access changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the actuator mask access changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the actuator mask access changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the actuator mask access leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the actuator mask access detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the actuator mask access omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the actuator mask access changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Complete actual entry state remains bound to the instruction trace.
        # Every independent byte helper keeps the complete known scalar SR mask.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the actuator mask access changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the actuator mask access changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the actuator mask access changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the actuator mask access replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the actuator mask access detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the actuator mask access omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the actuator mask access changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the actuator mask access changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the actuator mask access changes complete natural post-delay returned state')


def require_fixed_record_reads(result):
    """Retain the existing array dependency through each actual fixed-ID member."""
    calls=[row for row in result['calls'] if row['target']==0x25E20]
    ids=tuple(row['entry']['registers'][4] for row in calls)
    if ids not in ((0x71,),(0x71,0x123)):
        raise ValueError('the actuator mask changes its complete ordered post-delay diagnostic record IDs')
    reads=[row for row in result['accesses'] if row['site']==0x25E32]
    same(tuple((row['mode'],row['address'],row['width_bytes'],row['register'],row['domain']) for row in reads),
        tuple(('read',RAM_BASE+0x5718+3*identifier+1,1,0,'ram') for identifier in ids),
        'the actuator mask omits or substitutes a proven diagnostic-array member dependency')
    return tuple(0xFFFF5718+3*identifier+1 for identifier in ids)
