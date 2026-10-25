"""Independent physical and numeric/full-state admission of publication inhibit originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import publication_inhibit_contract as contract, byte_surface_equations as state
from kb import publication_inhibit_matrix as matrix,publication_inhibit_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-publication-inhibit-paths'
PREFIX = 'kb-publication-inhibit-observation '
HEADER = 'publication-inhibit-path-cases.h'
HARNESS = 'harness-publication-inhibit-path.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SINK = 'publication_inhibit_snapshot_return.s'
REQUIRED_BRANCHES = (0x3E1F0,0x3E2B6,0x3E2C0,0x3E2CA,0x2635E,
    0x3E2EA,0x3E2F4,0x3E2FC,0x3E322,0x3E340)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    for kind,address,owner in (('tbl',0x1202E,'turquoise-mushroom/tbl'),
            ('ram',0xFFFF1072,'vivid-meerkat/ram'),('ram',0xFFFF106A,'teal-giraffe/ram')):
        symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the publication inhibit path changes an exact table/live/snapshot owner')
        if symbol.value('width') is not None and not test_contract.exact(symbol.value('width'),8):
            raise ValueError('the publication inhibit path contradicts a current byte width')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the publication inhibit path lacks current normalized function anchors')
    return result

def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,ROM_to_snapshot_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Explicit sequenced cache/mode/snapshot inputs; no expected outputs. */',
        '#define PUBLICATION_INHIBIT_REGION '+json.dumps(REGION),
        'static const uint8_t publication_inhibit_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case publication_inhibit_cases[] = {'))
    for case in declared['cases']:
        values=(case['stage'],case['entry'],case['parent'],('stock','flat','rising','falling').index(case['pattern']),
            case['flat'],case['rpm'],case['brake'],case['fault'],case['initial_mode'],case['metadata'],
            case['native_bit'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()

def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the publication inhibit original repeats a raw observation JSON key')
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
        raise ValueError('the publication inhibit original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after','native_before','native_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the publication inhibit original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the publication inhibit original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the publication inhibit original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            native_before=test_stock_abi.raw(row['native_before'],256),native_after=test_stock_abi.raw(row['native_after'],256),
            calibration_before=calibration(row['calibration_before'],declared['calibration_spans']),
            calibration_after=calibration(row['calibration_after'],declared['calibration_spans'])))
    same(packet['observations'],actual,'the publication inhibit packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_PUBLICATION_INHIBIT status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the publication inhibit original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result,image):
    before,after=observed['memory_before'][0],observed['memory_after'][0]
    stage=case['stage']
    if stage in (0,1):
        filtered=numeric.filtered(image,before,case['fault'])
        if int.from_bytes(after[0x1E50:0x1E52],'big')!=filtered:
            raise ValueError('the actual publication filter differs from its separate integer equation')
        reads=[row['address']-0x1202E for row in result['accesses'] if row['domain']=='rom'
            and row['mode']=='read' and 0x1202E<=row['address']<0x12032 and row['width_bytes']==1]
        lookup=None
        if not before[0x2459]&32:
            lookup=numeric.lookup(observed['calibration_before'][0x1202E],case['rpm'])
            if reads!=lookup['operand_offsets'] or any(after[at]!=lookup['output'] for at in (0x1EE0,0x257A)):
                raise ValueError('the original calibration lookup changes its actual cells or cached byte')
        elif reads or after[0x257A]!=before[0x257A]:
            raise ValueError('the retained-cache mode rereads the calibration or changes its cache')
        expected=numeric.publication(filtered,after[0x257A],before[0x2459],before[0x2451])
        final=[row for row in result['accesses'] if row['site']==0x3E31A and row['mode']=='write']
        if (after[0x1072]!=expected or len(final)!=1 or final[0]['address']!=0x01001072
                or final[0]['bytes']!=f'{expected:02x}'):
            raise ValueError('the publication path changes its actual selected final byte store')
        allowed={0x25E4E,0x25E20,0x26358,0x26740}
    elif stage==2:
        expected=before[0x1072]
        if after[0x106A:0x1072]!=before[0x1072:0x107A]:
            raise ValueError('the bounded snapshot does not copy every actual live byte')
        if [row['target'] for row in result['calls']]!=[0x22558]:
            raise ValueError('the bounded snapshot changes its explicit natural byte-copy callee')
        for mode,start in (('read',0x01001072),('write',0x0100106A)):
            accesses=[row for row in result['accesses'] if row['domain']=='ram' and row['mode']==mode
                and start<=row['address']<start+8]
            if ([row['address'] for row in accesses]!=list(range(start,start+8))
                    or any(row['width_bytes']!=1 for row in accesses)):
                raise ValueError('the bounded snapshot lacks an exact physical source or destination byte')
        lookup=None;filtered=None;allowed={0x22558}
    else:raise ValueError('the publication inhibit original has another stage')
    if any(row['target'] not in allowed for row in result['calls']):
        raise ValueError('the publication inhibit path reaches an unadmitted callee')
    return dict(index=case['index'],parent=case['parent'],stage=stage,kind=case['kind'],
        output=expected,lookup=lookup,filtered=filtered,
        conditional_positive_path=case['initial_mode']==0 and case['brake']==0 and case['fault']==1,
        stock_scheduler_body_admitted=False,hardware_effects_admitted=False)

def require_state(declared,image,fixture,case,observed,prior):
    expected_before=matrix.before(case,prior)
    if (expected_before is None or observed['memory_before']!=(expected_before,)
            or not test_contract.exact(observed['context'],matrix.context(declared['source'],case))
            or observed['calibration_before']!=matrix.calibrations(declared['source'],image,case)
            or observed['calibration_after']!=observed['calibration_before']
            or observed['native_before']!=matrix.native_controls(expected_before)
            or observed['native_after']!=matrix.native_controls(observed['memory_after'][0])):
        raise ValueError('the publication inhibit original changes its exact mode-bit transition, stage continuity, calibration, native-control coherence or typed input')
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded)
            or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI
            or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the publication inhibit actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('an publication inhibit calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    oracle_source={**declared['source'],'entry':[*declared['source']['entry'],dict(start=0x20F3A,end=0x20F42)]}
    result=state.execute(oracle_source,bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual publication inhibit complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain','stub_reconstruction'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the publication inhibit original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the publication inhibit raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the publication inhibit original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the publication inhibit original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER,SINK}:
        raise ValueError('the publication inhibit original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source,SINK):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the publication inhibit original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the publication inhibit original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/publication_inhibit_capture.py',
                 'tools/kb/src/kb/publication_inhibit_contract.py','tools/kb/src/kb/publication_inhibit_matrix.py','tools/kb/src/kb/publication_inhibit_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/publication_inhibit_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the publication inhibit producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the publication inhibit GNU reconstruction changes stock instructions or literals')
    fixture,aliases,boundaries=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the publication inhibit original changes an exact RAM pointer or the wrapping ROM offset')
    same(packet['boundaries'],boundaries,'the publication inhibit original changes its exact post-store scheduler boundary')
    stub=packet['stub_reconstruction']
    if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
        raise ValueError('the publication inhibit original lacks its separately assembled scheduler boundary')
    same((stub['address'],stub['bytes'],stub['source_sha256']),(0x20F3A,'57f6472a000b0009',sha((root/'tools/sh-elf-run'/SINK).read_bytes())),'the scheduler boundary changes its actual compiled instruction bytes or source')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the publication inhibit fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the publication inhibit actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=4
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the publication inhibit original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_publication_inhibit_base_verifier')
    if simulator['command'][:3]!=[base.RUN,'--memory-region=0x01000000,64k','--memory-region=0xffff8400,256']:
        raise ValueError('the publication inhibit original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][3])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the publication inhibit original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the publication inhibit original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the publication inhibit original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]
    coverage={site:set() for site in REQUIRED_BRANCHES}
    prior=None
    for case,observed in zip(declared['cases'],actual):
        result,semantic_result=require_state(declared,image,fixture,case,observed,prior)
        prior=observed['memory_after'][0]
        semantics.append(semantic_result)
        for branch in result['branches']:
            if branch['site'] in coverage:
                coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the publication inhibit original omits a required conditional branch outcome')
    if {case['entry'] for case in declared['cases']}!=set(declared['source']['sequence']):
        raise ValueError('the publication inhibit original omits a natural stage entry')
    normal=[row for row in semantics if row['stage']==2 and row['conditional_positive_path']]
    if len({row['output'] for row in normal})<2:
        raise ValueError('the normal publication inhibit original has no witnessed variable calibration contribution')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,ROM_to_snapshot_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('publication_inhibit_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact publication inhibit marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the publication inhibit inputs change during independent admission')
    return result
