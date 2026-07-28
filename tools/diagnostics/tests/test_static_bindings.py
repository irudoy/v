import unittest

from tools.diagnostics import query


class StaticBindingQueryTest(unittest.TestCase):
    def test_binding_command_accepts_term_and_rom_filter(self):
        args = query.parser().parse_args(
            ["binding", "P0327", "--rom", "JK08A", "--limit", "10"]
        )
        self.assertEqual(args.command, "binding")
        self.assertEqual(args.term, "P0327")
        self.assertEqual(args.rom, "JK08A")
        self.assertEqual(args.limit, 10)

    def test_binding_query_keeps_confidence_and_applicability_separate(self):
        self.assertIn(
            "binding.confidence AS confidence",
            query.STATIC_BINDING_QUERY,
        )
        self.assertIn(
            "binding.applicability AS applicability",
            query.STATIC_BINDING_QUERY,
        )
        self.assertIn(
            "binding.source_verification AS source_verification",
            query.STATIC_BINDING_QUERY,
        )

    def test_dtc_and_firmware_addresses_are_exact_identifiers(self):
        self.assertEqual(
            query.canonical_binding_identifier("p0327"),
            "p0327",
        )
        self.assertEqual(
            query.canonical_binding_identifier("0xFFFF11AE"),
            "ffff11ae",
        )
        self.assertIsNone(query.canonical_binding_identifier("engine speed"))


if __name__ == "__main__":
    unittest.main()
