"""Exact grouped native bounded RPM contributor appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.rpm-inhibit-access-claims.toml'
PREFIX = 'rpm-inhibit-access-v1:jk08a:'
IDENTITIES = (('0004ed88-0000934e-reader',
  37710,
  'rev_limit_fuel_cut/tbl',
  322952,
  (324300,),
  'reader',
  'rpm_inhibit_paths',
  2,
  'unset',
  'unset',
  '70ecbbf456f967ab36a0dd619b75a1dc94d74e9e7cd253966b1e6c3a6595bb9c',
  '1142bb104cfb1ba31edc106a6f1a59b8507e718aeeb2068da5d41c833dbfb2b0',
  '618aea0b1135c8753edf78d8e11a2a3e145ff1def03d2fc9c65f2742987c0594',
  'b3680c256a902439f3caa677e881471fe74c658cf81716b07577a8a81f3655fb'),
 ('0004ed88-ffff2494-reader',
  4294911124,
  'stirring-mayfly/ram',
  322952,
  (324260,),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  '88dc10308ffd5e3be62c092cab27746b11d0256225c8441132c52516b56b974e',
  'ba2d02155a379777f1a28c09f28623ff865cc65cb044a70d8eebeae7de67297d',
  '0132dc3ecf7a56e8bfb5ddef18d0ec2b54cf76927857d44851fdc0b18d23b123',
  '9d2fbfe7d376228eb14b08a5c11da416823bb610a9874717c7e4e27b446f758a'),
 ('0004ed88-ffff2497-reader',
  4294911127,
  'fuel_inhibit/ram',
  322952,
  (324232, 324366, 324374),
  'reader',
  'rpm_inhibit_paths',
  1,
  8,
  False,
  '8c099bb7ca1b4a5f05da81ec0523531ab58f67039c3ca8be3d51608955101d79',
  '2b71f9f61c5cab12157546ef5ed6942f74e73ddd928b6d090b07f2e2ddd5f552',
  '744faf769ac91cab7dd6c8388851a94ad346d6569046e512ea92695d5d2ca408',
  'f8b088836455da94b8c9c28b858ee8ffe4d36f19d16181b3042de3077bedbb8e'),
 ('0004ed88-ffff24a6-reader',
  4294911142,
  'xanthic-yak/ram',
  322952,
  (324002, 324054, 324218),
  'reader',
  'rpm_inhibit_paths',
  1,
  8,
  False,
  '4e6bf0da961ede02df11d8213635d811715f47d112da304d8b44a2f664a609f4',
  'c83cf5ffbb0b305461f6efea05fd51934cc8746880baa85f3b128f4ca515bd91',
  'abd50297708e2231d97a437e19ba85c0030878f85859b8bd34c244772788d378',
  'ae16c8f68e68bab087296529fe5cf4d1c6b8cef8308c6b2c601b9e986d743fc9'),
 ('0004ed88-ffff2448-reader',
  4294911048,
  'resourceful-scorpion/ram',
  322952,
  (325432,),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  'fe922e2ee599f858e5e7b731b8a6e7e88c7818b9d2b0296a0508cc0a88c25ba7',
  'dc5a56af8c57eff02d776107d9f5a5c80ce365e44b8db510ce5f408c5adc3d92',
  '60cb95970720d972fd1174f633cf341723cde6ec9421dac759e8b72190e10bad',
  'fda41d67f37305d00979a4a43dbe015eb2db6e47520f99150638302e1918444d'),
 ('0004ed88-ffff418c-reader',
  4294918540,
  'obedient-stoat/ram',
  322952,
  (326306,),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  '4b43b51dfb71f11c787306301d9bf36cff4754fa9cf04dc866bd405d7b78c5b0',
  '4fc9bf572c4973fcfd2797b98aac30aeffe4a8e65414ec8404089007cda01436',
  'c8d3e45498b14958494617e0056f91bb7132c5530710f552708da86200f8fac9',
  '13cfc843d26d4aee76df85870e47dab112a11f4d0d53f6494f79e235a64af17c'),
 ('0004ed88-ffff2489-reader',
  4294911113,
  'accomplished-chicken/ram',
  322952,
  (329796, 329816, 329818, 329832),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  '7fc0f5fa3f548c789985aaabb3ba3967fccc3dc29d356d25761fa4b6c2175920',
  '12c470a8d175db0d57884b8a293c05700cdd6c848aa723e7a5dcd74411979d3e',
  '23937b643a62eb9cb1d54e7091bb215dc63c6fd8cb0421da437beedfe9f3fe0e',
  'd447ceec3d19b2f546f62533095f694a73c4bca5724ee0cc1aa0f672a572fbdc'),
 ('0004ed88-ffff249f-reader',
  4294911135,
  'resolute-bullfinch/ram',
  322952,
  (329884, 329916, 329918, 329932),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  '8e56b36afd49334f24c716d47e06314da2ca1093eb22a6b6d49f4627126c7c7c',
  'd5ff8c4fe16d14d9e4c0796e60f06def090ce1848e275ffaf6971d597dcfa4d5',
  '9be7ed657ae95ef974ee6caf8e2dc478bf4cfdaddf124a27da28ec38eda9f238',
  '181bec088b5d539c701ea63a90a395f182a0158458fa1a8096eba786b213cac3'),
 ('0004ed88-ffff41ea-reader',
  4294918634,
  'agate-kingfisher/ram',
  322952,
  (329698,),
  'reader',
  'rpm_inhibit_paths',
  1,
  'unset',
  'unset',
  '795ae8c7594daa65bbee880d68e76137b1d3e4149706de269a0c18021947285a',
  '85c99cc43c84c1e27980d05284933d156113d92aa4f87dfe6f509d86d192bf0e',
  'a13d91ee9b4db8c71ab800ee9a2b6907a7b25db490a8ed735552f652783dfe64',
  '35528fe6bb9ba9ec89bf99bfcfa4bf58995cff8b7332312022f11e9ecdbe16cc'),
 ('0004ed88-000085d9-reader',
  34265,
  'gifted-jackrabbit/tbl',
  322952,
  (324642,),
  'reader',
  'rpm_remaining_inhibit_paths',
  1,
  'unset',
  'unset',
  'adbb8843af22f6905e6621e97f9ba34d8f8f1148cb7d7140bd95ece8420426ce',
  'a65aec0a8164042bab3d922704067bcd6545fdb9fd57a5dd44c69264cb9a72da',
  '910b4753d841cbbe3f510b13702099e1d1cdb125f5cbbac197a26fb9be92afdf',
  'e6914679bfcf00a61ac42cb7dff13062e3d2246bff16a01cb0946c8b7bdeef92'),
 ('0004ed88-ffff247c-reader',
  4294911100,
  'ochre-jacamar/ram',
  322952,
  (326062, 326066, 326068),
  'reader',
  'rpm_remaining_inhibit_paths',
  1,
  'unset',
  'unset',
  '1207bd7b2aa266376884f3a784f913d6785590a23da2847dba2d7be3775977c7',
  '53456aa79d5b22cc9a8697cf16a34a98d2b90b5d0d759218a8ac3629665cdedf',
  '18ce0d8b74ffc0c84610fd911aa1ec5789c6cb917f1715043822a45127220fdd',
  'e7d1e0f4a68a2fd03265faf15224abbb43bbc6296bec5677a1c9944f3307ba9b'),
 ('0004ed88-ffff247f-reader',
  4294911103,
  'blue-oyster/ram',
  322952,
  (324400, 324518, 324668),
  'reader',
  'rpm_remaining_inhibit_paths',
  1,
  'unset',
  'unset',
  '14538f273e63967afb86e7fc260c98112ae69c558d44164490db7a69ad70207c',
  'c6f822e7d823e8bcb0035f08b01dfe212f0eaffa291e30ff7c875ff303dfbfbf',
  '20d6c78be48dbe650762c9ddae49a19bb804249e3ad07e00db408cc22de064e9',
  'a9c3321aacdcf9757a26f8dd3637546c39e2a7131a5f0f9269039360cf5253f7'),
 ('0004ed88-ffff249c-reader',
  4294911132,
  'jovial-buzzard/ram',
  322952,
  (330342, 330476, 330480, 330488),
  'reader',
  'rpm_remaining_inhibit_paths',
  1,
  8,
  'unset',
  'b73c446bfdd0ba749bc64527b07b576952f5e55bbfa37f47ac5041076f60e213',
  '6dfef45fb5205b380799ac2ee9a6863a40c1bbb9c09d6454f8f1d6a93bd44943',
  '3b0e03e5db49cd8130a08781731af185d2254417510a60337e25e356113b80a0',
  '8e13c12f44d0ea5d74c2cef5e6c36d44f8e248ba319735a47d91af9736124aaf'),
 ('0004ed88-ffff41f2-reader',
  4294918642,
  'heavenly-whippet/ram',
  322952,
  (324800, 324908, 324948, 325120, 325190),
  'reader',
  'rpm_remaining_inhibit_paths',
  1,
  'unset',
  'unset',
  '864f52c02760339d3172565de50cadf5a38c6cf6ac0eaa51b9721ecca3ddaba4',
  '11ad6c75b5b5099d5859b3c35730e26c5e3e3645dc9c681472958a8252b6411e',
  '70beb4a363f794a6e3183cf3fa32755ab3eff3fb51a6774fdd8443fa0a78caa9',
  '10f7a6257838da41794d00772d7d0fc55cc1bbfbab7c1e870a7a2cbe32e6a732'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-rpm-inhibit-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the bounded RPM contributor claims change their exact native admission boundary')
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
            raise ValueError('a bounded RPM contributor claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the bounded RPM contributor claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='rpm-inhibit-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the bounded RPM contributor proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two bounded RPM contributor claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two bounded RPM contributor claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the bounded RPM contributor claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the bounded RPM contributor owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the bounded RPM contributor grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='rpm-inhibit-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the bounded RPM contributor publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('rev_limit_fuel_cut/tbl', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('stirring-mayfly/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('fuel_inhibit/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('xanthic-yak/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('resourceful-scorpion/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('obedient-stoat/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('accomplished-chicken/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('resolute-bullfinch/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('agate-kingfisher/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('gifted-jackrabbit/tbl', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('ochre-jacamar/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('blue-oyster/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('jovial-buzzard/ram', 'reader', 'fuel_output_inhibit_coordinator/fn'), ('heavenly-whippet/ram', 'reader', 'fuel_output_inhibit_coordinator/fn')))
