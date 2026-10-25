"""Exact stock and native-owner descriptor for bounded coherent RAM copies.

Native publication requires the independently finalized shared COPY terminal.
Descriptors and controlled fixtures alone award no evidence level.
"""
import hashlib
import tomllib

from kb import coherent_copy_matrix as matrix, coherent_copy_members as pins
from kb import copy_evidence as common, repo
from kb.model import SymbolKey

KEY=pins.KEY
DESCRIPTOR=pins.DESCRIPTOR
FUNCTION_MEANING=pins.FUNCTION_MEANING
MEMBERS=pins.MEMBERS
FUNCTION=SymbolKey('7mfk','fn',0x20dfe)
MEMBER_KEYS=frozenset(SymbolKey('7mfk','ram',row[0]) for row in MEMBERS)

def parent(row):
    address,meaning=pins.CALLERS.get(row[6],(FUNCTION.address,FUNCTION_MEANING))
    return SymbolKey('7mfk','fn',address),meaning

ACCESS_RELATIONS=frozenset((row[2],row[1],parent(row)[1]) for row in MEMBERS)

def looks_like_access(relation):
    return ((relation.owner.key,relation.type,relation.to.key) in ACCESS_RELATIONS
            or any(registered(item) for item in relation.evidence))

def link_failure(model,relation):
    if not looks_like_access(relation):
        return None
    entries=[item for item in relation.evidence if registered(item)]
    if len(entries)!=1:
        return 'the coherent relation lacks its one exact owning execution attachment'
    return failure(entries[0],relation.owner.symbols.get('7mfk'),model,'identity')

def code_spans(window):
    code=[(window.entry,window.call+4)]
    if window.helper==0x22558:
        code.append((0x22558,0x22590))
    elif window.helper==0x22104:
        code.extend(((0x22104,0x22110),(0x2213a,0x22158)))
    elif window.helper==0x220f8:
        code.extend(((0x220f8,0x22104),(0x2211e,0x22158)))
    else:
        code.extend(((0x22038,0x22040),(0x220d8,0x220f8)))
    return tuple(code)

def pool_words(window,image):
    pools={}
    for start,end in code_spans(window):
        for at in range(start,end,2):
            word=int.from_bytes(image[at:at+2],'big')
            if word>>12==0xd:
                address=(at&~3)+4+(word&255)*4
                pools[address]=int.from_bytes(image[address:address+4],'big')
    if window.helper==0x22104:pools.update({0x22110:0x22158,0x22174:0x2213a})
    if window.helper==0x220f8:
        pools.update({0x22110:0x22158,0x22158+window.length:0x22156-window.length})
    for at,value in pools.items():
        if image[at:at+4]!=value.to_bytes(4,'big'):
            raise ValueError('a fixed dispatch pointer differs from stock')
    return [dict(address=at,value=value) for at,value in sorted(pools.items())]

def early_indices(window):
    return matrix.early_indices(window)

def member_descriptor(row):
    address,direction,meaning,width,signed,claim,call,kind,site,offset,transfer=row
    return dict(meaning=meaning,address=address,direction=direction,mechanism=kind,
        access_site=site,offset_bytes=offset,witness_width_bits=width or 8,
        transfer_width_bits=transfer,declared_width=str(width) if width is not None else 'unset',
        declared_signed=('signed' if signed else 'unsigned') if signed is not None else 'unset',
        claim_sha256=claim)

