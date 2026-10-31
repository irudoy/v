"""The periodic task tables are read from the ROM images that the project runs.

Every published entry number is an index into a pointer table whose base and
length the dispatcher loop carries in its own instructions. The decoder below
recovers both from the instruction bytes, so a document that names an entry is
checked against the silicon rather than against another document.
"""

import struct
import unittest
from pathlib import Path

from kb import store


ROOT = Path(__file__).resolve().parents[3]
IMAGES = ROOT / "rom-images"

# Dispatcher loops of JK08A, by the address of the pointer load.
PERIODIC_LOOP = 0x212F0
PENDING_LOOP = 0x20C98

# Table identities the repository publishes for JK08A.
PERIODIC_TABLE = 0x2196C
PERIODIC_ENTRIES = 124
PENDING_TABLE = 0x21834
PENDING_ENTRIES = 69

# Published entry numbers of the JK08A periodic table.
PERIODIC_INDEX_BY_FUNCTION = {
    0x769C0: 12,
    0x71508: 19,
    0x702A0: 21,
    0x79DD8: 22,
    0x730FC: 23,
    0x4ED88: 28,
    0x57608: 36,
    0x56FC0: 39,
    0x53698: 40,
    0x522C4: 42,
    0x4E974: 43,
    0x5C910: 55,
    0x4ECAC: 61,
    0x4E576: 64,
    0x493E8: 65,
    0x65434: 66,
    0x4D888: 71,
    0x57020: 81,
    0xC21E6: 84,
    0x65E54: 96,
    0x7BFC4: 101,
    0xA9554: 1,
}

# Published entry numbers of the JK08A pending-task table.
PENDING_INDEX_BY_FUNCTION = {
    0x39A8C: 22,
    0x394B8: 24,
    0x39788: 27,
    0x3EB84: 28,
    0x79DE4: 58,
    0xC38DE: 61,
    0xC3DE4: 63,
}

# Homologous tables, by ROM directory: base, entries, and the hooked entry.
TARGET_TABLES = {
    "23710-JK08A": (0x2196C, 124, 0x21970),
    "23710-JK00C": (0x219EC, 127, 0x219F0),
    "23710-JK00D": (0x219EC, 127, 0x219F0),
    "23710-1ND0A": (0x22058, 148, 0x2205C),
    "23710-1ME3B": (0x220C4, 152, 0x220C8),
    "23710-JK78C": (0x21A4C, 144, 0x21A4C),
}

# Knowledge-base layout of each ROM directory.
LAYOUTS = {
    "23710-JK08A": "7mfk",
    "23710-JK00C": "jk00c",
    "23710-JK00D": "jk00d",
    "23710-1ND0A": "1nd",
    "23710-1ME3B": "1me3b",
    "23710-JK78C": "jk78c",
}


def symbol_addresses(kind, name):
    """Return the address of each layout symbol of one knowledge-base meaning."""

    document = store.load(ROOT, store.path_of(kind, name))
    return {
        symbol["layout"]: int(symbol["address"], 16)
        for symbol in document["symbol"]
    }


def image(name):
    directory = IMAGES / name
    images = sorted(directory.glob("*stock*.bin"))
    return images[0].read_bytes()


def word(rom, address):
    return struct.unpack_from(">H", rom, address)[0]


def longword(rom, address):
    return struct.unpack_from(">I", rom, address)[0]


