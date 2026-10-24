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

GUIDE = '00-activate-teacher-guide.pdf'
DRAFT = '01-set-the-table-teacher-guide.pdf'
MISSION = 'mission-video-questions.pdf'
CONFETTI = 'confetti-file-questions.pdf'
SONG = 'songwriting-extension.pdf'


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.targets = sb.targets()

    def test_all_existing_sources_can_preview_without_flag(self):
        self.assertEqual(set(self.targets), {GUIDE, DRAFT, MISSION, CONFETTI, SONG})
        self.assertFalse(self.targets[DRAFT]['approved'])
        self.assertFalse(self.targets[SONG]['approved'])
        self.assertTrue(self.targets[GUIDE]['approved'])
        self.assertEqual(sb.selection(DRAFT)['outputs'], [DRAFT])
        self.assertEqual(sb.selection(SONG)['outputs'], [SONG])
        self.assertEqual(sb.selection('all-approved')['outputs'], [GUIDE, CONFETTI, MISSION])
        self.assertEqual(sb.selection(DRAFT)['status'][DRAFT], 'unapproved')
        self.assertEqual(sb.selection(GUIDE)['status'][GUIDE], 'approved')
        self.assertEqual(sb.selection(MISSION)['status'][MISSION], 'published')
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            sb.selection('missing.pdf')

    def test_sources_and_cover_are_targeted(self):
        for name, target in self.targets.items():
            for path in (target['source'], target.get('cover')):
                if path:
                    with self.subTest(path=path):
                        self.assertEqual(sb.select([path]), [name])

    def test_unconverted_stages_have_no_placeholder_build(self):
        for prefix in ['02-secret-ingredients', '03-the-showdown', '04-chew-on-this',
                       '05-plate-it-forward', '06-celebrate']:
            self.assertFalse(any(name.startswith(prefix) for name in self.targets))

    def test_renderer_consumers(self):
        for kind in ['teacher_guide', 'teacher_companion']:
            expected = sorted(n for n, t in self.targets.items() if t['kind'] == kind)
            self.assertEqual(sb.select([f'scripts/renderers/{kind}.py']), expected)

    def test_checks_and_metadata_do_not_render(self):
        for path in ['scripts/validate.py', 'scripts/select_builds.py',
                     'tests/test_select_builds.py',
                     'system/action_labels.json', 'system/EDITORIAL_GUIDE.md',
                     'content/story/story.md', 'content/worksheet.json', 'content/slides.json',
                     'README.md', 'content/confetti-cake-cottage/quest-01-bake-off-betrayal/quest.json',
                     'content/confetti-cake-cottage/quest-01-bake-off-betrayal/lessons/02-secret-ingredients/stage.json']:
            with self.subTest(path=path):
                self.assertEqual(sb.select([path]), [])

    def test_shared_build_inputs_rebuild_all_eligible_sources(self):
        for path in ['scripts/build_selected.py', 'requirements.txt',
                     '.github/workflows/build-resources.yml']:
            with self.subTest(path=path):
                self.assertEqual(set(sb.select([path])), set(self.targets))

    def test_registry_keys_are_only_ids(self):
        records=sb.read_json('catalog/resources.json')
        self.assertEqual(len(records),20)
        self.assertFalse(any('resource_id' in item or 'legacy_alias' in item for item in records.values()))
        self.assertEqual(records['ccc-q01-set-the-table-slides']['status'],'unapproved')
        self.assertTrue(records['ccc-q01-set-the-table-slides']['powerpoint_file_id'])

    def test_registry_status_only_does_not_trigger_rebuild(self):
        path='catalog/resources.json'
        old=sb.read_json(path)
        altered=copy.deepcopy(old)
        altered['ccc-q01-set-the-table-slides']['status']='published'
        with patch.object(sb, 'previous', return_value=json.dumps(altered)):
            self.assertEqual(sb.select([path], 'base'), [])
        altered['ccc-q01-set-the-table-slides']['url']='https://example.com/new'
        with patch.object(sb, 'previous', return_value=json.dumps(altered)):
            self.assertEqual(sb.select([path], 'base'), [DRAFT])

    def test_registry_dependency_consumer_scope(self):
        targets=copy.deepcopy(self.targets)
        targets[DRAFT]['data']['extra']={'ref': 'ccc-q01-mrs-tongsleys-letter'}
        with patch.object(sb, 'targets', return_value=targets), patch.object(
                sb, 'changed_registry_ids', return_value={'ccc-q01-mrs-tongsleys-letter'}):
            self.assertEqual(sb.select(['catalog/resources.json'], 'base'), [GUIDE, DRAFT])

    def test_source_metadata_edit_rebuilds_only_its_pdf(self):
        # Simpler selection favors an occasional redundant preview over diff logic.
        target=self.targets[DRAFT]
        self.assertEqual(sb.select([target['source']]), [DRAFT])

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
            source.write_text(json.dumps(data))
            run=subprocess.run([sys.executable, str(root/'scripts/validate.py')],
                               capture_output=True, text=True)
            self.assertNotEqual(run.returncode,0)
            for error in ['missing visual cover','step IDs not consecutive',
                          'unsupported action label','missing catalog resource ref']:
                self.assertIn(error,run.stdout)

    def test_history_branch_has_run_scoped_immutable_paths(self):
        workflow=(sb.ROOT / '.github/workflows/build-resources.yml').read_text()
        self.assertIn('preview_branch="pdf-preview-history"', workflow)
        self.assertIn('run_folder="previews/${RUN_ID}"', workflow)
        self.assertIn('git push origin "HEAD:refs/heads/$preview_branch"', workflow)



if __name__=='__main__':
    unittest.main()
