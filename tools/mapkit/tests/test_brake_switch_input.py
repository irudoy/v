"""Gate the PH1 stop-lamp-switch input facts published for JK78C and JK08A.

The code facts are read from the exact stock images. The terminal facts are read
from the tracked factory-manual fragments; they identify ECM terminal
122 as the stop lamp switch input, which makes PH1 (MCU pin 64) a terminal 122
candidate by signal identity, not a proven board route.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JK78C_ROM = ROOT / "rom-images/23710-JK78C/1JK78C-20260715-stock.bin"
JK08A_ROM = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
JK78C_DOC = ROOT / "defs/JK78C.vvel.md"
JK08A_DOC = ROOT / "defs/JK08A.rpm-drop-state.md"
MANUAL = ROOT / "refs/renesas-sh7059-sh7058s-hardware-manual.md"
FRAGMENTS = {
    2007: ROOT / "refs/diagnostics/nissan-esm-2007-g35-sedan/fragments.jsonl",
    2013: ROOT / "refs/diagnostics/nissan-esm-2013-g37-sedan/fragments.jsonl",
}
PIN_TRACER = ROOT / "tools/pin-tracer"
EDITED_SOURCES = (
    "defs/JK78C.vvel.md",
    "defs/JK08A.rpm-drop-state.md",
    "defs/JK08A.funcs.csv",
    "defs/JK08A.vars.csv",
    "defs/JK08A.findings.csv",
    "defs/JK08A.diagnostic-bindings.csv",
)

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


def _normalized(text: str) -> str:
    return " ".join(text.replace("\u2022", " ").split())


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


def test_ph1_is_pin_64_and_phdr_bit_1() -> None:
    manual = _normalized(MANUAL.read_text(encoding="utf-8"))
    assert "| 64 | B18 | PH1/D1 | D1 |" in manual
    assert "| 74 | D17 | PH9/D9 | NC |" in manual
    assert "| Port H data register | | | PHDR | | | R/W | H'0000 | | H'FFFFF72C | | 8, 16 |" in manual
    assert "H'FFFFF72C PHDR PH15DR PH14DR PH13DR PH12DR PH11DR PH10DR PH9DR PH8DR" in manual
    assert "H'FFFFF72D PH7DR PH6DR PH5DR PH4DR PH3DR PH2DR PH1DR PH0DR" in manual
    index = (PIN_TRACER / "index.html").read_text(encoding="utf-8")
    assert "setMcuRange(63, 69, pin => `PH${pin - 63}/D${pin - 63}`);" in index


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
FRAGMENT_EVIDENCE = (
    (2007, "EC-118", "[VQ35HR]", ("Indicates [ON/OFF] condition from the stop lamp BRAKE SW ON/OFF switch signal.",)),
    (2007, "EC-120", "[VQ35HR]", ("Indicates [ON/OFF] condition from ASCD brake BRAKE SW1 ON/OFF switch signal.",)),
    (2007, "EC-403", "[VQ35HR]", (
        "Turn ignition switch ON.",
        "126 Brake pedal (A/T) Slightly depressed Approx. 0V O M107 Ground (ASCD brake switch signal) "
        "Brake pedal and clutch pedal (M/T) Fully released Battery voltage",
    )),
    (2007, "EC-404", "[VQ35HR]", (
        "122 Slightly depressed Battery voltage M107 Ground Brake pedal (Stop lamp switch signal) Fully released Approx. 0V",
        "ASCD brake switch ECM Continuity Connector Terminal Connector Terminal E109 2 M107 126 Existed",
    )),
    (2007, "EC-407", "[VQ35HR]", ("Stop lamp switch ECM Continuity Connector Terminal Connector Terminal E110 2 M107 122 Existed",)),
    (2013, "EC-160", "[VQ37VHR]", ("Indicates [ON/OFF] condition from the stop BRAKE SW ON/OFF lamp switch signal.",)),
    (2013, "EC-161", "[VQ37VHR]", ("Indicates [ON/OFF] condition from ASCD BRAKE SW1 ON/OFF brake switch signal.",)),
    (2013, "EC-469", "[VQ37VHR]", (
        "Turn ignition switch ON.",
        "Slightly depressed Approx. 0 126 Brake pedal or clutch pedal (M/T) M107 (ASCD brake switch signal) 128 O "
        "Brake pedal (A/T) Fully released Battery voltage",
    )),
    (2013, "EC-735", "[VQ25HR]", ("Indicates [ON/OFF] condition from the stop lamp BRAKE SW ON/OFF switch signal.",)),
    (2013, "EC-736", "[VQ25HR]", ("Indicates [ON/OFF] condition from ASCD brake BRAKE SW1 ON/OFF switch signal.",)),
    (2013, "EC-938", "[VQ25HR]", (
        "126 Slightly depressed Approx. 0 M107 128 Brake pedal (ASCD brake switch signal) Fully released Battery voltage",
    )),
    (2013, "CCS-58", "[ICC]", ("Stop lamp switch ECM Continuity Connector Terminal Connector Terminal E110 2 M107 122 Existed",)),
)

def _fragment_pages(year: int) -> dict[str, str]:
    pages: dict[str, set[str]] = {}
    with FRAGMENTS[year].open(encoding="utf-8") as source:
        for line in source:
            fragment = json.loads(line)
            pages.setdefault(fragment["page_label"], set()).add(fragment["text"])
    return {label: _normalized(" ".join(sorted(texts))) for label, texts in pages.items()}


def test_manual_fragments_define_the_brake_signals_and_terminals() -> None:
    pages = {year: _fragment_pages(year) for year in FRAGMENTS}
    for year, label, tag, phrases in FRAGMENT_EVIDENCE:
        text = pages[year][label]
        assert tag in text, (year, label)
        for phrase in phrases:
            assert phrase in text, (year, label, phrase)


def test_pin_tracer_labels_the_brake_terminals() -> None:
    index = (PIN_TRACER / "index.html").read_text(encoding="utf-8")
    model = (PIN_TRACER / "model.js").read_text(encoding="utf-8")
    assert '122: ["P", "BRAKE"],' in index
    assert '126: ["BR", "BNCSW"],' in index
    assert 'BRAKE: "Stop lamp switch input",' in model


def _doc(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_documents_state_the_ph1_evidence() -> None:
    jk78c, jk08a = IMAGES["JK78C"], IMAGES["JK08A"]
    data = JK08A_ROM.read_bytes()
    base_word = jk08a["base_load"] + 4 + (_u16(data, jk08a["base_load"]) & 0xFF) * 2
    record = jk08a["family_13"] + 5 * 8
    doc = _doc(JK08A_DOC)
    for phrase in (
        f"`FUN_00038618` keeps the port H base `0x{jk08a['base']:08X}` (`ROM16[0x{base_word:05X}]`) at `@(4,r15)` "
        f"and at `0x{jk08a['read']:08X}..0x{jk08a['read'] + 0x14:08X}` reads the 16-bit `PHDR` word at "
        f"`0x{PHDR:08X}`, tests bit 1 (`tst #2`), and writes the result to `0xFFFF2451.bit7` with direct "
        "polarity: the bit is set while PH1 reads high.",
        "`PHDR` bit 1 is `PH1DR`, and PH1 is SH7058 FP-256H pin 64.",
        f"ROM32[0x{record:05X}] = 0x{jk08a['status_byte']:08X} ROM32[0x{record + 4:05X}] = "
        f"0x{jk08a['mask_pointer']:08X} ROM8 [0x{jk08a['mask_pointer']:05X}] = 0x{jk08a['mask']:02X}",
        "| 2007 G35 Sedan, VQ35HR | EC-118, EC-120 | EC-500, EC-404 | EC-500, EC-403 |",
        "| 2013 G Sedan, VQ25HR | EC-735, EC-736 | EC-1005 | EC-1006, EC-938 |",
        "| 2013 G Sedan, VQ37VHR | EC-160, EC-161 | EC-568 | EC-568, EC-469 |",
        "The harness continuity checks connect stop lamp switch connector E110 terminal 2 to ECM connector M107 "
        "terminal 122 (2007 EC-407, 2013 ICC section CCS-58) and ASCD brake switch connector E109 terminal 2 to "
        "M107 terminal 126 (2007 EC-404).",
        "Terminal 122 reads 0 V with the brake pedal fully released and battery voltage with the pedal slightly "
        "depressed, with the ignition switch OFF. Terminal 126 reads battery voltage released and 0 V depressed, "
        "with the ignition switch ON. The 2013 tables measure both against ECM ground terminal 128.",
        "PH1 is a terminal 122 candidate by signal identity",
        "labels terminal 122 `BRAKE` and terminal 126 `BNCSW`.",
        "measure the resistance from ECM terminal 122 to MCU pin 64.",
        "terminal 126 to pin 64 is the negative control.",
        "read DID `0x1305` bit 2. The candidate predicts the bit clear at 0 V and set at battery voltage.",
    ):
        assert phrase in doc, phrase

    doc = _doc(JK78C_DOC)
    for phrase in (
        f"`0xFFFF23B1.bit6` is the direct copy of `PHDR` bit 1 (`0x{PHDR:08X}`, PH1) that the input sampler "
        f"`FUN_0003BD78` takes at `0x{jk78c['read'] + 2:08X}`: the bit is set while PH1 reads high. PH1 is "
        "SH7058 FP-256H pin 64.",
        f"(`ROM32[0x{jk78c['family_13'] + 5 * 8:05X}]`, support mask `ROM8[0x{jk78c['mask_pointer']:05X}]` = "
        f"`0x{jk78c['mask']:02X}`)",
        "places that signal on ECM terminal 122 (EC-160, EC-568), so PH1 is a terminal 122 candidate by signal "
        "identity.",
        "PH1 carries the stop lamp switch signal of ECM terminal 122; a continuity check from terminal 122 to MCU "
        "pin 64 closes it for a given board.",
    ):
        assert phrase in doc, phrase


def _row(path: str, key: str) -> dict[str, str]:
    with (ROOT / path).open(encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        header = next(reader)
        for row in reader:
            if row and row[0] == key:
                return dict(zip(header, row))
    raise AssertionError((path, key))


def test_catalog_rows_name_ph1() -> None:
    expected = {
        ("defs/JK08A.funcs.csv", "00038618"): "PHDR bit 1 (PH1DR) is copied with direct polarity to ffff2451.bit7.",
        ("defs/JK08A.vars.csv", "ffff2451"): "Bit 7 directly mirrors SH7058 PHDR bit 1 (PH1DR)",
        ("defs/JK08A.vars.csv", "ffff257a"): "zero bypasses the PH1-derived ffff2451.bit7 requirement",
        ("defs/JK08A.findings.csv", "0001202e"): "ffff2451.bit7 directly mirrors SH7058 PHDR bit 1 (PH1DR)",
        ("defs/JK08A.diagnostic-bindings.csv", "brake-switch-did-1305-bit2"): (
            "PH1 is MCU pin 64 and a terminal 122 candidate by signal identity"
        ),
    }
    for (path, key), phrase in expected.items():
        assert any(phrase in value for value in _row(path, key).values()), (path, key)
    for path in EDITED_SOURCES:
        assert "PH9" not in (ROOT / path).read_text(encoding="utf-8"), path
