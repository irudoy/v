"""Exact stock caller scope, complete raw inputs and source-bound refusal controls."""
from copy import deepcopy
import pytest
from kb import repo
from kb import map_bias_division_caller_withdrawal_contract as contract
from kb import map_bias_division_caller_withdrawal_matrix as matrix


def raw_case(**changes):
    return dict(matrix.DEFAULTS,entry=0x702C6,index=0,kind='controlled-source',**changes)


def test_complete_nine_function_source_and_existing_observer_read_the_executed_descriptor():
    declared=contract.descriptor(repo.ROOT)
    assert contract.ENTRIES==(0x702C6,)
    assert set(contract.FUNCTIONS)=={0x702C6,0x22590,0x262E0,0x26A0C,0x26984,0x26848,0x26740,0x26C78,0x21CE0}
    assert len(declared['unit']['code'])==9
    assert sum((row['end']-row['start'])//2 for row in declared['unit']['code'])==453
    assert len(declared['unit']['pools'])==21 and len(declared['unit']['aliases'])==3
    assert len(declared['controlled_calibration'])==25
    assert len(declared['adapter']['fields'])==len(matrix.WIDTHS)==308
    assert (declared['context_bytes'],declared['frame_bytes'],declared['frame_prefix'])==(80,192,160)
    assert declared['observer']=='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
    assert {row['address'] for row in declared['unit']['aliases']}=={0x21DC8,0x704B0,0x704C8}
    assert declared['stock_function_stubs'] is False and declared['native_publication'] is False


@pytest.mark.parametrize('fault',('entry','extra-entry','body','pool','alias','observer','flag','field','selected-width'))
def test_exact_declaration_refuses_scope_code_pool_alias_ABI_or_input_substitution(monkeypatch,fault):
    value=deepcopy(contract.DECLARED)
    if fault=='entry':value['entries'][0]=0x22590
    elif fault=='extra-entry':value['entries'].append(0x22590)
    elif fault=='body':value['unit']['code'][-1]['end']-=2
    elif fault=='pool':value['unit']['pools'][0]['stock_hex']='00000000'
    elif fault=='alias':value['unit']['aliases'][0]['alias']+=4
    elif fault=='observer':value['frame_bytes']=160
    elif fault=='flag':value['native_geometry_inference']=True
    elif fault=='field':value['adapter']['fields'].pop()
    else:next(row for row in value['configuration'] if row['field']=='selected_scalar_word_942c')['size']=1
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


@pytest.mark.parametrize('fault',('bool-byte','wide-byte','wide-word','wide-dword','wide-register','bad-SR','supplied-output','wrong-root'))
def test_complete_raw_matrix_refuses_width_loss_unknown_outputs_and_changed_root(fault):
    value=raw_case()
    if fault=='bool-byte':value['byte_1880']=True
    elif fault=='wide-byte':value['axis_byte_00']=256
    elif fault=='wide-word':value['selected_scalar_word_942c']=65536
    elif fault=='wide-dword':value['dword_9818']=0x100000000
    elif fault=='wide-register':value['raw_r7']=-1
    elif fault=='bad-SR':value['initial_sr']=2
    elif fault=='wrong-root':value['entry']=0x262E0
    else:value['expected_quotient']=0
    with pytest.raises(ValueError):matrix.require_case(value)


def test_fixture_changes_only_three_four_byte_pointers_and_preserves_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    allowed={at for row in aliases for at in range(row['address'],row['address']+4)}
    assert {at for at,(before,after) in enumerate(zip(image,fixture)) if before!=after}<=allowed
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert len(aliases)==3


def test_selected_two_byte_prior_controls_neither_modify_code_nor_replace_complete_other_inputs():
    declared=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    cases=matrix.cases(declared,image)
    rows=[row for row in cases if row['kind']=='selected-two-byte-scalar-prior-only' and row['byte_18b4']==0]
    assert {row['selected_scalar_word_942c'] for row in rows}=={0,1,0x7FFF,0x8000,0xFFFE,0xFFFF}
    baseline=rows[0];before,_=contract.fixture_for_case(declared,image,baseline)
    for row in rows:
        matrix.require_case(row);after,_=contract.fixture_for_case(declared,image,row)
        assert matrix.memory(row)==matrix.memory(baseline)
        assert matrix.context(declared,row)==matrix.context(declared,baseline)
        assert {at for at,(first,last) in enumerate(zip(before,after)) if first!=last}<={0x942C,0x942D}
    assert {row['initial_sr'] for row in cases if row['kind']=='complete-QM-interrupt-T-context'}=={
        qm|interrupt|t for qm in (0,0x100,0x200,0x300) for interrupt in range(0,256,16) for t in (0,1)}


def test_adapter_remains_input_only_with_all_RAM_and_declared_physical_ROM_bytes():
    adapter=contract.descriptor(repo.ROOT)['adapter']
    assert adapter['profile']=='ordinary-80-572' and adapter['entries']==[0x702C6]
    assert {(row['offset'],row['width']) for row in adapter['memory']}=={(at,size) for name,at,size in matrix.RAM_FIELDS}
    assert len({row['name'] for row in adapter['fields']})==len(matrix.WIDTHS)
    assert {row['name']:row['bits'] for row in adapter['fields']}==matrix.WIDTHS
    assert all(not any(token in row['name'] for token in ('expected','computed','terminal','result')) for row in adapter['fields'])
