# Creating GitHub files through chat (text and binary)

This procedure applies when an assistant creates, extracts, or updates repository files from a chat request. It supplements [AGENTS.md](../AGENTS.md), [START_HERE.md](../START_HERE.md), and [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). It is a **file-transfer procedure**, not permission to approve content, change lesson designs, or publish to Google Drive.

## Standard workflow for every new resource

1. **Identify the source, destination, and status.** Check the current GitHub `main` files, the content contract, and the correct lesson/resource folder. Preserve the original source and record whether the material is `draft_transcription`, `draft_unpublished`, or `approved_source`. Do not infer editorial approval from a successful upload.
2. **Create/edit the editable source** (JSON, Markdown, Python, etc.) using the appropriate existing structure. Text must remain editable; never make a flattened PDF the only source when editable text is required.
3. **Store all PDF-rendering image dependencies in GitHub**, including covers, backgrounds, and illustrations, next to their relevant source or in the existing asset location. For a legacy PDF cover, extract its original page to a faithful PNG rather than inventing a replacement. Standalone image files delivered directly from Drive remain subject to the exception in `CONTENT_CONTRACT.md`.
4. **Work on a branch and a PR** for substantive changes, never silently mutate `main`. Keep newly migrated educational material unapproved until reviewed. Keep published Drive resources unchanged without explicit publishing instructions.
5. **Validate and review** the updated sources and generated outputs before approval. Report the files, commit/PR, validation, visual checks, any missing links, and unresolved status.

## GitHub text upload

For a **single UTF-8 file**, use the connected GitHub `create_file` / `update_file` actions. Fetch the existing file SHA before replacing it. For **multiple UTF-8 files or a mix of templates and images**, prefer the tested batch procedure below: a Git tree entry with `content` creates each editable text blob without a separate `create_file` call. Text-based JSON, Markdown, CSS, HTML, Python and ordinary SVG can be included this way. Verify UTF-8 encoding, trusted content, and intended file paths.

Do not pass PNG, JPG, PDF, ZIP, font, or other binary bytes to the text-file actions or Git tree `content` field; interpreting arbitrary binary as UTF-8 can corrupt it.

## Faster default: batch images and editable templates in one commit (verified)

**Use for 2+ source files**, especially when a new lesson includes multiple images plus JSON/Markdown templates. The tested method uploads separate binary blobs **concurrently**, inserts both the blob SHAs and the UTF-8 template contents into **one Git tree**, and advances the review branch **once**. This minimizes sequential GitHub writes; speed depends on transfer size and network latency, so do not promise a fixed time saving.

