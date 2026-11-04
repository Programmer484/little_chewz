# Shared editing and review checks

Use alongside the independent [Create](CREATE.md) and [Update](UPDATE.md) workflows. This file owns common validation, preview, source coordination and reporting conventions, **not publication**. Release steps live in [PUBLISH.md](PUBLISH.md); status definitions in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).

## Source and branch hygiene

- Read the owning file's `$instructions` pointer and verify current stable ID, GitHub revision, catalogue record and Drive metadata before writing.
- Default to a shared remote `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch for all work on that lesson. Reuse it across chats and resources; reconcile concurrent changes against its latest head and `main`, without force-pushing. **Only create a separate task branch when the user explicitly requests it.** Commit required images separately from text.
- Externally authored resources stay in their own creation tool and save catalogue changes on the lesson branch, not the generated-PDF pipeline. Non-lesson resources retain their established owner branch.
- Commit source changes, verify remote state and exclude secrets, temporary transfers and generated exports. Preserve unrelated work.

## Validation and previews

- Run `python scripts/validate.py` for content changes and relevant tests for tooling changes. Render generated PDFs with the repository renderer; inspect layout, content and links, and verify the review file in its holding folder.
- `scripts/select_builds.py` and `scripts/build_selected.py` are the supported Python preview path. Valid authored sources can be previewed regardless of delivery status; absent lesson sources produce no placeholders. Manual selection accepts an exact output filename or `all`.
- Every PR and `main` push runs validation; `scripts/select_builds.py` renders only affected PDFs. The first PR run compares with the base; subsequent pushes compare with the previous head when available. Existing preview history is preserved.
- Dependencies are discovered from source JSON file references and each renderer's own bundled asset paths. Changing a `templates/*/TEMPLATE.json` starter or template documentation validates only; changing a font, crest, or other renderer asset rebuilds its consumers. Renderer changes rebuild PDFs using that renderer; shared code and unknown potential inputs conservatively rebuild all. No dependency manifest or cache needs maintenance.
- Renderers generate deterministic PDFs with pinned library versions. Drive publication still verifies the actual PDF bytes with MD5 and requires existing approval safeguards.
- Give the verified **GitHub Actions run URL first** for PDF reviews (prefer the successful post-merge `main` run). Previews remain under `pdf-preview-history/previews/<run-id>/`; workflow artifacts expire sooner. Never automatically merge or delete historical preview branches.

## Report and stop

Report saved file locations, checks, preview links and unresolved blockers. Holding uploads, validation passes and ordinary merges **never prove publication**. For authorized official releases, linked-resource preflight, external publication, generated-PDF release merging and approved URL/checksum changes use [PUBLISH.md](PUBLISH.md).
