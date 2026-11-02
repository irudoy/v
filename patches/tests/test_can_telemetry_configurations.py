import json
from pathlib import Path
import tempfile
import tomllib
import unittest

from patches import can_telemetry_configurations as configurations
from tools.logs import can_telemetry_schema


CAPTURE = Path(configurations.__file__).with_name("can-telemetry-capture.s")


def catalog_text(change=None):
    raw = tomllib.loads(configurations.DEFAULT_SOURCE.read_text(encoding="utf-8"))
    if change is not None:
        change(raw)
    return raw


def write_toml(raw, directory):
    """Write the subset of TOML that the catalog uses."""

    def value(item):
        if isinstance(item, bool):
            return "true" if item else "false"
        if isinstance(item, (int, float)):
            return str(item)
        if isinstance(item, str):
            return json.dumps(item)
        if isinstance(item, list):
            return "[" + ", ".join(value(entry) for entry in item) + "]"
        return "{ " + ", ".join(f"{key} = {value(entry)}" for key, entry in item.items()) + " }"

    lines = [
        f"{key} = {value(raw[key])}"
        for key in ("schema_version", "profile", "rom")
    ]
    for table in ("configuration", "slot"):
        for row in raw[table]:
            lines.append(f"[[{table}]]")
            lines.extend(f"{key} = {value(entry)}" for key, entry in row.items())
    path = Path(directory) / "catalog.toml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class CatalogTest(unittest.TestCase):
    def load(self, change):
        with tempfile.TemporaryDirectory() as directory:
            return configurations.load_catalog(write_toml(catalog_text(change), directory))

    def test_the_slots_bind_the_rolling_launch_state_and_ecu_ram(self):
        catalog = configurations.load_catalog()
        addresses = {name: slot.address for name, slot in catalog.slots.items()}
        self.assertEqual(addresses, {
            "rolling_launch_speed_error_raw": 0xFFFF5D50,
            "rolling_launch_torque_fraction_raw": 0xFFFF5D4E,
            "rolling_launch_integrator_raw": 0xFFFF5D52,
            "rolling_launch_cut_counter": 0xFFFF5D5D,
            "ignition_dwell_angle_raw": 0xFFFF237A,
            "speed_frame_receive_age_raw": 0xFFFF3B38,
        })
        self.assertEqual(
            [item.configuration_id for item in catalog.configurations], [1, 2]
        )

    def test_the_ram_window_is_the_window_of_the_capture(self):
        text = CAPTURE.read_text(encoding="utf-8")
        for label, bound in zip(
            ("telemetry_dynamic_window_start", "telemetry_dynamic_window_end"),
            configurations.RAM_WINDOW,
        ):
            literal = text.split(f"{label}:\n", 1)[1].split("\n", 1)[0]
            self.assertEqual(literal, f".long 0x{bound & 0x00FFFFFF:08X}")

    def test_the_catalog_refuses_layouts_the_ecu_rejects(self):
        def widen(raw):
            raw["configuration"][1]["groups"][1] += ["rolling_launch_torque_fraction_raw", "rolling_launch_speed_error_raw"]

        def unaligned(raw):
            raw["slot"][0]["source"] = {"ecu_ram": 0xFFFF237B, "specification": "patches/rolling-launch.md"}

        def outside(raw):
            raw["slot"][4]["source"] = {"ecu_ram": 0xFFFFC000, "specification": "patches/rolling-launch.md"}

        def beyond_view(raw):
            raw["slot"][3]["source"] = {"rolling_launch": "spark_cut_counters", "byte": 2}

        def unused(raw):
            raw["configuration"][1]["groups"][1].remove("speed_frame_receive_age_raw")

        cases = {
            "group above six bytes": widen,
            "ID 0": lambda raw: raw["configuration"][0].update(id=0),
            "ID 128": lambda raw: raw["configuration"][0].update(id=128),
            "repeated ID": lambda raw: raw["configuration"][1].update(id=1),
            "three groups": lambda raw: raw["configuration"][1]["groups"].append(["rolling_launch_cut_counter"]),
            "unknown slot": lambda raw: raw["configuration"][0]["groups"][0].append("x"),
            "width 3": lambda raw: raw["slot"][0].update(width=3),
            "unaligned word": unaligned,
            "outside the RAM window": outside,
            "byte outside its view": beyond_view,
            "unknown view": lambda raw: raw["slot"][0].update(source={"rolling_launch": "x"}),
            "unused slot": unused,
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.load(change)

    def test_frames_encode_slot_group_width_and_address(self):
        catalog = configurations.load_catalog()
        frames = configurations.configuration_frames(catalog, catalog.configurations[1])
        self.assertEqual(len(frames), 8)
        cut = frames[6]
        self.assertEqual(cut[:6], bytes((0xC1, 2, 1 << 7 | 2 << 4 | 1, 0xFF, 0x5D, 0x5D)))
        self.assertEqual(frames[-1][:6], bytes((0xC2, 2, 2, 4, 3, 0)))
        for frame in frames:
            self.assertEqual(
                int.from_bytes(frame[6:], "big"),
                can_telemetry_schema.crc16_ccitt_false(frame[:6]),
            )
        document = json.loads(configurations.render_frames(catalog))
        self.assertEqual(document["default"], "C00000000000B020")
        self.assertEqual(
            document["configurations"][1]["frames"],
            [frame.hex().upper() for frame in frames],
        )


if __name__ == "__main__":
    unittest.main()
