"""The feed channel table of the README follows the published channels."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools.can_dashboard import descriptions, feed_table, live_feed


BEGIN = f"<!-- {feed_table.SECTION}:begin -->"
END = f"<!-- {feed_table.SECTION}:end -->"


def run(*argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return feed_table.main(list(argv))


class FeedTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = feed_table.DEFAULT_README.read_text(encoding="utf-8")
        head, rest = cls.text.split(BEGIN)
        cls.section, tail = rest.split(END)
        cls.head, cls.tail = head + BEGIN, END + tail

    def write(self, directory, section):
        path = Path(directory) / "README.md"
        path.write_text(self.head + section + self.tail, encoding="utf-8")
        return path

    def test_the_readme_holds_the_rendered_table(self):
        self.assertEqual(feed_table.readme_text(self.text), self.text)
        self.assertEqual(run("--check"), 0)

    def test_every_channel_has_one_row_with_its_source(self):
        rows = feed_table.render().splitlines()
        channels = live_feed.default_channels()
        self.assertEqual(
            [row.split(" | ")[0] for row in rows if row.startswith("| `")],
            [f"| `{channel.key}`" for channel in channels],
        )
        for channel in channels:
            with self.subTest(key=channel.key):
                (row,) = [row for row in rows if row.startswith(f"| `{channel.key}` |")]
                self.assertIn(f"| `{channel.logger_id}` | {channel.units} |", row)
                if channel.field is None:
                    self.assertIn(descriptions.describe(channel.source), row)
                else:
                    self.assertIn(f"`{channel.field}` at `", row)

    def test_a_stale_or_edited_row_fails_the_check(self):
        rows = self.section.splitlines()
        (load,) = [row for row in rows if row.startswith("| `load` |")]
        drifts = {
            "edited scale": self.section.replace(
                load, load.replace("/ 128", "/ 127")
            ),
            "removed channel": self.section.replace(
                "| `battery_v` |", "| `removed_v` |"
            ),
            "missing channel": self.section.replace(load + "\n", ""),
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, section in drifts.items():
                with self.subTest(drift=name):
                    self.assertNotEqual(section, self.section)
                    path = self.write(directory, section)
                    with self.assertRaisesRegex(
                        SystemExit, feed_table.GENERATE_COMMAND
                    ):
                        run("--check", "--readme", str(path))
                    self.assertEqual(run("--readme", str(path)), 0)
                    self.assertEqual(
                        path.read_text(encoding="utf-8"), self.text
                    )

    def test_missing_markers_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text(self.text.replace(BEGIN, ""), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "no markers"):
                run("--check", "--readme", str(path))

    def test_a_stock_channel_needs_the_description_of_its_metric(self):
        with mock.patch.object(descriptions, "DESCRIPTIONS", {}):
            with self.assertRaisesRegex(ValueError, "has no description"):
                feed_table.render()


if __name__ == "__main__":
    unittest.main()
