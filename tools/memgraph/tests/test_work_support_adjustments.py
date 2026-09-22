import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
BINDINGS = ROOT / "defs" / "JK08A.diagnostic-bindings.csv"
SPEC = ROOT / "defs" / "JK08A.work-support.md"

HANDLER = 0x34194
LID_BITMAP_POINTER = 0x22E30
LID_TABLE = 0x22E32
SCHEDULER_TABLE = 0x2196C
SCHEDULER_ENTRIES = 124
TIMING_DID_POINTER = 0x22760
IDLE_DID_POINTER = 0x22764

# LID n reads ROM16[0x22E32 + 2n]: flag-byte offset from 0xFFFF99F4, apply mask.
LID_WORDS = (
    0x0001, 0x0004, 0x0010, 0x0040,
    0x0101, 0x0104, 0x0110, 0x0140,
    0x0201, 0x0204, 0x0210, 0x0240,
    0x0301, 0x0304, 0x0310, 0x0340,
    0x0401, 0x0404, 0x0410, 0x0440,
)

# Scheduler pointer and entry, in pass order.
PERIODIC_STEPS = (
    (0x219EC, 0x41E84),  # -> FUN_000420B8: idle adjustment
    (0x21A80, 0x68670),  # session status and routing
    (0x21A84, 0x35318),  # -> FUN_00034FE4: LIDs 4..20
    (0x21A88, 0x4D888),  # -> FUN_0004AAD0: timing adjustment
    (0x21B38, 0x68254),  # -> FUN_00068040: stored-record requests
)

NEW_FUNCTIONS = {
    "00034194": "service",
    "0002e81a": "service",
    "00068270": "selector",
    "000682a2": "service",
    "000682e0": "selector",
    "000682f6": "selector",
    "0006836e": "selector",
    "000683b6": "service",
    "000685f2": "selector",
    "00068670": "dispatch",
    "00034fe4": "service",
    "00068254": "wrapper",
    "00035318": "wrapper",
}

NEW_REGISTERS = (
    "ffff99f4", "ffff99dc", "ffff99dd", "ffff99de", "ffff10da", "ffff115a",
    "ffff3168", "ffff316a", "ffff56f6", "ffff5690", "ffff4124", "ffff4125",
    "ffff40cc", "ffff4112", "ffff416a", "ffff424c", "ffff41aa", "ffff41ef",
    "ffff41b3", "ffff2b72", "ffff42d4", "ffff41b9", "ffff5b31",
)


def u8(data, offset):
    return data[offset]


def s8(data, offset):
    value = data[offset]
    return value - 0x100 if value & 0x80 else value


def u16(data, offset):
    return int.from_bytes(data[offset : offset + 2], "big")


