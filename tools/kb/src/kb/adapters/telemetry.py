"""The CAN telemetry profile of JK08A (tools/kb/SPEC.md, section 7.9).

`tools/kb/projections.toml` registers the generated telemetry profile.

- Each `[[field]]` and `[[context.field]]` gives the `field` entity of its
  `name` with `kind` as `origin`, `width`, `signed`, and its place: `page`,
  `offset`, and `profiles` in the stream, or the `context` and the `position`
  inside it. The signal whose `current_fields` lists the field is its
  `signal`, and its `dashboard` table, where the registry states one, is its
  `dashboard`.
- The source of an `ecu_ram` field is the `7mfk` symbol at its address, joined
  by the field as a telemetry source of the address profiles is. Its `scale`
  parses into the source meaning: the arithmetic in `raw`, a bare `raw`
  included, becomes `scale` in `x` with its `unit` from `[vocab] unit` of
  `tools/kb/config.toml`, a leading `candidate` sets `scale_level`, an
  enumeration becomes `value` entries and a list of named bits `bit` entries,
  and the remaining text joins the summary. A string that the parser cannot
  split fails the `fields` check, which refuses the conversion.
  The host `raw count` storage view declares no semantic conversion keys.
  `telemetry_units` of the stash lists the symbols whose unit the profile
  states.
- The source of a field of another origin is the allocation, named after
  the field without `_raw`, of the feature that owns its address: the state
  record or the dynamic page state and the configuration record of
  `can_telemetry` for `telemetry_state` and `rom_configuration`, and the
  active RAM of `map_switching` or `rolling_launch` in the reservation ledger
  for `runtime_state` (`layouts.origin_regions`). The field keeps its `scale` and
  names the allocation as `<feature>.<allocation>`. `feature_ram` of the
  stash holds the active RAM of every feature.
- The wire constants, `[[profile]]`, and the contexts become keys of the
  `can_telemetry` feature; the mailbox and the table, configuration, and
  state addresses become keys of its `7mfk` target. The feature `requires`
  every field it declares, so the source meaning of each is required on every
  layout that the feature targets.

From stage 4 the profile is a projection of the fields and of `can_telemetry`
(`profile`): the stream fields by page and offset, the fields of each context
by position, the source of an `ecu_ram` field at the address of its `7mfk`
symbol with the scale of its meaning, its values, or its named bits, the
source of another field at its allocation, and the `[dashboard]` table of each
field as its `[field.dashboard]`.
"""

from pathlib import Path
import re
import tomllib

from kb import repo, store
from kb.adapters import layouts
from kb.model import SymbolKey
from kb.repo import KbError
from kb.values import hexed

PROFILE = Path("patches/can-telemetry-profile.toml")
LAYOUT = Path("patches/can-telemetry-layout.toml")
RESERVATIONS = Path("patches/jk08a-runtime-reservations.toml")
SCHEMA_VERSION = 2
CANONICAL = "7mfk"
FEATURE = "can_telemetry"
STORED_COUNT_SCALE = "raw count"
WIRE_KEYS = ("protocol_version", "byte_order", "candidate_can_id", "candidate_tick_divisor",
             "base_tick_numerator", "pphi_hz", "fixed_page_count", "context_pages",
             "context_count", "header_sequence_bits")
ADDRESS_KEYS = ("table_address", "table_end", "configuration_address", "state_address")
DOCUMENT_KEYS = frozenset({"schema_version", "rom", "mailbox", "profile", "field", "context",
                           "padding", "padding_source", *WIRE_KEYS, *ADDRESS_KEYS})
FIELD_KEYS = frozenset({"name", "width", "source", "kind", "signed", "scale"})
# The presentation of a field, which a field may state.
OPTIONAL_FIELD_KEYS = frozenset({"dashboard"})
STREAM_KEYS = FIELD_KEYS | {"page", "offset", "profiles"}
CONTEXT_KEYS = frozenset({"page", "tag", "name", "field"})
PROFILE_KEYS = frozenset({"name", "id", "page_count"})
# The dynamic page, which a profile may state.
OPTIONAL_PROFILE_KEYS = frozenset({"dynamic"})
KINDS = ("ecu_ram", "rom_configuration", "runtime_state", "telemetry_state")

