from pathlib import Path
import tempfile
import unittest

from kb import compile, matrix, repo
from kb.model import Builder
from kb.repo import KbError


def builder():
    return Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})


class CellTest(unittest.TestCase):
    def test_a_wire_limitation_keeps_a_native_source_unavailable(self):
        b = builder()
        group = ("ram", "field", "state_raw")
        source = b.symbol("7mfk", "ram", 0xFFFF1000, "p.toml", group=group)
        other = b.symbol("jk00d", "ram", 0xFFFF1100, "p.toml", group=group)
        b.name(group, "state", "field", "p.toml")
        b.entity("field", "state_raw", "p.toml", refs={"source": [source]})
        b.entity("feature", "can_telemetry", "p.toml", refs={"requires": [("field", "state_raw")]})
        b.target("can_telemetry", "jk00d", "p.toml", status="supported", props={
            "unsupported": [{"symbol": other, "note": "The bit layout needs conversion."}]})
        model = b.finish()
        self.assertEqual(matrix.unavailable(model, model.targets["can_telemetry", "jk00d"]),
                         {"unsupported": 1})

    def test_a_cell_states_the_status_of_the_target_and_what_the_model_derives(self):
        b = builder()
        group = ("ram", "field", "load_raw")
        source = b.symbol("7mfk", "ram", 0xFFFF102C, "p.toml", group=group)
        b.name(group, "normalized_load", "field", "p.toml")
        b.status(group, "jk00d", "unresolved", "c.csv")
        other = ("ram", "field", "speed_raw")
        speed = b.symbol("7mfk", "ram", 0xFFFF1030, "p.toml", group=other)
        b.name(other, "vehicle_speed", "field", "p.toml")
        b.entity("field", "load_raw", "p.toml", props={"origin": "ecu_ram"},
                 refs={"source": [source]})
        b.entity("field", "speed_raw", "p.toml", props={"origin": "ecu_ram"},
                 refs={"source": [speed]})
        b.entity("field", "tick16", "p.toml", props={"origin": "telemetry_state"})
        b.entity("feature", "can_telemetry", "p.toml", refs={"requires": [
            ("field", "load_raw"), ("field", "speed_raw"), ("field", "tick16")]})
        b.target("can_telemetry", "7mfk", "p.toml", status="supported",
                 props={"mailbox_index": 26})
        b.target("can_telemetry", "jk00d", "p.toml", status="supported",
                 props={"mailbox_index": 26, "roles": {"speed_raw": {"note": "role"}}})
        table = ("tbl", "file", "fuel_map")
        home = b.symbol("7mfk", "tbl", 0xA29A, "f.toml", group=table)
        b.name(table, "fuel_map", "file", "f.toml")
        b.status(table, "jk00d", "absent", "f.toml")
        b.entity("feature", "definitions", "d.toml")
        b.target("definitions", "jk00d", "d.toml", status="supported",
                 props={"requires": [home]})
        b.target("runtime", "jk00d", "r.toml", status="supported", props={
            "injected_rom_start": "000de808", "injected_rom_end": "000e2700",
            "injected_ram_start": "ffff6000", "injected_ram_end": "ffff6300"})
        b.target("map_switching", "jk00d", "m.toml", status="planned", props={
            "families": {"fuel": home, "timing": home}, "unsupported": [{"note": "none"}]})
        model = b.finish()
        gaps = matrix.missing(model)
        self.assertEqual(
            [matrix.cell(model, feature, layout, gaps) for feature, layout in (
                ("runtime", "jk00d"), ("map_switching", "jk00d"), ("can_telemetry", "7mfk"),
                ("can_telemetry", "jk00d"), ("definitions", "jk00d"),
                ("rolling_launch", "jk00d"))],
            ["supported; ROM `0xDE808..0xE2700`, RAM `0xFFFF6000..0xFFFF6300`",
             "planned; 2 switched families, 1 unsupported; 1 meaning without a symbol "
             "(1 absent)",
             "supported; mailbox 26; every field available",
             "supported; mailbox 26; 1 field unavailable (1 unresolved)",
             "supported; 1 meaning without a symbol (1 absent)",
             "no target"])


class SectionTest(unittest.TestCase):
    def test_the_section_orders_the_features_by_the_build_and_links_their_specifications(self):
        b = builder()
        for slug in ("zeta", "definitions", "can_telemetry", "rolling_launch",
                     "map_switching", "runtime"):
            b.entity("feature", slug, "f.toml", props={
                "title": slug.replace("_", " ").title(), "summary": f"The {slug} | feature.",
                "specs": [f"patches/{slug}.md"]})
        b.target("zeta", "7mfk", "f.toml", status="unsupported")
        model = b.finish()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "patches").mkdir()
            for slug in matrix.order(model):
                (root / "patches" / f"{slug}.md").write_text("# Spec\n", encoding="utf-8")
            lines = matrix.render(model, root).splitlines()
            (root / "patches" / "zeta.md").unlink()
            with self.assertRaises(KbError) as refused:
                matrix.render(model, root)
        self.assertEqual(lines[:4], ["", "", "## Feature targets", ""])
        self.assertIn("| Layout | Images | Runtime | Map Switching | Rolling Launch | "
                      "Can Telemetry | Definitions | Zeta |", lines)
        self.assertIn("| `7mfk` | JK00A, JK03A, JK03B, JK08A | no target | no target | "
                      "no target | no target | no target | unsupported |", lines)
        self.assertIn("| Zeta (`zeta`) | The zeta \\| feature. | "
                      "[`patches/zeta.md`](../patches/zeta.md) |", lines)
        self.assertEqual(lines[-1], "")
        self.assertEqual((refused.exception.code, str(refused.exception)),
                         (3, "zeta/feature: specs names no file patches/zeta.md"))


if __name__ == "__main__":
    unittest.main()
