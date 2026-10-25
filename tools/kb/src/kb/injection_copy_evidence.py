"""Exact descriptor and native owner binding for the bounded injection copy."""
import hashlib
import tomllib
from kb import copy_evidence as common, injection_copy_matrix as matrix, repo
from kb.model import SymbolKey

SCHEMA = 1
KEY = 'snapshot-copy-v1:jk08a-injection-140'
DESCRIPTOR = 'defs/JK08A.injection-copy.toml'
REGION = 'jk08a-injection-snapshot'
FUNCTION = SymbolKey('7mfk', 'fn', 0x20dfe)
FUNCTION_MEANING = 'coherent_snapshot/fn'
# Address, direction, meaning, declared width/signedness and original claim digest.
MEMBERS = (
    (0xffff2333, 'writer', 'nippy-caribou/ram', 8, False, 'd0e0f11092826fb65dd6d60a9c6a579c2069f78150843ee06895fff3a145d762'),
    (0xffff2348, 'writer', 'berserk-terrier/ram', 16, False, '04cd562aa87fb3021922b45b5ca200794ebf13d337b0b3eba3d79abb6d981def'),
    (0xffff2356, 'writer', 'lumpy-kudu/ram', 8, True, '04cddf0fa28be02c2a27664e3c20a3adecfc73b8ddb39bb265b72ce0abb336d9'),
    (0xffff2364, 'writer', 'fabulous-koel/ram', 8, False, '4db3ea5bc2b9051cdd2c2eace1cc5dcb44dd9a6a4fc097ee02bb20d6430e1ead'),
    (0xffff2378, 'writer', 'liberal-gorilla/ram', 8, True, '70235cbdb97dd9b16795c75aa1d8bfe6d69581d168192438636e1ebf44d73c7a'),
    (0xffff237a, 'writer', 'aloof-stork/ram', None, None, '25ea6851dc3b423177e78e48b1e9c0f5db42db3c75eb0f37b8a3f9a6044a9630'),
    (0xffff2390, 'writer', 'quiet-gerbil/ram', None, None, '5125193b5af7a9ccc68e773467a88d46728396ee0c36c81819b21805900bb805'),
    (0xffff23aa, 'writer', 'flashy-jerboa/ram', 16, False, '281d7c82f5e58215fbcec9d302bae5ff0eb9de3ebd3e832d7592e901ef8a26bb'),
    (0xffff23b4, 'writer', 'intake_cvtc_duty_command_b1/ram', 8, None, 'c89be8e258e7bd9b70be552da5647fcfdde83228765bfe37cf64c7e219d70039'),
    (0xffff23b5, 'writer', 'intake_cvtc_duty_command_b2/ram', 8, None, 'b436a69988ba45ce8b773d1ce48b95df8c972674da3d50372baee757d589173a'),
    (0xffff23bf, 'reader', 'righteous-scorpion/ram', 8, False, '8bd8fbf487f234e24ff8bafe90f10ef805f140c0f16bd19bcf310cb74fc3b49f'),
    (0xffff23d4, 'reader', 'handsome-spaniel/ram', 16, False, '2a219912fded6fb7ce83f33d4c098357f47eb6012335b06f2c5f95bbc202af01'),
    (0xffff23e2, 'reader', 'lavender-dalmatian/ram', None, None, '4fcdcef70ab53b416da73edf01d1057f7ed64404d547470e38d8cdce599fda82'),
    (0xffff23f0, 'reader', 'flat-coyote/ram', 8, False, '5eef06a436dc72d2fc1e0e8950091578a083633b944d7fe30d24209274655360'),
    (0xffff2404, 'reader', 'functional-corgi/ram', None, None, 'aff485131fa71c6bb19e37ca01930beb11bf740118aaef9e2dd88f5ec9f791ae'),
    (0xffff2406, 'reader', 'cuddly-crow/ram', None, None, '4d289a51d2d19cb18d91f33e0e04af0ddfa63b7f375bdb6509f0b6e34f01d73e'),
    (0xffff240c, 'reader', 'fervent-bittern/ram', None, None, 'adedf796c8af24cd27165ae19d3b5f8667a24b83a417cf1094e5a62855fffc75'),
    (0xffff240e, 'reader', 'sepia-armadillo/ram', None, None, 'c95f3bfed4dd4cbf7117e9d127fa7578aa0ffe1518dd54eb87f050edf6e022e9'),
    (0xffff241c, 'reader', 'devout-swift/ram', 16, False, 'e5f598a9bff4c552d2c75b7c25dbc19d5c2f16935bdc15080a16ba83b4d944f9'),
    (0xffff2436, 'reader', 'portable-kingfisher/ram', 16, False, 'fe75bafe2ea579fd6f5e0173d2e0122702b7180d1acf617c3926fadad44a7e71'),

)
MEMBER_KEYS = frozenset(SymbolKey('7mfk', 'ram', row[0]) for row in MEMBERS)


