"""Exact native transition for four independently admitted diagnostic outputs."""

from copy import deepcopy
import json
from pathlib import Path

from kb import diagnostic_rom_contract as contract, diagnostic_rom_evidence as proof
from kb import test_contract
from kb.model import SymbolKey
from kb.repo import KbError


def operation_shape(op):
    return (set(op)=={'cmd','id','claim_sha256'} and op['cmd']=='reconcile-diagnostic-output'
        and any(op['id']==row[0] and op['claim_sha256']==identity
            for row,identity in zip(contract.ROWS,contract.ORIGINALS)))


def prepare(change,op):
    """Build through the normal owned-document writer; execute no ad hoc store."""
    from kb import reconciliation
    if not operation_shape(op):
        raise KbError('reconcile-diagnostic-output needs one exact registered original claim',code=3)
    declared=proof.native_rows(change.model)
    row=next(row for row in declared['reference'] if row['id']==op['id'])
    if row['id'] in change.diagnostic_resolutions:
        raise KbError('reconcile-diagnostic-output repeats an original claim',code=3)
    symbol=change.model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    original=[link for link in change.model.links if contract.original(row,link)]
    if len(original)!=1:
        raise KbError('reconcile-diagnostic-output needs the complete unchanged original reader',code=3)
    differences=[item for item in reconciliation.differences(change.model)
        if item['kind']=='access' and item['subject']==symbol.key.key
        and item['claim_sha256']==row['original_claim_sha256']]
    reviews=change.model.config.get('reconciliation',{}).get('review',())
    if len(differences)!=1:
        raise KbError('reconcile-diagnostic-output names no exact current raw access question',code=3)
    question=differences[0]
    matches=[item for item in reviews if isinstance(item,dict)
        and reconciliation.difference_key(item)==reconciliation.difference_key(question)]
    if (len(matches)!=1 or set(matches[0])!=set(question)|{'state','reason'}
            or matches[0].get('state')!='unresolved' or type(matches[0].get('reason')) is not str
            or not matches[0]['reason'].strip()
            or any(not test_contract.exact(matches[0].get(key),value) for key,value in question.items())):
        raise KbError('reconcile-diagnostic-output needs its complete exact retained unresolved review',code=3)
    try:
        proof.require_current(change.model)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
        raise KbError(f'reconcile-diagnostic-output lacks its qualified original execution: {error}',code=3) from None
    meaning=symbol.meaning
    path,document=change.document(meaning)
    expected_path=Path(json.loads(row['original_claim_json'])['sources'][0])
    if path!=expected_path or not (change.root/path).is_file():
        raise KbError('reconcile-diagnostic-output needs its existing exact owned native file',code=3)
    if not test_contract.exact(document.get('ledger'),json.loads(row['original_ledger_json'])):
        raise KbError('reconcile-diagnostic-output needs its complete exact original ledger rows',code=3)
    target=change.model.symbols[SymbolKey('7mfk','fn',declared['publisher_address'])].meaning
    entries=[(index,entry) for index,entry in enumerate(document.get('link',()))
        if change._same_link(entry,{'type':'reader'},target)]
    if len(entries)!=1:
        raise KbError('reconcile-diagnostic-output needs one exact original document relation',code=3)
    index,entry=entries[0]
    replacement=deepcopy(entry)
    replacement.update(type='depends',to=row['RAM_owner'],role='diagnostic-output',
        via=[f'7mfk:{address:08x}' for address in row['via']],
        note=json.loads(row['proposed_claim_json'])['props']['note'])
    evidence=contract.item(row)
    evidence['to']=evidence['to'].location
    replacement['evidence']=[evidence]
    document['link'][index]=replacement
    document['ledger']=json.loads(row['proposed_ledger_json'])
    geometry=next(item for item in declared['geometry'] if item['owner']==row['owner'])
    properties=json.loads(geometry['properties_json'])
    additions={key:value for key,value in properties.items() if symbol.value(key) is None}
    if any(symbol.value(key) is not None and not test_contract.exact(symbol.value(key),value)
            for key,value in properties.items()):
        raise KbError('reconcile-diagnostic-output contradicts an existing native geometry property',code=3)
    if additions:
        change._entry(meaning,document,symbol).update(additions)
    if row['owner']==declared['alias_note']['owner']:
        note=declared['alias_note']
        if not test_contract.exact(meaning.props.get('note'),json.loads(note['original_json'])):
            raise KbError('reconcile-diagnostic-output needs the exact original alias note',code=3)
        document['note']=json.loads(note['proposed_json'])
    change.diagnostic_resolutions[row['id']]=row['original_claim_sha256']
    if len(change.diagnostic_resolutions)==1:
        def complete(result):
            try:
                require_transition(change.model,result,change.diagnostic_resolutions)
            except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
                return f'the diagnostic output transition is incomplete or unqualified: {error}'
            return None
        change.expected.append(complete)
    change.lines.append(f'reconcile diagnostic output {row["id"]}: {row["original_claim_sha256"]}; exact conditional execution')


