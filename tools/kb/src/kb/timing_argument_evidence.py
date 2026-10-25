"""Conditional value arguments require one complete original natural execution."""

from copy import deepcopy
import hashlib,json
from weakref import WeakKeyDictionary
from kb import copy_evidence,ignition_literal_evidence,test_contract
from kb import timing_argument_contract as contract
from kb import timing_division_capture_evidence as caller,division_callees_capture_evidence as callees
from kb import timing_tail_capture_evidence as tail
from kb.model import SymbolKey

_ACCEPTED=WeakKeyDictionary()


def native_rows(model):
    declared=contract.descriptor(model.root)
    target=model.symbols.get(contract.FUNCTION)
    if target is None or target.meaning is None or target.meaning.key!=contract.TARGET:
        raise ValueError('the timing argument lacks its exact arithmetic callee identity')
    for row in declared['reference']:
        symbol=model.symbols.get(SymbolKey('7mfk','tbl',row['address']))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']:
            raise ValueError('the timing argument changes its exact calibration owner')
        links=[link for link in model.links if link.owner is symbol.meaning and
            (link.type=='reader' and link.to.key==contract.TARGET or contract.looks_like_dependency(link))]
        if len(links)!=1 or not (contract.original(row,links[0]) or contract.dependency(row,links[0])):
            raise ValueError('the timing argument needs its one complete original or replacement claim')
        key='original_ledger_json' if contract.original(row,links[0]) else 'proposed_ledger_json'
        if not test_contract.exact(contract.native_ledger(model,row['owner']),json.loads(row[key])):
            raise ValueError('the timing argument changes an original ledger row, selector or evidence position')
    return declared


def require_primary(model,record=None):
    declared=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    original,current=ignition_literal_evidence.require_original(model,record)
    candidate=record['candidate'];results={}
    for key,consumer in (('timing_division_paths',caller),('timing_tail_paths',tail),('division_callees_paths',callees)):
        packet=candidate['witness'][key]
        result=consumer.require_witness(model,packet,candidate['producer_inputs'])
        if original.count(packet['marker'])!=1 or result['image_sha256']!=declared['image_sha256']:
            raise ValueError('the timing argument combines different original executions or image identities')
        results[key]=result
    if candidate['producer_inputs'].get(contract.DESCRIPTOR)!=hashlib.sha256(
            copy_evidence._read(model.root,contract.DESCRIPTOR)).hexdigest():
        raise ValueError('the timing argument differs from the original complete producer input')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the timing argument source closure changes during independent consumption')
    return dict(proof=contract.KEY,scope='conditional-timing-argument',components=results,
        original_process_sha256=record['process_sha256'],native_model=record['native_model'],
        bounded_argument_lineage=True,physical_reader_inference=False,scale_admission=False,
        natural_scheduling_inference=False,hardware_qualification=False)


def owning_row(evidence,symbol,model,claim='identity'):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the timing argument needs its actual owning model and identity claim')
    if claim!='identity' and (getattr(claim,'name',None)!='identity'
            or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the timing argument supplies its owning identity only')
    rows=[row for row in contract.descriptor(model.root)['reference']
        if symbol.key==SymbolKey('7mfk','tbl',row['address']) and symbol.meaning.key==row['owner']]
    if len(rows)!=1 or not test_contract.exact(evidence,contract.item(rows[0])):
        raise ValueError('the timing argument changes its complete proof, owner or symbol')
    row=rows[0]
    attached=[(link,item) for link in model.links if link.owner is symbol.meaning
        for item in link.evidence if contract.registered(item)]
    if (len(attached)!=1 or not contract.dependency(row,attached[0][0])
            or not test_contract.exact(attached[0][1],evidence)
            or any(contract.registered(item) for item in symbol.evidence)):
        raise ValueError('the timing argument has no unique complete owning dependency')
    return row


def dependency_state(model):
    from kb.diagnostic_rom_evidence import dependency_state as complete_state
    return complete_state(model)


def require_current(model):
    before=dependency_state(model);held=_ACCEPTED.get(model)
    if held is not None and held[0]==before:return deepcopy(held[1])
    result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the timing argument changes during independent admission')
    _ACCEPTED[model]=before,deepcopy(result)
    return result


def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:
        owning_row(evidence,symbol,model,claim);require_current(model)
        return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):
        return 'missing or invalid complete timing argument execution context'


def link_failure(model,link):
    if not contract.looks_like_dependency(link):return None
    entries=[item for item in link.evidence if contract.registered(item)]
    if len(entries)!=1:return 'the timing argument lacks its one complete qualified owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')


def identity_only(symbol):
    return symbol is not None and symbol.layout=='7mfk' and symbol.meaning is not None and any(
        link.owner is symbol.meaning and contract.looks_like_dependency(link) for link in symbol.meaning.links)
