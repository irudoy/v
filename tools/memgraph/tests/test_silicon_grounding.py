import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
HARDWARE = ROOT / "patches" / "hardware-results.toml"

EVIDENCE_COLUMN = {
    "confidence": "evidence",
    "scale_conf": "scale_evidence",
    "contract_conf": "contract_evidence",
}
HARDWARE_TOKEN = "spec:hardware-results:"


def silicon_claims():
    """Yield (path, row id, property, evidence) for every silicon source claim."""
    for path in sorted(DEFS.glob("*.csv")):
        if path.name.endswith(".maps.csv"):
            continue
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            key = reader.fieldnames[0]
            for row in reader:
                for prop, column in EVIDENCE_COLUMN.items():
                    if row.get(prop) == "silicon":
                        yield path.name, row[key], prop, row.get(column)


class SiliconGroundingTest(unittest.TestCase):
    """Only a recorded hardware result establishes silicon behavior."""

    @classmethod
    def setUpClass(cls):
        with HARDWARE.open("rb") as source:
            cls.hardware = tomllib.load(source)

    def resolve(self, dotted):
        node = self.hardware
        for part in dotted.split("."):
            self.assertIsInstance(node, dict, dotted)
            self.assertIn(part, node, dotted)
            node = node[part]
        return node

    def test_every_silicon_claim_names_a_passing_hardware_result(self):
        claims = list(silicon_claims())
        self.assertTrue(claims)
        for name, row_id, prop, evidence in claims:
            with self.subTest(file=name, row=row_id, prop=prop):
                self.assertIsNotNone(evidence)
                keys = [
                    token.removeprefix(HARDWARE_TOKEN)
                    for token in (item.strip() for item in evidence.split(";"))
                    if token.startswith(HARDWARE_TOKEN)
                ]
                self.assertTrue(keys)
                for key in keys:
                    result = self.resolve(key)
                    self.assertEqual(result.get("hardware_status"), "pass")


if __name__ == "__main__":
    unittest.main()
