"""Post-guard offset inputs preserve exact existing bytes and ten prior claims."""

from copy import deepcopy
import json
import re

import pytest

from kb import phase_programmer_contract as contract,phase_programmer_matrix as matrix
from kb import phase_programmer_capture_evidence as proof,phase_programmer_semantics as scalar
from kb import phase_access_contract as owning,phase_access_evidence as owning_proof,repo
from kb.test_stock_capture import tool
from kb import byte_surface_equations as state

RETAINED_CLAIMS=(('ffff13b8-reader',
  'cd910dcbf30c3d090b3b1a9d8e10d765eac64f12003eab20d3dfbc615eff2cd3',
  '3b2832c18f4241eaa430a71c9c37fe1906aadbaaf8604cf0a36b09d488429f35'),
 ('ffff13b8-writer',
  '8e41c4bb288af2c59ba0f52c7594232bc77979950bf5f6a1a1fa7e0161b46bd8',
  '3fe06ab415d4fb6005cf0bee6761db6edbcb93d57674ec759ddf81a9b4e46637'),
 ('ffff1558-reader',
  '2009c140f1e08862fd8f77f8bf676bb8ca1693cac892ac9cb646f4806c07e8ce',
  'd6fdc35b7535e7d5eb72a9e9a03779c0353363669a3c7940bda1cfc80df2b4ba'),
 ('ffff1558-writer',
  'bb6a2d755f2f317e18e693398a96fb55a1e4a150e4b2cc6b39ec6708a6667832',
  'c3aa8817cd03f1838fd4d46305348905c8af31893e6b957e9787861e6a1c3280'),
 ('ffff155a-reader',
  '4f695ad9c1115d8bbaac83be399ca60cb0cf41cc8f4a2f7e0c8dff798c56c0d6',
  '630cf4298767017cea5aa02aa6e88403bc9ffd70dbc1d7136a01da6783cf15a8'),
 ('ffff155a-writer',
  '596e450f6b5a82a6749fccede61705a98b5a0400c690b909f3bc23fca439a5e7',
  '515fdcfd99a3380d2a390222e1c575d8956b3c4dad8401bc4acc4b19d0da7095'),
 ('ffff193b-reader',
  'f4e18c757da8f8186ae164e6f3fb22e51036af6e6ff1de040cd331dbe6d57735',
  '96328833ea9037739eaedef079b795d16a735497d06b62d6859222b826e94e0a'),
 ('ffff193b-writer',
  '590d921070d8ae82f97279f0d946a2a7d0e74aab582b6e975f3cc87c70d58f1a',
  'bb50b25bd7b1e4ab861cec1c9b1caf4840a7df2d3077dc38a5a2fcdb1f55f5f5'),
 ('00028e7c-ffff1558-writer',
  '7041bfbde9bd7daf310c37953c840411e76a35029abe3745be79eee1a471b9ed',
  'd7e6747681447aa99729dce1ee9c08d8af7c77aec397abb5973a9f74aae129cd'),
 ('00028e7c-ffff155a-writer',
  '30da7b19c7975d4070dfee9be1037b34c4affb914b795210099f2410ba113a41',
  '6090982220b9287fdaa1eb3300a7e38df82c6a5ba8d7f2ea6783f9ed12c82d10'))


def test_joint_twelve_preserves_all_ten_prior_original_and_proposed_claim_items():
    rows={row['id']:row for row in owning.descriptor(repo.ROOT)['reference']}
    assert len(rows)==12 and len({row['owner'] for row in rows.values()})==6
    for identity,before,after in RETAINED_CLAIMS:
        assert (rows[identity]['original_claim_sha256'],rows[identity]['proposed_claim_sha256'])==(before,after)
    added=[row for key,row in rows.items() if key not in {item[0] for item in RETAINED_CLAIMS}]
    assert {(row['owner'],row['function'],tuple(row['sites']),row['width_bytes'],row['declared_width'],row['declared_signed']) for row in added}=={
        ('amphibian-panda/ram',0x2B64A,(0x28E94,),2,16,False),
        ('injection_offset_reciprocal_residue/ram',0x2B64A,(0x28E98,),1,8,False)}
    for row in added:
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
        assert row['original_ledger_json']==row['proposed_ledger_json']
    assert set(owning_proof.COMPONENTS)=={'phase_normalization_paths','phase_programmer_paths'}