NUMBER = r"\d+(?:\.\d+)?"
TERM = rf"(?:raw|{NUMBER})"
# The arithmetic of a scale, a bare `raw` included, and its unit.
SCALE = re.compile(rf"(?P<candidate>candidate\s+)?(?P<arithmetic>{TERM}(?:\s*[-+*/]\s*{TERM})*)"
                   r"\s+(?P<unit>[^\s,;]+)[,;]?\s*(?P<rest>.*)", re.DOTALL)
# Arithmetic in `raw` inside the remaining text states a second scale.
SECOND = re.compile(r"\braw\s*[-+*/]|[-+*/]\s*raw\b")
RAW = re.compile(r"\braw\b")
ENUMERATION = "enumeration: "
BITS = "bits: "
# The prefix of the named entries of each key: the values of an enumeration
# and the named bits of a bit field.
NAMED = {"value": ENUMERATION, "bit": BITS}
ENTRY = re.compile(r"(\d+) ([A-Z][A-Z0-9_]*)")


def inputs(root):
    return [PROFILE.as_posix(), LAYOUT.as_posix(), RESERVATIONS.as_posix()]


def parse_scale(text, units):
    """The keys that the scale of an `ecu_ram` field gives its source meaning,
    or None for a string that the parser cannot split."""
    match = SCALE.fullmatch(text)
    if match:
        arithmetic, unit, rest = match["arithmetic"], match["unit"], match["rest"]
        if len(RAW.findall(arithmetic)) != 1 or unit not in units or SECOND.search(rest):
            return None
        keys = {"scale": re.sub(r"\s+", "", arithmetic).replace("raw", "x"), "unit": unit}
        if match["candidate"]:
            keys["scale_level"] = "candidate"
        if rest:
            keys["summary"] = rest
        return keys
    for key, prefix in NAMED.items():
        if text.startswith(prefix):
            entries = [ENTRY.fullmatch(item) for item in text[len(prefix):].split(", ")]
            if all(entries):
                return {key: [{key: int(item[1]), "name": item[2].lower()}
                              for item in entries]}
    return None


def _regions(b, root):
    """{kind: [(start, end, feature)]}: the addresses that the source of a field
    of each kind other than `ecu_ram` may occupy, and the feature that owns
    them."""
    layout = tomllib.loads((root / LAYOUT).read_text(encoding="utf-8"))
    ledger = tomllib.loads((root / RESERVATIONS).read_text(encoding="utf-8"))
    active = [(row["start"], row["end"], row["owner"]) for row in ledger["active_ram"]]
    b.stash.setdefault("feature_ram", active)
    return layouts.origin_regions(layout, active)


def declare(b, root):
    declare_profile(b, tomllib.loads((root / PROFILE).read_text(encoding="utf-8")),
                    _regions(b, root), PROFILE.as_posix())


