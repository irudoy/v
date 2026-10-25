"""Independent physical and numeric/full-state admission of timing-tail originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import timing_tail_contract as contract, byte_surface_equations as state
from kb import timing_tail_matrix as matrix,timing_tail_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-timing-tail-paths'
PREFIX = 'kb-timing-tail-observation '
HEADER = 'timing-tail-path-cases.h'
HARNESS = 'harness-timing-tail-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SINK = 'timing_tail_return.s'
REQUIRED_BRANCHES = (0x4B402,0x4B410,0x4B41E,0x4B42A,0x4B452,0x4B47A,
    0x2698C,0x26990,0x26994,0x269B8,0x2694C,0x26950,0x26954,0x26978,0x26742)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the timing path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the timing path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,owner in ((0x147CA,'indigo-fossa/tbl'),(0x11EFA,'outrageous-bustard/tbl')):
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the timing path changes an exact native calibration identity')
        if symbol.value('width') is not None and not test_contract.exact(symbol.value('width'),16 if address==0x147CA else 8):
            raise ValueError('the timing tail contradicts a declared calibration storage width')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    return result

def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Exact bounded-entry inputs; independent consumers own semantic outputs. */',
        '#define TIMING_TAIL_REGION '+json.dumps(REGION),
        'static const uint8_t timing_tail_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case timing_tail_cases[] = {'))
    for case in declared['cases']:
        values=(0,case['entry'],matrix.PATTERNS.index(case['pattern']),case['coordinate'],case['curve'],
            case['minimum'],case['enabled'],case['reverse_threshold'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()

def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the timing-tail original repeats a raw observation JSON key')
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
        raise ValueError('the timing-tail original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the timing-tail original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the timing-tail original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the timing-tail original mutates its const input context')
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
    same(packet['observations'],actual,'the timing-tail packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_TIMING_TAIL status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the timing-tail original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    expected=numeric.caller(observed['calibration_before'],observed['memory_before'][0])
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('the bounded timing tail disagrees with separate coefficient, curve, quotient or publication equations')
    calls=[row for row in result['calls'] if row['site'] in (0x4B434,0x4B446,0x4B470)]
    if [row['site'] for row in calls]!=([0x4B434,0x4B446,0x4B470] if expected['lookup_enabled'] else []):
        raise ValueError('the timing tail changes its actual conditional natural call order')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the timing tail invokes an undeclared helper')
    reads={start:[row['address']-start for row in result['accesses'] if row['mode']=='read'
        and row['domain']=='rom' and start<=row['address']<start+size and row['width_bytes']==width]
        for start,size,width in ((0x147CA,18,2),(0x11EFA,9,1))}
    arguments=None
    if expected['lookup_enabled']:
        byte_call,word_call,divide_call=calls
        if (byte_call['target']!=0x26474 or word_call['target']!=0x264CC or divide_call['target']!=0x21CE0
                or byte_call['entry']['registers'][4:7]!=(0x11EFA,0x11EEA,case['curve'])
                or word_call['entry']['registers'][4:7]!=(0x147CA,0x1460A,case['coordinate'])
                or divide_call['entry']['registers'][:2]!=(500000,expected['dividend'])
                or divide_call['entry']['macl']!=expected['dividend']
                or reads[0x147CA]!=list(reversed(expected['word_curve']['operand_offsets']))
                or reads[0x11EFA]!=expected['byte_curve']['operand_offsets']):
            raise ValueError('the timing tail loses its exact physical operands or post-delay division input lineage')
        arguments=dict(site=0x4B470,target=0x21CE0,divisor=500000,dividend=expected['dividend'],
            quotient=expected['quotient'],after_delay_slot=True,
            byte_curve=expected['byte_curve'],word_curve=expected['word_curve'])
    elif any(reads.values()) or result['calls']:
        raise ValueError('a disabled timing tail unexpectedly invokes a helper or reads a calibration')
    return dict(index=case['index'],lookup_enabled=expected['lookup_enabled'],arguments=arguments,
        coefficient=expected['coefficient'],output=expected['output'],
        parent_reachability_admitted=False,native_relation_publication=False,datum_identity_inference=False,
        scale_admission=False,natural_caller_reachability=False,hardware_qualification=False)

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
        raise ValueError('the timing-tail actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a timing-tail calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    oracle_source={**declared['source'],'entry':[*declared['source']['entry'],dict(start=0x4B4A4,end=0x4B4AC)]}
    result=state.execute(oracle_source,bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual timing-tail complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain','stub_reconstruction'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the timing-tail original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the timing-tail raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the timing-tail original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the timing-tail original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER,SINK}:
        raise ValueError('the timing-tail original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source,SINK):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the timing-tail original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the timing-tail original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/timing_tail_capture.py',
                 'tools/kb/src/kb/timing_tail_contract.py','tools/kb/src/kb/timing_tail_matrix.py','tools/kb/src/kb/timing_tail_semantics.py',
                 'tools/kb/src/kb/timing_division_matrix.py','tools/kb/src/kb/timing_division_semantics.py',
                 'tools/kb/src/kb/ignition_diagnostic_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/timing_tail_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the timing-tail producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the timing-tail GNU reconstruction changes stock instructions or literals')
    fixture,aliases,boundaries=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the timing-tail original changes its exact RAM aliases')
    same(packet['boundaries'],boundaries,'the timing-tail original changes its observing return boundary')
    stub=packet['stub_reconstruction']
    if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
        raise ValueError('the timing tail lacks its separately assembled observing return')
    if (stub['address']!=contract.BOUNDARY['address'] or stub['bytes']!=contract.BOUNDARY['bytes']
            or stub['source_sha256']!=sha((root/'tools/sh-elf-run'/SINK).read_bytes())):
        raise ValueError('the timing tail changes its exact observing return source or bytes')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the timing-tail fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the timing-tail actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the timing-tail original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_timing_tail_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the timing-tail original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the timing-tail original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the timing-tail original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the timing-tail original has another actual GNU toolchain')
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
        raise ValueError('the timing-tail original omits a required conditional branch outcome')
    independent={0x147CA:{},0x11EFA:{}}
    for semantic_row,observed in zip(semantics,actual):
        if semantic_row['arguments'] is None:continue
        for address,groups in independent.items():
            inputs=dict(memory=observed['memory_before'][0].hex(),
                calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=address})
            key=json.dumps(inputs,sort_keys=True,separators=(',',':'))
            groups.setdefault(key,set()).add((semantic_row['arguments']['dividend'],semantic_row['output']))
    if any(not any(len({dividend for dividend,output in outcomes})>=2
                   and len({output for dividend,output in outcomes})>=2 for outcomes in groups.values())
           for groups in independent.values()):
        raise ValueError('the timing original lacks independent table changes with distinct argument and bounded output values')
    if {case['entry'] for case in declared['cases']}!={matrix.ENTRY}:
        raise ValueError('the timing-tail original omits its direct function or helper entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,bounded_argument_lineage=True,parent_reachability_admitted=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('timing_tail_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact timing-tail marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the timing-tail inputs change during independent admission')
    return result
