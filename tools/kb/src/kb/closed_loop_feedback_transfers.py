"""Exact independent whole-feedback carriers, active-state stores and transition counter."""

from kb import test_contract

ROOT=0x5CBEC
TARGET=0x5D6AE
CALL=0x5CEF8
RETURN=0x5CEFC
WORK_BASE=0x5FFC
WORK_LOGICAL=0x88B0
ARGUMENTS=((0xFFFF106E,0x5CEDA,1),(0xFFFF1071,0x5CEF2,1),(0xFFFF11BC,0x5CEE6,2))
STORES=((0xFFFF895C,0x5D846),(0xFFFF8960,0x5D84E))


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def signed(value,bits):
    return (value-(1<<bits) if value&(1<<(bits-1)) else value)&0xFFFFFFFF


def require(observed,result,trace):
    access=result['accesses'];before=observed['memory_before'][0]
    calls=[row for row in result['calls'] if row['target']==TARGET]
    if len(calls)!=1:raise ValueError('the feedback proof omits or repeats its one real active-state call')
    call=calls[0];sp=observed['sp']-160
    same(tuple(call[key] for key in ('site','target','return_address','sp')),(CALL,TARGET,RETURN,sp),
        'the feedback proof changes its exact active-state call, continuation or caller frame')
    entry=call['entry'];registers=entry['registers']
    if (entry['sp'],entry['pr'],entry['gbr'])!=(sp,RETURN,WORK_BASE):
        raise ValueError('the feedback proof changes the actual active-state post-delay SP/PR/GBR')
    phase_before=trace['active_state']['before'];phase_after=trace['active_state']['after']
    control=int(bool(before[0x4184]&64))
    rpm=int.from_bytes(before[0x11BC:0x11BE],'big')
    if ((registers[4],registers[5],registers[6],registers[7],registers[9])!=
            (control,signed(before[0x1071],8),WORK_BASE+0x87,signed(rpm,16),0x010040B0)):
        raise ValueError('the feedback proof changes the full real R4/R5/R6/R7/R9 post-delay arguments')
    same(trace['active_state']['args'],(control,before[0x1071],
        [phase_before[0x8937],phase_before[0x8938]],rpm,before[0x106E]),
        'the feedback proof changes the separate effective scalar arguments or current bank byte phase')
    source_reads=[]
    for address,site,width in ARGUMENTS:
        rows=[row for row in access if row['site']==site and row['mode']=='read']
        wanted=dict(site=site,mode='read',address=0x01000000+(address&65535),
            width_bytes=width,bytes=before[address&65535:(address&65535)+width].hex(),domain='ram')
        if len(rows)!=1:raise ValueError('the feedback proof omits or repeats an exact physical caller source read')
        same({key:rows[0][key] for key in wanted},wanted,
            'the feedback proof changes a physical caller input, width, direction or value')
        source_reads.append(rows[0])
    source_store=[row for row in access if row['site']==0x5CEE0 and row['mode']=='write']
    if len(source_store)!=1:raise ValueError('the feedback proof omits the actual partial fifth-argument store')
    same(tuple(source_store[0][key] for key in ('address','width_bytes','bytes','domain')),
        (sp+3,1,bytes([before[0x106E]]).hex(),'frame'),
        'the feedback proof changes the partial byte store carrying the fifth argument')
    fifth=[row for row in access if row['site']==0x5D6D2 and row['mode']=='read']
    if (len(fifth)!=1 or (fifth[0]['address'],fifth[0]['width_bytes'],fifth[0]['domain'])!=(sp,4,'frame')
            or int(fifth[0]['bytes'],16)&255!=before[0x106E]):
        raise ValueError('the feedback proof changes the real fifth-word load or its effective low byte')
    pointer=WORK_BASE+0xAC
    for site,mode in ((0x5CEF4,'write'),(0x5D844,'read')):
        rows=[row for row in access if row['site']==site and row['mode']==mode]
        if len(rows)!=1:raise ValueError('the feedback proof omits an exact sixth output-pointer carrier')
        same(tuple(rows[0][key] for key in ('address','width_bytes','bytes','domain')),
            (sp+4,4,pointer.to_bytes(4,'big').hex(),'frame'),
            'the feedback proof changes its actual complete sixth-argument output pointer')
    outputs={}
    for address,site in STORES:
        rows=[row for row in access if row['site']==site and row['mode']=='write']
        if len(rows)!=1:raise ValueError('the feedback proof omits or repeats a real active-state four-byte store')
        offset=address&65535;data=phase_after[offset:offset+4]
        same(tuple(rows[0][key] for key in ('address','width_bytes','bytes','domain')),
            (WORK_BASE+offset-WORK_LOGICAL,4,data.hex(),'feedback-workspace'),
            'the feedback proof changes the exact output datum, store width, phase or value')
        outputs[address]=data
    returns=[row for row in result['branches'] if row['site']==0x5D868]
    if len(returns)!=1 or (returns[0]['kind'],returns[0]['target'])!=('return',RETURN):
        raise ValueError('the feedback proof changes the real active-state natural return and delay slot')
    ordered=[]
    for site,mode in ((0x5CEDA,'read'),(0x5CEE0,'write'),(0x5CEE6,'read'),(0x5CEF2,'read'),
            (0x5CEF4,'write'),(0x5D6D2,'read'),(0x5D844,'read'),(0x5D846,'write'),(0x5D84E,'write')):
        positions=[index for index,row in enumerate(access) if row['site']==site and row['mode']==mode]
        if len(positions)!=1:raise ValueError('the feedback proof omits or duplicates a required ordered carrier/store')
        ordered.append(positions[0])
    if ordered!=sorted(ordered):raise ValueError('the feedback proof reorders an exact physical argument carrier or output store')
    return dict(arguments={address:before[address&65535:(address&65535)+width]
        for address,site,width in ARGUMENTS},stores=outputs,
        scalar_before=phase_before,scalar_after=phase_after,call=call,
        fifth_word=int(fifth[0]['bytes'],16),sixth_pointer=pointer)


