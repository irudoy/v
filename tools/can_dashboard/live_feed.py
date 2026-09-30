"""Loopback UDP feed of live engineering values for table-cell overlays.

One ASCII datagram carries the values of the latest complete schema-verified
snapshot:

    RRUDP1 rpm=2512.5 bfs_ms=5.81543 timing_deg=24 ...

The first token names the format and its version. Every other token is
``key=value`` with a finite decimal value; a channel without a finite value is
left out of the datagram, and the receiver keeps its previous value. The
receiver is a RomRaider Logger external data source that is configured by the
plugin file this module writes, so both sides share one channel table: the
engine speed of the stock bus, then every telemetry field whose presentation
in the schema declares a feed channel, in profile order.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
import socket

from tools.can_dashboard import PRODUCT_NAME
from tools.logs import can_telemetry

MAGIC = "RRUDP1"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 47809
DATASOURCE_CLASS = "com.romraider.logger.external.udp.plugin.UdpDataSource"
DATASOURCE_NAME = PRODUCT_NAME
# RomRaider keeps its per-user files in this folder of the home directory and
# reads external data source plugin files from its plugins folder.
ROMRAIDER_USER_DIRECTORY = ".RomRaider"
PLUGIN_DIRECTORY = "plugins"
PLUGIN_FILE_NAME = "vq-telemetry.plugin"


@dataclass(frozen=True)
class FeedChannel:
    """One published value and its RomRaider Logger presentation.

    ``source`` is the metric key the model shows, and ``field`` the
    telemetry field of that key, or None for a value of the stock bus that
    the model attribute ``source`` holds.
    """

    key: str
    name: str
    units: str
    format: str
    minimum: float
    maximum: float
    step: float
    source: str
    field: str | None = None

    @property
    def logger_id(self):
        """RomRaider derives an external parameter ID from the item name."""
        return "X_" + self.name.replace(" ", "_")


# Channels of the stock bus, which follow the bus whatever the telemetry
# profile publishes. Engine speed is frame 0x180 at RPM * 8 every 10.24 ms;
# defs/JK08A.can.md states that frame.
STOCK_CHANNELS = (
    FeedChannel(
        "rpm", "VQ Engine Speed", "RPM", "0", 0, 8000, 1000, "stock_rpm"
    ),
)


def feed_channels(profile):
    """The feed channels of one profile of the schema: the stock channels,
    then the fields whose presentation declares a feed channel, in profile
    order, with the display units of their scales."""
    fed = []
    for field in can_telemetry.profile_fields(profile):
        feed = field.get("dashboard", {}).get("feed")
        if feed is None:
            continue
        fed.append(
            FeedChannel(
                feed["key"],
                feed["name"],
                can_telemetry.display_unit(field),
                feed["format"],
                feed["minimum"],
                feed["maximum"],
                feed["step"],
                can_telemetry.engineering_key(field["name"]),
                field["name"],
            )
        )
    return STOCK_CHANNELS + tuple(fed)


@lru_cache(maxsize=None)
def default_channels():
    """The feed channels of the bundled tuning profile."""
    _document, profiles = can_telemetry.load_schema(
        can_telemetry.DEFAULT_SCHEMA
    )
    return feed_channels(profiles["tuning"])


def feed_values(model, channels=None):
    """Return the finite channel values of a schema-verified model; the
    channels default to those of the profile the model decodes."""
    if not model.schema_verified:
        return {}
    if channels is None:
        channels = feed_channels(model.decoder.profile)
    values = {}
    for channel in channels:
        if channel.field is None:
            value = getattr(model, channel.source, None)
        else:
            value = model.value(channel.source)
        if isinstance(value, (int, float)) and math.isfinite(value):
            values[channel.key] = float(value)
    return values


def published_fields(channels=None):
    """Return the telemetry field each channel publishes, by Logger ID.

    A channel that follows the stock bus publishes no telemetry field and is
    left out.
    """
    channels = default_channels() if channels is None else channels
    return {
        channel.logger_id: channel.field
        for channel in channels
        if channel.field is not None
    }


def encode(values):
    """Encode channel values as one datagram; keys follow the channel table."""
    tokens = [MAGIC]
    tokens.extend(f"{key}={value:.7g}" for key, value in values.items())
    return " ".join(tokens).encode("ascii")


def plugin_properties(host=DEFAULT_HOST, port=DEFAULT_PORT, channels=None):
    """Return the RomRaider plugin file that declares the channel table; the
    channels default to those of the bundled tuning profile."""
    channels = default_channels() if channels is None else channels
    lines = [
        f"datasource.class={DATASOURCE_CLASS}",
        f"udp.name={DATASOURCE_NAME}",
        f"udp.host={host}",
        f"udp.port={port}",
    ]
    for index, channel in enumerate(channels, start=1):
        fields = (
            channel.key,
            channel.name,
            channel.units,
            channel.format,
            f"{channel.minimum:g}",
            f"{channel.maximum:g}",
            f"{channel.step:g}",
        )
        lines.append(f"udp.item.{index}=" + "|".join(fields))
    return "\n".join(lines) + "\n"


def plugin_path(home=None):
    """Return the per-user plugin file RomRaider reads at Logger start."""
    home = Path.home() if home is None else Path(home)
    return home / ROMRAIDER_USER_DIRECTORY / PLUGIN_DIRECTORY / PLUGIN_FILE_NAME


def plugin_state(path, host=DEFAULT_HOST, port=DEFAULT_PORT, channels=None):
    """Compare the plugin file with this endpoint and channel table."""
    try:
        text = Path(path).read_text(encoding="ascii")
    except FileNotFoundError:
        return "missing"
    except (OSError, ValueError):
        return "outdated"
    current = plugin_properties(host, port, channels)
    return "current" if text == current else "outdated"


def install_plugin(path, host=DEFAULT_HOST, port=DEFAULT_PORT, channels=None):
    """Write the plugin file, creating its folders; return its path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plugin_properties(host, port, channels), encoding="ascii")
    return path


