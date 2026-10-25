"""Exact registered calculation dispositions; representation grants no admission."""

from importlib import import_module
import json

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, native_ledger, plain
from kb.model import SymbolKey

MODE = 'calculation-dependency'
PREFIX = 'calculation-dependency-v1:jk08a:'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROLES = frozenset(('arithmetic-argument', 'arithmetic-output', 'conditional-publication',
                   'comparison-output', 'arithmetic-factor'))
FAMILIES = (('denominator', 'denominator_argument_contract', 'timing_denominator_capture_evidence'), ('signed-curve', 'signed_curve_argument_contract', 'signed_curve_capture_evidence'), ('fine-gopher', 'fine_gopher_argument_contract', 'fine_gopher_capture_evidence'), ('independent-leopard', 'independent_leopard_argument_contract', 'independent_leopard_capture_evidence'), ('uptight-duck', 'uptight_duck_argument_contract', 'uptight_duck_capture_evidence'), ('apc-reset-offset', 'apc_reset_offset_argument_contract', 'apc_reset_offset_capture_evidence'), ('quiet-cat', 'quiet_cat_argument_contract', 'quiet_cat_capture_evidence'), ('sexy-tamarin', 'sexy_tamarin_argument_contract', 'sexy_tamarin_capture_evidence'), ('viridian-armadillo', 'viridian_armadillo_argument_contract', 'viridian_armadillo_capture_evidence'), ('rugged-gerbil', 'rugged_gerbil_argument_contract', 'rugged_gerbil_capture_evidence'), ('spirited-hamster', 'spirited_hamster_argument_contract', 'spirited_hamster_capture_evidence'), ('arrogant-catfish', 'arrogant_catfish_argument_contract', 'arrogant_catfish_capture_evidence'), ('scaled-publication', 'scaled_publication_output_contract', 'scaled_publication_capture_evidence'), ('normalization', 'normalization_argument_contract', 'normalization_capture_evidence'), ('differential-curve', 'differential_curve_argument_contract', 'differential_curve_capture_evidence'), ('reciprocal-curves', 'reciprocal_curves_argument_contract', 'reciprocal_curves_capture_evidence'), ('counter-threshold', 'counter_threshold_factor_contract', 'counter_threshold_capture_evidence'), ('messy-roadrunner', 'messy_roadrunner_argument_contract', 'messy_roadrunner_capture_evidence'), ('radical-capuchin', 'radical_capuchin_output_contract', 'radical_capuchin_capture_evidence'), ('adorable-llama', 'adorable_llama_argument_contract', 'adorable_llama_capture_evidence'))
IDENTITIES = (('denominator', 'parent-a-curve', 'unnatural-petrel/tbl', 84730, '80cbf8f621c94122ed3b5f0dff31b9533041a5f2ace6551b374e9b0be836b84c', '36ff58c98699ee808ad63c667c11a85fd972590f4bb67abdad06a1558b34f0c3'), ('denominator', 'parent-b-curve', 'micro-penguin/tbl', 101846, '7cda92c8a519a4609170e0a85cafadace5a46e9aee8956d59d4cd6165affa0a0', '1fcec83e94754bd1cc5f4b27230e83abefd0d78e24a3a2bdd2cb5c145c25a036'), ('signed-curve', 'signed-curve', 'vagabond-seagull/tbl', 101862, 'a0684813cfd11044175a89d2dd6db0034da324e03237c04015a528e826c08754', '78b0571d8e9fe92a49ede195bad46f9cdfb2d18c23dcc7072cc24c9784e7dd98'), ('fine-gopher', 'rare-groundhog', 'rare-groundhog/tbl', 85826, '0802816efab791dc9628d684e8242ad4dd93bb30f11652870493199eb0336c88', '172723b188b9105e9293e5aeb036825da0f8af3618839ad95f328d7b77584ddb'), ('fine-gopher', 'ochre-tuna', 'ochre-tuna/tbl', 85842, '4a791359b5580126c4c6df9c1cfaced3ce3c51b7f8ecc4f2765876b589b53147', 'd7dfcfd30bcbaa2750e7b45338743b6d394a05d4a0e732141106833fba6aabc4'), ('fine-gopher', 'steady-beetle', 'steady-beetle/tbl', 86018, '3a41ee5da39614237a9eee1035313bc318b154eccdb10702ce3b348eeda904b5', '48c8d7e6f0e1140e4e8eeda6d8b1035c9b63729592cdd2d4bcfef4267421b82f'), ('independent-leopard', 'fuzzy-giraffe', 'fuzzy-giraffe/tbl', 75042, '08c132a3642b1b8b6d8249c6b6b3a5029876e3e64840b924d9762c32bb8e3ab9', '5a80d091a1fe6c5dbcb63e06bfe10f62a7f3ce6f94f1d39c0cf8622ea5b3ac26'), ('uptight-duck', 'blond-panther', 'blond-panther/tbl', 89216, '2d7b312e121db61661500de403724e6f1819cb75161bdd58a0ca8121adced08a', 'a1d8bba4066d78f247e88e99810bb30c1352b75a5c12ce78e9a9e05553852498'), ('apc-reset-offset', 'prophetic-jacamar', 'prophetic-jacamar/tbl', 73870, '46966e19ba37213a16104684d1590b856f525e2af2ca10b7f2fc0e05526a91f4', '7921999b799a1aabbb9c5d1826ef6323c832b60d83b747a653fd81e0bc3fc949'), ('quiet-cat', 'belligerent-potoo', 'belligerent-potoo/tbl', 74730, 'aa532916bff8865d5a53d99b38677467c90b047748d1f2b0fd01c53bc920d464', '7e4ba08c38431dede818b43c7b53d2959bef063ad5e1475dcf02752a88e3a491'), ('quiet-cat', 'red-bullmastiff', 'red-bullmastiff/tbl', 74770, '5fe1a1f3a93cc936590de0f3ff67df7b18f94137dc663ef31c514559f7c22991', '3534db4cd5ece066f3bddcc6b5ff1ed5190ff869ab36f19693ddf7275f67702c'), ('sexy-tamarin', 'sturdy-worm', 'sturdy-worm/tbl', 75050, 'eb871db5a6f0b38f7d7efc3444e0640b3c7ec7d68fd9715e019a0d56ec747619', '3dc894d384fe7fa9135522f8742563bbf19daf435fffbe327ee7de600406421b'), ('sexy-tamarin', 'foamy-cuckoo', 'foamy-cuckoo/tbl', 75058, '043f0659533233b92e315d11485c5d6342a1a6e92b6994ce683946f12df2f6a1', '300b6a0d58147921b7730ea84432a92f636d70f455188b08a55671e595bb30cb'), ('sexy-tamarin', 'strange-salmon', 'strange-salmon/tbl', 74738, '69eb70517728bd53a338ed82a74ae69e2163509a6a33f9693cf1115ca10bbd2f', '9267fec4ecc6235080db8f8179b03528e9f4dcd2f142b8f0851596accbf90ded'), ('sexy-tamarin', 'greedy-chamois', 'greedy-chamois/tbl', 74746, '57fa5de4f5cbb7812e42702279a04251aef47c4049f7d8ca3071a2594fcb5fac', 'dcf701a5d855fdc316db69756e8a66c216ead3fc1668690a4fbbd76ec1c4b961'), ('viridian-armadillo', 'sassy-flamingo', 'sassy-flamingo/tbl', 85570, 'c77afd3aa79a14a38639cdc0e8d97089eb6fcb902231809264c15a6b90f73cd5', 'cc7995982bdee421852f52debfff0b574f66bb493b627262862ef154cb782327'), ('rugged-gerbil', 'rugged-gerbil', 'rugged-gerbil/tbl', 86050, 'f1037864537f49062fcf0720b2b450191bb539a2c3c4f39f93cbd67501386474', '951893274bbef1f6f5c4eaf61a54750d30eaa18c25d59f9aba258fc6d556d54d'), ('spirited-hamster', 'spirited-hamster', 'spirited-hamster/tbl', 73686, 'ac7c4c96bee55f6dc436039550fd716cef70369394fecb07247f10e97f807060', 'bc34e115e809bee38fb8b29509490f8adf3ca381f5b0a3e6bff19cb1e6b8e08e'), ('arrogant-catfish', 'arrogant-catfish', 'arrogant-catfish/tbl', 74826, '53f8c3c78a93ecef8a86131c4ae5d19c83adfae15e2e7292505a157dfe475a92', 'f2fb31504d6029b732a2d1178f5a9cfc7193d1971737284a7296c3b02d164f97'), ('scaled-publication', 'first', 'jasper-taipan/ram', 4294906384, 'f5256752759284c2fd37d7926c4ebf672bea878ca5f15d5dda65bca240ab4ab6', 'c10f1e03863fc211203718fd15e556ec7179253e86ded14d7fec048d1a769eb5'), ('scaled-publication', 'second', 'snobbish-bird/ram', 4294906440, '92bf91b5ce6edcf089184a5c65066fc7cccc5c607bfc3211d5c545df465757c2', '8249d2970b09d4243ae6219f5a8a769f461f07b32662f8cb56972de4b85bb45b'), ('normalization', 'curve-a', 'brown-jackrabbit/tbl', 83354, '8f08f1a407b6105a42c4d5ef024df7a0275b5928ecf9fa0b52da744afe4e384f', '0e2c9f9f35cca2eebf5e8ddc4506109255986c68c18747da114af228327b3f7c'), ('normalization', 'curve-b', 'placid-mastiff/tbl', 83402, '0dd7759d7caf08c33c49ba8ff77e99df2c9e3d3c8bd9e538730df814fb527ae1', 'a056da320626e8dd9f8aa10dc889caa7e15356856752579a901374190c980fb6'), ('normalization', 'coefficient-table', 'tested-dragon/tbl', 84314, '51d58253de29fc01364cb080b35a933c5c4d7445906b0b4a1cc81e6d89515f84', '0f564465596f8788c687414faddfdfe8ddc791816c52489afd467bb6fa8a4320'), ('normalization', 'published-coefficient', 'nice-raven/ram', 4294912872, '9bfc5a922cc540e3e88c9e27912b76f262b84e07766bfd2cae2f4e1fccf273d9', '5c6012d4b64acfe373db425f03527fa0856aed01521ff3d5b36f4a900d85afd7'), ('differential-curve', 'first', 'unique-spider/tbl', 75576, '4fda54cceb753487c11ce575eb109b5923822781ea4392537a43c816385bd1c5', '1ea0b2b7c9376ced38fc1ffcbe8e99006b79488c7c14b52c0d1cd887baabd47b'), ('differential-curve', 'second', 'dexterous-bobcat/tbl', 75592, '16d40e47867f403fba1e7b783da1dbac40f08c380e7f44f29ba8d43c5a5cdc88', '06a1aa016ccf95fe50ce674589e646d6f40db1addacf83a98b21a025ff640f34'), ('reciprocal-curves', 'first', 'peach-skunk/tbl', 145348, '87c3b21c57403c559bb402adca4c55fa875d4b3c0df5d8e54d77f6e74f1771d4', '20bbdb6d0d7175203bee36abfffdd24622739607e606de9f6b704d016d5627b3'), ('reciprocal-curves', 'second', 'strange-sturgeon/tbl', 145412, '9779853b6b81cad9c9e9ded0f938311affce3e5921aa68d501b60222a9f112ad', '8ae07275121c595f890b0842dd8b6c060d014371e4f45ac305e9f70d0d700e1c'), ('counter-threshold', 'counter-threshold', 'natural-hedgehog/tbl', 43770, 'c52565bea75dd644bcf2fd1d78ed5caec3f658a0b00c32a4e9cdab91ab55efbe', 'eb000913a58842385f8308341406f5ff109155fe75b77d873bc52d260ca54937'), ('messy-roadrunner', 'messy-roadrunner', 'messy-roadrunner/tbl', 73530, 'ed17102dac02dbadeccf064daab5aff8b38c651692a8810909d7ae610b0a83e1', '198dcaf6c83d98f07a2d536a6fd7949c2a5c020d3117042fc6fdc318cba867d4'), ('radical-capuchin', 'radical-capuchin', 'radical-capuchin/tbl', 74594, 'a58bcad0795d1e7847fd8fe8b0a5aa7c62ea4b2e303aadf3fd0c9dd9bc38d857', 'b1c21f72041078046a8b460f855ce30897005d0f414d267cdf70bf084f0b36f3'), ('adorable-llama', 'adorable-llama', 'adorable-llama/tbl', 75736, '1b07a2ade5dc7afacbeeb87fbbed4c9e1204d9137ef2d1f6372909716f537e13', '969326b09ad7c8e647aa8a7ea3d649054b0994f51e29b8b259b8dd48c4ebdfc4'))


