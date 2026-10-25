"""Exact natural paired flag writer caller/helper paths, physical operands and complete returned state."""
from kb import test_contract
from kb import paired_inhibit_writer_withdrawal_contract as contract
RAM_BASE=0x01000000
ROM={510206: (510688, 4, 0),
 510210: (510692, 4, 6),
 510230: (510696, 4, 5),
 510266: (510684, 4, 4),
 510314: (510552, 2, 0),
 510318: (510554, 2, 0),
 510322: (510556, 2, 0),
 510346: (510558, 2, 0),
 510380: (510688, 4, 0),
 510384: (510692, 4, 5),
 510402: (510700, 4, 2),
 510404: (510560, 2, 0),
 510406: (510704, 4, 5),
 510418: (510696, 4, 6),
 510452: (510692, 4, 5),
 510470: (510684, 4, 5),
 510504: (510562, 2, 0),
 510508: (510564, 2, 0),
 510512: (510566, 2, 0),
 510522: (510568, 2, 0),
 514124: (514208, 4, 6)}
NATIVE_ROOTS=(('573e631e56ccae93bdac53c1906dadcc90aeb13a9fef5f5abe97af5d7fa3f437', 4294920773, 16796229),
 ('177290ea6eaeccff871ba8e2f041ef206f867d937656ff13aa6db177a9d94298', 4294920816, 16796272),
 ('f5ad4f5cd86f01b4ce9c961c46d182bd1a5ca987660d96cbe7df5f127d23cd36', 4294920902, 16796358),
 ('ace066de89ca0e146133354756c38ccda95830904176750f776020f78d758261', 4294924056, 16799512),
 ('e05ca8c55888e89a68795f8e3d2d7e22173743a4a5c13ad589ebab1854b4c532', 4294924056, 16799512))
NATIVE_FUNCTION_SCOPES=(('573e631e56ccae93bdac53c1906dadcc90aeb13a9fef5f5abe97af5d7fa3f437', 510376, 4294920773, 16796229),
 ('177290ea6eaeccff871ba8e2f041ef206f867d937656ff13aa6db177a9d94298', 510376, 4294920816, 16796272),
 ('f5ad4f5cd86f01b4ce9c961c46d182bd1a5ca987660d96cbe7df5f127d23cd36', 510376, 4294920902, 16796358),
 ('ace066de89ca0e146133354756c38ccda95830904176750f776020f78d758261', 510202, 4294924056, 16799512),
 ('e05ca8c55888e89a68795f8e3d2d7e22173743a4a5c13ad589ebab1854b4c532', 510376, 4294924056, 16799512))
RMW_SITES=(510232, 510236, 510240, 510244, 510248, 510252, 510256, 510288, 510292, 510296, 510300, 510304, 510308, 510312, 510420, 510424, 510428, 510432, 510436, 510440, 510444, 510478, 510482, 510486, 510490, 510494, 510498, 510502)
EXACT_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}
# Every instruction of the complete caller and real nibble-mask helper is required.
INFEASIBLE_SITES=set()
FEASIBLE_SITES=EXACT_SITES-INFEASIBLE_SITES


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,result,value,fixture):
    events=[]
    for index,site in enumerate(value['path']):
        if index in value['events']:
            events.extend(value['events'][index]);continue
        if site in ROM:
            address,width,register=ROM[site]
            events.append(dict(site=site,mode='read',address=address,width_bytes=width,register=register,
                domain='rom',bytes=fixture[address:address+width].hex()))
    return events


