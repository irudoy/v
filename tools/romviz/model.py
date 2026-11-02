#!/usr/bin/env python3
"""Build a portable address-space model from tracked ROM evidence sources."""

from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import math
from pathlib import Path
import re
import tomllib
import xml.etree.ElementTree as ET

from patches import rom_address_profiles
from patches import rom_checksums
from tools import rom_homology
from tools import rom_sources
from tools.mapkit import definition_projections
from tools.romviz import graph_atlas


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_DIR = Path(__file__).with_name("roms")
DEFAULT_IMAGE_REGISTRY = ROOT / "rom-images" / "roms.csv"
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
MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "rom",
        "label",
        "annotation_source",
        "image_registry",
        "identity_registry",
        "map_ledger",
        "axes",
        "interpolation",
        "reviewed_functions",
        "diagnostic_bindings",
        "dtc",
        "overrides",
        "definition_xml",
        "published_definition",
        "checksum_registry",
        "warnings",
        "metadata",
        "patch",
        "architecture",
    }
)
ARCHITECTURE_FIELDS = frozenset({"layout"})


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
    required = {"schema_version", "rom", "label", "image_registry"}
    missing = sorted(required - set(raw))
    extra = sorted(set(raw) - MANIFEST_FIELDS)
    if raw.get("schema_version") != 2 or missing or extra:
        raise ModelError(
            f"{path}: unsupported manifest; missing={missing}; extra={extra}"
        )
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", raw["rom"]):
        raise ModelError(f"{path}: invalid ROM label")
    source_fields = {"map_ledger", "axes", "interpolation"}
    present_sources = source_fields & set(raw)
    if present_sources and present_sources != source_fields:
        raise ModelError(
            f"{path}: canonical map source is incomplete; "
            f"missing={sorted(source_fields - present_sources)}"
        )
    if present_sources and "definition_xml" in raw:
        raise ModelError(f"{path}: canonical map source and definition_xml conflict")
    if "published_definition" in raw and "definition_xml" in raw:
        raise ModelError(f"{path}: definition_xml is the published definition; "
                         "published_definition conflicts with it")
    warnings = raw.get("warnings", [])
    if not isinstance(warnings, list) or any(
        not isinstance(value, str) or not value.strip() for value in warnings
    ):
        raise ModelError(f"{path}: warnings must be an array of nonempty strings")
    if "metadata" in raw and not isinstance(raw["metadata"], dict):
        raise ModelError(f"{path}: metadata must be a table")
    if "patch" in raw and not isinstance(raw["patch"], list):
        raise ModelError(f"{path}: patch must be an array of tables")
    if "architecture" in raw:
        _check_architecture_table(path, raw["architecture"])
    raw["_path"] = path
    return raw


def _check_architecture_table(path, table):
    if not isinstance(table, dict):
        raise ModelError(f"{path}: architecture must be a table")
    missing = sorted(ARCHITECTURE_FIELDS - set(table))
    extra = sorted(set(table) - ARCHITECTURE_FIELDS)
    if missing or extra:
        raise ModelError(
            f"{path}: architecture fields differ; missing={missing}; extra={extra}"
        )
    if not isinstance(table['layout'], str) or not re.fullmatch('[0-9a-z]+', table['layout']):
        raise ModelError(f'{path}: architecture.layout must name a layout')


def resolve_manifest(value):
    candidate = Path(value)
    if candidate.suffix == ".toml" or candidate.exists():
        return candidate.resolve()
    return (DEFAULT_MANIFEST_DIR / f"{value}.toml").resolve()


def registered_roms(registry=DEFAULT_IMAGE_REGISTRY):
    """Return every registered flash ROM in deterministic registry order."""
    roms = tuple(
        row.get("rom", "").strip()
        for row in _read_csv(registry)
        if row.get("rom", "").strip()
    )
    if len(roms) != len(set(roms)):
        raise ModelError(f"{registry}: duplicate ROM labels")
    return roms


def registered_manifests(registry=DEFAULT_IMAGE_REGISTRY):
    """Resolve one tracked romviz manifest for every registered flash ROM."""
    roms = registered_roms(registry)
    paths = tuple(resolve_manifest(rom) for rom in roms)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise ModelError(
            "registered ROM manifests are missing: "
            + ", ".join(_display_path(path) for path in missing)
        )
    return paths


