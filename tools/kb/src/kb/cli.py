"""The `kb` command line: `uv run kb <command>`."""

import argparse
from contextlib import redirect_stdout
from functools import wraps
import csv
import io
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib

from kb import (answer, catalog, checks, compile, family, fingerprint, graph, guard, instance, l0, lock, passes, project,
                read, reader, refs, repo, sites, spec, store, suggest, vocab, write)
from kb.answer import fit
from kb.repo import KbError


def _model_check(name, table=checks.CHECKS):
    def run(root):
        return [f"{issue.path}: {issue.subject}: {issue.message}"
                for issue in table[name](compile.cached(root))]
    return run


# Supported checks, in execution order.
CHECKS = {"l0": l0.check_all, "sites": sites.check,
          **{name: _model_check(name) for name in checks.CHECKS},
          "projections": project.check, "guard": guard.check}
# Reports of a check that do not fail it.
NOTES = {name: _model_check(name, checks.NOTES) for name in checks.NOTES}
LOCATION_RE = re.compile(r"(?:(?P<layout>[0-9a-z]{2,8}):)?(?:0x)?(?P<address>[0-9a-fA-F]{1,8})")


def budget_of(args, command, root=repo.ROOT):
    if getattr(args, "full", False):
        return None
    if getattr(args, "budget", None):
        return args.budget
    return repo.config(root).get("budget", {}).get(command)


def _source_read(command):
    """Keep source-only answers coherent and publish only a checked result."""
    @wraps(command)
    def run(args,root=repo.ROOT):
        with lock.held(root):
            before=fingerprint.compute(root)
            output=io.StringIO()
            with redirect_stdout(output):
                code=command(args,root)
            if fingerprint.compute(root)!=before:
                raise KbError('the source fingerprint changes during the isolated read',code=6)
            text=output.getvalue()
        sys.stdout.write(text)
        return code
    return run


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
    wanted = f"{address:08x}"
    with (root / repo.L0 / layout.id / "funcs.csv").open(newline="", encoding="utf-8") as source:
        if any(row["addr"] == wanted for row in csv.DictReader(source)):
            return wanted
    owners = sorted({entry for entry, _, _ in read.instructions_at(layout.id, address, root)})
    if not owners:
        raise KbError(f"{layout.id}:{wanted} is not an instruction of an L0 function", code=5)
    return f"{owners[0]:08x}"


def code_target(args, root=repo.ROOT,held=False):
    """The layout and the address that `kb code` shows, with the reference of
    their symbol: a location of the form `<layout>:<address>` as it stands,
    or else the function symbol that the reference names on `--layout`, or
    for a meaning on its home layout."""
    if refs.LOCATION.fullmatch(args.ref.strip()):
        return (*parse_location(args.ref, args.layout, root), None)
    with reader.graph_session(root,args.no_sync,held=held) as session:
        ref = refs.resolve(session, args.ref, args.layout, root)
        if ref.kind == "meaning" and args.layout is None and ref.node.get("home"):
            ref = refs.resolve(session, args.ref, ref.node["home"], root)
    if ref.kind == "location":
        return repo.layout(ref.layout, root), ref.address, None
    if ref.kind == "meaning" and ref.node["kind"] == "fn":
        raise KbError(f"{ref.text} has no symbol on {ref.layout or 'its home layout'}", code=5)
    if ref.kind != "symbol" or ref.node["kind"] != "fn":
        raise KbError(f"{ref.text} is no function; kb code shows the code of a function "
                      f"(kb show {ref.text})", code=2)
    return repo.layout(ref.node["layout"], root), ref.node["address"], ref.text


@_source_read
def command_code(args, root=repo.ROOT):
    layout, address, symbol = code_target(args, root,held=True)
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
    parts = [symbol] if symbol else []
    parts.append(f"{layout.id}:{entry}  fn  [l0] Ghidra {repo.ghidra_version(root)}, "
                 f"program of {layout.image}")
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
    return _checked_sources(args, root)






@_source_read
def _checked_sources(args, root=repo.ROOT):
    selected = args.only or list(CHECKS)
    record = passes.Passes(root)
    failed = 0
    for name in selected:
        failures = record.run(name, CHECKS[name], args.changed)
        if failures is None:
            print(f"check {name}: PASS, its inputs are those of its last pass")
            continue
        for failure in failures:
            print(f"{name}: {failure}")
        for note in NOTES[name](root) if name in NOTES else ():
            print(f"{name}: note: {note}")
        print(f"check {name}: {'FAIL ' + str(len(failures)) if failures else 'PASS'}")
        failed += len(failures)
    record.save()
    return 1 if failed else 0


