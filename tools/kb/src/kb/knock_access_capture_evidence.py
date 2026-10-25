"""Independent actual-original, complete-state and physical knock admission."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import knock_access_unit_contract as contract,knock_access_matrix as matrix
from kb import knock_access_semantics as numeric,knock_access_transfers as physical
from kb import byte_surface_equations as state
from kb.model import SymbolKey

REGION='jk08a-knock-accesses'
PREFIX='kb-knock-access-observation '
HEADER='knock-access-cases.h'
HARNESS='harness-knock-accesses.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN=Path(contract.RETURN_SOURCE).name


def sha(value):return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def sources(kind):
    unit=next(unit for unit in contract.UNITS if unit['id']==kind)
    return (Path(unit['assembly']).name,Path(matrix.INPUT_SOURCES[matrix.KINDS.index(kind)]).name)


def native_bindings(model):
    from kb import knock_access_contract as owning
    rows=owning.descriptor(model.root)['reference']
    if not {row['function'] for row in rows}<=set(model.functions.get('7mfk',())):
        raise ValueError('the knock original lacks a current normalized owning function')
    result=[]
    for row in rows:
        symbol=model.symbols.get(owning.symbol_key(row));old=json.loads(row['original_claim_json'])
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the knock original changes an exact native field, function or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image,kind):
    source=contract.selection(model.root,kind);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,kind=kind,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),
        calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    spans=matrix.calibration_spans(declared['source']);size=sum(width for at,width in spans)
    lines=['/* Explicit knock stage inputs; no expected outputs, GPRs or frame state. */',
        '#define KNOCK_ACCESS_REGION '+json.dumps(REGION),
        f'#define KNOCK_ACCESS_KIND {matrix.KINDS.index(declared["kind"])}U',
        f'#define KNOCK_ACCESS_CALIBRATION_SIZE {size}U',
        'static const uint32_t knock_access_calibration_starts[] = {'+
        ','.join(f'0x{at:x}U' for at,width in spans)+'};',
        'static const uint32_t knock_access_calibration_sizes[] = {'+
        ','.join(f'{width}U' for at,width in spans)+'};',
        'struct path_case {','    uint32_t kind,'+','.join(matrix.FIELDS)+';',
        *('    uint32_t '+name+'['+str(count)+'];' for name,count in matrix.ARRAYS),
        '    struct context context;',
        '    uint8_t calibration[KNOCK_ACCESS_CALIBRATION_SIZE];','};',
        'static const struct path_case knock_access_cases[] = {']
    for case in declared['cases']:
        values=','.join(f'0x{value:x}U' for value in
            (matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS)))
        arrays=','.join('{'+','.join(f'0x{value:x}U' for value in case[name])+'}' for name,count in matrix.ARRAYS)
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[at] for at,width in spans)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+values+','+arrays+',{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the knock stage original repeats a raw observation JSON key')
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
        raise ValueError('the knock stage original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the knock stage original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the knock stage original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the knock stage original mutates its const input context')
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
    same(packet['observations'],actual,'the knock stage packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_KNOCK_ACCESSES status=PASS region={REGION} kind={declared["kind"]} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the knock stage original lacks its unique complete marker')
    return parsed



def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed);context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big');seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('a knock actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry']):
            raise ValueError('a knock calibration input changes tested instructions or its observing return')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('a knock complete actual state disagrees with independent instruction equations')
    return result,physical.evaluate(case,observed,result)


def positive_key(observed,address,width,*,rom=False):
    memory=bytearray(observed['memory_before'][0]);cal=dict(observed['calibration_before'])
    if rom:
        found=[]
        for start,raw in cal.items():
            if start<=address and address+width<=start+len(raw):
                value=bytearray(raw);incoming=bytes(value[address-start:address-start+width])
                value[address-start:address-start+width]=bytes(width);cal[start]=bytes(value);found.append(incoming)
        if len(found)!=1:raise ValueError('a positive knock ROM alternative leaves its exact input datum')
        incoming=found[0]
    else:
        at=address&65535;incoming=bytes(memory[at:at+width]);memory[at:at+width]=bytes(width)
    held=dict(memory_sha256=sha(bytes(memory)),context=list(observed['context']),
        calibration={str(start):raw.hex() for start,raw in cal.items()})
    return json.dumps(held,sort_keys=True,separators=(',',':')),incoming.hex()


def require_positive(values,reason):
    if not any(len({item[0] for item in group})>=2 and len({item[1] for item in group})>=2 for group in values.values()):
        raise ValueError(reason)


def require_unit(model,image,kind,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('a knock stage original lacks its complete raw schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'a knock raw packet grants its own admission')
    root=Path(model.root).resolve()
    if packet['image_sha256']!=sha(image):raise ValueError('a knock stage changes its exact owned stock image')
    declared=declaration(model,image,kind);same(packet['declaration'],declared,'a knock stage changes its exact closure or inputs')
    names=(HARNESS,OBSERVER,RETURN,*sources(kind));consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HEADER,*names}:raise ValueError('a knock original omits an exact executable source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('a knock original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():raise ValueError('a knock original changes a private entry/calibration input')
    unit=declared['source']['unit'][0]
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in unit['code']],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in unit['pools']])
    same(packet['reconstruction'],reconstructed,'a knock GNU reconstruction changes stock code or literal spans')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'a knock original changes an exact unit-local RAM pointer')
    if type(packet['boundaries']) is not list or len(packet['boundaries'])!=len(unit['boundary']):
        raise ValueError('a knock stage changes its separate observing boundary count')
    for stub,boundary in zip(packet['boundaries'],unit['boundary']):
        if type(stub) is not dict or set(stub)!={'address','bytes','source_sha256','object_sha256','elf_sha256'}:
            raise ValueError('a knock return lacks its independent source/object/ELF reconstruction')
        same((stub['address'],stub['bytes'],stub['source_sha256']),
            (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
            'a knock observing return changes bytes, address or private source')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('a knock fixture changes an undeclared stock byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('a knock actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('a knock original changes its bounded actual command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_knock_access_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('a knock original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=kind or elf.parent.parent.name!=REGION:
        raise ValueError('a knock original executes another separate stage artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'a knock original changes compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('a knock original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set();groups={key:{} for key in ('source','axis')}
    coverage={site:set() for site in physical.REQUIRED_BRANCHES[kind]}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((site,mode,address,width) for site,mode,address,width,raw in value['accesses'])
        if case['channel']==1:
            at,width,rom=(0xFFFF2132,2,False) if kind=='normalization' else (
                (0xFFFF20C2,2,False) if kind=='metric' else (0x1108E,2,True))
            key,incoming=positive_key(observed,at,width,rom=rom)
            outputs=(value['scalar']['total'],value['scalar']['scaled'],value['scalar']['biased']) if kind=='metric' else (value['output'],)
            groups['source'].setdefault(key,set()).add((incoming,outputs))
            if kind in ('threshold','comparison'):
                key,incoming=positive_key(observed,0x15340,2,rom=True)
                groups['axis'].setdefault(key,set()).add((incoming,(value['output'],)))
    if any(values!={'taken','fallthrough'} for values in coverage.values()):
        raise ValueError('a knock original omits a required conditional branch outcome')
    require_positive(groups['source'],'a knock datum lacks positive output alternatives with every other input fixed')
    if kind=='metric':
        for index in range(3):
            projected={key:{(incoming,(output[index],)) for incoming,output in values} for key,values in groups['source'].items()}
            require_positive(projected,'a knock metric sum/signed/biased publication lacks its own positive alternatives')
    if kind in ('threshold','comparison'):require_positive(groups['axis'],'a knock axis lacks positive output alternatives with every other input fixed')
    return dict(kind=kind,region=REGION,fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),semantic_results=semantics,
        transfers=sorted(transfers),exact_knock_accesses=True,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()})


def require_witness(model,packet,inputs):
    if type(packet) is not dict or set(packet)!={'schema','semantic_admission','units'}:
        raise ValueError('the knock original lacks its exact four-stage raw container')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the knock raw container grants its own admission')
    if type(packet['units']) is not dict or set(packet['units'])!=set(matrix.KINDS):
        raise ValueError('the knock original omits or duplicates a separate stock stage')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256:raise ValueError('the knock original changes its owned stock image')
    for path in (contract.DESCRIPTOR,*matrix.INPUT_SOURCES,*numeric.ARITHMETIC_SOURCES,
        'defs/JK08A.knock-access-claims.toml','tools/kb/src/kb/knock_access_contract.py',
        'tools/kb/src/kb/knock_access_evidence.py','tools/kb/src/kb/knock_access_resolution.py',
        'tools/sh-elf-run/knock_access_capture.py','tools/kb/src/kb/knock_access_unit_contract.py',
        'tools/kb/src/kb/knock_access_matrix.py','tools/kb/src/kb/knock_access_semantics.py',
        'tools/kb/src/kb/knock_access_transfers.py','tools/kb/src/kb/knock_access_capture_evidence.py',
        'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a knock independent or producer source is stale')
    units={kind:require_unit(model,image,kind,packet['units'][kind],inputs) for kind in matrix.KINDS}
    from kb import knock_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['owner']=='knock_normalized_cache/ram':kind='normalization'
        elif row['function'] in (0x49D88,0x49E96):kind='metric'
        elif row['function']==0x4A238:kind='comparison'
        else:kind='threshold'
        admitted={tuple(value) for value in units[kind]['transfers']};mode='read' if row['direction']=='reader' else 'write'
        if not all((site,mode,row['address'],row['width_bytes']) in admitted for site in row['sites']):
            raise ValueError('a knock owning relation lacks its exact datum, helper path, sites or direction')
    return dict(region=REGION,image_sha256=sha(image),units=units,native_bindings=native_bindings(model),
        exact_knock_accesses=True,native_geometry_inference=False,datum_identity_inference=False,
        automatic_resolution=False,native_relation_publication=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('knock_accesses')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    for kind in matrix.KINDS:
        if original.count(packet['units'][kind]['marker'])!=1:
            raise ValueError('the original complete primary lacks a unique exact knock stage marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the knock inputs change during independent admission')
    return result