def decode_table_walk(rom, load_address):
    """Return (base, entries) of the pointer table the loop at this address walks.

    The loop reads a pointer through `mov.l @Rm,Rn`, `mov.l @Rm+,Rn`, or
    `mov.l @(R0,Rm),Rn`, calls it, and counts iterations down with `dt Rk`.
    The base comes from the PC-relative longword that initializes Rm, and the
    length from the immediate that initializes Rk.
    """

    load = word(rom, load_address)
    if load & 0xF00F not in (0x6002, 0x6006, 0x000E):
        raise AssertionError(f"{load_address:#x}: not a pointer load")
    pointer = (load >> 4) & 0xF
    counter = None
    for offset in range(2, 12, 2):
        candidate = word(rom, load_address + offset)
        if candidate & 0xF0FF == 0x4010:
            counter = (candidate >> 8) & 0xF
            break
    if counter is None:
        raise AssertionError(f"{load_address:#x}: no decrement found")

    base = entries = None
    for offset in range(2, 20, 2):
        instruction = word(rom, load_address - offset)
        register = (instruction >> 8) & 0xF
        if (
            base is None
            and instruction & 0xF000 == 0xD000
            and register == pointer
        ):
            literal = ((load_address - offset) & ~3) + 4 + (instruction & 0xFF) * 4
            base = longword(rom, literal)
        if (
            entries is None
            and instruction & 0xF000 == 0xE000
            and register == counter
        ):
            entries = instruction & 0xFF
    if base is None or entries is None:
        raise AssertionError(f"{load_address:#x}: table base or length not found")
    return base, entries


def table_index(rom, base, entries):
    index = {}
    for position in range(entries):
        index.setdefault(longword(rom, base + 4 * position), position)
    return index


class PeriodicSchedulerTableTest(unittest.TestCase):
    def setUp(self):
        self.rom = image("23710-JK08A")

    def test_the_dispatcher_loops_carry_their_table_identities(self):
        self.assertEqual(
            decode_table_walk(self.rom, PERIODIC_LOOP),
            (PERIODIC_TABLE, PERIODIC_ENTRIES),
        )
        self.assertEqual(
            decode_table_walk(self.rom, PENDING_LOOP),
            (PENDING_TABLE, PENDING_ENTRIES),
        )

    def test_published_periodic_entries_match_the_table(self):
        index = table_index(self.rom, PERIODIC_TABLE, PERIODIC_ENTRIES)
        for function, entry in PERIODIC_INDEX_BY_FUNCTION.items():
            with self.subTest(function=f"{function:06x}"):
                self.assertEqual(index.get(function), entry)

    def test_published_pending_entries_match_the_table(self):
        index = table_index(self.rom, PENDING_TABLE, PENDING_ENTRIES)
        for function, entry in PENDING_INDEX_BY_FUNCTION.items():
            with self.subTest(function=f"{function:06x}"):
                self.assertEqual(index.get(function), entry)

    def test_every_homologous_table_holds_its_hooked_entry(self):
        for name, (base, entries, slot) in TARGET_TABLES.items():
            with self.subTest(rom=name):
                rom = image(name)
                self.assertEqual((slot - base) % 4, 0)
                self.assertLess((slot - base) // 4, entries)
                self.assertEqual(
                    decode_table_walk(rom, self._periodic_loop(rom)),
                    (base, entries),
                )

    def _periodic_loop(self, rom):
        """Return the address of the periodic pointer load in this image."""

        for address in range(0x20800, 0x21800, 2):
            load = word(rom, address)
            if load & 0xF00F not in (0x6002, 0x6006):
                continue

            if word(rom, address + 2) & 0xF0FF != 0x400B:
                continue
            tail = address + 4
            if word(rom, tail) == 0x0009:
                tail += 2
            elif word(rom, tail) & 0xF0FF != 0x7004:
                continue
            else:
                tail += 2
            if word(rom, tail) & 0xF0FF != 0x4010:
                continue
            if word(rom, tail + 2) & 0xFF00 != 0x8B00:
                continue
            try:
                base, entries = decode_table_walk(rom, address)
            except AssertionError:
                continue
            if entries >= 100 and 0x21000 <= base < 0x23000:
                return address
        raise AssertionError("periodic dispatcher loop not found")

    def test_the_knowledge_base_states_each_table_and_hooked_entry(self):
        tables = symbol_addresses("const", "periodic_task_table")
        hooks = symbol_addresses("hook", "displaced_periodic_task")
        for name, (base, _entries, slot) in TARGET_TABLES.items():
            layout = LAYOUTS[name]
            with self.subTest(rom=name):
                self.assertEqual(tables[layout], base)
                self.assertEqual(hooks[layout], slot)


if __name__ == "__main__":
    unittest.main()
