"""The inputs of the checks and the record of their passes, which `kb check
--changed` compares (tools/kb/SPEC.md, section 13).

The inputs of a check are the files that it reads, those of the checks whose
results it reads included, and the source and configuration of `kb`: the
model checks read the model, which compiles from the inputs of the
fingerprint, the census registries of L0, and the Python files that the
`test` evidence of the model names, and the `projections` check renders the
model and reads every tracked file. `.kb/cache/checks.json` records for each
check the digest of its inputs when it last passed and the files it read
beyond those it states in advance; `kb check --changed` runs a check whose
digest differs from the recorded one.
"""

import json

from kb import fingerprint, l0, levels, match, project, repo, sites

RECORD = repo.STATE / "cache" / "checks.json"
KB = "tools/kb"
# Directories under tools/kb that no check reads.
UNREAD = {"tests", "__pycache__", ".pytest_cache"}
# The value of a tracked directory, a submodule, whose content no check reads.
DIRECTORY = "directory"


def model(root=repo.ROOT):
    """The files that a model check reads before its evidence names others:
    the inputs of the fingerprint and the census registries of L0."""
    from kb import compatibility
    config = repo.config(root)
    return (set(fingerprint.inputs(root))
            | {compatibility.PIN}
            | {settings["interp"] for settings in config["l0"].get("census", {}).values()})


def _projections(root):
    return set(project.tracked(root)) | model(root)


def _levels(root):
    return model(root) | {levels.HARDWARE.as_posix()}


# The files that a check reads, other than those of `kb` itself; a check
# that is not listed reads the model.
INPUTS = {
    "l0": l0.inputs,
    "sites": sites.inputs,
    "levels": _levels,
    "projections": _projections,
    "guard": project.tracked,
}


def common(root=repo.ROOT):
    """The source and configuration of `kb`, which every check reads."""
    base = root / KB
    return {path.relative_to(root).as_posix() for path in base.rglob("*")
            if path.is_file() and not UNREAD & set(path.relative_to(base).parts)}


class Passes:
    """The digests of the inputs of the checks at their last passes."""

    def __init__(self, root=repo.ROOT):
        self.root = root
        self.path = root / RECORD
        try:
            self.passed = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.passed = {}
        self.hashes = fingerprint.Hashes(root)
        self.lists = {}

    def inputs(self, name):
        """The input paths that a check states in advance."""
        function = INPUTS.get(name, model)
        if function not in self.lists:
            self.lists[function] = set(function(self.root))
        if common not in self.lists:
            self.lists[common] = common(self.root)
        return self.lists[function] | self.lists[common]

    def read(self, name):
        """The files that a check read at its last pass beyond its stated
        inputs."""
        entry = self.passed.get(name)
        return entry["read"] if isinstance(entry, dict) else []

    def value(self, path):
        """The blob hash of an input file, or the value of a directory."""
        from kb import compatibility
        if path == compatibility.PIN:
            return compatibility.reference_commit(self.root)
        if (self.root / path).is_dir():
            return DIRECTORY
        return self.hashes.of(path)

    def digest(self, name, read=None):
        """The digest of the current inputs of a check, with the files it
        read beyond them, by default those of its last pass."""
        paths = self.inputs(name) | set(self.read(name) if read is None else read)
        return fingerprint.digest((path, self.value(path)) for path in paths)

    def unchanged(self, name, value):
        """Whether the check passed with the inputs of this digest."""
        entry = self.passed.get(name)
        return isinstance(entry, dict) and entry["digest"] == value

    def run(self, name, check, changed=False):
        """The failures of a check, or None when `changed` and its inputs are
        those of its last pass; record the digest of a pass and forget the
        check after a failure."""
        digest = self.digest(name)
        if changed and self.unchanged(name, digest):
            return None
        match.READ.clear()
        failures = check(self.root)
        read = sorted(match.READ - self.inputs(name))
        if read != self.read(name):
            digest = self.digest(name, read)
        if failures:
            self.passed.pop(name, None)
        else:
            self.passed[name] = {"digest": digest, "read": read}
        return failures

    def save(self):
        self.hashes.save()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.passed, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
        temporary.replace(self.path)
