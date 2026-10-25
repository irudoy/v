"""Exact native dispositions of the sexy-tamarin value arguments."""

import json,tomllib
from pathlib import Path
from kb import test_contract
from kb.diagnostic_rom_contract import digest,canonical,retired_ledger
from kb.model import SymbolKey

DESCRIPTOR='defs/JK08A.sexy-tamarin-argument.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
TARGET='pompous-firefly/fn'
CALLER=0xC0D90
WRAPPER=0x26474
ROWS=(('sturdy-worm',0x1252A,'sturdy-worm/tbl',0xC0DF6,0xC0DF8,
       'eb871db5a6f0b38f7d7efc3444e0640b3c7ec7d68fd9715e019a0d56ec747619',
       '3dc894d384fe7fa9135522f8742563bbf19daf435fffbe327ee7de600406421b'),
      ('foamy-cuckoo',0x12532,'foamy-cuckoo/tbl',0xC0DF6,0xC0DF8,
       '043f0659533233b92e315d11485c5d6342a1a6e92b6994ce683946f12df2f6a1',
       '300b6a0d58147921b7730ea84432a92f636d70f455188b08a55671e595bb30cb'),
      ('strange-salmon',0x123F2,'strange-salmon/tbl',0xC0F28,0xC0F2A,
       '69eb70517728bd53a338ed82a74ae69e2163509a6a33f9693cf1115ca10bbd2f',
       '9267fec4ecc6235080db8f8179b03528e9f4dcd2f142b8f0851596accbf90ded'),
      ('greedy-chamois',0x123FA,'greedy-chamois/tbl',0xC0F28,0xC0F2A,
       '57fa5de4f5cbb7812e42702279a04251aef47c4049f7d8ca3071a2594fcb5fac',
       'dcf701a5d855fdc316db69756e8a66c216ead3fc1668690a4fbbd76ec1c4b961'))
FLAGS=('physical_reader_inference','scale_admission','hardware_qualification','natural_scheduling_inference',
       'universal_no_ROM_read','unrelated_claim_changes')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','image_sha256','scope','reference',*FLAGS}
            or value['id']!='jk08a-sexy-tamarin-argument' or value['layout']!='7mfk'
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] for key in FLAGS)
            or len(value['reference'])!=len(ROWS)):
        raise ValueError('the sexy-tamarin argument descriptor changes its exact admission boundary')
    keys={'id','address','owner','wrapper','caller','callsite','delay_slot','component',
          'original_claim_sha256','original_claim_json','proposed_claim_sha256','proposed_claim_json',
          'original_ledger_json','proposed_ledger_json'}
    via=[str(SymbolKey('7mfk','fn',CALLER)),str(SymbolKey('7mfk','fn',WRAPPER))]
    for row,expected in zip(value['reference'],ROWS):
        identity,address,owner,site,delay,original,proposed=expected
        if set(row)!=keys or row['id']!=identity or row['address']!=address or row['owner']!=owner:
            raise ValueError('the sexy-tamarin argument changes its exact owner')
        if not test_contract.exact((row['caller'],row['wrapper'],row['callsite'],row['delay_slot'],row['component'],
                row['original_claim_sha256'],row['proposed_claim_sha256']),
                (CALLER,WRAPPER,site,delay,'sexy_tamarin_paths',original,proposed)):
            raise ValueError('the sexy-tamarin argument changes its exact caller, delay slot or identity')
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        if (digest(old)!=original or digest(new)!=proposed or old['type']!='reader' or old['to']!=TARGET
                or new['type']!='depends' or new['to']!=TARGET or new['roles']!=['arithmetic-argument']
                or new['props']['via']!=via
                or not test_contract.exact(json.loads(row['proposed_ledger_json']),retired_ledger(row))):
            raise ValueError('the sexy-tamarin argument replacement changes another original property or ledger selector')
    return value


def original(row,link):
    return test_contract.exact(canonical(link),json.loads(row['original_claim_json']))
