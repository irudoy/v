"""Independent complete standalone signed-magnitude helper, NEG-minimum and selected native RAM-root absence."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport
from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract
from kb import signed_abs_register_helper_withdrawal_contract as contract,signed_abs_register_helper_withdrawal_matrix as matrix
from kb import signed_abs_register_helper_withdrawal_semantics as semantics,signed_abs_register_helper_withdrawal_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-signed-abs-register-helper-withdrawal-paths'
PREFIX='kb-signed-abs-register-helper-withdrawal-observation '
HEADER='signed-abs-register-helper-withdrawal-cases.h'
HARNESS='harness-signed-abs-register-helper-withdrawal-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (140690,)
SOURCE_FILES = ('tools/kb/src/kb/signed_abs_register_helper_withdrawal_contract.py',
 'tools/kb/src/kb/signed_abs_register_helper_withdrawal_matrix.py',
 'tools/kb/src/kb/signed_abs_register_helper_withdrawal_semantics.py',
 'tools/kb/src/kb/signed_abs_register_helper_withdrawal_transfers.py',
 'tools/kb/src/kb/signed_abs_register_helper_withdrawal_capture_evidence.py',
 'tools/kb/src/kb/byte_surface_equations.py',
 'tools/kb/src/kb/test_stock_capture.py',
 'defs/JK08A.signed-abs-register-helper-withdrawal-paths.toml',
 'defs/JK08A.scalar-ram-leaf-withdrawals.toml',
 'tools/kb/src/kb/scalar_ram_leaf_withdrawal_contract.py',
 'tools/kb/src/kb/scalar_ram_leaf_withdrawal_evidence.py',
 'tools/kb/src/kb/scalar_ram_leaf_withdrawal_resolution.py',
 'defs/JK08A.counter-access-claims.toml',
 'defs/JK08A.maf-access-claims.toml',
 'defs/JK08A.signed-abs-register-helper-withdrawal-paths.md',
 'tools/kb/tests/test_signed_abs_register_helper_withdrawal_contract.py',
 'tools/kb/tests/test_signed_abs_register_helper_withdrawal_capture_evidence.py',
 'tools/kb/tests/test_signed_abs_register_helper_withdrawal_native.py')


def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the standalone signed-magnitude helper original omits an exact natural entry')
    from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
    rows=[row for row in withdrawal.descriptor(model.root)['reference'] if row['component']=='signed_abs_register_helper_withdrawal_paths'];result=[]
    for row in rows:
        symbol=model.symbols.get(withdrawal.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None
                or function.meaning.key!=json.loads(row['original_claim_json'])['to']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (withdrawal.native_type(row,'width'),withdrawal.native_type(row,'signed')))):
            raise ValueError('the standalone signed-magnitude helper original changes a retained exact owner, function or native type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],function=function.key.key,
            function_meaning=function.meaning.key,original_claim_sha256=row['original_claim_sha256']))
    if len(result)!=1:raise ValueError('the standalone signed-magnitude helper original omits an exact original withdrawal identity')
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),
        calibration_spans=[[row['address'],row['size']] for row in contract.OBSERVED_SPANS],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,natural_scheduling_inference=False,native_publication=False,hardware_qualification=False)


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
        raise ValueError('the standalone signed-magnitude helper original changes complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the standalone signed-magnitude helper original changes complete natural instructions, pools, aliases or configuration bytes')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=True)
    value=semantics.evaluate(case['entry'],observed['memory_before'][0],observed['calibration_before'],
        observed['context'],observed['sr_before'],bytes(frame),observed['sp'],observed['continuation'])
    transfers.require(observed,result,value,fixture)
    return result,value


def actual_output(observed):
    entry=observed['entry'];memory=observed['memory_after'][0]
    outputs={}
    return (observed['exit'][-1],*(memory[at:at+size] for at,size in outputs.get(entry,())))


def require_positive_alternatives(actual,declared):
    fields={name:(at,width) for name,at,width in matrix.RAM_FIELDS}
    configuration={row['field']:(row['address'],row['size']) for row in contract.CONFIGURATION}
    for entry,names in matrix.ENTRY_FIELDS.items():
        for name in names:
            groups={}
            for observed in actual:
                if observed['entry']!=entry:continue
                memory=bytearray(observed['memory_before'][0]);context=list(observed['context'])
                frame=bytearray(observed['frame_before']);bound=bytearray(observed['bound_before'])
                calibration=dict(observed['calibration_before'])
                if name in matrix.REGISTERS:
                    index=matrix.REGISTERS.index(name);incoming=context[index];context[index]=0
                    if index==7:frame[164:168]=bytes(4)
                elif name in fields:
                    at,size=fields[name];incoming=bytes(memory[at:at+size]);memory[at:at+size]=bytes(size)
                else:
                    at,size=configuration[name];incoming=calibration[at];calibration[at]=bytes(size);cursor=0
                    for first,size in declared['bound_spans']:
                        for offset in range(len(incoming)):
                            if first<=at+offset<first+size:bound[cursor+at+offset-first]=0
                        cursor+=size
                held=dict(memory=bytes(memory).hex(),context=context,frame=bytes(frame).hex(),
                    sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                    sr=observed['sr_before'],entry=entry,bound=bytes(bound).hex(),
                    calibration={str(at):data.hex() for at,data in calibration.items()})
                key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
                groups.setdefault(key,set()).add((incoming,actual_output(observed)))
            if not any(len({row[0] for row in group})>=2 and len({row[1] for row in group})>=2 for group in groups.values()):
                raise ValueError('the standalone signed-magnitude helper original lacks changed actual return/store outputs with fixed-other '+name+' inputs')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the standalone signed-magnitude helper original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the standalone signed-magnitude helper raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the standalone signed-magnitude helper original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the standalone signed-magnitude helper original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the standalone signed-magnitude helper original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the standalone signed-magnitude helper original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the standalone signed-magnitude helper original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/signed_abs_register_helper_withdrawal_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a standalone signed-magnitude helper independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the standalone signed-magnitude helper independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the standalone signed-magnitude helper fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the standalone signed-magnitude helper fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the standalone signed-magnitude helper original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the standalone signed-magnitude helper original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_scalar_ram_product_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the standalone signed-magnitude helper original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the standalone signed-magnitude helper original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the standalone signed-magnitude helper original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the standalone signed-magnitude helper original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
    rows=[row for row in withdrawal.descriptor(root)['reference'] if row['component']=='signed_abs_register_helper_withdrawal_paths']
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};seen=set();entries=set();classes=set()
    fixed={site:set() for site in transfers.FIXED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed,root)
        classes.add('positive' if value['tags']['positive'] else 'zero' if value['tags']['zero'] else 'negative')
        if value['tags']['minimum_word']:classes.add('minimum-word')
        transfers.require_no_selected_datum(result,rows);entries.add(observed['entry']);seen.update(result['code'])
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if branch['site'] in fixed:fixed[branch['site']].add(branch['kind'])
    expected_code={site for first,last in contract.SPANS for site in range(first,last,2)}-set(transfers.INFEASIBLE_INSTRUCTIONS)
    if entries!=set(contract.ENTRIES) or seen!=expected_code:
        raise ValueError('the standalone signed-magnitude helper original omits a complete natural entry, feasible instruction or delay slot')
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the standalone signed-magnitude helper original omits a feasible conditional outcome')
    if any(fixed[site]!={outcome} for site,outcome in transfers.FIXED_BRANCHES.items()):
        raise ValueError('the standalone signed-magnitude helper original changes an exact byte/word product premise consequence')
    require_positive_alternatives(actual,declared)
    require_selected_prior_independence(actual,declared)
    if classes!={'zero','positive','negative','minimum-word'}:
        raise ValueError('the standalone helper omits the actual zero, sign or raw minimum-word class')
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_signed_abs_register_helper_withdrawal_paths=True,no_selected_datum_access=True,no_selected_ram_datum_access=True,
        complete_full_raw32_input=True,complete_signed_minimum_word_wrap=True,complete_zero_and_both_sign_paths=True,
        complete_independent_instruction_states=True,complete_unchanged_frame_RAM=True,complete_selected_root_priors=True,
        derived_channel_and_writer_dependencies_preserved=True,
        selected_native_RAM_aliases={f'{native:08x}':f'{alias:08x}' for original,native,alias in transfers.NATIVE_RAM_ROOTS},
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        operand_width_premise_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in fixed.items()},
        native_identity_admission=False,native_geometry_inference=False,automatic_resolution=False,
        scale_admission=False,units_admission=False,natural_caller_reachability=False,natural_scheduling_inference=False,native_publication=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),
        'the standalone signed-magnitude helper original replaces a natural return with an outside-code return')


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('signed_abs_register_helper_withdrawal_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual standalone signed-magnitude helper original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the standalone signed-magnitude helper inputs change during independent consumption')
    require_owning_result(result)
    return result


OWNING_FLAGS=('exact_signed_abs_register_helper_withdrawal_paths','complete_full_raw32_input',
    'complete_signed_minimum_word_wrap','complete_zero_and_both_sign_paths',
    'complete_independent_instruction_states','complete_unchanged_frame_RAM',
    'no_selected_datum_access','no_selected_ram_datum_access','complete_selected_root_priors',
    'derived_channel_and_writer_dependencies_preserved')
NON_ADMISSIONS=('native_identity_admission','native_geometry_inference','automatic_resolution',
    'scale_admission','units_admission','natural_caller_reachability','natural_scheduling_inference',
    'native_publication','hardware_qualification')


def require_owning_result(result):
    if (type(result) is not dict or any(result.get(name) is not True for name in OWNING_FLAGS)
            or any(result.get(name) is not False for name in NON_ADMISSIONS)):
        raise ValueError('the standalone signed-magnitude result lacks complete independent raw32/state/physical obligations or grants an inference')
    expected=[dict(symbol='7mfk-ffff2c1c/ram',meaning='wandering-grasshopper/ram',
        function='7mfk-00022590/fn',function_meaning='clay-capuchin/fn',
        original_claim_sha256='782dacc59731fbc23c8a52ec82e8f9cc0468235c9826a1eee5214cbe5d571417')]
    same(result.get('native_bindings'),expected,'the standalone helper substitutes its exact original, owner or full function')
    ignition_literal_evidence.require_hash(result.get('stdout_sha256'))
    return True


def require_selected_prior_independence(actual,declared):
    required={0,1,0x80000000}
    for name,address,width in matrix.RAM_FIELDS:
        groups={}
        for case,observed in zip(declared['cases'],actual):
            if case['kind']!='selected-raw-byte-prior-only':continue
            memory=bytearray(observed['memory_before'][0]);incoming=memory[address];memory[address]=0
            held=dict(memory=memory.hex(),entry=observed['entry'],context=list(observed['context']),
                frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
                abi=list(observed['abi_before']),sr=observed['sr_before'],bound=observed['bound_before'].hex(),
                calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            after=bytearray(observed['memory_after'][0]);after[address]=0
            result=(observed['exit'],bytes(after),observed['frame_after'])
            groups.setdefault(key,[]).append((incoming,observed['context'][4],result))
        admitted=set()
        for rows in groups.values():
            if {row[0] for row in rows}!={0,1,0x7F,0x80,0xFF}:continue
            if any(row[2]!=rows[0][2] for row in rows):
                raise ValueError('an unread selected raw byte changes complete actual CPU, unchanged RAM or frame with other inputs fixed')
            admitted.update(row[1] for row in rows)
        if admitted!=required:
            raise ValueError('the standalone helper omits fixed-other raw-byte priors for zero, positive or minimum-word arguments')
