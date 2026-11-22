"""Reviewed, exact-image preparation shared by export and on-demand code.

Plans bind registered seed entries, current ROM bytes, fragment joins, and the
primary scripts. Preparation never saves a program or recovers outside regions.
A sealed receipt binds the outputs of one independently prepared session.
"""

import csv
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import tomllib
import uuid

from kb import repo
from kb.repo import KbError

SEEDS = Path("tools/ghidra/seeds")
MERGES = Path("tools/ghidra/merges")
SCRIPTS = ("PrepareProgram.java", "RecoverFuncs.java", "AnalyzeFuncs.java", "MergeFuncs.java")
OUTPUT_SCRIPTS = (
    "ProgramSha256.java", "ExportGraph.java", "ExportXrefs.java",
    "ExportFunctionSignatures.java", "ExportFunctionTokens.java", "ResolveAccessors.java",
    "DecompileFuncs.java", "DumpFuncListing.java",
)
BUILDERS = ("tools/kb/src/kb/ghidra_preparation.py",
            "tools/ghidra/preparation.py", "tools/ghidra/decompile.py",
            "tools/ghidra/decompile.sh", "tools/ghidra/program_name.py",
            "tools/ghidra/export-l0.sh", "tools/kb/src/kb/l0.py")
ADDRESS = re.compile(r"[0-9a-f]{8}")
DIGEST = re.compile(r"[0-9a-f]{64}")
CONFIG_INPUT = f"{repo.CONFIG.as_posix()}#l0"


@dataclass(frozen=True)
class Fragment:
    entry: int
    instructions: int
    instruction_sha256: str


@dataclass(frozen=True)
class Seed:
    entry: int
    sites: tuple[int, ...]
    bytes: int
    instructions: int
    ranges: int
    instruction_sha256: str
    fragments: tuple[Fragment, ...]


@dataclass(frozen=True)
class Dispatch:
    entry: int
    site: int
    table: int
    targets: tuple[int, ...]
    former_entry: int
    former_end: int
    former_instruction_sha256: str
    ranges: tuple[tuple[int, int], ...]
    instruction_sha256: str

    @property
    def table_end(self):
        return self.table + 4 * len(self.targets)

    @property
    def bytes(self):
        return sum(end - start for start, end in self.ranges)

    @property
    def sites(self):
        return frozenset(site for start, end in self.ranges for site in range(start, end, 2))


@dataclass(frozen=True)
class DataTable:
    start: int
    end: int
    element: str
    sha256: str
    former_entry: int
    former_end: int
    former_instruction_sha256: str


@dataclass(frozen=True)
class Plan:
    layout: str
    image: str
    image_sha256: str
    image_size: int
    seeds: tuple[Seed, ...]
    pins: tuple[tuple[int, bytes], ...]
    references: tuple[tuple[int, int, int, str], ...]
    joins: tuple[tuple[int, int], ...]
    forbidden_entries: tuple[int, ...]
    inputs: dict[str, str]
    dispatches: tuple[Dispatch, ...] = ()
    data_tables: tuple[DataTable, ...] = ()
    # {input path: file}: the inputs whose bytes a session reads from another
    # file than the tracked one, as the registry that a proposed change renders.
    sources: dict[str, Path] = field(default_factory=dict)

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.inputs, sort_keys=True).encode()).hexdigest()

    @property
    def manifest(self):
        return {"schema_version": 1, "inputs": self.inputs}


def _keys(row, wanted, where):
    if not isinstance(row, dict) or set(row) != set(wanted):
        raise KbError(f"{where}: keys must be {', '.join(wanted)}")


def _address(value, where):
    if not isinstance(value, str) or ADDRESS.fullmatch(value) is None:
        raise KbError(f"{where}: expected eight lowercase hexadecimal digits")
    return int(value, 16)


def _digest(value, where):
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise KbError(f"{where}: expected a SHA-256 digest")
    return value


