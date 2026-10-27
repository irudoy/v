"""The firmware-gate image resolves from frozen inputs."""

from pathlib import Path
import re
import shlex


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools/sh-elf-run'
SNAPSHOT = re.compile(r'\d{8}T\d{6}Z')
EXACT = re.compile(r'[0-9][0-9A-Za-z.+:~-]*')


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