def declare_profile(b, document, regions, src):
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
    profiles = []
    for index, item in enumerate(document.get("profile", ())):
        if not PROFILE_KEYS <= set(item) <= PROFILE_KEYS | OPTIONAL_PROFILE_KEYS:
            b.issue("schema", src, f"profile.{item.get('name', index)}",
                    f"keys {sorted(item)}; the adapter reads {sorted(PROFILE_KEYS)}")
            continue
        profiles.append(dict(item))
    contexts = [{"name": item.get("name"), "page": item.get("page"), "tag": item.get("tag")}
                for item in document.get("context", ())]
    b.entity("feature", FEATURE, src, props={
        **{name: document[name] for name in WIRE_KEYS if name in document},
        "profiles": profiles, "contexts": contexts})
    if document.get("padding"):
        b.entity("feature", FEATURE, src, props={
            "padding": document["padding"],
            "padding_source": f"{FEATURE}.configuration_reserved"})
        b.target(FEATURE, CANONICAL, src).props.setdefault("allocations", {})[
            "configuration_reserved"] = {"address": hexed(document["padding_source"]), "width": 1}
    b.target(FEATURE, CANONICAL, src, props={
        "mailbox_index": document.get("mailbox"),
        **{name: hexed(document[name]) for name in ADDRESS_KEYS if name in document}})
    units = frozenset(b.config.get("vocab", {}).get("unit", ()))
    owners = b.stash.get("signal_fields", {})
    scaled = b.stash.setdefault("telemetry_units", set())
    seen, declared = set(), []
    fields = [(item, STREAM_KEYS, {"page": item.get("page"), "offset": item.get("offset"),
                                   "profiles": item.get("profiles")})
              for item in document.get("field", ())]
    for index, context in enumerate(document.get("context", ())):
        if set(context) != CONTEXT_KEYS:
            b.issue("schema", src, f"context.{context.get('name', index)}",
                    f"keys {sorted(context)}; the adapter reads {sorted(CONTEXT_KEYS)}")
            continue
        fields.extend((item, FIELD_KEYS, {"context": context["name"], "position": position})
                      for position, item in enumerate(context["field"]))
    for item, keys, place in fields:
        name = item.get("name")
        subject = f"field.{name}"
        missing, unknown = keys - set(item), set(item) - keys - OPTIONAL_FIELD_KEYS
        if missing or unknown:
            b.issue("schema", src, subject, f"missing {sorted(missing)}; "
                    f"unknown {sorted(unknown)}")
            continue
        if name in seen:
            b.issue("schema", src, subject, "a second field of the name")
            continue
        seen.add(name)
        kind = item["kind"]
        props = {"origin": kind, "width": item["width"], "signed": item["signed"], **place}
        if "dashboard" in item:
            props["dashboard"] = item["dashboard"]
        refs = {}
        signal = owners.get(name)
        if signal is not None:
            refs["signal"] = [("signal", signal)]
        elif kind == "ecu_ram":
            b.issue("fields", src, subject, "an ecu_ram field that no signal lists")
        if kind == "ecu_ram":
            key = _ecu_source(b, item, src, subject)
            if key is None:
                continue
            refs["source"] = [key]
            # The host storage view is not a semantic scale declaration.
            if item["scale"] == STORED_COUNT_SCALE:
                props["scale"] = STORED_COUNT_SCALE
                parsed = {}
            else:
                parsed = parse_scale(item["scale"], units)
            if parsed is None:
                b.issue("fields", src, subject, f"scale {item['scale']!r} gives the source "
                        "meaning no keys")
            else:
                b.props(key, parsed, src)
                if "unit" in parsed:
                    scaled.add(key)
        elif kind in regions:
            source = _allocation(b, item, regions[kind], src, subject)
            if source is None:
                continue
            props.update(source=source, scale=item["scale"])
        else:
            b.issue("schema", src, subject, f"kind {kind!r}")
            continue
        b.entity("field", name, src, props=props, refs=refs)
        declared.append(("field", name))
    # The feature transmits every field of its profiles and contexts, so it
    # requires the source meaning of each on every layout it targets.
    b.entity("feature", FEATURE, src, refs={"requires": declared})
    for name, signal in sorted(owners.items()):
        if name not in seen:
            b.issue("references", src, f"signal.{signal}",
                    f"current field {name} is no field of the profile")


def _ecu_source(b, item, src, subject):
    address = item["source"]
    kind = b.data_kind(CANONICAL, address)
    inside = any(start <= address < end for start, end, _ in b.stash.get("feature_ram", ()))
    if kind is None or inside:
        b.issue("fields", src, subject, f"ecu_ram source {address:08x} lies outside the "
                f"RAM and the peripherals of the stock program")
        return None
    name = item["name"]
    group = (kind, "field", name)
    key = b.symbol(CANONICAL, kind, address, src, group=group, strength="field")
    b.name(group, name.removesuffix("_raw"), "field", src)
    return key


