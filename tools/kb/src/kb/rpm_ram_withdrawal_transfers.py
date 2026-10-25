"""Independent ordered physical operands and complete natural leaf result guards."""

from kb import test_contract

RAM_BASE=0x01000000

# Exact physical instruction operands, not inferred table or caller bindings.
ROM={325430: (325904, 4, 6),
 325438: (325908, 4, 6),
 325980: (326512, 4, 0),
 325984: (326516, 4, 6),
 325986: (35647, 1, 0),
 325992: (326520, 4, 2),
 325996: (326524, 4, 7),
 326000: (37088, 2, 4),
 326002: (34014, 1, 0),
 326020: (326528, 4, 5),
 326022: (326300, 2, 0),
 326034: (326532, 4, 2),
 326040: (34013, 1, 0),
 326050: (34010, 1, 2),
 328586: (328800, 4, 1),
 328588: (328804, 4, 6),
 328596: (328808, 4, 6),
 328604: (328812, 4, 2),
 328606: (328816, 4, 5),
 328610: (35392, 1, 2),
 328624: (35915, 1, 0),
 328626: (328820, 4, 6),
 328628: (34572, 1, 0),
 328646: (35905, 1, 0),
 328650: (35904, 1, 0),
 328658: (35917, 1, 0),
 328660: (35916, 1, 0)}
READ={325432: (9288, 1, 0),
 325442: (4530, 1, 2),
 326024: (6450, 2, 6),
 326038: (4531, 1, 5),
 326068: (9340, 1, 0),
 328590: (16976, 1, 0),
 328598: (9304, 1, 0),
 328608: (4202, 1, 6)}
WRITE={}
# Special-register pushes/restores have no GPR operand in the physical record.
FRAME={325976: ('write', 4, None, 17),
 325978: ('write', 8, None, 15),
 326078: ('read', 8, None, 15),
 326082: ('read', 4, None, 17)}
INFEASIBLE_INSTRUCTIONS=()
FIXED_BRANCHES={}

NATIVE_RAM_ROOTS=(('79416ebc8cdc4b8e6cbb2346fbe6ea2a1c92bb11da20831c00f2d713bfaee2f1', 4294906286, 16781742),
 ('4feaccf3f93d5227575be371f3f8819566a59af0fa5c33fca4504992acfad289', 4294911347, 16786803),
 ('4f6035f8258eb3d177b5b7cde4c1e0981101765364f2e516d4a3fcddb1715dde', 4294924947, 16800403))


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def physical(observed,value,fixture):
    result=[]
    def event(site,mode,address,width,register,domain,raw):
        result.append(dict(site=site,mode=mode,address=address,width_bytes=width,
            register=register,domain=domain,bytes=raw.hex()))
    for site in value['path']:
        if site in (0x4F9AE,0x4F9B2):
            event(site,'read',RAM_BASE+0x247C,1,None,'ram',bytes((value['tags']['flags'],)))
            event(site,'write',RAM_BASE+0x247C,1,None,'ram',value['ram'][0x247C:0x247D])
            continue
        if site in FRAME:
            mode,depth,register,source=FRAME[site];address,width,domain=observed['sp']-depth,4,'frame'
            raw=observed['context'][source].to_bytes(4,'big')
        elif site in ROM:
            address,width,register=ROM[site];mode,domain='read','rom';raw=fixture[address:address+width]
        elif site in READ:
            offset,width,register=READ[site];address,domain,mode=RAM_BASE+offset,'ram','read'
            memory=value['ram'] if site==0x4F9B4 else observed['memory_before'][0]
            raw=memory[offset:offset+width]
        else:continue
        event(site,mode,address,width,register,domain,raw)
    return result


def require(observed,result,value,fixture):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the RPM RAM withdrawal original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the RPM RAM withdrawal original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=(value['ram'],)):
        raise ValueError('the RPM RAM withdrawal original changes independent complete frame or arithmetic RAM state')
    same(result['accesses'],physical(observed,value,fixture),
        'the RPM RAM withdrawal original changes ordered physical RAM/pool/configuration/stack address, width, register or byte effects')
    same(result['branches'],value['branches'],'the RPM RAM withdrawal original changes an independent natural conditional/jump/return outcome')
    same(result['code'],{site:fixture[site:site+2].hex() for site in value['path']},
        'the RPM RAM withdrawal original changes a complete expected natural instruction path or byte')
    if result['calls']:raise ValueError('the RPM RAM withdrawal original invents an outside call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the RPM RAM withdrawal original omits its complete natural instruction trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the RPM RAM withdrawal original changes a conditional, jump or RTS delay slot')
    if (trace[-1]['next']!=observed['continuation'] or trace[-1]['after']['registers'][15]!=observed['sp']
            or tuple(trace[-1]['after']['registers'][:15])!=value['registers']
            or trace[-1]['after']['gbr']!=observed['context'][15] or trace[-1]['after']['macl']!=observed['context'][17]):
        raise ValueError('the RPM RAM withdrawal original changes complete post-delay returned GPR/SP/GBR/MACL state')
    if any(site in result['code'] for site in INFEASIBLE_INSTRUCTIONS):
        raise ValueError('the RPM RAM withdrawal original leaves its independent byte/word product width premise')


def require_no_selected_datum(result,rows):
    identities=tuple((row['original_claim_sha256'],row['address'],
        RAM_BASE+(row['address']&65535)) for row in rows)
    if (not test_contract.exact(identities,NATIVE_RAM_ROOTS)
            or any(not row['owner'].endswith('/ram') or not 0xFFFF0000<=row['address']<=0xFFFFFFFF for row in rows)):
        raise ValueError('the RPM withdrawal substitutes a selected native RAM original or its exact simulator alias')
    for event in result['accesses']:
        if any(event['address']<=address<event['address']+event['width_bytes']
                for original,native,alias in NATIVE_RAM_ROOTS for address in (native,alias)):
            raise ValueError('the RPM withdrawal physically accesses a selected native RAM datum root or its simulator alias')
        if event['domain']=='rom' and event['site'] not in ROM:
            raise ValueError('the RPM withdrawal substitutes an undeclared ROM source for its exact pool or configuration operand')
