"""Panels, hero cards, and hover descriptions of the dashboard metrics.

A telemetry field takes its place from its presentation in the schema: the
label, digits, panel, order within the panel, and description, with the
display unit of its scale. The quantities of the stock frames, the drive
runs, and the GPS source are code metrics with fixed places among them.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from tools.can_dashboard.descriptions import describe
from tools.logs import can_telemetry


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    unit: str = ""
    digits: int = 1
    hexadecimal: bool = False


# The hero cards in catalog order: a code metric, or the engineering key of a
# telemetry field, whose card shows its label in capitals.
HERO = (
    Metric("rpm", "ENGINE SPEED", "RPM", 0),
    Metric("vehicle_speed_kmh", "VEHICLE SPEED", "km/h", 1),
    "calculated_load",
    "final_timing",
    "maf_total",
    Metric("injection_average_ms", "INJECTION CALC", "ms", 2),
    "coolant",
    Metric("gear", "SELECTOR", "", 0),
    Metric("tcm_gear", "GEAR", "", 0),
    Metric("selected_map", "SELECTED MAP", "", 0),
    Metric("zero_to_100_s", "0-100 KM/H", "s", 2),
    Metric("hundred_to_200_s", "100-200 KM/H", "s", 2),
)
OPTIONAL_HERO_KEYS = frozenset({
    "gear",
    "tcm_gear",
    "selected_map",
    "zero_to_100_s",
    "hundred_to_200_s",
})
# The panels of each tab, by title.
TABS = (
    ("Primary", (
        "Air and fuel",
        "Ignition, throttle, and CVTC",
        "Injection and knock",
        "Temperatures and context",
    )),
    ("Extended", (
        "Torque and requests",
        "CVTC detail",
        "Trims and supply",
        "Throttle sensors and protocol",
        "Learning and knock state",
    )),
    ("Dynamic", (
        "Page configuration",
        "Dynamic page",
    )),
)
# The code metrics of each panel, each at its order among the telemetry
# fields of the panel.
PANEL_CODE_METRICS = {
    "Temperatures and context": (
        (40, Metric("stock_rpm", "Stock CAN RPM", "RPM", 0)),
        (50, Metric("gear", "Selector")),
        (60, Metric("tcm_gear", "Gear", "", 0)),
        (70, Metric("selected_map", "Selected map", "", 0)),
        (100, Metric("ascd_button", "ASCD input")),
        (110, Metric("dashboard_state", "Dashboard state")),
        (120, Metric("gps_lat", "GPS latitude", "deg", 6)),
        (130, Metric("gps_lon", "GPS longitude", "deg", 6)),
        (140, Metric("gps_status", "GPS source")),
    ),
    "Page configuration": (
        (10, Metric("page_configuration", "Active configuration")),
        (20, Metric("page_group", "Group", "", 0)),
        (30, Metric("page_request", "Requested configuration")),
        (40, Metric("page_echo", "Echo")),
        (50, Metric("page_undecoded", "Undecoded pages", "", 0)),
    ),
}


@dataclass(frozen=True)
class Presentation:
    """The metrics of one telemetry profile and where the dashboard shows
    them.

    ``tabs`` holds the panels of each tab as (title, metrics) pairs, and
    ``hero`` the hero metrics in catalog order.
    """

    tabs: tuple
    hero: tuple
    descriptions: dict

    @property
    def default_hero(self):
        return tuple(
            metric.key
            for metric in self.hero
            if metric.key not in OPTIONAL_HERO_KEYS
        )

    def describe(self, key):
        """What a metric means, or an empty string."""
        return self.descriptions.get(key) or describe(key)


def field_metric(field, label):
    """The metric of a telemetry field under one label."""
    dashboard = field["dashboard"]
    return Metric(
        can_telemetry.engineering_key(field["name"]),
        label,
        can_telemetry.display_unit(field),
        dashboard["digits"],
        dashboard.get("hexadecimal", False),
    )


def build(profile):
    """The presentation of one profile of the schema.

    A field without a presentation stays out of the panels, the hero cards,
    and the descriptions. A panel that no tab shows, or two metrics at one
    order of a panel, are refused.
    """
    fields = {}
    rows = {
        title: list(PANEL_CODE_METRICS.get(title, ()))
        for _tab, titles in TABS
        for title in titles
    }
    descriptions = {}
    for field in can_telemetry.profile_fields(profile):
        dashboard = field.get("dashboard")
        if dashboard is None:
            continue
        key = can_telemetry.engineering_key(field["name"])
        fields[key] = field
        if "description" in dashboard:
            descriptions[key] = dashboard["description"]
        panel = dashboard.get("panel")
        if panel is None:
            continue
        if panel not in rows:
            raise ValueError(f"{field['name']}: no tab shows panel {panel!r}")
        label = dashboard.get("panel_label", dashboard["label"])
        rows[panel].append((dashboard["order"], field_metric(field, label)))
    for title, metrics in rows.items():
        orders = [order for order, _metric in metrics]
        if len(set(orders)) != len(orders):
            raise ValueError(f"panel {title!r} repeats an order")
    tabs = tuple(
        (
            tab,
            tuple(
                (
                    title,
                    tuple(
                        metric
                        for _order, metric in sorted(
                            rows[title], key=lambda row: row[0]
                        )
                    ),
                )
                for title in titles
            ),
        )
        for tab, titles in TABS
    )
    hero = tuple(
        item
        if isinstance(item, Metric)
        else field_metric(
            fields[item], fields[item]["dashboard"]["label"].upper()
        )
        for item in HERO
        if isinstance(item, Metric) or item in fields
    )
    return Presentation(tabs, hero, descriptions)


@lru_cache(maxsize=None)
def default():
    """The presentation of the bundled tuning profile."""
    _document, profiles = can_telemetry.load_schema(
        can_telemetry.DEFAULT_SCHEMA
    )
    return build(profiles["tuning"])
