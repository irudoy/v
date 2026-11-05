"""High-RAM probe collisions are rejected before any simulator execution."""

import importlib
from pathlib import Path

import pytest

from patches.tests.test_sh_elf_storage_layout import image


TOOL = Path(__file__).resolve().parents[2] / 'tools/sh-elf-run'


@pytest.mark.parametrize('address', (0x01000000, 0x0100FFFF, 0x01010000))
@pytest.mark.parametrize('kind', ('data', 'bss', 'virtual', 'physical'))
def test_probe_checks_alias_window_and_canary_before_execution(
    monkeypatch, address, kind,
):
    monkeypatch.syspath_prepend(str(TOOL))
    verifier = importlib.import_module('verify_simulator_memory')
    storage = importlib.import_module('elf_storage_layout')
    if kind in ('data', 'bss'):
        blob = image(section=(address, 4, 8 if kind == 'bss' else 1, 2))
    else:
        locations = (address, 0x110000) if kind == 'virtual' else (0x110000, address)
        blob = image(load=(*locations, 0, 4))
    compiled = []

    def compile_only(command, **kwargs):
        assert command[0] == verifier.base.GCC, 'overlapping probe reached a simulator'
        Path(command[-1]).write_bytes(blob)
        compiled.append(command)

    monkeypatch.setattr(verifier.base, 'run_command', compile_only)
    with pytest.raises(storage.ELFStorageError, match='intersects declared RAM'):
        verifier.verify()
    assert len(compiled) == 1
