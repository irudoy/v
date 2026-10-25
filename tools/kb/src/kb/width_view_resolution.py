"""Explicit narrow width dispositions backed by independent complete originals.

A diagnostic byte view or a byte counter can coexist with wider instructions
that use the same address. The admitted exception preserves those exact roles
and original questions; it proves no universal storage width, natural caller
range, disjointness, new identity or new access. Raw capture alone is insufficient.
"""

import hashlib
import json
from pathlib import Path
import tomllib

from kb import copy_evidence, ignition_literal_evidence, sid22_evidence, test_contract
from kb import width_view_capture_evidence as physical, width_view_evidence as contract
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.width-dispositions.toml'
KINDS = ('diagnostic-byte-view-with-word-working-access','byte-counter-with-conditional-word-vector-alias')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','scope','disposition'} or type(value['schema']) is not int
            or value['schema']!=1 or value['id']!='jk08a-narrow-width-dispositions'):
        raise ValueError('the width disposition has another exact schema or scope')
    declared=contract.descriptor(root)
    fields={field['symbol']:field for field in declared['field']}
    entries={row['symbol']:row for row in value['disposition']}
    if len(entries)!=len(value['disposition']) or set(entries)!=set(fields):
        raise ValueError('the width disposition omits, adds or repeats an original question')
    false_keys=('native_width_change','identity_grounding','access_grounding','natural_entry_inference',
                'selector_range_inference','zero_index_disjointness','hardware_qualification')
    keys={'symbol','meaning','original_claim_sha256','kind','declared_bits','physical_question_bits',
          'complete_SID22_required','complete_primary_required',*false_keys}
    for symbol,row in entries.items():
        field=fields[symbol]
        diagnostic=field['kind']=='diagnostic-byte-view'
        if (set(row)!=keys or row['meaning']!=field['meaning']
                or row['original_claim_sha256']!=field['original_claim_sha256']
                or row['kind']!=KINDS[0 if diagnostic else 1]
                or not test_contract.exact((row['declared_bits'],row['physical_question_bits']),(8,16))
                or row['complete_SID22_required'] is not diagnostic
                or row['complete_primary_required'] is not True
                or any(row[key] is not False for key in false_keys)):
            raise ValueError('the width disposition changes its original question, semantic byte role or admitted limits')
    return value


def registered_field(root,symbol):
    declared=contract.descriptor(root)
    registered={row['symbol'] for row in descriptor(root)['disposition']}
    matches=[row for row in declared['field'] if row['symbol']==symbol and symbol in registered]
    return matches[0] if len(matches)==1 else None


def require(model,symbol,claim,*,record=None,sid22_record=None):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol:
        raise ValueError('the narrow width disposition requires its actual complete native symbol')
    field=registered_field(model.root,symbol.key.key)
    if field is None:
        raise ValueError('the narrow width disposition does not register this exact symbol')
    contract.bind_fields(model,contract.descriptor(model.root))
    expected=dict(symbol=symbol.key.key,width=field['declared_bits'],
        observed=sorted((row['function'],row['site'],row['mode'],row['width_bytes']) for row in field['observed']))
    if not test_contract.exact(claim,expected):
        raise ValueError('the narrow width disposition receives another retained wider-access question')
    disposition=next(row for row in descriptor(model.root)['disposition'] if row['symbol']==symbol.key.key)
    if record is None:
        record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    if 'width_views' not in record['candidate']['witness']:
        raise ValueError('the narrow width disposition lacks its complete original working-state capture')
    _,current=ignition_literal_evidence.require_original(model,record)
    captured=physical.require_primary(model,record)
    support=captured['fields'].get(symbol.key.key)
    if not support or len(support)!=len(field['observed']) or any(row['physical_width_bytes']!=2 for row in support):
        raise ValueError('the narrow width disposition omits an original exact working instruction')
    diagnostic=None
    if disposition['complete_SID22_required']:
        if sid22_record is None:
            sid22_record=json.loads(copy_evidence._read(model.root,sid22_evidence.RECEIPT))
        failure=sid22_evidence.failure(sid22_evidence.item(field['meaning']),symbol,model,'identity',record=sid22_record)
        if failure:
            raise ValueError(failure)
        if (not test_contract.exact(sid22_record['terminal'],record['terminal'])
                or any(sid22_record[key]!=record[key] for key in ('process_path','process_sha256','native_model'))):
            raise ValueError('the narrow width disposition combines different original executions or native snapshots')
        diagnostic=physical.diagnostic_views(model,sid22_record).get(symbol.key.key)
        if diagnostic is None or diagnostic['response_bytes']!=1 or diagnostic['declared_bits']!=8:
            raise ValueError('the narrow width disposition lacks its exact actual diagnostic byte view')
    else:
        owners=((0xFFFF2142,'knock_count/ram',8),(0xFFFF2144,'knock_threshold_base/ram',16),
                (0xFFFF11DE,'knock_channel_primary/ram',8),(0xFFFF2143,'knock_channel_alternate/ram',8))
        for address,meaning,width in owners:
            native=model.symbols.get(SymbolKey('7mfk','ram',address))
            if (native is None or native.meaning is None or native.meaning.key!=meaning
                    or type(native.value('width')) is not int or native.value('width')!=width
                    or native.value('signed') is not False):
                raise ValueError('the narrow indexed disposition changes the byte counter, selector or distinct word-vector owner')
        if {(row['input'],row['active']) for row in captured['byte_counter']}!={(value,active) for value in range(256) for active in (False,True)}:
            raise ValueError('the narrow indexed disposition lacks its actual unsigned byte counter and both predicate outcomes')
        if any(contract.alias(0xFFFF2142) not in row['addresses'] for row in support):
            raise ValueError('the narrow indexed disposition hides its explicitly observed zero-index alias')
    if record['candidate']['producer_inputs'].get(DESCRIPTOR)!=hashlib.sha256((Path(model.root)/DESCRIPTOR).read_bytes()).hexdigest():
        raise ValueError('the narrow width disposition differs from its original complete producer input')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the narrow width disposition inputs change during admission')
    return dict(symbol=symbol.key.key,original_claim_sha256=field['original_claim_sha256'],
        source_l0=field['original_l0'],descriptor=DESCRIPTOR,
        descriptor_sha256=hashlib.sha256((Path(model.root)/DESCRIPTOR).read_bytes()).hexdigest(),
        original_process_sha256=record['process_sha256'],region=captured['region'],
        fixture_sha256=captured['fixture_sha256'],elf_sha256=captured['elf_sha256'],
        observations=captured['observations'],scope=disposition['kind'],declared_bits=field['declared_bits'],
        diagnostic_view=diagnostic,working_instruction_support=support,
        physical_question_bits=disposition['physical_question_bits'],semantic_width_inference=False,
        native_width_change=False,natural_entry_inference=False,selector_range_inference=False,
        zero_index_disjointness=False,identity_grounding=False,access_grounding=False,hardware_qualification=False)


def accepted(model,symbol,claim):
    try:
        return require(model,symbol,claim)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):
        return None
