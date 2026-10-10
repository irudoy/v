#!/usr/bin/env python3
"""Single annotation source for exact-code ROMs without copying defs/<rom>.*.

The code structure of a ROM is the L0 of its layout in `l0/<layout>/`, and the
curated function names of the layout are in `tools/ghidra/symbols/<layout>.csv`.
"""

from dataclasses import dataclass
import csv
import hashlib
from pathlib import Path
import re
import tomllib

from kb import l0 as kb_l0
from kb import repo as kb_repo


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "defs" / "rom-inheritance.toml"
IMAGE_REGISTRY = ROOT / "rom-images" / "roms.csv"
L0_ROOT = Path("l0")
SYMBOL_ROOT = Path("tools/ghidra/symbols")
SYMBOL_HEADER = "addr,name,note"
# Machine-local research exports: decompilations, listings, and the review
# inputs that L0 does not carry, such as diagnostic_refs.csv.
EXPORT_ROOT = Path("~/tools/ghidra-projects").expanduser()
EXACT_EXPORT_NAMES = {
    "JK08A": "export-JK08A-exact",
}
ROM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
ADDRESS_RE = re.compile(r"^[0-9a-f]{8}$")
FUNCTION_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
KINDS = frozenset({"exact-code"})
FIELDS = frozenset({
    "source", "kind", "target_sha256", "source_sha256", "ranges", "evidence",
})
PROSE_FIELDS = {
    "Func": frozenset({"semantics", "contract", "note"}),
    "Reg": frozenset({"semantics", "units", "note"}),
    "Map": frozenset({"semantics", "units", "note"}),
    "Axis": frozenset({"kind", "units", "note"}),
    "DiagnosticBinding": frozenset({"note"}),
}


class SourceModelError(ValueError):
    pass


@dataclass(frozen=True)
class SourceModel:
    target: str
    source: str
    kind: str
    target_sha256: str = ""
    source_sha256: str = ""
    ranges: tuple = ()
    evidence: str = ""

    @property
    def inherited(self):
        return self.target != self.source


def _read_registry(path):
    path = Path(path)
    try:
        with path.open("rb") as fh:
            document = tomllib.load(fh)
    except OSError as error:
        raise SourceModelError(f"ROM inheritance registry not found: {path}") from error
    unknown_top = sorted(set(document) - {"inherit"})
    if unknown_top:
        raise SourceModelError(
            f"{path}: unknown top-level sections {unknown_top}"
        )
    entries = document.get("inherit", {})
    if not isinstance(entries, dict):
        raise SourceModelError(f"{path}: inherit must be a TOML table")
    return path, entries


