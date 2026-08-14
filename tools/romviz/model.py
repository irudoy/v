#!/usr/bin/env python3
"""Build a portable address-space model from tracked ROM evidence sources."""

from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import importlib
import math
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_DIR = Path(__file__).with_name("roms")
LAYERS = (
    ("structure", "Firmware structure"),
    ("maps", "Maps and calibrations"),
    ("axes", "Axes"),
    ("diagnostics", "Diagnostics"),
    ("patches", "Custom patches"),
    ("integrity", "Integrity domains"),
)
STORAGE_BYTES = {
    "uint8": 1,
    "int8": 1,
    "uint16": 2,
    "int16": 2,
    "uint32": 4,
    "int32": 4,
    "float32": 4,
}
GENERIC_FUNCTION_RE = re.compile(r"^(?:FUN|thunk_FUN)_[0-9a-fA-F]+$")
ADDRESS_RE = re.compile(r"^(?:0x)?([0-9a-fA-F]{1,8})$")


class ModelError(ValueError):
    """Raised when visualization inputs violate their declared contract."""


def _repo_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def _display_path(path):
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _read_csv(path):
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = []
        for row in reader:
            row["_line"] = reader.line_num
            rows.append(row)
    return rows


def _parse_address(value, context="address"):
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        match = ADDRESS_RE.fullmatch(value.strip())
        if not match:
            raise ModelError(f"{context}: invalid address {value!r}")
        result = int(match.group(1), 16)
    else:
        raise ModelError(f"{context}: invalid address {value!r}")
    if result < 0:
        raise ModelError(f"{context}: negative address")
    return result


def _hex(value, width=6):
    return f"0x{value:0{width}X}"


def _storage_width(storage):
    return STORAGE_BYTES.get((storage or "").strip().lower())


def _dimension(value):
    value = (value or "").strip()
    match = re.fullmatch(r"1D-(\d+)", value)
    if match:
        return int(match.group(1)), 1
    match = re.fullmatch(r"(\d+)x(\d+)", value)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ModelError(f"unsupported map dimension {value!r}")


def _address_list(value, context="address list"):
    return [
        _parse_address(item, context)
        for item in (value or "").split(";")
        if item.strip()
    ]


def _first_sentence(value, fallback, limit=88):
    text = " ".join((value or "").strip().split())
    if not text:
        return fallback
    sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip() + "..."


def _humanize(value):
    return " ".join(part.capitalize() for part in value.replace("_", " ").split())


def _meta(**values):
    return [
        {"label": label.replace("_", " ").capitalize(), "value": str(value)}
        for label, value in values.items()
        if value not in (None, "", [], ())
    ]


def _object(
    *,
    object_id,
    layer,
    kind,
    start,
    end,
    label,
    source,
    description="",
    note="",
    confidence="",
    role="",
    reviewed=True,
    exact_extent=True,
    patch="",
    patch_status="",
    tags=(),
    meta=(),
    related=(),
):
    start = int(start)
    end = int(end)
    if start < 0 or end <= start:
        raise ModelError(f"{object_id}: invalid range [{start:#x}, {end:#x})")
    return {
        "id": object_id,
        "layer": layer,
        "kind": kind,
        "start": start,
        "end": end,
        "label": label,
        "source": source,
        "description": description or "",
        "note": note or "",
        "confidence": confidence or "",
        "role": role or "",
        "reviewed": bool(reviewed),
        "exactExtent": bool(exact_extent),
        "patch": patch or "",
        "patchStatus": patch_status or "",
        "tags": sorted({str(item) for item in tags if item}),
        "meta": list(meta),
        "related": list(related),
    }


def _load_manifest(path):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    required = {
        "schema_version",
        "rom",
        "label",
        "annotation_source",
        "image_registry",
        "ghidra_export",
        "map_ledger",
        "axes",
        "interpolation",
        "reviewed_functions",
        "diagnostic_bindings",
        "dtc",
        "overrides",
        "checksum_module",
        "patch",
    }
    if raw.get("schema_version") != 1 or not required <= set(raw):
        missing = sorted(required - set(raw))
        raise ModelError(f"{path}: unsupported manifest or missing fields {missing}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", raw["rom"]):
        raise ModelError(f"{path}: invalid ROM label")
    raw["_path"] = path
    return raw


