"""Single derived resource lifecycle, independent of inspector health."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "renderers"))
from publication_state import identity, publication_status
from resource_links import resolve_url
from publication_checks import unpublished_references

HOLDING = "https://drive.google.com/file/d/123456789012345678901234/view"
OFFICIAL = "https://drive.google.com/file/d/abcdefghijklmnopqrstuvwx/view"


class ResourceLifecycleTests(unittest.TestCase):
    def test_external_state_depends_only_on_official_and_different_holding_link(self):
        draft = {"production_type": "external", "holding_url": HOLDING,
                 "published_url": None, "url": HOLDING}
        self.assertEqual(publication_status(draft), "unpublished")
        self.assertEqual(resolve_url(draft), HOLDING)
        self.assertIsNone(resolve_url(draft, release=True))

        live = {**draft, "published_url": OFFICIAL, "holding_url": None}
        self.assertEqual(publication_status(live), "published")
        self.assertEqual(resolve_url(live), OFFICIAL)
        self.assertEqual(resolve_url(live, release=True), OFFICIAL)

        revised = {**live, "holding_url": HOLDING}
        self.assertEqual(publication_status(revised), "pending_publish")
        self.assertEqual(resolve_url(revised), OFFICIAL)

        same_file = {**live, "holding_url": OFFICIAL.replace("/view", "/view?usp=sharing")}
        self.assertEqual(publication_status(same_file), "published")
        self.assertEqual(identity(same_file["holding_url"]), identity(OFFICIAL))

    def test_generated_pdf_pending_only_when_current_md5_differs(self):
        record = {"production_type": "generated_pdf", "published_url": OFFICIAL,
                  "holding_url": HOLDING, "publication": {"artifact_md5": "a" * 32}}
        self.assertEqual(publication_status(record, "b" * 32), "pending_publish")
        self.assertEqual(publication_status(record, "a" * 32), "published")
        self.assertEqual(publication_status(record), "published")
        self.assertEqual(publication_status({**record, "publication": {}}, "b" * 32),
                         "published")  # Missing baseline is inspection's NEEDS REVIEW.
        self.assertEqual(publication_status({**record, "published_url": None}, "b" * 32),
                         "unpublished")

    def test_release_dependencies_need_official_url_not_a_current_checksum(self):
        target = {"kind": "teacher_guide", "data": {"core": [
            {"ref": "good"}, {"ref": "missing"}, {"ref": "draft"},
            {"ref": "pending"}, {"ref": "no-link"}]}}
        registry = {
            "good": {"published_url": OFFICIAL},
            "draft": {"holding_url": HOLDING},
            "pending": {"published_url": OFFICIAL, "holding_url": HOLDING},
            "no-link": {},
        }
        self.assertEqual(unpublished_references(target, registry), [
            "draft (unpublished)", "missing (missing)",
            "no-link (unpublished)"])


if __name__ == "__main__":
    unittest.main()