def _allocation(b, item, spans, src, subject):
    """The reference `<feature>.<allocation>` of the source of a field whose
    kind a feature allocates; the allocation joins the target of the feature."""
    address, width = item["source"], item["width"]
    owner = next((feature for start, end, feature in spans
                  if start <= address and address + width <= end), None)
    if owner is None:
        b.issue("fields", src, subject, f"{item['kind']} source {address:08x} lies outside "
                f"{', '.join(f'{start:08x}-{end:08x}' for start, end, _ in spans)}")
        return None
    name = item["name"].removesuffix("_raw")
    entry = {"address": hexed(address), "width": width}
    allocations = b.target(owner, CANONICAL, src).props.setdefault("allocations", {})
    if allocations.setdefault(name, entry) != entry:
        b.issue("audit", src, f"{owner}.{name}",
                f"allocation {entry} disagrees with {allocations[name]}")
    return f"{owner}.{name}"


def relate(b, root):
    pass


# Projection ----------------------------------------------------------------

HEADER = """\
# Authoritative wire schema and exact JK08A producer binding.
#
# The generator expands every multi-byte field to byte-source pointers used by
# the SH-2E capture loop and emits a ROM-neutral host decoder schema. Producer
# addresses, mailbox ownership, and ROM identity are not part of the host
# contract. The profile CRC covers the wire layout alone: protocol version,
# profile ID, page count, the placement, width, and signedness of every slot,
# and the dynamic page. Names, scale strings, and the host presentation of
# [field.dashboard] are outside it, and a slot that carries a different
# quantity takes a new profile ID. The host decodes the current profile ID
# alone. Under a nonzero configuration ID, the data bytes of the dynamic page
# of a profile carry the RAM slots of a host configuration; the fields of the
# page are its default configuration, ID 0.
"""
# The keys of the profile, its profiles, its fields, and its contexts in the
# order of the file.
TOP = ("schema_version", "rom", "protocol_version", "byte_order", "mailbox",
       "candidate_can_id", "candidate_tick_divisor", "base_tick_numerator", "pphi_hz",
       "fixed_page_count", "context_pages", "context_count", "header_sequence_bits",
       *ADDRESS_KEYS)
PROFILE_ORDER = ("name", "id", "page_count")
DYNAMIC_ORDER = ("page", "data_bytes", "configuration_offset")
STREAM_ORDER = ("name", "page", "offset", "width", "source", "profiles", "kind", "signed",
                "scale")
CONTEXT_ORDER = ("page", "tag", "name")
FIELD_ORDER = ("name", "width", "source", "kind", "signed", "scale")
# The keys of the presentation of a field and of its feed channel in the order
# of the file; each is optional.
DASHBOARD_ORDER = tuple(name for name, _ in store.DASHBOARD.keys if name != "feed")
FEED_ORDER = tuple(name for name, _ in store.FEED.keys)
# The integer keys that the file writes in hexadecimal.
HEXADECIMAL = {"candidate_can_id": "0x{:X}", "source": "0x{:08X}",
               "padding_source": "0x{:08X}",
               **{key: "0x{:08X}" for key in ADDRESS_KEYS}}
TOKEN = re.compile(r"x|\d+(?:\.\d+)?|[-+*/]")


def fields(model):
    """The field entities in the order of the profile: the stream fields by
    page and offset, then the fields of each context of `can_telemetry` by
    position."""
    feature = model.entities.get(("feature", FEATURE))
    contexts = [item.get("name") for item in (feature.props if feature else {}).get(
        "contexts", ())]
    found = [entity for (kind, _), entity in sorted(model.entities.items()) if kind == "field"]
    stream = [entity for entity in found if "context" not in entity.props]
    held = [entity for entity in found if "context" in entity.props]
    for entity in held:
        if entity.props["context"] not in contexts:
            raise KbError(f"{entity.key}: context {entity.props['context']!r} is no context of "
                          f"{FEATURE}", code=3)
    return (sorted(stream, key=lambda entity: (entity.props.get("page", -1),
                                                entity.props.get("offset", -1)))
            + sorted(held, key=lambda entity: (contexts.index(entity.props["context"]),
                                               entity.props.get("position", -1))))


