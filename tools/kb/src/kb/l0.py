"""L0: the machine extraction of each layout, stored in `l0/<layout>/`.

`export` runs the export scripts of `tools/ghidra/` headless against the
program of the layout's L0 image, normalizes the CSV files, writes them with
`manifest.toml`, and reports each function with a `fn` symbol whose entry or
body the export changes. `check_all` is the `l0` check of `kb check`.

Usage: python -m kb.l0 <layout> [--check] [--stage DIR] [--from-stage DIR]
"""

import argparse
import csv
from dataclasses import dataclass
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

from kb import repo
from kb.repo import KbError
from kb import ghidra_preparation as preparation

# Column types: `a` address, `i` decimal integer, `b` boolean, `h` hexadecimal
# bytes, `s` text; `?` allows an empty cell.
CORE = {
    "funcs.csv": (
        ("addr", "a"), ("size", "i"), ("is_thunk", "b"), ("is_external", "b"),
    ),
    "calls.csv": (("src", "a"), ("dst", "a")),
    "xrefs.csv": (("func_addr", "a"), ("periph_addr", "a"), ("kind", "s")),
    "function_signatures.csv": (
        ("addr", "a"), ("size", "i"), ("instructions", "i"),
        ("exact_sha256", "h"), ("mnemonic_sha256", "h"), ("shape_sha256", "h"),
    ),
    "function_sites.csv": (
        ("func_addr", "a"), ("ins_addr", "a"), ("ordinal", "i"), ("mnemonic", "s"),
    ),
    "function_references.csv": (
        ("func_addr", "a"), ("ins_addr", "a"), ("ordinal", "i"), ("mnemonic", "s"),
        ("ref_addr", "a"), ("width", "i"), ("value_hex", "h?"), ("ref_type", "s"),
    ),
    "function_tokens.csv": (
        ("func_addr", "a"), ("ins_addr", "a"), ("ordinal", "i"), ("mnemonic", "s"),
        ("shape", "s"),
    ),
}
ACCESSORS = (
    ("kernel", "a"), ("wrapper", "a"), ("slot", "a?"), ("accessor", "a?"),
    ("callsite", "a"), ("func", "s"),
    ("bt_r4", "a?"), ("bt_r5", "a?"), ("bt_r6", "a?"),
    ("df_r4", "a?"), ("df_r5", "a?"), ("df_r6", "a?"), ("df_r7", "a?"),
    ("k4", "s"), ("k5", "s"), ("k6", "s"), ("k7", "s"),
    ("verdict", "s"), ("branch", "i?"),
)
# Export columns that L0 leaves out: RenameFuncs.java writes project names
# into programs, and names come from L1.
DROPPED = {"funcs.csv": {"name"}}
MANIFEST = "manifest.toml"
# The fragments that MergeFuncs.java joins into their functions, per layout.
MERGES = Path("tools/ghidra/merges")
MERGE_HEADER = ("entry", "fragment", "note")
ENTRY_RE = re.compile(r"[0-9a-f]{8}")
ADDRESS_RE = re.compile(r"[0-9a-fA-F]{1,8}")
HEX_RE = re.compile(r"[0-9a-fA-F]+")
INTEGER_RE = re.compile(r"-?[0-9]+")


@dataclass(frozen=True)
class Census:
    """The accessor census of a layout: one ResolveAccessors run per kernel."""

    interp: str
    kernels: tuple
    fused: tuple
    copy_helpers: tuple

    @staticmethod
    def file(kernel):
        return f"accessors.{int(kernel, 16):x}.csv"


def census(layout_id, root=repo.ROOT):
    """The census plan of a layout from the configuration and its registry."""
    settings = repo.config(root).get("l0", {}).get("census", {}).get(layout_id)
    if settings is None:
        raise KbError(f"{repo.CONFIG}: [l0.census.{layout_id}] is missing")
    interp = settings["interp"]
    kernels, fused = set(), set()
    with (root / interp).open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            kernel = f"{int(row['kernel'], 16):08x}"
            kernels.add(kernel)
            if int(row["wrapper"], 16) == int(row["kernel"], 16):
                fused.add(kernel)
    helpers = tuple(f"{int(value, 16):08x}" for value in settings.get("copy_helpers", ()))
    return Census(interp, tuple(sorted(kernels)), tuple(sorted(fused)), helpers)