def command_sync(args, root=repo.ROOT):
    model, _ = graph.sync(root, full=args.full)
    print(f"model: {len(model.meanings)} meanings, {len(model.symbols)} symbols, "
          f"{len(model.links)} links")
    return 0


def command_instance(args, root=repo.ROOT):
    if args.action == "status":
        print("\n".join(instance.status(root)))
    else:
        getattr(instance, args.action)(root)
    return 0


def command_guard(args, root=None):
    """Manage only the saved guard override of one project and root session."""
    root = Path(root or repo.ROOT).resolve()
    try:
        path = project.hook.session_state_path(root, args.session)
        if args.action == "status":
            mode = project.hook.session_mode(root, args.session)
        else:
            path = project.hook.set_session_mode(root, args.session, args.action)
            mode = args.action
    except ValueError as error:
        raise KbError(str(error), code=2) from error
    except OSError as error:
        raise KbError(f"cannot update KB guard session state: {error}", code=6) from error
    state = {"project": str(root), "session_id": path.stem,
             "mode": mode, "state_path": str(path)}
    if args.json:
        print(json.dumps(state, sort_keys=True))
    else:
        saved = mode if mode is not None else "unset (hook environment fallback)"
        print(f"KB guard {saved}: session {path.stem} in {root}")
    return 0


def _stderr(text):
    print(text, file=sys.stderr)


def render(item):
    """A value of a query result in one line: nodes and relationships by key."""
    from neo4j.graph import Node, Path as GraphPath, Relationship

    if isinstance(item, Node):
        labels = ":".join(sorted(item.labels - {"Kb"}))
        return f"({labels} {item.get('key', item.element_id)})"
    if isinstance(item, Relationship):
        return f"[{item.type} {render(item.start_node)} -> {render(item.end_node)}]"
    if isinstance(item, GraphPath):
        return " ".join([render(item.start_node)] + [
            f"-[{rel.type}]- {render(rel.end_node)}" for rel in item.relationships])
    if isinstance(item, (list, dict)):
        return json.dumps(item, default=str, separators=(",", ":"), sort_keys=True)
    return str(item)


def _plain(item):
    from neo4j.graph import Node, Path as GraphPath, Relationship

    if isinstance(item, Node):
        return {"labels": sorted(item.labels - {"Kb"}), **dict(item)}
    if isinstance(item, Relationship):
        return {"type": item.type, "from": item.start_node.get("key"),
                "to": item.end_node.get("key"), **dict(item)}
    if isinstance(item, GraphPath):
        return [_plain(node) for node in item.nodes]
    if isinstance(item, list):
        return [_plain(entry) for entry in item]
    if isinstance(item, dict):
        return {key: _plain(entry) for key, entry in item.items()}
    return item


def command_cypher(args, root=repo.ROOT):
    params = {}
    for pair in args.param or ():
        name, sep, text = pair.partition("=")
        if not sep or not name:
            raise KbError(f"--param {pair!r} is not <name>=<json value>", code=2)
        try:
            params[name] = json.loads(text)
        except ValueError:
            params[name] = text
    reason = graph.refusal(args.query)
    if reason:
        raise KbError(reason, code=2)
    with reader.session(root,args.no_sync) as session:
        result=session.run(args.query,params)
        keys,records=result.keys(),list(result)
        if args.json:
            text = json.dumps([{key: _plain(record[key]) for key in keys} for record in records],
                              default=str, indent=1) + '\n'
        else:
            lines = ["\t".join(keys)]
            lines.extend("\t".join(render(record[key]) for key in keys) for record in records)
            lines.append(f"{len(records)} rows")
            text = fit("\n".join(lines) + "\n", budget_of(args, "cypher", root),
                       "a narrower query, LIMIT, --budget <tokens>,")
    sys.stdout.write(text)
    return 0


def _json_default(item):
    if isinstance(item, (set, frozenset, tuple)):
        return sorted(item)
    return str(item)


