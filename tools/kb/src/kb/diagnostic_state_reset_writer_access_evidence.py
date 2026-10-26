"""Owning identity support for the complete constant-zero diagnostic reset writer."""
import hashlib,json
from pathlib import Path
from kb import copy_evidence,store,test_contract
from kb import diagnostic_state_reset_writer_access_contract as contract
from kb import diagnostic_state_reset_writer_capture_evidence as capture
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state
from kb.model import SymbolKey
COMPONENTS={'diagnostic_state_reset_writer_paths':capture}

def native_rows(model):
    declared=contract.descriptor(model.root);rows=declared['reference']
    for row in rows:
        symbol=model.symbols.get(contract.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (contract.native_type(row,'width'),contract.native_type(row,'signed')))
                or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('the reset writers change an exact owner, retained native type or symbol evidence')
        document=store.load(model.root,Path(row['source']),model.overlay)
        phases=[phase for phase in ('original','proposed') if test_contract.exact(document,json.loads(row[phase+'_native_json']))]
        if len(phases)!=1:raise ValueError('the reset writers change complete owner facts outside their exact appends')
        if not test_contract.exact(native_ledger(model,row['owner']),json.loads(row['original_ledger_json'])):
            raise ValueError('the reset writers change a complete retained owner ledger or TEST position')
        if sum(contract.original(row,link) or contract.qualified(row,link) for link in model.links)!=1:
            raise ValueError('the reset writers lose or duplicate an exact original association')
    for retained in declared['retained_functions']:
        function=model.symbols.get(SymbolKey('7mfk','fn',retained['address']))
        if (function is None or function.meaning is None or function.meaning.key!=retained['owner']
                or not test_contract.exact(store.load(model.root,Path(retained['source']),model.overlay),json.loads(retained['native_json']))):
            raise ValueError('the reset writers change a complete retained function or its ledger')
    return rows


def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    result=capture.require_primary(model,record)
    for row in rows:require_result(result,row)
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/diagnostic_state_reset_writer_access_contract.py',
            'tools/kb/src/kb/diagnostic_state_reset_writer_access_evidence.py','tools/kb/src/kb/diagnostic_state_reset_writer_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256((Path(model.root)/path).read_bytes()).hexdigest():
            raise ValueError('the reset writer owning source differs from its original complete primary snapshot')
    return dict(scope='exact-diagnostic-state-reset-writer',components={'diagnostic_state_reset_writer_paths':result},
        original_claims={row['id']:row['original_claim_sha256'] for row in rows},native_model=record['native_model'],
        original_process_sha256=record['process_sha256'],scale_admission=False,units_admission=False,
        native_geometry_inference=False,natural_scheduling_inference=False,hardware_qualification=False)
def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the reset writer proof changes native, physical or TEST state during admission')
    return result
def owning_row(evidence,symbol,model,claim):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the reset writer proof requires its exact owning model and symbol')
    if claim!='identity' and (getattr(claim,'name',None)!='identity' or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the reset writer proof supports only its exact indexed writer identity')
    selected=[row for row in native_rows(model) if symbol.key==contract.symbol_key(row) and test_contract.exact(evidence,contract.item(row))]
    if len(selected)!=1:
        raise ValueError('the reset writer proof changes its one exact owning attachment')
    row=selected[0]
    attached=[link for link in model.links for item in link.evidence if test_contract.exact(item,evidence)]
    if len(attached)!=1 or attached[0].owner is not symbol.meaning or not contract.qualified(row,attached[0]):
        raise ValueError('the reset writer proof requires its unique complete qualified owning relation')
    return row
def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:owning_row(evidence,symbol,model,claim);require_current(model);return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return 'missing or invalid exact diagnostic reset writer execution context'
def accepted(model,symbol,function,claim):
    try:
        selected=[row for row in native_rows(model) if row['function']==function.key.address and symbol.key==contract.symbol_key(row)]
        if len(selected)!=1:return None
        row=selected[0]
        if (not test_contract.exact(contract.plain(claim),json.loads(row['proposed_claim_json']))
                or function.key!=SymbolKey('7mfk','fn',row['function']) or function.meaning.key!=json.loads(row['original_claim_json'])['to']
                or failure(contract.item(row),symbol,model,'identity') is not None):return None
        return dict(proof=contract.PREFIX+row['id'],callsite=f"7mfk:{row['sites'][-1]:08x}",scope=contract.item(row)['value']['scope'],support='identity')
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return None
def link_failure(model,link):
    if not contract.looks_like_access(link):return None
    entries=[e for e in link.evidence if contract.registered(e)]
    if len(entries)!=1:return 'the diagnostic reset writer relation lacks its one exact owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')
def identity_only(symbol):return symbol is not None and symbol.meaning is not None and any(contract.looks_like_access(link) for link in symbol.meaning.links)


REQUIRED_FLAGS=('exact_diagnostic_state_reset_writer_paths',*capture.OWNING_FLAGS)
NON_ADMISSIONS=('native_identity_admission','native_geometry_inference','scale_admission','units_admission',
    'natural_caller_reachability','natural_scheduling_inference','hardware_qualification','peripheral_side_effects_admission')

def require_result(result,row):
    if (type(result) is not dict or any(result.get(flag) is not True for flag in REQUIRED_FLAGS)
            or any(result.get(flag) is not False for flag in NON_ADMISSIONS)
            or not test_contract.exact(result.get('causal_inputs'),dict(raw_rom_8dfc=True,raw_rom_8dfd=True))
            or not test_contract.exact(result.get('constant_writer_inputs'),dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True))):
        raise ValueError('the reset owning boundary lacks complete exact native-bank,SR/frame/call,constant-zero or actual raw-ROM writer admission')
    expected=[dict(symbol=f"7mfk-{selected['address']:08x}/ram",meaning=selected['owner'],
        function=f"7mfk-{selected['function']:08x}/fn",function_meaning=json.loads(selected['original_claim_json'])['to'],
        original_claim_sha256=selected['original_claim_sha256']) for selected in contract.descriptor(Path(__file__).resolve().parents[4])['reference']]
    if not test_contract.exact(result.get('native_bindings'),expected):
        raise ValueError('the reset owning boundary substitutes the exact99DE writer original or complete function')
    from kb import diagnostic_reset_helper_writer_capture_evidence as helper_capture
    helper_capture.require_result(result)
    return True
