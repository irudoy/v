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

from collections import OrderedDict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
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
ESCAPABLE = re.compile(r'[\x00-\x1f\x7f"\\]')

# Value specs: a plain value (a scalar, an array of scalars, or an inline
# table), an integer in hexadecimal, or a DID number in four hexadecimal
# digits.
PLAIN, HEX, DID = "plain", "hex", "did"
TEXT, INTEGER, BOOLEAN, STRINGS = "text", "integer", "boolean", "strings"


@dataclass(frozen=True)
class Table:
    """The schema of a table: its keys in canonical order with the spec of each
    value, and the keys that sort an array of the table."""

    keys: tuple = ()
    sort: tuple = ()
    inline: bool = False

    def spec(self, key):
        if type(self) is Table and type(key) is str:
            keys = self.keys
            lookup = self.__dict__.get("_lookup")
            if lookup is None or lookup[0] is not keys:
                index = _schema_index(keys)
                object.__setattr__(self, "_lookup", (keys, index))
            else:
                index = lookup[1]
            if index is not None:
                return index.get(key)
        for name, spec in self.keys:
            if name == key:
                return spec
        return None

    def order(self, keys):
        known = [name for name, _ in self.keys if name in keys]
        if type(self) is Table and type(keys) in (dict, list, tuple, set, frozenset) \
                and keys and all(type(key) is str for key in keys):
            held = self.keys
            lookup = self.__dict__.get("_lookup")
            if lookup is None or lookup[0] is not held:
                index = _schema_index(held)
                object.__setattr__(self, "_lookup", (held, index))
            else:
                index = lookup[1]
            if index is not None:
                return known + sorted(key for key in keys if index.get(key) is None)
        return known + sorted(key for key in keys if self.spec(key) is None)


def _schema_index(keys):
    """First specs of exact immutable grammar keys; other inputs keep scans."""
    if type(keys) is not tuple or any(type(item) is not tuple or len(item) != 2
                                     or type(item[0]) is not str for item in keys):
        return None
    index = {}
    for name, spec in keys:
        if name not in index:
            index[name] = spec
    return index


_TABLE_SPEC, _TABLE_ORDER = Table.spec, Table.order
_PROGRAM_SHAPES = 64


def _table_program(table, present):
    """Prepare schema lookups, retaining current values and nested specs."""
    if (type(table) is not Table or Table.spec is not _TABLE_SPEC
            or Table.order is not _TABLE_ORDER
            or 'spec' in vars(table) or 'order' in vars(table)
            or any(type(key) is not str for key in present)):
        return None
    held = vars(table).get('_programs')
    if held is None or held[0] is not table.keys:
        index = _schema_index(table.keys)
        if index is None:
            return None
        held = (table.keys, index, OrderedDict())
        object.__setattr__(table, '_programs', held)
    index, programs = held[1:]
    if any(key not in index for key in present):
        return None
    shape = frozenset(present)
    if shape in programs:
        programs.move_to_end(shape)
        return programs[shape]
    program = tuple((key, table.spec(key)) for key in table.order(present))
    if any(spec is not None and type(spec) not in (str, Table, Array, Named)
           for _, spec in program):
        return None
    while len(programs) >= _PROGRAM_SHAPES:
        programs.popitem(last=False)
    programs[shape] = program
    return program


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


def _text(*names):
    return tuple((name, TEXT) for name in names)


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
CURATED = Table(_plain("order", "name", "title", "notes"))
SOURCE = Table(_plain("layout", "path", "sha256", "sections", "anchor", "role"), sort=("path", "anchor"))
VALUE = Table(_plain("value", "name", "summary", "reachable", "level")
              + (("evidence", Array(EVIDENCE)),), sort=("value",))
SYMBOL = Table(_plain("layout", "address", "name", "level", "former", "images", "width",
                      "signed", "storage", "cols", "rows", "points", "count", "quantity",
                      *SCALE, "index", "attribute", "summary", "note")
               + (("interp", INTERP), ("editor", EDITOR), ("curated", CURATED), ("bit", Array(BIT)),
                  ("evidence", Array(EVIDENCE))),
               sort=("layout", "address"))
