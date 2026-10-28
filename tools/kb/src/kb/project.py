"""Generate and check declared repository projections and knowledge access rules."""

from importlib import import_module
import importlib.util
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import tomllib

from kb import repo, spec
from kb.repo import KbError

PATH = Path("tools/kb/projections.toml")
BENCH = Path("tools/kb/bench.toml")
HOOK = Path("tools/kb/hook.py")
KEYS = {"path", "generator", "inputs", "consumers", "read", "check"}
REQUIRED = KEYS - {"check"}
READ = ("guarded", "open")
# A tracked file whose first lines say this declares itself generated.
GENERATED = re.compile(r"(?i)generated (?:by|from)|do not edit|not survive the next run")
HEAD_LINES = 6


def load(root=repo.ROOT):
    return tomllib.loads((root / PATH).read_text(encoding="utf-8")).get("projection", [])


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
    """Render the projections of `kb`, or those of
    `paths`; return [(path, changed)]. With `check`, write nothing and
    return whether each file differs from its rendering."""
    entries = [entry for entry in load(root)
               if rendered(entry)]
    unknown = sorted(set(paths) - {entry["path"] for entry in entries})
    if unknown:
        raise KbError(f"no projection that kb renders: {', '.join(unknown)}",
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
    fix = f"(fix: uv run kb project {shlex.quote(entry['path'])})"
    files = renderings(root, entry)
    failures = [f"{name}: matches {entry['path']} and is no file of its rendering "
                f"(fix: git rm {shlex.quote(name)})" for name in sorted(set(found) - set(files))]
    for name, text in sorted(files.items()):
        if not matches(split(entry["path"])[0], name):
            failures.append(f"{name}: lies outside the path of projection {entry['path']} "
                            f"(fix: {entry['generator']})")
        elif not (root / name).is_file():
            failures.append(f"{name}: missing {fix}")
        elif name not in found:
            failures.append(f"{name}: not tracked (fix: git add {shlex.quote(name)})")
        elif (root / name).read_bytes() != text.encode("utf-8"):
            failures.append(f"{name}: file: differs from its rendering {fix}")
    return failures


def check(root=repo.ROOT):
    """Failure lines of the `projections` check."""
    failures = []
    fix = f"(fix: edit {PATH.as_posix()})"
    files = tracked(root)
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
            if not found:
                continue
            if section is None:
                failures.extend(_compare(root, entry, found))
                continue
            text = current(root, entry)
            if text is None:
                failures.append(f"{file}: {section}: no markers {' '.join(markers(section))} "
                                f"(fix: add them and run uv run kb project {shlex.quote(entry['path'])})")
            elif text != render(root):
                failures.append(f"{file}: {section or 'file'}: differs from its rendering "
                                f"(fix: uv run kb project {shlex.quote(entry['path'])})")
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


def agents(root=repo.ROOT):
    """The `kb` section of AGENTS.md: the knowledge access rules, the questions
    with their commands, and the current owner of each fact."""
    bench = tomllib.loads((root / BENCH).read_text(encoding="utf-8"))
    lines = [
        "",
        "",
        "## Knowledge access",
        "",
        f"Generated by `uv run kb project AGENTS.md#kb` from `{spec.PATH.as_posix()}` and",
        f"`{BENCH.as_posix()}`.",
        "",
        "- Start with `uv run kb brief`: the graph, the layouts, the owners,",
        "  and the open gaps. `uv run kb` answers what the repository knows",
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
        "- The table below names the current owner of each fact. Change a fact in",
        "  its owner, then regenerate its projections.",
        "",
        "| Question | Command |",
        "|---|---|",
    ]
    lines.extend(f"| {item['question']} | `uv run {item['command']}` |"
                 for item in bench["question"])
    lines.extend(["", "| Registry | Facts | Owner |", "|---|---|---|"])
    lines.extend(f"| {row[0]} | {row[1]} | "
                 f"{row[2]} |"
                 for row in spec.table(spec.OWNERSHIP, root))
    lines.append("")
    return "\n".join(lines) + "\n"
