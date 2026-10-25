"""Independent ordered physical operands and natural delayed call/return boundaries."""

from kb import test_contract
from kb import rpm_remaining_inhibit_contract as contract

RAM=0x01000000
MASK=0xFFFFFFFF


def physical(before,value,fixture):
    memory=bytearray(before);rows=[]
    def read(site,address,width=4):
        data=(memory[address-RAM:address-RAM+width] if RAM<=address<=RAM+65536-width
            else fixture[address:address+width])
        if len(data)!=width:raise ValueError('a remaining RPM physical read leaves its exact domain')
        rows.append((site,'read',address,width,bytes(data).hex()))
    def rr(site,offset,width=1):read(site,RAM+offset,width)
    def ww(site,offset,data,width=1):
        raw=(data&((1<<(8*width))-1)).to_bytes(width,'big');memory[offset:offset+width]=raw
        rows.append((site,'write',RAM+offset,width,raw.hex()))

    if value['entry']==0x4EDC6:
        first=value['stationary'];active=first['active'];flags=before[0x247F]
        read(0x4F32A,0x4F460);rr(0x4F330,0x247F);read(0x4F332,0x4F454);rr(0x4F338,0x110E)
        if before[0x110E]==0:
            rr(0x4F33E,0x244F)
            if before[0x244F]&4:rr(0x4F344,0x2458)
        if active:
            if not flags&8:
                read(0x4F350,0x4F474);ww(0x4F356,0x258A,100);flags|=8;ww(0x4F360,0x247F,flags)
            else:
                read(0x4F362,0x4F474);rr(0x4F366,0x258A)
                if before[0x258A]==0:
                    read(0x4F36C,0x4F46C);read(0x4F36E,0x4F378,2);rr(0x4F370,0x11BC,2)
                    read(0x4F394,0x4F478);read(0x4F396,0x4F47C);read(0x26388,0x2639A,2)
                    curve=first['curve']
                    if curve['upper']:read(0x26398,0x124E1,1)
                    else:
                        read(0x26390,0x2639C)
                        read(0x26AAC,0x124D2+curve['index'],1);read(0x26AAE,0x124D3+curve['index'],1)
                        read(0x26AB4,0x26ABC)
                    read(0x4F39E,0x4F480);read(0x4F3A0,0x4F450,2)
                    rr(0x4F3A4,0x16A6,2);rr(0x4F3A6,0x247F)
                    read(0x4F3C0,0x4F480);read(0x4F3C4,0x4F450,2);read(0x4F3C6,0x4F474)
                    ww(0x4F3C8,0x16A6,int.from_bytes(first['memory'][0x16A6:0x16A8],'big'),2)
                    ww(0x4F3CC,0x258A,100)
            read(0x4F3CE,0x4F480);read(0x4F3D0,0x4F450,2);rr(0x4F3D2,0x16A6,2)
            read(0x4F3D4,0x4F484);read(0x4F3D6,0x911C,2)
            ready=int.from_bytes(memory[0x16A6:0x16A8],'big')>=int.from_bytes(fixture[0x911C:0x911E],'big')
            if ready:
                read(0x4F3DC,0x4F488);read(0x4F3DE,0x4F48C);rr(0x4F3E0,0x1071);read(0x4F3E2,0x8D0E,1)
                if before[0x1071]<fixture[0x8D0E]:rr(0x4F3E8,0x245D)
                ready=before[0x1071]>=fixture[0x8D0E] or bool(before[0x245D]&64)
            flags=(flags|16) if ready else (flags&239);ww(0x4F3F8,0x247F,flags)
            if flags&32:
                read(0x4F402,0x4F46C);rr(0x4F406,0x11AE);read(0x4F408,0x4F490);read(0x4F40A,0x85DA,1)
                if before[0x11AE]<fixture[0x85DA]:ww(0x4F43A,0x247F,flags&199)
            elif flags&16:
                read(0x4F41A,0x4F46C);rr(0x4F41E,0x11AE);read(0x4F420,0x4F490);read(0x4F422,0x85D9,1)
                if before[0x11AE]>=fixture[0x85D9]:ww(0x4F43A,0x247F,flags|32)
        else:
            read(0x4F42E,0x4F480);read(0x4F432,0x4F450,2);ww(0x4F434,0x16A6,0,2)
            ww(0x4F43A,0x247F,flags&199)
        rr(0x4F43C,0x247F)
        if bytes(memory)!=first['memory']:raise ValueError('the stationary physical trace changes separate complete scalar RAM')

        second=value['thermal'];thermal_flags=memory[0x41F2]
        read(0x4F4A2,0x4F6BC);read(0x4F4A8,0x4F6C0);read(0x4F4AA,0x186C9,1)
        if second['enabled']:
            rr(0x4F4B6,0x4184);rr(0x4F4C0,0x41F2);read(0x4F51A,0x4F6C8)
            ww(0x4F522,0x4397,10);ww(0x4F52A,0x4396,50);rr(0x4F52C,0x41F2)
            if thermal_flags&8:
                read(0x4F53C,0x4F6CC);rr(0x4F53E,0x5720)
                if not memory[0x5720]&16:
                    thermal_flags&=247;ww(0x4F548,0x41F2,thermal_flags)
                    read(0x4F54C,0x4F6C8);ww(0x4F552,0x4370,10);rr(0x4F554,0x41F2)
            read(0x4F558,0x4F6D0);rr(0x4F55A,0x1071);rr(0x4F55E,0x4209)
            read(0x4F566,0x4F6D4);read(0x4F568,0x8D15,1)
            site=0x4F578 if second['memory'][0x4209]&1 else 0x4F576
            rr(site,0x4209);ww(site,0x4209,second['memory'][0x4209])
            read(0x4F5AA,0x4F6C8);ww(0x4F5B2,0x4370,10)
            read(0x4F5B4,0x4F6CC);rr(0x4F5B6,0x5720)
            if memory[0x5720]&16:rr(0x4F5BC,0x571E)
            thermal_flags&=239;ww(0x4F5E4,0x41F2,thermal_flags)
            read(0x4F5FA,0x4F6DC);rr(0x4F5FE,0x11B3);rr(0x4F600,0x41F2);rr(0x4F604,0x41EE)
            if memory[0x41EE]&8:read(0x4F60C,0x4F6E0);read(0x4F60E,0x8957,1)
            read(0x4F614,0x4F6E4);read(0x4F616,0x88ED,1)
            site=0x4F624 if second['memory'][0x41EE]&8 else 0x4F622
            rr(site,0x41EE);ww(site,0x41EE,second['memory'][0x41EE])
            if thermal_flags&8:
                read(0x4F62C,0x4F6E8);rr(0x4F62E,0x2458)
                if not memory[0x2458]&32:rr(0x4F634,0x41EE)
            ww(0x4F644,0x41F2,second['flags'])
        rr(0x4F646,0x41F2)
    elif value['entry']==0x4EDE4:
        item=value['sustained'];read(0x4F95C,0x4FB70);read(0x4F960,0x4FB74);read(0x4F962,0x8B3F,1)
        clear=not item['enabled']
        if item['enabled']:
            read(0x4F968,0x4FB78);read(0x4F96C,0x4FB7C);read(0x4F970,0x90E0,2);read(0x4F972,0x84DE,1)
            read(0x4F984,0x4FB80);read(0x4F986,0x4FA9C,2);rr(0x4F98A,0x1932,2)
            clear=item['exposure']<item['threshold']
            if not clear:
                read(0x4F992,0x4FB84);rr(0x4F996,0x11B3);read(0x4F998,0x84DD,1)
                clear=before[0x11B3]<fixture[0x84DD]
                if not clear:
                    read(0x4F9A2,0x84DA,1)
                    if before[0x11B3]>=fixture[0x84DA]:rr(0x4F9AE,0x247C);ww(0x4F9AE,0x247C,item['flags'])
        if clear:rr(0x4F9B2,0x247C);ww(0x4F9B2,0x247C,item['flags'])
        rr(0x4F9B4,0x247C)
    elif value['entry']==0x4EE00:
        item=value['ceiling'];read(0x4EE00,0x4EF94);read(0x50A62,0x50B24);rr(0x50A66,0x249C)
        read(0x50A68,0x50B28);read(0x50A6C,0x8B3F,1)
        if item['enabled']:
            read(0x50A72,0x50B2C);rr(0x50A78,0x2714);rr(0x50A7C,0x2488)
            valid=before[0x2714]!=255
            if valid:
                read(0x50A88,0x50B30);rr(0x50A8A,0x4189);valid=not before[0x4189]&2
            if valid:
                read(0x50A90,0x50B34);rr(0x50A92,0x4250);valid=not before[0x4250]&128
            if valid:rr(0x50A9C,0x2714);valid=before[0x2714]!=0
            ww(0x50AA6 if valid else 0x50AC2,0x2488,item['memory'][0x2488])
            if valid:rr(0x50AAC,0x2714);read(0x50AAE,0x50B38);read(0x50AB2,0x89FD,1)
            read(0x50AC6,0x50B20);read(0x50AC8,0x50B06,2);ww(0x50ACA,0x31F6,item['target'])
            read(0x50ACE,0x50B14);rr(0x50AD0,0x11AE)
            if before[0x249C]&128:read(0x50ADA,0x50B38);read(0x50ADC,0x89FC,1)
            site=0x50AF0 if item['flags']&128 else 0x50AEC
            rr(site,0x249C);ww(site,0x249C,item['flags'])
        else:ww(0x50AF6,0x249C,item['flags'])
        rr(0x50AF8,0x249C)
    else:raise ValueError('the remaining RPM physical trace changes its exact entry phase')
    if bytes(memory)!=value['memory']:raise ValueError('the remaining RPM physical trace changes separate complete scalar RAM')
    return rows


