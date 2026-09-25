"""The compiler from the tracked inputs to the model (tools/kb/SPEC.md, section 9).

`build` runs the adapters of the legacy registries in two passes, joins the
symbols into meanings, and assigns names from `kb/names.csv`. The graph loader
and the checks read the model it returns.
"""

from functools import lru_cache
import csv
import tomllib

from kb import adapters, names, repo
from kb.model import Builder

SCHEMA = 1
PACKAGE = "tools/kb/src/kb"


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


def calibration(layouts, root=repo.ROOT):
    """{layout: (start, end)} of the calibration region its family declares."""
    document = tomllib.loads((root / repo.HOMOLOGY).read_text(encoding="utf-8"))
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
    found.update(names.inputs())
    found.update((repo.HOMOLOGY.as_posix(), repo.CATALOG.as_posix(), repo.CONFIG.as_posix()))
    found.update(path.relative_to(root).as_posix()
                 for path in (root / PACKAGE).rglob("*.py"))
    return sorted(found)


def build(root=repo.ROOT):
    config = repo.config(root)
    layouts = repo.layouts(root)
    builder = Builder(layouts, spaces(config), functions(layouts, root),
                      calibration(layouts, root), config)
    for adapter in adapters.ADAPTERS:
        adapter.declare(builder, root)
    for adapter in adapters.ADAPTERS:
        adapter.relate(builder, root)
    model = builder.finish()
    model.config = config
    model.functions = builder.functions
    model.spaces = builder.spaces
    model.names = names.read(root)
    names.assign(model, model.names)
    return model


@lru_cache(maxsize=1)
def cached(root=repo.ROOT):
    return build(root)
