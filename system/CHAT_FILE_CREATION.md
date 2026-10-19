# Creating GitHub files through chat (text and binary)

This procedure applies when an assistant creates, extracts, or updates repository files from a chat request. It supplements [AGENTS.md](../AGENTS.md), [START_HERE.md](../START_HERE.md), and [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). It is a **file-transfer procedure**, not permission to approve content, change lesson designs, or publish to Google Drive.

## Standard workflow for every new resource

1. **Identify the source, destination, and status.** Check the current GitHub `main` files, the content contract, and the correct lesson/resource folder. Preserve the original source and record whether the material is `draft_transcription`, `draft_unpublished`, or `approved_source`. Do not infer editorial approval from a successful upload.
2. **Create/edit the editable source** (JSON, Markdown, Python, etc.) using the appropriate existing structure. Text must remain editable; never make a flattened PDF the only source when editable text is required.
3. **Store all PDF-rendering image dependencies in GitHub**, including covers, backgrounds, and illustrations, next to their relevant source or in the existing asset location. For a legacy PDF cover, extract its original page to a faithful PNG rather than inventing a replacement. Standalone image files delivered directly from Drive remain subject to the exception in `CONTENT_CONTRACT.md`.
4. **Work on a branch and a PR** for substantive changes, never silently mutate `main`. Keep newly migrated educational material unapproved until reviewed. Keep published Drive resources unchanged without explicit publishing instructions.
5. **Validate and review** the updated sources and generated outputs before approval. Report the files, commit/PR, validation, visual checks, any missing links, and unresolved status.

## GitHub text upload

For UTF-8 text, use the connected GitHub `create_file` / `update_file` actions. Fetch the existing file SHA before replacing it. Do not use those actions for PNG, PDF, ZIP, font, or other binary bytes; interpreting arbitrary binary as UTF-8 can corrupt it.

## GitHub binary upload: verified chat workflow

The connected GitHub API supports **`create_blob` with `encoding: "base64"`**, followed by tree, commit, and branch-ref actions. This successfully committed a Set the Table `cover.png` on 2026-10-19. **A local path is not itself a GitHub upload.**

1. **Prepare the exact bytes** of the image or other binary file, from the supplied source or a tool-produced file. Keep the image intact unless a changed version has been requested/approved.
2. **Obtain Base64 without printing it in the chat or logs.** Prefer a direct binary-to-Base64 handoff where available. In the confirmed fallback, `files.manage_library` uploaded the local PNG via `container_path` to a uniquely named **temporary Google Drive file** under `/Google Drive/`. Fetch that exact returned Drive file ID with `Google_Drive.fetch({url, download_raw_file:true, include_base64:true})`; take its `b64_string` and confirm the expected file type. This temporary transfer is NOT a published Little Chewz asset. Do not create a public sharing link.
3. **Upload the Git blob:** call `GitHub.create_blob({repository_full_name, content: b64_string, encoding:"base64"})`. Keep the returned **blob SHA**.
4. **Attach it to the correct branch:** read the **current branch-head commit SHA** (e.g., via `get_pr_info` for an existing PR). Call `GitHub.create_tree` with an entry `{path:"content/.../cover.png",mode:"100644",type:"blob",sha:<blob SHA>}` and `base_tree_sha` set to the current base tree; the tested connector also accepted the current head commit SHA for this parameter. Next call `GitHub.create_commit` with that tree SHA and `parent_sha` equal to the head commit SHA.
5. **Advance the branch carefully:** call `GitHub.update_ref` with the new commit SHA, `force:false`, and `expected_sha` equal to the prior head SHA. If the branch moved, re-read it and **rebase/recreate the tree and commit**; never force-push over someone else's work.
6. **Verify the file in GitHub:** fetch the committed path on the branch using `GitHub.fetch_file({encoding:"base64"})`. Check the returned blob SHA equals the SHA from `create_blob`; check the intended repository path and image when feasible. Only then mark the cover/asset as committed in its stage metadata.
7. **Delete the temporary transfer file:** use `Google_Drive.delete_file` on the precise temporary Drive file URL/ID, and verify success. The Library deletion action was not supported for Google Drive files in the tested workflow. If cleanup fails, report the exact leftover temporary file and address it; never leave hidden transfer copies unreported. Never delete existing teacher-facing files.

### Minimal action sequence (connector names are descriptive)

```text
local binary file
  -> Base64 bytes (directly, or temporary private Drive transfer -> raw fetch)
  -> GitHub.create_blob(encoding="base64") -> blob SHA
  -> GitHub.create_tree(base_tree_sha=branch tree/head; entry=path + blob SHA)
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
