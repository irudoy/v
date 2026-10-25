"""Exact natural DFCO state caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import dfco_state_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={328694: (328824, 4, 9),
 328696: (328704, 2, 0),
 328698: (328828, 4, 10),
 328734: (328808, 4, 5),
 328742: (328832, 4, 2),
 328744: (328816, 4, 3),
 328852: (329392, 4, 4),
 328864: (329392, 4, 4),
 328894: (329392, 4, 4),
 328928: (329396, 4, 5),
 328936: (329400, 4, 2),
 328944: (329404, 4, 5),
 328952: (329408, 4, 5),
 328960: (329412, 4, 2),
 328964: (329416, 4, 4),
 328976: (329404, 4, 5),
 328984: (329412, 4, 3),
 328986: (329420, 4, 2),
 328990: (329416, 4, 1),
 329012: (329412, 4, 3),
 329034: (329042, 2, 0),
 329036: (329416, 4, 3),
 329056: (329416, 4, 3),
 329072: (329356, 2, 0),
 329074: (329424, 4, 5),
 329084: (329358, 2, 0),
 329086: (329428, 4, 5),
 329096: (329360, 2, 0),
 329102: (329356, 2, 0),
 329110: (329392, 4, 4),
 329118: (329358, 2, 0),
 329126: (329360, 2, 0),
 329130: (329362, 2, 0),
 329142: (329392, 4, 4),
 329152: (329358, 2, 0),
 329188: (329358, 2, 0),
 329194: (329360, 2, 0),
 329198: (329362, 2, 0),
 329206: (329432, 4, 6),
 329214: (329358, 2, 0),
 329222: (329360, 2, 0),
 329226: (329362, 2, 0),
 329230: (329392, 4, 4),
 329240: (329358, 2, 0),
 329248: (329360, 2, 0),
 329252: (329362, 2, 0),
 329256: (329364, 2, 0),
 329262: (329366, 2, 0),
 329266: (329362, 2, 0),
 329294: (329364, 2, 0),
 329296: (329436, 4, 2),
 329300: (329440, 4, 13),
 329334: (329396, 4, 7),
 329380: (329390, 2, 0),
 329384: (329444, 4, 5),
 329462: (329960, 4, 5),
 329474: (329964, 4, 3),
 329484: (329770, 2, 0),
 329488: (329772, 2, 0),
 329492: (329774, 2, 0),
 329502: (329772, 2, 0),
 329514: (329774, 2, 0),
 327716: (328236, 4, 0),
 327722: (328240, 4, 11),
 327726: (328244, 4, 6),
 327736: (328248, 4, 7),
 327738: (328010, 2, 0),
 327742: (328252, 4, 6),
 327744: (328012, 2, 4),
 327758: (328256, 4, 5),
 327770: (328252, 4, 6),
 327772: (328014, 2, 4),
 327786: (328260, 4, 5),
 327826: (328264, 4, 6),
 327828: (328016, 2, 0),
 327836: (328268, 4, 6),
 327844: (328272, 4, 3),
 327846: (328276, 4, 4),
 327850: (328280, 4, 6),
 327856: (328272, 4, 1),
 327860: (328284, 4, 4),
 327864: (328280, 4, 6),
 327872: (328256, 4, 6),
 327884: (328288, 4, 2),
 327948: (328272, 4, 3),
 327950: (328292, 4, 1),
 327976: (328292, 4, 3),
 327992: (328296, 4, 6),
 328030: (328300, 4, 6),
 328060: (328256, 4, 6),
 328072: (328288, 4, 2),
 328100: (328248, 4, 7),
 328102: (328230, 2, 0),
 328104: (328304, 4, 6),
 328108: (328232, 2, 0),
 328122: (328308, 4, 6),
 328136: (328312, 4, 5),
 328172: (328316, 4, 6),
 328176: (328320, 4, 6),
 328200: (328300, 4, 7),
 328324: (328772, 4, 6),
 328348: (328776, 4, 3),
 328352: (328780, 4, 5),
 328378: (328784, 4, 2),
 328382: (328788, 4, 5),
 328432: (328792, 4, 5),
 328492: (328792, 4, 5),
 328554: (328796, 4, 6),
 154678: (154920, 4, 1),
 156552: (156570, 2, 0),
 156560: (156572, 4, 6),
 158388: (158396, 4, 6)}
NATIVE_ROOTS=(('fdaf3867d48487219ed37f59f2a79110967257a3933c1f3d3a5cda122d0e6a55', 73974, None),
 ('6c0df85a37c801ca6a7d79ebf2c0a3a3ecbbc363e008f3167114fa6b1e9f97c6', 75492, None),
 ('dc34c59bb20daae1cf6908bb684df035a5825e89e2c052b27b26f886a28add13', 75544, None),
 ('0cfcf76e8ab04eab6aacd76907296a3acee472114a88a3f750d00e421a820ef6', 75800, None),
 ('d01e3e567c9a6dd847ddc78602b5ac9db022cb3d6f01c911d22c3453c3a3735f', 76172, None),
 ('d81705553131a9e20163fc8625517644ea150b1f8488cea0052a8b505f4280d1', 4294907069, 16782525),
 ('95bd095088335f1392d2daceb203c8655979cc4c4c08cc25355c97a37cb1aaf3', 4294907070, 16782526))
STATE_EXACT_SITES={site for first,last in contract.STATE_SPANS for site in range(first,last,2)}
STATE_FEASIBLE_SITES=set(STATE_EXACT_SITES)
RESTORE_EXACT_SITES={site for row in contract.RESTORE_SOURCE_UNIT['code'] for site in range(row['start'],row['end'],2)}
# Both caller diagnostic arguments are fixed non-sentinel words.
# The real 26388 wrapper selects the byte tail26A84 with a zero width flag.
RESTORE_INFEASIBLE_SITES={0x25C54,*range(0x26A60,0x26A84,2),*range(0x26A9C,0x26AAA,2)}
RESTORE_FEASIBLE_SITES=RESTORE_EXACT_SITES-RESTORE_INFEASIBLE_SITES
EXACT_SITES=STATE_EXACT_SITES|RESTORE_EXACT_SITES
INFEASIBLE_SITES=set(RESTORE_INFEASIBLE_SITES)
FEASIBLE_SITES=STATE_FEASIBLE_SITES|RESTORE_FEASIBLE_SITES


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
    same(observed['exit'],wanted,'the DFCO state caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the DFCO state caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the DFCO state caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the DFCO state caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the DFCO state caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the DFCO state caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the DFCO state caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the DFCO state caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the DFCO state caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the DFCO state caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the DFCO state caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the DFCO state caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the DFCO state caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the DFCO state caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the DFCO state caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the DFCO state caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Every helper argument and returned register has a separate exact value.
        # Complete actual entry state remains bound to the continuous trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the DFCO state caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the DFCO state caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the DFCO state caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the DFCO state caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the DFCO state caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the DFCO state caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the DFCO state caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the DFCO state caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the DFCO state caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the DFCO state caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the DFCO state caller physically accesses a selected unsupported ROM/native-RAM root or alias')


READER1939_IDENTITY = ('000503e0-ffff1939-reader-withdraw', '1f4d2097a3f3458effbf6627988f7ca56994e2ac95e3acc84ff759a7a665c531', 4294908217, 328672)


def require1939_reader_with_retained_writes(result,row):
    same(tuple(row[key] for key in ('id','original_claim_sha256','address','function')),
        READER1939_IDENTITY,'the DFCO reader-direction guard substitutes its exact original owner or function')
    selected=[event for event in result['accesses'] if any(
        event['address']<=at<event['address']+event['width_bytes'] for at in (0xFFFF1939,RAM_BASE+0x1939))]
    if any(event['mode']!='write' for event in selected):
        raise ValueError('the DFCO reader-direction original reads native1939 or an overlapping alias container')
    if len(selected)>1:
        raise ValueError('the DFCO reader-direction original duplicates an actual class publication')
    writes=[]
    for event in selected:
        site=event['site'];register={0x50574:6,0x50594:2}.get(site)
        if (register is None or event['address']!=RAM_BASE+0x1939 or event['width_bytes']!=1
                or event['register']!=register or event['domain']!='ram'
                or type(event['bytes']) is not str or len(event['bytes'])!=2):
            raise ValueError('the DFCO reader-direction original changes a retained actual writer site, width, register or address')
        raw=int(event['bytes'],16)
        if raw not in ((0,1,2) if site==0x50574 else (10,)):
            raise ValueError('the DFCO reader-direction original changes its actual class or forced-ten publication')
        writes.append((site,raw))
    return tuple(writes)