def require(observed,result,value,fixture):
    wanted=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],wanted,'the paired flag writer caller changes complete independent instruction CPU/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the paired flag writer caller changes complete separately composed RAM or ordered saved frame words')
    if any(result['registers'][index]!=wanted for index,wanted in value['known_registers'].items()):
        raise ValueError('the paired flag writer caller changes separately composed known returned registers')
    if result['sr']&value['sr_mask']!=value['sr']&value['sr_mask']:
        raise ValueError('the paired flag writer caller changes separate T, interrupt, M or preserved Q state')
    if any(result[key]!=value[key] for key in ('gbr','mach','macl','pr','sp')):
        raise ValueError('the paired flag writer caller changes complete independent special-register or stack return state')
    same(result['accesses'],physical(observed,result,value,fixture),
        'the paired flag writer caller changes ordered physical ROM/RAM/frame site, address, width, register or exact bytes')
    for site in RMW_SITES:
        if site not in result['code']:continue
        operands=[row for row in result['accesses'] if row['site']==site]
        if (len(operands)!=2 or [row['mode'] for row in operands]!=['read','write']
                or operands[0]['address']!=operands[1]['address']
                or any(row['width_bytes']!=1 or row['register'] is not None or row['domain']!='ram' for row in operands)):
            raise ValueError('the paired flag writer original changes one ordered physical read/modify/write operand pair')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the paired flag writer caller omits its complete real instruction trace')
    initial=trace[0]['before']
    same(tuple(initial[k] for k in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],
            observed['sr_before'],observed['continuation']),
        'the paired flag writer caller detaches complete instruction entry state from its actual incoming CPU')
    same(tuple(row['site'] for row in trace),value['path'],
        'the paired flag writer caller changes a separate natural branch, axis scan, helper call or post-delay return path')
    same(result['branches'],value['controls'],'the paired flag writer caller changes independently composed branch outcomes or real controls')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the paired flag writer caller changes an exact executed natural caller/helper instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the paired flag writer caller changes a real branch, call or return delay slot')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the paired flag writer caller leaves its complete feasible closure or ordered continuation')
        if index+1<len(trace):
            same(row['after'],trace[index+1]['before'],
                'the paired flag writer caller detaches complete intermediate CPU/SR state from its next real instruction')
    if len(result['calls'])!=len(value['calls']):raise ValueError('the paired flag writer caller omits or invents a real helper call')
    cursor=0
    for actual,expected in zip(result['calls'],value['calls']):
        same(tuple(actual[k] for k in ('site','target','return_address','sp')),
            tuple(expected[k] for k in ('site','target','return_address','sp')),
            'the paired flag writer caller changes a natural helper target, continuation or stack argument position')
        post=actual['entry']
        # Every helper argument and returned register has a separate exact value.
        # Complete actual entry state remains bound to the continuous trace.
        for index,wanted in enumerate(expected['registers']):
            if wanted is not None and post['registers'][index]!=wanted:
                raise ValueError('the paired flag writer caller changes a known separate post-delay helper register')
        same(tuple(post[k] for k in ('sp','gbr','mach','macl','pr')),
            (expected['sp'],expected['gbr'],expected['mach'],expected['macl'],expected['return_address']),
            'the paired flag writer caller changes separately composed post-delay helper SP/PR or special registers')
        if post['sr']&expected['sr_mask']!=expected['sr']&expected['sr_mask']:
            raise ValueError('the paired flag writer caller changes the known independently composed helper-entry SR')
        first=next((i+2 for i in range(cursor,len(trace)) if trace[i]['site']==expected['site']),None)
        if first is None or trace[first]['site']!=expected['target']:
            raise ValueError('the paired flag writer caller replaces its actual real helper entry')
        entered=trace[first]['before']
        same(tuple(post[k] for k in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
                entered['macl'],entered['sr'],entered['pr']),
            'the paired flag writer caller detaches complete helper-entry state from the exact post-delay instruction path')
        cursor=first
        terminal=next((i for i in range(first,len(trace)) if trace[i]['site']==expected['return_site']
            and i+1<len(trace) and trace[i+1]['next']==expected['return_address']),None)
        if terminal is None:raise ValueError('the paired flag writer caller omits a real natural helper post-delay return')
        restored=trace[terminal+1]['after']
        for index,wanted in enumerate(expected['return_registers']):
            if wanted is not None and restored['registers'][index]!=wanted:
                raise ValueError('the paired flag writer caller changes a known separately composed helper returned register')
        if (restored['registers'][15]!=expected['sp'] or restored['pr']!=expected['return_address']
                or any(restored[k]!=expected['return_'+k] for k in ('gbr','mach','macl'))
                or restored['sr']&expected['return_sr_mask']!=expected['return_sr']&expected['return_sr_mask']):
            raise ValueError('the paired flag writer caller changes independent helper post-delay SP/PR, special registers or known SR')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=result['registers']
            or any(last['after'][key]!=result[key] for key in ('gbr','mach','macl','sr','pr'))):
        raise ValueError('the paired flag writer caller changes complete natural post-delay returned state')


def require_no_selected_datum(result,rows,entry):
    identities=tuple((row['original_claim_sha256'],row['address'],RAM_BASE+(row['address']&65535)) for row in rows)
    same(identities,NATIVE_ROOTS,'the paired flag writer substitutes an exact original native root or alias')
    scopes=tuple((row['original_claim_sha256'],row['function'],row['address'],RAM_BASE+(row['address']&65535)) for row in rows)
    same(scopes,NATIVE_FUNCTION_SCOPES,'the paired flag writer substitutes the exact original function-to-root scope')
    trace=result.get('trace')
    if (type(entry) is not int or entry not in contract.ENTRIES or type(trace) is not list or not trace
            or trace[0].get('site')!=entry):
        raise ValueError('the paired flag writer detaches selected root absence from its complete actual observed entry')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for identity,function,native,alias in NATIVE_FUNCTION_SCOPES if function==entry for address in (native,alias)):
            raise ValueError('the paired flag writer physically accesses an exact selected root or alias for this actual entry')
