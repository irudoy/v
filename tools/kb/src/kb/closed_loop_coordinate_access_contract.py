"""Exact grouped native bounded closed-loop coordinate appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.closed-loop-coordinate-access-claims.toml'
PREFIX = 'closed-loop-coordinate-access-v1:jk08a:'
IDENTITIES = (('0003edb4-00008f98-reader',
  36760,
  'closed_loop_coordinate_midpoint/tbl',
  257460,
  (257978,),
  'reader',
  'closed_loop_coordinate_paths',
  2,
  'unset',
  'unset',
  '44d1de3f441125192062f317e57128bdae1c7ed7439726480c2e51e0e427d622',
  '3d39c42f35ad348538481021419645c6135c9e3609b05f94730623d9ecf736b6',
  '1e9cdd05acf3bba6868deef3222aaae07197dc0566a7f79161af34d55a31096b',
  '70ebd56f7e2cf12e374717b1930b2fca1dbb04e97cd1c96f13c3f86449e77f50'),
 ('0003edb4-00009384-reader',
  37764,
  'closed_loop_coefficient_upper_gate/tbl',
  257460,
  (258348,),
  'reader',
  'closed_loop_coordinate_paths',
  2,
  'unset',
  'unset',
  '5c78f99c7c9498845cc3d6497fd6d597dbca218784361a9011aad8900c9a690d',
  '4ebf8364da35d80ce5f2cb3e13900386d16b0771d7025bf9ad7ad2d9c774d473',
  'b19044831131282387c175ec3422ef4e74b9dbdcd926dcc75b6d122145db757c',
  '2ebd9762cc0e22dee16821023cf98ffbac6272c6a0a7d3e5e31833ac83a815e7'),
 ('0003edb4-00009386-reader',
  37766,
  'closed_loop_coefficient_lower_gate/tbl',
  257460,
  (258356,),
  'reader',
  'closed_loop_coordinate_paths',
  2,
  'unset',
  'unset',
  '402b71f74a53a552c68a02ec8874415cdb7bbcc9ea8fadc4f715a833f6397878',
  'ea4ab5b5336509cfb9c3458b3630a8e8e781b419e8ddc5704702d99f18cc5fe0',
  '92f2068363c87de49b5e7b8524aec687b4c0107ca38e37170fbd64d0ec77510e',
  '5cb107f06da674426cf4fe1cd9d800d07f63658ee571b802d6f6be76d6e2c6f2'),
 ('0003edb4-000095c6-reader',
  38342,
  'closed_loop_speed_lower_gate/tbl',
  257460,
  (258338,),
  'reader',
  'closed_loop_coordinate_paths',
  2,
  'unset',
  'unset',
  'cdfeaf26dc575a7618a29d612ea4d07716b96c0cac5cc2e463b6b7d627d70378',
  'b4345c224379d51749f4b2c675903801b3f8f88bf4ea6fb7841f356ccb5b560f',
  '9f32392c45ecf54655a1b801d0d017fa75344bac22047f5b9824c6e2228d2487',
  '78580e4fa77007b17dfc5c641cce1fddc2c8da642b052c777b855e75b02b4936'),
 ('0003edb4-00012292-reader',
  74386,
  'elite-turaco/tbl',
  257460,
  (156856,),
  'reader',
  'closed_loop_coordinate_paths',
  1,
  'unset',
  'unset',
  '5076445eec74c44c454f5703a20ebdf503ce7cdd0045df72a3cbd5268e6d7dfa',
  'f28bcf49bc12abfb95d588c7189a7f36506fdd8d7aeed3a76eac83ee04b7b678',
  '6fbbf2c87ce51ad027b63fa12fce63184647eba698d0e669867809bed918b199',
  '03806b398ea3be31a3005d8a1a293ae6e1c9ad4bcbf18f8560323b165062b397'),
 ('0003edb4-ffff2f8e-writer',
  4294913934,
  'grinning-skink/ram',
  257460,
  (257968,),
  'writer',
  'closed_loop_coordinate_paths',
  1,
  'unset',
  'unset',
  'cc3d132e2f997b1be34f25ed9415e718fafc237c4a559683b013363347b08ee1',
  '8d439a970f65d159d51190a6239a7a984b3e371f1f73175721e16211ed20777c',
  'c18efc41db5be8b1c277555d99ba5d3d2abbf0960866583816ff20cf947c1680',
  '11b263a69f8d4947fdc8515f70ef82cc05e8e5e85445db5414660f90d9104d7d'),
 ('0005d6ae-ffff895c-writer',
  4294936924,
  'crazy-lynx/ram',
  382638,
  (383046,),
  'writer',
  'closed_loop_feedback_paths',
  4,
  'unset',
  'unset',
  'a535e94809431d88296eb098fe16dba75bdbc75336929ebcf4901ad4eca2ef21',
  'a5e76f4317ab4fded692e641c2cc9b591b02dcff4daa747988a426b3f89ddc36',
  '6274f98140df9235f06c5e5ea6c90f3062f2d1f6d76d8b8a76336b0c474be4c4',
  'fbaf567da119493682fa3f3290bb38a2b55913c4b932f9490f4337acee1527bd'),
 ('0005d6ae-ffff8960-writer',
  4294936928,
  'arrogant-walrus/ram',
  382638,
  (383054,),
  'writer',
  'closed_loop_feedback_paths',
  4,
  'unset',
  'unset',
  '63359c57e6cdc7369d8ed9791a015cd55b6f1fb8708da9b267608a6585551cae',
  'd8874fb49bed97deaded2d3118dfc8ccbc930143f5fa7d4deb141c4a8744cca6',
  'd09ff48e3979e80d4d37c2c7e7b3acf50827f68b96d931ce5eb644f239371e6e',
  '861e17593d942ec79966dbaf2467ee8f9594afe0f35c08c15dc6bbddedd1af5c'),
 ('0005ca8c-ffff88ba-reader',
  4294936762,
  'closed_loop_feedback_transition_counter_b2/ram',
  379532,
  (379696, 379770, 379804),
  'reader',
  'closed_loop_feedback_paths',
  2,
  16,
  False,
  '38efa109e85c2b7158788ad15506c4d7062ba6adcbc0fff08decbcf570e38d47',
  '7742b466bb37e40a10737665a7fbbee69d2474a2289654946760d13596dcc140',
  '85912f7e76f4da2b5b444083a7971de57e3a5d66721cf14122685093b3f84067',
  'a561bbf4723bbf6eb3854af2984dce19b0c39b00920762bce71f1d74047df78b'),
 ('0005ca8c-ffff88ba-writer',
  4294936762,
  'closed_loop_feedback_transition_counter_b2/ram',
  379532,
  (379818, 379836),
  'writer',
  'closed_loop_feedback_paths',
  2,
  16,
  False,
  'c186b5d66d2b6ac73439c2ffc4431b3b4386042fc333010e6038738c4b1c4c6f',
  '5c3d0d9e35d61ba37bbf12a29202ad46b0e1b1447b1875614a271a45694b0c7a',
  '85912f7e76f4da2b5b444083a7971de57e3a5d66721cf14122685093b3f84067',
  'a561bbf4723bbf6eb3854af2984dce19b0c39b00920762bce71f1d74047df78b'),
 ('0005525a-0000990a-reader',
  39178,
  'fuel_coolant_coefficients/const',
  348762,
  (349158,),
  'reader',
  'closed_loop_coolant_paths',
  1,
  8,
  False,
  '73ac1338a230b99a635d72a05d8b67a68c562379048b03c1ffcccbb005a9d338',
  '9d2fd0ad972b517a53e51dfeba8311f807ccce92e5a2b7795104952c1b6758bf',
  '9e705a674561a60a3b1e4511ae98835fcace8f35b6bda8e390e3bba8a7129058',
  'd4a6efc0facf05dd653335e9a20fb40783df292538cec46b70d5591f457a090c'),
 ('0005525a-0005533c-reader',
  348988,
  'fuel_coolant_coordinate_offset/const',
  348762,
  (348970,),
  'reader',
  'closed_loop_coolant_paths',
  2,
  16,
  True,
  'd773155aadf3691cc8cd12896b8a1eb2698b8ff6ac0722d99db603c9a2939544',
  '186d1c548be0096477c25752c68d79d31b75bf41e543539abda3fe24e3192b28',
  '9c86c591d39dcb47756035857103c20bc8f4541e06335c9c3d7905ab932728c0',
  'b665e5cad1e33eec7d21fc152179d760de22a195b9a86bbe3b56ebe8b8d68db8'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-coordinate-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bounded closed-loop coordinate claims change their exact native admission boundary')
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
            raise ValueError('a bounded closed-loop coordinate claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bounded closed-loop coordinate claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='closed-loop-coordinate-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bounded closed-loop coordinate proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bounded closed-loop coordinate claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bounded closed-loop coordinate claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bounded closed-loop coordinate claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bounded closed-loop coordinate owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bounded closed-loop coordinate grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='closed-loop-coordinate-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bounded closed-loop coordinate publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('closed_loop_coordinate_midpoint/tbl', 'reader', 'enlightened-orangutan/fn'), ('closed_loop_coefficient_upper_gate/tbl', 'reader', 'enlightened-orangutan/fn'), ('closed_loop_coefficient_lower_gate/tbl', 'reader', 'enlightened-orangutan/fn'), ('closed_loop_speed_lower_gate/tbl', 'reader', 'enlightened-orangutan/fn'), ('elite-turaco/tbl', 'reader', 'enlightened-orangutan/fn'), ('grinning-skink/ram', 'writer', 'enlightened-orangutan/fn'), ('crazy-lynx/ram', 'writer', 'funky-toucanet/fn'), ('arrogant-walrus/ram', 'writer', 'funky-toucanet/fn'), ('closed_loop_feedback_transition_counter_b2/ram', 'reader', 'closed_loop_feedback_transition/fn'), ('closed_loop_feedback_transition_counter_b2/ram', 'writer', 'closed_loop_feedback_transition/fn'), ('fuel_coolant_coefficients/const', 'reader', 'knowing-potoo/fn'), ('fuel_coolant_coordinate_offset/const', 'reader', 'knowing-potoo/fn')))
