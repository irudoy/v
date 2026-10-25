"""Exact grouped native counter array appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.counter-access-claims.toml'
PREFIX = 'counter-array-access-v1:jk08a:'
IDENTITIES = (('ffff2571-writer',
  4294911345,
  'competent-scorpion/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  'f9309d993203ebd31f81e3034e05c8ab29ebbb14e6e893d33b14bc8a6f078aae',
  '46ce8ae892ff787b12c415c871210700eddb91d8bca42ef7594b9674c79e6cd7',
  '16a6f135e93e820503845f731b6aaf85f88f317d21ac7ff1432827245c41960c',
  '55e7fb996540becfa4e9efb0a12d87f064717c5a9bb142b9f8d72cea2623cf4d'),
 ('ffff2572-writer',
  4294911346,
  'prehistoric-polecat/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  'e72499732db40c2b2714fa3a48c41c9d05efe4bcf2f90b63a87852d6e3d12cab',
  'eeaf8f4a12534b7750e1d7e7d48593cba1ff0286026c9b6cb64b7d284e60ce67',
  '1a77a63021a365c68556ce75d45485aa11b52271c28b81f2c072cf5b80274fd0',
  '0eab52a51ef07086da690149af0a6b250f966e83fad307d731e9003afc797062'),
 ('ffff2573-writer',
  4294911347,
  'authentic-monkey/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '62f0c21e738d756080678370cf0f9b7d35abbab75bb05955dd12021cafdd804b',
  '688e8ea657d3fd7d1265b9b3aeaf4b169b4ca30f5f37a950600499ae14ca27bb',
  'c7589b2ce3724335e1c311c7fa4c7757e2fc2915d9586279de26e1c97db5e13d',
  '670f76b5c8d1c7828b3dc410d1c5e302bf6dfa18c8cd51a56909119ff15ce7c1'),
 ('ffff258a-writer',
  4294911370,
  'affable-prawn/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '1ff1de3f0032dcabd2661fff796a7cd8cbe0c0ab367e0ea697da8e56a5e14066',
  '5db5dda97cb41c7c365999c4aae49e0269e862786dee04b50b1b66e6636690e9',
  'cb6eb58d1382e7a2bc3a1314129787e8f1124992d8bddcf15ad996fc7121a0ae',
  '73f9d39092953490bb2a45db01613d6ad098a9feae5f735ebd14f045572280cf'),
 ('ffff2590-writer',
  4294911376,
  'crimson-binturong/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '68b243e83f4489108bf45730958db13b69779c2ab9e922bfe4da531f3fbea6ed',
  '5077d705bcc60a9ac38800d752ef2b39cc397d659bf9e90b055df5cae117c890',
  '19700f5f8ff330dbc30e736712917175e107ce6df9d32b383342591909911063',
  'f46d8fbb24666e99345bb0835ba876c5a3fdae051b325f444451fbf7ae595cb5'),
 ('ffff25e7-writer',
  4294911463,
  'magic-viper/ram',
  132108,
  (132546,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '306f4793d3e4563428aae4ff2ada161c7c0d7e798ce3457b0c87a2865345d747',
  'a46ccfea15625a108c152b8d6da4b4f4938b7baf7c10b2cd309df13c5ef38b81',
  '08a0894b4dd513270f07c4ec26b2f2dd827666e7468d9124cddc28a449823a22',
  'c003d83ef3635ab9634ae17fcb6b746025632ed63ab6896a9144d435d9e031a1'),
 ('ffff43be-writer',
  4294919102,
  'silent-elephant/ram',
  132108,
  (132798,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '9f15ea96a8cd7409922af6619647e60bac2b48f85b57b00ebf40a98ea4580dcf',
  '4a477aadfd1e0b02b83fe5e9feaffc661b43c1679706405bb4a40a63414f764b',
  '81f3ef6c222c43591059c2a98cc0813cd7a731846a5ef1641e2f5e07a89587b2',
  '19c11fb8fbcb83bd672364ceab0368b11ad3dcb2c22414c6d6d4d807db516ecc'),
 ('ffff4413-writer',
  4294919187,
  'aboriginal-dinosaur/ram',
  132108,
  (132622,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '200b7425ca3056320bebbcfe32286821b464ea79093c6eac822824451c36622e',
  '68221a007e3014390c1b052b2734c5414e17688069d7645e00e790cf70a50d68',
  'fbf0e6da57b0964ba04a72a40ec88d8fc3ac25f245eb314cef102ecf13c0ed24',
  'dacb2dad00f88439e5950e075e993fd103e114537583757759a8bff46f69dbbe'),
 ('ffff25ff-writer',
  4294911487,
  'event_interval_holdoff/ram',
  133368,
  (133462,),
  'writer',
  'counter_array_paths',
  1,
  'unset',
  'unset',
  '6cd674ec09b33c88479f35bb09d7dc472ff4a655f4d7ee8849b3cf75d3c11c57',
  'c50d0cfeb115929583ec09bf1ded814061e3550bea3e78ea0d28441b148b4598',
  'bd6ea6909ba9c08e9ecd8dfb9c1149358bed8e2860f169bf7086fe6dad365061',
  'abd5d1b1d932e473287fc2de133e9693385a2a92d11b6473ca651c2aeccca482'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-counter-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the counter array claims change their exact native admission boundary')
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
            raise ValueError('a counter array claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the counter array claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='counter-array-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the counter array proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two counter array claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two counter array claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the counter array claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the counter array owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the counter array grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='counter-array-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the counter array publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('competent-scorpion/ram', 'writer', 'periodic_tick_isr/fn'), ('prehistoric-polecat/ram', 'writer', 'periodic_tick_isr/fn'), ('authentic-monkey/ram', 'writer', 'periodic_tick_isr/fn'), ('affable-prawn/ram', 'writer', 'periodic_tick_isr/fn'), ('crimson-binturong/ram', 'writer', 'periodic_tick_isr/fn'), ('magic-viper/ram', 'writer', 'periodic_tick_isr/fn'), ('silent-elephant/ram', 'writer', 'periodic_tick_isr/fn'), ('aboriginal-dinosaur/ram', 'writer', 'periodic_tick_isr/fn'), ('event_interval_holdoff/ram', 'writer', 'gentle-bat/fn')))
