"""Dialog that turns the live value feed on and sets it up for RomRaider."""

from __future__ import annotations

import tkinter as tk

from tools.can_dashboard import live_feed
from tools.can_dashboard.settings import FeedSettings
from tools.can_dashboard.widgets import ToolButton


REFERENCE_TABLE = "Fuelling / Load Model / Internal Load Normalization Reference"
INTRODUCTION = (
    "RomRaider Logger receives these values and Overlay Log outlines the "
    "table cell at the live engine speed and load."
)
REFERENCE_HINT = (
    f"The value of the RomRaider table {REFERENCE_TABLE} in the flashed ROM. "
    "Without it the feed leaves VQ Engine Load out."
)
PLUGIN_HINT = (
    "RomRaider learns the parameters from this file when Logger starts. "
    "Install it once, and again after the endpoint changes."
)
# Plugin file state -> (caption, color role).
PLUGIN_STATES = {
    "current": ("installed for this endpoint", "ok"),
    "outdated": ("installed for other settings", "error"),
    "missing": ("not installed", "error"),
    None: ("", "muted"),
}


def endpoint_text(host, port):
    return f"{host}:{port}"


def reference_text(bfs_reference):
    """Show the reference as RomRaider shows its table: milliseconds.

    RomRaider shows three decimals. One word is 1/2048 ms, so a fourth decimal
    is added when the word needs it to read back unchanged.
    """
    if bfs_reference is None:
        return ""
    milliseconds = live_feed.reference_ms(bfs_reference)
    for digits in (3, 4):
        text = f"{milliseconds:.{digits}f}"
        if round(float(text) * live_feed.BFS_RAW_PER_MS) == bfs_reference:
            break
    return text


def parse_reference(text):
    """Return the reference word of the typed milliseconds; empty is none."""
    text = text.strip().replace(",", ".")
    if not text:
        return None
    try:
        milliseconds = float(text)
    except ValueError as error:
        raise ValueError(
            "load reference is not a number of milliseconds"
        ) from error
    return live_feed.reference_from_ms(milliseconds)


def parse_form(enabled, endpoint, reference):
    """Build feed settings from the dialog fields or raise ValueError."""
    host, port = live_feed.parse_endpoint(endpoint)
    return FeedSettings(
        enabled=bool(enabled),
        host=host,
        port=port,
        bfs_reference=parse_reference(reference),
    )


