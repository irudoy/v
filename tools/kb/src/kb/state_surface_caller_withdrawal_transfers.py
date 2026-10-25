"""Exact natural state surface caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import state_surface_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={411634: (411856, 4, 0),
 411640: (411796, 4, 2),
 411666: (411860, 4, 6),
 411674: (411864, 4, 13),
 411678: (411782, 2, 0),
 411680: (411812, 4, 14),
 411684: (411784, 2, 0),
 411690: (411786, 2, 0),
 411730: (411868, 4, 5),
 411734: (411836, 4, 7),
 411738: (411872, 4, 2),
 411744: (411876, 4, 4),
 411748: (411788, 2, 0),
 411750: (411880, 4, 5),
 411764: (411884, 4, 6),
 411772: (411782, 2, 0),
 411906: (412484, 4, 6),
 411940: (412488, 4, 6),
 411944: (412492, 4, 13),
 411950: (412180, 2, 0),
 411978: (412496, 4, 14),
 411982: (412182, 2, 0),
 412004: (412500, 4, 2),
 412012: (412184, 2, 0),
 412018: (412504, 4, 6),
 412036: (412484, 4, 6),
 412044: (412496, 4, 14),
 412048: (412182, 2, 0),
 412074: (412500, 4, 4),
 412078: (412492, 4, 13),
 412086: (412180, 2, 0),
 412092: (412184, 2, 0),
 412096: (412508, 4, 6),
 412108: (412186, 2, 2),
 412142: (412512, 4, 2),
 412150: (412180, 2, 0),
 155790: (155832, 4, 7),
 155822: (155828, 4, 7),
 156528: (156546, 2, 0),
 156536: (156548, 4, 6),
 158054: (158080, 4, 2),
 158388: (158396, 4, 6),
 157572: (157640, 4, 7)}
NATIVE_ROOTS=(('0057fd6cb20fac880f590fbd89fccd80768695872bed9c47fa438877314cec2b', 76626, None),
 ('55e5ca11aa978e3f61c1f44e450f5acc3fce0638cb0f1fdc434a77b0794c6eef', 76634, None))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# The implicit-byte entry starts at26A80 inside the full normal26A60 parent.
# Its literal224 becomes0 after SHLR8, so the word-cell sibling is excluded.
# The backward raw-axis scan selects a positive adjacent bracket even for
# unordered bytes. Its real fractional divider has no zero-divisor path.
# The split products are unsigned bytes, and floor(a*b/256)<=b; the exact
# negative adjustment and residual-clamp instructions are therefore excluded.
INFEASIBLE_SITES=(set(range(0x26A60,0x26A80,2))|set(range(0x26A9C,0x26AAA,2))
    |set(range(0x26D0A,0x26D0E,2))|set(range(0x6493E,0x64944,2))|{0x64960})
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
    same(observed['exit'],wanted,'the state surface caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the state surface caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the state surface caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the state surface caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the state surface caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the state surface caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the state surface caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the state surface caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the state surface caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the state surface caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the state surface caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the state surface caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the state surface caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the state surface caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the state surface caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the state surface caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Complete actual entry state remains bound to the instruction trace.
        # Only the fractional-divider Q/T flags use their explicit scalar mask.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the state surface caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the state surface caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the state surface caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the state surface caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the state surface caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the state surface caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the state surface caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the state surface caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the state surface caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the state surface caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the state surface caller physically accesses a selected unsupported ROM/native-RAM root or alias')
