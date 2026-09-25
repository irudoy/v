"""Interpolation registries and their correspondences (tools/kb/SPEC.md,
section 20.3).

- `interp` of `[l0.census.<layout>]` in `tools/kb/config.toml` names the
  registry of each layout. A registry belongs to the layout of the image in
  its file name; another layout that the census gives the same registry takes
  a row only where L0 hashes its wrapper and kernel functions to the same
  exact bytes, and those symbols join with `byte-identical` evidence.
- Each row gives `[interp]` of the meaning of its wrapper's `fn` symbol:
  `family` as `access`, `width` and `height` as `cols` and `rows`, `step`,
  `storagetype` as `storage`, and the axis types as `x_storage` and
  `y_storage`. `kernel` names the L0 function that holds the kernel entry,
  and `offset` gives the distance of the entry from that function's entry
  when the entry lies inside it, as the shift chains of the implicit kernels
  do.
- Each `mapped` row of `defs/JK08A-<ROM>.interp-correspondence.csv` joins
  the wrapper and kernel symbols of the image's layout to the `7mfk` symbols
  of its source entry with `interp-contract` evidence; an `unsupported` row
  gives the source wrapper the status `unresolved` there.
"""

from collections import defaultdict
import csv
from pathlib import Path
import re

from kb import repo

DEFS = Path("defs")
REGISTRY = re.compile(r"(?:.*/)?([0-9A-Z]+)\.interp\.csv")
CORRESPONDENCE = "JK08A-*.interp-correspondence.csv"
CANONICAL = "7mfk"
FIELDS = ("family", "kernel", "wrapper", "width", "height", "step", "storagetype",
          "axistype_x", "axistype_y")
PAIR_FIELDS = ("source_kernel", "source_wrapper", "target_kernel", "target_wrapper")
STATUSES = ("mapped", "unsupported")


def registries(config):
    """{registry path: layouts} from `[l0.census.<layout>]` of the configuration."""
    found = defaultdict(list)
    for layout, settings in sorted(config.get("l0", {}).get("census", {}).items()):
        found[settings["interp"]].append(layout)
    return dict(found)


def inputs(root):
    paths = set(registries(repo.config(root)))
    paths.update(path.relative_to(root).as_posix()
                 for path in (root / DEFS).glob(CORRESPONDENCE))
    return sorted(paths)


