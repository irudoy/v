"""Exact natural curve-scale caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import curve_scale_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 156972: (157004, 4, 7),
 156992: (157000, 4, 6),
 158118: (158144, 4, 2),
 751476: (751968, 4, 4),
 751480: (751972, 4, 5),
 751484: (751976, 4, 2),
 751492: (751980, 4, 5),
 751494: (751680, 2, 0),
 751514: (751682, 2, 2),
 751520: (751684, 2, 2),
 751526: (751984, 4, 2),
 751538: (751686, 2, 6),
 751552: (751988, 4, 4),
 751562: (751688, 2, 0),
 751576: (751992, 4, 2)}
NATIVE_ROOTS=(('c929ffe309a99404d540ecfdfbfad0a6be2232a343f56f29adfddec308af95a1', 89152, None),
 ('2fa5679cd811139cb212d0665cbe7a53415535a72d65c79d58e21e6f4d5f0542', 4294911795, 16787251),
 ('e353009592e533d5f7413aa3a4edaac73a80982db8c14fd47b6db9376eeccc0b', 4294914888, 16790344))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
INFEASIBLE_SITES={0x26D0A,0x26D0C,0x21BCC,0x21BCE}|set(range(0x21C70,0x21CD6,2))
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
    same(observed['exit'],wanted,'the curve-scale caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the curve-scale caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the curve-scale caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the curve-scale caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the curve-scale caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the curve-scale caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the curve-scale caller omits its complete real instruction trace')
    same(tuple(row['site'] for row in trace),value['path'],
        'the curve-scale caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the curve-scale caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the curve-scale caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the curve-scale caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the curve-scale caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the curve-scale caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the curve-scale caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the curve-scale caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','pr')),
            (expected['registers'],expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the curve-scale caller changes complete separately composed post-delay helper CPU/SP/PR arguments')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the curve-scale caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the curve-scale caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the curve-scale caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the curve-scale caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the curve-scale caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the curve-scale caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the curve-scale caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the curve-scale caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the curve-scale caller physically accesses a selected unsupported ROM/native-RAM root or alias')
