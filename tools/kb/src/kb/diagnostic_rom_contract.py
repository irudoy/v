"""Exact representations of four diagnostic-output dependency claims.

Representation matching grants no causal, access, scale or hardware proof.
The original positive execution and native write guards admit those separately.
"""

import hashlib
import json
import tomllib
from copy import deepcopy
from kb import test_contract
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.diagnostic-ROM-dependencies.toml'
KEY='diagnostic-ROM-v1:jk08a-output-dependencies'
PREFIX='diagnostic-ROM-'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('k-bfs',0x9284,'active-caracal/tbl',0xFFFF1026,'bfs/ram',16,(0x1208,)),
    ('exhaust-cold',0xB2FA,'meaty-guillemot/tbl',0xFFFF2327,'exhaust_cvtc_target/ram',8,(0x1166,)),
    ('exhaust-main',0xB33A,'exhaust_cvtc_target/tbl',0xFFFF2327,'exhaust_cvtc_target/ram',8,(0x1166,)),
    ('ignition-correction',0x147DA,'sincere-dragonfly/tbl',0xFFFF2022,'apc_output/ram',8,(0x1107,0x1108,0x1109,0x110A,0x113C)))
ORIGINALS=('a54e81b76506487bc4d6ad62b06eb8007df871ae163f41c2b2451ab9fecb7439',
    '773bb5c05fb01ade08e4316ae3feaf6f23782809755cf8bbe6363ca1876f1520',
    '07dd46c691870056fae3c1d94866e8383dc9867a6058c1662ebe211fb7356f26',
    '46cdc06c45f30a8aa231f7928c00bd9b92d0cdb605c27af12da340ca666e9ddb')
PROPOSED=('faecc814f7a54c0661e590f3a21829895ae8447405b223b3b71cdf3045e26059',
    '589a4ed9c7532bb63ae7d95050b565a53a4ab0eb9e269f9dbdae70ee2224c5ea',
    'be17ca2d103facff74519abbd62889faae500fb1091e39be6415af9c4964ae58',
    '59048af27cdf146c229a2667bdb7678e54bb84ae7abdfa1dacf1e3c1e9e694f5')
VIA=((0x3B75C,0x3235C),(0xBFDC0,0xBFE88,0x3235C),(0xBFDC0,0xBFE88,0x3235C),
     (0x4D99C,0x4DBE8,0x4DF82,0x3235C))


def plain(value):
    return json.loads(json.dumps(value,sort_keys=True,separators=(',',':'),default=str))


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),default=str).encode()).hexdigest()


def descriptor(root):
    from kb import copy_evidence
    value=tomllib.loads(copy_evidence._read(root,DESCRIPTOR).decode())
    flags=('physical_reader_inference','universal_no_ROM_read','hardware_qualification',
           'scale_level_changes','unrelated_claim_changes')
    if (set(value)!={'schema','id','layout','publisher','publisher_address','image_sha256','scope',
            'reference','geometry','alias_note',*flags}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-diagnostic-ROM-dependencies'
            or value['layout']!='7mfk' or value['publisher']!='married-moth/fn'
            or not test_contract.exact(value['publisher_address'],0x3235C)
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in flags)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the diagnostic ROM descriptor changes its exact image, publisher or bounded inference scope')
    row_keys={'id','address','owner','RAM_address','RAM_owner','RAM_width','dids','via',
        'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
        'RAM_reader_claim_sha256','condition','original_ledger_json','proposed_ledger_json'}
    for row,expected,identity,proposed,via in zip(value['reference'],ROWS,ORIGINALS,PROPOSED,VIA):
        key,address,owner,ram,ram_owner,width,dids=expected
        if set(row)!=row_keys:
            raise ValueError('a diagnostic ROM row changes its complete exact schema')
        stated={name:row[name] for name in ('id','address','owner','RAM_address','RAM_owner','RAM_width','dids','via')}
        wanted=dict(id=key,address=address,owner=owner,RAM_address=ram,RAM_owner=ram_owner,RAM_width=width,dids=list(dids),via=list(via))
        if not test_contract.exact(stated,wanted) or row['original_claim_sha256']!=identity:
            raise ValueError('a diagnostic ROM row changes its exact owning claim, source or diagnostic aliases')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if digest(old)!=identity or digest(new)!=proposed or row['proposed_claim_sha256']!=proposed:
            raise ValueError('a diagnostic ROM canonical claim differs from its complete declared identity')
        if (old['owner']!=owner or old['to']!='married-moth/fn' or old['type']!='reader'
                or old['layout']!='7mfk' or old['slot'] is not None or old['offset'] is not None
                or old['roles']!=[] or old['evidence']!=[]
                or new['owner']!=owner or new['to']!=ram_owner or new['type']!='depends'
                or new['layout']!='7mfk' or new['slot'] is not None or new['offset'] is not None
                or new['roles']!=['diagnostic-output'] or new['evidence']!=[]
                or new['stated']!=old['stated'] or new['sources']!=old['sources']
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or set(new['props'])!=set(old['props'])|{'via','note'}
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',site)) for site in via]):
            raise ValueError('a diagnostic ROM replacement changes an original property or its exact dependency class')
        if not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row)):
            raise ValueError('a diagnostic ROM ledger changes more than the original physical-reader selectors')
    geometry=((0x9284,'active-caracal/tbl',dict(storage='uint16',cols=1)),
        (0xB2FA,'meaty-guillemot/tbl',dict(storage='uint8',rows=8,cols=8)),
        (0xB33A,'exhaust_cvtc_target/tbl',dict(storage='uint8',rows=16,cols=16)),
        (0x147DA,'sincere-dragonfly/tbl',dict(storage='uint16',cols=8)))
    if len(value['geometry'])!=len(geometry):raise ValueError('the diagnostic ROM geometry owner set differs')
    for row,(address,owner,properties) in zip(value['geometry'],geometry):
        if (set(row)!={'owner','address','properties_json','scope'} or row['owner']!=owner
                or not test_contract.exact(row['address'],address)
                or not test_contract.exact(json.loads(row['properties_json']),properties)):
            raise ValueError('the diagnostic ROM geometry changes an exact conditional property or owner')
    note=value['alias_note']
    if set(note)!={'owner','original_json','proposed_json','scope'} or note['owner']!='sincere-dragonfly/tbl':
        raise ValueError('the diagnostic alias note has another exact owner or scope')
    old,new=json.loads(note['original_json']),json.loads(note['proposed_json'])
    phrase='also returns ffff2022 for four exact pointer-table aliases'
    if (type(old) is not list or not old or any(type(item) is not str for item in old)
            or sum(item.count(phrase) for item in old)!=1
            or not test_contract.exact(new,[item.replace(phrase,'returns ffff2022 for its exact pointer-table aliases') for item in old])):
        raise ValueError('the diagnostic alias note changes more than its ungated fixed count')
    return value


