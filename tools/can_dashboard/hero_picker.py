"""Dialog that chooses the cards of the dashboard hero row."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from tools.can_dashboard.widgets import ToolButton


LIST_WIDTH_CHARS = 46
PICKER_MIN_WIDTH = 900
PICKER_MIN_HEIGHT = 440


@dataclass(frozen=True)
class HeroChoice:
    key: str
    label: str
    group: str

    @property
    def caption(self):
        return f"{self.group}: {self.label}"


class HeroSelection:
    """Ordered choice of hero cards out of a catalog, bounded by a limit."""

    def __init__(self, choices, selected, limit):
        self.choices = tuple(choices)
        self.limit = limit
        self._by_key = {choice.key: choice for choice in self.choices}
        self.selected = []
        self.replace(selected)

    def replace(self, keys):
        self.selected = []
        for key in keys:
            self.add(key)

    def choice(self, key):
        return self._by_key[key]

    def available(self):
        return tuple(
            choice.key
            for choice in self.choices
            if choice.key not in self.selected
        )

    @property
    def full(self):
        return len(self.selected) >= self.limit

    def add(self, key):
        if key not in self._by_key or key in self.selected or self.full:
            return False
        self.selected.append(key)
        return True

    def remove(self, key):
        if key not in self.selected:
            return False
        self.selected.remove(key)
        return True

    def move(self, key, offset):
        if key not in self.selected:
            return False
        index = self.selected.index(key)
        target = index + offset
        if not 0 <= target < len(self.selected):
            return False
        self.selected.insert(target, self.selected.pop(index))
        return True


class HeroPicker(tk.Toplevel):
    """Two lists: the catalog on the left, the shown cards on the right."""

    def __init__(
        self,
        master,
        *,
        choices,
        selected,
        defaults,
        limit,
        colors,
        button_colors,
        fonts,
        on_apply,
        tooltip_options=None,
        scrollbar_style="Dashboard.Vertical.TScrollbar",
    ):
        super().__init__(master, bg=colors["bg"])
        self.title("Hero row cards")
        self.transient(master)
        self.resizable(True, True)
        self.minsize(PICKER_MIN_WIDTH, PICKER_MIN_HEIGHT)
        self.selection = HeroSelection(choices, selected, limit)
        self._defaults = tuple(defaults)
        self._on_apply = on_apply
        self._colors = colors
        self._available_keys = ()
        self.count_var = tk.StringVar(self)

        tk.Label(
            self,
            textvariable=self.count_var,
            bg=colors["bg"],
            fg=colors["muted"],
            font=fonts["label"],
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 4))

        lists = tk.Frame(self, bg=colors["bg"])
        lists.pack(fill="both", expand=True, padx=12)
        lists.columnconfigure(0, weight=1, uniform="list")
        lists.columnconfigure(2, weight=1, uniform="list")
        lists.rowconfigure(1, weight=1)
        for column, text in ((0, "AVAILABLE"), (2, "SHOWN, LEFT TO RIGHT")):
            tk.Label(
                lists,
                text=text,
                bg=colors["bg"],
                fg=colors["heading"],
                font=fonts["heading"],
                anchor="w",
            ).grid(row=0, column=column, sticky="w", pady=(0, 3))
        self.available_list = self._listbox(lists, fonts, scrollbar_style, 0)
        self.shown_list = self._listbox(lists, fonts, scrollbar_style, 2)

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

        middle = tk.Frame(lists, bg=colors["bg"])
        middle.grid(row=1, column=1, padx=8, sticky="n")
        for text, command, tooltip in (
            ("ADD", self.add_selected, "Show the chosen metric as a card"),
            ("REMOVE", self.remove_selected, "Take the chosen card away"),
            ("UP", lambda: self.move_selected(-1), "Move the card to the left"),
            ("DOWN", lambda: self.move_selected(1), "Move the card to the right"),
        ):
            button(middle, text, command, tooltip).pack(fill="x", pady=(0, 4))

        actions = tk.Frame(self, bg=colors["bg"])
        actions.pack(fill="x", padx=12, pady=10)
        button(
            actions,
            "DEFAULTS",
            self.restore_defaults,
            "Restore the default cards",
        ).pack(side="left")
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
            "Show these cards and remember the choice",
            lit=True,
        ).pack(side="right", padx=(0, 6))

        self.available_list.bind("<Double-Button-1>", self._on_add, add="+")
        self.shown_list.bind("<Double-Button-1>", self._on_remove, add="+")
        self.bind("<Escape>", lambda _event: self.destroy(), add="+")
        self.render()

    def _listbox(self, master, fonts, scrollbar_style, column):
        colors = self._colors
        holder = tk.Frame(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
        )
        holder.grid(row=1, column=column, sticky="nsew")
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)
        listbox = tk.Listbox(
            holder,
            bg=colors["panel"],
            fg=colors["text"],
            selectbackground=colors["select"],
            selectforeground=colors["select_text"],
            font=fonts["list"],
            activestyle="none",
            exportselection=False,
            highlightthickness=0,
            borderwidth=0,
            height=14,
            width=LIST_WIDTH_CHARS,
        )
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            holder,
            orient="vertical",
            command=listbox.yview,
            style=scrollbar_style,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        listbox.configure(yscrollcommand=scrollbar.set)
        return listbox

    def render(self, *, select_shown=None, select_available=None):
        selection = self.selection
        self._available_keys = selection.available()
        self.available_list.delete(0, "end")
        for key in self._available_keys:
            self.available_list.insert("end", selection.choice(key).caption)
        self.shown_list.delete(0, "end")
        for key in selection.selected:
            self.shown_list.insert("end", selection.choice(key).caption)
        if select_shown is not None and selection.selected:
            index = max(0, min(select_shown, len(selection.selected) - 1))
            self.shown_list.selection_set(index)
            self.shown_list.see(index)
        if select_available is not None and self._available_keys:
            index = max(0, min(select_available, len(self._available_keys) - 1))
            self.available_list.selection_set(index)
            self.available_list.see(index)
        self.count_var.set(
            f"{len(selection.selected)} of {selection.limit} cards shown. "
            "Cards share one row and shrink to fit."
        )

    def _current(self, listbox, keys):
        chosen = listbox.curselection()
        if not chosen or chosen[0] >= len(keys):
            return None, None
        return chosen[0], keys[chosen[0]]

    def add_selected(self):
        index, key = self._current(self.available_list, self._available_keys)
        if key is not None and self.selection.add(key):
            self.render(
                select_shown=len(self.selection.selected) - 1,
                select_available=index,
            )

    def remove_selected(self):
        index, key = self._current(self.shown_list, self.selection.selected)
        if key is not None and self.selection.remove(key):
            self.render(select_shown=index)

    def move_selected(self, offset):
        index, key = self._current(self.shown_list, self.selection.selected)
        if key is not None and self.selection.move(key, offset):
            self.render(select_shown=index + offset)

    def restore_defaults(self):
        self.selection.replace(self._defaults)
        self.render()

    def apply(self):
        keys = tuple(self.selection.selected)
        self.destroy()
        self._on_apply(keys)

    def _on_add(self, _event=None):
        self.add_selected()
        return "break"

    def _on_remove(self, _event=None):
        self.remove_selected()
        return "break"
