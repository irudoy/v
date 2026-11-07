import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools.can_dashboard import settings


CATALOG = ("rpm", "speed", "load", "gear", "stft_b1")
DEFAULT_HERO = ("rpm", "speed", "load")


def load(path):
    return settings.load(path, catalog=CATALOG, default_hero=DEFAULT_HERO)


class DefaultPathTest(unittest.TestCase):
    def test_macos_uses_application_support(self):
        path = settings.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="darwin",
            environ={"HOME": "/Users/operator"},
        )
        self.assertEqual(
            path,
            Path(
                "/Users/operator/Library/Application Support/"
                "VQ CAN Telemetry/settings.json"
            ),
        )

    def test_windows_uses_the_roaming_profile(self):
        path = settings.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="win32",
            environ={"HOME": "/home/operator", "APPDATA": "/profile/Roaming"},
        )
        self.assertEqual(
            path,
            Path("/profile/Roaming/VQ CAN Telemetry/settings.json"),
        )

    def test_windows_without_appdata_falls_back_to_the_home_profile(self):
        path = settings.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="win32",
            environ={"HOME": "/home/operator"},
        )
        self.assertEqual(
            path,
            Path("/home/operator/AppData/Roaming/VQ CAN Telemetry/settings.json"),
        )

    def test_other_platforms_follow_the_xdg_directory(self):
        explicit = settings.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="linux",
            environ={"HOME": "/home/operator", "XDG_CONFIG_HOME": "/cfg"},
        )
        implicit = settings.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="linux",
            environ={"HOME": "/home/operator"},
        )
        self.assertEqual(explicit, Path("/cfg/vq-can-telemetry/settings.json"))
        self.assertEqual(
            implicit,
            Path("/home/operator/.config/vq-can-telemetry/settings.json"),
        )


class NormalizeTest(unittest.TestCase):
    def test_hero_keys_keep_their_order_once_each(self):
        self.assertEqual(
            settings.normalize_hero(
                ["gear", "rpm", "gear", "unknown", 7, "load"],
                CATALOG,
            ),
            ("gear", "rpm", "load"),
        )

    def test_hero_keys_stop_at_the_limit(self):
        self.assertEqual(
            settings.normalize_hero(CATALOG, CATALOG, limit=2),
            ("rpm", "speed"),
        )

    def test_documents_of_any_shape_give_the_defaults(self):
        for document in (None, [], "dark", 4, {"theme": 1, "hero": "rpm"}):
            with self.subTest(document=document):
                self.assertEqual(
                    settings.normalize(
                        document,
                        catalog=CATALOG,
                        default_hero=DEFAULT_HERO,
                    ),
                    settings.Settings("dark", DEFAULT_HERO),
                )

    def test_an_empty_hero_list_is_a_choice_and_stays_empty(self):
        self.assertEqual(
            settings.normalize(
                {"theme": "light", "hero": []},
                catalog=CATALOG,
                default_hero=DEFAULT_HERO,
            ),
            settings.Settings("light", ()),
        )

    def test_an_unknown_theme_falls_back_to_dark(self):
        result = settings.normalize(
            {"theme": "sepia", "hero": ["load"]},
            catalog=CATALOG,
            default_hero=DEFAULT_HERO,
        )
        self.assertEqual(result, settings.Settings("dark", ("load",)))

    def test_the_timer_bar_is_hidden_unless_stored_as_shown(self):
        self.assertFalse(settings.Settings().timer)
        for stored, shown in ((True, True), (False, False), ("yes", False),
                              (1, False), (None, False)):
            with self.subTest(stored=stored):
                result = settings.normalize(
                    {"timer": stored},
                    catalog=CATALOG,
                    default_hero=DEFAULT_HERO,
                )
                self.assertIs(result.timer, shown)

    def test_the_restart_resend_is_on_unless_stored_as_off(self):
        self.assertTrue(settings.Settings().page_resend)
        for stored, enabled in ((True, True), (False, False), ("no", True),
                                (0, True), (None, True)):
            with self.subTest(stored=stored):
                result = settings.normalize(
                    {"page_resend": stored},
                    catalog=CATALOG,
                    default_hero=DEFAULT_HERO,
                )
                self.assertIs(result.page_resend, enabled)

    def test_the_feed_is_off_on_loopback_by_default(self):
        self.assertEqual(
            settings.FeedSettings(),
            settings.FeedSettings(False, "127.0.0.1", 47809),
        )
        for document in (None, [], "on", 1, {}):
            with self.subTest(document=document):
                self.assertEqual(
                    settings.normalize_feed(document),
                    settings.FeedSettings(),
                )

    def test_a_stored_feed_is_kept(self):
        self.assertEqual(
            settings.normalize_feed(
                {
                    "enabled": True,
                    "host": " 192.168.1.20 ",
                    "port": 5000,
                }
            ),
            settings.FeedSettings(True, "192.168.1.20", 5000),
        )

    def test_a_field_the_feed_does_not_have_is_dropped(self):
        self.assertEqual(
            settings.normalize_feed(
                {"enabled": True, "port": 5000, "bfs_reference": 27226}
            ),
            settings.FeedSettings(True, "127.0.0.1", 5000),
        )

    def test_invalid_feed_fields_fall_back_one_by_one(self):
        self.assertEqual(
            settings.normalize_feed(
                {
                    "enabled": "yes",
                    "host": "  ",
                    "port": 70000,
                }
            ),
            settings.FeedSettings(),
        )
        self.assertEqual(
            settings.normalize_feed({"enabled": True, "port": "47809"}),
            settings.FeedSettings(True, "127.0.0.1", 47809),
        )


class FileTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def test_a_missing_file_gives_the_defaults(self):
        self.assertEqual(
            load(self.directory / "absent.json"),
            settings.Settings("dark", DEFAULT_HERO),
        )

    def test_no_path_gives_the_defaults(self):
        self.assertEqual(load(None), settings.Settings("dark", DEFAULT_HERO))

    def test_a_damaged_file_gives_the_defaults(self):
        path = self.directory / "settings.json"
        path.write_text("{ not json", encoding="utf-8")
        self.assertEqual(load(path), settings.Settings("dark", DEFAULT_HERO))

    def test_saved_settings_load_back(self):
        path = self.directory / "nested" / "settings.json"
        chosen = settings.Settings(
            "light",
            ("gear", "rpm"),
            settings.FeedSettings(True, "127.0.0.1", 5000),
            timer=True,
            page_resend=False,
        )

        self.assertEqual(settings.save(path, chosen), path)

        self.assertEqual(load(path), chosen)
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            document,
            {
                "version": settings.SETTINGS_VERSION,
                "theme": "light",
                "hero": ["gear", "rpm"],
                "feed": {
                    "enabled": True,
                    "host": "127.0.0.1",
                    "port": 5000,
                },
                "timer": True,
                "page_resend": False,
            },
        )

    def test_saving_leaves_no_temporary_file(self):
        path = self.directory / "settings.json"
        settings.save(path, settings.Settings("dark", ("rpm",)))
        settings.save(path, settings.Settings("light", ()))
        self.assertEqual(
            sorted(item.name for item in self.directory.iterdir()),
            ["settings.json"],
        )

    def test_a_failed_write_keeps_the_previous_file(self):
        path = self.directory / "settings.json"
        previous = settings.Settings("light", ("rpm",))
        settings.save(path, previous)

        with mock.patch.object(
            settings.os,
            "replace",
            side_effect=OSError("disk full"),
        ):
            with self.assertRaises(OSError):
                settings.save(path, settings.Settings("dark", ("gear",)))

        self.assertEqual(load(path), previous)
        self.assertEqual(
            sorted(item.name for item in self.directory.iterdir()),
            ["settings.json"],
        )


if __name__ == "__main__":
    unittest.main()
