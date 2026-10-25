"""Independent complete byte judgement at native index 1 and actual causal fault publications."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state, ignition_literal_evidence, packed_transfer_evidence
from kb import repo, test_contract, test_stock_abi, width_view_matrix
from kb import rest_position_judgement_contract as contract, rest_position_judgement_matrix as matrix
from kb import rest_position_judgement_semantics as semantics, rest_position_judgement_transfers as transfers

REGION = 'jk08a-rest-position-judgement-paths'
PREFIX = 'kb-rest-position-judgement-observation '
HEADER = 'rest-position-judgement-cases.h'
HARNESS = 'harness-rest-position-judgement-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
MARKER = 'VQ_SH_ELF_REST_POSITION_JUDGEMENT'
SOURCE_FILES = (contract.DESCRIPTOR, 'defs/JK08A.rest-position-judgement-claims.toml', 'defs/JK08A.rest-position-judgement.md',
    *(f'tools/kb/src/kb/rest_position_judgement_{suffix}.py' for suffix in
      ('contract', 'matrix', 'semantics', 'transfers', 'capture_evidence', 'access_contract', 'access_evidence', 'access_resolution')),
    'tools/sh-elf-run/rest_position_judgement_capture.py', contract.UNIT['assembly'],
    'tools/sh-elf-run/' + HARNESS, 'tools/sh-elf-run/' + OBSERVER,
    *(f'tools/kb/tests/test_rest_position_judgement_{suffix}.py' for suffix in ('contract', 'capture_evidence', 'access')),
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
    from kb import rest_position_judgement_access_evidence as owning
    row=owning.native_rows(model)[0]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the rest-position judgement omits the complete natural90256 function')
    return dict(original_claim_sha256=row['original_claim_sha256'],owner=row['owner'],
        entry='7mfk:00090256',native_width=None,native_signed=None,exact_full_R4_bank_index=1)

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
        raise ValueError('the request limit normalization original omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the request packet substitutes observations for original stdout')
    keys={'schema','index','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the request observation changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the request limit normalization original changes exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the request limit normalization original mutates its immutable complete context')
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
        raise ValueError('the request limit normalization original changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the request limit normalization original changes complete instructions, pools, aliases or raw calibration')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.caller(observed['memory_before'][0],observed['calibration_before'],observed['context'])
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

def require_causal_alternatives(pairs):
    groups={}
    for observed,value in pairs:
        raw=observed['memory_after'][0]
        actual=(raw[0x358B],raw[0x3582])
        if actual!=value['flags'][1:]:
            raise ValueError('the rest-position causal group substitutes a scalar for actual fault-byte publications')
        key,incoming=held_key(observed,matrix.RAM_BASE+0x16BB,1,'ram')
        groups.setdefault(key,[]).append((incoming,actual))
    if not any(a[0]!=b[0] and all(x!=y for x,y in zip(a[1],b[1]))
            for rows in groups.values() for a in rows for b in rows):
        raise ValueError('the rest-position judgement lacks changed actual358B and3582 with every other complete input fixed')
    return dict(selected_byte16BB=True,actual_fault_bytes358B_and3582=True)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the request limit normalization original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the request limit normalization raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the request limit normalization original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the request limit normalization original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the request limit normalization original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the request limit normalization original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the request limit normalization original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the request limit normalization original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the request limit normalization original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the request limit normalization original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the request limit normalization original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the request limit normalization original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the request limit normalization original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the request limit normalization original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_rest_position_judgement_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the request limit normalization original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the request limit normalization original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the request limit normalization original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the request limit normalization original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared)
    pairs=[];seen=set();branches={};conditions=set();selected_values=set();control_values={at:set() for name,at,width in matrix.ROM_FIELDS}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed)
        pairs.append((observed,{key:item for key,item in value.items() if key!='memory'}))
        seen.update(result['code'])
        conditions.add('enabled' if value['enabled'] else 'reset')
        if value['enabled']:
            for which in ('first','second'):
                conditions.add(which+'-permit' if value[which+'_permit'] else which+'-reset-permit')
                window=value[which]
                conditions.add(which+'-counter-zero' if window['measured'] else which+'-counter-nonzero')
                if window['measured']:
                    if window['outside']:
                        conditions.add(which+'-outside-high' if window['value']>window['high'] else which+'-outside-low')
                        conditions.add(which+'-high-timer-zero' if window['high_fault'] else which+'-high-timer-nonzero')
                        conditions.add(which+'-low-timer-zero' if window['low_fault'] else which+'-low-timer-nonzero')
                    else:
                        conditions.add(which+'-in-range')
                        if window['value']==window['high']:conditions.add(which+'-high-equality')
                        if window['value']==window['low']:conditions.add(which+'-low-equality')
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
        for event in result['accesses']:
            if event['mode']!='read':continue
            if event['site'] in (0x9030C,0x903AA):selected_values.add(int(event['bytes'],16))
            if event['domain']=='rom' and event['address'] in control_values:
                control_values[event['address']].add(int(event['bytes'],16))
    if seen!=transfers.FEASIBLE_SITES:
        raise ValueError('the rest-position judgement omits a complete feasible instruction or natural delay slot')
    for site in CONDITIONAL_SITES:
        if branches.get(site)!={'taken','fallthrough'}:
            raise ValueError('the rest-position judgement omits an actual bank1 conditional branch outcome')
    required={'enabled','reset'}
    required.update(which+'-'+suffix for which in ('first','second') for suffix in
        ('permit','reset-permit','counter-zero','counter-nonzero','outside-high','outside-low','in-range',
         'high-equality','low-equality','high-timer-zero','high-timer-nonzero','low-timer-zero','low-timer-nonzero'))
    if conditions!=required:
        raise ValueError('the rest-position judgement omits an actual reset, counter, threshold, equality or timer path')
    if selected_values!=set(range(256)) or any(values!=set(range(256)) for values in control_values.values()):
        raise ValueError('the rest-position judgement omits an actual complete selected-byte or ROM-control read domain')
    causal=require_causal_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_rest_position_judgement=True,exact_full_native_R4_bank1=True,
        actual_selected9030C_903AA_reads_and_fault358B_3582_publications=True,
        complete_natural_CPU_SR_GBR_PR_SP_frame_ABI_RAM_and_ordered_RAM_ROM_operands=True,
        complete_both_reset_permits_counter_threshold_equality_and_four_timer_paths=True,causal_inputs=causal,
        branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        native_bank_general_identity_admission=False,natural_caller_reachability=False,
        natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('rest_position_judgement_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full request limit normalization marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the request limit normalization source inputs change during independent admission')
    return result

CONDITIONAL_SITES = (590432, 590452, 590462, 590472, 590476, 590510, 590520, 590524, 590528, 590536, 590576, 590616, 590630, 590646, 590672, 590734, 590774, 590786, 590802, 590828)
