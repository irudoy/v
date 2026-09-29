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
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
INTERP = ROOT / "defs" / "JK08A.interp.csv"
OVERRIDES = ROOT / "defs" / "JK08A.overrides.toml"
FUEL = ROOT / "defs" / "JK08A.fuel.md"
THROTTLE = ROOT / "defs" / "JK08A.throttle-control.md"

SPEED_WORD = 0xFFFF1196
SPEED_BLOCK = 0xFFFF11D4
SNAPSHOT = 0xFFFF119C
SNAPSHOT_SIZE = 0x38
COMPENSATION_BLOCK = 0xFFFF1114
ETC_BLOCK = 0xFFFF1E60
TORQUE_BLOCK = 0xFFFF128C
INTERVAL_BLOCK = 0xFFFF1FF4
PRIMARY_ROW = 0xFFFF1702
TRUSTFUL_ROW = 0xFFFF1CCA
# 32000000 over the 3.2 us interval of 120 crank degrees, 6250000/RPM counts.
SPEED_WORD_PER_RPM = Fraction(32_000_000, 6_250_000)

# (surface, row axis, column axis, 2D wrapper) of each requested-torque family.
PRIMARY = (0xE98E, 0x11D0C, 0x14114, 0x262E0)
TRUSTFUL = (0x175C8, 0x18716, 0x18AC6, 0x26660)
# Forward lookups that pass the row coordinate: (surface load, base load,
# base register, row load, extu.w r14,r7, call). The row load is
# mov.w @(r0,base),r14 after mov.w #offset,r0 and one mov.l of r4 or r5.
PRIMARY_LOOKUPS = (
    (0x7031E, 0x702D6, 12, 0x70320, 0x7032A, 0x70328),  # FUN_000702C6
    (0x739D0, 0x7398A, 13, 0x739DC, 0x739E4, 0x739E2),  # FUN_00073948
    (0x754A2, 0x7546E, 11, 0x754A4, 0x754AE, 0x754AC),  # FUN_000753D4
    (0x75554, 0x75548, 13, 0x75560, 0x75568, 0x75566),  # FUN_00075540
    (0x75D26, 0x75CEE, 12, 0x75D32, 0x75D3A, 0x75D38),  # FUN_00075C48
    (0x7AAF2, 0x7AAE8, 7, 0x7AAF4, 0x7AAFE, 0x7AAFC),  # FUN_0007A9FC
    (0x7AB54, 0x7AB4E, 12, 0x7AB56, 0x7AB62, 0x7AB60),  # FUN_0007AB18
)
TRUSTFUL_LOOKUPS = (
    (0x73ACC, 0x73A7A, 13, 0x73AD8, 0x73AE0, 0x73ADE),  # FUN_00073A44
    (0x7476E, 0x7474A, 12, 0x74770, 0x7477A, 0x74778),  # FUN_00074728
    (0x74A7E, 0x74A78, 13, 0x74A80, 0x74A86, 0x74A8C),  # FUN_000749BC
    (0x7ADFC, 0x7ADF8, 7, 0x7ADFE, 0x7AE08, 0x7AE06),  # FUN_0007ACB4
)
# Throttle-rev limiter FUN_0007584E passes snapshot ffff11b6 directly.
LIMITER_LOOKUP = 0x75A10
# Inverse lookups FUN_00073432 and FUN_00073628 load the primary surface
# three times and the trustful surface three times.
INVERSE_LOADS = {
    0xE98E: (0x734CE, 0x734E2, 0x7350C),
    0x175C8: (0x736AA, 0x736C8, 0x736F2),
}
# Stack column words: (mov #imm,r0, mov.w r0,@(2,r15), imm).
FIXED_COLUMNS = (
    (0x70318, 0x7031A, 0xFF),  # FUN_000702C6
    (0x75558, 0x7555A, 0xFF),  # FUN_00075540
    (0x75D2A, 0x75D2C, 0xFF),  # FUN_00075C48
    (0x7AB4C, 0x7AB50, 0xFF),  # FUN_0007AB18
    (0x74A76, 0x74A7A, 0xFF),  # FUN_000749BC
    (0x75A0A, 0x75A0C, 0x00),  # FUN_0007584E
)
# Primary tables and constants of FUN_00073948 and their trustful copies
# in FUN_00073A44, with the byte length of each.
CONVERSION_COPIES = (
    (0x0E98E, 0x175C8, 512),  # surface
    (0x11D0C, 0x18716, 16),  # row axis
    (0x14114, 0x18AC6, 32),  # column axis
    (0x13202, 0x18766, 64),  # opening area
    (0x155A0, 0x190D0, 64),  # throttle angle axis
    (0x15690, 0x18FD6, 64),  # lower segment
    (0x15500, 0x18E86, 64),  # lower segment axis
    (0x156D0, 0x18F96, 64),  # upper segment
    (0x15540, 0x18E46, 64),  # upper segment axis
    (0x08D8F, 0x15F82, 1),  # divisor
)


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


def stores_through(data, start, stop, register):
    """Return whether every instruction in start..stop that names register
    as Rn is a store addressed through it, which leaves it unchanged."""
    for address in names_register(data, start, stop, register):
        opcode = u16(data, address)
        top, low = opcode >> 12, opcode & 0xF
        if not (
            (top == 0x0 and low in (4, 5, 6))  # mov.x Rm,@(r0,Rn)
            or top == 0x1  # mov.l Rm,@(disp,Rn)
            or (top == 0x2 and low in (0, 1, 2))  # mov.x Rm,@Rn
        ):
            return False
    return True


