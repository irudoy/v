import csv
import tomllib
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
AXES = ROOT / "defs" / "JK08A.axes.csv"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
INTERP = ROOT / "defs" / "JK08A.interp.csv"
OVERRIDES = ROOT / "defs" / "JK08A.overrides.toml"
FUEL = ROOT / "defs" / "JK08A.fuel.md"

SPEED_WORD = 0xFFFF1196
SPEED_BLOCK = 0xFFFF11D4
SNAPSHOT = 0xFFFF119C
SNAPSHOT_SIZE = 0x38
COMPENSATION_BLOCK = 0xFFFF1114
ETC_BLOCK = 0xFFFF1E60
# 32000000 over the 3.2 us interval of 120 crank degrees, 6250000/RPM counts.
SPEED_WORD_PER_RPM = Fraction(32_000_000, 6_250_000)


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
    """Return the word a PC-relative MOV.W at address loads."""
    opcode = u16(data, address)
    assert opcode >> 12 == 0x9, hex(opcode)
    return u16(data, address + 4 + (opcode & 0xFF) * 2)


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


def names_register(data, start, stop, register):
    """Return the instructions in start..stop whose Rn field is register."""
    return [
        address
        for address in range(start, stop, 2)
        if (u16(data, address) >> 8) & 0xF == register
    ]


def rpm_per_count(shift):
    """Return the RPM of one count of the speed word shifted right by shift."""
    return Fraction(1 << shift) / SPEED_WORD_PER_RPM


def rows(path):
    with path.open(newline="", encoding="utf-8") as source:
        return {row["addr"]: row for row in csv.DictReader(source)}


def evidence(row, field="evidence"):
    return row[field].split(";")


class OverlayLookupOperandTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.axes = rows(AXES)
        cls.findings = rows(FINDINGS)
        cls.vars = rows(VARS)
        with INTERP.open(newline="", encoding="utf-8") as source:
            cls.interp = {row["wrapper"]: row for row in csv.DictReader(source)}
        with OVERRIDES.open("rb") as source:
            cls.overrides = tomllib.load(source)
        cls.fuel = " ".join(FUEL.read_text(encoding="utf-8").split())

    def test_speed_word_counts_rpm_times_5_12(self):
        # FUN_00038272 divides this constant by event interval ffff11fc.
        self.assertEqual(mov_l_literal(self.rom, 0x38280), 32_000_000)
        self.assertEqual(SPEED_WORD_PER_RPM, Fraction(512, 100))
        self.assertEqual(self.vars["ffff1196"]["units"], "rpm*5.12")

    def test_speed_producer_shifts_the_speed_word(self):
        rom = self.rom
        # FUN_000384FE: GBR = ffff11d4 and r13 = ffff1196 >> 3.
        self.assertEqual(mov_l_literal(rom, 0x38506), SPEED_BLOCK)
        self.assertEqual(u16(rom, 0x38508), 0x401E)  # ldc r0,gbr
        self.assertEqual(mov_l_literal(rom, 0x3850A), SPEED_WORD)
        self.assertEqual(u16(rom, 0x3850C), 0x6261)  # mov.w @r6,r2
        self.assertEqual(u16(rom, 0x38510), 0x622D)  # extu.w r2,r2
        self.assertEqual(u16(rom, 0x38512), 0x4209)  # shlr2 r2
        self.assertEqual(u16(rom, 0x38514), 0x4201)  # shlr r2
        self.assertEqual(u16(rom, 0x38516), 0x6D2D)  # extu.w r2,r13
        self.assertEqual(u16(rom, 0x3851A), 0x60D3)  # mov r13,r0
        self.assertEqual(u16(rom, 0x3851C), 0xC10A)  # mov.w r0,@(0x14,gbr)
        # ffff11ee = r13 >> 1.
        self.assertEqual(u16(rom, 0x38546), 0x60D3)
        self.assertEqual(u16(rom, 0x38548), 0x4001)  # shlr r0
        self.assertEqual(u16(rom, 0x3854C), 0xC10D)  # mov.w r0,@(0x1a,gbr)
        # ffff11f4 = r13 >> 3, stored in the delay slot of BSR 0x3846E.
        self.assertEqual(u16(rom, 0x38562), 0x4D09)  # shlr2 r13
        self.assertEqual(u16(rom, 0x38564), 0x4D01)  # shlr r13
        self.assertEqual(u16(rom, 0x38568), 0x60D3)
        self.assertEqual(branch_target(rom, 0x3856A), 0x3846E)
        self.assertEqual(u16(rom, 0x3856C), 0xC110)  # mov.w r0,@(0x20,gbr)
        # r13 keeps ffff1196 >> 3 between its load and the final shifts:
        # the two instructions that name it as Rn only read it.
        self.assertEqual(
            names_register(rom, 0x38518, 0x38562, 0xD), [0x3852E, 0x3853C]
        )
        self.assertEqual(u16(rom, 0x3852E), 0x0D47)  # mul.l r4,r13
        self.assertEqual(u16(rom, 0x3853C), 0x3D47)  # cmp/gt r4,r13
        # FUN_000384CC: ffff11eb = min(255, ffff11e8 >> 4).
        self.assertEqual(branch_target(rom, 0x3856E), 0x384CC)
        self.assertEqual(mov_l_literal(rom, 0x384CC), SPEED_BLOCK)
        self.assertEqual(u16(rom, 0x384CE), 0xE2FF)  # mov #-1,r2
        self.assertEqual(u16(rom, 0x384D0), 0x622C)  # extu.b r2,r2
        self.assertEqual(u16(rom, 0x384D2), 0x855A)  # mov.w @(0x14,r5),r0
        self.assertEqual(u16(rom, 0x384D4), 0x660D)  # extu.w r0,r6
        self.assertEqual(u16(rom, 0x384D6), 0x4609)  # shlr2 r6
        self.assertEqual(u16(rom, 0x384D8), 0x4609)
        self.assertEqual(u16(rom, 0x384DA), 0x3626)  # cmp/hi r2,r6
        self.assertEqual(conditional_target(rom, 0x384DC), 0x384E0)
        self.assertEqual(u16(rom, 0x384DE), 0x6623)  # mov r2,r6
        self.assertEqual(u16(rom, 0x384E0), 0xE017)  # mov #0x17,r0
        self.assertEqual(u16(rom, 0x384E2), 0x000B)  # rts
        self.assertEqual(u16(rom, 0x384E4), 0x0564)  # mov.b r6,@(r0,r5)
        self.assertEqual(SPEED_BLOCK + 0x14, 0xFFFF11E8)
        self.assertEqual(SPEED_BLOCK + 0x17, 0xFFFF11EB)
        self.assertEqual(SPEED_BLOCK + 0x1A, 0xFFFF11EE)
        self.assertEqual(SPEED_BLOCK + 0x20, 0xFFFF11F4)
        self.assertEqual(rpm_per_count(4), Fraction(25, 8))
        self.assertEqual(rpm_per_count(6), Fraction(25, 2))
        self.assertEqual(rpm_per_count(7), 25)

    def test_scheduler_copies_the_speed_block_to_the_snapshot(self):
        rom = self.rom
        # FUN_00020DFE calls block copier 0x220F8 with source r2,
        # destination r1, and size r0.
        self.assertEqual(mov_l_literal(rom, 0x20EFE), 0x220F8)  # r14
        self.assertEqual(names_register(rom, 0x20F00, 0x20F6C, 0xE), [])
        self.assertEqual(mov_l_literal(rom, 0x20F60), SNAPSHOT)  # r1
        self.assertEqual(names_register(rom, 0x20F62, 0x20F6C, 0x1), [])
        self.assertEqual(mov_l_literal(rom, 0x20F6A), SPEED_BLOCK)  # r2
        self.assertEqual(u16(rom, 0x20F6C), 0x4E0B)  # jsr @r14
        self.assertEqual(u16(rom, 0x20F6E), 0xE038)  # mov #0x38,r0
        # The copier enters its unrolled ladder at the entry for the size
        # and loads offset size-4 in the delay slot of the jump.
        self.assertEqual(mov_l_literal(rom, 0x220FA), 0x22158)
        self.assertEqual(u16(rom, 0x220FC), 0x033E)  # mov.l @(r0,r3),r3
        self.assertEqual(u16(rom, 0x220FE), 0x70FC)  # add #-4,r0
        self.assertEqual(u16(rom, 0x22100), 0x432B)  # jmp @r3
        self.assertEqual(u16(rom, 0x22102), 0x002E)  # mov.l @(r0,r2),r0
        self.assertEqual(u32(rom, 0x22158 + SNAPSHOT_SIZE), 0x2211E)
        loaded = {0: SNAPSHOT_SIZE - 4}
        copied = []
        for address in range(0x2211E, 0x22154, 2):
            opcode = u16(rom, address)
            top = opcode >> 12
            n = (opcode >> 8) & 0xF
            m = (opcode >> 4) & 0xF
            disp = (opcode & 0xF) * 4
            if top == 0x5 and m == 2:  # mov.l @(disp,r2),Rn
                loaded[n] = disp
            elif top == 0x1 and n == 1:  # mov.l Rm,@(disp,r1)
                copied.append((loaded.pop(m), disp))
            elif opcode == 0x6322:  # mov.l @r2,r3
                loaded[3] = 0
            elif opcode == 0x2132:  # mov.l r3,@r1
                copied.append((loaded.pop(3), 0))
            else:
                self.fail(f"{address:#x}: {opcode:#06x}")
        self.assertEqual(
            copied,
            [(offset, offset) for offset in range(SNAPSHOT_SIZE - 4, -4, -4)],
        )
        self.assertEqual(u16(rom, 0x22154), 0x000B)  # rts
        for source, destination in (
            (0xFFFF11EB, 0xFFFF11B3),
            (0xFFFF11EE, 0xFFFF11B6),
            (0xFFFF11F4, 0xFFFF11BC),
        ):
            with self.subTest(source=hex(source)):
                self.assertLess(source - SPEED_BLOCK, SNAPSHOT_SIZE)
                self.assertEqual(SNAPSHOT + source - SPEED_BLOCK, destination)

    def test_fuel_compensation_sites_pass_the_speed_word_and_the_qh0_byte(self):
        rom = self.rom
        # FUN_0002C648: the column byte goes to @(3,r15), the row word to r7.
        self.assertEqual(mov_l_literal(rom, 0x2CC7C), COMPENSATION_BLOCK)  # r12
        self.assertEqual(names_register(rom, 0x2CC7E, 0x2CC8A, 0xC), [])
        self.assertEqual(u16(rom, 0x2CC88), 0xE05C)  # mov #0x5c,r0
        self.assertEqual(u16(rom, 0x2CC8A), 0x00CC)  # mov.b @(r0,r12),r0
        self.assertEqual(mov_l_literal(rom, 0x2CC8C), SPEED_BLOCK)  # r3
        self.assertEqual(u16(rom, 0x2CC8E), 0x80F3)  # mov.b r0,@(3,r15)
        self.assertEqual(u16(rom, 0x2CC90), 0xE020)  # mov #0x20,r0
        self.assertEqual(u16(rom, 0x2CC92), 0x0E3D)  # mov.w @(r0,r3),r14
        self.assertEqual(mov_l_literal(rom, 0x2CC94), 0xA29A)  # r4
        self.assertEqual(mov_l_literal(rom, 0x2CC96), 0x11CF0)  # r5
        self.assertEqual(mov_l_literal(rom, 0x2CC98), 0x11D4C)  # r6
        self.assertEqual(mov_l_literal(rom, 0x2CC9A), 0x261F0)
        self.assertEqual(u16(rom, 0x2CC9C), 0x420B)  # jsr @r2
        self.assertEqual(u16(rom, 0x2CC9E), 0x67ED)  # extu.w r14,r7
        # FUN_0003BE3C: r9 = ffff11d4, r10 = ffff1114, r12 = ffff11f4.
        for address in (0x3BE90, 0x3BF2C, 0x3BF60, 0x3C092):
            with self.subTest(r9=hex(address)):
                self.assertEqual(u16(rom, address) >> 8, 0xD9)
                self.assertEqual(mov_l_literal(rom, address), SPEED_BLOCK)
        for address in (0x3BF28, 0x3BFBC):
            with self.subTest(r10=hex(address)):
                self.assertEqual(u16(rom, address) >> 8, 0xDA)
                self.assertEqual(mov_l_literal(rom, address), COMPENSATION_BLOCK)
        self.assertEqual(u16(rom, 0x3C0C4), 0xE020)  # mov #0x20,r0
        self.assertEqual(u16(rom, 0x3C0C8), 0x0C9D)  # mov.w @(r0,r9),r12
        self.assertEqual(u16(rom, 0x3C0CE), 0x6CCD)  # extu.w r12,r12
        self.assertEqual(u16(rom, 0x3C284), 0xE05C)
        self.assertEqual(mov_l_literal(rom, 0x3C286), 0xA29A)
        self.assertEqual(u16(rom, 0x3C288), 0x00AC)  # mov.b @(r0,r10),r0
        self.assertEqual(u16(rom, 0x3C28A), 0x67C3)  # mov r12,r7
        self.assertEqual(mov_l_literal(rom, 0x3C28C), 0x11CF0)
        self.assertEqual(mov_l_literal(rom, 0x3C28E), 0x11D4C)
        self.assertEqual(mov_l_literal(rom, 0x3C290), 0x261F0)
        self.assertEqual(u16(rom, 0x3C292), 0x420B)
        self.assertEqual(u16(rom, 0x3C294), 0x80F3)  # mov.b r0,@(3,r15)
        self.assertEqual(COMPENSATION_BLOCK + 0x5C, 0xFFFF1170)

    def test_fuel_compensation_rows_count_four_speed_word_counts(self):
        rom = self.rom
        # Wrapper 0x261F0: the row axis and word go to byte core 0x269C4,
        # then the column axis and the stacked byte to byte core 0x26944.
        self.assertEqual(u16(rom, 0x261F0), 0x4F22)  # sts.l pr,@-r15
        self.assertEqual(u16(rom, 0x261F2), 0x2F46)  # mov.l r4,@-r15
        self.assertEqual(u16(rom, 0x261F4), 0x677D)  # extu.w r7,r7
        self.assertEqual(u16(rom, 0x261F6), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x261F8), 0x6573)  # mov r7,r5
        self.assertEqual(mov_l_literal(rom, 0x261FA), 0x269C4)
        self.assertEqual(u16(rom, 0x261FC), 0x470B)  # jsr @r7
        self.assertEqual(u16(rom, 0x261FE), 0xE40F)  # mov #15,r4
        self.assertEqual(u16(rom, 0x26200), 0x2F56)  # mov.l r5,@-r15
        self.assertEqual(u16(rom, 0x26202), 0x2F46)
        self.assertEqual(u16(rom, 0x26204), 0x6063)  # mov r6,r0
        # Four pushes put the caller's @(0,r15) at @(16,r15).
        self.assertEqual(u16(rom, 0x26206), 0x55F4)  # mov.l @(16,r15),r5
        self.assertEqual(u16(rom, 0x26208), 0x655C)  # extu.b r5,r5
        self.assertEqual(mov_l_literal(rom, 0x2620A), 0x26944)
        self.assertEqual(u16(rom, 0x2620C), 0x470B)
        # Byte core 0x269C4 multiplies each point and the point span by four.
        self.assertEqual(u16(rom, 0x269C6), 0x014C)  # mov.b @(r0,r4),r1
        self.assertEqual(u16(rom, 0x269C8), 0x611C)  # extu.b r1,r1
        self.assertEqual(u16(rom, 0x269CA), 0x4108)  # shll2 r1
        self.assertEqual(u16(rom, 0x269CC), 0x3150)  # cmp/eq r5,r1
        self.assertEqual(u16(rom, 0x269EC), 0x3018)  # sub r1,r0
        self.assertEqual(u16(rom, 0x269EE), 0x4008)  # shll2 r0
        # Byte core 0x26944 compares each point directly.
        self.assertEqual(u16(rom, 0x26946), 0x014C)
        self.assertEqual(u16(rom, 0x26948), 0x611C)
        self.assertEqual(u16(rom, 0x2694A), 0x3510)  # cmp/eq r1,r5
        self.assertEqual(4 * rpm_per_count(6), 50)

    def test_qh0_byte_follows_throttle_area_over_engine_speed(self):
        rom = self.rom
        # FUN_0003B40A: ffff1f46 = min(65535, ROM8[0x8D8F] * ffff11f4).
        self.assertEqual(mov_l_literal(rom, 0x3B40C), 0x8D8F)
        self.assertEqual(u16(rom, 0x3B40E), 0xE020)  # mov #0x20,r0
        self.assertEqual(u16(rom, 0x3B410), 0x6260)  # mov.b @r6,r2
        self.assertEqual(mov_l_literal(rom, 0x3B412), SPEED_BLOCK)
        self.assertEqual(u16(rom, 0x3B416), 0x026D)  # mov.w @(r0,r6),r2
        self.assertEqual(u16(rom, 0x3B41A), 0x0657)  # mul.l r5,r6
        self.assertEqual(u16(rom, 0x3B422), 0x3267)  # cmp/gt r6,r2
        self.assertEqual(conditional_target(rom, 0x3B424), 0x3B428)
        self.assertEqual(mov_l_literal(rom, 0x3B42A), ETC_BLOCK)
        self.assertEqual(u16(rom, 0x3B42C), 0xE0E6)  # mov #-0x1a,r0
        self.assertEqual(u16(rom, 0x3B42E), 0x600C)  # extu.b r0,r0
        self.assertEqual(u16(rom, 0x3B430), 0x0265)  # mov.w r6,@(r0,r2)
        self.assertEqual(ETC_BLOCK + 0xE6, 0xFFFF1F46)
        # FUN_0003B436: ffff114e = min(65535, 0xDC1D00 / ffff1f46), or 0.
        self.assertEqual(mov_l_literal(rom, 0x3B438), ETC_BLOCK)
        self.assertEqual(u16(rom, 0x3B43E), 0x062D)  # mov.w @(r0,r2),r6
        self.assertEqual(u16(rom, 0x3B442), 0x2008)  # tst r0,r0
        self.assertEqual(conditional_target(rom, 0x3B444), 0x3B45C)
        self.assertEqual(mov_l_literal(rom, 0x3B446), 0x21CE0)
        self.assertEqual(mov_l_literal(rom, 0x3B448), 0xDC1D00)
        self.assertEqual(u16(rom, 0x3B44A), 0x420B)
        self.assertEqual(u16(rom, 0x3B452), 0x3066)  # cmp/hi r6,r0
        self.assertEqual(u16(rom, 0x3B45C), 0xE200)  # mov #0,r2
        self.assertEqual(mov_l_literal(rom, 0x3B45E), COMPENSATION_BLOCK)
        self.assertEqual(u16(rom, 0x3B460), 0xE03A)  # mov #0x3a,r0
        self.assertEqual(u16(rom, 0x3B466), 0x0525)  # mov.w r2,@(r0,r5)
        # FUN_0003B468: ffff1e60 = ffff3a76, or ROM word 0x916C while
        # ffff4246 bit 6 is set.
        self.assertEqual(mov_l_literal(rom, 0x3B468), ETC_BLOCK)
        self.assertEqual(mov_l_literal(rom, 0x3B46A), 0xFFFF4242)
        self.assertEqual(u16(rom, 0x3B46E), 0x8464)  # mov.b @(4,r6),r0
        self.assertEqual(u16(rom, 0x3B470), 0xC940)  # and #0x40,r0
        self.assertEqual(mov_l_literal(rom, 0x3B486), 0xFFFF39C4)
        self.assertEqual(u16(rom, 0x3B488), 0xE0B2)
        self.assertEqual(u16(rom, 0x3B48E), 0x006D)  # mov.w @(r0,r6),r0
        self.assertEqual(mov_l_literal(rom, 0x3B490), 0x916C)
        self.assertEqual(u16(rom, 0x3B496), 0x2101)  # mov.w r0,@r1
        # FUN_0003B520 writes ffff3a76 from two lookups of pair
        # 0x13202/0x155A0 through wrapper 0x26524.
        for address in (0x3B58C, 0x3B59A):  # both branches load r11
            with self.subTest(r11=hex(address)):
                self.assertEqual(u16(rom, address) >> 8, 0xDB)
                self.assertEqual(mov_l_literal(rom, address), 0x26524)
        self.assertEqual(u16(rom, 0x3B6BC) >> 8, 0xDC)
        self.assertEqual(mov_l_literal(rom, 0x3B6BC), 0x13202)  # r12
        self.assertEqual(names_register(rom, 0x3B6C6, 0x3B6E2, 0xC), [])
        for call, axis in ((0x3B6C2, 0x3B6C0), (0x3B6E0, 0x3B6DC)):
            with self.subTest(call=hex(call)):
                self.assertEqual(mov_l_literal(rom, axis), 0x155A0)
                self.assertEqual(u16(rom, call), 0x4B0B)  # jsr @r11
                self.assertEqual(u16(rom, call + 2), 0x64C3)  # mov r12,r4
        self.assertEqual(mov_l_literal(rom, 0x3B5AE), 0xFFFF39C4)  # r9
        self.assertEqual(u16(rom, 0x3B732), 0xE0B2)
        self.assertEqual(u16(rom, 0x3B736), 0x0925)  # mov.w r2,@(r0,r9)
        self.assertEqual(0xFFFF39C4 + 0xB2, 0xFFFF3A76)
        # FUN_0003B498: u from ffff1e60, ffff114e, and ffff120e, then the
        # high byte of curve 0x15042 at 4u or 0x15022 at u - 0x3C00.
        self.assertEqual(mov_l_literal(rom, 0x3B4A0), COMPENSATION_BLOCK)
        self.assertEqual(u16(rom, 0x3B4A2), 0x401E)  # ldc r0,gbr
        self.assertEqual(mov_l_literal(rom, 0x3B4AA), ETC_BLOCK)
        self.assertEqual(u16(rom, 0x3B4B0), 0x6261)  # mov.w @r6,r2
        self.assertEqual(u16(rom, 0x3B4B2), 0xC51D)  # mov.w @(0x3a,gbr),r0
        self.assertEqual(u16(rom, 0x3B4B8), 0x05E7)  # mul.l r14,r5
        self.assertEqual(u16(rom, 0x3B4BC), 0x4419)  # shlr8 r4
        self.assertEqual(u16(rom, 0x3B4BE), 0x4401)  # shlr r4
        self.assertEqual(u16(rom, 0x3B4C8), 0xC57D)  # mov.w @(0xfa,gbr),r0
        self.assertEqual(u16(rom, 0x3B4CC), 0x0527)  # mul.l r2,r5
        self.assertEqual(u16(rom, 0x3B4D0), 0x4519)  # shlr8 r5
        self.assertEqual(u16(rom, 0x3B4D2), 0x4509)  # shlr2 r5
        self.assertEqual(u16(rom, 0x3B4D4), 0x4501)  # shlr r5
        self.assertEqual(u16(rom, 0x3B4D6), 0x345C)  # add r5,r4
        self.assertEqual(u16(rom, 0x3B4D8), 0x3476)  # cmp/hi r7,r4
        self.assertEqual(u16(rom, 0x3B4E4), 0xE63C)  # mov #0x3c,r6
        self.assertEqual(u16(rom, 0x3B4E6), 0x4618)  # shll8 r6
        self.assertEqual(u16(rom, 0x3B4E8), 0x3063)  # cmp/ge r6,r0
        self.assertEqual(conditional_target(rom, 0x3B4EA), 0x3B4F4)
        self.assertEqual(mov_l_literal(rom, 0x3B4EE), 0x15042)
        self.assertEqual(branch_target(rom, 0x3B4F0), 0x3B4FE)
        self.assertEqual(u16(rom, 0x3B4F2), 0x4508)  # shll2 r5
        self.assertEqual(mov_l_literal(rom, 0x3B4FA), 0x15022)
        self.assertEqual(u16(rom, 0x3B4FC), 0x3528)  # sub r2,r5
        self.assertEqual(mov_l_literal(rom, 0x3B4FE), 0x263F4)
        self.assertEqual(u16(rom, 0x3B508), 0x4019)  # shlr8 r0
        self.assertEqual(u16(rom, 0x3B50A), 0xC05C)  # mov.b r0,@(0x5c,gbr)
        self.assertEqual(COMPENSATION_BLOCK + 0x3A, 0xFFFF114E)
        self.assertEqual(COMPENSATION_BLOCK + 0xFA, 0xFFFF120E)

    def test_torque_map_takes_the_speed_snapshot_and_the_stored_coordinate(self):
        rom = self.rom
        # FUN_00065928 copies the 16-word column axis to r15+4.
        self.assertEqual(mov_l_literal(rom, 0x6592E), 0x2378C)  # r2
        self.assertEqual(u16(rom, 0x65930), 0x61F3)  # mov r15,r1
        self.assertEqual(mov_l_literal(rom, 0x65932), 0x22558)
        self.assertEqual(u16(rom, 0x65934), 0x7104)  # add #4,r1
        self.assertEqual(u16(rom, 0x65936), 0xE520)  # mov #0x20,r5
        self.assertEqual(u16(rom, 0x65938), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x6593A), 0x6053)  # mov r5,r0
        # q = min(65535, ffff1024 * 40960 / ROM16[0x9534]).
        self.assertEqual(mov_l_literal(rom, 0x6593C), 0x9534)
        self.assertEqual(u16(rom, 0x6593E), 0x6521)  # mov.w @r2,r5
        self.assertEqual(mov_l_literal(rom, 0x65946), 0xFFFF1024)
        self.assertEqual(u16(rom, 0x65948), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x6594A), 0x6621)  # mov.w @r2,r6
        self.assertEqual(
            [u16(rom, address) for address in range(0x6594C, 0x6595C, 2)],
            [0x666D, 0x6263, 0x4208, 0x326C, 0x4218, 0x6623, 0x4608, 0x4608],
        )
        self.assertEqual(u16(rom, 0x6595E), 0x4600)  # shll r6
        self.assertEqual((4 + 1) << 8 << 2 << 2 << 1, 40960)
        self.assertEqual(mov_l_literal(rom, 0x6595C), 0x21BBC)
        self.assertEqual(u16(rom, 0x65960), 0x420B)
        self.assertEqual(u16(rom, 0x65962), 0x6163)  # mov r6,r1
        self.assertEqual(u16(rom, 0x65970), 0x3266)  # cmp/hi r6,r2
        self.assertEqual(u16(rom, 0x65974), 0x6263)  # mov r6,r2
        # q goes to ffff128c+0x338 and to the stacked column input.
        self.assertEqual(mov_l_literal(rom, 0x65976), 0xFFFF128C)  # r13
        self.assertEqual(mov_w_literal(rom, 0x6597A), 0x0338)
        self.assertEqual(0xFFFF128C + 0x338, 0xFFFF15C4)
        self.assertEqual(u16(rom, 0x65980), 0x0D25)  # mov.w r2,@(r0,r13)
        self.assertEqual(u16(rom, 0x65982), 0x6023)  # mov r2,r0
        self.assertEqual(u16(rom, 0x65984), 0x81F1)  # mov.w r0,@(2,r15)
        # The column axis is the stack copy and the row input is ffff11b6.
        self.assertEqual(u16(rom, 0x65978), 0x66F3)  # mov r15,r6
        self.assertEqual(u16(rom, 0x6597C), 0x7604)  # add #4,r6
        self.assertEqual(mov_l_literal(rom, 0x6597E), SNAPSHOT)  # r7
        self.assertEqual(u16(rom, 0x65986), 0x857D)  # mov.w @(0x1a,r7),r0
        self.assertEqual(mov_l_literal(rom, 0x65988), 0x10B8E)  # r4
        self.assertEqual(mov_l_literal(rom, 0x6598A), 0x14B4A)  # r5
        self.assertEqual(mov_l_literal(rom, 0x6598C), 0x262A8)
        self.assertEqual(u16(rom, 0x6598E), 0x420B)
        self.assertEqual(u16(rom, 0x65990), 0x670D)  # extu.w r0,r7
        self.assertEqual(SNAPSHOT + 0x1A, 0xFFFF11B6)
        # Wrapper 0x262A8 passes both inputs to word core 0x26984.
        self.assertEqual(u16(rom, 0x262AC), 0x677D)  # extu.w r7,r7
        self.assertEqual(u16(rom, 0x262AE), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x262B0), 0x6573)  # mov r7,r5
        self.assertEqual(mov_l_literal(rom, 0x262B2), 0x26984)
        self.assertEqual(u16(rom, 0x262B4), 0x470B)
        self.assertEqual(u16(rom, 0x262BC), 0x6063)  # mov r6,r0
        self.assertEqual(u16(rom, 0x262BE), 0x55F4)  # mov.l @(16,r15),r5
        self.assertEqual(u16(rom, 0x262C0), 0x655D)  # extu.w r5,r5
        self.assertEqual(u16(rom, 0x262C2), 0x470B)
        # Word core 0x26984 compares each point directly.
        self.assertEqual(u16(rom, 0x26986), 0x014D)  # mov.w @(r0,r4),r1
        self.assertEqual(u16(rom, 0x26988), 0x611D)  # extu.w r1,r1
        self.assertEqual(u16(rom, 0x2698A), 0x3510)  # cmp/eq r1,r5

    def test_injection_angle_maps_take_the_rpm25_snapshot(self):
        rom = self.rom
        for site, table in ((0x56CA8, 0x1230A), (0x56E2C, 0x12302)):
            with self.subTest(table=hex(table)):
                self.assertEqual(mov_l_literal(rom, site), SNAPSHOT)  # r5
                self.assertEqual(u16(rom, site + 2), 0xE017)  # mov #0x17,r0
                self.assertEqual(mov_l_literal(rom, site + 4), table)  # r4
                self.assertEqual(u16(rom, site + 6), 0x065C)  # mov.b @(r0,r5),r6
                self.assertEqual(mov_l_literal(rom, site + 8), 0x26370)
                self.assertEqual(u16(rom, site + 10), 0x420B)  # jsr @r2
                self.assertEqual(u16(rom, site + 12), 0x656C)  # extu.b r6,r5
        self.assertEqual(SNAPSHOT + 0x17, 0xFFFF11B3)
        # Wrapper 0x26370 returns point 7 from input 224; below it, kernel
        # 0x26A80 takes the point index from five right shifts.
        self.assertEqual(mov_w_literal(rom, 0x26370), 224)
        self.assertEqual(u16(rom, 0x26372), 0x655C)  # extu.b r5,r5
        self.assertEqual(u16(rom, 0x26374), 0x3502)  # cmp/hs r0,r5
        self.assertEqual(conditional_target(rom, 0x26376), 0x2637E)
        self.assertEqual(mov_l_literal(rom, 0x26378), 0x26A80)
        self.assertEqual(u16(rom, 0x2637A), 0x462B)  # jmp @r6
        self.assertEqual(u16(rom, 0x2637E), 0x000B)  # rts
        self.assertEqual(u16(rom, 0x26380), 0x8447)  # mov.b @(7,r4),r0
        self.assertEqual(rom[0x26A80:0x26A94], bytes.fromhex("45014325") * 5)
        registry = self.interp["00026370"]
        self.assertEqual(
            (registry["kernel"], registry["width"], registry["step"]),
            ("00026a80", "8", "32"),
        )
        self.assertEqual(32 * rpm_per_count(7), 800)

    def test_tracked_records_state_the_bound_operands(self):
        speed = self.axes["00011cf0"]
        self.assertEqual(
            (speed["units"], speed["scale_expr"], speed["scale_conf"]),
            ("RPM", "x*50", "code"),
        )
        self.assertIn(
            "indexed_by:ffff11f4@confidence", evidence(speed, "scale_evidence")
        )
        torque_speed = self.axes["00014b4a"]
        self.assertEqual(
            (
                torque_speed["units"],
                torque_speed["scale_expr"],
                torque_speed["scale_conf"],
            ),
            ("RPM", "x*3.125", "code"),
        )
        self.assertEqual(Fraction("3.125"), rpm_per_count(4))
        self.assertIn(
            "indexed_by:ffff11b6@confidence",
            evidence(torque_speed, "scale_evidence"),
        )
        load = self.axes["0002378c"]
        self.assertEqual(
            (load["units"], load["scale_conf"]), ("Normalized BFS [%]", "code")
        )
        self.assertEqual(
            Fraction(load["scale_expr"].removeprefix("x*")), Fraction(100, 40960)
        )
        self.assertIn(
            "indexed_by:ffff15c4@confidence", evidence(load, "scale_evidence")
        )
        qh0 = self.axes["00011d4c"]
        self.assertEqual(qh0["scale_conf"], "candidate")
        self.assertIn(
            "indexed_by:ffff1170@structural", evidence(qh0, "scale_evidence")
        )
        for table in ("00012302", "0001230a"):
            with self.subTest(table=table):
                tokens = evidence(self.findings[table])
                self.assertIn("indexed_by:ffff11b3@structural", tokens)
                self.assertIn("trace:00026370@structural", tokens)
                override = self.overrides["table"][table]
                self.assertEqual(override["static_axis_operand"], "ffff11b3")
                self.assertEqual(
                    override["static_axis"],
                    [point * 32 * rpm_per_count(7) for point in range(8)],
                )
        self.assertEqual(self.vars["ffff11f4"]["units"], "rpm/12.5")
        self.assertEqual(self.vars["ffff11b6"]["units"], "rpm/3.125")
        self.assertEqual(self.vars["ffff11b3"]["units"], "rpm/25")
        logparam = self.overrides["logparam"]
        self.assertEqual(
            logparam["ffff11f4"], {"id": "X_VQ_Engine_Speed", "units": "RPM"}
        )
        self.assertEqual(
            logparam["ffff11b6"], {"id": "X_VQ_Engine_Speed", "units": "RPM"}
        )
        self.assertEqual(
            logparam["ffff15c4"],
            {"id": "X_VQ_Engine_Load", "units": "Normalized BFS [%]"},
        )
        self.assertEqual(
            logparam["ffff11b3"],
            {"id": "X_VQ_Engine_Speed", "static_axis_name": "Engine Speed [RPM]"},
        )
        self.assertNotIn("ffff1170", logparam)

    def test_published_statements(self):
        for statement in (
            "row axis `0x11CF0` over RPM/12.5 word `0xFFFF11F4` and column "
            "axis `0x11D4C` over byte `0xFFFF1170`",
            "Byte core `0x269C4` compares each row point after multiplication "
            "by four with the RPM/12.5 word, so one row-axis count is 50 RPM.",
            "Byte core `0x26944` compares each column point with `0xFFFF1170` "
            "directly.",
            "`FUN_0003B498` writes that byte as the high byte of curve "
            "`0x15042`, at coordinate `4 * u` below `u = 0x3C00`, or of curve "
            "`0x15022`, at coordinate `u - 0x3C00` from there:",
            "u = min(65535, (0xFFFF1E60 * 0xFFFF114E >> 9) "
            "+ (0xFFFF120E * 0xFFFF114E >> 11))",
            "0xFFFF114E = min(65535, 0xDC1D00 / 0xFFFF1F46), or 0 while "
            "0xFFFF1F46 = 0",
            "0xFFFF1F46 = min(65535, ROM8[0x8D8F] * 0xFFFF11F4)",
            "`FUN_0003B40A` writes `0xFFFF1F46`, and `FUN_0003B436` writes "
            "`0xFFFF114E`, which is inversely proportional to engine speed.",
            "`FUN_0003B468` selects `0xFFFF1E60` from ETC-path value "
            "`0xFFFF3A76`, which `FUN_0003B520` derives through the Throttle "
            "Angle-to-Area pair `0x13202`/`0x155A0`, or from ROM word "
            "`0x916C`.",
        ):
            with self.subTest(statement=statement[:40]):
                self.assertIn(statement, self.fuel)


if __name__ == "__main__":
    unittest.main()
