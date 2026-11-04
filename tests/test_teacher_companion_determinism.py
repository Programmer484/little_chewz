"""Regression: repeated companion renders must have identical PDF bytes."""
from io import BytesIO
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "renderers"))
from teacher_companion import counted_canvas


class CompanionPDFDeterminismTests(unittest.TestCase):
    def test_doctemplate_invariant_none_does_not_randomize_pdf_id(self):
        canvas_type = counted_canvas(lambda canvas, page, total: None)
        results = []
        for _ in range(2):
            stream = BytesIO()
            canvas = canvas_type(stream, invariant=None)
            canvas.drawString(24, 50, "Deterministic companion")
            canvas.showPage()
            canvas.save()
            results.append(stream.getvalue())
        self.assertEqual(results[0], results[1])
        self.assertTrue(results[0].startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
