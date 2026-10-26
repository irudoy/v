"""Exact native access withdrawals retaining complete prior source and native-owner boundaries."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.scalar-ram-leaf-withdrawals.toml'
PREFIX = 'scalar-ram-leaf-withdrawal-v1:jk08a:'
MODE = 'scalar-ram-leaf-withdrawal'
IDENTITIES = (('00070d82-0000942c-withdraw',
  37932,
  'rev_limit_throttle_cut/tbl',
  462210,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '62eac25b8cd9d14e3ab6b61b533f4f10431c7ee9f88e10b1cecbaade8c5b1d71',
  None,
  'f25abda47a5c9982f1dd7b1ddc98a6fb28cb140c896590f17a7b21bb032be68e',
  '128de118f8a62d2ea08b8428e5cc3763e57e59fb7d58b0d09dc33b59c6495fcf'),
 ('0004af38-0000991a-withdraw',
  39194,
  'ignition_gated_surface_1/tbl',
  307000,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '4bd4050b3cb7951754a1107aee246c50349b7157aa24d1ffa6a16a2bfc9dd3f5',
  None,
  '9a3c08c74758841c82700345c06f580e1e33c5665e971408b8320f3e7c989daf',
  '8b6e138c928b21a0a1e4895a44beb84c9cb3c72a2c2d6d99f6634849d4e551f7'),
 ('0004ab94-0000a49a-withdraw',
  42138,
  'poetic-sidewinder/tbl',
  306068,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'd8996f6347ec30717c78b7fc4fd514b82303df19fd0f946a9e4911f39d6d8c5b',
  None,
  '3c9cfff61608f7e67bee293edefd56d598902ef8825dad61bf546571e7c3859a',
  'dd389cc80b4943081bbf71d68e5fa91c9fb58d0304cfff75453ab66e38f14340'),
 ('000554ae-0000a49a-withdraw',
  42138,
  'poetic-sidewinder/tbl',
  349358,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'bf7087b2b50b0d4f333e1bb4df0b62a5bfac5ee3c06301550cd346a3ade67d98',
  None,
  '3c9cfff61608f7e67bee293edefd56d598902ef8825dad61bf546571e7c3859a',
  'dd389cc80b4943081bbf71d68e5fa91c9fb58d0304cfff75453ab66e38f14340'),
 ('000a5530-0000abba-withdraw',
  43962,
  'tuscan-porcupine/tbl',
  677168,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '30f6ee3eda41d9da03afaae6758b79360fff541e4a896a1519db9b31e1fd4091',
  None,
  '4c7f8c193a83e1e80fcb39021582d7910ba0e922db4704005b38af305db5094f',
  '2768c0e7d3ba82f0e2aa1ff0e91e1cf102e41b5f7d8a9903222203bd8e0183d8'),
 ('000a5530-0000abfa-withdraw',
  44026,
  'soft-pronghorn/tbl',
  677168,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '7362861f57b2ab4da254a70d1b764dedac273b6559bf8a9272afbf764c39e323',
  None,
  '80972676b0b619930a8c94b713e48936f2c7b336ce4439fe21417d38ff80d6a7',
  '801e8e4f422a093c62e8dc3c3df71fe425f4efd15ff320048fa8cf2589b69079'),
 ('0004c136-00011fbe-withdraw',
  73662,
  'chestnut-wapiti/tbl',
  311606,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '83877203f6fd202b71a22ea05eb0d47620da305b8d449a5f98087567449d17f1',
  None,
  '49ff9abd19e7ce75f2323658c5648852bbd3cb36b97518d7ac6da775da245782',
  '398bf0808ae11e0c5fa2b8b74bce63e1acfb0a9402516884989bbe5cc10fb6aa'),
 ('000259be-00012032-withdraw',
  73778,
  'brilliant-harrier/tbl',
  154046,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '0254b3d244284e5ef3f749cd449c1f0ca18bd0bfcba14a7303b80e75e97de097',
  None,
  'f33607ec880a068d5f64fef4eee388373c08ad7adfb1d96491500ca576d7225f',
  'b93770ccac14f7a8d8c1e9f0ca3f61c6008caf4c03c6cd608cb363fc1276f0dd'),
 ('0004e112-0001219e-withdraw',
  74142,
  'idle_ignition_timing/tbl',
  319762,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'd0c7c99fc8ade0790b4ada64a7eb877150b3a275ff01c27c6f29bb50a9455e7f',
  None,
  '2f8b6a480e36b37757cbaa748cc2431efd4d2df2e04ddf0b6f5bd092db48390d',
  '6c19790e081c27f51c7c5beed5b3bbd53e91babba33b7298af6b81b39da7a65a'),
 ('000468b0-000122e2-withdraw',
  74466,
  'kind-mouse/tbl',
  288944,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'ec83ae96dc34abb023d925c3d887f0232d8cc46100cf1152566914eb255aba84',
  None,
  '0f12a63243440a80d65e2096782a138697d6a7b277712b9709b49c072888658a',
  '22d43a3879372261a3933f27d541cba59d4bf3ac2676932d3003c81a9de28447'),
 ('0004ab94-00012572-withdraw',
  75122,
  'cocky-lion/tbl',
  306068,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'd1942e13fd45c97b63dd4d6e7883a60ac7d6429ea80d9d75a3c929bd20f31a1a',
  None,
  'f02fd2339f3599d8eec245fecec5010d5d60a74f769b30d976c6da9e64905892',
  '0cf4399a26e010d3e6c19466af994f86d7a106eb187d8cdd923f37515f049d62'),
 ('000554ae-00012572-withdraw',
  75122,
  'cocky-lion/tbl',
  349358,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'd9ae07ee269973bf65c9f5f10fcbd653b1a8bf398f8ad9889873303a5f5974fc',
  None,
  'f02fd2339f3599d8eec245fecec5010d5d60a74f769b30d976c6da9e64905892',
  '0cf4399a26e010d3e6c19466af994f86d7a106eb187d8cdd923f37515f049d62'),
 ('0004bb6a-000126a8-withdraw',
  75432,
  'witty-panther/tbl',
  310122,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '59c478bfed6b111b1173c56c2aacc0843b9b3e68e42d2ec83bd45767bb8b25ba',
  None,
  '452822b9a76c041b602476d8bca6634bc5194e00aa1a1276ba2ec8c3e98cbf32',
  'f43af57d2cae01bf6533cf48fafe1c67e1153c64bac1c41f665918b3d9f4b1f8'),
 ('000468b0-00012798-withdraw',
  75672,
  'loud-squid/tbl',
  288944,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  '56392e0ef3e6c84d22fdd6e50c16303f805de7cf8b1921e91eb3a2ca8fb5b47e',
  None,
  '8cff081a5e40ed8a33cd2aff79a4f889065fa841a625a7b9d7d6b5988689d172',
  '8e32a4dd805e1167f32f94d05c84b90699fc489bb816a40eee7be8a0868af2e3'),
 ('000468b0-000127a8-withdraw',
  75688,
  'garrulous-civet/tbl',
  288944,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'b374e0e27834de09b0fc2e054d27137cf8dff90c29db174fb8912043ae5cfea7',
  None,
  'e4c6c3d95596fbd89286b19b14e50fbe6d0e97d8bcaf218b8dc10a2f73929368',
  '4eda7481ae4e6ffed0e19bd34bcbbafb9e8182d8db7475cb0c60cbd05c820cf8'),
 ('000468b0-000127e8-withdraw',
  75752,
  'complex-condor/tbl',
  288944,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'f0c2de10f116c5fcf21ec5492138dcd466c695518f1a86897459cdc49d75b500',
  None,
  'a94da0c6838fcb6fb460e828757a791fd2757682f60404ac6f4dcac13d2b8c85',
  '868b6dd230aa4e74194702039bc044baa421c5d39c5909a700eb66a309fd6ec6'),
 ('00039588-00012dea-withdraw',
  77290,
  'cautious-iguana/tbl',
  234888,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'dba64d011af41052e121fe148750283ea81afb95ec992a4cbc148edc1f088249',
  None,
  '566bad6887976959625a74ea4d0b586199b135a40417d858ac9a458e57026348',
  '1b7d340e93ccd484b4a135117d66bda1878d12be1f9098ffbfe39411058760d5'),
 ('00039874-00012dea-withdraw',
  77290,
  'cautious-iguana/tbl',
  235636,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'e402396559dd17c98946394c1ddd51da0bb0c556b0227aeb9a98d80147c49c7f',
  None,
  '566bad6887976959625a74ea4d0b586199b135a40417d858ac9a458e57026348',
  '1b7d340e93ccd484b4a135117d66bda1878d12be1f9098ffbfe39411058760d5'),
 ('0004c136-00014bfa-withdraw',
  84986,
  'hopping-bumblebee/tbl',
  311606,
  (),
  'withdrawal',
  'scalar_ram_leaf_paths',
  None,
  'unset',
  'unset',
  'ab639a4a392028164c07b4c55aec2e5e71de6b937fd5cdbe8262343d6667dd9b',
  None,
  '8ab0f7a789f7335f2fea258b8a2a36d2e975a235d037d53b09d8c9b3968d899d',
  '75045c556562814283e4e021d77cbd5ed65ff497bd3a58b75e59e9efe5712796'),
 ('000a5284-0000abba-withdraw',
  43962,
  'tuscan-porcupine/tbl',
  676484,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '49079a5f27a6eaf6cbd98b4c01e6df5e3c90299c2733958e08ecefd1dad77abd',
  None,
  '4c7f8c193a83e1e80fcb39021582d7910ba0e922db4704005b38af305db5094f',
  '2768c0e7d3ba82f0e2aa1ff0e91e1cf102e41b5f7d8a9903222203bd8e0183d8'),
 ('000a5284-0000abfa-withdraw',
  44026,
  'soft-pronghorn/tbl',
  676484,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  'aae3934fa0bdc4c566945b51bc78c9608206e103218c947e8419f4915c5ca0e1',
  None,
  '80972676b0b619930a8c94b713e48936f2c7b336ce4439fe21417d38ff80d6a7',
  '801e8e4f422a093c62e8dc3c3df71fe425f4efd15ff320048fa8cf2589b69079'),
 ('00052902-00012176-withdraw',
  74102,
  'vegan-bittern/tbl',
  338178,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '1203c702373ffa952f31f2b3ce62af854749e24f92b06761bec1e692803562a5',
  None,
  '5d9b90dea26ec90c908831318b49ed3c196ce8f60fc8a151ddf8c7a093906379',
  '6a2acca1266b69b6ffb2c4b6a66ada2a7b3426a9f2ae1de9eb699a627a374528'),
 ('0005444c-0001233a-withdraw',
  74554,
  'archetypal-herring/tbl',
  345164,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '5aadff23e65061162eb21e81a53fa223a2df9e82c8999244a2f9cb0d58535f1e',
  None,
  'caf10c5ecf1e0de61fa96948e15d38309bbfb76a096906b9e73b466b6fc4f245',
  '7b5d38eff314da228565a53bdbf723a46e78777bcdedee6c5e4beb1553fa4d00'),
 ('0005444c-00012352-withdraw',
  74578,
  'rugged-turkey/tbl',
  345164,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '6f87244dfbf5f668f11d4b1e6e023d2689254ce52f7a4a185d5bdfabe27f49bb',
  None,
  '6be79c380e6f42a12ed063d59c8df9d505939e9a82a8951e69de021fae13437c',
  '0dd2c72f4ae59dd336a7aa2b806b6a1fa6cc634d249dd7c5d8bbc0ffb1a30b4b'),
 ('000a5284-000123e2-withdraw',
  74722,
  'organic-markhor/tbl',
  676484,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '211523f962786d4111a6029f4d54f1689f3359705575f13f235b52a242acf873',
  None,
  '1fddee703a63fa97aa2b2e28dac23e24de9942e2153a17ca9f84946d280ff1f6',
  '0b4a2326a905124f484c3b1ffb012499d1d6f1a48244e0f164642ce9e1865bf5'),
 ('0005279c-00012432-withdraw',
  74802,
  'kind-kittiwake/tbl',
  337820,
  (),
  'withdrawal',
  'scalar_ram_product_paths',
  None,
  'unset',
  'unset',
  '16dd91b882b70fa7ee892396a8cd9b27ac8ce3d282d6715401562f2857d870d8',
  None,
  'b9837c5c6db54c8578f84e9e13e06e4c5df84d1e10e2e391c49d5e9c5c628b57',
  'f9a9b1191ad4b96a52bd653c176a7cd0e134aea6d62cb80504de053f3c1b041d'),
 ('000777fa-0000942c-withdraw',
  37932,
  'rev_limit_throttle_cut/tbl',
  489466,
  (),
  'withdrawal',
  'scalar_ram_gated_paths',
  None,
  'unset',
  'unset',
  '80f608dd0b63d9fce73fef76f2c19f747cc35bdba2eefd9e4442634d85c6e7ad',
  None,
  'f25abda47a5c9982f1dd7b1ddc98a6fb28cb140c896590f17a7b21bb032be68e',
  '128de118f8a62d2ea08b8428e5cc3763e57e59fb7d58b0d09dc33b59c6495fcf'),
 ('000907e8-0000b33a-withdraw',
  45882,
  'exhaust_cvtc_target/tbl',
  591848,
  (),
  'withdrawal',
  'scalar_ram_gated_paths',
  None,
  'unset',
  'unset',
  '90b6ba055509b84645fd596417cc3a7580d85e8efebdd53751be83099f307eec',
  None,
  '4188fdefed1aea89dd154044f1a3f664274a04bee012b8c1265fa0b722b38b80',
  '7093b2c6427975400099a38e1a10cbd8f9f596637707f75475966adeedd8851d'),
 ('00044448-00012c66-withdraw',
  76902,
  'colorful-dormouse/tbl',
  279624,
  (),
  'withdrawal',
  'scalar_ram_gated_paths',
  None,
  'unset',
  'unset',
  '0604afc85adf13b222f87d78e62078ce1423c16eb842f6c798cf45ad8b5a647e',
  None,
  'dfbd640fbb27b575644d80d9d2e8366c99aeb8444e36e822335ec98415ae8fff',
  '76e9f74812fd193ee9f92a4c37006c11fd08aa7eee14a3e06b0ffbd8e9af948a'),
 ('0003d45c-00012dea-withdraw',
  77290,
  'cautious-iguana/tbl',
  250972,
  (),
  'withdrawal',
  'scalar_ram_gated_paths',
  None,
  'unset',
  'unset',
  '486c2c2b8247e54a0371646f598382dabb7321a015eaea5e6582773940afa646',
  None,
  '566bad6887976959625a74ea4d0b586199b135a40417d858ac9a458e57026348',
  '1b7d340e93ccd484b4a135117d66bda1878d12be1f9098ffbfe39411058760d5'),
 ('00074c08-000153b8-withdraw',
  86968,
  'opal-camel/tbl',
  478216,
  (),
  'withdrawal',
  'scalar_ram_gated_paths',
  None,
  'unset',
  'unset',
  '4b3292cc03ac84ffdb54c818b43cee0aa035ff79e446fc3bc3199658a9db6f4a',
  None,
  '82ce563ebe68fd4cd3f5846c03a3fbfb383774f88b3050c90f4eec203427b556',
  '917a1ac6b98cf233cf44fc6d0dd1b19ef4c0fb4171104808255cade5b3de6b52'),
 ('0004f958-ffff11ae-withdraw',
  4294906286,
  'tough-earwig/ram',
  325976,
  (),
  'withdrawal',
  'rpm_ram_withdrawal_paths',
  None,
  'unset',
  'unset',
  '79416ebc8cdc4b8e6cbb2346fbe6ea2a1c92bb11da20831c00f2d713bfaee2f1',
  None,
  '532f401470afa6ba8e39afbb683c84608ec6448fd9a5b183ad9fc8aefac595ba',
  '71b1001bb6dfd07e1545b439c7d69c7cfbeeefd4365daf81a8ea83e057c2153e'),
 ('0005038a-ffff2573-withdraw',
  4294911347,
  'authentic-monkey/ram',
  328586,
  (),
  'withdrawal',
  'rpm_ram_withdrawal_paths',
  None,
  'unset',
  'unset',
  '4feaccf3f93d5227575be371f3f8819566a59af0fa5c33fca4504992acfad289',
  None,
  'c7589b2ce3724335e1c311c7fa4c7757e2fc2915d9586279de26e1c97db5e13d',
  'e74e608bb010bba85c3281b8acc814cbb0f869583c8deb9ab335a604843469f6'),
 ('0004f736-ffff5a93-withdraw',
  4294924947,
  'tourmaline-jackal/ram',
  325430,
  (),
  'withdrawal',
  'rpm_ram_withdrawal_paths',
  None,
  'unset',
  'unset',
  '4f6035f8258eb3d177b5b7cde4c1e0981101765364f2e516d4a3fcddb1715dde',
  None,
  'e3a513878b47fcd55a257fa79c8104071bade67b7117482e5762563cfbadb14c',
  '03afef4ada11273bb2033dfc03316ce73227b4e081db8546c27d7ddcfc5cb14d'),
 ('000265c4-ffff1b18-withdraw',
  4294908696,
  'aquatic-guillemot/ram',
  157124,
  (),
  'withdrawal',
  'register_overflow_paths',
  None,
  'unset',
  'unset',
  'a4964e35d1c13a7650b5dbcf19a08cba46eb862a8fbc9fe91df2fb65c365dbe8',
  None,
  'c2e4cacbe8fcdd695db8b41beb88c51ed42bf2d545b3bbd3ce77fd01ca011331',
  'c9e404828f2da93cbad8deb0f84ac5429c0f3c05e7ec33294b893a73f1839b75'),
 ('000cb1ca-0000942c-withdraw',
  37932,
  'rev_limit_throttle_cut/tbl',
  831946,
  (),
  'withdrawal',
  'scalar_ram_word_paths',
  None,
  'unset',
  'unset',
  '3b093cf5dda17d51844bfd5eda0482f3f60aa8eeddab660f55294a3c42210bb7',
  None,
  'f25abda47a5c9982f1dd7b1ddc98a6fb28cb140c896590f17a7b21bb032be68e',
  '128de118f8a62d2ea08b8428e5cc3763e57e59fb7d58b0d09dc33b59c6495fcf'),
 ('0006e490-0001296c-withdraw',
  76140,
  'scrupulous-yak/tbl',
  451728,
  (),
  'withdrawal',
  'scalar_ram_word_paths',
  None,
  'unset',
  'unset',
  '6979d26a6b9ca01b5e4e3dab5f2ab1878c8b82e53c6a9163d129cb2ed4ae3a6b',
  None,
  '9f9504e9c7c6ca5466e3258369196ba59232d1345125895e1841270c054cbd18',
  '4fbc439696d15ac6c0da8a661ebaf36de43ba6c7dc7690c8ee0cb458c73b410c'),
 ('00076380-00013528-withdraw',
  79144,
  'vivacious-sawfish/tbl',
  484224,
  (),
  'withdrawal',
  'scalar_ram_word_paths',
  None,
  'unset',
  'unset',
  '3c0d93540474efe7370d42aa1e8fc82f40077e48751a9adbcb944ede4def1a06',
  None,
  'd68826ef9458648c5088ddbaa7bf3d9e0af6856d91db5d3f2d8d7a2c773fb8ea',
  '3f7482b66d87b722851a6209cdc686289830da1ce3154f29dc48da221e43df97'),
 ('0004f7e0-ffff11ae-withdraw',
  4294906286,
  'tough-earwig/ram',
  325600,
  (),
  'withdrawal',
  'rpm_state_withdrawal_paths',
  None,
  'unset',
  'unset',
  '7c4981b684e613d09f1fe29f60b90f840989aa89579723d19a80eefc49e84aef',
  None,
  '532f401470afa6ba8e39afbb683c84608ec6448fd9a5b183ad9fc8aefac595ba',
  '71b1001bb6dfd07e1545b439c7d69c7cfbeeefd4365daf81a8ea83e057c2153e'),
 ('0004f9c4-ffff11ae-withdraw',
  4294906286,
  'tough-earwig/ram',
  326084,
  (),
  'withdrawal',
  'rpm_state_withdrawal_paths',
  None,
  'unset',
  'unset',
  '18889d3895c191b910d24b55b7f40067d1f548dc0b1558837e58b8f3c586d917',
  None,
  '532f401470afa6ba8e39afbb683c84608ec6448fd9a5b183ad9fc8aefac595ba',
  '71b1001bb6dfd07e1545b439c7d69c7cfbeeefd4365daf81a8ea83e057c2153e'),
 ('00052034-ffff120e-withdraw',
  4294906382,
  'red-sidewinder/ram',
  335924,
  (),
  'withdrawal',
  'indexed_word_update_paths',
  None,
  'unset',
  'unset',
  '8173eb6cb77ae22dd0fa72ea3bc4cdb758d15cd421cfac9f79cacfa10055387d',
  None,
  'ac4f55611e829e076e219e265b2a84f9169321d518a0ee7fe3b669e08506b143',
  'eedb1a3ced8ddbd913fcade7225e260d9ec9a9a38bfb67d8fc2b30b0940cc8fa'),
 ('0006e442-0001296c-withdraw',
  76140,
  'scrupulous-yak/tbl',
  451650,
  (),
  'withdrawal',
  'division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '06a28bfdc75877765648fadf97583dd485390c0ea215d8bddac0f7caedb15a12',
  None,
  '9f9504e9c7c6ca5466e3258369196ba59232d1345125895e1841270c054cbd18',
  '4fbc439696d15ac6c0da8a661ebaf36de43ba6c7dc7690c8ee0cb458c73b410c'),
 ('0003a254-ffff115e-withdraw',
  4294906206,
  'stoic-crow/ram',
  238164,
  (),
  'withdrawal',
  'division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '31c06ca11be68e06446e63008e1b925f9c6c91e2aad426c9ac5410d6cd249170',
  None,
  '049d13e968caf6fadbc18140298aafff0ed696ed4a69db08dee0bb5a71c2a9ef',
  '77ff65973d42b78482b948a4d9f3f6cd8290bfe53de2778bf683e102bd8c96b8'),
 ('000b7c84-ffff33fc-withdraw',
  4294915068,
  'tacky-barnacle/ram',
  752772,
  (),
  'withdrawal',
  'division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'c61ae22c08f4705d9dac2d3a011403f1d55fbaffdb4530e223f9d3d239053841',
  None,
  'b7cdc1024bcae24345f4d29b1e5d1964aa594c92600847b574238d6bbb601827',
  'c16a77eda9c2786ff25f3b1a8261e1c09ebf8e823104bb625994ba73a9bbbddb'),
 ('0006e3d8-ffff1300-withdraw',
  4294906624,
  'olivine-corgi/ram',
  451544,
  (),
  'withdrawal',
  'byte_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '8f902a61c4561dec84c2f7f0ae40da8d82fa4d7ef581ebfbead5a5d52ac27bc2',
  None,
  '81a04a8ab417e586d8abe8383f9e4d5c77f5ecb44f9cac709e30f039bdda4a95',
  'd9531595157343d7d52e7afcc9c615cccb4fa3ecf2178a070e38a72427ac7b99'),
 ('0006e3d8-ffff1f86-withdraw',
  4294909830,
  'daring-mosquito/ram',
  451544,
  (),
  'withdrawal',
  'byte_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '37bc9896cbf83383f331006e7744b1bee34ca2856dbfafcbacd9177547752ddd',
  None,
  'e930d44361c619b9e85e752ffd973cbc5c24eb4f1c01e11da2ce85d1fbb7dc04',
  '21d40523b2a29f8ebba164f696c3058be9ccc8a2d39a2a80aeb054c7723b9ea9'),
 ('0002c59c-ffff2451-withdraw',
  4294911057,
  'nickel-magpie/ram',
  181660,
  (),
  'withdrawal',
  'byte_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '09b5eff09ef2b5074732b1901c9a9146175e4c4aebb78fda440c06709ce571e4',
  None,
  'f734f4060b1e0f9c7f69743d14fe3a78c2242acaa03c16a61b3acc9ed475f7dd',
  'fdf553cf113f145172c9ca0fd129614975b79e43564b2b9810e6cb0a3d7b20d0'),
 ('0002c59c-ffff4185-withdraw',
  4294918533,
  'small-sheep/ram',
  181660,
  (),
  'withdrawal',
  'byte_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'a883d3c1766a31c36b0d4af9f9341d0b92f6df477e56465a49115809e41707e5',
  None,
  'a028fc2eb94222b5146fca8493eec7a35aa741fdc14ab746f8db8330b340ec0e',
  '639a6fa71b0e84dc781c47faaa7119c6779f0fc15ec625e6d38450b067d05084'),
 ('0002c59c-ffff84c0-withdraw',
  4294935744,
  'urban-roadrunner/ram',
  181660,
  (),
  'withdrawal',
  'byte_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '7bd9b7a26ba2a26d497c97c09db151002bf8bfd8b01bb5d88d1094277dc5cfc7',
  None,
  '28e6bd06e641fd8fd5df582934e0054205a3e98687ea5d9e4dfeb8eeebf93829',
  '3d997e24762941210db83e60f0769387caf810090ce37708b8907789bbc7a673'),
 ('00072f1e-000175c8-withdraw',
  95688,
  'horned-hedgehog/tbl',
  470814,
  (),
  'withdrawal',
  'word_interp_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '4b97eb1e73817d75504aa38835796a7d10bb9268be350a5b62dda81c5f001cc6',
  None,
  '714cac1d56456db699b7dfc928e733709870e9474d5a3389c67bb2343e68da12',
  'ff7d4980401a674d493dd69b592f7584a0dd5f7eab2876e3a5a05f4c38fa707a'),
 ('000b7b98-ffff1024-withdraw',
  4294905892,
  'kickass-mole/ram',
  752536,
  (),
  'withdrawal',
  'word_interp_caller_withdrawal_paths',
  None,
  16,
  False,
  'ae1c5d03bbbaed09e5d8c4437305e27d646d11b5ce31b4186ccb46bc80db691c',
  None,
  '767136dbc33de3c71e9887dadc4d3a8d3c7e8c765b2ac98470b25f5d0359b04f',
  '292caec8c117f86deeabd0ad17bd2e7fe6ca006fa6ed46ef15980569b0e8de79'),
 ('000b7b98-ffff11bc-withdraw',
  4294906300,
  'rpm/ram',
  752536,
  (),
  'withdrawal',
  'word_interp_caller_withdrawal_paths',
  None,
  16,
  False,
  '600906141f73792784d0da8ded0b5c30d632c7a90d94e1df0c6935fd7c872775',
  None,
  'ea849a7c8cdca9854eeb0d3b4b77d7e3a743ed631755053f815a1677c5c4d547',
  'b9a11f099e71dc2913a3f6624df4d1e5f6a52daf05e0f0c319f469322f6ee5c4'),
 ('00072f1e-ffff1d10-withdraw',
  4294909200,
  'rousing-caracara/ram',
  470814,
  (),
  'withdrawal',
  'word_interp_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '61ff5c17a1c2a129ea4a3395359986ede8da0aef857bb6d6fc706cf8c2f0a8a9',
  None,
  'ebf69335dbaebb6d40452f321331c423b90e70333b1a5ca1358b0dc6af26467a',
  '3e5d9ef9ab6759cf2b53b80f5832f59f3a6058cdf369807da38fd37a5fa4a689'),
 ('00072f1e-ffff35fe-withdraw',
  4294915582,
  'screeching-shellfish/ram',
  470814,
  (),
  'withdrawal',
  'word_interp_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '7cc39463a836a76598dd58578359fb7812eeeb0f673f03852f25d3e7639cd15d',
  None,
  '8fdb69492345ba13b433de0b467e238205d45c5f3fe51634d3c2124be4194afe',
  'ba02b31a512113bfe265961e210f0940ca32206bffd60710dc730a7bccc44e70'),
 ('0004e59c-00012432-withdraw',
  74802,
  'kind-kittiwake/tbl',
  320924,
  (),
  'withdrawal',
  'scaled_division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '37a7d0813e696d1ae72ff71cc98a0e9c83c5bb1ebaae0c2d6ef020df01fe2bc7',
  None,
  'b9837c5c6db54c8578f84e9e13e06e4c5df84d1e10e2e391c49d5e9c5c628b57',
  'f9a9b1191ad4b96a52bd653c176a7cd0e134aea6d62cb80504de053f3c1b041d'),
 ('00074b04-00015770-withdraw',
  87920,
  'vigilant-rat/tbl',
  477956,
  (),
  'withdrawal',
  'scaled_division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '8aa69bd24e2f365fc2ba12af43e13ec5ed1436dcb34c5c32179bd485ca529ce0',
  None,
  '187a097b5649112113b22d3a986179eb02cba429e31dc3a16c20ebb8855621b2',
  '9130b5cd88f461321ddfe64c1a49cb1ef30a727ba2de34565dfd4404181e7faf'),
 ('00074478-00019190-withdraw',
  102800,
  'towering-newt/tbl',
  476280,
  (),
  'withdrawal',
  'scaled_division_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '0e56068a2df4d1cc74996097fda4018457460adda77683a8ffa87bd7b0587f0b',
  None,
  '15a00794a1b74f81082958406ab63bafa825cfd5e1dca2c377246947384f2cb0',
  'c43eefa264ecf3eb85b03c02402d2bde87527db7dfcd40b404a16a2029aed3bd'),
 ('000b7768-00015c40-withdraw',
  89152,
  'magic-kingfisher/tbl',
  751464,
  (),
  'withdrawal',
  'curve_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'c929ffe309a99404d540ecfdfbfad0a6be2232a343f56f29adfddec308af95a1',
  None,
  '1c8f25ffe0026d142400fa9da095ceacb840ac730bbb2bcdfded3af5850fcf0f',
  '2d8f7ffa9cd4768a025b523ecc2563041ba561cf9c81a2ec1d193c23db5b85a3'),
 ('000b7768-ffff2733-withdraw',
  4294911795,
  'perky-agama/ram',
  751464,
  (),
  'withdrawal',
  'curve_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '2fa5679cd811139cb212d0665cbe7a53415535a72d65c79d58e21e6f4d5f0542',
  None,
  '1a35ed283d1c9e3fb43d21d189da4a8b254d225a1e779e2335ec48cd6b30d36a',
  'a30ba66194c1a9ea1534bd81d424873778f284446ac43ef75c984fe2c5fb0d8f'),
 ('000b7768-ffff3348-withdraw',
  4294914888,
  'ruddy-anaconda/ram',
  751464,
  (),
  'withdrawal',
  'curve_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'e353009592e533d5f7413aa3a4edaac73a80982db8c14fd47b6db9376eeccc0b',
  None,
  '0dd1d84e8efef214bad6c82baa1c853c2471764b78f486f1633f84df08964dc7',
  '89da17abcc08cbf335c3f73f91600cf841f10a19c9f6d8ef5c89669909a06b71'),
 ('000b78da-00015bf0-withdraw',
  89072,
  'prehistoric-boa/tbl',
  751834,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'e50bf2ae3fbd6e46ee8421e61c6d3019fcab782748a1de7f49b36fb90fdc2821',
  None,
  '0353478ac8b7a8b1682c9ec66de02cb776dcbbe2dbb15e022d5f66dd3aa84419',
  'f64d24270c44b8bae73b242099b93b8fcef01cdac039027700e57bcd49836993'),
 ('000b7a3c-00015c80-withdraw',
  89216,
  'blond-panther/tbl',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '135b4bf6288e3b975c8a616f93fc760776bb5751356b8805576b24ec0c97ee1a',
  None,
  'fcd2dc27bfdcecb1f27572554c21cfd124eefc04cf7f07fb33732d2127c3550a',
  '3abcc27fcf6519d36bcdab3013a5e501054f0da23419b83b34d9ea2cf5e1058e'),
 ('000b78da-ffff110e-withdraw',
  4294906126,
  'vehicle_speed/ram',
  751834,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  8,
  False,
  '036bd425947d6ea6b3d8f732a6427ad3e7bd555898e56beb96b30b026c1c9332',
  None,
  '4b49aa91d9395063f04121fc62ac04cecaf828f711ba4d02f5f00857d9da06ec',
  '16450fe1eb7986f94ade8b33b84d90b6f6b48023be3f1c5ec7392afa9fc53639'),
 ('000b7a3c-ffff110e-withdraw',
  4294906126,
  'vehicle_speed/ram',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  8,
  False,
  '32b20036c5e60a367da500146f25121094a9f11af3952e9063153cab4301788f',
  None,
  '4b49aa91d9395063f04121fc62ac04cecaf828f711ba4d02f5f00857d9da06ec',
  '16450fe1eb7986f94ade8b33b84d90b6f6b48023be3f1c5ec7392afa9fc53639'),
 ('000b7a3c-ffff178e-withdraw',
  4294907790,
  'gainful-crab/ram',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '76aa231e36017454b261a39ee19edf364ad4abb611477e3c0ca260f1e52c46b9',
  None,
  'b1a10f4d8e917a54f5ba52a8a9fe184ad07092194d160f2fc955828e8733ca5c',
  'ede4939065d5c562baeee2fce78b4d0e1305659cd9bb34e0060fbc2e76eb32f4'),
 ('000b78da-ffff2733-withdraw',
  4294911795,
  'perky-agama/ram',
  751834,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '92dfcb0943b8b651253776a006fba60c01487ea7b768b2dab387d69302848c14',
  None,
  '1a35ed283d1c9e3fb43d21d189da4a8b254d225a1e779e2335ec48cd6b30d36a',
  'a30ba66194c1a9ea1534bd81d424873778f284446ac43ef75c984fe2c5fb0d8f'),
 ('000b7a3c-ffff2733-withdraw',
  4294911795,
  'perky-agama/ram',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '7defb8aedceeaaa17c4a43a870460907d61b5e9933bea8b136732115ab3615a3',
  None,
  '1a35ed283d1c9e3fb43d21d189da4a8b254d225a1e779e2335ec48cd6b30d36a',
  'a30ba66194c1a9ea1534bd81d424873778f284446ac43ef75c984fe2c5fb0d8f'),
 ('000b78da-ffff3348-withdraw',
  4294914888,
  'ruddy-anaconda/ram',
  751834,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'ec181ca2f794853e947329334c40017f426533116fd07a94ffe46dc1174b70e9',
  None,
  '0dd1d84e8efef214bad6c82baa1c853c2471764b78f486f1633f84df08964dc7',
  '89da17abcc08cbf335c3f73f91600cf841f10a19c9f6d8ef5c89669909a06b71'),
 ('000b7a3c-ffff3348-withdraw',
  4294914888,
  'ruddy-anaconda/ram',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '9f418c7091d6acf535a07437acd5068090a8b59e50d8426db950136c98b527e3',
  None,
  '0dd1d84e8efef214bad6c82baa1c853c2471764b78f486f1633f84df08964dc7',
  '89da17abcc08cbf335c3f73f91600cf841f10a19c9f6d8ef5c89669909a06b71'),
 ('000b78da-ffff35a0-withdraw',
  4294915488,
  'curvy-mandrill/ram',
  751834,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '9d3662e96629145aec9374547056749303b0b6295506e49ba4693a4722ef566e',
  None,
  'c35507dc911e200bbb21abb42574cf7443c07c240ca45f33c10a290ba0e358d4',
  'a15fb5499f178a39cdfe66f283c3c3bf9d75ba3cc10b503e8645aaba04ea2150'),
 ('000b7a3c-ffff35b6-withdraw',
  4294915510,
  'peach-anteater/ram',
  752188,
  (),
  'withdrawal',
  'derivative_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '453f6650c03c4604fd20fcb4c273cf86f51d642ee1161d9a552dc0c7d39cc01f',
  None,
  'f0b0cc57c41cd0f3c73f2b95a9fdabf2afa08ed5dfcae7be6ad2c0529a668efb',
  '9f5e7f3c3e8898d8699188316120b47785628ccb2fd1c42d4f125bc68972093d'),
 ('000532ae-0001198e-withdraw',
  72078,
  'efficient-mastodon/tbl',
  340654,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '6058df3ab81fa13bb54d91f7e75c7a296e9dcd50b80d45dd2762b6d24b56837a',
  None,
  '1bc69b97a4dab5fce4b269fa6633877db7a85219fe97c87366fdbfafe20cc190',
  '8681cf95a45d141e96caf0e949659ec7ec9299c23262c8bf406000badd62c25b'),
 ('000532ae-000126b0-withdraw',
  75440,
  'remarkable-oriole/tbl',
  340654,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '6c9f4250619347ff8194043c8243c7d30e4d4bb389b002b66a88bf87efd8f235',
  None,
  'b61743e9c04b3a33bb82a0150e822bb9f90f793c7e2dc562b6e01d5732a2307a',
  '90dfa16f58bbfbc4b800e37c9fe34ca29be6e9a082a17147b6db31a21e51eb11'),
 ('000532ae-000126b8-withdraw',
  75448,
  'illegal-raptor/tbl',
  340654,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'c1d274e32563d7c74891c872fa46392064637818cd6e89dee35c5598cd0d09a8',
  None,
  '48267904607135e4a053a4fcea85c53c1b5727a391b21f8b44d7000c6171df46',
  '382c5ef1f1d054c649c622c974f3352399b8ee64f4e295c27029703cd888f062'),
 ('000532ae-00012a82-withdraw',
  76418,
  'sticky-cuckoo/tbl',
  340654,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '868537232a2d40bec435a486835bab723ad56022b92b2e0be29c65169deec358',
  None,
  '3e2f2f393e59f7426d2192f2578da734e3d9cbbde83fb22ffdcda88cf04f1223',
  '9a855dcd39cf36bd30c993f0e45c91568ac898cb7bd601a4eb60539df1c8ea29'),
 ('00074b68-000153b0-withdraw',
  86960,
  'origami-kangaroo/tbl',
  478056,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'd961725e5c49bea33ba3188206854a27395362e43f18d5f11d7ed583bb63eb41',
  None,
  '7de06cf5ec594386fee7feef9be44c0151e6e27a0c486eb681b94a046a735d76',
  '946cc291da233a0193d9092e06a53da077f1813cdc46cd96ea4ec5cffef105e1'),
 ('00074b68-000153b8-withdraw',
  86968,
  'opal-camel/tbl',
  478056,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '6c58ca67411a67c211c802575a710fae9d7e145d195d34f9f08d4e9a9caaf8b5',
  None,
  '82ce563ebe68fd4cd3f5846c03a3fbfb383774f88b3050c90f4eec203427b556',
  '917a1ac6b98cf233cf44fc6d0dd1b19ef4c0fb4171104808255cade5b3de6b52'),
 ('00075306-00015770-withdraw',
  87920,
  'vigilant-rat/tbl',
  480006,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'd5899807d9addb2b878cf5d643b4dfa2a132c11e24a42ebd8bfe47950dea631d',
  None,
  '187a097b5649112113b22d3a986179eb02cba429e31dc3a16c20ebb8855621b2',
  '9130b5cd88f461321ddfe64c1a49cb1ef30a727ba2de34565dfd4404181e7faf'),
 ('000532ae-ffff15f8-withdraw',
  4294907384,
  'adept-bumblebee/ram',
  340654,
  (),
  'withdrawal',
  'guarded_quotient_caller_withdrawal_paths',
  None,
  32,
  'unset',
  '1b3937e671acbb4fcf17f1915a3e236caf33f087a088b1e084202159125123b6',
  None,
  '800089280439616ecaf5a36b5ef26b9f025395ffda24f4623c42093b4dfbb453',
  '664aee688c3b3f9981f9f93b4bbebaae1c689f8ab5e78c7960403c840e44ae09'),
 ('000659ae-00010b8e-withdraw',
  68494,
  'lyrical-dragon/tbl',
  416174,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'ea68a6b80640ced3d347421e1ee38375a22e6c9cf0533775b444cda015a877b7',
  None,
  '034b6ea7b1d3a57cfe9ae857b1b626be8654ee1d3291cc0e1e9e5cc116b25039',
  '68ba1d1a29410bd0b8261336071e6f583ee8dc82ee2140e7321425657052a518'),
 ('0004bdc2-00012196-withdraw',
  74134,
  'cold_idle_ignition_timing/tbl',
  310722,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'c638206ca7fd33d917a82061925c79683301c5962be263783d279abd091196c6',
  None,
  '7ca4c86d16df613d76913a8e7955674cf99e9d066de5bc6b0ea12a17c26eda14',
  '8b461937103b70aaa04603c8653ff31fff6c29761775847d231a7b2d818f975d'),
 ('0004bdc2-0001219e-withdraw',
  74142,
  'idle_ignition_timing/tbl',
  310722,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'aa811f9566043dbf2c67f43e399ca35b654a4e71c2e867c02a1770567444e549',
  None,
  '2f8b6a480e36b37757cbaa748cc2431efd4d2df2e04ddf0b6f5bd092db48390d',
  '6c19790e081c27f51c7c5beed5b3bbd53e91babba33b7298af6b81b39da7a65a'),
 ('00041db6-000127a8-withdraw',
  75688,
  'garrulous-civet/tbl',
  269750,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'da9b2c172b7614e33d3f913c1790f81e57080f8fa8a6a04819431a70df59ff26',
  None,
  'e4c6c3d95596fbd89286b19b14e50fbe6d0e97d8bcaf218b8dc10a2f73929368',
  '4eda7481ae4e6ffed0e19bd34bcbbafb9e8182d8db7475cb0c60cbd05c820cf8'),
 ('00041db6-000127e8-withdraw',
  75752,
  'complex-condor/tbl',
  269750,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '798c9e94fd08d7709381dd7e051c1adbfdddf5b66dbf86bf5fda357d950b9098',
  None,
  'a94da0c6838fcb6fb460e828757a791fd2757682f60404ac6f4dcac13d2b8c85',
  '868b6dd230aa4e74194702039bc044baa421c5d39c5909a700eb66a309fd6ec6'),
 ('0003b498-00013202-withdraw',
  78338,
  'muscular-leech/tbl',
  242840,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '7a47a5cc01d09c1a49e7799cdcc523dbc8025b812b7c275d2e0d2056f0e62aaa',
  None,
  '992709b018fe9daea07fd9dabdca5c5139d4f5cb398c1e35d921f099283f0d0a',
  '44c9d12223f9ac23c077c6f8370dcd68d420db39ccfc62491eb955306a9671c7'),
 ('000659ae-000154a0-withdraw',
  87200,
  'pristine-deer/tbl',
  416174,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '8493572c035dac033b196ebb017eda328de39e92d345597c2bf41d343b257a2b',
  None,
  '453f350f8ee907f9fe45c359c77a5359dcae54c59d00e0f22c6399cb16983d5c',
  '2f0f68de86cb66accccd6f49ea059b5cddd7e1eb0d7ce2f3e3a09fbe02a3b3e1'),
 ('0003b498-000155a0-withdraw',
  87456,
  'monumental-snake/tbl',
  242840,
  (),
  'withdrawal',
  'mixed_curve_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '4246f372f407cd8d806292efe7d3c6e57559411abc87c010b448167fb21a3ad7',
  None,
  '44823d411cc018099a962329c981d396e757b727a8edcd27472fefb2ddc2da07',
  '738900550b21cec89a488ae16d068466c31a0cf5922f5ed736dc69fc6c45f75f'),
 ('0004d99c-00009a1a-withdraw',
  39450,
  'high_octane_timing_state/tbl',
  317852,
  (),
  'withdrawal',
  'timing_remainder_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '89a38d2dcd45777abd73579e85cf7b5dd431bc74e4a2260328a310210098f5f4',
  None,
  'd4c0bb9bf35120fb1220be7e9c7b2da2cdcad11062d40471ef0f527a3baed8e6',
  '2a942b23a41b60f6895ad3fd5f978d1d45561e283589622c8f80b48b6c890e59'),
 ('0004d99c-00009b1a-withdraw',
  39706,
  'high_detonation_timing_state/tbl',
  317852,
  (),
  'withdrawal',
  'timing_remainder_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '93e3a24dbabf0b837d2a841e770691a49219fdae0acb23fbf86292abc5b70294',
  None,
  'b780f1e77ae0a795dc54a2b061d9ba5b4f3b6beddf9358282070196446f5fa83',
  '3ee7bffa0df3bb81b57b71f75eaa7d12e25a7dd50ae4d046166084a599ff435d'),
 ('000521a8-00012302-withdraw',
  74498,
  'tangible-gharial/tbl',
  336296,
  (),
  'withdrawal',
  'timing_remainder_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'f46a6cd59f095a901dc94bc0a98d36dec248275c481b136cdd5453add9d11092',
  None,
  '2e54de5cacc2b109bf44de887ab7686766eea28fda654bd56eaded34d1df89a9',
  '0e04176201f9b7806e9c666e24b1d3e5ba9e073b756327a2ef3aaea5fde8ded0'),
 ('000521a8-0001230a-withdraw',
  74506,
  'crouching-orca/tbl',
  336296,
  (),
  'withdrawal',
  'timing_remainder_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '734ac219e0c8a85fb79e275db3666708bc66a9e4aa9be699f218fb89bf962744',
  None,
  '30effb77d4f96d5b3a4046b1139db1e46f15e3676e2413a7586a889f5964766d',
  '474a9ed1d5924e440b9c4c1c0c3c4641a4d7bdc5d85076f634d97a4d454ca52c'),
 ('0004d99c-ffff121a-withdraw',
  4294906394,
  'knock_timing_state/ram',
  317852,
  (),
  'withdrawal',
  'timing_remainder_caller_withdrawal_paths',
  None,
  16,
  True,
  '5e73c6e179defd8189e4bff04c27bc774d2b2b9a04068df7648d5096e352eac8',
  None,
  '4c726832967db8ba86883432477b8bd4f14150b324281b7e7d34385d80566ad1',
  '43ddbfacd3c2f1b38fef76efa25bb64218f9f7ea9c437eee3ba9573ecd9c8b81'),
 ('000bdc66-0000ab5a-withdraw',
  43866,
  'humongous-skunk/tbl',
  777318,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '732688d3434fc5a9a865a6cebd20539bcfc8910a4081e9b969e2acd61d7bd78d',
  None,
  '00321d61dced137315d40cb6035aca8c20b9255280e9c06aab031187ea622528',
  '297c885b83a9c527801df7e63dd576a226a51b12b225b900a3287320c64d9d5c'),
 ('000bdc66-0000b43a-withdraw',
  46138,
  'intake_cvtc_target/tbl',
  777318,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'f73ed3184f14337902a9cf59ecad78ad4758f406cf517eb3051d29b6c51ad816',
  None,
  'd3dc65f0308687e89ca03943f796897009e872ff464c41295dd0341befa296f2',
  '4cef2b57a75934c5dd5c54783838c0c248c96e09ad6774d66aaa6fa2826b743a'),
 ('000bdc66-0000b53a-withdraw',
  46394,
  'cunning-jackrabbit/tbl',
  777318,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '2e5256f30e8ea2c75bbf968f4a83d03fde44859214cb1f1891cf7a8148674f31',
  None,
  '43ade8341837b62b95edaf8710305134f52f3d9cd0236961272d7e9aada48e9d',
  'd53651b52b3a61d7323778fe1bcb07c8148c50d7945aabd48155bfeb8fc99abb'),
 ('00064cb2-0000b5fa-withdraw',
  46586,
  'sturdy-baboon/tbl',
  412850,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '0eb7a55d3774f6a93694313064815dcfa169939e114231fe1b262f249e4e7e81',
  None,
  '3671469b54f512e2e3e64f7e086f5b46b0b7a9f03a8508e57ae35180b6c0e58a',
  '20393582a28c43c127614fc3e2a53faef084348dedd923755856940ded2c7430'),
 ('00064cb2-00011fe6-withdraw',
  73702,
  'dramatic-warthog/tbl',
  412850,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'b302d7d9f9f92e555d671576982f93b50d101da12e7bd9d8c3756a1939d516ae',
  None,
  '83b0b4da302a18efb1270c84346f0b50a6ac3a4c858d8ca03fc09f57d3060431',
  '7cabba1c20ed7664d10a209d199987286c4af436123d12f0606401a9e38aee75'),
 ('000bdc66-000122f2-withdraw',
  74482,
  'stoic-ladybug/tbl',
  777318,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '156e43c13f7bac66de494bd9181c94497ad05da8619c9987c1ccb816a8577ca7',
  None,
  '0bd86d7af02e350e8eac9116408e02acb5116809d144d41b3b3b587e7d71d37b',
  '27dd2610be22eb6d9bf41e2010b4e611227246bc6aa1deeeac63a7ff3ecb16c6'),
 ('00064cb2-00012b32-withdraw',
  76594,
  'carrot-frog/tbl',
  412850,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '4ebd4423d2ab59540c501b6622cb53a52163bda63ba24c092463de7f4d67fef9',
  None,
  'e4dfadf15a429073e68f40e8b53b4415517e52431b6d184961cafd2b699ef784',
  'da0a38e8c699fc810b2a0c719f11f0e3eb8fa117609a5ac6802513716a025559'),
 ('00064cb2-00012b52-withdraw',
  76626,
  'quick-basilisk/tbl',
  412850,
  (),
  'withdrawal',
  'state_ratio_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'c836c14a4677ec716ae2b0a170eed751e0d6ee2f05b0edf5e78d5b156f56cd9c',
  None,
  '32e81f21247ff424a92ed5353ba843611e3e44f67db4e8044305556e4fc7d756',
  '615ac4e727f8aaa6660fae1f340769a818547ed665570d8972ffdab194b697cc'),
 ('000503e0-000120f6-withdraw',
  73974,
  'attentive-axolotl/tbl',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'fdaf3867d48487219ed37f59f2a79110967257a3933c1f3d3a5cda122d0e6a55',
  None,
  '87269ffc67bec0bbdc8a026533e60e544500b45d40d5a8a899ca23acb8d28938',
  '7ccac59a92ccf7705507bf04b09f94f7f95e1f2d7b90c6a505ababc406d39828'),
 ('000503e0-000126e4-withdraw',
  75492,
  'over_run_fuel_hold/tbl',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '6c0df85a37c801ca6a7d79ebf2c0a3a3ecbbc363e008f3167114fa6b1e9f97c6',
  None,
  'f96aca908a9aefcbe37e8a324817ce2350a5bf18f6ef54f2f2e3ec9f5f6d2177',
  '16970f965d32e73d207d9bc4853c397fdb4c6110925ffffbfb2c7d7ec211c19d'),
 ('000503e0-00012718-withdraw',
  75544,
  'over_run_fuel_cut/tbl',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'dc34c59bb20daae1cf6908bb684df035a5825e89e2c052b27b26f886a28add13',
  None,
  '04be30ca3ed3e9ed2cdc679a6d2b87d83dbf7521089f9a6c99656d45af53c988',
  '60647cd6263930f5d6b0c3e02f3d47f075968d6a529fd3d3f2cee6189fd09147'),
 ('000503e0-00012818-withdraw',
  75800,
  'over_run_fuel_restore/tbl',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '0cfcf76e8ab04eab6aacd76907296a3acee472114a88a3f750d00e421a820ef6',
  None,
  'f158deed2719307b587cc033c7e012306884ca346856e36bbedf75b0c8756bb6',
  'ae64c63809b0e5fbb41679e42022337606bd3396710feb90be114de2d4386323'),
 ('000503e0-0001298c-withdraw',
  76172,
  'over_run_fuel_intermediate_restore/tbl',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'd01e3e567c9a6dd847ddc78602b5ac9db022cb3d6f01c911d22c3453c3a3735f',
  None,
  'aeed62a4382d5c1410ab072b37a81a32f5fad9faed5f30aeab7e41137109c0d6',
  'bb89ae068a6785b48a2a1757c584a342c48fc7f1195cca9c3481675f0183eb80'),
 ('000503e0-ffff14bd-withdraw',
  4294907069,
  'vague-snail/ram',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'd81705553131a9e20163fc8625517644ea150b1f8488cea0052a8b505f4280d1',
  None,
  'baa59527e355f29bb0af79f7e5ed1c4b4be6863d3ddb74451e622c5e03c05ce1',
  '938226a21bfa92ddc037af3fa96302012784b00b798d66d05f8f1c894a50ec01'),
 ('000503e0-ffff14be-withdraw',
  4294907070,
  'versatile-whale/ram',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '95bd095088335f1392d2daceb203c8655979cc4c4c08cc25355c97a37cb1aaf3',
  None,
  'bb5dfdf330443b90cee37766a54dd8c1492a8815d8c9af73a3027c2b0e522d4a',
  '045d4aaf5d8fdd5753ff089c46eb607d87ff79f4f4fd8db3306950efb6f68ef5'),
 ('0007c9a8-ffff4a45-withdraw',
  4294920773,
  'rampant-lobster/ram',
  510376,
  (),
  'withdrawal',
  'paired_inhibit_writer_withdrawal_paths',
  None,
  'unset',
  'unset',
  '573e631e56ccae93bdac53c1906dadcc90aeb13a9fef5f5abe97af5d7fa3f437',
  None,
  '655a2fa84d7d62497832e5b983b3f3c3d03fa486e35ed2df102116cc45e6aa63',
  '84bd9bf73afd9b8ce33ba98ce59de470f1aa56cbec233a8ee8c4919dbe3da1a9'),
 ('0007c9a8-ffff4a70-withdraw',
  4294920816,
  'realistic-capybara/ram',
  510376,
  (),
  'withdrawal',
  'paired_inhibit_writer_withdrawal_paths',
  None,
  'unset',
  'unset',
  '177290ea6eaeccff871ba8e2f041ef206f867d937656ff13aa6db177a9d94298',
  None,
  '993861a3fc9ce4cdaa848f8a988c0b217e3b9cc9a98c61bb45eebd2cb2e258e2',
  'ab540508a90c193e4079ef19b6b4a90cf1b2762a50e2dc9b38958f9417541ca8'),
 ('0007c9a8-ffff4ac6-withdraw',
  4294920902,
  'neon-seagull/ram',
  510376,
  (),
  'withdrawal',
  'paired_inhibit_writer_withdrawal_paths',
  None,
  'unset',
  'unset',
  'f5ad4f5cd86f01b4ce9c961c46d182bd1a5ca987660d96cbe7df5f127d23cd36',
  None,
  '46746e4cd601cfc6e39d8643978842d32da1212320d6afcb6ed205557c130b06',
  '7e392e2f34281e395a24f9a0920d4c32a4716d1c68e74e2eb5a2b8c3f084a456'),
 ('0007c8fa-ffff5718-withdraw',
  4294924056,
  'hallowed-malkoha/ram',
  510202,
  (),
  'withdrawal',
  'paired_inhibit_writer_withdrawal_paths',
  None,
  8,
  False,
  'ace066de89ca0e146133354756c38ccda95830904176750f776020f78d758261',
  None,
  '4b92ea754828c2b160336d1f8dd251d64f15bdb30574f2fed7a02760ba2bcddb',
  '0ea2649276bb58361c8a12da4496f9f6fc9b57b5ec8524ea88fbfa8d8416562e'),
 ('0007c9a8-ffff5718-withdraw',
  4294924056,
  'hallowed-malkoha/ram',
  510376,
  (),
  'withdrawal',
  'paired_inhibit_writer_withdrawal_paths',
  None,
  8,
  False,
  'e05ca8c55888e89a68795f8e3d2d7e22173743a4a5c13ad589ebab1854b4c532',
  None,
  '4b92ea754828c2b160336d1f8dd251d64f15bdb30574f2fed7a02760ba2bcddb',
  '0ea2649276bb58361c8a12da4496f9f6fc9b57b5ec8524ea88fbfa8d8416562e'),
 ('000847dc-ffff4a45-withdraw',
  4294920773,
  'rampant-lobster/ram',
  542684,
  (),
  'withdrawal',
  'threshold_window_reader_withdrawal_paths',
  None,
  'unset',
  'unset',
  '91332b74676dace30966b844ce5be69f9644a43a70469030650e10d0199242bc',
  None,
  '655a2fa84d7d62497832e5b983b3f3c3d03fa486e35ed2df102116cc45e6aa63',
  '84bd9bf73afd9b8ce33ba98ce59de470f1aa56cbec233a8ee8c4919dbe3da1a9'),
 ('000847dc-ffff4a70-withdraw',
  4294920816,
  'realistic-capybara/ram',
  542684,
  (),
  'withdrawal',
  'threshold_window_reader_withdrawal_paths',
  None,
  'unset',
  'unset',
  '93514d35c445d606c7c81cb64e19a3bbd9051aaadeb9c0d454b2c35f85f63888',
  None,
  '993861a3fc9ce4cdaa848f8a988c0b217e3b9cc9a98c61bb45eebd2cb2e258e2',
  'ab540508a90c193e4079ef19b6b4a90cf1b2762a50e2dc9b38958f9417541ca8'),
 ('000847dc-ffff4ac6-withdraw',
  4294920902,
  'neon-seagull/ram',
  542684,
  (),
  'withdrawal',
  'threshold_window_reader_withdrawal_paths',
  None,
  'unset',
  'unset',
  '93f75ab408e355f23abf0134e8b711b2e82ed35b6a1c75e3627e75910fdd042d',
  None,
  '46746e4cd601cfc6e39d8643978842d32da1212320d6afcb6ed205557c130b06',
  '7e392e2f34281e395a24f9a0920d4c32a4716d1c68e74e2eb5a2b8c3f084a456'),
 ('00068d58-000120ce-withdraw',
  73934,
  'athletic-swallow/tbl',
  429400,
  (),
  'withdrawal',
  'aux_rate_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'cc2cab771f9d3771294ab340e9fb92f772883f0be348085ede20c30fcf3da4b0',
  None,
  'e44cad9d223215c456482206885010d150cef470d57f78e3207370245dfe98fa',
  '984b8563f639ec414f30b5a22541152f321f147360dd89282b7da836c16d1133'),
 ('000655b4-00010b8e-withdraw',
  68494,
  'lyrical-dragon/tbl',
  415156,
  (),
  'withdrawal',
  'paired_curve_normalization_withdrawal_paths',
  None,
  'unset',
  'unset',
  '0857c64cec33d674a469dc8d6cb8fc6360314e56e1e4f09cbbc44d5c60c2775e',
  None,
  '034b6ea7b1d3a57cfe9ae857b1b626be8654ee1d3291cc0e1e9e5cc116b25039',
  '68ba1d1a29410bd0b8261336071e6f583ee8dc82ee2140e7321425657052a518'),
 ('00065b08-00010b8e-withdraw',
  68494,
  'lyrical-dragon/tbl',
  416520,
  (),
  'withdrawal',
  'paired_curve_normalization_withdrawal_paths',
  None,
  'unset',
  'unset',
  '11bcb9488d622e9f157f3d5b3a553cea1bc9f439607efa759dc9d6d0c249433e',
  None,
  '034b6ea7b1d3a57cfe9ae857b1b626be8654ee1d3291cc0e1e9e5cc116b25039',
  '68ba1d1a29410bd0b8261336071e6f583ee8dc82ee2140e7321425657052a518'),
 ('0004ae6c-00012006-withdraw',
  73734,
  'dramatic-foxhound/tbl',
  306796,
  (),
  'withdrawal',
  'byte_ratio_producer_withdrawal_paths',
  None,
  'unset',
  'unset',
  '91c32f65b77d4ec19c96531ca7402eb1fa6b3c1b05a94eb3f41128ffe2bac40d',
  None,
  '3c82afacc743bc8711b7fd180f95424692c6fb3c28d9ac859ee262f42410c25e',
  '60a30b2395a9f5adbc5100700f2d21ab4929f33cb13ee7776b3237438a5f9247'),
 ('000647e8-00012b52-withdraw',
  76626,
  'quick-basilisk/tbl',
  411624,
  (),
  'withdrawal',
  'state_surface_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '0057fd6cb20fac880f590fbd89fccd80768695872bed9c47fa438877314cec2b',
  None,
  '32e81f21247ff424a92ed5353ba843611e3e44f67db4e8044305556e4fc7d756',
  '615ac4e727f8aaa6660fae1f340769a818547ed665570d8972ffdab194b697cc'),
 ('000647e8-00012b5a-withdraw',
  76634,
  'mindful-pogona/tbl',
  411624,
  (),
  'withdrawal',
  'state_surface_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '55e5ca11aa978e3f61c1f44e450f5acc3fce0638cb0f1fdc434a77b0794c6eef',
  None,
  '1b85fa418e70b77ce70a47367a8679556b5e25cf918f9db1325920049bd56e5b',
  '798c0e385d5dbb1570c9f36e4f4840bbc137473e6585316688545d5dba4f5fe5'),
 ('0004ba48-ffff23c5-withdraw',
  4294910917,
  'purple-chihuahua/ram',
  309832,
  (),
  'withdrawal',
  'byte_factor_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '47c4932e2c5dbceeaa8d0d301089b790354738e4ef80dfa93ebb005beb915442',
  None,
  'db2c931bcffc95f70c0e61c0a9a1d58fd79fbec61d26933d4ffc5b95732e6fb6',
  '063aed7ddceda9cf58bb263b8d9651a42090f39372f13077e7d0086de04fb2a0'),
 ('000464de-ffff1693-withdraw',
  4294907539,
  'urban-ibex/ram',
  287966,
  (),
  'withdrawal',
  'byte_sum_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '1dacd2a5176d35d9dc687370413cd3502b32f21417e16988f0948a9587b9d970',
  None,
  '19c850a2cc34a18212f7101e5f296409b84f36d70126ef7f5854bda269e5da4b',
  '5fa9ab5906f0b5586b27c9a393c924fed1715ca6fa154954201e2786e13e41f3'),
 ('000503e0-ffff1939-reader-withdraw',
  4294908217,
  'piquant-lemur/ram',
  328672,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '1f4d2097a3f3458effbf6627988f7ca56994e2ac95e3acc84ff759a7a665c531',
  None,
  'ba01cb238c8e7be06cda932c2caa6164367d5ff16dc14d1e284aeca769c6b0ec',
  'f1265c1c88ef93e34295fa672ae9eb303faa0fd8e1853a61fd171879d93a60d7'),
 ('000b784e-ffff3348-withdraw',
  4294914888,
  'ruddy-anaconda/ram',
  751694,
  (),
  'withdrawal',
  'curve_scale_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  '59ee18e4be7bbc935c2e08f6fcf90dc42c21494b0ce73ff39550cc184342305f',
  None,
  '0dd1d84e8efef214bad6c82baa1c853c2471764b78f486f1633f84df08964dc7',
  '89da17abcc08cbf335c3f73f91600cf841f10a19c9f6d8ef5c89669909a06b71'),
 ('00050018-ffff16aa-reader-withdraw',
  4294907562,
  'sassy-markhor/ram',
  327704,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'a66ad148b5399b0aa33727484628763c1d8210c778dd76e365159d56098cf5f8',
  None,
  'abff2842dc4903e66ed2f824e1f5cc4165514b495436c240811d0b4a52576107',
  'c6a4aabf99a969f484474fd32fe3c9b373acda9643ae6ff6d97d13ae3e6f0b9e'),
 ('00050018-ffff1778-reader-withdraw',
  4294907768,
  'nocturnal-adder/ram',
  327704,
  (),
  'withdrawal',
  'dfco_state_caller_withdrawal_paths',
  None,
  'unset',
  'unset',
  'ee78dd754d5bc5778e829fa0e0fad67c39036ac7bf491d27c0fd7f3a9af3dbf7',
  None,
  '243c9f95d9d0ff1394d96f292112c97a6902baf5e23d64968ba2c1f3f1f7ae27',
  'b55ea87326019c5359eae056c06670d06a6a92ef21c222f1b64ae2658c2c5a37'))
RETAINED_FUNCTIONS = (('lime-kittiwake/fn',
  154046,
  'kb/fn/lime-kittiwake.toml',
  '914600a187457062625df49c0c38b17ad75a872489ba1283205c7484177e0297'),
 ('liberal-tuna/fn',
  234888,
  'kb/fn/liberal-tuna.toml',
  'bba18f0ee67ba676d3483fbc7806024d659cd82b49ad19096e376cd5711e0ccd'),
 ('rose-hog/fn',
  235636,
  'kb/fn/rose-hog.toml',
  '23c22819a35aa3622ea1c4c196a21e1d97c204881219645f45e3403a9a0425ca'),
 ('thick-lionfish/fn',
  288944,
  'kb/fn/thick-lionfish.toml',
  '3a41180ce4afdf695d6aed620378f74d576b13d00195057c1a1487758090f37c'),
 ('tuscan-jerboa/fn',
  306068,
  'kb/fn/tuscan-jerboa.toml',
  '656f8c27dc1f4dc2dd9b72d47bc6c972ad41e3027de97e727c031ac771af13e9'),
 ('selected_timing_state_terms/fn',
  307000,
  'kb/fn/selected_timing_state_terms.toml',
  '7ae0b2481f75b505b250a68ccdba28adc6455c30bd1dcdea3ab5a1ee6301c7f8'),
 ('clever-woodlouse/fn',
  310122,
  'kb/fn/clever-woodlouse.toml',
  'ddf5fe92c1c0d22c06997bb95b7886fd273c27d457ce850d85f199eb122a59ff'),
 ('timing_state_latch/fn',
  311606,
  'kb/fn/timing_state_latch.toml',
  'ccaa4e201f813b8ab4e8dc3c9d0b37b9160c8cec23fd939a8f6009d7787fe247'),
 ('timing_state_decay/fn',
  319762,
  'kb/fn/timing_state_decay.toml',
  '75d0975588f360f812dc460a36cbee2880a4c89a4fdf7413e90bf933f8dcac0b'),
 ('fuel_base_accumulator/fn',
  349358,
  'kb/fn/fuel_base_accumulator.toml',
  '00979e3c706cba6cd6a04d88d510d481ad37405d6c9c859214de61a655ddefee'),
 ('request_limit_selector/fn',
  462210,
  'kb/fn/request_limit_selector.toml',
  '9e4019fa68da299f39b88111cda485a38a510032416755bc901935769068023c'),
 ('defiant-galago/fn',
  677168,
  'kb/fn/defiant-galago.toml',
  '0abddd9d15675f1453005f0416cee1a55e14fedcaabbb51756fcf1d711ceb8f5'),
 ('tall-tapir/fn',
  337820,
  'kb/fn/tall-tapir.toml',
  'afc3516986028bd3ddcb64d31c9eb59441032014b1ae80dfb1802255f32f2bb1'),
 ('transient_fuel_additive/fn',
  338178,
  'kb/fn/transient_fuel_additive.toml',
  'b7347bc42332e6b3ce5ab5dbd13c6d6e7db73e7ea8ee11bac6b7b6efef73d90f'),
 ('mini-wren/fn',
  345164,
  'kb/fn/mini-wren.toml',
  'c8a48c4af0cc145bd47796b0345151347d10e248a0e23891e9be80be3e0c5489'),
 ('cherubic-narwhal/fn',
  676484,
  'kb/fn/cherubic-narwhal.toml',
  'e93c04f325c9a5644010ac7622a23210e2c096f4613afb520c7903842353e96d'),
 ('piquant-echidna/fn',
  250972,
  'kb/fn/piquant-echidna.toml',
  '7fe7c4916f785902564281864ad62decf0e3bb3b9e8a64bdf1718e45bd37fc7d'),
 ('khaki-dodo/fn',
  279624,
  'kb/fn/khaki-dodo.toml',
  '4e15e323389e02339fec23a9821abad5d059f00099fea8a144172c415e597ca2'),
 ('brass-barnacle/fn',
  478216,
  'kb/fn/brass-barnacle.toml',
  'b12804e8749cbd636802ad4b9ecc6cd6e69ffc0f8101e343fe200f7acca2be5b'),
 ('transmission_request_bound_publisher/fn',
  489466,
  'kb/fn/transmission_request_bound_publisher.toml',
  'eda84a53fa5ff86273e1dfd27155664dee835337bd9d545b6ea1fbf9ffa742f5'),
 ('fortunate-mantis/fn',
  591848,
  'kb/fn/fortunate-mantis.toml',
  '37e514dd7999750bee8c46adffaa9a620cbd966af64c4aaf0b92d49683c520ef'),
 ('dual_bank_maf_fault_rpm_inhibit/fn',
  325430,
  'kb/fn/dual_bank_maf_fault_rpm_inhibit.toml',
  '7c9fba647f8422e24827293805b6cae9d8dab72d6516c8598251be4df39e0ddf'),
 ('low_speed_sustained_rpm_inhibit/fn',
  325976,
  'kb/fn/low_speed_sustained_rpm_inhibit.toml',
  'd78bc99aa876590006ea6fbba1a3d2226fc6c11bec93e60a5b1eda4e519786f4'),
 ('dfco_exit_delay_select/fn',
  328586,
  'kb/fn/dfco_exit_delay_select.toml',
  'e4149b74c190e81fb0e315343c229c4ce1cba6343cd8fd2960aed9522fdd39e1'),
 ('rough-porpoise/fn',
  157124,
  'kb/fn/rough-porpoise.toml',
  '5348c3783f73f66dca2bbe43e4bcb39432febdba0f8bbf068e2581059f6f7b31'),
 ('smoky-mantis/fn',
  451728,
  'kb/fn/smoky-mantis.toml',
  'eaaf57b898b5e9bfaca272d1f38e9aaa360b3bb00699f3125e5d413f5cbcf1e7'),
 ('sapphire-scorpion/fn',
  484224,
  'kb/fn/sapphire-scorpion.toml',
  'cea6c94f4e7dccefb649939a52a3dfe6119c1e9fd00f0cb4dc57f4db4d18269b'),
 ('throttle_target_scaler/fn',
  831946,
  'kb/fn/throttle_target_scaler.toml',
  '488d08c4c449345dfc0ffd36d3989687ac9830ad6cce522b2c85125d146b4316'),
 ('low_speed_rpm_exposure_accumulator_update/fn',
  325600,
  'kb/fn/low_speed_rpm_exposure_accumulator_update.toml',
  '587f9aabda58625338e8dd77625fd7c624c9aba6c6af82210886dfe3c1398162'),
 ('transition_window_low_speed_rpm_inhibit/fn',
  326084,
  'kb/fn/transition_window_low_speed_rpm_inhibit.toml',
  '876fbe6d1d471288d94725d33bfe6aa80b58c963e95d5fc53f707222a4174b84'),
 ('burrowing-muskox/fn',
  335924,
  'kb/fn/burrowing-muskox.toml',
  '3dee37e83032b1d8e81ead0fff6cbbc6894351d492a82efed88bc783515450c5'),
 ('daring-mongoose/fn',
  238164,
  'kb/fn/daring-mongoose.toml',
  'c2d39e6fb5a74005e41a043021a4194c115a2a0b9ca3fa42eb3ab4762dea77d3'),
 ('cobalt-fossa/fn',
  451650,
  'kb/fn/cobalt-fossa.toml',
  '093c32543486c67aa1b0a011995cc4629daa654bc0103f8492fffe12dae572b4'),
 ('adaptable-wolverine/fn',
  752772,
  'kb/fn/adaptable-wolverine.toml',
  '5940e1a24252b39b3473be8b5d43e6148152ae42331973e3ece1ef559812576a'),
 ('radical-chimpanzee/fn',
  181660,
  'kb/fn/radical-chimpanzee.toml',
  'c6686c4d13ef16ce04002cd744394e9684ea0f84b62a840bc99ceb2e0895ed68'),
 ('burgundy-hawk/fn',
  451544,
  'kb/fn/burgundy-hawk.toml',
  'a2f9f4be5c5f244e0f5de7dd87105739f22c5ccbe27e684b5360066e1e5d673a'),
 ('vigorous-silkworm/fn',
  470814,
  'kb/fn/vigorous-silkworm.toml',
  '02e0bbf82d78578ead849ee662ff3b337d58ea15550a8d2ab0895589521d6a9a'),
 ('cherubic-piculet/fn',
  752536,
  'kb/fn/cherubic-piculet.toml',
  'bb005b09d5c85f5927fc0619722ae3f9680a434fa4f57eadf84359daeab897d1'),
 ('angelic-ermine/fn',
  320924,
  'kb/fn/angelic-ermine.toml',
  '33314ee5029032de427d83ca0d7157ede4143c8237ca0a2797939b4b408e1e38'),
 ('persimmon-binturong/fn',
  476280,
  'kb/fn/persimmon-binturong.toml',
  '9b1a029aa907d70db09562c63b585f6c7f5b1548b87214441f31022c00aef611'),
 ('crouching-shrew/fn',
  477956,
  'kb/fn/crouching-shrew.toml',
  'c72513ade96d365d36e3d66ae51a8a0d72e7c90e22272f183747f719793e55ca'),
 ('curly-flounder/fn',
  751464,
  'kb/fn/curly-flounder.toml',
  '0d27a338bbb5e3a397a339e1c27189e895b694e07169cd901ed32f322685b40c'),
 ('refined-goose/fn',
  751834,
  'kb/fn/refined-goose.toml',
  '40063a6584c3ab43942fc36c6098f365297c0cd1e12f953ebbad573ff75efe08'),
 ('viridian-armadillo/fn',
  752188,
  'kb/fn/viridian-armadillo.toml',
  'bc4f4c91414b22abd74914024f2a40b0c8f6e5f433721e70d967b975f6fef4d2'),
 ('lush-degu/fn',
  340654,
  'kb/fn/lush-degu.toml',
  'dd99a670f310e2d4b556f5f0f2bed74887f0ddc22a5544c98d189895a4dad402'),
 ('authentic-eagle/fn',
  478056,
  'kb/fn/authentic-eagle.toml',
  '71def191e6aff95d0d0728674444113123d26ad0ca276d03da000df97a5ea41b'),
 ('pedal_request_scaler/fn',
  480006,
  'kb/fn/pedal_request_scaler.toml',
  'a5530c65bd0947e4671b1ecc562fa27f49735726bc521231df89969c8f5e78cd'),
 ('spiritual-rattlesnake/fn',
  242840,
  'kb/fn/spiritual-rattlesnake.toml',
  '5157a8b04ebc4bd2ee4a866c3329424563778d94a8ac627fbd547a768e598720'),
 ('cooperative-tench/fn',
  269750,
  'kb/fn/cooperative-tench.toml',
  'fbeb79ad56bacc4e8c778b82e0ae03bd1aa0ca375a08f0f5e247ec006daf2bd5'),
 ('timing_state_compositor/fn',
  310722,
  'kb/fn/timing_state_compositor.toml',
  'df3cd3a8b0eeccfdafd3d17d1e64c339dc953b7c7b3a51a4cdd292e23461532a'),
 ('white-malkoha/fn',
  416174,
  'kb/fn/white-malkoha.toml',
  'b6486eace6a7aa5d88cb17bf77596194cd53351970cd9f6ab7ace306a693872b'),
 ('event_timing_correction_builder/fn',
  317852,
  'kb/fn/event_timing_correction_builder.toml',
  '0b2b1618d87b96fe1d10b5e115165415042dc8d1952af3e79dde5ca78e7ba79a'),
 ('transformed_pulse_maximum/fn',
  336296,
  'kb/fn/transformed_pulse_maximum.toml',
  '8313edde2fec8aa83e1be71d3548a1e839b02df03283378efc2e6bd18d0a52e9'),
 ('strange-mushroom/fn',
  412850,
  'kb/fn/strange-mushroom.toml',
  'ae2c6408194d9d8b94dbc3bea72bdfce258f253e9d956cc8477502084f33ad13'),
 ('radiant-cuckoo/fn',
  777318,
  'kb/fn/radiant-cuckoo.toml',
  '6ba7ac014b97f20036ea3fb1d3dfe0b4e1eacb906f21f326b09ff6fdc752efd8'),
 ('dfco_state_machine/fn',
  328672,
  'kb/fn/dfco_state_machine.toml',
  '1ce5e49eb58040205d54f311c8582184e1228517db2f64bdca95aa3b86d23904'),
 ('classy-seahorse/fn',
  510202,
  'kb/fn/classy-seahorse.toml',
  'f96653b29b6fb8357cdfece6931853bd98ac231c167db36aeaa60920893bd5b9'),
 ('persimmon-giraffe/fn',
  510376,
  'kb/fn/persimmon-giraffe.toml',
  '00c1d87ce8ca7b351aad8c35da9da1679ec9fe8060d0c96807c718e75d858bdf'),
 ('devout-avocet/fn',
  542684,
  'kb/fn/devout-avocet.toml',
  '456e01f44932c89c432b6c7977deba5c3b7002703add7b11f0d4c10acbccb78c'),
 ('sepia-marmoset/fn',
  429400,
  'kb/fn/sepia-marmoset.toml',
  'b03d4814da6a959fc851727391f8514831437967fd733451082ddc3ea6465642'),
 ('vigorous-saluki/fn',
  415156,
  'kb/fn/vigorous-saluki.toml',
  '04104f7c47f145a4babbea50ec38679123b8671774d5bb823e42767a41deca33'),
 ('silky-vulture/fn',
  416520,
  'kb/fn/silky-vulture.toml',
  '23a4446f046ff2a2901035dabc1ce1a2b305689df32287aec670cc1d35b9b6d7'),
 ('energetic-honeybee/fn',
  306796,
  'kb/fn/energetic-honeybee.toml',
  'c4dfc6fdcc4f1e7ba546c9cb3c3a173503ef12f3d63c8772d8be55e72099e1fd'),
 ('spotted-zebra/fn',
  411624,
  'kb/fn/spotted-zebra.toml',
  '2b70a85848157a084c9b33bf40dfcdeada568997b216cd576c70f5b0c1d8e989'),
 ('charming-warthog/fn',
  309832,
  'kb/fn/charming-warthog.toml',
  'e93956baaf7fea895c081f4e1d4015dde485ab1da09e971850dd871c5b9771e9'),
 ('cherubic-salamander/fn',
  287966,
  'kb/fn/cherubic-salamander.toml',
  '71929d38a641cfc3a71e837a3c5ee7ad3bad2d9aec1eee82552f6f628b61ead1'),
 ('uptight-duck/fn',
  751694,
  'kb/fn/uptight-duck.toml',
  'c869d66b1a0495c487e8891a60e23c09439104abeea09203f1da1356dbb678e4'),
 ('dfco_restore_classify/fn',
  327704,
  'kb/fn/dfco_restore_classify.toml',
  '9bd459160be17c1280b8dd9693505e0715e26d2a7058541c14fce47009858937'))
PRIOR_REFERENCE_SHA256 = '97065661723b863b4a61c65e304a3a6fa4492b31b1859eee8b6ce516322759c6'
PRIOR_FUNCTION_SHA256 = 'd4546448515592cbda8fd42e6c762217dc27943572d644e0783620f59d1c691e'
PRIOR_FILES_SHA256 = {'defs/JK08A.scalar-ram-leaves.toml': '6e90413cffcac41a4379ddf756094592f173ca4031e81b97abed134f322bfd11',
 'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s': '501e6a13f06a3c91159bdc57b3c79945bf92a186fc11cd9055cb1579ccdfeb93',
 'tools/kb/src/kb/scalar_ram_leaf_contract.py': '5b10b67e5955923947b26b87bb15dbace6ae4e968289ebe3f25bf04396dc36e0',
 'tools/kb/src/kb/scalar_ram_leaf_matrix.py': 'b82b6c14907f766941ca8f79dd9be3b80add80968881fc0702397b13a24079a9',
 'tools/kb/src/kb/scalar_ram_leaf_semantics.py': '043a59b8465c045d025ad79aaa50adec277a67470cb65c9dab986761ff822abc',
 'tools/kb/src/kb/scalar_ram_leaf_transfers.py': '4242ddf6eae3cf0b6816ca60043cef08bc4fcb5b814b6d5269d83a7aa12c6f75',
 'tools/sh-elf-run/scalar_ram_leaf_capture.py': 'a0bb6ad156d713930d346ae3ef4d5dbdfc90c6a1e10f5ced9a7fe2fca38e37d6',
 'tools/sh-elf-run/harness-scalar-ram-leaf-paths.c': 'c24c336b28ce6d583541047fb9f71dc74ae5cfe4d50af06d1541b277d07aecd1',
 'tools/kb/tests/test_scalar_ram_leaf_adapter_generated.py': '3715a3e5a2e8274a1740e518111304d6181c2d50d365773dac1258fb6dbddb8f'}
PRIOR_JOINT_REFERENCE_SHA256 = '4f2634e114834b271b31e99c1fd3edaeff2515df6227904fd6418e49b696d34b'
PRIOR_JOINT_FUNCTION_SHA256 = '7f2bfc8d4ad207c45e381ae4008cd82e3cfc836b26e461c69a2b76408a04b686'
PRIOR_PRODUCT_FILES_SHA256 = {'defs/JK08A.scalar-ram-products.toml': 'ee1f9bb0f6afe2606c33eca501052cff507745ced9644e62983b6919a0c16a76',
 'tools/sh-elf-run/stock_jk08a_scalar_ram_products.s': '57e95f4f5580831571a4bab48c2b27f387df51d6d7cb78e43e12b0d570a6180f',
 'tools/kb/src/kb/scalar_ram_product_contract.py': '59d534fef42b21bf67b9858255dd91a41ae836df2bd9d79814fbc405ba36d5e8',
 'tools/kb/src/kb/scalar_ram_product_matrix.py': 'bda2a71c276ea8ef6a41c0f626a4203b7c0be92cea856bef127d8a3cd555d647',
 'tools/kb/src/kb/scalar_ram_product_semantics.py': 'fb783312ae6153f74dfbf53f65fca378d691eff3f7f8d8a697f8b1ce88a525d9',
 'tools/kb/src/kb/scalar_ram_product_transfers.py': '42d5db98342a0885ca67b9d56304aedec953f7820532292ca39dcd3b6c6ea3db',
 'tools/sh-elf-run/scalar_ram_product_capture.py': '3ec1e95a35d3307662a9ca475be4b2d2383a4e6af70b463cc29dd38279f3bfd1',
 'tools/sh-elf-run/harness-scalar-ram-product-paths.c': '37b200790f660248d3b90414949a7bb792e2be4c1fd5b2835ede3124e809244d',
 'tools/kb/tests/test_scalar_ram_product_adapter_generated.py': 'a2e284ef480fcb5718aa4b7799d88d0bd4f7c500b0d49778c8f34dbecddc4c68'}
PRIOR_GATED_REFERENCE_SHA256 = '6b957fe713297e9a6d1192b1b0c15af07aaf28ba46139ea25a068c9787320861'
PRIOR_GATED_FUNCTION_SHA256 = '018b612f8ce19c6d4da56d45764dbfd07b61dfb555637655407cbead2ac21d2e'
PRIOR_GATED_FILES_SHA256 = {'defs/JK08A.scalar-ram-gated.toml': 'd3f5e4a8d416fc94d28241a1101b67bbb127472a3b69f99b16447fb8808d0834',
 'tools/sh-elf-run/stock_jk08a_scalar_ram_gated.s': 'd9926cbb33e1aedf650cbabd4051f7742855a2020af48ba2384875f3ba98d63c',
 'tools/kb/src/kb/scalar_ram_gated_contract.py': '4e315d4e8bad246f853dc6d800b88e670055b6b845199ca32fe2fd7bd3b83993',
 'tools/kb/src/kb/scalar_ram_gated_matrix.py': 'a14523746f0626b25abaed69b692928d785f74bd3e93da13c09358232f5966a6',
 'tools/kb/src/kb/scalar_ram_gated_semantics.py': 'f8d087db1c6d5c8a4d157195af5fdf6f06b798a50a94b064b39aae377a1010aa',
 'tools/kb/src/kb/scalar_ram_gated_transfers.py': '30a009a87017b3afff1cecb7b0c86adebd47e471a2a1b4b6929c5de1079afb47',
 'tools/sh-elf-run/scalar_ram_gated_capture.py': 'c30b3e9baa1477fe028ea791e66fb7776a43cf3bf48ba7c594d37e33b8bd845b',
 'tools/sh-elf-run/harness-scalar-ram-gated-paths.c': '296bcdec953ba2dafb679f48c9342c9b7a377788ede9b2b2ed4b993a307817f7',
 'tools/kb/tests/test_scalar_ram_gated_adapter_generated.py': '392a006be15987839adb9efe5d06fedd4bdda16df4d7b0230a535126f64bb87b'}
RELATED_OWNER_INPUTS = (('defs/JK08A.counter-access-claims.toml',
  '2ead62713db1018feefbdf6c229ebe686455d2b080cce687ad20ff02db7b0416',
  'authentic-monkey/ram',
  ('ffff2573-writer',),
  'f1d77f6eaf487380cfdbfba016029376b5a57a3f760dfc61aa31c08d5030ef58'),
 ('defs/JK08A.maf-access-claims.toml',
  'f167526cab71bb45a83db2487fbdc1da237ae0ecd139cca9c3c419b0b238bcee',
  'tourmaline-jackal/ram',
  ('record0129-00025e20-member-reader', 'record0129-0003c3ac-member-reader'),
  '819b4b8ea255fb1df449762eb2975f9c8ad6b6f6c8ccb4e5f06c02df2dbf0de7'))
NATIVE_LINK_ROLES = {'0004f958-ffff11ae-withdraw': ('indexed_by',),
 '0004f7e0-ffff11ae-withdraw': ('indexed_by',),
 '0004f9c4-ffff11ae-withdraw': ('indexed_by',),
 '0003a254-ffff115e-withdraw': ('indexed_by',),
 '000b7c84-ffff33fc-withdraw': ('indexed_by',),
 '000b7b98-ffff1024-withdraw': ('indexed_by',),
 '000b7b98-ffff11bc-withdraw': ('indexed_by',),
 '00072f1e-ffff1d10-withdraw': ('indexed_by',),
 '000b7768-ffff2733-withdraw': ('indexed_by',),
 '000b7768-ffff3348-withdraw': ('indexed_by',),
 '000b78da-ffff110e-withdraw': ('indexed_by',),
 '000b7a3c-ffff110e-withdraw': ('indexed_by',),
 '000b78da-ffff2733-withdraw': ('indexed_by',),
 '000b7a3c-ffff2733-withdraw': ('indexed_by',),
 '000b78da-ffff3348-withdraw': ('indexed_by',),
 '000b7a3c-ffff3348-withdraw': ('indexed_by',),
 '000b78da-ffff35a0-withdraw': ('indexed_by',),
 '000b7a3c-ffff35b6-withdraw': ('indexed_by',),
 '000b784e-ffff3348-withdraw': ('indexed_by',)}
PRIOR_RPM_RAM_REFERENCE_SHA256 = '3bd975e9f3f02b055b05fa36aa708633441c21b47c598a940658b046923f3b0e'
PRIOR_RPM_RAM_FUNCTION_SHA256 = 'fc72ce9be899e1efd9ba000b55d03a2b045a36600cc939be5e82bacfb233236d'
PRIOR_RPM_RAM_FILES_SHA256 = {'defs/JK08A.rpm-ram-withdrawal-paths.toml': 'b826bccb4d6da7134e91bdb89b78a2dda56b727e6f9ff1c69ab7e510a5ecbb2a',
 'tools/sh-elf-run/stock_jk08a_rpm_ram_withdrawal.s': '0490a906e82972b0e48edfc313a5fe7adc3d66b970949fc47cfadb05ae92434f',
 'tools/kb/src/kb/rpm_ram_withdrawal_path_contract.py': '1d79d114fd7f2327a559163b2847d63fe87f2113cf527dd6b30b88ec3ecfc330',
 'tools/kb/src/kb/rpm_ram_withdrawal_matrix.py': '10bb6a8660100107ae89eeca859bc9e7749230100434f0f034bda7fe2d4a25b1',
 'tools/kb/src/kb/rpm_ram_withdrawal_semantics.py': '895a7212d5e1a8e1424a0349b11733abde899523dff229f1748748867c6b3a13',
 'tools/kb/src/kb/rpm_ram_withdrawal_transfers.py': '544146eb00637dad9646d5dfe0392d4921c6e39758b0ec4d8b681bb4066fba6b',
 'tools/sh-elf-run/rpm_ram_withdrawal_capture.py': '3c2f0d27b573f5ad6e8244475b994cd4b136273e42eb173735b25c26bdde5ecd',
 'tools/sh-elf-run/harness-rpm-ram-withdrawal-paths.c': 'bdfaf5638dadabf6ab9e9d5eed6740295abe3cf27e01b1de1ba427a8daf9268f',
 'tools/kb/tests/test_rpm_ram_withdrawal_adapter_generated.py': 'b5e21f0e8a9a8c4cb85fead30519f12eafa0ff019893a0dfb1715e3aa855680f'}
PRIOR_OVERFLOW_REFERENCE_SHA256 = '8915db074efb3d07481f35e3cf8d2d23dcc67e3ddb501e186e3d0196ced11a79'
PRIOR_OVERFLOW_FUNCTION_SHA256 = '99073339fe4dc1fa7113056be859dffa79228ae0cfed7ce3db5ffe592fd97f84'
PRIOR_OVERFLOW_FILES_SHA256 = {'defs/JK08A.register-overflow-paths.toml': 'ab0c75d4d17bd9364b5250f5e6204a7bc64dc9d962fba690cdcc9075fbb0426e',
 'tools/sh-elf-run/stock_jk08a_register_overflow.s': '105da0974169d90f3c543494fb443f2dce108b3116c374cf57fb66bcf9c20d9e',
 'tools/kb/src/kb/register_overflow_path_contract.py': 'a5d72cb5f0280347ac41bc2d6710b7bd9eb083ae99e18a39cd74670643e4879a',
 'tools/kb/src/kb/register_overflow_matrix.py': '5032411cb6337e13a47c2cf33855e417b3c4f3f10ec725bf4be15a09e6da6c22',
 'tools/kb/src/kb/register_overflow_semantics.py': 'fe7ffbd451bfc9f883a4428bd0bbd4919ff346c099ea8eaa605251d6b7925b28',
 'tools/kb/src/kb/register_overflow_transfers.py': 'f0d3cde573f998164dea1f8f48a779567a150a897c566ab6f1e42702d93ddb06',
 'tools/sh-elf-run/register_overflow_capture.py': '1dcdfa3dece3a588b3c5a53ccff919011c1daaa9e43b049207136c8bfc28ec36',
 'tools/sh-elf-run/harness-register-overflow-paths.c': '45bae2bedc27ee5ab60a6723451caac3e9ce9aac4f2dd55b3a5cb6064f0ec1c1',
 'tools/kb/tests/test_register_overflow_adapter_generated.py': 'e853f2a7bef8824673ed68b553c0614aaf867c6302ea1598113a18e121546782'}
GATED_ASSEMBLY_SOURCE_REPAIR = {'path': 'tools/sh-elf-run/stock_jk08a_scalar_ram_gated.s', 'before_sha256': 'd9926cbb33e1aedf650cbabd4051f7742855a2020af48ba2384875f3ba98d63c', 'after_sha256': '74ad8b6ad76131e2b3f7469c3415f6962dc4f0ffb4d35aa6495cc83ffa90c0ae', 'exact_text_changes': [('L_00044468:\n    shll 2 r11', 'L_00044468:\n    shll2 r11'), ('L_00074c5a:\n    shll 16 r2', 'L_00074c5a:\n    shll16 r2')], 'instruction_words_changed': False, 'source_preparation_only': True, 'assembler_execution': False}
PRIOR_WORD_REFERENCE_SHA256 = '0f720a974ec695faee5cca8a2bcf402a6b94225e72e3c7a5afa40e16294d7db8'
PRIOR_WORD_FUNCTION_SHA256 = '3c4f5c09acecc776a890224e1cddd6509f795f8281007c4f56dc0f91d6b53e2d'
PRIOR_WORD_FILES_SHA256 = {'defs/JK08A.scalar-ram-word-paths.toml': 'ece0399ed23ddb3111a4fd9d57e6e4567f1f45380625ec38c07f5c194eead2df',
 'tools/sh-elf-run/stock_jk08a_scalar_ram_word.s': '7c64e2966ab6d8467fd75b36b841d3d77d7d21dbda3d45d39719a068656bacf5',
 'tools/kb/src/kb/scalar_ram_word_path_contract.py': 'b09750b9ba64c38aa9fc1318632cd6df03bcd3063457a1136f369dbbdf131a88',
 'tools/kb/src/kb/scalar_ram_word_matrix.py': '47d138a37cb2cb3feae1b48e0bcc026e8b3186395a0e9c0a7ce5a12e261b5de4',
 'tools/kb/src/kb/scalar_ram_word_semantics.py': '1cd33cd7782c01a5bae3b603b7c8ed50d4d0f7e676d9d4b9f2ce73e4f1c387f1',
 'tools/kb/src/kb/scalar_ram_word_transfers.py': 'f383d57685d040a65dc3d7e14b023e289cc7d9e1ac2bd08b95a4db8727753e6a',
 'tools/sh-elf-run/scalar_ram_word_capture.py': 'd9adda16d6f7549d123b455869857c6b22552347580e5101d0a01a49328f07ec',
 'tools/sh-elf-run/harness-scalar-ram-word-paths.c': '7ab008689357093abb8599cebd1d074d718d5db0b8e655e09b98a3ee6046fc0d',
 'tools/kb/tests/test_scalar_ram_word_adapter_generated.py': '18e16a51f203daac331c31336fced1d9dd1b45a377ba2c38e20b9e12de458194'}
ORIGINAL_LINK_TYPES = {'00052034-ffff120e-withdraw': 'writer',
 '0006e3d8-ffff1300-withdraw': 'writer',
 '0006e3d8-ffff1f86-withdraw': 'writer',
 '0007c9a8-ffff4a45-withdraw': 'writer',
 '0007c9a8-ffff4a70-withdraw': 'writer',
 '0007c9a8-ffff4ac6-withdraw': 'writer',
 '0007c8fa-ffff5718-withdraw': 'writer',
 '0007c9a8-ffff5718-withdraw': 'writer',
 '0004ba48-ffff23c5-withdraw': 'writer',
 '000464de-ffff1693-withdraw': 'writer'}
PRIOR_RPM_STATE_REFERENCE_SHA256 = '56a8137b06abe0c18c93f2b656a526eeacd26336674ec9477ed5e76f8e85ae8d'
PRIOR_RPM_STATE_FUNCTION_SHA256 = '52f9ce10cc144b22183491cbbfcc2692b8729de7140536f3080d38e54d6b8bc8'
PRIOR_RPM_STATE_FILES_SHA256 = {'defs/JK08A.rpm-state-withdrawal-paths.toml': '186a30623053641f6ebc6ec33ba6950c343cae2f0e12358a199733b647e83dc6',
 'tools/sh-elf-run/stock_jk08a_rpm_state_withdrawal.s': '9b1375503ba40dabc0468cf12da9f3230142d4f8ca7b74e19e03c51995f1d1b6',
 'tools/kb/src/kb/rpm_state_withdrawal_contract.py': '2a80f8ca27381329003177818a07f002c59e64a0ed0733c1e5fe66e1916be89d',
 'tools/kb/src/kb/rpm_state_withdrawal_matrix.py': '814617d96572b5b1b7dc50f785a454c4a363d95d8ab9e8408252b21ada039a8f',
 'tools/kb/src/kb/rpm_state_withdrawal_semantics.py': '2d641560792c5fa957076ec089275f90f592460059a9858f21c159c8d03fd0ca',
 'tools/kb/src/kb/rpm_state_withdrawal_transfers.py': 'fbbe667c6364d71c9d50043fccca8c86bc4304be6f70963b4bc936df411b26c0',
 'tools/sh-elf-run/rpm_state_withdrawal_capture.py': 'dcfa77801506326598b63d34823fd05e25d3822e7d3f671b7dee02f84aecb42d',
 'tools/sh-elf-run/harness-rpm-state-withdrawal-paths.c': '6a1dd3864b693a1202ea3302027bc133317bde4a5f95180b0ef7a6fbc9a7a3ae',
 'tools/kb/tests/test_rpm_state_withdrawal_adapter_generated.py': 'eb2801616bb71e85fc2d41a07ea0d1f9f7586310efad12ff0e05a949376fa0ea'}
PRIOR_INDEXED_WORD_REFERENCE_SHA256 = 'fbdb8f2efb24da18c8f9e4f5006e1e6977d03e0c0242504d5c4588f74c018b6b'
PRIOR_INDEXED_WORD_FUNCTION_SHA256 = 'ed333ac1895de45be3572fe75812b80d451cf355093da3de4924ba5e42621bdd'
PRIOR_INDEXED_WORD_FILES_SHA256 = {'defs/JK08A.indexed-word-update-paths.toml': 'e6582da9f41dca64f68abdec63d39e93151ad438133ba3b57d5139a58cbe82b1',
 'tools/sh-elf-run/stock_jk08a_indexed_word_update.s': 'd9d00de69f1c726368be7181cc5d44eb86db008a2b610f4bcde0e1db25d8b595',
 'tools/kb/src/kb/indexed_word_update_contract.py': 'f64cd46822fb16d5e290cc0bf6c38460521f640b24bb4dc00a50e22cbc0f97ef',
 'tools/kb/src/kb/indexed_word_update_matrix.py': 'a1a072ff3964f05bfbba6787ee5c64d199f8c41f1a87fcb5302c55014fac2650',
 'tools/kb/src/kb/indexed_word_update_semantics.py': 'e765d967cc73ad4fb872dd430e4bd87487907aa08c5b802faf10a758b35bcd98',
 'tools/kb/src/kb/indexed_word_update_transfers.py': 'b031abcb966e1a5f17710b012baab8f652e12f954c7ac95f442b2d1ff4380fd7',
 'tools/sh-elf-run/indexed_word_update_capture.py': '870db2304b7240f2c34e3c0c96666f201844f7a99a3d2199d50e0f6bebe7ab1b',
 'tools/sh-elf-run/harness-indexed-word-update-paths.c': 'f1258cabf525d654b5a382bded695a536cabae1ff9bf7e7679977b14b13f9326',
 'tools/kb/tests/test_indexed_word_update_adapter_generated.py': '5edf16f78a8f04596d91c731ecc3d9e1a544849923b64016b2435b8532d2486a'}
PRIOR_DIVISION_CALLER_REFERENCE_SHA256 = '622cfc256e0e316a69d3970863f155063276844ac25ebfb44a646a9b5b051ac4'
PRIOR_DIVISION_CALLER_FUNCTION_SHA256 = 'a57f79b2bea51e59c8dbdf24c3bb80c862fc6e7a8b3507fa632f67b97311dacb'
PRIOR_DIVISION_CALLER_FILES_SHA256 = {'defs/JK08A.division-caller-withdrawal-paths.toml': '879410ec813e78ae4fc6ed3646a9803e78d83067d3d7d5b37b0d2d3071764352',
 'tools/sh-elf-run/stock_jk08a_division_caller_withdrawal.s': '3d605c3cb2c7f2c19b84b92c51be55ee1b59701480aa59d76ca78dd90d796667',
 'tools/kb/src/kb/division_caller_withdrawal_contract.py': 'b2b963a3446867fe6a6eeb494707312f572d62779060b9bae85341d1292ead23',
 'tools/kb/src/kb/division_caller_withdrawal_matrix.py': '47202ddcbab9180b6d2bd7b1a04cead69d5c4ad77c185a958d354b2a579f4401',
 'tools/kb/src/kb/division_caller_withdrawal_semantics.py': '0fd6b36d6618ef2e07b5bc59eee67d3186ce9cddeda257608af9e5a0a1bb9a94',
 'tools/kb/src/kb/division_caller_withdrawal_transfers.py': '2574ba811ea05471caee1eb932af889725c7f650395e49e699436324db9f87d6',
 'tools/sh-elf-run/division_caller_withdrawal_capture.py': 'deddad694de7ed1678ca667ffb93443d5ac520cbb7b10a100ccb9ade67c14d75',
 'tools/sh-elf-run/harness-division-caller-withdrawal-paths.c': '3f6154bf7068233ae42a999cb58624eccf17bd14bf89c622da400413b9eec999',
 'tools/kb/tests/test_division_caller_withdrawal_adapter_generated.py': '6ad4a0ba8cee21d9723115fbc1a59bc8614ef8de1bfce7e7e4de338a2fd961b3'}
PRIOR_BYTE_CURVE_CALLER_REFERENCE_SHA256 = '61c6cbfa819f518b84c9caa61e88dfe8968a0e2864d20e0a6e440b45569bf6a7'
PRIOR_BYTE_CURVE_CALLER_FUNCTION_SHA256 = '1411dd8072be9438222c878634b56596f0591fc90f503789d0c8579bbc6e53d2'
PRIOR_BYTE_CURVE_CALLER_FILES_SHA256 = {'defs/JK08A.byte-curve-caller-withdrawal-paths.toml': 'eef3bb053ec07819d675547b5667b0a188cbc0343643f318db8100ffe15e65c7',
 'tools/sh-elf-run/stock_jk08a_byte_curve_caller_withdrawal.s': '2042cd93ebd162de58c83323ba6477a37d5110a211b6d7755425dc33d6bd3c21',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_contract.py': 'aaaee28de43a668abbaf7ab4d1d0288eeedfbd7c19436dc78103dbb62d52c5dc',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_matrix.py': '3afd1bda60c112551d18e8fecb2197982f99550e94d97d0c63b7feec58a5e035',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_semantics.py': 'c334890fab9b66321bd6643a49020116babe6911b8dbc433dde9ff63b7cea56b',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_transfers.py': '45176f0d29df994a923a215650f4e5f752fee320a74dad5e38f7f3f9dae377a6',
 'tools/sh-elf-run/byte_curve_caller_withdrawal_capture.py': 'c3005baae784087eb3602f4bb2264a10131b8b978ba920c742d47103bfa3d931',
 'tools/sh-elf-run/harness-byte-curve-caller-withdrawal-paths.c': '51506e0f10f538727cbc453289ebc977bc9f1995f649c1d93bae8a16069940e4',
 'tools/kb/tests/test_byte_curve_caller_withdrawal_adapter_generated.py': '8e3a8a4cc92d9996e880b86c2303afab29e035136ffb0cfa66404fb9f0b12c65'}
PRIOR_WORD_INTERP_CALLER_REFERENCE_SHA256 = 'a8d36384b1d23acf6f4057552914903b8984ca6cb38bcc66d8c425381080a3b6'
PRIOR_WORD_INTERP_CALLER_FUNCTION_SHA256 = '333ffd89d773e1d1212ffa787deb1893d3ac13e07cc528cedd22ad0aa49d61ac'
PRIOR_WORD_INTERP_CALLER_FILES_SHA256 = {'defs/JK08A.word-interp-caller-withdrawal-paths.toml': '923067634016fb3a447d6c31caa92008ef526d75a2a3284851d2f9e0ba1918b0',
 'tools/sh-elf-run/stock_jk08a_word_interp_caller_withdrawal.s': '4704e098245d81eb898040926a020337a0fccdcf5e258151e03323f301070c9a',
 'tools/kb/src/kb/word_interp_caller_withdrawal_contract.py': '069abc5bfc1687155a7c0660c0d3a8834085c14d3225297fae0ca630010508ac',
 'tools/kb/src/kb/word_interp_caller_withdrawal_matrix.py': '9fac1a952481cb66647fa35c7075ff6632ef2b44be24e3cb59d8ddc6dcd84dd0',
 'tools/kb/src/kb/word_interp_caller_withdrawal_semantics.py': 'ed0a00dc33ad6bca12e969f42b01498b089280f9cd0137ef2df1349b74c7e2f8',
 'tools/kb/src/kb/word_interp_caller_withdrawal_transfers.py': 'c8506ca51c86d49a18beace79c0345c1c72f43ab6a03f5ac551f42e4b578aea2',
 'tools/sh-elf-run/word_interp_caller_withdrawal_capture.py': '5388dde6dc64c15473de7a752b08715ca2ceb48be9f1fbbe32098af781086494',
 'tools/sh-elf-run/harness-word-interp-caller-withdrawal-paths.c': 'e4714facffcb59d95bc5316687bd320202a85462cc48d5f2284814794c36a89a',
 'tools/kb/tests/test_word_interp_caller_withdrawal_adapter_generated.py': '0692736a0ea712b8d677858353b3fb034ea46984de1e93a65ed531d0c57e60c7'}
PRIOR_SCALED_DIVISION_REFERENCE_SHA256 = 'ffe4f9c059b62c4d5795909554e244cb51c832fe6ce75c1923905298f037b24b'
PRIOR_SCALED_DIVISION_FUNCTION_SHA256 = 'a607044e4715e0042eb25ae2f5571cd416e23c61fe1e725d174f367851cc7861'
PRIOR_SCALED_DIVISION_FILES_SHA256 = {'defs/JK08A.scaled-division-caller-withdrawal-paths.toml': '292b4325b1729c4383a2acab5cf8325fb95a433ca3e6411b13211f25a9fbf1c9',
 'tools/sh-elf-run/stock_jk08a_scaled_division_caller_withdrawal.s': '0cbc35189655b0044476305907e0cd6917a58f08e43aec92e34205bb91b04984',
 'tools/kb/src/kb/scaled_division_caller_withdrawal_contract.py': 'de4470473b34aa1d424f38f441deb0a28021a88b681bff6d57fa81f22985599d',
 'tools/kb/src/kb/scaled_division_caller_withdrawal_matrix.py': 'e91f630cb5da3242d715b210bbe41a16a40fc225eec67c04b8c1a95d35afa6ae',
 'tools/kb/src/kb/scaled_division_caller_withdrawal_semantics.py': '6fc887cd1c2c046e14c2c7c035d795bcdd6d719184ebf5b98c9cec308df43d8a',
 'tools/kb/src/kb/scaled_division_caller_withdrawal_transfers.py': '151772473ac138f8c20df3f0f50b898a4ff8f95abfd8685331638906094afafb',
 'tools/sh-elf-run/scaled_division_caller_withdrawal_capture.py': '29c3b976858cca121fc07db6a89be54e20369344abdae99a3965ab5371a8d205',
 'tools/sh-elf-run/harness-scaled-division-caller-withdrawal-paths.c': 'fa832d66e65db2257a5a1f13547b8e993cad7b3ad652f2a8c1034225699599a5',
 'tools/kb/tests/test_scaled_division_caller_withdrawal_adapter_generated.py': '5c54d801965ac81d22f2123e5171b8cc67c8aea39bd6c6926eb2b24e01341581'}
PRIOR_CURVE_SCALE_CALLER_REFERENCE_SHA256 = 'f3bab74f6d3a722523f4122db059af361bfb9c8e2a1d2e69ed4fec95741b7fcd'
PRIOR_CURVE_SCALE_CALLER_FUNCTION_SHA256 = 'aeb75a422da13fdd348d6e387129c41ae620975e85ef3d706d13f3dcdb289919'
PRIOR_CURVE_SCALE_CALLER_FILES_SHA256 = {'defs/JK08A.curve-scale-caller-withdrawal-paths.toml': 'ecb266e69212318a2313236dcadedd1310337979200982f4f351a619f27cf6be',
 'tools/sh-elf-run/stock_jk08a_curve_scale_caller_withdrawal.s': 'badbff3005e24f06e5f77635be706ab5e444f23935ff66c3dbd181d74f547682',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_contract.py': '37cb62fba8b9afe76e68315b17b9192601db47b0dea37bf51c8a7b3c6f60b570',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_matrix.py': 'cdd4f3e45562c3fcc5dbd99399d4f1d31b96e9585ebf95096cefbe7a773ac965',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_semantics.py': '5cec258c846ee2318f25793fd2638dd72be5ceb8afaa85c31a3aee8feac33df4',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_transfers.py': '593afd82c89f3a4f63fa9583682d8331c173a5bbdb0ccb7657c79fc57b0e0b7b',
 'tools/sh-elf-run/curve_scale_caller_withdrawal_capture.py': '5c34f2824f3723e45121b81eee378cf6cf04b29ff25e34c69be8149c781f94bf',
 'tools/sh-elf-run/harness-curve-scale-caller-withdrawal-paths.c': '51821b566a42135afc3bcce761355aa767f50be46f6afda7a36a46e568cf30e3',
 'tools/kb/tests/test_curve_scale_caller_withdrawal_adapter_generated.py': '106088e7dfe15fe0b26d521382ec056f831f6dfe4c218caae107a59620882100'}
PRIOR_DERIVATIVE_SCALE_CALLER_REFERENCE_SHA256 = '914e9a87a9dc56c5b4c1f021a0a897585fe2d80a1cf0afa05d2a07697e1d9d16'
PRIOR_DERIVATIVE_SCALE_CALLER_FUNCTION_SHA256 = '8ef6bac0edfc5edae6af02e4ae6b81a7c8f51aa7693b4905b46794b492ee3fda'
PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256 = {'defs/JK08A.derivative-scale-caller-withdrawal-paths.toml': '0be183b2f1d466d864f3a0c7fd4a06348807545e857a130f1b875cd9fe41c03f',
 'tools/sh-elf-run/stock_jk08a_derivative_scale_caller_withdrawal.s': '6ac5a5191d473a14120f4af6b577fe0bb51f6d3cbf037a351066f6dbb1d21b52',
 'tools/kb/src/kb/derivative_scale_caller_withdrawal_contract.py': '4849726f74fe5186938dfb26a6e3777aaa2881bfc6626e79681134142364d274',
 'tools/kb/src/kb/derivative_scale_caller_withdrawal_matrix.py': '1f2c19052fd75f99b8a994e2ae356ab92433b635582457bf4e5465b291397e71',
 'tools/kb/src/kb/derivative_scale_caller_withdrawal_semantics.py': 'c64d8f16d68cc5e5ce183baba2ed713288b551cd4163ca83781a72868fee822e',
 'tools/kb/src/kb/derivative_scale_caller_withdrawal_transfers.py': '3fcf5b0fd6d92f55545b1af28321f5c6591a78ccb5dbc43cf50b6b1e8ffef7f0',
 'tools/sh-elf-run/derivative_scale_caller_withdrawal_capture.py': 'b444e3b54bdc3d672ef02148e216ca0837685915db6dfe482af1750d122c4672',
 'tools/sh-elf-run/harness-derivative-scale-caller-withdrawal-paths.c': '785b72e03cb59699eb6f0c25b5aab3670cdf9e8122abd1f2e3ca2206bb5504f6',
 'tools/kb/tests/test_derivative_scale_caller_withdrawal_adapter_generated.py': '7bf3ea3baefbac230781ae5e610d0f05c61fa4bdec3d7fb75514d698dd7a0db2'}
PRIOR_GUARDED_QUOTIENT_CALLER_REFERENCE_SHA256 = 'd29d3d2fe60d7f732be611327a226dda9adf22544a47f19bf62c0d3964ddec42'
PRIOR_GUARDED_QUOTIENT_CALLER_FUNCTION_SHA256 = '4c59b15576a7f63c7a8a84784d482afc28b597bbab91f45a550595dab40d413e'
PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256 = {'defs/JK08A.guarded-quotient-caller-withdrawal-paths.toml': 'ca54f1c476688f909a7f1057635d96468450a85135ed3812521ef08f0e00fe5e',
 'tools/sh-elf-run/stock_jk08a_guarded_quotient_caller_withdrawal.s': 'b45f5a00d6614a18ff20cdca3b65d2a92cb157d13b4a2f70cd4cfd8a557f7d40',
 'tools/kb/src/kb/guarded_quotient_caller_withdrawal_contract.py': '4673b2dbfa379994a03e02034c89f3200ff77b95dc757b6045df7cca45e62f46',
 'tools/kb/src/kb/guarded_quotient_caller_withdrawal_matrix.py': 'bdb0d5103e0c828e5fef79e9d58a1e156ae77cd2bbadc5bd7a2531d6388d14f6',
 'tools/kb/src/kb/guarded_quotient_caller_withdrawal_semantics.py': '82bb6e1615482e6cf99d71dc7b61a1e30af07800a3780550254b2af125c56840',
 'tools/kb/src/kb/guarded_quotient_caller_withdrawal_transfers.py': '4db9974b7049065dfa22678e7f298d729888171fe2091bbd6582216089b39a8d',
 'tools/sh-elf-run/guarded_quotient_caller_withdrawal_capture.py': '4f334dc1667676978077ad00bd64709239b04ea7e0c341ed1a0f151b2590a619',
 'tools/sh-elf-run/harness-guarded-quotient-caller-withdrawal-paths.c': 'ac4dbecc901f0b5db9da74950bdd387cfc6878c5aa4845bf501a62d04d709c47',
 'tools/kb/tests/test_guarded_quotient_caller_withdrawal_adapter_generated.py': 'b1a11ce05c4edf34a07ef287e2b254a9be0aea93b305390e954cc7cc423fb0a6'}
PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256 = 'ad1db360b715649a6c2ad7e45f5700b3da1b644ac0b0dc200aa12929352cafef'
PRIOR_MIXED_CURVE_CALLER_FUNCTION_SHA256 = '52fb2f977d1bb6e90a01ec143fd1ed9f63da84b5675f0e1eafca47fd1804e3f5'
PRIOR_MIXED_CURVE_CALLER_FILES_SHA256 = {'defs/JK08A.mixed-curve-caller-withdrawal-paths.toml': '981b0db82094bd12e0d7693689d3b92dd76cf7a3014aa1de4b2046ffa01966d8',
 'tools/sh-elf-run/stock_jk08a_mixed_curve_caller_withdrawal.s': '396119d014a46cef95f4dee9dd0d1e2212138deefa6fc71d1fed66dbf5940a92',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_contract.py': '92da7ea75343a44fe132ec4dee276df7e6e8f010a6aa25d3c741b279c229bd82',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_matrix.py': 'f864ed45f70c63be6ad420c5dcdd8471bb56c38e17eb6215d8741780d827e19d',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_semantics.py': 'b124ded8e0c8144f6612f6df9e706e68a7e784cae12d87215a5f730acef7bdca',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_transfers.py': '03f7b96e668588ec61d9615bbd19229d43f19b7d145e4f0e5a610b580c1884cf',
 'tools/sh-elf-run/mixed_curve_caller_withdrawal_capture.py': '09af5cf9834060f992ae8d47aaeaa005e7536143d8109c18614977b3b5a13b73',
 'tools/sh-elf-run/harness-mixed-curve-caller-withdrawal-paths.c': '48d6e0c618e0d26328133d69d66fed9a69fe9294301754f4474c983c7adc9e19',
 'tools/kb/tests/test_mixed_curve_caller_withdrawal_adapter_generated.py': '6b6ddc6999d8502e5adcffc604127114adcd92d7302bb4f5b75e9bf575c4e4c7'}
PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256 = '8bb543e1959e4a3654aaa8173c783e1b395b87cb0ec924da80bbfac8f13a6109'
PRIOR_TIMING_REMAINDER_CALLER_FUNCTION_SHA256 = 'caad79cd28cc182efdec4523b65ad34bddcef3d7756d42b5e710aeb2a7821b01'
PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256 = {'defs/JK08A.timing-remainder-caller-withdrawal-paths.toml': '8864e9a79f9ba3248e4c18741ef3638765d45e70c447531687ed9e5327ecd2cb',
 'tools/sh-elf-run/stock_jk08a_timing_remainder_caller_withdrawal.s': 'bdcafe90954e5572909c4977c9c3ed6189c27f5ee256a47216aa4d1580b36ee4',
 'tools/kb/src/kb/timing_remainder_caller_withdrawal_contract.py': '7721dbf8a7f210de80ad7026cee096ebd57267c64fdf31aa5dc064125043a28e',
 'tools/kb/src/kb/timing_remainder_caller_withdrawal_matrix.py': 'd3346e11efc0ef00d59967e2e9c6f83d6187ac806e7bf31993922f608a5dc8df',
 'tools/kb/src/kb/timing_remainder_caller_withdrawal_semantics.py': '4dd5df277e479d88d8017d21ea29d1b60c833051758732d263ef6358d3c1a4dd',
 'tools/kb/src/kb/timing_remainder_caller_withdrawal_transfers.py': '4bd2a49f85b5c82a2ce245e62950b2d4f7f7d8acfd5f37e343b0649ab646e25c',
 'tools/sh-elf-run/timing_remainder_caller_withdrawal_capture.py': '2d99d14e04a65ce5c0020b2ed4e63e50de3c71ccea2284911821d9bfdb3bd179',
 'tools/sh-elf-run/harness-timing-remainder-caller-withdrawal-paths.c': 'bd2168d833987192fb2f9e9ef5016e2c173e8883f29b5347e24bfb36cb7721b8',
 'tools/kb/tests/test_timing_remainder_caller_withdrawal_adapter_generated.py': '705a0f06ab4f5e4a4e0e830d6acdcb053a8d1d1c9ec2c91d933032d5338c4f23'}
PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256 = 'd966d4b375342f7c6bf48fb1b54b5044ecf429d06a1cefd9bb78e473024b2503'
PRIOR_STATE_RATIO_CALLER_FUNCTION_SHA256 = 'd8c72011f60c2a5e602fc5d9c2414b641f04e5fed5d025bc3c195c16e76e547c'
PRIOR_STATE_RATIO_CALLER_FILES_SHA256 = {'defs/JK08A.state-ratio-caller-withdrawal-paths.toml': '5a38d08e07bb5f963e16c33540740f58d0f0a520c40ee88a22ab7d3d5396010f',
 'tools/sh-elf-run/stock_jk08a_state_ratio_caller_withdrawal.s': '3c718a799229ba47a9b1173971910d7ab1c0f62b91b1c288f742879945db0bba',
 'tools/kb/src/kb/state_ratio_caller_withdrawal_contract.py': 'd7a1c9161248739f4d7d991e63f3eb72b0fb9b597272b6b742512bc66f820c27',
 'tools/kb/src/kb/state_ratio_caller_withdrawal_matrix.py': 'b1e8833c7d18193a9ea5d7d3659a0c5d246f9e653a817242eb7bdac77f42da56',
 'tools/kb/src/kb/state_ratio_caller_withdrawal_semantics.py': 'c81144ca2626c027d36e0fd5b8c8d4e16122ae6d91ef8c75cd7ae1e0a6964da4',
 'tools/kb/src/kb/state_ratio_caller_withdrawal_transfers.py': '2d503593648257e50a1b0d73a38a0019178eac32c3d4e21e8f368b0820e4ca64',
 'tools/sh-elf-run/state_ratio_caller_withdrawal_capture.py': '010e437f41a1774c39bb31bac405c74219e26fbcde303526acab2d18e6102f9b',
 'tools/sh-elf-run/harness-state-ratio-caller-withdrawal-paths.c': 'd753c8981a6d5a3a82424db7f9f456a318c03ef84f48b76ee89085a10f785f84',
 'tools/kb/tests/test_state_ratio_caller_withdrawal_adapter_generated.py': '029017b2c52ccbfbf2d2f61c36e370eefdfa54f1817ea089bdf6d7ab4f74574a'}
PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256 = 'f5a92ae6b9da81d69da71a35d0c19ae70f75cfa6725fb21934635d53871ef91d'
PRIOR_DFCO_STATE_CALLER_FUNCTION_SHA256 = 'efe59944e20e9de38a6f54004076589c7b5dededa30437cdad60656b7acaab8a'
PRIOR_DFCO_STATE_CALLER_FILES_SHA256 = {'defs/JK08A.dfco-state-caller-withdrawal-paths.toml': '58ad8353f15bae7291fa1e85e0a8d5772fb3fd75e1db8707c07bc85b23981fd0',
 'tools/sh-elf-run/stock_jk08a_dfco_state_caller_withdrawal.s': 'c2edd846c2ed58be6b982d31a5aaf45c642ba17107ac1d125eaae2189aa22c22',
 'tools/kb/src/kb/dfco_state_caller_withdrawal_contract.py': 'bb79b3b5454c832dcd3c9ce315e1f1281a5d7b3b00f0952ce1212b4aed73d7d8',
 'tools/kb/src/kb/dfco_state_caller_withdrawal_matrix.py': '4e92f6cb0dc21249b103f01f98b8269a197b3dbaa31addefe4c99094db89805b',
 'tools/kb/src/kb/dfco_state_caller_withdrawal_semantics.py': 'ef74ffe8bbfdea61550533ba3e568f085c30d361f397746b871976a533f53876',
 'tools/kb/src/kb/dfco_state_caller_withdrawal_transfers.py': 'd86817700023bdb5db6b17c036e5fc153be750dad6b582ebf92161ca6b92c075',
 'tools/sh-elf-run/dfco_state_caller_withdrawal_capture.py': 'a12a121859f5d9eedfb96f5f6ba8263a098197b4dcddf8580e823e9fbd2ff4fd',
 'tools/sh-elf-run/harness-dfco-state-caller-withdrawal-paths.c': '39dc94def813c9fc1a94b5d17f029f33faa4f72e6e6d04b0a2584dce79d94662',
 'tools/kb/tests/test_dfco_state_caller_withdrawal_adapter_generated.py': '0773fd13664a5b09686aafb96943ab2cb531b06312a83f66ed56056e26f827b1'}
FUNCTION_POSTIMAGE_IDENTITIES = (('classy-seahorse/fn',
  510202,
  'kb/fn/classy-seahorse.toml',
  'f96653b29b6fb8357cdfece6931853bd98ac231c167db36aeaa60920893bd5b9',
  '80639e0d912d42dadf84e9ce2f25ab6a109efce3ed16a0c1fdc25b66968c6af2',
  '[{"dependency":[{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"defiant-tiger/ram","type":"reader"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"careful-coua/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"hallowed-malkoha/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"jumping-carp/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"neon-seagull/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"rampant-lobster/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"realistic-capybara/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":415,"registry":"funcs"}]',
  '[{"dependency":[{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"defiant-tiger/ram","type":"reader"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"careful-coua/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"jumping-carp/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"neon-seagull/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"rampant-lobster/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"realistic-capybara/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8],"notes":[0],"order":415,"registry":"funcs"}]'),
 ('persimmon-giraffe/fn',
  510376,
  'kb/fn/persimmon-giraffe.toml',
  '00c1d87ce8ca7b351aad8c35da9da1679ec9fe8060d0c96807c718e75d858bdf',
  '5b5c9acb1a6fb261a94ac6eaf1bb08986fe054e93d3e005ee51919bc6076f6ae',
  '[{"dependency":[{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"defiant-tiger/ram","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"hallowed-malkoha/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"jumping-carp/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"neon-seagull/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"rampant-lobster/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"realistic-capybara/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":416,"registry":"funcs"}]',
  '[{"dependency":[{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"defiant-tiger/ram","type":"reader"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"jumping-carp/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":416,"registry":"funcs"}]'),
 ('charming-warthog/fn',
  309832,
  'kb/fn/charming-warthog.toml',
  'e93956baaf7fea895c081f4e1d4015dde485ab1da09e971850dd871c5b9771e9',
  '81e54266e339e8373fd4063ea92197b26297ed33dc3d4d3664a2122adf7ee051',
  '[{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"clever-woodlouse/fn","type":"depends"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"fat-crayfish/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"witty-panther/tbl","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"aboriginal-dog/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"finicky-shellfish/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"hallowed-pelican/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"purple-chihuahua/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":313,"registry":"funcs"}]',
  '[{"dependency":[{"end":"owner","link_role":"consumer","relies":"structure","role":"consumer","supports":"identity","to":"clever-woodlouse/fn","type":"depends"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"fat-crayfish/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"witty-panther/tbl","type":"reader"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"aboriginal-dog/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"finicky-shellfish/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"hallowed-pelican/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7],"notes":[0],"order":313,"registry":"funcs"}]'),
 ('cherubic-salamander/fn',
  287966,
  'kb/fn/cherubic-salamander.toml',
  '71929d38a641cfc3a71e837a3c5ee7ad3bad2d9aec1eee82552f6f628b61ead1',
  '3c21af3c1695f8541f5ee82f3893f8be99caf700da96970ab118f398c14a0dc4',
  '[{"dependency":[{"end":"owner","link_role":"consumer","relies":"level","role":"consumer","supports":"identity","to":"quirky-silkworm/fn","type":"depends"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"smiling-bustard/tbl","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"saffron-manul/ram","type":"reader"},{"end":"owner","relies":"structure","role":"threshold","supports":"identity","to":"electric-gopher/ram","type":"threshold"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"rigorous-lizard/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"urban-ibex/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3],"notes":[0],"order":315,"registry":"funcs"}]',
  '[{"dependency":[{"end":"owner","link_role":"consumer","relies":"level","role":"consumer","supports":"identity","to":"quirky-silkworm/fn","type":"depends"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"smiling-bustard/tbl","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"saffron-manul/ram","type":"reader"},{"end":"owner","relies":"structure","role":"threshold","supports":"identity","to":"electric-gopher/ram","type":"threshold"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"rigorous-lizard/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3],"notes":[0],"order":315,"registry":"funcs"}]'),
 ('uptight-duck/fn',
 751694,
 'kb/fn/uptight-duck.toml',
 'c869d66b1a0495c487e8891a60e23c09439104abeea09203f1da1356dbb678e4',
 '7a971abdaedff46981c533e37ce360aa302a826bc0df0891e30707c25b2eab28',
 '[{"dependency":[{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"blond-panther/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"magic-kingfisher/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"prehistoric-boa/tbl","type":"reader"},{"end":"owner","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"complex-firefly/tbl","type":"depends"},{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"rpm/ram","type":"reader"},{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"ruddy-anaconda/ram","type":"reader"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"curvy-mandrill/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"mauve-myna/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"peach-anteater/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],"notes":[0],"order":480,"registry":"funcs"}]',
 '[{"dependency":[{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"blond-panther/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"magic-kingfisher/tbl","type":"reader"},{"end":"to","relies":"structure","role":"from_map","supports":"identity","to":"prehistoric-boa/tbl","type":"reader"},{"end":"owner","link_role":"indexed_by","relies":"structure","role":"indexed_by","supports":"identity","to":"complex-firefly/tbl","type":"depends"},{"end":"to","link_role":"indexed_by","relies":"level","role":"indexed_by","supports":"identity","to":"rpm/ram","type":"reader"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"curvy-mandrill/ram","type":"writer"},{"end":"to","relies":"structure","role":"writes","supports":"identity","to":"mauve-myna/ram","type":"writer"},{"end":"to","relies":"level","role":"writes","supports":"identity","to":"peach-anteater/ram","type":"writer"}],"fields":["role","semantics","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],"notes":[0],"order":480,"registry":"funcs"}]'))
FUNCTION_POSTIMAGE_CLAIMS = (('573e631e56ccae93bdac53c1906dadcc90aeb13a9fef5f5abe97af5d7fa3f437', 'rampant-lobster/ram', 510376),
 ('177290ea6eaeccff871ba8e2f041ef206f867d937656ff13aa6db177a9d94298', 'realistic-capybara/ram', 510376),
 ('f5ad4f5cd86f01b4ce9c961c46d182bd1a5ca987660d96cbe7df5f127d23cd36', 'neon-seagull/ram', 510376),
 ('ace066de89ca0e146133354756c38ccda95830904176750f776020f78d758261', 'hallowed-malkoha/ram', 510202),
 ('e05ca8c55888e89a68795f8e3d2d7e22173743a4a5c13ad589ebab1854b4c532', 'hallowed-malkoha/ram', 510376),
 ('47c4932e2c5dbceeaa8d0d301089b790354738e4ef80dfa93ebb005beb915442', 'purple-chihuahua/ram', 309832),
 ('1dacd2a5176d35d9dc687370413cd3502b32f21417e16988f0948a9587b9d970', 'urban-ibex/ram', 287966),
 ('59ee18e4be7bbc935c2e08f6fcf90dc42c21494b0ce73ff39550cc184342305f', 'ruddy-anaconda/ram', 751694))
PRIOR_PAIRED_INHIBIT_WRITER_REFERENCE_SHA256 = '402701d71dbfb418cbee703b7b25173e38e988fc5a59937dbea631757123a506'
PRIOR_PAIRED_INHIBIT_WRITER_FUNCTION_SHA256 = 'e21822d594e8f807e45deeea6f8e8c87a2af6a9c328cd450e7f10f51c79468d5'
PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256 = {'defs/JK08A.paired-inhibit-writer-withdrawal-paths.toml': 'f37e081ed11c77ec4022fce89be2eb1d3f690d6f8aab79e1f366a430d8ed2b49',
 'tools/sh-elf-run/stock_jk08a_paired_inhibit_writer_withdrawal.s': '53044d90056325b33154ec297377c17e4537809b8920812935e3a21a83328869',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_contract.py': 'c5b1f72c0c10a1f2516418459b4bc1fa186e1eb7ef4dc34b49fa347bdf734af1',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_matrix.py': 'ce82ffe2b16a9e901ab949acdcb570d9b68684bc225720fdca4431fdc54ceb88',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_semantics.py': '64786a40cc6a314ee77330035f3b3560e0cc8c269b599855c49ef56913215aeb',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_transfers.py': '263af512962490156926efb461bfc4d8f6556f2410a5c7af1f638446a2a11ad6',
 'tools/sh-elf-run/paired_inhibit_writer_withdrawal_capture.py': '13c6a8443db26aa6a31b32fdeba816e88a9e5ec4dc0d2cb3d828ff39fd935a32',
 'tools/sh-elf-run/harness-paired-inhibit-writer-withdrawal-paths.c': '252af6204971e188e1ab28236312a723f04c5c2eabf6ade2aaef08a66de8219e',
 'tools/kb/tests/test_paired_inhibit_writer_withdrawal_adapter_generated.py': '152455e3b9245ccc87025c889fb1d28f2508de4de3a3a7693ac0d51872e192e0'}
PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256 = '138d3f824235ddbb107d4a7228d832df73b45502498664bc42d4a7a0cd4eeaf9'
PRIOR_THRESHOLD_WINDOW_READER_FUNCTION_SHA256 = 'f27d85ed32cff5ed5897beeb3aec88c5d0d8e4ab66d9c78b737ba0544058f43c'
PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256 = {'defs/JK08A.threshold-window-reader-withdrawal-paths.toml': 'b10d66301522bdda0eb3ce6a688b8b5b7c2ef577ec5c4863a4c3d56676da35ce',
 'tools/sh-elf-run/stock_jk08a_threshold_window_reader_withdrawal.s': 'c86bf9dcb5e677277d1080f3782356c6bd05c00e61627aca5941bc335ab4424d',
 'tools/kb/src/kb/threshold_window_reader_withdrawal_contract.py': 'fe034fa349996f50ce4ac7de9015eb08622bf91930734a6964f50359875fa0a9',
 'tools/kb/src/kb/threshold_window_reader_withdrawal_matrix.py': '449956a342997292f7029a394da43f3d55152bdd1dc4bc361f881f25f1ae4a1d',
 'tools/kb/src/kb/threshold_window_reader_withdrawal_semantics.py': '12e6a68bfc0c97f207a020206710c178b09987749d5f6a9ca46e4ffdf854d9e7',
 'tools/kb/src/kb/threshold_window_reader_withdrawal_transfers.py': '8730171f4732a1a4c5f01bdb54cc9c0671e96b80975cefdee060d5f12ccbcdc6',
 'tools/sh-elf-run/threshold_window_reader_withdrawal_capture.py': 'f54ce639ab5e72c96941887d087866c6f604bd065a50ec2665af3c1b0b990b00',
 'tools/sh-elf-run/harness-threshold-window-reader-withdrawal-paths.c': 'f671fc911bbdc6e4b1c537f79f66e072b9cd2abf42d40c137acc3159cdb953a9',
 'tools/kb/tests/test_threshold_window_reader_withdrawal_adapter_generated.py': 'ed36979c54fdca02af1f8beb650f07a3e4e959cf7bd9c2f205a0a97e060cd66f'}
PRIOR_AUX_RATE_CALLER_REFERENCE_SHA256 = '6a021eeff06b28350138a417fcbd662163cd0934cf3d8dcf9b62a72158803605'
PRIOR_AUX_RATE_CALLER_FUNCTION_SHA256 = '693fdfe341417ff2918a59d0e011910356e1d147c59555acbdf1a77ab336055e'
PRIOR_AUX_RATE_CALLER_FILES_SHA256 = {'defs/JK08A.aux-rate-caller-withdrawal-paths.toml': 'cb79821b8ca0bd37e7e1f2c2c337e0531d7e468572350259bcc563823a0fd6b0',
 'tools/sh-elf-run/stock_jk08a_aux_rate_caller_withdrawal.s': 'b4b67afecb46a4d9d94409669a9dbbf2305a7c65d7e0cb8e09ec40588a93f831',
 'tools/kb/src/kb/aux_rate_caller_withdrawal_contract.py': 'd02e956dd54256ba5bf528a616abf54680ce7285ec04f90289cb01cea62167e0',
 'tools/kb/src/kb/aux_rate_caller_withdrawal_matrix.py': '294cbc8e2be61363f3468dc97fe0874b07c76fab1bfe17818201afdbe9425c6d',
 'tools/kb/src/kb/aux_rate_caller_withdrawal_semantics.py': 'ca6fb30d91b3428dae7f78cf82079caac66d6ebfa1fdd1df4b2b92861152e840',
 'tools/kb/src/kb/aux_rate_caller_withdrawal_transfers.py': '43e63b5c3b68106190ab9e2f5dd3eb112e32849a3fc0c1c30c9df354f60f9ada',
 'tools/sh-elf-run/aux_rate_caller_withdrawal_capture.py': '02b48c5c71a75a080e7d931564994f9c5f5734a84f07ed0f9b484c71f5795ede',
 'tools/sh-elf-run/harness-aux-rate-caller-withdrawal-paths.c': 'e280e5aaa5e0db27f4c111db17589558398fbe906d8fc56da6ad3518662b403d',
 'tools/kb/tests/test_aux_rate_caller_withdrawal_adapter_generated.py': '326fad44f23656ec0fba5dc39ec2647d795d6706d1e26fa2daf694a68b47833e'}
PAIRED_CURVE_NORMALIZATION_CLAIMS = (('000655b4-00010b8e-withdraw',
  'lyrical-dragon/tbl',
  415156,
  '0857c64cec33d674a469dc8d6cb8fc6360314e56e1e4f09cbbc44d5c60c2775e',
  '{"evidence":[],"layout":"7mfk","offset":null,"owner":"lyrical-dragon/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/lyrical-dragon.toml"],"stated":["7mfk"],"to":"vigorous-saluki/fn","type":"reader"}'),
 ('00065b08-00010b8e-withdraw',
  'lyrical-dragon/tbl',
  416520,
  '11bcb9488d622e9f157f3d5b3a553cea1bc9f439607efa759dc9d6d0c249433e',
  '{"evidence":[],"layout":"7mfk","offset":null,"owner":"lyrical-dragon/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/lyrical-dragon.toml"],"stated":["7mfk"],"to":"silky-vulture/fn","type":"reader"}'))
PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256 = '62dd066599653b5705ec80319bf6e7fd38b1a65095caccf2ab5c1c37373cfa42'
PRIOR_PAIRED_CURVE_NORMALIZATION_FUNCTION_SHA256 = '249f3fcd1118a1ea06d976ce88661584ec65fc0ca8d5415bc39aa5b60c8daa6e'
PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256 = {'defs/JK08A.paired-curve-normalization-withdrawal-paths.toml': '1f0651d867d529f8341aa5048d87fa100c3d964a8eaf3675f11b46bc806d151e',
 'tools/sh-elf-run/stock_jk08a_paired_curve_normalization_withdrawal.s': 'dc8513ab46df5788997426d139f2a7d347d43e64d3c72d7c0b23f7e787cd27d1',
 'tools/kb/src/kb/paired_curve_normalization_withdrawal_contract.py': 'db7826289052a7cdae6469e4fb037d44d33ae196f6af6600433a65dc593999b4',
 'tools/kb/src/kb/paired_curve_normalization_withdrawal_matrix.py': 'a05b2760ae0710e5a61d1038f34f640c0c42d4c1cf92ed8ae843ac5dc35afe7f',
 'tools/kb/src/kb/paired_curve_normalization_withdrawal_semantics.py': 'b62c632792435cca2b20b1ac3705485ce88a7354607e1212061f58703855961c',
 'tools/kb/src/kb/paired_curve_normalization_withdrawal_transfers.py': 'e0a3ce478db99f1c41d5a3ead96ae9c44a79d4f4d76c72ca5d49240b3562c5a2',
 'tools/sh-elf-run/paired_curve_normalization_withdrawal_capture.py': 'd20f448572eb374776a7c978de5c007848b1ef2d950afe09aeb03048ee59aa51',
 'tools/sh-elf-run/harness-paired-curve-normalization-withdrawal-paths.c': 'b9f9036b56472653fd6182bb6a7b8c5cb8400f69e13d5c13b7d770f8eb8de486',
 'tools/kb/tests/test_paired_curve_normalization_withdrawal_adapter_generated.py': '0ffb4dfd07e2409bdcb1990b296831ca419bc18de3e75ea6373e77fe1804b7ae'}
STATE_SURFACE_CLAIMS = (('000647e8-00012b52-withdraw',
  'quick-basilisk/tbl',
  411624,
  '0057fd6cb20fac880f590fbd89fccd80768695872bed9c47fa438877314cec2b',
  '{"evidence":[],"layout":"7mfk","offset":null,"owner":"quick-basilisk/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/quick-basilisk.toml"],"stated":["7mfk"],"to":"spotted-zebra/fn","type":"reader"}'),
 ('000647e8-00012b5a-withdraw',
  'mindful-pogona/tbl',
  411624,
  '55e5ca11aa978e3f61c1f44e450f5acc3fce0638cb0f1fdc434a77b0794c6eef',
  '{"evidence":[],"layout":"7mfk","offset":null,"owner":"mindful-pogona/tbl","props":{"layouts":["7mfk"],"relies":"structure","supports":"identity"},"roles":[],"slot":null,"sources":["kb/tbl/mindful-pogona.toml"],"stated":["7mfk"],"to":"spotted-zebra/fn","type":"reader"}'))
PRIOR_BYTE_RATIO_PRODUCER_REFERENCE_SHA256 = '4820a339eb6f77701fcdcc952b2604c7e6973f193bd28efadd594b674cdc7d76'
PRIOR_BYTE_RATIO_PRODUCER_FUNCTION_SHA256 = '74bd1ecab2ef49bfcca4454784323f0c743f63a024265095c59abb05c8bdbb3f'
PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256 = {'defs/JK08A.byte-ratio-producer-withdrawal-paths.toml': 'ba8d2b3648e3d9616a7a6d9c8e908df639d8ce4414b5f81d117ee1f8dc5b6e49',
 'tools/sh-elf-run/stock_jk08a_byte_ratio_producer_withdrawal.s': '5c6b74f8b4f4ea8308a76669fb24b993e0f96fc5209326badc3fbf14fbc88bb7',
 'tools/kb/src/kb/byte_ratio_producer_withdrawal_contract.py': 'fd600811a36de27bd093868c60faef219cc26a7ed3a1104981a657a9cecd0a05',
 'tools/kb/src/kb/byte_ratio_producer_withdrawal_matrix.py': '854d83f05814e9e6d2f7a91d49b91b78beb25ad081aeee9a3710a40a19fa65b6',
 'tools/kb/src/kb/byte_ratio_producer_withdrawal_semantics.py': '14e1c869143f7b4ab8fdcf35a23cd8be9ddde8c1dab499834c70954916200140',
 'tools/kb/src/kb/byte_ratio_producer_withdrawal_transfers.py': '36aa83913cd2dda776a1416ac927983d781ffb3d1c3df83007c3ed4490264d65',
 'tools/sh-elf-run/byte_ratio_producer_withdrawal_capture.py': 'a98dce6d3e1fc476de08ea1a15105d7e6a56d693d847d3e4ea39fb1b5a9d8095',
 'tools/sh-elf-run/harness-byte-ratio-producer-withdrawal-paths.c': 'ad17456485dd3f6a38b874e59196b8cde133ebcd7bf5a659e1ce3e50ca883102',
 'tools/kb/tests/test_byte_ratio_producer_withdrawal_adapter_generated.py': '86adbed97602257348ffeb85b0868a280afef4070aada5e0f494ccb373dc49c7'}
PRIOR_STATE_SURFACE_CALLER_REFERENCE_SHA256 = 'e7d591f844e8318122d4e077995c388f7966fac7e69a075552df339a2ce37d14'
PRIOR_STATE_SURFACE_CALLER_FUNCTION_SHA256 = '2b433f5202deb6e2c8dbd9f31d1e72e91468a597ec68acae50113c1efaaeba93'
PRIOR_STATE_SURFACE_CALLER_FILES_SHA256 = {'defs/JK08A.state-surface-caller-withdrawal-paths.toml': 'b7e416b9aaa4047b29f6d0cdacee18e7afadb272d511913f6a8c7379ab8d696c',
 'tools/sh-elf-run/stock_jk08a_state_surface_caller_withdrawal.s': '9e43b209d63cd94f647bb9c16dc56f8cbbb86b0370219d4be9831825d6221ddf',
 'tools/kb/src/kb/state_surface_caller_withdrawal_contract.py': 'd80a7c3306f39f2cf9853b424a5840e3d3325e0ae3c9bbdc0a713f1a5e648039',
 'tools/kb/src/kb/state_surface_caller_withdrawal_matrix.py': '25445bada6c97551ba99a9b85d3ca75d8d957ad478eda176a5cad38c5afeea67',
 'tools/kb/src/kb/state_surface_caller_withdrawal_semantics.py': '79bc61ff3cbdb1b9a182580dd19ee5c9a9e602bbc36d785efb3feebc75392e89',
 'tools/kb/src/kb/state_surface_caller_withdrawal_transfers.py': 'e10eef4c0aee4d9917ee1e1207e9d71eaa8e53e7150bd59a40e619cef0696c72',
 'tools/sh-elf-run/state_surface_caller_withdrawal_capture.py': '20dbb1f5e1f3348542a2e4b7e3110b68ba804b73c6b8cdd5ec122b610b506b79',
 'tools/sh-elf-run/harness-state-surface-caller-withdrawal-paths.c': '8a36c7668adf1d79516ea20913c0295f23edb990b63c08bdfc3c0201a27cb5c9',
 'tools/kb/tests/test_state_surface_caller_withdrawal_adapter_generated.py': 'fe49e5e3a37d40cc651f83ea15e023f977cfa5aa100dc1ed8bd91f6372f5bf06'}
PRIOR_BYTE_FACTOR_CALLER_REFERENCE_SHA256 = 'd4e6cb269ad186a648413f0d28abd881d66c661ce4ab90b308e374ec68c87b88'
PRIOR_BYTE_FACTOR_CALLER_FUNCTION_SHA256 = '0b1c2b1aaedc8632843657c0860a2acd739b27e5e3e6f0e95208fd6ca829a82e'
PRIOR_BYTE_FACTOR_CALLER_FILES_SHA256 = {'defs/JK08A.byte-factor-caller-withdrawal-paths.toml': '1e8b123d8d052888eca4ba10227f2550f4dac8800aedb2a531bcd867105a21d5',
 'tools/sh-elf-run/stock_jk08a_byte_factor_caller_withdrawal.s': '9227b8aa9b04bda24c6637e024a77f9ebbe0caf2b71537df52a45c574d38028e',
 'tools/kb/src/kb/byte_factor_caller_withdrawal_contract.py': '93d25d6f7f77aa4d810848ec2ec2db8b4db789ed8ef89c7446480101b9e1594a',
 'tools/kb/src/kb/byte_factor_caller_withdrawal_matrix.py': 'a90d7a6dba0fc9cf3869f1a10766dbb876b4449d841b78d29ac1f31e9038b866',
 'tools/kb/src/kb/byte_factor_caller_withdrawal_semantics.py': 'fe2a8106e301a184b55e99543613407b93896ff04045565b725f9dc5bb331a3e',
 'tools/kb/src/kb/byte_factor_caller_withdrawal_transfers.py': '69922fe3049f3cc5068da1621b2445cbc7ff0b71aa96c812b643ad728b38eed1',
 'tools/sh-elf-run/byte_factor_caller_withdrawal_capture.py': '065bf6f3cd7e44aa82c18899a828e189dd40052a79f6d011ca41c724343f6f6f',
 'tools/sh-elf-run/harness-byte-factor-caller-withdrawal-paths.c': '092c1a75d6980c9866f8b427fe35b153fe4886fd676a94b46826ea42c126aa3a',
 'tools/kb/tests/test_byte_factor_caller_withdrawal_adapter_generated.py': '2d87f294e0b25f1c85057588f638800d51834b13f8e24eb566689392be693e8f'}
FLAGS = ('native_identity_admission', 'native_geometry_inference', 'scale_admission', 'units_admission', 'natural_caller_reachability', 'hardware_qualification', 'replacement_relation', 'native_publication')


def native_type(row,field):
    value=row['declared_'+field]
    return None if value=='unset' else value


def symbol_key(row):
    return SymbolKey('7mfk',row['owner'].rsplit('/',1)[1],row['address'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference','function',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scalar-ram-leaf-withdrawals'
            or value['layout']!='7mfk'
            or value['image_sha256']!='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[name] is not False for name in FLAGS) or len(value['reference'])!=127):
        raise ValueError('the scalar RAM leaf withdrawal changes its exact absent-claim admission boundary')
    keys={'id','owner','address','function','component','direction','source','original_claim_sha256',
        'original_claim_json','original_native_sha256','original_native_json','original_ledger_json',
        'original_symbol_evidence_json','declared_width','declared_signed','proposed_native_sha256',
        'proposed_native_json','proposed_ledger_json'}
    originals,proposed={},{}
    for row,pinned in zip(value['reference'],IDENTITIES):
        identity=tuple(tuple() if key=='sites' else row.get(key) for key in (
            'id','address','owner','function','sites','direction','component','width_bytes','declared_width',
            'declared_signed','original_claim_sha256','proposed_claim_sha256','original_native_sha256','proposed_native_sha256'))
        if set(row)!=keys or not test_contract.exact(identity,pinned):
            raise ValueError('the scalar RAM leaf withdrawal changes an exact original, owner, natural entry or type')
        old=json.loads(row['original_claim_json'])
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        if (digest(old)!=row['original_claim_sha256'] or digest(before)!=row['original_native_sha256']
                or digest(after)!=row['proposed_native_sha256'] or old['owner']!=row['owner']
                or old['type']!=ORIGINAL_LINK_TYPES.get(row['id'],'reader') or old['layout']!='7mfk' or old['evidence']!=[]
                or old['sources']!=[row['source']] or old['slot'] is not None or old['offset'] is not None
                or not test_contract.exact(old['roles'],list(NATIVE_LINK_ROLES.get(row['id'],()))) or row['direction']!='withdrawal'):
            raise ValueError('the scalar RAM leaf withdrawal changes complete original or native content')
        for held,document in ((originals,before),(proposed,after)):
            if row['owner'] in held and not test_contract.exact(document,held[row['owner']]):
                raise ValueError('the grouped scalar RAM leaf withdrawal substitutes a shared owner image')
            held[row['owner']]=document
        symbols=[item for item in before['symbol'] if item['layout']=='7mfk' and int(item['address'],16)==row['address']]
        if (len(symbols)!=1 or not test_contract.exact(symbols[0].get('evidence',[]),json.loads(row['original_symbol_evidence_json']))
                or not test_contract.exact(before.get('ledger'),json.loads(row['original_ledger_json']))
                or not test_contract.exact(after.get('ledger'),json.loads(row['proposed_ledger_json']))
                or not test_contract.exact((symbols[0].get('width',before.get('width')),
                    symbols[0].get('signed',before.get('signed'))),(native_type(row,'width'),native_type(row,'signed')))):
            raise ValueError('the scalar RAM leaf withdrawal changes retained native symbol evidence, type or ledger')
    expected=deepcopy(originals)
    for row in value['reference']:
        old=json.loads(row['original_claim_json']);document=expected[row['owner']]
        matches=[index for index,link in enumerate(document.get('link',())) if link['type']==old['type'] and link['to']==old['to']]
        if len(matches)!=1:raise ValueError('the scalar RAM leaf withdrawal lacks one exact original native relation')
        removed=document['link'].pop(matches[0])
        props={name:item for name,item in removed.items() if name not in ('type','to','evidence','role')}
        native_roles=[] if 'role' not in removed else [removed['role']]
        if (not test_contract.exact(props,old['props']) or removed.get('evidence',[])!=[]
                or not test_contract.exact(native_roles,list(NATIVE_LINK_ROLES.get(row['id'],())))):
            raise ValueError('the scalar RAM leaf withdrawal substitutes original native relation content')
        for marker in document.get('ledger',()):
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency'] if not selector(row,row['owner'],item)]
    for document in expected.values():
        if not document.get('link'):document.pop('link',None)
        for marker in document.get('ledger',()):
            if not marker.get('dependency'):marker.pop('dependency',None)
    if len(expected)!=97 or not test_contract.exact(expected,proposed):
        raise ValueError('the scalar RAM leaf withdrawal changes another fact, link order, evidence, ledger identity, field or note')
    if len(value['function'])!=len(RETAINED_FUNCTIONS):
        raise ValueError('the scalar RAM leaf withdrawal omits a complete retained function input')
    for row,pinned in zip(value['function'],RETAINED_FUNCTIONS):
        if (set(row)!=({'owner','function','source','original_native_json','original_native_sha256'}|({'proposed_native_json','proposed_native_sha256','original_ledger_json','proposed_ledger_json'} if row['owner'] in {pin[0] for pin in FUNCTION_POSTIMAGE_IDENTITIES} else set()))
                or not test_contract.exact(tuple(row[name] for name in ('owner','function','source','original_native_sha256')),pinned)
                or digest(json.loads(row['original_native_json']))!=row['original_native_sha256']):
            raise ValueError('the scalar RAM leaf withdrawal changes a full retained function identity or TEST context')
    require_function_postimages(value)
    require_prior_boundary(root,value)
    require_prior_joint_boundary(root,value)
    require_prior_gated_boundary(root,value)
    require_prior_rpm_ram_boundary(root,value)
    require_prior_overflow_boundary(root,value)
    require_prior_word_boundary(root,value)
    require_prior_rpm_state_boundary(root,value)
    require_prior_indexed_word_boundary(root,value)
    require_prior_division_caller_boundary(root,value)
    require_prior_byte_curve_caller_boundary(root,value)
    require_prior_word_interp_caller_boundary(root,value)
    require_prior_scaled_division_boundary(root,value)
    require_prior_curve_scale_caller_boundary(root,value)
    require_prior_derivative_scale_caller_boundary(root,value)
    require_prior_guarded_quotient_caller_boundary(root,value)
    require_prior_mixed_curve_caller_boundary(root,value)
    require_prior_timing_remainder_caller_boundary(root,value)
    require_prior_state_ratio_caller_boundary(root,value)
    require_prior_DFCO_state_caller_boundary(root,value)
    require_prior_paired_inhibit_writer_boundary(root,value)
    require_prior_threshold_window_reader_boundary(root,value)
    require_prior_aux_rate_caller_boundary(root,value)
    require_prior_paired_curve_normalization_boundary(root,value)
    require_prior_byte_ratio_producer_boundary(root,value)
    require_prior_state_surface_caller_boundary(root,value)
    require_prior_byte_factor_caller_boundary(root,value)
    require_prior_reader_direction_boundary(value)
    require_prior_uptight_RAM3348_boundary(value)
    require_prior_restore16aa_boundary(value)
    require_prior_restore1778_boundary(value)
    return value


def selector(row,owner,item):
    old=json.loads(row['original_claim_json'])
    return (item.get('type')==old['type'] and ((owner==row['owner'] and item.get('end')=='owner' and item.get('to')==old['to'])
        or (owner==old['to'] and item.get('end')=='to' and item.get('to')==row['owner'])))


def registered(evidence):
    return (evidence.get('mode')==MODE or evidence.get('path')==DESCRIPTOR
        or isinstance(evidence.get('key'),str) and evidence['key'].startswith(PREFIX))


def publication(link,evidence):
    return False


def looks_like_access(link):
    return any(registered(item) for item in link.evidence) or any(original(row,link) for row in descriptor_identity_rows())


def descriptor_identity_rows():
    # Only pinned hashes identify original claims; no live store or model query.
    return (dict(owner=row[2],original_claim_sha256=row[10]) for row in IDENTITIES)


def original(row,link):
    value=canonical(link)
    return value['owner']==row['owner'] and digest(value)==row['original_claim_sha256']


def correction(row):return True


def operation(row):
    old=json.loads(row['original_claim_json'])
    return dict(cmd='unlink',meaning=row['owner'],type=old['type'],to=old['to'])


removal=operation


def operations(ops,root):
    owners={row[2] for row in IDENTITIES}
    selected=[op for op in ops if (op.get('cmd')=='unlink' and op.get('meaning') in owners)
        or any(registered(item) for item in op.get('evidence',()))]
    if not selected:return False
    expected=[operation(row) for row in descriptor(root)['reference']]
    if len(selected)!=127 or sorted(map(digest,selected))!=sorted(map(digest,expected)):
        raise ValueError('the scalar RAM leaf withdrawal requires exactly all127 unchanged normal unlink operations')
    return True


def require_prior_boundary(root,value):
    # Reconstruct the exact previous postimages by removing only the first
    # nineteen pinned originals from their complete original owner documents.
    # The full-record digest then retains every other prior reference field.
    rows=deepcopy(value['reference'][:19]);expected={
        row['owner']:json.loads(row['original_native_json']) for row in rows}
    for row in rows:
        old=json.loads(row['original_claim_json']);document=expected[row['owner']]
        matches=[index for index,link in enumerate(document.get('link',()))
            if link['type']==old['type'] and link['to']==old['to']]
        if len(matches)!=1:raise ValueError('the retained nineteen originals lose an exact native reader')
        document['link'].pop(matches[0])
        for marker in document.get('ledger',()):
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency'] if not selector(row,row['owner'],item)]
    for document in expected.values():
        if not document.get('link'):document.pop('link',None)
        for marker in document.get('ledger',()):
            if not marker.get('dependency'):marker.pop('dependency',None)
    for row in rows:
        document=expected[row['owner']]
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
    if digest(rows)!=PRIOR_REFERENCE_SHA256 or digest(value['function'][:12])!=PRIOR_FUNCTION_SHA256:
        raise ValueError('the product extension changes the complete retained nineteen-original source boundary')
    for name,sha256 in PRIOR_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the product extension changes a retained scalar leaf fixture, matrix, numerical source, producer or driver')


def require_prior_joint_boundary(root,value):
    # Reconstruct the exact previous postimages by removing only the first
    # twenty-six pinned originals from their complete original owner documents.
    # The full-record digest then retains every other prior reference field.
    rows=deepcopy(value['reference'][:26]);expected={
        row['owner']:json.loads(row['original_native_json']) for row in rows}
    for row in rows:
        old=json.loads(row['original_claim_json']);document=expected[row['owner']]
        matches=[index for index,link in enumerate(document.get('link',()))
            if link['type']==old['type'] and link['to']==old['to']]
        if len(matches)!=1:raise ValueError('the retained twenty-six originals lose an exact native reader')
        document['link'].pop(matches[0])
        for marker in document.get('ledger',()):
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency'] if not selector(row,row['owner'],item)]
    for document in expected.values():
        if not document.get('link'):document.pop('link',None)
        for marker in document.get('ledger',()):
            if not marker.get('dependency'):marker.pop('dependency',None)
    for row in rows:
        document=expected[row['owner']]
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
    if digest(rows)!=PRIOR_JOINT_REFERENCE_SHA256 or digest(value['function'][:16])!=PRIOR_JOINT_FUNCTION_SHA256:
        raise ValueError('the gated extension changes the complete retained twenty-six-original source boundary')
    for name,sha256 in PRIOR_PRODUCT_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the gated extension changes a retained scalar product fixture, matrix, numerical source, producer or driver')


def require_prior_gated_boundary(root,value):
    # Complete prefix postimages retain every preceding record field.
    # Current complete postimages have separate exact identity pins.
    if digest(prior_reference_rows(value,31))!=PRIOR_GATED_REFERENCE_SHA256 or digest(value['function'][:21])!=PRIOR_GATED_FUNCTION_SHA256:
        raise ValueError('the RPM extension changes the full preceding thirty-one originals or twenty-one functions')
    for name,sha256 in PRIOR_GATED_FILES_SHA256.items():
        if hashlib.sha256(prior_gated_source_bytes(root,name)).hexdigest()!=sha256:
            raise ValueError('the RPM extension changes a retained gated fixture, matrix, scalar, physical, producer or generated source')
    for name,sha256,owner,ids,reference_sha256 in RELATED_OWNER_INPUTS:
        raw=(Path(root)/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha256:
            raise ValueError('the RPM extension changes a retained counter or MAF native-source contract')
        related=tomllib.loads(raw.decode())
        rows=[row for row in related['reference'] if row['owner']==owner]
        if tuple(row['id'] for row in rows)!=ids or digest(rows)!=reference_sha256:
            raise ValueError('the RPM extension changes an existing other-family native claim or complete reference')
        own=[row for row in value['reference'][31:] if row['owner']==owner]
        if not own or any(not test_contract.exact(json.loads(row['original_native_json']),
                json.loads(other['original_native_json'])) for row in own for other in rows):
            raise ValueError('the RPM extension substitutes another original owner image for a retained counter or MAF fact')


def require_prior_rpm_ram_boundary(root,value):
    if digest(prior_reference_rows(value,34))!=PRIOR_RPM_RAM_REFERENCE_SHA256 or digest(value['function'][:24])!=PRIOR_RPM_RAM_FUNCTION_SHA256:
        raise ValueError('the overflow extension changes the complete preceding thirty-four originals or twenty-four functions')
    for name,sha256 in PRIOR_RPM_RAM_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the overflow extension changes a retained RPM RAM fixture, input, scalar, physical, producer or generated source')


def prior_reference_rows(value,count):
    # Rebuild the complete previous postimages from full original documents,
    # removing only that exact prefix. The digest retains every other field.
    for row,pinned in zip(value['reference'][:count],IDENTITIES[:count]):
        after=json.loads(row['proposed_native_json'])
        encoded=json.dumps(after,sort_keys=True,separators=(',',':'),ensure_ascii=True)
        if (row['proposed_native_json']!=encoded or digest(after)!=pinned[13]
                or row['proposed_native_sha256']!=pinned[13]
                or row['proposed_ledger_json']!=json.dumps(after.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True)):
            raise ValueError('the word extension substitutes an unpinned current full native postimage')
    rows=deepcopy(value['reference'][:count]);documents={row['owner']:json.loads(row['original_native_json']) for row in rows}
    for row in rows:
        old=json.loads(row['original_claim_json']);document=documents[row['owner']]
        found=[i for i,item in enumerate(document.get('link',())) if item['type']==old['type'] and item['to']==old['to']]
        if len(found)!=1:raise ValueError('the word extension loses a complete preceding native original')
        removed=document['link'].pop(found[0])
        if {k:v for k,v in removed.items() if k not in ('type','to','evidence','role')}!=old['props']:
            raise ValueError('the word extension changes a preceding full native relation')
        for marker in document.get('ledger',()):
            if 'dependency' in marker:marker['dependency']=[item for item in marker['dependency'] if not selector(row,row['owner'],item)]
    for document in documents.values():
        if not document.get('link'):document.pop('link',None)
        for marker in document.get('ledger',()):
            if not marker.get('dependency'):marker.pop('dependency',None)
    for row in rows:
        document=documents[row['owner']]
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),proposed_native_sha256=digest(document),proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
    return rows


def require_prior_overflow_boundary(root,value):
    if digest(prior_reference_rows(value,35))!=PRIOR_OVERFLOW_REFERENCE_SHA256 or digest(value['function'][:25])!=PRIOR_OVERFLOW_FUNCTION_SHA256:
        raise ValueError('the word extension changes the complete preceding thirty-five originals or twenty-five functions')
    for name,sha256 in PRIOR_OVERFLOW_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the word extension changes a retained overflow fixture, input, scalar, physical, producer or generated source')


def prior_gated_source_bytes(root,name):
    raw=(Path(root)/name).read_bytes();repair=GATED_ASSEMBLY_SOURCE_REPAIR
    if name!=repair['path']:return raw
    if hashlib.sha256(raw).hexdigest()!=repair['after_sha256']:
        raise ValueError('the exact gated assembly spelling correction changes another source byte')
    text=raw.decode()
    for old,new in repair['exact_text_changes']:
        if text.count(new)!=1:raise ValueError('the gated assembly loses an exact corrected shift site')
        text=text.replace(new,old,1)
    legacy=text.encode()
    if hashlib.sha256(legacy).hexdigest()!=repair['before_sha256']:
        raise ValueError('the gated assembly cannot reconstruct its complete retained previous source')
    return legacy


def require_prior_word_boundary(root,value):
    if digest(prior_reference_rows(value,38))!=PRIOR_WORD_REFERENCE_SHA256 or digest(value['function'][:28])!=PRIOR_WORD_FUNCTION_SHA256:
        raise ValueError('the RPM-state extension changes the complete preceding thirty-eight originals or twenty-eight functions')
    for name,sha256 in PRIOR_WORD_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the RPM-state extension changes a retained word fixture, input, scalar, physical, producer or generated source')


def require_prior_rpm_state_boundary(root,value):
    # Reconstruct the complete forty-reader prefix from original owner documents
    # and only that prefix of exact removals; later shared-owner deltas stay separate.
    if digest(prior_reference_rows(value,40))!=PRIOR_RPM_STATE_REFERENCE_SHA256 or digest(value['function'][:30])!=PRIOR_RPM_STATE_FUNCTION_SHA256:
        raise ValueError('the indexed writer changes the complete preceding forty reader records or thirty functions')
    for name,sha256 in PRIOR_RPM_STATE_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the indexed writer changes a retained RPM-state fixture, input, scalar, physical, producer or generated source')


def require_prior_indexed_word_boundary(root,value):
    # The new scrupulous-yak reader changes only its exact complete owner
    # postimage. Reconstruct each full preceding record using only prior41.
    if digest(prior_reference_rows(value,41))!=PRIOR_INDEXED_WORD_REFERENCE_SHA256 or digest(value['function'][:31])!=PRIOR_INDEXED_WORD_FUNCTION_SHA256:
        raise ValueError('the division callers change the complete preceding forty-one originals or thirty-one functions')
    for name,sha256 in PRIOR_INDEXED_WORD_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the division callers change a retained indexed-word fixture, input, scalar, physical, producer or generated source')


def require_prior_division_caller_boundary(root,value):
    # Reconstruct complete prior44 postimages from full originals and only
    # that prefix; current complete postimages retain separate exact pins.
    if digest(prior_reference_rows(value,44))!=PRIOR_DIVISION_CALLER_REFERENCE_SHA256 or digest(value['function'][:34])!=PRIOR_DIVISION_CALLER_FUNCTION_SHA256:
        raise ValueError('the byte-curve callers change the complete preceding forty-four originals or thirty-four functions')
    for name,sha256 in PRIOR_DIVISION_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the byte-curve callers change a retained division-caller fixture, input, scalar, physical, producer or generated source')


def require_prior_byte_curve_caller_boundary(root,value):
    # Reconstruct complete prior49 postimages from full originals and only
    # that prefix; the additional shared-owner delta remains separately pinned.
    if digest(prior_reference_rows(value,49))!=PRIOR_BYTE_CURVE_CALLER_REFERENCE_SHA256 or digest(value['function'][:36])!=PRIOR_BYTE_CURVE_CALLER_FUNCTION_SHA256:
        raise ValueError('the word callers change the complete preceding forty-nine originals or thirty-six functions')
    for name,sha256 in PRIOR_BYTE_CURVE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the word callers change a retained byte-curve caller fixture, input, scalar, physical, producer or generated source')


def require_prior_word_interp_caller_boundary(root,value):
    # Every complete prior field is retained through exact prefix postimages.
    # The shared owner permits only its separately pinned additional reader.
    if digest(prior_reference_rows(value,54))!=PRIOR_WORD_INTERP_CALLER_REFERENCE_SHA256 or digest(value['function'][:38])!=PRIOR_WORD_INTERP_CALLER_FUNCTION_SHA256:
        raise ValueError('the scaling callers change the complete preceding fifty-four originals or thirty-eight functions')
    for name,sha256 in PRIOR_WORD_INTERP_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the scaling callers change a retained word-caller fixture, input, scalar, physical, producer or generated source')


def require_prior_scaled_division_boundary(root,value):
    # Reconstruct the complete preceding prefix from full originals. Current
    # complete postimages retain separate exact pins for later shared readers.
    if digest(prior_reference_rows(value,57))!=PRIOR_SCALED_DIVISION_REFERENCE_SHA256 or digest(value['function'][:41])!=PRIOR_SCALED_DIVISION_FUNCTION_SHA256:
        raise ValueError('the curve-scale caller changes the complete preceding fifty-seven originals or forty-one functions')
    for name,sha256 in PRIOR_SCALED_DIVISION_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the curve-scale caller changes a retained scaling/division fixture, input, scalar, physical, producer or generated source')


def require_prior_curve_scale_caller_boundary(root,value):
    # Full prefix postimages retain all preceding fields. Current complete
    # postimages have separate exact identity pins for the four added readers.
    if digest(prior_reference_rows(value,60))!=PRIOR_CURVE_SCALE_CALLER_REFERENCE_SHA256 or digest(value['function'][:42])!=PRIOR_CURVE_SCALE_CALLER_FUNCTION_SHA256:
        raise ValueError('the derivative-scale callers change the complete preceding sixty originals or forty-two functions')
    for name,sha256 in PRIOR_CURVE_SCALE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the derivative-scale callers change a retained curve-scale fixture, input, scalar, physical, producer or generated source')


def require_prior_derivative_scale_caller_boundary(root,value):
    # Complete preceding records retain all fields through exact prefix
    # reconstruction. Current complete images have separate identity pins.
    if digest(prior_reference_rows(value,71))!=PRIOR_DERIVATIVE_SCALE_CALLER_REFERENCE_SHA256 or digest(value['function'][:44])!=PRIOR_DERIVATIVE_SCALE_CALLER_FUNCTION_SHA256:
        raise ValueError('the guarded quotient callers change the complete preceding seventy-one originals or forty-four functions')
    for name,sha256 in PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the guarded quotient callers change a retained paired derivative fixture, input, scalar, physical, producer or generated source')


def require_prior_guarded_quotient_caller_boundary(root,value):
    # Every field of the preceding records is retained through exact prefix
    # reconstruction. Current complete postimages have separate exact pins.
    if digest(prior_reference_rows(value,79))!=PRIOR_GUARDED_QUOTIENT_CALLER_REFERENCE_SHA256 or digest(value['function'][:47])!=PRIOR_GUARDED_QUOTIENT_CALLER_FUNCTION_SHA256:
        raise ValueError('the mixed curve callers change the complete preceding seventy-nine originals or forty-seven functions')
    for name,sha256 in PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the mixed curve callers change a retained guarded quotient fixture, input, scalar, physical, producer or generated source')


def require_prior_mixed_curve_caller_boundary(root,value):
    # Every complete prior record and current postimage remains byte exact.
    # Full prefix reconstruction retains the previous independent boundaries.
    if paired_curve_prefix_digest(value,87)!=PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,87))!=PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256 or digest(value['function'][:51])!=PRIOR_MIXED_CURVE_CALLER_FUNCTION_SHA256:
        raise ValueError('the timing remainder callers change the complete preceding eighty-seven originals or fifty-one functions')
    for name,sha256 in PRIOR_MIXED_CURVE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the timing remainder callers change a retained mixed curve fixture,input,equation,physical,producer or generated source')


def require_prior_timing_remainder_caller_boundary(root,value):
    # Every complete preceding record and current postimage remains exact.
    # Full prefix reconstruction retains every earlier independent boundary.
    if paired_curve_prefix_digest(value,92)!=PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,92))!=PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256 or digest(value['function'][:53])!=PRIOR_TIMING_REMAINDER_CALLER_FUNCTION_SHA256:
        raise ValueError('the state ratio callers change the complete preceding ninety-two originals or fifty-three functions')
    for name,sha256 in PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the state ratio callers change a retained timing remainder fixture,input,equation,physical,producer or generated source')


def require_prior_state_ratio_caller_boundary(root,value):
    # All preceding complete records and current images remain exact.
    # Full prefix reconstruction retains every earlier independent boundary.
    if paired_curve_prefix_digest(value,100)!=PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,100))!=PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256 or digest(value['function'][:55])!=PRIOR_STATE_RATIO_CALLER_FUNCTION_SHA256:
        raise ValueError('the DFCO state caller changes the complete preceding hundred originals or fifty-five functions')
    for name,sha256 in PRIOR_STATE_RATIO_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the DFCO state caller changes a retained state ratio fixture,input,equation,physical,producer or generated source')


def require_prior_DFCO_state_caller_boundary(root,value):
    # Complete preceding records,current images and source boundaries stay exact.
    if paired_curve_prefix_digest(value,107)!=PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,107))!=PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256 or digest(value['function'][:56])!=PRIOR_DFCO_STATE_CALLER_FUNCTION_SHA256:
        raise ValueError('the paired flag writer callers change the complete preceding107 originals or56 functions')
    for name,sha256 in PRIOR_DFCO_STATE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the paired flag writer callers change a retained DFCO fixture,input,equation,physical,producer or generated source')


def function_native_document(row,phase):
    if phase not in ('original','proposed'):
        raise ValueError('a function postimage changes its exact native phase')
    changed=row['owner'] in {pin[0] for pin in FUNCTION_POSTIMAGE_IDENTITIES}
    return json.loads(row[phase+'_native_json' if changed else 'original_native_json'])


def require_function_postimages(value):
    selected=tuple((row['original_claim_sha256'],row['owner'],row['function']) for row in value['reference']
        if json.loads(row['original_claim_json'])['to'] in {pin[0] for pin in FUNCTION_POSTIMAGE_IDENTITIES})
    if selected!=FUNCTION_POSTIMAGE_CLAIMS:
        raise ValueError('the paired writer substitutes an exact selected function-end selector scope')
    rows=[row for row in value['function'] if row['owner'] in {pin[0] for pin in FUNCTION_POSTIMAGE_IDENTITIES}]
    if len(rows)!=len(FUNCTION_POSTIMAGE_IDENTITIES):
        raise ValueError('the paired writer omits a complete function transition')
    removed=0
    for row,pinned in zip(rows,FUNCTION_POSTIMAGE_IDENTITIES):
        identity=tuple(row[key] for key in ('owner','function','source','original_native_sha256',
            'proposed_native_sha256','original_ledger_json','proposed_ledger_json'))
        if not test_contract.exact(identity,pinned):
            raise ValueError('the paired writer changes a complete original/function postimage identity')
        before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
        for phase,document in (('original',before),('proposed',after)):
            canonical=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True)
            ledger=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True)
            if (row[phase+'_native_json']!=canonical or digest(document)!=row[phase+'_native_sha256']
                    or row[phase+'_ledger_json']!=ledger):
                raise ValueError('the paired writer changes a complete canonical function image or its exact ledger')
        expected=deepcopy(before)
        for marker in expected.get('ledger',()):
            if 'dependency' not in marker:continue
            held=marker['dependency']
            marker['dependency']=[item for item in held if not any(selector(claim,row['owner'],item) for claim in value['reference'])]
            removed+=len(held)-len(marker['dependency'])
            if not marker['dependency']:marker.pop('dependency')
        if not test_contract.exact(expected,after):
            raise ValueError('the paired writer changes another function field,TEST context,ledger identity,selector order,note or claim')
    if removed!=8:
        raise ValueError('the full function transitions change their eight exact function-end ledger selectors')


def require_prior_paired_inhibit_writer_boundary(root,value):
    # Complete prior112 postimages reconstruct only the exact additional three
    # reader removals. Both previously pinned full function transitions stay exact.
    if digest(prior_reference_rows(value,112))!=PRIOR_PAIRED_INHIBIT_WRITER_REFERENCE_SHA256 or digest(value['function'][:58])!=PRIOR_PAIRED_INHIBIT_WRITER_FUNCTION_SHA256:
        raise ValueError('the threshold window changes the complete prior112 originals or58 full function records')
    for name,sha256 in PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the threshold window changes a retained paired flag fixture,input,equation,physical,producer or generated source')


def require_prior_threshold_window_reader_boundary(root,value):
    # Every preceding complete record,current datum image and full function
    # record stays exact,including both pinned function-end transitions.
    if paired_curve_prefix_digest(value,115)!=PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256 or digest(prior_reference_rows(value,115))!=PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256 or digest(value['function'][:59])!=PRIOR_THRESHOLD_WINDOW_READER_FUNCTION_SHA256:
        raise ValueError('the auxiliary rate caller changes the complete preceding115 originals or59 function records')
    for name,sha256 in PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the auxiliary rate caller changes a retained threshold-window fixture,input,equation,physical,producer or generated source')


def paired_curve_prefix_digest(value,count):
    # Only the two exact paired readers may change the full current image of
    # prior row79. Reconstruct every preceding field,then apply that complete
    # bounded link/selector delta and compare the entire current record.
    if count not in (87,92,100,107,115,116) or len(value['reference'])!=127:
        raise ValueError('the paired curve changes an exact retained prefix boundary')
    additional=value['reference'][116:118]
    identities=tuple(tuple(row[key] for key in ('id','owner','function','original_claim_sha256','original_claim_json')) for row in additional)
    if not test_contract.exact(identities,PAIRED_CURVE_NORMALIZATION_CLAIMS):
        raise ValueError('the paired curve changes its two exact additional reader identities')
    previous=prior_reference_rows(value,count)
    expected=deepcopy(previous)
    changed=0
    for row in expected:
        if row['owner']!='lyrical-dragon/tbl':continue
        if row['id']!='000659ae-00010b8e-withdraw':
            raise ValueError('the paired curve extends its shared-owner transition to another preceding record')
        document=json.loads(row['proposed_native_json']);removed_links=removed_selectors=0
        for claim in additional:
            old=json.loads(claim['original_claim_json'])
            if digest(old)!=claim['original_claim_sha256'] or old['owner']!=row['owner'] or old['type']!='reader' or old['evidence']!=[] or old['roles']!=[]:
                raise ValueError('the paired curve substitutes another complete original reader')
            matches=[index for index,item in enumerate(document.get('link',())) if item['type']==old['type'] and item['to']==old['to']]
            if len(matches)!=1:
                raise ValueError('the paired curve loses an exact shared-owner reader')
            removed=document['link'].pop(matches[0]);removed_links+=1
            if (removed.get('evidence',[])!=[] or 'role' in removed
                    or not test_contract.exact({key:item for key,item in removed.items() if key not in ('type','to','evidence')},old['props'])):
                raise ValueError('the paired curve changes the exact original reader properties')
            claim_selectors=0
            for marker in document.get('ledger',()):
                if 'dependency' not in marker:continue
                held=marker['dependency']
                selected=[item for item in held if selector(claim,row['owner'],item)]
                marker['dependency']=[item for item in held if not selector(claim,row['owner'],item)]
                claim_selectors+=len(selected)
                if not marker['dependency']:marker.pop('dependency')
            if claim_selectors!=1:
                raise ValueError('the paired curve changes its exact owner-end selector extent')
            removed_selectors+=claim_selectors
        if removed_links!=2 or removed_selectors!=2:
            raise ValueError('the paired curve changes its two-link/two-selector postimage delta')
        if not document.get('link'):document.pop('link',None)
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
        changed+=1
    expected=state_surface_current_prefix(expected,value)
    if changed!=1 or not test_contract.exact(expected,uptight_RAM3348_prior_current_rows(value,count)):
        raise ValueError('the paired curve changes another complete preceding record,current image,ledger,TEST,order,type,role or scope')
    return digest(previous)


def require_prior_aux_rate_caller_boundary(root,value):
    # The exact shared datum delta leaves all sixty full function records,
    # including both complete prior function transitions,unchanged.
    if paired_curve_prefix_digest(value,116)!=PRIOR_AUX_RATE_CALLER_REFERENCE_SHA256 or digest(value['function'][:60])!=PRIOR_AUX_RATE_CALLER_FUNCTION_SHA256:
        raise ValueError('the paired curve changes the complete preceding116 originals or60 full function records')
    for name,sha256 in PRIOR_AUX_RATE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the paired curve changes a retained auxiliary rate fixture,input,equation,physical,producer or generated source')


def require_prior_paired_curve_normalization_boundary(root,value):
    # Every preceding full current record remains exact,including the complete
    # paired-reader shared postimage and both full function transitions.
    if state_surface_prefix_digest(value,118)!=PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256 or digest(prior_reference_rows(value,118))!=PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256 or digest(value['function'][:62])!=PRIOR_PAIRED_CURVE_NORMALIZATION_FUNCTION_SHA256:
        raise ValueError('the byte ratio producer changes the complete preceding118 originals or62 full function records')
    for name,sha256 in PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the byte ratio producer changes a retained paired normalization fixture,input,equation,physical,producer or generated source')


def state_surface_additional_rows(value):
    if len(value['reference'])!=127:
        raise ValueError('the state surface changes its exact whole native source extent')
    additional=value['reference'][119:121]
    try:
        identities=tuple(tuple(row[key] for key in ('id','owner','function','original_claim_sha256','original_claim_json')) for row in additional)
    except (KeyError,TypeError):
        raise ValueError('the state surface omits an exact complete additional reader identity') from None
    if not test_contract.exact(identities,STATE_SURFACE_CLAIMS):
        raise ValueError('the state surface substitutes another complete additional reader scope')
    return additional


def state_surface_current_prefix(previous,value):
    if len(previous) not in (87,92,100,107,115,116,118,119):
        raise ValueError('the state surface changes an exact preceding full-record extent')
    additional=state_surface_additional_rows(value);expected=deepcopy(previous);changed=0
    for index,row in enumerate(expected):
        if row['owner']!='quick-basilisk/tbl':continue
        if index!=99 or row['id']!='00064cb2-00012b52-withdraw':
            raise ValueError('the state surface broadens its one preceding shared-owner record')
        document=json.loads(row['proposed_native_json']);removed_links=removed_selectors=0
        for claim in additional:
            old=json.loads(claim['original_claim_json'])
            if old['owner']!=row['owner']:continue
            if digest(old)!=claim['original_claim_sha256'] or old['type']!='reader' or old['evidence']!=[] or old['roles']!=[]:
                raise ValueError('the state surface changes its exact complete shared-owner reader')
            matches=[i for i,item in enumerate(document.get('link',())) if item['type']==old['type'] and item['to']==old['to']]
            if len(matches)!=1:raise ValueError('the state surface loses its sole additional shared-owner reader')
            removed=document['link'].pop(matches[0]);removed_links+=1
            if (removed.get('evidence',[])!=[] or 'role' in removed
                    or not test_contract.exact({key:item for key,item in removed.items() if key not in ('type','to','evidence')},old['props'])):
                raise ValueError('the state surface changes the complete original reader properties')
            for marker in document.get('ledger',()):
                if 'dependency' not in marker:continue
                held=marker['dependency'];selected=[item for item in held if selector(claim,row['owner'],item)]
                removed_selectors+=len(selected)
                marker['dependency']=[item for item in held if not selector(claim,row['owner'],item)]
                if not marker['dependency']:marker.pop('dependency')
        if removed_links!=1 or removed_selectors!=1:
            raise ValueError('the state surface changes its exact one-reader/one-owner-selector shared delta')
        if not document.get('link'):document.pop('link',None)
        row.update(proposed_native_json=json.dumps(document,sort_keys=True,separators=(',',':'),ensure_ascii=True),
            proposed_native_sha256=digest(document),
            proposed_ledger_json=json.dumps(document.get('ledger'),sort_keys=True,separators=(',',':'),ensure_ascii=True))
        changed+=1
    if changed!=int(len(previous)>99):
        raise ValueError('the state surface omits or broadens its exact preceding full owner postimage')
    return expected


def state_surface_prefix_digest(value,count):
    if count not in (118,119):
        raise ValueError('the state surface changes an exact preceding whole-record boundary')
    previous=prior_reference_rows(value,count)
    expected=state_surface_current_prefix(previous,value)
    if not test_contract.exact(expected,uptight_RAM3348_prior_current_rows(value,count)):
        raise ValueError('the state surface changes another complete preceding record,current image,ledger,TEST,order,type,role or scope')
    return digest(previous)


def require_prior_byte_ratio_producer_boundary(root,value):
    # Only the one exact additional owner delta is admitted. All63 complete
    # preceding functions and both full function transitions remain exact.
    if state_surface_prefix_digest(value,119)!=PRIOR_BYTE_RATIO_PRODUCER_REFERENCE_SHA256 or digest(value['function'][:63])!=PRIOR_BYTE_RATIO_PRODUCER_FUNCTION_SHA256:
        raise ValueError('the state surface changes the complete preceding119 originals or63 full function records')
    for name,sha256 in PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the state surface changes a retained byte-ratio fixture,input,equation,physical,producer or generated source')


def require_prior_state_surface_caller_boundary(root,value):
    # All121 complete preceding records,current images and64 full functions
    # remain exact,including row99,row79 and both complete function transitions.
    if digest(uptight_RAM3348_prior_current_rows(value,121))!=PRIOR_STATE_SURFACE_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,121))!=PRIOR_STATE_SURFACE_CALLER_REFERENCE_SHA256 or digest(value['function'][:64])!=PRIOR_STATE_SURFACE_CALLER_FUNCTION_SHA256:
        raise ValueError('the byte factor changes the complete preceding121 originals or64 full function records')
    for name,sha256 in PRIOR_STATE_SURFACE_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the byte factor changes a retained state-surface fixture,input,equation,physical,producer or generated source')


def require_prior_byte_factor_caller_boundary(root,value):
    # All122 complete preceding records/current images and65 full functions
    # remain exact,including row79,row99 and all three function transitions.
    if digest(uptight_RAM3348_prior_current_rows(value,122))!=PRIOR_BYTE_FACTOR_CALLER_REFERENCE_SHA256 or digest(prior_reference_rows(value,122))!=PRIOR_BYTE_FACTOR_CALLER_REFERENCE_SHA256 or digest(value['function'][:65])!=PRIOR_BYTE_FACTOR_CALLER_FUNCTION_SHA256:
        raise ValueError('the byte sum changes the complete preceding122 originals or65 full function records')
    for name,sha256 in PRIOR_BYTE_FACTOR_CALLER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=sha256:
            raise ValueError('the byte sum changes a retained byte-factor fixture,input,equation,physical,producer or generated source')


READER_ONLY_WITH_RETAINED_WRITER = ('000503e0-ffff1939-reader-withdraw', '1f4d2097a3f3458effbf6627988f7ca56994e2ac95e3acc84ff759a7a665c531', 4294908217, 328672)
PRIOR_READER_DIRECTION_REFERENCE_SHA256 = '7f7559ddffac6f75257ffd5b83ab963d40f2b1a8b31bb229b962a059876d24a5'
PRIOR_READER_DIRECTION_FUNCTION_SHA256 = '2947b18e099f608f8b3855eb29da423115a7c46c49f83aeb831a641e6b34965b'

def require_prior_reader_direction_boundary(value):
    if (digest(prior_reference_rows(value,123))!=PRIOR_READER_DIRECTION_REFERENCE_SHA256
            or digest(value['function'][:66])!=PRIOR_READER_DIRECTION_FUNCTION_SHA256):
        raise ValueError('the reader-direction withdrawal changes a complete prior123 record or66 function boundary')
    row=value['reference'][123]
    if tuple(row[key] for key in ('id','original_claim_sha256','address','function'))!=READER_ONLY_WITH_RETAINED_WRITER:
        raise ValueError('the reader-direction withdrawal changes its one exact retained-writer identity')
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    if (json.loads(row['original_claim_json'])['type']!='reader'
            or not test_contract.exact([r for r in before['link'] if r['type']=='writer'],after['link'])
            or before['unit']!='enum_u8' or after['unit']!=before['unit']):
        raise ValueError('the reader-direction withdrawal changes a complete actual writer or enum unit')


def require_prior_uptight_RAM3348_boundary(value):
    if (digest(prior_reference_rows(value,124))!=PRIOR_UPTIGHT_RAM3348_REFERENCE_SHA256
            or digest(value['function'][:66])!=PRIOR_UPTIGHT_RAM3348_FUNCTION_SHA256):
        raise ValueError('the uptight RAM3348 withdrawal changes a complete prior124 record or66 function boundary')
    row=value['reference'][124]
    if tuple(row[key] for key in ('id','original_claim_sha256','address','function','component'))!=UPTIGHT_RAM3348_WITHDRAWAL:
        raise ValueError('the uptight RAM3348 withdrawal changes its exact original or existing same-primary consumer')
    shared=[held for held in value['reference'][:124] if held['owner']==row['owner']]
    if ([held['function'] for held in shared]!=[0xB7768,0xB78DA,0xB7A3C]
            or any(not test_contract.exact(tuple(held[key] for key in
                ('original_native_json','proposed_native_json','original_native_sha256','proposed_native_sha256')),
                tuple(row[key] for key in ('original_native_json','proposed_native_json','original_native_sha256','proposed_native_sha256')))
                for held in shared)):
        raise ValueError('the uptight RAM3348 withdrawal changes a complete common four-reader owner image')


UPTIGHT_RAM3348_WITHDRAWAL = ('000b784e-ffff3348-withdraw', '59ee18e4be7bbc935c2e08f6fcf90dc42c21494b0ce73ff39550cc184342305f', 4294914888, 751694, 'curve_scale_caller_withdrawal_paths')
PRIOR_UPTIGHT_RAM3348_REFERENCE_SHA256 = 'a172ca9b5e1aead2a9419fbee4fd3da20e4771fec84cadb15a7f84bdb7f9aea5'
PRIOR_UPTIGHT_RAM3348_FUNCTION_SHA256 = '2947b18e099f608f8b3855eb29da423115a7c46c49f83aeb831a641e6b34965b'

UPTIGHT_RAM3348_PRIOR_SHARED_IDS = ('000b7768-ffff3348-withdraw', '000b78da-ffff3348-withdraw', '000b7a3c-ffff3348-withdraw')
UPTIGHT_RAM3348_PRIOR_SHARED_POSTIMAGE = ('{"ledger":[{"dependency":[{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"great-loon/ram","type":"input"},{"end":"owner","relies":"level","role":"indexed_by","supports":"identity","to":"raspberry-dragon/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"striped-horse/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"zealous-dalmatian/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],"notes":[0],"order":532,"registry":"vars"}],"level":"code","link":[{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"great-loon/ram","type":"input"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"raspberry-dragon/ram","type":"input"},{"layouts":["7mfk"],"relies":"structure","supports":"identity","to":"striped-horse/ram","type":"input"},{"layouts":["7mfk"],"reverse_relies":"level","reverse_supports":"identity","role":"indexed_by","to":"uptight-duck/fn","type":"reader"},{"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"zealous-dalmatian/fn","type":"reader"},{"layouts":["7mfk"],"relies":"level","supports":"identity","to":"zealous-dalmatian/fn","type":"writer"}],"note":["Exact DID 0x1101 and the hard-coded -50 offset establish the temperature representation. When the model-ready gate is clear, the retained state is replaced by current coolant temperature after the calculation; otherwise the saturated integrated result is retained for the next pass."],"summary":"Signed P0128 model-temperature state in 1e-6 deg C. FUN 000b6b5a seeds it as 1000000*uint8[ffff1071]-50000000, otherwise loads the retained integrated state ffff9df0, and passes it to three P0128 term accessors before adding scaled balance ffff3400.","symbol":[{"address":"ffff3348","evidence":[{"at":"7mfk:000b6c22","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c60","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c62","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c64","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c66","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c6a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c6e","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c7e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6c8e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6cc0","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6cd4","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6d26","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6d2e","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6d36","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b6d9c","key":"reference","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b78ee","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b78f0","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b78f2","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}},{"at":"7mfk:000b7a5a","key":"body","kind":"l0-context","supports":"identity","value":{"named":["000b6b5a","000b7768","000b78da","000b7a3c","ffff1071","ffff3348","ffff3400","ffff9df0"],"span":1}}],"layout":"7mfk","name":"ruddy-anaconda"}],"unit":"P0128 model temperature [1e-6 deg C]"}', '93b5e80935759100047f5d30f434097a08122954a0eec6e2703f06c3576b7164', '[{"dependency":[{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"great-loon/ram","type":"input"},{"end":"owner","relies":"level","role":"indexed_by","supports":"identity","to":"raspberry-dragon/ram","type":"input"},{"end":"owner","relies":"structure","role":"indexed_by","supports":"identity","to":"striped-horse/ram","type":"input"},{"end":"owner","relies":"level","role":"writes","supports":"identity","to":"zealous-dalmatian/fn","type":"writer"}],"fields":["semantics","units","confidence"],"identity":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],"notes":[0],"order":532,"registry":"vars"}]')


def uptight_RAM3348_prior_current_rows(value,count):
    # Admit every current full postimage before restoring only the three
    # pinned historical shared-owner postimage fields for earlier boundaries.
    prior_reference_rows(value,count)
    rows=deepcopy(value['reference'][:count]);changed=0
    fields=('proposed_native_json','proposed_native_sha256','proposed_ledger_json')
    current=value['reference'][124]
    for row in rows:
        if row['id'] not in UPTIGHT_RAM3348_PRIOR_SHARED_IDS:continue
        if (row['owner']!='ruddy-anaconda/ram' or not test_contract.exact(
                tuple(row[key] for key in fields),tuple(current[key] for key in fields))):
            raise ValueError('the uptight historical boundary substitutes a current complete shared-owner postimage')
        row.update(zip(fields,UPTIGHT_RAM3348_PRIOR_SHARED_POSTIMAGE));changed+=1
    if changed!=3:
        raise ValueError('the uptight historical boundary changes its three exact preceding shared-owner rows')
    return rows


RESTORE_READER_ONLY_WITH_RETAINED_WRITER=('00050018-ffff16aa-reader-withdraw', 'a66ad148b5399b0aa33727484628763c1d8210c778dd76e365159d56098cf5f8', 4294907562, 327704)
PRIOR_RESTORE16AA_REFERENCE_SHA256='d1970929b204661947618fd3a226df59a141877cb3975634b99d9b40c83e2e9d'
PRIOR_RESTORE16AA_FUNCTION_SHA256='3d2758d850b49ae04d5dfa2f7e5d99b952b92b7b779f5a7878e89f1bca915b90'


def require_prior_restore16aa_boundary(value):
    if (digest(value['reference'][:125])!=PRIOR_RESTORE16AA_REFERENCE_SHA256
            or digest(value['function'][:67])!=PRIOR_RESTORE16AA_FUNCTION_SHA256):
        raise ValueError('the restore reader withdrawal changes a complete prior125 record or67 function boundary')
    row=value['reference'][125]
    if tuple(row[key] for key in ('id','original_claim_sha256','address','function'))!=RESTORE_READER_ONLY_WITH_RETAINED_WRITER:
        raise ValueError('the restore reader withdrawal substitutes its exact original or natural caller')
    old=json.loads(row['original_claim_json'])
    before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    if (old['type']!='reader' or old['roles']!=[] or old['evidence']!=[] or old['to']!='dfco_restore_classify/fn'
            or row['declared_width']!='unset' or row['declared_signed']!='unset'
            or before.get('unit')!='RPM/25' or after.get('unit')!=before['unit']
            or not test_contract.exact([link for link in before['link'] if link['type']=='writer'],
                [link for link in after['link'] if link['type']=='writer'])):
        raise ValueError('the restore reader withdrawal changes its actual writer, native unit, unset types or original claim')
    function=value['function'][67]
    if function['owner']!=old['to'] or function['function']!=row['function'] or 'proposed_native_json' in function:
        raise ValueError('the restore reader withdrawal changes its complete retained function instead of its one reader')


RESTORE1778_READER_ONLY_WITH_RETAINED_WRITER=('00050018-ffff1778-reader-withdraw', 'ee78dd754d5bc5778e829fa0e0fad67c39036ac7bf491d27c0fd7f3a9af3dbf7', 4294907768, 327704)
PRIOR_RESTORE1778_REFERENCE_SHA256='5f6174a2dd7a29af1ffd4cf4655bc20ebd39d3ba1bbca1744f0598a2845bb563'
PRIOR_RESTORE1778_FUNCTION_SHA256='08b05ec5b91861ef106e37ac776f059be713c19c9c3698f687ce17a4296e7de7'


def require_prior_restore1778_boundary(value):
    if (digest(value['reference'][:126])!=PRIOR_RESTORE1778_REFERENCE_SHA256
            or digest(value['function'])!=PRIOR_RESTORE1778_FUNCTION_SHA256):
        raise ValueError('the intermediate restore reader changes a complete prior126 record or68 function boundary')
    row=value['reference'][126]
    if tuple(row[key] for key in ('id','original_claim_sha256','address','function'))!=RESTORE1778_READER_ONLY_WITH_RETAINED_WRITER:
        raise ValueError('the intermediate restore reader substitutes its exact original or natural caller')
    old=json.loads(row['original_claim_json']);before,after=(json.loads(row[phase+'_native_json']) for phase in ('original','proposed'))
    if (old['type']!='reader' or old['roles']!=[] or old['evidence']!=[] or old['to']!='dfco_restore_classify/fn'
            or row['declared_width']!='unset' or row['declared_signed']!='unset'
            or before.get('unit')!='RPM/25' or after.get('unit')!=before['unit']
            or not test_contract.exact([link for link in before['link'] if link['type']=='writer'],
                [link for link in after['link'] if link['type']=='writer'])):
        raise ValueError('the intermediate restore reader changes its actual writer, unit, unset types or original claim')
    function,=[item for item in value['function'] if item['owner']==old['to']]
    if function['function']!=row['function'] or 'proposed_native_json' in function:
        raise ValueError('the intermediate restore reader changes its complete retained function')
