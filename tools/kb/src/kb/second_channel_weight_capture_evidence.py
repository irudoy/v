"""Independent complete optional timing publication, local carrier and causal admission."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state, ignition_literal_evidence, packed_transfer_evidence
from kb import repo, test_contract, test_stock_abi, width_view_matrix
from kb import second_channel_weight_contract as contract, second_channel_weight_matrix as matrix
from kb import second_channel_weight_semantics as semantics, second_channel_weight_transfers as transfers
from kb import word_interp_caller_withdrawal_capture_evidence as complete_word,division_callees_capture_evidence as complete_division

REGION = 'jk08a-second-channel-weight-paths'
PREFIX = 'kb-second-channel-weight-observation '
HEADER = 'second-channel-weight-cases.h'
HARNESS = 'harness-second-channel-weight-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
MARKER = 'VQ_SH_ELF_SECOND_CHANNEL_WEIGHT'
SOURCE_FILES = (contract.DESCRIPTOR, 'defs/JK08A.second-channel-weight-claims.toml', 'defs/JK08A.second-channel-weight.md',
    *(f'tools/kb/src/kb/second_channel_weight_{suffix}.py' for suffix in
      ('contract', 'matrix', 'semantics', 'transfers', 'capture_evidence', 'access_contract', 'access_evidence', 'access_resolution')),
    'tools/sh-elf-run/second_channel_weight_capture.py', contract.UNIT['assembly'],
    'tools/sh-elf-run/' + HARNESS, 'tools/sh-elf-run/' + OBSERVER,
    *(f'tools/kb/tests/test_second_channel_weight_{suffix}.py' for suffix in ('contract', 'capture_evidence', 'access')),
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
    from kb import second_channel_weight_access_evidence as owning
    row = owning.native_rows(model)[0]
    if not set(contract.FUNCTIONS) <= set(model.functions.get('7mfk', ())):
        raise ValueError('the second-channel weight omits a complete required natural entry or helper')
    return dict(original_claim_sha256=row['original_claim_sha256'], owner=row['owner'],
                entry='7mfk:0007a804', native_width=None, native_signed=None)

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
        if key in value:raise ValueError('the second-channel weight observation repeats a raw JSON key')
        value[key]=item
    return value

def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    count=len(declared['cases']);marker=f'{MARKER} status=PASS region={REGION} cases={count}'
    if len(rows)!=count or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the second-channel weight original omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the second-channel weight packet substitutes observations for original stdout')
    keys={'schema','index','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the second-channel weight observation changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the second-channel weight original changes exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the second-channel weight original mutates its immutable complete context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the second-channel weight observation truncates complete relocated RAM')
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
        raise ValueError('the second-channel weight original changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the second-channel weight original changes complete instructions, pools, aliases or raw calibration')
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
        if len(spans)!=1:raise ValueError('the second-channel weight causal group loses an exact physical calibration span')
        at,raw=spans[0];offset=address-int(at);incoming=bytes(raw[offset:offset+width]);raw[offset:offset+width]=bytes(width)
        bound=mask_bound(bound,address,width)
    else:raise ValueError('the second-channel weight causal group substitutes a frame or synthetic intermediate input')
    held=dict(memory=memory.hex(),calibration={at:bytes(raw).hex() for at,raw in cal.items()},bound=bound.hex(),
        entry=observed['entry'],context=list(observed['context']),frame=observed['frame_before'].hex(),
        sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),sr=observed['sr_before'])
    return sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode()),incoming

CAUSAL_INPUTS=tuple((0x16F48+i*2,2,f'weight-surface-word-{i}',False) for i in range(64))+(
    (0x1630C,2,'raw-substitute-weight',True),)

def require_causal_alternatives(pairs):
    admitted={}
    for address,width,name,substitute in CAUSAL_INPUTS:
        groups={}
        for observed,value in pairs:
            if value['substitute']!=substitute:continue
            memory=observed['memory_after'][0]
            actual=tuple(int.from_bytes(memory[at:at+2],'big') for at in (0x35F4,0x35CA,0x35CC,0x1248))
            same(actual,(value['weight'],value['blended'],value['output'],value['value']),
                'the weight causal group substitutes scalars for actual publications')
            key,incoming=held_key(observed,address,width,'rom')
            groups.setdefault(key,[]).append((incoming,*actual))
        found=False
        for rows in groups.values():
            for a in rows:
                for z in rows:
                    if all(a[i]!=z[i] for i in range(5)):
                        found=True;break
                if found:break
            if found:break
        if not found:
            raise ValueError('the weight quantity lacks changed actual publications with every other input fixed: '+name)
        admitted[name]=True
    return admitted

def require_prior_invariance(pairs):
    groups={};seen={False:False,True:False}
    for observed,value in pairs:
        key,incoming=held_key(observed,matrix.RAM_BASE+0x35F4,2,'ram')
        outcome=(observed['memory_after'],observed['exit'],observed['frame_after'],
                 value['weight'],value['blended'],value['output'],value['value'])
        groups.setdefault((value['substitute'],key),[]).append((incoming,outcome))
    for (substitute,key),rows in groups.items():
        for a in rows:
            for z in rows:
                if a[0]!=z[0]:
                    seen[substitute]=True
                    same(a[1],z[1],'the second-channel quantity consumes overwritten prior35F4 RAM')
    if not all(seen.values()):
        raise ValueError('the second-channel quantity omits independent prior35F4 controls on either weight path')
    return {'surface':seen[False],'substitute':seen[True]}

def require_guard_invariance(pairs):
    admitted={}
    for address,name,alternate in ((0x18D56,'last-common-curve-guard',False),
                                    (0x190D0,'last-alternate-curve-guard',True)):
        groups={}
        for observed,value in pairs:
            if value['alternate']!=alternate:continue
            matches=[r for r in value['lookups'] if r['kind']=='word-curve'
                     and r['base']==(0x190B0 if alternate else 0x18D36)]
            if len(matches)!=1 or matches[0]['index']!=15 or matches[0]['fraction']!=0:continue
            key,incoming=held_key(observed,address,2,'rom')
            expected=dict(site=0x266FA,mode='read',address=address,width_bytes=2,register=0,
                          domain='rom',bytes=incoming.hex())
            if sum(test_contract.exact(r,expected) for r in value['operands'])!=1:
                raise ValueError('the second-channel endpoint omits its actual seventeenth physical word')
            outcome=(observed['memory_after'],value['first_curve'],value['second_curve'],
                     value['common_curve'],value['weight'],value['blended'],value['output'],value['value'])
            groups.setdefault(key,[]).append((incoming,outcome))
        seen=False
        for rows in groups.values():
            for a in rows:
                for z in rows:
                    if a[0]!=z[0]:
                        seen=True
                        same(a[1],z[1],'the word endpoint assigns a nonzero result weight to its physical guard')
        if not seen:raise ValueError('the word endpoint omits held-other physical guard controls: '+name)
        admitted[name]=True
    return admitted

def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the second-channel weight original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the second-channel weight raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the second-channel weight original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the second-channel weight original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the second-channel weight original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the second-channel weight original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the second-channel weight original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the second-channel weight original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the second-channel weight original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the second-channel weight original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the second-channel weight original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the second-channel weight original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the second-channel weight original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the second-channel weight original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_second_channel_weight_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the second-channel weight original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the second-channel weight original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the second-channel weight original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the second-channel weight original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);pairs=[];seen=set();branches={}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed);pairs.append((observed,value));seen.update(result['code'])
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
    if seen!=transfers.FEASIBLE_SITES:
        raise ValueError('the second-channel weight omits a complete feasible instruction, natural call or real delay slot')
    if set(branches)!=set(CONDITIONAL_SITES) or any(branches[site]!=(
            {transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'})
            for site in CONDITIONAL_SITES):
        raise ValueError('the second-channel weight omits a real mode, clamp, arithmetic or diagnostic branch outcome')
    causal=require_causal_alternatives(pairs);prior=require_prior_invariance(pairs);guards=require_guard_invariance(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_second_channel_weight_paths=True,actual35F4_publication_complete_liveR5_and_outputs=True,
        overwritten_prior35F4_invariant=prior,physical_guard_value_invariant=guards,
        complete_natural_entry_RAM_frame_and_CPU=True,causal_inputs=causal,
        branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    complete_word.require_primary(model,record)
    complete_division.require_primary(model,record)
    packet=record['candidate']['witness'].get('second_channel_weight_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full indexed word reader marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the second-channel weight source inputs change during independent admission')
    return dict(result,complete_existing_word_interpolation_and_division_originals_same_primary=True)

CONDITIONAL_SITES=(138468, 138474, 138482, 158458, 158530, 158544, 158572, 158604, 158608, 158612, 158648, 158994, 501792, 501852, 501918, 501924, 501950, 501980, 502028, 502072, 502086, 502098, 502112)
