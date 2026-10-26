import io
import json
import unittest
from unittest import mock

from kb import cli, mcp

# Commands that change state or serve, and so are no MCP read tools.
NOT_READ = {"sync", "instance", "guard", "mcp", "project", "fmt", "new", "set", "bind", "absent",
            "unresolved", "link", "set-link", "unlink", "select", "merge", "rename", "move", "apply",
            "retire", "family"}


class ToolTest(unittest.TestCase):
    def test_every_read_command_and_apply_is_one_tool(self):
        commands = set(mcp._subparsers(cli.build_parser()).choices)
        self.assertEqual(set(mcp.READ_COMMANDS), commands - NOT_READ)
        self.assertEqual(mcp.WRITE_COMMANDS, ("apply",))
        self.assertEqual([tool["name"] for tool in mcp.tools()],
                         [f"kb_{name}" for name in mcp.READ_COMMANDS + mcp.WRITE_COMMANDS])

    def test_retired_proof_commands_are_not_exposed(self):
        parser = cli.build_parser()
        names = {tool["name"] for tool in mcp.tools(parser)}
        commands = set(mcp._subparsers(parser).choices)
        for command in ("flow", "proof-group", "prepare-research"):
            with self.subTest(command=command):
                self.assertNotIn(command, commands)
                self.assertNotIn(f"kb_{command}", names)

    def test_apply_takes_a_batch_and_a_dry_run(self):
        schema = {tool["name"]: tool["inputSchema"] for tool in mcp.tools()}["kb_apply"]
        self.assertEqual(schema["required"], ["batch"])
        self.assertEqual(schema["properties"]["dry_run"]["type"], "boolean")
        self.assertEqual(mcp.argv("apply", {"batch": "ops.toml", "dry_run": True}),
                         ["apply", "ops.toml", "--dry-run"])

    def test_the_schema_follows_the_arguments_of_the_command(self):
        tools = {tool["name"]: tool["inputSchema"] for tool in mcp.tools()}
        path = tools["kb_path"]
        self.assertEqual(path["required"], ["first", "second"])
        self.assertEqual(path["properties"]["limit"]["type"], "integer")
        self.assertEqual(path["properties"]["expand"]["type"], "array")
        self.assertEqual(path["properties"]["no_sync"]["type"], "boolean")
        self.assertEqual(tools["kb_find"]["required"], ["words"])
        self.assertEqual(tools["kb_audit"]["properties"]["section"]["items"]["enum"],
                         ["disagreements", "names", "untyped", "levels", "chain-notes", "research"])
        self.assertNotIn("required", tools["kb_brief"])

    def test_a_call_gives_the_command_line_of_its_command(self):
        self.assertEqual(mcp.argv("find", {"words": "knock threshold", "limit": 5}),
                         ["find", "knock", "threshold", "--limit", "5"])
        self.assertEqual(mcp.argv("path", {"first": "7mfk:ffff1079", "second": "7mfk:ffff2326",
                                           "expand": ["a", "b"], "no_sync": True,
                                           "full": False}),
                         ["path", "7mfk:ffff1079", "7mfk:ffff2326", "--no-sync", "--expand",
                          "a", "--expand", "b"])
        with self.assertRaises(KeyError):
            mcp.argv("at", {"ref": "7mfk:0", "words": "x"})
        with self.assertRaises(ValueError):
            mcp.argv("brief", {"full": "yes"})

    def test_a_usage_error_returns_the_exit_code_of_the_command(self):
        code, text = mcp.call("audit", {"section": ["nothing"]})
        self.assertEqual(code, 2)
        self.assertTrue(text.startswith("exit 2\n"))
        self.assertIn("invalid choice", text)
        self.assertEqual(mcp.call("at", {"ref": "7mfk:0", "bogus": 1}),
                         (2, "exit 2\nerror: kb at takes no argument bogus\n"))


