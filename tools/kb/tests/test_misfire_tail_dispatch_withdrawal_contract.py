"""Controlled hysteresis, exact counter promotions, tail frame and native-root scope."""
import pytest
from kb import repo,proof_adapter
from kb import misfire_tail_dispatch_withdrawal_contract as contract,misfire_tail_dispatch_withdrawal_matrix as matrix
from kb import misfire_tail_dispatch_withdrawal_semantics as scalar,misfire_tail_dispatch_withdrawal_transfers as transfers
from kb import misfire_tail_dispatch_withdrawal_capture_evidence as proof


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x7C494,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0x7C494,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('prior,coordinate,threshold,admitted,wanted',((0,31,32,False,0),
    (128,27,32,False,0),(128,28,32,True,128),(0,32,32,True,128),
    (255,255,255,True,255),(127,0,0,True,255),(128,251,255,True,128),(128,250,255,False,0)))
def test_hysteresis_promotes_the_complete_unsigned_byte_before_adding_four(prior,coordinate,threshold,admitted,wanted):
    value=evaluate(byte_24c4=prior,byte_11b2=coordinate,config_8bda=threshold)
    row=next(item for item in value['lookups'] if item['kind']=='hysteresis-and-saturated-byte-counter')
    assert row['promoted_coordinate']==coordinate+(4 if prior&128 else 0)
    assert row['admitted'] is admitted and value['ram'][0x24C4]==wanted
    assert value['byte_counter']==(8 if admitted else 0)


@pytest.mark.parametrize('raw,wanted,returned',((0,1,1),(127,128,128),(128,129,129),(254,255,255),(255,255,0xFFFFFFFF)))
def test_saturating_byte_counter_keeps_its_distinct_complete_signed_early_return(raw,wanted,returned):
    value=evaluate(byte_11b2=255,byte_4096=raw)
    assert value['byte_counter']==wanted and len(value['calls'])==1
    assert value['calls'][0]['return_registers'][0]==returned
    writes=[row for row in value['events'].values() if row['site']==0x7C524]
    assert len(writes)==(0 if raw==255 else 1)
    if writes:assert writes[0]['bytes']==bytes([wanted]).hex()


@pytest.mark.parametrize('raw',(0,1,127,128,254,255))
def test_clear_hysteresis_result_resets_the_complete_counter_without_loading_its_old_value(raw):
    value=evaluate(byte_11b2=0,byte_24c4=0,byte_4096=raw)
    assert value['byte_counter']==0 and value['calls'][0]['return_registers'][0]==0
    assert all(row['site']!=0x7C50E for row in value['events'].values())


@pytest.mark.parametrize('counts,factors,wanted,flags',(((199,999,199),(1,1),(200,1000,200),0),
    ((200,1000,200),(1,1),(1,1,1),224),((65535,65535,65535),(1,1),(1,1,1),224),
    ((0,0,0),(0,0),(1,1,1),96),((50999,999,50999),(255,255),(51000,1000,51000),0),
    ((51000,999,51000),(255,255),(1,1000,1),96),((32768,0,32768),(255,255),(32769,1,32769),0)))
def test_three_independent_thresholds_reset_before_the_complete_low_word_increment(counts,factors,wanted,flags):
    value=evaluate(word_409e=counts[0],word_40a0=counts[1],word_40a2=counts[2],
        config_8354=factors[0],config_8656=factors[1])
    assert value['word_counters']==wanted and value['ram'][0x4241]==flags
    assert value['output']==wanted[2]
    assert value['preincrement_word_overflow_excluded_by_exact_raw_threshold_bounds'] is True


@pytest.mark.parametrize('prior',(0,1,31,32,64,128,224,255))
def test_ordered_threshold_flag_updates_preserve_every_prior_bit(prior):
    value=evaluate(word_409e=200,word_40a0=1000,word_40a2=200,byte_4241=prior)
    rows=[row for row in value['events'].values() if row['site'] in (0x87300,0x87318,0x8733A)]
    assert [(row['site'],row['bytes']) for row in rows]==[(0x87300,bytes([prior|32]).hex()),
        (0x87318,bytes([prior|160]).hex()),(0x8733A,bytes([prior|224]).hex())]
    assert 'byte_4241' not in matrix.ENTRY_FIELDS[0x7C494]


@pytest.mark.parametrize('speed,enough,words,returned',((0,False,(199,999,199),0x15C),
    (30,False,(199,999,199),0x15C),(31,True,(200,1000,200),200),
    (127,True,(200,1000,200),200),(128,True,(200,1000,200),200),(255,True,(200,1000,200),200)))
def test_sign_extended_byte_is_compared_as_the_full_unsigned_register(speed,enough,words,returned):
    value=evaluate(byte_3834=speed)
    row=next(item for item in value['lookups'] if item['kind']=='sign-extended-byte-unsigned-comparison')
    assert row['full_register']==(speed if speed<128 else speed|0xFFFFFF00)
    assert row['admitted'] is enough and value['word_counters']==words and value['output']==returned


@pytest.mark.parametrize('first_stop,third_stop,wanted,returned',((0,0,(200,1000,200),200),
    (1,0,(199,999,200),200),(0,1,(200,1000,199),0x85),(1,1,(199,999,199),0x85)))
def test_first_pair_and_third_counter_have_separate_actual_stop_gates(first_stop,third_stop,wanted,returned):
    value=evaluate(byte_444d=first_stop,byte_444c=third_stop)
    assert value['word_counters']==wanted and value['output']==returned
    assert len(value['local_counter_preimages'])==(0 if first_stop else 2)


