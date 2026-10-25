"""Independent complete remaining RPM originals and exact indexed constant-reader admission."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import rpm_remaining_inhibit_contract as contract,rpm_remaining_inhibit_matrix as matrix
from kb import rpm_remaining_inhibit_semantics as semantics,rpm_remaining_inhibit_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-rpm-remaining-inhibit-paths'
PREFIX='kb-rpm-remaining-inhibit-observation '
HEADER='rpm-remaining-inhibit-path-cases.h'
HARNESS='harness-rpm-remaining-inhibit-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0x4F33C,0x4F342,0x4F348,0x4F34E,0x4F36A,0x4F384,0x4F38E,
    0x4F3B0,0x4F3BC,0x4F3DA,0x4F3E6,0x4F3EC,0x4F3FE,0x4F40E,0x4F418,0x4F426,
    0x4F4AE,0x4F53A,0x4F542,0x4F562,0x4F570,0x4F5BA,0x4F608,0x4F61C,0x4F62A,0x4F632,0x4F638,
    0x4F966,0x4F97E,0x4F990,0x4F9A0,0x4F9A8,
    0x50A70,0x50A84,0x50A8E,0x50A96,0x50AA0,0x50AB8,0x50AD6,0x50AE6,0x2638E,0x26742)
FIXED_BRANCHES={0x4F4CA:'taken',0x4F534:'fallthrough',0x4F57C:'taken',0x4F5C4:'taken',
    0x4F5D0:'fallthrough',0x4F5D4:'fallthrough',0x4F5EC:'fallthrough',0x4F5F2:'taken',0x26A9A:'taken'}
EXCLUDED_RANGES=((0x4F4CE,0x4F51A),(0x4F57E,0x4F5AA),(0x4F5C6,0x4F5CE),
    (0x4F5DC,0x4F5E0),(0x4F5F4,0x4F5FA),(0x26A9C,0x26AAA))
SOURCE_FILES=('tools/kb/src/kb/rpm_remaining_inhibit_contract.py',
    'tools/kb/src/kb/rpm_remaining_inhibit_matrix.py','tools/kb/src/kb/rpm_remaining_inhibit_semantics.py',
    'tools/kb/src/kb/rpm_remaining_inhibit_transfers.py',
    'tools/kb/src/kb/rpm_remaining_inhibit_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/test_stock_capture.py','tools/kb/src/kb/width_view_matrix.py',contract.DESCRIPTOR)


def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the remaining RPM original lacks its exact normalized root or natural callees')
    from kb import rpm_inhibit_access_contract as owning
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        if row['component']!='rpm_remaining_inhibit_paths':continue
        symbol=model.symbols.get(owning.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (owning.native_type(row,'width'),owning.native_type(row,'signed')))):
            raise ValueError('the remaining RPM original changes an exact owner or retained semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner']))
    if len(result)!=5:raise ValueError('the remaining RPM original omits an exact owning relation')
    function=model.symbols.get(SymbolKey('7mfk','fn',contract.PARENT))
    if function is None or function.meaning is None or function.meaning.key!='fuel_output_inhibit_coordinator/fn':
        raise ValueError('the remaining RPM original changes its exact complete native root owner')
    result.append(dict(symbol=function.key.key,meaning=function.meaning.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),
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
        raise ValueError('the remaining RPM original changes a complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the remaining RPM original changes a complete executable, pool, pointer or controlled constant span')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the remaining RPM original disagrees with complete independent natural instruction state')
    if observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],):
        raise ValueError('the remaining RPM original disagrees with complete independent frame or RAM instruction effects')
    value=semantics.evaluate(case['entry'],observed['memory_before'][0],observed['calibration_before'],observed['context'])
    transfers.require(observed,result,value,fixture)
    require_premises(result,value)
    return result,value


def require_premises(result,value):
    if any(first<=site<last for site in result['code'] for first,last in EXCLUDED_RANGES):
        raise ValueError('the remaining RPM proof enters code excluded by its explicit quiet/byte-entry premise')
    if any(row['target']==0x7D8B8 for row in result['calls']):
        raise ValueError('the remaining RPM proof enters the excluded diagnostic dispatch without a producer proof')
    for site,outcome in FIXED_BRANCHES.items():
        actual=[row['kind'] for row in result['branches'] if row['site']==site]
        if site==0x26A9A:
            curve=value.get('stationary',{}).get('curve');count=int(curve is not None and not curve['upper'])
        else:
            enabled=value.get('thermal',{}).get('enabled',False)
            count=int(enabled and (site!=0x4F5C4 or bool(result['ram'][0x5720]&16)))
        if actual!=[outcome]*count:raise ValueError('the remaining RPM proof changes an exact conditional branch premise')


def require_positive_alternatives(actual,values,declared,rows):
    for row in rows:
        if row['component']!='rpm_remaining_inhibit_paths':continue
        address,width=row['address'],row['width_bytes'];groups={}
        for observed,value in zip(actual,values):
            entry={0x85D9:0x4EDC6,0xFFFF247F:0x4EDC6,0xFFFF41F2:0x4EDC6,
                0xFFFF247C:0x4EDE4,0xFFFF249C:0x4EE00}[address]
            if observed['entry']!=entry:continue
            memory=bytearray(observed['memory_before'][0])
            calibration={at:bytearray(data) for at,data in observed['calibration_before'].items()}
            bound=bytearray(observed['bound_before'])
            if address>=0xFFFF0000:
                offset=address&65535;incoming=bytes(memory[offset:offset+width]);memory[offset:offset+width]=bytes(width)
            else:
                owners=[at for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
                if len(owners)!=1:raise ValueError('a remaining RPM root lacks its exact controlled operand')
                owner=owners[0];offset=address-owner;incoming=bytes(calibration[owner][offset:offset+width])
                calibration[owner][offset:offset+width]=bytes(width)
                cursor=0
                for first,size in declared['bound_spans']:
                    left,right=max(first,address),min(first+size,address+width)
                    if left<right:bound[cursor+left-first:cursor+right-first]=bytes(right-left)
                    cursor+=size
            held=dict(memory=bytes(memory).hex(),context=list(observed['context']),frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                sr=observed['sr_before'],entry=observed['entry'],bound=bound.hex(),
                calibration={str(at):bytes(data).hex() for at,data in calibration.items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            output=observed['exit'][5] if address in (0x85D9,0xFFFF247F) else observed['exit'][19]
            groups.setdefault(key,set()).add((incoming,output))
        if not any(len({item[0] for item in group})>=2 and len({item[1] for item in group})>=2 for group in groups.values()):
            raise ValueError('a remaining RPM root lacks a changed real caller result under complete fixed-other inputs')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the remaining RPM original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the remaining RPM raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the remaining RPM original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the remaining RPM original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source,'publication_inhibit_snapshot_return.s')
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the remaining RPM original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the remaining RPM original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the remaining RPM original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/rpm_remaining_inhibit_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a remaining RPM independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the remaining RPM independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the remaining RPM fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the remaining RPM fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the remaining RPM original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the remaining RPM original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_rpm_remaining_inhibit_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the remaining RPM original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the remaining RPM original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the remaining RPM original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the remaining RPM original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};values=[];seen=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed,root);values.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        seen.update((row['site'],row['mode'],row['address'],row['width_bytes']) for row in result['accesses'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the remaining RPM original omits a required feasible conditional outcome')
    from kb import rpm_inhibit_access_contract as owning
    rows=owning.descriptor(root)['reference']
    for row in rows:
        if row['component']!='rpm_remaining_inhibit_paths':continue
        address=0x01000000+(row['address']&65535) if row['address']>=0xFFFF0000 else row['address']
        if any((site,'read',address,row['width_bytes']) not in seen for site in row['sites']):
            raise ValueError('a remaining RPM root lacks its exact physical consumer site and native width')
    require_positive_alternatives(actual,values,declared,rows)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_remaining_rpm_accesses=True,quiet_diagnostic_premise=dict(contract.DIAGNOSTIC_PREMISE),
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        native_geometry_inference=False,automatic_resolution=False,scale_admission=False,units_admission=False,
        diagnostic_producer_admission=False,whole_coordinator_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same(packet['boundaries'],list(contract.BOUNDARIES),'the remaining RPM original changes its separate outside-code returns')
    rows=packet['return_reconstruction']
    if type(rows) is not list or len(rows)!=len(contract.BOUNDARIES):
        raise ValueError('the remaining RPM original omits an assembled outside return')
    for row,boundary in zip(rows,contract.BOUNDARIES):
        if type(row) is not dict or set(row)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
            raise ValueError('the remaining RPM original changes a complete return reconstruction')
        same((row['address'],row['bytes'],row['source_sha256']),
            (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
            'the remaining RPM original changes assembled return bytes, location or source')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(row[key])


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('rpm_remaining_inhibit_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual remaining RPM original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the remaining RPM inputs change during independent consumption')
    return result
