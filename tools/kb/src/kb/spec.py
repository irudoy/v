"""Tables of tools/kb/SPEC.md that `kb` reads: the stages of the transition,
the ownership of facts by stage, and the acceptance questions."""

from pathlib import Path
import re

from kb import repo

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
    the header and the separator row."""
    rows = []
    for line in section(heading, root).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows[2:]


def plain(cell):
    return cell.replace("`", "")


def stages(root=repo.ROOT):
    found = []
    for cells in table(STAGES, root):
        number, _, name = cells[0].partition(". ")
        found.append({"number": int(number), "name": name})
    return found


def owners(root=repo.ROOT, stage=0):
    """Registries converted by `stage` with their owners, and the number of
    unconverted registries by the stage that converts them."""
    converted, pending = [], {}
    for registry, _, when, owner, _ in table(OWNERSHIP, root):
        number = re.search(r"\d+", when)
        if number is None:
            continue
        number = int(number.group())
        if number <= stage:
            converted.append({"registry": plain(registry), "owner": plain(owner),
                              "stage": number})
        else:
            pending[number] = pending.get(number, 0) + 1
    return {"converted": converted, "pending": pending}


def questions(root=repo.ROOT):
    return [{"id": int(number), "question": question, "command": plain(command),
             "budget": int(budget), "stage": int(stage)}
            for number, question, command, budget, stage in table(QUESTIONS, root)]
