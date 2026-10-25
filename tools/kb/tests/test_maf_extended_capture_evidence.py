"""Original raw state, physical inputs and bounded terminals govern admission."""

import copy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import maf_extended_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['maf_extended_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original extended MAF capture')
        pytest.skip('the complete original extended MAF capture is unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    assert result['exact_natural_MAF_transfers'] is True
    assert result['exact_battery_coefficient_transfer'] is True
    return model, record, packet


def refuse(original, packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0], packet, original[1]['candidate']['producer_inputs'])


@pytest.fixture(scope='module')
def battery_entries(original):
    from kb import maf_extended_contract as contract
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared);selected={}
    for name,mode,coefficient,sample in (('reset',0,0,1023),('retained',0,0x7900,1023),
            ('bypass',8,0,508),('normal',8,0x8000,508),('cap',8,0xC000,684),('wrap',8,0xFFFF,1024)):
        case=next(row for row in declared['cases'] if row['kind']=='battery'
            and (row['mode'],row['coefficient'],row['input'])==(mode,coefficient,sample))
        observed=observations[case['index']]
        result,value=proof.require_state(declared,image,fixture,case,observed)
        selected[name]=(case,observed,result,value)
    return declared,image,fixture,selected


@pytest.mark.parametrize('name',('reset','retained','bypass','normal','cap','wrap'))
@pytest.mark.parametrize('fault',('raw-input','coefficient-input','mode','raw-copy','byte-copy','output',
    'coefficient-after','neighbor','frame-before','frame-after','context','abi','sp','continuation','SR',
    'PR','GBR','MACL','MACH','R0'))
def test_actual_battery_coefficient_path_requires_complete_inputs_state_outputs_and_natural_terminal(battery_entries,name,fault):
    declared,image,fixture,selected=battery_entries;case,saved,_,_=selected[name];observed=copy.deepcopy(saved)
    offsets={'raw-input':0x1D6E,'coefficient-input':0x4970,'mode':0x4252,
        'raw-copy':0x1FC4,'byte-copy':0x1FC6,'output':0x1188,'coefficient-after':0x4970,'neighbor':0x1189}
    if fault in offsets:
        key='memory_before' if fault in ('raw-input','coefficient-input','mode') else 'memory_after'
        data=bytearray(observed[key][0]);data[offsets[fault]]^=1;observed[key]=(bytes(data),)
    elif fault in ('frame-before','frame-after'):
        key='frame_before' if fault=='frame-before' else 'frame_after'
        data=bytearray(observed[key]);data[148]^=1;observed[key]=bytes(data)
    elif fault in ('context','abi'):
        key='context' if fault=='context' else 'abi_after';values=list(observed[key]);values[0]^=1;observed[key]=tuple(values)
    elif fault in ('sp','continuation'):observed[fault]^=4
    else:
        field={'SR':0,'PR':1,'MACL':2,'MACH':3,'GBR':4,'R0':19}[fault]
        values=list(observed['exit']);values[field]^=1;observed['exit']=tuple(values)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('name',('reset','retained','bypass','cap','wrap'))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','value','swap-order','final-store'))
