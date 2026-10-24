# Editing templates

Templates are starting structures for supported source types: `teacher_guide/` (lesson.json), `teacher_companion/`, `story/`, and the `claude/` page style with its assets. `fonts/` holds the bundled Lato (OFL) used by the Teacher Guide and companion renderers; it is the same Lato 2.015 CI used before it was bundled. Add a template only for a source type with a working authoring workflow.

- **Build templates from individual assets.** Logos, crests, icons, and illustrations go in the template's `assets/` folder as separate image files that the renderer places around live text. Never generate or rasterize a whole page as one image. Full rule: [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#resources-slides-and-assets).
- Each `TEMPLATE.json` opens with the same `$instructions` pointer its sources need (the story template has an `instructions:` line), so copies inherit it. `scripts/validate.py` checks this.
- Renderers live in `scripts/renderers/`, not here ([scripts/AGENTS.md](../scripts/AGENTS.md)).
