"""Independent actual whole-feedback state, argument, store and source admission."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import closed_loop_feedback_access_contract as contract,closed_loop_feedback_matrix as matrix
from kb import closed_loop_feedback_transfers as transfers
from kb.model import SymbolKey
from tools.kb.tests import closed_loop_feedback_frame as frame
from tools.kb.tests import closed_loop_feedback_terminal as terminal

REGION='jk08a-closed-loop-feedback-paths'
PREFIX='kb-closed-loop-feedback-observation '
HEADER='closed-loop-feedback-path-cases.h'
HARNESS='harness-closed-loop-feedback-paths.c'
OBSERVER='invoke-closed-loop-feedback.s'
REQUIRED_BRANCHES=(0x5D6D0,0x5D6D8,0x5D6E4,0x5D6EC,0x5D700,0x5D70C,0x5D736,
    0x5D772,0x5D776,0x5D780,0x5D7CA,0x5D7E4,0x5D7EC,0x5D7FC,0x5D82C,
    0x5CAD8,0x5CADE,0x5CAE6,0x5CAF0,0x5CAFC,0x5CB02,0x5CB0A,0x5CB16,
    0x5CB38,0x5CB56,0x5CB70,0x5CBC6)
NATIVE=((0xFFFF106E,'fuzzy-mouse/ram',None,None),(0xFFFF1071,'raspberry-dragon/ram',None,None),
    (0xFFFF11BC,'rpm/ram',16,False),(0xFFFF895C,'crazy-lynx/ram',None,None),
    (0xFFFF8960,'arrogant-walrus/ram',None,None),
    (0xFFFF88BA,'closed_loop_feedback_transition_counter_b2/ram',16,False))
SOURCE_FILES=('tools/kb/src/kb/closed_loop_feedback_access_contract.py',
    'tools/kb/src/kb/closed_loop_feedback_matrix.py','tools/kb/src/kb/closed_loop_feedback_transfers.py',
    'tools/kb/src/kb/closed_loop_feedback_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
    'tools/sh-elf-run/closed_loop_feedback_capture.py','tools/kb/tests/closed_loop_feedback_model.py',
    'tools/kb/tests/closed_loop_feedback_frame.py','tools/kb/tests/closed_loop_feedback_terminal.py',
    contract.LEGACY_CONTRACT,contract.DESCRIPTOR)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not {contract.ENTRY,transfers.TARGET,0x5CA8C,0x5D66C}<=set(model.functions.get('7mfk',())):
        raise ValueError('the feedback original lacks its exact normalized real caller or active-state callee')
    result=[]
    for address,owner,width,signed in NATIVE:
        symbol=model.symbols.get(SymbolKey('7mfk','ram',address))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=owner
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(width,signed))):
            raise ValueError('the feedback original changes a native argument/store owner or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    for address,owner in ((contract.ENTRY,'strong-tarsier/fn'),(transfers.TARGET,'funky-toucanet/fn'),
            (0x5CA8C,'closed_loop_feedback_transition/fn'),(0x5D66C,'closed_loop_feedback_transition_packet/fn')):
        symbol=model.symbols.get(SymbolKey('7mfk','fn',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the feedback original changes its exact real caller/callee owner')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),
        calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,physical_callee_reader_inference=False,
        automatic_resolution=False,natural_scheduling_inference=False,hardware_qualification=False)


def header(declared,image):
    changes=[];rows=[]
    for case in declared['cases']:
        begin=len(changes);changes.extend(case['changes'])
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        values=b''.join(calibration[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        prefix=(int(case['kind']=='controlled'),case['entry'],case['zero'],case['seed_index'],begin,len(case['changes']))
        rows.append('    {'+','.join(f'0x{value:x}U' for value in prefix)+',{{'+registers+'},'+tail+'},{'+
            ','.join(f'0x{value:02x}U' for value in values)+'}},')
    lines=['/* Complete explicit feedback inputs; no expected outputs or terminal values. */',
        '#define FEEDBACK_REGION '+json.dumps(REGION),
        f'#define FEEDBACK_BOUND_SIZE {sum(row["size"] for row in contract.BOUND_SPANS)}U',
        'static const struct span feedback_bound[] = {'+
        ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in contract.BOUND_SPANS)+'};',
        'static const struct span feedback_controlled[] = {'+
        ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in contract.CONTROLLED_CALIBRATION)+'};',
        'static const struct change feedback_changes[] = {',
        *('    {'+f'0x{at:x}U,0x{value:x}U'+'},' for at,value in changes),
        '};','static const struct path_case feedback_cases[] = {',*rows,'};','']
    return '\n'.join(lines).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the feedback original repeats a raw JSON key')
        result[key]=value
    return result


def bound_bytes(value,size):
    if type(value) is not str or not value:raise ValueError('the feedback original omits a complete bound-byte snapshot')
    result=bytearray();previous=None
    for run in value.split(','):
        count,separator,data=run.partition(':')
        if (not separator or not count.isascii() or not count.isdecimal() or str(int(count))!=count
                or not 1<=int(count)<=size or len(data)!=2 or any(char not in '0123456789abcdef' for char in data)
                or data==previous or len(result)+int(count)>size):
            raise ValueError('the feedback bound-byte snapshot is incomplete or noncanonical')
        result.extend(bytes.fromhex(data)*int(count));previous=data
    if len(result)!=size:raise ValueError('the feedback bound-byte snapshot omits part of its complete declared spans')
    return bytes(result)


def observations(packet,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
        for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(rows)!=len(declared['cases']):raise ValueError('the feedback original omits or repeats an actual invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
        'workspace_before','workspace_after','calibration_before','calibration_after','bound_before','bound_after'}
    for index,(row,case) in enumerate(zip(rows,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the feedback raw observation changes its complete schema')
        wanted=dict(schema=1,index=index,kind=int(case['kind']=='controlled'),entry=contract.ENTRY)
        same({key:row[key] for key in wanted},wanted,'the feedback original changes its typed invocation order or role')
        context=test_stock_abi.raw(row['context'],76)
        if test_stock_abi.raw(row['context_after'],76)!=context:
            raise ValueError('the feedback original changes its const complete incoming context')
        out=test_stock_abi.raw(row['observation'],892)
        calibration={}
        for name in ('calibration_before','calibration_after'):
            data=test_stock_abi.raw(row[name],18);calibration[name]={};offset=0
            for address,size in declared['calibration_spans']:
                calibration[name][address]=data[offset:offset+size];offset+=size
        bound_size=sum(size for address,size in declared['bound_spans'])
        parsed.append(dict(index=index,entry=contract.ENTRY,context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:536],frame_after=out[536:888],sr_before=int.from_bytes(out[888:892],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            workspace_before=test_stock_abi.raw(row['workspace_before'],366),workspace_after=test_stock_abi.raw(row['workspace_after'],366),
            bound_before=bound_bytes(row['bound_before'],bound_size),bound_after=bound_bytes(row['bound_after'],bound_size),**calibration))
    same(packet['observations'],rows,'the feedback packet differs from its actual original stdout observations')
    marker=f'VQ_SH_ELF_CLOSED_LOOP_FEEDBACK status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the feedback original lacks its unique complete terminal marker')
    return parsed


def require_state(declared,image,case,observed,root):
    source=declared['source'];matrix.require_input(source,image,case,observed)
    fixture,_=contract.fixture_for_case(source,image,case,root)
    bound=b''.join(fixture[address:address+size] for address,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the feedback original changes an exact bound instruction, pool, alias or calibration byte')
    initial=b''.join((0xA3B4C5D6+17*index).to_bytes(4,'big') for index in range(88))
    if (observed['frame_before']!=initial or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the feedback original changes its complete initial frame, SP or external ABI')
    native_before,native_after=observed['workspace_before'],observed['workspace_after']
    if native_after[:32]!=native_before[:32] or native_after[334:]!=native_before[334:]:
        raise ValueError('the feedback original changes a low or high shared-workspace canary')
    ordinary_before,ordinary_after=observed['memory_before'][0],observed['memory_after'][0]
    if ordinary_after[0x88B0:0x89DE]!=ordinary_before[0x88B0:0x89DE]:
        raise ValueError('the feedback original writes the unaliased ordinary copy of its shared workspace')
    before=matrix.logical_ram(ordinary_before,native_before);after=matrix.logical_ram(ordinary_after,native_after)
    result=state.execute(source,fixture,(*observed['context'],0),before,initial,observed['sp'],
        observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the feedback original complete CPU differs from independent natural instruction equations')
    if observed['frame_after']!=result['frame'] or result['ram']!=after:
        raise ValueError('the feedback original complete memory or frame differs from independent natural instruction equations')
    numeric_after,trace=frame.semantic_trace(before,fixture)
    if after!=numeric_after:raise ValueError('the feedback original differs from the independent whole memory/state equations')
    expected_frame=frame.expectations(before,fixture,case['context_index'])
    predicted=bytearray(expected_frame['frame'])
    if expected_frame['fixups']!=[dict(at=288,source='continuation')]:
        raise ValueError('the feedback independent frame changes its exact natural caller PR binding')
    predicted[288:292]=observed['continuation'].to_bytes(4,'big')
    if bytes(predicted)!=observed['frame_after'] or expected_frame['result']!=numeric_after:
        raise ValueError('the feedback original differs from its separate complete nested-frame equations')
    cpu=terminal.expectations(numeric_after);context=observed['context'];exit=observed['exit']
    for register in range(15):
        wanted=cpu['r'+str(register)] if register<8 else context[register]
        if exit[19-register]!=wanted:raise ValueError('the feedback original differs from a separate terminal register equation')
    wanted_sr=(observed['sr_before']&~0x301)|(cpu['exit_q']<<8)|1
    if (exit[0]!=wanted_sr or exit[1]!=observed['continuation']
            or (exit[2],exit[3],exit[4])!=(context[17],context[16],context[15])):
        raise ValueError('the feedback original differs from separate full SR, natural PR or preserved special-register equations')
    values=transfers.require(observed,result,trace)
    values.update(transfers.require_transition(observed,result,trace,fixture))
    return result,values


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','command','simulator','stdout','stderr','stdout_sha256',
        'stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the feedback original changes its complete raw capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the feedback raw original grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the feedback original changes the owned stock image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the feedback original changes current exact sources or input cases')
    source=Path(contract.UNIT['assembly']).name;sources=(HARNESS,OBSERVER,source,Path(matrix.INPUT_SOURCE).name)
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HEADER,*sources}:
        raise ValueError('the feedback original omits an exact consumed source')
    for name in sources:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):raise ValueError('the feedback original consumes another source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():raise ValueError('the feedback original changes a compiled input-only header')
    for path in SOURCE_FILES:
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the feedback independent producer/consumer source is stale')
    reconstruction=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
            reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstruction,'the feedback GNU reconstruction changes a stock instruction or exact pool span')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the feedback original changes a full long/word alias declaration')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the feedback original changes an undeclared base fixture byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for name in ('stdout','stderr'):
        if type(packet[name]) is not str or packet[name+'_sha256']!=sha(packet[name].encode()):
            raise ValueError('the feedback original process stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the feedback original changes its actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_feedback_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the feedback original uses another simulator or ordinary RAM domain')
    elf=Path(simulator['command'][2]);private=elf.parent/'consumed'
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the feedback original executes another harness artifact')
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the feedback original changes its actual compiler, observer, source or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the feedback original changes its pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES}
    groups={address:{} for address,site,width in transfers.ARGUMENTS};writer_groups={address:{} for address,site in transfers.STORES}
    counter_groups={'reader':{},'writer':{}};counter_guard=set()
    for case,observed in zip(declared['cases'],actual):
        result,values=require_state(declared,image,case,observed,root)
        for row in result['branches']:
            if row['site'] in coverage:coverage[row['site']].add(row['kind'])
            if row['site']==0x5CB84:counter_guard.add(row['kind'])
        for address,site,width in transfers.ARGUMENTS:
            before=bytearray(observed['memory_before'][0]);offset=address&65535
            source_value=bytes(before[offset:offset+width]);before[offset:offset+width]=bytes(width)
            held=dict(memory=before.hex(),workspace=observed['workspace_before'].hex(),context=list(observed['context']),
                frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
                abi=list(observed['abi_before']),sr=observed['sr_before'],entry=observed['entry'],
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            effect=bytearray(values['scalar_after']);effect[offset:offset+width]=bytes(width)
            groups[address].setdefault(key,set()).add((source_value,bytes(effect)))
        before=bytearray(observed['memory_before'][0]);bank=before[0x10C8];before[0x10C8]=0
        held=dict(memory=before.hex(),workspace=observed['workspace_before'].hex(),context=list(observed['context']),
            frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
            abi=list(observed['abi_before']),sr=observed['sr_before'],entry=observed['entry'],
            calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
        key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
        for address,site in transfers.STORES:writer_groups[address].setdefault(key,set()).add((bank,values['stores'][address]))
        for direction,offset,width in (('reader',0x88BA,2),('writer',0x88C1,1)):
            memory=bytearray(observed['memory_before'][0]);native=bytearray(observed['workspace_before'])
            source_value=(values['transition_count_before'] if direction=='reader' else
                values['transition_flag_before']).to_bytes(width,'big')
            memory[offset:offset+width]=bytes(width)
            native_offset=32+offset-0x88B0;native[native_offset:native_offset+width]=bytes(width)
            held=dict(memory=memory.hex(),workspace=native.hex(),context=list(observed['context']),
                frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
                abi=list(observed['abi_before']),sr=observed['sr_before'],entry=observed['entry'],
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            output=(values['transition_count_after'],values['transition_flag_after'])
            counter_groups[direction].setdefault(key,set()).add((source_value,output))
    if any(values!={'taken','fallthrough'} for values in coverage.values()):
        raise ValueError('the feedback original omits a required feasible active-state or transition conditional branch outcome')
    if counter_guard!={'taken'}:raise ValueError('the transition counter original omits its exact feasible saturation-guard outcome')
    for group in (*groups.values(),*writer_groups.values(),*counter_groups.values()):
        if not any(len({row[0] for row in values})>=2 and len({row[1] for row in values})>=2 for values in group.values()):
            raise ValueError('a feedback argument or store lacks complete fixed-other positive original alternatives')
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_feedback_arguments=True,exact_feedback_stores=True,exact_transition_counter_accesses=True,
        transition_saturation_guard_outcomes=sorted(counter_guard),
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        physical_callee_reader_inference=False,native_geometry_inference=False,automatic_resolution=False,
        scale_admission=False,units_admission=False,natural_scheduling_inference=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('closed_loop_feedback_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the original complete primary lacks its unique exact feedback marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the feedback execution inputs change during independent consumption')
    return result
