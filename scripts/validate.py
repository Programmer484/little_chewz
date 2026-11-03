#!/usr/bin/env python3
"""Local, dependency-free source checks. Validation is not editorial signoff."""
from pathlib import Path
import json,sys,re
from select_builds import targets, resource_refs, read_json, generated_outputs
from publication_state import has_official_version
R=Path(__file__).resolve().parents[1]
def read_registry():
    duplicates = []
    def unique_pairs(pairs):
        seen = set()
        for key, _ in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        return dict(pairs)
    records = json.loads((R/'catalog/resources.json').read_text(),
                         object_pairs_hook=unique_pairs)
    if duplicates:
        raise SystemExit(f"ERROR: duplicate resource JSON keys: {sorted(set(duplicates))}")
    return records

registry=read_registry()
actions=json.loads((R/'system/action_labels.json').read_text())
allowed=set(actions['teacher_guide_actions']+actions['internal_row_types'])
# Every editable source names the instructions an editor must read; agents meet
# this pointer as soon as they open the file. Templates carry it so new files do too.
INSTRUCTIONS={
    'lesson':'Before editing, read system/EDITORIAL_GUIDE.md (writing) and system/CONTENT_CONTRACT.md (ownership, assets). Publication state derives from the registered Teacher Guide, not lesson.json. Save and preview per system/WORKFLOW.md.',
    'stage':'Provenance only; never add status or teaching content here. To convert this lesson, create lesson.json from templates/teacher_guide/TEMPLATE.json and follow system/EDITORIAL_GUIDE.md.',
    'companion':'Before editing, read system/RESOURCE_GUIDELINES.md (writing) and system/CONTENT_CONTRACT.md (ownership, assets). Status lives in catalog/resources.json, not here. Save and preview per system/WORKFLOW.md.',
    'quest':'Owns quest metadata and lesson order only; lesson publication state derives from each Teacher Guide resource in catalog/resources.json. Rules: system/CONTENT_CONTRACT.md; workflow: system/WORKFLOW.md.',
    'quest_catalog':'Navigation index only. Start at the root AGENTS.md. Each quest.json owns lesson sequence; catalog/resources.json owns resource links and publication evidence (system/CONTENT_CONTRACT.md).',
    'welcome':'Before editing, read templates/welcome/README.md (blocks, navigation) and system/CONTENT_CONTRACT.md (artwork as separate asset files, never a pre-rendered page). Status lives in catalog/resources.json. Save and preview per system/WORKFLOW.md.',
}
STORY_INSTRUCTIONS='instructions: Approved raw story text only; preserve wording, names, and dialogue. Rules in system/CONTENT_CONTRACT.md.'
def check_instructions(path,data,kind):
    expected=INSTRUCTIONS[kind]
    if not isinstance(data,dict) or data.get('$instructions')!=expected:
        errors.append(f'{path}: first key must be "$instructions": {json.dumps(expected)}')
errors=[]; warnings=[]
def check_ref(ref,source):
    if ref not in registry: errors.append(f'{source}: missing catalog resource ref {ref}')
FOLDERS={'welcome', 'teacher_guide', 'classroom_slides', 'student_material', 'teacher_resource'}
PDF_TEMPLATES={'teacher_guide': 'teacher_guide', 'teacher_companion': 'teacher_resource',
               'welcome': 'welcome'}
FIELDS={'title', 'type', 'published_url', 'holding_url', 'pdf',
        'pdf_url', 'human_reviewed_url', 'print'}