def expand_manifest_values(values):
    """Expand an empty selection or the explicit all token to the registry."""
    values = list(values or [])
    all_indexes = [
        index
        for index, value in enumerate(values)
        if str(value).strip().lower() == "all"
    ]
    if not values or all_indexes == [0] and len(values) == 1:
        return list(registered_manifests())
    if all_indexes:
        raise ModelError("ROM selection 'all' cannot be combined with explicit manifests")
    return values


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
    return image_path, data, digest, row


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


def _materialize_tokens(value, target_rom):
    """Replace only explicit target placeholders in presentation text."""
    if isinstance(value, str):
        return value.replace("{target_rom}", target_rom)
    if isinstance(value, list):
        return [_materialize_tokens(item, target_rom) for item in value]
    if isinstance(value, dict):
        return {
            key: _materialize_tokens(item, target_rom)
            for key, item in value.items()
        }
    return value


def _presentation(path, target_rom):
    path = Path(path)
    with path.open("rb") as source:
        raw = _materialize_tokens(tomllib.load(source), target_rom)
    return raw, {
        _parse_address(key): value
        for key, value in raw.get("table", {}).items()
    }


def _identity(manifest):
    if "identity_registry" not in manifest:
        return dict(manifest.get("metadata", {}))
    path = _repo_path(manifest["identity_registry"])
    with path.open("rb") as source:
        document = tomllib.load(source)
    try:
        identity = document["rom"][manifest["rom"]]
    except (KeyError, TypeError) as error:
        raise ModelError(
            f"{path}: identity for {manifest['rom']} is unavailable"
        ) from error
    if not isinstance(identity, dict):
        raise ModelError(f"{path}: identity for {manifest['rom']} is not a table")
    return identity


def _family(rom):
    """Return the homology family of a ROM with the relationships that name it."""
    _, families, relationships = rom_homology.load_homology()
    keys = [key for key, family in families.items() if rom in family.get("members", ())]
    if len(keys) > 1:
        raise ModelError(f"{rom} is a member of several homology families: {keys}")
    if not keys:
        return None
    key = keys[0]
    sides = ("left_family", "right_family")
    related = []
    for relationship in relationships:
        left, right = (relationship.get(side) for side in sides)
        if key not in (left, right):
            continue
        related.append({
            "family": right if left == key else left,
            **{name: value for name, value in relationship.items() if name not in sides},
        })
    return {"key": key, "fields": dict(families[key]), "relationships": related}


def _reviewed_functions(path):
    return {
        _parse_address(row["addr"], f"{path}:{row['_line']}"): row
        for row in _read_csv(path)
    }


def _kb_text(annotation, field, layout):
    """Return one KB text field and the layout it describes when it is not this one."""
    value = graph_atlas.text(annotation["props"].get(field))
    described = annotation[f"{field}Layout"]
    return value, described if value and described != layout else ""


def _kb_meta(annotation, layout):
    props = annotation["props"]
    return _meta(
        meaning=annotation["meaning"],
        symbol=annotation["reference"],
        block=props.get("block", ""),
        summary_layout=_kb_text(annotation, "summary", layout)[1],
        note_layout=_kb_text(annotation, "note", layout)[1],
    )