def test_actual_battery_coefficient_path_binds_the_current_word_and_exact_ordered_physical_reads(battery_entries,name,fault):
    _,image,_,selected=battery_entries;case,observed,saved,_=selected[name];result=copy.deepcopy(saved)
    row=next(row for row in result['accesses'] if row['site']==0x671E0)
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(copy.deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=2
    elif fault=='width':row['width_bytes']=1
    elif fault=='direction':row['mode']='write'
    elif fault=='value':
        data=bytearray.fromhex(row['bytes']);data[0]^=1;row['bytes']=data.hex()
    elif fault=='swap-order':
        first=result['accesses'].index(row);other=next(i for i,value in enumerate(result['accesses']) if value['site']==0x39AC4)
        result['accesses'][first],result['accesses'][other]=result['accesses'][other],result['accesses'][first]
    else:next(row for row in result['accesses'] if row['site']==0x39AE2)['width_bytes']=2
    with pytest.raises(ValueError):proof.semantic(case,observed,result,image)


@pytest.mark.parametrize('fault',('site','target','return-address','sp','entry-sp','entry-pr','gbr','sample','pointer',
    'omit-call','extra-call','return-site','return-target','return-order'))
def test_actual_battery_real_guard_scaler_and_natural_returns_bind_post_delay_state(battery_entries,fault):
    _,image,_,selected=battery_entries;case,observed,saved,_=selected['cap'];result=copy.deepcopy(saved)
    if fault=='omit-call':result['calls'].pop()
    elif fault=='extra-call':result['calls'].append(copy.deepcopy(result['calls'][0]))
    elif fault.startswith('return-') and fault!='return-address':
        returns=[row for row in result['branches'] if row['kind']=='return']
        if fault=='return-order':
            first=result['branches'].index(returns[0]);second=result['branches'].index(returns[1])
            result['branches'][first],result['branches'][second]=result['branches'][second],result['branches'][first]
        else:returns[0]['site' if fault=='return-site' else 'target']+=2
    elif fault in ('site','target','return-address','sp'):
        key='return_address' if fault=='return-address' else fault;result['calls'][1][key]^=4
    elif fault in ('entry-sp','entry-pr','gbr'):
        key={'entry-sp':'sp','entry-pr':'pr','gbr':'gbr'}[fault];result['calls'][1]['entry'][key]^=4
    else:
        values=list(result['calls'][1]['entry']['registers']);values[4 if fault=='sample' else 5]^=1
        result['calls'][1]['entry']['registers']=tuple(values)
    with pytest.raises(ValueError):proof.semantic(case,observed,result,image)


def test_actual_guard_reset_changes_the_coefficient_before_the_scaler_read(battery_entries):
    _,image,_,selected=battery_entries;case,observed,saved,value=selected['reset'];result=copy.deepcopy(saved)
    assert value['output']==255
    row=next(row for row in result['accesses'] if row['site']==0x671E0)
    assert row['bytes']=='8000';row['bytes']=observed['memory_before'][0][0x4970:0x4972].hex()
    with pytest.raises(ValueError):proof.semantic(case,observed,result,image)


@pytest.mark.parametrize('source',('defs/JK08A.maf-extended.toml','tools/kb/src/kb/maf_extended_matrix.py',
    'tools/kb/src/kb/maf_extended_semantics.py','tools/kb/src/kb/maf_extended_capture_evidence.py',
    'tools/sh-elf-run/stock_jk08a_maf_scaling.s','tools/sh-elf-run/harness-maf-extended-paths.c'))
def test_battery_coefficient_admission_requires_its_current_complete_consumed_source(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.mark.parametrize('field', ('declaration', 'consumed', 'reconstruction', 'aliases',
                                  'boundaries', 'stub_reconstruction', 'observations', 'simulator', 'toolchain'))
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
    record['candidate']['witness'].pop('maf_extended_paths')
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
        rows[0]['entry'] = 0x3AE8C
    elif fault == 'wrong-role':
        rows[0]['kind'] = 2
    else:
        rows[0]['index'] = True
    rewrite_observations(packet)
    refuse(original, packet)


@pytest.mark.parametrize('fault', ('unit', 'missing-unit', 'code', 'pool', 'alias', 'return', 'fixture',
    'observer', 'header', 'caller-source', 'return-source', 'command'))
def test_changed_natural_unit_or_consumed_artifact_refuses(original, fault):
    packet = copy.deepcopy(original[2])
    if fault == 'unit':
        packet['reconstruction'][0], packet['reconstruction'][1] = packet['reconstruction'][1], packet['reconstruction'][0]
    elif fault == 'missing-unit':
        packet['reconstruction'].pop()
    elif fault in ('code', 'pool'):
        selected = packet['reconstruction'][0]['code' if fault == 'code' else 'pools'][0]
        selected['reconstructed'] = '00' + selected['reconstructed'][2:]
    elif fault == 'alias':
        packet['aliases'][0]['alias'] += 4
    elif fault == 'return':
        packet['boundaries'] = [{'address': 0x3AF40, 'bytes': '000b0009'}]
    elif fault == 'fixture':
        packet['fixture_sha256'] = '0' * 64
    elif fault in ('observer', 'header', 'caller-source', 'return-source'):
        name = {'observer':proof.OBSERVER,'header':proof.HEADER,
            'caller-source':'stock_jk08a_maf_callers.s',
            'return-source':'publication_inhibit_snapshot_return.s'}[fault]
        packet['consumed'][name] += '00'
    else:
        packet['simulator']['command'][1] = '--memory-region=0x01000000,32k'
    refuse(original, packet)


@pytest.mark.parametrize('source', ('tools/kb/src/kb/maf_extended_semantics.py',
                                   'tools/kb/src/kb/maf_extended_contract.py',
                                   'tools/sh-elf-run/stock_jk08a_maf_contribution.s',
                                   'tools/sh-elf-run/stock_jk08a_maf_bank_publication.s',
                                   'tools/sh-elf-run/stock_jk08a_maf_diagnostic_copy.s',
                                   'tools/sh-elf-run/stock_jk08a_maf_callers.s',
                                   'tools/sh-elf-run/publication_inhibit_snapshot_return.s'))
def test_stale_current_source_refuses(original, source):
    inputs = dict(original[1]['candidate']['producer_inputs'])
    inputs[source] = '0' * 64
    with pytest.raises(ValueError):
        proof.require_witness(original[0], original[2], inputs)


@pytest.fixture(scope='module')
def publication_entries(original):
    from kb import maf_extended_contract as contract
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    selected={}
    for kind in ('bank-publication','diagnostic-copy'):
        case=next(case for case in declared['cases'] if case['kind']==kind and case['argument']==1)
        selected[kind]=(case,observations[case['index']])
    return declared,image,fixture,selected


@pytest.mark.parametrize('kind',('bank-publication','diagnostic-copy'))
@pytest.mark.parametrize('fault',('context','input','output','frame','exit','abi','sp','extra-calibration'))
def test_actual_new_natural_entry_refuses_wrong_field_state_or_call_context(publication_entries,kind,fault):
    declared,image,fixture,selected=publication_entries
    case,original=selected[kind]
    observed=copy.deepcopy(original)
    if fault=='context':
        values=list(observed['context']);values[4]^=1;observed['context']=tuple(values)
    elif fault in ('input','output'):
        key='memory_before' if fault=='input' else 'memory_after'
        at=({'bank-publication':0x1DFC,'diagnostic-copy':0x1D64} if fault=='input'
            else {'bank-publication':0x1050,'diagnostic-copy':0x1A40})[kind]
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('exit','abi'):
        key='exit' if fault=='exit' else 'abi_after'
        values=list(observed[key]);values[0]^=1;observed[key]=tuple(values)
    elif fault=='sp':
        observed['sp']+=4
    else:
        observed['calibration_before'][0x3C476]=bytes.fromhex('07b2')
    with pytest.raises(ValueError):
        proof.require_state(declared,image,fixture,case,observed)


@pytest.fixture(scope='module')
def caller_entries(original):
    from kb import maf_extended_contract as contract
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    selected={}
    for kind in ('compensation-caller','scaling-caller'):
        case=next(row for row in declared['cases'] if row['kind']==kind and
            (row['initialized']==3 if kind=='compensation-caller' else row['mode']==0 and row['coefficient']==0))
        observed=observations[case['index']]
        result,_=proof.require_state(declared,image,fixture,case,observed)
        selected[kind]=(case,observed,result)
    return declared,image,fixture,selected


@pytest.mark.parametrize('kind',('compensation-caller','scaling-caller'))
@pytest.mark.parametrize('fault',('input-b0','input-b1','output-b0','output-b1','neighbor',
    'frame','pr','r7','abi','sp','entry'))
def test_actual_caller_observation_refuses_changed_bank_or_full_return_state(caller_entries,kind,fault):
    declared,image,fixture,selected=caller_entries
    case,original,_=selected[kind];observed=copy.deepcopy(original)
    if fault.startswith(('input-','output-')) or fault=='neighbor':
        before=fault.startswith('input-')
        key='memory_before' if before else 'memory_after'
        address=(0x101C if kind=='compensation-caller' else 0x1D62) if before else (
            0x1E48 if kind=='compensation-caller' else 0x101C)
        address=0x1234 if fault=='neighbor' else address+(2 if fault.endswith('b1') else 0)
        memory=bytearray(observed[key][0]);memory[address]^=1;observed[key]=(bytes(memory),)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[24]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('pr','r7'):
        values=list(observed['exit']);values[1 if fault=='pr' else 12]^=1;observed['exit']=tuple(values)
    elif fault=='abi':
        values=list(observed['abi_after']);values[0]^=1;observed['abi_after']=tuple(values)
    elif fault=='sp':observed['sp']+=4
    else:observed['entry']+=2
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('register',(12,13,14))
def test_compensation_caller_refuses_changed_explicit_incoming_register(caller_entries,register):
    declared,image,fixture,selected=caller_entries
    case,original,_=selected['compensation-caller'];observed=copy.deepcopy(original)
    values=list(observed['context']);values[register]^=1;observed['context']=tuple(values)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('kind',('compensation-caller','scaling-caller'))
@pytest.mark.parametrize('fault',('missing-root','missing-child','order','bank','operand','target','physical'))
def test_real_caller_paths_refuse_changed_post_delay_arguments_calls_or_physical_transfers(caller_entries,kind,fault):
    _,image,_,selected=caller_entries
    case,observed,original=selected[kind];result=copy.deepcopy(original)
    if fault=='missing-root':result['calls'].pop(0)
    elif fault=='missing-child':result['calls'].pop(1)
    elif fault=='order':result['calls'][0],result['calls'][-1]=result['calls'][-1],result['calls'][0]
    elif fault=='target':result['calls'][0]['target']+=2
    elif fault=='physical':
        transfer=next(row for row in result['accesses'] if row['site']==(0x3AEAC if kind=='compensation-caller' else 0x3C450))
        transfer['address']+=2
    else:
        call=result['calls'][0 if fault=='bank' else (1 if kind=='compensation-caller' else 2)]
        register=4 if fault=='bank' or kind=='scaling-caller' else 0
        values=list(call['entry']['registers']);values[register]^=1;call['entry']['registers']=tuple(values)
    with pytest.raises(ValueError):proof.semantic(case,observed,result,image)


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('fault',('missing','address','bytes','source','object','elf','register','offset'))
def test_actual_caller_return_requires_exact_private_assembly_and_stack_premises(original,index,fault):
    packet=copy.deepcopy(original[2])
    if fault=='missing':packet['stub_reconstruction'].pop(index)
    elif fault in ('address','bytes','source','object','elf'):
        stub=packet['stub_reconstruction'][index]
        key={'source':'source_sha256','object':'object_sha256','elf':'elf_sha256'}.get(fault,fault)
        stub[key]=stub[key]+2 if key=='address' else ('00' if key=='bytes' else 'invalid')
    else:
        packet['boundaries'][index]['return_register' if fault=='register' else 'stack_return_offset']+=4
    refuse(original,packet)
