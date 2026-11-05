# GitHub binary-transfer runbook

This covers **connector transfer mechanics only**. Resource creation, editing, human approval and publication belong to [Create](CREATE.md), [Edit](EDIT.md) and [Publish](PUBLISH.md).

For one UTF-8 file use GitHub's file-creation/update action (fetch the existing SHA). For multiple files or binary artwork, Base64-encode bytes **privately** and create GitHub blobs, then one tree and commit based on the current branch's **tree SHA**, not its commit SHA. Binary tree elements use `{path, mode:"100644", type:"blob", sha:<blob SHA>}`; text entries may use `content`. Advance with an expected head SHA, without force-push. Read back committed files and verify exact hashes and sizes.

If transfer bytes must temporarily pass through Drive, use a private, authorized temporary file, verify bytes, then delete **only** that temporary ID. Never expose Base64, credentials, public temporary links or delete the original. Keep PDF text editable and artwork separate; cut legacy vector covers losslessly as `cover.pdf` rather than rasterizing them.

The previous `CHAT_FILE_CREATION.md` remains available in GitHub history for detailed examples. A transfer is not approval or publication.
