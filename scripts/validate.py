#!/usr/bin/env python3
"""Local, dependency-free source checks. Validation is not editorial signoff."""
from pathlib import Path
import json,sys,re
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
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ref):
        errors.append(f'{ref}: resource ID must be stable lowercase kebab-case')
    if not isinstance(item.get('type'),str) or not item['type']:
        errors.append(f'{ref}: missing established resource type')
    production = item.get('production_type')
    if production not in {'generated_pdf','external'}:
        errors.append(f'{ref}: explicit production_type must be generated_pdf or external')
    source = item.get('source')
    if not isinstance(source,dict) or source.get('kind') not in {'github','external_original','unknown'}:
        errors.append(f'{ref}: missing or invalid source provenance')
    elif source['kind']=='github':
        source_path=source.get('path','')
        candidate=Path(source_path)
        if (not source_path or candidate.is_absolute() or '..' in candidate.parts
                or candidate.parts[0] not in ('content','templates')
                or not (R/candidate).is_file()):
            errors.append(f'{ref}: GitHub source mapping invalid: {source_path}')
    elif source['kind']=='external_original' and source.get('url') and not source['url'].startswith('https://'):
        errors.append(f'{ref}: external original URL must use HTTPS')
    build = item.get('build')
    if production=='generated_pdf':
        if not isinstance(source,dict) or source.get('kind')!='github':
            errors.append(f'{ref}: generated PDFs must have GitHub editable source')
        if not isinstance(build,dict) or bool(build.get('renderer'))==bool(build.get('output')):
            errors.append(f'{ref}: generated PDF needs exactly one explicit build renderer or output')
        elif build.get('renderer'):
            if build.get('source') != (source if isinstance(source,dict) else {}).get('path'):
                errors.append(f'{ref}: renderer source disagrees with authoritative GitHub source')
        elif not isinstance(build.get('output'),str) or not build['output'].endswith('.pdf'):
            errors.append(f'{ref}: build output must be a PDF filename')
    elif production=='external' and build:
        errors.append(f'{ref}: external materials cannot enter the generated PDF renderer')
    for role in ('holding_url','published_url'):
        if role not in item:
            errors.append(f'{ref}: missing explicit {role} (use null if unknown)')
        elif item[role] is not None and (not isinstance(item[role],str) or not item[role].startswith('https://')):
            errors.append(f'{ref}: {role} must be HTTPS or null')
    if item.get('status') in {'pending_publish','published'} and not item.get('published_url'):
        errors.append(f'{ref}: live or pending resource needs an established published_url')
    publication=item.get('publication')
    if not isinstance(publication,dict) or publication.get('verification') not in {'unknown','unverified','verified'}:
        errors.append(f'{ref}: publication verification must be explicitly unknown, unverified or verified')
    else:
        if production=='external' and 'artifact_md5' in publication:
            errors.append(f'{ref}: external resources must not claim generated-PDF checksums')
        if publication.get('drive_file_id'):
            source_url=item.get('published_url') or item.get('url','')
            m=re.search(r'/d/([A-Za-z0-9_-]{20,})',source_url)
            if not m or m.group(1)!=publication['drive_file_id']:
                errors.append(f'{ref}: recorded Drive ID conflicts with live URL')
        if publication.get('verification')=='verified':
            if not re.fullmatch(r'[0-9a-f]{40}',publication.get('release_revision','')):
                errors.append(f'{ref}: verified publication needs an accepted Git revision')
            if not publication.get('confirmed_at') or not publication.get('method'):
                errors.append(f'{ref}: verified publication needs timestamp and method')
            if production=='generated_pdf' and publication.get('method')=='external_agent':
                # Live file predates its generated source (converted resource); the next
                # verified generated release replaces it in place and records a digest.
                if publication.get('artifact_md5'):
                    errors.append(f'{ref}: an external release cannot assert a generated-PDF digest')
            elif production=='generated_pdf':
                if publication.get('method')!='generated_pdf' or not re.fullmatch(r'[0-9a-f]{32}',publication.get('artifact_md5','')):
                    errors.append(f'{ref}: generated release needs verified 32-hex PDF digest')
                if not publication.get('drive_file_id'):
                    errors.append(f'{ref}: verified generated release needs exact Drive file ID')
            elif publication.get('method')!='external_agent':
                errors.append(f'{ref}: external release needs agent-confirmed publication method')
        elif publication.get('artifact_md5'):
            errors.append(f'{ref}: unverified publication cannot assert a verified PDF digest')
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
    if 'print' in item:
        printing = item['print'] if isinstance(item['print'], dict) else {}
        cards = printing.get('cards_per_sheet')
        if set(printing) != {'cards_per_sheet'} or not isinstance(cards, int) or cards < 1:
            errors.append(f'{ref}: print must be {{"cards_per_sheet": <whole number of identical cards on each page>}}')
    if item.get('status') in ('pending_publish','published') and not str(item.get('url','')).startswith('https://'):
        errors.append(f'{ref}: live/pending resource has no HTTPS URL')
    if item.get('link_note'): warnings.append(f'{ref}: {item["link_note"]}')
folders_path=R/'catalog/drive_folders.json'
if not folders_path.is_file():
    errors.append('Missing distinct Drive staging/final-folder registry')
else:
    folders=json.loads(folders_path.read_text())
    staging=folders.get('staging') or {}
    for purpose in ('root','generated_pdf','worksheets','visuals','other','slide_pdfs'):
        if not (staging.get(purpose) or {}).get('folder_id'):
            errors.append(f'Unconfigured holding folder: {purpose}')
    for category in ('01_TEACHER_GUIDES','02_CLASSROOM_SLIDES','03_STUDENT_MATERIALS','04_EXTRA_RESOURCES'):
        if not (staging.get('categories') or {}).get(category,{}).get('folder_id'):
            errors.append(f'Unconfigured holding category: {category}')
    for section in [*(value for value in staging.values() if isinstance(value,dict)),
                    *(value for value in (staging.get('categories') or {}).values() if isinstance(value,dict)),
                    (folders.get('published') or {})]:
        for key in ('folder_id','default_folder_id'):
            value=section.get(key)
            if value is not None and not re.fullmatch(r'[A-Za-z0-9_-]{15,}',str(value)):
                errors.append(f'catalog/drive_folders.json: invalid {key} {value!r}')
    for resource_id,folder_id in ((folders.get('published') or {}).get('by_resource_id') or {}).items():
        if resource_id not in registry:
            errors.append(f'Unknown published folder resource ID: {resource_id}')
        if not re.fullmatch(r'[A-Za-z0-9_-]{15,}',str(folder_id)):
            errors.append(f'Invalid published destination folder ID for {resource_id}')

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
