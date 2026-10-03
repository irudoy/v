"""The model checks (tools/kb/SPEC.md, section 13).

Each check returns `Issue` records; `kb check` prints one line per issue with
the file, the subject, and the message. Adapters report the issues they find
while reading a registry under the check that owns them.
"""

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import re

from kb import match, names, repo, store, vocab
from kb.model import MEANING_REF, SYMBOL_REF, Issue, SymbolKey
from kb.targets import CANONICAL

ROM = ("fn", "tbl", "axis", "const", "hook", "did", "dtc")
SPACE = {**{kind: "rom" for kind in ROM}, "ram": "ram", "reg": "io"}
LEVEL_KEYS = ("level", "contract_level", "scale_level")
VOCABULARY = {
    "access": vocab.TBL_ACCESS,
    "storage": vocab.STORAGE,
}
UNRESOLVED_KEYS = ("method", "target", "count", "l0")
L0_DIGEST = re.compile(r"[0-9a-f]{16}")


def _sources(meaning):
    return ";".join(sorted(meaning.sources)) or "model"


def _file(src):
    return src.startswith(f"{store.TREE.as_posix()}/")


def _from_files(sources):
    """Whether an entity file of `kb/` states the fact. The facts of an
    unconverted registry join the checks of stage 3 with its conversion."""
    return any(_file(src) for src in sources)


def _owned(model, symbol):
    """Whether the files own a symbol: only files state it, or a file entry
    states its evidence. A file entry that only names the symbol of a registry
    joins its meaning, and the registry keeps the symbol's evidence."""
    return symbol.key in model.file_evidence or (
        bool(symbol.sources) and all(_file(src) for src in symbol.sources))


def _files(sources):
    return ";".join(sorted(src for src in sources if src.startswith(f"{store.TREE.as_posix()}/")))


def _subject(meaning):
    if meaning.name:
        return meaning.key
    symbol = min(meaning.symbols.values(), key=lambda item: item.key, default=None)
    return symbol.key.key if symbol else f"?/{meaning.kind}"


def _evidence_issues(items, path, subject, check_required):
    for item in items:
        kind = item.get("kind")
        if kind not in vocab.EVIDENCE_KINDS:
            yield Issue("schema", path, subject, f"evidence kind {kind!r}")
            continue
        for key, value in item.items():
            if key == "legacy":
                continue
            if key not in vocab.EVIDENCE_KEYS:
                yield Issue("schema", path, subject, f"evidence key {key!r}")
        if item.get("supports") not in (None, *vocab.SUPPORTS):
            yield Issue("schema", path, subject, f"evidence supports {item['supports']!r}")
        if item.get("relies") not in (None, *vocab.RELIES):
            yield Issue("schema", path, subject, f"evidence relies {item['relies']!r}")
        if item.get("mode") not in (None, *vocab.INDIRECT_MODES):
            yield Issue("schema", path, subject, f"evidence mode {item['mode']!r}")
        if check_required and "legacy" not in item:
            required, _ = vocab.EVIDENCE_KINDS[kind]
            absent = [key for key in required if key not in item]
            if absent:
                yield Issue("schema", path, subject, f"{kind} evidence lacks {', '.join(absent)}")


def _key_issues(props, kind, path, subject, quantities):
    """Levels and vocabulary values of the keys of a meaning or of the
    overrides of a symbol."""
    for key in LEVEL_KEYS:
        if props.get(key) not in (None, *vocab.LEVELS):
            yield Issue("schema", path, subject, f"{key} {props[key]!r}")
    for key, allowed in VOCABULARY.items():
        if props.get(key) not in (None, *allowed):
            yield Issue("schema", path, subject, f"{key} {props[key]!r}")
    if kind in ("ram", "reg") and "width" in props:
        width = props["width"]
        if type(width) is not int or width not in (8, 16, 32):
            yield Issue("schema", path, subject,
                        f"width {width!r} of a {kind} must be 8, 16, or 32 bits")
    if kind == "axis" and props.get("quantity") not in (None, *quantities):
        yield Issue("schema", path, subject, f"quantity {props['quantity']!r} outside [vocab] "
                    "quantity of tools/kb/config.toml")


def _bit_issues(bits, width, path, subject):
    """Named bits of a bit field: a number below the access width in bits, a
    name, numbers and names that no other bit of the list repeats, a level
    from the vocabulary, and evidence items of section 7.6."""
    if not isinstance(bits, list) or not all(isinstance(bit, dict) for bit in bits):
        yield Issue("schema", path, subject, "bit is no array of tables")
        return
    numbers = Counter(bit.get("bit") for bit in bits)
    named = Counter(bit.get("name") for bit in bits)
    for bit in bits:
        number, name = bit.get("bit"), bit.get("name")
        where = f"{subject} bit {name}"
        if isinstance(number, bool) or not isinstance(number, int) or not 0 <= number < width:
            yield Issue("schema", path, where, f"bit {number!r} outside 0 to {width - 1}")
        elif numbers[number] > 1:
            yield Issue("schema", path, where, f"{numbers[number]} bits name bit {number}")
        if not isinstance(name, str) or not vocab.SEMANTIC_NAME.fullmatch(name):
            yield Issue("schema", path, where, f"bit name {name!r}")
        elif named[name] > 1:
            yield Issue("schema", path, where, f"{named[name]} bits share the name")
        if bit.get("level") not in (None, *vocab.LEVELS):
            yield Issue("schema", path, where, f"level {bit['level']!r}")
        yield from _evidence_issues(bit.get("evidence", ()), path, where, True)


