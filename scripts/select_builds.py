#!/usr/bin/env python3
"""Select registered, eligible review PDFs from their actual inputs."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA = {'source_note', 'unresolved', 'published_ref', 'migration_review'}


def read_json(path):
    return json.loads((ROOT / path).read_text())


def previous(path, base_ref):
    return subprocess.check_output(['git', 'show', f'{base_ref}:{path}'], cwd=ROOT, text=True)


def resource_refs(value):
    if isinstance(value, dict):
        return ({value['ref']} if isinstance(value.get('ref'), str) else set()).union(
            *(resource_refs(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(resource_refs(v) for v in value))
    return set()


def targets():
    """All existing lesson and companion sources are previewable; status controls release."""
    result = {}
    registry = read_json('catalog/resources.json')
    for school in read_json('catalog/quests.json')['school_index']:
        quest_path = school['quest_manifest']
        quest = read_json(quest_path)
        root = Path(quest_path).parent
        for lesson in quest['learning_sequence']:
            folder = root / 'lessons' / lesson['folder']
            source = folder / 'lesson.json'
            if not (ROOT / source).is_file():
                continue  # No placeholder PDF for an unconverted lesson.
            data = read_json(source.as_posix())
            name = f"{lesson['folder']}-teacher-guide.pdf"
            if name in result:
                raise ValueError(f'Duplicate output: {name}')
            result[name] = dict(
                source=source.as_posix(), kind='teacher_guide',
                approved=lesson.get('status', 'unapproved') in ('approved', 'published'),
                data=data, cover=(folder / data['cover']).as_posix()
            )
        for source in sorted((ROOT / root / 'resources/teacher_companion').glob('*.json')):
            data = json.loads(source.read_text())
            resource_id = data.get('resource_id')
            record = registry.get(resource_id)
            if record is None:
                raise ValueError(f'Companion has no registry entry: {resource_id}')
            name = source.stem + '.pdf'
            if name in result:
                raise ValueError(f'Duplicate output: {name}')
            result[name] = dict(
                source=source.relative_to(ROOT).as_posix(), kind='teacher_companion',
                approved=record.get('status', 'unapproved') in ('approved', 'published'), data=data
            )
    return result


def changed_registry_ids(base_ref):
    current = read_json('catalog/resources.json')
    if not base_ref:
        return set(current)
    old = json.loads(previous('catalog/resources.json', base_ref))
    return {key for key in old.keys() | current.keys()
            if (old.get(key) or {}).get('title') != (current.get(key) or {}).get('title')
            or (old.get(key) or {}).get('url') != (current.get(key) or {}).get('url')}


def output_source(data):
    return {key: value for key, value in data.items() if key not in METADATA}


def select(changed, base_ref=None):
    changed = {p.replace('\\', '/').removeprefix('./') for p in changed}
    registered = targets()
    selected = set()
    refs = changed_registry_ids(base_ref) if 'catalog/resources.json' in changed else set()
    shared = 'scripts/build_selected.py' in changed
    # Only rendering environment changes in workflow configuration affect PDFs.
    if '.github/workflows/build-resources.yml' in changed and base_ref:
        diff = subprocess.check_output(['git', 'diff', '--unified=0', base_ref, '--', '.github/workflows/build-resources.yml'], cwd=ROOT, text=True)
        shared |= any(re.search(r'runs-on:|python-version:|pip install|apt-get|fonts-|FONT_DIR|LITTLE_CHEWZ|scripts/renderers/|scripts/build_selected.py|working-directory:|container:', line)
                      for line in diff.splitlines() if line.startswith(('+', '-')))
    packages = set()
    if 'requirements.txt' in changed:
        current = (ROOT / 'requirements.txt').read_text().splitlines()
        old = previous('requirements.txt', base_ref).splitlines() if base_ref else []
        packages = {re.split(r'[=<>!~\[]', line)[0].lower() for line in set(current) ^ set(old) if line and not line.startswith('#')}
    shared |= bool(packages - {'pymupdf', 'reportlab'})
    for name, target in registered.items():
        kind = target['kind']
        dependencies = {target['source'], target.get('cover'), f'scripts/renderers/{kind}.py'}
        affected = bool(changed & dependencies)
        if target['source'] in changed and base_ref:
            try:
                old = json.loads(previous(target['source'], base_ref))
            except subprocess.CalledProcessError:  # New source file.
                pass
            else:
                affected = bool(changed & (dependencies - {target['source']})) or output_source(old) != output_source(target['data'])
        if shared or affected or refs & resource_refs(target['data']) or ('pymupdf' in packages if kind == 'teacher_guide' else 'reportlab' in packages):
            selected.add(name)
    return sorted(selected)


def selection(request=None, changed=(), base_ref=None):
    registered = targets()
    if request == 'all-approved':
        names = sorted(name for name, t in registered.items() if t['approved'])
    elif request:
        if request not in registered:
            raise ValueError(f'Unknown or missing-source PDF: {request}')
        names = [request]
    else:
        names = select(changed, base_ref)
    return {'outputs': names, 'source_paths': [registered[n]['source'] for n in names],
            'review_status': {n: 'approved_source' if registered[n]['approved'] else 'draft_preview' for n in names}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--changed', nargs='*', default=[])
    p.add_argument('--base-ref')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='All approved PDFs only')
    group.add_argument('--document', help='Output filename, or all-approved')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    result = selection('all-approved' if a.all else a.document, a.changed, a.base_ref)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