@pytest.mark.parametrize('mode,prerequisites',((0,3),(128,0),(128,1),(128,2)))
def test_each_failed_prerequisite_has_the_real_three_word_reset(mode,prerequisites):
    value=evaluate(byte_4251=mode,byte_41d2=prerequisites)
    assert value['word_counters']==(0,0,0) and value['output']==0
    assert value['local_counter_preimages']==()


@pytest.mark.parametrize('configuration',(0,1,127))
def test_disabled_tail_still_executes_the_full_first_leaf_and_restores_the_actual_MACL(configuration):
    value=evaluate(config_186ce=configuration)
    assert value['tail_disabled'] is True and value['byte_counter']==8
    assert value['word_counters']==(199,999,199) and value['output']==configuration
    assert all(not (row['domain']=='ram' and row['site']>=0x872D0) for row in value['events'].values())


def test_ordered_root_PR_and_tail_MACL_reuse_and_signed_counter_locals_have_distinct_full_preimages():
    value=evaluate(word_409e=32768,config_8354=255)
    saved=[row for row in value['events'].values() if row['site'] in (0x7C494,0x7C49E,0x872D0,0x8739C)]
    assert [(row['site'],row['mode'],row['address']) for row in saved]==[(0x7C494,'write',0x02000FFC),
        (0x7C49E,'read',0x02000FFC),(0x872D0,'write',0x02000FFC),(0x8739C,'read',0x02000FFC)]
    assert saved[0]['bytes']==saved[1]['bytes']=='02100000'
    assert saved[2]['bytes']==saved[3]['bytes']==value['macl'].to_bytes(4,'big').hex()
    assert value['local_counter_preimages']==((0x87370,0x02000FF4,0xFFFF8000),(0x87378,0x02000FF8,999))
    assert value['frame'][148:152]==bytes.fromhex('ffff8000')
    assert value['frame'][152:156]==(999).to_bytes(4,'big')
    assert value['frame'][156:160]==value['macl'].to_bytes(4,'big')
    assert value['sp']==0x02001000 and value['pr']==0x02100000


def native_rows():
    return [dict(original_claim_sha256='02d868473e3c258ee4fe81777aea05a65bd44e0a57d0e64ef658d8f3949df311',
        address=0xFFFF84BA,owner='antique-hawk/ram')]


@pytest.mark.parametrize('root',(0xFFFF84BA,0x010084BA))
@pytest.mark.parametrize('offset,width',((0,1),(-1,2),(-3,4)))
@pytest.mark.parametrize('mode',('read','write'))
@pytest.mark.parametrize('domain',('ram','rom','frame','changed'))
def test_selected_root_absence_rejects_every_overlapping_natural_operand_without_inferring_native_width(root,offset,width,mode,domain):
    result=dict(accesses=[dict(site=0x7C494,mode=mode,address=root+offset,width_bytes=width,register=0,domain=domain,bytes='00'*width)])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,native_rows())


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_fixture_grants_no_native_type_schedule_geometry_scale_hardware_stub_or_publication(tmp_path,flag):
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    target=tmp_path/contract.DESCRIPTOR;target.parent.mkdir(parents=True);target.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_source_counts_read_the_current_complete_fixture_and_raw_sources():
    words=' '.join((repo.ROOT/'defs/JK08A.misfire-tail-dispatch-withdrawal-paths.md').read_text().split())
    config={row['address'] for row in contract.CONFIGURATION}
    for phrase,actual,wanted in (('146 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),146),
        ('292 code bytes',sum(last-first for first,last in contract.SPANS),292),('3 complete code spans',len(contract.SPANS),3),
        ('14 conditional sites',len(proof.REQUIRED_BRANCHES),14),('12 complete RAM fields',len(matrix.RAM_FIELDS),12),
        ('4 configuration bytes',len(contract.CONFIGURATION),4),('26 raw input fields',len(matrix.WIDTHS),26),
        ('15 causal input fields',len(matrix.ENTRY_FIELDS[0x7C494]),15),('8 pointer aliases',len(contract.UNIT['aliases']),8),
        ('14 literal spans',len([row for row in contract.UNIT['pools'] if row['address'] not in config]),14),
        ('18 data spans',len(contract.UNIT['pools']),18),('18 calibration spans',len(contract.CONTROLLED_CALIBRATION),18)):
        assert phrase in words and actual==wanted
    assert contract.ENTRIES==(0x7C494,) and contract.HELPER_ENTRIES==(0x7C4E0,0x872D0)
    assert not transfers.INFEASIBLE_SITES and len(transfers.FEASIBLE_SITES)==146 and proof.FIXED_BRANCHES=={}
    assert {(row['address'],row['size']) for row in contract.CONFIGURATION}=={(0x8BDA,1),(0x186CE,1),(0x8354,1),(0x8656,1)}
    assert next(row['stock_hex'] for row in contract.UNIT['pools'] if row['address']==0x8739E)=='03e8'
    assert 200*((1<<matrix.WIDTHS['config_8354'])-1)==200*((1<<matrix.WIDTHS['config_8656'])-1)==51000<65535
    assert 'SPentry-4' in words and 'SPentry-12' in words and 'SPentry-8' in words
    assert 'same-address byte-counter +1' in words and 'native width and signedness remain unset' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==34
    assert 'Adapter35' in words and '68 preceding generated outputs' in words
    assert len(proof_adapter.DESCRIPTORS[:proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)])==34
