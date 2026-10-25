"""Exact grouped native learning transfer appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.learning-access-claims.toml'
PREFIX = 'learning-transfer-access-v1:jk08a:'
IDENTITIES = (('00057d1e-0000839c-reader',
  33692,
  'fuel_learning_aux_upper_bound/tbl',
  359710,
  (360774,),
  'reader',
  'learning_transfer_paths',
  1,
  'unset',
  'unset',
  '529f0cd3899ec15f65f89a636df957fc4a75ee613fb898fd583d2cb219b84d01',
  '8ccb7e04fab0b41bbb0f0eeee5ca18f43788905a647d13f68152c6c9884fc77e',
  '40b51e71f674b5f3106ed0679814118c225f54ab5c1b9cb52bf9ce1400fb75a9',
  '7c1eb01586658498f40dd8584d85e6204688eb47b28e269b6cd67956ccdd03ec'),
 ('00057d1e-0000839d-reader',
  33693,
  'fuel_learning_aux_lower_bound/tbl',
  359710,
  (360788,),
  'reader',
  'learning_transfer_paths',
  1,
  'unset',
  'unset',
  '237c62e9e603e6b6315802ebacafccd757b9b82f94c1690ba11302e4f6e4e9df',
  'ef04218b4fe796d57ab25281b7a7eb579a0d357358d85839c292353566d53c46',
  '348238ea9f917c836b217adca0e05ff42585e5d32c53a4af89c4be6c1b86ecd2',
  '7076cd5dfedebd089e47ccebf9469b6358f977d92c2f27979491d4e09ee4149d'),
 ('00057d1e-000088f5-reader',
  35061,
  'fuel_learning_aux_decay/tbl',
  359710,
  (360732,),
  'reader',
  'learning_transfer_paths',
  1,
  'unset',
  'unset',
  '34cb0ba5fb3bc27ecce9a7f9290d1620fa15395298026c039ca4f96729f1e244',
  '01070bc172c6b44ea756cac1fb01cfb39403f593cc574193f3f67ac5277e1ac1',
  'b7b169b546cf8f2a4ee71f58f3335e4b0c5830ca0955291413a71e4089bde4d5',
  '5d620d650a0273c224c634feb530a2eb048446b31aefb026c2a2a58db628b6a2'),
 ('00057d1e-ffff1350-reader',
  4294906704,
  'invaluable-barracuda/ram',
  359710,
  (359802, 359880),
  'reader',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  '50e81d437f52be115ebd58cca382e1d4e99c70051f6f70f9865a53d402d05279',
  '8d4d803ba93ec51b268d37a4b3b4fda260278bf05fc5316e73befed9ec37d7fc',
  'cf8067a61fef17c22acbcaa1dcfa5b8e98cf9741f631cff83a1a5ce721b61c2f',
  'fea090e9633787833053ebc87d7850c6f30854905670c013b53bf97898450657'),
 ('00057d1e-ffff22de-reader',
  4294910686,
  'stft_b2/ram',
  359710,
  (359916,),
  'reader',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  '0f69d3bf780d2b4112e086ac1d02eb4a91c75874416c5eb9f89717052a21a119',
  '1368605230af51beedc6c031035996a147bc931e871771596c838e8141499769',
  '80883e1b842e1a53c1f5cc8c1ff4e23752130da52915c9f43cdbd99af0530698',
  'bc962028d94b106ae3ce44e8707b2412a5ef9ef9895dda3eafa5c428d7352a4b'),
 ('0005796c-ffff2308-writer',
  4294910728,
  'inquisitive-dormouse/ram',
  358764,
  (359180,),
  'writer',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  'c1e04163294a04923961350463d0d7f4f3c022e33ef8b4f86dea738a3e01a617',
  '0fe069f1c6de71861d57dd0e74d000830b690271dad4f1682cf314037aad9a97',
  '865ac5c1c845034d9214633829bea5e17fd989a393e28a22e506144ba9e24814',
  '0b58e83f9ef111dba43069fa4cac2fa81698c1600ba95489d761c8d8a218d563'),
 ('00057d1e-ffff2308-reader',
  4294910728,
  'inquisitive-dormouse/ram',
  359710,
  (359950,),
  'reader',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  'e65afa619ba50fa764a292fc30d3a93d87cb5b40cd67ea10a48a5884833cb41f',
  '55b0fc6bd1c3dffd1965926dd0e7863c58ebf00f2c16f61be2b9c2ca18cceff9',
  '865ac5c1c845034d9214633829bea5e17fd989a393e28a22e506144ba9e24814',
  '0b58e83f9ef111dba43069fa4cac2fa81698c1600ba95489d761c8d8a218d563'),
 ('0005796c-ffff45a2-writer',
  4294919586,
  'af_adjustment_b2/ram',
  358764,
  (359120,),
  'writer',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  '63ea187d545aab4484b22367b2e81c9a8c4eb998fe046884f4bfedd2325ed1f2',
  '5eefe529c4724c9119664748f599346c7d9cc483a3898d3f2d528460fc12a08b',
  '07ff6e891f92ee2d4f33ee22a52567071c898abf6db2116f3b9a9dceaa910079',
  '1ea3f4cfa66d3f69d427f55dea0c56b354acce1c0e1535dc7cbc52f6e34ecb74'),
 ('0005796c-ffff49b0-writer',
  4294920624,
  'fuel_learning_aux_b2/ram',
  358764,
  (360704,),
  'writer',
  'learning_transfer_paths',
  1,
  8,
  False,
  '2ca47d39c33a1c3e36a3716093a3ad160de9f77fd55c8970fb3f54587308f4a0',
  'aa9ec98e957e82419cef5ab634512f224e31c476a36b5f99471f46c62ff2b913',
  '2f6e597b14e08de01e13b81455a8c8577e6a44aae9c8a3c385eaf9295414a1c0',
  'd6a10120baa799f9a2ea998bf9dabb666d5c033efc9b9d78f9849baa15b9ef19'),
 ('000580e8-ffff49b0-reader',
  4294920624,
  'fuel_learning_aux_b2/ram',
  360680,
  (360720,),
  'reader',
  'learning_transfer_paths',
  1,
  8,
  False,
  'f08ae3a9b032e1656726ca716504466e55c0675d66c90478f171d2dd24c08096',
  '4403f7db1ec2304139bba00b3c029567fd7d342edb664c08a772943c07bbde81',
  '2f6e597b14e08de01e13b81455a8c8577e6a44aae9c8a3c385eaf9295414a1c0',
  'd6a10120baa799f9a2ea998bf9dabb666d5c033efc9b9d78f9849baa15b9ef19'),
 ('000580e8-ffff49b0-writer',
  4294920624,
  'fuel_learning_aux_b2/ram',
  360680,
  (360704, 360728, 360760, 360802),
  'writer',
  'learning_transfer_paths',
  1,
  8,
  False,
  '608463f1a8f999bc43492bebb6f64ad311edbd4d2039c4f57ad730eafc7e552e',
  '93cf2d860bc3132b8d2276d8bf577d1d244ae70ee77124c96e420320a3d02730',
  '2f6e597b14e08de01e13b81455a8c8577e6a44aae9c8a3c385eaf9295414a1c0',
  'd6a10120baa799f9a2ea998bf9dabb666d5c033efc9b9d78f9849baa15b9ef19'),
 ('0005796c-ffff49f0-writer',
  4294920688,
  'fuel_learning_aux_b1/ram',
  358764,
  (360704,),
  'writer',
  'learning_transfer_paths',
  1,
  8,
  False,
  '9b4f79417c7ac4699e001360dbf83ae46e9cb7d6d6142450a20e0f7f0a0eea96',
  '9b12875edc4746cb0ae843d912be7c5abbb8419882d37e0f5ac726dc01799d3c',
  'c1b09dcc903928e02bb681180a51476f9d943da5ea63effe3a9c459b116223ce',
  'b7a77ab1319be8d886a3f4f747cd1f3e2093561fbcc70df6281d62a11ac9eb8f'),
 ('000580e8-ffff49f0-reader',
  4294920688,
  'fuel_learning_aux_b1/ram',
  360680,
  (360720,),
  'reader',
  'learning_transfer_paths',
  1,
  8,
  False,
  '518feb778cb7b5f2a9e230954d855a61cecbcc3133d97450cd4c002bf664f888',
  '400598c19659a1c3fe52c43a151985b704b25617b59cff355d90d5dcfba21085',
  'c1b09dcc903928e02bb681180a51476f9d943da5ea63effe3a9c459b116223ce',
  'b7a77ab1319be8d886a3f4f747cd1f3e2093561fbcc70df6281d62a11ac9eb8f'),
 ('000580e8-ffff49f0-writer',
  4294920688,
  'fuel_learning_aux_b1/ram',
  360680,
  (360704, 360728, 360760, 360802),
  'writer',
  'learning_transfer_paths',
  1,
  8,
  False,
  '4e846b5f182e4a2cd4e711c3aa7d7dc3fecaf51ae92660a8fe32ea528a33d314',
  'b6e9544d2a3352178ea23d64925ecd3472a68a85d9c2b825979dba2231280f5e',
  'c1b09dcc903928e02bb681180a51476f9d943da5ea63effe3a9c459b116223ce',
  'b7a77ab1319be8d886a3f4f747cd1f3e2093561fbcc70df6281d62a11ac9eb8f'),
 ('0005796c-ffff4b10-writer',
  4294920976,
  'diligent-bat/ram',
  358764,
  (360636,),
  'writer',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  '6074a39f0f5a139c52150a70509d07589d04f26d32541d2e5b205c4a2e923569',
  '260783bef3a86306045df5731fb08b382895d8fd581d3f33a95b55ec434a2107',
  '040f64834f42224df55969133a2554e8918d9f83b0210796e4b11e9e808ef040',
  'd7b23509bb40b6eba49d198f55a4d9b2c6ea8642f4e39798154621008167348b'),
 ('00057d1e-ffff4b10-writer',
  4294920976,
  'diligent-bat/ram',
  359710,
  (360636,),
  'writer',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  '68ac4709e94a8e9e48508d8cb4266e5350d59e819fd52515c56dfc263ecec4a1',
  '49744cf2e7c022fcce5979122c5d50e4d3eef32c4c9169379bb915fbc5f6ab1e',
  '040f64834f42224df55969133a2554e8918d9f83b0210796e4b11e9e808ef040',
  'd7b23509bb40b6eba49d198f55a4d9b2c6ea8642f4e39798154621008167348b'),
 ('0005796c-ffff4b90-writer',
  4294921104,
  'delectable-vole/ram',
  358764,
  (360636,),
  'writer',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  'e8eb0b67e81c693e557ef53e5a498c6d99aef0a1d57f1f7cc28c4d2ba7526bf8',
  'da96393c210c72f170996aac5fe65e965cff07c6b7118415dfca55bcbe7aa9bd',
  '6c9aafca0a21c7b8c8bd85926e1275fdd9667117afa335cfc60d61b8cf0b5763',
  '4afb908fb407bc632fe3c2428341016318a066eadceed428e5756c8c7ea58bc6'),
 ('00057d1e-ffff4b90-writer',
  4294921104,
  'delectable-vole/ram',
  359710,
  (360636,),
  'writer',
  'learning_transfer_paths',
  2,
  'unset',
  'unset',
  'aad338a63b9f0677659d341c028f3a11de3ffbd8e80a8ebe0ad283734e0ddb90',
  'de9a459d71e468926648e79e36e284321f288d5531150d32d11ae2b140ce51d2',
  '6c9aafca0a21c7b8c8bd85926e1275fdd9667117afa335cfc60d61b8cf0b5763',
  '4afb908fb407bc632fe3c2428341016318a066eadceed428e5756c8c7ea58bc6'),
 ('00057b26-ffff2304-writer',
  4294910724,
  'ltft_b2/ram',
  359206,
  (359466,),
  'writer',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  '26be0ad88a519038ef82a778a9576a2344fcf70912cf1f7ca353e444a197e3e5',
  '0a16de6bc2f82472fb8fb8dbf7a3094328deecf322b038e617f2e1ebdab79faf',
  '5d2be56bd7ccea918d49fcff34c3edd098b462b8a38d626224d6c16179dc732e',
  'f3d43a58e13d55b35468a4fb62a232a5027fd364d4dc67fdf9cf8732ce6001d0'),
 ('00057b26-ffff2308-reader',
  4294910728,
  'inquisitive-dormouse/ram',
  359206,
  (359222,),
  'reader',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  '91d275be970f1890160894accfeb3e490e6d6142baa130e2461be0c4c5f5b39e',
  '45aab6ef86a8132da53371443ca7ece79ba58eee429af04851bef40fdbd821b7',
  '865ac5c1c845034d9214633829bea5e17fd989a393e28a22e506144ba9e24814',
  '0b58e83f9ef111dba43069fa4cac2fa81698c1600ba95489d761c8d8a218d563'),
 ('00057b26-ffff564a-reader',
  4294923850,
  'benevolent-anteater/ram',
  359206,
  (359226,),
  'reader',
  'learning_transfer_paths',
  2,
  16,
  'unset',
  '2d7aa933de0700e2badc379ccd2b59fb9bce07a577da477a6da436ade9e86f7c',
  '036dbf8257e5fe54164fd09e50fb2a4fd06525dd2103b37934d8cd1ffc2921bc',
  '0d883f3395ac7fd1747717104b652e7fa4d37e85cfd8f4ed079f7b18dd0e4173',
  '204c7c9994e1b6c8a0e3a0ced5bfa6f720da1dc3655f3c8d39e9d86cee274f58'))
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-learning-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the learning transfer claims change their exact native admission boundary')
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
            raise ValueError('a learning transfer claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the learning transfer claim changes complete original/proposed content')
        evidence=item(row)
        expected=deepcopy(old);expected['evidence']=[*old['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='learning-transfer-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the learning transfer proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two learning transfer claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two learning transfer claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0]['evidence'],json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the learning transfer claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the learning transfer owner lacks its unique original relation')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the learning transfer grouped owner transition changes another native fact or evidence position')
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
    return (evidence.get('mode')=='learning-transfer-access' or evidence.get('path')==DESCRIPTOR
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
        raise ValueError('the learning transfer publication needs every unique exact registered normal link operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key) in (('fuel_learning_aux_upper_bound/tbl', 'reader', 'rousing-rhino/fn'), ('fuel_learning_aux_lower_bound/tbl', 'reader', 'rousing-rhino/fn'), ('fuel_learning_aux_decay/tbl', 'reader', 'rousing-rhino/fn'), ('invaluable-barracuda/ram', 'reader', 'rousing-rhino/fn'), ('stft_b2/ram', 'reader', 'rousing-rhino/fn'), ('inquisitive-dormouse/ram', 'writer', 'successful-tarantula/fn'), ('inquisitive-dormouse/ram', 'reader', 'rousing-rhino/fn'), ('af_adjustment_b2/ram', 'writer', 'successful-tarantula/fn'), ('fuel_learning_aux_b2/ram', 'writer', 'successful-tarantula/fn'), ('fuel_learning_aux_b2/ram', 'reader', 'wisteria-tarantula/fn'), ('fuel_learning_aux_b2/ram', 'writer', 'wisteria-tarantula/fn'), ('fuel_learning_aux_b1/ram', 'writer', 'successful-tarantula/fn'), ('fuel_learning_aux_b1/ram', 'reader', 'wisteria-tarantula/fn'), ('fuel_learning_aux_b1/ram', 'writer', 'wisteria-tarantula/fn'), ('diligent-bat/ram', 'writer', 'successful-tarantula/fn'), ('diligent-bat/ram', 'writer', 'rousing-rhino/fn'), ('delectable-vole/ram', 'writer', 'successful-tarantula/fn'), ('delectable-vole/ram', 'writer', 'rousing-rhino/fn'), ('ltft_b2/ram', 'writer', 'liberal-dormouse/fn'), ('inquisitive-dormouse/ram', 'reader', 'liberal-dormouse/fn'), ('benevolent-anteater/ram', 'reader', 'liberal-dormouse/fn')))
