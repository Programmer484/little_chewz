"""Regression checks for one-status-per-item preview selection."""
import copy
import json
import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import select_builds as sb

DRAFT = '01-set-the-table-teacher-guide.pdf'


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.targets = sb.targets()

    def test_all_existing_sources_can_preview_without_flag(self):
        self.assertTrue(self.targets)
        self.assertEqual(sb.selection('all')['outputs'], sorted(self.targets))
        for name in self.targets:
            with self.subTest(output=name):
                self.assertEqual(sb.selection(name)['outputs'], [name])
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            sb.selection('missing.pdf')

    def test_sources_and_cover_are_targeted(self):
        for name, target in self.targets.items():
            for path in (target['source'], target.get('cover')):
                if path:
                    with self.subTest(path=path):
                        self.assertEqual(sb.select([path]), [name])

        source = self.targets[DRAFT]['source']
        cover = self.targets[DRAFT]['cover']
        files, _ = sb.input_paths({'source': source, 'data': {'new_block': {
            'any_field_name': Path(cover).name}}})
        self.assertIn(cover, files)

    def test_lesson_targets_match_existing_sources(self):
        # Preview eligibility is based on an authored lesson.json, never
        # duplicated lesson publication status in quest.json or a build manifest.
        expected = {}
        for school in sb.read_json('catalog/quests.json')['school_index']:
            manifest = Path(school['quest_manifest'])
            quest = sb.read_json(manifest.as_posix())
            for lesson in quest['learning_sequence']:
                self.assertNotIn('status', lesson)
                source = manifest.parent / 'lessons' / lesson['folder'] / 'lesson.json'
                if (sb.ROOT / source).is_file():
                    expected[f"{lesson['folder']}-teacher-guide.pdf"] = source.as_posix()
        actual = {name: target['source'] for name, target in self.targets.items()
                  if target['kind'] == 'teacher_guide'}
        self.assertEqual(actual, expected)
        self.assertTrue(all('status' not in target for target in self.targets.values()))
        self.assertNotIn('status', sb.selection('all'))

    def test_teacher_guide_template_and_sources_have_no_duplicate_output(self):
        template = sb.read_json('templates/teacher_guide/TEMPLATE.json')
        self.assertNotIn('output', template)
        for field in ('assessment', 'prep_heading', 'prep_note', 'flow_style',
                      'bonuses', 'bonus_heading', 'bonus_rows', 'colored_section_titles'):
            self.assertIn(field, template)

        registry = sb.read_json('catalog/resources.json')
        for name, target in self.targets.items():
            if target['kind'] != 'teacher_guide':
                continue
            with self.subTest(source=target['source']):
                self.assertNotIn('output', target['data'])
                self.assertEqual(registry[target['resource_id']]['pdf']['output'], name)

    def test_renderer_consumers(self):
        for kind in {t['kind'] for t in self.targets.values()}:
            expected = sorted(n for n, t in self.targets.items() if t['kind'] == kind)
            self.assertEqual(sb.select([f'scripts/renderers/{kind}.py']), expected)

    def test_every_generated_pdf_has_explicit_registered_build_and_source(self):
        records=sb.read_json('catalog/resources.json')
        mapping=sb.generated_outputs(records)
        self.assertEqual(set(mapping), set(self.targets))
        for output, resource_id in mapping.items():
            self.assertEqual(self.targets[output]['resource_id'], resource_id)
            self.assertIn(records[resource_id]['pdf']['renderer'], {'teacher_guide', 'teacher_companion', 'welcome'})
        self.assertTrue(all('pdf' not in item
                            for item in records.values() if item.get('pdf') is None))

    def test_registry_link_change_rebuilds_consumers(self):
        path = 'catalog/resources.json'
        rid = 'ccc-q01-set-the-table-slides'
        previous = copy.deepcopy(sb.read_json(path))
        previous['ccc-q01-secret-ingredients-teacher-guide']['pdf']['approved_md5'] = "f" * 32
        with patch.object(sb, 'previous', return_value=json.dumps(previous)):
            self.assertEqual(sb.select([path], 'base'), [])

        previous[rid]['published_url'] = 'https://example.com/old-link'
        consumers = sorted(name for name, target in self.targets.items()
                           if rid in sb.resource_refs(target['data']))
        self.assertTrue(consumers)
        with patch.object(sb, 'previous', return_value=json.dumps(previous)):
            self.assertEqual(sb.select([path], 'base'), consumers)

    def test_templates_are_starters_and_assets_are_scoped(self):
        cases = {
            'templates/teacher_guide/TEMPLATE.json': set(),
            'templates/teacher_companion/TEMPLATE.json': set(),
            'templates/welcome/TEMPLATE.json': set(),
            'templates/fonts/Lato-Regular.ttf': {'teacher_guide', 'teacher_companion'},
            'templates/welcome/assets/crest.png': {'welcome', 'teacher_companion'},
            'templates/welcome/assets/little-chewz-logo.png': {'welcome'},
            'templates/welcome/assets/fonts/Outfit-Regular.ttf': {'welcome'},
        }
        for path, kinds in cases.items():
            with self.subTest(path=path):
                expected = sorted(n for n, t in self.targets.items() if t['kind'] in kinds)
                self.assertEqual(sb.select([path]), expected)

    def test_draft_validation_catches_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for folder in ['scripts','catalog','system','content']:
                shutil.copytree(sb.ROOT / folder, root / folder)
            source=root / self.targets[DRAFT]['source']
            data=json.loads(source.read_text())
            data['cover']='missing-cover.png'
            data['steps'][0]['id']=99
            data['steps'][0]['rows'][0]['kind']='INVALID'
            data['core'][0]['ref']='missing-resource'
            data['template'] = 'missing-template'
            source.write_text(json.dumps(data))
            quest_path=root/'content/confetti-cake-cottage/quest-01-bake-off-betrayal/quest.json'
            quest=json.loads(quest_path.read_text())
            quest['learning_sequence'][0]['status']='published'
            quest_path.write_text(json.dumps(quest))
            run=subprocess.run([sys.executable, str(root/'scripts/validate.py')],
                               capture_output=True, text=True)
            self.assertNotEqual(run.returncode,0)
            for error in ['missing visual cover','step IDs not consecutive',
                          'unsupported action label','missing catalog resource ref',
                          'must declare "template"',
                          'unexpected metadata fields']:
                self.assertIn(error,run.stdout)

if __name__=='__main__':
    unittest.main()
