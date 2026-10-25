"""Exact ordered physical operands, complete natural calls and caller/helper returned state."""
from kb import test_contract
from kb import byte_curve_caller_withdrawal_semantics as scalar
RAM_BASE=0x01000000
ROM={181664: (182268, 4, 0),
 181668: (182236, 4, 5),
 181670: (182272, 4, 4),
 181674: (182276, 4, 2),
 451548: (452044, 4, 6),
 451556: (452048, 4, 5),
 451558: (452052, 4, 4),
 451562: (452056, 4, 2),
 451572: (452036, 4, 7),
 451574: (451804, 2, 0),
 451586: (452048, 4, 5),
 451588: (452052, 4, 4),
 451592: (452056, 4, 2),
 451600: (452036, 4, 7),
 451602: (451808, 2, 0),
 451606: (451804, 2, 0),
 451614: (452060, 4, 6),
 451638: (452036, 4, 7),
 451640: (451810, 2, 0),
 156528: (156546, 2, 0),
 156536: (156548, 4, 6),
 158388: (158396, 4, 6)}
NATIVE_ROOTS=(('8f902a61c4561dec84c2f7f0ae40da8d82fa4d7ef581ebfbead5a5d52ac27bc2', 4294906624, 16782080),
 ('37bc9896cbf83383f331006e7744b1bee34ca2856dbfafcbacd9177547752ddd', 4294909830, 16785286),
 ('09b5eff09ef2b5074732b1901c9a9146175e4c4aebb78fda440c06709ce571e4', 4294911057, 16786513),
 ('a883d3c1766a31c36b0d4af9f9341d0b92f6df477e56465a49115809e41707e5', 4294918533, 16793989),
 ('7bd9b7a26ba2a26d497c97c09db151002bf8bfd8b01bb5d88d1094277dc5cfc7', 4294935744, 16811200))
READ={181672: (4215, 1, 0),
 451550: (9295, 1, 0),
 451560: (4207, 1, 0),
 451576: (5809, 1, 2),
 451590: (4207, 1, 0),
 451604: (5806, 1, 2),
 451612: (5809, 1, 5)}
WRITE={181680: (7972, 1, 0), 181686: (7764, 2, 0), 451648: (5990, 1, 2)}
EXACT_SPANS=((156528, 156546), (157504, 157550), (158336, 158364), (158378, 158394), (181660, 181696), (451544, 451650))
EXACT_SITES={site for first,last in EXACT_SPANS for site in range(first,last,2)}
HELPER_SPANS=((138172, 138454),)


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    events=[]
    for point in result['trace']:
        site=point['site']
        if site in value['frame_accesses']:
            mode,depth,register,raw=value['frame_accesses'][site]
            address,width,domain=observed['sp']-depth,4,'frame'
        elif site in (0x26380,0x26AAC,0x26AAE):
            if len(value['curves'])!=1:raise ValueError('the byte-curve physical source has no exact selected lookup')
            curve=value['curves'][0];index=7 if site==0x26380 else curve['index']+(site==0x26AAE)
            address,width,register=curve['base']+index,1,1 if site==0x26AAC else 0
            mode,domain='read','rom';raw=fixture[address:address+1]
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write';at,width,register=(READ if mode=='read' else WRITE)[site]
            address,domain=RAM_BASE+at,'ram'
            raw=observed['memory_before'][0][at:at+width] if mode=='read' else value['physical_writes'][site]
        else:continue
        events.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return events


