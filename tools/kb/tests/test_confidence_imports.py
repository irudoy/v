import subprocess
import sys

from kb import repo


def test_core_imports_and_confidence_analysis_load_no_stock_proof_modules():
    probe = """
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

def optional_proof(name):
    if not name.startswith('kb.'):
        return False
    leaf = name.rsplit('.', 1)[-1]
    return (leaf.endswith(('_contract', '_evidence', '_resolution', '_matrix', '_semantics'))
            or leaf in {'ordinary_access_registry', 'test_catalog', 'test_primary',
                        'test_origins', 'width_compatibility'}
            or leaf.startswith('test_stock'))

class NoProofImports:
    def find_spec(self, fullname, path=None, target=None):
        if optional_proof(fullname):
            raise AssertionError('core imports optional proof: ' + fullname)

sys.meta_path.insert(0, NoProofImports())
sys.path.insert(0, sys.argv[1])
from kb import cli, read, compile, store, model, graph, write, levels, checks, mcp

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'patches').mkdir()
    (root / levels.HARDWARE).write_text('')
    (root / 'probe.py').write_text('def test_probe():\\n    raise AssertionError("not executed")\\n')
    layout = SimpleNamespace(id='sample', family='sample', mcu='sample', images=())
    builder = model.Builder({'sample': layout}, {}, {'sample': frozenset({0x100})}, {})
    for address, support in ((0x2000, True), (0x2001, False)):
        item = {'kind': 'test', 'path': 'probe.py', 'key': 'test_probe'}
        if support:
            item['supports'] = 'identity'
        key = builder.symbol('sample', 'ram', address, 'test', evidence=[item])
        builder.props(key, {'level': 'code'}, 'test')
    optional = {'kind': 'indirect', 'supports': 'identity', 'mode': 'optional-domain-access',
                'at': 'sample:00000100'}
    ram = builder.symbol('sample', 'ram', 0x3000, 'test', evidence=[optional])
    builder.props(ram, {'level': 'code'}, 'test')
    fn = builder.symbol('sample', 'fn', 0x100, 'test')
    builder.props(fn, {'level': 'code'}, 'test')
    builder.link(ram, 'reader', fn, 'test', props={'relies': 'structure'}, evidence=[optional])
    found = builder.finish()
    found.root, found.config, found.functions = root, {}, builder.functions
    result = levels.analyze(found)
    confidence = {claim.subject: result.level(claim) for claim in result.claims}
    assert confidence['sample-00002000/ram'] == 'code', confidence
    assert confidence['sample-00002001/ram'] == 'candidate', confidence
    assert confidence['sample-00003000/ram'] == 'candidate', confidence
assert not any(optional_proof(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", probe, str(repo.ROOT / "tools/kb/src")],
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
