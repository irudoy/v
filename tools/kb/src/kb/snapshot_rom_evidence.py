"""Positive cached-publication dependency through the explicit snapshot sequence."""

from copy import deepcopy
import hashlib,json
from weakref import WeakKeyDictionary
from kb import copy_evidence,ignition_literal_evidence,test_contract
from kb import snapshot_rom_contract as contract,publication_inhibit_capture_evidence as execution
from kb.model import SymbolKey

_ACCEPTED=WeakKeyDictionary()


def native_rows(model):
    declared=contract.descriptor(model.root);row=declared['reference'][0]
    for kind,address,owner in (('tbl',row['address'],row['owner']),
            ('ram',row['RAM_address'],row['RAM_owner']),('ram',row['live_address'],row['live_owner'])):
        symbol=model.symbols.get(SymbolKey('7mfk',kind,address))
        if symbol is None or symbol.meaning is None or symbol.meaning.key!=owner:
            raise ValueError('the snapshot-ROM dependency changes an exact calibration, live or snapshot owner')
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    links=[link for link in model.links if link.owner is symbol.meaning and (
        link.type=='reader' and link.to.key=='coherent_snapshot/fn' or contract.looks_like_dependency(link))]
    if len(links)!=1 or not (contract.original(row,links[0]) or contract.dependency(row,links[0])):
        raise ValueError('the snapshot-ROM dependency needs its one complete original or replacement relation')
    key='original_ledger_json' if contract.original(row,links[0]) else 'proposed_ledger_json'
    if not test_contract.exact(contract.data.native_ledger(model,row['owner']),json.loads(row[key])):
        raise ValueError('the snapshot-ROM dependency changes an original ledger selector, row or evidence position')
    for name,value in declared['geometry'].items():
        if symbol.value(name) is not None and not test_contract.exact(symbol.value(name),value):
            raise ValueError('the snapshot-ROM dependency contradicts a declared conditional calibration geometry')
    return declared


def positive_sequences(packet,result):
    declared=packet['declaration']
    observations=execution.observations(packet,declared)
    groups={};semantic={row['index']:row for row in result['semantic_results']}
    for case,observed in zip(declared['cases'],observations):
        groups.setdefault(case['parent'],[]).append((case,observed,semantic[case['index']]))
    witnesses=[];variations={}
    for rows in groups.values():
        if [case['stage'] for case,observed,meaning in rows]!=[0,1,2]:
            raise ValueError('the snapshot-ROM dependency omits or reorders a complete actual sequence')
        if not all(meaning['conditional_positive_path'] for case,observed,meaning in rows):continue
        (first,initial,lookup),(second,publication,published),(third,snapshot,copied)=rows
        before=initial['memory_before'][0];cached=initial['memory_after'][0]
        changed=bytearray(cached);changed[0x2459]|=32
        live=publication['memory_after'][0]
        snap=snapshot['memory_after'][0]
        if (lookup['lookup'] is None or initial['entry']!=0x3E1DA or publication['entry']!=0x3E1DA
                or snapshot['entry']!=0x20F1C or cached[0x1072]!=0
                or cached[0x257A]!=lookup['lookup']['output'] or cached[0x1EE0]!=cached[0x257A]
                or publication['memory_before']!=(bytes(changed),) or snapshot['memory_before']!=(live,)
                or snap[0x106A:0x1072]!=live[0x1072:0x107A]
                or published['output']!=live[0x1072] or copied['output']!=snap[0x106A]
                or published['lookup'] is not None or live[0x257A]!=cached[0x257A]):
            raise ValueError('the snapshot-ROM dependency loses its actual cache, sole mode-bit change or complete live-to-snapshot continuity')
        filtered=published['filtered']
        if type(filtered) is not int or not 0<filtered<=65535:
            raise ValueError('the snapshot-ROM positive path lacks its exact nonzero filtered alternative')
        expected=(filtered>>8) if cached[0x257A]==0 else 0
        if snap[0x106A]!=expected:
            raise ValueError('the snapshot-ROM positive path lacks its nonzero alternative and exact cached Boolean selection')
        key=hashlib.sha256(before).hexdigest()
        table=initial['calibration_before'][0x1202E]
        variations.setdefault(key,set()).add((table,cached[0x257A],snap[0x106A]))
        witnesses.append(dict(parent=first['parent'],stages=[case['index'] for case,observed,meaning in rows],
            initial_memory_sha256=key,calibration=table.hex(),cached=cached[0x257A],
            live=live[0x1072],snapshot=snap[0x106A],source_bytes=live[0x1072:0x107A].hex(),
            destination_bytes=snap[0x106A:0x1072].hex()))
    if not any(len({table for table,cached,output in values})>=2
               and len({cached for table,cached,output in values})>=2
               and len({output for table,cached,output in values})>=2 for values in variations.values()):
        raise ValueError('the snapshot-ROM dependency lacks table-dependent cache and snapshot changes under equal original RAM')
    return witnesses


