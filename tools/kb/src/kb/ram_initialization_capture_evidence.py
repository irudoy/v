"""Independent full-state and complete-range admission of stock RAM clear writes."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import ram_initialization_contract as contract,ram_initialization_matrix as matrix
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-ram-initialization-paths'
PREFIX='kb-ram-initialization-observation '
HEADER='ram-initialization-cases.h'
HARNESS='harness-ram-initialization.c'
OBSERVER='stock_ignition_consumer_invoke.s'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import ram_clear_access_contract as owning
    if not {row['parent'] for row in contract.WINDOWS}<=set(model.functions.get('7mfk',())):
        raise ValueError('the RAM clear original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the RAM clear original changes an exact native field, parent or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[[address,4] for address in contract.POOLS],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Explicit stock clear inputs; no expected outputs. */',
           '#define RAM_INITIALIZATION_REGION '+json.dumps(REGION),
           '#define RAM_INITIALIZATION_PREFIX '+json.dumps(PREFIX),
           '#define RAM_INITIALIZATION_MARKER "VQ_SH_ELF_RAM_INITIALIZATION"',
           '#define RAM_INITIALIZATION_WORD_SEED 0',
           'static const uint32_t ram_initialization_pools[] = {'+
           ','.join(f'0x{address:x}U' for address in contract.POOLS)+'};',
           'static const struct path_case ram_initialization_cases[] = {']
    for case in declared['cases']:
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        lines.append(f'    {{0x{case["entry"]:x}U,0x{case["seed"]:x}U,{{{{{registers}}},{tail}}}}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the RAM clear original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the RAM clear original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the RAM clear original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the RAM clear original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the RAM clear original mutates its const input context')
        calibration={}
        for name in ('calibration_before','calibration_after'):
            data=test_stock_abi.raw(row[name],4*len(contract.POOLS))
            calibration[name]={address:data[index*4:index*4+4] for index,address in enumerate(contract.POOLS)}
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            **calibration))
    same(packet['observations'],actual,'the RAM clear packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_RAM_INITIALIZATION status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the RAM clear original lacks its unique complete marker')
    return parsed


def range_equation(window,before):
    """Clear complete aligned stores while their starts are below the stock limit."""
    first=window['first']&65535
    end=first+4*((window['limit']-window['first']+3)//4)
    expected=bytearray(before);expected[first:end]=bytes(end-first)
    return bytes(expected),first,end


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the RAM clear original changes its complete incoming frame, SP or caller ABI')
    result=state.execute(declared['source'],fixture,context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the RAM clear original disagrees with complete independent instruction-state equations')
    window=next(row for row in contract.WINDOWS if row['start']==case['entry'])
    memory,first,end=range_equation(window,observed['memory_before'][0])
    if observed['memory_after']!=(memory,) or result['steps']!=contract.steps(window) or result['calls']:
        raise ValueError('the RAM clear original changes its exact footprint, finite loop count or call-free path')
    accesses=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes'])
              for row in result['accesses'] if row['domain']=='ram']
    wanted=[(window['store'],'write',matrix.RAM_BASE+offset,4,'00000000') for offset in range(first,end,4)]
    if accesses!=wanted:raise ValueError('the RAM clear original changes an exact longword store, lane, order or direction')
    branches=[(row['site'],row['kind']) for row in result['branches']
              if row['site'] in (window['initial_branch'],window['loop_branch'])]
    wanted_branches=[(window['initial_branch'],'fallthrough')]
    wanted_branches.extend((window['loop_branch'],'taken') for _ in range((end-first)//4-1))
    wanted_branches.append((window['loop_branch'],'fallthrough'))
    if branches!=wanted_branches:raise ValueError('the RAM clear original omits a stock loop boundary or outcome')
    if 'natural_return' in window:
        require_natural_helper(window,observed,result,end)
    return result,dict(index=case['index'],parent=window['parent'],entry=window['start'],
        first=window['first'],limit=window['limit'],physical_end=0xFFFF0000+end,stores=(end-first)//4,
        seed=case['seed'],steps=result['steps'],store=window['store'],full_RAM_sha256=sha(memory),
        exact_longword_clear=True,native_geometry_inference=False,hardware_qualification=False)


def require_natural_helper(window,observed,result,end):
    """Bind the complete pointer-driven helper without replacing its natural RTS."""
    first,limit=window['first'],window['limit'];pointer=window['range_pointer']
    wanted=[(0x26F30,'read',0x26F9C,4,pointer.to_bytes(4,'big').hex()),
        (0x26F32,'read',pointer,4,(matrix.RAM_BASE+(first&65535)).to_bytes(4,'big').hex()),
        (0x26F36,'read',pointer+4,4,(matrix.RAM_BASE+(limit&65535)).to_bytes(4,'big').hex())]
    for offset in range(first&65535,end,4):
        wanted.append((0x26F3E,'write',matrix.RAM_BASE+offset,4,'00000000'))
        wanted.append((0x26F42,'read',pointer+4,4,(matrix.RAM_BASE+(limit&65535)).to_bytes(4,'big').hex()))
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain']!='frame']
    if not test_contract.exact(actual,wanted):
        raise ValueError('the natural clear helper changes exact ROM descriptor, pointer, limit reload or access order')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if (returns!=[(window['natural_return'],observed['continuation'])]
            or observed['frame_after']!=observed['frame_before']
            or any(row['domain']=='frame' for row in result['accesses'])):
        raise ValueError('the natural clear helper changes its real RTS, NOP delay or untouched complete frame')
    context=observed['context'];registers=result['registers']
    if ((registers[0],registers[1],registers[2],registers[6],result['gbr'],result['mach'],result['macl'])!=
            (matrix.RAM_BASE+(limit&65535),pointer,matrix.RAM_BASE+end,0,context[15],context[16],context[17])):
        raise ValueError('the natural clear helper changes independent limit/pointer/end/zero or complete special registers')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the RAM clear original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the RAM clear packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the RAM clear original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the RAM clear original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,HEADER}:
        raise ValueError('the RAM clear original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the RAM clear original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the RAM clear original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/ram_initialization_capture.py',
            'tools/kb/src/kb/ram_initialization_contract.py','tools/kb/src/kb/ram_initialization_matrix.py',
            'tools/kb/src/kb/ram_initialization_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
            'tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the RAM clear independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=address,stock=image[address:address+4].hex(),reconstructed=image[address:address+4].hex())
               for address in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the RAM clear GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the RAM clear fixture changes an exact range-pointer alias')
    same(packet['boundaries'],list(contract.RETURNS),'the RAM clear fixture changes an exact observation return')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the RAM clear fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the RAM clear original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the RAM clear original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_ram_initialization_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the RAM clear original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the RAM clear original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the RAM clear original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the RAM clear original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[]
    for case,observed in zip(declared['cases'],actual):
        _,value=require_state(declared,image,fixture,case,observed);semantics.append(value)
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_stock_clear_writes=True,native_geometry_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('ram_initialization_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique RAM clear component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the RAM clear inputs change during admission')
    return result
