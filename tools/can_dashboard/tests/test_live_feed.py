import copy
import math
from pathlib import Path
import socket
import tempfile
import types
import unittest

from tools.can_dashboard import app, live_feed, model
from tools.logs import can_telemetry


def verified_model():
    generator = model.DemoGenerator()
    dashboard = model.DashboardModel("tuning", 0x6F0, 1)
    for tick in range(1, 9):
        timestamp = tick * model.BASE_TICK_SECONDS
        frames = generator.group(tick, timestamp) + generator.stock_context(
            tick, timestamp
        )
        for index, frame in enumerate(frames):
            dashboard.process_frame(frame, now=timestamp + index * 0.00025)
    assert dashboard.schema_verified
    return dashboard


def tuning_profile():
    _document, profiles = can_telemetry.load_schema(
        can_telemetry.DEFAULT_SCHEMA
    )
    return profiles["tuning"]


def schema_calibrations():
    return can_telemetry.calibrations(tuning_profile())


class ChannelTableTest(unittest.TestCase):
    def test_every_source_is_a_declared_engineering_value(self):
        calibrations = schema_calibrations()
        for channel in live_feed.default_channels():
            with self.subTest(channel=channel.key):
                if channel.field is None:
                    self.assertTrue(
                        hasattr(model.DashboardModel(), channel.source)
                    )
                    continue
                self.assertEqual(
                    calibrations[channel.field].target, channel.source
                )

    def test_the_stock_channels_lead_and_fed_fields_follow_in_profile_order(
        self,
    ):
        channels = live_feed.default_channels()
        stock = len(live_feed.STOCK_CHANNELS)
        self.assertEqual(channels[:stock], live_feed.STOCK_CHANNELS)
        self.assertEqual(
            [channel.field for channel in channels[stock:]],
            [
                field["name"]
                for field in can_telemetry.profile_fields(tuning_profile())
                if "feed" in field.get("dashboard", {})
            ],
        )

    def test_a_channel_shows_the_display_unit_of_its_scale(self):
        units = {
            channel.key: channel.units
            for channel in live_feed.default_channels()
        }
        self.assertEqual(units["coolant_c"], "degC")
        self.assertEqual(units["load"], "%")
        self.assertEqual(units["bfs_ms"], "ms")
        self.assertEqual(units["alpha_n_flow_count"], "cnt")

    def test_published_fields_name_the_telemetry_source_of_each_channel(self):
        fields = live_feed.published_fields()
        # Engine speed follows stock frame 0x180, not a telemetry field.
        self.assertNotIn("X_VQ_Engine_Speed", fields)
        self.assertEqual(
            len(fields),
            sum(
                channel.field is not None
                for channel in live_feed.default_channels()
            ),
        )
        self.assertEqual(fields["X_VQ_Engine_Load"], "normalized_load_raw")
        self.assertEqual(
            fields["X_VQ_Throttle_Target"], "throttle_target_channel_0_raw"
        )
        self.assertEqual(fields["X_VQ_QH0_Flow_Potential"], "request_flow_raw")
        self.assertEqual(fields["X_VQ_QH0_Flow_Quantity"], "alpha_n_flow_raw")

    def test_keys_and_logger_ids_are_unique_wire_safe_tokens(self):
        channels = live_feed.default_channels()
        keys = [channel.key for channel in channels]
        ids = [channel.logger_id for channel in channels]
        self.assertEqual(len(set(keys)), len(keys))
        self.assertEqual(len(set(ids)), len(ids))
        for channel in channels:
            self.assertRegex(channel.key, r"^[a-z0-9_]+$")
            self.assertRegex(channel.logger_id, r"^X_[A-Za-z0-9_]+$")
            for text in (channel.name, channel.units, channel.format):
                self.assertNotIn("|", text)

    def test_axis_channels_keep_the_ids_the_definitions_bind(self):
        ids = {
            channel.key: channel.logger_id
            for channel in live_feed.default_channels()
        }
        self.assertEqual(ids["rpm"], "X_VQ_Engine_Speed")
        self.assertEqual(ids["load"], "X_VQ_Engine_Load")
        self.assertEqual(ids["throttle_target_pct"], "X_VQ_Throttle_Target")
        self.assertEqual(ids["request_flow_count"], "X_VQ_QH0_Flow_Potential")
        self.assertEqual(ids["alpha_n_flow_count"], "X_VQ_QH0_Flow_Quantity")

    def test_the_column_coordinate_channels_preserve_stored_counts(self):
        # Word core 00026984 compares the stored points of axis 00014114 with
        # ffff1980, and byte core 00026944 those of axis 00011d4c with
        # ffff1170. The host publishes counts while their physical percent
        # hypotheses lack an independent reference.
        channels = {
            channel.key: channel for channel in live_feed.default_channels()
        }
        calibrations = schema_calibrations()
        for key, field, factor, largest in (
            ("request_flow_count", "request_flow_raw", 1, 65535),
            ("alpha_n_flow_count", "alpha_n_flow_raw", 1, 255),
        ):
            with self.subTest(channel=key):
                calibration = calibrations[field]
                self.assertEqual(channels[key].field, field)
                self.assertEqual(channels[key].source, calibration.target)
                self.assertEqual(calibration.factor, factor)
                self.assertEqual(calibration.apply(0), channels[key].minimum)
                self.assertLessEqual(
                    calibration.apply(largest), channels[key].maximum
                )
                self.assertEqual(channels[key].units, "cnt")

    def test_the_throttle_target_channel_carries_the_axis_scale(self):
        # Overlay Log compares the published value with the stored points of
        # opening coordinate table 000155a0, whose code scale is the gradient
        # that FUN 0006f236 applies before J1979 publishes the byte as percent.
        target = next(
            channel
            for channel in live_feed.default_channels()
            if channel.key == "throttle_target_pct"
        )
        calibration = schema_calibrations()["throttle_target_channel_0_raw"]
        self.assertEqual(target.source, calibration.target)
        self.assertEqual(calibration.factor, 0x505B / 65536 / 4 * 100 / 255)
        self.assertEqual(calibration.apply(0), 0.0)
        # The stored points span 0..3172 counts, the range the channel declares.
        self.assertLessEqual(calibration.apply(3172), target.maximum)

    def test_a_profile_without_feed_channels_keeps_the_stock_channels(self):
        profile = copy.deepcopy(tuning_profile())
        for field in can_telemetry.profile_fields(profile):
            field.get("dashboard", {}).pop("feed", None)
        self.assertEqual(
            live_feed.feed_channels(profile), live_feed.STOCK_CHANNELS
        )