def _positive(value, where):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise KbError(f"{where}: expected a positive integer")
    return value


def _tables(value, where):
    if not isinstance(value, list) or not value or not all(isinstance(row, dict) for row in value):
        raise KbError(f"{where}: expected a nonempty array of tables")
    return value


def _addresses(values, where):
    if not isinstance(values, list):
        raise KbError(f"{where}: expected an address array")
    result = tuple(_address(value, where) for value in values)
    if len(set(result)) != len(result):
        raise KbError(f"{where}: duplicate address")
    return result


def _joins(layout, root):
    path = root / MERGES / f"{layout}.csv"
    if not path.is_file():
        raise KbError(f"{path}: a seed preparation requires a merge registry")
    lines = [line for line in path.read_text().splitlines() if line and not line.startswith("#")]
    reader = csv.reader(lines)
    if next(reader, None) != ["entry", "fragment", "note"]:
        raise KbError(f"{path}: expected entry,fragment,note")
    pairs, seen = [], set()
    for row in reader:
        if len(row) != 3 or not row[2].strip():
            raise KbError(f"{path}: expected reviewed entry,fragment,note")
        entry, fragment = (_address(value, str(path)) for value in row[:2])
        if entry == fragment or fragment in seen:
            raise KbError(f"{path}: a fragment joins one other entry")
        seen.add(fragment)
        pairs.append((entry, fragment))
    return tuple(pairs)


def _dispatches(rows, data, where):
    result = []
    for row in _tables(rows, where):
        _keys(row, ("entry", "site", "table", "targets", "former_entry", "former_end",
                    "former_instruction_sha256", "ranges", "instruction_sha256"), where)
        entry, site, table, former, former_end = (
            _address(row[key], where) for key in
            ("entry", "site", "table", "former_entry", "former_end"))
        targets = _addresses(row["targets"], where)
        if (not targets or len(targets) > 256 or table & 3 or former != table
                or not table + 4 * len(targets) < former_end <= len(data)
                or former_end & 1):
            raise KbError(f"{where}: invalid dispatch table or former body")
        former_sha = _digest(row["former_instruction_sha256"], where)
        if hashlib.sha256(data[former:former_end]).hexdigest() != former_sha:
            raise KbError(f"{where}: former dispatch body differs from the exact image")
        if not isinstance(row["ranges"], list) or not row["ranges"]:
            raise KbError(f"{where}: dispatch requires explicit code ranges")
        ranges = []
        for span in row["ranges"]:
            if not isinstance(span, list) or len(span) != 2:
                raise KbError(f"{where}: dispatch range requires start and exclusive end")
            start, end = (_address(value, where) for value in span)
            if (start & 1 or end & 1 or not start < end <= len(data)
                    or start < table + 4 * len(targets) and table < end
                    or ranges and start <= ranges[-1][1]):
                raise KbError(f"{where}: dispatch code ranges overlap data or each other")
            ranges.append((start, end))
        code = {at for start, end in ranges for at in range(start, end, 2)}
        if entry != ranges[0][0] or site not in code or any(target not in code for target in targets):
            raise KbError(f"{where}: dispatch entry, site and targets must lie in its code")
        if int.from_bytes(data[site:site + 2], "big") & 0xf0ff != 0x402b:
            raise KbError(f"{where}: dispatch requires an SH-2 register jump")
        actual = tuple(int.from_bytes(data[at:at + 4], "big")
                       for at in range(table, table + 4 * len(targets), 4))
        if actual != targets:
            raise KbError(f"{where}: dispatch targets differ from the exact image")
        instruction_sha = _digest(row["instruction_sha256"], where)
        if hashlib.sha256(b"".join(data[start:end] for start, end in ranges)).hexdigest() != instruction_sha:
            raise KbError(f"{where}: dispatch code differs from the exact image")
        result.append(Dispatch(entry, site, table, targets, former, former_end, former_sha,
                               tuple(ranges), instruction_sha))
    if len({item.entry for item in result}) != len(result):
        raise KbError(f"{where}: duplicate dispatch owner")
    for index, item in enumerate(result):
        for other in result[:index]:
            if (item.sites & other.sites
                    or item.table < other.table_end and other.table < item.table_end
                    or any(item.table <= site < item.table_end for site in other.sites)
                    or any(other.table <= site < other.table_end for site in item.sites)):
                raise KbError(f"{where}: dispatch contracts overlap")
    return tuple(result)


