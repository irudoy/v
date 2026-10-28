"""Gate the PH1 stop-lamp-switch input code facts of JK78C and JK08A.

The facts are read from the exact stock images: the input sampler copies the
PHDR bit of PH1 with direct polarity, and DID 0x1305 publishes the status byte
that carries it.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JK78C_ROM = ROOT / "rom-images/23710-JK78C/1JK78C-20260715-stock.bin"
JK08A_ROM = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"

# Per image: GBR literal load, port-base load, base store, reload of the PH1 read, and
# the expected r15-referencing instructions between the store and the reload.
IMAGES = {
    "JK78C": {
        "rom": JK78C_ROM,
        "gbr_load": 0x3BD8A,
        "gbr": 0xFFFF23B0,
        "base_load": 0x3BD90,
        "base": 0xFFFFF720,
        "store": 0x3BD98,
        "to_store": "ec00 d581 8566",
        "read": 0x3BE72,
        "read_ops": "52f1 8526 600d c802 60a3 8d01 c9bf cb40 d34e 6a0e c001",
        "bit": 6,
        "frame_ops": {
            0x3BDA2: 0x2FC0, 0x3BDB2: 0x80F8, 0x3BDB6: 0x80FC, 0x3BDC0: 0x0F24,
            0x3BDC8: 0x0F24, 0x3BDD0: 0x0F24, 0x3BDD8: 0x0F24, 0x3BE06: 0x1F68,
            0x3BE10: 0x1F68,
        },
        "indexed": {0x3BDC0: 0x3BDBE, 0x3BDC8: 0x3BDC6, 0x3BDD0: 0x3BDCE, 0x3BDD8: 0x3BDD6},
        "calls": (),
        "publisher_load": 0x35DCC,
        "family_13": 0x22A94,
        "status_byte": 0xFFFF34EF,
        "mask_pointer": 0x1354E,
        "mask": 0x54,
    },
    "JK08A": {
        "rom": JK08A_ROM,
        "gbr_load": 0x3862A,
        "gbr": 0xFFFF2450,
        "base_load": 0x38630,
        "base": 0xFFFFF728,
        "store": 0x3863C,
        "to_store": "ec00 d589 8562 2fc0 600d",
        "read": 0x3870C,
        "read_ops": "52f1 8522 600d c802 60d3 8d01 c97f cb80 d356 660e c001",
        "bit": 7,
        "frame_ops": {
            0x38668: 0x1F62, 0x3866E: 0x56F2, 0x38674: 0x1F62, 0x3867A: 0x56F2,
            0x38698: 0x80FC, 0x386A0: 0x84FC, 0x386A8: 0x84FC, 0x386E6: 0x0F64,
            0x386EE: 0x0F64, 0x386F6: 0x0F24, 0x38700: 0x0F64,
        },
        "indexed": {0x386E6: 0x386E4, 0x386EE: 0x386EC, 0x386F6: 0x386F4, 0x38700: 0x386FC},
        "calls": (0x3868C,),
        "publisher_load": 0x325A8,
        "family_13": 0x229E0,
        "status_byte": 0xFFFF3345,
        "mask_pointer": 0x11E44,
        "mask": 0x44,
    },
}
PHDR = 0xFFFFF72C


def _u16(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 2], "big")


def _u32(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 4], "big")


def _ops(data: bytes, address: int, count: int) -> str:
    return " ".join(f"{_u16(data, address + 2 * index):04x}" for index in range(count))


def _pc_literal(data: bytes, address: int) -> int:
    opcode = _u16(data, address)
    assert opcode >> 12 == 0xD
    return _u32(data, ((address + 4) & ~3) + (opcode & 0xFF) * 4)


def _pc_word(data: bytes, address: int) -> int:
    opcode = _u16(data, address)
    assert opcode >> 12 == 0x9
    return _u16(data, address + 4 + (opcode & 0xFF) * 2)


def _names_r15(opcode: int) -> bool:
    """True when an instruction names r15 as a register operand."""
    top, n, m = opcode >> 12, (opcode >> 8) & 0xF, (opcode >> 4) & 0xF
    if top <= 0x7:
        return 15 in (n, m)
    if top == 0x8:
        return n in (0x0, 0x1, 0x4, 0x5) and m == 15
    return top in (0x9, 0xD, 0xE) and n == 15


def _writes_gbr_or_calls(opcode: int) -> bool:
    top, low8 = opcode >> 12, opcode & 0xFF
    return top == 0xB or (top == 0x4 and low8 in (0x0B, 0x2B, 0x1E, 0x17)) or (top == 0x0 and low8 in (0x03, 0x23))


def test_ph1_input_is_copied_directly_in_both_images() -> None:
    for name, image in IMAGES.items():
        data = image["rom"].read_bytes()
        # GBR = status block; r6 = sign-extended port H word literal, stored at @(4,r15).
        assert _pc_literal(data, image["gbr_load"]) == image["gbr"], name
        assert _u16(data, image["gbr_load"] + 2) == 0x401E, name
        assert 0xFFFF0000 | _pc_word(data, image["base_load"]) == image["base"], name
        assert _u16(data, image["base_load"]) >> 8 == 0x96, name
        # None of the instructions between the base load and the store writes r6.
        between = (image["store"] - image["base_load"] - 2) // 2
        assert _ops(data, image["base_load"] + 2, between) == image["to_store"], name
        # The PH1 read: r2 = @(4,r15); r0 = mov.w @(disp,r2) = PHDR; tst #2; the bt/s skips
        # the or that sets the target bit, so the bit is set while PH1 reads high; mov.b r0,@(1,gbr).
        ops = [int(op, 16) for op in image["read_ops"].split()]
        assert _ops(data, image["read"], 11) == image["read_ops"], name
        assert ops[0] == 0x52F1 and ops[1] >> 8 == 0x85 and image["base"] + (ops[1] & 0xF) * 2 == PHDR, name
        assert ops[3] == 0xC802 and ops[5] == 0x8D01 and ops[10] == 0xC001, name
        bit = 1 << image["bit"]
        assert ops[6] == 0xC900 | (0xFF ^ bit) and ops[7] == 0xCB00 | bit, name
        # Between the store and the reload no instruction writes r15, GBR, or frame bytes 4..7.
        body = range(image["store"] + 2, image["read"], 2)
        frame = {a: _u16(data, a) for a in body if _names_r15(_u16(data, a))}
        assert frame == image["frame_ops"], name
        for address, opcode in frame.items():
            top, n, m, low = opcode >> 12, (opcode >> 8) & 0xF, (opcode >> 4) & 0xF, opcode & 0xF
            if top == 0x1:  # mov.l Rm,@(disp,r15)
                assert n == 15 and low * 4 >= 8, (name, hex(address))
            elif top == 0x8 and n in (0x0, 0x1):  # mov.b/mov.w R0,@(disp,r15)
                assert low * (n + 1) >= 8, (name, hex(address))
            elif top == 0x2:  # mov.b/w/l Rm,@r15 covers bytes 0..3
                assert n == 15 and low in (0x0, 0x1, 0x2), (name, hex(address))
            elif top == 0x0:  # mov.x Rm,@(r0,r15) with r0 = #imm >= 8
                assert n == 15 and low in (0x4, 0x5, 0x6), (name, hex(address))
                load = image["indexed"][address]
                assert _u16(data, load) >> 8 == 0xE0 and _u16(data, load) & 0xFF >= 8, (name, hex(address))
                assert all(_u16(data, a) >> 8 in (0x89, 0x8B, 0x8D, 0x8F) for a in range(load + 2, address, 2))
            else:  # loads from the frame
                assert (top == 0x5 and m == 15) or (top == 0x8 and n in (0x4, 0x5)), (name, hex(address))
        # Calls in the window follow the save-and-restore convention of this function's own prologue.
        calls = tuple(a for a in body if _writes_gbr_or_calls(_u16(data, a)))
        assert calls == image["calls"], name


def test_did_1305_binds_the_status_bytes() -> None:
    # The service-0x22 publisher loads the family 0x13 table with r0 = DID low byte * 8.
    publisher = "6063 8813 8b52 6053 4008 d4a2 4000 1f03 004e 88ff"
    for name, image in IMAGES.items():
        data = image["rom"].read_bytes()
        assert _ops(data, image["publisher_load"], 10) == publisher, name
        assert _pc_literal(data, image["publisher_load"] + 10) == image["family_13"], name
        record = image["family_13"] + 5 * 8
        assert _u32(data, record) == image["status_byte"], name
        assert _u32(data, record + 4) == image["mask_pointer"], name
        assert data[image["mask_pointer"]] == image["mask"], name


# (year, page label, section tag, normalized phrases) from the tracked fragment packs.


