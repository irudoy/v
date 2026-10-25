"""Controlled oracle contracts; these do not qualify MCU execution."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from kb import coherent_copy_matrix as matrix, coherent_copy_evidence as proof
from kb import repo

WINDOWS=matrix.WINDOWS

def chosen(call):
    return next(w for w in WINDOWS if w.call==call)

def case(window,**changes):
    return {**matrix.cases(window)[0],**changes}

def set_bytes(memory,address,data):
    memory[address&65535:(address&65535)+len(data)]=data

def test_exact_sources_and_native_binding_members():
    descriptor=proof.descriptor(repo.ROOT)
    assert len(WINDOWS)==len(descriptor['window'])==15
    for window,row in zip(WINDOWS,descriptor['window']):
        for field in ('entry','call','helper','source','destination'):
            assert getattr(window,field)==row[field]
        assert window.length==row['length_bytes']
        assert {'r'+str(r):value for r,value in window.context}==row['entry_context']
    assert len({m['meaning'] for row in descriptor['window'] for m in row['member']})==81
    assert sum(m['mechanism']=='word-lane' for row in descriptor['window'] for m in row['member'])==2
    assert 'complete' not in descriptor

def test_native_pins_bind_exact_owning_claims_and_declared_widths():
    from kb import compile,lock,reconciliation
    from kb.model import SymbolKey
    with lock.held(repo.ROOT):
        model=compile.build(repo.ROOT)
        claims=list(reconciliation.access_claims(model))
        for row in proof.MEMBERS:
            address,direction,meaning,width,signed,identity,*_=row
            symbol=model.symbols[SymbolKey('7mfk','ram',address)]
            assert symbol.meaning.key==meaning
            assert type(symbol.value('width')) is type(width) and symbol.value('width')==width
            assert type(symbol.value('signed')) is type(signed) and symbol.value('signed')==signed
            found=[claim for owner,function,claim in claims if owner is symbol
                   and function.key==proof.parent(row)[0] and claim['type']==direction]
            assert len(found)==1 and reconciliation.digest(found[0])==identity


def test_complete_ordered_matrix_has_distinguishable_read_lanes_and_contexts():
    assert sum(len(matrix.cases(w)) for w in WINDOWS)==17228
    for window in WINDOWS:
        rows=matrix.cases(window)
        assert [r['index'] for r in rows]==list(range(len(rows)))
        assert {(r['seed'],r['variant'],r['t']) for r in rows[:1024]}=={
            (s,v,t) for s in range(256) for v in range(2) for t in range(2)}
        isolated=rows[1024:-12]
        assert {(r['isolated'],r['variant']) for r in isolated}=={
            (at,v) for at in matrix.read_addresses(window) for v in range(2)}
        assert all(r['isolated'] is not None and not r['carry'] for r in isolated)
        assert [r['carry'] for r in rows[-12:]]==[False,True,True]*4

@pytest.mark.parametrize('call',[0x20f56,0x2132c])
def test_large_loop_returns_read_ahead_without_writing_it(call):
    window=chosen(call);row=case(window)
    before=bytearray(65536)
    set_bytes(before,window.source,bytes(range(window.length)))
    set_bytes(before,window.source+window.length,bytes.fromhex('11223344'))
    registers,t,after=matrix.expected(window,row,before,0x87654320)
    assert registers[0]==0x11223344 and t==0
    assert registers[1]==matrix.alias(window.destination)+window.length
    assert registers[2]==matrix.alias(window.source)
    assert registers[3]==matrix.incoming(window,row)[3]
    assert registers[7]==0x87654320
    assert after[window.destination&65535:(window.destination&65535)+window.length]==bytes(range(window.length))
    assert after[(window.source+window.length)&65535:((window.source+window.length)&65535)+4]==bytes.fromhex('11223344')

@pytest.mark.parametrize('call',[0x20f18,0x20f6c])
@pytest.mark.parametrize('t',[0,1])
def test_unrolled_word_tail_restores_registers_and_keeps_entry_t(call,t):
    window=chosen(call);row=case(window,t=t)
    before=bytearray([0xa5]*65536)
    set_bytes(before,window.source+4,bytes.fromhex('76543210'))
    registers,exit_t,after=matrix.expected(window,row,before,0x12345670)
    assert registers[0]==0x76543210 and exit_t==t
    assert registers[1]==matrix.alias(window.destination)
    assert registers[2]==matrix.alias(window.source)
    assert registers[3]==matrix.incoming(window,row)[3]
    assert after[(window.destination&65535)+4:(window.destination&65535)+8]==bytes.fromhex('76543210')

@pytest.mark.parametrize('call,advance',[(0x2105a,0),(0x20fcc,260)])
def test_byte_loop_sign_extends_last_byte_and_advances_only_full_groups(call,advance):
    window=chosen(call);row=case(window,t=1)
    before=bytearray([0xa5]*65536)
    set_bytes(before,window.source+window.length-1,b'\x80')
    registers,t,after=matrix.expected(window,row,before,0x12345670)
    assert registers[0]==0xffffff80 and t==0
    assert registers[1]==matrix.alias(window.destination)+advance
    assert registers[2]==matrix.alias(window.source)
    assert after[(window.destination&65535)+window.length-1]==0x80

def test_word_lanes_and_old_history_remain_distinct():
    window=chosen(0x20f56);row=case(window)
    before=bytearray(65536)
    set_bytes(before,0xffff1082,bytes.fromhex('11223344'))
    set_bytes(before,0xffff1086,bytes.fromhex('1281ff80'))
    _,_,after=matrix.expected(window,row,before,0x12345670)
    assert after[0x1082:0x1086]==bytes.fromhex('1281ff80')
    assert after[0x108a:0x108e]==bytes.fromhex('11223344')
    assert after[0x1083]==before[0x1087]==0x81
    assert after[0x1082]!=after[0x1083] and before[0x1086]!=before[0x1087]

@pytest.mark.parametrize('call,offsets',[(0x20f18,[60]),(0x20f56,[56,60]),(0x20f36,[52,56,60])])
def test_stack_saves_are_specific_to_each_helper_family(call,offsets):
    window=chosen(call);row=case(window)
    before=bytes(96);after=matrix.frame(window,row,before)
    changed=[at for at in range(0,96,4) if after[at:at+4]!=before[at:at+4]]
    assert changed==offsets
    assert after[:52]==before[:52] and after[64:]==before[64:]

def packet(window,row):
    """Controlled synthetic packet, exclusively for validator refusal tests."""
    before=matrix.seed(window,row)
    continuation=0x12345670
    gpr,t,after=matrix.expected(window,row,before,continuation)
    specials=matrix.special(row)
    sr=0x10000000|row['t']
    exit=[(sr&~1)|t,continuation,specials[2],specials[1],specials[0],*reversed(gpr)]
    abi=[*matrix.ABI,0x70000000,0x54321000]
    addresses=matrix.read_addresses(window)
    start=window.destination&65535
    frame=matrix.initial_frame(continuation)
    result=dict(index=row['index'],call=window.call,entry=window.entry,
        source=window.source,destination=window.destination,length=window.length,
        incoming=matrix.incoming(window,row),incoming_after=matrix.incoming(window,row),
        gbr=specials[0],mach=specials[1],macl=specials[2],entry_t=row['t'],
        gbr_after=specials[0],mach_after=specials[1],macl_after=specials[2],entry_t_after=row['t'],
        exit=exit,sp=abi[10]-164,continuation=continuation,sr_before=sr,
        abi_before=abi.copy(),abi_after=abi.copy(),frame_before=frame.hex(),
        frame_after=matrix.frame(window,row,frame).hex(),
        read_before=bytes(before[a&65535] for a in addresses).hex(),
        read_after=bytes(after[a&65535] for a in addresses).hex(),
        destination_before=before[start:start+window.length].hex(),
        destination_after=after[start:start+window.length].hex(),
        pools_before='11223344',pools_after='11223344',
        outside_changes=[[i,before[i],after[i]] for i in range(65536)
                         if not start<=i<start+window.length and before[i]!=after[i]])
    return result,after

@pytest.mark.parametrize('window',WINDOWS,ids=lambda w:f'{w.call:08x}')
def test_controlled_packet_covers_every_family_without_claiming_execution(window):
    row=case(window);observed,after=packet(window,row)
    assert matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))==after

@pytest.mark.parametrize('field',[
    'index','call','entry','source','destination','length','sp','continuation','sr_before',
    'gbr','mach','macl','entry_t','gbr_after','mach_after','macl_after','entry_t_after'])
def test_wrong_scalar_is_refused(field):
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row);observed[field]^=1
    with pytest.raises(ValueError):matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

@pytest.mark.parametrize('field',[
    'incoming','incoming_after','exit','abi_before','abi_after'])
def test_wrong_register_or_external_abi_is_refused(field):
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row);observed[field][0]^=1
    with pytest.raises(ValueError):matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

@pytest.mark.parametrize('field',[
    'read_before','read_after','destination_before','destination_after',
    'pools_before','pools_after','frame_after'])
def test_changed_byte_lane_or_pool_is_refused(field):
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row)
    raw=bytearray.fromhex(observed[field]);raw[-1]^=1;observed[field]=raw.hex()
    with pytest.raises(ValueError):matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

def test_omitted_history_footprint_is_refused():
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row);assert observed['outside_changes']
    observed['outside_changes'].pop()
    with pytest.raises(ValueError):matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

def test_read_ahead_lane_is_checked_separately_from_copied_payload():
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row)
    addresses=matrix.read_addresses(window)
    offset=addresses.index(window.source+window.length)
    raw=bytearray.fromhex(observed['read_after']);raw[offset]^=1;observed['read_after']=raw.hex()
    with pytest.raises(ValueError,match='read lanes or read-ahead'):
        matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

def test_matching_corruption_of_both_frame_snapshots_is_refused():
    window=chosen(0x20f56);row=case(window)
    observed,_=packet(window,row)
    for key in ('frame_before','frame_after'):
        raw=bytearray.fromhex(observed[key]);raw[8]^=1;observed[key]=raw.hex()
    with pytest.raises(ValueError,match='prepared stack seed'):
        matrix.validate_observation(window,row,observed,bytes.fromhex('11223344'))

def test_successive_state_requires_a_predecessor_and_preserves_unrelated_ram():
    window=chosen(0x20fcc)
    rows=matrix.cases(window)[-12:]
    assert not rows[0]['carry'] and rows[1]['carry']
    with pytest.raises(ValueError):matrix.seed(window,rows[1])
    before=matrix.seed(window,rows[0]);_,_,after=matrix.expected(window,rows[0],before,0x12345670)
    after[0x6000]=0x9b
    following=matrix.seed(window,rows[1],after)
    assert following[0x6000]==0x9b and following!=matrix.seed(window,{**rows[1],'carry':False})
