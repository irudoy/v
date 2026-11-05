"""Identify the firmware-gate image by the build inputs that define it."""

import hashlib
from pathlib import Path


TOOL = Path(__file__).resolve().parent
LABEL = 'vhrev.sh-elf-run.inputs'
# The Dockerfile and every local file that it copies into an image stage.
INPUTS = ('Dockerfile', 'gnu16.3-sh-pc-observer.patch',
          'gnu16.3-sh-high-ram-alias.patch',
          'gnu16.3-sh-irq-injection.patch')


def fingerprint(directory=TOOL):
    digest = hashlib.sha256()
    for name in INPUTS:
        content = (Path(directory) / name).read_bytes()
        digest.update(f'{name}\0{len(content)}\0'.encode())
        digest.update(content)
    return 'sha256:' + digest.hexdigest()


def label(directory=TOOL):
    """Return the `docker build --label` value for the current inputs."""
    return LABEL + '=' + fingerprint(directory)


if __name__ == '__main__':
    print(label())
