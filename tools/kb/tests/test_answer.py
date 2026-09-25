import unittest

from kb import answer
from kb.answer import DETAIL, EVIDENCE, FACTS, IDENTITY, LINKS, Answer


class TokensTest(unittest.TestCase):
    def test_tokens_count_utf8_bytes_by_three(self):
        self.assertEqual(answer.tokens("abc"), 1)
        self.assertEqual(answer.tokens("abcd"), 2)
        self.assertEqual(answer.tokens("ж"), 1)


class FitTest(unittest.TestCase):
    def test_an_answer_within_budget_is_unchanged(self):
        self.assertEqual(answer.fit("line\n", 10, "narrow"), "line\n")
        self.assertEqual(answer.fit("x" * 900, None, "narrow"), "x" * 900 + "\n")

    def test_a_cut_answer_starts_with_truncated_and_names_the_narrower_call(self):
        text = "".join(f"line {number:04d}\n" for number in range(400))
        out = answer.fit(text, 200, "kb code 7mfk:00026740 --budget 400")
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("TRUNCATED: "))
        self.assertIn("kb code 7mfk:00026740 --budget 400", first)
        self.assertLessEqual(answer.tokens(out), 200)


class SectionOrderTest(unittest.TestCase):
    def build(self):
        found = Answer("kb show x --budget <tokens>")
        found.section(None, IDENTITY, ["identity"])
        found.section("facts", FACTS, [f"fact {n}" for n in range(3)])
        found.section("first links", LINKS, [f"first {n}" for n in range(3)])
        found.section("second links", LINKS, [f"second {n}" for n in range(3)])
        found.section("detail", DETAIL, [f"detail {n}" for n in range(3)])
        found.section("evidence", EVIDENCE, [f"evidence {n}" for n in range(30)])
        return found

    def test_evidence_goes_first_from_its_end(self):
        found = self.build()
        full = found.text()
        out = found.text(answer.tokens(full) - 20)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("TRUNCATED: "))
        self.assertIn("detail 2", lines)
        self.assertIn("evidence 0", lines)
        self.assertNotIn("evidence 29", lines)

    def test_of_one_priority_the_last_section_goes_first(self):
        found = self.build()
        budget = answer.tokens("".join(line + "\n" for line in [
            "TRUNCATED: 99 of 99 lines shown; kb show x --budget <tokens> or --full shows the rest",
            "identity", "facts", "fact 0", "fact 1", "fact 2", "first links", "first 0",
            "first 1", "first 2"])) + 3
        lines = found.text(budget).splitlines()
        self.assertIn("first 2", lines)
        self.assertNotIn("second 0", lines)
        self.assertNotIn("second links", lines)
        self.assertNotIn("detail", lines)
        self.assertEqual(lines[0], "TRUNCATED: 7 of 43 lines shown; kb show x --budget <tokens> "
                                   "or --full shows the rest")

    def test_identity_survives_longest(self):
        lines = self.build().text(20).splitlines()
        self.assertEqual(lines[1:], ["identity"])


if __name__ == "__main__":
    unittest.main()
