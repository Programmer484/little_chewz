"""Celebrate template: renderer output, source checks, and build selection."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'renderers'))
import celebrate  # noqa: E402
import select_builds as sb  # noqa: E402
from resource_links import resolved_registry  # noqa: E402

TEMPLATE = ROOT / 'templates' / 'celebrate' / 'TEMPLATE.json'
COVER = ROOT / 'content/confetti-cake-cottage/quest-01-bake-off-betrayal/lessons/06-celebrate/cover.pdf'
REGISTRY = json.loads((ROOT / 'catalog/resources.json').read_text())
SLIDES, BADGES, PASSPORT = 'ccc-q01-celebrate-slides', 'ccc-q01-celebrate-quest-one-badges', 'ccc-school-pass-instructions'


def lesson(steps=4, finale_steps=1):
    """A filled-in copy of TEMPLATE.json using real catalogue resources."""
    d = json.loads(TEMPLATE.read_text())
    d['core'] = [{'ref': SLIDES, 'description': 'Slides 1–12'}]
    d['optional_prep'] = [{'ref': PASSPORT, 'description': 'M and L, if using'}]
    d['spot_art'] = {'images': ['assets/prop-a.png', 'assets/prop-b.png'], 'caption': 'Props'}
    d['steps'] = [{'id': i, 'title': f'Step {i}', 'mins': '5', 'sizes': ['S', 'M', 'L'] if i == 1 else ['L'],
                   'rows': [{'kind': 'SHOW', 'text': f'Slide {i} — Show it.'},
                            {'kind': 'GIVE', 'ref': BADGES, 'description': 'One per student', 'quantity': 'per_student'},
                            {'kind': 'DO', 'text': 'One concrete classroom direction that is long enough to wrap onto a second line of the flow.'}]}
                  for i in range(1, steps + 1)]
    d['finale'].update(badge='assets/badge.png', line='Strong teams learn, adapt, and rebuild.', step_count=finale_steps)
    return d


class CelebrateRendererTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / 'assets').mkdir()
        for name, size in (('prop-a', (300, 200)), ('prop-b', (120, 240)), ('badge', (200, 200))):
            Image.new('RGBA', size, (230, 102, 84, 255)).save(self.tmp / 'assets' / f'{name}.png')
        shutil.copy(COVER, self.tmp / 'cover.pdf')
        self.registry = resolved_registry(REGISTRY)

    def render(self, data):
        path = self.tmp / 'lesson.json'
        path.write_text(json.dumps(data))
        out, pages = celebrate.Guide(path, self.registry).render(self.tmp / 'out.pdf')
        return PdfReader(str(out)), pages

    def test_template_declares_its_renderer(self):
        self.assertEqual(json.loads(TEMPLATE.read_text())['template'], 'celebrate')
        self.assertTrue((ROOT / 'templates/celebrate/assets/celebrate-stamp.png').is_file())

    def test_renders_cover_overview_sizes_flow_and_finale_with_registry_links(self):
        pdf, pages = self.render(lesson())
        self.assertEqual(len(pdf.pages), pages)
        self.assertEqual(pages, 5)  # cover, At a Glance, sizes, one flow page, finale
        text = [page.extract_text() for page in pdf.pages]
        self.assertIn('AT A GLANCE', text[1])
        self.assertIn('CHOOSE YOUR SIZE', text[2])
        self.assertIn('Teaching Flow', text[3])
        self.assertIn('Mission complete', text[4])
        self.assertIn('05 / 05', text[4])
        self.assertIn('Step 4', text[4])  # finale holds the last step
        uris = {annot.get_object()['/A']['/URI'] for page in pdf.pages for annot in page.get('/Annots') or []
                if annot.get_object().get('/A')}
        expected = {self.registry[ref]['url'] for ref in (SLIDES, BADGES, PASSPORT)}
        self.assertEqual(uris, expected)
        self.assertTrue(all(uri.startswith('https://') for uri in uris))

    def test_long_flows_paginate_whole_steps(self):
        pdf, pages = self.render(lesson(steps=9, finale_steps=1))
        self.assertGreater(pages, 5)
        self.assertIn('CONTINUED ON NEXT PAGE', pdf.pages[3].extract_text())

    def test_without_cover_or_finale(self):
        data = lesson(); data.pop('cover'); data.pop('finale')
        pdf, pages = self.render(data)
        self.assertEqual(pages, 3)
        self.assertIn('01 / 03', pdf.pages[0].extract_text())

    def test_source_errors_fail_loudly(self):
        cases = {
            'undefined sizes': lambda d: d['steps'][0].update(sizes=['XL']),
            'step_count': lambda d: d['finale'].update(step_count=len(d['steps'])),
            'unknown resource': lambda d: d['core'].append({'ref': 'not-a-resource'}),
            'action label': lambda d: d['steps'][0]['rows'].append({'kind': 'NOTE', 'text': 'x'}),
            'consecutive': lambda d: d['steps'][1].update(id=7),
        }
        for message, mutate in cases.items():
            with self.subTest(message=message):
                data = lesson(); mutate(data)
                with self.assertRaisesRegex(ValueError, message):
                    self.render(data)


class CelebrateSelectionTests(unittest.TestCase):
    def test_lesson_template_selects_celebrate_renderer(self):
        original = sb.read_json

        def as_celebrate(path):
            data = original(path)
            if str(path).endswith('06-celebrate/lesson.json'):
                data = copy.deepcopy(data); data['template'] = 'celebrate'
            return data

        with patch.object(sb, 'read_json', as_celebrate):
            targets = sb.targets()
        self.assertEqual(targets['06-celebrate-teacher-guide.pdf']['kind'], 'celebrate')
        self.assertEqual(targets['00-activate-teacher-guide.pdf']['kind'], 'teacher_guide')


if __name__ == '__main__':
    unittest.main()
