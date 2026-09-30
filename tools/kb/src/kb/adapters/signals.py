"""JK08A tuning signals (tools/kb/SPEC.md, section 20.5).

- Each `[[signal]]` gives the `signal` entity of its `id`: `label` becomes
  `title`, `evidence` becomes `basis`, and `domain`, `priority`, `coverage`,
  and `note` keep their names.
- `sources` becomes `observes`, the meanings of the `7mfk` symbols at those
  addresses, and each of `widths` states the `width` of its symbol in bits,
  so that a registry that states another width disagrees. A source inside the
  RAM that a feature allocates (`feature_ram` of the stash) is no meaning:
  the signal observes the allocation of the feature target at that address
  and width, as `<feature>.<allocation>`.
- `dids` is derived: the DIDs whose `source` is an observed meaning. A stored
  set that differs goes to the audit. `current_fields` gives each field the
  signal it serves, which the telemetry fields read from `signal_fields` of
  the stash; from the conversion of the profile the field files state
  `signal`, and `current_fields` that differ from the fields whose `signal`
  names the signal go to the audit.
- `telemetry_profile`, `full_rate_hz`, and `rotating_divisor` become keys of
  the `can_telemetry` feature.
"""

from collections import defaultdict
from pathlib import Path
import tomllib

from kb.model import MEANING_REF, Ref

SIGNALS = Path("defs/JK08A.tuning-signals.toml")
SCHEMA_VERSION = 1
CANONICAL = "7mfk"
FEATURE = "can_telemetry"
FEATURE_KEYS = ("telemetry_profile", "full_rate_hz", "rotating_divisor")
DOCUMENT_KEYS = frozenset({"schema_version", "rom", "signal", *FEATURE_KEYS})
SIGNAL_KEYS = frozenset({"id", "domain", "label", "priority", "coverage", "current_fields",
                         "sources", "widths", "dids", "evidence", "note"})
SOURCE_KINDS = ("ram", "reg")


def inputs(root):
    return [SIGNALS.as_posix()]


def _dids(numbers):
    return ", ".join(f"{number:04x}" for number in sorted(numbers)) or "none"


def declare(b, root):
    declare_signals(b, tomllib.loads((root / SIGNALS).read_text(encoding="utf-8")),
                    SIGNALS.as_posix())


def declare_signals(b, document, src):
    if document.get("schema_version") != SCHEMA_VERSION:
        b.issue("schema", src, "schema_version",
                f"schema_version {document.get('schema_version')!r}; the adapter reads "
                f"{SCHEMA_VERSION}")
        return
    for name in sorted(set(document) - DOCUMENT_KEYS):
        b.issue("schema", src, name, "unknown key")
    if document.get("rom") not in b.layouts[CANONICAL].images:
        b.issue("schema", src, "rom", f"{document.get('rom')!r} is no image of {CANONICAL}")
        return
    b.entity("feature", FEATURE, src,
             props={name: document[name] for name in FEATURE_KEYS if name in document})
    pending, owners = [], {}
    for index, item in enumerate(document.get("signal", ())):
        subject = f"signal.{item.get('id', index)}"
        if set(item) != SIGNAL_KEYS:
            b.issue("schema", src, subject, f"missing {sorted(SIGNAL_KEYS - set(item))}; "
                    f"unknown {sorted(set(item) - SIGNAL_KEYS)}")
            continue
        if ("signal", item["id"]) in b.entities:
            b.issue("schema", src, subject, "a second signal of the id")
            continue
        if len(item["sources"]) != len(item["widths"]):
            b.issue("schema", src, subject, "sources and widths differ in length")
            continue
        b.entity("signal", item["id"], src, props={
            "title": item["label"], "domain": item["domain"], "priority": item["priority"],
            "coverage": item["coverage"], "basis": item["evidence"], "note": item["note"]})
        for name in item["current_fields"]:
            if name in owners:
                b.issue("schema", src, subject,
                        f"field {name} belongs to both {owners[name]} and {item['id']}")
                continue
            owners[name] = item["id"]
        pending.append((item["id"], tuple(zip(item["sources"], item["widths"])),
                        frozenset(item["dids"]), frozenset(item["current_fields"])))
    b.stash["signals"] = (src, pending)
    b.stash["signal_fields"] = owners


def _allocations(b):
    """{address: [(reference, width)]} of the allocations of the feature
    targets on the canonical layout."""
    found = defaultdict(list)
    for (feature, layout), target in sorted(b.targets.items()):
        if layout == CANONICAL:
            for name, entry in sorted(target.props.get("allocations", {}).items()):
                found[int(entry["address"], 16)].append((f"{feature}.{name}", entry["width"]))
    return found


def _served(b):
    """{signal slug: the fields whose `signal` names it}."""
    found = defaultdict(set)
    for (kind, name), entity in b.entities.items():
        if kind != "field":
            continue
        for ref in entity.refs.get("signal", ()):
            match = MEANING_REF.fullmatch(ref.text) if isinstance(ref, Ref) else None
            if match and match.group("kind") == "signal":
                found[match.group("name")].add(name)
            elif isinstance(ref, tuple) and ref[0] == "signal":
                found[ref[1]].add(name)
    return found


def relate(b, root):
    """Resolve the observed symbols and allocations; the DIDs come from
    `did_sources` of the stash, which the DID table fills first."""
    src, pending = b.stash.get("signals", (SIGNALS.as_posix(), ()))
    returned = b.stash.get("did_sources", {})
    allocations = _allocations(b)
    feature_ram = b.stash.get("feature_ram", ())
    served = _served(b)
    for slug, sources, dids, current in pending:
        subject = f"signal.{slug}"
        observed, allocated = [], []
        for address, width in sources:
            owner = next((feature for start, end, feature in feature_ram
                          if start <= address < end), None)
            if owner is not None:
                found = [ref for ref, size in allocations.get(address, ()) if size == width]
                if not found:
                    b.issue("references", src, subject, f"source {address:08x} lies in the "
                            f"RAM of {owner} and names none of its allocations of {width} "
                            f"bytes")
                    continue
                allocated.append(found[0])
                continue
            key = b.resolve(CANONICAL, address, SOURCE_KINDS, src)
            if key is None:
                b.issue("references", src, subject,
                        f"source {address:08x} is no RAM or register address of {CANONICAL}")
                continue
            key = b.symbol(key.layout, key.kind, key.address, src)
            b.keys(key, {"width": 8 * width}, src)
            observed.append(key)
        b.entity("signal", slug, src, props={"observes": allocated} if allocated else None,
                 refs={"observes": observed} if observed else None)
        derived = set().union(*(returned.get(key, ()) for key in observed))
        if derived != dids:
            b.issue("audit", src, subject, f"dids {_dids(dids)} differ from the DIDs that "
                    f"return an observed meaning: {_dids(derived)}")
        if served[slug] != current:
            b.issue("audit", src, subject, f"current_fields {sorted(current)} differ from the "
                    f"fields whose signal it is: {sorted(served[slug])}")