class EngineLoadTest(unittest.TestCase):
    def test_load_is_the_normalized_load_the_ecu_computes(self):
        sources = {
            channel.key: channel.source
            for channel in live_feed.default_channels()
        }
        calibration = schema_calibrations()["normalized_load_raw"]
        self.assertEqual(sources["load"], calibration.target)
        # Raw 128 is the reference schedule, and one code is 0.78125 percent.
        self.assertEqual(calibration.apply(128), 100.0)
        self.assertEqual(calibration.apply(1), 0.78125)

    def test_saturated_load_fits_the_logger_range(self):
        load = next(
            channel
            for channel in live_feed.default_channels()
            if channel.key == "load"
        )
        calibration = schema_calibrations()["normalized_load_raw"]
        self.assertEqual(calibration.apply(0), load.minimum)
        self.assertLessEqual(calibration.apply(255), load.maximum)


class FeedValuesTest(unittest.TestCase):
    def test_verified_model_yields_the_engineering_values(self):
        dashboard = verified_model()
        values = live_feed.feed_values(dashboard)
        self.assertEqual(
            list(values),
            [channel.key for channel in live_feed.default_channels()],
        )
        self.assertEqual(values["rpm"], dashboard.stock_rpm)
        self.assertEqual(
            values["load"], dashboard.raw["normalized_load_raw"] * 100 / 128
        )
        self.assertEqual(values["coolant_c"], 90)
        self.assertEqual(values["bfs_ms"], dashboard.raw["bfs_raw"] / 2048)

    def test_unverified_model_yields_nothing(self):
        dashboard = verified_model()
        dashboard.schema_verified = False
        self.assertEqual(live_feed.feed_values(dashboard), {})

    def test_missing_and_non_finite_values_are_left_out(self):
        dashboard = verified_model()
        dashboard.stock_rpm = math.nan
        del dashboard.engineering["coolant"]
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
            float(received["rpm"]), dashboard.stock_rpm
        )
        self.assertEqual(
            round(float(received["bfs_ms"]) * 2048), dashboard.raw["bfs_raw"]
        )
        self.assertEqual(
            float(received["load"]),
            float(f"{dashboard.raw['normalized_load_raw'] * 100 / 128:.7g}"),
        )
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
        channels = live_feed.default_channels()
        items = [
            properties[f"udp.item.{index}"].split("|")
            for index in range(1, len(channels) + 1)
        ]
        self.assertNotIn(f"udp.item.{len(channels) + 1}", properties)
        self.assertEqual(
            [item[0] for item in items],
            [channel.key for channel in channels],
        )
        self.assertEqual(
            items[0], ["rpm", "VQ Engine Speed", "RPM", "0", "0", "8000", "1000"]
        )
        self.assertTrue(all(len(item) == 7 for item in items))

    def test_every_item_is_a_value_the_datagram_carries(self):
        lines = live_feed.plugin_properties().splitlines()
        derived = [
            line
            for line in lines
            if line.startswith("udp.item.")
            and line.split("=", 1)[0].count(".") > 2
        ]
        self.assertEqual(derived, [])
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
