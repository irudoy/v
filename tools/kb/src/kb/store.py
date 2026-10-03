"""Entity files of `kb/` (tools/kb/SPEC.md, sections 4 and 7).

A meaning lives at `kb/<kind>/<name>.toml` and a designed entity at
`kb/<kind>/<slug>.toml`. `render` writes a document in the canonical form of
section 4.2: keys in the order of the schema of the kind, absent keys omitted,
short strings on one line, long strings wrapped within 78 columns, arrays that
do not fit on one line with one element per line, DID numbers and offsets in
hexadecimal, and arrays of tables sorted by the keys the schema names. Keys
outside the schema follow the known keys in alphabetical order. `canonical` is
the `canonical` check: every file equals the rendering of its parse.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import re
import tempfile
import tomllib

from kb import vocab
from kb.model import Issue

TREE = Path("kb")
WIDTH = 78
SHORT = 72
INDENT = "    "
BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")
ESCAPES = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f",
           "\r": "\\r"}

# Value specs: a plain value (a scalar, an array of scalars, or an inline
# table), an integer in hexadecimal, or a DID number in four hexadecimal
# digits.
PLAIN, HEX, DID = "plain", "hex", "did"


@dataclass(frozen=True)
class Table:
    """The schema of a table: its keys in canonical order with the spec of each
    value, and the keys that sort an array of the table."""

    keys: tuple = ()
    sort: tuple = ()
    inline: bool = False

    def spec(self, key):
        for name, spec in self.keys:
            if name == key:
                return spec
        return None

    def order(self, keys):
        known = [name for name, _ in self.keys if name in keys]
        return known + sorted(key for key in keys if self.spec(key) is None)


@dataclass(frozen=True)
class Array:
    """An array of tables of one schema."""

    table: Table


@dataclass(frozen=True)
class Named:
    """A table whose keys are names and whose values are tables of one schema;
    the entries follow in alphabetical order."""

    table: Table


def _plain(*names):
    return tuple((name, PLAIN) for name in names)


EVIDENCE = Table(_plain(*vocab.EVIDENCE_KEYS))
SCALE = ("unit", "scale", "to_raw", "scale_level")
INTERP = Table(_plain("access", "kernel") + (("offset", HEX),)
               + _plain("cols", "rows", "step", "storage", "x_storage", "y_storage"))
VIEW = Table(_plain(*vocab.VIEW_KEYS), sort=("name",))
EDITOR = Table(_plain(*vocab.EDITOR_KEYS) + (("view", Array(VIEW)),))
LOGPARAM = Table(_plain(*vocab.LOGPARAM_KEYS))
CLAIM = Table(_plain("label", "id"), inline=True)
DIAGNOSTIC = Table(_plain("id", "kind", "label", "key") + (("claim", CLAIM),)
                   + _plain("applicability", "scope", "priority", "level", "note")
                   + (("evidence", Array(EVIDENCE)),), sort=("id",))
LEDGER_DEPENDENCY = Table(_plain("role", "to", "type", "end", "link_role", "relies", "supports",
                                "offset_text") + (("offset", HEX),),
                          sort=("supports", "role", "to", "relies", "offset"))
LEDGER_OFFSET = Table(_plain("evidence", "text"), sort=("evidence",))
LEDGER = Table(_plain("registry", "order", "binding", "fields", "notes", "storage_description", "identity",
                      "contract", "scale", "title", "name")
               + (("dependency", Array(LEDGER_DEPENDENCY)), ("offset", Array(LEDGER_OFFSET))),
               sort=("registry",))
BIT = Table(_plain("bit", "name", "summary", "level") + (("evidence", Array(EVIDENCE)),),
            sort=("bit",))
VALUE = Table(_plain("value", "name", "summary", "reachable", "level")
              + (("evidence", Array(EVIDENCE)),), sort=("value",))
SYMBOL = Table(_plain("layout", "address", "name", "level", "former", "images", "width",
                      "signed", "storage", "cols", "rows", "points", "count", "quantity",
                      *SCALE, "index", "attribute", "summary", "note")
               + (("interp", INTERP), ("editor", EDITOR), ("bit", Array(BIT)),
                  ("evidence", Array(EVIDENCE))),
               sort=("layout", "address"))
STATUS = Table(_plain("layout", "state", "method", "target", "count", "l0", "note")
               + (("evidence", Array(EVIDENCE)),), sort=("layout",))
LINK = Table(_plain("type", "to", "slot") + (("offset", HEX),)
             + _plain("via", "layouts", "relies", "supports", "reverse_relies",
                      "reverse_supports", "role", "note")
             + (("evidence", Array(EVIDENCE)),), sort=("type", "to", "slot", "offset"))
ANALOG = Table(_plain("to", "note"), sort=("to",))

COMMON = ("title", "summary", "note", "level", "home", "role", "block", "former")
KIND_KEYS = {
    "fn": _plain("contract", "contract_level") + (("interp", INTERP),),
    "ram": _plain("width", "signed", *SCALE) + (("bit", Array(BIT)), ("value", Array(VALUE))),
    "reg": _plain("width", "signed", *SCALE) + (("bit", Array(BIT)), ("value", Array(VALUE))),
    "tbl": _plain("access", "cols", "rows", "storage", *SCALE),
    "axis": _plain("quantity", "points", "storage", *SCALE),
    "const": _plain("width", "count", "storage"),
    "hook": _plain("width"),
    "did": (("number", DID),) + _plain("width"),
    "dtc": _plain("code", "group", "disabled"),
}
FEATURE_TABLES = (("editor", EDITOR), ("logparam", LOGPARAM),
                  ("diagnostic", Array(DIAGNOSTIC)), ("ledger", Array(LEDGER)))
ARRAYS = (("symbol", Array(SYMBOL)), ("status", Array(STATUS)), ("link", Array(LINK)),
          ("analog", Array(ANALOG)))

TARGET = Table(_plain("layout", "status", "note"), sort=("layout",))
STEP = Table(_plain("from", "to", "effect", "sign", "via", "note", "specs"))
FEED = Table(_plain("key", "name", "format", "minimum", "maximum", "step"))
DASHBOARD = Table(_plain("label", "digits", "unit", "hexadecimal", "group", "panel",
                         "panel_label", "order", "description") + (("feed", FEED),))
DESIGNED = {
    "stage": Table(_plain("title", "lane", "order", "summary")),
    "block": Table(_plain("title", "stage", "summary", "generic", "specs", "home")),
    "endpoint": Table(_plain("title", "direction", "block", "peripheral", "summary",
                             "registers", "functions", "specs")),
    "chain": Table(_plain("title", "summary", "quantity", "output", "specs", "home")
                   + (("step", Array(STEP)),)),
    "signal": Table(_plain("title", "domain", "priority", "coverage", "basis", "observes",
                           "note")),
    "field": Table(_plain("signal", "source", "origin", "width", "signed", "scale",
                          "profiles", "page") + (("offset", HEX),)
                   + _plain("context", "position") + (("dashboard", DASHBOARD),)),
    "feature": Table(_plain("title", "summary", "specs", "acceptance", "requires", "vendor")
                     + (("target", Array(TARGET)),)),
}


def schema(kind):
    """The schema of the files of a kind."""
    if kind in DESIGNED:
        return DESIGNED[kind]
    if kind not in KIND_KEYS:
        raise KeyError(kind)
    return Table(_plain(*COMMON) + KIND_KEYS[kind] + FEATURE_TABLES + ARRAYS)


# Paths ---------------------------------------------------------------------


def path_of(kind, name):
    return TREE / kind / f"{name}.toml"


def files(root, overlay=None):
    """[(kind, name, repository path)] of every entity file, by kind and name.
    `overlay` maps repository paths to the text that replaces a file, or to
    None for a file that a change removes."""
    found = set()
    for kind in vocab.KINDS:
        directory = root / TREE / kind
        if directory.is_dir():
            found.update((kind, path.stem, path.relative_to(root))
                         for path in directory.glob("*.toml"))
    for path, text in (overlay or {}).items():
        path = Path(path)
        entry = (path.parent.name, path.stem, path)
        if text is None:
            found.discard(entry)
        elif path.parent.parent == TREE and path.parent.name in vocab.KINDS \
                and path.suffix == ".toml":
            found.add(entry)
    return sorted(found, key=lambda entry: (vocab.KINDS.index(entry[0]), entry[1]))


def load(root, path, overlay=None):
    if overlay and Path(path) in overlay:
        text = overlay[Path(path)]
        if text is None:
            raise FileNotFoundError(f"{Path(path).as_posix()} leaves the store")
        return tomllib.loads(text)
    return tomllib.loads((root / path).read_text(encoding="utf-8"))


def write(root, changes):
    """Write {repository path: text, or None to remove} through temporary files
    and renames."""
    for path, text in sorted(changes.items(), key=lambda item: str(item[0])):
        target = root / path
        if text is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
        os.replace(temporary, target)


# Rendering -----------------------------------------------------------------


def render(kind, document):
    """The canonical text of an entity file of a kind."""
    lines = []
    _table(lines, (), document, schema(kind), None)
    return "\n".join(lines) + "\n"


def _empty(value):
    return value is None or value == "" or value == [] or value == {} or value == ()


def _infer(value):
    """The spec of a value outside the schema."""
    if isinstance(value, dict):
        if value and all(isinstance(entry, dict) for entry in value.values()):
            return Named(Table())
        return Table()
    if isinstance(value, list) and value and all(isinstance(entry, dict) for entry in value):
        return Array(Table())
    return PLAIN


def _is_table(spec):
    return isinstance(spec, (Array, Named)) or (isinstance(spec, Table) and not spec.inline)


def _table(lines, path, document, table, header):
    present = {key: value for key, value in document.items() if not _empty(value)}
    order = table.order(present)
    specs = {key: table.spec(key) or _infer(present[key]) for key in order}
    plain = [key for key in order if not _is_table(specs[key])]
    nested = [key for key in order if _is_table(specs[key])]
    if header is not None and (plain or header.startswith("[[")):
        if lines:
            lines.append("")
        lines.append(header)
    for key in plain:
        lines.extend(_assignment(key, present[key], specs[key]))
    for key in nested:
        spec, value, inner = specs[key], present[key], path + (key,)
        if isinstance(spec, Array):
            for item in _sorted(value, spec.table.sort):
                _table(lines, inner, item, spec.table, f"[[{_dotted(inner)}]]")
        elif isinstance(spec, Named):
            for name in sorted(value):
                entry = value[name]
                if _empty(entry):
                    continue
                _table(lines, inner + (name,), entry, spec.table,
                       f"[{_dotted(inner + (name,))}]")
        else:
            _table(lines, inner, value, spec, f"[{_dotted(inner)}]")


def _sorted(items, keys):
    if not keys:
        return list(items)

    def order(item):
        return tuple((0, type(item[key]).__name__, item[key]) if key in item else (1, "", 0)
                     for key in keys)

    return sorted(items, key=order)


def _dotted(parts):
    return ".".join(_key(part) for part in parts)


def _key(name):
    return name if BARE_KEY.fullmatch(name) else f'"{escape(name)}"'


def escape(text):
    out = []
    for char in text:
        if char in ESCAPES:
            out.append(ESCAPES[char])
        elif ord(char) < 0x20 or ord(char) == 0x7F:
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    return "".join(out)


def _assignment(key, value, spec):
    prefix = f"{_key(key)} = "
    if isinstance(value, str):
        return string_lines(value, prefix, "")
    if isinstance(value, list):
        return _array(prefix, value, spec)
    return [prefix + _scalar(value, spec)]


def _scalar(value, spec):
    """One line for a value that is no string and no array of strings."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        if spec == DID and value >= 0:
            return f"0x{value:04x}"
        if spec == HEX and value >= 0:
            return f"0x{value:x}"
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return f'"{escape(value)}"'
    if isinstance(value, dict):
        table = spec if isinstance(spec, Table) else Table()
        items = [f"{_key(key)} = {_scalar(value[key], table.spec(key))}"
                 for key in table.order(value) if not _empty(value[key])]
        return "{" + ", ".join(items) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_scalar(item, spec) for item in value) + "]"
    raise TypeError(f"no TOML form for {value!r}")


