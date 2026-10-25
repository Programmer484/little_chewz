# Agent command contract

The user-facing phrases **`/create`**, **`/update`**, and **`/merge`** are AI-agent instructions, not executable programs. The source procedure is [CREATE.md](CREATE.md); client-side slash aliases require separate configuration. Infer the requested resource from the conversation and verify its stable ID in live GitHub records.

## `/create [instructions]`

Use the already prototyped content. Follow [CREATE.md](CREATE.md) and the correct `production_type` workflow. Create a review copy in the actual Google Drive holding folder, record its `holding_url` separately from `published_url`, preserve existing identities, and keep `status: unpublished` until confirmed official publication.

- **`generated_pdf`:** commit editable source and build assets on `edit/<resource-id>`, build through the existing Python renderer, upload a review PDF to the PDF-generated holding folder, register the build, then provide a PR and preview.
- **`external`:** create using the appropriate agent tool, upload the finished file to the relevant holding folder, and commit catalogue metadata. No GitHub source branch, editable-source copy, renderer, or PR merge is required to publish the external asset.

## `/update [instructions]`

- **Generated PDF:** fetch the remote `edit/<resource-id>` branch, reconcile concurrent changes, update only the authorized source/assets, validate and preview, and non-force push. Never overwrite another agent's commits.
- **External:** edit in the original creation tool, replace the existing holding file **in place** when possible, verify the file and update the catalogue through a normal GitHub bookkeeping change. Do not invoke a PDF build or resource merge.

Editing a draft does not change the currently verified live release status.

## `/merge [instructions]` — generated PDFs only

Requires explicit human approval of the exact reviewed generated PDF. Reconcile and validate the resource branch, append its **single-resource** authorized release marker at `.github/resource-releases/<PR-number>.json` with `{"signal":"authorized-resource-merge","pr_number":<PR-number>,"resource_ids":["<resource-id>"]}`, then merge the PR into `main`. GitHub Actions runs a guarded build, replaces the established official PDF **in place**, reads back the exact Drive checksum/file ID, records publication, and safely deletes the old branch only if it has not advanced. Check the Actions run and report errors truthfully. A first-ever official destination must be placed and verified by an agent before later automatic replacements.

**Do not use `/merge` for external resources.** External publication is a distinct agent-managed Drive procedure: move or replace in the official destination, verify, then record the confirmed status in GitHub. There is no separate user-facing `/publish` command, scheduled inspection, or external checksum pipeline.
