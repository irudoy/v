"""Exact natural timing remainder caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import timing_remainder_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 138602: (138696, 4, 1),
 138604: (138700, 4, 2),
 138960: (139064, 4, 1),
 138962: (139068, 4, 2),
 156884: (156916, 4, 7),
 156904: (156912, 4, 6),
 158118: (158144, 4, 2),
 317864: (318368, 4, 0),
 317868: (318372, 4, 2),
 317870: (318376, 4, 7),
 317890: (318380, 4, 14),
 317916: (318380, 4, 14),
 317920: (318384, 4, 4),
 317942: (318388, 4, 6),
 317944: (318384, 4, 4),
 317948: (318380, 4, 14),
 317994: (318392, 4, 12),
 318020: (318396, 4, 13),
 318024: (318368, 4, 4),
 318028: (318116, 2, 0),
 318030: (318400, 4, 6),
 318052: (318368, 4, 4),
 318056: (318116, 2, 0),
 318076: (318396, 4, 13),
 318080: (318404, 4, 4),
 318084: (318408, 4, 5),
 318086: (318412, 4, 2),
 318092: (318416, 4, 5),
 318104: (318420, 4, 5),
 318106: (318368, 4, 4),
 318110: (318118, 2, 0),
 318120: (318424, 4, 2),
 318122: (318368, 4, 4),
 318126: (318364, 2, 0),
 318138: (318428, 4, 6),
 318158: (318376, 4, 7),
 318172: (318400, 4, 5),
 318180: (318368, 4, 4),
 318182: (318366, 2, 0),
 318196: (318400, 4, 3),
 318212: (318400, 4, 3),
 318228: (318432, 4, 2),
 318324: (318396, 4, 13),
 318344: (318436, 4, 2),
 336304: (336536, 4, 0),
 336310: (336540, 4, 6),
 336318: (336544, 4, 2),
 336326: (336548, 4, 2),
 336334: (336552, 4, 2),
 336396: (336556, 4, 2),
 336400: (336534, 2, 0),
 336424: (336560, 4, 6),
 336434: (336564, 4, 6),
 336450: (336568, 4, 2),
 336458: (336572, 4, 2),
 336496: (336576, 4, 5)}
NATIVE_ROOTS=(('89a38d2dcd45777abd73579e85cf7b5dd431bc74e4a2260328a310210098f5f4', 39450, None),
 ('93e3a24dbabf0b837d2a841e770691a49219fdae0acb23fbf86292abc5b70294', 39706, None),
 ('f46a6cd59f095a901dc94bc0a98d36dec248275c481b136cdd5453add9d11092', 74498, None),
 ('734ac219e0c8a85fb79e275db3666708bc66a9e4aa9be699f218fb89bf962744', 74506, None),
 ('5e73c6e179defd8189e4bff04c27bc774d2b2b9a04068df7648d5096e352eac8', 4294906394, 16781850))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# These exclusions follow only the two complete callers and actual fixed
# positive divisors. Every full preceding helper original remains required.
INFEASIBLE_SITES=({0x21BCC,0x21BCE,0x21BFE,0x21C00,0x21C64,0x21C66,
    0x21E26,0x21E28,0x21E5E,0x21E60,0x21EC4,0x21EC6,
    0x26D0A,0x26D0C,0x4DB82,0x5226C}
    |set(range(0x21C70,0x21CD6,2))|set(range(0x21D6A,0x21DC6,2))
    |set(range(0x21ED0,0x21F38,2)))
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
    same(observed['exit'],wanted,'the timing remainder caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the timing remainder caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the timing remainder caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the timing remainder caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the timing remainder caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the timing remainder caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the timing remainder caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the timing remainder caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the timing remainder caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the timing remainder caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the timing remainder caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the timing remainder caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the timing remainder caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the timing remainder caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the timing remainder caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the timing remainder caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the timing remainder caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the timing remainder caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the timing remainder caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the timing remainder caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the timing remainder caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the timing remainder caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the timing remainder caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the timing remainder caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the timing remainder caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the timing remainder caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the timing remainder caller physically accesses a selected unsupported ROM/native-RAM root or alias')