def scale_text(props):
    """The profile string of the scale of a meaning: its arithmetic in `raw`
    with its unit, after `candidate` for a candidate scale, or else its values
    as an enumeration or its named bits as `bits: <n> <NAME>, ...`; None for a
    meaning without any of them or with arithmetic that the string cannot
    state."""
    scale, unit = props.get("scale"), props.get("unit")
    if isinstance(scale, str) and isinstance(unit, str):
        tokens = TOKEN.findall(scale)
        if "".join(tokens) != re.sub(r"\s+", "", scale):
            return None
        text = " ".join("raw" if token == "x" else token for token in tokens) + f" {unit}"
        return f"candidate {text}" if props.get("scale_level") == "candidate" else text
    for key, prefix in NAMED.items():
        if props.get(key):
            return prefix + ", ".join(f"{item[key]} {item['name'].upper()}"
                                      for item in sorted(props[key], key=lambda item: item[key]))
    return None


def profile_document(model):
    """The document of the profile from the fields, the `can_telemetry`
    feature, and its `7mfk` target."""
    feature = model.entities.get(("feature", FEATURE))
    target = model.targets.get((FEATURE, CANONICAL))
    if feature is None or target is None:
        raise KbError(f"the model holds no {FEATURE} feature with a {CANONICAL} target", code=3)
    allocations = {f"{owner}.{name}": entry
                   for (owner, layout), held in sorted(model.targets.items())
                   if layout == CANONICAL
                   for name, entry in held.props.get("allocations", {}).items()}
    document = {"schema_version": SCHEMA_VERSION, "rom": model.layouts[CANONICAL].image,
                "mailbox": target.props.get("mailbox_index"),
                **{key: feature.props.get(key) for key in WIRE_KEYS},
                **{key: int(target.props[key], 16) for key in ADDRESS_KEYS
                   if key in target.props},
                "profile": [dict(item) for item in feature.props.get("profiles", ())],
                "field": []}
    contexts = {item["name"]: {**item, "field": []} for item in feature.props.get("contexts", ())}
    for entity in fields(model):
        props = entity.props
        item = {"name": entity.slug, "width": props.get("width"), "kind": props.get("origin"),
                "signed": props.get("signed"), **_source(model, entity, allocations)}
        if props.get("dashboard"):
            item["dashboard"] = props["dashboard"]
        if "context" in props:
            contexts[props["context"]]["field"].append(item)
        else:
            document["field"].append({**item, "page": props.get("page"),
                                      "offset": props.get("offset"),
                                      "profiles": props.get("profiles")})
    document["context"] = list(contexts.values())
    if feature.props.get("padding"):
        document["padding"] = feature.props["padding"]
        allocation = allocations.get(feature.props.get("padding_source"))
        if allocation is None or allocation.get("width") != 1:
            raise KbError("telemetry padding requires its single-byte allocation", code=3)
        document["padding_source"] = int(allocation["address"], 16)
    return document


def _source(model, entity, allocations):
    """{source, scale} of a field: the address of the `7mfk` symbol of an
    `ecu_ram` field with the scale of its meaning, or the address of the
    allocation of another field with its own scale."""
    props = entity.props
    if props.get("origin") != "ecu_ram":
        entry = allocations.get(props.get("source"))
        if entry is None:
            raise KbError(f"{entity.key}: source {props.get('source')!r} is no allocation of a "
                          f"{CANONICAL} target", code=3)
        return {"source": int(entry["address"], 16), "scale": props.get("scale")}
    keys = entity.refs.get("source", ())
    if len(keys) != 1 or not isinstance(keys[0], SymbolKey) or keys[0].layout != CANONICAL:
        raise KbError(f"{entity.key}: the source names no {CANONICAL} symbol", code=3)
    if props.get("scale") == STORED_COUNT_SCALE:
        return {"source": keys[0].address, "scale": STORED_COUNT_SCALE}
    meaning = model.meaning_of(keys[0])
    scale = scale_text(meaning.props) if meaning else None
    if meaning is not None and not any(
            key in meaning.props for key in ("scale", "unit", "value", "bit")):
        # This host storage view supplies no semantic scale or evidence.
        scale = STORED_COUNT_SCALE
    return {"source": keys[0].address, "scale": scale}


