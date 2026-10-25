"""Exact natural byte ratio producer/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import byte_ratio_producer_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 138602: (138696, 4, 1),
 138604: (138700, 4, 2),
 306800: (307140, 4, 7),
 306802: (306880, 2, 0),
 306806: (306878, 2, 0),
 306822: (307144, 4, 6),
 306824: (306882, 2, 0),
 306850: (307116, 4, 5),
 306888: (307148, 4, 2),
 306910: (307092, 4, 6),
 306934: (307116, 4, 6),
 306946: (307152, 4, 6),
 306962: (307128, 4, 6),
 306988: (307156, 4, 2)}
NATIVE_ROOTS=(('91c32f65b77d4ec19c96531ca7402eb1fa6b3c1b05a94eb3f41128ffe2bac40d', 73734, None),)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# The first unsigned divisor is a nonzero raw byte-word product;the second is5.
# Both unsigned word/large and short/long paths remain reachable. The signed
# fallback supplies divisor5. Only the exact zero/negative/large tails below
# are excluded;their full bytes and the complete direct-helper original remain bound.
INFEASIBLE_SITES=set(range(0x21BCC,0x21BD0,2))|set(range(0x21C70,0x21CD6,2))|set(range(0x21D6A,0x21D76,2))
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def saved_post_DIV1_R1_bytes(observed,result,value):
    opaque=[event for event in value['events'].values() if event['bytes'] is None]
    sites=tuple(event['site'] for event in opaque)
    same(sites,value['opaque_frame_sites'],'the byte-ratio caller changes its exact opaque frame-carrier extent')
    if not sites:return {}
    same(sites,(0x22508,0x22518),'the byte-ratio caller broadens its two exact saved post-DIV1 R1 operands')
    if observed['entry']!=0x4AE6C:raise ValueError('the saved R1 carrier changes its complete natural caller')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the saved R1 carrier omits its complete actual instruction trace')
    positions={site:[index for index,row in enumerate(trace) if row['site']==site] for site in sites}
    if any(len(indexes)!=1 for indexes in positions.values()):
        raise ValueError('the saved R1 carrier duplicates or omits an actual instruction')
    first,last=(positions[site][0] for site in sites)
    write,read=trace[first],trace[last];saved=write['before']['registers'][1]
    if type(saved) is not int or not 0<=saved<=0xFFFFFFFF or not first<last:
        raise ValueError('the saved R1 carrier changes its complete actual raw word or order')
    address=observed['sp']-12
    for event in opaque:
        same(tuple(event[key] for key in ('mode','address','width_bytes','register','domain')),
            ('write' if event['site']==0x22508 else 'read',address,4,1,'frame'),
            'the saved R1 carrier changes an exact stack site,address,width,register or direction')
    same((write['before']['registers'][15],write['after']['registers'][15],
        read['before']['registers'][15],read['after']['registers'][15],read['after']['registers'][1]),
        (address+4,address,address,address+4,saved),
        'the saved R1 word detaches from its real predecrement store or postincrement restoration')
    overwrite=next((event for index,event in value['events'].items() if index>last and event['mode']=='write'
        and event['domain']=='frame' and event['address']==address),None)
    if overwrite is None or overwrite['site']!=0x21BBC or overwrite['width_bytes']!=4 or overwrite['bytes'] is None:
        raise ValueError('the saved R1 word omits the complete independently known signed-helper overwrite')
    raw=saved.to_bytes(4,'big').hex()
    return {0x22508:raw,0x22518:raw}


def physical(observed,result,value,fixture):
    events=[];opaque=saved_post_DIV1_R1_bytes(observed,result,value)
    for index,site in enumerate(value['path']):
        if index in value['events']:
            event=value['events'][index]
            events.append(dict(event,bytes=opaque[site]) if event['bytes'] is None else event);continue
        if site in ROM:
            address,width,register=ROM[site]
            events.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
    return events


def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the byte ratio producer changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the byte ratio producer changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the byte ratio producer changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the byte ratio producer changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the byte ratio producer changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the byte ratio producer changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the byte ratio producer omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the byte ratio producer detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the byte ratio producer changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the byte ratio producer changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the byte ratio producer changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the byte ratio producer changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the byte ratio producer leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the byte ratio producer detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the byte ratio producer omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the byte ratio producer changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the byte ratio producer changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the byte ratio producer changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the byte ratio producer changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the byte ratio producer replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the byte ratio producer detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the byte ratio producer omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the byte ratio producer changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the byte ratio producer changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the byte ratio producer changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the byte ratio producer substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the byte ratio producer physically accesses a selected unsupported ROM/native-RAM root or alias')
