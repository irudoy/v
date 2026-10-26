"""Independent complete indexed byte OR, actual state and positive computed publications."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract
from kb import diagnostic_record_bits3_6_contract as contract,diagnostic_record_bits3_6_matrix as matrix
from kb import diagnostic_record_bits3_6_semantics as semantics,diagnostic_record_bits3_6_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-diagnostic-record-bits3-6-paths'
PREFIX='kb-diagnostic-record-bits3-6-observation '
HEADER='diagnostic-record-bits3-6-cases.h'
HARNESS='harness-diagnostic-record-bits3-6-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=()
FIXED_BRANCHES={}
SOURCE_FILES = ('defs/JK08A.diagnostic-record-bits3-6-paths.toml',
 'defs/JK08A.diagnostic-record-bit4-claims.toml',
 'defs/JK08A.diagnostic-record-bits3-6.md',
 'tools/sh-elf-run/stock_jk08a_diagnostic_record_bits3_6.s',
 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'tools/sh-elf-run/diagnostic_record_bits3_6_capture.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_contract.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_matrix.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_semantics.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_transfers.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_capture_evidence.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_access_contract.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_access_evidence.py',
 'tools/kb/src/kb/diagnostic_record_bits3_6_access_resolution.py',
 'tools/kb/tests/test_diagnostic_record_bits3_6_contract.py',
 'tools/kb/tests/test_diagnostic_record_bits3_6_capture_evidence.py',
 'tools/kb/tests/test_diagnostic_record_bits3_6_access.py',
 'tools/kb/src/kb/byte_surface_equations.py',
 'tools/kb/src/kb/packed_transfer_evidence.py',
 'tools/kb/src/kb/test_stock_capture.py',
 'tools/kb/src/kb/ignition_literal_evidence.py',
 'tools/kb/src/kb/test_contract.py')



def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import diagnostic_record_bit4_access_evidence as owning
    row,=[item for item in owning.native_rows(model) if item['component']=='diagnostic_record_bits3_6_paths']
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the bits3/6 original omits its exact complete natural entry')
    return [dict(symbol='7mfk-ffff5718/ram',meaning=row['owner'],function='7mfk-0008c942/fn',
        function_meaning='provocative-vulture/fn',original_claim_sha256=row['original_claim_sha256'])]


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
        raise ValueError('the diagnostic-record bits3/6 writer original changes complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the diagnostic-record bits3/6 writer original changes complete natural instructions, pools, aliases or configuration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(case['entry'],observed['memory_before'][0],observed['calibration_before'],
        observed['context'],observed['sr_before'],bytes(frame),observed['sp'],observed['continuation'])
    transfers.require(observed,result,value,fixture)
    return result,value


def require_positive_alternatives(actual,declared,publications):
    if (type(actual) is not list or len(actual)!=len(declared['cases'])
            or type(publications) is not dict or set(publications)!=set(range(len(actual)))):
        raise ValueError('the bits3/6 writer omits complete actual computed member publications')
    groups={index:{} for index in contract.INDICES}
    for at,(case,observed) in enumerate(zip(declared['cases'],actual)):
        index=observed['context'][4]
        if type(index) is not int or index not in contract.INDICES:
            raise ValueError('the bits3/6 alternatives replace an exact full-R4 physical index')
        address=matrix.RAM_BASE+0x5718+3*index+2
        incoming=observed['memory_before'][0][address-matrix.RAM_BASE]
        published=observed['memory_after'][0][address-matrix.RAM_BASE]
        same(publications[at],{(address,1):bytes([published]),(matrix.RAM_BASE+0x507F,1):b'\x01'},
            'the bits3/6 writer changes its exact two reconstructed and observed computed byte publications')
        if published!=incoming|0x48:
            raise ValueError('the bits3/6 writer substitutes an echo or an arbitrary actual byte for OR 0x48')
        memory=bytearray(observed['memory_before'][0]);memory[address-matrix.RAM_BASE]=0
        held=dict(memory=memory.hex(),context=observed['context'],frame=observed['frame_before'].hex(),
            sp=observed['sp'],continuation=observed['continuation'],abi=observed['abi_before'],
            sr=observed['sr_before'],entry=observed['entry'],bound=observed['bound_before'].hex(),
            calibration={str(start):raw.hex() for start,raw in observed['calibration_before'].items()})
        key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
        groups[index].setdefault(key,[]).append((incoming,published))
    for index,held in groups.items():
        if not any(any(a[0]!=b[0] and a[1]!=b[1] and a[0]!=a[1] and b[0]!=b[1]
                and a[1]==a[0]|0x48 and b[1]==b[0]|0x48 for a in values for b in values)
                for values in held.values()):
            raise ValueError('the bits3/6 writer lacks fixed-other distinct actual computed byte alternatives at one exact common member')


def computed_publications(observed,result):
    index=observed['context'][4];address=matrix.RAM_BASE+0x571A+3*index
    incoming=observed['memory_before'][0][address-matrix.RAM_BASE]
    writes=[event for event in result['accesses'] if event['domain']=='ram' and event['mode']=='write']
    expected=[(0x8C954,address,bytes([incoming|8])),(0x8C95E,address,bytes([incoming|0x48])),
        (0x8C966,matrix.RAM_BASE+0x507F,b'\x01')]
    if len(writes)!=len(expected):raise ValueError('the bits3/6 writer omits or duplicates an ordered same-address computed write')
    for event,(site,at,raw) in zip(writes,expected):
        same((event['site'],event['address'],event['width_bytes'],event['bytes']),
            (site,at,1,raw.hex()),'the bits3/6 writer merges,swaps or substitutes its actual ordered OR stages or delay store')
    final=observed['memory_after'][0]
    same(final[address-matrix.RAM_BASE:address-matrix.RAM_BASE+1],bytes([incoming|0x48]),
        'the bits3/6 writer detaches the actual final byte from its complete two-stage physical writes')
    same(final[0x507F:0x5080],b'\x01','the bits3/6 writer detaches its actual RTS-delay flag publication')
    return {(address,1):bytes([incoming|0x48]),(matrix.RAM_BASE+0x507F,1):b'\x01'}


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the diagnostic-record bits3/6 writer original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the diagnostic-record bits3/6 writer raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the diagnostic-record bits3/6 writer original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the diagnostic-record bits3/6 writer original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the diagnostic-record bits3/6 writer original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the diagnostic-record bits3/6 writer original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the diagnostic-record bits3/6 writer original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/diagnostic_record_bits3_6_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a diagnostic-record bits3/6 writer independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the diagnostic-record bits3/6 writer independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the diagnostic-record bits3/6 writer fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the diagnostic-record bits3/6 writer fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the diagnostic-record bits3/6 writer original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the diagnostic-record bits3/6 writer original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_scalar_ram_product_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the diagnostic-record bits3/6 writer original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the diagnostic-record bits3/6 writer original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the diagnostic-record bits3/6 writer original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the diagnostic-record bits3/6 writer original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};seen=set();entries=set()
    fixed={site:set() for site in FIXED_BRANCHES};publications={}
    for index,(case,observed) in enumerate(zip(declared['cases'],actual)):
        result,value=require_state(declared,image,case,observed,root)
        entries.add(observed['entry']);seen.update(result['code'])
        publications[index]=computed_publications(observed,result)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if branch['site'] in fixed:fixed[branch['site']].add(branch['kind'])
    expected_code=transfers.FEASIBLE_SITES
    if entries!=set(contract.ENTRIES) or seen!=expected_code:
        raise ValueError('the diagnostic-record bits3/6 writer original omits a complete natural entry, feasible instruction or delay slot')
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the diagnostic-record bits3/6 writer original omits a feasible conditional outcome')
    if any(fixed[site]!={wanted} for site,wanted in FIXED_BRANCHES.items()):
        raise ValueError('the bits3/6 writer changes a declared fixed conditional outcome')
    require_positive_alternatives(actual,declared,publications)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_diagnostic_record_bits3_6_paths=True,complete_two_ordered_byte_OR_stages_and_RTS_delay=True,
        complete_CPU_SR_frame_RAM=True,complete_physical_member_preimages_and_publications=True,
        fixed_other_actual_common_member_alternatives=True,complete_native_owner_function_TEST_ledger=True,
        no_array_extent_inference=True,no_selected_datum_absence_inference=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        fixed_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in fixed.items()},
        native_identity_admission=False,native_geometry_inference=False,automatic_resolution=False,
        scale_admission=False,units_admission=False,natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),
        'the diagnostic-record bits3/6 writer original replaces a natural return with an outside-code return')


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('diagnostic_record_bits3_6_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual diagnostic-record bits3/6 writer original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the diagnostic-record bits3/6 writer inputs change during independent consumption')
    return result
