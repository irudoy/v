"""Exact word widths, low32 products, signed rates and complete channel inputs."""

import hashlib
import json
import tomllib
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import scalar_ram_word_path_contract as contract,scalar_ram_word_matrix as matrix
from kb import scalar_ram_word_semantics as scalar,scalar_ram_word_transfers as transfers
from kb import scalar_ram_word_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('load,factor,scale,cap,expected',((1,1,16384,0xFFFFFFFF,1),
    (1,1,32768,0xFFFFFFFF,65534),(1,1,65535,0xFFFFFFFF,65535),(1,1,32768,0,0),
    (1,1,16384,2,0),(255,65535,1,0xFFFFFFFF,1019)))
def test_product_retains_signed_scale_low32_then_logical_high16(load,factor,scale,cap,expected):
    value=evaluate(0x6E490,load=load,factor=factor,scale=scale,cap=cap)
    assert int.from_bytes(value['ram'][0x1300:0x1302],'big')==expected
    assert value['registers'][0]==0x74 and value['registers'][2]==expected
    assert value['sr']&1==0 and 0x6E4BE not in value['path']
    assert value['branches'][-2]==dict(site=0x6E4BC,target=0x6E4C0,kind='taken',delay=False)


@pytest.mark.parametrize('current,target,rate,expected,t',((0,1,0,0,False),(0,1,1,1,False),
    (0,1,65535,1,True),(1,0,0,1,True),(1,0,1,0,True),(1,0,65535,0,False),
    (32768,32767,65535,32767,False),(32767,32768,65535,32768,True)))
def test_signed_rate_equations_bind_both_directions_and_equality_T(current,target,rate,expected,t):
    value=evaluate(0x76380,current=current,target=target,fall_rate=rate,rise_rate=rate)
    assert int.from_bytes(value['ram'][0x3D70:0x3D72],'big')==expected
    assert value['registers'][0]==0x3AC and bool(value['sr']&1)==t
    assert value['path'][-2:]==(0x763B2,0x763B4)


@pytest.mark.parametrize('index',(0,1,127,128,254,255))
@pytest.mark.parametrize('source,expected',((0,0x2000),(0xDFF,0xFFF0),(0xE00,65535),(65535,65535)))
def test_every_byte_index_keeps_the_exact_word_operand_and_real_RTS_store(index,source,expected):
    value=evaluate(0xCB1CA,raw_r4=index,**{f'channel_source_{index:03d}':source})
    address=0x387A+2*index
    assert value['ram'][address:address+2]==expected.to_bytes(2,'big')
    assert value['registers'][0]==2*index and value['registers'][2]==matrix.RAM_BASE+0x387A
    assert value['registers'][3]==0x1A2 and value['registers'][6]==expected
    assert value['path'][-2:]==(0xCB1F4,0xCB1F6)
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xCB1CA,raw_r4=index,**{f'channel_source_{index:03d}':source})
    before=matrix.memory(case)
    assert value['ram'][:address]==before[:address] and value['ram'][address+2:]==before[address+2:]


def test_channel_index_uses_only_the_byte_while_preserving_the_complete_raw_argument():
    first=evaluate(0xCB1CA,raw_r4=255);second=evaluate(0xCB1CA,raw_r4=0xAAAAFFFF)
    assert first['ram']==second['ram'] and first['tags']==second['tags']
    assert first['registers'][4]==255 and second['registers'][4]==0xAAAAFFFF


def test_declared_channel_arrays_and_configuration_words_have_complete_distinct_memory_bytes():
    source=contract.descriptor(repo.ROOT);fields=matrix.RAM_FIELDS
    for prefix,start in (('channel_source_',0x28BC),('channel_previous_',0x387A)):
        rows=[r for r in fields if r[0].startswith(prefix)]
        assert rows==[(f'{prefix}{i:03d}',start+2*i,2) for i in range(256)]
        assert all(dict(offset=at,width=width,field=name) in source['adapter']['memory'] for name,at,width in rows)
    assert len({at+i for _,at,width in fields for i in range(width)})==sum(width for _,at,width in fields)
    assert [(r['address'],r['size']) for r in contract.CONFIGURATION]==[(0x93C8,2),(0x6E4E8,2),(0x6E5F0,4),(0x90A6,2),(0x90A8,2)]


