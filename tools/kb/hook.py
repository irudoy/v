#!/usr/bin/env python3
"""The access guard of the knowledge model (tools/kb/SPEC.md, section 15).

Claude Code and Codex run this hook before the registered file and shell
tools. Codex reports shell commands as Bash and file patches as apply_patch.
It reads the tool call as JSON on standard input and
denies a call that reads or searches a guarded tree or projection, or edits a
guarded tree or any projection, with a reason that names the command to use.
It uses only the standard library and reads its lists from
tools/kb/config.toml (`[guard]`) and tools/kb/projections.toml. `kb guard` records a session override; without an override,
`KB_GUARD=off` in the hook environment disables it.

Shell inspection preserves quotes, operators, subshell directories and raw
here-documents. Literal pipeline data becomes file operands for reading xargs
commands. File operands, redirections, substitutions and selected Git
operations have access checks; literal draft and message bodies remain data.
Inline Python supports finite literal file and metadata forms, with a
conservative refusal for unknown operations involving protected references.
Trusted `kb`, `make` and repository runners keep their input access after
shell substitutions and redirections have been checked. An unsupported Python
interpreter produces a deliberate denial rather than a hook error.
"""

import ast
import fnmatch
import glob
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path("tools/kb/config.toml")
PROJECTIONS = Path("tools/kb/projections.toml")
EDITS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
RUNNERS = ("tools/", "patches/")
DIRECTORY = ("cd", "pushd", "popd")
# Prefixes that run the rest of the command line as a command, with their
# options that take the next word as their value. timeout also takes a
# duration before the command, and env -S splits its value into words.
WRAPPERS = {
    "command": frozenset(),
    "env": frozenset({"-C", "--chdir", "-S", "--split-string", "-u", "--unset"}),
    "exec": frozenset({"-a"}),
    "nice": frozenset({"-n", "--adjustment"}),
    "nohup": frozenset(),
    "time": frozenset({"-f", "--format", "-o", "--output"}),
    "timeout": frozenset({"-k", "--kill-after", "-s", "--signal"}),
}
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
        raise ValueError("guard mode must be on or off")
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
    projections = read(PROJECTIONS).get("projection", [])
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
        cwd, variables = cwd or self.cwd, dict(os.environ)
        inherited = variables.copy()
        scopes = []
        pipeline = []
        for words, documents in literal_loops(commands(command)):
            upstream = pipeline
            producer, _ = redirections(executed(words))
            literals = (producer[1:] if producer and os.path.basename(producer[0]) in {"echo", "printf"}
                        else [])
            pipeline = ([*upstream, *literals, *(text for text, _ in documents)]
                        if words and getattr(words[0], "piped", False) else [])
            if words == ["("] and getattr(words[0], "operator", False):
                scopes.append((cwd, variables.copy()))
                continue
            if words == [")"] and getattr(words[0], "operator", False):
                if scopes:
                    cwd, variables = scopes.pop()
                continue
            for word in words:
                reason = self.substitutions(word, cwd)
                if reason:
                    return reason
            local = variables.copy()
            prefix = list(words)
            wrapper_values = []
            while prefix:
                if _assignment(prefix[0]):
                    key, value = prefix.pop(0).split("=", 1)
                    local[key] = shell_value(value, variables)
                elif (unwrapped := _wrapped(prefix)) is not None:
                    prefix, values = unwrapped
                    wrapper_values += values
                else:
                    break
            # Wrapper option values such as `time -o FILE` and `env -C DIR`
            # may name paths.
            reason = self.shell_paths([shell_value(value, variables) for value in wrapper_values],
                                      "unknown", cwd)
            if reason:
                return reason
            extra_refs = [value for name, value in local.items() if inherited.get(name) != value]
            leaf = executed(words)
            if not leaf:
                variables = local
                continue
            clean, redirects = redirections(leaf)
            for operator, value in redirects:
                if operator == "<<<":
                    reason = self.substitutions(value, cwd)
                    if reason:
                        return reason
                    continue
                reason = self.shell_paths([shell_value(value, variables)],
                    "read" if operator in {"<", "<&"} else "edit", cwd)
                if reason:
                    return reason
            if not clean:
                continue
            program = os.path.basename(clean[0])
            for text, quoted in documents:
                if not quoted:
                    reason = self.substitutions(text, cwd)
                    if reason:
                        return reason
            if program in DIRECTORY:
                if len(clean) > 1:
                    value = shell_value(clean[1], variables)
                    if "$" in value:
                        return "cannot inspect a dynamic working directory; use an explicit path."
                    cwd = Path(os.path.normpath(cwd / os.path.expanduser(value)))
                continue
            if program == "git":
                reason = self.git_operation([shell_value(word, variables) for word in clean[1:]], cwd)
                if reason:
                    return reason
                continue
            if (program == "gh" and len(clean) > 2 and clean[1] in {"issue", "pr"}
                    and clean[2] in {"create", "comment", "close", "edit"}):
                files = {"--body-file", "-F"}
                reason = self.shell_paths([shell_value(value, variables)
                    for value in option_files(clean[3:], files)], "read", cwd)
                if reason:
                    return reason
                arguments = without_option_values(clean[3:], files | {"--comment", "--body", "--title", "-b", "-t"})
                reason = self.shell_paths([part for word in arguments
                    for part in candidates(shell_value(word, variables))], "unknown", cwd)
                if reason:
                    return reason
                continue
            if INTERPRETER.match(program) and program.startswith("python"):
                python_args = clean[1:]
                while python_args and python_args[0].startswith("-") and python_args[0] not in {"-", "-c", "-m"}:
                    python_args = python_args[2:] if python_args[0] in {"-W", "-X"} else python_args[1:]
                stdin = documents and (not python_args or python_args[0] == "-")
                if "-c" in clean or stdin:
                    arguments = (clean[clean.index("-c") + 2:] if "-c" in clean
                                 else clean[clean.index("-") + 1:] if "-" in clean else [])
                    reason = self.shell_paths([part for word in arguments
                        for part in candidates(shell_value(word, variables))], "unknown", cwd)
                    if reason:
                        return reason
                    source = (clean[clean.index("-c") + 1] if "-c" in clean
                              else "\n".join(item[0] for item in documents))
                    reason = self.python_operations(source, cwd, extra_refs)
                    if reason:
                        return reason
                    continue
                if len(clean) > 1 and messaging_script(clean[1]):
                    reason = self.shell_paths([part for value in extra_refs for part in candidates(value)], "unknown", cwd)
                    if reason:
                        return reason
                    values = option_files(clean[2:], {"--file"})
                    reason = self.shell_paths([shell_value(value, variables) for value in values], "read", cwd)
                    if reason:
                        return reason
                    continue
            if program == "xargs":
                reason = self.shell_paths([shell_value(value, variables)
                    for value in option_files(clean[1:], {"-a", "--arg-file"})], "read", cwd)
                if reason:
                    return reason
                invoked = xargs_command(clean[1:])
                if (invoked and os.path.basename(invoked[0]) not in {"printf", "echo", "true", "false", ":"}
                        and not self.passes(invoked, cwd)):
                    mode, _ = file_operands(invoked)
                    reason = self.shell_paths([part for word in [*upstream, *invoked[1:]]
                        for part in candidates(shell_value(word, variables))], mode, cwd)
                    if reason:
                        return reason
                continue
            if self.passes(clean, cwd):
                continue
            if program in {"sh", "bash", "zsh"} and (documents or "-c" in clean):
                text = (clean[clean.index("-c") + 1] if "-c" in clean
                        else "\n".join(item[0] for item in documents))
                reason = self.bash(text, cwd)
                if reason:
                    return reason
                continue
            if program in {"printf", "echo", "true", "false", ":"}:
                continue
            if program in {"test", "[", "[["} and not any(
                    word in {"-e", "-f", "-d", "-r", "-w", "-x", "-s", "-L", "-h", "-nt", "-ot", "-ef"} for word in clean):
                continue
            reason = self.shell_paths([part for value in extra_refs for part in candidates(value)], "unknown", cwd)
            if reason:
                return reason
            if program == "sort":
                reason = self.shell_paths(option_files(clean[1:], {"-o", "--output"}), "edit", cwd)
                if reason:
                    return reason
            if program in {"sed", "awk", "gawk"}:
                _, _, sources = editor_inputs(clean)
                reason = self.shell_paths([part for source in sources
                    if editor_file_actions(source, program)
                    for part in PATHLIKE.findall(shell_value(source, variables))], "unknown", cwd)
                if reason:
                    return reason
            mode, values = file_operands(clean)
            values = [shell_value(value, variables) for value in values]
            if not values and program in {"ls", "find", *SEARCHERS}:
                values = [str(cwd)]
            reason = self.shell_paths(values, mode, cwd)
            if reason:
                return reason
        return None

    def substitutions(self, text, cwd):
        """Inspect simple command substitutions; ambiguous guarded forms refuse."""
        if not getattr(text, "expansion", True):
            return None
        pattern = re.compile(r"\$\(([^()]*)\)|`([^`]*)`", re.DOTALL)
        for match in pattern.finditer(text):
            reason = self.bash(match.group(1) if match.group(1) is not None else match.group(2), cwd)
            if reason:
                return reason
        if "$(" in pattern.sub("", text) or "`" in pattern.sub("", text):
            return "cannot inspect a nested command substitution; use explicit file operands."
        return None

    def shell_paths(self, values, mode, cwd):
        for value in values:
            if not value or value == "-" or value.isdigit():
                continue
            dynamic = re.search(r"[$`]", value)
            if dynamic:
                prefix = value[:dynamic.start()]
                base = Path(prefix) if prefix.endswith("/") else Path(prefix).parent
                if (os.path.isabs(prefix) and not self.root.is_relative_to(base.resolve())
                        and not base.resolve().is_relative_to(self.root)):
                    continue
                return "cannot inspect a dynamic file operand; use an explicit path or the KB command."
            for option in expand(value):
                absolute = os.path.expanduser(option)
                if not os.path.isabs(absolute):
                    absolute = str(cwd / absolute)
                if "**" in absolute:
                    first = next((index for index, char in enumerate(absolute) if char in "*?["), len(absolute))
                    prefix = Path(absolute[:first]).parent if not absolute[:first].endswith("/") else Path(absolute[:first])
                    if self.root.is_relative_to(prefix.resolve()):
                        return "a recursive file pattern can enter protected paths; use explicit KB references."
                paths = glob.glob(absolute, recursive=True) if glob.has_magic(absolute) else [absolute]
                for path in paths or [absolute]:
                    if mode in {"edit", "unknown"}:
                        reason = self.edit({"file_path": path, "content": ""})
                        if reason:
                            return reason
                    reason = self.read(path)
                    if reason:
                        return reason
        return None

    def git_operation(self, words, cwd):
        index = 0
        while index < len(words) and words[index].startswith("-"):
            if words[index] == "-C" and index + 1 < len(words):
                cwd = cwd / words[index + 1]
            index += 2 if words[index] in {"-C", "-c", "--git-dir", "--work-tree"} else 1
        if index >= len(words):
            return None
        command, args = words[index], words[index + 1:]
        outputs = option_files(args, {"--output"})
        reason = self.shell_paths(outputs, "edit", cwd)
        if reason:
            return reason
        if command == "commit":
            return self.shell_paths(option_files(args, {"-F", "--file", "-t", "--template"}), "read", cwd)
        if command == "show":
            revisions = args[:args.index("--")] if "--" in args else args
            for word in revisions:
                if ":" in word and not word.startswith("-"):
                    reason = self.shell_paths([word.split(":", 1)[1]], "read", cwd)
                    if reason:
                        return reason
        if command in {"restore", "checkout", "rm", "mv"}:
            if "--staged" in args and "--worktree" not in args or "--cached" in args:
                return None
            return self.shell_paths([word for word in args if not word.startswith("-")], "edit", cwd)
        if command == "grep":
            return self.shell_paths(operands(["grep", *args]) or [str(cwd)], "read", cwd)
        if command == "diff" and "--no-index" in args:
            return self.shell_paths([word for word in args if not word.startswith("-")], "read", cwd)
        if self.git_passes(words):
            return None
        return self.shell_paths([part for word in args for part in candidates(word)], "unknown", cwd)

    def python_operations(self, source, cwd, extra_refs=()):
        """Inspect finite literal file forms; unknown uses of protected data refuse."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return "cannot inspect the Python program; use complete literal file operations."
        assignments = []
        for item in ast.walk(tree):
            if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                assignments.append((item.targets[0].id, item.value))
            if isinstance(item, ast.withitem) and isinstance(item.optional_vars, ast.Name):
                assignments.append((item.optional_vars.id, item.context_expr))
        bindings = {name: value for name, value in assignments
                    if sum(other == name for other, _ in assignments) == 1}

        def path(node, visited=()):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if isinstance(node, ast.Name) and node.id in bindings and node.id not in visited:
                return path(bindings[node.id], (*visited, node.id))
            if isinstance(node, ast.Call) and call_name(node.func).split(".")[-1] in {"Path", "open"} and node.args:
                return path(node.args[0], visited)
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)):
                left, right = path(node.left, visited), path(node.right, visited)
                if left is not None and right is not None:
                    return str(Path(left) / right) if isinstance(node.op, ast.Div) else left + right
            return None

        protected = (any(self.shell_paths(candidates(value), "unknown", cwd) for value in extra_refs)
                     or any(self.shell_paths(candidates(node.value), "unknown", cwd)
                            for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)))
        imports = {alias.asname or alias.name.split(".")[0] for node in ast.walk(tree)
                   if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        if protected:
            allowed = {"pathlib", "json", "tomllib", "hashlib", "datetime", "re", "sys", "os"}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    return "cannot inspect custom Python operations on protected references; use the KB command."
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Attribute) for target in node.targets):
                    return "cannot inspect rebound Python operations on protected references; use the KB command."
                if isinstance(node, ast.Import) and any(alias.name.split(".")[0] not in allowed for alias in node.names):
                    return "cannot inspect external Python operations on protected references; use the KB command."
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] not in allowed:
                    return "cannot inspect external Python operations on protected references; use the KB command."

        def data(node, visited=()):
            if isinstance(node, ast.Constant):
                return True
            if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
                return all(data(item, visited) for item in node.elts)
            if isinstance(node, ast.Dict):
                return all(data(item, visited) for item in node.values)
            if isinstance(node, ast.Subscript):
                return data(node.value, visited)
            if isinstance(node, ast.Name):
                # Repeated literal-data transformations are finite too. Every
                # preceding assignment must be data; file operands still use
                # the unique-binding resolver above.
                values = [value for name, value in assignments if name == node.id
                          and (value.lineno, value.col_offset) < (node.lineno, node.col_offset)]
                return bool(values) and all(id(value) not in visited and
                    data(value, (*visited, id(value))) for value in values)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                name = call_name(node.func)
                if name.split(".")[0] in {"json", "tomllib", "hashlib", "datetime", "re"}:
                    return True
                if node.func.attr == "read_text" and path(node.func.value) is not None:
                    return True
                return data(node.func.value, visited) and node.func.attr in {
                    "split", "rsplit", "strip", "partition", "replace", "decode", "encode", "get"}
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"str", "bytes", "repr"}:
                return node.func.id not in bindings and node.func.id not in imports
            return False
        readers = {"read_text", "read_bytes", "read", "readline", "readlines", "glob", "rglob", "iterdir"}
        writers = {"write_text", "write_bytes", "write", "unlink", "rename", "replace", "touch", "mkdir"}
        safe = {"print", "str", "bytes", "len", "any", "all", "sorted", "list", "dict", "tuple", "set",
                "SystemExit", "ValueError", "RuntimeError", "AssertionError",
                "enumerate", "range", "zip", "int", "bool", "isinstance", "split", "rsplit", "strip",
                "lstrip", "rstrip", "startswith", "endswith", "partition", "rpartition", "replace",
                "loads", "dumps", "dump", "sha256", "hexdigest", "encode", "decode", "join", "get",
                "items", "keys", "values", "append", "now", "isoformat"}
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            name = call_name(call.func).split(".")[-1]
            value, mode = None, "read"
            if protected and isinstance(call.func, ast.Name) and name in safe and (name in imports or name in bindings):
                return "cannot inspect a rebound Python operation on protected references; use the KB command."
            if name == "Path":
                value = path(call.args[0]) if call.args else None
            elif name == "open":
                method = isinstance(call.func, ast.Attribute)
                value = path(call.func.value) if method else path(call.args[0]) if call.args else None
                position = 0 if method else 1
                flags = next((path(item.value) for item in call.keywords if item.arg == "mode"),
                             path(call.args[position]) if len(call.args) > position else "r")
                if flags is None and protected:
                    return "cannot inspect dynamic Python file mode; use an explicit mode."
                mode = "edit" if any(flag in (flags or "") for flag in "wax+") else "read"
            elif isinstance(call.func, ast.Attribute) and name in readers | writers:
                value = path(call.func.value)
                mode = "edit" if name in writers else "read"
                # String replacement is data, unlike Path.replace().
                if name == "replace" and data(call.func.value):
                    continue
                if name in {"rename", "replace"} and call.args:
                    destination = path(call.args[0])
                    if destination is None and protected:
                        return "cannot inspect a dynamic Python destination; use an explicit path."
                    if destination is not None:
                        reason = self.shell_paths([destination], "edit", cwd)
                        if reason:
                            return reason
            elif protected and name not in safe:
                return "cannot inspect an unknown Python operation on protected references; use the KB command."
            else:
                continue
            if value is None:
                if protected:
                    return "cannot inspect a dynamic Python file operand; use the KB command."
            else:
                reason = self.shell_paths([value], mode, cwd)
                if reason:
                    return reason
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
        """Whether git runs an allowed review or maintenance subcommand.

        git_operation checks blob reads and output writes before this list.
        The former show --stat entry retains its narrower compatibility.
        """
        index = 0
        while index < len(words) and words[index].startswith("-"):
            index += 2 if words[index] in ("-C", "-c", "--git-dir", "--work-tree") else 1
        if index >= len(words):
            return False
        subcommand = words[index]
        if subcommand == "show":
            return "show" in self.git or "--stat" in words[index:] and "show --stat" in self.git
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


def executed(words):
    words = _unwrap(words)
    if words and os.path.basename(words[0]) == "uv" and words[1:2] == ["run"]:
        words = _uv_run(words[2:])
    return words


def shell_value(word, variables):
    return re.sub(r"\$(?:\{([A-Za-z_]\w*)\}|([A-Za-z_]\w*))",
                  lambda match: variables.get(match.group(1) or match.group(2), match.group()), word)


def option_files(words, options):
    found, index = [], 0
    while index < len(words):
        word = words[index]
        index += 1
        if word in options and index < len(words):
            found.append(words[index])
            index += 1
        else:
            for option in options:
                if word.startswith(option + "="):
                    found.append(word[len(option) + 1:])
                    break
                if len(option) == 2 and word.startswith(option) and len(word) > 2:
                    found.append(word[2:])
                    break
    return found


def without_option_values(words, options):
    """Arguments after removing declared literal-data or separately checked options."""
    result, index = [], 0
    while index < len(words):
        word = words[index]
        index += 1
        if word in options:
            index += 1
        elif not any(word.startswith(option + "=") or
                     len(option) == 2 and word.startswith(option) and len(word) > 2
                     for option in options):
            result.append(word)
    return result


def xargs_command(words):
    """The finite xargs option forms before its invoked command."""
    values = {"-a", "--arg-file", "-d", "--delimiter", "-E", "--eof", "-I", "--replace",
              "-L", "--max-lines", "-n", "--max-args", "-P", "--max-procs", "-s", "--max-chars"}
    index = 0
    while index < len(words):
        word = words[index]
        if word == "--":
            return words[index + 1:]
        if not word.startswith("-"):
            return words[index:]
        index += 2 if word in values else 1
    return ["echo"]


def redirections(words):
    kept, found, index = [], [], 0
    while index < len(words):
        word = words[index]
        if getattr(word, "operator", False) and word in {"<", ">", ">>", "<>", ">&", "<&", "&>", "&>>", "<<", "<<<"}:
            if index + 1 >= len(words):
                found.append((word, "$uninspectable_redirect"))
                break
            if kept and kept[-1].isdigit():
                kept.pop()
            if word != "<<":
                found.append((word, words[index + 1]))
            index += 2
        else:
            kept.append(word)
            index += 1
    return kept, found


def messaging_script(value):
    path = Path(value).expanduser().resolve()
    return any(path == Path.home() / root / "skills/codex-messaging/scripts/sessions.py"
               for root in (".codex", ".agents"))


def call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return call_name(node.value) + "." + node.attr
    return ""


def file_operands(words):
    program, args = os.path.basename(words[0]), words[1:]
    if program in SEARCHERS:
        return "read", operands(words)
    if program in {"sed", "awk", "gawk"}:
        mode, files, _ = editor_inputs(words)
        return mode, files
    readers = {"cat", "head", "tail", "cut", "sort", "wc", "ls", "find", "less", "more", "od", "xxd", "strings"}
    mode = "read" if program in readers else "edit" if program in {
        "cp", "mv", "rm", "tee", "touch", "truncate", "install"} else "unknown"
    value_options = {
        "head": {"-n", "-c", "--lines", "--bytes"},
        "tail": {"-n", "-c", "--lines", "--bytes"},
        "cut": {"-d", "-f", "-c", "-b", "--delimiter", "--fields", "--characters", "--bytes"},
        "sort": {"-t", "-k", "--field-separator", "--key"},
    }.get(program, set())
    values, index = [], 0
    while index < len(args):
        word = args[index]
        index += 1
        if word in value_options:
            index += 1
        elif word.startswith("--") and "=" in word:
            values.append(word.split("=", 1)[1])
        elif not word.startswith("-"):
            values.append(word)
    return mode, values if mode != "unknown" else [part for word in words for part in candidates(word)]


def editor_inputs(words):
    """Separate sed/awk program text, program files and actual file operands."""
    files, sources, script, index = [], [], False, 1
    while index < len(words):
        word = words[index]
        index += 1
        if word in {"-e", "--expression", "-f", "--file", "-v", "-F"} and index < len(words):
            value = words[index]
            index += 1
            if word in {"-e", "--expression"}:
                sources.append(value)
                script = True
            elif word in {"-f", "--file"}:
                files.append(value)
                script = True
        elif word.startswith(("--expression=", "--file=")):
            (sources if word.startswith("--expression=") else files).append(word.split("=", 1)[1])
            script = True
        elif word.startswith(("-e", "-f")) and len(word) > 2:
            (sources if word.startswith("-e") else files).append(word[2:])
            script = True
        elif word.startswith("-") or not word:
            continue
        elif not script:
            sources.append(word)
            script = True
        else:
            files.append(word)
    mode = "edit" if any(word == "--in-place" or word.startswith(("-i", "--in-place=")) for word in words[1:]) else "read"
    return mode, files, sources


def editor_file_actions(source, program):
    """Finite embedded I/O forms; ordinary formatting text has no file operands."""
    if program != "sed":
        return bool(re.search(r">|\b(?:getline|system)\b|@(?:include|load)\b", source))
    for command in re.split(r"[;\n]", source):
        match = re.match(r"\s*(?:[\d$,!]+|/[^/]*/)?\s*s([^\w\s])", command)
        if match:
            # Skip the two delimited data fields; only flags can add I/O.
            fields = re.split(r"(?<!\\)" + re.escape(match[1]), command[match.end():], maxsplit=2)
            if len(fields) == 3 and re.fullmatch(r"[gpiImM\d\s]*", fields[2]):
                continue
        # Unrecognized programs keep the conservative check of explicit paths.
        return True
    return False


def _wrapped(words):
    """The words after one leading wrapper and the values of its options, or
    None when the command does not start with a wrapper."""
    if not words or words[0] not in WRAPPERS:
        return None
    takes_value, rest, values = WRAPPERS[words[0]], list(words[1:]), []
    while rest and rest[0].startswith("-"):
        option = rest.pop(0)
        if option == "--":
            break
        # A value follows as the next word, after `=` of a long option, or
        # attached to a short option.
        name, value = option, None
        if option.startswith("--") and "=" in option:
            name, value = option.split("=", 1)
        elif not option.startswith("--") and option[:2] in takes_value and len(option) > 2:
            name, value = option[:2], option[2:]
        if name not in takes_value:
            continue
        if value is None:
            if not rest:
                break
            value = rest.pop(0)
        if name in {"-S", "--split-string"}:
            rest = [*value.split(), *rest]
        else:
            values.append(value)
    if words[0] == "timeout" and rest:
        rest.pop(0)
    return rest, values


def _unwrap(words):
    """The words of a simple command after its assignments and wrappers."""
    while words:
        if _assignment(words[0]):
            words = words[1:]
        elif (unwrapped := _wrapped(words)) is not None:
            words = unwrapped[0]
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
    kept, rest, pattern, options = [], unwrapped[1:], "--files" in unwrapped[1:], True
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
            index += 1
        elif options and word.startswith("-") and word != "-":
            kept.append(word)
        elif not pattern:
            pattern = True
        else:
            kept.append(word)
    return kept


def commands(command):
    """Simple commands with their raw here-document bodies and quote state."""
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
            bodies.append(("\n".join(body), bool(match.group(2))))
    found = _simple("\n".join(kept))
    if sum(getattr(word, "operator", False) and word == "<<" for words in found for word in words) != len(bodies):
        # A here-document marker inside quotes: every line is a command.
        found, bodies = _simple(command), []
    result = []
    for words in found:
        body = []
        for _ in range(sum(getattr(word, "operator", False) and word == "<<" for word in words)):
            if bodies:
                body.append(bodies.pop(0))
        result.append((words, body))
    return result


def literal_loops(items, budget=None):
    """Inspect each finite literal for-list; unknown iteration values stay unknown."""
    budget = [256] if budget is None else budget
    result, index = [], 0
    while index < len(items):
        words, documents = items[index]
        index += 1
        if len(words) < 2 or words[0] != "for" or not words[1].isidentifier():
            result.append((words, documents))
            continue
        body, depth, end = [], 1, index
        while end < len(items):
            nested, docs = items[end]
            if nested[:1] == ["do"]:
                piped = getattr(nested[0], "piped", False)
                nested = nested[1:]
                if nested:
                    nested[0].piped = piped
            end += 1
            if nested[:1] == ["for"]:
                depth += 1
            elif nested[:1] == ["done"]:
                depth -= 1
                if not depth:
                    break
            if nested:
                body.append((nested, docs))
        finite = (not depth and words[2:3] == ["in"] and not documents
                  and all(not re.search(r"[$`*?\[{}]", value) for value in words[3:]))
        if finite:
            for value in words[3:]:
                budget[0] -= 1
                if budget[0] < 0:
                    return [([ShellWord("__uninspectable_loop__"), "$loop_limit"], [])]
                result.append(([ShellWord(f"{words[1]}={value}")], []))
                result.extend(literal_loops(body, budget))
            index = end
        else:
            result.append((words, documents))
            result.append(([ShellWord(f"{words[1]}=$unknown_loop_value")], []))
            if not depth:
                result.extend(literal_loops(body, budget))
                index = end
    return result


class ShellWord(str):
    def __new__(cls, value, *, operator=False, expansion=False):
        instance = super().__new__(cls, value)
        instance.operator, instance.expansion = operator, expansion
        return instance


SHELL_OPERATOR = re.compile(r"&&|\|\||<<<|<<|&>>|&>|>>|<>|>&|<&|[();|&\n<>]")


def _substitution_end(text, start):
    """End of one balanced substitution; its contents remain shell source."""
    if text[start] == "`":
        index = start + 1
        while index < len(text):
            if text[index] == "\\":
                index += 2
            elif text[index] == "`":
                return index + 1
            else:
                index += 1
    else:
        depth, quote, index = 1, None, start + 2
        while index < len(text):
            char = text[index]
            if char == "\\" and quote != "'":
                index += 2
                continue
            if quote:
                if char == quote:
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if not depth:
                    return index + 1
            index += 1
    raise ValueError("unterminated command substitution")


def _shell_words(text):
    """POSIX quote removal retains operators and executable substitutions."""
    tokens, value, quote, started, expansion, index = [], "", None, False, False, 0

    def word():
        nonlocal value, started, expansion
        if started:
            tokens.append(ShellWord(value, expansion=expansion))
        value, started, expansion = "", False, False

    while index < len(text):
        char = text[index]
        if quote == "'":
            if char == "'":
                quote = None
            else:
                value += char
            index += 1
            continue
        if char == "\\":
            if index + 1 == len(text):
                raise ValueError("trailing escape")
            next_char = text[index + 1]
            if quote == '"' and next_char not in '$`"\\\n':
                value += char
                index += 1
                continue
            if next_char != "\n":
                value += next_char
                started = True
            index += 2
            continue
        if char == "`" or text.startswith("$(", index):
            end = _substitution_end(text, index)
            value += text[index:end]
            started, expansion, index = True, True, end
            continue
        if quote == '"':
            if char == '"':
                quote = None
            else:
                value += char
            index += 1
            continue
        if char in "'\"":
            quote, started = char, True
            index += 1
            continue
        if char == "#" and not started:
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        operator = SHELL_OPERATOR.match(text, index)
        if operator:
            word()
            tokens.append(ShellWord(operator.group(), operator=True))
            index = operator.end()
        elif char in " \t\r":
            word()
            index += 1
        else:
            value += char
            started = True
            index += 1
    if quote:
        raise ValueError("unterminated quote")
    word()
    return tokens


def _simple(text):
    """Commands and subshell boundaries, without mistaking quoted data for operators."""
    found, words = [], []
    try:
        for token in _shell_words(text):
            if token.operator and token in {";", "&&", "||", "|", "&", "\n", "(", ")"}:
                if words:
                    words[0].piped = token == "|"
                    found.append(words)
                words = []
                if token in {"(", ")"}:
                    found.append([token])
            else:
                words.append(token)
    except ValueError:
        return [["__uninspectable_shell__", text]]
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


def denial(reason):
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "kb guard: " + reason}}, sys.stdout)
    return 0


def main():
    if sys.version_info < (3, 11):
        return denial("Python 3.11 or newer is required; restore the working tree's .venv interpreter.")
    call = json.load(sys.stdin)
    mode = session_mode(ROOT, call.get("session_id"))
    if mode == "off" or (mode is None and os.environ.get("KB_GUARD", "").lower() == "off"):
        return 0
    try:
        reason = Guard(ROOT, call.get("cwd")).decide(call.get("tool_name", ""),
                                                    call.get("tool_input") or {})
    except ModuleNotFoundError as error:
        if error.name == "tomllib":
            return denial("Python 3.11 with tomllib is required; restore the working tree's .venv interpreter.")
        raise
    if reason:
        session = session_key(call.get("session_id"))
        maintenance = (f"uv run kb guard off --session {session}" if session else
                       "KB_GUARD=off in the hook environment")
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": f"kb guard: {reason} ({maintenance} disables the "
                                        "guard for maintenance)"}}, sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # A broken guard must not block the session.
        print(f"kb guard: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
