"""Integration tests for immutable, run-scoped PDF preview history."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = ROOT / "scripts/publish_pdf_previews.sh"
HISTORY_REF = "refs/heads/pdf-preview-history"


class PreviewHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.work = self.root / "work"
        subprocess.run(["git", "init", "--bare", str(self.remote)],
                       check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.work)],
                       check=True, capture_output=True)
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")
        (self.work / "README.md").write_text("main branch\n")
        self.git("add", "README.md")
        self.git("commit", "-m", "initial")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-u", "origin", "main")
        self.original_head = self.git("rev-parse", "HEAD").stdout.strip()
        (self.work / "exports").mkdir()
        self.summary = self.root / "summary.md"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.work), *args],
                              check=True, capture_output=True, text=True)

    def preview(self, run_id, data):
        (self.work / "exports/lesson.pdf").write_bytes(data)
        env = {**os.environ, "RUN_ID": str(run_id),
               "REPO": "example/little_chewz",
               "GITHUB_STEP_SUMMARY": str(self.summary)}
        return subprocess.run(["bash", str(PUBLISHER)],
                              cwd=self.work, env=env,
                              capture_output=True, text=True)

    def history_paths(self):
        result = subprocess.run(
            ["git", "--git-dir", str(self.remote), "ls-tree", "-r",
             "--name-only", HISTORY_REF],
            check=True, capture_output=True, text=True)
        return result.stdout.splitlines()

    def historical_pdf(self, run_id):
        return subprocess.check_output([
            "git", "--git-dir", str(self.remote),
            "show", f"{HISTORY_REF}:previews/{run_id}/lesson.pdf"])

    def test_runs_append_under_distinct_paths_and_restore_checkout(self):
        self.assertEqual(self.preview(1001, b"first PDF").returncode, 0)
        self.assertEqual(self.preview(1002, b"second PDF").returncode, 0)
        self.assertEqual(self.history_paths(), [
            "previews/1001/lesson.pdf", "previews/1002/lesson.pdf"])
        self.assertEqual(self.historical_pdf(1001), b"first PDF")
        self.assertEqual(self.historical_pdf(1002), b"second PDF")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(),
                         self.original_head)
        self.assertIn("previews/1002/lesson.pdf", self.summary.read_text())

    def test_same_run_id_never_overwrites_existing_preview(self):
        self.assertEqual(self.preview(2001, b"original").returncode, 0)
        attempt = self.preview(2001, b"replacement")
        self.assertNotEqual(attempt.returncode, 0)
        self.assertIn("already exists", attempt.stdout + attempt.stderr)
        self.assertEqual(self.history_paths(), ["previews/2001/lesson.pdf"])
        self.assertEqual(self.historical_pdf(2001), b"original")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(),
                         self.original_head)


if __name__ == "__main__":
    unittest.main()
