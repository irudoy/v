"""Original raw state, physical inputs and bounded terminals govern admission."""

import copy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import learning_transfer_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['learning_transfer_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original learned-grid capture')
        pytest.skip('the complete original learned-grid capture is unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    assert result['exact_learning_transfers'] is True
    return model, record, packet


def refuse(original, packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0], packet, original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field', ('declaration', 'consumed', 'reconstruction', 'aliases',
                                  'boundaries', 'observations', 'simulator', 'toolchain'))
def test_missing_physical_or_terminal_input_refuses(original, field):
    packet = dict(original[2])
    packet.pop(field)
    refuse(original, packet)


@pytest.mark.parametrize('returncode,limit', ((1, 1200), (0, 0), (0, 1201)))
def test_failed_or_changed_original_terminal_refuses(original, returncode, limit):
    packet = copy.deepcopy(original[2])
    packet['simulator'].update(returncode=returncode, timeout_seconds=limit)
    refuse(original, packet)


@pytest.mark.parametrize('field', ('context', 'context_after', 'observation', 'calibration_before', 'calibration_after'))
def test_changed_actual_state_refuses_even_with_consistent_stream_hash(original, field):
    packet = copy.deepcopy(original[2])
    actual = packet['observations']
    row = actual[0]
    raw = bytearray.fromhex(row[field])
    if raw:
        raw[0] ^= 1
    else:
        raw.append(1)
    row[field] = raw.hex()
    lines = packet['stdout'].splitlines(keepends=True)
    position = next(index for index, line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position] = proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n'
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original, packet)


def test_missing_common_original_component_refuses(original):
    record = copy.deepcopy(original[1])
    record['candidate']['witness'].pop('learning_transfer_paths')
    with pytest.raises(ValueError):
        proof.require_primary(original[0], record)


@pytest.mark.parametrize('field', ('ram_before', 'ram_after'))
def test_changed_unrelated_ram_refuses_with_consistent_stream_hash(original, field):
    from kb import width_view_matrix
    packet = copy.deepcopy(original[2])
    row = packet['observations'][0]
    memory = bytearray(width_view_matrix.decode_rle(row[field]))
    memory[0x1234] ^= 1
    parts, start = [], 0
    while start < len(memory):
        end = start + 1
        while end < len(memory) and memory[end] == memory[start]:
            end += 1
        parts.append(f'{end - start}:{memory[start]:02x}')
        start = end
    row[field] = ','.join(parts)
    lines = packet['stdout'].splitlines(keepends=True)
    position = next(index for index, line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position] = proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n'
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original, packet)


