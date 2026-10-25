"""Exact natural paired curve normalization caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import paired_curve_normalization_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 156840: (156872, 4, 7),
 156860: (156868, 4, 6),
 158054: (158080, 4, 2),
 415166: (415788, 4, 0),
 415172: (415792, 4, 6),
 415182: (415796, 4, 7),
 415186: (415788, 4, 12),
 415196: (415490, 2, 0),
 415228: (415800, 4, 4),
 415230: (415804, 4, 5),
 415232: (415808, 4, 2),
 415244: (415812, 4, 7),
 415248: (415490, 2, 0),
 415284: (415800, 4, 4),
 415286: (415804, 4, 5),
 415288: (415808, 4, 2),
 415302: (415492, 2, 0),
 415318: (415816, 4, 5),
 415328: (415812, 4, 7),
 415340: (415788, 4, 12),
 415342: (415494, 2, 0),
 415348: (415796, 4, 7),
 415352: (415820, 4, 2),
 415410: (415800, 4, 4),
 415412: (415804, 4, 5),
 415414: (415808, 4, 2),
 415416: (415788, 4, 12),
 415424: (415492, 2, 0),
 415454: (415496, 2, 6),
 415472: (415498, 2, 0),
 416530: (417140, 4, 0),
 416536: (417144, 4, 6),
 416546: (417148, 4, 2),
 416550: (417140, 4, 12),
 416560: (416886, 2, 0),
 416596: (417152, 4, 4),
 416600: (417156, 4, 5),
 416602: (417160, 4, 2),
 416612: (417164, 4, 7),
 416616: (416886, 2, 0),
 416650: (417152, 4, 4),
 416652: (417156, 4, 5),
 416654: (417160, 4, 2),
 416668: (416888, 2, 0),
 416684: (417168, 4, 5),
 416694: (417164, 4, 7),
 416696: (417148, 4, 2),
 416726: (417152, 4, 4),
 416728: (417156, 4, 5),
 416730: (417160, 4, 2),
 416732: (417140, 4, 12),
 416740: (416888, 2, 0),
 416770: (416890, 2, 6),
 416788: (416892, 2, 0)}
NATIVE_ROOTS=(('0857c64cec33d674a469dc8d6cb8fc6360314e56e1e4f09cbbc44d5c60c2775e', 68494, None),
 ('11bcb9488d622e9f157f3d5b3a553cea1bc9f439607efa759dc9d6d0c249433e', 68494, None))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Signed division receives positive1..256 and admits both numerator signs.
# Fractional division receives the positive adjacent byte-axis bracket.
# Three caller upper-cap instructions are unreachable from their complete raw
# signed-byte difference or EXTU.B premises. Every full broader prior helper
# original remains mandatory from the identical primary.
INFEASIBLE_SITES=({0x655FA,0x65B50,0x65BD4}|set(range(0x21BCC,0x21BD0,2))
    |set(range(0x21C70,0x21CD6,2))|set(range(0x26D0A,0x26D0E,2)))
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
    same(observed['exit'],wanted,'the paired curve normalization caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the paired curve normalization caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the paired curve normalization caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the paired curve normalization caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the paired curve normalization caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the paired curve normalization caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the paired curve normalization caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the paired curve normalization caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the paired curve normalization caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the paired curve normalization caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the paired curve normalization caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the paired curve normalization caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the paired curve normalization caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the paired curve normalization caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the paired curve normalization caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the paired curve normalization caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the paired curve normalization caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the paired curve normalization caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the paired curve normalization caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the paired curve normalization caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the paired curve normalization caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the paired curve normalization caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the paired curve normalization caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the paired curve normalization caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the paired curve normalization caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the paired curve normalization caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the paired curve normalization caller physically accesses a selected unsupported ROM/native-RAM root or alias')
