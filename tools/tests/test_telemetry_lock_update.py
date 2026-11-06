"""The telemetry update derives the layout locks with the payload manifest."""

from dataclasses import replace
from functools import lru_cache
from pathlib import Path
import sys

import pytest

TOOL_DIR = Path(__file__).resolve().parents[1] / "sh-elf-run"
sys.path.insert(0, str(TOOL_DIR))
import generate_runtime_targets as generator

from patches import can_telemetry_assembly
from patches import can_telemetry_layout
from patches import can_telemetry_locks
from patches import can_telemetry_profile


@lru_cache(maxsize=None)
def tracked():
    layout = can_telemetry_layout.load_layout()
    return (
        layout,
        can_telemetry_layout.DEFAULT_MANIFEST.read_text(encoding="utf-8"),
        can_telemetry_assembly.DEFAULT_PAYLOADS.read_text(encoding="utf-8"),
        dict(can_telemetry_assembly.load_payloads(layout)),
    )


def assembler(blobs):
    """Stand in for the GNU unit assembler with fixed unit bytes."""
    def assemble(layout, parsed, build_dir, *, canonical=False):
        assert canonical
        assert set(parsed) == set(layout.assembly_unit_by_key)
        return dict(blobs)
    return assemble


@lru_cache(maxsize=None)
def changed_table():
    """Append one data byte to the pointer table, as an intentional change."""
    layout, _text, _manifest, blobs = tracked()
    unit = layout.assembly_unit_by_key["tables"]
    source = (can_telemetry_layout.DEFAULT_MANIFEST.parent / unit.source).read_text(
        encoding="utf-8"
    )
    changed = replace(
        layout, source_texts=(("tables", source.rstrip("\n") + "\n.byte 0x5A\n"),)
    )
    blobs = dict(blobs)
    blob = bytearray(blobs["tables"])
    blob[unit.data_bytes] = 0x5A
    blobs["tables"] = bytes(blob)
    return changed, blobs


def test_unchanged_inputs_reproduce_the_layout_and_manifest_exactly():
    layout, text, manifest, blobs = tracked()
    rendered, content, changed = generator.update_telemetry(
        layout, text, assemble=assembler(blobs)
    )
    assert rendered == text
    assert content == manifest
    assert changed == ()


def test_a_changed_unit_updates_its_locks_and_its_manifest_entry():
    _layout, text, manifest, _blobs = tracked()
    changed, blobs = changed_table()
    rendered, content, fields = generator.update_telemetry(
        changed, text, assemble=assembler(blobs)
    )
    assert [field for field, _before, _after in fields] == [
        "tables.expected_sha256",
        "tables.data_bytes",
        "expected_composition_sha256",
    ]
    differing = [
        old.split("=")[0].strip()
        for old, new in zip(text.splitlines(), rendered.splitlines())
        if old != new
    ]
    assert differing == ["expected_composition_sha256", "expected_sha256", "data_bytes"]
    assert content != manifest
    updated = replace(
        can_telemetry_locks.load_text(rendered), source_texts=changed.source_texts
    )
    assert generator._checked_telemetry(updated, assembler(blobs)) == content


def test_the_strict_path_refuses_stale_locks_and_names_the_update():
    changed, blobs = changed_table()
    with pytest.raises(
        can_telemetry_locks.LockError,
        match=r"tables\.expected_sha256, tables\.data_bytes, "
        r"expected_composition_sha256; after an intentional change run "
        r"tools/sh-elf-run/generate-targets\.sh --telemetry --update",
    ):
        generator._checked_telemetry(changed, assembler(blobs))


def test_the_update_writes_the_layout_and_the_manifest(tmp_path, monkeypatch, capsys):
    layout_path = tmp_path / "can-telemetry-layout.toml"
    manifest_path = tmp_path / "can-telemetry-payloads.toml"
    layout_path.write_text("old layout\n", encoding="utf-8")
    manifest_path.write_text("old manifest\n", encoding="utf-8")
    monkeypatch.setattr(generator.can_telemetry_layout, "DEFAULT_MANIFEST", layout_path)
    monkeypatch.setattr(generator.can_telemetry_assembly, "DEFAULT_PAYLOADS", manifest_path)
    monkeypatch.setattr(generator.can_telemetry_layout, "load_layout", lambda path: path)

    def update(layout, text):
        assert layout == layout_path and text == "old layout\n"
        return "new layout\n", "new manifest\n", (("tables.data_bytes", 10, 11),)

    monkeypatch.setattr(generator, "update_telemetry", update)
    assert generator.main(["--telemetry", "--update"]) == 0
    assert layout_path.read_text(encoding="utf-8") == "new layout\n"
    assert manifest_path.read_text(encoding="utf-8") == "new manifest\n"
    assert sorted(item.name for item in tmp_path.iterdir()) == sorted(
        (layout_path.name, manifest_path.name)
    )
    output = capsys.readouterr().out
    assert "lock tables.data_bytes: 10 -> 11" in output
    assert "changed_locks=1" in output


@pytest.mark.parametrize("flags", (
    ["--update"],
    ["--telemetry", "--update", "--check"],
    ["--rolling", "--update", "--check"],
    ["--rolling", "--telemetry", "--update"],
))
def test_an_update_names_one_family_and_excludes_check(flags):
    with pytest.raises(SystemExit):
        generator.main(flags)


def test_a_stale_profile_projection_names_its_generator(tmp_path):
    outputs = {
        name: tmp_path / path.name
        for name, path in (
            ("tables", can_telemetry_profile.DEFAULT_TABLES),
            ("schema", can_telemetry_profile.DEFAULT_SCHEMA),
            ("identity", can_telemetry_profile.DEFAULT_IDENTITY),
        )
    }
    can_telemetry_profile.generate(**outputs)
    can_telemetry_profile.generate(**outputs, check=True)
    outputs["identity"].write_text("stale\n", encoding="utf-8")
    with pytest.raises(ValueError, match="regenerate them with "
                       + can_telemetry_profile.GENERATE_COMMAND):
        can_telemetry_profile.generate(**outputs, check=True)