for ref,item in registry.items():
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ref):
        errors.append(f'{ref}: resource ID must be stable lowercase kebab-case')
    if not isinstance(item,dict):
        errors.append(f'{ref}: resource entry must be an object')
        continue
    unknown = set(item) - FIELDS
    if unknown:
        errors.append(f'{ref}: obsolete or unknown metadata fields {sorted(unknown)}')
    if not isinstance(item.get('title'),str) or not item['title']:
        errors.append(f'{ref}: title required')
    category = item.get('type')
    if category not in FOLDERS:
        errors.append(f'{ref}: type must match a published Drive category')
    for role in ('published_url','holding_url'):
        url = item.get(role)
        if role not in item:
            errors.append(f'{ref}: explicit {role} required (null if absent)')
        elif url is not None and (not isinstance(url,str) or not url.startswith('https://')):
            errors.append(f'{ref}: {role} must be HTTPS or null')
    pdf = item.get('pdf')
    if pdf is not None:
        if not isinstance(pdf,dict):
            errors.append(f'{ref}: pdf must be an object')
            continue
        template = pdf.get('template')
        if template not in PDF_TEMPLATES:
            errors.append(f'{ref}: unsupported generated PDF template')
        elif PDF_TEMPLATES[template] != category:
            errors.append(f'{ref}: PDF template does not match delivery folder type')
        extra = set(pdf)-{'template','output','source','approved_md5','revision'}
        if extra:
            errors.append(f'{ref}: unknown pdf metadata {sorted(extra)}')
        output, source = pdf.get('output'), pdf.get('source')
        if bool(output)==bool(source):
            errors.append(f'{ref}: PDF needs exactly one output or source')
        if output is not None and (not isinstance(output,str) or not output.endswith('.pdf') or '/' in output):
            errors.append(f'{ref}: PDF output must be a filename ending in .pdf')
        if source is not None:
            candidate=Path(source) if isinstance(source,str) else Path('/')
            if (not isinstance(source,str) or candidate.is_absolute() or '..' in candidate.parts
                    or not (R/candidate).is_file()):
                errors.append(f'{ref}: PDF source must be a valid repository file')
        if template == 'welcome' and not source:
            errors.append(f'{ref}: Welcome renderer needs a source')
        if template in {'teacher_guide','teacher_companion'} and not output:
            errors.append(f'{ref}: guide/companion needs an output mapping')
        approved=pdf.get('approved_md5')
        revision=pdf.get('revision')
        if approved is not None and not re.fullmatch(r'[0-9a-f]{32}',str(approved)):
            errors.append(f'{ref}: approved_md5 must be an exact verified MD5')
        if revision is not None and not re.fullmatch(r'[0-9a-f]{40}',str(revision)):
            errors.append(f'{ref}: revision must be an accepted Git SHA')
        if bool(approved)!=bool(revision):
            errors.append(f'{ref}: approved PDF checksum and accepted revision must be recorded together')
        if approved and not item.get('published_url'):
            errors.append(f'{ref}: cannot approve unpublished PDF bytes')
    elif 'pdf' in item:
        errors.append(f'{ref}: omit pdf unless generated')
    reviewed=item.get('human_reviewed_url')
    if reviewed is not None:
        if not isinstance(reviewed,str) or reviewed!=item.get('published_url'):
            errors.append(f'{ref}: human approval must match current published URL exactly')
        elif re.match(r'https://(?:drive|docs)\\.google\\.com/',reviewed):
            errors.append(f'{ref}: Drive files always use automatic API inspection')
    if 'pdf_url' in item:
        if category!='classroom_slides' or not isinstance(item['pdf_url'],str) or not item['pdf_url'].startswith('https://'):
            errors.append(f'{ref}: pdf_url is only for classroom-slide source PDFs')
    if 'print' in item:
        printing = item['print'] if isinstance(item['print'],dict) else {}
        cards = printing.get('cards_per_sheet')
        if (category!='student_material' or set(printing)!={'cards_per_sheet'}
                or type(cards) is not int or cards < 2):
            errors.append(f'{ref}: print requires student_material with cards_per_sheet >= 2')
folders_path=R/'catalog/drive_folders.json'
if not folders_path.is_file():
    errors.append('Missing distinct Drive staging/final-folder registry')
