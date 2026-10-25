"""Exact natural misfire tail dispatch/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import misfire_tail_dispatch_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={509082: (509088, 4, 2),
 509152: (509228, 4, 1),
 509154: (509232, 4, 4),
 509158: (509236, 4, 2),
 509174: (509240, 4, 7),
 553682: (553888, 4, 1),
 553686: (553892, 4, 6),
 553694: (553896, 4, 5),
 553716: (553900, 4, 6),
 553724: (553900, 4, 5),
 553732: (553886, 2, 6),
 553740: (553900, 4, 6),
 553748: (553900, 4, 5),
 553754: (553904, 4, 5),
 553772: (553900, 4, 6),
 553782: (553900, 4, 5),
 553788: (553900, 4, 6),
 553798: (553908, 4, 6),
 553812: (553912, 4, 6),
 553826: (553916, 4, 6),
 553854: (553916, 4, 6)}
NATIVE_ROOTS=(('02d868473e3c258ee4fe81777aea05a65bd44e0a57d0e64ef658d8f3949df311', 4294935738, 16811194),)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Every instruction belongs to the complete root and two complete real leaves.
# The exact selected native root and its ordinary alias are protected without
# assigning a native width, signedness, scheduling or hardware identity.
INFEASIBLE_SITES=set()
FEASIBLE_SITES=EXACT_SITES
NATIVE_SPANS=(('02d868473e3c258ee4fe81777aea05a65bd44e0a57d0e64ef658d8f3949df311',0xFFFF84BA,1),('02d868473e3c258ee4fe81777aea05a65bd44e0a57d0e64ef658d8f3949df311',0x010084BA,1))


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
    same(observed['exit'],wanted,'the misfire tail dispatch changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the misfire tail dispatch changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the misfire tail dispatch changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the misfire tail dispatch changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the misfire tail dispatch changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the misfire tail dispatch changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the misfire tail dispatch omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the misfire tail dispatch detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the misfire tail dispatch changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the misfire tail dispatch changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the misfire tail dispatch changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the misfire tail dispatch changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the misfire tail dispatch leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the misfire tail dispatch detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the misfire tail dispatch omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the misfire tail dispatch changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Complete actual entry state remains bound to the instruction trace.
        # Every independent byte helper keeps the complete known scalar SR mask.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the misfire tail dispatch changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the misfire tail dispatch changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the misfire tail dispatch changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the misfire tail dispatch replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the misfire tail dispatch detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the misfire tail dispatch omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the misfire tail dispatch changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the misfire tail dispatch changes independent helper post-delay SP/PR, special registers or known SR')
    if len(result['calls'])!=1:
        raise ValueError('the misfire tail dispatch changes its single real BSR and two complete leaf bodies')
    call=result['calls'][0]
    same(tuple(call[key] for key in ('site','target','return_address','sp')),
        (0x7C496,0x7C4E0,0x7C49A,observed['sp']-4),
        'the misfire tail dispatch detaches the exact real BSR target, continuation or saved-PR position')
    same(tuple(call['entry'][key] for key in ('registers','sp','gbr','mach','macl','sr','pr')),
        (tuple(observed['context'][:15]),observed['sp']-4,*observed['context'][15:18],observed['sr_before'],0x7C49A),
        'the misfire tail dispatch detaches complete post-NOP callee arguments and state from actual root input')
    tail=next((index for index,row in enumerate(trace) if row['site']==0x7C49C),None)
    if (tail is None or trace[tail+1]['site']!=0x7C49E or not trace[tail+1]['delay_slot']
            or trace[tail+2]['site']!=0x872D0
            or trace[tail+2]['before']['registers'][15]!=observed['sp']
            or trace[tail+2]['before']['pr']!=observed['continuation']):
        raise ValueError('the misfire tail omits the actual post-delay restored root PR/SP entry')
    saved=[row for row in result['accesses'] if row['site'] in (0x7C494,0x7C49E,0x872D0,0x8739C)]
    same([(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in saved],
        [(0x7C494,'write',observed['sp']-4,4,observed['continuation'].to_bytes(4,'big').hex()),
         (0x7C49E,'read',observed['sp']-4,4,observed['continuation'].to_bytes(4,'big').hex()),
         (0x872D0,'write',observed['sp']-4,4,observed['context'][17].to_bytes(4,'big').hex()),
         (0x8739C,'read',observed['sp']-4,4,observed['context'][17].to_bytes(4,'big').hex())],
        'the misfire tail changes the ordered shared PR/MACL save-slot identity or contents')
    local=[row for row in result['accesses'] if row['site'] in (0x87370,0x87378)]
    same([(row['site'],row['address'],row['width_bytes'],row['register'],row['bytes']) for row in local],
        [(site,address,4,0,raw.to_bytes(4,'big').hex()) for site,address,raw in value['local_counter_preimages']],
        'the misfire tail changes either distinct signed pre-increment local word')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the misfire tail dispatch changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the misfire tail dispatch substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<start+size and start<event['address']+event['width_bytes']
                for identity,start,size in NATIVE_SPANS):
            raise ValueError('the misfire tail dispatch directly accesses the exact selected native RAM root or its ordinary alias')