class FeedDialog(tk.Toplevel):
    """One place for the feed: the switch, the endpoint, the load reference."""

    def __init__(
        self,
        master,
        *,
        feed,
        colors,
        button_colors,
        fonts,
        on_apply,
        tooltip_options=None,
        plugin_path=None,
    ):
        super().__init__(master, bg=colors["bg"])
        self.title("RomRaider live value feed")
        self.transient(master)
        self.resizable(False, False)
        self._colors = colors
        self._on_apply = on_apply
        self.plugin_path = (
            live_feed.plugin_path() if plugin_path is None else plugin_path
        )
        self.enabled = feed.enabled
        self.endpoint_var = tk.StringVar(
            self, value=endpoint_text(feed.host, feed.port)
        )
        self.reference_var = tk.StringVar(
            self, value=reference_text(feed.bfs_reference)
        )
        self.message_var = tk.StringVar(self)
        self.plugin_var = tk.StringVar(self)

        def button(parent, text, command, tooltip, **options):
            return ToolButton(
                parent,
                text=text,
                command=command,
                colors=button_colors,
                tooltip=tooltip,
                tooltip_options=tooltip_options,
                font=fonts["button"],
                **options,
            )

        self._note(INTRODUCTION, fonts["label"], colors["text"]).pack(
            fill="x", padx=12, pady=(12, 8)
        )
        switch = tk.Frame(self, bg=colors["bg"])
        switch.pack(fill="x", padx=12)
        self.publish_button = button(
            switch,
            "PUBLISH",
            self.toggle_enabled,
            "Publish the values of every received snapshot",
            lit=self.enabled,
        )
        self.publish_button.pack(side="left")

        form = tk.Frame(self, bg=colors["bg"])
        form.pack(fill="x", padx=12, pady=(10, 0))
        form.columnconfigure(1, weight=1)
        self.endpoint_entry = self._field(
            form, 0, "UDP ENDPOINT", self.endpoint_var, fonts
        )
        self.reference_entry = self._field(
            form, 1, "100 % LOAD, MS", self.reference_var, fonts
        )
        self._note(REFERENCE_HINT, fonts["label"], colors["muted"]).pack(
            fill="x", padx=12, pady=(6, 0)
        )

        plugin = tk.Frame(self, bg=colors["bg"])
        plugin.pack(fill="x", padx=12, pady=(12, 0))
        button(
            plugin,
            "INSTALL PLUGIN",
            self.install_plugin,
            f"Write {self.plugin_path}",
        ).pack(side="left")
        self.plugin_label = tk.Label(
            plugin,
            textvariable=self.plugin_var,
            bg=colors["bg"],
            fg=colors["muted"],
            font=fonts["label"],
            anchor="w",
        )
        self.plugin_label.pack(side="left", padx=(10, 0))
        self._note(
            f"{self.plugin_path}\n{PLUGIN_HINT}",
            fonts["label"],
            colors["muted"],
        ).pack(fill="x", padx=12, pady=(6, 0))

        self.message_label = tk.Label(
            self,
            textvariable=self.message_var,
            bg=colors["bg"],
            fg=colors["muted"],
            font=fonts["label"],
            anchor="w",
            justify="left",
            wraplength=440,
        )
        self.message_label.pack(fill="x", padx=12, pady=(10, 0))

        actions = tk.Frame(self, bg=colors["bg"])
        actions.pack(fill="x", padx=12, pady=12)
        button(
            actions,
            "CANCEL",
            self.destroy,
            "Close without changes",
        ).pack(side="right")
        button(
            actions,
            "APPLY",
            self.apply,
            "Use these settings now and remember them",
            lit=True,
        ).pack(side="right", padx=(0, 6))
        self.bind("<Escape>", lambda _event: self.destroy(), add="+")
        self.bind("<Return>", lambda _event: self.apply(), add="+")
        self.endpoint_var.trace_add(
            "write", lambda *_args: self.show_plugin_state()
        )
        self.show_plugin_state()

    def _note(self, text, font, color):
        return tk.Label(
            self,
            text=text,
            bg=self._colors["bg"],
            fg=color,
            font=font,
            anchor="w",
            justify="left",
            wraplength=440,
        )

    def _field(self, form, row, label, variable, fonts):
        colors = self._colors
        tk.Label(
            form,
            text=label,
            bg=colors["bg"],
            fg=colors["heading"],
            font=fonts["heading"],
            anchor="w",
        ).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=3)
        entry = tk.Entry(
            form,
            textvariable=variable,
            width=24,
            bg=colors["panel"],
            fg=colors["text"],
            insertbackground=colors["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["select"],
            font=fonts["entry"],
        )
        entry.grid(row=row, column=1, sticky="w", pady=3, ipady=2)
        return entry

    def _report(self, text, role):
        self.message_var.set(text)
        self.message_label.configure(fg=self._colors[role])

    def _form(self):
        return parse_form(
            self.enabled,
            self.endpoint_var.get(),
            self.reference_var.get(),
        )

    def toggle_enabled(self):
        self.enabled = not self.enabled
        self.publish_button.configure(lit=self.enabled)

    def plugin_state(self):
        """State of the plugin file for the typed endpoint; None if invalid."""
        try:
            host, port = live_feed.parse_endpoint(self.endpoint_var.get())
        except ValueError:
            return None
        return live_feed.plugin_state(self.plugin_path, host, port)

    def show_plugin_state(self):
        caption, role = PLUGIN_STATES[self.plugin_state()]
        self.plugin_var.set(caption)
        self.plugin_label.configure(fg=self._colors[role])

    def install_plugin(self):
        try:
            host, port = live_feed.parse_endpoint(self.endpoint_var.get())
        except ValueError as error:
            self._report(str(error), "error")
            return None
        try:
            path = live_feed.install_plugin(self.plugin_path, host, port)
        except OSError as error:
            self._report(f"Plugin file was not written: {error}", "error")
            return None
        self.show_plugin_state()
        self._report("Plugin file written. Restart RomRaider Logger.", "ok")
        return path

    def apply(self):
        try:
            feed = self._form()
        except ValueError as error:
            self._report(str(error), "error")
            return
        self.destroy()
        self._on_apply(feed)
