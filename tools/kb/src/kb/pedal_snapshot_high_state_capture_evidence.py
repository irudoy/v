"""Independent existing prefix, continuous complete RAM and full pedal-status admission."""
import hashlib,json
from pathlib import Path
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence
from kb import repo,test_contract,test_stock_abi,width_view_matrix,coherent_copy_matrix as coherent
from kb import pedal_snapshot_high_state_contract as contract,pedal_snapshot_high_state_matrix as matrix
from kb import pedal_snapshot_high_state_semantics as numeric,pedal_snapshot_high_state_transfers as transfers
REGION='jk08a-pedal-snapshot-high-state-paths'
PREFIX='kb-pedal-snapshot-high-state-observation '
HEADER='pedal-snapshot-high-state-cases.h'
HARNESS='harness-pedal-snapshot-high-state-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
SNAPSHOT_OBSERVER='stock_injection_start_delay_invoke.s'
MARKER='VQ_SH_ELF_PEDAL_SNAPSHOT_HIGH_STATE'
SOURCE_FILES=(contract.DESCRIPTOR,'defs/JK08A.pedal-snapshot-high-state-claims.toml',
    'defs/JK08A.pedal-snapshot-high-state.md',
    *(f'tools/kb/src/kb/pedal_snapshot_high_state_{suffix}.py' for suffix in
      ('contract','matrix','semantics','transfers','capture_evidence','access_contract','access_evidence','access_resolution')),
    'tools/sh-elf-run/pedal_snapshot_high_state_capture.py',contract.UNIT['assembly'],contract.SNAPSHOT['assembly'],
    'tools/sh-elf-run/'+HARNESS,'tools/sh-elf-run/'+OBSERVER,'tools/sh-elf-run/'+SNAPSHOT_OBSERVER,
    *(f'tools/kb/tests/test_pedal_snapshot_high_state_{suffix}.py' for suffix in ('contract','capture_evidence','access')))


def sha(raw):return hashlib.sha256(raw).hexdigest()
def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def native_bindings(model):
    from kb import pedal_snapshot_high_state_access_evidence as owning
    rows=owning.native_rows(model)
    if len(rows)!=1 or rows[0]['owner']!='pedal/ram' or not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the pedal pair omits its exact native owner or normalized source context')
    return dict(original_claims={row['owner']:row['original_claim_sha256'] for row in rows},
                entry='7mfk:00047a56',retained_native_types={'pedal/ram':[None,None]})


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',source=source,
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),cases=list(matrix.cases(source,image)),
        calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS],semantic_admission=False,
        native_geometry_inference=False,natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the pedal raw observation repeats a JSON key')
        result[key]=value
    return result


def decode_observer(raw,legacy=False):
    size=380 if legacy else 572;frame_size=96 if legacy else 192
    data=test_stock_abi.raw(raw,size)
    return dict(exit=test_stock_abi.words(data[:80]),sp=int.from_bytes(data[80:84],'big'),
        continuation=int.from_bytes(data[84:88],'big'),abi_before=test_stock_abi.words(data[88:136]),
        abi_after=test_stock_abi.words(data[136:184]),frame_before=data[184:184+frame_size],
        frame_after=data[184+frame_size:184+2*frame_size],sr_before=int.from_bytes(data[-4:],'big'))


def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    marker=f'{MARKER} status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the pedal pair omits its complete ordered raw stream or terminal')
    same(packet['observations'],rows,'the pedal pair substitutes a packet for the original stdout')
    keys={'schema','index','snapshot_entry','entry','snapshot_context','snapshot_context_after','snapshot_observation',
        'context','context_after','observation','ram_before','ram_after_snapshot','ram_before_comparator','ram_after',
        'calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the pedal pair changes its complete raw schema')
        same((row['schema'],row['index'],row['snapshot_entry'],row['entry']),
             (1,index,contract.SNAPSHOT['entry'],contract.ENTRY),'the pedal pair changes its actual entry order')
        legacy=test_stock_abi.raw(row['snapshot_context'],76);context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['snapshot_context_after'],76)!=legacy or test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the pedal pair mutates a complete immutable phase context')
        cal={}
        for name in ('calibration_before','calibration_after'):
            data=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=data[offset:offset+size];offset+=size
        bound_size=sum(size for at,size in declared['bound_spans'])
        parsed.append(dict(index=index,entry=row['entry'],snapshot_entry=row['snapshot_entry'],
            snapshot_context=test_stock_abi.words(legacy),context=test_stock_abi.words(context),
            snapshot_observer=decode_observer(row['snapshot_observation'],True),comparator_observer=decode_observer(row['observation']),
            memory_before=width_view_matrix.decode_rle(row['ram_before']),
            memory_after_snapshot=width_view_matrix.decode_rle(row['ram_after_snapshot']),
            memory_before_comparator=width_view_matrix.decode_rle(row['ram_before_comparator']),
            memory_after=width_view_matrix.decode_rle(row['ram_after']),
            bound_before=test_stock_abi.raw(row['bound_before'],bound_size),bound_after=test_stock_abi.raw(row['bound_after'],bound_size),**cal))
    return parsed


