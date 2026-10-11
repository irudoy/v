"""Projections: the generated files of the repository (tools/kb/SPEC.md,
section 14).

`tools/kb/projections.toml` registers every generated file. A projection path
is a repository path, a pattern whose `*` stays inside one directory for the
files of one generator, or `<file>#<name>` for the section of a file between
`<!-- <name>:begin -->` and `<!-- <name>:end -->`. A generator `kb.<module>:<function>`
is a function of this package that renders the file or the section from the
repository root, and for a pattern returns {path: text} of its files; `kb
project` writes the projections of such generators whose stage the
transition has reached, and the `projections` check compares them with their
rendering and a pattern's tracked files with the files of its rendering. A projection of another generator keeps that generator
and the gate that compares it, and the check requires its files and the
repository paths of its command to exist. The path grammar is that of the
access guard `tools/kb/hook.py`, whose functions this module uses.

The owner of the facts of a registry of section 19 follows from its files: the
owner after conversion owns them once every tracked file that the registry
names is a projection of `kb` or a module that reads `kb`, or once `converted`
of `tools/kb/bench.toml` lists a registry whose conversion leaves no such file.
The `projections` check requires each row of section 19 to state one stage and
each entry of `converted` to name a row whose stage has started and whose files
do not convert it.
"""

import ast
from importlib import import_module
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib

from kb import adapters, repo, spec
from kb.repo import KbError

PATH = Path("tools/kb/projections.toml")
BENCH = Path("tools/kb/bench.toml")
HOOK = Path("tools/kb/hook.py")
KEYS = {"path", "generator", "stage", "inputs", "consumers", "read", "check"}
REQUIRED = KEYS - {"stage", "check"}
READ = ("guarded", "open")
# A tracked file whose first lines say this declares itself generated.
GENERATED = re.compile(r"(?i)generated (?:by|from)|do not edit|not survive the next run")
HEAD_LINES = 6


def load(root=repo.ROOT):
    return tomllib.loads((root / PATH).read_text(encoding="utf-8")).get("projection", [])


def stage(root=repo.ROOT):
    """The highest transition stage that has started."""
    return tomllib.loads((root / BENCH).read_text(encoding="utf-8"))["stage"]


def listed(root=repo.ROOT):
    """The registries of section 19 whose conversion `converted` of
    `bench.toml` records because it leaves no file that `kb` renders or that
    reads `kb`."""
    return tomllib.loads((root / BENCH).read_text(encoding="utf-8")).get("converted", [])


def _hook():
    """The access guard of this working tree."""
    found = importlib.util.spec_from_file_location(
        "kb_hook", Path(__file__).resolve().parents[2] / HOOK.name)
    module = importlib.util.module_from_spec(found)
    found.loader.exec_module(module)
    return module


hook = _hook()
split, matches, markers = hook.split, hook.matches, hook.markers


def tracked(root=repo.ROOT):
    result = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True,
                            check=True)
    return sorted(name for name in result.stdout.decode().split("\0") if name)


def section_span(text, name):
    """(start, stop) of the text between the markers of a section, or None."""
    begin, end = markers(name)
    start, stop = text.find(begin), text.find(end)
    if start < 0 or stop < start:
        return None
    return start + len(begin), stop


def rendered(entry):
    """Whether `kb` renders the projection."""
    return entry.get("generator", "").startswith("kb.")


def generator(entry):
    module, _, function = entry["generator"].partition(":")
    return getattr(import_module(module), function)


def renderings(root, entry):
    """{file: text} of a projection that `kb` renders as whole files."""
    result = generator(entry)(root)
    if isinstance(result, dict):
        return {Path(name).as_posix(): text for name, text in result.items()}
    return {split(entry["path"])[0]: result}


def current(root, entry):
    """The current content of a projection that `kb` renders."""
    file, section = split(entry["path"])
    text = (root / file).read_bytes().decode("utf-8")
    if section is None:
        return text
    span = section_span(text, section)
    return None if span is None else text[span[0]:span[1]]


def write(root=repo.ROOT, paths=(), check=False):
    """Render the projections of `kb` at the current stage, or those of
    `paths`; return [(path, changed)]. With `check`, write nothing and
    return whether each file differs from its rendering."""
    entries = [entry for entry in load(root)
               if rendered(entry) and entry.get("stage", 0) <= stage(root)]
    unknown = sorted(set(paths) - {entry["path"] for entry in entries})
    if unknown:
        raise KbError(f"no projection that kb renders at this stage: {', '.join(unknown)}",
                      code=2)
    done = []
    for entry in entries:
        if paths and entry["path"] not in paths:
            continue
        file, section = split(entry["path"])
        if section is None:
            changed = False
            for name, text in sorted(renderings(root, entry).items()):
                path = root / name
                if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                    if not check:
                        _replace(path, text)
                    changed = True
            done.append((entry["path"], changed))
            continue
        old = (root / file).read_bytes().decode("utf-8")
        span = section_span(old, section)
        if span is None:
            raise KbError(f"{file} has no markers {' '.join(markers(section))}", code=1)
        new = old[:span[0]] + generator(entry)(root) + old[span[1]:]
        if new != old and not check:
            _replace(root / file, new)
        done.append((entry["path"], new != old))
    return done


