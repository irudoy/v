"""Exact paired word curves,direct saturation and retained scalar dependency scope."""
from copy import deepcopy
import pytest
from kb import repo,proof_adapter
from kb import paired_word_curve_sum_withdrawal_contract as contract,paired_word_curve_sum_withdrawal_matrix as matrix
from kb import paired_word_curve_sum_withdrawal_semantics as scalar,paired_word_curve_sum_withdrawal_transfers as transfers
from kb import paired_word_curve_sum_withdrawal_capture_evidence as proof


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x72C3C,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0x72C3C,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('first,second,quarter,last,wanted_first,wanted_second',((1000,500,400,200,1400,1200),
    (0,0,4,0,0,0),(65535,65535,0,0,65535,65535),(0,0,65535,65535,0,65535),
    (0,65535,4,65535,65534,65535),(65535,1,4,1,65535,65535),(32768,32768,4,32768,65535,65535)))
def test_direct_path_keeps_full_unsigned_promotions_quarter_floor_and_two_distinct_caps(first,second,quarter,last,wanted_first,wanted_second):
    value=evaluate(byte_24d2=0,byte_24ce=0,word_183e=first,word_1340=second,word_120e=quarter,word_2a1c=last)
    assert value['first_output']==wanted_first and value['second_output']==wanted_second
    assert value['ram'][0x19B2:0x19B4]==wanted_first.to_bytes(2,'big')
    assert value['ram'][0x19B6:0x19B8]==wanted_second.to_bytes(2,'big')
    assert value['output']==0x72A and value['calls']==[] and value['known_registers'][5]==65535


@pytest.mark.parametrize('raw,wanted',((0,0),(1,2),(32767,65534),(32768,65535),(65535,65535)))
def test_two_real_curve_results_have_an_independent_full_word_sum_cap(raw,wanted):
    value=evaluate(**{field:raw for field in matrix.CURVE_FIELDS})
    assert value['first_output']==value['second_output']==wanted and value['output']==0x72A
    assert len([row for row in value['calls'] if row['target']==0x26524])==2
    assert value['known_registers'][5]==0xFFFFFFFF


@pytest.mark.parametrize('first,second,coordinate,other,wanted',((0,65535,1024,0,32767),(65535,0,1024,2048,32768)))
def test_both_unsigned_interpolation_directions_keep_their_distinct_rounding(first,second,coordinate,other,wanted):
    value=evaluate(curve_word_00=first,curve_word_01=second,word_28bc=coordinate,word_28be=other)
    curves=[row for row in value['lookups'] if row['kind']=='curve']
    assert curves[0]['value']==wanted and curves[1]['value']==0
    assert value['first_output']==value['second_output']==wanted
    assert curves[0]['fraction']==32768


@pytest.mark.parametrize('neighbor',(0,1,32767,32768,65535))
def test_endpoint_reads_the_complete_last_neighbor_without_granting_numerical_causality(neighbor):
    value=evaluate(word_28bc=65535,word_28be=65535,curve_word_32=neighbor)
    events=[row for row in value['events'].values() if row['site']==0x26536]
    assert len(events)==2 and all((row['address'],row['width_bytes'],row['bytes'])==(0x13242,2,neighbor.to_bytes(2,'big').hex()) for row in events)
    assert value['first_output']==value['second_output']==65535
    assert 'curve_word_32' not in matrix.ENTRY_FIELDS[0x72C3C]


def scalar_rows():
    return [dict(original_claim_sha256='782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b',address=0x942C,owner='rev_limit_throttle_cut/tbl')]


@pytest.mark.parametrize('address,width',((0x942B,2),(0x942C,1),(0x942D,1),(0x942D,2)))
@pytest.mark.parametrize('mode',('read','write'))
@pytest.mark.parametrize('domain',('rom','ram','frame','changed'))
def test_the_complete_existing_uint16_scalar_is_protected_independently_of_operand_labels(address,width,mode,domain):
    result=dict(accesses=[dict(site=0x72C3C,mode=mode,address=address,width_bytes=width,register=0,domain=domain,bytes='00'*width)])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,scalar_rows())


