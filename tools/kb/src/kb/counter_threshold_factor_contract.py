"""One exact owning dimensionless factor; representation alone grants no scale."""

import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, native_ledger, plain, retired_ledger
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.counter-threshold-factor.toml'
KEY = 'counter-threshold-factor-v1:jk08a-aafa'
MODE = 'arithmetic-factor'
OWNER = 'natural-hedgehog/tbl'
TARGET = 'pompous-firefly/fn'
SYMBOL = SymbolKey('7mfk', 'tbl', 0xAAFA)
FUNCTION = SymbolKey('7mfk', 'fn', 0x21BBC)
FIELDS = dict(unit='ratio', scale='x/10', to_raw='x*10', scale_level='code')
ORIGINAL = 'c52565bea75dd644bcf2fd1d78ed5caec3f658a0b00c32a4e9cdab91ab55efbe'
PROPOSED = 'eb000913a58842385f8308341406f5ff109155fe75b77d873bc52d260ca54937'
FLAGS = ('physical_reader_inference', 'physical_time_units_inference', 'hardware_qualification',
         'natural_scheduling_inference', 'unrelated_claim_changes')


def descriptor(root):
    value = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if (set(value) != {'schema', 'id', 'layout', 'image_sha256', 'scope', 'reference',
                       'owned_factor_scale_only', *FLAGS}
            or not test_contract.exact(value['schema'], 1)
            or value['id'] != 'jk08a-counter-threshold-factor' or value['layout'] != '7mfk'
            or value['image_sha256'] != 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or value['owned_factor_scale_only'] is not True or any(value[key] is not False for key in FLAGS)
            or len(value['reference']) != 1):
        raise ValueError('the counter-threshold factor changes its exact owning scale scope')
    row = value['reference'][0]
    keys = {'id', 'address', 'owner', 'wrapper', 'caller', 'callsite', 'delay_slot', 'component',
            'owned_fields_json', 'original_claim_sha256', 'original_claim_json',
            'proposed_claim_sha256', 'proposed_claim_json', 'original_ledger_json', 'proposed_ledger_json'}
    if (set(row) != keys or not test_contract.exact(tuple(row[key] for key in
            ('id', 'address', 'owner', 'wrapper', 'caller', 'callsite', 'delay_slot', 'component')),
            ('counter-threshold', 0xAAFA, OWNER, 0x260BC, 0x79538, 0x79728, 0x7972A, 'counter_threshold_paths'))
            or row['original_claim_sha256'] != ORIGINAL or row['proposed_claim_sha256'] != PROPOSED
            or not test_contract.exact(json.loads(row['owned_fields_json']), FIELDS)):
        raise ValueError('the counter-threshold factor changes its native owner, call or original scale')
    old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
    if (digest(old) != ORIGINAL or digest(new) != PROPOSED or old['type'] != 'reader'
            or old['owner'] != OWNER or old['to'] != TARGET or old['props']['supports'] != 'scale'
            or old['props']['relies'] != 'contract' or new['type'] != 'depends'
            or new['roles'] != [MODE] or new['props']['via'] != [str(SymbolKey('7mfk', 'fn', at))
                                                               for at in (0x79538, 0x260BC)]
            or any(not test_contract.exact(new[key], old[key]) for key in
                   ('owner', 'to', 'layout', 'slot', 'offset', 'sources', 'stated', 'evidence'))
            or set(new['props']) != set(old['props']) | {'via', 'note'}
            or any(not test_contract.exact(new['props'].get(key), item) for key, item in old['props'].items())
            or not test_contract.exact(json.loads(row['proposed_ledger_json']), retired_ledger(row))):
        raise ValueError('the owning factor changes another original fact or ledger selector')
    return value


def item(row):
    return dict(kind='indirect', mode=MODE, key=KEY, path=DESCRIPTOR, at='7mfk:0000aafa',
        to=FUNCTION, supports='scale', value=dict(owner=OWNER, owned_fields=FIELDS,
            original_claim_sha256=row['original_claim_sha256'], caller=0x79538, wrapper=0x260BC,
            callsite=0x79728, delay_slot=0x7972A, scope='owning-dimensionless-ratio-factor',
            physical_reader_inference=False, physical_time_units_inference=False,
            natural_scheduling_inference=False, hardware_qualification=False))


def original(row, link):
    return test_contract.exact(canonical(link), json.loads(row['original_claim_json']))


def dependency(row, link):
    expected = json.loads(row['proposed_claim_json'])
    expected['evidence'] = [plain(item(row))]
    return test_contract.exact(canonical(link), expected)


def registered(evidence):
    return (evidence.get('mode') == MODE or evidence.get('path') == DESCRIPTOR
            or isinstance(evidence.get('key'), str) and evidence['key'].startswith('counter-threshold-factor-'))


def looks_like_dependency(link):
    return (MODE in link.roles or any(registered(value) for value in link.evidence)
            or link.owner.key == OWNER and link.type == 'depends' and link.to.key == TARGET)
