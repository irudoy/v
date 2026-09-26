"""The `guard` check (tools/kb/SPEC.md, sections 13 and 15).

The tracked `.claude/settings.json` runs `tools/kb/hook.py` before every
guarded tool, `.ignore` keeps ripgrep out of the guarded trees and the guarded
projections, and the hook denies what `tools/kb/config.toml` and
`tools/kb/projections.toml` guard: a read and an edit in every tree, an edit of
a file of every projection, and a read of every guarded projection.
"""

import json
from pathlib import Path

from kb import project, repo

SETTINGS = Path(".claude/settings.json")
IGNORE = Path(".ignore")
HOOK = project.HOOK
TOOLS = ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep", "Glob", "Bash")


def _registered(root):
    """The tools whose PreToolUse hooks run the guard."""
    settings = json.loads((root / SETTINGS).read_text(encoding="utf-8"))
    covered = set()
    for group in settings.get("hooks", {}).get("PreToolUse", []):
        if any(HOOK.as_posix() in item.get("command", "") for item in group.get("hooks", [])):
            covered.update(group.get("matcher", "").split("|"))
    return covered


def check(root=repo.ROOT):
    """Failure lines of the `guard` check."""
    failures = []
    files = project.tracked(root)
    if SETTINGS.as_posix() not in files:
        failures.append(f"{SETTINGS.as_posix()}: not tracked (fix: git add -f "
                        f"{SETTINGS.as_posix()})")
    try:
        missing = [tool for tool in TOOLS if tool not in _registered(root)]
    except (OSError, ValueError) as error:
        missing = list(TOOLS)
        failures.append(f"{SETTINGS.as_posix()}: {error}")
    if missing:
        failures.append(f"{SETTINGS.as_posix()}: PreToolUse does not run {HOOK.as_posix()} "
                        f"before {', '.join(missing)} (fix: add them to the matcher)")
    guard = project.hook.Guard(root)
    ignored = {line.strip() for line in (root / IGNORE).read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.startswith("#")}
    guarded = [entry for entry in guard.projections if entry.get("read") == "guarded"]
    wanted = [f"/{tree}/" for tree in guard.trees]
    wanted += [f"/{option}" for entry in guarded
               for option in project.hook.expand(project.split(entry["path"])[0])]
    for line in wanted:
        if line not in ignored:
            failures.append(f"{IGNORE.as_posix()}: {line} is not listed (fix: add it)")
    for tree in guard.trees:
        sample = next((name for name in files if name.startswith(tree + "/")), f"{tree}/x")
        for tool, arguments in (("Read", {"file_path": str(root / sample)}),
                                ("Edit", {"file_path": str(root / sample)})):
            if guard.decide(tool, arguments) is None:
                failures.append(f"{HOOK.as_posix()}: {tool} of {sample} passes the guard of "
                                f"{tree}/ (fix: [guard] trees of tools/kb/config.toml)")
    for entry in guard.projections:
        file, section = project.split(entry["path"])
        sample = next((name for name in files if project.matches(file, name)), None)
        if sample is None:
            continue
        edit = {"file_path": str(root / sample)}
        if section:
            text = (root / sample).read_text(encoding="utf-8")
            span = project.section_span(text, section)
            edit.update(old_string=text[span[0]:span[1]] if span else "", new_string="")
        if guard.decide("Edit", edit) is None:
            failures.append(f"{HOOK.as_posix()}: an edit of {entry['path']} passes the guard "
                            f"(fix: {project.PATH.as_posix()})")
        if entry in guarded and guard.decide("Read", {"file_path": str(root / sample)}) is None:
            failures.append(f"{HOOK.as_posix()}: a read of guarded {entry['path']} passes the "
                            f"guard (fix: {project.PATH.as_posix()})")
    return failures