def _data_tables(rows, data, where):
    result = []
    for row in _tables(rows, where):
        _keys(row, ("start", "end", "element", "sha256", "former_entry", "former_end",
                    "former_instruction_sha256"), where)
        start, end, former, former_end = (
            _address(row[key], where) for key in ("start", "end", "former_entry", "former_end"))
        if (row["element"] != "s16" or any(at & 1 for at in (start, end, former, former_end))
                or not start <= former < former_end <= end <= len(data)):
            raise KbError(f"{where}: invalid signed-16 data table or former body")
        digest = _digest(row["sha256"], where)
        former_digest = _digest(row["former_instruction_sha256"], where)
        if hashlib.sha256(data[start:end]).hexdigest() != digest:
            raise KbError(f"{where}: data table differs from the exact image")
        if hashlib.sha256(data[former:former_end]).hexdigest() != former_digest:
            raise KbError(f"{where}: former data-table body differs from the exact image")
        item = DataTable(start, end, row["element"], digest, former, former_end, former_digest)
        if any(start < other.end and other.start < end for other in result):
            raise KbError(f"{where}: data tables overlap")
        result.append(item)
    return tuple(result)


def _config_bytes(root):
    """Canonical export settings; unrelated configuration is not an input."""
    settings = repo.config(root).get("l0")
    if not isinstance(settings, dict):
        raise KbError(f"{repo.CONFIG}: the output preparation requires [l0]")
    return (json.dumps(settings, sort_keys=True, separators=(",", ":")) + "\n").encode()


def execution_inputs(layout_id, root=repo.ROOT):
    """Actual output producers and the selected layout census inputs.

    These hashes prevent a kept output from receiving the current manifest
    after its producer or census contract changes. The executed producers
    remain bound even when the configured script list omits one of them.
    """
    root = Path(root)
    settings = repo.config(root).get("l0")
    if not isinstance(settings, dict):
        raise KbError(f"{repo.CONFIG}: the output preparation requires [l0]")
    scripts = settings.get("scripts")
    if (not isinstance(scripts, list) or not scripts
            or any(not isinstance(name, str) or Path(name).name != name
                   or not name.endswith(".java") for name in scripts)):
        raise KbError(f"{repo.CONFIG}: l0.scripts must contain local Java script names")
    census = settings.get("census", {}).get(layout_id)
    if not isinstance(census, dict) or not isinstance(census.get("interp"), str):
        raise KbError(f"{repo.CONFIG}: [l0.census.{layout_id}].interp is missing")
    interp = Path(census["interp"])
    if interp.is_absolute() or ".." in interp.parts or not interp.parts:
        raise KbError(f"{repo.CONFIG}: the census registry must be a repository path")
    found = {interp}
    found.update(repo.GHIDRA_SCRIPTS / name for name in set(scripts) | set(OUTPUT_SCRIPTS))
    for path in found:
        if not (root / path).is_file():
            raise KbError(f"{path}: a primary output preparation input is missing")
    return tuple(sorted(found))


