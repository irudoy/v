import io
import json
import unittest

from kb import cli, mcp

# Commands that change state or serve, and so are no MCP read tools.
NOT_READ = {"sync", "instance", "mcp"}


class ToolTest(unittest.TestCase):
    def test_every_read_command_is_one_tool(self):
        commands = set(mcp._subparsers(cli.build_parser()).choices)
        self.assertEqual(set(mcp.READ_COMMANDS), commands - NOT_READ)
        self.assertEqual([tool["name"] for tool in mcp.tools()],
                         [f"kb_{name}" for name in mcp.READ_COMMANDS])

    def test_the_schema_follows_the_arguments_of_the_command(self):
        tools = {tool["name"]: tool["inputSchema"] for tool in mcp.tools()}
        path = tools["kb_path"]
        self.assertEqual(path["required"], ["first", "second"])
        self.assertEqual(path["properties"]["limit"]["type"], "integer")
        self.assertEqual(path["properties"]["expand"]["type"], "array")
        self.assertEqual(path["properties"]["no_sync"]["type"], "boolean")
        self.assertEqual(tools["kb_find"]["required"], ["words"])
        self.assertEqual(tools["kb_audit"]["properties"]["section"]["items"]["enum"],
                         ["disagreements", "names", "untyped", "unsplit"])
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


if __name__ == "__main__":
    unittest.main()
