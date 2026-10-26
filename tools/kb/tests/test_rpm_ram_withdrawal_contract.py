"""Exact selected RAM aliases, original roles and natural RPM helper boundaries."""

import json
import pytest

from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import rpm_ram_withdrawal_path_contract as contract,rpm_ram_withdrawal_matrix as matrix
from kb import rpm_ram_withdrawal_semantics as scalar,rpm_ram_withdrawal_transfers as transfers
from kb import rpm_ram_withdrawal_capture_evidence as proof
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('flags,rpm,output,t',((0,255,0,1),(128,191,0,0),(128,192,1,1),(255,255,1,1)))
def test_MAF_summary_retains_both_actual_input_bytes_and_natural_return_delay(flags,rpm,output,t):
    value=evaluate(0x4F736,maf_fault_flags=flags,maf_rpm=rpm)
    assert value['registers'][0]==value['registers'][2]==output and value['sr']&1==t
    assert value['registers'][6]==(192 if flags&128 else 0x01002448)
    assert value['path'][-2:]==(0x4F754,0x4F756)


@pytest.mark.parametrize('flags,rpm,disabled,expected',((0,80,0,128),(128,66,0,128),
    (0,66,0,0),(255,59,0,127),(255,80,128,127)))
def test_sustained_state_preserves_retention_set_clear_and_original_low_bits(flags,rpm,disabled,expected):
    value=evaluate(0x4F958,sustained_flags=flags,sustained_rpm=rpm,disable_mask=disabled)
    assert value['ram'][0x247C]==expected and value['registers'][0]==int(bool(expected&128))
    assert value['sr']&1==int(not bool(expected&128))
    assert value['path'][-2:]==(0x4F9C0,0x4F9C2)


@pytest.mark.parametrize('exposure,expected',((65534,0),(65535,1)))
def test_word_configuration_zero_extends_and_caps_the_full_byte_product(exposure,expected):
    value=evaluate(0x4F958,exposure_base=65535,exposure_factor=255,exposure=exposure)
    assert value['registers'][0]==expected and value['registers'][4]==65535
    assert value['tags']['threshold']==65535 and value['tags']['product']==65535*255


@pytest.mark.parametrize('argument,configuration,expected',((1,0,30),(2,0,20),(2,128,10),
    (0,0,50),(0,128,40),(0xFFFF0001,0,50),(0x80000002,0,50)))
def test_delay_selector_uses_full_R4_and_the_exact_five_actual_ROM_bytes(argument,configuration,expected):
    value=evaluate(0x5038A,raw_r4=argument,delay_configuration=configuration)
    assert value['registers'][0]==value['registers'][2]==expected and value['registers'][4]==argument
    assert value['path'][-2:]==(0x503DC,0x503DE)


def test_two_byte_configuration_changes_exactly_its_declared_big_endian_word():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4F958,exposure_base=0xABCD)
    fixture,_=contract.fixture_for_case(source,image,case)
    assert fixture[0x90E0:0x90E2]==b'\xab\xcd'
    assert fixture[0x90DF]==image[0x90DF] and fixture[0x90E2]==image[0x90E2]
    assert matrix.calibrations(source,image,case)[0x90E0]==b'\xab\xcd'


def test_exact_fixture_retains_every_instruction_and_only_eight_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and len(aliases)==8


def test_only_the_exact_original_indexed_by_reader_has_the_pinned_nonempty_role():
    rows=withdrawal.descriptor(repo.ROOT)['reference']
    selected=[row for row in rows if json.loads(row['original_claim_json'])['roles']]
    assert len(selected)==1 and selected[0]['id']=='0004f958-ffff11ae-withdraw'
    assert withdrawal.NATIVE_LINK_ROLES=={selected[0]['id']:('indexed_by',)}
    assert json.loads(selected[0]['original_claim_json'])['roles']==['indexed_by']


@pytest.mark.parametrize('root',transfers.NATIVE_RAM_ROOTS)
@pytest.mark.parametrize('address_kind',('native','alias','interior'))
@pytest.mark.parametrize('domain',('ram','rom'))
def test_selected_native_RAM_root_and_its_exact_alias_cannot_be_read_or_hidden(root,address_kind,domain):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='rpm_ram_withdrawal_paths']
    original,native,alias=root;address=native if address_kind=='native' else alias
    width=1
    if address_kind=='interior':address-=1;width=2
    result=dict(accesses=[dict(site=0x4F738,mode='read',address=address,width_bytes=width,domain=domain)])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows)


def test_wrong_native_original_or_alias_mapping_refuses_without_awarding_another_field_identity():
    rows=[dict(row) for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='rpm_ram_withdrawal_paths']
    rows[0]['address']+=1
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[]),rows)


@pytest.mark.parametrize('field,value',(('exposure_base',65536),('exposure',-1),('delay_11',256),
    ('raw_r4',1<<32),('initial_sr',2),('disable_mask',True)))
def test_raw_RAM_argument_and_configuration_widths_reject_substitution(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4F958);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_and_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_original_counts_and_native_RAM_aliases_bind_the_executed_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='rpm_ram_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.rpm-ram-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==3 and len(declared['reference'])==135 and len(declared['function'])==75
    assert len({row['owner'] for row in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('114 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),114),
        ('228 code bytes',sum(b-a for a,b in contract.SPANS),228),('27 literal/configuration spans',len(contract.UNIT['pools']),27),
        ('8 pointer aliases',len(contract.UNIT['aliases']),8),('14 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),14)):
        assert phrase in words and actual==wanted
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))
        -sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==127 and '126 matching ledger selectors' in words
    for original,native,alias in transfers.NATIVE_RAM_ROOTS:
        assert f'{native:08X}' in text and f'{alias:08X}' in text
    assert 'thirteen families and forty-seven capture bindings' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'preceding eight adapters' in words and proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==8