def plan(layout_id, root=repo.ROOT, registry=None, *, layout=None):
    """The reviewed primary preparation, or None for an unconfigured layout.

    This read-only API performs no graph access, enrollment, or Ghidra call.
    Seed.fragments identify the reviewed former entries for owner integration.
    `registry` is a file whose bytes take the place of the census registry of
    the layout: the registry that a proposed change renders, which the plan
    binds as that input once the change writes the same bytes.
    """
    root = Path(root)
    layout = layout or repo.layout(layout_id, root)
    path = root / SEEDS / f"{layout_id}.toml"
    if not path.is_file():
        return None
    try:
        document = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise KbError(f"{path}: {error}") from error
    _keys(document, ("schema_version", "layout", "image", "image_sha256", "image_size",
                     "forbidden_entries", "seed", "pin", "reference")
          + tuple(key for key in ("dispatch", "data_table") if key in document), str(path))
    if document["schema_version"] != 1 or isinstance(document["schema_version"], bool):
        raise KbError(f"{path}: unsupported preparation schema")
    if (document["layout"], document["image"]) != (layout.id, layout.image):
        raise KbError(f"{path}: preparation names another layout or image")
    image = repo.images(root)[layout.image]
    expected_sha = _digest(document["image_sha256"], str(path))
    data = image.path.read_bytes()
    size = _positive(document["image_size"], str(path))
    if (expected_sha != image.sha256 or hashlib.sha256(data).hexdigest() != expected_sha
            or len(data) != size):
        raise KbError(f"{path}: preparation differs from the registered image bytes")
    pins = []
    for row in _tables(document["pin"], str(path)):
        _keys(row, ("address", "bytes"), str(path))
        address = _address(row["address"], str(path))
        value = row["bytes"]
        if (not isinstance(value, str) or re.fullmatch(r"(?:[0-9a-f]{2})+", value) is None):
            raise KbError(f"{path}: pin bytes must be nonempty lowercase hexadecimal")
        value = bytes.fromhex(value)
        if data[address:address + len(value)] != value:
            raise KbError(f"{path}: pin {address:08x} differs from the exact image")
        pins.append((address, value))
    if len({address for address, _ in pins}) != len(pins):
        raise KbError(f"{path}: duplicate pin")
    seeds = []
    for row in _tables(document["seed"], str(path)):
        _keys(row, ("entry", "sites", "bytes", "instructions", "ranges", "instruction_sha256")
              + (("fragment",) if isinstance(row, dict) and "fragment" in row else ()),
              str(path))
        entry = _address(row["entry"], str(path))
        sites = _addresses(row["sites"], str(path))
        if not sites or entry & 1 or entry >= size or any(site & 1 or site >= size for site in sites):
            raise KbError(f"{path}: seed and sites must identify aligned instructions")
        if not any(address == entry and len(value) >= 2 for address, value in pins):
            raise KbError(f"{path}: seed {entry:08x} lacks an exact prologue pin")
        # A seed without fragments joins nothing; one with them names each.
        fragments = []
        for fragment in (_tables(row["fragment"], str(path)) if "fragment" in row else ()):
            _keys(fragment, ("entry", "instructions", "instruction_sha256"), str(path))
            fragments.append(Fragment(_address(fragment["entry"], str(path)),
                                      _positive(fragment["instructions"], str(path)),
                                      _digest(fragment["instruction_sha256"], str(path))))
        if len({f.entry for f in fragments}) != len(fragments):
            raise KbError(f"{path}: seed requires unique reviewed fragments")
        seeds.append(Seed(entry, sites, _positive(row["bytes"], str(path)),
                          _positive(row["instructions"], str(path)),
                          _positive(row["ranges"], str(path)),
                          _digest(row["instruction_sha256"], str(path)), tuple(fragments)))
    if not seeds or len({s.entry for s in seeds}) != len(seeds):
        raise KbError(f"{path}: preparation requires unique reviewed seeds")
    joins = _joins(layout_id, root)
    for seed in seeds:
        for fragment in seed.fragments:
            if (seed.entry, fragment.entry) not in joins:
                raise KbError(f"{path}: fragment {fragment.entry:08x} lacks a reviewed join")
    seed_entries = {seed.entry for seed in seeds}
    fragment_entries = [fragment.entry for seed in seeds for fragment in seed.fragments]
    if (len(set(fragment_entries)) != len(fragment_entries)
            or seed_entries & set(fragment_entries)
            or any(seed.bytes != seed.instructions * 2 for seed in seeds)):
        raise KbError(f"{path}: conflicting seed/fragment entries or instruction size")
    references = []
    for row in _tables(document["reference"], str(path)):
        _keys(row, ("owner", "site", "target", "type"), str(path))
        if row["type"] not in ("read", "write", "call"):
            raise KbError(f"{path}: reference type must be read, write, or call")
        owner, site, target = (_address(row[key], str(path)) for key in ("owner", "site", "target"))
        seed = next((s for s in seeds if s.entry == owner), None)
        if seed is None or site not in seed.sites:
            raise KbError(f"{path}: reference has no reviewed seed/site owner")
        references.append((owner, site, target, row["type"]))
    if len(set(references)) != len(references):
        raise KbError(f"{path}: duplicate reviewed reference")
    # A seed entry is reached through a pinned pointer word, or through a
    # reviewed call of another seed: the function that the analysis of that
    # seed creates at its call target.
    for seed in seeds:
        if not (any(value == seed.entry.to_bytes(4, "big") for _, value in pins)
                or any(target == seed.entry and type_ == "call" and owner != seed.entry
                       for owner, _, target, type_ in references)):
            raise KbError(f"{path}: seed {seed.entry:08x} lacks an exact entry-pointer pin "
                          "and a reviewed call of another seed")
    forbidden = _addresses(document["forbidden_entries"], str(path))
    if set(forbidden) & {seed.entry for seed in seeds}:
        raise KbError(f"{path}: a seed is forbidden")
    dispatches = _dispatches(document["dispatch"], data, str(path)) if "dispatch" in document else ()
    if any(item.entry in seed_entries | set(fragment_entries) | set(forbidden)
           or item.former_entry in seed_entries | set(fragment_entries) | set(forbidden)
           for item in dispatches):
        raise KbError(f"{path}: dispatch conflicts with a seed, join or forbidden entry")
    data_tables = _data_tables(document["data_table"], data, str(path)) if "data_table" in document else ()
    known_code = seed_entries | set(fragment_entries) | set(forbidden)
    known_code.update(site for seed in seeds for site in seed.sites)
    known_code.update(site for pair in joins for site in pair)
    for item in data_tables:
        if (any(item.start <= site < item.end for site in known_code)
                or any(any(item.start <= site < item.end for site in dispatch.sites)
                       or item.start < dispatch.table_end and dispatch.table < item.end
                       for dispatch in dispatches)):
            raise KbError(f"{path}: data table conflicts with another preparation contract")
    paths = [path.relative_to(root), MERGES / f"{layout_id}.csv", repo.CATALOG, repo.HOMOLOGY,
             repo.GHIDRA_PIN, *(Path(path) for path in BUILDERS),
             *(repo.GHIDRA_SCRIPTS / name for name in SCRIPTS),
             *execution_inputs(layout_id, root)]
    inputs = {path.as_posix(): repo.sha256_file(root / path) for path in paths}
    inputs[CONFIG_INPUT] = hashlib.sha256(_config_bytes(root)).hexdigest()
    sources = {}
    if registry is not None:
        interp = repo.config(root)["l0"]["census"][layout_id]["interp"]
        inputs[interp] = repo.sha256_file(registry)
        sources[interp] = Path(registry).resolve()
    return Plan(layout.id, layout.image, expected_sha, size, tuple(seeds), tuple(pins),
                tuple(references), joins, forbidden, dict(sorted(inputs.items())), dispatches,
                data_tables, sources)


