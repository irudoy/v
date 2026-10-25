"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={325602: (325916, 4, 6),
 325604: (35647, 1, 0),
 325614: (325952, 4, 2),
 325618: (325956, 4, 4),
 325622: (37088, 2, 5),
 325624: (34014, 1, 0),
 325642: (325956, 4, 3),
 325644: (34014, 1, 0),
 325652: (325960, 4, 6),
 325662: (325932, 4, 2),
 325664: (325844, 2, 0),
 325678: (325960, 4, 6),
 325686: (325964, 4, 6),
 325694: (325968, 4, 6),
 325696: (33751, 1, 0),
 325702: (325972, 4, 6),
 325710: (325912, 4, 6),
 325720: (325940, 4, 2),
 325724: (325956, 4, 3),
 325728: (34007, 1, 2),
 325734: (325908, 4, 2),
 325738: (325956, 4, 3),
 325742: (34012, 1, 0),
 325752: (325956, 4, 3),
 325754: (34011, 1, 0),
 325762: (325932, 4, 2),
 325764: (325844, 2, 0),
 325766: (325956, 4, 3),
 325770: (34014, 1, 0),
 325784: (325956, 4, 3),
 325786: (34014, 1, 0),
 325794: (325932, 4, 3),
 325796: (325844, 2, 0),
 325810: (325932, 4, 2),
 325812: (325844, 2, 0),
 325834: (325932, 4, 3),
 325836: (325844, 2, 0),
 325852: (325932, 4, 3),
 325856: (325894, 2, 0),
 325870: (325932, 4, 3),
 325874: (325894, 2, 0),
 325882: (325932, 4, 3),
 325886: (325894, 2, 0),
 326086: (326536, 4, 0),
 326092: (326516, 4, 6),
 326096: (35647, 1, 0),
 326120: (326528, 4, 7),
 326122: (326302, 2, 0),
 326128: (326528, 4, 7),
 326132: (326302, 2, 0),
 326156: (326302, 2, 0),
 326168: (326532, 4, 2),
 326172: (326540, 4, 4),
 326176: (34990, 1, 0),
 326182: (34989, 1, 0),
 326200: (326528, 4, 7),
 326202: (326302, 2, 0),
 326214: (326544, 4, 6),
 326224: (326532, 4, 2),
 326228: (326540, 4, 4),
 326232: (34985, 1, 0),
 326238: (326548, 4, 2),
 326244: (34984, 1, 0),
 326250: (326552, 4, 2),
 326256: (34986, 1, 0),
 326262: (326528, 4, 7),
 326264: (326302, 2, 0),
 326266: (34983, 1, 2)}
READ={325654: (9304, 1, 0),
 325666: (6450, 2, 6),
 325680: (9295, 1, 0),
 325688: (16976, 1, 0),
 325704: (9423, 1, 0),
 325714: (16852, 1, 0),
 325726: (4366, 1, 6),
 325740: (4531, 1, 7),
 325768: (6450, 2, 7),
 325814: (6450, 2, 6),
 326090: (9367, 1, 0),
 326102: (9295, 1, 0),
 326112: (9299, 1, 0),
 326136: (5776, 1, 6),
 326174: (4531, 1, 6),
 326208: (9309, 1, 0),
 326218: (16852, 1, 0),
 326230: (4531, 1, 6),
 326240: (4209, 1, 0),
 326254: (4366, 1, 6),
 326268: (5776, 1, 5),
 326286: (9367, 1, 0)}
WRITE={325798: (6450, 2, 4),
 325838: (6450, 2, 2),
 325858: (6450, 2, 2),
 325876: (6450, 2, 2),
 325888: (6450, 2, 2),
 326126: (5776, 1, 5),
 326160: (5776, 1, 2),
 326196: (9367, 1, 0),
 326206: (5776, 1, 2),
 326284: (9367, 1, 0)}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={325600: ('write', 4, None, 17),
 325892: ('read', 4, None, 17),
 326084: ('write', 4, None, 15),
 326298: ('read', 4, None, 15)}
INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}

NATIVE_RAM_ROOTS=(('7c4981b684e613d09f1fe29f60b90f840989aa89579723d19a80eefc49e84aef', 4294906286, 16781742),
 ('18889d3895c191b910d24b55b7f40067d1f548dc0b1558837e58b8f3c586d917', 4294906286, 16781742))


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[]
    for site in value['path']:
        if site in FRAME:
            mode,depth,register,source=FRAME[site]
            address,width,domain=observed['sp']-depth,4,'frame'
            raw=observed['context'][source].to_bytes(4,'big')
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ or site in WRITE:
            mode='read' if site in READ else 'write';offset,width,register=(READ if mode=='read' else WRITE)[site]
            address,domain=RAM_BASE+offset,'ram'
            if mode=='write':
                if site not in value['tags']['physical_writes']:
                    raise ValueError('the RPM-state scalar equations omit an actual ordered status or accumulator write')
                raw=value['tags']['physical_writes'][site]
            else:
                raw=value['tags']['physical_reads'].get(site,observed['memory_before'][0][offset:offset+width])
        else:continue
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the RPM state withdrawal original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the RPM state withdrawal original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the RPM state withdrawal original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the RPM state withdrawal original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the RPM state withdrawal original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the RPM state withdrawal original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the RPM state withdrawal original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the RPM state withdrawal original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the RPM state withdrawal original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the RPM state withdrawal original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the RPM state withdrawal original leaves its independent byte/word product width premise')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535)) for row in rows)
    if (not test_contract.exact(identities,NATIVE_RAM_ROOTS)
            or any(not row['owner'].endswith('/ram') or not 0xFFFF0000<=row['address']<=0xFFFFFFFF for row in rows)):
        raise ValueError('the RPM state withdrawal substitutes a selected native RAM original or its exact simulator alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for original,native,alias in NATIVE_RAM_ROOTS for address in (native,alias)):
            raise ValueError('the RPM state withdrawal physically accesses a selected native RAM datum root or its simulator alias')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the RPM state withdrawal substitutes an undeclared ROM source for its exact pool or configuration operand')
