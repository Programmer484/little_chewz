# Editing apps

`apps/` holds standalone teacher-facing web apps. They are separate from the Python Teacher Guide pipeline: they read repository records but never edit lesson sources, set publication status, or publish to Drive.

| App | Purpose | Read first |
| --- | --- | --- |
| `print-pack-builder/` | Teachers pick lesson activities and class numbers and download one combined student-worksheet PDF | [print-pack-builder/README.md](print-pack-builder/README.md) |

- **No separate print configuration.** The Print Pack Builder reads every `lesson.json` and `catalog/resources.json` at build time ([how guides map to the builder](print-pack-builder/README.md#where-lessons-come-from)): `GIVE` worksheets are included, `MORE` worksheets are checkboxes, `step.options` are pick-one choices, and only `type: student_material` links count. A worksheet becomes downloadable when its catalogue entry has a valid official `published_url`. Never add per-lesson lists, allowlists or Drive IDs to the app.
- **Editing a guide edits the builder.** When you add, move or remove a student worksheet in a `lesson.json`, the builder changes with it; describe its copies in the guide ("One per student", "One per group of 3–4"). For cards printed several to a page, add `"print": {"cards_per_sheet": N}` to the catalogue entry, counted from the actual PDF. An option in `step.options` may set `"group_size": N`, the default students per group for that option; teachers can still change it.
- The site runs without a login (`REQUIRE_ACCESS: "false"`), which is only acceptable because published student worksheets are shared publicly on Drive. Require the login before publishing a worksheet that must stay private.
- Do not commit real worksheets, credentials or `.dev.vars`; demo files are synthetic (`npm run fixtures`).
- Use a dedicated non-lesson branch for app work. After editing, run `npm run check` in the app folder; CI runs the same in `.github/workflows/print-pack-builder.yml`.
