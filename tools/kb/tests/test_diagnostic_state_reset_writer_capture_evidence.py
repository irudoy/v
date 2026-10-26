"""Complete reset CPU/call/native effects and actual raw-primary refusal boundaries."""
from copy import deepcopy
import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence,packed_transfer_evidence
from kb import byte_surface_equations as state
from kb import diagnostic_state_reset_writer_contract as contract,diagnostic_state_reset_writer_matrix as matrix
from kb import diagnostic_state_reset_writer_semantics as numeric,diagnostic_state_reset_writer_transfers as transfers
from kb import diagnostic_state_reset_writer_capture_evidence as proof


def reconstructed(**updates):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='independent-reset-refusal',**updates)
    context=matrix.context(source,case);memory=matrix.memory(case)
    fixture,_=contract.fixture_for_case(source,image,case);cal=matrix.calibrations(source,image,case)
    sp=0x30000000;continuation=0x30010000;sr=context[18]|0x08000400
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,sr,trace=True)
    value=numeric.evaluate(contract.ENTRY,memory,cal,context,sr,bytes(frame),sp,continuation)
    bound=b''.join(fixture[row['address']:row['address']+row['size']] for row in contract.BOUND_SPANS)
    abi=(*packed_transfer_evidence.ABI,sp+164,0xABCD1234)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        memory_before=(memory,),memory_after=(matrix.physical_ordinary(result['ram'],memory),),
        native_before=matrix.native_bytes(memory),native_after=matrix.native_bytes(result['ram']),
        bound_before=bound,bound_after=bound,calibration_before=cal,calibration_after=cal,
        frame_before=bytes(frame),frame_after=result['frame'],sr_before=sr,abi_before=abi,abi_after=abi,
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    assert transfers.require(observed,result,value,fixture) is True
    return observed,result,value,fixture


@pytest.mark.parametrize('gate',(0,64))
@pytest.mark.parametrize('prior',(0,1,127,128,255))
def test_real_constant_zero_store_keeps_its_full_R14_loop_address_and_ordinary_shadow(gate,prior):
    observed,result,value,fixture=reconstructed(byte_41e1=gate,prior_99de=prior)
    at=proof.native_offset(0xFFFF99DE)
    assert observed['native_before'][at]==prior and observed['native_after'][at]==0
    assert observed['memory_after'][0][0x99DE]==prior
    writes=[row for row in result['accesses'] if row['site']==0x2E84A]
    assert len(writes)==24 and writes[2]==dict(site=0x2E84A,mode='write',address=0xFFFF99DE,width_bytes=1,register=14,domain='native-io',bytes='00')
    assert result['calls'][1]['registers'][4]==2 and result['calls'][1]['entry']['registers'][4]==0xA5
    assert result['gbr']==observed['context'][15] and result['macl']==observed['context'][17]
    assert result['registers'][14]==observed['context'][14] and result['sp']==observed['sp']
    assert result['sr']&~1==observed['sr_before']&~1 and result['sr']&1==int(not gate)


@pytest.mark.parametrize('raw',(0,1,127,128,255))
def test_conditional_unsigned_ROM_products_keep_full_signed_load_and_MACL_restore(raw):
    observed,result,value,fixture=reconstructed(byte_41e1=64,raw_rom_8dfc=raw,raw_rom_8dfd=255-raw)
    for address,wanted in ((0xFFFFF588,raw*125),(0xFFFFF58A,raw*125),
            (0xFFFFF58C,(255-raw)*125),(0xFFFFF58E,(255-raw)*125),
            (0xFFFFF590,0),(0xFFFFF592,0),(0xFFFFF594,0),(0xFFFFF596,0)):
        at=proof.native_offset(address);assert observed['native_after'][at:at+2]==wanted.to_bytes(2,'big')
    load=next(row for row in result['trace'] if row['site']==0xCD806)
    assert load['after']['registers'][2]==(raw if raw<128 else raw-256)&0xFFFFFFFF
    multiply=next(row for row in result['trace'] if row['site']==0xCD80A)
    assert multiply['after']['macl']==raw*125
    assert result['macl']==observed['context'][17]