def _width(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 8


def schema(model):
    issues = [issue for issue in model.issues if issue.check == "schema"]
    quantities = tuple(model.config.get("vocab", {}).get("quantity", ()))
    for meaning in model.meanings:
        path, subject, props = _sources(meaning), _subject(meaning), meaning.props
        issues.extend(_key_issues(props, meaning.kind, path, subject, quantities))
        role = props.get("role")
        roles = {"fn": vocab.FN_ROLES, "tbl": vocab.TBL_ROLES}.get(meaning.kind)
        if role is not None and (roles is None or role not in roles):
            issues.append(Issue("schema", path, subject, f"role {role!r} of a {meaning.kind}"))
        if "bit" in props:
            issues.extend(_bit_issues(props["bit"], _width(props.get("width")), path, subject))
        for symbol in meaning.symbols.values():
            issues.extend(_key_issues(symbol.props, meaning.kind, path, symbol.key.key,
                                      quantities))
            issues.extend(_evidence_issues(symbol.evidence, path, symbol.key.key, True))
            if "bit" in symbol.props:
                issues.extend(_bit_issues(symbol.props["bit"], _width(symbol.value("width")),
                                          path, symbol.key.key))
        for binding in meaning.tables.get("diagnostic", ()):
            if binding.get("level") not in (None, *vocab.LEVELS):
                issues.append(Issue("schema", path, subject,
                                    f"diagnostic {binding['id']} level {binding['level']!r}"))
            issues.extend(_evidence_issues(binding.get("evidence", ()), path,
                                           f"{subject} diagnostic {binding['id']}", True))
        for link in meaning.links:
            if link.type not in vocab.LINK_TYPES:
                issues.append(Issue("schema", path, subject, f"link type {link.type!r}"))
            for key in ("relies", "reverse_relies"):
                if link.props.get(key) not in (None, *vocab.RELIES):
                    issues.append(Issue("schema", path, subject, f"link {key} {link.props[key]!r}"))
            if link.type == "depends" and not link.roles:
                issues.append(Issue("schema", path, subject, "a depends link without role"))
        for layout, status in sorted(meaning.statuses.items()):
            if _from_files(status.sources):
                issues.extend(_evidence_issues(status.evidence, _files(status.sources),
                                               _status_subject(meaning, layout), True))
    for (kind, _), entity in sorted(model.entities.items()):
        path = ";".join(sorted(entity.sources))
        for key, allowed in vocab.ENTITY_VOCABULARY.get(kind, {}).items():
            if entity.props.get(key) not in (None, *allowed):
                issues.append(Issue("schema", path, entity.key, f"{key} {entity.props[key]!r}"))
    return issues


def canonical(model):
    """Every entity file equals the canonical rendering of its parse."""
    return store.canonical(model.root, model.overlay)


def names_check(model):
    issues = []
    semantic = defaultdict(list)
    for meaning in model.meanings:
        if meaning.semantic:
            semantic[(meaning.kind, meaning.name)].append(meaning)
            if not vocab.SEMANTIC_NAME.fullmatch(meaning.name) or not 3 <= len(meaning.name) <= 48:
                issues.append(Issue("names", _sources(meaning), meaning.key,
                                    "a semantic name has 3 to 48 characters of "
                                    "[a-z][a-z0-9]*(_[a-z0-9]+)*"))
    for (kind, name), found in sorted(semantic.items()):
        if len(found) > 1:
            where = "; ".join(sorted(_sources(meaning) for meaning in found))
            issues.append(Issue("names", where, f"{name}/{kind}",
                                f"{len(found)} meanings of kind {kind} share the name"))
    rows = model.names
    by_name = Counter(row.name for row in rows)
    by_key = Counter(row.key for row in rows)
    semantic_names = {name for _, name in semantic}
    for row in rows:
        where = names.PATH.as_posix()
        subject = f"{row.layout}-{row.address:08x}/{row.kind}"
        if not vocab.GENERATED_NAME.fullmatch(row.name):
            issues.append(Issue("names", where, subject, f"generated name {row.name!r}"))
        if by_name[row.name] > 1:
            issues.append(Issue("names", where, subject, f"generated name {row.name} repeats"))
        if by_key[row.key] > 1:
            issues.append(Issue("names", where, subject, "two rows for one symbol"))
        if row.name in semantic_names:
            issues.append(Issue("names", where, subject, f"{row.name} is a semantic name"))
        if row.layout not in model.layouts or row.kind not in vocab.MEANING_KINDS:
            issues.append(Issue("names", where, subject, "unknown layout or kind"))
    issues.extend(_file_names(model, by_name, by_key, semantic_names))
    lacking = names.missing(model, rows)
    if lacking:
        sample = ", ".join(key.key for key in lacking[:3])
        issues.append(Issue("names", names.PATH.as_posix(), f"{len(lacking)} symbols",
                            f"no generated name, among them {sample}; run `uv run kb sync`"))
    return issues


def _file_names(model, by_name, by_key, semantic_names):
    """The generated names that files give symbols share the rules of the rows
    of `kb/names.csv`, and a file carries the name of its meaning."""
    issues = []
    files = defaultdict(list)
    for key, (name, _, src) in sorted(model.file_names.items()):
        subject = key.key
        if (key.layout, key.kind, key.address) in by_key:
            issues.append(Issue("names", src, subject,
                                f"the symbol has a row of {names.PATH.as_posix()} too"))
        if not name:
            continue
        files[name].append(src)
        if not vocab.GENERATED_NAME.fullmatch(name):
            issues.append(Issue("names", src, subject, f"generated name {name!r}"))
        if name in semantic_names:
            issues.append(Issue("names", src, subject, f"{name} is a semantic name"))
        if by_name.get(name):
            issues.append(Issue("names", src, subject,
                                f"generated name {name} is a row of {names.PATH.as_posix()}"))
    for name, srcs in sorted(files.items()):
        if len(srcs) > 1:
            issues.append(Issue("names", ";".join(sorted(srcs)), name,
                                f"generated name {name} repeats"))
    held = defaultdict(list)
    for (kind, name), (meaning, src) in sorted(model.files.items()):
        if meaning is None:
            continue
        held[id(meaning)].append(src)
        if meaning.name != name:
            issues.append(Issue("names", src, f"{name}/{kind}",
                                f"the meaning is {meaning.key}; a file carries the name of "
                                "its meaning"))
    for srcs in held.values():
        if len(srcs) > 1:
            issues.append(Issue("names", ";".join(srcs), f"{len(srcs)} files",
                                "the files hold one meaning; merge them"))
    return issues


def references(model):
    issues = [issue for issue in model.issues if issue.check == "references"]
    known = set(model.symbols)
    for meaning in model.meanings:
        for symbol in meaning.symbols.values():
            for item in symbol.evidence:
                target = item.get("to")
                if isinstance(target, SymbolKey) and target not in known:
                    issues.append(Issue("references", _sources(meaning), symbol.key.key,
                                        f"evidence names {target.key}, which no registry holds"))
    return issues


def symbols(model):
    issues = [issue for issue in model.issues if issue.check == "symbols"]
    for key, symbol in sorted(model.symbols.items()):
        path = ";".join(sorted(symbol.sources))
        mcu = model.spaces[model.layouts[key.layout].mcu]
        start, end = mcu[SPACE[key.kind]]
        if not start <= key.address < end:
            issues.append(Issue("symbols", path, key.key,
                                f"the address lies outside the {SPACE[key.kind]} space of "
                                f"{model.layouts[key.layout].mcu}"))
        if key.kind == "fn" and key.address not in model.functions[key.layout]:
            issues.append(Issue("symbols", path, key.key,
                                f"no function entry of l0/{key.layout}/funcs.csv"))
    return issues


def _item(item):
    where = item.get("at") or item.get("to")
    if isinstance(where, SymbolKey):
        where = where.key
    return f"{item.get('kind')} evidence" + (f" at {where}" if where else "")


def _bit_evidence(meaning):
    """(path, subject, symbol, item) of each evidence item of the named bits
    of a meaning and of the bits that its symbols override; the symbol is
    that of the meaning on the layout of the item's `at`, or None."""
    owners = [(_subject(meaning), meaning.props.get("bit"))]
    owners += [(symbol.key.key, symbol.props.get("bit"))
               for _, symbol in sorted(meaning.symbols.items())]
    for subject, bits in owners:
        for bit in bits if isinstance(bits, list) else ():
            if not isinstance(bit, dict):
                continue
            for item in bit.get("evidence", ()):
                at = match.location(item.get("at"))
                yield (_sources(meaning), f"{subject} bit {bit.get('name')}",
                       meaning.symbols.get(at[0]) if at else None, item)


def _bits(model):
    """Each typed evidence item of a named bit whose kind L0 decides holds
    for the symbol of the meaning on the layout of its `at`."""
    issues = []
    for meaning in model.meanings:
        for path, subject, symbol, item in _bit_evidence(meaning):
            if "legacy" in item:
                continue
            if symbol is None:
                issues.append(Issue("homology", path, subject,
                                    f"{_item(item)}: `at` lies on no layout of a symbol of the "
                                    "meaning"))
                continue
            if item.get("kind") == "rom-bytes":
                continue
            failure = match.verify(model, symbol, item)
            if failure:
                issues.append(Issue("homology", path, subject, f"{_item(item)}: {failure}"))
    return issues


def _explicit_terminal(item):
    """Typed ledger terminals whose verification covers every supported claim."""
    return item.get("kind") in ("test", "l0-context") or (
        item.get("kind") == "indirect" and item.get("mode") == "base")


def homology(model):
    """File-owned symbols reach an anchor through verified identity or homology
    evidence (section 7.3). Every typed base, test, and context item of a symbol holds,
    including ledger-owned symbols; other ledger items retain their scope.
    Typed evidence of a named bit holds for the symbol of its layout."""
    issues = _bits(model)
    keys = sorted(key for key, symbol in model.symbols.items() if _owned(model, symbol))
    owned = set(keys)
    ranks = match.grounded(model, keys) if keys else {}
    for key, symbol in sorted(model.symbols.items()):
        path = _files(symbol.sources) if key in owned else ";".join(sorted(symbol.sources))
        for item in symbol.evidence:
            supports = item.get("supports", "identity")
            if item.get("kind") == "rom-bytes" or "legacy" in item:
                continue
            explicit = _explicit_terminal(item)
            if not explicit and (key not in owned or supports not in ("identity", "homology")):
                continue
            if (key in owned and supports == "homology"
                    and item.get("kind") not in match.HOMOLOGY_KINDS):
                issues.append(Issue("homology", path, key.key,
                                    f"{_item(item)} supports no homology"))
                if not explicit:
                    continue
            failure = match.verify(model, symbol, item)
            if failure:
                issues.append(Issue("homology", path, key.key, f"{_item(item)}: {failure}"))
        if key in owned and ranks[key][0] < match.CANDIDATE:
            issues.append(Issue("homology", path, key.key,
                                "neither an anchor nor homologous to one: no identity evidence "
                                "of its layout grounds it, and no verified homology evidence "
                                "reaches an anchor"))
    return issues


def links(model):
    issues = []
    for link in model.links:
        owners, targets = vocab.LINK_TYPES.get(link.type, ((), ()))
        if link.owner.kind not in owners or link.to.kind not in targets:
            issues.append(Issue(
                "links", ";".join(sorted(link.sources)), _subject(link.owner),
                f"{link.type} link from a {link.owner.kind} to {_subject(link.to)}; "
                f"the type joins {'/'.join(owners)} to {'/'.join(targets)}"))
        if link.type == "selector" and link.to.kind == "fn" and link.slot is not None:
            issues.append(Issue(
                "links", ";".join(sorted(link.sources)), _subject(link.owner),
                "a function-result selector has no bit or axis slot"))
    return issues


def _claimed(link):
    """The layouts where both ends of a link have symbols, within `layouts`."""
    allowed = link.props.get("layouts")
    return [layout for layout in sorted(set(link.owner.symbols) & set(link.to.symbols))
            if not allowed or layout in allowed]


def _hook_words(model, path, symbol, to, offset):
    props = {**symbol.meaning.props, **symbol.props}
    width = int(props.get("width") or 32) // 8
    expected = (to.address + offset) & ((1 << 8 * width) - 1)
    for rom, data in match.images(model, symbol.layout, symbol.props.get("images")):
        word = int.from_bytes(data[symbol.address:symbol.address + width], "big")
        if word != expected:
            shown = f"{to.key.key}" + (f" + {offset}" if offset else "")
            yield Issue("image-bytes", path, symbol.key.key,
                        f"{rom} holds {word:0{2 * width}x} at {symbol.address:08x}; the target "
                        f"{shown} is {expected:0{2 * width}x}")


def _did_sources(path, symbol, to, offset):
    tables = [item for item in symbol.evidence if item.get("kind") == "did-table"]
    if not tables:
        yield Issue("image-bytes", path, symbol.key.key,
                    f"the source {to.key.key} claims {symbol.layout}, where no did-table "
                    "evidence states the entry")
        return
    words = str(tables[0].get("value", "")).split()
    expected = f"{to.address:08x}"
    if offset is None:
        found = expected in words
    else:
        found = offset < len(words) and words[offset] == expected
    if not found:
        place = "" if offset is None else f" at position {offset}"
        yield Issue("image-bytes", path, symbol.key.key,
                    f"the entry {' '.join(words)} lacks the source {to.key.key}{place}")


def image_bytes(model):
    """Hook target words, DID table entries and the sources they point at, and
    every typed `rom-bytes` value agree with every image of the layout that
    the symbol applies to (section 13; the storage and dimensions of the other
    ROM symbols join at stage 8)."""
    issues = []
    for meaning in model.meanings:
        path = _sources(meaning)
        for link in meaning.links:
            if link.owner is not meaning or link.type not in ("target", "source"):
                continue
            for layout in _claimed(link):
                symbol, to = meaning.symbols[layout], link.to.symbols[layout]
                if link.type == "target" and meaning.kind == "hook":
                    issues.extend(_hook_words(model, path, symbol, to, link.offset or 0))
                elif link.type == "source" and meaning.kind == "did":
                    issues.extend(_did_sources(path, symbol, to, link.offset))
        for symbol in meaning.symbols.values():
            for item in symbol.evidence:
                if item.get("kind") not in ("rom-bytes", "did-table") or "legacy" in item:
                    continue
                failure = match.verify(model, symbol, item)
                if failure:
                    issues.append(Issue("image-bytes", path, symbol.key.key,
                                        f"{_item(item)}: {failure}"))
        for path, subject, symbol, item in _bit_evidence(meaning):
            if item.get("kind") != "rom-bytes" or "legacy" in item or symbol is None:
                continue
            failure = match.verify(model, symbol, item)
            if failure:
                issues.append(Issue("image-bytes", path, subject, f"{_item(item)}: {failure}"))
    return issues


def _status_subject(meaning, layout):
    return f"{_subject(meaning)} on {layout}"


def statuses(model):
    """`absent` carries evidence, `unresolved` carries the method, the target,
    the count, and the L0 digest of its search (section 7.4), and each `l0`
    and `rom-bytes` evidence item holds on the L0 and the images of the
    status's layout, for the statuses that files state."""
    issues = []
    for meaning in model.meanings:
        for layout, status in sorted(meaning.statuses.items()):
            if not _from_files(status.sources):
                continue
            path, subject = _files(status.sources), _status_subject(meaning, layout)
            if status.state == "absent" and not status.evidence:
                issues.append(Issue("statuses", path, subject, "an absent status without evidence"))
            for item in status.evidence:
                failure = match.verify_status(model, layout, item)
                if failure:
                    issues.append(Issue("statuses", path, subject, f"{_item(item)}: {failure}"))
            if status.state != "unresolved":
                continue
            props = status.props
            lacking = [key for key in UNRESOLVED_KEYS if props.get(key) in (None, "")]
            if lacking:
                issues.append(Issue("statuses", path, subject,
                                    f"an unresolved status without {', '.join(lacking)}"))
                continue
            if props["method"] not in vocab.EVIDENCE_KINDS:
                issues.append(Issue("statuses", path, subject,
                                    f"method {props['method']!r} is no evidence kind"))
            count = props["count"]
            if isinstance(count, bool) or not isinstance(count, int) or count < 0 or count == 1:
                issues.append(Issue("statuses", path, subject,
                                    f"count {count!r}; a search states 0 or more than 1 match"))
            if not L0_DIGEST.fullmatch(str(props["l0"])):
                issues.append(Issue("statuses", path, subject,
                                    f"l0 {props['l0']!r} is not 16 hexadecimal digits"))
            target = str(props["target"])
            if not (match.location(target) or SYMBOL_REF.fullmatch(target)
                    or MEANING_REF.fullmatch(target)):
                issues.append(Issue("statuses", path, subject,
                                    f"target {target!r} is neither a location nor a reference"))
    return issues


def stale(model):
    """The `unresolved` statuses of files whose search predates the L0 of
    their layout; staleness is reported and does not fail."""
    notes, digests = [], {}
    for meaning in model.meanings:
        for layout, status in sorted(meaning.statuses.items()):
            recorded = status.props.get("l0")
            if status.state != "unresolved" or not recorded or not _from_files(status.sources):
                continue
            if layout not in digests:
                digests[layout] = match.l0_digest(layout, model.root)
            if recorded != digests[layout]:
                notes.append(Issue(
                    "statuses", _files(status.sources), _status_subject(meaning, layout),
                    f"the search ran on L0 {recorded}, and the L0 of {layout} is "
                    f"{digests[layout]}; `uv run kb unresolved {meaning.key} --layout {layout}` "
                    "repeats it"))
    return notes


def writers(model):
    """Each store of a `ram` or `reg` symbol that aligns on the layout of
    another symbol of its meaning aligns with a store of that symbol (the
    writer gate); `[writers] review` of `tools/kb/config.toml` lists the
    contradictions that await review."""
    review = set(model.config.get("writers", {}).get("review", ()))
    issues, seen = [], set()
    for found in match.writers(model):
        meaning, symbol = found.meaning, found.symbol
        subject = f"{meaning.key}/{symbol.layout}" if meaning.name else symbol.key.key
        entry = f"{subject} {found.site}"
        seen.add(entry)
        if entry not in review:
            issues.append(Issue("writers", ";".join(sorted(symbol.sources)), subject,
                                f"{found.message}; review the binding, or list `{entry}` in "
                                f"[writers] review of {repo.CONFIG.as_posix()}"))
    for entry in sorted(review - seen):
        issues.append(Issue("writers", repo.CONFIG.as_posix(), entry,
                            "the contradiction under review no longer reproduces; remove the "
                            "entry"))
    return issues


def _field_targets(model):
    """{field key: [(layout, target)]}: the targets of the features that
    require each field."""
    by_feature = defaultdict(list)
    for (feature, layout), target in sorted(model.targets.items()):
        by_feature[feature].append((layout, target))
    found = defaultdict(list)
    for (kind, slug), entity in sorted(model.entities.items()):
        if kind != "feature":
            continue
        for ref in entity.refs.get("requires", ()):
            if isinstance(ref, tuple) and ref[0] == "field":
                found[ref] += by_feature[slug]
    return found


def _source_symbol(model, entity):
    """The `7mfk` `ram` or `reg` symbol that the source of an `ecu_ram` field
    names, or None."""
    keys = entity.refs.get("source", ())
    if (len(keys) == 1 and isinstance(keys[0], SymbolKey) and keys[0].layout == CANONICAL
            and keys[0].kind in ("ram", "reg")):
        return model.symbols.get(keys[0])
    return None


def _reads(model, entity, targets):
    """[(layout, symbol)] that an `ecu_ram` field reads: its source on `7mfk`,
    and on each other layout that a feature requiring it targets the symbol
    that fills the role of the field in the target, or else the symbol of the
    source meaning, or None."""
    source = _source_symbol(model, entity)
    found = {CANONICAL: source}
    for layout, target in targets:
        if layout == CANONICAL:
            continue
        role = target.props.get("roles", {}).get(entity.slug)
        symbol = model.symbols.get(role.get("symbol")) if isinstance(role, dict) else None
        if symbol is None and source is not None and source.meaning is not None:
            symbol = source.meaning.symbols.get(layout)
        if found.get(layout) is None:
            found[layout] = symbol
    return sorted(found.items())


def _allocation(model, entity):
    """(feature, allocation name, allocation entry or None) that the source
    `<feature>.<allocation>` of a field of an origin other than `ecu_ram`
    names on the `7mfk` target of the feature."""
    source = entity.props.get("source")
    feature, _, name = source.partition(".") if isinstance(source, str) else ("", "", "")
    target = model.targets.get((feature, CANONICAL))
    entry = (target.props.get("allocations", {}) if target else {}).get(name)
    return feature, name, entry if isinstance(entry, dict) else None


def _span(entry):
    """(start, end) of an allocation entry, or None."""
    try:
        start = int(entry["address"], 16)
    except (KeyError, TypeError, ValueError):
        return None
    width = entry.get("width")
    return (start, start + width) if isinstance(width, int) and width > 0 else None


def fields(model):
    """Every field names a source of its origin, and every `ecu_ram` field a
    signal and no scale; the source of an `ecu_ram` field is a `7mfk` `ram` or
    `reg` symbol outside the RAM that the features allocate, and the `signed`
    of the field agrees with each symbol that it reads where the symbol
    states it; on every layout that a feature requiring the field targets,
    the source meaning has a symbol or a status, or a symbol fills the role of
    the field in the target. The source of a field of another origin is the
    allocation named after the field without `_raw`, inside a region of its
    origin that the feature of the allocation owns (`origin_regions` of the
    stash), and the field carries its scale (section 7.9)."""
    issues = [issue for issue in model.issues if issue.check == "fields"]
    feature_ram = model.stash.get("feature_ram", ())
    regions = model.stash.get("origin_regions", {})
    targets = _field_targets(model)
    for (kind, slug), entity in sorted(model.entities.items()):
        if kind != "field":
            continue
        props = entity.props
        found = []
        if props.get("origin") != "ecu_ram":
            if not isinstance(props.get("scale"), str):
                found.append(f"a {props.get('origin')} field without scale")
            feature, name, entry = _allocation(model, entity)
            span = _span(entry) if entry is not None else None
            if name != slug.removesuffix("_raw") or entry is None:
                found.append(f"source {props.get('source')!r} is no allocation of a "
                             f"{CANONICAL} target named after the field")
            elif span is None or not any(
                    owner == feature and start <= span[0] and span[1] <= end
                    for start, end, owner in regions.get(props.get("origin"), ())):
                found.append(f"allocation {props['source']} lies outside the "
                             f"{props.get('origin')} regions of {feature}")
        else:
            if not any(ref in model.entities for ref in entity.refs.get("signal", ())
                       if isinstance(ref, tuple)):
                found.append("an ecu_ram field that names no signal")
            if "scale" in props:
                found.append(f"an ecu_ram field with scale {props['scale']!r}; the meaning of "
                             "its source holds the scale")
            source = _source_symbol(model, entity)
            if source is None:
                found.append(f"the source names no {CANONICAL} ram or reg symbol")
                issues += [Issue("fields", ";".join(sorted(entity.sources)), entity.key,
                                 message) for message in found]
                continue
            if any(start <= source.address < end for start, end, _ in feature_ram):
                found.append(f"the source {source.key.key} lies in the RAM that a feature "
                             "allocates")
            for layout, symbol in _reads(model, entity, targets[(kind, slug)]):
                if symbol is None:
                    if layout not in source.meaning.statuses:
                        found.append(f"on {layout} the source meaning has no symbol and no "
                                     "status, and no symbol fills the role of the field")
                    continue
                signed = symbol.value("signed")
                if isinstance(signed, bool) and signed != bool(props.get("signed")):
                    found.append(f"signed {bool(props.get('signed'))} disagrees with "
                                 f"{symbol.key.key}, whose signed is {signed}")
        issues += [Issue("fields", ";".join(sorted(entity.sources)), entity.key, message)
                   for message in found]
    return issues


def widths(model):
    """Every field width fits what the field reads: each symbol that an
    `ecu_ram` field reads (`_reads`) states a width of at least the bits of
    the field, and the allocation of a field of another origin holds at least
    its bytes. The access widths of the symbols in L0 join the check at stage
    8."""
    issues = []
    targets = _field_targets(model)
    for (kind, slug), entity in sorted(model.entities.items()):
        if kind != "field":
            continue
        path, width = ";".join(sorted(entity.sources)), entity.props.get("width")
        found = []
        if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
            found.append(f"width {width!r} is no positive number of bytes")
        elif entity.props.get("origin") != "ecu_ram":
            _, _, entry = _allocation(model, entity)
            span = _span(entry) if entry is not None else None
            if span is not None and width > span[1] - span[0]:
                found.append(f"the field of {width} bytes exceeds allocation "
                             f"{entity.props['source']}, which holds {span[1] - span[0]}")
        else:
            for layout, symbol in _reads(model, entity, targets[(kind, slug)]):
                if symbol is None:
                    continue
                bits = symbol.value("width")
                if isinstance(bits, bool) or not isinstance(bits, int):
                    found.append(f"{symbol.key.key} states no width")
                elif width * 8 > bits:
                    found.append(f"the field of {width} bytes exceeds {symbol.key.key}, whose "
                                 f"width is {bits} bits")
        issues += [Issue("widths", path, entity.key, message) for message in found]
    return issues


def levels_check(model):
    """The mandatory claim-level gate from stage 5."""
    from kb import levels
    return levels.check(model)


def ledgers_check(model):
    """Every owned ledger view selects facts that the compiled model holds."""
    if not model.stash.get("ledger_rows"):
        return []
    from kb import ledger_projection
    try:
        ledger_projection.render(model)
    except (repo.KbError, KeyError, TypeError, ValueError) as error:
        return [Issue("ledgers", "kb/", "ledger views", str(error))]
    return []


def _entity_ref(value, kind, model):
    return (isinstance(value, tuple) and len(value) == 2
            and all(isinstance(part, str) for part in value)
            and value[0] == kind and value in model.entities)


def _architecture_specs(value, model):
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return ['specs must be an array of paths']
    root = Path(getattr(model, 'root', repo.ROOT)).resolve()
    found = []
    for spec in value:
        path = Path(spec)
        try:
            target = (root / path).resolve()
            valid = (not path.is_absolute() and target.is_relative_to(root)
                     and target.is_file())
        except (OSError, ValueError):
            valid = False
        if not valid:
            found.append(f'specs names no repository file: {spec!r}')
    return found


def _architecture_metadata(entity, model, check):
    """The scalar metadata that the generated architecture view requires."""
    required = {'stage': ('title', 'summary', 'lane'),
                'block': ('title', 'summary'),
                'endpoint': ('title', 'summary', 'direction', 'peripheral'),
                'chain': ('title', 'summary', 'quantity')}[entity.kind]
    found = [f'{field} must be a nonempty string' for field in required
             if not isinstance(entity.props.get(field), str)
             or not entity.props[field].strip()]
    order = entity.props.get('order')
    if order is not None and (isinstance(order, bool) or not isinstance(order, int) or order < 1):
        found.append('order must be a positive integer')
    home = entity.props.get('home')
    if home is not None and (not isinstance(home, str) or home not in model.layouts):
        found.append('home must name a declared layout')
    if entity.kind == 'block' and entity.props.get('generic') is not None \
            and not isinstance(entity.props['generic'], bool):
        found.append('generic must be a boolean')
    found += _architecture_specs(entity.props.get('specs'), model)
    path = ';'.join(sorted(entity.sources))
    return [Issue(check, path, entity.key, message) for message in found]


def blocks(model):
    """Declared placements and endpoints resolve before a write is accepted."""
    issues = []
    for (kind, _), entity in model.entities.items():
        if kind in ('stage', 'block', 'endpoint'):
            issues += _architecture_metadata(entity, model, 'blocks')
    declared = {entity.key: entity for (kind, _), entity in model.entities.items()
                if kind == 'block'}
    for entity in declared.values():
        stage = entity.refs.get('stage', [])
        if len(stage) != 1 or not _entity_ref(stage[0], 'stage', model):
            issues.append(Issue('blocks', ';'.join(sorted(entity.sources)), entity.key,
                                'a block needs exactly one declared stage'))
    for meaning in model.meanings:
        block = meaning.props.get('block')
        if block is not None and (not isinstance(block, str) or block not in declared):
            issues.append(Issue('blocks', _sources(meaning), _subject(meaning),
                                f'block {block!r} is not a declared block'))
        home = meaning.symbols.get(meaning.home)
        reviewed = home.value('level') if home else meaning.props.get('level')
        if (meaning.kind == 'fn' and reviewed in ('code', 'silicon')
                and not block):
            issues.append(Issue('blocks', _sources(meaning), _subject(meaning),
                                'a reviewed function needs a block'))
    for (kind, _), entity in model.entities.items():
        if kind != 'endpoint':
            continue
        path = ';'.join(sorted(entity.sources))
        target = entity.refs.get('block', [])
        if len(target) != 1 or not _entity_ref(target[0], 'block', model):
            issues.append(Issue('blocks', path, entity.key, 'an endpoint needs one declared block'))
        members = entity.refs.get('registers', []) + entity.refs.get('functions', [])
        if not members:
            issues.append(Issue('blocks', path, entity.key, 'an endpoint needs registers or functions'))
        for field, kinds in (('registers', ('reg', 'ram')), ('functions', ('fn',))):
            if any(not isinstance(key, SymbolKey) or key not in model.symbols
                   or key.kind not in kinds for key in entity.refs.get(field, [])):
                issues.append(Issue('blocks', path, entity.key, f'{field} contain an invalid member'))
    return issues


def chains(model):
    """Ordered chain references, vocabulary, output, and acyclic flow.

    Arithmetic-only notes and the migration of prose conditions remain a
    separate stage-6 requirement. Connectivity never proves arithmetic.
    """
    issues = []
    for (kind, _), entity in model.entities.items():
        if kind != 'chain':
            continue
        issues += _architecture_metadata(entity, model, 'chains')
        path = ';'.join(sorted(entity.sources))
        home = entity.props.get('home', CANONICAL)
        output = entity.refs.get('output', [])
        if len(output) != 1 or not isinstance(output[0], SymbolKey):
            issues.append(Issue('chains', path, entity.key, 'a chain needs one symbol output'))
        if not entity.steps:
            issues.append(Issue('chains', path, entity.key, 'a chain needs ordered steps'))
        pairs, destinations, following = set(), set(), defaultdict(set)
        for index, step in enumerate(entity.steps, 1):
            subject = f'{entity.key} step {index}'
            if step.get('note') is not None and not isinstance(step['note'], str):
                issues.append(Issue('chains', path, subject, 'note must be a string'))
            issues += [Issue('chains', path, subject, message)
                       for message in _architecture_specs(step.get('specs'), model)]
            if step.get('effect') not in vocab.STEP_EFFECTS:
                issues.append(Issue('chains', path, subject, f'effect {step.get("effect")!r}'))
            if step.get('sign') not in vocab.STEP_SIGNS:
                issues.append(Issue('chains', path, subject, f'sign {step.get("sign")!r}'))
            via = step.get('via', [])
            if not isinstance(via, list):
                issues.append(Issue('chains', path, subject, 'via must be an ordered array'))
                via = []
            refs = [step.get('from'), step.get('to'), *via]
            valid = all(isinstance(key, SymbolKey) and key in model.symbols
                        and key.layout == home for key in refs)
            if not valid:
                issues.append(Issue('chains', path, subject, f'every reference needs a symbol on {home}'))
                continue
            if any(key.kind != 'fn' for key in via):
                issues.append(Issue('chains', path, subject, 'via must name functions'))
            first, second = refs[:2]
            pair = first, second
            if pair in pairs:
                issues.append(Issue('chains', path, subject, 'a source/destination pair is repeated'))
            pairs.add(pair)
            destinations.add(second)
            following[first].add(second)
        if (len(output) == 1 and isinstance(output[0], SymbolKey)
                and (output[0] not in destinations or output[0].layout != home)):
            issues.append(Issue('chains', path, entity.key, 'the output must be a step destination on the home layout'))
        reached, active = set(), set()

        def cyclic(key):
            if key in active:
                return True
            if key in reached:
                return False
            active.add(key)
            if any(cyclic(child) for child in following[key]):
                return True
            active.remove(key)
            reached.add(key)
            return False

        if any(cyclic(key) for key in list(following)):
            issues.append(Issue('chains', path, entity.key, 'steps form a cycle'))
    return issues


CHECKS = {
    "schema": schema,
    "canonical": canonical,
    "names": names_check,
    "references": references,
    "symbols": symbols,
    "homology": homology,
    "links": links,
    "widths": widths,
    "image-bytes": image_bytes,
    "statuses": statuses,
    "writers": writers,
    "fields": fields,
    "levels": levels_check,
    "ledgers": ledgers_check,
    'blocks': blocks,
    'chains': chains,
}

# Reports of a check that do not fail it.
NOTES = {
    "statuses": stale,
}


AUDIT_SECTIONS = ("disagreements", "names", "untyped", "levels", "chain-notes")
# The model issues that each section reports.
AUDIT_ISSUES = {"audit": "disagreements", "untyped": "untyped"}


def audit(model, sections=AUDIT_SECTIONS):
    """{section: issues} of the requested sections: disagreements of one fact
    between registries, other registry names of a named meaning, legacy
    evidence without the keys of its kind under the registry that states it,
    which the conversion of its registry types, and the levels of the claims
    (`kb.levels`)."""
    found = {section: set() for section in AUDIT_SECTIONS if section in sections}
    for issue in model.issues:
        section = AUDIT_ISSUES.get(issue.check)
        if section in found:
            found[section].add(issue)
    for meaning in model.meanings if "names" in found else ():
        others = defaultdict(set)
        for name, tier, src in meaning.other_names:
            if tier != "former":
                others[(name, tier)].add(src)
        for (name, tier), srcs in others.items():
            found["names"].add(Issue("audit", ";".join(sorted(srcs)), meaning.key,
                                     f"the {tier} name {name} names the same meaning"))
    if "levels" in found:
        # kb.levels reads the helpers of this module.
        from kb import levels

        found["levels"].update(levels.check(model))
    if 'chain-notes' in found:
        found['chain-notes'].update(chain_notes(model))
    return {section: sorted(issues) for section, issues in found.items()}


def chain_notes(model):
    """Notes awaiting arithmetic-only migration, without changing levels.

    The exact rejected text and the step binding enter each issue. A changed
    note or flow cannot reuse the held rejection in differential write checks.
    """
    from kb.arithmetic import Grammar

    grammar = Grammar(model.config)
    found = []
    for (kind, _), entity in model.entities.items():
        if kind != 'chain':
            continue
        for index, step in enumerate(entity.steps, 1):
            note = step.get('note')
            if note is None:
                continue
            failure = grammar.validate(note)
            if failure:
                binding = repr(tuple(step.get(field) for field in
                                     ('from', 'to', 'via', 'effect', 'sign')))
                digest = hashlib.sha256(binding.encode()).hexdigest()[:16]
                found.append(Issue('chain-notes', ';'.join(sorted(entity.sources)),
                                   f'{entity.key} step {index}',
                                   f'note {note!r}: {failure}; step binding {digest}'))
    return found
