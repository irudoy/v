"""Exact grouped native phase normalization appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.phase-access-claims.toml'
PREFIX = 'phase-normalization-access-v1:jk08a:'
IDENTITIES = (('ffff13b8-reader',
  4294906808,
  'huge-lori/ram',
  167368,
  (167376, 167434),
  'reader',
  'phase_normalization_paths',
  2,
  16,
  False,
  'cd910dcbf30c3d090b3b1a9d8e10d765eac64f12003eab20d3dfbc615eff2cd3',
  '3b2832c18f4241eaa430a71c9c37fe1906aadbaaf8604cf0a36b09d488429f35',
  '7e40fce911e4c2c881d7cdd2f41d6b853202b7d5e46e415f9318c2e098c5c25a',
  '41e6d1b44a496a88765571910c2ccc57aa739f81d74de1024b644397ef0f91dc'),
 ('ffff13b8-writer',
  4294906808,
  'huge-lori/ram',
  167368,
  (167426, 167506, 167522, 167534),
  'writer',
  'phase_normalization_paths',
  2,
  16,
  False,
  '8e41c4bb288af2c59ba0f52c7594232bc77979950bf5f6a1a1fa7e0161b46bd8',
  '3fe06ab415d4fb6005cf0bee6761db6edbcb93d57674ec759ddf81a9b4e46637',
  '7e40fce911e4c2c881d7cdd2f41d6b853202b7d5e46e415f9318c2e098c5c25a',
  '41e6d1b44a496a88765571910c2ccc57aa739f81d74de1024b644397ef0f91dc'),
 ('ffff1558-reader',
  4294907224,
  'vivacious-petrel/ram',
  167368,
  (167376, 167434),
  'reader',
  'phase_normalization_paths',
  2,
  'unset',
  'unset',
  '2009c140f1e08862fd8f77f8bf676bb8ca1693cac892ac9cb646f4806c07e8ce',
  'd6fdc35b7535e7d5eb72a9e9a03779c0353363669a3c7940bda1cfc80df2b4ba',
  '1f8e7115936d16325390dcb4a71392e88c432d2f9994a84f1050c05681dbf2ab',
  '02d5df8584761c357574a03f4b75505a917a55d9722df46a6d2d2f78ab726442'),
 ('ffff1558-writer',
  4294907224,
  'vivacious-petrel/ram',
  167368,
  (167426, 167506, 167522, 167534),
  'writer',
  'phase_normalization_paths',
  2,
  'unset',
  'unset',
  'bb6a2d755f2f317e18e693398a96fb55a1e4a150e4b2cc6b39ec6708a6667832',
  'c3aa8817cd03f1838fd4d46305348905c8af31893e6b957e9787861e6a1c3280',
  '1f8e7115936d16325390dcb4a71392e88c432d2f9994a84f1050c05681dbf2ab',
  '02d5df8584761c357574a03f4b75505a917a55d9722df46a6d2d2f78ab726442'),
 ('ffff155a-reader',
  4294907226,
  'peridot-pony/ram',
  167368,
  (167428, 167524, 167536),
  'reader',
  'phase_normalization_paths',
  1,
  'unset',
  'unset',
  '4f695ad9c1115d8bbaac83be399ca60cb0cf41cc8f4a2f7e0c8dff798c56c0d6',
  '630cf4298767017cea5aa02aa6e88403bc9ffd70dbc1d7136a01da6783cf15a8',
  '4de8d8784c4936fa2ec41b5db4f7accfcf469bc33ec5f1984cbd3f6824561557',
  '3520aa5497aa46854195e81c56ec65308e3dd4ccb4d5f5ec68c9304e06558733'),
 ('ffff155a-writer',
  4294907226,
  'peridot-pony/ram',
  167368,
  (167432, 167542),
  'writer',
  'phase_normalization_paths',
  1,
  'unset',
  'unset',
  '596e450f6b5a82a6749fccede61705a98b5a0400c690b909f3bc23fca439a5e7',
  '515fdcfd99a3380d2a390222e1c575d8956b3c4dad8401bc4acc4b19d0da7095',
  '4de8d8784c4936fa2ec41b5db4f7accfcf469bc33ec5f1984cbd3f6824561557',
  '3520aa5497aa46854195e81c56ec65308e3dd4ccb4d5f5ec68c9304e06558733'),
 ('ffff193b-reader',
  4294908219,
  'economic-collie/ram',
  167368,
  (167428, 167524, 167536),
  'reader',
  'phase_normalization_paths',
  1,
  8,
  False,
  'f4e18c757da8f8186ae164e6f3fb22e51036af6e6ff1de040cd331dbe6d57735',
  '96328833ea9037739eaedef079b795d16a735497d06b62d6859222b826e94e0a',
  'a7560d28ab5c356dfc9d4aeeb11a1c9415a52d11f662fe80815c2ee68fc0fc22',
  'eb6d7e02edc6fdaf375014e65e9212fd09d052e3ccc82eddade65d51ad8a88d1'),
 ('ffff193b-writer',
  4294908219,
  'economic-collie/ram',
  167368,
  (167432, 167542),
  'writer',
  'phase_normalization_paths',
  1,
  8,
  False,
  '590d921070d8ae82f97279f0d946a2a7d0e74aab582b6e975f3cc87c70d58f1a',
  'bb50b25bd7b1e4ab861cec1c9b1caf4840a7df2d3077dc38a5a2fcdb1f55f5f5',
  'a7560d28ab5c356dfc9d4aeeb11a1c9415a52d11f662fe80815c2ee68fc0fc22',
  'eb6d7e02edc6fdaf375014e65e9212fd09d052e3ccc82eddade65d51ad8a88d1'),
 ('00028e7c-ffff1558-writer',
  4294907224,
  'vivacious-petrel/ram',
  167548,
  (167572,),
  'writer',
  'phase_normalization_paths',
  2,
  'unset',
  'unset',
  '7041bfbde9bd7daf310c37953c840411e76a35029abe3745be79eee1a471b9ed',
  'd7e6747681447aa99729dce1ee9c08d8af7c77aec397abb5973a9f74aae129cd',
  '1f8e7115936d16325390dcb4a71392e88c432d2f9994a84f1050c05681dbf2ab',
  '02d5df8584761c357574a03f4b75505a917a55d9722df46a6d2d2f78ab726442'),
 ('00028e7c-ffff155a-writer',
  4294907226,
  'peridot-pony/ram',
  167548,
  (167576,),
  'writer',
  'phase_normalization_paths',
  1,
  'unset',
  'unset',
  '30da7b19c7975d4070dfee9be1037b34c4affb914b795210099f2410ba113a41',
  '6090982220b9287fdaa1eb3300a7e38df82c6a5ba8d7f2ea6783f9ed12c82d10',
  '4de8d8784c4936fa2ec41b5db4f7accfcf469bc33ec5f1984cbd3f6824561557',
  '3520aa5497aa46854195e81c56ec65308e3dd4ccb4d5f5ec68c9304e06558733'),
 ('0002b64a-ffff166c-writer',
  4294907500,
  'injection_offset_reciprocal_residue/ram',
  177738,
  (167576,),
  'writer',
  'phase_programmer_paths',
  1,
  8,
  False,
  '1727fb656a3f1458c2a2d315eed5a6bfb847dceecf067916b128f2bcae1e8254',
  '5a23c79e6cd5683408ef097b75fbf9bc050da4eb53e3e38ce1754a25e698d97a',
  '870f566755ab2023ec2fb3b9e2d4932f085ff195c99e71d4f9ae45010eb6bb84',
  'cba063e311233e8ad9939a13f79358a0a480c7456476a488b85c884b8564f60e'),
 ('0002b64a-ffff16c2-writer',
  4294907586,
  'amphibian-panda/ram',
  177738,
  (167572,),
  'writer',
  'phase_programmer_paths',
  2,
  16,
  False,
  'f998ea9ba5aceae53c66b760e004e85c6478e1fe21e51a0626dc0881eeb763d5',
  'bd4909d1d1457beb255e4eed97ba4cc7d9a0fddb80f165cf618d6ca1a5ce2617',
  '42d5b7e0b0a0fce8518cfa1115aa1b025ae4cceb45567aee6522812be6d1efe3',
  '860b7029b47590581a9ec600683f5d2c9c1e3bb48d38847dc9e1858abae3e17b'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-phase-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the phase normalization claims change their exact native admission boundary')
    keys={'id','address','owner','function','sites','direction','source','component','original_claim_sha256',
          'original_claim_json','proposed_claim_sha256','proposed_claim_json','original_native_sha256',
          'original_native_json','proposed_native_sha256','proposed_native_json','original_ledger_json',
          'proposed_ledger_json','original_symbol_evidence_json','evidence_json','width_bytes','declared_width','declared_signed'}
    originals,proposed={},{}
    for row,pinned in zip(value['reference'],IDENTITIES):
        identity=tuple(row[key] if key!='sites' else tuple(row[key]) for key in
            ('id','address','owner','function','sites','direction','component','width_bytes','declared_width','declared_signed','original_claim_sha256','proposed_claim_sha256',
             'original_native_sha256','proposed_native_sha256'))
        if set(row)!=keys or not test_contract.exact(identity,pinned):
            raise ValueError('a phase normalization claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the phase normalization claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='phase-normalization-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the phase normalization proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two phase normalization claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two phase normalization claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the phase normalization claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the phase normalization owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the phase normalization grouped owner transition changes another native fact or evidence position')
    return value


def item(row):
    return json.loads(row['evidence_json'])


def symbol_key(row):
    return SymbolKey('7mfk','ram',row['address'])


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def qualified(row,link):
    return test_contract.exact(canonical(link),json.loads(row['proposed_claim_json']))


def registered(evidence):
    return (evidence.get('mode')=='phase-normalization-access' or evidence.get('path')==DESCRIPTOR
            or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def publication(link,evidence):
    """Only an exact pinned owning append is neutral to an existing physical scope."""
    if not registered(evidence):
        return False
    identity=digest(canonical(link))
    return any(link.owner.key==row[2] and evidence.get('key')==PREFIX+row[0]
               and identity==row[11] for row in IDENTITIES)


def operation(row):
    claim=json.loads(row['original_claim_json'])
    return dict(cmd='link',meaning=row['owner'],type=row['direction'],to=claim['to'],evidence=[item(row)])


def operations(ops,root):
    selected=[op for op in ops if any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    expected=[operation(row) for row in descriptor(root)['reference']]
    if len(selected)!=len(expected) or sorted(map(digest,selected))!=sorted(map(digest,expected)):
        raise ValueError('the phase normalization publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('huge-lori/ram', 'reader', 'apc_command_phase_normalizer/fn'), ('huge-lori/ram', 'writer', 'apc_command_phase_normalizer/fn'), ('vivacious-petrel/ram', 'reader', 'apc_command_phase_normalizer/fn'), ('vivacious-petrel/ram', 'writer', 'apc_command_phase_normalizer/fn'), ('peridot-pony/ram', 'reader', 'apc_command_phase_normalizer/fn'), ('peridot-pony/ram', 'writer', 'apc_command_phase_normalizer/fn'), ('economic-collie/ram', 'reader', 'apc_command_phase_normalizer/fn'), ('economic-collie/ram', 'writer', 'apc_command_phase_normalizer/fn'), ('vivacious-petrel/ram', 'writer', 'split_u8_by_ten/fn'), ('peridot-pony/ram', 'writer', 'split_u8_by_ten/fn'), ('injection_offset_reciprocal_residue/ram', 'writer', 'pumpkin-peacock/fn'), ('amphibian-panda/ram', 'writer', 'pumpkin-peacock/fn')))