def _replace(path, text):
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(handle, "w", encoding="utf-8", newline="") as target:
        target.write(text)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def _paths(root, items, files):
    """Repository paths among `items` (entries with a slash) that match no
    tracked file or directory."""
    missing = []
    for item in items:
        if "/" not in item:
            continue
        pattern = item.rstrip("/")
        if any(matches(pattern, name) or name.startswith(pattern + "/") for name in files) \
                or (root / pattern).exists():
            continue
        missing.append(item)
    return missing


def _compare(root, entry, found):
    """Failure lines of the files of a projection that `kb` renders whole,
    whose tracked files are `found`."""
    fix = f"(fix: uv run kb project {entry['path']})"
    files = renderings(root, entry)
    failures = [f"{name}: matches {entry['path']} and is no file of its rendering "
                f"(fix: git rm {name})" for name in sorted(set(found) - set(files))]
    for name, text in sorted(files.items()):
        if not matches(split(entry["path"])[0], name):
            failures.append(f"{name}: lies outside the path of projection {entry['path']} "
                            f"(fix: {entry['generator']})")
        elif not (root / name).is_file():
            failures.append(f"{name}: missing {fix}")
        elif name not in found:
            failures.append(f"{name}: not tracked (fix: git add {name})")
        elif (root / name).read_bytes() != text.encode("utf-8"):
            failures.append(f"{name}: file: differs from its rendering {fix}")
    return failures


def check(root=repo.ROOT):
    """Failure lines of the `projections` check."""
    failures = []
    fix = f"(fix: edit {PATH.as_posix()})"
    files = tracked(root)
    now = stage(root)
    owners = {}
    try:
        entries = load(root)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return [f"{PATH.as_posix()}: {error}"]
    for index, entry in enumerate(entries):
        where = f"{PATH.as_posix()}: projection {entry.get('path', index)}"
        if set(entry) - KEYS or REQUIRED - set(entry):
            failures.append(f"{where}: keys {sorted(set(entry) - KEYS)} unknown, "
                            f"{sorted(REQUIRED - set(entry))} missing {fix}")
            continue
        if entry["read"] not in READ:
            failures.append(f"{where}: read {entry['read']!r} is none of {', '.join(READ)} {fix}")
        if "stage" in entry and not isinstance(entry["stage"], int):
            failures.append(f"{where}: stage {entry['stage']!r} is no stage number {fix}")
        file, section = split(entry["path"])
        found = [name for name in files if matches(file, name)]
        if not found:
            failures.append(f"{where}: path matches no tracked file {fix}")
        for name in found:
            if name in owners:
                failures.append(f"{where}: {name} is also a file of projection {owners[name]} "
                                f"{fix}")
            owners[name] = entry["path"]
        for key in ("inputs", "consumers"):
            for item in _paths(root, entry[key], files):
                failures.append(f"{where}: {key} {item} does not exist {fix}")
        if rendered(entry):
            try:
                render = generator(entry)
            except (ImportError, AttributeError, ValueError):
                failures.append(f"{where}: generator {entry['generator']} is no function of "
                                f"kb {fix}")
                continue
            if entry.get("stage", 0) > now or not found:
                continue
            if section is None:
                failures.extend(_compare(root, entry, found))
                continue
            text = current(root, entry)
            if text is None:
                failures.append(f"{file}: {section}: no markers {' '.join(markers(section))} "
                                f"(fix: add them and run uv run kb project {entry['path']})")
            elif text != render(root):
                failures.append(f"{file}: {section or 'file'}: differs from its rendering "
                                f"(fix: uv run kb project {entry['path']})")
        else:
            words = [word for word in entry["generator"].split() if "/" in word
                     and not word.startswith("-")]
            for item in _paths(root, words, files):
                failures.append(f"{where}: generator names {item}, which does not exist {fix}")
    trees = tuple(repo.config(root).get("guard", {}).get("trees", ()))
    for name in files:
        if name in owners or name.startswith(trees) or not (root / name).is_file() \
                or (root / name).is_symlink():
            continue
        try:
            with (root / name).open(encoding="utf-8") as source:
                head = "".join(source.readline() for _ in range(HEAD_LINES))
        except (UnicodeDecodeError, OSError):
            continue
        if GENERATED.search(head):
            failures.append(f"{name}: declares itself generated and no projection registers "
                            f"it {fix}")
    return failures + ownership(root)


