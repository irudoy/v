"""Independent physical and numeric/full-state admission of exhaust-target originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import exhaust_target_contract as contract, byte_surface_equations as state
from kb import exhaust_target_matrix as matrix
from kb.model import SymbolKey

REGION = 'jk08a-exhaust-target-paths'
PREFIX = 'kb-exhaust-target-observation '
HEADER = 'exhaust-target-path-cases.h'
HARNESS = 'harness-exhaust-target-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0xBFFC6,0xC00B8,0xC052A,0xC05F0,0x259D4)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    for address,owner in ((0xFFFF2327,'exhaust_cvtc_target/ram'),):
        symbol=model.symbols.get(SymbolKey('7mfk','ram',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the exhaust-target path changes a current RAM identity or layout')
        if symbol.value('width') is not None and not test_contract.exact(symbol.value('width'),8):
            raise ValueError('the exhaust-target path changes an exact source-byte width')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the exhaust-target path lacks its current normalized function anchors')
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
    lines=['/* Raw mode and register inputs; no semantic output columns. */',
        '#define EXHAUST_TARGET_REGION '+json.dumps(REGION),
        'static const struct path_case exhaust_target_cases[] = {']
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),case['entry'],case['selected'],case['value'],case['mode'],
                case['first'],case['second'],case['margin'],case['latched'],case['variant'],case['sr'],case['cold'],case['main'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the exhaust-target original repeats a raw observation JSON key')
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
        raise ValueError('the exhaust-target original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the exhaust-target original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the exhaust-target original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the exhaust-target original mutates its const input context')
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
    same(packet['observations'],actual,'the exhaust-target packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_EXHAUST_TARGET status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the exhaust-target original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    if case['kind']=='hysteresis':
        adjusted=case['first']-(case['margin'] if case['latched'] else 0)
        expected=int(adjusted<=case['second'])
        if observed['exit'][19]!=expected or result['calls']:
            raise ValueError('the natural hysteresis helper changes its separate conditional integer equation')
        return dict(kind=case['kind'],index=case['index'],output=expected)
    expected=case['value'] if case['mode']==0 else 91
    after=observed['memory_after'][0]
    if after[0x2327]!=expected:
        raise ValueError('the exhaust-target endpoint or explicit replacement mode changes its independent output equation')
    if len(result['calls'])!=2 or any(row['target']!=0x259D0 for row in result['calls']):
        raise ValueError('the admitted exhaust-target mode reaches another callee or omits a natural hysteresis call')
    source_address=0x01001C5F if case['selected']==0 else 0x01001C5D
    source_site=0xC00CA if case['selected']==0 else 0xC0144
    selected=[row for row in result['accesses'] if row['site']==source_site and row['mode']=='read']
    if case['mode']==0:
        if len(selected)!=1 or selected[0]['address']!=source_address or selected[0]['bytes']!=f'{case["value"]:02x}':
            raise ValueError('the exhaust-target positive endpoint lacks its actual selected source read')
        frame_slot=observed['sp']-96
        writes=[row for row in result['accesses'] if row['mode']=='write' and row['address']==frame_slot]
        required={0xC04C6,0xC05F6}
        if not required<={row['site'] for row in writes} or any(
                row['site'] in required and row['bytes']!=f'{case["value"]:08x}' for row in writes):
            raise ValueError('the exhaust-target intermediate SP+0 definitions lack the selected value')
        final=[row for row in result['accesses'] if row['site']==0xC0CEE and row['mode']=='write']
        if len(final)!=1 or final[0]['address']!=0x01002327 or final[0]['bytes']!=f'{case["value"]:02x}':
            raise ValueError('the exhaust-target positive endpoint does not reach the actual terminal byte store')
    elif case['mode']==1 and selected:
        raise ValueError('the disabled exhaust-target mode unexpectedly reads the selected table result')
    return dict(kind=case['kind'],index=case['index'],selected_source=source_address,output=expected,
                conditional_positive_path=case['mode']==0,mode=case['mode'],scale_admission=False,
                all_modes=False,native_relation_publication=False)


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
        raise ValueError('the exhaust-target actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('an exhaust-target calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual exhaust-target complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the exhaust-target original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the exhaust-target raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the exhaust-target original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the exhaust-target original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the exhaust-target original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the exhaust-target original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the exhaust-target original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/exhaust_target_capture.py',
                 'tools/kb/src/kb/exhaust_target_contract.py','tools/kb/src/kb/exhaust_target_matrix.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/exhaust_target_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the exhaust-target producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the exhaust-target GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the exhaust-target original changes an exact RAM pointer or the wrapping ROM offset')
    same(packet['boundaries'],[],'the exhaust-target original replaces a natural return or stock helper')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the exhaust-target fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the exhaust-target actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the exhaust-target original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_exhaust_target_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the exhaust-target original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the exhaust-target original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the exhaust-target original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the exhaust-target original has another actual GNU toolchain')
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
        raise ValueError('the exhaust-target original omits a required conditional branch outcome')
    if {case['entry'] for case in declared['cases']}!=set(contract.FUNCTIONS):
        raise ValueError('the exhaust-target original omits its direct function or helper entry')
    paths={(row['selected_source'],row['output']) for row in semantics if row.get('conditional_positive_path')}
    if paths!={(address,value) for address in (0x01001C5F,0x01001C5D) for value in matrix.VALUES}:
        raise ValueError('the exhaust-target original lacks an exact conditional endpoint witness')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,ROM_to_DID_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('exhaust_target_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact exhaust-target marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the exhaust-target inputs change during independent admission')
    return result
