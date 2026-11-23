"""JK08A tuning signals (tools/kb/SPEC.md, section 7.9).

`tools/kb/projections.toml` registers the generated signal catalog.

- Each `[[signal]]` gives the `signal` entity of its `id`: `label` becomes
  `title`, `evidence` becomes `basis`, and `domain`, `priority`, `coverage`,
  and `note` keep their names.
- `sources` becomes `observes`, the meanings of the `7mfk` symbols at those
  addresses, and each of `widths` states the `width` of its symbol in bits,
  so that a registry that states another width disagrees. A source inside the
  RAM that a feature allocates (`feature_ram` of the stash) is no meaning:
  the signal observes the allocation of the feature target at that address
  and width, as `<feature>.<allocation>`. The `observes` references keep the
  order of `sources`, and the allocations are also a key of the signal.
- `dids` is derived: the DIDs whose `source` is an observed meaning. A stored
  set that differs goes to the audit. `current_fields` gives each field the
  signal it serves, which the telemetry fields read from `signal_fields` of
  the stash; from the conversion of the profile the field files state
  `signal`, and `current_fields` that differ from the fields whose `signal`
  names the signal go to the audit.
- `telemetry_profile`, `full_rate_hz`, and `rotating_divisor` become keys of
  the `can_telemetry` feature.

From stage 4 the catalog is a projection of the signals and of
`can_telemetry` (`catalog`): the signals by domain, by priority from `core`
to `research`, and by slug; `sources` and `widths` from `observes` in its
order, the address and the width of the `7mfk` symbol of each observed
meaning or of each allocation; `current_fields` the fields whose `signal`
names the signal, by observed source in the order of `observes`, the fields
of one source in the order of the profile, and the other fields after them;
and `dids` the DIDs that return each observed meaning, in the order of
`observes` and by number.
"""

from collections import defaultdict
from pathlib import Path
import tomllib

from kb import repo, store, vocab
from kb.adapters import telemetry
from kb.model import MEANING_REF, Ref, SymbolKey
from kb.repo import KbError

SIGNALS = Path("defs/registries/JK08A.tuning-signals.toml")
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


def allocations(targets):
    """{address: [(reference, width)]} of the allocations of the feature
    targets on the canonical layout."""
    found = defaultdict(list)
    for (feature, layout), target in sorted(targets.items()):
        if layout == CANONICAL:
            for name, entry in sorted(target.props.get("allocations", {}).items()):
                found[int(entry["address"], 16)].append((f"{feature}.{name}", entry["width"]))
    return found


def served(entities):
    """{signal slug: the fields whose `signal` names it}."""
    found = defaultdict(set)
    for (kind, name), entity in entities.items():
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
    relate_signals(b, allocations(b.targets), served(b.entities))


def relate_signals(b, held, serving):
    """Resolve the observed symbols and the allocations of `held` ({address:
    [(reference, width)]}), and audit the fields of `serving` ({signal: the
    fields whose `signal` names it}); the DIDs come from `did_sources` of the
    stash, which the DID table fills first, and the RAM of the features from
    `feature_ram`."""
    src, pending = b.stash.get("signals", (SIGNALS.as_posix(), ()))
    returned = b.stash.get("did_sources", {})
    feature_ram = b.stash.get("feature_ram", ())
    for slug, sources, dids, current in pending:
        subject = f"signal.{slug}"
        observed, allocated, order = [], [], []
        for address, width in sources:
            owner = next((feature for start, end, feature in feature_ram
                          if start <= address < end), None)
            if owner is not None:
                found = [ref for ref, size in held.get(address, ()) if size == width]
                if not found:
                    b.issue("references", src, subject, f"source {address:08x} lies in the "
                            f"RAM of {owner} and names none of its allocations of {width} "
                            f"bytes")
                    continue
                allocated.append(found[0])
                order.append(found[0])
                continue
            key = b.resolve(CANONICAL, address, SOURCE_KINDS, src)
            if key is None:
                b.issue("references", src, subject,
                        f"source {address:08x} is no RAM or register address of {CANONICAL}")
                continue
            key = b.symbol(key.layout, key.kind, key.address, src)
            b.keys(key, {"width": 8 * width}, src)
            observed.append(key)
            order.append(key)
        b.entity("signal", slug, src, props={"observes": allocated} if allocated else None,
                 refs={"observes": order} if order else None)
        derived = set().union(*(returned.get(key, ()) for key in observed))
        if derived != dids:
            b.issue("audit", src, subject, f"dids {_dids(dids)} differ from the DIDs that "
                    f"return an observed meaning: {_dids(derived)}")
        if serving[slug] != current:
            b.issue("audit", src, subject, f"current_fields {sorted(current)} differ from the "
                    f"fields whose signal it is: {sorted(serving[slug])}")


# Projection ----------------------------------------------------------------

HEADER = """\
# Canonical observation coverage for JK08A tuning work.
#
# This catalog distinguishes signals already carried by the custom CAN profile,
# values available in stock RAM or service 0x22, stock CAN context, and
# measurements that need new firmware instrumentation or external equipment.
# It does not assign a physical conversion where exact code and target evidence
# do not establish one.
"""
# The keys of the catalog and of its signals in the order of the file.
TOP = ("schema_version", "rom", *FEATURE_KEYS)
SIGNAL_ORDER = ("id", "domain", "label", "priority", "coverage", "current_fields", "sources",
                "widths", "dids", "evidence", "note")
