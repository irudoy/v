"""Independent two-phase stock quantity, full-state continuity and causal admission."""
import hashlib,json
from pathlib import Path
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo,test_contract,test_stock_abi,width_view_matrix
from kb import coasting_term_quantity_contract as contract,coasting_term_quantity_matrix as matrix
from kb import coasting_term_quantity_semantics as semantics,coasting_term_quantity_transfers as transfers
from kb import byte_factor_caller_withdrawal_capture_evidence as complete_original

REGION='jk08a-coasting-term-quantity-paths'
PREFIX='kb-coasting-term-quantity-observation '
HEADER='coasting-term-quantity-cases.h'
HARNESS='harness-coasting-term-quantity-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
MARKER='VQ_SH_ELF_COASTING_TERM_QUANTITY'
SOURCE_FILES=(contract.DESCRIPTOR,'defs/JK08A.coasting-term-quantity-claims.toml','defs/JK08A.coasting-term-quantity.md',
    *(f'tools/kb/src/kb/coasting_term_quantity_{suffix}.py' for suffix in ('contract','matrix','semantics','transfers','capture_evidence','access_contract','access_evidence','access_resolution')),
    'tools/sh-elf-run/coasting_term_quantity_capture.py',contract.UNIT['assembly'],
    'tools/sh-elf-run/'+HARNESS,'tools/sh-elf-run/'+OBSERVER,
    *(f'tools/kb/tests/test_coasting_term_quantity_{suffix}.py' for suffix in ('contract','capture_evidence','access')),
    'tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/packed_transfer_evidence.py','tools/kb/src/kb/test_stock_capture.py',
    'tools/kb/src/kb/width_view_matrix.py','tools/kb/src/kb/ignition_literal_evidence.py')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def same(a,b,reason):
    if not test_contract.exact(a,b):raise ValueError(reason)

def native_bindings(model):
    from kb import coasting_term_quantity_access_evidence as owning
    row=owning.native_rows(model)[0]
    if not set(contract.ENTRIES)<=set(model.functions.get('7mfk',())):
        raise ValueError('the quantity original omits either complete natural stock phase entry')
    return dict(original_claim_sha256=row['original_claim_sha256'],owner=row['owner'],
        producer='7mfk:0002c626',consumer='7mfk:00047120',native_width=None,native_signed=None)

def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',source=source,
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),cases=list(matrix.cases(source,image)),
        phases=[dict(r) for r in source['phases']],calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS],semantic_admission=False,
        native_geometry_inference=False,natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)

