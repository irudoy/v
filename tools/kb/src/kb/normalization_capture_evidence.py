"""Independent physical and numeric/full-state admission of normalization originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import normalization_contract as contract, byte_surface_equations as state
from kb import normalization_matrix as matrix,normalization_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-normalization-paths'
PREFIX = 'kb-normalization-observation '
HEADER = 'normalization-path-cases.h'
HARNESS = 'harness-normalization-paths.c'
OBSERVER = 'stock_normalization_invoke.s'
SINK = 'normalization_return.s'
REQUIRED_BRANCHES = (0x627EA,0x26742,0x2698C,0x26990,0x26994,0x269B8)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the normalization path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the normalization path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,kind,owner in ((0x1495A,'tbl','tested-dragon/tbl'),(0x1459A,'tbl','brown-jackrabbit/tbl'),
            (0x145CA,'tbl','placid-mastiff/tbl'),(0xFFFF2B68,'ram','nice-raven/ram')):
        symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the normalization path changes an exact native table or coefficient owner')
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
    lines=['/* Explicit sequenced inputs; no expected semantic outputs. */',
        '#define NORMALIZATION_REGION '+json.dumps(REGION),
        'static const uint8_t normalization_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case normalization_cases[] = {'))
    for case in declared['cases']:
        values=(case['entry'],matrix.KINDS.index(case['kind']),matrix.PATTERNS.index(case['pattern']),
            matrix.KINDS.index(case['selected']),case['coordinate'],case['coefficient_coordinate'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the normalization original repeats a raw observation JSON key')
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
        raise ValueError('the normalization original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the normalization original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the normalization original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the normalization original mutates its const input context')
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
    same(packet['observations'],actual,'the normalization packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_NORMALIZATION status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the normalization original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    expected=numeric.caller(observed['calibration_before'],observed['memory_before'][0],case)
    if observed['memory_after']!=(expected['memory'],) or expected['fault']!=b'\xa5\xc3\xd2\xe1':
        raise ValueError('the normalization RAM disagrees with independent lookup/product/output equations')
    calls=[row for row in result['calls'] if row['target']==0x21CE0]
    actual=[(row['site'],row['entry']['registers'][0],row['entry']['registers'][1]) for row in calls]
    wanted=[] if case['kind']=='coefficient' else [(0x627E0,50000,expected['dividend'])]
    if actual!=wanted:
        raise ValueError('the normalization divider changes its exact post-delay product or constant divisor')
    at=expected['table'];readings=[row['address']-at for row in result['accesses'] if row['domain']=='rom'
        and row['mode']=='read' and at<=row['address']<at+34 and row['width_bytes']==2]
    if readings!=list(expected['lookup']['reads']):
        raise ValueError('the normalization path changes its exact physical word reads')
    if case['kind']!='coefficient':
        other=0x145CA if at==0x1459A else 0x1459A
        if any(row['domain']=='rom' and row['mode']=='read' and other<=row['address']<other+32 for row in result['accesses']):
            raise ValueError('a normalization selected entry reads its unselected U curve')
        loaded=[row for row in result['accesses'] if row['site']==0x627D6 and row['domain']=='ram'
                and row['mode']=='read' and row['address']==matrix.RAM_BASE+0x2B68 and row['width_bytes']==2]
        if len(loaded)!=1 or loaded[0]['bytes']!=expected['coefficient'].to_bytes(2,'big').hex():
            raise ValueError('the normalization product omits the actual published coefficient load')
    elif [(row['site'],row['kind']) for row in result['branches'] if row['site']==0x627B4]!=[(0x627B4,'fallthrough')]:
        raise ValueError('the explicit coefficient entry changes its nonzero R8 observing-boundary premise')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the normalization original invokes an undeclared helper')
    return dict(index=case['index'],kind=case['kind'],group=case['group'],table=at,lookup=expected['lookup']['value'],
        coefficient=expected['coefficient'],dividend=expected['dividend'],output=expected['output'],
        parent_reachability_admitted=False,native_relation_publication=False,datum_identity_inference=False,
        scale_admission=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    seeded[188:192]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded)
            or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI
            or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the normalization actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a normalization calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    oracle_source={**declared['source'],'entry':[*declared['source']['entry'],
        *[dict(start=row['address'],end=row['address']+8) for row in contract.BOUNDARIES]]}
    result=state.execute(oracle_source,bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual normalization complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain','stub_reconstruction'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the normalization original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the normalization raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the normalization original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the normalization original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER,SINK}:
        raise ValueError('the normalization original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source,SINK):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the normalization original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the normalization original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/normalization_capture.py',
                 'tools/kb/src/kb/normalization_contract.py','tools/kb/src/kb/normalization_matrix.py','tools/kb/src/kb/normalization_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/normalization_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the normalization producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the normalization GNU reconstruction changes stock instructions or literals')
    fixture,aliases,boundaries=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the normalization original changes its exact RAM aliases')
    same(packet['boundaries'],boundaries,'the normalization original changes its observing return boundary')
    stubs=packet['stub_reconstruction']
    if type(stubs) is not list or len(stubs)!=len(contract.BOUNDARIES):
        raise ValueError('the normalization original lacks both separately assembled observing returns')
    for stub,boundary in zip(stubs,contract.BOUNDARIES):
        if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
            raise ValueError('the normalization observing return changes its complete reconstruction schema')
        if (stub['address']!=boundary['address'] or stub['bytes']!=boundary['bytes']
                or stub['source_sha256']!=sha((root/'tools/sh-elf-run'/SINK).read_bytes())):
            raise ValueError('the normalization original changes a separately assembled return')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the normalization fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the normalization actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the normalization original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_normalization_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the normalization original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the normalization original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the normalization original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the normalization original has another actual GNU toolchain')
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
        raise ValueError('the normalization original omits a required conditional branch outcome')
    groups={}
    for case,observed,row in zip(declared['cases'],actual,semantics):
        groups.setdefault(case['group'],[]).append((case,observed,row))
    variation={0x1459A:{},0x145CA:{},0x1495A:{}}
    for pairs in groups.values():
        if len(pairs)!=2 or pairs[0][0]['kind']!='coefficient' or pairs[1][0]['kind']!=pairs[0][0]['selected']:
            raise ValueError('the normalization original changes a complete coefficient/consumer pair')
        first,before,coefficient=pairs[0];second,after,normalized=pairs[1]
        if before['memory_after']!=after['memory_before'] or before['calibration_after']!=after['calibration_before']:
            raise ValueError('the normalization original breaks complete RAM or calibration continuity')
        for address in (normalized['table'],0x1495A):
            held=dict(memory=before['memory_before'][0].hex(),selected=second['kind'],
                coordinates=(second['coordinate'],second['coefficient_coordinate']),
                calibration={str(at):raw.hex() for at,raw in before['calibration_before'].items() if at!=address})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            variation[address].setdefault(key,set()).add((coefficient['coefficient'],normalized['lookup'],
                normalized['dividend'],normalized['output']))
    for address,inputs in variation.items():
        wanted=(0,2,3) if address==0x1495A else (1,2,3)
        if not any(all(len({row[index] for row in outcomes})>=2 for index in wanted) for outcomes in inputs.values()):
            raise ValueError('the normalization original lacks an independent K or selected-U change with distinct product/output')
    if {case['entry'] for case in declared['cases']}!=set(matrix.ENTRIES):
        raise ValueError('the normalization original omits one exact conditional entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,sequenced_normalization_lineage=True,parent_reachability_admitted=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('normalization_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact normalization marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the normalization inputs change during independent admission')
    return result
