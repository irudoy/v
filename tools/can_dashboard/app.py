#!/usr/bin/env python3
"""Cross-platform live dashboard for VQ custom CAN telemetry."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass, replace
import math
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import (
    PRODUCT_NAME,
    PRODUCT_SHORT_NAME,
    PRODUCT_SLUG,
    __version__,
)
from tools.can_dashboard import logfile as dashboard_log
from tools.can_dashboard import settings as dashboard_settings
from tools.can_dashboard.feed_dialog import FeedDialog
from tools.can_dashboard.hero_picker import HeroChoice, HeroPicker
from tools.can_dashboard.model import (
    DEFAULT_BITRATE,
    DEFAULT_CAN_ID,
    DashboardModel,
    FrameClock,
    FrameRecord,
    SnapshotRecord,
)
from tools.can_dashboard.live_feed import LiveFeed, parse_endpoint
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.can_dashboard.replay import (
    ReplayError,
    ReplayLoaded,
    ReplayPlayer,
    load_timeline,
    next_speed,
)
from tools.can_dashboard.sources import (
    ControlRequest,
    ControlStatus,
    PcanConfiguration,
    SourceStatus,
    run_demo,
    run_pcan,
)
from tools.can_dashboard.widgets import (
    Cluster,
    FlowBar,
    HeroRow,
    ResponsiveGrid,
    ScrollableFrame,
    StatusField,
    ToolButton,
    Tooltip,
    elide,
    elide_middle,
    hero_value_size,
    split_label_value,
)
from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


@dataclass(frozen=True)
class Palette:
    """Colors of one theme; `traces` colors the hero cards by position."""

    name: str
    bg: str
    panel: str
    panel_alt: str
    border: str
    text: str
    muted: str
    heading: str
    green: str
    amber: str
    red: str
    blue: str
    cyan: str
    traces: tuple
    button_face: str
    button_hover: str
    lit_text: str

    def button_colors(self):
        return {
            "face": self.button_face,
            "hover": self.button_hover,
            "text": self.text,
            "border": self.border,
            "focus": self.blue,
            "lit": self.green,
            "record": self.red,
            "lit_text": self.lit_text,
        }

    def tooltip_options(self):
        return {
            "background": self.panel_alt,
            "foreground": self.text,
            "border": self.border,
            "font": ui_font(9),
        }


DARK = Palette(
    name="dark",
    bg="#000000",
    panel="#0b0b0b",
    panel_alt="#161616",
    border="#363636",
    text="#f5f5f5",
    muted="#a3a3a3",
    heading="#ffb000",
    green="#2fd35a",
    amber="#ffb000",
    red="#ff453a",
    blue="#4da3ff",
    cyan="#00d0d8",
    traces=(
        "#ffd400",
        "#00d8ff",
        "#ff4fd8",
        "#35e06f",
        "#ff8a1f",
        "#5c9dff",
        "#ff5a4f",
        "#f5f5f5",
    ),
    button_face="#161616",
    button_hover="#2a2a2a",
    lit_text="#000000",
)
LIGHT = Palette(
    name="light",
    bg="#ffffff",
    panel="#f2f2f2",
    panel_alt="#e4e4e4",
    border="#8c8c8c",
    text="#000000",
    muted="#404040",
    heading="#0b3d91",
    green="#087a2c",
    amber="#8a5200",
    red="#c4141b",
    blue="#0b57d0",
    cyan="#006d77",
    traces=(
        "#8a6500",
        "#00708c",
        "#a3158c",
        "#087a2c",
        "#b84a00",
        "#0b57d0",
        "#c4141b",
        "#000000",
    ),
    button_face="#e4e4e4",
    button_hover="#d0d0d0",
    lit_text="#ffffff",
)
PALETTES = {palette.name: palette for palette in (DARK, LIGHT)}

if sys.platform == "darwin":
    FONT_UI, FONT_UI_BOLD, FONT_MONO = "Helvetica Neue", None, "Menlo"
elif sys.platform.startswith("win"):
    FONT_UI, FONT_UI_BOLD, FONT_MONO = "Segoe UI", "Segoe UI Semibold", "Consolas"
else:
    FONT_UI, FONT_UI_BOLD, FONT_MONO = "DejaVu Sans", None, "DejaVu Sans Mono"


def ui_font(size, bold=False):
    if not bold:
        return (FONT_UI, size)
    if FONT_UI_BOLD is not None:
        return (FONT_UI_BOLD, size)
    return (FONT_UI, size, "bold")


def mono_font(size, bold=False):
    return (FONT_MONO, size, "bold") if bold else (FONT_MONO, size)


LOG = dashboard_log.logger()
POLL_INTERVAL_MS = 25
REFRESH_INTERVAL_MS = 50
PREFERRED_WINDOW_WIDTH = 1520
PREFERRED_WINDOW_HEIGHT = 920
MIN_WINDOW_WIDTH = 560
MIN_WINDOW_HEIGHT = 460
HERO_PAD = 8
HERO_SPARKLINE_HEIGHT = 34
HERO_UNIT_GAP = 5
HERO_UNIT_TOP = 6
PANEL_MIN_WIDTH = 250
PANEL_VALUE_WIDTH = 150
PANEL_VALUE_MIN_WIDTH = 104
PANEL_PAD = 10
PANEL_GAP = 6
FOOTNOTE = (
    "* Candidate transform. Timing is a software "
    "command; injection is a compensated command, not a measured electrical "
    "duration."
)
HEALTH_FIELDS = (
    ("tick", "Producer tick counter", "tick=65535"),
    ("groups", "Completed telemetry groups", "groups=9999999"),
    ("mismatch", "Schema mismatches", "mismatch=9999"),
    ("errors", "CAN error frames", "errors=9999"),
    ("overrun", "Producer snapshot overruns", "overrun=9999"),
    ("tx_abort", "Producer transmit aborts", "tx_abort=9999"),
    ("flags", "Telemetry status flags", "flags=overrun_latched,abort_latched"),
)


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    unit: str = ""
    digits: int = 1
    hexadecimal: bool = False


@dataclass(frozen=True)
class SourceEnvelope:
    generation: int
    event: SourceStatus | ControlStatus | FrameRecord | ReplayLoaded


def _parse_standard_can_id(value: str) -> int:
    try:
        can_id = int(value, 0)
    except (TypeError, ValueError) as error:
        raise ValueError("data CAN ID must be in 0x001..0x7FE") from error
    if not 1 <= can_id <= 0x7FE:
        raise ValueError("data CAN ID must be in 0x001..0x7FE")
    return can_id


HERO_METRICS = (
    Metric("rpm", "ENGINE SPEED", "RPM", 0),
    Metric("vehicle_speed_kmh", "VEHICLE SPEED", "km/h", 1),
    Metric("calculated_load_percent", "CALCULATED LOAD", "%", 1),
    Metric("timing_command_deg", "TIMING COMMAND", "degBTDC", 0),
    Metric("maf_total_g_s", "TOTAL AIRFLOW", "g/s", 2),
    Metric("injection_average_ms", "INJECTION CALC", "ms", 2),
    Metric("coolant_deg_c", "COOLANT", "degC", 0),
    Metric("gear", "SELECTOR", "", 0),
    Metric("selected_map", "SELECTED MAP", "", 0),
    Metric("zero_to_100_s", "0-100 KM/H", "s", 2),
    Metric("hundred_to_200_s", "100-200 KM/H", "s", 2),
)
OPTIONAL_HERO_KEYS = frozenset({
    "gear",
    "selected_map",
    "zero_to_100_s",
    "hundred_to_200_s",
})

PANELS = (
    ("Air and fuel", (
        Metric("maf_b1_v", "MAF bank 1", "V", 3),
        Metric("maf_b2_v", "MAF bank 2", "V", 3),
        Metric("bfs_ms", "BFS", "ms", 3),
        Metric("front_oxygen_sensor_b1_raw", "Front O2 sensor B1", "raw", 0),
        Metric("front_oxygen_sensor_b2_raw", "Front O2 sensor B2", "raw", 0),
        Metric("af_state_factor", "A/F state factor", "", 4),
        Metric("stft_b1_percent", "STFT bank 1", "%", 2),
        Metric("stft_b2_percent", "STFT bank 2", "%", 2),
        Metric("ltft_b1_percent", "LTFT bank 1", "%", 2),
        Metric("ltft_b2_percent", "LTFT bank 2", "%", 2),
    )),
    ("Ignition, throttle, and CVTC", (
        Metric("apc_command_raw", "APC command", "raw", 0),
        Metric("app1_v", "APP 1", "V", 3),
        Metric("app2_v", "APP 2", "V", 3),
        Metric("tps_b1_v", "TPS bank 1", "V", 3),
        Metric("tps_b2_v", "TPS bank 2", "V", 3),
        Metric("absolute_throttle_percent", "Absolute throttle", "%", 1),
        Metric("intake_cvtc_actual_b1_deg_ca", "Intake CVTC actual B1", "degCA", 1),
        Metric("intake_cvtc_actual_b2_deg_ca", "Intake CVTC actual B2", "degCA", 1),
        Metric("intake_cvtc_target_deg_ca", "Intake CVTC target", "degCA", 1),
        Metric("exhaust_cvtc_target_deg_ca", "Exhaust CVTC target", "degCA", 1),
        Metric("intake_cvtc_duty_b1_percent", "CVTC duty B1", "%", 1),
        Metric("intake_cvtc_duty_b2_percent", "CVTC duty B2", "%", 1),
    )),
    ("Injection and knock", (
        Metric("injection_0_ms", "Injection calc 0", "ms", 2),
        Metric("injection_1_ms", "Injection calc 1", "ms", 2),
        Metric("injection_2_ms", "Injection calc 2", "ms", 2),
        Metric("injection_3_ms", "Injection calc 3", "ms", 2),
        Metric("injection_4_ms", "Injection calc 4", "ms", 2),
        Metric("injection_5_ms", "Injection calc 5", "ms", 2),
        Metric("fuel_inhibit_mask", "Fuel inhibit mask", "", 0, True),
        Metric("knock_timing_state", "Knock timing state", "state", 3),
        Metric("knock_surface_mode", "Active hot surface"),
        Metric("knock_count_latched", "Knock interval count", "", 0),
        Metric("knock_channel_mask_latched", "Knock channel mask", "", 0, True),
        Metric("knock_margin_min_ch1_raw", "Knock margin ch 1", "raw", 0),
        Metric("knock_margin_min_ch2_raw", "Knock margin ch 2", "raw", 0),
        Metric("knock_margin_min_ch3_raw", "Knock margin ch 3", "raw", 0),
        Metric("knock_margin_min_ch4_raw", "Knock margin ch 4", "raw", 0),
        Metric("knock_margin_min_ch5_raw", "Knock margin ch 5", "raw", 0),
        Metric("knock_margin_min_ch6_raw", "Knock margin ch 6", "raw", 0),
    )),
    ("Temperatures and context", (
        Metric("iat_deg_c", "Intake air", "degC", 0),
        Metric("fuel_temperature_deg_c", "Fuel temperature", "degC", 0),
        Metric("oil_temperature_deg_c", "Oil temperature", "degC", 0),
        Metric("timing_state_2023_raw", "Timing state 2023", "", 0, True),
        Metric("timing_state_564c_raw", "Timing state 564C", "", 0, True),
        Metric("stock_rpm", "Stock CAN RPM", "RPM", 0),
        Metric("gear", "Selector"),
        Metric("ascd_button", "ASCD input"),
        Metric("dashboard_state", "Dashboard state"),
        Metric("context_name", "Last context"),
        Metric("gps_lat", "GPS latitude", "deg", 6),
        Metric("gps_lon", "GPS longitude", "deg", 6),
        Metric("gps_status", "GPS source"),
    )),
)

EXTENDED_PANELS = (
    ("Torque and requests", (
        Metric("engine_torque_state_nm", "Engine torque state", "Nm*", 1),
        Metric("throttle_request_bounded_raw", "Bounded throttle request", "raw", 0),
        Metric("throttle_target_shared_raw", "Shared throttle target", "raw", 0),
        Metric("throttle_target_channel_0_raw", "Throttle target channel 0", "raw", 0),
        Metric("throttle_target_channel_1_raw", "Throttle target channel 1", "raw", 0),
        Metric(
            "injection_end_angle_deg",
            "End of injection after intake TDC",
            "degATDC",
            0,
        ),
    )),
    ("CVTC detail", (
        Metric("exhaust_cvtc_actual_b1_deg_ca", "Exhaust CVTC actual B1", "degCA", 1),
        Metric("exhaust_cvtc_actual_b2_deg_ca", "Exhaust CVTC actual B2", "degCA", 1),
        Metric("intake_cvtc_duty_command_b1_percent", "Intake CVTC duty command B1", "%", 1),
        Metric("intake_cvtc_duty_command_b2_percent", "Intake CVTC duty command B2", "%", 1),
        Metric("exhaust_cvtc_duty_b1_word_percent", "Exhaust CVTC duty B1 word", "%", 1),
        Metric("exhaust_cvtc_duty_b2_word_percent", "Exhaust CVTC duty B2 word", "%", 1),
    )),
    ("Trims, pressure, and sensors", (
        Metric("ltft_learned_b1_percent", "LTFT learned bank 1", "%", 2),
        Metric("ltft_adjustment_b1_percent", "LTFT adjustment bank 1", "%", 2),
        Metric("atmospheric_pressure_raw", "Atmospheric pressure", "raw", 0),
        Metric("battery_voltage_v", "Battery voltage", "V", 2),
        Metric("front_af_sensor_b1_word_raw", "Front A/F sensor B1", "raw", 0),
        Metric("front_af_sensor_b2_word_raw", "Front A/F sensor B2", "raw", 0),
    )),
    ("Throttle and A/F states", (
        Metric("secondary_tps_b1_v", "Secondary TPS B1", "V", 3),
        Metric("secondary_tps_b2_v", "Secondary TPS B2", "V", 3),
        Metric("af_adjustment_b1_raw", "A/F adjustment B1", "raw", 0, True),
        Metric("af_adjustment_b2_raw", "A/F adjustment B2", "raw", 0, True),
        Metric("protocol_version", "Protocol version", "", 0),
        Metric("profile_crc16", "Profile CRC16", "", 0, True),
    )),
)


TABS = (
    ("Primary", PANELS),
    ("Extended", EXTENDED_PANELS),
)
DEFAULT_HERO_KEYS = tuple(
    metric.key for metric in HERO_METRICS if metric.key not in OPTIONAL_HERO_KEYS
)
RUN_METRICS = {"zero_to_100_s": "0-100", "hundred_to_200_s": "100-200"}


def _hero_catalog():
    """Every metric a hero card can show, the dedicated hero metrics first."""
    metrics = {metric.key: metric for metric in HERO_METRICS}
    choices = [
        HeroChoice(metric.key, metric.label.title(), "Summary")
        for metric in HERO_METRICS
    ]
    for _tab, panels in TABS:
        for title, panel_metrics in panels:
            for metric in panel_metrics:
                if metric.key in metrics:
                    continue
                metrics[metric.key] = metric
                choices.append(HeroChoice(metric.key, metric.label, title))
    return metrics, tuple(choices)


HERO_CATALOG, HERO_CHOICES = _hero_catalog()


class Sparkline(tk.Canvas):
    def __init__(self, master, color, palette, history=None):
        super().__init__(
            master,
            width=1,
            height=HERO_SPARKLINE_HEIGHT,
            background=palette.panel,
            highlightthickness=0,
        )
        self.color = color
        self.baseline = palette.border
        self.values = history if history is not None else deque(maxlen=180)
        self.bind("<Configure>", lambda _event: self.redraw())

    def push(self, value):
        if isinstance(value, (int, float)):
            self.values.append(float(value))
            self.redraw()

    def redraw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        self.create_line(0, height - 1, width, height - 1, fill=self.baseline)
        if len(self.values) < 2:
            return
        low = min(self.values)
        high = max(self.values)
        span = high - low
        if span < 1e-9:
            span = 1.0
        points = []
        denominator = max(1, len(self.values) - 1)
        for index, value in enumerate(self.values):
            x = index * (width - 1) / denominator
            y = height - 3 - (value - low) * (height - 7) / span
            points.extend((x, y))
        self.create_line(*points, fill=self.color, width=2, smooth=True)


class HeroCard(tk.Frame):
    """Headline value with a trace; it shrinks with the width it is given.

    The value font follows the card width, the title and the value elide, and
    the unit hides when a full-width sample of the value leaves no room.

    The card asks for a width of its own that the shown text cannot change:
    the title takes one character and the value row holds its size against
    its labels. A row of cards is therefore laid out from the width of the
    row alone, and a long value elides instead of widening every card,
    which would resize the cards and re-elide their values without end.
    """

    def __init__(self, master, metric, color, palette, history=None):
        super().__init__(
            master,
            bg=palette.panel,
            highlightbackground=palette.border,
            highlightthickness=1,
        )
        self.metric = metric
        self._title = metric.label.upper()
        self._value = "--"
        self._width = 0
        self._unit_shown = bool(metric.unit)
        self._title_font = tkfont.Font(root=master, font=ui_font(8, bold=True))
        self._value_font = tkfont.Font(root=master, font=mono_font(22, bold=True))
        self._unit_font = tkfont.Font(root=master, font=ui_font(8))
        self.title_label = tk.Label(
            self,
            text=self._title,
            bg=palette.panel,
            fg=palette.muted,
            font=self._title_font,
            anchor="w",
            width=1,
        )
        self.title_label.pack(fill="x", padx=HERO_PAD, pady=(6, 0))
        self.value_row = tk.Frame(self, bg=palette.panel, width=1, height=1)
        self.value_row.pack_propagate(False)
        self.value_row.pack(fill="x", padx=HERO_PAD)
        self.value_label = tk.Label(
            self.value_row,
            text=self._value,
            bg=palette.panel,
            fg=color,
            font=self._value_font,
            anchor="w",
        )
        self.value_label.pack(side="left")
        self.unit_label = tk.Label(
            self.value_row,
            text=metric.unit,
            bg=palette.panel,
            fg=palette.muted,
            font=self._unit_font,
        )
        if self._unit_shown:
            self.unit_label.pack(
                side="left",
                padx=(HERO_UNIT_GAP, 0),
                pady=(HERO_UNIT_TOP, 0),
            )
        self._row_height = None
        self._label_chrome = (
            self.value_label.winfo_reqheight()
            - self._value_font.metrics("linespace")
        )
        self._fit_value_row()
        self.sparkline = Sparkline(self, color, palette, history)
        self.sparkline.pack(fill="x", padx=6, pady=(0, 6))
        self.tooltip = Tooltip(
            self.title_label,
            self.tooltip_text,
            **palette.tooltip_options(),
        )
        self.bind("<Configure>", self._on_configure, add="+")

    @property
    def value_size(self):
        return int(self._value_font.cget("size"))

    def tooltip_text(self):
        unit = f" [{self.metric.unit}]" if self.metric.unit else ""
        return f"{self._title}{unit}\n{self._value}"

    @property
    def unit_shown(self):
        return self._unit_shown

    def _sample(self):
        metric = self.metric
        if metric.hexadecimal:
            return "0xFFFF"
        return "8888" + ("." + "8" * metric.digits if metric.digits else "")

    def _on_configure(self, event):
        if event.widget is self and event.width != self._width:
            self.fit(event.width)

    def fit(self, width):
        self._width = width
        inner = max(1, width - 2 * HERO_PAD - 2)
        size = hero_value_size(width)
        if size != self.value_size:
            self._value_font.configure(size=size)
        self.title_label.configure(
            text=elide(self._title, self._title_font.measure, inner)
        )
        needed = (
            self._value_font.measure(self._sample())
            + HERO_UNIT_GAP
            + self._unit_font.measure(self.metric.unit)
        )
        unit_shown = bool(self.metric.unit) and needed <= inner
        if unit_shown != self._unit_shown:
            self._unit_shown = unit_shown
            if unit_shown:
                self.unit_label.pack(
                    side="left",
                    padx=(HERO_UNIT_GAP, 0),
                    pady=(HERO_UNIT_TOP, 0),
                )
            else:
                self.unit_label.pack_forget()
        self._fit_value_row()
        self._show_value()

    def _fit_value_row(self):
        """Hold the value row at the height its own fonts ask for.

        The height comes from the fonts, because a label reports the size
        it asks for one idle pass after the font it draws with changes.
        """
        height = self._value_font.metrics("linespace") + self._label_chrome
        if self._unit_shown:
            height = max(
                height,
                self._unit_font.metrics("linespace")
                + self._label_chrome
                + HERO_UNIT_TOP,
            )
        if height != self._row_height:
            self._row_height = height
            self.value_row.configure(height=height)

    def _show_value(self):
        available = 0
        if self._width:
            available = max(1, self._width - 2 * HERO_PAD - 2)
            if self._unit_shown:
                available -= HERO_UNIT_GAP + self._unit_font.measure(
                    self.metric.unit
                )
        self.value_label.configure(
            text=elide(self._value, self._value_font.measure, available)
        )

    def update_value(self, text, numeric=None):
        if text != self._value:
            self._value = text
            self._show_value()
        if numeric is not None:
            self.sparkline.push(numeric)


class DataPanel(tk.Frame):
    """Titled list of metric rows that shrinks with its grid cell.

    A narrow cell takes width from the value column down to
    PANEL_VALUE_MIN_WIDTH and then elides the labels in the middle, which
    keeps a trailing bank or channel suffix; the tooltip of a label carries
    its full text.
    """

    def __init__(self, master, title, metrics, palette):
        super().__init__(
            master,
            bg=palette.panel,
            highlightbackground=palette.border,
            highlightthickness=1,
        )
        self.variables = {}
        self.labels = []
        self.fields = []
        self._fitted = None
        self._label_font = tkfont.Font(root=self, font=ui_font(9))
        tk.Label(
            self,
            text=title.upper(),
            bg=palette.panel,
            fg=palette.heading,
            font=ui_font(9, bold=True),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=PANEL_PAD,
            pady=(8, 6),
        )
        self.columnconfigure(0, weight=1)
        for row, metric in enumerate(metrics, start=1):
            label = tk.Label(
                self,
                text=metric.label,
                bg=palette.panel,
                fg=palette.muted,
                font=ui_font(9),
            )
            label.grid(
                row=row,
                column=0,
                sticky="w",
                padx=(PANEL_PAD, PANEL_GAP),
                pady=1,
            )
            label.tooltip = Tooltip(
                label,
                lambda text=metric.label: text,
                **palette.tooltip_options(),
            )
            self.labels.append((label, metric.label))
            variable = tk.StringVar(self, value="--")
            self.variables[metric.key] = variable
            field = StatusField(
                self,
                variable,
                title=metric.label,
                background=palette.panel,
                foreground=palette.text,
                font=mono_font(10),
                copy_feedback=palette.green,
                anchor="e",
                reserve=PANEL_VALUE_WIDTH,
                tooltip_options=palette.tooltip_options(),
            )
            field.grid(
                row=row,
                column=1,
                sticky="e",
                padx=(PANEL_GAP, PANEL_PAD),
                pady=1,
            )
            self.fields.append(field)
        self.bind("<Configure>", self._on_configure, add="+")

    def _on_configure(self, event):
        self.fit(event.width)

    def fit(self, width):
        """Share a cell of this pixel width between labels and values."""
        if width == self._fitted or not self.fields:
            return
        self._fitted = width
        border = int(self.cget("highlightthickness"))
        available = width - 2 * (border + PANEL_PAD + PANEL_GAP)
        measure = self._label_font.measure
        first, _full = self.labels[0]
        chrome = first.winfo_reqwidth() - measure(first.cget("text"))
        widest = max(measure(full) for _label, full in self.labels) + chrome
        field = self.fields[0]
        label_width, value_width = split_label_value(
            available,
            widest,
            field.outer_width(PANEL_VALUE_WIDTH),
            field.outer_width(PANEL_VALUE_MIN_WIDTH),
        )
        for field in self.fields:
            field.set_outer_width(value_width)
        for label, full in self.labels:
            shown = elide_middle(full, measure, label_width - chrome)
            if shown != label.cget("text"):
                label.configure(text=shown)

    def set_value(self, key, value):
        self.variables[key].set(value)


STATUS_FIELDS = (
    ("source_var", "Telemetry source", "text", "left",
     "Source: PCAN_USBBUS1, 500000 bit/s"),
    ("schema_var", "Wire schema state", "amber", "left", "Schema: VERIFIED"),
    ("rate_var", "Group and frame rates", "cyan", "left",
     "Groups: 100.0 Hz | Frames: 1000.0 Hz"),
    ("loss_var", "Loss and integrity counters", "muted", "left",
     "Loss: 0 | Incomplete: 0 | Malformed: 0 | Source drops: 0"),
    ("control_var", "Last stream command", "cyan", "right",
     "Control: START queued"),
    ("record_var", "MLG recording", "amber", "right", "MLG: recording"),
    ("feed_var", "Live value feed", "muted", "right",
     "Feed: udp 127.0.0.1:47809, 999999 sent"),
)
STREAM_CAPTIONS = {"start": "\u25b6 STREAM", "stop": "\u25a0 STREAM"}
RECORD_CAPTIONS = {False: "\u25cf REC", True: "\u25a0 REC"}
THEME_CAPTIONS = {"dark": "LIGHT", "light": "DARK"}
PLAY_CAPTIONS = {False: "\u25b6 PLAY", True: "\u2016 PAUSE"}
REPLAY_STEP_SECONDS = 5.0
REPLAY_FILETYPES = (
    ("Replay files", "*.trc *.mlg *.log *.txt"),
    ("PEAK trace", "*.trc"),
    ("Dashboard MLG recording", "*.mlg"),
    ("candump log", "*.log *.txt"),
    ("All files", "*.*"),
)
MAP_TOOLTIP = (
    "The telemetry stream does not carry the active map index. The dashboard "
    "sets Map 1 when it observes a controller start, and Map N when a "
    "SET + CANCEL selector gesture is answered by N feedback pulses of the "
    "CRUISE and SET lamps."
)
RUN_TOOLTIPS = {
    "0-100": (
        "0-100 km/h: armed at standstill, started by the first ABS speed "
        "above zero (about 1.5 km/h), stopped where the speed crosses "
        "100 km/h. Last run and best run of this source."
    ),
    "100-200": (
        "100-200 km/h: armed below 97 km/h, timed between the crossings of "
        "100 and 200 km/h. Last run and best run of this source."
    ),
}


def format_replay_time(seconds):
    """Minutes and seconds to a tenth, as m:ss.s."""
    minutes, rest = divmod(round(max(0.0, seconds), 1), 60.0)
    return f"{int(minutes)}:{rest:04.1f}"


class DashboardApp:
    player = None

    def __init__(self, root, args):
        self.root = root
        self.args = args
        self.events = queue.Queue(maxsize=20_000)
        self.source_drops = 0
        self.stop_event = None
        self.worker = None
        self.control_requests = None
        self.pcan_active = False
        self.source_generation = 0
        self.closed = False
        self.source_state = "stopped"
        self.source_detail = "not connected"
        self.model = DashboardModel(
            args.profile,
            args.can_id,
            args.tick_divisor,
            args.schema,
        )
        self.recorder = None
        self.recording_clock = None
        self.feed = None
        self.last_ui_group = 0
        self.stream_command = "start"
        self.source_button_active = None
        self.settings_path = getattr(args, "settings", None)
        self.settings = dashboard_settings.load(
            self.settings_path,
            catalog=HERO_CATALOG,
            default_hero=DEFAULT_HERO_KEYS,
        )
        self.feed_settings = self._launch_feed_settings()
        self.palette = PALETTES[self.settings.theme]
        self.hero_history = {}
        self.hero_cards = {}
        self.data_panels = []
        self.tab_panels = []
        self.panel_grids = []
        self.tab_buttons = []
        self.active_tab = 0
        self.picker = None
        self.feed_dialog = None
        self.status_dot_color = None
        self.map_color = None
        self.run_colors = {}
        self.scrub_position = None
        self._create_variables()
        self._restart_feed()
        self.root.title(f"{PRODUCT_NAME} v{__version__}")
        self._apply_initial_geometry()
        self._build_window()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        for sequence, handler in (
            ("<space>", self._on_replay_key_play),
            ("<Left>", lambda event: self._on_replay_key_step(event, -1)),
            ("<Right>", lambda event: self._on_replay_key_step(event, 1)),
            ("<Home>", self._on_replay_key_home),
        ):
            self.root.bind(sequence, handler, add="+")
        if sys.platform == "darwin":
            self.root.tk.createcommand("::tk::mac::Quit", self.close)
        self.root.after(POLL_INTERVAL_MS, self._poll)
        self.root.after(REFRESH_INTERVAL_MS, self._refresh_tick)
        if args.demo:
            self.root.after(200, self.start_demo)
        elif args.replay:
            self.root.after(200, lambda: self.start_replay(args.replay))
        elif not args.no_auto_connect:
            self.root.after(300, self.start_pcan)
        if args.record is not None:
            self.root.after(500, lambda: self.start_recording(args.record))

    def _create_variables(self):
        """Own every displayed value outside the widgets.

        A theme change rebuilds the widgets; the values survive it here.
        """
        self.status_var = tk.StringVar(self.root, value="DISCONNECTED")
        self.channel_var = tk.StringVar(self.root, value=self.args.channel)
        self.can_id_var = tk.StringVar(self.root, value=f"0x{self.args.can_id:03X}")
        self.active_var = tk.BooleanVar(self.root, value=not self.args.listen_only)
        self.source_var = tk.StringVar(self.root, value="Source: not connected")
        self.schema_var = tk.StringVar(self.root, value="Schema: waiting")
        self.rate_var = tk.StringVar(self.root, value="Groups: 0.0 Hz | Frames: 0.0 Hz")
        self.loss_var = tk.StringVar(self.root, value="Loss: 0 | Incomplete: 0 | Malformed: 0")
        self.control_var = tk.StringVar(self.root, value="Control: idle")
        self.record_var = tk.StringVar(self.root, value="MLG: idle")
        self.feed_var = tk.StringVar(self.root, value="Feed: off")
        self.map_var = tk.StringVar(self.root, value="MAP ?")
        self.run_value_vars = {
            name: tk.StringVar(self.root, value="--")
            for name in RUN_TOOLTIPS
        }
        self.run_best_vars = {
            name: tk.StringVar(self.root, value="best --")
            for name in RUN_TOOLTIPS
        }
        self.replay_time_var = tk.StringVar(self.root, value="0:00.0 / 0:00.0")
        self.health_vars = {
            key: tk.StringVar(self.root, value=f"{key}=--")
            for key, _title, _sample in HEALTH_FIELDS
        }

    def _build_window(self):
        """Build every widget in the current palette, replacing older ones."""
        for child in self.root.winfo_children():
            child.destroy()
        self.hero_cards = {}
        self.data_panels = []
        self.tab_panels = []
        self.panel_grids = []
        self.tab_buttons = []
        self.picker = None
        self.feed_dialog = None
        self.source_button_active = None
        self.status_dot_color = None
        self.map_color = None
        self.run_colors = {}
        self.root.configure(bg=self.palette.bg)
        self._configure_styles()
        self._build_header()
        self._build_status_bar()
        self._build_drive_bar()
        self._build_replay_bar()
        self._build_health_bar()
        self._build_content()
        self._sync_source_button()
        self._sync_record_button()
        self._sync_replay_bar()

    def _apply_initial_geometry(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = max(
            MIN_WINDOW_WIDTH,
            min(PREFERRED_WINDOW_WIDTH, screen_width - 80),
        )
        height = max(
            MIN_WINDOW_HEIGHT,
            min(PREFERRED_WINDOW_HEIGHT, screen_height - 120),
        )
        left = max(0, (screen_width - width) // 2)
        top = max(0, (screen_height - height) // 3)
        self.root.geometry(f"{width}x{height}+{left}+{top}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    def _configure_styles(self):
        palette = self.palette
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Dashboard.Vertical.TScrollbar",
            background=palette.panel_alt,
            troughcolor=palette.bg,
            bordercolor=palette.border,
            arrowcolor=palette.muted,
            darkcolor=palette.panel_alt,
            lightcolor=palette.panel_alt,
        )
        style.map(
            "Dashboard.Vertical.TScrollbar",
            background=[("active", palette.border)],
        )

    def _tool_button(self, master, text, command, tooltip, **options):
        return ToolButton(
            master,
            text=text,
            command=command,
            colors=self.palette.button_colors(),
            tooltip=tooltip,
            tooltip_options=self.palette.tooltip_options(),
            font=ui_font(9, bold=True),
            **options,
        )

    def _build_header(self):
        palette = self.palette
        header = FlowBar(self.root, bg=palette.bg, spacing_x=5, spacing_y=5)
        header.pack(side="top", fill="x", padx=12, pady=(7, 5))
        self.title_label = header.add(tk.Label(
            header,
            text=f"{PRODUCT_SHORT_NAME} v{__version__}",
            bg=palette.bg,
            fg=palette.muted,
            font=ui_font(10, bold=True),
        ))

        link = Cluster(header, bg=palette.bg)
        self.status_dot = tk.Label(
            link,
            text="\u25cf",
            bg=palette.bg,
            fg=palette.muted,
            font=ui_font(11),
        )
        self.status_dot.pack(side="left", padx=(6, 4))
        self.status_field = StatusField(
            link,
            self.status_var,
            title="Link state",
            background=palette.bg,
            foreground=palette.muted,
            font=ui_font(10, bold=True),
            copy_feedback=palette.green,
            tooltip_options=palette.tooltip_options(),
        )
        self.status_field.pack(side="left")
        header.add(link)

        header.add(
            self._control_entry(header, "CH", self.channel_var, 13),
            align="right",
        )
        header.add(
            self._control_entry(header, "ID", self.can_id_var, 6),
            align="right",
        )
        self.active_button = self._tool_button(
            header,
            "ACK",
            self.toggle_active,
            "Active/ACK PCAN state: the adapter acknowledges frames and can "
            "send START and STOP. Off selects listen-only. It applies at the "
            "next connect.",
            lit=self.active_var.get(),
        )
        header.add(self.active_button, align="right")
        self.source_button = self._tool_button(
            header,
            "CONNECT",
            self.toggle_source,
            "Open or close the PCAN channel",
        )
        header.add(self.source_button, align="right")
        header.add(
            self._tool_button(
                header,
                "DEMO",
                self.start_demo,
                "Run the deterministic demo source",
            ),
            align="right",
        )
        header.add(
            self._tool_button(
                header,
                "REPLAY",
                self.select_replay,
                "Replay a PEAK TRC 1.1 trace, a dashboard MLG recording, or a "
                "compact candump log",
            ),
            align="right",
        )
        self.stream_button = self._tool_button(
            header,
            self._stream_button_text(),
            self.toggle_stream,
            "Send START or STOP to the ECU telemetry stream",
            lit=self.stream_command == "stop",
        )
        header.add(self.stream_button, align="right")
        self.record_button = self._tool_button(
            header,
            RECORD_CAPTIONS[False],
            self.toggle_recording,
            "Record the telemetry to an MLG file",
            lit_role="record",
        )
        header.add(self.record_button, align="right")
        self.feed_button = self._tool_button(
            header,
            "FEED",
            self.open_feed_dialog,
            "Send live values to RomRaider Logger for the table overlay",
            lit=self.feed is not None,
        )
        header.add(self.feed_button, align="right")
        header.add(
            self._tool_button(
                header,
                "CARDS",
                self.open_hero_picker,
                "Choose the cards of the top row",
            ),
            align="right",
        )
        self.theme_button = self._tool_button(
            header,
            THEME_CAPTIONS[palette.name],
            self.toggle_theme,
            "Switch between the dark theme and the daylight theme",
        )
        header.add(self.theme_button, align="right")

    def _build_status_bar(self):
        palette = self.palette
        bar = FlowBar(
            self.root,
            bg=palette.panel_alt,
            highlightbackground=palette.border,
            highlightthickness=1,
            spacing_x=14,
            spacing_y=4,
            pad_x=10,
            pad_y=4,
        )
        bar.pack(side="top", fill="x", padx=12, pady=(0, 7))
        for name, title, role, align, sample in STATUS_FIELDS:
            if name == "feed_var" and self.feed is None:
                sample = self.feed_var.get()
            bar.add(
                self._status_field(
                    bar,
                    getattr(self, name),
                    title,
                    getattr(palette, role),
                    sample,
                    anchor="e" if align == "right" else "w",
                ),
                align=align,
            )

    def _build_health_bar(self):
        palette = self.palette
        bar = FlowBar(
            self.root,
            bg=palette.panel_alt,
            spacing_x=14,
            spacing_y=4,
            pad_x=10,
            pad_y=4,
        )
        bar.pack(side="bottom", fill="x", padx=12, pady=(0, 7))
        for key, title, sample in HEALTH_FIELDS:
            bar.add(
                self._status_field(
                    bar,
                    self.health_vars[key],
                    title,
                    palette.muted,
                    sample,
                )
            )

    def _build_drive_bar(self):
        """Selected map and the acceleration timers, under the status bar."""
        palette = self.palette
        bar = FlowBar(self.root, bg=palette.bg, spacing_x=18, spacing_y=4)
        bar.pack(side="top", fill="x", padx=12, pady=(0, 6))
        self.drive_bar = bar
        badge = tk.Frame(bar, bg=palette.border)
        self.map_label = tk.Label(
            badge,
            textvariable=self.map_var,
            width=6,
            bg=palette.panel_alt,
            fg=palette.muted,
            font=ui_font(15, bold=True),
            padx=8,
        )
        self.map_label.pack(padx=1, pady=1)
        Tooltip(self.map_label, self._map_tooltip, **palette.tooltip_options())
        bar.add(badge)
        self.run_value_labels = {}
        for name, tooltip in RUN_TOOLTIPS.items():
            cluster = Cluster(bar, bg=palette.bg)
            title = tk.Label(
                cluster,
                text=name,
                bg=palette.bg,
                fg=palette.muted,
                font=ui_font(9, bold=True),
            )
            title.pack(side="left", padx=(0, 6))
            value = tk.Label(
                cluster,
                textvariable=self.run_value_vars[name],
                width=8,
                anchor="e",
                bg=palette.bg,
                fg=palette.text,
                font=mono_font(14, bold=True),
            )
            value.pack(side="left")
            best = tk.Label(
                cluster,
                textvariable=self.run_best_vars[name],
                width=14,
                anchor="w",
                bg=palette.bg,
                fg=palette.muted,
                font=mono_font(9),
            )
            best.pack(side="left", padx=(8, 0))
            for widget in (title, value, best):
                Tooltip(widget, tooltip, **palette.tooltip_options())
            self.run_value_labels[name] = value
            bar.add(cluster)
        bar.add(
            self._tool_button(
                bar,
                "RESET TIMES",
                self.reset_acceleration,
                "Clear the last and best 0-100 and 100-200 km/h times",
            ),
            align="right",
        )

    def _build_replay_bar(self):
        """Transport controls and the scrub line of a loaded replay."""
        palette = self.palette
        bar = tk.Frame(
            self.root,
            bg=palette.panel_alt,
            highlightbackground=palette.border,
            highlightthickness=1,
        )
        self.replay_bar = bar
        controls = tk.Frame(bar, bg=palette.panel_alt)
        controls.pack(side="left", padx=(6, 0), pady=4)
        self.play_button = self._tool_button(
            controls,
            PLAY_CAPTIONS[False],
            self.toggle_play,
            "Play or pause the replay (Space)",
            pady=1,
        )
        self.loop_button = self._tool_button(
            controls,
            "LOOP",
            self.toggle_loop,
            "Repeat the replay, or the region between IN and OUT",
            pady=1,
        )
        self.loop_in_button = self._tool_button(
            controls,
            "IN",
            self.toggle_loop_in,
            "Start the loop region at the current position; click again "
            "to clear it",
            pady=1,
        )
        self.loop_out_button = self._tool_button(
            controls,
            "OUT",
            self.toggle_loop_out,
            "End the loop region at the current position; click again "
            "to clear it",
            pady=1,
        )
        self.speed_button = self._tool_button(
            controls,
            "1x",
            self.cycle_speed,
            "Replay speed; click for the next of 0.25x to 8x",
            pady=1,
        )
        for button in (
            self.play_button,
            self.loop_button,
            self.loop_in_button,
            self.loop_out_button,
            self.speed_button,
        ):
            button.pack(side="left", padx=(0, 4))
        self.replay_time_label = tk.Label(
            bar,
            textvariable=self.replay_time_var,
            width=17,
            anchor="e",
            bg=palette.panel_alt,
            fg=palette.cyan,
            font=mono_font(9),
        )
        self.replay_time_label.pack(side="right", padx=(0, 8))
        self.timeline_canvas = tk.Canvas(
            bar,
            width=160,
            height=24,
            bg=palette.panel_alt,
            highlightthickness=0,
            cursor="hand2",
        )
        self.timeline_canvas.pack(
            side="left", fill="x", expand=True, padx=8, pady=4
        )
        Tooltip(
            self.timeline_canvas,
            "Click or drag to move the replay; Left and Right step 5 s, "
            "Home returns to the loop start",
            **palette.tooltip_options(),
        )
        self.timeline_canvas.bind(
            "<Configure>", lambda _event: self._draw_timeline(), add="+"
        )
        self.timeline_canvas.bind("<Button-1>", self._on_timeline_drag, add="+")
        self.timeline_canvas.bind("<B1-Motion>", self._on_timeline_drag, add="+")
        self.timeline_canvas.bind(
            "<ButtonRelease-1>", self._on_timeline_release, add="+"
        )

    def _sync_replay_bar(self):
        bar = getattr(self, "replay_bar", None)
        if bar is None:
            return
        if self.player is None:
            if bar.winfo_manager():
                bar.pack_forget()
            return
        if not bar.winfo_manager():
            bar.pack(
                side="top",
                fill="x",
                padx=12,
                pady=(0, 7),
                after=self.drive_bar,
            )
        self._sync_replay_controls()

    def _sync_replay_controls(self):
        player = self.player
        if player is None or getattr(self, "play_button", None) is None:
            return
        self.play_button.configure(
            text=PLAY_CAPTIONS[player.playing],
            lit=player.playing,
        )
        self.loop_button.configure(lit=player.loop)
        self.loop_in_button.configure(lit=player.loop_in is not None)
        self.loop_out_button.configure(lit=player.loop_out is not None)
        self.speed_button.configure(text=f"{player.speed:g}x")
        self._refresh_replay()

    def _map_tooltip(self):
        tracker = self.model.drive.map
        return f"{tracker.reason}.\n\n{MAP_TOOLTIP}"

    def _timeline_bounds(self):
        width = self.timeline_canvas.winfo_width()
        return 6, max(7, width - 6)

    def _timeline_x(self, seconds):
        left, right = self._timeline_bounds()
        duration = self.player.duration
        share = seconds / duration if duration > 0 else 0.0
        return left + max(0.0, min(1.0, share)) * (right - left)

    def _timeline_seconds(self, x):
        left, right = self._timeline_bounds()
        share = (x - left) / (right - left)
        return max(0.0, min(1.0, share)) * self.player.duration

    def _on_timeline_drag(self, event):
        if self.player is None:
            return
        self.scrub_position = self._timeline_seconds(event.x)
        self._refresh_replay()

    def _on_timeline_release(self, event):
        if self.player is None:
            return
        self.scrub_position = None
        self._replay_seek(self._timeline_seconds(event.x))
        self._refresh_replay()

    def _draw_timeline(self):
        canvas = getattr(self, "timeline_canvas", None)
        player = self.player
        if canvas is None or player is None:
            return
        palette = self.palette
        canvas.delete("all")
        height = max(canvas.winfo_height(), 12)
        middle = height // 2
        left, right = self._timeline_bounds()
        canvas.create_rectangle(
            left, middle - 2, right, middle + 2,
            fill=palette.border, outline="",
        )
        if player.loop_in is not None or player.loop_out is not None:
            start, stop = player.region()
            canvas.create_rectangle(
                self._timeline_x(start), middle - 6,
                self._timeline_x(stop), middle + 6,
                fill="", outline=palette.cyan, width=1,
            )
        position = (
            player.position
            if self.scrub_position is None
            else self.scrub_position
        )
        cursor = self._timeline_x(position)
        canvas.create_rectangle(
            left, middle - 2, cursor, middle + 2,
            fill=palette.heading, outline="",
        )
        canvas.create_line(
            cursor, 2, cursor, height - 2, fill=palette.text, width=2
        )

    def _refresh_replay(self):
        player = self.player
        if player is None:
            return
        position = (
            player.position
            if self.scrub_position is None
            else self.scrub_position
        )
        self.replay_time_var.set(
            f"{format_replay_time(position)} / "
            f"{format_replay_time(player.duration)}"
        )
        self._draw_timeline()

    def _refresh_drive(self):
        palette = self.palette
        drive = self.model.drive
        number = drive.map.number
        self.map_var.set("MAP ?" if number is None else f"MAP {number}")
        color = palette.muted if number is None else palette.heading
        if color != self.map_color:
            self.map_color = color
            self.map_label.configure(fg=color)
        for run in drive.acceleration.runs:
            elapsed = run.elapsed()
            if elapsed is not None:
                text, color = f"{elapsed:.2f} s", palette.amber
            elif run.last is not None:
                text, color = f"{run.last.seconds:.2f} s", palette.text
            else:
                text, color = "--", palette.muted
            self.run_value_vars[run.name].set(text)
            if color != self.run_colors.get(run.name):
                self.run_colors[run.name] = color
                self.run_value_labels[run.name].configure(fg=color)
            best = "--" if run.best is None else f"{run.best.seconds:.2f} s"
            self.run_best_vars[run.name].set(f"best {best}")

    def _build_content(self):
        palette = self.palette
        content = ScrollableFrame(self.root, background=palette.bg)
        content.pack(side="top", fill="both", expand=True)
        body = content.content

        self.hero_row = HeroRow(body, spacing=6, bg=palette.bg)
        self.hero_row.pack(fill="x", padx=12 - self.hero_row.margin)
        self._build_hero_cards()

        tabs = tk.Frame(body, bg=palette.bg)
        tabs.pack(fill="x", padx=12, pady=(7, 0))
        host = tk.Frame(body, bg=palette.bg)
        host.pack(fill="both", expand=True, padx=12, pady=(4, 7))
        host.bind("<Configure>", self._layout_panel_grids, add="+")
        for index, (tab_name, definitions) in enumerate(TABS):
            button = self._tool_button(
                tabs,
                tab_name.upper(),
                lambda index=index: self.select_tab(index),
                f"Show the {tab_name.lower()} panels",
                pady=2,
            )
            button.pack(side="left", padx=(0, 4))
            self.tab_buttons.append(button)
            panels = ResponsiveGrid(
                host,
                min_column_width=PANEL_MIN_WIDTH,
                spacing=6,
                uniform="panel",
                row_weight=1,
                min_from_children=False,
                balanced=True,
                bg=palette.bg,
            )
            self.panel_grids.append(panels)
            tab_panels = []
            for title, metrics in definitions:
                panel = panels.add(DataPanel(panels, title, metrics, palette))
                tab_panels.append((panel, metrics))
                self.data_panels.append((panel, metrics))
            self.tab_panels.append(tuple(tab_panels))
        self.select_tab(self.active_tab)

        self.footnote = tk.Label(
            body,
            text=FOOTNOTE,
            bg=palette.bg,
            fg=palette.muted,
            font=ui_font(8),
            anchor="w",
            justify="left",
        )
        self.footnote.pack(fill="x", padx=13, pady=(0, 6))
        self.footnote.bind("<Configure>", self._wrap_footnote, add="+")

    def _build_hero_cards(self):
        """Fill the hero row with the configured cards, in their order."""
        for card in self.hero_cards.values():
            card.destroy()
        keys = self.settings.hero
        self.hero_history = {
            key: self.hero_history.get(key, deque(maxlen=180)) for key in keys
        }
        traces = self.palette.traces
        self.hero_cards = {
            key: HeroCard(
                self.hero_row,
                HERO_CATALOG[key],
                traces[index % len(traces)],
                self.palette,
                self.hero_history[key],
            )
            for index, key in enumerate(keys)
        }
        self.hero_row.set_cards(tuple(self.hero_cards.values()))
        if not keys:
            self.hero_row.configure(height=1)

    def select_tab(self, index):
        """Show one tab of panels; only a shown panel follows live values."""
        self.active_tab = index
        for position, panels in enumerate(self.panel_grids):
            if position == index:
                panels.pack(fill="both", expand=True)
            else:
                panels.pack_forget()
        for position, button in enumerate(self.tab_buttons):
            button.configure(lit=position == index)
        if index < len(self.tab_panels):
            self._refresh_panels(index)

    def _store_settings(self, **changes):
        """Adopt changed settings and write them when a file is configured."""
        self.settings = dashboard_settings.Settings(**{
            "theme": self.settings.theme,
            "hero": self.settings.hero,
            "feed": self.settings.feed,
            **changes,
        })
        if self.settings_path is None:
            return
        try:
            dashboard_settings.save(self.settings_path, self.settings)
        except OSError as error:
            messagebox.showwarning(
                "Settings were not saved",
                f"{self.settings_path}\n{error}",
            )

    def toggle_theme(self):
        name = "light" if self.palette.name == "dark" else "dark"
        self._store_settings(theme=name)
        self.palette = PALETTES[name]
        self._build_window()

    def toggle_active(self):
        self.active_var.set(not self.active_var.get())
        self.active_button.configure(lit=self.active_var.get())

    def open_hero_picker(self):
        if self.picker is not None and self.picker.winfo_exists():
            self.picker.lift()
            return
        palette = self.palette
        self.picker = HeroPicker(
            self.root,
            choices=HERO_CHOICES,
            selected=self.settings.hero,
            defaults=DEFAULT_HERO_KEYS,
            limit=dashboard_settings.HERO_LIMIT,
            colors={
                "bg": palette.bg,
                "panel": palette.panel,
                "border": palette.border,
                "text": palette.text,
                "muted": palette.muted,
                "heading": palette.heading,
                "select": palette.blue,
                "select_text": palette.lit_text,
            },
            button_colors=palette.button_colors(),
            fonts={
                "label": ui_font(9),
                "heading": ui_font(9, bold=True),
                "list": ui_font(10),
                "button": ui_font(9, bold=True),
            },
            on_apply=self.apply_hero_keys,
            tooltip_options=palette.tooltip_options(),
        )

    def _launch_feed_settings(self):
        """Stored feed settings with the command-line overrides of this run."""
        feed = self.settings.feed
        if self.args.publish_udp is not None:
            host, port = self.args.publish_udp
            feed = replace(feed, enabled=True, host=host, port=port)
        return feed

    def _restart_feed(self):
        if self.feed is not None:
            self.feed.close()
            self.feed = None
        feed = self.feed_settings
        if not feed.enabled:
            self.feed_var.set("Feed: off")
            return
        try:
            self.feed = LiveFeed(feed.host, feed.port)
        except OSError as error:
            self.feed_var.set(f"Feed: {error}")
            return
        self.feed_var.set(f"Feed: {self.feed.status()}")

    def open_feed_dialog(self):
        if self.feed_dialog is not None and self.feed_dialog.winfo_exists():
            self.feed_dialog.lift()
            return
        palette = self.palette
        self.feed_dialog = FeedDialog(
            self.root,
            feed=self.feed_settings,
            colors={
                "bg": palette.bg,
                "panel": palette.panel,
                "border": palette.border,
                "text": palette.text,
                "muted": palette.muted,
                "heading": palette.heading,
                "select": palette.blue,
                "ok": palette.green,
                "error": palette.red,
            },
            button_colors=palette.button_colors(),
            fonts={
                "label": ui_font(9),
                "heading": ui_font(9, bold=True),
                "entry": mono_font(10),
                "button": ui_font(9, bold=True),
            },
            on_apply=self.apply_feed,
            tooltip_options=palette.tooltip_options(),
        )

    def apply_feed(self, feed):
        """Run the feed as the dialog set it and remember the choice."""
        self.feed_settings = feed
        self._store_settings(feed=feed)
        self._restart_feed()
        self._build_window()

    def apply_hero_keys(self, keys):
        keys = dashboard_settings.normalize_hero(keys, HERO_CATALOG)
        self._store_settings(hero=keys)
        self._build_hero_cards()

    def _layout_panel_grids(self, event):
        for panels in self.panel_grids:
            panels.layout(event.width)

    def _wrap_footnote(self, event):
        wrap = max(240, event.width - 4)
        if wrap != self.footnote.cget("wraplength"):
            self.footnote.configure(wraplength=wrap)

    def _status_field(self, master, variable, title, color, sample, anchor="w"):
        return StatusField(
            master,
            variable,
            title=title,
            background=self.palette.panel_alt,
            foreground=color,
            font=mono_font(9),
            copy_feedback=self.palette.green,
            anchor=anchor,
            sample=sample,
            tooltip_options=self.palette.tooltip_options(),
        )

    def _control_entry(self, parent, label, variable, width):
        palette = self.palette
        group = tk.Frame(parent, bg=palette.bg)
        tk.Label(
            group,
            text=label,
            bg=palette.bg,
            fg=palette.muted,
            font=ui_font(8, bold=True),
        ).pack(side="left", padx=(0, 4))
        tk.Entry(
            group,
            textvariable=variable,
            width=width,
            bg=palette.panel_alt,
            fg=palette.text,
            insertbackground=palette.text,
            relief="flat",
            highlightthickness=1,
            highlightbackground=palette.border,
            highlightcolor=palette.blue,
            font=mono_font(9),
        ).pack(side="left", ipady=2)
        return group

    def _source_emitter(self):
        generation = self.source_generation

        def emit(event):
            if generation != self.source_generation:
                return
            envelope = SourceEnvelope(generation, event)
            try:
                self.events.put_nowait(envelope)
            except queue.Full:
                self.source_drops += 1
                if isinstance(event, SourceStatus):
                    try:
                        self.events.get_nowait()
                        self.events.put_nowait(envelope)
                    except (queue.Empty, queue.Full):
                        pass

        return emit

    def _selected_can_id(self):
        try:
            return _parse_standard_can_id(self.can_id_var.get())
        except ValueError as error:
            self._set_source_status("error", str(error))
            return None

    def _new_model(self, can_id):
        self.model = DashboardModel(
            self.args.profile,
            can_id,
            self.args.tick_divisor,
            self.args.schema,
        )
        self.last_ui_group = 0
        self.source_drops = 0

    def toggle_source(self):
        if self.source_is_active():
            self.stop_source()
        else:
            self.start_pcan()

    def source_is_active(self):
        return self.player is not None or (
            self.worker is not None and self.worker.is_alive()
        )

    def _sync_source_button(self):
        active = self.source_is_active()
        if active == self.source_button_active:
            return
        self.source_button_active = active
        self.source_button.configure(
            text="DISCONNECT" if active else "CONNECT",
            lit=active,
        )

    def _sync_record_button(self):
        recording = self.recorder is not None
        self.record_button.configure(
            text=RECORD_CAPTIONS[recording],
            lit=recording,
        )

    def start_pcan(self):
        self.stop_source()
        can_id = self._selected_can_id()
        if can_id is None:
            return
        channel = self.channel_var.get().strip()
        if not channel:
            self._set_source_status("error", "PCAN channel is empty")
            return
        self._new_model(can_id)
        config = PcanConfiguration(
            channel=channel,
            bitrate=self.args.bitrate,
            can_id=can_id,
            listen_only=not self.active_var.get(),
            reset_channel=self.args.reset_channel,
        )
        self.stop_event = threading.Event()
        self.control_requests = queue.Queue(maxsize=8)
        self.pcan_active = not config.listen_only
        self.worker = threading.Thread(
            target=run_pcan,
            args=(
                config,
                self.stop_event,
                self._source_emitter(),
                self.control_requests,
            ),
            daemon=True,
            name="pcan-reader",
        )
        self._set_source_status("connecting", f"opening {channel}")
        self.worker.start()

    def toggle_stream(self):
        self.send_stream_command(self.stream_command)

    def _stream_button_text(self):
        return STREAM_CAPTIONS[self.stream_command]

    def _set_stream_command(self, command):
        self.stream_command = command
        self.stream_button.configure(
            text=self._stream_button_text(),
            lit=command == "stop",
        )

    def send_stream_command(self, command):
        if (
            self.control_requests is None
            or self.worker is None
            or not self.worker.is_alive()
        ):
            self.control_var.set("Control error: connect PCAN first")
            return
        if not self.pcan_active:
            self.control_var.set(
                "Control error: reconnect with ACK enabled"
            )
            return
        try:
            can_id, payload = can_telemetry_schema.control_frame(
                self.model.decoder.schema,
                self.model.can_id,
                command,
            )
            self.control_requests.put_nowait(
                ControlRequest(command, can_id, payload)
            )
        except queue.Full:
            detail = "command queue is full"
            self.control_var.set(f"Control error: {detail}")
            return
        except ValueError as error:
            detail = str(error)
            self.control_var.set(f"Control error: {detail}")
            return
        self.control_var.set(f"Control: {command.upper()} queued")

    def start_demo(self):
        self.stop_source()
        can_id = self._selected_can_id()
        if can_id is None:
            return
        self._new_model(can_id)
        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_demo,
            args=(
                can_id,
                self.stop_event,
                self._source_emitter(),
                self.args.profile,
                self.args.schema,
            ),
            daemon=True,
            name="telemetry-demo",
        )
        self.worker.start()

    def select_replay(self):
        path = filedialog.askopenfilename(
            title="Select a TRC, MLG, or candump replay",
            filetypes=REPLAY_FILETYPES,
        )
        if path:
            self.start_replay(Path(path))

    def start_replay(self, path):
        """Load a replay file in the background, then play it."""
        self.stop_source()
        can_id = self._selected_can_id()
        if can_id is None:
            return
        self._new_model(can_id)
        path = Path(path)
        emit = self._source_emitter()
        profile = self.args.profile
        schema = self.args.schema

        def load():
            try:
                timeline = load_timeline(path, can_id, profile, schema)
            except (ReplayError, ValueError) as error:
                emit(SourceStatus("error", f"replay failed: {error}"))
                return
            emit(ReplayLoaded(timeline))

        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=load,
            daemon=True,
            name="replay-loader",
        )
        self._set_source_status("connecting", f"loading {path.name}")
        self.worker.start()

    def _open_replay(self, timeline):
        self.player = ReplayPlayer(
            timeline,
            self.args.replay_speed,
            loop=getattr(self.args, "replay_loop", False),
        )
        self._replay_seek(0.0, keep_recording=True)
        self.player.play(time.monotonic())
        self._set_source_status(
            "connected",
            f"replay {timeline.path.name}, {timeline.kind}, "
            f"{format_replay_time(timeline.duration)}",
        )
        self._sync_replay_bar()

    def _process_item(self, item, now):
        if isinstance(item, SnapshotRecord):
            return self.model.process_record(item, now)
        return self.model.process_frame(item, now)

    def _replay_seek(self, target, keep_recording=False):
        """Rebuild the model at a source time of the loaded replay.

        A recording holds one continuous time line, so a seek ends it unless
        the replay has just opened.
        """
        player = self.player
        if player is None:
            return
        if not keep_recording:
            self.stop_recording()
        host = time.monotonic()
        first, last = player.seek(target, host)
        timeline = player.timeline
        self._new_model(timeline.can_id)
        self.model.drive = timeline.drive_at(first)
        for index in range(first, last):
            item_now = player.host_time(timeline.times[index], host)
            self._process_item(timeline.item(index, item_now), item_now)
        for history in self.hero_history.values():
            history.clear()

    def _advance_replay(self, now):
        player = self.player
        timeline = player.timeline
        first, last, ended = player.advance(now)
        new_snapshot = False
        for index in range(first, last):
            item_now = player.host_time(timeline.times[index], now)
            item = timeline.item(index, item_now)
            if self._process_item(item, item_now) is not None:
                new_snapshot = True
                self._record_snapshot(item, item_now)
        if ended:
            if player.loop:
                self._replay_seek(player.region()[0])
            else:
                player.pause()
                self._sync_replay_controls()
        return new_snapshot

    def toggle_play(self):
        player = self.player
        if player is None:
            return
        if player.playing:
            player.pause()
        else:
            if player.at_stop():
                self._replay_seek(player.region()[0])
            player.play(time.monotonic())
        self._sync_replay_controls()

    def toggle_loop(self):
        if self.player is not None:
            self.player.loop = not self.player.loop
            self._sync_replay_controls()

    def toggle_loop_in(self):
        player = self.player
        if player is None:
            return
        if player.loop_in is None:
            player.set_loop_in()
        else:
            player.loop_in = None
        self._sync_replay_controls()

    def toggle_loop_out(self):
        player = self.player
        if player is None:
            return
        if player.loop_out is None:
            player.set_loop_out()
        else:
            player.loop_out = None
        self._sync_replay_controls()

    def cycle_speed(self):
        player = self.player
        if player is not None:
            player.set_speed(next_speed(player.speed), time.monotonic())
            self._sync_replay_controls()

    def replay_step(self, seconds):
        if self.player is not None:
            self._replay_seek(self.player.position + seconds)

    def reset_acceleration(self):
        self.model.drive.acceleration.reset_results()

    @staticmethod
    def _typing(event):
        return isinstance(event.widget, (tk.Entry, tk.Text, ttk.Entry))

    def _on_replay_key_play(self, event):
        if self.player is None or self._typing(event):
            return None
        self.toggle_play()
        return "break"

    def _on_replay_key_step(self, event, direction):
        if self.player is None or self._typing(event):
            return None
        self.replay_step(direction * REPLAY_STEP_SECONDS)
        return "break"

    def _on_replay_key_home(self, event):
        if self.player is None or self._typing(event):
            return None
        self._replay_seek(self.player.region()[0])
        return "break"

    @staticmethod
    def _default_recording_name():
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return f"{timestamp}_{PRODUCT_SLUG}-v{__version__}"

    def toggle_recording(self):
        if self.recorder is None:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self, path=None):
        if self.recorder is not None:
            return
        interactive = path is None
        if interactive:
            path = filedialog.asksaveasfilename(
                title="Save MLVLG recording",
                defaultextension=".mlg",
                initialfile=self._default_recording_name(),
                filetypes=(("MegaLogViewer log", "*.mlg"), ("All files", "*.*")),
            )
            if not path:
                return
        output = Path(path)
        force = False
        if output.exists():
            if not interactive:
                self.record_var.set(f"MLG error: {output.name} already exists")
                return
            force = messagebox.askyesno(
                "Replace MLVLG recording",
                f"Replace existing file?\n{output}",
            )
            if not force:
                return
        try:
            self.recorder = TelemetryMlgRecorder(
                output,
                self.args.profile,
                time.time(),
                force=force,
                schema_path=self.args.schema,
            )
        except (OSError, ValueError) as error:
            self.record_var.set(f"MLG error: {error}")
            LOG.error("recording not started: %s", error)
            return
        self.recording_clock = FrameClock(time.monotonic())
        self._sync_record_button()
        self.record_var.set(f"MLG: recording {output.name}")
        LOG.info("recording to %s", output)

    def stop_recording(self):
        if self.recorder is None:
            return
        recorder = self.recorder
        self.recorder = None
        self.recording_clock = None
        self._sync_record_button()
        try:
            summary = recorder.close()
        except (OSError, ValueError) as error:
            recorder.abort()
            self.record_var.set(f"MLG error: {error}")
            LOG.error("recording not saved: %s", error)
            return
        if summary.event_records:
            self.record_var.set(
                f"MLG: saved {summary.output.name}, "
                f"{summary.event_records} snapshots"
            )
            LOG.info(
                "recording saved: %s, %d snapshots",
                summary.output,
                summary.event_records,
            )
        else:
            detail = (
                "existing file unchanged"
                if summary.output_existed
                else "file not created"
            )
            self.record_var.set(f"MLG: no complete snapshots, {detail}")

    def stop_source(self):
        self.stop_recording()
        self.player = None
        self._sync_replay_bar()
        self.source_generation += 1
        if self.stop_event is not None:
            self.stop_event.set()
        if self.worker is not None and self.worker.is_alive():
            self.worker.join(timeout=0.3)
        while True:
            try:
                self.events.get_nowait()
            except queue.Empty:
                break
        self.stop_event = None
        self.worker = None
        self.control_requests = None
        self.pcan_active = False
        self._set_stream_command("start")
        if self.source_state not in {"stopped", "error"}:
            self._set_source_status("stopped", "source stopped")

    def _set_source_status(self, state, detail):
        if (state, detail) != (self.source_state, self.source_detail):
            log = LOG.error if state == "error" else LOG.info
            log("source %s: %s", state, detail)
        self.source_state = state
        self.source_detail = detail
        self.source_var.set(f"Source: {detail}")

    def _poll(self):
        now = time.monotonic()
        processed = 0
        new_snapshot = False
        while processed < 4000:
            try:
                envelope = self.events.get_nowait()
            except queue.Empty:
                break
            processed += 1
            if not isinstance(envelope, SourceEnvelope):
                continue
            if envelope.generation != self.source_generation:
                continue
            event = envelope.event
            if isinstance(event, SourceStatus):
                self._set_source_status(event.state, event.detail)
                if event.state == "connected":
                    # Live frames carry source time from the moment the
                    # source opened; the bus silence before the first frame
                    # tells a controller start from a running stream.
                    self.model.clock = FrameClock(now)
                if event.state in {"stopped", "error"}:
                    self.stop_recording()
            elif isinstance(event, ControlStatus):
                sent = event.state == "sent"
                prefix = "Control" if sent else "Control error"
                self.control_var.set(f"{prefix}: {event.detail}")
                (LOG.info if sent else LOG.error)(
                    "control %s: %s",
                    event.command,
                    event.detail,
                )
                if sent and event.command in {"start", "stop"}:
                    self._set_stream_command(
                        "stop" if event.command == "start" else "start"
                    )
            elif isinstance(event, ReplayLoaded):
                self._open_replay(event.timeline)
            elif isinstance(event, FrameRecord):
                if self.model.process_frame(event) is not None:
                    new_snapshot = True
                    self._record_snapshot(event, now)
        if self.player is not None:
            new_snapshot = self._advance_replay(now) or new_snapshot
        if new_snapshot and self.feed is not None:
            self.feed.publish(self.model)
            self.feed_var.set(f"Feed: {self.feed.status()}")
        self.root.after(POLL_INTERVAL_MS, self._poll)

    def _record_snapshot(self, item, now):
        if self.recorder is None:
            return
        elapsed = self.recording_clock.elapsed(item, now)
        if elapsed is None:
            return
        try:
            self.recorder.append(self.model, elapsed)
        except (OSError, ValueError) as error:
            self.recorder.abort()
            self.recorder = None
            self.recording_clock = None
            self._sync_record_button()
            self.record_var.set(f"MLG error: {error}")
            LOG.error("recording aborted: %s", error)

    def _refresh_tick(self):
        """Paint the window on a timer of its own.

        The drain of the source queue and the painting of the window keep
        separate timers, because a painting driven from the drain can only
        land on a drain tick: a platform that rounds a timer up to its own
        step then carries the painting to the next tick after the one it
        was asked for, and the window is painted at half the rate the
        interval names.
        """
        self._refresh(time.monotonic())
        self.root.after(REFRESH_INTERVAL_MS, self._refresh_tick)

    def _metric_value(self, key):
        if key == "selected_map":
            return self.model.selected_map
        if key in RUN_METRICS:
            run = self.model.drive.acceleration.run(RUN_METRICS[key])
            return None if run.last is None else run.last.seconds
        if key == "rpm":
            return self.model.value("rpm", self.model.stock_rpm)
        if key == "stock_rpm":
            return self.model.stock_rpm
        if key == "vehicle_speed_kmh":
            return self.model.vehicle_speed_kmh
        if key == "gear":
            return self.model.gear
        if key == "ascd_button":
            return self.model.ascd_button
        if key == "dashboard_state":
            return self.model.dashboard_state
        if key == "context_name":
            return self.model.context_name
        if key in {"gps_lat", "gps_lon", "gps_status"}:
            return getattr(self.model, key)
        if key == "injection_average_ms":
            values = [
                self.model.value(f"injection_{index}_ms")
                for index in range(6)
            ]
            values = [
                value
                for value in values
                if isinstance(value, (int, float)) and math.isfinite(value)
            ]
            return sum(values) / len(values) if values else None
        return self.model.value(key)

    @staticmethod
    def _format(metric, value):
        if value is None:
            return "--"
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)) and not math.isfinite(value):
            return "--"
        if metric.hexadecimal:
            width = 4 if value > 0xFF else 2
            return f"0x{int(value):0{width}X}"
        if metric.digits == 0:
            return f"{value:.0f}"
        return f"{value:.{metric.digits}f}"

    def _refresh_panels(self, index):
        """Write the current values into the panels of one tab."""
        for panel, metrics in self.tab_panels[index]:
            for metric in metrics:
                value = self._metric_value(metric.key)
                text = self._format(metric, value)
                if text != "--" and metric.unit:
                    text = f"{text} {metric.unit}"
                panel.set_value(metric.key, text)

    def _refresh(self, now):
        stats = self.model.stats(now)
        age = stats.last_snapshot_age
        palette = self.palette
        if self.source_state == "error":
            state, color = "ERROR", palette.red
        elif self.source_state not in {"connected"}:
            state, color = self.source_state.upper(), palette.muted
        elif self.player is not None and not self.player.playing:
            state, color = "PAUSED", palette.amber
        elif age is None:
            state, color = f"WAITING FOR 0x{self.model.can_id:03X}", palette.amber
        elif age > 0.5:
            state, color = f"STALE {age:.1f}s", palette.red
        elif not self.model.schema_verified:
            state, color = "WAITING FOR HEALTH CONTEXT", palette.amber
        else:
            state, color = "LIVE", palette.green
        self.status_var.set(state)
        if color != self.status_dot_color:
            self.status_dot_color = color
            self.status_dot.configure(fg=color)
        self.status_field.set_foreground(color)
        self._sync_source_button()
        self.schema_var.set(
            "Schema: VERIFIED" if self.model.schema_verified else "Schema: waiting"
        )
        self.rate_var.set(
            f"Groups: {stats.snapshot_hz:5.1f} Hz | Frames: {stats.telemetry_frame_hz:6.1f} Hz"
        )
        self.loss_var.set(
            f"Loss: {stats.missed_snapshots} | Incomplete: {stats.incomplete_groups} | "
            f"Malformed: {stats.malformed_frames} | Restarts: {stats.producer_restarts} | "
            f"Source drops: {self.source_drops}"
        )

        new_group = stats.completed_groups != self.last_ui_group
        self.last_ui_group = stats.completed_groups
        for key, card in self.hero_cards.items():
            metric = card.metric
            value = self._metric_value(key)
            card.update_value(
                self._format(metric, value),
                value if new_group and isinstance(value, (int, float)) else None,
            )
        self._refresh_panels(self.active_tab)
        self._refresh_drive()
        self._refresh_replay()

        flags = self.model.telemetry_status_flags
        active_flags = ",".join(
            name for name, active in flags.items() if active
        )
        for key, value in (
            ("tick", self.model.last_tick if self.model.last_tick is not None else "--"),
            ("groups", stats.completed_groups),
            ("mismatch", stats.schema_mismatches),
            ("errors", stats.error_frames),
            ("overrun", self.model.raw.get("snapshot_overrun_count", "--")),
            ("tx_abort", self.model.raw.get("tx_abort_count", "--")),
            ("flags", active_flags or "none"),
        ):
            self.health_vars[key].set(f"{key}={value}")

    def close(self):
        """Save the recording, release the source and the feed, end the window.

        Every way out of the window leads here: the close button, the quit
        command of the platform, and the return of the main loop. The first
        one to arrive does the work, because a recording is saved once and a
        destroyed window cannot be destroyed again.
        """
        if self.closed:
            return
        self.closed = True
        LOG.info("window closed")
        self.stop_source()
        if self.feed is not None:
            self.feed.close()
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("--channel", default="PCAN_USBBUS1")
    parser.add_argument("--bitrate", type=int, default=DEFAULT_BITRATE)
    parser.add_argument("--can-id", type=lambda value: int(value, 0), default=DEFAULT_CAN_ID)
    parser.add_argument(
        "--schema",
        type=Path,
        default=can_telemetry.DEFAULT_SCHEMA,
        help="ROM-neutral telemetry wire-schema JSON",
    )
    parser.add_argument("--profile", default="tuning")
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument(
        "--listen-only",
        action="store_true",
        help="open PCAN without transmission or ACK participation",
    )
    parser.add_argument(
        "--reset-channel",
        action=argparse.BooleanOptionalAction,
        default=sys.platform == "darwin",
        help="release the PCAN-Basic channel before and after use (default on macOS)",
    )
    parser.add_argument("--demo", action="store_true")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--pcan-driver-check",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--settings",
        type=Path,
        help="presentation settings file (default: the per-user file)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="log file of this run (default: the per-user file beside the "
        "settings file)",
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="run without a log file",
    )
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--replay-speed", type=float, default=1.0)
    parser.add_argument(
        "--replay-loop",
        action="store_true",
        help="repeat the replay from its start when it ends",
    )
    parser.add_argument("--no-auto-connect", action="store_true")
    parser.add_argument(
        "--record",
        type=Path,
        help="start MLVLG recording to this new file",
    )
    parser.add_argument(
        "--publish-udp",
        metavar="[HOST:]PORT",
        help="send live engineering values to this UDP endpoint in this run, "
        "whatever the stored feed setting says",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.bitrate <= 0:
        raise SystemExit("bitrate must be positive")
    if not 1 <= args.can_id <= 0x7FE:
        raise SystemExit("data CAN ID must be in 0x001..0x7FE")
    if not 1 <= args.tick_divisor <= 0xFF:
        raise SystemExit("tick divisor must be in 1..255")
    if not math.isfinite(args.replay_speed) or args.replay_speed <= 0:
        raise SystemExit("replay speed must be positive")
    try:
        if args.publish_udp is not None:
            args.publish_udp = parse_endpoint(args.publish_udp)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.pcan_driver_check:
        from tools.can_dashboard.sources import _check_pcan_driver

        _check_pcan_driver()
        return 0
    if args.smoke_test:
        args.demo = True
        args.no_auto_connect = True
        args.settings = None
        args.no_log_file = True
    elif args.settings is None:
        args.settings = dashboard_settings.default_path(
            PRODUCT_NAME,
            PRODUCT_SLUG,
        )
    if args.no_log_file:
        args.log_file = None
    else:
        if args.log_file is None:
            args.log_file = dashboard_log.default_path(
                PRODUCT_NAME,
                PRODUCT_SLUG,
            )
        dashboard_log.configure(args.log_file)
    root = tk.Tk()
    dashboard_log.install_hooks(LOG, root)
    LOG.info(
        "start %s %s, python %s on %s, profile %s, CAN ID 0x%03X",
        PRODUCT_NAME,
        __version__,
        sys.version.split()[0],
        sys.platform,
        args.profile,
        args.can_id,
    )
    dashboard = DashboardApp(root, args)
    if args.smoke_test:
        root.withdraw()
        root.after(1500, root.quit)
        root.mainloop()
        completed_groups = dashboard.model.stats(
            time.monotonic()
        ).completed_groups
        dashboard.close()
        if completed_groups == 0:
            raise SystemExit("dashboard smoke test received no complete groups")
        return 0
    root.mainloop()
    dashboard.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
