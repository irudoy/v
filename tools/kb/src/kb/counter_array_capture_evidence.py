"""Independent full-state and complete-range admission of stock counter array writes."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import counter_array_contract as contract,counter_array_matrix as matrix
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-counter-array-paths'
PREFIX='kb-counter-array-observation '
HEADER='ram-initialization-cases.h'
HARNESS='harness-ram-initialization.c'
OBSERVER='stock_ignition_consumer_invoke.s'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import counter_access_contract as owning
    if not {row['parent'] for row in contract.WINDOWS}<=set(model.functions.get('7mfk',())):
        raise ValueError('the counter array original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the counter array original changes an exact native field, parent or semantic type')
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
    lines=['/* Explicit stock counter-array inputs; no expected outputs. */',
           '#define RAM_INITIALIZATION_REGION '+json.dumps(REGION),
           '#define RAM_INITIALIZATION_PREFIX '+json.dumps(PREFIX),
           '#define RAM_INITIALIZATION_MARKER "VQ_SH_ELF_COUNTER_ARRAYS"',
           '#define RAM_INITIALIZATION_WORD_SEED 1',
           'static const uint32_t ram_initialization_pools[] = {'+
           ','.join(f'0x{address:x}U' for address in contract.POOLS)+'};',
           'static const struct word_range ram_initialization_word_ranges[] = {'+
           ','.join(f'{{0x{row["first"]&65535:x}U,{row["count"]}U}}' for row in contract.ARRAYS if row['width_bytes']==2)+'};',
           'static const struct path_case ram_initialization_cases[] = {']
    for case in declared['cases']:
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        lines.append(f'    {{0x{case["entry"]:x}U,0x{case["seed"]:x}U,{{{{{registers}}},{tail}}}}},')
    lines.extend(('};','#define RAM_INITIALIZATION_BYTE_INPUTS 1',
        'struct byte_input { uint32_t offset,value,enabled; };',
        'static const struct byte_input ram_initialization_byte_inputs[] = {'))
    for case in declared['cases']:
        if 'holdoff' in case:
            if case['entry']!=0x2093E or type(case['holdoff']) is not int or not 0<=case['holdoff']<=255:
                raise ValueError('the holdoff header changes its exact byte operand or bounded counter entry')
            lines.append(f'    {{0x25ffU,{case["holdoff"]}U,1U}},')
        else:lines.append('    {0U,0U,0U},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the counter array original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the counter array original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the counter array original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the counter array original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the counter array original mutates its const input context')
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
    same(packet['observations'],actual,'the counter array packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_COUNTER_ARRAYS status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the counter array original lacks its unique complete marker')
    return parsed


def array_equation(window,before):
    """Independent per-element saturation and exact conditional access sequence."""
    expected=bytearray(before);accesses=[];branches=[];steps=window['prefix_steps']+2;arrays=[]
    for array in contract.ARRAYS:
        if array['entry']!=window['start']:continue
        first=array['first']&65535;width=array['width_bytes'];written=0
        branches.append((array['initial_branch'],'fallthrough'))
        for index in range(array['count']):
            offset=first+index*width;address=matrix.RAM_BASE+offset
            incoming=before[offset:offset+width];value=int.from_bytes(incoming,'big')
            accesses.append((array['read'],'read',address,width,incoming.hex()))
            branches.append((array['zero_branch'],'taken' if value==0 else 'fallthrough'))
            steps+=8
            if value:
                output=(value-1).to_bytes(width,'big');expected[offset:offset+width]=output
                accesses.extend(((array['repeat_read'],'read',address,width,incoming.hex()),
                                 (array['store'],'write',address,width,output.hex())))
                written+=1;steps+=4
            branches.append((array['loop_branch'],'taken' if index+1<array['count'] else 'fallthrough'))
        arrays.append(dict(first=array['first'],count=array['count'],width_bytes=width,written=written))
    return bytes(expected),accesses,branches,steps,arrays


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the counter array original changes its complete incoming frame, SP or caller ABI')
    result=state.execute(declared['source'],fixture,context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the counter array original disagrees with complete independent instruction-state equations')
    window=next(row for row in contract.WINDOWS if row['start']==case['entry'])
    memory,wanted,wanted_branches,steps,arrays=array_equation(window,observed['memory_before'][0])
    if observed['memory_after']!=(memory,) or result['steps']!=steps or result['calls']:
        raise ValueError('the counter-array original changes its conditional footprint, loop count or call-free path')
    accesses=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes'])
              for row in result['accesses'] if row['domain']=='ram']
    if accesses!=wanted:
        raise ValueError('the counter-array original changes an exact read, repeated read, conditional store or element')
    sites={array[key] for array in contract.ARRAYS if array['entry']==window['start']
           for key in ('initial_branch','zero_branch','loop_branch')}
    branches=[(row['site'],row['kind']) for row in result['branches'] if row['site'] in sites]
    if branches!=wanted_branches:
        raise ValueError('the counter-array original omits an exact zero/nonzero or loop outcome')
    if window['start']==0x2093E:
        require_holdoff_transfer(observed,result,wanted)
    return result,dict(index=case['index'],parent=window['parent'],entry=window['start'],seed=case['seed'],
        steps=steps,arrays=arrays,full_RAM_sha256=sha(memory),exact_conditional_decrement=True,
        native_geometry_inference=False,periodic_cadence_inference=False,hardware_qualification=False)


def require_holdoff_transfer(observed,result,accesses):
    """Bind the exact element offset and bounded observing return to the stock loop."""
    pointer=0x010025FB;limit=pointer+7
    wanted=[(0x2093E,'read',0x20B44,4,pointer.to_bytes(4,'big').hex()),*accesses]
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain']!='frame']
    if not test_contract.exact(actual,wanted):
        raise ValueError('the holdoff proof changes its exact pointer, byte offset, conditional transfer or access order')
    if ([(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']!=
            [(0x20962,observed['continuation'])]
            or observed['frame_after']!=observed['frame_before']
            or any(row['domain']=='frame' for row in result['accesses'])):
        raise ValueError('the holdoff proof changes its outside RTS/NOP, actual return or untouched frame')
    registers=result['registers'];context=observed['context']
    if ((registers[0],registers[2],registers[5],registers[6],result['gbr'],result['mach'],result['macl'])!=
            (context[0],limit,pointer,limit,context[15],context[16],context[17])):
        raise ValueError('the holdoff proof changes its independent complete pointer/end/context terminal')


def require_holdoff_positive(actual,declared):
    groups={}
    for case,observed in zip(declared['cases'],actual):
        if case['entry']!=0x2093E or 'holdoff' not in case:continue
        memory=bytearray(observed['memory_before'][0]);incoming=memory[0x25FF];memory[0x25FF]=0
        held=dict(entry=observed['entry'],memory=bytes(memory).hex(),context=list(observed['context']),
            frame=observed['frame_before'].hex(),sp=observed['sp'],continuation=observed['continuation'],
            sr=observed['sr_before'],abi=list(observed['abi_before']),
            calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups.setdefault(key,set()).add((incoming,observed['memory_after'][0][0x25FF]))
    if not any({incoming for incoming,output in group}>={0,1,2,127,128,254,255}
            and all(output==max(0,incoming-1) for incoming,output in group)
            and len({output for incoming,output in group})>1 for group in groups.values()):
        raise ValueError('the holdoff proof lacks positive exact-byte output alternatives with every other complete input fixed')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the counter array original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the counter array packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the counter array original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the counter array original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,HEADER}:
        raise ValueError('the counter array original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the counter array original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the counter array original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/counter_array_capture.py',
            'tools/kb/src/kb/counter_array_contract.py','tools/kb/src/kb/counter_array_matrix.py',
            'tools/kb/src/kb/counter_array_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
            'tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the counter array independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=address,stock=image[address:address+4].hex(),reconstructed=image[address:address+4].hex())
               for address in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the counter array GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the counter array fixture changes an exact range-pointer alias')
    same(packet['boundaries'],list(contract.RETURNS),'the counter array fixture changes an exact observation return')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the counter array fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the counter array original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the counter array original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_counter_array_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the counter array original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the counter array original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the counter array original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the counter array original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];writes=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed);semantics.append(value)
        writes.update((row['site'],0xFFFF0000+row['address']-matrix.RAM_BASE,row['width_bytes'])
                      for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write')
    require_holdoff_positive(actual,declared)
    from kb import counter_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if (row['sites'][0],row['address'],row['width_bytes']) not in writes:
            raise ValueError('a counter-array owning writer lacks its positive exact physical store')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_counter_array_writes=True,exact_holdoff_byte=True,native_geometry_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('counter_array_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique counter array component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the counter array inputs change during admission')
    return result
