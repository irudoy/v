"""Independent physical and numeric admission of the uptight-duck original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import uptight_duck_contract as contract, byte_surface_equations as state
from kb import uptight_duck_matrix as matrix, uptight_duck_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-uptight-duck-paths'
PREFIX = 'kb-uptight-duck-observation '
HEADER = 'uptight-duck-path-cases.h'
HARNESS = 'harness-uptight-duck-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0x21BD2,0x21CCA,0x26742,0x2698C,0x26990,0x26994,0x269B8,0xB78A4,0xB78B8)
TABLE = 0x15C80


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the uptight-duck path omits a current normalized function in its natural closure')
    for entry in contract.FUNCTIONS:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',entry))
        if symbol is None or symbol.meaning is None:
            raise ValueError('the uptight-duck path lacks a current normalized function owner')
        result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
    symbol=model.symbols.get(SymbolKey('7mfk','tbl',TABLE))
    if symbol is None or symbol.meaning is None or symbol.meaning.key!='blond-panther/tbl':
        raise ValueError('the uptight-duck path changes the 00015C80 owner')
    result.append(dict(symbol=symbol.key.key,meaning=symbol.meaning.key))
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
    lines=['/* Explicit uptight-duck inputs; independent consumers own numeric and state outputs. */',
        '#define UPTIGHT_DUCK_REGION '+json.dumps(REGION),
        'static const uint8_t uptight_duck_stock_calibrations[] = {']
    for start,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct path_case uptight_duck_cases[] = {'))
    for case in declared['cases']:
        values=(case['entry'],matrix.PATTERNS.index(case['pattern']),('stock','strict','high').index(case['axis']),
            case['coordinate'],case['dividend'],case['threshold'],matrix.PATTERNS.index(case['side']),
            case['variant'],case['sr'],matrix.fifth_word(case),matrix.prior3348(case))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the uptight-duck original repeats a raw observation JSON key')
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
        raise ValueError('the uptight-duck original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the uptight-duck original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=0,entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the uptight-duck original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the uptight-duck original mutates its const input context')
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
    same(packet['observations'],actual,'the uptight-duck packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_UPTIGHT_DUCK status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the uptight-duck original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result):
    expected=numeric.caller(observed['calibration_before'],observed['memory_before'][0],case['dividend'],case['coordinate'])
    if observed['memory_after']!=(expected['memory'],) or expected['fault']!=b'\xa5\xc3\xd2\xe1':
        raise ValueError('the uptight-duck RAM disagrees with the lookup or publication equations')
    calls=[row for row in result['calls'] if row['target']==0x21BBC]
    if (len(calls)!=1 or calls[0]['site']!=0xB7892 or calls[0]['entry']['registers'][0]!=contract.DIVISOR
            or calls[0]['entry']['registers'][1]!=case['dividend']):
        raise ValueError('the signed call lacks constant divisor 000F4240 and the incoming R4 dividend')
    reads=[row['address']-TABLE for row in result['accesses'] if row['domain']=='rom' and row['mode']=='read'
           and TABLE<=row['address']<TABLE+66 and row['width_bytes']==2]
    wanted=list(expected['third']['offsets'])
    if reads[-len(wanted):]!=wanted:
        raise ValueError('the 00015C80 lookup changes its exact physical word reads')
    if any(row['target'] not in contract.FUNCTIONS for row in result['calls']):
        raise ValueError('the uptight-duck path invokes an undeclared helper')
    return dict(index=case['index'],lookup=expected['third']['value'],chosen=expected['chosen'],
        dividend=case['dividend'],divisor=contract.DIVISOR,fault_preserved=True,
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
        raise ValueError('the uptight-duck actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('an uptight-duck calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual uptight-duck complete state disagrees with independent natural instruction equations')
    require_no_RAM3348_access(result)
    return result,semantic(case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the uptight-duck original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the uptight-duck raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the uptight-duck original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the uptight-duck original changes current closure or exact inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the uptight-duck original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the uptight-duck original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the uptight-duck original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/uptight_duck_capture.py','tools/kb/src/kb/uptight_duck_contract.py',
                 'tools/kb/src/kb/uptight_duck_matrix.py','tools/kb/src/kb/uptight_duck_semantics.py',
                 'tools/kb/src/kb/division_callees_semantics.py','tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/uptight_duck_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the uptight-duck producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in declared['source']['pool']])
    same(packet['reconstruction'],reconstructed,'the uptight-duck GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the uptight-duck original changes an exact RAM pointer')
    same(packet['boundaries'],[],'the uptight-duck original replaces a natural return')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the uptight-duck fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the uptight-duck actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or simulator['returncode']!=0 or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the uptight-duck original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_uptight_duck_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the uptight-duck original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the uptight-duck original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the uptight-duck original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the uptight-duck original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    coordinate_pairs=[];prior_pairs=[]
    semantics=[]; coverage={site:set() for site in REQUIRED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,row=require_state(declared,image,fixture,case,observed)
        semantics.append(row)
        if 'prior3348' in case:prior_pairs.append((observed,result))
        elif 'fifth_word' in case:coordinate_pairs.append((observed,result))
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the uptight-duck original omits a required conditional branch outcome')
    if not any(row['chosen']==1 for row in semantics) or not any(row['chosen']==row['lookup'] and row['lookup'] for row in semantics):
        raise ValueError('the uptight-duck original lacks both the constant publication and the lookup publication')
    groups={}
    for row,observed in zip(semantics,actual):
        held=dict(memory=observed['memory_before'][0].hex(),dividend=row['dividend'],
            calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items() if at!=TABLE})
        key=json.dumps(held,sort_keys=True,separators=(',',':'))
        groups.setdefault(key,set()).add((row['lookup'],row['dividend']))
    if not any(len({item[0] for item in outcomes})>=2 and len({item[1] for item in outcomes})==1 for outcomes in groups.values()):
        raise ValueError('the uptight-duck original lacks a curve change that leaves the signed dividend unchanged')
    require_coordinate_response(coordinate_pairs)
    require_prior3348_independence(prior_pairs)
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        exact_R5_coordinate_response=True,real_three_curve_R6_and_publications=True,
        no_selected_RAM3348_access=True,prior3348_complete_state_independence=True,
        lookup_is_not_the_signed_operand=True,native_geometry_inference=False,
        datum_identity_inference=False,automatic_resolution=False,natural_caller_reachability=False,
        hardware_qualification=False,native_relation_publication=False,scale_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('uptight_duck_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact uptight-duck marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the uptight-duck inputs change during independent admission')
    return result



def require_coordinate_response(pairs):
    groups={}
    calls_wanted=((0xB786C,0x15BF0),(0xB7876,0x15C40),(0xB7888,0x15C80))
    for observed,result in pairs:
        coordinate=observed['context'][5]
        if type(coordinate) is not int or not 0<=coordinate<=65535:
            raise ValueError('the uptight coordinate response changes the complete unsigned-word input')
        calls=[row for row in result['calls'] if row['target']==0x26524]
        same([(row['site'],row['target']) for row in calls],[(site,0x26524) for site,base in calls_wanted],
            'the uptight coordinate response omits or substitutes an actual natural curve call')
        for call,(site,base) in zip(calls,calls_wanted):
            registers=call['entry']['registers']
            same((registers[4],registers[5],registers[6]),(base,0x13CA8,coordinate),
                'the uptight coordinate response detaches a real post-delay R6 from its incoming R5')
        outputs=[]
        for address in (0x35A0,0x35B6):
            events=[event for event in result['accesses'] if event['mode']=='write'
                and event['address']<=matrix.RAM_BASE+address<event['address']+event['width_bytes']]
            if len(events)!=1:raise ValueError('the uptight coordinate response omits or duplicates a real word publication')
            event=events[0];register=({0xB78C0:7,0xB78C6:2} if address==0x35A0 else {0xB78BA:2}).get(event['site'])
            if register is None:raise ValueError('the uptight coordinate response changes a real publication site')
            actual=observed['memory_after'][0][address:address+2]
            same((event['address'],event['width_bytes'],event['register'],event['domain'],event['bytes']),
                (matrix.RAM_BASE+address,2,register,'ram',actual.hex()),
                'the uptight coordinate response substitutes a byte lane, register or actual word value')
            outputs.append(actual)
        context=list(observed['context']);context[5]=0
        held=dict(context=context,memory=sha(observed['memory_before'][0]),
            frame=sha(observed['frame_before']),sp=observed['sp'],continuation=observed['continuation'],
            abi=observed['abi_before'],sr_before=observed['sr_before'],entry=observed['entry'],
            calibration={str(at):sha(raw) for at,raw in observed['calibration_before'].items()})
        key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
        group=groups.setdefault(key,{})
        if coordinate in group:same(group[coordinate],tuple(outputs),'one complete coordinate input changes its actual outputs')
        group[coordinate]=tuple(outputs)
    required={0,1,99,100,101,149,150,151,1599,1600,1601,3099,3100,3101,
        32767,32768,65534,65535,*range(0,3101,100),*range(50,3100,100)}
    admitted=False
    for group in groups.values():
        if not required<=group.keys():continue
        if any(any(group[index*100][column]==group[index*100+50][column] for column in range(2)) for index in range(31)):
            raise ValueError('the uptight coordinate response lacks changed actual outputs in a real axis interval')
        if any(group[coordinate]!=group[3100] for coordinate in (3101,32767,32768,65534,65535) if coordinate in group):
            raise ValueError('the uptight coordinate response changes an actual endpoint publication')
        admitted=True
    if not admitted:raise ValueError('the uptight coordinate response lacks the complete fixed-other word and knot domain')
    return True


def require_no_RAM3348_access(result):
    for event in result['accesses']:
        address,width=event['address'],event['width_bytes']
        if (type(address) is not int or not 0<=address<=0xFFFFFFFF
                or type(width) is not int or width not in (1,2,4)
                or event['mode'] not in ('read','write')):
            raise ValueError('the uptight RAM3348 absence guard changes a typed physical access')
        if any(address<base+4 and base<address+width for base in (0xFFFF3348,matrix.RAM_BASE+0x3348)):
            raise ValueError('the complete uptight callee physically accesses the selected RAM3348 bytes')
    return True


def require_prior3348_independence(pairs):
    groups={}
    required={0,0xFFFFFFFF,0xA5C3D2E1,0x7FFF,0x8000,0xFFFF,0x10000,0x7FFFFFFF,
        *(1<<bit for bit in range(32)),*((1<<bit)^0xFFFFFFFF for bit in range(32))}
    for observed,result in pairs:
        require_no_RAM3348_access(result)
        before=observed['memory_before'][0];after=observed['memory_after'][0]
        same(after[0x3348:0x334C],before[0x3348:0x334C],
            'the uptight callee changes any of the four unread prior RAM3348 bytes')
        prior=int.from_bytes(before[0x3348:0x334C],'big')
        held=dict(context=observed['context'],memory=sha(before[:0x3348]+bytes(4)+before[0x334C:]),
            frame=sha(observed['frame_before']),sp=observed['sp'],continuation=observed['continuation'],
            abi=observed['abi_before'],sr_before=observed['sr_before'],entry=observed['entry'],
            calibration={str(at):sha(raw) for at,raw in observed['calibration_before'].items()})
        key=sha(json.dumps(held,sort_keys=True,separators=(',',':')).encode())
        modes=tuple(next(row['kind'] for row in result['branches'] if row['site']==site)
            for site in (0xB78A4,0xB78B8))
        output=dict(exit=observed['exit'],frame=sha(observed['frame_after']),abi=observed['abi_after'],
            memory=sha(after[:0x3348]+bytes(4)+after[0x334C:]),
            calibration={str(at):sha(raw) for at,raw in observed['calibration_after'].items()},
            calls=result['calls'],branches=result['branches'],accesses=result['accesses'])
        group=groups.setdefault(key,{})
        if prior in group:raise ValueError('the uptight prior RAM3348 domain repeats one complete held-other input')
        group[prior]=(modes,output)
    seen=set()
    for group in groups.values():
        if not required<=group.keys():
            raise ValueError('the uptight prior RAM3348 contrast omits a bit, complement or boundary with other inputs fixed')
        reference=group[0]
        for value in group.values():
            same(value,reference,'the uptight result or physical path depends on unread prior RAM3348 bytes')
        seen.add(reference[0])
    if seen!={(first,second) for first in ('taken','fallthrough') for second in ('taken','fallthrough')}:
        raise ValueError('the uptight prior RAM3348 contrast omits a real publication-branch combination')
    return True
