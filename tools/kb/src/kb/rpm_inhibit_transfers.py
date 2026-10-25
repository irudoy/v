"""Exact independent physical order and real caller/leaf return boundaries."""

from kb import rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import test_contract

MASK=0xFFFFFFFF


def physical(before,calibration,value,fixture):
    memory=bytearray(before);rows=[]
    def emit(site,mode,address,width,data=None):
        if matrix.RAM_BASE<=address and address+width<=matrix.RAM_BASE+matrix.RAM_SIZE:
            offset=address-matrix.RAM_BASE
            if mode=='write':
                raw=(data&((1<<(8*width))-1)).to_bytes(width,'big');memory[offset:offset+width]=raw
            else:raw=bytes(memory[offset:offset+width])
        else:
            if mode!='read' or not 0<=address<=len(fixture)-width:
                raise ValueError('the RPM contributor transfer changes an exact memory domain')
            raw=fixture[address:address+width]
        rows.append((site,mode,address,width,raw.hex()))
    def read(site,address,width):emit(site,'read',address,width)
    def write(site,address,width,data):emit(site,'write',address,width,data)
    def ram_read(site,offset,width=1):read(site,matrix.RAM_BASE+offset,width)
    def ram_write(site,offset,data,width=1):write(site,matrix.RAM_BASE+offset,width,data)

    path=value.get('path','contributors')
    if path=='composite-status':
        read(0x4EDEA,0x4EF8C,4)
        read(0x507D8,0x508FC,4);read(0x507DE,0x50900,4);ram_read(0x507E2,0x41EA)
        read(0x507E8,0x50904,4);read(0x259E4,0x25B98,4)
        read(0x507F8,0x50904,4);read(0x259E4,0x25B98,4)
        read(0x5083E,0x5090C,4);ram_read(0x50842,0x11B3);ram_read(0x50844,0x2489)
        site=0x5085A if value['low_active'] else 0x50858
        ram_read(site,0x2489);ram_write(site,0x2489,value['memory'][0x2489])
        ram_read(0x5085C,0x245D)
        if before[0x245D]&64:
            ram_read(0x50862,0x2458)
            if before[0x2458]&32:ram_read(0x50868,0x2489)
        read(0x50872,0x508EC,4);ram_read(0x50878,0x110E)
        read(0x50886,0x50910,4);read(0x50888,0x50914,4);read(0x26370,0x26382,2)
        if value['coordinate']>=224:read(0x26380,0x12A39,1)
        else:
            read(0x26378,0x26384,4)
            first,second=value['curve']['offsets']
            read(0x26AAC,0x12A32+first,1);read(0x26AAE,0x12A32+second,1)
            read(0x26AB4,0x26ABC,4)
        read(0x50890,0x50918,4);read(0x50892,0x508E6,2)
        ram_write(0x50896,0x17CA,value['threshold'],2)
        ram_read(0x5089A,0x11BC,2);ram_read(0x5089C,0x249F)
        if before[0x249F]&4:read(0x508A4,0x5091C,4);read(0x508A6,0x9462,2)
        read(0x508AC,0x50918,4);read(0x508AE,0x508E6,2);ram_read(0x508B0,0x17CA,2)
        site=0x508BE if value['high_active'] else 0x508BC
        ram_read(site,0x249F);ram_write(site,0x249F,value['memory'][0x249F])
        ram_read(0x508C0,0x24CE)
        if not before[0x24CE]&4:ram_read(0x508C6,0x24D2)
        if before[0x24CE]&4 or before[0x24D2]&1:ram_read(0x508CC,0x249F)
        if bytes(memory)!=value['memory']:
            raise ValueError('the composite physical transfers disagree with separate complete-memory latch/curve equations')
        return rows,bytes(memory)
    if path!='contributors':
        if path=='maf-summary':
            read(0x4F736,0x4F910,4);ram_read(0x4F738,0x2448)
            if before[0x2448]&128:
                read(0x4F73E,0x4F914,4);ram_read(0x4F742,0x11B2)
        elif path=='shared-status':
            read(0x4FAA0,0x4FB9C,4);ram_read(0x4FAA2,0x418C)
        else:raise ValueError('the summary physical consumer changes its exact bounded path')
        if bytes(memory)!=value['memory']:
            raise ValueError('the summary physical transfers change complete RAM')
        return rows,bytes(memory)

    first=value['vehicle'];state=before[0x24A6];control=before[0x24A7]
    read(0x4F19E,0x4F1FC,4);ram_read(0x4F1A2,0x24A6);ram_read(0x4F1A8,0x24A7)
    if first['entry_active']:
        if control&32:ram_write(0x4F1BC,0x24A6,state&254)
        read(0x4F1BE,0x4F224,4);read(0x4F1C2,0x4F23C,4)
        ram_read(0x4F1C4,0x110E);read(0x4F1C6,0x8DC3,1)
        if first['speed']<first['off']:
            ram_write(0x4F1D0,0x24A7,control&127)
            ram_read(0x4F1D6,0x24A6);ram_write(0x4F1D6,0x24A6,memory[0x24A6]&254)
    else:
        read(0x4F240,0x4F454,4);read(0x4F244,0x4F458,4)
        ram_read(0x4F246,0x110E);read(0x4F248,0x8DB7,1)
        if first['speed']>=first['on']:
            if not control&128:
                read(0x4F254,0x4F45C,4);read(0x4F256,0x8CAF,1)
                ram_write(0x4F258,0x24F6,calibration[0x8CAF][0])
                ram_write(0x4F25E,0x24A7,control|128)
            ram_read(0x4F260,0x24F6)
            if memory[0x24F6]==0:
                ram_read(0x4F266,0x24A7)
                if not memory[0x24A7]&32:ram_write(0x4F272,0x24A6,state|1)
        else:ram_write(0x4F278,0x24A7,control&127)
    ram_read(0x4F27A,0x24A6)
    if bytes(memory)!=first['memory']:
        raise ValueError('the vehicle physical transfers disagree with its separate complete-memory equations')

    second=value['main'];incoming=bytes(memory);flags=incoming[0x2497]
    read(0x4F284,0x4F460,4);ram_read(0x4F288,0x2497)
    read(0x4F28A,0x4F464,4);read(0x4F28E,0x8B38,1)
    if second['config']&128:
        ram_read(0x4F29E,0x2499)
        if incoming[0x2499]&2:
            ram_read(0x4F2A4,0x2494)
            if incoming[0x2494]&32:ram_read(0x4F2AA,0x244F)
        if second['pair']!=2:ram_read(0x4F2BA,0x2468)
    else:ram_read(0x4F294,0x2468)
    if second['pair']==0:
        read(0x4F2CA,0x4F468,4);read(0x4F2CC,0x934E,2);read(0x4F2CE,0x9352,2)
    elif second['pair']==1:
        read(0x4F2C0,0x4F468,4);read(0x4F2C2,0x9350,2);read(0x4F2C8,0x9354,2)
    else:
        read(0x4F2B0,0x4F468,4);read(0x4F2B2,0x9356,2);read(0x4F2B8,0x9358,2)
    read(0x4F2D2,0x4F46C,4);ram_read(0x4F2DE,0x11BC,2)
    if second['entry_active']:
        if second['rpm']<second['off']:ram_write(0x4F314,0x2497,flags&249)
    elif second['rpm']>=second['on']:
        if not flags&2:
            read(0x4F2F8,0x4F470,4);read(0x4F2FA,0x8C69,1)
            ram_write(0x4F2FC,0x24F1,calibration[0x8C69][0]);ram_write(0x4F302,0x2497,flags|2)
        ram_read(0x4F304,0x24F1)
        if memory[0x24F1]==0:
            ram_read(0x4F30E,0x2497);ram_write(0x4F30E,0x2497,memory[0x2497]|4)
    else:ram_write(0x4F314,0x2497,flags&253)
    ram_read(0x4F316,0x2497)
    if bytes(memory)!=value['memory']:
        raise ValueError('the RPM physical transfers disagree with separate composed complete-memory equations')
    return rows,bytes(memory)