def u32(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


def mov_l_literal(data, address):
    """Return the literal a PC-relative MOV.L at address loads."""
    opcode = u16(data, address)
    assert opcode >> 12 == 0xD, hex(opcode)
    return u32(data, ((address + 4) & ~3) + (opcode & 0xFF) * 4)


def mov_w_literal(data, address):
    """Return the sign-extended word a PC-relative MOV.W at address loads."""
    opcode = u16(data, address)
    assert opcode >> 12 == 0x9, hex(opcode)
    word = u16(data, address + 4 + (opcode & 0xFF) * 2)
    return word | 0xFFFF0000 if word & 0x8000 else word


def branch_target(data, address):
    """Return the target of a BRA or BSR at address."""
    opcode = u16(data, address)
    assert opcode >> 12 in (0xA, 0xB), hex(opcode)
    displacement = opcode & 0xFFF
    if displacement & 0x800:
        displacement -= 0x1000
    return address + 4 + displacement * 2


def conditional_target(data, address):
    """Return the target of a BT, BF, BT/S, or BF/S at address."""
    opcode = u16(data, address)
    assert opcode >> 8 in (0x89, 0x8B, 0x8D, 0x8F), hex(opcode)
    displacement = opcode & 0xFF
    if displacement & 0x80:
        displacement -= 0x100
    return address + 4 + displacement * 2


def gbr_byte(opcode, base):
    """Return the byte address of a MOV.B/AND.B/OR.B/TST.B GBR form."""
    return base + (opcode & 0xFF)


class WorkSupportAdjustmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        with FUNCS.open(newline="", encoding="utf-8") as source:
            cls.funcs = {row["addr"]: row for row in csv.DictReader(source)}
        with VARS.open(newline="", encoding="utf-8") as source:
            cls.vars = {row["addr"]: row for row in csv.DictReader(source)}
        with BINDINGS.open(newline="", encoding="utf-8") as source:
            cls.bindings = {row["id"]: row for row in csv.DictReader(source)}
        cls.spec = " ".join(SPEC.read_text(encoding="utf-8").split())

    def assertOps(self, expected):
        for address, opcode in expected:
            with self.subTest(address=hex(address)):
                self.assertEqual(u16(self.rom, address), opcode)

    def test_dispatcher_selects_the_write_handler(self):
        rom = self.rom
        self.assertEqual(u16(rom, 0x2F9EA), 0x883B)  # cmp/eq #0x3b,r0
        self.assertEqual(conditional_target(rom, 0x2F9EC), 0x2F9F4)
        self.assertEqual(mov_l_literal(rom, 0x2F9EE), HANDLER)
        self.assertEqual(u16(rom, 0x2F9F0), 0x422B)  # jmp @r2
        self.assertEqual(u32(rom, 0x2FB0C), HANDLER)

    def test_request_layout_and_lid_zero_bitmap(self):
        rom = self.rom
        # LID 0xFFFF8005 -> 0xFFFF39C4 + 0x640.
        self.assertEqual(mov_w_literal(rom, 0x3419C), 0xFFFF8005)
        self.assertEqual(mov_l_literal(rom, 0x3419E), 0xFFFF39C4)
        self.assertEqual(mov_w_literal(rom, 0x341A2), 0x0640)
        self.assertOps((
            (0x341A0, 0x6650),  # mov.b @r5,r6
            (0x341AA, 0x0D64),  # mov.b r6,@(r0,r13)
            (0x341AE, 0xE77B),  # mov #0x7b,r7
            (0x341DC, 0x076E),  # mov.l @(r0,r6),r7
            (0x34226, 0x420B),  # jsr @r2
        ))
        self.assertEqual(conditional_target(rom, 0x341A8), 0x3422E)
        self.assertEqual(mov_l_literal(rom, 0x341D8), LID_BITMAP_POINTER)
        self.assertEqual(u32(rom, LID_BITMAP_POINTER), 0x11E3D)
        self.assertEqual(rom[0x11E3D:0x11E41], bytes((0xC0, 0x00, 0x00, 0x00)))
        self.assertEqual(mov_l_literal(rom, 0x34220), 0x2EC9A)
        # VALUE 0xFFFF8006 and CONTROL 0xFFFF8007 -> 0xFFFF28F8 + 0x29C/0x29D.
        self.assertOps((
            (0x3422E, 0x8451),  # mov.b @(1,r5),r0
            (0x3423A, 0x0E24),  # mov.b r2,@(r0,r14)
            (0x3423C, 0x8452),  # mov.b @(2,r5),r0
            (0x34244, 0x0E24),
        ))
        self.assertEqual(mov_l_literal(rom, 0x34232), 0xFFFF28F8)
        self.assertEqual(mov_w_literal(rom, 0x34238), 0x029C)
        self.assertEqual(mov_w_literal(rom, 0x34240), 0x029D)

    def test_lid_table_masks_and_slots(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x34246), LID_TABLE + 2)
        self.assertOps((
            (0x3424C, 0x77FE),  # add #-2,r7
            (0x3424E, 0x047D),  # mov.w @(r0,r7),r4
            (0x34266, 0x4519),  # shlr8 r5
            (0x3426C, 0x7718),  # add #0x18,r7
            (0x34270, 0x375C),  # add r5,r7
        ))
        self.assertEqual(
            tuple(u16(rom, LID_TABLE + 2 * lid) for lid in range(1, 21)),
            LID_WORDS,
        )
        self.assertEqual(u16(rom, LID_TABLE + 2 * 21), 0xFFFF)
        # Slot base 0xFFFF99DC; the store uses base - 1 indexed by LID.
        self.assertEqual(mov_w_literal(rom, 0x34262), 0xFFFF99DC)
        self.assertEqual(mov_w_literal(rom, 0x34322), 0xFFFF99DC)
        self.assertOps((
            (0x34368, 0x76FF),  # add #-1,r6
            (0x34396, 0x76FF),
            (0x3439C, 0x0654),  # mov.b r5,@(r0,r6)
        ))
        # LIDs 4 and above take the second path; LIDs 21 and above answer 0x12.
        self.assertOps(((0x34230, 0xE404), (0x34234, 0x3643),
                        (0x34304, 0xE415), (0x34306, 0x3643)))
        self.assertEqual(conditional_target(rom, 0x34242), 0x34304)
        self.assertEqual(conditional_target(rom, 0x34308), 0x343A6)

    def test_control_codes_status_checks_and_negative_responses(self):
        rom = self.rom
        # Control 0x00 of LIDs 1..3 checks 0xFFFF40CC.
        self.assertEqual(mov_l_literal(rom, 0x34278), 0xFFFF40CC)
        self.assertOps((
            (0x34268, 0x2228),  # tst r2,r2 (CONTROL)
            (0x3427A, 0xE6FF),  # mov #-1,r6
            (0x34282, 0x3560),  # cmp/eq r6,r5
            (0x34288, 0x224B),  # or r4,r2: apply bit
            (0x3428A, 0x2720),
            (0x3428E, 0x4200),  # shll r2: store mask
            (0x34290, 0x6527),  # not r2,r5
            (0x3429A, 0x2760),
        ))
        self.assertEqual(conditional_target(rom, 0x3426E), 0x3429C)
        self.assertEqual(conditional_target(rom, 0x34284), 0x34348)
        # Control 0x55 of LIDs 1..3 checks 0xFFFF40CC and sets the store bit.
        self.assertEqual(u16(rom, 0x3429E), 0x8855)  # cmp/eq #0x55,r0
        self.assertEqual(conditional_target(rom, 0x342A0), 0x342CA)
        self.assertEqual(mov_l_literal(rom, 0x342A8), 0xFFFF40CC)
        self.assertEqual(conditional_target(rom, 0x342B4), 0x34348)
        self.assertOps((
            (0x342BA, 0x4200),  # shll r2
            (0x342BE, 0x252B),  # or r2,r5: store bit
            (0x342C0, 0x6247),  # not r4,r2
            (0x342C4, 0x2529),  # and r2,r5: clear apply bit
            (0x342C8, 0x2750),
        ))
        # Control 0xFF clears both bits and zeroes the slot; others answer 0x12.
        self.assertOps(((0x342CA, 0xE6FF), (0x342CE, 0x3260)))
        self.assertEqual(conditional_target(rom, 0x342D0), 0x343A6)
        self.assertOps(((0x342E8, 0x2760), (0x342EA, 0xE600),
                        (0x342F6, 0x0564)))
        self.assertEqual(branch_target(rom, 0x342F4), 0x3439E)
        # LIDs 4..20: control 0x00 checks 0xFFFF40CC + 0x46 = 0xFFFF4112.
        self.assertEqual(conditional_target(rom, 0x3432E), 0x34374)
        self.assertEqual(mov_l_literal(rom, 0x34338), 0xFFFF40CC)
        self.assertOps(((0x3433A, 0xE046), (0x3433E, 0x052C)))
        self.assertEqual(conditional_target(rom, 0x34346), 0x3434C)
        self.assertEqual(conditional_target(rom, 0x3437A), 0x343A6)
        # A failed status check answers with the status byte in r5.
        self.assertEqual(branch_target(rom, 0x34348), 0x343AA)
        self.assertEqual(u16(rom, 0x3434A), 0xE43B)  # mov #0x3b,r4
        self.assertOps(((0x343A6, 0xE43B), (0x343A8, 0xE512)))
        self.assertEqual(branch_target(rom, 0x343AA), 0x34114)
        self.assertEqual(branch_target(rom, 0x3439E), 0x343B8)

    def test_reset_clears_flags_and_slots(self):
        rom = self.rom
        self.assertEqual(branch_target(rom, 0x2E824), 0x2E76E)
        self.assertEqual(mov_w_literal(rom, 0x2E828), 0xFFFF99D8)
        self.assertOps((
            (0x2E82E, 0xE706),  # mov #6,r7
            (0x2E832, 0x741C),  # add #0x1c,r4: 0xFFFF99F4
            (0x2E836, 0x24E0),  # mov.b r14,@r4
            (0x2E842, 0x7404),  # add #4,r4: 0xFFFF99DC
            (0x2E846, 0xE718),  # mov #0x18,r7
            (0x2E84A, 0x24E0),
            (0x2E856, 0xE402),  # mov #2,r4: 0xFFFF99D8..0xFFFF99D9
            (0x2E85A, 0x25E0),
        ))
        # FUN_0002EA0A: transport state 8 and 0xFFFF8468 not 3 or 4.
        self.assertOps(((0x2EC1A, 0x8808), (0x2EC22, 0x8803),
                        (0x2EC26, 0x8804)))
        self.assertEqual(mov_w_literal(rom, 0x2EC1E), 0xFFFF8468)
        self.assertEqual(branch_target(rom, 0x2EC2A), 0x2E81A)

    def test_scheduler_order_and_block_copies(self):
        rom = self.rom
        self.assertEqual(u16(rom, 0x212EC), 0xEE00 | SCHEDULER_ENTRIES)
        self.assertEqual(mov_l_literal(rom, 0x212EE), SCHEDULER_TABLE)
        self.assertOps(((0x212F0, 0x62D2), (0x212F2, 0x420B),
                        (0x212F4, 0x7D04), (0x212F6, 0x4E10)))
        self.assertEqual(conditional_target(rom, 0x212F8), 0x212F0)
        last = SCHEDULER_TABLE + 4 * (SCHEDULER_ENTRIES - 1)
        self.assertEqual(last, 0x21B58)
        for pointer, entry in PERIODIC_STEPS:
            with self.subTest(pointer=hex(pointer)):
                self.assertEqual(u32(rom, pointer), entry)
                self.assertTrue(SCHEDULER_TABLE <= pointer <= last)
        self.assertEqual(
            [pointer for pointer, _ in PERIODIC_STEPS],
            sorted(pointer for pointer, _ in PERIODIC_STEPS),
        )
        # Entry chains.
        self.assertEqual(mov_l_literal(rom, 0x41E8C), 0x43AEE)
        self.assertEqual(u16(rom, 0x41E8E), 0x420B)
        self.assertEqual(mov_l_literal(rom, 0x43B1A), 0x420B8)
        self.assertEqual(u16(rom, 0x43B1C), 0x430B)
        self.assertEqual(branch_target(rom, 0x35318), 0x34FE4)
        self.assertEqual(mov_l_literal(rom, 0x4D88E), 0x4AAD0)
        self.assertEqual(u16(rom, 0x4D890), 0x430B)
        self.assertEqual(branch_target(rom, 0x68256), 0x68040)
        self.assertEqual(branch_target(rom, 0x6825A), 0x67358)
        # Before the loop: 0xFFFF417E -> 0xFFFF4180, 0xFFFF417F -> 0xFFFF417E,
        # 0xFFFF4184 -> 0xFFFF4186, 0xFFFF4185 -> 0xFFFF4184,
        # 0xFFFF41A6 -> 0xFFFF41A8.
        self.assertEqual(mov_l_literal(rom, 0x21060), 0xFFFF417E)
        self.assertEqual(mov_l_literal(rom, 0x21074), 0xFFFF4180)
        self.assertEqual(mov_l_literal(rom, 0x21078), 0xFFFF417F)
        self.assertOps(((0x21072, 0x6240), (0x21076, 0x2620),
                        (0x2107A, 0x6260), (0x2107E, 0x2420)))
        self.assertEqual(mov_l_literal(rom, 0x21084), 0xFFFF4184)
        self.assertEqual(mov_l_literal(rom, 0x2108A), 0xFFFF4186)
        self.assertEqual(mov_l_literal(rom, 0x2108E), 0xFFFF4185)
        self.assertOps(((0x21088, 0x6240), (0x2108C, 0x2620),
                        (0x21090, 0x6260), (0x21092, 0x2420)))
        self.assertEqual(mov_l_literal(rom, 0x2109C), 0xFFFF41A7)
        self.assertEqual(mov_l_literal(rom, 0x210A4), 0xFFFF41A5)
        self.assertOps(((0x210A8, 0x8461), (0x210BA, 0x8041)))
        # 0x80 bytes 0xFFFF1114 -> 0xFFFF1094: r12 = 0xF0, r0 = r12 - 0x70.
        self.assertEqual(mov_l_literal(rom, 0x20F48), 0xFFFF1094)  # r1
        self.assertEqual(mov_l_literal(rom, 0x20F50), 0xFFFF1114)  # r2
        self.assertEqual(((u16(rom, 0x20F48) >> 8) & 0xF, (u16(rom, 0x20F50) >> 8) & 0xF),
                         (1, 2))
        self.assertOps(((0x20E14, 0xECF0), (0x20E16, 0x6CCC),
                        (0x20F54, 0x60C3), (0x20F56, 0x490B),
                        (0x20F58, 0x7090)))
        snapshot = 0xF0 - 0x70
        self.assertLess(0xFFFF115A - 0xFFFF1114, snapshot)
        self.assertEqual(0xFFFF1094 + 0xFFFF115A - 0xFFFF1114, 0xFFFF10DA)
        # After the loop: 0x58 bytes 0xFFFF4124 -> 0xFFFF40CC and 0x66 bytes
        # 0xFFFF56B2 -> 0xFFFF564C.
        self.assertEqual(mov_l_literal(rom, 0x2131E), 0xFFFF40CC)  # r1
        self.assertEqual(mov_l_literal(rom, 0x2132A), 0xFFFF4124)  # r2
        self.assertEqual(((u16(rom, 0x2131E) >> 8) & 0xF, (u16(rom, 0x2132A) >> 8) & 0xF),
                         (1, 2))
        self.assertOps(((0x2132C, 0x490B), (0x2132E, 0xE058)))
        self.assertEqual(mov_l_literal(rom, 0x21330), 0xFFFF564C)  # r1
        self.assertEqual(mov_l_literal(rom, 0x21332), 0xFFFF56B2)  # r2
        self.assertEqual(((u16(rom, 0x21330) >> 8) & 0xF, (u16(rom, 0x21332) >> 8) & 0xF),
                         (1, 2))
        # FUN_00022558 copies r0 bytes from @r2 to @r1.
        self.assertOps(((0x22564, 0x340C), (0x22566, 0x6024),
                        (0x22568, 0x2100)))
        self.assertOps(((0x21334, 0x4B0B), (0x21336, 0xE066)))
        for source, destination, length, cell, copy in (
            (0xFFFF4124, 0xFFFF40CC, u16(rom, 0x2132E) & 0xFF, 0xFFFF4124, 0xFFFF40CC),
            (0xFFFF4124, 0xFFFF40CC, u16(rom, 0x2132E) & 0xFF, 0xFFFF416A, 0xFFFF4112),
            (0xFFFF56B2, 0xFFFF564C, u16(rom, 0x21336) & 0xFF, 0xFFFF56B2, 0xFFFF564C),
            (0xFFFF56B2, 0xFFFF564C, u16(rom, 0x21336) & 0xFF, 0xFFFF56F6, 0xFFFF5690),
        ):
            with self.subTest(cell=hex(cell)):
                self.assertLess(cell - source, length)
                self.assertEqual(destination + cell - source, copy)
        # FUN_00068670 calls the helpers in order and ends at FUN_000685F2.
        self.assertEqual(
            [branch_target(rom, address) for address in range(0x68672, 0x6868E, 4)],
            [0x68270, 0x682A2, 0x682E0, 0x682F6, 0x6836E, 0x683B6, 0x683CC],
        )
        self.assertEqual(branch_target(rom, 0x6868E), 0x685F2)

    def test_session_status_order(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x683DA), 0xFFFF4124)
        # r12 carries 0xA2, 0xA3, 0xA1; r10 carries the later checks.
        self.assertOps((
            (0x68496, 0xEC00), (0x6849A, 0x6AC3), (0x6849E, 0x6BC3),
            (0x6850C, 0xECA2),  # 42D4 nonzero or 4184 bit 6
            (0x684B0, 0xC840),
            (0x684C0, 0xC802), (0x684C6, 0xECA3),  # 41A6 bit 1 clear
            (0x684CA, 0xC801), (0x684CE, 0xECA1), (0x684D0, 0xEB02),
            (0x684D8, 0xE6E0), (0x684DE, 0x3263), (0x684E4, 0xEAA4),
            (0x684EA, 0xC820), (0x684F0, 0xEAA5),  # 244F bit 5 clear
            (0x684F6, 0xC820), (0x684FC, 0xEA10),  # 41A6 bit 5 set
            (0x68500, 0xC880), (0x68506, 0xEAA6),  # 4184 bit 7 clear
            (0x6850A, 0xEAFF), (0x6850E, 0xEB01),
            (0x68520, 0xC000), (0x68526, 0xCB10),
            (0x68528, 0xC000), (0x6852C, 0xC9EF),
            (0x6852E, 0xC086), (0x68532, 0xC001),
        ))
        self.assertEqual(mov_l_literal(rom, 0x68494), 0xFFFF42D3)
        self.assertEqual(u16(rom, 0x6849C), 0x8421)  # mov.b @(1,r2),r0
        for address, target in (
            (0x684AA, 0x6850C), (0x684B2, 0x6850C), (0x684C4, 0x6850E),
            (0x684E2, 0x6850E), (0x684EE, 0x6850E), (0x684FA, 0x6850E),
            (0x68504, 0x6850E), (0x68508, 0x68510),
        ):
            with self.subTest(address=hex(address)):
                opcode = u16(rom, address)
                if opcode >> 12 in (0xA, 0xB):
                    self.assertEqual(branch_target(rom, address), target)
                else:
                    self.assertEqual(conditional_target(rom, address), target)
        self.assertEqual(mov_l_literal(rom, 0x684D2), 0xFFFF1094)
        self.assertEqual(u16(rom, 0x684D4), 0xE046)  # 0xFFFF10DA
        self.assertEqual(mov_l_literal(rom, 0x684E6), 0xFFFF244F)
        self.assertEqual(gbr_byte(u16(rom, 0x684A2), 0xFFFF4124), 0xFFFF41B3)

    def test_status_inputs(self):
        rom = self.rom
        # FUN_00068270: 0xFFFF41A6 bit 1 = coolant snapshot within 110..255.
        self.assertEqual(mov_l_literal(rom, 0x68276), 0x8CC7)
        self.assertEqual(mov_l_literal(rom, 0x68278), 0xFFFF106A)
        self.assertEqual((u8(rom, 0x8CC7), u8(rom, 0x8CC8)), (0xFF, 110))
        self.assertOps((
            (0x6827A, 0x8471), (0x6827E, 0x8447), (0x68284, 0x3166),
            (0x6828C, 0x6270), (0x6828E, 0x3026), (0x68296, 0xCB02),
            (0x6829A, 0xC9FD), (0x6829C, 0xC001),
        ))
        self.assertEqual(mov_l_literal(rom, 0x68272), 0xFFFF41A5)
        # FUN_000683B6: afterrun countdown 0xFFFF42D4 = ROM8[0x8283].
        self.assertEqual(mov_l_literal(rom, 0x683B6), 0xFFFF4184)
        self.assertEqual(u16(rom, 0x683BA), 0xC840)
        self.assertEqual(mov_l_literal(rom, 0x683BE), 0x8283)
        self.assertEqual(u8(rom, 0x8283), 250)
        self.assertEqual(mov_l_literal(rom, 0x683C2), 0xFFFF42D3)
        self.assertEqual(u16(rom, 0x683C6), 0x8061)  # mov.b r0,@(1,r6)
        # FUN_00038618: PLDR bit 4 debouncer and 0xFFFF4185 bit 7.
        self.assertEqual(mov_w_literal(rom, 0x387D6), 0xFFFFF756)
        self.assertOps(((0x38896, 0x8554), (0x3889A, 0xC810),
                        (0x38916, 0xE205), (0x38918, 0xE06B),
                        (0x3891A, 0x0524), (0x3891E, 0xE602),
                        (0x38930, 0xE601), (0x38932, 0xE600),
                        (0x38944, 0xC97F), (0x3894C, 0xCB80),
                        (0x38958, 0x8029)))
        self.assertEqual(mov_l_literal(rom, 0x38914), 0xFFFF256A)
        self.assertEqual(0xFFFF256A + 0x6B, 0xFFFF25D5)
        self.assertEqual(mov_l_literal(rom, 0x388FA), 0xFFFF39C4)
        self.assertEqual(mov_l_literal(rom, 0x38948), 0xFFFF417C)
        # FUN_0007F870: 0xFFFF41A6 bit 5 while state 4 counts 1..100.
        self.assertOps(((0x7FA08, 0x8804), (0x7FA12, 0xE564),
                        (0x7FA46, 0xCF20), (0x7FA4A, 0xCDDF)))

    def test_adjustment_routing_and_edges(self):
        rom = self.rom
        self.assertEqual(mov_w_literal(rom, 0x683E0), 0xFFFF99F4)
        self.assertEqual(mov_l_literal(rom, 0x683E2), 0xFFFF424C)
        # Rising edges of store bits 1, 3, and 5.
        self.assertOps((
            (0x68402, 0xC902), (0x6840C, 0xC802), (0x68412, 0xCB04),
            (0x68416, 0xC9FB), (0x68418, 0xC086),
            (0x6841E, 0xC908), (0x6842C, 0xC880), (0x68434, 0xCB01),
            (0x68438, 0xC9FE), (0x6843A, 0xC0CA),
            (0x6843E, 0xC920), (0x68448, 0xC820), (0x6844E, 0xCB40),
            (0x68492, 0xC9BF), (0x68498, 0xC08F),
        ))
        # Accepted LID 1 -> 0xFFFF424C bit 4.
        self.assertOps(((0x6853A, 0xC803), (0x68540, 0xC810),
                        (0x68548, 0xCB10), (0x6854C, 0xC9EF),
                        (0x68550, 0x2200)))
        self.assertEqual(mov_l_literal(rom, 0x6854E), 0xFFFF424C)
        # Accepted LID 2 -> 0xFFFF41EF bit 3 and 0xFFFF3168 = min(99DD, 20).
        self.assertOps(((0x68554, 0xC80C), (0x6855A, 0xC810),
                        (0x68562, 0xCB08), (0x68564, 0xC0CB),
                        (0x68566, 0x8421), (0x68568, 0x650C),
                        (0x68578, 0x3427), (0x6858E, 0xC9F7)))
        self.assertEqual(mov_l_literal(rom, 0x68570), 0x8909)
        self.assertEqual(u8(rom, 0x8909), 20)
        self.assertEqual(mov_l_literal(rom, 0x68580), 0xFFFF28F8)
        self.assertEqual(mov_w_literal(rom, 0x68582), 0x0870)
        self.assertEqual(u16(rom, 0x68586), 0x0264)  # mov.b r6,@(r0,r2)
        # Accepted LID 3 -> 0xFFFF56BA = 0xFFFF99DE.
        self.assertOps(((0x68598, 0xC830), (0x6859E, 0xC810),
                        (0x685A6, 0x8452), (0x685A8, 0x8028)))
        self.assertEqual(mov_l_literal(rom, 0x685A4), 0xFFFF56B2)
        # Previous levels.
        self.assertOps(((0x685B2, 0xC9FD), (0x685B4, 0xCB02),
                        (0x685B6, 0xC086), (0x685C4, 0xC97F),
                        (0x685C6, 0xCB80), (0x685C8, 0xC0CB),
                        (0x685D2, 0xC9DF), (0x685D4, 0xCB20),
                        (0x685DE, 0xC08F)))

    def test_timing_adjustment_source_and_window(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x4AAD2), 0x821C)
        self.assertEqual((s8(rom, 0x821D), s8(rom, 0x821C)), (-5, 0))
        self.assertEqual(mov_l_literal(rom, 0x4AAD4), 0xFFFF41A9)
        self.assertOps(((0x4AAD6, 0xE010), (0x4AADA, 0xC801)))
        self.assertEqual(conditional_target(rom, 0x4AADC), 0x4AB6A)
        self.assertEqual(mov_l_literal(rom, 0x4AADE), 0xFFFF424C)
        self.assertOps(((0x4AAE2, 0xC810), (0x4AB06, 0xC820)))
        self.assertEqual(mov_w_literal(rom, 0x4AAE6), 0xFFFF99DC)
        # Automatic step of 0xFFFF10DA: 0 below 0x20, -8 from 0xC0,
        # else 4 - 2 * (x >> 5).
        self.assertOps(((0x4AB0E, 0xE520), (0x4AB1A, 0xE600),
                        (0x4AB1C, 0xE5C0), (0x4AB26, 0xE6F8),
                        (0x4AB2E, 0xE6FE), (0x4AB34, 0x7604)))
        self.assertEqual(mov_l_literal(rom, 0x4AB56), 0xFFFF28F8)
        self.assertEqual(u16(rom, 0x4AB58), 0xE0CE)  # 0xFFFF29C6
        self.assertEqual(mov_l_literal(rom, 0x4AB6C), 0xFFFF56B2)
        self.assertEqual(u16(rom, 0x4AB6E), 0x2620)
        # FUN_0004DBE8 adds 0xFFFF564C only while 0xFFFF5B31 bits 1..5 are clear.
        self.assertEqual(mov_l_literal(rom, 0x4DC00), 0xFFFF119C)
        self.assertEqual(mov_l_literal(rom, 0x4DC04), 0xFFFF5B31)
        self.assertOps((
            (0x4DC02, 0xE017), (0x4DC06, 0x062C),  # 0xFFFF11B3
            (0x4DC08, 0x6470),                     # 0xFFFF5B31
            (0x4DC4A, 0x6820),                     # 0xFFFF1048
            (0x4DC88, 0x8427),                     # 0xFFFF1072 + 7
        ))
        self.assertEqual((u8(rom, 0x8897), u8(rom, 0x8896)), (48, 128))
        self.assertEqual((u8(rom, 0x8768), u8(rom, 0x8767)), (64, 96))
        self.assertOps((
            (0x4DC0E, 0xC804), (0x4DC14, 0x7508), (0x4DC1E, 0x3522),
            (0x4DC22, 0xC9FB), (0x4DC24, 0xCB04),
            (0x4DC2C, 0xC808), (0x4DC30, 0x7608), (0x4DC3A, 0x3626),
            (0x4DC3E, 0xCB08), (0x4DC40, 0xC9F7),
            (0x4DC4C, 0xC810), (0x4DC54, 0x7604), (0x4DC5E, 0x3622),
            (0x4DC62, 0xC9EF), (0x4DC64, 0xCB10),
            (0x4DC6C, 0xC820), (0x4DC72, 0x7604), (0x4DC7C, 0x3626),
            (0x4DC80, 0xCB20), (0x4DC82, 0xC9DF),
            (0x4DC90, 0xC802), (0x4DC94, 0x7603), (0x4DC96, 0xE26E),
            (0x4DC9A, 0x3622), (0x4DC9E, 0xC9FD), (0x4DCA0, 0xCB02),
            (0x4DCBE, 0xC83E), (0x4DCC6, 0xE200), (0x4DCCA, 0x6260),
        ))
        self.assertEqual(mov_l_literal(rom, 0x4DC16), 0x8897)
        self.assertEqual(mov_l_literal(rom, 0x4DC32), 0x8896)
        self.assertEqual(mov_l_literal(rom, 0x4DC42), 0xFFFF1048)
        self.assertEqual(mov_l_literal(rom, 0x4DC56), 0x8768)
        self.assertEqual(mov_l_literal(rom, 0x4DC74), 0x8767)
        self.assertEqual(mov_l_literal(rom, 0x4DC84), 0xFFFF1072)
        self.assertEqual(mov_l_literal(rom, 0x4DCC8), 0xFFFF564C)

    def test_idle_adjustment_source(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x42E5A), 0x870E)
        self.assertEqual(u8(rom, 0x870E) & 1, 0)
        self.assertEqual(u16(rom, 0x42E5E), 0xC801)
        self.assertEqual(mov_l_literal(rom, 0x42E66), 0xFFFF41A9)
        self.assertOps((
            (0x42E68, 0xE010), (0x42E6C, 0xC801),  # 0xFFFF41B9 bit 0
            (0x42E70, 0xE046), (0x42E74, 0xC808),  # 0xFFFF41EF bit 3
            (0x42E8E, 0x3467), (0x42E94, 0x6643),  # min(0xFFFF3168, 20)
            (0x42E96, 0xC810),                     # bit 4: automatic step
            (0x42EA0, 0xE5C0), (0x42EAC, 0xE604), (0x42EB6, 0x4608),
            (0x42ECA, 0x3647), (0x42ECE, 0xE600),
            (0x42ED2, 0xE044), (0x42ED4, 0x0264),  # 0xFFFF56B2 + 0x44
            (0x42EE2, 0x845C),                     # ROM8[0x12748 + 12]
        ))
        self.assertEqual(conditional_target(rom, 0x42E6E), 0x42ECE)
        self.assertEqual(mov_w_literal(rom, 0x42E7A), 0x0870)
        self.assertEqual(mov_w_literal(rom, 0x42EBA), 0x0872)
        self.assertEqual(mov_l_literal(rom, 0x42E86), 0x8903)
        self.assertEqual(u16(rom, 0x42E8A), 0x8426)  # ROM8[0x8909]
        self.assertEqual(mov_l_literal(rom, 0x42ED0), 0xFFFF56B2)
        self.assertEqual(mov_l_literal(rom, 0x42EE0), 0x12748)
        self.assertEqual(u8(rom, 0x12754), 44)

    def test_automatic_branch(self):
        rom = self.rom
        # FUN_000682A2 counts changes of 0xFFFF417E bit 6 against 0xFFFF4180.
        self.assertEqual(mov_l_literal(rom, 0x682A2), 0xFFFF417C)
        self.assertOps(((0x682A4, 0x8472), (0x682AE, 0x8474),
                        (0x682C0, 0xE5FF), (0x682DA, 0x0454)))
        self.assertEqual(mov_w_literal(rom, 0x682C2), 0x027A)
        # FUN_000682E0 closes the decision window.
        self.assertEqual(mov_l_literal(rom, 0x682E0), 0xFFFF244F)
        self.assertEqual(mov_l_literal(rom, 0x682E8), 0xFFFF41A9)
        self.assertOps(((0x682E4, 0xC820), (0x682EC, 0xCB08),
                        (0x682F0, 0x8061)))
        # FUN_000682F6 selects the request.
        self.assertEqual(mov_l_literal(rom, 0x682F8), 0xFFFF417E)
        self.assertEqual((u8(rom, 0x8B34), u8(rom, 0x8B42)), (0x81, 0xE0))
        self.assertOps((
            (0x682FE, 0xC808), (0x68306, 0xC802), (0x68310, 0xE603),
            (0x68312, 0x3262), (0x6831A, 0xC802), (0x6831E, 0xC801),
            (0x68322, 0x846E), (0x68324, 0xC810), (0x6832C, 0xC840),
            (0x68330, 0xC820), (0x68334, 0xC43B), (0x68336, 0xC801),
            (0x68346, 0x3263), (0x6834C, 0xC840), (0x68354, 0xCF01),
            (0x68356, 0xCDFE), (0x6835C, 0xCF40), (0x68360, 0xC9FE),
            (0x68366, 0xCDBF),
        ))
        self.assertEqual(mov_l_literal(rom, 0x68316), 0x8B34)
        self.assertEqual(gbr_byte(u16(rom, 0x682FC), 0xFFFF417E), 0xFFFF41AA)
        self.assertEqual(0xFFFF417E + 0x71, 0xFFFF41EF)
        # FUN_0006836E withdraws the requests.
        self.assertOps((
            (0x68378, 0xC802), (0x6837E, 0xC403), (0x68386, 0xC820),
            (0x68392, 0xCDFE), (0x68396, 0xCDBF), (0x6839C, 0xC803),
            (0x683A4, 0xCDFE), (0x683A8, 0xC80C), (0x683AE, 0xCDBF),
        ))
        self.assertEqual(mov_l_literal(rom, 0x68370), 0xFFFF41A5)
        self.assertEqual((0xFFFF41A5 + 5, 0xFFFF41A5 + 0x4A),
                         (0xFFFF41AA, 0xFFFF41EF))
        # FUN_000685F2 routes the requests.
        self.assertEqual(mov_l_literal(rom, 0x685F4), 0xFFFF4184)
        self.assertOps((
            (0x68606, 0xC980), (0x6860E, 0xC840), (0x68612, 0xC422),
            (0x68614, 0xC802), (0x6861E, 0xC820), (0x68624, 0xC820),
            (0x68628, 0x2118), (0x6862C, 0xC4C8), (0x68630, 0xC426),
            (0x68632, 0xC801), (0x68638, 0xC9DF), (0x6863A, 0xCB20),
            (0x6863C, 0xC0C8), (0x6863E, 0xC46B), (0x68640, 0xC840),
            (0x6864A, 0xC801), (0x68652, 0xCB10), (0x68656, 0xC9EF),
            (0x6865A, 0xC06B), (0x68664, 0xCDDF), (0x68668, 0xCDEF),
        ))
        self.assertEqual(mov_l_literal(rom, 0x68646), 0x870E)

    def test_stored_records(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x6804A), 0xFFFF4184)
        self.assertEqual(mov_w_literal(rom, 0x68050), 0xFFFF9A65)
        self.assertOps((
            (0x6805E, 0xC810), (0x68066, 0xC9CF),        # bit 4 clears 4, 5
            (0x68070, 0xC980), (0x6807A, 0xC801),        # 4184 bit 7, 41AA bit 0
            (0x68080, 0xC914), (0x68082, 0x8814),        # LID-1 edge, accepted
            (0x68086, 0xE027), (0x68088, 0xCF80),        # latch 41AB bit 7
            (0x6808C, 0xC920),                           # writer busy
            (0x68096, 0xC880),
            (0x680A2, 0x6250), (0x680A4, 0xE674),        # record 0x74
            (0x680A6, 0x0724), (0x680AC, 0x4218),
            (0x680AE, 0x0764), (0x680B8, 0x252B), (0x680BA, 0x0755),
            (0x680BE, 0xCB20), (0x680C6, 0xCDFE), (0x680CC, 0xCD7F),
            (0x680DA, 0xC840), (0x680E0, 0xC810), (0x680E6, 0xC801),
            (0x680EA, 0xE06B), (0x680EC, 0xCF20),        # idle latch
            (0x680F6, 0xC820), (0x680FC, 0xE674),
            (0x68104, 0x0724), (0x6810A, 0x0764), (0x68116, 0x4518),
            (0x6811A, 0x0725), (0x6811E, 0xCB20),
            (0x68124, 0xCDBF), (0x68126, 0xCDDF),
            (0x68136, 0xC42F), (0x68138, 0xC840),        # LID-3 edge
            (0x6813E, 0xE27E), (0x68144, 0x0724), (0x68146, 0x8458),
            (0x6814C, 0x4518), (0x6814E, 0x0755), (0x68152, 0xCB20),
            (0x681A0, 0xE273), (0x681DE, 0xE24E), (0x6822C, 0xE270),
        ))
        self.assertEqual(mov_l_literal(rom, 0x6809A), 0xFFFF56B2)
        self.assertEqual(mov_l_literal(rom, 0x6809E), 0xFFFF28F8)
        self.assertEqual(u16(rom, 0x6809C), 0xE0CE)  # 0xFFFF29C6
        self.assertEqual(mov_w_literal(rom, 0x680AA), 0x03DE)  # 0xFFFF2CD6
        self.assertEqual(mov_w_literal(rom, 0x680B0), 0x0872)  # 0xFFFF316A
        self.assertEqual(mov_w_literal(rom, 0x680B4), 0x03EA)  # 0xFFFF2CE2
        self.assertEqual(mov_w_literal(rom, 0x680FE), 0x0870)  # 0xFFFF3168
        self.assertEqual(0xFFFF28F8 + 0x3DE, 0xFFFF2CD6)
        self.assertEqual(0xFFFF28F8 + 0x3EA, 0xFFFF2CE2)
        # FUN_000686B8 restores records 0x74 and 0x7E.
        self.assertEqual(mov_l_literal(rom, 0x686C6), 0x6727C)
        self.assertOps((
            (0x686C2, 0xC801), (0x686C8, 0x420B), (0x686CA, 0xE474),
            (0x686CE, 0xE47E), (0x686D0, 0x420B), (0x686DC, 0xC801),
            (0x686E2, 0xE0CE), (0x686EC, 0x4519), (0x686EE, 0x0754),
            (0x686F2, 0x0764), (0x686F8, 0x4019), (0x686FA, 0x8068),
        ))
        self.assertEqual(mov_w_literal(rom, 0x686F0), 0x0872)
        self.assertEqual(mov_l_literal(rom, 0x686F6), 0xFFFF56B2)
        # FUN_0002D120 calls the step at startup.
        self.assertEqual(mov_l_literal(rom, 0x2D3F8), 0x686B8)
        self.assertEqual(u16(rom, 0x2D3FA), 0x420B)
        # FUN_0006727C compares two SCI2 reads for ROM8[0x8A37] attempts.
        self.assertEqual(mov_l_literal(rom, 0x6728E), 0x8A37)
        self.assertEqual(u8(rom, 0x8A37), 3)
        self.assertEqual(branch_target(rom, 0x672A0), 0x66BD0)
        self.assertEqual(branch_target(rom, 0x672A8), 0x66BD0)
        self.assertOps(((0x672B2, 0x3E50), (0x672B8, 0xCDFE),
                        (0x672CC, 0xCF01), (0x672CE, 0xE000)))

    def test_lids_4_to_20_status(self):
        rom = self.rom
        self.assertEqual(mov_l_literal(rom, 0x34FEE), 0xFFFF4124)
        self.assertOps((
            (0x34FF4, 0xC4E9), (0x34FF8, 0xC495), (0x34FFA, 0xC901),
            (0x34FFE, 0xC460), (0x35002, 0xC980),
            (0x3500C, 0xE0FF), (0x3500E, 0xC046),  # 0xFFFF416A = 0xFF
            (0x35010, 0xE000), (0x35012, 0xC047),
            (0x35016, 0xCB01), (0x3501A, 0xC0E9),
            (0x3501E, 0xC9FE), (0x35022, 0xC0E9),
            (0x35026, 0xE0A6), (0x35028, 0xE0A1), (0x3502C, 0xC046),
            (0x35030, 0xE002), (0x35032, 0xE001), (0x35034, 0xC047),
            (0x3503A, 0xC8C0),
        ))
        self.assertEqual(conditional_target(rom, 0x35024), 0x3502A)
        self.assertEqual(mov_w_literal(rom, 0x35036), 0xFFFF99F4)
        self.assertEqual(mov_l_literal(rom, 0x35048), 0xFFFF4558)
        self.assertEqual(mov_w_literal(rom, 0x3504C), 0x100C)
        self.assertEqual(0xFFFF4558 + 0x100C, 0xFFFF5564)

    def test_diagnostic_identity(self):
        rom = self.rom
        # High DID byte 0x11 indexes the byte-pointer table at 0x226AC.
        self.assertEqual(0x226AC + 4 * 0x2D, TIMING_DID_POINTER)
        self.assertEqual(0x226AC + 4 * 0x2E, IDLE_DID_POINTER)
        self.assertEqual(u32(rom, TIMING_DID_POINTER), 0xFFFF564C)
        self.assertEqual(u32(rom, IDLE_DID_POINTER), 0xFFFF5690)
        timing = self.bindings["ignition-timing-adjustment-did-112d"]
        idle = self.bindings["idle-speed-adjustment-did-112e"]
        self.assertEqual((timing["firmware_addr"], idle["firmware_addr"]),
                         ("ffff564c", "ffff5690"))
        self.assertIn("rom_const:00022760=ffff564c", timing["evidence"])
        self.assertIn("rom_const:00022764=ffff5690", idle["evidence"])
        self.assertEqual(timing["source_claim_id"],
                         "ecudocs-p32m-997c5a9:data:cid-112dh-crrctd-ign-tim-f2c3d2db")
        self.assertEqual(idle["source_claim_id"],
                         "ecudocs-p32m-997c5a9:data:cid-112eh-crrct-idl-rpm-e5544d19")
        for row in (timing, idle):
            self.assertEqual((row["rom_scope"], row["applicability"]),
                             ("exact-code", "nissan_family_candidate"))

    def test_ledger_rows(self):
        for addr, role in NEW_FUNCTIONS.items():
            with self.subTest(addr=addr):
                self.assertEqual(self.funcs[addr]["role"], role)
                self.assertEqual(self.funcs[addr]["confidence"], "code")
        for addr in NEW_REGISTERS:
            with self.subTest(addr=addr):
                self.assertEqual(self.vars[addr]["confidence"], "code")
        self.assertIn("TARGET IGN TIM ADJ", self.funcs["0004aad0"]["semantics"])
        self.assertIn("TARGET IGN TIM ADJ", self.vars["ffff564c"]["semantics"])
        self.assertIn("TARGET IDLE RPM ADJ", self.vars["ffff56f6"]["semantics"])
        self.assertIn("DID 0x112d", self.vars["ffff564c"]["semantics"])
        self.assertIn("DID 0x112e", self.vars["ffff5690"]["semantics"])
        self.assertIn("rom_const:00022760=ffff564c", self.vars["ffff564c"]["evidence"])
        self.assertIn("rom_const:00022764=ffff5690", self.vars["ffff5690"]["evidence"])
        self.assertIn("SID 0x3b selects FUN_00034194 through entry 0x2fb0c",
                      self.funcs["0002f928"]["semantics"])

    def test_published_lid_table(self):
        rom = self.rom

        def fields(lid):
            word = u16(rom, LID_TABLE + 2 * lid)
            apply_bit = (word & 0xFF).bit_length() - 1
            return word, 0xFFFF99F4 + (word >> 8), apply_bit, 0xFFFF99DB + lid

        for lid in range(1, 5):
            word, flag, apply_bit, slot = fields(lid)
            with self.subTest(lid=lid):
                self.assertIn(
                    f"| {lid} | `0x{word:04X}` | `0x{flag:08X}` | {apply_bit} "
                    f"| {apply_bit + 1} | `0x{slot:08X}` |",
                    self.spec,
                )
        for first in range(5, 21, 4):
            rows = [fields(lid) for lid in range(first, first + 4)]
            self.assertEqual(len({flag for _, flag, _, _ in rows}), 1)
            with self.subTest(lids=f"{first}..{first + 3}"):
                self.assertIn(
                    f"| {first}..{first + 3} | `0x{rows[0][0]:04X}..0x{rows[-1][0]:04X}` "
                    f"| `0x{rows[0][1]:08X}` "
                    f"| {', '.join(str(row[2]) for row in rows)} "
                    f"| {', '.join(str(row[2] + 1) for row in rows)} "
                    f"| `0x{rows[0][3]:08X}..0x{rows[-1][3]:08X}` |",
                    self.spec,
                )

    def test_published_window(self):
        rom = self.rom
        coolant = u16(rom, 0x4DC96) & 0xFF        # mov #0x6e,r2
        coolant_band = u16(rom, 0x4DC94) & 0xFF   # add #3,r6
        rpm_band = u16(rom, 0x4DC14) & 0xFF       # add #8,r5
        load_band = u16(rom, 0x4DC54) & 0xFF      # add #4,r6
        low_rpm, high_rpm = u8(rom, 0x8897), u8(rom, 0x8896)
        low_load, high_load = u8(rom, 0x8768), u8(rom, 0x8767)
        self.assertEqual((u16(rom, 0x4DC30) & 0xFF, u16(rom, 0x4DC72) & 0xFF),
                         (rpm_band, load_band))
        rows = (
            f"| 1 | raw coolant `0xFFFF1079` | at or above {coolant} "
            f"({coolant - 50} deg C) | below {coolant - coolant_band} |",
            f"| 2 | RPM/25 `0xFFFF11B3` | at or above `ROM8[0x8897] = {low_rpm}` "
            f"({low_rpm * 25} rpm) | below {low_rpm - rpm_band} "
            f"({(low_rpm - rpm_band) * 25} rpm) |",
            f"| 3 | RPM/25 `0xFFFF11B3` | at or below {high_rpm - rpm_band} "
            f"({(high_rpm - rpm_band) * 25} rpm) | above `ROM8[0x8896] = {high_rpm}` "
            f"({high_rpm * 25} rpm) |",
            f"| 4 | Q7 normalized base fuel schedule `0xFFFF1048` | at or above "
            f"`ROM8[0x8768] = {low_load}` | below {low_load - load_band} |",
            f"| 5 | Q7 normalized base fuel schedule `0xFFFF1048` | at or below "
            f"{high_load - load_band} | above `ROM8[0x8767] = {high_load}` |",
        )
        for row in rows:
            with self.subTest(row=row):
                self.assertIn(row, self.spec)

    def test_published_statements(self):
        rom = self.rom
        spec = self.spec
        statements = (
            f"walks {SCHEDULER_ENTRIES} pointers at `0x2196C..0x21B58`",
            "The bytes are `C0 00 00 00`",
            f"ROM8[0x821D] = {s8(rom, 0x821D)}, ROM8[0x821C] = {s8(rom, 0x821C)})",
            f"`ROM8[0x8CC8] = {u8(rom, 0x8CC8)}` and `ROM8[0x8CC7] = {u8(rom, 0x8CC7)}`",
            f"`ROM8[0x8283] = {u8(rom, 0x8283)}`",
            f"holds for {u8(rom, 0x8283) * 1024 / 10000:.1f} s after the signal clears",
            f"min(0xFFFF99DD, ROM8[0x8909] = {u8(rom, 0x8909)})",
            f"`ROM8[0x12754] = {u8(rom, 0x12754)}`",
            f"gives the stock limit of {u8(rom, 0x8909)} counts as "
            f"{u8(rom, 0x8909) * 25 // 2} rpm",
            f"`ROM8[0x8A37] = {u8(rom, 0x8A37)}` attempts",
            f"`ROM8[0x8B34] = 0x{u8(rom, 0x8B34):02X}`",
            f"`ROM8[0x8B42] = 0x{u8(rom, 0x8B42):02X}`",
            f"`ROM8[0x870E] = 0x{u8(rom, 0x870E):02X}`",
            f"ROM32[0x22760] = 0x{u32(rom, TIMING_DID_POINTER):08X}",
            f"ROM32[0x22764] = 0x{u32(rom, IDLE_DID_POINTER):08X}",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                self.assertIn(statement, spec)


if __name__ == "__main__":
    unittest.main()
