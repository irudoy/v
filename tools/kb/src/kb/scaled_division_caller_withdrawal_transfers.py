"""Exact natural scaling/division operands, post-delay helper state and returned CPU paths."""
from kb import test_contract
from kb import scaled_division_caller_withdrawal_contract as contract
from kb import scaled_division_caller_withdrawal_semantics as scalar
ROM={320930: (321036, 4, 0),
 320934: (321036, 4, 4),
 320938: (321028, 2, 0),
 320944: (321030, 2, 0),
 320980: (321040, 4, 6),
 321012: (321036, 4, 4),
 321014: (321032, 2, 0),
 476286: (476476, 4, 14),
 476288: (476460, 2, 0),
 476292: (476462, 2, 0),
 476302: (476480, 4, 6),
 476310: (476464, 2, 0),
 476312: (476484, 4, 5),
 476320: (476488, 4, 5),
 476328: (476466, 2, 6),
 476348: (476468, 2, 0),
 476352: (476492, 4, 6),
 476362: (476496, 4, 6),
 476374: (476500, 4, 2),
 476394: (476470, 2, 0),
 476400: (476504, 4, 2),
 476420: (476472, 2, 0),
 476428: (476472, 2, 0),
 476448: (476470, 2, 0),
 477966: (478500, 4, 2),
 477970: (478504, 4, 14),
 477974: (478280, 2, 0),
 477978: (478508, 4, 13),
 477986: (478512, 4, 6),
 477994: (478282, 2, 0),
 478000: (478516, 4, 7),
 478012: (478284, 2, 4),
 478022: (478516, 4, 7),
 478040: (478286, 2, 0)}
NATIVE_ROOTS=(('37a7d0813e696d1ae72ff71cc98a0e9c83c5bb1ebaae0c2d6ef020df01fe2bc7', 74802, None),
 ('8aa69bd24e2f365fc2ba12af43e13ec5ed1436dcb34c5c32179bd485ca529ce0', 87920, None),
 ('0e56068a2df4d1cc74996097fda4018457460adda77683a8ffa87bd7b0587f0b', 102800, None))
CALLER_SITES={site for first,last in scalar.CALLER_SPANS for site in range(first,last,2)}
SHIFT_SITES=set(range(0x224FA,0x22508,2))
HELPER_SITES=set(range(0x21BBC,0x21CD6,2))|SHIFT_SITES
EXACT_SITES=CALLER_SITES|HELPER_SITES
FEASIBLE_CALLER_SITES=CALLER_SITES-{0x4E5D2}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    rows=[];delays={call['site']+2:call for call in value['calls']}
    for site in value['caller_path']:
        if site in value['events']:rows.append(value['events'][site])
        elif site in ROM:
            address,width,register=ROM[site]
            rows.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
        if site in delays:rows.extend(delays[site]['physical'])
    return rows


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the scaled caller changes complete independent instruction CPU/SR state')
    if (observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)
            or observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']):
        raise ValueError('the scaled caller changes complete separately composed RAM or intermediate saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the scaled caller changes separately composed known returned registers')
    if (result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']
            or any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp'))):
        raise ValueError('the scaled caller changes separate known SR, special registers or complete stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the scaled caller changes ordered physical site, mode, address, width, register, domain or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the scaled caller omits its complete real instruction trace')
    same(tuple(row['site'] for row in trace if row['site'] in CALLER_SITES),value['caller_path'],
        'the scaled caller changes a separate natural branch, call delay or return path')
    same([row for row in result['branches'] if row['site'] in CALLER_SITES],value['caller_branches'],
        'the scaled caller changes independent natural controls or feasible branch outcomes')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the scaled caller changes exact executed caller/helper instruction bytes')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the scaled caller changes an actual branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in EXACT_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the scaled caller leaves its exact complete real helper closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the scaled caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the scaled caller omits or invents an actual helper call')
    cursor=0
    for actual,wanted in zip(result['calls'],value['calls']):
        same(tuple(actual[key] for key in ('site','target','return_address','sp')),
            tuple(wanted[key] for key in ('site','target','return_address','sp')),
            'the scaled caller changes an exact helper target, stack or continuation')
        post=actual['entry']
        same(tuple(post[key] for key in ('registers','sp','gbr','mach','macl','pr')),
            (wanted['registers'],wanted['sp'],wanted['gbr'],wanted['mach'],wanted['macl'],wanted['return_address']),
            'the scaled caller changes complete separately composed post-delay helper CPU/SP/PR arguments')
        if post['sr']&wanted['sr_mask']!=wanted['sr']&wanted['sr_mask']:
            raise ValueError('the scaled caller changes known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==wanted['site']),None)
        if first is None or trace[first]['site']!=wanted['target']:
            raise ValueError('the scaled caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[key] for key in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the scaled caller detaches complete helper-entry state from its exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==wanted['return_site']
            and i+1<len(trace) and trace[i+1]['next']==wanted['return_address']),None)
        if terminal is None:raise ValueError('the scaled caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,expected in enumerate(wanted['return_registers']):
            if expected is not None and restored['registers'][index]!=expected:
                raise ValueError('the scaled caller changes a known independent helper returned register')
        if (restored['registers'][15]!=wanted['sp'] or restored['pr']!=wanted['return_address']
                or any(restored[key]!=wanted['return_'+key] for key in ('gbr','mach','macl'))
                or restored['sr']&wanted['return_sr_mask']!=wanted['return_sr']&wanted['return_sr_mask']):
            raise ValueError('the scaled caller changes independent helper post-delay stack, special registers or known SR')
        if wanted['target']==0x224FA:
            same(tuple(row['site'] for row in trace[first:terminal+2]),tuple(range(0x224FA,0x22508,2)),
                'the scaled caller substitutes a value for the real six arithmetic shifts and RTS delay')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the scaled caller changes complete natural post-delay returned CPU/SR state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],None) for row in rows)
    same(identities,NATIVE_ROOTS,'the scaled caller substitutes an exact original selected ROM reader identity')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes'] for original,address,alias in NATIVE_ROOTS):
            raise ValueError('the scaled caller physically accesses a selected unsupported ROM reader root')
