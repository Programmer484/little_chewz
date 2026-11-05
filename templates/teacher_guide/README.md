# Teacher Guide source template

Copy `TEMPLATE.json` to a quest lesson folder as `lesson.json` and fill in its metadata, resources and Teaching Flow. The PDF renderer is `scripts/renderers/teacher_guide.py`.

**Do not put `output` in `lesson.json`.** The official filename belongs only in `catalog/resources.json` under the guide resource's `pdf.output` (normally `<lesson-folder>-teacher-guide.pdf`). The normal build passes that filename to the renderer; direct rendering without `--output` uses the registered filename in the lesson folder. An explicit `--output` overrides the destination.

The starter includes all supported optional top-level presentation fields with inert defaults:

- `assessment`: optional string or list of bullets; empty hides the section.
- `prep_heading`: heading for `optional_prep`; `prep_note`: optional italic preparation text.
- `flow_style`: `compact` supports structured A/B/C/D `steps[].options`.
- `bonuses`: up to two linked extension resources at the end of Teaching Flow.
- `bonus_rows`: alternative extension action rows. **Populate either `bonuses` or `bonus_rows`, not both.**
- `bonus_heading`: heading for whichever bonus section is populated.
- `colored_section_titles`: set true to use the stage accent for overview section headings.

Each Teaching Flow step has an incrementing `id`, a `title`, `mins` (for example `"5"` or `"OPTIONAL"`), and `rows` with `kind` plus `text`, `ref`, or `links`. Optional `options` have an A/B/C/D `label`, `title`, and `rows`; `group_size` may be set for group printing. The renderer supports `SHOW`, `KEEP`, `READ`, `LISTEN`, `ASK`, `DO`, `GIVE`, `MORE`, and internal `QUOTE` rows.

Resources use registered `ref` identifiers, not direct URLs. The Print Pack Builder derives included worksheets from `GIVE` rows, optional worksheets from `MORE` rows and printable extras from `optional_prep`/`bonuses`; preparation `core` alone does not create print entries. Printable worksheet links require `quantity: "per_student"` or `"per_group"`.

Validation: `python scripts/validate.py`. Managed preview: `python scripts/select_builds.py --all --output /tmp/selection.json` then `python scripts/build_selected.py --manifest /tmp/selection.json`.
