"""Exact natural derivative-scale caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import derivative_scale_caller_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 138602: (138696, 4, 1),
 138604: (138700, 4, 2),
 156884: (156916, 4, 7),
 156904: (156912, 4, 6),
 156928: (156960, 4, 7),
 156948: (156956, 4, 6),
 158118: (158144, 4, 2),
 751852: (751980, 4, 4),
 751854: (751954, 2, 0),
 751874: (751956, 2, 2),
 751880: (751958, 2, 6),
 751886: (752032, 4, 2),
 751898: (751960, 2, 5),
 751916: (752036, 4, 4),
 751936: (752040, 4, 6),
 752048: (752632, 4, 2),
 752056: (752636, 4, 2),
 752078: (752640, 4, 4),
 752086: (752644, 4, 2),
 752108: (752648, 4, 4),
 752110: (752652, 4, 5),
 752112: (752656, 4, 2),
 752122: (752378, 2, 2),
 752138: (752660, 4, 5),
 752158: (752660, 4, 5),
 752170: (752664, 4, 6),
 752172: (752380, 2, 0),
 752202: (752668, 4, 0),
 752218: (752640, 4, 7),
 752224: (752382, 2, 0),
 752246: (752384, 2, 2),
 752252: (752386, 2, 2),
 752258: (752672, 4, 2),
 752270: (752388, 2, 6),
 752288: (752676, 4, 4),
 752294: (752680, 4, 5),
 752298: (752684, 4, 2),
 752308: (752688, 4, 5),
 752332: (752692, 4, 2),
 752356: (752640, 4, 7),
 752364: (752644, 4, 2),
 752398: (752696, 4, 4),
 752400: (752700, 4, 5),
 752402: (752656, 4, 2),
 752412: (752624, 2, 2),
 752480: (752660, 4, 6),
 752498: (752660, 4, 6),
 752502: (752626, 2, 0),
 752510: (752664, 4, 6),
 752512: (752628, 2, 0)}
NATIVE_ROOTS=(('e50bf2ae3fbd6e46ee8421e61c6d3019fcab782748a1de7f49b36fb90fdc2821', 89072, None),
 ('135b4bf6288e3b975c8a616f93fc760776bb5751356b8805576b24ec0c97ee1a', 89216, None),
 ('036bd425947d6ea6b3d8f732a6427ad3e7bd555898e56beb96b30b026c1c9332', 4294906126, 16781582),
 ('32b20036c5e60a367da500146f25121094a9f11af3952e9063153cab4301788f', 4294906126, 16781582),
 ('76aa231e36017454b261a39ee19edf364ad4abb611477e3c0ca260f1e52c46b9', 4294907790, 16783246),
 ('92dfcb0943b8b651253776a006fba60c01487ea7b768b2dab387d69302848c14', 4294911795, 16787251),
 ('7defb8aedceeaaa17c4a43a870460907d61b5e9933bea8b136732115ab3615a3', 4294911795, 16787251),
 ('ec181ca2f794853e947329334c40017f426533116fd07a94ffe46dc1174b70e9', 4294914888, 16790344),
 ('9f418c7091d6acf535a07437acd5068090a8b59e50d8426db950136c98b527e3', 4294914888, 16790344),
 ('9d3662e96629145aec9374547056749303b0b6295506e49ba4693a4722ef566e', 4294915488, 16790944),
 ('453f6650c03c4604fd20fcb4c273cf86f51d642ee1161d9a552dc0c7d39cc01f', 4294915510, 16790966))
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
INFEASIBLE_SITES={0x26D0A,0x26D0C,0x21BCC,0x21BCE}|set(range(0x21C70,0x21CD6,2))|set(range(0x21D6A,0x21DC6,2))
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
    if observed['frame_before'][160:164]!=observed['context'][19].to_bytes(4,'big'):
        raise ValueError('the derivative-scale caller detaches the complete fifth stack argument from its raw context word')
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the derivative-scale caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the derivative-scale caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the derivative-scale caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the derivative-scale caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the derivative-scale caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the derivative-scale caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the derivative-scale caller omits its complete real instruction trace')
    same(tuple(row['site'] for row in trace),value['path'],
        'the derivative-scale caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the derivative-scale caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the derivative-scale caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the derivative-scale caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the derivative-scale caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the derivative-scale caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the derivative-scale caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the derivative-scale caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # The scalar quotient does not determine DIV1 remainder R1 or Q.
        # Complete actual entry state remains bound to the instruction trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the derivative-scale caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the derivative-scale caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the derivative-scale caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the derivative-scale caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the derivative-scale caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the derivative-scale caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the derivative-scale caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the derivative-scale caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the derivative-scale caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535) if row['owner'].endswith('/ram') else None) for row in rows)
    same(identities,NATIVE_ROOTS,'the derivative-scale caller substitutes an exact original ROM/native-RAM root or alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,native,alias in NATIVE_ROOTS for address in ((native,) if alias is None else (native,alias))):
            raise ValueError('the derivative-scale caller physically accesses a selected unsupported ROM/native-RAM root or alias')
