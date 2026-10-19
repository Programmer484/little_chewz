"""Regression checks for dependency selection and draft eligibility."""
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

GUIDE = '00-activate-teacher-guide.pdf'
DRAFT = '01-set-the-table-teacher-guide.pdf'
MISSION = 'mission-video-questions.pdf'
CONFETTI = 'confetti-file-questions.pdf'


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.targets = sb.targets()

    def test_sources_and_cover_are_targeted(self):
        for name, target in self.targets.items():
            for path in [target['source'], target.get('cover')]:
                if path:
                    with self.subTest(path=path):
                        self.assertEqual(sb.select([path]), [name])

    def test_renderer_consumers(self):
        for kind in ['teacher_guide', 'teacher_companion']:
            expected = sorted(n for n, t in self.targets.items() if t['kind'] == kind)
            self.assertEqual(sb.select([f'scripts/renderers/{kind}.py']), expected)

    def test_checks_and_unrelated_files_do_not_render(self):
        for path in ['scripts/validate.py', 'scripts/select_builds.py', 'scripts/build.py',
                     '.github/workflows/build-resources.yml', 'tests/test_select_builds.py',
                     'system/action_labels.json', 'system/EDITORIAL_GUIDE.md',
                     'templates/lesson/TEMPLATE.json', 'content/story/story.md',
                     'content/worksheet.json', 'content/slides.json', 'README.md']:
            with self.subTest(path=path):
                self.assertEqual(sb.select([path]), [])

    def test_shared_builder_and_dependencies(self):
        self.assertEqual(set(sb.select(['scripts/build_selected.py'])), set(self.targets))
        self.assertEqual(set(sb.select(['requirements.txt'])), set(self.targets))
        with patch.object(sb, 'previous', return_value='PyMuPDF==1.26.7\nreportlab==4.4.8\n'):
            self.assertEqual(sb.select(['requirements.txt'], 'base'), [CONFETTI, MISSION])

    def test_registry_targets_two_consumers(self):
        targets = copy.deepcopy(self.targets)
        targets[DRAFT]['data']['extra'] = {'ref': 'ccc-q01-mrs-tongsleys-letter'}
        with patch.object(sb, 'targets', return_value=targets), patch.object(sb, 'changed_registry_ids', return_value={'ccc-q01-mrs-tongsleys-letter'}):
            self.assertEqual(sb.select(['catalog/resources.json'], 'base'), [GUIDE, DRAFT])
        with patch.object(sb, 'changed_registry_ids', return_value={'unused'}):
            self.assertEqual(sb.select(['catalog/resources.json'], 'base'), [])

    def test_manual_requests_and_disabled_drafts(self):
        self.assertEqual(sb.selection('all-approved')['outputs'], [GUIDE, CONFETTI, MISSION])
        self.assertEqual(sb.selection(DRAFT)['outputs'], [DRAFT])
        with self.assertRaisesRegex(ValueError, 'preview-disabled'):
            sb.selection('songwriting-extension.pdf')
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            sb.selection('missing.pdf')

    def test_new_draft_discovered_without_selector_changes(self):
        original = sb.read_json
        def read(path):
            data = original(path)
            if str(path).endswith('stage.json') and '01-set-the-table' in str(path):
                data['preview_enabled'] = False
            return data
        with patch.object(sb, 'read_json', side_effect=read):
            self.assertNotIn(DRAFT, sb.targets())
        self.assertIn(DRAFT, sb.targets())

    def test_source_metadata_does_not_render(self):
        target = self.targets[MISSION]
        old = dict(target['data'], source_note='previous note')
        with patch.object(sb, 'previous', return_value=json.dumps(old)):
            self.assertEqual(sb.select([target['source']], 'base'), [])

    def test_enabling_preview_builds_only_draft(self):
        stage = self.targets[DRAFT]['stage']
        with patch.object(sb, 'previous', return_value='{"preview_enabled": false}'):
            self.assertEqual(sb.select([stage], 'base'), [DRAFT])
        with patch.object(sb, 'previous', return_value='{"preview_enabled": true}'):
            self.assertEqual(sb.select([stage], 'base'), [])

    def test_draft_validation_catches_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ['scripts', 'catalog', 'system', 'content']:
                shutil.copytree(sb.ROOT / folder, root / folder)
            source = root / self.targets[DRAFT]['source']
            data = json.loads(source.read_text())
            data['cover'] = 'missing-cover.png'
            data['steps'][0]['id'] = 99
            data['steps'][0]['rows'][0]['kind'] = 'INVALID'
            data['core'][0]['ref'] = 'missing-resource'
            source.write_text(json.dumps(data))
            run = subprocess.run([sys.executable, str(root / 'scripts/validate.py')], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            for error in ['missing visual cover', 'step IDs not consecutive', 'unsupported action label', 'missing catalog resource ref']:
                self.assertIn(error, run.stdout)

    def test_workflow_changes_only_render_for_environment(self):
        path = '.github/workflows/build-resources.yml'
        with patch.object(sb.subprocess, 'check_output', return_value='+          retention-days: 5\n'):
            self.assertEqual(sb.select([path], 'base'), [])
        with patch.object(sb.subprocess, 'check_output', return_value='+          python-version: "3.12"\n'):
            self.assertEqual(set(sb.select([path], 'base')), set(self.targets))


if __name__ == '__main__':
    unittest.main()
