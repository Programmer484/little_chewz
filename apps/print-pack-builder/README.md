# Little Chewz Print Pack Builder

A small web app for Grade 4–6 teachers: choose a lesson, pick the activities you will run, check the copies, and download **one combined PDF** of every student worksheet.

**Open → Choose activities → Copies & download**

**There is no separate print configuration.** The builder reads each lesson's Teacher Guide source (`lesson.json`) and `catalog/resources.json` at build time, so a worksheet added to a guide and published in the catalogue becomes printable on the next deploy ([Where lessons come from](#where-lessons-come-from)). It never edits lesson sources and never publishes anything. It is independent of the Python Teacher Guide pipeline.

| Part | Technology | Where |
| --- | --- | --- |
| Teacher app | React + TypeScript + Vite | `src/` |
| Guide reader, copy plan, print order, file checks | TypeScript | `shared/` (`derive.ts` reads the guides) |
| API and secure Drive proxy | Cloudflare Worker (Static Assets + Vite plugin) | `worker/` |
| Demo lesson and its synthetic files | JSON + generated fixtures | `config/demo/`, `worker/demo/` |
| PDF assembly | `pdf-lib`, in the browser | `src/lib/assemble.ts` |
| Tests | Vitest | `tests/` |

## Quick start: local demo (no credentials)

Requires Node 20.19+ (CI uses Node 22).

```bash
cd apps/print-pack-builder
npm ci
cp .dev.vars.example .dev.vars   # sets RESOURCE_MODE=demo
npm run dev                      # http://localhost:5173
```

In demo mode the app shows a **Sample Lesson** built from synthetic PDF, PNG and JPEG files, plus the real lessons. Real published worksheets are replaced by clearly labelled placeholder pages, so the whole flow works end to end without touching Google Drive. The demo uses exactly the same API, planning and PDF-assembly code as production.

## Commands