@pytest.mark.parametrize('address,width',((0x942A,2),(0x942E,1)))
def test_direct_scalar_guard_keeps_both_exact_nonoverlap_boundaries(address,width):
    result=dict(accesses=[dict(site=0x72C3C,mode='read',address=address,width_bytes=width,register=0,domain='rom',bytes='00'*width)])
    transfers.require_no_selected_datum(result,scalar_rows())


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_fixture_grants_no_identity_geometry_scale_units_scheduling_stub_or_hardware_claim(tmp_path,flag):
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    target=tmp_path/contract.DESCRIPTOR;target.parent.mkdir(parents=True);target.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_source_counts_bind_the_fixture_raw_geometry_and_domain_consumers():
    words=' '.join((repo.ROOT/'defs/JK08A.paired-word-curve-sum-withdrawal-paths.md').read_text().split())
    for phrase,actual,wanted in (('237 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),237),
        ('474 code bytes',sum(b-a for a,b in contract.SPANS),474),('5 complete code spans',len(contract.SPANS),5),
        ('235 feasible instructions',len(transfers.FEASIBLE_SITES),235),('14 literal spans',len(contract.UNIT['pools']),14),
        ('5 pointer aliases',len(contract.UNIT['aliases']),5),('10 complete RAM fields',len(matrix.RAM_FIELDS),10),
        ('65 raw scalar configuration fields',len(contract.CONFIGURATION),65),('85 raw input fields',len(matrix.WIDTHS),85),
        ('16 calibration spans',len(contract.CONTROLLED_CALIBRATION),16),('11 two-sided conditions',len(proof.REQUIRED_BRANCHES),11),
        ('1 fixed condition',len(proof.FIXED_BRANCHES),1),('8 complete previous source files',len(contract.REUSED_HELPER_FILES_SHA256),8)):
        assert phrase in words and actual==wanted
    assert contract.ENTRIES==(0x72C3C,) and contract.HELPER_ENTRIES==(0x26524,0x26984,0x26740,0x26C78)
    assert transfers.INFEASIBLE_SITES=={0x26D0A,0x26D0C} and proof.FIXED_BRANCHES=={0x26C7A:'fallthrough'}
    assert transfers.NATIVE_SPANS==(('782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b',0x942C,2),)
    curve=[row for row in contract.CONFIGURATION if row['field'].startswith('curve_word_')]
    axis=[row for row in contract.CONFIGURATION if row['field'].startswith('axis_word_')]
    assert [(row['address'],row['size']) for row in curve]==[(0x13202+2*i,2) for i in range(33)]
    assert [(row['address'],row['size']) for row in axis]==[(0x155A0+2*i,2) for i in range(32)]
    assert '32 raw axis words' in words and '33 physical curve words' in words
    assert 'curve_word_32' not in matrix.ENTRY_FIELDS[0x72C3C]
    assert 'both bytes of `942C..942E`' in words and 'returned R0 is `0x72A`' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==33
    assert 'Adapter34' in words and '66 preceding generated outputs' in words
    assert len(proof_adapter.DESCRIPTORS[:proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)])==33


def test_shared_owning_publication_reads_current_execution_descriptor_and_registry():
    import json
    from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
    from kb import scalar_ram_leaf_withdrawal_evidence as family,ordinary_access_registry as registry
    declared=withdrawal.descriptor(repo.ROOT)
    text=' '.join((repo.ROOT/'defs/JK08A.paired-word-curve-sum-withdrawal-paths.md').read_text().split())
    owners={row['owner']:row for row in declared['reference']}
    datum=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']) or ())-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']) or ()) for row in owners.values())
    functions=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    readers=sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])
    for phrase in (f"{len(declared['reference'])} exact access originals",f'{readers} readers and eleven',
            f'{len(owners)} complete datum owners',f"{len(declared['function'])} complete functions",
            f'{datum+functions} matching ledger selectors',f'{datum} datum-end selectors and {functions} function-end selectors',
            f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures'):
        assert phrase in text
    assert len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert len(family.COMPONENTS)==33 and 'Thirty-three independent components' in text
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert withdrawal.digest(withdrawal.paired_word_sum_prior_current_rows(declared,127))==withdrawal.PRIOR_CLAMP_PAIRED_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:68])==withdrawal.PRIOR_CLAMP_PAIRED_FUNCTION_SHA256
