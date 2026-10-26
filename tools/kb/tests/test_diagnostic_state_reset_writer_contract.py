"""Full reset source boundary, input-only transport and exact native permissions."""
from copy import deepcopy
import re
import pytest
from kb import repo,byte_surface_equations as state
from kb import diagnostic_state_reset_writer_contract as contract,diagnostic_state_reset_writer_matrix as matrix
from kb import diagnostic_state_reset_writer_transfers as transfers


def case(**changes):return dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled-reset-source',**changes)


def test_published_counts_read_the_executed_descriptor_and_driver():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.diagnostic-state-reset-writer.md').read_text()
    actual=(sum((row['end']-row['start'])//2 for row in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    found=re.search(r'binds (\d+) stock instructions in (\d+) entry and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert found is not None and tuple(map(int,found.groups()))==actual==(272,1,4,30,6,31)
    assert int(re.search(r'(\d+) complete functions',text)[1])==len(source['functions'])==3
    assert int(re.search(r'(\d+) conditional sites',text)[1])==len(transfers.CONDITIONAL_SITES)==13
    for name in ('context','frame'):
        assert int(re.search(r'(\d+)-byte '+name,text)[1])==source[name+'_bytes']
    driver=(repo.ROOT/'tools/sh-elf-run/harness-diagnostic-state-reset-writer-paths.c').read_text()
    assert int(re.search(r'(\d+)-byte observer',text)[1])==int(re.search(r'sizeof\(struct observation\)==(\d+)U',driver)[1])==572
    assert int(re.search(r'(\d+) complete context words',text)[1])==len(matrix.context(source,case()))==20
    assert int(re.search(r'all (\d+) ordinary RAM bytes',text)[1])==matrix.RAM_SIZE==65536
    assert int(re.search(r'(\d+) native snapshot bytes',text)[1])==sum(row['size'] for row in source['native_storage'])==matrix.NATIVE_SIZE==2304
    assert int(re.search(r'(\d+) native snapshot banks',text)[1])==len(source['native_storage'])==3
    assert int(re.search(r'(\d+) exact native permissions',text)[1])==len(source['native_permissions'])==27
    assert source['exact_owner_address']==0xFFFF99DE and source['exact_owner_write_site']==0x2E84A
    assert source['exact_owner_loop_iteration']==2 and source['actual_constant_publication']==0


def test_fixture_preserves_all_code_internal_pool_signed_native_words_and_call_targets():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {at for at,(before,after) in enumerate(zip(image,fixture)) if before!=after}<={at for row in aliases for at in range(row['address'],row['address']+4)}
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for address in (0x2E780,0x2E8BE,0x2E8C8,0x2E8CA,0x2E8CC,0x2E8CE,0xCD858,0xCD85A):
        assert fixture[address:address+2]==image[address:address+2]
    for address in (0x2E914,0xCDAC8):assert fixture[address:address+4]==image[address:address+4]
    assert 0x2E780 not in transfers.FEASIBLE_SITES
    for address in (0x2E77A,0x2E780,0x2E84A,0xCD812,0xCD85A):
        altered=bytearray(image);altered[address]^=1
        with pytest.raises(ValueError):contract.independent_fixture(source,bytes(altered))


@pytest.mark.parametrize('fault',('wide-byte','wide-word','wide-register','bool-prior','bad-SR','other-root','missing','expected-output'))
def test_input_shape_refuses_narrowing_and_supplied_outputs(fault):
    raw=case()
    if fault=='wide-byte':raw['prior_99de']=256
    elif fault=='wide-word':raw['native_word_f588']=65536
    elif fault=='wide-register':raw['raw_r4']=1<<32
    elif fault=='bool-prior':raw['prior_99de']=False
    elif fault=='bad-SR':raw['initial_sr']=2
    elif fault=='other-root':raw['entry']=0x2E76E
    elif fault=='missing':raw.pop('byte_40be')
    else:raw['expected_target']=0
    with pytest.raises(ValueError):matrix.require_case(raw)


def test_inputs_supply_all_target_priors_and_raw_ROM_bytes_with_other_inputs_fixed():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();rows=matrix.cases(source,image)
    for gate in (0,64):
        selected=[row for row in rows if row['kind']=='constant-zero-target-with-held-other-inputs' and row['byte_41e1']==gate]
        assert {row['prior_99de'] for row in selected}==set(range(256))
        assert len({tuple((key,value) for key,value in row.items() if key not in ('prior_99de','index')) for row in selected})==1
    for name in ('raw_rom_8dfc','raw_rom_8dfd'):
        assert {row[name] for row in rows if row['byte_41e1']==64}==set(range(256))
    for row in rows:matrix.require_case(row)
    header=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'native_fills[3]' in header and 'struct context context' in header and 'expected_target' not in header
    assert '\\n' not in header and '\n' in header


def invoke(source,fixture,*,sp=0x30000000):
    raw=case();context=matrix.context(source,raw)
    return state.execute(source,fixture,context,matrix.memory(raw),bytes(192),sp,0x30010000,contract.ENTRY,context[18],trace=True)


@pytest.mark.parametrize('fault',('id','image','span','span-type','native-size','native-type','permission-site','permission-mode','permission-width-type','extra-native-key'))
def test_native_profile_requires_exact_ROM_root_spans_banks_and_typed_permissions(fault):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();fixture,_=contract.fixture_for_case(source,image,case())
    source=deepcopy(source)
    if fault=='id':source['id']='jk08a-io-accesses'
    elif fault=='image':source['image_sha256']='0'*64
    elif fault=='span':source['entry'][0]['end']+=2
    elif fault=='span-type':source['entry'][0]['start']=float(source['entry'][0]['start'])
    elif fault=='native-size':source['native_storage'][1]['size']+=1
    elif fault=='native-type':source['native_storage'][0]['size']=256.0
    elif fault=='permission-site':source['native_permissions'][0]['site']+=2
    elif fault=='permission-mode':source['native_permissions'][0]['modes'].append('read')
    elif fault=='permission-width-type':source['native_permissions'][0]['width_bytes']=True
    else:source['native_storage'][0]['extra']=True
    with pytest.raises(ValueError):invoke(source,fixture)


@pytest.mark.parametrize('fault',('different-address','wide-store','write-only-read','bank-frame-overlap'))
def test_native_profile_denies_other_PC_address_width_mode_or_frame_storage(fault):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();fixture,_=contract.fixture_for_case(source,image,case())
    fixture=bytearray(fixture)
    if fault=='different-address':fixture[0x2E780:0x2E782]=bytes.fromhex('99d4')
    elif fault=='wide-store':fixture[0x2E77A:0x2E77C]=bytes.fromhex('2571')
    elif fault=='write-only-read':fixture[0x2E77A:0x2E77C]=bytes.fromhex('6750')
    with pytest.raises(ValueError):invoke(source,bytes(fixture),sp=0xFFFF99A0 if fault=='bank-frame-overlap' else 0x30000000)