def test_all_real_loops_and_every_feasible_instruction_require_complete_gate_paths():
    first=reconstructed(byte_41e1=0)[1];second=reconstructed(byte_41e1=64)[1]
    assert set(first['code'])|set(second['code'])==transfers.FEASIBLE_SITES
    for site in transfers.CONDITIONAL_SITES:
        assert {row['kind'] for result in (first,second) for row in result['branches'] if row['site']==site}=={'taken','fallthrough'}
    observed,result,value,fixture=reconstructed(byte_41de=255,byte_41b9=255,byte_41ba=255,byte_41e1=255,native_9a6b=255)
    for address,wanted in ((0x41DE,0xFA),(0x41B9,7),(0x41BA,0x6F),(0x41E1,0x9F)):
        assert observed['memory_after'][0][address]==wanted
    assert observed['native_after'][proof.native_offset(0xFFFF9A6B)]==63


@pytest.mark.parametrize('fault',('target-echo','ordinary-shadow','native-canary','ordinary-other','native-product','frame','exit-SR','detached-SR',
    'exit-R14','MACL','intermediate-MACL','signed-ROM-carrier','pre-delay-R4','post-delay-argument','call-PR','call-SP',
    'skip-store','store-width','store-address','store-register','full-zero-carrier','attached-operand','return','delay','opcode','literal-as-code'))
def test_matching_final_zero_cannot_replace_complete_state_calls_and_physical_operands(fault):
    observed,result,value,fixture=reconstructed(byte_41e1=64,prior_99de=7)
    if fault in ('target-echo','native-canary','native-product'):
        raw=bytearray(observed['native_after']);at=proof.native_offset(0xFFFF99DE if fault=='target-echo' else 0xFFFF9900 if fault=='native-canary' else 0xFFFFF588)
        raw[at]^=1;observed['native_after']=bytes(raw)
    elif fault in ('ordinary-shadow','ordinary-other'):
        raw=bytearray(observed['memory_after'][0]);raw[0x99DE if fault=='ordinary-shadow' else 0x2222]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='frame':
        raw=bytearray(observed['frame_after']);raw[140]^=1;observed['frame_after']=bytes(raw)
    elif fault in ('exit-SR','exit-R14','MACL'):
        raw=list(observed['exit']);raw[{'exit-SR':0,'exit-R14':5,'MACL':2}[fault]]^=0x100;observed['exit']=tuple(raw)
    elif fault=='detached-SR':result['sr']^=256;observed['exit']=(result['sr'],*observed['exit'][1:])
    elif fault=='intermediate-MACL':next(row for row in result['trace'] if row['site']==0xCD80A)['after']['macl']^=0x10000
    elif fault in ('signed-ROM-carrier','pre-delay-R4','full-zero-carrier'):
        site,register={'signed-ROM-carrier':(0xCD808,2),'pre-delay-R4':(0x2E884,4),'full-zero-carrier':(0x2E84A,14)}[fault]
        row=next(row for row in result['trace'] if row['site']==site);raw=list(row['before']['registers']);raw[register]^=0x10000;row['before']['registers']=tuple(raw)
    elif fault=='post-delay-argument':
        row=result['calls'][1]['entry'];raw=list(row['registers']);raw[4]^=256;row['registers']=tuple(raw)
    elif fault in ('call-PR','call-SP'):result['calls'][1]['entry']['pr' if fault=='call-PR' else 'sp']+=4
    elif fault=='skip-store':result['accesses']=[row for row in result['accesses'] if row['address']!=0xFFFF99DE]
    elif fault in ('store-width','store-address','store-register'):
        row=next(row for row in result['accesses'] if row['address']==0xFFFF99DE);row[{'store-width':'width_bytes','store-address':'address','store-register':'register'}[fault]]+=1
    elif fault=='attached-operand':next(row for row in result['trace'] if row['site']==0x2E84A)['accesses']=[]
    elif fault=='return':result['trace'][-1]['next']+=2
    elif fault=='delay':result['trace'][-1]['delay_slot']=False
    elif fault=='opcode':result['trace'][0]['bytes']='0009'
    else:result['code'][0x2E780]='99c4'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.fixture(scope='module')
