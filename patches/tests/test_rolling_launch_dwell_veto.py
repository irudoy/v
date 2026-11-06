"""The arming veto consumes one q word and preserves the stock divider ABI."""

from dataclasses import replace

import pytest

from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_layout as storage


@pytest.mark.parametrize("key,old,new,message", (
    ("spark_cut", "mov.w @(0x1a,r5),r0", "mov.b @(0x1a,r5),r0", "one aligned q word"),
    ("spark_cut", "mov.b @(0x1,r3),r0", "mov.b @(0x2,r3),r0", "armed cylinder"),
    ("spark_cut", "ldc r0,sr\nmov r5,r0", "ldc r6,sr\nmov r5,r0", "commit is not masked"),
    ("spark_cut", "lds.l @r15+,pr", "add 0x4,r15", "preserve the divider"),
    ("spark_cut", "mov.w r0,@(0x18,r3)", "mov.b r0,@(0x18,r3)", "store contract"),
    ("spark_events", "or 0xf0,r0", "or 0x80,r0", "not masked"),
    ("spark_events", "mov.b r0,@r4\nmov.b r0,@(0x3,r4)",
     "mov.b r0,@r4\nnop", "invalidate the reset cache"),
    ("spark_events", "rl_event_cache_store:\nmov.b r0,@(0x3,r4)",
     "rl_event_cache_store:\nnop", "publish its cache"),
    ("ignition_adapter", ".long 0x000D6348", ".long 0x000D6248", "retired schema-5"),
))
def test_veto_source_audit_rejects_a_changed_contract(key, old, new, message):
    layout = storage.load_layout()
    unit = layout.assembly_unit_by_key[key]
    source = (storage.DEFAULT_MANIFEST.parent / unit.source).read_text()
    assert source.count(old) >= 1
    changed = replace(layout, source_texts=((key, source.replace(old, new, 1)),))
    with pytest.raises(ValueError, match=message):
        assembly.validate_assembly_sources(changed)


def test_veto_helper_consumes_only_its_declared_rom_reserve():
    layout = storage.load_layout()
    storage.validate_reservations(layout)
    helper = layout.assembly_unit_by_key["spark_events"]
    assert (helper.span.start, helper.span.end) == (0xD6268, 0xD6320)
    assert (layout.ram.extension.start, layout.ram.extension.end) == (0xFFFF6100, 0xFFFF6120)
