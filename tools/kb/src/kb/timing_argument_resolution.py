"""Exact native transition for conditional timing arithmetic arguments."""

from copy import deepcopy
import json
from pathlib import Path
from kb import timing_argument_contract as contract,timing_argument_evidence as proof,test_contract
from kb.model import SymbolKey
from kb.repo import KbError


def operation_shape(op):
    return (set(op)=={'cmd','id','claim_sha256'} and op['cmd']=='reconcile-timing-argument'
        and any(op['id']==row[0] and op['claim_sha256']==identity
            for row,identity in zip(contract.ROWS,contract.ORIGINALS)))


def prepare(change,op):
    from kb import reconciliation
    if not operation_shape(op):raise KbError('reconcile-timing-argument needs one exact registered original claim',code=3)
    declared=proof.native_rows(change.model)
    row=next(row for row in declared['reference'] if row['id']==op['id'])
    if row['id'] in change.argument_resolutions:raise KbError('reconcile-timing-argument repeats an original claim',code=3)
    symbol=change.model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    original=[link for link in change.model.links if contract.original(row,link)]
    if len(original)!=1:raise KbError('reconcile-timing-argument needs the complete unchanged original reader',code=3)
    questions=[item for item in reconciliation.differences(change.model)
        if item['kind']=='access' and item['subject']==symbol.key.key
        and item['claim_sha256']==row['original_claim_sha256']]
    if len(questions)!=1:raise KbError('reconcile-timing-argument names no exact current raw access question',code=3)
    question=questions[0]
    reviews=[item for item in change.model.config.get('reconciliation',{}).get('review',())
        if isinstance(item,dict) and reconciliation.difference_key(item)==reconciliation.difference_key(question)]
    if (len(reviews)!=1 or set(reviews[0])!=set(question)|{'state','reason'}
            or reviews[0].get('state')!='unresolved' or type(reviews[0].get('reason')) is not str
            or not reviews[0]['reason'].strip()
            or any(not test_contract.exact(reviews[0].get(key),value) for key,value in question.items())):
        raise KbError('reconcile-timing-argument needs its complete exact retained unresolved review',code=3)
    try:proof.require_current(change.model)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
        raise KbError(f'reconcile-timing-argument lacks its qualified original execution: {error}',code=3) from None
    path,document=change.document(symbol.meaning)
    if path!=Path(json.loads(row['original_claim_json'])['sources'][0]) or not (change.root/path).is_file():
        raise KbError('reconcile-timing-argument needs its existing exact owned native file',code=3)
    if not test_contract.exact(document.get('ledger'),json.loads(row['original_ledger_json'])):
        raise KbError('reconcile-timing-argument needs its complete exact original ledger rows',code=3)
    target=change.model.symbols[contract.FUNCTION].meaning
    links=[(index,entry) for index,entry in enumerate(document.get('link',()))
        if change._same_link(entry,{'type':'reader'},target)]
    if len(links)!=1:raise KbError('reconcile-timing-argument needs one exact original document relation',code=3)
    index,entry=links[0]
    replacement=deepcopy(entry)
    replacement.update(type='depends',to=contract.TARGET,role=contract.ROLE,
        via=[f'7mfk:{site:08x}' for site in (row['caller'],row['wrapper'])],
        note=json.loads(row['proposed_claim_json'])['props']['note'])
    evidence=contract.item(row);evidence['to']=evidence['to'].location
    replacement['evidence']=[evidence]
    document['link'][index]=replacement
    document['ledger']=json.loads(row['proposed_ledger_json'])
    change.argument_resolutions[row['id']]=row['original_claim_sha256']
    if len(change.argument_resolutions)==1:
        def complete(result):
            try:require_transition(change.model,result,change.argument_resolutions)
            except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError) as error:
                return f'the timing argument transition is incomplete or unqualified: {error}'
            return None
        change.expected.append(complete)
    change.lines.append(f'reconcile timing argument {row["id"]}: {row["original_claim_sha256"]}; exact conditional execution')


def require_transition(before,after,resolutions):
    from kb import test_origins,copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence
    declared=contract.descriptor(before.root)
    if not test_contract.exact(resolutions,{row['id']:row['original_claim_sha256'] for row in declared['reference']}):
        raise ValueError('the timing argument transition requires every exact registered original claim')
    proof.native_rows(before);proof.native_rows(after)
    for row in declared['reference']:
        if (sum(contract.original(row,link) for link in before.links)!=1
                or sum(contract.dependency(row,link) for link in after.links)!=1
                or any(contract.original(row,link) for link in after.links)):
            raise ValueError('the timing argument transition substitutes or retains an original relation')
    old={key:origin.packet() for key,origin in test_origins.index(before).items()}
    new={key:origin.packet() for key,origin in test_origins.index(after).items()}
    if not test_contract.exact(old,new):raise ValueError('the timing argument changes an original TEST context or attachment')
    # The registered replacements have no endpoint in an existing COPY/SID22 scope.
    # Their exact scopes stay equal; no broad normalization admits the change.
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        if module.scope_digest(before)!=module.scope_digest(after):
            raise ValueError('the timing argument transition changes an existing physical proof namespace')
    proof.require_current(after)
    return declared


def retires(before,after,claim,resolutions):
    if contract.digest(contract.plain(claim)) not in resolutions.values():return False
    try:
        declared=require_transition(before,after,resolutions)
        return any(test_contract.exact(contract.plain(claim),json.loads(row['original_claim_json']))
            for row in declared['reference'])
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):return False


def publication_expected(before,after,resolutions,before_view,after_view):
    declared=require_transition(before,after,resolutions)
    expected=deepcopy(before_view)
    ledger={row['owner']:json.loads(row['proposed_ledger_json']) for row in declared['reference']}
    expected['ordered']['native_ledgers']=[(kind,name,ledger.get(f'{name}/{kind}',items),source)
        for kind,name,items,source in expected['ordered']['native_ledgers']]
    for row in declared['reference']:
        old_key=row['owner'],'reader',contract.TARGET,None,None
        new_key=row['owner'],'depends',contract.TARGET,None,None
        for section in (expected['facts']['links'],expected['origins']['links']):
            if old_key not in section or new_key in section:
                raise ValueError('the timing argument transition changes its exact relation namespace')
            del section[old_key]
        expected['facts']['links'][new_key]=after_view['facts']['links'][new_key]
        expected['origins']['links'][new_key]=after_view['origins']['links'][new_key]
    return expected
