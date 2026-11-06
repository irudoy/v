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


def redirected(tmp_path, monkeypatch):
    """Point the rolling layout and manifest of the CLI at temporary files."""
    layout_path = tmp_path / "rolling-launch-layout.toml"
    manifest_path = tmp_path / "rolling-launch-payloads.toml"
    layout_path.write_text("old layout\n", encoding="utf-8")
    manifest_path.write_text("old manifest\n", encoding="utf-8")
    monkeypatch.setattr(generator.rolling_launch_layout, "DEFAULT_MANIFEST", layout_path)
    monkeypatch.setattr(generator.rolling_launch_assembly, "DEFAULT_PAYLOADS", manifest_path)
    monkeypatch.setattr(generator.rolling_launch_layout, "load_layout", lambda path: path)
    return layout_path, manifest_path


def tracked_bytes():
    return storage.DEFAULT_MANIFEST.read_bytes(), assembly.DEFAULT_PAYLOADS.read_bytes()


def test_the_rolling_update_writes_the_layout_and_the_manifest(tmp_path, monkeypatch, capsys):
    tracked_before = tracked_bytes()
    layout_path, manifest_path = redirected(tmp_path, monkeypatch)

    def update(layout, text):
        assert layout == layout_path and text == "old layout\n"
        return "new layout\n", "new manifest\n", [
            ("spark_cut.sha256", "1" * 64, "2" * 64),
            ("composition.sha256", "3" * 64, "4" * 64),
        ]

    monkeypatch.setattr(generator, "update_rolling", update)
    assert generator.main(["--rolling", "--update"]) == 0
    assert layout_path.read_text(encoding="utf-8") == "new layout\n"
    assert manifest_path.read_text(encoding="utf-8") == "new manifest\n"
    assert sorted(item.name for item in tmp_path.iterdir()) == sorted(
        (layout_path.name, manifest_path.name)
    )
    output = capsys.readouterr().out
    assert f"lock spark_cut.sha256: {'1' * 64} -> {'2' * 64}" in output
    assert f"lock composition.sha256: {'3' * 64} -> {'4' * 64}" in output
    assert (f"status=PASS output={manifest_path} layout={layout_path} "
            "family=rolling changed_locks=2") in output
    monkeypatch.undo()
    assert tracked_bytes() == tracked_before


def test_a_refused_rolling_update_writes_nothing(tmp_path, monkeypatch, capsys):
    layout_path, manifest_path = redirected(tmp_path, monkeypatch)

    def update(layout, text):
        raise ValueError("spark_cut: JMP target disagrees with its machine word")

    monkeypatch.setattr(generator, "update_rolling", update)
    with pytest.raises(SystemExit) as refusal:
        generator.main(["--rolling", "--update"])
    assert refusal.value.code == 2
    assert layout_path.read_text(encoding="utf-8") == "old layout\n"
    assert manifest_path.read_text(encoding="utf-8") == "old manifest\n"
    assert sorted(item.name for item in tmp_path.iterdir()) == sorted(
        (layout_path.name, manifest_path.name)
    )
    assert "JMP target disagrees with its machine word" in capsys.readouterr().err


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
