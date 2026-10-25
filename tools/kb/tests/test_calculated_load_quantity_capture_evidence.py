"""Causal handoff, conditional numeric behavior and complete raw/CPU refusal controls."""
from copy import deepcopy
import json
import pytest
from kb import repo,packed_transfer_evidence
from kb import calculated_load_quantity_contract as contract,calculated_load_quantity_matrix as matrix
from kb import calculated_load_quantity_semantics as semantics,calculated_load_quantity_transfers as transfers
from kb import calculated_load_quantity_capture_evidence as proof,byte_surface_equations as state

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-refusal-control');value.update(updates);return value

def equations(value):
    memory=matrix.memory(value)
    cal={0x870E:bytes((value['control_870e'],)),0x11B7B:bytes(value['axis']),0x129D2:bytes(value['curve']),
        0x1491A:b''.join(v.to_bytes(2,'big') for v in value['load_curve'])}
    producer=semantics.evaluate(0,memory,cal);consumer=semantics.evaluate(1,producer['memory'],cal)
    return producer,consumer,cal

def test_real_source_change_propagates_through_computed_K_and_guarded_division():
    a,b,cal=equations(case())
    curve=[128]*17;curve[5]=64;c,d,_=equations(case(curve=curve))
    assert (a['value'],b['value'],c['value'],d['value'])==(128,64,64,128)
    assert b['K']==a['value'] and d['K']==c['value']
    assert b['second_division']==dict(divisor=128,dividend=8192,quotient=64)
    assert d['second_division']==dict(divisor=64,dividend=8192,quotient=128)
    assert any(row['site']==0xB999A and row['address']==0x0100329F and row['bytes']=='80' for row in a['operands'])
    assert any(row['site']==0x808F4 and row['bytes']=='80' for row in b['operands'])
    for poison in (0,1,127,255):assert equations(case(prior_329f=poison))[1]['value']==64

def test_disabled_control_and_real_zero_K_preserve_distinct_conditional_obligations():
    p,c,_=equations(case(curve=[64]*17,control_870e=0x28))
    assert p['value']==64 and c['value']==64 and c['K'] is None and c['second_division'] is None
    assert not any(row['site']==0x808F4 for row in c['operands'])
    p,c,_=equations(case(curve=[0]*17))
    assert p['value']==0 and c['K']==0 and c['value']==255 and c['second_division'] is None

def test_complete_low_sample_byte_and_zero_weight_neighbor_receive_no_false_numerical_credit():
    for low in (0,1,127,128,254,255):
        p,c,_=equations(case(word_4524=0x5000|low))
        assert (p['value'],c['value'])==(128,64)
    for neighbor in (0,1,127,128,254,255):
        curve=[128]*17;curve[16]=neighbor
        p,c,_=equations(case(word_4524=0xFF00,curve=curve))
        assert (p['value'],c['value'])==(128,64)
        assert any(r['site']==0x264B2 and r['address']==0x129E2 and r['bytes']==bytes((neighbor,)).hex() for r in p['operands'])

def test_actual_minus_one_predicate_and_zero_divisor_full_dword_are_retained():
    p,c,_=equations(case(load_curve=[0]*16))
    assert c['predicates']==[(0x808AE,187,0),(0x808B6,8,0),(0x808BE,0xFFFFFFFF,0)]
    assert c['first_divisor']==0 and c['first_quotient']==0 and c['value']==0
    writes=[r for r in c['operands'] if r['mode']=='write']
    assert writes==[dict(site=0x21D6E,mode='write',address=0x01009818,width_bytes=4,register=2,domain='ram',bytes='0000044e'),
        dict(site=0x80926,mode='write',address=0x0100413E,width_bytes=1,register=6,domain='ram',bytes='00')]
    assert c['memory'][0x9818:0x981C]==bytes.fromhex('0000044e')

def test_endpoint_word_return_sign_extension_precedes_the_real_caller_EXTU_W():
    p,c,_=equations(case(byte_11b3=240,load_curve=[65535]*16))
    curve=next(r for r in c['calls'] if r['site']==0x808D4)
    divide=next(r for r in c['calls'] if r['site']==0x808E2)
    assert curve['returned'][0]==0xFFFFFFFF
    assert divide['arguments'][0]==65535 and c['first_divisor']==65535

def handoff():
    p,c,cal=equations(case())
    a=dict(phase=0,pair=0,memory_before=(matrix.memory(case()),),memory_after=(p['memory'],),
        calibration_after=cal,bound_after=b'complete-bound')
    b=dict(phase=1,pair=0,memory_before=(p['memory'],),memory_after=(c['memory'],),
        calibration_before=deepcopy(cal),bound_before=b'complete-bound')
    return a,b,p,c

