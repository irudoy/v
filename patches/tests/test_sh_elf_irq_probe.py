"""An injected exception cannot write its frame into allocated ELF storage."""

import importlib
from pathlib import Path

import pytest

from patches.tests.test_sh_elf_storage_layout import image


TOOL = Path(__file__).resolve().parents[2] / 'tools/sh-elf-run'


@pytest.mark.parametrize('kind', ('data', 'bss', 'virtual', 'physical'))
@pytest.mark.parametrize('offset', (-16, -1))
def test_irq_stack_collision_stops_before_an_enabled_run(monkeypatch, kind, offset):
    monkeypatch.syspath_prepend(str(TOOL))
    verifier = importlib.import_module('verify_simulator_irq')
    storage = importlib.import_module('elf_storage_layout')
    sp = 0x00170030
    address = sp + offset
    if kind in ('data', 'bss'):
        blob = image(section=(address, 4, 8 if kind == 'bss' else 1, 2))
    else:
        addresses = (address, 0x110000) if kind == 'virtual' else (0x110000, address)
        blob = image(load=(*addresses, 0, 4))
    controls = []

    def compiled(directory, case):
        elf = directory / 'probe.elf'
        elf.write_bytes(blob)
        return elf

    def control(elf, request=None):
        assert request is None, 'an overlapping frame reaches an enabled simulator'
        controls.append(elf)
        return None, dict(hits=0, expected_sp=sp)

    def enabled(*args):
        pytest.fail('an overlapping frame reaches an enabled probe')

    monkeypatch.setattr(verifier, 'compile_probe', compiled)
    monkeypatch.setattr(verifier, 'symbols', lambda elf: dict(irq_stack_bytes=16))
    monkeypatch.setattr(verifier, 'run_probe', control)
    monkeypatch.setattr(verifier, 'check_positive', enabled)
    with pytest.raises(storage.ELFStorageError, match='intersects declared RAM'):
        verifier.verify()
    assert len(controls) == 1
