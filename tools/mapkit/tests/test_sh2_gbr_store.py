"""GBR-relative word stores in the stock-code interpreter."""

from itertools import product

import pytest

from tools.mapkit.sh2_interpreter import MASK, Sh2


@pytest.mark.parametrize("base, displacement, value", tuple(product(
    (0x100, 0xFFFF8D58, 0xFFFFFF00),
    (0, 10, 255),
    (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0xFFFF0000, 0x1234ABCD),
)))
def test_gbr_word_store_uses_scaled_unsigned_displacement_and_low_word(
    base, displacement, value,
):
    machine = Sh2((0xC100 | displacement).to_bytes(2, "big"))
    machine.gbr = base
    machine.r = [(index * 0x11111111) & MASK for index in range(16)]
    machine.r[0] = value
    machine.t = machine.q = machine.m = 1
    machine.mach, machine.macl = 0x12345678, 0x87654321
    before = (list(machine.r), machine.gbr, machine.pr, machine.t,
              machine.q, machine.m, machine.mach, machine.macl)
    address = (base + 2 * displacement) & MASK
    machine.seed(address - 1, b"\xA5\x55\x55\x5A")

    assert machine.run(0, (2,)) == 2
    assert machine.peek(address, 2) == value & 0xFFFF
    assert machine.peek(address - 1) == 0xA5
    assert machine.peek(address + 2) == 0x5A
    assert machine.written() == {address, address + 1}
    assert machine.stores == [(0, address, 2, value & 0xFFFF)]
    assert machine.loads == []
    assert (machine.r, machine.gbr, machine.pr, machine.t,
            machine.q, machine.m, machine.mach, machine.macl) == before


def test_gbr_word_store_executes_in_branch_delay_slot():
    machine = Sh2(bytes.fromhex("a001 c10a 0009 0009"))
    machine.gbr, machine.r[0] = 0xFFFF8D58, 0xFFFF0000
    machine.t = 1

    assert machine.run(0, (6,)) == 6
    assert machine.stores == [(2, 0xFFFF8D6C, 2, 0)]
    assert machine.r[0] == 0xFFFF0000
    assert machine.t == 1


@pytest.mark.parametrize("base, displacement", ((0, 0), (0xFFFFFFFE, 1)))
def test_gbr_word_store_preserves_image_write_guard(base, displacement):
    data = (0xC100 | displacement).to_bytes(2, "big")
    machine = Sh2(data)
    machine.gbr, machine.r[0] = base, 0xABCD

    with pytest.raises(AssertionError, match="store into the image 0x00000000"):
        machine.run(0, (2,))
    assert machine.data == data
    assert machine.stores == []
    assert machine.ram == {}


def test_neighboring_unsupported_gbr_opcode_is_rejected():
    machine = Sh2(bytes.fromhex("c30a"))
    with pytest.raises(AssertionError, match="opcode c30a"):
        machine.run(0, (2,))
    assert machine.stores == []