def resolve_manifest(value):
    candidate = Path(value)
    if candidate.suffix == ".toml" or candidate.exists():
        return candidate.resolve()
    return (DEFAULT_MANIFEST_DIR / f"{value}.toml").resolve()


def _registry_image(manifest):
    registry = _repo_path(manifest["image_registry"])
    matches = [
        row
        for row in _read_csv(registry)
        if row.get("rom", "").strip() == manifest["rom"]
    ]
    if len(matches) != 1:
        raise ModelError(
            f"{registry}: expected one image for {manifest['rom']}, found {len(matches)}"
        )
    row = matches[0]
    image_path = registry.parent / row["path"]
    data = image_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != row["sha256"]:
        raise ModelError(
            f"{image_path}: SHA-256 is {digest}, expected {row['sha256']}"
        )
    return image_path, data, digest


def _page_metrics(data, page_size=256):
    pages = []
    for start in range(0, len(data), page_size):
        page = data[start : start + page_size]
        counts = [0] * 256
        for value in page:
            counts[value] += 1
        entropy = 0.0
        for count in counts:
            if count:
                probability = count / len(page)
                entropy -= probability * math.log2(probability)
        pages.append({
            "entropy": round(entropy / 8, 4),
            "erased": round(counts[0xFF] / len(page), 4),
        })
    return {"pageSize": page_size, "pages": pages}


def _presentation(path):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    return raw, {
        _parse_address(key): value
        for key, value in raw.get("table", {}).items()
    }


def _reviewed_functions(path):
    return {
        _parse_address(row["addr"], f"{path}:{row['_line']}"): row
        for row in _read_csv(path)
    }


def _function_objects(manifest, rom_size, warnings):
    review_path = _repo_path(manifest["reviewed_functions"])
    reviewed = _reviewed_functions(review_path)
    export_dir = _repo_path(manifest["ghidra_export"])
    graph_path = export_dir / "funcs.csv"
    structural = {}
    if graph_path.exists():
        for row in _read_csv(graph_path):
            start = _parse_address(row["addr"], f"{graph_path}:{row['_line']}")
            if start >= rom_size or row.get("is_external") == "true":
                continue
            size = int(row["size"])
            if size <= 0:
                continue
            structural[start] = row
    else:
        warnings.append(
            f"Ghidra function export is unavailable at {_display_path(graph_path)}; "
            "reviewed functions use point extents."
        )

    objects = []
    for start in sorted(set(structural) | set(reviewed)):
        graph = structural.get(start)
        review = reviewed.get(start)
        body_size = int(graph["size"]) if graph else 2
        end = min(rom_size, start + max(1, body_size))
        if start >= rom_size:
            continue
        ghidra_name = graph["name"] if graph else f"FUN_{start:08x}"
        has_review = review is not None
        if has_review:
            fallback = ghidra_name if not GENERIC_FUNCTION_RE.fullmatch(ghidra_name) else f"Function {_hex(start)}"
            label = _first_sentence(review["semantics"], fallback)
            description = review["semantics"]
            note = review["note"]
            confidence = review["confidence"]
            role = review["role"]
            sources = (
                f"{_display_path(review_path)}:{review['_line']}",
                f"{_display_path(graph_path)}:{graph['_line']}" if graph else "",
            )
        else:
            label = ghidra_name
            description = "Ghidra function structure without a reviewed semantic annotation."
            note = ""
            confidence = "structural"
            role = ""
            sources = (f"{_display_path(graph_path)}:{graph['_line']}",)
        objects.append(_object(
            object_id=f"function:{start:08x}",
            layer="structure",
            kind="reviewed-function" if has_review else "function-structure",
            start=start,
            end=end,
            label=label,
            source="; ".join(item for item in sources if item),
            description=description,
            note=note,
            confidence=confidence,
            role=role,
            reviewed=has_review,
            exact_extent=bool(graph),
            tags=("function", role, confidence, "reviewed" if has_review else "structure-only"),
            meta=_meta(
                ghidra_name=ghidra_name,
                body_bytes=body_size if graph else "unknown",
                thunk=graph.get("is_thunk") if graph else "",
            ),
        ))
    return objects


