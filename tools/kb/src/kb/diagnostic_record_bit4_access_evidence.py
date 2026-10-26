"""Owning identity support for exact indexed diagnostic-record writers and composite reader."""
import hashlib,json
from pathlib import Path
from kb import copy_evidence,store,test_contract
from kb import diagnostic_record_bit4_access_contract as contract
from kb import diagnostic_record_bit4_capture_evidence as capture
from kb import diagnostic_record_bits3_6_capture_evidence as bits3_6_capture
from kb import diagnostic_record_composite_gate_capture_evidence as composite_capture
from kb import diagnostic_record_highbit_clear_capture_evidence as highbit_clear_capture
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state
from kb.model import SymbolKey
COMPONENTS={'diagnostic_record_bit4_paths':capture,'diagnostic_record_bits3_6_paths':bits3_6_capture,'diagnostic_record_composite_gate_paths':composite_capture,'diagnostic_record_highbit_clear_paths':highbit_clear_capture}

def native_rows(model):
    declared=contract.descriptor(model.root);rows=declared['reference'];row=rows[0]
    symbol=model.symbols.get(contract.symbol_key(row))
    if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
            or not test_contract.exact((symbol.value('width'),symbol.value('signed')),(8,False))
            or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
        raise ValueError('the diagnostic writers change their exact owner, unsigned byte type or original symbol evidence')
    document=store.load(model.root,Path(row['source']),model.overlay)
    phases=[phase for phase in ('original','proposed') if test_contract.exact(document,json.loads(row[phase+'_native_json']))]
    if len(phases)!=1:raise ValueError('the diagnostic writers change complete shared owner facts outside their exact owning appends')
    for retained in declared['retained_functions']:
        function=model.symbols.get(SymbolKey('7mfk','fn',retained['address']))
        if (function is None or function.meaning is None or function.meaning.key!=retained['owner']
                or not test_contract.exact(store.load(model.root,Path(retained['source']),model.overlay),json.loads(retained['native_json']))):
            raise ValueError('the diagnostic writers change a complete retained function or its ledger selectors')
    if not test_contract.exact(native_ledger(model,row['owner']),json.loads(row['original_ledger_json'])):
        raise ValueError('the diagnostic writers change complete original ledger or TEST positions')
    for selected in rows:
        if sum(contract.original(selected,link) or contract.qualified(selected,link) for link in model.links)!=1:
            raise ValueError('the diagnostic writer loses or duplicates an exact original association')
    return rows


def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    components={}
    for row in rows:
        result=COMPONENTS[row['component']].require_primary(model,record);require_result(result,row)
        components[row['component']]=result
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/diagnostic_record_bit4_access_contract.py',
            'tools/kb/src/kb/diagnostic_record_bit4_access_evidence.py','tools/kb/src/kb/diagnostic_record_bit4_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256((Path(model.root)/path).read_bytes()).hexdigest():
            raise ValueError('the diagnostic writer owning source differs from the identical complete primary')
    return dict(scope='exact-indexed-diagnostic-record-writers',components=components,
        original_claims={row['id']:row['original_claim_sha256'] for row in rows},native_model=record['native_model'],
        original_process_sha256=record['process_sha256'],scale_admission=False,units_admission=False,
        native_geometry_inference=False,natural_scheduling_inference=False,hardware_qualification=False)
def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the bit4 writer proof changes native, physical or TEST state during admission')
    return result
