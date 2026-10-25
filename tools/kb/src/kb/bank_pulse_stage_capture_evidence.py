"""Independent physical and numeric admission of the bank-pulse-stage original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import bank_pulse_stage_contract as contract, byte_surface_equations as state
from kb import bank_pulse_stage_matrix as matrix, bank_pulse_stage_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-bank-pulse-stages'
PREFIX = 'kb-bank-pulse-stage-observation '
HEADER = 'bank-pulse-stage-cases.h'
HARNESS = 'harness-bank-pulse-stages.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SOURCES=('stock_jk08a_pulse_precursor.s','stock_jk08a_channel_pulse.s',
         'pulse-precursor-cases.h','channel-pulse-cases.h')
REQUIRED_BRANCHES=(0x4E992,0x4E9AC,0x4E9B8,0x4E9D6,0x4E9DE,0x4EA38,0x4EA40,
    0x4EA4E,0x4EA60,0x4EA82,0x4EA8A,0x4EA9A,0x21CF2,0x26582,0x265B0,0x265BC,
    0x4EBBA,0x4EBC4,0x4EBCE,0x4EC2A,0x4EC50,0x4EC5E,0x4EC76,0x4EC80,
    0x5B81C,0x5B854,0x5B86C,0x5B876)
WATCHED_ROM={0x4E9C0,0x4EA48,0x4EA94,0x4EC48,0x4EC64}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    from kb import bank_pulse_access_contract as owning
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the bank-pulse stage original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the bank-pulse stage original changes an exact native field, parent or semantic type')
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
    spans=matrix.calibration_spans(declared['source']);size=sum(width for at,width in spans)
    lines=['/* Explicit stage inputs; no expected outputs, GPRs or frame state. */',
           '#define BANK_PULSE_STAGE_REGION '+json.dumps(REGION),
           f'#define BANK_PULSE_STAGE_CALIBRATION_SIZE {size}U',
           'static const uint32_t bank_pulse_stage_calibration_starts[] = {'+
           ','.join(f'0x{at:x}U' for at,width in spans)+'};',
           'static const uint32_t bank_pulse_stage_calibration_sizes[] = {'+
           ','.join(f'{width}U' for at,width in spans)+'};',
           'struct path_case {',
           '    uint32_t kind,'+','.join(matrix.FIELDS)+';',
           '    struct context context;',
           '    uint8_t calibration[BANK_PULSE_STAGE_CALIBRATION_SIZE];',
           '};',
           'static const struct path_case bank_pulse_stage_cases[] = {']
    for case in declared['cases']:
        values=','.join(f'0x{value:x}U' for value in (matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS)))
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[at] for at,width in spans)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+values+',{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the bank-pulse-stage original repeats a raw observation JSON key')
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
        raise ValueError('the bank-pulse-stage original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the bank-pulse-stage original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the bank-pulse-stage original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the bank-pulse-stage original mutates its const input context')
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
    same(packet['observations'],actual,'the bank-pulse-stage packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_BANK_PULSE_STAGES status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the bank-pulse-stage original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,precursor_numeric=None):
    before=observed['memory_before'][0];cal=observed['calibration_before'];wanted=[];required=[]
    def read(site,address,width,raw):wanted.append((site,'read',address,width,raw.hex()))
    def write(site,address,width,raw):wanted.append((site,'write',address,width,raw.hex()))
    def ramread(site,at,width=2):read(site,0xFFFF0000+at,width,before[at:at+width])
    def ramwrite(site,at,width,value):write(site,0xFFFF0000+at,width,value.to_bytes(width,'big'))
    def call(site,target,arguments):
        position=len(required);required.append((site,target))
        if position>=len(result['calls']):raise ValueError('a bank-pulse stage omits a real helper call')
        registers=result['calls'][position]['entry']['registers']
        if any(registers[index]!=value for index,value in arguments.items()):
            raise ValueError('a bank-pulse stage changes an actual post-delay helper argument')
    if case['kind']=='precursor':
        if precursor_numeric is None:raise ValueError('the precursor lacks its separate existing arithmetic equations')
        expected=numeric.precursor(before,cal,precursor_numeric);values=expected['inputs']
        ramread(0x4E98E,0x245D,1)
        ramread(0x4E998,0x123E) if values['source_flags']&32 else ramread(0x4E9A2,0x1024)
        ramread(0x4E9A8,0x24D2,1)
        if values['cap_flags']&1:
            ramread(0x4E9B2,0x11BC)
            if values['speed']:
                read(0x4E9C0,0x96E0,4,numeric.data(cal,0x96E0,4))
                call(0x4E9C2,0x21CE0,{0:values['speed'],1:values['cap_numerator']})
            ramread(0x4E9D0,0x34F6);ramwrite(0x4E9E8,0x196A,2,expected['selected_bfs'])
        ramread(0x4E9F2,0x22E6)
        for bank in (0,1):
            ramread(0x4EA10,0x40B6+bank*2);ramread(0x4EA1C,0x2300)
            call(0x4EA20,0x21CE0,{0:25600,1:expected['bank_numerators'][bank]})
            ramread(0x4EA30,0x165E)
            call(0x4EA32,0x2657C,{4:(expected['bank_quotients'][bank]+expected['transient'])&0xFFFFFFFF,
                5:values['gain'],6:0xFFFFFFFE})
            read(0x4EA48,0x94E8,2,numeric.data(cal,0x94E8,2))
            ramwrite(0x4EA62,0x18C0+bank*2,2,expected[f'bank{bank}_output'])
        ramread(0x4EA6C,0x2300);ramread(0x4EA74,0x165E)
        call(0x4EA78,0x2657C,{4:(expected['h']+expected['transient'])&0xFFFFFFFF,
            5:values['gain'],6:0xFFFFFFFE})
        ramread(0x4EA7E,0x24A1,1);read(0x4EA94,0x94E8,2,numeric.data(cal,0x94E8,2))
        ramwrite(0x4EAA8,0x24A1,1,expected['updated_flags']);ramwrite(0x4EAB0,0x1876,2,expected['common_output'])
    else:
        index=case['channel'];expected=numeric.channel(before,cal,index)
        ramread(0x4EBC8,0x22E0,1)
        if expected['inhibited']:
            ramread(0x4EBD2,0x2436);ramwrite(0x4EBDA,0x23D4+index*2,2,expected['transformed'])
        else:
            ramread(0x4EC2E if index&1 else 0x4EC36,0x191C+(index&1)*2)
            ramread(0x4EC42,0x1396+index*2);read(0x4EC48,0x8D92,1,numeric.data(cal,0x8D92,1))
            if expected['flag']&8:ramread(0x4EC58,0x1466+index*2)
            if expected['positive']:
                read(0x4EC64,0x129C0+index,1,numeric.data(cal,0x129C0+index,1))
                call(0x4EC6C,0x224F8,{0:expected['product']})
            call(0x4EC88,0x5B7EC,{4:expected['compensated']})
            ramwrite(0x4EC94,0x23D4+index*2,2,expected['transformed'])
        ramwrite(0x4EC9E,0x23C8+index*2,2,expected['compensated'])
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('a bank-pulse stage actual RAM differs from its separate existing scalar and footprint equations')
    actual=[]
    for row in result['accesses']:
        if row['domain']!='ram' and row['site'] not in WATCHED_ROM:continue
        address=row['address']
        if row['domain']=='ram':address=0xFFFF0000+address-matrix.RAM_BASE
        elif row['domain']!='rom':raise ValueError('a bank-pulse stage leaves its exact RAM/ROM domain')
        actual.append((row['site'],row['mode'],address,row['width_bytes'],row['bytes']))
    same(actual,wanted,'a bank-pulse stage changes an exact datum/site/width/direction/value or delay-slot transfer')
    same([(row['site'],row['target']) for row in result['calls']],required,
        'a bank-pulse stage changes its exact real helper order or closure')
    return dict(index=case['index'],kind=case['kind'],entry=case['entry'],output=expected['output'],accesses=actual,
        exact_bank_pulse_stages=True,native_geometry_inference=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the bank-pulse-stage actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry']):
            raise ValueError('a bank-pulse stage calibration input changes tested instructions')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual bank-pulse-stage complete state disagrees with independent natural instruction equations')
    precursor_numeric=None
    if case['kind']=='precursor':
        from kb.test_stock_capture import tool
        precursor_numeric=tool(repo.ROOT if root is None else root,Path(numeric.PRECURSOR_NUMERIC).name,'_kb_bank_pulse_stage_numeric')
    return result,semantic(case,observed,result,precursor_numeric)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the bank-pulse-stage original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the bank-pulse-stage raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the bank-pulse-stage original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the bank-pulse-stage original changes current closure or exact inputs')
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,HEADER,*SOURCES}:
        raise ValueError('the bank-pulse stage original omits an exact reused executable source')
    for name in (HARNESS,OBSERVER,*SOURCES):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the bank-pulse stage original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the bank-pulse-stage original changes a private entry or calibration input')
    for path in (*matrix.INPUT_SOURCES,contract.DESCRIPTOR,'tools/sh-elf-run/bank_pulse_stage_capture.py','tools/kb/src/kb/bank_pulse_stage_contract.py',
                 'tools/kb/src/kb/bank_pulse_stage_matrix.py','tools/kb/src/kb/bank_pulse_stage_semantics.py',
                 'tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/bank_pulse_stage_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py',
                 numeric.PRECURSOR_NUMERIC,numeric.CHANNEL_ARITHMETIC_SOURCE):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the bank-pulse-stage producer or independent contract source is stale')
    reconstructed=[]
    for unit in declared['source']['unit']:
        reconstructed.append(dict(unit=unit['id'],source=unit['assembly'],
            code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
                       reconstructed=image[row['start']:row['end']].hex()) for row in unit['code']],
            pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in unit['pools']]))
    same(packet['reconstruction'],reconstructed,'a bank-pulse stage GNU reconstruction changes stock code or literal spans')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the bank-pulse-stage original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the bank-pulse stage original introduces a stock-function stub or observing boundary')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the bank-pulse-stage fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the bank-pulse-stage actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the bank-pulse-stage original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_bank_pulse_stage_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the bank-pulse-stage original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the bank-pulse-stage original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the bank-pulse-stage original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the bank-pulse-stage original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES};groups={}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((case['entry'],site,mode,address,width)
                         for site,mode,address,width,raw in value['accesses'])
        if case['kind']=='precursor':
            at=0x40B8;memory=bytearray(observed['memory_before'][0]);incoming=bytes(memory[at:at+2]);memory[at:at+2]=bytes(2)
            held=dict(memory_sha256=sha(bytes(memory)),context=list(observed['context']),
                calibration={str(address):data.hex() for address,data in observed['calibration_before'].items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups.setdefault(key,set()).add((incoming.hex(),value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the bank-pulse stage original omits a required conditional branch outcome')
    if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2
               for values in groups.values()):
        raise ValueError('the bank1 multiplier lacks positive output alternatives with every other input fixed')
    from kb import bank_pulse_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['component']!='bank_pulse_stages':continue
        kind=row['function']
        mode='read' if row['direction']=='reader' else 'write'
        if not all((kind,site,mode,row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a bank-pulse stage owning relation lacks its exact positive datum, path, site or direction')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_bank_pulse_stages=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,datum_identity_inference=False,automatic_resolution=False,
        native_relation_publication=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('bank_pulse_stages')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact bank-pulse-stage marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the bank-pulse-stage inputs change during independent admission')
    return result