def require_snapshot(case,observed):
    before=observed['memory_before'];after=observed['memory_after_snapshot'];actual=observed['snapshot_observer']
    context=observed['snapshot_context'];meta=matrix.snapshot_case(case)
    expected_gpr,t,expected=coherent.expected(matrix.WINDOW,meta,before,actual['continuation'])
    if after!=bytes(expected) or after!=numeric.snapshot(before) or observed['memory_before_comparator']!=after:
        raise ValueError('the pedal pair loses exact existing history, block bytes or continuous complete intermediate RAM')
    if (context!=matrix.snapshot_context(case) or context[11]!=0x22558 or context[7]!=0x20FA4
            or actual['sr_before']&0x301!=case['snapshot_t']
            or actual['abi_before'][:10]!=tuple(coherent.ABI) or actual['abi_before']!=actual['abi_after']
            or actual['sp']!=(actual['abi_before'][10]-164)&0xFFFFFFFF):
        raise ValueError('the pedal snapshot changes an existing entry premise, full ABI or natural SP')
    same(actual['exit'],((actual['sr_before']&~1)|t,actual['continuation'],context[17],context[16],context[15],*reversed(expected_gpr)),
         'the pedal snapshot changes independently computed full GPR/SR/specials or its existing return')
    frame=coherent.initial_frame(actual['continuation'])
    if actual['frame_before']!=frame or actual['frame_after']!=bytes(coherent.frame(matrix.WINDOW,meta,frame)):
        raise ValueError('the pedal snapshot changes its existing complete96-byte frame or helper stack values')
    if before[0x2672:0x2674]!=after[0x266E:0x2670] or before[0x2674:0x2676]!=after[0x2670:0x2672]:
        raise ValueError('the pedal snapshot changes either actual word of the registered history transfer')


def require_state(declared,image,case,observed):
    matrix.require_input(declared['source'],image,case,observed);require_snapshot(case,observed)
    actual=observed['comparator_observer'];context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=actual['continuation'].to_bytes(4,'big')
    if (actual['frame_before']!=bytes(frame) or actual['sp']!=actual['abi_before'][10]-164
            or actual['abi_before'][:10]!=packed_transfer_evidence.ABI or actual['abi_before']!=actual['abi_after']):
        raise ValueError('the pedal comparator changes its complete prepared frame, natural SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the pedal pair changes complete stock bytes, aliases, boundary or raw calibration')
    value=numeric.caller(observed['memory_before_comparator'],observed['calibration_before'],context)
    result=state.execute(declared['source'],fixture,context,observed['memory_before_comparator'],bytes(frame),
        actual['sp'],actual['continuation'],contract.ENTRY,actual['sr_before'],trace=True)
    transfers.require(dict(actual,context=context,memory_before=(observed['memory_before_comparator'],),
        memory_after=(observed['memory_after'],),calibration_before=observed['calibration_before']),result,value,fixture)
    return result,value


def held_key(observed):
    memory=bytearray(observed['memory_before']);incoming=bytes(memory[0x2672:0x2674]);memory[0x2672:0x2674]=bytes(2)
    phases=[]
    for key in ('snapshot_observer','comparator_observer'):
        value=observed[key];phases.append(dict(frame=value['frame_before'].hex(),sp=value['sp'],
            continuation=value['continuation'],abi=list(value['abi_before']),sr=value['sr_before']))
    value=dict(memory=memory.hex(),snapshot_context=list(observed['snapshot_context']),context=list(observed['context']),
        calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()},
        bound=observed['bound_before'].hex(),phases=phases,entries=[observed['snapshot_entry'],observed['entry']])
    return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode()),incoming