def _wire_text(prepared, root, run_id, wire):
    """The complete session contract; only its run identity varies."""
    lines = [f"schema\t1", f"layout\t{prepared.layout}", f"digest\t{prepared.digest}",
             f"image_sha256\t{prepared.image_sha256}", f"image_size\t{prepared.image_size}",
             f"run_id\t{run_id}"]
    for path, digest in prepared.inputs.items():
        absolute = str(Path(wire).with_suffix(".l0.json").resolve() if path == CONFIG_INPUT
                       else prepared.sources.get(path) or Path(root).resolve() / path)
        if any(char in absolute for char in "\t\r\n"):
            raise KbError("preparation paths cannot contain tabs or line breaks")
        lines.append(f"input\t{path}\t{digest}\t{absolute}")
    for seed in prepared.seeds:
        lines.append(f"seed\t{seed.entry:08x}\t{seed.bytes}\t{seed.instructions}\t"
                     f"{seed.ranges}\t{seed.instruction_sha256}")
        lines += [f"site\t{seed.entry:08x}\t{site:08x}" for site in seed.sites]
        lines += [f"fragment\t{seed.entry:08x}\t{f.entry:08x}\t{f.instructions}\t"
                  f"{f.instruction_sha256}" for f in seed.fragments]
    lines += [f"pin\t{address:08x}\t{value.hex()}" for address, value in prepared.pins]
    lines += [f"reference\t{owner:08x}\t{site:08x}\t{target:08x}\t{type_}"
              for owner, site, target, type_ in prepared.references]
    lines += [f"join\t{entry:08x}\t{fragment:08x}" for entry, fragment in prepared.joins]
    lines += [f"forbidden\t{entry:08x}" for entry in prepared.forbidden_entries]
    for item in prepared.dispatches:
        lines.append(f"dispatch\t{item.entry:08x}\t{item.site:08x}\t{item.table:08x}\t"
                     f"{item.table_end:08x}\t{item.former_entry:08x}\t{item.former_end:08x}\t"
                     f"{item.former_instruction_sha256}\t{item.bytes}\t{len(item.sites)}\t"
                     f"{len(item.ranges)}\t{item.instruction_sha256}")
        lines += [f"dispatch_range\t{item.entry:08x}\t{start:08x}\t{end:08x}"
                  for start, end in item.ranges]
        lines += [f"dispatch_target\t{item.entry:08x}\t{target:08x}" for target in item.targets]
    for item in prepared.data_tables:
        lines.append(f"data_table\t{item.start:08x}\t{item.end:08x}\t{item.element}\t{item.sha256}\t"
                     f"{item.former_entry:08x}\t{item.former_end:08x}\t{item.former_instruction_sha256}")
    lines.append(f"merges\t{Path(root).resolve() / MERGES / (prepared.layout + '.csv')}")
    return "\n".join(lines) + "\n"


