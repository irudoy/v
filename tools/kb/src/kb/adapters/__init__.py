"""Adapters of the entity files and of the legacy registries (tools/kb/SPEC.md,
section 20).

Each adapter module declares `inputs`, the repository paths it reads, and two
passes over a `model.Builder`: `declare` states the symbols, names, keys, and
statuses of its registry, and `relate` states the links, which resolve
against the symbols that every adapter declared. The entity files come first:
they own the facts of the registries that their stage converted.

`ORDER` is the order of every adapter. The compiler runs `ADAPTERS`, which
leave out the adapters of the registries that the entity files own since
their conversion; `kb.convert` runs `ORDER` to compile the model before a
conversion.
"""

from kb.adapters import (architecture, curated, definitions, dids, files, interp, ledgers,
                         native, overrides, profiles, signals, telemetry)

ORDER = (files, curated, ledgers, profiles, definitions, interp, native, dids, signals,
         telemetry, overrides, architecture)
CONVERTED = (interp,)
ADAPTERS = tuple(adapter for adapter in ORDER if adapter not in CONVERTED)


def inputs(root):
    found = set()
    for adapter in ADAPTERS:
        found.update(adapter.inputs(root))
    return sorted(found)
