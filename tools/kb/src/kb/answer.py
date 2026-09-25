"""Answers of the read commands and their budgets (tools/kb/SPEC.md, section 12.4).

An answer is a list of sections, each with a priority. Within its budget an
answer prints whole; over it, the lines of the lowest-priority section go
first, from its end, and of sections with one priority the last goes first.
The first line of the answer, which states its subject, stays. The first line
of a cut answer reads `TRUNCATED` with the shown and total line counts and the
option or narrower command that shows the rest.
"""

from dataclasses import dataclass, field
import math

# Section priorities: identity survives longest, evidence goes first.
IDENTITY, FACTS, LINKS, DETAIL, EVIDENCE = 50, 40, 30, 20, 10


def tokens(text):
    """Output tokens as the specification counts them: UTF-8 bytes / 3."""
    return math.ceil(len(text.encode("utf-8")) / 3)


def _size(line):
    return len(line.encode("utf-8")) + 1


@dataclass
class Section:
    title: str | None
    priority: int
    lines: list = field(default_factory=list)


class Answer:
    def __init__(self, rest):
        """`rest` names the option or narrower command that shows what a cut
        answer omits."""
        self.rest = rest
        self.sections = []
        self.data = {}

    def section(self, title, priority, lines=()):
        found = Section(title, priority, list(lines))
        self.sections.append(found)
        return found

    def lines(self):
        out = []
        for section in self.sections:
            if not section.lines:
                continue
            if section.title:
                out.append(section.title)
            out.extend(section.lines)
        return out

    def text(self, budget=None):
        full = self.lines()
        rendered = "".join(line + "\n" for line in full)
        if budget is None or tokens(rendered) <= budget:
            return rendered
        total = sum(len(section.lines) for section in self.sections)
        kept = {id(section): list(section.lines) for section in self.sections}
        header = f"TRUNCATED: {total} of {total} lines shown; {self.rest} or --full shows the rest"
        limit = budget * 3 - _size(header) - 8
        used = sum(_size(line) for line in full)
        first = next((section for section in self.sections if section.lines), None)
        order = sorted(enumerate(self.sections), key=lambda item: (item[1].priority, -item[0]))
        for _, section in order:
            lines = kept[id(section)]
            # The first line of an answer states its subject and stays.
            while lines[1 if section is first else 0:] and used > limit:
                used -= _size(lines.pop())
                if not lines and section.title:
                    used -= _size(section.title)
            if used <= limit:
                break
        shown = sum(len(lines) for lines in kept.values())
        out = [f"TRUNCATED: {shown} of {total} lines shown; {self.rest} or --full shows the rest"]
        for section in self.sections:
            lines = kept[id(section)]
            if not lines:
                continue
            if section.title:
                out.append(section.title)
            out.extend(lines)
        return "".join(line + "\n" for line in out)


def fit(text, budget, rest):
    """Cut a plain text answer to its budget, as one section."""
    answer = Answer(rest)
    answer.section(None, IDENTITY, text.rstrip("\n").split("\n"))
    return answer.text(budget)
