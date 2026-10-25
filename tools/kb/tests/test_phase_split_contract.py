"""Splitter arguments and native identity retain the original normalizer contract."""

from copy import deepcopy

import pytest

from kb import phase_access_contract as owning,phase_normalization_contract as contract
from kb import phase_normalization_matrix as matrix,phase_split_semantics as split,repo

RETAINED_CLAIMS=(('ffff13b8-reader',
  'cd910dcbf30c3d090b3b1a9d8e10d765eac64f12003eab20d3dfbc615eff2cd3',
  '3b2832c18f4241eaa430a71c9c37fe1906aadbaaf8604cf0a36b09d488429f35'),
 ('ffff13b8-writer',
  '8e41c4bb288af2c59ba0f52c7594232bc77979950bf5f6a1a1fa7e0161b46bd8',
  '3fe06ab415d4fb6005cf0bee6761db6edbcb93d57674ec759ddf81a9b4e46637'),
 ('ffff1558-reader',
  '2009c140f1e08862fd8f77f8bf676bb8ca1693cac892ac9cb646f4806c07e8ce',
  'd6fdc35b7535e7d5eb72a9e9a03779c0353363669a3c7940bda1cfc80df2b4ba'),
 ('ffff1558-writer',
  'bb6a2d755f2f317e18e693398a96fb55a1e4a150e4b2cc6b39ec6708a6667832',
  'c3aa8817cd03f1838fd4d46305348905c8af31893e6b957e9787861e6a1c3280'),
 ('ffff155a-reader',
  '4f695ad9c1115d8bbaac83be399ca60cb0cf41cc8f4a2f7e0c8dff798c56c0d6',
  '630cf4298767017cea5aa02aa6e88403bc9ffd70dbc1d7136a01da6783cf15a8'),
 ('ffff155a-writer',
  '596e450f6b5a82a6749fccede61705a98b5a0400c690b909f3bc23fca439a5e7',
  '515fdcfd99a3380d2a390222e1c575d8956b3c4dad8401bc4acc4b19d0da7095'),
 ('ffff193b-reader',
  'f4e18c757da8f8186ae164e6f3fb22e51036af6e6ff1de040cd331dbe6d57735',
  '96328833ea9037739eaedef079b795d16a735497d06b62d6859222b826e94e0a'),
 ('ffff193b-writer',
  '590d921070d8ae82f97279f0d946a2a7d0e74aab582b6e975f3cc87c70d58f1a',
  'bb50b25bd7b1e4ab861cec1c9b1caf4840a7df2d3077dc38a5a2fcdb1f55f5f5'))


def test_joint_ten_preserves_all_eight_prior_original_and_proposed_claim_items():
    rows={row['id']:row for row in owning.descriptor(repo.ROOT)['reference']}
    for identity,before,after in RETAINED_CLAIMS:
        assert (rows[identity]['original_claim_sha256'],rows[identity]['proposed_claim_sha256'])==(before,after)
    added=[row for key,row in rows.items() if key not in {item[0] for item in RETAINED_CLAIMS}
           and row['component']=='phase_normalization_paths']
    assert {(row['owner'],row['function'],tuple(row['sites']),row['width_bytes']) for row in added}=={
        ('vivacious-petrel/ram',0x28E7C,(0x28E94,),2),('peridot-pony/ram',0x28E7C,(0x28E98,),1)}
    assert all(row['declared_width']==row['declared_signed']=='unset' for row in added)


@pytest.mark.parametrize('argument,count,remainder,t',((0,0,0,1),(9,0,9,1),(10,1,0,0),(255,25,5,0),
    (256,25,6,0),(65535,6553,5,0),(65536,6554,252,0),(0x80000000,0,0,1),(0xFFFFFFFF,65535,9,0)))
def test_full_R4_low_product_shift_and_truncation_have_independent_literal_boundaries(argument,count,remainder,t):
    actual=split.scalar(argument)
    assert (actual['quotient'],actual['remainder'],actual['exit_t'])==(count,remainder,t)


@pytest.mark.parametrize('argument',range(256))
def test_quotient_remainder_by_ten_meaning_has_an_explicit_byte_domain(argument):
    actual=split.scalar(argument)
    assert (actual['quotient'],actual['remainder'])==divmod(argument,10)


@pytest.mark.parametrize('pair',(0,1))
def test_splitter_argument_alternatives_hold_every_other_context_and_memory_input_fixed(pair):
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    first=next(row for row in matrix.cases(declared,image) if row['entry']==0x28E7C and row['pair']==pair and row['argument']==9)
    other=deepcopy(first);other['argument']=10
    a,b=list(matrix.context(declared,first)),list(matrix.context(declared,other))
    assert a[4]!=b[4];a[4]=b[4]
    assert a==b and matrix.memory(first)==matrix.memory(other)