def _function_objects(manifest, rom_size, warnings, annotations=None, layout=""):
    review_path = None
    reviewed = {}
    if "reviewed_functions" in manifest:
        review_path = _repo_path(manifest["reviewed_functions"])
        reviewed = _reviewed_functions(review_path)
    elif annotations is not None:
        reviewed = {item["address"]: item for item in annotations if item["kind"] == "fn"}
    else:
        warnings.append(
            "Reviewed function annotations are not declared for this ROM."
        )

    try:
        graph_path = rom_sources.l0_dir(manifest["rom"]) / "funcs.csv"
        names = rom_sources.function_names(manifest["rom"])
    except ValueError as error:
        raise ModelError(str(error)) from error
    structural = {}
    for row in _read_csv(graph_path):
        start = _parse_address(row["addr"], f"{graph_path}:{row['_line']}")
        if start >= rom_size or row.get("is_external") == "true":
            continue
        size = int(row["size"])
        if size <= 0:
            continue
        structural[start] = row

    objects = []
    for start in sorted(set(structural) | set(reviewed)):
        graph = structural.get(start)
        review = reviewed.get(start)
        body_size = int(graph["size"]) if graph else 2
        end = min(rom_size, start + max(1, body_size))
        if start >= rom_size:
            continue
        function_name = rom_sources.function_name(names, f"{start:08x}")
        has_review = review is not None
        extra_meta = []
        if has_review and review_path is None:
            props = review["props"]
            label = review["name"]
            description = _kb_text(review, "summary", layout)[0]
            note = _kb_text(review, "note", layout)[0]
            confidence = props.get("level", "")
            role = props.get("role", "")
            sources = (
                *props.get("src", []),
                f"{_display_path(graph_path)}:{graph['_line']}" if graph else "",
            )
            extra_meta = _kb_meta(review, layout)
        elif has_review:
            fallback = function_name if not GENERIC_FUNCTION_RE.fullmatch(function_name) else f"Function {_hex(start)}"
            label = _first_sentence(review["semantics"], fallback)
            description = review["semantics"]
            note = review["note"]
            confidence = review["confidence"]
            role = review["role"]
            sources = (
                f"{_display_path(review_path)}:{review['_line']}"
                if review_path else "",
                f"{_display_path(graph_path)}:{graph['_line']}" if graph else "",
            )
        else:
            label = function_name
            description = "L0 function structure without a reviewed semantic annotation."
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
            tags=("function", role, confidence, "reviewed" if has_review else "structure-only",
                  "kb" if extra_meta else ""),
            meta=_meta(
                function_name=function_name,
                body_bytes=body_size if graph else "unknown",
                thunk=graph.get("is_thunk") if graph else "",
            ) + extra_meta,
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


