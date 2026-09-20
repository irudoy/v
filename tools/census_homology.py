#!/usr/bin/env python3
"""Pair the accessor census of two ROMs at table level.

The entities are the ROM operands of registered interpolation entries: the map
in `df_r4` and the axis arrays in `df_r5` and `df_r6`. A target entity receives
a source homolog through three independent methods, applied in this order:

1. `aligned-reference`: a source function and its best target function are
   aligned by instruction shape, and the two entities are the literal values of
   aligned instructions. Every vote of the source entity names one target.
2. `unique-exact-content`: the stored bytes and geometry of an unpaired target
   entity occur once in each census, and the source entity has no pair.
3. `published-registry`: the reviewed definition correspondences and the
   target-native table registry publish both entities under one role. A
   published pair may name a source that a census method pairs with another
   target: the target image stores separate copies of one source table for
   separate readers.

`--check` validates the tracked ledger against the registered stock images and
the published registries without Ghidra exports.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from difflib import SequenceMatcher
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import rom_correspondence, rom_homology  # noqa: E402


LEDGER_FIELDS = (
    "kind",
    "target",
    "geometry",
    "status",
    "source",
    "method",
    "bytes_equal",
    "note",
)
STATUSES = ("homolog", "ambiguous", "unpaired")
METHODS = ("aligned-reference", "unique-exact-content", "published-registry")
UNPAIRED_NOTES = ("flat-content", "duplicate-content", "no-content-match")
ELEMENT_BYTES = {"uint8": 1, "uint16": 2}
MIN_FUNCTION_RATIO = 0.75
MIN_TOKEN_OVERLAP = 0.55
CANDIDATE_LIMIT = 12
NATIVE_REGISTRY = ROOT / "defs" / "vq37-native-tables.toml"
DEFINITION_ADDRESSES = {
    "1ND0A": ROOT / "defs" / "JK08A-1ND.definition-addresses.csv",
    "1ND3B": ROOT / "defs" / "JK08A-1ND.definition-addresses.csv",
    "1ME3B": ROOT / "defs" / "JK08A-1ME3B.definition-addresses.csv",
    "JK78C": ROOT / "defs" / "JK08A-JK78C.definition-addresses.csv",
}


class CensusHomologyError(ValueError):
    """The census inputs or the tracked ledger are inconsistent."""


def ledger_path(source_rom, target_rom):
    return ROOT / "defs" / f"{source_rom}-{target_rom}.census-correspondence.csv"


def _map_geometry(entry):
    width = int(entry["width"])
    height = int(entry["height"]) if entry["height"] else 1
    if entry["family"] == "implicit":
        step = int(entry["step"])
        storage = "uint16" if (width - 1) * step >= 256 else "uint8"
        return f"{width}x{height}:{storage}:step{step}"
    return f"{width}x{height}:{entry['storagetype']}"


def geometry_bytes(geometry):
    """Return the stored size of the largest reading of an entity."""
    sizes = []
    for item in geometry.split("|"):
        parts = item.split(":")
        try:
            cells = 1
            for factor in parts[0].split("x"):
                cells *= int(factor)
            sizes.append(cells * ELEMENT_BYTES[parts[1]])
        except (IndexError, KeyError, ValueError) as error:
            raise CensusHomologyError(f"invalid geometry {geometry!r}") from error
    return max(sizes)


def read_entities(registry_path, export_dir, image_size):
    """Return {address: (kind, geometry)} for every registered ROM operand."""
    registry = rom_correspondence.read_interp(registry_path)
    found = defaultdict(lambda: {"kinds": set(), "geometry": set()})
    cache = {}
    for entry in registry:
        specs = [("map", "df_r4", _map_geometry(entry))]
        if entry["family"] == "explicit":
            specs.append(("axis", "df_r5", f"{entry['width']}:{entry['axistype_x']}"))
            if entry["height"]:
                specs.append(
                    ("axis", "df_r6", f"{entry['height']}:{entry['axistype_y']}")
                )
        for row in rom_correspondence._read_census(export_dir, entry["kernel"], cache):
            if row["wrapper"] != entry["wrapper"]:
                continue
            for kind, field, geometry in specs:
                if not row.get(field):
                    continue
                address = int(row[field], 16)
                if not 0x8000 <= address < image_size:
                    continue
                found[address]["kinds"].add(kind)
                found[address]["geometry"].add((kind, geometry))
    entities = {}
    for address, record in found.items():
        kind = "map" if "map" in record["kinds"] else "axis"
        geometry = "|".join(
            sorted(text for item_kind, text in record["geometry"] if item_kind == kind)
        )
        entities[address] = (kind, geometry)
    return entities


def read_tokens(export_dir):
    """Return {function: instruction shapes in ordinal order}."""
    path = Path(export_dir) / "function_tokens.csv"
    rows = defaultdict(list)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                rows[row["func_addr"]].append((int(row["ordinal"]), row["shape"]))
    except (OSError, KeyError, ValueError) as error:
        raise CensusHomologyError(f"token export cannot be read: {path}") from error
    return {
        function: tuple(shape for _ordinal, shape in sorted(items))
        for function, items in rows.items()
    }


def best_function(source, source_tokens, target_tokens, exact, reserved, target_counts=None):
    """Return (ratio, target) of the best shape alignment, or None."""
    if source in exact:
        return 1.0, exact[source]
    shapes = source_tokens[source]
    counts = Counter(shapes)
    candidates = []
    for target in sorted(target_tokens):
        other = target_tokens[target]
        if target in reserved or not 0.6 * len(shapes) <= len(other) <= 1.6 * len(shapes):
            continue
        other_counts = target_counts[target] if target_counts else Counter(other)
        overlap = sum((counts & other_counts).values()) / max(len(shapes), len(other))
        if overlap > MIN_TOKEN_OVERLAP:
            candidates.append((-overlap, target))
    scored = [
        (-SequenceMatcher(None, shapes, target_tokens[target], autojunk=False).ratio(), target)
        for _overlap, target in sorted(candidates)[:CANDIDATE_LIMIT]
    ]
    if not scored:
        return None
    ratio, target = min(scored)
    return -ratio, target


def aligned_ordinals(source_shapes, target_shapes):
    matcher = SequenceMatcher(None, source_shapes, target_shapes, autojunk=False)
    return {
        left + offset: right + offset
        for left, right, size in matcher.get_matching_blocks()
        for offset in range(size)
    }


def reference_votes(source_export, target_export, source_entities, target_entities):
    """Vote target entities for source entities through aligned literal loads."""
    signatures = [
        rom_correspondence.read_signatures(Path(export) / "function_signatures.csv")
        for export in (source_export, target_export)
    ]
    exact = {
        match.source: match.target
        for match in rom_correspondence.match_functions(*signatures)
    }
    reserved = set(exact.values())
    source_tokens, target_tokens = read_tokens(source_export), read_tokens(target_export)
    target_counts = {function: Counter(shapes) for function, shapes in target_tokens.items()}

    def entity_loads(export, entities):
        loads = defaultdict(lambda: defaultdict(list))
        for row in rom_correspondence.read_function_references(export):
            if row.width == 4 and int(row.value_hex, 16) in entities:
                loads[row.func_addr][row.ordinal].append(int(row.value_hex, 16))
        return loads

    source_loads = entity_loads(source_export, source_entities)
    target_loads = entity_loads(target_export, target_entities)
    votes = defaultdict(Counter)
    for function in sorted(source_loads):
        if function not in source_tokens:
            continue
        best = best_function(
            function, source_tokens, target_tokens, exact, reserved, target_counts
        )
        if best is None or best[0] < MIN_FUNCTION_RATIO:
            continue
        target = best[1]
        ordinals = aligned_ordinals(source_tokens[function], target_tokens[target])
        for ordinal, values in source_loads[function].items():
            peer = ordinals.get(ordinal)
            if peer is None:
                continue
            for value in values:
                for other in target_loads.get(target, {}).get(peer, ()):
                    votes[value][other] += 1
    return votes


def published_pairs(source_rom, target_rom):
    """Return {target address: source address} of roles published for both ROMs."""
    pairs = {}

    def definition_targets(rom):
        path = DEFINITION_ADDRESSES.get(rom)
        if path is None or not path.exists():
            return {}
        with path.open(newline="", encoding="utf-8") as source:
            return {
                (row["entity"], row["source"], row["variant"]): int(row["target"], 16)
                for row in csv.DictReader(source)
                if row["target"]
            }

    left, right = definition_targets(source_rom), definition_targets(target_rom)
    for key in sorted(left.keys() & right.keys()):
        pairs[right[key]] = left[key]
    with NATIVE_REGISTRY.open("rb") as source:
        native = tomllib.load(source)["target"]
    if source_rom in native and target_rom in native:
        for kind in ("table", "axis"):
            left = {
                row["id"]: row["address"]
                for row in native[source_rom].get(kind, ())
                if "address" in row
            }
            for row in native[target_rom].get(kind, ()):
                if "address" in row and row["id"] in left:
                    pairs.setdefault(row["address"], left[row["id"]])
    return pairs


def _stored(image, address, geometry):
    return bytes(image[address : address + geometry_bytes(geometry)])


def build_ledger(source_entities, target_entities, votes, published, images):
    """Classify every target entity and return ledger rows."""
    source_image, target_image = images
    claims = defaultdict(list)
    for source, counter in votes.items():
        for target in counter:
            claims[target].append((source, len(counter) == 1))

    paired = {}
    ambiguous = {}
    for target, items in claims.items():
        clean = sorted(source for source, single in items if single)
        if len(clean) == 1 and source_entities[clean[0]] == target_entities[target]:
            paired[target] = (clean[0], "aligned-reference")
        else:
            ambiguous[target] = sorted(source for source, _single in items)

    def content_index(entities, image):
        index = defaultdict(list)
        for address, (kind, geometry) in entities.items():
            index[(kind, geometry, _stored(image, address, geometry))].append(address)
        return index

    source_content = content_index(source_entities, source_image)
    target_content = content_index(target_entities, target_image)
    notes = {}
    for target in sorted(target_entities):
        if target in paired or target in ambiguous:
            continue
        kind, geometry = target_entities[target]
        key = (kind, geometry, _stored(target_image, target, geometry))
        taken = {source for source, _method in paired.values()}
        candidates = [item for item in source_content.get(key, ()) if item not in taken]
        if len(set(key[2])) <= 1:
            notes[target] = "flat-content"
        elif len(candidates) == 1 and len(target_content[key]) == 1:
            paired[target] = (candidates[0], "unique-exact-content")
        elif candidates:
            notes[target] = "duplicate-content"
        else:
            notes[target] = "no-content-match"

    for target, source in sorted(published.items()):
        if target not in target_entities or source not in source_entities:
            continue
        if target in paired:
            if paired[target][0] != source:
                raise CensusHomologyError(
                    f"{target:08x}: census pair {paired[target][0]:08x} contradicts "
                    f"the published pair {source:08x}"
                )
            continue
        paired[target] = (source, "published-registry")
        ambiguous.pop(target, None)
        notes.pop(target, None)

    rows = []
    for target in sorted(target_entities):
        kind, geometry = target_entities[target]
        row = dict.fromkeys(LEDGER_FIELDS, "")
        row.update(kind=kind, target=f"{target:08x}", geometry=geometry)
        if target in paired:
            source, method = paired[target]
            equal = _stored(source_image, source, geometry) == _stored(
                target_image, target, geometry
            )
            row.update(
                status="homolog",
                source=f"{source:08x}",
                method=method,
                bytes_equal="yes" if equal else "no",
            )
        elif target in ambiguous:
            row.update(
                status="ambiguous",
                note=" ".join(f"{item:08x}" for item in ambiguous[target]),
            )
        else:
            row.update(status="unpaired", note=notes[target])
        rows.append(row)
    return rows


def read_ledger(path):
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != LEDGER_FIELDS:
                raise CensusHomologyError(
                    f"{path}: header {reader.fieldnames}; expected {list(LEDGER_FIELDS)}"
                )
            return list(reader)
    except OSError as error:
        raise CensusHomologyError(f"ledger cannot be read: {path}") from error


def write_ledger(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_ledger(rows, source_rom, target_rom, images=None):
    """Validate a ledger against the stock images and the published registries."""
    if images is None:
        registered = rom_homology.load_images()
        images = (registered[source_rom].data, registered[target_rom].data)
    source_image, target_image = images
    targets = [row["target"] for row in rows]
    if targets != sorted(set(targets)):
        raise CensusHomologyError("ledger targets must be unique and ascending")
    automatic = Counter(
        row["source"]
        for row in rows
        if row["status"] == "homolog" and row["method"] != "published-registry"
    )
    repeated = sorted(source for source, count in automatic.items() if count > 1)
    if repeated:
        raise CensusHomologyError(
            f"census methods pair one source with two targets: {', '.join(repeated)}"
        )
    by_target = {}
    for row in rows:
        context = f"target {row['target']}"
        if row["kind"] not in {"map", "axis"} or row["status"] not in STATUSES:
            raise CensusHomologyError(f"{context}: invalid kind or status")
        target = int(row["target"], 16)
        size = geometry_bytes(row["geometry"])
        if target + size > len(target_image):
            raise CensusHomologyError(f"{context}: entity lies outside the image")
        if row["status"] == "homolog":
            if row["method"] not in METHODS:
                raise CensusHomologyError(f"{context}: invalid method")
            source = int(row["source"], 16)
            equal = (
                source_image[source : source + size]
                == target_image[target : target + size]
            )
            if row["bytes_equal"] != ("yes" if equal else "no"):
                raise CensusHomologyError(f"{context}: bytes_equal differs from the images")
            if row["method"] == "unique-exact-content" and not equal:
                raise CensusHomologyError(f"{context}: content pair is not exact")
            by_target[target] = source
        elif row["source"] or row["method"] or row["bytes_equal"]:
            raise CensusHomologyError(f"{context}: unpaired row names a pair")
        elif row["status"] == "unpaired" and row["note"] not in UNPAIRED_NOTES:
            raise CensusHomologyError(f"{context}: invalid note")
    for target, source in published_pairs(source_rom, target_rom).items():
        if target in by_target and by_target[target] != source:
            raise CensusHomologyError(
                f"target {target:08x}: ledger source {by_target[target]:08x} "
                f"contradicts the published source {source:08x}"
            )
    return summarize(rows)


def summarize(rows):
    summary = {}
    for kind in ("map", "axis"):
        subset = [row for row in rows if row["kind"] == kind]
        counts = Counter(row["status"] for row in subset)
        methods = Counter(row["method"] for row in subset if row["method"])
        summary[kind] = {
            "total": len(subset),
            **{status: counts.get(status, 0) for status in STATUSES},
            **{method: methods.get(method, 0) for method in METHODS},
            "bytes_equal": sum(row["bytes_equal"] == "yes" for row in subset),
        }
    return summary


def render_summary(summary):
    return "\n".join(
        f"{kind}: " + " ".join(f"{key}={value}" for key, value in values.items())
        for kind, values in summary.items()
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", default="1ND0A")
    parser.add_argument("--target", default="1ME3B")
    parser.add_argument("--source-export", type=Path)
    parser.add_argument("--target-export", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    path = args.output or ledger_path(args.source, args.target)
    try:
        if args.check:
            summary = validate_ledger(read_ledger(path), args.source, args.target)
            print(render_summary(summary))
            print(f"status=PASS ledger={path.relative_to(ROOT)}")
            return 0
        if args.source_export is None or args.target_export is None:
            parser.error("--source-export and --target-export are required")
        registered = rom_homology.load_images()
        images = (registered[args.source].data, registered[args.target].data)
        source_entities = read_entities(
            ROOT / "defs" / f"{args.source}.interp.csv", args.source_export, len(images[0])
        )
        target_entities = read_entities(
            ROOT / "defs" / f"{args.target}.interp.csv", args.target_export, len(images[1])
        )
        votes = reference_votes(
            args.source_export, args.target_export, source_entities, target_entities
        )
        rows = build_ledger(
            source_entities,
            target_entities,
            votes,
            published_pairs(args.source, args.target),
            images,
        )
        write_ledger(path, rows)
        print(render_summary(validate_ledger(rows, args.source, args.target, images)))
        print(f"source_entities={len(source_entities)} output={path}")
        return 0
    except (
        CensusHomologyError,
        rom_correspondence.CorrespondenceError,
        rom_homology.HomologyError,
    ) as error:
        print(f"census_homology: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
