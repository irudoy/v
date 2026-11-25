"""The `guard` check (tools/kb/SPEC.md, sections 13 and 15).

The tracked Claude Code, Codex, and Antigravity hook settings run
`tools/kb/hook.py` before every guarded tool, `.ignore` keeps ripgrep out of
the guarded trees and projections, and the hook denies what
`tools/kb/config.toml` and `tools/kb/projections.toml` guard: a read and an
edit in every tree, an edit of a file of every projection, and a read of every
guarded projection.
"""

import json
from pathlib import Path

from kb import project, repo

SETTINGS = Path(".claude/settings.json")
CODEX_SETTINGS = Path(".codex/hooks.json")
AGY_SETTINGS = Path(".agents/hooks.json")
IGNORE = Path(".ignore")
HOOK = project.HOOK
TOOLS = ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep", "Glob", "Bash")
CODEX_TOOLS = (*TOOLS, "apply_patch")
AGY_TOOLS = (
    "read_file",
    "edit_file",
    "write_file",
    "run_command",
    "view_file",
    "view_file_outline",
    "view_code_item",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "grep_search",
    "find_by_name",
    "list_dir",
)


def _registered(root, settings_path=SETTINGS):
    """The tools whose PreToolUse hooks run the guard."""
    settings = json.loads((root / settings_path).read_text(encoding="utf-8"))
    covered = set()
    for group in settings.get("hooks", {}).get("PreToolUse", []):
        if any(item.get("type") == "command" and not item.get("async") and
               HOOK.as_posix() in item.get("command", "") for item in group.get("hooks", [])):
            covered.update(group.get("matcher", "").split("|"))
    return covered


def _registered_agy(root, settings_path=AGY_SETTINGS):
    """The tools whose enabled Antigravity PreToolUse hooks run the guard."""
    settings = json.loads((root / settings_path).read_text(encoding="utf-8"))
    if not isinstance(settings, dict):
        raise ValueError("hooks.json root must be a JSON object")
    covered = set()
    for spec in settings.values():
        if not isinstance(spec, dict) or spec.get("enabled", True) is False:
            continue
        for group in spec.get("PreToolUse", []):
            if any(item.get("type", "command") == "command" and not item.get("async") and
                   HOOK.as_posix() in item.get("command", "") for item in group.get("hooks", [])):
                matcher = group.get("matcher", "")
                if matcher in ("*", ""):
                    covered.update(AGY_TOOLS)
                else:
                    covered.update(matcher.split("|"))
    return covered


def check(root=repo.ROOT):
    """Failure lines of the `guard` check."""
    failures = []
    files = project.tracked(root)
    configs = (
        (SETTINGS, TOOLS, _registered),
        (CODEX_SETTINGS, CODEX_TOOLS, _registered),
        (AGY_SETTINGS, AGY_TOOLS, _registered_agy),
    )
    for settings, tools, reader in configs:
        if settings.as_posix() not in files:
            failures.append(f"{settings.as_posix()}: not tracked (fix: git add -f "
                            f"{settings.as_posix()})")
        try:
            registered = reader(root, settings)
            missing = [tool for tool in tools if tool not in registered]
        except (OSError, ValueError) as error:
            missing = list(tools)
            failures.append(f"{settings.as_posix()}: {error}")
        if missing:
            failures.append(f"{settings.as_posix()}: PreToolUse does not run {HOOK.as_posix()} "
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
                                ("Edit", {"file_path": str(root / sample)}),
                                ("apply_patch", {"command": "*** Begin Patch\n"
                                 f"*** Delete File: {sample}\n*** End Patch\n"}),
                                ("read_file", {"Path": str(root / sample)}),
                                ("edit_file", {"Path": str(root / sample), "Target": "",
                                               "Replacement": ""}),
                                ("write_file", {"Path": str(root / sample), "Content": ""})):
            if guard.decide(tool, arguments) is None:
                failures.append(f"{HOOK.as_posix()}: {tool} of {sample} passes the guard of "
                                f"{tree}/ (fix: [guard] trees of tools/kb/config.toml)")
    for entry in guard.projections:
        file, section = project.split(entry["path"])
        sample = next((name for name in files if project.matches(file, name)), None)
        if sample is None:
            continue
        edit = {"file_path": str(root / sample)}
        agy_edit = {"Path": str(root / sample), "Target": "", "Replacement": ""}
        if section:
            text = (root / sample).read_text(encoding="utf-8")
            span = project.section_span(text, section)
            snippet = text[span[0]:span[1]] if span else ""
            edit.update(old_string=snippet, new_string="")
            agy_edit["Target"] = snippet
        if guard.decide("Edit", edit) is None:
            failures.append(f"{HOOK.as_posix()}: an edit of {entry['path']} passes the guard "
                            f"(fix: {project.PATH.as_posix()})")
        if guard.decide("edit_file", agy_edit) is None:
            failures.append(f"{HOOK.as_posix()}: edit_file of {entry['path']} passes the guard "
                            f"(fix: {project.PATH.as_posix()})")
        if guard.decide("write_file", {"Path": str(root / sample), "Content": ""}) is None:
            failures.append(f"{HOOK.as_posix()}: write_file of {entry['path']} passes the guard "
                            f"(fix: {project.PATH.as_posix()})")
        patch = "*** Begin Patch\n" + f"*** Delete File: {sample}\n*** End Patch\n"
        if guard.decide("apply_patch", {"command": patch}) is None:
            failures.append(f"{HOOK.as_posix()}: apply_patch of {entry['path']} passes the "
                            f"guard (fix: {project.PATH.as_posix()})")
        if entry in guarded and guard.decide("Read", {"file_path": str(root / sample)}) is None:
            failures.append(f"{HOOK.as_posix()}: a read of guarded {entry['path']} passes the "
                            f"guard (fix: {project.PATH.as_posix()})")
        if entry in guarded and guard.decide("read_file", {"Path": str(root / sample)}) is None:
            failures.append(f"{HOOK.as_posix()}: read_file of guarded {entry['path']} passes the "
                            f"guard (fix: {project.PATH.as_posix()})")
    return failures
