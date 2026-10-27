import unittest

from tools.can_dashboard import package_locks as locks
from tools.version_index import python_version


TARGET = locks.LockTarget(
    "example",
    "requirements-example.txt",
    "requirements-example.lock",
    "x86_64-pc-windows-msvc",
    ("setuptools",),
)
REQUIREMENTS = "python-can[pcan]==4.6.1\n# builds the source distribution\nsetuptools==84.2.1\n"
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64


def lock_text(requirements=REQUIREMENTS, python="3.11", *, can="4.6.1"):
    return locks.header(TARGET, requirements, python) + (
        f"python-can=={can} \\\n"
        f"    --hash={HASH_A} \\\n"
        f"    --hash={HASH_B}\n"
        "    # via -r requirements-example.txt\n"
        "setuptools==84.2.1 \\\n"
        f"    --hash={HASH_C}\n"
        "    # via -r requirements-example.txt\n"
        "uptime==3.0.1 \\\n"
        f"    --hash={HASH_A}\n"
        "    # via python-can\n"
    )


class LockTest(unittest.TestCase):
    def test_a_lock_pins_every_entry_with_its_hashes(self):
        entries = locks.parse_lock(lock_text())
        self.assertEqual(sorted(entries), ["python-can", "setuptools", "uptime"])
        self.assertEqual(entries["python-can"].version, "4.6.1")
        self.assertEqual(entries["python-can"].hashes, (HASH_A, HASH_B))
        self.assertEqual(entries["uptime"].hashes, (HASH_A,))

    def test_a_current_lock_has_no_problems(self):
        self.assertEqual(locks.check_lock(TARGET, REQUIREMENTS, lock_text(), "3.11"), [])

    def test_a_changed_requirement_file_needs_a_new_lock(self):
        changed = REQUIREMENTS.replace("4.6.1", "4.6.2")
        problems = locks.check_lock(TARGET, changed, lock_text(), "3.11")
        self.assertEqual(len(problems), 1)
        self.assertIn("was not generated for the current", problems[0])

    def test_a_lock_of_another_python_is_refused(self):
        problems = locks.check_lock(TARGET, REQUIREMENTS, lock_text(python="3.12"), "3.11")
        self.assertIn("Python 3.11", problems[0])

    def test_a_declared_pin_must_be_locked_at_its_version(self):
        problems = locks.check_lock(TARGET, REQUIREMENTS, lock_text(can="4.6.0"), "3.11")
        self.assertEqual(
            problems,
            [
                "requirements-example.lock locks python-can 4.6.0, "
                "requirements-example.txt declares 4.6.1"
            ],
        )

    def test_a_bootstrap_distribution_must_be_declared(self):
        requirements = "python-can[pcan]==4.6.1\n"
        text = lock_text(requirements)
        problems = locks.check_lock(TARGET, requirements, text, "3.11")
        self.assertEqual(
            problems,
            ["requirements-example.txt does not declare bootstrap setuptools"],
        )

    def test_unhashed_and_inexact_entries_are_refused(self):
        with self.assertRaisesRegex(ValueError, "lacks sha256 hashes"):
            locks.parse_lock("wrapt==1.17.3\n")
        with self.assertRaisesRegex(ValueError, "not an exact pin"):
            locks.parse_lock(f"wrapt>=1.17 --hash={HASH_A}\n")
        with self.assertRaisesRegex(ValueError, "not an exact pin"):
            locks.declared_pins("wrapt>=1.17\n")

    def test_bootstrap_text_is_the_lock_entry_of_each_bootstrap_name(self):
        self.assertEqual(
            locks.bootstrap_text(TARGET, lock_text()),
            f"setuptools==84.2.1 \\\n    --hash={HASH_C}\n",
        )
        self.assertEqual(locks.parse_lock(locks.bootstrap_text(TARGET, lock_text()))["setuptools"].hashes, (HASH_C,))

    def test_the_resolution_targets_one_platform_and_the_project_python(self):
        command = locks.compile_command(locks.TARGET_BY_NAME["windows"], "3.11")
        self.assertEqual(command[:3], ["uv", "pip", "compile"])
        self.assertIn("--generate-hashes", command)
        self.assertIn("--no-config", command)
        self.assertEqual(command[command.index("--python-version") + 1], "3.11")
        self.assertEqual(
            command[command.index("--python-platform") + 1], "x86_64-pc-windows-msvc"
        )
        self.assertEqual(command[-1], "tools/can_dashboard/requirements-windows.txt")

    def test_the_tracked_locks_follow_their_requirements(self):
        python = python_version()
        for target in locks.TARGETS:
            with self.subTest(target=target.name):
                requirements = (locks.ROOT / target.requirements).read_text(encoding="utf-8")
                lock = (locks.ROOT / target.lock).read_text(encoding="utf-8")
                self.assertEqual(locks.check_lock(target, requirements, lock, python), [])
                entries = locks.parse_lock(lock)
                for name in target.bootstrap:
                    self.assertIn(name, entries)


if __name__ == "__main__":
    unittest.main()
