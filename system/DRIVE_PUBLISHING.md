# Publishing to Google Drive

Owns the automated in-place Drive publish step. Approval and status rules belong to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md); the edit and review routine belongs to [WORKFLOW.md](WORKFLOW.md).

## What it does

**Actions → Publish to Drive → Run workflow** takes one registry ID from `catalog/resources.json` and:

1. Runs only from `main`, after `scripts/validate.py` passes.
2. Refuses the entry unless its status is `approved` or `published`.
3. Builds the PDF from the entry's `build` instructions.
4. Checks the Drive destination (from `url`) is a PDF the service account can edit.
5. Replaces the file's contents in place (`files.update`). The file ID, link, name, folder, and sharing stay the same; Drive keeps the previous version in **Manage versions**.
6. Verifies Drive's MD5 matches the local PDF, then changes an `approved` entry to `published` and commits that to `main`.

Run it first with **dry run** ticked (the default): it builds and checks access without uploading. Every run attaches the built PDF as a run artifact.

## Registering a document

Add `build` to the registry entry. The entry's `url` must be the existing Drive file to replace.

```json
"ccc-q01-welcome": {
  "url": "https://drive.google.com/file/d/<file-id>/view",
  "status": "approved",
  "build": {"renderer": "claude", "source": "content/.../welcome/welcome.json"}
}
```

For a Teacher Guide or companion already built by `scripts/build_selected.py`, use its output name instead: `"build": {"output": "00-activate-teacher-guide.pdf"}`.

Currently registered: `ccc-q01-welcome` (Quest_Overview.pdf in 00_WELCOME).

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.