STATUS = Table(_plain("layout", "state", "method", "target", "count", "candidate", "l0",
                      "note")
               + (("evidence", Array(EVIDENCE)),), sort=("layout",))
LINK = Table(_plain("type", "to", "slot") + (("offset", HEX),)
             + _plain("via", "layouts", "relies", "supports", "reverse_relies",
                      "reverse_supports", "role", "note")
             + (("evidence", Array(EVIDENCE)),), sort=("type", "to", "slot", "offset"))
ANALOG = Table(_plain("to", "note"), sort=("to",))

COMMON = ("retired", "title", "summary", "note", "level", "home", "role", "block", "former")
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
                  ("diagnostic", Array(DIAGNOSTIC)), ("ledger", Array(LEDGER)),
                  ("source", Array(SOURCE)))
ARRAYS = (("symbol", Array(SYMBOL)), ("status", Array(STATUS)), ("link", Array(LINK)),
          ("analog", Array(ANALOG)))

TARGET = Table(_plain("layout", "status", "note"), sort=("layout",))
CATALOG = Table((("order", INTEGER),) + _text("source", "sha256", "original"), sort=("order",))
RESEARCH = Table(_text("state", "source_commit", "source_path", "source_sha256")
                 + (("order", INTEGER),) + _text("step_sha256", "original"))
STEP = Table(_text("from", "to", "effect", "sign")
             + (("via", STRINGS), ("note", TEXT), ("specs", STRINGS),
                ("research", RESEARCH)))
FEED = Table(_plain("key", "name", "format", "minimum", "maximum", "step"))
DASHBOARD = Table(_plain("label", "digits", "unit", "hexadecimal", "group", "panel",
                         "panel_label", "order", "description") + (("feed", FEED),))
DESIGNED = {
    "stage": Table(_text("title", "lane") + (("order", INTEGER),) + _text("summary")),
    "block": Table(_text("title", "stage", "summary")
                   + (("generic", BOOLEAN), ("specs", STRINGS), ("home", TEXT),
                      ("order", INTEGER))),
    "endpoint": Table(_text("title", "direction", "block", "peripheral", "summary")
                      + (("registers", STRINGS), ("functions", STRINGS), ("specs", STRINGS),
                         ("home", TEXT), ("order", INTEGER))),
    "chain": Table(_text("title", "summary", "quantity", "output")
                   + (("specs", STRINGS), ("home", TEXT), ("layouts", STRINGS), ("order", INTEGER),
                      ("step", Array(STEP)))),
    "signal": Table(_plain("title", "domain", "priority", "coverage", "basis", "observes",
                           "note")),
    "field": Table(_plain("signal", "source", "origin", "width", "signed", "scale",
                          "profiles", "page") + (("offset", HEX),)
                   + _plain("context", "position") + (("dashboard", DASHBOARD),)),
    "feature": Table(_plain("title", "summary", "specs", "acceptance", "requires", "vendor",
                            "requirements_state")
                     + (("catalog", Array(CATALOG)), ("target", Array(TARGET)))),
}


def schema(kind):
    """The schema of the files of a kind."""
    if kind in DESIGNED:
        return Table((("retired", BOOLEAN),) + DESIGNED[kind].keys, sort=DESIGNED[kind].sort)
    if kind not in KIND_KEYS:
        raise KeyError(kind)
    return Table(_plain(*COMMON) + KIND_KEYS[kind] + FEATURE_TABLES + ARRAYS)


_NATIVE_SCHEMA, _NATIVE_PLAIN = schema, _plain
_NATIVE_TABLE, _NATIVE_TABLE_INIT = Table, Table.__init__
_NATIVE_ARRAY, _NATIVE_NAMED, _NATIVE_INLINE = Array, Named, Table.inline
_RENDER_SCHEMAS = OrderedDict()


