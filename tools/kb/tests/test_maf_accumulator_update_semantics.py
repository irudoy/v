"""Exact counter wrap, unsigned products and physical byte-curve boundary equations."""
from copy import deepcopy
from kb import repo,maf_accumulator_update_contract as contract
from kb import maf_accumulator_update_semantics as numeric
from kb import maf_accumulator_update_matrix as matrix
def case(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='complete-source-refusal')
    value.update({row['name']:image[row['address']:row['address']+row['size']]
                  for row in contract.DECLARED['input_blobs']})
    value.update(changes)
    return value


def equations(**changes):
    value=case(**changes)
    return numeric.caller(matrix.memory(value),matrix.input_calibrations(value),matrix.context({},value))


def test_counter_latch_wraps_before_the_actual_byte_store():
    value=equations(phase_second=2,count_latched=0,call_count=0,rom_829e=5)
    assert value['memory'][0x3989]==251
    assert value['divisor']==263


def test_full_uint32_decay_and_initialization_precedence():
    for old,wanted in ((0,0),(1,0),(0xFFFFFFFF,0xFFFEFFFF)):
        value=equations(accumulator=old,rom_9410=65535,phase_first=0,scaled=2)
        assert value['value']==wanted and value['branch']=='decay'
    init=equations(initialized=0,enabled=0,rom_95b6=65535)
    assert init['value']==0xFFFF0000 and init['branch']=='initialize'
    zero=equations(initialized=2,enabled=0)
    assert zero['value']==0 and zero['branch']=='zero'


def test_real_zero_divisor_bypasses_both_calls_and_selects_byte255():
    value=equations(latched_count=0,rom_8a4c=0,phase_first=0,phase_second=0,count_latched=2)
    assert value['divisor']==0 and value['first_quotient'] is value['second_quotient'] is None
    assert value['mean']==value['memory'][0x397A]==255


def test_curve_keeps_guard_reads_and_exact_endpoints_without_weighting_the_guard():
    axis=bytes(range(0,256,32));values=bytes((*range(0,256,32),255))
    assert numeric.byte_curve(values,axis,255)==dict(index=7,fraction=0,first=224,last=255,value=224)
    assert numeric.byte_curve(values,axis,16)==dict(index=0,fraction=32768,first=0,last=32,value=16)
    decreasing=bytes(reversed(values))
    assert numeric.byte_curve(decreasing,axis,16)['value']==240
    repeated=numeric.byte_curve(values,bytes(8),255)
    assert repeated['index']==7 and repeated['fraction']==0


def test_output_equations_preserve_the_other_bank_and_neighbor_bytes():
    value=case();before=matrix.memory(value);after=equations()['memory']
    for first,last in ((0x3998,0x399C),(0x397C,0x3980),(0x101C,0x101E),(0x3A1E,0x3A1F)):
        assert after[first:last]==before[first:last]