def require_transition(before,after,resolutions):
    from kb import test_origins
    declared=contract.descriptor(before.root)
    wanted={row['id']:row['original_claim_sha256'] for row in declared['reference']}
    if not test_contract.exact(resolutions,wanted):
        raise ValueError('the diagnostic output transition requires all four exact original claims')
    proof.native_rows(before)
    proof.native_rows(after)
    for row in declared['reference']:
        if (sum(contract.original(row,link) for link in before.links)!=1
                or sum(contract.dependency(row,link) for link in after.links)!=1
                or any(contract.original(row,link) for link in after.links)):
            raise ValueError('the diagnostic output transition substitutes or retains an original relation')
    old_contexts={key:origin.packet() for key,origin in test_origins.index(before).items()}
    new_contexts={key:origin.packet() for key,origin in test_origins.index(after).items()}
    if not test_contract.exact(old_contexts,new_contexts):
        raise ValueError('the diagnostic output transition changes an original TEST attachment or context')
    proof.require_current(after)
    return declared


def retires(before,after,claim,resolutions):
    if contract.digest(contract.plain(claim)) not in resolutions.values():
        return False
    try:
        declared=require_transition(before,after,resolutions)
        return any(test_contract.exact(contract.plain(claim),json.loads(row['original_claim_json']))
            for row in declared['reference'])
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):
        return False


def publication_expected(before,after,resolutions,before_view,after_view):
    """Permit only the explicit replacements, absent geometry and one note phrase."""
    from kb import convert
    declared=require_transition(before,after,resolutions)
    expected=deepcopy(before_view)
    ledger_updates={row['owner']:json.loads(row['proposed_ledger_json']) for row in declared['reference']}
    expected['ordered']['native_ledgers']=[(kind,name,ledger_updates.get(f'{name}/{kind}',ledger),source)
        for kind,name,ledger,source in before_view['ordered']['native_ledgers']]
    for row in declared['reference']:
        old_key=row['owner'],'reader',declared['publisher'],None,None
        new_key=row['owner'],'depends',row['RAM_owner'],None,None
        for section in (expected['facts']['links'],expected['origins']['links']):
            if old_key not in section or new_key in section:
                raise ValueError('the diagnostic output transition changes its exact original relation namespace')
            del section[old_key]
        expected['facts']['links'][new_key]=after_view['facts']['links'][new_key]
        expected['origins']['links'][new_key]=after_view['origins']['links'][new_key]
    for row in declared['geometry']:
        key=SymbolKey('7mfk','tbl',row['address'])
        old,new=before.symbols[key],after.symbols[key]
        properties=json.loads(row['properties_json'])
        if any(old.value(name) is not None and not test_contract.exact(old.value(name),value)
                for name,value in properties.items()):
            raise ValueError('the diagnostic geometry contradicts an original native property')
        props={**old.props,**{name:value for name,value in properties.items() if old.value(name) is None}}
        same=test_contract.exact(new.props,props)
        if not same:
            raise ValueError('the diagnostic geometry changes another property or adds an unnecessary override')
        original=expected['facts']['symbols'][key.location,key.kind]
        expected['facts']['symbols'][key.location,key.kind]=(*original[:3],convert._value(after,props),*original[4:])
        ordered=expected['ordered']['symbols'][key]
        expected['ordered']['symbols'][key]=(props,*ordered[1:])
    note=declared['alias_note']
    old=next(meaning for meaning in before.meanings if meaning.key==note['owner'])
    new=next(meaning for meaning in after.meanings if meaning.key==note['owner'])
    if not test_contract.exact(old.props.get('note'),json.loads(note['original_json'])):
        raise ValueError('the diagnostic alias note has another complete original value')
    props={**old.props,'note':json.loads(note['proposed_json'])}
    if not test_contract.exact(new.props,props):
        raise ValueError('the diagnostic alias note changes another property or qualifier')
    expected['facts']['meanings'][old.key]['props']=convert._value(after,props)
    ordered=expected['ordered']['meanings'][old.key]
    expected['ordered']['meanings'][old.key]=(props,*ordered[1:])
    return expected
