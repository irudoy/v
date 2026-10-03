"""The entity files of the store (tools/kb/SPEC.md, sections 4 and 7).

- A meaning file `<kind>/<name>.toml` of the store gives one meaning: its
  symbols join the group of the file with the strength `file`, a semantic file
  name names the meaning with the tier `file`, and each former name reserves
  the name with the tier `former`. The keys of the meaning, its feature
  tables, its statuses, and its links state the facts of the meaning; the keys
  of a symbol state the overrides of its layout.
- A generated file name leaves the meaning unnamed: every symbol carries its
  generated name in `name`, and the file takes the name of the home symbol.
- A symbol merges by layout, kind, and address with the symbols that the
  adapters of the unconverted registries declare, so a file owns the facts of
  its conversion stage and a registry keeps the others.
- References stay text until the model names the meanings: the `to` of a
  link, `via`, `kernel` of `[interp]`, `static_axis_operand` of `[editor]`,
  a reference-form `to` of evidence, the symbol references of the feature
  targets, and the meaning references of their `requires`. A location
  `<layout>:<address>` in evidence stays a location.
- A feature file `feature/<slug>.toml` gives the feature entity with its keys
  and each `[[target]]` the target of its layout; the keys of a feature and of
  its targets are those of the feature (section 7.9).
- A field file `field/<name>.toml` gives the field entity with its keys; its
  `signal` and the `source` of an `ecu_ram` field are references, and the
  source names the `7mfk` symbol of its meaning; the `fields` check verifies
  the signal, the source, and the scale of each field. The `can_telemetry`
  feature requires every field, and `telemetry_units` of the stash holds the
  `7mfk` symbols whose numeric source meanings own their unit, including an
  absent unit. Enumerations and bit fields without a file unit retain the
  ledger's storage description.
- A signal file `signal/<slug>.toml` gives the signal entity with its keys;
  `observes` lists meaning references, which name the `7mfk` symbols of
  their meanings, and allocation references `<feature>.<allocation>`, which
  are also a key of the signal. An allocation reference that names no
  allocation of a `7mfk` target fails the `references` check.
"""

import tomllib

from kb import store, vocab
from kb.model import MEANING_REF, Ref

ADDRESS_KEYS = ("layout", "address", "name", "former", "evidence")
MEANING_ARRAYS = ("symbol", "status", "link", "analog")
TABLE_KEYS = ("editor", "logparam", "diagnostic", "ledger")
# Keys of a feature target whose entries hold a symbol reference: tables of
# named entries, arrays of entries, tables of references, and lists of meaning
# references, which name the home symbol of their meaning.
TARGET_REFS = {"roles": "symbol", "hooks": "hook", "allocations": "did"}
TARGET_ARRAYS = {"variants": "symbol", "omitted": "symbol", "unsupported": "symbol"}
TARGET_TABLES = ("families", "symbols")
TARGET_LISTS = ("requires",)
# Designed kinds that the store holds from the stage that converts them.
CONVERTED_KINDS = ("feature", "field", "signal", "stage", "block", "endpoint", "chain")
# The feature that transmits the fields, and the layout of the symbols that
# the source of an `ecu_ram` field and the observed meanings of a signal name
# and of the targets whose allocations a signal observes.
TELEMETRY = "can_telemetry"
TELEMETRY_LAYOUT = "7mfk"


def inputs(root):
    return [path.as_posix() for _, _, path in store.files(root)]


