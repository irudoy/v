"""Conditional ROM-to-RAM-to-DID admission from one complete original primary.

The admitted dependencies establish selected software paths. They establish
neither a ROM read by the diagnostic publisher nor units, all operating modes,
natural scheduling, stock scheduler effects, or hardware behavior.
"""

from copy import deepcopy
import hashlib
import json
from weakref import WeakKeyDictionary

from kb import copy_evidence, ignition_literal_evidence, sid22_evidence, test_contract
from kb import diagnostic_rom_contract as contract
from kb import byte_surface_capture_evidence as surface
from kb import exhaust_target_capture_evidence as exhaust
from kb import bfs_path_capture_evidence as bfs
from kb import ignition_diagnostic_capture_evidence as ignition
from kb.model import SymbolKey

COMPONENTS=(('byte_surface_paths',surface),('exhaust_target_paths',exhaust),
    ('bfs_paths',bfs),('ignition_diagnostic_paths',ignition))
_ACCEPTED=WeakKeyDictionary()


def same(actual,expected,reason):
    if not test_contract.exact(actual,expected):
        raise ValueError(reason)


def native_rows(model):
    """Bind complete claims and owners without assuming dependency admission."""
    declared=contract.descriptor(model.root)
    for row in declared['reference']:
        for kind,address,owner in (('tbl',row['address'],row['owner']),
                ('ram',row['RAM_address'],row['RAM_owner'])):
            symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
            if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
                raise ValueError('a diagnostic dependency changes an exact table or RAM owner')
        candidates=[link for link in model.links if link.owner.key==row['owner'] and (
            link.type=='reader' and link.to.key==declared['publisher']
            or link.type=='depends' and link.to.key==row['RAM_owner']
            or contract.looks_like_dependency(link))]
        if len(candidates)!=1 or not (contract.original(row,candidates[0]) or contract.dependency(row,candidates[0])):
            raise ValueError('a diagnostic dependency lacks its one complete original or replacement claim')
        state='original_ledger_json' if contract.original(row,candidates[0]) else 'proposed_ledger_json'
        same(contract.native_ledger(model,row['owner']),json.loads(row[state]),
            'a diagnostic dependency changes an original ledger selector, row or evidence position')
    return declared


