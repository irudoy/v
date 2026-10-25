"""Independent physical and numeric/full-state admission of counter-threshold originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import counter_threshold_contract as contract, byte_surface_equations as state
from kb import counter_threshold_matrix as matrix,counter_threshold_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-counter-threshold-paths'
PREFIX = 'kb-counter-threshold-observation '
HEADER = 'counter-threshold-path-cases.h'
HARNESS = 'harness-counter-threshold-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SINK = 'counter_threshold_return.s'
REQUIRED_BRANCHES = (0x796C0,0x79700,0x79738,0x79746,0x2694C,0x26950,0x26954,0x26978)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the counter-threshold path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the counter-threshold path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,owner in ((0xAAFA,'natural-hedgehog/tbl'),):
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the counter-threshold path changes its exact native factor-table identity')
        scale={key:symbol.value(key) for key in ('unit','scale','to_raw','scale_level')}
        if not test_contract.exact(scale,dict(unit='ratio',scale='x/10',to_raw='x*10',scale_level='code')):
            raise ValueError('the counter-threshold original changes its existing owned dimensionless scale')
        result.append(dict(symbol=symbol.key.key,meaning=owner,preserved_scale=scale))
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
        '#define COUNTER_THRESHOLD_REGION '+json.dumps(REGION),
        'static const uint8_t counter_threshold_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case counter_threshold_cases[] = {'))
    for case in declared['cases']:
        values=(case['entry'],matrix.PATTERNS.index(case['pattern']),matrix.AXES.index(case['axis']),case['row'],case['word'],case['elapsed'],case['counter'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()

def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the counter-threshold original repeats a raw observation JSON key')
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
        raise ValueError('the counter-threshold original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the counter-threshold original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the counter-threshold original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the counter-threshold original mutates its const input context')
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
    same(packet['observations'],actual,'the counter-threshold packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_COUNTER_THRESHOLD status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the counter-threshold original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    expected=numeric.caller(observed['calibration_before'],observed['memory_before'][0])
    if (observed['memory_after']!=(expected['memory'],) or observed['exit'][7]!=expected['active']
            or expected['fault']!=b'\xa5\xc3\xd2\xe1'):
        raise ValueError('the counter-threshold RAM or active flag disagrees with independent cell/factor/timer equations')
    actual=[(row['site'],row['entry']['registers'][0],row['entry']['registers'][1])
            for row in result['calls'] if row['target']==0x21BBC]
    if actual!=[(0x79728,10,expected['dividend'])]:
        raise ValueError('the counter-threshold call changes its constant divisor or post-delay byte product')
    lookups=[(row['site'],row['entry']['registers'][4:8]) for row in result['calls'] if row['target']==0x260BC]
    if lookups!=[(0x7969C,(0xAAFA,0x12FEE,0x12FF2,case['row'])),
                 (0x796E6,(0xAAEA,0x12FEE,0x12FF2,case['row']))]:
        raise ValueError('the counter-threshold path changes its actual grid, row/column axes or row coordinate')
    fifth=[row for row in result['accesses'] if row['site']==0x260D2 and row['domain']=='frame' and row['mode']=='read']
    wanted=(0xB6C70000|expected['column']).to_bytes(4,'big').hex()
    if (len(fifth)!=2 or any(row['address']!=observed['sp'] or row['width_bytes']!=4 or row['bytes']!=wanted for row in fifth)):
        raise ValueError('the counter-threshold wrapper changes its actual caller-local SP+3 column input')
    for table,looked in ((0xAAFA,expected['first']),(0xAAEA,expected['second'])):
        reads=[row['address']-table for row in result['accesses'] if row['domain']=='rom' and row['mode']=='read'
               and table<=row['address']<table+16 and row['width_bytes']==1]
        if reads!=list(looked['reads']):
            raise ValueError('the counter-threshold path interpolates or changes its actual lower-knot cell read')
    for site in (0x796B0,0x796C8):
        rows=[row for row in result['branches'] if row['site']==site]
        if rows and any(row['kind']!='taken' for row in rows):
            raise ValueError('the unsigned source word takes an unreachable negative rounding branch')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the counter-threshold path invokes an undeclared stock helper')
    return dict(index=case['index'],raw=expected['first']['value'],elapsed=case['elapsed'],
        dividend=expected['dividend'],divisor=10,quotient=expected['quotient'],threshold=expected['threshold'],
        counter=expected['counter'],active=expected['active'],row=expected['first']['row'],column=expected['first']['column'],
        parent_reachability_admitted=False,native_relation_publication=False,
        datum_identity_inference=False,scale_admission=False,physical_time_units_inference=False,hardware_qualification=False)


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
        raise ValueError('the counter-threshold actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a counter-threshold calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    oracle_source={**declared['source'],'entry':[*declared['source']['entry'],dict(start=0x7974A,end=0x79752)]}
    result=state.execute(oracle_source,bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual counter-threshold complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain','stub_reconstruction'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the counter-threshold original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the counter-threshold raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the counter-threshold original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the counter-threshold original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER,SINK}:
        raise ValueError('the counter-threshold original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source,SINK):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the counter-threshold original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the counter-threshold original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/counter_threshold_capture.py',
                 'tools/kb/src/kb/counter_threshold_contract.py','tools/kb/src/kb/counter_threshold_matrix.py','tools/kb/src/kb/counter_threshold_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/byte_surface_semantics.py',
                 'tools/kb/src/kb/counter_threshold_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the counter-threshold producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the counter-threshold GNU reconstruction changes stock instructions or literals')
    fixture,aliases,boundaries=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the counter-threshold original changes its exact RAM aliases')
    same(packet['boundaries'],boundaries,'the counter-threshold original changes its observing return boundary')
    stub=packet['stub_reconstruction']
    if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
        raise ValueError('the counter-threshold window lacks its separately assembled observing return')
    if (stub['address']!=contract.BOUNDARY['address'] or stub['bytes']!=contract.BOUNDARY['bytes']
            or stub['source_sha256']!=sha((root/'tools/sh-elf-run'/SINK).read_bytes())):
        raise ValueError('the counter-threshold window changes its exact observing return source or bytes')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the counter-threshold fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the counter-threshold actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the counter-threshold original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_counter_threshold_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the counter-threshold original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the counter-threshold original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the counter-threshold original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the counter-threshold original has another actual GNU toolchain')
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
        raise ValueError('the counter-threshold original omits a required conditional branch outcome')
    groups={}
    for row,observed,case in zip(semantics,actual,declared['cases']):
        held=dict(context=list(observed['context']),memory=observed['memory_before'][0].hex(),
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=0xAAFA})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups.setdefault(key,set()).add((row['raw'],row['dividend'],row['threshold'],row['active']))
    if not any(all(len({row[index] for row in outcomes})>=2 for index in range(4)) for outcomes in groups.values()):
        raise ValueError('the counter-threshold original lacks independent factor/product/threshold/active variation')
    if not any(row['counter']==65535 for row in semantics):
        raise ValueError('the counter-threshold original omits word-counter saturation')
    if {case['entry'] for case in declared['cases']}!={matrix.ENTRY}:
        raise ValueError('the counter-threshold original omits its direct function or helper entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,bounded_ratio_factor_lineage=True,parent_reachability_admitted=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('counter_threshold_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact counter-threshold marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the counter-threshold inputs change during independent admission')
    return result
