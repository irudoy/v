"""Published accumulator counts, exact aliases and complete typed input refusals."""
from copy import deepcopy
import re
import pytest
from kb import repo
from kb import maf_accumulator_update_contract as contract, maf_accumulator_update_matrix as matrix


def case(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='complete-source-refusal')
    value.update({row['name']:image[row['address']:row['address']+row['size']]
                  for row in contract.DECLARED['input_blobs']})
    value.update(changes)
    return value


def test_published_counts_and_controls_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.maf-accumulator-update.md').read_text()
    numbers=re.search(r'(\d+) instructions in (\d+) functions, (\d+) code spans, (\d+) literal pools,\s*'
                      r'(\d+) RAM pointer aliases and (\d+) calibration spans',text)
    counts=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(contract.FUNCTIONS),
            len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),
            len(source['controlled_calibration']))
    assert numbers is not None and tuple(map(int,numbers.groups()))==counts==(774,6,9,27,8,42)
    root_count=sum((min(r['end'],0x3AE8A)-max(r['start'],0x3AA12))//2
                   for r in source['unit']['code'] if r['start']<0x3AE8A and r['end']>0x3AA12)
    assert int(re.search(r'binds (\d+) root instructions',text)[1])==root_count==514
    assert int(re.search(r'root uses (\d+) stack bytes',text)[1])==source['root_stack_bytes']==56
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==11
    assert int(re.search(r'(\d+) complete curve blobs',text)[1])==len(source['input_blobs'])==4
    assert source['actual_output']==dict(base=0xFFFF3998,stride=4,address=0xFFFF399C,width_bytes=4,
                                        sites=[0x3AD8A,0x3AE1A,0x3AE74])
    assert source['entries']==[0x3AA12] and source['natural_GBR']==0xFFFF3968
    assert source['complete_existing_MAF_originals_required_same_primary'] is True
    assert source['complete_unsigned_division_original_required_same_primary'] is True


def test_only_declared_complete_pointer_aliases_change_the_fixture():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    changed={i for i,(a,b) in enumerate(zip(image,fixture)) if a!=b}
    assert changed<={at for row in aliases for at in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert any(row['original']==0xFFFF3968 for row in aliases)
    altered=bytearray(image);altered[0x3AA12]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(altered))


@pytest.mark.parametrize('fault',('bool-long','wide-long','wide-byte','short-curve','short-context',
    'other-index','bool-index','bad-SR','supplied-output'))
def test_raw_inputs_refuse_missing_state_and_supplied_results(fault):
    value=case()
    if fault=='bool-long':value['accumulator']=True
    elif fault=='wide-long':value['accumulator']=1<<32
    elif fault=='wide-byte':value['rom_829e']=256
    elif fault=='short-curve':value['mean_values']=bytes(8)
    elif fault=='short-context':value['context'].pop()
    elif fault=='other-index':value['context'][4]=0
    elif fault=='bool-index':value['context'][4]=True
    elif fault=='bad-SR':value['context'][18]=2
    else:value['expected_accumulator']=1
    with pytest.raises(ValueError):matrix.require_case(value)


def test_header_carries_only_complete_inputs_and_no_supplied_outputs():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=case();header=matrix.header(dict(source=source,cases=[value]),image).decode()
    assert 'struct context context' in header and 'maf_accumulator_calibration_blobs' in header
    assert all(word not in header for word in ('expected_accumulator','computed_factor','supplied_result'))
