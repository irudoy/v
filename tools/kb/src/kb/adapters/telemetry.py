"""The CAN telemetry profile of JK08A (tools/kb/SPEC.md, sections 7.9 and
20.5).

- Each `[[field]]` and `[[context.field]]` gives the `field` entity of its
  `name` with `kind` as `origin`, `width`, `signed`, and its place: `page`,
  `offset`, and `profiles` in the stream, or the `context` and the `position`
  inside it. The signal whose `current_fields` lists the field is its
  `signal`.
- The source of an `ecu_ram` field is the `7mfk` symbol at its address, joined
  by the field as a telemetry source of the address profiles is. Its `scale`
  parses into the source meaning: the arithmetic in `raw` becomes `scale` in
  `x` with its `unit` from `[vocab] unit` of `tools/kb/config.toml`, a leading
  `candidate` sets `scale_level`, an enumeration becomes `value` entries, and
  the remaining text joins the summary. A string that the parser cannot split
  stays the `scale` of the field and goes to the `unsplit` section of the
  audit. `telemetry_units` of the stash lists the symbols whose unit the
  profile states.
- The source of a field of another origin is the allocation, named after
  the field without `_raw`, of the feature that owns its address: the state
  record and the configuration record of `can_telemetry` for
  `telemetry_state` and `rom_configuration`, and the active RAM of
  `map_switching` or `rolling_launch` in the reservation ledger for
  `runtime_state`. The field keeps its `scale` and names the allocation as
  `<feature>.<allocation>`. `feature_ram` of the stash holds the active RAM of
  every feature.
- The wire constants, `[[profile]]`, and the contexts become keys of the
  `can_telemetry` feature; the mailbox and the table, configuration, and
  state addresses become keys of its `7mfk` target. The feature `requires`
  every field it declares, so the source meaning of each is required on every
  layout that the feature targets.
"""

from pathlib import Path
import re
import tomllib

from kb.values import hexed

PROFILE = Path("patches/can-telemetry-profile.toml")
LAYOUT = Path("patches/can-telemetry-layout.toml")
RESERVATIONS = Path("patches/jk08a-runtime-reservations.toml")
SCHEMA_VERSION = 2
CANONICAL = "7mfk"
FEATURE = "can_telemetry"
RUNTIME_OWNERS = ("map_switching", "rolling_launch")
WIRE_KEYS = ("protocol_version", "byte_order", "candidate_can_id", "candidate_tick_divisor",
             "base_tick_numerator", "pphi_hz", "fixed_page_count", "context_pages",
             "context_count", "header_sequence_bits")
ADDRESS_KEYS = ("table_address", "table_end", "configuration_address", "state_address")
DOCUMENT_KEYS = frozenset({"schema_version", "rom", "mailbox", "profile", "field", "context",
                           *WIRE_KEYS, *ADDRESS_KEYS})
FIELD_KEYS = frozenset({"name", "width", "source", "kind", "signed", "scale"})
STREAM_KEYS = FIELD_KEYS | {"page", "offset", "profiles"}
CONTEXT_KEYS = frozenset({"page", "tag", "name", "field"})
PROFILE_KEYS = frozenset({"name", "id", "page_count"})
KINDS = ("ecu_ram", "rom_configuration", "runtime_state", "telemetry_state")

NUMBER = r"\d+(?:\.\d+)?"
TERM = rf"(?:raw|{NUMBER})"
SCALE = re.compile(rf"(?P<candidate>candidate\s+)?(?P<arithmetic>{TERM}(?:\s*[-+*/]\s*{TERM})+)"
                   r"\s+(?P<unit>[^\s,;]+)[,;]?\s*(?P<rest>.*)", re.DOTALL)
# Arithmetic in `raw` inside the remaining text states a second scale.
SECOND = re.compile(r"\braw\s*[-+*/]|[-+*/]\s*raw\b")
RAW = re.compile(r"\braw\b")
ENUMERATION = "enumeration: "
VALUE = re.compile(r"(\d+) ([A-Z][A-Z0-9_]*)")


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
    if text.startswith(ENUMERATION):
        values = [VALUE.fullmatch(item) for item in text[len(ENUMERATION):].split(", ")]
        if all(values):
            return {"value": [{"value": int(item[1]), "name": item[2].lower()}
                              for item in values]}
    return None


def _regions(b, root):
    """{kind: [(start, end, feature)]}: the addresses that the source of a field
    of each kind other than `ecu_ram` may occupy, and the feature that owns
    them."""
    layout = tomllib.loads((root / LAYOUT).read_text(encoding="utf-8"))
    ledger = tomllib.loads((root / RESERVATIONS).read_text(encoding="utf-8"))
    ram = layout["ram"]
    active = [(row["start"], row["end"], row["owner"]) for row in ledger["active_ram"]]
    b.stash["feature_ram"] = active
    configuration = layout["configuration_address"]
    return {
        "telemetry_state": [(ram["state_start"], ram["state_start"] + ram["state_size"],
                             FEATURE)],
        "rom_configuration": [(configuration, configuration + layout["configuration_size"],
                               FEATURE)],
        "runtime_state": [span for span in active if span[2] in RUNTIME_OWNERS],
    }


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
        if set(item) != PROFILE_KEYS:
            b.issue("schema", src, f"profile.{item.get('name', index)}",
                    f"keys {sorted(item)}; the adapter reads {sorted(PROFILE_KEYS)}")
            continue
        profiles.append(dict(item))
    contexts = [{"name": item.get("name"), "page": item.get("page"), "tag": item.get("tag")}
                for item in document.get("context", ())]
    b.entity("feature", FEATURE, src, props={
        **{name: document[name] for name in WIRE_KEYS if name in document},
        "profiles": profiles, "contexts": contexts})
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
        if set(item) != keys:
            b.issue("schema", src, subject, f"missing {sorted(keys - set(item))}; "
                    f"unknown {sorted(set(item) - keys)}")
            continue
        if name in seen:
            b.issue("schema", src, subject, "a second field of the name")
            continue
        seen.add(name)
        kind = item["kind"]
        props = {"origin": kind, "width": item["width"], "signed": item["signed"], **place}
        refs = {}
        signal = owners.get(name)
        if signal is not None:
            refs["signal"] = [("signal", signal)]
        elif kind == "ecu_ram":
            b.issue("schema", src, subject, "an ecu_ram field that no signal lists")
        if kind == "ecu_ram":
            key = _ecu_source(b, item, src, subject)
            if key is None:
                continue
            refs["source"] = [key]
            parsed = parse_scale(item["scale"], units)
            if parsed is None:
                props["scale"] = item["scale"]
                b.issue("unsplit", src, subject, f"scale {item['scale']!r}")
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
        b.issue("schema", src, subject, f"ecu_ram source {address:08x} lies outside the "
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
        b.issue("schema", src, subject, f"{item['kind']} source {address:08x} lies outside "
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
