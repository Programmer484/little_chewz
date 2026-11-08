# Editing teaching content

Follow the relevant guide below for the file being edited. Source JSON carries content, not embedded agent instructions; `scripts/validate.py` checks its data structure and resource references.

| Editing | Read first |
| --- | --- |
| `<school>/<quest>/quest.json` | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states). It owns the ordered lesson list and quest facts, not publication status. Derive each lesson's state from its registered Teacher Guide resource. |
| `lessons/<stage>/lesson.json` | [EDITORIAL_GUIDE.md](../system/EDITORIAL_GUIDE.md), then [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) |
| `resources/teacher_companion/*.json` | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md) |
| `welcome/` (registry-built documents) | [templates/welcome/README.md](../templates/welcome/README.md) |
| Lesson slides (Drive PDFs, not stored here) | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |
| Covers, icons, artwork | [Asset rules](../system/CONTENT_CONTRACT.md#resources-slides-and-assets): separate image files, covers as cut `cover.pdf` |

Linked resource names, URLs, and publication evidence (including each lesson's Teacher Guide) live in [catalog/resources.json](../catalog/AGENTS.md); all publication states are derived, never stored.

**Student worksheets print from the guide.** The [Print Pack Builder](../apps/AGENTS.md) reads each `lesson.json`: a `student_material` under `GIVE` is printed for everyone, under `MORE` it is an optional checkbox, and inside `step.options` it follows the A/B/C choice. Adding a worksheet to a guide, and publishing it in the catalogue, makes it printable with no other step. Keep each worksheet's description stating its copies (`One per student`, `One per team of 2–3`). An option may set `group_size` (students per group) as the builder's default for its per-group materials; otherwise the builder uses 4.

After editing, run `python scripts/validate.py` and save through a PR per [EDIT.md](../system/EDIT.md).
