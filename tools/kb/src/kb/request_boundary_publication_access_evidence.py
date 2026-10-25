"""Owning identity support for one complete actual delegated word writer."""
import hashlib,json
from pathlib import Path
from kb import copy_evidence,store,test_contract
from kb import request_boundary_publication_access_contract as contract
from kb import request_boundary_publication_capture_evidence as capture
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state
from kb.model import SymbolKey
COMPONENTS={'request_boundary_publication_paths':capture}

def native_rows(model):
    declared=contract.descriptor(model.root);row=declared['reference'][0]
    symbol=model.symbols.get(contract.symbol_key(row))
    if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
            or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(16,None))
            or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
        raise ValueError('the delegated writer changes an exact owner, retained width, absent signedness or symbol evidence')
    for function in declared['retained_functions']:
        selected=model.symbols.get(SymbolKey('7mfk','fn',function['address']))
        if (selected is None or selected.meaning is None or selected.meaning.key!=function['owner']
                or not test_contract.exact(store.load(model.root,Path(function['source']),model.overlay),json.loads(function['native_json']))):
            raise ValueError('the delegated writer changes complete retained natural function facts')
    document=store.load(model.root,Path(row['source']),model.overlay)
    matches=[phase for phase in ('original','proposed') if test_contract.exact(document,json.loads(row[phase+'_native_json']))]
    if len(matches)!=1:raise ValueError('the delegated writer changes complete retained native owner facts')
    ledger=json.loads(row['original_ledger_json'])
    if (ledger is None and any(f'{name}/{kind}'==row['owner'] for kind,name,_,_ in model.stash.get('ledger_rows',()))
            or ledger is not None and not test_contract.exact(native_ledger(model,row['owner']),ledger)):
        raise ValueError('the delegated writer changes a retained ledger selector, evidence or TEST position')
    links=[link for link in model.links if contract.original(row,link) or contract.qualified(row,link)]
    if len(links)!=1:raise ValueError('the delegated writer loses or duplicates its retained original relation')
    return [row]

def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    result=capture.require_primary(model,record)
    if result.get('exact_delegated_request_publication') is not True:
        raise ValueError('the delegated writer proof lacks complete actual delegated writer admission')
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/request_boundary_publication_access_contract.py',
            'tools/kb/src/kb/request_boundary_publication_access_evidence.py','tools/kb/src/kb/request_boundary_publication_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256((Path(model.root)/path).read_bytes()).hexdigest():
            raise ValueError('the delegated writer owning source differs from its original complete primary snapshot')
    return dict(scope='exact-delegated-request-publication',components={'request_boundary_publication_paths':result},
        original_claims={rows[0]['id']:rows[0]['original_claim_sha256']},native_model=record['native_model'],
        original_process_sha256=record['process_sha256'],scale_admission=False,units_admission=False,
        native_geometry_inference=False,natural_scheduling_inference=False,hardware_qualification=False)
def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the delegated writer proof changes native, physical or TEST state during admission')
    return result
def owning_row(evidence,symbol,model,claim):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the delegated writer proof requires its exact owning model and symbol')
    if claim!='identity' and (getattr(claim,'name',None)!='identity' or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the delegated writer proof supports only its exact conditional identity association')
    row=native_rows(model)[0]
    if symbol.key!=contract.symbol_key(row) or not test_contract.exact(evidence,contract.item(row)):
        raise ValueError('the delegated writer proof changes its one exact owning attachment')
    attached=[link for link in model.links for item in link.evidence if test_contract.exact(item,evidence)]
    if len(attached)!=1 or attached[0].owner is not symbol.meaning or not contract.qualified(row,attached[0]):
        raise ValueError('the delegated writer proof requires its unique complete qualified owning relation')
    return row
def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:owning_row(evidence,symbol,model,claim);require_current(model);return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return 'missing or invalid exact conditional quantity execution context'
def accepted(model,symbol,function,claim):
    try:
        row=native_rows(model)[0]
        if (not test_contract.exact(contract.plain(claim),json.loads(row['proposed_claim_json']))
                or function.key!=SymbolKey('7mfk','fn',row['function']) or function.meaning.key!='request_boundary_dispatch/fn'
                or failure(contract.item(row),symbol,model,'identity') is not None):return None
        return dict(proof=contract.PREFIX+row['id'],callsite='7mfk:00079dd8',scope=contract.item(row)['value']['scope'],support='identity')
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return None
def link_failure(model,link):
    if not contract.looks_like_access(link):return None
    entries=[e for e in link.evidence if contract.registered(e)]
    if len(entries)!=1:return 'the conditional quantity relation lacks its one exact owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')
def identity_only(symbol):return symbol is not None and symbol.meaning is not None and any(contract.looks_like_access(link) for link in symbol.meaning.links)