1. **Prepare exact assets and local hashes.** For each PNG or other binary, optionally calculate the expected Git blob SHA locally: SHA-1 of the bytes `blob <byte_length>\0` followed by the exact file bytes (where `\0` is a **single NUL byte**, not two text characters). Keep template sources in UTF-8 and use their intended repository paths. Do not alter the original art just to make it uploadable.
2. **Get Base64 for all binaries.** Prefer direct Base64 from the actual file source or from a Drive file already available. For locally generated/chat files when a direct handoff is unavailable, send **multiple** `files.manage_library` `upload` operations in **one request** to uniquely named temporary files under `/Google Drive/`. Use `source_file_ref.file_id` when exported file snapshots provide it; otherwise use `container_path`. Keep temporary uploads non-public, track every returned ID, and confirm sizes.
3. **Parallelize independent work.** Fetch all temporary Drive files using `Google_Drive.fetch({url, download_raw_file:true, include_base64:true})` via `Promise.all` or an equivalent batch mechanism. Check expected MIME/file signatures/sizes. Then upload all binaries with independent `GitHub.create_blob({repository_full_name,content:b64_string,encoding:"base64"})` calls **in parallel**. Await all results and retain the per-file blob SHA and path. Do not print Base64 payloads into chat, logs or commits.
4. **Get a fresh base tree.** Read the current target branch-head **commit SHA**, then obtain the corresponding **Git tree SHA** (for example: GitHub GET `/repos/{owner}/{repo}/git/commits/{head_sha}`, `tree.sha`). Use the actual tree SHA for `base_tree_sha`; do not depend on a connector accepting a commit SHA in place of a tree.
5. **Build a single tree** using `GitHub.create_tree({repository_full_name,base_tree_sha,tree_elements})`. Include one element per binary: `{path,mode:"100644",type:"blob",sha:<uploaded blob SHA>}`. Include one element per editable template: `{path,mode:"100644",type:"blob",content:<UTF-8 string>}`. File entries can create or replace files, so check intended paths and preserve unrelated sources.
6. **Commit and advance once.** Call `GitHub.create_commit({repository_full_name,message,tree_sha,parent_sha:<head commit SHA>})`. Then `GitHub.update_ref({repository_full_name,branch_name,sha:<new commit SHA>,force:false,expected_sha:<old head commit SHA>})`. If the branch changed, fetch the new head and rebuild from its current tree; do not force-overwrite other changes. Use a feature branch and PR, never quietly change `main`.
7. **Verify each file independently.** `GitHub.fetch_file({repository_full_name,path,ref:branch,encoding:"base64"})` for binary files; require its blob SHA to equal the `create_blob` SHA (and the local expected SHA where available). For UTF-8 templates, fetch and compare or parse the committed content. Inspect important images visually when possible and ensure **one commit actually contains all intended paths**.
8. **Clean up every temporary file** with `Google_Drive.delete_file` using the exact returned temporary IDs; verify each deletion. If validation used temporary Git test fixtures, delete those paths on the test branch before merging documentation. Report cleanup failures explicitly.

### Verified batch test — 2026-10-19