def read_registry(path=DEFAULT_REGISTRY):
    path, raw = _read_registry(path)
    entries = {}
    for target, row in raw.items():
        if not ROM_RE.fullmatch(target) or not isinstance(row, dict):
            raise SourceModelError(f"{path}: invalid inherit.{target} entry")
        unknown = sorted(set(row) - FIELDS)
        if unknown:
            raise SourceModelError(
                f"{path}: inherit.{target} contains unknown fields {unknown}"
            )
        missing = sorted(FIELDS - set(row))
        if missing:
            raise SourceModelError(
                f"{path}: inherit.{target} is missing fields {missing}"
            )
        source = row["source"]
        kind = row["kind"]
        if not isinstance(source, str) or not ROM_RE.fullmatch(source):
            raise SourceModelError(
                f"{path}: inherit.{target}.source is not a ROM label"
            )
        if source == target:
            raise SourceModelError(
                f"{path}: inherit.{target} references itself"
            )
        if kind not in KINDS:
            raise SourceModelError(
                f"{path}: inherit.{target}.kind={kind!r} is not in {sorted(KINDS)}"
            )
        for field in ("target_sha256", "source_sha256"):
            if not isinstance(row[field], str) or not SHA256_RE.fullmatch(row[field]):
                raise SourceModelError(
                    f"{path}: inherit.{target}.{field} is not a SHA-256"
                )
        ranges = row["ranges"]
        if not isinstance(ranges, list) or not ranges:
            raise SourceModelError(
                f"{path}: inherit.{target}.ranges must be a nonempty array"
            )
        parsed_ranges = []
        for value in ranges:
            if not isinstance(value, str) or not re.fullmatch(
                r"0x[0-9a-fA-F]+:0x[0-9a-fA-F]+", value
            ):
                raise SourceModelError(
                    f"{path}: inherit.{target}.ranges contains invalid value {value!r}"
                )
            start_text, end_text = value.split(":", 1)
            start, end = int(start_text, 16), int(end_text, 16)
            if start >= end:
                raise SourceModelError(
                    f"{path}: inherit.{target}.ranges contains empty range {value}"
                )
            parsed_ranges.append((start, end, value))
        ordered = sorted(parsed_ranges)
        if parsed_ranges != ordered or any(
            left[1] > right[0] for left, right in zip(ordered, ordered[1:])
        ):
            raise SourceModelError(
                f"{path}: inherit.{target}.ranges are unordered or overlap"
            )
        if not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise SourceModelError(
                f"{path}: inherit.{target}.evidence is empty"
            )
        entries[target] = SourceModel(
            target=target,
            source=source,
            kind=kind,
            target_sha256=row["target_sha256"],
            source_sha256=row["source_sha256"],
            ranges=tuple(ranges),
            evidence=row["evidence"],
        )

    chained = sorted(
        target for target, model in entries.items() if model.source in entries
    )
    if chained:
        raise SourceModelError(
            f"{path}: inheritance chains are forbidden; targets: {chained}"
        )
    return entries


def resolve(rom, path=DEFAULT_REGISTRY):
    if not isinstance(rom, str) or not ROM_RE.fullmatch(rom):
        raise SourceModelError(f"invalid ROM label {rom!r}")
    return read_registry(path).get(
        rom,
        SourceModel(target=rom, source=rom, kind="canonical"),
    )


def default_export_dir(rom):
    """Return the machine-local research export directory for a ROM label."""
    if not isinstance(rom, str) or not ROM_RE.fullmatch(rom):
        raise SourceModelError(f"invalid ROM label {rom!r}")
    return EXPORT_ROOT / EXACT_EXPORT_NAMES.get(rom, f"export-{rom}")


def layout_of(rom, root=ROOT):
    """Return the id of the layout whose L0 holds the code of a ROM.

    A family that inherits addresses has one layout for all its members;
    every other family has one layout per member.
    """
    if not isinstance(rom, str) or not ROM_RE.fullmatch(rom):
        raise SourceModelError(f"invalid ROM label {rom!r}")
    for layout in kb_repo.layouts(root).values():
        if rom in layout.images:
            return layout.id
    raise SourceModelError(
        f"ROM {rom} belongs to no layout of rom-images/homology.toml"
    )


def l0_dir(rom, root=ROOT):
    """Return the tracked L0 directory of a ROM's layout."""
    return root / L0_ROOT / layout_of(rom, root)


def verify_l0(rom, root=ROOT):
    """Hold the L0 of a ROM's layout to its manifest, the pins, and the catalog."""
    failures = kb_l0.check_all(root, only={layout_of(rom, root)})
    if failures:
        raise SourceModelError(
            "L0 check failed: " + "; ".join(str(failure) for failure in failures[:5])
        )