def _answer(args, command, build, root=repo.ROOT):
    """Print the answer of a read command within its budget, or its data."""
    with reader.graph_session(root,args.no_sync) as session:
        found = build(session)
        if args.json:
            text = json.dumps(found.data, default=_json_default, indent=1, sort_keys=True) + '\n'
        else:
            text = found.text(budget_of(args, command, root))
    sys.stdout.write(text)
    return 0


def command_at(args, root=repo.ROOT):
    return _answer(args, "at", lambda g: read.at(
        g, args.ref, args.layout, root, literal=args.literal), root)


def command_show(args, root=repo.ROOT):
    return _answer(args, "show", lambda g: read.show(g, args.ref, args.layout, root), root)


def command_where(args, root=repo.ROOT):
    return _answer(args, "where", lambda g: read.where(g, args.ref, root), root)


def command_impact(args, root=repo.ROOT):
    return _answer(args, "impact",
                   lambda g: read.impact(g, args.ref, args.layout, args.expand, root), root)


def command_path(args, root=repo.ROOT):
    return _answer(args, "path", lambda g: read.path(
        g, args.first, args.second, args.layout, args.expand, args.limit, root), root)


def command_find(args, root=repo.ROOT):
    return _answer(args, "find", lambda g: read.find(g, args.words, args.limit, root), root)


def command_brief(args, root=repo.ROOT):
    return _answer(args, "brief", lambda g: read.brief(g, root), root)


def command_gaps(args, root=repo.ROOT):
    if args.catalog:
        if args.feature:
            raise KbError('gaps --catalog does not take --feature', code=2)
        return _answer(args, 'gaps', lambda g: catalog.report(compile.cached(root), args.layout), root)
    return _answer(args, "gaps", lambda g: read.gaps(g, args.feature, args.layout, root), root)


def command_log(args, root=repo.ROOT):
    return _answer(args, "log", lambda g: read.log(g, args.ref, root), root)


def command_raw(args, root=repo.ROOT):
    return _answer(args, "raw", lambda g: read.raw(g, args.ref, root), root)


def command_suggest(args, root=repo.ROOT):
    if bool(args.blocks) == bool(args.ref):
        raise KbError('suggest takes a reference or --blocks', code=2)
    return _answer(args, 'suggest', lambda g: (
        suggest.blocks(g, args.layout, root) if args.blocks
        else suggest.symbols(g, args.ref, args.layout, root)), root)


def baseline_tokens(steps, root=repo.ROOT):
    """Tokens of the output of a question's baseline steps."""
    total = 0
    for step in steps:
        result = subprocess.run(step["run"], cwd=root, capture_output=True)
        if result.returncode not in (0, 1):
            raise KbError(f"baseline {shlex.join(step['run'])} failed: "
                          f"{result.stderr.decode(errors='replace').strip()}")
        if step.get("read"):
            for line in result.stdout.decode().splitlines():
                if line.strip():
                    total += answer.tokens((root / line.strip()).read_text(encoding="utf-8"))
        else:
            total += answer.tokens(result.stdout.decode(errors="replace"))
    return total


def command_bench(args, root=repo.ROOT):
    config = read.bench(root)
    questions = [(question, spec.expectations(question)) for question in config["question"]]
    known = {question["id"] for question, _ in questions}
    if args.only and (unknown := sorted(set(args.only) - known)):
        raise KbError(f"no benchmark questions {unknown}; known ids: {sorted(known)}", code=2)
    selected = [(question, expected) for question, expected in questions
                if not args.only or question["id"] in args.only]
    if not selected:
        raise KbError("no benchmark questions selected",
                      code=2)
    failed = 0
    for question, expected in selected:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(shlex.split(question["command"])[1:] + ["--full"])
        rendered = out.getvalue()
        used = answer.tokens(rendered)
        base = baseline_tokens(question["baseline"], root)
        missing = [pattern.pattern for pattern in expected if pattern.search(rendered) is None]
        passed = code == 0 and not missing and used <= question["budget"] and used < base
        failed += not passed
        print(f"{question['id']:>2}  {'PASS' if passed else 'FAIL'}  {used:>5} tokens, budget "
              f"{question['budget']:>5}, baseline {base:>6}  {question['command']}"
              + ("" if code == 0 else f"  exit {code}")
              + (f"  missing expected content: {missing!r}" if missing else ""))
    return 1 if failed else 0


