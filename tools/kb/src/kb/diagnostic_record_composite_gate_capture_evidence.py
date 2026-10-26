"""Independent complete short-circuit array reads, natural calls and actual returned R0."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract
from kb import diagnostic_record_composite_gate_contract as contract,diagnostic_record_composite_gate_matrix as matrix
from kb import diagnostic_record_composite_gate_semantics as semantics,diagnostic_record_composite_gate_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-diagnostic-record-composite-gate-paths'
PREFIX='kb-diagnostic-record-composite-gate-observation '
HEADER='diagnostic-record-composite-gate-cases.h'
HARNESS='harness-diagnostic-record-composite-gate-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0x259EA,0x259FA,0x25A06,0x25A2A,0x25A32,0x25A3A,0x25A42,0x25A4A,0x25A52,0x25A5A,0x25A66,0x25A72,0x25A7E)
FIXED_BRANCHES={0x25A1A:'fallthrough',0x25A22:'fallthrough'}
SOURCE_FILES = ('defs/JK08A.diagnostic-record-composite-gate-paths.toml',
 'defs/JK08A.diagnostic-record-bit4-claims.toml',
 'defs/JK08A.diagnostic-record-composite-gate.md',
 'tools/sh-elf-run/stock_jk08a_diagnostic_record_composite_gate.s',
 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'tools/sh-elf-run/diagnostic_record_composite_gate_capture.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_contract.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_matrix.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_semantics.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_transfers.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_capture_evidence.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_access_contract.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_access_evidence.py',
 'tools/kb/src/kb/diagnostic_record_composite_gate_access_resolution.py',
 'tools/kb/tests/test_diagnostic_record_composite_gate_contract.py',
 'tools/kb/tests/test_diagnostic_record_composite_gate_capture_evidence.py',
 'tools/kb/tests/test_diagnostic_record_composite_gate_access.py',
 'tools/kb/src/kb/byte_surface_equations.py',
 'tools/kb/src/kb/packed_transfer_evidence.py',
 'tools/kb/src/kb/test_stock_capture.py',
 'tools/kb/src/kb/ignition_literal_evidence.py',
 'tools/kb/src/kb/test_contract.py',
 'tools/kb/tests/test_diagnostic_record_composite_gate_access.py')



def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import diagnostic_record_bit4_access_evidence as owning
    row,=[item for item in owning.native_rows(model) if item['component']=='diagnostic_record_composite_gate_paths']
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the bit4 original omits its exact complete natural entry')
    return [dict(symbol='7mfk-ffff5718/ram',meaning=row['owner'],function='7mfk-00025a12/fn',
        function_meaning='ruby-kangaroo/fn',original_claim_sha256=row['original_claim_sha256'])]


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),
        calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def header(declared,image):
    return proof_adapter.header(declared['source']['adapter'],declared['cases'],
        lambda case: matrix.context(declared['source'],case),
        lambda case: matrix.calibrations(declared['source'],image,case))


def observations(packet,declared):
    return proof_transport.decode(packet,declared,declared['source']['adapter'])


def require_state(declared,image,case,observed,root):
    matrix.require_input(declared['source'],image,case,observed)
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the diagnostic-record composite gate original changes complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the diagnostic-record composite gate original changes complete natural instructions, pools, aliases or configuration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(case['entry'],observed['memory_before'][0],observed['calibration_before'],
        observed['context'],observed['sr_before'],bytes(frame),observed['sp'],observed['continuation'])
    transfers.require(observed,result,value,fixture)
    return result,value


def require_positive_alternatives(actual,declared):
    if type(actual) is not list or len(actual)!=len(declared['cases']):
        raise ValueError('the composite gate omits complete actual short-circuit observations')
    for observed in actual:
        output=observed['exit'][-1]
        expected=int(any(observed['memory_before'][0][0x571A+3*index]&0x60 for index in contract.INDICES))
        if type(output) is not int or output not in (0,1) or output!=expected:
            raise ValueError('the composite positive original substitutes an input echo or arbitrary returned word for the actual complete Boolean gate')
    for index in contract.INDICES:
        groups={};offset=0x571A+3*index
        for observed in actual:
            memory=bytearray(observed['memory_before'][0]);incoming=memory[offset];memory[offset]=0
            held=dict(memory=memory.hex(),context=observed['context'],frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=observed['abi_before'],
                sr=observed['sr_before'],entry=observed['entry'],bound=observed['bound_before'].hex(),
                calibration={str(start):raw.hex() for start,raw in observed['calibration_before'].items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            groups.setdefault(key,[]).append((incoming,observed['exit'][-1]))
        if not any(any(a[0]!=b[0] and a[1]!=b[1] and {a[1],b[1]}=={0,1}
                for a in values for b in values) for values in groups.values()):
            raise ValueError('the composite gate lacks distinct actual returned R0 with every other complete input fixed for one exact record member')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the diagnostic-record composite gate original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the diagnostic-record composite gate raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the diagnostic-record composite gate original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the diagnostic-record composite gate original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the diagnostic-record composite gate original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the diagnostic-record composite gate original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the diagnostic-record composite gate original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/diagnostic_record_composite_gate_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a diagnostic-record composite gate independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the diagnostic-record composite gate independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the diagnostic-record composite gate fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the diagnostic-record composite gate fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the diagnostic-record composite gate original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the diagnostic-record composite gate original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_scalar_ram_product_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the diagnostic-record composite gate original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the diagnostic-record composite gate original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the diagnostic-record composite gate original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the diagnostic-record composite gate original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};seen=set();entries=set()
    fixed={site:set() for site in FIXED_BRANCHES}
    for index,(case,observed) in enumerate(zip(declared['cases'],actual)):
        result,value=require_state(declared,image,case,observed,root)
        entries.add(observed['entry']);seen.update(result['code'])
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if branch['site'] in fixed:fixed[branch['site']].add(branch['kind'])
    expected_code=transfers.FEASIBLE_SITES
    if entries!=set(contract.ENTRIES) or seen!=expected_code:
        raise ValueError('the diagnostic-record composite gate original omits a complete natural entry, feasible instruction or delay slot')
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the diagnostic-record composite gate original omits a feasible conditional outcome')
    if any(fixed[site]!={wanted} for site,wanted in FIXED_BRANCHES.items()):
        raise ValueError('the composite gate changes a declared fixed conditional outcome')
    require_positive_alternatives(actual,declared)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_diagnostic_record_composite_gate_paths=True,complete_actual_sentinel_and_short_circuit_calls=True,
        complete_nested_indexed_array_reads=True,complete_CPU_SR_frame_RAM=True,
        fixed_other_actual_R0_alternatives=True,complete_native_owner_function_TEST_ledger=True,
        no_array_extent_inference=True,no_selected_datum_absence_inference=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        fixed_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in fixed.items()},
        native_identity_admission=False,native_geometry_inference=False,automatic_resolution=False,
        scale_admission=False,units_admission=False,natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),
        'the diagnostic-record composite gate original replaces a natural return with an outside-code return')


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('diagnostic_record_composite_gate_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual diagnostic-record composite gate original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the diagnostic-record composite gate inputs change during independent consumption')
    return result