def require_primary(model,record=None):
    declared=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    original,current=ignition_literal_evidence.require_original(model,record)
    candidate=record['candidate'];packet=candidate['witness']['publication_inhibit_paths']
    result=execution.require_witness(model,packet,candidate['producer_inputs'])
    if original.count(packet['marker'])!=1 or result['image_sha256']!=declared['image_sha256']:
        raise ValueError('the snapshot-ROM dependency changes its unique complete original or owned image')
    witnesses=positive_sequences(packet,result)
    if candidate['producer_inputs'].get(contract.DESCRIPTOR)!=hashlib.sha256(
            copy_evidence._read(model.root,contract.DESCRIPTOR)).hexdigest():
        raise ValueError('the snapshot-ROM dependency differs from the original complete producer input')
    if ignition_literal_evidence.execution_inputs(model.root)!=current:
        raise ValueError('the snapshot-ROM execution closure changes during independent consumption')
    return dict(proof=contract.KEY,scope='conditional-cached-snapshot',component=result,sequences=witnesses,
        original_process_sha256=record['process_sha256'],native_model=record['native_model'],
        physical_reader_inference=False,universal_no_ROM_read=False,scale_admission=False,
        natural_scheduling_inference=False,hardware_qualification=False)


def owning_row(evidence,symbol,model,claim='identity'):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None:
        raise ValueError('the snapshot-ROM dependency needs its actual owning model and identity claim')
    if claim!='identity' and (getattr(claim,'name',None)!='identity'
            or getattr(claim,'subject',None) not in (symbol.key.key,symbol.meaning.key,symbol.meaning.name)):
        raise ValueError('the snapshot-ROM dependency supplies its owning identity only')
    row=contract.descriptor(model.root)['reference'][0]
    if (symbol.key!=SymbolKey('7mfk','tbl',row['address']) or symbol.meaning.key!=row['owner']
            or not test_contract.exact(evidence,contract.item(row))):
        raise ValueError('the snapshot-ROM dependency changes its complete evidence, owner or symbol')
    attached=[(link,item) for link in model.links if link.owner is symbol.meaning
        for item in link.evidence if contract.registered(item)]
    if (len(attached)!=1 or not contract.dependency(row,attached[0][0])
            or not test_contract.exact(attached[0][1],evidence)
            or any(contract.registered(item) for item in symbol.evidence)):
        raise ValueError('the snapshot-ROM proof has no unique complete owning dependency')
    return row


def dependency_state(model):
    from kb.diagnostic_rom_evidence import dependency_state as complete_state
    return complete_state(model)


def require_current(model):
    before=dependency_state(model);held=_ACCEPTED.get(model)
    if held is not None and held[0]==before:return deepcopy(held[1])
    result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the snapshot-ROM dependency changes during independent admission')
    _ACCEPTED[model]=before,deepcopy(result)
    return result


def failure(evidence,symbol=None,model=None,claim=None):
    if not contract.registered(evidence):return None
    try:
        owning_row(evidence,symbol,model,claim);require_current(model)
        return None
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,IndexError,RecursionError):
        return 'missing or invalid complete snapshot-ROM execution context'


def link_failure(model,link):
    if not contract.looks_like_dependency(link):return None
    entries=[item for item in link.evidence if contract.registered(item)]
    if len(entries)!=1:return 'the snapshot-ROM dependency lacks its one complete qualified owning proof'
    return failure(entries[0],link.owner.symbols.get('7mfk'),model,'identity')


def identity_only(symbol):
    return symbol is not None and symbol.layout=='7mfk' and symbol.meaning is not None and any(
        link.owner is symbol.meaning and contract.looks_like_dependency(link) for link in symbol.meaning.links)
