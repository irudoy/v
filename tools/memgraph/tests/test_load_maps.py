import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

    def implicit_2d(self, **changes):
        return {"family": "implicit-2d", "kernel": "00028908", "wrapper": "00027d74",
                "width": "8", "height": "8", "step": "32", "storagetype": "uint8",
                "axistype_x": "", "axistype_y": "", **changes}

    def test_implicit_2d_entry_declares_both_dimensions_its_step_and_element(self):
        reg = load_maps.read_registry(self.registry([self.implicit_2d()]))
        geometry = load_maps.geometry(reg[0])
        self.assertEqual(geometry, {"dims": 2, "width": 8, "height": 8, "step": 32,
                                    "limit": 224, "storagetype": "uint8"})

    def test_implicit_2d_entry_takes_its_element_from_the_registry(self):
        # The finisher reads uint16 cells; the limit of the byte inputs does not
        # select the element as it does for a one-dimensional implicit entry.
        reg = load_maps.read_registry(self.registry([self.implicit_2d(storagetype="uint16")]))
        self.assertEqual(load_maps.geometry(reg[0])["storagetype"], "uint16")

    def test_implicit_2d_entry_refuses_a_missing_or_foreign_declaration(self):
        for changes, message in (
                ({"step": ""}, "lacks an axis step"),
                ({"storagetype": ""}, "its finisher reads it"),
                ({"height": ""}, "one point count"),
                ({"height": "16"}, "one point count"),
                ({"axistype_x": "uint8"}, "no axis array"),
                ({"axistype_y": "uint8"}, "no axis array")):
            with self.subTest(changes=changes):
                path = self.registry([self.implicit_2d(**changes)])
                with self.assertRaises(SystemExit) as raised:
                    load_maps.read_registry(path)
                self.assertIn(message, str(raised.exception))

    def test_tracked_1me3b_registry_is_fused_throughout(self):
        reg = load_maps.read_registry(str(ROOT / "defs" / "registries" / "1ME3B.interp.csv"))
        self.assertEqual(len(reg), 37)
        self.assertTrue(all(e["kernel"] == e["wrapper"] for e in reg))
        implicit = [e for e in reg if e["family"] == "implicit"]
        self.assertEqual(len(implicit), 10)
        self.assertTrue(all(not e["height"] for e in implicit))
        two_d = [e for e in reg if e["height"]]
        self.assertEqual(len(two_d), 18)
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

    def test_implicit_2d_entry_reads_a_map_without_axis_nodes(self):
        # r5 and r6 carry raw inputs; a recovered ROM value there is no axis.
        entry = {
            "family": "implicit-2d", "kernel": "00026ae0", "wrapper": "00026040",
            "width": "8", "height": "8", "step": "32", "storagetype": "uint8",
            "axistype_x": "", "axistype_y": "",
        }
        rows = [with_geometry(
            census_row("00026ae0", "00026040", "0000a8ea", "00010020", "00010030"), entry)]
        maps, axes, interps, kernels, accesses, dropped = load_maps.build(rows)
        self.assertEqual(axes, {})
        self.assertEqual(interps["00026ae0"]["role"], "kernel")
        self.assertEqual(interps["00026040"]["role"], "wrapper")
        self.assertEqual(kernels, {"00026040": "00026ae0"})
        table = maps["0000a8ea"]
        self.assertEqual((table["family"], table["dims"], table["width"], table["height"],
                          table["step"], table["limit"], table["storagetype"]),
                         ("implicit-2d", 2, 8, 8, 32, 224, "uint8"))
        self.assertEqual((accesses[0]["axis_x"], accesses[0]["axis_y"]), ("", ""))
        self.assertEqual(dropped, 0)

    def test_fused_implicit_2d_entry_is_its_own_kernel(self):
        entry = {
            "family": "implicit-2d", "kernel": "000289cc", "wrapper": "000289cc",
            "width": "8", "height": "8", "step": "8192", "storagetype": "uint16",
            "axistype_x": "", "axistype_y": "",
        }
        rows = [with_geometry(census_row("000289cc", "000289cc", "0000b97a"), entry)]
        maps, axes, interps, kernels, accesses, dropped = load_maps.build(rows)
        self.assertEqual(set(interps), {"000289cc"})
        self.assertEqual(interps["000289cc"]["role"], "fused")
        self.assertEqual(maps["0000b97a"]["limit"], 7 * 8192)
        self.assertEqual(maps["0000b97a"]["storagetype"], "uint16")


class FindingsTest(unittest.TestCase):
    def test_a_manual_row_cannot_declare_the_implicit_2d_access_model(self):
        header = load_maps.FINDING_FIELDS
        row = dict.fromkeys(header, "")
        row.update(addr="0000a8ea", family="implicit-2d", width="8", height="8",
                   storagetype="uint8", confidence="candidate", role="table")
        tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        writer = csv.DictWriter(tmp, fieldnames=header)
        writer.writeheader()
        writer.writerow(row)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        with self.assertRaises(SystemExit) as raised:
            load_maps.apply_findings(tmp.name, {}, [])
        self.assertIn("which is an access model", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