def function_names(rom, root=ROOT):
    """Return {entry address: curated name} of the layout of a ROM.

    Every row names a function entry of the layout's L0 once, and every name
    is unique. A layout without a registry has no curated names.
    """
    layout = layout_of(rom, root)
    path = root / SYMBOL_ROOT / f"{layout}.csv"
    if not path.exists():
        return {}
    with (root / L0_ROOT / layout / "funcs.csv").open(newline="", encoding="utf-8") as source:
        entries = {row["addr"] for row in csv.DictReader(source)}
    names = {}
    header = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        where = f"{path.relative_to(root)}:{number}"
        if not line.strip() or line.startswith("#"):
            continue
        if not header:
            if line != SYMBOL_HEADER:
                raise SourceModelError(f"{where}: header must be {SYMBOL_HEADER}")
            header = True
            continue
        fields = line.split(",")
        if len(fields) != 3:
            raise SourceModelError(f"{where}: expected addr,name,note without commas in note")
        addr, name, _ = fields
        if not ADDRESS_RE.fullmatch(addr):
            raise SourceModelError(f"{where}: addr is not eight lowercase hexadecimal digits")
        if not FUNCTION_NAME_RE.fullmatch(name):
            raise SourceModelError(f"{where}: invalid function name {name!r}")
        if addr not in entries:
            raise SourceModelError(f"{where}: {addr} is not a function entry of l0/{layout}")
        if addr in names:
            raise SourceModelError(f"{where}: {addr} is named twice")
        if name in names.values():
            raise SourceModelError(f"{where}: {name} names two functions")
        names[addr] = name
    if not header:
        raise SourceModelError(f"{path.relative_to(root)}: header {SYMBOL_HEADER} is missing")
    return names


def function_name(names, addr):
    """Return the curated name of a function entry or its generated name."""
    return names.get(addr, f"FUN_{addr}")


def definition_paths(model, root=ROOT):
    defs = root / "defs"
    return {
        "Func": defs / f"{model.source}.funcs.csv",
        "Reg": defs / f"{model.source}.vars.csv",
        "Map": defs / f"{model.source}.findings.csv",
        "Axis": defs / f"{model.source}.axes.csv",
        "Interp": defs / f"{model.source}.interp.csv",
        "DiagnosticBinding": defs / f"{model.source}.diagnostic-bindings.csv",
    }


def materialize_rows(model, label, rows):
    """Substitute the target label only in human-readable shared-source fields."""
    if not model.inherited:
        return rows
    fields = PROSE_FIELDS.get(label, ())
    return [
        {
            key: (
                value.replace(model.source, model.target)
                if key in fields and isinstance(value, str)
                else value
            )
            for key, value in row.items()
        }
        for row in rows
    ]


def verify_image_binding(model, path=IMAGE_REGISTRY):
    """Bind an exact-code relationship to specific images, not only labels."""
    if not model.inherited:
        return
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as error:
        raise SourceModelError(f"image registry not found: {path}") from error
    by_rom = {}
    for row in rows:
        rom = row.get("rom", "")
        if not rom:
            continue
        if rom in by_rom:
            raise SourceModelError(f"{path}: ROM {rom} is declared more than once")
        by_rom[rom] = row
    expected = {
        model.target: model.target_sha256,
        model.source: model.source_sha256,
    }
    bad = [
        f"{rom}: registry={by_rom.get(rom, {}).get('sha256')!r}, "
        f"inheritance={digest!r}"
        for rom, digest in expected.items()
        if by_rom.get(rom, {}).get("sha256") != digest
    ]
    if bad:
        raise SourceModelError(
            "exact-code inheritance does not match the image registry: "
            + "; ".join(bad)
        )
    images = {}
    for rom, digest in expected.items():
        image_path = path.parent / by_rom[rom]["path"]
        try:
            data = image_path.read_bytes()
        except OSError as error:
            raise SourceModelError(f"exact-code ROM image not found: {image_path}") from error
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            raise SourceModelError(
                f"{image_path}: SHA-256 is {actual}, expected {digest}"
            )
        images[rom] = data
    target_data = images[model.target]
    source_data = images[model.source]
    for value in model.ranges:
        start_text, end_text = value.split(":", 1)
        start, end = int(start_text, 16), int(end_text, 16)
        if end > len(target_data) or end > len(source_data):
            raise SourceModelError(
                f"exact-code range {value} exceeds one of the images"
            )
        if target_data[start:end] != source_data[start:end]:
            raise SourceModelError(
                f"exact-code range {value} differs between "
                f"{model.target}/{model.source}"
            )