def _interp_index(path):
    result = {}
    for row in _read_csv(path):
        key = (row["family"], row["kernel"].lower(), row["wrapper"].lower())
        result[key] = row
    return result


def _map_objects(manifest, presentation, rom_size):
    path = _repo_path(manifest["map_ledger"])
    interp = _interp_index(_repo_path(manifest["interpolation"]))
    objects = []
    axis_uses = defaultdict(list)
    for row in _read_csv(path):
        start = _parse_address(row["table"], f"{path}:{row['_line']}")
        width, height = _dimension(row["dim"])
        element_bytes = _storage_width(row["storagetype"])
        if element_bytes is None:
            raise ModelError(
                f"{path}:{row['_line']}: unsupported storage {row['storagetype']!r}"
            )
        size = width * height * element_bytes
        if start + size > rom_size:
            raise ModelError(f"{path}:{row['_line']}: map exceeds ROM")
        override = presentation.get(start, {})
        label = override.get("name") or _first_sentence(
            row["semantics"], f"Map {_hex(start)}"
        )
        category = override.get("category", "")
        objects.append(_object(
            object_id=f"map:{start:08x}",
            layer="maps",
            kind="map",
            start=start,
            end=start + size,
            label=label,
            source=f"{_display_path(path)}:{row['_line']}",
            description=row["semantics"],
            note=row["note"],
            confidence=row["confidence"],
            role=row["role"],
            tags=("map", row["family"], row["role"], row["confidence"], category),
            meta=_meta(
                dimension=row["dim"],
                storage=row["storagetype"],
                scaling=row["scaling"],
                family=row["family"],
                kernel=_hex(_parse_address(row["kernel"])) if row["kernel"] else "",
                wrapper=_hex(_parse_address(row["via"])) if row["via"] else "",
                category=category,
                emitted=override.get("emit", "default"),
            ),
            related=[
                {
                    "label": f"{axis_name.upper()} axis"
                    + (f" {index + 1}" if len(_address_list(row[axis_name])) > 1 else ""),
                    "address": address,
                }
                for axis_name in ("axis_x", "axis_y")
                for index, address in enumerate(_address_list(row[axis_name]))
            ],
        ))
        interp_row = interp.get((
            row["family"], row["kernel"].lower(), row["via"].lower()
        ))
        for axis_name, count in (("axis_x", width), ("axis_y", height)):
            type_key = "axistype_x" if axis_name == "axis_x" else "axistype_y"
            storage = interp_row.get(type_key, "") if interp_row else ""
            byte_width = _storage_width(storage)
            for address in _address_list(row[axis_name]):
                axis_uses[address].append({
                    "map": start,
                    "count": count,
                    "storage": storage,
                    "bytes": count * byte_width if byte_width else None,
                    "axis": axis_name[-1],
                })
    return objects, axis_uses


def _axis_objects(manifest, axis_uses, rom_size):
    path = _repo_path(manifest["axes"])
    objects = []
    for row in _read_csv(path):
        start = _parse_address(row["addr"], f"{path}:{row['_line']}")
        uses = axis_uses.get(start, [])
        known_sizes = {item["bytes"] for item in uses if item["bytes"]}
        size = max(known_sizes, default=1)
        exact = bool(known_sizes)
        if start + size > rom_size:
            raise ModelError(f"{path}:{row['_line']}: axis exceeds ROM")
        label = row["units"] if row["units"] and row["units"] != "raw" else f"{_humanize(row['kind'])} axis {_hex(start)}"
        related = [
            {"label": f"Map {_hex(item['map'])}", "address": item["map"]}
            for item in uses[:16]
        ]
        objects.append(_object(
            object_id=f"axis:{start:08x}",
            layer="axes",
            kind="axis",
            start=start,
            end=start + size,
            label=label,
            source=f"{_display_path(path)}:{row['_line']}",
            description=row["note"],
            confidence=row["scale_conf"],
            role=row["kind"],
            exact_extent=exact,
            tags=("axis", row["kind"], row["scale_conf"]),
            meta=_meta(
                scale=row["scale_expr"],
                inverse=row["to_byte"],
                inferred_bytes=size if exact else "unknown",
                map_uses=len(uses),
            ),
            related=related,
        ))
    return objects


