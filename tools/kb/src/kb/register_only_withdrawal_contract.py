"""Twelve exact before-present/after-absent native reader withdrawals."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.register-only-withdrawals.toml'
PREFIX = 'register-only-withdrawal-v1:jk08a:'
MODE = 'register-only-withdrawal'
IDENTITIES = (('000259d0-00008e3a-withdraw',
  36410,
  'apricot-carp/tbl',
  154064,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  'cd417736058f07670ae507ef446d43392b8d8ecde4713ccd0e3365e0e496a23f',
  None,
  'c107305c4b1058ebfa6abae23182aa6dec1cbaceca52a566732104bd83c70dfe',
  '8c84ad227be0dd914d208448b3a268707ae1d7d390c42df37aee0f69c053488d'),
 ('000259d0-00008e3c-withdraw',
  36412,
  'imported-civet/tbl',
  154064,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '78b98855222718d37d5cf0aaae145cc7ac5e71d354b30b19c4dcdef22d20d0cc',
  None,
  '05d8751803ee1807ce790679b5d03bc8fff7d2fda6bf4a7f4e6c13fb1b3070e9',
  'b2ff1c8f726ed78399dbc567ad33796de5a12a9c86587ea19e038424198ac671'),
 ('0002251c-00012126-withdraw',
  74022,
  'woodoo-loon/tbl',
  140572,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  'ed84fe25ec83532689390f7b9d04b3531a34dd9103356a70ba45ff3a19e10dd0',
  None,
  '4583ea22fe47cc306902bc660c4308621ef624028d3d2f061a70c58d52e537e5',
  '7e97b3f09b0930fbf93cb08c8cd9b7492716f5d88b825e479d6b8dcd1e801d22'),
 ('00026740-00012126-withdraw',
  74022,
  'woodoo-loon/tbl',
  157504,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '5186363c50a9f125349ef101af5f897ba27bec04e605a56e6ace7fcdb125cba0',
  None,
  '4583ea22fe47cc306902bc660c4308621ef624028d3d2f061a70c58d52e537e5',
  '7e97b3f09b0930fbf93cb08c8cd9b7492716f5d88b825e479d6b8dcd1e801d22'),
 ('00026740-00012196-withdraw',
  74134,
  'cold_idle_ignition_timing/tbl',
  157504,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '4daaf757d0d4108cbe66e6dae6f187beafcb44debeae6aaa337aa98a484178c8',
  None,
  '7ca4c86d16df613d76913a8e7955674cf99e9d066de5bc6b0ea12a17c26eda14',
  'b69c10a31e2ae4ab45e996e27732b0a55cb154928069eceed2aa2da4427a6057'),
 ('000224f8-000122ea-withdraw',
  74474,
  'thankful-woodlouse/tbl',
  140536,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  'a8551a2692510cfcee624615b58da94d86b47559240459536f7e10cb54d2d324',
  None,
  '23387526b13084d7f8191aa0e959ce7fd9e1c9a8ea31e80e6c8e5c7a35a2fb75',
  '6ae7ac506337a81f58540fd45211860afda5cdbb4fb015135f03edac8248f205'),
 ('000224f8-000122f2-withdraw',
  74482,
  'stoic-ladybug/tbl',
  140536,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '8b77d2de1849f696423a548f8467dbb8006a8f316a009c4af3613af7adcf4ce4',
  None,
  '0bd86d7af02e350e8eac9116408e02acb5116809d144d41b3b3b587e7d71d37b',
  '78aa17876368dff3f231db145f6f79b1216f254066ba8c05a616cbb21c92a1a4'),
 ('000224f8-00012552-withdraw',
  75090,
  'spry-quokka/tbl',
  140536,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '4869ba8f1d939a6484364443f430305417f6417d63840eca0956d52855010cad',
  None,
  '946c3e78118fc87b28315e86e2f2989585ef5676fb5b9ca8f926420995cc0b65',
  'cfd482dac6407055d701b379fb8238994ae0159ce631203376350518d95773cb'),
 ('000224f8-00012c02-withdraw',
  76802,
  'rampant-groundhog/tbl',
  140536,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  '72e8b93d48245f80a6f5f29c61b731aa095d4e7f77c617731ffaf1feeb65dbca',
  None,
  '7943cc5f35ce25a2f418d1ab0f74472a8b5475594340fd6e309e0cbbd820f06c',
  '914f532f8e94a8597912a7b2bd523d485b953c4c0e4f3a1f79f27817efc81021'),
 ('000224f8-00012d72-withdraw',
  77170,
  'resourceful-muskrat/tbl',
  140536,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  'b90096e16bf4aa1873a67229932cc0a5aea343bd2007bdae1ccb426c67aaeee5',
  None,
  'c154a7b896d4b883b77a4d26a9cf0fc5079547f0d32efcd723da2bb6032c8530',
  'c47d0f322acffe053237c5a710b1d7e96d33003377a81b43b454d5c8a3b27dce'),
 ('000224fa-0001300e-withdraw',
  77838,
  'convivial-mamba/tbl',
  140538,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  'unset',
  'unset',
  'bf9a3872d4ab3d6a035157cefdf6ced78cac704a1a02e04720a27649ec15a4c0',
  None,
  '6daef9973064e13aa0a3c6601e2de433d1099fcc9cc6338c33834114ac9e8bb4',
  '6d4f88a15623ba44db34f3f04ee6c462db4fcf17a0aecc6b589decdac1a41415'),
 ('00050a4c-ffff22e0-withdraw',
  4294910688,
  'fuel_inhibit_mask/ram',
  330316,
  (),
  'withdrawal',
  'register_only_helper_paths',
  None,
  8,
  'unset',
  '58c006e6754df9b157888cee4f461ad85788ace7edc48ee9801477e08eff7bab',
  None,
  'f59d7fbfc4ec28d1e7485bcc7f148d94d0ca39c90a3a93d9ec90c3dd22e7653b',
  '7480a02ea887781efa64f87a52ebe24b2e8852591594239cd523c62648f77bcb'))
FLAGS = ('native_identity_admission', 'native_geometry_inference', 'scale_admission', 'units_admission', 'natural_caller_reachability', 'hardware_qualification', 'replacement_relation', 'native_publication')


def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def symbol_key(row):
    return SymbolKey('7mfk',row['owner'].rsplit('/',1)[1],row['address'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-register-only-withdrawals'
            or value['layout']!='7mfk'
            or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[name] is not False for name in FLAGS) or len(value['reference'])!=12):
        raise ValueError('the register-only withdrawal changes its exact absent-claim admission boundary')
    keys={'id','owner','address','function','component','direction','source','original_claim_sha256',
        'original_claim_json','original_native_sha256','original_native_json','original_ledger_json',
        'original_symbol_evidence_json','declared_width','declared_signed','proposed_native_sha256',
        'proposed_native_json','proposed_ledger_json'}
    originals,proposed={},{}
    for row,pinned in zip(value['reference'],IDENTITIES):
        identity=tuple(tuple() if key=='sites' else row.get(key) for key in (
            'id','address','owner','function','sites','direction','component','width_bytes','declared_width',
            'declared_signed','original_claim_sha256','proposed_claim_sha256','original_native_sha256','proposed_native_sha256'))
        if set(row)!=keys or not test_contract.exact(identity,pinned):
            raise ValueError('the register-only withdrawal changes an exact original, owner, natural entry or type')
        old=json.loads(row['original_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(before)!=row['original_native_sha256']
                or digest(after)!=row['proposed_native_sha256'] or old['owner']!=row['owner']
                or old['type']!='reader' or old['layout']!='7mfk' or old['evidence']!=[]
                or old['sources']!=[row['source']] or old['slot'] is not None or old['offset'] is not None
                or old['roles']!=[] or row['direction']!='withdrawal'):
            raise ValueError('the register-only withdrawal changes complete original or native content')
        for held,document in ((originals,before),(proposed,after)):
            if row['owner'] in held and not test_contract.exact(document,held[row['owner']]):
                raise ValueError('the grouped register-only withdrawal substitutes a shared owner image')
            held[row['owner']]=document
        symbols=[item for item in before['symbol'] if item['layout']=='7mfk' and int(item['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0].get('evidence',[]),json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(after.get('ledger'),json.loads(row['proposed_ledger_json']))
                or not test_contract.exact((symbols[0].get('width',before.get('width')),
                    symbols[0].get('signed',before.get('signed'))),(native_type(row,'width'),native_type(row,'signed')))):
            raise ValueError('the register-only withdrawal changes retained native symbol evidence, type or ledger')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json']);document=expected[row['owner']]
        matches=[index for index,link in enumerate(document.get('link',())) if link['type']==old['type'] and link['to']==old['to']]
        if len(matches)!=1:raise ValueError('the register-only withdrawal lacks one exact original native relation')
        removed=document['link'].pop(matches[0])
        props={name:item for name,item in removed.items() if name not in ('type','to','evidence')}
        if (not test_contract.exact(props,old['props']) or removed.get('evidence',[])!=[]):
            raise ValueError('the register-only withdrawal substitutes original native relation content')
        for marker in document.get('ledger',()):
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency'] if not selector(row,row['owner'],item)]
    for document in expected.values():
        if not document.get('link'):document.pop('link',None)
        for marker in document.get('ledger',()):
            if not marker.get('dependency'):marker.pop('dependency',None)
    if len(expected)!=11 or not test_contract.exact(expected,proposed):
        raise ValueError('the register-only withdrawal changes another fact, link order, evidence, ledger identity, field or note')
    return value


def selector(row,owner,item):
    old=json.loads(row['original_claim_json'])
    return (item.get('type')==old['type'] and ((owner==row['owner'] and item.get('end')=='owner' and item.get('to')==old['to'])
        or (owner==old['to'] and item.get('end')=='to' and item.get('to')==row['owner'])))


def registered(evidence):
    return (evidence.get('mode')==MODE or evidence.get('path')==DESCRIPTOR
        or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def publication(link,evidence):
    return False


def looks_like_access(link):
    return any(registered(item) for item in link.evidence) or any(original(row,link) for row in descriptor_identity_rows())


def descriptor_identity_rows():
    # Only pinned hashes identify original claims; no live store or model query.
    return (dict(owner=row[2],original_claim_sha256=row[10]) for row in IDENTITIES)


def original(row,link):
    value=canonical(link)
    return value['owner']==row['owner'] and digest(value)==row['original_claim_sha256']


def correction(row):return True


def operation(row):
    old=json.loads(row['original_claim_json'])
    return dict(cmd='unlink',meaning=row['owner'],type=old['type'],to=old['to'])


removal=operation


def operations(ops,root):
    owners={row[2] for row in IDENTITIES}
    selected=[op for op in ops if (op.get('cmd')=='unlink' and op.get('meaning') in owners)
        or any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    expected=[operation(row) for row in descriptor(root)['reference']]
    if len(selected)!=12 or sorted(map(digest,selected))!=sorted(map(digest,expected)):
        raise ValueError('the register-only withdrawal requires exactly all twelve unchanged normal unlink operations')
    return True