def _definition_rom(path, target_rom):
    """The single ROM element of a definition XML whose identity is the target."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ModelError(f"definition XML cannot be loaded: {path}: {error}") from error
    roms = root.findall("./rom")
    if len(roms) != 1:
        raise ModelError(f"{path}: expected one ROM definition")
    rom = roms[0]
    xml_id = (rom.findtext("./romid/xmlid") or "").strip()
    if xml_id != target_rom:
        raise ModelError(
            f"{path}: definition identity is {xml_id!r}, expected {target_rom!r}"
        )
    return rom


def _published_tables(manifest):
    """The names under which the published definition of an image shows each start.

    A table carries its name and category. An axis carries its name and the
    tables that use it, because one axis serves several tables.
    """
    source = manifest.get("definition_xml") or manifest.get("published_definition")
    if not source:
        return None
    path = _repo_path(source)
    rom = _definition_rom(path, manifest["rom"])
    tables = defaultdict(list)
    axes = {}
    for table in rom.findall("./table"):
        address = table.get("storageaddress")
        if not address or table.get("type") in {"Switch", "BitwiseSwitch"}:
            continue
        name = table.get("name", "")
        start = _parse_address(address, f"{path}: {name}")
        tables[f"{start:08x}"].append({"name": name, "category": table.get("category", "")})
        for axis in table.findall("./table"):
            axis_address = axis.get("storageaddress")
            if not axis_address:
                continue
            axis_start = _parse_address(axis_address, f"{path}: {name} / {axis.get('name')}")
            record = axes.setdefault((f"{axis_start:08x}", axis.get("name", "")), [])
            if name not in record:
                record.append(name)
    for (start, name), users in axes.items():
        tables[start].append({"name": name, "axisOf": users})
    return {"source": _display_path(path), "tables": dict(sorted(tables.items()))}


def _definition_xml_objects(manifest, rom_size):
    """Load emitted target addresses without reconstructing source-ROM claims."""
    path = _repo_path(manifest["definition_xml"])
    rom = _definition_rom(path, manifest["rom"])

    source_name = _display_path(path)
    map_objects = []
    switch_objects = []
    axes = {}
    map_index = 0
    switch_index = 0

    def shape(node, context):
        try:
            width = int(node.get("sizex", "1"), 10)
            height = int(node.get("sizey", "1"), 10)
        except ValueError as error:
            raise ModelError(f"{path}: {context} has invalid geometry") from error
        if width <= 0 or height <= 0:
            raise ModelError(f"{path}: {context} has nonpositive geometry")
        return width, height

    for table in rom.findall("./table"):
        table_type = table.get("type", "")
        address_text = table.get("storageaddress")
        if not address_text:
            continue
        start = _parse_address(address_text, f"{path}: {table.get('name', table_type)}")
        width, height = shape(table, table.get("name", table_type))
        element_bytes = _storage_width(table.get("storagetype"))
        if element_bytes is None:
            raise ModelError(
                f"{path}: unsupported storage {table.get('storagetype')!r}"
            )
        size = width * height * element_bytes
        if start + size > rom_size:
            raise ModelError(f"{path}: table {table.get('name')!r} exceeds ROM")
        category = table.get("category", "")
        description = " ".join((table.findtext("./description") or "").split())

        if table_type in {"Switch", "BitwiseSwitch"}:
            states = [
                node.get("name", "")
                for node in table.findall("./state") + table.findall("./bit")
                if node.get("name")
            ]
            switch_objects.append(_object(
                object_id=f"definition-switch:{switch_index}:{start:08x}",
                layer="patches",
                kind="definition-switch",
                start=start,
                end=start + size,
                label=table.get("name", f"Definition switch {_hex(start)}"),
                source=source_name,
                description=description,
                role=category,
                patch="definition-controls",
                patch_status="available",
                tags=("patch", "definition-control", category, table_type),
                meta=_meta(
                    storage=table.get("storagetype"),
                    states=", ".join(states),
                ),
            ))
            switch_index += 1
            continue

        scaling = table.find("./scaling")
        related = []
        for axis in table.findall("./table"):
            axis_address_text = axis.get("storageaddress")
            if not axis_address_text:
                continue
            axis_start = _parse_address(
                axis_address_text,
                f"{path}: {table.get('name')} / {axis.get('name')}",
            )
            axis_storage = axis.get("storagetype")
            axis_bytes = _storage_width(axis_storage)
            if axis_bytes is None:
                raise ModelError(
                    f"{path}: unsupported axis storage {axis_storage!r}"
                )
            axis_type = axis.get("type", "")
            default_count = width if "X Axis" in axis_type else height
            size_attr = "sizex" if "X Axis" in axis_type else "sizey"
            try:
                count = int(axis.get(size_attr, str(default_count)), 10)
            except ValueError as error:
                raise ModelError(f"{path}: invalid axis geometry") from error
            axis_end = axis_start + count * axis_bytes
            if count <= 0 or axis_end > rom_size:
                raise ModelError(f"{path}: axis {axis.get('name')!r} exceeds ROM")
            record = axes.setdefault(axis_start, {
                "end": axis_end,
                "labels": set(),
                "types": set(),
                "storage": set(),
                "maps": [],
            })
            record["end"] = max(record["end"], axis_end)
            record["labels"].add(axis.get("name", f"Axis {_hex(axis_start)}"))
            record["types"].add(axis_type)
            record["storage"].add(axis_storage)
            record["maps"].append((start, table.get("name", "Map")))
            related.append({
                "label": axis.get("name", "Axis"),
                "address": axis_start,
            })

        map_objects.append(_object(
            object_id=f"definition-map:{map_index}:{start:08x}",
            layer="maps",
            kind="definition-map",
            start=start,
            end=start + size,
            label=table.get("name", f"Map {_hex(start)}"),
            source=source_name,
            description=description,
            role=category,
            tags=("map", "definition", table_type, category),
            meta=_meta(
                dimensions=f"{width}x{height}",
                storage=table.get("storagetype"),
                units=scaling.get("units", "") if scaling is not None else "",
                scaling=scaling.get("expression", "") if scaling is not None else "",
                category=category,
            ),
            related=related,
        ))
        map_index += 1

    axis_objects = []
    for start, record in sorted(axes.items()):
        labels = sorted(record["labels"])
        uses = record["maps"]
        axis_objects.append(_object(
            object_id=f"definition-axis:{start:08x}",
            layer="axes",
            kind="definition-axis",
            start=start,
            end=record["end"],
            label=labels[0] if len(labels) == 1 else f"Shared axis {_hex(start)}",
            source=source_name,
            description="; ".join(labels),
            role=", ".join(sorted(record["types"])),
            tags=("axis", "definition", *record["types"]),
            meta=_meta(
                storage=", ".join(sorted(record["storage"])),
                map_uses=len(uses),
            ),
            related=[
                {"label": label, "address": address}
                for address, label in uses[:16]
            ],
        ))
    return map_objects, axis_objects, switch_objects


def _geometry(values, kind, origin):
    """Element count and width of a KB or census table or axis, if both are known."""
    element_bytes = _storage_width(values.get("storage"))
    if element_bytes is None:
        return None
    if kind == "axis":
        if not values.get("points"):
            return None
        dimension = f"1D-{values['points']}"
        cols, rows = values["points"], 1
    else:
        # A table without columns is one scalar element.
        cols, rows = values.get("cols") or 1, values.get("rows") or 1
        dimension = f"{cols}x{rows}"
    count = cols * rows
    return {"count": count, "bytes": element_bytes, "size": count * element_bytes,
            "cols": cols, "rows": rows, "dimension": dimension,
            "storage": values["storage"], "origin": origin}


def _kb_geometry(annotation, kind):
    fields = ("storage", "points") if kind == "axis" else ("storage", "cols", "rows")
    origin = "kb symbol" if annotation["own"] & set(fields) else "kb meaning"
    return _geometry(annotation["props"], kind, origin)


def _census_confirms(knowledge, image, kind, start, geometry):
    """Whether the census entries at a KB start have the KB shape.

    One census entry matches the KB dimension and element width exactly. A KB
    table of R > 1 rows can group R adjacent census curves of its columns that
    share one census axis set, because the census records each lookup of the
    grouped table separately.
    """
    def entry(address):
        values = knowledge.census.get((image, kind, address))
        return _geometry(values, kind, "census") if values else None

    first = entry(start)
    if first and (first["dimension"], first["bytes"]) == (geometry["dimension"],
                                                          geometry["bytes"]):
        return True
    if kind != "tbl" or geometry["rows"] < 2:
        return False
    row_bytes = geometry["cols"] * geometry["bytes"]
    shared = None
    for row in range(geometry["rows"]):
        address = start + row * row_bytes
        part = entry(address)
        axes = knowledge.census_uses.get((image, kind, address), set())
        if (part is None or (part["cols"], part["rows"], part["bytes"])
                != (geometry["cols"], 1, geometry["bytes"])
                or not axes or (shared is not None and axes != shared)):
            return False
        shared = axes
    return True


def _editor_status(props, image):
    editor = props.get("editor") or {}
    if editor.get("emit") is False:
        return "emit = false"
    if not editor:
        return "no editor declaration"
    return f"declared, not published for {image}"


def _kb_calibration_objects(annotations, objects, knowledge, image, layout, rom_size):
    """Add the KB tables and axes that no definition object publishes at their start.

    A definition object of the other kind at the same start publishes the
    range in its other role, so the KB object of that dual role is not hidden.
    Return the objects and the geometry conflicts between KB, census and the
    published definition extents.
    """
    published = defaultdict(list)
    for item in objects:
        if item["kind"] in {"definition-map", "definition-axis"}:
            kind = "tbl" if item["kind"] == "definition-map" else "axis"
            published[(kind, item["start"])].append(item)
    names = {(annotation["kind"], annotation["address"]): annotation["name"]
             for annotation in annotations}
    found, conflicts = [], []
    for annotation in annotations:
        kind, start = annotation["kind"], annotation["address"]
        if kind not in {"tbl", "axis"}:
            continue
        reference = annotation["reference"]
        kb = _kb_geometry(annotation, kind)
        census_values = knowledge.census.get((image, kind, start))
        census = _geometry(census_values, kind, "census") if census_values else None
        if kb and census and not _census_confirms(knowledge, image, kind, start, kb):
            conflicts.append(f"{reference}: kb {kb['dimension']} {kb['storage']}, "
                             f"census {census['dimension']} {census['storage']}")
        if published[(kind, start)]:
            for item in published[(kind, start)]:
                if kb and item["end"] - item["start"] != kb["size"]:
                    conflicts.append(f"{reference}: kb {kb['size']} bytes, "
                                     f"{item['id']} {item['end'] - item['start']} bytes")
            continue
        geometry = kb or census
        size = geometry["size"] if geometry else 1
        if start + size > rom_size:
            raise ModelError(f"{reference}: extent exceeds ROM")
        props = annotation["props"]
        if annotation["related"]:
            related_addresses = annotation["related"]
        else:
            related_addresses = sorted(knowledge.census_uses.get((image, kind, start), ()))
        related_label = "Map" if kind == "axis" else "Axis"
        other = "axis" if kind == "tbl" else "tbl"
        dual = published[(other, start)]
        if dual:
            editor = (f"published as {dual[0]['id']} through "
                      f"{names.get((other, start)) or dual[0]['label']}")
        else:
            editor = _editor_status(props, image)
        found.append(_object(
            object_id=f"kb-{'map' if kind == 'tbl' else 'axis'}:{start:08x}",
            layer="maps" if kind == "tbl" else "axes",
            kind="kb-map" if kind == "tbl" else "kb-axis",
            start=start,
            end=start + size,
            label=annotation["name"],
            source="; ".join(props.get("src", [])),
            description=_kb_text(annotation, "summary", layout)[0],
            note=_kb_text(annotation, "note", layout)[0],
            confidence=props.get("level", ""),
            role=props.get("role", ""),
            exact_extent=geometry is not None,
            tags=("map" if kind == "tbl" else "axis", "kb", "" if dual else "hidden",
                  props.get("role", ""), props.get("level", "")),
            meta=_meta(
                editor=editor,
                dimension=geometry["dimension"] if geometry else "",
                storage=geometry["storage"] if geometry else "",
                geometry=geometry["origin"] if geometry else "unknown",
            ) + _kb_meta(annotation, layout),
            related=[
                {"label": f"{related_label} {_hex(address)}", "address": address}
                for address in related_addresses[:16]
            ],
        ))
    return found, conflicts


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


def _checksum_objects(rom, registry_value, rom_size):
    registry = _repo_path(registry_value)
    try:
        layout = rom_checksums.layout_for_rom(rom, registry)
    except rom_checksums.ChecksumError as error:
        raise ModelError(str(error)) from error
    if layout.rom_size != rom_size:
        raise ModelError(
            f"{registry}: checksum layout for {rom} has size {layout.rom_size:#x}, "
            f"expected {rom_size:#x}"
        )
    source_name = f"{_display_path(registry)} [layout.{layout.key}]"
    objects = []
    for name, start, width in layout.checksum_fields:
        objects.append(_object(
            object_id=f"checksum-field:{name}",
            layer="integrity",
            kind="checksum-field",
            start=start,
            end=start + width,
            label=f"{_humanize(name)} field",
            source=source_name,
            description="Stored checksum reference from the registered target layout.",
            role="checksum field",
            tags=("checksum", "field"),
            meta=_meta(width_bytes=width),
        ))
    for domain in layout.domains:
        name = domain.key
        start = domain.start
        end = domain.end
        exclusions = domain.exclusions
        if not (0 <= start < end <= rom_size):
            raise ModelError(f"{registry}: invalid checksum domain {name}")
        objects.append(_object(
            object_id=f"checksum-domain:{name}",
            layer="integrity",
            kind="checksum-domain",
            start=start,
            end=end,
            label=f"{_humanize(name)} domain",
            source=source_name,
            description="Half-open checksum coverage domain.",
            role="checksum domain",
            tags=("checksum", "domain"),
            meta=_meta(excluded_words=len(exclusions)),
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
    expected_rom = spec.get("source_rom", spec["target_rom"])
    if raw.get("rom") != expected_rom:
        raise ModelError(
            f"{path}: patch source ROM is {raw.get('rom')!r}, "
            f"expected {expected_rom!r}"
        )
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


def _address_profile_objects(spec, rom_size):
    path = _repo_path(
        spec.get("path", rom_address_profiles.DEFAULT_REGISTRY)
    )
    try:
        profile = rom_address_profiles.profile_for_rom(spec["target_rom"], path)
    except rom_address_profiles.AddressProfileError as error:
        raise ModelError(str(error)) from error
    if profile.rom_size != rom_size:
        raise ModelError(
            f"{path}: address profile for {profile.rom} has size "
            f"{profile.rom_size:#x}, expected {rom_size:#x}"
        )
    patch_id = spec["id"]
    patch_label = spec["label"]
    status = spec["status"]
    composed = status == "composed"
    source_name = f"{_display_path(path)} [profile.{profile.rom}]"
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

    add(
        "erased-envelope",
        "free-rom",
        profile.free_rom.start,
        profile.free_rom.end,
        f"{patch_label} verified erased envelope",
        description=dict(profile.evidence).get("free_rom", ""),
    )
    add(
        "patch-claim",
        "injected-rom",
        profile.injected_rom.start,
        profile.injected_rom.end,
        f"{patch_label} {'composed' if composed else 'candidate'} allocation",
        description=(
            "Exact target allocation emitted by the current production builder."
            if composed
            else "Exact target allocation registered for future unified composition; "
            "the current production builder does not emit this target."
        ),
    )
    for group, hooks in (
        ("map", profile.map_hooks),
        ("rolling", profile.rolling_hooks),
        ("can", profile.can_hooks),
    ):
        for hook in hooks:
            related = []
            if hook.stock < rom_size:
                related.append({"label": "Stock target/value", "address": hook.stock})
            if hook.replacement < rom_size:
                related.append({"label": "Replacement target", "address": hook.replacement})
            add(
                "patch-hook",
                f"{group}-{hook.key}",
                hook.address,
                hook.address + 4,
                f"{patch_label}: {_humanize(hook.key)}",
                meta=_meta(
                    stock=_hex(hook.stock, 8),
                    base=_hex(hook.base, 8),
                    replacement=_hex(hook.replacement, 8),
                ),
                related=related,
            )
    for binding in profile.rolling_diagnostics:
        add(
            "patch-diagnostic-pointer",
            f"did-{binding.did:04x}",
            binding.pointer_address,
            binding.pointer_address + 4,
            f"{patch_label}: DID 0x{binding.did:04X} {_humanize(binding.key)}",
            meta=_meta(
                target=_hex(binding.target, 8),
                value_width=binding.width,
            ),
        )
    return objects


def _patch_objects(manifest, rom_size, warnings):
    objects = []
    for source_spec in manifest.get("patch", []):
        spec = dict(source_spec)
        spec["target_rom"] = manifest["rom"]
        if spec["kind"] == "layout":
            path = _repo_path(spec["path"])
            if not path.exists() and spec.get("optional"):
                warnings.append(f"Optional patch layout {_display_path(path)} is unavailable.")
                continue
            objects.extend(_patch_layout_objects(spec, rom_size))
        elif spec["kind"] == "telemetry-profile":
            objects.extend(_telemetry_profile_objects(spec, rom_size, warnings))
        elif spec["kind"] == "address-profile":
            objects.extend(_address_profile_objects(spec, rom_size))
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


def _architecture_binding(manifest, cache):
    """Bind an image to its layout's symbols in one current graph snapshot."""
    context = f"{_display_path(manifest['_path'])} architecture"
    if '_knowledge' not in cache:
        try:
            cache['_knowledge'] = graph_atlas.snapshot(ROOT)
        except graph_atlas.repo.KbError as error:
            raise ModelError(f'{context}: {error}') from error
    knowledge = cache['_knowledge']
    layout = manifest['architecture']['layout']
    actual = knowledge.images.get(manifest['rom'])
    if layout not in knowledge.layouts or actual != layout:
        raise ModelError(f'{context}: {manifest["rom"]} belongs to {actual}, not to {layout}')
    view = knowledge.model(layout, manifest['rom'])
    return {'source': view.view_key, 'mode': 'layout', 'layout': layout,
            'image': manifest['rom']}


