"""Independent physical and full-state admission of the existing record-member and bounded coordinator call."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import maf_record_contract as contract,maf_record_matrix as matrix
from kb import maf_record_semantics as scalar
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-maf-record-paths'
PREFIX='kb-maf-record-observation '
HEADER='maf-record-cases.h'
HARNESS='harness-maf-record.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN='publication_inhibit_snapshot_return.s'
REQUIRED_BRANCHES=(0x25E26,0x3C3D0)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import maf_access_contract as owning
    if not {row['parent'] for row in contract.WINDOWS}<=set(model.functions.get('7mfk',())):
        raise ValueError('the MAF record reader original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        if row['component']!='maf_record_paths':continue
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the MAF record reader original changes an exact native field, parent or semantic type')
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
    return proof_adapter.header(declared['source']['adapter'],declared['cases'],
        lambda case: matrix.context(declared['source'],case),
        None)





def observations(packet,declared):
    return proof_transport.decode(packet,declared,declared['source']['adapter'])



def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the MAF record reader original changes its complete incoming frame, SP or caller ABI')
    source=dict(declared['source'],entry=[*declared['source']['entry'],dict(start=contract.BOUNDARY['address'],end=contract.BOUNDARY['address']+8)])
    result=state.execute(source,fixture,context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the MAF record reader original disagrees with complete independent instruction-state equations')
    return result,scalar.evaluate(case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the MAF record reader original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the MAF record reader packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the MAF record reader original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the MAF record reader original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,RETURN,HEADER}:
        raise ValueError('the MAF record reader original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER,RETURN):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the MAF record reader original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the MAF record reader original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/maf_record_capture.py',
            'tools/kb/src/kb/maf_record_contract.py','tools/kb/src/kb/maf_record_matrix.py',
            'tools/kb/src/kb/maf_record_capture_evidence.py','tools/kb/src/kb/maf_record_semantics.py',
            'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/width_view_matrix.py',
            'tools/kb/tests/test_ram_structure.py',*proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the MAF record independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                    reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the MAF record reader GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the MAF record reader fixture changes its exact base-pointer alias')
    if type(packet['boundaries']) is not list or len(packet['boundaries'])!=1:
        raise ValueError('the MAF record reader lacks its independently reconstructed observing return')
    stub=packet['boundaries'][0];boundary=contract.BOUNDARY
    if type(stub) is not dict or set(stub)!={'address','bytes','source_sha256','object_sha256','elf_sha256'}:
        raise ValueError('the MAF record reader return lacks its exact source/object/ELF schema')
    same((stub['address'],stub['bytes'],stub['source_sha256']),
        (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
        'the MAF record reader observing return changes bytes, address or private source')
    for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the MAF record reader fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the MAF record reader original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the MAF record reader original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_maf_record_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the MAF record reader original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the MAF record reader original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the MAF record reader original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the MAF record reader original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES};groups={entry:{} for entry in (0x25E20,0x3C3C6)}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((row['site'],row['mode'],0xFFFF0000+row['address']-matrix.RAM_BASE,row['width_bytes'])
                         for row in result['accesses'] if row['domain']=='ram')
        if not any(row['site']==0x25E32 and row['mode']=='read' and row['address']==matrix.RAM_BASE+0x5A94
                   and row['width_bytes']==1 for row in result['accesses']):continue
        memory=bytearray(observed['memory_before'][0]);incoming=memory[0x5A94];memory[0x5A94]=0
        held=dict(memory=memory.hex(),context=list(observed['context']),
            calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups[case['entry']].setdefault(key,set()).add((incoming,value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the MAF record reader omits its predicate sentinel or coordinator branch outcome')
    for alternatives in groups.values():
        if not any(len({item[0] for item in values})>=2 and len({item[1] for item in values})>=2
                   for values in alternatives.values()):
            raise ValueError('a record-member reader lacks positive output alternatives with every other input fixed')
    from kb import maf_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['component']!='maf_record_paths':continue
        address=row['address']+row['member_offset']
        if not all((site,'read',address,row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a record-member owning relation lacks its positive exact byte1 transfer')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_MAF_record_reads=True,native_geometry_inference=False,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('maf_record_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique MAF record reader component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the MAF record reader inputs change during admission')
    return result
