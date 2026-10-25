"""Independent physical binding of raw stock observations to the primary gate."""

from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

from kb import test_contract


def tool(root, filename, name):
    """Load the declared local producer library without invoking its entrypoint."""
    path = Path(root).resolve() / 'tools/sh-elf-run' / filename
    source = path.read_bytes()
    source_digest = hashlib.sha256(source).hexdigest()
    module = sys.modules.get(name)
    if module is not None:
        if (Path(module.__file__).resolve() != path
                or getattr(module, '_kb_bound_source_sha256', None) != source_digest):
            raise ValueError('the TEST stock library belongs to another checkout or source snapshot')
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('the declared TEST stock library is unavailable')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        exec(compile(source, str(path), 'exec'), module.__dict__)
        if path.read_bytes() != source:
            raise ValueError('the TEST stock library source changes while loading')
        module._kb_bound_source_sha256 = source_digest
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _hash(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def require(model, primary, key, declaration):
    """Require the existing complete region and exact physical consumed bytes.

    The caller separately validates the original shared primary terminal and
    the adapter's semantic equations. This function grants no native claim.
    """
    root = Path(model.root).resolve()
    capture = tool(root, 'native_test_capture.py', '_kb_native_test_capture')
    stock = tool(root, 'verify_stock_code.py', '_kb_native_test_stock')
    spec = capture.Spec.from_packet(declaration)
    if spec.region != key:
        raise ValueError('the TEST semantic adapter requests another stock region')
    regions = [region for region in stock.REGIONS if region.key == key]
    if len(regions) != 1 or key not in stock.REGION_OBSERVERS:
        raise ValueError('the TEST semantic adapter has no exact current stock ABI region')
    region = regions[0]
    if spec.invocations != region.cases:
        raise ValueError('the TEST capture changes the complete original region size')
    record = primary.raw_regions()[key]
    required = {'region', 'capture', 'consumed', 'augmented_harness', 'code', 'pools',
                'image_sha256', 'fixture_sha256', 'elf_sha256', 'observer_object_sha256',
                'command', 'simulator', 'stdout', 'stderr', 'toolchain', 'semantic_admission'}
    if (type(record) is not dict or set(record) != required
            or record['semantic_admission'] is not False
            or not test_contract.exact(record['region'], json.loads(test_contract.json_text(asdict(region))))):
        raise ValueError('the TEST raw region replaces its current registered stock contract')
    sources = capture.consumed_sources(root, region, stock.REGION_OBSERVERS[key])
    if not test_contract.exact(record['consumed'], {path: data.hex() for path, data in sorted(sources.items())}):
        raise ValueError('the TEST raw region has different or incomplete consumed executable sources')
    expected_harness = sources['tools/sh-elf-run/' + region.harness] + capture.appendix(spec)
    if record['augmented_harness'] != expected_harness.hex():
        raise ValueError('the TEST augmented harness changes its exact original source or ABI appendix')
    observed = capture.observe(record['stdout'], spec)
    if not test_contract.exact(record['capture'], observed):
        raise ValueError('the TEST raw observations differ from their actual region stdout')
    marker = f'VQ_SH_ELF_STOCK_CODE status=PASS region={key} cases={region.cases}'
    if record['stdout'].splitlines().count(marker) != 1:
        raise ValueError('the TEST raw region lacks its unique complete original PASS marker')
    expected_terminal = dict(returncode=0,
        stdout_sha256=hashlib.sha256(record['stdout'].encode()).hexdigest(),
        stderr_sha256=hashlib.sha256(record['stderr'].encode()).hexdigest())
    if not test_contract.exact(record['simulator'], expected_terminal):
        raise ValueError('the TEST raw region replaces its actual simulator terminal or streams')
    command = record['command']
    if (type(command) is not list or len(command) != 3
            or command[:2] != [stock.base_verifier.RUN,
                              f'--memory-region={stock.base_verifier.TEST_RAM_BASE:#x},64k']
            or type(command[2]) is not str or Path(command[2]).name != key + '-harness.elf'):
        raise ValueError('the TEST raw region runs another simulator command or executable')
    image = stock.stock_image(region.rom)
    code = [dict(start=start, end=end, stock=image[start:end].hex(),
                 reconstructed=image[start:end].hex()) for start, end in region.code_spans]
    pools = [dict(address=address, stock=image[address:address + size].hex(),
                  reconstructed=image[address:address + size].hex()) for address, size in region.pools]
    if not test_contract.exact(record['code'], code) or not test_contract.exact(record['pools'], pools):
        raise ValueError('the TEST raw region changes its stock instructions or GNU pool reconstruction')
    fixture = stock.build_fixture(region, image)
    if (record['image_sha256'] != hashlib.sha256(image).hexdigest()
            or record['fixture_sha256'] != hashlib.sha256(fixture).hexdigest()
            or not _hash(record['elf_sha256']) or not _hash(record['observer_object_sha256'])):
        raise ValueError('the TEST raw region changes its ROM, prepared fixture or actual artifact identity')
    toolchain = record['toolchain']
    if (type(toolchain) is not dict or set(toolchain) != {'simulator_version', 'gcc_version', 'binaries'}
            or toolchain['simulator_version'] != '16.3' or toolchain['gcc_version'] != '13.3.0'
            or type(toolchain['binaries']) is not dict
            or set(toolchain['binaries']) != {'as', 'ld', 'objcopy', 'gcc', 'run'}
            or not all(_hash(value) for value in toolchain['binaries'].values())):
        raise ValueError('the TEST raw region lacks the pinned actual GNU toolchain identities')
    return dict(region=key, cases=region.cases,
                image_sha256=record['image_sha256'], fixture_sha256=record['fixture_sha256'],
                elf_sha256=record['elf_sha256'], observer_object_sha256=record['observer_object_sha256'],
                consumed={path: hashlib.sha256(data).hexdigest() for path, data in sorted(sources.items())},
                stdout_sha256=expected_terminal['stdout_sha256'])
