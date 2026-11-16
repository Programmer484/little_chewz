"""Welcome's inline links must remain clickable across line breaks."""
import io
import sys
import unittest
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from renderers import welcome


class WelcomeLinksTests(unittest.TestCase):
    def test_wrapped_link_has_an_annotation_per_line(self):
        stream = io.BytesIO()
        pdf = canvas.Canvas(stream)
        text = "Pre-Pilot Questionnaire"
        url = "https://forms.gle/GkwBH7WpVPPw3Lin9"
        font, size = "Helvetica", 11.5
        max_width = welcome.width("Questionnaire", font, size) + 1
        welcome.text_block(pdf, 50, 700, text, font, size, 16.5,
                           max_width, welcome.BODY_INK)
        welcome.underline_link(pdf, text, {"text": text, "url": url},
                               50, 700, font, size, 16.5, max_width)
        pdf.showPage()
        pdf.save()
        annotations = PdfReader(io.BytesIO(stream.getvalue())).pages[0]["/Annots"]
        self.assertEqual(len(annotations), 2)
        for annotation in annotations:
            self.assertEqual(annotation.get_object()["/A"]["/URI"], url)

    def test_non_https_link_rejected(self):
        pdf = canvas.Canvas(io.BytesIO())
        with self.assertRaises(ValueError):
            welcome.underline_link(pdf, "Link", {"text": "Link", "url": "http://example.com"},
                                   50, 700, "Helvetica", 11.5, 16.5, 100)


if __name__ == "__main__":
    unittest.main()
