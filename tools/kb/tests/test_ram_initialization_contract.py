"""Exact clear windows retain native limits, field types and observation boundaries."""

from copy import deepcopy
import json

import pytest

from kb import ram_initialization_contract as contract,ram_initialization_matrix as matrix
from kb import ram_initialization_capture_evidence as proof,ram_clear_access_contract as owning,repo


def test_exact_five_stock_paths_keep_their_instruction_bytes_and_full_last_stores():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    restored=bytearray(fixture)
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    for row in contract.RETURNS:restored[row['address']:row['address']+4]=image[row['address']:row['address']+4]
    assert bytes(restored)==image
    assert len(declared['window'])==5
    assert {row['parent'] for row in declared['window']}=={0x27AC0,0x27C50,0x2FC24,0x34B70,0x26F30}
    assert declared['instruction_budget']==34484
    for window in declared['window']:
        assert fixture[window['start']:window['end']]==image[window['start']:window['end']]
        assert (window['limit']-window['first'])%4==2


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_never_admits_boot_reset_geometry_or_hardware(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('fault',('budget','range','loop-size','window','boolean-budget'))
def test_instruction_budget_is_bound_to_this_exact_stock_family(fault):
    declared=deepcopy(contract.descriptor(repo.ROOT))
    if fault=='budget':declared['instruction_budget']+=1
    elif fault=='range':declared['window'][0]['limit']+=4
    elif fault=='loop-size':declared['window'][0]['loop_steps']+=1
    elif fault=='window':declared['id']='another-family'
    else:declared['instruction_budget']=True
    with pytest.raises(ValueError):contract.oracle_budget(declared)


def test_complete_seed_matrix_covers_every_window_without_zero_initialized_fields():
    declared=contract.descriptor(repo.ROOT);cases=matrix.cases(declared,b'')
    assert len(cases)==15
    for window in contract.WINDOWS:
        selected=[row for row in cases if row['entry']==window['start']]
        assert {row['seed'] for row in selected}=={0x25,0xA5,0xFF}
        for case in selected:
            assert matrix.context(declared,case)[15]==window['gbr']
            assert len(matrix.memory(case))==65536 and set(matrix.memory(case))=={case['seed']}


@pytest.mark.parametrize('index,physical_end',((0,0x4514),(1,0x261C),(2,0x5CF4),(3,0x5CF4),(4,0x5CF4)))
def test_complete_range_equation_retains_neighbors_and_final_two_tail_bytes(index,physical_end):
    before=bytes([0xA5])*65536
    expected,first,end=proof.range_equation(contract.WINDOWS[index],before)
    assert end==physical_end
    assert expected[:first]==before[:first] and expected[end:]==before[end:]
    assert expected[first:end]==bytes(end-first)
    limit=contract.WINDOWS[index]['limit']&65535
    assert expected[limit:end]==b'\0\0'
    assert expected[first-1]==expected[end]==0xA5


def test_joint43_documents_preserve_all_native_semantic_types_and_shared_postimages():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==43 and len({row['owner'] for row in rows})==17
    assert sum(row['function']==0x27AC0 for row in rows)==9
    assert sum(row['function']==0x27C50 for row in rows)==7
    assert sum(row['function']==0x2FC24 for row in rows)==13
    assert sum(row['function']==0x34B70 for row in rows)==13
    assert sum(row['function']==0x26F30 for row in rows)==1
    for row in rows:
        assert row['direction']=='writer' and row['width_bytes']==4
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        assert before.get('ledger')==after.get('ledger')
        assert before['symbol']==after['symbol']
        if row['owner']=='spectacular-seahorse/ram':
            assert (row['declared_width'],row['declared_signed'])==(16,'unset')
        elif row['owner']=='wondrous-sparrow/ram':
            assert (row['declared_width'],row['declared_signed'])==(16,False)
        else:assert (row['declared_width'],row['declared_signed'])==('unset','unset')
    for owner in {row['owner'] for row in rows}:
        group=[row for row in rows if row['owner']==owner]
        assert len({row['original_native_json'] for row in group})==1
        assert len({row['proposed_native_json'] for row in group})==1


def test_documented_counts_and_addresses_follow_the_executed_descriptors():
    rows=owning.descriptor(repo.ROOT)['reference']
    text=(repo.ROOT/'defs/JK08A.ram-initialization.md').read_text()
    assert f'{len(rows)} existing writer' in text
    assert f'{len({row["owner"] for row in rows})} complete owner' in text
    for window in contract.WINDOWS:
        assert f'`{window["parent"]:08X}`' in text
        assert f'`{window["start"]:08X}`' in text
    for path in ('tools/kb/README.md','tools/sh-elf-run/README.md'):
        text=(repo.ROOT/path).read_text()
        assert str(len(rows))+' '+('exact writer' if path=='tools/kb/README.md' else 'owning') in text


def test_documented_indirect_modes_follow_the_runtime_vocabulary():
    import re
    from kb import vocab
    text=(repo.ROOT/'tools/kb/SPEC.md').read_text()
    row=next(line for line in text.splitlines() if line.startswith('| `mode` | For `indirect`:'))
    assert tuple(re.findall(r'`([^`]+)`',row)[2:])==vocab.INDIRECT_MODES
