"""Synthetic PDF → PPTX regression checks: link parity and page sizing."""
import sys
import tempfile
import unittest
from pathlib import Path

import fitz
from pptx import Presentation
from pptx.enum.action import PP_ACTION_TYPE

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pdf_to_linked_slides import convert


class PdfToLinkedSlidesTests(unittest.TestCase):
    def test_external_and_internal_links(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "input.pdf"
            pptx = Path(directory) / "output.pptx"
            doc = fitz.open()
            for number in (1, 2):
                page = doc.new_page(width=960, height=540)
                page.insert_text((40, 40), f"Slide {number}")
            url = "https://example.org/?one=1&two=2"
            doc[0].insert_link({
                "kind": fitz.LINK_URI,
                "uri": url,
                "from": fitz.Rect(60, 70, 220, 130),
            })
            doc[0].insert_link({
                "kind": fitz.LINK_GOTO,
                "page": 1,
                "to": fitz.Point(0, 0),
                "from": fitz.Rect(250, 70, 410, 130),
            })
            doc.save(pdf)
            doc.close()

            result = convert(pdf, pptx)
            self.assertTrue(result["verified"])
            self.assertEqual(result["slides"], 2)
            self.assertEqual(result["link_count"], 2)
            self.assertFalse(result["warnings"])
            presentation = Presentation(pptx)
            self.assertEqual(len(presentation.slides), 2)
            actions = [shape.click_action for shape in presentation.slides[0].shapes]
            self.assertEqual(sum(
                action.action == PP_ACTION_TYPE.HYPERLINK
                and action.hyperlink.address == url for action in actions
            ), 1)
            self.assertEqual(sum(
                action.action == PP_ACTION_TYPE.NAMED_SLIDE for action in actions
            ), 1)

    def test_mixed_page_aspect_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "bad.pdf"
            pptx = Path(directory) / "bad.pptx"
            doc = fitz.open()
            doc.new_page(width=960, height=540)
            doc.new_page(width=500, height=500)
            doc.save(pdf)
            doc.close()
            with self.assertRaisesRegex(ValueError, "Mixed-aspect"):
                convert(pdf, pptx)
            self.assertFalse(pptx.exists())


if __name__ == "__main__":
    unittest.main()
