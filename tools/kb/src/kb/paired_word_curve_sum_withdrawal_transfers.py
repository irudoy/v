"""Exact natural paired word curve sum/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import paired_word_curve_sum_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={470086: (470268, 4, 0),
 470092: (470272, 4, 6),
 470106: (470268, 4, 7),
 470108: (470260, 2, 0),
 470110: (470276, 4, 4),
 470150: (470268, 4, 7),
 470152: (470262, 2, 0),
 470154: (470280, 4, 6),
 470182: (470284, 4, 14),
 470186: (470288, 4, 12),
 470190: (470292, 4, 13),
 470194: (470296, 4, 2),
 470210: (470296, 4, 2),
 470236: (470268, 4, 7),
 470238: (470262, 2, 0),
 470242: (470264, 2, 0),
 156972: (157004, 4, 7),
 156992: (157000, 4, 6),
 158118: (158144, 4, 2)}
NATIVE_ROOTS=(('782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b', 37932, None),)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Every caller and curve/axis/interpolation instruction is feasible. The only
# excluded instructions are the complete helper's zero-divisor return,which
# the rightmost actual positive fractional bracket cannot enter.
INFEASIBLE_SITES={0x26D0A,0x26D0C}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES
NATIVE_SPANS=(('782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b',0x942C,2),)


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
    same(observed['exit'],wanted,'the paired word curve sum changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the paired word curve sum changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the paired word curve sum changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the paired word curve sum changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the paired word curve sum changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the paired word curve sum changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the paired word curve sum omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the paired word curve sum detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the paired word curve sum changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the paired word curve sum changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the paired word curve sum changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the paired word curve sum changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the paired word curve sum leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the paired word curve sum detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the paired word curve sum omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the paired word curve sum changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Complete actual entry state remains bound to the instruction trace.
        # Fractional DIV1 Q/T remain checked by the complete independent instruction oracle;the separate scalar mask retains every independently known SR bit.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the paired word curve sum changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the paired word curve sum changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the paired word curve sum changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the paired word curve sum replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the paired word curve sum detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the paired word curve sum omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the paired word curve sum changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the paired word curve sum changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the paired word curve sum changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the paired word curve sum substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<first+size and first<event['address']+event['width_bytes']
                for identity,first,size in NATIVE_SPANS):
            raise ValueError('the paired word curve caller directly accesses either byte of the selected existing scalar')
