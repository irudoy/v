"""Exact native transition for the conditional cached snapshot dependency."""

from copy import deepcopy
import json
from pathlib import Path
from kb import snapshot_rom_contract as contract,snapshot_rom_evidence as proof,test_contract
from kb.model import SymbolKey
from kb.repo import KbError


def operation_shape(op):
    return (set(op)=={'cmd','id','claim_sha256'} and op['cmd']=='reconcile-snapshot-output'
        and op['id']=='inhibit-publication' and op['claim_sha256']==contract.ORIGINAL)


def prepare(change,op):
    from kb import reconciliation
    if not operation_shape(op):raise KbError('reconcile-snapshot-output needs its exact registered original claim',code=3)
    declared=proof.native_rows(change.model);row=declared['reference'][0]
    if row['id'] in change.snapshot_resolutions:raise KbError('reconcile-snapshot-output repeats its original claim',code=3)
    symbol=change.model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    original=[link for link in change.model.links if contract.original(row,link)]
    if len(original)!=1:raise KbError('reconcile-snapshot-output needs the complete unchanged original reader',code=3)
    questions=[item for item in reconciliation.differences(change.model)
        if item['kind']=='access' and item['subject']==symbol.key.key and item['claim_sha256']==contract.ORIGINAL]
    if len(questions)!=1:raise KbError('reconcile-snapshot-output names no exact current raw access question',code=3)
    question=questions[0]
    reviews=[item for item in change.model.config.get('reconciliation',{}).get('review',())
        if isinstance(item,dict) and reconciliation.difference_key(item)==reconciliation.difference_key(question)]
    if (len(reviews)!=1 or set(reviews[0])!=set(question)|{'state','reason'} or reviews[0].get('state')!='unresolved'
            or type(reviews[0].get('reason')) is not str or not reviews[0]['reason'].strip()
            or any(not test_contract.exact(reviews[0].get(key),value) for key,value in question.items())):
        raise KbError('reconcile-snapshot-output needs its complete exact retained unresolved review',code=3)
    try:proof.require_current(change.model)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
        raise KbError(f'reconcile-snapshot-output lacks its qualified original execution: {error}',code=3) from None
    path,document=change.document(symbol.meaning)
    if path!=Path(json.loads(row['original_claim_json'])['sources'][0]) or not (change.root/path).is_file():
        raise KbError('reconcile-snapshot-output needs its existing exact owned native file',code=3)
    if not test_contract.exact(document.get('ledger'),json.loads(row['original_ledger_json'])):
        raise KbError('reconcile-snapshot-output needs its complete exact original ledger rows',code=3)
    target=change.model.symbols[SymbolKey('7mfk','fn',0x20DFE)].meaning
    links=[(index,entry) for index,entry in enumerate(document.get('link',()))
        if change._same_link(entry,{'type':'reader'},target)]
    if len(links)!=1:raise KbError('reconcile-snapshot-output needs one exact original document relation',code=3)
    index,entry=links[0];replacement=deepcopy(entry)
    replacement.update(type='depends',to=row['RAM_owner'],role='snapshot-output',
        via=['7mfk:0003e1da','7mfk:00020dfe'],note=json.loads(row['proposed_claim_json'])['props']['note'])
    evidence=contract.item(row);evidence['to']=evidence['to'].location;replacement['evidence']=[evidence]
    document['link'][index]=replacement;document['ledger']=json.loads(row['proposed_ledger_json'])
    properties=declared['geometry']
    if any(symbol.value(key) is not None and not test_contract.exact(symbol.value(key),value)
            for key,value in properties.items()):
        raise KbError('reconcile-snapshot-output contradicts an existing conditional geometry property',code=3)
    additions={key:value for key,value in properties.items() if symbol.value(key) is None}
    if additions:change._entry(symbol.meaning,document,symbol).update(additions)
    change.snapshot_resolutions[row['id']]=contract.ORIGINAL
    def complete(result):
        try:require_transition(change.model,result,change.snapshot_resolutions)
        except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
            return f'the snapshot-ROM transition is incomplete or unqualified: {error}'
        return None
    change.expected.append(complete)
    change.lines.append(f'reconcile snapshot output {row["id"]}: {contract.ORIGINAL}; exact conditional execution')


def require_transition(before,after,resolutions):
    from kb import test_origins,copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence
    declared=contract.descriptor(before.root);row=declared['reference'][0]
    if not test_contract.exact(resolutions,{row['id']:contract.ORIGINAL}):
        raise ValueError('the snapshot-ROM transition needs its one exact original claim')
    proof.native_rows(before);proof.native_rows(after)
    if (sum(contract.original(row,link) for link in before.links)!=1
            or sum(contract.dependency(row,link) for link in after.links)!=1
            or any(contract.original(row,link) for link in after.links)):
        raise ValueError('the snapshot-ROM transition substitutes or retains its original relation')
    old={key:origin.packet() for key,origin in test_origins.index(before).items()}
    new={key:origin.packet() for key,origin in test_origins.index(after).items()}
    if not test_contract.exact(old,new):raise ValueError('the snapshot-ROM transition changes an original TEST context or attachment')
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        if module.scope_digest(before)!=module.scope_digest(after):
            raise ValueError('the snapshot-ROM transition changes an existing physical proof namespace')
    proof.require_current(after)
    return declared


def retires(before,after,claim,resolutions):
    if contract.data.digest(contract.data.plain(claim)) not in resolutions.values():return False
    try:
        declared=require_transition(before,after,resolutions)
        return test_contract.exact(contract.data.plain(claim),json.loads(declared['reference'][0]['original_claim_json']))
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):return False


def publication_expected(before,after,resolutions,before_view,after_view):
    from kb import convert
    declared=require_transition(before,after,resolutions);row=declared['reference'][0]
    expected=deepcopy(before_view)
    expected['ordered']['native_ledgers']=[(kind,name,
        json.loads(row['proposed_ledger_json']) if f'{name}/{kind}'==row['owner'] else ledger,source)
        for kind,name,ledger,source in expected['ordered']['native_ledgers']]
    old_key=row['owner'],'reader','coherent_snapshot/fn',None,None
    new_key=row['owner'],'depends',row['RAM_owner'],None,None
    for section in (expected['facts']['links'],expected['origins']['links']):
        if old_key not in section or new_key in section:
            raise ValueError('the snapshot-ROM transition changes its exact original relation namespace')
        del section[old_key]
    expected['facts']['links'][new_key]=after_view['facts']['links'][new_key]
    expected['origins']['links'][new_key]=after_view['origins']['links'][new_key]
    key=SymbolKey('7mfk','tbl',row['address']);old,new=before.symbols[key],after.symbols[key]
    props={**old.props,**{name:value for name,value in declared['geometry'].items() if old.value(name) is None}}
    if not test_contract.exact(new.props,props):
        raise ValueError('the snapshot-ROM geometry changes another property or adds an unnecessary override')
    original=expected['facts']['symbols'][key.location,key.kind]
    expected['facts']['symbols'][key.location,key.kind]=(*original[:3],convert._value(after,props),*original[4:])
    ordered=expected['ordered']['symbols'][key];expected['ordered']['symbols'][key]=(props,*ordered[1:])
    return expected
