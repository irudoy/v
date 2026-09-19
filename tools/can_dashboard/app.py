#!/usr/bin/env python3
"""Cross-platform live dashboard for VQ custom CAN telemetry."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import math
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import PRODUCT_NAME, PRODUCT_SLUG, __version__
from tools.can_dashboard.model import (
    DEFAULT_BITRATE,
    DEFAULT_CAN_ID,
    DashboardModel,
    FrameRecord,
)
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.can_dashboard.sources import (
    ControlRequest,
    ControlStatus,
    PcanConfiguration,
    SourceStatus,
    run_demo,
    run_pcan,
    run_replay,
)
from tools.can_dashboard.widgets import (
    Cluster,
    FlowBar,
    ResponsiveGrid,
    ScrollableFrame,
    StatusField,
)
from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


BG = "#0d1117"
PANEL = "#161b22"
PANEL_ALT = "#1d2430"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
GREEN = "#3fb950"
AMBER = "#d29922"
RED = "#f85149"
BLUE = "#58a6ff"
CYAN = "#39c5cf"
PURPLE = "#bc8cff"

PREFERRED_WINDOW_WIDTH = 1520
PREFERRED_WINDOW_HEIGHT = 920
MIN_WINDOW_WIDTH = 560
MIN_WINDOW_HEIGHT = 460
HERO_MIN_WIDTH = 164
HERO_SPARKLINE_WIDTH = 140
PANEL_MIN_WIDTH = 268
PANEL_VALUE_WIDTH = 150
NOTEBOOK_TAB_PADDING = 8
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
    event: SourceStatus | ControlStatus | FrameRecord


def _parse_standard_can_id(value: str) -> int:
    try:
        can_id = int(value, 0)
    except (TypeError, ValueError) as error:
        raise ValueError("data CAN ID must be in 0x001..0x7FE") from error
    if not 1 <= can_id <= 0x7FE:
        raise ValueError("data CAN ID must be in 0x001..0x7FE")
    return can_id


RECORDING_CLOCK_TOLERANCE_SECONDS = 1.0


def _finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


class RecordingClock:
    """Elapsed seconds of one MLVLG recording, measured on the frame clock.

    A data block carries a 10 us timestamp, so a record must hold the time its
    frame reached the interface: the host dequeue time collapses a burst
    drained from the driver queue onto a single tick. Elapsed time starts at
    the offset of the first recorded frame from the recording start and then
    advances by the interface step, or by the host receive step when the source
    reports no frame time. An interface clock that steps backwards, or ahead of
    the host clock by more than the queueing tolerance, is abandoned without
    breaking elapsed time.
    """

    def __init__(self, started: float):
        self.started = started
        self.source_clock = False
        self._source_time = None
        self._host_time = None
        self._elapsed = 0.0

    def elapsed(self, frame: FrameRecord, fallback: float):
        host_time = (
            frame.received_monotonic
            if _finite(frame.received_monotonic)
            else fallback
        )
        if not _finite(self.started) or not _finite(host_time):
            return None
        if host_time < self.started:
            return None
        source_time = (
            frame.timestamp
            if _finite(frame.timestamp) and frame.timestamp >= 0.0
            else None
        )
        if self._host_time is None:
            self.source_clock = source_time is not None
            self._source_time = source_time
            self._host_time = host_time
            self._elapsed = host_time - self.started
            return self._elapsed
        host_step = max(host_time - self._host_time, 0.0)
        source_step = (
            source_time - self._source_time
            if self.source_clock
            and source_time is not None
            and self._source_time is not None
            else None
        )
        if source_step is None:
            step = host_step
        elif 0.0 <= source_step <= host_step + RECORDING_CLOCK_TOLERANCE_SECONDS:
            step = source_step
        else:
            self.source_clock = False
            step = host_step
        self._source_time = source_time
        self._host_time = host_time
        self._elapsed += step
        return self._elapsed


HERO_METRICS = (
    Metric("rpm", "ENGINE SPEED", "RPM", 0),
    Metric("vehicle_speed_kmh", "VEHICLE SPEED", "km/h", 1),
    Metric("calculated_load_percent", "CALCULATED LOAD", "%", 1),
    Metric("timing_command_deg", "TIMING COMMAND", "degBTDC", 0),
    Metric("maf_total_g_s", "TOTAL AIRFLOW", "g/s", 2),
    Metric("injection_average_ms", "INJECTION CALC", "ms", 2),
    Metric("coolant_deg_c", "COOLANT", "degC", 0),
    Metric("gear", "SELECTOR", "", 0),
)

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
    )),
    ("Temperatures and context", (
        Metric("iat_deg_c", "Intake air", "degC", 0),
        Metric("fuel_temperature_deg_c", "Fuel temperature", "degC", 0),
        Metric("oil_temperature_deg_c", "Oil temperature", "degC", 0),
        Metric("timing_state_2023_raw", "Timing state 2023", "", 0, True),
        Metric("timing_state_564c_raw", "Timing state 564C", "", 0, True),
        Metric("stock_rpm", "Stock CAN RPM", "RPM", 0),
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
        Metric("injection_timing_state_raw", "Injection timing state", "raw", 0),
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
        Metric("secondary_tps_b1_raw", "Secondary TPS B1", "raw", 0),
        Metric("secondary_tps_b2_raw", "Secondary TPS B2", "raw", 0),
        Metric("af_adjustment_b1_raw", "A/F adjustment B1", "raw", 0, True),
        Metric("af_adjustment_b2_raw", "A/F adjustment B2", "raw", 0, True),
        Metric("protocol_version", "Protocol version", "", 0),
        Metric("profile_crc16", "Profile CRC16", "", 0, True),
    )),
)


class Sparkline(tk.Canvas):
    def __init__(self, master, color=BLUE, **kwargs):
        super().__init__(
            master,
            width=HERO_SPARKLINE_WIDTH,
            height=46,
            background=PANEL,
            highlightthickness=0,
            **kwargs,
        )
        self.color = color
        self.values = deque(maxlen=180)
        self.bind("<Configure>", lambda _event: self.redraw())

    def push(self, value):
        if isinstance(value, (int, float)):
            self.values.append(float(value))
            self.redraw()

    def redraw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        self.create_line(0, height - 1, width, height - 1, fill=BORDER)
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
    def __init__(self, master, metric, color):
        super().__init__(master, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.metric = metric
        self.value_var = tk.StringVar(value="--")
        self.unit_var = tk.StringVar(value=metric.unit)
        tk.Label(
            self,
            text=metric.label,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w", padx=12, pady=(10, 0))
        value_row = tk.Frame(self, bg=PANEL)
        value_row.pack(fill="x", padx=12)
        tk.Label(
            value_row,
            textvariable=self.value_var,
            bg=PANEL,
            fg=color,
            font=("Segoe UI Semibold", 23),
        ).pack(side="left")
        tk.Label(
            value_row,
            textvariable=self.unit_var,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(6, 0), pady=(10, 0))
        self.sparkline = Sparkline(self, color=color)
        self.sparkline.pack(fill="x", padx=8, pady=(0, 7))

    def update_value(self, text, numeric=None):
        self.value_var.set(text)
        if numeric is not None:
            self.sparkline.push(numeric)


class DataPanel(tk.Frame):
    def __init__(self, master, title, metrics):
        super().__init__(master, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.variables = {}
        tk.Label(
            self,
            text=title.upper(),
            bg=PANEL,
            fg=BLUE,
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 8))
        self.columnconfigure(0, weight=1)
        for row, metric in enumerate(metrics, start=1):
            tk.Label(
                self,
                text=metric.label,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 9),
            ).grid(row=row, column=0, sticky="w", padx=(12, 6), pady=2)
            variable = tk.StringVar(value="--")
            self.variables[metric.key] = variable
            field = StatusField(
                self,
                variable,
                title=metric.label,
                background=PANEL,
                foreground=TEXT,
                font=("Consolas", 10),
                copy_feedback=GREEN,
                anchor="e",
                reserve=PANEL_VALUE_WIDTH,
            )
            field.grid(row=row, column=1, sticky="e", padx=(6, 12), pady=2)

    def set_value(self, key, value):
        self.variables[key].set(value)


class DashboardApp:
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
        self.last_ui_group = 0
        self.stream_command = "start"
        self.source_button_active = False
        self.hero_cards = {}
        self.data_panels = []
        self.panel_grids = []
        self._build_window()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(50, self._poll)
        if args.demo:
            self.root.after(200, self.start_demo)
        elif args.replay:
            self.root.after(200, lambda: self.start_replay(args.replay))
        elif not args.no_auto_connect:
            self.root.after(300, self.start_pcan)
        if args.record is not None:
            self.root.after(500, lambda: self.start_recording(args.record))

    def _build_window(self):
        self.root.title(f"{PRODUCT_NAME} v{__version__}")
        self.root.configure(bg=BG)
        self._apply_initial_geometry()
        self._configure_styles()
        self._build_header()
        self._build_status_bar()
        self._build_health_bar()
        self._build_content()

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
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI Semibold", 9), padding=(10, 6))
        style.configure("TCheckbutton", background=BG, foreground=TEXT)
        style.configure(
            "Dashboard.Vertical.TScrollbar",
            background=PANEL_ALT,
            troughcolor=BG,
            bordercolor=BORDER,
            arrowcolor=MUTED,
            darkcolor=PANEL_ALT,
            lightcolor=PANEL_ALT,
        )
        style.map(
            "Dashboard.Vertical.TScrollbar",
            background=[("active", BORDER)],
        )

    def _build_header(self):
        header = FlowBar(self.root, bg=BG, spacing_x=8, spacing_y=8)
        header.pack(side="top", fill="x", padx=14, pady=(12, 8))
        header.add(tk.Label(
            header,
            text=f"{PRODUCT_NAME.upper()} v{__version__}",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI Semibold", 17),
        ))

        link = Cluster(header, bg=BG)
        self.status_dot = tk.Label(
            link,
            text="\u25cf",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 17),
        )
        self.status_dot.pack(side="left", padx=(6, 5))
        self.status_var = tk.StringVar(value="DISCONNECTED")
        self.status_field = StatusField(
            link,
            self.status_var,
            title="Link state",
            background=BG,
            foreground=MUTED,
            font=("Segoe UI Semibold", 10),
            copy_feedback=GREEN,
        )
        self.status_field.pack(side="left")
        header.add(link)

        self.channel_var = tk.StringVar(value=self.args.channel)
        self.can_id_var = tk.StringVar(value=f"0x{self.args.can_id:03X}")
        self.listen_only_var = tk.BooleanVar(value=not self.args.active)
        header.add(
            self._control_entry(header, "Channel", self.channel_var, 15),
            align="right",
        )
        header.add(
            self._control_entry(header, "CAN ID", self.can_id_var, 8),
            align="right",
        )
        header.add(
            ttk.Checkbutton(
                header,
                text="Listen-only",
                variable=self.listen_only_var,
            ),
            align="right",
        )
        self.source_button = ttk.Button(
            header,
            text="Connect",
            command=self.toggle_source,
        )
        header.add(self.source_button, align="right")
        header.add(
            ttk.Button(header, text="Demo", command=self.start_demo),
            align="right",
        )
        header.add(
            ttk.Button(header, text="Replay", command=self.select_replay),
            align="right",
        )
        self.stream_button = ttk.Button(
            header,
            text=self._stream_button_text(),
            command=self.toggle_stream,
        )
        header.add(self.stream_button, align="right")
        self.record_button = ttk.Button(
            header,
            text="Record MLG",
            command=self.toggle_recording,
        )
        header.add(self.record_button, align="right")

    def _build_status_bar(self):
        bar = FlowBar(
            self.root,
            bg=PANEL_ALT,
            highlightbackground=BORDER,
            highlightthickness=1,
            spacing_x=14,
            spacing_y=4,
            pad_x=12,
            pad_y=7,
        )
        bar.pack(side="top", fill="x", padx=14, pady=(0, 9))
        self.source_var = tk.StringVar(value="Source: not connected")
        self.schema_var = tk.StringVar(value="Schema: waiting")
        self.rate_var = tk.StringVar(value="Groups: 0.0 Hz | Frames: 0.0 Hz")
        self.loss_var = tk.StringVar(value="Loss: 0 | Incomplete: 0 | Malformed: 0")
        self.control_var = tk.StringVar(value="Control: idle")
        self.record_var = tk.StringVar(value="MLG: idle")
        for variable, title, color, align, sample in (
            (
                self.source_var,
                "Telemetry source",
                TEXT,
                "left",
                "Source: PCAN_USBBUS1, 500000 bit/s",
            ),
            (self.schema_var, "Wire schema state", AMBER, "left", "Schema: VERIFIED"),
            (
                self.rate_var,
                "Group and frame rates",
                CYAN,
                "left",
                "Groups: 100.0 Hz | Frames: 1000.0 Hz",
            ),
            (
                self.loss_var,
                "Loss and integrity counters",
                MUTED,
                "left",
                "Loss: 0 | Incomplete: 0 | Malformed: 0 | Source drops: 0",
            ),
            (
                self.control_var,
                "Last stream command",
                CYAN,
                "right",
                "Control error: connect PCAN first",
            ),
            (
                self.record_var,
                "MLG recording",
                AMBER,
                "right",
                "MLG: recording telemetry.mlg",
            ),
        ):
            bar.add(
                self._status_field(
                    bar,
                    variable,
                    title,
                    color,
                    sample,
                    anchor="e" if align == "right" else "w",
                ),
                align=align,
            )

    def _build_health_bar(self):
        bar = FlowBar(
            self.root,
            bg=PANEL_ALT,
            spacing_x=14,
            spacing_y=4,
            pad_x=12,
            pad_y=6,
        )
        bar.pack(side="bottom", fill="x", padx=14, pady=(0, 8))
        self.health_vars = {}
        for key, title, sample in HEALTH_FIELDS:
            variable = tk.StringVar(value=f"{key}=--")
            self.health_vars[key] = variable
            bar.add(self._status_field(bar, variable, title, MUTED, sample))

    def _build_content(self):
        content = ScrollableFrame(self.root, background=BG)
        content.pack(side="top", fill="both", expand=True)
        body = content.content

        heroes = ResponsiveGrid(
            body,
            min_column_width=HERO_MIN_WIDTH,
            spacing=5,
            uniform="hero",
            bg=BG,
        )
        heroes.pack(fill="x", padx=14)
        colors = (GREEN, BLUE, PURPLE, CYAN, AMBER, RED, TEXT, BLUE)
        for metric, color in zip(HERO_METRICS, colors):
            self.hero_cards[metric.key] = heroes.add(
                HeroCard(heroes, metric, color)
            )

        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True, padx=14, pady=9)
        notebook.bind("<Configure>", self._layout_panel_grids, add="+")
        for tab_name, definitions in (
            ("Primary", PANELS),
            ("Extended", EXTENDED_PANELS),
        ):
            panels = ResponsiveGrid(
                notebook,
                min_column_width=PANEL_MIN_WIDTH,
                spacing=6,
                uniform="panel",
                row_weight=1,
                bg=BG,
            )
            notebook.add(panels, text=tab_name)
            self.panel_grids.append(panels)
            for title, metrics in definitions:
                panel = panels.add(DataPanel(panels, title, metrics))
                self.data_panels.append((panel, metrics))

        self.footnote = tk.Label(
            body,
            text=FOOTNOTE,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 8),
            anchor="w",
            justify="left",
        )
        self.footnote.pack(fill="x", padx=15, pady=(0, 8))
        self.footnote.bind("<Configure>", self._wrap_footnote, add="+")

    def _layout_panel_grids(self, event):
        for panels in self.panel_grids:
            panels.layout(event.width - NOTEBOOK_TAB_PADDING)

    def _wrap_footnote(self, event):
        wrap = max(240, event.width - 4)
        if wrap != self.footnote.cget("wraplength"):
            self.footnote.configure(wraplength=wrap)

    def _status_field(self, master, variable, title, color, sample, anchor="w"):
        return StatusField(
            master,
            variable,
            title=title,
            background=PANEL_ALT,
            foreground=color,
            font=("Consolas", 9),
            copy_feedback=GREEN,
            anchor=anchor,
            sample=sample,
        )

    @staticmethod
    def _control_entry(parent, label, variable, width):
        group = tk.Frame(parent, bg=BG)
        tk.Label(
            group,
            text=label,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w")
        tk.Entry(
            group,
            textvariable=variable,
            width=width,
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Consolas", 9),
        ).pack(ipady=4)
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
        return self.worker is not None and self.worker.is_alive()

    def _sync_source_button(self):
        active = self.source_is_active()
        if active == self.source_button_active:
            return
        self.source_button_active = active
        self.source_button.configure(text="Disconnect" if active else "Connect")

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
            listen_only=self.listen_only_var.get(),
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
        return f"{self.stream_command.capitalize()} stream"

    def _set_stream_command(self, command):
        self.stream_command = command
        self.stream_button.configure(text=self._stream_button_text())

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
                "Control error: reconnect with Listen-only disabled"
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
            title="Select PEAK TRC 1.1 or compact candump log",
            filetypes=(
                ("PEAK trace", "*.trc"),
                ("candump log", "*.log *.txt"),
                ("All files", "*.*"),
            ),
        )
        if path:
            self.start_replay(Path(path))

    def start_replay(self, path):
        self.stop_source()
        can_id = self._selected_can_id()
        if can_id is None:
            return
        self._new_model(can_id)
        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_replay,
            args=(
                Path(path),
                self.stop_event,
                self._source_emitter(),
                self.args.replay_speed,
            ),
            daemon=True,
            name="telemetry-replay",
        )
        self.worker.start()

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
            return
        self.recording_clock = RecordingClock(time.monotonic())
        self.record_button.configure(text="Stop MLG")
        self.record_var.set(f"MLG: recording {output.name}")

    def stop_recording(self):
        if self.recorder is None:
            return
        recorder = self.recorder
        self.recorder = None
        self.recording_clock = None
        self.record_button.configure(text="Record MLG")
        try:
            summary = recorder.close()
        except (OSError, ValueError) as error:
            recorder.abort()
            self.record_var.set(f"MLG error: {error}")
            return
        if summary.event_records:
            self.record_var.set(
                f"MLG: saved {summary.output.name}, "
                f"{summary.event_records} snapshots"
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
        self.source_state = state
        self.source_detail = detail
        self.source_var.set(f"Source: {detail}")

    def _poll(self):
        now = time.monotonic()
        processed = 0
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
                if event.state in {"stopped", "error"}:
                    self.stop_recording()
            elif isinstance(event, ControlStatus):
                prefix = "Control" if event.state == "sent" else "Control error"
                self.control_var.set(f"{prefix}: {event.detail}")
                if event.state == "sent" and event.command in {"start", "stop"}:
                    self._set_stream_command(
                        "stop" if event.command == "start" else "start"
                    )
            elif isinstance(event, FrameRecord):
                snapshot = self.model.process_frame(event)
                if snapshot is not None and self.recorder is not None:
                    elapsed = self.recording_clock.elapsed(event, now)
                    if elapsed is None:
                        continue
                    try:
                        self.recorder.append(self.model, elapsed)
                    except (OSError, ValueError) as error:
                        self.recorder.abort()
                        self.recorder = None
                        self.recording_clock = None
                        self.record_button.configure(text="Record MLG")
                        self.record_var.set(f"MLG error: {error}")
        self._refresh(now)
        self.root.after(50, self._poll)

    def _metric_value(self, key):
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

    def _refresh(self, now):
        stats = self.model.stats(now)
        age = stats.last_snapshot_age
        if self.source_state == "error":
            state, color = "ERROR", RED
        elif self.source_state not in {"connected"}:
            state, color = self.source_state.upper(), MUTED
        elif age is None:
            state, color = f"WAITING FOR 0x{self.model.can_id:03X}", AMBER
        elif age > 0.5:
            state, color = f"STALE {age:.1f}s", RED
        elif not self.model.schema_verified:
            state, color = "WAITING FOR HEALTH CONTEXT", AMBER
        else:
            state, color = "LIVE", GREEN
        self.status_var.set(state)
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
            f"Malformed: {stats.malformed_frames} | Source drops: {self.source_drops}"
        )

        new_group = stats.completed_groups != self.last_ui_group
        self.last_ui_group = stats.completed_groups
        for metric in HERO_METRICS:
            value = self._metric_value(metric.key)
            card = self.hero_cards[metric.key]
            card.update_value(
                self._format(metric, value),
                value if new_group and isinstance(value, (int, float)) else None,
            )
        for panel, metrics in self.data_panels:
            for metric in metrics:
                value = self._metric_value(metric.key)
                text = self._format(metric, value)
                if text != "--" and metric.unit:
                    text = f"{text} {metric.unit}"
                panel.set_value(metric.key, text)

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
        self.stop_source()
        self.root.destroy()


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
    parser.add_argument("--active", action="store_true", help="participate in ACK instead of listen-only")
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
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--replay-speed", type=float, default=1.0)
    parser.add_argument("--no-auto-connect", action="store_true")
    parser.add_argument(
        "--record",
        type=Path,
        help="start MLVLG recording to this new file",
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
    if args.pcan_driver_check:
        from tools.can_dashboard.sources import _check_pcan_driver

        _check_pcan_driver()
        return 0
    if args.smoke_test:
        args.demo = True
        args.no_auto_connect = True
    root = tk.Tk()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
