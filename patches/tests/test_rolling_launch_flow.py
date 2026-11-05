import re

import pytest

from patches import map_switching_assembly as common
from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_flow as flow
from patches import rolling_launch_layout as storage


@pytest.fixture(scope="module")
def layout():
    return storage.load_layout()


@pytest.fixture(scope="module")
def entries(layout):
    return [assembly.SOURCE_LABELS[key] for key in layout.code_region_by_key]


def _parsed(layout, key=None, old=None, new=None):
    """Parse every unit, with one replacement in the unit of key.

    The flow check runs on the parsed sources directly, so a mutation reaches
    it even where an ABI check of the unit refuses it first.
    """
    parsed = {}
    for unit in layout.assembly_units:
        path = storage.DEFAULT_MANIFEST.parent / unit.source
        text = path.read_text(encoding="utf-8")
        if unit.key == key:
            assert text.count(old) == 1, old
            text = text.replace(old, new)
        parsed[unit.key] = common.parse_source_text(
            text, path, unit.span.start, unit.span.end
        )
    return parsed


def _declarations(old=None, new=None):
    text = flow.DEFAULT_FLOW.read_text(encoding="utf-8")
    if old is not None:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return flow.load_declarations(text=text)


def test_tracked_sources_meet_every_declared_convention(layout, entries):
    functions, _externals, _continuations = flow.load_declarations()
    result = flow.validate_flow(_parsed(layout), entries)
    assert set(result) == {item.name for item in functions}


# The two defects that dcf2f367 fixes: the RPM gate built its flag bit with
# SHLL after the comparison, and the valid gate shifted the validator result
# through r3, which holds the sampled button through the gate chain.
@pytest.mark.parametrize("old,new,messages", (
    ("mov #0x40,r1\nshll r1\nmov.w @(0x4,r9),r0\nmov r0,r7\n"
     "mov.w @(0xc,r10),r0\ncmp/ge r0,r7\n",
     "mov.w @(0x4,r9),r0\nmov r0,r7\nmov.w @(0xc,r10),r0\ncmp/ge r0,r7\n"
     "mov #0x40,r1\nshll r1\n",
     (r"rolling-launch-engine\.s:\d+: T of shll at rolling-launch-engine\.s:\d+ "
      r"reaches the call of rl_gate_valid_pass_t of rolling_launch_engine",
      r"the T of cmp/ge reaches no consumer in rolling_launch_engine")),
    ("rl_gate_valid:\ncmp/pl r12\n", "rl_gate_valid:\nmov r12,r3\nshlr r3\n",
     (r"rolling_launch_engine reads r3 after rl_gate_valid_pass_t writes it",
      r"rolling_launch_engine reads r3 after rl_gate_valid writes it",
      r"rl_gate_valid: writes \[r3, r11, r13, t\], declared \[r11, r13, t\]")),
))
def test_historical_engine_defects_fail_the_check(layout, entries, old, new, messages):
    with pytest.raises(flow.FlowError) as error:
        flow.validate_flow(_parsed(layout, "engine", old, new), entries)
    for message in messages:
        assert re.search(message, str(error.value)), message