def require_calls(observed,result,value):
    if value.get('path')=='composite-status':
        require_composite_calls(observed,result,value)
        return
    if value.get('path','contributors')!='contributors':
        require_summary_calls(observed,result,value)
        return
    sp=observed['sp'];wanted=[(0x4EDBE,0x4F19C,0x4EDC2,sp),(0x4EDC2,0x4F282,0x4EDC6,sp)]
    actual=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    if not test_contract.exact(actual,wanted):
        raise ValueError('the RPM contributor proof changes an exact real caller, callee or call frame')
    for index,row in enumerate(result['calls']):
        entry=row['entry'];registers=entry['registers']
        r0=value['prior'] if index==0 else value['vehicle']['output']
        r14=value['prior'] if index==0 else value['output'][1]
        if ((entry['sp'],entry['pr'],entry['gbr'])!=(sp,row['return_address'],contract.INCOMING_GBR)
                or (registers[0],registers[14])!=(r0,r14)):
            raise ValueError('the RPM contributor proof changes the actual MOV/OR delay-slot R0/R14 or caller premises')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(returns,[(0x4F27E,0x4EDC2),(0x4F320,0x4EDC6),(0x4EDCA,observed['continuation'])]):
        raise ValueError('the RPM contributor proof changes a natural leaf or outside observing return')
    exit=observed['exit'];context=observed['context']
    if ((exit[19],exit[5])!=value['output']
            or (exit[1],exit[12],exit[2],exit[3],exit[4])!=(observed['continuation'],observed['continuation'],
                context[17],context[16],contract.INCOMING_GBR)):
        raise ValueError('the RPM contributor proof changes its independent output pair or complete restored terminal')


