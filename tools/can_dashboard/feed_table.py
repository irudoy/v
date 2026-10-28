#!/usr/bin/env python3
"""Render the feed channel table of the dashboard README.

The table follows the channel table that the live feed publishes for the
bundled tuning profile: the stock channels with the description of their
metric, then every field whose presentation declares a feed channel with the
scale of that field in the schema.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import descriptions
from tools.can_dashboard import live_feed
from tools.logs import can_telemetry


DEFAULT_README = Path(__file__).with_name("README.md")
# The marked section of the README that holds the feed channel table.
SECTION = "feed-channels"
GENERATE_COMMAND = "uv run python tools/can_dashboard/feed_table.py"


def render(schema=can_telemetry.DEFAULT_SCHEMA):
    """Render the feed channel table of the tuning profile of a schema."""
    _document, profiles = can_telemetry.load_schema(schema)
    profile = profiles["tuning"]
    fields = {
        field["name"]: field for field in can_telemetry.profile_fields(profile)
    }
    lines = [
        "",
        "| Key | RomRaider Logger ID | Units | Source |",
        "| --- | --- | --- | --- |",
    ]
    for channel in live_feed.feed_channels(profile):
        if channel.field is None:
            description = descriptions.describe(channel.source)
            if not description:
                raise ValueError(
                    f"stock feed channel {channel.key}: metric "
                    f"{channel.source} has no description"
                )
            source = f"stock metric `{channel.source}`: {description}"
        else:
            source = f"`{channel.field}` at `{fields[channel.field]['scale']}`"
        lines.append(
            f"| `{channel.key}` | `{channel.logger_id}` | {channel.units} "
            f"| {source} |"
        )
    lines.append("")
    return "\n".join(lines)


def readme_text(text, schema=can_telemetry.DEFAULT_SCHEMA):
    """Return `text` with its marked feed channel section rendered."""
    begin, end = f"<!-- {SECTION}:begin -->", f"<!-- {SECTION}:end -->"
    start, stop = text.find(begin), text.find(end)
    if start < 0 or stop < start:
        raise ValueError(f"the README has no markers {begin} {end}")
    start += len(begin)
    return text[:start] + render(schema) + text[stop:]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument(
        "--schema", type=Path, default=can_telemetry.DEFAULT_SCHEMA
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = args.readme.read_text(encoding="utf-8")
    try:
        rendered = readme_text(text, args.schema)
    except (ValueError, can_telemetry.DecodeError) as error:
        raise SystemExit(f"{args.readme}: {error}") from error
    if rendered != text:
        if args.check:
            raise SystemExit(
                f"{args.readme}: the {SECTION} section is stale; "
                f"regenerate it with {GENERATE_COMMAND}"
            )
        args.readme.write_text(rendered, encoding="utf-8")
    print(f"status=PASS section={SECTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
