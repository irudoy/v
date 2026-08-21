from pathlib import Path
import tempfile
import tomllib
import unittest

from tools.mapkit import definition_targets


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
ROMS = (
    "JK00A",
    "JK03A",
    "JK03B",
    "JK08A",
    "JK00C",
    "JK00D",
    "JK78C",
)


class DefinitionTargetsTest(unittest.TestCase):
    def test_registered_targets_have_deterministic_family_order(self):
        self.assertEqual(definition_targets.registered_targets(), ROMS)
        self.assertEqual(definition_targets.registered_sources(), ("JK08A",))

    def test_all_registered_targets_bind_to_their_stock_identity(self):
        for rom in ROMS:
            with self.subTest(rom=rom):
                target = definition_targets.load_target(rom)
                self.assertEqual(target.rom, rom)
                self.assertEqual(target.source, "JK08A")
                self.assertEqual(target.image.rom, rom)
                self.assertEqual(
                    target.definition_projection is not None,
                    rom in {"JK00C", "JK00D", "JK78C"},
                )
                address = int(target.romid["internalidaddress"], 16)
                identity = target.romid["internalidstring"].encode("ascii")
                self.assertEqual(
                    target.image.data[address : address + len(identity)],
                    identity,
                )

    def test_target_presentation_is_materialized_without_source_copies(self):
        with (DEFS / "JK08A.overrides.toml").open("rb") as source:
            canonical = tomllib.load(source)
        target = definition_targets.load_target("JK00A")
        materialized = definition_targets.materialize_overrides(
            target, canonical
        )

        self.assertEqual(canonical["rom"]["xmlid"], "JK08A")
        self.assertEqual(materialized["rom"]["xmlid"], "JK00A")
        self.assertEqual(materialized["rom"]["submodel"], "VQ35HR")
        self.assertIn(
            "Exact JK00A only",
            materialized["switch"][0]["description"],
        )
        self.assertIn(
            "defs/JK08A.notes.md",
            materialized["rom"]["comment"]["text"],
        )
        self.assertNotIn(
            definition_targets.TARGET_ROM_TOKEN,
            materialized["switch"][0]["description"],
        )
        self.assertEqual(
            materialized["rom"]["comment"]["text"],
            canonical["rom"]["comment"]["text"],
        )

    def test_unregistered_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "identities.toml"
            path.write_text(
                "schema_version = 1\n\n"
                "[rom.UNKNOWN]\n"
                + "\n".join(
                    f'{field} = "value"'
                    for field in definition_targets.ROMID_FIELDS
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                definition_targets.DefinitionTargetError,
                "no editor identity",
            ):
                definition_targets.load_target("JK08A", path)


if __name__ == "__main__":
    unittest.main()
