"""Independent physical and numeric/full-state admission of byte-surface originals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import byte_surface_contract as contract, byte_surface_equations as state
from kb import byte_surface_matrix as matrix, byte_surface_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-byte-surface-paths'
PREFIX = 'kb-byte-surface-observation '
HEADER = 'byte-surface-path-cases.h'
HARNESS = 'harness-byte-surface-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
REQUIRED_BRANCHES = (0xBFDDA,0xBFDE0,0xBFE2E,0xBFE5A,0xBFE66,
    0x2694C,0x26950,0x26954,0x26978,0x26788,0x26796,0x267B2,0x26742,0x26C7A)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    result=[]
    for address,owner,size in ((0xB2FA,'meaty-guillemot/tbl',8),(0xB33A,'exhaust_cvtc_target/tbl',16)):
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the byte-surface native table has another exact owning identity or layout')
        for key,expected in (('rows',size),('cols',size),('storage','uint8'),('width',8)):
            value=symbol.value(key)
            if value is not None and not test_contract.exact(value,expected):
                raise ValueError('the byte-surface conditional geometry contradicts a current native table property')
        result.append(dict(symbol=symbol.key.key,meaning=owner,native_geometry_inference=False))
    for key,(start,end) in contract.ENTRIES.items():
        if start not in model.functions.get('7mfk',()):
            raise ValueError('the byte-surface closure entry lacks its current normalized function anchor')
    return result


def declaration(model,image):
    source=contract.descriptor(model.root)
    contract.require_image(source,image)
    native_bindings(model)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,ROM_to_DID_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    spans=declared['calibration_spans']
    tables={row['table'] for row in declared['source']['surface']}
    lines=['/* Exact entry/calibration inputs; independent consumers own outputs. */',
        '#define BYTE_SURFACE_REGION '+json.dumps(REGION),
        f'#define BYTE_SURFACE_CALIBRATION_BYTES {sum(size for start,size in spans)}U',
        'static const struct calibration_span byte_surface_calibrations[] = {']
    offset=0
    for start,size in spans:
        lines.append(f'    {{0x{start:x}U,{size}U,{offset}U,{int(start in tables)}U}},')
        offset+=size
    lines.extend(('};','static const uint8_t byte_surface_stock_calibrations[] = {'))
    for start,size in spans:
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[start:start+size])+',')
    lines.extend(('};','static const struct surface_case byte_surface_cases[] = {'))
    for case in declared['cases']:
        surface=next(row for row in declared['source']['surface'] if row['table']==case['table'])
        values=(matrix.KINDS.index(case['kind']),case['entry'],case['table'],surface['row_axis'],
            surface['col_axis'],surface['cols'],case['axis'],case['axis_max'],case['row'],case['col'],
            case['pattern'],case['configuration'],case['force'],case['correction'],case['row_index'],case['col_index'],
            case['row_fraction'],case['col_fraction'],case['first'],case['second'],case['divisor'],case['dividend'],
            case['variant'],case['sr'],case['bridge'],case['bridge_selected'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the byte-surface original repeats a raw observation JSON key')
        result[key]=value
    return result


def calibration(value,spans):
    raw=test_stock_abi.raw(value,sum(size for start,size in spans))
    result={}
    offset=0
    for start,size in spans:
        result[start]=raw[offset:offset+size]
        offset+=size
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the byte-surface original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation',
          'ram_before','ram_after','calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the byte-surface original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the byte-surface original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the byte-surface original mutates its const input context')
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
    same(packet['observations'],actual,'the byte-surface packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_BYTE_SURFACES status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the byte-surface original lacks its unique complete marker')
    return parsed


def _table_reads(result,start,size):
    return [row['address']-start for row in result['accesses']
            if row['domain']=='rom' and start<=row['address']<start+size and row['width_bytes']==1]


def semantic(declared,case,observed,result):
    source=declared['source']
    calibrations=observed['calibration_before']
    tables={row['table']:calibrations[row['table']] for row in source['surface']}
    axes={address:calibrations[address] for row in source['surface'] for address in (row['row_axis'],row['col_axis'])}
    selected=next(row for row in source['surface'] if row['table']==case['table'])
    context=observed['context']
    raw=observed['exit'][19]
    kind=case['kind']
    if kind=='caller':
        before,after=observed['memory_before'][0],observed['memory_after'][0]
        expected=numeric.caller(tables,axes,before[0x11AE],before[0x102C],before[0x2468],
            calibrations[0x8615][0],before[0x2466])
        if any(after[address&65535]!=value for address,value in expected['outputs'].items()):
            raise ValueError('the actual byte-surface caller disagrees with independent selection, correction or clamp equations')
        for row,key in zip(source['surface'],('first','main','correction')):
            wanted=expected[key]
            reads=_table_reads(result,row['table'],row['rows']*row['cols'])
            if reads!=(wanted['reads'] if wanted is not None else []):
                raise ValueError('the byte-surface caller uses another exact ROM cell or unexpected correction path')
        return dict(kind=kind,index=case['index'],selected_coordinate=expected['selected_coordinate'],
            outputs={f'{address:08x}':value for address,value in expected['outputs'].items()},
            unclamped=expected['unclamped'],
            lower_clamp=expected['lower_clamp'],upper_clamp=expected['upper_clamp'])
    if kind in ('wrapper','surface'):
        if kind=='wrapper':
            expected=numeric.surface(tables[selected['table']],axes[selected['row_axis']],axes[selected['col_axis']],
                context[7]&255,context[19]&255)
        else:
            expected=numeric.at(tables[selected['table']],selected['rows'],selected['cols'],
                context[0],context[2],context[1],context[3])
        if raw!=expected['raw'] or _table_reads(result,selected['table'],selected['rows']*selected['cols'])!=expected['reads']:
            raise ValueError('the actual byte-surface lookup changes its independent cell, fraction, sign-extension or numeric result')
        return dict(kind=kind,index=case['index'],table=selected['table'],result=expected)
    if kind=='axis':
        index,fraction=numeric.axis_position(calibrations[case['axis']],context[5])
        if (observed['exit'][15],observed['exit'][14])!=(index,fraction):
            raise ValueError('the actual byte-axis search changes its independent endpoint, knot or fraction')
        return dict(kind=kind,index=case['index'],position=index,fraction=fraction)
    if kind=='linear':
        expected=numeric.linear(context[0],context[2],context[3])
    elif kind=='divider':
        expected=0 if context[0]==0 else context[1]//context[0]
    else:
        raise ValueError('the byte-surface semantic consumer receives an undeclared numeric role')
    if raw!=expected:
        raise ValueError('the actual natural byte helper disagrees with its separate integer equation')
    return dict(kind=kind,index=case['index'],output=expected)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded)
            or observed['sp']!=(observed['abi_before'][10]-164)&0xFFFFFFFF
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI
            or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the byte-surface actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<row['address']+row['width_bytes'] and row['address']<start+len(data)
                       for row in declared['source']['pool'])):
            raise ValueError('a byte-surface calibration input changes tested instructions or PC-relative data')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after']!=result['frame'] or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual byte-surface complete state disagrees with independent natural instruction equations')
    return result,semantic(declared,case,observed,result)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256',
        'fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries','command','simulator',
        'stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the byte-surface original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the byte-surface raw packet grants its own admission')
    root=Path(model.root).resolve()
    catalog=repo.images(root)['JK08A']
    image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the byte-surface original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the byte-surface original changes current closure, scope or exact bounded inputs')
    source=Path(declared['source']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the byte-surface original omits a consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the byte-surface original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the byte-surface original changes a private entry/calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/byte_surface_capture.py',
                 'tools/kb/src/kb/byte_surface_contract.py','tools/kb/src/kb/byte_surface_matrix.py',
                 'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/byte_surface_semantics.py',
                 'tools/kb/src/kb/byte_surface_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the byte-surface producer or independent contract source is stale')
    spans=sorted((row['start'],row['end']) for row in declared['source']['entry'])
    pools=declared['source']['pool']
    reconstructed=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),reconstructed=image[start:end].hex())
        for start,end in spans],pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['width_bytes']].hex(),
        reconstructed=image[row['address']:row['address']+row['width_bytes']].hex()) for row in pools])
    same(packet['reconstruction'],reconstructed,'the byte-surface GNU reconstruction changes stock instructions or literals')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the byte-surface original changes an exact RAM pointer or the wrapping ROM offset')
    same(packet['boundaries'],[],'the byte-surface original replaces a natural return or stock helper')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the byte-surface fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the byte-surface actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the byte-surface original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_byte_surface_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the byte-surface original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the byte-surface original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the byte-surface original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the byte-surface original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    semantics=[]
    coverage={site:set() for site in REQUIRED_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,semantic_result=require_state(declared,image,fixture,case,observed)
        semantics.append(semantic_result)
        for branch in result['branches']:
            if branch['site'] in coverage:
                coverage[branch['site']].add(branch['kind'])
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the byte-surface original omits a required conditional branch outcome')
    caller_cases=[row for row in semantics if row['kind']=='caller']
    if ({(row['lower_clamp'],row['upper_clamp']) for row in caller_cases}
            != {(False,False),(True,False),(False,True)}
            or not {0,255}<={row['unclamped'] for row in caller_cases}):
        raise ValueError('the byte-surface original omits a correction clamp outcome or exact boundary')
    if {case['entry'] for case in declared['cases']}!={start for start,end in contract.ENTRIES.values()}:
        raise ValueError('the byte-surface original omits an exact natural caller/helper entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        native_geometry_inference=False,ROM_to_DID_dependency_inference=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('byte_surface_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact byte-surface marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the byte-surface inputs change during independent admission')
    return result
