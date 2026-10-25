"""Independent physical and numeric/full-state admission of denominator originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import timing_denominator_contract as contract, byte_surface_equations as state
from kb import timing_denominator_matrix as matrix,timing_denominator_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-timing-denominator-paths'
PREFIX = 'kb-timing-denominator-observation '
HEADER = 'timing-denominator-path-cases.h'
HARNESS = 'harness-timing-denominator-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0x7B2DE,0x7B31A,0x7B33A,0x7B366,0x7B370,0x7B37A,0x7B386,
    0x7B402,0x7B41A,0x7B426,0x7B46C,0x7B48E,0x7B4BC,0x7B4CA,
    0x26862,0x26870,0x2688C,0x26B42,0x26B50,0x26B6C,
    0x2698C,0x26990,0x26994,0x26B8C,0x26B90,0x26B94,0x26742,0x26AFA)
PARENTS = {
    'parent-a': dict(surface=0x7B2F2,curve=0x7B310,unsigned=0x7B32E,signed=0x7B356,stack=0x7B2E8,
        surface_target=0x262A8,curve_target=0x264CC,table=0xC98E,table_size=512,curve_table=0x14AFA,
        registers=lambda case:(0xC98E,0x13478,0x13498,case['row']),curve_registers=lambda case:(0x14AFA,0x134B8,case['curve'])),
    'parent-b': dict(surface=0x7B444,curve=0x7B462,unsigned=0x7B482,signed=0x7B4AA,stack=0x7B438,
        surface_target=0x26628,curve_target=0x266BC,table=0x16948,table_size=512,curve_table=0x18DD6,
        registers=lambda case:(0x16948,0x18846,0x18866,case['row']),curve_registers=lambda case:(0x18DD6,0x18886,case['curve'])),
}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the denominator path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the denominator path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,owner in ((0x14AFA,'unnatural-petrel/tbl'),(0x18DD6,'micro-penguin/tbl')):
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the denominator path changes an exact native calibration identity')
        if symbol.value('width') is not None and not test_contract.exact(symbol.value('width'),16):
            raise ValueError('the denominator path contradicts a declared eight-word calibration width')
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
    lines=['/* Explicit natural-entry inputs; independent consumers own numeric and state outputs. */',
        '#define TIMING_DENOMINATOR_REGION '+json.dumps(REGION),
        'static const uint8_t timing_denominator_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case timing_denominator_cases[] = {'))
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),case['entry'],matrix.PATTERNS.index(case['pattern']),
            case['row'],case['column'],case['curve'],case['gate'],case['override'],case['high'],
            case['low'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()

def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the timing-denominator original repeats a raw observation JSON key')
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
        raise ValueError('the timing-denominator original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the timing-denominator original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the timing-denominator original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the timing-denominator original mutates its const input context')
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
    same(packet['observations'],actual,'the timing-denominator packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_TIMING_DENOMINATOR status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the timing-denominator original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    expected=numeric.caller(case['kind'],observed['calibration_before'],observed['memory_before'][0])
    if observed['memory_after']!=(expected['memory'],) or expected['fault']!=b'\xa5\xc3\xd2\xe1':
        raise ValueError('the denominator RAM disagrees with separate lookup, quotient, clamp or fault equations')
    parent=PARENTS[case['kind']]
    sites=(parent['surface'],parent['curve'],parent['unsigned'],parent['signed'])
    call_rows=[row for row in result['calls'] if row['site'] in sites]
    if expected['zero_bypass']:
        expected_sites=[parent['surface'],parent['curve'],parent['signed']]
    elif expected['active']:
        expected_sites=list(sites)
    else:
        expected_sites=[]
    if [row['site'] for row in call_rows]!=expected_sites:
        raise ValueError('the denominator parent changes its actual conditional natural call order')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the denominator parent invokes an undeclared helper')
    ranges=((parent['table'],parent['table_size'],2),(parent['curve_table'],18,2))
    table_reads={start:[row['address']-start for row in result['accesses']
        if row['domain']=='rom' and row['mode']=='read' and start<=row['address']<start+size
        and row['width_bytes']==width] for start,size,width in ranges}
    arguments=None
    if expected['active']:
        surface_call,curve_call=call_rows[0],call_rows[1]
        divide_call=next((row for row in call_rows if row['site']==parent['unsigned']),None)
        signed_call=call_rows[-1]
        if (surface_call['target']!=parent['surface_target'] or curve_call['target']!=parent['curve_target']
                or signed_call['target']!=0x21BBC
                or tuple(surface_call['entry']['registers'][4:8])!=parent['registers'](case)
                or tuple(curve_call['entry']['registers'][4:7])!=parent['curve_registers'](case)):
            raise ValueError('a denominator helper lacks its exact post-delay lookup arguments')
        stack=[row for row in result['accesses'] if row['site']==parent['stack']]
        if (len(stack)!=1 or stack[0]['domain']!='frame' or stack[0]['mode']!='write'
                or stack[0]['address']!=surface_call['entry']['sp']+2 or stack[0]['width_bytes']!=2
                or stack[0]['bytes']!=case['column'].to_bytes(2,'big').hex()):
            raise ValueError('the denominator surface wrapper loses its actual caller-local column argument')
        if (table_reads[parent['table']]!=expected['surface']['operand_offsets']
                or table_reads[parent['curve_table']]!=expected['curve']['operand_offsets']):
            raise ValueError('a denominator lookup changes its exact physical table operand reads')
        if expected['zero_bypass']:
            if divide_call is not None:
                raise ValueError('a zero denominator lookup inherits the unsigned divider call')
        else:
            if (divide_call is None or divide_call['target']!=0x21CE0
                    or tuple(divide_call['entry']['registers'][:2])!=(expected['unsigned']['divisor'],expected['unsigned']['dividend'])):
                raise ValueError('the unsigned divider lacks its exact post-delay divisor and dividend')
            arguments=dict(site=parent['unsigned'],target=0x21CE0,after_delay_slot=True,**expected['unsigned'],
                surface=expected['surface'],curve=expected['curve'])
        if any(row['domain']=='rom' and row['site'] in range(0x21BBC,0x21DC6)
               and row['address'] in (parent['table'],parent['curve_table']) for row in result['accesses']):
            raise ValueError('a divider instruction is attributed a denominator calibration read')
    elif any(table_reads.values()) or result['calls']:
        raise ValueError('a gated or overridden denominator path unexpectedly reads a table or invokes a helper')
    return dict(index=case['index'],kind=case['kind'],active=expected['active'],zero_bypass=expected['zero_bypass'],
        arguments=arguments,output=expected['output'],fault_preserved=True,
        native_relation_publication=False,datum_identity_inference=False,scale_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)

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
        raise ValueError('the timing-denominator actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a timing-denominator calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual timing-denominator complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the timing-denominator original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the timing-denominator raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the timing-denominator original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the timing-denominator original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the timing-denominator original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the timing-denominator original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the timing-denominator original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/timing_denominator_capture.py',
                 'tools/kb/src/kb/timing_denominator_contract.py','tools/kb/src/kb/timing_denominator_matrix.py',
                 'tools/kb/src/kb/timing_denominator_semantics.py','tools/kb/src/kb/division_callees_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/timing_denominator_capture_evidence.py',
                 'tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the timing-denominator producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the timing-denominator GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the timing-denominator original changes an exact RAM pointer or the wrapping ROM offset')
    same(packet['boundaries'],[],'the timing-denominator original replaces a natural return or stock helper')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the timing-denominator fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the timing-denominator actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the timing-denominator original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_timing_denominator_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the timing-denominator original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the timing-denominator original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the timing-denominator original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the timing-denominator original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]
    coverage={site:set() for site in REQUIRED_BRANCHES}
    floors={0x269B8:set(),0x26BB8:set()}
    for case,observed in zip(declared['cases'],actual):
        result,semantic_result=require_state(declared,image,fixture,case,observed)
        semantics.append(semantic_result)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if branch['site'] in floors:floors[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the timing-denominator original omits a required conditional branch outcome')
    if any(outcomes!={'taken'} for outcomes in floors.values()):
        raise ValueError('a denominator axis floor changes its declared unsigned zero-boundary outcome')
    if not any(row['zero_bypass'] and row['arguments'] is None for row in semantics):
        raise ValueError('the denominator original lacks a zero-lookup bypass distinct from the divider fault store')
    if not any(row['arguments'] is not None for row in semantics):
        raise ValueError('the denominator original lacks a positive post-delay unsigned division')
    independent={0x14AFA:{},0x18DD6:{}}
    for semantic_row,observed in zip(semantics,actual):
        if semantic_row['arguments'] is None:continue
        address=0x14AFA if semantic_row['kind']=='parent-a' else 0x18DD6
        held=dict(memory=observed['memory_before'][0].hex(),
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=address})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        independent[address].setdefault(key,set()).add((semantic_row['arguments']['quotient'],semantic_row['output']))
    if any(not any(len({quotient for quotient,output in outcomes})>=2
                   and len({output for quotient,output in outcomes})>=2 for outcomes in groups.values())
           for groups in independent.values()):
        raise ValueError('the denominator original lacks independent curve changes with distinct quotients and outputs')
    if {case['entry'] for case in declared['cases']}!={0x7B2C8,0x7B3F4}:
        raise ValueError('the timing-denominator original omits one natural parent entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,bounded_argument_lineage=True,zero_bypass_distinct_from_fault_store=True,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('timing_denominator_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact timing-denominator marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the timing-denominator inputs change during independent admission')
    return result