def _render_schema(kind):
    """Prepare private grammar traversals while public schemas stay separate."""
    if (type(kind) is not str or schema is not _NATIVE_SCHEMA
            or _plain is not _NATIVE_PLAIN or Table is not _NATIVE_TABLE
            or Table.__init__ is not _NATIVE_TABLE_INIT
            or Table.__getattribute__ is not object.__getattribute__
            or Table.spec is not _TABLE_SPEC or Table.order is not _TABLE_ORDER
            or _table is not _NATIVE_TABLE_RENDERER):
        return schema(kind)
    if kind in DESIGNED:
        declared = DESIGNED[kind]
        if type(declared) is not Table:
            return schema(kind)
        sources = (declared.keys, declared.sort, BOOLEAN)
    elif kind in KIND_KEYS:
        sources = (COMMON, KIND_KEYS[kind], FEATURE_TABLES, ARRAYS, PLAIN)
    else:
        return schema(kind)
    held = _RENDER_SCHEMAS.get(kind)
    if held is not None:
        previous, keys, sort, table = held
        if (len(previous) == len(sources)
                and all(old is current for old, current in zip(previous, sources))
                and table.keys is keys and table.sort is sort and table.inline is False
                and 'spec' not in vars(table) and 'order' not in vars(table)):
            _RENDER_SCHEMAS.move_to_end(kind)
            return table
    if kind in DESIGNED:
        if _schema_index(declared.keys) is None or type(declared.sort) is not tuple:
            return schema(kind)
    elif (type(COMMON) is not tuple or any(type(name) is not str for name in COMMON)
          or any(_schema_index(keys) is None for keys in sources[1:4])):
        return schema(kind)
    table = schema(kind)
    while len(_RENDER_SCHEMAS) >= 32:
        _RENDER_SCHEMAS.popitem(last=False)
    _RENDER_SCHEMAS[kind] = sources, table.keys, table.sort, table
    return table


# Paths ---------------------------------------------------------------------


def path_of(kind, name):
    return TREE / kind / f"{name}.toml"


def owns(model, symbol):
    """Whether the files own a symbol: only files state it, or a file entry
    states its evidence. A file entry that only names the symbol of a registry
    joins its meaning, and the registry keeps the symbol's evidence."""
    tree = f"{TREE.as_posix()}/"
    return symbol.key in model.file_evidence or (
        bool(symbol.sources) and all(source.startswith(tree) for source in symbol.sources))


def evidence_layouts(link):
    """The layouts of the evidence locations of a stored link."""
    return {item["at"].split(":", 1)[0] for item in link.get("evidence", ())
            if isinstance(item, dict) and isinstance(item.get("at"), str) and ":" in item["at"]}


def link_layouts(link):
    """The layouts that a stored link states: those of its evidence locations
    and those of its `layouts`."""
    layouts = link.get("layouts")
    return evidence_layouts(link) | (
        {layout for layout in layouts if isinstance(layout, str)}
        if isinstance(layouts, list) else set())


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
    """Publish supported source texts, or removals, with an exact-file journal.

    A caller's publication keeps the journal through subsequent graph sync.
    A standalone write completes its file phase before removing its journal.
    """
    from kb import publication
    with publication.transaction(root, changes) as change:
        if change is not None:
            change.write(changes)


# Rendering -----------------------------------------------------------------


def render(kind, document):
    """The canonical text of an entity file of a kind."""
    lines = []
    _table(lines, (), document, _render_schema(kind), None)
    return "\n".join(lines) + "\n"


def render_batch(operations):
    """A primary writer batch without executing or promoting its operations."""
    lines = []
    keys = Table((("step", Array(STEP)),))
    operation = Table(_text("cmd", "ref") + (("keys", keys),))
    table = Table((("op", Array(operation)),))
    _table(lines, (), {"op": operations}, table, None)
    return "\n".join(lines) + "\n"