@_source_read
def command_audit(args, root=repo.ROOT):
    found = checks.audit(compile.cached(root), args.section or checks.AUDIT_SECTIONS)
    for section, issues in found.items():
        for issue in issues:
            print(f"{section}: {issue.path}: {issue.subject}: {issue.message}")
    print("audit: " + ", ".join(f"{len(issues)} {section}" for section, issues in found.items()))
    return 0




def command_project(args, root=repo.ROOT):
    if args.check:
        found = project.write(root, args.paths, check=True)
        for path, changed in found:
            print(f"{path}: {'differs from its rendering' if changed else 'current'}")
        return 1 if any(changed for _, changed in found) else 0
    with lock.held(root):
        for path, changed in project.write(root, args.paths):
            print(f"{path}: {'written' if changed else 'current'}")
    return 0


def command_fmt(args, root=repo.ROOT):
    with lock.held(root):
        for path in store.fmt(root, args.paths):
            print(f"{path.as_posix()}: rewritten")
    return 0


def _write(args, ops, root=repo.ROOT):
    """Apply write operations as one change and print the files it writes and
    one line per operation; a dry run prints the diff instead of writing."""
    change, texts = write.apply(ops, root, dry_run=args.dry_run, log=_stderr)
    for path, text in texts.items():
        done = "written" if text is not None else "removed"
        print(f"{path.as_posix()}: {'would be ' + done if args.dry_run else done}")
    for line in change.lines:
        print(line)
    if args.dry_run:
        sys.stdout.write(change.diff(texts))
    return 0


def command_new(args, root=repo.ROOT):
    place = "symbol" if refs.LOCATION.fullmatch(args.ref.strip()) else "slug"
    return _write(args, [{
        "cmd": "new", "kind": args.kind, place: args.ref, "name": args.name,
        "evidence": [write.parse_evidence(text) for text in args.evidence or ()],
        "level": args.level, "note": args.note}], root)


def command_set(args, root=repo.ROOT):
    keys, unset = write.parse_assignments(args.assignments)
    return _write(args, [{"cmd": "set", "ref": args.ref, "layout": args.layout, "keys": keys,
                          "unset": unset}], root)


def command_retire(args, root=repo.ROOT):
    operation = {'cmd': 'retire', 'ref': args.ref}
    if getattr(args, 'withdraw_ledger', None):
        operation['withdraw_ledger'] = args.withdraw_ledger
    return _write(args, [operation], root)


def command_rebase_reviews(args, root=repo.ROOT):
    return _write(args, [{'cmd': 'rebase-reviews', 'layout': args.layout,
                         'from_l0': args.from_l0,
                         'reasons_reviewed': args.reasons_reviewed}], root)


def command_family(args, root=repo.ROOT):
    metadata = None
    if args.operation == 'new':
        metadata = dict(kind=args.kind, mcu=args.mcu, flash_size=args.flash_size,
                        software_ids=args.software_id)
        if args.kind == 'exact-code':
            if not args.calibration_region or not args.exact_range:
                raise KbError('an exact-code family needs calibration region and exact ranges', code=2)
            metadata.update(calibration_region=args.calibration_region, exact_ranges=args.exact_range)
    print(family.apply(args.operation, args.family, args.image, args.layout, args.census,
                       metadata, root=root, dry_run=args.dry_run, log=_stderr))
    return 0


def command_bind(args, root=repo.ROOT):
    return _write(args, [{
        "cmd": "bind", "meaning": args.meaning, "symbol": args.symbol,
        "evidence": [write.parse_evidence(text) for text in args.evidence or ()],
        "from": args.source, "level": args.level, "note": args.note}], root)


def command_absent(args, root=repo.ROOT):
    return _write(args, [{
        "cmd": "absent", "meaning": args.meaning, "layout": args.layout,
        "evidence": [write.parse_evidence(text) for text in args.evidence],
        "note": args.note}], root)


def command_unresolved(args, root=repo.ROOT):
    return _write(args, [{
        "cmd": "unresolved", "meaning": args.meaning, "layout": args.layout,
        "from": args.source, "method": args.method, "target": args.target,
        "count": args.count, "note": args.note}], root)


def _link_keys(args):
    keys, unset = write.parse_assignments(args.assignments)
    if unset:
        raise repo.KbError(f"a link key takes a value: {', '.join(unset)}", code=2)
    return keys


def command_link(args, root=repo.ROOT):
    return _write(args, [{
        "cmd": "link", "meaning": args.meaning, "type": args.type, "to": args.to,
        "keys": _link_keys(args),
        "evidence": [write.parse_evidence(text) for text in args.evidence or ()]}], root)