def require_calls(observed,result,value):
    sp=observed['sp'];context=observed['context'];entry=value['entry'];calls=[];returns=[]
    if entry==0x4EDC6:
        calls=[(0x4EDC6,0x4F324,0x4EDCA,sp)]
        curve=value['stationary']['curve']
        if curve is not None:
            calls.append((0x4F398,0x26388,0x4F39C,sp-16))
            data=observed['calibration_before'][0x124D2]
            site=(0x26396 if curve['upper'] else
                0x2676A if data[curve['index']]<=data[curve['index']+1] else 0x26758)
            returns.append((site,0x4F39C))
        calls.append((0x4EDCA,0x4F494,0x4EDCE,sp));returns.extend(((0x4F44C,0x4EDCA),(0x4F65E,0x4EDCE)))
        boundary=0x4EDCE
    elif entry==0x4EDE4:
        calls=[(0x4EDE4,0x4F958,0x4EDE8,sp)];returns=[(0x4F9C0,0x4EDE8)];boundary=0x4EDEA
        if observed['exit'][17]!=value['r2']:raise ValueError('the sustained caller loses its actual EXTU.B result in R2')
    elif entry==0x4EE00:
        calls=[(0x4EE02,0x50A60,0x4EE06,sp)];returns=[(0x50B02,0x4EE06)];boundary=0x4EE06
    else:raise ValueError('the remaining RPM call proof changes its exact entry')
    actual=[tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']]
    if not test_contract.exact(actual,calls):raise ValueError('the remaining RPM proof changes a real target, delayed call, continuation or SP')
    for row in result['calls']:
        entered=row['entry'];registers=entered['registers'];site=row['site']
        expected_gbr=RAM+0x244C if site==0x4F398 else contract.INCOMING_GBR
        if (entered['sp'],entered['pr'],entered['gbr'])!=(row['sp'],row['return_address'],expected_gbr):
            raise ValueError('the remaining RPM proof changes complete post-delay call frame or GBR')
        if site==0x4F398:
            if (registers[4],registers[5],registers[2])!=(0x124D2,value['stationary']['curve']['coordinate'],0x26388):
                raise ValueError('the stationary curve changes actual table, byte argument or real target')
        else:
            r0=value['stationary']['output'] if site==0x4EDCA else context[0]
            r14=context[14]|context[0]|(value['stationary']['output'] if site==0x4EDCA else 0)
            if (registers[0],registers[14])!=(r0,r14):raise ValueError('the remaining RPM proof changes actual caller OR/NOP delay operands')
            if site==0x4EE02 and registers[3]!=0x50A60:
                raise ValueError('the CAN ceiling caller changes its actual loaded natural target')
    returns.append((boundary+4,observed['continuation']))
    actual=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if not test_contract.exact(actual,returns):raise ValueError('the remaining RPM proof changes natural RTS paths or the separate outside return')
    if ((observed['exit'][19],observed['exit'][5])!=value['output']
            or (observed['exit'][1],observed['exit'][12],observed['exit'][2],observed['exit'][3],observed['exit'][4])!=
                (observed['continuation'],observed['continuation'],context[17],context[16],contract.INCOMING_GBR)):
        raise ValueError('the remaining RPM proof changes independent terminal outputs, return, special registers or restored GBR')


def require(observed,result,value,fixture):
    expected=physical(observed['memory_before'][0],value,fixture)
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain']!='frame']
    if not test_contract.exact(actual,expected):raise ValueError('the remaining RPM proof changes ordered exact physical reads, writes or bytes')
    if observed['memory_after']!=(value['memory'],):raise ValueError('the remaining RPM proof changes separate complete scalar RAM')
    require_calls(observed,result,value)