def expected_descriptor(image,header):
    if hashlib.sha256(image).hexdigest()!=pins.IMAGE_SHA256:
        raise ValueError('the coherent copy stock image differs from its exact catalog identity')
    expected=dict(schema=1,id=KEY,layout='7mfk',image='JK08A',image_sha256=pins.IMAGE_SHA256,
        parent=FUNCTION_MEANING,function=0x20dfe,
        parents=[dict(function=key.address,meaning=meaning) for key,meaning in
                 sorted({parent(row) for row in MEMBERS},key=lambda item:item[0].address)],
        scope='Bounded callers with explicit entry registers; scheduler reachability, cadence and hardware atomicity require separate evidence.',
        simulation=dict(ram_base=matrix.RAM_BASE,ram_size=65536,boundary_bytes='57f6472a000b0009',
            return_register=7,stack_return_offset=24,frame_bytes_below_sp=64,frame_bytes_total=96,
            observer='tools/sh-elf-run/stock_injection_start_delay_invoke.s'),
        matrix=dict(cases=sum(len(matrix.cases(w)) for w in matrix.WINDOWS),
            feedback_cases=sum(len(early_indices(w)) for w in matrix.WINDOWS),windows=len(matrix.WINDOWS),
            header='tools/sh-elf-run/coherent-copy-cases.h',header_sha256=hashlib.sha256(header).hexdigest()),
        window=[])
    for window in matrix.WINDOWS:
        address,meaning=pins.CALLERS.get(window.call,(FUNCTION.address,FUNCTION_MEANING))
        row=dict(key=f'jk08a-coherent-{window.call:08x}',entry=window.entry,call=window.call,
            parent=meaning,function=address,
            delay_slot=window.call+2,end=window.call+4,helper=window.helper,source=window.source,
            destination=window.destination,length_bytes=window.length,cases=len(matrix.cases(window)),
            feedback_cases=len(early_indices(window)),entry_context={'r'+str(r):v for r,v in window.context},
            assembly='tools/sh-elf-run/stock_jk08a_coherent_'+f'{window.call:08x}'+'.s',
            read_ahead_bytes=4 if window.helper==0x22038 else 0,
            code=[dict(start=a,bytes=image[a:b].hex()) for a,b in code_spans(window)],
            pool=pool_words(window,image),member=[member_descriptor(r) for r in MEMBERS if r[6]==window.call])
        if window.helper==0x22038:
            row['large_scope']='Only caller-fixed lengths 88 and 128, greater than 64; the compact dispatch table is outside the executed path.'
        expected['window'].append(row)
    return expected

def validate_descriptor(value,image,header):
    from kb.test_contract import exact
    if not exact(value,expected_descriptor(image,header)):
        raise ValueError('the coherent copy descriptor changes its exact bounded context')
    return value

def descriptor(root=repo.ROOT):
    value=tomllib.loads(common._read(root,DESCRIPTOR).decode('utf-8'))
    catalog=repo.images(root)['JK08A']
    image=common._read(root,catalog.path.relative_to(root).as_posix())
    header=common._read(root,'tools/sh-elf-run/coherent-copy-cases.h')
    return validate_descriptor(value,image,header)


def registered(evidence, symbol=None):
    key=evidence.get('key')
    return ((isinstance(key,str) and key.startswith('coherent-copy-'))
            or evidence.get('path')==DESCRIPTOR or evidence.get('mode')=='coherent-copy')


def member_item(row):
    address,direction,meaning,width,signed,identity,call,kind,site,offset,transfer=row
    return dict(kind='indirect',mode='coherent-copy',key=KEY,path=DESCRIPTOR,
        at=f'7mfk:{call:08x}',to=parent(row)[0],supports='identity',
        value=dict(direction=direction,mechanism=kind,access_site=f'7mfk:{site:08x}',
            offset_bytes=offset,width_bits=width or 8,transfer_width_bits=transfer))


def member(model,symbol,*,row=None,evidence=None):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or row is not None and row not in MEMBERS):
        raise ValueError('the coherent copy requires complete native context')
    candidates=[entry for entry in MEMBERS if symbol.key==SymbolKey('7mfk','ram',entry[0])
                and (row is None or entry==row)
                and (evidence is None or common.encode(evidence)==common.encode(member_item(entry)))]
    if len(candidates)!=1:
        raise ValueError('the coherent copy requires one exact owning caller attachment')
    selected=candidates[0]
    address,direction,meaning,width,signed,identity=selected[:6]
    function,function_meaning=parent(selected)
    if (function not in model.symbols or model.symbols[function].meaning is None
            or model.symbols[function].meaning.key!=function_meaning
            or symbol.meaning is None or symbol.meaning.key!=meaning
            or type(symbol.value('width')) is not type(width) or symbol.value('width')!=width
            or type(symbol.value('signed')) is not type(signed) or symbol.value('signed')!=signed):
        raise ValueError('the coherent member owner, caller, width or signedness changed')
    return selected


