"""Exact natural word caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import word_interp_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={156338: (156380, 4, 7),
 156370: (156376, 4, 7),
 157468: (157500, 4, 7),
 157488: (157496, 4, 6),
 157790: (157856, 4, 7),
 158118: (158144, 4, 2),
 158630: (158656, 4, 2),
 470816: (471072, 4, 5),
 470820: (471060, 4, 7),
 470824: (471042, 2, 0),
 470844: (471076, 4, 4),
 470846: (471080, 4, 2),
 470854: (471060, 4, 7),
 470856: (471044, 2, 0),
 470876: (471084, 4, 4),
 470878: (471088, 4, 5),
 470880: (471080, 4, 2),
 470888: (471060, 4, 7),
 470890: (471044, 2, 0),
 752550: (752704, 4, 5),
 752554: (752708, 4, 6),
 752558: (752712, 4, 4),
 752562: (752716, 4, 3),
 752588: (752664, 4, 5),
 752590: (752630, 2, 0)}
NATIVE_ROOTS=(('4b97eb1e73817d75504aa38835796a7d10bb9268be350a5b62dda81c5f001cc6', 95688, None),
 ('ae1c5d03bbbaed09e5d8c4437305e27d646d11b5ce31b4186ccb46bc80db691c', 4294905892, 16781348),
 ('600906141f73792784d0da8ded0b5c30d632c7a90d94e1df0c6935fd7c872775', 4294906300, 16781756),
 ('61ff5c17a1c2a129ea4a3395359986ede8da0aef857bb6d6fc706cf8c2f0a8a9', 4294909200, 16784656),
 ('7cc39463a836a76598dd58578359fb7812eeeb0f673f03852f25d3e7639cd15d', 4294915582, 16791038))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
INFEASIBLE_SITES={0x72F3A,0x26D0A,0x26D0C,0x26DA2,0x26DA4}
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    events=[]
    for index,site in enumerate(value['path']):
        if index in value['events']:
            events.append(value['events'][index]);continue
        if site in ROM:
            address,width,register=ROM[site]
            events.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
    return events


def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the word caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the word caller changes complete separately composed RAM or ordered saved frame words')
    same(result['registers'],value['registers'],'the word caller changes separately composed complete returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the word caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the word caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the word caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the word caller omits its complete real instruction trace')
    same(tuple(row['site'] for row in trace),value['path'],
        'the word caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the word caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the word caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the word caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the word caller leaves its complete feasible closure or ordered continuation')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the word caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the word caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','pr')),
            (expected['registers'],expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the word caller changes complete separately composed post-delay helper CPU/SP/PR arguments')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the word caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the word caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the word caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the word caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        same(tuple(restored['registers'][:15]),expected['return_registers'],
            'the word caller changes complete separately composed real helper returned registers')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the word caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the word caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the word caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the word caller physically accesses a selected unsupported ROM/native-RAM root or alias')