def pc_literal_loads(data, value):
    """Return every PC-relative MOV.L in data that loads value."""
    pattern = value.to_bytes(4, "big")
    loads = []
    literal = data.find(pattern)
    while literal != -1:
        if literal % 4 == 0:
            # A MOV.L reaches literals up to 255 longwords past (PC + 4) & ~3.
            for address in range(max(0, literal - 1024), literal, 2):
                opcode = u16(data, address)
                if (
                    opcode >> 12 == 0xD
                    and ((address + 4) & ~3) + (opcode & 0xFF) * 4 == literal
                ):
                    loads.append(address)
        literal = data.find(pattern, literal + 1)
    return sorted(loads)


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
        cls.throttle = " ".join(THROTTLE.read_text(encoding="utf-8").split())

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
            (0xFFFF1208, 0xFFFF11D0),
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
        # FUN_0003BD74: r9 = ffff11d4, r10 = ffff1114, r12 = ffff11f4.
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

    def test_maf_range_monitors_evaluate_the_qh0_curves(self):
        rom = self.rom
        # FUN_0008152A (P0101) and FUN_00081D74 (P010B) read inflow area
        # ffff120e and both curves of FUN_0003B498 on two paths each.
        for loads, value in (
            ((0x815C4, 0x8163C, 0x81E5C, 0x81ED8), 0xFFFF120E),
            ((0x81606, 0x8166E, 0x81EA2, 0x81F0A), 0x15042),
            ((0x81610, 0x81676, 0x81EAC, 0x81F12), 0x15022),
        ):
            for load in loads:
                with self.subTest(load=hex(load)):
                    self.assertEqual(mov_l_literal(rom, load), value)
        self.assertEqual(mov_l_literal(rom, 0x3B4EE), 0x15042)
        self.assertEqual(mov_l_literal(rom, 0x3B4FA), 0x15022)
        # The two curves of 16 words span high bytes 4..204 and 204..224.
        lower = [rom[0x15042 + 2 * index] for index in range(16)]
        upper = [rom[0x15022 + 2 * index] for index in range(16)]
        self.assertEqual((min(lower), max(lower)), (4, 204))
        self.assertEqual((min(upper), max(upper)), (204, 224))
        # 0xDC1D00 / (8 * RPM) scaled by 2^-9 is 3522 / RPM.
        self.assertEqual(round(Fraction(0xDC1D00, 8 * 512)), 3522)

    def test_requested_torque_row_coordinates_clamp_the_speed_snapshots(self):
        rom = self.rom
        # FUN_0003DE4C: GBR = ffff119c.
        self.assertEqual(mov_l_literal(rom, 0x3DE4E), SNAPSHOT)
        self.assertEqual(u16(rom, 0x3DE50), 0x401E)  # ldc r0,gbr
        self.assertEqual(
            [u16(rom, address) for address in range(0x3DE52, 0x3DE78, 2)],
            [
                0xC50D,  # mov.w @(0x1a,gbr),r0: ffff11b6
                0xE520,  # mov #0x20,r5
                0x670D,  # extu.w r0,r7
                0x3753,  # cmp/ge r5,r7
                0x8D01,  # bt/s 0x3DE60
                0x6273,  # mov r7,r2
                0xE220,  # mov #0x20,r2
                0xD41E,  # mov.l @(0x3dedc,pc),r4
                0x9034,  # mov.w @(0x3dece,pc),r0
                0x0425,  # mov.w r2,@(r0,r4): ffff1702
                0xC51A,  # mov.w @(0x34,gbr),r0: ffff11d0
                0x620D,  # extu.w r0,r2
                0x3253,  # cmp/ge r5,r2
                0x8900,  # bt 0x3DE70
                0xE220,  # mov #0x20,r2
                0xD41A,  # mov.l @(0x3dedc,pc),r4
                0x6673,  # mov r7,r6
                0x902C,  # mov.w @(0x3ded0,pc),r0
                0x0425,  # mov.w r2,@(r0,r4): ffff1cca
            ],
        )
        self.assertEqual(conditional_target(rom, 0x3DE5A), 0x3DE60)
        self.assertEqual(conditional_target(rom, 0x3DE6C), 0x3DE70)
        self.assertEqual(mov_l_literal(rom, 0x3DE60), TORQUE_BLOCK)
        self.assertEqual(mov_l_literal(rom, 0x3DE70), TORQUE_BLOCK)
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x3DE62), PRIMARY_ROW)
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x3DE74), TRUSTFUL_ROW)
        self.assertEqual(SNAPSHOT + 0x1A, 0xFFFF11B6)
        self.assertEqual(SNAPSHOT + 0x34, 0xFFFF11D0)
        # The clamp at 32 counts is 100 RPM, below the first row point.
        self.assertEqual(32 * rpm_per_count(4), 100)

    def test_trustful_speed_word_has_the_primary_representation(self):
        rom = self.rom
        # FUN_000385BC: ffff1206 = 12000000 / (ROM8[0x88FB] * ffff22d4) and
        # ffff1208 = uint16(ffff1206) >> 1, or zero for both while
        # ffff417f bit 5 is set. Divider 0x21CE0 returns r1 / r0.
        self.assertEqual(mov_l_literal(rom, 0x385C2), SPEED_BLOCK)
        self.assertEqual(u16(rom, 0x385C4), 0x401E)  # ldc r0,gbr
        self.assertEqual(mov_l_literal(rom, 0x385C6), 0xFFFF417F)
        self.assertEqual(u16(rom, 0x385C8), 0x6060)  # mov.b @r6,r0
        self.assertEqual(u16(rom, 0x385CA), 0xC820)  # tst #0x20,r0
        self.assertEqual(conditional_target(rom, 0x385CC), 0x385E8)
        self.assertEqual(mov_l_literal(rom, 0x385CE), 0x88FB)  # r6
        self.assertEqual(mov_l_literal(rom, 0x385D0), INTERVAL_BLOCK)  # r5
        self.assertEqual(u16(rom, 0x385D2), 0x6260)  # mov.b @r6,r2
        self.assertEqual(mov_w_literal(rom, 0x385D4), 0x2E0)
        self.assertEqual(u16(rom, 0x385D6), 0x662C)  # extu.b r2,r6
        self.assertEqual(mov_l_literal(rom, 0x385D8), 12_000_000)  # r1
        self.assertEqual(u16(rom, 0x385DA), 0x025E)  # mov.l @(r0,r5),r2
        self.assertEqual(u16(rom, 0x385DC), 0x0267)  # mul.l r6,r2
        self.assertEqual(mov_l_literal(rom, 0x385DE), 0x21CE0)
        self.assertEqual(u16(rom, 0x385E0), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x385E2), 0x001A)  # sts macl,r0
        self.assertEqual(branch_target(rom, 0x385E4), 0x385EC)
        self.assertEqual(u16(rom, 0x385E6), 0x6203)  # mov r0,r2
        self.assertEqual(u16(rom, 0x385E8), 0xE200)  # mov #0,r2
        self.assertEqual(u16(rom, 0x385EA), 0x6023)  # mov r2,r0
        self.assertEqual(u16(rom, 0x385EC), 0xC119)  # mov.w r0,@(0x32,gbr)
        self.assertEqual(u16(rom, 0x385EE), 0x602D)  # extu.w r2,r0
        self.assertEqual(u16(rom, 0x385F0), 0x4001)  # shlr r0
        self.assertEqual(u16(rom, 0x385F2), 0xC11A)  # mov.w r0,@(0x34,gbr)
        self.assertEqual(rom[0x88FB], 3)
        self.assertEqual(INTERVAL_BLOCK + 0x2E0, 0xFFFF22D4)
        self.assertEqual(SPEED_BLOCK + 0x32, 0xFFFF1206)
        self.assertEqual(SPEED_BLOCK + 0x34, 0xFFFF1208)
        # Event handler FUN_000208F8 calls both interval samplers in turn.
        self.assertEqual(mov_l_literal(rom, 0x20908), 0x28AF8)
        self.assertEqual(mov_l_literal(rom, 0x2090E), 0x28B5C)
        for call in (0x2090A, 0x20910):
            self.assertEqual(u16(rom, call), 0x420B)  # jsr @r2
            self.assertEqual(u16(rom, call + 2), 0x0009)  # nop
        # Both samplers apply the same gates to capture ffff185c, form
        # (capture - previous) >> 5 with the same borrow, and keep the
        # capture as their own previous value in r1.
        for entry, previous, gate, lock, capture, borrow, shifts, keep in (
            (
                0x28AF8, 0xFFFF84CC, 0x28AFA, 0x28B02, 0x28B12, 0x28B18,
                (0x28B24, 0x28B26, 0x28B2C), 0x28B34,
            ),
            (
                0x28B5C, 0xFFFF84D0, 0x28B5E, 0x28B66, 0x28B78, 0x28B7E,
                (0x28B88, 0x28B8C, 0x28B90), 0x28B94,
            ),
        ):
            with self.subTest(sampler=hex(entry)):
                self.assertEqual(u16(rom, entry) >> 8, 0x91)  # mov.w ...,r1
                self.assertEqual(mov_w_literal(rom, entry) | 0xFFFF0000, previous)
                self.assertEqual(names_register(rom, entry + 2, keep + 8, 1), [])
                self.assertEqual(mov_l_literal(rom, gate), 0xFFFF24C8)
                self.assertEqual(u16(rom, gate + 2), 0x8461)  # mov.b @(1,r6),r0
                self.assertEqual(u16(rom, gate + 4), 0xC820)  # tst #0x20,r0
                self.assertEqual(mov_l_literal(rom, lock), 0xFFFF25FB)
                self.assertEqual(u16(rom, lock + 2), 0x8464)  # mov.b @(4,r6),r0
                self.assertEqual(u16(rom, lock + 4), 0x2008)  # tst r0,r0
                for load in (capture, keep):
                    self.assertEqual(mov_l_literal(rom, load), TORQUE_BLOCK)
                    self.assertEqual(
                        TORQUE_BLOCK + mov_w_literal(rom, load + 2), 0xFFFF185C
                    )
                self.assertEqual(u16(rom, capture + 4), 0x046E)  # mov.l @(r0,r6),r4
                self.assertEqual(
                    [u16(rom, borrow + offset) for offset in range(0, 10, 2)],
                    [0x6012, 0x3402, 0x8D01, 0x3408, 0x74FF],
                )  # mov.l @r1,r0; cmp/hs r0,r4; bt/s; sub r0,r4; add #-1,r4
                self.assertEqual(
                    [u16(rom, shift) for shift in shifts], [0x4409, 0x4409, 0x4401]
                )  # shlr2 r4; shlr2 r4; shlr r4
                self.assertEqual(u16(rom, keep + 4), 0x006E)  # mov.l @(r0,r6),r0
                self.assertEqual(u16(rom, keep + 6), 0x000B)  # rts
                self.assertEqual(u16(rom, keep + 8), 0x2102)  # mov.l r0,@r1
        # Sampler 0x28AF8 stores ffff11fc and sampler 0x28B5C ffff22d4.
        self.assertEqual(mov_l_literal(rom, 0x28B28), SPEED_BLOCK)  # r5
        self.assertEqual(u16(rom, 0x28B2E), 0x154A)  # mov.l r4,@(0x28,r5)
        self.assertEqual(mov_l_literal(rom, 0x28B8A), INTERVAL_BLOCK)  # r5
        self.assertEqual(mov_w_literal(rom, 0x28B8E), 0x2E0)
        self.assertEqual(u16(rom, 0x28B92), 0x0546)  # mov.l r4,@(r0,r5)
        self.assertEqual(SPEED_BLOCK + 0x28, 0xFFFF11FC)
        # FUN_0002B768 stores r6 to both words.
        self.assertEqual(mov_l_literal(rom, 0x2B7A0), INTERVAL_BLOCK)  # r10
        self.assertTrue(stores_through(rom, 0x2B7A2, 0x2B80A, 0xA))
        self.assertEqual(mov_l_literal(rom, 0x2B800), SPEED_BLOCK)  # r12
        self.assertEqual(mov_w_literal(rom, 0x2B804), 0x2E0)
        self.assertEqual(u16(rom, 0x2B80A), 0x0A66)  # mov.l r6,@(r0,r10)
        self.assertEqual(u16(rom, 0x2B812), 0x1C6A)  # mov.l r6,@(0x28,r12)
        self.assertEqual(names_register(rom, 0x2B80C, 0x2B812, 6), [])
        # FUN_0002C648 stores r9 to both words; between the stores, the only
        # instruction whose Rn field reads 9 is and #0xdf,r0.
        self.assertEqual(mov_l_literal(rom, 0x2C674), INTERVAL_BLOCK)  # r12
        self.assertTrue(stores_through(rom, 0x2C676, 0x2CA44, 0xC))
        self.assertEqual(mov_l_literal(rom, 0x2C772), SPEED_BLOCK)  # r13
        self.assertEqual(u16(rom, 0x2C994), 0x1D9A)  # mov.l r9,@(0x28,r13)
        self.assertEqual(names_register(rom, 0x2C996, 0x2CA44, 9), [0x2CA3C])
        self.assertEqual(u16(rom, 0x2CA3C), 0xC9DF)
        self.assertEqual(mov_w_literal(rom, 0x2CA40), 0x2E0)
        self.assertEqual(u16(rom, 0x2CA44), 0x0C96)  # mov.l r9,@(r0,r12)
        # FUN_00099A48 stores r6 = -1 to both words.
        self.assertEqual(u16(rom, 0x99B8E), 0xE6FF)  # mov #-1,r6
        self.assertEqual(mov_l_literal(rom, 0x99B90), INTERVAL_BLOCK)  # r5
        self.assertTrue(stores_through(rom, 0x99B92, 0x99BB6, 5))
        self.assertEqual(names_register(rom, 0x99B90, 0x99BB6, 6), [])
        self.assertEqual(u16(rom, 0x99BAC), 0xE060)  # mov #0x60,r0
        self.assertEqual(mov_l_literal(rom, 0x99BAE), SNAPSHOT)  # r2
        self.assertEqual(u16(rom, 0x99BB0), 0x0266)  # mov.l r6,@(r0,r2)
        self.assertEqual(mov_w_literal(rom, 0x99BB4), 0x2E0)
        self.assertEqual(u16(rom, 0x99BB6), 0x0566)  # mov.l r6,@(r0,r5)
        self.assertEqual(SNAPSHOT + 0x60, 0xFFFF11FC)
        # With ffff22d4 = ffff11fc = 6250000/RPM counts, ffff1208 counts
        # 0.32 per RPM, the representation of ffff11ee.
        self.assertEqual(
            Fraction(12_000_000, 3 * 6_250_000) / 2, 1 / rpm_per_count(4)
        )

    def test_requested_torque_row_axes_count_sixteen_speed_counts(self):
        rom = self.rom
        # The trustful wrapper and byte core share the code of the primary
        # ones. Each wrapper passes the row input to its byte core in r5
        # and reads the stacked column word from @(16,r15) after four pushes.
        self.assertEqual(rom[0x262E0:0x26314], rom[0x26660:0x26694])
        self.assertEqual(rom[0x26A0C:0x26A58], rom[0x26BC4:0x26C10])
        for wrapper, core in ((0x262E0, 0x26A0C), (0x26660, 0x26BC4)):
            with self.subTest(wrapper=hex(wrapper)):
                self.assertEqual(u16(rom, wrapper + 4), 0x677D)  # extu.w r7,r7
                self.assertEqual(u16(rom, wrapper + 6), 0x6053)  # mov r5,r0
                self.assertEqual(u16(rom, wrapper + 8), 0x6573)  # mov r7,r5
                self.assertEqual(mov_l_literal(rom, wrapper + 10), core)
                self.assertEqual(u16(rom, wrapper + 12), 0x470B)  # jsr @r7
                self.assertEqual(u16(rom, wrapper + 14), 0xE40F)  # mov #15,r4
                self.assertEqual(u16(rom, wrapper + 22), 0x55F4)
                self.assertEqual(u16(rom, wrapper + 24), 0x655D)  # extu.w r5,r5
        # Byte core 0x26A0C multiplies each point and both span points by 16.
        self.assertEqual(u16(rom, 0x26A0E), 0x014C)  # mov.b @(r0,r4),r1
        self.assertEqual(u16(rom, 0x26A10), 0x611C)  # extu.b r1,r1
        self.assertEqual(u16(rom, 0x26A12), 0x4108)  # shll2 r1
        self.assertEqual(u16(rom, 0x26A14), 0x4108)  # shll2 r1
        self.assertEqual(u16(rom, 0x26A16), 0x3150)  # cmp/eq r5,r1
        self.assertEqual(
            [u16(rom, address) for address in range(0x26A2A, 0x26A3A, 2)],
            [0x6130, 0x8431, 0x611C, 0x600C, 0x4008, 0x4108, 0x4008, 0x4108],
        )
        # FUN_000730FC passes ffff1702 to inverse lookup FUN_00073432.
        self.assertEqual(mov_l_literal(rom, 0x7310E), TORQUE_BLOCK)  # r11
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73110), PRIMARY_ROW)
        self.assertEqual(branch_target(rom, 0x73112), 0x73432)  # bsr
        self.assertEqual(u16(rom, 0x73114), 0x04BD)  # mov.w @(r0,r11),r4
        # FUN_00073432 compares the row input with the first and the last
        # point of 0x11D0C, each multiplied by 16.
        self.assertEqual(mov_l_literal(rom, 0x73446), 0x11D0C)  # r14
        self.assertEqual(u16(rom, 0x73448), 0x674D)  # extu.w r4,r7
        self.assertEqual(u16(rom, 0x7344E), 0x62E0)  # mov.b @r14,r2
        self.assertEqual(u16(rom, 0x73452), 0x662C)  # extu.b r2,r6
        self.assertEqual(u16(rom, 0x73454), 0x4608)  # shll2 r6
        self.assertEqual(u16(rom, 0x73458), 0x4608)  # shll2 r6
        self.assertEqual(u16(rom, 0x7345E), 0x3767)  # cmp/gt r6,r7
        self.assertEqual(u16(rom, 0x73468), 0x84EF)  # mov.b @(15,r14),r0
        self.assertEqual(u16(rom, 0x7346A), 0x620C)  # extu.b r0,r2
        self.assertEqual(u16(rom, 0x7346C), 0x4208)  # shll2 r2
        self.assertEqual(u16(rom, 0x7346E), 0x4208)  # shll2 r2
        self.assertEqual(u16(rom, 0x73470), 0x3723)  # cmp/ge r2,r7
        # FUN_00073628 reads ffff1cca and compares it the same way.
        self.assertEqual(mov_l_literal(rom, 0x7363C), 0x18716)  # r10
        self.assertEqual(mov_l_literal(rom, 0x7363E), TORQUE_BLOCK)  # r14
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73640), TRUSTFUL_ROW)
        self.assertEqual(u16(rom, 0x73642), 0x62A0)  # mov.b @r10,r2
        self.assertEqual(u16(rom, 0x73644), 0x0DED)  # mov.w @(r0,r14),r13
        self.assertEqual(u16(rom, 0x73646), 0x622C)  # extu.b r2,r2
        self.assertEqual(u16(rom, 0x73648), 0x4208)  # shll2 r2
        self.assertEqual(u16(rom, 0x7364A), 0x6DDD)  # extu.w r13,r13
        self.assertEqual(u16(rom, 0x7364C), 0x4208)  # shll2 r2
        self.assertEqual(u16(rom, 0x7364E), 0x3D23)  # cmp/ge r2,r13
        # One stored count is 16 counts of 3.125 RPM.
        self.assertEqual(16 * rpm_per_count(4), 50)
        self.assertEqual(rom[0x18716:0x18726], rom[0x11D0C:0x11D1C])
        self.assertEqual(
            [point * 50 for point in rom[0x11D0C:0x11D1C]],
            [*range(800, 6401, 400), 7200],
        )

    def test_every_requested_torque_lookup_takes_its_row_coordinate(self):
        rom = self.rom
        for family, row, lookups, direct in (
            (PRIMARY, PRIMARY_ROW, PRIMARY_LOOKUPS, (LIMITER_LOOKUP,)),
            (TRUSTFUL, TRUSTFUL_ROW, TRUSTFUL_LOOKUPS, ()),
        ):
            surface = family[0]
            self.assertEqual(
                pc_literal_loads(rom, surface),
                sorted(
                    [lookup[0] for lookup in lookups]
                    + list(direct)
                    + list(INVERSE_LOADS[surface])
                ),
            )
            for load, base_load, base, row_load, extend, call in lookups:
                with self.subTest(surface=hex(surface), load=hex(load)):
                    self.assertEqual(mov_l_literal(rom, base_load), TORQUE_BLOCK)
                    self.assertEqual((u16(rom, base_load) >> 8) & 0xF, base)
                    # Registers r8..r14 survive calls; between the base load
                    # and the row load the base register only addresses
                    # stores.
                    self.assertTrue(
                        stores_through(rom, base_load + 2, row_load, base)
                    )
                    self.assertEqual(u16(rom, row_load - 4) >> 8, 0x90)
                    self.assertEqual(
                        TORQUE_BLOCK + mov_w_literal(rom, row_load - 4), row
                    )
                    self.assertIn(u16(rom, row_load - 2) >> 8, (0xD4, 0xD5))
                    # mov.w @(r0,base),r14, then extu.w r14,r7.
                    self.assertEqual(u16(rom, row_load), 0x0E0D | base << 4)
                    self.assertEqual(
                        names_register(rom, row_load + 2, extend, 14), []
                    )
                    self.assertEqual(u16(rom, extend), 0x67ED)
                    self.assertEqual(names_register(rom, extend + 2, call, 7), [])
                    self.assertEqual(u16(rom, call), 0x420B)  # jsr @r2
                    # r4, r5, r6, and r2 are each loaded once before the call.
                    start = min(load, row_load - 4)
                    for register, value in zip((4, 5, 6, 2), family):
                        named = names_register(rom, start, call, register)
                        self.assertEqual(len(named), 1)
                        self.assertEqual(mov_l_literal(rom, named[0]), value)
        # FUN_0007584E passes snapshot ffff11b6 through r7.
        self.assertEqual(mov_l_literal(rom, 0x75A08), SNAPSHOT)  # r3
        self.assertEqual(u16(rom, 0x75A0E), 0x853D)  # mov.w @(0x1a,r3),r0
        for load, value in zip((0x75A10, 0x75A12, 0x75A16, 0x75A18), PRIMARY):
            self.assertEqual(mov_l_literal(rom, load), value)
        self.assertEqual(u16(rom, 0x75A14), 0x670D)  # extu.w r0,r7
        self.assertEqual(u16(rom, 0x75A1A), 0x420B)  # jsr @r2
        # Fixed columns: mov #imm,r0, then mov.w r0,@(2,r15).
        for constant, store, immediate in FIXED_COLUMNS:
            with self.subTest(column=hex(store)):
                self.assertEqual(u16(rom, constant), 0xE000 | immediate)
                self.assertEqual(names_register(rom, constant + 2, store, 0), [])
                self.assertEqual(u16(rom, store), 0x81F1)

    def test_primary_conversion_divides_the_opening_area_by_engine_speed(self):
        rom = self.rom
        # FUN_00073948: GBR = ffff128c and r14 = 0xFFFF.
        self.assertEqual(mov_l_literal(rom, 0x73950), TORQUE_BLOCK)
        self.assertEqual(u16(rom, 0x73952), 0x401E)  # ldc r0,gbr
        self.assertEqual(u16(rom, 0x73956), 0xC553)  # mov.w @(0xa6,gbr),r0
        self.assertEqual(TORQUE_BLOCK + 0xA6, 0xFFFF1332)
        self.assertEqual(u16(rom, 0x73958), 0xEEFF)  # mov #-1,r14
        self.assertEqual(u16(rom, 0x7395A), 0x6EED)  # extu.w r14,r14
        # area = lookup of 0x13202 over 0x155A0 at min(0xFFFF, 4 * ffff1332).
        self.assertEqual(
            [u16(rom, address) for address in range(0x7395C, 0x73966, 2)],
            [0x660D, 0x4608, 0x36E6, 0x8B00, 0x66E3],
        )  # extu.w r0,r6; shll2 r6; cmp/hi r14,r6; bf; mov r14,r6
        self.assertEqual(mov_l_literal(rom, 0x73966), 0x13202)  # r4
        self.assertEqual(mov_l_literal(rom, 0x73968), 0x155A0)  # r5
        self.assertEqual(mov_l_literal(rom, 0x7396A), 0x26524)  # r7
        self.assertEqual(u16(rom, 0x7396C), 0x470B)  # jsr @r7
        # ffff12a0 = min(0xFFFF, 2 * area).
        self.assertEqual(
            [u16(rom, address) for address in range(0x73970, 0x7397A, 2)],
            [0x660D, 0x4600, 0x36E6, 0x8B00, 0x66E3],
        )  # extu.w r0,r6; shll r6; cmp/hi r14,r6; bf; mov r14,r6
        self.assertEqual(u16(rom, 0x7397C), 0x6063)  # mov r6,r0
        self.assertEqual(u16(rom, 0x73986), 0xC10A)  # mov.w r0,@(0x14,gbr)
        self.assertEqual(TORQUE_BLOCK + 0x14, 0xFFFF12A0)
        # ffff1824 = 4 * (ffff12a0 << 16) / ROM8[0x8D8F] / ffff1702.
        self.assertEqual(mov_l_literal(rom, 0x7397A), 0x8D8F)  # r5
        self.assertEqual(u16(rom, 0x7397E), 0x616D)  # extu.w r6,r1
        self.assertEqual(mov_l_literal(rom, 0x73980), 0x21CE0)  # r6
        self.assertEqual(u16(rom, 0x73982), 0x6250)  # mov.b @r5,r2
        self.assertEqual(u16(rom, 0x73984), 0x4128)  # shll16 r1
        self.assertEqual(u16(rom, 0x73988), 0x652C)  # extu.b r2,r5
        self.assertEqual(mov_l_literal(rom, 0x7398A), TORQUE_BLOCK)  # r13
        self.assertEqual(u16(rom, 0x7398C), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x7398E), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x73990), 0x6103)  # mov r0,r1
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73992), PRIMARY_ROW)
        self.assertEqual(mov_l_literal(rom, 0x73994), 0x21CE0)  # r6
        self.assertEqual(u16(rom, 0x73996), 0x4108)  # shll2 r1
        self.assertEqual(u16(rom, 0x73998), 0x02DD)  # mov.w @(r0,r13),r2
        self.assertEqual(u16(rom, 0x7399A), 0x652D)  # extu.w r2,r5
        self.assertEqual(u16(rom, 0x7399C), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x7399E), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x739A0), 0x6603)  # mov r0,r6
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x739A2), 0xFFFF1824)
        self.assertEqual(u16(rom, 0x739A6), 0x0D66)  # mov.l r6,@(r0,r13)
        # Up to ROM16[0x1553E] the coordinate indexes 0x15690 over 0x15500,
        # above it 0x156D0 over 0x15540 at min(0xFFFF, ffff1824 >> 4).
        self.assertEqual(mov_l_literal(rom, 0x739A4), 0x15500)  # r5
        self.assertEqual(u16(rom, 0x739A8), 0xE03E)  # mov #0x3e,r0
        self.assertEqual(u16(rom, 0x739AA), 0x025D)  # mov.w @(r0,r5),r2
        self.assertEqual(u16(rom, 0x739AE), 0x3626)  # cmp/hi r2,r6
        self.assertEqual(conditional_target(rom, 0x739B0), 0x739B8)
        self.assertEqual(mov_l_literal(rom, 0x739B2), 0x15690)  # r4
        self.assertEqual(branch_target(rom, 0x739B4), 0x739C6)
        self.assertEqual(
            [u16(rom, address) for address in range(0x739B8, 0x739C2, 2)],
            [0x4609, 0x4609, 0x36E6, 0x8B00, 0x66E3],
        )  # shlr2 r6; shlr2 r6; cmp/hi r14,r6; bf; mov r14,r6
        self.assertEqual(mov_l_literal(rom, 0x739C2), 0x156D0)  # r4
        self.assertEqual(mov_l_literal(rom, 0x739C4), 0x15540)  # r5
        self.assertEqual(mov_l_literal(rom, 0x739C6), 0x26524)  # r7
        self.assertEqual(u16(rom, 0x739C8), 0x470B)  # jsr @r7
        # ffff1980 = the segment value, which is also the stacked column.
        self.assertEqual(u16(rom, 0x739CC), 0x6203)  # mov r0,r2
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x739CE), 0xFFFF1980)
        self.assertEqual(u16(rom, 0x739D2), 0x0D25)  # mov.w r2,@(r0,r13)
        self.assertEqual(u16(rom, 0x739D4), 0x6023)  # mov r2,r0
        self.assertEqual(u16(rom, 0x739D6), 0x81F1)  # mov.w r0,@(2,r15)
        # ffff19ba = the surface value + 0x8000.
        self.assertEqual(u16(rom, 0x739E6), 0x620D)  # extu.w r0,r2
        self.assertEqual(mov_l_literal(rom, 0x739E8), 0x8000)  # r5
        self.assertEqual(u16(rom, 0x739EA), 0x622F)  # exts.w r2,r2
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x739EC), 0xFFFF19BA)
        self.assertEqual(u16(rom, 0x739EE), 0x325C)  # add r5,r2
        self.assertEqual(u16(rom, 0x739F0), 0x0D25)  # mov.w r2,@(r0,r13)
        self.assertEqual(rom[0x8D8F], 100)
        self.assertEqual(u16(rom, 0x1553E), 45187)
        self.assertEqual(0x15500 + 31 * 2, 0x1553E)
        # 4 * 65536 / 100 over RPM/3.125 counts is 8192 / RPM.
        self.assertEqual(Fraction(4 * 65536, 100) * rpm_per_count(4), 8192)

    def test_trustful_conversion_repeats_the_primary_chain_over_copies(self):
        rom = self.rom
        for primary, trustful, size in CONVERSION_COPIES:
            with self.subTest(primary=hex(primary)):
                self.assertEqual(
                    rom[primary : primary + size], rom[trustful : trustful + size]
                )
        self.assertEqual(u16(rom, 0x18EC4), u16(rom, 0x1553E))
        # The 1D wrappers 0x26524 and 0x26714 share their code.
        self.assertEqual(rom[0x26524:0x26548], rom[0x26714:0x26738])
        copies = {primary: trustful for primary, trustful, _size in CONVERSION_COPIES}
        copies[0x26524] = 0x26714
        copies[0x262E0] = 0x26660
        # FUN_00073A44 loads the copy wherever FUN_00073948 loads a primary
        # table, constant, or wrapper.
        for primary_site, trustful_site in (
            (0x73966, 0x73A62),
            (0x73968, 0x73A64),
            (0x7396A, 0x73A66),
            (0x7397A, 0x73A76),
            (0x739A4, 0x73AA0),
            (0x739B2, 0x73AAE),
            (0x739C2, 0x73ABE),
            (0x739C4, 0x73AC0),
            (0x739C6, 0x73AC2),
            (0x739D0, 0x73ACC),
            (0x739DA, 0x73AD6),
            (0x739DE, 0x73ADA),
            (0x739E0, 0x73ADC),
        ):
            with self.subTest(site=hex(trustful_site)):
                self.assertEqual(
                    copies[mov_l_literal(rom, primary_site)],
                    mov_l_literal(rom, trustful_site),
                )
                self.assertEqual(
                    u16(rom, primary_site) >> 8, u16(rom, trustful_site) >> 8
                )
        self.assertEqual(mov_l_literal(rom, 0x73A4C), TORQUE_BLOCK)  # gbr
        self.assertEqual(u16(rom, 0x73A52), 0xC553)  # mov.w @(0xa6,gbr),r0
        self.assertEqual(
            [u16(rom, address) for address in range(0x73A54, 0x73A62, 2)],
            [0xEEFF, 0x6EED, 0x660D, 0x4608, 0x36E6, 0x8B00, 0x66E3],
        )
        self.assertEqual(u16(rom, 0x73A68), 0x470B)  # jsr @r7
        self.assertEqual(
            [u16(rom, address) for address in range(0x73A6C, 0x73A76, 2)],
            [0x660D, 0x4600, 0x36E6, 0x8B00, 0x66E3],
        )
        # ffff1ca8 = min(0xFFFF, 2 * area), then the two divisions.
        self.assertEqual(u16(rom, 0x73A78), 0x616D)  # extu.w r6,r1
        self.assertEqual(mov_l_literal(rom, 0x73A7A), TORQUE_BLOCK)  # r13
        self.assertEqual(u16(rom, 0x73A7C), 0x4128)  # shll16 r1
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73A7E), 0xFFFF1CA8)
        self.assertEqual(u16(rom, 0x73A80), 0x6250)  # mov.b @r5,r2
        self.assertEqual(u16(rom, 0x73A82), 0x0D65)  # mov.w r6,@(r0,r13)
        self.assertEqual(mov_l_literal(rom, 0x73A84), 0x21CE0)  # r6
        self.assertEqual(u16(rom, 0x73A86), 0x652C)  # extu.b r2,r5
        self.assertEqual(u16(rom, 0x73A88), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x73A8A), 0x6053)  # mov r5,r0
        self.assertEqual(u16(rom, 0x73A8C), 0x6103)  # mov r0,r1
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73A8E), TRUSTFUL_ROW)
        self.assertEqual(mov_l_literal(rom, 0x73A90), 0x21CE0)  # r6
        self.assertEqual(u16(rom, 0x73A92), 0x4108)  # shll2 r1
        self.assertEqual(u16(rom, 0x73A94), 0x02DD)  # mov.w @(r0,r13),r2
        self.assertEqual(u16(rom, 0x73A96), 0x652D)  # extu.w r2,r5
        self.assertEqual(u16(rom, 0x73A98), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x73A9A), 0x6053)  # mov r5,r0
        # ffff1ce0 = the quotient, then the segment choice at the copy of
        # ROM16[0x1553E].
        self.assertEqual(u16(rom, 0x73A9C), 0x6603)  # mov r0,r6
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73A9E), 0xFFFF1CE0)
        self.assertEqual(u16(rom, 0x73AA2), 0x0D66)  # mov.l r6,@(r0,r13)
        self.assertEqual(u16(rom, 0x73AA4), 0xE03E)  # mov #0x3e,r0
        self.assertEqual(u16(rom, 0x73AA6), 0x025D)  # mov.w @(r0,r5),r2
        self.assertEqual(u16(rom, 0x73AAA), 0x3626)  # cmp/hi r2,r6
        self.assertEqual(conditional_target(rom, 0x73AAC), 0x73AB4)
        self.assertEqual(branch_target(rom, 0x73AB0), 0x73AC2)
        self.assertEqual(
            [u16(rom, address) for address in range(0x73AB4, 0x73ABE, 2)],
            [0x4609, 0x4609, 0x36E6, 0x8B00, 0x66E3],
        )
        self.assertEqual(u16(rom, 0x73AC4), 0x470B)  # jsr @r7
        # ffff1d0e = the segment value and the stacked column.
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73ACA), 0xFFFF1D0E)
        self.assertEqual(u16(rom, 0x73ACE), 0x0D25)  # mov.w r2,@(r0,r13)
        self.assertEqual(u16(rom, 0x73AD0), 0x6023)  # mov r2,r0
        self.assertEqual(u16(rom, 0x73AD2), 0x81F1)  # mov.w r0,@(2,r15)
        # ffff1d1a = the surface value - 0x8000, which equals the value
        # + 0x8000 in the 16-bit store.
        self.assertEqual(u16(rom, 0x73AE2), 0x620D)  # extu.w r0,r2
        self.assertEqual(TORQUE_BLOCK + mov_w_literal(rom, 0x73AE4), 0xFFFF1D1A)
        self.assertEqual(u16(rom, 0x73AE6), 0xE580)  # mov #-0x80,r5
        self.assertEqual(u16(rom, 0x73AE8), 0x622F)  # exts.w r2,r2
        self.assertEqual(u16(rom, 0x73AEA), 0x4518)  # shll8 r5
        self.assertEqual(u16(rom, 0x73AEC), 0x325C)  # add r5,r2
        self.assertEqual(u16(rom, 0x73AEE), 0x0D25)  # mov.w r2,@(r0,r13)
        self.assertEqual(-0x8000 % 0x10000, 0x8000)

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
        for axis, row in (("00011d0c", "ffff1702"), ("00018716", "ffff1cca")):
            with self.subTest(axis=axis):
                record = self.axes[axis]
                self.assertEqual(
                    (record["units"], record["scale_expr"], record["scale_conf"]),
                    ("RPM", "x*50", "code"),
                )
                self.assertIn(
                    f"indexed_by:{row}@confidence",
                    evidence(record, "scale_evidence"),
                )
                self.assertEqual(
                    logparam[row], {"id": "X_VQ_Engine_Speed", "units": "RPM"}
                )
        for axis, column in (("00014114", "ffff1980"), ("00018ac6", "ffff1d0e")):
            with self.subTest(axis=axis):
                record = self.axes[axis]
                self.assertEqual(record["scale_conf"], "candidate")
                self.assertIn(
                    f"indexed_by:{column}@structural",
                    evidence(record, "scale_evidence"),
                )
        for register in ("ffff1702", "ffff1cca", "ffff11d0", "ffff1208"):
            self.assertEqual(self.vars[register]["units"], "rpm/3.125")
        self.assertEqual(self.vars["ffff1206"]["units"], "rpm*0.64")
        # The streamed column coordinates repeat the candidate expressions of
        # the axes they index directly.
        for axis, column, parameter in (
            ("00011d4c", "ffff1170", "X_VQ_QH0_Flow_Quantity"),
            ("00014114", "ffff1980", "X_VQ_QH0_Flow_Potential"),
        ):
            with self.subTest(column=column):
                record = self.axes[axis]
                self.assertEqual(
                    logparam[column],
                    {
                        "id": parameter,
                        "units": record["units"],
                        "scale": record["scale_expr"],
                    },
                )
        # The trustful and inverse coordinates and the MAF-table inputs are
        # not streamed.
        for register in (
            "ffff1d0e",
            "ffff198a",
            "ffff1d14",
            "ffff1e48",
            "ffff1e4a",
        ):
            self.assertNotIn(register, logparam)

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
            "Both addends of `u` are opening areas in the value domain of "
            "`0x13202`, divided by engine speed.",
            "u ~= 3522 * (0xFFFF1E60 + 0xFFFF120E / 4) / RPM",
            "The column coordinate is therefore an alpha-N flow estimate: "
            "opening area over engine speed through a saturating curve.",
            "MAF range monitors `FUN_0008152A` (P0101) and `FUN_00081D74` "
            "(P010B) evaluate the same curve pair and read `0xFFFF120E`.",
        ):
            with self.subTest(statement=statement[:40]):
                self.assertIn(statement, self.fuel)
        for statement in (
            "FFFF1702 = max(32, FFFF11B6) FFFF1CCA = max(32, FFFF11D0)",
            "so `FFFF22D4` equals `FFFF11FC` and "
            "`FFFF1208 = floor(2000000 / FFFF11FC)`",
            "One stored row-axis count is therefore 50 RPM, and the row points "
            "decode to 800 through 6400 RPM in 400 RPM steps and 7200 RPM.",
            "Every forward lookup of `0xE98E` passes `FFFF1702` as the row "
            "input except throttle-rev limiter `0007584E`, which passes "
            "`FFFF11B6`; the two differ only below 100 RPM. Every lookup of "
            "`0x175C8` passes `FFFF1CCA`.",
            "FFFF1824 = floor(4 * floor(FFFF12A0 * 65536 / ROM8[0x8D8F]) "
            "/ FFFF1702)",
            "`FFFF1824 = 8192 * FFFF12A0 / RPM`: the column input is an "
            "opening area divided by engine speed.",
            "at column `0xFFFF`, the last column; `0007584E` reads `0xE98E` "
            "at column 0.",
            "`FFFF19B2 + (FFFF120E >> 2) = FFFF183E + FFFF1340`",
        ):
            with self.subTest(statement=statement[:40]):
                self.assertIn(statement, self.throttle)


