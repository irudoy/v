import unittest

from kb import derive, repo, sh2


def image(code, pools=(), size=0x200):
    """An image with 16-bit words at their addresses and (address, bytes) pools."""
    data = bytearray(size)
    for address, word in code.items():
        data[address:address + 2] = word.to_bytes(2, "big")
    for address, raw in pools:
        data[address:address + len(raw)] = raw
    return bytes(data)


def pairs(code, pools=(), func=0x100):
    data = image(code, pools)
    return {pair.ins: pair for pair in derive.function_pairs(func, sorted(code), data)}


class DecodeTest(unittest.TestCase):
    def test_pc_relative_loads_align_long_pools(self):
        self.assertEqual(sh2.decode(0xD107, 0x102).value, ("pool", 0x120, 4))
        self.assertEqual(sh2.decode(0xD107, 0x100).value, ("pool", 0x120, 4))
        self.assertEqual(sh2.decode(0x920E, 0x104).value, ("pool", 0x124, 2))
        self.assertEqual(sh2.decode(0xC703, 0x102).value, ("mova", 0x110))

    def test_displacements_scale_with_the_access_width(self):
        self.assertEqual(sh2.decode(0x8413, 0).access, sh2.Access(1, 3, 1, "load"))
        self.assertEqual(sh2.decode(0x8513, 0).access, sh2.Access(1, 6, 2, "load"))
        self.assertEqual(sh2.decode(0x5213, 0).access, sh2.Access(1, 12, 4, "load"))
        self.assertEqual(sh2.decode(0x1213, 0).access, sh2.Access(2, 12, 4, "store"))
        self.assertEqual(sh2.decode(0xC105, 0).access, sh2.Access("gbr", 10, 2, "store"))
        self.assertEqual(sh2.decode(0xCD01, 0).access, sh2.Access("gbr", 0, 1, "update", True))
        self.assertEqual(sh2.decode(0x2216, 0).access, sh2.Access(2, -4, 4, "store"))

    def test_transfers_and_delay_slots(self):
        bsr = sh2.decode(0xBFFE, 0x100)
        self.assertEqual((bsr.flow, bsr.target, bsr.delayed), ("call", 0x100, True))
        bts = sh2.decode(0x8D02, 0x100)
        self.assertEqual((bts.flow, bts.target, bts.delayed), ("cbranch", 0x108, True))
        self.assertEqual(sh2.decode(0x8902, 0x100).delayed, False)
        self.assertEqual((sh2.decode(0x430B, 0).flow, sh2.decode(0x000B, 0).flow),
                         ("call", "return"))
        self.assertEqual(sh2.decode(0x411E, 0).gbr, ("copy", 1))
        self.assertIsNone(sh2.decode(0x412E, 0).gbr)

    def test_shifts_keep_their_register_and_width(self):
        self.assertEqual(sh2.decode(0x4018, 0).value, ("shl", 8))
        self.assertEqual(sh2.decode(0x4128, 0).value, ("shl", 16))
        self.assertEqual(sh2.decode(0x4220, 0).value, ("shl", 1))
        self.assertEqual(sh2.decode(0x4309, 0).value, ("shr", 2))
        self.assertEqual(sh2.decode(0x4421, 0).value, ("sar", 1))
        self.assertEqual(sh2.decode(0x4018, 0).dest, 0)
        # Rotations and dt set the register without a known value.
        self.assertIsNone(sh2.decode(0x4004, 0).value)
        self.assertIsNone(sh2.decode(0x4010, 0).value)