FAMILIES += (('closed-loop-sample', 'closed_loop_sample_argument_contract',
              'closed_loop_coordinate_capture_evidence'),)
IDENTITIES += (('closed-loop-sample', 'sample-word', 'placid-jackrabbit/ram', 0xFFFF4524,
                'f1396c2c91e34029ae10383d5ad32a5671db7d1ef3c7e2fbcc6def256b8b11dc',
                '99cf8f379dae318eea43badfd3f29f9dee76d6ddf80d38f75c191a48df75265b'),)
FAMILIES += (('closed-loop-feedback','closed_loop_feedback_argument_contract','closed_loop_feedback_capture_evidence'),)
IDENTITIES += (('closed-loop-feedback',
  '0005d6ae-ffff106e-reader',
  'fuzzy-mouse/ram',
  4294905966,
  '928c9951f1e5672688735f3989b21f2d9e03f7fb9185feaa3ca5ac87e47d1aa1',
  'ca5ace58fb88dc646fe213391ee0e5b3c43ab07d41631baec9911c32941b88b5'),
 ('closed-loop-feedback',
  '0005d6ae-ffff1071-reader',
  'raspberry-dragon/ram',
  4294905969,
  'cc89127e93f9180455c1eef41565c5de0e6e81fd5ed018014e7da76e51dfffb2',
  '123f14c7ddfee1141e4d0ac1792ecc9692e436dbed5fb576d6097ec8a426104c'),
 ('closed-loop-feedback',
  '0005d6ae-ffff11bc-reader',
  'rpm/ram',
  4294906300,
  '36fbbc963182a1490e03dfe07e009022ca5bd60284c6d02b75633f7b1f8ba0c8',
  'c9a92fbd586d2073961b49ea17101672dadf6d601287da53542a9d90a2183db3'))

