"""Exact monitor raw gates,absolute comparisons,unordered limits and direct-table scope."""
from copy import deepcopy
import pytest
from kb import repo,proof_adapter
from kb import clamp_latch_caller_withdrawal_contract as contract,clamp_latch_caller_withdrawal_matrix as matrix
from kb import clamp_latch_caller_withdrawal_semantics as scalar,clamp_latch_caller_withdrawal_transfers as transfers
from kb import clamp_latch_caller_withdrawal_capture_evidence as proof


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x39316,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0x39316,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('state,word,lower,upper,wanted',((100,1,0,255,101),(100,65535,0,255,99),
    (0,32768,0,255,0),(255,32767,0,255,255),(100,0,200,50,200),(250,0,200,100,100),(100,0,128,127,128)))
def test_signed_word_addend_and_unordered_clamp_follow_the_two_real_conditions(state,word,lower,upper,wanted):
    value=evaluate(byte_55e6=state,word_1ee2=word,config_8692=lower,config_8693=upper)
    assert value['ram'][0x55E6]==wanted and value['output']==0x144
    assert value['ram'][0x422F]==0xA4 and value['ram'][0x1FA4:0x1FA6]==bytes.fromhex('a53c')
    assert value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('first,second,count',((100,100,2),(91,100,2),(90,100,1),(109,100,2),(110,100,1),(0,255,1),(255,0,1)))
def test_first_absolute_call_has_exact_post_delay_subtraction_and_ten_boundary(first,second,count):
    value=evaluate(byte_11ea=first,byte_22e4=second)
    assert len(value['calls'])==count
    call=value['calls'][0]
    assert (call['site'],call['target'],call['registers'][4])==(0x3936C,0x22590,(first-second)&0xFFFFFFFF)
    assert call['return_registers'][0]==abs(first-second) and call['return_site']==0x22596


@pytest.mark.parametrize('word,previous',((0,65535),(65535,0),(25,0),(25,227),(25,228),(25,229),(25,100),(16384,65535)))
def test_second_absolute_call_retains_full_unsigned_word_shift_and_signed_difference(word,previous):
    value=evaluate(word_1062=word,word_1fa4=previous)
    call=value['calls'][1];difference=word*4-previous
    assert (call['site'],call['target'],call['registers'][4])==(0x3938A,0x22590,difference&0xFFFFFFFF)
    assert call['return_registers'][0]==abs(difference)
    assert call['return_sr']&1==int(difference>0)


@pytest.mark.parametrize('raw',(0,1,127,128,255,256,32767,32768,65535))
def test_final_real_word_refresh_preserves_every_source_bit_after_its_signed_load(raw):
    value=evaluate(word_1026=raw)
    assert value['ram'][0x1FA4:0x1FA6]==raw.to_bytes(2,'big') and value['known_registers'][2]==(raw if raw<32768 else raw-65536)&0xFFFFFFFF
    assert value['output']==0x144


def table_rows():
    return [dict(original_claim_sha256='4193a93d663def7a0f8c62b6519e3909b5ae7523997ae08977dd9f3cbdb32951',address=0x15630,owner='nice-coucal/tbl')]


@pytest.mark.parametrize('offset',range(16))
@pytest.mark.parametrize('mode',('read','write'))
@pytest.mark.parametrize('domain',('rom','ram','frame','changed'))
def test_direct_reader_guard_protects_each_byte_of_the_whole_eight_word_owner(offset,mode,domain):
    result=dict(accesses=[dict(site=0x39316,mode=mode,address=0x15630+offset,width_bytes=1,domain=domain,register=0,bytes='00')])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,table_rows())


@pytest.mark.parametrize('address,width,overlap',((0x1562E,2,False),(0x1562F,2,True),(0x1563F,2,True),(0x15640,1,False)))
def test_complete_table_interval_keeps_both_exact_cross_boundary_overlap_rules(address,width,overlap):
    result=dict(accesses=[dict(site=0x39316,mode='read',address=address,width_bytes=width,domain='rom',register=0,bytes='00'*width)])
    if overlap:
        with pytest.raises(ValueError):transfers.require_no_selected_datum(result,table_rows())
    else:transfers.require_no_selected_datum(result,table_rows())


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_natural_fixture_grants_no_geometry_scale_units_scheduling_stub_or_hardware_claim(tmp_path,flag):
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    target=tmp_path/contract.DESCRIPTOR;target.parent.mkdir(parents=True);target.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_independent_source_counts_read_the_executed_fixture_input_and_domain_sources():
    words=' '.join((repo.ROOT/'defs/JK08A.clamp-latch-caller-withdrawal-paths.md').read_text().split())
    for phrase,actual,wanted in (('118 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),118),
        ('236 code bytes',sum(b-a for a,b in contract.SPANS),236),('2 complete code spans',len(contract.SPANS),2),
        ('118 feasible instructions',len(transfers.FEASIBLE_SITES),118),('20 pinned data spans',len(contract.UNIT['pools']),20),
        ('14 pointer aliases',len(contract.UNIT['aliases']),14),('15 complete RAM fields',len(matrix.RAM_FIELDS),15),
        ('3 scalar configuration fields',len(contract.CONFIGURATION),3),('28 raw input fields',len(matrix.WIDTHS),28),
        ('20 calibration spans',len(contract.CONTROLLED_CALIBRATION),20),('14 two-sided conditions',len(proof.REQUIRED_BRANCHES),14)):
        assert phrase in words and actual==wanted
    assert contract.ENTRIES==(0x39316,) and contract.HELPER_ENTRIES==(0x22590,)
    assert transfers.INFEASIBLE_SITES==set() and proof.FIXED_BRANCHES=={}
    assert transfers.NATIVE_SPANS==(('4193a93d663def7a0f8c62b6519e3909b5ae7523997ae08977dd9f3cbdb32951',0x15630,16),)
    assert transfers.ABSOLUTE_CALL_INPUTS=={0x3936C:(-255,255),0x3938A:(-65535,262140)}
    assert 'complete 16-byte table interval' in words and 'generic22590 original remains incomplete' in words

    assert 'returned R0 is0x144' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==32
    assert 'Adapter33' in words and '64 preceding generated outputs' in words
    assert len(proof_adapter.DESCRIPTORS[:proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)])==32


def test_shared_owning_publication_reads_current_execution_descriptor_and_registry():
    import json
    from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
    from kb import scalar_ram_leaf_withdrawal_evidence as family,ordinary_access_registry as registry
    declared=withdrawal.descriptor(repo.ROOT)
    text=' '.join((repo.ROOT/'defs/JK08A.clamp-latch-caller-withdrawal-paths.md').read_text().split())
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
    assert len(family.COMPONENTS)==34 and 'Thirty-four independent components' in text
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert withdrawal.digest(withdrawal.paired_word_sum_prior_current_rows(declared,127))==withdrawal.PRIOR_CLAMP_PAIRED_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:68])==withdrawal.PRIOR_CLAMP_PAIRED_FUNCTION_SHA256
