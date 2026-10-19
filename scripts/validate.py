#!/usr/bin/env python3
"""Local, dependency-free source checks. Validation is not editorial signoff."""
from pathlib import Path
import json,sys,re
from select_builds import targets, resource_refs
R=Path(__file__).resolve().parents[1]
registry=json.loads((R/'catalog/resources.json').read_text())
actions=json.loads((R/'system/action_labels.json').read_text())
allowed=set(actions['teacher_guide_actions']+actions['internal_row_types'])
errors=[]; warnings=[];seen=set()
def check_ref(ref,source):
    if ref not in registry: errors.append(f'{source}: missing catalog resource ref {ref}')
for ref,item in registry.items():
    rid=item.get('resource_id')
    if not rid or rid in seen: errors.append(f'duplicate/missing resource_id: {ref} -> {rid}')
    seen.add(rid)
    if item.get('approved_link') and not str(item.get('url','')).startswith('https://'):
        errors.append(f'{ref}: approved resource has no HTTPS URL')
    if item.get('link_note'): warnings.append(f'{ref}: {item["link_note"]}')
lesson_paths = sorted(set(R.glob('content/**/lessons/**/lesson.json')) | set(R.glob('content/**/lessons/**/lesson.draft.json')))
for path in lesson_paths:
    d=json.loads(path.read_text())
    for field in ['key','goal','steps','outcomes','cover','output']:
        if field not in d: errors.append(f'{path}: missing {field}')
    for ref in resource_refs(d): check_ref(ref,path)
    cover=path.parent/d.get('cover','')
    if not cover.is_file(): errors.append(f'{path}: missing visual cover {cover.name}')
    ids=[]
    for section in ['core','optional_prep','bonuses']:
        for item in d.get(section,[]): check_ref(item['ref'],path)
    for st in d.get('steps',[]):
        ids.append(st.get('id'))
        options=st.get('options',[])
        labels=[option.get('label') for option in options]
        if len(labels)!=len(set(labels)) or any(k not in ('A','B','C','D') for k in labels):
            errors.append(f'{path}: option labels must be unique A/B/C/D')
        for option in options:
            if not option.get('title') or not option.get('rows'):
                errors.append(f'{path}: option must have a title and rows')
        rows=st.get('rows',[])+[row for option in options for row in option.get('rows',[])]
        for row in rows:
            k=row.get('kind','').upper()
            if k not in allowed: errors.append(f'{path}: unsupported action label {k}')
            if row.get('ref'):check_ref(row['ref'],path)
            for link in row.get('links',[]):check_ref(link['ref'],path)
    if ids!=list(range(1,len(ids)+1)): errors.append(f'{path}: step IDs not consecutive')
    if len(d.get('outcomes',[]))!=3: warnings.append(f'{path}: guide convention normally uses three outcomes')
for path in R.glob('content/**/resources/**/*.json'):
    d=json.loads(path.read_text())
    if not d.get('resource_id') or not d.get('review_status'):
        errors.append(f'{path}: companion missing stable ID/status')
    if d.get('review_status')=='draft_unpublished':warnings.append(f'{path.name}: not approved for publishing')
try:
    registered = targets()
    for name, target in registered.items():
        for ref in resource_refs(target['data']):
            record = registry.get(ref, {})
            if not str(record.get('url', '')).startswith('https://'):
                errors.append(f'{name}: unresolved HTTPS destination for {ref}')
            elif not record.get('approved_link'):
                warnings.append(f'{name}: {ref} is unapproved; preview only')
except (ValueError, KeyError, OSError) as exc:
    errors.append(f'PDF registration/eligibility: {exc}')
print(f'Validated {len(registry)} registry links; {len(lesson_paths)} editable lesson; {len(list(R.glob("content/**/resources/**/*.json")))} companion sources')
for m in warnings:print('WARN:',m)
for m in errors:print('ERROR:',m)
print('PASS' if not errors else 'FAILED')
sys.exit(bool(errors))