def _array(prefix, values, spec):
    single = [None if isinstance(item, str) and len(item) > SHORT else _scalar(item, spec)
              for item in values]
    if None not in single:
        line = prefix + "[" + ", ".join(single) + "]"
        if len(line) <= WIDTH:
            return [line]
    lines = [prefix + "["]
    for item, text in zip(values, single):
        if isinstance(item, str):
            lines.extend(string_lines(item, INDENT, ","))
        else:
            lines.append(f"{INDENT}{text},")
    lines.append("]")
    return lines


def string_lines(text, prefix, suffix):
    """A string as a basic string on one line when it has at most 72
    characters, and otherwise as a multiline basic string whose lines end in a
    space and a backslash, so that the value holds no newline."""
    escaped = escape(text)
    if len(text) <= SHORT:
        return [f'{prefix}"{escaped}"{suffix}']
    close = '"""' + suffix
    words = escaped.split(" ")
    lines, current = [], [words[0]]
    for index in range(1, len(words)):
        word = words[index]
        width = len(" ".join(current)) + 1 + len(word)
        if width + 2 > WIDTH and _breaks(current[-1], word):
            lines.append(current)
            current = [word]
        else:
            current.append(word)
    if len(" ".join(current)) + len(close) > WIDTH:
        for cut in range(len(current) - 1, 0, -1):
            head, tail = current[:cut], current[cut:]
            if _breaks(head[-1], tail[0]) and len(" ".join(tail)) + len(close) <= WIDTH:
                lines.append(head)
                current = tail
                break
    lines.append(current)
    body = [" ".join(line) + " \\" for line in lines[:-1]] + [" ".join(lines[-1]) + close]
    return [f'{prefix}"""'] + body


