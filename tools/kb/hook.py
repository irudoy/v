#!/usr/bin/env python3
"""The access guard of the knowledge model (tools/kb/SPEC.md, section 15).

Claude Code and Codex run this hook before the registered file and shell
tools. Codex reports shell commands as Bash and file patches as apply_patch.
It reads the tool call as JSON on standard input and
denies a call that reads knowledge whose owner lies under a guarded tree or in
a guarded projection, edits a guarded tree or a projection, searches a guarded
path, or names one in a shell command, with a reason that names the command to
use. It uses only the standard library and reads its lists from
tools/kb/config.toml (`[guard]`), tools/kb/projections.toml, and the stage of
tools/kb/bench.toml: a projection whose `stage` lies ahead is still owned by
its registry. A launcher records a session override; without an override,
`KB_GUARD=off` in the hook environment disables it.

A shell command splits into simple commands at the shell operators and line
breaks, and the body of a here-document belongs to the command that reads it.
A word, or a path-like part of it, names a path when it holds a slash or
equals a projection file; the pattern of a search program names none, and a
command that runs inside a guarded tree names that tree. A simple command that
names a guarded path passes when it changes the directory or runs `kb`, a git
subcommand of the allow list, `make`, or a repository script under `tools/` or
`patches/`, which read their inputs as the gates do.
"""

import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path("tools/kb/config.toml")
PROJECTIONS = Path("tools/kb/projections.toml")
BENCH = Path("tools/kb/bench.toml")
EDITS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
RUNNERS = ("tools/", "patches/")
DIRECTORY = ("cd", "pushd", "popd")
# Prefixes that run the rest of the command line as a command.
WRAPPERS = ("command", "env", "exec", "nohup", "time")
INTERPRETER = re.compile(r"(?:python(?:\d+(?:\.\d+)?)?|bash|sh|zsh)$")
# Options of `uv run` that take the next word as their value.
UV_VALUES = {"--project", "--directory", "--package", "--with", "--with-editable",
             "--with-requirements", "--python", "-p", "--env-file", "--extra", "--group",
             "--index", "--default-index"}
# Search programs, the options that give their pattern, and the options that
# take the next word as their value.
SEARCHERS = {"ack", "ag", "egrep", "fgrep", "grep", "rg"}
PATTERNS = {"-e", "--regexp", "-f", "--file"}
SEARCH_VALUES = {"-A", "-B", "-C", "-g", "-j", "-m", "-M", "-t", "-T", "--after-context",
                 "--before-context", "--colors", "--context", "--exclude", "--exclude-dir",
                 "--glob", "--iglob", "--include", "--max-columns", "--max-count",
                 "--max-depth", "--sort", "--sortr", "--threads", "--type", "--type-not"}
PUNCTUATION = "();<>|&\n"
HEREDOC = re.compile(r"(?<!<)<<(?!<)(-?)[ \t]*(['\"]?)([^\s'\"<>|&;()]+)\2")
PATHLIKE = re.compile(r"[^\s'\"`()\[\]{},:;=<>|&$]+")
BRACES = re.compile(r"\{([^{}]*)\}")
# An edit reason lists the inputs of a projection up to this many.
LISTED_INPUTS = 4


def session_key(session_id):
    """Canonical UUID of an explicit root session, or None."""
    try:
        return str(uuid.UUID(session_id)) if isinstance(session_id, str) else None
    except ValueError:
        return None


def session_state_path(root, session_id):
    """Local state keyed by the canonical project path and root session UUID."""
    key = session_key(session_id)
    if key is None:
        raise ValueError("an explicit session UUID is required")
    project = str(Path(root).resolve())
    digest = hashlib.sha256(project.encode("utf-8")).hexdigest()
    return Path.home() / ".local/state/vq-kb-guard" / digest / f"{key}.json"


def session_mode(root, session_id):
    """Read a valid override; missing or malformed state grants no exception."""
    key = session_key(session_id)
    if key is None:
        return None
    try:
        state = json.loads(session_state_path(root, key).read_text(encoding="utf-8"))
        if (isinstance(state, dict) and type(state.get("version")) is int
                and state["version"] == 1
                and state.get("project") == str(Path(root).resolve())
                and state.get("session_id") == key and state.get("mode") in ("on", "off")):
            return state["mode"]
    except (OSError, ValueError):
        pass
    return None


