"""Independent complete-state, native-workspace and physical coordinate admission."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import closed_loop_coordinate_contract as contract,closed_loop_coordinate_matrix as matrix
from kb import closed_loop_coordinate_semantics as scalar
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-closed-loop-coordinate-paths'
PREFIX='kb-closed-loop-coordinate-observation '
HEADER='closed-loop-coordinate-cases.h'
HARNESS='harness-closed-loop-coordinate.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN='publication_inhibit_snapshot_return.s'
REQUIRED_BRANCHES=(0x26742,0x2694C,0x26950,0x3EFC8,0x3EFD4,0x3EFEA,0x3EFF8,
    0x3F07E,0x3F09A,0x3F0AA,0x3F0B8,0x3F0C6,0x3F0E4,0x3F0EE,0x3F0FC,0x3F11C,0x3F128,
    0x3F132,0x3F13A,0x3F13E,0x3F146,0x3F150)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import closed_loop_coordinate_access_contract as owning
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the coordinate conditioner original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        if row['component']!='closed_loop_coordinate_paths':continue
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the coordinate conditioner original changes an exact native field, parent or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),calibration_spans=[[row['address'],row['size']] for row in contract.pools()],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    pools=contract.pools();size=sum(row['size'] for row in pools)
    lines=['/* Explicit source words, native premise and calibration inputs; no expected outputs. */',
        '#define CLOSED_LOOP_COORDINATE_REGION '+json.dumps(REGION),
        f'#define COORDINATE_CALIBRATION_SIZE {size}U',
        'static const uint32_t calibration_starts[] = {'+
        ','.join(f'0x{row["address"]:x}U' for row in pools)+'};',
        'static const uint32_t calibration_sizes[] = {'+
        ','.join(f'{row["size"]}U' for row in pools)+'};',
        'struct path_case { uint32_t entry,'+','.join(matrix.FIELDS)+';',
        '    struct context context; uint8_t calibration[COORDINATE_CALIBRATION_SIZE]; };',
        'static const struct path_case closed_loop_coordinate_cases[] = {']
    for case in declared['cases']:
        fields=','.join(f'0x{case[key]:x}U' for key in ('entry',*matrix.FIELDS))
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[row['address']] for row in pools)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+fields+',{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the coordinate conditioner original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the coordinate conditioner original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after','native_before','native_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the coordinate conditioner original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the coordinate conditioner original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the coordinate conditioner original mutates its const input context')
        calibration={}
        for name in ('calibration_before','calibration_after'):
            data=test_stock_abi.raw(row[name],sum(pool['size'] for pool in contract.pools()))
            calibration[name]={};offset=0
            for pool in contract.pools():
                size=pool['size'];calibration[name][pool['address']]=data[offset:offset+size];offset+=size
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            native_before=test_stock_abi.raw(row['native_before'],256),
            native_after=test_stock_abi.raw(row['native_after'],256),**calibration))
    same(packet['observations'],actual,'the coordinate conditioner packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_CLOSED_LOOP_COORDINATE status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the coordinate conditioner original lacks its unique complete marker')
    return parsed



def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the coordinate conditioner original changes its complete incoming frame, SP or caller ABI')
    source=dict(declared['source'],entry=[*declared['source']['entry'],dict(start=contract.BOUNDARY['address'],end=contract.BOUNDARY['address']+8)])
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if any(row['start']<start+len(data) and start<row['end'] for row in contract.WINDOWS):
            raise ValueError('a coordinate calibration changes a tested stock instruction')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(source,bytes(expected_fixture),context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or matrix.logical(observed)!=result['ram']):
        raise ValueError('the coordinate conditioner original disagrees with complete independent instruction-state equations')
    return result,scalar.evaluate(case,observed,result)


def require_sample_alternatives(observations):
    groups={}
    for observed in observations:
        memory=bytearray(observed['memory_before'][0]);incoming=bytes(memory[0x4524:0x4526])
        memory[0x4524:0x4526]=bytes(2)
        held=dict(memory=memory.hex(),native=observed['native_before'].hex(),
            context=list(observed['context']),frame=observed['frame_before'].hex(),sp=observed['sp'],
            continuation=observed['continuation'],abi=list(observed['abi_before']),sr_before=observed['sr_before'],
            entry=observed['entry'],calibration={str(at):data.hex()
                for at,data in observed['calibration_before'].items()})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        output=observed['memory_after'][0][0x8558:0x855C]
        groups.setdefault(key,set()).add((incoming,output))
    if not any(len({item[0] for item in values})>=2 and len({item[1] for item in values})>=2
            for values in groups.values()):
        raise ValueError('the coordinate sample argument lacks varying actual output with every other complete input fixed')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the coordinate conditioner original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the coordinate conditioner packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the coordinate conditioner original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the coordinate conditioner original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,RETURN,HEADER,Path(matrix.INPUT_SOURCE).name}:
        raise ValueError('the coordinate conditioner original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER,RETURN,Path(matrix.INPUT_SOURCE).name):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the coordinate conditioner original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the coordinate conditioner original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/closed_loop_coordinate_capture.py',
            'tools/kb/src/kb/closed_loop_coordinate_contract.py','tools/kb/src/kb/closed_loop_coordinate_matrix.py',
            'tools/kb/src/kb/closed_loop_coordinate_capture_evidence.py','tools/kb/src/kb/closed_loop_coordinate_semantics.py',
            'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/width_view_matrix.py',
            matrix.INPUT_SOURCE):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the coordinate call independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                    reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.pools()])
    same(packet['reconstruction'],reconstructed,'the coordinate conditioner GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the coordinate conditioner fixture changes its exact base-pointer alias')
    if type(packet['boundaries']) is not list or len(packet['boundaries'])!=1:
        raise ValueError('the coordinate conditioner lacks its independently reconstructed observing return')
    stub=packet['boundaries'][0];boundary=contract.BOUNDARY
    if type(stub) is not dict or set(stub)!={'address','bytes','source_sha256','object_sha256','elf_sha256'}:
        raise ValueError('the coordinate conditioner return lacks its exact source/object/ELF schema')
    same((stub['address'],stub['bytes'],stub['source_sha256']),
        (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
        'the coordinate conditioner observing return changes bytes, address or private source')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the coordinate conditioner fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the coordinate conditioner original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=4):
        raise ValueError('the coordinate conditioner original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_closed_loop_coordinate_base_verifier')
    if simulator['command'][:3]!=[base.RUN,'--memory-region=0x01000000,64k','--memory-region=0xffff8500,256']:
        raise ValueError('the coordinate conditioner original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][3])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the coordinate conditioner original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the coordinate conditioner original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the coordinate conditioner original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES}
    from kb import closed_loop_coordinate_access_contract as owning
    rows=[row for row in owning.descriptor(root)['reference'] if row['component']=='closed_loop_coordinate_paths'];groups={row['id']:{} for row in rows}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((row['site'],row['mode'],
            0xFFFF0000+row['address']-matrix.RAM_BASE if row['domain']=='ram' else row['address'],row['width_bytes'])
            for row in result['accesses'] if row['domain']!='frame')
        for row in rows:
            address=0x12292 if row['direction']=='writer' else row['address']
            width=1 if row['direction']=='writer' else row['width_bytes']
            calibration={str(at):bytearray(data) for at,data in observed['calibration_before'].items()}
            selected=[(at,data) for at,data in calibration.items() if int(at)<=address< int(at)+len(data)]
            if len(selected)!=1:raise ValueError('a coordinate owning input lacks its exact physical calibration')
            at,data=selected[0];offset=address-int(at);incoming=bytes(data[offset:offset+width]);data[offset:offset+width]=bytes(width)
            held=dict(memory=observed['memory_before'][0].hex(),native=observed['native_before'].hex(),
                context=list(observed['context']),frame=observed['frame_before'].hex(),sp=observed['sp'],
                continuation=observed['continuation'],abi=list(observed['abi_before']),sr_before=observed['sr_before'],
                calibration={at:bytes(data).hex() for at,data in calibration.items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            output=value['coefficient'] if row['direction']=='writer' else tuple(value['output'])
            groups[row['id']].setdefault(key,set()).add((incoming,output))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the coordinate original omits a required reachable saturation, coefficient or admission branch outcome')
    for alternatives in groups.values():
        if not any(len({item[0] for item in values})>=2 and len({item[1] for item in values})>=2
                   for values in alternatives.values()):
            raise ValueError('a coordinate owning relation lacks positive alternatives with every other input fixed')
    for row in rows:
        direction='read' if row['direction']=='reader' else 'write'
        if not all((site,direction,row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a coordinate owning relation lacks its exact positive physical root/gate/publication transfer')
    require_sample_alternatives(actual)
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_coordinate_accesses=True,exact_sample_argument=True,native_geometry_inference=False,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('closed_loop_coordinate_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique coordinate conditioner component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the coordinate conditioner inputs change during admission')
    return result