def rewrite_observations(packet):
    iterator = iter(packet['observations'])
    lines = []
    for line in packet['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row = next(iterator, None)
            if row is not None:
                lines.append(proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n')
        else:
            lines.append(line)
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()


@pytest.mark.parametrize('fault', ('omit', 'duplicate', 'swap', 'wrong-entry', 'wrong-role', 'wrong-index'))
def test_changed_invocation_set_refuses_with_consistent_raw_stream(original, fault):
    packet = copy.deepcopy(original[2])
    rows = packet['observations']
    if fault == 'omit':
        rows.pop()
    elif fault == 'duplicate':
        rows[-1] = copy.deepcopy(rows[0])
    elif fault == 'swap':
        rows[0], rows[-1] = rows[-1], rows[0]
    elif fault == 'wrong-entry':
        rows[0]['entry'] = 0x5796E
    elif fault == 'wrong-role':
        rows[0]['kind'] = 2
    else:
        rows[0]['index'] = True
    rewrite_observations(packet)
    refuse(original, packet)


@pytest.mark.parametrize('fault',('unit','missing-unit','code','pool','alias','return','fixture',
    'observer','header','selection-source','learning-source','input-source','command'))
def test_changed_unit_or_private_executable_input_refuses(original,fault):
    packet=copy.deepcopy(original[2])
    if fault=='unit':packet['reconstruction'][0],packet['reconstruction'][1]=packet['reconstruction'][1],packet['reconstruction'][0]
    elif fault=='missing-unit':packet['reconstruction'].pop()
    elif fault in ('code','pool'):
        selected=packet['reconstruction'][0]['code' if fault=='code' else 'pools'][0]
        selected['reconstructed']='00'+selected['reconstructed'][2:]
    elif fault=='alias':packet['aliases'][0]['alias']+=4
    elif fault=='return':packet['boundaries']=[dict(address=0x58168,bytes='000b0009')]
    elif fault=='fixture':packet['fixture_sha256']='0'*64
    elif fault=='command':packet['simulator']['command'][1]='--memory-region=0x01000000,32k'
    else:
        name={'observer':proof.OBSERVER,'header':proof.HEADER,
            'selection-source':'stock_jk08a_grid_selection.s','learning-source':'stock_jk08a_grid_learning.s',
            'input-source':'stock-jk08a-grid-learning-cases.h'}[fault]
        packet['consumed'][name]+='00'
    refuse(original,packet)


@pytest.mark.parametrize('source',('tools/kb/src/kb/learning_transfer_contract.py',
    'tools/kb/src/kb/learning_transfer_matrix.py','tools/kb/src/kb/learning_transfer_semantics.py',
    'tools/kb/src/kb/learning_transfer_capture_evidence.py','tools/sh-elf-run/harness-learning-transfers.c',
    'tools/sh-elf-run/stock_jk08a_grid_selection.s','tools/sh-elf-run/stock_jk08a_grid_learning.s',
    'tools/sh-elf-run/stock-jk08a-grid-selection-cases.h','tools/sh-elf-run/stock-jk08a-grid-learning-cases.h'))
def test_stale_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_entries(original):
    from kb import learning_transfer_contract as contract
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared);selected={}
    for kind in ('selection','learning','auxiliary'):
        for bank in (0,1):
            case=next(row for row in declared['cases'] if row['kind']==kind and row['argument']==bank
                and (row['cell']==23039 if kind=='selection' else row['cell_index']==0))
            observed=observations[case['index']]
            result,_=proof.require_state(declared,image,fixture,case,observed)
            selected[kind,bank]=(case,observed,result)
    return declared,image,fixture,selected


@pytest.mark.parametrize('kind',('selection','learning','auxiliary'))
@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('fault',('input','output','sibling','outside','context','frame','pr','abi','sp','continuation','calibration'))
def test_each_natural_entry_refuses_changed_datum_or_complete_state(actual_entries,kind,bank,fault):
    declared,image,fixture,selected=actual_entries
    case,original,_=selected[kind,bank];observed=copy.deepcopy(original)
    if fault in ('input','output','sibling','outside'):
        key='memory_before' if fault=='input' else 'memory_after'
        at=(0x1024 if kind=='selection' else 0x134E+bank*2) if fault=='input' else (0x4B10 if bank else 0x4B90)
        if fault=='output' and kind=='auxiliary':at=0x49B0 if bank else 0x49F0
        if fault=='sibling':at=0x4B90 if bank else 0x4B10
        elif fault=='outside':at=0x1234
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='context':
        values=list(observed['context']);values[4]^=1;observed['context']=tuple(values)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('pr','abi'):
        key='exit' if fault=='pr' else 'abi_after';values=list(observed[key]);values[1]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        at=next(iter(observed['calibration_before']));data=bytearray(observed['calibration_before'][at]);data[0]^=1
        observed['calibration_before'][at]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('kind,fault',[(kind,fault) for kind in ('selection','learning','auxiliary')
    for fault in ('site','width','direction','address','bytes','extra-call','missing-call','bank-argument')
    if kind!='auxiliary' or fault not in ('missing-call','bank-argument')])
def test_actual_transfer_or_post_delay_call_mutation_refuses(actual_entries,kind,fault):
    _,image,_,selected=actual_entries
    case,observed,original=selected[kind,1];result=copy.deepcopy(original)
    if fault=='extra-call':result['calls'].append(dict(site=0x58164,target=0x58092))
    elif fault in ('missing-call','bank-argument'):
        assert result['calls']
        if fault=='missing-call':result['calls'].pop()
        else:
            call=next(row for row in result['calls'] if row['target']==0x580E8)
            values=list(call['entry']['registers']);values[6]^=1;call['entry']['registers']=tuple(values)
    else:
        row=next(row for row in result['accesses'] if row['site'] in proof.WATCHED)
        if fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']*=2
        elif fault=='direction':row['mode']='write' if row['mode']=='read' else 'read'
        elif fault=='address':row['address']+=1
        else:row['bytes']='00'+row['bytes'][2:] if row['bytes'][:2]!='00' else '01'+row['bytes'][2:]
    with pytest.raises(ValueError):proof.semantic(case,observed,result,image)