def set_session_mode(root, session_id, mode):
    """Atomically persist only this project's session override."""
    if mode not in ("on", "off"):
        raise ValueError("KB_GUARD must be on or off")
    path = session_state_path(root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    state = {"version": 1, "project": str(Path(root).resolve()),
             "session_id": session_key(session_id), "mode": mode}
    descriptor, name = tempfile.mkstemp(prefix=".session-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(state, stream, sort_keys=True)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return path


def load(root=ROOT):
    """(trees, git allow list, active projections) of the repository at `root`."""
    import tomllib

    def read(path):
        return tomllib.loads((root / path).read_text(encoding="utf-8"))

    config = read(CONFIG).get("guard", {})
    stage = read(BENCH).get("stage", 0)
    projections = [entry for entry in read(PROJECTIONS).get("projection", [])
                   if entry.get("stage", 0) <= stage]
    return (tuple(tree.rstrip("/") for tree in config.get("trees", ())),
            tuple(config.get("git", ())), projections)


def split(path):
    """(file, section) of a projection path `<file>#<section>`."""
    file, _, section = path.partition("#")
    return file, section or None


def expand(pattern):
    """The patterns of a projection path whose `{a,b}` lists alternatives."""
    match = BRACES.search(pattern)
    if match is None:
        return [pattern]
    return [option for choice in match.group(1).split(",")
            for option in expand(pattern[:match.start()] + choice + pattern[match.end():])]


def matches(pattern, relative):
    """Whether a repository path matches a projection path pattern, segment by
    segment, so that `*` stays inside one directory."""
    names = relative.split("/")
    for option in expand(pattern):
        parts = option.split("/")
        if len(parts) == len(names) and all(
                fnmatch.fnmatchcase(name, part) for part, name in zip(parts, names)):
            return True
    return False


def markers(name):
    return f"<!-- {name}:begin -->", f"<!-- {name}:end -->"


class Guard:
    def __init__(self, root=ROOT, cwd=None):
        self.root = Path(root).resolve()
        self.cwd = Path(cwd) if cwd else self.root
        self.trees, self.git, self.projections = load(self.root)

    # Paths ---------------------------------------------------------------

    def relative(self, text, cwd=None):
        """The repository path of a file path, or None outside the repository;
        a symbolic link counts as its target."""
        if not text:
            return None
        path = Path(os.path.expanduser(text))
        if not path.is_absolute():
            path = (cwd or self.cwd) / path
        for candidate in (path.resolve(), Path(os.path.normpath(path))):
            try:
                relative = candidate.relative_to(self.root).as_posix()
            except ValueError:
                continue
            return "" if relative == "." else relative
        return None

    def tree(self, relative):
        """The guarded tree that holds a repository path."""
        if not relative:
            return None
        return next((tree for tree in self.trees
                     if relative == tree or relative.startswith(tree + "/")), None)

    def projection(self, relative):
        """The active projection entry of a generated file."""
        if not relative:
            return None
        return next((entry for entry in self.projections
                     if matches(split(entry["path"])[0], relative)), None)

    def guarded(self, relative):
        """A guarded tree, or the path of a guarded projection, that holds a
        repository path; None for any other path. A directory above them is
        open: `.ignore` keeps its searches out of them."""
        tree = self.tree(relative)
        if tree:
            return tree + "/"
        entry = self.projection(relative)
        if entry and entry.get("read") == "guarded" and "#" not in entry["path"]:
            return entry["path"]
        return None

    # Decisions -----------------------------------------------------------

    def decide(self, tool, arguments):
        """The reason to deny a tool call, or None to let it pass."""
        if tool in EDITS:
            return self.edit(arguments)
        if tool == "Read":
            return self.read(arguments.get("file_path"))
        if tool in ("Grep", "Glob"):
            return self.search(tool, arguments)
        if tool == "Bash":
            workdir = arguments.get("workdir")
            cwd = self.cwd / workdir if workdir else self.cwd
            return self.bash(arguments.get("command", ""), cwd)
        if tool == "apply_patch":
            return self.patch(arguments.get("command", ""))
        return None

    def patch(self, command):
        """Inspect every source and destination of a Codex file patch.

        Reconstruct only marked projections, without writing any file, so an
        edit outside their generated section stays open as it does for Edit.
        An uninspectable patch is denied rather than skipping its paths.
        """
        try:
            changes = patch_files(command)
        except (TypeError, ValueError) as error:
            return f"cannot inspect apply_patch: {error}; use a complete file patch."
        for change in changes:
            path, move = change["path"], change.get("move")
            whole = change["kind"] != "Update" or move is not None
            reason = self.edit({"file_path": path, **({"content": ""} if whole else {})})
            if reason:
                return reason
            if move:
                reason = self.edit({"file_path": move, "content": ""})
                if reason:
                    return reason
            relative = self.relative(path)
            entry = self.projection(relative)
            if change["kind"] == "Update" and entry and "#" in entry["path"]:
                try:
                    original = (self.root / relative).read_text(encoding="utf-8")
                    content = patched_text(original, change["body"])
                except (OSError, ValueError) as error:
                    return (f"cannot inspect apply_patch of {entry['path']}: {error}; "
                            f"regenerate it with `{entry['generator']}`.")
                reason = self.edit({"file_path": path, "content": content})
                if reason:
                    return reason
        return None

    def edit(self, arguments):
        relative = self.relative(arguments.get("file_path") or arguments.get("notebook_path"))
        tree = self.tree(relative)
        if tree == "kb":
            return (f"{relative} belongs to the knowledge model and changes only through kb: "
                    "`uv run kb sync` draws the generated names of kb/names.csv, and the "
                    "write commands of tools/kb/SPEC.md section 12.3 change entity files.")
        if tree:
            return (f"{relative} is the L0 export of its layout: rerun "
                    "`tools/ghidra/export-l0.sh` instead of editing it.")
        entry = self.projection(relative)
        if entry is None:
            return None
        file, section = split(entry["path"])
        if section and not self.touches_section(relative, section, arguments):
            return None
        inputs = entry.get("inputs", ())
        inputs = (", ".join(inputs) if 0 < len(inputs) <= LISTED_INPUTS
                  else f"the inputs that {PROJECTIONS.as_posix()} lists")
        what = f"the {section} section of {file}" if section else relative
        return (f"{what} is generated by `{entry['generator']}`; edit {inputs} and "
                "regenerate it.")

    def touches_section(self, relative, name, arguments):
        """Whether an edit changes the marked section of a file or its markers."""
        try:
            text = (self.root / relative).read_text(encoding="utf-8")
        except OSError:
            return False
        begin, end = markers(name)
        start, stop = text.find(begin), text.find(end)
        if start < 0 or stop < start:
            return False
        stop += len(end)
        if "content" in arguments:
            new = arguments["content"]
            first, last = new.find(begin), new.find(end)
            return first < 0 or last < first or new[first:last + len(end)] != text[start:stop]
        for item in arguments.get("edits") or [arguments]:
            old = item.get("old_string", "")
            index = text.find(old) if old else -1
            while index >= 0:
                if index < stop and index + len(old) > start:
                    return True
                if not item.get("replace_all"):
                    break
                index = text.find(old, index + 1)
        return False

    def read(self, file_path):
        relative = self.relative(file_path)
        tree = self.tree(relative)
        if tree == "kb":
            return f"{relative} is a knowledge file: {knowledge(relative)}"
        if tree:
            parts = relative.split("/")
            layout = parts[1] if len(parts) > 2 else "<layout>"
            return (f"{relative} is L0: ask `uv run kb at {layout}:<address>`, "
                    f"`uv run kb code {layout}:<address>`, or `uv run kb cypher \"<query>\"`.")
        if self.guarded(relative):
            return (f"{relative} is a guarded projection: ask `uv run kb show <ref>`, "
                    "`uv run kb where <ref>`, or `uv run kb find <words>`.")
        return None

    def search(self, tool, arguments):
        base = arguments.get("path") or str(self.cwd)
        places = [base]
        if tool == "Glob":
            prefix = []
            for part in arguments.get("pattern", "").split("/"):
                if any(char in part for char in "*?[{"):
                    break
                prefix.append(part)
            if prefix:
                places.append(os.path.join(base, *prefix))
        for place in places:
            relative = self.relative(place)
            guarded = self.guarded(relative)
            if guarded:
                return (f"{relative} lies in {guarded}, whose knowledge kb answers: search "
                        "with `uv run kb find <words>`.")
        return None

    def bash(self, command, cwd=None):
        cwd = cwd or self.cwd
        for words, body in commands(command):
            named = []
            inside = self.tree(self.relative(str(cwd)))
            if inside:
                named.append(inside + "/")
            for word in operands(words) + body:
                for candidate in candidates(word):
                    relative = self.relative(candidate, cwd)
                    found = self.guarded(relative) if "/" in candidate else (
                        self.projection(relative) and self.guarded(relative))
                    if found:
                        named.append(found)
            if named and not self.passes(words, cwd):
                return (f"the command names {named[0]}, whose knowledge kb answers: use "
                        "`uv run kb` (at, code, cypher for l0/; show, raw, find, where for "
                        "kb/ and guarded projections).")
            if words[:1] in (["cd"], ["pushd"]) and len(words) > 1:
                cwd = Path(os.path.normpath(cwd / os.path.expanduser(words[1])))
        return None

    def passes(self, words, cwd=None):
        """Whether a simple command may name a guarded path."""
        words = _unwrap(words)
        if not words:
            return False
        program = os.path.basename(words[0])
        if program in DIRECTORY or program == "make":
            return True
        if program == "git":
            return self.git_passes(words[1:])
        if program == "uv" and words[1:2] == ["run"]:
            words = _uv_run(words[2:])
            if not words:
                return False
            program = os.path.basename(words[0])
        if INTERPRETER.match(program):
            words = words[1:]
            if words[:2] == ["-m", "kb"]:
                return True
            while words and words[0].startswith("-"):
                words = words[1:]
            if not words:
                return False
        elif program == "kb":
            return True
        elif "/" not in words[0]:
            # A PATH command such as cat is not a repository script merely
            # because its working directory lies under tools/ or patches/.
            return False
        runner = self.relative(words[0], cwd) or ""
        return runner.startswith(RUNNERS)

    def git_passes(self, words):
        """Whether a git command line after `git` runs a subcommand of the
        allow list; `show` passes only with `--stat`."""
        index = 0
        while index < len(words) and words[index].startswith("-"):
            index += 2 if words[index] in ("-C", "-c", "--git-dir", "--work-tree") else 1
        if index >= len(words):
            return False
        subcommand = words[index]
        if subcommand == "show":
            return "--stat" in words[index:] and "show --stat" in self.git
        return subcommand in self.git


def knowledge(relative):
    """The commands that answer a file under kb/."""
    parts = relative.split("/")
    if relative == "kb/names.csv":
        return ("ask `uv run kb show <layout>:<address>` or `uv run kb show <name>` for a "
                "generated name, and `uv run kb log <ref>` for its former names.")
    if len(parts) == 3 and parts[2].endswith(".toml"):
        ref = f"{parts[2][:-len('.toml')]}/{parts[1]}"
        return f"ask `uv run kb show {ref}` or `uv run kb raw {ref}`."
    return "ask `uv run kb show <ref>`, `uv run kb raw <ref>`, or `uv run kb find <words>`."


def _assignment(word):
    name, sep, _ = word.partition("=")
    return bool(sep) and name.isidentifier()


def _unwrap(words):
    """The words of a simple command after its assignments and wrappers."""
    while words:
        if _assignment(words[0]):
            words = words[1:]
        elif words[0] in WRAPPERS:
            words = words[1:]
            while words and words[0].startswith("-"):
                words = words[1:]
        else:
            break
    return words


def _uv_run(words):
    """The command that `uv run` runs, after its options."""
    while words and words[0].startswith("-"):
        words = words[2:] if words[0] in UV_VALUES else words[1:]
    return words


def operands(words):
    """The words of a simple command that may name paths: all of them but the
    pattern of a search program."""
    unwrapped = _unwrap(words)
    if not unwrapped or os.path.basename(unwrapped[0]) not in SEARCHERS:
        return words
    kept, rest, pattern, options = [], unwrapped[1:], False, True
    index = 0
    while index < len(rest):
        word = rest[index]
        index += 1
        if options and word == "--":
            options = False
        elif options and (word in PATTERNS or word.startswith(("--regexp=", "--file="))):
            pattern = True
            if word in PATTERNS:
                value = rest[index] if index < len(rest) else ""
                index += 1
            else:
                value = word.split("=", 1)[1]
            if word.startswith(("-f", "--file")):
                kept.append(value)
        elif options and word in SEARCH_VALUES:
            kept.extend(rest[index - 1:index + 1])
            index += 1
        elif options and word.startswith("-") and word != "-":
            kept.append(word)
        elif not pattern:
            pattern = True
        else:
            kept.append(word)
    return kept


def _operator(token):
    """Whether a punctuation token separates simple commands; redirections
    stay words of their command."""
    return any(char in token for char in ";&|()\n")


def commands(command):
    """[(words, here-document tokens)] of the simple commands of a command
    line. A here-document gives the path-like tokens of its body to the command
    that reads it."""
    lines, bodies, kept = command.split("\n"), [], []
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        kept.append(line)
        for match in HEREDOC.finditer(line):
            body = []
            while index < len(lines):
                text = lines[index]
                index += 1
                if (text.lstrip("\t") if match.group(1) else text) == match.group(3):
                    break
                body.append(text)
            bodies.append(PATHLIKE.findall("\n".join(body)))
    found = _simple("\n".join(kept))
    if sum(word == "<<" for words in found for word in words) != len(bodies):
        # A here-document marker inside quotes: every line is a command.
        found, bodies = _simple(command), []
    result = []
    for words in found:
        body = []
        for _ in range(sum(word == "<<" for word in words)):
            body.extend(bodies.pop(0) if bodies else ())
        result.append((words, body))
    return result


def _simple(text):
    """The simple commands of a text without here-document bodies."""
    lexer = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    found, words = [], []
    try:
        for token in lexer:
            if token and all(char in PUNCTUATION for char in token) and _operator(token):
                if words:
                    found.append(words)
                words = []
            else:
                words.append(token)
    except ValueError:
        return [line.split() for line in text.split("\n") if line.split()]
    if words:
        found.append(words)
    return found


def candidates(word):
    """The word and its path-like parts, such as the value of an option or a
    path in a quoted program."""
    found = [word] + [part for part in PATHLIKE.findall(word) if part != word]
    return [item for item in found if item and not item.startswith("-")]


def patch_files(command):
    """File operations of the apply_patch grammar, including rename targets."""
    if not isinstance(command, str):
        raise ValueError("patch command is not a string")
    lines = command.strip().splitlines()
    if len(lines) < 2 or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        raise ValueError("missing patch delimiters")
    changes, current = [], None
    for line in lines[1:-1]:
        match = re.fullmatch(r"\*\*\* (Add|Update|Delete) File: (.+)", line)
        if match:
            current = {"kind": match[1], "path": match[2], "body": []}
            changes.append(current)
        elif line.startswith("*** Move to: "):
            if current is None or current["kind"] != "Update" or "move" in current:
                raise ValueError("unexpected move target")
            current["move"] = line[len("*** Move to: "):]
            if not current["move"]:
                raise ValueError("empty move target")
        elif current is None or current["kind"] == "Delete":
            raise ValueError("unexpected patch body")
        elif current["kind"] == "Add" and not line.startswith("+"):
            raise ValueError("unexpected added-file line")
        elif current["kind"] == "Update" and not (
                not line or line[0] in " +-" or line == "@@" or line.startswith("@@ ") or
                line == "*** End of File"):
            raise ValueError("unexpected update line")
        else:
            current["body"].append(line)
    return changes


def _patch_index(lines, expected, start, eof=False):
    """Locate patch context, with the whitespace matching of apply_patch."""
    if not expected:
        return len(lines) if eof else start
    positions = range(start, len(lines) - len(expected) + 1)
    if eof:
        positions = [len(lines) - len(expected)]
    for normalize in (lambda line: line, str.rstrip, str.strip):
        wanted = [normalize(line) for line in expected]
        for index in positions:
            if index >= start and [normalize(line) for line in lines[
                    index:index + len(expected)]] == wanted:
                return index
    if eof:
        return _patch_index(lines, expected, start)
    raise ValueError("patch context does not match")


def patched_text(text, body):
    """Reconstruct an update for the marked-section check; never apply it."""
    lines, chunks, cursor, index = text.splitlines(), [], 0, 0
    while index < len(body):
        header = body[index]
        if header == "@@" or header.startswith("@@ "):
            index += 1
            if header.startswith("@@ "):
                cursor = _patch_index(lines, [header[3:]], cursor) + 1
        before, after, eof = [], [], False
        while index < len(body):
            line = body[index]
            if line == "@@" or line.startswith("@@ "):
                break
            index += 1
            if line == "*** End of File":
                eof = True
                break
            prefix, value = (line[0], line[1:]) if line else (" ", "")
            if prefix in " -":
                before.append(value)
            if prefix in " +":
                after.append(value)
        position = _patch_index(lines, before, cursor, eof)
        chunks.append((position, len(before), after))
        cursor = position + len(before)
    for position, count, after in reversed(chunks):
        lines[position:position + count] = after
    return "\n".join(lines) + "\n"


def main():
    call = json.load(sys.stdin)
    mode = session_mode(ROOT, call.get("session_id"))
    if mode == "off" or (mode is None and os.environ.get("KB_GUARD", "").lower() == "off"):
        return 0
    reason = Guard(ROOT, call.get("cwd")).decide(call.get("tool_name", ""),
                                                call.get("tool_input") or {})
    if reason:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": f"kb guard: {reason} (KB_GUARD=off disables the "
                                        "guard for maintenance)"}}, sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # A broken guard must not block the session.
        print(f"kb guard: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
