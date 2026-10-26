"""Independent complete natural AN1 dispatch state, physical sources and positive nested selected-table reads."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import an1_source_dispatch_access_contract as contract
from kb import an1_source_dispatch_access_matrix as matrix
from kb import an1_source_dispatch_access_semantics as semantics
from kb import an1_source_dispatch_access_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-an1-source-dispatch-access-paths'
PREFIX='kb-an1-source-dispatch-access-observation '
HEADER='an1-source-dispatch-access-cases.h'
HARNESS='harness-an1-source-dispatch-access-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
MARKER='VQ_SH_ELF_AN1_SOURCE_DISPATCH_ACCESS'
COMPONENT='an1_source_dispatch_access_paths'
OWNING_FLAGS=('complete_native_control_window','complete_two_lane_RAM_sequence','complete_natural_calls_and_physical_operands','complete_selected_table_and_actual_PID_publication')
OWNING_NON_ADMISSIONS=('native_identity_admission','native_geometry_inference','scale_admission',
    'units_admission','natural_caller_reachability','natural_scheduling_inference','hardware_qualification')
SOURCE_FILES=(contract.DESCRIPTOR,'defs/JK08A.an1-source-dispatch-access-paths.md',
    contract.UNIT['assembly'], 'tools/sh-elf-run/'+HARNESS,'tools/sh-elf-run/'+OBSERVER,
    'tools/sh-elf-run/an1_source_dispatch_access_capture.py',
    *(f'tools/kb/src/kb/an1_source_dispatch_access_{suffix}.py' for suffix in
        ('contract','matrix','semantics','transfers','capture_evidence')),
    *(f'tools/kb/tests/test_an1_source_dispatch_access_{suffix}.py' for suffix in
        ('contract','capture_evidence','native')),
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/test_stock_capture.py',
    'tools/kb/src/kb/test_stock_abi.py','tools/kb/src/kb/width_view_matrix.py',
    'tools/kb/src/kb/ignition_literal_evidence.py','tools/kb/src/kb/test_contract.py',
    'tools/kb/src/kb/packed_transfer_evidence.py',
    'defs/JK08A.an1-source-dispatch-access-claims.toml',
    'tools/kb/src/kb/an1_source_dispatch_access_native_contract.py',
    'tools/kb/src/kb/an1_source_dispatch_access_evidence.py',
    'tools/kb/src/kb/an1_source_dispatch_access_resolution.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def native_bindings(model):
    from kb import an1_source_dispatch_access_native_contract as owning
    row,=owning.descriptor(model.root)['reference']
    symbol=model.symbols.get(owning.symbol_key(row));function=model.symbols.get(SymbolKey('7mfk','fn',contract.ENTRY))
    if (not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',()))
            or symbol is None or symbol.meaning is None or symbol.meaning.key!='cautious-iguana/tbl'
            or function is None or function.meaning is None or function.meaning.key!='romantic-caiman/fn'
            or symbol.value('width') is not None or symbol.value('signed') is not None
            or row['original_claim_sha256']!=contract.DECLARED['selected']['original_claim_sha256']):
        raise ValueError('the AN1 dispatch changes its exact original owner,function,full closure or unset native type')
    return dict(original_claim_sha256=row['original_claim_sha256'],owner=row['owner'],entry='7mfk:0003d832',
        native_width=None,native_signed=None,scope='exact-natural-nested-table-reader')


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',source=source,
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),cases=list(matrix.cases(source,image)),
        calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,natural_caller_reachability=False,
        natural_scheduling_inference=False,hardware_qualification=False)


def objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the AN1 dispatch observation repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    marker=f'{MARKER} status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the AN1 dispatch omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the AN1 dispatch substitutes observations for actual original stdout')
    keys={'schema','index','entry','context','context_after','observation','ram_before','ram_after',
        'calibration_before','calibration_after','bound_before','bound_after','native_before','native_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the AN1 dispatch changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the AN1 dispatch changes its exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the AN1 dispatch mutates its complete const context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the AN1 dispatch truncates complete ordinary RAM')
        size=sum(size for at,size in declared['bound_spans'])
        parsed.append(dict(index=index,entry=row['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(memory['ram_before'],),memory_after=(memory['ram_after'],),
            bound_before=test_stock_abi.raw(row['bound_before'],size),bound_after=test_stock_abi.raw(row['bound_after'],size),
            native_before=test_stock_abi.raw(row['native_before'],256),native_after=test_stock_abi.raw(row['native_after'],256),**cal))
    return parsed


def require_state(declared,image,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=observed['abi_before'][10]-164
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the AN1 dispatch changes its complete prepared frame,natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the AN1 dispatch changes complete instructions,pools,aliases or physical calibration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.sequence(observed['memory_before'][0],observed['calibration_before'])
    transfers.require(observed,result,value,fixture)
    return result,value


def held_cell(observed,address):
    calibration={str(at):bytearray(raw) for at,raw in observed['calibration_before'].items()}
    incoming=calibration[str(0x12DEA)][address-0x12DEA]
    calibration[str(0x12DEA)][address-0x12DEA]=0
    bound=bytearray(observed['bound_before']);offset=0
    for row in contract.BOUND_SPANS:
        if row['address']<=address<row['address']+row['size']:bound[offset+address-row['address']]=0
        offset+=row['size']
    held=dict(memory=observed['memory_before'][0].hex(),native=observed['native_before'].hex(),
        calibration={at:bytes(raw).hex() for at,raw in calibration.items()},bound=bound.hex(),
        entry=observed['entry'],context=list(observed['context']),frame=observed['frame_before'].hex(),
        sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),sr=observed['sr_before'])
    return sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode()),incoming


def require_cell_alternatives(pairs):
    result={}
    for index in range(32):
        groups={}
        for observed,value in pairs:
            actual=observed['memory_after'][0][0x3F41]
            if actual!=value['publication']:raise ValueError('the AN1 causal group replaces the actual PID publication with a scalar')
            key,incoming=held_cell(observed,0x12DEA+index)
            groups.setdefault(key,[]).append((incoming,actual))
        if not any(a[0]!=b[0] and a[1]!=b[1] for rows in groups.values() for a in rows for b in rows):
            raise ValueError('the AN1 table lacks a changed actual PID byte with every other complete input fixed: '+str(index))
        result[str(index)]=True
    return result


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the AN1 dispatch original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the AN1 dispatch raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the AN1 dispatch original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the AN1 dispatch original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the AN1 dispatch original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the AN1 dispatch original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the AN1 dispatch original changes its private raw input-only header')
    for path in SOURCE_FILES:
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the AN1 dispatch original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the AN1 dispatch original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the AN1 dispatch original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the AN1 dispatch original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the AN1 dispatch original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the AN1 dispatch original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=4):
        raise ValueError('the AN1 dispatch original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_an1_source_dispatch_access_base')
    if simulator['command'][:3]!=[base.RUN,'--memory-region=0x01000000,64k','--memory-region=0xffff8400,256']:raise ValueError('the AN1 dispatch original changes its existing runner or memory profile')
    elf=Path(simulator['command'][3]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the AN1 dispatch original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the AN1 dispatch original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the AN1 dispatch original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);pairs=[];seen=set();branches={};native_values=set();table_bytes=set();histories=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed)
        pairs.append((observed,dict(publication=value['publication'])))
        seen.update(result['code']);native_values.add(observed['native_before'][0xC3]);histories.add(value['tags']['history'])
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
        for event in result['accesses']:
            if event['domain']=='rom' and 0x12DEA<=event['address']<0x12E0A:
                table_bytes.update(range(event['address'],event['address']+event['width_bytes']))
    if seen!=transfers.FEASIBLE_SITES:raise ValueError('the AN1 dispatch omits a feasible complete instruction or natural delay slot')
    for site in CONDITIONAL_SITES:
        wanted={transfers.FIXED_BRANCHES[site]} if site in transfers.FIXED_BRANCHES else {'taken','fallthrough'}
        if branches.get(site)!=wanted:raise ValueError('the AN1 dispatch omits a real caller-scoped gate or helper branch outcome')
    if native_values!=set(range(256)) or histories!={'initialize','update','hold'}:
        raise ValueError('the AN1 dispatch omits complete native control preimages or a history state')
    if table_bytes!=set(range(0x12DEA,0x12E0A)):raise ValueError('the AN1 dispatch omits a physical selected table cell')
    causal=require_cell_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_an1_source_dispatch_access_paths=True,actual_selected_table_access=True,
        complete_native_control_window=True,complete_two_lane_RAM_sequence=True,
        complete_natural_calls_and_physical_operands=True,complete_selected_table_and_actual_PID_publication=True,
        causal_cells=causal,branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_identity_admission=False,native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get(COMPONENT)
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full AN1 dispatch marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the AN1 inputs change during independent same-primary admission')
    return result


def require_owning_result(result):
    if (type(result) is not dict or result.get('exact_an1_source_dispatch_access_paths') is not True
            or result.get('actual_selected_table_access') is not True
            or any(result.get(flag) is not True for flag in OWNING_FLAGS)
            or any(result.get(flag) is not False for flag in OWNING_NON_ADMISSIONS)):
        raise ValueError('the AN1 owning boundary lacks its full independent positive natural-dispatch result')
    expected=dict(original_claim_sha256=contract.DECLARED['selected']['original_claim_sha256'],
        owner='cautious-iguana/tbl',entry='7mfk:0003d832',native_width=None,native_signed=None,
        scope='exact-natural-nested-table-reader')
    same(result.get('native_bindings'),expected,'the AN1 owning boundary substitutes its exact original or native reader scope')
    return True

CONDITIONAL_SITES=(138176, 138186, 138194, 138204, 138212, 138236, 156582, 157506, 158362, 250480, 250504, 250550, 250554, 250606, 250612, 250616, 250622, 250722, 250744, 250842, 250856, 250890, 250930, 250938, 250980, 250988, 251004, 251034, 251082, 251182, 251238, 251308, 251352, 251362, 251408, 251412, 251422, 251434, 251444, 251506, 251514, 251524, 251538, 251546, 251554, 251572, 251596, 251612, 251638, 251672, 251692, 251704, 251718, 251736, 251838, 251876, 251900, 251932)