def declare(b, root):
    # {(kind, name): (symbol keys by layout, whether the file owns the unit)}
    # of the meaning files, and [(name, source reference)] of the `ecu_ram`
    # fields.
    meanings, sources, fields = {}, [], []
    for kind, name, path in store.files(root, b.overlay):
        src = path.as_posix()
        try:
            document = store.load(root, path, b.overlay)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
            b.issue("schema", src, f"{name}/{kind}", f"no TOML: {error}")
            continue
        if kind in vocab.MEANING_KINDS:
            _unknown(b, src, f"{name}/{kind}", document, store.schema(kind))
            keys = _meaning(b, kind, name, document, src)
            owns_unit = "unit" in document or not any(
                key in document for key in ("value", "bit"))
            meanings[(kind, name)] = (keys, owns_unit)
        elif kind == "feature":
            _feature(b, name, document, src)
        elif kind == "field":
            _unknown(b, src, f"{name}/{kind}", document, store.schema(kind))
            source = _field(b, name, document, src)
            fields.append(("field", name))
            if source is not None:
                sources.append(source)
        elif kind == "signal":
            _unknown(b, src, f"{name}/{kind}", document, store.schema(kind))
            _signal(b, name, document, src)
        elif kind in ("stage", "block", "endpoint", "chain"):
            _unknown(b, src, f"{name}/{kind}", document, store.schema(kind))
            _architecture(b, kind, name, document, src)
        else:
            b.issue("schema", src, f"{name}/{kind}",
                    f"the store holds no {kind} entities before their conversion stage")
    if fields:
        b.entity("feature", TELEMETRY, store.path_of("feature", TELEMETRY).as_posix(),
                 refs={"requires": fields})
    units = b.stash.setdefault("telemetry_units", set())
    for text in sources:
        found = MEANING_REF.fullmatch(text)
        place = (found["kind"], found["name"]) if found else None
        keys, unit = meanings.get(place, ({}, False))
        if unit and TELEMETRY_LAYOUT in keys:
            units.add(keys[TELEMETRY_LAYOUT])


def relate(b, root):
    for slug, src, references in b.stash.get(__name__, ()):
        for reference in references:
            feature, _, name = reference.partition(".")
            target = b.targets.get((feature, TELEMETRY_LAYOUT))
            if target is None or name not in target.props.get("allocations", {}):
                b.issue("references", src, f"{slug}/signal", f"{reference} is no allocation "
                        f"of a {TELEMETRY_LAYOUT} target")


def _unknown(b, src, subject, document, table, path=""):
    """Schema issues of the keys outside the schema of a table and its
    nested tables."""
    for key, value in document.items():
        spec = table.spec(key)
        where = f"{path}{key}"
        if spec is None:
            b.issue("schema", src, subject, f"unknown key {where}")
        elif isinstance(spec, store.Array) and isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    _unknown(b, src, subject, item, spec.table, f"{where}[{index}].")
        elif isinstance(spec, store.Table) and spec.keys and isinstance(value, dict):
            _unknown(b, src, subject, value, spec, f"{where}.")


def _address(b, src, subject, entry):
    layout, text = entry.get("layout"), entry.get("address")
    if layout not in b.layouts:
        b.issue("schema", src, subject, f"layout {layout!r}")
        return None
    if not isinstance(text, str) or not vocab.ADDRESS.fullmatch(text):
        b.issue("schema", src, subject, f"address {text!r} of {layout} is not eight lowercase "
                "hexadecimal digits")
        return None
    return layout, int(text, 16)


def _refs(value, src, layout=None):
    """References of a nested value of `[interp]`, `[editor]`, or a link."""
    return Ref(value, src, layout) if isinstance(value, str) else value


def _evidence(items, src):
    """Evidence items with a reference-form `to` as a reference."""
    found = []
    for item in items:
        item = dict(item)
        target = item.get("to")
        if isinstance(target, str) and "/" in target:
            item["to"] = Ref(target, src)
        found.append(item)
    return found


def _keys(props, src, layout=None):
    """Keys of a meaning or a symbol with their references."""
    found = dict(props)
    if isinstance(found.get("interp"), dict) and "kernel" in found["interp"]:
        found["interp"] = {**found["interp"],
                           "kernel": _refs(found["interp"]["kernel"], src, layout)}
    editor = found.get("editor")
    if isinstance(editor, dict) and "static_axis_operand" in editor:
        found["editor"] = {**editor, "static_axis_operand": _refs(
            editor["static_axis_operand"], src, layout)}
    return found


