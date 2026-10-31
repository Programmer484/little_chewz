# Editing tooling

| File | Purpose | Read first |
| --- | --- | --- |
| `renderers/teacher_guide.py` | Teacher Guide PDF layout | [EDITORIAL_GUIDE.md §7](../system/EDITORIAL_GUIDE.md#7-generator-engineering-boundaries) |
| `renderers/teacher_companion.py` | Companion PDF layout | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md#presentation) |
| `renderers/claude.py` | Welcome/claude page style | [templates/claude/README.md](../templates/claude/README.md) |
| `select_builds.py`, `build_selected.py` | Explicit generated-PDF output mappings and previews | [WORKFLOW.md](../system/WORKFLOW.md#previews-and-cleanup) |
| `validate.py` | Objective source/registry checks and instructions freshness | [AI_RULES.md](../system/AI_RULES.md#maintaining-instructions) |
| `build_agents_md.py` | Regenerate root `AGENTS.md` | Run after any instruction edit |
| `publish_to_drive.py` | Generated-PDF in-place Drive replacement/checksum | [PUBLISH.md](../system/PUBLISH.md) |
| `release_on_merge.py` | Single authorized generated-PDF merge selection and release | [PUBLISH.md](../system/PUBLISH.md) |
| `inspect_publications.py` | Manual read-only publication evidence inspection | [PUBLISH.md](../system/PUBLISH.md#on-demand-inspection) |
| `pdf_to_linked_slides.py` | Human-reviewed slide PDF to linked PPTX | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |

PDF previews use `renderers/resource_links.py` to select holding URLs; generated-PDF release builds use published URLs and `publication_checks.py` to reject unpublished dependencies. Only Python-generated PDFs enter the build-and-publish pipeline. External resources have no automatic GitHub merge publisher or source-generation engine; agents handle Drive holding and official publication directly.

When changing renderer inputs or build selection, update `select_builds.py` and relevant tests. Run `python scripts/validate.py` and `python -m unittest discover -s tests` after edits.