class LiteralPairTest(unittest.TestCase):
    POOL_L = (0x120, bytes.fromhex("ffff1234"))
    POOL_W = (0x124, bytes.fromhex("8010"))

    def test_long_and_sign_extended_word_literals_pair_with_accesses(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x8413,  # mov.b @(3,r1),r0
            0x104: 0x920E,  # mov.w @(0x124),r2
            0x106: 0x2201,  # mov.w r0,@r2
            0x108: 0x000B,  # rts
            0x10A: 0x0009,
        }, (self.POOL_L, self.POOL_W))
        self.assertEqual(sorted(found), [0x102, 0x106])
        first, second = found[0x102], found[0x106]
        self.assertEqual((first.address, first.literal, first.pool, first.base, first.mode,
                          first.size), (0xFFFF1237, 0xFFFF1234, 0x120, "r1", "load", 1))
        self.assertEqual((second.address, second.literal, second.base, second.mode),
                         (0xFFFF8010, 0xFFFF8010, "r2", "store"))

    def test_a_call_clobbers_caller_saved_registers_after_its_slot(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0xD806,  # mov.l @(0x120),r8
            0x104: 0x430B,  # jsr @r3
            0x106: 0x6110,  # slot: mov.b @r1,r1 (before the call)
            0x108: 0x6010,  # mov.b @r1,r0 (r1 lost)
            0x10A: 0x6080,  # mov.b @r8,r0 (r8 kept)
            0x10C: 0x000B,
            0x10E: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual(sorted(found), [0x106, 0x10A])
        self.assertEqual(found[0x10A].base, "r8")

    def test_paths_with_different_literals_leave_no_pair(self):
        code = {
            0x100: 0x8902,  # bt 0x108
            0x102: 0xD107,  # mov.l @(0x120),r1
            0x104: 0xA001,  # bra 0x10a
            0x106: 0x0009,
            0x108: 0xD106,  # mov.l @(0x124),r1
            0x10A: 0x6010,  # mov.b @r1,r0
            0x10C: 0x000B,
            0x10E: 0x0009,
        }
        self.assertEqual(pairs(code, (self.POOL_L, (0x124, bytes.fromhex("ffff2000")))), {})

    def test_paths_that_keep_the_literal_keep_the_pair(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x8901,  # bt 0x108
            0x104: 0x6313,  # mov r1,r3
            0x106: 0x0009,
            0x108: 0x6010,  # mov.b @r1,r0
            0x10A: 0x000B,
            0x10C: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual(sorted(found), [0x108])

    def test_immediates_copies_and_gbr_follow_the_literal(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x7104,  # add #4,r1
            0x104: 0x6213,  # mov r1,r2
            0x106: 0x411E,  # ldc r1,gbr
            0x108: 0xC402,  # mov.b @(2,gbr),r0
            0x10A: 0x6020,  # mov.b @r2,r0
            0x10C: 0x000B,
            0x10E: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual(found[0x108].address, 0xFFFF123A)
        self.assertEqual(found[0x108].base, "gbr")
        self.assertEqual(found[0x10A].address, 0xFFFF1238)
        self.assertEqual(found[0x10A].literal, 0xFFFF1234)

    def test_an_unknown_index_yields_the_table_base(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x021C,  # mov.b @(r0,r1),r2
            0x104: 0xE004,  # mov #4,r0
            0x106: 0x021C,
            0x108: 0x000B,
            0x10A: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual((found[0x102].address, found[0x102].indexed), (0xFFFF1234, True))
        self.assertEqual((found[0x106].address, found[0x106].indexed), (0xFFFF1238, False))

    def test_an_index_built_by_shifts_is_known(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x411E,  # ldc r1,gbr
            0x104: 0xE006,  # mov #6,r0
            0x106: 0x4018,  # shll8 r0
            0x108: 0x70B7,  # add #-73,r0
            0x10A: 0xCC01,  # tst.b #1,@(r0,gbr)
            0x10C: 0xE080,  # mov #-128,r0
            0x10E: 0x4021,  # shar r0
            0x110: 0x021C,  # mov.b @(r0,r1),r2
            0x112: 0x000B,  # rts
            0x114: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual((found[0x10A].address, found[0x10A].literal, found[0x10A].indexed),
                         (0xFFFF17EB, 0xFFFF1234, False))
        self.assertEqual((found[0x110].address, found[0x110].indexed), (0xFFFF11F4, False))

    def test_a_shifted_literal_is_no_base(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x4108,  # shll2 r1
            0x104: 0x6010,  # mov.b @r1,r0
            0x106: 0x000B,
            0x108: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual(found, {})

    def test_stc_gbr_takes_the_literal_of_gbr(self):
        found = pairs({
            0x100: 0xD107,  # mov.l @(0x120),r1
            0x102: 0x7104,  # add #4,r1
            0x104: 0x411E,  # ldc r1,gbr
            0x106: 0x0212,  # stc gbr,r2
            0x108: 0x430B,  # jsr @r3
            0x10A: 0x0009,
            0x10C: 0x0312,  # stc gbr,r3 (a call keeps GBR)
            0x10E: 0x4F17,  # ldc.l @r15+,gbr
            0x110: 0x0412,  # stc gbr,r4 (GBR unknown)
            0x112: 0x000B,
            0x114: 0x0009,
        }, (self.POOL_L,))
        self.assertEqual(sorted(found), [0x106, 0x10C])
        for site in (0x106, 0x10C):
            pair = found[site]
            self.assertEqual((pair.address, pair.literal, pair.pool, pair.base, pair.mode),
                             (0xFFFF1238, 0xFFFF1234, 0x120, "gbr", "literal"))


def references(layout, sites):
    """{(site, address, reference type)} of the L0 references at `sites`."""
    path = repo.ROOT / repo.L0 / layout / "function_references.csv"
    return {(int(row["ins_addr"], 16), int(row["ref_addr"], 16), row["ref_type"])
            for row in derive.read_rows(path) if int(row["ins_addr"], 16) in sites}


def pairs_at(layout, sites):
    return {pair.ins: pair for pair in derive.literal_pairs(layout) if pair.ins in sites}


class StockLayoutTest(unittest.TestCase):
    """Accesses of the VQ37VHR layouts whose addresses registers build from
    immediates, shifts, or GBR."""

    def test_peripheral_bases_built_from_immediates_reach_l0(self):
        # mov #-10,Rn; shll8 Rn; add #-128,Rn builds the base 0xFFFFF580 of
        # the word stores at displacements 0x12 and 0x10.
        for layout, stores in (
                ("1nd", {0x1109AC: 0xFFFFF592, 0x110A00: 0xFFFFF590, 0x110A26: 0xFFFFF590}),
                ("1me3b", {0x11C482: 0xFFFFF592, 0x11C4D6: 0xFFFFF590, 0x11C4FC: 0xFFFFF590})):
            with self.subTest(layout=layout):
                self.assertEqual(references(layout, set(stores)),
                                 {(site, address, "write") for site, address in stores.items()})

    def test_an_index_built_by_shifts_addresses_its_gbr_cell(self):
        # mov #6,r0; shll8 r0; add #-73,r0 indexes GBR 0xFFFE942C to 0xFFFE99E3
        # before each tst.b #imm,@(r0,gbr).
        sites = {0x119F68, 0x119F72, 0x119F8E}
        self.assertEqual(references("1me3b", sites),
                         {(site, 0xFFFE99E3, "read") for site in sites})
        found = {site: (pair.address, pair.literal, pair.base, pair.mode, pair.indexed)
                 for site, pair in pairs_at("1me3b", sites).items()}
        self.assertEqual(found, {site: (0xFFFE99E3, 0xFFFE942C, "gbr", "load", False)
                                 for site in sites})

    def test_stc_gbr_takes_the_source_of_the_scheduler_copies(self):
        # stc gbr,r2 passes the GBR block to the copy helper as its source.
        for layout, site, block, pool in (("1nd", 0x21738, 0xFFFE93CC, 0x21560),
                                          ("1me3b", 0x217A8, 0xFFFE939C, 0x21548)):
            with self.subTest(layout=layout):
                pair = pairs_at(layout, {site})[site]
                self.assertEqual((pair.address, pair.literal, pair.pool, pair.base, pair.mode),
                                 (block, block, pool, "gbr", "literal"))


if __name__ == "__main__":
    unittest.main()