def require_summary_calls(observed,result,value):
    if value['path']=='maf-summary':call,target,continuation,return_site=0x4EDD2,0x4F736,0x4EDD6,0x4F754
    elif value['path']=='shared-status':call,target,continuation,return_site=0x4EDF8,0x4FAA0,0x4EDFC,0x4FAA8
    else:raise ValueError('the summary call consumer changes its exact path')
    calls=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    if not test_contract.exact(calls,[(call,target,continuation,observed['sp'])]):
        raise ValueError('the summary proof changes its real caller, target, return or SP')
    entry=result['calls'][0]['entry'];registers=entry['registers']
    if ((entry['sp'],entry['pr'],entry['gbr'])!=(observed['sp'],continuation,contract.INCOMING_GBR)
            or (registers[0],registers[2],registers[14])!=(value['incoming_r0'],value['incoming_r2'],value['output'][1])):
        raise ValueError('the summary proof changes its exact post-delay R0/R2/R14 or caller premises')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(returns,[(return_site,continuation),(continuation+4,observed['continuation'])]):
        raise ValueError('the summary proof changes its natural or outside observing return')
    exit=observed['exit'];context=observed['context']
    if ((exit[19],exit[5])!=value['output']
            or (exit[1],exit[12],exit[2],exit[3],exit[4])!=(observed['continuation'],observed['continuation'],
                context[17],context[16],contract.INCOMING_GBR)):
        raise ValueError('the summary proof changes its independent output pair or restored terminal')


def require(observed,result,value,fixture):
    rows,memory=physical(observed['memory_before'][0],observed['calibration_before'],value,fixture)
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain']!='frame']
    if not test_contract.exact(actual,rows) or observed['memory_after']!=(memory,):
        raise ValueError('the RPM contributor proof changes an ordered physical site, value, width, direction or complete RAM')
    require_calls(observed,result,value)
    return value


def require_composite_calls(observed,result,value):
    sp=observed['sp'];inner=sp-24
    calls=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    wanted=[(0x4EDEC,0x507CE,0x4EDF0,sp),(0x507F0,0x259E4,0x507F4,inner),
        (0x507FA,0x259E4,0x507FE,inner),(0x5088A,0x26370,0x5088E,inner)]
    if not test_contract.exact(calls,wanted):
        raise ValueError('the composite proof changes its exact real call closure, returns or nested frame')
    for index,row in enumerate(result['calls']):
        entry=row['entry'];registers=entry['registers']
        if (entry['sp'],entry['pr'],entry['gbr'])!=(wanted[index][3],wanted[index][2],
                contract.INCOMING_GBR if index==0 else matrix.RAM_BASE+0x2458):
            raise ValueError('the composite proof changes a real post-delay SP, PR or GBR premise')
        if index==0:
            expected=(value['incoming_r0'],value['incoming_r2'],0x507CE,value['output'][1])
            if (registers[0],registers[2],registers[3],registers[14])!=expected:
                raise ValueError('the composite proof changes caller MOV.L or full OR R2/R14 delay-slot words')
        elif index in (1,2):
            if ((registers[0],registers[4],registers[7],registers[14])!=
                    (value['seed'] if index==1 else 0,MASK,value['seed'],matrix.RAM_BASE+0x41A9)):
                raise ValueError('the composite proof changes either exact sentinel argument, seed store or real helper premise')
        elif ((registers[0],registers[2],registers[4],registers[5],registers[6],registers[7],registers[12],registers[13],registers[14])!=
                (0x7A,0x26370,0x12A32,value['coordinate'],value['coordinate']//4,
                 int(bool(value['seed'] or value['low_output'])),matrix.RAM_BASE+0x119C,
                 value['low_coordinate'],matrix.RAM_BASE+0x41A9)):
            raise ValueError('the composite proof changes the real byte-curve post-delay coordinate, table or retained frame inputs')
    if value['coordinate']>=224:curve_return=0x2637E
    else:
        first,second=value['curve']['offsets'];table=observed['calibration_before'][0x12A32]
        curve_return=0x2676A if table[second]>=table[first] else 0x26758
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(returns,[(0x25A0E,0x507F4),(0x25A0E,0x507FE),
            (curve_return,0x5088E),(0x508E2,0x4EDF0),(0x4EDF4,observed['continuation'])]):
        raise ValueError('the composite proof changes a natural sentinel/curve/root or outside observing return')
    exit=observed['exit'];context=observed['context']
    if ((exit[19],exit[5])!=value['output']
            or (exit[1],exit[12],exit[2],exit[3],exit[4])!=(observed['continuation'],observed['continuation'],
                context[17],context[16],contract.INCOMING_GBR)
            or (exit[6],exit[7])!=(context[13],context[12])):
        raise ValueError('the composite proof changes its independent output pair, saved registers or complete restored terminal')