def item(row):
    return dict(kind='indirect',mode='diagnostic-output',key=KEY,path=DESCRIPTOR,
        at=f'7mfk:{row["address"]:08x}',to=SymbolKey('7mfk','ram',row['RAM_address']),supports='identity',
        value=dict(owner=row['owner'],RAM_owner=row['RAM_owner'],original_claim_sha256=row['original_claim_sha256'],
                   scope='conditional-diagnostic-output',physical_reader_inference=False,hardware_qualification=False))


def canonical(link):
    return plain(dict(owner=link.owner.key,to=link.to.key,type=link.type,layout='7mfk',
        slot=link.slot,offset=link.offset,roles=sorted(link.roles),props=link.props,
        evidence=link.evidence,stated=sorted(link.stated),sources=sorted(link.sources)))


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def dependency(row,link):
    expected=json.loads(row['proposed_claim_json'])
    expected['evidence']=[plain(item(row))]
    return test_contract.exact(canonical(link),expected)


def sid_representation_only(link,root):
    """Exclude only these exact representations from the RAM-publisher namespace.

    SID22 proves its RAM source reads. This normalization never accepts a ROM
    dependency, which requires the independent joint execution admission.
    """
    if link.owner.key not in {row[2] for row in ROWS}:return False
    for row in descriptor(root)['reference']:
        if row['owner']==link.owner.key:return original(row,link) or dependency(row,link)
    return False


def registered(evidence):
    return (evidence.get('mode')=='diagnostic-output' or evidence.get('path')==DESCRIPTOR
            or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def looks_like_dependency(link):
    return ('diagnostic-output' in link.roles or any(registered(item) for item in link.evidence)
            or any(link.owner.key==owner and link.type=='depends' and link.to.key==ram_owner
                   for key,address,owner,ram,ram_owner,width,dids in ROWS))


def retired_ledger(row):
    """Withdraw only exact selectors of the replaced physical reader.

    The conditional dependency stays native; no legacy reader token stands
    for it, and no legacy token grants a scale inference from transport.
    """
    before=json.loads(row['original_ledger_json'])
    if type(before) is not list or not before or any(type(marker) is not dict for marker in before):
        raise ValueError('the diagnostic ROM ledger has no complete original row')
    claim=json.loads(row['original_claim_json'])
    supports=claim['props']['supports']
    supports=supports if type(supports) is list else [supports]
    after=deepcopy(before)
    removed=[]
    for marker in after:
        kept=[]
        for selector in marker.get('dependency',()):
            expected=dict(role='consumer',to=claim['to'],type='reader',end='owner',
                relies=claim['props']['relies'],supports=selector.get('supports'))
            if test_contract.exact(selector,expected) and selector['supports'] in supports:
                removed.append(selector['supports'])
            else:kept.append(selector)
        if 'dependency' in marker:marker['dependency']=kept
    if sorted(removed)!=sorted(supports):
        raise ValueError('the diagnostic ROM ledger lacks exactly its original supported reader selectors')
    return after


def native_ledger(model,owner):
    rows=[ledger for kind,name,ledger,source in model.stash.get('ledger_rows',()) if f'{name}/{kind}'==owner]
    if len(rows)!=1:
        raise ValueError('the diagnostic ROM owner has no unique original ledger binding')
    return plain(rows[0])
