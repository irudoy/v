"""Independent complete bank2 CVTC originals and exact indexed constant-reader admission."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import test_contract,test_stock_abi,width_view_matrix
from kb import exhaust_cvtc_contract as contract,exhaust_cvtc_matrix as matrix
from kb import exhaust_cvtc_semantics as semantics,exhaust_cvtc_transfers as transfers
from kb.model import SymbolKey

REGION='jk08a-exhaust-cvtc-transition-paths'
PREFIX='kb-exhaust-cvtc-observation '
HEADER='exhaust-cvtc-path-cases.h'
HARNESS='harness-exhaust-cvtc-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0xC1E0A,0xC1E18,0xC1E28,0xC1E3A,0xC1E44,0xC1E5C,
    0xC1E6C,0xC1E80,0xC1E88,0xC1E9A,0xC1EAA,0xC1EC0,0xC1EEA,0xC1F64,
    0xC1FA2,0xC1FD8,0xC1FDE,0xC209A,0xC20BC,0xC20C8,0xC20EA,0xC20F2,
    0xC20FE,0xC212C,0xC2132,0x2694C,0x26950,0x26954,0x26978,0x26742,
    0x21CF2,0x21F52,0x21F66,0x21FC2)
FIXED_BRANCHES={0x21CE4:'fallthrough',0x21CEA:'fallthrough',0x21F44:'fallthrough',
    0x21F4A:'fallthrough',0x26C7A:'fallthrough',0xC1EF0:'taken',0xC1FEA:'fallthrough'}
EXCLUDED_RANGES=((0x21D6A,0x21DC6),(0x21FD0,0x2202E),(0x26D0A,0x26D0E))
SOURCE_FILES=('tools/kb/src/kb/exhaust_cvtc_contract.py',
    'tools/kb/src/kb/exhaust_cvtc_matrix.py','tools/kb/src/kb/exhaust_cvtc_semantics.py',
    'tools/kb/src/kb/exhaust_cvtc_transfers.py',
    'tools/kb/src/kb/exhaust_cvtc_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/test_stock_capture.py','tools/kb/src/kb/width_view_matrix.py',contract.DESCRIPTOR,
    'tools/kb/src/kb/cvtc_gain_output_contract.py','defs/JK08A.cvtc-gain-output.toml')


def sha(data):return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the CVTC original lacks an exact normalized natural root or real helper')
    from kb import exhaust_cvtc_access_contract as owning
    rows=owning.descriptor(model.root)['reference'];result=[]
    for row in rows:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None
                or function.meaning.key!=json.loads(row['original_claim_json'])['to']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (owning.native_type(row,'width'),owning.native_type(row,'signed')))):
            raise ValueError('the CVTC original changes its exact datum/root owner or retained native type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],function=function.key.key,
            function_meaning=function.meaning.key,original_claim_sha256=row['original_claim_sha256']))
    if len(result)!=11:raise ValueError('the CVTC original omits an exact original owning relation')
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),
        calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    return proof_adapter.header(declared['source']['adapter'],declared['cases'],
        lambda case: matrix.context(declared['source'],case),
        lambda case: matrix.calibrations(declared['source'],image,case))





def observations(packet,declared):
    return proof_transport.decode(packet,declared,declared['source']['adapter'])


def require_state(declared,image,case,observed,root):
    matrix.require_input(declared['source'],image,case,observed)
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=observed['context'][19].to_bytes(4,'big');frame[164:168]=observed['context'][7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the bank2 CVTC original changes a complete incoming frame, SP or external ABI')
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    bound=b''.join(fixture[at:at+size] for at,size in declared['bound_spans'])
    if observed['bound_before']!=bound or observed['bound_after']!=bound:
        raise ValueError('the bank2 CVTC original changes a complete executable, pool, pointer or controlled constant span')
    result=state.execute(declared['source'],fixture,observed['context'],observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'],trace=case['entry']==0xC1DEC)
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    same(observed['exit'],expected,'the bank2 CVTC original disagrees with complete independent natural instruction state')
    if observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],):
        raise ValueError('the bank2 CVTC original disagrees with complete independent frame or RAM instruction effects')
    value=semantics.evaluate(case['entry'],observed['memory_before'][0],observed['calibration_before'],observed['context'])
    transfers.require(observed,result,value,fixture)
    require_premises(result,value)
    require_gain_transfer(observed,result,value)
    return result,value


def require_gain_transfer(observed,result,value):
    if value['entry']!=0xC1DEC:return
    curve=value['curve'];trace=result.get('trace')
    if type(trace) is not list:raise ValueError('the CVTC result lacks its exact real return-to-store instruction states')
    returned=[row for row in trace if row['site']==0xC1ED8]
    stored=[row for row in trace if row['site']==0xC1EE2]
    if curve is None:
        if returned or stored or observed['memory_after'][0][0x143A]!=observed['memory_before'][0][0x143A]:
            raise ValueError('the inactive CVTC path fabricates a helper return or gain publication')
        return
    if len(returned)!=1 or len(stored)!=1:
        raise ValueError('the CVTC result omits or repeats its exact real return and publication')
    first,last=returned[0],stored[0];gain=curve['value']
    if first['before']['registers'][0]!=gain or first['after']['registers'][6]!=gain:
        raise ValueError('the CVTC result changes the actual helper R0 and its byte-extension carrier')
    if (first['before']['registers'][15]!=observed['sp']-40
            or first['before']['pr']!=0xC1ED8 or first['before']['gbr']!=observed['context'][15]
            or last['before']['registers'][6]!=gain
            or observed['memory_after'][0][0x143A]!=gain):
        raise ValueError('the CVTC result changes the real return phase, complete caller state or actual143A byte')
    expected=dict(site=0xC1EE2,mode='write',address=0x0100143A,width_bytes=1,register=6,
        domain='ram',bytes=bytes((gain,)).hex())
    if not test_contract.exact(last['accesses'],[expected]):
        raise ValueError('the CVTC result changes its exact byte publication site, width, value or R6 carrier')


def require_gain_output(model,actual,values):
    from kb import cvtc_gain_output_contract as output
    from kb.diagnostic_rom_contract import plain
    row=output.descriptor(model.root)['reference'][0]
    symbol=model.symbols.get(SymbolKey('7mfk','ram',row['address']))
    function=model.symbols.get(SymbolKey('7mfk','fn',0x26474))
    if (symbol is None or symbol.meaning is None or symbol.meaning.key!=output.OWNER
            or function is None or function.meaning is None or function.meaning.key!=output.TARGET
            or symbol.value('width') is not None or symbol.value('signed') is not None
            or not test_contract.exact(plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
        raise ValueError('the CVTC result changes its exact native output/helper owner, unset type or L0/TEST origins')
    groups={'coordinate':{},'curve':{}}
    for observed,value in zip(actual,values):
        if value['entry']!=0xC1DEC or value['curve'] is None:continue
        for channel in groups:
            memory=bytearray(observed['memory_before'][0]);bound=bytearray(observed['bound_before'])
            calibration=dict(observed['calibration_before'])
            if channel=='coordinate':
                incoming=bytes((memory[0x2772],));memory[0x2772]=0
            else:
                incoming=calibration[0x1205A];calibration[0x1205A]=bytes(9);cursor=0
                for span in contract.BOUND_SPANS:
                    at,size=span['address'],span['size'];left,right=max(at,0x1205A),min(at+size,0x12063)
                    if left<right:bound[cursor+left-at:cursor+right-at]=bytes(right-left)
                    cursor+=size
            held=dict(memory=bytes(memory).hex(),context=list(observed['context']),frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                sr=observed['sr_before'],entry=observed['entry'],bound=bytes(bound).hex(),
                calibration={str(at):data.hex() for at,data in calibration.items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            groups[channel].setdefault(key,set()).add((incoming,observed['memory_after'][0][0x143A]))
    for channel,items in groups.items():
        if not any(len({item[0] for item in group})>=2 and len({item[1] for item in group})>=2 for group in items.values()):
            raise ValueError('the CVTC result lacks changed actual143A output with fixed-other '+channel+' inputs')


def require_premises(result,value):
    if any(first<=site<last for site in result['code'] for first,last in EXCLUDED_RANGES):
        raise ValueError('the CVTC proof enters a zero-divisor or wide-divisor path excluded by its explicit inputs')
    counts={0x21CE4:len(value['quotients']),0x21CEA:len(value['quotients']),
        0x21F44:int('remainder_call' in value),0x21F4A:int('remainder_call' in value),
        0x26C7A:int(value['curve'] is not None and value['curve']['division'] is not None),
        0xC1EF0:int(value['curve'] is not None and bool(value['configuration']&8)),
        0xC1FEA:int(value['entry']==0xC1DEC)}
    for site,outcome in FIXED_BRANCHES.items():
        actual=[row['kind'] for row in result['branches'] if row['site']==site]
        if actual!=[outcome]*counts[site]:
            raise ValueError('the CVTC proof changes an exact bank2/divisor/clamp conditional consequence')


def require_positive_alternatives(actual,values,declared,rows):
    sources={
        (0xC1DEC,0xFFFF1AA8,'writer'):(0x1B1A,2,0x1AA8,4),
        (0xC2040,0xFFFF1AA8,'reader'):(0x1AA8,4,0x1C72,2),
        (0xC1DEC,0xFFFF1AAE,'reader'):(0x1AAE,2,0x1AA8,4),
        (0xC2040,0xFFFF1AAE,'writer'):(0x1AA8,4,0x1AAE,2),
        (0xC2040,0xFFFF1AB6,'reader'):(0x1AB6,2,0x1AAE,2),
        (0xC2040,0xFFFF1AB6,'writer'):(0x1AAE,2,0x1AB6,2),
        (0xC1DEC,0xFFFF1B1A,'reader'):(0x1B1A,2,0x1AA8,4),
        (0xC1DEC,0xFFFF1B1D,'reader'):(0x1B1D,1,0x1AA8,4),
        (0xC1DEC,0xFFFF1B1D,'writer'):(0x248B,1,0x1B1D,1),
        (0xC2040,0xFFFF1B1D,'reader'):(0x1B1D,1,0x1AAE,2),
        (0xC2040,0xFFFF1C72,'writer'):(0x1AA8,4,0x1C72,2)}
    for row in rows:
        source,width,target,target_width=sources[(row['function'],row['address'],row['direction'])];groups={}
        for observed,value in zip(actual,values):
            if observed['entry']!=row['function']:continue
            memory=bytearray(observed['memory_before'][0]);incoming=bytes(memory[source:source+width])
            memory[source:source+width]=bytes(width)
            held=dict(memory=bytes(memory).hex(),context=list(observed['context']),frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                sr=observed['sr_before'],entry=observed['entry'],bound=observed['bound_before'].hex(),
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
            output=observed['memory_after'][0][target:target+target_width]
            groups.setdefault(key,set()).add((incoming,output))
        if not any(len({item[0] for item in group})>=2 and len({item[1] for item in group})>=2
                for group in groups.values()):
            raise ValueError('a CVTC original lacks an exact real output change with all other complete inputs fixed')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','return_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the bank2 CVTC original changes its complete capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the bank2 CVTC raw packet grants its own admission')
    root=Path(model.root).resolve();proof_adapter.require_generated(root,contract.DESCRIPTOR);catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the bank2 CVTC original changes its exact owned image')
    declared=declaration(model,image);same(packet['declaration'],declared,'the bank2 CVTC original changes current exact source inputs')
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={HEADER,*names}:
        raise ValueError('the bank2 CVTC original omits a complete consumed source')
    for name in names:
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the bank2 CVTC original consumes another source snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the bank2 CVTC original changes its input-only compiled header')
    for path in (*SOURCE_FILES,'tools/sh-elf-run/exhaust_cvtc_capture.py',
            *proof_adapter.source_files(root,contract.DESCRIPTOR)):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('a bank2 CVTC independent input or consumer source is stale')
    reconstructed=dict(code=[dict(start=first,end=last,stock=image[first:last].hex(),reconstructed=image[first:last].hex())
        for first,last in contract.SPANS],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.UNIT['pools']])
    same(packet['reconstruction'],reconstructed,'the bank2 CVTC independent GNU reconstruction changes stock code or data')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    require_return_reconstruction(root,packet)
    same(packet['aliases'],aliases,'the bank2 CVTC fixture changes an exact existing native pointer alias')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the bank2 CVTC fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the bank2 CVTC original changes a complete terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the bank2 CVTC original changes its actual simulator invocation or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_exhaust_cvtc_base')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the bank2 CVTC original changes its pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:raise ValueError('the bank2 CVTC original executes another harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the bank2 CVTC original changes its compiler, complete sources or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the bank2 CVTC original changes its complete pinned GNU toolchain')
    for value in toolchain['binaries'].values():ignition_literal_evidence.require_hash(value)
    proof_adapter.require_source_inputs(root,contract.DESCRIPTOR,inputs)
    actual=observations(packet,declared);coverage={site:set() for site in REQUIRED_BRANCHES};values=[];seen=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,case,observed,root);values.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        seen.update((row['site'],row['mode'],row['address'],row['width_bytes']) for row in result['accesses'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the bank2 CVTC original omits a required feasible conditional outcome')
    from kb import exhaust_cvtc_access_contract as owning
    rows=owning.descriptor(root)['reference']
    for row in rows:
        if row['component']!='exhaust_cvtc_transition_paths':raise ValueError('the CVTC proof substitutes a raw component')
        address=0x01000000+(row['address']&65535) if row['address']>=0xFFFF0000 else row['address']
        if any((site,'read' if row['direction']=='reader' else 'write',address,row['width_bytes']) not in seen for site in row['sites']):
            raise ValueError('a bank2 CVTC root lacks its exact physical consumer site and native width')
    require_positive_alternatives(actual,values,declared,rows)
    require_gain_output(model,actual,values)
    return dict(region=REGION,observations=len(actual),image_sha256=sha(image),fixture_sha256=sha(fixture),
        elf_sha256=packet['elf_sha256'],stdout_sha256=packet['stdout_sha256'],native_bindings=native_bindings(model),
        exact_cvtc_accesses=True,exact_cvtc_gain_output=True,exact_input_premise=dict(contract.PREMISE),
        conditional_branch_outcomes={f'{site:08x}':sorted(outcomes) for site,outcomes in coverage.items()},
        native_geometry_inference=False,automatic_resolution=False,scale_admission=False,units_admission=False,
        sensor_producer_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_return_reconstruction(root,packet):
    same((packet['boundaries'],packet['return_reconstruction']),([],[]),
        'the bank2 CVTC original replaces a natural return with an outside-code return')


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('exhaust_cvtc_transition_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete primary omits its unique actual bank2 CVTC original')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the bank2 CVTC inputs change during independent consumption')
    return result
