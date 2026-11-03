# Little Chewz Print Pack Builder

A small web app for Grade 4–6 teachers: choose a lesson, pick the activities you will run, check the copies, and download **one combined PDF** of every student worksheet.

**Open → tick activities → check copies → download**, all on one page.

**There is no separate print configuration.** The builder reads each lesson's Teacher Guide source (`lesson.json`) and `catalog/resources.json` at build time, so a worksheet added to a guide and published in the catalogue becomes printable on the next deploy ([Where lessons come from](#where-lessons-come-from)). It never edits lesson sources and never publishes anything. It is independent of the Python Teacher Guide pipeline.

| Part | Technology | Where |
| --- | --- | --- |
| Teacher app | React + TypeScript + Vite | `src/` |
| Guide reader, copy plan, packet boundaries, file checks | TypeScript | `shared/` (`derive.ts` reads the guides) |
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

1. The Worker discovers the current lessons through `catalog/quests.json` → `quest.json` → `lesson.json`, and resolves worksheet IDs through `catalog/resources.json`. Only `student_worksheet` resources with trusted official `published_url` Drive file URLs can be fetched in drive mode.
2. **Everything is a checkbox, with the guide's defaults pre-ticked.** `GIVE` and unreferenced preparation `core` worksheets start ticked; A/B options, `MORE` and bonus worksheets start unticked. Teachers may pick one option, both or none, and untick any core worksheet, for example to print only an extension they decided to add after printing the rest. A choice with nothing picked shows a **soft warning** that does not block the download. An empty pack cannot be downloaded.
3. Steps whose worksheets and optional extras would otherwise appear twice share one heading.
4. The teacher enters the class size. Each selected group activity has a **Groups** field, prefilled with `Math.ceil(studentCount / 4)` (the lesson's default group size) and showing how many students that puts in each group. Enter 1 for **one whole-class copy**. Teachers may override each print line's copies independently, down to 0. A worksheet selected both per student and per group prints only the student copies, since every student already has one; setting its student copies to 0 brings the group copies back.
5. Download fetches each distinct selected file once and combines all copies into **one PDF**. Nothing is uploaded or stored. Class size and the double-sided preference are saved only in the browser.

### Print order and duplex

- **Always:** student packets first, one complete packet per student in lesson order; then all `per_group` resources and multi-card cutouts, grouped by resource.
- Each student packet contains the worksheets in sequence, preserving every multi-page worksheet. Two different one-page worksheets may share opposite sides of the same physical sheet.
- With **Print double-sided** on, a blank is added *only at an odd student-packet boundary* and when a shared material needs an empty reverse. Cards with `print.cards_per_sheet > 1` are always front-only, even if their PDF has multiple pages.
- With duplex off, no blank pages are inserted. For duplex output, select **Print on both sides / flip on long edge** in the printer dialog. No manual duplex or print-order selector.
- PDF pages are copied without rasterization; PNG/JPEG images are embedded proportionally, and repeated copies reuse image and PDF streams. The PDF contains intentional blank backs where required.

### Metadata: no separate print configuration

The print builder reads only `lesson.json` worksheet links and `catalog/resources.json`:

| Guide reference | Printing behavior |
| --- | --- |
| `GIVE` row or unreferenced preparation `core` | Ticked by default; can be unticked |
| `MORE` row, optional preparation or bonus | Optional checkbox |
| `step.options` A/B/C/D | Unticked; any combination, soft warning when none |
| `MORE` inside an option | Optional extension when that option is selected |
| No guide source yet | Materials coming soon |
| Guide without student worksheets | No student printing |

Every link to a `student_worksheet`, including `row.links` entries, must have explicit `"quantity": "per_student"` or `"quantity": "per_group"`. A whole class is one group, **not** a third quantity type. Descriptions do not determine copy counts. Missing/invalid quantities fail `python scripts/validate.py`; the builder also fails closed if malformed metadata reaches it.

For a resource with several cards or cutouts per physical sheet, use the existing `"print": {"cards_per_sheet": 4}` in `catalog/resources.json`, counted from the actual PDF. Ordinary worksheets omit the `print` property. For one card per group, five groups with four cards on a sheet need two file copies. Multi-card sheets are placed with shared materials and get empty backs in duplex mode.

Unpublished resources remain visible as unavailable; no Drive ID or URL is sent to the browser. No extra lesson lists, inferred rules, or new dependencies are needed.

### Current lessons

| Lesson | Builder shows | Downloadable now |
| --- | --- | --- |
| Activate | No student printing needed | – |
| Set the Table | KWLS Starter (Preparation); Small Bite 1 A School Song / B Mission Vocabulary (+ Our Vocabulary checkbox); Small Bite 2 A Which Word Fits? (Our Vocabulary) / B Team Builder; Extras: Vocabulary Cards | Team Builder, Vocabulary Cards, KWLS Starter (recorded published for audit testing; access not independently verified). School Song Activity and Our Vocabulary show "Coming soon" until published. |
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

The pilot runs **without a login** (`REQUIRE_ACCESS: "false"` in `wrangler.jsonc`). This is acceptable because the only files ever served are published student worksheets linked from a guide, and published worksheets in the official student-materials folder are shared "anyone with the link can view" (checked 2026-11-02). The Worker can never become a proxy for other Drive files: worksheets lacking an official URL, review copies and anything not linked from a guide get 404.

If a published worksheet ever needs to stay private, set `REQUIRE_ACCESS` to `"true"` and follow [Optional: private login](#optional-private-login-cloudflare-access) first.

In `drive` mode every resource request must pass, in order:

1. Resource ID format check, then: linked from a guide, `student_worksheet`, a valid official Drive `published_url` (anything else gets 404).
2. **Login, when required:** the Cloudflare Access `Cf-Access-Jwt-Assertion` token is verified against your team's public keys (RS256 signature, audience, issuer, expiry). If a login is required but `ACCESS_TEAM_DOMAIN` or `ACCESS_AUD` is not set, real downloads are **switched off** (503); the only exception is local testing with `LOCAL_DRIVE_TESTING=true` on `localhost`.
3. Google credentials present (`GOOGLE_SERVICE_ACCOUNT_JSON` secret), else 503.
4. Drive metadata check: not trashed, a PDF, PNG or JPEG, size within 25 MB.
5. Download streamed back with its first bytes checked against the type Drive reports, and size enforced while streaming.

Responses are `Cache-Control: private, no-store` and `X-Content-Type-Options: nosniff`. Tokens and keys stay inside the Worker. The app collects no names, emails or student information; only a student count and group size, which stay in the browser.

## Environment variables and secrets

| Name | Kind | Value |
| --- | --- | --- |
| `RESOURCE_MODE` | variable | `disabled`, `demo` or `drive` |
| `REQUIRE_ACCESS` | variable | `"false"` for no login (official files only); anything else requires Cloudflare Access |
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
