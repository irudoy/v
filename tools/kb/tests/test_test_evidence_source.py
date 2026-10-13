"""Test-definition evidence follows current file bytes in one process."""

import ast
import os
from types import SimpleNamespace

import pytest

from kb import match


@pytest.fixture
def evidence(tmp_path):
    path = tmp_path / "evidence.py"
    path.write_text("def test_first():\n    return True\n", encoding="utf-8")
    context = SimpleNamespace(model=SimpleNamespace(root=tmp_path),
                              item={"path": path.name, "key": "test_first"})
    return path, context


@pytest.mark.parametrize("change", ["remove", "rename", "replace"])
def test_changed_file_refuses_the_former_name_without_reset(evidence, change):
    path, context = evidence
    assert match._verify_test(context) is None
    previous = path.stat()
    replacement = "def test_other():\n    return True\n"
    if change == "remove":
        path.write_text("value = True\n", encoding="utf-8")
    elif change == "rename":
        path.write_text(replacement, encoding="utf-8")
    else:
        other = path.with_suffix(".replacement")
        other.write_text(replacement, encoding="utf-8")
        other.replace(path)
    # Same size and timestamp cannot stand in for the bytes of the file.
    os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns))
    assert path.stat().st_mtime_ns == previous.st_mtime_ns
    if change != "remove":
        assert path.stat().st_size == previous.st_size
    assert match._verify_test(context) == "evidence.py defines no function test_first"
    if change != "remove":
        context.item["key"] = "test_other"
        assert match._verify_test(context) is None
    path.write_text("async def test_added():\n    return True\n", encoding="utf-8")
    context.item["key"] = "test_added"
    assert match._verify_test(context) is None
    context.item["key"] = "test_first"
    assert match._verify_test(context) is not None


def test_deleted_file_refuses_the_cached_definition(evidence):
    path, context = evidence
    assert match._verify_test(context) is None
    path.unlink()
    assert match._verify_test(context) == "evidence.py is no Python file of the repository"
    path.write_text("def test_other():\n    pass\n", encoding="utf-8")
    assert match._verify_test(context) == "evidence.py defines no function test_first"
    context.item["key"] = "test_other"
    assert match._verify_test(context) is None


def test_unchanged_bytes_reuse_one_parse_and_keep_read_dependencies(evidence, monkeypatch):
    path, context = evidence
    monkeypatch.setattr(match, "READ", set())
    original = ast.parse
    parsed = []

    def parse(source, **kwargs):
        parsed.append((source, kwargs["filename"]))
        return original(source, **kwargs)

    monkeypatch.setattr(ast, "parse", parse)
    assert match._verify_test(context) is None
    first = match._functions_of(path)
    assert match._verify_test(context) is None
    assert match._functions_of(path) is first
    assert isinstance(first, frozenset)
    assert parsed == [(path.read_text(encoding="utf-8"), str(path))]
    assert path.name in match.READ
    path.write_text("def test_other():\n    return True\n", encoding="utf-8")
    assert match._verify_test(context) is not None
    assert len(parsed) == 2


@pytest.mark.parametrize("invalid", ["syntax", "utf8"])
def test_changed_invalid_source_keeps_errors_and_recovers_without_reset(evidence, invalid):
    path, context = evidence
    assert match._verify_test(context) is None
    source = b"def test_first(:\n" if invalid == "syntax" else b"\xff"
    path.write_bytes(source)
    error = SyntaxError if invalid == "syntax" else UnicodeDecodeError
    for _ in range(2):
        with pytest.raises(error) as refused:
            match._verify_test(context)
        if invalid == "syntax":
            assert refused.value.filename == str(path)
    path.write_text("def test_fixed():\n    pass\n", encoding="utf-8")
    assert match._verify_test(context) is not None
    context.item["key"] = "test_fixed"
    assert match._verify_test(context) is None


@pytest.mark.parametrize("reader", ["parse", "walk"])
def test_changed_ast_reader_owns_its_preparation(evidence, monkeypatch, reader):
    _, context = evidence
    assert match._verify_test(context) is None
    if reader == "parse":
        original = ast.parse
        monkeypatch.setattr(ast, "parse", lambda source, **kwargs: original("", **kwargs))
    else:
        monkeypatch.setattr(ast, "walk", lambda tree: ())
    assert match._verify_test(context) == "evidence.py defines no function test_first"


def test_cache_retention_is_bounded_and_large_sources_execute_directly(evidence, monkeypatch):
    path, context = evidence
    for i in range(match._TEST_FUNCTION_CACHE_ENTRIES + 1):
        path.write_text(f"def test_first():\n    return {i}\n", encoding="utf-8")
        assert match._verify_test(context) is None
    info = match._functions_from_source.cache_info()
    assert info.maxsize == match._TEST_FUNCTION_CACHE_ENTRIES
    assert info.currsize <= info.maxsize
    source = ("#" * match._TEST_FUNCTION_SOURCE_BYTES + "\n"
              "def test_large():\n    pass\n")
    path.write_text(source, encoding="utf-8")
    context.item["key"] = "test_large"
    original = ast.parse
    parsed = []

    def parse(text, **kwargs):
        parsed.append(len(text))
        return original(text, **kwargs)

    monkeypatch.setattr(ast, "parse", parse)
    assert match._verify_test(context) is None
    assert match._verify_test(context) is None
    assert parsed == [len(source), len(source)]
    assert match._functions_from_source.cache_info() == info


def test_identical_source_at_other_paths_keeps_diagnostic_filename(evidence):
    path, _ = evidence
    other = path.with_name("other.py")
    source = "def invalid(:\n"
    for candidate in (path, other):
        candidate.write_text(source, encoding="utf-8")
        with pytest.raises(SyntaxError) as refused:
            match._functions_of(candidate)
        assert refused.value.filename == str(candidate)


def test_async_nested_and_method_definitions_keep_ast_walk_scope(evidence):
    path, _ = evidence
    path.write_text("def outer():\n    async def inner():\n        pass\n"
                    "class Example:\n    def method(self):\n        pass\n", encoding="utf-8")
    assert match._functions_of(path) == frozenset({"outer", "inner", "method"})
