"""Exact grouped native bank2 CVTC appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.exhaust-cvtc-access-claims.toml'
PREFIX = 'exhaust-cvtc-access-v1:jk08a:'
IDENTITIES = (('000c1dec-ffff1aa8-writer',
  4294908584,
  'flat-oryx/ram',
  794092,
  (794612,),
  'writer',
  'exhaust_cvtc_transition_paths',
  4,
  'unset',
  'unset',
  'ea4ae236c35be6880fce19389d65f3a9bd0e2c8fc75d97d566d04104e0d46430',
  'fcdd4f7e3e4dea2854bc9df0c7370fffd0d553a4b123581aece6dc9eabc17b25',
  'c81c8e4d25f263513ffbdfc69c22c49000adfaf4640f45dd92301082ec47b106',
  'd090f36761a2124d60a93cd80399325a9563f23e2a385b5ac67dbcecbc268464'),
 ('000c2040-ffff1aa8-reader',
  4294908584,
  'flat-oryx/ram',
  794688,
  (794718,),
  'reader',
  'exhaust_cvtc_transition_paths',
  4,
  'unset',
  'unset',
  'c41a5aacad7934ba20b3457bcd94a265c20d0efbff0942db9776a0ee6d5dab5e',
  '19bc774a13b0ec52bc379a4f6ff41692f584920b2930bfc12b497a387cc3f337',
  'c81c8e4d25f263513ffbdfc69c22c49000adfaf4640f45dd92301082ec47b106',
  'd090f36761a2124d60a93cd80399325a9563f23e2a385b5ac67dbcecbc268464'),
 ('000c1dec-ffff1aae-reader',
  4294908590,
  'exhaust_cvtc_duty_b2_word/ram',
  794092,
  (794232,),
  'reader',
  'exhaust_cvtc_transition_paths',
  2,
  16,
  'unset',
  '12cbbb43fad9a55151ad24b50568ba99a723cf99c94adf2fabd2148c841b1886',
  '057c3166898b2093e4f6ea95918224cfbfed97d148508e0911b564929ff06e20',
  'ce0240563c09d7a17a1dac9337d7426238b1de83d496b9b8ad67a56e1cb6f510',
  'e7ad66879fa192ec4e542a29efc8ecaba60b1960fe8c6148f76b6607766c956a'),
 ('000c2040-ffff1aae-writer',
  4294908590,
  'exhaust_cvtc_duty_b2_word/ram',
  794688,
  (794942,),
  'writer',
  'exhaust_cvtc_transition_paths',
  2,
  16,
  'unset',
  '6fb60c109afdd80ed598972cc0db7a81a509e2c4a1e2c69571f233474b8b3d00',
  '86345050dc05861ae015624a72a24c59c7f8ecab3ded8e894e1f1f4d18462c18',
  'ce0240563c09d7a17a1dac9337d7426238b1de83d496b9b8ad67a56e1cb6f510',
  'e7ad66879fa192ec4e542a29efc8ecaba60b1960fe8c6148f76b6607766c956a'),
 ('000c2040-ffff1ab6-reader',
  4294908598,
  'bizarre-civet/ram',
  794688,
  (794900,),
  'reader',
  'exhaust_cvtc_transition_paths',
  2,
  'unset',
  'unset',
  'f2d3a94b1950ab977cbcc8a20208a6dbedeb1679d60c57ba5942c7bc26c96284',
  '566d09f32eb37e3ea3945712b91b013a88ebdda643b898d4e6cdaa77cbdb6ef9',
  '7c16e718a31d314fe725fbcf020b7b5d7406b12e71bd4fd53414949865eefbfa',
  'b2b731e559696593bddff53884099141095eef57ee9660f7b853827b42d623fa'),
 ('000c2040-ffff1ab6-writer',
  4294908598,
  'bizarre-civet/ram',
  794688,
  (794842,),
  'writer',
  'exhaust_cvtc_transition_paths',
  2,
  'unset',
  'unset',
  '5e7c262146cf9a3f85c646d10f94c4dc7d865a69e71e692e69171fa11bcbdc74',
  '94edd7f3e46f58d00a4af2d4c2bb28a87ddac02baeaad34f2c8c5e64fe958ebc',
  '7c16e718a31d314fe725fbcf020b7b5d7406b12e71bd4fd53414949865eefbfa',
  'b2b731e559696593bddff53884099141095eef57ee9660f7b853827b42d623fa'),
 ('000c1dec-ffff1b1a-reader',
  4294908698,
  'maize-chinchilla/ram',
  794092,
  (794380,),
  'reader',
  'exhaust_cvtc_transition_paths',
  2,
  'unset',
  'unset',
  '4cd7be91561e9bc2eb84f9c00a599f9d7306ee0b0e8381a5b427f53636a14953',
  '96701c70a38cc2b6b1d8c5c89059e320fd69790ae58907fea287b3566e814fe7',
  '85b2ab6ee2306674385b491c6e0f70b2836cdadef6af53db0c68d957831c5bb8',
  'f1cb7fc045d4551e5f4b2db1eccd22da693f950e332f1f0010b2913ef2421b29'),
 ('000c1dec-ffff1b1d-reader',
  4294908701,
  'elastic-frog/ram',
  794092,
  (794118, 794300),
  'reader',
  'exhaust_cvtc_transition_paths',
  1,
  'unset',
  'unset',
  '61b453fd1d87e856bcb4c07fa53f2256bb9161baf3c769c15a73e80cc04d2cfe',
  'b175282cb7b77fd3ceb6092ad441cedee5a5b302d57b7bd36b9ee729d94d56b4',
  '3789c84cce4b72e87cb990a27cf60b453f731c8792e6b95b116c4da6f49bb4e2',
  '3bcbb8d62ccdd1122ad2015ae393615dd131b25d2ce5b90f51bd65b173a03117'),
 ('000c1dec-ffff1b1d-writer',
  4294908701,
  'elastic-frog/ram',
  794092,
  (794162, 794214, 794258, 794292),
  'writer',
  'exhaust_cvtc_transition_paths',
  1,
  'unset',
  'unset',
  'feba45b0fff323f06076f9a4dea717cd4c60798135a134e939ebed9f0bc4dd45',
  '90c08080edad0a4fff605bee65f113b6b05e29b05ed7875551267d91657a223c',
  '3789c84cce4b72e87cb990a27cf60b453f731c8792e6b95b116c4da6f49bb4e2',
  '3bcbb8d62ccdd1122ad2015ae393615dd131b25d2ce5b90f51bd65b173a03117'),
 ('000c2040-ffff1b1d-reader',
  4294908701,
  'elastic-frog/ram',
  794688,
  (794852,),
  'reader',
  'exhaust_cvtc_transition_paths',
  1,
  'unset',
  'unset',
  '09c6854307547c3045c7124b273525406a11955f2355b45a7a1ff629af129d6c',
  '6a015ff32b7afbf4681e08f859f55b6fe75e54685761cd58299c738194645323',
  '3789c84cce4b72e87cb990a27cf60b453f731c8792e6b95b116c4da6f49bb4e2',
  '3bcbb8d62ccdd1122ad2015ae393615dd131b25d2ce5b90f51bd65b173a03117'),
 ('000c2040-ffff1c72-writer',
  4294909042,
  'glossy-capuchin/ram',
  794688,
  (794798,),
  'writer',
  'exhaust_cvtc_transition_paths',
  2,
  'unset',
  'unset',
  'b39b24f86f0433b7b9a5fbe1013fd4e8278a20ac7abf6af6bf197177532eb78f',
  'd7ceb36257dfb940af058818eb760998d5409540ba4864b9ec4a7cb1c6eb60f8',
  '15806f38322f9f7beef7da60e4ca5a9c87d2372c1ccd447c61f4b551b198f3ad',
  '365663f51bc396573608dc77f3261f6a6fe9fc2d97d4e039c7f0849f951da311'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-exhaust-cvtc-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bank2 CVTC claims change their exact native admission boundary')
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
            raise ValueError('a bank2 CVTC claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bank2 CVTC claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='exhaust-cvtc-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bank2 CVTC proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bank2 CVTC claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bank2 CVTC claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bank2 CVTC claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bank2 CVTC owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bank2 CVTC grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='exhaust-cvtc-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bank2 CVTC publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('flat-oryx/ram', 'writer', 'orange-hamster/fn'), ('flat-oryx/ram', 'reader', 'grinning-fulmar/fn'), ('exhaust_cvtc_duty_b2_word/ram', 'reader', 'orange-hamster/fn'), ('exhaust_cvtc_duty_b2_word/ram', 'writer', 'grinning-fulmar/fn'), ('bizarre-civet/ram', 'reader', 'grinning-fulmar/fn'), ('bizarre-civet/ram', 'writer', 'grinning-fulmar/fn'), ('maize-chinchilla/ram', 'reader', 'orange-hamster/fn'), ('elastic-frog/ram', 'reader', 'orange-hamster/fn'), ('elastic-frog/ram', 'writer', 'orange-hamster/fn'), ('elastic-frog/ram', 'reader', 'grinning-fulmar/fn'), ('glossy-capuchin/ram', 'writer', 'grinning-fulmar/fn')))
