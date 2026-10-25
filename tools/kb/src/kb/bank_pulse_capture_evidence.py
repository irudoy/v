"""Independent physical and full-state admission of natural bank pulse."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import bank_pulse_contract as contract,bank_pulse_matrix as matrix,bank_pulse_semantics as numeric
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-bank-pulse-paths'
PREFIX='kb-bank-pulse-observation '
HEADER='bank-pulse-cases.h'
HARNESS='harness-bank-pulse.c'
OBSERVER='stock_ignition_consumer_invoke.s'
INPUT=Path(matrix.INPUT_SOURCE).name
REQUIRED_BRANCHES=(0x4EAF8,0x4EB10,0x4EB1C,0x4EB2C,0x4EB50,0x4EB70,0x4EB90)
WATCHED={0x4EAE6,0x4EAF0,0x4EAF4,0x4EB04,0x4EB0C,0x4EB12,0x4EB22,
         0x4EB42,0x4EB5E,0x4EB60,0x4EB7A,0x4EB9A}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import bank_pulse_access_contract as owning
    if not {row['parent'] for row in contract.WINDOWS}<=set(model.functions.get('7mfk',())):
        raise ValueError('the bank pulse original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the bank pulse original changes an exact native field, parent or semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner'],parent=function.key.key))
    return result


def declaration(model,image):
    source=contract.descriptor(model.root);contract.require_image(source,image);native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=model.root)),calibration_spans=[[row['address'],row['size']] for row in contract.POOLS],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Explicit banked word inputs; no expected outputs or registers. */',
           '#define BANK_PULSE_REGION '+json.dumps(REGION),
           'static const struct path_case bank_pulse_cases[] = {']
    for case in declared['cases']:
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        fields=','.join(f'0x{case[key]:x}U' for key in ('entry',*matrix.FIELDS))
        lines.append('    {'+fields+',{{'+registers+'},'+tail+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the bank pulse original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the bank pulse original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the bank pulse original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the bank pulse original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the bank pulse original mutates its const input context')
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
    same(packet['observations'],actual,'the bank pulse packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_BANK_PULSE status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the bank pulse original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result):
    before=observed['memory_before'][0];bank=case['raw_r4']&255;shift=bank*2
    flag1=observed['calibration_before'][0x893D][0];flag2=observed['calibration_before'][0x8940][0]
    expected=numeric.evaluate(before,bank,flag1,flag2)
    if (observed['memory_after']!=(expected['memory'],) or result['calls']
            or tuple(result['registers'][index] for index in (0,1,2,4,5,6,7))
               !=(shift,shift,expected['output'],expected['trim'],expected['corrected'],0x690,matrix.RAM_BASE+0x191C)
            or result['sr']&1!=expected['exit_t']):
        raise ValueError('the bank pulse disagrees with its separate scalar, scratch, cap or complete RAM equations')
    wanted=[]
    def read(site,at):wanted.append((site,'read',0xFFFF0000+at,2,before[at:at+2].hex()))
    def flag(site,at,value):wanted.append((site,'read',at,1,bytes([value]).hex()))
    read(0x4EAE6,0x22DC+shift);read(0x4EAF0,0x2A24+shift);flag(0x4EAF4,0x893D,flag1)
    if flag1&2:read(0x4EB04,0x2302+shift)
    else:
        flag(0x4EB0C,0x8940,flag2)
        read(0x4EB12 if flag2&16 else 0x4EB22,expected['control_address'])
        if expected['include_l']:read(0x4EB42,0x2302+shift)
    read(0x4EB5E,0x18C0+shift);read(0x4EB60,0x2436)
    if expected['precursor']:read(0x4EB7A,0x2310+shift)
    wanted.append((0x4EB9A,'write',0xFFFF191C+shift,2,expected['output'].to_bytes(2,'big').hex()))
    actual=[]
    for row in result['accesses']:
        if row['domain']!='ram' and row['site'] not in WATCHED:continue
        address=row['address']
        if row['domain']=='ram':address=0xFFFF0000+address-matrix.RAM_BASE
        elif row['domain']!='rom':raise ValueError('the bank pulse leaves its exact RAM/ROM domain')
        actual.append((row['site'],row['mode'],address,row['width_bytes'],row['bytes']))
    same(actual,wanted,'the bank pulse changes an exact datum/site/width/direction/value or conditional read')
    return dict(index=case['index'],bank=bank,output=expected['output'],accesses=actual,
        include_l=expected['include_l'],precursor=expected['precursor'],trim=expected['trim'],
        exact_bank_pulse=True,native_geometry_inference=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the bank pulse original changes its complete incoming frame, SP or caller ABI')
    prepared=bytearray(fixture)
    for at,data in observed['calibration_before'].items():prepared[at:at+len(data)]=data
    result=state.execute(declared['source'],bytes(prepared),context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the bank pulse original disagrees with complete independent instruction-state equations')
    return result,semantic(case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the bank pulse original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the bank pulse packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the bank pulse original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the bank pulse original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,HEADER,INPUT}:
        raise ValueError('the bank pulse original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER,INPUT):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the bank pulse original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the bank pulse original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/bank_pulse_capture.py',
            'tools/kb/src/kb/bank_pulse_contract.py','tools/kb/src/kb/bank_pulse_matrix.py',
            'tools/kb/src/kb/bank_pulse_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
            'tools/kb/src/kb/width_view_matrix.py','tools/kb/src/kb/bank_pulse_semantics.py',contract.ARITHMETIC_SOURCE):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the bank pulse independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                    reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the bank pulse GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the bank pulse fixture changes its exact base-pointer alias')
    same(packet['boundaries'],list(contract.RETURNS),'the bank pulse fixture changes an exact observation return')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the bank pulse fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the bank pulse original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the bank pulse original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_bank_pulse_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the bank pulse original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the bank pulse original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the bank pulse original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the bank pulse original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES}
    groups={(bank,role):{} for bank in (0,1) for role in matrix.READER_FIELDS}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((row['site'],row['mode'],0xFFFF0000+row['address']-matrix.RAM_BASE,row['width_bytes'])
                         for row in result['accesses'] if row['domain']=='ram')
        for role in matrix.READER_FIELDS:
            at=dict(matrix.WORDS)[role]+value['bank']*2;width=2
            if not any(mode=='read' and address==0xFFFF0000+at and size==width
                       for site,mode,address,size,data in value['accesses']):continue
            memory=bytearray(observed['memory_before'][0]);incoming=bytes(memory[at:at+width]);memory[at:at+width]=bytes(width)
            held=dict(memory_sha256=sha(bytes(memory)),context=list(observed['context']),
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[value['bank'],role].setdefault(key,set()).add((incoming.hex(),value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the bank pulse omits a required conditional outcome')
    for alternatives in groups.values():
        if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2
                   for values in alternatives.values()):
            raise ValueError('a bank-pulse reader lacks positive output alternatives with every other input fixed')
    from kb import bank_pulse_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['component']!='bank_pulse_paths':continue
        mode='read' if row['direction']=='reader' else 'write'
        if not all((site,mode,row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a bank pulse owning relation lacks its positive exact physical transfer')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_bank_pulse=True,native_geometry_inference=False,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('bank_pulse_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique bank pulse component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the bank pulse inputs change during admission')
    return result