def _meaning(b, kind, name, document, src):
    """Declare a meaning file; returns {layout: symbol key} of its entries."""
    group = (kind, "file", name)
    keys = {}
    subject = f"{name}/{kind}"
    b.files[(kind, name)] = (group, src)
    semantic = bool(vocab.SEMANTIC_NAME.fullmatch(name))
    if semantic:
        b.name(group, name, "file", src)
    elif not vocab.GENERATED_NAME.fullmatch(name):
        b.issue("names", src, subject, "a file name is a semantic or a generated name")
    for former in document.get("former", ()):
        b.name(group, former, "former", src)
    props = {key: value for key, value in document.items()
             if key not in MEANING_ARRAYS + TABLE_KEYS + ("former",)}
    for key in ("editor", "logparam"):
        if key in document:
            props[key] = document[key]
    b.props(group, _keys(props, src), src)
    if document.get("ledger"):
        b.stash.setdefault("ledger_rows", []).append((kind, name, document["ledger"], src))
    for binding in document.get("diagnostic", ()):
        b.table(group, "diagnostic", {**binding, "evidence": _evidence(
            binding.get("evidence", ()), src)}, src)
    for index, entry in enumerate(document.get("symbol", ())):
        place = _address(b, src, f"{subject} symbol {index}", entry)
        if place is None:
            continue
        layout, address = place
        props = {key: value for key, value in entry.items() if key not in ADDRESS_KEYS}
        key = b.symbol(layout, kind, address, src, group=group, strength="file",
                       props=_keys(props, src, layout),
                       evidence=_evidence(entry.get("evidence", ()), src))
        keys.setdefault(layout, key)
        if entry.get("evidence"):
            b.file_evidence.add(key)
        generated = entry.get("name")
        if semantic and generated:
            b.issue("names", src, key.key, "a symbol of a named meaning carries a generated name")
        if not semantic and not generated:
            b.issue("names", src, key.key, "a symbol of an unnamed meaning lacks its generated "
                    "name")
        former = tuple(_former_name(text) for text in entry.get("former", ()))
        b.file_names[key] = (generated if not semantic else None, former, src)
        if generated and not semantic:
            b.generated[key] = generated
    for entry in document.get("status", ()):
        layout = entry.get("layout")
        if layout not in b.layouts:
            b.issue("schema", src, subject, f"status layout {layout!r}")
            continue
        if entry.get("state") not in vocab.STATUS_STATES:
            b.issue("schema", src, subject, f"status state {entry.get('state')!r} on {layout}")
            continue
        props = {key: value for key, value in entry.items()
                 if key not in ("layout", "state", "evidence")}
        b.status(group, layout, entry["state"], src, props=props,
                 evidence=_evidence(entry.get("evidence", ()), src))
    for entry in document.get("link", ()):
        if not isinstance(entry.get("to"), str) or "type" not in entry:
            b.issue("schema", src, subject, "a link without type or to")
            continue
        props = {key: value for key, value in entry.items()
                 if key not in ("type", "to", "evidence")}
        if "via" in props:
            props["via"] = [_refs(item, src) for item in props["via"]]
        evidence = _evidence(entry.get("evidence", ()), src)
        stated = {item["at"].split(":", 1)[0] for item in evidence
                  if isinstance(item.get("at"), str) and ":" in item["at"]}
        b.link(group, entry["type"], Ref(entry["to"], src), src, props=props,
               evidence=evidence, layouts=stated or props.get("layouts") or None)
    return keys


def _former_name(text):
    """The name of a former full reference, or a former name."""
    return text.split("/", 1)[0]


def _field(b, name, document, src):
    """Declare a field file; returns the source reference of an `ecu_ram`
    field, or None."""
    props = {key: value for key, value in document.items() if key != "signal"}
    refs = {}
    if isinstance(document.get("signal"), str):
        refs["signal"] = [Ref(document["signal"], src)]
    source = None
    if document.get("origin") == "ecu_ram" and isinstance(props.get("source"), str):
        source = props.pop("source")
        refs["source"] = [Ref(source, src, TELEMETRY_LAYOUT)]
    b.entity("field", name, src, props=props, refs=refs)
    return source


