"""Separate existing coolant equations and exact selected-operand/call transfers."""

from pathlib import Path
import sys

from kb import closed_loop_coolant_matrix as matrix,test_contract
from kb.test_stock_capture import tool

WATCHED={0x5532A,0x5532C,0x26380,0x26AAC,0x26AAE,0x5539E,0x553AC,0x553CA,
    0x553E6,0x553EC,0x55402,0x5541C,0x55422,0x5543C,0x55442,0x5544C,0x5544E,
    0x5545C,0x5545E,0x55498}


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def numerical(root,case):
    directory=Path(root).resolve()/'tools/sh-elf-run';previous=list(sys.path)
    try:
        sys.path.insert(0,str(directory))
        library=tool(root,'stock_coolant_conditional_model.py','_kb_coolant_independent_numerical')
    finally:
        sys.path[:]=previous
    dependency=sys.modules.get(library.State.__module__)
    if dependency is None or Path(dependency.__file__).resolve()!=directory/'stock_injection_end_angle_model.py':
        raise ValueError('the coolant numerical equations import another declared local arithmetic library')
    inputs={name:case[name] for name in matrix.FIELDS}
    inputs.update({name:case[name] for name,size in matrix.ARRAYS})
    value=inputs['coolant_offset'];inputs['coolant_offset']=value-65536 if value&32768 else value
    return library.case(case['index'],**inputs)


def require(case,observed,result,root):
    value=numerical(root,case);before=observed['memory_before'][0];memory=bytearray(before)
    memory[0x2492]=value['updated_a'];memory[0x2493]=value['updated_b']
    memory[0x2485]=value['updated_direction'];memory[0x15DA:0x15DC]=value['output'].to_bytes(2,'big')
    if value['enabled']:memory[0x15DD]=value['lookup'];memory[0x15DC]=value['selected']
    same(observed['memory_after'],(bytes(memory),),'the coolant original disagrees with separate complete RAM and scalar equations')
    context=observed['context'];frame=bytearray(observed['frame_before'])
    for at,byte in value['frame_writes'].items():frame[at]=byte
    frame[136:140]=observed['continuation'].to_bytes(4,'big')
    same(observed['frame_after'],bytes(frame),'the coolant original disagrees with its separate complete nested-frame equations')
    same(context[:15],tuple(value['incoming']),'the coolant numerical model uses another complete incoming register context')
    wanted_sr=(observed['sr_before']&~0x301)|(value['expected_sr']&0x301)
    same(observed['exit'],(wanted_sr,observed['continuation'],context[17],context[16],context[15],
        *reversed(value['expected'])),'the coolant original disagrees with separate full terminal CPU/SR/PR/GBR/MACH/MACL equations')
    physical(case,observed,result,value)
    return dict(enabled=bool(value['enabled']),coordinate=value['coordinate'],lookup=value['lookup'],
        selected=value['selected'],output=value['output'],
        selected_index=(4*next((i for i in range(1,4) if case['rpm_select']<=case['rpm_axis'][i]),4)
            +next((i for i in range(1,4) if case['load']<=case['load_axis'][i]),4)-5) if value['enabled'] else None)