def publication_pairs():
    # Controlled boundary records exercise publication refusals; the actual primary independently admits the full stock paths.
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();pairs=[];memory_cache={};ordinary_cache={}
    changes=[dict(prior_99de=prior,byte_41e1=gate) for gate in (0,64) for prior in range(256)]
    changes.extend(dict(byte_41e1=64,**{name:raw}) for name in ('raw_rom_8dfc','raw_rom_8dfd') for raw in range(256))
    for update in changes:
        case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled-publication-boundary',**update)
        key=case['byte_41e1'],case['prior_99de']
        if key not in memory_cache:memory_cache[key]=matrix.memory(case)
        memory=memory_cache[key];cal=matrix.calibrations(source,image,case);value=numeric.numerical(memory,cal)
        if key not in ordinary_cache:ordinary_cache[key]=matrix.physical_ordinary(value['ram'],memory)
        fixture,_=contract.fixture_for_case(source,image,case)
        observed=dict(entry=contract.ENTRY,context=matrix.context(source,case),sp=0x30000000,continuation=0x30010000,
            sr_before=0,abi_before=tuple(range(12)),frame_before=bytes(192),memory_before=(memory,),memory_after=(ordinary_cache[key],),
            native_before=matrix.native_bytes(memory),native_after=matrix.native_bytes(value['ram']),calibration_before=cal,
            bound_before=b''.join(fixture[row['address']:row['address']+row['size']] for row in contract.BOUND_SPANS))
        pairs.append((observed,{name:value[name] for name in ('gate','target_before','target_after','products')}))
    return pairs


def test_constant_publication_accepts_identical_zero_outputs_with_all_complete_priors(publication_pairs):
    result=proof.require_publications(publication_pairs)
    assert result['constant_writer_inputs']==dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True)
    assert result['causal_inputs']==dict(raw_rom_8dfc=True,raw_rom_8dfd=True)


@pytest.mark.parametrize('fault',('missing-prior','one-gate','target-echo','ordinary-copy','other-input','ROM-product','constant-ROM-output'))
def test_constant_and_ROM_publications_refuse_omissions_echoes_and_detached_inputs(publication_pairs,fault):
    pairs=[(dict(observed),dict(value)) for observed,value in publication_pairs]
    if fault=='missing-prior':pairs=[pair for pair in pairs if pair[1]['target_before']!=7]
    elif fault=='one-gate':pairs=[pair for pair in pairs if pair[1]['gate']]
    elif fault in ('target-echo','ordinary-copy','other-input'):
        observed,value=pairs[1]
        if fault=='target-echo':
            raw=bytearray(observed['native_after']);raw[proof.native_offset(0xFFFF99DE)]=value['target_before'];observed['native_after']=bytes(raw)
        elif fault=='ordinary-copy':
            raw=bytearray(observed['memory_after'][0]);raw[0x99DE]=0;observed['memory_after']=(bytes(raw),)
        else:
            raw=list(observed['context']);raw[8]^=1;observed['context']=tuple(raw)
    else:
        observed,value=pairs[-1];raw=bytearray(observed['native_after']);at=proof.native_offset(0xFFFFF58C)
        raw[at:at+2]=bytes(2);observed['native_after']=bytes(raw)
    with pytest.raises(ValueError):proof.require_publications(pairs)


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness'][proof.COMPONENT]
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the complete B acceptance requires the actual diagnostic reset writer original')
        pytest.skip('the complete diagnostic reset writer original is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert proof.require_owning_result(result) is True
    assert result['causal_inputs']==dict(raw_rom_8dfc=True,raw_rom_8dfd=True)
    assert result['exact_diagnostic_state_reset_writer_paths'] is True and len(result['native_bindings'])==1
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
    'native-io-before','native-io-after','outside-return','short-native','short-RAM','short-observer','bool-index','duplicate-key'))
def test_actual_complete_original_refuses_source_transport_and_native_substitutions(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'].pop()
    elif fault=='alias':packet['aliases'].append(dict(address=0,alias=4))
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='native-window':packet['simulator']['command'][2]='--memory-region=0xffff8500,256'
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
        elif fault=='short-native':rows[0]['native_io_after']=rows[0]['native_io_after'][:-2]
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
