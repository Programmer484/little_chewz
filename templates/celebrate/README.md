# `celebrate` template: end-of-quest Celebrate guide

A Teacher Guide for the optional celebration after a quest. It keeps the Teacher Guide design system (Lato, cream page, coral accent, the 44 / 82 / 129 / 551 pt Teaching Flow grid, action labels, linked resource lines) and adds four Celebrate elements:

- **Confetti band**: the six stage colours across the top of every page.
- **Invitation**: At a Glance opens with a Lobster headline and a dashed "ticket" card (When / How long / Must-do) beside the Celebrate stamp.
- **Party sizes**: a *Choose your size* page (S / M / L menu, then Preparation). Each Teaching Flow step shows coral chips for the sizes that include it.
- **Finale**: a *Mission complete* page with the quest badge, one closing line, and the last steps.

Page order: cover, At a Glance, Choose your size, Teaching Flow (as many pages as needed; steps are never split), finale.

Renderer: [`scripts/renderers/celebrate.py`](../../scripts/renderers/celebrate.py), with ReportLab and pypdf. Writing rules are the Teacher Guide's ([EDITORIAL_GUIDE.md](../../system/EDITORIAL_GUIDE.md)): no Assessment section, one ASK per step, allowed action labels only.

## Using it

Copy `TEMPLATE.json` into the quest's `lessons/06-celebrate/` folder as `lesson.json` and fill it in. In `catalog/resources.json`, the guide resource uses `"pdf": {"renderer": "celebrate", "output": "06-celebrate-teacher-guide.pdf"}`. The build selector then renders it with this renderer instead of `teacher_guide`.

Direct render from the repository root:

```bash
python scripts/renderers/celebrate.py <lesson.json> --output <review.pdf>
```

## Fields

Shared with the Teacher Guide: `key`, `title` (its first `/` part is the page-header stage name), `grade`, `duration`, `print_note`, `goal`, `outcomes`, `focus`, `curriculum`, `core`, `optional_prep`, `prep_heading`, `cover`, and `steps` (`id`, `title`, `mins`, `rows`).

Celebrate additions:

| Field | Purpose |
| --- | --- |
| `invitation.headline` | Lobster headline on At a Glance. |
| `invitation.rows` | `[label, text]` pairs inside the ticket card. |
| `invitation.stamp` | Optional image path; defaults to `assets/celebrate-stamp.png`. |
| `size_intro`, `size_tip` | Optional sentence above the menu; optional tinted tip below it. |
| `sizes[]` | `label` (one letter), `title`, `time`, `text`, `steps` (for example `"Steps 1, 4"`). |
| `steps[].sizes` | Labels of the sizes that include the step; drawn as chips. |
| `spot_art` | `images` (paths) and an optional `caption`, shown under Preparation. Optional `height` (pt). |
| `finale` | `headline`, `kicker`, `badge` (image path), `line`, and `step_count`: how many of the **last** steps move to the finale page. Omit `finale` for no finale page. |

All steps stay in `steps`, so the Print Pack Builder and validation read them as usual. Resources use catalogue `ref` IDs, never URLs.

## Artwork

The template's own asset is the Celebrate stamp in `assets/`. Quest artwork (the quest badge, photo-booth props) lives in that quest's lesson folder as separate image files referenced from `lesson.json`, never as a pre-rendered page ([asset rule](../../system/CONTENT_CONTRACT.md#resources-slides-and-assets)). Prepare props with transparent backgrounds. Fonts come from `templates/fonts/` (Lato) and `templates/welcome/assets/fonts/` (Lobster); the logo from `templates/welcome/assets/`.

## Checks

`python scripts/validate.py` checks party sizes, step size labels and `finale.step_count` alongside the normal lesson checks. The renderer fails loudly on undefined sizes, unknown resources, unsupported action labels, and pages that overflow. Tests: `python -m unittest tests.test_celebrate`.
