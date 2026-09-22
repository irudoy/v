"""Loopback UDP feed of live engineering values for table-cell overlays.

One ASCII datagram carries the values of the latest complete schema-verified
snapshot:

    RRUDP1 rpm=2512.5 bfs_ms=5.81543 timing_deg=24 ...

The first token names the format and its version. Every other token is
``key=value`` with a finite decimal value; a channel without a finite value is
left out of the datagram, and the receiver keeps its previous value. The
receiver is a RomRaider Logger external data source that is configured by the
plugin file this module writes, so both sides share one channel table.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import socket

from tools.can_dashboard import PRODUCT_NAME

MAGIC = "RRUDP1"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 47809
DATASOURCE_CLASS = "com.romraider.logger.external.udp.plugin.UdpDataSource"
DATASOURCE_NAME = PRODUCT_NAME
LOAD_KEY = "load"
# RomRaider keeps its per-user files in this folder of the home directory and
# reads external data source plugin files from its plugins folder.
ROMRAIDER_USER_DIRECTORY = ".RomRaider"
PLUGIN_DIRECTORY = "plugins"
PLUGIN_FILE_NAME = "vq-telemetry.plugin"


@dataclass(frozen=True)
class FeedChannel:
    """One published value and its RomRaider Logger presentation."""

    key: str
    name: str
    units: str
    format: str
    minimum: float
    maximum: float
    step: float
    source: str

    @property
    def logger_id(self):
        """RomRaider derives an external parameter ID from the item name."""
        return "X_" + self.name.replace(" ", "_")


CHANNELS = (
    FeedChannel("rpm", "VQ Engine Speed", "RPM", "0", 0, 8000, 1000, "rpm"),
    FeedChannel(
        LOAD_KEY,
        "VQ Engine Load",
        "%",
        "0.00",
        0,
        200,
        20,
        "normalized_load_percent",
    ),
    FeedChannel(
        "bfs_ms", "VQ Base Fuel Schedule", "ms", "0.000", 0, 20, 2, "bfs_ms"
    ),
    FeedChannel(
        "timing_deg",
        "VQ Timing Command",
        "degBTDC",
        "0",
        -20,
        60,
        10,
        "timing_command_deg",
    ),
    FeedChannel(
        "maf_g_s", "VQ Total Airflow", "g/s", "0.00", 0, 400, 50, "maf_total_g_s"
    ),
    FeedChannel(
        "throttle_pct",
        "VQ Absolute Throttle",
        "%",
        "0.0",
        0,
        100,
        10,
        "absolute_throttle_percent",
    ),
    FeedChannel(
        "coolant_c", "VQ Coolant Temperature", "C", "0", -40, 140, 20,
        "coolant_deg_c",
    ),
    FeedChannel(
        "iat_c", "VQ Intake Air Temperature", "C", "0", -40, 140, 20,
        "iat_deg_c",
    ),
    FeedChannel(
        "intake_cam_b1_deg",
        "VQ Intake Cam B1",
        "degCA",
        "0.0",
        -64,
        64,
        16,
        "intake_cvtc_actual_b1_deg_ca",
    ),
    FeedChannel(
        "intake_cam_b2_deg",
        "VQ Intake Cam B2",
        "degCA",
        "0.0",
        -64,
        64,
        16,
        "intake_cvtc_actual_b2_deg_ca",
    ),
    FeedChannel(
        "stft_b1_pct", "VQ STFT B1", "%", "0.00", -25, 25, 5, "stft_b1_percent"
    ),
    FeedChannel(
        "stft_b2_pct", "VQ STFT B2", "%", "0.00", -25, 25, 5, "stft_b2_percent"
    ),
    FeedChannel(
        "ltft_b1_pct", "VQ LTFT B1", "%", "0.00", -25, 25, 5, "ltft_b1_percent"
    ),
    FeedChannel(
        "ltft_b2_pct", "VQ LTFT B2", "%", "0.00", -25, 25, 5, "ltft_b2_percent"
    ),
    FeedChannel(
        "battery_v", "VQ Battery Voltage", "V", "0.00", 8, 16, 1,
        "battery_voltage_v",
    ),
    FeedChannel(
        "throttle_target_pct",
        "VQ Throttle Target",
        "%",
        "0.00",
        0,
        100,
        10,
        "throttle_target_b1_percent",
    ),
)


def feed_values(model):
    """Return the finite channel values of a schema-verified model."""
    if not model.schema_verified:
        return {}
    values = {}
    for channel in CHANNELS:
        value = model.engineering.get(channel.source)
        if isinstance(value, (int, float)) and math.isfinite(value):
            values[channel.key] = float(value)
    return values


def encode(values):
    """Encode channel values as one datagram; keys follow the channel table."""
    tokens = [MAGIC]
    tokens.extend(f"{key}={value:.7g}" for key, value in values.items())
    return " ".join(tokens).encode("ascii")


def plugin_properties(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Return the RomRaider plugin file that declares the channel table."""
    lines = [
        f"datasource.class={DATASOURCE_CLASS}",
        f"udp.name={DATASOURCE_NAME}",
        f"udp.host={host}",
        f"udp.port={port}",
    ]
    for index, channel in enumerate(CHANNELS, start=1):
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


def plugin_state(path, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Compare the plugin file with this endpoint and channel table."""
    try:
        text = Path(path).read_text(encoding="ascii")
    except FileNotFoundError:
        return "missing"
    except (OSError, ValueError):
        return "outdated"
    return "current" if text == plugin_properties(host, port) else "outdated"


def install_plugin(path, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Write the plugin file, creating its folders; return its path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plugin_properties(host, port), encoding="ascii")
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

    def __init__(self, host, port, sock=None):
        self.endpoint = (host, port)
        self.sent = 0
        self.errors = 0
        self.last_error = None
        self._socket = sock or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def publish(self, model):
        """Send one datagram; return whether the model had values to send."""
        values = feed_values(model)
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