def write_plan(prepared, target, root=repo.ROOT):
    """Write a plan and checked export-settings snapshot for the primary script."""
    data = _config_bytes(root)
    if hashlib.sha256(data).hexdigest() != prepared.inputs.get(CONFIG_INPUT):
        raise KbError(f"{target}: the preparation export configuration is stale")
    Path(target).with_suffix(".l0.json").write_bytes(data)
    Path(target).write_text(_wire_text(prepared, root, uuid.uuid4().hex, target))


def verify_wire(prepared, wire, root=repo.ROOT):
    """Refuse a kept plan whose contract differs despite current input digests."""
    try:
        text = Path(wire).read_text()
    except OSError as error:
        raise KbError(f"{wire}: the session preparation plan is missing") from error
    data = _config_bytes(root)
    if hashlib.sha256(data).hexdigest() != prepared.inputs.get(CONFIG_INPUT):
        raise KbError(f"{wire}: the preparation export configuration is stale")
    try:
        snapshot = Path(wire).with_suffix(".l0.json").read_bytes()
    except OSError as error:
        raise KbError(f"{wire}: the preparation configuration snapshot is missing") from error
    if snapshot != data:
        raise KbError(f"{wire}: the preparation configuration snapshot changed")
    ids = [line.split("\t", 1)[1] for line in text.splitlines() if line.startswith("run_id\t")]
    if (len(ids) != 1 or re.fullmatch(r"[0-9a-f]{32}", ids[0]) is None
            or text != _wire_text(prepared, root, ids[0], wire)):
        raise KbError(f"{wire}: the session preparation contract is stale or changed")


