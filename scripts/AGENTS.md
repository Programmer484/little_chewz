# Editing tooling

| File | Purpose | Read first |
| --- | --- | --- |
| `renderers/teacher_guide.py` | Teacher Guide PDF layout | [EDITORIAL_GUIDE.md §7](../system/EDITORIAL_GUIDE.md#7-generator-engineering-boundaries) (layout constants, Lato, strict links) |
| `renderers/teacher_companion.py` | Companion PDF layout | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md#presentation) |
| `renderers/claude.py` | `claude` page style (Welcome PDF) | [templates/claude/README.md](../templates/claude/README.md) |
| `select_builds.py`, `build_selected.py` | Which PDFs a change previews, and the batch builder | [WORKFLOW.md: PDF build selection](../system/WORKFLOW.md#pdf-build-selection) |
| `validate.py` | Objective source checks, including `$instructions` pointers and `AGENTS.md` freshness | [AI_RULES.md: maintaining instructions](../system/AI_RULES.md#maintaining-instructions) |
| `build_agents_md.py` | Regenerates the root `AGENTS.md` from all instruction files | Run after editing any instruction file |
| `publish_to_drive.py` | In-place Drive replacement | [DRIVE_PUBLISHING.md](../system/DRIVE_PUBLISHING.md) |
| `pdf_to_linked_slides.py` | Approved slide PDF to linked PPTX | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |

A renderer for a registry-built document is `renderers/<name>.py`, matching `build.renderer` in `catalog/resources.json`. When adding a renderer input or changing how builds are invoked, update `select_builds.py` and `tests/` in the same PR. Run `python scripts/validate.py` and `python -m unittest discover -s tests`.
