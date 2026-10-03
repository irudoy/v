"""On-demand code through the primary read-only Ghidra runner.

Verified output files and their cache key replace the accepted cache together.
A failed preparation, decompiler, requested output, or promotion preserves it.
"""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from kb import repo
from kb.repo import KbError
from kb import ghidra_preparation as preparation
from tools.ghidra import program_name


@contextmanager
def cache_lock(target):
    """Serialize primary requests for one local output directory."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with (target.parent / f".{target.name}.decompile.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def primary_result(command, root):
    """Keep the primary process log whenever output acceptance fails."""
    with tempfile.NamedTemporaryFile(prefix="ghidra-decompile-", suffix=".log",
                                     mode="w", delete=False) as output:
        log = Path(output.name)
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        except OSError as error:
            output.write(str(error) + "\n")
            print(f"headless Ghidra log: {log}", file=sys.stderr)
            raise
        output.write(result.stdout + result.stderr)
    try:
        yield result
    except BaseException:
        print(f"headless Ghidra log: {log}", file=sys.stderr)
        raise
    else:
        log.unlink()


def valid_output(path, entry):
    try:
        text = path.read_text()
    except (OSError, UnicodeError):
        return False
    return (text.startswith("// ") and f" @ {entry}  size=" in text.splitlines()[0]
            and "// decompile failed:" not in text)


def decompile(rom_key, addresses, *, project_dir=None, project_name="vq-hr",
              program="", outdir=None, listings=False, force=False, root=repo.ROOT):
    """Return checked output paths, accepting nothing on a failed primary run."""
    root = Path(root)
    catalog = repo.images(root)
    if rom_key not in catalog:
        raise KbError(f"unknown registered ROM {rom_key!r}", code=2)
    image = catalog[rom_key]
    actual = hashlib.sha256(image.path.read_bytes()).hexdigest()
    if actual != image.sha256:
        raise KbError(f"registered {rom_key} image differs from its catalog digest")
    project_dir = project_dir or os.environ.get(
        "GHIDRA_PROJECT_DIR", os.path.expanduser("~/tools/ghidra-projects"))
    program = program or program_name.resolve(
        rom_key, image.path.name, program_name.read_index(project_dir, project_name))
    values = tuple(int(str(address).removeprefix("0x"), 16) for address in addresses)
    if not values or any(value < 0 or value > 0xffffffff for value in values):
        raise KbError("requested entries must be 32-bit hexadecimal addresses", code=2)
    entries = tuple(dict.fromkeys(f"{value:08x}" for value in values))
    target = Path(outdir or Path(project_dir) / f"export-{rom_key}").expanduser().absolute()
    if target.is_symlink() or target.exists() and not target.is_dir():
        raise KbError(f"{target}: code cache must be a nonsymlink directory")
    layout = next((item for item in repo.layouts(root).values() if item.image == rom_key), None)
    prepared = preparation.plan(layout.id, root) if layout else None
    key = program_name.cache_key(rom_key, program, actual, root)
    wanted = [name for entry in entries for name in
              ([f"decomp_{entry}.c", f"funclisting_{entry}.txt"] if listings
               else [f"decomp_{entry}.c"])]
    with cache_lock(target):
        try:
            metadata = json.loads((target / ".decompile-files.json").read_text())
            old_key = (target / ".decompile-key").read_text().strip()
        except (OSError, ValueError):
            metadata, old_key = {}, None
        if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
            metadata = {}
        digests = metadata.get("files", {}) if metadata.get("key") == key and old_key == key else {}
        if not isinstance(digests, dict):
            digests = {}
        missing = [name for name in wanted if force or name not in digests
                   or not valid_output(target / name, name.split("_")[1].split(".")[0])
                   or repo.sha256_file(target / name) != digests[name]]
        if not missing:
            return [target / name for name in wanted]
        with tempfile.TemporaryDirectory(prefix="ghidra-decompile-stage-", dir=target.parent) as temporary:
            stage = Path(temporary)
            wire, receipt = stage / "preparation.tsv", stage / "preparation.json"
            if prepared is not None:
                preparation.write_plan(prepared, wire, root)
            arguments = ["-postScript", "ProgramSha256.java", str(stage / "program.sha256")]
            decomp = [name[len("decomp_"):-2] for name in missing if name.startswith("decomp_")]
            listing = [name[len("funclisting_"):-4] for name in missing if name.startswith("funclisting_")]
            if decomp:
                arguments += ["-postScript", "DecompileFuncs.java", str(stage), *decomp]
            if listing:
                arguments += ["-postScript", "DumpFuncListing.java", str(stage), *listing]
            arguments = preparation.session(prepared, wire, receipt, arguments,
                                            ["program.sha256", *missing])
            command = [str(root / repo.GHIDRA_PIN), str(project_dir), project_name,
                       "-process", program, "-noanalysis", "-readOnly",
                       "-scriptPath", str(root / repo.GHIDRA_SCRIPTS), *arguments]
            with primary_result(command, root) as result:
                if result.returncode != 0:
                    raise KbError(f"headless Ghidra failed: {result.stderr or result.stdout}")
                if not (stage / "program.sha256").is_file():
                    raise KbError(f"program {program} has no recorded SHA-256; {result.stdout}")
                if (stage / "program.sha256").read_text().strip() != actual:
                    raise KbError(f"program {program} holds another image")
                if prepared is not None:
                    preparation.verify_receipt(
                        prepared, receipt, ["program.sha256", *missing], wire=wire, root=root)
                for name in missing:
                    entry = name.split("_")[1].split(".")[0]
                    if not valid_output(stage / name, entry):
                        raise KbError(f"requested output {name} is absent or unsuccessful; {result.stdout}")
                if program_name.cache_key(rom_key, program, actual, root) != key:
                    raise KbError("the primary input key changed during decompilation")
                replacement = stage / "cache"
                if target.is_dir():
                    shutil.copytree(target, replacement)
                else:
                    replacement.mkdir()
                if old_key != key:
                    for pattern in ("decomp_*.c", "funclisting_*.txt"):
                        for path in replacement.glob(pattern):
                            path.unlink()
                    digests = {}
                for name in missing:
                    shutil.copy2(stage / name, replacement / name)
                    digests[name] = repo.sha256_file(stage / name)
                (replacement / ".decompile-key").write_text(key + "\n")
                (replacement / ".decompile-files.json").write_text(json.dumps(
                    {"schema_version": 1, "key": key, "files": digests}, sort_keys=True) + "\n")
                preparation.promote_directory(replacement, target)
        return [target / name for name in wanted]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-r", dest="rom", default="JK08A")
    parser.add_argument("-p", dest="program", default="")
    parser.add_argument("-o", dest="outdir")
    parser.add_argument("-l", dest="listings", action="store_true")
    parser.add_argument("-f", dest="force", action="store_true")
    parser.add_argument("addresses", nargs="+")
    args = parser.parse_args(argv)
    try:
        paths = decompile(args.rom, args.addresses, program=args.program, outdir=args.outdir,
                          listings=args.listings, force=args.force,
                          project_name=os.environ.get("GHIDRA_PROJECT_NAME", "vq-hr"))
        for path in paths:
            print(path)
        return 0
    except (KbError, LookupError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return getattr(error, "code", 1)


if __name__ == "__main__":
    sys.exit(main())
