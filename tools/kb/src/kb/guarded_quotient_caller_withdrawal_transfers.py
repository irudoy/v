"""Exact natural guarded quotient caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import guarded_quotient_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 340668: (340960, 4, 0),
 340674: (340964, 4, 2),
 340678: (340968, 4, 12),
 340710: (340960, 4, 11),
 340712: (340922, 2, 0),
 340722: (340972, 4, 7),
 340752: (340972, 4, 7),
 340778: (340976, 4, 5),
 340802: (340924, 2, 0),
 340804: (340980, 4, 1),
 340814: (340926, 2, 0),
 340824: (340984, 4, 2),
 340844: (340924, 2, 0),
 340848: (340926, 2, 0),
 340860: (340928, 2, 2),
 340884: (340924, 2, 0),
 340888: (340926, 2, 0),
 340904: (340928, 2, 2),
 340992: (341180, 4, 11),
 340994: (341166, 2, 0),
 340998: (341168, 2, 0),
 341006: (341170, 2, 0),
 341012: (341172, 2, 0),
 341022: (341174, 2, 0),
 341026: (341184, 4, 6),
 341034: (341176, 2, 0),
 341070: (341188, 4, 6),
 341078: (341192, 4, 5),
 341108: (341196, 4, 2),
 341132: (341178, 2, 0),
 478060: (478500, 4, 0),
 478066: (478520, 4, 6),
 478086: (478524, 4, 6),
 478088: (478504, 4, 5),
 478098: (478288, 2, 0),
 478108: (478528, 4, 2),
 478114: (478532, 4, 2),
 478130: (478532, 4, 3),
 478148: (478516, 4, 6),
 480010: (480324, 4, 7),
 480012: (480074, 2, 0),
 480022: (480320, 4, 2),
 480032: (480328, 4, 5),
 480034: (480076, 2, 0),
 480044: (480332, 4, 4),
 480058: (480336, 4, 2),
 480092: (480320, 4, 3),
 480104: (480332, 4, 4),
 480112: (480286, 2, 6),
 480132: (480324, 4, 7),
 480140: (480288, 2, 0)}
NATIVE_ROOTS=(('6058df3ab81fa13bb54d91f7e75c7a296e9dcd50b80d45dd2762b6d24b56837a', 72078, None),
 ('6c9f4250619347ff8194043c8243c7d30e4d4bb389b002b66a88bf87efd8f235', 75440, None),
 ('c1d274e32563d7c74891c872fa46392064637818cd6e89dee35c5598cd0d09a8', 75448, None),
 ('868537232a2d40bec435a486835bab723ad56022b92b2e0be29c65169deec358', 76418, None),
 ('d961725e5c49bea33ba3188206854a27395362e43f18d5f11d7ed583bb63eb41', 86960, None),
 ('6c58ca67411a67c211c802575a710fae9d7e145d195d34f9f08d4e9a9caaf8b5', 86968, None),
 ('d5899807d9addb2b878cf5d643b4dfa2a132c11e24a42ebd8bfe47950dea631d', 87920, None),
 ('1b3937e671acbb4fcf17f1915a3e236caf33f087a088b1e084202159125123b6', 4294907384, 16782840))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
INFEASIBLE_SITES={0x21BCC,0x21BCE,0x21CCC,0x21CCE,0x5337C,0x5337E}
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
    same(observed['exit'],wanted,'the guarded quotient caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the guarded quotient caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the guarded quotient caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the guarded quotient caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the guarded quotient caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the guarded quotient caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the guarded quotient caller omits its complete real instruction trace')
    same(tuple(row['site'] for row in trace),value['path'],
        'the guarded quotient caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the guarded quotient caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the guarded quotient caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the guarded quotient caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the guarded quotient caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the guarded quotient caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the guarded quotient caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the guarded quotient caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the guarded quotient caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the guarded quotient caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the guarded quotient caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the guarded quotient caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the guarded quotient caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the guarded quotient caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the guarded quotient caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the guarded quotient caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the guarded quotient caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the guarded quotient caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the guarded quotient caller physically accesses a selected unsupported ROM/native-RAM root or alias')
