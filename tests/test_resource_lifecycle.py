"""Single derived resource lifecycle, independent of inspector health."""
import sys
import hashlib
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "renderers"))
from publication_state import identity, publication_status, status_report, lesson_status_report
from resource_links import resolve_url
from publication_checks import unpublished_references

HOLDING = "https://drive.google.com/file/d/123456789012345678901234/view"
OFFICIAL = "https://drive.google.com/file/d/abcdefghijklmnopqrstuvwx/view"


class ResourceLifecycleTests(unittest.TestCase):
    def test_external_state_depends_only_on_official_and_different_holding_link(self):
        draft = {"holding_url": HOLDING, "published_url": None}
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
        record = {"published_url": OFFICIAL, "holding_url": HOLDING,
                  "pdf": {"renderer": "teacher_guide", "output": "guide.pdf", "approved_md5": "a" * 32}}
        self.assertEqual(publication_status(record, "b" * 32), "pending_publish")
        self.assertEqual(publication_status(record, "a" * 32), "published")
        self.assertEqual(publication_status(record), "published")
        self.assertEqual(publication_status({**record, "pdf": {"renderer": "teacher_guide", "output": "guide.pdf"}}, "b" * 32),
                         "published")  # Missing baseline is inspection's NEEDS REVIEW.
        self.assertEqual(publication_status({**record, "published_url": None}, "b" * 32),
                         "unpublished")

    def test_generated_status_report_compares_real_current_pdf_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "current.pdf"
            pdf.write_bytes(b"first build")
            approved = hashlib.md5(b"first build").hexdigest()
            record = {"published_url": OFFICIAL,
                      "pdf": {"renderer": "teacher_guide", "output": "guide.pdf", "approved_md5": approved}}
            build = lambda *_: pdf
            self.assertEqual(status_report({"guide": record}, builder=build)[0]["status"],
                             "published")
            pdf.write_bytes(b"revised build")
            updated = status_report({"guide": record}, builder=build)[0]
            self.assertEqual(updated["status"], "pending_publish")
            self.assertEqual(updated["checksum_evidence"], "changed")
            record["pdf"].pop("approved_md5")
            unchecked = status_report({"guide": record}, builder=build)[0]
            self.assertEqual(unchecked["status"], "published")
            self.assertIn("NEEDS REVIEW", unchecked["checksum_evidence"])

    def test_lessons_use_their_registered_guide_not_quest_flags(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "guide.pdf"
            pdf.write_bytes(b"approved guide")
            approved = hashlib.md5(pdf.read_bytes()).hexdigest()
            registry = {
                "q-activate-teacher-guide": {
                    "pdf": {"renderer": "teacher_guide", "output": "00-activate-teacher-guide.pdf", "approved_md5": approved},
                    "published_url": OFFICIAL,
                },
                "q-table-teacher-guide": {
                    "pdf": {"renderer": "teacher_guide", "output": "01-set-the-table-teacher-guide.pdf"},
                    "published_url": None,
                },
            }
            quest = {"id": "q", "learning_sequence": [
                {"folder": "00-activate", "title": "Activate", "status": "unpublished"},
                {"folder": "01-set-the-table", "title": "Set the Table", "status": "published"},
                {"folder": "02-next", "title": "Next", "status": "published"},
            ]}
            index = {"school_index": [{"quest_manifest": "q/quest.json"}]}
            report = lambda: lesson_status_report(
                registry, index, lambda _: quest, builder=lambda *_: pdf)
            rows = report()
            self.assertEqual([row["status"] for row in rows],
                             ["published", "unpublished", "unpublished"])
            self.assertEqual(rows[0]["guide_resource_id"], "q-activate-teacher-guide")
            self.assertIsNone(rows[2]["guide_resource_id"])
            pdf.write_bytes(b"changed guide")
            self.assertEqual(report()[0]["status"], "pending_publish")
            registry["q-activate-teacher-guide"]["pdf"].pop("approved_md5")
            self.assertIn("NEEDS REVIEW", report()[0]["checksum_evidence"])

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
