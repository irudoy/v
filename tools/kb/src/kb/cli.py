"""The `kb` command line: `uv run kb <command>`."""

import argparse
import csv
import math
from pathlib import Path
import re
import subprocess
import sys

from kb import l0, repo
from kb.repo import KbError

# Checks active at the current transition stage, in execution order.
CHECKS = {"l0": l0.check_all}
LOCATION_RE = re.compile(r"(?:(?P<layout>[0-9a-z]{2,8}):)?(?:0x)?(?P<address>[0-9a-fA-F]{1,8})")


def tokens(text):
    """Output tokens as the specification counts them: UTF-8 bytes / 3."""
    return math.ceil(len(text.encode("utf-8")) / 3)


def fit(text, budget, narrower):
    """Cut text to its budget; the first line of a cut answer reads TRUNCATED."""
    if budget is None or tokens(text) <= budget:
        return text
    lines = text.splitlines(keepends=True)
    kept, used = [], 0
    limit = budget * 3 - 200
    for line in lines:
        size = len(line.encode("utf-8"))
        if used + size > limit:
            break
        kept.append(line)
        used += size
    header = (
        f"TRUNCATED: {len(kept)} of {len(lines)} lines shown; "
        f"{narrower} or --full shows the rest\n"
    )
    return header + "".join(kept)


def budget_of(args, command, root=repo.ROOT):
    if getattr(args, "full", False):
        return None
    if getattr(args, "budget", None):
        return args.budget
    return repo.config(root).get("budget", {}).get(command)


def parse_location(text, layout_option=None, root=repo.ROOT):
    match = LOCATION_RE.fullmatch(text.strip())
    if not match:
        raise KbError(f"{text!r} is not <layout>:<address>", code=2)
    layout_id = match.group("layout") or layout_option
    if not layout_id:
        raise KbError(f"{text!r} names no layout; use <layout>:<address> or --layout", code=2)
    if match.group("layout") and layout_option and layout_option != layout_id:
        raise KbError(f"{text!r} and --layout {layout_option} disagree", code=2)
    return repo.layout(layout_id, root), int(match.group("address"), 16)


def containing_function(layout, address, root=repo.ROOT):
    """The L0 function entry at or containing an instruction address."""
    base = root / repo.L0 / layout.id
    wanted = f"{address:08x}"
    with (base / "funcs.csv").open(newline="", encoding="utf-8") as source:
        if any(row["addr"] == wanted for row in csv.DictReader(source)):
            return wanted
    with (base / "function_tokens.csv").open(newline="", encoding="utf-8") as source:
        owners = sorted({row["func_addr"] for row in csv.DictReader(source)
                         if row["ins_addr"] == wanted})
    if not owners:
        raise KbError(f"{layout.id}:{wanted} is not an instruction of an L0 function", code=5)
    return owners[0]


def command_code(args, root=repo.ROOT):
    layout, address = parse_location(args.ref, args.layout, root)
    entry = containing_function(layout, address, root)
    command = [str(root / "tools/ghidra/decompile.sh"), "-r", layout.image]
    if args.listing:
        command.append("-l")
    if args.force:
        command.append("-f")
    command.append(entry)
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        raise KbError(result.stderr.strip() or "decompile.sh failed", code=6)
    paths = [Path(line) for line in result.stdout.splitlines() if line.strip()]
    parts = [f"{layout.id}:{entry}  fn  [l0] Ghidra {repo.ghidra_version(root)}, "
             f"program of {layout.image}"]
    if entry != f"{address:08x}":
        parts.append(f"  {layout.id}:{address:08x} lies in the body of {layout.id}:{entry}")
    for path in paths:
        parts.append(f"--- {path.name}")
        parts.append(path.read_text(encoding="utf-8").rstrip("\n"))
    text = "\n".join(parts) + "\n"
    sys.stdout.write(fit(text, budget_of(args, "code", root),
                         f"kb code {layout.id}:{entry} --budget <tokens>"))
    return 0


def command_check(args, root=repo.ROOT):
    selected = args.only or list(CHECKS)
    unknown = sorted(set(selected) - set(CHECKS))
    if unknown:
        raise KbError(f"unknown or inactive checks {unknown}; active: {', '.join(CHECKS)}", code=2)
    failed = 0
    for name in selected:
        failures = CHECKS[name](root)
        for failure in failures:
            print(f"{name}: {failure}")
        print(f"check {name}: {'FAIL ' + str(len(failures)) if failures else 'PASS'}")
        failed += len(failures)
    return 1 if failed else 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="kb", description="Knowledge model and entry point (tools/kb/SPEC.md)."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="run the checks of the current stage")
    check.add_argument("--changed", action="store_true",
                       help="run the checks whose inputs changed (every active check)")
    check.add_argument("--only", action="append", help="run one check; repeatable")
    check.set_defaults(handler=command_check)

    code = commands.add_parser("code", help="decompilation or listing of a function")
    code.add_argument("ref", help="<layout>:<address>")
    code.add_argument("--layout")
    code.add_argument("-l", "--listing", action="store_true", help="add the listing")
    code.add_argument("-f", "--force", action="store_true", help="rerun Ghidra")
    code.add_argument("--budget", type=int)
    code.add_argument("--full", action="store_true")
    code.set_defaults(handler=command_code)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except KbError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
