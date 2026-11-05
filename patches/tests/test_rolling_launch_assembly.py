from dataclasses import replace

import pytest

from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_layout as storage


@pytest.fixture(scope="module")
def layout():
    return storage.load_layout()


def _with_source(layout, key, old, new):
    unit = layout.assembly_unit_by_key[key]
    text = (storage.DEFAULT_MANIFEST.parent / unit.source).read_text()
    assert text.count(old) == 1, old
    return replace(layout, source_texts=((key, text.replace(old, new)),))


def test_tracked_sources_pass_every_abi_check(layout):
    parsed = assembly.validate_assembly_sources(layout)
    assert set(parsed) == set(layout.assembly_unit_by_key)


@pytest.mark.parametrize("key,old,new,message", (
    ("wrappers", "mov #0x8,r2", "mov #0x7,r2", "startup wrapper must clear"),
    ("engine", "mov r8,r1\nmov #0x0,r0\nmov #0x7,r2",
     "mov r8,r1\nmov #0x0,r0\nmov #0x6,r2", "corrupt-state recovery"),
    ("engine", "mov #0x1e,r0\nmov.w r2,@(r0,r8)", "mov #0x1e,r0\nmov.b r2,@(r0,r8)",
     "corrupt-state recovery"),
    ("engine", "tst 0x2,r0\nbf rl_gate_table_valid",
     "tst 0x1,r0\nbf rl_gate_table_valid", "keeps CONFIG_VALID"),
    ("speed_controller", "add 0x28,r0", "add 0x2a,r0", "slot gain"),
    ("rpm", "cmp/pz r4", "cmp/pl r4", "divider leaf"),
    ("actuation", "tst 0x1,r0", "tst 0x2,r0", "CONFIG_VALID"),
    ("actuation", "mov r1,r0\nmov.w r0,@(0x1e,r7)\nmov r5,r0\nmov.w r0,@(0x1a,r4)",
     "mov r5,r0\nmov.w r0,@(0x1a,r4)\nmov r1,r0\nmov.w r0,@(0x1e,r7)", "q last"),
    ("slot_validator", "mov #0x5,r5", "mov #0x4,r5", "slot or table bounds"),
    ("state_check", "and 0x7f,r0\nmov.b @(r0,r7),r0\nbra rl_check_byte_compare\nnop\n"
     "rl_check_byte_base:\nmov.b @(r0,r6),r0\nrl_check_byte_compare:\nextu.b r0,r0\n"
     "mov.b @r2+,r1\ncmp/hi r1,r0\nbt rl_check_fail_near",
     "and 0x7f,r0\nmov.b @(r0,r7),r0\nbra rl_check_byte_compare\nnop\n"
     "rl_check_byte_base:\nmov.b @(r0,r6),r0\nrl_check_byte_compare:\nextu.b r0,r0\n"
     "mov.b @r2+,r1\ncmp/hi r1,r0\nbt rl_check_fail", "8-bit branch reach"),
    ("speed_controller", "mov.w r0,@(0x2,r7)\nldc r6,sr", "ldc r6,sr\nmov.w r0,@(0x2,r7)",
     "error pair is not one masked store group"),
    ("rpm", "mov.w r0,@(0x2,r7)\nldc r3,sr", "ldc r3,sr\nmov.w r0,@(0x2,r7)",
     "error pair is not one masked store group"),
    ("actuation", "mov.l r0,@-r15\nor 0xf0,r0\nldc r0,sr\nmov.l @(rl_act_extension_address,pc),r7",
     "mov.l r0,@-r15\nor 0x00,r0\nldc r0,sr\nmov.l @(rl_act_extension_address,pc),r7",
     "store the law under the mask"),
    ("actuation", "rl_act_ignition_stock:\nmov r4,r5\n", "rl_act_ignition_stock:\nmov r4,r6\n",
     "stock publication differs"),
    ("engine", "mov.w r0,@(0x1e,r9)\nldc r6,sr", "ldc r6,sr\nmov.w r0,@(0x1e,r9)",
     "wire views under one mask"),
    ("engine", "mov r5,r0\nmov.b r0,@(0x4,r8)\nmov.b @(0x3,r10),r0\nmov.b r0,@(0x5,r8)",
     "mov.b @(0x3,r10),r0\nmov.b r0,@(0x5,r8)\nmov r5,r0\nmov.b r0,@(0x4,r8)",
     "mode after the map"),
    ("engine", "rl_abort:\nmov #0x2,r0\nmov.b r0,@r8\nmov r2,r0\nmov.b r0,@(0x1,r8)",
     "rl_abort:\nmov r2,r0\nmov.b r0,@(0x1,r8)\nmov #0x2,r0\nmov.b r0,@r8",
     "abort must leave ACTIVE with its first store"),
))
def test_abi_checks_reject_a_changed_contract(layout, key, old, new, message):
    with pytest.raises(ValueError, match=message):
        assembly.validate_assembly_sources(_with_source(layout, key, old, new))


def test_entry_literals_must_name_the_labels_of_their_units(layout, monkeypatch):
    literals = assembly._expected_long_literals()
    literals["actuation"]["rl_act_views"] = 0x000D718C
    monkeypatch.setattr(assembly, "_expected_long_literals", lambda: literals)
    changed = _with_source(layout, "actuation", ".long 0x000D7190", ".long 0x000D718C")
    with pytest.raises(ValueError, match="rl_act_views does not name state_check"):
        assembly.validate_assembly_sources(changed)


def test_engine_runs_the_masked_entry_of_the_record_check(layout, monkeypatch):
    literals = assembly._expected_long_literals()
    literals["engine"]["rl_state_check_entry"] = 0x000D7000
    monkeypatch.setattr(assembly, "_expected_long_literals", lambda: literals)
    changed = _with_source(layout, "engine", ".long 0x000D7008", ".long 0x000D7000")
    with pytest.raises(ValueError, match="rolling_launch_state_check_masked"):
        assembly.validate_assembly_sources(changed)
