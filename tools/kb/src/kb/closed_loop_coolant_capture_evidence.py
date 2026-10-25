"""Independent complete coolant originals and exact indexed constant-reader admission."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import closed_loop_coolant_access_contract as contract,closed_loop_coolant_matrix as matrix
from kb import closed_loop_coolant_semantics as semantics
from kb.model import SymbolKey

REGION='jk08a-closed-loop-coolant-paths'
PREFIX='kb-closed-loop-coolant-observation '
HEADER='closed-loop-coolant-path-cases.h'
HARNESS='harness-closed-loop-coolant-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0x5527A,0x55288,0x552A0,0x552B2,0x552C6,0x552D8,0x552E6,
    0x552EE,0x55304,0x55318,0x55322,0x55336,0x553B2,0x553BA,0x553D0,0x553D8,
    0x553FA,0x55410,0x55430,0x5543A,0x55470,0x5547E,0x26376,0x26742,0x22592)
SOURCE_FILES=('tools/kb/src/kb/closed_loop_coolant_access_contract.py',
    'tools/kb/src/kb/closed_loop_coolant_matrix.py','tools/kb/src/kb/closed_loop_coolant_semantics.py',
    'tools/kb/src/kb/closed_loop_coolant_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/test_stock_capture.py','tools/kb/src/kb/width_view_matrix.py',
    'tools/sh-elf-run/stock_coolant_conditional_model.py',
    'tools/sh-elf-run/stock_injection_end_angle_model.py',contract.DESCRIPTOR)


def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the coolant original lacks its exact normalized root or natural callees')
    result=[]
    for address,owner,width,signed in ((0x990A,'fuel_coolant_coefficients/const',8,False),
            (0x5533C,'fuel_coolant_coordinate_offset/const',16,True)):
        symbol=model.symbols.get(SymbolKey('7mfk','const',address))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=owner
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(width,signed))):
            raise ValueError('the coolant original changes an exact constant owner or retained semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    function=model.symbols.get(SymbolKey('7mfk','fn',contract.ENTRY))
    if function is None or function.meaning is None or function.meaning.key!='knowing-potoo/fn':
        raise ValueError('the coolant original changes its exact complete native root owner')
    result.append(dict(symbol=function.key.key,meaning=function.meaning.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),
        calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


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
        raise ValueError('the coolant original changes a complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the coolant original changes a complete executable, pool, pointer or controlled constant span')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the coolant original disagrees with complete independent natural instruction state')
    if observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],):
        raise ValueError('the coolant original disagrees with complete independent frame or RAM instruction effects')
    return result,semantics.require(case,observed,result,root)


def require_positive_alternatives(actual,values,declared):
    for address,width in ((0x990A,1),(0x5533C,2)):
        groups={}
        for observed,value in zip(actual,values):
            if not value['enabled'] or address==0x990A and value['selected_index']!=0:continue
            calibration={at:bytearray(data) for at,data in observed['calibration_before'].items()}
            owners=[at for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
            if len(owners)!=1:raise ValueError('the coolant positive proof lacks its exact selected native operand')
            owner=owners[0];offset=address-owner;incoming=bytes(calibration[owner][offset:offset+width])
            calibration[owner][offset:offset+width]=bytes(width)
            bound=bytearray(observed['bound_before']);cursor=0
            for first,size in declared['bound_spans']:
                left,right=max(first,address),min(first+size,address+width)
                if left<right:bound[cursor+left-first:cursor+right-first]=bytes(right-left)
                cursor+=size
            held=dict(memory=observed['memory_before'][0].hex(),context=list(observed['context']),
                frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
                abi=list(observed['abi_before']),sr=observed['sr_before'],entry=observed['entry'],bound=bound.hex(),
                calibration={str(at):bytes(data).hex() for at,data in calibration.items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            output=observed['memory_after'][0][0x15DA:0x15DC]
            groups.setdefault(key,set()).add((incoming,output))
        if not any(len({row[0] for row in group})>=2 and len({row[1] for row in group})>=2 for group in groups.values()):
            raise ValueError('a coolant constant lacks a changed derived output under complete fixed-other input alternatives')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the coolant original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the coolant raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the coolant original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the coolant original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source,Path(matrix.INPUT_SOURCE).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the coolant original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the coolant original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the coolant original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/closed_loop_coolant_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a coolant independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the coolant independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the coolant fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the coolant fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the coolant original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the coolant original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_closed_loop_coolant_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the coolant original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the coolant original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the coolant original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the coolant original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};fixed=set();selected=set();values=[]
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed,root);values.append(value)
        if value['enabled']:selected.add(value['selected_index'])
        for row in result['branches']:
            if row['site'] in coverage:coverage[row['site']].add(row['kind'])
            if row['site']==0x26A9A:fixed.add(row['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the coolant original omits a required feasible conditional outcome')
    if fixed!={'taken'} or selected!=set(range(16)):
        raise ValueError('the coolant original omits its exact byte-entry premise or a selected coefficient index')
    require_positive_alternatives(actual,values,declared)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_coolant_accesses=True,exact_selected_coefficient=True,exact_signed_offset=True,
        selected_coefficient_indices=sorted(selected),byte_entry_guard_outcomes=sorted(fixed),
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        native_geometry_inference=False,automatic_resolution=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('closed_loop_coolant_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual coolant original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the coolant inputs change during independent consumption')
    return result