def require_transition(observed,result,trace,fixture):
    before,after=trace['transition']['before'],trace['transition']['after']
    word=lambda data,at:int.from_bytes(data[at:at+2],'big')
    count=word(before,0x88BA);flag=before[0x88C1]
    control=before[0x89D8];factor=before[0x89D9];coefficient=fixture[0x8822]
    trigger=bool(control==0 and before[0x88CD]!=0
        or word(before,0x89CE)==0x4000 and word(before,0x88B4)>0x4000
        or word(before,0x89CC)==0 and word(before,0x88B6)!=0)
    active=flag==1 or trigger
    threshold=(factor*coefficient)&65535
    nominal,observed_word=word(before,0x89D2),word(before,0x89D6)
    lower=(nominal-word(fixture,0x92EE))&65535;upper=(nominal+word(fixture,0x92F0))&65535
    inside=lower<=observed_word<=upper
    increment=active and count<=threshold and not inside
    expected_count=count+1 if increment else 0
    expected_flag=(1 if flag==0 else flag) if increment else 0
    if expected_count>65535 or (word(after,0x88BA),after[0x88C1])!=(expected_count,expected_flag):
        raise ValueError('the transition counter disagrees with separate byte-product/band/unsigned-counter/flag equations')
    rows=[]
    def emit(site,mode,address,width,value):
        rows.append((site,mode,address,width,value.to_bytes(width,'big').hex(),'feedback-workspace'))
    counter=0x6006;flag_at=0x600D
    emit(0x5CAD4,'read',flag_at,1,flag)
    if active:
        emit(0x5CB12,'read',flag_at,1,flag)
        if flag==0:emit(0x5CB1E,'write',flag_at,1,1)
        emit(0x5CB30,'read',counter,2,count)
        if increment:
            emit(0x5CB7A,'read',counter,2,count);emit(0x5CB9C,'read',counter,2,count)
            emit(0x5CBAA,'write',counter,2,expected_count)
        else:
            emit(0x5CBB4,'write',flag_at,1,0);emit(0x5CBBC,'write',counter,2,0)
    else:
        emit(0x5CBB4,'write',flag_at,1,0);emit(0x5CBBC,'write',counter,2,0)
    sites={0x5CAD4,0x5CB12,0x5CB1E,0x5CB30,0x5CB7A,0x5CB9C,0x5CBAA,0x5CBB4,0x5CBBC}
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes','domain'))
        for row in result['accesses'] if row['site'] in sites and row['address'] in (counter,flag_at)]
    same(actual,rows,'the software-bank-2 counter proof changes an exact ordered read, store, flag, width, value or phase')
    calls=[row for row in result['calls'] if row['target'] in (0x5D66C,0x5CA8C)]
    sp=observed['sp']
    same([tuple(row[key] for key in ('site','target','return_address','sp')) for row in calls],
        [(0x5CC4C,0x5D66C,0x5CC50,sp-160),(0x5D696,0x5CA8C,0x5D69A,sp-168)],
        'the transition counter proof changes its exact real packet/callee call sequence or nested frame')
    for index,call in enumerate(calls):
        entry=call['entry'];wanted_gbr=WORK_BASE if index==0 else 0x6118
        if (entry['sp'],entry['pr'],entry['gbr'])!=(sp-160-8*index,call['return_address'],wanted_gbr):
            raise ValueError('the transition counter proof changes an exact packet/callee post-delay SP/PR/GBR')
        registers=entry['registers']
        wanted=(signed(before[0x14C1],8),factor,signed(word(before,0x89CC),16),signed(word(before,0x89CE),16))
        same(tuple(registers[register] for register in (4,5,6,7)),wanted,
            'the transition counter proof changes a real complete packet scalar argument')
        if index==1 and (registers[0],registers[3])!=(signed(observed_word,16),0x010029E2):
            raise ValueError('the transition counter proof changes its final observed-word load or source pointer')
    for store,load,offset,pointer in ((0x5CC2C,0x5D684,0,0x010028B8),
            (0x5CC36,0x5D68E,4,0x010029E2),(0x5CC42,0x5D69C,8,0x60A4)):
        for site,mode in ((store,'write'),(load,'read')):
            carrier=[row for row in result['accesses'] if row['site']==site and row['mode']==mode]
            if len(carrier)!=1:raise ValueError('the transition counter proof omits a real complete packet pointer carrier')
            same(tuple(carrier[0][key] for key in ('address','width_bytes','bytes','domain')),
                (sp-160+offset,4,pointer.to_bytes(4,'big').hex(),'frame'),
                'the transition counter proof changes an actual nominal/observed/output packet pointer')
    delay=[row for row in result['accesses'] if row['site']==0x5D698 and row['mode']=='write']
    if len(delay)!=1:raise ValueError('the transition counter proof omits the actual packet delay-slot word store')
    same(tuple(delay[0][key] for key in ('address','width_bytes','bytes','domain')),
        (0x6122,2,before[0x89D6:0x89D8].hex(),'feedback-workspace'),
        'the transition counter proof changes the final observed-bank word in the real call delay slot')
    output=[row for row in result['accesses'] if row['site']==0x5D6A4 and row['mode']=='write']
    if len(output)!=1:raise ValueError('the transition counter proof omits its software-bank-2 output flag')
    same(tuple(output[0][key] for key in ('address','width_bytes','bytes','domain')),
        (0x60A5,1,bytes([expected_flag]).hex(),'feedback-workspace'),
        'the transition counter proof changes its phase-correct bank-2 packet output flag')
    ordered=[(0x5CC2C,'write',sp-160),(0x5CC36,'write',sp-156),(0x5CC42,'write',sp-152),
        (0x5D684,'read',sp-160),(0x5D68E,'read',sp-156),(0x5D698,'write',0x6122),
        *((site,mode,address) for site,mode,address,width,data,domain in rows),
        (0x5D69C,'read',sp-152),(0x5D6A4,'write',0x60A5)]
    positions=[]
    for key in ordered:
        matches=[index for index,row in enumerate(result['accesses'])
            if tuple(row[field] for field in ('site','mode','address'))==key]
        if len(matches)!=1:raise ValueError('the transition proof omits or repeats a complete ordered packet/counter carrier')
        positions.append(matches[0])
    if positions!=sorted(positions):raise ValueError('the transition proof reorders the real packet delay, counter phase or output flag')
    returns=[(row['site'],row['kind'],row['target']) for row in result['branches'] if row['site'] in (0x5CBE4,0x5D6AA)]
    same(returns,[(0x5CBE4,'return',0x5D69A),(0x5D6AA,'return',0x5CC50)],
        'the transition counter proof changes a natural callee or packet return')
    guard=[row['kind'] for row in result['branches'] if row['site']==0x5CB84]
    if any(kind!='taken' for kind in guard) or any(0x5CB86<=pc<0x5CB92 for pc in result['code']):
        raise ValueError('the transition proof enters the saturation branch excluded by the preceding byte-product threshold')
    return dict(transition_before=before,transition_after=after,transition_count_before=count,
        transition_count_after=expected_count,transition_flag_before=flag,transition_flag_after=expected_flag,
        transition_threshold=threshold,transition_active=active,transition_inside_band=inside,
        transition_increment=increment,transition_guard_observed=bool(guard))
