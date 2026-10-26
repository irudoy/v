"""Independent full timer equations and actual raw-primary refusal boundaries."""
from copy import deepcopy
import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence,packed_transfer_evidence
from kb import byte_surface_equations as state
from kb import indexed_timer_refresh_writer_contract as contract
from kb import indexed_timer_refresh_writer_matrix as matrix
from kb import indexed_timer_refresh_writer_semantics as numeric
from kb import indexed_timer_refresh_writer_transfers as transfers
from kb import indexed_timer_refresh_writer_capture_evidence as proof


def reconstructed(**updates):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='independent-timer-refusal',**updates)
    context=matrix.context(source,case);memory=matrix.memory(case)
    fixture,_=contract.fixture_for_case(source,image,case);cal=matrix.calibrations(source,image,case)
    sp=0x30000000;continuation=0x30010000;sr=context[18]|0x08000400
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,sr,trace=True)
    value=numeric.evaluate(contract.ENTRY,memory,cal,context,sr,bytes(frame),sp,continuation)
    ordinary=bytearray(result['ram']);ordinary[0x8500:0x8600]=memory[0x8500:0x8600]
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    abi=(*packed_transfer_evidence.ABI,sp+164,0xABCD1234)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        memory_before=(memory,),memory_after=(bytes(ordinary),),native_before=memory[0x8500:0x8600],
        native_after=result['ram'][0x8500:0x8600],bound_before=bound,bound_after=bound,
        calibration_before=cal,calibration_after=cal,frame_before=bytes(frame),frame_after=result['frame'],
        sr_before=sr,abi_before=abi,abi_after=abi,
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,value,fixture)
    return observed,result,value,fixture


@pytest.mark.parametrize('reload',(0,1,127,128,255))
def test_exact43BE_reload_uses_signed_full_R6_and_real_BRA_delay(reload):
    observed,result,value,fixture=reconstructed(raw_r5=0,reload=reload)
    assert value['timer']==0x010043BE and value['mask']==7 and value['refreshed']
    assert observed['memory_after'][0][0x43BE]==reload
    carrier=next(row for row in result['trace'] if row['site']==0x9023E)
    assert carrier['delay_slot'] is True and carrier['before']['registers'][6]==(reload if reload<128 else reload-256)&0xFFFFFFFF
    assert next(row for row in result['accesses'] if row['site']==0x9023E)==dict(
        site=0x9023E,mode='write',address=0x010043BE,width_bytes=1,register=6,domain='ram',bytes=bytes([reload]).hex())
    assert int.from_bytes(observed['frame_after'][148:152],'big')==0xFFFFFFA0


@pytest.mark.parametrize('index',(0,1,6,254,255,0xFFFFFFFF))
def test_complete_index_addition_and_wrapped_timer_address(index):
    observed,result,value,fixture=reconstructed(raw_r4=index,raw_r5=0,reload=173)
    assert value['mask']==(index+1)&0xFFFFFFFF
    assert value['timer']==(0x010043B8+index)&0xFFFFFFFF
    assert observed['memory_after'][0][value['timer']-matrix.RAM_BASE]==173
    assert result['sp']==observed['sp'] and result['registers'][14]==observed['context'][14]


def test_mask_is_full_R4_plus_one_and_enabled_is_full_nonzero_R5():
    observed,result,value,fixture=reconstructed(raw_r4=6,raw_r5=0x10000,arm=0,other_arm=0,
        native_indicator=16,timer_006=0)
    assert value['enabled'] and value['mask']==7 and value['judged_set'] and not value['refreshed']
    assert observed['memory_after'][0][0x3581]==7
    assert observed['native_after'][12]==128 and observed['memory_after'][0][0x850C]==0