def test_only_two_pointer_literals_and_the_outside_return_change_in_the_fixture():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    fixture,aliases=contract.independent_fixture(declared,image)
    assert aliases==[dict(address=0x2B864,original=0xFFFF128C,alias=0x0100128C),
        dict(address=0x2B874,original=0xFFFF1FF4,alias=0x01001FF4)]
    restored=bytearray(fixture)
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    restored[0x2B6F8:0x2B700]=image[0x2B6F8:0x2B700]
    assert bytes(restored)==image
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert sum((row['end']-row['start'])//2 for row in contract.WINDOWS)==35
    assert sum(row['size'] for row in contract.POOLS)==20
    assert fixture[0x2B6F8:0x2B700]==bytes.fromhex('57f6472a000b0009')


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_implicit_guard_programmer_peripheral_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('period,remainder,q,residue,t',((0,0,0,0,1),(1,9,0,9,1),(1,10,1,0,0),
    (8192,4,3277,254,0),(25000,8,20001,246,0),(65535,119,0xE68A,37,0),
    (65535,255,0x804C,9,0),(65535,1,6553,5,0)))
def test_real_caller_products_follow_low32_reciprocal_arithmetic(period,remainder,q,residue,t):
    result=scalar.scalar(period,remainder)
    assert (result['argument'],result['quotient'],result['remainder'],result['exit_t'])==(period*remainder,q,residue,t)


@pytest.mark.parametrize('period,remainder',((-1,0),(65536,0),(0,-1),(0,256),(True,1)))
def test_scalar_refuses_a_different_input_width(period,remainder):
    with pytest.raises(ValueError):scalar.scalar(period,remainder)


def test_legacy_expected_outputs_are_not_raw_input_sources(tmp_path):
    source=(repo.ROOT/contract.LEGACY_INPUTS).read_text()
    changed=re.sub(r'^(\{(?:0x[0-9a-f]+U,){4})0x[0-9a-f]+U,',r'\g<1>0xabcdef01U,',source,flags=re.M)
    path=tmp_path/contract.LEGACY_INPUTS;path.parent.mkdir(parents=True);path.write_text(changed)
    assert changed!=source and matrix.legacy_inputs(tmp_path)==matrix.legacy_inputs(repo.ROOT)


@pytest.mark.parametrize('field,at,width',(('period',0x22BC,2),('remainder',0x193B,1)))
def test_positive_input_alternatives_hold_complete_other_memory_context_and_literals(field,at,width):
    declared=contract.descriptor(repo.ROOT)
    case=dict(index=0,entry=0x2B6D4,period=8192,remainder=4,variant=0,sr=0)
    other=deepcopy(case);other[field]+=1
    assert matrix.context(declared,case)==matrix.context(declared,other)
    a,b=bytearray(matrix.memory(case)),bytearray(matrix.memory(other))
    assert a[at:at+width]!=b[at:at+width];a[at:at+width]=b[at:at+width]
    assert a==b


def test_private_header_and_observer_context_match_without_expected_outputs():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image,root=repo.ROOT)))
    producer=tool(repo.ROOT,'phase_programmer_capture.py','_kb_phase_programmer_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)


@pytest.mark.parametrize('register',(0,7,14))
@pytest.mark.parametrize('sr',(0,1,0x301))
def test_LDS_register_PR_observing_return_uses_the_frame_value_and_natural_delay_slot(register,sr):
    entry,sp,continuation=0x200,0x02000100,0x123456
    context=tuple([0x17283900+index for index in range(15)]+[0x12344321,0x13579BDF,0x2468ACE0,sr,0xB6C70000])
    frame=bytearray([0xA5])*192;frame[184:188]=continuation.to_bytes(4,'big')
    words=(0x50F6|(register<<8),0x402A|(register<<8),0x000B,0x0009)
    code=b''.join(word.to_bytes(2,'big') for word in words)
    fixture=bytearray(1024);fixture[entry:entry+8]=code
    result=state.execute(dict(id='jk08a-phase-programmer',entry=[dict(start=entry,end=entry+8)]),
        bytes(fixture),context,bytes([0xA5])*65536,bytes(frame),sp,continuation,entry,sr)
    expected=list(context[:15]);expected[register]=continuation
    assert result['registers']==tuple(expected)
    assert (result['pr'],result['sp'],result['sr'],result['mach'],result['macl'],result['gbr'])==(
        continuation,sp,sr,context[16],context[17],context[15])
    assert result['frame']==bytes(frame) and result['ram']==bytes([0xA5])*65536
    assert [(row['site'],row['target'],row['kind']) for row in result['branches']]==[(entry+4,continuation,'return')]
    assert result['code']=={entry+2*index:word.to_bytes(2,'big').hex() for index,word in enumerate(words)}
    assert result['calls']==[] and [(row['domain'],row['address'],row['width_bytes'],row['bytes'])
        for row in result['accesses']]==[('frame',sp+24,4,continuation.to_bytes(4,'big').hex())]
