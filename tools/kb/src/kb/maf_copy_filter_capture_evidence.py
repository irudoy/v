"""Independent physical and numeric admission of the maf-copy-filter original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import maf_copy_filter_contract as contract, byte_surface_equations as state
from kb import maf_copy_filter_matrix as matrix, maf_copy_filter_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-maf-copy-filter-paths'
PREFIX = 'kb-maf-copy-filter-observation '
HEADER = 'maf-copy-filter-path-cases.h'
HARNESS = 'harness-maf-copy-filter-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = {0x3A998: {'taken'}, 0x3A99E: {'taken'},
    0x3A9CA: {'taken','fallthrough'}, 0x3A9EE: {'taken','fallthrough'},
    0x3A9F2: {'taken','fallthrough'}, 0x3A9F6: {'taken','fallthrough'}}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the MAF original omits a normalized natural function')
    result=[]
    for kind,address,owner in (('fn',0x3A982,'brass-ammonite/fn'),('fn',0x3A9AA,'sandy-chameleon/fn'),
            ('ram',0xFFFF1056,'opalescent-pronghorn/ram'),('ram',0xFFFF105A,'dancing-hippo/ram'),
            ('ram',0xFFFF1DF2,'spiked-dalmatian/ram')):
        symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the MAF original changes its exact current function or word owner')
        if kind=='ram' and (not test_contract.exact(symbol.value('width'),16)
                            or symbol.value('signed') is not False):
            raise ValueError('the MAF original changes an existing unsigned 16-bit storage fact')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
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
    lines=['/* Explicit natural bank/word/mode/coefficient inputs; no expected results. */',
        '#define MAF_COPY_FILTER_REGION '+json.dumps(REGION),
        'static const uint8_t maf_copy_filter_stock_calibrations[] = {26U};',
        'static const struct path_case maf_copy_filter_cases[] = {']
    for case in declared['cases']:
        values=(case['entry'],matrix.KINDS.index(case['kind']),case['argument'],case['input'],
                case['previous'],case['flags'],case['coefficient'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the maf-copy-filter original repeats a raw observation JSON key')
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
        raise ValueError('the maf-copy-filter original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the maf-copy-filter original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the maf-copy-filter original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the maf-copy-filter original mutates its const input context')
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
    same(packet['observations'],actual,'the maf-copy-filter packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_MAF_COPY_FILTER status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the maf-copy-filter original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,image):
    expected=numeric.output(case['kind'],case['argument'],observed['memory_before'][0],case['coefficient'])
    if observed['memory_after']!=(expected['memory'],) or observed['exit'][19]!=expected['bank_offset']:
        raise ValueError('the MAF RAM or return offset disagrees with independent copy/filter/anti-stall equations')
    source,destination=matrix.RAM_BASE+expected['source'],matrix.RAM_BASE+expected['destination']
    physical=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes'])
              for row in result['accesses'] if row['domain']=='ram']
    if case['kind']=='copy':
        wanted=[(0x3A98E,'read',source,2,expected['input'].to_bytes(2,'big').hex()),
                (0x3A9A8,'write',destination,2,expected['output'].to_bytes(2,'big').hex())]
    else:
        wanted=[(0x3A9BE,'read',source,2,expected['input'].to_bytes(2,'big').hex()),
                (0x3A9C0,'read',matrix.RAM_BASE+0x2461,1,bytes([case['flags']]).hex())]
        if expected['weighted']:
            wanted.append((0x3A9CE,'read',destination,2,expected['previous'].to_bytes(2,'big').hex()))
        wanted.append((0x3AA08 if expected['weighted'] else 0x3AA0A,'write',destination,2,
                       expected['output'].to_bytes(2,'big').hex()))
    if physical!=wanted:
        raise ValueError('the MAF original changes an exact datum, bank, access site, direction, width or delay-slot store')
    coefficient=[(row['address'],row['width_bytes'],row['bytes']) for row in result['accesses'] if row['site']==0x3A9D4]
    if coefficient!=([(0x870A,1,bytes([case['coefficient']]).hex())] if expected['weighted'] else []):
        raise ValueError('the MAF original changes its conditional real coefficient-byte read')
    if result['calls']:
        raise ValueError('a MAF natural entry invokes an undeclared helper')
    return dict(index=case['index'],kind=case['kind'],bank=case['argument']&255,
        input=expected['input'],output=expected['output'],weighted=expected['weighted'],step=expected['step'],
        accesses=[dict(site=site,mode=mode,address=0xFFFF0000+(address-matrix.RAM_BASE),width_bytes=width,bytes=raw)
                  for site,mode,address,width,raw in physical],
        native_relation_publication=False,datum_identity_inference=False,scale_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the maf-copy-filter actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'] if row['address']!=0x870A)):
            raise ValueError('a maf-copy-filter calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual maf-copy-filter complete state disagrees with independent natural instruction equations')
    return result,semantic(case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the maf-copy-filter original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the maf-copy-filter raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the maf-copy-filter original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the maf-copy-filter original changes current closure or exact inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the maf-copy-filter original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the maf-copy-filter original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the maf-copy-filter original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/maf_copy_filter_capture.py','tools/kb/src/kb/maf_copy_filter_contract.py',
                 'tools/kb/src/kb/maf_copy_filter_matrix.py','tools/kb/src/kb/maf_copy_filter_semantics.py',
                 'tools/kb/src/kb/division_callees_semantics.py','tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/maf_copy_filter_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the maf-copy-filter producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in declared['source']['pool']])
    same(packet['reconstruction'],reconstructed,'the maf-copy-filter GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the maf-copy-filter original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the maf-copy-filter original replaces a natural return')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the maf-copy-filter fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the maf-copy-filter actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or simulator['returncode']!=0 or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the maf-copy-filter original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_maf_copy_filter_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the maf-copy-filter original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the maf-copy-filter original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the maf-copy-filter original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the maf-copy-filter original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[];coverage={site:set() for site in REQUIRED_BRANCHES};groups={}
    for case,observed in zip(declared['cases'],actual):
        result,semantic_result=require_state(declared,image,fixture,case,observed)
        semantics.append(semantic_result)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        memory=bytearray(observed['memory_before'][0])
        start=(0x1054 if case['kind']=='copy' else 0x1058)+(case['argument']&255)*2
        memory[start:start+2]=bytes(2)
        held=dict(kind=case['kind'],bank=case['argument']&255,weighted=semantic_result['weighted'],
            memory=memory.hex(),context=list(observed['context']),
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups.setdefault(key,set()).add((semantic_result['input'],semantic_result['output']))
    if any(coverage[site]!=required for site,required in REQUIRED_BRANCHES.items()):
        raise ValueError('the MAF original omits a feasible natural branch outcome or changes a typed-copy invariant')
    for kind,weighted in (('copy',False),('filter',False),('filter',True)):
        for bank in (0,1):
            choices=[values for key,values in groups.items() if
                (json.loads(key)['kind'],json.loads(key)['bank'],json.loads(key)['weighted'])==(kind,bank,weighted)]
            if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2 for values in choices):
                raise ValueError('the MAF original lacks positive input/output variation with complete other inputs fixed')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        exact_banked_word_accesses=True,native_geometry_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('maf_copy_filter_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact maf-copy-filter marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the maf-copy-filter inputs change during independent admission')
    return result
