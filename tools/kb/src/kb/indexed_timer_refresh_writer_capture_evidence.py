"""Complete timer CPU, physical native/ordinary state and positive writer admission."""
import hashlib
import json
from pathlib import Path
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import indexed_timer_refresh_writer_contract as contract
from kb import indexed_timer_refresh_writer_matrix as matrix
from kb import indexed_timer_refresh_writer_semantics as semantics
from kb import indexed_timer_refresh_writer_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-indexed-timer-refresh-writer-paths'
PREFIX='kb-indexed-timer-refresh-writer-observation '
HEADER='indexed-timer-refresh-writer-cases.h'
HARNESS='harness-indexed-timer-refresh-writer-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
MARKER='VQ_SH_ELF_INDEXED_TIMER_REFRESH_WRITER'
COMPONENT='indexed_timer_refresh_writer_paths'
OWNING_FLAGS=('complete_native_control_window','complete_full_zero_nonzero_enable_paths',
    'complete_actual_critical_SR_and_R14_GBR_frame','complete_ordinary_native_state_and_physical_operands',
    'actual_exact_owner_reload_publications','complete_native_owner_function_TEST_ledger')
SOURCE_FILES=(contract.DESCRIPTOR,'defs/JK08A.indexed-timer-refresh-writer-claims.toml',
    'defs/JK08A.indexed-timer-refresh-writer.md',contract.UNIT['assembly'],
    'tools/sh-elf-run/'+HARNESS,'tools/sh-elf-run/'+OBSERVER,'tools/sh-elf-run/indexed_timer_refresh_writer_capture.py',
    *(f'tools/kb/src/kb/indexed_timer_refresh_writer_{suffix}.py' for suffix in
        ('contract','matrix','semantics','transfers','capture_evidence','access_contract','access_evidence','access_resolution')),
    *(f'tools/kb/tests/test_indexed_timer_refresh_writer_{suffix}.py' for suffix in ('contract','capture_evidence','access')),
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/test_stock_capture.py',
    'tools/kb/src/kb/test_stock_abi.py','tools/kb/src/kb/width_view_matrix.py',
    'tools/kb/src/kb/ignition_literal_evidence.py','tools/kb/src/kb/test_contract.py',
    'tools/kb/src/kb/packed_transfer_evidence.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def native_bindings(model):
    from kb import indexed_timer_refresh_writer_access_evidence as owning
    row=owning.native_rows(model)[0]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the timer writer omits its exact complete natural function')
    return [dict(symbol='7mfk-ffff43be/ram',meaning=row['owner'],function='7mfk-0009018c/fn',
        function_meaning='satisfied-myna/fn',original_claim_sha256=row['original_claim_sha256'])]


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
        if key in result:raise ValueError('the timer writer observation repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=objects) for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    marker=f'{MARKER} status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the timer writer omits or duplicates its complete ordered natural-entry stream')
    same(packet['observations'],rows,'the timer writer substitutes observations for actual original stdout')
    keys={'schema','index','entry','context','context_after','observation','ram_before','ram_after',
        'calibration_before','calibration_after','bound_before','bound_after','native_before','native_after'}
    parsed=[]
    for index,row in enumerate(rows):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the timer writer changes its complete raw schema')
        same({key:row[key] for key in ('schema','index','entry')},dict(schema=1,index=index,entry=contract.ENTRY),
            'the timer writer changes its exact invocation order or natural entry')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:raise ValueError('the timer writer mutates its complete const context')
        out=test_stock_abi.raw(row['observation'],572);cal={}
        for name in ('calibration_before','calibration_after'):
            raw=test_stock_abi.raw(row[name],sum(size for at,size in declared['calibration_spans']));offset=0;cal[name]={}
            for at,size in declared['calibration_spans']:cal[name][at]=raw[offset:offset+size];offset+=size
        memory={name:width_view_matrix.decode_rle(row[name]) for name in ('ram_before','ram_after')}
        if any(len(raw)!=matrix.RAM_SIZE for raw in memory.values()):raise ValueError('the timer writer truncates complete ordinary RAM')
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
        raise ValueError('the timer writer changes its complete prepared frame,natural SP or external caller ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the timer writer changes complete instructions,pools,aliases or physical calibration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],
        bytes(frame),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(observed['entry'],observed['memory_before'][0],observed['calibration_before'],
        observed['context'],observed['sr_before'],bytes(frame),observed['sp'],observed['continuation'])
    transfers.require(observed,result,value,fixture)
    return result,value


def require_causal_alternatives(pairs):
    groups={};native_pairs={};changed_native=False;owner_seen=False
    for observed,value in pairs:
        if observed['context'][4]==6 and value['refreshed']:
            raw=observed['memory_after'][0][0x43BE:0x43BF]
            expected=observed['calibration_before'][0x8E23]
            if raw!=expected:raise ValueError('the timer writer detaches the actual43BE byte from the complete physical reload source')
            cal={str(at):data.hex() for at,data in observed['calibration_before'].items()};cal[str(0x8E23)]='00'
            bound=bytearray(observed['bound_before']);offset=0
            for span in contract.BOUND_SPANS:
                if span['address']==0x8E23:bound[offset]=0
                offset+=span['size']
            held=dict(memory=observed['memory_before'][0].hex(),native=observed['native_before'].hex(),
                context=observed['context'],frame=observed['frame_before'].hex(),sp=observed['sp'],
                continuation=observed['continuation'],abi=observed['abi_before'],sr=observed['sr_before'],
                calibration=cal,bound=bytes(bound).hex(),entry=observed['entry'])
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            groups.setdefault(key,[]).append((expected,raw));owner_seen=True
        if value['native_reset_written']:
            before=observed['native_before'][12];after=observed['native_after'][12]
            if after!=before|128:raise ValueError('the timer writer substitutes an echo or arbitrary native reset byte for the real OR80')
            memory=bytearray(observed['memory_before'][0]);memory[0x850C]=0
            native=bytearray(observed['native_before']);native[12]=0
            held=dict(memory=memory.hex(),native=native.hex(),context=observed['context'],frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=observed['abi_before'],sr=observed['sr_before'],
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()},bound=observed['bound_before'].hex(),entry=observed['entry'])
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            native_pairs.setdefault(key,[]).append((before,after));changed_native|=before!=after
    if not owner_seen or not any(any(a[0]!=b[0] and a[1]!=b[1] for a in rows for b in rows) for rows in groups.values()):
        raise ValueError('the timer writer lacks changed actual43BE publications with every complete other input fixed')
    if not changed_native or not any(any(a[0]!=b[0] and a[1]!=b[1] and a[0]!=a[1] and b[0]!=b[1]
            for a in rows for b in rows) for rows in native_pairs.values()):
        raise ValueError('the timer writer lacks distinct actual computed native reset bytes with every other complete input fixed')
    return dict(exact_owner_refresh=True,actual_native_OR80=True)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the timer writer original changes its complete actual capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the timer writer raw packet grants itself admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the timer writer original changes its complete owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the timer writer original changes its exact current paired source inputs')
    names=(HARNESS,OBSERVER,Path(contract.UNIT['assembly']).name)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the timer writer original omits a complete consumed executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;raw=(root/path).read_bytes()
        if packet['consumed'][name]!=raw.hex() or inputs.get(path)!=sha(raw):raise ValueError('the timer writer original consumes another complete source snapshot')
    if packet['consumed'][HEADER]!=matrix.header(declared,image).hex():raise ValueError('the timer writer original changes its private raw input-only header')
    for path in SOURCE_FILES:
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the timer writer original omits or changes a complete independent source dependency')
    reconstruction=dict(code=[dict(start=a,end=b,stock=image[a:b].hex(),reconstructed=image[a:b].hex()) for a,b in contract.SPANS],
        pools=[dict(address=r['address'],stock=image[r['address']:r['address']+r['size']].hex(),reconstructed=image[r['address']:r['address']+r['size']].hex()) for r in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the timer writer original changes exact independent GNU reconstruction')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the timer writer original changes an exact declared pointer alias')
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),'the timer writer original replaces a natural return or inserts a stock call bridge')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the timer writer original changes an undeclared fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):raise ValueError('the timer writer original changes complete actual terminal streams')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=4):
        raise ValueError('the timer writer original changes its bounded actual simulator terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_indexed_timer_refresh_writer_base')
    if simulator['command'][:3]!=[base.RUN,'--memory-region=0x01000000,64k','--memory-region=0xffff8500,256']:raise ValueError('the timer writer original changes its existing runner or memory profile')
    elf=Path(simulator['command'][3]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the timer writer original executes another domain artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}','-Wl,--section-start=.rom=0',
        '-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the timer writer original changes the existing GNU workflow, observer or fixture sources')
    tools=packet['toolchain']
    if (type(tools) is not dict or set(tools)!={'simulator_version','gcc_version','binaries'}
            or tools['simulator_version']!='16.3' or tools['gcc_version']!='13.3.0'
            or set(tools['binaries'])!={'as','ld','objcopy','gcc','run'}):raise ValueError('the timer writer original changes its pinned GNU toolchain')
    for value in tools['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);pairs=[];seen=set();branches={};paths=set();native_values=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed)
        pairs.append((observed,value));seen.update(result['code']);native_values.add(observed['native_before'][12])
        if value['blocked']:paths.add('judged-blocked')
        elif not value['enabled']:paths.add('disabled-refresh')
        elif value['native_reset_written']:paths.add('critical-native-reset')
        else:paths.add('already-armed-path')
        if value['indicator'] and value['enabled'] and not value['blocked']:
            paths.add('timer-live' if value['timer_live'] else 'timer-expired-latch')
        if value['refreshed'] and value['enabled']:paths.add('indicator-clear-refresh')
        for branch in result['branches']:
            if branch['kind'] in ('taken','fallthrough'):branches.setdefault(branch['site'],set()).add(branch['kind'])
    if seen!=transfers.FEASIBLE_SITES:raise ValueError('the timer writer omits a full feasible instruction or real delay slot')
    if any(branches.get(site)!={'taken','fallthrough'} for site in transfers.CONDITIONAL_SITES):
        raise ValueError('the timer writer omits a real zero/nonzero enable,native or timer conditional outcome')
    if native_values!=set(range(256)):raise ValueError('the timer writer omits full raw native reset byte preimages')
    if paths!={'judged-blocked','disabled-refresh','critical-native-reset','already-armed-path','timer-live','timer-expired-latch','indicator-clear-refresh'}:
        raise ValueError('the timer writer omits an actual ordinary/native/SR or positive timer path')
    causal=require_causal_alternatives(pairs)
    return dict(region=REGION,observations=len(actual),native_bindings=native_bindings(model),
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],
        exact_indexed_timer_refresh_writer_paths=True,complete_native_control_window=True,complete_full_zero_nonzero_enable_paths=True,
        complete_actual_critical_SR_and_R14_GBR_frame=True,complete_ordinary_native_state_and_physical_operands=True,
        actual_exact_owner_reload_publications=True,complete_native_owner_function_TEST_ledger=True,
        causal_inputs=causal,branch_outcomes={f'{site:08x}':sorted(values) for site,values in branches.items()},
        native_identity_admission=False,native_geometry_inference=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get(COMPONENT)
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique full timer writer marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the timer writer inputs change during independent same-primary admission')
    return result


def require_owning_result(result):
    if type(result) is not dict or result.get('exact_indexed_timer_refresh_writer_paths') is not True or any(result.get(flag) is not True for flag in OWNING_FLAGS):
        raise ValueError('the timer owning boundary lacks a complete independent native,state,physical or positive writer result')
    return True