# Generators ------------------------------------------------------------------


def active(root=repo.ROOT, now=None):
    """The tracked files of the projections that `kb` renders whole at stage
    `now`, by default the current one."""
    now = stage(root) if now is None else now
    files = tracked(root)
    found = set()
    for entry in load(root):
        file, section = split(entry["path"])
        if rendered(entry) and section is None and entry.get("stage", 0) <= now:
            found.update(name for name in files if matches(file, name))
    return found


def _stages(when):
    """The stages that a conversion cell of section 19 names."""
    return [int(number) for number in re.findall(r"(?<![\w`])\d+(?![\w`])", when)]


def _stage(when):
    """The stage of a conversion cell of section 19, or None for a registry
    that is not converted or is generated."""
    numbers = _stages(when)
    return numbers[0] if numbers else None


def patterns(row):
    """The path patterns of the tracked files that the first cell of a row of
    section 19 names, with `<name>` as `*`."""
    return [re.sub(r"<[^>]+>", "*", item) for item in re.findall(r"`([^`]+)`", row[0])
            if "/" in item]


def _imports_kb(path):
    """Whether a Python module imports the `kb` package."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False
    return any((isinstance(node, ast.Import)
                and any(alias.name.split(".")[0] == "kb" for alias in node.names))
               or (isinstance(node, ast.ImportFrom) and not node.level
                   and (node.module or "").split(".")[0] == "kb")
               for node in ast.walk(tree))


class Readers:
    """Whether a tracked file reads the entity files through the `kb` API
    while no adapter reads it: a Python module that imports `kb` and that no
    adapter of `adapters.ORDER` names among its inputs, which load on first
    use."""

    def __init__(self, root):
        self.root, self.read = root, None

    def __call__(self, name):
        if not name.endswith(".py") or not _imports_kb(self.root / name):
            return False
        if self.read is None:
            self.read = {path for adapter in adapters.ORDER for path in adapter.inputs(self.root)}
        return name not in self.read


def _named(row, files):
    """The tracked files (of `files`) that the first cell of a row names."""
    return {name for pattern in patterns(row) for name in files if matches(pattern, name)}


def _rendered(row, files, rendered_files, reader):
    """Whether the files of a row convert it: it names tracked files, and each
    is a projection that `kb` renders (`rendered_files`) or a module that
    reads the entity files through the `kb` API while no adapter reads it
    (`reader`)."""
    named = _named(row, files)
    return bool(named) and all(name in rendered_files or (reader is not None and reader(name))
                               for name in named)


def converted(row, now, files, rendered_files, reader=None, chosen=()):
    """Whether the owner after conversion owns the facts of a row of section
    19 at stage `now`, the highest stage that has started: a registry created
    in a stage owns its facts from that stage, and the owner after conversion
    owns those of a row whose stage has started once its files convert it or
    once `chosen`, the `converted` list of `bench.toml`, names its registry."""
    when = row[2]
    number = _stage(when)
    if number is None or number > now:
        return False
    if when.startswith("created in ") or spec.plain(row[0]) in chosen:
        return True
    return _rendered(row, files, rendered_files, reader)


def owners(root=repo.ROOT, now=None):
    """Registries whose owner after conversion owns their facts at stage
    `now`, with the owners, and the number of registries that own their facts
    until conversion by the stage that converts them."""
    now = stage(root) if now is None else now
    files, rendered_files, reader = tracked(root), active(root, now), Readers(root)
    chosen = listed(root)
    done, pending = [], {}
    for row in spec.table(spec.OWNERSHIP, root):
        number = _stage(row[2])
        if number is None:
            continue
        if converted(row, now, files, rendered_files, reader, chosen):
            done.append({"registry": spec.plain(row[0]), "owner": spec.plain(row[3]),
                         "stage": number})
        else:
            pending[number] = pending.get(number, 0) + 1
    return {"converted": done, "pending": pending}


def _owner(row, now, files, rendered_files, reader, chosen):
    """The owner of the facts of a registry of section 19 at stage `now`."""
    _, _, when, after, _ = row
    if _stage(when) is None or when.startswith("created in "):
        return after
    if converted(row, now, files, rendered_files, reader, chosen):
        return f"{after} since stage {when}"
    return f"the registry until stage {when}"


def ownership(root=repo.ROOT):
    """Failure lines of section 19 and of `converted` of `bench.toml`: a row
    states one stage, and an entry names the registry of a row with a stage
    that has started and whose files do not convert it."""
    now, rows = stage(root), spec.table(spec.OWNERSHIP, root)
    failures = [f"{spec.PATH.as_posix()}: section 19: {spec.plain(row[0])} states stages "
                f"{', '.join(map(str, _stages(row[2])))}; a row states one stage (fix: give "
                "each stage its row)" for row in rows if len(_stages(row[2])) > 1]
    chosen = listed(root)
    where, fix = f"{BENCH.as_posix()}: converted", f"(fix: edit {BENCH.as_posix()})"
    if not isinstance(chosen, list) or not all(isinstance(item, str) for item in chosen):
        return failures + [f"{where}: {chosen!r} is no list of registries {fix}"]
    by_registry = {spec.plain(row[0]): row for row in rows}
    files, rendered_files, reader = tracked(root), active(root, now), Readers(root)
    for item in chosen:
        row = by_registry.get(item)
        number = None if row is None else _stage(row[2])
        if number is None or row[2].startswith("created in "):
            failures.append(f"{where} {item}: names no row of section 19 that converts in a "
                            f"stage {fix}")
        elif number > now:
            failures.append(f"{where} {item}: its row converts in stage {number}, which has "
                            f"not started {fix}")
        elif _rendered(row, files, rendered_files, reader):
            failures.append(f"{where} {item}: its files convert it {fix}")
    return failures


def legacy(sources, root=repo.ROOT):
    """The rows of `kb/names.csv`: their number, the rows by the first stage
    that converts a registry of section 19 stating their symbol, the rows by
    the registries that state their symbol when none of them converts, and
    the rows that reserve the name of a symbol that no registry states.
    `sources` maps (layout, kind, address) of each symbol to the repository
    paths that state it; a path that no row names stands for itself."""
    from kb import names

    table = [(patterns(row), _stage(row[2]), spec.plain(row[0]))
             for row in spec.table(spec.OWNERSHIP, root) if not row[2].startswith("created in ")]
    counts = {"rows": 0, "leave": {}, "stay": {}, "reserved": 0}
    for entry in names.read(root):
        counts["rows"] += 1
        paths = sources.get(entry.key)
        if not paths:
            counts["reserved"] += 1
            continue
        numbers, holders = set(), set()
        for path in paths:
            found = next(((number, registry) for named, number, registry in table
                          if any(matches(pattern, path) for pattern in named)), None)
            if found is None:
                holders.add(path)
            elif found[0] is None:
                holders.add(found[1])
            else:
                numbers.add(found[0])
        if numbers:
            counts["leave"][min(numbers)] = counts["leave"].get(min(numbers), 0) + 1
        else:
            key = ", ".join(sorted(holders))
            counts["stay"][key] = counts["stay"].get(key, 0) + 1
    return counts


def agents(root=repo.ROOT):
    """The `kb` section of AGENTS.md: the knowledge access rules, the questions
    of the current stage with their commands, and the owner of each fact."""
    now = stage(root)
    names = {row["number"]: row["name"] for row in spec.stages(root)}
    bench = tomllib.loads((root / BENCH).read_text(encoding="utf-8"))
    lines = [
        "",
        "",
        "## Knowledge access",
        "",
        f"Generated by `uv run kb project AGENTS.md#kb` from `{spec.PATH.as_posix()}` and",
        f"`{BENCH.as_posix()}`; the transition is at stage {now}, {names.get(now, '?')}.",
        "",
        "- Start with `uv run kb brief`: the graph, the layouts, the stage, the",
        "  owners, and the open gaps. `uv run kb` answers what the repository knows",
        "  about the symbols, meanings, links, statuses, and evidence of every",
        "  layout, and the MCP server `kb` serves the same read commands as the",
        "  tools `kb_<command>`. Ask `kb` before searching the registries or reading",
        "  `l0/`.",
        "- The access guard `tools/kb/hook.py` denies reading, searching, and editing",
        "  `kb/` and `l0/`, reading the guarded projections, and editing the files",
        "  that `tools/kb/projections.toml` registers as generated; its reason names",
        "  the command to use. `uv run kb guard off --session <id>` disables it",
        "  for one root session; `on` enables it and `status` shows its saved override.",
        "  `KB_GUARD=off` in the hook environment is the fallback without an override.",
        "- The table below names the owner of each fact: a registry owns its facts",
        "  until the commit of its stage converts it. Change a fact in its owner,",
        "  then regenerate its projections.",
        "",
        "| Question | Command |",
        "|---|---|",
    ]
    lines.extend(f"| {item['question']} | `uv run {item['command']}` |"
                 for item in bench["question"] if item["stage"] <= now)
    files, rendered_files, reader = tracked(root), active(root, now), Readers(root)
    chosen = listed(root)
    lines.extend(["", f"| Registry | Facts | Owner at stage {now} |", "|---|---|---|"])
    lines.extend(f"| {row[0]} | {row[1]} | "
                 f"{_owner(row, now, files, rendered_files, reader, chosen)} |"
                 for row in spec.table(spec.OWNERSHIP, root))
    lines.append("")
    return "\n".join(lines) + "\n"
