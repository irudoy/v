"""Exact knock datum transfers and real post-delay helper arguments."""

from kb import knock_access_matrix as matrix,knock_access_semantics as numeric,test_contract

WATCHED_ROM={0x49DA2,0x49E2A,0x49E4E,0x49EA0,0x49EA6,0x49EB2,0x49ECA,
    0x4A002,0x4A2F4,0x2650A,0x26510,0x26986,0x2699C,0x2699E}
REQUIRED_BRANCHES={
    'normalization':(0x4A27E,0x4A3C4,0x4A2B2,0x4A3F6,0x4A502,0x4A470,
        0x4A47A,0x4A44C,0x4A55C,0x4A574,0x21CF2),
    'metric':(0x4A2B8,0x49DB6,0x49DC6,0x49DEA,0x49DF6,0x49E30,
        0x49E40,0x49E48,0x49E52,0x49EC4,0x49ECE,0x49EE8),
    'threshold':(0x4A006,0x2698C,0x26990,0x26994,0x269B8,0x26742),
    'comparison':(0x4A006,0x2698C,0x26990,0x26994,0x269B8,0x26742,
        0x4A2F8,0x4A328,0x4A338,0x4A35E,0x4A376),
}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def evaluate(case,observed,result):
    before=observed['memory_before'][0];cal=observed['calibration_before']
    expected=numeric.expected(case,before,cal);kind=case['kind'];channel=expected['channel']
    alternate=bool(case['selector']&8);wanted=[];required=[]
    def access(site,mode,address,width,raw):wanted.append((site,mode,address,width,raw.hex()))
    def read(site,at,width=2,raw=None):
        access(site,'read',0xFFFF0000+at,width,before[at:at+width] if raw is None else raw)
    def write(site,at,width,value):access(site,'write',0xFFFF0000+at,width,(value&((1<<(width*8))-1)).to_bytes(width,'big'))
    def rom(site,at,width):access(site,'read',at,width,numeric.data(cal,at,width))
    def call(site,target,arguments):
        position=len(required);required.append((site,target))
        if position>=len(result['calls']):raise ValueError('a knock stage omits a real helper call')
        registers=result['calls'][position]['entry']['registers']
        if any(registers[index]!=value for index,value in arguments.items()):
            raise ValueError('a knock stage changes an actual post-delay helper argument')
    if kind=='normalization':
        read(0x4A3B6 if alternate else 0x4A270,0x2154,1)
        cache=0x20D2+16*(channel-1)
        if not expected['blocks']:
            for index in range(4):
                write(0x4A3E8 if alternate else 0x4A2A4,0x20C2+4*index,2,65535)
                write(0x4A3EA if alternate else 0x4A2A6,cache+4*index,2,65535)
                write(0x4A3EE if alternate else 0x4A2AA,0x20C4+4*index,2,65535)
                write(0x4A3F2 if alternate else 0x4A2AE,cache+2+4*index,2,65535)
        else:
            read(0x4A4FE,0x87E1,1)
            if expected['flag']:read(0x4A512,0x2152)
            else:read(0x4A52E,0x2143,1);read(0x4A53A,0x2152)
            for index,value in enumerate(expected['words']):
                if expected['flag']:
                    read(0x4A45A,0x2132+2*index)
                    call(0x4A466,0x21CE0,{0:32*expected['blocks'],1:expected['bins'][index]*expected['multiplier']})
                    write(0x4A47C,0x20C2+2*index,2,value)
                    read(0x4A488 if alternate else 0x4A43C,0x2143 if alternate else 0x11DE,1)
                    write(0x4A494 if alternate else 0x4A446,cache+2*index,2,value)
                else:
                    read(0x4A546,0x2132+2*index)
                    call(0x4A554,0x21CE0,{0:32*expected['blocks'],1:expected['bins'][index]*expected['multiplier']})
                    write(0x4A55E,0x20C2+2*index,2,value)
                    if not alternate:read(0x4A580,0x11DE,1)
                    write(0x4A56C if alternate else 0x4A58C,cache+2*index,2,value)
    elif kind=='metric':
        selected=4*(channel-1);total=expected['total'].to_bytes(4,'big')
        if case['scope']==0:
            read(0x4A4A2 if alternate else 0x4A2C4,0x2143 if alternate else 0x11DE,1)
            for index,value in enumerate(expected['differences']):
                read(0x4A4B2 if alternate else 0x4A2D4,0x20C2+2*index)
                read(0x4A4B8 if alternate else 0x4A2DA,0x2178+16*(channel-1)+2*index)
                write(0x4A4BE if alternate else 0x4A2E0,0x2158+4*index,4,value)
            call(0x4A2E6,0x49D88,{})
            rom(0x49DA2,0x8618,1)
            for index,value in enumerate(expected['differences']):
                call(0x49DB0,0x221BC,{0:1,1:index})
                if not expected['mask']&(1<<index):read(0x49E80,0x2158+4*index,4,(value&0xFFFFFFFF).to_bytes(4,'big'))
            rom(0x49E2A,0x8870,1);rom(0x49E4E,0x8B3D,1)
            read(0x49E5C if alternate else 0x49E88,0x2143 if alternate else 0x11DE,1)
            write(0x49E66 if alternate else 0x49E94,0x2274+selected,4,expected['total'])
            call(0x4A2EA,0x49E96,{})
        for site,at in ((0x49EA0,0x86A7),(0x49EA6,0x8694),(0x49EB2,0x86AC),(0x49ECA,0x8B3D)):
            rom(site,at,1)
        read(0x49F5E if alternate else 0x49ED4,0x2143 if alternate else 0x11DE,1)
        read(0x49EE4,0x2274+selected,4,total)
        read(0x49F68 if expected['total']&0x80000000 else 0x49EF2,0x2274+selected,4,total)
        read(0x49F1E,0x2274+selected,4,total)
        write(0x49F32,0x21F8+selected,4,expected['scaled'])
        read(0x49F3C,0x21F8+selected,4,expected['scaled'].to_bytes(4,'big'))
        write(0x49F4C,0x21D8+selected,4,expected['biased'])
    else:
        if kind=='comparison':call(0x4A2EE,0x49FFC,{})
        rom(0x4A002,0x8B3D,1)
        read(0x4A010 if alternate else 0x4A044,0x2143 if alternate else 0x11DE,1)
        read(0x4A024,0x11F4)
        call(0x4A02C,0x264F8,{4:expected['row'],5:0x15340,6:expected['coordinate']})
        call(0x26502,0x26984,{0:0x15340,4:30,5:expected['coordinate']})
        lower=expected['index']
        stop=lower if expected['coordinate']>=expected['axis'][0] else 0
        for index in range(15,stop-1,-1):rom(0x26986,0x15340+2*index,2)
        if expected['axis'][lower]<expected['coordinate'] and lower<15:
            rom(0x2699C,0x15340+2*lower,2);rom(0x2699E,0x15342+2*lower,2)
            call(0x269AA,0x26C78,{0:expected['axis'][lower+1]-expected['axis'][lower],
                1:(expected['coordinate']-expected['axis'][lower])*65536})
        rom(0x2650A,expected['row']+2*lower+2,2);rom(0x26510,expected['row']+2*lower,2)
        write(0x4A03A,0x2144+2*(channel-1),2,expected['threshold'])
        if not {0x26984,0x26740}<=set(result['code']):
            raise ValueError('a knock table or axis relation lacks its actual helper and unsigned tail closure')
        if kind=='comparison':
            exceeded=expected['exceeded'];rom(0x4A2F4,0x8B3D,1)
            read(0x4A40A if alternate else 0x4A300,0x2143 if alternate else 0x11DE,1)
            read(0x4A314,0x21D8+4*(channel-1),4)
            read(0x4A31A,0x2144+2*(channel-1),2,expected['threshold'].to_bytes(2,'big'))
            read(0x4A412 if exceeded else 0x4A32C,0x24C2,1)
            write(0x4A418 if exceeded else 0x4A330,0x24C2,1,expected['memory'][0x24C2])
            read(0x4A332,0x24C2,1,expected['memory'][0x24C2:0x24C3])
            call(0x4A420 if exceeded else 0x4A342,0x221BC,{0:1,1:channel-1})
            read(0x4A42C if exceeded else 0x4A34E,0x2150,1)
            write(0x4A436 if exceeded else 0x4A358,0x2150,1,expected['memory'][0x2150])
            if exceeded:
                read(0x4A368,0x2142,1);write(0x4A384,0x2142,1,expected['memory'][0x2142])
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('a knock stage actual RAM differs from separate scalar and complete footprint equations')
    actual=[]
    for row in result['accesses']:
        if row['domain']!='ram' and row['site'] not in WATCHED_ROM:continue
        address=row['address']
        if row['domain']=='ram':address=0xFFFF0000+address-matrix.RAM_BASE
        elif row['domain']!='rom':raise ValueError('a knock datum leaves its exact RAM/ROM domain')
        actual.append((row['site'],row['mode'],address,row['width_bytes'],row['bytes']))
    # Stable site grouping retains the order of repeated accesses at each site.
    same(sorted(actual,key=lambda row:row[0]),sorted(wanted,key=lambda row:row[0]),
        'a knock stage changes an exact datum/site/width/direction/value or repeated-site order')
    same([(row['site'],row['target']) for row in result['calls']],required,
        'a knock stage changes its exact real helper order or closure')
    return dict(index=case['index'],kind=kind,entry=case['entry'],output=expected['output'],
        accesses=actual,channel=channel,exact_knock_accesses=True,
        scalar={key:value for key,value in expected.items() if key!='memory'},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)