def command_unlink(args, root=repo.ROOT):
    return _write(args, [{"cmd": "unlink", "meaning": args.meaning, "type": args.type,
                          "to": args.to, "keys": _link_keys(args)}], root)


def command_set_link(args, root=repo.ROOT):
    keys, unset = write.parse_assignments(args.assignments)
    selector = {name: getattr(args, name) for name in ("slot", "offset")
                if getattr(args, name) is not None}
    return _write(args, [{"cmd": "set-link", "meaning": args.meaning,
                          "type": args.type, "to": args.to, "selector": selector,
                          "keys": keys, "unset": unset}], root)


def command_select(args, root=repo.ROOT):
    keys, unset = write.parse_assignments(args.assignments)
    if unset:
        raise repo.KbError(f"a dependency key takes a value: {', '.join(unset)}", code=2)
    return _write(args, [{"cmd": "select", "meaning": args.meaning,
                          "registry": args.registry, "order": args.order,
                          "dependency": keys}], root)


def command_merge(args, root=repo.ROOT):
    return _write(args, [{
        "cmd": "merge", "meaning": args.meaning, "other": args.other,
        "evidence": [write.parse_evidence(text) for text in args.evidence or ()],
        "from": args.source}], root)


def command_rename(args, root=repo.ROOT):
    return _write(args, [{"cmd": "rename", "meaning": args.meaning, "name": args.name}], root)


def command_move(args, root=repo.ROOT):
    if args.legacy_reservation:
        if args.evidence or args.source or args.level or args.note:
            raise KbError("--legacy-reservation takes no evidence, from, level or note", code=2)
        from kb import legacy_reservation
        change, texts = legacy_reservation.apply(
            args.symbol, args.to, root, dry_run=args.dry_run, log=_stderr)
        for path in texts:
            print(f"{path.as_posix()}: {'would be written' if args.dry_run else 'written'}")
        for line in change.lines:
            print(line)
        if args.dry_run:
            sys.stdout.write(change.diff(texts))
        return 0
    return _write(args, [{
        "cmd": "move", "symbol": args.symbol, "to": args.to,
        "evidence": [write.parse_evidence(text) for text in args.evidence or ()],
        "from": args.source, "level": args.level, "note": args.note}], root)


def command_apply(args, root=repo.ROOT):
    return _write(args, write.read_batch(Path(args.batch)), root)


def command_mcp(args, root=repo.ROOT):
    from kb import mcp

    return mcp.serve_stdio()