def _rows(b, root, path, fields):
    with (root / path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        header = tuple(reader.fieldnames or ())
        if header not in fields:
            b.issue("schema", path, "header", f"columns {list(header)}; expected "
                    + " or ".join(str(list(item)) for item in fields))
            return []
        return list(reader)


def _owners(root, layout, addresses):
    """{address: function entries} of the L0 functions whose bodies hold an
    instruction at each address."""
    found = defaultdict(list)
    if not addresses:
        return found
    data = (root / repo.L0 / layout / "function_tokens.csv").read_bytes()
    wanted = b"|".join(f"{address:08x}".encode() for address in sorted(addresses))
    for match in re.finditer(rb"^([0-9a-f]{8}),(%b)," % wanted, data, re.M):
        found[int(match.group(2), 16)].append(int(match.group(1), 16))
    return found


def _signatures(root, layout):
    """{function entry: SHA-256 of its exact bytes} from the L0 of a layout."""
    path = root / repo.L0 / layout / "function_signatures.csv"
    with path.open(newline="", encoding="utf-8") as source:
        return {int(row["addr"], 16): row["exact_sha256"] for row in csv.DictReader(source)}


class Entries:
    """The L0 function that holds each kernel entry of a layout, read from L0
    on the first question."""

    def __init__(self, b, root, layout, entries):
        self.b, self.root, self.layout, self.entries = b, root, layout, entries
        self.found = None

    def __call__(self, entry):
        """(function entry, offset) of the function that holds the entry, or None."""
        if self.found is None:
            inner = {item for item in self.entries if not self.b.is_function(self.layout, item)}
            owners = _owners(self.root, self.layout, inner)
            self.found = {item: (item, 0) for item in self.entries if item not in inner}
            for item in inner:
                holders = owners.get(item, [])
                if len(holders) == 1:
                    self.found[item] = (holders[0], item - holders[0])
        return self.found.get(entry)


def declare(b, root):
    layout_of = {rom: layout.id for layout in b.layouts.values() for rom in layout.images}
    entries = {}
    for path, layouts in sorted(registries(b.config).items()):
        rom = REGISTRY.fullmatch(path)
        own = layout_of.get(rom.group(1)) if rom else None
        if own not in layouts:
            b.issue("schema", path, "registry", f"the registry of {own or 'no layout'} serves "
                    f"the census of {', '.join(layouts)}")
            continue
        rows = _rows(b, root, path, (FIELDS,))
        kernels = {int(row["kernel"], 16) for row in rows}
        entries[own] = Entries(b, root, own, kernels)
        _declare_registry(b, path, own, rows, entries[own])
        for layout in layouts:
            if layout != own:
                entries[layout] = Entries(b, root, layout, kernels)
                _declare_copies(b, root, path, own, layout, rows, entries[own])
    for path in sorted((root / DEFS).glob(CORRESPONDENCE)):
        _declare_pairs(b, root, path.relative_to(root).as_posix(), layout_of, entries)


def _integer(text):
    return int(text) if text else None


def _declare_registry(b, path, layout, rows, entries):
    seen = set()
    for number, row in enumerate(rows, start=2):
        where = f"{path}:{number}"
        wrapper, kernel = int(row["wrapper"], 16), int(row["kernel"], 16)
        if wrapper in seen:
            b.issue("schema", where, row["wrapper"], "a second row of the wrapper")
            continue
        seen.add(wrapper)
        if not b.is_function(layout, wrapper):
            b.issue("symbols", where, row["wrapper"],
                    f"the wrapper is no function entry of l0/{layout}/funcs.csv")
            continue
        holder = entries(kernel)
        if holder is None:
            b.issue("symbols", where, row["kernel"],
                    f"no function of l0/{layout} holds an instruction at the kernel entry")
            continue
        function, offset = holder
        interp = {
            "access": row["family"],
            "kernel": b.symbol(layout, "fn", function, path),
            "offset": offset or None,
            "cols": _integer(row["width"]),
            "rows": _integer(row["height"]),
            "step": _integer(row["step"]),
            "storage": row["storagetype"] or None,
            "x_storage": row["axistype_x"] or None,
            "y_storage": row["axistype_y"] or None,
        }
        b.keys(b.symbol(layout, "fn", wrapper, path),
               {"interp": {name: value for name, value in interp.items() if value is not None}},
               path)


def _declare_copies(b, root, path, own, layout, rows, entries):
    """The symbols of a registry on another layout whose L0 functions carry the
    same exact bytes at the same entries."""
    ours, theirs = _signatures(root, own), _signatures(root, layout)
    functions = set()
    for row in rows:
        functions.add(int(row["wrapper"], 16))
        holder = entries(int(row["kernel"], 16))
        if holder is not None:
            functions.add(holder[0])
    for function in sorted(functions):
        digest = ours.get(function)
        if digest is None:
            continue
        if theirs.get(function) != digest:
            b.issue("audit", path, f"{layout}:{function:08x}",
                    f"the function differs from {own}:{function:08x}, so the row does not "
                    f"carry to {layout}")
            continue
        origin = b.symbol(own, "fn", function, path)
        key = b.symbol(layout, "fn", function, path, evidence=[{
            "kind": "byte-identical", "supports": "homology",
            "at": f"{layout}:{function:08x}", "to": origin, "sha256": digest}])
        b.join(origin, key, path)


def _declare_pairs(b, root, path, layout_of, entries):
    rom = Path(path).name.split(".")[0].split("-", 1)[1]
    layout = layout_of.get(rom)
    if layout is None or layout not in entries or CANONICAL not in entries:
        b.issue("schema", path, rom, "no census registry of the image or of the canonical layout")
        return
    rows = _rows(b, root, path, (PAIR_FIELDS + ("evidence",),
                                 PAIR_FIELDS + ("status", "evidence")))
    for number, row in enumerate(rows, start=2):
        where = f"{path}:{number}"
        status = row.get("status") or "mapped"
        subject = f"{row['source_kernel']}:{row['source_wrapper']}"
        if status not in STATUSES:
            b.issue("schema", where, subject, f"unknown status {status}")
            continue
        wrapper = b.symbol(CANONICAL, "fn", int(row["source_wrapper"], 16), path)
        if status == "unsupported":
            b.status(wrapper, layout, "unresolved", path, props={
                "method": "interp-contract", "target": wrapper.location, "count": 0,
                "note": row["evidence"]}, evidence=[{
                    "kind": "registry", "supports": "identity", "path": path, "key": subject,
                    "note": row["evidence"]}])
            continue
        source = entries[CANONICAL](int(row["source_kernel"], 16))
        target = entries[layout](int(row["target_kernel"], 16))
        if source is None or target is None:
            b.issue("symbols", where, subject, "no L0 function holds a kernel entry of the row")
            continue
        address = int(row["target_wrapper"], 16)
        if not b.is_function(layout, address):
            b.issue("symbols", where, subject,
                    f"the target wrapper is no function entry of l0/{layout}/funcs.csv")
            continue
        for origin, address, key in (
                (wrapper, address, row["source_wrapper"]),
                (b.symbol(CANONICAL, "fn", source[0], path), target[0], row["source_kernel"])):
            symbol = b.symbol(layout, "fn", address, path, evidence=[{
                "kind": "interp-contract", "supports": "homology", "to": origin, "path": path,
                "key": key, "value": row["evidence"], "legacy": f"{status}:{row['evidence']}"}])
            b.join(origin, symbol, where)


def relate(b, root):
    pass
