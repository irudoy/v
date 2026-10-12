"""The compiler from the tracked inputs to the model (tools/kb/SPEC.md, section 9).

`build` runs the adapters of the legacy registries in two passes, joins the
symbols into meanings, and assigns names from `kb/names.csv`. The graph loader
and the checks read the model it returns.
"""

from functools import lru_cache
import csv
from pathlib import Path
import tomllib

from kb import adapters, names, repo
from kb.allocation import allocation_phase
from kb.model import Builder, SymbolKey

SCHEMA = 1
PACKAGE = "tools/kb/src/kb"
# Modules of the command line, the read and write commands, the MCP server, the
# checks and the record of their passes, the projections, the conversions, the
# guard, and the instances, and the adapters of converted registries, by their
# path in the package. They do not change the graph, so they are no compiler
# inputs.
NOT_COMPILER = frozenset({"answer.py", "checks.py", "cli.py", "convert.py", "guard.py",
                          "instance.py", "lock.py", "mcp.py", "passes.py", "project.py",
                          "read.py", "refs.py", "spec.py", "write.py", "legacy_reservation.py",
                          "architecture_projection.py", "ledger_projection.py", "history.py", "suggest.py",
                          "arithmetic.py", "research.py", "reader.py", "family.py",
                          *(f"adapters/{adapter.__name__.rsplit('.', 1)[1]}.py"
                            for adapter in adapters.CONVERTED)})


def spaces(config):
    """{MCU: {space: (start, end)}} from `[mcu.<name>]` of the configuration."""
    return {
        mcu: {space: (int(bounds[0], 16), int(bounds[1], 16)) for space, bounds in row.items()}
        for mcu, row in config["mcu"].items()
    }


def functions(layouts, root=repo.ROOT):
    """{layout: function entries} from the L0 of every layout."""
    found = {}
    for layout in layouts:
        with (root / repo.L0 / layout / "funcs.csv").open(newline="", encoding="utf-8") as source:
            found[layout] = frozenset(int(row["addr"], 16) for row in csv.DictReader(source))
    return found


def calibration(layouts, root=repo.ROOT, overlay=None):
    """{layout: (start, end)} of the calibration region its family declares."""
    text = (overlay or {}).get(repo.HOMOLOGY)
    if text is None:
        text = (root / repo.HOMOLOGY).read_text(encoding="utf-8")
    document = tomllib.loads(text)
    found = {}
    for layout in layouts.values():
        region = document["family"][layout.family].get("calibration_region")
        if region:
            start, end = (int(part, 16) for part in region.split(":"))
            found[layout.id] = (start, end)
    return found


def inputs(root=repo.ROOT):
    """Repository paths whose content the model depends on, excluding L0."""
    found = set(adapters.inputs(root))
    from kb import compatibility
    found.update(compatibility.inputs(root))
    found.update(names.inputs())
    from kb import source_bindings
    found.update(path.as_posix() for path in source_bindings.PATHS)
    found.update((repo.HOMOLOGY.as_posix(), repo.CATALOG.as_posix(), repo.CONFIG.as_posix()))
    if (root / repo.OWNER_CONFIG).is_file():
        found.add(repo.OWNER_CONFIG.as_posix())
    found.update(path.relative_to(root).as_posix()
                 for path in (root / PACKAGE).rglob("*.py")
                 if path.relative_to(root / PACKAGE).as_posix() not in NOT_COMPILER)
    return sorted(found)


def builder_of(root=repo.ROOT, overlay=None):
    """A builder over the layouts, functions, and regions of the working tree,
    whose adapters read the files of `overlay` in place of those on disk."""
    overlay = {Path(path): text for path, text in (overlay or {}).items()}
    config = repo.config(root, overlay)
    layouts = repo.layouts(root, overlay)
    builder = Builder(layouts, spaces(config), functions(layouts, root),
                      calibration(layouts, root, overlay), config)
    builder.overlay = overlay
    return builder


@allocation_phase
def build(root=repo.ROOT, overlay=None, order=None):
    """The model of the working tree, with the entity files and `kb/names.csv`
    of `overlay` ({repository path: text, or None}) in place of those on
    disk, compiled by the adapters of `order`, by default the compiler's."""
    builder = builder_of(root, overlay)
    config, overlay = builder.config, builder.overlay
    rows = names.read(root, overlay)
    builder.generated.update({SymbolKey(row.layout, row.kind, row.address): row.name
                              for row in rows})
    order = adapters.ADAPTERS if order is None else order
    for adapter in order:
        adapter.declare(builder, root)
    for adapter in order:
        adapter.relate(builder, root)
    model = builder.finish()
    model.root = root
    model.overlay = overlay
    model.config = config
    model.functions = builder.functions
    model.spaces = builder.spaces
    model.names = rows
    names.assign(model, rows)
    return model


@lru_cache(maxsize=1)
def _cached(root, digest):
    from kb import fingerprint
    model = build(root)
    if fingerprint.compute(root).value != digest:
        raise repo.KbError('compiler inputs change while building the cached model', code=3)
    return model


def cached(root=repo.ROOT):
    """Reuse a model only while the exact compiler fingerprint is current."""
    from kb import fingerprint
    root = Path(root).resolve()
    return _cached(root, fingerprint.compute(root).value)


cached.cache_clear = _cached.cache_clear
cached.cache_info = _cached.cache_info
