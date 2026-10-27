"""Telemetry byte locks follow from the unit sources, blobs and base."""

from dataclasses import replace
from functools import lru_cache
import re

import pytest

from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_locks


@lru_cache(maxsize=None)
def tracked():
    return (
        can_telemetry_layout.load_layout(),
        can_telemetry_layout.DEFAULT_MANIFEST.read_text(encoding="utf-8"),
    )


@lru_cache(maxsize=None)
def changed_table():
    """Append one data byte to the generated pointer table.

    The blob carries the byte in place of fill, as the GNU assembler would.
    """
    layout, _text = tracked()
    unit = layout.assembly_unit_by_key["tables"]
    source = (can_telemetry_layout.DEFAULT_MANIFEST.parent / unit.source).read_text(
        encoding="utf-8"
    )
    changed = replace(
        layout,
        source_texts=(("tables", source.rstrip("\n") + "\n.byte 0x5A\n"),),
    )
    blobs = dict(can_telemetry_assembly.load_payloads(layout))
    blob = bytearray(blobs["tables"])
    assert blob[unit.data_bytes] == unit.fill
    blob[unit.data_bytes] = 0x5A
    blobs["tables"] = bytes(blob)
    counted = can_telemetry_locks.counted(changed)
    parsed = can_telemetry_assembly.validate_assembly_sources(counted)
    locks = can_telemetry_locks.derive(counted, parsed, blobs)
    return changed, counted, blobs, locks


def test_tracked_payloads_reproduce_the_tracked_locks():
    layout, _text = tracked()
    parsed = can_telemetry_assembly.validate_assembly_sources(layout)
    blobs = can_telemetry_assembly.load_payloads(layout)
    locks = can_telemetry_locks.derive(layout, parsed, blobs)
    assert locks == can_telemetry_locks.locks_of(layout)
    assert can_telemetry_locks.changes(layout, locks) == ()


def test_tracked_sources_carry_the_tracked_counts():
    layout, _text = tracked()
    assert can_telemetry_locks.counted(layout) == layout


def test_rendering_the_tracked_locks_keeps_every_byte():
    layout, text = tracked()
    locks = can_telemetry_locks.locks_of(layout)
    assert can_telemetry_locks.render(text, locks) == text
    assert can_telemetry_locks.load_text(text) == layout


def test_changed_unit_derives_locks_that_the_strict_path_accepts():
    changed, counted, blobs, locks = changed_table()
    tables = changed.assembly_unit_by_key["tables"]
    assert counted.assembly_unit_by_key["tables"].data_bytes == tables.data_bytes + 1
    assert [field for field, _before, _after in can_telemetry_locks.changes(
        changed, locks
    )] == [
        "tables.expected_sha256",
        "tables.data_bytes",
        "expected_composition_sha256",
    ]
    locked = can_telemetry_locks.apply(changed, locks)
    result = can_telemetry_compose.compose(layout=locked, blobs=blobs)
    assert result.sha256 == locks.expected_composition_sha256
    with pytest.raises(ValueError, match="tables: blob SHA-256 is"):
        can_telemetry_compose.compose(layout=counted, blobs=blobs)
    stale = replace(
        locked, expected_composition_sha256=changed.expected_composition_sha256
    )
    with pytest.raises(ValueError, match="default telemetry composition SHA-256"):
        can_telemetry_compose.compose(layout=stale, blobs=blobs)


def test_rendered_layout_differs_in_the_changed_lock_lines_alone():
    _changed, _counted, _blobs, locks = changed_table()
    layout, text = tracked()
    rendered = can_telemetry_locks.render(text, locks)
    before = text.splitlines(keepends=True)
    after = rendered.splitlines(keepends=True)
    assert len(before) == len(after)
    differing = [
        (old, new) for old, new in zip(before, after) if old != new
    ]
    assert [old.split("=")[0].strip() for old, _new in differing] == [
        "expected_composition_sha256",
        "expected_sha256",
        "data_bytes",
    ]
    assert can_telemetry_locks.load_text(rendered) == can_telemetry_locks.apply(
        layout, locks
    )


@pytest.mark.parametrize(
    ("edit", "message"),
    (
        (
            lambda text: text.replace("instruction_count = 48\n", "", 1),
            r"unit 'wrappers' lacks \['instruction_count'\]",
        ),
        (
            lambda text: text.replace(
                "data_bytes = 42\n", "data_bytes = 42\ndata_bytes = 42\n", 1
            ),
            "wrappers.data_bytes is declared twice",
        ),
        (
            lambda text: text.replace(
                "instruction_count = 48", "instruction_count = 0x30", 1
            ),
            "instruction_count is not a literal lock value",
        ),
        (
            lambda text: text.replace('key = "wrappers"', 'key = "spare"', 1),
            "unit 'spare' has no lock",
        ),
        (
            lambda text: text.replace(
                '[[assembly_unit]]\nkey = "wrappers"',
                '[[assembly_unit]]\ndata_bytes = 42\nkey = "wrappers"',
                1,
            ),
            "data_bytes precedes the unit key",
        ),
        (
            lambda text: re.sub(
                r'expected_composition_sha256 = "[0-9a-f]{64}"\n', "", text
            ),
            "expected_composition_sha256 is not declared",
        ),
    ),
)
def test_rendering_refuses_an_ambiguous_layout(edit, message):
    layout, text = tracked()
    edited = edit(text)
    assert edited != text
    with pytest.raises(can_telemetry_locks.LockError, match=message):
        can_telemetry_locks.render(edited, can_telemetry_locks.locks_of(layout))


def test_rendering_refuses_a_lock_without_a_layout_unit():
    layout, text = tracked()
    locks = can_telemetry_locks.locks_of(layout)
    spare = replace(locks.units[0], key="spare")
    with pytest.raises(
        can_telemetry_locks.LockError,
        match=r"locked units \['spare'\] are not declared",
    ):
        can_telemetry_locks.render(text, replace(locks, units=locks.units + (spare,)))
    with pytest.raises(can_telemetry_locks.LockError, match="differ from the layout units"):
        can_telemetry_locks.apply(layout, replace(locks, units=locks.units + (spare,)))


def test_derivation_refuses_incomplete_or_resized_blobs():
    layout, _text = tracked()
    parsed = can_telemetry_assembly.validate_assembly_sources(layout)
    blobs = dict(can_telemetry_assembly.load_payloads(layout))
    incomplete = {key: value for key, value in blobs.items() if key != "tables"}
    with pytest.raises(
        can_telemetry_locks.LockError, match=r"blob set differs; missing=\['tables'\]"
    ):
        can_telemetry_locks.derive(layout, parsed, incomplete)
    with pytest.raises(
        can_telemetry_locks.LockError, match="tables: blob has 511 bytes, expected 512"
    ):
        can_telemetry_locks.derive(
            layout, parsed, {**blobs, "tables": blobs["tables"][:-1]}
        )
