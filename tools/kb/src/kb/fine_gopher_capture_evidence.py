"""Independent physical and numeric admission of the fine-gopher original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import fine_gopher_contract as contract, byte_surface_equations as state
from kb import fine_gopher_matrix as matrix, fine_gopher_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-fine-gopher-paths'
PREFIX = 'kb-fine-gopher-observation '
HEADER = 'fine-gopher-path-cases.h'
HARNESS = 'harness-fine-gopher-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0x21CEA,0x21CF2,0x26742,0x2698C,0x26990,0x26994,0x6064E,0x6068A,0x60692,0x606A0,
    0x606EE,0x60718,0x60732,0x6073E,0x6074C,0x60798,0x607BE,0x607EE,0x607F6,0x60804,0x60816,0x6081C,
    0x60828,0x6083A,0x6089A,0x608BE,0x608CE,0x608EC,0x60902,0x60914,0x60928,0x60952,0x6097E,0x6099E,
    0x609D4,0x609E2,0x609F2)
OPEN = ((0x14F42,'rare-groundhog/tbl','rare_call'),(0x14F52,'ochre-tuna/tbl','ochre_call'),
        (0x15002,'steady-beetle/tbl','beetle_call'))
SIMULATOR = ('--memory-region=0x01000000,64k','--memory-region=0xffff8c00,256','--memory-region=0xffff9900,512')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the fine-gopher path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the fine-gopher path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    for address,owner,name in OPEN:
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the fine-gopher path changes an open unsigned-curve owner')
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
    lines=['/* Explicit fine-gopher inputs; independent consumers own numeric and state outputs. */',
        '#define FINE_GOPHER_REGION '+json.dumps(REGION),
        'static const uint8_t fine_gopher_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case fine_gopher_cases[] = {'))
    names=('entry','curve_c','curve_d','curve_a','curve_b','curve_e','coordinate','byte_coordinate','gate','left','right',
           'word_a','word_b','divisor','rom_ec','rom_66','block0','block8','blockc','block10','block14','block18','block1a',
           'block1c','block20','block24','port','variant','sr')
    for case in declared['cases']:
        values=[case['entry']]
        values.extend(matrix.PATTERNS.index(case[name]) for name in ('curve_c','curve_d','curve_a','curve_b','curve_e'))
        values.extend(case[name] for name in names[6:])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the fine-gopher original repeats a raw observation JSON key')
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
        raise ValueError('the fine-gopher original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'gbr_before','gbr_after','block_before','block_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the fine-gopher original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the fine-gopher original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the fine-gopher original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            gbr_before=test_stock_abi.raw(row['gbr_before'],matrix.GBR_SIZE),
            gbr_after=test_stock_abi.raw(row['gbr_after'],matrix.GBR_SIZE),
            block_before=test_stock_abi.raw(row['block_before'],matrix.BLOCK_SIZE),
            block_after=test_stock_abi.raw(row['block_after'],matrix.BLOCK_SIZE),
            calibration_before=calibration(row['calibration_before'],declared['calibration_spans']),
            calibration_after=calibration(row['calibration_after'],declared['calibration_spans'])))
    same(packet['observations'],actual,'the fine-gopher packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_FINE_GOPHER status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the fine-gopher original lacks its unique complete marker')
    return parsed


def logical(observed):
    full=bytearray(observed['memory_after'][0])
    full[0x8C00:0x8D00]=observed['gbr_after']
    full[0x9900:0x9B00]=observed['block_after']
    return bytes(full)


def table_reads(result,address):
    return [row['address']-address for row in result['accesses'] if row['domain']=='rom' and row['mode']=='read'
            and address<=row['address']<address+18 and row['width_bytes']==2]


def semantic(case,observed,result):
    full=logical(observed)
    expected=numeric.caller(observed['calibration_before'],observed['memory_before'][0])
    if full!=expected['memory'] or expected['fault']!=b'\xa5\xc3\xd2\xe1':
        raise ValueError('the fine-gopher RAM disagrees with the lookup, quotient or fault equations')
    oracle=[(row['site'],row['entry']['registers'][0],row['entry']['registers'][1])
            for row in result['calls'] if row['target']==0x21CE0]
    mine=[(row['site'],row['divisor'],row['dividend']) for row in expected['calls']]
    if oracle!=mine:
        raise ValueError('an unsigned divider lacks its exact post-delay divisor and dividend')
    for address,owner,name in OPEN:
        curve=expected['beetle'] if address==0x15002 else expected['rare'] if address==0x14F42 else expected['ochre']
        wanted=[] if curve is None else curve['operand_offsets']
        if table_reads(result,address)!=wanted:
            raise ValueError('a fine-gopher lookup changes its exact physical operand reads')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the fine-gopher path invokes an undeclared helper')
    return dict(index=case['index'],zero_bypass=expected['zero_bypass'],beetle_lookup=expected['beetle_lookup'],
        rare_call=expected['rare_call'],ochre_call=expected['ochre_call'],beetle_call=expected['beetle_call'],
        fault_preserved=True,native_relation_publication=False,datum_identity_inference=False,
        scale_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    before=observed['memory_before'][0]
    after=observed['memory_after'][0]
    if (observed['gbr_before']!=before[0x8C00:0x8D00] or observed['block_before']!=before[0x9900:0x9B00]
            or after[0x8C00:0x8D00]!=observed['gbr_before'] or after[0x9900:0x9B00]!=observed['block_before']):
        raise ValueError('the fine-gopher relocated image absorbs an absolute GBR or block write')
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the fine-gopher actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a fine-gopher calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,before,bytes(seeded),observed['sp'],
        observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    restored=bytearray(result['ram'])
    restored[0x8C00:0x8D00]=observed['gbr_before']
    restored[0x9900:0x9B00]=observed['block_before']
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(bytes(restored),) or logical(observed)!=result['ram']):
        raise ValueError('the actual fine-gopher complete state disagrees with independent natural instruction equations')
    return result,semantic(case,observed,result)


def vary(semantics,actual,address,name):
    groups={}
    for row,observed in zip(semantics,actual):
        spec=row[name]
        if not spec:continue
        held=dict(memory=observed['memory_before'][0].hex(),
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=address})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups.setdefault(key,set()).add((spec['dividend'],spec['quotient']))
    if not any(len({item[0] for item in outcomes})>=2 and len({item[1] for item in outcomes})>=2 for outcomes in groups.values()):
        raise ValueError('the fine-gopher original lacks an independent curve change with distinct dividends and quotients')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the fine-gopher original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the fine-gopher raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the fine-gopher original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the fine-gopher original changes current closure or exact inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the fine-gopher original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the fine-gopher original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the fine-gopher original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/fine_gopher_capture.py','tools/kb/src/kb/fine_gopher_contract.py',
                 'tools/kb/src/kb/fine_gopher_matrix.py','tools/kb/src/kb/fine_gopher_semantics.py',
                 'tools/kb/src/kb/division_callees_semantics.py','tools/kb/src/kb/timing_denominator_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/fine_gopher_capture_evidence.py',
                 'tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the fine-gopher producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in declared['source']['pool']])
    same(packet['reconstruction'],reconstructed,'the fine-gopher GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the fine-gopher original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the fine-gopher original replaces a natural return')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the fine-gopher fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the fine-gopher actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or simulator['returncode']!=0 or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=5):
        raise ValueError('the fine-gopher original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_fine_gopher_base_verifier')
    if tuple(simulator['command'][1:4])!=SIMULATOR or simulator['command'][0]!=base.RUN:
        raise ValueError('the fine-gopher original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][4])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the fine-gopher original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the fine-gopher original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the fine-gopher original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]; coverage={site:set() for site in REQUIRED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,row=require_state(declared,image,fixture,case,observed)
        semantics.append(row)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the fine-gopher original omits a required conditional branch outcome')
    if not any(row['zero_bypass'] and row['beetle_call'] is None for row in semantics):
        raise ValueError('the fine-gopher original lacks a zero-divisor bypass distinct from the divider fault store')
    if not any(row['beetle_call'] for row in semantics):
        raise ValueError('the fine-gopher original lacks a positive post-delay unsigned division of 00015002')
    for address,owner,name in OPEN:vary(semantics,actual,address,name)
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        zero_bypass_distinct_from_fault_store=True,native_geometry_inference=False,
        datum_identity_inference=False,automatic_resolution=False,natural_caller_reachability=False,
        hardware_qualification=False,native_relation_publication=False,scale_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('fine_gopher_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact fine-gopher marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the fine-gopher inputs change during independent admission')
    return result
