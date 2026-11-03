# Editing teaching content

Every source file in this folder opens with a `$instructions` key (stories: an `instructions:` frontmatter line) naming the guides to read before editing it. `scripts/validate.py` requires it, and the templates carry it, so new files get it too.

| Editing | Read first |
| --- | --- |
| `<school>/<quest>/quest.json` | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states). It owns lesson sequence and provenance, not publication status. Derive each lesson's state from its registered Teacher Guide resource. |
| `lessons/<stage>/lesson.json` | [EDITORIAL_GUIDE.md](../system/EDITORIAL_GUIDE.md), then [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) |
| `lessons/<stage>/stage.json` | Provenance only. To convert a lesson, start from [templates/teacher_guide/TEMPLATE.json](../templates/teacher_guide/TEMPLATE.json). |
| `resources/teacher_companion/*.json` | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md) |
| `story/*.md` | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md); approved text only, wording preserved |
| `welcome/` (registry-built documents) | [templates/welcome/README.md](../templates/welcome/README.md) |
| Lesson slides (Drive PDFs, not stored here) | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |
| Covers, icons, artwork | [Asset rules](../system/CONTENT_CONTRACT.md#resources-slides-and-assets): separate image files, covers as cut `cover.pdf` |

Linked resource names, URLs, and publication evidence (including each lesson's Teacher Guide) live in [catalog/resources.json](../catalog/AGENTS.md); all publication states are derived, never stored.

**Student worksheets print from the guide.** The [Print Pack Builder](../apps/AGENTS.md) reads each `lesson.json`: a `student_material` under `GIVE` is printed for everyone, under `MORE` it is an optional checkbox, and inside `step.options` it follows the A/B/C choice. Adding a worksheet to a guide, and publishing it in the catalogue, makes it printable with no other step. Keep each worksheet's description stating its copies (`One per student`, `One per team of 2–3`). An option may set `group_size` (students per group) as the builder's default for its per-group materials; otherwise the builder uses 4.

After editing, run `python scripts/validate.py` and save through a PR per [WORKFLOW.md](../system/WORKFLOW.md).
