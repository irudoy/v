"""Patch tests run independently of optional stock-code evidence plugins.

``--rom ROM`` deselects each parametrized case whose parameters name another
supported ROM, its family, or its layout; cases that name no ROM still run.
"""

from patches import runtime_targets
from tools import rom_homology


def pytest_addoption(parser):
    parser.addoption(
        "--rom",
        choices=runtime_targets.SUPPORTED_ROMS,
        help="deselect parametrized cases that name another ROM, family, or layout",
    )


def rom_names():
    """Return the casefolded names of every supported ROM by ROM: the ROM,
    its family, and the layouts that its family declares for it."""
    _settings, families, _relationships = rom_homology.load_homology()
    names = {}
    for family, declaration in families.items():
        layouts = declaration.get("layouts", {})
        for rom in declaration["members"]:
            if rom not in runtime_targets.SUPPORTED_ROMS:
                continue
            own = [key for key, owner in layouts.items() if owner == rom]
            names[rom] = frozenset(
                name.casefold() for name in (rom, family, *(own or layouts))
            )
    return names


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _strings(item)


def pytest_collection_modifyitems(config, items):
    rom = config.getoption("--rom")
    if rom is None:
        return
    names = rom_names()
    allowed = names[rom]
    foreign = frozenset().union(*names.values()) - allowed
    selected, deselected = [], []
    for item in items:
        params = getattr(getattr(item, "callspec", None), "params", {})
        named = {value.casefold() for value in _strings(params)}
        (deselected if named & foreign else selected).append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
