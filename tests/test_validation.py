"""Regression tests for template-scoped, composable validation."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation.common import Context
from validation.runner import RULES, validate_source


class ValidationRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in RULES:
            folder = self.root / "templates" / name
            folder.mkdir(parents=True)
            (folder / "TEMPLATE.json").write_text("{}")
        self.registry = {
            "registered-guide": {"type": "teacher_resource", "published_url": "https://example.org/x"},
            "worksheet": {"type": "student_material", "published_url": "https://example.org/w"},
        }
        self.ctx = Context(self.root, self.registry, {"SHOW", "DO", "MORE", "QUOTE"})
        self.lesson_path = self.root / "content" / "lessons" / "01-set-the-table" / "lesson.json"
        self.lesson_path.parent.mkdir(parents=True)
        (self.lesson_path.parent / "cover.pdf").write_bytes(b"%PDF")

    def lesson(self, template="teacher_guide"):
        return {
            "template": template, "key": "stage", "goal": "Goal", "cover": "cover.pdf",
            "outcomes": ["One", "Two", "Three"], "steps": [
                {"id": 1, "rows": [{"kind": "DO", "text": "Activity"}]}
            ],
        }

    def errors(self):
        return "\\n".join(self.ctx.errors)

    def test_celebrate_inherits_teacher_guide_and_only_celebrate_extras(self):
        doc = self.lesson("celebrate")
        doc["steps"][0]["rows"][0]["kind"] = "INVALID"
        validate_source(self.ctx, self.lesson_path, doc, "lesson")
        self.assertIn("unsupported action label INVALID", self.errors())
        self.assertIn("celebrate guide needs party sizes", self.errors())
        self.assertIn("invitation headline", self.errors())
        self.assertNotIn("companion missing", self.errors())
        self.assertNotIn("activity guide needs", self.errors())

    def test_teacher_guide_does_not_run_celebrate_checks(self):
        validate_source(self.ctx, self.lesson_path, self.lesson(), "lesson")
        self.assertEqual(self.ctx.errors, [])

    def test_welcome_has_no_teacher_guide_or_companion_dependencies(self):
        source = self.root / "welcome.json"
        doc = {"template": "welcome", "pages": [{"blocks": [{"type": "nav",
               "items": [{"resource": "registered-guide"}]}]}]}
        validate_source(self.ctx, source, doc, "standalone")
        self.assertEqual(self.ctx.errors, [])
        doc["pages"][0]["blocks"][0]["items"][0]["resource"] = "not-registered"
        validate_source(self.ctx, source, doc, "standalone")
        self.assertIn("navigation names unknown resource not-registered", self.errors())
        self.assertNotIn("missing cover", self.errors())

    def test_activity_guide_composes_companion_plus_activity_only(self):
        source = self.root / "resource.json"
        doc = {"template": "activity_guide", "resource_id": "registered-guide",
               "blocks": [{"type": "heading", "text": "Before class"}]}
        validate_source(self.ctx, source, doc, "companion")
        self.assertIn("activity guide needs kind", self.errors())
        self.assertIn("activity guide needs a 'How it runs' section", self.errors())
        self.assertNotIn("missing cover", self.errors())
        self.assertNotIn("missing steps", self.errors())

    def test_repeated_unknown_reference_produces_one_shared_error(self):
        doc = self.lesson()
        doc["core"] = [{"ref": "unknown-id"}, {"ref": "unknown-id"}]
        doc["steps"][0]["rows"].append({"kind": "SHOW", "ref": "unknown-id"})
        validate_source(self.ctx, self.lesson_path, doc, "lesson")
        self.assertEqual(self.errors().count("missing catalog resource ref unknown-id"), 1)

    def test_wrong_template_cannot_skip_owner_validation(self):
        validate_source(self.ctx, self.lesson_path, {"template": "welcome"}, "lesson")
        self.assertIn("cannot be used for lesson sources", self.errors())
        self.assertIn("missing goal", self.errors())

    def test_worksheet_quantity_checked_once_in_guide(self):
        doc = self.lesson()
        doc["core"] = [{"ref": "worksheet"}]
        validate_source(self.ctx, self.lesson_path, doc, "lesson")
        self.assertEqual(self.errors().count("worksheet worksheet must set quantity"), 1)


if __name__ == "__main__":
    unittest.main()
