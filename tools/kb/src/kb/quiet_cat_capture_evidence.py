"""Independent physical and numeric admission of the quiet-cat original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import quiet_cat_contract as contract, byte_surface_equations as state
from kb import quiet_cat_matrix as matrix, quiet_cat_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-quiet-cat-paths'
PREFIX = 'kb-quiet-cat-observation '
HEADER = 'quiet-cat-path-cases.h'
HARNESS = 'harness-quiet-cat-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0x21BD2,0x21BE4,0x26742,0x26788,0x2694C,0x26950,0x26954,0x26978,0xBE34E,0xBE360,
    0xBE366,0xBE3F2,0xBE450,0xBE45A,0xBE4E0,0xBE52A,0xBE564,0xBE57C,0xBE592)
TABLES = {0x123EA:'belligerent-potoo/tbl', 0x12412:'red-bullmastiff/tbl'}
SIGNED = 0xBE41E


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the quiet-cat path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the quiet-cat path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,owner in TABLES.items():
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the quiet-cat path changes a signed-curve owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
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
    lines=['/* Explicit quiet-cat inputs; independent consumers own numeric and state outputs. */',
        '#define QUIET_CAT_REGION '+json.dumps(REGION),
        'static const uint8_t quiet_cat_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case quiet_cat_cases[] = {'))
    for case in declared['cases']:
        values=(case['entry'],matrix.PATTERNS.index(case['pattern']),case['input'],case['source'],case['other'],
            case['coordinate'],case['side'],case['flag'],case['gate'],case['wide'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the quiet-cat original repeats a raw observation JSON key')
        result[key]=value
    return result


def calibration(value,spans):
    raw=test_stock_abi.raw(value,sum(size for start,size in spans))
    result={}; offset=0
    for start,size in spans:
        result[start]=raw[offset:offset+size]; offset+=size
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the quiet-cat original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the quiet-cat original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the quiet-cat original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the quiet-cat original mutates its const input context')
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
    same(packet['observations'],actual,'the quiet-cat packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_QUIET_CAT status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the quiet-cat original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,image):
    expected=numeric.caller(image,observed['calibration_before'],observed['memory_before'][0],case['input'])
    if observed['memory_after']!=(expected['memory'],) or expected['fault']!=b'\xa5\xc3\xd2\xe1':
        raise ValueError('the quiet-cat RAM disagrees with the lookup or quotient equations')
    got=[(row['site'],row['entry']['registers'][0],row['entry']['registers'][1])
         for row in result['calls'] if row['target']==0x21BBC]
    mine=[(row['site'],row['divisor'],row['dividend']) for row in expected['calls']]
    signed=[row for row in mine if row[0]==SIGNED]
    if got!=mine or signed!=[(SIGNED,contract.DIVISOR,expected['dividend'])]:
        raise ValueError('the signed call lacks constant divisor 100 and the lookup product dividend')
    table=expected['table']
    reads=[row['address']-table for row in result['accesses'] if row['domain']=='rom' and row['mode']=='read'
           and table<=row['address']<table+9 and row['width_bytes']==1]
    other=0x12412 if table==0x123EA else 0x123EA
    if (reads!=list(expected['lookup']['offsets']) or any(row['domain']=='rom' and row['mode']=='read'
            and other<=row['address']<other+8 for row in result['accesses'])):
        raise ValueError('the selected quiet-cat lookup changes its exact physical byte reads')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the quiet-cat path invokes an undeclared helper')
    return dict(index=case['index'],input=case['input'],dividend=expected['dividend'],lookup=expected['lookup']['value'],
        table=table,divisor=contract.DIVISOR,fault_preserved=True,native_relation_publication=False,
        datum_identity_inference=False,scale_admission=False,natural_caller_reachability=False,
        hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the quiet-cat actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a quiet-cat calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual quiet-cat complete state disagrees with independent natural instruction equations')
    return result,semantic(case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the quiet-cat original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the quiet-cat raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the quiet-cat original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the quiet-cat original changes current closure or exact inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the quiet-cat original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the quiet-cat original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the quiet-cat original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/quiet_cat_capture.py','tools/kb/src/kb/quiet_cat_contract.py',
                 'tools/kb/src/kb/quiet_cat_matrix.py','tools/kb/src/kb/quiet_cat_semantics.py',
                 'tools/kb/src/kb/division_callees_semantics.py','tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/quiet_cat_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the quiet-cat producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in declared['source']['pool']])
    same(packet['reconstruction'],reconstructed,'the quiet-cat GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the quiet-cat original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the quiet-cat original replaces a natural return')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the quiet-cat fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the quiet-cat actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or simulator['returncode']!=0 or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the quiet-cat original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_quiet_cat_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the quiet-cat original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the quiet-cat original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the quiet-cat original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the quiet-cat original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]; coverage={site:set() for site in REQUIRED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,row=require_state(declared,image,fixture,case,observed)
        semantics.append(row)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the quiet-cat original omits a required conditional branch outcome')
    for table,wanted in ((0x123EA,0),(0x12412,1)):
        groups={}
        for row,observed,case in zip(semantics,actual,declared['cases']):
            if (case['input']==0)!=(wanted==0):continue
            held=dict(memory=observed['memory_before'][0].hex(),
                calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=table})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups.setdefault(key,set()).add((row['dividend'],row['lookup']))
        if not any(len({item[0] for item in outcomes})>=2 and len({item[1] for item in outcomes})>=2
                   for outcomes in groups.values()):
            raise ValueError('the quiet-cat original lacks an independent curve change with distinct dividends')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        lookup_scales_the_signed_dividend=True,native_geometry_inference=False,
        datum_identity_inference=False,automatic_resolution=False,natural_caller_reachability=False,
        hardware_qualification=False,native_relation_publication=False,scale_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('quiet_cat_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact quiet-cat marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the quiet-cat inputs change during independent admission')
    return result
