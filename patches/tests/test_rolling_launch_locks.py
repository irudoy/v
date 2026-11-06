"""GNU-derived Rolling Launch locks retain the strict machine-byte checks."""

from dataclasses import replace
from pathlib import Path
import sys

import pytest

from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_layout as storage

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "sh-elf-run"))
import generate_runtime_targets as generator


def tracked():
    layout = storage.load_layout()
    return layout, storage.DEFAULT_MANIFEST.read_text(), assembly.load_payloads(layout)


def test_rolling_update_is_byte_identical_when_locks_match():
    layout, text, blobs = tracked()
    rendered, payloads, changed = generator.update_rolling(
        layout, text, lambda *args, **kwargs: blobs,
    )
    assert rendered == text
    assert payloads == assembly.DEFAULT_PAYLOADS.read_text()
    assert changed == []


def test_rolling_update_replaces_stale_locks_without_enabling_hold(tmp_path):
    layout, text, blobs = tracked()
    units = tuple(replace(unit, expected_sha256="0" * 64) for unit in layout.assembly_units)
    stale = replace(layout, assembly_units=units, expected_composition_sha256="0" * 64,
                    hold_actuator=False)
    assert text.count("hold_actuator = true") == 1
    stale_text = text.replace(layout.expected_composition_sha256, "0" * 64).replace(
        "hold_actuator = true", "hold_actuator = false")
    for unit in layout.assembly_units:
        stale_text = stale_text.replace(unit.expected_sha256, "0" * 64)
    rendered, payloads, changed = generator.update_rolling(
        stale, stale_text, lambda *args, **kwargs: blobs,
    )
    path = tmp_path / "rolling-layout.toml"
    path.write_text(rendered)
    # The generator rewrites the locks and leaves the actuator declaration unset.
    updated = storage.load_layout(path)
    assert updated == replace(layout, hold_actuator=False)
    assert not updated.hold_actuator
    assert payloads == assembly.DEFAULT_PAYLOADS.read_text()
    assert len(changed) == len(units) + 1


def test_rolling_update_rejects_a_machine_jump_that_disagrees_with_source():
    layout, text, blobs = tracked()
    parsed = assembly.validate_assembly_sources(layout)["spark_cut"]
    jump = next(item for item in parsed.statements if item.text.lower() == "jmp @r0")
    unit = layout.assembly_unit_by_key["spark_cut"]
    damaged = bytearray(blobs["spark_cut"])
    offset = jump.address - unit.span.start
    damaged[offset:offset + 2] = bytes.fromhex("000b")
    blobs["spark_cut"] = bytes(damaged)
    with pytest.raises(ValueError, match="JMP.*machine word"):
        generator.update_rolling(layout, text, lambda *args, **kwargs: blobs)