| Command | What it does |
| --- | --- |
| `npm run dev` | Vite dev server; the Worker runs in the real Workers runtime (workerd) |
| `npm run typecheck` | TypeScript project build check (app, Worker, tests) |
| `npm run lint` | ESLint |
| `npm test` | Unit and integration tests |
| `npm run build` | Production build into `dist/` |
| `npm run check` | All four above, as CI runs them |
| `npm run preview` | Build, then serve the production build locally in workerd |
| `npm run deploy` | Build and `wrangler deploy` (needs a Cloudflare login) |
| `npm run fixtures` | Regenerate the synthetic demo files (`python3`, with the repo's `reportlab` and `Pillow`) |

`npm run dev` and `npm run preview` read `.dev.vars` (git-ignored) for local variables.

## How it works

1. `GET /api/lessons` returns every lesson of every quest, derived from the guides, as **sanitized** JSON: titles, activities, default copy rules and an `available` flag per worksheet. It never contains Drive file IDs or URLs.
2. The teacher picks activities, then sees one row per worksheet with a suggested number of copies (from class size and group size) that they can change.
3. On **Download Print Pack**, the browser fetches each worksheet from `GET /api/resources/:resourceId`, checks each file, and assembles one PDF with `pdf-lib`, in the order the teacher chose. If any file fails, nothing is downloaded and the teacher sees which worksheet failed.
4. Generated packets are never uploaded or stored anywhere. Class size, group size and print settings are remembered in that browser only.

### PDF assembly

- PDF pages are copied, not rasterized; artwork and text are untouched and page sizes are kept.
- Multi-page worksheets repeat whole (pages 1, 2, 1, 2, ...).
- **Order:** "One worksheet at a time" (all copies of each worksheet together) or "Student packets" (one of each per-student worksheet for student 1, then student 2...; group and class copies follow). `printSequence` in `shared/plan.ts`.
- **Double-sided:** a blank page follows every copy with an odd number of pages, so each copy starts on its own sheet and no two copies share a sheet when printed on both sides. The download message reminds teachers to choose "Print on both sides" (flip on long edge).
- Repeat copies share the first copy's content and image streams, so 25 copies are barely larger than one. (Real check: 25 copies each of the five Secret Ingredients worksheets, 125 pages, came to 1.65 MB from 1.68 MB of source files.)
- PNG and JPEG worksheets are embedded once and fitted proportionally, centred with a 0.25 in margin, on a US Letter page (landscape for wide images).
- Every file is checked by its first bytes, so a Drive HTML error page can never end up in a pack.
- Limits (`shared/limits.ts`): 25 MB per file, 120 MB of source files per pack, 1,500 pages per pack, 200 students, groups of 1–30.

## Where lessons come from

`worker/catalog.ts` walks `catalog/quests.json` → each `quest.json` → its `learning_sequence` → `lessons/<folder>/lesson.json`, and `shared/derive.ts` turns each guide into the teacher's choices. A link counts only when the catalogue types it **`student_worksheet`**; slides, videos, stories and teacher pages are ignored.

| In the Teacher Guide (`lesson.json`) | In the Print Pack Builder |
| --- | --- |
| `GIVE` row in a step | Included automatically |
| `MORE` row in a step | Checkbox |
| `step.options` (A, B, C, D) | Choose one |
| `GIVE` row inside an option | Printed when that option is chosen |
| `MORE` row inside an option | Checkbox shown when that option is chosen |
| Preparation `core` worksheet not linked in any step | Included automatically, under "Preparation" |
| `optional_prep` or `bonuses` worksheet not linked in any step | Checkbox under "Extras" |
| A lesson with no `lesson.json` yet | "Materials coming soon" |
| A lesson with no student worksheets | "No student printing needed" |

- **Suggested copies** come from the guide's own description of that worksheet (the Preparation line first, then the Teaching Flow row): wording with "group" or "team" means one per group, "for the class" means one for the class, anything else one per student. Teachers can change every number, so the guide's quantity wording only needs to be roughly right.
- **Downloadable** when the catalogue entry is `status: published` with a Drive file `published_url` (matching `publication.drive_file_id` when recorded). Otherwise the worksheet shows "Coming soon: not published yet" and is never included. There is no allowlist.
- **Cards printed several to a page:** add `"print": {"cards_per_sheet": 4}` to the worksheet's catalogue entry, using the number of identical cards on each page **counted from the actual PDF**. The suggestion then counts cards, and the pack prints `ceil(cards / 4)` sheets (8 groups → 2 sheets). `scripts/validate.py` checks the field.
- **Formats:** PDF (best), PNG or JPEG files on Drive. Google Docs, Slides and Sheets files are refused until an export step is added.
- Lesson URLs are `/lesson/<quest-id>-<folder without its number>`, e.g. `/lesson/ccc-q01-secret-ingredients`.

**Adding a worksheet to a lesson:** link it from the guide (`GIVE`, `MORE`, or Preparation), register it in the catalogue as a `student_worksheet`, and publish it into the official student-materials folder. Nothing in this app needs editing. Redeploy (or let GitHub builds redeploy) to update the live site. `tests/derive.test.ts` runs against the real guides and catalogue in CI whenever a `lesson.json`, `quest.json` or the catalogue changes.

### Current lessons

| Lesson | Builder shows | Downloadable now |
| --- | --- | --- |
| Activate | No student printing needed | – |
| Set the Table | KWLS Starter (Preparation); Small Bite 1 A School Song / B Mission Vocabulary (+ Mission Vocabulary checkbox); Small Bite 2 A Which Word Fits? / B Team Builder; Extras: Vocabulary Cards | Team Builder, Vocabulary Cards, KWLS Starter (recorded published for audit testing; access not independently verified). School Song Activity and Mission Vocabulary show "Coming soon" until published. |
| Secret Ingredients | Clue Tracker Core and Chapter Notes (included); Clue Tracker Extension (checkbox); Small Bite A Conflict Report / B Character Profile (+ Advanced checkbox) | All five |
| The Showdown | Step 3 choose one: A Design, B Decorate, C Bake, D Mystery (team cards one per group, plus design sheet or recipe); Step 5 TASTE reflection checkbox | None yet: all its worksheets are unpublished placeholders, so it shows "Materials awaiting review" |
| Chew On This, Plate It Forward, Celebrate | Materials coming soon (no `lesson.json` yet) | – |

## Modes and security

`RESOURCE_MODE` (a Worker variable) controls what `/api/resources/*` serves:

| Mode | Serves | Use |
| --- | --- | --- |
| `drive` (default in `wrangler.jsonc`) | real published worksheets from Google Drive; 503 until the Google key secret is set | the deployed pilot site |
| `demo` (default in `.dev.vars.example`) | synthetic fixtures and labelled placeholders; never contacts Google | local demo |
| `disabled` | nothing (503) | switching downloads off |

### Login (`REQUIRE_ACCESS`)

The pilot runs **without a login** (`REQUIRE_ACCESS: "false"` in `wrangler.jsonc`). This is acceptable because the only files ever served are published student worksheets linked from a guide, and published worksheets in the official student-materials folder are shared "anyone with the link can view" (checked 2026-11-02). The Worker can never become a proxy for other Drive files: unpublished worksheets, review copies and anything not linked from a guide get 404.

If a published worksheet ever needs to stay private, set `REQUIRE_ACCESS` to `"true"` and follow [Optional: private login](#optional-private-login-cloudflare-access) first.

In `drive` mode every resource request must pass, in order:

1. Resource ID format check, then: linked from a guide, `student_worksheet`, `published`, Drive file URL (anything else gets 404).
2. **Login, when required:** the Cloudflare Access `Cf-Access-Jwt-Assertion` token is verified against your team's public keys (RS256 signature, audience, issuer, expiry). If a login is required but `ACCESS_TEAM_DOMAIN` or `ACCESS_AUD` is not set, real downloads are **switched off** (503); the only exception is local testing with `LOCAL_DRIVE_TESTING=true` on `localhost`.
3. Google credentials present (`GOOGLE_SERVICE_ACCOUNT_JSON` secret), else 503.
4. Drive metadata check: not trashed, a PDF, PNG or JPEG, size within 25 MB.
5. Download streamed back with its first bytes checked against the type Drive reports, and size enforced while streaming.

Responses are `Cache-Control: private, no-store` and `X-Content-Type-Options: nosniff`. Tokens and keys stay inside the Worker. The app collects no names, emails or student information; only a student count and group size, which stay in the browser.

## Environment variables and secrets

| Name | Kind | Value |
| --- | --- | --- |
| `RESOURCE_MODE` | variable | `disabled`, `demo` or `drive` |
| `REQUIRE_ACCESS` | variable | `"false"` for no login (published files only); anything else requires Cloudflare Access |
| `ACCESS_TEAM_DOMAIN` | variable | only with a login: your Zero Trust team domain, e.g. `littlechewz.cloudflareaccess.com` |
| `ACCESS_AUD` | variable | only with a login: the Access application's Audience (AUD) tag |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **secret** | full JSON key of a read-only service account |
| `LOCAL_DRIVE_TESTING` | local only (`.dev.vars`) | `true` to test real Drive files on localhost without Access |

Set variables in `wrangler.jsonc` (or the dashboard) and the secret with `npx wrangler secret put GOOGLE_SERVICE_ACCOUNT_JSON`. Never commit keys.

## Setup steps that need account access

Status (2026-11-02): the `viewer@` account exists with no project roles, and `03_STUDENT_MATERIALS` is shared with it as Viewer (checked). Deploying and adding the key are still to do, from the owner's machine.

### 1. Read-only Google Drive access

The site uses its own read-only service account, `viewer@little-chewz.iam.gserviceaccount.com`, separate from the `drive-publisher` account GitHub Actions uses, so a leaked site key could never edit files.

1. Google Cloud Console → `little-chewz` project → **IAM & Admin → Service Accounts → Create**. Give it **no** project roles or principals.
2. **Keys → Add key → JSON**. Treat the file like a password and never commit it.
3. The **Google Drive API** is already enabled in that project for the publisher.
4. In Drive, share the official `Confetti Cake Pilot! / 03_STUDENT_MATERIALS` folder with the account's email as **Viewer**, notifications off. Do not share the holding folder or anything outside the permitted root. The site still only serves published worksheets that a guide links.

To revoke: remove the account from the folder, or delete its key.

### 2. Deploy (workers.dev)

```bash
cd apps/print-pack-builder
npx wrangler login
npm run deploy
```

This creates `little-chewz-print-pack-builder.<your-subdomain>.workers.dev` in `drive` mode. Until step 3, worksheet downloads answer "Google Drive credentials are not configured".

### 3. Add the Google key

```bash
npx wrangler secret put GOOGLE_SERVICE_ACCOUNT_JSON < /path/to/key.json
```

The secret takes effect immediately, with no redeploy. Then delete the key file. With `REQUIRE_ACCESS: "false"`, anyone with the site address can download packs of the published (already public) worksheets. Check: `https://<site>/api/health` shows `"driveConfigured":true`, then open Secret Ingredients in an incognito window and download a pack.

### Optional: private login (Cloudflare Access)

Not needed while every published worksheet is public. Free for up to 50 users.

1. Cloudflare dashboard → **Zero Trust** (pick a team name; the Free plan is enough).
2. **Access → Applications → Add an application → Self-hosted**. Domain: the `workers.dev` hostname above (or the custom domain later). Alternatively, in **Workers → your Worker → Settings → Domains & Routes**, turn on Cloudflare Access for the `workers.dev` route.
3. Add an **Allow** policy for the invited pilot teachers' emails (one-time PIN login works without any other identity provider).
4. Copy the application's **Audience (AUD) tag**. Set `ACCESS_TEAM_DOMAIN` (`<team>.cloudflareaccess.com`) and `ACCESS_AUD` in `wrangler.jsonc` `vars` (or the dashboard), set `REQUIRE_ACCESS` to `"true"`, and deploy.
5. Check: an incognito window must get the Access login page; after signing in, Secret Ingredients downloads real worksheets.

`preview_urls` is off in `wrangler.jsonc` so version preview hostnames do not bypass Access. When a login is required, the Worker re-verifies the Access token anyway.

### 4. Deploy from GitHub (optional)

Cloudflare dashboard → **Workers → your Worker → Settings → Builds → Connect** to `Programmer484/little_chewz`:

- Root directory: `apps/print-pack-builder`
- Build command: `npm ci && npm run build`
- Deploy command: `npx wrangler deploy`
- Production branch: `main`; build watch paths: `apps/print-pack-builder/*`, `catalog/*`, `content/*`

Recommended: then every merged guide or catalogue change reaches the live site with no manual deploy. The build reads `catalog/` and `content/` from the repository root, which are present because Workers Builds clones the whole repository. GitHub Actions only checks the app (`.github/workflows/print-pack-builder.yml`); it does not deploy.

### 5. Custom domain later

Add the domain to Cloudflare, then **Workers → your Worker → Settings → Domains & Routes → Add → Custom domain**. If a login is required, add the same hostname to the Access application **before** switching on `drive` mode there. Nothing in the app needs to change.

## Free tier notes

One Worker with static assets. Static asset requests are free; the Worker runs only for `/api/*` (about one request per worksheet in a pack plus one for the lesson list). The Workers Free plan allows 100,000 Worker requests per day and 10 ms CPU per request; fetching from Drive is network time, not CPU. Assembly runs in the teacher's browser. Without a login, anyone with the address can use the site, so these request limits are shared by everyone; switch on Access if traffic or abuse becomes a concern. Cloudflare Access Free covers up to 50 users. These are current published limits, not guarantees; check the Cloudflare pricing pages before a larger rollout.

## Known limits and follow-ups

- **Character Profile Advanced** has a 261 × 348 pt page (about 3.6 × 4.8 in). The pack keeps source page sizes, so it prints small at "actual size"; teachers should use "Fit to page", or the source PDF should be re-exported at Letter/A4.
- Three Secret Ingredients worksheets are A4, and Character Profile Core is a Letter-proportioned 529 × 684 pt page (about 7.3 × 9.5 in). Mixed sizes print fine with "Fit to page".
- Annotations (links, form fields) are kept on the first copy of a page and dropped from repeat copies, so shared annotation objects never point at the wrong page. Printed appearance is unchanged.
- Protected (encrypted) PDFs are rejected with a clear message.
- Direct lesson links: `/lesson/<lessonId>`, e.g. `/lesson/ccc-q01-secret-ingredients`, ready for Teacher Guides to link to.
- A worksheet with separate colour and printer-friendly files is not supported yet; see SYS-005 in `SYSTEM_IMPROVEMENTS.md`.
