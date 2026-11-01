"""Stable Drive links for previews; strict catalogue status before publication."""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "renderers"))
from resource_links import resolve_url, resolved_registry
from publication_checks import unpublished_references

URL = "https://drive.google.com/file/d/123456789012345678901234/view"


class ResourceLifecycleTests(unittest.TestCase):
    def test_holding_url_previews_without_publishing(self):
        item = {"status": "unpublished", "holding_url": URL,
                "published_url": None, "url": None}
        self.assertEqual(resolve_url(item), URL)
        self.assertIsNone(resolve_url(item, release=True))

    def test_move_preserves_url_without_confusing_status(self):
        item = {"status": "published", "holding_url": URL,
                "published_url": URL, "url": URL}
        self.assertEqual(resolve_url(item, release=True), URL)
        self.assertEqual(resolve_url(item), URL)

    def test_review_prefers_new_holding_revision(self):
        original = URL.replace("123456789012345678901234", "abcdefghijklmnopqrstuvwx")
        item = {"status": "published", "holding_url": URL,
                "published_url": original, "url": original}
        self.assertEqual(resolve_url(item), URL)
        self.assertEqual(resolve_url(item, release=True), original)
        self.assertEqual(resolved_registry({"test": item})["test"]["url"], URL)

    def test_release_blocks_any_unpublished_or_unverified_reference(self):
        target = {"kind": "teacher_guide", "data": {"core": [{"ref": "published"},
                  {"ref": "unpublished"}, {"ref": "pending"}, {"ref": "missing"}]}}
        reg = {"published": {"status": "published", "published_url": URL},
               "unpublished": {"status": "unpublished", "holding_url": URL},
               "pending": {"status": "pending_publish", "published_url": URL}}
        self.assertEqual(unpublished_references(target, reg),
                         ["missing (missing)", "pending (pending_publish)", "unpublished (unpublished)"])

    def test_published_status_requires_verified_destination_link(self):
        target = {"kind": "teacher_companion", "data": {"links": [{"ref": "a"}]}}
        self.assertEqual(unpublished_references(target, {"a": {"status": "published"}}),
                         ["a (published)"])
        self.assertEqual(unpublished_references(target, {"a": {"status": "published",
                                "published_url": URL}}), [])

    def test_unpublished_navigation_is_not_a_clickable_dependency(self):
        target = {"kind": "welcome", "data": {"nav": [{"resource": "a"}]}}
        self.assertEqual(unpublished_references(target, {"a": {"status": "unpublished"}}), [])


if __name__ == "__main__":
    unittest.main()
