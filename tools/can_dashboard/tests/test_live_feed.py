import math
from pathlib import Path
import socket
import tempfile
import types
import unittest
import xml.etree.ElementTree as ElementTree

from tools.can_dashboard import app, live_feed, model
from tools.logs import can_telemetry

DEFINITIONS = Path(__file__).resolve().parents[3] / "defs"
# Stock JK08A ROM16[0x9534], the Base Fuel Schedule at raw load 128.
JK08A_BFS_REFERENCE = 27226


def romraider_load(bfs_raw, reference):
    """Evaluate the plugin-file expression as RomRaider does.

    The datagram carries the schedule as text with seven significant digits,
    and the table variable holds the ROM word.
    """
    names = {
        "bfs_ms": float(f"{bfs_raw / 2048:.7g}"),
        "reference": float(reference),
        "floor": math.floor,
        "round": lambda value: math.floor(value + 0.5),
        "min": min,
    }
    return eval(live_feed.LOAD_EXPRESSION, {"__builtins__": {}}, names)


def verified_model():
    generator = model.DemoGenerator()
    dashboard = model.DashboardModel("tuning", 0x6F0, 1)
    for tick in range(1, 9):
        timestamp = tick * model.BASE_TICK_SECONDS
        for index, frame in enumerate(generator.group(tick, timestamp)):
            dashboard.process_frame(frame, now=timestamp + index * 0.00025)
    assert dashboard.schema_verified
    return dashboard


class ChannelTableTest(unittest.TestCase):
    def test_every_source_is_a_declared_engineering_value(self):
        targets = {
            calibration.target
            for table in (
                can_telemetry.RAW_CALIBRATIONS,
                model.DASHBOARD_CALIBRATIONS,
            )
            for calibration in table.values()
        }
        for channel in live_feed.CHANNELS:
            if channel.key == live_feed.LOAD_KEY:
                self.assertIsNone(channel.source)
                self.assertEqual(
                    channel.expression, live_feed.LOAD_EXPRESSION
                )
                self.assertEqual(
                    channel.tables,
                    (("reference", live_feed.LOAD_REFERENCE_TABLE),),
                )
            else:
                self.assertIn(channel.source, targets)
                self.assertIsNone(channel.expression)
                self.assertEqual(channel.tables, ())

    def test_keys_and_logger_ids_are_unique_wire_safe_tokens(self):
        keys = [channel.key for channel in live_feed.CHANNELS]
        ids = [channel.logger_id for channel in live_feed.CHANNELS]
        self.assertEqual(len(set(keys)), len(keys))
        self.assertEqual(len(set(ids)), len(ids))
        for channel in live_feed.CHANNELS:
            self.assertRegex(channel.key, r"^[a-z0-9_]+$")
            self.assertRegex(channel.logger_id, r"^X_[A-Za-z0-9_]+$")
            for text in (channel.name, channel.units, channel.format):
                self.assertNotIn("|", text)

    def test_axis_channels_keep_the_ids_the_definitions_bind(self):
        ids = {channel.key: channel.logger_id for channel in live_feed.CHANNELS}
        self.assertEqual(ids["rpm"], "X_VQ_Engine_Speed")
        self.assertEqual(ids["load"], "X_VQ_Engine_Load")