FAMILIES += (('cvtc-gain','cvtc_gain_output_contract','exhaust_cvtc_capture_evidence'),)
IDENTITIES += (('cvtc-gain','gain-byte','curious-perch/ram',0xFFFF143A,
    'cec5b97e2720bd806454629804b8da0bc2b992853dfbf7ee9fb67c8944fc9c0b',
    '66919e81f22e84f81b0ff2ff6f41189720fc5e28548422c510f2355f4f64d99f'),)


def rows(root):
    result = []
    for family, module, consumer in FAMILIES:
        contract = import_module('kb.' + module)
        declared = contract.descriptor(root)
        if declared['image_sha256'] != IMAGE_SHA256:
            raise ValueError('a calculation disposition changes its exact stock image')
        for row in declared['reference']:
            old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
            support = 'scale' if family == 'counter-threshold' else 'identity'
            original_support = (old['props'] == dict(layouts=['7mfk'], reverse_relies='structure',
                reverse_supports='identity') and old['roles'] == ['indexed_by'] and old['evidence'] == []
                if family in ('closed-loop-sample','closed-loop-feedback') else old['props'].get('supports') == support)
            if (digest(old) != row['original_claim_sha256'] or digest(new) != row['proposed_claim_sha256']
                    or old['owner'] != row['owner'] or new['owner'] != row['owner']
                    or old['type'] != 'reader' or new['type'] != 'depends'
                    or len(new['roles']) != 1 or new['roles'][0] not in ROLES
                    or not original_support or new['props']['supports'] != support):
                raise ValueError('a calculation disposition changes its exact original support or replacement class')
            result.append(dict(row, family=family, module=module, consumer=consumer,
                descriptor=contract.DESCRIPTOR, operation_id=family + ':' + row['id'],
                symbol_kind=row['owner'].rsplit('/', 1)[1], role=new['roles'][0]))
    identities = tuple((row['family'], row['id'], row['owner'], row['address'],
                        row['original_claim_sha256'], row['proposed_claim_sha256']) for row in result)
    if (not test_contract.exact(identities, IDENTITIES)
            or len({row['operation_id'] for row in result}) != len(result)
            or len({row['original_claim_sha256'] for row in result}) != len(result)):
        raise ValueError('the calculation registry changes an exact original identity or family membership')
    return result


