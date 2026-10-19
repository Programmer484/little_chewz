# System Improvements

A dedicated backlog for improvements to the Little Chewz **source editing, validation, regeneration, and review system**, separate from educational content design and publication work.

- **Status**: Proposed → Planned → In progress → Implemented. Entries are not implemented merely by being recorded here.
- **Priority**: P0 = blocking; P1 = important next improvement; P2 = optional.
- **Scope**: System tooling and workflow, not lesson content.
- **Policy**: Do not publish to Google Drive automatically. Published assets and link IDs remain unchanged without explicit approval.

## SYS-001 — GitHub Actions regeneration and validation for cloud-chat edits

**Status:** Implemented (Phase 1 + Phase 2 targeted PDF selection)  
**Priority:** P1  
**Owner:** To be assigned  
**Requested:** 2026-10-18

### Problem

Editing from ChatGPT can modify and commit GitHub source files, and PDF rendering already works in a separate cloud working environment. However, GitHub currently has no checked-in CI workflow that runs the project's own Python validation or regenerates PDF previews for a proposed change. Running checks outside the repository requires transferring files and increases the risk of previewing a different source revision.

### Goal

Make GitHub the authoritative, reproducible build-and-review environment for changes made through cloud chat. A pull request should show whether editable sources validate and offer generated PDFs for review, without publishing them.

### Proposed implementation

**Phase 1 — Reliable CI and previews**
1. Add `.github/workflows/build-resources.yml` triggered by relevant pull requests, plus manual runs (no duplicate push-to-main build). Allow manual dispatch.
2. Set up a supported Python runtime, install pinned project dependencies, and make a compatible Lato font family available to the teacher-guide renderer (without committing font binaries to this repository).
3. Run `python scripts/validate.py` and fail the check on errors.
4. Regenerate all *currently buildable and approved* teacher-guide and teacher-companion sources using `scripts/build.py`. Include draft outputs only when explicitly requested; never treat six lesson-stage skeletons as buildable lessons.
5. Verify that produced PDFs exist and can be opened; audit internal/external PDF link annotations to the extent supported locally. This does not prove Google Drive sharing permissions.
6. Upload the generated PDFs as ephemeral GitHub Actions artifacts associated with the exact commit/PR. Report validation/build errors clearly.

**Phase 2 — Targeted edits and dependency-aware builds (implemented for existing three approved PDFs)**
1. Determine affected outputs from changed lesson/resource JSON, referenced assets, resource registry, templates, and renderers. A shared renderer/config change should rebuild every dependent output.
2. Support a manual `all` rebuild and a single-resource preview for cloud-chat changes.
3. Provide a concise PR status/summary listing source files changed, generated outputs, warnings, unresolved references, and artifacts.

### Acceptance criteria

- A pull request changing one Activate question triggers a passing validation and produces an updated, downloadable Teacher Guide preview for that PR's commit.
- A change to a companion JSON produces the matching companion preview.
- Invalid references, missing required artwork, or renderer failures make the CI check fail.
- The CI runner does not require a developer's local machine or font files committed to GitHub.
- No generated PDF is committed as canonical source, and no GitHub Actions job replaces or publishes Drive files.

### Dependencies / design boundaries

- Current build entry point: `scripts/build.py`; validator: `scripts/validate.py`; renderers: `scripts/renderers/`.
- PDF builds use repository-local, versioned image assets under `system/CONTENT_CONTRACT.md`; use `system/CHAT_FILE_CREATION.md` to transfer source artwork when needed.
- Image generation itself, slideshow rendering, student worksheet rendering, and Drive publication are **out of scope** for this entry.

### Completion record

- [x] GitHub Actions workflow and pinned runner dependencies implemented and verified
- [x] Validation and generated-preview artifacts verified on PR #2 (3 PDFs; 7-day artifact)
- [x] Targeted dependency-aware regeneration implemented with regression tests
- [x] Review workflow documented in `START_HERE.md`


### Targeted-build implementation note (2026-10-18)

Selection lives in `scripts/select_builds.py` and verified rendering in `scripts/build_selected.py`. PR builds compare file changes against the PR's base commit; validation always runs. One resource edit builds that resource, changed shared renderers build their consumers, and only changed resource-registry entries referenced by a document trigger its rebuild. Unrelated source/doc changes create no PDF artifacts. Unknown dependencies conservatively rebuild all currently approved PDFs. Manual dispatch rebuilds all. The unapproved songwriting draft remains excluded. Existing source content and Drive publishing are not changed.

## SYS-002 — Lesson-scoped slide generation

**Status:** Planned (policy decided; generator not implemented)  
**Priority:** P2  
**Requested:** 2026-10-19

Build independent, editable slide sets **per lesson**, not a complete continuous quest deck. Support surgical edits and regenerate only changed slides or the affected lesson. Preserve source assets, stable resource IDs, lesson-local slide numbers, review status and existing published links. The old 44-slide quest deck is a historical reference, not a generation target.

Implement slide rendering and targeted build registration only when a real, reviewed lesson-slide source requires them. Validate and review generated previews before publishing. Do not generate placeholder slides, renumber legacy assets automatically, change the existing PDF workflow, or publish to Drive without instruction.
