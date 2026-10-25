"""Exact natural GBR, unsigned quotients, curve operands and complete accumulator state."""
from kb import test_contract
from kb import maf_accumulator_update_contract as contract

RAM_BASE = 0x01000000
MASK = 0xFFFFFFFF
EXACT_SITES = {at for first,last in contract.SPANS for at in range(first,last,2)}
FEASIBLE_SITES = EXACT_SITES - set(contract.DECLARED['caller_scoped_infeasible_sites'])
FIXED_BRANCHES = {int(site):outcome for site,outcome in contract.DECLARED['caller_scoped_fixed_branches'].items()}
RAM_READS = {
    0x3AA3C:(0x3A1F,1,2),0x3AA46:(0x421A,1,4),0x3AA4A:(0x1075,1,0),0x3AA5C:(0x101E,2,6),
    0x3AA70:(0x3969,1,2),0x3AA7C:(0x3977,1,0),0x3AAAC:(0x3977,1,0),0x3AAB8:(0x421A,1,4),
    0x3AAC2:(0x101E,2,6),0x3AAD0:(0x1188,1,6),0x3AAE4:(0x396B,1,6),0x3AAF0:(0x3978,1,0),
    0x3AB20:(0x3978,1,0),0x3AB28:(0x398C,1,0),0x3AB36:(0x398B,1,2),0x3ABA2:(0x398B,1,2),
    0x3ABBC:(0x3997,1,0),0x3ABFC:(0x421A,1,2),0x3AC04:(0x3977,1,0),0x3AC12:(0x3978,1,0),
    0x3AC20:(0x1188,1,2),0x3AC3E:(0x3980,4,6),0x3AC62:(0x3989,1,2),0x3AC82:(0x3980,4,1),
    0x3ACB8:(0x397A,1,6),0x3ACD2:(0x3992,1,0),0x3ACDA:(0x3978,1,0),0x3ACE8:(0x3989,1,6),
    0x3AD10:(0x3992,1,0),0x3AD1C:(0x398B,1,0),0x3AD22:(0x3977,1,0),0x3AD3C:(0x3992,1,0),
    0x3AD44:(0x3977,1,0),0x3AD56:(0x3990,2,6),0x3AD70:(0x39A0,1,0),0x3AD92:(0x3977,1,0),
    0x3ADA4:(0x3A1F,1,6),0x3ADB6:(0x439B,1,6),0x3ADC6:(0x3992,1,0),0x3ADCE:(0x399C,4,4),
    0x3ADD8:(0x39A1,1,0),0x3ADFE:(0x3994,1,6),0x3AE1C:(0x39A1,1,0)}
STORE_REGISTERS = {0x3AA6C:0,0x3AA86:0,0x3AA9C:4,0x3AAA6:0,0x3AAAA:6,0x3AAE0:0,
    0x3AAFA:0,0x3AB1E:6,0x3AB54:6,0x3AB5A:0,0x3ABBA:6,0x3ABEE:2,0x3ABFA:0,
    0x3AC58:6,0x3ACB0:6,0x3ACD0:2,0x3AD0E:4,0x3AD38:5,0x3AD42:0,0x3AD6E:2,
    0x3AD8A:6,0x3AD90:0,0x3AE1A:4,0x3AE24:0,0x3AE74:6}
ROM_READS = {0x3AA40:(0x829F,1,0),0x3AA4E:(0x82A0,1,0),0x3AA60:(0x8F8A,2,2),
    0x3AA72:(0x829E,1,6),0x3AAC6:(0x8F8C,2,2),0x3AAD2:(0x82A1,1,0),
    0x3AAE6:(0x829E,1,2),0x3AB38:(0x829E,1,6),0x3ABC8:(0x8A4E,1,0),
    0x3ABCA:(0x8D75,1,2),0x3ABD6:(0x8A4C,1,6),0x3AC24:(0x8D75,1,6),
    0x3AC64:(0x8A4C,1,6),0x3ACEC:(0x8A4C,1,5),0x3AD80:(0x95B6,2,2),
    0x3ADA6:(0x829F,1,0),0x3ADE6:(0x9410,2,6),0x3AE5A:(0x9410,2,5)}
