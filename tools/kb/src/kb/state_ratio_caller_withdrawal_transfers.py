"""Exact natural state ratio caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import state_ratio_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 138602: (138696, 4, 1),
 138604: (138700, 4, 2),
 156528: (156546, 2, 0),
 156536: (156548, 4, 6),
 158388: (158396, 4, 6),
 412858: (413136, 4, 0),
 412864: (413148, 4, 6),
 412872: (413152, 4, 5),
 412888: (413156, 4, 6),
 412896: (413160, 4, 4),
 412898: (413164, 4, 6),
 412938: (413164, 4, 6),
 412962: (413168, 4, 2),
 412976: (413172, 4, 6),
 412996: (413124, 2, 2),
 413006: (413144, 4, 6),
 413034: (413136, 4, 14),
 413052: (413136, 4, 14),
 413054: (413126, 2, 0),
 413068: (413176, 4, 5),
 413084: (413132, 4, 2),
 413096: (413180, 4, 4),
 413110: (413136, 4, 14),
 413114: (413126, 2, 0),
 413118: (413128, 2, 0),
 413184: (413680, 4, 6),
 413192: (413684, 4, 6),
 413200: (413688, 4, 6),
 413214: (413688, 4, 6),
 413228: (413692, 4, 3),
 413236: (413696, 4, 7),
 413244: (413700, 4, 6),
 413246: (413396, 2, 0),
 413256: (413704, 4, 14),
 413258: (413398, 2, 0),
 413266: (413400, 2, 0),
 413272: (413684, 4, 6),
 413280: (413700, 4, 6),
 413282: (413396, 2, 0),
 413284: (413692, 4, 3),
 413300: (413696, 4, 7),
 413308: (413704, 4, 14),
 413314: (413704, 4, 14),
 413316: (413400, 2, 0),
 413348: (413400, 2, 0),
 413350: (413708, 4, 3),
 413366: (413688, 4, 6),
 413378: (413402, 2, 0),
 413382: (413404, 2, 0),
 413386: (413406, 2, 0),
 413390: (413408, 2, 0),
 413410: (413712, 4, 7),
 413434: (413716, 4, 6),
 413442: (413692, 4, 3),
 413450: (413708, 4, 3),
 413460: (413704, 4, 14),
 413462: (413666, 2, 0),
 413472: (413668, 2, 0),
 413482: (413670, 2, 0),
 413486: (413672, 2, 0),
 413502: (413670, 2, 0),
 413506: (413670, 2, 0),
 413512: (413674, 2, 0),
 413516: (413676, 2, 0),
 413520: (413720, 4, 2),
 413542: (413668, 2, 0),
 413550: (413676, 2, 0),
 413566: (413724, 4, 6),
 413590: (413704, 4, 14),
 413592: (413666, 2, 0),
 413614: (413666, 2, 0),
 413628: (413704, 4, 14),
 413632: (413666, 2, 0),
 413648: (413704, 4, 14),
 413650: (413666, 2, 0),
 777328: (777564, 4, 6),
 777336: (777568, 4, 6),
 777348: (777572, 4, 6),
 777362: (777576, 4, 2),
 777404: (777560, 4, 5),
 777412: (777580, 4, 2),
 777420: (777584, 4, 6),
 777426: (777588, 4, 6),
 777428: (777466, 2, 0),
 777434: (777592, 4, 6),
 777442: (777592, 4, 6),
 777452: (777596, 4, 6),
 777600: (778144, 4, 14),
 777614: (778148, 4, 2),
 777632: (778152, 4, 13),
 777634: (777944, 2, 0),
 777638: (777946, 2, 0),
 777670: (778156, 4, 5),
 777700: (778148, 4, 6),
 777710: (778152, 4, 13),
 777712: (777944, 2, 0),
 777718: (778152, 4, 13),
 777720: (777946, 2, 0),
 777728: (777948, 2, 0),
 777730: (778160, 4, 5),
 777742: (778164, 4, 5),
 777748: (777950, 2, 0),
 777758: (778160, 4, 6),
 777768: (777952, 2, 0),
 777776: (778168, 4, 7),
 777794: (778172, 4, 2),
 777802: (778176, 4, 2),
 777814: (778156, 4, 6),
 777840: (778180, 4, 4),
 777842: (778184, 4, 6),
 777848: (778148, 4, 3),
 777850: (778188, 4, 4),
 777854: (778184, 4, 6),
 777864: (777952, 2, 0),
 777866: (778168, 4, 7),
 777884: (778192, 4, 5),
 777894: (777954, 2, 0),
 777928: (778164, 4, 5)}
NATIVE_ROOTS=(('732688d3434fc5a9a865a6cebd20539bcfc8910a4081e9b969e2acd61d7bd78d', 43866, None),
 ('f73ed3184f14337902a9cf59ecad78ad4758f406cf517eb3051d29b6c51ad816', 46138, None),
 ('2e5256f30e8ea2c75bbf968f4a83d03fde44859214cb1f1891cf7a8148674f31', 46394, None),
 ('0eb7a55d3774f6a93694313064815dcfa169939e114231fe1b262f249e4e7e81', 46586, None),
 ('b302d7d9f9f92e555d671576982f93b50d101da12e7bd9d8c3756a1939d516ae', 73702, None),
 ('156e43c13f7bac66de494bd9181c94497ad05da8619c9987c1ccb816a8577ca7', 74482, None),
 ('4ebd4423d2ab59540c501b6622cb53a52163bda63ba24c092463de7f4d67fef9', 76594, None),
 ('c836c14a4677ec716ae2b0a170eed751e0d6ee2f05b0edf5e78d5b156f56cd9c', 76626, None))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# These exclusions follow only the complete actual callers: both signed
# word-divisor signs and positive bounded unsigned divisors remain admitted.
# The two EXTU.W branches and the convex byte cap have fixed outcomes.
# Every full preceding helper original remains required.
INFEASIBLE_SITES=({0xBDC9E,0xBDCB6}
    |set(range(0x21C70,0x21CD6,2))|set(range(0x21D6A,0x21DC6,2)))
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
    same(observed['exit'],wanted,'the state ratio caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the state ratio caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the state ratio caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the state ratio caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the state ratio caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the state ratio caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the state ratio caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the state ratio caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the state ratio caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the state ratio caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the state ratio caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the state ratio caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the state ratio caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the state ratio caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the state ratio caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the state ratio caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the state ratio caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the state ratio caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the state ratio caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the state ratio caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the state ratio caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the state ratio caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the state ratio caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the state ratio caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the state ratio caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the state ratio caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the state ratio caller physically accesses a selected unsupported ROM/native-RAM root or alias')
