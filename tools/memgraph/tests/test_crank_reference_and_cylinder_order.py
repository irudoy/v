import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
OVERRIDES = ROOT / "defs" / "JK08A.overrides.toml"
FUEL = ROOT / "defs" / "JK08A.fuel.md"
IGNITION = ROOT / "defs" / "JK08A.ignition-output.md"


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
        cls.fuel = " ".join(FUEL.read_text(encoding="utf-8").split())
        cls.ignition = " ".join(IGNITION.read_text(encoding="utf-8").split())
        with OVERRIDES.open("rb") as source:
            cls.overrides = tomllib.load(source)

    def test_ici0a_vector_enters_the_tooth_prologue(self):
        self.assertEqual(u32be(self.rom, 0x20154), 0x00028EA2)
        self.assertEqual(u32be(self.rom, 0x29020), 0xFFFF128C)
        # mov.w @(22,r11),r0; mov r0,r4; mov.w @(pc),r0; mov.w r4,@(r0,r8):
        # OSBR1 to window offset 0x2fe, 0xFFFF158A.
        self.assertEqual(self.rom[0x28F1C:0x28F24], bytes.fromhex("85bb640390750845"))
        self.assertEqual(self.rom[0x2900E:0x29010], bytes.fromhex("02fe"))
        driver = self.funcs["00029588"]
        self.assertIn("rom_const:00020154=00028ea2", driver["evidence"])
        self.assertIn("prologue 00028ea2", driver["semantics"])
        self.assertIn("writes:00029588@structural", self.vars["ffff158a"]["evidence"])

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
        self.assertIn("writes:00029588@structural", counter["evidence"])
        self.assertEqual(self.vars["ffff196c"]["units"], "ratio*64")
        self.assertIn("latches 9", self.vars["ffff13b4"]["note"])

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
        self.assertIn("110 degrees after that tooth", self.funcs["0004df82"]["note"])
        index = self.vars["ffff11de"]
        self.assertEqual(index["units"], "cylinder number 1..6")
        self.assertIn("110 degrees before compression TDC", index["semantics"])
        self.assertIn("110 degrees before compression", self.ignition)

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
        self.assertIn("P0301", builder["note"])
        attribution = self.vars["ffff4038"]
        self.assertEqual(attribution["units"], "cylinder number 1..6")
        self.assertIn("rom_const:0002265c=[0,4,5,6,1,2,3]", attribution["evidence"])
        self.assertIn("event index ffff11de equals the cylinder number", self.funcs["00085a70"]["note"])

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
        self.assertIn("190 or 98 degrees before intake TDC", self.fuel)

    def test_dwell_channel_tables_and_spark_edge(self):
        self.assertEqual(u32be(self.rom, 0x2AD9C), 0x00022680)
        self.assertEqual(u32be(self.rom, 0x2B094), 0x00022687)
        self.assertIn("rom_const:00022687=[0,2,4,8,16,32,1]", self.funcs["0002af38"]["evidence"])
        self.assertIn("spark edge", self.vars["ffff13bd"]["note"])
        self.assertIn("low state is the dwell", self.vars["ffff13d1"]["note"])
        self.assertIn("dwell angle in crank degrees", self.funcs["0004e080"]["note"])
        self.assertIn("## Crank reference and output edges", self.ignition)

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
        self.assertIn("D - 590 degrees after the following intake TDC", self.fuel)
        self.assertIn("not measured", self.fuel)
        self.assertIn("cylinder k + 1", self.vars["ffff2228"]["note"])
        self.assertEqual(self.rom[0x8770], 120)


if __name__ == "__main__":
    unittest.main()
