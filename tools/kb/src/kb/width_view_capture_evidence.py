"""Independent physical and full-state admission of bounded width-view captures."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, test_contract, test_stock_abi, repo
from kb import width_view_evidence as contract, width_view_matrix as matrix

REGION = 'jk08a-width-views'
PREFIX = 'kb-width-view-observation '
HEADER = 'width-view-cases.h'
HARNESS = 'harness-width-views.c'
OBSERVER = 'stock_width_view_invoke.s'
BOUNDARY = bytes.fromhex('57f6472a000b0009')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def declaration(model):
    declared=contract.descriptor(model.root)
    contract.bind_fields(model,declared)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((Path(model.root)/contract.DESCRIPTOR).read_bytes()),
        windows=declared['window'],fields=declared['field'],image=declared['image'],
        cases=[dict(window=index,case=case) for index,window in enumerate(declared['window'])
               for case in matrix.cases(window)],semantic_width_inference=False,
        natural_entry_inference=False,selector_range_inference=False,
        automatic_resolution=False,hardware_qualification=False,semantic_admission=False)


def header(declared):
    lines=['/* Exact bounded inputs; independent consumers own semantic outputs. */',
           '#define WIDTH_VIEW_REGION '+json.dumps(REGION),
           f'#define WIDTH_VIEW_WINDOWS {len(declared["windows"])}U',
           'static const struct width_case width_cases[] = {']
    for row in declared['cases']:
        case=row['case']
        window=declared['windows'][row['window']]
        values=(row['window'],case['index'],case['entry'],case['pattern'],case['selector'],
                case['variant'],case['sr'],contract.alias(window['gbr']),
                int(window['key']=='4544-write-b'),int(window['key']=='2142-indexed-store'),
                2 if window['key']=='2142-byte-counter' else int(case['entry']==0x3CEBE))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the width-view original repeats a raw observation JSON key')
        result[key]=value
    return result


def observations(packet,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in packet['stdout'].splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the width-view original omits or duplicates a complete raw invocation')
    keys={'schema','index','window','case','context','context_after','observation','ram_before','ram_after'}
    parsed=[]
    for index,(row,wanted) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the width-view original changes its complete raw observation schema')
        identity=dict(schema=1,index=index,window=wanted['window'],case=wanted['case']['index'])
        same({key:row[key] for key in identity},identity,'the width-view original changes typed case identity or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the width-view original mutates its const input context')
        out=test_stock_abi.raw(row['observation'],572)
        parsed.append(dict(index=index,entry=wanted['case']['entry'],context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]),sp=int.from_bytes(out[80:84],'big'),
            continuation=int.from_bytes(out[84:88],'big'),
            abi_before=test_stock_abi.words(out[88:136]),abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376],frame_after=out[376:568],sr_before=int.from_bytes(out[568:572],'big'),
            memory_before=(matrix.decode_rle(row['ram_before']),),memory_after=(matrix.decode_rle(row['ram_after']),)))
    same(packet['observations'],actual,'the width-view packet differs from its actual raw stdout')
    marker=(f'VQ_SH_ELF_WIDTH_VIEWS status=PASS region={REGION} cases={len(parsed)} '
            f'windows={len(declared["windows"])}')
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the width-view original lacks its unique complete marker')
    return parsed


def require_witness(model,packet,inputs):
    required={'schema','declaration','semantic_admission','consumed','reconstruction',
        'image_sha256','fixture_sha256','elf_sha256','observer_object_sha256','aliases','boundaries',
        'command','simulator','stdout','stderr','stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=required:
        raise ValueError('the width-view original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the width-view packet grants its own admission')
    declared=declaration(model)
    same(packet['declaration'],declared,'the width-view packet changes native claims, entries or explicit inputs')
    root=Path(model.root).resolve()
    entry=repo.images(root)['JK08A']
    image=entry.path.read_bytes()
    if sha(image)!=entry.sha256 or packet['image_sha256']!=sha(image) or declared['image']['sha256']!=sha(image):
        raise ValueError('the width-view original changes its exact owned stock image')
    source=Path(declared['image']['assembly']).name
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,source,HEADER}:
        raise ValueError('the width-view original omits a private consumed executable input')
    for name in (HARNESS,OBSERVER,source):
        path='tools/sh-elf-run/'+name
        data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the width-view original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared).hex():
        raise ValueError('the width-view private header changes an entry, byte, selector or stack input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/width_view_capture.py',
                 'tools/kb/src/kb/width_view_evidence.py','tools/kb/src/kb/width_view_matrix.py',
                 'tools/kb/src/kb/width_view_capture_evidence.py','tools/kb/src/kb/packed_transfer_evidence.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the width-view producer or independent contract source is stale')
    spans=sorted({span for row in declared['windows'] for span in contract.spans(row)})
    pools=set()
    for start,end in spans:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word >> 12 in (9,13):
                width=4 if word >> 12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                pools.add((address,width))
    pools=sorted(pools)
    reconstruction=dict(code=[dict(start=start,end=end,stock=image[start:end].hex(),
        reconstructed=image[start:end].hex()) for start,end in spans],pools=[dict(address=address,
        stock=image[address:address+size].hex(),reconstructed=image[address:address+size].hex()) for address,size in pools])
    same(packet['reconstruction'],reconstruction,'the width-view GNU reconstruction changes exact stock instructions or pools')
    aliases=[]
    fixture=bytearray(image)
    for address,size in pools:
        original=int.from_bytes(image[address:address+size],'big')
        if size==4 and original>=0xFFFF0000:
            relocated=contract.alias(original)
            fixture[address:address+4]=relocated.to_bytes(4,'big')
            aliases.append(dict(address=address,original=original,alias=relocated))
    boundaries=[dict(address=row['end'],bytes=BOUNDARY.hex()) for row in declared['windows']]
    for row in boundaries:
        address=row['address']
        if (any(address<end and start<address+len(BOUNDARY) for start,end in spans)
                or any(address<pool+size and pool<address+len(BOUNDARY) for pool,size in pools)):
            raise ValueError('a width-view boundary changes tested stock instructions or data')
        fixture[address:address+len(BOUNDARY)]=BOUNDARY
    same(packet['aliases'],aliases,'the width-view original changes its RAM bank, byte lane or pool relocation')
    same(packet['boundaries'],boundaries,'the width-view original changes its observation boundary')
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the width-view fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):
        ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the width-view actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'returncode','command','timeout_seconds'}
            or type(simulator['returncode']) is not int or simulator['returncode']!=0
            or type(simulator['timeout_seconds']) is not int or simulator['timeout_seconds']!=1200
            or type(simulator['command']) is not list or len(simulator['command'])!=3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the width-view simulator changes its actual terminal or command')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_width_view_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the width-view original names another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the width-view original executes another compiled harness')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',str(private),f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),
        str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the width-view original changes its compiled sources, observer or fixture')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or type(toolchain['binaries']) is not dict or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the width-view original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():
        ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared)
    witnessed={}
    counter=[]
    for row,observed in zip(declared['cases'],actual):
        window=declared['windows'][row['window']]
        matrix.require_input(window,row['case'],observed)
        result=contract.require_observation(window,image,observed)
        if window['key']=='2142-byte-counter':
            before,after=observed['memory_before'][0],observed['memory_after'][0]
            active=observed['context'][0]!=0
            count=before[0x2142]
            expected=min(255,count+int(active))
            if after[0x2142]!=expected or after[0x2143]!=before[0x2143]:
                raise ValueError('the width-view byte counter changes its unsigned saturation or independent neighbor')
            count_accesses=[row for row in result['accesses'] if row['address']==contract.alias(0xFFFF2142)]
            if (active and [(row['site'],row['mode'],row['width_bytes']) for row in count_accesses]
                    != [(0x4A368,'read',1),(0x4A384,'write',1)] or not active and count_accesses):
                raise ValueError('the width-view counter changes its actual byte accesses or clear-branch preservation')
            counter.append(dict(input=count,active=active,output=expected))
        for access in result['accesses']:
            witnessed.setdefault(access['site'],[]).append(access)
    support={}
    if {(row['input'],row['active']) for row in counter}!={(value,active) for value in range(256) for active in (False,True)}:
        raise ValueError('the width-view original omits a byte counter value or an admitted predicate outcome')
    for field in declared['fields']:
        rows=[]
        for observed in field['observed']:
            mode='read' if observed['mode'] in ('load','read') else 'write'
            matching=[row for row in witnessed.get(observed['site'],())
                      if row['mode']==mode and row['width_bytes']==observed['width_bytes']]
            if not matching:
                raise ValueError('the width-view original omits a retained exact wider instruction')
            if field['kind']=='diagnostic-byte-view':
                address=contract.alias(field['diagnostic']['address'])
                if any(row['address']!=address for row in matching):
                    raise ValueError('the width-view original changes a constant working-state address')
            elif any(row['address']<contract.alias(0xFFFF2142) or row['address']>contract.alias(0xFFFF2142)+510
                     or (row['address']-contract.alias(0xFFFF2142))&1 for row in matching):
                raise ValueError('the width-view indexed observation exceeds its explicit bounded input matrix')
            rows.append(dict(function=observed['function'],site=observed['site'],mode=observed['mode'],
                physical_width_bytes=observed['width_bytes'],addresses=sorted({row['address'] for row in matching})))
        support[field['symbol']]=rows
    return dict(region=REGION,fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),fields=support,byte_counter=counter,
        semantic_width_inference=False,natural_entry_inference=False,selector_range_inference=False,
        automatic_resolution=False,hardware_qualification=False)


def require_primary(model,record):
    """Require the exact existing original primary, without an extra receipt."""
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('width_views')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its exact unique width-view marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the width-view execution inputs change during independent consumption')
    return result


def diagnostic_views(model,record):
    """Bind exact byte bindings after the caller admits the complete SID22 original.

    This structural mapping is insufficient as an execution verdict. The common
    Primary requires full independent SID22 validation and the same original
    process/native snapshot before exposing it with the bounded state proof.
    """
    from kb import sid22_evidence
    from kb.model import SymbolKey
    descriptor=sid22_evidence.descriptor(model.root)
    if record['candidate']['scope']!=sid22_evidence.scope_digest(model):
        raise ValueError('the diagnostic byte view changes its independently admitted native scope')
    result={}
    for field in contract.descriptor(model.root)['field']:
        if field['kind']!='diagnostic-byte-view':
            continue
        view=field['diagnostic']
        symbol=model.symbols.get(SymbolKey('7mfk','ram',view['address']))
        member=sid22_evidence._member(model,symbol,descriptor)
        bindings=[row for row in descriptor.bindings if row.member==member.meaning and row.did==view['did']]
        if (member.meaning!=field['meaning'] or member.declared_width!=field['declared_bits']
                or len(bindings)!=1 or bindings[0].record!=view['record']
                or bindings[0].read_addresses!=(view['address'],) or view['width_bytes']!=1):
            raise ValueError('the diagnostic width view changes its exact DID, pointer slot, byte address or declared member')
        result[field['symbol']]=dict(did=view['did'],record=view['record'],read_addresses=[view['address']],
            response_bytes=1,declared_bits=field['declared_bits'],semantic_storage_width_inference=False,
            underlying_producer_range_inference=False)
    return result
