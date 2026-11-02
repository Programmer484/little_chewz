# Little Chewz Print Pack Builder

A small web app for Grade 4–6 teachers: choose a lesson, pick the activities you will run, enter your class size, and download **one combined PDF** with the right number of copies of every student worksheet.

**Open → Choose → Enter quantities → Review → Download**

It is independent of the repository's Python Teacher Guide pipeline. It reads `catalog/resources.json` (read-only) for resource identity and status, never edits lesson sources, and never publishes anything.

| Part | Technology | Where |
| --- | --- | --- |
| Teacher app | React + TypeScript + Vite | `src/` |
| Shared rules (manifests, quantities, file checks) | TypeScript | `shared/` |
| API and secure Drive proxy | Cloudflare Worker (Static Assets + Vite plugin) | `worker/` |
| Lesson print manifests, quests, pilot allowlist | JSON | `config/` |
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

In demo mode the app shows a **Sample Lesson** built from synthetic PDF, PNG and JPEG files, plus the real lessons. Real allowlisted worksheets are replaced by clearly labelled placeholder pages, so the whole flow (choose, quantities, review, download) works end to end without touching Google Drive. The demo uses exactly the same API, planning and PDF-assembly code as production.

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

1. `GET /api/lessons` returns every lesson manifest, joined with the registry and pilot allowlist, as **sanitized** JSON: titles, activities, quantity rules and an `available` flag per resource. It never contains Drive file IDs or URLs.
2. The teacher picks options. `shared/plan.ts` turns the selection and class numbers into a print plan.
3. On **Download Print Pack**, the browser fetches each planned resource from `GET /api/resources/:resourceId`, checks each file, and assembles one PDF with `pdf-lib`. If any file fails, nothing is downloaded and the teacher sees which resource failed.
4. Generated packets are never uploaded or stored anywhere.

### PDF assembly

- PDF pages are copied, not rasterized; artwork and text are untouched and page sizes are kept.
- Multi-page worksheets repeat whole (pages 1, 2, 1, 2, ...).
- Repeat copies share the first copy's content and image streams, so 25 copies are barely larger than one. (Real check: 25 copies each of the five Secret Ingredients worksheets, 125 pages, came to 1.65 MB from 1.68 MB of source files.)
- PNG and JPEG worksheets are embedded once and fitted proportionally, centred with a 0.25 in margin, on a US Letter page (landscape for wide images).
- Every file is checked by its first bytes, so a Drive HTML error page can never end up in a pack.
- Limits (`shared/limits.ts`): 25 MB per file, 120 MB of source files per pack, 1,500 pages per pack, 200 students, groups of 1–30.

## Lesson print manifests

One JSON file per lesson in `config/lessons/`. **Adding a lesson is configuration only:** drop in a new manifest; the Worker picks up every `config/lessons/*.json` at build time. Manifests are separate from `lesson.json` and do not change the Teacher Guide schema.

```jsonc
{
  "lessonId": "ccc-q01-secret-ingredients",   // URL: /lesson/ccc-q01-secret-ingredients
  "questId": "ccc-q01",                        // from config/quests.json
  "lessonFolder": "02-secret-ingredients",     // must match quest.json learning_sequence
  "order": 2,
  "title": "Secret Ingredients",               // must match the quest.json title
  "status": "ready",                           // ready | no_student_printing | in_progress
  "statusNote": "Shown when not ready",
  "defaults": { "studentCount": 25, "groupSize": 4 },
  "sections": [
    { "kind": "core", "id": "...", "title": "Step 1 · ...", "materials": [ /* always included */ ] },
    { "kind": "choice", "id": "...", "title": "Choose One", "options": [
      { "id": "...", "label": "A", "title": "...", "summary": "...", "materials": [],
        "extensions": [ /* checkboxes shown only when this option is chosen */ ] }
    ] },
    { "kind": "optional", "id": "...", "title": "...", "items": [ /* independent checkboxes */ ] }
  ]
}
```

A material is:

```json
{ "resourceId": "ccc-q01-…", "quantity": { "rule": "per_group" }, "cardsPerSheet": 4, "pages": 1, "note": "One per group" }
```

