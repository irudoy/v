"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={335926: (336244, 4, 0),
 335932: (336240, 4, 6),
 335936: (36242, 1, 0),
 335944: (336256, 4, 6),
 335946: (34814, 1, 2),
 335948: (336260, 4, 6),
 335966: (336248, 4, 2),
 335970: (336176, 2, 6),
 335986: (336248, 4, 6),
 335988: (336178, 2, 0),
 336022: (336168, 2, 5),
 336030: (336264, 4, 6),
 336082: (336168, 2, 5)}
READ={335954: (8928, 1, 0),
 335980: (5166, 2, 6),
 335990: (5887, 1, 2),
 335996: (4640, 1, 0),
 336004: (4702, 1, 0),
 336038: (9032, 2, 5),
 336050: (5014, 2, 6),
 336094: (4640, 1, 0)}
WRITE={336002: (4640, 1, 0), 336068: (9032, 2, 6), 336100: (4640, 1, 0)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={}
INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}

NATIVE_RAM_ROOTS=(('8173eb6cb77ae22dd0fa72ea3bc4cdb758d15cd421cfac9f79cacfa10055387d', 4294906382, 16781838),)


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[]
    for site in value['path']:
        if site in value['tags']['frame_accesses']:
            mode,depth,register,raw=value['tags']['frame_accesses'][site]
            address,width,domain=observed['sp']-depth,4,'frame'
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write';offset,width,register=(READ if mode=='read' else WRITE)[site]
            if site in (0x5206C,0x520A6,0x520B2,0x520C4):offset+=2*value['tags']['index']
            address,domain=RAM_BASE+offset,'ram'
            raw=(observed['memory_before'][0][offset:offset+width] if mode=='read'
                else value['tags']['physical_writes'][site])
        else:continue
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the indexed word update original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the indexed word update original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the indexed word update original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the indexed word update original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the indexed word update original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the indexed word update original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the indexed word update original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the indexed word update original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the indexed word update original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the indexed word update original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the indexed word update original leaves its independent byte/word product width premise')
    points={row['site']:row for row in trace}
    if points[0x52038]['after']['gbr']!=RAM_BASE+0x120E:
        raise ValueError('the indexed word original changes the actual temporary GBR base')
    if value['tags']['counter_changed']:
        if (points[0x5209C]['after']['sr']!=value['tags']['interrupted_sr']
                or points[0x5208A]['before']['sr']!=((observed['sr_before']&~1)|1)
                or points[0x520D8]['after']['sr']!=value['sr']):
            raise ValueError('the indexed word original changes the temporary interrupt mask or exact restored SR')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535)) for row in rows)
    if (not test_contract.exact(identities,NATIVE_RAM_ROOTS)
            or any(not row['owner'].endswith('/ram') or not 0xFFFF0000<=row['address']<=0xFFFFFFFF for row in rows)):
        raise ValueError('the indexed word update substitutes a selected native RAM original or its exact simulator alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for original,native,alias in NATIVE_RAM_ROOTS for address in (native,alias)):
            raise ValueError('the indexed word update physically accesses a selected native RAM datum root or its simulator alias')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the indexed word update substitutes an undeclared ROM source for its exact pool or configuration operand')
