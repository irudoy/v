"""Machine-owned KB command, ownership and benchmark contracts."""

from pathlib import Path
import re
import tomllib

from kb import repo
from kb.repo import KbError

PATH = Path("tools/kb/contracts.toml")
BENCH = Path("tools/kb/bench.toml")
OWNERSHIP = "Ownership"


def table(heading, root=repo.ROOT):
    """Read declarative contract rows without reading documentation."""
    document = tomllib.loads((root / PATH).read_text(encoding="utf-8"))
    try:
        rows = document["table"][heading]["rows"]
    except KeyError as error:
        raise KbError(f"{PATH}: missing contract {heading!r}", code=2) from error
    if not isinstance(rows, list) or not all(
            isinstance(row, list) and all(isinstance(cell, str) for cell in row)
            for row in rows):
        raise KbError(f"{PATH}: {heading!r} requires string-cell rows", code=2)
    return rows


def plain(cell):
    return cell.replace("`", "")




def questions(root=repo.ROOT):
    """The benchmark owner supplies question identities and budgets."""
    keys = ("id", "question", "command", "budget")
    return [{key: item[key] for key in keys} for item in
            tomllib.loads((root / BENCH).read_text(encoding="utf-8"))["question"]]


def expectations(question):
    """Compile the required content of a benchmark question as multiline regexes.
    A missing or empty contract cannot accept an answer."""
    label = f"question {question.get('id', '?')}: expect"
    stated = question.get("expect")
    if not isinstance(stated, list) or not stated:
        raise KbError(f"{label} requires a nonempty array of regular expressions", code=2)
    found = []
    for text in stated:
        if not isinstance(text, str) or not text.strip():
            raise KbError(f"{label} contains an empty or non-string pattern", code=2)
        try:
            pattern = re.compile(text, re.MULTILINE)
        except re.error as error:
            raise KbError(f"{label} has invalid pattern {text!r}: {error}", code=2) from error
        if pattern.search("") is not None:
            raise KbError(f"{label} pattern {text!r} accepts empty content", code=2)
        found.append(pattern)
    return found
