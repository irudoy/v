"""Independent exact CVTC physical widths, delayed arguments and natural returns."""

from kb import test_contract
from kb import exhaust_cvtc_contract as contract


def require_calls(observed,result,value):
    sp=observed['sp'];context=observed['context'];calls=[];returns=[]
    if value['entry']==0xC1DEC:
        curve=value['curve']
        if curve is not None:
            calls.extend(((0xC1ED4,0x26474,0xC1ED8,sp-40),
                (0x2647E,0x26944,0x26482,sp-48)))
            if curve['division'] is not None:
                calls.append((0x2696A,0x26C78,0x2696E,sp-52))
                returns.extend(((0x26D06,0x2696E),(0x26970,0x26482)))
            else:returns.append((0x2697C,0x26482))
            returns.append((0x2676A if curve['right']>=curve['left'] else 0x26758,0xC1ED8))
            if value['configuration']&8:
                calls.extend(((0xC1F24,0x21CE0,0xC1F28,sp-40),
                    (0xC1F46,0x21F40,0xC1F4A,sp-40),
                    (0xC1F56,0x21CE0,0xC1F5A,sp-40)))
                first,second=value['quotients']
                returns.extend(((0x21D08 if first[1]<first[2]*256 else 0x21D66,0xC1F28),
                    (0x21F6E if value['high']<625*256 else 0x21FCC,0xC1F4A),
                    (0x21D08 if second[1]<second[2]*256 else 0x21D66,0xC1F5A)))
        returns.append((0xC2000,observed['continuation']))
        expected_t=0
    else:
        calls.extend(((0xC2078,0x21CE0,0xC207C,sp-32),(0xC208A,0x21CE0,0xC208E,sp-32)))
        for site,dividend,divisor,quotient in value['quotients']:
            returns.append((0x21D08 if dividend<divisor*256 else 0x21D66,site+4))
        returns.append((0xC214E,observed['continuation']))
        expected_t=int(value['precap_output']>1024)
    actual=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    if not test_contract.exact(actual,calls):
        raise ValueError('the CVTC proof changes a complete natural call, target, continuation or stack phase')
    for row in result['calls']:
        site=row['site'];entered=row['entry'];registers=entered['registers']
        if (entered['sp'],entered['pr'],entered['gbr'],entered['mach'])!=(
                row['sp'],row['return_address'],context[15],context[16]):
            raise ValueError('the CVTC proof changes the real post-delay stack, PR, GBR or MACH')
        if site==0xC1ED4:
            wanted={2:0x26474,4:0x1205A,5:0x12850,6:value['curve']['coordinate'],14:1}
        elif site==0x2647E:
            wanted={0:0x12850,4:7,5:value['curve']['coordinate'],7:0x26944}
        elif site==0x2696A:
            dividend,divisor=value['curve']['division'];wanted={0:divisor,1:dividend,2:0x26C78}
        elif site==0xC1F46:
            wanted={0:625,1:value['high'],4:0x21F40}
        else:
            _,dividend,divisor,quotient=next(item for item in value['quotients'] if item[0]==site)
            wanted={0:divisor,1:dividend}
            wanted[7 if site in (0xC1F24,0xC1F56) else 6]=0x21CE0
            if site==0xC208A:wanted[13]=1024
        if any(registers[index]!=expected for index,expected in wanted.items()):
            raise ValueError('the CVTC proof changes a real call operand after its actual delay slot')
    actual=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(actual,returns):
        raise ValueError('the CVTC proof changes a real helper or root RTS and its continuation')
    if value['curve'] is not None:
        tail=[row for row in result['branches'] if row['site']==0x26492]
        if len(tail)!=1 or not test_contract.exact((tail[0]['kind'],tail[0]['target'],tail[0]['delay']),('jump',0x26740,True)):
            raise ValueError('the CVTC byte wrapper loses its real delayed interpolation tail')
    if ((observed['exit'][1],observed['exit'][2],observed['exit'][3],observed['exit'][4])!=
            (observed['continuation'],context[17],context[16],context[15])
            or observed['exit'][0]&1!=expected_t):
        raise ValueError('the CVTC proof changes independently restored PR/MACL/MACH/GBR or terminal comparison T')
    restored=range(12,15) if value['entry']==0xC1DEC else range(9,15)
    if any(observed['exit'][19-register]!=context[register] for register in restored):
        raise ValueError('the CVTC proof changes a naturally saved and restored root register')


def require(observed,result,value,fixture):
    pools=[];physical=[]
    for row in result['accesses']:
        if row['domain']=='frame':continue
        site=row['site'];word=int.from_bytes(fixture[site:site+2],'big')
        if word>>12 in (9,13):
            width=4 if word>>12==13 else 2
            at=((site&~3) if width==4 else site)+4+(word&255)*width
            expected=(site,'read',at,width,fixture[at:at+width].hex())
            if tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))!=expected:
                raise ValueError('the CVTC proof changes an executed PC-relative pool operand or byte width')
            pools.append(site)
        else:
            physical.append(tuple(row[key] for key in ('site','mode','address','width_bytes','bytes')))
    expected_pools=[]
    for site,raw in result['code'].items():
        if raw!=fixture[site:site+2].hex():raise ValueError('the CVTC trace substitutes a tested instruction byte')
        if int.from_bytes(fixture[site:site+2],'big')>>12 in (9,13):expected_pools.append(site)
    if sorted(pools)!=sorted(expected_pools):
        raise ValueError('the CVTC proof omits or repeats an executed literal-pool load')
    expected=[(site,mode,at,width,scalar.to_bytes(width,'big').hex())
        for site,mode,at,width,scalar in value['physical']]
    if not test_contract.exact(physical,expected):
        raise ValueError('the CVTC proof changes exact ordered physical byte/word/long inputs or writes')
    if observed['memory_after']!=(value['memory'],) or result['ram']!=value['memory']:
        raise ValueError('the CVTC proof changes separate complete scalar RAM or an untouched neighbor')
    offset,width=value['output_address'],value['output_width']
    if observed['memory_after'][0][offset:offset+width]!=value['output'].to_bytes(width,'big'):
        raise ValueError('the CVTC proof loses its exact independently calculated root publication')
    require_calls(observed,result,value)
