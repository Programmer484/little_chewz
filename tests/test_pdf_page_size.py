"""Printable PDF page-size verification: Letter portrait/landscape, all pages."""
import sys
import unittest
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pdf_page_size import check_letter


def pdf_bytes(*sizes):
    doc = fitz.open()
    for w, h in sizes:
        doc.new_page(width=w, height=h)
    data = doc.tobytes()
    doc.close()
    return data


class PageSizeTests(unittest.TestCase):
    def test_portrait_and_landscape_letter(self):
        check_letter(pdf_bytes((612, 792), (792, 612)))

    def test_reject_a4_and_mixed_page_sizes(self):
        for sizes in [[(595.28, 841.89)], [(612, 792), (595.28, 841.89)]]:
            with self.subTest(sizes=sizes):
                with self.assertRaisesRegex(ValueError, "US Letter"):
                    check_letter(pdf_bytes(*sizes))

    def test_allow_one_point_rounding_only(self):
        check_letter(pdf_bytes((612.4, 791.7)))
        with self.assertRaises(ValueError):
            check_letter(pdf_bytes((610, 792)))

    def test_invalid_pdf(self):
        with self.assertRaises(ValueError):
            check_letter(b"not a pdf")


if __name__ == "__main__":
    unittest.main()
