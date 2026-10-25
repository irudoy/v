"""Exact grouped native bank pulse appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.bank-pulse-access-claims.toml'
PREFIX = 'bank-pulse-access-v1:jk08a:'
IDENTITIES = (('0004ead4-ffff18c2-reader', 4294908098, 'famous-grouse/ram', 322260, (322398,), 'reader', 'bank_pulse_paths', 2, 16, 'unset', 'e02152c89a7d3553dbc1c519ea79eae4389b9207f07edd9bb68e86eae28bb142', '8355c22a9d8d71132a8d62cdecfd4ef272d46d3b5e2082d00b6e3ba15c8d23c2', '7a59ce63d155dcffc255e3f70f506c309bbb14580334b4afb7491d2b47bbb502', '75c31fead85d03603f61514049859f9691ac4f0ce30f6e2ee4814604eaf68e50'), ('0004ead4-ffff191e-writer', 4294908190, 'able-cougar/ram', 322260, (322458,), 'writer', 'bank_pulse_paths', 2, 16, 'unset', '4782e61bba1b46098272e830b4ab1a3302dbe1a7f868f45ab902203d68c5357b', '2a5b0dc70a260262edad8638d7e5c6491adc019e307100c210d61e0b6e14a9f0', '59e59fcf7aa0345e60b7d7da2988f4e58c6fb1350a49baffa9c57afc2b58de78', '729e93d776c26164e7524ddd3d730fcb4b78dc06062ec7f40b089ba7b6e7be26'), ('0004ead4-ffff22de-reader', 4294910686, 'stft_b2/ram', 322260, (322278,), 'reader', 'bank_pulse_paths', 2, 16, 'unset', 'd6c9010fdfae9011d986b2473c5d4227d54421c55beccc480b9cd3fefbdc4beb', '6b00dff3e94b44e5da4f2c0f0a531ef5c5b81af64f8e7a7e0ce4d265c6ada080', '80883e1b842e1a53c1f5cc8c1ff4e23752130da52915c9f43cdbd99af0530698', 'a4612156dd4f00a674246ddf7075468826026a8fa2445025f1ca1bc910f62e0a'), ('0004ead4-ffff2304-reader', 4294910724, 'ltft_b2/ram', 322260, (322308, 322370), 'reader', 'bank_pulse_paths', 2, 16, 'unset', 'f8272431a9a3af8d9238a77743f6a3643c415e3b21023b2f12a619d63bc195c7', 'df2b3477b9b989ab0316452ad6e6f41206fba5a126c30671371221e129ea9618', '5d2be56bd7ccea918d49fcff34c3edd098b462b8a38d626224d6c16179dc732e', '79c619b423104af9c5448a43233312b56c1b39b1153d0318b21ffbbfed8e446e'), ('0004ead4-ffff2312-reader', 4294910738, 'axiomatic-squirrel/ram', 322260, (322426,), 'reader', 'bank_pulse_paths', 2, 16, 'unset', '336208a50f16a4fc7fc608d017bcd4b03ce2da8a71b0603c47a15b3f458bd12c', 'cebdfdf879e07d82e3ef1263095ec316e88a946b1acf91ee194c75b456475584', '76d059dcf4cf4cc49d9af4d13b3936abe8d9912105ae29d0758e9eea4f4e96e0', 'af9e03faf08e797aff5a707d320a79f562f53b5b4dbb1b3316707beeffd116ee'), ('0004ead4-ffff2a26-reader', 4294912550, 'illustrious-peccary/ram', 322260, (322288,), 'reader', 'bank_pulse_paths', 2, 16, 'unset', 'f96f50f86761abb5025fca977e4d135b0e8ed118a1ac34fad355cc21f654c777', '5eeabd03bf7e43172d57b3885ffce4f01d46ef23694139c177cecde5931946dc', '418309c0e0157723d95618813feefeeb6afe118e758e1a5a826eb49a5468ccd4', '455352a5afe7578687feb300ad9f27d62f5e3fecc52273d49436cb7e3c0ad6ab'), ('0004e974-ffff18c2-writer', 4294908098, 'famous-grouse/ram', 321908, (322146,), 'writer', 'bank_pulse_stages', 2, 16, 'unset', '59a30e65317afed810d0e8d1048860f3a15c9aa6de16ad51455b753365b6d73d', '85ec22cfda3e3a178e2f6a6d692025e815f7dab2b8786231cac405db02bddb2b', '7a59ce63d155dcffc255e3f70f506c309bbb14580334b4afb7491d2b47bbb502', '75c31fead85d03603f61514049859f9691ac4f0ce30f6e2ee4814604eaf68e50'), ('0004eba2-ffff23ca-writer', 4294910922, 'injection_1/ram', 322466, (322718,), 'writer', 'bank_pulse_stages', 2, 'unset', 'unset', '6c105f8ae0b27ea50ec4e06ff507e98e8ae20bea8b21c22b20d697182ef5a892', '6323403324210f3736520830ef9c499787abd179df46c008945d5258c4fe59bb', 'df35e9d5953ed866a83ea98ba72ffcbdb7d20ffb37267fb0ae87d848b0a136a2', '75b6c4dc4356f384088a8d1c8588144a1c979e1ec18e76c846b0f0554a2da907'), ('0004e974-ffff40b8-reader', 4294918328, 'giga-eel/ram', 321908, (322064,), 'reader', 'bank_pulse_stages', 2, 16, 'unset', '1b30e3c0ddf677221b77d09d9157e96b2aaa98c67fc6951ec9f3f491229ad9e3', '15697792abc70ccbf5dd126a420dcd025570d3771a9dd192fd33bc61a453e5f9', 'ff895849c274564ccd86621a9a4b7337987284b6fd8964133eb59e232a0f73dc', 'e8ccbc016214bfc761c3d0c24ea4fc5324e02c7d9f16c6a0184930f01d0b8571'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-bank-pulse-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bank pulse claims change their exact native admission boundary')
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
            raise ValueError('a bank pulse claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bank pulse claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='bank-pulse-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bank pulse proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bank pulse claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bank pulse claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bank pulse claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bank pulse owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bank pulse grouped owner transition changes another native fact or evidence position')
    return value


def item(row):
    return json.loads(row['evidence_json'])


def symbol_key(row):
    return SymbolKey('7mfk',row['owner'].rsplit('/',1)[1],row['address'])


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def qualified(row,link):
    return test_contract.exact(canonical(link),json.loads(row['proposed_claim_json']))


def registered(evidence):
    return (evidence.get('mode')=='bank-pulse-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bank pulse publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('famous-grouse/ram', 'reader', 'bank_base_pulse_builder/fn'), ('able-cougar/ram', 'writer', 'bank_base_pulse_builder/fn'), ('stft_b2/ram', 'reader', 'bank_base_pulse_builder/fn'), ('ltft_b2/ram', 'reader', 'bank_base_pulse_builder/fn'), ('axiomatic-squirrel/ram', 'reader', 'bank_base_pulse_builder/fn'), ('illustrious-peccary/ram', 'reader', 'bank_base_pulse_builder/fn'), ('famous-grouse/ram', 'writer', 'injection_pulse_precursor_builder/fn'), ('injection_1/ram', 'writer', 'injector_channel_pulse_builder/fn'), ('giga-eel/ram', 'reader', 'injection_pulse_precursor_builder/fn')))
