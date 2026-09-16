import csv
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if "neo4j" not in sys.modules:
    neo4j = types.ModuleType("neo4j")
    neo4j.GraphDatabase = object
    sys.modules["neo4j"] = neo4j

import load_maps  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HEADER = ["family", "kernel", "wrapper", "width", "height", "step", "storagetype",
          "axistype_x", "axistype_y"]


def census_row(kernel, wrapper, base, axis_x="", axis_y="", callsite="00040010"):
    return {
        "kernel": kernel, "wrapper": wrapper, "slot": "00040100",
        "accessor": "00040000", "callsite": callsite, "func": "orig",
        "bt_r4": base, "bt_r5": axis_x, "bt_r6": axis_y,
        "df_r4": base, "df_r5": axis_x, "df_r6": axis_y, "df_r7": "",
        "k4": "pool", "k5": "pool" if axis_x else "none",
        "k6": "pool" if axis_y else "none", "k7": "none",
        "verdict": "agree", "branch": "",
    }


def with_geometry(row, entry):
    out = dict(row)
    for column in ("family", "width", "height", "step", "storagetype",
                   "axistype_x", "axistype_y"):
        out[column] = entry[column]
    return out


class RegistryTest(unittest.TestCase):
    def registry(self, rows):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        writer = csv.DictWriter(tmp, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return tmp.name

    def test_fused_entry_names_itself_as_kernel(self):
        path = self.registry([{
            "family": "explicit", "kernel": "0002a0b4", "wrapper": "0002a0b4",
            "width": "16", "height": "16", "step": "", "storagetype": "uint16",
            "axistype_x": "uint16", "axistype_y": "uint16",
        }])
        reg = load_maps.read_registry(path)
        self.assertEqual(reg[0]["kernel"], reg[0]["wrapper"])

    def test_tracked_1me3b_registry_is_fused_throughout(self):
        reg = load_maps.read_registry(str(ROOT / "defs" / "1ME3B.interp.csv"))
        self.assertEqual(len(reg), 34)
        self.assertTrue(all(e["kernel"] == e["wrapper"] for e in reg))
        implicit = [e for e in reg if e["family"] == "implicit"]
        self.assertEqual(len(implicit), 9)
        self.assertTrue(all(not e["height"] for e in implicit))
        two_d = [e for e in reg if e["height"]]
        self.assertEqual(len(two_d), 16)
        self.assertTrue(all(e["width"] == e["height"] for e in two_d))


class BuildTest(unittest.TestCase):
    def test_fused_entry_carries_geometry_and_no_kernel_relationship(self):
        entry = {
            "family": "explicit", "kernel": "0002af88", "wrapper": "0002af88",
            "width": "16", "height": "", "step": "", "storagetype": "uint16",
            "axistype_x": "uint16", "axistype_y": "",
        }
        rows = [with_geometry(census_row("0002af88", "0002af88", "00010000", "00010020"),
                              entry)]
        maps, axes, interps, kernels, accesses, dropped = load_maps.build(rows)
        self.assertEqual(set(interps), {"0002af88"})
        node = interps["0002af88"]
        self.assertEqual(node["role"], "fused")
        self.assertEqual((node["dims"], node["width"], node["storagetype"]),
                         (1, 16, "uint16"))
        self.assertEqual(kernels, {"0002af88": "0002af88"})
        self.assertEqual(set(maps), {"00010000"})
        self.assertEqual(set(axes), {"00010020"})
        self.assertEqual(axes["00010020"]["len"], 16)
        self.assertEqual(len(accesses), 1)
        self.assertEqual(dropped, 0)

    def test_wrapper_entry_keeps_a_separate_kernel_node(self):
        entry = {
            "family": "explicit", "kernel": "00028d88", "wrapper": "00028440",
            "width": "4", "height": "4", "step": "", "storagetype": "uint8",
            "axistype_x": "uint8", "axistype_y": "uint8",
        }
        rows = [with_geometry(
            census_row("00028d88", "00028440", "00010000", "00010020", "00010030"), entry)]
        maps, axes, interps, kernels, accesses, dropped = load_maps.build(rows)
        self.assertEqual(set(interps), {"00028d88", "00028440"})
        self.assertEqual(interps["00028d88"]["role"], "kernel")
        self.assertEqual(interps["00028440"]["role"], "wrapper")
        self.assertEqual(kernels, {"00028440": "00028d88"})
        self.assertEqual(set(axes), {"00010020", "00010030"})


if __name__ == "__main__":
    unittest.main()
