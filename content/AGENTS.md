# Editing teaching content

Every source file in this folder opens with a `$instructions` key (stories: an `instructions:` frontmatter line) naming the guides to read before editing it. `scripts/validate.py` requires it, and the templates carry it, so new files get it too.

| Editing | Read first |
| --- | --- |
| `<school>/<quest>/quest.json` | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states). It owns lesson delivery status; branch-only edits do not change it. |
| `lessons/<stage>/lesson.json` | [EDITORIAL_GUIDE.md](../system/EDITORIAL_GUIDE.md), then [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) |
| `lessons/<stage>/stage.json` | Provenance only. To convert a lesson, start from [templates/teacher_guide/TEMPLATE.json](../templates/teacher_guide/TEMPLATE.json). |
| `resources/teacher_companion/*.json` | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md) |
| `story/*.md` | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md); approved text only, wording preserved |
| `welcome/` (registry-built documents) | [templates/claude/README.md](../templates/claude/README.md) |
| Lesson slides (Drive PDFs, not stored here) | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |
| Covers, icons, artwork | [Asset rules](../system/CONTENT_CONTRACT.md#resources-slides-and-assets): separate image files, covers as cut `cover.pdf` |

Linked resource names, URLs, and companion status live in [catalog/resources.json](../catalog/AGENTS.md), never in these files. After editing, run `python scripts/validate.py` and save through a PR per [WORKFLOW.md](../system/WORKFLOW.md).