def _kb_annotations(manifest, knowledge, architecture):
    """Take the annotations of a manifest without ledgers from its KB bindings."""
    if {"reviewed_functions", "map_ledger"} & set(manifest):
        return None
    return knowledge.address_annotations(architecture["layout"], manifest["rom"])


def _bind_objects(objects, architecture, knowledge):
    """Attach semantic search and placement facts without changing geometry."""
    kinds = {'reviewed-function': 'fn', 'function-structure': 'fn',
             'map': 'tbl', 'definition-map': 'tbl', 'kb-map': 'tbl', 'axis': 'axis',
             'definition-axis': 'axis', 'kb-axis': 'axis', 'diagnostic-binding': 'did',
             'dtc-record': 'dtc'}
    layout = architecture['layout']
    for item in objects:
        kind = kinds.get(item['kind'])
        key = f'{layout}-{item["start"]:08x}/{kind}'
        found = knowledge.symbol_keys.get(key)
        if found:
            binding = knowledge.binding(found[0], layout, architecture['image'])
            if binding['symbol'] is not None:
                item['binding'] = binding


def build_rom_model(manifest_path, architecture_cache=None):
    manifest = _load_manifest(manifest_path)
    image_path, image, digest, registry_row = _registry_image(manifest)
    rom_size = len(image)
    warnings = list(manifest.get("warnings", []))
    overrides_path = None
    overrides = {}
    presentation = {}
    if "overrides" in manifest:
        overrides_path = _repo_path(manifest["overrides"])
        overrides, presentation = _presentation(overrides_path, manifest["rom"])

    architecture = knowledge = annotations = None
    if "architecture" in manifest:
        cache = {} if architecture_cache is None else architecture_cache
        architecture = _architecture_binding(manifest, cache)
        knowledge = cache['_knowledge']
        annotations = _kb_annotations(manifest, knowledge, architecture)
    layout = architecture["layout"] if architecture else ""

    objects = []
    objects.extend(_function_objects(manifest, rom_size, warnings, annotations, layout))
    if "map_ledger" in manifest:
        map_objects, axis_uses = _map_objects(manifest, presentation, rom_size)
        objects.extend(map_objects)
        objects.extend(_axis_objects(manifest, axis_uses, rom_size))
    elif "definition_xml" in manifest:
        definition_maps, definition_axes, definition_switches = (
            _definition_xml_objects(manifest, rom_size)
        )
        objects.extend(definition_maps)
        objects.extend(definition_axes)
        objects.extend(definition_switches)
    else:
        warnings.append("Map and axis evidence is not declared for this ROM.")
    if annotations is not None:
        calibrations, conflicts = _kb_calibration_objects(
            annotations, objects, knowledge, manifest["rom"], layout, rom_size
        )
        if conflicts:
            raise ModelError(
                f"{manifest['rom']}: KB table and axis geometry disagrees with the census "
                f"or the published definition: " + "; ".join(conflicts)
            )
        objects.extend(calibrations)

    if "diagnostic_bindings" in manifest:
        objects.extend(_diagnostic_objects(manifest, rom_size))
    else:
        warnings.append("Diagnostic bindings are not declared for this ROM.")
    if "dtc" in manifest:
        objects.extend(_dtc_objects(manifest, rom_size))
    else:
        warnings.append("DTC storage evidence is not declared for this ROM.")
    if overrides_path:
        objects.extend(_switch_objects(overrides_path, overrides, rom_size))
    if "checksum_registry" in manifest:
        objects.extend(_checksum_objects(
            manifest["rom"], manifest["checksum_registry"], rom_size
        ))
    else:
        warnings.append("A checksum layout is not registered for this ROM.")
    objects.extend(_patch_objects(manifest, rom_size, warnings))
    if architecture:
        _bind_objects(objects, architecture, knowledge)
    else:
        warnings.append("A firmware architecture model is not declared for this ROM.")
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

    rom_info = _identity(manifest)
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
            "Annotation source": manifest.get("annotation_source", manifest["rom"]),
        },
        "identity": dict(rom_info),
        "registry": {
            name: value for name, value in registry_row.items() if name != "_line"
        },
        "layout": layout,
        "family": _family(manifest["rom"]),
        "published": _published_tables(manifest),
        "counts": dict(counts),
        "reviewedFunctions": reviewed_functions,
        "structuralFunctions": structural_functions,
        "pageMetrics": _page_metrics(image),
        "warnings": warnings,
        "architecture": architecture,
        "objects": objects,
    }


def build_atlas(manifests):
    values = expand_manifest_values(manifests)
    cache = {}
    roms = [build_rom_model(resolve_manifest(value), cache) for value in values]
    ids = [rom["id"] for rom in roms]
    if len(set(ids)) != len(ids):
        raise ModelError(f"duplicate ROM models: {ids}")
    architectures = {}
    knowledge = cache.get('_knowledge')
    models = knowledge.models.values() if knowledge else []
    for architecture in sorted(models, key=lambda item: item.view_key):
        if architecture.view_key in architectures:
            raise ModelError(f"duplicate architecture models for {architecture.view_key}")
        architectures[architecture.view_key] = architecture.export()
    return {
        "schemaVersion": 1,
        "layers": [{"id": key, "label": label} for key, label in LAYERS],
        "roms": roms,
        "architectures": architectures,
    }
