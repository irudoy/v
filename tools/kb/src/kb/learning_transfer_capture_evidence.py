"""Independent physical and numeric admission of the learning-transfer original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import learning_transfer_contract as contract, byte_surface_equations as state
from kb import learning_transfer_matrix as matrix, learning_transfer_semantics as numeric
from kb import learning_publication_transfers as publication
from kb.model import SymbolKey

REGION = 'jk08a-learning-transfer-paths'
PREFIX = 'kb-learning-transfer-observation '
HEADER = 'learning-transfer-cases.h'
HARNESS = 'harness-learning-transfers.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SOURCES=('stock_jk08a_grid_selection.s','stock_jk08a_grid_learning.s',
         'stock-jk08a-grid-selection-cases.h','stock-jk08a-grid-learning-cases.h',
         'stock_jk08a_ltft_publication.s','stock-jk08a-ltft-publication-cases.h')
REQUIRED_BRANCHES=(0x580F4,0x58108,0x58128,0x5812C,0x5814E,0x5815C,
                   0x57D44,0x57D52,0x57D5C,0x57D8E,0x57D9A,0x57DB8,0x57DF6,0x57DFC,
                   0x57E02,0x57E20,0x57EA8,0x5809A,0x580BA,*publication.BRANCHES)
WATCHED={0x57A8C,0x57A92,0x57AD0,0x57B0C,0x580BC,0x58100,0x57D7A,0x57DC8,
         0x57DEC,0x57E0E,0x58110,0x58118,0x5811C,0x58138,0x58140,0x58146,0x58154,0x58162}
READERS=(('learning',0xFFFF1350,2),('learning',0xFFFF22DE,2),('learning',0xFFFF2308,2),
         ('learning',0x839C,1),('learning',0x839D,1),('learning',0x88F5,1),
         ('auxiliary',0xFFFF49B0,1),('auxiliary',0xFFFF49F0,1),
         ('publication',0xFFFF2308,2),('publication',0xFFFF564A,2))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    from kb import learning_access_contract as owning
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the learning transfer original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the learning transfer original changes an exact native field, parent or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    spans=matrix.calibration_spans(declared['source'])
    size=sum(width for at,width in spans)
    lines=['/* Explicit learned-grid inputs; no expected outputs. */',
           '#define LEARNING_TRANSFER_REGION '+json.dumps(REGION),
           f'#define LEARNING_TRANSFER_CALIBRATION_SIZE {size}U',
           'static const uint32_t learning_transfer_calibration_starts[] = {'+
           ','.join(f'0x{at:x}U' for at,width in spans)+'};',
           'static const uint32_t learning_transfer_calibration_sizes[] = {'+
           ','.join(f'{width}U' for at,width in spans)+'};',
           'struct path_case {',
           '    uint32_t kind,'+','.join(matrix.FIELDS)+';',
           '    uint32_t thresholds[3]; struct context context;',
           '    uint8_t calibration[LEARNING_TRANSFER_CALIBRATION_SIZE];',
           '};',
           'static const struct path_case learning_transfer_cases[] = {']
    for case in declared['cases']:
        values=','.join(f'0x{value:x}U' for value in (matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS)))
        thresholds=','.join(f'{value}U' for value in case['thresholds'])
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[at] for at,width in spans)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+values+',{'+thresholds+'},{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the learning-transfer original repeats a raw observation JSON key')
        result[key]=value
    return result


def calibration(value,spans):
    raw=test_stock_abi.raw(value,sum(size for start,size in spans))
    result={}; offset=0
    for start,size in spans:
        result[start]=raw[offset:offset+size]; offset+=size
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the learning-transfer original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the learning-transfer original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the learning-transfer original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the learning-transfer original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            calibration_before=calibration(row['calibration_before'],declared['calibration_spans']),
            calibration_after=calibration(row['calibration_after'],declared['calibration_spans'])))
    same(packet['observations'],actual,'the learning-transfer packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_LEARNING_TRANSFERS status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the learning-transfer original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,image):
    if case['kind']=='publication':return publication.evaluate(case,observed,result)
    before=observed['memory_before'][0];cal=observed['calibration_before'];bank=case['argument']&255
    kind=case['kind'];wanted=[];required=[]
    grid=0x4B10 if bank else 0x4B90;aux=0x49B0 if bank else 0x49F0
    def data(at,size):
        for first,raw in cal.items():
            if first<=at and at+size<=first+len(raw):return raw[at-first:at-first+size]
        raise ValueError('the learned-grid numeric consumer lacks an exact observed calibration byte')
    def read(site,address,width,raw):wanted.append((site,'read',address,width,raw.hex()))
    def write(site,address,width,raw):wanted.append((site,'write',address,width,raw.hex()))
    def ram(at):return 0xFFFF0000+at
    def call(site,target,arguments):
        position=len(required);required.append((site,target))
        if position>=len(result['calls']):raise ValueError('the learned-grid original omits a real natural helper call')
        registers=result['calls'][position]['entry']['registers']
        if any(registers[index]!=value for index,value in arguments.items()):
            raise ValueError('the learned-grid original changes an actual post-delay helper argument')
    def auxiliary_transfers(value):
        if value['reset']:
            for index in range(64):write(0x58100,ram(aux+index),1,bytes(1))
            return
        at=aux+value['index']
        read(0x58110,ram(at),1,bytes([value['incoming']]))
        write(0x58118,ram(at),1,bytes([value['incremented']]))
        read(0x5811C,0x88F5,1,data(0x88F5,1))
        if value['decayed']:write(0x58138,ram(at),1,bytes([value['retained']]))
        read(0x58140,ram(0x134E+bank*2),2,before[0x134E+bank*2:0x1350+bank*2])
        read(0x58146,0x839C,1,data(0x839C,1))
        if value['input']<data(0x839C,1)[0]*256:read(0x58154,0x839D,1,data(0x839D,1))
        if value['outside']:write(0x58162,ram(at),1,bytes(1))
    if kind=='selection':
        expected=numeric.selection(before,bank,list(data(0x12592,8)),list(data(0x126DC,8)),
            data(0x881B,1)[0],data(0x881A,1)[0],data(0x8A9E,1)[0],data(0x8A9F,1)[0])
        at=grid+expected['index']*2
        read(0x57A8C if bank else 0x57A92,ram(at),2,before[at:at+2])
        if expected['predicate_called']:call(0x57ABC,0x25E20,{4:0x129})
        if expected['reset']:
            write(0x57AD0,ram(0x45A0+bank*2),2,bytes(2))
            call(0x57AE2 if bank else 0x57AF2,0x58092,{4:matrix.RAM_BASE+grid,5:25600,6:255})
            for index in range(64):write(0x580BC,ram(grid+index*2),2,bytes.fromhex('6400'))
            call(0x57AFA,0x580E8,{4:matrix.RAM_BASE+aux,5:255,6:bank})
            auxiliary_transfers(dict(reset=True))
        write(0x57B0C,ram(0x2306+bank*2),2,expected['output'].to_bytes(2,'big'))
        output=expected['output']
    elif kind=='learning':
        expected=numeric.learning(before,bank,list(before[0x2C21:0x2C24]),list(data(0x129C6,4)),
            data(0x8A9D,1)[0],data(0x88F5,1)[0],data(0x8A9E,1)[0],data(0x8A9F,1)[0],
            data(0x839D,1)[0],data(0x839C,1)[0])
        if expected['enabled']:
            for index in range(min(3,expected['region']+1)):
                read(0x57D7A,ram(0x134E+bank*2),2,before[0x134E+bank*2:0x1350+bank*2])
                call(0x57D86,0x22590,{4:(expected['input']-25600)&0xFFFFFFFF,14:before[0x2C21+index]})
            read(0x57DC8,ram(0x134E+bank*2),2,before[0x134E+bank*2:0x1350+bank*2])
            read(0x57DEC,ram(0x22DC+bank*2),2,before[0x22DC+bank*2:0x22DE+bank*2])
            read(0x57E0E,ram(0x2306+bank*2),2,before[0x2306+bank*2:0x2308+bank*2])
            call(0x57EC6 if bank else 0x57EBA,0x58092,
                {4:matrix.RAM_BASE+grid,5:expected['output'],6:expected['index']})
            write(0x580BC,ram(grid+expected['index']*2),2,expected['output'].to_bytes(2,'big'))
            call(0x57ED4,0x580E8,{4:matrix.RAM_BASE+aux,5:expected['index'],6:bank})
            auxiliary_transfers(expected['auxiliary'])
            output=(expected['output'],expected['auxiliary']['output'])
        else:output=None
    elif kind=='auxiliary':
        expected=numeric.auxiliary(before,bank,case['cell_index'],data(0x88F5,1)[0],
            data(0x839D,1)[0],data(0x839C,1)[0])
        auxiliary_transfers(expected);output=expected.get('output')
    else:raise ValueError('the learned-grid original changes its exact invocation family')
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('the learned-grid actual RAM disagrees with separate scalar and footprint equations')
    actual=[]
    for row in result['accesses']:
        if row['site'] not in WATCHED:continue
        address=row['address']
        if row['domain']=='ram':address=0xFFFF0000+address-matrix.RAM_BASE
        elif row['domain']!='rom':raise ValueError('a learned-grid transfer leaves its exact RAM or ROM domain')
        actual.append((row['site'],row['mode'],address,row['width_bytes'],row['bytes']))
    same(actual,wanted,'the learned-grid original changes an exact datum/site/width/direction/value or natural delay-slot transfer')
    same([(row['site'],row['target']) for row in result['calls']],required,
        'the learned-grid original changes its actual natural helper order or call closure')
    return dict(index=case['index'],kind=kind,bank=bank,output=output,accesses=actual,
        reset=expected.get('reset'),enabled=expected.get('enabled'),
        exact_learning_transfers=True,native_geometry_inference=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the learning-transfer actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry']):
            raise ValueError('a learned-grid calibration input changes tested instructions')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual learning-transfer complete state disagrees with independent natural instruction equations')
    return result,semantic(case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the learning-transfer original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the learning-transfer raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the learning-transfer original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the learning-transfer original changes current closure or exact inputs')
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,HEADER,*SOURCES}:
        raise ValueError('the learned-grid original omits an exact reused executable source')
    for name in (HARNESS,OBSERVER,*SOURCES):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the learned-grid original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the learning-transfer original changes a private entry or calibration input')
    for path in (*matrix.INPUT_SOURCES,contract.DESCRIPTOR,'tools/sh-elf-run/learning_transfer_capture.py','tools/kb/src/kb/learning_transfer_contract.py',
                 'tools/kb/src/kb/learning_transfer_matrix.py','tools/kb/src/kb/learning_transfer_semantics.py',
                 'tools/kb/src/kb/learning_publication_transfers.py',publication.ARITHMETIC_SOURCE,
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/learning_transfer_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the learning-transfer producer or independent contract source is stale')
    reconstructed=[]
    for unit in declared['source']['unit']:
        reconstructed.append(dict(unit=unit['id'],source=unit['assembly'],
            code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
                       reconstructed=image[row['start']:row['end']].hex()) for row in unit['code']],
            pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in unit['pools']]))
    same(packet['reconstruction'],reconstructed,'a learned-grid GNU reconstruction changes stock code or literal spans')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the learning-transfer original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the learned-grid original introduces a stock-function stub or observing boundary')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the learning-transfer fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the learning-transfer actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the learning-transfer original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_learning_transfer_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the learning-transfer original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the learning-transfer original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the learning-transfer original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the learning-transfer original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES};groups={key:{} for key in READERS}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((case['kind'],site,mode,address,width)
                         for site,mode,address,width,raw in value['accesses'])
        for kind,address,width in READERS:
            if case['kind']!=kind or not any(mode=='read' and at==address and size==width
                    for site,mode,at,size,raw in value['accesses']):continue
            memory=bytearray(observed['memory_before'][0])
            calibration={at:bytearray(raw) for at,raw in observed['calibration_before'].items()}
            if address>=0xFFFF0000:
                offset=address&65535;incoming=bytes(memory[offset:offset+width]);memory[offset:offset+width]=bytes(width)
            else:
                selected=[(first,raw) for first,raw in calibration.items()
                          if first<=address and address+width<=first+len(raw)]
                if len(selected)!=1:raise ValueError('a learned-grid ROM reader lacks its one exact original byte span')
                first,raw=selected[0];offset=address-first
                incoming=bytes(raw[offset:offset+width]);raw[offset:offset+width]=bytes(width)
            held=dict(memory_sha256=sha(bytes(memory)),context=list(observed['context']),
                      calibration={str(at):raw.hex() for at,raw in calibration.items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[kind,address,width].setdefault(key,set()).add((incoming.hex(),value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the learned-grid original omits a required enable, cell, clamp, reset or auxiliary branch outcome')
    for reader,alternatives in groups.items():
        if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2
                   for values in alternatives.values()):
            raise ValueError(f'the learned-grid reader {reader} lacks positive output alternatives with other inputs fixed')
    from kb import learning_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        kind={0x5796C:'selection',0x57D1E:'learning',0x580E8:'auxiliary',0x57B26:'publication'}[row['function']]
        mode='read' if row['direction']=='reader' else 'write'
        if not all((kind,site,mode,row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a learned-grid owning relation lacks its exact positive datum, path, site or direction')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_learning_transfers=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,datum_identity_inference=False,automatic_resolution=False,
        native_relation_publication=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('learning_transfer_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact learning-transfer marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the learning-transfer inputs change during independent admission')
    return result