def registered(evidence, symbol=None):
    key = evidence.get('key')
    return ((isinstance(key, str) and key.startswith('snapshot-copy-'))
            or evidence.get('path') == DESCRIPTOR or evidence.get('mode') == 'snapshot-copy')


def member_item(row):
    address, direction, meaning, width, signed, identity = row
    start = matrix.SOURCE if direction == 'reader' else matrix.DESTINATION
    return dict(kind='indirect', mode='snapshot-copy', key=KEY, path=DESCRIPTOR,
                at='7mfk:00021318', to=FUNCTION, supports='identity',
                value=dict(direction=direction, offset_bytes=address-start, width_bits=width or 8))


def descriptor(root=repo.ROOT):
    value = tomllib.loads(common._read(root, DESCRIPTOR).decode('utf-8'))
    if (set(value) != {'schema','id','layout','image','copy','caller','entry_context',
                       'simulation','matrix','code','pool','member'}
            or type(value['copy']['overlap']) is not bool
            or type(value['schema']) is not int or value['schema'] != SCHEMA or value['id'] != KEY
            or value['layout'] != '7mfk' or value['image'] != 'JK08A'
            or value['copy'] != dict(source=matrix.SOURCE, destination=matrix.DESTINATION,
                                    length_bytes=140, overlap=False)):
        raise ValueError('the descriptor describes another injection copy')
    if value['caller'] != dict(meaning=FUNCTION_MEANING, function=0x20dfe, entry=0x21314,
            call=0x21318, delay_slot=0x2131a, end=0x2131c, callee=0x22558, callee_end=0x22590):
        raise ValueError('the injection caller boundary changed')
    if value['entry_context'] != dict(r11=0x22558, r12=140,
            scope='bounded caller with explicit R11/R12; complete scheduler execution and hardware atomicity require separate evidence'):
        raise ValueError('the injection entry contexts changed')
    if value['simulation'] != dict(ram_base=matrix.RAM_BASE, ram_size=65536, boundary=0x2131c,
            boundary_bytes='57f6472a000b0009', return_register=7, stack_return_offset=24,
            frame_bytes_below_sp=64):
        raise ValueError('the injection simulation boundary changed')
    header = 'tools/sh-elf-run/injection-snapshot-cases.h'
    if value['matrix'] != dict(count=1700, caller_affine=1024, caller_isolated=280,
            helper=384, successive=12, header=header,
            header_sha256=hashlib.sha256(common._read(root, header)).hexdigest()):
        raise ValueError('the injection matrix identity changed')
    expected = []
    for address, direction, meaning, width, signed, identity in MEMBERS:
        start = matrix.SOURCE if direction == 'reader' else matrix.DESTINATION
        expected.append(dict(meaning=meaning, direction=direction, address=address,
            offset_bytes=address-start, witness_width_bits=width or 8,
            declared_width=str(width) if width is not None else 'unset',
            declared_signed=('signed' if signed else 'unsigned') if signed is not None else 'unset',
            claim_sha256=identity))
    if value['member'] != expected:
        raise ValueError('the injection descriptor has other native members')
    image = repo.images(root)['JK08A']
    data = common._read(root, image.path.relative_to(root).as_posix())
    if hashlib.sha256(data).hexdigest() != image.sha256:
        raise ValueError('the stock image disagrees with its catalog')
    spans = ((0x21314,0x2131c),(0x22558,0x22590))
    if value['code'] != [dict(start=start, bytes=data[start:end].hex()) for start,end in spans]:
        raise ValueError('the injection descriptor disagrees with exact stock instructions')
    pools = [(0x213a0, matrix.DESTINATION),(0x213a4, matrix.SOURCE)]
    if value['pool'] != [dict(address=address,value=word) for address,word in pools]:
        raise ValueError('the injection descriptor has other pools')
    for address,word in pools:
        if int.from_bytes(data[address:address+4],'big') != word:
            raise ValueError('a stock injection pointer pool changed')
    for site,register,pool in ((0x21314,1,0x213a0),(0x21316,2,0x213a4)):
        word=int.from_bytes(data[site:site+2],'big')
        if word>>8 != 0xd0+register or (site&~3)+4+(word&255)*4 != pool:
            raise ValueError('an injection pointer load changed')
    if data[0x21318:0x2131c] != bytes.fromhex('4b0b60c3'):
        raise ValueError('the injection JSR or R12 delay slot changed')
    return value