@pytest.mark.parametrize('initial_sr',[qm|interrupt|t for qm in (0,256,512,768) for interrupt in range(0,256,16) for t in (0,1)])
def test_critical_section_restores_full_SR_and_real_saved_R14_GBR(initial_sr):
    observed,result,value,fixture=reconstructed(initial_sr=initial_sr,arm=0,other_arm=0,native_reset=1)
    trace={row['site']:row for row in result['trace']}
    assert trace[0x901D0]['after']['sr']&240==240
    assert trace[0x901EE]['after']['sr']==trace[0x901BE]['before']['sr']
    assert observed['native_after'][12]==129
    assert result['gbr']==observed['context'][15] and result['registers'][14]==observed['context'][14]
    assert result['frame'][152:160]==observed['context'][15].to_bytes(4,'big')+observed['context'][14].to_bytes(4,'big')
    assert result['trace'][-1]['site']==0x9024E and result['trace'][-1]['next']==observed['continuation']


@pytest.mark.parametrize('fault',('ordinary-shadow','ordinary-other','native-indicator','native-canary','native-echo',
    'frame','SR','detached-SR','R14','GBR','operand-width','operand-source','operand-register','operand-byte',
    'full-carrier','critical-SR','temporary-word','delay','return','call','opcode','branch'))
def test_matching_timer_byte_cannot_replace_full_actual_state_and_physical_transitions(fault):
    observed,result,value,fixture=reconstructed(arm=0,other_arm=0,native_reset=1,raw_r5=0 if fault=='temporary-word' else 1)
    if fault in ('ordinary-shadow','ordinary-other'):
        raw=bytearray(observed['memory_after'][0]);raw[0x850C if fault=='ordinary-shadow' else 0x2222]^=128
        observed['memory_after']=(bytes(raw),)
    elif fault in ('native-indicator','native-canary','native-echo'):
        raw=bytearray(observed['native_after']);at={'native-indicator':13,'native-canary':255,'native-echo':12}[fault]
        raw[at]^=128;observed['native_after']=bytes(raw)
    elif fault=='frame':
        raw=bytearray(observed['frame_after']);raw[148]^=1;observed['frame_after']=bytes(raw)
    elif fault in ('SR','R14','GBR'):
        raw=list(observed['exit']);raw[{'SR':0,'R14':5,'GBR':4}[fault]]^=0x100;observed['exit']=tuple(raw)
    elif fault=='detached-SR':
        result['sr']^=0x100;observed['exit']=(result['sr'],*observed['exit'][1:])
    elif fault.startswith('operand-'):
        row=next(row for row in result['accesses'] if row['site']==0x901DE)
        key={'operand-width':'width_bytes','operand-source':'address','operand-register':'register','operand-byte':'bytes'}[fault]
        row[key]='00' if key=='bytes' else row[key]+1
    elif fault=='temporary-word':
        next(row for row in result['accesses'] if row['site']==0x90228)['address']+=4
    elif fault in ('full-carrier','critical-SR'):
        row=next(row for row in result['trace'] if row['site']==(0x901D0 if fault=='critical-SR' else 0x901DE))
        if fault=='critical-SR':row['after']['sr']^=16
        else:
            registers=list(row['before']['registers']);registers[0 if fault=='full-carrier' else 15]^=0x10000
            row['before']['registers']=tuple(registers)
    elif fault=='delay':result['trace'][-1]['delay_slot']=False
    elif fault=='return':result['trace'][-1]['next']+=2
    elif fault=='call':result['calls'].append(dict(site=0x9018C,target=0x264CC))
    elif fault=='opcode':result['trace'][0]['bytes']='0009'
    else:result['branches'].pop()
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def positive_pairs():
    pairs=[]
    for reload in (0,1,255):
        observed,result,value,fixture=reconstructed(raw_r5=0,reload=reload);pairs.append((observed,value))
    for reset in (0,1):
        observed,result,value,fixture=reconstructed(native_reset=reset);pairs.append((observed,value))
    return pairs


def test_actual_distinct_reload_and_native_OR80_hold_every_other_complete_input():
    assert proof.require_causal_alternatives(positive_pairs())==dict(exact_owner_refresh=True,actual_native_OR80=True)


