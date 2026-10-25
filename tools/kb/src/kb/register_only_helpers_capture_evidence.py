"""Independent natural register-helper state and exact absence of datum access."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract
from kb import register_only_helpers_contract as contract,register_only_helpers_matrix as matrix
from kb import register_only_helpers_semantics as semantics
from kb.model import SymbolKey

REGION='jk08a-register-only-helper-paths'
PREFIX='kb-register-only-helper-observation '
HEADER='register-only-helper-cases.h'
HARNESS='harness-register-only-helper-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0x259D4,0x26742)
SOURCE_FILES=('tools/kb/src/kb/register_only_helpers_contract.py',
    'tools/kb/src/kb/register_only_helpers_matrix.py','tools/kb/src/kb/register_only_helpers_semantics.py',
    'tools/kb/src/kb/register_only_helpers_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/test_stock_capture.py',contract.DESCRIPTOR,
    'defs/JK08A.register-only-withdrawals.toml',
    'tools/kb/src/kb/register_only_withdrawal_contract.py',
    'tools/kb/src/kb/register_only_withdrawal_evidence.py',
    'tools/kb/src/kb/register_only_withdrawal_resolution.py',
    'tools/kb/tests/test_channel_pulse_chain.py','tools/kb/tests/test_fuel_cut_consumer_chain.py',
    'tools/kb/tests/test_engine_speed_byte_tables.py')


def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the register-only original omits an exact natural entry')
    from kb import register_only_withdrawal_contract as withdrawal
    rows=withdrawal.descriptor(model.root)['reference'];result=[]
    for row in rows:
        symbol=model.symbols.get(withdrawal.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None
                or function.meaning.key!=json.loads(row['original_claim_json'])['to']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (withdrawal.native_type(row,'width'),withdrawal.native_type(row,'signed')))):
            raise ValueError('the register-only original changes a retained exact owner, function or native type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],function=function.key.key,
            function_meaning=function.meaning.key,original_claim_sha256=row['original_claim_sha256']))
    if len(result)!=12:raise ValueError('the register-only original omits an exact original withdrawal identity')
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),
        calibration_spans=[[row['address'],row['size']] for row in contract.OBSERVED_SPANS],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    return proof_adapter.header(declared['source']['adapter'],declared['cases'],
        lambda case: matrix.context(declared['source'],case),
        lambda case: matrix.calibrations(declared['source'],image,case))


def observations(packet,declared):
    return proof_transport.decode(packet,declared,declared['source']['adapter'])


def require_state(declared,image,case,observed,root):
    matrix.require_input(declared['source'],image,case,observed)
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the register-only original changes a complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the register-only original changes a complete natural instruction span')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(case['entry'],observed['context'],observed['sr_before'],bytes(frame),
        observed['sp'],observed['continuation'])
    require_scalar_state(observed,result,value)
    return result,value


def require_scalar_state(observed,result,value):
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the register-only original changes complete independent instruction state')
    same(observed['exit'],value['exit'],'the register-only original changes independent complete scalar register/SR state')
    if (observed['frame_after']!=result['frame'] or observed['frame_after']!=value['frame']
            or observed['memory_after']!=(result['ram'],) or observed['memory_after']!=observed['memory_before']):
        raise ValueError('the register-only original changes an independent complete stack or no-datum RAM expectation')
    same(result['accesses'],value['physical'],'the register-only original changes its ordered frame-only physical accesses')
    same(result['branches'],value['branches'],'the register-only original changes an independent branch or natural return')
    if result['calls'] or tuple(result['code'])!=value['path']:
        raise ValueError('the register-only original changes its complete independent natural path or invents a call')
    trace=result.get('trace')
    if type(trace) is not list or tuple(row['site'] for row in trace)!=value['path']:
        raise ValueError('the register-only original omits its complete delayed natural path trace')
    delayed={row['site']+2 for row in value['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the register-only original changes a conditional or RTS delay slot')
    returned=[row for row in trace if row['site']==value['return_site']]
    if len(returned)!=1 or returned[0]['before']['pr']!=observed['continuation']:
        raise ValueError('the register-only original substitutes its natural return carrier')
    last=trace[-1]
    if (last['next']!=observed['continuation'] or last['after']['registers'][15]!=observed['sp']
            or tuple(last['after']['registers'][:15])!=value['registers']):
        raise ValueError('the register-only original changes its post-delay returned register/SP state')


def require_positive_alternatives(actual):
    arguments={0x224F8:(0,),0x224FA:(0,),0x2251C:(0,),0x259D0:(4,5,6,7),
        0x26740:(0,2,3),0x50A4C:(4,5,6)}
    for entry,registers in arguments.items():
        for register in registers:
            groups={}
            for observed in actual:
                if observed['entry']!=entry:continue
                context=list(observed['context']);incoming=context[register];context[register]=0
                frame=bytearray(observed['frame_before'])
                if register==7:frame[164:168]=bytes(4)
                held=dict(context=context,frame=bytes(frame).hex(),memory=observed['memory_before'][0].hex(),
                    sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                    sr=observed['sr_before'],entry=entry,bound=observed['bound_before'].hex(),
                    calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
                key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
                groups.setdefault(key,set()).add((incoming,observed['exit'][-1]))
            if not any(len({row[0] for row in group})>=2 and len({row[1] for row in group})>=2 for group in groups.values()):
                raise ValueError('the register-only original lacks actual R0 variation with fixed-other register arguments')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the register-only original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the register-only raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the register-only original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the register-only original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the register-only original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the register-only original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the register-only original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/register_only_helpers_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a register-only independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the register-only independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the register-only fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the register-only fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the register-only original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the register-only original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_register_only_helpers_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the register-only original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the register-only original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the register-only original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the register-only original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};seen=set();entries=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed,root);entries.add(observed['entry']);seen.update(result['code'])
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
    if entries!=set(contract.ENTRIES) or seen!={site for first,last in contract.SPANS for site in range(first,last,2)}:
        raise ValueError('the register-only original omits a natural entry, branch instruction or delayed instruction')
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the register-only original omits a feasible conditional branch outcome')
    require_positive_alternatives(actual)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_register_only_paths=True,no_datum_access=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        native_identity_admission=False,native_geometry_inference=False,automatic_resolution=False,
        scale_admission=False,units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),
        'the register-only original replaces a natural return with an outside-code return')


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('register_only_helper_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual register-only original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the register-only inputs change during independent consumption')
    return result