def _toml(key, value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return HEXADECIMAL.get(key, "{}").format(value)
    if isinstance(value, str):
        return f'"{store.escape(value)}"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml(key, item) for item in value) + "]"
    raise KbError(f"no profile form of {key} = {value!r}", code=3)


def _assignment(key, value):
    """The lines of one key: a string longer than a short line as the store
    writes it, a multiline basic string whose value holds no newline."""
    if isinstance(value, str) and len(value) > store.SHORT:
        return store.string_lines(value, f"{key} = ", "")
    return [f"{key} = {_toml(key, value)}"]


def _block(header, item, order, subject, optional=False):
    """The lines of one table of the profile with the keys of `order`, each
    of which the table states unless they are `optional`, followed by its
    presentation and the feed channel of the presentation."""
    unknown = sorted(set(item) - set(order) - {"field", "dashboard", "feed"})
    missing = [] if optional else [key for key in order if item.get(key) is None]
    if unknown or missing:
        raise KbError(f"{subject}: unknown keys {unknown}, no value of {missing}", code=3)
    lines = [header] if header else []
    for key in order:
        if item.get(key) is not None:
            lines += _assignment(key, item[key])
    blocks = ["\n".join(lines)]
    table = header.strip("[]") if header else None
    if item.get("dashboard"):
        blocks.append(_block(f"[{table}.dashboard]", item["dashboard"], DASHBOARD_ORDER,
                             f"{subject}.dashboard", optional=True))
    if item.get("feed"):
        blocks.append(_block(f"[{table}.feed]", item["feed"], FEED_ORDER, f"{subject}.feed",
                             optional=True))
    return "\n\n".join(blocks)


def render_profile(document):
    """The text of `patches/can-telemetry-profile.toml` from its document."""
    top = {key: value for key, value in document.items()
           if key not in ("profile", "field", "context", "padding")}
    order = TOP + (("padding_source",) if "padding_source" in top else ())
    blocks = [HEADER + "\n" + _block(None, top, order, "profile")]
    for item in document.get("profile", ()):
        subject = f"profile.{item.get('name')}"
        blocks.append(_block("[[profile]]", {key: value for key, value in item.items()
                                             if key != "dynamic"}, PROFILE_ORDER, subject))
        if item.get("dynamic"):
            blocks.append(_block("[profile.dynamic]", item["dynamic"], DYNAMIC_ORDER,
                                 f"{subject}.dynamic"))
    blocks += [_block("[[padding]]", item,
                      ("page", "offset", "width") + (("tag",) if "tag" in item else ()),
                      "padding") for item in document.get("padding", ())]
    blocks += [_block("[[field]]", item, STREAM_ORDER, f"field.{item.get('name')}")
               for item in document.get("field", ())]
    for context in document.get("context", ()):
        blocks.append(_block("[[context]]", context, CONTEXT_ORDER,
                             f"context.{context.get('name')}"))
        blocks += [_block("[[context.field]]", item, FIELD_ORDER, f"field.{item.get('name')}")
                   for item in context.get("field", ())]
    return "\n\n".join(blocks) + "\n"


def _scales(document):
    """(document without the `ecu_ram` scales, {field: its `ecu_ram` scale})."""
    scales = {}

    def strip(item):
        if item.get("kind") != "ecu_ram":
            return item
        scales[item.get("name")] = item.get("scale")
        return {key: value for key, value in item.items() if key != "scale"}

    found = {**document, "field": [strip(item) for item in document.get("field", ())],
             "context": [{**context, "field": [strip(item) for item in context.get("field", ())]}
                         for context in document.get("context", ())]}
    return found, scales


def scale_changes(text, document):
    """[(field, scale of `text`, scale of `document`)] of the `ecu_ram` scales
    that the profile document changes in the profile text; a text outside the
    form of the projection or another change refuses."""
    held = tomllib.loads(text)
    if render_profile(held) != text:
        raise KbError(f"{PROFILE.as_posix()} is not in the form of its projection", code=3)
    before, old = _scales(held)
    after, new = _scales(document)
    if before != after:
        raise KbError(f"the model changes {PROFILE.as_posix()} beyond the scales of its "
                      "ecu_ram fields", code=3)
    return [(name, old[name], new[name]) for name in old if old[name] != new.get(name)]


def profile(root=repo.ROOT):
    """The text of `patches/can-telemetry-profile.toml` from the model."""
    from kb import compile
    return render_profile(profile_document(compile.cached(root)))
