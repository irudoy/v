import math
from pathlib import Path
import socket
import tempfile
import types
import unittest

from tools.can_dashboard import app, live_feed, model
from tools.logs import can_telemetry

# Stock JK08A ROM16[0x9534], the Base Fuel Schedule at raw load 128.
JK08A_BFS_REFERENCE = 27226


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
            else:
                self.assertIn(channel.source, targets)

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
        load = live_feed.engine_load_percent
        self.assertEqual(load(JK08A_BFS_REFERENCE, JK08A_BFS_REFERENCE), 100.0)
        self.assertEqual(load(0, JK08A_BFS_REFERENCE), 0.0)
        one_code = -(-JK08A_BFS_REFERENCE // 128)
        self.assertEqual(load(one_code, JK08A_BFS_REFERENCE), 0.78125)
        self.assertEqual(load(one_code - 1, JK08A_BFS_REFERENCE), 0.0)

    def test_coordinate_saturates_at_raw_255(self):
        self.assertEqual(
            live_feed.engine_load_percent(0xFFFF, JK08A_BFS_REFERENCE),
            255 * 100 / 128,
        )

    def test_reference_must_fit_the_rom_word(self):
        for value in (0, -1, 0x10000, 27226.0, True):
            with self.assertRaises(ValueError):
                live_feed.validate_bfs_reference(value)
        self.assertEqual(live_feed.validate_bfs_reference(27226), 27226)

    def test_editor_milliseconds_name_the_reference_word(self):
        self.assertEqual(
            live_feed.BFS_RAW_PER_MS
            * can_telemetry.RAW_CALIBRATIONS["bfs_raw"].factor,
            1,
        )
        shown = f"{live_feed.reference_ms(JK08A_BFS_REFERENCE):.3f}"
        self.assertEqual(shown, "13.294")
        self.assertEqual(
            live_feed.reference_from_ms(float(shown)), JK08A_BFS_REFERENCE
        )
        self.assertEqual(live_feed.reference_from_ms(1), 2048)

    def test_milliseconds_outside_the_rom_word_are_rejected(self):
        for value in (0, -1, 32, math.nan, math.inf, True, "13.294", None):
            with self.assertRaises(ValueError):
                live_feed.reference_from_ms(value)


class FeedValuesTest(unittest.TestCase):
    def test_verified_model_yields_engineering_values_and_derived_load(self):
        dashboard = verified_model()
        values = live_feed.feed_values(dashboard, JK08A_BFS_REFERENCE)
        self.assertEqual(
            list(values), [channel.key for channel in live_feed.CHANNELS]
        )
        self.assertEqual(values["rpm"], dashboard.raw["rpm_raw"] * 12.5)
        self.assertEqual(values["coolant_c"], 90)
        self.assertEqual(
            values["load"],
            min(255, dashboard.raw["bfs_raw"] * 128 // JK08A_BFS_REFERENCE)
            * 0.78125,
        )

    def test_load_needs_the_reference_and_the_other_values_do_not(self):
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

    def test_unverified_model_yields_nothing(self):
        dashboard = verified_model()
        dashboard.schema_verified = False
        self.assertEqual(
            live_feed.feed_values(dashboard, JK08A_BFS_REFERENCE), {}
        )

    def test_missing_and_non_finite_values_are_left_out(self):
        dashboard = verified_model()
        dashboard.engineering["rpm"] = math.nan
        del dashboard.engineering["coolant_deg_c"]
        del dashboard.raw["bfs_raw"]
        values = live_feed.feed_values(dashboard, JK08A_BFS_REFERENCE)
        for key in ("rpm", "coolant_c", "load"):
            self.assertNotIn(key, values)
        self.assertIn("iat_c", values)


class EncodingTest(unittest.TestCase):
    def test_datagram_is_magic_and_key_value_tokens(self):
        payload = live_feed.encode({"rpm": 2512.5, "load": 43.75})
        self.assertEqual(payload, b"RRUDP1 rpm=2512.5 load=43.75")

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
        feed = live_feed.LiveFeed(
            "127.0.0.1", receiver.getsockname()[1], JK08A_BFS_REFERENCE
        )
        self.addCleanup(feed.close)
        dashboard = verified_model()

        self.assertTrue(feed.publish(dashboard))

        tokens = receiver.recv(2048).decode("ascii").split(" ")
        self.assertEqual(tokens[0], live_feed.MAGIC)
        received = dict(token.split("=") for token in tokens[1:])
        self.assertEqual(
            float(received["rpm"]), dashboard.raw["rpm_raw"] * 12.5
        )
        self.assertEqual(feed.sent, 1)
        self.assertIn("1 sent", feed.status())
        self.assertNotIn("no load reference", feed.status())

    def test_feed_without_a_reference_runs_and_says_so(self):
        sent = []
        sock = types.SimpleNamespace(
            sendto=lambda payload, endpoint: sent.append(payload),
            close=lambda: None,
        )
        feed = live_feed.LiveFeed("127.0.0.1", 47809, sock=sock)
        self.assertTrue(feed.publish(verified_model()))
        keys = [
            token.split("=")[0]
            for token in sent[0].decode("ascii").split(" ")[1:]
        ]
        self.assertIn("rpm", keys)
        self.assertNotIn(live_feed.LOAD_KEY, keys)
        self.assertIn("no load reference", feed.status())

    def test_unverified_model_sends_nothing(self):
        sent = []
        sock = types.SimpleNamespace(
            sendto=lambda payload, endpoint: sent.append(payload),
            close=lambda: None,
        )
        feed = live_feed.LiveFeed("127.0.0.1", 47809, 27226, sock=sock)
        dashboard = verified_model()
        dashboard.schema_verified = False
        self.assertFalse(feed.publish(dashboard))
        self.assertEqual(sent, [])

    def test_send_failure_is_counted_and_reported(self):
        def fail(payload, endpoint):
            raise OSError("network is down")

        sock = types.SimpleNamespace(sendto=fail, close=lambda: None)
        feed = live_feed.LiveFeed("127.0.0.1", 47809, 27226, sock=sock)
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
        self.assertIsNone(args.bfs_reference)

    def test_reference_accepts_hexadecimal(self):
        args = app.build_parser().parse_args(
            ["--publish-udp", "47809", "--bfs-reference", "0x6A5A"]
        )
        self.assertEqual(args.bfs_reference, JK08A_BFS_REFERENCE)

    def test_invalid_overrides_are_rejected_before_the_window_opens(self):
        for argv in (
            ["--publish-udp", "47809", "--bfs-reference", "0"],
            ["--publish-udp", "0", "--bfs-reference", "27226"],
            ["--publish-udp", "host:"],
            ["--bfs-reference", "65536"],
        ):
            with self.assertRaises(SystemExit):
                app.main(argv)


if __name__ == "__main__":
    unittest.main()