def physical(case,observed,result,value):
    rows=[];calibration=observed['calibration_before'];before=observed['memory_before'][0]
    def emit(site,mode,address,width,raw,domain):rows.append((site,mode,address,width,raw.hex(),domain))
    def rom(site,address,width):
        matches=[data[address-at:address-at+width] for at,data in calibration.items()
            if at<=address and address+width<=at+len(data)]
        if len(matches)!=1:raise ValueError('the coolant physical constant leaves its exact observed calibration span')
        emit(site,'read',address,width,matches[0],'rom')
    def ram(site,mode,offset,width,raw):emit(site,mode,matrix.RAM_BASE+offset,width,raw,'ram')
    calls=[];returns=[];sp=observed['sp']-52
    if value['enabled']:
        rom(0x5532A,0x5533C,2);ram(0x5532C,'read',0x106F,1,before[0x106F:0x1070])
        coordinate=value['coordinate'];table=calibration[0x12422]
        if coordinate>=224:
            rom(0x26380,0x12429,1);return_site=0x2637E
        else:
            index=coordinate//32;rom(0x26AAC,0x12422+index,1);rom(0x26AAE,0x12423+index,1)
            return_site=0x2676A if table[index+1]>=table[index] else 0x26758
        calls.append((0x55392,0x26370,0x55396,sp));returns.append((return_site,'return',0x55396))
        ram(0x5539E,'write',0x15DD,1,bytes([value['lookup']]))
        load_index=next((i for i in range(1,4) if case['load']<=case['load_axis'][i]),4)
        rpm_index=next((i for i in range(1,4) if case['rpm_select']<=case['rpm_axis'][i]),4)
        for index in range(1,min(3,load_index)+1):rom(0x553AC,0x11B1B+index,1)
        for index in range(1,min(3,rpm_index)+1):rom(0x553CA,0x11B17+index,1)
        selected=4*rpm_index+load_index-5
        if not 0<=selected<16 or value['selected']!=calibration[0x990A][selected]:
            raise ValueError('the coolant selected byte disagrees with the separate load/RPM bin index')
        rom(0x553E6,0x990A+selected,1);ram(0x553EC,'write',0x15DC,1,bytes([value['selected']]))
        difference=value['lookup']*value['selected']-case['old']
        if case['flags_a']&1:
            ram(0x55402,'read',0x15DA,2,before[0x15DA:0x15DC])
            ram(0x5541C,'write',0x2485,1,bytes([value['updated_direction']]))
            rom(0x55422,0x9090,2)
            if abs(difference)>case['rate']:
                positive=difference>=0
                ram(0x5543C if positive else 0x5544C,'read',0x15DA,2,before[0x15DA:0x15DC])
                rom(0x55442 if positive else 0x5544E,0x9090,2)
            calls.append((0x5541A,0x22590,0x5541E,sp));returns.append((0x22596,'return',0x5541E))
        rom(0x5545C,0x929A,2);ram(0x5545E,'read',0x22E8,2,before[0x22E8:0x22EA])
    ram(0x55498,'write',0x15DA,2,value['output'].to_bytes(2,'big'))
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes','domain'))
        for row in result['accesses'] if row['site'] in WATCHED]
    same(actual,rows,'the coolant original changes an exact ordered constant/index/curve/limiter/cap/publication transfer')
    same([tuple(row[key] for key in ('site','target','return_address','sp')) for row in result['calls']],calls,
        'the coolant original changes its real natural curve/absolute call closure or frame')
    for index,call in enumerate(result['calls']):
        entry=call['entry'];registers=entry['registers']
        same((entry['sp'],entry['pr'],entry['gbr']),(sp,call['return_address'],matrix.RAM_BASE+0x2458),
            'the coolant original changes actual post-delay SP/PR/GBR')
        if index==0:
            same((registers[2],registers[4],registers[5],registers[12]),
                (0x26370,0x12422,value['coordinate'],matrix.RAM_BASE+0x128C),
                'the coolant original changes the actual byte-curve arguments or EXTU.B delay slot')
        else:
            old=case['old'];signed_old=(old-65536 if old&32768 else old)&0xFFFFFFFF
            same((registers[0],registers[4],registers[5],registers[6],registers[12]),
                (value['updated_direction'],difference&0xFFFFFFFF,signed_old,difference&0xFFFFFFFF,matrix.RAM_BASE+0x128C),
                'the coolant original changes the complete signed difference or real flag-store call delay slot')
    returns.append((0x554AA,'return',observed['continuation']))
    same([(row['site'],row['kind'],row['target']) for row in result['branches'] if row['kind']=='return'],returns,
        'the coolant original changes an exact natural helper or root return')
    if any(row['kind']!='taken' for row in result['branches'] if row['site']==0x26A9A) \
            or any(0x26A9C<=pc<0x26AAA for pc in result['code']):
        raise ValueError('the coolant original enters a word-only path excluded by its exact byte-curve call')
