"""Complete source boundary, raw controls, native permissions and input-only ABI."""
from copy import deepcopy
import re
import pytest
from kb import repo,byte_surface_equations as state
from kb import indexed_timer_refresh_writer_contract as contract
from kb import indexed_timer_refresh_writer_matrix as matrix
from kb import indexed_timer_refresh_writer_transfers as transfers


def case(**changes):
    return dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled-timer-source',**changes)


def test_published_counts_read_the_executed_source_and_unchanged_driver():
    source=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.indexed-timer-refresh-writer.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    found=re.search(r'binds (\d+) stock instructions in (\d+) entry and (\d+) span,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert found is not None and tuple(map(int,found.groups()))==actual==(98,1,1,7,3,8)
    for name,wanted in (('context',80),('frame',192)):
        assert int(re.search(r'(\d+)-byte '+name,text)[1])==source[name+'_bytes']==wanted
    driver=(repo.ROOT/'tools/sh-elf-run/harness-indexed-timer-refresh-writer-paths.c').read_text()
    assert int(re.search(r'(\d+)-byte observer',text)[1])==int(re.search(r'sizeof\(struct observation\)==(\d+)U',driver)[1])==572
    assert int(re.search(r'(\d+) complete context words',text)[1])==len(matrix.context(source,case()))==20
    assert int(re.search(r'all (\d+) ordinary RAM bytes',text)[1])==matrix.RAM_SIZE==65536
    assert int(re.search(r'(\d+)-byte native window',text)[1])==source['native_control_bytes']['window_size']==matrix.NATIVE_SIZE==256
    assert int(re.search(r'(\d+) conditional sites',text)[1])==len(transfers.CONDITIONAL_SITES)==6
    assert source['software_index_premise']==dict(first=0,last=255,additional=[0xFFFFFFFF])
    assert source['exact_owner_index']==6 and source['exact_owner_address']==0xFFFF43BE


def test_fixture_preserves_every_instruction_and_the_native_signed_literal():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    changed={at for at,(old,new) in enumerate(zip(image,fixture)) if old!=new}
    allowed={at for row in aliases for at in range(row['address'],row['address']+4)}
    assert changed<=allowed and len(aliases)==3
    assert fixture[0x9018C:0x90250]==image[0x9018C:0x90250]==bytes.fromhex(contract.STOCK_CODE_HEX)
    assert fixture[0x90254:0x90256]==bytes.fromhex('850c')
    for address in (0x9018C,0x9024E,0x90254,0x903F8):
        altered=bytearray(image);altered[address]^=1
        with pytest.raises(ValueError):contract.independent_fixture(source,bytes(altered))


@pytest.mark.parametrize('fault',('wide-byte','wide-register','bool-byte','unsupported-index','bad-SR','extra-result','other-entry','missing'))
def test_raw_inputs_refuse_width_loss_and_supplied_results(fault):
    raw=case()
    if fault=='wide-byte':raw['native_reset']=256
    elif fault=='wide-register':raw['raw_r5']=1<<32
    elif fault=='bool-byte':raw['arm']=False
    elif fault=='unsupported-index':raw['raw_r4']=256
    elif fault=='bad-SR':raw['initial_sr']=2
    elif fault=='extra-result':raw['expected_timer']=100
    elif fault=='other-entry':raw['entry']+=2
    else:raw.pop('timer_006')
    with pytest.raises(ValueError):matrix.require_case(raw)


def test_matrix_has_full_enable_width_indices_and_independent_native_preimages():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert {row['raw_r4'] for row in rows}==set(contract.INDICES)
    assert {row['raw_r5'] for row in rows}>={0,1,0x10000,0x80000000,0xFFFFFFFF}
    for name in ('native_reset','native_indicator','arm','other_arm','judged','reload','timer_006'):
        assert {row[name] for row in rows}==set(range(256))
    assert {row['initial_sr'] for row in rows}=={qm|interrupt|t for qm in (0,256,512,768) for interrupt in range(0,256,16) for t in (0,1)}
    for row in rows:matrix.require_case(row)
    header=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'uint32_t ram[262]' in header and 'struct context context' in header
    assert '\\n' not in header and '\n' in header
    assert 'expected_timer' not in header and 'expected_native' not in header


def invoke(source,fixture,raw,*,sp=0x30000000):
    context=matrix.context(source,raw)
    return state.execute(source,fixture,context,matrix.memory(raw),bytes(192),sp,0x30010000,
        contract.ENTRY,context[18],trace=True)


@pytest.mark.parametrize('fault',('id','image','span','span-type','window-start','window-size','window-type','addresses','addresses-type','extra-native-key'))
def test_native85_profile_requires_exact_rom_root_span_and_typed_controls(fault):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,_=contract.fixture_for_case(source,image,case());source=deepcopy(source)
    if fault=='id':source['id']='jk08a-publication-inhibit-path'
    elif fault=='image':source['image_sha256']='0'*64
    elif fault=='span':source['entry'][0]['end']+=2
    elif fault=='span-type':source['entry'][0]['end']=float(source['entry'][0]['end'])
    elif fault=='window-start':source['native_control_bytes']['window_start']-=256
    elif fault=='window-size':source['native_control_bytes']['window_size']+=1
    elif fault=='window-type':source['native_control_bytes']['window_size']=256.0
    elif fault=='addresses':source['native_control_bytes']['addresses'].append(0xFFFF850E)
    elif fault=='addresses-type':source['native_control_bytes']['addresses']=tuple(source['native_control_bytes']['addresses'])
    else:source['native_control_bytes']['extra']=True
    with pytest.raises(ValueError):invoke(source,fixture,case())


@pytest.mark.parametrize('fault',('indicator-write','unused-read','wide-read','wide-write','overlap-frame'))
def test_native85_profile_has_only_two_exact_byte_permissions(fault):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,_=contract.fixture_for_case(source,image,case());fixture=bytearray(fixture)
    if fault=='indicator-write':fixture[0x90254:0x90256]=bytes.fromhex('850d')
    elif fault=='unused-read':fixture[0x90254:0x90256]=bytes.fromhex('850b')
    elif fault=='wide-read':fixture[0x901DA:0x901DC]=bytes.fromhex('6051')
    elif fault=='wide-write':fixture[0x901DE:0x901E0]=bytes.fromhex('2501')
    with pytest.raises(ValueError):invoke(source,bytes(fixture),case(),sp=0xFFFF85A0 if fault=='overlap-frame' else 0x30000000)