def owning_row(evidence,symbol,model,claim):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the diagnostic writer requires its exact owning model and symbol')
    if claim!='identity' and (getattr(claim,'name',None)!='identity' or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the diagnostic writer supports only its own exact identity association')
    selected=[row for row in native_rows(model) if symbol.key==contract.symbol_key(row) and test_contract.exact(evidence,contract.item(row))]
    if len(selected)!=1:raise ValueError('the diagnostic writer substitutes its exact owning attachment')
    row=selected[0];attached=[link for link in model.links for item in link.evidence if test_contract.exact(item,evidence)]
    if len(attached)!=1 or attached[0].owner is not symbol.meaning or not contract.qualified(row,attached[0]):
        raise ValueError('the diagnostic writer requires one unique complete qualified original relation')
    return row
def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:owning_row(evidence,symbol,model,claim);require_current(model);return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return 'missing or invalid exact conditional bit4 writer execution context'
def accepted(model,symbol,function,claim):
    try:
        rows=[row for row in native_rows(model) if row['function']==function.key.address]
        if len(rows)!=1:return None
        row=rows[0]
        if (not test_contract.exact(contract.plain(claim),json.loads(row['proposed_claim_json']))
                or function.key!=SymbolKey('7mfk','fn',row['function'])
                or function.meaning.key!=json.loads(row['original_claim_json'])['to']
                or failure(contract.item(row),symbol,model,'identity') is not None):return None
        return dict(proof=contract.PREFIX+row['id'],callsite=f"7mfk:{row['sites'][-1]:08x}",scope=contract.item(row)['value']['scope'],support='identity')
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):return None
def link_failure(model,link):
    if not contract.looks_like_access(link):return None
    entries=[e for e in link.evidence if contract.registered(e)]
    if len(entries)!=1:return 'the conditional bit4 writer relation lacks its one exact owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')
def identity_only(symbol):return symbol is not None and symbol.meaning is not None and any(contract.looks_like_access(link) for link in symbol.meaning.links)


REQUIRED_FLAGS=('exact_diagnostic_record_bit4_paths','complete_indexed_byte_OR_and_RTS_delay',
    'complete_CPU_SR_frame_RAM','complete_physical_member_preimages_and_publications',
    'fixed_other_actual_common_member_alternatives','complete_native_owner_function_TEST_ledger',
    'no_array_extent_inference','no_selected_datum_absence_inference')


def require_result(result,row):
    flags=COMPONENT_FLAGS.get(row['component'])
    if flags is None or type(result) is not dict or any(result.get(flag) is not True for flag in flags):
        raise ValueError('a diagnostic writer lacks complete independent ordered physical, state, actual-byte or native admission')
    expected=[dict(symbol='7mfk-ffff5718/ram',meaning=row['owner'],function=f"7mfk-{row['function']:08x}/fn",
        function_meaning=json.loads(row['original_claim_json'])['to'],original_claim_sha256=row['original_claim_sha256'])]
    if not test_contract.exact(result.get('native_bindings'),expected):
        raise ValueError('a diagnostic writer substitutes its exact original native owner or complete function')
    return True


COMPONENT_FLAGS={'diagnostic_record_bit4_paths':REQUIRED_FLAGS,
    'diagnostic_record_bits3_6_paths':tuple('complete_two_ordered_byte_OR_stages_and_RTS_delay'
        if flag=='complete_indexed_byte_OR_and_RTS_delay' else flag.replace('exact_diagnostic_record_bit4_paths','exact_diagnostic_record_bits3_6_paths')
        for flag in REQUIRED_FLAGS),'diagnostic_record_highbit_clear_paths':('exact_diagnostic_record_highbit_clear_paths', 'complete_AND7F_read_write_RTS_delay', 'complete_sentinel_no_RAM_access', 'complete_full_R4_modulo_addressing', 'complete_CPU_SR_frame_RAM', 'complete_physical_member_preimages_and_publications', 'fixed_other_actual_common_member_alternatives', 'complete_native_owner_function_TEST_ledger', 'no_array_extent_inference', 'no_selected_datum_absence_inference')}


COMPONENT_FLAGS['diagnostic_record_composite_gate_paths']=(
    'exact_diagnostic_record_composite_gate_paths','complete_actual_sentinel_and_short_circuit_calls',
    'complete_nested_indexed_array_reads','complete_CPU_SR_frame_RAM','fixed_other_actual_R0_alternatives',
    'complete_native_owner_function_TEST_ledger','no_array_extent_inference','no_selected_datum_absence_inference')
