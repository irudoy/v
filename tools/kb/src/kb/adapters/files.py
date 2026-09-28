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
"""

import tomllib

from kb import store, vocab
from kb.model import Ref

ADDRESS_KEYS = ("layout", "address", "name", "former", "evidence")
MEANING_ARRAYS = ("symbol", "status", "link", "analog")
TABLE_KEYS = ("editor", "logparam", "diagnostic")
# Keys of a feature target whose entries hold a symbol reference: tables of
# named entries, arrays of entries, tables of references, and lists of meaning
# references, which name the home symbol of their meaning.
TARGET_REFS = {"roles": "symbol", "hooks": "hook", "allocations": "did"}
TARGET_ARRAYS = {"variants": "symbol", "omitted": "symbol", "unsupported": "symbol"}
TARGET_TABLES = ("families", "symbols")
TARGET_LISTS = ("requires",)
# Designed kinds that the store holds from the stage that converts them.
CONVERTED_KINDS = ("feature",)


def inputs(root):
    return [path.as_posix() for _, _, path in store.files(root)]


def declare(b, root):
    for kind, name, path in store.files(root, b.overlay):
        src = path.as_posix()
        try:
            document = store.load(root, path, b.overlay)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
            b.issue("schema", src, f"{name}/{kind}", f"no TOML: {error}")
            continue
        if kind in vocab.MEANING_KINDS:
            _unknown(b, src, f"{name}/{kind}", document, store.schema(kind))
            _meaning(b, kind, name, document, src)
        elif kind in CONVERTED_KINDS:
            _feature(b, name, document, src)
        else:
            b.issue("schema", src, f"{name}/{kind}",
                    f"the store holds no {kind} entities before their conversion stage")


def relate(b, root):
    pass


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
    group = (kind, "file", name)
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
               evidence=evidence, layouts=stated or None)


def _former_name(text):
    """The name of a former full reference, or a former name."""
    return text.split("/", 1)[0]


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