def _empty(value):
    if type(value) in (str, list, dict, tuple):
        return not value
    if type(value) in (bool, int, float):
        return False
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


_NATIVE_IS_TABLE = _is_table


def _partition(order, specs):
    if (_is_table is not _NATIVE_IS_TABLE or Table is not _NATIVE_TABLE
            or Array is not _NATIVE_ARRAY or Named is not _NATIVE_NAMED
            or Table.inline is not _NATIVE_INLINE
            or Table.__getattribute__ is not object.__getattribute__):
        return None
    plain, nested = [], []
    for key in order:
        spec = specs[key]
        kind = type(spec)
        if kind is Table:
            if type(spec.inline) is not bool:
                return None
            is_table = not spec.inline
        elif kind in (Array, Named):
            is_table = True
        elif kind is str or spec is None:
            is_table = False
        else:
            return None
        (nested if is_table else plain).append(key)
    return plain, nested


def _table(lines, path, document, table, header):
    present = {key: value for key, value in document.items() if not _empty(value)}
    program = _table_program(table, present)
    if program is None:
        order = table.order(present)
        specs = {key: table.spec(key) or _infer(present[key]) for key in order}
    else:
        order = [key for key, _ in program]
        specs = {key: spec or _infer(present[key]) for key, spec in program}
    partition = _partition(order, specs)
    if partition is None:
        plain = [key for key in order if not _is_table(specs[key])]
        nested = [key for key in order if _is_table(specs[key])]
    else:
        plain, nested = partition
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


_NATIVE_TABLE_RENDERER = _table


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
    if type(name) is str and len(name) <= 128 and BARE_KEY is _NATIVE_BARE_KEY:
        return name if _bare_key(name) else f'"{escape(name)}"'
    return name if BARE_KEY.fullmatch(name) else f'"{escape(name)}"'


_NATIVE_BARE_KEY = BARE_KEY


@lru_cache(maxsize=512)
def _bare_key(name):
    return _NATIVE_BARE_KEY.fullmatch(name) is not None


def escape(text):
    if type(text) is str and ESCAPABLE.search(text) is None:
        return text
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
    if (type(text) is str and type(escaped) is str
            and type(prefix) is str and type(suffix) is str
            and len(escaped) <= 1024 and len(prefix) <= 64 and len(suffix) <= 64
            and type(WIDTH) is int and 1 <= WIDTH <= 256
            and _breaks is _NATIVE_BREAKS and _wrap_lines is _NATIVE_WRAP_LINES):
        return list(_string_program(escaped, prefix, suffix, WIDTH))
    return _wrap_lines(escaped, prefix, suffix, WIDTH)


@lru_cache(maxsize=2048)
def _string_program(escaped, prefix, suffix, width):
    return tuple(_wrap_lines(escaped, prefix, suffix, width))


def _wrap_lines(escaped, prefix, suffix, limit):
    close = '"""' + suffix
    words = escaped.split(" ")
    lines, current = [], [words[0]]
    current_width = len(words[0])
    for index in range(1, len(words)):
        word = words[index]
        width = current_width + 1 + len(word)
        if width + 2 > limit and _breaks(current[-1], word):
            lines.append(current)
            current = [word]
            current_width = len(word)
        else:
            current.append(word)
            current_width = width
    if len(" ".join(current)) + len(close) > limit:
        for cut in range(len(current) - 1, 0, -1):
            head, tail = current[:cut], current[cut:]
            if _breaks(head[-1], tail[0]) and len(" ".join(tail)) + len(close) <= limit:
                lines.append(head)
                current = tail
                break
    lines.append(current)
    body = [" ".join(line) + " \\" for line in lines[:-1]] + [" ".join(lines[-1]) + close]
    return [f'{prefix}"""'] + body


def _breaks(left, right):
    """A line may end between two words that one space separates."""
    return bool(left) and bool(right)


_NATIVE_BREAKS, _NATIVE_WRAP_LINES = _breaks, _wrap_lines


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