def expected_files(plan):
    return sorted(set(CORE) | {Census.file(kernel) for kernel in plan.kernels})


def columns_of(name):
    return ACCESSORS if name.startswith("accessors.") else CORE[name]


def _cell(kind, text, where):
    optional = kind.endswith("?")
    base = kind.rstrip("?")
    if text == "":
        if optional or base == "s":
            return ""
        raise KbError(f"{where}: empty cell")
    if base == "a":
        if not ADDRESS_RE.fullmatch(text):
            raise KbError(f"{where}: {text!r} is not an address")
        return f"{int(text, 16):08x}"
    if base == "i":
        if not INTEGER_RE.fullmatch(text):
            raise KbError(f"{where}: {text!r} is not an integer")
        return str(int(text))
    if base == "b":
        if text not in ("true", "false"):
            raise KbError(f"{where}: {text!r} is not a boolean")
        return text
    if base == "h":
        if not HEX_RE.fullmatch(text):
            raise KbError(f"{where}: {text!r} is not hexadecimal")
        return text.lower()
    return text


def _key(columns, row):
    key = []
    for (_, kind), value in zip(columns, row):
        base = kind.rstrip("?")
        if value == "":
            key.append((0, 0 if base in "ai" else ""))
        elif base == "a":
            key.append((1, int(value, 16)))
        elif base == "i":
            key.append((1, int(value)))
        else:
            key.append((1, value))
    return tuple(key)


def render(columns, rows):
    """The normal form: one header, minimal quoting, LF, unique sorted rows."""
    unique = sorted(set(rows), key=lambda row: _key(columns, row))
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow([name for name, _ in columns])
    writer.writerows(unique)
    return out.getvalue(), len(unique)


def normalize(name, text, where):
    """Normalize the rows of one export file; returns (text, rows)."""
    columns = columns_of(name)
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader, None)
    if header is None:
        raise KbError(f"{where}: empty file")
    wanted = [column for column, _ in columns]
    extra = set(header) - set(wanted) - DROPPED.get(name, set())
    missing = set(wanted) - set(header)
    if extra or missing:
        raise KbError(
            f"{where}: columns differ; missing={sorted(missing)} extra={sorted(extra)}"
        )
    index = [header.index(column) for column in wanted]
    rows = []
    for number, raw in enumerate(reader, 2):
        if len(raw) != len(header):
            raise KbError(f"{where}:{number}: {len(raw)} cells, header has {len(header)}")
        rows.append(tuple(
            _cell(kind, raw[position], f"{where}:{number}:{column}")
            for (column, kind), position in zip(columns, index)
        ))
    return render(columns, rows)


def _toml_string(value):
    return json.dumps(value, ensure_ascii=False)


def _toml_array(key, values):
    inline = f"{key} = [{', '.join(_toml_string(value) for value in values)}]"
    if len(inline) <= 78:
        return inline + "\n"
    body = "".join(f"    {_toml_string(value)},\n" for value in values)
    return f"{key} = [\n{body}]\n"


def render_manifest(manifest):
    lines = [
        f"layout = {_toml_string(manifest['layout'])}\n",
        f"image = {_toml_string(manifest['image'])}\n",
        f"image_sha256 = {_toml_string(manifest['image_sha256'])}\n",
        f"program = {_toml_string(manifest['program'])}\n",
        f"ghidra = {_toml_string(manifest['ghidra'])}\n",
        "\n[census]\n",
        f"interp = {_toml_string(manifest['census']['interp'])}\n",
        _toml_array("kernels", manifest["census"]["kernels"]),
        _toml_array("fused", manifest["census"]["fused"]),
        _toml_array("copy_helpers", manifest["census"]["copy_helpers"]),
        "\n[scripts]\n",
    ]
    lines += [
        f"{_toml_string(script)} = {_toml_string(digest)}\n"
        for script, digest in sorted(manifest["scripts"].items())
    ]
    if "preparation" in manifest:
        lines += ["\n[preparation]\n", "schema_version = 1\n", "\n[preparation.inputs]\n"]
        lines += [f"{_toml_string(path)} = {_toml_string(digest)}\n"
                  for path, digest in sorted(manifest["preparation"]["inputs"].items())]
    for name, entry in sorted(manifest["files"].items()):
        lines.append(f"\n[files.{_toml_string(name)}]\n")
        lines.append(f"sha256 = {_toml_string(entry['sha256'])}\n")
        lines.append(f"rows = {entry['rows']}\n")
    return "".join(lines)


