# Creating and transferring source files

Applies to files created, extracted, or updated through chat. Source/status rules belong to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md); branch, PR, review, and delivery requirements belong to [WORKFLOW.md](WORKFLOW.md). A successful upload proves storage, not editorial approval or permission to publish.

## Choose the available path

- **Local checkout:** write the exact source files, inspect them, and commit/push through the normal workflow. No connector transfer is needed.
- **Connector, one UTF-8 file:** use GitHub text-file creation/update; fetch the existing SHA before replacement.
- **Connector, multiple files or binary assets:** use the batch procedure below. Never stop at “the connector cannot upload binary” without checking its Base64 blob + tree/commit/ref capabilities.

Keep text editable. Commit every image required by a PDF build to its source location; extract legacy covers faithfully rather than inventing replacements. Save a cover as a one-page `cover.pdf` cut losslessly from the source PDF (for example `qpdf --empty --pages <source.pdf> <page> -- cover.pdf`), never as a rasterized PNG: rasterizing turns vector text into pixels and lowers artwork resolution. Do not pass PNG/JPG/PDF/ZIP/font bytes to text-file actions or Git tree `content` fields.

## Connector batch procedure

Use one tree and commit for related files; the same procedure handles a single binary. Tool names below describe capabilities and may vary by connector.

1. **Prepare.** Confirm intended paths, source/status, exact bytes, and UTF-8 text. Calculate expected binary Git blob SHAs where possible: SHA-1 of `blob <byte_length>` + one NUL byte + file bytes. Preserve artwork unless a change is requested.
2. **Obtain Base64 privately.** Prefer direct access to the source bytes. If unavailable, upload required local assets as uniquely named, non-public temporary Drive files through `files.manage_library` (prefer `source_file_ref.file_id`, otherwise `container_path`). Batch multiple uploads; retain exact returned IDs and sizes. Fetch those files with `Google_Drive.fetch({url, download_raw_file:true, include_base64:true})`. Check signatures, types, and sizes; never print Base64.
3. **Upload blobs.** Call `GitHub.create_blob({repository_full_name, content:b64_string, encoding:"base64"})` for each binary. Independent fetches/blob uploads may run concurrently; await every result and retain its path and blob SHA.
4. **Read the current branch.** Obtain its head commit SHA and that commit's actual `tree.sha`, for example via GET `/repos/{owner}/{repo}/git/commits/{head_sha}`. Do not substitute a commit SHA for a tree SHA. Work on the source review branch, not directly on `main`.
5. **Create one tree.** Call `GitHub.create_tree({repository_full_name, base_tree_sha, tree_elements})`. Binary entries use `{path, mode:"100644", type:"blob", sha:<blob SHA>}`; UTF-8 entries use `{path, mode:"100644", type:"blob", content:<text>}`. Preserve unrelated paths.
6. **Commit and advance.** Call `GitHub.create_commit` with that tree and the previous head as parent, then `GitHub.update_ref` with `force:false` and `expected_sha:<previous head>`. If the branch moved, rebuild against its new head; never overwrite concurrent changes.
7. **Verify remote files.** Fetch each committed binary with `GitHub.fetch_file({path, ref:branch, encoding:"base64"})`. Require its blob SHA to match the upload and the local expected SHA where available. Compare/parse committed text, inspect important images, and verify the commit contains every intended path. Only then record assets as committed.
8. **Clean temporary transfers.** Delete only the exact temporary IDs created in step 2 using `Google_Drive.delete_file`; verify deletion. The Library deletion action did not support Drive in the tested workflow. Remove temporary test fixtures before merge and report any cleanup failure. Never delete teacher-facing originals.

Transfer only authorized project files. Do not include secrets, create public transfer links, or use this procedure to bypass permissions. Complete validation, output review, and PR delivery under the workflow; a green preview covers only registered outputs.

## Verified examples

- **Single binary, 2026-10-19:** Set the Table `cover.png`, faithfully extracted from page 1 of the supplied four-page guide; 174,736 bytes, Git blob SHA `18435859d4cca4f0c3ba20916839f9fe55a11771`. Saved under `content/confetti-cake-cottage/quest-01-bake-off-betrayal/lessons/01-set-the-table/` in [commit 13999639](https://github.com/Programmer484/little_chewz/commit/13999639fed6664a84991829c83313bb076ac162), [PR #8](https://github.com/Programmer484/little_chewz/pull/8). Remote SHA matched; temporary transfer deleted.
- **Batch, 2026-10-19:** two PNGs and one editable JSON file in [test commit fe197fec](https://github.com/Programmer484/little_chewz/commit/fe197fec38888fd2bd64d63c797a8b63a2ed2d22). Both PNG SHAs matched local hashes (`f361e2c6ef9a167c71fd3d4f5c8909803cccb651`, 13,778 bytes; `2a7727eb90997b86639a400f31564f27488f0758`, 606 bytes); JSON parsed correctly; both temporary Drive files were deleted. Test fixtures belong only on the isolated test branch. This verifies batching, not a performance benchmark.

The original Activate cover arrived in [PR #1](https://github.com/Programmer484/little_chewz/pull/1); its exact transfer method is not established by Git history.