@pytest.mark.parametrize('fault',('unrelated-RAM-byte','same-K-reset','calibration','bound','pair','phase','synthetic-K'))
def test_matching_K_or_final_numbers_cannot_replace_complete_actual_phase_continuity(fault):
    a,b,p,c=handoff();transfers.require_handoff(a,b,p,c)
    if fault in ('unrelated-RAM-byte','same-K-reset'):
        ram=bytearray(b['memory_before'][0]);ram[0x4000 if fault=='unrelated-RAM-byte' else 0x4524]^=1;b['memory_before']=(bytes(ram),)
    elif fault=='calibration':b['calibration_before'][0x870E]=b'\x28'
    elif fault=='bound':b['bound_before']=b'other-bound'
    elif fault=='pair':b['pair']=1
    elif fault=='phase':b['phase']=0
    else:p['value']^=1
    with pytest.raises(ValueError):transfers.require_handoff(a,b,p,c)

def raw_packet():
    declared=dict(cases=[case()],calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS])
    rows=[]
    for phase in (0,1):
        context=b''.join(v.to_bytes(4,'big') for v in matrix.context({},case(),phase)).hex()
        rows.append(dict(schema=1,pair=0,phase=phase,phase_id=('producer','consumer')[phase],entry=contract.ENTRIES[phase],
            context=context,context_after=context,observation=bytes(572).hex(),ram_before='65536:a5',ram_after='65536:a5',
            calibration_before=bytes(sum(n for at,n in declared['calibration_spans'])).hex(),
            calibration_after=bytes(sum(n for at,n in declared['calibration_spans'])).hex(),
            bound_before=bytes(sum(n for at,n in declared['bound_spans'])).hex(),
            bound_after=bytes(sum(n for at,n in declared['bound_spans'])).hex()))
    marker=proof.MARKER+' status=PASS region='+proof.REGION+' pairs=1 phases=2'
    packet=dict(observations=deepcopy(rows),marker=marker,stdout='\n'.join([*(proof.PREFIX+json.dumps(r) for r in rows),marker]))
    return declared,rows,packet

@pytest.mark.parametrize('fault',('missing','reverse','duplicate-id','wrong-entry','context','duplicate-key'))
def test_raw_stream_refuses_incomplete_or_detached_phase_identity_before_any_semantic_admission(fault):
    declared,rows,packet=raw_packet();assert len(proof.observations(packet,declared))==2
    if fault=='missing':rows.pop()
    elif fault=='reverse':rows.reverse()
    elif fault=='duplicate-id':rows[1]['phase']=0
    elif fault=='wrong-entry':rows[1]['entry']=0xB997C
    elif fault=='context':rows[1]['context_after']=bytes(80).hex()
    packet['observations']=deepcopy(rows)
    packet['stdout']='\n'.join([*(proof.PREFIX+json.dumps(r) for r in rows),packet['marker']])
    if fault=='duplicate-key':packet['stdout']=packet['stdout'].replace('"schema": 1','"schema": 1, "schema": 1',1)
    with pytest.raises(ValueError):proof.observations(packet,declared)

def reconstructed_producer():
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT);value=case()
    fixture,_=contract.fixture_for_case(source,image,value);context=matrix.context(source,value,0)
    sp,continuation=0x30000000,0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,matrix.memory(value),bytes(frame),sp,continuation,0xB997C,0,trace=True)
    observed=dict(phase=0,pair=0,context=context,sp=sp,continuation=continuation,
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        frame_after=result['frame'],memory_after=(result['ram'],),sr_before=0)
    numeric=semantics.evaluate(0,matrix.memory(value),matrix.calibrations(source,image,value))
    return observed,result,numeric,fixture

@pytest.mark.parametrize('fault',('exit-SR','frame-byte','RAM-byte','actual-call-argument','returned-PR','physical-width','delay-slot'))
def test_complete_stock_state_control_rejects_changes_outside_the_scalar_K(fault):
    observed,result,numeric,fixture=reconstructed_producer();transfers.require(observed,result,numeric,fixture)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='frame-byte':raw=bytearray(observed['frame_after']);raw[0]^=1;observed['frame_after']=bytes(raw)
    elif fault=='RAM-byte':raw=bytearray(observed['memory_after'][0]);raw[0]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='actual-call-argument':
        raw=list(result['calls'][0]['entry']['registers']);raw[6]^=1;result['calls'][0]['entry']['registers']=tuple(raw)
    elif fault=='returned-PR':result['pr']^=2
    elif fault=='physical-width':next(r for r in result['accesses'] if r['site']==0xB999A)['width_bytes']=2
    else:result['trace'][-1]['delay_slot']=False
    with pytest.raises(ValueError):transfers.require(observed,result,numeric,fixture)