def scripts(root=repo.ROOT):
    names = repo.config(root)["l0"]["scripts"]
    return {name: repo.sha256_file(root / repo.GHIDRA_SCRIPTS / name) for name in names}


def resolve_program(image, root=repo.ROOT):
    """Program name and image digest through tools/ghidra/program_name.py."""
    command = [
        sys.executable, "-m", "tools.ghidra.program_name", image,
        "--project-dir", _project_dir(), "--project-name", _project_name(),
    ]
    result = subprocess.run(
        command, cwd=root, capture_output=True, text=True, env=_root_env(root)
    )
    if result.returncode != 0:
        raise KbError(result.stderr.strip() or f"program lookup failed for {image}")
    program, sha256 = result.stdout.strip().split("\t")
    return program, sha256


def _root_env(root):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(root), env.get("PYTHONPATH")]))
    return env


def _project_dir():
    return os.environ.get(
        "GHIDRA_PROJECT_DIR", os.path.expanduser("~/tools/ghidra-projects")
    )


def _project_name():
    return os.environ.get("GHIDRA_PROJECT_NAME", "vq-hr")


def output_groups(plan):
    """Files sealed by the core session and every independent census session."""
    return [("program.sha256", *sorted(CORE)),
            *((Census.file(kernel),) for kernel in plan.kernels)]


def sessions(plan, stage, prepared=None, root=repo.ROOT):
    """Headless script arguments of every independently prepared session."""
    stage = str(stage)
    runs = [[
        "-postScript", "ProgramSha256.java", f"{stage}/program.sha256",
        "-postScript", "ExportGraph.java", stage,
        "-postScript", "ExportXrefs.java", stage,
        "-postScript", "ExportFunctionSignatures.java", stage,
        "-postScript", "ExportFunctionTokens.java", stage,
    ]]
    # One session per kernel: a function that the resolver recovers in memory
    # must not carry over into the census of another kernel.
    for kernel in plan.kernels:
        arguments = [f"{int(kernel, 16):x}"]
        if kernel in plan.fused:
            arguments.append("fused")
        arguments += [f"{int(helper, 16):x}" for helper in plan.copy_helpers]
        runs.append(["-postScript", "ResolveAccessors.java", stage, *arguments])
    if prepared is not None:
        for number, (arguments, outputs) in enumerate(zip(runs, output_groups(plan)), 1):
            wire = Path(stage) / f"preparation-{number}.tsv"
            receipt = Path(stage) / f"preparation-{number}.json"
            preparation.write_plan(prepared, wire, root)
            runs[number - 1] = preparation.session(prepared, wire, receipt, arguments, outputs)
    return runs


def run_sessions(jobs, root=repo.ROOT, workers=1, log=print):
    """Run (program, script arguments, log path) jobs headless.

    With more than one worker, every worker opens its own copy of the project,
    because a Ghidra project admits one process at a time; the sessions are
    read-only, so the copies hold the same programs.
    """
    import concurrent.futures
    import queue

    project_dir, project_name = _project_dir(), _project_name()
    with tempfile.TemporaryDirectory(prefix="kb-l0-projects-") as copies:
        slots = queue.Queue()
        if workers <= 1:
            slots.put(project_dir)
        else:
            for number in range(workers):
                target = Path(copies) / f"p{number}"
                target.mkdir()
                shutil.copy2(Path(project_dir) / f"{project_name}.gpr", target)
                shutil.copytree(
                    Path(project_dir) / f"{project_name}.rep",
                    target / f"{project_name}.rep",
                )
                slots.put(str(target))

        def run(job):
            program, arguments, log_path = job
            slot = slots.get()
            try:
                command = [
                    str(root / repo.GHIDRA_PIN), slot, project_name,
                    "-process", program, "-noanalysis", "-readOnly",
                    "-scriptPath", str(root / repo.GHIDRA_SCRIPTS), *arguments,
                ]
                result = subprocess.run(command, capture_output=True, text=True)
                Path(log_path).write_text(result.stdout + result.stderr)
                return job, result.returncode
            finally:
                slots.put(slot)

        failed = []
        with concurrent.futures.ThreadPoolExecutor(max(1, workers)) as pool:
            for done, (job, code) in enumerate(pool.map(run, jobs), 1):
                log(f"ghidra session {done}/{len(jobs)}: {Path(job[2]).name} exit {code}")
                if code != 0:
                    failed.append(job[2])
        if failed:
            raise KbError(f"headless Ghidra failed; logs: {', '.join(map(str, failed))}")


