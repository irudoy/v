"""Independent physical and full-state admission of natural phase normalization."""

import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state,ignition_literal_evidence,packed_transfer_evidence,repo
from kb import phase_normalization_contract as contract,phase_normalization_matrix as matrix
from kb import phase_split_semantics as split
from kb import test_contract,test_stock_abi,width_view_matrix
from kb.model import SymbolKey

REGION='jk08a-phase-normalization-paths'
PREFIX='kb-phase-normalization-observation '
HEADER='phase-normalization-cases.h'
HARNESS='harness-phase-normalization.c'
OBSERVER='stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES=(0x28DD6,0x28DDE,0x28DE4,0x28DEA,0x28DEE,0x28DF6,0x28DFC,0x28E12,
                   0x28E1C,0x28E22,0x28E2E,0x28E38,0x28E44,0x28E4A,0x28E58,0x28E5C,0x28E92)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):raise ValueError(reason)


def native_bindings(model):
    from kb import phase_access_contract as owning
    if not {row['parent'] for row in contract.WINDOWS}<=set(model.functions.get('7mfk',())):
        raise ValueError('the phase normalization original lacks a current normalized parent function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        function=model.symbols.get(SymbolKey('7mfk','fn',row['function']))
        old=json.loads(row['original_claim_json'])
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or function is None or function.meaning is None or function.meaning.key!=old['to']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the phase normalization original changes an exact native field, parent or semantic type')
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
    lines=['/* Explicit native pointer pairs and scalar inputs; no expected outputs. */',
           '#define PHASE_NORMALIZATION_REGION '+json.dumps(REGION),
           'static const struct path_case phase_normalization_cases[] = {']
    for case in declared['cases']:
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        fields=','.join(f'0x{case[key]:x}U' for key in ('entry','word','byte','count','remainder','phase'))
        lines.append('    {'+fields+',{{'+registers+'},'+tail+'}},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the phase normalization original repeats a raw JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):raise ValueError('the phase normalization original omits or duplicates an invocation')
    parsed=[]
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:raise ValueError('the phase normalization original changes its complete raw schema')
        wanted=dict(schema=1,index=index,kind=int(case['entry']==0x28E7C),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the phase normalization original changes typed invocation identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the phase normalization original mutates its const input context')
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
    same(packet['observations'],actual,'the phase normalization packet differs from the actual original stdout')
    marker=f'VQ_SH_ELF_PHASE_NORMALIZATION status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the phase normalization original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,numeric):
    if case['entry']==0x28E7C:return split.evaluate(case,observed,result)
    before=observed['memory_before'][0];word=case['word']&65535;byte=case['byte']&65535
    incoming=int.from_bytes(before[word:word+2],'big');remainder=before[byte];phase=before[0x13B2]
    count,residue,r0,r2,r5,exit_t=numeric.normalized(incoming,remainder,phase)
    memory=bytearray(before);memory[word:word+2]=count.to_bytes(2,'big');memory[byte]=residue
    if (observed['memory_after']!=(bytes(memory),) or result['calls']
            or (result['registers'][0],result['registers'][2],result['registers'][5],result['registers'][7],result['sr']&1)
               !=(r0,r2,r5,matrix.RAM_BASE+byte,exit_t)):
        raise ValueError('the phase normalizer disagrees with the separate existing integer and scratch-state equations')
    wanted=[(0x28DCE,'read',matrix.RAM_BASE+0x13B2,1,bytes([phase]).hex()),
            (0x28DD0,'read',matrix.RAM_BASE+word,2,before[word:word+2].hex())]
    def transfer(site,mode,offset,width,data):
        wanted.append((site,mode,matrix.RAM_BASE+offset,width,data.hex()))
    if phase==9 and incoming==9:
        transfer(0x28E02,'write',word,2,bytes.fromhex('0008'))
        transfer(0x28E04,'read',byte,1,bytes([remainder]))
        transfer(0x28E08,'write',byte,1,bytes([residue]))
        transfer(0x28E0A,'read',word,2,bytes.fromhex('0008'))
    else:
        word_site=None;byte_read=None
        if phase==4:
            if 6<=incoming<=15:word_site=0x28E52
            elif incoming==5:word_site,byte_read=0x28E6E,0x28E70
            elif incoming==4:word_site,byte_read=0x28E62,0x28E64
        elif phase==9:
            if incoming>=10:word_site,byte_read=0x28E6E,0x28E70
        elif 15<=incoming<=24 or 3<=incoming<=12:word_site=0x28E52
        elif incoming in (2,14):word_site,byte_read=0x28E6E,0x28E70
        elif incoming in (1,13):word_site,byte_read=0x28E62,0x28E64
        if word_site is not None:transfer(word_site,'write',word,2,count.to_bytes(2,'big'))
        if byte_read is not None:
            transfer(byte_read,'read',byte,1,bytes([remainder]))
            transfer(0x28E76,'write',byte,1,bytes([residue]))
    actual=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes'])
            for row in result['accesses'] if row['domain']=='ram']
    if actual!=wanted:
        raise ValueError('the phase normalizer changes a physical pointer, site, width, direction, value or delay-slot transfer')
    return dict(index=case['index'],pair=case['pair'],count=count,remainder=residue,
        output=(count,residue),accesses=actual,exact_phase_normalization=True,
        native_geometry_inference=False,natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed,*,root=None):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(frame) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the phase normalization original changes its complete incoming frame, SP or caller ABI')
    result=state.execute(declared['source'],fixture,context,observed['memory_before'][0],bytes(frame),
        observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the phase normalization original disagrees with complete independent instruction-state equations')
    from kb.test_stock_capture import tool
    numeric=tool(repo.ROOT if root is None else root,Path(contract.NUMERIC).name,'_kb_phase_normalization_numeric')
    return result,semantic(case,observed,result,numeric)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
          'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
          'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:raise ValueError('the phase normalization original lacks its complete physical schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the phase normalization packet grants its own admission')
    root=Path(model.root).resolve();catalog=repo.images(root)['JK08A'];image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):raise ValueError('the phase normalization original changes its owned image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the phase normalization original changes an exact current window or input')
    source=Path(contract.ASSEMBLY).name
    if type(packet['consumed']) is not dict or set(packet['consumed'])!={source,HARNESS,OBSERVER,HEADER}:
        raise ValueError('the phase normalization original omits a consumed executable source')
    for name in (source,HARNESS,OBSERVER):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if packet['consumed'][name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the phase normalization original consumes another executable snapshot')
    if packet['consumed'][HEADER]!=header(declared,image).hex():raise ValueError('the phase normalization original changes an explicit private input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/phase_normalization_capture.py',
            'tools/kb/src/kb/phase_normalization_contract.py','tools/kb/src/kb/phase_normalization_matrix.py',
            'tools/kb/src/kb/phase_normalization_capture_evidence.py','tools/kb/src/kb/byte_surface_equations.py',
            'tools/kb/src/kb/phase_split_semantics.py',
            'tools/kb/src/kb/width_view_matrix.py',contract.NUMERIC):
        if inputs.get(path)!=sha((root/path).read_bytes()):raise ValueError('the phase normalization independent execution source is stale')
    reconstructed=dict(code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
        reconstructed=image[row['start']:row['end']].hex()) for row in contract.WINDOWS],
        pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                    reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in contract.POOLS])
    same(packet['reconstruction'],reconstructed,'the phase normalization GNU reconstruction changes stock instructions or descriptors')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the phase normalization fixture changes its exact base-pointer alias')
    same(packet['boundaries'],list(contract.RETURNS),'the phase normalization fixture changes an exact observation return')
    if packet['fixture_sha256']!=sha(fixture):raise ValueError('the phase normalization fixture changes an undeclared byte')
    for key in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[key])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the phase normalization original changes a terminal stream')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the phase normalization original changes its actual simulator or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_phase_normalization_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the phase normalization original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the phase normalization original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the phase normalization original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3'
            or toolchain.get('gcc_version')!='13.3.0' or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the phase normalization original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[];transfers=set()
    coverage={site:set() for site in REQUIRED_BRANCHES};split_groups={pair:{} for pair in range(len(contract.PAIRS))}
    groups={(pair,role):{} for pair in range(len(contract.PAIRS)) for role in ('word','byte')}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed,root=root);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
        transfers.update((row['site'],row['mode'],0xFFFF0000+row['address']-matrix.RAM_BASE,row['width_bytes'])
                         for row in result['accesses'] if row['domain']=='ram')
        if case['entry']==0x28E7C:
            context=list(observed['context']);argument=context[4];context[4]=0
            held=dict(memory=observed['memory_before'][0].hex(),context=context,
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            split_groups[case['pair']].setdefault(key,set()).add((argument,value['output']))
        for role,width in (('word',2),('byte',1)):
            at=case[role]&65535
            if not any(mode=='read' and address==matrix.RAM_BASE+at and size==width
                       for site,mode,address,size,data in value['accesses']):continue
            memory=bytearray(observed['memory_before'][0]);incoming=bytes(memory[at:at+width]);memory[at:at+width]=bytes(width)
            held=dict(memory=memory.hex(),context=list(observed['context']),
                calibration={str(at):data.hex() for at,data in observed['calibration_before'].items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[case['pair'],role].setdefault(key,set()).add((incoming.hex(),value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the phase normalizer omits a required conditional outcome')
    for alternatives in groups.values():
        if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2
                   for values in alternatives.values()):
            raise ValueError('a normalizer reader lacks positive output alternatives with every other input fixed')
    for alternatives in split_groups.values():
        for index in (0,1):
            if not any(len({value[0] for value in values})>=2 and len({value[1][index] for value in values})>=2
                       for values in alternatives.values()):
                raise ValueError('a splitter writer lacks positive R4 alternatives with every other input fixed')
    from kb import phase_access_contract as owning
    for row in owning.descriptor(root)['reference']:
        if row['component']!='phase_normalization_paths':continue
        mode='read' if row['direction']=='reader' else 'write'
        if not all((site,mode,row['address'],row['width_bytes']) in transfers for site in row['sites']):
            raise ValueError('a phase normalizer owning relation lacks its positive exact physical transfer')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,exact_phase_normalization=True,native_geometry_inference=False,
        conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('phase_normalization_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:raise ValueError('the complete original lacks its unique phase normalization component')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:raise ValueError('the phase normalization inputs change during admission')
    return result
