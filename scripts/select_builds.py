#!/usr/bin/env python3
"""Select registered, eligible review PDFs from their actual inputs."""
import argparse
import ast
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
    """Registry IDs named by welcome-style navigation rows (`resource` keys)."""
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
        if not entry.get('pdf'):
            continue
        build = entry.get('pdf') or {}
        name = build.get('output') or f'{rid}.pdf'
        if not name or not name.endswith('.pdf') or '/' in name:
            raise ValueError(f'{rid}: generated PDF has no valid output mapping')
        if name in result:
            raise ValueError(f'Duplicate generated PDF output {name}: {result[name]} and {rid}')
        result[name] = rid
    return result


def targets():
    """All existing lesson and companion sources can preview independently of publication."""
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
                data=data
            )
    # Registry entries with a standalone pdf.source (e.g. Welcome) render independently,
    # output as <resource-id>.pdf. Their whole source folder (icons, cover) is their input.
    for resource_id, record in registry.items():
        build = record.get('pdf') or {}
        if not build.get('source'):
            continue
        source = Path(build['source'])
        data = read_json(source.as_posix())
        name = f'{resource_id}.pdf'
        if name in result:
            raise ValueError(f'Duplicate output: {name}')
        result[name] = dict(
            source=source.as_posix(), kind=build['renderer'],
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


def input_paths(target):
    """Discover files and directories referenced by any JSON block."""
    source = Path(target['source'])
    files, folders = {source.as_posix()}, set()

    # Companions also read their enclosing quest.json for stage headings.
    for parent in (ROOT / source).parents:
        quest = parent / 'quest.json'
        if quest.is_file():
            files.add(quest.relative_to(ROOT).as_posix())
            break
        if parent == ROOT:
            break

    def scan(value):
        if isinstance(value, dict):
            for item in value.values():
                scan(item)
        elif isinstance(value, list):
            for item in value:
                scan(item)
        elif isinstance(value, str) and 0 < len(value) < 240 and '\n' not in value and '://' not in value:
            # Any block can refer to a local file; no block names or asset keys.
            try:
                path = (ROOT / source.parent / value).resolve()
                if not path.is_relative_to(ROOT.resolve()):
                    return
                if path.is_file():
                    files.add(path.relative_to(ROOT).as_posix())
                elif path.is_dir():
                    folders.add(path.relative_to(ROOT).as_posix().rstrip('/') + '/')
            except (OSError, ValueError):
                pass

    scan(target['data'])
    return files, folders



def renderer_assets(kind):
    """Discover bundled assets from the renderer's own path expressions."""
    source = ROOT / 'scripts/renderers' / f'{kind}.py'
    paths = set()
    for node in ast.walk(ast.parse(source.read_text())):
        parts = []
        while (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
               and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)):
            parts.insert(0, node.right.value)
            node = node.left
        if len(parts) > 1 and parts[0] == 'templates':
            paths.add(Path(*parts))
    # Drop intermediate directories when a renderer names a more specific asset.
    used = {p for p in paths if not any(p != other and p in other.parents for other in paths)}
    files = {p.as_posix() for p in used if (ROOT / p).is_file()}
    folders = {p.as_posix().rstrip('/') + '/' for p in used if (ROOT / p).is_dir()}
    return files, folders

def changed_registry_ids(base_ref, fields=('title', 'holding_url', 'published_url')):
    current = read_json('catalog/resources.json')
    if not base_ref:
        return set(current)
    old = json.loads(previous('catalog/resources.json', base_ref))
    return {key for key in old.keys() | current.keys()
            if any((old.get(key) or {}).get(f) != (current.get(key) or {}).get(f) for f in fields)}



def changed_pdf_config_ids(base_ref):
    """Only generator inputs select new previews; approved checksums are not source edits."""
    current = read_json('catalog/resources.json')
    if not base_ref:
        return set(current)
    old = json.loads(previous('catalog/resources.json', base_ref))
    def config(resource):
        pdf = (resource or {}).get('pdf') or {}
        return {key: pdf.get(key) for key in ('renderer','output','source')}
    return {rid for rid in old.keys() | current.keys()
            if config(old.get(rid)) != config(current.get(rid))}


def select(changed, base_ref=None):
    changed = {p.replace('\\', '/').removeprefix('./') for p in changed}
    # Starter JSON and template documentation are not runtime PDF inputs.
    changed = {p for p in changed if not (p.startswith('templates/') and
               (p.endswith('/TEMPLATE.json') or p.endswith('.md')))}
    registered = targets()
    renderer_files = {f"scripts/renderers/{t['kind']}.py" for t in registered.values()}
    assets_by_kind = {kind: renderer_assets(kind) for kind in {t['kind'] for t in registered.values()}}

    # Shared code may affect any output; assets are scoped by renderer below.
    if any(p in {'requirements.txt', 'catalog/quests.json'}
           or p.startswith('.github/actions/pdf-setup/')
           or (p.startswith('scripts/') and p.endswith('.py') and p not in renderer_files)
           for p in changed):
        return sorted(registered)

    registry_changed = 'catalog/resources.json' in changed
    refs = changed_registry_ids(base_ref) if registry_changed else set()
    builds_changed = changed_pdf_config_ids(base_ref) if registry_changed else set()
    selected, recognized = set(), set()
    for name, target in registered.items():
        files, folders = input_paths(target)
        asset_files, asset_folders = assets_by_kind[target['kind']]
        files.update(asset_files)
        folders.update(asset_folders)
        files.add(f"scripts/renderers/{target['kind']}.py")
        hits = {p for p in changed if p in files or any(p.startswith(folder) for folder in folders)}
        recognized.update(hits)
        if (hits or target['resource_id'] in builds_changed
                or refs & (resource_refs(target['data']) | nav_refs(target['data']))):
            selected.add(name)

    # Shortcut: when a changed potential input cannot be attributed to a PDF,
    # rebuild all rather than risk a stale preview. Upgrade only if overbuilds hurt.
    unknown = changed - recognized - {'catalog/resources.json'}
    if any(p.startswith('content/')
           or (not p.startswith(('apps/', 'tests/', 'system/', 'catalog/', '.github/'))
               and not p.endswith('.md'))
           for p in unknown):
        return sorted(registered)
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
    return {'outputs': names, 'source_paths': [registered[n]['source'] for n in names]}


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
