"""Exact existing-owner I/O proofs and positive native-site attribution."""

from copy import deepcopy
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.diagnostic_rom_contract import canonical, digest, plain
from kb.model import SymbolKey

DESCRIPTOR = 'defs/JK08A.io-access-claims.toml'
PREFIX = 'io-access-v1:jk08a:'
IDENTITIES = (('mailbox26-control', 4294958144, 'solemn-heron/reg', 'append-link-proof', 798654, 798692, 798808, 2, 'f9f323f37557fec26eb85d24c3d152dda5cad209f1409359fc965181f94db22c', '6489d26d5e941915f9cd390fcce1a8625cea9465dfda9429296e0a1014907f62', '400611819a11f03efa2dc52fc33b95f6280cae737a79d67d71496e818304b35a', 'ed60bf37ac1877bec0584f867dbe8afc0fb5e79c9d0be14a64c4b1b91e1fb393'), ('capture-word-attribution', 4294964272, 'ingenious-kagu/reg', 'relocate-site-evidence', 8256, 8256, 8270, 4, '9f4bc5c60b95559a1da54bef1dbe23c4a94adde07183e82ef5e66e9f7b9ca8a2', '74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b', '13192c2f0f716f3a1c5ab474340d7f76f934dc6dbe5084cdb2f8a154d14dd2e8', '0114ca03a71df36164aabc870228ec6dbed0fd7b7d92f53f7e9ce9901352a913'), ('monitor-input-word', 4294965076, 'precise-kagu/reg', 'append-link-proof', 683460, 683464, 683684, 2, 'edde43425c45e484554d6759f189ff782a45c2ade7d008ee7a7ed0b02ebac440', 'fe357da5d0d609aad64a1b853f489bda7cbda3ffeab547741da4af7dfc765de5', 'ab588ca1db3a8332e5ca2df856f73e6325608c891f83c4b504383d44616b0956', '721fb64182be97afe13bf3f7362847f3a74ef2ee91a6f5b85a0ea125d2d23405'))
FLAGS = ('native_function_publication', 'native_geometry_publication', 'universal_no_read_claim',
         'scale_admission', 'physical_units_inference', 'peripheral_side_effects_admission',
         'natural_caller_reachability', 'hardware_qualification', 'unrelated_claim_changes')


