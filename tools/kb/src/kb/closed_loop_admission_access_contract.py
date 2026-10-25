"""Exact grouped native bounded closed-loop admission appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.closed-loop-admission-access-claims.toml'
PREFIX = 'closed-loop-admission-access-v1:jk08a:'
IDENTITIES = (('000a0ee8-ffff97a9-writer',
  4294940585,
  'closed_loop_integrator_admission_2c_b2/ram',
  659176,
  (659238, 659240),
  'writer',
  'closed_loop_admission_paths',
  1,
  8,
  False,
  'c171e3d6192e851ffb705d1ce3b00424ab504ef84032647bbc28fd686e5691f1',
  '6b90f98d38d031d8772a26241ef4d463997220b72db9027efa1a50b5a0c116a9',
  '4a51843632ad9a9ac784643147aa82f30830be28f3b0c14478de5b3bcfa519fd',
  '4449c66d73002675dc9c862b13fbc515f83d61d2b2e4c1438857882412765c69'),
 ('000a0ee8-ffff97ab-writer',
  4294940587,
  'closed_loop_integrator_admission_2e_b2/ram',
  659176,
  (659276, 659278),
  'writer',
  'closed_loop_admission_paths',
  1,
  8,
  False,
  '0ac99c02c39236a1da3f2cb78579bac9ff61848bab6dcd116462692b7f1e3b19',
  '256fa868893fb326a256d02ba5e756adae144f7551fe9e85ef64ab0bcd10c243',
  '431b937a3140b727f59a9dacd4572b5728c569db980cca51283baab015261d80',
  'b48d00b5f8915ae5e81c9e91a0f077d025940cf0cf8ab24eb5caab140a797da5'),
 ('000a0ee8-ffff97ad-writer',
  4294940589,
  'closed_loop_integrator_admission_30_b2/ram',
  659176,
  (659314, 659316),
  'writer',
  'closed_loop_admission_paths',
  1,
  8,
  False,
  'acd74ab55ab623541a5009921f627691c0cc26ffb18c08c77101742867266004',
  '12eae24bb6e45b2feb3e273638a3fea64928e4713796d60ff30dc4c944914d1f',
  '5fa195c4cd6a8a6a47519c53e2bb7fd7579699fbe794214c8fc41729afd0c7eb',
  'ea1087bc42e632c2abf78b85c35807c4d2cefbbde72c13157d0655416ceac6ae'),
 ('000a0ee8-ffff97b6-writer',
  4294940598,
  'closed_loop_integrator_admission_39_b2/ram',
  659176,
  (659482, 659500),
  'writer',
  'closed_loop_admission_paths',
  1,
  8,
  False,
  'e00035df500450f717b75c830ae51e90afa3ec3477564ad49421300634d6ddef',
  '0540595d143f38b6f2e2e3c08a9a0e8fd0234d1f1deaa11037c2387f6845334b',
  'e7de9c8e006a157e000244db0a253c1a83fa78ad4e8456293f0159ea9f0e41a9',
  '95643a9bcb88e3ca50b9a0412a17efd2b26b012087cb64983b5d734eb382dac2'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-admission-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bounded closed-loop admission claims change their exact native admission boundary')
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
            raise ValueError('a bounded closed-loop admission claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bounded closed-loop admission claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='closed-loop-admission-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bounded closed-loop admission proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bounded closed-loop admission claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bounded closed-loop admission claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bounded closed-loop admission claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bounded closed-loop admission owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bounded closed-loop admission grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='closed-loop-admission-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bounded closed-loop admission publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('closed_loop_integrator_admission_2c_b2/ram', 'writer', 'diamond-dragonfly/fn'), ('closed_loop_integrator_admission_2e_b2/ram', 'writer', 'diamond-dragonfly/fn'), ('closed_loop_integrator_admission_30_b2/ram', 'writer', 'diamond-dragonfly/fn'), ('closed_loop_integrator_admission_39_b2/ram', 'writer', 'diamond-dragonfly/fn')))
