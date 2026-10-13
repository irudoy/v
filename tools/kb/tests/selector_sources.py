"""Canonical sources with populated rows for isolated selector contracts.

The zero-filled catalog item supports the original reference-reader input
contract. The instruction corpus is empty; reference declarations describe
controlled fixture identities and do not establish stock ROM behavior.
"""

import copy
import hashlib
import json
from pathlib import Path

from kb import l0, repo, store
from tools.kb.tests import architecture_sources


STATE, FUNCTION = 'knock_timing_state/ram', 'knock_function/fn'
STATE_PATH = store.path_of('ram', 'knock_timing_state')
FUNCTION_PATH = store.path_of('fn', 'knock_function')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_sources(root):
    hashes = architecture_sources.write_sources(root)
    identity = {'kind': 'spec', 'path': 'defs/fixture.md', 'key': 'controlled_identity'}
    scale = {**identity, 'key': 'controlled_index', 'supports': 'scale'}

    def marker(registry, order, fields, **keys):
        return {'registry': registry, 'order': order, 'fields': fields,
                'dependency': [], **keys}

    def symbol(address, **keys):
        return {'layout': keys.pop('layout', '7mfk'), 'address': address,
                'evidence': [copy.deepcopy(identity)], **keys}

    relation = {'type': 'writer', 'to': FUNCTION, 'layouts': ['7mfk'],
                'relies': 'structure', 'supports': 'identity',
                'reverse_relies': 'structure', 'reverse_supports': 'identity',
                'note': 'Retain unrelated writer metadata.'}
    state = {'summary': 'Controlled signed timing state.', 'width': 16, 'signed': True,
             'unit': 'deg', 'note': 'Retain unrelated owner metadata.',
             'symbol': [symbol('ffff121a'), symbol('ffff121c', layout='1nd')],
             'ledger': [marker('vars', 584, ['semantics', 'units', 'confidence'], identity=[0])],
             'link': [copy.deepcopy(relation)]}
    state['ledger'][0]['dependency'] = [{
        'role': 'consumer', 'to': 'capture_copy/fn', 'type': 'reader', 'end': 'owner',
        'relies': 'structure', 'supports': 'identity'}]
    state['link'].append({'type': 'reader', 'to': 'capture_copy/fn', 'layouts': ['7mfk'],
                          'relies': 'structure', 'supports': 'identity'})
    function = {'summary': 'Controlled writer function.', 'block': 'capture/block',
                'symbol': [symbol('000493e8'), symbol('000493ea', layout='1nd')],
                'ledger': [marker('funcs', 142, ['semantics', 'confidence'], identity=[0]),
                           marker('curated', 98, ['name'])]}
    function['ledger'][0]['dependency'] = [{
        'role': 'writes', 'to': 'unrelated_probe/ram', 'type': 'writer', 'end': 'to',
        'relies': 'structure', 'supports': 'identity'}]
    other_path = store.path_of('ram', 'unrelated_probe')
    other = copy.deepcopy(store.load(root, other_path))
    other['ledger'] = [marker('vars', 1000, ['semantics'], dependency=[{
        'role': 'writes', 'to': FUNCTION, 'type': 'writer', 'end': 'owner',
        'relies': 'structure', 'supports': 'identity'}])]
    other['link'] = [copy.deepcopy(relation)]
    axis = {'summary': 'Controlled index axis.', 'quantity': 'rpm', 'unit': 'RPM',
            'scale': 'x', 'to_raw': 'x', 'scale_level': 'code',
            'symbol': [symbol('00011cf0', name='fascinating-hog',
                              evidence=[copy.deepcopy(identity), copy.deepcopy(scale)])],
            'ledger': [marker('axes', 0, ['kind', 'units', 'scale_expr', 'to_byte', 'scale_conf'],
                             scale=[1], dependency=[{
                'role': 'indexed_by', 'to': 'unrelated_probe/ram', 'type': 'index',
                'end': 'owner', 'relies': 'structure', 'supports': 'scale'}])],
            'link': [{'type': 'index', 'to': 'unrelated_probe/ram', 'layouts': ['7mfk'],
                      'relies': 'structure', 'supports': 'scale'}]}
    image = bytes(0x100000)
    image_path = Path('rom-images/fixture.bin')
    interp_path = Path(repo.config(root)['l0']['census']['7mfk']['interp'])
    homology = (root / repo.HOMOLOGY).read_text() + '''[family.selector_foreign]
kind = "distinct-code"
mcu = "SH7058"
same_address_inheritance = false
members = ["SELECTOR_FOREIGN"]
[family.selector_foreign.layouts]
1nd = "SELECTOR_FOREIGN"
'''
    texts = {repo.HOMOLOGY: homology,
             Path('l0/1nd/funcs.csv'): 'addr\n000493ea\n',
             STATE_PATH: store.render('ram', state), FUNCTION_PATH: store.render('fn', function),
             other_path: store.render('ram', other),
             store.path_of('axis', 'fascinating-hog'): store.render('axis', axis),
             Path('l0/7mfk/funcs.csv'): 'addr\n00010000\n00010002\n000493e8\n',
             repo.CATALOG: 'rom,path,sha256\n' + ''.join(
                 f'{label},fixture.bin,{sha(image)}\n' for label in ('FIXTURE', 'SELECTOR_FOREIGN')),
             interp_path: 'wrapper,kernel\n',
             Path('l0/7mfk/function_tokens.csv'): 'func_addr,ins_addr,ordinal,mnemonic,shape\n',
             Path('l0/7mfk/function_references.csv'): (
                 'func_addr,ins_addr,ordinal,mnemonic,ref_addr,width,value_hex,ref_type\n'
                 '000493e8,000493e8,0,fixture_ref,ffff1012,2,,CONTROLLED\n'
                 '000493e8,000493ea,1,fixture_ref,ffff121a,2,,CONTROLLED\n')}
    config = repo.config(root)
    config['l0']['census']['1nd'] = {'interp': 'defs/fixture-1nd.interp.csv'}
    texts[Path('defs/fixture-1nd.interp.csv')] = 'wrapper,kernel\n'
    texts[repo.CONFIG] = ''.join(json.dumps(key) + ' = ' + architecture_sources._value(value)
                                + '\n' for key, value in config.items())
    for layout in ('7mfk', '1nd'):
        for filename, columns in l0.CORE.items():
            path = Path('l0') / layout / filename
            if path not in texts and not (root / path).exists():
                texts[path] = ','.join(name for name, _ in columns) + '\n'
    for path, text in texts.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        hashes[str(path)] = sha(text.encode())
    (root / image_path).write_bytes(image)
    hashes[str(image_path)] = sha(image)
    for layout in ('7mfk', '1nd'):
        manifest = '# Controlled instruction-free selector inputs.\n' + (
            f'layout = "{layout}"\nimage_sha256 = "{sha(image)}"\n')
        for filename in l0.CORE:
            path = Path('l0') / layout / filename
            manifest += f'[files."{filename}"]\nsha256 = "{sha((root / path).read_bytes())}"\n'
        path = Path('l0') / layout / l0.MANIFEST
        (root / path).write_text(manifest, encoding='utf-8')
        hashes[str(path)] = sha(manifest.encode())
    return hashes


unchanged = architecture_sources.unchanged
