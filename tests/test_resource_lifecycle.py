"""Keep review links separate from verified release dependencies."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "renderers"))
from resource_links import resolve_url
from publication_checks import unpublished_references

HOLDING = "https://drive.google.com/file/d/123456789012345678901234/view"
OFFICIAL = "https://drive.google.com/file/d/abcdefghijklmnopqrstuvwx/view"


class ResourceLifecycleTests(unittest.TestCase):
    def test_previews_can_use_holding_files_without_releasing_drafts(self):
        draft = {"status": "unpublished", "holding_url": HOLDING,
                 "published_url": None, "url": None}
        self.assertEqual(resolve_url(draft), HOLDING)
        self.assertIsNone(resolve_url(draft, release=True))

        revised = {"status": "published", "holding_url": HOLDING,
                   "published_url": OFFICIAL, "url": OFFICIAL}
        self.assertEqual(resolve_url(revised), OFFICIAL)
        self.assertEqual(resolve_url(revised, release=True), OFFICIAL)

        # An approved published resource may not fall back to its old review link.
        bad_live = {"status": "published", "holding_url": HOLDING,
                    "published_url": None, "url": HOLDING}
        self.assertIsNone(resolve_url(bad_live))
        self.assertIsNone(resolve_url(bad_live, release=True))

    def test_release_requires_published_link_for_every_dependency(self):
        target = {"kind": "teacher_guide", "data": {"core": [
            {"ref": "good"}, {"ref": "missing"}, {"ref": "draft"},
            {"ref": "pending"}, {"ref": "no-link"}]}}
        registry = {
            "good": {"status": "published", "published_url": OFFICIAL},
            "draft": {"status": "unpublished", "holding_url": HOLDING},
            "pending": {"status": "pending_publish", "published_url": OFFICIAL},
            "no-link": {"status": "published"},
        }
        self.assertEqual(unpublished_references(target, registry), [
            "draft (unpublished)", "missing (missing)",
            "no-link (published)", "pending (pending_publish)"])


if __name__ == "__main__":
    unittest.main()
