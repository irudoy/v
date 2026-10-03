"""Tables of tools/kb/SPEC.md that `kb` reads: the stages of the transition,
the ownership of facts by stage, and the acceptance questions."""

from pathlib import Path
import re

from kb import repo
from kb.repo import KbError

PATH = Path("tools/kb/SPEC.md")
STAGES = "### 21.3 Stages"
OWNERSHIP = "## 19. Ownership by stage"
QUESTIONS = "## 18. Acceptance questions"


def section(heading, root=repo.ROOT):
    """The text under a heading, up to the next heading of its level or above."""
    text = (root / PATH).read_text(encoding="utf-8")
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index("\n" + heading + "\n") + len(heading) + 2
    stop = re.compile(r"^#{1,%d} " % level, re.M).search(text, start)
    return text[start:stop.start() if stop else len(text)]


def table(heading, root=repo.ROOT):
    """The rows of the first table under a heading as lists of cells, without
    the header and the separator row; `\\|` in a cell is a literal bar."""
    rows = []
    for line in section(heading, root).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break
            continue
        rows.append([cell.strip().replace("\\|", "|")
                     for cell in re.split(r"(?<!\\)\|", line.strip("|"))])
    return rows[2:]


def plain(cell):
    return cell.replace("`", "")


def stages(root=repo.ROOT):
    found = []
    for cells in table(STAGES, root):
        number, _, name = cells[0].partition(". ")
        found.append({"number": int(number), "name": name})
    return found


def questions(root=repo.ROOT):
    return [{"id": int(number), "question": question, "command": plain(command),
             "budget": int(budget), "stage": int(stage)}
            for number, question, command, budget, stage in table(QUESTIONS, root)]


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