An isolated test branch received **two distinct PNGs and one editable JSON template in a single commit**: [test commit `fe197fec`](https://github.com/Programmer484/little_chewz/commit/fe197fec38888fd2bd64d63c797a8b63a2ed2d22). Both PNGs originated from temporary crops of the supplied Set the Table cover; no published art was changed. A single library request transferred both PNGs temporarily, the two Base64 files were fetched concurrently, and the two Git blobs were created concurrently. Both blob SHAs matched Git's locally computed expected SHA-1; the JSON was inserted directly via Git tree `content`. After advancing the branch once, **all three committed files were read back and passed verification**:

- 13,778-byte PNG: `f361e2c6ef9a167c71fd3d4f5c8909803cccb651`
- 606-byte PNG: `2a7727eb90997b86639a400f31564f27488f0758`
- `template.json`: parsed correctly as JSON and contained the expected test data.

The two temporary Drive files were deleted successfully. The test fixtures are temporary branch-only files and must **not** be part of the final documentation PR diff. This is a tested reduction in **sequential commit/ref operations**, not a benchmark claiming a precise elapsed-time improvement.

## GitHub binary upload: verified chat workflow

The connected GitHub API supports **`create_blob` with `encoding: "base64"`**, followed by tree, commit, and branch-ref actions. This successfully committed a Set the Table `cover.png` on 2026-10-19. **A local path is not itself a GitHub upload.**

1. **Prepare the exact bytes** of the image or other binary file, from the supplied source or a tool-produced file. Keep the image intact unless a changed version has been requested/approved.
2. **Obtain Base64 without printing it in the chat or logs.** Prefer a direct binary-to-Base64 handoff where available. In the confirmed fallback, `files.manage_library` uploads the local PNG to a uniquely named **temporary Google Drive file** under `/Google Drive/` (prefer an exported `source_file_ref`, or use `container_path` when unavailable). Fetch that exact returned Drive file ID with `Google_Drive.fetch({url, download_raw_file:true, include_base64:true})`; take its `b64_string` and confirm the expected file type. This temporary transfer is NOT a published Little Chewz asset. Do not create a public sharing link.
3. **Upload the Git blob:** call `GitHub.create_blob({repository_full_name, content: b64_string, encoding:"base64"})`. Keep the returned **blob SHA**.
4. **Attach it to the correct branch:** read the **current branch-head commit SHA** (e.g., via `get_pr_info` for an existing PR), then read the Git commit's **`tree.sha`**. Call `GitHub.create_tree` with an entry `{path:"content/.../cover.png",mode:"100644",type:"blob",sha:<blob SHA>}` and `base_tree_sha` set to that **Git tree SHA**. Next call `GitHub.create_commit` with the new tree SHA and `parent_sha` equal to the original branch-head commit SHA. For multi-file changes, use the batch procedure above instead.
5. **Advance the branch carefully:** call `GitHub.update_ref` with the new commit SHA, `force:false`, and `expected_sha` equal to the prior head SHA. If the branch moved, re-read it and **rebase/recreate the tree and commit**; never force-push over someone else's work.
6. **Verify the file in GitHub:** fetch the committed path on the branch using `GitHub.fetch_file({encoding:"base64"})`. Check the returned blob SHA equals the SHA from `create_blob`; check the intended repository path and image when feasible. Only then mark the cover/asset as committed in its stage metadata.
7. **Delete the temporary transfer file:** use `Google_Drive.delete_file` on the precise temporary Drive file URL/ID, and verify success. The Library deletion action was not supported for Google Drive files in the tested workflow. If cleanup fails, report the exact leftover temporary file and address it; never leave hidden transfer copies unreported. Never delete existing teacher-facing files.

### Minimal action sequence (connector names are descriptive)

```text
local binary file
  -> Base64 bytes (directly, or temporary private Drive transfer -> raw fetch)
  -> GitHub.create_blob(encoding="base64") -> blob SHA
  -> GitHub.create_tree(base_tree_sha=branch's Git tree SHA; entry=path + blob SHA)
  -> GitHub.create_commit(parent_sha=previous branch head; tree_sha=new tree)
  -> GitHub.update_ref(force=false, expected_sha=previous branch head)
  -> GitHub.fetch_file(path, ref=branch, encoding="base64") -> verify SHA
  -> delete the temporary Drive transfer, if used
```

### Known successful example

- Source: supplied four-page `Set_The_Table_Guide.pdf`, page 1 (cover).
- Destination: `content/confetti-cake-cottage/quest-01-bake-off-betrayal/lessons/01-set-the-table/cover.png`.
- Binary: 174,736-byte PNG; Git blob SHA `18435859d4cca4f0c3ba20916839f9fe55a11771`.
- Commit: [13999639](https://github.com/Programmer484/little_chewz/commit/13999639fed6664a84991829c83313bb076ac162); [Set the Table PR #8](https://github.com/Programmer484/little_chewz/pull/8).
- Verified: `fetch_file` reported that same blob SHA at the correct branch path. Temporary Drive transfer deleted successfully.

The older Activate `cover.png` entered GitHub with [migration PR #1](https://github.com/Programmer484/little_chewz/pull/1), but Git history does **not** reveal its exact transfer command. Do not claim its upload method has been reconstructed. The **Set the Table** workflow above is independently tested and reproducible.

## What a successful transfer does *not* prove

GitHub acceptance proves file storage, **not** editorial approval, correct image placement, link authorization, source integrity outside the verified file, or PDF layout quality. Run repository validation (`python scripts/validate.py`), register/execute applicable targeted PDF builds, review rendered pages and hyperlinks, and leave unresolved materials as drafts. A green GitHub Actions preview may only validate currently registered outputs, not every new unregistered lesson.

**Security:** transfer only files needed for the authorized project; do not embed secrets in assets, print Base64 payloads, upload to an unrelated service, or leave temporary Drive copies behind. Do not use this workaround to bypass permissions or approval gates.
