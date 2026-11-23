import csv
import hashlib
import io
from itertools import combinations_with_replacement
from pathlib import Path
import tempfile
import unittest

from kb import repo, sites

# Stage 1 of tools/kb/SPEC.md: at least this share of the `site:` tokens of
# the JK08A ledgers reproduces from L0.
REQUIRED_SHARE = 0.85

# Code of the synthetic layout t1: A continues into B, C calls D with `bsr`,
# and E reaches F with a `bra` that a flow override records as a call.
CODE = {
    0x00: 0xE001,  # A: mov #1,r0
    0x02: 0x0009,  # nop
    0x04: 0x0009,  # nop, continues into B
    0x06: 0x0009,  # B: nop
    0x08: 0x000B,  # rts
    0x0A: 0x0009,  # nop in the delay slot, before C
    0x0C: 0xB002,  # C: bsr 0x14
    0x0E: 0x0009,  # nop
    0x10: 0x000B,  # rts
    0x12: 0x0009,  # nop in the delay slot, before D
    0x14: 0x0009,  # D: nop
    0x16: 0x000B,  # rts
    0x18: 0x0009,  # nop in the delay slot, before E
    0x1A: 0xA001,  # E: bra 0x20
    0x1C: 0x0009,  # nop in the delay slot
    0x1E: 0x1234,  # a literal word outside every body
    0x20: 0x0009,  # F: nop
    0x22: 0x000B,  # rts
    0x24: 0x0009,  # nop in the delay slot
}
BODIES = {0x00: (0x00, 0x02, 0x04), 0x06: (0x06, 0x08, 0x0A),
          0x0C: (0x0C, 0x0E, 0x10, 0x12), 0x14: (0x14, 0x16, 0x18),
          0x1A: (0x1A, 0x1C), 0x20: (0x20, 0x22, 0x24)}
LEDGER = (
    ("00000000", "site:00000002;site:00000006;site:0000001e", "A"),
    ("00000006", "site:00000000", "B after 00000000"),
    ("0000000c", "site:00000014", "C"),
    ("00000014", "trace:00000020@structural;site:0000000e;site:00000022", "D"),
    ("0000001a", "site:00000022", "E"),
    ("00000020", "site:0000001a", "F"),
)


def table(header, *rows):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def synthetic_root(base):
    """A repository root with layout t1 of image T1, the L0 files that the
    `sites` check reads, and the function ledger `defs/registries/T1.funcs.csv`."""
    root = Path(base) / "repo"
    image = bytearray(0x40)
    for address, word in CODE.items():
        image[address:address + 2] = word.to_bytes(2, "big")
    (root / "rom-images/T1").mkdir(parents=True)
    (root / "rom-images/T1/T1.bin").write_bytes(bytes(image))
    write(root / repo.CATALOG, table(("path", "rom", "sha256", "note"), (
        "T1/T1.bin", "T1", hashlib.sha256(bytes(image)).hexdigest(), "synthetic")))
    write(root / repo.HOMOLOGY, (
        '[family.test]\nkind = "exact-code"\nmembers = ["T1"]\ncanonical = "T1"\n'
        'mcu = "SH7058"\nsame_address_inheritance = false\nlayouts = { t1 = "T1" }\n'
    ))
    write(root / repo.CONFIG, '[l0.census.t1]\ninterp = "defs/registries/T1.interp.csv"\n')
    write(root / "defs/registries/T1.interp.csv", "family,kernel,wrapper\n")
    base = root / repo.L0 / "t1"
    write(base / "function_tokens.csv", table(
        ("func_addr", "ins_addr", "ordinal", "mnemonic", "shape"),
        *((f"{entry:08x}", f"{address:08x}", index, "nop", "nop")
          for entry, body in BODIES.items() for index, address in enumerate(body))))
    write(base / "function_references.csv", table(
        ("func_addr", "ins_addr", "ordinal", "mnemonic", "ref_addr", "width", "value_hex",
         "ref_type"),
        ("0000000c", "0000000c", "0", "bsr", "00000014", "0", "", "unconditional_call"),
        ("0000001a", "0000001a", "0", "bra", "00000020", "0", "", "unconditional_call"),
    ))
    write(root / "defs/registries/T1.funcs.csv", table(
        ("addr", "role", "semantics", "contract", "contract_conf", "contract_evidence",
         "confidence", "evidence", "note"),
        *((addr, "accessor", prose, "", "", "", "code", evidence, "")
          for addr, evidence, prose in LEDGER)))
    return root


