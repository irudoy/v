"""Exact representation of the conditional cached-publication snapshot dependency."""
import json,tomllib
from kb import diagnostic_rom_contract as data,test_contract
from kb.model import SymbolKey
DESCRIPTOR='defs/JK08A.snapshot-ROM-dependency.toml'
KEY='snapshot-ROM-v1:jk08a-inhibit-publication'
PREFIX='snapshot-ROM-'
ID='jk08a-snapshot-ROM-dependency'
OWNER='turquoise-mushroom/tbl'
RAM_OWNER='teal-giraffe/ram'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ORIGINAL='9931126fbeddf67582df91a5b6939c5c00ec7a6471eb7fa6e4879e048fef5212'
PROPOSED='cc1d1bfe9a833513e465b8780e7a01f63a5bcc7a2efc6e601cb494288c812fc4'
FLAGS=('physical_reader_inference', 'universal_no_ROM_read', 'natural_scheduling_inference', 'scale_admission', 'hardware_qualification')


def descriptor(root):
    from kb import copy_evidence
    value=tomllib.loads(copy_evidence._read(root,DESCRIPTOR).decode())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference','geometry',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!=ID or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['geometry'],dict(storage='uint8',cols=4))
            or len(value['reference'])!=1):
        raise ValueError('the snapshot-ROM descriptor changes its exact source, geometry or admission boundary')
    row=value['reference'][0]
    keys={'id','owner','address','original_claim_sha256','original_claim_json','proposed_claim_sha256',
        'proposed_claim_json','original_ledger_json','proposed_ledger_json','RAM_owner','RAM_address','live_owner','live_address'}
    wanted=dict(id='inhibit-publication',owner=OWNER,address=0x1202E,RAM_owner=RAM_OWNER,RAM_address=0xFFFF106A,
        live_owner='vivid-meerkat/ram',live_address=0xFFFF1072)
    if (set(row)!=keys or not test_contract.exact({key:row[key] for key in wanted},wanted)
            or row['original_claim_sha256']!=ORIGINAL or row['proposed_claim_sha256']!=PROPOSED):
        raise ValueError('the snapshot-ROM dependency changes its complete original owner or byte identity')
    old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
    if data.digest(old)!=ORIGINAL or data.digest(new)!=PROPOSED:
        raise ValueError('the snapshot-ROM dependency changes its complete canonical claim')
    if not test_contract.exact(json.loads(row['proposed_ledger_json']),data.retired_ledger(row)):
        raise ValueError('the snapshot-ROM ledger changes more than its exact physical reader selector')
    return value


def item(row):
    return dict(kind='indirect',mode='snapshot-output',key=KEY,path=DESCRIPTOR,
        at='7mfk:0001202e',to=SymbolKey('7mfk','ram',0xFFFF106A),supports='identity',
        value=dict(owner=OWNER,original_claim_sha256=ORIGINAL,scope='conditional-cached-snapshot',
            physical_reader_inference=False,natural_scheduling_inference=False,hardware_qualification=False))


def original(row,link):
    return test_contract.exact(data.canonical(link),json.loads(row['original_claim_json']))


def dependency(row,link):
    expected=json.loads(row['proposed_claim_json']);expected['evidence']=[data.plain(item(row))]
    return test_contract.exact(data.canonical(link),expected)


def registered(evidence):
    return (evidence.get('mode')=='snapshot-output' or evidence.get('path')==DESCRIPTOR
        or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def looks_like_dependency(link):
    return ('snapshot-output' in link.roles or any(registered(item) for item in link.evidence)
        or link.owner.key==OWNER and link.type=='depends' and link.to.key==RAM_OWNER)


def representation_only(link,root):
    if link.owner.key!=OWNER:return False
    row=descriptor(root)['reference'][0]
    return original(row,link) or dependency(row,link)