def link(model,symbol,row):
    from kb import reconciliation
    function=model.symbols[parent(row)[0]].meaning
    found=[item for item in model.links if item.owner is symbol.meaning and item.to is function
           and item.type==row[1] and '7mfk' in (item.props.get('layouts') or ['7mfk'])]
    if len(found)!=1:
        raise ValueError('the coherent copy needs one original native relation')
    result=found[0];fields=common.claim_fields(result,'7mfk');item=member_item(row)
    fields={**fields,'evidence':[entry for entry in fields['evidence'] if common.encode(entry)!=common.encode(item)]}
    if reconciliation.digest(fields)!=row[5]:
        raise ValueError('the original coherent native claim changed')
    if sum(common.encode(entry)==common.encode(item) for entry in result.evidence)>1:
        raise ValueError('duplicate coherent proof attachment')
    return result


def publication(relation,evidence):
    if relation.slot is not None or relation.offset is not None:
        return False
    return any(relation.to.key==parent(row)[1] and relation.owner.key==row[2] and relation.type==row[1]
               and common.encode(evidence)==common.encode(member_item(row)) for row in MEMBERS)


def consumed_names(value):
    return (DESCRIPTOR,'tools/sh-elf-run/harness-coherent-copy-capture.c',
        'tools/sh-elf-run/stock_injection_start_delay_invoke.s',
        'tools/sh-elf-run/coherent-copy-cases.h',*(row['assembly'] for row in value['window']))