def exact_path(entry,continuation,value):
    result=[];pc=entry
    while pc!=continuation:
        if pc not in EXACT_SITES or len(result)>256:
            raise ValueError('the constant-root byte-curve equations leave the finite natural caller/interior closure')
        result.append(pc);control=value['controls'].get(pc)
        if control is None:pc+=2;continue
        if control['delay']:result.append(pc+2)
        pc=pc+4 if control['kind']=='call' and control['target']==0x21BBC else control['target']
    return tuple(result)


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the byte-curve caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the byte-curve caller changes complete independent quotient/clamp RAM or exact saved frame words')
    for index,wanted in value['known_registers'].items():
        if result['registers'][index]!=wanted:raise ValueError('the byte-curve caller changes a separate complete known returned register')
    if (bool(result['sr']&1)!=value['t'] or result['sr']&~0x301!=observed['sr_before']&~0x301
            or (result['sr']&0x200 if value['division_active'] else (result['sr']^observed['sr_before'])&0x300)):
        raise ValueError('the byte-curve caller changes separate final T, interrupt state or admitted helper M/Q preservation')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the byte-curve caller changes independent complete special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the byte-curve caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the byte-curve caller omits its complete instruction trace')
    same(tuple(r['site'] for r in trace if r['site'] in EXACT_SITES),exact_path(observed['entry'],observed['continuation'],value),
        'the byte-curve caller changes a separate natural branch, call delay or return path')
    same([r for r in result['branches'] if r['site'] in EXACT_SITES],list(value['controls'].values()),
        'the byte-curve caller changes an independent conditional, post-delay call, jump or natural return')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
        'the byte-curve caller changes an exact executed caller/helper instruction byte')
    delayed={r['site']+2 for r in result['branches'] if r['delay']}
    if {r['site'] for r in trace if r['delay_slot']}!=delayed:
        raise ValueError('the byte-curve caller changes an actual caller/helper branch or return delay slot')
    for index,row in enumerate(trace):
        wanted=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['next']!=wanted or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the byte-curve caller changes ordered complete helper control or terminal continuation')
        if row['site'] not in EXACT_SITES and not any(a<=row['site']<b for a,b in HELPER_SPANS):
            raise ValueError('the byte-curve caller leaves its exact real helper byte closure')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the byte-curve caller omits or invents a real helper call')
    for call,wanted in zip(result['calls'],value['calls']):
        same(tuple(call[k] for k in ('site','target','return_address','sp')),
            tuple(wanted[k] for k in ('site','target','return_address','sp')),'the byte-curve caller changes its exact natural helper')
        post=call['entry']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (wanted['registers'],wanted['sp'],wanted['gbr'],wanted['mach'],wanted['macl'],wanted['sr'],wanted['return_address']),
            'the byte-curve caller changes complete independently reconstructed post-delay helper CPU/SP/PR/MACL arguments')
        first=next(i for i,row in enumerate(trace) if row['site']==wanted['site'])+2
        if trace[first]['site']!=wanted['target']:raise ValueError('the byte-curve caller replaces its real helper entry')
        return_site=wanted['return_site']
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==return_site),None)
        if terminal is None or terminal+2>=len(trace):raise ValueError('the byte-curve caller omits a real natural helper return')
        restored=trace[terminal+1]['after']
        if (trace[terminal+1]['next']!=wanted['return_address'] or restored['registers'][15]!=wanted['sp']
                or restored['pr']!=wanted['return_address']):
            raise ValueError('the byte-curve caller changes helper post-delay SP/PR or continuation')
        for register,expected in enumerate(wanted['return_registers']):
            if expected is not None and restored['registers'][register]!=expected:
                raise ValueError('the real byte-curve/division helper changes a separate returned or preserved register')
        if (any(restored[k]!=wanted[k] for k in ('gbr','mach','macl'))
                or restored['sr']&wanted['return_sr_mask']!=wanted['return_sr']&wanted['return_sr_mask']):
            raise ValueError('the real byte-curve/division helper changes independent special-register or known SR state')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=result['registers']
            or any(trace[-1]['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the byte-curve caller changes its complete post-delay returned registers or SP')


def require_no_selected_datum(result,rows):
    identities=tuple((r['original_claim_sha256'],r['address'],
        RAM_BASE+(r['address']&65535) if r['owner'].endswith('/ram') else None) for r in rows)
    same(identities,NATIVE_ROOTS,'the byte-curve caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the byte-curve caller physically accesses a selected unsupported ROM/native-RAM root or alias')
