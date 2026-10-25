"""Independent complete raw CPU/RAM paths, state publications and direct-table withdrawal."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state, ignition_literal_evidence, packed_transfer_evidence
from kb import repo, test_contract, test_stock_abi, width_view_matrix
from kb import bfs_state_caller_withdrawal_contract as contract, bfs_state_caller_withdrawal_matrix as matrix
from kb import bfs_state_caller_withdrawal_semantics as semantics, bfs_state_caller_withdrawal_transfers as transfers
from kb import byte_factor_caller_withdrawal_capture_evidence as complete_original

REGION = 'jk08a-bfs-state-caller-withdrawal-paths'
PREFIX = 'kb-bfs-state-caller-withdrawal-observation '
HEADER = 'bfs-state-caller-withdrawal-cases.h'
HARNESS = 'harness-bfs-state-caller-withdrawal-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
MARKER = 'VQ_SH_ELF_BFS_STATE_CALLER_WITHDRAWAL'
SOURCE_FILES = (contract.DESCRIPTOR, 'defs/JK08A.bfs-state-caller-withdrawal-paths.md',
    *(f'tools/kb/src/kb/bfs_state_caller_withdrawal_{suffix}.py' for suffix in
        ('contract','matrix','semantics','transfers','capture_evidence')),
    'tools/sh-elf-run/bfs_state_caller_withdrawal_capture.py',contract.UNIT['assembly'],
    'tools/sh-elf-run/'+HARNESS,'tools/sh-elf-run/'+OBSERVER,
    *(f'tools/kb/tests/test_bfs_state_caller_withdrawal_{suffix}.py' for suffix in
        ('contract','capture_evidence','native')),
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/packed_transfer_evidence.py',
    'tools/kb/src/kb/test_stock_capture.py','tools/kb/src/kb/test_stock_abi.py',
    'tools/kb/src/kb/width_view_matrix.py','tools/kb/src/kb/ignition_literal_evidence.py','tools/kb/src/kb/test_contract.py')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def same(actual, wanted, reason):
    if not test_contract.exact(actual, wanted):
        raise ValueError(reason)

def native_bindings(model):
    from kb import scalar_ram_leaf_withdrawal_contract as owning
    rows=[row for row in owning.descriptor(model.root)['reference']
        if row['component']=='bfs_state_caller_withdrawal_paths']
    if (len(rows)!=1 or rows[0]['original_claim_sha256']!=contract.DECLARED['selected']['original_claim_sha256']
            or rows[0]['owner']!='nice-coucal/tbl' or rows[0]['function']!=contract.ENTRY
            or not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',()))):
        raise ValueError('the BFS state caller lacks its exact future coherent whole-datum withdrawal boundary')
    return dict(original_claim_sha256=rows[0]['original_claim_sha256'],owner=rows[0]['owner'],
        entry='7mfk:0003a750',native_width=None,native_signed=None,scope='whole-datum-absence')

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
        raise ValueError('the BFS state caller original omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the request packet substitutes observations for original stdout')
    keys={'schema','index','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the request observation changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the BFS state caller original changes exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the BFS state caller original mutates its immutable complete context')
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
        raise ValueError('the BFS state caller original changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the BFS state caller original changes complete instructions, pools, aliases or raw calibration')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(observed['entry'],observed['memory_before'][0],observed['calibration_before'],
        observed['context'],observed['sr_before'],bytes(frame),observed['sp'],observed['continuation'])
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


CAUSAL_INPUTS=tuple([('ram',matrix.RAM_BASE+at,width,name) for name,at,width in matrix.RAM_FIELDS
    if name in ('byte_1077','word_1026','word_1062')]
    +[('rom',at,width,name) for name,(at,width) in matrix.CAUSAL_CONFIGURATION.items()])
PUBLICATIONS=((0x1F78,1),(0x2542,1),(0x39D0,4),(0x39D4,4),(0x24BA,1),(0x2461,1))

def require_causal_alternatives(pairs):
    admitted={}
    for domain,address,width,name in CAUSAL_INPUTS:
        groups={}
        for observed,value in pairs:
            actual=tuple(observed['memory_after'][0][at:at+size] for at,size in PUBLICATIONS)
            expected=tuple(value['quantities']['memory'][at:at+size] for at,size in PUBLICATIONS)
            if actual!=expected:raise ValueError('the BFS state causal group substitutes scalar outputs for actual publications')
            key,incoming=held_key(observed,address,width,domain);groups.setdefault(key,[]).append((incoming,actual))
        if not any(a[0]!=z[0] and a[1]!=z[1] for rows in groups.values() for a in rows for z in rows):
            raise ValueError('the BFS state original lacks a changed actual publication with every other complete input fixed: '+name)
        admitted[name]=True
    return admitted


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the BFS state caller original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the BFS state caller raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the BFS state caller original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the BFS state caller original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the BFS state caller original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the BFS state caller original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the BFS state caller original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the BFS state caller original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the BFS state caller original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the BFS state caller original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the BFS state caller original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the BFS state caller original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the BFS state caller original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the BFS state caller original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_bfs_state_caller_withdrawal_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the BFS state caller original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the BFS state caller original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the BFS state caller original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the BFS state caller original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)

    actual=observations(packet,declared);pairs=[];seen=set();branches={};source_bytes=set()
    from kb import scalar_ram_leaf_withdrawal_contract as owning
    rows=[row for row in owning.descriptor(root)['reference'] if row['component']=='bfs_state_caller_withdrawal_paths']
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed);transfers.require_no_selected_datum(result,rows)
        pairs.append((observed,value));seen.update(result['code'])
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
        for event in result['accesses']:
            if event['domain']=='rom' and event['mode']=='read' and 0x12A3A<=event['address']<0x12A42:
                source_bytes.update(range(event['address'],event['address']+event['width_bytes']))
    if seen!=transfers.FEASIBLE_SITES:
        raise ValueError('the BFS state original omits a complete feasible instruction, helper tail or delay slot')
    for site in CONDITIONAL_SITES:
        wanted={transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'}
        if branches.get(site)!=wanted:raise ValueError('the BFS state original omits an exact feasible conditional outcome')
    if source_bytes!=set(range(0x12A3A,0x12A42)):
        raise ValueError('the BFS state original omits an actual active curve byte or real endpoint')
    causal=require_causal_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_bfs_state_caller_withdrawal_paths=True,no_selected_datum_access=True,
        complete_selected_table_interval_absence=True,derived_RAM_and_producer_dependencies_preserved=True,
        complete_state_transitions_and_quantity_window=True,complete_natural_calls_live_stores_CPU_frame_and_RAM=True,
        causal_inputs=causal,branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_identity_admission=False,native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)

def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    complete_original.require_primary(model,record)
    packet=record['candidate']['witness'].get('bfs_state_caller_withdrawal_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full BFS state caller original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the BFS state caller source inputs change during independent admission')
    return dict(result,complete_direct_helpers_same_primary=True,complete_existing_byte_factor_original_same_primary=True)

CONDITIONAL_SITES=(155174,
 156534,
 157506,
 158362,
 239454,
 239464,
 239500,
 239508,
 239518,
 239528,
 239536,
 239560,
 239572,
 239594,
 239604,
 239610,
 239618,
 239626,
 239638,
 239654,
 239688,
 239694,
 239716,
 239738,
 239766,
 239784,
 239800)
