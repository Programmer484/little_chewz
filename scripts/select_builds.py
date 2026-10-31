#!/usr/bin/env python3
"""Select registered, eligible review PDFs from their actual inputs."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def nav_refs(value):
    """Registry IDs named by claude-style navigation rows (`resource` keys)."""
    if isinstance(value, dict):
        own = {value['resource']} if isinstance(value.get('resource'), str) else set()
        return own.union(*(nav_refs(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(nav_refs(v) for v in value))
    return set()


def generated_outputs(registry):
    """Explicit stable resource ID mapping for every Python-rendered PDF."""
    result = {}
    for rid, entry in registry.items():
        if entry.get('production_type') != 'generated_pdf':
            continue
        build = entry.get('build') or {}
        name = f'{rid}.pdf' if build.get('renderer') else build.get('output')
        if not name or not name.endswith('.pdf') or '/' in name:
            raise ValueError(f'{rid}: generated PDF has no valid output mapping')
        if name in result:
            raise ValueError(f'Duplicate generated PDF output {name}: {result[name]} and {rid}')
        result[name] = rid
    return result


def targets():
    """All existing lesson and companion sources are previewable; status tracks delivery."""
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
                status=lesson.get('status', 'unpublished'),
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
                status=record.get('status', 'unpublished'),
                data=data
            )
    # Registry entries with `build.renderer` are standalone documents (e.g. the Welcome PDF),
    # output as <resource-id>.pdf. Their whole source folder (icons, cover) is their input.
    for resource_id, record in registry.items():
        build = record.get('build') or {}
        if not build.get('renderer'):
            continue
        source = Path(build['source'])
        data = read_json(source.as_posix())
        name = f'{resource_id}.pdf'
        if name in result:
            raise ValueError(f'Duplicate output: {name}')
        status = record.get('status', 'unpublished')
        result[name] = dict(
            source=source.as_posix(), kind=build['renderer'], status=status,
            data=data,
            cover=(source.parent / data['cover']).as_posix() if data.get('cover') else None,
            folder=source.parent.as_posix()
        )
    mapping = generated_outputs(registry)
    missing = sorted(set(result) - set(mapping))
    extra = sorted(set(mapping) - set(result))
    if missing or extra:
        raise ValueError(f'Generated PDF mapping mismatch: missing {missing}; obsolete {extra}')
    for output, rid in mapping.items():
        result[output]['resource_id'] = rid
    return result


def changed_registry_ids(base_ref, fields=('title', 'url')):
    current = read_json('catalog/resources.json')
    if not base_ref:
        return set(current)
    old = json.loads(previous('catalog/resources.json', base_ref))
    return {key for key in old.keys() | current.keys()
            if any((old.get(key) or {}).get(f) != (current.get(key) or {}).get(f) for f in fields)}



def select(changed, base_ref=None):
    changed = {p.replace('\\', '/').removeprefix('./') for p in changed}
    registered = targets()
    selected = set()
    registry_changed = 'catalog/resources.json' in changed
    refs = changed_registry_ids(base_ref) if registry_changed else set()
    # Navigation rows link only published/pending_publish entries, so status matters there.
    nav_changed = changed_registry_ids(base_ref, ('title', 'url', 'status')) if registry_changed else set()
    builds_changed = changed_registry_ids(base_ref, ('build', 'production_type', 'source')) if registry_changed else set()
    # Conservative and simple: shared build/CI/dependency changes rebuild eligible PDFs.
    # This may create extra previews, but cannot miss a new rendering dependency.
    shared = bool(changed & {
        'scripts/build_selected.py', 'requirements.txt',
        '.github/workflows/build-resources.yml', '.github/actions/pdf-setup/action.yml',
    })
    for name, target in registered.items():
        kind = target['kind']
        dependencies = {target['source'], target.get('cover'), f'scripts/renderers/{kind}.py'}
        prefixes = [f'templates/{kind}/assets/']
        if kind in ('teacher_guide', 'teacher_companion'):
            prefixes.append('templates/fonts/')  # bundled Lato
        if kind == 'teacher_companion':
            dependencies.add('templates/claude/assets/crest.png')  # shared masthead crest
        if target.get('folder'):
            prefixes.append(target['folder'] + '/')
        affected = bool(changed & dependencies) or any(
            path.startswith(prefix) for path in changed for prefix in prefixes)
        if (shared or affected or target.get('resource_id') in builds_changed
                or refs & resource_refs(target['data'])
                or nav_changed & nav_refs(target['data'])):
            selected.add(name)
    return sorted(selected)


def selection(request=None, changed=(), base_ref=None):
    registered = targets()
    if request == 'all':
        names = sorted(registered)
    elif request:
        if request not in registered:
            raise ValueError(f'Unknown or missing-source PDF: {request}')
        names = [request]
    else:
        names = select(changed, base_ref)
    return {'outputs': names, 'source_paths': [registered[n]['source'] for n in names],
            'status': {n: registered[n]['status'] for n in names}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--changed', nargs='*', default=[])
    p.add_argument('--base-ref')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='All registered PDF sources')
    group.add_argument('--document', help='Output filename, or all')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    result = selection('all' if a.all else a.document, a.changed, a.base_ref)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