def session(prepared, wire, receipt, arguments, outputs):
    """Prepare and seal one primary session around its unchanged output scripts."""
    if prepared is None:
        return arguments
    return ["-postScript", "PrepareProgram.java", "prepare", str(wire), str(receipt),
            *outputs, *arguments, "-postScript", "PrepareProgram.java", "seal", str(wire),
            str(receipt), *outputs]


def verify_receipt(prepared, path, outputs, *, wire=None, root=repo.ROOT):
    """Refuse an unsealed, stale, partial, or modified session result."""
    try:
        receipt = json.loads(Path(path).read_text())
    except (OSError, ValueError) as error:
        raise KbError(f"{path}: preparation receipt is missing or invalid") from error
    if not isinstance(receipt, dict):
        raise KbError(f"{path}: preparation receipt is not an object")
    if (receipt.get("schema_version") != 1 or receipt.get("complete") is not True
            or receipt.get("preserved") is not True or receipt.get("digest") != prepared.digest
            or receipt.get("image_sha256") != prepared.image_sha256
            or receipt.get("current_sha256") != prepared.image_sha256
            or receipt.get("layout") != prepared.layout):
        raise KbError(f"{path}: preparation receipt is stale or unsuccessful")
    if wire is not None:
        verify_wire(prepared, wire, root)
        if receipt.get("wire_sha256") != repo.sha256_file(wire):
            raise KbError(f"{path}: preparation receipt belongs to another session")
    recorded = receipt.get("outputs")
    if not isinstance(recorded, dict) or set(recorded) != set(outputs):
        raise KbError(f"{path}: preparation receipt has another output set")
    for name, digest in recorded.items():
        target = Path(path).parent / name
        if not target.is_file() or repo.sha256_file(target) != digest:
            raise KbError(f"{path}: sealed output {name} is missing or changed")
    return receipt


def verify_stage(prepared, stage, groups, root=repo.ROOT):
    """Verify every independently prepared core or census session of a raw stage.

    Group numbering matches the primary export session order. No accepted
    target is changed, and stale stages cannot acquire current input hashes.
    """
    if prepared is None:
        return
    stage = Path(stage)
    for number, outputs in enumerate(groups, 1):
        verify_receipt(prepared, stage / f"preparation-{number}.json", outputs,
                       wire=stage / f"preparation-{number}.tsv", root=root)


