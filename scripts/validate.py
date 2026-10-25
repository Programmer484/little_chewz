#!/usr/bin/env python3
"""Local, dependency-free source checks. Validation is not editorial signoff."""
from pathlib import Path
import json,sys
from select_builds import targets, resource_refs, read_json
R=Path(__file__).resolve().parents[1]
registry=json.loads((R/'catalog/resources.json').read_text())
actions=json.loads((R/'system/action_labels.json').read_text())
allowed=set(actions['teacher_guide_actions']+actions['internal_row_types'])
STATUSES={'unpublished','pending_publish','published'}
# Every editable source names the instructions an editor must read; agents meet
# this pointer as soon as they open the file. Templates carry it so new files do too.
INSTRUCTIONS={
    'lesson':'Before editing, read system/EDITORIAL_GUIDE.md (writing) and system/CONTENT_CONTRACT.md (ownership, assets). Status lives in quest.json, not here. Save and preview per system/WORKFLOW.md.',
    'stage':'Provenance only; never add status or teaching content here. To convert this lesson, create lesson.json from templates/teacher_guide/TEMPLATE.json and follow system/EDITORIAL_GUIDE.md.',
    'companion':'Before editing, read system/RESOURCE_GUIDELINES.md (writing) and system/CONTENT_CONTRACT.md (ownership, assets). Status lives in catalog/resources.json, not here. Save and preview per system/WORKFLOW.md.',
    'quest':'Owns lesson delivery status (unpublished, pending_publish, published); WIP on branches does not alter it. Rules: system/CONTENT_CONTRACT.md; workflow: system/WORKFLOW.md.',
    'quest_catalog':'Navigation index only. Start at the root AGENTS.md. Each quest.json owns lesson status; catalog/resources.json owns resource names, links, and status (system/CONTENT_CONTRACT.md).',
    'claude':'Before editing, read templates/claude/README.md (blocks, navigation) and system/CONTENT_CONTRACT.md (artwork as separate asset files, never a pre-rendered page). Status lives in catalog/resources.json. Save and preview per system/WORKFLOW.md.',
}
STORY_INSTRUCTIONS='instructions: Approved raw story text only; preserve wording, names, and dialogue. Rules in system/CONTENT_CONTRACT.md.'
def check_instructions(path,data,kind):
    expected=INSTRUCTIONS[kind]
    if not isinstance(data,dict) or data.get('$instructions')!=expected:
        errors.append(f'{path}: first key must be "$instructions": {json.dumps(expected)}')
errors=[]; warnings=[]
def check_ref(ref,source):
    if ref not in registry: errors.append(f'{source}: missing catalog resource ref {ref}')
for ref,item in registry.items():
    if not ref:
        errors.append('catalog contains an empty resource ID key')
    if 'resource_id' in item:
        errors.append(f'{ref}: redundant resource_id; the registry key is the stable ID')
    if 'legacy_alias' in item:
        errors.append(f'{ref}: legacy_alias belongs in archive/2026-10/resource-aliases.json')
    if item.get('status', 'unpublished') not in STATUSES:
        errors.append(f'{ref}: invalid status {item.get("status")}')
    if 'approved_link' in item:
        errors.append(f'{ref}: obsolete approved_link field; use status')
    if item.get('status') in ('pending_publish','published') and not str(item.get('url','')).startswith('https://'):
        errors.append(f'{ref}: live/pending resource has no HTTPS URL')
    if item.get('link_note'): warnings.append(f'{ref}: {item["link_note"]}')
for path in R.glob('content/**/lessons/**/lesson.draft.json'):
    errors.append(f'{path}: use lesson.json; separate draft filenames are obsolete')
for path in R.glob('content/**/lessons/**/stage.json'):
    stage=json.loads(path.read_text())
    check_instructions(path,stage,'stage')
    duplicate=set(stage) & {'id','title','status','preview_enabled','lesson_source','required_fields','guide_metadata','slide_sequence','activity_decision'}
    if duplicate: errors.append(f'{path}: duplicated stage fields {sorted(duplicate)}')
