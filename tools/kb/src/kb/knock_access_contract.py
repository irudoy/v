"""Exact grouped native bounded knock appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.knock-access-claims.toml'
PREFIX = 'knock-access-v1:jk08a:'
IDENTITIES = (('00049ffc-0001108e-reader',
  69774,
  'amorphous-bird/tbl',
  303100,
  (156944,),
  'reader',
  'knock_accesses',
  2,
  'unset',
  'unset',
  'a1fd54ff5cae129cbf494b930699f81443ebf239ce1008fc55d1c1adb2dfed27',
  '437c9f2314f3981c40cdfeadafd3eec11712c1a016772fc9f63376b13764dfd6',
  '11eaf40948a4e49be192b5d19cba6167fdcd368f7af4c7c201567ae680c41111',
  '790757985eea7186ed2fdcd4b9da58e7e488ee92fa3a4192a002c7e541a1537d'),
 ('0004a238-0001108e-reader',
  69774,
  'amorphous-bird/tbl',
  303672,
  (156944,),
  'reader',
  'knock_accesses',
  2,
  'unset',
  'unset',
  'da88b7f76b0ad5d2582cdeedb2397c6754964b902631873b99daed26dcfe39d3',
  'b627e2c9d0eb29cc34bc519193a17335bfd52a64e9e8b0a41c52c0409542385e',
  '11eaf40948a4e49be192b5d19cba6167fdcd368f7af4c7c201567ae680c41111',
  '790757985eea7186ed2fdcd4b9da58e7e488ee92fa3a4192a002c7e541a1537d'),
 ('00026984-00015340-reader',
  86848,
  'laughing-caterpillar/axis',
  158084,
  (158086, 158108),
  'reader',
  'knock_accesses',
  2,
  'unset',
  'unset',
  '9bc99705effa847ba5363f6a37916757c5b2d4658e71cc3832cb88208f256586',
  'e94041d033b2408a83e83ed95b1b7ade4a492e69cb0541104bde6408bccc6e7d',
  'ad4456be586d0090e4398994fd2e66bcf89c77f8248c546ad3253a7ec72dfbb4',
  '5c78850ce19034f5bd4aaa30dafa2407b76c7d68ebb78d05eddd700fec9139dd'),
 ('0004a238-ffff20d2-writer',
  4294910162,
  'knock_normalized_cache/ram',
  303672,
  (303782, 304106, 304198, 304276, 304492, 304524),
  'writer',
  'knock_accesses',
  2,
  16,
  False,
  '2046f85f1348c652aa746c4f3cf05ed626cd0302e370fa3e3032c9705ec0c283',
  '37df8a06b26839a307ef961bb771ff71fb5952a6b5b768bbaaeeda59f5cdb1da',
  'ccd3a9230b7cba5f1d66c0accf585227dd433acd90bcef25ead43430591c6b29',
  'f2d0c00c6f86efc1a4e0b26554042ee9a34485e5a8f18be7b397f0cdd34b86e0'),
 ('00049ffc-ffff2144-writer',
  4294910276,
  'knock_threshold_base/ram',
  303100,
  (303162,),
  'writer',
  'knock_accesses',
  2,
  16,
  False,
  '2e21f6107e6524e00c3725a7edd1a08d08e4a1092f987abb8500b46e81078f8b',
  '948407cfc0a13d2ef75c777fc35ee54fe299ab7db698aa686c9be4b24de3bba4',
  '6bc3a364e119e5c35726f8eb6db22ed3e5c8b6bd85a7627aa3f9246f7ee255f1',
  'f519299f8e851badb486bd85ab4fae3cfe50460bf1492d61e6cac30dfa778799'),
 ('00049e96-ffff21d8-writer',
  4294910424,
  'knock_metric_base/ram',
  302742,
  (302924,),
  'writer',
  'knock_accesses',
  4,
  32,
  False,
  '18b35b6c03ace54bdf03fd849f18420da5bfe75c174a1f0e55e86ad133b08dc0',
  'bf9960d7edc2d5c54ad531686cde9ee53db7a4721e0174072abbddee9717c164',
  '0233724ef9c202c9eb9bd2d5a38124601a2de9c151dc7c56e0f1faf1fd1c435a',
  '7e630d884309ba369ebde7c0434df05bbc1d093e74a3a7daebd7925a69136d56'),
 ('00049e96-ffff21f8-writer',
  4294910456,
  'knock_signed_metric_base/ram',
  302742,
  (302898,),
  'writer',
  'knock_accesses',
  4,
  32,
  True,
  '86b41d2c123f962e160472435a185a5aaeef5c99da071e0c4f15ea6dd8b149b4',
  'a1309ef7b1c2f3cec048aa5c6b5cc34cd4868c22f06eeefee41dbdca70238f27',
  '1b4957eb1f746e96368df95289353970a7f33f86e2a747ba0b93c2482d4875ac',
  '8df2fa31dfa57065ce659880efdabaea87c2b24fee58e6a32d604a6902ae935f'),
 ('00049d88-ffff2274-writer',
  4294910580,
  'knock_metric_sum/ram',
  302472,
  (302694, 302740),
  'writer',
  'knock_accesses',
  4,
  32,
  True,
  '23b1c0fd64619ad43b474965aae66d2983cfa3362ce5a3fc4019c453bb384ff7',
  '9cdd135ea44617117b5528f1181ce739550af9d1a45af2339e1774a5f7cc962f',
  '1dad161e565e48dd81760d59816730c0f611f4ef0397a177af80fc14ec7224dd',
  'e92892e02e26ccd4263deeac7f153b459955d54c7f0d6a852736e2bc6c5811f6'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-knock-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bounded knock claims change their exact native admission boundary')
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
            raise ValueError('a bounded knock claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bounded knock claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='knock-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bounded knock proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bounded knock claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bounded knock claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bounded knock claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bounded knock owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bounded knock grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='knock-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bounded knock publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('amorphous-bird/tbl', 'reader', 'knock_slice_threshold_lookup/fn'), ('amorphous-bird/tbl', 'reader', 'knock_slice_evaluator/fn'), ('laughing-caterpillar/axis', 'reader', 'versatile-junglefowl/fn'), ('knock_normalized_cache/ram', 'writer', 'knock_slice_evaluator/fn'), ('knock_threshold_base/ram', 'writer', 'knock_slice_threshold_lookup/fn'), ('knock_metric_base/ram', 'writer', 'knock_metric_scaler/fn'), ('knock_signed_metric_base/ram', 'writer', 'knock_metric_scaler/fn'), ('knock_metric_sum/ram', 'writer', 'knock_selected_difference_sum/fn')))