def member(model, symbol):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or FUNCTION not in model.symbols or model.symbols[FUNCTION].meaning is None
            or model.symbols[FUNCTION].meaning.key != FUNCTION_MEANING):
        raise ValueError('the injection copy requires complete native context')
    for row in MEMBERS:
        address, direction, meaning, width, signed, identity = row
        if symbol.key == SymbolKey('7mfk','ram',address):
            if (symbol.meaning is None or symbol.meaning.key != meaning
                    or type(symbol.value('width')) is not type(width) or symbol.value('width') != width
                    or type(symbol.value('signed')) is not type(signed) or symbol.value('signed') != signed):
                raise ValueError('the injection member owner, width or signedness changed')
            return row
    raise ValueError('the injection copy supports another member')


def link(model, symbol, row):
    from kb import reconciliation
    function=model.symbols[FUNCTION].meaning
    found=[item for item in model.links if item.owner is symbol.meaning and item.to is function
           and item.type==row[1] and '7mfk' in (item.props.get('layouts') or ['7mfk'])]
    if len(found)!=1:
        raise ValueError('the injection copy needs one original native relation')
    result=found[0]
    fields=common.claim_fields(result,'7mfk')
    proof=member_item(row)
    fields={**fields,'evidence':[item for item in fields['evidence'] if item!=proof]}
    if reconciliation.digest(fields)!=row[5]:
        raise ValueError('the original injection native claim changed')
    if sum(item==proof for item in result.evidence)>1:
        raise ValueError('duplicate injection proof attachment')
    return result


def publication(relation, evidence):
    """Recognize only the exact original owner and unique typed proof shape."""
    if relation.to.key != FUNCTION_MEANING or relation.slot is not None or relation.offset is not None:
        return False
    return any(relation.owner.key == row[2] and relation.type == row[1]
               and common.encode(evidence) == common.encode(member_item(row)) for row in MEMBERS)