def stage_jobs(layout, plan, stage, root=repo.ROOT):
    """The headless jobs of one layout; writes program.txt into the stage."""
    program, _ = resolve_program(layout.image, root)
    stage = Path(stage)
    stage.mkdir(parents=True, exist_ok=True)
    (stage / "program.txt").write_text(program + "\n")
    prepared = preparation.plan(layout.id, root)
    return [
        (program, arguments, stage / f"session-{number}.log")
        for number, arguments in enumerate(sessions(plan, stage, prepared, root), 1)
    ]


def verify_stage(layout, stage, root=repo.ROOT):
    recorded = (Path(stage) / "program.sha256").read_text().strip()
    expected = repo.images(root)[layout.image].sha256
    if recorded != expected:
        program = (Path(stage) / "program.txt").read_text().strip()
        raise KbError(
            f"program {program} holds {recorded}; the registered {layout.image} "
            f"image is {expected}"
        )


def build(layout, plan, stage, out_dir, root=repo.ROOT):
    """Normalize a staged export into `out_dir` and write its manifest."""
    stage, out_dir = Path(stage), Path(out_dir)
    catalog = repo.images(root)
    verify_stage(layout, stage, root)
    prepared = preparation.plan(layout.id, root)
    preparation.verify_stage(prepared, stage, output_groups(plan), root)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in expected_files(plan):
        source = stage / name
        if not source.is_file():
            raise KbError(f"{source}: the export lacks {name}; a partial export is refused")
        text, rows = normalize(name, source.read_text(encoding="utf-8"), str(source))
        target = out_dir / name
        target.write_text(text, encoding="utf-8", newline="")
        files[name] = {"sha256": repo.sha256_file(target), "rows": rows}
    manifest = {
        "layout": layout.id,
        "image": layout.image,
        "image_sha256": catalog[layout.image].sha256,
        "program": (stage / "program.txt").read_text().strip(),
        "ghidra": repo.ghidra_version(root),
        "census": {
            "interp": plan.interp,
            "kernels": list(plan.kernels),
            "fused": list(plan.fused),
            "copy_helpers": list(plan.copy_helpers),
        },
        "scripts": scripts(root),
        "files": files,
    }
    if prepared is not None:
        preparation.check_exports(prepared, out_dir, root)
        manifest["preparation"] = prepared.manifest
    (out_dir / MANIFEST).write_text(render_manifest(manifest), encoding="utf-8")
    return manifest


def _functions(base):
    """{entry: size} and {entry: instruction addresses} of an L0 directory."""
    with (Path(base) / "funcs.csv").open(newline="", encoding="utf-8") as source:
        sizes = {int(row["addr"], 16): int(row["size"]) for row in csv.DictReader(source)}
    bodies = {}
    with (Path(base) / "function_tokens.csv").open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            bodies.setdefault(int(row["func_addr"], 16), set()).add(int(row["ins_addr"], 16))
    return sizes, bodies