class ThrottleOpeningScaleTest(unittest.TestCase):
    """Bind the percent scale of opening coordinate table 0x155A0 to the ROM."""

    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.axes = rows(AXES)
        cls.findings = rows(FINDINGS)
        cls.vars = rows(VARS)
        cls.funcs = rows(FUNCS)
        with OVERRIDES.open("rb") as source:
            cls.overrides = tomllib.load(source)
        cls.fuel = " ".join(FUEL.read_text(encoding="utf-8").split())
        cls.throttle = " ".join(THROTTLE.read_text(encoding="utf-8").split())

    def test_monitor_averages_both_channels_in_the_area_domain(self):
        rom = self.rom
        # FUN_0003E548: GBR = ffff277e.
        self.assertEqual(mov_l_literal(rom, 0x3E554), 0xFFFF277E)
        self.assertEqual(u16(rom, 0x3E556), 0x401E)  # ldc r0,gbr
        # r6 = min(0xFFFF, 4 * ffff284e) and r14 = min(0xFFFF, 4 * ffff2850).
        self.assertEqual(
            [u16(rom, address) for address in range(0x3E5BE, 0x3E5DA, 2)],
            [
                0xC568, 0xE2FF, 0x622D, 0x660D, 0xC569, 0x4608, 0x650D,
                0x3626, 0x8F01, 0x4508, 0x6623, 0x3526, 0x8900, 0x6253,
            ],
        )  # mov.w @(0xd0,gbr),r0 ... cmp/hi r2,r5; bt; mov r5,r2
        self.assertEqual(0xFFFF277E + 0xD0, 0xFFFF284E)
        self.assertEqual(0xFFFF277E + 0xD2, 0xFFFF2850)
        self.assertEqual(mov_l_literal(rom, 0x3E5DA), 0x13202)  # r11
        self.assertEqual(mov_l_literal(rom, 0x3E5DE), 0x155A0)  # r13
        self.assertEqual(mov_l_literal(rom, 0x3E5E2), 0x26524)  # r12
        # Both channels read the areas of 0x13202 over 0x155A0, and their
        # mean reads back through the reversed pair.
        self.assertEqual(
            [u16(rom, address) for address in range(0x3E5E4, 0x3E608, 2)],
            [
                0x64B3, 0x4C0B, 0x65D3, 0x66ED, 0x81F4, 0x64B3, 0x4C0B,
                0x65D3, 0x6203, 0x85F4, 0x622D, 0x64D3, 0x670D, 0x65B3,
                0x372C, 0x4701, 0x4C0B, 0x667D,
            ],
        )  # mov r11,r4; jsr @r12; mov r13,r5 ... add r2,r7; shlr r7; jsr @r12
        # ffff3f7c = the coordinate divided by four.
        self.assertEqual(u16(rom, 0x3E608), 0x620D)  # extu.w r0,r2
        self.assertEqual(mov_l_literal(rom, 0x3E60A), 0xFFFF39C4)  # r6
        self.assertEqual(0xFFFF39C4 + mov_w_literal(rom, 0x3E60C), 0xFFFF3F7C)
        self.assertEqual(u16(rom, 0x3E60E), 0x4209)  # shlr2 r2
        self.assertEqual(u16(rom, 0x3E610), 0x0625)  # mov.w r2,@(r0,r6)

    def test_absolute_throttle_scales_the_monitor_by_0x505b(self):
        rom = self.rom
        # FUN_0006F236: r2 = ffff4250 & 0x40.
        self.assertEqual(mov_l_literal(rom, 0x6F23C), 0xFFFF424C)  # r6
        self.assertEqual(u16(rom, 0x6F244), 0x8464)  # mov.b @(4,r6),r0
        self.assertEqual(u16(rom, 0x6F24E), 0xC940)  # and #0x40,r0
        self.assertEqual(u16(rom, 0x6F252), 0x6203)  # mov r0,r2
        # It takes the idle-base branch while bit 0 of ROM8[0x8B2C] is clear
        # and ffff4250 bit 6 is clear.
        self.assertEqual(mov_l_literal(rom, 0x6F280), 0x8B2C)  # r5
        self.assertEqual(u16(rom, 0x6F282), 0x6050)  # mov.b @r5,r0
        self.assertEqual(u16(rom, 0x6F284), 0xC801)  # tst #1,r0
        self.assertEqual(conditional_target(rom, 0x6F286), 0x6F2B6)  # bf
        self.assertEqual(rom[0x8B2C], 0x02)
        self.assertEqual(u16(rom, 0x6F288), 0x2228)  # tst r2,r2
        self.assertEqual(conditional_target(rom, 0x6F28A), 0x6F2CE)  # bf
        # r5 = max(0, ffff3f7c - ffff28f8).
        self.assertEqual(mov_l_literal(rom, 0x6F28C), 0xFFFF39C4)  # r6
        self.assertEqual(0xFFFF39C4 + mov_w_literal(rom, 0x6F28E), 0xFFFF3F7C)
        self.assertEqual(mov_l_literal(rom, 0x6F290), 0xFFFF28F8)  # r2
        self.assertEqual(
            [u16(rom, address) for address in range(0x6F292, 0x6F2A4, 2)],
            [0x056D, 0x6421, 0x655D, 0x644D, 0x3543, 0x8901, 0xA001, 0xE500, 0x3548],
        )  # mov.w @(r0,r6),r5; mov.w @r2,r4 ... cmp/ge r4,r5 ... sub r4,r5
        # r6 = r5 * 0x505b >> 16.
        self.assertEqual(mov_w_literal(rom, 0x6F2A4), 0x505B)  # r2
        self.assertEqual(u16(rom, 0x6F2A6), 0x0257)  # mul.l r5,r2
        self.assertEqual(u16(rom, 0x6F2A8), 0x061A)  # sts macl,r6
        self.assertEqual(branch_target(rom, 0x6F2AA), 0x6F2D4)
        self.assertEqual(u16(rom, 0x6F2AC), 0x4629)  # shlr16 r6
        # The branch without the idle base applies the same gradient.
        self.assertEqual(0xFFFF39C4 + mov_w_literal(rom, 0x6F2BC), 0xFFFF3F7C)
        self.assertEqual(mov_w_literal(rom, 0x6F2C0), 0x505B)  # r6
        self.assertEqual(u16(rom, 0x6F2C4), 0x0627)  # mul.l r2,r6
        # While ffff4250 bit 6 is set the byte is ROM8[0x864E].
        self.assertEqual(mov_l_literal(rom, 0x6F2CE), 0x864E)  # r2
        self.assertEqual(u16(rom, 0x6F2D0), 0x6620)  # mov.b @r2,r6
        self.assertEqual(rom[0x864E], 0x0C)
        # ffff1075 = min(255, r6).
        self.assertEqual(
            [u16(rom, address) for address in range(0x6F2D4, 0x6F2E0, 2)],
            [0xE2FF, 0x622C, 0x3626, 0x8900, 0x6263, 0x6023],
        )  # mov #-1,r2; extu.b r2,r2; cmp/hi r2,r6; bt; mov r6,r2; mov r2,r0
        self.assertEqual(mov_l_literal(rom, 0x6F2E0), 0xFFFF1072)  # r2
        self.assertEqual(u16(rom, 0x6F2E2), 0x8023)  # mov.b r0,@(3,r2)

    def test_pid_0x11_returns_the_absolute_throttle_byte(self):
        rom = self.rom
        # FUN_00035856 answers J1979 Mode 01 PID 0x11 with ffff1075.
        self.assertEqual(u16(rom, 0x35DDA), 0x8811)  # cmp/eq #0x11,r0
        self.assertEqual(conditional_target(rom, 0x35DDC), 0x35DEC)  # bf
        self.assertEqual(mov_l_literal(rom, 0x35DDE), 0xFFFF1072)  # r2
        self.assertEqual(u16(rom, 0x35DE2), 0x8423)  # mov.b @(3,r2),r0
        self.assertEqual(u16(rom, 0x35DE4), 0x460B)  # jsr @r6
        self.assertEqual(u16(rom, 0x35DE6), 0x6403)  # mov r0,r4

    def test_wide_open_monitor_applies_the_same_gradient(self):
        rom = self.rom
        # FUN_00054EB8: ffff3528 = min(255, ffff40c6 * 0x505b >> 16).
        self.assertEqual(mov_l_literal(rom, 0x54EBA), 0xFFFF40C6)  # r6
        self.assertEqual(u16(rom, 0x54EBC), 0x6261)  # mov.w @r6,r2
        self.assertEqual(mov_w_literal(rom, 0x54EBE), 0x505B)  # r6
        self.assertEqual(
            [u16(rom, address) for address in range(0x54EC0, 0x54ED6, 2)],
            [
                0x622D, 0x0627, 0x021A, 0x6629, 0xE2FF, 0x666F, 0x622C,
                0x3626, 0x8B00, 0x6623, 0x6263,
            ],
        )  # extu.w r2,r2; mul.l r2,r6 ... cmp/hi r2,r6; bf; mov r2,r6
        self.assertEqual(mov_l_literal(rom, 0x54ED6), 0xFFFF28F8)  # r6
        self.assertEqual(0xFFFF28F8 + mov_w_literal(rom, 0x54ED8), 0xFFFF3528)
        self.assertEqual(u16(rom, 0x54EDA), 0x0624)  # mov.b r2,@(r0,r6)

    def test_one_coordinate_count_is_the_published_gradient(self):
        # 0x505b / 65536 per quarter coordinate, 100 / 255 percent per byte.
        per_count = Fraction(0x505B, 65536) / 4 * Fraction(100, 255)
        self.assertEqual(per_count, Fraction(34285, 1114112))
        self.assertEqual(round(100 / per_count, 1), Fraction("3249.6"))
        self.assertEqual(round(3172 * per_count, 1), Fraction("97.6"))
        self.assertEqual(round(Fraction(200 * 100, 255), 1), Fraction("78.4"))
        stored = [u16(self.rom, 0x155A0 + 2 * index) for index in range(32)]
        self.assertEqual((stored[0], stored[-1]), (0, 3172))
        self.assertEqual(
            self.rom[0x155A0:0x155E0], self.rom[0x190D0:0x19110]
        )
        for table, conf in (("000155a0", "code"), ("000190d0", "candidate")):
            for ledger in (self.axes, self.findings):
                with self.subTest(table=table, ledger=ledger is self.axes):
                    record = ledger[table]
                    self.assertEqual(
                        (
                            record["units"],
                            record["scale_expr"],
                            record["to_byte"],
                            record["scale_conf"],
                        ),
                        (
                            "Throttle Valve Opening [%]",
                            "x*34285/1114112",
                            "x*1114112/34285",
                            conf,
                        ),
                    )
        tokens = evidence(self.axes["000155a0"], "scale_evidence")
        for token in (
            "indexed_by:ffff28bc@structural",
            "trace:0003e548@structural",
            "trace:0006f236@structural",
            "consumer:00035856@confidence",
            "rom_const:0006f2ae=0x505b",
            "rom_const:00054f2e=0x505b",
            "site:0003e610",
            "site:0006f2a4",
            "site:0006f2e2",
        ):
            self.assertIn(token, tokens)
        publisher = evidence(self.funcs["0006f236"])
        for token in (
            "consumer:ffff3f7c@structural",
            "base:ffff28f8@structural",
            "writes:ffff1075@structural",
            "rom_const:00008b2c=0x02",
            "rom_const:0006f2ae=0x505b",
            "rom_const:0006f306=0x505b",
            "rom_const:0000864e=0x0c",
        ):
            self.assertIn(token, publisher)
        self.assertEqual(self.vars["ffff1075"]["units"], "percent*255/100")
        self.assertIn("rom_const:0006f2ae=0x505b", evidence(self.vars["ffff3f7c"]))
        self.assertIn("rom_const:00054f2e=0x505b", evidence(self.vars["ffff3528"]))
        self.assertEqual(
            self.overrides["logparam"]["ffff28bc"],
            {"id": "X_VQ_Throttle_Target", "units": "Throttle Valve Opening [%]"},
        )

    def test_published_statements(self):
        for statement in (
            "`0006F236` writes `min(255, (FFFF3F7C - FFFF28F8) * 0x505B >> 16)` "
            "to `FFFF1075`, which `00035856` returns for J1979 Mode 01 PID 0x11 "
            "as `A * 100 / 255` percent.",
            "`0x505B / 65536 / 4 * 100 / 255 = 34285 / 1114112` percent of "
            "throttle opening: 100 percent is 3249.6 counts, and the stored "
            "axis points `0..3172` span `0..97.6` percent.",
            "No ECM diagnostic item publishes the coordinate in degrees, so the "
            "catalog `0.0275` degree scale remains a candidate.",
        ):
            with self.subTest(statement=statement[:40]):
                self.assertIn(statement, self.throttle)
        for statement in (
            "`FUN_0006F236` applies the same gradient, after subtracting idle "
            "base `0xFFFF28F8`, to the byte it publishes as J1979 PID 0x11 "
            "absolute throttle, so `0xFFFF3528` is throttle opening from "
            "coordinate zero at 100/255 percent per count, and the latch "
            "threshold 200 is 78.4 percent.",
        ):
            with self.subTest(statement=statement[:40]):
                self.assertIn(statement, self.fuel)


if __name__ == "__main__":
    unittest.main()