def scope_digest(model):
    """Bind every incident fact of the twenty members and their caller."""
    from pathlib import Path
    from kb import convert
    if any(not hasattr(model, name) for name in
           ('layouts','spaces','functions','config','overlay','names')):
        raise ValueError('the injection scope requires a complete native model')
    for path in model.overlay:
        path=Path(path)
        if path.is_absolute() or '..' in path.parts or (
                (not path.parts or path.parts[0]!='kb') and path!=repo.OWNER_CONFIG):
            raise ValueError('an overlay changes injection execution inputs')
    meanings={FUNCTION_MEANING:model.symbols[FUNCTION].meaning}
    for row in MEMBERS:
        symbol=model.symbols[SymbolKey('7mfk','ram',row[0])]
        member(model,symbol)
        link(model,symbol,row)
        meanings[row[2]]=symbol.meaning
    value=lambda data:convert._value(model,data)
    owners=[]
    for key,meaning in sorted(meanings.items()):
        links=[]
        for relation in model.links:
            if relation.owner is not meaning and relation.to is not meaning:
                continue
            from kb import snapshot_rom_contract
            if snapshot_rom_contract.representation_only(relation,model.root):
                continue
            links.append((relation.owner.key,relation.type,relation.to.key,relation.slot,relation.offset,
                value(relation.props),value(common.semantic_evidence(relation)),relation.roles,
                relation.stated,relation.sources))
        owners.append(dict(key=key,kind=meaning.kind,semantic=meaning.semantic,
            props=value(meaning.props),tables=value(meaning.tables),names=meaning.other_names,
            sources=meaning.sources,tier=meaning.tier,name_sources=meaning.name_sources,
            groups=value(meaning.groups),
            statuses={name:(status.state,value(status.props),value(status.evidence),status.sources)
                      for name,status in meaning.statuses.items()},
            symbols={name:(symbol.key,symbol.name,symbol.generated,symbol.former,value(symbol.props),
                           value(symbol.evidence),symbol.sources,symbol.implicit)
                     for name,symbol in meaning.symbols.items()},links=links))
    settings={key:data for key,data in model.config.items()
              if key not in ('names','reconciliation','source_bindings')}
    return common.digest(common.encode(dict(owners=owners,layouts=model.layouts,spaces=model.spaces,
                                           functions=model.functions,settings=settings)))


def validate_witness(witness, inputs, root):
    """Independently validate the complete original GNU observation packet."""
    from kb.test_contract import exact
    descriptor(root)
    cases=matrix.cases()
    if witness['region']!=REGION or not exact(witness['cases'],cases):
        raise ValueError('the injection matrix is wrong, skipped or reordered')
    if len(witness['observations'])!=len(cases):
        raise ValueError('the injection execution omits actual observations')
    memory=None
    for index,(case,observed) in enumerate(zip(cases,witness['observations'])):
        memory=matrix.validate_observation(index,case,observed,memory)
    consumed=(DESCRIPTOR,'tools/sh-elf-run/stock_jk08a_injection_snapshot.s',
        'tools/sh-elf-run/harness-stock-jk08a-injection-snapshot.c',
        'tools/sh-elf-run/injection-snapshot-cases.h',
        'tools/sh-elf-run/harness-injection-snapshot-capture.c',
        'tools/sh-elf-run/stock_injection_start_delay_invoke.s')
    if set(witness['consumed'])!=set(consumed):
        raise ValueError('the injection capture omits private consumed sources')
    for path,data in witness['consumed'].items():
        if hashlib.sha256(bytes.fromhex(data)).hexdigest()!=inputs[path]:
            raise ValueError('the injection execution consumes another source snapshot')
    image=repo.images(root)['JK08A']
    data=common._read(root,image.path.relative_to(root).as_posix())
    if witness['image_sha256']!=hashlib.sha256(data).hexdigest():
        raise ValueError('the injection execution uses another stock image')
    spans=((0x21314,0x2131c),(0x22558,0x22590))
    required=[dict(start=start,end=end,stock=data[start:end].hex(),reconstructed=data[start:end].hex())
              for start,end in spans]
    if not exact(witness['code'],required):
        raise ValueError('the injection stock instructions differ from their reconstruction')
    pools=[dict(address=0x213a0,stock=data[0x213a0:0x213a8].hex(),
                reconstructed=data[0x213a0:0x213a8].hex())]
    if not exact(witness['pools'],pools):
        raise ValueError('the injection pointer pools differ from their reconstruction')
    if not exact(witness['aliases'],[[0x213a0,0xffff2330,0x01002330],[0x213a4,0xffff23bc,0x010023bc]]):
        raise ValueError('the injection fixture has undeclared RAM relocations')
    if not exact(witness['entry'],dict(r11=0x22558,r12=140,caller=0x21314,callsite=0x21318,
            delay_slot=0x2131a,source=matrix.SOURCE,destination=matrix.DESTINATION,length=140)):
        raise ValueError('the injection bounded entry assumptions changed')
    boundary=bytes.fromhex('57f6472a000b0009')
    if not exact(witness['boundary'],dict(address=0x2131c,bytes=boundary.hex())):
        raise ValueError('the injection observation boundary changes')
    fixture=bytearray(data)
    fixture[0x213a0:0x213a4]=(0x01002330).to_bytes(4,'big')
    fixture[0x213a4:0x213a8]=(0x010023bc).to_bytes(4,'big')
    fixture[0x2131c:0x2131c+len(boundary)]=boundary
    if witness['fixture_sha256']!=hashlib.sha256(fixture).hexdigest():
        raise ValueError('the injection fixture changes undeclared stock bytes')
    sha=lambda value:type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value)
    if not sha(witness['elf_sha256']):
        raise ValueError('the injection execution lacks its compiled ELF identity')
    toolchain=witness['toolchain']
    if (toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}
            or not all(sha(value) for value in toolchain['binaries'].values())):
        raise ValueError('the injection execution has another GNU toolchain')


