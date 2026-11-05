import json
from pathlib import Path
import tempfile
import tomllib
import unittest

from patches import can_telemetry_configurations as configurations
from tools.logs import can_telemetry_schema


CAPTURE = Path(configurations.__file__).with_name("can-telemetry-capture.s")
# The slot layouts of the released configuration IDs as (name, width, signed)
# per group. A recorded trace decodes with any later catalog, so a released
# ID keeps its layout for good; a changed layout takes a new ID and a new row.
RELEASED = {
    1: (
        (
            ("rolling_launch_speed_error_raw", 2, True),
            ("rolling_launch_torque_fraction_raw", 2, False),
            ("rolling_launch_cut_counter", 1, False),
            ("ignition_dwell_angle_raw", 1, False),
        ),
    ),
    2: (
        (
            ("rolling_launch_speed_error_raw", 2, True),
            ("rolling_launch_torque_fraction_raw", 2, False),
            ("rolling_launch_cut_counter", 1, False),
            ("ignition_dwell_angle_raw", 1, False),
        ),
        (
            ("rolling_launch_integrator_raw", 2, True),
            ("speed_frame_receive_age_raw", 1, False),
            ("rolling_launch_cut_counter", 1, False),
        ),
    ),
    3: (
        (
            ("rolling_launch_control_error_raw", 2, True),
            ("rolling_launch_law_output_raw", 2, False),
            ("rolling_launch_cut_counter", 1, False),
            ("rolling_launch_mode_trim", 1, False),
        ),
    ),
    4: (
        (
            ("rolling_launch_consumed_q_sum_raw", 4, False),
            ("rolling_launch_cut_counter", 1, False),
            ("rolling_launch_mode_trim", 1, False),
        ),
        (
            ("rolling_launch_cut_fraction_raw", 2, False),
            ("rolling_launch_law_output_raw", 2, False),
            ("rolling_launch_efficiency", 2, False),
        ),
    ),
    5: (
        (
            ("rolling_launch_speed_sample_raw", 2, False),
            ("rolling_launch_selected_target_raw", 2, False),
            ("rolling_launch_status", 1, False),
            ("ignition_dwell_angle_raw", 1, False),
        ),
        (
            ("rolling_launch_rpm_sample_raw", 2, False),
            ("rolling_launch_stock_command_raw", 1, False),
            ("rolling_launch_effective_command_raw", 1, False),
            ("rolling_launch_accepted_button_raw", 1, False),
            ("rolling_launch_speed_age_raw", 1, False),
        ),
    ),
    6: (
        (
            ("rolling_launch_cut_fraction_raw", 2, False),
            ("rolling_launch_cut_counter", 1, False),
            ("rolling_launch_accepted_button_raw", 1, False),
            ("rolling_launch_status", 1, False),
            ("rolling_launch_speed_age_raw", 1, False),
        ),
    ),
}


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
            "rolling_launch_control_error_raw": 0xFFFF6102,
            "rolling_launch_law_output_raw": 0xFFFF6116,
            "rolling_launch_mode_trim": 0xFFFF611E,
            "rolling_launch_consumed_q_sum_raw": 0xFFFF6110,
            "rolling_launch_cut_fraction_raw": 0xFFFF5D5A,
            "rolling_launch_efficiency": 0xFFFF610E,
            "rolling_launch_speed_sample_raw": 0xFFFF6106,
            "rolling_launch_selected_target_raw": 0xFFFF611C,
            "rolling_launch_status": 0xFFFF611F,
            "rolling_launch_rpm_sample_raw": 0xFFFF6104,
            "rolling_launch_stock_command_raw": 0xFFFF6108,
            "rolling_launch_effective_command_raw": 0xFFFF6109,
            "rolling_launch_accepted_button_raw": 0xFFFF6114,
            "rolling_launch_speed_age_raw": 0xFFFF6115,
        })
        self.assertEqual(
            [(item.configuration_id, item.status) for item in catalog.configurations],
            [(1, "historical"), (2, "historical"), (3, "current"), (4, "current"),
             (5, "current"), (6, "current")],
        )

    def test_released_configuration_ids_keep_their_layouts(self):
        catalog = configurations.load_catalog()
        layouts = {
            item.configuration_id: tuple(
                tuple((slot.name, slot.width, slot.signed) for slot in group)
                for group in catalog.group_slots(item)
            )
            for item in catalog.configurations
        }
        for configuration_id, layout in RELEASED.items():
            with self.subTest(configuration_id=configuration_id):
                self.assertEqual(layouts.get(configuration_id), layout)

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
            raw["slot"][3]["width"] = 1

        def unused(raw):
            raw["configuration"][1]["groups"][1].remove("speed_frame_receive_age_raw")

        def state_slot(raw, **changes):
            row = next(row for row in raw["slot"] if row["name"] == "rolling_launch_law_output_raw")
            row.update(changes)

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
            "unknown status": lambda raw: raw["configuration"][2].update(status="retired"),
            "no status": lambda raw: raw["configuration"][2].pop("status"),
            "unknown state field": lambda raw: state_slot(raw, source={"rolling_launch_state": "x"}),
            "state field of another width": lambda raw: state_slot(raw, width=4),
            "state field of another signedness": lambda raw: state_slot(raw, signed=True),
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.load(change)

    def test_frames_encode_slot_group_width_and_address(self):
        catalog = configurations.load_catalog()
        actuation = next(item for item in catalog.configurations if item.configuration_id == 4)
        frames = configurations.configuration_frames(catalog, actuation)
        self.assertEqual(len(frames), 7)
        self.assertEqual(frames[0][:6], bytes((0xC1, 4, 0 << 4 | 4, 0xFF, 0x61, 0x10)))
        self.assertEqual(frames[1][:6], bytes((0xC1, 4, 1 << 4 | 1, 0xFF, 0x5D, 0x5D)))
        self.assertEqual(frames[5][:6], bytes((0xC1, 4, 1 << 7 | 2 << 4 | 2, 0xFF, 0x61, 0x0E)))
        self.assertEqual(frames[-1][:6], bytes((0xC2, 4, 2, 3, 3, 0)))
        for frame in frames:
            self.assertEqual(
                int.from_bytes(frame[6:], "big"),
                can_telemetry_schema.crc16_ccitt_false(frame[:6]),
            )
        document = json.loads(configurations.render_frames(catalog))
        self.assertEqual(document["default"], "C00000000000B020")
        rendered = {row["id"]: row for row in document["configurations"]}
        self.assertEqual(sorted(rendered), [3, 4, 5, 6])
        self.assertEqual(rendered[4]["frames"], [frame.hex().upper() for frame in frames])

    def test_the_schema_keeps_the_historical_configurations(self):
        catalog = configurations.load_catalog()
        entries = configurations.schema_entries(catalog)
        self.assertEqual([row["id"] for row in entries["configurations"]], [1, 2, 3, 4, 5, 6])
        self.assertTrue(all(row.keys() == {"id", "name", "label", "groups"}
                            for row in entries["configurations"]))


if __name__ == "__main__":
    unittest.main()
