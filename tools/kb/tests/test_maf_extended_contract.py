"""Natural reused units retain exact code, subentry calls and typed native owners."""

from copy import deepcopy

import pytest

from kb import maf_extended_contract as contract, maf_extended_matrix as matrix
from kb import maf_access_contract as owning, repo


def test_six_units_change_only_declared_literals_and_outside_code_observing_returns():
    declared = contract.descriptor(repo.ROOT)
    assert len(declared['unit']) == 6
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert {row['address'] for row in aliases} == set(contract.ALIASES)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in contract.BOUNDARIES:
        start=row['address'];size=len(bytes.fromhex(row['bytes']))
        assert fixture[start:start+size] == bytes.fromhex('57f6472a000b0009')
        assert all(not (first<start+size and start<last) for first,last in contract.SPANS)
        restored[start:start+size] = image[start:start+size]
    assert bytes(restored) == image
    for start, end in contract.SPANS:
        assert fixture[start:end] == image[start:end]
    assert 0x224FA in contract.CALL_TARGETS and 0x224F8 in contract.FUNCTIONS
    assert any(row == {'start': 0x224FA, 'end': 0x22508}
               for unit in declared['unit'] for row in unit['code'])


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_joint_native_descriptor_retains_mixed_types_and_shared_owner_postimages():
    rows = owning.descriptor(repo.ROOT)['reference']
    assert len(rows) == 34
    assert len({row['owner'] for row in rows}) == 21
    assert sum(row['component'] == 'maf_extended_paths' for row in rows) == 26
    for owner, width, signed in (('imposing-auk/ram', 32, True),
                                 ('maf_correction_state_b2/ram', 16, True),
                                 ('maf_fallback_latch_b2/ram', 8, False)):
        selected = [row for row in rows if row['owner'] == owner]
        assert selected and all((row['declared_width'], row['declared_signed']) == (width, signed)
                               for row in selected)
    shared = [row for row in rows if row['owner'] == 'spiked-dalmatian/ram']
    assert {row['direction'] for row in shared} == {'reader', 'writer'}
    assert {row['component'] for row in shared} == {'maf_copy_filter_paths', 'maf_extended_paths'}
    assert len({row['original_native_json'] for row in shared}) == 1
    assert len({row['proposed_native_json'] for row in shared}) == 1
    for owner in ('imposing-auk/ram','hairy-dalmatian/ram'):
        selected=[row for row in rows if row['owner']==owner]
        assert len(selected)==2
        assert len({row['original_native_json'] for row in selected})==1
        assert len({row['proposed_native_json'] for row in selected})==1
    for owner,count in (('maf_b1/ram',2),('maf_b2/ram',4)):
        selected=[row for row in rows if row['owner']==owner]
        assert len(selected)==count
        assert len({row['original_native_json'] for row in selected})==1
        assert len({row['proposed_native_json'] for row in selected})==1
        assert all((row['declared_width'],row['declared_signed'])==(16,False) for row in selected)
    untyped=next(row for row in rows if row['owner']=='camouflaged-cockle/ram')
    assert (untyped['width_bytes'],untyped['declared_width'],untyped['declared_signed'])==(2,'unset','unset')
    assert owning.native_type(untyped,'width') is owning.native_type(untyped,'signed') is None


def test_fixed_other_reader_pairs_keep_complete_context_and_unselected_family_bytes():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    cases = matrix.cases(declared, image)
    for kind, address, width, field in (('compensation', 0x101E, 2, 'input'),
                                       ('contribution', 0x1DF2, 2, 'input'),
                                       ('scaling', 0x1D64, 2, 'input'),
                                       ('bank-publication', 0x1DFC, 4, 'input'),
                                       ('diagnostic-copy', 0x1D64, 2, 'input')):
        case = next(row for row in cases if row['kind'] == kind and row['argument'] == 1)
        other = deepcopy(case)
        other[field] ^= 1
        assert matrix.context(declared, case) == matrix.context(declared, other)
        assert matrix.calibrations(declared, image, case) == matrix.calibrations(declared, image, other)
        first, second = bytearray(matrix.memory(case)), bytearray(matrix.memory(other))
        assert first[address:address + width] != second[address:address + width]
        first[address:address + width] = second[address:address + width]
        assert first == second


@pytest.mark.parametrize('address,field',((0x101C,'input'),(0x101E,'previous')))
def test_compensation_caller_reader_alternatives_hold_the_other_bank_and_complete_context_fixed(address,field):
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    case=next(row for row in matrix.cases(declared,image) if row['kind']=='compensation-caller')
    other=deepcopy(case);other[field]^=1
    assert matrix.context(declared,case)==matrix.context(declared,other)
    assert matrix.context(declared,case)[12:15]==(0,1,0x01001E1C)
    assert matrix.calibrations(declared,image,case)==matrix.calibrations(declared,image,other)
    first,second=bytearray(matrix.memory(case)),bytearray(matrix.memory(other))
    assert first[address:address+2]!=second[address:address+2]
    first[address:address+2]=second[address:address+2]
    assert first==second


def test_caller_windows_preserve_natural_parents_and_explicit_incoming_premises():
    declared=contract.descriptor(repo.ROOT)
    assert declared['caller']==list(contract.CALLERS)
    assert [(row['parent'],row['entry'],row['end']) for row in declared['caller']]==[
        (0x3A904,0x3A91A,0x3A922),(0x3C3AC,0x3C3B6,0x3C3BE)]
    assert declared['caller'][0]['incoming']==dict(r12=0,r13=1,r14=0x01001E1C)
    assert declared['caller'][1]['incoming']=={}
    assert len(declared['natural_entries'])==8
    assert all(row['return_register']==7 and row['stack_return_offset']==24 for row in declared['boundary'])


@pytest.mark.parametrize('old,new',(('r12 = 0','r12 = 1'),('r13 = 1','r13 = 0'),
    ('r14 = 16784924','r14 = 16784928'),('entry = 239898','entry = 239900'),
    ('address = 239906','address = 239908'),('return_register = 7','return_register = 6'),
    ('stack_return_offset = 24','stack_return_offset = 20')))
def test_descriptor_refuses_changed_caller_or_observing_return_premise(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    assert old in text
    path.write_text(text.replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_document_names_actual_calls_and_preserved_semantic_types():
    text = (repo.ROOT / 'defs/JK08A.maf-extended.md').read_text()
    for address in (0x3AE8A, 0x3AF42, 0x3C408, 0x224FA, 0x21CE0, 0x67188, 0x671D8,
                    0x3B224,0x3B234,0x3B250,0x3C45C,0x3C466,0x3C46E,
                    0x3A904,0x3A91A,0x3A922,0x3C3AC,0x3C3B6,0x3C3BE):
        assert f'`{address:08X}`' in text
    assert 'signed 32-bit' in text and 'signed 16-bit' in text and '8-bit' in text
    rows=owning.descriptor(repo.ROOT)['reference']
    assert f'all {len(rows)} exact original claims' in text
    assert f'joint {len(rows)}-access batch' in (repo.ROOT/'tools/sh-elf-run/README.md').read_text()
    assert f'bind {len(rows)} exact accesses' in (repo.ROOT/'tools/kb/README.md').read_text()
    assert f'uses {len(rows)} exact ordinary `link`' in (repo.ROOT/'tools/kb/SPEC.md').read_text()
