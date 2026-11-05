"""Protect the shared command and caller ABI of the ignition adapter."""

from pathlib import Path

import pytest

from patches import map_switching_assembly as common
from patches import rolling_launch_assembly as assembly


SOURCE = Path(assembly.__file__).with_name("rolling-launch-ignition-adapter.s")


def parse(source):
    return common.parse_source_text(source, SOURCE, 0xD3EA0, 0xD3F60)


def test_adapter_publishes_before_applying_the_returned_command():
    parsed = parse(SOURCE.read_text())
    assembly._validate_16_bit_source_forms(parsed)
    common._validate_delay_slots(parsed)
    assembly._validate_ignition_abi(parsed)
    assert common._long_literals(parsed) == assembly._expected_long_literals()["ignition_adapter"]


@pytest.mark.parametrize("old,new", (
    ("mov r5,r4", "mov r4,r4"),
    ("mov r5,r0\nmov.l @(rl_ign_command_address,pc),r1\nmov.b r0,@r1\n", ""),
    ("lds.l @r15+,macl", "add 0x4,r15"),
    ("mov.l @r15+,r6", "mov.l @r15+,r5"),
    ("cmp/hi r2,r3", "cmp/hi r3,r2"),
    ("mov #0x28,r2", "mov #0x29,r2"),
    ("cmp/hi r2,r0\nbf rl_ign_publish", "cmp/hi r2,r0\nbt rl_ign_publish"),
    ("mov.b @(0x4,r2),r0", "mov.b @(0x3,r2),r0"),
    ("mov.b @(r0,r1),r0", "mov.b @(0x3,r2),r0"),
))
def test_adapter_rejects_command_or_caller_contract_damage(old, new):
    source = SOURCE.read_text()
    assert source.count(old) == 1
    with pytest.raises(ValueError, match="ignition adapter"):
        assembly._validate_ignition_abi(parse(source.replace(old, new)))


def test_adapter_rejects_storing_the_candidate_before_publication():
    source = SOURCE.read_text()
    call = "mov.l @(rl_ign_publisher,pc),r0\njsr @r0\nnop\n"
    store = "mov r5,r0\nmov.l @(rl_ign_command_address,pc),r1\nmov.b r0,@r1\n"
    assert call + store in source
    with pytest.raises(ValueError, match="apply the publisher return"):
        assembly._validate_ignition_abi(parse(source.replace(call + store, store + call)))
