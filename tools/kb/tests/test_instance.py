import os
import unittest
from unittest import mock

from kb import instance, repo


class InstanceTest(unittest.TestCase):
    def test_the_compose_file_gives_the_image_port_and_flags(self):
        service = instance.compose()
        self.assertTrue(service.image.startswith("memgraph/memgraph-mage:"))
        self.assertEqual(service.container, "vq-memgraph-mage")
        self.assertIn("--data-recovery-on-startup=true", service.flags)
        self.assertIsInstance(service.port, int)

    def test_a_linked_tree_takes_a_container_name_from_its_path(self):
        self.assertEqual(instance.container_name("/a/b"), instance.container_name("/a/b"))
        self.assertNotEqual(instance.container_name("/a/b"), instance.container_name("/a/c"))
        self.assertRegex(instance.container_name("/a/b"), r"^kb-[0-9a-f]{12}$")

    def test_the_port_range_lies_outside_the_main_instance(self):
        start, end = instance.settings()["ports"]
        self.assertLess(start, end)
        self.assertFalse(start <= instance.compose().port < end)
        self.assertGreaterEqual(instance.settings()["max_running"], 1)

    def test_the_main_tree_uses_the_published_port(self):
        if not instance.is_main(repo.ROOT):
            self.skipTest("a linked working tree")
        with mock.patch.dict(os.environ):
            os.environ.pop("KB_BOLT", None)
            self.assertEqual(instance.uri(), f"bolt://localhost:{instance.compose().port}")


if __name__ == "__main__":
    unittest.main()