@pytest.mark.parametrize('fault',('timer-echo','native-echo','missing-reload','missing-native','changed-other-CPU','changed-native-canary','same-native-value'))
def test_positive_writer_obligations_refuse_echoes_missing_or_unheld_alternatives(fault):
    pairs=positive_pairs()
    if fault=='timer-echo':
        raw=bytearray(pairs[0][0]['memory_after'][0]);raw[0x43BE]=37;pairs[0][0]['memory_after']=(bytes(raw),)
    elif fault=='native-echo':pairs[-1][0]['native_after']=pairs[-1][0]['native_before']
    elif fault=='missing-reload':pairs=pairs[3:]
    elif fault=='missing-native':pairs=pairs[:3]
    elif fault=='changed-other-CPU':
        for n,(observed,value) in enumerate(pairs[:3]):
            raw=list(observed['context']);raw[8]+=n;observed['context']=tuple(raw)
    elif fault=='changed-native-canary':
        raw=bytearray(pairs[-1][0]['native_before']);raw[255]^=1;pairs[-1][0]['native_before']=bytes(raw)
    else:pairs[-1]=deepcopy(pairs[-2])
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness'][proof.COMPONENT]
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the complete B acceptance requires the actual indexed timer writer original')
        pytest.skip('the complete indexed timer writer original is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert proof.require_owning_result(result) is True
    assert result['causal_inputs']==dict(exact_owner_refresh=True,actual_native_OR80=True)
    assert result['exact_indexed_timer_refresh_writer_paths'] is True and len(result['native_bindings'])==1
    return model,record,packet,result


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def restream(packet):
    rows=iter(packet['observations']);lines=[]
    for line in packet['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row=next(rows,None)
            if row is not None:lines.append(proof.PREFIX+json.dumps(row,separators=(',',':'))+'\n')
        else:lines.append(line)
    packet['stdout']=''.join(lines);packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()


@pytest.mark.parametrize('field',('schema','declaration','consumed','reconstruction','aliases','observations','simulator',
    'toolchain','command','marker','stdout_sha256','observer_object_sha256','boundaries','return_reconstruction'))
def test_actual_primary_requires_every_exact_raw_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','native-window','observer','header',
    'omit','duplicate','swap','entry','context-after','calibration-before','calibration-after','bound-before','bound-after',
    'native-before','native-after','outside-return','short-native','short-RAM','short-observer','bool-index','duplicate-key'))
def test_actual_complete_original_refuses_source_transport_and_native_substitutions(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'].pop()
    elif fault=='alias':packet['aliases'].append(dict(address=0,alias=4))
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='native-window':packet['simulator']['command'][2]='--memory-region=0xffff8400,256'
    elif fault=='observer':packet['consumed'][proof.OBSERVER]+='00'
    elif fault=='header':packet['consumed'][proof.HEADER]+='00'
    elif fault=='outside-return':packet['boundaries'].append(dict(address=0xC2000,bytes='000b0009'))
    elif fault=='duplicate-key':
        packet['stdout']=packet['stdout'].replace(proof.PREFIX+'{',proof.PREFIX+'{"schema":1,',1)
        packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    else:
        rows=packet['observations']
        if fault=='omit':rows.pop()
        elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
        elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
        elif fault=='entry':rows[0]['entry']+=2
        elif fault=='short-native':rows[0]['native_after']=rows[0]['native_after'][:-2]
        elif fault=='short-RAM':rows[0]['ram_before']='1:a5'
        elif fault=='short-observer':rows[0]['observation']=rows[0]['observation'][:-2]
        elif fault=='bool-index':rows[0]['index']=False
        else:
            field=fault.replace('-','_');raw=bytearray.fromhex(rows[0][field]);raw[0]^=1;rows[0][field]=raw.hex()
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',proof.SOURCE_FILES)
def test_actual_consumer_requires_each_complete_source_dependency(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)
