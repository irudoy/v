import unittest

from kb import sites

# Stage 1 of tools/kb/SPEC.md: at least this share of the `site:` tokens of
# the JK08A ledgers reproduces from L0.
REQUIRED_SHARE = 0.85


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


class JK08ALedgerSitesTest(unittest.TestCase):
    def test_the_site_tokens_of_the_ledgers_reproduce_from_l0(self):
        found = sites.ledger_sites("7mfk", "JK08A")
        counts = sites.summary(found)["all"]
        self.assertGreater(sum(counts.values()), 10000)
        self.assertGreaterEqual(sites.share(counts), REQUIRED_SHARE, dict(counts))


if __name__ == "__main__":
    unittest.main()