def descriptor(root):
    value = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if (set(value) != {'schema', 'id', 'layout', 'image_sha256', 'scope', 'reference', *FLAGS}
            or not test_contract.exact(value['schema'], 1) or value['id'] != 'jk08a-io-access-claims'
            or value['layout'] != '7mfk'
            or value['image_sha256'] != 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
            or any(value[key] is not False for key in FLAGS) or len(value['reference']) != len(IDENTITIES)):
        raise ValueError('the I/O claim descriptor changes its exact existing-owner scope')
    keys = {'id', 'address', 'owner', 'disposition', 'actual_function', 'window_entry', 'site', 'width_bytes',
            'source', 'component', 'original_claim_sha256', 'original_claim_json', 'proposed_claim_sha256',
            'proposed_claim_json', 'original_native_sha256', 'original_native_json', 'proposed_native_sha256',
            'proposed_native_json', 'original_ledger_json', 'proposed_ledger_json',
            'original_symbol_evidence_json', 'proposed_symbol_evidence_json', 'evidence_json'}
    for row, identity in zip(value['reference'], IDENTITIES):
        if (set(row) != keys or not test_contract.exact(tuple(row[key] for key in
                ('id', 'address', 'owner', 'disposition', 'actual_function', 'window_entry', 'site', 'width_bytes',
                 'original_claim_sha256', 'proposed_claim_sha256', 'original_native_sha256', 'proposed_native_sha256')),
                identity) or row['component'] != 'io_access_paths'):
            raise ValueError('an I/O claim changes an exact original owner, site, width or disposition')
        old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
        before, after = json.loads(row['original_native_json']), json.loads(row['proposed_native_json'])
        if (digest(old) != row['original_claim_sha256'] or digest(new) != row['proposed_claim_sha256']
                or digest(before) != row['original_native_sha256'] or digest(after) != row['proposed_native_sha256']
                or old['owner'] != row['owner'] or old['sources'] != [row['source']]
                or row['source'] != 'kb/reg/' + row['owner'].rsplit('/', 1)[0] + '.toml'):
            raise ValueError('an I/O claim changes its full original/proposed native content')
        evidence = item(row)
        if (set(evidence) != {'kind', 'mode', 'key', 'path', 'at', 'supports', 'value', 'note'}
                or evidence['kind'] != 'indirect' or evidence['mode'] != 'io-access'
                or evidence['key'] != PREFIX + row['id'] or evidence['path'] != DESCRIPTOR
                or evidence['at'] != f'7mfk:{row["site"]:08x}' or evidence['supports'] != 'identity'):
            raise ValueError('the I/O proof changes its exact owning attachment')
        expected = deepcopy(before)
        symbols = [symbol for symbol in expected.get('symbol', ()) if symbol['layout'] == '7mfk'
                   and int(symbol['address'], 16) == row['address']]
        links = [(index, link) for index, link in enumerate(expected.get('link', ()))
                 if link['type'] == old['type'] and link['to'] == old['to']]
        if len(symbols) != 1 or len(links) != 1:
            raise ValueError('the I/O transition lacks a unique original symbol or relation')
        symbol = symbols[0]
        if not test_contract.exact(symbol.get('evidence', []), json.loads(row['original_symbol_evidence_json'])):
            raise ValueError('the I/O transition changes original symbol evidence or its order')
        index, link = links[0]
        if row['disposition'] == 'relocate-site-evidence':
            if (row['owner'] != 'ingenious-kagu/reg' or old['type'] != 'reader'
                    or old['to'] != 'capture_interval_update/fn' or old['roles'] != ['indexed_by']
                    or before.get('ledger') is not None or new is not None):
                raise ValueError('the captured-word transition changes another attribution or creates a function')
            del expected['link'][index]
            symbol.setdefault('evidence', []).append(evidence)
        else:
            qualified = deepcopy(old)
            qualified['evidence'] = [*old['evidence'], evidence]
            if not test_contract.exact(new, qualified):
                raise ValueError('the I/O link proof changes more than its exact owning evidence append')
            link.setdefault('evidence', []).append(evidence)
        if (not test_contract.exact(after, expected)
                or not test_contract.exact(json.loads(row['original_ledger_json']), before.get('ledger'))
                or not test_contract.exact(json.loads(row['proposed_ledger_json']), before.get('ledger'))
                or not test_contract.exact(json.loads(row['proposed_symbol_evidence_json']), symbol.get('evidence', []))):
            raise ValueError('the I/O transition changes another native field, ledger or evidence position')
    return value


def symbol_key(row):
    return SymbolKey('7mfk', 'reg', row['address'])


def item(row):
    return json.loads(row['evidence_json'])


def original(row, link):
    return test_contract.exact(canonical(link), json.loads(row['original_claim_json']))


def qualified(row, link):
    expected = json.loads(row['proposed_claim_json'])
    return expected is not None and test_contract.exact(canonical(link), expected)


def registered(evidence):
    return (evidence.get('mode') == 'io-access' or evidence.get('path') == DESCRIPTOR
            or isinstance(evidence.get('key'), str) and evidence['key'].startswith(PREFIX))


def looks_like_access(link):
    return (any(registered(item) for item in link.evidence)
            or (link.owner.key, link.type, link.to.key) in (
                ('solemn-heron/reg', 'writer', 'granite-chameleon/fn'),
                ('ingenious-kagu/reg', 'reader', 'capture_interval_update/fn'),
                ('precise-kagu/reg', 'reader', 'festive-gopher/fn')))
