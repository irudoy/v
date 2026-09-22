import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
VARS = ROOT / "defs" / "JK08A.vars.csv"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
CVTC = ROOT / "defs" / "JK08A.cvtc.md"

LATCH = 0xFFFF5B2C
REGION_BOUNDS = 0x22624
REGION_START = 0xFFFF4514
REGION_STOP = 0xFFFF5CF2
STARTUP_TABLE = 0x225F4
SECTION_TABLE = 0x2260C

# Direct writers of the latch byte other than FUN_000BD20A: the byte store
# and the instruction that changes the loaded byte before it.
OTHER_WRITES = (
    (0x7C620, 0x7C61E, 0xC9F7),  # FUN_0007C57A: and #0xF7,r0
    (0x7D090, 0x7D08E, 0xC9F7),  # FUN_0007CF14
    (0x7D0E0, 0x7D0DE, 0xC9F7),
    (0x7D16E, 0x7D16A, 0xC9FB),  # and #0xFB,r0 or or #0x04,r0
    (0x7D16E, 0x7D16C, 0xCB04),
    (0x7D194, 0x7D190, 0xC9FD),  # and #0xFD,r0 or or #0x02,r0
    (0x7D194, 0x7D192, 0xCB02),
    (0x7DDA2, 0x7DDA0, 0xCB08),  # FUN_0007DC32: or #0x08,r0
    (0x804C2, 0x804C0, 0xC9F7),  # FUN_0008042C
    (0x82EF2, 0x82EF0, 0xC9F7),  # FUN_00082C8A
    (0x82F8C, 0x82F8A, 0xC9EF),
    (0x83F3A, 0x83F32, 0x220B),  # or r0,r2 with r0 = 0x10
    (0x84024, 0x84018, 0xC9EF),
    (0x84E80, 0x84E7E, 0xCB08),  # FUN_00084CD0
    (0x85016, 0x85014, 0xCB08),
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


def gbr_longword(data, base, address):
    """Return the longword a MOV.L @(disp,GBR),R0 at address loads from base."""
    opcode = u16(data, address)
    assert opcode >> 8 == 0xC6, hex(opcode)
    return u32(data, base + (opcode & 0xFF) * 4)


def written(start, stop):
    """Return the bytes a longword loop writes while the address lies below stop."""
    return range(start, start + max(0, (stop - start + 3) // 4) * 4)


def references(data, target):
    """Return the direct BRA/BSR branches and longword pointers to target."""
    found = []
    for address in range(0, len(data) - 1, 2):
        if u16(data, address) >> 12 in (0xA, 0xB):
            if branch_target(data, address) == target:
                kind = "bsr" if u16(data, address) >> 12 == 0xB else "bra"
                found.append((kind, address))
        if address + 4 <= len(data) and u32(data, address) == target:
            found.append(("pointer", address))
    return found


class CoolantLatchRetentionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        with VARS.open(newline="", encoding="utf-8") as source:
            cls.vars = {row["addr"]: row for row in csv.DictReader(source)}
        with FUNCS.open(newline="", encoding="utf-8") as source:
            cls.funcs = {row["addr"]: row for row in csv.DictReader(source)}
        cls.cvtc = " ".join(CVTC.read_text(encoding="utf-8").split())

    def test_zero_loop_covers_the_latch_byte(self):
        rom = self.rom
        # FUN_00026F30: r1 = 0x22624, r2 = @r1, store zero while r2 < @(4,r1).
        self.assertEqual(mov_l_literal(rom, 0x26F30), REGION_BOUNDS)
        self.assertEqual(u16(rom, 0x26F32), 0x6012)  # mov.l @r1,r0
        self.assertEqual(u16(rom, 0x26F34), 0x6203)  # mov r0,r2
        self.assertEqual(u16(rom, 0x26F36), 0x5011)  # mov.l @(4,r1),r0
        self.assertEqual(u16(rom, 0x26F38), 0x3202)  # cmp/hs r0,r2
        self.assertEqual(conditional_target(rom, 0x26F3A), 0x26F48)
        self.assertEqual(u16(rom, 0x26F3C), 0xE600)  # mov #0,r6
        self.assertEqual(u16(rom, 0x26F3E), 0x2262)  # mov.l r6,@r2
        self.assertEqual(u16(rom, 0x26F40), 0x7204)  # add #4,r2
        self.assertEqual(u16(rom, 0x26F42), 0x5011)
        self.assertEqual(u16(rom, 0x26F44), 0x3202)
        self.assertEqual(conditional_target(rom, 0x26F46), 0x26F3E)
        self.assertEqual(u16(rom, 0x26F48), 0x000B)  # rts
        self.assertEqual(u32(rom, REGION_BOUNDS), REGION_START)
        self.assertEqual(u32(rom, REGION_BOUNDS + 4), REGION_STOP)
        region = written(REGION_START, REGION_STOP)
        self.assertEqual((region.start, region.stop - 1), (0xFFFF4514, 0xFFFF5CF3))
        self.assertIn(LATCH, region)

    def test_reinitializer_is_the_only_caller_of_the_zero_loop(self):
        rom = self.rom
        self.assertEqual(references(rom, 0x26F30), [("bsr", 0x26F14)])
        # FUN_00026F08: GBR = 0xFFFF5CF6; clear the marker and check word,
        # zero the region, run the defaults, and write marker 0xAA55.
        self.assertEqual(mov_l_literal(rom, 0x26F0C), 0xFFFF5CF6)
        self.assertEqual(u16(rom, 0x26F0E), 0x401E)  # ldc r0,gbr
        self.assertEqual(u16(rom, 0x26F10), 0xE000)  # mov #0,r0
        self.assertEqual(u16(rom, 0x26F12), 0xC100)  # mov.w r0,@(0,gbr)
        self.assertEqual(branch_target(rom, 0x26F14), 0x26F30)
        self.assertEqual(u16(rom, 0x26F16), 0xC101)  # mov.w r0,@(2,gbr)
        self.assertEqual(branch_target(rom, 0x26F18), 0x26F4C)
        self.assertEqual(mov_l_literal(rom, 0x26F4E), 0x2C254)
        self.assertEqual(u16(rom, 0x26F50), 0x420B)  # jsr @r2
        self.assertEqual(mov_l_literal(rom, 0x26F54), 0x68794)
        self.assertEqual(u16(rom, 0x26F56), 0x422B)  # jmp @r2
        self.assertEqual(mov_w_literal(rom, 0x26F1C), 0xAA55)
        self.assertEqual(u16(rom, 0x26F20), 0xC100)
        self.assertEqual(mov_l_literal(rom, 0x26F1E), 0xFFFF5B2F)
        self.assertEqual(u16(rom, 0x26F24), 0xCB80)  # or #0x80,r0

    def test_reinitializer_callers(self):
        rom = self.rom
        self.assertEqual(
            references(rom, 0x26F08),
            [("bsr", 0x26E8A), ("pointer", 0x27D24), ("pointer", 0xCE844)],
        )
        # FUN_00026E1C: PLDR bit 4 gates the checks; the marker must be 0xAA55,
        # and check word 0x6997 selects the checksum.
        self.assertEqual(mov_l_literal(rom, 0x26E20), 0xFFFF5CF4)
        self.assertEqual(mov_w_literal(rom, 0x26E2C), 0xF756)
        self.assertEqual(u16(rom, 0x26E2E), 0x8564)  # mov.w @(8,r6),r0
        self.assertEqual(u16(rom, 0x26E32), 0xC810)  # tst #0x10,r0
        self.assertEqual(conditional_target(rom, 0x26E34), 0x26E8E)
        self.assertEqual(u16(rom, 0x26E36), 0xC501)  # mov.w @(2,gbr),r0
        self.assertEqual(mov_l_literal(rom, 0x26E38), 0xAA55)
        self.assertEqual(conditional_target(rom, 0x26E3E), 0x26E8A)
        self.assertEqual(mov_w_literal(rom, 0x26E42), 0x6997)
        self.assertEqual(branch_target(rom, 0x26E4A), 0x26DC4)
        # FUN_00027C50 calls it when range check FUN_00026EA0 returns zero.
        self.assertEqual(mov_l_literal(rom, 0x27CCC), 0x26EA0)
        self.assertEqual(u16(rom, 0x27CCE), 0x420B)
        self.assertEqual(u16(rom, 0x27CD2), 0x2008)  # tst r0,r0
        self.assertEqual(conditional_target(rom, 0x27CD4), 0x27CDC)
        self.assertEqual(mov_l_literal(rom, 0x27CD6), 0x26F08)
        self.assertEqual(u16(rom, 0x27CD8), 0x420B)
        # FUN_000CD85C calls it while 0xFFFF41B0 bit 4 is set.
        self.assertEqual(u16(rom, 0xCE7C6), 0x84CC)  # mov.b @(12,r12),r0
        self.assertEqual(u16(rom, 0xCE7C8), 0xC810)
        self.assertEqual(conditional_target(rom, 0xCE7CA), 0xCE800)
        self.assertEqual(mov_l_literal(rom, 0xCE7D6), 0x26F08)
        self.assertEqual(u16(rom, 0xCE7DA), 0x420B)

    def test_startup_initializers_leave_the_region(self):
        rom = self.rom
        # FUN_00027E24 waits for PLDR bit 4, then runs both initializers.
        self.assertEqual(u16(rom, 0x27E7E), 0x85E4)  # mov.w @(8,r14),r0
        self.assertEqual(u16(rom, 0x27E82), 0xC810)
        self.assertEqual(conditional_target(rom, 0x27E84), 0x27E7E)
        self.assertEqual(branch_target(rom, 0x27EBC), 0x27AC0)
        self.assertEqual(branch_target(rom, 0x27EC0), 0x27C50)
        # FUN_00027AC0 runs the region check first, then its loops.
        self.assertEqual(mov_l_literal(rom, 0x27AC4), STARTUP_TABLE)
        self.assertEqual(mov_l_literal(rom, 0x27AC8), 0x26E1C)
        self.assertEqual(u16(rom, 0x27ACA), 0x420B)
        spans = [
            (
                gbr_longword(rom, STARTUP_TABLE, 0x27ACE),
                gbr_longword(rom, STARTUP_TABLE, 0x27AD2),
            ),
            (
                gbr_longword(rom, STARTUP_TABLE, 0x27AE4),
                gbr_longword(rom, STARTUP_TABLE, 0x27AE8),
            ),
            (mov_l_literal(rom, 0x27AFA), mov_l_literal(rom, 0x27AFC)),
            (mov_l_literal(rom, 0x27B0C), mov_l_literal(rom, 0x27B0E)),
            (
                gbr_longword(rom, STARTUP_TABLE, 0x27B1E),
                gbr_longword(rom, STARTUP_TABLE, 0x27B22),
            ),
        ]
        self.assertEqual(branch_target(rom, 0x27B7C), 0x27C50)
        # FUN_00027C50: zero loops, then the initialized-data copy.
        self.assertEqual(mov_l_literal(rom, 0x27C54), SECTION_TABLE)
        for start, stop in ((0x27C58, 0x27C5C), (0x27C6E, 0x27C72),
                            (0x27C84, 0x27C88), (0x27C9A, 0x27C9E),
                            (0x27CB0, 0x27CB8)):
            spans.append((
                gbr_longword(rom, SECTION_TABLE, start),
                gbr_longword(rom, SECTION_TABLE, stop),
            ))
        self.assertEqual(gbr_longword(rom, SECTION_TABLE, 0x27CB4), 0x25590)
        self.assertEqual(
            spans,
            [
                (0xFFFF981C, 0xFFFF9F0A),
                (0xFFFF261C, 0xFFFF4512),
                (0xFFFFA314, 0xFFFFA572),
                (0xFFFFA574, 0xFFFFA6DD),
                (0xFFFF8000, 0xFFFF8499),
                (0xFFFF84A0, 0xFFFF981C),
                (0xFFFF1000, 0xFFFF261A),
                (0xFFFFA314, 0xFFFFA314),
                (0xFFFFA314, 0xFFFFA314),
                (0xFFFF9F0C, 0xFFFFA314),
            ],
        )
        region = written(REGION_START, REGION_STOP)
        below = [written(*span) for span in spans if span[0] < REGION_START]
        above = [written(*span) for span in spans if span[0] >= REGION_START]
        self.assertEqual(max(span.stop for span in below), REGION_START)
        self.assertEqual(min(span.start for span in above if span), 0xFFFF8000)
        self.assertGreaterEqual(min(span.start for span in above), region.stop)

    def test_only_the_coolant_producer_changes_bit_6(self):
        rom = self.rom
        # FUN_000BD20A sets bit 6 at 0xBD2C6 and clears it at 0xBD2D4.
        self.assertEqual(mov_l_literal(rom, 0xBD2C0), LATCH - 2)
        self.assertEqual(u16(rom, 0xBD2C2), 0x8452)  # mov.b @(2,r5),r0
        self.assertEqual(u16(rom, 0xBD2C4), 0xCB40)  # or #0x40,r0
        self.assertEqual(u16(rom, 0xBD2C6), 0x8052)  # mov.b r0,@(2,r5)
        self.assertEqual(mov_l_literal(rom, 0xBD2CE), LATCH - 2)
        self.assertEqual(u16(rom, 0xBD2D0), 0x8462)
        self.assertEqual(u16(rom, 0xBD2D2), 0xC9BF)  # and #0xBF,r0
        self.assertEqual(u16(rom, 0xBD2D4), 0x8062)
        for store, change, opcode in OTHER_WRITES:
            with self.subTest(store=hex(store)):
                # mov.b r0,@(2,Rn) after an operation that keeps bit 6.
                self.assertEqual(u16(rom, store) & 0xFF0F, 0x8002)
                self.assertEqual(u16(rom, change), opcode)
                if opcode >> 8 in (0xC9, 0xCB):
                    self.assertTrue(opcode >> 8 == 0xC9 and opcode & 0x40
                                    or opcode >> 8 == 0xCB and not opcode & 0x40)
        self.assertEqual(u16(rom, 0x83F30), 0xE010)  # mov #0x10,r0
        self.assertEqual(u16(rom, 0x83F38), 0x6023)  # mov r2,r0
        self.assertEqual(u16(rom, 0x84016), 0x6023)
        self.assertEqual(u16(rom, 0x8401A), 0x6203)  # mov r0,r2
        self.assertEqual(u16(rom, 0x84020), 0x6023)

    def test_published_statement(self):
        self.assertIn(
            "The latch byte lies in the retained RAM region "
            "`0xFFFF4514..0xFFFF5CF3`.",
            self.cvtc,
        )
        self.assertIn(
            "whose zero loops and initialized-data copy write only below "
            "`0xFFFF4514` and from `0xFFFF8000` upward.",
            self.cvtc,
        )
        self.assertIn(
            "it stores zero longwords from `ROM32[0x22624] = 0xFFFF4514` while "
            "the address lies below `ROM32[0x22628] = 0xFFFF5CF2`. Only "
            "`FUN 00026F08` calls it;",
            self.cvtc,
        )
        self.assertIn(
            "`FUN 000CD85C` calls it at `0xCE7DA` while `0xFFFF41B0` bit 4 is set.",
            self.cvtc,
        )
        self.assertIn(
            "Among the direct writers of the byte, only `FUN 000BD20A` changes "
            "bit 6.",
            self.cvtc,
        )
        self.assertIn(
            "a start between raw coolant 65 and 124 inherits the latch of "
            "earlier operation, and the clear-latch path needs a start below "
            "raw 65 or a zeroed region.",
            self.cvtc,
        )
        latch = self.vars["ffff5b2c"]
        self.assertIn(
            "The byte lies in retained RAM region ffff4514..ffff5cf3",
            latch["semantics"],
        )
        for token in ("writes:00026f30@structural", "writes:0002fc24@structural",
                      "writes:00034b70@structural", "writes:000bd20a@structural",
                      "rom_const:00022624=ffff4514",
                      "rom_const:00022628=ffff5cf2", "site:00026f3e",
                      "site:000bd2c6", "site:000bd2d4"):
            with self.subTest(token=token):
                self.assertIn(token, latch["evidence"].split(";"))
        self.assertIn(
            "zeroes ffff4514..ffff5cf3, including coolant latch byte ffff5b2c",
            self.funcs["00026f30"]["semantics"],
        )
        self.assertIn(
            "FUN 00026f08 is its only direct caller", self.funcs["00026f30"]["note"]
        )
        self.assertIn(
            "zeroes retained region ffff4514..ffff5cf3 through FUN 00026f30",
            self.funcs["00026f08"]["semantics"],
        )
        self.assertIn(
            "rejection calls reinitializer FUN 00026f08",
            self.funcs["00026e1c"]["semantics"],
        )
        self.assertIn(
            "It first runs retained-region check FUN 00026e1c.",
            self.funcs["00027ac0"]["semantics"],
        )


if __name__ == "__main__":
    unittest.main()
