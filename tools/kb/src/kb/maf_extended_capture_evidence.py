"""Independent physical and numeric admission of the maf-extended original."""

import hashlib
import json
from pathlib import Path

from kb import ignition_literal_evidence, packed_transfer_evidence, repo
from kb import test_contract, test_stock_abi, width_view_matrix
from kb import maf_extended_contract as contract, byte_surface_equations as state
from kb import maf_extended_matrix as matrix, maf_extended_semantics as numeric
from kb.model import SymbolKey

REGION = 'jk08a-maf-extended-paths'
PREFIX = 'kb-maf-extended-observation '
HEADER = 'maf-extended-path-cases.h'
HARNESS = 'harness-maf-extended-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
SOURCES = ('stock_jk08a_maf_compensation.s','stock_jk08a_maf_contribution.s','stock_jk08a_maf_scaling.s',
           'stock_jk08a_maf_bank_publication.s','stock_jk08a_maf_diagnostic_copy.s',
           'stock_jk08a_maf_callers.s','publication_inhibit_snapshot_return.s')
REQUIRED_BRANCHES = (0x3AEB4,0x3AEE4,0x3AEF4,0x3AF6E,0x3AF78,0x3AF8A,0x3AFAE,0x67192,0x671A6,0x671B0,0x3C434,0x671F8,0x3B244)
NATIVE_WORDS = ((4294905886, 'maf_b2/ram', 16, False), (4294909284, 'hairy-dalmatian/ram', 16, False), (4294909426, 'spiked-dalmatian/ram', 16, False), (4294909436, 'imposing-auk/ram', 32, True), (4294909442, 'maf_base_b2/ram', 16, False), (4294909450, 'maf_base_reference_b2/ram', 16, False), (4294909460, 'maf_fallback_reference_b2/ram', 32, False), (4294909466, 'maf_delta_reference_b2/ram', 16, False), (4294909470, 'maf_correction_state_b2/ram', 16, True), (4294909490, 'maf_residual_magnitude_b2/ram', 16, False), (4294909514, 'careful-penguin/ram', 16, False), (4294916508, 'unselfish-okapi/ram', 32, False), (4294919115, 'maf_fallback_latch_b2/ram', 8, False), (4294920560, 'satisfied-oarfish/ram', 16, False), (4294908480, 'camouflaged-cockle/ram', None, None), (4294905884, 'maf_b1/ram', 16, False))
PARENTS = {241290: 'enchanted-cricket/fn', 246792: 'outstanding-penguin/fn', 241474: 'mustard-squid/fn', 242212: 'artichoke-mantis/fn', 246876: 'active-snail/fn', 239876: 'dual_bank_maf_coordinator/fn', 246700: 'dual_bank_maf_diagnostic_coordinator/fn'}
CLAIM_SITES = {'compensation': {241344, 241412, 241324, 241456, 241362}, 'contribution': {241792, 241538, 241848, 242114, 242178, 241512, 241578, 241710, 241680, 242064, 242034, 242132, 242196, 241624, 241978, 241598}, 'scaling': {246816, 422368, 246828, 246864, 422298, 422332}, 'bank-publication': {242256, 242218, 242228, 242236}, 'diagnostic-copy': {246894, 246886}, 'compensation-caller': {241344, 241456, 241362, 241412, 241324}, 'scaling-caller': {246816, 422368, 246864, 422298, 246828, 422332}}
READERS = (('compensation', 4294905886, 2), ('compensation', 4294916508, 4), ('contribution', 4294909426, 2), ('contribution', 4294909450, 2), ('contribution', 4294909460, 4), ('contribution', 4294909466, 2), ('contribution', 4294909470, 2), ('contribution', 4294909490, 2), ('contribution', 4294919115, 1), ('scaling', 4294909284, 2), ('scaling', 4294920560, 2), ('bank-publication', 4294909436, 4), ('diagnostic-copy', 4294909284, 2), ('compensation-caller', 4294905884, 2), ('compensation-caller', 4294905886, 2))


