import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'renderers'))

import teacher_companion  # noqa: E402

QUEST = ROOT / 'content/confetti-cake-cottage/quest-01-bake-off-betrayal'


class TeacherCompanionRendererTest(unittest.TestCase):
    def render(self, data, registry=None):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out.pdf'
            teacher_companion.generator(data, out, registry or {})
            return out.read_bytes()

    def template(self):
        data = json.loads((ROOT / 'templates/teacher_companion/TEMPLATE.json').read_text())
        data['_base'] = str(QUEST / 'resources/teacher_companion')
        return data

    def test_template_renders_every_block(self):
        data = self.template()
        registry = {'REGISTRY-ID': {'title': 'Example', 'url': 'https://example.org/x'}}
        self.assertTrue(self.render(data, registry).startswith(b'%PDF'))

    def test_activity_template_renders(self):
        data = json.loads((ROOT / 'templates/activity_guide/TEMPLATE.json').read_text())
        data['_base'] = str(QUEST / 'resources/teacher_companion')
        self.assertTrue(self.render(data).startswith(b'%PDF'))

    def test_long_and_short_pairs_tables_render(self):
        data = self.template()
        rows = [{'term': f'Term {i}', 'text': 'Text'} for i in range(9)]
        data['blocks'] = [{'type': 'heading', 'text': 'Short'}, {'type': 'pairs', 'items': rows[:3]},
                          {'type': 'heading', 'text': 'Long'}, {'type': 'pairs', 'items': rows},
                          {'type': 'heading', 'text': 'Tip'}, {'type': 'paragraph', 'text': 'One line.'}]
        self.assertTrue(self.render(data).startswith(b'%PDF'))

    def test_pairs_details_render(self):
        data = self.template()
        data['blocks'] = [{'type': 'heading', 'text': 'Choose one'},
                          {'type': 'pairs', 'items': [{'term': 'A · Design', 'details': [
                              ['Time', '20–30 min'], ['Prepare', 'A longer line of preparation that wraps ' * 3]]}]}]
        self.assertTrue(self.render(data).startswith(b'%PDF'))

    def test_option_overview_template_renders(self):
        data = json.loads((ROOT / 'templates/option_overview/TEMPLATE.json').read_text())
        data['_base'] = str(QUEST / 'resources/teacher_companion')
        self.assertTrue(self.render(data).startswith(b'%PDF'))

    def test_option_adds_section_suffix(self):
        data = self.template()
        data['option'] = 'b'
        label, _, _ = teacher_companion.section_info(data)
        self.assertTrue(label.endswith('OPTION B'))

    def test_bad_checklist_style_and_unknown_block_fail(self):
        for block in ({'type': 'checklist', 'style': 'circle', 'items': ['x']}, {'type': 'table'}):
            data = copy.deepcopy(self.template())
            data['blocks'] = [block]
            with self.assertRaises(ValueError):
                self.render(data)

    def test_overlong_step_title_line_fails(self):
        data = self.template()
        data['blocks'] = [{'type': 'steps', 'items': [
            {'title': 'A very long step title ' * 4, 'tag': 'Guide step 3', 'mins': '18–20 min', 'text': 'x'}]}]
        with self.assertRaises(ValueError):
            self.render(data)


if __name__ == '__main__':
    unittest.main()