def body_changes(old, new, names):
    """Lines for each entry of `names` ({entry: name}) whose function differs
    between the L0 directories `old` and `new`: the entry is no function entry,
    its size differs, or a new entry lies in its former body."""
    old_sizes, old_bodies = _functions(old)
    new_sizes, new_bodies = _functions(new)
    holders = {}
    for entry, body in new_bodies.items():
        for address in body:
            holders.setdefault(address, set()).add(entry)
    added = set(new_sizes) - set(old_sizes)
    lines = []
    for entry in sorted(set(names) & set(old_sizes)):
        label = f"{entry:08x} {names[entry]}"
        if entry not in new_sizes:
            where = ", ".join(f"{owner:08x}" for owner in sorted(holders.get(entry, ())))
            lines.append(f"{label}: no function entry; the instruction lies in "
                         f"{where or 'no function'}")
            continue
        parts = []
        if new_sizes[entry] != old_sizes[entry]:
            parts.append(f"size {old_sizes[entry]} -> {new_sizes[entry]}")
        inside = sorted(added & old_bodies.get(entry, set()))
        if inside:
            parts.append("new entries in the former body: "
                         + ", ".join(f"{address:08x}" for address in inside))
        if parts:
            lines.append(f"{label}: " + "; ".join(parts))
    return lines


def review(layout_id, old, new, root=repo.ROOT):
    """`body_changes` for the functions with a `fn` symbol of the layout."""
    from kb import compile  # the compiler reads L0 through the adapters

    try:
        model = compile.cached(root)
    except KbError as error:
        return [f"the model does not compile, so no function is compared: {error}"]
    names = {}
    for key, symbol in model.symbols.items():
        if key.layout == layout_id and key.kind == "fn":
            names[key.address] = symbol.meaning.key if symbol.meaning is not None else key.key
    return body_changes(old, new, names)


def export(layout_id, *, check=False, stage=None, from_stage=None, workers=1,
           root=repo.ROOT, log=print):
    """Export one layout into l0/<layout>/, or compare a fresh export with it.
    Each function with a `fn` symbol whose entry or body the export changes
    is logged as a `review:` line."""
    layout = repo.layout(layout_id, root)
    plan = census(layout_id, root)
    with tempfile.TemporaryDirectory(prefix=f"kb-l0-{layout_id}-") as scratch:
        scratch = Path(scratch)
        if from_stage:
            staged = Path(from_stage)
        else:
            staged = Path(stage) if stage else scratch / "stage"
            run_sessions(stage_jobs(layout, plan, staged, root), root, workers, log)
        built = scratch / "l0"
        build(layout, plan, staged, built, root)
        target = root / repo.L0 / layout_id
        if (target / "funcs.csv").is_file() and (target / "function_tokens.csv").is_file():
            for line in review(layout_id, target, built, root):
                log(f"review: {line}")
        if check:
            differences = compare_dirs(built, target)
            for line in differences:
                log(f"differs: {line}")
            return not differences
        preparation.promote_directory(built, target)
        log(f"wrote {target.relative_to(root)}")
        return True


def compare_dirs(left, right):
    left, right = Path(left), Path(right)
    names = {path.name for path in left.iterdir()}
    if right.is_dir():
        names |= {path.name for path in right.iterdir()}
    differences = []
    for name in sorted(names):
        a, b = left / name, right / name
        if not a.exists() or not b.exists() or a.read_bytes() != b.read_bytes():
            differences.append(name)
    return differences


@dataclass(frozen=True)
class Failure:
    path: str
    key: str
    message: str
    fix: str

    def __str__(self):
        return f"{self.path}: {self.key}: {self.message} ({self.fix})"


def _normal_cache(root):
    path = root / repo.STATE / "cache" / "l0-normal.json"
    try:
        return path, set(json.loads(path.read_text()))
    except (OSError, ValueError):
        return path, set()


