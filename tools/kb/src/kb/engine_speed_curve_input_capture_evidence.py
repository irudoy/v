"""Independent complete caller, actual engine-speed argument and causal output admission."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state, ignition_literal_evidence, packed_transfer_evidence
from kb import repo, test_contract, test_stock_abi, width_view_matrix
from kb import engine_speed_curve_input_contract as contract, engine_speed_curve_input_matrix as matrix
from kb import engine_speed_curve_input_semantics as semantics, engine_speed_curve_input_transfers as transfers
from kb import word_interp_caller_withdrawal_capture_evidence as complete_word,division_callees_capture_evidence as complete_division
from kb import byte_factor_caller_withdrawal_capture_evidence as complete_implicit
from kb import mixed_curve_caller_withdrawal_capture_evidence as complete_mixed
from kb import byte_surface_capture_evidence as complete_surface

REGION = 'jk08a-engine-speed-curve-input-paths'
PREFIX = 'kb-engine-speed-curve-input-observation '
HEADER = 'engine-speed-curve-input-cases.h'
HARNESS = 'harness-engine-speed-curve-input-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
MARKER = 'VQ_SH_ELF_ENGINE_SPEED_CURVE_INPUT'
SOURCE_FILES = (contract.DESCRIPTOR, 'defs/JK08A.engine-speed-curve-input-claims.toml', 'defs/JK08A.engine-speed-curve-input.md',
    *(f'tools/kb/src/kb/engine_speed_curve_input_{suffix}.py' for suffix in
      ('contract', 'matrix', 'semantics', 'transfers', 'capture_evidence', 'access_contract', 'access_evidence', 'access_resolution')),
    'tools/sh-elf-run/engine_speed_curve_input_capture.py', contract.UNIT['assembly'],
    'tools/sh-elf-run/' + HARNESS, 'tools/sh-elf-run/' + OBSERVER,
    *(f'tools/kb/tests/test_engine_speed_curve_input_{suffix}.py' for suffix in ('contract', 'capture_evidence', 'access')),
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
    from kb import engine_speed_curve_input_access_evidence as owning
    row = owning.native_rows(model)[0]
    if not set(contract.FUNCTIONS) <= set(model.functions.get('7mfk', ())):
        raise ValueError('the engine-speed curve input omits a complete required natural entry or helper')
    return dict(original_claim_sha256=row['original_claim_sha256'], owner=row['owner'],
                entry='7mfk:0004afdc', primitive='7mfk:00026370', native_width=None, native_signed=None)

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
        if key in value:raise ValueError('the engine-speed curve input observation repeats a raw JSON key')
        value[key]=item
    return value

def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    count=len(declared['cases']);marker=f'{MARKER} status=PASS region={REGION} cases={count}'
    if len(rows)!=count or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the engine-speed curve input original omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the engine-speed curve input packet substitutes observations for original stdout')
    keys={'schema','index','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the engine-speed curve input observation changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the engine-speed curve input original changes exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the engine-speed curve input original mutates its immutable complete context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the engine-speed curve input observation truncates complete relocated RAM')
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
        raise ValueError('the engine-speed curve input original changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the engine-speed curve input original changes complete instructions, pools, aliases or raw calibration')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(observed['memory_before'][0],observed['calibration_before'],observed['frame_before'])
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
        if len(spans)!=1:raise ValueError('the engine-speed curve input causal group loses an exact physical calibration span')
        at,raw=spans[0];offset=address-int(at);incoming=bytes(raw[offset:offset+width]);raw[offset:offset+width]=bytes(width)
        bound=mask_bound(bound,address,width)
    else:raise ValueError('the engine-speed curve input causal group substitutes a frame or synthetic intermediate input')
    held=dict(memory=memory.hex(),calibration={at:bytes(raw).hex() for at,raw in cal.items()},bound=bound.hex(),
        entry=observed['entry'],context=list(observed['context']),frame=observed['frame_before'].hex(),
        sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),sr=observed['sr_before'])
    return sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode()),incoming

CAUSAL_BRANCHES=('first','second','third')

def require_causal_alternatives(pairs):
    admitted={}
    for branch in CAUSAL_BRANCHES:
        groups={}
        for observed,value in pairs:
            if value['speed_branch']!=branch:continue
            memory=observed['memory_after'][0]
            actual=memory[0x1511],memory[0x23EE]
            same(actual,(value['speed_register']&255,value['value']),
                'the speed causal group substitutes scalars for actual1511/23EE publications')
            key,incoming=held_key(observed,matrix.RAM_BASE+0x11B2,1,'ram')
            if incoming!=bytes([value['speed_coordinate']]):
                raise ValueError('the speed causal group detaches the real RAM byte from its actual coordinate')
            groups.setdefault(key,[]).append((incoming,*actual))
        found=False
        for rows in groups.values():
            for a in rows:
                for z in rows:
                    if all(a[i]!=z[i] for i in range(3)):
                        found=True;break
                if found:break
            if found:break
        if not found:
            raise ValueError('the speed quantity lacks changed actual publications with all other inputs fixed: '+branch)
        admitted[branch]=True
    return admitted

def require_substitute_invariance(pairs):
    groups={}
    for observed,value in pairs:
        if value['speed_branch']!='substitute':continue
        key,incoming=held_key(observed,matrix.RAM_BASE+0x11B2,1,'ram')
        memory=bytearray(observed['memory_after'][0])
        if bytes(memory[0x11B2:0x11B3])!=incoming:
            raise ValueError('the substitute path changes its unconsumed RAM11B2 byte')
        memory[0x11B2]=0
        outcome=(bytes(memory),observed['exit'],observed['frame_after'],
                 value['speed_register'],value['value'])
        groups.setdefault(key,[]).append((incoming,outcome))
    seen=False
    for rows in groups.values():
        for a in rows:
            for z in rows:
                if a[0]!=z[0]:
                    seen=True
                    same(a[1],z[1],'the substitute path consumes an independently varied snapshot byte')
    if not seen:
        raise ValueError('the speed quantity omits complete substitute-path snapshot controls')
    return True

def require_prior_publication_invariance(pairs):
    groups={}
    for observed,value in pairs:
        key,incoming=held_key(observed,matrix.RAM_BASE+0x1511,1,'ram')
        outcome=(observed['memory_after'],observed['exit'],observed['frame_after'],
                 value['speed_register'],value['value'])
        groups.setdefault(key,[]).append((incoming,outcome))
    seen=False
    for rows in groups.values():
        for a in rows:
            for z in rows:
                if a[0]!=z[0]:
                    seen=True
                    same(a[1],z[1],'the speed quantity consumes cached1511 instead of its actual produced value')
    if not seen:
        raise ValueError('the speed quantity omits independent overwritten1511 inputs')
    return True

def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the engine-speed curve input original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the engine-speed curve input raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the engine-speed curve input original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the engine-speed curve input original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the engine-speed curve input original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the engine-speed curve input original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the engine-speed curve input original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the engine-speed curve input original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the engine-speed curve input original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the engine-speed curve input original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the engine-speed curve input original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the engine-speed curve input original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the engine-speed curve input original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the engine-speed curve input original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_engine_speed_curve_input_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the engine-speed curve input original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the engine-speed curve input original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the engine-speed curve input original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the engine-speed curve input original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);pairs=[];seen=set();branches={}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed);pairs.append((observed,value));seen.update(result['code'])
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
    if seen!=transfers.FEASIBLE_SITES:
        raise ValueError('the engine-speed curve input omits a complete feasible instruction, natural call or real delay slot')
    if set(branches)!=set(CONDITIONAL_SITES) or any(branches[site]!=(
            {transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'})
            for site in CONDITIONAL_SITES):
        raise ValueError('the engine-speed curve input omits a real mode, clamp, arithmetic or diagnostic branch outcome')
    causal=require_causal_alternatives(pairs);prior=require_prior_publication_invariance(pairs);substitute=require_substitute_invariance(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_engine_speed_curve_input_paths=True,actual11B2_to_R5_and_complete1511_23EE_publications=True,
        overwritten_prior1511_invariant=prior,substitute_snapshot_invariant=substitute,
        complete_natural_entry_RAM_frame_and_CPU=True,causal_inputs=causal,
        branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    complete_implicit.require_primary(model,record)
    complete_mixed.require_primary(model,record)
    complete_surface.require_primary(model,record)
    complete_word.require_primary(model,record)
    complete_division.require_primary(model,record)
    packet=record['candidate']['witness'].get('engine_speed_curve_input_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full indexed word reader marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the engine-speed curve input source inputs change during independent admission')
    return dict(result,complete_existing_implicit_mixed_word_surface_and_division_originals_same_primary=True)

CONDITIONAL_SITES=(138176, 138186, 138194, 138204, 138212, 138236, 138468, 138474, 156534, 157506, 157576, 157590, 157618, 158028, 158032, 158036, 158072, 158092, 158096, 158100, 158136, 158362, 158842, 307204, 307218, 307240, 307260, 307276, 307306, 307316, 307320, 307330, 307358, 307364, 307414, 307436, 307444, 307466, 307476, 307490, 307496, 307502, 307562, 307570, 307604, 307622, 307632, 307638, 307666, 307692, 307814, 307828, 307834, 307840, 307910, 307958, 307964, 307982, 307992, 308052, 308064, 308104, 308226, 308240, 308254, 308266, 308306, 308346, 308422, 308434)