def require_causal_alternatives(pairs):
    groups={}
    for observed,value in pairs:
        actual=bool(observed['memory_after'][0x246A]&128)
        if actual!=value['pedal_high']:raise ValueError('the pedal causal group substitutes a scalar for actual246A.bit7')
        key,incoming=held_key(observed);groups.setdefault(key,[]).append((incoming,actual))
    if not any(a[0]!=b[0] and a[1]!=b[1] for rows in groups.values() for i,a in enumerate(rows) for b in rows[i+1:]):
        raise ValueError('the pedal pair lacks held-other actual2672 word changes in the final physical high-state bit')
    return dict(native_word=0xFFFF2672,snapshot_word=0xFFFF266E,actual_output_byte=0xFFFF246A,
                actual_output_mask=128,width_bytes=2,other_complete_phase_inputs_fixed=True)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the pedal pair changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the pedal raw pair grants itself semantic admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the pedal pair changes its owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the pedal pair changes current paired source inputs')
    names=(HARNESS,OBSERVER,SNAPSHOT_OBSERVER,Path(contract.UNIT['assembly']).name,Path(contract.SNAPSHOT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the pedal pair omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the pedal pair consumes another source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the pedal pair changes its private input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the pedal pair omits or changes a complete source dependency')
    reconstruction={}
    for name,unit in (('comparator',contract.UNIT),('snapshot',contract.SNAPSHOT)):
        reconstruction[name]=dict(code=[dict(start=r['start'],end=r['end'],stock=image[r['start']:r['end']].hex(),
            reconstructed=image[r['start']:r['end']].hex()) for r in unit['code']],
            pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),
                reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in unit['pools']])
    same(packet['reconstruction'],reconstruction,'the pedal pair changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the pedal pair changes a complete declared pointer relocation')
    same(packet['boundaries'],[dict(address=0x20FD0,bytes='57f6472a000b0009')],
         'the pedal pair changes the exact existing coherent observing boundary')
    same(packet['return_reconstruction'],[],'the pedal pair inserts a new return bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the pedal pair changes an undeclared fixture byte')
    ignition_literal_evidence.require_hash(packet['elf_sha256'])
    if type(packet['observer_object_sha256']) is not dict or set(packet['observer_object_sha256'])!={'invoke.o','snapshot-invoke.o'}:
        raise ValueError('the pedal pair omits one complete existing observer object')
    for value in packet['observer_object_sha256'].values():ignition_literal_evidence.require_hash(value)
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the pedal pair changes a complete actual terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the pedal pair changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_pedal_snapshot_high_state_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the pedal pair changes its runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the pedal pair executes another artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'snapshot-invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the pedal pair changes its existing GNU workflow or either observer')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the pedal pair changes its pinned GNU tools')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);pairs=[];seen=set();branches={};modes=set();decisions=set()
    source_sizes={r['address']:r['size'] for r in (*contract.DECLARED['control_blobs'],*contract.DECLARED['input_blobs'])}
    source_bytes={at:set() for at in source_sizes}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed)
        pairs.append((observed,{k:v for k,v in value.items() if k!='memory'}));seen.update(result['code'])
        modes.add(value['curve_mode']);decisions.add(value['temperature_decision'])
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
        for operand in result['accesses']:
            if operand['domain']!='rom' or operand['mode']!='read':continue
            for at,size in source_sizes.items():
                if at<=operand['address'] and operand['address']+operand['width_bytes']<=at+size:
                    source_bytes[at].update(range(operand['address'],operand['address']+operand['width_bytes']))
    if seen!=transfers.FEASIBLE_SITES:raise ValueError('the pedal pair omits a feasible complete comparator instruction or delay slot')
    for site in CONDITIONAL_SITES:
        wanted={transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'}
        if branches.get(site)!=wanted:raise ValueError('the pedal pair omits a real caller-scoped comparator branch outcome')
    if modes!={False,True} or decisions!={'set','clear','hold'}:raise ValueError('the pedal pair omits a complete actual comparator mode')
    for at,values in source_bytes.items():
        if values!=set(range(at,at+source_sizes[at])):raise ValueError('the pedal pair omits an actual physical curve/control byte')
    causal=require_causal_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),image_sha256=sha(image),
        fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_pedal_snapshot_high_state=True,complete_existing_prefix_and_continuous_RAM=True,
        complete_comparator_CPU_frame_and_physical_operands=True,causal_input=causal,
        branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('pedal_snapshot_high_state_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full paired pedal marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the pedal pair changes source inputs during admission')
    return result

CONDITIONAL_SITES=(155174, 156638, 157506, 158362, 293486, 293512, 293540, 293550, 293566, 293580, 293586, 293610, 293616, 293624, 293634, 293642, 293654, 293660, 293666, 293672, 293778, 293788, 293800, 293816, 293832, 293838, 293846, 293852, 293876, 293882, 293890, 293900, 293910, 293954, 293966, 293974, 293988, 294006, 294016, 294026, 294036, 294046, 294056, 294064, 294068, 294080, 294090, 294098, 294102, 294114, 294124, 294144, 294156, 294162, 294186, 294200, 294306, 294318, 294338, 294350, 294362, 294378, 294402, 294414, 294426, 294438, 294448, 294468, 294480, 294492, 294516, 294522, 294528, 294534, 294542, 294546, 294552)
