#!/usr/bin/env python3
"""Audit JK08A tuning-editor names, categories, and visibility decisions."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout


DEFAULT_SOURCE = ROOT / "defs" / "JK08A.overrides.toml"
ADDRESS_IN_NAME = re.compile(r"\(0x[0-9A-Fa-f]+\)")
VISIBLE_NAME_FRAGMENTS = ("Trustful", "scheduler counts", "(x-128)")
ALLOWED_TOP_LEVELS = {
    "Electronic Throttle Control",
    "Fuelling",
    "Ignition Timing",
    "Limiters",
    "Torque Model",
    "Variable Valve Timing",
}
NON_TUNING_TABLES = {
    "0000abba": "diagnostic-only surface with unknown verdict direction",
    "0000abfa": "diagnostic-only surface with unknown verdict direction",
    "000120f6": "stock-inactive DFCO branch",
    "0001491a": "diagnostic calculated-load publication only",
}
VALIDATION_PAIRS = (
    (
        "0000e98e",
        "000175c8",
        "Requested Torque Conversion by QH0 - Primary",
        "Requested Torque Conversion by QH0 - Validation Copy",
    ),
    (
        "00013202",
        "00018766",
        "Throttle Angle-to-Area Conversion - Primary",
        "Throttle Angle-to-Area Conversion - Validation Copy",
    ),
)


@dataclass(frozen=True)
class AuditReport:
    canonical_table_count: int
    visible_table_count: int
    hidden_table_count: int
    masked_view_count: int
    switchable_family_count: int
    categories: dict[str, int]
    hidden_non_tuning: dict[str, str]

    def as_dict(self):
        return {
            "canonical_table_count": self.canonical_table_count,
            "visible_table_count": self.visible_table_count,
            "hidden_table_count": self.hidden_table_count,
            "masked_view_count": self.masked_view_count,
            "switchable_family_count": self.switchable_family_count,
            "categories": self.categories,
            "hidden_non_tuning": self.hidden_non_tuning,
        }


def _category_parts(category, context):
    if not isinstance(category, str) or not category:
        raise ValueError(f"{context}: missing category")
    parts = category.split(" / ")
    if any(not part or part.strip() != part for part in parts):
        raise ValueError(f"{context}: category path is not canonical")
    if "//" in category or "/" in "".join(parts):
        raise ValueError(f"{context}: category path uses a noncanonical separator")
    if parts[0] not in ALLOWED_TOP_LEVELS:
        raise ValueError(f"{context}: unsupported top-level category {parts[0]!r}")
    return parts


def _validate_visible_name(name, context):
    if not isinstance(name, str) or not name or name.strip() != name:
        raise ValueError(f"{context}: invalid visible name")
    if ADDRESS_IN_NAME.search(name):
        raise ValueError(f"{context}: visible name contains a storage address")
    for fragment in VISIBLE_NAME_FRAGMENTS:
        if fragment in name:
            raise ValueError(
                f"{context}: visible name contains presentation detail {fragment!r}"
            )


def audit(path=DEFAULT_SOURCE):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    default_emit = raw.get("presentation", {}).get("default_emit")
    if default_emit is not True:
        raise ValueError("presentation.default_emit must remain true")
    tables = raw.get("table")
    if not isinstance(tables, dict):
        raise ValueError("table presentation mapping is absent")

    visible = {}
    for address, presentation in tables.items():
        context = f"table.{address}"
        emitted = presentation.get("emit", default_emit)
        if not isinstance(emitted, bool):
            raise ValueError(f"{context}: emit must be Boolean")
        if not emitted:
            continue
        _validate_visible_name(presentation.get("name"), context)
        _category_parts(presentation.get("category"), context)
        visible[address] = presentation

    for index, view in enumerate(raw.get("masked_view", [])):
        context = f"masked_view[{index}]"
        source = str(view.get("source", "")).lower()
        if source not in visible:
            raise ValueError(f"{context}: source is not a visible table")
        _validate_visible_name(view.get("name"), context)
        _category_parts(view.get("category"), context)

    for address, reason in NON_TUNING_TABLES.items():
        presentation = tables.get(address)
        if presentation is None:
            raise ValueError(f"table.{address}: non-tuning decision is absent")
        if presentation.get("emit", default_emit):
            raise ValueError(f"table.{address}: must remain hidden because {reason}")

    for primary, validation, primary_name, validation_name in VALIDATION_PAIRS:
        if tables[primary]["name"] != primary_name:
            raise ValueError(f"table.{primary}: primary-pair name differs")
        if tables[validation]["name"] != validation_name:
            raise ValueError(f"table.{validation}: validation-copy name differs")
        if tables[primary]["category"] != tables[validation]["category"]:
            raise ValueError(f"table.{validation}: validation-copy category differs")

    layout = map_switching_layout.load_layout()
    for family in layout.families:
        address = f"{family.canonical_address:08x}"
        presentation = tables.get(address)
        if presentation is None:
            raise ValueError(f"{family.key}: canonical presentation is absent")
        if family.name != presentation["name"]:
            raise ValueError(f"{family.key}: manifest and editor names differ")

    categories = Counter(
        presentation["category"] for presentation in visible.values()
    )
    return AuditReport(
        canonical_table_count=len(tables),
        visible_table_count=len(visible),
        hidden_table_count=len(tables) - len(visible),
        masked_view_count=len(raw.get("masked_view", [])),
        switchable_family_count=len(layout.families),
        categories=dict(sorted(categories.items())),
        hidden_non_tuning=NON_TUNING_TABLES,
    )


def render_text(report):
    lines = [
        "JK08A tuning-editor presentation audit",
        f"Canonical tables: {report.canonical_table_count}",
        f"Visible canonical tables: {report.visible_table_count}",
        f"Hidden canonical tables: {report.hidden_table_count}",
        f"Masked views: {report.masked_view_count}",
        f"Switchable families: {report.switchable_family_count}",
        "",
        "Visible categories:",
    ]
    for category, count in report.categories.items():
        lines.append(f"  {count:2}  {category}")
    lines.extend(("", "Explicit non-tuning exclusions:"))
    for address, reason in report.hidden_non_tuning.items():
        lines.append(f"  0x{int(address, 16):05X}  {reason}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit JK08A editor presentation and visibility"
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        report = audit(args.source)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.format == "json":
        json.dump(report.as_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
