"""Independent complete original admission of bounded vehicle/main contributor accesses."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence,packed_transfer_evidence,repo,test_contract,test_stock_abi,width_view_matrix
from kb import rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import rpm_inhibit_semantics as numeric,rpm_inhibit_transfers as transfers,byte_surface_equations as state
from kb.model import SymbolKey

REGION='jk08a-rpm-inhibit-paths'
PREFIX='kb-rpm-inhibit-observation '
HEADER='rpm-inhibit-path-cases.h'
HARNESS='harness-rpm-inhibit-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
SOURCES=('stock_jk08a_rpm_inhibit_callers.s', 'stock_jk08a_vehicle_speed_fuel_cut.s', 'stock_jk08a_main_rpm_fuel_cut.s', 'stock_jk08a_rpm_summary_leaves.s', 'stock_jk08a_composite_rpm_inhibit.s', 'stock_jk08a_diagnostic_fault_sentinel.s', 'stock_jk08a_implicit_byte_curve.s', 'publication_inhibit_snapshot_return.s')
PARENTS={0x4ED88:'fuel_output_inhibit_coordinator/fn',0x4F19C:'vehicle_speed_fuel_cut_state_machine/fn',
    0x4F282:'main_rpm_fuel_cut_state_machine/fn',0x4F736:'dual_bank_maf_fault_rpm_inhibit/fn',
    0x4FAA0:'shared_status_bit1_fuel_inhibit/fn',0x507CE:'composite_status_rpm_inhibit/fn',
    0x259E4:'diagnostic_record_byte2_fault_predicate/fn'}
REQUIRED_BRANCHES=(0x4F1B0,0x4F1B6,0x4F1CA,0x4F24C,0x4F252,0x4F264,0x4F26A,
    0x4F292,0x4F298,0x4F2A2,0x4F2A8,0x4F2AE,0x4F2BE,0x4F2DC,0x4F2E4,0x4F2F0,0x4F2F6,0x4F308,
    0x4F73C,0x4F74C,0x50848,0x50852,0x50860,0x50866,0x5086C,0x5087E,
    0x508A0,0x508B6,0x508C4,0x508CA,0x508D0,0x26376,0x26742)
FIXED_BRANCHES={0x259EA:'taken',0x507F6:'fallthrough',0x50800:'taken',0x26A9A:'taken'}
UNREACHABLE_BRANCHES=(0x5080E,0x5081E,0x50838,0x259FA,0x25A06)



def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    from kb import rpm_inhibit_access_contract as owning
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the RPM contributor original lacks a normalized current parent or leaf function')
    result=[]
    for row in owning.descriptor(model.root)['reference']:
        symbol=model.symbols.get(owning.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact(symbol.value('width'),owning.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'),owning.native_type(row,'signed'))):
            raise ValueError('the RPM contributor original changes an exact native owner or retained semantic type')
        result.append(dict(symbol=symbol.key.key,meaning=row['owner']))
    for address,owner in PARENTS.items():
        symbol=model.symbols.get(SymbolKey('7mfk','fn',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the RPM contributor original changes its exact real caller or leaf owner')
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
    lines=['/* Explicit bounded contributor path inputs; no expected outputs. */',
        '#define RPM_INHIBIT_REGION '+json.dumps(REGION),
        'static const uint8_t rpm_inhibit_stock_calibrations[] = {']
    for at,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[at:at+size])+',')
    lines.extend(('};','static const struct path_case rpm_inhibit_cases[] = {'))
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the rpm-inhibit original repeats a raw observation JSON key')
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
        raise ValueError('the rpm-inhibit original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the rpm-inhibit original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the rpm-inhibit original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the rpm-inhibit original mutates its const input context')
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
    same(packet['observations'],actual,'the rpm-inhibit packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_RPM_INHIBIT status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the rpm-inhibit original lacks its unique complete marker')
    return parsed


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the rpm-inhibit actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<at+4 and at<start+len(data) for at in contract.ALIASES)):
            raise ValueError('a bounded RPM calibration input changes tested instructions or a pointer literal')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual rpm-inhibit complete state disagrees with independent natural instruction equations')
    if case['kind']=='contributors':
        value=numeric.compose(observed['memory_before'][0],observed['calibration_before'],context[0])
    elif case['kind']=='composite-status':
        value=numeric.composite(observed['memory_before'][0],observed['calibration_before'],context[0],context[2],context[14])
    else:value=numeric.summary(observed['memory_before'][0],case['kind'],context[0],context[2],context[14])
    transfers.require(observed,result,value,bytes(expected_fixture))
    if case['kind']=='composite-status':require_composite_branches(result)
    return result,value


def require_composite_branches(result):
    for site,outcome in FIXED_BRANCHES.items():
        actual=[row['kind'] for row in result['branches'] if row['site']==site]
        count=2 if site==0x259EA else 0 if site==0x26A9A and not any(
            row['site']==0x26378 for row in result['accesses']) else 1
        if actual!=[outcome]*count:
            raise ValueError('the bounded sentinel/byte-curve proof changes an exact feasible one-sided branch')
    if (any(row['site'] in UNREACHABLE_BRANCHES for row in result['branches'])
            or any(row['domain']=='ram' and row['address'] in (matrix.RAM_BASE+0x1038,matrix.RAM_BASE+0x4200)
                for row in result['accesses'])):
        raise ValueError('the bounded composite proof enters a branch excluded by its exact sentinel arguments')


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','stub_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the rpm-inhibit original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the rpm-inhibit raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the rpm-inhibit original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the rpm-inhibit original changes current closure or exact inputs')
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,HEADER,*SOURCES}:
        raise ValueError('the bounded RPM original omits an exact reused executable source')
    for name in (HARNESS,OBSERVER,*SOURCES):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the bounded RPM original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the rpm-inhibit original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/rpm_inhibit_capture.py','tools/kb/src/kb/rpm_inhibit_contract.py',
                 'tools/kb/src/kb/rpm_inhibit_matrix.py','tools/kb/src/kb/rpm_inhibit_semantics.py',
                 'tools/kb/src/kb/rpm_inhibit_transfers.py','tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/rpm_inhibit_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py',
                 'tools/kb/src/kb/apc_reset_offset_semantics.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the rpm-inhibit producer or independent contract source is stale')
    reconstructed=[]
    for unit in declared['source']['unit']:
        reconstructed.append(dict(unit=unit['id'],source=unit['assembly'],
            code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
                       reconstructed=image[row['start']:row['end']].hex()) for row in unit['code']],
            pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in unit['pools']]))
    same(packet['reconstruction'],reconstructed,'a bounded RPM GNU reconstruction changes stock code or literal spans')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the rpm-inhibit original changes an exact RAM pointer')
    same(packet['boundaries'],list(contract.BOUNDARIES),'the rpm-inhibit original changes its exact outside-code observing returns')
    stubs=packet['stub_reconstruction']
    if type(stubs) is not list or len(stubs)!=len(contract.BOUNDARIES):
        raise ValueError('the bounded RPM original omits a separately assembled observing return')
    for stub,boundary in zip(stubs,contract.BOUNDARIES):
        if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
            raise ValueError('the bounded RPM original changes its complete return reconstruction')
        same((stub['address'],stub['bytes'],stub['source_sha256']),
            (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
            'the bounded RPM observing return changes assembled bytes, address or private source')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the rpm-inhibit fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the rpm-inhibit actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the rpm-inhibit original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_rpm_inhibit_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the rpm-inhibit original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the rpm-inhibit original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the rpm-inhibit original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the rpm-inhibit original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[]
    from kb import rpm_inhibit_access_contract as owning
    rows=[row for row in owning.descriptor(root)['reference'] if row['component']=='rpm_inhibit_paths']
    groups={row['id']:{} for row in rows}
    coverage={site:set() for site in REQUIRED_BRANCHES};fixed={site:set() for site in FIXED_BRANCHES};seen=set()
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed)
        if case['kind']=='contributors':
            semantics.append(dict(index=case['index'],output=value['output'],prior=value['prior'],
                vehicle={key:item for key,item in value['vehicle'].items() if key!='memory'},
                main={key:item for key,item in value['main'].items() if key!='memory'}))
        else:semantics.append(dict(index=case['index'],**{key:item for key,item in value.items() if key!='memory'}))
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if case['kind']=='composite-status' and branch['site'] in fixed:fixed[branch['site']].add(branch['kind'])
        accesses={(entry['site'],entry['mode'],
            0xFFFF0000+entry['address']-matrix.RAM_BASE if entry['domain']=='ram' else entry['address'],
            entry['width_bytes']) for entry in result['accesses'] if entry['domain']!='frame'}
        seen.update(accesses)
        for row in rows:
            if not any((site,'read',row['address'],row['width_bytes']) in accesses for site in row['sites']):continue
            memory=bytearray(observed['memory_before'][0]);calibration={str(at):bytearray(data)
                for at,data in observed['calibration_before'].items()}
            if row['address']>=0xFFFF0000:
                offset=row['address']&65535;incoming=bytes(memory[offset:offset+row['width_bytes']])
                memory[offset:offset+row['width_bytes']]=bytes(row['width_bytes'])
            else:
                selected=[(at,data) for at,data in calibration.items()
                    if int(at)<=row['address'] and row['address']+row['width_bytes']<=int(at)+len(data)]
                if len(selected)!=1:raise ValueError('an RPM owning root lacks its exact calibration word')
                at,data=selected[0];offset=row['address']-int(at);incoming=bytes(data[offset:offset+row['width_bytes']])
                data[offset:offset+row['width_bytes']]=bytes(row['width_bytes'])
            held=dict(kind=case['kind'],entry=case['entry'],memory=memory.hex(),
                context=list(observed['context']),frame=observed['frame_before'].hex(),
                sp=observed['sp'],continuation=observed['continuation'],abi=list(observed['abi_before']),
                sr_before=observed['sr_before'],calibration={at:bytes(data).hex() for at,data in calibration.items()})
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[row['id']].setdefault(key,set()).add((incoming,value['output']))
    if any(values!={'taken','fallthrough'} for values in coverage.values()):
        raise ValueError('the RPM contributor original omits a required actual conditional branch outcome')
    if any(fixed[site]!={outcome} for site,outcome in FIXED_BRANCHES.items()):
        raise ValueError('the composite original omits an exact feasible sentinel/byte-curve branch')
    for row in rows:
        if not all((site,'read',row['address'],row['width_bytes']) in seen for site in row['sites']):
            raise ValueError('the RPM contributor original omits an exact positive owning root or state read')
        if not any(len({item[0] for item in values})>=2 and len({item[1] for item in values})>=2
                for values in groups[row['id']].values()):
            raise ValueError('an RPM owning input lacks output-pair variation with every other complete input fixed')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        fixed_branch_outcomes={f'{site:08x}':sorted(values) for site,values in fixed.items()},
        exact_bounded_rpm_inhibit_accesses=True,exact_summary_bit_accesses=True,exact_composite_status_accesses=True,
        native_geometry_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        full_coordinator_admission=False,stock_conditioned_pair_reachability=False,stock_shared_status_reachability=False,
        stock_composite_seed_reachability=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)



def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('rpm_inhibit_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact rpm-inhibit marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the rpm-inhibit inputs change during independent admission')
    return result
