"""`kb mcp`: the read commands and `kb apply` over the Model Context Protocol
on standard input and output (tools/kb/SPEC.md, section 12.6).

Each read command is one tool `kb_<command>`, and `kb_apply` applies a batch of
write operations; the input schema of a tool follows the arguments of its
command. A call runs the command as `kb <command>` runs it,
with the same budgets, and returns its standard output; a nonzero exit code
returns an error result that states the code and the error. The transport is
newline-delimited JSON-RPC 2.0. Child processes write their output to the
standard error, so that only protocol messages reach the standard output.
"""

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
import sys

from kb import cli

# The read commands of section 12.2 that the current stage implements.
READ_COMMANDS = ("brief", "show", "at", "where", "impact", "path", "find", "gaps", "code", "suggest",
                 "log", "raw", "cypher", "audit", "bench", "check")
# Writes reach MCP as batches (section 12.3).
WRITE_COMMANDS = ("apply",)
COMMANDS = READ_COMMANDS + WRITE_COMMANDS
VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
INSTRUCTIONS = (
    "Knowledge of the VQ HR ECU repository: symbols, meanings, links, statuses, and "
    "evidence of every layout. Each tool runs the `kb` command of its name with the same "
    "arguments and budgets. Answers state full references, one fact per line; a first "
    "line that reads TRUNCATED names the option that shows the rest. kb_apply applies a "
    "batch file of new, set, bind, absent, unresolved, link, unlink, merge, rename, and move "
    "operations as one change, or checks it and returns its diff with dry_run.")


def _subparsers(parser):
    return next(action for action in parser._actions
                if isinstance(action, argparse._SubParsersAction))


def _property(action):
    """The JSON Schema of one argument."""
    if isinstance(action, argparse._StoreTrueAction):
        schema = {"type": "boolean"}
    elif isinstance(action, argparse._AppendAction) or action.nargs == "+":
        item = {"type": "integer" if action.type is int else "string"}
        if action.choices:
            item["enum"] = list(action.choices)
        schema = {"type": "array", "items": item}
    else:
        schema = {"type": "integer" if action.type is int else "string"}
        if action.choices:
            schema["enum"] = list(action.choices)
    if action.help:
        schema["description"] = action.help
    return schema


def _arguments(command):
    """The arguments of a subparser without help: (dest, action) in order."""
    return [(action.dest, action) for action in command._actions
            if not isinstance(action, argparse._HelpAction)]


def tools(parser=None):
    """The tool descriptions of the read commands and `kb_apply`."""
    parser = parser or cli.build_parser()
    commands = _subparsers(parser)
    helps = {choice.dest: choice.help for choice in commands._choices_actions}
    found = []
    for name in COMMANDS:
        properties, required = {}, []
        for dest, action in _arguments(commands.choices[name]):
            properties[dest] = _property(action)
            if not action.option_strings:
                required.append(dest)
        schema = {"type": "object", "properties": properties, "additionalProperties": False}
        if required:
            schema["required"] = required
        found.append({"name": f"kb_{name}", "description": f"kb {name}: {helps[name]}",
                      "inputSchema": schema})
    return found


def argv(name, arguments, parser=None):
    """The command line of a tool call; a `KeyError` or `ValueError` names an
    argument that the command does not take or a value of the wrong type."""
    parser = parser or cli.build_parser()
    known = dict(_arguments(_subparsers(parser).choices[name]))
    unknown = sorted(set(arguments) - set(known))
    if unknown:
        raise KeyError(f"kb {name} takes no argument {', '.join(unknown)}")
    line, options = [name], []
    for dest, action in known.items():
        if dest not in arguments or arguments[dest] is None:
            continue
        value = arguments[dest]
        if not action.option_strings:
            if action.nargs == "+":
                line.extend(value.split() if isinstance(value, str) else map(str, value))
            else:
                line.append(str(value))
        elif isinstance(action, argparse._StoreTrueAction):
            if not isinstance(value, bool):
                raise ValueError(f"{dest} is a boolean")
            if value:
                options.append(action.option_strings[-1])
        elif isinstance(action, argparse._AppendAction):
            for item in value if isinstance(value, list) else [value]:
                options.extend([action.option_strings[-1], str(item)])
        else:
            options.extend([action.option_strings[-1], str(value)])
    return line + options


def call(name, arguments):
    """(exit code, text) of one command run in process."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = cli.main(argv(name, arguments))
        except SystemExit as stop:
            code = stop.code if isinstance(stop.code, int) else 2
        except (KeyError, ValueError) as error:
            print(f"error: {error.args[0]}", file=sys.stderr)
            code = 2
    if code == 0:
        return 0, out.getvalue()
    return code, f"exit {code}\n{err.getvalue()}{out.getvalue()}"


def _error(ident, code, message):
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": code, "message": message}}


def handle(message, state):
    """The response to one JSON-RPC message, or None for a notification."""
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" \
            or not isinstance(message.get("method"), str):
        return _error(message.get("id") if isinstance(message, dict) else None, -32600,
                      "Invalid Request")
    ident, method = message.get("id"), message["method"]
    params = message.get("params") or {}
    if "id" not in message:
        return None
    if method == "initialize":
        requested = params.get("protocolVersion")
        result = {"protocolVersion": requested if requested in VERSIONS else VERSIONS[0],
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "kb", "version": _version()},
                  "instructions": INSTRUCTIONS}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": state.setdefault("tools", tools())}
    elif method == "tools/call":
        name = str(params.get("name", ""))
        if not name.startswith("kb_") or name[3:] not in COMMANDS:
            return _error(ident, -32602, f"Unknown tool: {name}")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return _error(ident, -32602, "arguments is not an object")
        code, text = call(name[3:], arguments)
        result = {"content": [{"type": "text", "text": text}], "isError": code != 0}
    else:
        return _error(ident, -32601, f"Method not found: {method}")
    return {"jsonrpc": "2.0", "id": ident, "result": result}


def _version():
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("kb")
    except PackageNotFoundError:
        return "0"


def serve(source, sink):
    """Answer the messages of `source`, one JSON value per line, on `sink`."""
    state = {}
    for line in source:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except ValueError:
            responses = [_error(None, -32700, "Parse error")]
        else:
            batch = message if isinstance(message, list) else [message]
            responses = [response for response in (handle(item, state) for item in batch)
                         if response is not None]
            if isinstance(message, list) and responses:
                responses = [responses]
        for response in responses:
            sink.write(json.dumps(response, separators=(",", ":")) + "\n")
            sink.flush()


def serve_stdio():
    """Serve on the process's standard input and output; the output descriptor
    of the process then leads to the standard error."""
    sink = os.fdopen(os.dup(sys.stdout.fileno()), "w", encoding="utf-8")
    sys.stdout.flush()
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    serve(io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8"), sink)
    return 0
