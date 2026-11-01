"""Render the Welcome document with the welcome template, using only requirements.txt."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
WELCOME = ROOT / "content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json"


class WelcomeTemplateTests(unittest.TestCase):
    def test_welcome_renders_with_cover_and_navigation_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "welcome.pdf"
            subprocess.run([sys.executable, str(ROOT / "scripts/renderers/welcome.py"), str(WELCOME),
                            "--output", str(out)], check=True, capture_output=True)
            reader = PdfReader(str(out))
            self.assertEqual(len(reader.pages), 6)
            uris = [a.get_object()["/A"].get("/URI") for a in reader.pages[-1].get("/Annots") or []]
            self.assertTrue(uris and all(u.startswith("https://") for u in uris))


if __name__ == "__main__":
    unittest.main()
