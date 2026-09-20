"""Responsive presentation widgets for the telemetry dashboard."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


ELLIPSIS = "..."
SCROLLBAR_RESERVE = 14
RELAYOUT_DELAY_MS = 16
WHEEL_NOTCH = 120.0
WHEEL_PIXELS = 60
TOUCHPAD_PIXELS = 20
TOUCHPAD_INTERVAL = 5


def elide(text, measure, available, ellipsis=ELLIPSIS):
    """Shorten text with a trailing ellipsis until it fits a pixel width."""
    if not text or available <= 0 or measure(text) <= available:
        return text
    low = 0
    high = len(text)
    shortened = ellipsis
    while low <= high:
        middle = (low + high) // 2
        candidate = text[:middle].rstrip() + ellipsis
        if measure(candidate) <= available:
            shortened = candidate
            low = middle + 1
        else:
            high = middle - 1
    return shortened


def row_width(widths, spacing):
    """Return the width one row of items needs, gaps included."""
    if not widths:
        return 0
    return sum(widths) + spacing * (len(widths) - 1)


def wrap_rows(widths, available, spacing):
    """Group item indexes into rows that stay inside the available width."""
    rows = []
    current = []
    used = 0
    for index, width in enumerate(widths):
        needed = width if not current else width + spacing
        if current and used + needed > available:
            rows.append(tuple(current))
            current = [index]
            used = width
            continue
        current.append(index)
        used += needed
    if current:
        rows.append(tuple(current))
    return tuple(rows)


def responsive_columns(count, minimum_width, available, spacing):
    """Return how many equal columns of at least minimum_width fit."""
    if count <= 0:
        return 0
    if available <= 0 or minimum_width <= 0:
        return count
    columns = (available + spacing) // (minimum_width + spacing)
    return max(1, min(count, int(columns)))


HERO_VALUE_SIZES = ((170, 22), (130, 18), (100, 15), (76, 12))
HERO_VALUE_SIZE_FLOOR = 10


def hero_value_size(width):
    """Return the value font size a hero card of this pixel width uses."""
    for minimum, size in HERO_VALUE_SIZES:
        if width >= minimum:
            return size
    return HERO_VALUE_SIZE_FLOOR


class Tooltip:
    """Hover bubble that reports the full text behind a widget."""

    def __init__(
        self,
        widget,
        provider,
        *,
        delay=400,
        background="#1d2430",
        foreground="#e6edf3",
        border="#30363d",
        font=("Segoe UI", 9),
        wraplength=520,
    ):
        self.widget = widget
        self.provider = provider
        self.delay = delay
        self.background = background
        self.foreground = foreground
        self.border = border
        self.font = font
        self.wraplength = wraplength
        self._scheduled = None
        self._window = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<Destroy>", self.hide, add="+")

    def _schedule(self, _event=None):
        self.hide()
        self._scheduled = self.widget.after(self.delay, self.show)

    def show(self):
        self._scheduled = None
        text = self.provider() if callable(self.provider) else self.provider
        if not text or self._window is not None:
            return
        window = tk.Toplevel(self.widget)
        window.wm_overrideredirect(True)
        window.configure(bg=self.border)
        tk.Label(
            window,
            text=text,
            bg=self.background,
            fg=self.foreground,
            font=self.font,
            justify="left",
            anchor="w",
            wraplength=self.wraplength,
            padx=8,
            pady=5,
        ).pack(padx=1, pady=1)
        window.update_idletasks()
        self._window = window
        self._place(window)

    def _place(self, window):
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        if x + width > self.widget.winfo_screenwidth():
            x = max(0, self.widget.winfo_screenwidth() - width - 8)
        if y + height > self.widget.winfo_screenheight():
            y = max(0, self.widget.winfo_rooty() - height - 6)
        window.wm_geometry(f"+{int(x)}+{int(y)}")

    def hide(self, _event=None):
        if self._scheduled is not None:
            try:
                self.widget.after_cancel(self._scheduled)
            except tk.TclError:
                pass
            self._scheduled = None
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
            self._window = None


class StatusField(tk.Label):
    """Status value that elides to the bar width and copies on click."""

    def __init__(
        self,
        master,
        variable,
        *,
        title,
        background,
        foreground,
        font=("Consolas", 9),
        copy_feedback=None,
        tooltip_hint="Click to copy",
        anchor="w",
        sample=None,
        reserve=0,
        tooltip_options=None,
    ):
        super().__init__(
            master,
            bg=background,
            fg=foreground,
            font=font,
            anchor=anchor,
            cursor="hand2",
        )
        self.title = title
        self.variable = variable
        self.tooltip_hint = tooltip_hint
        self._font = tkfont.Font(root=master, font=font)
        self._unit = max(1, self._font.measure("0"))
        self._reserved = self._font.measure(sample) if sample else reserve
        self._foreground = foreground
        self._copy_feedback = copy_feedback or foreground
        self._available = 0
        self._text = ""
        self._flash = None
        self._trace = variable.trace_add("write", self._on_variable)
        self.bind("<Button-1>", self.copy, add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")
        self.tooltip = Tooltip(
            self,
            self.tooltip_text,
            **(tooltip_options or {}),
        )
        self.set_text(variable.get())

    def _on_variable(self, *_args):
        self.set_text(self.variable.get())

    def set_text(self, text):
        if text == self._text:
            return
        self._text = text
        self._apply()

    def set_available_width(self, width):
        if width == self._available:
            return
        self._available = width
        self._apply()

    def _apply(self):
        limit = self._available
        if self._reserved:
            limit = self._reserved if limit <= 0 else min(limit, self._reserved)
        text = elide(self._text, self._font.measure, limit)
        if self._reserved:
            self.configure(text=text, width=max(1, -(-limit // self._unit)))
        else:
            self.configure(text=text)

    @property
    def text(self):
        return self._text

    def set_foreground(self, color):
        if color == self._foreground:
            return
        self._foreground = color
        if self._flash is None:
            self.configure(fg=color)

    def tooltip_text(self):
        return f"{self.title}\n{self._text}\n{self.tooltip_hint}"

    def copy(self, _event=None):
        self.clipboard_clear()
        self.clipboard_append(self._text)
        self.configure(fg=self._copy_feedback)
        if self._flash is not None:
            self.after_cancel(self._flash)
        self._flash = self.after(600, self._restore_foreground)
        return "break"

    def _restore_foreground(self):
        self._flash = None
        self.configure(fg=self._foreground)

    def _on_destroy(self, _event=None):
        try:
            self.variable.trace_remove("write", self._trace)
        except (tk.TclError, ValueError):
            pass
        if self._flash is not None:
            try:
                self.after_cancel(self._flash)
            except tk.TclError:
                pass
            self._flash = None


class Cluster(tk.Frame):
    """Group of widgets that stays together inside a flow bar."""

    def set_available_width(self, width):
        for child in self.winfo_children():
            setter = getattr(child, "set_available_width", None)
            if setter is not None:
                setter(width)


class FlowBar(tk.Frame):
    """Row of widgets that wraps into more rows when the width is short."""

    def __init__(
        self,
        master,
        *,
        spacing_x=10,
        spacing_y=6,
        pad_x=0,
        pad_y=0,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._spacing_x = spacing_x
        self._spacing_y = spacing_y
        self._pad_x = pad_x
        self._pad_y = pad_y
        self._items = []
        self._row_frames = []
        self._signature = None
        self._pending = None
        self.bind("<Configure>", self._on_configure, add="+")

    def add(self, widget, *, align="left"):
        self._items.append((widget, align))
        widget.bind("<Configure>", self._on_child_configure, add="+")
        self._request_layout()
        return widget

    @property
    def rows(self):
        return len(self._signature[1]) if self._signature is not None else 0

    def _on_configure(self, event):
        self.layout(event.width)

    def _on_child_configure(self, _event=None):
        self._request_layout()

    def _request_layout(self):
        if self._pending is not None:
            return
        self._pending = self.after(RELAYOUT_DELAY_MS, self._flush)

    def _flush(self):
        self._pending = None
        if self.winfo_exists():
            self.layout(self.winfo_width())

    def layout(self, available):
        if not self._items or available <= 1:
            return
        inner = max(0, available - 2 * self._pad_x)
        for widget, _align in self._items:
            setter = getattr(widget, "set_available_width", None)
            if setter is not None:
                setter(inner)
        widths = [widget.winfo_reqwidth() for widget, _align in self._items]
        single = row_width(widths, self._spacing_x) <= inner
        rows = (
            (tuple(range(len(widths))),)
            if single
            else wrap_rows(widths, inner, self._spacing_x)
        )
        signature = (single, rows)
        if signature == self._signature:
            return
        self._signature = signature
        self._place(rows, single)

    def _place(self, rows, single):
        while len(self._row_frames) < len(rows):
            self._row_frames.append(tk.Frame(self, bg=self.cget("bg")))
        for index, frame in enumerate(self._row_frames):
            if index < len(rows):
                frame.pack(
                    fill="x",
                    padx=self._pad_x,
                    pady=(self._pad_y if index == 0 else self._spacing_y // 2,
                          self._pad_y if index == len(rows) - 1 else 0),
                )
            else:
                frame.pack_forget()
        for row_index, row in enumerate(rows):
            frame = self._row_frames[row_index]
            members = [self._items[index] for index in row]
            for widget, _align in members:
                widget.pack_forget()
            for widget, align in members:
                if single and align == "right":
                    continue
                self._mount(widget, frame, "left", (0, self._spacing_x))
            if not single:
                continue
            for widget, align in reversed(members):
                if align != "right":
                    continue
                self._mount(widget, frame, "right", (self._spacing_x, 0))

    def _mount(self, widget, frame, side, padx):
        """Pack an item into a row frame and keep it above that frame.

        Items are siblings of the row frames, so a freshly created frame
        stacks over them and hides everything it holds until they are raised.
        """
        widget.pack(in_=frame, side=side, padx=padx)
        widget.lift()


class ResponsiveGrid(tk.Frame):
    """Grid that keeps every column at least min_column_width wide."""

    def __init__(
        self,
        master,
        *,
        min_column_width,
        spacing=6,
        uniform="cell",
        row_weight=0,
        min_from_children=True,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._min_column_width = min_column_width
        self._min_from_children = min_from_children
        self._spacing = spacing
        self._uniform = uniform
        self._row_weight = row_weight
        self._items = []
        self._columns = None
        self._pending = None
        self.bind("<Configure>", self._on_configure, add="+")

    def add(self, widget):
        self._items.append(widget)
        self._columns = None
        widget.bind("<Configure>", self._on_child_configure, add="+")
        self._request_layout()
        return widget

    def _on_configure(self, event):
        self.layout(event.width)

    def _on_child_configure(self, _event=None):
        self._request_layout()

    def _request_layout(self):
        if self._pending is not None:
            return
        self._pending = self.after(RELAYOUT_DELAY_MS, self._flush)

    def _flush(self):
        self._pending = None
        if self.winfo_exists():
            self.layout(self.winfo_width())

    @property
    def columns(self):
        return self._columns

    def minimum_column_width(self):
        if not self._min_from_children:
            return self._min_column_width
        widths = [widget.winfo_reqwidth() for widget in self._items]
        return max(self._min_column_width, max(widths, default=0))

    def layout(self, available):
        if not self._items:
            return
        columns = responsive_columns(
            len(self._items),
            self.minimum_column_width(),
            available,
            self._spacing,
        )
        if columns == self._columns:
            return
        self._columns = columns
        used_columns, used_rows = self.grid_size()
        for column in range(used_columns):
            self.columnconfigure(column, weight=0, uniform="")
        for row in range(used_rows):
            self.rowconfigure(row, weight=0)
        for column in range(columns):
            self.columnconfigure(column, weight=1, uniform=self._uniform)
        rows = 0
        for index, widget in enumerate(self._items):
            row, column = divmod(index, columns)
            rows = max(rows, row + 1)
            widget.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else self._spacing, 0),
                pady=(0 if row == 0 else self._spacing, 0),
            )
        for row in range(rows):
            self.rowconfigure(row, weight=self._row_weight)


class ToolButton(tk.Label):
    """Flat toolbar button with a lit state, drawn the same on every OS.

    A native button ignores its colors on macOS, so the button is a label.
    `configure` accepts `lit` beside the label options; a lit button reports
    an active link, stream, recording, or mode.
    """

    def __init__(
        self,
        master,
        *,
        text,
        command,
        colors,
        tooltip=None,
        tooltip_options=None,
        font=("Segoe UI Semibold", 9),
        lit_role="lit",
        lit=False,
        padx=8,
        pady=3,
    ):
        self._colors = dict(colors)
        self._lit_role = lit_role
        self._lit = bool(lit)
        self._hover = False
        self._command = command
        super().__init__(
            master,
            text=text,
            font=font,
            padx=padx,
            pady=pady,
            cursor="hand2",
            takefocus=1,
            highlightthickness=1,
        )
        self._paint()
        self.bind("<Button-1>", self._on_click, add="+")
        self.bind("<Return>", self._on_click, add="+")
        self.bind("<space>", self._on_click, add="+")
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.tooltip = (
            Tooltip(self, tooltip, **(tooltip_options or {}))
            if tooltip
            else None
        )

    @property
    def lit(self):
        return self._lit

    def configure(self, cnf=None, **options):
        lit = options.pop("lit", None)
        result = None
        if cnf is not None or options or lit is None:
            result = super().configure(cnf, **options)
        if lit is not None and bool(lit) != self._lit:
            self._lit = bool(lit)
            self._paint()
        return result

    config = configure

    def invoke(self):
        return self._command()

    def _paint(self):
        colors = self._colors
        if self._lit:
            background = colors[self._lit_role]
            foreground = colors["lit_text"]
            border = background
        else:
            background = colors["hover" if self._hover else "face"]
            foreground = colors["text"]
            border = colors["border"]
        super().configure(
            bg=background,
            fg=foreground,
            highlightbackground=border,
            highlightcolor=colors["focus"],
        )

    def _on_click(self, _event=None):
        self.invoke()
        return "break"

    def _on_enter(self, _event=None):
        self._hover = True
        self._paint()

    def _on_leave(self, _event=None):
        self._hover = False
        self._paint()


class HeroRow(tk.Frame):
    """Single row of equal cards that shrink instead of wrapping.

    Every card carries half of the gap on each side, so equal columns give
    equal cards; `margin` is the width the row adds beyond its outer cards.
    """

    def __init__(self, master, *, spacing=6, min_card_width=48, **kwargs):
        super().__init__(master, **kwargs)
        self._spacing = spacing
        self._min_card_width = min_card_width
        self._cards = ()
        self._columns = 0

    @property
    def cards(self):
        return self._cards

    @property
    def margin(self):
        return self._spacing // 2

    def set_cards(self, cards):
        for card in self._cards:
            if card not in cards and card.winfo_exists():
                card.grid_forget()
        self._cards = tuple(cards)
        for column in range(max(self._columns, len(self._cards))):
            used = column < len(self._cards)
            self.columnconfigure(
                column,
                weight=1 if used else 0,
                uniform="hero" if used else "",
                minsize=self._min_card_width if used else 0,
            )
        self._columns = len(self._cards)
        self.rowconfigure(0, weight=1)
        for column, card in enumerate(self._cards):
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(self.margin, self._spacing - self.margin),
            )


class ScrollableFrame(tk.Frame):
    """Vertical scroller whose content keeps the viewport width."""

    def __init__(
        self,
        master,
        *,
        background,
        scrollbar_style="Dashboard.Vertical.TScrollbar",
        stretch=True,
        **kwargs,
    ):
        super().__init__(master, bg=background, **kwargs)
        self._stretch = stretch
        self.canvas = tk.Canvas(
            self,
            bg=background,
            highlightthickness=0,
            bd=0,
            takefocus=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            style=scrollbar_style,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content = tk.Frame(self.canvas, bg=background)
        self._window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=SCROLLBAR_RESERVE)
        self.rowconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self._content_height = None
        self._touchpad_events = 0
        self.content.bind("<Configure>", self._on_content_configure, add="+")
        self.canvas.bind("<Configure>", self._on_canvas_configure, add="+")
        self.bind_all("<MouseWheel>", self._on_wheel, add="+")
        self.bind_all("<Button-4>", self._on_wheel, add="+")
        self.bind_all("<Button-5>", self._on_wheel, add="+")
        try:
            self.bind_all("<TouchpadScroll>", self._on_touchpad, add="+")
        except tk.TclError:
            pass

    def _on_content_configure(self, _event=None):
        self._sync()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._window, width=event.width)
        self._sync()

    def _sync(self):
        viewport = self.canvas.winfo_height()
        required = self.content.winfo_reqheight()
        if self._stretch and viewport > 1:
            height = max(required, viewport)
            if height != self._content_height:
                self._content_height = height
                self.canvas.itemconfigure(self._window, height=height)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        needed = required > viewport
        if needed and not self.scrollbar.winfo_ismapped():
            self.scrollbar.grid(row=0, column=1, sticky="ns")
        elif not needed and self.scrollbar.winfo_ismapped():
            self.scrollbar.grid_remove()
            self.canvas.yview_moveto(0)

    def _contains(self, widget):
        while widget is not None:
            if widget is self:
                return True
            parent = widget.winfo_parent()
            if not parent:
                return False
            try:
                widget = widget.nametowidget(parent)
            except KeyError:
                return False
        return False

    def _targets(self, event):
        """Report whether a global scroll event belongs to this scroller.

        The bindings are global, so a destroyed scroller keeps receiving
        events. The scrollbar keeps its own stock bindings, so events over it
        are left alone instead of being scrolled twice.
        """
        try:
            if not self.winfo_exists() or not self.scrollbar.winfo_ismapped():
                return False
        except tk.TclError:
            return False
        widget = event.widget
        if isinstance(widget, str):
            try:
                widget = self.nametowidget(widget)
            except KeyError:
                return False
        if widget is self.scrollbar:
            return False
        return self._contains(widget)

    def _scroll_pixels(self, pixels):
        region = self.canvas.bbox("all")
        if not region:
            return
        span = region[3] - region[1]
        if span <= 0:
            return
        self.canvas.yview_moveto(self.canvas.yview()[0] + pixels / span)

    def _on_wheel(self, event):
        if not self._targets(event):
            return
        if event.num == 4:
            self._scroll_pixels(-WHEEL_PIXELS)
            return
        if event.num == 5:
            self._scroll_pixels(WHEEL_PIXELS)
            return
        notches = event.delta / WHEEL_NOTCH
        if abs(notches) < 0.1:
            notches = 1.0 if event.delta > 0 else -1.0
        self._scroll_pixels(-notches * WHEEL_PIXELS)

    def _on_touchpad(self, event):
        """Scroll a trackpad gesture, which Tk reports apart from the wheel.

        Tk packs both axes into the delta and fires about sixty events per
        second, so every fifth one is acted on, as the stock bindings do.
        """
        self._touchpad_events += 1
        if self._touchpad_events % TOUCHPAD_INTERVAL:
            return
        if not self._targets(event):
            return
        steps = event.delta & 0xFFFF
        if steps >= 0x8000:
            steps -= 0x10000
        if steps:
            self._scroll_pixels(-steps * TOUCHPAD_PIXELS)