class ProtocolTest(unittest.TestCase):
    def ask(self, method, params=None, ident=1):
        message = {"jsonrpc": "2.0", "id": ident, "method": method}
        if params is not None:
            message["params"] = params
        return mcp.handle(message, {})

    def test_initialize_agrees_on_a_version(self):
        result = self.ask("initialize", {"protocolVersion": "2025-03-26"})["result"]
        self.assertEqual(result["protocolVersion"], "2025-03-26")
        self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(result["serverInfo"]["name"], "kb")
        self.assertEqual(self.ask("initialize", {"protocolVersion": "1999-01-01"})
                         ["result"]["protocolVersion"], mcp.VERSIONS[0])

    def test_errors_follow_json_rpc(self):
        self.assertEqual(self.ask("ping"), {"jsonrpc": "2.0", "id": 1, "result": {}})
        self.assertEqual(self.ask("resources/list")["error"]["code"], -32601)
        self.assertEqual(self.ask("tools/call", {"name": "kb_sync"})["error"]["code"], -32602)
        self.assertEqual(self.ask("tools/call", {"name": "kb_guard",
                                                "arguments": {"action": "off"}})
                         ["error"]["code"], -32602)
        self.assertEqual(mcp.handle({"id": 3, "method": "ping"}, {})["error"]["code"], -32600)
        self.assertIsNone(mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"},
                                     {}))

    def test_a_failed_command_is_an_error_result(self):
        result = self.ask("tools/call", {"name": "kb_audit",
                                         "arguments": {"section": ["nothing"]}})["result"]
        self.assertTrue(result["isError"])
        self.assertTrue(result["content"][0]["text"].startswith("exit 2\n"))

    def test_the_server_answers_one_line_per_message(self):
        source = io.StringIO("\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            "not json",
            json.dumps([{"jsonrpc": "2.0", "id": 2, "method": "ping"}]),
        ]) + "\n")
        sink = io.StringIO()
        mcp.serve(source, sink)
        self.assertEqual([json.loads(line) for line in sink.getvalue().splitlines()], [
            {"jsonrpc": "2.0", "id": 1, "result": {}},
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            [{"jsonrpc": "2.0", "id": 2, "result": {}}],
        ])

    def test_bad_calls_and_empty_batch_do_not_stop_the_following_ping(self):
        bad = [
            {"params": []}, {"params": None},
            {"params": {"name": "kb_find", "arguments": {"words": 5}}},
            {"params": {"name": "kb_find", "arguments": {"words": []}}},
            {"params": {"name": "kb_path", "arguments": {"first": "a", "second": "b", "limit": True}}},
            {"params": {"name": "kb_audit", "arguments": {"section": "levels"}}},
            {"params": {"name": "kb_brief", "arguments": None}},
            {"params": {"name": "kb_at", "arguments": {}}},
        ]
        for wrong in bad + [[]]:
            with self.subTest(message=wrong), mock.patch.object(cli, "main") as command:
                request = dict(jsonrpc="2.0", id=1, method="tools/call", **wrong) if isinstance(wrong, dict) else wrong
                source = io.StringIO(json.dumps(request) + '\n' + json.dumps(dict(jsonrpc="2.0", id=2, method="ping")) + '\n')
                sink = io.StringIO()
                mcp.serve(source, sink)
                failed, ping = map(json.loads, sink.getvalue().splitlines())
                self.assertTrue("error" in failed or failed["result"]["isError"])
                self.assertEqual(ping, dict(jsonrpc="2.0", id=2, result={}))
                command.assert_not_called()

    def test_unexpected_command_and_protocol_failures_are_contained(self):
        requests = [dict(jsonrpc="2.0", id=1, method="tools/call", params=dict(name="kb_brief")),
                    dict(jsonrpc="2.0", id=2, method="ping")]
        for target in (cli, mcp):
            attribute = "main" if target is cli else "_version"
            if target is mcp:
                requests[0] = dict(jsonrpc="2.0", id=1, method="initialize")
            with mock.patch.object(target, attribute, side_effect=RuntimeError("probe failure")):
                sink = io.StringIO()
                mcp.serve(io.StringIO(''.join(json.dumps(item) + '\n' for item in requests)), sink)
            failed, ping = map(json.loads, sink.getvalue().splitlines())
            self.assertIn("probe failure", json.dumps(failed))
            self.assertEqual(ping["result"], {})


if __name__ == "__main__":
    unittest.main()