def test_exact_fixture_retains_all_instruction_bytes_and_only_five_declared_long_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and len(aliases)==5


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_owning_geometry_scale_caller_hardware_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,value',(('factor',65536),('scale',-1),('cap',1<<32),
    ('channel_source_255',True),('channel_previous_255',65536),('raw_r4',1<<32),('initial_sr',2)))
def test_raw_input_refuses_wrong_width_boolean_signed_and_SR_substitutions(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xCB1CA);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


def test_normal_producer_and_generated_adapter_share_the_exact_terminal_marker():
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'scalar_ram_word_capture.py','_kb_word_producer_source_contract')
    source=contract.descriptor(repo.ROOT)
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_SCALAR_RAM_WORD'
    assert source['adapter']['prefix']==producer.PREFIX and source['adapter']['region']==producer.REGION
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_natural_assembly_uses_exact_numbered_SH_shift_mnemonics():
    source=(repo.ROOT/contract.UNIT['assembly']).read_text()
    for site,instruction in ((0x6E4A6,'shll2 r2'),(0x6E4B8,'shlr16 r2'),
            (0xCB1D8,'shll8 r3'),(0xCB1DC,'shll2 r2'),(0xCB1DE,'shll2 r2')):
        assert f'L_{site:08x}:\n    {instruction}\n' in source


def test_published_preceding_source_and_adapter_counts_retain_exact_file_boundaries():
    maps=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256)
    files={name:sha for mapping in maps for name,sha in mapping.items()}
    repair=withdrawal.GATED_ASSEMBLY_SOURCE_REPAIR
    assert len(files)==45 and len(files)-sum(name==repair['path'] for name in files)==44
    for name,sha in files.items():
        data=withdrawal.prior_gated_source_bytes(repo.ROOT,name)
        assert hashlib.sha256(data).hexdigest()==sha
    preceding=proof_adapter.DESCRIPTORS[:proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)]
    outputs={tomllib.loads((repo.ROOT/name).read_text())['adapter'][key]
        for name in preceding for key in ('driver','refusals')}
    assert len(preceding)==10 and len(outputs)==20
    image=repo.images()['JK08A'].path.read_bytes()
    assert len(contract.ENTRIES)==3
    assert sum(image[at:at+2]==b'\x00\x0b' for first,last in contract.SPANS for at in range(first,last,2))==3
    assert withdrawal.digest(withdrawal.descriptor(repo.ROOT)['function'][:25])==withdrawal.PRIOR_OVERFLOW_FUNCTION_SHA256


def test_published_word_counts_and_original_identities_bind_the_executed_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='scalar_ram_word_paths']
    text=(repo.ROOT/'defs/JK08A.scalar-ram-word-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==3 and len(declared['reference'])==129 and len(declared['function'])==70
    assert len({r['owner'] for r in declared['reference']})==98
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,expected in (('78 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),78),
        ('156 code bytes',sum(b-a for a,b in contract.SPANS),156),('16 literal/configuration spans',len(contract.UNIT['pools']),16),
        ('5 pointer aliases',len(contract.UNIT['aliases']),5),('5 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),5),
        ('1 fixed conditional outcome',len(transfers.FIXED_BRANCHES),1),('1 unreachable instruction',len(transfers.INFEASIBLE_INSTRUCTIONS),1)):
        assert phrase in words and actual==expected
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==121 and '121 matching ledger selectors' in words
    assert 'thirteen families and forty-seven capture bindings' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==10 and 'preceding ten adapters' in words