class EngineLoadTest(unittest.TestCase):
    def test_reference_is_raw_128_and_one_code_is_0_78125_percent(self):
        load = romraider_load
        self.assertEqual(load(JK08A_BFS_REFERENCE, JK08A_BFS_REFERENCE), 100.0)
        self.assertEqual(load(0, JK08A_BFS_REFERENCE), 0.0)
        one_code = -(-JK08A_BFS_REFERENCE // 128)
        self.assertEqual(load(one_code, JK08A_BFS_REFERENCE), 0.78125)
        self.assertEqual(load(one_code - 1, JK08A_BFS_REFERENCE), 0.0)

    def test_coordinate_saturates_at_raw_255(self):
        self.assertEqual(
            romraider_load(0xFFFF, JK08A_BFS_REFERENCE), 255 * 100 / 128
        )

    def test_expression_is_the_integer_arithmetic_of_the_ecu(self):
        for reference in (JK08A_BFS_REFERENCE, 1, 12345, 0xFFFF):
            changed = [
                bfs_raw
                for bfs_raw in range(0x10000)
                if romraider_load(bfs_raw, reference)
                != min(255, bfs_raw * 128 // reference) * 100 / 128
            ]
            self.assertEqual(changed, [], reference)

    def test_expression_reads_the_schedule_the_datagram_carries(self):
        sources = {channel.key: channel.source for channel in live_feed.CHANNELS}
        self.assertEqual(sources["bfs_ms"], "bfs_ms")
        calibration = can_telemetry.RAW_CALIBRATIONS["bfs_raw"]
        self.assertEqual(calibration.target, "bfs_ms")
        self.assertEqual(calibration.factor * 2048, 1)
        self.assertIn("bfs_ms*2048", live_feed.LOAD_EXPRESSION)

    def test_definitions_hold_the_reference_word_under_the_table_name(self):
        bound = 0
        for path in sorted(DEFINITIONS.glob("*.xml")):
            tables = list(ElementTree.parse(path).getroot().iter("table"))
            ids = {channel.logger_id for channel in live_feed.CHANNELS}
            if not any(table.get("logparam") in ids for table in tables):
                continue
            bound += 1
            references = [
                table
                for table in tables
                if table.get("name") == live_feed.LOAD_REFERENCE_TABLE
            ]
            with self.subTest(definition=path.name):
                self.assertEqual(len(references), 1)
                reference = references[0]
                self.assertEqual(reference.get("storagetype"), "uint16")
                self.assertEqual(reference.get("endian"), "big")
                self.assertEqual(reference.get("sizex"), "1")
                self.assertEqual(
                    reference.find("scaling").get("expression"), "x/2048"
                )
        self.assertGreater(bound, 0)


class FeedValuesTest(unittest.TestCase):
    def test_verified_model_yields_the_engineering_values(self):
        dashboard = verified_model()
        values = live_feed.feed_values(dashboard)
        self.assertEqual(
            list(values),
            [
                channel.key
                for channel in live_feed.CHANNELS
                if channel.key != live_feed.LOAD_KEY
            ],
        )
        self.assertEqual(values["rpm"], dashboard.raw["rpm_raw"] * 12.5)
        self.assertEqual(values["coolant_c"], 90)
        self.assertEqual(values["bfs_ms"], dashboard.raw["bfs_raw"] / 2048)

    def test_unverified_model_yields_nothing(self):
        dashboard = verified_model()
        dashboard.schema_verified = False
        self.assertEqual(live_feed.feed_values(dashboard), {})

    def test_missing_and_non_finite_values_are_left_out(self):
        dashboard = verified_model()
        dashboard.engineering["rpm"] = math.nan
        del dashboard.engineering["coolant_deg_c"]
        values = live_feed.feed_values(dashboard)
        for key in ("rpm", "coolant_c"):
            self.assertNotIn(key, values)
        self.assertIn("iat_c", values)


class EncodingTest(unittest.TestCase):
    def test_datagram_is_magic_and_key_value_tokens(self):
        payload = live_feed.encode({"rpm": 2512.5, "bfs_ms": 5.8125})
        self.assertEqual(payload, b"RRUDP1 rpm=2512.5 bfs_ms=5.8125")

    def test_values_keep_seven_significant_digits(self):
        payload = live_feed.encode({"bfs_ms": 1 / 3, "rpm": 12750.0})
        self.assertEqual(payload, b"RRUDP1 bfs_ms=0.3333333 rpm=12750")


class EndpointTest(unittest.TestCase):
    def test_port_alone_selects_loopback(self):
        self.assertEqual(
            live_feed.parse_endpoint("47809"), ("127.0.0.1", 47809)
        )
        self.assertEqual(
            live_feed.parse_endpoint("192.168.1.20:5000"),
            ("192.168.1.20", 5000),
        )

    def test_invalid_endpoints_are_rejected(self):
        for text in ("", "port", "0", "65536", ":47809", "host:"):
            with self.assertRaises(ValueError):
                live_feed.parse_endpoint(text)


class LiveFeedTest(unittest.TestCase):
    def test_publish_delivers_one_datagram_over_loopback(self):
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(receiver.close)
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(2.0)
        feed = live_feed.LiveFeed("127.0.0.1", receiver.getsockname()[1])
        self.addCleanup(feed.close)
        dashboard = verified_model()

        self.assertTrue(feed.publish(dashboard))

        tokens = receiver.recv(2048).decode("ascii").split(" ")
        self.assertEqual(tokens[0], live_feed.MAGIC)
        received = dict(token.split("=") for token in tokens[1:])
        self.assertEqual(
            float(received["rpm"]), dashboard.raw["rpm_raw"] * 12.5
        )
        self.assertEqual(
            round(float(received["bfs_ms"]) * 2048), dashboard.raw["bfs_raw"]
        )
        self.assertNotIn(live_feed.LOAD_KEY, received)
        self.assertEqual(feed.sent, 1)
        self.assertEqual(
            feed.status(), f"udp 127.0.0.1:{receiver.getsockname()[1]}, 1 sent"
        )

    def test_unverified_model_sends_nothing(self):
        sent = []
        sock = types.SimpleNamespace(
            sendto=lambda payload, endpoint: sent.append(payload),
            close=lambda: None,
        )
        feed = live_feed.LiveFeed("127.0.0.1", 47809, sock=sock)
        dashboard = verified_model()
        dashboard.schema_verified = False
        self.assertFalse(feed.publish(dashboard))
        self.assertEqual(sent, [])

    def test_send_failure_is_counted_and_reported(self):
        def fail(payload, endpoint):
            raise OSError("network is down")

        sock = types.SimpleNamespace(sendto=fail, close=lambda: None)
        feed = live_feed.LiveFeed("127.0.0.1", 47809, sock=sock)
        self.assertTrue(feed.publish(verified_model()))
        self.assertEqual((feed.sent, feed.errors), (0, 1))
        self.assertIn("1 errors: network is down", feed.status())


class PluginFileTest(unittest.TestCase):
    def test_plugin_file_declares_class_endpoint_and_every_channel(self):
        text = live_feed.plugin_properties("127.0.0.1", 47809)
        properties = dict(
            line.split("=", 1) for line in text.splitlines()
        )
        self.assertEqual(
            properties["datasource.class"], live_feed.DATASOURCE_CLASS
        )
        self.assertEqual(properties["udp.port"], "47809")
        items = [
            properties[f"udp.item.{index}"].split("|")
            for index in range(1, len(live_feed.CHANNELS) + 1)
        ]
        self.assertEqual(
            [item[0] for item in items],
            [channel.key for channel in live_feed.CHANNELS],
        )
        self.assertEqual(
            items[0], ["rpm", "VQ Engine Speed", "RPM", "0", "0", "8000", "1000"]
        )
        self.assertTrue(all(len(item) == 7 for item in items))

    def test_plugin_file_derives_the_load_from_the_open_rom(self):
        lines = live_feed.plugin_properties().splitlines()
        index = 1 + [channel.key for channel in live_feed.CHANNELS].index(
            live_feed.LOAD_KEY
        )
        derived = [
            line for line in lines if line.startswith(f"udp.item.{index}.")
        ]
        self.assertEqual(
            derived,
            [
                f"udp.item.{index}.expression="
                "min(255, floor(round(bfs_ms*2048)*128/reference))*100/128",
                f"udp.item.{index}.table.reference="
                "Internal Load Normalization Reference",
            ],
        )
        others = [
            line
            for line in lines
            if line.startswith("udp.item.")
            and line.split("=", 1)[0].count(".") > 2
            and line not in derived
        ]
        self.assertEqual(others, [])
        for line in lines:
            self.assertNotIn("\\", line)
            self.assertEqual(line, line.strip())

    def test_the_plugin_file_lives_in_the_per_user_romraider_folder(self):
        self.assertEqual(
            live_feed.plugin_path("/home/tuner"),
            Path("/home/tuner/.RomRaider/plugins/vq-telemetry.plugin"),
        )
        self.assertEqual(
            live_feed.plugin_path(), live_feed.plugin_path(Path.home())
        )

    def test_install_creates_the_folders_and_tracks_the_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = live_feed.plugin_path(directory)
            self.assertEqual(live_feed.plugin_state(path), "missing")
            for _attempt in range(2):
                self.assertEqual(
                    live_feed.install_plugin(path, "127.0.0.1", 5000), path
                )
                self.assertEqual(
                    path.read_text(encoding="ascii"),
                    live_feed.plugin_properties("127.0.0.1", 5000),
                )
            self.assertEqual(
                live_feed.plugin_state(path, "127.0.0.1", 5000), "current"
            )
            self.assertEqual(live_feed.plugin_state(path), "outdated")
            path.write_bytes(b"\xff\xfe")
            self.assertEqual(
                live_feed.plugin_state(path, "127.0.0.1", 5000), "outdated"
            )

    def test_cli_writes_the_plugin_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vq.plugin"
            self.assertEqual(
                live_feed.main(
                    ["--write-plugin", str(path), "--endpoint", "5000"]
                ),
                0,
            )
            self.assertEqual(
                path.read_text(encoding="ascii"),
                live_feed.plugin_properties("127.0.0.1", 5000),
            )


class DashboardArgumentsTest(unittest.TestCase):
    def test_feed_is_off_by_default(self):
        args = app.build_parser().parse_args([])
        self.assertIsNone(args.publish_udp)

    def test_the_load_reference_is_not_an_argument(self):
        with self.assertRaises(SystemExit):
            app.build_parser().parse_args(["--bfs-reference", "27226"])

    def test_invalid_overrides_are_rejected_before_the_window_opens(self):
        for argv in (
            ["--publish-udp", "0"],
            ["--publish-udp", "host:"],
        ):
            with self.assertRaises(SystemExit):
                app.main(argv)


if __name__ == "__main__":
    unittest.main()