def check_layout(layout, root=repo.ROOT, verified=None):
    """Failures of one layout's L0 against its manifest, the pins, and the catalog."""
    base = root / repo.L0 / layout.id
    shown = f"{repo.L0}/{layout.id}"
    export_cmd = f"tools/ghidra/export-l0.sh {layout.id}"
    failures = []

    def fail(path, key, message, fix=export_cmd):
        failures.append(Failure(path, key, message, fix))

    manifest_path = base / MANIFEST
    if not manifest_path.is_file():
        fail(f"{shown}/{MANIFEST}", "layout", "the layout has no L0 export")
        return failures
    try:
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        fail(f"{shown}/{MANIFEST}", "syntax", str(error))
        return failures
    where = f"{shown}/{MANIFEST}"
    catalog = repo.images(root)
    if manifest.get("layout") != layout.id:
        fail(where, "layout", f"names {manifest.get('layout')!r}")
    if manifest.get("image") != layout.image:
        fail(where, "image", f"names {manifest.get('image')!r}, the L0 image is {layout.image}")
    elif manifest.get("image_sha256") != catalog[layout.image].sha256:
        fail(where, "image_sha256", "differs from the image catalog")
    if manifest.get("ghidra") != repo.ghidra_version(root):
        fail(where, "ghidra", f"{manifest.get('ghidra')!r} differs from the pin "
             f"{repo.ghidra_version(root)} in {repo.GHIDRA_PIN}")
    current = scripts(root)
    recorded = manifest.get("scripts", {})
    for script in sorted(set(current) | set(recorded)):
        if recorded.get(script) != current.get(script):
            fail(where, f"scripts.{script}", "the export script changed since the export")
    plan = census(layout.id, root)
    expected_census = {
        "interp": plan.interp,
        "kernels": list(plan.kernels),
        "fused": list(plan.fused),
        "copy_helpers": list(plan.copy_helpers),
    }
    if manifest.get("census") != expected_census:
        fail(where, "census", f"differs from {repo.CONFIG} and {plan.interp}")
    listed = manifest.get("files", {})
    present = {path.name for path in base.iterdir() if path.name != MANIFEST}
    wanted = set(expected_files(plan))
    for name in sorted(wanted - set(listed)):
        fail(where, f"files.{name}", "the manifest lacks a required file")
    for name in sorted(present - set(listed)):
        fail(f"{shown}/{name}", "file", "the manifest does not list the file")
    for name in sorted(set(listed) - wanted):
        fail(where, f"files.{name}", "the file is not part of the layout's L0")
    for name in sorted(set(listed) & present):
        path = base / name
        digest = repo.sha256_file(path)
        if digest != listed[name].get("sha256"):
            fail(f"{shown}/{name}", "sha256", "differs from the manifest")
            continue
        if verified is not None and digest in verified:
            continue
        text = path.read_bytes().decode("utf-8")
        try:
            normal, rows = normalize(name, text, f"{shown}/{name}")
        except KbError as error:
            fail(f"{shown}/{name}", "normal-form", str(error))
            continue
        if normal != text:
            fail(f"{shown}/{name}", "normal-form", "the file is not in normal form")
        elif rows != listed[name].get("rows"):
            fail(f"{shown}/{name}", "rows", f"{rows} rows, the manifest lists {listed[name].get('rows')}")
        elif verified is not None:
            verified.add(digest)
    for name in sorted(set(listed) - present):
        fail(f"{shown}/{name}", "file", "the file is missing")
    failures += _join_failures(layout, base, present, root)
    try:
        prepared = preparation.plan(layout.id, root)
        expected_preparation = prepared.manifest if prepared is not None else None
        if manifest.get("preparation") != expected_preparation:
            fail(where, "preparation", "the preparation inputs differ from the accepted export")
        if prepared is not None and set(CORE) <= present:
            preparation.check_exports(prepared, base, root)
    except (KbError, OSError, ValueError, KeyError) as error:
        fail(where, "preparation", str(error))
    return failures


def merges(layout_id, root=repo.ROOT):
    """(entry, fragment) pairs of `tools/ghidra/merges/<layout>.csv`: the
    fragments that MergeFuncs.java joins into the function of each entry."""
    path = root / MERGES / f"{layout_id}.csv"
    if not path.is_file():
        return []
    shown = (MERGES / path.name).as_posix()
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.startswith("#")]
    reader = csv.reader(lines)
    if tuple(next(reader, ())) != MERGE_HEADER:
        raise KbError(f"{shown}: the header must be {','.join(MERGE_HEADER)}")
    pairs, seen = [], set()
    for row in reader:
        if len(row) != 3 or not all(ENTRY_RE.fullmatch(cell) for cell in row[:2]):
            raise KbError(f"{shown}: {','.join(row)}: expected entry,fragment,note with "
                          "eight-digit addresses and no comma in the note")
        entry, fragment = int(row[0], 16), int(row[1], 16)
        if fragment in seen or fragment == entry:
            raise KbError(f"{shown}: {row[1]}: a fragment joins one other function")
        seen.add(fragment)
        pairs.append((entry, fragment))
    return pairs


