"""Checks for multi-ID publishing and automatic publish-on-merge selection."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_to_drive as pub


class ParseIdsTests(unittest.TestCase):
    def test_space_and_comma_separated_ids_keep_order(self):
        self.assertEqual(pub.parse_ids(["ccc-q01-welcome, ccc-q01-a", "ccc-q01-b"]),
                         ["ccc-q01-welcome", "ccc-q01-a", "ccc-q01-b"])

    def test_malformed_repeated_or_empty_ids_are_rejected(self):
        for values in (["CCC_Q01"], ["a", "a"], [" , "], []):
            with self.subTest(values=values), self.assertRaises(pub.PublishError):
                pub.parse_ids(values)


class LiveIdsTests(unittest.TestCase):
    REGISTRY = {
        "ccc-q01-welcome": {"published_url": "u", "pdf": {"renderer": "welcome", "source": "w.json"}},
        "ccc-q01-guide": {"published_url": "u", "pdf": {"renderer": "teacher_guide", "output": "00-guide.pdf"}},
        "ccc-q01-key": {"published_url": "u", "pdf": {"renderer": "teacher_companion", "output": "key.pdf"}},
        "ccc-q01-draft": {"published_url": None, "pdf": {"renderer": "teacher_companion", "output": "draft.pdf"}},
        "ccc-q01-sheet": {"published_url": "u"},
        "ccc-q01-untouched": {"published_url": "u", "pdf": {"renderer": "teacher_guide", "output": "01-guide.pdf"}},
    }

    def test_affected_live_pdfs_publish_companions_first_and_welcome_last(self):
        outputs = ["ccc-q01-welcome.pdf", "00-guide.pdf", "key.pdf", "draft.pdf"]
        live, skipped = pub.live_ids_for_outputs(outputs, self.REGISTRY)
        self.assertEqual(live, ["ccc-q01-key", "ccc-q01-guide", "ccc-q01-welcome"])
        self.assertEqual(skipped, ["ccc-q01-draft"])

    def test_nothing_affected_publishes_nothing(self):
        self.assertEqual(pub.live_ids_for_outputs([], self.REGISTRY), ([], []))


class PublishManyTests(unittest.TestCase):
    def test_stops_at_first_failure_and_lists_unattempted_ids(self):
        calls = []

        def fake_publish(resource_id, dry_run=False, expected_revision=None):
            calls.append(resource_id)
            if resource_id == "b":
                raise pub.PublishError("no access")
            return {"resource_id": resource_id, "result": "replaced in place"}

        with patch.object(pub, "publish", fake_publish):
            reports = pub.publish_many(["a", "b", "c"])
        self.assertEqual(calls, ["a", "b"])
        self.assertEqual(reports[1], {"resource_id": "b", "result": "FAILED", "error": "no access"})
        self.assertEqual(reports[2], {"result": "not attempted", "resource_ids": ["c"]})

    def test_passes_dry_run_and_revision_through(self):
        seen = []

        def fake_publish(resource_id, dry_run=False, expected_revision=None):
            seen.append((resource_id, dry_run, expected_revision))
            return {"resource_id": resource_id}

        with patch.object(pub, "publish", fake_publish):
            pub.publish_many(["a", "b"], dry_run=True, expected_revision="f" * 40)
        self.assertEqual(seen, [("a", True, "f" * 40), ("b", True, "f" * 40)])


if __name__ == "__main__":
    unittest.main()
