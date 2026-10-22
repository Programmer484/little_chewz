#!/usr/bin/env python3
"""Local, dependency-free source checks. Validation is not editorial signoff."""
from pathlib import Path
import json,sys,re
from select_builds import targets, resource_refs, read_json
R=Path(__file__).resolve().parents[1]
registry=json.loads((R/'catalog/resources.json').read_text())
actions=json.loads((R/'system/action_labels.json').read_text())
allowed=set(actions['teacher_guide_actions']+actions['internal_row_types'])
STATUSES={'unapproved','approved','published'}
errors=[]; warnings=[];seen=set()
def check_ref(ref,source):
    if ref not in registry: errors.append(f'{source}: missing catalog resource ref {ref}')
for ref,item in registry.items():
    rid=item.get('resource_id')
    if not rid or rid in seen: errors.append(f'duplicate/missing resource_id: {ref} -> {rid}')
    seen.add(rid)
    if item.get('status', 'unapproved') not in STATUSES:
        errors.append(f'{ref}: invalid status {item.get("status")}')
    if 'approved_link' in item:
        errors.append(f'{ref}: obsolete approved_link field; use status')
    if item.get('status')=='published' and not str(item.get('url','')).startswith('https://'):
        errors.append(f'{ref}: published resource has no HTTPS URL')
    if item.get('link_note'): warnings.append(f'{ref}: {item["link_note"]}')
for path in R.glob('content/**/lessons/**/lesson.draft.json'):
    errors.append(f'{path}: use lesson.json; separate draft filenames are obsolete')
for path in R.glob('content/**/lessons/**/stage.json'):
    stage=json.loads(path.read_text())
    duplicate=set(stage) & {'id','title','status','preview_enabled','lesson_source','required_fields','guide_metadata','slide_sequence','activity_decision'}
    if duplicate: errors.append(f'{path}: duplicated stage fields {sorted(duplicate)}')
for school in read_json('catalog/quests.json')['school_index']:
    quest_path=R / school['quest_manifest']
    quest=json.loads(quest_path.read_text())
    for lesson in quest['learning_sequence']:
        status=lesson.get('status','unapproved')
        if status not in STATUSES:
            errors.append(f'{quest_path}: invalid lesson status {status}')
        folder=quest_path.parent/'lessons'/lesson['folder']
        if status in ('approved','published') and not (folder/'lesson.json').is_file():
            errors.append(f'{folder}: approved/published lesson has no lesson.json')
lesson_paths = sorted(R.glob('content/**/lessons/**/lesson.json'))
for path in lesson_paths:
    d=json.loads(path.read_text())
    if 'review_status' in d or 'preview_enabled' in d:
        errors.append(f'{path}: obsolete lesson status/preview field')
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
        if options and d.get('flow_style')!='compact':
            errors.append(f'{path}: structured options require flow_style: compact')
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
    if not d.get('resource_id') or d.get('resource_id') not in registry:
        errors.append(f'{path}: companion missing registered resource ID')
    if 'review_status' in d or 'preview_enabled' in d:
        errors.append(f'{path}: status belongs in catalog/resources.json')
    if registry.get(d.get('resource_id'),{}).get('status','unapproved')=='unapproved':
        warnings.append(f'{path.name}: unapproved companion; preview only')
try:
    registered = targets()
    for name, target in registered.items():
        for ref in resource_refs(target['data']):
            record = registry.get(ref, {})
            if not str(record.get('url', '')).startswith('https://'):
                errors.append(f'{name}: unresolved HTTPS destination for {ref}')
            elif record.get('status','unapproved')!='published':
                warnings.append(f'{name}: {ref} is not published; preview only')
except (ValueError, KeyError, OSError) as exc:
    errors.append(f'PDF registration/eligibility: {exc}')
print(f'Validated {len(registry)} registry links; {len(lesson_paths)} editable lesson; {len(list(R.glob("content/**/resources/**/*.json")))} companion sources')
for m in warnings:print('WARN:',m)
for m in errors:print('ERROR:',m)
print('PASS' if not errors else 'FAILED')
sys.exit(bool(errors))
