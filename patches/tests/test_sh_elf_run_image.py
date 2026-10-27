"""The firmware-gate image resolves from frozen inputs and carries their identity."""

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools/sh-elf-run'
SNAPSHOT = re.compile(r'\d{8}T\d{6}Z')
EXACT = re.compile(r'[0-9][0-9A-Za-z.+:~-]*')


@pytest.fixture
def image_inputs(monkeypatch):
    monkeypatch.syspath_prepend(str(TOOL))
    import image_inputs
    return image_inputs


def instructions():
    """Join continued Dockerfile lines into (keyword, arguments) pairs."""
    rows, current = [], ''
    for line in (TOOL / 'Dockerfile').read_text().splitlines():
        if not current and (not line.strip() or line.lstrip().startswith('#')):
            continue
        current += line.rstrip('\\').strip() + ' '
        if not line.endswith('\\'):
            keyword, _, arguments = current.strip().partition(' ')
            rows.append((keyword.upper(), arguments))
            current = ''
    return rows


def arguments():
    return dict(value.split('=', 1) for keyword, value in instructions() if keyword == 'ARG')


def expand(text):
    values = arguments()
    return re.sub(r'\$\{(\w+)\}', lambda match: values[match.group(1)], text)


def test_every_external_base_is_bound_to_a_digest():
    stages, external = set(), []
    for keyword, value in instructions():
        if keyword == 'FROM':
            words = value.split()
            if words[0] not in stages:
                external.append(words[0])
            if len(words) == 3 and words[1].upper() == 'AS':
                stages.add(words[2])
    assert len(external) == 1
    assert re.fullmatch(r'debian:trixie-\d{8}-slim@sha256:[0-9a-f]{64}', external[0])


def test_packages_resolve_only_from_fixed_snapshots():
    rows = instructions()
    runs = [value for keyword, value in rows if keyword == 'RUN']
    sources, = [index for index, value in enumerate(runs)
                if '/etc/apt/sources.list.d/debian.sources' in value]
    updates = [index for index, value in enumerate(runs) if 'apt-get update' in value]
    assert updates and sources < min(updates)
    uris = re.findall(r'URIs: (\S+?)["\']', runs[sources])
    assert [expand(uri).rsplit('/', 2)[1:] for uri in uris] == [
        ['debian', arguments()['DEBIAN_SNAPSHOT']],
        ['debian-security', arguments()['DEBIAN_SECURITY_SNAPSHOT']],
    ]
    assert all(uri.startswith('http://snapshot.debian.org/archive/') for uri in uris)
    assert all(SNAPSHOT.fullmatch(arguments()[name])
               for name in ('DEBIAN_SNAPSHOT', 'DEBIAN_SECURITY_SNAPSHOT'))
    assert 'deb.debian.org' not in (TOOL / 'Dockerfile').read_text()
    # Later stages inherit these sources only by deriving from the first stage.
    froms = [value.split()[0] for keyword, value in rows if keyword == 'FROM']
    assert all(base == 'toolchain' for base in froms[1:])


def test_toolchain_and_python_install_exact_versions():
    install = next(value for keyword, value in instructions()
                   if keyword == 'RUN' and 'apt-get install' in value)
    words = shlex.split(install.split('--no-install-recommends', 1)[1].split('&&', 1)[0])
    pins = dict(expand(word).split('=', 1) for word in words)
    assert set(pins) == {'binutils-sh-elf', 'gcc-sh-elf', 'libnewlib-sh-elf-dev',
                         'python3', 'python3.13'}
    assert all(EXACT.fullmatch(version) for version in pins.values())


def test_image_inputs_cover_every_local_build_source(image_inputs):
    local = []
    for keyword, value in instructions():
        if keyword not in ('COPY', 'ADD'):
            continue
        words = value.split()
        flags = [word for word in words if word.startswith('--')]
        if any(flag.startswith('--from=') for flag in flags):
            continue
        sources = [word for word in words if not word.startswith('--')][:-1]
        for source in sources:
            if re.match(r'https?://', source):
                assert any(flag.startswith('--checksum=sha256:') for flag in flags)
            else:
                local.append(source)
    assert set(image_inputs.INPUTS) == {'Dockerfile', *local}
    assert len(image_inputs.INPUTS) == len(set(image_inputs.INPUTS))


def test_runtime_generation_labels_its_build(tmp_path, image_inputs):
    directory = tmp_path / 'bin'
    directory.mkdir()
    calls = tmp_path / 'docker-calls.jsonl'
    fake = directory / 'docker'
    fake.write_text(f'#!{sys.executable}\n'
        'import json,os,sys\n'
        "with open(os.environ['VQ_GENERATE_TEST_CALLS'],'a') as out:\n"
        " out.write(json.dumps(dict(args=sys.argv[1:],context=os.environ.get('DOCKER_CONTEXT'),"
        "host=os.environ.get('DOCKER_HOST')))+'\\n')\n")
    fake.chmod(0o755)
    environment = dict(os.environ, PATH=str(directory) + os.pathsep + os.environ['PATH'],
        VQ_GENERATE_TEST_CALLS=str(calls), VQ_SH_ELF_IMAGE='controlled-image',
        DOCKER_CONTEXT='unrelated-context', DOCKER_HOST='unrelated-host')
    result = subprocess.run([str(TOOL / 'generate-targets.sh'), '--check'], env=environment,
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    build, run = [json.loads(line) for line in calls.read_text().splitlines()]
    assert build['args'] == ['build', '--tag', 'controlled-image',
                             '--label', image_inputs.label(), str(TOOL)]
    assert run['args'][:2] == ['run', '--rm']
    assert f'type=bind,src={ROOT},dst=/workspace' in run['args']
    assert run['args'][-3:] == ['controlled-image', 'tools/sh-elf-run/generate_runtime_targets.py',
                                '--check']
    assert all(row['context'] == 'default' and row['host'] is None for row in (build, run))
