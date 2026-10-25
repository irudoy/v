"""Independent physical and numeric/full-state admission of io-access originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import io_access_contract as contract, byte_surface_equations as state
from kb import io_access_matrix as matrix,io_access_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-io-access-paths'
PREFIX = 'kb-io-access-observation '
HEADER = 'io-access-path-cases.h'
HARNESS = 'harness-io-access-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SINKS = ('io_capture_return.s','io_monitor_return.s','io_access_return.s')
REQUIRED_BRANCHES = (0xC2FF4,0xC2FF8,0xC2FFC,0xC3000,0xC3004)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the I/O original omits a normalized function in its exact bounded closure')
    result=[]
    for address,owner in ((0xFFFFDC40,'solemn-heron/reg'),(0xFFFFF430,'ingenious-kagu/reg'),
                           (0xFFFFF754,'precise-kagu/reg')):
        symbol=model.symbols.get(SymbolKey('7mfk','reg',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the I/O original changes an exact owning native register')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    for address,owner in ((0xC2FBE,'granite-chameleon/fn'),(0xA6DC4,'festive-gopher/fn')):
        symbol=model.symbols.get(SymbolKey('7mfk','fn',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the I/O original changes an exact existing native parent function')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    result.append(dict(function='7mfk:00002040',native_function_publication=False,
                       bounded_scope='native read204E and operand formation before015CC'))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Exact entry, native storage and descriptor inputs; no expected outputs. */',
        '#define IO_ACCESS_REGION '+json.dumps(REGION),
        'static const uint8_t io_access_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const uint8_t io_access_records[][4] = {'))
    for raw in matrix.RECORDS:
        lines.append('    {'+','.join(f'0x{value:02x}U' for value in raw)+'},')
    lines.extend(('};','static const struct path_case io_access_cases[] = {'))
    for case in declared['cases']:
        values=(case['entry'],matrix.KINDS.index(case['kind']),case['group'],matrix.PATTERNS.index(case['pattern']),
                case['slot'],case['selector'],case['param'],case['word'],case['prior'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the io-access original repeats a raw observation JSON key')
        result[key]=value
    return result


def calibration(value,spans):
    raw=test_stock_abi.raw(value,sum(size for start,size in spans))
    result={}
    offset=0
    for start,size in spans:
        result[start]=raw[offset:offset+size]
        offset+=size
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the io-access original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after','native_io_before','native_io_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the io-access original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the io-access original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the io-access original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            native_before=test_stock_abi.raw(row['native_io_before'],sum(size for at,size in matrix.NATIVE_IO)),
            native_after=test_stock_abi.raw(row['native_io_after'],sum(size for at,size in matrix.NATIVE_IO)),
            calibration_before=calibration(row['calibration_before'],declared['calibration_spans']),
            calibration_after=calibration(row['calibration_after'],declared['calibration_spans'])))
    same(packet['observations'],actual,'the io-access packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_IO_ACCESS status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the io-access original lacks its unique complete marker')
    return parsed


def semantic(declared,case,observed,result):
    native=[row for row in result['accesses'] if row['domain']=='native-io']
    if case['kind']=='capture':
        expected=numeric.capture(case['param'],case['word'])
        reads=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in native]
        if (reads!=[(0x204E,'read',0xFFFFF430,4,case['word'].to_bytes(4,'big').hex())]
                or observed['exit'][19]!=expected['raw_word'] or observed['exit'][17]!=expected['packed']
                or observed['exit'][13]!=expected['low_word']
                or observed['frame_after'][144:146]!=expected['low_word'].to_bytes(2,'big')):
            raise ValueError('the capture original changes its actual uint32 read or separate operand/stack equations')
        value=dict(raw_word=expected['raw_word'],packed=expected['packed'])
    elif case['kind'] in ('monitor-prefix','monitor-read'):
        expected=numeric.monitor(observed['calibration_before'][0x23AC4],case['selector'],case['word'])
        if case['kind']=='monitor-prefix':
            branches=[row['kind'] for row in result['branches'] if row['site']==0xA6DE0]
            if (native or observed['exit'][15]!=expected['offset'] or observed['exit'][4]!=0x23AC4
                    or observed['exit'][17]!=0xFFFFF754 or branches!=['taken']):
                raise ValueError('the monitor prefix changes its actual descriptor GBR/stride/nonzero pointer')
        else:
            reads=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in native]
            if (reads!=[(0xA6EA4,'read',0xFFFFF754,2,case['word'].to_bytes(2,'big').hex())]
                    or observed['exit'][0]&1!=int(expected['unmasked'])):
                raise ValueError('the monitor read changes its actual native word, exact-width mask or T-bit outcome')
            pointers=[row for row in result['accesses'] if row['site']==0xA6EA2 and row['domain']=='rom']
            masks=[row for row in result['accesses'] if row['site']==0xA6EAA and row['domain']=='rom']
            if (len(pointers)!=1 or pointers[0]['address']!=0x23AC4+expected['offset']
                    or pointers[0]['width_bytes']!=4 or pointers[0]['bytes']!='fffff754'
                    or len(masks)!=1 or masks[0]['address']!=0x23AC8+expected['offset']
                    or masks[0]['width_bytes']!=2 or masks[0]['bytes']!=expected['mask'].to_bytes(2,'big').hex()):
                raise ValueError('the monitor read changes its actual selected pointer/mask descriptor lanes')
        value=dict(selector=case['selector'],mask=expected['mask'],unmasked=expected['unmasked'],
                   configured_caller_reachability_admitted=False)
    else:
        offset=case['slot']*4
        record=observed['calibration_before'][0x975A][offset:offset+4]
        expected=numeric.mailbox(record,case['slot'],case['prior'],observed['memory_before'][0])
        wanted=[(site,'write',expected['address']+offset,2,value.to_bytes(2,'big').hex())
                for site,(offset,value) in zip((0xC3058,0xC305C,0xC306E,0xC3072,0xC3074,0xC3078),expected['words'])]
        if ([(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in native]!=wanted
                or result['ram']!=expected['memory'] or observed['exit'][10]!=expected['mask']):
            raise ValueError('the mailbox original changes its actual word writes, selected record fields or flag mask')
        value=dict(slot=case['slot'],identifier=expected['words'][0][1],control=expected['words'][2][1])
    if result['calls']:
        raise ValueError('a bounded I/O entry invokes a helper outside its explicit window')
    return dict(index=case['index'],group=case['group'],kind=case['kind'],**value,
        native_relation_publication=False,native_function_publication=False,scale_admission=False,
        peripheral_side_effects_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed,previous=None):
    matrix.require_input(declared['source'],image,case,observed,previous)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded)
            or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI
            or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the I/O original changes its complete initial frame, SP, independent fifth/R7 or caller ABI')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('an I/O descriptor input changes tested instruction bytes or a PC-relative literal')
        expected_fixture[start:start+len(data)]=data
    oracle_source={**declared['source'],'entry':[*declared['source']['entry'],
        *[dict(start=row['address'],end=row['address']+len(bytes.fromhex(row['bytes']))) for row in contract.BOUNDARIES]]}
    result=state.execute(oracle_source,bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    relocated=bytearray(result['ram'])
    for start,size in matrix.NATIVE_IO:
        offset=start&65535
        relocated[offset:offset+size]=observed['memory_before'][0][offset:offset+size]
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(bytes(relocated),)
            or observed['native_after']!=matrix.native_bytes(result['ram'])):
        raise ValueError('the actual I/O complete state or independent native/relocated snapshots disagree')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain','stub_reconstruction'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the io-access original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the io-access raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the io-access original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the io-access original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER,*SINKS}:
        raise ValueError('the io-access original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source,*SINKS):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the io-access original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the io-access original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/io_access_capture.py',
                 'tools/kb/src/kb/io_access_contract.py','tools/kb/src/kb/io_access_matrix.py','tools/kb/src/kb/io_access_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/io_access_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the io-access producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the io-access GNU reconstruction changes stock instructions or literals')
    fixture,aliases,boundaries=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the io-access original changes its exact RAM aliases')
    same(packet['boundaries'],boundaries,'the io-access original changes its observing return boundary')
    stubs=packet['stub_reconstruction']
    if type(stubs) is not list or len(stubs)!=len(contract.BOUNDARIES):
        raise ValueError('the io-access original lacks its four separately assembled observing returns')
    for stub,boundary in zip(stubs,contract.BOUNDARIES):
        if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
            raise ValueError('the io-access observing return changes its complete reconstruction schema')
        if (stub['address']!=boundary['address'] or stub['bytes']!=boundary['bytes']
                or stub['source_sha256']!=sha((root/boundary['source']).read_bytes())):
            raise ValueError('the io-access original changes a separately assembled return')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the io-access fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the io-access actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=6
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the io-access original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_io_access_base_verifier')
    if simulator['command'][:5]!=[base.RUN,'--memory-region=0x01000000,64k',
            '--memory-region=0xffffd900,1024','--memory-region=0xfffff400,256','--memory-region=0xfffff700,256']:
        raise ValueError('the io-access original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][5])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the io-access original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the io-access original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the io-access original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[];coverage={site:set() for site in REQUIRED_BRANCHES};previous=None
    for case,observed in zip(declared['cases'],actual):
        if case['kind']=='monitor-read':
            if (previous is None or semantics[-1]['kind']!='monitor-prefix' or semantics[-1]['group']!=case['group']
                    or previous['memory_after']!=observed['memory_before']
                    or previous['native_after']!=observed['native_before']
                    or not test_contract.exact(previous['calibration_after'],observed['calibration_before'])):
                raise ValueError('the monitor read substitutes its actual prefix result or resets native/RAM/descriptor state')
        result,semantic_result=require_state(declared,image,fixture,case,observed,
            previous if case['kind']=='monitor-read' else None)
        semantics.append(semantic_result);previous=observed
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the mailbox original omits a descriptor-type branch outcome')
    groups={};mailbox_groups={};monitor={0:set(),6:set()}
    for row,observed,case in zip(semantics,actual,declared['cases']):
        if case['kind']=='capture':
            memory=bytearray(observed['memory_before'][0]);memory[0xF430:0xF434]=bytes(4)
            held=dict(context=list(observed['context']),memory=memory.hex(),
                      calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups.setdefault(key,set()).add((row['raw_word'],row['packed']))
        elif case['kind']=='mailbox':
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()}
            raw=bytearray(observed['calibration_before'][0x975A]);offset=case['slot']*4;raw[offset:offset+4]=bytes(4)
            calibration[str(0x975A)]=raw.hex()
            held=dict(context=list(observed['context']),memory=observed['memory_before'][0].hex(),calibration=calibration)
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            mailbox_groups.setdefault(key,set()).add((row['identifier'],row['control']))
        elif case['kind']=='monitor-read':monitor[case['selector']].add(row['unmasked'])
    if not any(all(len({row[index] for row in values})>=2 for index in (0,1)) for values in groups.values()):
        raise ValueError('the capture original lacks native-word/packed-operand variation with other inputs fixed')
    if not any(all(len({row[index] for row in values})>=2 for index in (0,1)) for values in mailbox_groups.values()):
        raise ValueError('the mailbox original lacks independent record/identifier/control variation')
    if any(values!={False,True} for values in monitor.values()):
        raise ValueError('a selected monitor word omits a masked or unmasked native input')
    if {case['entry'] for case in declared['cases']}!=set(matrix.ENTRIES):
        raise ValueError('the I/O original omits a bounded entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,bounded_physical_IO_access=True,parent_reachability_admitted=False,
        datum_identity_inference=False,automatic_resolution=False,native_function_publication=False,
        natural_caller_reachability=False,hardware_qualification=False,peripheral_side_effects_admission=False,
        native_relation_publication=False,scale_admission=False,all_modes=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('io_access_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact io-access marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the io-access inputs change during independent admission')
    return result
