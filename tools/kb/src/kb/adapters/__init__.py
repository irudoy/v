"""Adapters of the legacy registries (tools/kb/SPEC.md, section 20).

Each adapter module declares `INPUTS`, the repository paths it reads, and two
passes over a `model.Builder`: `declare` states the symbols, names, keys, and
statuses of its registry, and `relate` states the links, which resolve
against the symbols that every adapter declared.
"""

from kb.adapters import curated, ledgers, profiles

ADAPTERS = (curated, ledgers, profiles)


def inputs(root):
    found = set()
    for adapter in ADAPTERS:
        found.update(adapter.inputs(root))
    return sorted(found)