def _signal(b, slug, document, src):
    """Declare a signal file: the meaning references of `observes` name the
    `7mfk` symbols of their meanings, and its allocation references stay
    text, which `relate` checks."""
    props = {key: value for key, value in document.items() if key != "observes"}
    observes = document.get("observes", [])
    if not isinstance(observes, list) or not all(isinstance(item, str) for item in observes):
        b.issue("schema", src, f"{slug}/signal", "observes is no array of references")
        observes = []
    allocated = [item for item in observes if not MEANING_REF.fullmatch(item)]
    if allocated:
        props["observes"] = allocated
        b.stash.setdefault(__name__, []).append((slug, src, allocated))
    refs = [Ref(item, src, TELEMETRY_LAYOUT) if MEANING_REF.fullmatch(item) else item
            for item in observes]
    b.entity("signal", slug, src, props=props, refs={"observes": refs} if refs else None)


def _architecture(b, kind, slug, document, src):
    """Architecture references resolve on the entity's home layout."""
    fields = {'block': ('stage',), 'endpoint': ('block', 'registers', 'functions'),
              'chain': ('output',)}.get(kind, ())
    props = {key: value for key, value in document.items() if key not in (*fields, 'step')}
    home = document.get('home', '7mfk')
    references = {}
    for field in fields:
        value = document.get(field)
        if value is None:
            continue
        listed = [value] if field in ('stage', 'block', 'output') else value
        if not isinstance(listed, list) or any(not isinstance(ref, str) for ref in listed):
            b.issue('schema', src, f'{slug}/{kind}', f'{field} is no array of references')
            continue
        references[field] = [Ref(ref, src, home, strict=True) for ref in listed]
    entity = b.entity(kind, slug, src, props=props, refs=references)
    if kind != 'chain':
        return
    steps = document.get('step', [])
    if not isinstance(steps, list) or any(not isinstance(step, dict) for step in steps):
        b.issue('schema', src, f'{slug}/chain', 'step is no array of tables')
        return
    for index, step in enumerate(steps, 1):
        if any(not isinstance(step.get(field), str) for field in ('from', 'to')):
            b.issue('schema', src, f'{slug}/chain#{index}', 'from and to must be references')
            continue
        via = step.get('via', [])
        if not isinstance(via, list) or any(not isinstance(ref, str) for ref in via):
            b.issue('schema', src, f'{slug}/chain#{index}', 'via is no array of references')
            continue
        entity.steps.append({'from': Ref(step['from'], src, home, strict=True),
                             'to': Ref(step['to'], src, home, strict=True),
                             'effect': step.get('effect'), 'sign': step.get('sign'),
                             'via': [Ref(ref, src, home, strict=True) for ref in via],
                             'note': step.get('note'), 'specs': step.get('specs')})


def _feature(b, slug, document, src):
    props = {key: value for key, value in document.items() if key != "target"}
    b.entity("feature", slug, src, props=props)
    for entry in document.get("target", ()):
        layout = entry.get("layout")
        if layout not in b.layouts:
            b.issue("schema", src, f"{slug}/feature", f"target layout {layout!r}")
            continue
        props = {key: value for key, value in entry.items()
                 if key not in ("layout", "status")}
        for key, field in TARGET_REFS.items():
            if isinstance(props.get(key), dict):
                props[key] = {name: ({**item, field: Ref(item[field], src, layout)}
                                     if isinstance(item, dict) and field in item else item)
                              for name, item in props[key].items()}
        for key, field in TARGET_ARRAYS.items():
            if isinstance(props.get(key), list):
                props[key] = [{**item, field: Ref(item[field], src, layout)}
                              if isinstance(item, dict) and field in item else item
                              for item in props[key]]
        for key in TARGET_TABLES:
            if isinstance(props.get(key), dict):
                props[key] = {name: Ref(item, src, layout) if isinstance(item, str) else item
                              for name, item in props[key].items()}
        for key in TARGET_LISTS:
            if isinstance(props.get(key), list):
                props[key] = [Ref(item, src) if isinstance(item, str) else item
                              for item in props[key]]
        b.target(slug, layout, src, status=entry.get("status"), props=props)
