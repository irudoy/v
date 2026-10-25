"""Actual-original refusals for complete ignition diagnostic physical and state inputs."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence,width_view_matrix
from kb import ignition_diagnostic_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['ignition_diagnostic_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its original complete ignition diagnostic record')
        pytest.skip('the original complete ignition diagnostic record is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['ROM_to_DID_dependency_inference'] is False
    assert result['native_geometry_inference'] is False
    assert set(result['conditional_branch_outcomes'])=={f'{site:08x}' for site in proof.REQUIRED_BRANCHES}
    return model,record,packet


def refuse(original,packet):
    model,record,_=original
    with pytest.raises(ValueError):
        proof.require_witness(model,packet,record['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('consumed','reconstruction','aliases','boundaries','image_sha256',
    'fixture_sha256','elf_sha256','observer_object_sha256','simulator','declaration','observations','stub_reconstruction'))
def test_original_ignition_diagnostic_physical_inputs_cannot_be_omitted(original,field):
    packet=dict(original[2])
    packet.pop(field)
    refuse(original,packet)


@pytest.mark.parametrize('fault',('layout','entry','helper-stub','scale','DID-inference','missing-pool',
    'source','alias-byte','boundary','failed-simulator','timeout-bound','self-admission'))
def test_original_ignition_diagnostic_bindings_and_limits_cannot_be_substituted(original,fault):
    packet=dict(original[2])
    if fault in ('layout','entry','helper-stub','scale','DID-inference','missing-pool'):
        declared=deepcopy(packet['declaration'])
        packet['declaration']=declared
        if fault=='layout':declared['layout']='1nd'
        elif fault=='entry':declared['source']['entry'][0]['start']+=2
        elif fault=='helper-stub':declared['source']['stock_function_stubs']=True
        elif fault=='scale':declared['source']['scale_admission']=True
        elif fault=='DID-inference':declared['ROM_to_DID_dependency_inference']=True
        else:declared['source']['pool'].pop()
    elif fault=='source':packet['consumed']={**packet['consumed'],proof.OBSERVER:'000b0009'}
    elif fault=='alias-byte':packet['aliases']=[{**row,'alias':row['alias']+1} for row in packet['aliases']]
    elif fault=='boundary':packet['boundaries']=[dict(address=0x4E07C,bytes='000b0009')]
    elif fault=='failed-simulator':packet['simulator']={**packet['simulator'],'returncode':4}
    elif fault=='timeout-bound':packet['simulator']={**packet['simulator'],'timeout_seconds':False}
    else:packet['semantic_admission']=True
    refuse(original,packet)


def encode(memory):
    result=[]
    start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        result.append(f'{end-start}:{memory[start]:02x}')
        start=end
    return ','.join(result)


@pytest.mark.parametrize('field,offset',(
    ('context',28),('context',60),('context',64),('context',68),('context',75),('context',79),
    ('context_after',28),('observation',2),('observation',3),('observation',7),('observation',11),
    ('observation',15),('observation',51),('observation',83),('observation',183),
    ('observation',375),('observation',567),('calibration_before',0),('calibration_after',0),
    ('ram_before',0x237E),('ram_before',0x24C0),('ram_after',0x12D6),('native_before',0xC4),('native_after',0x26),('ram_after',0x1234)))
def test_consistent_original_stream_cannot_replace_independent_full_state_or_calibration_equations(original,field,offset):
    held=original[2]
    packet=dict(held)
    row=dict(held['observations'][0])
    if field.startswith('ram_'):
        value=bytearray(width_view_matrix.decode_rle(row[field]))
        value[offset]^=1
        row[field]=encode(value)
    else:
        value=bytearray.fromhex(row[field])
        value[offset]^=1
        row[field]=value.hex()
    packet['observations']=[row,*held['observations'][1:]]
    lines=held['stdout'].splitlines()
    position=next(index for index,line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position]=proof.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)


@pytest.mark.parametrize('fault',('missing','wrong-original','failed-terminal','partial-cases','reordered-cases'))
def test_ignition_diagnostic_paths_require_the_same_complete_successful_original_primary(original,fault):
    model,held,_=original
    record={**held,'candidate':dict(held['candidate']),'terminal':dict(held['terminal'])}
    if fault=='missing':
        record['candidate']['witness']={key:value for key,value in held['candidate']['witness'].items() if key!='ignition_diagnostic_paths'}
    elif fault=='wrong-original':record['process_sha256']='0'*64
    elif fault=='failed-terminal':record['terminal']['actual_exit_code']=1
    else:
        packet=dict(held['candidate']['witness']['ignition_diagnostic_paths'])
        rows=list(packet['observations'])
        if fault=='partial-cases':rows.pop()
        else:rows[0],rows[1]=rows[1],rows[0]
        packet['observations']=rows
        record['candidate']['witness']={**held['candidate']['witness'],'ignition_diagnostic_paths':packet}
    with pytest.raises(ValueError):
        proof.require_primary(model,record)


@pytest.mark.parametrize('fault',('owner','layout','width','function-anchor'))
def test_current_native_binding_cannot_be_substituted_by_an_unrelated_fact(original,fault):
    from copy import copy
    from kb.model import SymbolKey
    model=copy(original[0])
    model.symbols=dict(model.symbols)
    key=SymbolKey('7mfk','ram',0xFFFF2022)
    if fault=='function-anchor':
        model.functions={**model.functions,'7mfk':frozenset(model.functions['7mfk'])-{0x4D99C}}
    elif fault=='layout':
        model.symbols.pop(key)
    else:
        symbol=copy(model.symbols[key])
        symbol.props=dict(symbol.props)
        model.symbols[key]=symbol
        if fault=='owner':
            symbol.meaning=copy(symbol.meaning)
            symbol.meaning.name='unrelated-controlled-table'
        else:symbol.props['width']=True
    with pytest.raises(ValueError):proof.native_bindings(model)


def test_curve_ownership_cannot_be_replaced_by_an_unrelated_table_at_the_same_address(original):
    from copy import copy
    from kb.model import SymbolKey
    model=copy(original[0])
    model.symbols=dict(model.symbols)
    key=SymbolKey('7mfk','tbl',0x147DA)
    symbol=copy(model.symbols[key])
    symbol.meaning=copy(symbol.meaning)
    symbol.meaning.name='unrelated-controlled-curve'
    model.symbols[key]=symbol
    with pytest.raises(ValueError):proof.native_bindings(model)


def replace_observation(held,index,row):
    packet=dict(held)
    packet['observations']=[*held['observations'][:index],row,*held['observations'][index+1:]]
    lines=held['stdout'].splitlines()
    positions=[position for position,line in enumerate(lines) if line.startswith(proof.PREFIX)]
    lines[positions[index]]=proof.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    return packet


@pytest.mark.parametrize('stage',(1,2))
def test_sequenced_stages_cannot_reset_RAM_between_natural_calls(original,stage):
    from kb import ignition_diagnostic_matrix as matrix
    held=original[2]
    row=dict(held['observations'][stage])
    case=held['declaration']['cases'][stage]
    initial=matrix.initial_memory(case)
    assert width_view_matrix.decode_rle(row['ram_before'])!=initial
    row['ram_before']=encode(initial)
    row['native_before']=matrix.native_controls(initial).hex()
    refuse(original,replace_observation(held,stage,row))


@pytest.mark.parametrize('fault',('missing-region','wrong-native-region','stock-body','sink-byte','sink-source'))
def test_native_control_window_and_post_store_scheduler_scope_are_exact(original,fault):
    held=original[2]
    packet=dict(held)
    if fault in ('missing-region','wrong-native-region'):
        simulator={**held['simulator'],'command':list(held['simulator']['command'])}
        packet['simulator']=simulator
        if fault=='missing-region':simulator['command'].pop(2)
        else:simulator['command'][2]='--memory-region=0xffff9900,512'
    elif fault=='stock-body':
        packet['boundaries']=[{**row,'stock_body_admitted':True} for row in held['boundaries']]
    else:
        stub={**held['stub_reconstruction']}
        packet['stub_reconstruction']=stub
        if fault=='sink-byte':stub['bytes']='e001000b0009'
        else:stub['source_sha256']='0'*64
    refuse(original,packet)
