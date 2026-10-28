"""Identifier positions and actual writes have independent read-only contracts."""

from contextlib import contextmanager
import json

import pytest

from kb import cli, graph, reader


META_QUERY = ("MATCH (m:Kb:Meta) RETURN m.commit AS commit, m.dirty AS dirty, "
              "m.fingerprint AS fingerprint, m.copy_proof_state AS copy_proof_state, "
              "m.loaded_at AS loaded_at")

READS = [
    META_QUERY,
    "MATCH (m) RETURN m . commit AS /* alias */ commit",
    "MATCH (m:CREATE) RETURN m.`SET` AS `DELETE`, $commit AS commit",
    "MATCH (commit) RETURN commit",
    "WITH 1 AS commit RETURN commit ORDER BY commit",
    "WITH 1 AS create RETURN create, {delete: create} AS result",
    "CALL read.proc() YIELD commit AS commit RETURN commit",
    "CALL read.proc() YIELD node, commit AS commit RETURN commit",
    "CALL create() YIELD value RETURN value",
    "RETURN 'CREATE (n); COMMIT' AS text // DELETE n",
    'RETURN "SET n.x = 1" AS text /* CALL mutate.write() */',
    "RETURN 1 AS commit; RETURN 2 AS rollback",
    "MATCH (m) RETURN m.CALL AS call, m.`CALL periodic.iterate` AS text",
]

WRITES = [
    "CREATE (n)", "MERGE (n)", "MATCH (n) DELETE n", "MATCH (n) DETACH DELETE n",
    "MATCH (n) SET n.x=1", "MATCH (n) REMOVE n.x", "DROP INDEX ON :X(y)",
    "FOREACH (n IN [] | CREATE (m))", "LOAD CSV FROM '/x' AS row RETURN row",
    "FREE /* comment */ MEMORY", "STORAGE MODE IN_MEMORY_ANALYTICAL",
    "ANALYZE GRAPH", "LOCK DATA", "UNLOCK DATA", "GRANT ROLE x TO y",
    "REVOKE ROLE x FROM y", "DENY READ TO x", "BEGIN", "COMMIT", "ROLLBACK",
    "RETURN 1 AS commit; COMMIT", "WITH 1 AS create CREATE (n)",
    "WITH 1 AS set MATCH (n) SET n.x=1 RETURN set",
    "MATCH (n) RETURN n; /* read finished */ CREATE (m)",
    "CALL { WITH 1 AS create CREATE (n) RETURN n } RETURN n",
    "CALL read.proc() YIELD node, commit SET node.x=1 RETURN commit",
]


@pytest.mark.parametrize("query", READS)
def test_explicit_identifier_positions_are_not_write_commands(query):
    assert graph.refusal(query) is None


@pytest.mark.parametrize("query", WRITES)
def test_real_write_commands_remain_refused(query):
    assert "the query writes" in graph.refusal(query)


@pytest.mark.parametrize("query,name", [
    ("CALL mutate.write()", "mutate.write"),
    ("CALL `mutate` /* gap */ . `write` ()", "mutate.write"),
    ("CALL `mutate.write`()", "mutate.write"),
    ("CALL `mutate``.write`()", "mutate`.write"),
    ("CALL `mutate.write```()", "mutate.write`"),
    ("WITH 1 AS call CALL mutate.write() YIELD value RETURN value", "mutate.write"),
    ("CALL create()", "create"),
    ("CALL periodic.iterate('RETURN 1', 'CREATE (n)', {})", ""),
    ("CALL `periodic`.`iterate`('RETURN 1', 'CREATE (n)', {})", ""),
])
def test_write_and_nested_query_procedures_keep_their_call_identity(query, name):
    assert "procedure" in graph.refusal(query, {name} if name else set())


@pytest.mark.parametrize("query", ["RETURN 'CREATE", "RETURN `DELETE", "RETURN 1 /* COMMIT"])
def test_unterminated_input_is_reported_as_syntax_instead_of_a_write(query):
    reason = graph.refusal(query)
    assert reason.startswith("cypher: unterminated")
    assert "the query writes" not in reason


class Result(list):
    def keys(self):
        return list(self[0])


class Transaction:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result, error, []

    def run(self, query, params):
        self.calls.append((query, params))
        if self.error:
            raise self.error
        return self.result


def expose(monkeypatch, transaction, writers=()):
    @contextmanager
    def session(*args, **kwargs):
        yield reader.ReadTransaction(transaction, writers)
    monkeypatch.setattr(cli.reader, "session", session)


def test_observed_projection_reaches_the_primary_cli_and_driver_unchanged(monkeypatch, capsys):
    expected = dict(commit="source", dirty=False, fingerprint="current",
                    copy_proof_state=None, loaded_at="loaded")
    transaction = Transaction(Result([expected]))
    expose(monkeypatch, transaction)
    assert cli.main(["cypher", META_QUERY, "--json", "--no-sync"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == [expected] and captured.err == ""
    assert transaction.calls == [(META_QUERY, {})]


@pytest.mark.parametrize("query", WRITES + ["CALL mutate.write()", "CALL `mutate.write`()"])
def test_primary_cli_never_executes_a_real_write(monkeypatch, capsys, query):
    transaction = Transaction()
    expose(monkeypatch, transaction, {"mutate.write"})
    assert cli.main(["cypher", query, "--json"]) == 2
    assert capsys.readouterr().out == ""
    assert transaction.calls == []


def test_backend_syntax_validity_is_not_inferred_from_classifier_acceptance(monkeypatch, capsys):
    from neo4j.exceptions import Neo4jError
    transaction = Transaction(error=Neo4jError._hydrate_neo4j(
        code="Neo.ClientError.Statement.SyntaxError", message="expected an expression"))
    expose(monkeypatch, transaction)
    assert graph.refusal("RETURN (") is None
    assert cli.main(["cypher", "RETURN ("]) == 2
    captured = capsys.readouterr()
    assert "cypher: expected an expression" in captured.err
    assert "the query writes" not in captured.err
    assert transaction.calls == [("RETURN (", {})]
