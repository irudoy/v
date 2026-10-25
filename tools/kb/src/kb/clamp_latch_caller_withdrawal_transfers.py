"""Exact natural clamp latch caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import clamp_latch_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={234266: (234588, 4, 0),
 234270: (234608, 4, 6),
 234282: (234612, 4, 5),
 234288: (234616, 4, 5),
 234292: (234620, 4, 5),
 234304: (234624, 4, 5),
 234312: (234628, 4, 5),
 234320: (234632, 4, 5),
 234332: (234636, 4, 6),
 234338: (234640, 4, 6),
 234344: (234644, 4, 6),
 234358: (234648, 4, 6),
 234360: (234580, 4, 5),
 234364: (234644, 4, 6),
 234390: (234616, 4, 5),
 234400: (234584, 4, 2),
 234418: (234580, 4, 5),
 234422: (234652, 4, 4),
 234450: (234656, 4, 6),
 234458: (234656, 4, 5),
 234468: (234660, 4, 6),
 234472: (234580, 4, 5)}
NATIVE_ROOTS=(('4193a93d663def7a0f8c62b6519e3909b5ae7523997ae08977dd9f3cbdb32951', 87600, None),)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Every instruction and both absolute-helper branch outcomes are feasible in
# the complete natural caller;the whole eight-word ROM owner is protected.
INFEASIBLE_SITES=set()
FEASIBLE_SITES=EXACT_SITES
NATIVE_SPANS=(('4193a93d663def7a0f8c62b6519e3909b5ae7523997ae08977dd9f3cbdb32951',0x15630,16),)
ABSOLUTE_CALL_INPUTS={0x3936C:(-255,255),0x3938A:(-65535,262140)}


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
    same(observed['exit'],wanted,'the clamp latch caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the clamp latch caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the clamp latch caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the clamp latch caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the clamp latch caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the clamp latch caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the clamp latch caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the clamp latch caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the clamp latch caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the clamp latch caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the clamp latch caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the clamp latch caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the clamp latch caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the clamp latch caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the clamp latch caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the clamp latch caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Complete actual entry state remains bound to the instruction trace.
        # Every independent byte helper keeps the complete known scalar SR mask.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the clamp latch caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the clamp latch caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the clamp latch caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the clamp latch caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the clamp latch caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the clamp latch caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the clamp latch caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the clamp latch caller changes independent helper post-delay SP/PR, special registers or known SR')
    for call in result['calls']:
        if call['site'] not in ABSOLUTE_CALL_INPUTS or call['target']!=0x22590:
            raise ValueError('the clamp latch caller substitutes either complete natural absolute helper call')
        incoming=call['entry']['registers'][4]
        incoming=incoming-(1<<32) if incoming&(1<<31) else incoming
        lower,upper=ABSOLUTE_CALL_INPUTS[call['site']]
        if not lower<=incoming<=upper:
            raise ValueError('the clamp latch caller expands a natural post-delay argument to a generic helper-input claim')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the clamp latch caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the clamp latch caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<start+size and start<event['address']+event['width_bytes']
                for identity,start,size in NATIVE_SPANS):
            raise ValueError('the clamp latch caller directly accesses the selected complete sixteen-byte ROM table')
