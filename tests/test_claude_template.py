"""Smoke-test Welcome PDF output against authored pages and linked resources."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
WELCOME = ROOT / "content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json"
REGISTRY = ROOT / "catalog/resources.json"


class ClaudeTemplateTests(unittest.TestCase):
    def test_welcome_renders_authored_pages_with_navigation_links(self):
        source = json.loads(WELCOME.read_text())
        registry = json.loads(REGISTRY.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "welcome.pdf"
            subprocess.run([sys.executable, str(ROOT / "scripts/renderers/claude.py"),
                            str(WELCOME), "--output", str(out)],
                           check=True, capture_output=True)

            reader = PdfReader(str(out))
            offset = int(bool(source.get("cover")))
            # Count follows the authored source, not a stale literal.
            self.assertEqual(len(reader.pages), len(source["pages"]) + offset)
            if offset:
                self.assertTrue((WELCOME.parent / source["cover"]).is_file())
            for page_source, pdf_page in zip(source["pages"], reader.pages[offset:]):
                with self.subTest(page=page_source["title"]):
                    text = pdf_page.extract_text() or ""
                    self.assertIn(page_source["title"], text)
                    self.assertGreater(len(text.strip()), 30)

            links = []
            for page in reader.pages:
                for annotation in page.get("/Annots") or []:
                    action = annotation.get_object().get("/A")
                    if action:
                        url = action.get("/URI")
                        if url:
                            links.append(str(url))
            self.assertTrue(links)
            self.assertTrue(all(url.startswith("https://") for url in links))
            required = []
            for page in source["pages"]:
                for block in page["blocks"]:
                    if block["type"] != "nav":
                        continue
                    for item in block["items"]:
                        rid = item.get("resource")
                        if not rid:
                            continue
                        record = registry[rid]
                        if record["status"] in {"published", "pending_publish"}:
                            required.append(record["url"])
            self.assertTrue(required)
            for url in required:
                with self.subTest(destination=url):
                    self.assertIn(url, links)


if __name__ == "__main__":
    unittest.main()
