"""Independent physical and full-state admission of the bounded two-curve lookup slice."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import maf_transfer_contract as contract,maf_transfer_matrix as matrix
from kb import maf_transfer_semantics as scalar
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-maf-transfer-paths'
PREFIX='kb-maf-transfer-observation '
HEADER='maf-transfer-cases.h'
HARNESS='harness-maf-transfer.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN='publication_inhibit_snapshot_return.s'
REQUIRED_BRANCHES=(0x26416,0x26742)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import maf_access_contract as owning
    if 0x3A904 not in model.functions.get('7mfk',()):
        raise ValueError('the MAF curve slice original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        if row['component']!='maf_transfer_paths':continue
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['correct_original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the MAF curve slice original changes an exact native field, parent or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[[row['address'],row['size']] for row in contract.POOLS],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Explicit ADC16 and curve inputs; no expected outputs. */',
           '#define MAF_TRANSFER_REGION '+json.dumps(REGION),
           'static const struct path_case maf_transfer_cases[] = {']
    for case in declared['cases']:
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        fields=','.join(f'0x{case[key]:x}U' for key in ('entry','adc1','adc2'))
        curves=matrix.calibrations(declared['source'],image,case)[0x141F4]
        data=','.join(f'0x{value:02x}U' for value in curves)
        lines.append('    {'+fields+',{{'+registers+'},'+tail+'},{'+data+'}},')
    return '\n'.join((*lines,'};','')).encode()



def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the MAF curve slice original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the MAF curve slice original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the MAF curve slice original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the MAF curve slice original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the MAF curve slice original mutates its const input context')
        calibration={}
        for name in ('calibration_before','calibration_after'):
            data=test_stock_abi.raw(row[name],sum(pool['size'] for pool in contract.POOLS))
            calibration[name]={};offset=0
            for pool in contract.POOLS:
                size=pool['size'];calibration[name][pool['address']]=data[offset:offset+size];offset+=size
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=case['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(width_view_matrix.decode_rle(row['ram_before']),),
            memory_after=(width_view_matrix.decode_rle(row['ram_after']),),
            **calibration))
    same(packet['observations'],actual,'the MAF curve slice packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_MAF_TRANSFER status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the MAF curve slice original lacks its unique complete marker')
    return parsed



def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the MAF curve slice original changes its complete incoming frame, SP or caller ABI')
    source=dict(declared['source'],entry=[*declared['source']['entry'],dict(start=contract.BOUNDARY['address'],end=contract.BOUNDARY['address']+8)])
    active=bytearray(fixture)
    for at,data in observed['calibration_before'].items():active[at:at+len(data)]=data
    for row in contract.WINDOWS:
        if active[row['start']:row['end']]!=fixture[row['start']:row['end']]:
            raise ValueError('the MAF curve input calibration changes a tested instruction')
    result=state.execute(source,bytes(active),context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the MAF curve slice original disagrees with complete independent instruction-state equations')
    return result,scalar.evaluate(case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the MAF curve slice original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the MAF curve slice packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the MAF curve slice original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the MAF curve slice original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,RETURN,HEADER}:
        raise ValueError('the MAF curve slice original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER,RETURN):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the MAF curve slice original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the MAF curve slice original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/maf_transfer_capture.py',
            'tools/kb/src/kb/maf_transfer_contract.py','tools/kb/src/kb/maf_transfer_matrix.py',
            'tools/kb/src/kb/maf_transfer_capture_evidence.py','tools/kb/src/kb/maf_transfer_semantics.py',
            'tools/kb/src/kb/byte_surface_equations.py',
            'tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the MAF curve slice independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                    reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the MAF curve slice GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the MAF curve slice fixture changes its exact base-pointer alias')
    if type(packet['boundaries']) is not list or len(packet['boundaries'])!=1:
        raise ValueError('the MAF curve slice lacks its independently reconstructed observing return')
    stub=packet['boundaries'][0];boundary=contract.BOUNDARY
    if type(stub) is not dict or set(stub)!={'address','bytes','source_sha256','object_sha256','elf_sha256'}:
        raise ValueError('the MAF curve slice return lacks its exact source/object/ELF schema')
    same((stub['address'],stub['bytes'],stub['source_sha256']),
        (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
        'the MAF curve slice observing return changes bytes, address or private source')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the MAF curve slice fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the MAF curve slice original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the MAF curve slice original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_maf_transfer_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the MAF curve slice original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the MAF curve slice original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the MAF curve slice original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the MAF curve slice original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES};groups={row['address']:{} for row in contract.CURVES}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if branch['site']==0x26A9A and branch['kind']!='fallthrough':
                raise ValueError('the word-curve wrapper enters the unrelated byte-curve arm')
        transfers.update((row['site'],row['mode'],row['address'],row['width_bytes'])
                         for row in result['accesses'] if row['domain']=='rom')
        for curve in contract.CURVES:
            at=curve['address'];offset=at-0x141F4
            if not any(row['site']==0x26AA0 and row['mode']=='read' and row['address']==at
                       and row['width_bytes']==2 for row in result['accesses']):continue
            calibration={str(address):data.hex() for address,data in observed['calibration_before'].items()}
            data=bytearray(observed['calibration_before'][0x141F4]);incoming=bytes(data[offset:offset+2])
            data[offset:offset+2]=bytes(2);calibration[str(0x141F4)]=data.hex()
            held=dict(memory=observed['memory_before'][0].hex(),context=list(observed['context']),calibration=calibration)
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[at].setdefault(key,set()).add((incoming.hex(),value['output'][curve['channel']]))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the MAF curve slice omits a required clamp or interpolation outcome')
    for alternatives in groups.values():
        if not any(len({item[0] for item in values})>=2 and len({item[1] for item in values})>=2
                   for values in alternatives.values()):
            raise ValueError('a MAF curve root lacks positive output alternatives with every other input fixed')
    from kb import maf_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['component']!='maf_transfer_paths':continue
        if not all((site,'read',row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a corrected MAF curve reader lacks its positive exact root transfer')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_MAF_curve_reads=True,native_geometry_inference=False,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('maf_transfer_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique MAF curve slice component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the MAF curve slice inputs change during admission')
    return result