| `quantity.rule` | Copies |
| --- | --- |
| `per_student` | student count |
| `per_group` | `ceil(students / groupSize)` |
| `per_class` | `count` (default 1) |
| `per_activity` | `count` (default 1) when its activity is chosen |
| `teacher_adjustable` | `count` as the default; the teacher can change it |

- **Cards several to a page:** set `cardsPerSheet` to the number of identical cards printed on each page, **verified by opening the actual PDF**. The rule then counts cards, and the pack prints `ceil(cards / cardsPerSheet)` copies of the file. Eight groups needing one card each, at four cards per sheet, print two sheets.
- `pages` is the verified page count of one copy; the review screen shows a total only when every line has one.
- Teachers can add spare copies (or sheets) to any line.
- If two selected activities use the same resource, it is printed once at the larger quantity.
- Rules are tested in `tests/config.test.ts`: every `resourceId` must exist in `catalog/resources.json`, be a `student_worksheet`, and be referenced by that lesson's `lesson.json`; titles and folders must match `quest.json`.

### Current lessons

| Lesson | Manifest status | Downloadable now |
| --- | --- | --- |
| Activate | `no_student_printing` | Nothing to print (slides, videos, read-aloud) |
| Set the Table | `ready`, activities mapped from the Teaching Flow | **None yet.** KWLS Starter, School Song Activity and Our Vocabulary are `unpublished`; Team Builder is `published` but its publication is `unverified`. All stay unavailable until reviewed. |
| Secret Ingredients | `ready` | Clue Tracker Core, Clue Tracker Extension, Chapter Notes, Character Profile Core, Character Profile Advanced (all `published` and `verified`; MIME and page counts checked against Drive on 2026-11-01) |
| The Showdown | `in_progress` | Nothing. The Teacher Guide is still a draft (PR #77) and its A–D materials are placeholders. |

Mapping decisions to confirm: Secret Ingredients prints Clue Tracker Core **one per student** (the Teaching Flow has students complete it in pairs); the Set the Table Small Bite 1B "Our Vocabulary" reference is **one per group**, the same as Small Bite 2A. Vocabulary Cards and the Songwriting Extension are not included: the cards are outside the current Teaching Flow and their cards-per-sheet is unverified, and the extension is a teacher companion, not a student worksheet.

## Pilot allowlist

`config/pilot-allowlist.json` lists the **only** resources the Worker will serve:

```json
"ccc-q01-secret-ingredients-chapter-notes": {
  "source": "published",
  "mimeType": "application/pdf",
  "approval": "Why this is allowed, who checked it, when"
}
```

- It never contains Drive IDs. The Worker resolves the trusted file ID from the registry's `published_url` at build time, and only when the record is `status: published`, `publication.verification: verified`, a printable type, and the URL's ID matches `publication.drive_file_id`.
- `"source": "holding"` can authorize a not-yet-published review file for the pilot (its `holding_url`) **without changing canonical publication status**. It requires an explicit `approval` note and is a human decision. No holding files are allowed today.
- A resource missing from the allowlist, or failing the registry checks, shows as "Awaiting review" or "Not published and verified yet" and is never included in a pack.

## Modes and security

`RESOURCE_MODE` (a Worker variable) controls what `/api/resources/*` serves:

| Mode | Serves | Use |
| --- | --- | --- |
| `drive` (default in `wrangler.jsonc`) | real allowlisted files from Google Drive; 503 until the Google key secret is set | the deployed pilot site |
| `demo` (default in `.dev.vars.example`) | synthetic fixtures and labelled placeholders; never contacts Google | local demo |
| `disabled` | nothing (503) | switching downloads off |

### Login (`REQUIRE_ACCESS`)

The pilot currently runs **without a login** (`REQUIRE_ACCESS: "false"` in `wrangler.jsonc`). This is safe for the current allowlist because every allowlisted worksheet is a published Drive file already shared as "anyone with the link can view" (checked 2026-11-01). Even without a login:

- only allowlisted, published and verified resources are served, so the Worker can never become a proxy for other Drive files;
- allowlist entries with `"source": "holding"` (review copies, which may be private) are **refused** with 403 unless a login is required.

To require a login later, set `REQUIRE_ACCESS` to `"true"` (or remove it) and follow [Optional: private login](#optional-private-login-cloudflare-access). Do this before allowlisting any file that is not public.

In `drive` mode every resource request must pass, in order:

1. Resource ID format check, then the server-side allowlist (unknown and unapproved IDs both get 404).
2. **Login, when required:** the Cloudflare Access `Cf-Access-Jwt-Assertion` token is verified against your team's public keys (RS256 signature, audience, issuer, expiry). If a login is required but `ACCESS_TEAM_DOMAIN` or `ACCESS_AUD` is not set, real downloads are **switched off** (503); the only exception is local testing with `LOCAL_DRIVE_TESTING=true` on `localhost`. Without a login, only published files pass this step.
3. Google credentials present (`GOOGLE_SERVICE_ACCOUNT_JSON` secret), else 503.
4. Drive metadata check: not trashed, MIME type equals the allowlisted type, size within 25 MB.
5. Download streamed back with its first bytes checked (a real PDF/PNG/JPEG) and size enforced while streaming.

Responses are `Cache-Control: private, no-store` and `X-Content-Type-Options: nosniff`. Tokens and keys stay inside the Worker. The app collects no names, emails or student information; only a student count and group size, which never leave the browser.

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

These are not done yet; they need the project owner's Google and Cloudflare accounts.

### 1. Read-only Google Drive access

The site uses its own read-only service account, `viewer@little-chewz.iam.gserviceaccount.com`, separate from the `drive-publisher` account GitHub Actions uses, so a leaked site key could never edit files.

1. Google Cloud Console → `little-chewz` project → **IAM & Admin → Service Accounts → Create**. Give it **no** project roles or principals.
2. **Keys → Add key → JSON**. Treat the file like a password and never commit it.
3. The **Google Drive API** is already enabled in that project for the publisher.
4. In Drive, share the official `Confetti Cake Pilot! / 03_STUDENT_MATERIALS` folder with the account's email as **Viewer**, notifications off. Do not share the holding folder or anything outside the permitted root. The allowlist still limits which files the site serves.

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

The secret takes effect immediately, with no redeploy. Then delete the key file. With `REQUIRE_ACCESS: "false"`, anyone with the site address can download packs of the allowlisted (already public) worksheets. Check: `https://<site>/api/health` shows `"driveConfigured":true`, then open Secret Ingredients in an incognito window and download a pack.

### Optional: private login (Cloudflare Access)

Not needed while every allowlisted file is public. Free for up to 50 users.

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
- Production branch: `main`; build watch paths: `apps/print-pack-builder/*`, `catalog/*`

The build reads `../../catalog/resources.json`, which is present because Workers Builds clones the whole repository. GitHub Actions only checks the app (`.github/workflows/print-pack-builder.yml`); it does not deploy.

### 5. Custom domain later

Add the domain to Cloudflare, then **Workers → your Worker → Settings → Domains & Routes → Add → Custom domain**. If a login is required, add the same hostname to the Access application **before** switching on `drive` mode there. Nothing in the app needs to change.

## Free tier notes

One Worker with static assets. Static asset requests are free; the Worker runs only for `/api/*` (about one request per worksheet in a pack plus one for the lesson list). The Workers Free plan allows 100,000 Worker requests per day and 10 ms CPU per request; fetching from Drive is network time, not CPU. Assembly runs in the teacher's browser. Without a login, anyone with the address can use the site, so these request limits are shared by everyone; switch on Access if traffic or abuse becomes a concern. Cloudflare Access Free covers up to 50 users. These are current published limits, not guarantees; check the Cloudflare pricing pages before a larger rollout.

## Known limits and follow-ups

- **Character Profile Advanced** has a 261 × 348 pt page (about 3.6 × 4.8 in). The pack keeps source page sizes, so it prints small at "actual size"; teachers should use "Fit to page", or the source PDF should be re-exported at Letter/A4.
- Three Secret Ingredients worksheets are A4, and Character Profile Core is a Letter-proportioned 529 × 684 pt page (about 7.3 × 9.5 in). Mixed sizes print fine with "Fit to page".
- Annotations (links, form fields) are kept on the first copy of a page and dropped from repeat copies, so shared annotation objects never point at the wrong page. Printed appearance is unchanged.
- Protected (encrypted) PDFs are rejected with a clear message.
- Direct lesson links: `/lesson/<lessonId>`, e.g. `/lesson/ccc-q01-secret-ingredients`, ready for Teacher Guides to link to later.
