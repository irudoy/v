"""Exact grouped native MAF appends through existing normal link operations."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.maf-access-claims.toml'
PREFIX = 'maf-access-v1:jk08a:'
IDENTITIES = (('source-copy-read',
  4294905942,
  'opalescent-pronghorn/ram',
  240002,
  (240014,),
  'reader',
  'maf_copy_filter_paths',
  2,
  16,
  False,
  '21db09a9086ae3b5adc83c2d4f791dc059e67e85b8217f06598cc4b72e3cecb5',
  'fe80961d1d8c1e77f46962b1d0a60a2209282b736b9ec54dd309481b83657a6e',
  'fa3cf1e7a286806f0bf6e9b3e5789df3991a7a187446578be50183f33a78d266',
  '1bc2c0e68a44ebbe139b50d5c569601f5ae72ae9fda8f0b2d8cdff0df9876aa0'),
 ('working-copy-write',
  4294905946,
  'dancing-hippo/ram',
  240002,
  (240040,),
  'writer',
  'maf_copy_filter_paths',
  2,
  16,
  False,
  'ac1ad6b7a6672ba41af0dfe843bde29dc0baa8aa898a197e471efc1a7f5f25a5',
  '7138f95f417bdec8f3ba6c1bc19e069805fa83d45261094e93d24d640bdee169',
  'efb65f0a965d7e02679bee36a1446fb4ba4c4da89a4a50e75896fe3d1adc3b9e',
  '669bab604aa3e58bc8887cae3d23ea1259d7eb3708cbf51a1a81e8b820a3fd7f'),
 ('working-filter-read',
  4294905946,
  'dancing-hippo/ram',
  240042,
  (240062,),
  'reader',
  'maf_copy_filter_paths',
  2,
  16,
  False,
  '5ab267868dd51ea5ae2d1b3a7780a71bc0e798783fc2879d933e65d9f0777be0',
  'f22a7990423a12a4a14ce32da7a24b3160e34cfd81db835085708994bace5c12',
  'efb65f0a965d7e02679bee36a1446fb4ba4c4da89a4a50e75896fe3d1adc3b9e',
  '669bab604aa3e58bc8887cae3d23ea1259d7eb3708cbf51a1a81e8b820a3fd7f'),
 ('filtered-write',
  4294909426,
  'spiked-dalmatian/ram',
  240042,
  (240136, 240138),
  'writer',
  'maf_copy_filter_paths',
  2,
  16,
  False,
  '7cbccd9dda9359fa412fd5b4969c60da78de8eb9334c9590a5d8cc25a066563d',
  'cf804816b1a3cc8c65a20c9ab398b5c499ca57554fb5d2c70d05a7421da5a24c',
  '83d0f0851aca3f96425348066ee31e837689824fb55dd5fa79a8ae6046e24a84',
  'e8fe653cb4bc35377105bc547e34ce0720ca7cd1fb8a3b9ed291b130a0ca30f3'),
 ('compensation-maf_b2-reader',
  4294905886,
  'maf_b2/ram',
  241290,
  (241324,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '898d03601a1d28c49910e94b25a1e9be119034362757917de9f12f406e172e6d',
  '8538031e4dfecdf5751b0a857b8a929ed6e3e33168a0ab7405c53a50d1e489de',
  '8fbb8693f44e9306b9efaa16811422e5a6028641f09333fb11f6612375b53691',
  'a7986da7d0b8cc685969c3db6d0a0128ad5cc33208398f7856b5d9068504b849'),
 ('scaling-maf_b2-writer',
  4294905886,
  'maf_b2/ram',
  246792,
  (246864,),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '3dbf56c5fc82c2e6afd84baa876cdb0a755da041fad7d4b73c4e0e1782b15972',
  '63545b3cc8149452fee2f553f3ce7b220270995a6a10da17929b563f315dc686',
  '8fbb8693f44e9306b9efaa16811422e5a6028641f09333fb11f6612375b53691',
  'a7986da7d0b8cc685969c3db6d0a0128ad5cc33208398f7856b5d9068504b849'),
 ('scaling-hairy-dalmatian-reader',
  4294909284,
  'hairy-dalmatian/ram',
  246792,
  (246816, 246828),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '0b594aebf06f660c1d93bb2e038b2ec041dc5f4fc20c454e5777bdc349a702e9',
  '961186e4b3bd4cd2cd7f67a31e9cc8bb0ebe81ab112a9e36b26949a4805788e7',
  '682ab901b05dd5058a5592a2cfad472327ab37784bcb8e9db146a69a001200a4',
  '00a85816e8b91fa558aa963537563764b72589806c8c11e716cd95843848dd6e'),
 ('contribution-spiked-dalmatian-reader',
  4294909426,
  'spiked-dalmatian/ram',
  241474,
  (241512,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  'b3dfed53b2069841254a1c3738a1cf1c00134d0c0f11ee3f56b1fcd0c651d520',
  '67fa4ad65f54bc9747d01094d9d2abaf7d4c7961579785e4acbc7ed756f89763',
  '83d0f0851aca3f96425348066ee31e837689824fb55dd5fa79a8ae6046e24a84',
  'e8fe653cb4bc35377105bc547e34ce0720ca7cd1fb8a3b9ed291b130a0ca30f3'),
 ('contribution-imposing-auk-writer',
  4294909436,
  'imposing-auk/ram',
  241474,
  (242034, 242064, 242178),
  'writer',
  'maf_extended_paths',
  4,
  32,
  True,
  'cace53a58cd8759a617d7fcf2c65fe92d5b76af57abe98be6f6cd971333a7859',
  '6b78e748fd9ad4f38c49d65cafade6b2b50b2e07dce488060c7a93305d5325e7',
  '65e12daad47173eb93f1aebf58efaf444db69c0a88fa4bc2a9168676f510eab0',
  '58d136bd12ea0c3fc5317e5347d17ee8ef39ecdf80cdb57dd408ba0407fa37b4'),
 ('contribution-maf_base_b2-writer',
  4294909442,
  'maf_base_b2/ram',
  241474,
  (241680, 241710, 242196),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '777736ee479b0f971724f6891bbf9fa3c0ef053d20bcba38c1afb73dced7bb56',
  'eb2157343299afda91336918d2d77b49b8b21cbc7bda16f5421098c1b6683dbb',
  '654db642d3ab1425846a5ba21431085ef179e346ae6f4b44650c5437921ed5eb',
  '87413480c09f75963525353a62dd3e9ff2aee56065935afb83d5c86b3e3dda72'),
 ('contribution-maf_base_reference_b2-reader',
  4294909450,
  'maf_base_reference_b2/ram',
  241474,
  (241598,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '4378c408e8054bf17c413a665806ca4b9fde061f051d39e791895981ebed7286',
  'e04ddbe3030d55c4201126cfca410803a035567f7122c8d7ac922d24e5851e82',
  '4d69ac2f6167616500055cb7ef129a60e0e2009656ee5993a0c24d91490f214a',
  '18caad3f6d0b4813fa654865fe41b86a0752748acff1f34e1963d4d4bf727b70'),
 ('contribution-maf_fallback_reference_b2-reader',
  4294909460,
  'maf_fallback_reference_b2/ram',
  241474,
  (242132,),
  'reader',
  'maf_extended_paths',
  4,
  32,
  False,
  '157bb8276fba723b60557fafa1e1e253aeaf8f31e3c64972ddefb171e3825e93',
  '36207c0d6b740cafd7eaf3656cf05837e397d33f9fc429a1d3e32a22e49e26d8',
  'e622599fcbb4053e128f93691dc50ec3340055b8f42a2b74bbf6fafbc3465020',
  '085fe5c14e82af17e1c423d69efd333d94199285fa001c36ec01c32ea579010d'),
 ('contribution-maf_delta_reference_b2-reader',
  4294909466,
  'maf_delta_reference_b2/ram',
  241474,
  (241792,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '2c736ddc09e7d7e520bfe2d5dc09fcec5b6a5f59eb35f376954122d1c89e0b2e',
  'd5f0e9665f161a5c00290a990fe8f56e6c872901c564b49255a00882ae6255d8',
  'fb86816d43fdcdaae400665ef25363ed2d0115f8778dbe8d1375785d022c587d',
  '85e220b501723ba6217d6c178a9b82ce8f3cfdf05e4692689a97b49bf3f9380a'),
 ('contribution-maf_correction_state_b2-reader',
  4294909470,
  'maf_correction_state_b2/ram',
  241474,
  (241848,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  True,
  '3d35631835ffaae3bbbf26014ab92237dd2089bff698ddd6ffcd22309a40a8c8',
  'ac7b1db63ebc21e932dfa9dea708c893007d71fdb6d442eddfeba63afe8bff23',
  '4398aa35cc120d2319bbd7ba9ac67197ae438cb2c1fc7fc9fc430a5291f94ba5',
  '8ef7c352d429d09082ca1ca56cdd590939f682f40bd9e506174ce21141d9bd3c'),
 ('contribution-maf_correction_state_b2-writer',
  4294909470,
  'maf_correction_state_b2/ram',
  241474,
  (241978,),
  'writer',
  'maf_extended_paths',
  2,
  16,
  True,
  '1fd6f9682d7dce044568ab1317e59a5f31f191551dca4ca083d94ecf89639473',
  '66e4c59e6dc7f387e6cd9a92025e5cd407a4e8c9ce3281560ac1cfd2f8d3d0aa',
  '4398aa35cc120d2319bbd7ba9ac67197ae438cb2c1fc7fc9fc430a5291f94ba5',
  '8ef7c352d429d09082ca1ca56cdd590939f682f40bd9e506174ce21141d9bd3c'),
 ('contribution-maf_residual_magnitude_b2-reader',
  4294909490,
  'maf_residual_magnitude_b2/ram',
  241474,
  (241624,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  'eac83dc713bd03fd012e8bedf0d22316ad114cc7fdbc4fc3fa5f9eb1b1a7fb89',
  '80e214f69296ece8eae3e565766d94a744a00cbfa4858bd525d1193f842d87c1',
  '899d35cc15ae9f4546f3a40b5d5a5bf6344f1a7587bd3904a423a04b1f2c60f4',
  '7f3658cdaeb8b657b985dd663b178528666447d2072b84dc4515fa5db987d112'),
 ('contribution-maf_residual_magnitude_b2-writer',
  4294909490,
  'maf_residual_magnitude_b2/ram',
  241474,
  (242114,),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '4e5b7be2550ed584894f5f98f76da7fb2e0fd6edfb359a3bab8f8927ff593970',
  '24b5e2ef5b2484b2390718c371467de4b48ad89fd7e3cc6654c3ae9840d1d025',
  '899d35cc15ae9f4546f3a40b5d5a5bf6344f1a7587bd3904a423a04b1f2c60f4',
  '7f3658cdaeb8b657b985dd663b178528666447d2072b84dc4515fa5db987d112'),
 ('compensation-careful-penguin-writer',
  4294909514,
  'careful-penguin/ram',
  241290,
  (241344, 241456),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '6f6b6a0cf72aeebc83c580294c5f22e36bc92e6f820b843f7388406644626b9f',
  '7d55cc778646fdab4c4b4ca437990a93dc63788ce0bf2a352e049fee133201ea',
  '5e8844cd23152731866a53beac600c666efc8634a7338a3f783271658f69f680',
  'fd33964bc105b030b6a65647e4c2e4c49a30bf233b01ab972b7a326729cc8077'),
 ('compensation-unselfish-okapi-reader',
  4294916508,
  'unselfish-okapi/ram',
  241290,
  (241412,),
  'reader',
  'maf_extended_paths',
  4,
  32,
  False,
  'ea8e96f7c3b7d707b217531213c19333f38938775f0fadfe9ac7f8bdee34ae10',
  'bd9528fd860f509c6be308579562ba305c9a1daaa45a4d9e78970fd31a1acd92',
  '8ba4c3dd82c2332d2b4c7350a07998ca705aaeed9d9e51a8f5970d474130dc20',
  'f69a8c53ce9241a32b77bed389f2fa751c271c34850c7fc61eaed2cfb3a1d278'),
 ('contribution-maf_fallback_latch_b2-reader',
  4294919115,
  'maf_fallback_latch_b2/ram',
  241474,
  (241578,),
  'reader',
  'maf_extended_paths',
  1,
  8,
  False,
  '8445ff7bc56148877a932fc97a6dbae908b9042ae11cbbc45ec470049b388821',
  '9defc3796efbd1b2ffae5f572e26de5b89fb6b2ef95617894682abd0c196fb4a',
  '74670f73fa5b4f22f5f17a964847d5949d6967866fe9a4f921292b8d3822e03c',
  'bc1b33afdba6b0f43f255e15d4f4013c2a50d56db1564e279c1206a909910f55'),
 ('contribution-maf_fallback_latch_b2-writer',
  4294919115,
  'maf_fallback_latch_b2/ram',
  241474,
  (241538,),
  'writer',
  'maf_extended_paths',
  1,
  8,
  False,
  '41413d431ee2bea5c4f10d4200624a5b7f9d6c5ee8532321c315eba3d3efe5fa',
  'b37a661e144f3ed72f832c8ddaeba4f065e0727ed9cb0a1b8e5cea54750d2bcb',
  '74670f73fa5b4f22f5f17a964847d5949d6967866fe9a4f921292b8d3822e03c',
  'bc1b33afdba6b0f43f255e15d4f4013c2a50d56db1564e279c1206a909910f55'),
 ('scaling-satisfied-oarfish-reader',
  4294920560,
  'satisfied-oarfish/ram',
  246792,
  (422298, 422368),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '1c7eda6de3bbf13303062b8cf7813df1cd3023b1c1732ca74b1d89859b1952d4',
  '4209b73969ea642ba49798b1019279852e820f8509ada5bcfcea9344d3cf1eef',
  '193c493a0d78db3719978c8aad65211421a8127d8ffaadd249182d88feebfcb7',
  '5f4096b636f1887ee5ab39bfe6f5ee92c699e81a05e094e050de3a96e5490d48'),
 ('bank-publication-imposing-auk-reader',
  4294909436,
  'imposing-auk/ram',
  242212,
  (242228,),
  'reader',
  'maf_extended_paths',
  4,
  32,
  True,
  '608e1cdd5a9de994c2fff9c61edba7c514600d36b2958a10bf1353fbf04b3c32',
  'fb3aba755984c5562f82adebd5376b9b189e15b2c1749ce77dbb946ea854117a',
  '65e12daad47173eb93f1aebf58efaf444db69c0a88fa4bc2a9168676f510eab0',
  '58d136bd12ea0c3fc5317e5347d17ee8ef39ecdf80cdb57dd408ba0407fa37b4'),
 ('diagnostic-copy-hairy-dalmatian-reader',
  4294909284,
  'hairy-dalmatian/ram',
  246876,
  (246886,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '63f13a76f1b78957c1ca2b08a196f7beb01018fb76d9afc0ccecd228ad2aa774',
  '2d5850279c89e27a8da6fc92a66ab4f4cad1b3023282e13e8f9975a16182101c',
  '682ab901b05dd5058a5592a2cfad472327ab37784bcb8e9db146a69a001200a4',
  '00a85816e8b91fa558aa963537563764b72589806c8c11e716cd95843848dd6e'),
 ('diagnostic-copy-camouflaged-cockle-writer',
  4294908480,
  'camouflaged-cockle/ram',
  246876,
  (246894,),
  'writer',
  'maf_extended_paths',
  2,
  'unset',
  'unset',
  '22ca2650452300cedf2c7f1e569da2ccbf3d4bbe56b628a6c579dc12ea297ed2',
  'a8b209b4c0d933eb822f22696b153273fa549d04a253837bd82611483a516a37',
  '3f2b5e1618404ce2ba9e14fd20bc35cdcb84b5ff92a8e0d71cd1cb5e00f73b74',
  '1766b717dcf4457f7c7301373bcfa16640bf85a0f8887e1b03012e0fe04545e9'),
 ('caller-0003a904-ffff101c-reader',
  4294905884,
  'maf_b1/ram',
  239876,
  (241324,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  'fbf07c23421d0ff0c890398e2e8069a9f4c265585afea6197d07197a52c081ea',
  '52d806502c68beb0c53528edb14e27d80a8e28a2dad703d01de0d1db586340fa',
  '7fd7d809b3226131c249c759938aedb06655c432c9730d7ae374fb4fe497b1cf',
  '3021aa1da3e4a969e6d1d03ceb3eed157a41edd70e7ff44898bc54424dee518f'),
 ('caller-0003c3ac-ffff101c-writer',
  4294905884,
  'maf_b1/ram',
  246700,
  (246864,),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '7083a7107757459b32fca8b093c684839cf2c1fd568aea31630c7f84b041a13c',
  '7ba3d01d10c4d41349c03e862f0e12880d0a6bdf065f6e1ba4149e02443eec90',
  '7fd7d809b3226131c249c759938aedb06655c432c9730d7ae374fb4fe497b1cf',
  '3021aa1da3e4a969e6d1d03ceb3eed157a41edd70e7ff44898bc54424dee518f'),
 ('caller-0003a904-ffff101e-reader',
  4294905886,
  'maf_b2/ram',
  239876,
  (241324,),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '58e8a5e9d93f20fa1d7c2aa00bd3a9e307112a4ef77d0744fd96de77721d56e0',
  'eef1d6519a77e88f3dcc9152467ddb270eef4f7bec17859c1320ab127eaea23b',
  '8fbb8693f44e9306b9efaa16811422e5a6028641f09333fb11f6612375b53691',
  'a7986da7d0b8cc685969c3db6d0a0128ad5cc33208398f7856b5d9068504b849'),
 ('caller-0003c3ac-ffff101e-writer',
  4294905886,
  'maf_b2/ram',
  246700,
  (246864,),
  'writer',
  'maf_extended_paths',
  2,
  16,
  False,
  '8ebd0c6858b263bd8caf0d163fb359139e9aa3086814c3aa96491b0d60da0f0e',
  'ab7bd0fee14209feccc7108409efb4f9aae62e43ea8e6ebeacd77c28540339b7',
  '8fbb8693f44e9306b9efaa16811422e5a6028641f09333fb11f6612375b53691',
  'a7986da7d0b8cc685969c3db6d0a0128ad5cc33208398f7856b5d9068504b849'),
 ('curve-attribution-000141f4-reader',
  82420,
  'ivory-gecko/tbl',
  239876,
  (158368,),
  'reader',
  'maf_transfer_paths',
  2,
  'unset',
  'unset',
  '46995c63593c220320f2ffedeb1d6267526afb705a51d496d43d4424ae58be3b',
  '18c1dca9421876c62a1970caf53d576f6b2e24421e65c42c9efc4d6359e9d988',
  'f4dfa79052b18869096553a139addc77fd45b79033c0e31987e3a9d9e6f49af5',
  '119722d0dbd28852bea15deb9eec0d76806f27347c074a5923bedc310ff83de3'),
 ('curve-attribution-00014274-reader',
  82548,
  'wealthy-woodlouse/tbl',
  239876,
  (158368,),
  'reader',
  'maf_transfer_paths',
  2,
  'unset',
  'unset',
  'dad443c04ad68fac2f161b492fcf6a7774dfcfd1b41e3ef1a8c3c592bde62e8d',
  '02f7dc21b70d9cc137fcd12b1ec0a05a9c62c5bba0ad3bed3f83b6eaf9f6629f',
  'd73ad9dc824fb5c630e6c08baa65f28a0e1ebedf6f56cbb11dca5b7f208a4c74',
  'ea0ed03ea45613017e28504d221d4ee9b7e2245d550f169e55f81f9f3574a59c'),
 ('record0129-00025e20-member-reader',
  4294924947,
  'tourmaline-jackal/ram',
  155168,
  (155186,),
  'reader',
  'maf_record_paths',
  1,
  'unset',
  'unset',
  'f30f4db31b9f87ef1c9f19a70901913958a1e29c6f49bfc8f12f08a2e60a5871',
  'a56c8398762e7113df7a01106c53eec89a4b2a4c5731d7f6ad93336ed218ce1b',
  'e3a513878b47fcd55a257fa79c8104071bade67b7117482e5762563cfbadb14c',
  '9e1b3dc5bad99b827a1af3255192f50899f1965ac3c2ab274c116e345614760d'),
 ('record0129-0003c3ac-member-reader',
  4294924947,
  'tourmaline-jackal/ram',
  246700,
  (155186,),
  'reader',
  'maf_record_paths',
  1,
  'unset',
  'unset',
  '6f481722cf7e67db72a44a02e3c958c86d7bf3bc44a58ccc424df14ca783a926',
  '785553a93dcc96b2f4f279a9125f36f6fbd78e085f8646f4644f2c8f248de1f1',
  'e3a513878b47fcd55a257fa79c8104071bade67b7117482e5762563cfbadb14c',
  '9e1b3dc5bad99b827a1af3255192f50899f1965ac3c2ab274c116e345614760d'),
 ('battery-satisfied-oarfish-reader',
  4294920560,
  'satisfied-oarfish/ram',
  236190,
  (422298, 422368),
  'reader',
  'maf_extended_paths',
  2,
  16,
  False,
  '93cf03a0382ab39a6bfbc1e336c7044eafaf5c8911ed48b5d87b1bf77d0fa907',
  'cd2bf7223cb3ac29731f8933beda585e007571e3f83b09a1fcdaa106efe7b8df',
  '193c493a0d78db3719978c8aad65211421a8127d8ffaadd249182d88feebfcb7',
  '5f4096b636f1887ee5ab39bfe6f5ee92c699e81a05e094e050de3a96e5490d48'),
 ('accumulator-unselfish-okapi-writer',
  4294916508,
  'unselfish-okapi/ram',
  240146,
  (241034, 241178, 241268),
  'writer',
  'maf_accumulator_update_paths',
  4,
  32,
  False,
  '2a134b5e8eafa8d1f8ffba6f3df484436a9bc84f0044c4aa144454772e403975',
  '9be37c315c0b62121750c5e807cb47148740421bb32ce2e960f30e4b8ecc8184',
  '8ba4c3dd82c2332d2b4c7350a07998ca705aaeed9d9e51a8f5970d474130dc20',
  'f69a8c53ce9241a32b77bed389f2fa751c271c34850c7fc61eaed2cfb3a1d278'))
CORRECTIONS = {'curve-attribution-000141f4-reader': '543545f4fccf3ffdf90d0dad4d4b7ed53e48e0d7407fe40c493c7b2b46e87464',
 'curve-attribution-00014274-reader': 'd26e0662ba981f7244580fb6de61fa2b95090af2762d2fa44afa756416c09b47'}
RECORD_MEMBERS = {'record0129-00025e20-member-reader': (1, 3, 297), 'record0129-0003c3ac-member-reader': (1, 3, 297)}
FLAGS = ('native_function_publication','native_geometry_publication','scale_admission',
         'units_admission','natural_scheduling_inference','hardware_qualification')

def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def correction(row):
    return row['id'] in CORRECTIONS


def record_member(row):
    return row['id'] in RECORD_MEMBERS


def base_claim(row):
    return json.loads(row['correct_original_claim_json'] if correction(row) else row['original_claim_json'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-maf-access-claims'
            or value['layout']!='7mfk' or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(IDENTITIES)):
        raise ValueError('the MAF claims change their exact native admission boundary')
    keys={'id','address','owner','function','sites','direction','source','component','original_claim_sha256',
          'original_claim_json','proposed_claim_sha256','proposed_claim_json','original_native_sha256',
          'original_native_json','proposed_native_sha256','proposed_native_json','original_ledger_json',
          'proposed_ledger_json','original_symbol_evidence_json','evidence_json','width_bytes','declared_width','declared_signed'}
    originals,proposed={},{}
    for row,pinned in zip(value['reference'],IDENTITIES):
        identity=tuple(row[key] if key!='sites' else tuple(row[key]) for key in
            ('id','address','owner','function','sites','direction','component','width_bytes','declared_width','declared_signed','original_claim_sha256','proposed_claim_sha256',
             'original_native_sha256','proposed_native_sha256'))
        extra=({'disposition','correct_original_claim_sha256','correct_original_claim_json'} if correction(row) else
            {'member_offset','record_size','record_index'} if record_member(row) else set())
        if set(row)!=keys|extra or not test_contract.exact(identity,pinned):
            raise ValueError('a MAF claim changes its exact owner, function, sites, direction or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(new)!=row['proposed_claim_sha256']
                or digest(before)!=row['original_native_sha256'] or digest(after)!=row['proposed_native_sha256']
                or old['owner']!=row['owner'] or old['type']!=row['direction'] or old['sources']!=[row['source']]):
            raise ValueError('the MAF claim changes complete original/proposed content')
        evidence=item(row)
        if record_member(row):
            if (tuple(row[key] for key in ('member_offset','record_size','record_index'))!=RECORD_MEMBERS[row['id']]
                    or row['owner']!='tourmaline-jackal/ram' or row['address']!=0xFFFF5A93
                    or row['component']!='maf_record_paths' or row['direction']!='reader' or row['width_bytes']!=1
                    or row['sites']!=[0x25E32] or row['function'] not in (0x25E20,0x3C3AC)
                    or row['declared_width']!='unset' or row['declared_signed']!='unset'
                    or row['address']+row['member_offset']!=0xFFFF5718+3*row['record_index']+1
                    or any(not test_contract.exact(evidence['value'].get(key),row[key])
                        for key in ('member_offset','record_size','record_index'))):
                raise ValueError('a MAF record reader changes its exact existing byte1 membership or retained semantic type')
        base=base_claim(row)
        if correction(row):
            if (row['disposition']!='replace-reader-attribution'
                    or row['correct_original_claim_sha256']!=CORRECTIONS[row['id']]
                    or digest(base)!=row['correct_original_claim_sha256']
                    or old['to']!='wondrous-camel/fn' or old['type']!='reader' or old['evidence']!=[]
                    or base['to']!='dual_bank_maf_coordinator/fn' or base['type']!='reader'
                    or base['owner']!=row['owner'] or base['sources']!=[row['source']]
                    or base['slot'] is not None or base['offset'] is not None
                    or base['stated']!=['7mfk'] or base['evidence']!=[] or base['roles']!=[]
                    or row['component']!='maf_transfer_paths' or row['function']!=0x3A904):
                raise ValueError('a MAF correction changes its exact unsupported or already-existing correct reader')
        expected=deepcopy(base);expected['evidence']=[*base['evidence'],evidence]
        if (not test_contract.exact(new,expected) or evidence['kind']!='indirect' or evidence['mode']!='maf-access'
                or evidence['key']!=PREFIX+row['id'] or evidence['path']!=DESCRIPTOR
                or evidence['at']!=f'7mfk:{row["sites"][0]:08x}' or evidence['supports']!='identity'):
            raise ValueError('the MAF proof changes more than one exact owning evidence append')
        if row['owner'] in originals and not test_contract.exact(before,originals[row['owner']]):
            raise ValueError('two MAF claims substitute the shared owner preimage')
        originals[row['owner']]=before
        if row['owner'] in proposed and not test_contract.exact(after,proposed[row['owner']]):
            raise ValueError('two MAF claims substitute the grouped owner postimage')
        proposed[row['owner']]=after
        symbols=[entry for entry in before['symbol'] if entry['layout']=='7mfk' and int(entry['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0].get('evidence',[]),json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['proposed_ledger_json']))):
            raise ValueError('the MAF claim changes a retained symbol or ledger position')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json'])
        links=[link for link in expected[row['owner']].get('link',()) if link['type']==old['type'] and link['to']==old['to']]
        if len(links)!=1:raise ValueError('the MAF owner lacks its unique original relation')
        if correction(row):
            expected[row['owner']]['link'].remove(links[0]);base=base_claim(row)
            links=[link for link in expected[row['owner']]['link'] if link['type']==base['type'] and link['to']==base['to']]
            if len(links)!=1:raise ValueError('the MAF owner lacks its unique already-existing correct reader')
        links[0].setdefault('evidence',[]).append(item(row))
    if not test_contract.exact(expected,proposed):
        raise ValueError('the MAF grouped owner transition changes another native fact or evidence position')
    return value


def item(row):
    return json.loads(row['evidence_json'])


def symbol_key(row):
    return SymbolKey('7mfk',row['owner'].rsplit('/',1)[1],row['address'])


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))


def qualified(row,link):
    return test_contract.exact(canonical(link),json.loads(row['proposed_claim_json']))


def correct_original(row,link):
    return correction(row) and test_contract.exact(canonical(link),base_claim(row))


def registered(evidence):
    return (evidence.get('mode') in ('maf-access','maf-copy-filter')
            or evidence.get('path') in (DESCRIPTOR,'defs/JK08A.maf-copy-filter-claims.toml')
            or isinstance(evidence.get('key'),str) and evidence['key'].startswith((PREFIX,'maf-copy-filter-v1:jk08a:')))


def publication(link,evidence):
    """Only one exact pinned owning append is neutral to a physical scope."""
    if not registered(evidence) or sum(test_contract.exact(entry,evidence) for entry in link.evidence)!=1:
        return False
    identity=digest(canonical(link))
    return any(link.owner.key==row[2] and evidence.get('key')==PREFIX+row[0]
               and identity==row[11] for row in IDENTITIES)


def operation(row):
    claim=base_claim(row)
    return dict(cmd='link',meaning=row['owner'],type=row['direction'],to=claim['to'],evidence=[item(row)])


def removal(row):
    if not correction(row):raise ValueError('an unchanged MAF relation has no registered removal')
    old=json.loads(row['original_claim_json'])
    return dict(cmd='unlink',meaning=row['owner'],type=old['type'],to=old['to'])


def operations(ops,root):
    selected=[op for op in ops if any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    rows=descriptor(root)['reference'];expected=[operation(row) for row in rows]
    if len(selected)!=len(expected) or sorted(map(digest,selected))!=sorted(map(digest,expected)):
        raise ValueError('the MAF publication needs every unique exact registered normal link operation')
    for row in rows:
        if correction(row) and sum(test_contract.exact(op,removal(row)) for op in ops)!=1:
            raise ValueError('the MAF correction needs its unique exact existing unlink operation')
    return True


def looks_like_access(link):
    return (any(registered(entry) for entry in link.evidence)
            or (link.owner.key,link.type,link.to.key)==('unselfish-okapi/ram','writer','kind-millipede/fn')
            or (link.owner.key,link.type,link.to.key) in (('opalescent-pronghorn/ram', 'reader', 'brass-ammonite/fn'), ('dancing-hippo/ram', 'writer', 'brass-ammonite/fn'), ('dancing-hippo/ram', 'reader', 'sandy-chameleon/fn'), ('spiked-dalmatian/ram', 'writer', 'sandy-chameleon/fn'), ('maf_b2/ram', 'reader', 'enchanted-cricket/fn'), ('maf_b2/ram', 'writer', 'outstanding-penguin/fn'), ('hairy-dalmatian/ram', 'reader', 'outstanding-penguin/fn'), ('spiked-dalmatian/ram', 'reader', 'mustard-squid/fn'), ('imposing-auk/ram', 'writer', 'mustard-squid/fn'), ('maf_base_b2/ram', 'writer', 'mustard-squid/fn'), ('maf_base_reference_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_fallback_reference_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_delta_reference_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_correction_state_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_correction_state_b2/ram', 'writer', 'mustard-squid/fn'), ('maf_residual_magnitude_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_residual_magnitude_b2/ram', 'writer', 'mustard-squid/fn'), ('careful-penguin/ram', 'writer', 'enchanted-cricket/fn'), ('unselfish-okapi/ram', 'reader', 'enchanted-cricket/fn'), ('maf_fallback_latch_b2/ram', 'reader', 'mustard-squid/fn'), ('maf_fallback_latch_b2/ram', 'writer', 'mustard-squid/fn'), ('satisfied-oarfish/ram', 'reader', 'outstanding-penguin/fn'), ('imposing-auk/ram', 'reader', 'artichoke-mantis/fn'), ('hairy-dalmatian/ram', 'reader', 'active-snail/fn'), ('camouflaged-cockle/ram', 'writer', 'active-snail/fn'), ('maf_b1/ram', 'reader', 'dual_bank_maf_coordinator/fn'), ('maf_b1/ram', 'writer', 'dual_bank_maf_diagnostic_coordinator/fn'), ('maf_b2/ram', 'reader', 'dual_bank_maf_coordinator/fn'), ('maf_b2/ram', 'writer', 'dual_bank_maf_diagnostic_coordinator/fn'), ('ivory-gecko/tbl', 'reader', 'wondrous-camel/fn'), ('wealthy-woodlouse/tbl', 'reader', 'wondrous-camel/fn'), ('tourmaline-jackal/ram', 'reader', 'diagnostic_record_byte1_bit7_predicate/fn'), ('tourmaline-jackal/ram', 'reader', 'dual_bank_maf_diagnostic_coordinator/fn')))
