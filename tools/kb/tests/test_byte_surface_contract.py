"""Fixture, directed numeric and natural full-state source contracts."""

import pytest

from kb import repo
from kb import byte_surface_contract as contract,byte_surface_equations as state
from kb import byte_surface_matrix as matrix,byte_surface_semantics as numeric


@pytest.fixture(scope='module')
def sources():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    return declared,image,fixture,aliases


def test_wrapping_ROM_offset_stays_outside_exact_RAM_pointer_aliases(sources):
    declared,image,fixture,aliases=sources
    assert {row['address'] for row in aliases}==set(contract.ALIASES)
    assert fixture[0xC0008:0xC000C]==image[0xC0008:0xC000C]==bytes.fromhex('ffff5773')
    assert (int.from_bytes(fixture[0xC0000:0xC0004],'big')+int.from_bytes(fixture[0xC0008:0xC000C],'big'))&0xFFFFFFFF==0x8615
    for row in declared['entry']:
        assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    reconstructed=bytearray(fixture)
    for row in aliases:reconstructed[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(reconstructed)==image


@pytest.mark.parametrize('fault',('RAM-offset','geometry','entry','stub','DID-scope','geometry-publication','caller-reachability'))
def test_descriptor_refuses_changed_executable_or_inference_scope(tmp_path,fault):
    source=(repo.ROOT/contract.DESCRIPTOR).read_text()
    original=source
    if fault=='RAM-offset':
        source=source.replace('address = 0x000c0008\nwidth_bytes = 4\nstock_value = 0xffff5773\nRAM_pointer_alias = false',
            'address = 0x000c0008\nwidth_bytes = 4\nstock_value = 0xffff5773\nRAM_pointer_alias = true')
    elif fault=='geometry':source=source.replace('rows = 8','rows = 16',1)
    elif fault=='entry':source=source.replace('start = 0x000bfdc0','start = 0x000bfdc2',1)
    else:
        key={'stub':'stock_function_stubs','DID-scope':'ROM_to_DID_dependency_inference',
             'geometry-publication':'native_geometry_changed','caller-reachability':'natural_caller_reachability'}[fault]
        source=source.replace(key+' = false',key+' = true',1)
    assert source!=original
    path=tmp_path/contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(source)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_direct_cell_sign_extension_is_separate_from_byte_value_and_fractional_return():
    axis=bytes((0,32,64,96))
    table=bytes([128])*16
    direct=numeric.surface(table,axis,axis,32,64)
    fractional=numeric.surface(table,axis,axis,33,64)
    assert direct['byte']==fractional['byte']==128
    assert direct['raw']==0xFFFFFF80 and fractional['raw']==128
    assert numeric.linear(10,0,32768)==5
    assert numeric.linear(1,0,32768)==1
    assert numeric.linear(0,1,32768)==0


@pytest.mark.parametrize('divisor,dividend',((0,0xFFFFFFFF),(1,0xFFFFFFFF),(255,0x80000000),(0xFFFFFFFF,0xFFFFFFFF)))
def test_real_divider_instruction_model_matches_unsigned_integer_result_without_clobbering_inputs(sources,divisor,dividend):
    declared,_,fixture,_=sources
    registers=[(0x1728394A+index*0x110203)&0xFFFFFFFF for index in range(15)]
    registers[0],registers[1]=divisor,dividend
    context=(*registers,0x12344321,0x13579BDF,0x2468ACE0,0x3F1,0xA1B2C3D4)
    before=bytes([0x5D])*65536
    result=state.execute(declared,fixture,context,before,bytes(192),0x02000000,0x2000ABCC,0x26C78,context[18])
    assert result['registers'][0]==(dividend//divisor if divisor else 0)
    assert result['registers'][2:]==tuple(registers[2:])
    assert result['ram']==before and result['sp']==0x02000000 and result['pr']==0x2000ABCC
    assert result['sr']&0x200==(context[18]&0x200 if divisor==0 else 0)


def test_correction_patterns_admit_both_clamps_and_their_exact_boundaries(sources):
    declared,image,_,_=sources
    outputs={}
    for pattern in (1,2,6,7):
        case=dict(pattern=pattern,configuration=2)
        calibrations=matrix.calibrations(declared,image,case)
        tables={row['table']:calibrations[row['table']] for row in declared['surface']}
        axes={address:calibrations[address] for row in declared['surface'] for address in (row['row_axis'],row['col_axis'])}
        outputs[pattern]=numeric.caller(tables,axes,128,127,0,calibrations[0x8615][0],64)
    assert outputs[1]['lower_clamp'] and outputs[1]['output_main']==0
    assert outputs[2]['upper_clamp'] and outputs[2]['output_main']==255
    assert outputs[6]['unclamped']==0 and not outputs[6]['lower_clamp']
    assert outputs[7]['unclamped']==255 and not outputs[7]['upper_clamp']


def test_document_geometry_reads_the_executed_descriptor():
    import re
    declared=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.byte-surface-paths.md').read_text()
    for row in declared['surface']:
        assert f"| `{row['table']:08X}` | {row['rows']-1} | {row['cols']} |" in text
    harness=(repo.ROOT/'tools/sh-elf-run/harness-byte-surface-paths.c').read_text()
    for name in ('context','observation'):
        size=re.search(r'_Static_assert\(sizeof\(struct '+name+r'\)==([0-9]+)U',harness)[1]
        assert size+'-byte' in text
    assert state.ISA_REFERENCE_ID in text and state.ISA_REFERENCE in text
    assert '`000C0008`' in text and '`FFFF5773`' in text and '`00008615`' in text


def test_directed_bridge_inputs_leave_the_caller_outputs_unseeded(sources):
    declared,image,_,_=sources
    rows=[case for case in matrix.cases(declared,image) if case['bridge']==1]
    assert {(case['pattern'],case['bridge_selected']) for case in rows}=={
        (pattern,selected) for pattern in (8,9) for selected in (0,1)}
    for case in rows:
        ram=matrix.memory(case)
        assert ram[0x1C5F]==ram[0x1C5D]==0
        assert ram[0x2327]==91 and ram[0x248B]==5 and ram[0x1284]==1
        assert ram[0x11AE]==ram[0x102C]==ram[0x2466]==ram[0x2468]==0
        spans=matrix.calibrations(declared,image,case)
        expected=(150,160) if case['pattern']==8 else (151,180)
        assert spans[0xB2FA]==bytes([expected[0]])*64
        assert spans[0xB33A]==bytes([expected[1]])*256