@pytest.mark.parametrize("key,old,new,message", (
    ("rpm", "mov r6,r4\nbsr rolling_launch_rpm_fraction",
     "mov r6,r4\nmov #0x0,r8\nbsr rolling_launch_rpm_fraction",
     r"rolling_launch_rpm_controller: writes \[r0, r1, r2, r3, r6, r7, r8, macl, t\]"),
    ("slot_validator", "tst r7,r7\nbt rl_val_return",
     "tst r7,r7\nmov #0x0,r0\ncmp/eq 0x1,r0\nbt rl_val_return",
     "the T of tst reaches no consumer in rolling_launch_slot_validator"),
    ("rpm", "mov.l r4,@-r15\nmov.l r5,@-r15\n",
     "mov.l r4,@-r15\nmov.l r5,@-r15\nmov.l r6,@-r15\n",
     "rolling_launch_rpm_controller leaves 1 stack words"),
    ("rpm", "mov.l @r15+,r5\nmov.l @r15+,r4\n", "mov.l @r15+,r5\nadd 0x4,r15\n",
     "stack access other than a long push or pop"),
    ("wrappers", "mov.l @(rolling_launch_engine_entry,pc),r0\njsr @r0\nnop\n"
     "lds.l @r15+,pr\n",
     "mov.l @(rolling_launch_engine_entry,pc),r0\njsr @r0\nnop\nmov.l @r15+,r1\n",
     "rolling_launch_periodic_wrapper returns without its entry PR"),
    ("engine", "bsr rl_window\nnop\nbra rl_gate_rpm\nnop",
     "bsr rl_window\nnop\nbt rl_gate_rpm\nnop",
     r"T of a call at rolling-launch-engine\.s:\d+ reaches the branch of "
     r"rolling_launch_engine"),
    # A call into another unit names the address of an entry label.
    ("spark_cut", "bsr 0x000D6780\n", "bsr 0x000D6782\n",
     r"rolling-launch-spark-cut\.s:\d+: 0x000d6782 is no label"),
    # RTS takes its return address from PR before its slot restores PR.
    ("wrappers", "mov.l @(rolling_launch_engine_entry,pc),r0\njsr @r0\nnop\n"
     "lds.l @r15+,pr\nrts\nnop\n",
     "mov.l @(rolling_launch_engine_entry,pc),r0\njsr @r0\nnop\nrts\nlds.l @r15+,pr\n",
     "rolling_launch_periodic_wrapper returns without its entry PR"),
    # BSR and JSR write the continuation to PR before their slot saves PR.
    ("engine", "rl_window:\nsts.l pr,@-r15\nmov #-0x41,r1\nand r1,r11\nmov r4,r7\n"
     "sub r6,r7\nmov.w @(0x1a,r10),r0\nextu.w r0,r0\nshlr8 r0\ncmp/ge r7,r0\n"
     "mov #0x40,r1\nmov #0x14,r2\nbsr rl_gate_valid_pass_t\nnop\n",
     "rl_window:\nmov #-0x41,r1\nand r1,r11\nmov r4,r7\n"
     "sub r6,r7\nmov.w @(0x1a,r10),r0\nextu.w r0,r0\nshlr8 r0\ncmp/ge r7,r0\n"
     "mov #0x40,r1\nmov #0x14,r2\nbsr rl_gate_valid_pass_t\nsts.l pr,@-r15\n",
     "rl_window returns without its entry PR"),
    ("wrappers", "rolling_launch_periodic_wrapper:\nsts.l pr,@-r15\n"
     "mov.l @(rolling_launch_periodic_stock,pc),r0\njsr @r0\nnop\n",
     "rolling_launch_periodic_wrapper:\n"
     "mov.l @(rolling_launch_periodic_stock,pc),r0\njsr @r0\nsts.l pr,@-r15\n",
     "rolling_launch_periodic_wrapper returns without its entry PR"),
))
def test_flow_check_refuses_a_changed_source(layout, entries, key, old, new, message):
    with pytest.raises(flow.FlowError, match=message):
        flow.validate_flow(_parsed(layout, key, old, new), entries)


# A tail callee returns to PR after the slot of JMP, so a restore in that
# slot keeps the entry PR, as does a restore before RTS.
def test_flow_check_accepts_a_restore_in_the_slot_of_a_tail_jump(layout, entries):
    old = ("lds.l @r15+,pr\nmov.l @(rl_rpm_control_publisher,pc),r0\njmp @r0\nnop\n")
    new = ("mov.l @(rl_rpm_control_publisher,pc),r0\njmp @r0\nlds.l @r15+,pr\n")
    result = flow.validate_flow(_parsed(layout, "rpm", old, new), entries)
    assert "rolling_launch_rpm_controller" in result


@pytest.mark.parametrize("old,new,message", (
    ('label = "rl_validate_config"\nreads = ["r10"]',
     'label = "rl_validate_config"\nreads = ["r4", "r10"]',
     r"rl_validate_config: reads \[r10\], declared \[r4, r10\]"),
    ('label = "rl_window"\nreads = ["r4", "r6", "r10", "r11", "r12", "r13"]',
     'label = "rl_window"\nreads = ["r4", "r6", "r10", "r11", "r12", "r13", "t"]',
     "rl_window: declares a T input that reaches no consumer"),
    ('[[external]]\naddress = 0x00021CE0\nname = "stock unsigned divider"\n'
     'reads = ["r0", "r1"]\nwrites = ["r0", "r1", "t"]\noutputs = ["r0"]\n', "",
     "stock unsigned divider|0x00021ce0 has no declared convention"),
    ('[[continuation]]', '[[external]]\naddress = 0x00000100\nname = "unused"\n\n'
     '[[continuation]]', "declared conventions reach no call or entry: unused"),
))
def test_flow_check_refuses_a_changed_declaration(layout, entries, old, new, message):
    with pytest.raises(flow.FlowError, match=message):
        flow.validate_flow(_parsed(layout), entries, _declarations(old, new))


@pytest.mark.parametrize("old,new,message", (
    ("schema_version = 1", "schema_version = 2", "schema_version = 1"),
    ('label = "rl_validate_config"\nreads = ["r10"]\n'
     'writes = ["r0", "r1", "r2", "r3", "r5", "r6", "r7", "t"]\noutputs = ["r0"]',
     'label = "rl_validate_config"\nreads = ["r10"]\n'
     'writes = ["r1", "r2", "r3", "r5", "r6", "r7", "t"]\noutputs = ["r0"]',
     "an output is not among the writes"),
    ('label = "rolling_launch_engine"\n'
     'writes = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "macl", "t"]\n'
     't_producers = ["dt"]',
     'label = "rolling_launch_engine"\n'
     'writes = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "macl", "t"]\n'
     't_producers = ["cmp/eq"]', "t_producers names a comparison"),
))
def test_declarations_refuse_an_invalid_entry(old, new, message):
    with pytest.raises(flow.FlowError, match=message):
        _declarations(old, new)