def failure(evidence, symbol=None, model=None, claim=None, *, record=None):
    try:
        row=member(model,symbol)
        if common.encode(evidence)!=common.encode(member_item(row)):
            return 'the injection copy requires its exact typed evidence scope'
        if claim!='identity' and (getattr(claim,'name',None)!='identity'
                or getattr(claim,'subject',None) not in (symbol.key.key,row[2],row[2].rsplit('/',1)[0])):
            return 'the injection copy requires identity-claim context'
        relation=link(model,symbol,row)
        if sum(common.encode(item)==common.encode(evidence) for item in relation.evidence)!=1:
            return 'the injection copy requires its unique owning link evidence'
        # Both copy domains are bound to the same original full primary terminal.
        can_reader=model.symbols[SymbolKey('7mfk','ram',common.MEMBERS['reader'][1])]
        return common.failure(common.item('reader'),can_reader,model,'identity',record=record)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):
        return 'missing or invalid qualified injection execution context'


def accepted(model,symbol,function,claim):
    if function.key!=FUNCTION or symbol.key not in MEMBER_KEYS:
        return None
    entries=[entry for entry in claim['evidence'] if registered(entry,symbol)]
    if len(entries)!=1 or failure(entries[0],symbol,model,'identity') is not None:
        return None
    row=member(model,symbol)
    if claim!=common.claim_fields(link(model,symbol,row),'7mfk'):
        return None
    return dict(proof=KEY,callsite='7mfk:00021318',scope='bounded-copy',support='identity')


def retires(before,after,old_claim):
    """Retire exactly one original review after an identity-only proof append."""
    from kb import reconciliation
    try:
        if any(registered(entry) for entry in old_claim['evidence']):
            return False
        found=[(symbol,function,claim) for symbol,function,claim in reconciliation.access_claims(after)
               if reconciliation.claim_identity(claim)==reconciliation.claim_identity(old_claim)]
        if len(found)!=1:
            return False
        symbol,function,claim=found[0]
        row=member(after,symbol)
        proof=member_item(row)
        if claim['evidence']!=[*old_claim['evidence'],proof] or {**claim,'evidence':old_claim['evidence']}!=old_claim:
            return False
        original=before.symbols[symbol.key]
        member(before,original)
        if scope_digest(before)!=scope_digest(after):
            return False
        return accepted(after,symbol,function,claim) is not None
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return False
