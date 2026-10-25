"""The LTFT extension retains exact earlier learning claims and native boundaries."""

from copy import deepcopy
import hashlib

import pytest

from kb import copy_evidence,copy_witness,ignition_literal_evidence,repo
from kb import learning_access_contract as owning,learning_transfer_matrix as matrix
from kb import learning_transfer_contract as contract

RETAINED_CLAIMS=(('00057d1e-0000839c-reader',
  '529f0cd3899ec15f65f89a636df957fc4a75ee613fb898fd583d2cb219b84d01',
  '8ccb7e04fab0b41bbb0f0eeee5ca18f43788905a647d13f68152c6c9884fc77e'),
 ('00057d1e-0000839d-reader',
  '237c62e9e603e6b6315802ebacafccd757b9b82f94c1690ba11302e4f6e4e9df',
  'ef04218b4fe796d57ab25281b7a7eb579a0d357358d85839c292353566d53c46'),
 ('00057d1e-000088f5-reader',
  '34cb0ba5fb3bc27ecce9a7f9290d1620fa15395298026c039ca4f96729f1e244',
  '01070bc172c6b44ea756cac1fb01cfb39403f593cc574193f3f67ac5277e1ac1'),
 ('00057d1e-ffff1350-reader',
  '50e81d437f52be115ebd58cca382e1d4e99c70051f6f70f9865a53d402d05279',
  '8d4d803ba93ec51b268d37a4b3b4fda260278bf05fc5316e73befed9ec37d7fc'),
 ('00057d1e-ffff22de-reader',
  '0f69d3bf780d2b4112e086ac1d02eb4a91c75874416c5eb9f89717052a21a119',
  '1368605230af51beedc6c031035996a147bc931e871771596c838e8141499769'),
 ('0005796c-ffff2308-writer',
  'c1e04163294a04923961350463d0d7f4f3c022e33ef8b4f86dea738a3e01a617',
  '0fe069f1c6de71861d57dd0e74d000830b690271dad4f1682cf314037aad9a97'),
 ('00057d1e-ffff2308-reader',
  'e65afa619ba50fa764a292fc30d3a93d87cb5b40cd67ea10a48a5884833cb41f',
  '55b0fc6bd1c3dffd1965926dd0e7863c58ebf00f2c16f61be2b9c2ca18cceff9'),
 ('0005796c-ffff45a2-writer',
  '63ea187d545aab4484b22367b2e81c9a8c4eb998fe046884f4bfedd2325ed1f2',
  '5eefe529c4724c9119664748f599346c7d9cc483a3898d3f2d528460fc12a08b'),
 ('0005796c-ffff49b0-writer',
  '2ca47d39c33a1c3e36a3716093a3ad160de9f77fd55c8970fb3f54587308f4a0',
  'aa9ec98e957e82419cef5ab634512f224e31c476a36b5f99471f46c62ff2b913'),
 ('000580e8-ffff49b0-reader',
  'f08ae3a9b032e1656726ca716504466e55c0675d66c90478f171d2dd24c08096',
  '4403f7db1ec2304139bba00b3c029567fd7d342edb664c08a772943c07bbde81'),
 ('000580e8-ffff49b0-writer',
  '608463f1a8f999bc43492bebb6f64ad311edbd4d2039c4f57ad730eafc7e552e',
  '93cf2d860bc3132b8d2276d8bf577d1d244ae70ee77124c96e420320a3d02730'),
 ('0005796c-ffff49f0-writer',
  '9b4f79417c7ac4699e001360dbf83ae46e9cb7d6d6142450a20e0f7f0a0eea96',
  '9b12875edc4746cb0ae843d912be7c5abbb8419882d37e0f5ac726dc01799d3c'),
 ('000580e8-ffff49f0-reader',
  '518feb778cb7b5f2a9e230954d855a61cecbcc3133d97450cd4c002bf664f888',
  '400598c19659a1c3fe52c43a151985b704b25617b59cff355d90d5dcfba21085'),
 ('000580e8-ffff49f0-writer',
  '4e846b5f182e4a2cd4e711c3aa7d7dc3fecaf51ae92660a8fe32ea528a33d314',
  'b6e9544d2a3352178ea23d64925ecd3472a68a85d9c2b825979dba2231280f5e'),
 ('0005796c-ffff4b10-writer',
  '6074a39f0f5a139c52150a70509d07589d04f26d32541d2e5b205c4a2e923569',
  '260783bef3a86306045df5731fb08b382895d8fd581d3f33a95b55ec434a2107'),
 ('00057d1e-ffff4b10-writer',
  '68ac4709e94a8e9e48508d8cb4266e5350d59e819fd52515c56dfc263ecec4a1',
  '49744cf2e7c022fcce5979122c5d50e4d3eef32c4c9169379bb915fbc5f6ab1e'),
 ('0005796c-ffff4b90-writer',
  'e8eb0b67e81c693e557ef53e5a498c6d99aef0a1d57f1f7cc28c4d2ba7526bf8',
  'da96393c210c72f170996aac5fe65e965cff07c6b7118415dfca55bcbe7aa9bd'),
 ('00057d1e-ffff4b90-writer',
  'aad338a63b9f0677659d341c028f3a11de3ffbd8e80a8ebe0ad283734e0ddb90',
  'de9a459d71e468926648e79e36e284321f288d5531150d32d11ae2b140ce51d2'))


def test_joint_extension_retains_all_eighteen_original_and_proposed_claim_items():
    rows={row['id']:row for row in owning.descriptor(repo.ROOT)['reference']}
    for identity,before,after in RETAINED_CLAIMS:
        assert (rows[identity]['original_claim_sha256'],rows[identity]['proposed_claim_sha256'])==(before,after)
    added=[row for key,row in rows.items() if key not in {item[0] for item in RETAINED_CLAIMS}]
    assert {(row['owner'],row['address'],row['direction'],tuple(row['sites'])) for row in added}=={
        ('ltft_b2/ram',0xFFFF2304,'writer',(0x57C2A,)),
        ('inquisitive-dormouse/ram',0xFFFF2308,'reader',(0x57B36,)),
        ('benevolent-anteater/ram',0xFFFF564A,'reader',(0x57B3A,))}
    assert all((row['declared_width'],row['declared_signed'])==(16,'unset') for row in added)


@pytest.mark.parametrize('field,address',(('ltft_l',0x2308),('ltft_a',0x564A)))
def test_publication_reader_alternatives_hold_every_other_physical_input_fixed(field,address):
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=[row for row in matrix.cases(declared,image) if row['kind']=='publication' and row['argument']==1]
    first=next(row for row in cases if row['ltft_l']==row['ltft_a']==25600 and row['ltft_mask']==3)
    second=deepcopy(first);second[field]+=1
    assert matrix.context(declared,first)==matrix.context(declared,second)
    a,b=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    assert a[address:address+2]!=b[address:address+2];a[address:address+2]=b[address:address+2]
    assert a==b and matrix.calibrations(declared,image,first)==matrix.calibrations(declared,image,second)


def test_complete_primary_provenance_binds_the_existing_LTFT_arithmetic_source():
    path='tools/kb/tests/test_ltft_publication_chain.py'
    digest=hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()
    assert path in copy_evidence.EXECUTION_FILES
    assert copy_witness.provenance(repo.ROOT)[path]==ignition_literal_evidence.execution_inputs(repo.ROOT)[path]==digest
