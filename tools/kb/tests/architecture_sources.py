"""Canonical source data for isolated architecture writer contracts."""

import copy
import hashlib
import json
from pathlib import Path

from kb import repo, store


def _value(data):
    if isinstance(data, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + _value(v) for k, v in data.items()) + '}'
    if isinstance(data, list):
        return '[' + ', '.join(_value(v) for v in data) + ']'
    return json.dumps(data)


def write_sources(root):
    """A disposable root with complete schema inputs and independent documents.

    The two layout declarations provide function-entry and address geometry.
    Fixture specification evidence anchors these controlled identities; the
    source data carry no stock instruction or hardware claims.
    """
    config = copy.deepcopy(repo.config())
    config['writers']['review'] = []
    texts = {
        repo.CONFIG: ''.join(json.dumps(k) + ' = ' + _value(v) + '\n' for k, v in config.items()),
        repo.HOMOLOGY: '''[family.probe]
kind = "exact-code"
mcu = "SH7058"
same_address_inheritance = false
members = ["FIXTURE"]
[family.probe.layouts]
7mfk = "FIXTURE"
[family.foreign]
kind = "distinct-code"
mcu = "SH7058"
same_address_inheritance = false
members = ["FOREIGN"]
[family.foreign.layouts]
jk78c = "FOREIGN"
''',
        repo.CATALOG: 'rom,path,sha256\n',
        Path('patches/hardware-results.toml'): '',
        Path('defs/fixture.md'): 'Controlled identities for isolated source-writer contracts.\n',
        Path('l0/7mfk/funcs.csv'): 'addr\n00010000\n00010002\n',
        Path('l0/jk78c/funcs.csv'): 'addr\n0008d384\n',
    }
    proof = [{'kind': 'spec', 'path': 'defs/fixture.md'}]
    ram = ['rpm', *('capture_' + str(i) for i in range(1, 7)), 'engine_speed_result', 'fuel_inhibit']
    for i, name in enumerate([*ram, 'unrelated_probe']):
        document = {'summary': 'Fixture ' + name + '.', 'width': 16, 'signed': False,
                    'symbol': [{'layout': '7mfk', 'address': f'{0xffff1000 + 2*i:08x}',
                                'evidence': copy.deepcopy(proof)}]}
        if name == 'unrelated_probe':
            document['note'] = 'Preserve unrelated metadata.'
        texts[store.path_of('ram', name)] = store.render('ram', document)
    for i, name in enumerate(('capture_copy', 'capture_convert')):
        texts[store.path_of('fn', name)] = store.render('fn', {
            'summary': 'Fixture call ' + name + '.', 'block': 'capture/block',
            'symbol': [{'layout': '7mfk', 'address': f'{0x10000 + 2*i:08x}',
                        'evidence': copy.deepcopy(proof)}]})
    texts[store.path_of('fn', 'accelerator_pedal_pair_selector')] = store.render('fn', {
        'summary': 'Foreign-only fixture call.',
        'symbol': [{'layout': 'jk78c', 'address': '0008d384',
                    'evidence': copy.deepcopy(proof)}]})
    texts[store.path_of('stage', 'capture')] = store.render('stage', {
        'title': 'Capture', 'summary': 'Fixture capture stage.', 'lane': 'flow', 'order': 1})
    texts[store.path_of('block', 'capture')] = store.render('block', {
        'title': 'Capture', 'summary': 'Fixture capture block.', 'stage': 'capture/stage', 'order': 1})
    steps = [{'from': ram[i] + '/ram', 'to': ram[i+1] + '/ram',
              'via': ['capture_copy/fn' if i % 2 == 0 else 'capture_convert/fn'],
              'effect': 'copies', 'sign': 'positive', 'note': 'to = from'} for i in range(7)]
    texts[store.path_of('chain', 'engine_speed')] = store.render('chain', {
        'title': 'Capture', 'summary': 'Fixture ordered capture.', 'quantity': 'Capture counts',
        'home': '7mfk', 'order': 1, 'output': 'engine_speed_result/ram', 'step': steps})
    for path, text in texts.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    return {str(path): hashlib.sha256(text.encode()).hexdigest() for path, text in texts.items()}


def unchanged(root, hashes):
    """Every disposable source retains its construction bytes."""
    return all(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
               for path, digest in hashes.items())
