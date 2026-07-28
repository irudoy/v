#!/usr/bin/env python3
"""Complete reproducible ingestion of one ROM into Memgraph.

Node-owner order is fixed:
  load_graph.py -> load_xrefs.py -> load_maps.py -> load_code.py
  -> load_diagnostic_bindings.py -> audit

Invocation:
  uv run --no-project --with neo4j python tools/memgraph/ingest.py JK08A
"""
import argparse
import csv
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import load_code  # noqa: E402
import load_diagnostic_bindings  # noqa: E402
import load_maps  # noqa: E402
import rom_sources  # noqa: E402
from provenance import ProvenanceError, analyze_claims  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MEMGRAPH = Path(__file__).resolve().parent

EXPORT_HEADERS = {
    "funcs.csv": ["addr", "name", "size", "is_thunk", "is_external"],
    "calls.csv": ["src", "dst"],
    "xrefs.csv": ["func_addr", "periph_addr", "kind"],
}
BOOL_VALUES = frozenset({"true", "false"})
XREF_KINDS = frozenset({"R", "W", "D", "L", "?"})
STABLE_PYTHON = ["uv", "run", "--no-project", "--with", "neo4j", "python"]


class IngestError(ProvenanceError):
    pass


def read_export(path, expected):
    if not path.exists():
        raise IngestError(f"export input not found: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != expected:
            raise IngestError(
                f"{path}: header {reader.fieldnames}; expected {expected}"
            )
        return list(reader)


def export_error(path, row_number, message):
    raise IngestError(f"{path}:{row_number}: {message}")


def check_export_addr(path, row_number, column, value):
    if not isinstance(value, str) or not load_code.ADDR_RE.match(value):
        export_error(
            path, row_number,
            f"{column} is not eight lowercase hexadecimal digits: {value!r}",
        )


def validate_exports(exported, export_dir):
    """Validate export values and foreign keys before the first loader runs."""
    funcs_path = export_dir / "funcs.csv"
    func_addrs = set()
    for row_number, row in enumerate(exported["funcs.csv"], 2):
        if None in row or any(value is None for value in row.values()):
            export_error(funcs_path, row_number, "field count does not match the header")
        check_export_addr(funcs_path, row_number, "addr", row["addr"])
        if row["addr"] in func_addrs:
            export_error(funcs_path, row_number, f"duplicate addr {row['addr']}")
        func_addrs.add(row["addr"])
        if not row["size"].isdecimal() or int(row["size"]) <= 0:
            export_error(
                funcs_path, row_number,
                f"size is not a positive decimal number: {row['size']!r}",
            )
        for column in ("is_thunk", "is_external"):
            if row[column] not in BOOL_VALUES:
                export_error(
                    funcs_path, row_number,
                    f"{column} is outside {sorted(BOOL_VALUES)}: {row[column]!r}",
                )

    calls_path = export_dir / "calls.csv"
    for row_number, row in enumerate(exported["calls.csv"], 2):
        if None in row or any(value is None for value in row.values()):
            export_error(calls_path, row_number, "field count does not match the header")
        for column in ("src", "dst"):
            check_export_addr(calls_path, row_number, column, row[column])
            if row[column] not in func_addrs:
                export_error(
                    calls_path, row_number,
                    f"{column}={row[column]} is absent from funcs.csv",
                )

    xrefs_path = export_dir / "xrefs.csv"
    for row_number, row in enumerate(exported["xrefs.csv"], 2):
        if None in row or any(value is None for value in row.values()):
            export_error(xrefs_path, row_number, "field count does not match the header")
        check_export_addr(xrefs_path, row_number, "func_addr", row["func_addr"])
        check_export_addr(xrefs_path, row_number, "periph_addr", row["periph_addr"])
        if row["func_addr"] not in func_addrs:
            export_error(
                xrefs_path, row_number,
                f"func_addr={row['func_addr']} is absent from funcs.csv",
            )
        if row["kind"] not in XREF_KINDS:
            export_error(
                xrefs_path, row_number,
                f"kind is outside {sorted(XREF_KINDS)}: {row['kind']!r}",
            )
    return func_addrs


def read_code_sources(rom):
    model = rom_sources.resolve(rom)
    rom_sources.verify_image_binding(model)
    paths = rom_sources.definition_paths(model)
    funcs = load_code.read_rows(str(paths["Func"]), load_code.FUNC_FIELDS)
    vars_ = load_code.read_rows(str(paths["Reg"]), load_code.VAR_FIELDS)
    maps = load_code.read_rows(str(paths["Map"]), load_code.MAP_FIELDS)
    axes = load_code.read_rows(str(paths["Axis"]), load_code.AXIS_FIELDS)
    funcs = rom_sources.materialize_rows(model, "Func", funcs)
    vars_ = rom_sources.materialize_rows(model, "Reg", vars_)
    maps = rom_sources.materialize_rows(model, "Map", maps)
    axes = rom_sources.materialize_rows(model, "Axis", axes)
    load_code.check_func_contracts(funcs, str(paths["Func"]))
    claims = load_code.source_claims(rom, [
        ("Func", funcs, str(paths["Func"])),
        ("Reg", vars_, str(paths["Reg"])),
        ("Map", maps, str(paths["Map"])),
        ("Axis", axes, str(paths["Axis"])),
    ])
    return model, paths, funcs, vars_, maps, axes, claims


def preflight_maps(export_dir, rom, model, paths):
    registry = paths["Interp"]
    reg = load_maps.read_registry(str(registry))
    rows, _ = load_maps.read_censuses(str(export_dir), reg, str(registry))
    load_maps.check_dims(
        rows, {entry["wrapper"]: 2 if entry["height"] else 1 for entry in reg}
    )
    maps, axes, _, _, accesses, _ = load_maps.build(rows)
    load_maps.apply_findings(str(paths["Map"]), maps, accesses, model)
    load_maps.apply_axis_facts(str(paths["Axis"]), axes, model)
    image = load_maps.romkit.load(rom)
    load_maps.characterize(image, maps, axes)
    return registry, maps, axes, accesses


def claim_inventory(export_funcs, xrefs, funcs, vars_, maps, axes):
    inventory = {
        "Func": {
            row["addr"]: {"confidence": "", "contract_conf": ""}
            for row in export_funcs
        },
        "Reg": {
            row["periph_addr"]: {"confidence": ""} for row in xrefs
        },
        "Map": {
            addr: {
                "confidence": row.get("confidence", ""),
                "scale_conf": row.get("scale_conf", ""),
            }
            for addr, row in maps.items()
        },
        "Axis": {
            addr: {
                "confidence": row.get("confidence", ""),
                "scale_conf": row.get("scale_conf", ""),
            }
            for addr, row in axes.items()
        },
    }
    for row in funcs:
        if row["addr"] not in inventory["Func"]:
            raise IngestError(
                f"defs function {row['addr']} is absent from exported funcs.csv"
            )
        inventory["Func"][row["addr"]].update(
            confidence=row["confidence"],
            contract_conf=row["contract_conf"],
        )
    for row in vars_:
        inventory["Reg"].setdefault(row["addr"], {})
        inventory["Reg"][row["addr"]]["confidence"] = row["confidence"]
    return inventory


def preflight(export_dir, rom, strict):
    exported = {
        name: read_export(export_dir / name, header)
        for name, header in EXPORT_HEADERS.items()
    }
    exported_func_addrs = validate_exports(exported, export_dir)

    model, paths, funcs, vars_, _, _, claims = read_code_sources(rom)
    binding_rows = load_diagnostic_bindings.validate_rows(
        load_diagnostic_bindings.read_rows(paths["DiagnosticBinding"]),
        paths["DiagnosticBinding"],
    )
    binding_rows = load_diagnostic_bindings.materialize_rows(
        model, binding_rows
    )
    registry, maps, axes, accesses = preflight_maps(
        export_dir, rom, model, paths
    )

    orphans = sorted({
        row["accessor"] for row in accesses
        if row["accessor"] not in exported_func_addrs
    })
    if orphans:
        raise IngestError(
            f"export predates RecoverFuncs: {len(orphans)} accessors without Func nodes: "
            f"{orphans[:10]}"
        )

    inventory = claim_inventory(
        exported["funcs.csv"], exported["xrefs.csv"], funcs, vars_, maps, axes
    )
    dependencies, gaps, levels, grounded = load_code.resolve_claim_dependencies(
        rom, claims, inventory
    )
    load_code.require_no_gaps(gaps)
    analysis = analyze_claims(levels, dependencies, grounded)
    code = {
        claim for claim, level in levels.items()
        if level in ("code", "silicon")
    }
    below = [
        claim for claim in code if analysis.effective[claim] != levels[claim]
    ]
    ungrounded = [claim for claim in code if not analysis.grounded[claim]]
    if strict and (below or ungrounded):
        raise IngestError(
            f"strict provenance: below declared={len(below)}, "
            f"without grounding={len(ungrounded)}"
        )
    print(
        f"Preflight {rom}: funcs={len(exported['funcs.csv'])}, "
        f"xrefs={len(exported['xrefs.csv'])}, maps={len(maps)}, axes={len(axes)}, "
        f"claims={len(levels)}, RESTS_ON={len(dependencies)}, "
        f"diagnostic_bindings={len(binding_rows)}"
    )
    print(
        f"  annotation source={model.source}, mode={model.kind}, "
        f"value image={rom}"
    )
    print(
        f"  code/silicon below declared={len(below)}, "
        f"without grounding={len(ungrounded)}, cyclic_SCC={len(analysis.cyclic_components)}"
    )
    return registry, model, paths


def commands(export_dir, rom, registry, paths, strict):
    python = sys.executable
    result = [
        [python, str(MEMGRAPH / "load_graph.py"), str(export_dir), rom],
        [python, str(MEMGRAPH / "load_xrefs.py"), str(export_dir), rom],
        [
            python, str(MEMGRAPH / "load_maps.py"), str(export_dir), rom,
            str(registry), str(paths["Map"]), str(paths["Axis"]),
        ],
        [python, str(MEMGRAPH / "load_code.py"), rom],
        [python, str(MEMGRAPH / "load_diagnostic_bindings.py"), rom],
        [python, str(MEMGRAPH / "provenance_report.py"), "audit", rom],
    ]
    if strict:
        result[-1].append("--strict")
    return result


def display_command(command):
    """Return a stable command that remains valid after the temporary uv environment is removed."""
    return [*STABLE_PYTHON, *command[1:]]


def parser():
    out = argparse.ArgumentParser(description=__doc__)
    out.add_argument("rom", nargs="?", default="JK08A")
    out.add_argument(
        "--export-dir", type=Path,
        help="Ghidra export directory; default: canonical directory registered for the ROM",
    )
    out.add_argument(
        "--strict", action="store_true",
        help="treat an effective downgrade or missing grounding as an error",
    )
    out.add_argument(
        "--dry-run", action="store_true",
        help="run preflight and display commands without changing the graph",
    )
    return out


def main():
    args = parser().parse_args()
    export_dir = (
        args.export_dir.expanduser().resolve()
        if args.export_dir
        else rom_sources.default_export_dir(args.rom)
    )
    try:
        registry, model, paths = preflight(export_dir, args.rom, args.strict)
    except (OSError, ProvenanceError, ValueError) as error:
        sys.exit(str(error))

    steps = commands(export_dir, args.rom, registry, paths, args.strict)
    for number, command in enumerate(steps, 1):
        print(
            f"[{number}/{len(steps)}] {shlex.join(display_command(command))}",
            flush=True,
        )
        if args.dry_run:
            continue
        try:
            subprocess.run(command, cwd=ROOT, check=True)
        except subprocess.CalledProcessError as error:
            return error.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