BATTERY_BRANCHES = (0x67192,0x671A6,0x671B0,0x39AD8)
PARENTS[0x39A9E] = 'battery_voltage_publish/fn'
CLAIM_SITES['battery'] = {0x39AAE,0x39AB0,0x39AB8,0x6718A,0x6719A,0x671BC,0x39AC4,0x671E0,0x39AE2}
READERS += (('battery',0xFFFF4970,2),)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_bindings(model):
    if not set(contract.FUNCTIONS)<=set(model.functions.get('7mfk',())):
        raise ValueError('the extended MAF original omits a normalized function in its exact natural closure')
    result=[]
    for address,owner,width,signed in NATIVE_WORDS:
        symbol=model.symbols.get(SymbolKey('7mfk','ram',address))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=owner
                or not test_contract.exact(symbol.value('width'),width)
                or not test_contract.exact(symbol.value('signed'),signed)):
            raise ValueError('the extended MAF original changes a declared native owner, width or signedness')
        result.append(dict(symbol=symbol.key.key,meaning=owner))
    for address,owner in PARENTS.items():
        symbol=model.symbols.get(SymbolKey('7mfk','fn',address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the extended MAF original changes an exact natural parent owner')
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
    lines=['/* Explicit natural MAF path inputs; no expected outputs. */',
        '#define MAF_EXTENDED_REGION '+json.dumps(REGION),
        'static const uint8_t maf_extended_stock_calibrations[] = {']
    for at,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[at:at+size])+',')
    lines.extend(('};','static const struct path_case maf_extended_cases[] = {'))
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the maf-extended original repeats a raw observation JSON key')
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
        raise ValueError('the maf-extended original omits or duplicates a real invocation')
    keys={'schema','index','kind','entry','context','context_after','observation','ram_before','ram_after',
          'calibration_before','calibration_after'}
    parsed=[]
    for index,(row,case) in enumerate(zip(actual,declared['cases'])):
        if type(row) is not dict or set(row)!=keys:
            raise ValueError('the maf-extended original changes its complete raw observation schema')
        wanted=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        same({key:row[key] for key in wanted},wanted,'the maf-extended original changes typed invocation role or order')
        context=test_stock_abi.raw(row['context'],80)
        if test_stock_abi.raw(row['context_after'],80)!=context:
            raise ValueError('the maf-extended original mutates its const input context')
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
    same(packet['observations'],actual,'the maf-extended packet differs from its actual original stdout')
    marker=f'VQ_SH_ELF_MAF_EXTENDED status=PASS region={REGION} cases={len(parsed)}'
    if packet['stdout'].splitlines().count(marker)!=1 or packet['marker']!=marker:
        raise ValueError('the maf-extended original lacks its unique complete marker')
    return parsed


