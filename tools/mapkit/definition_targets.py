#!/usr/bin/env python3
"""Resolve one ROM-specific editor definition from canonical shared sources."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

from tools.mapkit import rom as romkit
from tools import rom_sources


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IDENTITIES = ROOT / "defs" / "rom-identities.toml"
ROMID_FIELDS = (
    "xmlid",
    "internalidaddress",
    "internalidstring",
    "ecuid",
    "caseid",
    "make",
    "model",
    "submodel",
    "market",
    "transmission",
    "memmodel",
    "endian",
    "filesize",
    "author",
    "version",
)

# RomRaider accepts flashmethod as optional metadata for a compatible flashing
# implementation. Do not emit one until the project validates that path on the
# exact ECU family; dump-tool provenance is not evidence of compatibility.


class DefinitionTargetError(ValueError):
    """Raised when a target identity or inheritance binding is invalid."""


@dataclass(frozen=True)
class DefinitionTarget:
    rom: str
    source: str
    source_model: rom_sources.SourceModel
    romid: dict[str, str]
    image: romkit.Image


def _load_identities(path=DEFAULT_IDENTITIES):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise DefinitionTargetError(
            f"definition identity registry cannot be loaded: {path}: {error}"
        ) from error
    if set(document) != {"schema_version", "rom"}:
        raise DefinitionTargetError(
            f"{path}: expected only schema_version and rom"
        )
    if document["schema_version"] != 1:
        raise DefinitionTargetError(
            f"{path}: unsupported schema_version {document['schema_version']!r}"
        )
    identities = document["rom"]
    if not isinstance(identities, dict) or not identities:
        raise DefinitionTargetError(f"{path}: no [rom.*] identities")
    expected = set(ROMID_FIELDS)
    for rom, row in identities.items():
        if not isinstance(row, dict) or set(row) != expected:
            actual = set(row) if isinstance(row, dict) else set()
            raise DefinitionTargetError(
                f"{path} [rom.{rom}]: fields differ; "
                f"missing={sorted(expected - actual)}; "
                f"extra={sorted(actual - expected)}"
            )
        if any(not isinstance(value, str) or not value for value in row.values()):
            raise DefinitionTargetError(
                f"{path} [rom.{rom}]: every identity field must be text"
            )
    return identities


def registered_targets(identity_path=DEFAULT_IDENTITIES):
    """Return definition targets in their declared generation order."""
    return tuple(_load_identities(identity_path))


def registered_sources(
    identity_path=DEFAULT_IDENTITIES,
    inheritance_path=rom_sources.DEFAULT_REGISTRY,
):
    """Return unique canonical sources for all registered definition targets."""
    sources = []
    for rom in registered_targets(identity_path):
        source = rom_sources.resolve(rom, path=inheritance_path).source
        if source not in sources:
            sources.append(source)
    return tuple(sources)


def load_target(rom, identity_path=DEFAULT_IDENTITIES):
    """Load and bind one target to its stock image and canonical source."""
    identities = _load_identities(identity_path)
    if rom not in identities:
        raise DefinitionTargetError(f"no editor identity is registered for {rom}")
    try:
        source_model = rom_sources.resolve(rom)
        rom_sources.verify_image_binding(source_model)
        image = romkit.load(rom)
    except (OSError, ValueError, rom_sources.SourceModelError) as error:
        raise DefinitionTargetError(str(error)) from error

    romid = dict(identities[rom])
    if romid["xmlid"] != rom or romid["ecuid"] != f"1{rom}":
        raise DefinitionTargetError(
            f"{identity_path} [rom.{rom}]: XML or ECU identity differs from label"
        )
    address_text = romid["internalidaddress"]
    if not re.fullmatch(r"[0-9a-fA-F]+", address_text):
        raise DefinitionTargetError(
            f"{identity_path} [rom.{rom}]: internalidaddress is not hexadecimal"
        )
    address = int(address_text, 16)
    expected = romid["internalidstring"].encode("ascii")
    actual = image.data[address : address + len(expected)]
    if actual != expected:
        raise DefinitionTargetError(
            f"{rom}: stock bytes at {address:#x} are {actual!r}, "
            f"expected {expected!r}"
        )
    return DefinitionTarget(
        rom=rom,
        source=source_model.source,
        source_model=source_model,
        romid=romid,
        image=image,
    )


def _replace_label(value, source, target):
    if isinstance(value, str):
        return value.replace(source, target)
    if isinstance(value, list):
        return [_replace_label(item, source, target) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_label(item, source, target)
            for key, item in value.items()
        }
    return value


def materialize_overrides(target, overrides):
    """Apply target labels and ROM identity without duplicating presentation."""
    result = _replace_label(copy.deepcopy(overrides), target.source, target.rom)
    source_comment = overrides.get("rom", {}).get("comment")
    result["rom"] = dict(target.romid)
    if source_comment is not None:
        comment = _replace_label(
            copy.deepcopy(source_comment), target.source, target.rom
        )
        comment = _replace_label(
            comment,
            f"defs/{target.rom}.",
            f"defs/{target.source}.",
        )
        result["rom"]["comment"] = comment
    return result
