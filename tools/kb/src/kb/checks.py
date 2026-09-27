"""The model checks (tools/kb/SPEC.md, section 13).

Each check returns `Issue` records; `kb check` prints one line per issue with
the file, the subject, and the message. Adapters report the issues they find
while reading a registry under the check that owns them.
"""

from collections import Counter, defaultdict
import re

from kb import match, names, repo, store, vocab
from kb.model import MEANING_REF, SYMBOL_REF, Issue, SymbolKey

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
    if kind == "axis" and props.get("quantity") not in (None, *quantities):
        yield Issue("schema", path, subject, f"quantity {props['quantity']!r} outside [vocab] "
                    "quantity of tools/kb/config.toml")


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
        for symbol in meaning.symbols.values():
            issues.extend(_key_issues(symbol.props, meaning.kind, path, symbol.key.key,
                                      quantities))
            issues.extend(_evidence_issues(symbol.evidence, path, symbol.key.key, True))
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


def homology(model):
    """Every symbol that the files own is an anchor or reaches one through
    verified homology evidence, and each of its typed identity and homology
    evidence items that L0 or the images decide holds (section 7.3)."""
    keys = sorted(key for key, symbol in model.symbols.items() if _owned(model, symbol))
    if not keys:
        return []
    ranks = match.grounded(model, keys)
    issues = []
    for key in keys:
        symbol = model.symbols[key]
        path = _files(symbol.sources)
        for item in symbol.evidence:
            supports = item.get("supports", "identity")
            if (supports not in ("identity", "homology") or item.get("kind") == "rom-bytes"
                    or "legacy" in item):
                continue
            if supports == "homology" and item.get("kind") not in match.HOMOLOGY_KINDS:
                issues.append(Issue("homology", path, key.key,
                                    f"{_item(item)} supports no homology"))
                continue
            failure = match.verify(model, symbol, item)
            if failure:
                issues.append(Issue("homology", path, key.key, f"{_item(item)}: {failure}"))
        if ranks[key][0] < match.CANDIDATE:
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


CHECKS = {
    "schema": schema,
    "canonical": canonical,
    "names": names_check,
    "references": references,
    "symbols": symbols,
    "homology": homology,
    "links": links,
    "image-bytes": image_bytes,
    "statuses": statuses,
    "writers": writers,
}

# Reports of a check that do not fail it.
NOTES = {
    "statuses": stale,
}


AUDIT_SECTIONS = ("disagreements", "names", "untyped", "unsplit")


def audit(model):
    """{section: issues}: disagreements of one fact between registries, other
    registry names of a named meaning, legacy evidence without the keys of its
    kind under the registry that states it, which the conversion of its
    registry types, and the scales of telemetry fields that the conversion
    cannot split into their meanings."""
    found = {section: set() for section in AUDIT_SECTIONS}
    for issue in model.issues:
        if issue.check in ("untyped", "unsplit"):
            found[issue.check].add(issue)
        elif issue.check == "audit":
            found["disagreements"].add(issue)
    for meaning in model.meanings:
        others = defaultdict(set)
        for name, tier, src in meaning.other_names:
            if tier != "former":
                others[(name, tier)].add(src)
        for (name, tier), srcs in others.items():
            found["names"].add(Issue("audit", ";".join(sorted(srcs)), meaning.key,
                                     f"the {tier} name {name} names the same meaning"))
    return {section: sorted(issues) for section, issues in found.items()}