check_instructions(R/'catalog/quests.json',read_json('catalog/quests.json'),'quest_catalog')
for school in read_json('catalog/quests.json')['school_index']:
    quest_path=R / school['quest_manifest']
    quest=json.loads(quest_path.read_text())
    check_instructions(quest_path,quest,'quest')
    for lesson in quest['learning_sequence']:
        status=lesson.get('status','unpublished')
        if status not in STATUSES:
            errors.append(f'{quest_path}: invalid lesson status {status}')
        folder=quest_path.parent/'lessons'/lesson['folder']
        if status in ('pending_publish','published') and not (folder/'lesson.json').is_file():
            errors.append(f'{folder}: live/pending lesson has no lesson.json')
lesson_paths = sorted(R.glob('content/**/lessons/**/lesson.json'))
for path in lesson_paths:
    d=json.loads(path.read_text())
    check_instructions(path,d,'lesson')
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
    check_instructions(path,d,'companion')
    if not d.get('resource_id') or d.get('resource_id') not in registry:
        errors.append(f'{path}: companion missing registered resource ID')
    if 'review_status' in d or 'preview_enabled' in d:
        errors.append(f'{path}: status belongs in catalog/resources.json')
    if registry.get(d.get('resource_id'),{}).get('status','unpublished')=='unpublished':
        warnings.append(f'{path.name}: unpublished companion; preview only')
for path in R.glob('content/**/story/*.md'):
    if STORY_INSTRUCTIONS not in path.read_text().split('---')[1]:
        errors.append(f'{path}: frontmatter must include the line "{STORY_INSTRUCTIONS}"')
for ref,item in registry.items():
    build=item.get('build') or {}
    if build.get('renderer'):
        if build['renderer'] not in INSTRUCTIONS or not (R/f"scripts/renderers/{build['renderer']}.py").is_file():
            errors.append(f'{ref}: unknown build renderer {build["renderer"]}')
            continue
        source=R/build.get('source','')
        if not source.is_file():
            errors.append(f'{ref}: build source {source} is missing'); continue
        doc=json.loads(source.read_text())
        check_instructions(source.relative_to(R),doc,build['renderer'])
        from select_builds import nav_refs
        for nav in nav_refs(doc):
            if nav not in registry: errors.append(f'{source}: navigation names unknown resource {nav}')
for path,kind in [('templates/teacher_guide/TEMPLATE.json','lesson'),
                  ('templates/teacher_companion/TEMPLATE.json','companion'),
                  ('templates/claude/TEMPLATE.json','claude')]:
    if (R/path).is_file(): check_instructions(path,json.loads((R/path).read_text()),kind)
try:
    registered = targets()
    for name, target in registered.items():
        for ref in resource_refs(target['data']):
            record = registry.get(ref, {})
            if not str(record.get('url', '')).startswith('https://'):
                errors.append(f'{name}: unresolved HTTPS destination for {ref}')
            elif record.get('status','unpublished')!='published':
                warnings.append(f'{name}: {ref} is not verified current on Drive; preview only')
except (ValueError, KeyError, OSError) as exc:
    errors.append(f'PDF registration/eligibility: {exc}')
try:
    import build_agents_md
    if not build_agents_md.BRIEF.is_file() or build_agents_md.BRIEF.read_text(encoding='utf-8')!=build_agents_md.render():
        errors.append('AGENTS.md is stale; run python scripts/build_agents_md.py')
except OSError as exc:
    errors.append(f'AGENTS.md cannot be built: {exc}')
print(f'Validated {len(registry)} registry links; {len(lesson_paths)} editable lesson; {len(list(R.glob("content/**/resources/**/*.json")))} companion sources')
for m in warnings:print('WARN:',m)
for m in errors:print('ERROR:',m)
print('PASS' if not errors else 'FAILED')
sys.exit(bool(errors))