def objects(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('the quantity observation repeats a raw JSON key')
        value[key]=item
    return value

def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    count=len(declared['cases']);marker=f'{MARKER} status=PASS region={REGION} pairs={count} phases={2*count}'
    if len(rows)!=count*2 or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the quantity original omits or duplicates its complete ordered two-phase stream')
    same(packet['observations'],rows,'the quantity packet substitutes observations for its original stdout')
    keys={'schema','pair','phase','phase_id','entry','context','context_after','observation',
        'ram_before','ram_after','calibration_before','calibration_after','bound_before','bound_after'}
    parsed=[]
    for index,row in enumerate(rows):
        phase=index%2;pair=index//2
        if type(row) is not dict or set(row)!=keys:raise ValueError('the quantity phase changes its complete raw schema')
        same({k:row[k] for k in ('schema','pair','phase','phase_id','entry')},
            dict(schema=1,pair=pair,phase=phase,phase_id=contract.PHASES[phase],entry=contract.ENTRIES[phase]),
            'the quantity original changes exact phase order, pair identity or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the quantity phase mutates its immutable complete context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(n for at,n in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the quantity phase truncates complete relocated RAM')
        size=sum(n for at,n in declared['bound_spans'])
        parsed.append(dict(pair=pair,phase=phase,phase_id=row['phase_id'],entry=row['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(memory['ram_before'],),memory_after=(memory['ram_after'],),
            bound_before=test_stock_abi.raw(row['bound_before'],size),bound_after=test_stock_abi.raw(row['bound_after'],size),**cal))
    return parsed

def require_state(declared,image,case,observed,phase,previous=None):
    matrix.require_input(declared['source'],image,case,observed,phase,previous)
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=observed['abi_before'][10]-164
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the quantity phase changes its complete prepared frame, natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the quantity phase changes exact instructions, pools, aliases or raw calibration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(phase,observed['memory_before'][0],observed['calibration_before'])
    transfers.require(observed,result,value,fixture)
    return result,value

def mask_bound(raw,address,width):
    out=bytearray(raw);offset=0
    for row in contract.BOUND_SPANS:
        start,size=row['address'],row['size'];first=max(start,address);last=min(start+size,address+width)
        if first<last:out[offset+first-start:offset+last-start]=bytes(last-first)
        offset+=size
    return bytes(out)

def held_key(producer,consumer,address,width,domain):
    memory=bytearray(producer['memory_before'][0]);cal={str(at):bytearray(raw) for at,raw in producer['calibration_before'].items()}
    incoming=None;bound=producer['bound_before']
    if domain=='ram':
        offset=address-matrix.RAM_BASE;incoming=bytes(memory[offset:offset+width]);memory[offset:offset+width]=bytes(width)
    elif domain=='rom':
        spans=[(at,raw) for at,raw in cal.items() if int(at)<=address and address+width<=int(at)+len(raw)]
        if len(spans)!=1:raise ValueError('the quantity causal group loses an exact selected physical calibration span')
        at,raw=spans[0];offset=address-int(at);incoming=bytes(raw[offset:offset+width]);raw[offset:offset+width]=bytes(width)
        bound=mask_bound(bound,address,width)
    else:raise ValueError('the quantity causal group substitutes a frame or synthetic handoff input')
    held=dict(memory=memory.hex(),calibration={at:bytes(raw).hex() for at,raw in cal.items()},bound=bound.hex(),
        phases=[dict(entry=o['entry'],phase=o['phase'],context=list(o['context']),frame=o['frame_before'].hex(),
            sp=o['sp'],continuation=o['continuation'],abi=list(o['abi_before']),sr=o['sr_before']) for o in (producer,consumer)])
    return sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode()),incoming


CAUSAL_INPUTS=tuple(('rom',0x122E2+i,1,f'source-cell-{i}') for i in range(8))

def require_causal_alternatives(pairs):
    admitted={}
    for domain,address,width,name in CAUSAL_INPUTS:
        groups={}
        for producer,consumer,pvalue,cvalue in pairs:
            actual=consumer['memory_after'][0][0x13EA:0x13EC]
            if actual!=cvalue['value'].to_bytes(2,'big'):
                raise ValueError('the coasting causal group detaches its actual final13EA publication')
            key,incoming=held_key(producer,consumer,address,width,domain)
            groups.setdefault(key,[]).append((incoming,actual,pvalue,cvalue))
        found=False
        for rows in groups.values():
            for a in rows:
                for z in rows:
                    if (a[0]!=z[0] and a[1]!=z[1] and a[2]['value']!=z[2]['value']
                            and a[3]['source_word']==a[2]['value'] and z[3]['source_word']==z[2]['value']):
                        found=True;break
                if found:break
            if found:break
        if not found:
            raise ValueError('the coasting original lacks changed actual carried words and final13EA with every other complete input fixed: '+name)
        admitted[name]=True
    return admitted


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the quantity original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the quantity raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the quantity original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the quantity original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the quantity original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the quantity original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the quantity original changes its private raw input-only header')
    for path in (*SOURCE_FILES,*contract.DECLARED['reused_source_sha256']):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the quantity original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the quantity original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the quantity original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the quantity original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the quantity original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the quantity original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the quantity original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_coasting_term_quantity_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:raise ValueError('the quantity original changes its existing runner or memory profile')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the quantity original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the quantity original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the quantity original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)

    actual=observations(packet,declared);pairs=[];seen=set();branches={};source_sites=set()
    for i,case in enumerate(declared['cases']):
        completion,boundary=actual[2*i:2*i+2]
        presult,pvalue=require_state(declared,image,case,completion,0)
        cresult,cvalue=require_state(declared,image,case,boundary,1,completion)
        transfers.require_handoff(completion,boundary,pvalue,cvalue);pairs.append((completion,boundary,pvalue,cvalue))
        for result in (presult,cresult):
            seen.update(result['code'])
            for row in result['branches']:
                if row['kind'] in ('taken','fallthrough'):branches.setdefault(row['site'],set()).add(row['kind'])
        source_sites.update(event['site'] for event in pvalue['operands'] if event['mode']=='read' and 0x122E2<=event['address']<0x122EA)
    if seen!=transfers.FEASIBLE_SITES:raise ValueError('the coasting pair omits a complete feasible instruction or real delay slot')
    if source_sites!={0x26380,0x26AAC,0x26AAE}:
        raise ValueError('the coasting pair omits a real source-table endpoint or interpolated byte read')
    if set(branches)!=set(CONDITIONAL_SITES) or any(branches[site]!=({transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'}) for site in CONDITIONAL_SITES):
        raise ValueError('the coasting pair omits a real conditional mode, signed comparison or admission outcome')
    causal=require_causal_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),pairs=len(pairs),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_coasting_term_quantity_paths=True,complete_RAM_calibration_bound_continuity=True,
        actual_source_curve_carried_words_and_coasting_publication=True,causal_inputs=causal,
        branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)

def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    complete_original.require_primary(model,record)
    packet=record['candidate']['witness'].get('coasting_term_quantity_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual coasting pair marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the coasting source inputs change during independent admission')
    return dict(result,complete_existing_byte_factor_original_same_primary=True)

CONDITIONAL_SITES=(155174,
 155222,
 155230,
 155238,
 155246,
 155254,
 155262,
 155270,
 155278,
 155286,
 155298,
 155310,
 155322,
 156534,
 156558,
 157506,
 158362,
 291128,
 291138,
 291156,
 291168,
 291182,
 291196,
 291224,
 291240,
 291248,
 291258,
 291264,
 291288,
 291296,
 291328,
 291336,
 291362,
 291374,
 291390,
 291400,
 291428,
 291446,
 291480,
 291504,
 291556,
 291562,
 291574,
 291596,
 291618,
 291636,
 291648)