def parse_endpoint(text):
    """Parse ``PORT`` or ``HOST:PORT``."""
    text = text.strip()
    host, separator, port_text = text.rpartition(":")
    if not separator:
        host = DEFAULT_HOST
    if not host:
        raise ValueError("feed host is empty")
    try:
        port = int(port_text)
    except ValueError as error:
        raise ValueError(f"feed port is not a number: {port_text}") from error
    if not 1 <= port <= 0xFFFF:
        raise ValueError("feed port must be in 1..65535")
    return host, port


class LiveFeed:
    """Send the latest model values to one UDP endpoint."""

    def __init__(self, host, port, sock=None, channels=None):
        self.endpoint = (host, port)
        self.channels = channels
        self.sent = 0
        self.errors = 0
        self.last_error = None
        self._socket = sock or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def publish(self, model):
        """Send one datagram; return whether the model had values to send."""
        if self.channels is None:
            self.channels = feed_channels(model.decoder.profile)
        values = feed_values(model, self.channels)
        if not values:
            return False
        try:
            self._socket.sendto(encode(values), self.endpoint)
        except OSError as error:
            self.errors += 1
            self.last_error = str(error)
            return True
        self.sent += 1
        return True

    def status(self):
        host, port = self.endpoint
        text = f"udp {host}:{port}, {self.sent} sent"
        if self.errors:
            text += f", {self.errors} errors: {self.last_error}"
        return text

    def close(self):
        self._socket.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-plugin",
        type=Path,
        required=True,
        metavar="PATH",
        help="write the RomRaider plugin file, e.g. <RomRaider>/plugins/vq.plugin",
    )
    parser.add_argument(
        "--endpoint",
        default=f"{DEFAULT_HOST}:{DEFAULT_PORT}",
        metavar="[HOST:]PORT",
        help="UDP endpoint the RomRaider plugin listens on",
    )
    args = parser.parse_args(argv)
    try:
        host, port = parse_endpoint(args.endpoint)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.write_plugin.write_text(
        plugin_properties(host, port), encoding="ascii"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