def validate_witness(witness,inputs,root):
    """Check every registered actual window against independent state equations."""
    from kb.test_contract import exact
    value=descriptor(root)
    if (set(witness)!={'schema','key','windows','consumed','toolchain'}
            or not exact(witness['schema'],1) or witness['key']!=KEY
            or type(witness['windows']) is not list or len(witness['windows'])!=len(matrix.WINDOWS)):
        raise ValueError('the complete coherent copy packet is missing or has another schema')
    consumed=witness['consumed']
    if set(consumed)!=set(consumed_names(value)):
        raise ValueError('the coherent capture omits private consumed sources')
    for path,data in consumed.items():
        if hashlib.sha256(bytes.fromhex(data)).hexdigest()!=inputs[path]:
            raise ValueError('the coherent capture consumes another source snapshot')
    image=repo.images(root)['JK08A'];data=common._read(root,image.path.relative_to(root).as_posix())
    fields={'region','cases','observations','code','pools','image_sha256','fixture_sha256',
            'elf_sha256','aliases','boundary','instructions'}
    for window,row,actual in zip(matrix.WINDOWS,value['window'],witness['windows']):
        cases=matrix.cases(window)
        if (set(actual)!=fields or actual['region']!=row['key'] or not exact(actual['cases'],cases)
                or type(actual['observations']) is not list or len(actual['observations'])!=len(cases)):
            raise ValueError('a coherent matrix is wrong, skipped, duplicated or reordered')
        pools=b''.join(matrix.alias(p['value']).to_bytes(4,'big') for p in row['pool'])
        memory=None
        for case,observed in zip(cases,actual['observations']):
            memory=matrix.validate_observation(window,case,observed,pools,memory)
        code=[dict(start=a,end=b,stock=data[a:b].hex(),reconstructed=data[a:b].hex())
              for a,b in code_spans(window)]
        pointers=[dict(address=p['address'],stock=data[p['address']:p['address']+4].hex(),
                       reconstructed=data[p['address']:p['address']+4].hex()) for p in row['pool']]
        if not exact(actual['code'],code) or not exact(actual['pools'],pointers):
            raise ValueError('the coherent instruction or pointer reconstruction changes')
        if not exact(actual['instructions'],sum((b-a)//2 for a,b in code_spans(window))):
            raise ValueError('the coherent instruction count changes')
        aliases=[[p['address'],p['value'],matrix.alias(p['value'])] for p in row['pool'] if p['value']>=0xffff0000]
        boundary=dict(address=window.call+4,bytes='57f6472a000b0009')
        if not exact(actual['aliases'],aliases) or not exact(actual['boundary'],boundary):
            raise ValueError('the coherent relocation or observation boundary changes')
        fixture=bytearray(data)
        for address,original,alias in aliases:fixture[address:address+4]=alias.to_bytes(4,'big')
        fixture[boundary['address']:boundary['address']+8]=bytes.fromhex(boundary['bytes'])
        if (actual['image_sha256']!=hashlib.sha256(data).hexdigest()
                or actual['fixture_sha256']!=hashlib.sha256(fixture).hexdigest()):
            raise ValueError('the coherent image or fixture changes undeclared bytes')
        if not _sha(actual['elf_sha256']):
            raise ValueError('the coherent execution lacks its compiled ELF identity')
    toolchain=witness['toolchain']
    if (set(toolchain)!={'simulator_version','gcc_version','binaries'}
            or toolchain['simulator_version']!='16.3' or toolchain['gcc_version']!='13.3.0'
            or set(toolchain['binaries'])!={'as','ld','objcopy','gcc','run'}
            or not all(_sha(value) for value in toolchain['binaries'].values())):
        raise ValueError('the coherent execution has another GNU toolchain')


def _sha(value):
    return type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def scope_digest(model):
    """Bind every incident fact of the registered members and both callers."""
    from pathlib import Path
    from kb import convert
    if any(not hasattr(model, name) for name in
           ('layouts','spaces','functions','config','overlay','names')):
        raise ValueError('the coherent scope requires a complete native model')
    for path in model.overlay:
        path=Path(path)
        if path.is_absolute() or '..' in path.parts or (
                (not path.parts or path.parts[0]!='kb') and path!=repo.OWNER_CONFIG):
            raise ValueError('an overlay changes coherent execution inputs')
    meanings={FUNCTION_MEANING:model.symbols[FUNCTION].meaning}
    for row in MEMBERS:
        symbol=model.symbols[SymbolKey('7mfk','ram',row[0])]
        member(model,symbol,row=row)
        link(model,symbol,row)
        meanings[row[2]]=symbol.meaning
        function,meaning=parent(row)
        meanings[meaning]=model.symbols[function].meaning
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




def failure(evidence, symbol=None, model=None, claim=None, *, record=None):
    try:
        row=member(model,symbol,evidence=evidence)
        if common.encode(evidence)!=common.encode(member_item(row)):
            return 'the coherent copy requires its exact typed evidence scope'
        if claim!='identity' and (getattr(claim,'name',None)!='identity'
                or getattr(claim,'subject',None) not in (symbol.key.key,row[2],row[2].rsplit('/',1)[0])):
            return 'the coherent copy requires identity-claim context'
        relation=link(model,symbol,row)
        if sum(common.encode(item)==common.encode(evidence) for item in relation.evidence)!=1:
            return 'the coherent copy requires its unique owning link evidence'
        # Both copy domains are bound to the same original full primary terminal.
        can_reader=model.symbols[SymbolKey('7mfk','ram',common.MEMBERS['reader'][1])]
        return common.failure(common.item('reader'),can_reader,model,'identity',record=record)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):
        return 'missing or invalid qualified coherent execution context'


def accepted(model,symbol,function,claim):
    if symbol.key not in MEMBER_KEYS:
        return None
    entries=[entry for entry in claim['evidence'] if registered(entry,symbol)]
    if len(entries)!=1 or failure(entries[0],symbol,model,'identity') is not None:
        return None
    row=member(model,symbol,evidence=entries[0])
    if function.key!=parent(row)[0]:
        return None
    if claim!=common.claim_fields(link(model,symbol,row),'7mfk'):
        return None
    return dict(proof=KEY,callsite=f'7mfk:{row[6]:08x}',scope='bounded-copy' if row[7]=='copy' else 'bounded-word-lane',support='identity')


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
        entries=[entry for entry in claim['evidence'] if registered(entry)]
        if len(entries)!=1:
            return False
        row=member(after,symbol,evidence=entries[0])
        proof=member_item(row)
        if claim['evidence']!=[*old_claim['evidence'],proof] or {**claim,'evidence':old_claim['evidence']}!=old_claim:
            return False
        original=before.symbols[symbol.key]
        member(before,original,row=row)
        if scope_digest(before)!=scope_digest(after):
            return False
        return accepted(after,symbol,function,claim) is not None
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return False
