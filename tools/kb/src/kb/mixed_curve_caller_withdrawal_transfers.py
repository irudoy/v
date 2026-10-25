"""Exact natural mixed curve caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import mixed_curve_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 138602: (138696, 4, 1),
 138604: (138700, 4, 2),
 156282: (156324, 4, 7),
 156314: (156320, 4, 7),
 156660: (156684, 4, 0),
 156668: (156680, 4, 6),
 156796: (156828, 4, 7),
 156816: (156824, 4, 6),
 157790: (157856, 4, 7),
 158054: (158080, 4, 2),
 158118: (158144, 4, 2),
 158388: (158396, 4, 6),
 242848: (243312, 4, 0),
 242858: (243300, 4, 6),
 242910: (243300, 4, 6),
 242926: (243332, 4, 4),
 242938: (243336, 4, 4),
 242942: (243340, 4, 2),
 269754: (269940, 4, 0),
 269758: (269944, 4, 6),
 269776: (269936, 4, 2),
 269778: (269922, 2, 0),
 269782: (269924, 2, 0),
 269788: (269926, 2, 0),
 269796: (269948, 4, 2),
 269800: (269928, 2, 0),
 269808: (269920, 2, 0),
 269814: (269932, 4, 4),
 269826: (269952, 4, 2),
 310732: (311048, 4, 0),
 310738: (311076, 4, 6),
 310740: (311080, 4, 7),
 310750: (311048, 4, 13),
 310768: (311026, 2, 0),
 310776: (311028, 2, 0),
 310786: (311084, 4, 5),
 310814: (311088, 4, 6),
 310822: (311092, 4, 6),
 310834: (311096, 4, 6),
 310836: (311100, 4, 4),
 310840: (311104, 4, 5),
 310842: (311108, 4, 2),
 310848: (311112, 4, 7),
 310854: (311116, 4, 7),
 310862: (311120, 4, 4),
 310864: (311124, 4, 5),
 310866: (311128, 4, 6),
 310868: (311132, 4, 2),
 310890: (311030, 2, 0),
 310902: (311136, 4, 0),
 310910: (311140, 4, 6),
 310940: (311144, 4, 6),
 310956: (311048, 4, 13),
 310960: (311028, 2, 0),
 310962: (311144, 4, 6),
 311008: (311032, 2, 0),
 416182: (416432, 4, 14),
 416184: (416402, 2, 0),
 416186: (416488, 4, 5),
 416212: (416492, 4, 6),
 416232: (416496, 4, 6),
 416238: (416404, 2, 0),
 416254: (416406, 2, 2),
 416258: (416408, 2, 0),
 416284: (416500, 4, 6),
 416294: (416504, 4, 6),
 416320: (416508, 4, 4),
 416322: (416512, 4, 5),
 416324: (416516, 4, 2),
 416380: (416410, 2, 2),
 416388: (416412, 2, 0)}
NATIVE_ROOTS=(('ea68a6b80640ced3d347421e1ee38375a22e6c9cf0533775b444cda015a877b7', 68494, None),
 ('c638206ca7fd33d917a82061925c79683301c5962be263783d279abd091196c6', 74134, None),
 ('aa811f9566043dbf2c67f43e399ca35b654a4e71c2e867c02a1770567444e549', 74142, None),
 ('da9b2c172b7614e33d3f913c1790f81e57080f8fa8a6a04819431a70df59ff26', 75688, None),
 ('798c9e94fd08d7709381dd7e051c1adbfdddf5b66dbf86bf5fda357d950b9098', 75752, None),
 ('7a47a5cc01d09c1a49e7799cdcc523dbc8025b812b7c275d2e0d2056f0e62aaa', 78338, None),
 ('8493572c035dac033b196ebb017eda328de39e92d345597c2bf41d343b257a2b', 87200, None),
 ('4246f372f407cd8d806292efe7d3c6e57559411abc87c010b448167fb21a3ad7', 87456, None))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# These exclusions follow only the actual four caller operands. The full
# generic division, implicit endpoint and register originals remain required.
INFEASIBLE_SITES=({0x21BCC,0x21BCE,0x26402,0x26404,0x26A60,0x26A62,0x26D0A,0x26D0C}
    |set(range(0x21C70,0x21C7C,2))|set(range(0x21CEC,0x21D76,2))
    |set(range(0x26AAA,0x26AB4,2)))
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
    same(observed['exit'],wanted,'the mixed curve caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the mixed curve caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the mixed curve caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the mixed curve caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the mixed curve caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the mixed curve caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the mixed curve caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the mixed curve caller detaches complete instruction entry state from its actual incoming CPU')
    if any(event['address']<0x15042 and 0x1503E<event['address']+event['width_bytes']
            for event in result['accesses']):
        raise ValueError('the mixed curve caller accesses the immutable unread gap between its two disjoint implicit curves')
    same(tuple(row['site'] for row in trace),value['path'],
        'the mixed curve caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the mixed curve caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the mixed curve caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the mixed curve caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the mixed curve caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the mixed curve caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the mixed curve caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the mixed curve caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the mixed curve caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the mixed curve caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the mixed curve caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the mixed curve caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the mixed curve caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the mixed curve caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the mixed curve caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the mixed curve caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the mixed curve caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the mixed curve caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the mixed curve caller physically accesses a selected unsupported ROM/native-RAM root or alias')
