"""Readable release outcomes and per-dependency explanations."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from format_release_report import blocked_rows, format_report


class ReleaseReportTests(unittest.TestCase):
    def test_blocked_dependencies_render_as_separate_plain_language_rows(self):
        result = {
            "pr": 122,
            "blocked": [{
                "resource_id": "teacher-guide",
                "reason": "teacher-guide: pre-publication inspection blocked: "
                          "songwriting: NEEDS REVIEW (Approved PDF checksum not recorded); "
                          "audio: NEEDS REVIEW (Cannot read Drive sharing permissions)"
            }]
        }
        summary = format_report(result)
        self.assertIn("| NEEDS REVIEW | songwriting |", summary)
        self.assertIn("| NEEDS REVIEW | audio |", summary)
        self.assertIn("verified baseline", summary)
        self.assertIn("exact URL", summary)
        self.assertIn("release-report.json", summary)
        self.assertNotIn("pre-publication inspection blocked:", summary)

    def test_success_table(self):
        summary = format_report({
            "pr": 1, "published": [{"resource_id": "teacher-guide"}], "blocked": []
        })
        self.assertIn("| Published | teacher-guide |", summary)
        self.assertNotIn("No publication recorded", summary)

    def test_other_blocker_shows_reason(self):
        self.assertEqual(blocked_rows("guide", "no approved link"),
                         [("Blocked", "guide", "no approved link")])


if __name__ == "__main__":
    unittest.main()