def semantic(case,observed,result,image):
    before=observed['memory_before'][0];cal=observed['calibration_before'];kind=case['kind']
    if kind=='compensation':
        expected=numeric.compensation(case['argument'],before,int.from_bytes(cal[0x9586],'big'),int.from_bytes(cal[0x958C],'big'))
    elif kind=='contribution':
        expected=numeric.contribution(case['argument'],before,cal[0x82B6],cal[0x82BD][0],cal[0x8AC3][0])
    elif kind=='scaling':
        expected=numeric.scaling(case['argument'],before,cal[0x87F8],int.from_bytes(cal[0x92BE],'big'))
    elif kind=='battery':
        expected=numeric.battery(before,cal[0x87F8],int.from_bytes(cal[0x92BE],'big'))
    elif kind=='bank-publication':
        expected=numeric.bank_publication(case['argument'],before)
    elif kind=='diagnostic-copy':
        expected=numeric.diagnostic_copy(case['argument'],before)
    elif kind in ('compensation-caller','scaling-caller'):
        expected=numeric.bank_call_sequence(kind,before,cal)
    else:
        raise ValueError('the extended MAF original changes its exact invocation kind')
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('the extended MAF actual RAM disagrees with separate natural numeric/state equations')
    wanted=[];bank=case['argument']&255;offset=bank*2;wide=bank*4
    def read(site,address,width,data=before):
        wanted.append((site,'read',address,width,data[address:address+width].hex()))
    def write(site,address,width,data=None):
        data=expected['memory'] if data is None else data
        wanted.append((site,'write',address,width,data[address:address+width].hex()))
    calls=[(row['site'],row['target']) for row in result['calls']]
    if kind=='compensation':
        read(0x3AEAC,0x101C+offset,2)
        if not expected['initialized']:
            write(0x3AEC0,0x1E48+offset,2)
        else:
            read(0x3AED2,0x1E48+offset,2)
            if expected['denominator']:
                read(0x3AF04,0x3998+wide,4)
            write(0x3AF30,0x1E48+offset,2)
        required=[(0x3AF20,0x21CE0)] if expected['initialized'] and expected['denominator'] else []
        if calls!=required:
            raise ValueError('the compensation original changes its real initialized/nonzero natural call')
        if required:
            entry=result['calls'][0]['entry']
            if tuple(entry['registers'][:2])!=(expected['denominator'],expected['numerator']):
                raise ValueError('the compensation division changes its actual post-delay denominator/numerator')
    elif kind=='contribution':
        read(0x3AF68,0x1DF0+offset,2)
        if expected['forced']:
            write(0x3AF82,0x43CA+bank,1)
        if before[0x2462]&1 and not expected['forced']:
            read(0x3AFAA,0x43CA+bank,1)
        if expected['active']:
            read(0x3AFBE,0x1E08+offset,2)
            read(0x3AFD8,0x1E30+offset,2)
            write(0x3B010 if expected['candidate']<0 else 0x3B02E,0x1E00+offset,2)
            read(0x3B080,0x1E18+offset,2)
            read(0x3B0B8,0x1E1C+offset,2)
            write(0x3B13A,0x1E1C+offset,2)
            write(0x3B172 if expected['adjusted']<0 else 0x3B190,0x1DF8+wide,4)
            write(0x3B1C2,0x1E30+offset,2)
        else:
            read(0x3B1D4,0x1E10+wide,4)
            write(0x3B202,0x1DF8+wide,4)
            write(0x3B214,0x1E00+offset,2)
        if calls!=([(0x3B154,0x224FA)] if expected['active'] else []):
            raise ValueError('the contribution original changes its real active six-shift helper entry')
        if expected['active']:
            entry=result['calls'][0]['entry'];factor=cal[0x82B6][0] if expected['correction']>=0 else 64
            if (entry['registers'][0]!=((expected['correction']*factor)&0xFFFFFFFF)
                    or entry['registers'][5]!=(numeric.signed(expected['base'],16)&0xFFFFFFFF)):
                raise ValueError('the contribution helper changes its actual delay-slot operand or caller-local base')
    elif kind=='scaling':
        if expected['guarded']:
            read(0x6719A,0x4970,2)
            if expected['reset']:
                write(0x671BC,0x4970,2)
        read(0x3C420,0x1D62+offset,2)
        read(0x671E0,0x4970,2,data=expected['memory'])
        read(0x3C42C,0x1D62+offset,2)
        write(0x3C450,0x101C+offset,2)
        if calls!=[(0x3C414,0x67188),(0x3C426,0x671D8)]:
            raise ValueError('the scaling original changes its actual guard/scaler natural call order')
        first,second=(row['entry'] for row in result['calls'])
        if (first['registers'][13]!=bank or second['registers'][4]!=(numeric.signed(expected['sample'],16)&0xFFFFFFFF)
                or second['registers'][5]!=second['sp']):
            raise ValueError('the scaling calls change bank staging, actual sample or caller-local output pointer')
    elif kind=='battery':
        read(0x39AAE,0x1D6E,2);write(0x39AB0,0x1FC4,2);write(0x39AB8,0x1FC6,1)
        read(0x6718A,0x4252,1)
        if expected['guarded']:
            read(0x6719A,0x4970,2)
            if expected['reset']:write(0x671BC,0x4970,2)
        read(0x39AC4,0x1FC6,1,data=expected['memory'])
        read(0x671E0,0x4970,2,data=expected['memory']);write(0x39AE2,0x1188,1)
        call_sp=(observed['sp']-12)&0xFFFFFFFF
        wanted_calls=[(0x39ABC,0x67188,0x39AC0,call_sp),(0x39ACA,0x671D8,0x39ACE,call_sp)]
        if not test_contract.exact([tuple(row[key] for key in ('site','target','return_address','sp'))
                for row in result['calls']],wanted_calls):
            raise ValueError('the battery coefficient proof changes its exact real guard/scaler call sequence')
        for row in result['calls']:
            entry=row['entry']
            if (entry['sp'],entry['pr'],entry['gbr'])!=(call_sp,row['return_address'],0x01001E60):
                raise ValueError('the battery helper changes its actual caller frame, PR or GBR')
        scaler=result['calls'][1]['entry']
        if (scaler['registers'][4],scaler['registers'][5])!=(expected['sample'],call_sp):
            raise ValueError('the battery scaler changes its unsigned byte operand or actual delay-slot output pointer')
        returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
        if not test_contract.exact(returns,[(0x671C2,0x39AC0),(0x671FE,0x39ACE),(0x39AEA,observed['continuation'])]):
            raise ValueError('the battery proof changes a real guard, scaler or natural publisher return')
        context=observed['context'];exit=observed['exit']
        if (exit[19],exit[1],exit[2],exit[3],exit[4])!=(0x74,observed['continuation'],context[17],context[16],context[15]):
            raise ValueError('the battery publisher changes its terminal offset, PR, MACL, MACH or restored GBR')
    elif kind=='bank-publication':
        read(0x3B22A,0x1E2A,2)
        read(0x3B234,0x1DF8+wide,4)
        read(0x3B23C,0x2368,2)
        write(0x3B250,0x104C+wide,4)
        if calls:
            raise ValueError('the bank publication introduces an unexecuted helper call')
    elif kind=='diagnostic-copy':
        read(0x3C466,0x1D62+offset,2)
        write(0x3C46E,0x1A3E+offset,2)
        if calls:
            raise ValueError('the diagnostic word copy introduces an unexecuted helper call')
    else:
        required=[];previous=before;call_index=0
        for index,step in enumerate(expected['steps']):
            if kind=='compensation-caller':
                root=(0x3A91A+index*4,0x3AE8A)
                required.append(root)
                if call_index>=len(result['calls']):
                    raise ValueError('the compensation caller omits an actual natural call')
                root_call=result['calls'][call_index];call_index+=1
                if root_call['entry']['registers'][4]!=index:
                    raise ValueError('the compensation caller changes its actual post-delay bank argument')
                read(0x3AEAC,0x101C+index*2,2,data=previous)
                if not step['initialized']:
                    write(0x3AEC0,0x1E48+index*2,2,data=step['memory'])
                else:
                    read(0x3AED2,0x1E48+index*2,2,data=previous)
                    if step['denominator']:
                        read(0x3AF04,0x3998+index*4,4,data=previous)
                        required.append((0x3AF20,0x21CE0))
                        if call_index>=len(result['calls']):
                            raise ValueError('the compensation caller omits its nested division')
                        child=result['calls'][call_index]['entry'];call_index+=1
                        if tuple(child['registers'][:2])!=(step['denominator'],step['numerator']):
                            raise ValueError('the compensation caller changes a nested division operand')
                    write(0x3AF30,0x1E48+index*2,2,data=step['memory'])
            else:
                root=(0x3C3B6+index*4,0x3C408)
                required.extend((root,(0x3C414,0x67188),(0x3C426,0x671D8)))
                if len(result['calls'])<call_index+3:
                    raise ValueError('the scaling caller omits an actual root, guard or scaling call')
                root_call,guard,scaler=result['calls'][call_index:call_index+3];call_index+=3
                if (root_call['entry']['registers'][4]!=index or guard['entry']['registers'][13]!=index
                        or scaler['entry']['registers'][4]!=(numeric.signed(step['sample'],16)&0xFFFFFFFF)
                        or scaler['entry']['registers'][5]!=scaler['entry']['sp']):
                    raise ValueError('the scaling caller changes a bank, nested sample or caller-local output pointer')
                if step['guarded']:
                    read(0x6719A,0x4970,2,data=previous)
                    if step['reset']:write(0x671BC,0x4970,2,data=step['memory'])
                read(0x3C420,0x1D62+index*2,2,data=previous)
                read(0x671E0,0x4970,2,data=step['memory'])
                read(0x3C42C,0x1D62+index*2,2,data=previous)
                write(0x3C450,0x101C+index*2,2,data=step['memory'])
            previous=step['memory']
        if calls!=required or call_index!=len(result['calls']):
            raise ValueError('the dual-bank caller changes its exact natural call order or closure')
    physical=[(row['site'],row['mode'],row['address']-matrix.RAM_BASE,row['width_bytes'],row['bytes'])
        for row in result['accesses'] if row['domain']=='ram' and row['site'] in CLAIM_SITES[kind]]
    if physical!=wanted:
        raise ValueError('an extended MAF original changes an exact datum, site, direction, width or delay-slot transfer')
    return dict(index=case['index'],kind=kind,bank=bank,output=expected['output'],
        active=expected.get('active'),initialized=expected.get('initialized'),guarded=expected.get('guarded'),
        accesses=[dict(site=site,mode=mode,address=0xFFFF0000+address,width_bytes=width,bytes=raw)
                  for site,mode,address,width,raw in physical],
        native_relation_publication=False,scale_admission=False,units_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)


