"""Teacher Guide filenames are defined in the resource catalogue, not lesson JSON."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "renderers"))

import select_builds
import teacher_guide


class TeacherGuideOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = select_builds.read_json("catalog/resources.json")

    def test_registered_default_filename_for_every_lesson(self):
        for name, target in select_builds.targets().items():
            if target["kind"] != "teacher_guide":
                continue
            source = ROOT / target["source"]
            with self.subTest(name=name):
                self.assertNotIn("output", target["data"])
                self.assertEqual(
                    teacher_guide.registered_output(source, self.registry),
                    source.parent / name,
                )

    def test_unregistered_lesson_requires_explicit_output(self):
        source = ROOT / "unregistered" / "lesson.json"
        with self.assertRaisesRegex(ValueError, "register the guide or supply --output"):
            teacher_guide.registered_output(source, self.registry)


if __name__ == "__main__":
    unittest.main()