# The integer keys that the file writes in hexadecimal.
HEXADECIMAL = {"sources": "0x{:08X}", "dids": "0x{:04X}"}


def place(entity):
    """The place of a signal in the catalog: by domain, by priority from
    `core` to `research`, and by slug."""
    ranks = vocab.ENTITY_VOCABULARY["signal"]["priority"]
    priority = entity.props.get("priority")
    return (entity.props.get("domain", ""),
            ranks.index(priority) if priority in ranks else len(ranks), entity.slug)


def returned(model):
    """{meaning key: the numbers of the DIDs whose `source` is the meaning}."""
    found = defaultdict(set)
    for link in model.links:
        if link.type == "source" and link.owner.kind == "did" \
                and isinstance(link.owner.props.get("number"), int):
            found[link.to.key].add(link.owner.props["number"])
    return found


def observed(model, entity, entries):
    """[(source, address, width in bytes)] of what a signal observes, in the
    order of `observes`: the key of the meaning of a `7mfk` symbol with the
    address and the width of the symbol, or an allocation reference with the
    address and the width of the allocation."""
    found = []
    for item in entity.refs.get("observes", ()):
        if isinstance(item, SymbolKey):
            symbol = model.symbols.get(item)
            width = symbol.value("width") if symbol is not None else None
            if (item.layout != CANONICAL or symbol is None or symbol.meaning is None
                    or not isinstance(width, int) or width % 8):
                raise KbError(f"{entity.key}: {item.key} is no {CANONICAL} symbol of a meaning "
                              "with a width in bytes", code=3)
            found.append((symbol.meaning.key, item.address, width // 8))
            continue
        entry = entries.get(item)
        if entry is None:
            raise KbError(f"{entity.key}: {item!r} is no allocation of a {CANONICAL} target",
                          code=3)
        found.append((item, int(entry["address"], 16), entry["width"]))
    return found


def _source(model, field):
    """The meaning key of the source of an `ecu_ram` field, or else the
    allocation reference of its source."""
    keys = field.refs.get("source", ())
    if keys and isinstance(keys[0], SymbolKey):
        meaning = model.meaning_of(keys[0])
        return meaning.key if meaning is not None else None
    return field.props.get("source")


def catalog_document(model):
    """The document of the catalog from the signals, the fields, and the
    `can_telemetry` feature."""
    feature = model.entities.get(("feature", FEATURE))
    if feature is None:
        raise KbError(f"the model holds no {FEATURE} feature", code=3)
    entries = {f"{owner}.{name}": entry
               for (owner, layout), target in sorted(model.targets.items())
               if layout == CANONICAL
               for name, entry in target.props.get("allocations", {}).items()}
    numbers = returned(model)
    serving = defaultdict(list)
    for field in telemetry.fields(model):
        for ref in field.refs.get("signal", ()):
            if isinstance(ref, tuple) and ref[0] == "signal":
                serving[ref[1]].append(field)
    document = {"schema_version": SCHEMA_VERSION, "rom": model.layouts[CANONICAL].image,
                **{key: feature.props.get(key) for key in FEATURE_KEYS}, "signal": []}
    found = [entity for (kind, _), entity in model.entities.items() if kind == "signal"]
    for entity in sorted(found, key=place):
        props = entity.props
        sources = observed(model, entity, entries)
        fields, dids = [], []
        for source, _, _ in sources:
            fields += [field.slug for field in serving[entity.slug]
                       if _source(model, field) == source and field.slug not in fields]
            dids += [number for number in sorted(numbers.get(source, ())) if number not in dids]
        fields += [field.slug for field in serving[entity.slug] if field.slug not in fields]
        notes = props.get("note") or []
        if len(notes) != 1:
            raise KbError(f"{entity.key}: the catalog holds one note of a signal, and it has "
                          f"{len(notes)}", code=3)
        document["signal"].append({
            "id": entity.slug, "domain": props.get("domain"), "label": props.get("title"),
            "priority": props.get("priority"), "coverage": props.get("coverage"),
            "current_fields": fields, "sources": [address for _, address, _ in sources],
            "widths": [width for _, _, width in sources], "dids": dids,
            "evidence": props.get("basis"), "note": notes[0]})
    return document


def _toml(key, value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return HEXADECIMAL.get(key, "{}").format(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return f'"{store.escape(value)}"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml(key, item) for item in value) + "]"
    raise KbError(f"no catalog form of {key} = {value!r}", code=3)


def _block(header, item, order, subject):
    """The lines of one table of the catalog with the keys of `order`."""
    unknown = sorted(set(item) - set(order) - {"signal"})
    missing = [key for key in order if item.get(key) is None]
    if unknown or missing:
        raise KbError(f"{subject}: unknown keys {unknown}, no value of {missing}", code=3)
    return "\n".join(([header] if header else []) +
                     [f"{key} = {_toml(key, item[key])}" for key in order])


def render_catalog(document):
    """The text of `defs/registries/JK08A.tuning-signals.toml` from its document."""
    top = {key: value for key, value in document.items() if key != "signal"}
    blocks = [HEADER + "\n" + _block(None, top, TOP, "catalog")]
    blocks += [_block("[[signal]]", item, SIGNAL_ORDER, f"signal.{item.get('id')}")
               for item in document.get("signal", ())]
    return "\n\n".join(blocks) + "\n"


def catalog(root=repo.ROOT):
    """The text of `defs/registries/JK08A.tuning-signals.toml` from the model."""
    from kb import compile
    return render_catalog(catalog_document(compile.cached(root)))