def require_state(declared,image,fixture,case,observed):
    matrix.require_input(declared['source'],image,case,observed)
    context=observed['context']
    seeded=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    seeded[160:164]=context[19].to_bytes(4,'big')
    seeded[164:168]=context[7].to_bytes(4,'big')
    seeded[184:188]=observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before']!=bytes(seeded) or observed['sp']!=((observed['abi_before'][10]-164)&0xFFFFFFFF)
            or observed['abi_before'][:10]!=packed_transfer_evidence.ABI or observed['abi_before']!=observed['abi_after']):
        raise ValueError('the maf-extended actual entry frame, independent fifth/R7, SP or caller ABI changes')
    expected_fixture=bytearray(fixture)
    for start,data in observed['calibration_before'].items():
        if (any(start<row['end'] and row['start']<start+len(data) for row in declared['source']['entry'])
                or any(start<at+4 and at<start+len(data) for at in contract.ALIASES)):
            raise ValueError('an extended MAF calibration input changes tested instructions or a pointer literal')
        expected_fixture[start:start+len(data)]=data
    result=state.execute(declared['source'],bytes(expected_fixture),context,observed['memory_before'][0],
        bytes(seeded),observed['sp'],observed['continuation'],observed['entry'],observed['sr_before'])
    expected=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
    if (not test_contract.exact(observed['exit'],expected) or observed['frame_after']!=result['frame']
            or observed['memory_after']!=(result['ram'],)):
        raise ValueError('the actual maf-extended complete state disagrees with independent natural instruction equations')
    return result,semantic(case,observed,result,image)


