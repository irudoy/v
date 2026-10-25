"""Owning identity support for one executed conditional table-derived quantity."""
import hashlib,json
from pathlib import Path
from kb import copy_evidence,store,test_contract
from kb import blend_weight_quantity_access_contract as contract
from kb import blend_weight_quantity_capture_evidence as capture
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state
from kb.model import SymbolKey
COMPONENTS={'blend_weight_quantity_paths':capture}

def native_rows(model):
    declared=contract.descriptor(model.root);row=declared['reference'][0]
    symbol=model.symbols.get(contract.symbol_key(row))
    if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
            or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(None,None))
            or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
        raise ValueError('the shared-weight proof changes its exact owner, unset semantic types or original evidence')
    document=store.load(model.root,Path(row['source']),model.overlay)
    matches=[phase for phase in ('original','proposed') if test_contract.exact(document,json.loads(row[phase+'_native_json']))]
    if len(matches)!=1:
        raise ValueError('the shared-weight proof changes complete owner facts outside its exact append')
    for retained in declared['retained_functions']:
        function=model.symbols.get(SymbolKey('7mfk','fn',retained['address']))
        if (function is None or function.meaning is None or function.meaning.key!=retained['owner']
                or not test_contract.exact(store.load(model.root,Path(retained['source']),model.overlay),json.loads(retained['native_json']))):
            raise ValueError('the shared-weight proof changes a complete retained producer or consumer function')
    ledger=json.loads(row['original_ledger_json'])
    if ledger is not None and not test_contract.exact(native_ledger(model,row['owner']),ledger):
        raise ValueError('the shared-weight proof changes a complete retained ledger, evidence or TEST position')
    links=[link for link in model.links if contract.original(row,link) or contract.qualified(row,link)]
    if len(links)!=1:
        raise ValueError('the shared-weight proof loses or duplicates its original quantity relation')
    return [row]


def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    result=capture.require_primary(model,record)
    if result.get('exact_two_phase_shared_weight_quantity') is not True:
        raise ValueError('the quantity proof lacks complete actual producer-to-consumer admission')
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/blend_weight_quantity_access_contract.py',
            'tools/kb/src/kb/blend_weight_quantity_access_evidence.py','tools/kb/src/kb/blend_weight_quantity_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256((Path(model.root)/path).read_bytes()).hexdigest():
            raise ValueError('the quantity owning source differs from its original complete primary snapshot')
    return dict(scope='exact-two-phase-shared-blend-weight-quantity',components={'blend_weight_quantity_paths':result},
        original_claims={rows[0]['id']:rows[0]['original_claim_sha256']},native_model=record['native_model'],
        original_process_sha256=record['process_sha256'],scale_admission=False,units_admission=False,
        native_geometry_inference=False,natural_scheduling_inference=False,hardware_qualification=False)
def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the quantity proof changes native, physical or TEST state during admission')
    return result
def owning_row(evidence,symbol,model,claim):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the quantity proof requires its exact owning model and symbol')
    if claim!='identity' and (getattr(claim,'name',None)!='identity' or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the quantity proof supports only its exact conditional identity association')
    row=native_rows(model)[0]
    if symbol.key!=contract.symbol_key(row) or not test_contract.exact(evidence,contract.item(row)):
        raise ValueError('the quantity proof changes its one exact owning attachment')
    attached=[link for link in model.links for item in link.evidence if test_contract.exact(item,evidence)]
    if len(attached)!=1 or attached[0].owner is not symbol.meaning or not contract.qualified(row,attached[0]):
        raise ValueError('the quantity proof requires its unique complete qualified owning relation')
    return row
def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:owning_row(evidence,symbol,model,claim);require_current(model);return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return 'missing or invalid exact conditional quantity execution context'
def accepted(model,symbol,function,claim):
    try:
        row=native_rows(model)[0]
        if (not test_contract.exact(contract.plain(claim),json.loads(row['proposed_claim_json']))
                or function.key!=SymbolKey('7mfk','fn',row['function']) or function.meaning.key!='tuscan-vulture/fn'
                or failure(contract.item(row),symbol,model,'identity') is not None):return None
        return dict(proof=contract.PREFIX+row['id'],callsite='7mfk:0007211a',scope=contract.item(row)['value']['scope'],support='identity')
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return None
def link_failure(model,link):
    if not contract.looks_like_access(link):return None
    entries=[e for e in link.evidence if contract.registered(e)]
    if len(entries)!=1:return 'the conditional quantity relation lacks its one exact owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')
def identity_only(symbol):return symbol is not None and symbol.meaning is not None and any(contract.looks_like_access(link) for link in symbol.meaning.links)
