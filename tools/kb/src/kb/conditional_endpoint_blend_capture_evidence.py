"""Independent complete endpoint words, actual signed blend and two owning surface admissions."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state, ignition_literal_evidence, packed_transfer_evidence
from kb import repo, test_contract, test_stock_abi, width_view_matrix
from kb import conditional_endpoint_blend_contract as contract, conditional_endpoint_blend_matrix as matrix
from kb import conditional_endpoint_blend_semantics as semantics, conditional_endpoint_blend_transfers as transfers
from kb import timing_denominator_capture_evidence as helper_original

REGION = 'jk08a-conditional-endpoint-blend-paths'
PREFIX = 'kb-conditional-endpoint-blend-observation '
HEADER = 'conditional-endpoint-blend-cases.h'
HARNESS = 'harness-conditional-endpoint-blend-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
MARKER = 'VQ_SH_ELF_CONDITIONAL_ENDPOINT_BLEND'
SOURCE_FILES = (contract.DESCRIPTOR, 'defs/JK08A.conditional-endpoint-blend-claims.toml', 'defs/JK08A.conditional-endpoint-blend.md',
    *(f'tools/kb/src/kb/conditional_endpoint_blend_{suffix}.py' for suffix in
      ('contract', 'matrix', 'semantics', 'transfers', 'capture_evidence', 'access_contract', 'access_evidence', 'access_resolution')),
    'tools/sh-elf-run/conditional_endpoint_blend_capture.py', contract.UNIT['assembly'],
    'tools/sh-elf-run/' + HARNESS, 'tools/sh-elf-run/' + OBSERVER,
    *(f'tools/kb/tests/test_conditional_endpoint_blend_{suffix}.py' for suffix in ('contract', 'capture_evidence', 'access')),
    'tools/kb/src/kb/byte_surface_equations.py', 'tools/kb/src/kb/packed_transfer_evidence.py',
    'tools/kb/src/kb/test_stock_capture.py', 'tools/kb/src/kb/test_stock_abi.py',
    'tools/kb/src/kb/width_view_matrix.py', 'tools/kb/src/kb/ignition_literal_evidence.py',
    'tools/kb/src/kb/test_contract.py')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)

def native_bindings(model):
    from kb import conditional_endpoint_blend_access_evidence as owning
    rows = owning.native_rows(model)
    if not set(contract.FUNCTIONS) <= set(model.functions.get('7mfk', ())):
        raise ValueError('the conditional endpoint blend omits a complete normalized function in its real closure')
    return dict(original_claims={row['owner']: row['original_claim_sha256'] for row in rows},
                entry='7mfk:00076108', retained_native_types={row['owner']: [None, None] for row in rows})

def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',source=source,
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),cases=list(matrix.cases(source,image)),
        calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS],semantic_admission=False,
        native_geometry_inference=False,natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)

def objects(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('the request observation repeats a raw JSON key')
        value[key]=item
    return value

def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    count=len(declared['cases']);marker=f'{MARKER} status=PASS region={REGION} cases={count}'
    if len(rows)!=count or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the conditional endpoint blend original omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the request packet substitutes observations for original stdout')
    keys={'schema','index','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the request observation changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the conditional endpoint blend original changes exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the conditional endpoint blend original mutates its immutable complete context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the request observation truncates complete relocated RAM')
        size=sum(size for at,size in declared['bound_spans'])
        parsed.append(dict(index=index,entry=row['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(memory['ram_before'],),memory_after=(memory['ram_after'],),
            bound_before=test_stock_abi.raw(row['bound_before'],size),bound_after=test_stock_abi.raw(row['bound_after'],size),**cal))
    return parsed

def require_state(declared,image,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=observed['abi_before'][10]-164
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the conditional endpoint blend original changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the conditional endpoint blend original changes complete instructions, pools, aliases or raw calibration')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.caller(observed['memory_before'][0],observed['calibration_before'])
    transfers.require(observed,result,value,fixture)
    return result,value

def mask_bound(raw,address,width):
    out=bytearray(raw);offset=0
    for row in contract.BOUND_SPANS:
        start,size=row['address'],row['size'];first=max(start,address);last=min(start+size,address+width)
        if first<last:out[offset+first-start:offset+last-start]=bytes(last-first)
        offset+=size
    return bytes(out)

def held_key(observed,address,width,domain):
    memory=bytearray(observed['memory_before'][0]);cal={str(at):bytearray(raw) for at,raw in observed['calibration_before'].items()}
    bound=observed['bound_before']
    if domain=='ram':
        offset=address-matrix.RAM_BASE;incoming=bytes(memory[offset:offset+width]);memory[offset:offset+width]=bytes(width)
    elif domain=='rom':
        spans=[(at,raw) for at,raw in cal.items() if int(at)<=address and address+width<=int(at)+len(raw)]
        if len(spans)!=1:raise ValueError('the request causal group loses an exact physical calibration span')
        at,raw=spans[0];offset=address-int(at);incoming=bytes(raw[offset:offset+width]);raw[offset:offset+width]=bytes(width)
        bound=mask_bound(bound,address,width)
    else:raise ValueError('the request causal group substitutes a frame or synthetic intermediate input')
    held=dict(memory=memory.hex(),calibration={at:bytes(raw).hex() for at,raw in cal.items()},bound=bound.hex(),
        entry=observed['entry'],context=list(observed['context']),frame=observed['frame_before'].hex(),
        sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),sr=observed['sr_before'])
    return sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode()),incoming

CAUSAL_SURFACES = ((0xDE8E, 'surface-a'), (0xE08E, 'surface-b'))

def require_causal_alternatives(pairs):
    admitted = {}
    for address, name in CAUSAL_SURFACES:
        groups = {}
        for observed, value in pairs:
            actual = int.from_bytes(observed['memory_after'][0][0x18E6:0x18E8], 'big')
            if actual != value['value']:
                raise ValueError('the endpoint causal group substitutes a scalar for actual blended word bytes')
            key, incoming = held_key(observed, address, 512, 'rom')
            groups.setdefault(key, []).append((incoming, actual))
        changed_cells = set()
        for rows in groups.values():
            for index, first in enumerate(rows):
                for second in rows[index+1:]:
                    if first[0] == second[0] or first[1] == second[1]:
                        continue
                    changed = [cell for cell in range(256) if first[0][2*cell:2*cell+2] != second[0][2*cell:2*cell+2]]
                    if len(changed) == 1:
                        changed_cells.add(changed[0])
        if changed_cells != set(range(256)):
            raise ValueError('the endpoint original lacks actual output changes for every single surface word with all other complete inputs fixed: ' + name)
        admitted[name] = dict(all256_actual_word_alternatives=True)
    return admitted

def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the conditional endpoint blend original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the conditional endpoint blend raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the conditional endpoint blend original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the conditional endpoint blend original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the conditional endpoint blend original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the conditional endpoint blend original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the conditional endpoint blend original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the conditional endpoint blend original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the conditional endpoint blend original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the conditional endpoint blend original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the conditional endpoint blend original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the conditional endpoint blend original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the conditional endpoint blend original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the conditional endpoint blend original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_conditional_endpoint_blend_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x1000000,64k']:raise ValueError('the conditional endpoint blend original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the conditional endpoint blend original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the conditional endpoint blend original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the conditional endpoint blend original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual = observations(packet, declared)
    pairs, seen, branches, choices = [], set(), {}, set()
    source_bytes = {address: set() for address in (0xDE8E, 0xE08E, 0x13D14, 0x13D34)}
    for case, observed in zip(declared['cases'], actual):
        result, value = require_state(declared, image, case, observed)
        # Whole numerical RAM is already compared with actual raw RAM; the
        # causal layer retains its scalar fields and complete observed inputs.
        pairs.append((observed, {key: item for key, item in value.items() if key != 'memory'}))
        seen.update(result['code'])
        choices.add(value['branch'])
        for branch in result['branches']:
            if branch['kind'] in ('taken', 'fallthrough'):
                branches.setdefault(branch['site'], set()).add(branch['kind'])
        for event in result['accesses']:
            if event['domain'] != 'rom' or event['mode'] != 'read':
                continue
            for address in source_bytes:
                size = 512 if address in (0xDE8E, 0xE08E) else 32
                if address <= event['address'] and event['address'] + event['width_bytes'] <= address + size:
                    source_bytes[address].update(range(event['address'], event['address'] + event['width_bytes']))
    if seen != transfers.FEASIBLE_SITES:
        raise ValueError('the endpoint original omits a feasible complete stock instruction or delay slot')
    for site in CONDITIONAL_SITES:
        wanted = {transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken', 'fallthrough'}
        if branches.get(site) != wanted:
            raise ValueError('the endpoint original omits a real caller-scoped branch outcome')
    if choices != {'endpoint-a', 'endpoint-b', 'intermediate', 'gate-a-refusal', 'gate-b-refusal'}:
        raise ValueError('the endpoint original omits an actual final signed word choice')
    for address, actual_bytes in source_bytes.items():
        size = 512 if address in (0xDE8E, 0xE08E) else 32
        if actual_bytes != set(range(address, address+size)):
            raise ValueError('the endpoint original omits an actual complete surface or axis word byte')
    causal = require_causal_alternatives(pairs)
    return dict(region=REGION, observations=len(actual), native_bindings=native_bindings(model),
                image_sha256=sha(image), fixture_sha256=sha(fixture), elf_sha256=packet['elf_sha256'],
                stdout_sha256=packet['stdout_sha256'], exact_two_surface_conditional_endpoint_blend=True,
                complete_natural_calls_live_stores_CPU_frame_and_RAM=True,
                actual_signed_endpoints_weight_and_all_blend_choices=True, actual_ROM_gate_refusals_and_active_path=True, causal_inputs=causal,
                branch_outcomes={f'{site:08x}': sorted(values) for site, values in branches.items()},
                native_geometry_inference=False, scale_admission=False, units_admission=False,
                natural_caller_reachability=False, natural_scheduling_inference=False, hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    helper_original.require_primary(model,record)
    packet=record['candidate']['witness'].get('conditional_endpoint_blend_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full conditional endpoint blend marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the conditional endpoint blend source inputs change during independent admission')
    return result

CONDITIONAL_SITES = (157506, 157794, 157808, 157836, 158092, 158096, 158100, 158136, 158842, 483432, 483444, 483554, 483568, 483580, 483602, 483610, 483630, 483646)
