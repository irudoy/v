"""Canonical populated sources for isolated generic writer contracts.

The catalog buffer and instruction-free corpora supply the original reader
inputs. Reference declarations and specification evidence describe controlled
fixture identities and establish no stock instruction or hardware behavior.
"""

import copy
import hashlib
import json
from pathlib import Path

from kb import l0, names, repo, store
from tools.kb.tests import architecture_sources, selector_sources


def sha(data):
    return hashlib.sha256(data).hexdigest()

def write_sources(root):
    hashes = selector_sources.write_sources(root)
    identity = {'kind': 'spec', 'path': 'defs/fixture.md', 'key': 'controlled_identity'}

    def symbol(layout, address, **keys):
        return {'layout': layout, 'address': address, 'evidence': [copy.deepcopy(identity)], **keys}

    def ram(summary, *symbols, **keys):
        return {'summary': summary, 'width': 16, 'signed': False,
                'symbol': list(symbols), **keys}

    def function(summary, *symbols):
        return {'summary': summary, 'block': 'capture/block', 'symbol': list(symbols)}

    rpm = ram('Controlled reader source.', symbol('7mfk', 'ffff11bc'),
              symbol('1nd', 'ffff11bc'), symbol('1me3b', 'ffff11bc'),
              note='Retain unrelated reader metadata.', link=[
                  {'type': 'reader', 'to': 'rev_fuel_cut_state_machine/fn',
                   'note': 'Retain held reader metadata.', 'evidence': [copy.deepcopy(identity)]},
                  {'type': 'reader', 'to': 'cryptic-heron/fn'}])
    documents = {
        ('ram', 'rpm'): rpm,
        ('ram', 'throttle_runtime'): ram('Controlled contract-free input.',
            symbol('7mfk', 'ffff1796'), symbol('jk78c', 'ffff17a4'),
            note='Retain unrelated input metadata.'),
        ('ram', 'fuel_inhibit'): ram('Controlled named state without a raw conversion.',
            symbol('7mfk', 'ffff2497'), symbol('jk00c', 'ffff251f')),
        ('tbl', 'astute-toad'): {'summary': 'Controlled unnamed table.', 'storage': 'uint8',
            'cols': 1, 'rows': 1, 'symbol': [symbol('7mfk', '00011ff6', name='astute-toad')]},
        ('fn', 'accelerator_pedal_pair_selector'): function('Controlled input consumer.',
            symbol('7mfk', '0006ec68'), symbol('jk78c', '0008d384')),
        ('fn', 'rev_fuel_cut_state_machine'): function('Controlled named reader.',
            symbol('7mfk', '00020004'), symbol('1nd', '00020006'),
            symbol('1me3b', '00020008')),
        ('fn', 'uptight-tiger'): function('Controlled unnamed reader with a foreign alias.',
            symbol('7mfk', '00020000', name='uptight-tiger'),
            symbol('1nd', '00020002', name='cryptic-heron')),
        ('fn', 'asparagus-scallop'): function('Controlled unnamed table accessor.',
            symbol('7mfk', '0002000a', name='asparagus-scallop')),
        ('tbl', 'fuel_compensation_alternate'): {'summary': 'Controlled table links.',
            'storage': 'uint8', 'cols': 1, 'rows': 1,
            'symbol': [symbol('7mfk', '00030000')], 'link': [
                {'type': 'axis', 'to': 'fascinating-hog/axis', 'slot': 'x'},
                {'type': 'reader', 'to': 'asparagus-scallop/fn', 'role': 'accessor'}]},
        ('feature', 'map_switching'): {},
    }
    documents[('fn', 'accelerator_pedal_pair_selector')]['level'] = 'code'
    layouts = {'7mfk': 'FIXTURE', 'jk78c': 'FOREIGN', 'jk00c': 'PROBE00C',
               'jk00d': 'PROBE00D', '1nd': 'PROBE1ND', '1me3b': 'PROBE1ME3B'}
    homology = ''
    for layout, image in layouts.items():
        homology += (f'[family.probe_{layout}]\nkind = "distinct-code"\nmcu = "SH7058"\n'
                     f'same_address_inheritance = false\nmembers = ["{image}"]\n'
                     f'[family.probe_{layout}.layouts]\n{layout} = "{image}"\n')
    texts = {store.path_of(kind, slug): store.render(kind, document)
             for (kind, slug), document in documents.items()}
    image_digest = sha(bytes(0x100000))
    texts.update({
        repo.HOMOLOGY: homology,
        repo.CATALOG: 'rom,path,sha256\n' + ''.join(
            f'{image},fixture.bin,{image_digest}\n' for image in layouts.values()),
        names.PATH: names.render([names.Row('7mfk', 'ram', 0xffff0ff0,
                                           'probe-heron', ('probe-otter',))]),
        Path('tools/kb/SPEC.md'): (repo.ROOT / 'tools/kb/SPEC.md').read_text(encoding='utf-8'),
        Path('l0/7mfk/funcs.csv'): 'addr\n00010000\n00010002\n000493e8\n0006ec68\n'
                                  '00020000\n00020004\n0002000a\n',
        Path('l0/1nd/funcs.csv'): 'addr\n00020002\n00020006\n',
        Path('l0/1me3b/funcs.csv'): 'addr\n00020008\n',
        Path('l0/jk00c/funcs.csv'): 'addr\n',
        Path('l0/jk00d/funcs.csv'): 'addr\n',
    })
    config = repo.config(root)
    for layout in layouts:
        config['l0']['census'][layout] = {'interp': f'defs/fixture-{layout}.interp.csv'}
        texts[Path(config['l0']['census'][layout]['interp'])] = 'wrapper,kernel\n'
        for filename, columns in l0.CORE.items():
            path = Path('l0') / layout / filename
            if path not in texts and not (root / path).exists():
                texts[path] = ','.join(name for name, _ in columns) + '\n'
        tokens = Path('l0') / layout / 'function_tokens.csv'
        references = Path('l0') / layout / 'function_references.csv'
        if layout != '7mfk':
            texts[tokens] = 'func_addr,ins_addr,ordinal,mnemonic,shape\n'
            texts[references] = 'func_addr,ins_addr,ordinal,mnemonic,ref_addr,width,value_hex,ref_type\n'
    refs = Path('l0/7mfk/function_references.csv')
    texts[refs] = (root / refs).read_text() + (
        '00010000,00010000,0,fixture_ref,ffff11bc,2,,CONTROLLED\n')
    texts[repo.CONFIG] = ''.join(json.dumps(key) + ' = ' + architecture_sources._value(value)
                                + '\n' for key, value in config.items())
    for path, text in texts.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        hashes[str(path)] = sha(text.encode())
    for layout in layouts:
        manifest = '# Controlled instruction-free fixture inputs.\n' + (
            f'layout = "{layout}"\nimage_sha256 = "{image_digest}"\n')
        for filename in l0.CORE:
            path = Path('l0') / layout / filename
            manifest += f'[files."{filename}"]\nsha256 = "{sha((root / path).read_bytes())}"\n'
        path = Path('l0') / layout / l0.MANIFEST
        (root / path).write_text(manifest, encoding='utf-8')
        hashes[str(path)] = sha(manifest.encode())
    return hashes


unchanged = selector_sources.unchanged
