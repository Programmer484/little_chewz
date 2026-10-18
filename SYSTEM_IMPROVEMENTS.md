# System Improvements

A dedicated backlog for improvements to the Little Chewz **source editing, validation, regeneration, and review system**, separate from educational content design and publication work.

- **Status**: Proposed → Planned → In progress → Implemented. Entries are not implemented merely by being recorded here.
- **Priority**: P0 = blocking; P1 = important next improvement; P2 = optional.
- **Scope**: System tooling and workflow, not lesson content.
- **Policy**: Do not publish to Google Drive automatically. Published assets and link IDs remain unchanged without explicit approval.

## SYS-001 — GitHub Actions regeneration and validation for cloud-chat edits

**Status:** In progress (Phase 1 test)  
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

**Phase 2 — Targeted edits and dependency-aware builds**
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
- For any future Drive-hosted art referenced by PDF builds, a separate approved-asset fetch/cache workflow is needed; not part of SYS-001 until its access model is decided.
- Image generation itself, slideshow rendering, student worksheet rendering, and Drive publication are **out of scope** for this entry.

### Completion record

- [x] Workflow and pinned runner dependencies committed on test branch (verification pending)
- [ ] Validation and generated-preview artifacts verified on a test PR
- [ ] Targeted dependency-aware regeneration implemented and tested
- [x] Review workflow documented in `START_HERE.md`

