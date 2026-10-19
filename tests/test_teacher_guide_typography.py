"""Ensure Teacher Guide MORE rows use the same font size as regular instructions."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "renderers"))
import teacher_guide as guide


class TeachingFlowTypographyTests(unittest.TestCase):
    def test_more_title_and_description_match_do_body_size(self):
        step = {
            "id": 1,
            "title": "Optional resource",
            "mins": "3",
            "rows": [
                {"kind": "MORE", "ref": "test-resource", "description": "Extra material"},
                {"kind": "DO", "text": "Discuss the resource."},
            ],
        }
        # Inspect the arguments passed by the shared renderer, without
        # requiring any graphic/pdf output or installed fonts for this test.
        with (
            patch.object(guide, "step_begin", return_value=0),
            patch.object(guide, "label"),
            patch.object(guide, "resource_line", return_value=12) as linked,
            patch.object(guide, "para", return_value=12) as body,
        ):
            guide.draw_step(None, step, 0, {})

        linked_size = linked.call_args.kwargs["size"]
        description_size = linked.call_args.kwargs["description_size"]
        body_size = body.call_args.kwargs["size"]
        self.assertEqual(linked_size, guide.FLOW_BODY_SIZE)
        self.assertEqual(description_size, linked_size)
        self.assertEqual(body_size, linked_size)


if __name__ == "__main__":
    unittest.main()