else:
    folders=json.loads(folders_path.read_text())
    staging=folders.get('staging') or {}
    for purpose in ('root','generated_pdf','worksheets','visuals','other','slide_pdfs'):
        if not (staging.get(purpose) or {}).get('folder_id'):
            errors.append(f'Unconfigured holding folder: {purpose}')
    for category in ('01_TEACHER_GUIDES','02_CLASSROOM_SLIDES','03_STUDENT_MATERIALS','04_TEACHER_RESOURCES'):
        if not (staging.get('categories') or {}).get(category,{}).get('folder_id'):
            errors.append(f'Unconfigured holding category: {category}')
    for section in [*(value for value in staging.values() if isinstance(value,dict)),
                    *(value for value in (staging.get('categories') or {}).values() if isinstance(value,dict)),
                    (folders.get('published') or {})]:
        for key in ('folder_id','default_folder_id'):
            value=section.get(key)
            if value is not None and not re.fullmatch(r'[A-Za-z0-9_-]{15,}',str(value)):
                errors.append(f'catalog/drive_folders.json: invalid {key} {value!r}')
    for resource_id,folder in ((folders.get('published') or {}).get('by_resource_id') or {}).items():
        if resource_id not in registry:
            errors.append(f'Unknown published folder resource ID: {resource_id}')
        if isinstance(folder, dict):
            if not folder or set(folder) - {'main', 'pdf'} or 'main' not in folder:
                errors.append(f'Invalid paired published folder mapping for {resource_id}')
            folder_ids = folder.values()
        else:
            folder_ids = (folder,)
        for folder_id in folder_ids:
            if not isinstance(folder_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{15,}', folder_id):
                errors.append(f'Invalid published destination folder ID for {resource_id}')

for path in R.glob('content/**/lessons/**/lesson.draft.json'):
    errors.append(f'{path}: use lesson.json; separate draft filenames are obsolete')
for path in R.glob('content/**/lessons/**/stage.json'):
    stage=json.loads(path.read_text())
    check_instructions(path,stage,'stage')
    duplicate=set(stage) & {'id','title','status','preview_enabled','lesson_source','required_fields','guide_metadata','slide_sequence','activity_decision'}
    if duplicate: errors.append(f'{path}: duplicated stage fields {sorted(duplicate)}')
check_instructions(R/'catalog/quests.json',read_json('catalog/quests.json'),'quest_catalog')
guide_outputs = generated_outputs(registry)
for school in read_json('catalog/quests.json')['school_index']:
    quest_path=R / school['quest_manifest']
    quest=json.loads(quest_path.read_text())
    check_instructions(quest_path,quest,'quest')
    for lesson in quest['learning_sequence']:
        redundant = set(lesson) & {'status','published_url','holding_url','publication'}
        if redundant:
            errors.append(f'{quest_path}: lesson {lesson["folder"]} has redundant publication fields {sorted(redundant)}')
        folder=quest_path.parent/'lessons'/lesson['folder']
        guide_id=guide_outputs.get(f"{lesson['folder']}-teacher-guide.pdf")
        if guide_id and registry[guide_id].get('published_url') and not (folder/'lesson.json').is_file():
            errors.append(f'{folder}: published Teacher Guide has no lesson.json')
lesson_paths = sorted(R.glob('content/**/lessons/**/lesson.json'))
for path in lesson_paths:
    d=json.loads(path.read_text())
    check_instructions(path,d,'lesson')
    if set(d) & {'review_status','preview_enabled','status','holding_url','published_url'}:
        errors.append(f'{path}: obsolete lesson publication/preview fields')
    for field in ['key','goal','steps','outcomes','cover','output']:
        if field not in d: errors.append(f'{path}: missing {field}')
    def check_quantity(link):
        ref = link.get('ref') if isinstance(link, dict) else None
        if not ref:
            return
        quantity = link.get('quantity')
        if registry.get(ref, {}).get('type') == 'student_material':
            if quantity not in ('per_student', 'per_group'):
                errors.append(f'{path}: worksheet {ref} must set quantity to per_student or per_group')
        elif quantity is not None:
            errors.append(f'{path}: non-worksheet {ref} must not set quantity')
    for ref in resource_refs(d): check_ref(ref,path)
    cover=path.parent/d.get('cover','')
    if not cover.is_file(): errors.append(f'{path}: missing visual cover {cover.name}')
    ids=[]
    for section in ['core','optional_prep','bonuses']:
        for item in d.get(section,[]):
            check_ref(item['ref'],path)
            check_quantity(item)
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
            check_quantity(row)
            for link in row.get('links',[]): check_quantity(link)
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
        errors.append(f'{path}: resource status is derived from publication evidence')
    if not has_official_version(registry.get(d.get('resource_id'), {})):
        warnings.append(f'{path.name}: unpublished companion; preview only')
for path in R.glob('content/**/story/*.md'):
    if STORY_INSTRUCTIONS not in path.read_text().split('---')[1]:
        errors.append(f'{path}: frontmatter must include the line "{STORY_INSTRUCTIONS}"')
for ref,item in registry.items():
    build=item.get('pdf') or {}
    if build.get('source'):
        if build['template'] not in INSTRUCTIONS or not (R/f"scripts/renderers/{build['template']}.py").is_file():
            errors.append(f'{ref}: unknown PDF template {build["template"]}')
            continue
        source=R/build.get('source','')
        if not source.is_file():
            errors.append(f'{ref}: build source {source} is missing'); continue
        doc=json.loads(source.read_text())
        check_instructions(source.relative_to(R),doc,build['template'])
        from select_builds import nav_refs
        for nav in nav_refs(doc):
            if nav not in registry: errors.append(f'{source}: navigation names unknown resource {nav}')
for path,kind in [('templates/teacher_guide/TEMPLATE.json','lesson'),
                  ('templates/teacher_companion/TEMPLATE.json','companion'),
                  ('templates/welcome/TEMPLATE.json','welcome')]:
    if (R/path).is_file(): check_instructions(path,json.loads((R/path).read_text()),kind)
try:
    registered = targets()
    for name, target in registered.items():
        for ref in resource_refs(target['data']):
            record = registry.get(ref, {})
            if not str(record.get('published_url') or record.get('holding_url') or '').startswith('https://'):
                errors.append(f'{name}: unresolved HTTPS destination for {ref}')
            elif not has_official_version(record):
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
