"""Census arguments that the delay slot of the call writes.

`tools/ghidra/ResolveAccessors.java` evaluates the symbolic fallback (`sp`),
the copy match (`copy`) and the backtrack baseline (`bt_r4`..`bt_r6`) of such
a register after the slot. A slot that loads a constant or a literal fixes the
value; an extension bounds it. Any other write in the slot leaves the register
without a fallback value.
"""

import csv

import pytest

from kb import derive, l0, repo, sh2, sites

LAYOUTS = ("7mfk", "jk00c", "jk00d", "jk78c", "1nd", "1me3b")


def census_rows(layout):
    base = repo.ROOT / repo.L0 / layout
    for kernel in l0.census(layout).kernels:
        with (base / l0.Census.file(kernel)).open(newline="", encoding="utf-8") as source:
            yield from csv.DictReader(source)


def produced(slot, data):
    """The value that the slot loads from its own operands, or None."""
    if slot.value and slot.value[0] == "const":
        return slot.value[1]
    if slot.value and slot.value[0] == "pool":
        _, pool, size = slot.value
        value = int.from_bytes(data[pool:pool + size], "big")
        return sh2.sext(value, 16) & sh2.MASK if size == 2 else value
    return None


def evaluated(slot):
    """Whether the export gives the slot result a value: mov Rm,Rn, mov #imm,
    a PC-relative load, add #imm, or an extension. A post-increment or
    pre-decrement access also adds to its register, but leaves no value."""
    if not slot.value:
        return False
    kind = slot.value[0]
    return kind in ("const", "pool", "copy", "extu", "exts") or (
        kind == "addi" and slot.word >> 12 == 0x7)


def bounded(slot, value):
    if slot.value and slot.value[0] == "extu":
        return value < 1 << slot.value[1]
    if slot.value and slot.value[0] == "exts":
        half = 1 << (slot.value[1] - 1)
        return value < half or value > sh2.MASK - half
    return True


@pytest.mark.parametrize("layout", LAYOUTS)
def test_slot_written_arguments_hold_the_value_after_the_slot(layout):
    data = derive.image_bytes(repo.layout(layout))
    stale = []
    for row in census_rows(layout):
        slot = sites.delay_slot(data, int(row["callsite"], 16), sites.CALL_TRANSFERS)
        if slot is None:
            continue
        value = produced(slot, data)
        for register in sorted(slot.writes & {4, 5, 6, 7}):
            cells = []
            if register < 7 and row[f"bt_r{register}"]:
                cells.append(("bt", int(row[f"bt_r{register}"], 16)))
            if row[f"k{register}"] in ("sp", "copy") and row[f"df_r{register}"]:
                cells.append((row[f"k{register}"], int(row[f"df_r{register}"], 16)))
            for kind, cell in cells:
                if (value is not None and cell != value) or not bounded(slot, cell) or (
                        kind == "bt" and value is None) or (
                        kind != "bt" and not evaluated(slot)):
                    stale.append((row["callsite"], register, kind, f"{cell:08x}"))
    assert stale == []


def census_row(layout, callsite):
    return next(row for row in census_rows(layout) if row["callsite"] == callsite)


def test_a_stack_copy_in_the_slot_reaches_the_copied_rom_source():
    # mov r15,r4 in the slot of the call at 00068d3a passes the stack buffer
    # that the copy helper 00022558 fills from 000237ac.
    row = census_row("7mfk", "00068d3a")
    assert (row["df_r4"], row["k4"], row["bt_r4"]) == ("000237ac", "copy", "")


def test_a_constant_in_the_slot_is_also_the_backtrack_baseline():
    # mov #0,r6 in the slot of the call at 0007383c sets the third argument.
    row = census_row("7mfk", "0007383c")
    assert (row["df_r6"], row["k6"], row["bt_r6"]) == ("00000000", "const", "00000000")


def test_a_register_copy_in_the_slot_passes_the_copied_value():
    # add r13,r14 at 000aba90 forms axis 0000fc5c, and mov r14,r5 in the slot
    # of the call at 000aba98 passes it.
    row = census_row("1me3b", "000aba98")
    assert (row["df_r5"], row["k5"], row["bt_r5"]) == ("0000fc5c", "sp", "")


def test_an_extension_in_the_slot_applies_to_the_fallback():
    # mov.w at 0005f5c4 loads ffffb400, and extu.w r6,r6 in the slot of the
    # call at 0005f5cc passes 0000b400.
    row = census_row("1me3b", "0005f5cc")
    assert (row["df_r6"], row["k6"], row["bt_r6"]) == ("0000b400", "sp", "")


def test_an_extension_of_a_memory_word_in_the_slot_leaves_no_value():
    # extu.w r7,r6 in the slot of the call at 00069590 extends the word that
    # mov.w at 0006958a reads from ffff31dc.
    row = census_row("7mfk", "00069590")
    assert (row["df_r6"], row["bt_r6"]) == ("", "")


def test_a_2d_implicit_entry_passes_its_base_through_the_kernel_slot():
    # 00026040 loads the shift kernel 00026ae0 from its pool and calls it once
    # for each input; its readers pass the base of the map in r4.
    rows = {row["callsite"]: row for row in census_rows("7mfk")
            if row["kernel"] == "00026ae0"}
    assert {site: (row["wrapper"], row["df_r4"]) for site, row in rows.items()} == {
        "0005258c": ("00026040", "0000a8ea"),
        "000526c2": ("00026040", "00009eda"),
    }


def test_a_fused_2d_implicit_entry_is_its_own_kernel():
    # 000288b4 computes both fractions and reads the cells itself; the reader
    # passes the 1ME3B copy of the 00009eda surface of 7mfk.
    rows = [row for row in census_rows("1me3b") if row["callsite"] == "0007ee7e"]
    assert [(row["kernel"], row["wrapper"], row["df_r4"]) for row in rows] == [
        ("000288b4", "000288b4", "00009ef4")]