CALL_TARGETS = {0x3AC86:0x21CE0,0x3AC90:0x21CE0,0x3ACC0:0x26474,
    0x3AD5E:0x26474,0x2647E:0x26944,0x2696A:0x26C78}


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def event(site,mode,address,width,register,domain,raw):
    return dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())


def curve_reads(calibration,value):
    rows=[]
    for axis_at,values_at,curve in ((0x11BC3,0x12D82,value['mean_curve']),
                                     (0x11BBB,0x12C4A,value['factor_curve'])):
        if curve is None:continue
        axis=calibration[axis_at];table=calibration[values_at]
        for index in range(7,curve['index']-1,-1):
            rows.append(event(0x26946,'read',axis_at+index,1,1,'rom',axis[index:index+1]))
        if curve['fraction']:
            index=curve['index']
            rows.extend((event(0x2695C,'read',axis_at+index,1,1,'rom',axis[index:index+1]),
                         event(0x2695E,'read',axis_at+index+1,1,0,'rom',axis[index+1:index+2])))
        index=curve['index']
        rows.extend((event(0x26486,'read',values_at+index+1,1,0,'rom',table[index+1:index+2]),
                     event(0x2648C,'read',values_at+index,1,1,'rom',table[index:index+1])))
    return rows


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
         'the MAF accumulator changes complete independently reconstructed exit CPU/SR')
    if (observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)
            or observed['memory_after']!=(value['memory'],)):
        raise ValueError('the MAF accumulator changes complete frame, independent publications or unrelated RAM')
    if (result['sp']!=observed['sp'] or result['pr']!=observed['continuation']
            or (result['gbr'],result['mach'],result['macl'])!=observed['context'][15:18]
            or tuple(result['registers'][8:15])!=observed['context'][8:15]):
        raise ValueError('the MAF accumulator changes retained CPU or natural return')
    trace=result.get('trace')
    if type(trace) is not list or not trace or trace[0]['site']!=contract.ENTRY:
        raise ValueError('the MAF accumulator lacks its complete natural entry trace')
    initial=trace[0]['before']
    same(tuple(initial[key] for key in ('registers','gbr','mach','macl','sr','pr')),
         ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
         'the MAF accumulator detaches complete initial CPU from immutable inputs')
    for index,row in enumerate(trace):
        destination=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        old_gbr=0x3AA12<=row['site']<=0x3AA24 or 0x3AE7A<=row['site']<=0x3AE88
        gbr=observed['context'][15] if old_gbr else RAM_BASE+0x3968
        if (row['site'] not in FEASIBLE_SITES or row['next']!=destination
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')
                or row['bytes']!=fixture[row['site']:row['site']+2].hex() or row['before']['gbr']!=gbr):
            raise ValueError('the MAF accumulator changes exact instruction bytes, natural GBR or continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the MAF accumulator detaches intermediate CPU state')
    same(result['code'],{r['site']:fixture[r['site']:r['site']+2].hex() for r in trace},
         'the MAF accumulator changes exact executed instruction identities')
    if {r['site'] for r in trace if r['delay_slot']}!={r['site']+2 for r in result['branches'] if r['delay']}:
        raise ValueError('the MAF accumulator omits or invents a real delay slot')
    for branch in result['branches']:
        if branch['site'] in FIXED_BRANCHES and branch['kind']!=FIXED_BRANCHES[branch['site']]:
            raise ValueError('the MAF accumulator reaches an impossible wrapped-word or guarded-divisor path')
    memory=bytearray(observed['memory_before'][0]);writes=[];curve_operands=[]
    for operand in result['accesses']:
        site=operand['site']
        if operand['domain']=='ram':
            if operand['mode']=='read':
                if site not in RAM_READS:raise ValueError('the MAF accumulator invents a native RAM read')
                at,width,register=RAM_READS[site]
                same(operand,event(site,'read',RAM_BASE+at,width,register,'ram',memory[at:at+width]),
                     'the MAF accumulator changes an actual indexed RAM read or its complete physical bytes')
            else:
                position=len(writes)
                if position>=len(value['publications']):raise ValueError('the MAF accumulator adds an unrelated RAM write')
                expected=value['publications'][position];at=expected['address'];width=expected['size']
                raw=expected['value'].to_bytes(width,'big')
                same(operand,event(expected['site'],'write',RAM_BASE+at,width,STORE_REGISTERS[expected['site']],'ram',raw),
                     'the MAF accumulator changes ordered independent native publications')
                memory[at:at+width]=raw;writes.append(operand)
        elif operand['domain']=='rom':
            if site in contract.LITERAL_OPERANDS:
                at,width,register=contract.LITERAL_OPERANDS[site]
                same(operand,event(site,'read',at,width,register,'rom',fixture[at:at+width]),
                     'the MAF accumulator changes an exact PC-relative literal operand')
            elif site in ROM_READS:
                at,width,register=ROM_READS[site]
                same(operand,event(site,'read',at,width,register,'rom',fixture[at:at+width]),
                     'the MAF accumulator changes an actual raw ROM control, width or register')
            elif site in (0x26946,0x2695C,0x2695E,0x26486,0x2648C):curve_operands.append(operand)
            else:raise ValueError('the MAF accumulator introduces an unrelated ROM operand')
        elif operand['domain']!='frame':raise ValueError('the MAF accumulator introduces another native storage domain')
    if len(writes)!=len(value['publications']) or bytes(memory)!=value['memory']:
        raise ValueError('the MAF accumulator omits a real independent RAM publication')
    same(curve_operands,curve_reads(observed['calibration_before'],value),
         'the MAF accumulator changes ordered exact physical curve/axis reads or the ninth guard byte')
    local_base=observed['sp']-56
    expected_locals=[(0x3AA38,'write',3,1,1)]
    local_sites={8:0x3AA82,12:0x3AAF6,16:0x3AD3E,20:0x3AE1E}
    for row in value['local_writes']:
        number=row['value'];number=number if number<128 else number-256
        expected_locals.append((local_sites[row['offset']],'write',row['offset'],4,number&MASK))
    if value['divisor']:expected_locals.append((0x3ACA8,'read',3,1,1))
    expected_locals.append((0x3ACC6,'read',3,1,1))
    if value['factor_curve'] is not None:expected_locals.append((0x3AD64,'read',3,1,1))
    if value['decayed'] is not None:
        expected_locals.extend(((0x3ADD2,'write',4,4,value['old']),
            (0x3ADEC if value['branch']=='decay-and-scale-once' else 0x3AE60,'read',4,4,value['old'])))
    expected_locals.sort(key=lambda row:row[0])
    actual_locals=[(r['site'],r['mode'],r['address']-local_base,r['width_bytes'],int(r['bytes'],16))
        for r in result['accesses'] if r['domain']=='frame' and local_base<=r['address']
        and r['address']+r['width_bytes']<=local_base+24]
    same(actual_locals,expected_locals,'the MAF accumulator changes actual local byte/long operands or signed frame values')
    expected_calls=[]
    if value['divisor']:expected_calls.extend((0x3AC86,0x3AC90))
    expected_calls.extend((0x3ACC0,0x2647E))
    if value['mean_curve']['fraction']:expected_calls.append(0x2696A)
    if value['factor_curve'] is not None:
        expected_calls.extend((0x3AD5E,0x2647E))
        if value['factor_curve']['fraction']:expected_calls.append(0x2696A)
    same([c['site'] for c in result['calls']],expected_calls,'the MAF accumulator changes complete nested helper call order')
    cursor=0;curve_number=-1
    for call in result['calls']:
        site=call['site'];target=CALL_TARGETS[site]
        stack_delta=56 if site>=0x3AA12 else 64 if site==0x2647E else 68
        if call['target']!=target or call['return_address']!=site+4 or call['sp']!=observed['sp']-stack_delta:
            raise ValueError('the MAF accumulator changes a real helper target, nested SP or continuation')
        first=next((i+2 for i in range(cursor,len(trace)-2) if trace[i]['site']==site),None)
        if first is None or trace[first]['site']!=target:raise ValueError('the MAF accumulator replaces a real post-delay entry')
        cursor=first;before=trace[first]['before']
        same(tuple(call['entry'][key] for key in ('registers','sp','gbr','mach','macl','sr','pr')),
             (tuple(before['registers'][:15]),before['registers'][15],before['gbr'],before['mach'],before['macl'],before['sr'],before['pr']),
             'the MAF accumulator detaches complete real post-delay operands')
        terminal=next((i for i in range(first,len(trace)-1) if any(b['kind']=='return' for b in trace[i]['branches'])
            and trace[i+1]['next']==site+4),None)
        if terminal is None:raise ValueError('the MAF accumulator omits a complete natural helper return')
        returned=trace[terminal+1]['after'];registers=call['entry']['registers']
        if returned['registers'][15]!=call['sp'] or returned['pr']!=site+4:
            raise ValueError('the MAF accumulator changes natural helper return SP/PR')
        if site in (0x3AC86,0x3AC90):
            divisor=value['divisor'] if site==0x3AC86 else 1000
            dividend=next(r['value'] for r in value['publications'] if r['address']==0x3980) if site==0x3AC86 and any(r['address']==0x3980 for r in value['publications']) else integer_sum(observed) if site==0x3AC86 else value['first_quotient']
            quotient=value['first_quotient'] if site==0x3AC86 else value['second_quotient']
            if registers[:2]!=(divisor,dividend) or returned['registers'][0]!=quotient:
                raise ValueError('the MAF accumulator substitutes a live unsigned divisor, dividend or quotient')
        elif target==0x26474:
            curve_number+=1;axis_at,values_at,coordinate=(0x11BC3,0x12D82,value['mean']) if curve_number==0 else (0x11BBB,0x12C4A,int.from_bytes(value['memory'][0x3990:0x3992],'big')>>8)
            if registers[4:7]!=(values_at,axis_at,coordinate):raise ValueError('the MAF accumulator changes a real byte-curve argument')
            curve=value['mean_curve'] if curve_number==0 else value['factor_curve']
            if returned['registers'][0]!=curve['value']:raise ValueError('the MAF accumulator changes an independent byte-curve result')
        elif target==0x26944:
            axis_at=0x11BC3 if curve_number==0 else 0x11BBB
            curve=value['mean_curve'] if curve_number==0 else value['factor_curve']
            if registers[0]!=axis_at or registers[4]!=7 or returned['registers'][4:6]!=(curve['index'],curve['fraction']):
                raise ValueError('the MAF accumulator changes a complete physical axis result')
        else:
            curve=value['mean_curve'] if curve_number==0 else value['factor_curve']
            axis_at=0x11BC3 if curve_number==0 else 0x11BBB
            axis=observed['calibration_before'][axis_at];coordinate=value['mean'] if curve_number==0 else int.from_bytes(value['memory'][0x3990:0x3992],'big')>>8
            divisor=axis[curve['index']+1]-axis[curve['index']]
            numerator=(coordinate-axis[curve['index']])<<16
            if registers[:2]!=(divisor,numerator) or returned['registers'][0]!=curve['fraction']:
                raise ValueError('the MAF accumulator substitutes actual fraction operands or quotient')
    final=[r for r in trace if r['site'] in (0x3AD8A,0x3AE1A,0x3AE74)]
    if len(final)!=1 or final[0]['before']['registers'][STORE_REGISTERS[final[0]['site']]]!=value['value']:
        raise ValueError('the MAF accumulator substitutes matching bytes for its complete live uint32 store')


def integer_sum(observed):
    return int.from_bytes(observed['memory_before'][0][0x3980:0x3984],'big')