def require_sid22(model,declared,record,primary):
    """Keep RAM reader identities and every existing DID SOURCE slot intact."""
    same(record['terminal'],primary['terminal'],'the diagnostic dependency combines different original terminals')
    for key in ('process_path','process_sha256','native_model'):
        same(record[key],primary[key],'the diagnostic dependency combines different original executions or native snapshots')
    descriptor=sid22_evidence.descriptor(model.root)
    first=declared['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','ram',first['RAM_address'])]
    failure=sid22_evidence.failure(sid22_evidence.item(first['RAM_owner']),symbol,model,'identity',record=record)
    if failure:
        raise ValueError(failure)
    result={}
    for row in declared['reference']:
        symbol=model.symbols[SymbolKey('7mfk','ram',row['RAM_address'])]
        member=sid22_evidence.validate_item(sid22_evidence.item(row['RAM_owner']),symbol,model,
            'identity',contract=descriptor)
        if (member.claim_sha256!=row['RAM_reader_claim_sha256']
                or not test_contract.exact(member.declared_width,row['RAM_width'])):
            raise ValueError('the diagnostic dependency changes its complete RAM reader or width')
        bindings=[entry for entry in descriptor.bindings if entry.member==row['RAM_owner']]
        if sorted(entry.did for entry in bindings)!=sorted(row['dids']):
            raise ValueError('the diagnostic dependency changes its exact RAM-source diagnostic aliases')
        addresses=tuple(row['RAM_address']+index for index in range(row['RAM_width']//8))
        if any(entry.read_addresses!=addresses for entry in bindings):
            raise ValueError('the diagnostic dependency does not terminate at the actual DID source bytes')
        result[row['id']]=dict(member=member.meaning,claim_sha256=member.claim_sha256,
            bindings=[dict(did=entry.did,record=entry.record,offset=entry.source_offset,
                addresses=list(entry.read_addresses)) for entry in bindings])
    return result


def require_exhaust_bridge(surface_packet,exhaust_packet):
    """Compose separately observed entries by equality of all RAM bytes.

    Full-state/numeric consumers must validate both originals before this
    composition is used. Registers and frames remain explicit independent
    entry premises; no natural call or scheduling edge is inferred.
    """
    left=surface.observations(surface_packet,surface_packet['declaration'])
    right=exhaust.observations(exhaust_packet,exhaust_packet['declaration'])
    pairs=[]
    used=set()
    expected={(cold,main,selected) for cold,main in ((150,160),(151,180)) for selected in (0,1)}
    for case,observed in zip(surface_packet['declaration']['cases'],left):
        if case['bridge']!=1:
            continue
        if case['kind']!='caller' or case['entry']!=0xBFDC0:
            raise ValueError('the diagnostic bridge starts outside the actual surface caller')
        memory=observed['memory_after'][0]
        cold,main,selected=memory[0x1C5F],memory[0x1C5D],case['bridge_selected']
        key=cold,main,selected
        if key not in expected or key in used:
            raise ValueError('the diagnostic bridge repeats or changes a directed surface result')
        matches=[(target,following) for target,following in zip(exhaust_packet['declaration']['cases'],right)
            if target['bridge']==1 and target['kind']=='conditioned' and target['mode']==0
            and (target['cold'],target['main'],target['selected'])==key]
        if len(matches)!=1:
            raise ValueError('the diagnostic bridge lacks its unique selected exhaust endpoint')
        target,following=matches[0]
        if (memory!=following['memory_before'][0] or len(memory)!=65536
                or following['entry']!=0xBFE88
                or following['memory_after'][0][0x2327]!=(cold if selected==0 else main)):
            raise ValueError('the diagnostic bridge resets or substitutes RAM between observed entries')
        used.add(key)
        pairs.append(dict(surface_index=case['index'],exhaust_index=target['index'],selected=selected,
            cold=cold,main=main,output=following['memory_after'][0][0x2327],
            shared_RAM_sha256=hashlib.sha256(memory).hexdigest()))
    if used!=expected or sum(case['bridge']==1 for case in exhaust_packet['declaration']['cases'])!=len(expected):
        raise ValueError('the diagnostic bridge omits or duplicates a conditional composition')
    return pairs


def require_primary(model,record=None,sid22_record=None):
    """Consume existing COPY and SID22 records; publish no additional receipt."""
    declared=native_rows(model)
    if record is None:
        record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    if sid22_record is None:
        sid22_record=json.loads(copy_evidence._read(model.root,sid22_evidence.RECEIPT))
    original,current=ignition_literal_evidence.require_original(model,record)
    candidate=record['candidate']
    results={}
    for key,consumer in COMPONENTS:
        packet=candidate['witness'][key]
        results[key]=consumer.require_witness(model,packet,candidate['producer_inputs'])
        if original.count(packet['marker'])!=1:
            raise ValueError('the diagnostic dependency lacks a unique component in the complete original primary')
        if results[key]['image_sha256']!=declared['image_sha256']:
            raise ValueError('the diagnostic dependency composes executions of different owned ROM images')
    diagnostic=require_sid22(model,declared,sid22_record,record)
    bridge=require_exhaust_bridge(candidate['witness']['byte_surface_paths'],candidate['witness']['exhaust_target_paths'])
    positive=[row for row in results['bfs_paths']['semantic_results'] if row['conditional_positive_path']]
    if len({row['output'] for row in positive})<2:
        raise ValueError('the diagnostic dependency lacks distinct K-dependent BFS outputs')
    normal=[row for row in results['ignition_diagnostic_paths']['semantic_results']
        if row['stage']==2 and row['conditional_positive_path']]
    if len({row['output'] for row in normal})<2:
        raise ValueError('the diagnostic dependency lacks distinct sequenced ignition command outputs')
    if candidate['producer_inputs'].get(contract.DESCRIPTOR)!=hashlib.sha256(
            copy_evidence._read(model.root,contract.DESCRIPTOR)).hexdigest():
        raise ValueError('the diagnostic dependency differs from its original complete producer input')
    same(ignition_literal_evidence.execution_inputs(model.root),current,
        'the diagnostic dependency executable inputs change during independent consumption')
    return dict(proof=contract.KEY,scope='conditional-diagnostic-output',
        original_process_sha256=record['process_sha256'],native_model=record['native_model'],
        components=results,exhaust_bridge=bridge,diagnostic=diagnostic,
        physical_reader_inference=False,universal_no_ROM_read=False,scale_admission=False,
        all_modes=False,natural_scheduling_inference=False,hardware_qualification=False)


def owning_row(evidence,symbol,model,claim='identity'):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or symbol.meaning is None):
        raise ValueError('the diagnostic dependency needs its actual identity claim and owning model')
    if claim!='identity' and (getattr(claim,'name',None)!='identity'
            or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,
                symbol.meaning.key.rsplit('/',1)[0])):
        raise ValueError('the diagnostic dependency admits its owning identity claim only')
    declared=contract.descriptor(model.root)
    rows=[row for row in declared['reference'] if symbol.key==SymbolKey('7mfk','tbl',row['address'])
        and symbol.meaning.key==row['owner']]
    if len(rows)!=1 or not test_contract.exact(evidence,contract.item(rows[0])):
        raise ValueError('the diagnostic dependency proof changes its exact item, owner, address or scope')
    row=rows[0]
    attached=[(link,item) for link in model.links for item in link.evidence if contract.registered(item)
        and link.owner is symbol.meaning]
    if (len(attached)!=1 or not contract.dependency(row,attached[0][0])
            or not test_contract.exact(attached[0][1],evidence)
            or any(contract.registered(item) for item in symbol.evidence)):
        raise ValueError('the diagnostic dependency proof has no unique exact owning relation')
    return row


