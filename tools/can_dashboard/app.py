#!/usr/bin/env python3
"""Windows-oriented live dashboard for the JK08A custom CAN stream."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
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

from tools.can_dashboard import __version__
from tools.can_dashboard.model import (
    DEFAULT_BITRATE,
    DEFAULT_CAN_ID,
    DashboardModel,
    FrameRecord,
)
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.can_dashboard.sources import (
    PcanConfiguration,
    SourceStatus,
    run_demo,
    run_pcan,
    run_replay,
)


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


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    unit: str = ""
    digits: int = 1
    hexadecimal: bool = False


HERO_METRICS = (
    Metric("rpm", "ENGINE SPEED", "RPM", 0),
    Metric("vehicle_speed_kmh", "VEHICLE SPEED", "km/h*", 1),
    Metric("calculated_load_percent", "CALCULATED LOAD", "%", 1),
    Metric("timing_command_deg", "TIMING COMMAND", "deg*", 0),
    Metric("maf_total_g_s", "TOTAL AIRFLOW", "g/s*", 2),
    Metric("injection_average_ms", "INJECTION CALC", "ms*", 2),
    Metric("coolant_deg_c", "COOLANT", "degC*", 0),
    Metric("gear", "SELECTOR", "", 0),
)

PANELS = (
    ("Air and fuel", (
        Metric("maf_b1_v", "MAF bank 1", "V*", 3),
        Metric("maf_b2_v", "MAF bank 2", "V*", 3),
        Metric("bfs_ms", "BFS", "ms*", 3),
        Metric("af_b1_raw", "A/F bank 1", "raw", 0),
        Metric("af_b2_raw", "A/F bank 2", "raw", 0),
        Metric("af_state_factor", "A/F state factor", "", 4),
        Metric("stft_b1_percent", "STFT bank 1", "%", 2),
        Metric("stft_b2_percent", "STFT bank 2", "%", 2),
        Metric("ltft_b1_percent", "LTFT bank 1", "%", 2),
        Metric("ltft_b2_percent", "LTFT bank 2", "%", 2),
    )),
    ("Ignition, throttle, and CVTC", (
        Metric("apc_command_raw", "APC command", "raw", 0),
        Metric("app1_v", "APP 1", "V*", 3),
        Metric("app2_v", "APP 2", "V*", 3),
        Metric("tps_b1_v", "TPS bank 1", "V*", 3),
        Metric("tps_b2_v", "TPS bank 2", "V*", 3),
        Metric("absolute_throttle_raw", "Absolute throttle", "raw", 0),
        Metric("intake_cvtc_actual_b1_deg_ca", "CVTC actual B1", "degCA*", 1),
        Metric("intake_cvtc_actual_b2_deg_ca", "CVTC actual B2", "degCA*", 1),
        Metric("intake_cvtc_target_b1_raw", "CVTC target B1", "raw", 0),
        Metric("intake_cvtc_target_b2_raw", "CVTC target B2", "raw", 0),
        Metric("intake_cvtc_duty_b1_percent", "CVTC duty B1", "%", 1),
        Metric("intake_cvtc_duty_b2_percent", "CVTC duty B2", "%", 1),
    )),
    ("Injection and knock", (
        Metric("injection_0_ms", "Injection calc 0", "ms*", 2),
        Metric("injection_1_ms", "Injection calc 1", "ms*", 2),
        Metric("injection_2_ms", "Injection calc 2", "ms*", 2),
        Metric("injection_3_ms", "Injection calc 3", "ms*", 2),
        Metric("injection_4_ms", "Injection calc 4", "ms*", 2),
        Metric("injection_5_ms", "Injection calc 5", "ms*", 2),
        Metric("fuel_inhibit_mask", "Fuel inhibit mask", "", 0, True),
        Metric("knock_timing_state_raw", "Knock timing state", "", 0, True),
        Metric("knock_surface_state", "Knock surface", "", 0, True),
        Metric("knock_count_latched", "Knock interval count", "", 0),
        Metric("knock_channel_mask_latched", "Knock channel mask", "", 0, True),
    )),
    ("Temperatures and context", (
        Metric("iat_deg_c", "Intake air", "degC*", 0),
        Metric("fuel_temperature_deg_c", "Fuel temperature", "degC*", 0),
        Metric("oil_temperature_deg_c", "Oil temperature", "degC*", 0),
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


class Sparkline(tk.Canvas):
    def __init__(self, master, color=BLUE, **kwargs):
        super().__init__(
            master,
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
            tk.Label(
                self,
                textvariable=variable,
                bg=PANEL,
                fg=TEXT,
                font=("Consolas", 10),
            ).grid(row=row, column=1, sticky="e", padx=(6, 12), pady=2)

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
        self.source_state = "stopped"
        self.source_detail = "not connected"
        self.model = DashboardModel(args.profile, args.can_id, args.tick_divisor)
        self.recorder = None
        self.recording_started_monotonic = None
        self.last_ui_group = 0
        self.hero_cards = {}
        self.data_panels = []
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
        self.root.title(f"JK08A CAN Telemetry v{__version__}")
        self.root.configure(bg=BG)
        self.root.geometry("1520x920")
        self.root.minsize(1180, 760)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI Semibold", 9), padding=(10, 6))
        style.configure("TCheckbutton", background=BG, foreground=TEXT)

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(
            top,
            text=f"JK08A CAN TELEMETRY v{__version__}",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI Semibold", 17),
        ).pack(side="left")
        self.status_dot = tk.Label(top, text="●", bg=BG, fg=MUTED, font=("Segoe UI", 17))
        self.status_dot.pack(side="left", padx=(18, 5))
        self.status_var = tk.StringVar(value="DISCONNECTED")
        tk.Label(
            top,
            textvariable=self.status_var,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI Semibold", 10),
        ).pack(side="left")

        controls = tk.Frame(top, bg=BG)
        controls.pack(side="right")
        self.channel_var = tk.StringVar(value=self.args.channel)
        self.can_id_var = tk.StringVar(value=f"0x{self.args.can_id:03X}")
        self.listen_only_var = tk.BooleanVar(value=not self.args.active)
        self._control_entry(controls, "Channel", self.channel_var, 15)
        self._control_entry(controls, "CAN ID", self.can_id_var, 8)
        ttk.Checkbutton(
            controls,
            text="Listen-only",
            variable=self.listen_only_var,
        ).pack(side="left", padx=8)
        ttk.Button(controls, text="Connect", command=self.start_pcan).pack(side="left", padx=3)
        ttk.Button(controls, text="Demo", command=self.start_demo).pack(side="left", padx=3)
        ttk.Button(controls, text="Replay", command=self.select_replay).pack(side="left", padx=3)
        ttk.Button(controls, text="Stop", command=self.stop_source).pack(side="left", padx=3)
        self.record_button = ttk.Button(
            controls,
            text="Record MLG",
            command=self.toggle_recording,
        )
        self.record_button.pack(side="left", padx=(9, 3))

        telemetry_bar = tk.Frame(self.root, bg=PANEL_ALT, highlightbackground=BORDER, highlightthickness=1)
        telemetry_bar.pack(fill="x", padx=14, pady=(0, 9))
        self.source_var = tk.StringVar(value="Source: not connected")
        self.schema_var = tk.StringVar(value="Schema: waiting")
        self.rate_var = tk.StringVar(value="Groups: 0.0 Hz | Frames: 0.0 Hz")
        self.loss_var = tk.StringVar(value="Loss: 0 | Incomplete: 0 | Malformed: 0")
        self.record_var = tk.StringVar(value="MLG: idle")
        for variable, color in (
            (self.source_var, TEXT),
            (self.schema_var, AMBER),
            (self.rate_var, CYAN),
            (self.loss_var, MUTED),
        ):
            tk.Label(
                telemetry_bar,
                textvariable=variable,
                bg=PANEL_ALT,
                fg=color,
                font=("Consolas", 9),
            ).pack(side="left", padx=12, pady=7)
        tk.Label(
            telemetry_bar,
            textvariable=self.record_var,
            bg=PANEL_ALT,
            fg=AMBER,
            font=("Consolas", 9),
        ).pack(side="right", padx=12, pady=7)

        heroes = tk.Frame(self.root, bg=BG)
        heroes.pack(fill="x", padx=14)
        colors = (GREEN, BLUE, PURPLE, CYAN, AMBER, RED, TEXT, BLUE)
        for column, (metric, color) in enumerate(zip(HERO_METRICS, colors)):
            heroes.columnconfigure(column, weight=1, uniform="hero")
            card = HeroCard(heroes, metric, color)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 5, 0))
            self.hero_cards[metric.key] = card

        panels = tk.Frame(self.root, bg=BG)
        panels.pack(fill="both", expand=True, padx=14, pady=9)
        for column in range(4):
            panels.columnconfigure(column, weight=1, uniform="panel")
        panels.rowconfigure(0, weight=1)
        for column, (title, metrics) in enumerate(PANELS):
            panel = DataPanel(panels, title, metrics)
            panel.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 6, 0))
            self.data_panels.append((panel, metrics))

        self.health_var = tk.StringVar(value="No telemetry groups received")
        tk.Label(
            self.root,
            textvariable=self.health_var,
            bg=PANEL_ALT,
            fg=MUTED,
            font=("Consolas", 9),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 4), ipady=6)
        tk.Label(
            self.root,
            text="* Target-correlated or candidate transform. Timing is a software command; injection is a compensated command, not a measured electrical duration.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 8))

    @staticmethod
    def _control_entry(parent, label, variable, width):
        group = tk.Frame(parent, bg=BG)
        group.pack(side="left", padx=4)
        tk.Label(group, text=label, bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
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

    def _emit(self, event):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            self.source_drops += 1

    def _new_model(self, can_id):
        self.model = DashboardModel(
            self.args.profile,
            can_id,
            self.args.tick_divisor,
        )
        self.last_ui_group = 0
        self.source_drops = 0

    def start_pcan(self):
        try:
            can_id = int(self.can_id_var.get(), 0)
            if not 1 <= can_id <= 0x7FF:
                raise ValueError
        except ValueError:
            self._set_source_status("error", "CAN ID must be in 0x001..0x7FF")
            return
        channel = self.channel_var.get().strip()
        if not channel:
            self._set_source_status("error", "PCAN channel is empty")
            return
        self.stop_source()
        self._new_model(can_id)
        config = PcanConfiguration(
            channel=channel,
            bitrate=self.args.bitrate,
            can_id=can_id,
            listen_only=self.listen_only_var.get(),
        )
        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_pcan,
            args=(config, self.stop_event, self._emit),
            daemon=True,
            name="pcan-reader",
        )
        self._set_source_status("connecting", f"opening {channel}")
        self.worker.start()

    def start_demo(self):
        try:
            can_id = int(self.can_id_var.get(), 0)
        except ValueError:
            can_id = self.args.can_id
            self.can_id_var.set(f"0x{can_id:03X}")
        self.stop_source()
        self._new_model(can_id)
        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_demo,
            args=(can_id, self.stop_event, self._emit),
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
        can_id = int(self.can_id_var.get(), 0)
        self._new_model(can_id)
        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_replay,
            args=(Path(path), self.stop_event, self._emit, self.args.replay_speed),
            daemon=True,
            name="telemetry-replay",
        )
        self.worker.start()

    @staticmethod
    def _default_recording_name():
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return f"{timestamp}_jk08a-can-v{__version__}.mlg"

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
            )
        except (OSError, ValueError) as error:
            self.record_var.set(f"MLG error: {error}")
            return
        self.recording_started_monotonic = time.monotonic()
        self.record_button.configure(text="Stop MLG")
        self.record_var.set(f"MLG: recording {output.name}")

    def stop_recording(self):
        if self.recorder is None:
            return
        recorder = self.recorder
        self.recorder = None
        self.recording_started_monotonic = None
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
            self.record_var.set("MLG: no complete snapshots, file not created")

    def stop_source(self):
        self.stop_recording()
        if self.stop_event is not None:
            self.stop_event.set()
        if self.worker is not None and self.worker.is_alive():
            self.worker.join(timeout=0.3)
        self.stop_event = None
        self.worker = None
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
                event = self.events.get_nowait()
            except queue.Empty:
                break
            processed += 1
            if isinstance(event, SourceStatus):
                self._set_source_status(event.state, event.detail)
                if event.state in {"stopped", "error"}:
                    self.stop_recording()
            elif isinstance(event, FrameRecord):
                snapshot = self.model.process_frame(event)
                if snapshot is not None and self.recorder is not None:
                    event_time = (
                        event.received_monotonic
                        if event.received_monotonic is not None
                        else now
                    )
                    elapsed = max(
                        0.0,
                        event_time - self.recording_started_monotonic,
                    )
                    try:
                        self.recorder.append(self.model, elapsed)
                    except (OSError, ValueError) as error:
                        self.recorder.abort()
                        self.recorder = None
                        self.recording_started_monotonic = None
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
            values = [value for value in values if value is not None]
            return sum(values) / len(values) if values else None
        return self.model.value(key)

    @staticmethod
    def _format(metric, value):
        if value is None:
            return "--"
        if isinstance(value, str):
            return value
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
        health = (
            f"tick={self.model.last_tick if self.model.last_tick is not None else '--'} | "
            f"groups={stats.completed_groups} | schema_mismatch={stats.schema_mismatches} | "
            f"error_frames={stats.error_frames} | overrun={self.model.raw.get('snapshot_overrun_count', '--')} | "
            f"tx_abort={self.model.raw.get('tx_abort_count', '--')} | "
            f"status_flags={','.join(name for name, active in flags.items() if active) or 'none'}"
        )
        self.health_var.set(health)

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
    parser.add_argument("--profile", choices=("core32", "wide54"), default="wide54")
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument("--active", action="store_true", help="participate in ACK instead of listen-only")
    parser.add_argument("--demo", action="store_true")
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
    if not 1 <= args.can_id <= 0x7FF:
        raise SystemExit("CAN ID must be in 0x001..0x7FF")
    if not 1 <= args.tick_divisor <= 0xFF:
        raise SystemExit("tick divisor must be in 1..255")
    if args.replay_speed <= 0:
        raise SystemExit("replay speed must be positive")
    root = tk.Tk()
    DashboardApp(root, args)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
