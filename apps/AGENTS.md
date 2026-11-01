# Editing apps

`apps/` holds standalone teacher-facing web apps. They are separate from the Python Teacher Guide pipeline: they read repository records but never edit lesson sources, change publication status, or publish to Drive.

| App | Purpose | Read first |
| --- | --- | --- |
| `print-pack-builder/` | Teachers pick lesson activities and class numbers and download one combined student-worksheet PDF | [print-pack-builder/README.md](print-pack-builder/README.md) |

- **Print manifests** (`print-pack-builder/config/lessons/*.json`) reference stable IDs in `catalog/resources.json` and must follow the lesson's Teaching Flow. Never put Drive IDs or URLs in them. Card counts per sheet and page counts must be verified from the actual file.
- **Pilot allowlist** (`print-pack-builder/config/pilot-allowlist.json`) is the only list of resources the app may serve. Adding an entry is a human pilot decision; it never changes a resource's `status` ([CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states)). The site currently runs without a login (`REQUIRE_ACCESS: "false"`), which is only acceptable because every allowlisted file is already shared publicly on Drive; require the login before allowlisting any file that is not.
- Do not commit real worksheets, credentials or `.dev.vars`; demo files are synthetic (`npm run fixtures`).
- Use a dedicated non-lesson branch for app work. After editing, run `npm run check` in the app folder; CI runs the same in `.github/workflows/print-pack-builder.yml`.
