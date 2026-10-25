"""Natural uptight-duck entry: the lookup is published, not divided."""

import pytest
from kb import compile,repo
from kb import uptight_duck_contract as contract, uptight_duck_matrix as matrix, uptight_duck_semantics as numeric
from kb import uptight_duck_argument_contract as arguments
from kb.model import SymbolKey


def test_uptight_duck_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0xB784E and contract.DIVISOR==0xF4240
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_uptight_duck_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_signed_call_keeps_the_incoming_dividend_while_the_curve_changes_publication():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=matrix.cases(declared,image)
    varied=next(case for case in cases if case['pattern']=='constant' and case['axis']=='strict' and case['coordinate']==150)
    replaced=next(case for case in cases if case['threshold']==150)
    published=numeric.caller(matrix.calibrations(declared,image,varied),matrix.memory(varied),varied['dividend'],varied['coordinate'])
    constant=numeric.caller(matrix.calibrations(declared,image,replaced),matrix.memory(replaced),replaced['dividend'],replaced['coordinate'])
    assert published['divisor']==0xF4240 and published['dividend']==varied['dividend']
    assert published['chosen']==published['third']['value']==1000
    assert constant['chosen']==1 and constant['dividend']==replaced['dividend']
    assert published['fault']==constant['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_the_constant_divisor_and_the_lookup():
    text=(repo.ROOT/'defs/JK08A.uptight-duck.md').read_text()
    for address in (0xB784E,0x15C80,0x13CA8,0x26524,0xB7892,0xB7894,0x21BBC):
        assert f'`{address:08X}`' in text
    assert '`000F4240`' in text and '`FFFF9818`' in text


def test_pinned_disposition_matches_the_current_signed_reader_claim():
    model=compile.build(repo.ROOT)
    row=arguments.descriptor(repo.ROOT)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
              and item.to.key==arguments.TARGET)
    assert arguments.original(row,link)
    assert row['component']=='uptight_duck_paths'



def test_all_original_eleven_case_records_and_complete_contexts_remain_exact():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    original=(('last','strict',150,5000000,0,'stock'),('rising','strict',150,5000000,0,'stock'),
        ('constant','strict',150,5000000,0,'stock'),('zero','strict',150,5000000,0,'stock'),
        ('stock','stock',0,0,0,'stock'),('stock','stock',1000,0xFFFFFFFF,0,'stock'),
        ('last','strict',0,0,150,'stock'),('constant','high',0,0,0,'stock'),
        ('rising','strict',3100,50000000,0,'stock'),('last','strict',50,1000000,0,'stock'),
        ('stock','stock',0,0,0,'last'))
    assert len([row for row in rows if 'fifth_word' not in row])==len(original)==11
    for index,(pattern,axis,coordinate,dividend,threshold,side) in enumerate(original):
        sr=(index&1)|((index&15)<<4)|((index&3)<<8)
        expected=dict(index=index,entry=contract.ENTRY,pattern=pattern,axis=axis,side=side,
            coordinate=coordinate,dividend=dividend,threshold=threshold,variant=index%4,sr=sr)
        assert rows[index]==expected
        registers=[(0x1728394A+reg*0x110203+(index%4)*0x1000101)&0xFFFFFFFF for reg in range(15)]
        registers[4:7]=[dividend,coordinate,matrix.POINTER]
        assert matrix.context(source,rows[index])==(*registers,0x12344321,0x13579BDF,0x2468ACE0,sr,0xB6C70000|coordinate)


def test_coordinate_contrasts_hold_every_other_raw_context_RAM_and_calibration_input_fixed():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=[row for row in matrix.cases(source,image) if 'fifth_word' in row and 'prior3348' not in row]
    coordinates={row['coordinate'] for row in rows}
    assert set(range(0,3101,100))<=coordinates and set(range(50,3100,100))<=coordinates
    assert {0,1,32767,32768,65534,65535}<=coordinates
    held=[]
    for row in rows:
        context=list(matrix.context(source,row));assert context[5]==row['coordinate'];context[5]=0
        assert context[19]==0xA5B6C7D8
        held.append((context,matrix.memory(row),matrix.calibrations(source,image,row)))
    assert rows and all(value==held[0] for value in held)
    text=(repo.ROOT/'defs/JK08A.uptight-duck.md').read_text()
    assert '11 original cases' in text and 'fixed fifth word' in text


@pytest.mark.parametrize('value',(True,-1,0x100000000))
def test_coordinate_inputs_refuse_a_truncated_or_boolean_fifth_word(value):
    with pytest.raises(ValueError):matrix.fifth_word(dict(coordinate=0,fifth_word=value))


def test_prior_RAM3348_definitions_change_only_the_four_explicit_bytes_in_each_publication_mode():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    groups={}
    for case in matrix.cases(source,image):
        if 'prior3348' not in case:continue
        before=matrix.memory(case)
        assert int.from_bytes(before[0x3348:0x334C],'big')==case['prior3348']
        key=case['side'],case['threshold']
        held=(matrix.context(source,case),before[:0x3348]+bytes(4)+before[0x334C:],
            matrix.calibrations(source,image,case))
        values,prior=groups.setdefault(key,({},held));assert prior==held
        assert case['prior3348'] not in values;values[case['prior3348']]=case
    required={0,0xFFFFFFFF,0xA5C3D2E1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,
        *(1<<bit for bit in range(32)),*((1<<bit)^0xFFFFFFFF for bit in range(32))}
    assert set(groups)=={(side,threshold) for side in ('zero','rising') for threshold in (0,255)}
    assert all(set(values)==required for values,held in groups.values())


@pytest.mark.parametrize('value',(True,-1,0x100000000))
def test_prior_RAM3348_input_refuses_boolean_or_truncated_values(value):
    with pytest.raises(ValueError):matrix.prior3348(dict(prior3348=value))