def _diagnostic_objects(manifest, rom_size):
    path = _repo_path(manifest["diagnostic_bindings"])
    by_address = defaultdict(list)
    for row in _read_csv(path):
        try:
            address = _parse_address(row["firmware_addr"])
        except ModelError:
            continue
        if address < rom_size:
            by_address[address].append(row)
    objects = []
    for address, rows in sorted(by_address.items()):
        labels = sorted({row["diagnostic_label"] for row in rows if row["diagnostic_label"]})
        ids = sorted({row["id"] for row in rows})
        objects.append(_object(
            object_id=f"diagnostic-binding:{address:08x}",
            layer="diagnostics",
            kind="diagnostic-binding",
            start=address,
            end=address + 1,
            label=labels[0] if len(labels) == 1 else f"{len(rows)} diagnostic bindings",
            source="; ".join(
                f"{_display_path(path)}:{row['_line']}" for row in rows
            ),
            description="; ".join(labels),
            note="\n\n".join(row["note"] for row in rows if row["note"]),
            confidence=", ".join(sorted({row["confidence"] for row in rows})),
            role=", ".join(sorted({row["kind"] for row in rows})),
            exact_extent=False,
            tags=("diagnostic", *(row["kind"] for row in rows)),
            meta=_meta(bindings=len(rows), ids=", ".join(ids[:8])),
        ))
    return objects