class ClassifyTest(unittest.TestCase):
    DATA = bytes(0x100) + bytes.fromhex("ffff1026") + bytes(0x100)

    def classify(self, site, subject=0xFFFF1000, span=1, named=frozenset(), found=None,
                 owned=None, links=()):
        return sites.classify(site, subject, span, set(named), found or {}, owned or {},
                              self.DATA, list(links))

    def test_kinds_in_precedence_order(self):
        self.assertEqual(self.classify(0x10, found={0x10: {0xFFFF1000}}), "reference")
        self.assertEqual(self.classify(0x10, subject=0x9000, span=16,
                                       found={0x10: {0x900E}}), "reference")
        self.assertEqual(self.classify(0x10, subject=0x9000, span=16,
                                       found={0x10: {0x9010}}), None)
        self.assertEqual(self.classify(0x10, named={0x400}, owned={0x10: {0x400}}), "body")
        self.assertEqual(self.classify(0x100, named={0xFFFF1026}), "pointer")
        self.assertEqual(self.classify(0x10, owned={0x10: {0x500}},
                                       links=[(0xFFFF1000, 0x500)]), "linked")
        self.assertEqual(self.classify(0x10, owned={0x10: {0x500}},
                                       links=[(0xFFFF1001, 0x500)]), None)

    def test_extent_follows_the_stated_dimensions(self):
        self.assertEqual(sites.extent("maps", {"dim": "1D-8", "storagetype": "uint16"}), 16)
        self.assertEqual(sites.extent("maps", {"dim": "16x16", "storagetype": "uint8"}), 256)
        self.assertEqual(sites.extent("findings", {"width": "", "height": "",
                                                   "storagetype": ""}), 1)
        self.assertEqual(sites.extent("vars", {}), 1)


class LinkedRangeTest(unittest.TestCase):
    def test_duplicate_pairs_and_interval_boundaries_follow_the_address_range(self):
        pairs = [(0, 10), (2, 20), (2, 20), (2, 21), (3, 30), (7, 70)]
        for values in (pairs, tuple(pairs)):
            for subject, span in ((-1, 1), (0, 1), (1, 1), (2, 1), (2, 2),
                                  (3, 4), (3, 5), (8, 1), (2, 0), (2, -1)):
                with self.subTest(values=type(values).__name__, subject=subject, span=span):
                    expected = {owner for address, owner in pairs
                                if subject <= address < subject + span}
                    self.assertEqual(sites.linked(subject, span, values), expected)
        self.assertEqual(sites.linked(0, 1, []), set())
        self.assertEqual(sites.linked(0, 1, ()), set())

    def test_small_sorted_multisets_match_an_independent_interval_set(self):
        pairs = [(address, owner) for address in range(3) for owner in range(2)]
        for length in range(4):
            for values in combinations_with_replacement(pairs, length):
                for subject in range(-1, 5):
                    for span in (-1, 0, 1, 2, 4):
                        expected = {owner for address, owner in values
                                    if subject <= address < subject + span}
                        self.assertEqual(sites.linked(subject, span, values), expected)

    def test_repeated_queries_return_fresh_sets_and_observe_pair_changes(self):
        pairs = [(0, 10), (1, 20)]
        first = sites.linked(0, 2, pairs)
        first.add(30)
        self.assertEqual(sites.linked(0, 2, pairs), {10, 20})
        pairs[1] = (1, 40)
        self.assertEqual(sites.linked(0, 2, pairs), {10, 40})

    def test_a_narrow_query_does_not_copy_or_scan_the_unrelated_suffix(self):
        class ObservedPairs(list):
            examined = 0

            def __getitem__(self, key):
                self.examined += len(range(*key.indices(len(self)))) if isinstance(key, slice) else 1
                return super().__getitem__(key)

            def __iter__(self):
                for value in super().__iter__():
                    self.examined += 1
                    yield value

        pairs = ObservedPairs((address, address % 11) for address in range(100000))
        self.assertEqual(sites.linked(0, 1, pairs), {0})
        self.assertLessEqual(pairs.examined, 64)


class SitesCheckTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = synthetic_root(scratch.name)

    def test_continuation_stops_at_transfers_and_their_delay_slots(self):
        self.assertEqual(sites.runs_into("t1", self.root), {
            0x00: {0x06}, 0x06: set(), 0x0C: set(), 0x14: set(), 0x1A: set(), 0x20: set()})

    def test_calls_are_call_instructions_in_both_directions(self):
        self.assertEqual(dict(sites.calls("t1", self.root)), {0x0C: {0x14}, 0x14: {0x0C}})
        self.assertEqual(sites.related("t1", 0x00, self.root), {0x00, 0x06})
        self.assertEqual(sites.related("t1", 0x14, self.root), {0x14, 0x0C})
        self.assertEqual(sites.related("t1", 0x1A, self.root), {0x1A})

    def test_a_site_in_an_unrelated_body_fails(self):
        failures = [line.split(" lies in the body of ")
                    for line in sites.check(self.root)]
        self.assertEqual([(head, tail.split(",")[0]) for head, tail in failures], [
            ("defs/registries/T1.funcs.csv: 00000006: site:00000000", "00000000"),
            ("defs/registries/T1.funcs.csv: 0000001a: site:00000022", "00000020"),
        ])


class JK08ALedgerSitesTest(unittest.TestCase):
    def test_the_site_tokens_of_the_ledgers_reproduce_from_l0(self):
        found = sites.ledger_sites("7mfk", "JK08A")
        counts = sites.summary(found)["all"]
        self.assertGreater(sum(counts.values()), 10000)
        self.assertGreaterEqual(sites.share(counts), REQUIRED_SHARE, dict(counts))


if __name__ == "__main__":
    unittest.main()
