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
"""

from importlib import import_module
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib

from kb import repo, spec
from kb.repo import KbError

PATH = Path("tools/kb/projections.toml")
BENCH = Path("tools/kb/bench.toml")
HOOK = Path("tools/kb/hook.py")
KEYS = {"path", "generator", "stage", "inputs", "consumers", "read"}
REQUIRED = KEYS - {"stage"}
READ = ("guarded", "open")
# A tracked file whose first lines say this declares itself generated.
GENERATED = re.compile(r"(?i)generated (?:by|from)|do not edit|not survive the next run")
HEAD_LINES = 6


def load(root=repo.ROOT):
    return tomllib.loads((root / PATH).read_text(encoding="utf-8")).get("projection", [])


def stage(root=repo.ROOT):
    return tomllib.loads((root / BENCH).read_text(encoding="utf-8"))["stage"]


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
    text = (root / file).read_text(encoding="utf-8")
    if section is None:
        return text
    span = section_span(text, section)
    return None if span is None else text[span[0]:span[1]]


def write(root=repo.ROOT, paths=()):
    """Render the projections of `kb` at the current stage, or those of
    `paths`; return [(path, changed)]."""
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
                if not path.is_file() or path.read_text(encoding="utf-8") != text:
                    _replace(path, text)
                    changed = True
            done.append((entry["path"], changed))
            continue
        old = (root / file).read_text(encoding="utf-8")
        span = section_span(old, section)
        if span is None:
            raise KbError(f"{file} has no markers {' '.join(markers(section))}", code=1)
        new = old[:span[0]] + generator(entry)(root) + old[span[1]:]
        if new != old:
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
        elif (root / name).read_text(encoding="utf-8") != text:
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
    return failures


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


def _first(when):
    """The first stage that a conversion cell of section 19 names, or None."""
    numbers = [int(number) for number in re.findall(r"(?<![\w`])\d+(?![\w`])", when)]
    return min(numbers) if numbers else None


def converted(row, now, files, rendered_files):
    """Whether the owner after conversion owns the facts of a row of section
    19 at stage `now`: the row's stage precedes `now`, or it is `now` and a
    projection that `kb` renders registers every tracked file that the row
    names (`rendered_files`, of the tracked `files`). A registry created in a
    stage owns its facts from that stage."""
    when = row[2]
    first = _first(when)
    if first is None:
        return False
    if first < now or (first == now and when.startswith("created in ")):
        return True
    if first > now:
        return False
    patterns = [re.sub(r"<[^>]+>", "*", item) for item in re.findall(r"`([^`]+)`", row[0])
                if "/" in item]
    named = {name for pattern in patterns for name in files if matches(pattern, name)}
    return bool(named) and named <= rendered_files


def owners(root=repo.ROOT, now=None):
    """Registries whose owner after conversion owns their facts at stage
    `now`, with the owners, and the number of registries that own their facts
    until conversion by the stage that converts them."""
    now = stage(root) if now is None else now
    files, rendered_files = tracked(root), active(root, now)
    done, pending = [], {}
    for row in spec.table(spec.OWNERSHIP, root):
        first = _first(row[2])
        if first is None:
            continue
        if converted(row, now, files, rendered_files):
            done.append({"registry": spec.plain(row[0]), "owner": spec.plain(row[3]),
                         "stage": first})
        else:
            pending[first] = pending.get(first, 0) + 1
    return {"converted": done, "pending": pending}


def _owner(row, now, files, rendered_files):
    """The owner of the facts of a registry of section 19 at stage `now`."""
    _, _, when, after, _ = row
    if _first(when) is None or when.startswith("created in "):
        return after
    if converted(row, now, files, rendered_files):
        return f"{after} since stage {when}"
    return f"the registry until stage {when}"


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
        "  the command to use. `KB_GUARD=off` disables it for maintenance.",
        "- A registry owns its facts until the stage that converts it: change the",
        "  owner that the table below names, then regenerate its projections.",
        "",
        "| Question | Command |",
        "|---|---|",
    ]
    lines.extend(f"| {item['question']} | `uv run {item['command']}` |"
                 for item in bench["question"] if item["stage"] <= now)
    files, rendered_files = tracked(root), active(root, now)
    lines.extend(["", f"| Registry | Facts | Owner at stage {now} |", "|---|---|---|"])
    lines.extend(f"| {row[0]} | {row[1]} | {_owner(row, now, files, rendered_files)} |"
                 for row in spec.table(spec.OWNERSHIP, root))
    lines.append("")
    return "\n".join(lines) + "\n"