def require_witness(model,packet,inputs):
    keys={'schema','declaration','semantic_admission','consumed','reconstruction','image_sha256','fixture_sha256',
        'elf_sha256','observer_object_sha256','aliases','boundaries','stub_reconstruction','command','simulator','stdout','stderr',
        'stdout_sha256','stderr_sha256','observations','marker','toolchain'}
    if type(packet) is not dict or set(packet)!=keys:
        raise ValueError('the maf-extended original lacks its complete physical capture schema')
    same((packet['schema'],packet['semantic_admission']),(1,False),'the maf-extended raw packet grants its own admission')
    root=Path(model.root).resolve(); catalog=repo.images(root)['JK08A']; image=catalog.path.read_bytes()
    if sha(image)!=catalog.sha256 or packet['image_sha256']!=sha(image):
        raise ValueError('the maf-extended original changes its exact owned stock image')
    declared=declaration(model,image)
    same(packet['declaration'],declared,'the maf-extended original changes current closure or exact inputs')
    consumed=packet['consumed']
    if type(consumed) is not dict or set(consumed)!={HARNESS,OBSERVER,HEADER,*SOURCES}:
        raise ValueError('the extended MAF original omits an exact reused executable source')
    for name in (HARNESS,OBSERVER,*SOURCES):
        path='tools/sh-elf-run/'+name;data=(root/path).read_bytes()
        if consumed[name]!=data.hex() or inputs.get(path)!=sha(data):
            raise ValueError('the extended MAF original consumes another executable source snapshot')
    if consumed[HEADER]!=header(declared,image).hex():
        raise ValueError('the maf-extended original changes a private entry or calibration input')
    for path in (contract.DESCRIPTOR,'tools/sh-elf-run/maf_extended_capture.py','tools/kb/src/kb/maf_extended_contract.py',
                 'tools/kb/src/kb/maf_extended_matrix.py','tools/kb/src/kb/maf_extended_semantics.py',
                 'tools/kb/src/kb/division_callees_semantics.py','tools/kb/src/kb/byte_surface_equations.py',
                 'tools/kb/src/kb/maf_extended_capture_evidence.py','tools/kb/src/kb/width_view_matrix.py'):
        if inputs.get(path)!=sha((root/path).read_bytes()):
            raise ValueError('the maf-extended producer or independent contract source is stale')
    reconstructed=[]
    for unit in declared['source']['unit']:
        reconstructed.append(dict(unit=unit['id'],source=unit['assembly'],
            code=[dict(start=row['start'],end=row['end'],stock=image[row['start']:row['end']].hex(),
                       reconstructed=image[row['start']:row['end']].hex()) for row in unit['code']],
            pools=[dict(address=row['address'],stock=image[row['address']:row['address']+row['size']].hex(),
                        reconstructed=image[row['address']:row['address']+row['size']].hex()) for row in unit['pools']]))
    same(packet['reconstruction'],reconstructed,'an extended MAF GNU reconstruction changes stock code or literal spans')
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    same(packet['aliases'],aliases,'the maf-extended original changes an exact RAM pointer')
    same(packet['boundaries'],list(contract.BOUNDARIES),'the maf-extended original changes its exact outside-code observing returns')
    stubs=packet['stub_reconstruction']
    if type(stubs) is not list or len(stubs)!=len(contract.BOUNDARIES):
        raise ValueError('the extended MAF original omits a separately assembled observing return')
    for stub,boundary in zip(stubs,contract.BOUNDARIES):
        if type(stub) is not dict or set(stub)!={'address','bytes','object_sha256','elf_sha256','source_sha256'}:
            raise ValueError('the extended MAF original changes its complete return reconstruction')
        same((stub['address'],stub['bytes'],stub['source_sha256']),
            (boundary['address'],boundary['bytes'],sha((root/boundary['source']).read_bytes())),
            'the extended MAF observing return changes assembled bytes, address or private source')
        for key in ('object_sha256','elf_sha256'):ignition_literal_evidence.require_hash(stub[key])
    if packet['fixture_sha256']!=sha(fixture):
        raise ValueError('the maf-extended fixture changes an undeclared stock byte')
    for name in ('elf_sha256','observer_object_sha256'):ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout','stderr'):
        if type(packet[stream]) is not str or packet[stream+'_sha256']!=sha(packet[stream].encode()):
            raise ValueError('the maf-extended actual simulator stream changes')
    simulator=packet['simulator']
    if (type(simulator) is not dict or set(simulator)!={'command','returncode','timeout_seconds'}
            or not test_contract.exact((simulator['returncode'],simulator['timeout_seconds']),(0,1200))
            or type(simulator['command']) is not list or len(simulator['command'])!=3):
        raise ValueError('the maf-extended original changes its bounded actual simulator command or terminal')
    from kb.test_stock_capture import tool
    base=tool(root,'verify_map_switching.py','_kb_maf_extended_base_verifier')
    if simulator['command'][:2]!=[base.RUN,'--memory-region=0x01000000,64k']:
        raise ValueError('the maf-extended original uses another pinned simulator or memory domain')
    elf=Path(simulator['command'][2])
    if elf.name!='harness.elf' or elf.parent.name!=REGION:
        raise ValueError('the maf-extended original executes another harness artifact')
    private=elf.parent/'consumed'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(private),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',str(elf),str(private/HARNESS),str(elf.parent/'invoke.o'),str(elf.parent/'fixture.o')]
    same(packet['command'],command,'the maf-extended original changes its compiled source, observer or fixture command')
    toolchain=packet['toolchain']
    if (type(toolchain) is not dict or toolchain.get('simulator_version')!='16.3' or toolchain.get('gcc_version')!='13.3.0'
            or set(toolchain.get('binaries',{}))!={'as','ld','objcopy','gcc','run'}):
        raise ValueError('the maf-extended original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():ignition_literal_evidence.require_hash(identity)
    actual=observations(packet,declared);semantics=[]
    coverage={site:set() for site in REQUIRED_BRANCHES};groups={row:{} for row in READERS}
    battery_coverage={site:set() for site in BATTERY_BRANCHES}
    for case,observed in zip(declared['cases'],actual):
        result,value=require_state(declared,image,fixture,case,observed);semantics.append(value)
        for branch in result['branches']:
            if branch['site'] in coverage:coverage[branch['site']].add(branch['kind'])
            if case['kind']=='battery' and branch['site'] in battery_coverage:
                battery_coverage[branch['site']].add(branch['kind'])
        for kind,address,width in READERS:
            if case['kind']!=kind or (kind not in ('compensation-caller','battery') and value['bank']!=1) or not any(row['mode']=='read' and row['address']==address
                    and row['width_bytes']==width for row in value['accesses']):
                continue
            memory=bytearray(observed['memory_before'][0]);offset=address&65535
            incoming=bytes(memory[offset:offset+width]);memory[offset:offset+width]=bytes(width)
            held=dict(memory=memory.hex(),context=list(observed['context']),
                calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()})
            if kind=='battery':
                held.update(frame=observed['frame_before'].hex(),sp=observed['sp'],
                    continuation=observed['continuation'],abi=list(observed['abi_before']),sr_before=observed['sr_before'])
            key=json.dumps(held,sort_keys=True,separators=(',',':'))
            groups[kind,address,width].setdefault(key,set()).add((incoming.hex(),value['output']))
    if any(outcomes!={'taken','fallthrough'} for outcomes in coverage.values()):
        raise ValueError('the extended MAF original omits a required mode, boundary or access-path outcome')
    if any(outcomes!={'taken','fallthrough'} for outcomes in battery_coverage.values()):
        raise ValueError('the battery coefficient original omits its own required guard-boundary or byte-cap branch outcome')
    for reader,alternatives in groups.items():
        if not any(len({value[0] for value in values})>=2 and len({value[1] for value in values})>=2
                   for values in alternatives.values()):
            raise ValueError(f'the extended MAF reader {reader} lacks positive value/output alternatives with other inputs fixed')
    if {case['entry'] for case in declared['cases']}!=set(contract.ENTRIES):
        raise ValueError('the extended MAF original omits a natural parent entry')
    return dict(region=REGION,image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=packet['elf_sha256'],
        stdout_sha256=packet['stdout_sha256'],observations=len(actual),native_bindings=native_bindings(model),
        semantic_results=semantics,conditional_branch_outcomes={f'{site:08x}':sorted(values) for site,values in coverage.items()},
        exact_natural_MAF_transfers=True,exact_battery_coefficient_transfer=True,
        battery_branch_outcomes={f'{site:08x}':sorted(values) for site,values in battery_coverage.items()},
        native_geometry_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False,
        native_relation_publication=False,scale_admission=False,units_admission=False)


def require_primary(model,record):
    original,current=ignition_literal_evidence.require_original(model,record)
    packet=record['candidate']['witness'].get('maf_extended_paths')
    result=require_witness(model,packet,record['candidate']['producer_inputs'])
    if original.count(packet['marker'])!=1:
        raise ValueError('the original complete primary lacks its unique exact maf-extended marker')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the maf-extended inputs change during independent admission')
    return result
