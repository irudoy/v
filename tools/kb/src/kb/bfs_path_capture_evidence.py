"""Independent physical and numeric/full-state admission of bfs originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import bfs_path_contract as contract, byte_surface_equations as state
from kb import bfs_path_matrix as matrix
from kb.model import SymbolKey

REGION = 'jk08a-bfs-paths'
PREFIX = 'kb-bfs-observation '
HEADER = 'bfs-path-cases.h'
HARNESS = 'harness-bfs-path.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0x3B806,0x3BB8C)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    for kind,address,owner,width in (('tbl',0x9284,'active-caracal/tbl',16),('ram',0xFFFF1026,'bfs/ram',16)):
        symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the BFS path changes an exact K or diagnostic result identity')
        if symbol.value('width') is not None and not test_contract.exact(symbol.value('width'),width):
            raise ValueError('the BFS path changes a current declared word width')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    if 0x3B75C not in model.functions.get('7mfk',()):
        raise ValueError('the BFS path lacks its current normalized producer anchor')
    return result


def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,ROM_to_DID_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Explicit K, mode and register inputs; no expected-output columns. */',
        '#define BFS_PATH_REGION '+json.dumps(REGION),
        'static const struct path_case bfs_path_cases[] = {']
    for case in declared['cases']:
        values=(0,case['entry'],case['k'],int(case['stock_input']),case['aggregate'],case['rpm'],
                case['mode'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the bfs original repeats a raw observation JSON key')
        result[key]=value
    return result


def calibration(value,spans):
    raw=test_stock_abi.raw(value,sum(size for start,size in spans))
    result={}
    offset=0
    for start,size in spans:
        result[start]=raw[offset:offset+size]
        offset+=size
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the bfs original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the bfs original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the bfs original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the bfs original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            calibration_before=calibration(row['calibration_before'],declared['calibration_spans']),
            calibration_after=calibration(row['calibration_after'],declared['calibration_spans'])))
    same(packet['observations'],actual,'the bfs packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_BFS_PATH status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the bfs original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result,image):
    factor,denominator=image[0x8A27],image[0x88FB]*max(case['rpm'],64)
    if not denominator:
        raise ValueError('the conditional BFS numeric path loses its positive stock denominator')
    aggregate=case['aggregate']
    scaled=0 if aggregate==0 or aggregate&0x80000000 else min(aggregate*case['k']*factor//(256*denominator),0x726F9)
    coefficient=int.from_bytes(image[0x3B8BA:0x3B8BC],'big')
    quarter=(scaled*coefficient)>>16
    compensated=min(quarter,65535)
    expected=min(compensated,image[0x12CAD]<<8) if case['mode']==0 else image[0x974E]<<8
    after=observed['memory_after'][0]
    if int.from_bytes(after[0x1E40:0x1E44],'big')!=quarter:
        raise ValueError('the natural BFS K-dependent branch changes its independent wide integer equation')
    if int.from_bytes(after[0x1026:0x1028],'big')!=expected:
        raise ValueError('the BFS normal cap or explicit alternate mode changes its independent output equation')
    actual=[row for row in result['accesses'] if row['site']==0x3BC7E and row['mode']=='write']
    if len(actual)!=1 or actual[0]['address']!=0x01001026 or actual[0]['bytes']!=f'{expected:04x}':
        raise ValueError('the BFS conditional result does not reach its actual diagnostic word store')
    read=[row for row in result['accesses'] if row['site']==0x3B814 and row['mode']=='read']
    positive=aggregate!=0 and not aggregate&0x80000000
    if positive:
        if len(read)!=1 or read[0]['address']!=0x9284 or read[0]['bytes']!=f'{case["k"]:04x}':
            raise ValueError('the BFS K-dependent path lacks its actual original calibration word read')
    elif read:
        raise ValueError('the nonpositive BFS aggregate unexpectedly reads the K word')
    allowed={0x21CE0,0x21F40,0x259E4,0x26388,0x22508}
    if any(row['target'] not in allowed for row in result['calls']):
        raise ValueError('the admitted BFS mode reaches another unstated natural callee')
    return dict(kind='bfs',index=case['index'],mode=case['mode'],K=case['k'],stock_input=case['stock_input'],
        quarter=quarter,output=expected,conditional_positive_path=positive and case['mode']==0,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded)
            or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI
            or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the bfs actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('an bfs calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual bfs complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the bfs original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the bfs raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the bfs original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the bfs original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the bfs original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the bfs original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the bfs original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/bfs_path_capture.py',
                 'tools/kb/src/kb/bfs_path_contract.py','tools/kb/src/kb/bfs_path_matrix.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/bfs_path_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the bfs producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the bfs GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the bfs original changes an exact RAM pointer or the wrapping ROM offset')
    same(packet['boundaries'],[],'the bfs original replaces a natural return or stock helper')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the bfs fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the bfs actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the bfs original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_bfs_path_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the bfs original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the bfs original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the bfs original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the bfs original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]
    coverage={site:set() for site in REQUIRED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,semantic_result=require_state(declared,image,fixture,case,observed)
        semantics.append(semantic_result)
        for branch in result['branches']:
            if branch['site'] in coverage:
                coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the bfs original omits a required conditional branch outcome')
    if {case['entry'] for case in declared['cases']}!={0x3B75C}:
        raise ValueError('the BFS original changes its complete natural producer entry')
    if not {row['K'] for row in semantics if row['conditional_positive_path']}>=set(matrix.K_VALUES):
        raise ValueError('the BFS original omits a conditional K-dependent calibration input')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,ROM_to_DID_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('bfs_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact bfs marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the bfs inputs change during independent admission')
    return result
