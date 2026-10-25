"""Exact ordered physical operands, complete natural calls and caller/helper returned state."""
from kb import test_contract
from kb import division_caller_withdrawal_semantics as scalar
RAM_BASE=0x01000000
ROM={238166: (238732, 4, 6),
 238168: (33609, 1, 0),
 238174: (238736, 4, 2),
 238194: (238740, 4, 5),
 238200: (238744, 4, 2),
 451654: (452064, 4, 2),
 451672: (452036, 4, 5),
 451674: (451810, 2, 0),
 451688: (451812, 2, 2),
 451692: (452068, 4, 5),
 451716: (452072, 4, 5),
 451718: (451814, 2, 0),
 752776: (753176, 4, 2),
 752782: (753180, 4, 2),
 752790: (753184, 4, 6),
 752794: (34115, 1, 0),
 752796: (34114, 1, 2),
 752804: (752882, 2, 4),
 752822: (752884, 2, 2),
 752828: (753188, 4, 5),
 752850: (753192, 4, 2),
 752852: (753196, 4, 6),
 752858: (753200, 4, 6),
 752868: (753204, 4, 6),
 752870: (752886, 2, 0)}
NATIVE_ROOTS=(('06a28bfdc75877765648fadf97583dd485390c0ea215d8bddac0f7caedb15a12', 76140, None),
 ('31c06ca11be68e06446e63008e1b925f9c6c91e2aad426c9ac5410d6cd249170', 4294906206, 16781662),
 ('c61ae22c08f4705d9dac2d3a011403f1d55fbaffdb4530e223f9d3d239053841', 4294915068, 16790524))
READ={0x6E44A:(0x11B3,1,6),0x6E462:(0x1766,1,2)}
WRITE={0x3A27A:(0x1020,1,0),0x3A27E:(0x118E,1,6),0x6E48E:(0x1F86,1,2),0xB7CE8:(0x3400,4,2)}
CALLER_SITES={site for first,last in scalar.CALLER_SPANS for site in range(first,last,2)}
HELPER_SPANS=((0x21BBC,0x21CD6),(0x21CE0,0x21DC6))


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    events=[]
    for point in result['trace']:
        site=point['site']
        if site in value['frame_accesses']:
            mode,depth,register,raw=value['frame_accesses'][site]
            address,width,domain=observed['sp']-depth,4,'frame'
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write';at,width,register=(READ if mode=='read' else WRITE)[site]
            address,domain=RAM_BASE+at,'ram'
            raw=observed['memory_before'][0][at:at+width] if mode=='read' else value['physical_writes'][site]
        else:continue
        events.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return events


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the division caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the division caller changes complete independent quotient/clamp RAM or exact saved frame words')
    for index,wanted in value['known_registers'].items():
        if result['registers'][index]!=wanted:raise ValueError('the division caller changes a separate complete known returned register')
    if (bool(result['sr']&1)!=value['t'] or result['sr']&~0x301!=observed['sr_before']&~0x301
            or (result['sr']&0x200 if value['helper_active'] else (result['sr']^observed['sr_before'])&0x300)):
        raise ValueError('the division caller changes separate final T, interrupt state or admitted helper M/Q preservation')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the division caller changes independent complete special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the division caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the division caller omits its complete instruction trace')
    same(tuple(r['site'] for r in trace if r['site'] in CALLER_SITES),value['caller_path'],
        'the division caller changes a separate natural branch, call delay or return path')
    same([r for r in result['branches'] if r['site'] in CALLER_SITES],value['caller_branches'],
        'the division caller changes an independent conditional, post-delay call, jump or natural return')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the division caller changes an exact executed caller/helper instruction byte')
    delayed={r['site']+2 for r in result['branches'] if r['delay']}
    if {r['site'] for r in trace if r['delay_slot']}!=delayed:
        raise ValueError('the division caller changes an actual caller/helper branch or return delay slot')
    for index,row in enumerate(trace):
        wanted=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['next']!=wanted or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the division caller changes ordered complete helper control or terminal continuation')
        if row['site'] not in CALLER_SITES and not any(a<=row['site']<b for a,b in HELPER_SPANS):
            raise ValueError('the division caller leaves its exact real helper byte closure')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the division caller omits or invents a real helper call')
    for call,wanted in zip(result['calls'],value['calls']):
        same(tuple(call[k] for k in ('site','target','return_address','sp')),
            tuple(wanted[k] for k in ('site','target','return_address','sp')),'the division caller changes its exact natural helper')
        post=call['entry']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (wanted['registers'],wanted['sp'],wanted['gbr'],wanted['mach'],wanted['macl'],wanted['sr'],wanted['return_address']),
            'the division caller changes complete independently reconstructed post-delay helper CPU/SP/PR/MACL arguments')
        first=next(i for i,row in enumerate(trace) if row['site']==wanted['site'])+2
        if trace[first]['site']!=wanted['target']:raise ValueError('the division caller replaces its real helper entry')
        return_site=(0x21C6C if wanted['long_path'] else 0x21C04) if wanted['target']==0x21BBC else (0x21D66 if wanted['long_path'] else 0x21D08)
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==return_site),None)
        if terminal is None or terminal+2>=len(trace):raise ValueError('the division caller omits its actual natural helper return')
        restored=trace[terminal+1]['after']
        if (trace[terminal+1]['next']!=wanted['return_address'] or restored['registers'][15]!=wanted['sp']
                or restored['pr']!=wanted['return_address']):
            raise ValueError('the division caller changes the helper post-delay SP or natural continuation')
        for register in range(2,15):
            if restored['registers'][register]!=wanted['registers'][register]:raise ValueError('the real helper changes a preserved incoming register')
        if any(restored[k]!=wanted[k] for k in ('gbr','mach','macl')):
            raise ValueError('the real helper changes complete incoming special-register state')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=result['registers']
            or any(trace[-1]['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the division caller changes its complete post-delay returned registers or SP')


def require_no_selected_datum(result,rows):
    identities=tuple((r['original_claim_sha256'],r['address'],
        RAM_BASE+(r['address']&65535) if r['owner'].endswith('/ram') else None) for r in rows)
    same(identities,NATIVE_ROOTS,'the division caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the division caller physically accesses a selected unsupported ROM/native-RAM root or alias')