def _join_failures(layout, base, present, root):
    """Each join of the merge registry of a layout that its L0 lacks."""
    registry = (MERGES / f"{layout.id}.csv").as_posix()
    fix = (f"run MergeFuncs.java with {registry} on the program, then "
           f"tools/ghidra/export-l0.sh {layout.id}")
    try:
        joins = merges(layout.id, root)
    except KbError as error:
        return [Failure(registry, "syntax", str(error), "correct the registry")]
    if not joins or not {"funcs.csv", "function_tokens.csv"} <= present:
        return []
    sizes, bodies = _functions(base)
    failures = []
    for entry, fragment in joins:
        if entry not in sizes:
            failures.append(Failure(registry, f"{entry:08x}",
                                    "the entry is no function entry of the L0", fix))
        elif fragment in sizes:
            failures.append(Failure(registry, f"{fragment:08x}",
                                    f"the fragment of {entry:08x} is a function entry "
                                    "of the L0", fix))
        elif fragment not in bodies.get(entry, set()):
            failures.append(Failure(registry, f"{fragment:08x}",
                                    f"the fragment lies outside the body of {entry:08x}",
                                    fix))
    return failures


def inputs(root=repo.ROOT):
    """The files that the `l0` check reads: every file under `l0/`, the image
    catalog, the layouts, the configuration, the Ghidra pin, the export
    scripts, the census registries, and the join registries."""
    config = repo.config(root)
    found = {path.relative_to(root).as_posix()
             for path in (root / repo.L0).rglob("*") if path.is_file()}
    found.update(path.as_posix() for path in (repo.CATALOG, repo.HOMOLOGY, repo.CONFIG,
                                              repo.GHIDRA_PIN))
    found.update((repo.GHIDRA_SCRIPTS / name).as_posix() for name in config["l0"]["scripts"])
    found.update(settings["interp"] for settings in config["l0"].get("census", {}).values())
    found.update((MERGES / path.name).as_posix() for path in (root / MERGES).glob("*.csv"))
    found.update(preparation.inputs(root))
    return sorted(found)


def check_all(root=repo.ROOT, only=None):
    """The `l0` check over every layout, or over the layout ids in `only`."""
    cache_path, verified = _normal_cache(root)
    failures = []
    known = repo.layouts(root)
    for layout in known.values():
        if only is None or layout.id in only:
            failures += check_layout(layout, root, verified)
    base = root / repo.L0
    if only is None and base.is_dir():
        for path in sorted(base.iterdir()):
            if path.name not in known:
                failures.append(Failure(
                    f"{repo.L0}/{path.name}", "layout",
                    "the directory is not a layout of rom-images/homology.toml",
                    "remove it or declare the layout",
                ))
    if only is None and (root / MERGES).is_dir():
        for path in sorted((root / MERGES).glob("*.csv")):
            if path.stem not in known:
                failures.append(Failure(
                    (MERGES / path.name).as_posix(), "layout",
                    "the registry is not of a layout of rom-images/homology.toml",
                    "remove it or declare the layout",
                ))
    if only is None:
        for path in sorted((root / preparation.SEEDS).glob("*.toml")):
            if path.stem not in known:
                failures.append(Failure(
                    path.relative_to(root).as_posix(), "layout",
                    "the preparation registry names an unknown layout",
                    "declare its layout or remove the registry",
                ))
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(sorted(verified)))
    except OSError:
        pass
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export the L0 of one layout.")
    parser.add_argument("layout")
    parser.add_argument("--check", action="store_true",
                        help="export into a temporary directory and compare")
    parser.add_argument("--stage", help="keep the raw export in this directory")
    parser.add_argument("--from-stage",
                        help="normalize a raw export instead of running Ghidra")
    parser.add_argument("--jobs", type=int, default=1,
                        help="parallel headless sessions, each on a copy of the project")
    args = parser.parse_args(argv)
    try:
        same = export(args.layout, check=args.check, stage=args.stage,
                      from_stage=args.from_stage, workers=args.jobs)
    except KbError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.code
    if args.check:
        print(f"l0 {args.layout}: {'identical' if same else 'differs'}")
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