def build_parser():
    parser = argparse.ArgumentParser(
        prog="kb", description="Knowledge model and entry point (tools/kb/SPEC.md)."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="run supported model and source checks")
    check.add_argument("--changed", action="store_true",
                       help="run the checks whose inputs differ from those of their last pass")
    check.add_argument("--only", action="append", help="run one check; repeatable")
    check.set_defaults(handler=command_check)

    sync = commands.add_parser("sync", help="compile the inputs and load the graph")
    sync.add_argument("--full", action="store_true", help="reload every element")
    sync.set_defaults(handler=command_sync)

    manage = commands.add_parser("instance", help="the graph instance of the working tree")
    manage.add_argument("action", choices=("up", "down", "status", "prune"))
    manage.set_defaults(handler=command_instance)

    access = commands.add_parser("guard", help="the saved KB guard override of one session")
    access.add_argument("action", choices=("on", "off", "status"))
    access.add_argument("--session", required=True, help="explicit root session UUID")
    access.add_argument("--json", action="store_true", help="structured saved state")
    access.set_defaults(handler=command_guard)

    cypher = commands.add_parser("cypher", help="a read-only Cypher query")
    cypher.add_argument("query")
    cypher.add_argument("--param", action="append",
                        help="<name>=<value>, the value as JSON or text; repeatable")
    cypher.add_argument("--json", action="store_true", help="structured output, no budget")
    cypher.add_argument("--budget", type=int)
    cypher.add_argument("--full", action="store_true")
    cypher.add_argument("--no-sync", action="store_true",
                        help="fail instead of syncing a stale graph")
    cypher.set_defaults(handler=command_cypher)

    audit = commands.add_parser(
        "audit", help="registry disagreements, claim levels, and chain arithmetic")
    audit.add_argument("--section", action="append", choices=checks.AUDIT_SECTIONS,
                       help="compute and print one section; repeatable")
    audit.set_defaults(handler=command_audit)

    def reader(name, help_text, *positional, layout=True):
        command = commands.add_parser(name, help=help_text)
        for argument, argument_help in positional:
            command.add_argument(argument, help=argument_help)
        if layout:
            command.add_argument("--layout", help="restrict the answer to one layout")
        command.add_argument("--budget", type=int, help="output budget in tokens")
        command.add_argument("--full", action="store_true", help="no budget")
        command.add_argument("--json", action="store_true", help="structured output, no budget")
        command.add_argument("--no-sync", action="store_true",
                             help="fail instead of syncing a stale graph")
        return command

    reference = ("ref", "a reference (tools/kb/SPEC.md, section 5.2)")
    at = reader("at", "the symbol at an address and the L0 facts there", reference)
    at.add_argument("--literal", action="store_true",
                    help="also list exact exported 32-bit load values equal to the address")
    at.set_defaults(handler=command_at)
    reader("show", "an entity with its symbols, links, and evidence", reference) \
        .set_defaults(handler=command_show)
    reader("where", "the symbol or status of a meaning on every layout", reference,
           layout=False).set_defaults(handler=command_where)
    impact = reader("impact", "every entity that depends on a reference", reference)
    impact.add_argument("--expand", action="append", help="expand a hub; repeatable")
    impact.set_defaults(handler=command_impact)
    route = reader("path", "the shortest typed paths between two entities",
                   ("first", "a reference"), ("second", "a reference"))
    route.add_argument("--expand", action="append", help="expand a hub; repeatable")
    route.add_argument("--limit", type=int, default=3, help="paths to list (default 3)")
    route.set_defaults(handler=command_path)
    search = reader("find", "entities ranked by name, former name, title, and summary",
                    layout=False)
    search.add_argument("words", nargs="+")
    search.add_argument("--limit", type=int, default=15, help="results to list (default 15)")
    search.set_defaults(handler=command_find)
    reader("brief", "the state of the knowledge base", layout=False) \
        .set_defaults(handler=command_brief)
    gap = reader("gaps", "required meanings without a symbol, grouped by status")
    gap.add_argument("--feature", help="the meanings that one feature requires")
    gap.add_argument('--catalog', action='store_true', help='parity acceptance and target status')
    gap.set_defaults(handler=command_gaps)
    reader("log", "the history of an entity through renames and redirects", reference,
           layout=False).set_defaults(handler=command_log)
    reader("raw", "the registry records of an entity", reference, layout=False) \
        .set_defaults(handler=command_raw)
    candidates = reader('suggest', 'candidate symbols by evidence channel or architecture blocks', layout=False)
    candidates.add_argument('ref', nargs='?', help='the source symbol or meaning')
    candidates.add_argument('--blocks', action='store_true')
    candidates.add_argument('--layout', required=True, help='the target layout')
    candidates.set_defaults(handler=command_suggest)

    bench = commands.add_parser("bench", help="answer the acceptance questions (bench.toml)")
    bench.add_argument("--only", type=int, action="append", help="one question id; repeatable")
    bench.set_defaults(handler=command_bench)

    code = commands.add_parser("code", help="decompilation or listing of a function")
    code.add_argument("ref", help="a function, its meaning, or <layout>:<address> of an "
                      "instruction (tools/kb/SPEC.md, section 5.2)")
    code.add_argument("--layout", help="the layout of the symbol of a meaning, or of an address")
    code.add_argument("-l", "--listing", action="store_true", help="add the listing")
    code.add_argument("-f", "--force", action="store_true", help="rerun Ghidra")
    code.add_argument("--budget", type=int)
    code.add_argument("--full", action="store_true")
    code.add_argument("--no-sync", action="store_true",
                      help="fail instead of syncing a stale graph")
    code.set_defaults(handler=command_code)

    render = commands.add_parser("project", help="render the projections that kb generates")
    render.add_argument("paths", nargs="*", help="projection paths of tools/kb/projections.toml")
    render.add_argument("--check", action="store_true",
                        help="write nothing; exit 1 when a projection differs from its rendering")
    render.set_defaults(handler=command_project)

    rewrite = commands.add_parser("fmt", help="rewrite entity files in canonical form")
    rewrite.add_argument("paths", nargs="*", help="entity files; every file by default")
    rewrite.set_defaults(handler=command_fmt)

    def writer(name, help_text, *positional):
        command = commands.add_parser(name, help=help_text)
        for argument, argument_help in positional:
            command.add_argument(argument, help=argument_help)
        command.add_argument("--dry-run", action="store_true",
                             help="check the change and print its diff without writing")
        return command

    meaning = ("meaning", "the meaning, or its symbol that a search starts from")
    evidence = "an evidence item as a TOML inline table; repeatable"
    source = "the layout of the symbol of the meaning that the search starts from"
    start = writer("new", "a meaning with the symbol at a location, or a designed entity",
                   ("kind", "the kind of the meaning or of the designed entity"),
                   ("ref", "<layout>:<address> of the symbol, or the slug of the designed "
                    "entity"))
    start.add_argument("--name", help="the semantic name of the meaning; by default the "
                       "generated name of the symbol")
    start.add_argument("--evidence", action="append",
                       help=f"{evidence} of the identity of the symbol on its layout; a symbol "
                       "requires it")
    start.add_argument("--level", choices=vocab.LEVELS, help="the level of the symbol")
    start.add_argument("--note", help="prose about the symbol")
    start.set_defaults(handler=command_new)
    assign = writer("set", "keys of a meaning, a symbol, a designed entity, or a feature target",
                    ("ref", "the meaning, its symbol, or the designed entity"))
    assign.add_argument("assignments", nargs="+", metavar="key=value",
                        help="a TOML value or else a string; an empty value unsets the key, "
                        "and a dotted key names a key of a table")
    assign.add_argument("--layout", help="the symbol of a meaning, or the target of a feature, "
                        "on this layout")
    assign.set_defaults(handler=command_set)
    bind = writer("bind", "a symbol of a meaning on another layout, with evidence", meaning,
                  ("symbol", "<layout>:<address> of the symbol"))
    bind.add_argument("--evidence", action="append",
                      help=f"{evidence}; by default the evidence of the search")
    bind.add_argument("--from", dest="source", help=source)
    bind.add_argument("--level", choices=vocab.LEVELS, help="the level of the symbol")
    bind.add_argument("--note", help="prose about the symbol")
    bind.set_defaults(handler=command_bind)
    absent = writer("absent", "status absent with the evidence that removes the mechanism",
                    meaning)
    absent.add_argument("--layout", required=True)
    absent.add_argument("--evidence", action="append", required=True, help=evidence)
    absent.add_argument("--note", help="prose about the status")
    absent.set_defaults(handler=command_absent)
    unresolved = writer("unresolved", "status unresolved with the method and target of the "
                        "search", meaning)
    unresolved.add_argument("--layout", required=True)
    unresolved.add_argument("--from", dest="source", help=source)
    unresolved.add_argument("--method", choices=tuple(vocab.EVIDENCE_KINDS),
                            help="the evidence kind of a stated search")
    unresolved.add_argument("--target", help="what a stated search looked for")
    unresolved.add_argument("--count", type=int, help="the matches of a stated search")
    unresolved.add_argument("--note", help="prose about the status")
    unresolved.set_defaults(handler=command_unresolved)
    ends = (("meaning", "the meaning whose file states the link"),
            ("type", "the link type (tools/kb/SPEC.md, section 7.5)"),
            ("to", "the meaning that the link names"))
    link = writer("link", "a typed link of a meaning to another meaning", *ends)
    link.add_argument("assignments", nargs="*", metavar="key=value",
                      help="a key of the link as a TOML value or else a string")
    link.add_argument("--evidence", action="append", help=evidence)
    link.set_defaults(handler=command_link)
    unlink = writer("unlink", "remove a link from the file of a meaning", *ends)
    unlink.add_argument("assignments", nargs="*", metavar="key=value",
                        help="slot or offset, which choose among the links of one type and "
                        "target")
    unlink.set_defaults(handler=command_unlink)
    amend = writer("set-link", "mutable properties of one existing owned native link", *ends)
    amend.add_argument("assignments", nargs="+", metavar="key=value",
                       help="mutable link keys; an empty value unsets its key")
    amend.add_argument("--slot", help="the exact held slot; absent selects an absent slot")
    amend.add_argument("--offset", type=lambda text: int(text, 0),
                       help="the exact held integer offset; absent selects an absent offset")
    amend.set_defaults(handler=command_set_link)
    select = writer("select", "select an existing native relation in an owned ledger row",
                    meaning, ("registry", "the existing ledger registry"))
    select.add_argument("order", type=int, help="the existing nonnegative ledger row order")
    select.add_argument("assignments", nargs="+", metavar="key=value",
                        help="keys of ledger.dependency as TOML values or strings")
    select.set_defaults(handler=command_select)
    merge = writer("merge", "join another meaning, or another file of one meaning, into a "
                   "meaning", ("meaning", "the meaning that keeps its name, or its symbol that "
                               "a search starts from"),
                   ("other", "the meaning or the meaning file that joins it"))
    merge.add_argument("--evidence", action="append",
                       help=f"{evidence} at the layout of a symbol of the other meaning; by "
                       "default the evidence of the search")
    merge.add_argument("--from", dest="source", help=source)
    merge.set_defaults(handler=command_merge)
    rename = writer("rename", "give a meaning a semantic name", ("meaning", "the meaning"),
                    ("name", "the semantic name"))
    rename.set_defaults(handler=command_rename)
    move = writer("move", "correct the address of a symbol on its layout, or its meaning",
                  ("symbol", "the symbol"),
                  ("to", "<layout>:<address> of the symbol, or the meaning that it joins"))
    move.add_argument("--legacy-reservation", action="store_true",
                      help="preserve an existing generated function name after a reviewed "
                           "legacy-owner and L0 entry repair; no entity adoption")
    move.add_argument("--evidence", action="append",
                      help=f"{evidence}; by default the evidence of the search")
    move.add_argument("--from", dest="source", help="the layout of the symbol that the search "
                      "starts from, of the meaning of the symbol or of the meaning that it "
                      "joins; by default the home symbol")
    move.add_argument("--level", choices=vocab.LEVELS, help="the level of the symbol")
    move.add_argument("--note", help="prose about the symbol")
    move.set_defaults(handler=command_move)
    writer("apply", "a batch of write operations as one change",
           ("batch", "a TOML file of [[op]] tables")).set_defaults(handler=command_apply)
    retiring = writer('retire', 'make an unused owned entity inactive and reserve its names', reference)
    retiring.add_argument('--withdraw-ledger', action='append', metavar='registry:order',
                          help='explicitly withdraw every owned ledger selector of a vanished L0 function entry')
    retiring.set_defaults(handler=command_retire)
    rebase = writer('rebase-reviews', 'rebind exact unresolved reviews after an L0 export')
    rebase.add_argument('--layout', required=True, help='the layout whose reviews may change')
    rebase.add_argument('--from-l0', required=True, help='the previous exported-data digest')
    rebase.add_argument('--reasons-reviewed', action='store_true',
                        help='include custom reasons after reviewing their code dependencies')
    rebase.set_defaults(handler=command_rebase_reviews)
    onboarding = commands.add_parser('family', help='record a family or image with a stock-bound census')
    operations = onboarding.add_subparsers(dest='operation', required=True)
    for name in ('new', 'add'):
        command = operations.add_parser(name)
        command.add_argument('family', help='the stable family id')
        command.add_argument('--image', required=True, help='the registered target image')
        command.add_argument('--layout', required=name == 'new', help='a new stable layout id')
        command.add_argument('--census', required=True, help='the source-target census report under defs/')
        command.add_argument('--dry-run', action='store_true')
        if name == 'new':
            command.add_argument('--kind', choices=('exact-code', 'near-code', 'distinct-code'), default='distinct-code')
            command.add_argument('--mcu', required=True, choices=('SH7058', 'SH7059'))
            command.add_argument('--flash-size', required=True, type=lambda text: int(text, 0))
            command.add_argument('--software-id', action='append', required=True)
            command.add_argument('--calibration-region')
            command.add_argument('--exact-range', action='append')
        command.set_defaults(handler=command_family)

    serve = commands.add_parser("mcp", help="serve the read commands and kb_apply over MCP "
                                "on stdio")
    serve.set_defaults(handler=command_mcp)
    return parser


def main(argv=None):
    from neo4j.exceptions import DriverError
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except KbError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.code
    except DriverError as error:
        print(f'error: graph connection or configuration failed ({error}); check KB_BOLT and the working-tree instance',file=sys.stderr)
        return 6
    except BrokenPipeError:
        # A reader such as `head` closed the output; the rest of it is discarded.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0


if __name__ == "__main__":
    sys.exit(main())
