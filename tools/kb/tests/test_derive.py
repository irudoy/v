import unittest

from kb import derive, sh2


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


if __name__ == "__main__":
    unittest.main()
