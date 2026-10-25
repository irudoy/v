"""Exact native representations of the sequenced normalization arguments."""

import json
from pathlib import Path
import tomllib
from kb import test_contract
from kb.diagnostic_rom_contract import canonical,digest,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.normalization-arguments.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ROWS=(('curve-a', 83354, 'tbl', 'brown-jackrabbit/tbl', '8f08f1a407b6105a42c4d5ef024df7a0275b5928ecf9fa0b52da744afe4e384f', '0e2c9f9f35cca2eebf5e8ddc4506109255986c68c18747da114af228327b3f7c'), ('curve-b', 83402, 'tbl', 'placid-mastiff/tbl', '0dd7759d7caf08c33c49ba8ff77e99df2c9e3d3c8bd9e538730df814fb527ae1', 'a056da320626e8dd9f8aa10dc889caa7e15356856752579a901374190c980fb6'), ('coefficient-table', 84314, 'tbl', 'tested-dragon/tbl', '51d58253de29fc01364cb080b35a933c5c4d7445906b0b4a1cc81e6d89515f84', '0f564465596f8788c687414faddfdfe8ddc791816c52489afd467bb6fa8a4320'), ('published-coefficient', 4294912872, 'ram', 'nice-raven/ram', '9bfc5a922cc540e3e88c9e27912b76f262b84e07766bfd2cae2f4e1fccf273d9', '5c6012d4b64acfe373db425f03527fa0856aed01521ff3d5b36f4a900d85afd7'))
FLAGS=('physical_reader_inference', 'scale_admission', 'hardware_qualification', 'natural_scheduling_inference', 'universal_no_ROM_read', 'unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-normalization-arguments'
            or value['layout']!='7mfk' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or len(value['reference'])!=len(ROWS)):
        raise ValueError('the normalization argument descriptor changes its exact conditional scope')
    keys={'id','address','symbol_kind','owner','target','caller','wrapper','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    for row,expected in zip(value['reference'],ROWS):
        key,address,kind,owner,original,proposed=expected
        if (set(row)!=keys or not test_contract.exact(tuple(row[name] for name in
                ('id','address','symbol_kind','owner','original_claim_sha256','proposed_claim_sha256')),expected)
                or not test_contract.exact(tuple(row[name] for name in
                    ('target','caller','wrapper','callsite','delay_slot','component')),
                    ('unsigned_divide/fn',0x6205C,0x264F8,0x627E0,0x627E2,'normalization_paths'))):
            raise ValueError('a normalization argument changes its exact source, call or delay slot')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!='unsigned_divide/fn'
                or new['type']!='depends' or new['to']!=old['to'] or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=[str(SymbolKey('7mfk','fn',at)) for at in (0x6205C,0x264F8)]
                or any(not test_contract.exact(new[name],old[name]) for name in
                       ('owner','layout','slot','offset','sources','stated','evidence'))
                or any(not test_contract.exact(new['props'].get(name),item) for name,item in old['props'].items())
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('a normalization argument changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
