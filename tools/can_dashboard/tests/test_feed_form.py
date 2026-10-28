import unittest

from tools.can_dashboard import live_feed, settings
from tools.can_dashboard.settings import FeedSettings


class FormTest(unittest.TestCase):
    def test_the_form_builds_feed_settings(self):
        self.assertEqual(
            settings.parse_feed_form(True, " 127.0.0.1:5000 "),
            FeedSettings(True, "127.0.0.1", 5000),
        )
        self.assertEqual(
            settings.parse_feed_form(False, "47809"),
            FeedSettings(False, live_feed.DEFAULT_HOST, 47809),
        )

    def test_the_form_rejects_an_invalid_endpoint(self):
        for endpoint in ("", "host:", ":5000", "0", "70000", "host:port"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    settings.parse_feed_form(True, endpoint)

    def test_the_default_endpoint_round_trips(self):
        defaults = FeedSettings()
        self.assertEqual(
            settings.parse_feed_form(
                False,
                settings.endpoint_text(defaults.host, defaults.port),
            ),
            defaults,
        )
