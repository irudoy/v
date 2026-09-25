import io
import tempfile
import unittest
from pathlib import Path

from kb import lock
from kb.repo import KbError


class LockTest(unittest.TestCase):
    def test_a_second_holder_gives_up_with_code_7_and_names_the_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with lock.held(root, timeout=5):
                self.assertIn("pid ", (root / lock.PATH).read_text())
                log = io.StringIO()
                with self.assertRaises(KbError) as refused:
                    with lock.held(root, timeout=0, log=log):
                        pass
                self.assertEqual(refused.exception.code, 7)
                self.assertIn("held by pid ", log.getvalue())
            with lock.held(root, timeout=0):
                pass
            self.assertEqual((root / lock.PATH).read_text(), "")


if __name__ == "__main__":
    unittest.main()
