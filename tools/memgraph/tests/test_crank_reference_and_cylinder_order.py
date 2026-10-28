import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
OVERRIDES = ROOT / "defs" / "JK08A.overrides.toml"


def read_by(path, key):
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key]: row for row in csv.DictReader(source)}


def u32be(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


def normalize(tooth, count, remainder):
    """Reference model of FUN_00028DC8."""
    if tooth == 4:
        if 6 <= count <= 15:
            return count - 2, remainder
        if count == 5:
            return 3, remainder + 20
        if count == 4:
            return 3, remainder + 10
        return count, remainder
    if tooth == 9:
        if count == 9:
            return 8, remainder + 10
        if count >= 10:
            return count - 2, remainder + 20
        return count, remainder
    if 15 <= count <= 24:
        return count - 4, remainder
    if count == 14:
        return 10, remainder + 20
    if count == 13:
        return 10, remainder + 10
    if 3 <= count <= 12:
        return count - 2, remainder
    if count == 2:
        return 0, remainder + 20
    if count == 1:
        return 0, remainder + 10
    return count, remainder


# Tooth angles after tooth 7: two missing teeth follow tooth 7.
TOOTH_ANGLE = {7: 0, 8: 30, 9: 40, 0: 50, 1: 60, 2: 70, 3: 80, 4: 90, 5: 100, 6: 110}


def fire_angle(tooth, count, remainder):
    """Angle after the starting tooth at which a normalized command fires."""
    order = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]
    start = order.index(tooth)
    angle = 0
    position = start
    current = tooth
    for _ in range(count):
        position = (position + 1) % 10
        following = order[position]
        step = (TOOTH_ANGLE[following] - TOOTH_ANGLE[current]) % 120 or 120
        angle += step
        current = following
    return angle + remainder


class CrankReferenceAndCylinderOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by(FUNCS, "addr")
        cls.vars = read_by(VARS, "addr")
        with OVERRIDES.open("rb") as source:
            cls.overrides = tomllib.load(source)

    def test_ici0a_vector_enters_the_tooth_prologue(self):
        self.assertEqual(u32be(self.rom, 0x20154), 0x00028EA2)
        self.assertEqual(u32be(self.rom, 0x29020), 0xFFFF128C)
        # mov.w @(22,r11),r0; mov r0,r4; mov.w @(pc),r0; mov.w r4,@(r0,r8):
        # OSBR1 to window offset 0x2fe, 0xFFFF158A.
        self.assertEqual(self.rom[0x28F1C:0x28F24], bytes.fromhex("85bb640390750845"))
        self.assertEqual(self.rom[0x2900E:0x29010], bytes.fromhex("02fe"))
        driver = self.funcs["00028ea2"]
        self.assertIn("rom_const:00020154=00028ea2", driver["evidence"])
        self.assertIn("prologue 00028ea2", driver["semantics"])
        self.assertIn("writes:00028ea2@structural", self.vars["ffff158a"]["evidence"])

    def test_tooth_counter_and_gap_detection_constants(self):
        self.assertEqual(u32be(self.rom, 0x29224), 0x00008C81)
        self.assertEqual(u32be(self.rom, 0x29228), 0x00021BBC)
        self.assertEqual(u32be(self.rom, 0x2922C), 0x00008C89)
        self.assertEqual(u32be(self.rom, 0x29230), 0x00008C82)
        self.assertEqual(self.rom[0x8C81], 8)
        self.assertEqual(self.rom[0x8C82], 8)
        self.assertEqual(self.rom[0x8C89], 118)
        # Counter offset 0x126 and latch offset 0x128 of window 0xFFFF128C.
        self.assertEqual(self.rom[0x29016:0x29018], bytes.fromhex("0126"))
        self.assertEqual(0xFFFF128C + 0x126, 0xFFFF13B2)
        # mov #74,r0; shll2 r0: 0x128.
        self.assertEqual(self.rom[0x28FE8:0x28FEA], bytes.fromhex("e04a"))
        self.assertEqual(self.rom[0x28FEC:0x28FEE], bytes.fromhex("4008"))
        # cmp/eq #8,r0 and multiplier 0x5555: tooth 8 spans three pitches.
        self.assertEqual(self.rom[0x29126:0x29128], bytes.fromhex("8808"))
        self.assertEqual(self.rom[0x29154:0x29156], bytes.fromhex("5555"))
        # The gap ratio 64 * 3 exceeds the threshold and 64 / 3 does not.
        self.assertGreater(64 * 3, self.rom[0x8C89])
        self.assertLess(64 // 3, self.rom[0x8C89])
        counter = self.vars["ffff13b2"]
        self.assertEqual(counter["units"], "crank tooth 0..9")
        self.assertIn("writes:00028ea2@structural", counter["evidence"])
        self.assertEqual(self.vars["ffff196c"]["units"], "ratio*64")

    def test_normalizer_is_exact_for_two_missing_teeth_after_tooth_seven(self):
        for count in range(1, 25):
            with self.subTest(tooth=7, count=count):
                events, remainder = normalize(7, count, 0)
                self.assertEqual(fire_angle(7, events, remainder), 10 * count)
        for count in range(4, 16):
            with self.subTest(tooth=4, count=count):
                events, remainder = normalize(4, count, 0)
                self.assertEqual(fire_angle(4, events, remainder), 10 * count)
        for count in (9, 10):
            with self.subTest(tooth=9, count=count):
                events, remainder = normalize(9, count, 0)
                self.assertEqual(fire_angle(9, events, remainder), 10 * count)
        normalizer = self.funcs["00028dc8"]
        self.assertIn("two-missing-teeth gap", normalizer["semantics"])
        for caller in ("0002acba", "0002b64a", "00057380"):
            self.assertIn(f"trace:{caller}@structural", normalizer["evidence"])

    def test_reference_tooth_is_110_degrees_before_compression_tdc(self):
        self.assertEqual(self.rom[0x83D5], 110)
        self.assertEqual(u32be(self.rom, 0x2991C), 0x000221BC)
        self.assertEqual(u32be(self.rom, 0x29920), 0x000208F8)
        # Command 95 splits as nine 10-degree steps plus 5 degrees; the
        # scheduler passes count - 1 and remainder + 10 to the normalizer.
        events, remainder = normalize(7, 9 - 1, 5 + 10)
        self.assertEqual((events, remainder), (6, 15))
        self.assertEqual(fire_angle(7, events, remainder), 95)
        index = self.vars["ffff11de"]
        self.assertEqual(index["units"], "cylinder number 1..6")
        self.assertIn("110 degrees before compression TDC", index["semantics"])

    def test_cylinder_tables(self):
        expected = {
            0x2265C: "00040506010203",
            0x22664: "00020304050601",
            0x2266B: "00060102030405",
            0x22672: "00020304050601",
            0x22679: "00200102040810",
            0x22680: "00020304050601",
            0x22687: "00020408102001",
            0x226A2: "0018302103060c",
        }
        for address, data in expected.items():
            with self.subTest(table=hex(address)):
                self.assertEqual(self.rom[address : address + 7], bytes.fromhex(data))
        self.assertEqual(self.rom[0x22695:0x2269B], bytes.fromhex("020408102001"))
        self.assertEqual(u32be(self.rom, 0x2A0E0), 0x0002266B)
        self.assertEqual(u32be(self.rom, 0x2A0E8), 0x00022672)
        self.assertEqual(u32be(self.rom, 0x2A0F4), 0x00022679)
        self.assertEqual(u32be(self.rom, 0x2A3B4), 0x000226A2)
        self.assertEqual(u32be(self.rom, 0x2A3D4), 0x0002265C)
        self.assertEqual(u32be(self.rom, 0x29900), 0x00022695)

    def test_misfire_attribution_makes_the_event_index_the_cylinder_number(self):
        self.assertEqual(u32be(self.rom, 0x2A3CC), 0x00008BDC)
        self.assertEqual(u32be(self.rom, 0x2A3DC), 0x00008BDD)
        self.assertEqual(self.rom[0x8BDC], 9)
        self.assertEqual(self.rom[0x8BDD], 9)
        self.assertEqual(u32be(self.rom, 0x85D0C), 0xFFFF1DAC)
        table = self.rom[0x2265C:0x2265C + 7]
        for index in range(1, 7):
            with self.subTest(index=index):
                # Tooth 9 of event c is 70 degrees before compression TDC of c;
                # the tested interval T[n-1] ends 120 degrees earlier and spans
                # 50..170 degrees after compression TDC of index c - 3.
                end = -70 - 120
                start = end - 120
                tdc = -360
                self.assertEqual((start - tdc, end - tdc), (50, 170))
                self.assertEqual(table[index], (index - 3 - 1) % 6 + 1)
        # and.b #0xe0 / and.b #0x3f clear, or.b #0x10 sets the first flag.
        self.assertEqual(self.rom[0x84AB0:0x84AB2], bytes.fromhex("cde0"))
        self.assertEqual(self.rom[0x84AB4:0x84AB6], bytes.fromhex("cd3f"))
        self.assertEqual(self.rom[0x84AC4:0x84AC6], bytes.fromhex("cf10"))
        self.assertEqual(self.rom[0x84B08:0x84B0A], bytes.fromhex("cf80"))
        self.assertEqual(self.rom[0x84B14:0x84B16], bytes.fromhex("cf40"))
        self.assertEqual(self.rom[0x8862], 6)
        self.assertEqual(self.rom[0x8863], 6)
        # Counter bases one word above totals 0xFFFF37F8 and 0xFFFF3806.
        self.assertEqual(u32be(self.rom, 0x83F68), 0xFFFF36D8)
        self.assertEqual(self.rom[0x83E7E:0x83E80], bytes.fromhex("0122"))
        self.assertEqual(0xFFFF36D8 + 0x122, 0xFFFF37FA)
        self.assertEqual(0xFFFF36D8 + (0x4C << 2), 0xFFFF3808)
        builder = self.funcs["00084aa4"]
        self.assertEqual(builder["role"], "monitor")
        attribution = self.vars["ffff4038"]
        self.assertEqual(attribution["units"], "cylinder number 1..6")
        self.assertIn("rom_const:0002265c=[0,4,5,6,1,2,3]", attribution["evidence"])

    def test_start_phase_constants_and_grouped_pulse(self):
        self.assertEqual(self.rom[0x8D5F], 0)
        self.assertEqual(self.rom[0x8D60], 92)
        table = self.rom[0x226A2:0x226A2 + 7]
        for index in range(1, 7):
            with self.subTest(index=index):
                bits = {(index + 2) % 6, (index + 3) % 6}
                self.assertEqual(table[index], sum(1 << bit for bit in bits))
        # Tooth 4 is 20 degrees before compression TDC of cylinder j, which is
        # intake TDC of cylinder j + 3; cylinder j + 4 follows 120 degrees later.
        self.assertEqual(110 - 90, 20)
        self.assertEqual(110 - 90 + 120, 140)
        # Start-phase pulse on tooth 9 with lead 3: cylinder n - 2.
        self.assertEqual(-(40 - 110) + 120, 190)
        self.assertEqual(190 - 92, 98)

    def test_dwell_channel_tables_and_spark_edge(self):
        self.assertEqual(u32be(self.rom, 0x2AD9C), 0x00022680)
        self.assertEqual(u32be(self.rom, 0x2B094), 0x00022687)
        self.assertIn("rom_const:00022687=[0,2,4,8,16,32,1]", self.funcs["0002af38"]["evidence"])

    def test_injection_tables_are_published_with_the_intake_tdc_coordinate(self):
        for address, name in (
            ("00012302", "End of Injection Angle - Base"),
            ("0001230a", "End of Injection Angle - Conditional"),
        ):
            with self.subTest(table=address):
                entry = self.overrides["table"][address]
                self.assertEqual(entry["name"], name)
                self.assertEqual(entry["category"], "Fuelling / Injection")
                self.assertTrue(entry.get("emit", True))
                self.assertEqual(
                    entry["static_axis"], [800 * cell for cell in range(8)]
                )
        self.assertEqual(self.rom[0x8770], 120)


IMAGES = ROOT / "rom-images"

# Homologs of the JK08A end-of-injection reference chain. "block" is the offset
# of the JK08A sequencing constant block 0x22658..0x226A9 in the target image.
# 1ME3B holds the block without the ROM misfire attribution map and its pad
# byte: "block_head" places JK08A 0x22658..0x2265B, "block" places
# 0x22664..0x226A9, and "ram_map" is the map its tooth handler builds in RAM.
HOMOLOGS = {
    "JK08A": {
        "image": ROM,
        "block": 0x0,
        "reference": 0x83D5,
        "reference_literal": 0x83D5,
        "table": 0x21B5C,
        "feeder": 0x208F8,
        "sequencer": 0x54A44,
        "ignition_task": 0x4E162,
        "scheduler": 0x2A892,
        "reader": 0x521A8,
        "dispatch": (0x2965A, 0x29662, 0x2966A, 0x29672, 0x2967A),
    },
    "JK00C": {
        "image": IMAGES / "23710-JK00C" / "1JK00C-20260803-stock.bin",
        "block": 0x8C,
        "reference": 0x83D8,
        "reference_literal": 0x83D8,
        "table": 0x21BE8,
        "feeder": 0x20926,
        "sequencer": 0x56978,
        "ignition_task": 0x4FAB2,
        "scheduler": 0x2B51A,
        "reader": 0x53BF8,
        "dispatch": (0x2A2E2, 0x2A2EA, 0x2A2F2, 0x2A2FA, 0x2A302),
    },
    "JK00D": {
        "image": IMAGES / "23710-JK00D" / "1JK00D-20260726-stock.bin",
        "block": 0x8C,
        "reference": 0x83D8,
        "reference_literal": 0x83D8,
        "table": 0x21BE8,
        "feeder": 0x20926,
        "sequencer": 0x56974,
        "ignition_task": 0x4FAAE,
        "scheduler": 0x2B51A,
        "reader": 0x53BF4,
        "dispatch": (0x2A2E2, 0x2A2EA, 0x2A2F2, 0x2A2FA, 0x2A302),
    },
    "JK78C": {
        "image": IMAGES / "23710-JK78C" / "1JK78C-20260715-stock.bin",
        "block": 0x68,
        "reference": 0x838F,
        "reference_literal": 0x838F,
        "table": 0x21C8C,
        "feeder": 0x2095C,
        "sequencer": 0x70EDC,
        "ignition_task": 0x69A80,
        "scheduler": 0x2D6F6,
        "reader": 0x6E12C,
        "dispatch": (0x2C0DE, 0x2C0E6, 0x2C0EE, 0x2C0F6, 0x2C0FE),
    },
    "1ND0A": {
        "image": IMAGES / "23710-1ND0A" / "11ND0A-20260715-stock.bin",
        "block": 0x3C0,
        "reference": 0x83AB,
        "reference_literal": 0x83AA,
        "table": 0x222A8,
        "feeder": 0x20CF4,
        "sequencer": 0x7D3E8,
        "ignition_task": 0x74AFA,
        "scheduler": 0x2E464,
        "reader": 0x79D2E,
        "dispatch": (0x2D082, 0x2D086, 0x2D08E, 0x2D096, 0x2D09E),
    },
}
HOMOLOGS["1ND3B"] = dict(
    HOMOLOGS["1ND0A"],
    image=IMAGES / "23710-1ND3B" / "11ND3B-20260715-stock.bin",
)
HOMOLOGS["1ME3B"] = {
    "image": IMAGES / "23710-1ME3B" / "11ME3B-20260825-stock.bin",
    "block": 0x434,
    "block_head": 0x43C,
    "ram_map": 0xFFFEEA58,
    "tooth_handler": 0x2F730,
    "reference": 0x83B2,
    "reference_literal": 0x83B0,
    "table": 0x22324,
    "feeder": 0x20D04,
    "sequencer": 0x81EEC,
    "ignition_task": 0x78F14,
    "scheduler": 0x311B2,
    "reader": 0x7E736,
    "dispatch": (0x2FEC2, 0x2FEC6, 0x2FECE, 0x2FED6, 0x2FEDE),
}


def literal_sites(data, value):
    needle = value.to_bytes(4, "big")
    return [
        offset
        for offset in range(0, len(data) - 3, 4)
        if data[offset : offset + 4] == needle
    ]


class HomologousInjectionReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = {
            name: facts["image"].read_bytes() for name, facts in HOMOLOGS.items()
        }

    def test_sequencing_constant_block_is_byte_identical(self):
        reference = self.images["JK08A"][0x22658:0x226AA]
        self.assertEqual(reference[0x4:0xB].hex(), "00040506010203")
        self.assertEqual(reference[0x3D:0x43].hex(), "020408102001")
        for name, facts in HOMOLOGS.items():
            with self.subTest(rom=name):
                data = self.images[name]
                if "ram_map" in facts:
                    head = 0x22658 + facts["block_head"]
                    tail = 0x22664 + facts["block"]
                    self.assertEqual(data[head : head + 4], reference[:4])
                    self.assertEqual(head + 4, tail)
                    self.assertEqual(
                        data[tail : tail + len(reference) - 0xC], reference[0xC:]
                    )
                    self.assertEqual(data.find(reference[0x4:0xB]), -1)
                    continue
                start = 0x22658 + facts["block"]
                self.assertEqual(data[start : start + len(reference)], reference)

    def test_1me3b_builds_the_misfire_attribution_map_in_ram(self):
        data = self.images["1ME3B"]
        facts = HOMOLOGS["1ME3B"]
        handler = facts["tooth_handler"]
        sites = literal_sites(data, facts["ram_map"])
        self.assertEqual(len(sites), 2)
        for site in sites:
            self.assertTrue(handler < site < handler + 0x1500)
        # tst #1 on 0xFFFEBA4D, then the two immediate sequences stored to
        # offsets 1..6 of the map; offset 0 receives zero in the delay slot.
        self.assertEqual(
            data[0x2F78C:0x2F7C2].hex(),
            "c8018f0c2520"
            "e0058051e0068052e0018053e0028054e0038055a00be004"
            "e0048051e0058052e0068053e0018054e0028055e0038056",
        )
        self.assertEqual(u32be(data, 0x2F84C) + 2, 0xFFFEBA4D)
        # Interval end tooth and start tooth of the misfire capture.
        self.assertEqual((data[0x8AEE], data[0x8AF0]), (9, 9))
        self.assertEqual(u32be(data, 0x3595C), 0x8AEB)
        self.assertEqual(
            data[0x3581A:0x35830].hex(),
            "84e5620c84e3660c32638d0ee5073253890136538904",
        )
        # Reset entry 0x2E23A: bsr 0x2DF4E, whose tail jumps to 0x34340, comes
        # before the main loop first lowers the interrupt mask at 0x2E444.
        self.assertEqual(u32be(data, 0x0), 0x2614)
        self.assertEqual(data[0x2E40A:0x2E40C].hex(), "bda0")
        self.assertEqual(data[0x2DF6A:0x2DF70].hex(), "d24a422b4f26")
        self.assertEqual(u32be(data, 0x2E094), 0x34340)
        self.assertEqual(data[0x2E43A:0x2E446].hex(), "0502e6ff4618760f2569450e")

    def test_tooth_seven_reference_and_ignition_constant(self):
        for name, facts in HOMOLOGS.items():
            with self.subTest(rom=name):
                data = self.images[name]
                self.assertEqual(data[facts["reference"]], 110)
                words = [
                    int.from_bytes(data[site : site + 2], "big")
                    for site in facts["dispatch"]
                ]
                self.assertEqual(words, [0x8804, 0x8806, 0x8807, 0x8808, 0x8809])
                task = facts["ignition_task"]
                window = range(task - 0x300, task + 0x300)
                for literal in (facts["reference_literal"], facts["scheduler"]):
                    self.assertTrue(
                        any(site in window for site in literal_sites(data, literal)),
                        f"{literal:#x}",
                    )

    def test_engine_event_tasks_and_single_literal_bindings(self):
        for name, facts in HOMOLOGS.items():
            with self.subTest(rom=name):
                data = self.images[name]
                table = facts["table"]
                self.assertEqual(u32be(data, table + 4), facts["sequencer"])
                self.assertEqual(u32be(data, table + 16), facts["ignition_task"])
                feeder = facts["feeder"]
                self.assertTrue(
                    any(
                        feeder < site < feeder + 0x300
                        for site in literal_sites(data, table)
                    )
                )
                sequencer = facts["sequencer"]
                base_sites = literal_sites(data, 0x2268E + facts["block"])
                self.assertEqual(len(base_sites), 1)
                self.assertTrue(sequencer < base_sites[0] < sequencer + 0x400)
                if "ram_map" not in facts:
                    self.assertEqual(
                        len(literal_sites(data, 0x2265C + facts["block"])), 1
                    )
                reader = facts["reader"]
                self.assertTrue(
                    any(
                        reader < site < reader + 0x300
                        for site in literal_sites(data, 0xC49B)
                    )
                )


if __name__ == "__main__":
    unittest.main()