def symbol_key(row):
    return SymbolKey('7mfk', row['symbol_kind'], row['address'])


def target(row, proposed=True):
    claim = json.loads(row['proposed_claim_json' if proposed else 'original_claim_json'])
    return {'pompous-firefly/fn': SymbolKey('7mfk', 'fn', 0x21BBC),
            'unsigned_divide/fn': SymbolKey('7mfk', 'fn', 0x21CE0),
            'screeching-panther/fn': SymbolKey('7mfk', 'fn', 0x3EF74),
            'funky-toucanet/fn': SymbolKey('7mfk','fn',0x5D6AE),
            'brilliant-ibis/fn': SymbolKey('7mfk','fn',0x26474),
            'sage-chamois/ram': SymbolKey('7mfk', 'ram', 0xFFFF8CB4)}[claim['to']]


def item(row):
    if row['family'] == 'counter-threshold':
        from kb import counter_threshold_factor_contract
        return counter_threshold_factor_contract.item(row)
    return dict(kind='indirect', mode=MODE, key=PREFIX + row['operation_id'], path=row['descriptor'],
        at=f'7mfk:{row["address"]:08x}', to=target(row), supports='identity',
        value=dict(owner=row['owner'], family=row['family'], component=row['component'], role=row['role'],
            original_claim_sha256=row['original_claim_sha256'], proposed_claim_sha256=row['proposed_claim_sha256'],
            scope='exact-conditional-calculation', physical_reader_inference=False, scale_admission=False,
            natural_scheduling_inference=False, hardware_qualification=False))