def check_exports(prepared, directory, root=repo.ROOT):
    """Check exact seed bodies, cited owners, direct references, and entry limits."""
    def records(name):
        with (Path(directory) / name).open(newline="") as source:
            return list(csv.DictReader(source))
    data = repo.images(root)[prepared.image].path.read_bytes()
    if hashlib.sha256(data).hexdigest() != prepared.image_sha256:
        raise KbError("prepared export belongs to changed image bytes")
    funcs = {int(row["addr"], 16) for row in records("funcs.csv")}
    if set(prepared.forbidden_entries) & funcs:
        raise KbError("prepared export contains an unreviewed outside-function entry")
    signatures = {int(row["addr"], 16): row for row in records("function_signatures.csv")}
    bodies, holders = {}, {}
    for row in records("function_tokens.csv"):
        owner, site = int(row["func_addr"], 16), int(row["ins_addr"], 16)
        bodies.setdefault(owner, set()).add(site)
        holders.setdefault(site, set()).add(owner)
    for seed in prepared.seeds:
        row = signatures.get(seed.entry, {})
        if (seed.entry not in funcs or row.get("exact_sha256") != seed.instruction_sha256
                or row.get("size") != str(seed.bytes)
                or row.get("instructions") != str(seed.instructions)
                or len(bodies.get(seed.entry, set())) != seed.instructions
                or not {seed.entry, *seed.sites} <= bodies.get(seed.entry, set())):
            raise KbError(f"prepared export lacks the reviewed body of {seed.entry:08x}")
        body = sorted(bodies[seed.entry])
        if any(holders.get(site) != {seed.entry} for site in body):
            raise KbError(f"prepared export has overlapping owners for {seed.entry:08x}")
        ranges = sum(index == 0 or site != body[index - 1] + 2
                     for index, site in enumerate(body))
        exact = hashlib.sha256(b"".join(data[site:site + 2] for site in body)).hexdigest()
        if ranges != seed.ranges or exact != seed.instruction_sha256:
            raise KbError(f"prepared instruction sites differ for {seed.entry:08x}")
    for entry, fragment in prepared.joins:
        if entry not in funcs or fragment in funcs or fragment not in bodies.get(entry, set()):
            raise KbError(f"prepared export lacks the reviewed join {entry:08x}/{fragment:08x}")
    for item in prepared.dispatches:
        row = signatures.get(item.entry, {})
        if (item.entry not in funcs or item.former_entry in funcs
                or row.get("exact_sha256") != item.instruction_sha256
                or row.get("size") != str(item.bytes)
                or row.get("instructions") != str(len(item.sites))
                or bodies.get(item.entry) != item.sites
                or any(holders.get(site) != {item.entry} for site in item.sites)
                or any(site in holders for site in range(item.table, item.table_end, 2))):
            raise KbError(f"prepared export lacks the reviewed dispatch body {item.entry:08x}")
    for item in prepared.data_tables:
        if (any(item.start <= entry < item.end for entry in funcs)
                or any(item.start <= site < item.end for site in holders)):
            raise KbError(f"prepared export retains executable data table at {item.start:08x}")
    references = {(int(row["func_addr"], 16), int(row["ins_addr"], 16),
                   int(row["ref_addr"], 16), row["ref_type"])
                  for row in records("function_references.csv")}
    for owner, site, target, type_ in prepared.references:
        if not any((owner, site, target) == row[:3] and type_ in row[3] for row in references):
            raise KbError(f"prepared export lacks {type_} at {site:08x}")
    for item in prepared.dispatches:
        if any((item.entry, item.site, target, "computed_jump") not in references
               for target in item.targets):
            raise KbError(f"prepared export lacks computed dispatch flow at {item.site:08x}")


def promote_directory(source, target):
    """Replace a verified directory, restoring the accepted one on rename failure.

    The backup stays on the same filesystem until the replacement succeeds.
    This is an exception rollback, not a multi-system or crash transaction.
    """
    source, target = Path(source), Path(target)
    if target.is_symlink():
        raise KbError(f"{target}: refusing a symlink output target")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{target.name}-promote-", dir=target.parent))
    replacement, backup = tmp / "replacement", tmp / "accepted"
    keep_backup = False
    try:
        shutil.copytree(source, replacement)
        had_target = target.exists()
        if had_target:
            target.rename(backup)
        try:
            replacement.rename(target)
        except BaseException as failure:
            if had_target:
                try:
                    backup.rename(target)
                except OSError as rollback:
                    keep_backup = True
                    raise KbError(f"promotion failed: {failure}; restore failed: {rollback}; "
                                  f"accepted outputs remain at {backup}") from rollback
            raise
    finally:
        if not keep_backup:
            shutil.rmtree(tmp)


def inputs(root=repo.ROOT):
    """Tracked inputs of configured preparation plans and registry validation."""
    found = set()
    known = repo.layouts(root)
    for path in sorted((Path(root) / SEEDS).glob("*.toml")):
        if path.stem not in known:
            raise KbError(f"{path}: preparation registry names an unknown layout")
        found.update(repo.CONFIG.as_posix() if key == CONFIG_INPUT else key
                     for key in plan(path.stem, root).inputs)
    return sorted(found)