def _breaks(left, right):
    """A line may end between two words that one space separates."""
    return bool(left) and bool(right)


# The canonical check --------------------------------------------------------


def canonical(root, overlay=None):
    """Issues of the files that differ from the canonical rendering of their
    parse, or that do not parse; `overlay` as in `files`."""
    issues = []
    for kind, name, path in files(root, overlay):
        if overlay and path in overlay:
            text = overlay[path]
        else:
            text = (root / path).read_text(encoding="utf-8")
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            issues.append(Issue("canonical", path.as_posix(), f"{name}/{kind}",
                                f"no TOML: {error}"))
            continue
        if render(kind, document) != text:
            issues.append(Issue("canonical", path.as_posix(), f"{name}/{kind}",
                                "differs from its canonical form; run `uv run kb fmt`"))
    return issues


def fmt(root, paths=None):
    """Rewrite the files, or those of `paths`, in canonical form; returns the
    rewritten paths."""
    chosen = {Path(path) for path in paths} if paths else None
    changes = {}
    for kind, _, path in files(root):
        if chosen is not None and path not in chosen:
            continue
        text = (root / path).read_text(encoding="utf-8")
        rendered = render(kind, tomllib.loads(text))
        if rendered != text:
            changes[path] = rendered
    write(root, changes)
    return sorted(changes)