def dependency_state(model):
    """Cache identity only; independent admission never accepts this digest."""
    from kb import convert,write
    return contract.digest(test_contract.encode(dict(native=convert.dump(model),
        publication=write.publication_view(model),overlay=model.overlay,
        groups={meaning.key:meaning.groups for meaning in model.meanings},
        config=model.config,layouts=model.layouts,spaces=model.spaces,functions=model.functions,
        links=[contract.canonical(link) for link in model.links],
        execution=ignition_literal_evidence.execution_inputs(model.root),
        physical=copy_evidence.inputs(model.root),
        receipts=(copy_evidence.proof_state(model.root),copy_evidence.proof_state(model.root,live=True)))))


def require_current(model):
    """Reuse admission only while all native, physical and original bytes agree."""
    before=dependency_state(model)
    held=_ACCEPTED.get(model)
    if held is not None and held[0]==before:
        return deepcopy(held[1])
    result=require_primary(model)
    if dependency_state(model)!=before:
        raise ValueError('the diagnostic dependency changes during independent admission')
    _ACCEPTED[model]=before,deepcopy(result)
    return result


def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):
        return None
    try:
        owning_row(evidence,symbol,model,claim)
        require_current(model)
        return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):
        return 'missing or invalid complete diagnostic ROM dependency execution context'


def link_failure(model,link):
    """A relation cannot donate a level through its unqualified structure."""
    if not contract.looks_like_dependency(link):
        return None
    symbol=link.owner.symbols.get('7mfk')
    entries=[entry for entry in link.evidence if contract.registered(entry)]
    if len(entries)!=1:
        return 'the conditional diagnostic dependency lacks its one exact qualified proof'
    return failure(entries[0],symbol,model,'identity')


def identity_only(symbol):
    return symbol is not None and symbol.layout=='7mfk' and symbol.meaning is not None and any(
        link.owner is symbol.meaning and contract.looks_like_dependency(link)
        for link in symbol.meaning.links)