def _dtc_objects(manifest, rom_size):
    path = _repo_path(manifest["dtc"])
    objects = []
    for row in _read_csv(path):
        record = _parse_address(row["record_addr"], f"{path}:{row['_line']}")
        attribute = _parse_address(row["attribute_addr"], f"{path}:{row['_line']}")
        attribute_size = max(1, len(row["stock_attribute"]) // 2)
        for kind, address, size, label in (
            ("dtc-record", record, 12, f"{row['dtc']} descriptor"),
            ("dtc-attribute", attribute, attribute_size, f"{row['dtc']} attribute"),
        ):
            if address + size > rom_size:
                raise ModelError(f"{path}:{row['_line']}: DTC range exceeds ROM")
            objects.append(_object(
                object_id=f"{kind}:{row['index']}:{address:08x}",
                layer="diagnostics",
                kind=kind,
                start=address,
                end=address + size,
                label=label,
                source=f"{_display_path(path)}:{row['_line']}",
                description=row["note"],
                confidence=row["confidence"],
                role=row["group"],
                tags=("dtc", kind, row["group"], row["dtc"]),
                meta=_meta(
                    index=row["index"],
                    stock_attribute=row["stock_attribute"] if kind == "dtc-attribute" else "",
                    disabled_attribute=row["disabled_attribute"] if kind == "dtc-attribute" else "",
                ),
            ))
    return objects


def _switch_objects(overrides_path, overrides, rom_size):
    objects = []
    for index, row in enumerate(overrides.get("switch", [])):
        start = _parse_address(row["storageaddress"])
        width = _storage_width(row.get("storagetype")) or 1
        count = int(row.get("sizex", 1))
        size = width * count
        if start + size > rom_size:
            raise ModelError(f"{overrides_path}: switch {row.get('name')} exceeds ROM")
        states = ", ".join(item["name"] for item in row.get("state", []))
        objects.append(_object(
            object_id=f"definition-switch:{index}:{start:08x}",
            layer="patches",
            kind="definition-switch",
            start=start,
            end=start + size,
            label=row.get("name", f"Definition switch {_hex(start)}"),
            source=_display_path(overrides_path),
            description=row.get("description", ""),
            role=row.get("category", ""),
            patch="definition-controls",
            patch_status="available",
            tags=("patch", "definition-control", row.get("category", "")),
            meta=_meta(storage=row.get("storagetype"), states=states),
        ))
    return objects


def _checksum_objects(module_name, rom_size):
    module = importlib.import_module(module_name)
    objects = []
    fields = getattr(module, "CHECKSUM_FIELDS", ())
    for name, start, width in fields:
        objects.append(_object(
            object_id=f"checksum-field:{name}",
            layer="integrity",
            kind="checksum-field",
            start=start,
            end=start + width,
            label=f"{_humanize(name)} field",
            source=f"{module.__name__.replace('.', '/')}.py",
            description="Stored checksum reference regenerated by the ROM builder.",
            role="checksum field",
            tags=("checksum", "field"),
            meta=_meta(width_bytes=width),
        ))
    prefixes = sorted({
        name[:-6]
        for name in dir(module)
        if name.endswith("_START") and hasattr(module, name[:-6] + "_END")
    })
    for prefix in prefixes:
        start = getattr(module, prefix + "_START")
        end = getattr(module, prefix + "_END")
        if not (0 <= start < end <= rom_size):
            raise ModelError(f"{module_name}: invalid checksum domain {prefix}")
        objects.append(_object(
            object_id=f"checksum-domain:{prefix.lower()}",
            layer="integrity",
            kind="checksum-domain",
            start=start,
            end=end,
            label=f"{_humanize(prefix)} domain",
            source=f"{module.__name__.replace('.', '/')}.py",
            description="Half-open checksum coverage domain.",
            role="checksum domain",
            tags=("checksum", "domain"),
        ))
    return objects


def _assembly_segments(path, rom_size):
    """Measure the small .org/.align/.byte/.word/.long SH source subset."""
    path = Path(path)
    cursor = None
    segment_start = None
    segments = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if not line or line.endswith(":"):
            continue
        if line.startswith(".org "):
            if segment_start is not None and cursor > segment_start:
                segments.append((segment_start, cursor))
            cursor = _parse_address(line[5:].strip(), f"{path}:{line_number}")
            segment_start = cursor
            continue
        if cursor is None:
            continue
        if line.startswith(".align "):
            alignment = int(line[7:].strip(), 0)
            if alignment <= 0 or alignment & (alignment - 1):
                raise ModelError(f"{path}:{line_number}: invalid alignment")
            cursor = (cursor + alignment - 1) & -alignment
            continue
        directive = next(
            ((prefix, width) for prefix, width in ((".byte ", 1), (".word ", 2), (".long ", 4)) if line.startswith(prefix)),
            None,
        )
        if directive:
            prefix, width = directive
            values = [item.strip() for item in line[len(prefix):].split(",") if item.strip()]
            cursor += width * len(values)
        elif line.startswith("."):
            raise ModelError(f"{path}:{line_number}: unsupported directive")
        else:
            cursor += 2
        if cursor > rom_size:
            raise ModelError(f"{path}:{line_number}: assembly exceeds ROM")
    if segment_start is not None and cursor > segment_start:
        segments.append((segment_start, cursor))
    return segments


def _patch_layout_objects(spec, rom_size):
    path = _repo_path(spec["path"])
    with path.open("rb") as source:
        raw = tomllib.load(source)
    if raw.get("rom") != spec.get("rom", raw.get("rom")):
        raise ModelError(f"{path}: patch ROM differs")
    patch_id = spec["id"]
    patch_label = spec["label"]
    status = spec["status"]
    source_name = _display_path(path)
    objects = []

    def add(kind, key, start, end, label, *, description="", meta=(), related=()):
        if not (0 <= start < end <= rom_size):
            raise ModelError(f"{path}: {kind}.{key} is outside ROM")
        objects.append(_object(
            object_id=f"patch:{patch_id}:{kind}:{key}",
            layer="patches",
            kind=kind,
            start=start,
            end=end,
            label=label,
            source=source_name,
            description=description,
            role=patch_label,
            patch=patch_id,
            patch_status=status,
            tags=("patch", patch_id, status, kind),
            meta=meta,
            related=related,
        ))

    claimed = []
    if "claimed_rom_start" in raw and "claimed_rom_end" in raw:
        claimed.append((raw["claimed_rom_start"], raw["claimed_rom_end"], "primary"))
    if "owned_rom_start" in raw and "owned_rom_end" in raw:
        claimed.append((raw["owned_rom_start"], raw["owned_rom_end"], "owned"))
    for index, row in enumerate(raw.get("claimed_rom_extension", [])):
        claimed.append((row["start"], row["end"], f"extension-{index + 1}"))
    for start, end, key in claimed:
        add("patch-claim", key, start, end, f"{patch_label} claimed ROM")

    if "free_rom_start" in raw and "free_rom_end" in raw:
        add(
            "erased-envelope",
            "free-rom",
            raw["free_rom_start"],
            raw["free_rom_end"],
            f"{patch_label} verified erased envelope",
        )

    if "reserved_rom_start" in raw and "reserved_rom_end" in raw:
        add(
            "patch-reserve",
            "reserved-rom",
            raw["reserved_rom_start"],
            raw["reserved_rom_end"],
            f"{patch_label} future ROM reserve",
        )

    unit_by_region = {}
    for unit in raw.get("assembly_unit", []):
        for region_key in unit.get("code_regions", []):
            unit_by_region[region_key] = unit
    for row in raw.get("code_region", []):
        unit = unit_by_region.get(row["key"], {})
        add(
            "patch-code",
            row["key"],
            row["start"],
            row["end"],
            f"{patch_label}: {_humanize(row['key'])}",
            meta=_meta(
                entry=_hex(row.get("entry", row["start"])),
                assembly=unit.get("source", ""),
                instructions=unit.get("instruction_count", ""),
                data_bytes=unit.get("data_bytes", ""),
            ),
        )

    for unit in raw.get("assembly_unit", []):
        if unit.get("code_regions"):
            continue
        add(
            "patch-data",
            f"assembly-{unit['key']}",
            unit["start"],
            unit["end"],
            f"{patch_label}: {_humanize(unit['key'])}",
            meta=_meta(
                assembly=unit.get("source", ""),
                data_bytes=unit.get("data_bytes", ""),
            ),
        )

    if "configuration_address" in raw and "configuration_size" in raw:
        start = raw["configuration_address"]
        add(
            "patch-configuration",
            "configuration",
            start,
            start + raw["configuration_size"],
            f"{patch_label} configuration",
        )
    if "mailbox_record_address" in raw:
        start = raw["mailbox_record_address"]
        add(
            "patch-site",
            "mailbox-record",
            start,
            start + 4,
            f"{patch_label} mailbox record",
            meta=_meta(stock=_hex(raw.get("mailbox_record_stock", 0))),
        )
    feedback = raw.get("feedback", {})
    if "config_record_address" in feedback:
        start = feedback["config_record_address"]
        add(
            "patch-site",
            "feedback-config-record",
            start,
            start + 4,
            f"{patch_label} CAN mailbox record",
        )
    if "phase_counts_address" in feedback:
        start = feedback["phase_counts_address"]
        add(
            "patch-data",
            "feedback-phase-counts",
            start,
            start + 2,
            f"{patch_label} feedback timing",
        )

    slot_count = raw.get("slot_count", 5)
    for family in raw.get("family", []):
        width = family["width"] * family["height"] * (_storage_width(family["storage_type"]) or 1)
        for slot, start in enumerate(family.get("copies", []), 2):
            related = ({"label": "Canonical map", "address": family["canonical_address"]},)
            add(
                "patch-map-copy",
                f"{family['key']}-map-{slot}",
                start,
                start + width,
                f"{family['name']} - Map {slot}",
                meta=_meta(group=family.get("group"), storage=family.get("storage_type"), bytes=width),
                related=related,
            )
            objects.append(_object(
                object_id=f"custom-map:{patch_id}:{family['key']}:map-{slot}",
                layer="maps",
                kind="custom-map",
                start=start,
                end=start + width,
                label=f"{family['name']} - Map {slot}",
                source=source_name,
                description=f"Custom map copy owned by the {patch_label} composition.",
                role=family.get("group", patch_label),
                patch=patch_id,
                patch_status=status,
                tags=("map", "custom", patch_id, status, family.get("group", "")),
                meta=_meta(
                    dimensions=f"{family['width']}x{family['height']}",
                    storage=family.get("storage_type"),
                    bytes=width,
                ),
                related=related,
            ))
        if "pointer_table" in family:
            start = family["pointer_table"]
            add(
                "patch-pointer-table",
                family["key"],
                start,
                start + slot_count * 4,
                f"{family['name']} pointer table",
                related=({"label": "Canonical map", "address": family["canonical_address"]},),
            )

    for row in raw.get("hook", []):
        related = []
        replacement = row.get("replacement")
        if isinstance(replacement, int) and replacement < rom_size:
            related.append({"label": "Replacement target", "address": replacement})
        stock = row.get("stock")
        if isinstance(stock, int) and stock < rom_size:
            related.append({"label": "Stock target/value", "address": stock})
        add(
            "patch-hook",
            row["key"],
            row["address"],
            row["address"] + row["width"],
            f"{patch_label}: {_humanize(row['key'])}",
            description=row.get("purpose", ""),
            meta=_meta(width_bytes=row["width"], stock=_hex(stock) if isinstance(stock, int) else "", replacement=_hex(replacement) if isinstance(replacement, int) else ""),
            related=related,
        )

    for row in raw.get("anchor", []):
        add(
            "patch-anchor",
            row["key"],
            row["address"],
            row["address"] + row["width"],
            f"{patch_label}: {_humanize(row['key'])}",
            description=row.get("purpose", ""),
        )

    for row in raw.get("diagnostic", []):
        start = row["pointer_address"]
        add(
            "patch-diagnostic-pointer",
            f"did-{row['did']:04x}",
            start,
            start + 4,
            f"{patch_label}: DID 0x{row['did']:04X} {row['name']}",
            meta=_meta(target=_hex(row["target"], 8), value_width=row["width"]),
        )
    return objects


def _telemetry_profile_objects(spec, rom_size, warnings):
    path = _repo_path(spec["path"])
    if not path.exists():
        if spec.get("optional"):
            warnings.append(f"Optional patch profile {_display_path(path)} is unavailable.")
            return []
        raise ModelError(f"patch profile not found: {path}")
    with path.open("rb") as source:
        raw = tomllib.load(source)
    patch_id = spec["id"]
    patch_label = spec["label"]
    status = spec["status"]
    source_name = _display_path(path)
    objects = []

    def add(kind, key, start, end, label, source=source_name, meta=()):
        if not (0 <= start < end <= rom_size):
            raise ModelError(f"{path}: {kind}.{key} is outside ROM")
        objects.append(_object(
            object_id=f"patch:{patch_id}:{kind}:{key}",
            layer="patches",
            kind=kind,
            start=start,
            end=end,
            label=label,
            source=source,
            description="Candidate allocation; not part of the composed ROM builder layout.",
            role=patch_label,
            patch=patch_id,
            patch_status=status,
            tags=("patch", patch_id, status, kind),
            meta=meta,
        ))

    add(
        "patch-data",
        "source-tables",
        raw["table_address"],
        raw["table_end"],
        f"{patch_label} source tables",
        meta=_meta(profiles=len(raw.get("profile", [])), fields=len(raw.get("field", []))),
    )
    config_start = raw["configuration_address"]
    add(
        "patch-configuration",
        "configuration",
        config_start,
        config_start + 16,
        f"{patch_label} configuration",
    )
    for assembly_value in spec.get("assembly", []):
        assembly_path = _repo_path(assembly_value)
        if not assembly_path.exists():
            if spec.get("optional"):
                warnings.append(f"Optional assembly {_display_path(assembly_path)} is unavailable.")
                continue
            raise ModelError(f"assembly source not found: {assembly_path}")
        for index, (start, end) in enumerate(_assembly_segments(assembly_path, rom_size), 1):
            add(
                "patch-code",
                f"{assembly_path.stem}-{index}",
                start,
                end,
                f"{patch_label}: {_humanize(assembly_path.stem)} {index}",
                source=_display_path(assembly_path),
            )
    return objects


def _patch_objects(manifest, rom_size, warnings):
    objects = []
    for source_spec in manifest.get("patch", []):
        spec = dict(source_spec)
        spec["rom"] = manifest["rom"]
        if spec["kind"] == "layout":
            path = _repo_path(spec["path"])
            if not path.exists() and spec.get("optional"):
                warnings.append(f"Optional patch layout {_display_path(path)} is unavailable.")
                continue
            objects.extend(_patch_layout_objects(spec, rom_size))
        elif spec["kind"] == "telemetry-profile":
            objects.extend(_telemetry_profile_objects(spec, rom_size, warnings))
        else:
            raise ModelError(f"unsupported patch source kind {spec['kind']!r}")
    return objects


def _validate_objects(objects, rom_size):
    ids = set()
    for item in objects:
        if item["id"] in ids:
            raise ModelError(f"duplicate object id {item['id']}")
        ids.add(item["id"])
        if item["layer"] not in {key for key, _label in LAYERS}:
            raise ModelError(f"{item['id']}: unknown layer {item['layer']}")
        if not (0 <= item["start"] < item["end"] <= rom_size):
            raise ModelError(f"{item['id']}: range is outside ROM")


def build_rom_model(manifest_path):
    manifest = _load_manifest(manifest_path)
    image_path, image, digest = _registry_image(manifest)
    rom_size = len(image)
    warnings = []
    overrides_path = _repo_path(manifest["overrides"])
    overrides, presentation = _presentation(overrides_path)

    objects = []
    objects.extend(_function_objects(manifest, rom_size, warnings))
    map_objects, axis_uses = _map_objects(manifest, presentation, rom_size)
    objects.extend(map_objects)
    objects.extend(_axis_objects(manifest, axis_uses, rom_size))
    objects.extend(_diagnostic_objects(manifest, rom_size))
    objects.extend(_dtc_objects(manifest, rom_size))
    objects.extend(_switch_objects(overrides_path, overrides, rom_size))
    objects.extend(_checksum_objects(manifest["checksum_module"], rom_size))
    objects.extend(_patch_objects(manifest, rom_size, warnings))
    _validate_objects(objects, rom_size)
    objects.sort(key=lambda item: (item["start"], item["end"], item["layer"], item["id"]))

    counts = defaultdict(int)
    reviewed_functions = 0
    structural_functions = 0
    for item in objects:
        counts[item["layer"]] += 1
        if item["kind"] in {"reviewed-function", "function-structure"}:
            structural_functions += 1
            reviewed_functions += int(item["reviewed"])

    rom_info = overrides.get("rom", {})
    return {
        "id": manifest["rom"],
        "label": manifest["label"],
        "size": rom_size,
        "sha256": digest,
        "image": _display_path(image_path),
        "metadata": {
            "ECU ID": rom_info.get("ecuid", ""),
            "Vehicle": " ".join(filter(None, (rom_info.get("make"), rom_info.get("model")))),
            "Engine": rom_info.get("submodel", ""),
            "MCU": rom_info.get("memmodel", ""),
            "Byte order": rom_info.get("endian", ""),
        },
        "counts": dict(counts),
        "reviewedFunctions": reviewed_functions,
        "structuralFunctions": structural_functions,
        "pageMetrics": _page_metrics(image),
        "warnings": warnings,
        "objects": objects,
    }


def build_atlas(manifests):
    roms = [build_rom_model(resolve_manifest(value)) for value in manifests]
    ids = [rom["id"] for rom in roms]
    if len(set(ids)) != len(ids):
        raise ModelError(f"duplicate ROM models: {ids}")
    return {
        "schemaVersion": 1,
        "layers": [{"id": key, "label": label} for key, label in LAYERS],
        "roms": roms,
    }
