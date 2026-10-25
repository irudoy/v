"""Owning identity support for three exact indexed trim accesses with complete native preservation."""
import hashlib
import json
from pathlib import Path
from kb import copy_evidence, store, test_contract
from kb import ltft_adjustment_update_access_contract as contract
from kb import ltft_adjustment_update_capture_evidence as capture
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state
from kb.model import SymbolKey
COMPONENTS={'ltft_adjustment_update_paths':capture}

def native_rows(model):
    declared=contract.descriptor(model.root);rows=declared['reference'];phases=set()
    for retained in declared['retained_functions']:
        symbol=model.symbols.get(SymbolKey('7mfk','fn',retained['address']))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=retained['owner']
                or not test_contract.exact(store.load(model.root,Path(retained['source']),model.overlay),json.loads(retained['native_json']))):
            raise ValueError('the trim proof changes complete retained function, uncertainty or ledger facts')
    for row in rows:
        symbol=model.symbols.get(contract.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(16,None))
                or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('the trim proof changes an exact owner, native width, signedness or symbol evidence')
        document=store.load(model.root,Path(row['source']),model.overlay)
        matches=[phase for phase in ('original','proposed') if test_contract.exact(document,json.loads(row[phase+'_native_json']))]
        if len(matches)!=1:
            raise ValueError('the trim proof changes complete native owner facts outside its finite known composition')
        phases.add(matches[0])
        ledger=json.loads(row['original_ledger_json'])
        if (ledger is None and any(f'{name}/{kind}'==row['owner'] for kind,name,_,_ in model.stash.get('ledger_rows',()))
                or ledger is not None and not test_contract.exact(native_ledger(model,row['owner']),ledger)):
            raise ValueError('the trim proof changes a retained ledger selector or evidence/TEST position')
        links=[link for link in model.links if contract.original(row,link) or contract.qualified(row,link)]
        if len(links)!=1:
            raise ValueError('the trim proof loses or duplicates one exact original relation')
    if len(phases)!=1:
        raise ValueError('the trim proof requires one complete common before or nine-evidence after phase')
    phase=next(iter(phases))
    for companion in declared['companions']:
        wanted=json.loads(companion[phase+'_claim_json'])
        if sum(test_contract.exact(contract.canonical(link),wanted) for link in model.links)!=1:
            raise ValueError('the trim proof changes or partially attaches a finite known existing companion')
    return rows

def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    result=capture.require_primary(model,record)
    if result.get('exact_ltft_adjustment_update') is not True:
        raise ValueError('the trim proof lacks complete independent updater admission')
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/ltft_adjustment_update_access_contract.py',
            'tools/kb/src/kb/ltft_adjustment_update_access_evidence.py','tools/kb/src/kb/ltft_adjustment_update_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256((Path(model.root)/path).read_bytes()).hexdigest():
            raise ValueError('the trim owning source differs from its complete original primary snapshot')
    return dict(scope='exact-index1-ltft-adjustment-update',components={'ltft_adjustment_update_paths':result},
        original_claims={row['id']:row['original_claim_sha256'] for row in rows},native_model=record['native_model'],
        original_process_sha256=record['process_sha256'],scale_admission=False,units_admission=False,
        native_geometry_inference=False,natural_scheduling_inference=False,hardware_qualification=False)
def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the trim proof changes native, physical or TEST state during admission')
    return result
def owning_row(evidence,symbol,model,claim):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the trim proof requires its exact owning model and symbol')
    if claim!='identity' and (getattr(claim,'name',None)!='identity' or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the trim proof supports only its exact owning identity relation')
    selected=[row for row in native_rows(model) if symbol.key==contract.symbol_key(row) and test_contract.exact(evidence,contract.item(row))]
    if len(selected)!=1:raise ValueError('the trim proof changes an exact owning evidence attachment')
    row=selected[0];attached=[link for link in model.links for item in link.evidence if test_contract.exact(item,evidence)]
    if len(attached)!=1 or attached[0].owner is not symbol.meaning or not contract.qualified(row,attached[0]):
        raise ValueError('the trim proof requires a unique exact qualified owning relation')
    return row
def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:owning_row(evidence,symbol,model,claim);require_current(model);return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return 'missing or invalid exact indexed trim execution context'
def accepted(model,symbol,function,claim):
    try:
        selected=[row for row in native_rows(model) if test_contract.exact(contract.plain(claim),json.loads(row['proposed_claim_json']))]
        if (len(selected)!=1 or function.key!=SymbolKey('7mfk','fn',0x58168) or function.meaning.key!='pretty-mongrel/fn'
                or failure(contract.item(selected[0]),symbol,model,'identity') is not None):return None
        row=selected[0]
        return dict(proof=contract.PREFIX+row['id'],callsite=f'7mfk:{row["sites"][0]:08x}',scope=contract.item(row)['value']['scope'],support='identity')
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return None
def link_failure(model,link):
    if not contract.looks_like_access(link):return None
    entries=[item for item in link.evidence if contract.registered(item)]
    if len(entries)!=1:return 'the indexed trim relation lacks its one exact owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')
def identity_only(symbol):return symbol is not None and symbol.meaning is not None and any(contract.looks_like_access(link) for link in symbol.meaning.links)