def original(row, link):
    return test_contract.exact(canonical(link), json.loads(row['original_claim_json']))


def dependency(row, link):
    expected = json.loads(row['proposed_claim_json'])
    expected['evidence'] = [plain(item(row))]
    return test_contract.exact(canonical(link), expected)


def registered(evidence):
    from kb import counter_threshold_factor_contract, timing_argument_contract
    if timing_argument_contract.registered(evidence):
        return False
    return (isinstance(evidence.get('mode'), str) and evidence['mode'] in ROLES | {MODE}
            or isinstance(evidence.get('path'), str) and evidence['path'] in {
            'defs/JK08A.' + family + suffix for family, suffix in DESCRIPTORS}
            or isinstance(evidence.get('key'), str) and evidence['key'].startswith(PREFIX)
            or counter_threshold_factor_contract.registered(evidence))


DESCRIPTORS = (('denominator-arguments', '.toml'), ('signed-curve-argument', '.toml'), ('fine-gopher-arguments', '.toml'), ('independent-leopard-argument', '.toml'), ('uptight-duck-argument', '.toml'), ('apc-reset-offset-argument', '.toml'), ('quiet-cat-argument', '.toml'), ('sexy-tamarin-argument', '.toml'), ('viridian-armadillo-argument', '.toml'), ('rugged-gerbil-argument', '.toml'), ('spirited-hamster-argument', '.toml'), ('arrogant-catfish-argument', '.toml'), ('scaled-publication-outputs', '.toml'), ('normalization-arguments', '.toml'), ('differential-curve-arguments', '.toml'), ('reciprocal-curves-arguments', '.toml'), ('counter-threshold-factor', '.toml'), ('messy-roadrunner-argument', '.toml'), ('radical-capuchin-output', '.toml'), ('adorable-llama-argument', '.toml'))


DESCRIPTORS += (('closed-loop-sample-argument', '.toml'),('closed-loop-feedback-arguments','.toml'))
DESCRIPTORS += (('cvtc-gain-output','.toml'),)


def looks_like_dependency(link):
    from kb import timing_argument_contract
    timing_owners = {row[2] for row in timing_argument_contract.ROWS}
    owners = {row[2] for row in IDENTITIES}
    return (any(registered(value) for value in link.evidence)
            or bool(ROLES.intersection(link.roles)) and link.owner.key not in timing_owners
            or link.owner.key in owners and link.type == 'depends'
               and link.to.key in ('pompous-firefly/fn', 'unsigned_divide/fn', 'sage-chamois/ram',
                                   'screeching-panther/fn','funky-toucanet/fn'))

